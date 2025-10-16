"""
Test-specific protocol combinations for type-safe testing.
Combines production and testing protocols for comprehensive test coverage.
"""

from typing import Protocol
from mytower.game.entities.entities_protocol import (
    ElevatorProtocol, 
    ElevatorTestingProtocol,
    PersonProtocol,
    PersonTestingProtocol,
    ElevatorBankProtocol,
    ElevatorBankTestingProtocol,
    FloorProtocol,
    BuildingProtocol,
)


class TestableElevatorProtocol(ElevatorProtocol, ElevatorTestingProtocol, Protocol):
    """
    Combined protocol for testing Elevators.
    Provides both production interface and testing hooks.
    """
    pass


class TestablePersonProtocol(PersonProtocol, PersonTestingProtocol, Protocol):
    """
    Combined protocol for testing Persons.
    Provides both production interface and testing hooks.
    """
    pass


class TestableElevatorBankProtocol(ElevatorBankProtocol, ElevatorBankTestingProtocol, Protocol):
    """
    Combined protocol for testing ElevatorBanks.
    Provides both production interface and testing hooks.
    """
    pass


# Floor and Building don't need testing protocols yet
# They can use production protocols directly
TestableFloorProtocol = FloorProtocol
TestableBuildingProtocol = BuildingProtocol
