
from mytower.game.core.types import RGB, FloorType, PersonState, ElevatorState, VerticalDirection, Color
from dataclasses import dataclass
from typing import List

from mytower.game.core.units import Blocks


@dataclass
class PersonSnapshot:
    """Immutable snapshot of person state for API consumption"""
    person_id: str
    current_floor_num: int
    current_floor_float: Blocks
    current_block_float: Blocks
    destination_floor_num: int
    destination_block_num: Blocks
    state: PersonState
    waiting_time: float
    mad_fraction: float  # 0.0 to 1.0
    draw_color: RGB  # RGB color for rendering


@dataclass
class ElevatorSnapshot:
    """Immutable snapshot of elevator state for API consumption"""
    id: str
    current_floor: Blocks
    current_block: Blocks
    destination_floor: Blocks
    state: ElevatorState
    nominal_direction: VerticalDirection
    door_open: bool
    passenger_count: int
    available_capacity: int
    max_capacity: int

@dataclass
class ElevatorBankSnapshot:
    """Immutable snapshot of elevator bank state for API consumption"""
    horizontal_block: int
    min_floor: int
    max_floor: int
    

@dataclass
class FloorSnapshot:
    """Immutable snapshot of floor state for API consumption"""
    floor_type: FloorType
    floor_number: int  # NOTE: We'll need to think about what this means with multiple height floors
    floor_height_blocks: int  
    left_edge_block: int
    floor_width_blocks: int
    person_count: int 
    floor_color: Color  # RGB color for rendering
    floorboard_color: Color  # RGB color for rendering


@dataclass
class BuildingSnapshot:
    """Complete building state snapshot for API consumption"""
    time: float
    money: int
    floors: List[FloorSnapshot]
    elevators: List[ElevatorSnapshot]
    elevator_banks: List[ElevatorBankSnapshot]
    people: List[PersonSnapshot]

