# game/config.py
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from mytower.game.core.units import Blocks, Meters

if TYPE_CHECKING:
    from mytower.game.core.types import RGB
    from mytower.game.entities.elevator import ElevatorConfigProtocol, ElevatorCosmeticsProtocol
    from mytower.game.views.desktop_ui import UIConfigProtocol
    from mytower.game.entities.person import PersonConfigProtocol, PersonCosmeticsProtocol

# It can't seem to make up its mind whether to use snake_case because they are class properties or UPPER_CASE for constants
# So, it gets neither
# pylint: disable=invalid-name 
@dataclass
class ElevatorConfig:
    """Concrete implementation of Elevator configuration"""
    MAX_SPEED: Final[float] = 0.75  # Floors per second
    MAX_CAPACITY: Final[int] = 15  # Number of people who can fit on board
    PASSENGER_LOADING_TIME: Final[float] = 1.0  # How long it takes a single passenger to board
    IDLE_WAIT_TIMEOUT: Final[float] = 0.5  # Seconds: how often an idle elevator checks for passengers
    IDLE_LOG_TIMEOUT: Final[float] = 0.5  # Seconds: how often to log status while Idle
    MOVING_LOG_TIMEOUT: Final[float] = 0.5  # Seconds: how often to log status while Moving


@dataclass
class ElevatorCosmetics:
    """Implements Elevator Cosmetics Protocol"""

    SHAFT_COLOR: Final[RGB] = (100, 100, 100)
    SHAFT_OVERHEAD_COLOR: Final[RGB] = (24, 24, 24)
    CLOSED_COLOR: Final[RGB] = (50, 50, 200)
    OPEN_COLOR: Final[RGB] = (200, 200, 50)
    SHAFT_OVERHEAD_HEIGHT: Final[Meters] = Blocks(1.0).in_meters
    ELEVATOR_WIDTH: Final[Meters] = Blocks(1.0).in_meters
    ELEVATOR_HEIGHT: Final[Meters] = Blocks(1.0).in_meters


@dataclass
class PersonConfig:
    """Concrete implementation of Person configuration"""

    MAX_SPEED: Final[float] = 1.35  # Meters per second (4.8 km/h, 3.0 mph - Midwestern walking speed)
    WALKING_ACCELERATION: Final[float] = 0.5  # Meters per second squared
    WALKING_DECELERATION: Final[float] = 0.5  # Meters per second squared
    MAX_WAIT_TIME: Final[float] = 90.0  # seconds before getting very angry
    IDLE_TIMEOUT: Final[float] = 5.0  # In person.py update_idle method
    RADIUS: Final[Meters] = Meters(1.75)  # Visual size of person in meters


@dataclass
class PersonCosmetics:
    """Implements Person Cosmetics Proto."""

    ANGRY_MAX_RED: Final[int] = 192
    ANGRY_MIN_GREEN: Final[int] = 0
    ANGRY_MIN_BLUE: Final[int] = 0
    INITIAL_MAX_RED: Final[int] = 32
    INITIAL_MAX_GREEN: Final[int] = 128
    INITIAL_MAX_BLUE: Final[int] = 128
    INITIAL_MIN_RED: Final[int] = 0
    INITIAL_MIN_GREEN: Final[int] = 0
    INITIAL_MIN_BLUE: Final[int] = 0


@dataclass
class UIConfig:
    """Default UI configuration implementation"""

    BACKGROUND_COLOR: Final[RGB] = (220, 220, 220)
    BORDER_COLOR: Final[RGB] = (150, 150, 150)
    TEXT_COLOR: Final[RGB] = (0, 0, 0)
    BUTTON_COLOR: Final[RGB] = (200, 200, 200)
    BUTTON_HOVER_COLOR: Final[RGB] = (180, 180, 180)
    UI_FONT_NAME: Final[tuple[str, ...]] = ("Garamond", "Menlo", "Lucida Sans Typewriter")  # List of preferred fonts
    UI_FONT_SIZE: Final[int] = 20  # Default font size for UI elements
    FLOOR_LABEL_FONT_NAME: Final[tuple[str, ...]] = ("Century Gothic", "Menlo", "Lucida Sans Typewriter")  # List of preferred fonts
    FLOOR_LABEL_FONT_SIZE: Final[int] = 18  # Font size for floor labels

# pylint: enable=invalid-name

class GameConfig:
    def __init__(self) -> None:
        self._elevator: ElevatorConfigProtocol = ElevatorConfig()
        self._person: PersonConfigProtocol = PersonConfig()
        self._person_cosmetics: PersonCosmeticsProtocol = PersonCosmetics()
        self._elevator_cosmetics: ElevatorCosmeticsProtocol = ElevatorCosmetics()
        self._ui_config: UIConfigProtocol = UIConfig()
        self._initial_speed: float = 1.0
        # etc.

    @property
    def elevator(self) -> ElevatorConfigProtocol:
        return self._elevator

    @property
    def person(self) -> PersonConfigProtocol:
        return self._person

    @property
    def person_cosmetics(self) -> PersonCosmeticsProtocol:
        return self._person_cosmetics

    @property
    def elevator_cosmetics(self) -> ElevatorCosmeticsProtocol:
        return self._elevator_cosmetics

    @property
    def ui_config(self) -> UIConfigProtocol:
        return self._ui_config

    @property
    def initial_speed(self) -> float:
        return self._initial_speed
