from typing import Any, List, Optional

import strawberry

from mytower.api import unit_scalars  # Import the module to register scalars
from mytower.api.game_bridge import get_game_bridge
from mytower.api.graphql_types import (BuildingSnapshotGQL, FloorTypeGQL,
                                       PersonSnapshotGQL)
from mytower.api.type_conversions import (convert_building_snapshot,
                                          convert_person_snapshot)
from mytower.game.controllers.controller_commands import (
    AddElevatorBankCommand, AddElevatorCommand, AddFloorCommand,
    AddPersonCommand, Command)
from mytower.game.core.types import FloorType
from mytower.game.core.units import Blocks, Meters, Pixels, Time, Velocity
from mytower.game.models.model_snapshots import BuildingSnapshot


# Convenience functions
def queue_command(command: Command[Any]) -> str:
    return get_game_bridge().queue_command(command)

def get_building_state() -> Optional[BuildingSnapshot]:
    return get_game_bridge().get_building_snapshot()


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World from MyTower!"
    
    @strawberry.field
    def game_time(self) -> Time:
        snapshot: BuildingSnapshot | None = get_building_state()
        return snapshot.time if snapshot else Time(0.0)

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



@strawberry.type  
class Mutation:
    @strawberry.mutation
    def add_floor(self, floor_type: FloorTypeGQL) -> str:
        domain_floor_type = FloorType(floor_type.value)
        command = AddFloorCommand(floor_type=domain_floor_type)
        return queue_command(command)
        
    @strawberry.mutation
    def add_person(self, floor: int, block: float, dest_floor: int, dest_block: int) -> str:
        command = AddPersonCommand(floor=floor, block=block, 
                                 dest_floor=dest_floor, dest_block=dest_block)
        return queue_command(command)
        
    @strawberry.mutation
    def add_elevator_bank(self, h_cell: int, min_floor: int, max_floor: int) -> str:
        command = AddElevatorBankCommand(h_cell=h_cell, min_floor=min_floor, max_floor=max_floor)
        return queue_command(command)

    @strawberry.mutation
    def add_elevator(self, elevator_bank_id: str) -> str:
        command = AddElevatorCommand(elevator_bank_id=elevator_bank_id)
        return queue_command(command)

    # Debug / synchronous versions of the above mutations
    # These block until the command is processed and return the result directly
    # Useful for testing and simple scripts
    # Not recommended for production use due to blocking nature
    @strawberry.mutation
    def add_floor_sync(self, floor_type: FloorTypeGQL) -> int:
        domain_floor_type = FloorType(floor_type.value)
        return get_game_bridge().execute_add_floor_sync(domain_floor_type)
        
    @strawberry.mutation
    def add_person_sync(self, floor: int, block: float, dest_floor: int, dest_block: int) -> str:
        return get_game_bridge().execute_add_person_sync(floor, block, dest_floor, dest_block)

    @strawberry.mutation
    def add_elevator_bank_sync(self, h_cell: int, min_floor: int, max_floor: int) -> str:
        return get_game_bridge().execute_add_elevator_bank_sync(h_cell, min_floor, max_floor)

    @strawberry.mutation
    def add_elevator_sync(self, elevator_bank_id: str) -> str:
        return get_game_bridge().execute_add_elevator_sync(elevator_bank_id)

schema = strawberry.Schema(
    query=Query, 
    mutation=Mutation,
    scalar_overrides={
        Time: unit_scalars.Time,
        Blocks: unit_scalars.Blocks,
        Meters: unit_scalars.Meters,
        Pixels: unit_scalars.Pixels,
        Velocity: unit_scalars.Velocity
    }
)