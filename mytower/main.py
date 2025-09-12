import sys
from typing import NoReturn

import pygame
from pygame.surface import Surface
from pygame.time import Clock

from mytower.game.core.config import GameConfig
from mytower.game.core.constants import BACKGROUND_COLOR, FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from mytower.game.controllers.game_controller import GameController
from mytower.game.models.game_model import GameModel
from mytower.game.utilities import demo_builder
from mytower.game.utilities.input import MouseState, mouse
from mytower.game.utilities.logger import LoggerProvider
from mytower.game.views.desktop_view import DesktopView

# Initialize pygame
# pylint: disable=no-member
pygame.init()

# Get display info and calculate 75% of display size
display_info = pygame.display.Info()
max_width = int(display_info.current_w * 0.75)
max_height = int(display_info.current_h * 0.75)

# Use the minimum of 75% of display or the constants
window_width: int = min(SCREEN_WIDTH, max_width)
window_height: int = min(SCREEN_HEIGHT, max_height)

# Set up the display
screen: Surface = pygame.display.set_mode((window_width, window_height), vsync=1)
pygame.display.set_caption("MyTower")

clock: Clock = pygame.time.Clock()


def main() -> NoReturn:
    # Make the Logger provider, if we need to use this outside main(), then we can promote it to file scope
    logger_provider: LoggerProvider = LoggerProvider()
    main_logger: demo_builder.MyTowerLogger = logger_provider.get_logger("Main")

    # Initialize the mouse with the logger provider
    global mouse
    mouse = MouseState(logger_provider)

    # Create game state
    config: GameConfig = GameConfig()
    game_model = GameModel(logger_provider)
    game_controller = GameController(model=game_model, logger_provider=logger_provider)
    desktop_view = DesktopView(logger_provider, game_model, game_controller, config, window_width, window_height)
    demo_builder.build_model_building(game_controller, logger_provider)
    running = True
    main_logger.info("Entering main loop.")
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
                    game_controller.set_paused(not game_controller.is_paused())
                elif event.key == pygame.K_UP:
                    game_controller.set_speed(game_controller.speed + 0.25)
                elif event.key == pygame.K_DOWN:
                    game_controller.set_speed(game_controller.speed - 0.25)

        # Update mouse state
        mouse.update()

        # Update game state
        game_controller.update(dt)

        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        desktop_view.draw(screen)

        # Update the display
        pygame.display.flip()

        # Cap the framerate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
