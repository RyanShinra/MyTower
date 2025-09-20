# In mytower/api/game_bridge.py
from queue import Queue
import queue
import threading
from time import time
from typing import Any, Dict, Optional, Tuple, TypeVar
from mytower.game.controllers.controller_commands import AddElevatorBankCommand, AddElevatorCommand, AddFloorCommand, AddPersonCommand, Command, CommandResult
from mytower.game.controllers.game_controller import GameController
from mytower.game.core.types import FloorType
from mytower.game.models.model_snapshots import BuildingSnapshot



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

    def __init__(self, controller: GameController, snapshot_fps: int = 20) -> None:
        self._controller: GameController = controller
        self._update_lock = threading.RLock()
        self._command_queue: Queue[Tuple[str, Command[Any]]] = Queue()
        
        self._snapshot_lock = threading.Lock()
        self._latest_snapshot: Optional[BuildingSnapshot] = None
        self._snapshot_interval_s: float = 1.0 / snapshot_fps
        self._last_snapshot_time: float = 0.0
        self._command_results: Dict[str, CommandResult[Any]] = {}
    
    def update_game(self, dt: float) -> None:
        """Update the game controller and process commands"""
        with self._update_lock:
            while not self._command_queue.empty():
                try:
                    _cmd_id, command = self._command_queue.get_nowait()
                    self._command_results[_cmd_id] = self._controller.execute_command(command)
                except queue.Empty:
                    break
            
            self._controller.update(dt)
            
            # Create snapshot if interval elapsed
            now: float = time()
            if now - self._last_snapshot_time > self._snapshot_interval_s:
                new_snapshot: BuildingSnapshot = self._controller.get_building_state()
                with self._snapshot_lock:
                    self._latest_snapshot = new_snapshot
                    self._last_snapshot_time = now
    
    T = TypeVar('T')
    def execute_command_sync(self, command: Command[T]) -> CommandResult[T]:
        with self._update_lock:
            # Execute immediately, blocking updates
            return self._controller.execute_command(command)
     
    def queue_command(self, command: Command[Any]) -> str:
        command_id: str = f"cmd_{time()}"
        self._command_queue.put((command_id, command))
        return command_id
    
    def get_building_state(self) -> Optional[BuildingSnapshot]:
        with self._snapshot_lock:
            return self._latest_snapshot  # Returns cached snapshot
        
    def get_command_result(self, command_id: str) -> Optional[CommandResult[Any]]:
        return self._command_results.get(command_id, None)
    
    def get_all_command_results(self) -> Dict[str, CommandResult[Any]]:
        return dict(self._command_results)  # Return a copy


    def execute_add_floor_sync(self, floor_type: FloorType) -> int:
        """Type-safe floor addition"""
        command = AddFloorCommand(floor_type)
        result: CommandResult[int] = self.execute_command_sync(command)
        
        if result.success and result.data is not None:
            return result.data  # Type checker knows this is int
        raise RuntimeError(f"Failed to add floor: {result.error}")

        
    def execute_add_person_sync(self, floor: int, block: float, dest_floor: int, dest_block: int) -> str:
        """Type-safe person addition"""
        command = AddPersonCommand(floor=floor, block=block, dest_floor=dest_floor, dest_block=dest_block)
        result: CommandResult[str] = self.execute_command_sync(command)
        
        if result.success and result.data is not None:
            return result.data  # Type checker knows this is str
        raise RuntimeError(f"Failed to add person: {result.error}")


    def execute_add_elevator_bank_sync(self, h_cell: int, min_floor: int, max_floor: int) -> str:
        """Type-safe elevator bank addition"""
        command = AddElevatorBankCommand(h_cell=h_cell, min_floor=min_floor, max_floor=max_floor)
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
_bridge: Optional[GameBridge] = None

def initialize_game_bridge(controller: GameController) -> None:
    global _bridge
    _bridge = GameBridge(controller)

def get_game_bridge() -> GameBridge:
    if _bridge is None:
        raise RuntimeError("Game bridge not initialized")
    return _bridge


