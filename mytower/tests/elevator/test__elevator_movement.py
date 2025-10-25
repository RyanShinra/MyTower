
import pytest

from mytower.game.core.types import VerticalDirection
from mytower.game.core.units import Blocks
from mytower.game.entities.elevator import Elevator
from mytower.game.entities.entities_protocol import ElevatorDestination

class TestMovement:

    def test_set_destination_floor_down(self, elevator: Elevator) -> None:
        elevator.testing_set_current_vertical_pos(Blocks(4))
        destination = ElevatorDestination(floor=2, direction=VerticalDirection.DOWN, has_destination=True)
        elevator.set_destination(destination)
        assert elevator.destination_floor == 2
        assert elevator.nominal_direction == VerticalDirection.DOWN

    def test_set_destination_floor_same_floor(self, elevator: Elevator) -> None:
        # Setup: The elevator defaults to floor 1, this will change the state of nominal_direction
        destination_3 = ElevatorDestination(floor=3, direction=VerticalDirection.UP, has_destination=True)
        elevator.set_destination(destination_3)
        assert elevator.nominal_direction == VerticalDirection.UP

        # Test destination on same floor
        elevator.testing_set_current_vertical_pos(Blocks(2))
        destination_2 = ElevatorDestination(floor=2, direction=VerticalDirection.STATIONARY, has_destination=True)
        elevator.set_destination(destination_2)  # Already on floor 2
        assert elevator.nominal_direction == VerticalDirection.STATIONARY

    def test_set_invalid_destination_floor(self, elevator: Elevator) -> None:
        """Test that setting invalid destination floor raises ValueError"""
        with pytest.raises(ValueError):
            destination = ElevatorDestination(floor=15, direction=VerticalDirection.UP, has_destination=True)
            elevator.set_destination(destination)  # Above max floor

        with pytest.raises(ValueError):
            destination = ElevatorDestination(floor=0, direction=VerticalDirection.DOWN, has_destination=True)
            elevator.set_destination(destination)  # Below min floor