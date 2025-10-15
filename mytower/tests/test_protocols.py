"""
Test-specific protocol combinations for type-safe testing.
Combines production and testing protocols for comprehensive test coverage.
"""

from typing import Protocol
from mytower.game.entities.entities_protocol import (
    ElevatorProtocol, 
    ElevatorTestingProtocol,
    PersonProtocol,
    # Add others as needed
)


class TestableElevatorProtocol(ElevatorProtocol, ElevatorTestingProtocol, Protocol):
    """
    Combined protocol for testing Elevators.
    Provides both production interface and testing hooks.
    """
    pass


class TestablePersonProtocol(PersonProtocol, Protocol):
    """
    Combined protocol for testing Persons.
    Extend with PersonTestingProtocol when it exists.
    """
    pass
