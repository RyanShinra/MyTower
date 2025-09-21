# game/ui.py
from typing import List, Optional, Protocol

import pygame

from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger
from mytower.game.core.types import RGB, MouseButtons, MousePos, PygameSurface



# pylint: disable=invalid-name
class UIConfigProtocol(Protocol):
    """Config requirements for UI elements"""

    @property
    def BACKGROUND_COLOR(self) -> RGB: ...  # noqa E701

    @property
    def BORDER_COLOR(self) -> RGB: ...  # noqa E701

    @property
    def TEXT_COLOR(self) -> RGB: ...  # noqa E701

    @property
    def BUTTON_COLOR(self) -> RGB: ...  # noqa E701

    @property
    def BUTTON_HOVER_COLOR(self) -> RGB: ...  # noqa E701
    
    @property
    def UI_FONT_NAME(self) -> tuple[str, ...]: ...  # noqa E701

    @property
    def UI_FONT_SIZE(self) -> int: ...  # noqa E701
    
    # TODO: #23 This should be moved into its own config protocol
    @property
    def FLOOR_LABEL_FONT_NAME(self) -> tuple[str, ...]: ...  # noqa E701

    @property
    def FLOOR_LABEL_FONT_SIZE(self) -> int: ...  # noqa E701
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
    ) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("ui")
        self._rect = pygame.Rect(x, y, width, height)
        self._text = text
        self._ui_config: UIConfigProtocol = ui_config
        self._is_hovered = False
        self._is_clicked = False

    @property
    def rect(self) -> pygame.Rect:
        return self._rect

    @property
    def text(self) -> str:
        return self._text

    @property
    def is_clicked(self) -> bool:
        return self._is_clicked

    @property
    def is_hovered(self) -> bool:
        return self._is_hovered

    def update(self, mouse_pos: MousePos, mouse_pressed: MouseButtons) -> None:
        """Update button state based on mouse position and clicks"""
        self._is_hovered: bool = self._rect.collidepoint(mouse_pos)
        self._is_clicked: bool = self._is_hovered and mouse_pressed[0]



    def draw(self, surface: PygameSurface) -> None:
        """Draw the button on the given surface"""
        # Draw button background
        color = self._ui_config.BUTTON_HOVER_COLOR if self._is_hovered else self._ui_config.BUTTON_COLOR
        pygame.draw.rect(surface, color, self._rect)
        pygame.draw.rect(surface, self._ui_config.TEXT_COLOR, self._rect, 2)  # Border

        # Draw text
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(self._text, True, self._ui_config.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self._rect.center)
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



    def add_button(self, text: str, width: int = 100, height: int = 30) -> Button:
        """Add a button to the toolbar"""
        x: int = self._rect.x + 10 + len(self._buttons) * (width + 10)
        y: int = self._rect.y + (self._rect.height - height) // 2

        button = Button(self._logger_provider, x, y, width, height, text, self._ui_config)
        self._buttons.append(button)
        return button

    def update(self, mouse_pos: MousePos, mouse_pressed: MouseButtons) -> None:
        """Update toolbar and its buttons"""
        for button in self._buttons:
            button.update(mouse_pos, mouse_pressed)



    def draw(self, surface: PygameSurface) -> None:
        """Draw the toolbar and its buttons"""
        # Draw toolbar background
        pygame.draw.rect(surface, self._ui_config.BACKGROUND_COLOR, self._rect)
        pygame.draw.rect(surface, self._ui_config.BORDER_COLOR, self._rect, 2)  # Border

        # Draw buttons
        for button in self._buttons:
            button.draw(surface)
