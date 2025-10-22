from __future__ import annotations  # Defer type evaluation

from typing import TYPE_CHECKING

import pygame

from mytower.game.core.units import Blocks, Pixels, rect_from_pixels

if TYPE_CHECKING:
    from pygame import Surface

    from mytower.game.core.config import ElevatorCosmeticsProtocol
    from mytower.game.models.model_snapshots import ElevatorBankSnapshot
    from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger
    
    
class ElevatorBankRenderer:
    def __init__(self, logger_provider: LoggerProvider, cosmetics_config: ElevatorCosmeticsProtocol) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("ElevatorBankRenderer")
        self._cosmetics_config: ElevatorCosmeticsProtocol = cosmetics_config


    def draw(self, surface: Surface, elevator_bank: ElevatorBankSnapshot) -> None:
        screen_height: Pixels = Pixels(surface.get_height())
        
        max_floor_block: Blocks = Blocks(elevator_bank.max_floor)
        min_floor_block: Blocks = Blocks(elevator_bank.min_floor - 1)  # Include ground floor space
        
        if max_floor_block < min_floor_block:
            raise ValueError(f"Elevator bank {elevator_bank.id} max_floor {elevator_bank.max_floor} < min_floor {elevator_bank.min_floor}")

        # TODO: This all breaks down if floors are more than 1 Block tall (eg. lobby)
        shaft_height: Pixels = Blocks(elevator_bank.max_floor - elevator_bank.min_floor + 1).in_pixels
        shaft_top_z: Pixels = Blocks(elevator_bank.max_floor).in_pixels
        shaft_top_y: Pixels = screen_height - shaft_top_z
        shaft_left_x: Pixels = elevator_bank.horizontal_position.in_pixels
        width: Pixels = self._cosmetics_config.ELEVATOR_WIDTH.in_pixels

        shaft_overhead_top_z: Pixels = shaft_top_z + self._cosmetics_config.SHAFT_OVERHEAD_HEIGHT.in_pixels
        shaft_overhead_top_y: Pixels = screen_height - shaft_overhead_top_z

        # Draw the elevator shaft
        pygame.draw.rect(
            surface,
            self._cosmetics_config.SHAFT_COLOR,
            rect_from_pixels(shaft_left_x, shaft_top_y, width, shaft_height))
        
        # Draw the shaft overhead
        pygame.draw.rect(
            surface,
            self._cosmetics_config.SHAFT_OVERHEAD_COLOR,
            rect_from_pixels(shaft_left_x, shaft_overhead_top_y, width, self._cosmetics_config.SHAFT_OVERHEAD_HEIGHT.in_pixels)
        )
