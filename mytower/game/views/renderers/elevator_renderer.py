from __future__ import annotations  # Defer type evaluation

from typing import TYPE_CHECKING

import pygame

from mytower.game.core.constants import (  # TODO: Move this into a config
    BLOCK_HEIGHT,
    BLOCK_WIDTH,
)




if TYPE_CHECKING:
    from pygame import Surface
    from mytower.game.entities.elevator import ElevatorCosmeticsProtocol
    from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger

class ElevatorRenderer:
    def __init__(self, logger_provider: LoggerProvider, cosmetics_config: ElevatorCosmeticsProtocol) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("ElevatorRenderer")
        self._cosmetics_config: ElevatorCosmeticsProtocol = cosmetics_config

    def draw(self, surface: Surface, elevator: ElevatorSnapshot) -> None:
        screen_height: int = surface.get_height()
        elevator_height: int = BLOCK_HEIGHT  # Elevators are one block high for now
        # This is technically the height of a floor, not an elevator
        elevator_top_z: float = elevator.current_floor * BLOCK_HEIGHT
        elevator_top_y: int = screen_height - int(elevator_top_z)

        elevator_width: int = BLOCK_WIDTH
        # This is technically the left edge of a block, not an elevator
        elevator_left_x: int = int(elevator.current_block * BLOCK_WIDTH)

        color = self._cosmetics_config.open_color if elevator.door_open else self._cosmetics_config.closed_color

        pygame.draw.rect(surface, color, (elevator_left_x, elevator_top_y, elevator_width, elevator_height))