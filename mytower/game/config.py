# game/config.py
from __future__ import annotations
from typing import TYPE_CHECKING, Final
from dataclasses import dataclass

if TYPE_CHECKING:
    from game.elevator import ElevatorConfigProtocol
    from game.person import PersonConfigProtocol

@dataclass
class ElevatorConfig:
    """Concrete implementation of Elevator configuration"""
    max_speed: Final[float] = 0.75  # Floors per second
    max_capacity: Final[int] = 15  # Number of people who can fit on board
    passenger_loading_time: Final[float] = 1.0  # seconds before getting very angry
    idle_wait_timeout: Final[float] = 0.5  # Seconds: how often an idle elevator checks for passengers
    idle_log_timeout: Final[float] = 0.5  # Seconds: how often to log status while Idle
    moving_log_timeout: Final[float] = 0.5  # Seconds: how often to log status while Moving

@dataclass
class PersonConfig:
    """Concrete implementation of Person configuration"""
    max_speed: Final[float] = 0.5  # blocks per second
    max_wait_time: Final[float] = 90.0  # seconds before getting very angry
    idle_timeout: Final[float] = 5.0  # In person.py update_idle method
    radius: Final[int] = 5  # Visual size of person

class GameConfig:
    def __init__(self) -> None:
        self.elevator: ElevatorConfigProtocol = ElevatorConfig()
        self.person: PersonConfigProtocol = PersonConfig()
        # etc.