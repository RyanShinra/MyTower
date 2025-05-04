# game/ui.py
import pygame
from typing import List, Optional
from game.constants import (
    BUTTON_COLOR, BUTTON_HOVER_COLOR, UI_TEXT_COLOR,
    UI_BACKGROUND_COLOR, UI_BORDER_COLOR
)
from game.types import RGB, MousePos, MouseButtons, PygameSurface
from game.logger import LoggerProvider

class Button:
    """
    A simple button UI element
    """
    def __init__(self, logger_provider: LoggerProvider, x: int, y: int, width: int, height: int, text: str, color:RGB=BUTTON_COLOR, hover_color:RGB=BUTTON_HOVER_COLOR, text_color:RGB=UI_TEXT_COLOR):
        self._logger = logger_provider.get_logger("ui")
        self._rect = pygame.Rect(x, y, width, height)
        self._text = text
        self._color = color
        self._hover_color = hover_color
        self._text_color = text_color
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
        self._is_hovered = self._rect.collidepoint(mouse_pos)
        self._is_clicked = self._is_hovered and mouse_pressed[0]
        
    def draw(self, surface: PygameSurface) -> None:
        """Draw the button on the given surface"""
        # Draw button background
        color = self._hover_color if self._is_hovered else self._color
        pygame.draw.rect(surface, color, self._rect)
        pygame.draw.rect(surface, self._text_color, self._rect, 2)  # Border
        
        # Draw text
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(self._text, True, self._text_color)
        text_rect = text_surface.get_rect(center=self._rect.center)
        surface.blit(text_surface, text_rect)

class Toolbar:
    """
    A toolbar for building tools and controls
    """
    def __init__(self, logger_provider: LoggerProvider, x: int, y: int, width: int, height: int):
        self._logger_provider: LoggerProvider = logger_provider
        self._logger = logger_provider.get_logger("ui")
        self._rect = pygame.Rect(x, y, width, height)
        self._buttons: List[Button] = []
        self._active_tool: Optional[str] = None
        self._bg_color = UI_BACKGROUND_COLOR
        
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
        x = self._rect.x + 10 + len(self._buttons) * (width + 10)
        y = self._rect.y + (self._rect.height - height) // 2
        
        button = Button(self._logger_provider, x, y, width, height, text)
        self._buttons.append(button)
        return button
        
    def update(self, mouse_pos: MousePos, mouse_pressed: MouseButtons) -> None:
        """Update toolbar and its buttons"""
        for button in self._buttons:
            button.update(mouse_pos, mouse_pressed)
            
    def draw(self, surface: PygameSurface) -> None:
        """Draw the toolbar and its buttons"""
        # Draw toolbar background
        pygame.draw.rect(surface, self._bg_color, self._rect)
        pygame.draw.rect(surface, UI_BORDER_COLOR, self._rect, 2)  # Border
        
        # Draw buttons
        for button in self._buttons:
            button.draw(surface)