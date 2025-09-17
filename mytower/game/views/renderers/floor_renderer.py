import pygame
from pygame import Surface
from pygame.font import Font
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict
from typing_extensions import Final

from mytower.game.core.constants import (
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

from mytower.game.core.types import Color, FloorType
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger

@dataclass
class FloorInfo:
    """
    Struct
    """

    color: Color
    height: int

# Available floor types
LOBBY_INFO: Final = FloorInfo(LOBBY_COLOR, LOBBY_HEIGHT)
FLOOR_TYPES: Dict[FloorType, FloorInfo] = {
    FloorType.LOBBY: FloorInfo(LOBBY_COLOR, LOBBY_HEIGHT),
    FloorType.OFFICE: FloorInfo(OFFICE_COLOR, OFFICE_HEIGHT),
    FloorType.APARTMENT: FloorInfo(APARTMENT_COLOR, APARTMENT_HEIGHT),
    FloorType.HOTEL: FloorInfo(HOTEL_COLOR, HOTEL_HEIGHT),
    FloorType.RESTAURANT: FloorInfo(RESTAURANT_COLOR, RESTAURANT_HEIGHT),
    FloorType.RETAIL: FloorInfo(RETAIL_COLOR, RETAIL_HEIGHT),
}


class FloorRenderer:
    def __init__(self, logger_provider: LoggerProvider, font: Font) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("FloorRenderer")
        self._font: Font = font

    # TODO: The lower edge depends on the floor below it, so we need to pass that in (in blocks) instead of floor_num
    def draw(self, surface: Surface, floor_num: int, left_edge: int, floor_width: int, floor_type: FloorType) -> None:
        screen_height: int = surface.get_height()
        floor_height: int = FLOOR_TYPES[floor_type].height

        floor_bottom_z: int = (floor_num - 1) * BLOCK_HEIGHT  # Floors are 1 indexed
        floor_top_z: int = floor_bottom_z + floor_height  # NOTE: This will break of floor_height is not 1 block
        floor_top_y: int = screen_height - floor_top_z

        # Draw the main floor rectangle
        pygame.draw.rect(surface, FLOOR_TYPES[floor_type].color, (left_edge, floor_top_y, floor_width, floor_height))

        # Draw the floorboard at the top of the floor
        pygame.draw.rect(surface, FLOORBOARD_COLOR, (left_edge, floor_top_y, floor_width, 4))

        # Optionally draw the floor number for debugging
        text_surface: Surface = self._font.render(f"Floor {floor_num}", True, (0, 0, 0))
        surface.blit(text_surface, (left_edge + 5, floor_top_y + 5))