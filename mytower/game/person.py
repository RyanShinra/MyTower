# game/person.py
import random
import pygame

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
        floor_height = 20
        y_pos = screen_height - (self.current_floor * floor_height) - floor_height / 2
        x_pos = self.x_pos * 20 + 10  # 20 pixels per grid cell
        
        pygame.draw.circle(
            surface,
            self.color,
            (int(x_pos), int(y_pos)),
            5  # radius
        )