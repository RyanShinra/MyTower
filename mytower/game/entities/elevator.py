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

from typing import TYPE_CHECKING, Final, List
from typing import Optional as Opt
from typing import Sequence, override

from mytower.game.core.config import (ElevatorConfigProtocol,
                                      ElevatorCosmeticsProtocol)
from mytower.game.core.id_generator import IDGenerator
from mytower.game.core.types import ElevatorState, VerticalDirection
from mytower.game.core.units import (Blocks, Meters, Time,  # Add Velocity
                                     Velocity)
from mytower.game.entities.entities_protocol import (ElevatorBankProtocol,
                                                     ElevatorDestination,
                                                     ElevatorProtocol,
                                                     ElevatorTestingProtocol,
                                                     PersonProtocol)
from mytower.game.utilities.logger import LoggerProvider

if TYPE_CHECKING:
    from mytower.game.utilities.logger import MyTowerLogger

# flake8: noqa: E701


class Elevator(ElevatorProtocol, ElevatorTestingProtocol):
    """
    An elevator in the building that transports people between floors.
    """

    _id_generator: IDGenerator = IDGenerator("elevator")

    def __init__(
        self,
        logger_provider: LoggerProvider,
        elevator_bank: ElevatorBankProtocol,  # Changed to protocol
        min_floor: int,
        max_floor: int,
        config: ElevatorConfigProtocol,
        cosmetics_config: ElevatorCosmeticsProtocol,
        starting_floor: int | None = None,
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
        # Assign unique ID and increment counter
        self._elevator_id: str = Elevator._id_generator.get_next_id()

        self._logger: MyTowerLogger = logger_provider.get_logger("Elevator")
        self._parent_elevator_bank: ElevatorBankProtocol = elevator_bank

        self._min_floor: int = min_floor
        self._max_floor: int = max_floor
        self._config: ElevatorConfigProtocol = config
        self._cosmetics_config: ElevatorCosmeticsProtocol = cosmetics_config

        # Current state
        self._vertical_position: Blocks = Blocks(min_floor if starting_floor is None else starting_floor)  # Floor number (can be fractional when moving)
        self._destination_floor: int = min_floor if starting_floor is None else starting_floor  # Let's not stop between floors
        self._door_open: bool = False
        self._state: ElevatorState = ElevatorState.IDLE
        self._motion_direction: VerticalDirection = VerticalDirection.STATIONARY  # -1 for down, 0 for stopped, 1 for up

        # Used for assignments; What people say: "is this elevator going up or down?"
        # It's only updated when a new destination is assigned
        self._nominal_direction: VerticalDirection = VerticalDirection.STATIONARY
        self._passengers: List[PersonProtocol] = []  # People inside the elevator

        self._unloading_timeout: Time = Time(0.0)
        self._loading_timeout: Time = Time(0.0)
        self._idle_time: Time = Time(0.0)
        self._last_logged_state: Opt[ElevatorState] = None  # Track the last logged state
        self._idle_log_timer: Time = Time(0.0)
        self._moving_log_timer: Time = Time(0.0)

    @property
    @override
    def elevator_id(self) -> str:
        """Get the unique elevator ID"""
        return self._elevator_id

    @property
    @override
    def elevator_state(self) -> ElevatorState:
        return self._state

    @override
    def testing_set_state(self, state: ElevatorState) -> None:
        self._state = state

    @property
    @override
    def avail_capacity(self) -> int:
        return self._config.MAX_CAPACITY - len(self._passengers)

    @property
    @override
    def max_capacity(self) -> int:
        return self._config.MAX_CAPACITY

    @property
    @override
    def passenger_count(self) -> int:
        return len(self._passengers)

    @property
    @override
    def is_empty(self) -> bool:
        return len(self._passengers) == 0

    @property
    @override
    def motion_direction(self) -> VerticalDirection:
        return self._motion_direction

    @override
    def testing_set_motion_direction(self, direction: VerticalDirection) -> None:
        self._motion_direction = direction

    @property
    @override
    def nominal_direction(self) -> VerticalDirection:
        return self._nominal_direction

    @override
    def testing_set_nominal_direction(self, direction: VerticalDirection) -> None:
        self._nominal_direction = direction

    @property
    @override
    def current_floor_int(self) -> int:
        return int(self._vertical_position)

    @override
    def testing_set_current_vertical_pos(self, floor: Blocks) -> None:
        if not (self.min_floor <= int(floor) <= self.max_floor):
            raise ValueError(
                f"Testing floor {floor} is out of bounds. Valid range: {self.min_floor} to {self.max_floor}."
            )
        self._vertical_position = floor

    @property
    @override
    def vertical_position(self) -> Blocks:
        return self._vertical_position

    @property
    @override
    def horizontal_position(self) -> Blocks:
        return self._parent_elevator_bank.horizontal_position

    @property
    @override
    def parent_elevator_bank(self) -> ElevatorBankProtocol:
        return self._parent_elevator_bank

    @property
    @override
    def door_open(self) -> bool:
        return self._door_open

    @door_open.setter
    @override
    def door_open(self, value: bool) -> None:
        self._door_open = value

    @property
    @override
    def min_floor(self) -> int:
        return self._min_floor

    @property
    @override
    def max_floor(self) -> int:
        return self._max_floor

    @property
    @override
    def max_velocity(self) -> Velocity:  # Changed return type from float
        return self._config.MAX_SPEED

    @property
    @override
    def idle_wait_timeout(self) -> Time:  # Added public property for idle_wait_timeout
        return self._config.IDLE_WAIT_TIMEOUT

    @property
    @override
    def destination_floor(self) -> int:
        return self._destination_floor

    @property
    @override
    def idle_time(self) -> Time:
        return self._idle_time

    @idle_time.setter
    @override
    def idle_time(self, value: Time) -> None:
        self._idle_time = value

    @override
    def set_destination(self, destination: ElevatorDestination) -> None:
        if (destination.floor > self.max_floor) or (destination.floor < self.min_floor):
            raise ValueError(
                f"Destination floor {destination} is out of bounds. Valid range: {self.min_floor} to {self.max_floor}."
            )

        self._logger.info(
            f"{self.elevator_state} Elevator: Setting destination floor to {destination} from current floor {self.current_floor_int}"
        )
        if self.current_floor_int < destination.floor:
            self._logger.info(f"{self.elevator_state} Elevator: Going UP")
            self._motion_direction = VerticalDirection.UP
            self._nominal_direction = destination.direction
            self._state = ElevatorState.READY_TO_MOVE

        elif self.current_floor_int > destination.floor:
            self._logger.info(f"{self.elevator_state} Elevator: Going DOWN")
            self._motion_direction = VerticalDirection.DOWN
            self._nominal_direction = destination.direction
            self._state = ElevatorState.READY_TO_MOVE

        else:
            self._logger.info(f"{self.elevator_state} Elevator: Going NOWHERE")
            self._motion_direction = VerticalDirection.STATIONARY
            self._nominal_direction = VerticalDirection.STATIONARY
            self._state = ElevatorState.IDLE

        self._destination_floor = destination.floor

    @override
    def testing_set_passengers(self, passengers: Sequence[PersonProtocol]) -> None:
        """Set passengers directly for testing purposes."""
        if len(passengers) > self._config.MAX_CAPACITY:
            raise ValueError(f"Cannot set {len(passengers)} passengers: exceeds max capacity of {self._config.MAX_CAPACITY}")
        self._passengers = list(passengers)  # Defensive copy

    @override
    def testing_get_passengers(self) -> List[PersonProtocol]:
        return self._passengers.copy()

    @override
    def request_load_passengers(self, direction: VerticalDirection) -> None:
        """Instructs an idle elevator to begin loading and sets it to nominally go in `direction`.
           The actual loading will happen on the next time step, after evaluating the state machine.
           Other valid loading states may become possible in the future.
        """
        if self.elevator_state == ElevatorState.IDLE:
            self._state = ElevatorState.LOADING
            self._nominal_direction = direction
            self._logger.info(f"{self.elevator_state} Elevator: Loading: {direction}")
        else:
            err_str: str = f"{self.elevator_state} Elevator: Cannot load passengers while elevator is in {self.elevator_state} state"
            self._logger.warning(err_str)
            raise RuntimeError(err_str)

    @override
    def passengers_who_want_off(self) -> List[PersonProtocol]:
        answer: Final[List[PersonProtocol]] = []
        for p in self._passengers:
            if p.destination_floor_num == self.current_floor_int:
                answer.append(p)

        return answer

    @override
    def get_passenger_destinations_in_direction(self, floor: int, direction: VerticalDirection) -> List[int]:
        """Returns sorted list of floors in the direction of travel"""

        if direction == VerticalDirection.STATIONARY:
            self._logger.error(f"{self.elevator_state} Elevator: Invalid direction STATIONARY for floor {floor}")
            return []

        floors_set: set[int] = set()
        for p in self._passengers:
            if direction == VerticalDirection.UP and p.destination_floor_num > floor:
                floors_set.add(p.destination_floor_num)

            elif direction == VerticalDirection.DOWN and p.destination_floor_num < floor:
                floors_set.add(p.destination_floor_num)

        sorted_floors: Final[List[int]] = list(floors_set)
        if direction == VerticalDirection.UP:
            sorted_floors.sort()
        elif direction == VerticalDirection.DOWN:
            sorted_floors.sort(reverse=True)

        return sorted_floors

    @override
    def update(self, dt: Time) -> None:
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

    def _update_idle(self, dt: Time) -> None:
        self._idle_log_timer += dt
        if self._idle_log_timer >= self._config.IDLE_LOG_TIMEOUT:
            self._logger.trace(f"{self.elevator_state} Elevator: Elevator is idle on floor {self.current_floor_int}")
            self._idle_log_timer = Time(0.0)
        self._motion_direction = VerticalDirection.STATIONARY

    def _update_moving(self, dt: Time) -> None:
        # Physics with proper units - type checker now knows this is Meters!
        distance: Meters = self.max_velocity * dt  # No cast needed!
        dy_blocks: Blocks = distance.in_blocks

        cur_floor: float = float(self._vertical_position) + float(dy_blocks) * self.motion_direction.value

        if self._moving_log_timer >= self._config.MOVING_LOG_TIMEOUT:
            self._logger.trace(
                f"{self.elevator_state} Elevator: Moving {self.motion_direction} from {self._vertical_position} to {cur_floor}"
            )
            self._moving_log_timer = Time(0.0)

        done: bool = False

        if self.motion_direction == VerticalDirection.UP:
            if cur_floor >= self.destination_floor:
                done = True
        elif self.motion_direction == VerticalDirection.DOWN:
            if cur_floor <= self.destination_floor:
                done = True

        if done:
            self._logger.info(
                f"{self.elevator_state} Elevator: Arrived from moving {self.motion_direction} -> ARRIVED"
            )
            cur_floor = float(self.destination_floor)
            self._state = ElevatorState.ARRIVED
            self._motion_direction = VerticalDirection.STATIONARY

        cur_floor = min(self.max_floor, cur_floor)
        cur_floor = max(self.min_floor, cur_floor)
        self._vertical_position = Blocks(cur_floor)

    def _update_arrived(self, dt: Time) -> None:
        who_wants_off: Final[List[PersonProtocol]] = self.passengers_who_want_off()

        if len(who_wants_off) > 0:
            self._state = ElevatorState.UNLOADING
        else:
            self._state = ElevatorState.IDLE
        self._logger.debug(
            f"{self.elevator_state} Elevator: Having arrived, elevator has {len(who_wants_off)} passengers to disembark -> {self._state}"
        )

    def _update_unloading(self, dt: Time) -> None:
        self._unloading_timeout += dt
        if self._unloading_timeout < self._config.PASSENGER_LOADING_TIME:
            return

        self._unloading_timeout = Time(0.0)
        who_wants_off: Final[List[PersonProtocol]] = self.passengers_who_want_off()

        if len(who_wants_off) > 0:
            self._logger.debug(f"{self.elevator_state} Elevator: Unloading Passenger")
            disembarking_passenger: Final[PersonProtocol] = who_wants_off.pop()

            self._passengers.remove(disembarking_passenger)
            disembarking_passenger.disembark_elevator()

        else:
            self._logger.debug(f"{self.elevator_state} Elevator: Unloading Complete -> LOADING")
            self._state = ElevatorState.LOADING
        return

    def _update_loading(self, dt: Time) -> None:
        self._loading_timeout += dt
        if self._loading_timeout < self._config.PASSENGER_LOADING_TIME:
            return

        self._loading_timeout = Time(0.0)

        # We could have an "Overstuffed" option here in the future
        if self.avail_capacity <= 0:
            self._logger.info(f"{self.elevator_state} Elevator: Loading at Capacity -> READY_TO_MOVE")
            self._state = ElevatorState.READY_TO_MOVE  # We're full, get ready to move
            self.door_open = False
            return

        # There is still room, add a person
        self._logger.debug(
            f"{self.elevator_state} Elevator: Trying to dequeue a passenger going {self.nominal_direction} from {self.current_floor_int}"
        )
        who_wants_on: PersonProtocol | None = self.parent_elevator_bank.try_dequeue_waiting_passenger(
            self.current_floor_int, self.nominal_direction
        )
        if who_wants_on is not None:
            who_wants_on.board_elevator(self)
            self._passengers.append(who_wants_on)
        else:
            self._logger.debug(f"{self.elevator_state} Elevator: Loading Complete: No more willing passengers -> READY_TO_MOVE")
            self._state = ElevatorState.READY_TO_MOVE  # Nobody else wants to get on
            self.door_open = False
        return

    def _update_ready_to_move(self, dt: Time) -> None:
        self._logger.debug(
            f"{self.elevator_state} Elevator: Elevator ready to move from floor {self.current_floor_int} to {self.destination_floor}"
        )
        if self.current_floor_int != self.destination_floor:
            self._logger.info(
                f"{self.elevator_state} Elevator: Elevator starting to MOVE {self.nominal_direction} towards floor {self.destination_floor}"
            )
            self._state = ElevatorState.MOVING
        elif len(self._passengers) == 0:
            self._logger.info(f"{self.elevator_state} Elevator: No Destination -> IDLE")
            self._state = ElevatorState.IDLE
        # Implicit Else, wait here for the bank to provide a new destination

