"""
Entity protocols for MyTower game.
Defines interfaces for game entities to avoid circular imports and improve testability.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Protocol, List, Sequence, Any
from mytower.game.core.units import Blocks, Velocity, Time
from mytower.game.core.types import HorizontalDirection, PersonState, ElevatorState, VerticalDirection, FloorType, Color

if TYPE_CHECKING:
    pass  # All references are now forward-references via string literals or protocol types


class PersonProtocol(Protocol):
    """Protocol defining the interface for Person entities"""
    
    @property
    def current_floor_num(self) -> int: ...
    
    @property
    def current_floor_float(self) -> Blocks: ...

    @property
    def destination_floor_num(self) -> int: ...
    
    @property
    def current_block_float(self) -> Blocks: ...
    
    @property
    def current_floor(self) -> FloorProtocol | None: ...  # Changed
    
    @property
    def destination_block_num(self) -> Blocks: ...
    
    @property
    def person_id(self) -> str: ...
    
    @property
    def state(self) -> PersonState: ...
    
    @property
    def direction(self) -> HorizontalDirection: ...
    
    @direction.setter
    def direction(self, value: HorizontalDirection) -> None: ...
    
    @property
    def max_velocity(self) -> Velocity: ...
    
    @property
    def building(self) -> BuildingProtocol: ...  # Changed
    
    @property
    def waiting_time(self) -> Time: ...
    
    @property
    def mad_fraction(self) -> float: ...
    
    @property
    def draw_color(self) -> tuple[int, int, int]: ...

    def set_destination(self, dest_floor_num: int, dest_block_num: Blocks) -> None: ...
    
    def find_nearest_elevator_bank(self) -> None | ElevatorBankProtocol: ...  # Changed
    
    def board_elevator(self, elevator: ElevatorProtocol) -> None: ...  # Changed
    
    def disembark_elevator(self) -> None: ...

    def update(self, dt: Time) -> None: ...

    def update_idle(self, dt: Time) -> None: ...

    def update_walking(self, dt: Time) -> None: ...

    def testing_set_dest_floor_num(self, dest_floor: int) -> None: ...


class ElevatorProtocol(Protocol):
    """Protocol defining the interface for Elevator entities"""
    
    @property
    def elevator_id(self) -> str: ...
    
    @property
    def state(self) -> ElevatorState: ...
    
    @property
    def current_floor_int(self) -> int: ...
    
    @property
    def fractional_floor(self) -> Blocks: ...
    
    @property
    def current_block_float(self) -> Blocks: ...
    
    @property
    def destination_floor(self) -> int: ...
    
    @property
    def max_velocity(self) -> Velocity: ...
    
    @property
    def min_floor(self) -> int: ...
    
    @property
    def max_floor(self) -> int: ...
    
    @property
    def passenger_count(self) -> int: ...
    
    @property
    def max_capacity(self) -> int: ...
    
    @property
    def avail_capacity(self) -> int: ...
    
    @property
    def door_open(self) -> bool: ...
    
    @door_open.setter
    def door_open(self, value: bool) -> None: ...
    
    @property
    def motion_direction(self) -> VerticalDirection: ...
    
    @property
    def nominal_direction(self) -> VerticalDirection: ...
    
    @property
    def parent_elevator_bank(self) -> ElevatorBankProtocol: ...
    
    @property
    def is_empty(self) -> bool: ...
    
    @property
    def idle_time(self) -> Time: ...
    
    @idle_time.setter
    def idle_time(self, value: Time) -> None: ...
    
    @property
    def idle_wait_timeout(self) -> Time: ...
    
    def set_destination_floor(self, dest_floor: int) -> None: ...
    
    def update(self, dt: Time) -> None: ...
    
    def get_passenger_destinations_in_direction(self, floor: int, direction: VerticalDirection) -> List[int]: ...
    
    def request_load_passengers(self, direction: VerticalDirection) -> None: ...
    
    def passengers_who_want_off(self) -> List[PersonProtocol]: ...


class ElevatorTestingProtocol(Protocol):
    """Testing-only protocol for Elevator - provides internal state access for unit tests"""
    
    def testing_set_state(self, state: ElevatorState) -> None: ...
    
    def testing_set_motion_direction(self, direction: VerticalDirection) -> None: ...
    
    def testing_set_nominal_direction(self, direction: VerticalDirection) -> None: ...
    
    def testing_set_current_floor(self, floor: Blocks) -> None: ...
    
    def testing_set_passengers(self, passengers: Sequence[PersonProtocol]) -> None: ...
    
    def testing_get_passengers(self) -> List[PersonProtocol]: ...


class ElevatorBankProtocol(Protocol):
    """Protocol defining the interface for ElevatorBank entities"""
    
    @property
    def elevator_bank_id(self) -> str: ...
    
    @property
    def horizontal_block(self) -> Blocks: ...
    
    @property
    def min_floor(self) -> int: ...
    
    @property
    def max_floor(self) -> int: ...
    
    @property
    def elevators(self) -> List[ElevatorProtocol]: ...  # Changed

    def get_waiting_block(self) -> Blocks: ...
    
    def add_waiting_passenger(self, passenger: PersonProtocol) -> None: ...
    
    def request_elevator(self, floor: int, direction: VerticalDirection) -> None: ...
    
    def try_dequeue_waiting_passenger(self, floor: int, direction: VerticalDirection) -> PersonProtocol | None: ...


class ElevatorBankTestingProtocol(Protocol):
    """Testing-only protocol for ElevatorBank"""
    
    def testing_get_upward_queue(self, floor: int) -> Any: ...  # Returns deque but avoid circular import
    
    def testing_get_downward_queue(self, floor: int) -> Any: ...
    
    def testing_update_idle_elevator(self, elevator: ElevatorProtocol, dt: Time) -> None: ...  # Changed
    
    def testing_update_ready_elevator(self, elevator: ElevatorProtocol) -> None: ...  # Changed
    
    def testing_collect_destinations(self, elevator: ElevatorProtocol, floor: int, direction: VerticalDirection) -> List[int]: ...  # Changed
    
    def testing_select_next_floor(self, destinations: List[int], direction: VerticalDirection) -> int: ...


class FloorProtocol(Protocol):
    """Protocol defining the interface for Floor entities"""
    
    @property
    def floor_num(self) -> int: ...
    
    @property
    def floor_type(self) -> FloorType: ...
    
    @property
    def width(self) -> Blocks: ...
    
    @property
    def height(self) -> Blocks: ...
    
    @property
    def left_edge(self) -> Blocks: ...
    
    @property
    def number_of_people(self) -> int: ...
    
    @property
    def color(self) -> Color: ...
    
    @property
    def floorboard_color(self) -> Color: ...
    
    def add_person(self, person: PersonProtocol) -> None: ...
    
    def remove_person(self, person_id: str) -> None: ...


class BuildingProtocol(Protocol):
    """Protocol defining the interface for Building entities"""
    
    @property
    def num_floors(self) -> int: ...
    
    @property
    def floor_width(self) -> Blocks: ...
    
    @property
    def people(self) -> List[PersonProtocol]: ...  # Add this - Building has a people property
    
    def add_floor(self, floor_type: FloorType) -> int: ...
    
    def get_floor_by_number(self, floor_num: int) -> FloorProtocol | None: ...
    
    def add_elevator_bank(self, elevator_bank: ElevatorBankProtocol) -> None: ...
    
    def get_elevator_banks(self) -> List[ElevatorBankProtocol]: ...
    
    def get_elevator_banks_on_floor(self, floor_num: int) -> List[ElevatorBankProtocol]: ...
    
    def get_elevators(self) -> List[ElevatorProtocol]: ...
    
    def get_floors(self) -> List[FloorProtocol]: ...  # Add this
    
    def add_person(self, person: PersonProtocol) -> None: ...
    
    def remove_person(self, person_id: str) -> None: ...  # Add this - was missing
    
    def update(self, dt: Time) -> None: ...  # Changed from float to Time


class PersonTestingProtocol(Protocol):
    """Testing-only protocol for Person - provides internal state access for unit tests"""
    
    def testing_set_dest_floor_num(self, dest_floor: int) -> None: ...
    
    def testing_confirm_dest_block_is(self, block: Blocks) -> bool: ...
    
    def testing_set_next_elevator_bank(self, next_bank: ElevatorBankProtocol) -> None: ...  # Changed
    
    def testing_set_wait_time(self, time: Time) -> None: ...
    
    def testing_get_wait_time(self) -> Time: ...
    
    def testing_get_max_wait_time(self) -> Time: ...
    
    def testing_set_current_elevator(self, elevator: ElevatorProtocol) -> None: ...  # Changed
    
    def testing_get_current_elevator(self) -> ElevatorProtocol | None: ...  # Changed
    
    def testing_get_next_elevator_bank(self) -> ElevatorBankProtocol | None: ...  # Changed
    
    def testing_set_current_floor_float(self, cur_floor: float) -> None: ...
    
    def testing_get_current_floor_float(self) -> float: ...
    
    def testing_set_current_block_float(self, cur_block: Blocks) -> None: ...
    
    def testing_set_current_state(self, state: PersonState) -> None: ...
    
    def testing_set_current_floor(self, floor: FloorProtocol) -> None: ...  # Changed
