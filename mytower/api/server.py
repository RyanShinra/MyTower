import logging
import os
from collections import defaultdict
from typing import DefaultDict

import uvicorn
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
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

# Initialize rate limiter
# Rate limits can be configured via environment variables:
# - MYTOWER_RATE_LIMIT_MUTATIONS: Rate limit for mutations (default: "100/minute")
# - MYTOWER_RATE_LIMIT_QUERIES: Rate limit for queries (default: "200/minute")
# - MYTOWER_MAX_WS_CONNECTIONS: Max WebSocket connections per IP (default: 10)
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="MyTower GraphQL API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
ws_connections: DefaultDict[str, int] = defaultdict(int)
MAX_WS_CONNECTIONS_PER_IP: int = int(os.getenv("MYTOWER_MAX_WS_CONNECTIONS", "10"))

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

# Custom rate-limited GraphQL router with WebSocket connection limiting
class RateLimitedGraphQLRouter(GraphQLRouter):
    """
    GraphQL router with rate limiting and WebSocket connection tracking.

    Rate limits:
    - Queries: 200/minute (configurable via MYTOWER_RATE_LIMIT_QUERIES)
    - Mutations: 100/minute (configurable via MYTOWER_RATE_LIMIT_MUTATIONS)
    - WebSocket connections: 10 concurrent per IP (configurable via MYTOWER_MAX_WS_CONNECTIONS)

    This provides defense against:
    - DoS attacks via query/mutation spam
    - Command queue exhaustion
    - Resource exhaustion from too many concurrent subscriptions
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rate limits for queries and mutations (per IP address)
        self.query_rate = os.getenv("MYTOWER_RATE_LIMIT_QUERIES", "200/minute")
        self.mutation_rate = os.getenv("MYTOWER_RATE_LIMIT_MUTATIONS", "100/minute")
        logger.info(f"🛡️  Rate limiting enabled: Queries={self.query_rate}, Mutations={self.mutation_rate}")
        logger.info(f"🛡️  WebSocket limit: {MAX_WS_CONNECTIONS_PER_IP} concurrent connections per IP")

    async def __call__(self, request: Request):
        client_ip = get_remote_address(request)

        # Check if this is a WebSocket connection (subscription)
        if request.headers.get("upgrade", "").lower() == "websocket":
            if ws_connections[client_ip] >= MAX_WS_CONNECTIONS_PER_IP:
                logger.warning(
                    f"🚫 WebSocket connection limit exceeded for {client_ip}: "
                    f"{ws_connections[client_ip]}/{MAX_WS_CONNECTIONS_PER_IP}"
                )
                # Return 429 Too Many Requests
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too many concurrent WebSocket connections",
                        "limit": MAX_WS_CONNECTIONS_PER_IP,
                        "message": f"Maximum {MAX_WS_CONNECTIONS_PER_IP} concurrent subscriptions per IP"
                    }
                )

            # Track WebSocket connection
            ws_connections[client_ip] += 1
            logger.info(f"🔌 WebSocket connected: {client_ip} ({ws_connections[client_ip]}/{MAX_WS_CONNECTIONS_PER_IP})")

            try:
                response = await super().__call__(request)
                return response
            finally:
                # Decrement connection count when WebSocket closes
                ws_connections[client_ip] -= 1
                logger.info(f"🔌 WebSocket disconnected: {client_ip} ({ws_connections[client_ip]}/{MAX_WS_CONNECTIONS_PER_IP})")

        # For regular HTTP requests (queries/mutations), apply rate limiting based on operation type
        # Parse the GraphQL request to determine if it's a query or mutation
        try:
            body = await request.body()
            if body:
                import json
                data = json.loads(body)
                query = data.get("query", "")

                # Simple heuristic: check if the query starts with "mutation"
                # More sophisticated parsing could be done, but this covers most cases
                is_mutation = query.strip().lower().startswith("mutation")

                # Apply appropriate rate limit
                if is_mutation:
                    # Stricter limit for mutations (they modify state and use command queue)
                    try:
                        await limiter.limit(self.mutation_rate)(self._dummy_endpoint)(request)
                    except RateLimitExceeded:
                        logger.warning(f"🚫 Mutation rate limit exceeded for {client_ip}")
                        raise
                else:
                    # More lenient limit for queries (read-only)
                    try:
                        await limiter.limit(self.query_rate)(self._dummy_endpoint)(request)
                    except RateLimitExceeded:
                        logger.warning(f"🚫 Query rate limit exceeded for {client_ip}")
                        raise
        except Exception as e:
            # If we can't parse the request, apply the stricter mutation limit as a safety measure
            logger.debug(f"Could not parse GraphQL request for rate limiting: {e}")
            try:
                await limiter.limit(self.mutation_rate)(self._dummy_endpoint)(request)
            except RateLimitExceeded:
                logger.warning(f"🚫 Rate limit exceeded for {client_ip} (default)")
                raise

        return await super().__call__(request)

    async def _dummy_endpoint(self, request: Request):
        """Dummy endpoint for rate limiting (slowapi requires a callable)"""
        pass

graphql_app: RateLimitedGraphQLRouter[None, None] = RateLimitedGraphQLRouter(
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
def read_root(request: Request) -> dict[str, str]:
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
