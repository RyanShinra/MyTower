# game/config.py
from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from game.elevator import ElevatorConfigProtocol
    from game.person import PersonConfigProtocol

@dataclass
class ElevatorConfig:
    """Concrete implementation of Elevator configuration"""
    max_speed: float = 0.75
    max_capacity: int = 15
    passenger_loading_time: float = 1.0
    idle_log_timeout: float = 0.5
    moving_log_timeout: float = 0.5

@dataclass
class PersonConfig:
    """Concrete implementation of Person configuration"""
    max_speed: float = 0.5
    max_wait_time: float = 90.0
    idle_timeout: float = 5.0
    radius: int = 5

class GameConfig:
    def __init__(self):
        self.elevator: ElevatorConfigProtocol = ElevatorConfig()
        self.person: PersonConfigProtocol = PersonConfig()
        # etc.