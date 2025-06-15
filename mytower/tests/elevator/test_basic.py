

from mytower.game.elevator import Elevator, ElevatorState
from mytower.game.types import VerticalDirection

class TestElevatorBasics:
        
    def test_initial_state(self, elevator: Elevator) -> None:
        """Test that elevator initializes with correct values"""
        assert elevator.state == ElevatorState.IDLE
        assert elevator.current_floor_int == 1
        assert elevator.min_floor == 1
        assert elevator.max_floor == 10
        assert elevator.avail_capacity == 15
        assert elevator.is_empty

    def test_set_destination_floor_up(self, elevator: Elevator) -> None:
        """Test setting destination floor and direction updates"""
        # The elevator defaults to floor 1
        elevator.set_destination_floor(5)
        assert elevator.destination_floor == 5
        assert elevator.nominal_direction == VerticalDirection.UP
        
    def test_avail_capacity(self) -> None:
        pass

    def test_door_open_setter_and_getter(self) -> None:
        pass