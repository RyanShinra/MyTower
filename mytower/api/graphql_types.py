# In mytower/api/schema.py

from typing import List
import strawberry


@strawberry.type
class PersonSnapshotGQL:
    person_id: str
    current_floor_num: int
    current_block_float: float
    destination_floor_num: int
    destination_block_num: int
    state: str  # Convert PersonState enum to string
    waiting_time: float
    mad_fraction: float

@strawberry.type
class ElevatorSnapshotGQL:
    id: str
    current_floor: float
    current_block: float
    destination_floor: int
    state: str  # Convert ElevatorState enum to string
    door_open: bool
    passenger_count: int
    available_capacity: int
    max_capacity: int

@strawberry.type
class FloorSnapshotGQL:
    floor_number: int
    floor_type: str  # Convert FloorType enum to string
    floor_height_blocks: int
    person_count: int

@strawberry.type
class BuildingSnapshotGQL:
    time: float
    money: int
    floors: List[FloorSnapshotGQL]
    elevators: List[ElevatorSnapshotGQL]
    people: List[PersonSnapshotGQL]