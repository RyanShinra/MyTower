from __future__ import annotations  # Defer type evaluation

from typing import TYPE_CHECKING

import pygame

from mytower.game.core.constants import FLOORBOARD_HEIGHT
from mytower.game.core.primitive_constants import PIXELS_PER_METER
from mytower.game.core.types import VerticalDirection
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
            raise ValueError(
                f"Elevator bank {elevator_bank.id} max_floor {elevator_bank.max_floor} < min_floor {elevator_bank.min_floor}"
            )

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
            rect_from_pixels(shaft_left_x, shaft_top_y, width, shaft_height),
        )

        # Draw the shaft overhead
        pygame.draw.rect(
            surface,
            self._cosmetics_config.SHAFT_OVERHEAD_COLOR,
            rect_from_pixels(
                shaft_left_x, shaft_overhead_top_y, width, self._cosmetics_config.SHAFT_OVERHEAD_HEIGHT.in_pixels
            ),
        )

        # Calculate font size based on shaft width for crisp rendering
        arrow_font_size: int = max(12, int(width.value * 0.65))
        arrow_font = pygame.font.SysFont("Arial", arrow_font_size)

        for floor_number in range(elevator_bank.min_floor, elevator_bank.max_floor + 1):
            floor_bottom_z: Pixels = Blocks(floor_number - 1).in_pixels  # TODO: Extract this from FloorRenderer
            floor_top_z: Pixels = (
                floor_bottom_z + Blocks(1).in_pixels
            )  # TODO: This height depends on the floor, so send in that snapshot
            floor_top_y: Pixels = (
                screen_height - floor_top_z
            )  # This will need adjustment if floors are taller than 1 Block

            # Draw the floorboard at the top of the floor
            # TODO: #52 This should come from the FloorSnapshot instead of being hardcoded
            pygame.draw.rect(
                surface,
                self._cosmetics_config.SHAFT_OVERHEAD_COLOR,
                rect_from_pixels(shaft_left_x, floor_top_y, width, FLOORBOARD_HEIGHT),
            )

            #  TODO: Make the line thickness a config option
            # Get active call directions for this floor
            active_directions: set[VerticalDirection] = elevator_bank.floor_requests.get(floor_number, set())

            # Draw up arrow if requested
            if VerticalDirection.UP in active_directions:
                up_arrow = arrow_font.render("▲", True, (0, 255, 0))  # Green
                # arrow_width, arrow_height = up_arrow.get_size()
                # TODO: #53 Create a centering function
                # up_text_x: Pixels = shaft_left_x + (width - Pixels(arrow_width)) / 2.0
                up_text_x: Pixels = shaft_left_x
                up_text_z: Pixels = floor_top_z + Pixels(int(PIXELS_PER_METER / 3.0))
                up_text_y: Pixels = screen_height - up_text_z
                surface.blit(up_arrow, (up_text_x.value, up_text_y.value))

            # Draw down arrow if requested
            if VerticalDirection.DOWN in active_directions:
                down_arrow = arrow_font.render("▼", True, (255, 0, 0))  # Red
                # arrow_width, arrow_height = down_arrow.get_size()
                # down_text_x: Pixels = shaft_left_x + (width - Pixels(arrow_width)) / 2.0
                down_text_x: Pixels = shaft_left_x
                down_text_z: Pixels = floor_bottom_z + Blocks(1).in_pixels / 2.0 + Pixels(int(PIXELS_PER_METER / 3.0))
                down_text_y: Pixels = screen_height - down_text_z
                surface.blit(down_arrow, (down_text_x.value, down_text_y.value))
