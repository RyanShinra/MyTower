# game/game_state.py
import pygame
from pygame import Surface

# from mytower.game.building import Building
from mytower.game.controllers.game_controller import GameController
# from mytower.game.demo_builder import build_model_building
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger
from mytower.game.models.game_model import GameModel



class DesktopView:
    """
    Manages the overall game state including the building, UI, and game controls.
    """

    def __init__(self, logger_provider: LoggerProvider, game_model: GameModel, game_controller: GameController, screen_width: int, screen_height: int) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("GameState")

        self._screen_width: int = screen_width
        self._screen_height: int = screen_height

        # self._building: Building = build_model_building(logger_provider)
        self._game_model: GameModel = game_model
        self._game_controller: GameController = game_controller

        # UI state
        self._paused: bool = False

    # @property
    # def building(self) -> Building:
    #     return self._building

    @property
    def screen_width(self) -> int:
        return self._screen_width

    @property
    def screen_height(self) -> int:
        return self._screen_height


    def draw(self, surface: Surface) -> None:
        """Draw the entire game state"""
        # Draw building
        # self._logger.debug("I want to draw a building")
        #TODO: Refactor this once all the snapshots are ready and the other draw code is extracted
        self._game_model.temp_draw_building(surface)

        # Draw UI elements
        self._draw_ui(surface)



    def _draw_ui(self, surface: Surface) -> None:
        """Draw UI elements like time, money, etc."""
        # Draw time
        font = pygame.font.SysFont(None, 24)

        # Convert time to hours:minutes
        time: float = self._game_controller.get_game_time()
        hours: int = int(time // 3600) % 24
        minutes: int = int(time // 60) % 60
        seconds: int = int(time) % 60
        time_str: str = f"[{self._game_controller.speed:.2f}X] Time: {hours:02d}:{minutes:02d}:{seconds:02d}"

        text = font.render(time_str, True, (0, 0, 0))
        surface.blit(text, (10, 10))

        # Draw money
        money_str = f"Money: ${self._game_model.money:,}"
        text = font.render(money_str, True, (0, 0, 0))
        surface.blit(text, (10, 40))
