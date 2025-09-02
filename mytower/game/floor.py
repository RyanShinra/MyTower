# game/floor.py
from __future__ import annotations  # Defer type evaluation

from dataclasses import dataclass
# from typing import TYPE_CHECKING, Any, Dict, List, Optional
from typing import TYPE_CHECKING, Dict
from typing_extensions import Final

import pygame
from pygame import Surface
from pygame.font import Font

from mytower.game.constants import (
    APARTMENT_COLOR,
    APARTMENT_HEIGHT,
    BLOCK_HEIGHT,
    BLOCK_WIDTH,
    FLOORBOARD_COLOR,
    HOTEL_COLOR,
    HOTEL_HEIGHT,
    LOBBY_COLOR,
    LOBBY_HEIGHT,
    OFFICE_COLOR,
    OFFICE_HEIGHT,
    RESTAURANT_COLOR,
    RESTAURANT_HEIGHT,
    RETAIL_COLOR,
    RETAIL_HEIGHT,
)
from mytower.game.logger import LoggerProvider, MyTowerLogger
from mytower.game.types import Color, FloorType

# from mytower.game.ui import UIConfigProtocol


if TYPE_CHECKING:
    from mytower.game.building import Building
    from mytower.game.person import PersonProtocol

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
    LOBBY_INFO: Final = FloorInfo(LOBBY_COLOR, LOBBY_HEIGHT)
    FLOOR_TYPES: Dict[FloorType, FloorInfo] = {
        FloorType.LOBBY: FloorInfo(LOBBY_COLOR, LOBBY_HEIGHT),
        FloorType.OFFICE: FloorInfo(OFFICE_COLOR, OFFICE_HEIGHT),
        FloorType.APARTMENT: FloorInfo(APARTMENT_COLOR, APARTMENT_HEIGHT),
        FloorType.HOTEL: FloorInfo(HOTEL_COLOR, HOTEL_HEIGHT),
        FloorType.RESTAURANT: FloorInfo(RESTAURANT_COLOR, RESTAURANT_HEIGHT),
        FloorType.RETAIL: FloorInfo(RETAIL_COLOR, RETAIL_HEIGHT),
    }

    def __init__(
        self, logger_provider: LoggerProvider, building: Building, floor_num: int, floor_type: FloorType
    ) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("floor")
        self._building: Building = building
        # Floors are 1 indexed
        self._floor_num: int = floor_num

        if floor_type not in self.FLOOR_TYPES:
            raise ValueError(f"Invalid floor type: {floor_type}")

        self._floor_type: FloorType = floor_type
        self._color: Color = self.FLOOR_TYPES[floor_type].color
        self._height: int = self.FLOOR_TYPES[floor_type].height

        self._people: Dict[str, PersonProtocol] = {}  # People currently on this floor    
        
        # Grid of rooms/spaces on this floor
        # mypy: allow-any-explicit
        # self._grid: List[Optional[Any]] = [None] * building.floor_width

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

    # @property
    # def grid(self) -> List[Optional[Any]]:
    #     return self._grid
    
    def add_person(self, person: PersonProtocol) -> None:
        """Add a person to the floor"""
        self._people[person.person_id] = person
        
    def remove_person(self, person_id: str) -> PersonProtocol:
        """Remove a person from the floor, returns the person if found, throws if not"""
        # This is fairly reasonable since only a person should be removing themselves from the floor
        # If it throws, then it's a pretty serious problem
        person: PersonProtocol | None = self._people.pop(person_id, None)
        if not person:
            raise KeyError(f"Person not found: {person_id}")
        return person
            
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
        floor_y_top: int = screen_height - (self._floor_num * floor_height)
        floor_x_left = 0

        # Draw the main floor rectangle
        _ = pygame.draw.rect(
            surface, self._color, (floor_x_left, floor_y_top, self._building.floor_width * BLOCK_WIDTH, floor_height)
        )
        _ = pygame.draw.rect(
            surface, FLOORBOARD_COLOR, (floor_x_left, floor_y_top, self._building.floor_width * BLOCK_WIDTH, 2)
        )

        # Draw floor number
        font: Font = pygame.font.SysFont(["Palatino Linotype", "Menlo", "Lucida Sans Typewriter"], 18)
        text: Surface = font.render(f"{self._floor_num}", True, (0, 0, 0))
        _ = surface.blit(text, (floor_x_left + 8, floor_y_top + 12))
