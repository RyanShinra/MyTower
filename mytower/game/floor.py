# game/floor.py
from __future__ import annotations  # Defer type evaluation
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any, Dict, List, Optional
import pygame
from game.constants import ( BLOCK_WIDTH, BLOCK_HEIGHT, 
    LOBBY_COLOR,  OFFICE_COLOR,  APARTMENT_COLOR,  HOTEL_COLOR,  RESTAURANT_COLOR,  RETAIL_COLOR, 
    LOBBY_HEIGHT, OFFICE_HEIGHT, APARTMENT_HEIGHT, HOTEL_HEIGHT, RESTAURANT_HEIGHT, RETAIL_HEIGHT, UI_TEXT_COLOR
)
from game.logger import get_logger

from game.types import Color
from game.types import FloorType
from pygame import Surface

if TYPE_CHECKING:
    from game.building import Building

logger = get_logger("floor")

# See FloorInfo below
class Floor:
    """
    A floor in the building that can contain various room types
    """
    @dataclass
    class FloorInfo:
        """
        Struct
        """
        color: Color 
        height: int


    # Available floor types
    # We shall return one day to fix this Any (turns out, that day is today)
    lobby_info = FloorInfo(LOBBY_COLOR, LOBBY_HEIGHT)
    FLOOR_TYPES: Dict[FloorType, FloorInfo] = {
        FloorType.LOBBY: FloorInfo(LOBBY_COLOR, LOBBY_HEIGHT),
        FloorType.OFFICE: FloorInfo(OFFICE_COLOR, OFFICE_HEIGHT),
        FloorType.APARTMENT: FloorInfo(APARTMENT_COLOR, APARTMENT_HEIGHT),
        FloorType.HOTEL: FloorInfo(HOTEL_COLOR, HOTEL_HEIGHT),
        FloorType.RESTAURANT: FloorInfo(RESTAURANT_COLOR, RESTAURANT_HEIGHT),
        FloorType.RETAIL: FloorInfo(RETAIL_COLOR, RETAIL_HEIGHT),
    }
    
    def __init__(self, building: Building, floor_num: int, floor_type: FloorType) -> None:
        self._building: Building = building
        # Floors are 1 indexed
        self._floor_num: int = floor_num
        
        if floor_type not in self.FLOOR_TYPES:
            raise ValueError(f"Invalid floor type: {floor_type}")
        
        self._floor_type: FloorType = floor_type
        self._color: Color = self.FLOOR_TYPES[floor_type].color
        self._height: int = self.FLOOR_TYPES[floor_type].height
        
        # Grid of rooms/spaces on this floor
        self._grid: List[Optional[Any]] = [None] * building.floor_width
    
    @property
    def building(self) -> Building:
        return self._building
        
    @property
    def floor_num(self) -> int:
        return self._floor_num
        
    @property
    def floor_type(self) -> FloorType:
        return self._floor_type
        
    @property
    def color(self) -> Color:
        return self._color
        
    @property
    def height(self) -> int:
        return self._height
        
    @property
    def grid(self) -> List[Optional[Any]]:
        return self._grid
    
    def update(self, dt: float) -> None:
        """Update floor simulation"""
        pass  # To be implemented
    
    def draw(self, surface: Surface) -> None:
        """Draw the floor on the given surface"""
        # Calculate vertical position (inverted Y axis, 0 is at the bottom)
        screen_height: int = surface.get_height()
        floor_height: int = BLOCK_HEIGHT * self._height
        # These are 1 indexed, plus 
        # 460 = 480 - (1 * 20) , the top of floor 1
        # 440 = 480 - (2 * 20) , the top of floor 2
        floor_y_top = screen_height - (self._floor_num * floor_height)
        floor_x_left = 0
        
        # Draw the main floor rectangle
        pygame.draw.rect(
            surface, 
            self._color, 
            (floor_x_left, floor_y_top, self._building.floor_width * BLOCK_WIDTH, floor_height)
        )
        pygame.draw.rect(
            surface, 
            UI_TEXT_COLOR, 
            (floor_x_left, floor_y_top, self._building.floor_width * BLOCK_WIDTH, 2)
        )
        
        # Draw floor number
        font = pygame.font.SysFont(['Palatino Linotype','Menlo', 'Lucida Sans Typewriter'], 18)
        text = font.render(f"{self._floor_num}", True, (0, 0, 0))
        surface.blit(text, (floor_x_left + 8, floor_y_top + 12))