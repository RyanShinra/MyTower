import uvicorn
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from mytower.api.schema import schema

app = FastAPI(title="MyTower GraphQL API")

# WebSocket subscriptions are automatically enabled in Strawberry's FastAPI integration
# Both protocols are supported by default:
# - graphql-transport-ws: Modern protocol (recommended)
# - graphql-ws: Legacy protocol for backward compatibility
# Strawberry's GraphQLRouter automatically handles protocol negotiation

graphql_app: GraphQLRouter[None, None] = GraphQLRouter(schema=schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "MyTower GraphQL API", "graphql": "/graphql"}

def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
