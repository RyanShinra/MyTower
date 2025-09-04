# game/game_state.py
import pygame
from pygame import Surface

from mytower.game.building import Building
from mytower.game.demo_builder import build_model_building
from mytower.game.logger import LoggerProvider, MyTowerLogger



class GameState:
    """
    Manages the overall game state including the building, UI, and game controls.
    """

    def __init__(self, logger_provider: LoggerProvider, screen_width: int, screen_height: int) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("GameState")

        self._screen_width: int = screen_width
        self._screen_height: int = screen_height

        self._building: Building = build_model_building(logger_provider)

        # Game time tracking
        self._time: float = 0.0  # Game time in seconds
        self._speed: float = 3.0  # Game speed multiplier

        # UI state
        self._paused: bool = False

    @property
    def building(self) -> Building:
        return self._building

    @property
    def screen_width(self) -> int:
        return self._screen_width

    @property
    def screen_height(self) -> int:
        return self._screen_height

    @property
    def time(self) -> float:
        return self._time

    @property
    def speed(self) -> float:
        return self._speed

    def set_speed(self, value: float) -> None:
        self._speed = value

    @property
    def paused(self) -> bool:
        return self._paused

    @paused.setter
    def paused(self, value: bool) -> None:
        self._paused = value



    def update(self, dt: float) -> None:
        """Update game state by time increment dt (in seconds)"""
        if not self._paused:
            # Scale dt by game speed
            game_dt: float = dt * self._speed
            self._time += game_dt

            # Update building and all its components
            self._building.update(game_dt)



    def draw(self, surface: Surface) -> None:
        """Draw the entire game state"""
        # Draw building
        # self._logger.debug("I want to draw a building")
        self._building.draw(surface)

        # Draw UI elements
        self._draw_ui(surface)



    def _draw_ui(self, surface: Surface) -> None:
        """Draw UI elements like time, money, etc."""
        # Draw time
        font = pygame.font.SysFont(None, 24)

        # Convert time to hours:minutes
        hours = int(self._time // 3600) % 24
        minutes = int(self._time // 60) % 60
        seconds = int(self._time) % 60
        time_str = f"Time: {hours:02d}:{minutes:02d}:{seconds:02d}"

        text = font.render(time_str, True, (0, 0, 0))
        surface.blit(text, (10, 10))

        # Draw money
        money_str = f"Money: ${self._building.money:,}"
        text = font.render(money_str, True, (0, 0, 0))
        surface.blit(text, (10, 40))
