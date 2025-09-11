from __future__ import annotations  # Defer type evaluation

from typing import TYPE_CHECKING
import pygame

from mytower.game.core.constants import BLOCK_HEIGHT, BLOCK_WIDTH # TODO: Move this into a config
from mytower.game.entities.person import PersonConfigProtocol, PersonCosmeticsProtocol

if TYPE_CHECKING:
    from pygame import Surface
    from mytower.game.models.model_snapshots import PersonSnapshot
    from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger


class PersonRenderer:
    def __init__(self, person_config: PersonConfigProtocol, person_cosmetics: PersonCosmeticsProtocol, logger_provider: LoggerProvider) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("PersonRenderer")
        self._cosmetics: PersonCosmeticsProtocol = person_cosmetics
        self._config: PersonConfigProtocol = person_config
        
    def y_position(self, surface: Surface, person: PersonSnapshot) -> int:
        """Calculate the z position for the given person"""
        apparent_floor: float = person.current_floor_float - 1.0  # Floors are 1 indexed
        z_bottom: float = apparent_floor * BLOCK_HEIGHT
        z_centered: int = int(z_bottom + (BLOCK_HEIGHT / 2))
        
        screen_height: int = surface.get_height()
        y_pos: int = screen_height - z_centered
        return y_pos


    def x_position(self, surface: Surface, person: PersonSnapshot) -> int:
        """Calculate the x position for the given person"""
        x_left: float = person.current_block_float * BLOCK_WIDTH
        x_centered: int = int(x_left + (BLOCK_WIDTH / 2))
        return x_centered
    


    def draw(self, surface: Surface, person: PersonSnapshot) -> None:
        """Draw the person on the given surface"""
        self._logger.debug(f"Drawing person: {person.person_id}")
        
        # Calculate position and draw a simple circle for now
        y_pos: int = self.y_position(surface, person)
        x_pos: int = self.x_position(surface, person)

        # Draw the person as a circle
        pygame.draw.circle(surface, person.draw_color, (x_pos, y_pos), self._config.radius)
