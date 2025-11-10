"""
Thread-safe bridge between the GraphQL API and the game simulation.

Provides the GameBridge class for safe command queuing and state retrieval,
and exposes a singleton instance for use throughout the application.
"""

import logging
import queue
import threading
from queue import Queue
from time import time
from typing import Any, TypeVar

from mytower.game.controllers.controller_commands import (
    AddElevatorBankCommand, AddElevatorCommand, AddFloorCommand,
    AddPersonCommand, Command, CommandResult)
from mytower.game.controllers.game_controller import GameController
from mytower.game.core.types import FloorType
from mytower.game.core.units import Blocks
from mytower.game.models.model_snapshots import BuildingSnapshot

logger = logging.getLogger("mytower.api.game_bridge")


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

    # Command result TTL in seconds - results older than this are cleaned up
    COMMAND_RESULT_TTL_SECONDS: float = 60.0
    # How often to run cleanup (every N seconds)
    CLEANUP_INTERVAL_SECONDS: float = 10.0


    def __init__(self, controller: GameController, snapshot_fps: int = 20) -> None:

        self._controller: GameController = controller

        self._update_lock = threading.Lock()
        self._command_lock = threading.Lock()
        self._snapshot_lock = threading.Lock()

        self._game_thread_id: int | None = None

        self._command_queue: Queue[tuple[str, Command[Any]]] = Queue(maxsize=10)  # TODO: Make configurable someday
        # Store command results with timestamps: {command_id: (timestamp, result)}
        self._command_results: dict[str, tuple[float, CommandResult[Any]]] = {}
        self._last_cleanup_time: float = time()

        self._latest_snapshot: BuildingSnapshot | None = None
        self._snapshot_interval_s: float = 1.0 / snapshot_fps
        self._last_snapshot_time: float = 0.0

        # The update_game will clear (set) during startup
        self._game_thread_ready = threading.Event()

    @property
    def game_thread_ready(self) -> threading.Event:
        return self._game_thread_ready

    def _cleanup_old_command_results(self) -> None:
        """
        Remove command results older than COMMAND_RESULT_TTL_SECONDS.
        Must be called with _update_lock held.
        """
        current_time = time()
        cutoff_time = current_time - self.COMMAND_RESULT_TTL_SECONDS

        # Find expired command IDs
        expired_ids = [
            cmd_id for cmd_id, (timestamp, _) in self._command_results.items()
            if timestamp < cutoff_time
        ]

        # Remove expired results
        if expired_ids:
            for cmd_id in expired_ids:
                del self._command_results[cmd_id]
            logger.info(
                f"Cleaned up {len(expired_ids)} old command results "
                f"(total remaining: {len(self._command_results)})"
            )

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
            current_time = time()

            # Execute commands and store results with timestamps
            for cmd_id, command in commands_this_frame:
                result = self._controller.execute_command(command)
                self._command_results[cmd_id] = (current_time, result)

            self._controller.update(dt)

            # Periodic cleanup of old command results
            if current_time - self._last_cleanup_time >= self.CLEANUP_INTERVAL_SECONDS:
                self._cleanup_old_command_results()
                self._last_cleanup_time = current_time

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
    def queue_command(self, command: Command[Any]) -> str:
        command_id: str = f"cmd_{time()}"
        self._command_queue.put((command_id, command))
        return command_id

    def get_building_snapshot(self) -> BuildingSnapshot | None:
        with self._snapshot_lock:
            return self._latest_snapshot  # Returns cached snapshot

    def get_command_result_sync(self, command_id: str) -> CommandResult[Any] | None:
        with self._update_lock:
            result_tuple = self._command_results.get(command_id, None)
            if result_tuple is None:
                return None
            # Extract just the result from the (timestamp, result) tuple
            return result_tuple[1]

    def get_all_command_results_sync(self) -> dict[str, CommandResult[Any]]:
        with self._update_lock:
            # Extract just the results from the (timestamp, result) tuples
            return {cmd_id: result for cmd_id, (_, result) in self._command_results.items()}


    def execute_add_floor_sync(self, floor_type: FloorType) -> int:
        """Type-safe floor addition"""
        command = AddFloorCommand(floor_type)
        result: CommandResult[int] = self.execute_command_sync(command)

        if result.success and result.data is not None:
            return result.data  # Type checker knows this is int
        raise RuntimeError(f"Failed to add floor: {result.error}")


    def execute_add_person_sync(self, init_floor: int, init_horiz_position: Blocks, dest_floor: int, dest_horiz_position: Blocks) -> str:
        """Type-safe person addition"""
        command = AddPersonCommand(init_floor=init_floor, init_horiz_position=init_horiz_position, dest_floor=dest_floor, dest_horiz_position=dest_horiz_position)
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

def initialize_game_bridge(controller: GameController) -> GameBridge:
    global _bridge
    _bridge = GameBridge(controller)
    return _bridge

def get_game_bridge() -> GameBridge:
    if _bridge is None:
        raise RuntimeError("Game bridge not initialized")
    return _bridge
