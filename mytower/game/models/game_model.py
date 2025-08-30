"""
Model layer: Pure business logic and data management
No pygame dependencies, no rendering logic
"""
from __future__ import annotations
# from typing import List, Dict, Optional
from typing import Optional


from mytower.game.floor import Floor
from mytower.game.logger import LoggerProvider, MyTowerLogger
# from mytower.game.types import FloorType, PersonState, ElevatorState, VerticalDirection
from mytower.game.models.model_snapshots import BuildingSnapshot, ElevatorSnapshot, FloorSnapshot, PersonSnapshot
from mytower.game.types import FloorType
from mytower.game.building import Building
from mytower.game.config import GameConfig


class GameModel:
    """
    Pure business logic layer - manages game state
    Provides clean interfaces for external consumption
    """
    def __init__(self, logger_provider: LoggerProvider) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger('GameModel')
        
        
        self._building = Building(logger_provider, width=20)
        self._config = GameConfig()
        
        # For now, placeholder attributes
        self._time: float = 0.0
        self._speed: float = 1.0
        self._paused: bool = False
        
        # TODO: Move initialization logic from GameState here
        # self._initialize_building()
    
    # @property
    # def logger(self) -> MyTowerLogger:
    #     return self._logger
    
    @property
    def is_paused(self) -> bool:
        return self._paused
    
    @property
    def current_time(self) -> float:
        return self._time
    
    # Command Methods (for GraphQL mutations)
    def add_floor(self, floor_type: FloorType) -> int:
        """Add a new floor to the building"""
        try:
            new_floor_num: int = self._building.add_floor(floor_type)
            return new_floor_num
        except Exception as e:
            self._logger.exception(f"Failed to add floor of type {floor_type}: {e}")
            raise RuntimeError(f"Failed to add floor of type {floor_type.name}: {str(e)}") from e
    
    def add_person(self, floor: int, block: float, dest_floor: int, dest_block: int) -> Optional[str]:
        """Add a new person to the building, returns person ID if successful"""
        try:
            # TODO: Create person and add to building
            # TODO: Generate and return unique person ID
            return f"person_placeholder"
        except Exception as e:
            self._logger.exception(f"Failed to add person: {e}")
            raise RuntimeError(f"Failed to add person at floor {floor}, block {block}: {str(e)}") from e
    
    def set_game_speed(self, speed: float) -> bool:
        """Set game simulation speed"""
        try:
            if 0.0 <= speed <= 10.0:  # Reasonable bounds
                self._speed = speed
                return True
            return False
        except Exception as e:
            self._logger.exception(f"Failed to set game speed to {speed}: {e}")
            raise RuntimeError(f"Failed to set game speed to {speed}: {str(e)}") from e
    
    def set_pause_state(self, paused: bool) -> bool:
        """Set game pause state"""
        try:
            self._paused = paused
            return True
        except Exception as e:
            self._logger.exception(f"Failed to set pause state to {paused}: {e}")
            raise RuntimeError(f"Failed to set pause state to {paused}: {str(e)}") from e
    
    def toggle_pause(self) -> bool:
        """Toggle game pause state, returns new state"""
        try:
            self._paused = not self._paused
            return self._paused
        except Exception as e:
            self._logger.exception(f"Failed to toggle pause state: {e}")
            raise RuntimeError(f"Failed to toggle pause state: {str(e)}") from e
    
    # Simulation Methods
    def update(self, dt: float) -> None:
        """Update game simulation"""
        try:
            if not self._paused:
                game_dt: float = dt * self._speed
                self._time += game_dt
                # TODO: self._building.update(game_dt)
        except Exception as e:
            self._logger.exception(f"Failed to update game simulation with dt={dt}: {e}")
            raise RuntimeError(f"Failed to update game simulation: {str(e)}") from e
    
    def get_building_snapshot(self) -> BuildingSnapshot:
        """Get complete building state as immutable snapshot"""
        try:
            # TODO: Implement snapshot creation from self._building
            return BuildingSnapshot(
                time=self._time,
                money=0,  # self._building.money,
                floors=[],  # self._get_floor_snapshots(),
                elevators=[],  # self._get_elevator_snapshots(),
                people=[]   # self._get_person_snapshots()
            )
        except Exception as e:
            self._logger.exception(f"Failed to get building snapshot: {e}")
            raise RuntimeError(f"Failed to get building snapshot: {str(e)}") from e
    
    def get_person_by_id(self, person_id: str) -> Optional[PersonSnapshot]:
        """Get specific person state by ID"""
        try:
            # TODO: Implement person lookup and snapshot creation
            return None
        except Exception as e:
            self._logger.exception(f"Failed to get person by id {person_id}: {e}")
            raise RuntimeError(f"Failed to get person by id {person_id}: {str(e)}") from e
    
    def get_elevator_by_id(self, elevator_id: str) -> Optional[ElevatorSnapshot]:
        """Get specific elevator state by ID"""
        try:
            # TODO: Implement elevator lookup and snapshot creation
            return None
        except Exception as e:
            self._logger.exception(f"Failed to get elevator by id {elevator_id}: {e}")
            raise RuntimeError(f"Failed to get elevator by id {elevator_id}: {str(e)}") from e
    
    def get_floor_info(self, floor_number: int) -> Optional[FloorSnapshot]:
        """Get specific floor information"""
        try:
            # TODO: Implement floor lookup and snapshot creation
            return None
        except Exception as e:
            self._logger.exception(f"Failed to get floor info for floor {floor_number}: {e}")
            raise RuntimeError(f"Failed to get floor info for floor {floor_number}: {str(e)}") from e
