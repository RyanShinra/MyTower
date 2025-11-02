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
from typing import TYPE_CHECKING, NoReturn

# noqa: F401
if TYPE_CHECKING:
    import pygame  # type: ignore # noqa: F401
    from pygame.surface import Surface  # type: ignore # noqa: F401
    from pygame.time import Clock  # type: ignore # noqa: F401

from mytower.api.game_bridge import GameBridge, initialize_game_bridge
from mytower.api.server import run_server
from mytower.game.controllers.game_controller import GameController
from mytower.game.core.config import GameConfig
from mytower.game.core.constants import BACKGROUND_COLOR, FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from mytower.game.models.game_model import GameModel
from mytower.game.models.model_snapshots import BuildingSnapshot
from mytower.game.utilities import demo_builder
from mytower.game.utilities.cli_args import GameArgs, parse_args, print_startup_banner
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger
from mytower.game.utilities.simulation_loop import start_simulation_thread


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
    game_controller = GameController(
        model=game_model,
        logger_provider=logger_provider,
        fail_fast=args.fail_fast,
        print_exceptions=args.print_exceptions,
    )
    bridge: GameBridge = initialize_game_bridge(game_controller)

    if args.demo:
        demo_builder.build_model_building(game_controller, logger_provider)

    return bridge, game_controller


def run_headless_mode(args: GameArgs, logger_provider: LoggerProvider) -> NoReturn:
    """
    Headless mode: GraphQL server only (for AWS deployment).

    Thread architecture:
    - Main thread: HTTP server (uvicorn blocks here)
    - Background thread: Game simulation loop
    """
    logger: MyTowerLogger = logger_provider.get_logger("Main")

    logger.info("Starting headless mode...")
    # GameBridge, GameController
    bridge, _ = setup_game(args, logger_provider)

    # Start simulation in background thread
    start_simulation_thread(bridge, logger_provider=logger_provider, target_fps=args.target_fps)

    # Start HTTP server on main thread (blocks)
    logger.info(f"GraphQL server starting on http://localhost:{args.port}/graphql")
    logger.info("If running in Docker: Use the port from your -p flag")
    run_server(host="0.0.0.0", port=args.port)

    # Never reaches here (uvicorn.run blocks)
    sys.exit(0)


# pylint: disable=no-member
def run_desktop_mode(args: GameArgs, logger_provider: LoggerProvider) -> NoReturn:
    """
    Desktop mode: Pygame rendering with local simulation.


    Thread architecture:
    - Main thread: Pygame event loop + rendering (must be main on macOS)
    - Background thread: Game simulation loop
    """
    # Import pygame only when needed for desktop mode
    import pygame  # type: ignore # noqa: F811
    from pygame.surface import Surface  # type: ignore # noqa: F811
    from pygame.time import Clock  # type: ignore # noqa: F811

    from mytower.game.utilities.input import MouseState
    from mytower.game.views.desktop_view import DesktopView

    logger: MyTowerLogger = logger_provider.get_logger("Main")

    logger.info("Starting desktop mode...")

    # Initialize pygame (must be on main thread)
    pygame.init()

    # Calculate window size (75% of screen)
    display_info = pygame.display.Info()
    max_width = int(display_info.current_w * 0.9)
    max_height = int(display_info.current_h * 0.9)
    window_width: int = min(SCREEN_WIDTH, max_width)
    window_height: int = min(SCREEN_HEIGHT, max_height)

    screen: Surface = pygame.display.set_mode((window_width, window_height), vsync=1)
    pygame.display.set_caption(f"MyTower: (Desktop Mode) - v.0.0.1 [{window_width}x{window_height}]")
    clock: Clock = pygame.time.Clock()

    # Setup game
    config = GameConfig()
    bridge, game_controller = setup_game(args, logger_provider)
    desktop_view = DesktopView(logger_provider, config, window_width, window_height)
    mouse = MouseState(logger_provider)

    # NEW: Create input handler (manages toolbar and keyboard)
    from mytower.game.views.input_handler import InputHandler

    input_handler = InputHandler(
        logger_provider=logger_provider,
        ui_config=config.ui_config,
        screen_width=window_width,
        screen_height=window_height,
        enqueue_callback=bridge.queue_command,
    )

    # Start simulation in background thread
    start_simulation_thread(bridge, logger_provider=logger_provider, target_fps=args.target_fps)

    # Main pygame loop
    logger.info("Entering pygame main loop...")
    running = True

    while running:
        # Get latest snapshot from bridge
        snapshot: BuildingSnapshot | None = bridge.get_building_snapshot()

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
                else:
                    input_handler.handle_keyboard_event(event, snapshot)

        # Update mouse
        mouse.update()

        # Update input handler (handles button hover, clicks)
        input_handler.update(mouse.get_pos(), mouse.get_pressed(), snapshot)

        # Render
        screen.fill(BACKGROUND_COLOR)
        if snapshot:
            desktop_view.draw(screen, snapshot, game_controller.speed)

        # Draw UI (toolbar, buttons)
        input_handler.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


def run_hybrid_mode(args: GameArgs, logger_provider: LoggerProvider) -> NoReturn:
    """
    Hybrid mode: Desktop + local GraphQL server.

    Thread architecture:
    - Main thread: Pygame event loop + rendering
    - Background thread 1: Game simulation loop
    - Background thread 2: HTTP server (FastAPI)

    Both desktop and GraphQL share the same GameBridge,
    so mutations from GraphQL are immediately visible in the desktop view.
    """
    # Import pygame only when needed for hybrid mode
    import pygame  # type: ignore # noqa: F811
    from pygame.surface import Surface  # type: ignore # noqa: F811
    from pygame.time import Clock  # type: ignore # noqa: F811

    from mytower.game.utilities.input import MouseState
    from mytower.game.views.desktop_view import DesktopView

    logger: MyTowerLogger = logger_provider.get_logger("Main")

    logger.info("Starting hybrid mode (Desktop + GraphQL)...")

    # Initialize pygame
    pygame.init()  # pylint: disable=no-member

    display_info = pygame.display.Info()
    max_width = int(display_info.current_w * 0.90)
    max_height = int(display_info.current_h * 0.90)
    window_width: int = min(SCREEN_WIDTH, max_width)
    window_height: int = min(SCREEN_HEIGHT, max_height)

    screen: Surface = pygame.display.set_mode((window_width, window_height), vsync=1)
    pygame.display.set_caption(f"MyTower: (Hybrid Mode) - v.0.0.1 [{window_width}x{window_height}]")
    clock: Clock = pygame.time.Clock()

    # Setup game
    config = GameConfig()
    bridge, game_controller = setup_game(args, logger_provider)
    desktop_view = DesktopView(logger_provider, config, window_width, window_height)
    mouse = MouseState(logger_provider)

    # NEW: Create input handler (manages toolbar and keyboard)
    from mytower.game.views.input_handler import InputHandler

    input_handler = InputHandler(
        logger_provider=logger_provider,
        ui_config=config.ui_config,
        screen_width=window_width,
        screen_height=window_height,
        enqueue_callback=bridge.queue_command,
    )

    # Start simulation in background thread
    start_simulation_thread(bridge, logger_provider=logger_provider, target_fps=args.target_fps)

    # Start GraphQL server in background thread
    def graphql_thread_target() -> None:
        logger.info(f"GraphQL server starting on http://localhost:{args.port}/graphql")
        logger.info("If running in Docker: Use the port from your -p flag")
        run_server(host="127.0.0.1", port=args.port)

    graphql_thread = threading.Thread(target=graphql_thread_target, daemon=True, name="GraphQLServer")
    graphql_thread.start()

    # Main pygame loop (same as desktop mode)
    logger.info("Entering pygame main loop...")
    running = True

    while running:
        snapshot: BuildingSnapshot | None = bridge.get_building_snapshot()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # TODO: These need to go on the GameBridge command queue to avoid race conditions
                    game_controller.set_paused(not game_controller.is_paused())
                elif event.key == pygame.K_UP:
                    game_controller.set_speed(game_controller.speed + 0.25)
                elif event.key == pygame.K_DOWN:
                    game_controller.set_speed(game_controller.speed - 0.25)
                else:
                    input_handler.handle_keyboard_event(event, snapshot)

        mouse.update()
        # Update input handler (handles button hover, clicks)
        input_handler.update(mouse.get_pos(), mouse.get_pressed(), snapshot)

        screen.fill(BACKGROUND_COLOR)
        if snapshot:
            desktop_view.draw(screen, snapshot, game_controller.speed)

        # Draw UI (toolbar, buttons)
        input_handler.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


def run_remote_mode(args: GameArgs, logger_provider: LoggerProvider) -> NoReturn:
    """
    Remote mode: Desktop connected to remote server (future implementation).

    Thread architecture:
    - Main thread: Pygame event loop + rendering
    - Background thread: WebSocket client receiving snapshots

    In this mode, there's no local simulation - all state comes from
    the remote server via WebSocket.
    """
    logger: MyTowerLogger = logger_provider.get_logger("Main")

    logger.error("Remote mode not yet implemented")

    raise NotImplementedError(
        f"Remote mode is not yet implemented.\n"
        f"Future: Connect to {args.remote_url} via WebSocket\n"
        f"and render remote game state locally."  # pyright: ignore[reportImplicitStringConcatenation]
    )


def main() -> NoReturn:
    """
    Main entry point - routes to appropriate mode based on arguments.
    """
    args: GameArgs = parse_args()
    print_startup_banner(args)

    logger_provider = LoggerProvider(log_level=args.log_level, log_file=args.log_file)
    logger: MyTowerLogger = logger_provider.get_logger("Main")

    # Log startup configuration
    if args.print_exceptions:
        logger.info("Exception stack traces enabled")
    if args.fail_fast:
        logger.info("Fail-fast mode enabled")

    logger.info(f"Console Log level set to {logger.get_level_name(args.log_level)}")
    if args.log_file:
        logger.info(f"Trace Logging to file: {args.log_file}")

    # Route to appropriate mode
    if args.mode == "headless":
        run_headless_mode(args, logger_provider)
    elif args.mode == "hybrid":
        run_hybrid_mode(args, logger_provider)
    elif args.mode == "remote":
        run_remote_mode(args, logger_provider)
    else:  # desktop
        run_desktop_mode(args, logger_provider)

if __name__ == "__main__":
    main()
