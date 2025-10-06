# mytower/main.py
"""
MyTower - Main entry point

Supports multiple execution modes:
- Desktop: Local game with pygame rendering
- Headless: GraphQL server only (for AWS deployment)
- Hybrid: Desktop + local GraphQL server (for testing)
- Remote: Desktop connected to remote server (future)
"""

import sys
import threading
from typing import NoReturn

import pygame
from pygame.surface import Surface
from pygame.time import Clock

from mytower.api.game_bridge import GameBridge, initialize_game_bridge
from mytower.api.server import run_server
from mytower.game.controllers.game_controller import GameController
from mytower.game.core.config import GameConfig
from mytower.game.core.constants import BACKGROUND_COLOR, FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from mytower.game.models.game_model import GameModel
from mytower.game.models.model_snapshots import BuildingSnapshot
from mytower.game.utilities import demo_builder
from mytower.game.utilities.cli_args import GameArgs, parse_args, print_startup_banner
from mytower.game.utilities.input import MouseState
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger
from mytower.game.utilities.simulation_loop import start_simulation_thread
from mytower.game.views.desktop_view import DesktopView


def setup_game(args: GameArgs, logger_provider: LoggerProvider) -> tuple[GameBridge, GameController]:
    """
    Common game setup for all modes.
    
    Creates the core game objects:
    - GameModel (simulation state)
    - GameController (command execution)
    - GameBridge (thread-safe coordination)
    
    Optionally populates with demo content.
    """
    game_model = GameModel(logger_provider)
    game_controller = GameController(model=game_model, logger_provider=logger_provider)
    bridge = initialize_game_bridge(game_controller)
    
    if args.demo:
        demo_builder.build_model_building(game_controller, logger_provider)
    
    return bridge, game_controller


def run_headless_mode(args: GameArgs) -> NoReturn:
    """
    Headless mode: GraphQL server only (for AWS deployment).
    
    Thread architecture:
    - Main thread: HTTP server (uvicorn blocks here)
    - Background thread: Game simulation loop
    """
    logger_provider = LoggerProvider()
    logger: MyTowerLogger = logger_provider.get_logger("Main")
    
    logger.info("Starting headless mode...")
    # GameBridge, GameController
    bridge, _ = setup_game(args, logger_provider)

    # Start simulation in background thread
    start_simulation_thread(bridge, target_fps=args.target_fps)
    
    # Start HTTP server on main thread (blocks)
    logger.info(f"GraphQL server starting on http://localhost:{args.port}/graphql")
    run_server(host="0.0.0.0", port=args.port)
    
    # Never reaches here (uvicorn.run blocks)
    sys.exit(0)

# pylint: disable=no-member
def run_desktop_mode(args: GameArgs) -> NoReturn:
    """
    Desktop mode: Pygame rendering with local simulation.
    
    Thread architecture:
    - Main thread: Pygame event loop + rendering (must be main on macOS)
    - Background thread: Game simulation loop
    """
    logger_provider = LoggerProvider()
    logger = logger_provider.get_logger("Main")
    
    logger.info("Starting desktop mode...")
    
    # Initialize pygame (must be on main thread)
    pygame.init()
    
    # Calculate window size (75% of screen)
    display_info = pygame.display.Info()
    max_width = int(display_info.current_w * 0.75)
    max_height = int(display_info.current_h * 0.75)
    window_width: int = min(SCREEN_WIDTH, max_width)
    window_height: int = min(SCREEN_HEIGHT, max_height)
    
    screen: Surface = pygame.display.set_mode((window_width, window_height), vsync=1)
    pygame.display.set_caption("MyTower")
    clock: Clock = pygame.time.Clock()
    
    # Setup game
    config = GameConfig()
    bridge, game_controller = setup_game(args, logger_provider)
    desktop_view = DesktopView(logger_provider, config, window_width, window_height)
    mouse = MouseState(logger_provider)
    
    # Start simulation in background thread
    start_simulation_thread(bridge, target_fps=args.target_fps)
    
    # Main pygame loop
    logger.info("Entering pygame main loop...")
    running = True
    
    while running:        
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    game_controller.set_paused(not game_controller.is_paused())
                elif event.key == pygame.K_UP:
                    game_controller.set_speed(game_controller.speed + 0.25)
                elif event.key == pygame.K_DOWN:
                    game_controller.set_speed(game_controller.speed - 0.25)
        
        # Update mouse
        mouse.update()
        
        # Get latest snapshot from bridge
        snapshot: BuildingSnapshot | None = bridge.get_building_state()
        
        # Render
        screen.fill(BACKGROUND_COLOR)
        if snapshot:
            desktop_view.draw(screen, snapshot, game_controller.speed)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit(0)


def run_hybrid_mode(args: GameArgs) -> NoReturn:
    """
    Hybrid mode: Desktop + local GraphQL server.
    
    Thread architecture:
    - Main thread: Pygame event loop + rendering
    - Background thread 1: Game simulation loop
    - Background thread 2: HTTP server (FastAPI)
    
    Both desktop and GraphQL share the same GameBridge,
    so mutations from GraphQL are immediately visible in the desktop view.
    """
    logger_provider = LoggerProvider()
    logger: MyTowerLogger = logger_provider.get_logger("Main")
    
    logger.info("Starting hybrid mode (Desktop + GraphQL)...")
    
    # Initialize pygame
    pygame.init()  # pylint: disable=no-member
    
    display_info = pygame.display.Info()
    max_width = int(display_info.current_w * 0.75)
    max_height = int(display_info.current_h * 0.75)
    window_width: int = min(SCREEN_WIDTH, max_width)
    window_height: int = min(SCREEN_HEIGHT, max_height)
    
    screen: Surface = pygame.display.set_mode((window_width, window_height), vsync=1)
    pygame.display.set_caption("MyTower - Hybrid Mode")
    clock: Clock = pygame.time.Clock()
    
    # Setup game
    config = GameConfig()
    bridge, game_controller = setup_game(args, logger_provider)
    desktop_view = DesktopView(logger_provider, config, window_width, window_height)
    mouse = MouseState(logger_provider)
    
    # Start simulation in background thread
    start_simulation_thread(bridge, target_fps=args.target_fps)
    
    # Start GraphQL server in background thread
    def graphql_thread_target() -> None:
        logger.info(f"GraphQL server starting on http://localhost:{args.port}/graphql")
        run_server(host="127.0.0.1", port=args.port)
    
    graphql_thread = threading.Thread(
        target=graphql_thread_target,
        daemon=True,
        name="GraphQLServer"
    )
    graphql_thread.start()
    
    # Main pygame loop (same as desktop mode)
    logger.info("Entering pygame main loop...")
    running = True
    
    while running:        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    game_controller.set_paused(not game_controller.is_paused())
                elif event.key == pygame.K_UP:
                    game_controller.set_speed(game_controller.speed + 0.25)
                elif event.key == pygame.K_DOWN:
                    game_controller.set_speed(game_controller.speed - 0.25)
        
        mouse.update()
        # TODO: We need to revisit this to avoid potential stutter, this blocks the main thread while updating
        # (tantamount to just doing a direct call to game_controller)
        snapshot: BuildingSnapshot | None = bridge.get_building_state()
        
        screen.fill(BACKGROUND_COLOR)
        if snapshot:
            desktop_view.draw(screen, snapshot, game_controller.speed)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit(0)


def run_remote_mode(args: GameArgs) -> NoReturn:
    """
    Remote mode: Desktop connected to remote server (future implementation).
    
    Thread architecture:
    - Main thread: Pygame event loop + rendering
    - Background thread: WebSocket client receiving snapshots
    
    In this mode, there's no local simulation - all state comes from
    the remote server via WebSocket.
    """
    logger_provider = LoggerProvider()
    logger: MyTowerLogger = logger_provider.get_logger("Main")
    
    logger.error("Remote mode not yet implemented")
    
    raise NotImplementedError(
        f"Remote mode is not yet implemented.\n"
        f"Future: Connect to {args.remote_url} via WebSocket\n"
        f"and render remote game state locally." # pyright: ignore[reportImplicitStringConcatenation]
    )


def main() -> NoReturn:
    """
    Main entry point - routes to appropriate mode based on arguments.
    """
    args: GameArgs = parse_args()
    print_startup_banner(args)
    
    # Route to appropriate mode
    if args.mode == 'headless':
        run_headless_mode(args)
    elif args.mode == 'hybrid':
        run_hybrid_mode(args)
    elif args.mode == 'remote':
        run_remote_mode(args)
    else:  # desktop
        run_desktop_mode(args)


if __name__ == "__main__":
     main()