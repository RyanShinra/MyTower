from __future__ import annotations  # Defer type evaluation

from typing import TYPE_CHECKING, Dict, List

from pygame import Surface


# pyright: ignore[reportImportCycles] 
from mytower.game.entities.elevator import Elevator
from mytower.game.entities.floor import Floor
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger
from mytower.game.core.types import FloorType

if TYPE_CHECKING:
    from mytower.game.entities.person import PersonProtocol
    from mytower.game.entities.elevator_bank import ElevatorBank


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
        
        # TODO: Remove this when fully migrating to GameModel and Floor ownership
        self._people: Dict[str, PersonProtocol] = {}  # Dictionary of people in the building with their id as the key        

    @property
    def num_floors(self) -> int:
        """Return the number of floors in the building."""
        return len(self._floors)

    @property
    def floor_width(self) -> int:
        return self._floor_width
    
    # TODO: Remove this when fully migrating to GameModel and Floor ownership
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

    # TODO: Remove this when fully migrating to GameModel and Floor ownership
    def add_person(self, person: PersonProtocol) -> None:
        self._people[person.person_id] = person

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

    def get_floor_by_number(self, floor_num: int) -> Floor | None:
        return self._floors.get(floor_num)

    def get_elevator_banks(self) -> List[ElevatorBank]:
        return self._elevator_banks

    def get_elevators(self) -> List[Elevator]:
        """Get all elevators from all banks"""
        elevators: List[Elevator] = []
        for bank in self._elevator_banks:
            elevators.extend(bank.elevators)
        return elevators

    def update(self, dt: float) -> None:
        """Update the building state by time increment dt (in seconds)"""
        pass        


    def draw(self, surface: Surface) -> None:
        """Draw the building on the given surface"""
        # Draw floors from bottom to top
        for floor_num in sorted(self._floors.keys()):
            self._floors[floor_num].draw(surface)

        for elevator in self._elevator_banks:
            # self._logger.debug("I want to draw an elevator bank")
            if hasattr(elevator, "draw"):
                elevator.draw(surface)
