# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

from __future__ import annotations  # Defer type evaluation

import threading
from typing import TYPE_CHECKING, Final, override

from mytower.game.core.config import GameConfig, PersonCosmeticsProtocol
from mytower.game.core.id_generator import IDGenerator
from mytower.game.core.types import HorizontalDirection, PersonState
from mytower.game.core.units import Blocks, Meters, Time, Velocity
from mytower.game.entities.entities_protocol import BuildingProtocol, PersonProtocol, PersonTestingProtocol
from mytower.game.utilities.logger import MyTowerLogger

if TYPE_CHECKING:
    from mytower.game.entities.entities_protocol import ElevatorBankProtocol, ElevatorProtocol, FloorProtocol
    from mytower.game.utilities.logger import LoggerProvider


class Person(PersonProtocol, PersonTestingProtocol):
    """
    A person in the building who moves between floors and has needs.
    """

    NULL_PERSON_ID: Final[int] = 0
    _id_generator: IDGenerator = IDGenerator("person")
    _color_index: int = 0  # Static counter for color palette
    _color_lock: threading.Lock = threading.Lock()  # Thread safety for color index


    def __init__(
        self,
        logger_provider: LoggerProvider,
        building: BuildingProtocol,
        initial_floor_number: int,
        initial_horiz_position: Blocks,
        config: GameConfig,
    ) -> None:
        # Assign unique ID and increment counter
        self._person_id: str = Person._id_generator.get_next_id()

        self._logger: MyTowerLogger = logger_provider.get_logger("person")
        self._building: BuildingProtocol = building
        self._current_vert_position: Blocks = Blocks(initial_floor_number)
        self._current_horiz_position: Blocks = initial_horiz_position
        self._dest_horiz_position: Blocks = initial_horiz_position
        self._dest_floor_num: int = initial_floor_number
        self._state: PersonState = PersonState.IDLE
        self._direction: HorizontalDirection = HorizontalDirection.STATIONARY
        self._config: Final[GameConfig] = config
        self._cosmetics: Final[PersonCosmeticsProtocol] = config.person_cosmetics
        self._next_elevator_bank: ElevatorBankProtocol | None = None
        self._idle_timeout: Time = Time(0.0)  # Changed to Time
        self._current_elevator: ElevatorProtocol | None = None
        self._waiting_time: Time = Time(0.0)  # Changed to Time

        if initial_floor_number < 0 or initial_floor_number > building.num_floors:
            raise ValueError(f"Initial floor {initial_floor_number} is out of bounds (0-{building.num_floors})")

        if initial_horiz_position < Blocks(0) or initial_horiz_position > building.building_width:
            raise ValueError(f"Initial block {initial_horiz_position} is out of bounds (0-{building.building_width})")

        self._current_floor: FloorProtocol | None = None
        self._assign_floor(initial_floor_number)

        # Appearance (for visualization)
        # Use palette color for this person (thread-safe)
        with Person._color_lock:
            palette_color: tuple[int, int, int] = self._cosmetics.COLOR_PALETTE[
                Person._color_index % len(self._cosmetics.COLOR_PALETTE)
            ]
            Person._color_index += 1  # Increment for next person

        self._original_red: Final[int] = palette_color[0]
        self._original_green: Final[int] = palette_color[1]
        self._original_blue: Final[int] = palette_color[2]

        self._red_range: int = abs(self._cosmetics.ANGRY_MAX_RED - self._original_red)
        self._green_range: int = abs(self._cosmetics.ANGRY_MIN_GREEN - self._original_green)
        self._blue_range: int = abs(self._cosmetics.ANGRY_MIN_BLUE - self._original_blue)

    @property
    @override
    def person_id(self) -> str:
        """Get the unique person ID"""
        return self._person_id

    @property
    @override
    def building(self) -> BuildingProtocol:
        return self._building

    @property
    @override
    def current_floor_num(self) -> int:
        return int(self._current_vert_position)

    @property
    @override
    def current_vertical_position(self) -> Blocks:
        return self._current_vert_position

    @property
    @override
    def destination_horizontal_position(self) -> Blocks:
        return self._dest_horiz_position

    @property
    @override
    def current_horizontal_position(self) -> Blocks:
        return self._current_horiz_position

    @property
    @override
    def current_floor(self) -> FloorProtocol | None:
        return self._current_floor

    @property
    @override
    def destination_floor_num(self) -> int:
        return self._dest_floor_num

    @property
    @override
    def state(self) -> PersonState:
        return self._state

    @property
    @override
    def direction(self) -> HorizontalDirection:
        return self._direction

    @direction.setter
    def direction(self, value: HorizontalDirection) -> None:
        self._direction = value

    @property
    @override
    def max_velocity(self) -> Velocity:
        return self._config.person.MAX_SPEED  # 1.35 m/s

    @property
    @override
    def waiting_time(self) -> Time:
        return self._waiting_time


    @override
    def set_destination(self, dest_floor_num: int, dest_horiz_position: Blocks) -> None:
        # Check if destination values are out of bounds and raise warnings
        # TODO: This will need be revised if we ever have buildings with negative floor numbers
        if dest_floor_num < 0 or dest_floor_num > self.building.num_floors:
            raise ValueError(f"Destination floor {dest_floor_num} is out of bounds (0-{self.building.num_floors})")

        # TODO: We will need to revisit this when buildings don't start at block 0 (the far left edge of the screen)
        if dest_horiz_position < Blocks(0) or dest_horiz_position > self.building.building_width:
            raise ValueError(
                f"dest_horiz_position {dest_horiz_position} is out of bounds (0-{float(self.building.building_width)})"
            )

        # Validation passed - set destinations directly
        self._dest_floor_num = dest_floor_num
        self._dest_horiz_position = dest_horiz_position


    @override
    def find_nearest_elevator_bank(self) -> None | ElevatorBankProtocol:
        elevator_list: Final[list[ElevatorBankProtocol]] = self.building.get_elevator_banks_on_floor(
            self.current_floor_num
        )
        closest_el: ElevatorBankProtocol | None = None

        closest_dist: Blocks = self.building.building_width + Blocks(5)

        for elevator in elevator_list:
            # TODO: Add logic to skip elevator banks that don't go to dest floor
            dist: Blocks = abs(elevator.horizontal_position - self._current_horiz_position)
            if dist < closest_dist:
                closest_dist = dist
                closest_el = elevator

        return closest_el

    def _assign_floor(self, floor_num: int) -> None:
        self._current_floor = self.building.get_floor_by_number(floor_num)
        if not self._current_floor:
            raise RuntimeError(f"Cannot assign person to floor {floor_num} , the floor does not exist.")

        self._current_floor.add_person(self)

    def _clear_floor(self) -> None:
        if not self._current_floor:
            raise RuntimeError("Cannot clear floor: person is not currently on a floor.")

        self._current_floor.remove_person(self._person_id)
        self._current_floor = None


    @override
    def board_elevator(self, elevator: ElevatorProtocol) -> None:
        self._current_elevator = elevator
        self._waiting_time = Time(0.0)
        self._state = PersonState.IN_ELEVATOR

        try:
            self._clear_floor()
        except RuntimeError as e:
            raise RuntimeError(f"Person {self._person_id} is not on a floor but is trying to board an elevator.") from e


    @override
    def disembark_elevator(self) -> None:
        if self._current_elevator is None:
            raise RuntimeError("Cannot disembark elevator: no elevator is currently boarded.")

        if self.state != PersonState.IN_ELEVATOR:
            raise RuntimeError("Cannot disembark elevator: person must be in elevator state.")

        self._current_horiz_position = self._current_elevator.parent_elevator_bank.get_waiting_position()
        self._current_vert_position = Blocks(self._current_elevator.current_floor_int)

        try:
            self._assign_floor(self._current_elevator.current_floor_int)
        except RuntimeError as e:
            raise RuntimeError(
                f"Cannot disembark elevator: floor {self._current_elevator.current_floor_int} does not exist."
            ) from e

        self._waiting_time = Time(0.0)
        self._current_elevator = None
        self._next_elevator_bank = None
        self._state = PersonState.IDLE


    @override
    def update(self, dt: Time) -> None:
        """Update person's state and position"""

        match self.state:
            case PersonState.IDLE:
                self.update_idle(dt)

            case PersonState.WALKING:
                self.update_walking(dt)

            case PersonState.WAITING_FOR_ELEVATOR:
                self._waiting_time += dt
                # Eventually handle "storming off" here

            case PersonState.IN_ELEVATOR:
                if self._current_elevator:
                    self._waiting_time += dt
                    self._current_vert_position = self._current_elevator.vertical_position
                    self._current_horiz_position = self._current_elevator.parent_elevator_bank.horizontal_position

            case _:
                self._logger.warning(f"Unknown state: {self.state}")  # type: ignore[unreachable]
                raise ValueError(f"Unknown state: {self.state}")


    @override
    def update_idle(self, dt: Time) -> None:  # Changed parameter type
        self.direction = HorizontalDirection.STATIONARY

        zero_seconds: Time = Time(0.0)
        self._idle_timeout = max(zero_seconds, self._idle_timeout - dt)
        if self._idle_timeout > zero_seconds:
            return

        current_destination_block: Blocks = self._dest_horiz_position

        if self._dest_floor_num != self.current_floor_num:
            # Find the nearest elevator, go in that direction
            self._next_elevator_bank = self.find_nearest_elevator_bank()
            if self._next_elevator_bank:
                current_destination_block = self._next_elevator_bank.get_waiting_position()
                self._logger.trace(
                    f"IDLE Person: Destination fl. {self.destination_floor_num} != current fl. {self.current_floor_num} -> WALKING to Elevator block: {current_destination_block}"
                )
                self._state = PersonState.WALKING
            else:
                # There's no elevator on this floor, maybe one is coming soon...
                current_destination_block = self._current_horiz_position  # why move? There's nowhere to go
                self._logger.trace(
                    f"IDLE Person: Destination fl. {self.destination_floor_num} != current fl. {self.current_floor_num} -> IDLE b/c no Elevator on this floor"
                )
                self._state = PersonState.IDLE
                # Set a timer so that we don't run this constantly
                self._idle_timeout = self._config.person.IDLE_TIMEOUT  # Already Time type

        if current_destination_block < self._current_horiz_position:
            # Already on the right floor (or walking to elevator?)
            self._logger.trace(
                f"IDLE Person: Destination is on this floor: {self.destination_floor_num}, WALKING LEFT to block: {current_destination_block}"
            )
            self._state = PersonState.WALKING
            self.direction = HorizontalDirection.LEFT

        elif current_destination_block > self._current_horiz_position:
            self._logger.trace(
                f"IDLE Person: Destination is on this floor: {self.destination_floor_num}, WALKING RIGHT to block: {current_destination_block}"
            )
            self._state = PersonState.WALKING
            self.direction = HorizontalDirection.RIGHT


    @override
    def update_walking(self, dt: Time) -> None:  # Changed parameter type
        done: bool = False

        # TODO: Probably need a next_block_this_floor or some such for all these walking directions
        horiz_waypoint: Blocks = (
            self._next_elevator_bank.get_waiting_position() if self._next_elevator_bank else self._dest_horiz_position
        )

        if horiz_waypoint < self._current_horiz_position:
            self.direction = HorizontalDirection.LEFT
        elif horiz_waypoint > self._current_horiz_position:
            self.direction = HorizontalDirection.RIGHT

        distance: Meters = self.max_velocity * dt
        next_horiz_position: Blocks = self._current_horiz_position + distance.in_blocks * self.direction.value

        if self.direction == HorizontalDirection.RIGHT:
            if next_horiz_position >= horiz_waypoint:
                done = True
        elif self.direction == HorizontalDirection.LEFT:
            if next_horiz_position <= horiz_waypoint:
                done = True

        if done:
            self.direction = HorizontalDirection.STATIONARY
            next_horiz_position = horiz_waypoint  # Snap to exact position
            if self._next_elevator_bank:
                self._next_elevator_bank.add_waiting_passenger(self)
                self._state = PersonState.WAITING_FOR_ELEVATOR
            else:
                self._state = PersonState.IDLE
            self._logger.debug(
                f"WALKING Person: Arrived at destination (fl {self.current_floor_num}, bk {horiz_waypoint}) -> {self.state}"
            )

        # TODO: Update these with floor extents, not building extents
        if next_horiz_position < Blocks(0) or next_horiz_position > self.building.building_width:
            # TODO: Consider raising an exception here instead of just clamping
            self._logger.warning(
                f"WALKING Person: Attempted to walk out of bounds to block {next_horiz_position} on floor {self.current_floor_num}. Clamping to valid range."
            )

        next_horiz_position = min(next_horiz_position, self.building.building_width)
        next_horiz_position = max(next_horiz_position, Blocks(0))
        self._current_horiz_position = next_horiz_position


    # TESTING ONLY: Set the destination floor directly (for unit tests)
    @override
    def testing_set_dest_floor_num(self, dest_floor: int) -> None:
        if dest_floor < 0 or dest_floor > self.building.num_floors:
            self._logger.warning(
                f"[TEST] Destination floor {dest_floor} is out of bounds (0-{self.building.num_floors})"
            )
            raise ValueError(f"[TEST] Destination floor {dest_floor} is out of bounds (0-{self.building.num_floors})")
        self._dest_floor_num = min(max(dest_floor, 0), self.building.num_floors)

    @override
    def testing_confirm_horiz_dest_is(self, block: Blocks) -> bool:
        return self._dest_horiz_position == block

    @override
    def testing_set_next_elevator_bank(self, next_bank: ElevatorBankProtocol) -> None:
        self._next_elevator_bank = next_bank

    @override
    def testing_set_wait_time(self, time: Time) -> None:
        self._waiting_time = time

    @override
    def testing_get_wait_time(self) -> Time:
        return self._waiting_time

    @override
    def testing_get_max_wait_time(self) -> Time:
        return self._config.person.MAX_WAIT_TIME

    @override
    def testing_set_current_elevator(self, elevator: ElevatorProtocol) -> None:
        self._current_elevator = elevator

    @override
    def testing_get_current_elevator(self) -> ElevatorProtocol | None:
        return self._current_elevator

    @override
    def testing_get_next_elevator_bank(self) -> ElevatorBankProtocol | None:
        return self._next_elevator_bank

    @override
    def testing_set_current_vertical_position(self, cur_floor: float) -> None:
        self._current_vert_position = Blocks(cur_floor)

    @override
    def testing_get_current_vertical_position(self) -> float:
        return float(self._current_vert_position)

    @override
    def testing_set_current_horiz_position(self, cur_block: Blocks) -> None:
        self._current_horiz_position = cur_block

    @override
    def testing_set_current_state(self, state: PersonState) -> None:
        self._state = state

    @override
    def testing_set_current_floor(self, floor: FloorProtocol) -> None:
        self._current_floor = floor

    @property
    @override
    def mad_fraction(self) -> float:
        """Returns 0.0 to 1.0 based on waiting time"""
        max_wait: Time = self._config.person.MAX_WAIT_TIME
        if max_wait > Time(0.0):
            return self._waiting_time / max_wait  # Type checker knows this is float!
        return 0.0

    @property
    def draw_color_red(self) -> int:
        """As the person becomes more upset, they become more red"""
        color_red: int = self._original_red + int(self._red_range * self.mad_fraction)
        return max(0, min(254, color_red))

    @property
    def draw_color_green(self) -> int:
        """As the person becomes more upset, they become less green"""
        color_green: int = self._original_green - int(self._green_range * self.mad_fraction)
        return max(0, min(254, color_green))

    @property
    def draw_color_blue(self) -> int:
        """As the person becomes more upset, they become less blue"""
        color_blue: int = self._original_blue - int(self._blue_range * self.mad_fraction)
        return max(0, min(254, color_blue))

    @property
    @override
    def draw_color(self) -> tuple[int, int, int]:
        """Get the color for the person based on their current state"""
        return (self.draw_color_red, self.draw_color_green, self.draw_color_blue)
