"""
Model layer: Pure business logic and data management
No pygame dependencies, no rendering logic
"""
from __future__ import annotations
# from typing import List, Dict, Optional
from typing import List, Optional
from dataclasses import dataclass

from mytower.game.logger import LoggerProvider, MyTowerLogger
from mytower.game.types import FloorType, PersonState, ElevatorState, VerticalDirection


@dataclass
class PersonSnapshot:
    """Immutable snapshot of person state for API consumption"""
    id: str
    current_floor: int
    current_block: float
    destination_floor: int
    destination_block: int
    state: PersonState
    waiting_time: float


@dataclass
class ElevatorSnapshot:
    """Immutable snapshot of elevator state for API consumption"""
    id: str
    current_floor: float
    destination_floor: int
    state: ElevatorState
    nominal_direction: VerticalDirection
    door_open: bool
    passenger_count: int
    available_capacity: int


@dataclass
class FloorSnapshot:
    """Immutable snapshot of floor state for API consumption"""
    floor_number: int
    floor_type: FloorType
    person_count: int


@dataclass
class BuildingSnapshot:
    """Complete building state snapshot for API consumption"""
    time: float
    money: int
    floors: List[FloorSnapshot]
    elevators: List[ElevatorSnapshot]
    people: List[PersonSnapshot]


class GameModel:
    """
    Pure business logic layer - manages game state
    Provides clean interfaces for external consumption
    """
    def __init__(self, logger_provider: LoggerProvider) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger('GameModel')
        
        # These imports will come from your existing classes
        # from game.building import Building
        # from game.config import GameConfig
        
        # self._building = Building(logger_provider, width=20)
        # self._config = GameConfig()
        
        # For now, placeholder attributes
        self._time = 0.0
        self._speed = 1.0
        self._paused = False
        self._building = None  # Will be Building instance
        self._config = None     # Will be GameConfig instance
        
        # TODO: Move initialization logic from GameState here
        # self._initialize_building()
    
    @property
    def logger(self) -> MyTowerLogger:
        return self._logger
    
    @property
    def is_paused(self) -> bool:
        return self._paused
    
    @property
    def current_time(self) -> float:
        return self._time
    
    # Query Methods (for GraphQL queries)
    def get_building_snapshot(self) -> BuildingSnapshot:
        """Get complete building state as immutable snapshot"""
        # TODO: Implement snapshot creation from self._building
        return BuildingSnapshot(
            time=self._time,
            money=0,  # self._building.money,
            floors=[],  # self._get_floor_snapshots(),
            elevators=[],  # self._get_elevator_snapshots(),
            people=[]   # self._get_person_snapshots()
        )
    
    def get_person_by_id(self, person_id: str) -> Optional[PersonSnapshot]:
        """Get specific person state by ID"""
        # TODO: Implement person lookup and snapshot creation
        return None
    
    def get_elevator_by_id(self, elevator_id: str) -> Optional[ElevatorSnapshot]:
        """Get specific elevator state by ID"""
        # TODO: Implement elevator lookup and snapshot creation
        return None
    
    def get_floor_info(self, floor_number: int) -> Optional[FloorSnapshot]:
        """Get specific floor information"""
        # TODO: Implement floor lookup and snapshot creation
        return None
    
    # Command Methods (for GraphQL mutations)
    def add_floor(self, floor_type: FloorType) -> bool:
        """Add a new floor to the building"""
        try:
            # TODO: self._building.add_floor(floor_type)
            return True
        except Exception as e:
            self._logger.error(f"Failed to add floor: {e}")
            return False
    
    def add_person(self, floor: int, block: float, dest_floor: int, dest_block: int) -> Optional[str]:
        """Add a new person to the building, returns person ID if successful"""
        try:
            # TODO: Create person and add to building
            # TODO: Generate and return unique person ID
            return f"person_placeholder"
        except Exception as e:
            self._logger.error(f"Failed to add person: {e}")
            return None
    
    def set_game_speed(self, speed: float) -> bool:
        """Set game simulation speed"""
        if 0.0 <= speed <= 10.0:  # Reasonable bounds
            self._speed = speed
            return True
        return False
    
    def set_pause_state(self, paused: bool) -> bool:
        """Set game pause state"""
        self._paused = paused
        return True
    
    def toggle_pause(self) -> bool:
        """Toggle game pause state, returns new state"""
        self._paused = not self._paused
        return self._paused
    
    # Simulation Methods
    def update(self, dt: float) -> None:
        """Update game simulation"""
        if not self._paused:
            game_dt = dt * self._speed
            self._time += game_dt
            # TODO: self._building.update(game_dt)
