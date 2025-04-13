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
from typing import Final, List, TYPE_CHECKING, Optional as Opt

import pygame
from game.constants import (
    BLOCK_WIDTH, BLOCK_HEIGHT,
    ELEVATOR_SHAFT_COLOR, UI_TEXT_COLOR
)
from game.types import VerticalDirection
from collections import deque

if TYPE_CHECKING:
    from pygame import Surface
    from game.building import Building
    from game.person import Person
    from game.elevator import Elevator

class ElevatorBank:
    
    def __init__(self, building: Building, h_cell: int, min_floor: int, max_floor: int) -> None:
         # Passengers waiting for the elevator on each floor
        self.__building: Building = building
        self.__horizontal_block: int = h_cell
        self.__min_floor: int = min_floor
        self.__max_floor: int = max_floor
        self.__upward_waiting_passengers: dict[int, deque[Person]] = {floor: deque() for floor in range(self.__min_floor, self.__max_floor + 1)}
        self.__downward_waiting_passengers: dict[int, deque[Person]] = {floor: deque() for floor in range(self.__min_floor, self.__max_floor + 1)}
        self.__elevators: List[Elevator] = []
        self.__requests: dict[int, set[VerticalDirection]] = {floor: set() for floor in range(self.__min_floor, self.__max_floor + 1)}
        pass
    
    @property
    def building(self) -> Building:
        return self.__building
    
    @property
    def min_floor(self) -> int:
        return self.__min_floor

    @property
    def max_floor(self) -> int:
        return self.__max_floor
    
    @property
    def horizontal_block(self) -> int:
        return self.__horizontal_block

    @property
    def elevators(self) -> List[Elevator]:
        return self.__elevators

    @property
    def waiting_passengers(self) -> dict[int, deque[Person]]:
        return self.__upward_waiting_passengers

    @property
    def requests(self) -> dict[int, set[VerticalDirection]]:
        return self.__requests
    
    def add_elevator(self, elevator: Elevator) -> None:
        if elevator is None: # pyright: ignore
            raise ValueError("Elevator cannot be None") 
        
        self.__elevators.append(elevator)

        
    def request_elevator(self, floor: int, direction: VerticalDirection) -> bool:
        floor_request: set[VerticalDirection] | None = self.__requests.get(floor)
        if floor_request is None:
            raise KeyError(f"Floor {floor} is not within the valid range of floors: {self.__min_floor}:{self.__max_floor}")           
        
        floor_request.add(direction)
        return True
    
    
    def add_waiting_passenger(self, passenger: Person) -> bool:
        if passenger is None: # pyright: ignore
            raise ValueError('Person cannot be None')
        
        current_queue: deque[Person] | None = None
        if passenger.current_floor == passenger.destination_floor:
            raise ValueError(f"Person cannot go to the same floor: current floor {passenger.current_floor} = destination floor {passenger.destination_floor}")
        
        elif passenger.current_floor < passenger.destination_floor:
            current_queue = self.__upward_waiting_passengers.get(passenger.current_floor)
        else:
            current_queue = self.__downward_waiting_passengers.get(passenger.current_floor)
        
        if current_queue is None:
            raise KeyError(f"Floor {passenger.current_floor} is not within the valid range of floors: {self.__min_floor}:{self.__max_floor}")  
        
        #TODO: Do we want a max queue length?
        current_queue.append(passenger)
        return True 
    
    
    def dequeue_waiting_passenger(self, floor: int, direction: VerticalDirection) -> Person | None: 
        if direction == VerticalDirection.STATIONARY:
            raise ValueError(f"Trying to get 'STATIONARY' Queue on floor {floor}")
        
        current_queue: deque[Person] | None = self._get_waiting_passengers(floor, direction)
        
        if current_queue is None:
            raise KeyError(f"Floor {floor} is not within the valid range of floors: {self.__min_floor}:{self.__max_floor}")  
        
        if len(current_queue) == 0:
            return None
        
        return current_queue.popleft()
        

    def get_waiting_block(self) -> int:
        # TODO: Update this once we add building extents
        return max(1, self.horizontal_block - 1)
    
    def update(self, dt: float) -> None:
        """Update elevator status over time increment dt (in seconds)"""
        for el in self.elevators:
            if el.state == 'IDLE':
                self._update_idle_elevator(el)
        pass
    
    def _update_idle_elevator(self, elevator: Elevator) -> None:
        """Idle generally means it's ready to move"""
        # First, let's figure out if there is anybody here who wants to go "UP" or "DOWN"
        # This section is if the elevator was just waiting at a floor and somebody pushed the button
        floor: int = elevator.current_floor
        direction: VerticalDirection = elevator.nominal_direction
        who_wants_to_get_on = self._get_waiting_passengers(floor, direction)
            
        if who_wants_to_get_on:
            elevator.request_load_passengers()
            return
        
        # OK, nobody wants to get on, let's see if the elevator has a reason to go "UP"
        dest_floor = floor
        dest_direction = direction
        dest_floor = self._get_destination_floor(elevator, floor, dest_direction)
        if dest_floor == floor:
            dest_direction = VerticalDirection.UP if direction == VerticalDirection.DOWN else VerticalDirection.UP
            dest_floor = self._get_destination_floor(elevator, floor, dest_direction)
            
        # OK, now either dest_floor is this one, or above or below - go there now
        elevator.set_destination_floor(dest_floor)
        
        # Oh, and we need to clear the request on that floor
        dest_requests = self.__requests.get(dest_floor)
        if not dest_requests:
            raise KeyError(f"Destination floor (to clear request) {dest_floor} does not exist in the valid range of floors: {self.__min_floor}:{self.__max_floor}")
        dest_requests.discard(dest_direction)
        
        return
            
    def _get_destination_floor(self, elevator: Elevator, floor: int, direction: VerticalDirection) -> int:
        dest_floor: int = floor
        isUp: Final[bool] = direction == VerticalDirection.UP
        isDown: Final[bool] = direction == VerticalDirection.DOWN
        
        elevator_call_destinations: List[int] = self._get_floor_requests_in_dir_from_floor(floor, direction)
        passenger_requests: List[int] = elevator.get_passenger_destinations_in_direction(floor, direction)
        
        if elevator_call_destinations and passenger_requests:
            if isUp:
                dest_floor = min(passenger_requests[0], elevator_call_destinations[0])
            elif isDown:
                dest_floor = max(passenger_requests[0], elevator_call_destinations[0])
        elif elevator_call_destinations: # no passenger requests, just answering a call
            dest_floor = elevator_call_destinations[0]
        elif passenger_requests:
            dest_floor = passenger_requests[0]
        # else there's no requests, so stay here
        return dest_floor
    
    
    
    def _get_waiting_passengers(self, floor: int, direction: VerticalDirection) -> Opt[deque[Person]]:
        """Helper method to get passengers waiting on a floor in a specific direction"""
        if direction == VerticalDirection.UP:
            up_pass: dict[int, deque[Person]] = self.__upward_waiting_passengers
            return up_pass.get(floor) if up_pass.get(floor) else None
        
        elif direction == VerticalDirection.DOWN:
            down_pass: dict[int, deque[Person]] = self.__downward_waiting_passengers
            return down_pass.get(floor) if down_pass.get(floor) else None
        
        return None
    
    def _get_floor_requests_in_dir_from_floor(self, start_floor: int, direction: VerticalDirection) -> List[int]:
        """The requests are where the 'call buttons' are pressed - this may need updating for programmable elevators"""
        answer: List[int] = []
        search_range: Opt[range] = None
        
        if direction == VerticalDirection.UP:
            search_range = range(start_floor + 1, self.max_floor + 1)
            
        elif direction == VerticalDirection.DOWN:
            search_range = range(start_floor - 1, self.min_floor - 1, -1)
        else:
            raise ValueError(f"Cannot get floor requests for STATIONARY direction from floor {start_floor}")
    
        for floor in search_range:
            floor_requests = self.requests.get(floor)
            if floor_requests is not None and direction in floor_requests:
                answer.append(floor)

    
        return answer
    
    
    def draw(self, surface: Surface) -> None:
        """Draw the elevator on the given surface"""
        screen_height: int = surface.get_height()
        
        shaft_left = self.__horizontal_block * BLOCK_WIDTH
        width = BLOCK_WIDTH
        
        # Draw shaft from min to max floor
        #     420 = 480 - (3 * 20)
        shaft_top = screen_height - (self.__max_floor * BLOCK_HEIGHT)
        shaft_overhead = screen_height - ((self.__max_floor + 1) * BLOCK_HEIGHT)
        #     480 = 480 - ((1 - 1) * 20)
        shaft_bottom = screen_height - ((self.__min_floor - 1) * BLOCK_HEIGHT)
        pygame.draw.rect(
            surface,
            ELEVATOR_SHAFT_COLOR,
            (shaft_left, shaft_top, width, shaft_bottom - shaft_top)
        )
        
        pygame.draw.rect(
            surface,
            UI_TEXT_COLOR,
            (shaft_left, shaft_overhead, width, shaft_top - shaft_overhead)
        )
        pass