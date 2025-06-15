

from mytower.game.elevator import Elevator, ElevatorState
from mytower.game.types import VerticalDirection

class TestStateMachine:
    
    def test_update_idle_stays_idle(self, elevator: Elevator) -> None:
        """Test transition from IDLE to MOVING state"""
        # Set up conditions for transition
        elevator.testing_set_state(ElevatorState.IDLE)
        elevator.set_destination_floor(5)  # Set a destination above current floor

        # Update the elevator
        elevator.update(1.0)

        # Check if state transitioned correctly
        assert elevator.state == ElevatorState.IDLE

    def test_update_ready_to_move_to_moving(self, elevator: Elevator) -> None:
        """Test transition from IDLE to MOVING state"""
        # Set up conditions for transition
        elevator.testing_set_state(ElevatorState.READY_TO_MOVE)
        elevator.set_destination_floor(5)  # Set a destination above current floor

        # Update the elevator
        elevator.update(1.0)

        # Check if state transitioned correctly
        assert elevator.state == ElevatorState.MOVING
        
    def test_update_ready_to_move_to_still_not_moving(self, elevator: Elevator) -> None:
        """Test transition from IDLE to MOVING state"""
        # Set up conditions for transition
        elevator.testing_set_state(ElevatorState.READY_TO_MOVE)
        elevator.set_destination_floor(1)  # Set a destination at same floor

        # Update the elevator
        elevator.update(1.0)

        # Check if state transitioned correctly
        assert elevator.state == ElevatorState.IDLE

    def test_update_moving_to_arrived(self, elevator: Elevator) -> None:
        """Test transition from MOVING to ARRIVED state when reaching destination"""
        # Set up conditions for transition
        elevator.testing_set_state(ElevatorState.MOVING)
        elevator.set_destination_floor(2)  # Set a destination
        elevator.testing_set_current_floor(1.9)  # Almost at destination
        elevator.testing_set_motion_direction(VerticalDirection.UP)

        # Update the elevator - should reach destination
        elevator.update(0.2)

        # Check if state transitioned correctly
        assert elevator.state == ElevatorState.ARRIVED
