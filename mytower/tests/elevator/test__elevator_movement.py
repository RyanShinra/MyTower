
import pytest

from mytower.game.entities.elevator import Elevator
from mytower.game.core.types import VerticalDirection



class TestMovement:
    
    def test_set_destination_floor_down(self, elevator: Elevator) -> None:
        elevator.testing_set_current_vertical_pos(4)
        elevator.set_destination_floor(2)
        assert elevator.destination_floor == 2
        assert elevator.nominal_direction == VerticalDirection.DOWN



    def test_set_destination_floor_same_floor(self, elevator: Elevator) -> None:
        # Setup: The elevator defaults to floor 1, this will change the state of nominal_direction
        elevator.set_destination_floor(3)
        assert elevator.nominal_direction == VerticalDirection.UP

        # Test destination on same floor
        elevator.testing_set_current_vertical_pos(2)
        elevator.set_destination_floor(2)  # Already on floor 2
        assert elevator.nominal_direction == VerticalDirection.STATIONARY



    def test_set_invalid_destination_floor(self, elevator: Elevator) -> None:
        """Test that setting invalid destination floor raises ValueError"""
        with pytest.raises(ValueError):
            elevator.set_destination_floor(15)  # Above max floor

        with pytest.raises(ValueError):
            elevator.set_destination_floor(0)  # Below min floor