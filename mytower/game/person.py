# game/person.py
import random
import pygame
from game.constants import CELL_WIDTH, CELL_HEIGHT

class Person:
    """
    A person in the building who moves between floors and has needs.
    """
    def __init__(self, building, current_floor, x_pos):
        self.building = building
        self.current_floor = current_floor
        self.x_pos = x_pos
        self.state = "IDLE"  # IDLE, WALKING, WAITING_FOR_ELEVATOR, IN_ELEVATOR
        
        # Appearance (for visualization)
        self.color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
    
    def update(self, dt):
        """Update person's state and position"""
        pass  # To be implemented
    
    def draw(self, surface):
        """Draw the person on the given surface"""
        # Calculate position and draw a simple circle for now
        screen_height = surface.get_height()
        y_pos = screen_height - (self.current_floor * CELL_HEIGHT) - CELL_HEIGHT / 2
        x_pos = self.x_pos * CELL_WIDTH + CELL_WIDTH / 2
        
        pygame.draw.circle(
            surface,
            self.color,
            (int(x_pos), int(y_pos)),
            5  # radius
        )