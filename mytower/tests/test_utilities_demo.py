# test_utilities_demo.py
"""
Demonstration of the new type-safe test utilities.
This file shows how to use TypedMockFactory, StateAssertions, and BoundaryTestMixin.
"""

from unittest.mock import Mock

from mytower.game.entities.person import Person
from mytower.game.core.types import PersonState, ElevatorState
from mytower.tests.test_utilities import TypedMockFactory, StateAssertions, BoundaryTestMixin
from mytower.tests.conftest import PERSON_DEFAULT_FLOOR, PERSON_DEFAULT_BLOCK


class TestTypedMockFactoryDemo:
    """Demonstrate TypedMockFactory usage"""

    def test_create_person_mock(self, typed_mock_factory: TypedMockFactory) -> None:
        """Test creating a properly typed Person mock"""
        person_mock = typed_mock_factory.create_person_mock(
            current_floor=5,
            destination_floor=8,
            current_block=15.5,
            person_id="demo_person",
            state=PersonState.WALKING
        )
        
        # All properties are properly typed and accessible
        assert person_mock.current_floor_num == 5
        assert person_mock.destination_floor_num == 8
        assert person_mock.current_block_float == 15.5
        assert person_mock.person_id == "demo_person"
        assert person_mock.state == PersonState.WALKING
        
        # Methods are available
        assert hasattr(person_mock, 'board_elevator')
        assert hasattr(person_mock, 'disembark_elevator')

    def test_create_elevator_mock(self, typed_mock_factory: TypedMockFactory) -> None:
        """Test creating a properly typed Elevator mock"""
        elevator_mock = typed_mock_factory.create_elevator_mock(
            current_floor=3,
            state=ElevatorState.MOVING,
            elevator_id="demo_elevator",
            passenger_count=7
        )
        
        assert elevator_mock.current_floor_int == 3
        assert elevator_mock.state == ElevatorState.MOVING
        assert elevator_mock.elevator_id == "demo_elevator"
        assert elevator_mock.passenger_count == 7
        assert elevator_mock.fractional_floor == 3.0  # Default based on current_floor

    def test_create_building_mock(self, typed_mock_factory: TypedMockFactory) -> None:
        """Test creating a properly typed Building mock"""
        building_mock = typed_mock_factory.create_building_mock(
            num_floors=15,
            floor_width=25,
            has_floors=True
        )
        
        assert building_mock.num_floors == 15
        assert building_mock.floor_width == 25
        assert building_mock.get_floor_by_number(1) is not None  # has_floors=True


class TestStateAssertionsDemo:
    """Demonstrate StateAssertions usage"""

    def test_assert_person_state(
        self, 
        person_with_floor: Person, 
        state_assertions: StateAssertions
    ) -> None:
        """Test using StateAssertions for cleaner person state testing"""
        # Instead of multiple individual asserts, use one clear assertion
        state_assertions.assert_person_state(
            person_with_floor,
            expected_state=PersonState.IDLE,
            expected_floor=PERSON_DEFAULT_FLOOR,
            expected_block=PERSON_DEFAULT_BLOCK,
            expected_destination_floor=PERSON_DEFAULT_FLOOR
        )

    def test_assert_elevator_state(
        self, 
        typed_mock_factory: TypedMockFactory,
        state_assertions: StateAssertions
    ) -> None:
        """Test using StateAssertions for elevator state testing"""
        elevator_mock = typed_mock_factory.create_elevator_mock(
            current_floor=7,
            state=ElevatorState.ARRIVED,
            passenger_count=3
        )
        
        # Clean, readable state assertion
        state_assertions.assert_elevator_state(
            elevator_mock,
            expected_state=ElevatorState.ARRIVED,
            expected_floor=7,
            expected_passenger_count=3
        )


class TestBoundaryTestMixinDemo(BoundaryTestMixin):
    """Demonstrate BoundaryTestMixin usage"""

    def test_boundary_validation_example(self, person_with_floor: Person) -> None:
        """Test using BoundaryTestMixin for boundary testing"""
        valid_floors = [1, 5, 10]
        invalid_floors = [-1, 11, 100]  # 0 is excluded because some buildings may have a valid floor 0 (e.g., ground floor)
        
        # Test person destination floor boundary validation
        def set_dest_floor(floor_num: int) -> None:
            person_with_floor.set_destination(dest_floor_num=floor_num, dest_block_num=10)
        
        # This tests both valid and invalid values in one clean call
        self.assert_boundary_validation(
            func=set_dest_floor,
            valid_values=valid_floors,
            invalid_values=invalid_floors,
            exception_type=ValueError
        )

    def test_building_mock_factory_boundary(
        self, 
        typed_mock_factory: TypedMockFactory
    ) -> None:
        """Test boundary validation with mock factory"""
        def create_building_with_floors(num_floors: int) -> Mock:
            return typed_mock_factory.create_building_mock(num_floors=num_floors)
        
        valid_floor_counts = [1, 10, 50]
        
        # Test that building creation works for valid values
        for valid_count in valid_floor_counts:
            building = create_building_with_floors(valid_count)
            assert building.num_floors == valid_count


class TestIntegratedUtilitiesDemo:
    """Demonstrate using multiple utilities together"""

    def test_person_elevator_interaction_complete(
        self,
        person_with_floor: Person,
        typed_mock_factory: TypedMockFactory,
        state_assertions: StateAssertions
    ) -> None:
        """Test complete person-elevator interaction using all utilities"""
        # Create properly typed elevator mock
        elevator_mock = typed_mock_factory.create_elevator_mock(
            current_floor=8,
            state=ElevatorState.IDLE,
            elevator_id="test_elevator_complete"
        )
        
        # Test boarding
        person_with_floor.board_elevator(elevator_mock)
        
        # Use state assertions for clean validation
        state_assertions.assert_person_state(
            person_with_floor,
            expected_state=PersonState.IN_ELEVATOR
        )
        
        # Verify elevator reference
        assert person_with_floor.testing_get_current_elevator() == elevator_mock
        
        # Test disembarking
        floor_mock = typed_mock_factory.create_floor_mock(floor_num=8)
        person_with_floor.building.get_floor_by_number.return_value = floor_mock  # type: ignore
        
        person_with_floor.disembark_elevator()
        
        # Clean state validation after disembarking
        state_assertions.assert_person_state(
            person_with_floor,
            expected_state=PersonState.IDLE,
            expected_floor=8
        )