from mytower.game.types import FloorType, PersonState, ElevatorState, VerticalDirection
from dataclasses import dataclass
from typing import List

@dataclass
class PersonSnapshot:
    """Immutable snapshot of person state for API consumption"""
    id: str
    current_floor: int
    current_block: float
    destination_floor: int
    destination_block: int
    state: PersonState
    waiting_time: float


@dataclass
class ElevatorSnapshot:
    """Immutable snapshot of elevator state for API consumption"""
    id: str
    current_floor: float
    destination_floor: int
    state: ElevatorState
    nominal_direction: VerticalDirection
    door_open: bool
    passenger_count: int
    available_capacity: int


@dataclass
class FloorSnapshot:
    """Immutable snapshot of floor state for API consumption"""
    floor_number: int
    floor_type: FloorType
    person_count: int


@dataclass
class BuildingSnapshot:
    """Complete building state snapshot for API consumption"""
    time: float
    money: int
    floors: List[FloorSnapshot]
    elevators: List[ElevatorSnapshot]
    people: List[PersonSnapshot]

