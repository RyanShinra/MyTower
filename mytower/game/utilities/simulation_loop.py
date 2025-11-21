import threading
import time

from mytower.api.game_bridge import GameBridge
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger


def run_simulation_loop(
    bridge: GameBridge, logger_provider: LoggerProvider, target_fps: int = 60, shutdown_event: threading.Event | None = None
) -> None:
    """Run the game loop without pygame display

    Args:
        bridge: GameBridge for thread-safe game updates
        logger_provider: Logger provider for logging
        target_fps: Target frames per second
        shutdown_event: Optional event to signal graceful shutdown
    """
    logger: MyTowerLogger = logger_provider.get_logger("SimulationLoop")
    logger.info(f"Starting simulation loop at target {target_fps} FPS")

    frame_interval: float = 1.0 / target_fps
    frame_count: int = 0
    last_log_time: float = time.perf_counter()
    sim_start_time: float = time.perf_counter()

    # Schedule first frame NOW
    next_frame_time: float = time.perf_counter()
    sleep_log_counter: int = 0

    while shutdown_event is None or not shutdown_event.is_set():
        frame_start_time: float = time.perf_counter()

        # Always advance by fixed interval (deterministic)
        bridge.update_game(frame_interval)

        # Capture time immediately after game update for accurate frame processing time measurement
        frame_end_time: float = time.perf_counter()

        frame_count += 1

        # Diagnostic logging every 5 seconds
        if frame_count % (target_fps * 5) == 0:
            elapsed_wall_time: float = frame_end_time - last_log_time
            expected_time: float = 5.0
            speedup: float = expected_time / elapsed_wall_time if elapsed_wall_time > 0 else 0

            frame_process_time: float = frame_end_time - frame_start_time

            logger.debug(
                f"Frame {frame_count}: "
                f"Process={frame_process_time * 1000:.2f}ms, "
                f"Wall-time speedup={speedup:.2f}x, "
                # pyright: ignore[reportImplicitStringConcatenation]
                f"Avg FPS={frame_count / (frame_end_time - sim_start_time):.1f}"
            )
            last_log_time = frame_end_time

        # Schedule NEXT frame (absolute timing)
        next_frame_time += frame_interval
        sleep_duration: float = next_frame_time - frame_end_time

        # Only sleep if > 1ms needed.
        # Rationale: time.sleep() is imprecise for sub-millisecond durations due to OS timer granularity,
        # and sleeping for very short intervals can introduce unnecessary overhead. Most OSes cannot reliably
        # sleep for less than 1ms, so we avoid sleeping unless the required duration exceeds this threshold.
        if sleep_duration > 0.001:
            before_sleep: float = time.perf_counter()
            time.sleep(sleep_duration)
            after_sleep: float = time.perf_counter()
            actual_sleep: float = after_sleep - before_sleep

            if actual_sleep < sleep_duration - 0.001:  # 1ms tolerance
                # Log a warning but not too frequently
                if sleep_log_counter % 10 == 0:  # Log every 10th occurrence of sleep shortfall (not every 10 frames)
                    logger.warning(
                        f"Slept for {actual_sleep:.6f}s, which is less than scheduled {sleep_duration:.6f}s"
                    )
                sleep_log_counter += 1

        elif sleep_duration < -frame_interval:
            # We're more than one frame behind - reset schedule
            logger.warning(f"Simulation loop is severely behind schedule by {-sleep_duration:.4f}s - resetting")
            next_frame_time = time.perf_counter()
        # else: slightly behind but catchable, just don't sleep

    # Graceful shutdown
    logger.info(f"Simulation loop shutting down gracefully after {frame_count} frames")

def start_simulation_thread(
    bridge: GameBridge, logger_provider: LoggerProvider, target_fps: int = 60, shutdown_event: threading.Event | None = None
) -> threading.Thread:
    """Start the simulation in a background thread

    Args:
        bridge: GameBridge for thread-safe game updates
        logger_provider: Logger provider for logging
        target_fps: Target frames per second
        shutdown_event: Optional event to signal graceful shutdown. If provided, thread will not be daemon.

    Returns:
        Started thread instance
    """
    # If shutdown_event provided, make thread non-daemon so we can join it
    is_daemon = shutdown_event is None

    thread = threading.Thread(
        target=run_simulation_loop,
        args=(bridge, logger_provider, target_fps, shutdown_event),
        daemon=is_daemon,
        name="GameSimulation"
    )
    thread.start()

    # Wait for it to be ready
    if not bridge.game_thread_ready.wait(timeout=10.0):
        raise RuntimeError("Simulation thread failed to initialize")

    return thread
