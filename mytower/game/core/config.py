# game/config.py
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Protocol

from mytower.game.core.types import RGB
from mytower.game.core.units import Blocks, Meters, Time, Velocity

if TYPE_CHECKING:
    from mytower.game.views.desktop_ui import UIConfigProtocol

# It can't seem to make up its mind whether to use snake_case because they are class properties or UPPER_CASE for constants
# So, it gets neither
# pylint: disable=invalid-name

# flake8: noqa: E704
# Protocol definitions for configuration
class ElevatorConfigProtocol(Protocol):
    """Config requirements for Elevator class"""

    @property
    def MAX_SPEED(self) -> Velocity: ...

    @property
    def MAX_CAPACITY(self) -> int: ...

    @property
    def PASSENGER_LOADING_TIME(self) -> Time: ...

    @property
    def IDLE_LOG_TIMEOUT(self) -> Time: ...

    @property
    def MOVING_LOG_TIMEOUT(self) -> Time: ...

    @property
    def IDLE_WAIT_TIMEOUT(self) -> Time: ...

class ElevatorCosmeticsProtocol(Protocol):
    """Visual appearance settings for Elevator class"""

    @property
    def SHAFT_COLOR(self) -> RGB: ...

    @property
    def SHAFT_OVERHEAD_COLOR(self) -> RGB: ...

    @property
    def CLOSED_COLOR(self) -> RGB: ...

    @property
    def OPEN_COLOR(self) -> RGB: ...

    @property
    def SHAFT_OVERHEAD_HEIGHT(self) -> Meters: ...
    
    @property
    def ELEVATOR_WIDTH(self) -> Meters: ...
    
    @property
    def ELEVATOR_HEIGHT(self) -> Meters: ...

class PersonConfigProtocol(Protocol):
    """Config requirements for Person class"""

    @property
    def MAX_SPEED(self) -> Velocity: ...

    @property
    def MAX_WAIT_TIME(self) -> Time: ...

    @property
    def IDLE_TIMEOUT(self) -> Time: ...

    @property
    def RADIUS(self) -> Meters: ...

class PersonCosmeticsProtocol(Protocol):
    """Visual appearance settings for Person class"""

    @property
    def ANGRY_MAX_RED(self) -> int: ...

    @property
    def ANGRY_MIN_GREEN(self) -> int: ...

    @property
    def ANGRY_MIN_BLUE(self) -> int: ...

    @property
    def INITIAL_MAX_RED(self) -> int: ...

    @property
    def INITIAL_MAX_GREEN(self) -> int: ...

    @property
    def INITIAL_MAX_BLUE(self) -> int: ...

    @property
    def INITIAL_MIN_RED(self) -> int: ...

    @property
    def INITIAL_MIN_GREEN(self) -> int: ...

    @property
    def INITIAL_MIN_BLUE(self) -> int: ...

    @property
    def COLOR_PALETTE(self) -> tuple[tuple[int, int, int], ...]: ...

# Concrete configuration implementations
@dataclass
class ElevatorConfig:
    """Concrete implementation of Elevator configuration"""
    MAX_SPEED: Velocity = Velocity(3.5)  # Changed from float to Velocity (m/s)
    MAX_CAPACITY: Final[int] = 15  # Number of people who can fit on board
    PASSENGER_LOADING_TIME: Time = Time(1.0)  # Time to load one passenger
    IDLE_WAIT_TIMEOUT: Time = Time(0.5)  # Seconds: how often an idle elevator checks for passengers
    IDLE_LOG_TIMEOUT: Time = Time(0.5)  # Seconds: how often to log status while Idle
    MOVING_LOG_TIMEOUT: Time = Time(0.5)  # Seconds: how often to log status while Moving


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
    """Person behavior configuration with explicit units"""
    MAX_SPEED: Velocity = Velocity(1.35)  # Explicit m/s (approx 3 mph)
    WALKING_ACCELERATION: float = 0.5  # TODO: Make this Velocity/Time
    WALKING_DECELERATION: float = 0.5  # TODO: Make this Velocity/Time
    MAX_WAIT_TIME: Time = Time(90.0)   # Explicit seconds
    IDLE_TIMEOUT: Time = Time(5.0)     # Explicit seconds
    RADIUS: Meters = Meters(1.75 / 2)      # Explicit meters (divide by two so that the radius is half the average height of 175 cm)


@dataclass
class PersonCosmetics:
    """Implements Person Cosmetics Proto."""

    ANGRY_MAX_RED: Final[int] = 192
    ANGRY_MIN_GREEN: Final[int] = 0
    ANGRY_MIN_BLUE: Final[int] = 0
    INITIAL_MAX_RED: Final[int] = 64
    INITIAL_MAX_GREEN: Final[int] = 160
    INITIAL_MAX_BLUE: Final[int] = 160
    INITIAL_MIN_RED: Final[int] = 0
    INITIAL_MIN_GREEN: Final[int] = 0
    INITIAL_MIN_BLUE: Final[int] = 0
    
    # Predefined color palette for people (10 colors using the clamped values)
    COLOR_PALETTE: Final[tuple[tuple[int, int, int], ...]] = (
        (32, 32, 32),       # Black
        (64, 0, 0),      # Dark Red
        (64, 64, 0),    # Yellow-Green
        (0, 128, 0),     # Green
        (0, 128, 128),   # Cyan
        (32, 80, 80),    # Teal
        (16, 16, 64),   # Dark Blue
        (0, 0, 160),     # Blue
        (64, 0, 128),    # Purple
    )


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
        self._initial_speed: float = 5.0 # TODO: Change this back to 1.0
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
