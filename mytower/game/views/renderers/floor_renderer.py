import pygame
from pygame import Surface
from pygame.font import Font

from mytower.game.core.constants import BLOCK_HEIGHT, BLOCK_WIDTH
from mytower.game.models.model_snapshots import FloorSnapshot
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger


class FloorRenderer:
    def __init__(self, logger_provider: LoggerProvider, font: Font) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("FloorRenderer")
        self._font: Font = font

    def calculate_floor_bottom_position(self, floor_number: int) -> int:
        """
        Calculates the bottom position (in pixels) of the given floor number.
        Floors are 1-indexed, so floor 1 starts at position 0.
        """
        return (floor_number - 1) * BLOCK_HEIGHT

    # TODO: The lower edge depends on the floor below it, so we need to pass that in (in blocks) instead of floor_num
    def draw(self, surface: Surface, floor: FloorSnapshot) -> None:
        screen_height: int = surface.get_height()
        floor_height: int = floor.floor_height_blocks * BLOCK_HEIGHT

        floor_bottom_z: int = self.calculate_floor_bottom_position(floor.floor_number)
        floor_top_z: int = floor_bottom_z + floor_height
        floor_top_y: int = screen_height - floor_top_z
        left_edge: int = floor.left_edge_block * BLOCK_WIDTH
        floor_width: int = floor.floor_width_blocks * BLOCK_WIDTH

        # Draw the main floor rectangle
        pygame.draw.rect(surface, floor.floor_color, (left_edge, floor_top_y, floor_width, floor_height))

        # Draw the floorboard at the top of the floor
        pygame.draw.rect(surface, floor.floorboard_color, (left_edge, floor_top_y, floor_width, 4))

        # Optionally draw the floor number for debugging
        text_surface: Surface = self._font.render(f"Floor {floor.floor_number}", True, (0, 0, 0))
        surface.blit(text_surface, (left_edge + 5, floor_top_y + 5))