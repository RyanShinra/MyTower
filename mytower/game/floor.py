# game/floor.py
from typing import Any, Dict, List, Optional
import pygame
from game.constants import ( CELL_WIDTH, CELL_HEIGHT, 
    LOBBY_COLOR, OFFICE_COLOR, APARTMENT_COLOR, HOTEL_COLOR, RESTAURANT_COLOR, RETAIL_COLOR,
    LOBBY_HEIGHT, OFFICE_HEIGHT, APARTMENT_HEIGHT, HOTEL_HEIGHT, RESTAURANT_HEIGHT, RETAIL_HEIGHT
)

from game.types import RGB, Color
from game.types import FloorType
from building import Building


class Floor:
    """
    A floor in the building that can contain various room types
    """
    # Available floor types
    # We shall return one day to fix this Any (turns out, that day is today)
    FLOOR_TYPES: Dict[FloorType, Dict[str, Color | int]] = {
        "LOBBY": {"color": LOBBY_COLOR, "height": LOBBY_HEIGHT},
        "OFFICE": {"color": OFFICE_COLOR, "height": OFFICE_HEIGHT},
        "APARTMENT": {"color": APARTMENT_COLOR, "height": APARTMENT_HEIGHT},
        "HOTEL": {"color": HOTEL_COLOR, "height": HOTEL_HEIGHT},
        "RESTAURANT": {"color": RESTAURANT_COLOR, "height": RESTAURANT_HEIGHT},
        "RETAIL": {"color": RETAIL_COLOR, "height": RETAIL_HEIGHT},
    }
    
    def __init__(self, building: Building, floor_num: int, floor_type: FloorType):
        self.building: Building = building
        self.floor_num: int = floor_num
        
        if floor_type not in self.FLOOR_TYPES:
            raise ValueError(f"Invalid floor type: {floor_type}")
        
        self.floor_type: FloorType = floor_type
        self.color: Color = self.FLOOR_TYPES[floor_type]["color"]
        self.height: int = self.FLOOR_TYPES[floor_type]["height"]
        
        # Grid of rooms/spaces on this floor
        self.gri: List[Optional[Any]] = [None] * building.width
    
    def update(self, dt):
        """Update floor simulation"""
        pass  # To be implemented
    
    def draw(self, surface):
        """Draw the floor on the given surface"""
        # Calculate vertical position (inverted Y axis, 0 is at the bottom)
        screen_height: int = surface.get_height()
        floor_height: int = CELL_HEIGHT * self.height
        y_pos = screen_height - (self.floor_num * floor_height) - floor_height
        
        # Draw the main floor rectangle
        pygame.draw.rect(
            surface, 
            self.color, 
            (0, y_pos, self.building.width * CELL_WIDTH, floor_height)
        )
        
        # Draw floor number
        font = pygame.font.SysFont(None, 20)
        text = font.render(f"{self.floor_num}", True, (0, 0, 0))
        surface.blit(text, (5, y_pos + 5))