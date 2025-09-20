from enum import Enum
from typing import Any, Optional

import strawberry
from mytower.api.game_bridge import get_game_bridge
from mytower.game.controllers.controller_commands import (Command, 
    AddFloorCommand, AddPersonCommand, AddElevatorBankCommand, AddElevatorCommand)

from mytower.game.core.types import FloorType
from mytower.game.models.model_snapshots import BuildingSnapshot


# Convenience functions
def queue_command(command: Command[Any]) -> str:
    return get_game_bridge().queue_command(command)

def get_building_state() -> Optional[BuildingSnapshot]:
    return get_game_bridge().get_building_state()


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


@strawberry.enum
class FloorTypeGQL(Enum):
    LOBBY = "LOBBY"
    OFFICE = "OFFICE"
    APARTMENT = "APARTMENT"
    HOTEL = "HOTEL"
    RESTAURANT = "RESTAURANT"
    RETAIL = "RETAIL"

@strawberry.type  
class Mutation:
    @strawberry.field
    def add_floor(self, floor_type: FloorTypeGQL) -> str:
        domain_floor_type = FloorType(floor_type.value)
        command = AddFloorCommand(floor_type=domain_floor_type)
        return queue_command(command)
        
    @strawberry.field
    def add_person(self, floor: int, block: float, dest_floor: int, dest_block: int) -> str:
        command = AddPersonCommand(floor=floor, block=block, 
                                 dest_floor=dest_floor, dest_block=dest_block)
        return queue_command(command)
        
    @strawberry.field
    def add_elevator_bank(self, h_cell: int, min_floor: int, max_floor: int) -> str:
        command = AddElevatorBankCommand(h_cell=h_cell, min_floor=min_floor, max_floor=max_floor)
        return queue_command(command)
        
    @strawberry.field
    def add_elevator(self, elevator_bank_id: str) -> str:
        command = AddElevatorCommand(elevator_bank_id=elevator_bank_id)
        return queue_command(command)

schema = strawberry.Schema(query=Query, mutation=Mutation)