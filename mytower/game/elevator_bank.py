# game/elevator_bank.py
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

from collections import deque
from typing import TYPE_CHECKING, Final, List, NamedTuple
from typing import Optional as Opt

import pygame

from mytower.game.constants import BLOCK_HEIGHT, BLOCK_WIDTH
from mytower.game.logger import LoggerProvider, MyTowerLogger
from mytower.game.types import ElevatorState, VerticalDirection

if TYPE_CHECKING:
    from pygame import Surface

    from mytower.game.building import Building
    from mytower.game.elevator import Elevator, ElevatorCosmeticsProtocol
    from mytower.game.person import PersonProtocol


class ElevatorBank:
    # Used in deciding if to move or not
    class ElevatorDestination(NamedTuple):
        has_destination: bool
        floor: int
        direction: VerticalDirection

    # Alias for ElevatorDestination
    Destination = ElevatorDestination

    class DirQueue(NamedTuple):
        queue: deque[PersonProtocol]
        direction: VerticalDirection

    # Define a reusable empty deque as a class-level constant
    EMPTY_DEQUE: Final[deque[PersonProtocol]] = deque()

    def __init__(
        self,
        logger_provider: LoggerProvider,
        building: Building,
        h_cell: int,
        min_floor: int,
        max_floor: int,
        cosmetics_config: ElevatorCosmeticsProtocol,
    ) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("ElevatorBank")

        # Passengers waiting for the elevator on each floor
        self._building: Building = building
        self._horizontal_block: int = h_cell
        self._min_floor: int = min_floor
        self._max_floor: int = max_floor
        self._cosmetics_config: ElevatorCosmeticsProtocol = cosmetics_config
        self._upward_waiting_passengers: dict[int, deque[PersonProtocol]] = {
            floor: deque() for floor in range(self._min_floor, self._max_floor + 1)
        }
        self._downward_waiting_passengers: dict[int, deque[PersonProtocol]] = {
            floor: deque() for floor in range(self._min_floor, self._max_floor + 1)
        }
        self._elevators: List[Elevator] = []
        self._requests: dict[int, set[VerticalDirection]] = {
            floor: set() for floor in range(self._min_floor, self._max_floor + 1)
        }
        pass

    @property
    def building(self) -> Building:
        return self._building

    @property
    def min_floor(self) -> int:
        return self._min_floor

    @property
    def max_floor(self) -> int:
        return self._max_floor

    @property
    def horizontal_block(self) -> int:
        return self._horizontal_block

    @property
    def elevators(self) -> List[Elevator]:
        return self._elevators

    @property
    def waiting_passengers(self) -> dict[int, deque[PersonProtocol]]:
        return self._upward_waiting_passengers

    @property
    def requests(self) -> dict[int, set[VerticalDirection]]:
        return self._requests

    def add_elevator(self, elevator: Elevator) -> None:
        if elevator is None:  # pyright: ignore
            raise ValueError("Elevator cannot be None")

        self._elevators.append(elevator)

    def request_elevator(self, floor: int, direction: VerticalDirection) -> bool:
        floor_request: set[VerticalDirection] | None = self._requests.get(floor)
        if floor_request is None:
            raise KeyError(
                f"Floor {floor} is not within the valid range of floors: {self._min_floor}:{self._max_floor}"
            )

        floor_request.add(direction)
        return True

    # TODO: We may want to pass in the direction here, or target floor as an argument
    def add_waiting_passenger(self, passenger: PersonProtocol) -> bool:
        if passenger is None:  # pyright: ignore
            raise ValueError("PersonProtocol cannot be None")

        if passenger.current_floor < self.min_floor or passenger.current_floor > self.max_floor:
            raise ValueError(
                f"Floor {passenger.current_floor} is not within the valid range of floors: {self._min_floor}:{self._max_floor}"
            )

        self._logger.info(
            f"Adding passenger going from floor {passenger.current_floor} to floor {passenger.destination_floor}"
        )

        current_queue: deque[PersonProtocol] | None = None
        if passenger.current_floor == passenger.destination_floor:
            raise ValueError(
                f"PersonProtocol cannot go to the same floor: current floor {passenger.current_floor} = destination floor {passenger.destination_floor}"
            )

        elif passenger.current_floor < passenger.destination_floor:
            self._logger.info("Adding Passenger to Going UP queue, Requesting UP")
            if passenger.current_floor not in self._upward_waiting_passengers:
                raise KeyError(
                    f"Floor {passenger.current_floor} is not within the valid range of floors for upward_waiting_passengers, {self._upward_waiting_passengers.keys}"
                )
            self.request_elevator(passenger.current_floor, VerticalDirection.DOWN)
            current_queue = self._upward_waiting_passengers.get(passenger.current_floor)
        else:
            self._logger.info("Adding Passenger to Going DOWN queue, Requesting DOWN")
            if passenger.current_floor not in self._downward_waiting_passengers:
                raise KeyError(
                    f"Floor {passenger.current_floor} is not within the valid range of floors for _downward_waiting_passengers, {self._downward_waiting_passengers.keys}"
                )
            self.request_elevator(passenger.current_floor, VerticalDirection.UP)
            current_queue = self._downward_waiting_passengers.get(passenger.current_floor)

        if current_queue is None:
            raise KeyError(f"Why can't we get a current Queue on floor:  {passenger.current_floor}")
        # TODO: Do we want a max queue length?
        current_queue.append(passenger)
        return True

    def try_dequeue_waiting_passenger(self, floor: int, direction: VerticalDirection) -> Opt[PersonProtocol]:
        self._logger.debug(f"Attempting to dequeue a waiting passenger on floor {floor} in direction {direction}")

        if direction == VerticalDirection.STATIONARY:
            self._logger.error(f"Invalid direction 'STATIONARY' for dequeue operation on floor {floor}")
            raise ValueError(f"Trying to get 'STATIONARY' Queue on floor {floor}")

        result: ElevatorBank.DirQueue = self._get_waiting_passengers(floor, direction)
        current_queue: deque[PersonProtocol] = result[0]

        if len(current_queue) == 0:
            self._logger.info(f"No passengers waiting on floor {floor} in direction {direction}")
            return None

        passenger: PersonProtocol = current_queue.popleft()
        self._logger.debug(f"Dequeued passenger from floor {floor} heading {direction}")
        return passenger

    def _get_waiting_passengers(self, floor: int, nom_direction: VerticalDirection) -> ElevatorBank.DirQueue:
        """Helper method to get passengers waiting on a floor in a specific direction"""
        self._logger.debug(f"Getting waiting passengers on floor {floor} for direction {nom_direction}")
        up_pass: deque[PersonProtocol] = self._upward_waiting_passengers.get(floor, deque())
        down_pass: deque[PersonProtocol] = self._downward_waiting_passengers.get(floor, deque())

        self._logger.debug(f"Upward passengers: {len(up_pass)}, Downward passengers: {len(down_pass)}")

        UP = VerticalDirection.UP
        DOWN = VerticalDirection.DOWN

        if nom_direction == UP:
            self._logger.debug(f"Returning upward passengers queue for floor {floor}")
            return ElevatorBank.DirQueue(up_pass, UP)

        elif nom_direction == VerticalDirection.DOWN:
            self._logger.debug(f"Returning downward passengers queue for floor {floor}")
            return ElevatorBank.DirQueue(down_pass, DOWN)

        elif nom_direction == VerticalDirection.STATIONARY:
            self._logger.debug(f"Checking both directions for stationary elevator on floor {floor}")
            if up_pass:
                self._logger.debug(f"Returning upward passengers queue for floor {floor}")
                return ElevatorBank.DirQueue(up_pass, UP)
            if down_pass:
                self._logger.debug(f"Returning downward passengers queue for floor {floor}")
                return ElevatorBank.DirQueue(down_pass, DOWN)

        self._logger.debug(f"No passengers waiting on floor {floor} in any direction")
        return ElevatorBank.DirQueue(ElevatorBank.EMPTY_DEQUE, VerticalDirection.STATIONARY)

    def get_waiting_block(self) -> int:
        # TODO: Update this once we add building extents
        return max(1, self.horizontal_block - 1)

    def update(self, dt: float) -> None:
        """Update elevator status over time increment dt (in seconds)"""
        for el in self.elevators:
            # Need to actually update the thing
            el.update(dt)
            if el.state == ElevatorState.IDLE:
                self._update_idle_elevator(el, dt)
            elif el.state == ElevatorState.READY_TO_MOVE:
                self._update_ready_elevator(el)
        pass

    def _update_idle_elevator(self, elevator: Elevator, dt: float) -> None:
        """Idle means it arrived at this floor with nobody who wanted to disembark on this floor"""
        elevator.idle_time += dt
        # Access idle_wait_timeout from the elevator's public property
        if elevator.idle_time < elevator.idle_wait_timeout:  # Use public property
            return

        elevator.idle_time = 0.0

        # First, let's figure out if there is anybody here who wants to go UP or DOWN
        # This section is if the elevator was just waiting at a floor and somebody pushed the button
        floor: int = elevator.current_floor_int
        nom_direction: VerticalDirection = elevator.nominal_direction

        result: ElevatorBank.DirQueue = self._get_waiting_passengers(floor, nom_direction)
        who_wants_to_get_on: deque[PersonProtocol] = result[0]
        new_direction: VerticalDirection = result[1]

        if who_wants_to_get_on:
            elevator.request_load_passengers(new_direction)
            return

        # OK, nobody wants to get on, let's see if the elevator has a reason to go UP or DOWN
        self._update_ready_elevator(elevator)

        return

    def _update_ready_elevator(self, elevator: Elevator) -> None:
        floor: int = elevator.current_floor_int
        nom_direction: VerticalDirection = elevator.nominal_direction

        self._logger.debug(
            f"Finding next destination for elevator at floor {floor} with nominal direction {nom_direction}"
        )
        where_to: ElevatorBank.ElevatorDestination = self._get_next_destination(elevator, floor, nom_direction)

        self._logger.info(
            f"Setting destination to {where_to.floor} with direction {where_to.direction}, has_destination={where_to.has_destination}"
        )
        elevator.set_destination_floor(where_to.floor)

        # Oh, and we need to clear the request on that floor
        if where_to.has_destination:
            dest_requests: set[VerticalDirection] | None = self._requests.get(where_to.floor)
            if dest_requests:
                self._logger.debug(f"Clearing {where_to.direction} request for floor {where_to.floor}")
                dest_requests.discard(where_to.direction)
        else:
            self._logger.debug(f"No new destination - staying at floor {where_to.floor}")

        return

    # Returns true if we're going to move
    def _get_next_destination(
        self, elevator: Elevator, current_floor: int, current_direction: VerticalDirection
    ) -> ElevatorBank.ElevatorDestination:
        UP = VerticalDirection.UP
        STATIONARY = VerticalDirection.STATIONARY

        # Shall we keep going this way?
        destinations: List[int] = self._collect_destinations(elevator, floor=current_floor, direction=current_direction)
        if destinations:
            next_floor: int = self._select_next_floor(destinations, current_direction)
            return ElevatorBank.Destination(True, next_floor, current_direction)

        # No? Shall we turn around?
        opposite_dir: VerticalDirection = current_direction.invert()
        if opposite_dir == STATIONARY:
            # Bias to search up
            opposite_dir = UP

        destinations = self._collect_destinations(elevator, floor=current_floor, direction=opposite_dir)
        if destinations:
            next_floor = self._select_next_floor(destinations, opposite_dir)
            return ElevatorBank.Destination(True, next_floor, opposite_dir)

        # Well, nobody seems to want to go anywhere, let's stay put
        return ElevatorBank.Destination(False, current_floor, STATIONARY)

    def _collect_destinations(self, elevator: Elevator, floor: int, direction: VerticalDirection) -> List[int]:
        destinations: List[int] = []

        # Passengers have higher priority
        destinations.extend(elevator.get_passenger_destinations_in_direction(floor, direction))

        # Call requests come second
        destinations.extend(self._get_floor_requests_in_dir_from_floor(floor, direction, direction))

        return destinations

    def _select_next_floor(self, destinations: List[int], direction: VerticalDirection) -> int:
        if direction == VerticalDirection.UP:
            # Go to the lowest floor above us
            return min(destinations)
        else:
            # Going down or stationary (what??) go to the highest floor below us
            return max(destinations)

    def _get_floor_requests_in_dir_from_floor(
        self, start_floor: int, search_direction: VerticalDirection, req_direction: VerticalDirection
    ) -> List[int]:
        """The requests are where the 'call buttons' are pressed - this may need updating for programmable elevators"""
        self._logger.debug(f"Getting floor requests from floor {start_floor} in direction {search_direction}")
        answer: List[int] = []
        search_range: Opt[range] = None

        if search_direction == VerticalDirection.UP:
            search_range = range(start_floor + 1, self.max_floor + 1)
        elif search_direction == VerticalDirection.DOWN:
            search_range = range(start_floor - 1, self._min_floor - 1, -1)
        else:
            self._logger.warning(f"Cannot get floor requests for STATIONARY direction from floor {start_floor}")
            return answer

        if search_range:
            for floor in search_range:
                floor_requests: set[VerticalDirection] | None = self.requests.get(floor)
                self._logger.trace(f"Checking floor {floor}: Requests = {floor_requests}")
                if floor_requests is not None and req_direction in floor_requests:
                    self._logger.debug(f"Adding floor {floor} to answer list")
                    answer.append(floor)

        self._logger.debug(
            f"Final list of floor requests in Search direction {search_direction} from floor {start_floor} going {req_direction}: {answer}"
        )
        return answer

    def draw(self, surface: Surface) -> None:
        """Draw the elevator Bank on the given surface"""
        # self._logger.debug("I'm drawing an Elevator Bank")
        screen_height: int = surface.get_height()

        shaft_left: int = self._horizontal_block * BLOCK_WIDTH
        width: int = BLOCK_WIDTH

        # Draw shaft from min to max floor
        #     420 = 480 - (3 * 20)
        shaft_top: int = screen_height - (self._max_floor * BLOCK_HEIGHT)
        shaft_overhead: int = screen_height - ((self._max_floor + 1) * BLOCK_HEIGHT)
        #     480 = 480 - ((1 - 1) * 20)
        shaft_bottom = screen_height - ((self._min_floor - 1) * BLOCK_HEIGHT)
        pygame.draw.rect(
            surface, self._cosmetics_config.shaft_color, (shaft_left, shaft_top, width, shaft_bottom - shaft_top)
        )

        pygame.draw.rect(
            surface,
            self._cosmetics_config.shaft_overhead,
            (shaft_left, shaft_overhead, width, shaft_top - shaft_overhead),
        )

        # now draw the elevators
        for el in self.elevators:
            # self._logger.debug("I want to draw an elevator")
            el.draw(surface)
