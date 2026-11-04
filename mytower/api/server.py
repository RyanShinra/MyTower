# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

import asyncio
import json
import logging
import os
import re
import threading
from collections import defaultdict
from collections.abc import Awaitable, Callable, Sequence
from typing import Final, overload, override

import uvicorn
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import HTTPConnection
from strawberry import UNSET
from strawberry.fastapi import GraphQLRouter
from strawberry.http.typevars import Context, RootValue
from strawberry.schema import BaseSchema

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
# Without them, the chained calls limiter.limit(rate)(probe) would have
# unclear Callable types.
#
# The decorator pattern works like this:
# 1. limiter.limit("100/minute") -> returns a RateLimitDecorator
# 2. decorator(probe) -> returns an AsyncEndpoint (wrapped version)
# 3. wrapped_probe(request) -> executes the rate limit check

# An async endpoint that takes a Request and returns None
# This matches the signature of the rate-limit probes below.
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
# Rate limiting is applied per client using slowapi's Limiter.
# The limiter is a module-level singleton (dependency injection pattern).
# This is standard practice for FastAPI middleware/dependencies.


def get_client_key(request: HTTPConnection) -> str:
    """
    Rate-limit bucket key for a request or WebSocket handshake.

    Behind a load balancer (the AWS deployment) every request arrives from the
    balancer's address, so keying on the socket peer would put all players in
    one bucket. The rightmost X-Forwarded-For entry is the one appended by the
    last proxy and is the only one a client cannot forge through that proxy.

    Without a proxy in front, a client can set the header freely and choose its
    own bucket. That is acceptable for the alpha; the stricter fix is uvicorn's
    proxy-headers support with FORWARDED_ALLOW_IPS set to the balancer.

    The parameter must be named ``request``: slowapi inspects the signature to
    decide whether to pass the request in.
    """
    forwarded_for: str = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        last_hop: str = forwarded_for.split(",")[-1].strip()
        if last_hop:
            return last_hop
    return get_remote_address(request)  # type: ignore[arg-type]  # only reads .client, works for WebSocket too


limiter = Limiter(key_func=get_client_key)

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
                    f"[WS] WebSocket disconnected: {ip} (0/{MAX_WS_CONNECTIONS_PER_IP})"
                )
                del ws_connections[ip]
                # Do NOT delete the lock here; keep it for future synchronization
                # TODO: Optionally implement lock cleanup if memory usage is a concern
            else:
                logger.info(
                    f"[WS] WebSocket disconnected: {ip} ({current_count}/{MAX_WS_CONNECTIONS_PER_IP})"
                )


# WebSocket subscriptions are automatically enabled in Strawberry's FastAPI integration
# Both protocols are supported by default:
# - graphql-transport-ws: Modern protocol (recommended)
# - graphql-ws: Legacy protocol for backward compatibility
# Strawberry's GraphQLRouter automatically handles protocol negotiation

# Add middleware to log all requests and apply rate limiting
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"[HTTP] Incoming request: {request.method} {request.url}")
    logger.info(f"[CHECK] Client: {request.client.host if request.client else 'unknown'}")
    logger.info(f"[CHECK] Headers: {dict(request.headers)}")
    response = await call_next(request)
    logger.info(f"[RESPONSE] Response status: {response.status_code}")
    return response

# ============================================================================
# Custom GraphQL Router with Rate Limiting
# ============================================================================
# Why override run()?
# app.include_router() copies the router's routes into the app; the router
# object itself is never called, so overriding __call__ on it does nothing.
# Strawberry's GraphQLRouter registers three closures (GET, POST, WebSocket)
# and every one of them calls self.run(request=..., context=..., root_value=...).
# Overriding run() is therefore the one place that sees every request, HTTP
# and WebSocket alike, before Strawberry executes anything.
#
# Alternative approaches considered:
# 1. Middleware: Can't differentiate query vs mutation without parsing
# 2. FastAPI dependency on include_router: one dependency list is applied to
#    both HTTP and WebSocket routes, and the two need different handling
# 3. Strawberry extension: More invasive, requires schema modification
# 4. Overriding __call__: dead code, see above (this was the original bug)
# ============================================================================

# Mutation detection. A GraphQL document may start with whitespace and
# line comments before the operation keyword; skip those, then require the
# word "mutation". Documents that select an operation by operationName from
# several definitions are not handled and fall back to the query limit.
_MUTATION_PATTERN: Final[re.Pattern[str]] = re.compile(r"^(?:\s|#[^\n]*)*mutation\b", re.IGNORECASE)


def looks_like_mutation(body: bytes) -> bool:
    """
    Classify a raw GraphQL-over-HTTP body for rate limiting.

    Returns True when the mutation (stricter) limit should apply. Anything we
    cannot read as a single {"query": "..."} document is treated as a mutation
    on purpose: the safe failure is to over-limit, not under-limit. An empty
    body (a GET, or GraphiQL) is a query.
    """
    if not body:
        return False
    try:
        payload = json.loads(body)
    except ValueError:
        return True
    if not isinstance(payload, dict):
        return True
    query = payload.get("query", "")
    if not isinstance(query, str):
        return True
    return _MUTATION_PATTERN.match(query) is not None


# slowapi counts hits per decorated function name (module.qualname) and stores
# them under that name, so queries and mutations need two distinct probes to
# get independent counters. Each probe is decorated exactly once, in the
# router's __init__. Decorating per request (the previous design) appended a
# duplicate limit to slowapi's registry on every call, which both leaked memory
# and made each request cost N hits.
async def _query_probe(request: Request) -> None:
    """Rate-limit probe for GraphQL queries. Does nothing; the decorator does the work."""


async def _mutation_probe(request: Request) -> None:
    """Rate-limit probe for GraphQL mutations. Does nothing; the decorator does the work."""


class RateLimitedGraphQLRouter(GraphQLRouter[Context, RootValue]):
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

    def __init__(
        self,
        schema: BaseSchema,
        subscription_protocols: Sequence[str] = ("graphql-transport-ws", "graphql-ws"),
    ) -> None:
        super().__init__(schema=schema, subscription_protocols=subscription_protocols)
        # Load rate limits from environment (human-readable format)
        self.query_rate: str = os.getenv("MYTOWER_RATE_LIMIT_QUERIES", "200/minute")
        self.mutation_rate: str = os.getenv("MYTOWER_RATE_LIMIT_MUTATIONS", "100/minute")

        # Bind each limit to its probe once. See the note above the probes.
        query_decorator: RateLimitDecorator = limiter.limit(self.query_rate)
        mutation_decorator: RateLimitDecorator = limiter.limit(self.mutation_rate)
        self._check_query_limit: AsyncEndpoint = query_decorator(_query_probe)
        self._check_mutation_limit: AsyncEndpoint = mutation_decorator(_mutation_probe)

        logger.info(
            f"[RATE_LIMIT] Rate limiting enabled: "
            f"Queries={self.query_rate}, Mutations={self.mutation_rate}"
        )
        logger.info(
            f"[RATE_LIMIT] WebSocket limit: "
            f"{MAX_WS_CONNECTIONS_PER_IP} concurrent connections per IP"
        )

    @overload
    async def run(
        self, request: Request, context: Context = UNSET, root_value: RootValue | None = UNSET
    ) -> Response:
        ...

    @overload
    async def run(
        self, request: WebSocket, context: Context = UNSET, root_value: RootValue | None = UNSET
    ) -> WebSocket:
        ...

    @override
    async def run(
        self,
        request: Request | WebSocket,
        context: Context = UNSET,
        root_value: RootValue | None = UNSET,
    ) -> Response | WebSocket:
        """
        Entry point for every GraphQL request (see the module note on why run()).

        HTTP requests are checked against the query or mutation limit and then
        handed to Strawberry. WebSocket handshakes are counted per client and
        refused when the client already holds the maximum number of connections.
        """
        if isinstance(request, WebSocket):
            return await self._run_websocket(request, context, root_value)

        await self._enforce_http_rate_limit(request)
        return await super().run(request=request, context=context, root_value=root_value)

    async def _enforce_http_rate_limit(self, request: Request) -> None:
        """
        Apply the query or mutation limit to one HTTP request.

        Starlette caches the body on the Request after the first read, so
        Strawberry can still read it afterwards.

        Raises:
            RateLimitExceeded: handled by the app-level handler, which returns 429.
        """
        client_key: str = get_client_key(request)
        body: bytes = await request.body()
        is_mutation: bool = looks_like_mutation(body)
        operation_type: str = "Mutation" if is_mutation else "Query"
        check: AsyncEndpoint = self._check_mutation_limit if is_mutation else self._check_query_limit
        try:
            await check(request)
        except RateLimitExceeded:
            logger.warning(f"[RATE_LIMIT] {operation_type} rate limit exceeded for {client_key}")
            raise
        logger.debug(f"[RATE_LIMIT] {operation_type} rate limit check passed for {client_key}")

    async def _run_websocket(
        self, websocket: WebSocket, context: Context, root_value: RootValue | None
    ) -> WebSocket:
        """
        Count a WebSocket connection against its client's limit for its whole lifetime.

        A refused handshake is closed before accept, which the client sees as a
        failed upgrade. The count is decremented in a finally block so a crash
        inside the subscription handler cannot leak a slot.
        """
        client_key: str = get_client_key(websocket)
        lock = await get_or_create_lock(client_key)
        async with lock:
            if ws_connections[client_key] >= MAX_WS_CONNECTIONS_PER_IP:
                logger.warning(
                    f"[RATE_LIMIT] WebSocket connection limit exceeded for {client_key}: "
                    f"{ws_connections[client_key]}/{MAX_WS_CONNECTIONS_PER_IP}"
                )
                await websocket.close(
                    code=1013,  # "Try Again Later"
                    reason=f"Maximum {MAX_WS_CONNECTIONS_PER_IP} concurrent subscriptions per client",
                )
                return websocket

            ws_connections[client_key] += 1
            current_count: int = ws_connections[client_key]
            # Log inside the lock so the count in the message is the one we set
            logger.info(f"[WS] WebSocket connected: {client_key} ({current_count}/{MAX_WS_CONNECTIONS_PER_IP})")

        try:
            return await super().run(request=websocket, context=context, root_value=root_value)
        finally:
            await decrement_ws_connection(client_key)


graphql_app: RateLimitedGraphQLRouter[None, None] = RateLimitedGraphQLRouter(
    schema=schema,
    # Enable detailed logging for subscriptions
    subscription_protocols=["graphql-transport-ws", "graphql-ws"],
)

# Log WebSocket endpoint registration
logger.info(" GraphQL WebSocket endpoint registered at /graphql")
logger.info(" Supported protocols: graphql-transport-ws, graphql-ws")

app.include_router(graphql_app, prefix="/graphql")

# Apply rate limiting to root endpoints
@app.get("/")
@limiter.limit(os.getenv("MYTOWER_RATE_LIMIT_QUERIES", "200/minute"))
# The `request` parameter is required by the rate limiter decorator but is unused.
def read_root(request: Request) -> dict[str, str]:
    logger.info("[HTTP] Root endpoint called")
    return {"message": "MyTower GraphQL API", "graphql": "/graphql"}

@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring (no rate limit)"""
    return {"status": "healthy", "service": "MyTower GraphQL API"}

async def run_server_async(
    host: str = "127.0.0.1",
    port: int = 8000,
    shutdown_event: threading.Event | None = None
) -> None:
    """
    Run the server asynchronously with graceful shutdown support.

    Args:
        host: Host to bind to
        port: Port to bind to
        shutdown_event: Optional threading.Event for graceful shutdown
    """
    logger.info(f"[START] Starting server on {host}:{port}")
    logger.info(f"[CHECK] WebSocket URL: ws://{host}:{port}/graphql")
    logger.info(f"[CHECK] GraphQL endpoint: http://{host}:{port}/graphql")

    # Create config and server
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
    )
    server = uvicorn.Server(config)

    # If shutdown_event provided, monitor it in background
    if shutdown_event is not None:
        async def shutdown_monitor():
            """Monitor shutdown event and trigger server shutdown"""
            try:
                while not shutdown_event.is_set():
                    await asyncio.sleep(0.1)
                logger.info("Shutdown event detected, stopping server...")
                server.should_exit = True
            except Exception as e:
                logger.error(f"Shutdown monitor encountered error: {e}", exc_info=True)
                server.should_exit = True

        # Start monitoring task - it will be cleaned up automatically when event loop exits
        asyncio.create_task(shutdown_monitor())

    # Run server (blocks until shutdown)
    await server.serve()
    logger.info("Server stopped")

    # The shutdown monitor will be automatically cancelled when the event loop exits.
    # No need to explicitly wait for it since it's just monitoring the shutdown_event
    # which becomes irrelevant once the server has already stopped.


def run_server(host: str = "127.0.0.1", port: int = 8000, shutdown_event: threading.Event | None = None) -> None:
    """
    Run the server with graceful shutdown support (synchronous wrapper).

    Args:
        host: Host to bind to
        port: Port to bind to
        shutdown_event: Optional threading.Event for graceful shutdown
    """
    asyncio.run(run_server_async(host, port, shutdown_event))


if __name__ == "__main__":
    run_server()
