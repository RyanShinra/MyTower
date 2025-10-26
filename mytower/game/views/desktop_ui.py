# game/ui.py
# flake8: noqa: E701

from typing import Callable, List, Optional, Protocol

import pygame
from pygame import Surface as PygameSurface
from pygame.font import Font

from mytower.game.core.types import RGB, MouseButtons, MousePos
from mytower.game.models.model_snapshots import BuildingSnapshot
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger

# pylint: disable=invalid-name
class UIConfigProtocol(Protocol):
    """Config requirements for UI elements"""

    @property
    def BACKGROUND_COLOR(self) -> RGB:
        ...

    @property
    def BORDER_COLOR(self) -> RGB:
        ...

    @property
    def TEXT_COLOR(self) -> RGB:
        ...

    @property
    def BUTTON_COLOR(self) -> RGB:
        ...

    @property
    def BUTTON_HOVER_COLOR(self) -> RGB:
        ...

    @property
    def UI_FONT_NAME(self) -> tuple[str, ...]:
        ...

    @property
    def UI_FONT_SIZE(self) -> int:
        ...

    # TODO: #23 This should be moved into its own config protocol
    @property
    def FLOOR_LABEL_FONT_NAME(self) -> tuple[str, ...]:
        ...

    @property
    def FLOOR_LABEL_FONT_SIZE(self) -> int:
        ...

# pylint: enable=invalid-name


class Button:
    """
    A simple button UI element
    """

    def __init__(
        self,
        logger_provider: LoggerProvider,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        ui_config: UIConfigProtocol,
        on_click: Callable[[BuildingSnapshot | None], None],
    ) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("ui")
        self._rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self._text: str = text
        self._ui_config: UIConfigProtocol = ui_config
        self._on_click: Callable[[BuildingSnapshot | None], None] = on_click
        self._is_hovered: bool = False
        self._is_clicked: bool = False
        self._was_pressed: bool = False  # To track previous frame's pressed state

    @property
    def rect(self) -> pygame.Rect:
        return self._rect

    @property
    def text(self) -> str:
        return self._text

    def set_text(self, text: str) -> None:
        """Update button text"""
        self._text = text

    @property
    def is_hovered(self) -> bool:
        return self._is_hovered

    def update(
        self, mouse_pos: MousePos, mouse_pressed: MouseButtons, building_snapshot: BuildingSnapshot | None
    ) -> None:
        """
        Update button state and trigger callback on click.

        Detects click as: mouse pressed this frame AND hovering AND wasn't pressed last frame
        This prevents multiple triggers while holding the button down.
        """
        self._is_hovered = self._rect.collidepoint(mouse_pos)
        is_pressed_now: bool = mouse_pressed[0]

        # Click = pressed now, hovering, and wasn't pressed last frame (rising edge)
        if self._is_hovered and is_pressed_now and not self._was_pressed:
            self._on_click(building_snapshot)  # Trigger callback

        self._was_pressed = is_pressed_now

    def draw(self, surface: PygameSurface) -> None:
        """Draw the button on the given surface"""
        # Draw button background
        color = self._ui_config.BUTTON_HOVER_COLOR if self._is_hovered else self._ui_config.BUTTON_COLOR
        pygame.draw.rect(surface, color, self._rect)
        pygame.draw.rect(surface, self._ui_config.TEXT_COLOR, self._rect, 2)  # Border

        # Draw text
        font: Font = pygame.font.SysFont(None, 24)
        text_surface: PygameSurface = font.render(self._text, True, self._ui_config.TEXT_COLOR)
        text_rect: pygame.Rect = text_surface.get_rect(center=self._rect.center)
        surface.blit(text_surface, text_rect)


class Toolbar:
    """
    A toolbar for building tools and controls
    """

    def __init__(
        self, logger_provider: LoggerProvider, x: int, y: int, width: int, height: int, ui_config: UIConfigProtocol
    ) -> None:
        self._logger_provider: LoggerProvider = logger_provider
        self._logger: MyTowerLogger = logger_provider.get_logger("ui")
        self._rect = pygame.Rect(x, y, width, height)
        self._buttons: List[Button] = []
        self._active_tool: Optional[str] = None
        self._ui_config: UIConfigProtocol = ui_config

    @property
    def rect(self) -> pygame.Rect:
        return self._rect

    @property
    def buttons(self) -> List[Button]:
        return self._buttons

    @property
    def active_tool(self) -> Optional[str]:
        return self._active_tool

    def set_active_tool(self, value: Optional[str]) -> None:
        self._active_tool = value

    def add_button(
        self, text: str, on_click: Callable[[BuildingSnapshot | None], None], width: int = 100, height: int = 30
    ) -> Button:
        """Add a button to the toolbar"""
        # x: int = self._rect.x + 10 + len(self._buttons) * (width + 10)
        x: int = self._buttons[-1].rect.right + 10 if self._buttons else self._rect.x + 10
        y: int = self._rect.y + (self._rect.height - height) // 2

        button = Button(self._logger_provider, x, y, width, height, text, self._ui_config, on_click)
        self._buttons.append(button)
        return button

    def update(
        self, mouse_pos: MousePos, mouse_pressed: MouseButtons, building_snapshot: BuildingSnapshot | None
    ) -> None:
        """Update toolbar and its buttons"""
        for button in self._buttons:
            button.update(mouse_pos, mouse_pressed, building_snapshot)

    def draw(self, surface: PygameSurface) -> None:
        """Draw the toolbar and its buttons"""
        # Draw toolbar background
        pygame.draw.rect(surface, self._ui_config.BACKGROUND_COLOR, self._rect)
        pygame.draw.rect(surface, self._ui_config.BORDER_COLOR, self._rect, 2)  # Border

        # Draw buttons
        for button in self._buttons:
            button.draw(surface)
