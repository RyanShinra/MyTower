import threading
import time
from typing import NoReturn
from mytower.api.server import run_server
from mytower.api.game_bridge import GameBridge, get_game_bridge, initialize_game_bridge
from mytower.game.controllers.game_controller import GameController
from mytower.game.models.game_model import GameModel
from mytower.game.utilities.logger import LoggerProvider

def run_headless_game() -> NoReturn:
    """Run the game loop without pygame display"""
    logger_provider = LoggerProvider()
    game_model = GameModel(logger_provider)
    game_controller = GameController(model=game_model, logger_provider=logger_provider)
    
    # Set up the bridge
    initialize_game_bridge(game_controller)
    game_bridge: GameBridge = get_game_bridge()
    # Simple game loop
    # TODO: Add proper & graceful shutdown handling
    while True:
        game_bridge.update_game(0.016)  # ~60 FPS
        time.sleep(0.016)

def main() -> None:
    # Start game loop in separate thread
    game_thread = threading.Thread(target=run_headless_game, daemon=True)
    game_thread.start()
    
    # Start HTTP server (blocking)
    print("Starting MyTower GraphQL server...")
    print("GraphQL Playground: http://localhost:8000/graphql")
    run_server()

if __name__ == "__main__":
    main()
