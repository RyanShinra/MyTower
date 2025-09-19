# game/config.py
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from mytower.game.core.constants import BLOCK_HEIGHT, BLOCK_WIDTH
from mytower.game.core.types import RGB
from mytower.game.views.desktop_ui import UIConfigProtocol

if TYPE_CHECKING:
    from mytower.game.entities.elevator import ElevatorConfigProtocol, ElevatorCosmeticsProtocol
    from mytower.game.entities.person import PersonConfigProtocol, PersonCosmeticsProtocol


@dataclass
class ElevatorConfig:
    """Concrete implementation of Elevator configuration"""

    max_speed: Final[float] = 0.75  # Floors per second
    max_capacity: Final[int] = 15  # Number of people who can fit on board
    passenger_loading_time: Final[float] = 1.0  # How long it takes a single passenger to board
    idle_wait_timeout: Final[float] = 0.5  # Seconds: how often an idle elevator checks for passengers
    idle_log_timeout: Final[float] = 0.5  # Seconds: how often to log status while Idle
    moving_log_timeout: Final[float] = 0.5  # Seconds: how often to log status while Moving


@dataclass
class ElevatorCosmetics:
    """Implements Elevator Cosmetics Protocol"""

    shaft_color: Final[RGB] = (100, 100, 100)
    shaft_overhead_color: Final[RGB] = (24, 24, 24)
    closed_color: Final[RGB] = (50, 50, 200)
    open_color: Final[RGB] = (200, 200, 50)
    shaft_overhead_height: Final[int] = BLOCK_HEIGHT  # Pixels
    elevator_width: Final[int] = BLOCK_WIDTH  # Pixels


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
    ui_font_name: Final[tuple[str, ...]] = ("Garamond", "Menlo", "Lucida Sans Typewriter")  # List of preferred fonts
    ui_font_size: Final[int] = 20  # Default font size for UI elements
    floor_label_font_name: Final[tuple[str, ...]] = ("Century Gothic", "Menlo", "Lucida Sans Typewriter")  # List of preferred fonts
    floor_label_font_size: Final[int] = 18  # Font size for floor labels

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
