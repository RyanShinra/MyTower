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

# pylint: disable=unused-import, import-error
# type: ignore[import]

from __future__ import annotations  # Defer type evaluation
from csv import Error
from operator import truediv
from typing import Final, List, TYPE_CHECKING

import pygame
from game.constants import (
    BLOCK_WIDTH, BLOCK_HEIGHT,
    ELEVATOR_SHAFT_COLOR, ELEVATOR_CLOSED_COLOR, ELEVATOR_OPEN_COLOR, UI_TEXT_COLOR
)
from game.types import ElevatorState, VerticalDirection
from pygame import Surface

if TYPE_CHECKING:
    from game.building import Building
    from game.person import Person
    from game.elevator import Elevator

class ElevatorBank:
    
    def __init__(self, building: Building, h_cell: int, min_floor: int, max_floor: int, elevators: List[Elevator]) -> None:
         # Passengers waiting for the elevator on each floor
        self.__building: Building = building
        self.__horizontal_block: int = h_cell
        self.__min_floor: int = min_floor
        self.__max_floor: int = max_floor
        self.__waiting_passengers: dict[int, List[Person]] = {floor: [] for floor in range(self.__min_floor, self.__max_floor + 1)}
        self.__elevators: List[Elevator] = elevators.copy()
        self.__requests: dict[int, set[VerticalDirection]] = {floor: set() for floor in range(self.__min_floor, self.__max_floor + 1)}
        pass
    
    def add_elevator(self, elevator: Elevator) -> None:
        if elevator is None: 
            raise ValueError("Elevator cannot be None") 
        
        self.__elevators.append(elevator)
        
    def request_elevator(self, floor: int, direction: VerticalDirection) -> bool:
        if floor not in self.__requests.keys():
            raise KeyError(f"Floor {floor} is not within the valid range of floors: {self.__min_floor}:{self.__max_floor}")           
        
        self.__requests.get(floor).add(direction)
        return True
    
    def add_waiting_passenger(self, passenger: Person) -> bool:
        if passenger is None:
            raise ValueError('Person cannot be None')
        
        if passenger.current_floor not in self.__waiting_passengers.keys():
            raise KeyError(f"Floor {passenger.current_floor} is not within the valid range of floors: {self.__min_floor}:{self.__max_floor}")  
        
        self.__waiting_passengers.get(passenger.current_floor).append(passenger)
    
    
    def update(self, dt: float) -> None:
        """Update elevator status over time increment dt (in seconds)"""
        pass
    
    def draw(self, surface: Surface) -> None:
        """Draw the elevator on the given surface"""
        pass