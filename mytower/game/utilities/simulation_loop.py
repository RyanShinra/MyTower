import threading
import time
from mytower.api.game_bridge import GameBridge


def run_simulation_loop(bridge: GameBridge, target_fps: int = 60) -> None:
    """Run the game loop without pygame display"""
    frame_interval: float = 1.0 / target_fps
    
    # Simple game loop
    # TODO: Add proper & graceful shutdown handling
    while True:
        # Be sure to use the game_bridge here, not the game_controller directly
        bridge.update_game(frame_interval)
        time.sleep(frame_interval)


def start_simulation_thread(bridge: GameBridge, target_fps: int = 60) -> threading.Thread:
    """Start the simulation in a background thread"""
    thread = threading.Thread(
        target=run_simulation_loop,
        args=(bridge, target_fps),
        daemon=True,
        name="GameSimulation"
    )
    thread.start()
    
    # Wait for it to be ready
    if not bridge.game_thread_ready.wait(timeout=10.0):
        raise RuntimeError("Simulation thread failed to initialize")
    
    return thread