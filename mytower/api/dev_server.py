
from mytower.api.server import run_server
from mytower.api.game_bridge import GameBridge, initialize_game_bridge
from mytower.game.controllers.game_controller import GameController
from mytower.game.models.game_model import GameModel
from mytower.game.utilities.logger import LoggerProvider
from mytower.game.utilities.simulation_loop import start_simulation_thread



def main() -> None:
    logger_provider = LoggerProvider()
    game_model = GameModel(logger_provider)
    game_controller = GameController(model=game_model, logger_provider=logger_provider)

    bridge: GameBridge = initialize_game_bridge(game_controller)

    # Start game loop in separate thread
    start_simulation_thread(bridge, target_fps=60)

    # Start HTTP server (blocking)
    print("Starting MyTower GraphQL server...")
    print("GraphQL Playground: http://localhost:8000/graphql")
    run_server()


if __name__ == "__main__":
    main()
