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
    ELEVATOR_SHAFT_COLOR, ELEVATOR_CLOSED_COLOR, ELEVATOR_OPEN_COLOR, UI_TEXT_COLOR
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
    def __init__(self, building: Building, h_cell: int, min_floor: int, max_floor: int, max_velocity: float) -> None:
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
        
        # Current state
        self.current_floor: float = min_floor  # Floor number (can be fractional when moving)
        self.destination_floor: int = min_floor # Let's not stop between floors
        self.door_open: bool = False
        self.state: ElevatorState = "IDLE"
        self.direction: VerticalDirection = VerticalDirection.STATIONARY  # -1 for down, 0 for stopped, 1 for up
        self.occupants: List[Person] = []  # People inside the elevator
       
    
    def set_destination_floor(self, dest_floor: int) -> None:
        if (dest_floor > self.max_floor) or (dest_floor < self.min_floor):
            raise ValueError(f"Destination floor {dest_floor} is out of bounds. Valid range: {self.min_floor} to {self.max_floor}.")
        
        if self.current_floor < dest_floor:
            self.direction = VerticalDirection.UP
        elif self.current_floor > dest_floor:
            self.direction = VerticalDirection.DOWN
        else:
            self.direction = VerticalDirection.STATIONARY
            
        self.destination_floor = dest_floor
        
    def get_waiting_block(self) -> int:
        # TODO: Update this once we add building extents
        return max(1, self.horizontal_block - 1)
    
    def update(self, dt: float) -> None:
        """Update elevator status over time increment dt (in seconds)"""
        cur_floor: float = self.current_floor + dt * self.max_veloxity * self.direction.value
              
        done: bool = False
        
        if self.direction == VerticalDirection.UP:
            if cur_floor >= self.destination_floor:
                done = True
        elif self.direction == VerticalDirection.DOWN:
            if cur_floor <= self.destination_floor:
                done = True
                
        if done:
            self.direction = VerticalDirection.STATIONARY 
            cur_floor = self.destination_floor
        
        cur_floor = min(self.max_floor, cur_floor)
        cur_floor = max(self.min_floor, cur_floor)
        self.current_floor = cur_floor
        
    
    def draw(self, surface: Surface) -> None:
        """Draw the elevator on the given surface"""
        # Calculate positions
        screen_height = surface.get_height()
        #   450 = 480 - (1.5 * 20)
        car_top = screen_height - int(self.current_floor * BLOCK_HEIGHT)
        shaft_left = self.horizontal_block * BLOCK_WIDTH
        width = BLOCK_WIDTH
        
        # Draw shaft from min to max floor
        #     420 = 480 - (3 * 20)
        shaft_top = screen_height - (self.max_floor * BLOCK_HEIGHT)
        shaft_overhead = screen_height - ((self.max_floor + 1) * BLOCK_HEIGHT)
        #     480 = 480 - ((1 - 1) * 20)
        shaft_bottom = screen_height - ((self.min_floor - 1) * BLOCK_HEIGHT)
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
        
        # Draw elevator car
        color = ELEVATOR_OPEN_COLOR if self.door_open else ELEVATOR_CLOSED_COLOR
        pygame.draw.rect(
            surface,
            color,
            (shaft_left, car_top, width, BLOCK_HEIGHT)
        )