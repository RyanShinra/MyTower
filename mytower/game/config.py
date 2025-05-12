# game/config.py
from __future__ import annotations
from typing import TYPE_CHECKING, Final
from dataclasses import dataclass

from mytower.game.types import RGB
from mytower.game.ui import UIConfigProtocol

if TYPE_CHECKING:
    from game.elevator import ElevatorConfigProtocol, ElevatorCosmeticsProtocol
    from game.person import PersonConfigProtocol, PersonCosmeticsProtocol

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
class ElevatorCosmetics:
    """Implements Elevator Cosmetics Protocol"""
    shaft_color: Final[RGB] = (100, 100, 100)
    shaft_overhead: Final[RGB] = (24, 24, 24)
    closed_color: Final[RGB] = (50, 50, 200)
    open_color: Final[RGB] = (200, 200, 50)

@dataclass
class PersonConfig:
    """Concrete implementation of Person configuration"""
    max_speed: Final[float] = 0.5  # blocks per second
    max_wait_time: Final[float] = 90.0  # seconds before getting very angry
    idle_timeout: Final[float] = 5.0  # In person.py update_idle method
    radius: Final[int] = 5  # Visual size of person

@dataclass
class PersonCosmetics:
    """Implements Person Cosmetics Proto."""
    angry_max_red: Final[int] = 192
    angry_min_green: Final[int] = 0
    angry_min_blue: Final[int] = 0
    initial_max_red: Final[int] = 32
    initial_max_green: Final[int] = 128
    initial_max_blue: Final[int] = 128
    initial_min_red: Final[int] = 0
    initial_min_green: Final[int] = 0
    initial_min_blue: Final[int] = 0
    
@dataclass
class UIConfig:
    """Default UI configuration implementation"""
    background_color: Final[RGB] = (220, 220, 220)
    border_color: Final[RGB] = (150, 150, 150)
    text_color: Final[RGB] = (0, 0, 0)
    button_color: Final[RGB] = (200, 200, 200)
    button_hover_color: Final[RGB] = (180, 180, 180)

class GameConfig:
    def __init__(self) -> None:
        self.elevator: ElevatorConfigProtocol = ElevatorConfig()
        self.person: PersonConfigProtocol = PersonConfig()
        self.person_cosmetics: PersonCosmeticsProtocol = PersonCosmetics()
        self.elevator_cosmetics: ElevatorCosmeticsProtocol = ElevatorCosmetics()
        self.ui_config: UIConfigProtocol = UIConfig()
        # etc.