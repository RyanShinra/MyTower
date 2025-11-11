from __future__ import annotations  # Defer type evaluation

import sys
from typing import Final

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


from mytower.game.core.types import FloorType
from mytower.game.core.units import Blocks, Time
from mytower.game.entities.entities_protocol import \
    ElevatorBankList  # Use alias
from mytower.game.entities.entities_protocol import ElevatorList  # Use alias
from mytower.game.entities.entities_protocol import FloorList  # Use alias
from mytower.game.entities.entities_protocol import (BuildingProtocol,
                                                     ElevatorBankProtocol,
                                                     ElevatorProtocol,
                                                     FloorProtocol)
from mytower.game.entities.floor import Floor
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger


class Building(BuildingProtocol):
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

        self._floor_width: Blocks = Blocks(width)  # Width in grid cells
        self._floors: dict[int, Floor] = {}  # Dictionary with floor number as key
        self._elevator_banks: list[ElevatorBankProtocol] = []  # List of elevator objects

    @property
    @override
    def num_floors(self) -> int:
        """Return the number of floors in the building."""
        return len(self._floors)

    @property
    @override
    def building_width(self) -> Blocks:
        return self._floor_width


    @override
    def add_floor(self, floor_type: FloorType) -> int:
        """Add a new floor to the building"""
        next_floor_num: int = self.num_floors + 1
        # TODO: Left extent is hardcoded to 0 for now
        left_edge: Blocks = Blocks(0)
        self._floors[next_floor_num] = Floor(
            self._logger_provider, self, next_floor_num, floor_type, left_edge, self._floor_width
        )
        return next_floor_num

    @override
    def add_elevator_bank(self, elevator_bank: ElevatorBankProtocol) -> None:
        """Add a new elevator to the building"""
        self._elevator_banks.append(elevator_bank)


    @override
    def get_elevator_banks_on_floor(self, floor_num: int) -> ElevatorBankList:  # ✅ Cleaner
        """Returns a list of all elevators that are currently on the specified floor"""
        return [
            bank
            for bank in self._elevator_banks
            if (
                hasattr(bank, "min_floor")
                and hasattr(bank, "max_floor")  # noqa: W503
                and (bank.min_floor <= floor_num <= bank.max_floor)  # noqa: W503
            )
        ]

    @override
    def get_floors(self) -> FloorList:  # ✅ Cleaner
        return [self._floors[floor_num] for floor_num in range(1, self.num_floors + 1)]

    @override
    def get_floor_by_number(self, floor_num: int) -> FloorProtocol | None:
        return self._floors.get(floor_num)

    @override
    def get_elevator_banks(self) -> list[ElevatorBankProtocol]:
        return self._elevator_banks

    @override
    def get_elevators(self) -> ElevatorList:  # ✅ Cleaner
        """Get all elevators from all banks"""
        elevators: Final[list[ElevatorProtocol]] = []
        for bank in self._elevator_banks:
            elevators.extend(bank.elevators)
        return elevators

    @override
    def update(self, dt: Time) -> None:
        """Update the building state by time increment dt"""
        pass
