# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

"""
Thread-safe bridge between the GraphQL API and the game simulation.

Provides the GameBridge class for safe command queuing and state retrieval,
and exposes a singleton instance for use throughout the application.
"""

import os
import queue
import threading
from collections import deque
from queue import Queue
from time import time
from typing import Any, TypeVar

from mytower.game.controllers.controller_commands import (
    AddElevatorBankCommand,
    AddElevatorCommand,
    AddFloorCommand,
    AddPersonCommand,
    Command,
    CommandResult,
)
from mytower.game.controllers.game_controller import GameController
from mytower.game.core.types import FloorType
from mytower.game.core.units import Blocks
from mytower.game.models.model_snapshots import BuildingSnapshot
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger


class GameBridge:
    """
    Thread-safe bridge between GraphQL API and game simulation.

    IMPORTANT: In threaded mode, this is the ONLY safe way to interact
    with the game controller. Direct controller access will cause:
    - Race conditions between HTTP and game threads
    - Lost mutations (commands not processed in frame order)
    - Inconsistent snapshots for GraphQL queries

    Usage:
        bridge = GameBridge(controller)

        # Game thread:
        bridge.update_game(dt)

        # HTTP threads:
        bridge.queue_command(cmd)
        bridge.get_building_state()
    """

    # Max command results to keep in memory (~1MB, fits in L3 cache)
    # Supports potential undo/replay features while preventing unbounded growth
    MAX_COMMAND_RESULTS = 4000

    # Default queue size - can be overridden via environment variable or constructor
    DEFAULT_COMMAND_QUEUE_SIZE = 100

    def __init__(
        self,
        controller: GameController,
        snapshot_fps: int = 20,
        command_queue_size: int | None = None,
        logger_provider: LoggerProvider | None = None,
    ) -> None:
        self._controller: GameController = controller

        self._update_lock = threading.Lock()
        self._command_lock = threading.Lock()
        self._snapshot_lock = threading.Lock()
        self._metrics_lock = threading.Lock()  # Protects queue metrics

        self._game_thread_id: int | None = None

        # Command queue size: Priority order: constructor arg > env var > default
        # Validate and parse queue size
        if command_queue_size is not None:
            if command_queue_size <= 0:
                raise ValueError(f"command_queue_size must be positive, got {command_queue_size}")
            self._queue_size = command_queue_size
        else:
            env_queue_size = os.getenv("MYTOWER_COMMAND_QUEUE_SIZE")
            if env_queue_size:
                try:
                    parsed_size = int(env_queue_size)
                    if parsed_size <= 0:
                        raise ValueError(f"MYTOWER_COMMAND_QUEUE_SIZE must be positive, got {parsed_size}")
                    self._queue_size = parsed_size
                except ValueError as e:
                    raise ValueError(f"Invalid MYTOWER_COMMAND_QUEUE_SIZE: {e}") from e
            else:
                self._queue_size = self.DEFAULT_COMMAND_QUEUE_SIZE

        self._command_queue: Queue[tuple[str, Command[Any]]] = Queue(maxsize=self._queue_size)

        # Command result cache with fixed-size eviction (prevents unbounded memory growth)
        self._command_results: dict[str, CommandResult[Any]] = {}
        self._command_ids: deque[str] = deque(maxlen=self.MAX_COMMAND_RESULTS)  # Tracks insertion order

        self._latest_snapshot: BuildingSnapshot | None = None
        self._snapshot_interval_s: float = 1.0 / snapshot_fps
        self._last_snapshot_time: float = 0.0

        # The update_game will clear (set) during startup
        self._game_thread_ready = threading.Event()

        # Initialize logger
        self._logger: MyTowerLogger | None
        if logger_provider:
            self._logger = logger_provider.get_logger("GameBridge")
        else:
            self._logger = None

        # Queue metrics (protected by _metrics_lock)
        self._queue_full_count = 0
        self._total_commands_queued = 0
        self._max_queue_size_seen = 0

        if self._logger:
            self._logger.info(f"GameBridge initialized with command queue size: {self._queue_size}")

    @property
    def game_thread_ready(self) -> threading.Event:
        return self._game_thread_ready


    def update_game(self, dt: float) -> None:
        """Update the game controller and process commands"""
        current_thread: int = threading.get_ident()

        if self._game_thread_id is None:
            self._game_thread_id = current_thread
            self._game_thread_ready.set()  # 🚦 Signal that game thread is ready
        elif self._game_thread_id != current_thread:
            raise RuntimeError("update_game() called from wrong thread!")

        commands_this_frame: list[tuple[str, Command[Any]]] = []
        with self._command_lock:
            while not self._command_queue.empty():
                try:
                    commands_this_frame.append(self._command_queue.get_nowait())
                except queue.Empty:
                    break
        # End of with self._command_lock, releases self._command_lock

        with self._update_lock:
            for cmd_id, command in commands_this_frame:
                result = self._controller.execute_command(command)

                # If deque is at capacity, remove the oldest result before adding new one
                if len(self._command_ids) == self.MAX_COMMAND_RESULTS:
                    oldest_id = self._command_ids[0]  # Peek at oldest (will be evicted on append)
                    self._command_results.pop(oldest_id, None)

                # Add new result and track its ID (deque auto-evicts oldest if at maxlen)
                self._command_ids.append(cmd_id)
                self._command_results[cmd_id] = result

            self._controller.update(dt)

            new_snapshot: BuildingSnapshot = self._controller.get_building_state()
        # End of with self._update_lock, releases self._update_lock

        with self._snapshot_lock:
            self._latest_snapshot = new_snapshot

    # End of update_game()

    T = TypeVar("T")

    def execute_command_sync(self, command: Command[T]) -> CommandResult[T]:
        with self._update_lock:
            # Execute immediately, blocking updates
            return self._controller.execute_command(command)

    # TODO: Change the command_id to a sequential integer for easier tracking
    def queue_command(self, command: Command[Any], timeout: float | None = None) -> str:
        """
        Queue a command for execution on the game thread.

        Args:
            command: The command to execute
            timeout: Optional timeout in seconds. If None, blocks indefinitely.
                    Set to 0 for non-blocking (raises queue.Full if queue is full)

        Returns:
            Command ID for tracking the result

        Raises:
            queue.Full: If timeout is 0 and queue is full
        """
        command_id: str = f"cmd_{time()}"

        # Sample queue size for monitoring (best-effort, may be stale in multi-threaded context)
        current_queue_size = self._command_queue.qsize()

        # Track peak queue size with thread-safe update
        with self._metrics_lock:
            if current_queue_size > self._max_queue_size_seen:
                self._max_queue_size_seen = current_queue_size

        # Log if queue is getting full (>75% capacity)
        if self._logger and current_queue_size > (self._queue_size * 0.75):
            self._logger.warning(
                f"Command queue is {(current_queue_size / self._queue_size) * 100:.1f}% full "
                f"({current_queue_size}/{self._queue_size}). "
                f"Consider increasing MYTOWER_COMMAND_QUEUE_SIZE if this happens frequently."
            )

        try:
            # Queue the command with appropriate blocking behavior
            if timeout is None:
                # Block indefinitely (default behavior)
                self._command_queue.put((command_id, command))
            elif timeout == 0:
                # Non-blocking: use block=False instead of timeout=False (correct API usage)
                self._command_queue.put((command_id, command), block=False)
            else:
                # Block with timeout
                self._command_queue.put((command_id, command), timeout=timeout)

            # Only increment after successful queue insertion (thread-safe)
            with self._metrics_lock:
                self._total_commands_queued += 1

        except queue.Full:
            # Track queue full events (thread-safe)
            with self._metrics_lock:
                self._queue_full_count += 1
                full_count = self._queue_full_count

            if self._logger:
                self._logger.error(
                    f"Command queue is FULL ({self._queue_size} commands). "
                    f"Command rejected. Queue has been full {full_count} times. "
                    f"Increase MYTOWER_COMMAND_QUEUE_SIZE environment variable."
                )
            raise

        return command_id

    def get_building_snapshot(self) -> BuildingSnapshot | None:
        with self._snapshot_lock:
            return self._latest_snapshot  # Returns cached snapshot

    def get_command_result_sync(self, command_id: str) -> CommandResult[Any] | None:
        with self._update_lock:
            return self._command_results.get(command_id, None)

    def get_all_command_results_sync(self) -> dict[str, CommandResult[Any]]:
        with self._update_lock:
            return dict(self._command_results)  # Return a copy

    def get_queue_metrics(self) -> dict[str, int | float]:
        """
        Get command queue metrics for monitoring and debugging.

        Returns:
            Dictionary with queue metrics:
            - current_size: Current number of commands in queue
            - max_size: Maximum queue capacity
            - utilization: Current queue utilization as percentage (0-100)
            - total_queued: Total commands queued since startup
            - max_seen: Maximum queue size seen since startup
            - full_count: Number of times queue was completely full
        """
        current_size = self._command_queue.qsize()
        with self._metrics_lock:
            return {
                "current_size": current_size,
                "max_size": self._queue_size,
                "utilization": (current_size / self._queue_size * 100) if self._queue_size > 0 else 0,
                "total_queued": self._total_commands_queued,
                "max_seen": self._max_queue_size_seen,
                "full_count": self._queue_full_count,
            }


    def execute_add_floor_sync(self, floor_type: FloorType) -> int:
        """Type-safe floor addition"""
        command = AddFloorCommand(floor_type)
        result: CommandResult[int] = self.execute_command_sync(command)

        if result.success and result.data is not None:
            return result.data  # Type checker knows this is int
        raise RuntimeError(f"Failed to add floor: {result.error}")


    def execute_add_person_sync(
        self, init_floor: int, init_horiz_position: Blocks, dest_floor: int, dest_horiz_position: Blocks
    ) -> str:
        """Type-safe person addition"""
        command = AddPersonCommand(
            init_floor=init_floor,
            init_horiz_position=init_horiz_position,
            dest_floor=dest_floor,
            dest_horiz_position=dest_horiz_position,
        )
        result: CommandResult[str] = self.execute_command_sync(command)

        if result.success and result.data is not None:
            return result.data  # Type checker knows this is str
        raise RuntimeError(f"Failed to add person: {result.error}")


    def execute_add_elevator_bank_sync(self, horiz_position: Blocks, min_floor: int, max_floor: int) -> str:
        """Type-safe elevator bank addition"""
        command = AddElevatorBankCommand(horiz_position=horiz_position, min_floor=min_floor, max_floor=max_floor)
        result: CommandResult[str] = self.execute_command_sync(command)

        if result.success and result.data is not None:
            return result.data  # Type checker knows this is str
        raise RuntimeError(f"Failed to add elevator bank: {result.error}")


    def execute_add_elevator_sync(self, elevator_bank_id: str) -> str:
        """Type-safe elevator addition"""
        command = AddElevatorCommand(elevator_bank_id=elevator_bank_id)
        result: CommandResult[str] = self.execute_command_sync(command)

        if result.success and result.data is not None:
            return result.data  # Type checker knows this is str
        raise RuntimeError(f"Failed to add elevator: {result.error}")

# Module-level singleton
_bridge: GameBridge | None = None


def initialize_game_bridge(
    controller: GameController,
    command_queue_size: int | None = None,
    logger_provider: LoggerProvider | None = None,
) -> GameBridge:
    """
    Initialize the global GameBridge singleton.

    Args:
        controller: GameController instance to wrap
        command_queue_size: Optional queue size override (default: 100 or MYTOWER_COMMAND_QUEUE_SIZE env var)
        logger_provider: Optional logger provider for metrics and debugging

    Returns:
        Initialized GameBridge instance
    """
    global _bridge
    _bridge = GameBridge(
        controller=controller, command_queue_size=command_queue_size, logger_provider=logger_provider
    )
    return _bridge


def get_game_bridge() -> GameBridge:
    if _bridge is None:
        raise RuntimeError("Game bridge not initialized")
    return _bridge
