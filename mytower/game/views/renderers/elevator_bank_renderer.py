from __future__ import annotations  # Defer type evaluation

from typing import TYPE_CHECKING

import pygame

from mytower.game.core.constants import (  # TODO: Move this into a config
    BLOCK_HEIGHT,
    BLOCK_WIDTH,
)

if TYPE_CHECKING:
    from pygame import Surface
    from mytower.game.models.model_snapshots import ElevatorBankSnapshot
    from mytower.game.entities.elevator import ElevatorCosmeticsProtocol
    from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger
class ElevatorBankRenderer:
    def __init__(self, logger_provider: LoggerProvider, cosmetics_config: ElevatorCosmeticsProtocol) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("ElevatorBankRenderer")
        self._cosmetics_config: ElevatorCosmeticsProtocol = cosmetics_config

    def draw(self, surface: Surface, elevator_bank: ElevatorBankSnapshot) -> None:
        screen_height: int = surface.get_height()
        
        shaft_height: int = (elevator_bank.max_floor - elevator_bank.min_floor + 1) * BLOCK_HEIGHT
        shaft_top_z: int = elevator_bank.max_floor * BLOCK_HEIGHT
        shaft_top_y: int = screen_height - shaft_top_z
        shaft_left_x: int = elevator_bank.horizontal_block * BLOCK_WIDTH
        width: int = self._cosmetics_config.elevator_width

        shaft_overhead_top_z: int = shaft_top_z + self._cosmetics_config.shaft_overhead_height
        shaft_overhead_top_y: int = screen_height - shaft_overhead_top_z

        # Draw the elevator shaft
        pygame.draw.rect(
            surface,
            self._cosmetics_config.shaft_color,
            (shaft_left_x, shaft_top_y, width, shaft_height))
        
        # Draw the shaft overhead
        pygame.draw.rect(
            surface,
            self._cosmetics_config.shaft_overhead_color,
            (shaft_left_x, shaft_overhead_top_y, width, self._cosmetics_config.shaft_overhead_height)
        )
