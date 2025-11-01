import threading
import time

from mytower.api.game_bridge import GameBridge
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger


def run_simulation_loop(bridge: GameBridge, logger_provider: LoggerProvider, target_fps: int = 60) -> None:
    """Run the game loop without pygame display"""
    logger: MyTowerLogger = logger_provider.get_logger("SimulationLoop")
    logger.info(f"Starting simulation loop at target {target_fps} FPS")

    frame_interval: float = 1.0 / target_fps
    frame_count: int = 0
    last_log_time: float = time.perf_counter()
    sim_start_time: float = time.perf_counter()

    # Schedule first frame NOW
    next_frame_time: float = time.perf_counter()

    while True:
        frame_start_time: float = time.perf_counter()

        # Always advance by fixed interval (deterministic)
        bridge.update_game(frame_interval)

        frame_count += 1

        # Diagnostic logging every 5 seconds
        if frame_count % (target_fps * 5) == 0:
            current_time: float = time.perf_counter()
            elapsed_wall_time: float = current_time - last_log_time
            expected_time: float = 5.0
            speedup: float = expected_time / elapsed_wall_time if elapsed_wall_time > 0 else 0

            frame_process_time: float = current_time - frame_start_time

            logger.info(
                f"Frame {frame_count}: "
                f"Process={frame_process_time * 1000:.2f}ms, "
                f"Wall-time speedup={speedup:.2f}x, "
                f"Avg FPS={frame_count / (current_time - sim_start_time):.1f}"  # type: ignore
            )
            last_log_time = current_time

        # Schedule NEXT frame (absolute timing)
        next_frame_time += frame_interval
        current_time: float = time.perf_counter()
        sleep_duration: float = next_frame_time - current_time

        if sleep_duration > 0.001:  # Only sleep if > 1ms needed
            time.sleep(sleep_duration)
        elif sleep_duration < -frame_interval:
            # We're more than one frame behind - reset schedule
            logger.warning(f"Simulation loop is severely behind schedule by {-sleep_duration:.4f}s - resetting")
            next_frame_time = time.perf_counter()
        # else: slightly behind but catchable, just don't sleep

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
