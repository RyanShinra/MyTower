from enum import Enum
from typing import Any, List, Optional

import strawberry
from mytower.api.game_bridge import get_game_bridge
from mytower.api.graphql_types import BuildingSnapshotGQL, PersonSnapshotGQL
from mytower.api.type_conversions import convert_building_snapshot, convert_person_snapshot
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
        snapshot: BuildingSnapshot | None = get_building_state()
        return snapshot.time if snapshot else 0.0

    @strawberry.field
    def is_running(self) -> bool:
        return get_building_state() is not None

     
    @strawberry.field
    def building_state(self) -> Optional[BuildingSnapshotGQL]:
        snapshot: BuildingSnapshot | None = get_building_state()
        return convert_building_snapshot(snapshot) if snapshot else None
    
    @strawberry.field
    def all_people(self) -> Optional[List[PersonSnapshotGQL]]:
        snapshot: BuildingSnapshot | None = get_building_state()
        if not snapshot:
            return None
        return [convert_person_snapshot(p) for p in snapshot.people]

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