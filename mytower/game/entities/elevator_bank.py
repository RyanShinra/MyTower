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
from typing import override

import pygame

from mytower.game.core.id_generator import IDGenerator
from mytower.game.core.types import ElevatorState, VerticalDirection
from mytower.game.core.units import Blocks, Pixels, Time, rect_from_pixels
from mytower.game.entities.entities_protocol import (
    BuildingProtocol, ElevatorBankProtocol, ElevatorBankTestingProtocol,
    ElevatorProtocol, PersonProtocol)
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger

if TYPE_CHECKING:
    from pygame import Surface

    from mytower.game.core.config import ElevatorCosmeticsProtocol


class ElevatorBank(ElevatorBankProtocol, ElevatorBankTestingProtocol):
    """
    An elevator bank managing multiple elevators serving a range of floors.
    """
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

    _id_generator: IDGenerator = IDGenerator("elevator_bank")

    def __init__(
        self,
        logger_provider: LoggerProvider,
        building: BuildingProtocol,  # Changed to protocol
        h_cell: int,
        min_floor: int,
        max_floor: int,
        cosmetics_config: ElevatorCosmeticsProtocol,
    ) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("ElevatorBank")

        self._elevator_bank_id: Final[str] = ElevatorBank._id_generator.get_next_id()

        # Passengers waiting for the elevator on each floor
        self._building: BuildingProtocol = building
        self._horizontal_block: Blocks = Blocks(h_cell)
        self._min_floor: int = min_floor
        self._max_floor: int = max_floor
        self._cosmetics_config: ElevatorCosmeticsProtocol = cosmetics_config
        
        # NOTE: We will need to revisit this validation if we add basement floors
        if self._min_floor < 1:
            raise ValueError(f"min_floor must be >= 1, got {self._min_floor}")
        if self._max_floor < self._min_floor:
            raise ValueError(f"max_floor must be >= min_floor, got {self._max_floor} < {self._min_floor}")
        
        if self.max_floor > self.building.num_floors:
            raise ValueError(
                f"max_floor {self.max_floor} exceeds building's number of floors {self.building.num_floors}"
            )
        
        # Passengers waiting on each floor who want to go UP
        # Key: floor number, Value: queue of people waiting to go upward from that floor
        self._upward_waiting_passengers: dict[int, deque[PersonProtocol]] = {
            floor: deque() for floor in range(self._min_floor, self._max_floor + 1)
        }
        
        # Passengers waiting on each floor who want to go DOWN  
        # Key: floor number, Value: queue of people waiting to go downward from that floor
        self._downward_waiting_passengers: dict[int, deque[PersonProtocol]] = {
            floor: deque() for floor in range(self._min_floor, self._max_floor + 1)
        }
        self._elevators: List[ElevatorProtocol] = []  # Changed to protocol
        self._requests: dict[int, set[VerticalDirection]] = {
            floor: set() for floor in range(self._min_floor, self._max_floor + 1)
        }
        pass

    @property
    @override
    def elevator_bank_id(self) -> str:
        return self._elevator_bank_id

    @property
    def building(self) -> BuildingProtocol:
        return self._building

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
    def horizontal_position(self) -> Blocks:
        return self._horizontal_block

    @property
    @override
    def elevators(self) -> List[ElevatorProtocol]:
        return self._elevators

    @property
    def waiting_passengers(self) -> dict[int, deque[PersonProtocol]]:
        return self._upward_waiting_passengers

    # I'm deprecating this, we should use a better accessor below.

    def get_requests_for_floor(self, floor: int) -> set[VerticalDirection]:
        """Testing method to check what elevator requests exist for a floor"""
        return self._requests[floor].copy()  # Return a copy to prevent modification
    
    def get_requests_for_floors(self, floors: List[int]) -> set[VerticalDirection]:
        return self._requests[floors[0]].copy()  # Return a copy to prevent modification

    @override
    def add_elevator(self, elevator: ElevatorProtocol) -> None:  # Changed to protocol
        if elevator is None:  # pyright: ignore
            raise ValueError("Elevator cannot be None")  # pyright: ignore[reportUnreachable]

        self._elevators.append(elevator)

    def _validate_floor(self, floor: int) -> None:
        """Validate that floor is within the valid range for this elevator bank"""
        if floor < self._min_floor or floor > self._max_floor:
            raise ValueError(f"Floor {floor} out of range {self._min_floor}-{self._max_floor}")


            
    @override
    def request_elevator(self, floor: int, direction: VerticalDirection) -> None:
        self._validate_floor(floor)
        
        if not (direction == VerticalDirection.UP or direction == VerticalDirection.DOWN):
            raise KeyError(f"Passenger cannot request_elevator to go in direction {direction}")
        
        floor_request: set[VerticalDirection] | None = self._requests.get(floor)
        
        if floor_request is None:
            # This indicates a serious internal consistency bug
            raise RuntimeError(f"Internal error: Floor {floor} missing from requests dict. " +\
                            f"This should never happen after validation.")

        floor_request.add(direction)


    @override
    def add_waiting_passenger(self, passenger: PersonProtocol) -> None:
        if passenger is None:  # pyright: ignore
            raise ValueError("PersonProtocol cannot be None") # pyright: ignore[reportUnreachable]

        if passenger.current_floor_num < self.min_floor or passenger.current_floor_num > self.max_floor:
            raise ValueError(
                f"Floor {passenger.current_floor_num} is not within the valid range of floors: {self._min_floor}:{self._max_floor}"
            )

        self._logger.info(
            f"Adding passenger going from floor {passenger.current_floor_num} to floor {passenger.destination_floor_num}"
        )

        current_queue: deque[PersonProtocol] | None = None
        if passenger.current_floor_num == passenger.destination_floor_num:
            raise ValueError(
                f"PersonProtocol cannot go to the same floor: current floor {passenger.current_floor_num} = destination floor {passenger.destination_floor_num}"
            )

        elif passenger.current_floor_num < passenger.destination_floor_num:
            self._logger.info("Adding Passenger to Going UP queue, Requesting UP")
            if passenger.current_floor_num not in self._upward_waiting_passengers:
                raise KeyError(
                    f"Floor {passenger.current_floor_num} is not within the valid range of floors for upward_waiting_passengers, {self._upward_waiting_passengers.keys}"
                )
            self.request_elevator(passenger.current_floor_num, VerticalDirection.UP)
            current_queue = self._upward_waiting_passengers.get(passenger.current_floor_num)
        
        else:
            self._logger.info("Adding Passenger to Going DOWN queue, Requesting DOWN")
            if passenger.current_floor_num not in self._downward_waiting_passengers:
                raise KeyError(
                    f"Floor {passenger.current_floor_num} is not within the valid range of floors for _downward_waiting_passengers, {self._downward_waiting_passengers.keys}"
                )
            self.request_elevator(passenger.current_floor_num, VerticalDirection.DOWN)
            current_queue = self._downward_waiting_passengers.get(passenger.current_floor_num)

        if current_queue is None:
            raise KeyError(f"Why can't we get a current Queue on floor:  {passenger.current_floor_num}")
        # TODO: Do we want a max queue length?
        current_queue.append(passenger)


    @override
    def try_dequeue_waiting_passenger(self, floor: int, direction: VerticalDirection) -> Opt[PersonProtocol]:
        self._logger.debug(f"Attempting to dequeue a waiting passenger on floor {floor} in direction {direction}")
        self._validate_floor(floor)

        if direction == VerticalDirection.STATIONARY:
            self._logger.error(f"Invalid direction 'STATIONARY' for dequeue operation on floor {floor}")
            raise ValueError(f"Trying to get 'STATIONARY' Queue on floor {floor}")

        result: Final[ElevatorBank.DirQueue] = self._get_waiting_passengers(floor, direction)
        current_queue: deque[PersonProtocol] = result[0]

        if len(current_queue) == 0:
            self._logger.info(f"No passengers waiting on floor {floor} in direction {direction}")
            return None

        passenger: Final[PersonProtocol] = current_queue.popleft()
        self._logger.debug(f"Dequeued passenger from floor {floor} heading {direction}")
        return passenger


    # In ElevatorBank class
    @override
    def testing_get_upward_queue(self, floor: int) -> deque[PersonProtocol]:
        """
        Testing method to access the queue of passengers waiting on a specific floor
        who want to travel upward.
        
        Args:
            floor: The floor number (1-based) to get the upward queue for
            
        Returns:
            Queue of people on that floor waiting to go up
        """
        return self._upward_waiting_passengers[floor]

    @override
    def testing_get_downward_queue(self, floor: int) -> deque[PersonProtocol]:
        """
        Testing method to access downward waiting passengers queue
        Args:
            floor: The floor number (1-based) to get the downward queue for
            
        Returns:
            Queue of people on that floor waiting to go up
        """
        return self._downward_waiting_passengers[floor]

    @override
    def testing_update_idle_elevator(self, elevator: ElevatorProtocol, dt: Time) -> None:
        """Testing method to access idle elevator update logic"""
        self._update_idle_elevator(elevator, dt)

    @override
    def testing_update_ready_elevator(self, elevator: ElevatorProtocol) -> None:
        """Testing method to access ready elevator update logic"""
        self._update_ready_elevator(elevator)

    @override
    def testing_collect_destinations(self, elevator: ElevatorProtocol, floor: int, direction: VerticalDirection) -> List[int]:
        return self._collect_destinations(elevator, floor, direction)

    @override
    def testing_select_next_floor(self, destinations: List[int], direction: VerticalDirection) -> int:
        return self._select_next_floor(destinations, direction)

    def _get_waiting_passengers(self, floor: int, nom_direction: VerticalDirection) -> ElevatorBank.DirQueue:
        """Helper method to get passengers waiting on a floor in a specific direction"""
        self._logger.debug(f"Getting waiting passengers on floor {floor} for direction {nom_direction}")
        up_pass: deque[PersonProtocol] = self._upward_waiting_passengers.get(floor, deque())
        down_pass: deque[PersonProtocol] = self._downward_waiting_passengers.get(floor, deque())

        self._logger.debug(f"Upward passengers: {len(up_pass)}, Downward passengers: {len(down_pass)}")
        
        # Disable pylint invalid-name (c0103) - Used as constants only here
        # pylint: disable=c0103
        UP: Final = VerticalDirection.UP
        DOWN: Final = VerticalDirection.DOWN
        STATIONARY: Final = VerticalDirection.STATIONARY
        
        if nom_direction == UP:
            self._logger.debug(f"Returning upward passengers queue for floor {floor}")
            return ElevatorBank.DirQueue(up_pass, UP)

        elif nom_direction == DOWN:
            self._logger.debug(f"Returning downward passengers queue for floor {floor}")
            return ElevatorBank.DirQueue(down_pass, DOWN)

        elif nom_direction == STATIONARY:
            self._logger.debug(f"Checking both directions for stationary elevator on floor {floor}")
            if up_pass:
                self._logger.debug(f"Returning upward passengers queue for floor {floor}")
                return ElevatorBank.DirQueue(up_pass, UP)
            if down_pass:
                self._logger.debug(f"Returning downward passengers queue for floor {floor}")
                return ElevatorBank.DirQueue(down_pass, DOWN)

        self._logger.debug(f"No passengers waiting on floor {floor} in any direction")
        return ElevatorBank.DirQueue(ElevatorBank.EMPTY_DEQUE, STATIONARY)


    @override
    def get_waiting_position(self) -> Blocks:
        """The block where people wait for the elevator, it's just to the left of the elevator bank unless it's at the left edge of the building, then it's just to the right"""
        # TODO: Update this once we add building extents
        return max(Blocks(1), self.horizontal_position - Blocks(1))


    @override
    def update(self, dt:Time) -> None:  # Accept both for now during transition
        """Update elevator status over time increment dt (in seconds)"""
        # Convert to float for internal use
        
        for el in self.elevators:
            # Need to actually update the thing
            # The elevators are all updated separately, now in GameModel
            if el.elevator_state == ElevatorState.IDLE:
                self._update_idle_elevator(el, dt)
            elif el.elevator_state == ElevatorState.READY_TO_MOVE:
                self._update_ready_elevator(el)
        pass


    def _update_idle_elevator(self, elevator: ElevatorProtocol, dt: Time) -> None:
        """Idle means it arrived at this floor with nobody who wanted to disembark on this floor"""
        elevator.idle_time += dt
        # Access idle_wait_timeout from the elevator's public property
        if elevator.idle_time < elevator.idle_wait_timeout:  # Use public property
            return

        elevator.idle_time = Time(0.0)

        # First, let's figure out if there is anybody here who wants to go UP or DOWN
        # This section is if the elevator was just waiting at a floor and somebody pushed the button
        floor: int = elevator.current_floor_int
        nom_direction: Final[VerticalDirection] = elevator.nominal_direction

        result: Final[ElevatorBank.DirQueue] = self._get_waiting_passengers(floor, nom_direction)
        who_wants_to_get_on: deque[PersonProtocol] = result[0]
        new_direction: Final[VerticalDirection] = result[1]

        if who_wants_to_get_on:
            elevator.request_load_passengers(new_direction)
            return

        # OK, nobody wants to get on, let's see if the elevator has a reason to go UP or DOWN
        self._update_ready_elevator(elevator)

        return


    def _update_ready_elevator(self, elevator: ElevatorProtocol) -> None:
        floor: int = elevator.current_floor_int
        nom_direction: Final[VerticalDirection] = elevator.nominal_direction

        self._logger.debug(
            f"Finding next destination for elevator at floor {floor} with nominal direction {nom_direction}"
        )
        next_destination: Final[ElevatorBank.ElevatorDestination] = self._get_next_destination(elevator, floor, nom_direction)
        
        if next_destination.has_destination:
            self._logger.info(
                f"Setting destination to {next_destination.floor} with direction {next_destination.direction}, has_destination={next_destination.has_destination}"
            )
            elevator.set_destination_floor(next_destination.floor)

            # Oh, and we need to clear the request on that floor
            requests_at_destination: set[VerticalDirection] | None = self._requests.get(next_destination.floor)
            
            if requests_at_destination:
                self._logger.debug(f"Clearing {next_destination.direction} request for floor {next_destination.floor}")
                requests_at_destination.discard(next_destination.direction)
        
        else:
            self._logger.debug(f"No new destination - staying at floor {next_destination.floor}")

        return


    def _get_next_destination(
        self, elevator: ElevatorProtocol, current_floor: int, current_direction: VerticalDirection
    ) -> ElevatorBank.ElevatorDestination:
        
        # Normalize STATIONARY direction before doing any searches
        search_direction: VerticalDirection = current_direction
        if search_direction == VerticalDirection.STATIONARY:
            search_direction = VerticalDirection.UP  # Bias to search up when stationary
        
        # Now search in the normalized direction
        destinations: List[int] = self._collect_destinations(elevator, floor=current_floor, direction=search_direction)
        if destinations:
            next_floor: int = self._select_next_floor(destinations, search_direction)
            return ElevatorBank.Destination(True, next_floor, search_direction)

        # No? Shall we turn around?
        opposite_dir: Final[VerticalDirection] = search_direction.invert()
        destinations = self._collect_destinations(elevator, floor=current_floor, direction=opposite_dir)
        if destinations:
            next_floor = self._select_next_floor(destinations, opposite_dir)
            return ElevatorBank.Destination(True, next_floor, opposite_dir)

        # Well, nobody seems to want to go anywhere, let's stay put
        return ElevatorBank.Destination(False, current_floor, VerticalDirection.STATIONARY)


    def _collect_destinations(self, elevator: ElevatorProtocol, floor: int, direction: VerticalDirection) -> List[int]:
        destinations: Final[List[int]] = []

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
        answer: Final[List[int]] = []
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
                # floor_requests: set[VerticalDirection] | None = self.requests.get(floor)
                floor_requests: set[VerticalDirection] | None = self._requests.get(floor)
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
        screen_height: Pixels = Pixels(surface.get_height())

        shaft_left: Pixels = self._horizontal_block.in_pixels
        width: Pixels = self._cosmetics_config.ELEVATOR_WIDTH.in_pixels

        # Draw shaft from min to max floor
        shaft_top: Pixels = screen_height - Blocks(self._max_floor).in_pixels
        shaft_overhead: Pixels = screen_height - Blocks(self._max_floor + 1).in_pixels
        shaft_bottom: Pixels = screen_height - Blocks(self._min_floor - 1).in_pixels
        
        elevator_shaft_rect: tuple[int, int, int, int] = rect_from_pixels(shaft_left, shaft_top, width, shaft_bottom - shaft_top)
        pygame.draw.rect(
            surface,
            self._cosmetics_config.SHAFT_COLOR,
            elevator_shaft_rect
        )

        # Draw overhead part of shaft
        elevator_overhead_rect: tuple[int, int, int, int] = rect_from_pixels(shaft_left, shaft_overhead, width, shaft_top - shaft_overhead)
        pygame.draw.rect(
            surface,
            self._cosmetics_config.SHAFT_OVERHEAD_COLOR,
            elevator_overhead_rect
        )


