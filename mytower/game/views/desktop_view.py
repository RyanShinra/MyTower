# game/game_state.py
from typing import Final

import pygame
from pygame import Surface
from pygame.font import Font

from mytower.game.core.config import GameConfig
from mytower.game.core.types import PersonState
from mytower.game.core.units import Time
from mytower.game.models.model_snapshots import (
    BuildingSnapshot,
    ElevatorBankSnapshot,
    ElevatorSnapshot,
    FloorSnapshot,
    PersonSnapshot,
)
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger
from mytower.game.views.desktop_ui import UIConfigProtocol
from mytower.game.views.renderers.elevator_bank_renderer import ElevatorBankRenderer
from mytower.game.views.renderers.elevator_renderer import ElevatorRenderer
from mytower.game.views.renderers.floor_renderer import FloorRenderer
from mytower.game.views.renderers.person_renderer import PersonRenderer


class DesktopView:
    """
    Manages the overall game state including the building, UI, and game controls.
    """


    def __init__(
        self, logger_provider: LoggerProvider, config: GameConfig, screen_width: int, screen_height: int
    ) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("GameState")

        self._screen_width: int = screen_width
        self._screen_height: int = screen_height

        # Configuration
        self._config: Final[GameConfig] = config
        ui_config: Final[UIConfigProtocol] = self._config.ui_config  # For easier access
        floor_font: Final[Font] = pygame.font.SysFont(ui_config.FLOOR_LABEL_FONT_NAME, ui_config.FLOOR_LABEL_FONT_SIZE)

        self._person_renderer: PersonRenderer = PersonRenderer(
            self._config.person, self._config.person_cosmetics, logger_provider
        )
        self._elevator_renderer: ElevatorRenderer = ElevatorRenderer(logger_provider, self._config.elevator_cosmetics)
        self._elevator_bank_renderer: ElevatorBankRenderer = ElevatorBankRenderer(
            logger_provider, self._config.elevator_cosmetics
        )
        self._floor_renderer: FloorRenderer = FloorRenderer(logger_provider, floor_font)

        # UI state
        self._paused: bool = False

    @property
    def screen_width(self) -> int:
        return self._screen_width

    @property
    def screen_height(self) -> int:
        return self._screen_height


    def draw(self, surface: Surface, snapshot: BuildingSnapshot, speed: float) -> None:
        """Draw the entire game state"""

        # TODO: There's nothing to draw for building yet, but we might later
        # Render in Painter's algorithm order [Sky, Building, Floors, Offices, Elevators, decorative sprites, People, UI]  # noqa: E501
        all_floors: Final[list[FloorSnapshot]] = snapshot.floors
        for floor in all_floors:
            self._floor_renderer.draw(surface, floor)

        all_people: Final[list[PersonSnapshot]] = snapshot.people
        for person in all_people:
            if person.state != PersonState.IN_ELEVATOR:
                self._person_renderer.draw(surface, person)

        all_elevator_banks: Final[list[ElevatorBankSnapshot]] = snapshot.elevator_banks
        for bank in all_elevator_banks:
            self._elevator_bank_renderer.draw(surface, bank)

        all_elevators: Final[list[ElevatorSnapshot]] = snapshot.elevators
        for elevator in all_elevators:
            self._elevator_renderer.draw(surface, elevator)

        for person in all_people:
            if person.state == PersonState.IN_ELEVATOR:
                self._person_renderer.draw(surface, person)

        # Draw UI elements
        self._draw_ui(surface, snapshot, speed)


    # TODO: Right now we have to coordinate this with the toolbar in InputHandler
    def _draw_ui(self, surface: Surface, snapshot: BuildingSnapshot, speed: float) -> None:
        """Draw UI elements like time, money, etc."""
        # Draw time
        ui_config: Final[UIConfigProtocol] = self._config.ui_config
        font: Final[Font] = pygame.font.SysFont(ui_config.UI_FONT_NAME, ui_config.UI_FONT_SIZE)

        time: Time = snapshot.time
        hours: int = int(time.in_hours // 1) % 24
        minutes: int = int(time.in_minutes // 1) % 60
        seconds: int = int(time.in_seconds // 1) % 60
        time_str: str = f"[{speed:.2f}X] Time: {hours:02d}:{minutes:02d}:{seconds:02d}"

        text: Final[Surface] = font.render(time_str, True, (255, 255, 255))  # White text
        # Draw translucent background for time text
        text_rect = text.get_rect()
        text_rect.x = 10
        text_rect.y = 60
        padding = 5
        bg_rect = text_rect.inflate(padding * 2, padding * 2)
        bg_surface = Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(190)  # 75% transparency
        bg_surface.fill((0, 0, 0))  # Black background
        surface.blit(bg_surface, bg_rect)
        surface.blit(text, (10, 60))  # OMG magic numbers

        # Draw money
        money_str: str = f"Money: ${snapshot.money:,}"
        money_text: Final[Surface] = font.render(money_str, True, (255, 255, 255))  # White text
        # Draw translucent background for money text
        money_rect = money_text.get_rect()
        money_rect.x = 10
        money_rect.y = 90
        money_bg_rect = money_rect.inflate(padding * 2, padding * 2)
        money_bg_surface = Surface((money_bg_rect.width, money_bg_rect.height))
        money_bg_surface.set_alpha(190)  # 75% transparency
        money_bg_surface.fill((0, 0, 0))  # Black background
        surface.blit(money_bg_surface, money_bg_rect)
        surface.blit(money_text, (10, 90))  # OMG magic numbers
