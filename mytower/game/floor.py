# game/floor.py
import pygame

class Floor:
    """
    A floor in the building that can contain various room types
    """
    # Available floor types
    FLOOR_TYPES = {
        "LOBBY": {"color": (200, 200, 200), "height": 1},
        "OFFICE": {"color": (150, 200, 250), "height": 1},
        "APARTMENT": {"color": (250, 200, 150), "height": 1},
        "HOTEL": {"color": (200, 150, 250), "height": 1},
        "RESTAURANT": {"color": (250, 150, 200), "height": 1},
        "RETAIL": {"color": (150, 250, 200), "height": 1},
    }
    
    def __init__(self, building, floor_num, floor_type):
        self.building = building
        self.floor_num = floor_num
        
        if floor_type not in self.FLOOR_TYPES:
            raise ValueError(f"Invalid floor type: {floor_type}")
        
        self.floor_type = floor_type
        self.color = self.FLOOR_TYPES[floor_type]["color"]
        self.height = self.FLOOR_TYPES[floor_type]["height"]
        
        # Grid of rooms/spaces on this floor
        self.grid = [None] * building.width
    
    def update(self, dt):
        """Update floor simulation"""
        pass  # To be implemented
    
    def draw(self, surface):
        """Draw the floor on the given surface"""
        # Calculate vertical position (inverted Y axis, 0 is at the bottom)
        # Each floor is 20 pixels tall in this example
        screen_height = surface.get_height()
        floor_height = 20 * self.height
        y_pos = screen_height - (self.floor_num * floor_height) - floor_height
        
        # Draw the main floor rectangle
        pygame.draw.rect(
            surface, 
            self.color, 
            (0, y_pos, self.building.width * 20, floor_height)
        )
        
        # Draw floor number
        font = pygame.font.SysFont(None, 20)
        text = font.render(f"{self.floor_num}", True, (0, 0, 0))
        surface.blit(text, (5, y_pos + 5))