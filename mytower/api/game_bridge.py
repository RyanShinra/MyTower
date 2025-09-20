from queue import Queue
import queue
import threading
from time import time
from typing import Any, Optional, Tuple
from mytower.game.controllers.controller_commands import Command
from mytower.game.controllers.game_controller import GameController
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
        self._controller: Optional[GameController]  = controller
        self._command_queue_lock = threading.Lock()
        self._command_queue: Queue[Tuple[str, Command[Any]]] = Queue()
        
        self._snapshot_lock = threading.Lock()
        self._latest_snapshot: Optional[BuildingSnapshot] = None
        self._snapshot_interval_s: float = 1.0 / snapshot_fps
        self._last_snapshot_time: float = 0.0
    
    def update_game(self, dt: float) -> None:
        """Update the game controller and process commands"""
        if not self._controller:
            return
        while not self._command_queue.empty():
            try:
                _cmd_id, command = self._command_queue.get_nowait()
                self._controller.execute_command(command)
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
     
    def queue_command(self, command: Command[Any]) -> str:
        command_id: str = f"cmd_{time()}"
        self._command_queue.put((command_id, command))
        return command_id
    
    def get_building_state(self) -> Optional[BuildingSnapshot]:
        with self._snapshot_lock:
            return self._latest_snapshot  # Returns cached snapshot
            
    def get_game_time(self) -> float:
        # Fast, lock-free read from snapshot
        snapshot: BuildingSnapshot | None = self.get_building_state()
        return snapshot.time if snapshot else 0.0

# Module-level singleton
_bridge: Optional[GameBridge] = None

def initialize_game_bridge(controller: GameController) -> None:
    global _bridge
    _bridge = GameBridge(controller)

def get_game_bridge() -> GameBridge:
    if _bridge is None:
        raise RuntimeError("Game bridge not initialized")
    return _bridge


