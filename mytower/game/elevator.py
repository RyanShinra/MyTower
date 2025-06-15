# game/elevator.py
# This file is part of MyTower.
#
# MyTower is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MyTower is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MyTower. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations  # Defer type evaluation

from typing import TYPE_CHECKING, List
from typing import Optional as Opt
from typing import Protocol

import pygame
from pygame import Surface

from mytower.game.constants import BLOCK_HEIGHT, BLOCK_WIDTH
from mytower.game.logger import LoggerProvider
from mytower.game.types import RGB, ElevatorState, VerticalDirection

if TYPE_CHECKING:
    from mytower.game.elevator_bank import ElevatorBank
    from mytower.game.logger import MyTowerLogger
    from mytower.game.person import Person


class ElevatorConfigProtocol(Protocol):
    """Config requirements for Elevator class"""

    @property
    def max_speed(self) -> float: ...  # noqa E701

    @property
    def max_capacity(self) -> int: ...  # noqa E701

    @property
    def passenger_loading_time(self) -> float: ...  # noqa E701

    @property
    def idle_log_timeout(self) -> float: ...  # noqa E701

    @property
    def moving_log_timeout(self) -> float: ...  # noqa E701

    @property
    def idle_wait_timeout(self) -> float: ...  # noqa E701


class ElevatorCosmeticsProtocol(Protocol):
    """Visual appearance settings for Elevator class"""

    @property
    def shaft_color(self) -> RGB: ...  # noqa E701

    @property
    def shaft_overhead(self) -> RGB: ...  # noqa E701

    @property
    def closed_color(self) -> RGB: ...  # noqa E701

    @property
    def open_color(self) -> RGB: ...  # noqa E701


class Elevator:
    """
    An elevator in the building that transports people between floors.
    """

    def __init__(
        self,
        logger_provider: LoggerProvider,
        elevator_bank: ElevatorBank,
        h_cell: int,
        min_floor: int,
        max_floor: int,
        config: ElevatorConfigProtocol,
        cosmetics_config: ElevatorCosmeticsProtocol,
    ) -> None:
        """
        Initialize a new elevator

        Args:
            building: The Building object this elevator belongs to
            x_pos: X position in grid cells
            min_floor: Lowest floor this elevator serves
            max_floor: Highest floor this elevator serves
            config: Configuration object for the elevator.
            cosmetics_config: Visual appearance configuration for the elevator.
            logger_provider: Initializes self._logger.
        """
        self._logger: MyTowerLogger = logger_provider.get_logger("Elevator")
        self._parent_elevator_bank: ElevatorBank = elevator_bank
        self._horizontal_block: int = h_cell
        self._min_floor: int = min_floor
        self._max_floor: int = max_floor
        self._config: ElevatorConfigProtocol = config
        self._cosmetics_config: ElevatorCosmeticsProtocol = cosmetics_config

        # Current state
        self._current_floor_float: float = float(min_floor)  # Floor number (can be fractional when moving)
        self._destination_floor: int = min_floor  # Let's not stop between floors
        self._door_open: bool = False
        self._state: ElevatorState = ElevatorState.IDLE
        self._motion_direction: VerticalDirection = VerticalDirection.STATIONARY  # -1 for down, 0 for stopped, 1 for up

        # Used for assignments; What people say: "is this elevator going up or down?"
        # It's only updated when a new destination is assigned
        self._nominal_direction: VerticalDirection = VerticalDirection.STATIONARY
        self._passengers: List[Person] = []  # People inside the elevator

        self._unloading_timeout: float = 0.0
        self._loading_timeout: float = 0.0
        self._idle_time: float = 0.0
        self._last_logged_state: Opt[ElevatorState] = None  # Track the last logged state
        self._idle_log_timer: float = 0.0
        self._moving_log_timer: float = 0.0

    @property
    def state(self) -> ElevatorState:
        return self._state

    def testing_set_state(self, state: ElevatorState) -> None:
        self._state = state

    @property
    def avail_capacity(self) -> int:
        return self._config.max_capacity - len(self._passengers)

    @property
    def is_empty(self) -> bool:
        return len(self._passengers) == 0

    @property
    def motion_direction(self) -> VerticalDirection:
        return self._motion_direction

    def testing_set_motion_direction(self, direction: VerticalDirection) -> None:
        self._motion_direction = direction

    @property
    def nominal_direction(self) -> VerticalDirection:
        return self._nominal_direction

    def testing_set_nominal_direction(self, direction: VerticalDirection) -> None:
        self._nominal_direction = direction
    
    @property
    def current_floor_int(self) -> int:
        return int(self._current_floor_float)

    def testing_set_current_floor(self, floor: float) -> None:
        if not (self.min_floor <= floor <= self.max_floor):
            raise ValueError(
                f"Testing floor {floor} is out of bounds. Valid range: {self.min_floor} to {self.max_floor}."
            )
        self._current_floor_float = float(floor)

    @property
    def fractional_floor(self) -> float:
        return self._current_floor_float

    @property
    def parent_elevator_bank(self) -> ElevatorBank:
        return self._parent_elevator_bank

    @property
    def horizontal_block(self) -> int:
        return self._horizontal_block

    @property
    def door_open(self) -> bool:
        return self._door_open

    @door_open.setter
    def door_open(self, value: bool) -> None:
        self._door_open = value

    @property
    def min_floor(self) -> int:
        return self._min_floor

    @property
    def max_floor(self) -> int:
        return self._max_floor

    @property
    def max_velocity(self) -> float:
        return self._config.max_speed

    @property
    def idle_wait_timeout(self) -> float:  # Added public property for idle_wait_timeout
        return self._config.idle_wait_timeout

    @property
    def destination_floor(self) -> int:
        return self._destination_floor

    @property
    def idle_time(self) -> float:
        return self._idle_time

    @idle_time.setter
    def idle_time(self, value: float) -> None:
        self._idle_time = value


    def set_destination_floor(self, dest_floor: int) -> None:
        if (dest_floor > self.max_floor) or (dest_floor < self.min_floor):
            raise ValueError(
                f"Destination floor {dest_floor} is out of bounds. Valid range: {self.min_floor} to {self.max_floor}."
            )

        self._logger.info(
            f"{self.state} Elevator: Setting destination floor to {dest_floor} from current floor {self.current_floor_int}"
        )
        if self.current_floor_int < dest_floor:
            self._logger.info(f"{self.state} Elevator: Going UP")
            self._motion_direction = VerticalDirection.UP
            self._nominal_direction = VerticalDirection.UP
        elif self.current_floor_int > dest_floor:
            self._logger.info(f"{self.state} Elevator: Going DOWN")
            self._motion_direction = VerticalDirection.DOWN
            self._nominal_direction = VerticalDirection.DOWN
        else:
            self._logger.info(f"{self.state} Elevator: Going NOWHERE")
            self._motion_direction = VerticalDirection.STATIONARY
            self._nominal_direction = VerticalDirection.STATIONARY
        self._destination_floor = dest_floor

    def testing_set_passengers(self, passengers: List[Person]) -> None:
        """Set passengers directly for testing purposes."""
        if len(passengers) > self._config.max_capacity:
            raise ValueError(f"Cannot set {len(passengers)} passengers: exceeds max capacity of {self._config.max_capacity}")
        self._passengers = passengers.copy()  # Defensive copy
        
    def testing_get_passengers(self) -> List[Person]:
        return self._passengers.copy()

    def request_load_passengers(self, direction: VerticalDirection) -> None:
        if self.state == ElevatorState.IDLE:
            self._state = ElevatorState.LOADING
            self._nominal_direction = direction
            self._logger.info(f"{self.state} Elevator: Loading: {direction}")
        else:
            self._logger.warning(
                f"{self.state} Elevator: Cannot load passengers while elevator is in {self.state} state"
            )
            raise RuntimeError(f"{self.state} Elevator: Cannot load passengers while elevator is in {self.state} state")

    def passengers_who_want_off(self) -> List[Person]:
        answer: List[Person] = []
        for p in self._passengers:
            if p.destination_floor == self.current_floor_int:
                answer.append(p)

        return answer

    def get_passenger_destinations_in_direction(self, floor: int, direction: VerticalDirection) -> List[int]:
        """Returns sorted list of floors in the direction of travel"""

        if direction == VerticalDirection.STATIONARY:
            self._logger.error(f"{self.state} Elevator: Invalid direction STATIONARY for floor {floor}")
            return []

        floors_set: set[int] = set()
        for p in self._passengers:
            if direction == VerticalDirection.UP and p.destination_floor > floor:
                floors_set.add(p.destination_floor)

            elif direction == VerticalDirection.DOWN and p.destination_floor < floor:
                floors_set.add(p.destination_floor)

        sorted_floors: List[int] = list(floors_set)
        if direction == VerticalDirection.UP:
            sorted_floors.sort()
        elif direction == VerticalDirection.DOWN:
            sorted_floors.sort(reverse=True)

        return sorted_floors

    def update(self, dt: float) -> None:
        """Update elevator status over time increment dt (in seconds)"""
        if self._state != self._last_logged_state:
            self._logger.info(f"Elevator state changed to: {self._state}")
            self._last_logged_state = self._state

        match self._state:
            case ElevatorState.IDLE:
                # Arrived at the floor w/ nobody who wanted to disembark on this floor
                self.door_open = False
                self._update_idle(dt)

            case ElevatorState.MOVING:
                # Continue moving towards the destination floor
                self.door_open = False
                self._update_moving(dt)

            case ElevatorState.ARRIVED:
                # Arrived at a floor, check if anyone wants to get off
                self._update_arrived(dt)

            case ElevatorState.UNLOADING:
                # Allow people to exit the elevator
                self.door_open = True
                self._update_unloading(dt)

            case ElevatorState.LOADING:
                # Allow people to enter or exit the elevator
                self.door_open = True
                self._update_loading(dt)

            case ElevatorState.READY_TO_MOVE:
                # Just finished loading, decide where to go next
                self.door_open = False
                self._update_ready_to_move(dt)

            case _:
                # pragma: no cover
                self._logger.error(f"Unknown elevator state: {self._state}")  # type: ignore[unreachable]

                raise ValueError(f"Unknown elevator state: {self._state}")

    def _update_idle(self, dt: float) -> None:
        self._idle_log_timer += dt
        if self._idle_log_timer >= self._config.idle_log_timeout:
            self._logger.trace(f"{self.state} Elevator: Elevator is idle on floor {self.current_floor_int}")
            self._idle_log_timer = 0.0
        self._motion_direction = VerticalDirection.STATIONARY

    def _update_moving(self, dt: float) -> None:
        dy: float = dt * self.max_velocity * self.motion_direction.value
        cur_floor: float = self._current_floor_float + dy
        if self._moving_log_timer >= self._config.moving_log_timeout:
            self._logger.trace(
                f"{self.state} Elevator: Elevator moving {self.motion_direction} from floor {self._current_floor_float} to {cur_floor}"
            )
            self._moving_log_timer = 0.0

        done: bool = False

        if self.motion_direction == VerticalDirection.UP:
            if cur_floor >= self.destination_floor:
                done = True
        elif self.motion_direction == VerticalDirection.DOWN:
            if cur_floor <= self.destination_floor:
                done = True

        if done:
            self._logger.info(
                f"{self.state} Elevator: The elevator has arrived from moving {self.motion_direction} -> ARRIVED"
            )
            cur_floor = self.destination_floor
            self._state = ElevatorState.ARRIVED
            self._motion_direction = VerticalDirection.STATIONARY

        cur_floor = min(self.max_floor, cur_floor)
        cur_floor = max(self.min_floor, cur_floor)
        self._current_floor_float = cur_floor

    def _update_arrived(self, dt: float) -> None:
        who_wants_off: List[Person] = self.passengers_who_want_off()

        if len(who_wants_off) > 0:
            self._state = ElevatorState.UNLOADING
        else:
            self._state = ElevatorState.IDLE
        self._logger.debug(
            f"{self.state} Elevator: Having arrived, elevator has {len(who_wants_off)} passengers to disembark -> {self._state}"
        )

    def _update_unloading(self, dt: float) -> None:
        self._unloading_timeout += dt
        if self._unloading_timeout < self._config.passenger_loading_time:
            return

        self._unloading_timeout = 0.0
        who_wants_off: List[Person] = self.passengers_who_want_off()

        if len(who_wants_off) > 0:
            self._logger.debug(f"{self.state} Elevator: Unloading Passenger")
            disembarking_passenger: Person = who_wants_off.pop()
            self._passengers.remove(disembarking_passenger)
            disembarking_passenger.disembark_elevator()
        else:
            self._logger.debug(f"{self.state} Elevator: Unloading Complete -> LOADING")
            self._state = ElevatorState.LOADING
        return

    def _update_loading(self, dt: float) -> None:
        self._loading_timeout += dt
        if self._loading_timeout < self._config.passenger_loading_time:
            return

        self._loading_timeout = 0.0

        # We could have an "Overstuffed" option here in the future
        if self.avail_capacity <= 0:
            self._logger.info(f"{self.state} Elevator: Loading at Capacity -> READY_TO_MOVE")
            self._state = ElevatorState.READY_TO_MOVE  # We're full, get ready to move
            self.door_open = False
            return

        # There is still room, add a person
        self._logger.debug(
            f"{self.state} Elevator: Trying to dequeue a passenger going {self.nominal_direction} from {self.current_floor_int}"
        )
        who_wants_on: Person | None = self.parent_elevator_bank.try_dequeue_waiting_passenger(
            self.current_floor_int, self.nominal_direction
        )
        if who_wants_on is not None:
            who_wants_on.board_elevator(self)
            self._passengers.append(who_wants_on)
        else:
            self._logger.debug(f"{self.state} Elevator: Loading Complete: No more willing passengers -> READY_TO_MOVE")
            self._state = ElevatorState.READY_TO_MOVE  # Nobody else wants to get on
            self.door_open = False
        return

    def _update_ready_to_move(self, dt: float) -> None:
        self._logger.debug(
            f"{self.state} Elevator: Elevator ready to move from floor {self.current_floor_int} to {self.destination_floor}"
        )
        if self.current_floor_int != self.destination_floor:
            self._logger.info(
                f"{self.state} Elevator: Elevator starting to MOVE {self.nominal_direction} towards floor {self.destination_floor}"
            )
            self._state = ElevatorState.MOVING
        else:
            self._logger.info(f"{self.state} Elevator: No Destination -> IDLE")
            self._state = ElevatorState.IDLE

    def draw(self, surface: Surface) -> None:
        """Draw the elevator on the given surface"""
        # Calculate positions
        screen_height = surface.get_height()
        #   450 = 480 - (1.5 * 20)
        # We want the private member here since it's a float and we're computing pixels
        car_top = screen_height - int(self._current_floor_float * BLOCK_HEIGHT)
        shaft_left = self._horizontal_block * BLOCK_WIDTH
        width = BLOCK_WIDTH

        # Draw shaft from min to max floor
        #     420 = 480 - (3 * 20)
        # shaft_top = screen_height - (self._max_floor * BLOCK_HEIGHT)
        # shaft_overhead = screen_height - ((self._max_floor + 1) * BLOCK_HEIGHT)
        #     480 = 480 - ((1 - 1) * 20)
        # shaft_bottom = screen_height - ((self._min_floor - 1) * BLOCK_HEIGHT)
        # pygame.draw.rect(
        #     surface,
        #     self._cosmetics_config.shaft_color,
        #     (shaft_left, shaft_top, width, shaft_bottom - shaft_top)
        # )

        # pygame.draw.rect(
        #     surface,
        #     UI_TEXT_COLOR,
        #     (shaft_left, shaft_overhead, width, shaft_top - shaft_overhead)
        # )

        # Draw elevator car
        color = self._cosmetics_config.open_color if self.door_open else self._cosmetics_config.closed_color
        pygame.draw.rect(surface, color, (shaft_left, car_top, width, BLOCK_HEIGHT))

        # Draw any passengers or other elements after the elevator
        # to make them appear on top of the elevator
        # TODO: Depending on the size of the passenger icon, we can add judder here later to make it look crowded
        for p in self._passengers:
            p.draw(surface)
