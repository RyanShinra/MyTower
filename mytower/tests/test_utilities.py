# test_utilities.py
"""
Type-safe test utilities for MyTower tests.
Provides mock factories and assertion helpers to improve test maintainability and type safety.
"""

from typing import Any, Protocol, Callable
from unittest.mock import Mock, PropertyMock
import pytest

from mytower.game.entities.person import PersonProtocol
from mytower.game.entities.elevator import Elevator
from mytower.game.entities.building import Building
from mytower.game.entities.floor import Floor
from mytower.game.entities.elevator_bank import ElevatorBank
from mytower.game.core.types import PersonState, ElevatorState, VerticalDirection


class MockFactoryProtocol(Protocol):
    """Protocol for creating type-safe mocks"""
    
    def create_person_mock(
        self, 
        current_floor: int = 1,
        destination_floor: int = 1,
        current_block: float = 10.0,
        person_id: str = "test_person_1",
        **overrides: Any
    ) -> Mock: ...
    
    def create_elevator_mock(
        self,
        current_floor: int = 1, 
        state: ElevatorState = ElevatorState.IDLE,
        elevator_id: str = "test_elevator_1",
        **overrides: Any
    ) -> Mock: ...
    
    def create_building_mock(
        self,
        num_floors: int = 10,
        floor_width: int = 20,
        has_floors: bool = True,
        **overrides: Any
    ) -> Mock: ...

    def create_floor_mock(
        self,
        floor_num: int = 1,
        **overrides: Any
    ) -> Mock: ...

    def create_elevator_bank_mock(
        self,
        horizontal_block: int = 5,
        min_floor: int = 1,
        max_floor: int = 10,
        **overrides: Any
    ) -> Mock: ...


class TypedMockFactory:
    """Type-safe mock creation factory"""
    
    def create_person_mock(
        self, 
        current_floor: int = 1,
        destination_floor: int = 1,
        current_block: float = 10.0,
        person_id: str = "test_person_1",
        state: PersonState = PersonState.IDLE,
        **overrides: Any
    ) -> Mock:
        """Create a properly typed Person mock"""
        mock = Mock(spec=PersonProtocol)
        
        # Set up properties with PropertyMock for proper behavior
        type(mock).current_floor_num = PropertyMock(return_value=current_floor)
        type(mock).destination_floor_num = PropertyMock(return_value=destination_floor)
        type(mock).current_block_float = PropertyMock(return_value=current_block)
        type(mock).person_id = PropertyMock(return_value=person_id)
        type(mock).state = PropertyMock(return_value=state)
        
        # Set up methods
        mock.board_elevator = Mock()
        mock.disembark_elevator = Mock()
        mock.set_destination = Mock()
        mock.update = Mock()
        mock.find_nearest_elevator_bank = Mock(return_value=None)
        
        # Apply any overrides
        for key, value in overrides.items():
            if hasattr(type(mock), key):
                # If it's a property, set it via PropertyMock
                setattr(type(mock), key, PropertyMock(return_value=value))
            else:
                setattr(mock, key, value)
            
        return mock
    
    def create_elevator_mock(
        self,
        current_floor: int = 1, 
        state: ElevatorState = ElevatorState.IDLE,
        elevator_id: str = "test_elevator_1",
        fractional_floor: float | None = None,
        passenger_count: int = 0,
        max_capacity: int = 15,
        **overrides: Any
    ) -> Mock:
        """Create a properly typed Elevator mock"""
        mock = Mock(spec=Elevator)
        
        if fractional_floor is None:
            fractional_floor = float(current_floor)
        
        # Set up properties
        type(mock).current_floor_int = PropertyMock(return_value=current_floor)
        type(mock).fractional_floor = PropertyMock(return_value=fractional_floor)
        type(mock).elevator_id = PropertyMock(return_value=elevator_id)
        type(mock).state = PropertyMock(return_value=state)
        type(mock).passenger_count = PropertyMock(return_value=passenger_count)
        type(mock).max_capacity = PropertyMock(return_value=max_capacity)
        type(mock).door_open = PropertyMock(return_value=False)
        type(mock).nominal_direction = PropertyMock(return_value=VerticalDirection.STATIONARY)
        
        # Set up methods
        mock.set_destination_floor = Mock()
        mock.update = Mock()
        mock.add_passenger = Mock()
        mock.remove_passenger = Mock()
        
        # Mock parent elevator bank
        mock.parent_elevator_bank = Mock()
        mock.parent_elevator_bank.horizontal_block = 5
        mock.parent_elevator_bank.get_waiting_block = Mock(return_value=5)
        
        # Apply any overrides
        for key, value in overrides.items():
            if hasattr(type(mock), key):
                setattr(type(mock), key, PropertyMock(return_value=value))
            else:
                setattr(mock, key, value)
            
        return mock
    
    def create_building_mock(
        self,
        num_floors: int = 10,
        floor_width: int = 20,
        has_floors: bool = True,
        **overrides: Any
    ) -> Mock:
        """Create a properly typed Building mock"""
        mock = Mock(spec=Building)
        
        # Set up properties
        mock.num_floors = num_floors
        mock.floor_width = floor_width
        mock.people = []
        
        # Set up methods
        mock.get_elevator_banks_on_floor = Mock(return_value=[])
        mock.add_person = Mock()
        mock.get_elevator_banks = Mock(return_value=[])
        
        if has_floors:
            mock_floor = self.create_floor_mock()
            mock.get_floor_by_number = Mock(return_value=mock_floor)
        else:
            mock.get_floor_by_number = Mock(return_value=None)
            
        # Apply any overrides
        for key, value in overrides.items():
            setattr(mock, key, value)
            
        return mock
    
    def create_floor_mock(
        self,
        floor_num: int = 1,
        **overrides: Any
    ) -> Mock:
        """Create a properly typed Floor mock"""
        mock = Mock(spec=Floor)
        
        # Set up properties
        mock.floor_num = floor_num
        mock.width = 20
        mock.height = 1
        mock.left_edge = 0
        mock.number_of_people = 0
        
        # Set up methods
        mock.add_person = Mock()
        mock.remove_person = Mock()
        
        # Apply any overrides
        for key, value in overrides.items():
            setattr(mock, key, value)
            
        return mock
    
    def create_elevator_bank_mock(
        self,
        horizontal_block: int = 5,
        min_floor: int = 1,
        max_floor: int = 10,
        **overrides: Any
    ) -> Mock:
        """Create a properly typed ElevatorBank mock"""
        mock = Mock(spec=ElevatorBank)
        
        # Set up properties
        mock.horizontal_block = horizontal_block
        mock.min_floor = min_floor
        mock.max_floor = max_floor
        
        # Set up methods
        mock.get_waiting_block = Mock(return_value=horizontal_block)
        mock.add_waiting_passenger = Mock()
        mock.request_elevator = Mock()
        mock.get_requests_for_floor = Mock(return_value=set())
        
        # Apply any overrides
        for key, value in overrides.items():
            setattr(mock, key, value)
            
        return mock


class StateAssertions:
    """Common state assertion helpers for improved test readability"""
    
    @staticmethod
    def assert_person_state(
        person: PersonProtocol,
        expected_state: PersonState,
        expected_floor: int | None = None,
        expected_block: float | None = None,
        expected_destination_floor: int | None = None
    ) -> None:
        """Assert person is in expected state and position"""
        assert person.state == expected_state, f"Expected state {expected_state}, got {person.state}"
        
        if expected_floor is not None:
            assert person.current_floor_num == expected_floor, f"Expected floor {expected_floor}, got {person.current_floor_num}"
        
        if expected_block is not None:
            assert person.current_block_float == expected_block, f"Expected block {expected_block}, got {person.current_block_float}"
        
        if expected_destination_floor is not None:
            assert person.destination_floor_num == expected_destination_floor, f"Expected destination floor {expected_destination_floor}, got {person.destination_floor_num}"
    
    @staticmethod
    def assert_elevator_state(
        elevator: Elevator,
        expected_state: ElevatorState,
        expected_floor: int | None = None,
        expected_passenger_count: int | None = None,
        expected_destination: int | None = None
    ) -> None:
        """Assert elevator is in expected state"""
        assert elevator.state == expected_state, f"Expected state {expected_state}, got {elevator.state}"
        
        if expected_floor is not None:
            assert elevator.current_floor_int == expected_floor, f"Expected floor {expected_floor}, got {elevator.current_floor_int}"
        
        if expected_passenger_count is not None:
            assert elevator.passenger_count == expected_passenger_count, f"Expected {expected_passenger_count} passengers, got {elevator.passenger_count}"
        
        if expected_destination is not None:
            assert elevator.destination_floor == expected_destination, f"Expected destination {expected_destination}, got {elevator.destination_floor}"
    
    @staticmethod
    def assert_mock_called_with_person(
        mock_method: Mock,
        expected_person: PersonProtocol,
        call_index: int = 0
    ) -> None:
        """Assert a mock method was called with a specific person"""
        assert mock_method.call_count > call_index, f"Expected at least {call_index + 1} calls, got {mock_method.call_count}"
        
        actual_person = mock_method.call_args_list[call_index][0][0]
        assert actual_person == expected_person, f"Expected person {expected_person.person_id}, got {actual_person.person_id}"
    
    @staticmethod
    def assert_no_exceptions_raised(func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Assert that a function call does not raise any exceptions"""
        try:
            func(*args, **kwargs)
        except Exception as e:
            pytest.fail(f"Expected no exceptions, but {type(e).__name__} was raised: {e}")


class BoundaryTestMixin:
    """Mixin providing common boundary testing patterns"""
    
    @staticmethod
    def assert_boundary_validation(
        func: Callable[..., Any], 
        valid_values: list[Any], 
        invalid_values: list[Any],
        exception_type: type[Exception] = ValueError,
        **kwargs: Any
    ) -> None:
        """Test boundary conditions for a function"""
        # Test valid values don't raise exceptions
        for valid_value in valid_values:
            try:
                func(valid_value, **kwargs)
            except Exception as e:
                pytest.fail(f"Valid value {valid_value} raised {type(e).__name__}: {e}")
            
        # Test invalid values raise appropriate exceptions
        for invalid_value in invalid_values:
            with pytest.raises(exception_type):
                func(invalid_value, **kwargs)


# Global instances for easy importing
mock_factory = TypedMockFactory()
state_assertions = StateAssertions()
boundary_test_mixin = BoundaryTestMixin()