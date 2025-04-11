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
from typing import List, TYPE_CHECKING

import pygame
from game.constants import (
    BLOCK_WIDTH, BLOCK_HEIGHT,
    ELEVATOR_CLOSED_COLOR, ELEVATOR_OPEN_COLOR
)
from game.types import ElevatorState, VerticalDirection
from pygame import Surface

if TYPE_CHECKING:
    from game.building import Building
    from game.person import Person

class Elevator:
    """
    An elevator in the building that transports people between floors.
    """
    def __init__(self, building: Building, h_cell: int, min_floor: int, max_floor: int, max_velocity: float, max_capacity: int) -> None:
        """
        Initialize a new elevator
        
        Args:
            building: The Building object this elevator belongs to
            x_pos: X position in grid cells
            min_floor: Lowest floor this elevator serves
            max_floor: Highest floor this elevator serves
            max_velocity: Speed in floors per second
        """
        self.building: Building = building
        self.horizontal_block: int = h_cell
        self.min_floor: int = min_floor
        self.max_floor: int = max_floor
        self.max_veloxity: float = max_velocity
        self.__max_capacity: int = max_capacity
        
        # Current state
        self._current_floor_pos: float = min_floor  # Floor number (can be fractional when moving)
        self.destination_floor: int = min_floor # Let's not stop between floors
        self.door_open: bool = False
        self._state: ElevatorState = "IDLE"
        self._direction: VerticalDirection = VerticalDirection.STATIONARY  # -1 for down, 0 for stopped, 1 for up
        self.passengers: List[Person] = []  # People inside the elevator
       
    
    def set_destination_floor(self, dest_floor: int) -> None:
        if (dest_floor > self.max_floor) or (dest_floor < self.min_floor):
            raise ValueError(f"Destination floor {dest_floor} is out of bounds. Valid range: {self.min_floor} to {self.max_floor}.")
        
        if self.current_floor < dest_floor:
            self._direction = VerticalDirection.UP
        elif self.current_floor > dest_floor:
            self._direction = VerticalDirection.DOWN
        else:
            self._direction = VerticalDirection.STATIONARY
            
        self.destination_floor = dest_floor
        
    def get_waiting_block(self) -> int:
        # TODO: Update this once we add building extents
        return max(1, self.horizontal_block - 1)
    
    @property
    def state(self) -> ElevatorState:
        return self._state
    
    @property
    def avail_capacity(self) -> int:
        return self.__max_capacity - len(self.passengers)
    
    @property
    def direction(self) -> VerticalDirection:
        return self._direction
        
    @property
    def current_floor(self) -> int:
        return int(self._current_floor_pos)
    
    def update(self, dt: float) -> None:
        """Update elevator status over time increment dt (in seconds)"""
        match self._state:
            case "IDLE":
                self._direction = VerticalDirection.STATIONARY
            
            case "MOVING":
                # Continue moving towards the destination floor
                self.door_open = False
                self.update_moving(dt)
            
            case "ARRIVED":
                pass
            
            case "UNLOADING":
                # Allow people to exit the elevator
                self.door_open = True
                # TODO: Write update_unloading(self)
                # Transition to LOADING after unloading is complete
                self._state = "LOADING"
            
            case "LOADING":
                # Allow people to enter or exit the elevator
                self.door_open = True
                # Transition to IDLE after loading is complete
                self._state = "IDLE"

            case _:
                raise ValueError(f"Unknown elevator state: {self._state}")
        
        
    def update_moving(self, dt: float) -> None:
        cur_floor: float = self.current_floor + dt * self.max_veloxity * self.direction.value
              
        done: bool = False
        
        if self.direction == VerticalDirection.UP:
            if cur_floor >= self.destination_floor:
                done = True
        elif self.direction == VerticalDirection.DOWN:
            if cur_floor <= self.destination_floor:
                done = True
                
        if done:
            # self._direction = VerticalDirection.STATIONARY 
            cur_floor = self.destination_floor
            self._state = "ARRIVED"
        
        cur_floor = min(self.max_floor, cur_floor)
        cur_floor = max(self.min_floor, cur_floor)
        self._current_floor_pos = cur_floor
        
    def update_arrived(self, dt: float) -> None:
        somebody_wants_off = False
        for p in self.passengers:
            if p.destination_floor == self.current_floor:
                somebody_wants_off = True
        
        if somebody_wants_off:
            self._state = "UNLOADING"
        else:
            self._state = "IDLE"
    
    def draw(self, surface: Surface) -> None:
        """Draw the elevator on the given surface"""
        # Calculate positions
        screen_height = surface.get_height()
        #   450 = 480 - (1.5 * 20) 
        # We want the private member here since it's a float and we're computing pixels
        car_top = screen_height - int(self._current_floor_pos * BLOCK_HEIGHT)
        shaft_left = self.horizontal_block * BLOCK_WIDTH
        width = BLOCK_WIDTH
        
        # Draw shaft from min to max floor
        #     420 = 480 - (3 * 20)
        # shaft_top = screen_height - (self.max_floor * BLOCK_HEIGHT)
        # shaft_overhead = screen_height - ((self.max_floor + 1) * BLOCK_HEIGHT)
        #     480 = 480 - ((1 - 1) * 20)
        # shaft_bottom = screen_height - ((self.min_floor - 1) * BLOCK_HEIGHT)
        # pygame.draw.rect(
        #     surface,
        #     ELEVATOR_SHAFT_COLOR,
        #     (shaft_left, shaft_top, width, shaft_bottom - shaft_top)
        # )
        
        # pygame.draw.rect(
        #     surface,
        #     UI_TEXT_COLOR,
        #     (shaft_left, shaft_overhead, width, shaft_top - shaft_overhead)
        # )
        
        # Draw elevator car
        color = ELEVATOR_OPEN_COLOR if self.door_open else ELEVATOR_CLOSED_COLOR
        pygame.draw.rect(
            surface,
            color,
            (shaft_left, car_top, width, BLOCK_HEIGHT)
        )