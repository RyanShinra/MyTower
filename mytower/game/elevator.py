# game/elevator.py
from typing import List
import pygame
from game.constants import (
    CELL_WIDTH, CELL_HEIGHT,
    ELEVATOR_SHAFT_COLOR, ELEVATOR_CLOSED_COLOR, ELEVATOR_OPEN_COLOR
)
from game.types import Color, ElevatorState, Direction
from game.building import Building
from game.person import Person
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
        self.min_floo: int = min_floor
        self.max_floor: int = max_floor
        
        # Current state
        self.current_floor: int = min_floor  # Floor number (can be fractional when moving)
        self.door_open: bool = False
        self.state: ElevatorState = "IDLE"
        self.direction: Direction = 0  # -1 for down, 0 for stopped, 1 for up
        self.occupants: List[Person] = []  # People inside the elevator
    
    def update(self, dt):
        """Update elevator status over time increment dt (in seconds)"""
        pass  # To be implemented
    
    def draw(self, surface):
        """Draw the elevator on the given surface"""
        # Calculate positions
        screen_height = surface.get_height()
        y_pos = screen_height - int(self.current_floor * CELL_HEIGHT) - CELL_HEIGHT
        x_pos = self.x_pos * CELL_WIDTH
        width = CELL_WIDTH
        
        # Draw shaft from min to max floor
        shaft_top = screen_height - (self.max_floor * CELL_HEIGHT) - CELL_HEIGHT
        shaft_bottom = screen_height - (self.min_floor * CELL_HEIGHT)
        pygame.draw.rect(
            surface,
            ELEVATOR_SHAFT_COLOR,
            (x_pos, shaft_top, width, shaft_bottom - shaft_top)
        )
        
        # Draw elevator car
        color = ELEVATOR_OPEN_COLOR if self.door_open else ELEVATOR_CLOSED_COLOR
        pygame.draw.rect(
            surface,
            color,
            (x_pos, y_pos, width, CELL_HEIGHT)
        )