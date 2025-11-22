# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

from __future__ import annotations  # Defer type evaluation

from typing import TYPE_CHECKING

import pygame

from mytower.game.core.units import Pixels, rect_from_pixels

if TYPE_CHECKING:
    from pygame import Surface

    from mytower.game.core.config import ElevatorCosmeticsProtocol
    from mytower.game.models.model_snapshots import ElevatorSnapshot
    from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger


class ElevatorRenderer:

    def __init__(self, logger_provider: LoggerProvider, cosmetics_config: ElevatorCosmeticsProtocol) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("ElevatorRenderer")
        self._cosmetics_config: ElevatorCosmeticsProtocol = cosmetics_config


    def draw(self, surface: Surface, elevator: ElevatorSnapshot) -> None:
        screen_height: Pixels = Pixels(surface.get_height())
        elevator_height: Pixels = self._cosmetics_config.ELEVATOR_HEIGHT.in_pixels

        elevator_top_z: Pixels = elevator.vertical_position.in_pixels
        elevator_top_y: Pixels = screen_height - elevator_top_z

        elevator_width: Pixels = self._cosmetics_config.ELEVATOR_WIDTH.in_pixels
        elevator_left_x: Pixels = elevator.horizontal_position.in_pixels

        color = self._cosmetics_config.OPEN_COLOR if elevator.door_open else self._cosmetics_config.CLOSED_COLOR

        pygame.draw.rect(
            surface, color, rect_from_pixels(elevator_left_x, elevator_top_y, elevator_width, elevator_height)
        )
