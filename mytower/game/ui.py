# game/ui.py
import pygame

class Button:
    """
    A simple button UI element
    """
    def __init__(self, x, y, width, height, text, color=(200, 200, 200), hover_color=(180, 180, 180), text_color=(0, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.is_clicked = False
        
    def update(self, mouse_pos, mouse_pressed):
        """Update button state based on mouse position and clicks"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.is_clicked = self.is_hovered and mouse_pressed[0]
        
    def draw(self, surface):
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
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.buttons = []
        self.active_tool = None
        self.bg_color = (220, 220, 220)
        
    def add_button(self, text, width=100, height=30):
        """Add a button to the toolbar"""
        x = self.rect.x + 10 + len(self.buttons) * (width + 10)
        y = self.rect.y + (self.rect.height - height) // 2
        
        button = Button(x, y, width, height, text)
        self.buttons.append(button)
        return button
        
    def update(self, mouse_pos, mouse_pressed):
        """Update toolbar and its buttons"""
        for button in self.buttons:
            button.update(mouse_pos, mouse_pressed)
            
    def draw(self, surface):
        """Draw the toolbar and its buttons"""
        # Draw toolbar background
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, (150, 150, 150), self.rect, 2)  # Border
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)