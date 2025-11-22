# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

# test_utilities_demo.py
"""
Demonstration of the new type-safe test utilities.
Shows proper handling of Mock vs Protocol types.
"""

from typing import cast
from unittest.mock import Mock

from mytower.game.core.types import ElevatorState, PersonState
from mytower.game.core.units import Blocks
from mytower.game.entities.entities_protocol import ElevatorProtocol, PersonProtocol
from mytower.game.entities.person import Person
from mytower.tests.conftest import PERSON_DEFAULT_BLOCK, PERSON_DEFAULT_FLOOR
from mytower.tests.test_utilities import StateAssertions, TypedMockFactory


class TestTypedMockFactoryDemo:
    """Demonstrate TypedMockFactory usage with proper type handling"""


    def test_create_person_mock_basic(self, typed_mock_factory: TypedMockFactory) -> None:
        """Test creating a Person mock - basic usage without type casting"""
        # Factory returns Mock - this is honest
        person_mock: Mock = typed_mock_factory.create_person_mock(
            current_floor=5, destination_floor=8, current_block=15.5, person_id="demo_person", state=PersonState.WALKING
        )

        # Mock supports the protocol interface
        assert person_mock.current_floor_num == 5
        assert person_mock.destination_floor_num == 8
        assert person_mock.state == PersonState.WALKING


    def test_create_person_mock_with_protocol_typing(self, typed_mock_factory: TypedMockFactory) -> None:
        """Test creating a Person mock with explicit protocol typing"""
        # When you need PersonProtocol typing, use cast
        person_mock_raw = typed_mock_factory.create_person_mock(
            current_floor=5, destination_floor=8, current_block=15.5, person_id="demo_person", state=PersonState.WALKING
        )

        # Explicit cast when protocol type is needed
        person_protocol: PersonProtocol = cast(PersonProtocol, person_mock_raw)

        # Now type checker knows it's a PersonProtocol
        def process_person(p: PersonProtocol) -> int:
            return p.current_floor_num

        result = process_person(person_protocol)
        assert result == 5


    def test_create_elevator_mock(self, typed_mock_factory: TypedMockFactory) -> None:
        """Test creating an Elevator mock"""
        elevator_mock = typed_mock_factory.create_elevator_mock(
            current_floor=3, state=ElevatorState.MOVING, elevator_id="demo_elevator", passenger_count=7
        )

        # Use as Mock directly in tests
        assert elevator_mock.current_floor_int == 3
        assert elevator_mock.state == ElevatorState.MOVING

        # Cast when needed for protocol-typed functions
        elevator_protocol: ElevatorProtocol = cast(ElevatorProtocol, elevator_mock)
        assert elevator_protocol.elevator_id == "demo_elevator"


class TestStateAssertionsDemo:
    """Demonstrate StateAssertions with proper Mock handling"""


    def test_assert_person_state_with_real_person(
        self, person_with_floor: Person, state_assertions: StateAssertions
    ) -> None:
        """Test using StateAssertions with a real Person object"""
        # StateAssertions accepts both PersonProtocol and Mock
        state_assertions.assert_person_state(
            person_with_floor,
            expected_state=PersonState.IDLE,
            expected_floor=PERSON_DEFAULT_FLOOR,
            expected_block=PERSON_DEFAULT_BLOCK,
            expected_destination_floor=PERSON_DEFAULT_FLOOR,
        )

    def test_assert_person_state_with_mock(
        self, typed_mock_factory: TypedMockFactory, state_assertions: StateAssertions
    ) -> None:
        """Test using StateAssertions with a Mock"""
        person_mock = typed_mock_factory.create_person_mock(current_floor=7, state=PersonState.WALKING)

        # StateAssertions handles Mock just fine
        state_assertions.assert_person_state(person_mock, expected_state=PersonState.WALKING, expected_floor=7)


class TestIntegratedUtilitiesDemo:
    """Demonstrate using multiple utilities together"""


    def test_person_elevator_interaction_complete(
        self, person_with_floor: Person, typed_mock_factory: TypedMockFactory, state_assertions: StateAssertions
    ) -> None:
        """Test complete person-elevator interaction using all utilities"""
        # Create elevator mock
        elevator_mock_raw = typed_mock_factory.create_elevator_mock(
            current_floor=8, state=ElevatorState.IDLE, elevator_id="test_elevator_complete"
        )

        # Cast to protocol for person.board_elevator() which expects ElevatorProtocol
        elevator_mock = cast(ElevatorProtocol, elevator_mock_raw)

        # Test boarding
        person_with_floor.board_elevator(elevator_mock)

        # Use state assertions (accepts both protocol and Mock)
        state_assertions.assert_person_state(person_with_floor, expected_state=PersonState.IN_ELEVATOR)

        # Verify elevator reference
        assert person_with_floor.testing_get_current_elevator() == elevator_mock

        # For disembarking, we need a floor to exist in the building
        # The person_with_floor fixture's building already has a mocked floor
        # We just need to ensure it returns the right floor for the current location
        floor_mock = typed_mock_factory.create_floor_mock(floor_num=8)

        # Get the building mock (from fixture) and configure it
        # Note: person_with_floor uses mock_building_with_floor from conftest
        building_mock = cast(Mock, person_with_floor.building)
        building_mock.get_floor_by_number.return_value = floor_mock

        person_with_floor.disembark_elevator()

        # Clean state validation after disembarking
        state_assertions.assert_person_state(person_with_floor, expected_state=PersonState.IDLE, expected_floor=8)


    def test_person_with_fully_mocked_dependencies(
        self,
        typed_mock_factory: TypedMockFactory,
        state_assertions: StateAssertions,
        mock_logger_provider: Mock,
        mock_game_config: Mock,
    ) -> None:
        """
        Demonstrate testing with fully controlled mocks.

        This pattern gives you complete control over all dependencies,
        which is useful when you need to test specific edge cases.
        """
        # Create a fully mocked building
        building_mock: Mock = typed_mock_factory.create_building_mock(num_floors=10, floor_width=20.0)

        # Configure the building mock's floor behavior
        floor_mock: Mock = typed_mock_factory.create_floor_mock(floor_num=5)
        building_mock.get_floor_by_number.return_value = floor_mock

        # Create a person with the mocked building
        person = Person(
            logger_provider=mock_logger_provider,
            building=building_mock,  # BuildingProtocol satisfied by Mock
            initial_floor_number=5,
            initial_horiz_position=Blocks(10.0),
            config=mock_game_config,
        )

        # Now we have full control over building behavior
        state_assertions.assert_person_state(person, expected_state=PersonState.IDLE, expected_floor=5)

        # Verify the building mock was called correctly during Person init
        building_mock.get_floor_by_number.assert_called_with(5)
        floor_mock.add_person.assert_called_once_with(person)


class TestProperMockTypingPatterns:
    """Demonstrate proper patterns for Mock vs Protocol typing"""


    def test_when_to_cast_to_protocol(self, typed_mock_factory: TypedMockFactory) -> None:
        """Show when casting to protocol is necessary"""
        # Create mock - returns Mock
        person_mock_raw = typed_mock_factory.create_person_mock(current_floor=5, destination_floor=10)

        # Pattern 1: Use as Mock when testing mock behavior
        person_mock_raw.board_elevator.assert_not_called()  # Mock-specific method

        # Pattern 2: Cast to protocol when passing to production code
        def process_person_production(p: PersonProtocol) -> str:
            return f"Floor {p.current_floor_num}"

        person_protocol = cast(PersonProtocol, person_mock_raw)
        result = process_person_production(person_protocol)
        assert result == "Floor 5"

    def test_mock_flexibility(self, typed_mock_factory: TypedMockFactory) -> None:
        """Show that Mocks are more flexible than protocols"""
        elevator_mock = typed_mock_factory.create_elevator_mock()

        # Mock allows runtime property changes - protocols don't
        elevator_mock.custom_test_property = "test_value"
        assert elevator_mock.custom_test_property == "test_value"

        # This flexibility is useful in tests but breaks protocol contract
        # That's why we return Mock, not ElevatorProtocol
