# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

from typing import Final

import pygame
from pygame import Surface
from pygame.font import Font

from mytower.game.core.constants import FLOORBOARD_HEIGHT
from mytower.game.core.units import Blocks, Pixels, rect_from_pixels
from mytower.game.models.model_snapshots import FloorSnapshot
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger


class FloorRenderer:

    def __init__(self, logger_provider: LoggerProvider, font: Font) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("FloorRenderer")
        self._font: Font = font

    def calculate_floor_bottom_position(self, floor_number: int) -> Pixels:
        """
        Calculates the bottom position (in pixels) of the given floor number.
        Floors are 1-indexed, so floor 1 starts at position 0.
        """
        return Blocks(floor_number - 1).in_pixels


    # TODO: The lower edge depends on the floor below it, so we need to pass that in (in blocks) instead of floor_num
    def draw(self, surface: Surface, floor: FloorSnapshot) -> None:
        screen_height: Pixels = Pixels(surface.get_height())
        floor_height: Pixels = floor.floor_height.in_pixels

        floor_bottom_z: Pixels = self.calculate_floor_bottom_position(floor.floor_number)
        floor_top_z: Pixels = floor_bottom_z + floor_height
        floor_top_y: Pixels = screen_height - floor_top_z
        left_edge: Pixels = floor.left_edge_block.in_pixels
        floor_width: Pixels = floor.floor_width.in_pixels

        # Draw the main floor rectangle
        pygame.draw.rect(
            surface, floor.floor_color, rect_from_pixels(left_edge, floor_top_y, floor_width, floor_height)
        )

        # Draw the floorboard at the top of the floor
        pygame.draw.rect(
            surface, floor.floorboard_color, rect_from_pixels(left_edge, floor_top_y, floor_width, FLOORBOARD_HEIGHT)
        )

        # Optionally draw the floor number for debugging
        text_surface: Final[Surface] = self._font.render(f"Floor {floor.floor_number}", True, (0, 0, 0))
        surface.blit(text_surface, (int(left_edge) + 5, int(floor_top_y) + 5))
