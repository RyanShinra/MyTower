# game/ui.py
import pygame
from typing import List, Optional
from game.constants import (
    BUTTON_COLOR, BUTTON_HOVER_COLOR, UI_TEXT_COLOR,
    UI_BACKGROUND_COLOR, UI_BORDER_COLOR
)
from game.types import RGB, MousePos, MouseButtons, PygameSurface

class Button:
    """
    A simple button UI element
    """
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color:RGB=BUTTON_COLOR, hover_color:RGB=BUTTON_HOVER_COLOR, text_color:RGB=UI_TEXT_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.is_clicked = False
        
    def update(self, mouse_pos: MousePos, mouse_pressed: MouseButtons) -> None:
        """Update button state based on mouse position and clicks"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.is_clicked = self.is_hovered and mouse_pressed[0]
        
    def draw(self, surface: PygameSurface) -> None:
        """Draw the button on the given surface"""
        # Draw button background
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, self.text_color, self.rect, 2)  # Border
        
        # Draw text
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class Toolbar:
    """
    A toolbar for building tools and controls
    """
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.buttons: List[Button] = []
        self.active_tool: Optional[str] = None
        self.bg_color = UI_BACKGROUND_COLOR
        
    def add_button(self, text: str, width: int = 100, height: int = 30) -> Button:
        """Add a button to the toolbar"""
        x = self.rect.x + 10 + len(self.buttons) * (width + 10)
        y = self.rect.y + (self.rect.height - height) // 2
        
        button = Button(x, y, width, height, text)
        self.buttons.append(button)
        return button
        
    def update(self, mouse_pos: MousePos, mouse_pressed: MouseButtons) -> None:
        """Update toolbar and its buttons"""
        for button in self.buttons:
            button.update(mouse_pos, mouse_pressed)
            
    def draw(self, surface: PygameSurface) -> None:
        """Draw the toolbar and its buttons"""
        # Draw toolbar background
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 2)  # Border
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)