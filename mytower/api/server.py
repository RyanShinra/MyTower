import asyncio
import json
import logging
import os
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from strawberry.fastapi import GraphQLRouter

from mytower.api.schema import schema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Type Aliases for Rate Limiting
# ============================================================================
# These type aliases make the rate limiting decorator pattern explicit.
# Without them, the chained calls limiter.limit(rate)(endpoint)(request)
# would have unclear Callable types.
#
# The decorator pattern works like this:
# 1. limiter.limit("100/minute") -> returns a RateLimitDecorator
# 2. decorator(endpoint) -> returns an AsyncEndpoint (wrapped version)
# 3. wrapped_endpoint(request) -> executes the rate limit check

# An async endpoint that takes a Request and returns None
# This matches the signature of _dummy_endpoint: async def(Request) -> None
AsyncEndpoint = Callable[[Request], Awaitable[None]]

# A decorator that transforms an endpoint into a rate-limited endpoint
# Takes: an AsyncEndpoint
# Returns: an AsyncEndpoint (with rate limiting applied)
RateLimitDecorator = Callable[[AsyncEndpoint], AsyncEndpoint]

# ============================================================================
# Rate Limiting Configuration
# ============================================================================
# slowapi: A rate limiting library for FastAPI (wrapper around `limits`)
# Status: Alpha quality, production-tested, inactive maintenance (12+ months)
# Why: Simple human-readable limits ("100/minute"), widely used
# Alternative: Could use `limits` directly or `fastapi-limiter` (Redis-based)
#
# Rate limiting is applied per-IP address using slowapi's Limiter.
# The limiter is a module-level singleton (dependency injection pattern).
# This is standard practice for FastAPI middleware/dependencies.
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="MyTower GraphQL API")
app.state.limiter = limiter
# Type note: slowapi's _rate_limit_exceeded_handler expects a specific exception
# type (RateLimitExceeded) but FastAPI's add_exception_handler uses a generic
# protocol that expects Callable[[Request, Exception], Response]. The signatures
# are compatible at runtime but type checkers flag this as incompatible.
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# Configure CORS middleware
# SECURITY WARNING: The default configuration allows all origins (*) which is suitable
# for development only. For production, you MUST set MYTOWER_CORS_ORIGINS to a
# comma-separated list of allowed origins.
#
# IMPORTANT: When using allow_credentials=True, wildcard origins (*) are not allowed
# by CORS specification. The configuration below automatically disables credentials
# when wildcard origins are detected.
#
# Production example:
#   MYTOWER_CORS_ORIGINS="https://example.com,https://app.example.com"
origins_env: str = os.getenv("MYTOWER_CORS_ORIGINS", "*")
# Filter out empty strings after stripping whitespace - avoiding double strip() calls
origins_list: list[str] = origins_env.split(",")
allowed_origins: list[str] = []
for origin in origins_list:
    stripped_origin: str = origin.strip()
    if stripped_origin:
        allowed_origins.append(stripped_origin)

# Fallback to wildcard if no valid origins provided (handles empty string or whitespace-only env var)
if not allowed_origins:
    allowed_origins = ["*"]

# Disable credentials if using wildcard origins (CORS security requirement)
use_credentials: bool = "*" not in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=use_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection tracking per IP
# This prevents a single client from opening too many concurrent WebSocket connections
ws_connections: defaultdict[str, int] = defaultdict(int)
# Locks to synchronize access to ws_connections and prevent race conditions
ws_connection_locks: dict[str, asyncio.Lock] = {}
# Global lock to ensure atomic creation of per-IP locks
_ws_locks_creation_lock: asyncio.Lock = asyncio.Lock()
MAX_WS_CONNECTIONS_PER_IP: int = int(os.getenv("MYTOWER_MAX_WS_CONNECTIONS", "10"))

async def get_or_create_lock(ip: str) -> asyncio.Lock:
    """
    Get or create a lock for the given IP address.

    This function ensures atomic lock creation to prevent race conditions
    where multiple tasks might create different Lock instances for the same IP.

    Args:
        ip: The IP address to get/create a lock for

    Returns:
        The asyncio.Lock instance for this IP
    """
    if ip not in ws_connection_locks:
        async with _ws_locks_creation_lock:
            # Double-check pattern: another task might have created it while we waited
            if ip not in ws_connection_locks:
                ws_connection_locks[ip] = asyncio.Lock()
    return ws_connection_locks[ip]

async def decrement_ws_connection(ip: str) -> None:
    """
    Decrement the WebSocket connection count for the given IP.
    If the count reaches zero, remove the IP from the dictionary.

    Async-safe: Uses per-IP locks to prevent race conditions between concurrent async tasks.
    """
    lock = await get_or_create_lock(ip)
    async with lock:
        if ip in ws_connections:
            ws_connections[ip] -= 1
            current_count = ws_connections[ip]
            if current_count <= 0:
                logger.info(
                    f"🔌 WebSocket disconnected: {ip} (0/{MAX_WS_CONNECTIONS_PER_IP})"
                )
                del ws_connections[ip]
                # Do NOT delete the lock here; keep it for future synchronization
                # TODO: Optionally implement lock cleanup if memory usage is a concern
            else:
                logger.info(
                    f"🔌 WebSocket disconnected: {ip} ({current_count}/{MAX_WS_CONNECTIONS_PER_IP})"
                )


# WebSocket subscriptions are automatically enabled in Strawberry's FastAPI integration
# Both protocols are supported by default:
# - graphql-transport-ws: Modern protocol (recommended)
# - graphql-ws: Legacy protocol for backward compatibility
# Strawberry's GraphQLRouter automatically handles protocol negotiation

# Add middleware to log all requests and apply rate limiting
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"📨 Incoming request: {request.method} {request.url}")
    logger.info(f"🔍 Client: {request.client.host if request.client else 'unknown'}")
    logger.info(f"🔍 Headers: {dict(request.headers)}")
    response = await call_next(request)
    logger.info(f"📤 Response status: {response.status_code}")
    return response

# ============================================================================
# Custom GraphQL Router with Rate Limiting
# ============================================================================
# Why override __call__?
# The GraphQLRouter.__call__ method is the ASGI interface for handling requests.
# Overriding it allows us to intercept requests before they reach Strawberry
# to apply rate limiting and WebSocket connection tracking.
#
# Alternative approaches considered:
# 1. Middleware: Can't differentiate query vs mutation without parsing
# 2. FastAPI dependency: Doesn't work with Strawberry's router pattern
# 3. Strawberry extension: More invasive, requires schema modification
#
# This approach is industry-standard for FastAPI router customization.
# ============================================================================

class RateLimitedGraphQLRouter(GraphQLRouter):
    """
    GraphQL router with rate limiting and WebSocket connection tracking.

    Rate limits (configurable via environment variables):
    - Queries: 200/minute (MYTOWER_RATE_LIMIT_QUERIES)
    - Mutations: 100/minute (MYTOWER_RATE_LIMIT_MUTATIONS)
    - WebSocket connections: 10 concurrent per IP (MYTOWER_MAX_WS_CONNECTIONS)

    Security benefits:
    - Prevents DoS attacks via query/mutation spam
    - Protects command queue from exhaustion
    - Limits resource consumption from concurrent subscriptions
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Load rate limits from environment (human-readable format)
        self.query_rate: str = os.getenv("MYTOWER_RATE_LIMIT_QUERIES", "200/minute")
        self.mutation_rate: str = os.getenv("MYTOWER_RATE_LIMIT_MUTATIONS", "100/minute")
        logger.info(
            f"🛡️  Rate limiting enabled: "
            f"Queries={self.query_rate}, Mutations={self.mutation_rate}"
        )
        logger.info(
            f"🛡️  WebSocket limit: "
            f"{MAX_WS_CONNECTIONS_PER_IP} concurrent connections per IP"
        )

    async def __call__(self, request: Request):  # type: ignore[override]
        """
        ASGI application interface with rate limiting.

        LISKOV SUBSTITUTION PRINCIPLE (LSP) NOTE:
        This override technically violates LSP because the parent class expects
        __call__(scope, receive, send) while we accept __call__(request).

        Why this is safe:
        1. FastAPI's routing system always calls routers with a Request object
        2. The Request object wraps (scope, receive, send) internally
        3. This pattern is standard in FastAPI ecosystem (see FastAPI's APIRouter)
        4. Runtime behavior is correct; only static type checking complains

        Alternative considered:
        Accept (scope, receive, send) and construct Request manually, but this
        duplicates FastAPI's internal logic and is more error-prone.

        Type checker suppression: type: ignore[override] acknowledges the
        signature mismatch while confirming runtime safety.
        """
        client_ip: str = get_remote_address(request)

        # ====================================================================
        # WebSocket Connection Limiting
        # ====================================================================
        upgrade_header: str = request.headers.get("upgrade", "").lower()
        if upgrade_header == "websocket":
            # Check and increment connection count with synchronization
            # to prevent race conditions from concurrent requests
            lock = await get_or_create_lock(client_ip)
            async with lock:
                # Check if client has exceeded WebSocket connection limit
                if ws_connections[client_ip] >= MAX_WS_CONNECTIONS_PER_IP:
                    logger.warning(
                        f"🚫 WebSocket connection limit exceeded for {client_ip}: "
                        f"{ws_connections[client_ip]}/{MAX_WS_CONNECTIONS_PER_IP}"
                    )
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Too many concurrent WebSocket connections",
                            "limit": MAX_WS_CONNECTIONS_PER_IP,
                            "message": (
                                f"Maximum {MAX_WS_CONNECTIONS_PER_IP} "
                                "concurrent subscriptions per IP"
                            )
                        }
                    )

                # Track WebSocket connection (increment before, decrement after)
                ws_connections[client_ip] += 1
                current_count: int = ws_connections[client_ip]
                # Log inside lock to ensure consistency
                logger.info(
                    f"🔌 WebSocket connected: {client_ip} "
                    f"({current_count}/{MAX_WS_CONNECTIONS_PER_IP})"
                )

            try:
                # Pass request to parent GraphQLRouter
                # Note: Parent expects ASGI (scope, receive, send) but FastAPI's
                # Request wraps these. This works due to Starlette's design but
                # type checkers complain about missing parameters.
                response = await super().__call__(request)  # type: ignore[call-arg]
                return response
            finally:
                # ALWAYS decrement counter, even if exception occurs
                # This ensures we don't leak connection counts
                # Logging happens inside decrement_ws_connection under the lock
                await decrement_ws_connection(client_ip)

        # ====================================================================
        # HTTP Rate Limiting (Queries and Mutations)
        # ====================================================================
        # We need to parse the GraphQL request to determine if it's a query
        # or mutation so we can apply different rate limits.
        #
        # REQUEST BODY CONSUMPTION NOTE:
        # Starlette's Request.body() caches the body after first read, allowing
        # multiple calls to body() throughout the request lifecycle. This means
        # the parent GraphQLRouter can still access the body even after we read
        # it here. See: https://github.com/encode/starlette/blob/master/starlette/requests.py
        is_mutation: bool = False  # Default to query (safer assumption for unknown operations)
        try:
            request_body: bytes = await request.body()
            if request_body:
                # Parse JSON body to extract GraphQL query
                data: dict[str, Any] = json.loads(request_body)
                query: str = data.get("query", "")

                # Simple heuristic: mutations start with "mutation" keyword
                # This covers 99% of cases. More sophisticated parsing is possible
                # but adds complexity without much benefit.
                # TODO(#123): Consider parsing operationName for more accuracy, see end of file for more details
                is_mutation = query.strip().lower().startswith("mutation")

                # Select appropriate rate limit
                rate_to_apply: str = (
                    self.mutation_rate if is_mutation
                    else self.query_rate
                )

                # Apply rate limit check
                await self._apply_rate_limit(request, rate_to_apply)

                # Log which limit was applied
                operation_type: str = "Mutation" if is_mutation else "Query"
                logger.debug(
                    f"✓ {operation_type} rate limit check passed for {client_ip}"
                )

        except RateLimitExceeded as main_rate_limit_error:
            # Rate limit exceeded - log and re-raise for FastAPI error handler
            # The re-raise is explicit (not naked) to make the flow clear
            operation_type = "Mutation" if is_mutation else "Query"
            logger.warning(
                f"🚫 {operation_type} rate limit exceeded for {client_ip}"
            )
            # raise main_rate_limit_error from None
            raise main_rate_limit_error # TODO: Review if from None is needed here

        except Exception as parse_error:
            # Couldn't parse request body - apply stricter limit as safety measure
            logger.debug(
                f"Could not parse GraphQL request for rate limiting: {parse_error}"
            )
            try:
                # Use mutation rate (stricter) when we can't determine type
                await self._apply_rate_limit(request, self.mutation_rate)
            except RateLimitExceeded as fallback_rate_limit_error:
                logger.warning(
                    f"🚫 Rate limit exceeded for {client_ip} (default/unparseable)"
                )
                raise fallback_rate_limit_error from None

        # Pass request to parent GraphQLRouter for actual GraphQL processing
        # Note: Parent expects ASGI (scope, receive, send) but FastAPI's Request
        # wraps these. This works due to Starlette's design but type checkers
        # complain about missing parameters.
        return await super().__call__(request)  # type: ignore[call-arg]

    async def _apply_rate_limit(self, request: Request, rate: str) -> None:
        """
        Apply rate limiting to a request.

        Args:
            request: The incoming request
            rate: Rate limit string (e.g., "100/minute")

        Raises:
            RateLimitExceeded: If the rate limit is exceeded

        Note:
            This method uses slowapi's decorator pattern:
            1. limiter.limit(rate) returns a decorator function
            2. The decorator wraps a callable (slowapi requirement)
            3. Calling it triggers the rate limit check
        """
        rate_limit_decorator: RateLimitDecorator = limiter.limit(rate)
        rate_limited_callable: AsyncEndpoint = rate_limit_decorator(
            self._dummy_endpoint
        )
        await rate_limited_callable(request)

    async def _dummy_endpoint(self, request: Request) -> None:
        """
        Dummy endpoint required by slowapi.

        slowapi's rate limiter wraps a callable (function/endpoint) and checks
        rate limits before calling it. We don't need the actual callable to do
        anything - we just need the rate limit check to run.

        This is a quirk of slowapi's API design.
        """
        pass

graphql_app: RateLimitedGraphQLRouter = RateLimitedGraphQLRouter(
    schema=schema,
    # Enable detailed logging for subscriptions
    subscription_protocols=["graphql-transport-ws", "graphql-ws"],
)

# Log WebSocket endpoint registration
logger.info("🔌 GraphQL WebSocket endpoint registered at /graphql")
logger.info("📡 Supported protocols: graphql-transport-ws, graphql-ws")

app.include_router(graphql_app, prefix="/graphql")

# Apply rate limiting to root endpoints
@app.get("/")
@limiter.limit(os.getenv("MYTOWER_RATE_LIMIT_QUERIES", "200/minute"))
# The `_request` parameter is required by the rate limiter decorator but is unused.
def read_root(_request: Request) -> dict[str, str]:
    logger.info("📍 Root endpoint called")
    return {"message": "MyTower GraphQL API", "graphql": "/graphql"}

@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring (no rate limit)"""
    return {"status": "healthy", "service": "MyTower GraphQL API"}

def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    logger.info(f"🚀 Starting server on {host}:{port}")
    logger.info(f"🔍 WebSocket URL: ws://{host}:{port}/graphql")
    logger.info(f"🔍 GraphQL endpoint: http://{host}:{port}/graphql")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    run_server()



# The mutation detection heuristic (line 309) using query.strip().lower().startswith("mutation") will incorrectly classify queries that have GraphQL comments before the mutation keyword. For example:

# `# Add a new floor`
# `mutation { addFloor(...) }`
# This would be treated as a query instead of a mutation, applying the wrong rate limit. While .strip() removes whitespace, it doesn't remove GraphQL comments (which start with #). Consider using a regex pattern that skips comments: re.match(r'^\s*(#[^\n]*)?\s*mutation\b', query, re.IGNORECASE) or using a GraphQL parser.
