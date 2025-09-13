from mytower.game.core.types import FloorType, PersonState, ElevatorState, VerticalDirection
from dataclasses import dataclass
from typing import List


@dataclass
class PersonSnapshot:
    """Immutable snapshot of person state for API consumption"""
    person_id: str
    current_floor_num: int
    current_floor_float: float
    current_block_float: float
    destination_floor_num: int
    destination_block_num: int
    state: PersonState
    waiting_time: float
    mad_fraction: float  # 0.0 to 1.0
    draw_color: tuple[int, int, int]
    draw_color_red: int
    draw_color_green: int
    draw_color_blue: int


@dataclass
class ElevatorSnapshot:
    """Immutable snapshot of elevator state for API consumption"""
    id: str
    current_floor: float
    current_block: float
    destination_floor: int
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
    floor_number: int
    floor_type: FloorType
    person_count: int  # Not yet implemented    


@dataclass
class BuildingSnapshot:
    """Complete building state snapshot for API consumption"""
    time: float
    money: int
    floors: List[FloorSnapshot]
    elevators: List[ElevatorSnapshot]
    people: List[PersonSnapshot]

