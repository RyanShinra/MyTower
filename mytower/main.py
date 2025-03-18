import pygame
import sys
from pygame.locals import *
from game.game_state import GameState

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BACKGROUND_COLOR = (240, 240, 240)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MyTower")
clock = pygame.time.Clock()

def main():
    # Create game state
    game_state = GameState(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    running = True
    
    while running:
        # Calculate delta time (for time-based movement)
        dt = clock.get_time() / 1000.0  # Convert to seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_SPACE:
                    # Toggle pause
                    game_state.paused = not game_state.paused
        
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