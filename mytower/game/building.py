# game/building.py
from __future__ import annotations  # Defer type evaluation

from typing import TYPE_CHECKING, Dict, List

from pygame import Surface

from mytower.game.constants import STARTING_MONEY
from mytower.game.floor import Floor
from mytower.game.logger import LoggerProvider, MyTowerLogger
from mytower.game.types import FloorType

if TYPE_CHECKING:
    from mytower.game.person import PersonProtocol
    from mytower.game.elevator_bank import ElevatorBank


class Building:
    """
    The main building class that contains all floors, elevators, and people.
    """

    def __init__(
        self,
        logger_provider: LoggerProvider,
        width: int = 20,
    ) -> None:
        self._logger_provider: LoggerProvider = logger_provider
        self._logger: MyTowerLogger = logger_provider.get_logger("Building")

        self._floor_width: int = width  # Width in grid cells
        self._floors: Dict[int, Floor] = {}  # Dictionary with floor number as key
        self._elevator_banks: List[ElevatorBank] = []  # List of elevator objects
        self._people: List[PersonProtocol] = []  # List of people in the building
        self._time: float = 0.0  # Game time in minutes
        self._money: int = STARTING_MONEY  # Starting money

        # Add ground floor by default
        self.add_floor(FloorType.LOBBY)

    @property
    def num_floors(self) -> int:
        """Return the number of floors in the building."""
        return len(self._floors)

    @property
    def money(self) -> int:
        return self._money

    @property
    def floor_width(self) -> int:
        return self._floor_width

    def add_floor(self, floor_type: FloorType) -> Floor:
        """Add a new floor to the building"""
        next_floor = self.num_floors + 1
        self._floors[next_floor] = Floor(self._logger_provider, self, next_floor, floor_type)
        return self._floors[next_floor]

    def add_elevator_bank(self, elevator_bank: ElevatorBank) -> None:
        """Add a new elevator to the building"""
        self._elevator_banks.append(elevator_bank)

    def add_person(self, person: PersonProtocol) -> None:
        self._people.append(person)

    def get_elevator_banks_on_floor(self, floor_num: int) -> List[ElevatorBank]:
        """Returns a list of all elevators that are currently on the specified floor"""
        return [
            bank
            for bank in self._elevator_banks
            if (
                hasattr(bank, "min_floor")
                and hasattr(bank, "max_floor")
                and (bank.min_floor <= floor_num <= bank.max_floor)
            )
        ]

    def update(self, dt: float) -> None:
        """Update the building simulation by dt time"""
        self._time += dt

        for elevator in self._elevator_banks:
            if hasattr(elevator, "update"):
                elevator.update(dt)

        for person in self._people:
            if hasattr(person, "update"):
                person.update(dt)

    def draw(self, surface: Surface) -> None:
        """Draw the building on the given surface"""
        # Draw floors from bottom to top
        for floor_num in sorted(self._floors.keys()):
            self._floors[floor_num].draw(surface)

        for elevator in self._elevator_banks:
            # self._logger.debug("I want to draw an elevator bank")
            if hasattr(elevator, "draw"):
                elevator.draw(surface)

        for person in self._people:
            # self._logger.debug("I want to draw a person")
            if hasattr(person, "draw") and callable(person.draw):
                person.draw(surface)
