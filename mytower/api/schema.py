import strawberry
from mytower.api.game_bridge import get_game_bridge

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World from MyTower!"
    
    @strawberry.field
    def game_time(self) -> float:
        return get_game_bridge().get_game_time()
    
    @strawberry.field
    def is_running(self) -> bool:
        return get_game_bridge().get_building_state() is not None

schema = strawberry.Schema(query=Query)
