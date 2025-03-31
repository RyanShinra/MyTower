import pygame
import sys
from typing import NoReturn

from game.game_state import GameState

from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BACKGROUND_COLOR
from game.input import mouse

from pygame.surface import Surface
from pygame.time import Clock

# Initialize pygame
# pylint: disable=no-member
pygame.init()  

# Set up the display
screen: Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), vsync=1)
pygame.display.set_caption("MyTower")

clock: Clock = pygame.time.Clock()
def main() -> NoReturn:
    # Create game state
    game_state = GameState(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    running = True
    
    while running:
        # Calculate delta time (for time-based movement)
        dt: float = clock.get_time() / 1000.0  # Convert to seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Toggle pause
                    game_state.paused = not game_state.paused
        
        # Update mouse state
        mouse.update()
        
        # Update game state
        game_state.update(dt)
        
        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        game_state.draw(screen)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the framerate
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()