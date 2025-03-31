# game/person.py
from __future__ import annotations  # Defer type evaluation
from typing import TYPE_CHECKING, Final, List

import random
import pygame
from pygame import Surface
from game.constants import BLOCK_WIDTH, BLOCK_HEIGHT
from game.types import HorizontalDirection, PersonState
from mytower.game.elevator import Elevator


if TYPE_CHECKING:
    from game.building import Building
    from mytower.game.elevator import Elevator

class Person:
    """
    A person in the building who moves between floors and has needs.
    """
    def __init__(self, building: Building, current_floor: int, current_block: float, max_velocity: float) -> None:
        self.building: Building = building
        self._current_floor: int = current_floor
        self.current_block: float = current_block
        self._dest_block: int = int(current_block)
        self._dest_floor: int = current_floor
        self.state: PersonState = "IDLE"  # IDLE, WALKING, WAITING_FOR_ELEVATOR, IN_ELEVATOR
        self.direction: HorizontalDirection = 1
        self.max_velocity: float = max_velocity
        self._next_elevator: Elevator | None = None
                
        # Appearance (for visualization)
        self.color = (
            random.randint(0, 128),
            random.randint(0, 128),
            random.randint(0, 128)
        )
        
    @property
    def current_floor(self) -> int:
        return self._current_floor
                
    def set_destination(self, dest_floor: int, dest_block: int) -> None:
        dest_floor = min(dest_floor, self.building.num_floors)
        dest_floor = max(dest_floor, 0)
        self._dest_floor = dest_floor
        
        dest_block = min(dest_block, self.building.floor_width)
        dest_block = max(dest_block, 0)
        self._dest_block = dest_block
        
    def find_nearest_elevator(self) -> None | Elevator:
        elevator_list: List[Elevator] = self.building.get_elevator_banks_on_floor(self.current_floor)
        closest_el = None
        closest_dist = self.building.floor_width + 5
        
        for elevator in elevator_list :
            dist = abs(elevator.horizontal_block - self.current_block)
            if (dist < closest_dist) :
                closest_dist = dist
                closest_el = elevator
                
        return closest_el

        
    def update(self, dt: float) -> None:
        """Update person's state and position"""
        match self.state:
            case "IDLE":
                self.update_idle()

            case "WALKING":
                self.update_walking(dt)
                pass
            case "WAITING_FOR_ELEVATOR":
                # Handle waiting for elevator
                pass
            case "IN_ELEVATOR":
                # Handle in elevator state
                pass
            case _:
                # Handle unexpected states
                print(f"Unknown state: {self.state}")
             
    def update_idle(self) -> None:
        LEFT: Final[int] = -1 
        RIGHT: Final[int] = 1
        self.direction = 0
        
        if self._dest_floor > self.current_floor or self._dest_floor < self.current_floor:
            '''TODO: Find the nearest elevator, go in that direction'''
            self._next_elevator = self.find_nearest_elevator()
            if self._next_elevator:
                # TODO: Bounds wrap this to block 1 (i.e. have them board on the right)
                
                self.state = "WALKING"
            else:
                self.state = "IDLE"
                # TODO: Set a timer so that we don't run this constantly (like every 5 seconds)
        
        elif self._dest_block < self.current_block:
            # Already on the right floor (or walking to elevator?)
            self.state = "WALKING"
            self.direction = LEFT    
        
        elif self._dest_block > self.current_block:
            self.state = "WALKING"
            self.direction = RIGHT

    def update_walking(self, dt: float) -> None:
         # pylint disable=C103
        LEFT: Final[int] = -1
        RIGHT: Final[int] = 1 # pylint disable=invalid-name
        done: bool = False
        if self._next_elevator:
            # TODO: Probably need a next_block_this_floor or some such for all these walking directions
            pass
        else:
            next_block: float = self.current_block + dt * self.max_velocity * self.direction
            # Alredy on the right floor
            if self.direction == RIGHT:
                if next_block >= self._dest_block:
                    done = True
            elif self.direction == LEFT:
                if next_block <= self._dest_block:
                    done = True
            
            if done:
                self.direction = 0
                next_block = self._dest_block
                self.state = "IDLE"    
                
            next_block = min(next_block, self.building.floor_width)
            next_block = max(next_block, 0)
            self.current_block = next_block    

    
    def draw(self, surface: Surface) -> None:
        """Draw the person on the given surface"""
        # Calculate position and draw a simple circle for now
        screen_height = surface.get_height()
        y_pos = screen_height - ((self.current_floor - 1) * BLOCK_HEIGHT) - (BLOCK_HEIGHT / 2)
        x_pos = self.current_block * BLOCK_WIDTH + BLOCK_WIDTH / 2
        
        # Print coordinates for debugging
        
        
        pygame.draw.circle(
            surface,
            self.color,
            (int(x_pos), int(y_pos)),
            5  # radius
        )