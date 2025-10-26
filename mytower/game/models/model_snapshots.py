from dataclasses import dataclass
from typing import List

from mytower.game.core.types import (RGB, Color, ElevatorState, FloorType,
                                     PersonState, VerticalDirection)
from mytower.game.core.units import Blocks, Time


@dataclass
class PersonSnapshot:
    """Immutable snapshot of person state for API consumption"""
    person_id: str
    current_floor_num: int
    current_vertical_position: Blocks
    current_horizontal_position: Blocks
    destination_floor_num: int
    destination_horizontal_position: Blocks
    state: PersonState
    waiting_time: Time
    mad_fraction: float  # 0.0 to 1.0
    draw_color: RGB  # RGB color for rendering


@dataclass
class ElevatorSnapshot:
    """Immutable snapshot of elevator state for API consumption"""
    id: str
    vertical_position: Blocks
    horizontal_position: Blocks
    destination_floor: int
    elevator_state: ElevatorState
    nominal_direction: VerticalDirection
    door_open: bool
    passenger_count: int
    available_capacity: int
    max_capacity: int

# TODO: Add Elevator references so that the GraphQL layer can resolve them
@dataclass
class ElevatorBankSnapshot:
    """Immutable snapshot of elevator bank state for API consumption"""
    id: str
    horizontal_position: Blocks
    min_floor: int
    max_floor: int
    floor_requests: dict[int, set[VerticalDirection]]  # floor number to set of requests


@dataclass
class FloorSnapshot:
    """Immutable snapshot of floor state for API consumption"""
    floor_type: FloorType
    floor_number: int  # NOTE: We'll need to think about what this means with multiple height floors
    floor_height: Blocks
    left_edge_block: Blocks
    floor_width: Blocks
    person_count: int
    floor_color: Color  # RGB color for rendering
    floorboard_color: Color  # RGB color for rendering


@dataclass
class BuildingSnapshot:
    """Complete building state snapshot for API consumption"""
    time: Time
    money: int
    floors: List[FloorSnapshot]
    elevators: List[ElevatorSnapshot]
    elevator_banks: List[ElevatorBankSnapshot]
    people: List[PersonSnapshot]

