

from mytower.game.core.units import Blocks, Time
from mytower.game.entities.elevator import Elevator, ElevatorState
from mytower.game.core.types import VerticalDirection
from mytower.game.entities.entities_protocol import ElevatorDestination


class TestStateMachine:

    def test_update_idle_stays_idle(self, elevator: Elevator) -> None:
        """Test that IDLE elevator transitions to MOVING when destination is set"""
        # Set up conditions for transition
        elevator.testing_set_state(ElevatorState.IDLE)
        destination = ElevatorDestination(floor=5, direction=VerticalDirection.UP, has_destination=True)
        elevator.set_destination(destination)  # Set a destination above current floor - this changes state to READY_TO_MOVE

        # Update the elevator
        elevator.update(Time(1.0))

        # Check if state transitioned correctly - should be MOVING now
        assert elevator.elevator_state == ElevatorState.MOVING

    def test_update_ready_to_move_to_moving(self, elevator: Elevator) -> None:
        """Test transition from IDLE to MOVING state"""
        # Set up conditions for transition
        elevator.testing_set_state(ElevatorState.READY_TO_MOVE)
        destination = ElevatorDestination(floor=5, direction=VerticalDirection.UP, has_destination=True)
        elevator.set_destination(destination)  # Set a destination above current floor

        # Update the elevator
        elevator.update(Time(1.0))

        # Check if state transitioned correctly
        assert elevator.elevator_state == ElevatorState.MOVING

    def test_update_ready_to_move_to_still_not_moving(self, elevator: Elevator) -> None:
        """Test transition from IDLE to MOVING state"""
        # Set up conditions for transition
        elevator.testing_set_state(ElevatorState.READY_TO_MOVE)
        destination = ElevatorDestination(floor=1, direction=VerticalDirection.STATIONARY, has_destination=True)
        elevator.set_destination(destination)  # Set a destination at same floor

        # Update the elevator
        elevator.update(Time(1.0))

        # Check if state transitioned correctly
        assert elevator.elevator_state == ElevatorState.IDLE

    def test_update_moving_to_arrived(self, elevator: Elevator) -> None:
        """Test transition from MOVING to ARRIVED state when reaching destination"""
        # Set up conditions for transition
        destination = ElevatorDestination(floor=2, direction=VerticalDirection.UP, has_destination=True)
        elevator.set_destination(destination)  # Set a destination - this sets state to READY_TO_MOVE
        elevator.testing_set_current_vertical_pos(Blocks(1.9))  # Almost at destination
        elevator.testing_set_motion_direction(VerticalDirection.UP)
        elevator.testing_set_state(ElevatorState.MOVING)  # Now set to MOVING after position/destination set

        # Update the elevator - should reach destination
        elevator.update(Time(0.2))

        # Check if state transitioned correctly
        assert elevator.elevator_state == ElevatorState.ARRIVED
