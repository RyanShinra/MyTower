# game/elevator.py
from __future__ import annotations  # Defer type evaluation
from typing import List, TYPE_CHECKING

import pygame
from game.constants import (
    CELL_WIDTH, CELL_HEIGHT,
    ELEVATOR_SHAFT_COLOR, ELEVATOR_CLOSED_COLOR, ELEVATOR_OPEN_COLOR, UI_TEXT_COLOR
)
from game.types import ElevatorState, Direction
from game.person import Person
from pygame.surface import Surface

if TYPE_CHECKING:
    from game.building import Building

class Elevator:
    """
    An elevator in the building that transports people between floors.
    """
    def __init__(self, building: Building, x_pos: int, min_floor: int, max_floor: int):
        """
        Initialize a new elevator
        
        Args:
            building: The Building object this elevator belongs to
            x_pos: X position in grid cells
            min_floor: Lowest floor this elevator serves
            max_floor: Highest floor this elevator serves
        """
        self.building: Building = building
        self.x_pos: int = x_pos
        self.min_floor: int = min_floor
        self.max_floor: int = max_floor
        
        # Current state
        self.current_floor: float = min_floor  # Floor number (can be fractional when moving)
        self.door_open: bool = False
        self.state: ElevatorState = "IDLE"
        self.direction: Direction = 0  # -1 for down, 0 for stopped, 1 for up
        self.occupants: List[Person] = []  # People inside the elevator
    
    def update(self, dt: float):
        """Update elevator status over time increment dt (in seconds)"""
        pass  # To be implemented
    
    def draw(self, surface: Surface):
        """Draw the elevator on the given surface"""
        # Calculate positions
        screen_height = surface.get_height()
        #   450 = 480 - (1.5 * 20)
        car_top = screen_height - int(self.current_floor * CELL_HEIGHT)
        shaft_left = self.x_pos * CELL_WIDTH
        width = CELL_WIDTH
        
        # Draw shaft from min to max floor
        #     420 = 480 - (3 * 20)
        shaft_top = screen_height - (self.max_floor * CELL_HEIGHT)
        shaft_overhead = screen_height - ((self.max_floor + 1) * CELL_HEIGHT)
        #     480 = 480 - ((1 - 1) * 20)
        shaft_bottom = screen_height - ((self.min_floor - 1) * CELL_HEIGHT)
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
            (shaft_left, car_top, width, CELL_HEIGHT)
        )