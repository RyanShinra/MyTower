# game/elevator.py
import pygame

class Elevator:
    """
    An elevator in the building that transports people between floors.
    """
    def __init__(self, building, x_pos, min_floor, max_floor):
        """
        Initialize a new elevator
        
        Args:
            building: The Building object this elevator belongs to
            x_pos: X position in grid cells
            min_floor: Lowest floor this elevator serves
            max_floor: Highest floor this elevator serves
        """
        self.building = building
        self.x_pos = x_pos
        self.min_floor = min_floor
        self.max_floor = max_floor
        
        # Current state
        self.current_floor = min_floor  # Floor number (can be fractional when moving)
        self.door_open = False
        self.occupants = []  # People inside the elevator
    
    def update(self, dt):
        """Update elevator status over time increment dt (in seconds)"""
        pass  # To be implemented
    
    def draw(self, surface):
        """Draw the elevator on the given surface"""
        # Calculate positions
        screen_height = surface.get_height()
        floor_height = 20
        y_pos = screen_height - int(self.current_floor * floor_height) - floor_height
        x_pos = self.x_pos * 20  # 20 pixels per grid cell
        width = 20
        
        # Draw shaft from min to max floor
        shaft_top = screen_height - (self.max_floor * floor_height) - floor_height
        shaft_bottom = screen_height - (self.min_floor * floor_height)
        pygame.draw.rect(
            surface,
            (100, 100, 100),
            (x_pos, shaft_top, width, shaft_bottom - shaft_top)
        )
        
        # Draw elevator car
        color = (200, 200, 50) if self.door_open else (50, 50, 200)
        pygame.draw.rect(
            surface,
            color,
            (x_pos, y_pos, width, floor_height)
        )