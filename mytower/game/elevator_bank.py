# game/elevator_pank.py
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
from typing import List, TYPE_CHECKING

import pygame
from game.constants import (
    BLOCK_WIDTH, BLOCK_HEIGHT,
    ELEVATOR_SHAFT_COLOR, UI_TEXT_COLOR
)
from game.types import ElevatorState, VerticalDirection  # pyright: ignore
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
        self.__waiting_passengers: dict[int, deque[Person]] = {floor: deque() for floor in range(self.__min_floor, self.__max_floor + 1)}
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
        return self.__waiting_passengers

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
        
        current_queue: deque[Person] | None = self.__waiting_passengers.get(passenger.current_floor)
        if current_queue is None:
            raise KeyError(f"Floor {passenger.current_floor} is not within the valid range of floors: {self.__min_floor}:{self.__max_floor}")  
        
        #TODO: Do we want a max queue length?
        current_queue.append(passenger)
        return True 
    
    def dequeue_waiting_passenger(self, floor: int) -> Person | None: 
        current_queue: deque[Person] | None = self.__waiting_passengers.get(floor)
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
        pass
    
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