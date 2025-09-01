from __future__ import annotations  # Defer type evaluation

from typing import TYPE_CHECKING, Dict, List

from pygame import Surface

from mytower.game.constants import STARTING_MONEY
# pyright: ignore[reportImportCycles] 
from mytower.game.elevator import Elevator
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
        self._people: Dict[str, PersonProtocol] = {}  # Dictionary of people in the building with their id as the key
        self._time: float = 0.0  # Game time in minutes
        self._money: int = STARTING_MONEY  # Starting money

        # Add ground floor by default
        # It might be helpful to hold onto this reference in the future
        _ = self.add_floor(FloorType.LOBBY)

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
    
    @property
    def people(self) -> List[PersonProtocol]:
        return list(self._people.values())

    def add_floor(self, floor_type: FloorType) -> int:
        """Add a new floor to the building"""
        next_floor_num: int = self.num_floors + 1
        self._floors[next_floor_num] = Floor(self._logger_provider, self, next_floor_num, floor_type)
        return next_floor_num

    def add_elevator_bank(self, elevator_bank: ElevatorBank) -> None:
        """Add a new elevator to the building"""
        self._elevator_banks.append(elevator_bank)

    def add_person(self, person: PersonProtocol) -> None:
        self._people[person.person_id] = person
        
    def get_person_by_id(self, person_id: str) -> PersonProtocol | None:
        return self._people.get(person_id)

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
        
    def get_floors(self) -> List[Floor]:
        return [
            self._floors[floor_num]
            for floor_num in range(1, self.num_floors + 1)
        ]

    def get_elevator_banks(self) -> List[ElevatorBank]:
        return self._elevator_banks

    def get_elevators(self) -> List[Elevator]:
        """Get all elevators from all banks"""
        elevators: List[Elevator] = []
        for bank in self._elevator_banks:
            elevators.extend(bank.elevators)
        return elevators

    def update(self, dt: float) -> None:
        """Update the building simulation by dt time"""
        self._time += dt

        for elevator in self._elevator_banks:
            if hasattr(elevator, "update"):
                elevator.update(dt)

        for person in self.people:
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

        for person in self.people:
            # self._logger.debug("I want to draw a person")
            if hasattr(person, "draw") and callable(person.draw):
                person.draw(surface)
