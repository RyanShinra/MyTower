import threading
import time
from mytower.api.game_bridge import GameBridge


def run_simulation_loop(bridge: GameBridge, target_fps: int = 60) -> None:
    """Run the game loop without pygame display"""
    frame_interval: float = 1.0 / target_fps
    
    # Simple game loop
    # TODO: Add proper & graceful shutdown handling
    while True:
        frame_start_time: float = time.perf_counter()
        
        # Be sure to use the game_bridge here, not the game_controller directly
        bridge.update_game(frame_interval)
        
        frame_end_time: float = time.perf_counter()
        frame_elapsed_time: float = frame_end_time - frame_start_time
        sleep_duration: float = frame_interval - frame_elapsed_time
        
        if sleep_duration > 0:
            time.sleep(sleep_duration)
        else:
            # We're running behind, consider logging a warning if this happens often
            print(f"Warning: Simulation loop is running behind schedule by {-sleep_duration:.4f} seconds")
            pass


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