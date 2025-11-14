import logging

import uvicorn
from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter

from mytower.api.schema import schema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="MyTower GraphQL API")

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
