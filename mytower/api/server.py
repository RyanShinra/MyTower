import logging
import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from mytower.api.schema import schema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="MyTower GraphQL API")

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
origins_env = os.getenv("MYTOWER_CORS_ORIGINS", "*")
# Filter out empty strings after stripping whitespace
allowed_origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]

# Fallback to wildcard if no valid origins provided (handles empty string or whitespace-only env var)
if not allowed_origins:
    allowed_origins = ["*"]

# Disable credentials if using wildcard origins (CORS security requirement)
use_credentials = "*" not in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=use_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket subscriptions are automatically enabled in Strawberry's FastAPI integration
# Both protocols are supported by default:
# - graphql-transport-ws: Modern protocol (recommended)
# - graphql-ws: Legacy protocol for backward compatibility
# Strawberry's GraphQLRouter automatically handles protocol negotiation

# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"📨 Incoming request: {request.method} {request.url}")
    logger.info(f"🔍 Client: {request.client.host if request.client else 'unknown'}")
    logger.info(f"🔍 Headers: {dict(request.headers)}")
    response = await call_next(request)
    logger.info(f"📤 Response status: {response.status_code}")
    return response

graphql_app: GraphQLRouter[None, None] = GraphQLRouter(
    schema=schema,
    # Enable detailed logging for subscriptions
    subscription_protocols=["graphql-transport-ws", "graphql-ws"],
)

# Log WebSocket endpoint registration
logger.info("🔌 GraphQL WebSocket endpoint registered at /graphql")
logger.info("📡 Supported protocols: graphql-transport-ws, graphql-ws")

app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def read_root() -> dict[str, str]:
    logger.info("📍 Root endpoint called")
    return {"message": "MyTower GraphQL API", "graphql": "/graphql"}

@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring"""
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
