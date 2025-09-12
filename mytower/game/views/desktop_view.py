# game/game_state.py
from typing import List
import pygame
from pygame import Surface
from mytower.game.controllers.game_controller import GameController
from mytower.game.core.config import GameConfig
from mytower.game.models.model_snapshots import PersonSnapshot
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger
from mytower.game.models.game_model import GameModel
from mytower.game.views.renderers.person_renderer import PersonRenderer



class DesktopView:
    """
    Manages the overall game state including the building, UI, and game controls.
    """

    def __init__(self, logger_provider: LoggerProvider, game_model: GameModel, game_controller: GameController, config: GameConfig, screen_width: int, screen_height: int) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("GameState")

        self._screen_width: int = screen_width
        self._screen_height: int = screen_height

        self._game_model: GameModel = game_model  # Eventually this will need to be removed for proper MVC
        self._game_controller: GameController = game_controller
        
        # Configuration
        self._config: GameConfig = config
        
        self._person_renderer: PersonRenderer = PersonRenderer(self._config.person, self._config.person_cosmetics, logger_provider)

        # UI state
        self._paused: bool = False

    @property
    def screen_width(self) -> int:
        return self._screen_width

    @property
    def screen_height(self) -> int:
        return self._screen_height


    def draw(self, surface: Surface) -> None:
        """Draw the entire game state"""
        
        # TODO: Person is extracted, get the others later (person is rendered last)
        self._game_model.temp_draw_building(surface)
        
        all_people: List[PersonSnapshot] = self._game_controller.get_all_people()
        for person in all_people:
            self._person_renderer.draw(surface, person)

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

        text: Surface = font.render(time_str, True, (0, 0, 0))
        surface.blit(text, (10, 10))

        # Draw money
        money_str: str = f"Money: ${self._game_model.money:,}"
        text = font.render(money_str, True, (0, 0, 0))
        surface.blit(text, (10, 40))
