import sys
from typing import NoReturn

import pygame
from pygame.surface import Surface
from pygame.time import Clock

from mytower.game.constants import BACKGROUND_COLOR, FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from mytower.game.game_state import GameState
from mytower.game.input import MouseState, mouse
from mytower.game.logger import LoggerProvider

# Initialize pygame
# pylint: disable=no-member
pygame.init()

# Set up the display
screen: Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), vsync=1)
pygame.display.set_caption("MyTower")

clock: Clock = pygame.time.Clock()


def main() -> NoReturn:
    # Make the Logger provider, if we need to use this outside main(), then we can promote it to file scope
    logger_provider: LoggerProvider = LoggerProvider()

    # Initialize the mouse with the logger provider
    global mouse
    mouse = MouseState(logger_provider)

    # Create game state
    game_state = GameState(logger_provider, SCREEN_WIDTH, SCREEN_HEIGHT)
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
