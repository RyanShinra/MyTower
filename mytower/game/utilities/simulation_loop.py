import threading
import time

from mytower.api.game_bridge import GameBridge
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger


def run_simulation_loop(bridge: GameBridge, logger_provider: LoggerProvider, target_fps: int = 60) -> None:
    """Run the game loop without pygame display"""
    logger: MyTowerLogger = logger_provider.get_logger("SimulationLoop")
    logger.info(f"Starting simulation loop at target {target_fps} FPS")

    frame_interval: float = 1.0 / target_fps
    last_log_time: float = time.perf_counter()
    frame_count: int = 0

    # Simple game loop
    # TODO: Add proper & graceful shutdown handling
    while True:
        frame_start_time: float = time.perf_counter()

        # Be sure to use the game_bridge here, not the game_controller directly
        bridge.update_game(frame_interval)

        frame_end_time: float = time.perf_counter()
        frame_elapsed_time: float = frame_end_time - frame_start_time
        sleep_duration: float = frame_interval - frame_elapsed_time

        # Log actual vs intended sleep
        pre_sleep: float = time.perf_counter()
        if sleep_duration > 0:
            time.sleep(sleep_duration)
        else:
            # We're running behind, consider logging a warning if this happens often
            logger.warning(f"Simulation loop is running behind schedule by {-sleep_duration:.4f} seconds")
            pass

        post_sleep: float = time.perf_counter()
        actual_sleep: float = post_sleep - pre_sleep

        frame_count += 1

        # Log every 5 seconds
        if frame_count % (target_fps * 5) == 0:
            elapsed_wall_time: float = time.perf_counter() - last_log_time
            expected_time: float = 5.0  # Should be ~5 seconds
            speedup: float = expected_time / elapsed_wall_time if elapsed_wall_time > 0 else 0

            logger.info(
                f"Frame {frame_count}: "
                f"Process={frame_elapsed_time*1000:.2f}ms, "
                f"Sleep(target)={sleep_duration*1000:.2f}ms, "
                f"Sleep(actual)={actual_sleep*1000:.2f}ms, "
                f"Wall-time speedup={speedup:.2f}x"
            )
            last_log_time = time.perf_counter()

def start_simulation_thread(
    bridge: GameBridge, logger_provider: LoggerProvider, target_fps: int = 60
) -> threading.Thread:
    """Start the simulation in a background thread"""
    thread = threading.Thread(
        target=run_simulation_loop, args=(bridge, logger_provider, target_fps), daemon=True, name="GameSimulation"
    )
    thread.start()

    # Wait for it to be ready
    if not bridge.game_thread_ready.wait(timeout=10.0):
        raise RuntimeError("Simulation thread failed to initialize")

    return thread
