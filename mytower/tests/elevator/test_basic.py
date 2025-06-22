
import pytest
from typing import Callable, List, Final
from unittest.mock import MagicMock
from mytower.game.elevator import Elevator, ElevatorState
from mytower.game.person import Person
from mytower.game.types import VerticalDirection

# from mytower.tests.elevator.conftest import mock_person_factory

class TestElevatorBasics:
        
    def test_initial_state(self, elevator: Elevator) -> None:
        """Test that elevator initializes with correct values"""
        assert elevator.state == ElevatorState.IDLE
        assert elevator.current_floor_int == 1
        assert elevator.min_floor == 1
        assert elevator.max_floor == 10 # This should be at least 3 for a test below
        assert elevator.avail_capacity == 15
        assert elevator.is_empty

    def test_set_destination_floor_up(self, elevator: Elevator) -> None:
        """Test setting destination floor and direction updates"""
        # The elevator defaults to floor 1
        elevator.set_destination_floor(5)
        assert elevator.destination_floor == 5
        assert elevator.nominal_direction == VerticalDirection.UP
        
    def test_avail_capacity(self, elevator: Elevator, mock_person_factory: Callable[[int], MagicMock], mock_config: MagicMock) -> None:
        max_cap: int = mock_config.max_capacity
        assert elevator.avail_capacity == max_cap
        
        passengers: List[Person] = [mock_person_factory(floor) for floor in range (1, 11)]
        elevator.testing_set_passengers(passengers)
        assert elevator.avail_capacity == max_cap - len(passengers)
        
        full_passengers: List[Person] = [mock_person_factory(floor) for floor in range(1, max_cap + 1)]  # 15 passengers
        elevator.testing_set_passengers(full_passengers)
        assert elevator.avail_capacity == 0
        
        oh_no_too_many: List[Person] = [mock_person_factory(floor) for floor in range(1, max_cap + 2)] # 15 passengers
        with pytest.raises(ValueError):
            elevator.testing_set_passengers(oh_no_too_many)
        
    def test_door_open_setter_and_getter(self, elevator: Elevator) -> None:
        # Doors start closed - sensible, yes?
        assert elevator.door_open == False    
    
        elevator.door_open = True
        assert elevator.door_open == True
        
        elevator.door_open = False
        assert elevator.door_open == False

    def test_testing_set_current_floor(self, elevator: Elevator) -> None:
        elevator.testing_set_current_floor(2.0)
        assert elevator.current_floor_int == 2  
        assert elevator.fractional_floor == 2.0
        
        elevator.testing_set_current_floor(2.2)
        assert elevator.current_floor_int == 2
        assert elevator.fractional_floor == 2.2
        
        with pytest.raises(ValueError):
            elevator.testing_set_current_floor(elevator.min_floor - 2)
        
        with pytest.raises(ValueError):
            elevator.testing_set_current_floor(elevator.max_floor + 2)
            
    def test_idle_wait_timeout_property(self, elevator: Elevator, mock_config: MagicMock) -> None:
        """Test that idle_wait_timeout property returns the value from config"""
        assert elevator.idle_wait_timeout == mock_config.idle_wait_timeout

    def test_idle_time_property(self, elevator: Elevator, mock_config: MagicMock) -> None:
        """Test that idle_time property returns the value in Elevator.py"""
        assert elevator.idle_time == 0.0 # Default constant in the Elevator C'tor
        
        # Test the setter
        elevator.idle_time = 5.5
        assert elevator.idle_time == 5.5
        
        # Test setting back to zero
        elevator.idle_time = 0.0
        assert elevator.idle_time == 0.0

    def test_horizontal_block_property(self, elevator: Elevator) -> None:
        """Test that horizontal_block property returns the value encoded in Elevator c'tor in conftest.py"""
        TESTING_H_CELL_VALUE: Final[int] = 5 # Go look in conftest.py for this in the c'tor param list
        assert elevator.horizontal_block == TESTING_H_CELL_VALUE