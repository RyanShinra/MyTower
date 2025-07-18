from typing import Callable, List, Sequence
from unittest.mock import MagicMock  # , # patch

from typing import Final
import pytest

from mytower.game.elevator import Elevator, ElevatorState
from mytower.game.types import VerticalDirection
from mytower.tests.elevator.conftest import PersonProtocol


class TestPassengers:
    
    def test_passengers_who_want_off_current_floor(
        self, elevator: Elevator, mock_person_factory: Callable[[int], MagicMock]
    ) -> None:
        """Test filtering passengers by destination floor"""
        # Elevator starts on floor one (see test_initial_state above)
        passenger_current_floor: PersonProtocol = mock_person_factory(1)
        passenger_another_floor: PersonProtocol = mock_person_factory(5)

        elevator.testing_set_passengers([passenger_another_floor, passenger_current_floor])
        who_wants_off: List[PersonProtocol] = elevator.passengers_who_want_off()

        assert len(who_wants_off) == 1
        assert who_wants_off[0] == passenger_current_floor

    @pytest.mark.parametrize(
        "current_floor,direction,expected_floors",
        [
            (3, VerticalDirection.UP, [5, 7]),
            (5, VerticalDirection.DOWN, [3, 1]),
            (2, VerticalDirection.STATIONARY, []),
            (1, VerticalDirection.DOWN, []),  # At min floor going down
            (7, VerticalDirection.UP, []),  # At max floor going up
            (4, VerticalDirection.UP, [5, 7]),  # From middle floor
        ],
    )
    def test_get_passenger_destinations_by_direction(
        self,
        elevator: Elevator,
        mock_person_factory: Callable[[int], MagicMock],
        current_floor: int,
        direction: VerticalDirection,
        expected_floors: List[int],
    ) -> None:
        """Test getting sorted destinations in the direction of 'direction' """
        elevator.testing_set_current_floor(current_floor)
        dest_floors: List[int] = [1, 3, 5, 7]

        passengers: Sequence[PersonProtocol] = [mock_person_factory(floor) for floor in dest_floors]
        elevator.testing_set_passengers(passengers)

        actual_floors: List[int] = elevator.get_passenger_destinations_in_direction(current_floor, direction)
        assert expected_floors == actual_floors

    def test_passengers_boarding(self, elevator: Elevator, mock_elevator_bank: MagicMock) -> None:
        """Test passengers boarding the elevator"""
        # Create a mock person
        mock_person = MagicMock()
        mock_person.destination_floor = 5

        # Setup elevator bank to return our mock person
        mock_elevator_bank.try_dequeue_waiting_passenger.return_value = mock_person

        # Set elevator to loading state and update
        elevator.testing_set_state(ElevatorState.LOADING)
        elevator.testing_set_nominal_direction(VerticalDirection.UP)
        elevator.update(1.1)  # Time > passenger_loading_time

        # Check that the passenger was added
        current_passengers: Final[List[PersonProtocol]] = elevator.testing_get_passengers()
        assert len(current_passengers) == 1
        assert current_passengers[0] == mock_person

        # Check that elevator asked bank for passenger with correct params
        mock_elevator_bank.try_dequeue_waiting_passenger.assert_called_with(
            elevator.current_floor_int, VerticalDirection.UP
        )

    def test_request_load_passengers_valid_state(self, elevator: Elevator) -> None:
        """Test request_load_passengers works from IDLE state"""
        elevator.testing_set_state(ElevatorState.IDLE)
        
        elevator.request_load_passengers(VerticalDirection.UP)
        
        assert elevator.state == ElevatorState.LOADING
        assert elevator.nominal_direction == VerticalDirection.UP

    def test_request_load_passengers_invalid_state(self, elevator: Elevator) -> None:
        """Test request_load_passengers raises exception from non-IDLE state"""
        elevator.testing_set_state(ElevatorState.MOVING)  # Pick one representative invalid state
        
        with pytest.raises(RuntimeError, match=".*Cannot load passengers while elevator is in .* state"):
            elevator.request_load_passengers(VerticalDirection.UP)
            
    def test_update_arrived_with_passengers_wanting_off(self, elevator: Elevator, mock_person_factory: Callable[[int], PersonProtocol]) -> None:
        # Setup: elevator arrives at floor 3 with passengers going to floor 3
        elevator.testing_set_state(ElevatorState.ARRIVED)
        elevator.testing_set_current_floor(3.0)
        
        passengers = [
            mock_person_factory(3),  # Wants off here
            mock_person_factory(5),  # Doesn't want off
        ]
        elevator.testing_set_passengers(passengers)
        
        # Act
        elevator.update(0.1)  # dt doesn't matter for this method
        
        # Assert
        assert elevator.state == ElevatorState.UNLOADING