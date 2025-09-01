"""
Model layer: Pure business logic and data management
No pygame dependencies, no rendering logic
"""
from __future__ import annotations
# from typing import List, Dict, Optional
from typing import List, Optional


from mytower.game.elevator import Elevator
from mytower.game.logger import LoggerProvider, MyTowerLogger
# from mytower.game.types import FloorType, PersonState, ElevatorState, VerticalDirection
from mytower.game.models.model_snapshots import BuildingSnapshot, ElevatorSnapshot, FloorSnapshot, PersonSnapshot
from mytower.game.models.snapshot_builders import build_elevator_snapshot, build_floor_snapshot, build_person_snapshot
from mytower.game.person import Person, PersonProtocol
from mytower.game.types import FloorType
from mytower.game.building import Building
from mytower.game.config import GameConfig


class GameModel:
    """
    Pure business logic layer - manages game state
    Provides clean interfaces for external consumption
    """
    def __init__(self, logger_provider: LoggerProvider) -> None:
        self._logger_provider: LoggerProvider =logger_provider
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

    
    def add_person(self, floor: int, block: float, dest_floor: int, dest_block: int) -> str:
        """Add a new person to the building, returns person ID if successful"""
        try:
            new_person: Person = Person(
                logger_provider=self._logger_provider,
                building=self._building,
                current_floor=floor,
                current_block=block,
                config=self._config
            )
            
            new_person.set_destination(dest_floor=dest_floor, dest_block=dest_block)
            self._building.add_person(new_person)
            return new_person.person_id

        except Exception as e:
            self._logger.exception(f"Failed to add person: {e}")
            raise RuntimeError(f"Failed to add person at floor {floor}, block {block}: {str(e)}") from e
    
    def set_game_speed(self, speed: float) -> bool:
        """Set game simulation speed"""
        try:
            if 0.0 <= speed <= 10.0:  # Reasonable bounds
                self._speed = speed
                return True

            self._logger.warning(f"Attempted to set invalid game speed: {speed}")
            return False
        except Exception as e:
            self._logger.exception(f"Failed to set game speed to {speed}: {e}")
            raise RuntimeError(f"Failed to set game speed to {speed}: {str(e)}") from e
    
    def set_pause_state(self, paused: bool) -> None:
        """Set game pause state"""
        try:
            self._paused = paused
            self._logger.info(f"Set pause state to {paused}")

        except Exception as e:
            self._logger.exception(f"Failed to set pause state to {paused}: {e}")
            raise RuntimeError(f"Failed to set pause state to {paused}: {str(e)}") from e
    
    def toggle_pause(self) -> bool:
        """Toggle game pause state, returns new state"""
        try:
            self.set_pause_state(not self._paused)
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
                floors=self._get_floor_snapshots(),
                elevators=self._get_elevator_snapshots(),
                people=[]   # self._get_person_snapshots()
            )
        except Exception as e:
            self._logger.exception(f"Failed to get building snapshot: {e}")
            raise RuntimeError(f"Failed to get building snapshot: {str(e)}") from e
    
    def _get_floor_snapshots(self) -> list[FloorSnapshot]:
        """Helper to get snapshots of all floors"""
        try:
            return [
                build_floor_snapshot(floor) for floor in self._building.get_floors()
            ]
            
        except Exception as e:
            self._logger.exception(f"Failed to get floor snapshots: {e}")
            raise RuntimeError(f"Failed to get floor snapshots: {str(e)}") from e

    
    def _get_elevator_snapshots(self) -> list[ElevatorSnapshot]:
        """Helper to get snapshots of all elevators"""
        try:
            return [
                build_elevator_snapshot(elevator) for elevator in self._building.get_elevators()
            ]

        except Exception as e:
            self._logger.exception(f"Failed to get elevator snapshots: {e}")
            raise RuntimeError(f"Failed to get elevator snapshots: {str(e)}") from e

    
    def _get_person_snapshots(self) -> list[PersonSnapshot]:
        """Helper to get snapshots of all people"""
        try:
            return [
                build_person_snapshot(person) for person in self._building.people
            ]

        except Exception as e:
            self._logger.exception(f"Failed to get person snapshots: {e}")
            raise RuntimeError(f"Failed to get person snapshots: {str(e)}") from e

    
    def get_person_by_id(self, person_id: str) -> Optional[PersonSnapshot]:
        """Get specific person state by ID"""
        try:
            person: PersonProtocol | None = self._building.get_person_by_id(person_id)
            if person:
                return build_person_snapshot(person)
            
            return None
        
        except Exception as e:
            self._logger.exception(f"Failed to get person by id {person_id}: {e}")
            raise RuntimeError(f"Failed to get person by id {person_id}: {str(e)}") from e

    
    def get_elevator_by_id(self, elevator_id: str) -> Optional[ElevatorSnapshot]:
        """Get specific elevator state by ID"""
        try:
            elevators: List[Elevator] = self._building.get_elevators()
            for elevator in elevators:
                if elevator.elevator_id == elevator_id:
                    return build_elevator_snapshot(elevator)
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
