from __future__ import annotations  # Defer type evaluation

from typing import TYPE_CHECKING, Final

import pygame
from pygame.font import Font

from mytower.game.core.config import (PersonConfigProtocol,
                                      PersonCosmeticsProtocol)
from mytower.game.core.constants import (  # TODO: Move this into a config
    BLOCK_WIDTH, DEFAULT_FLOOR_HEIGHT)
from mytower.game.core.units import Blocks, Pixels

if TYPE_CHECKING:
    from pygame import Surface

    from mytower.game.models.model_snapshots import PersonSnapshot
    from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger


class PersonRenderer:
    def __init__(self, person_config: PersonConfigProtocol, person_cosmetics: PersonCosmeticsProtocol, logger_provider: LoggerProvider) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("PersonRenderer")
        self._cosmetics: PersonCosmeticsProtocol = person_cosmetics
        self._config: PersonConfigProtocol = person_config

    # Someday this will be replaced with a proper transform system
    def y_position(self, surface: Surface, vert_position: Blocks) -> Pixels:
        """Calculate the y position for the given person"""
        apparent_floor: Blocks = vert_position - Blocks(1.0)  # Floors are 1 indexed / Alternatively, we want the feet to be at the bottom of the block
        z_bottom: Pixels = apparent_floor.in_pixels
        
        half_floor_height: Pixels = Pixels(int(float(DEFAULT_FLOOR_HEIGHT.in_pixels) / 2.0))
        z_centered: Pixels = z_bottom + half_floor_height

        screen_height: Pixels = Pixels(surface.get_height())
        y_centered: Pixels = screen_height - z_centered
        return y_centered


    def x_position(self, _: Surface, horiz_position: Blocks) -> Pixels:
        """Calculate the x position for the given person"""
        x_left: Pixels = horiz_position.in_pixels
        block_half_width: Pixels = Pixels(int(BLOCK_WIDTH.in_pixels / 2.0))
        x_centered: Pixels = x_left + block_half_width
        return x_centered


    def draw(self, drawing_surface: Surface, person: PersonSnapshot) -> None:
        """Draw the person on the given surface"""
        self._logger.trace(f"Drawing person: {person.person_id}")

        # Calculate position and draw a simple circle for now
        y_center: Pixels = self.y_position(drawing_surface, person.current_vertical_position)
        x_center: Pixels = self.x_position(drawing_surface, person.current_horizontal_position)
        draw_center: tuple[int, int] = (int(x_center), int(y_center))
        draw_radius: int = int(self._config.RADIUS.in_pixels)
        
        x_dest_center: Pixels = self.x_position(drawing_surface, person.destination_horizontal_position)
        y_dest_center: Pixels = self.y_position(drawing_surface, Blocks(person.destination_floor_num))
        draw_dest_center: tuple[int, int] = (int(x_dest_center), int(y_dest_center))
        
        font: Final[Font] = pygame.font.SysFont("Consolas", 24)
        dest_target: Final[Surface] = font.render("X", True, person.draw_color)
        drawing_surface.blit(dest_target, (draw_dest_center[0] - dest_target.get_width() // 2, draw_dest_center[1] - dest_target.get_height() // 2))
        # Draw the person as a circle
        pygame.draw.circle(drawing_surface, person.draw_color, draw_center, draw_radius)
        
        
