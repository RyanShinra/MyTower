# test_el_bank_ready_elevator.py

from typing import Final
from unittest.mock import MagicMock

import pytest

from mytower.game.core.types import VerticalDirection
from mytower.game.entities.elevator_bank import ElevatorBank
from mytower.game.entities.entities_protocol import ElevatorDestination
from mytower.tests.conftest import PersonFactory


class TestReadyElevatorLogic:
    """Tests for the core elevator dispatch algorithm in _update_ready_elevator()"""

    def test_ready_elevator_prioritizes_passengers_when_no_closer_requests(
        self, elevator_bank: ElevatorBank, mock_elevator: MagicMock
    ) -> None:
        """Test that passengers get priority when there are no call requests closer than passenger destinations"""
        mock_elevator.current_floor_int = 5
        mock_elevator.nominal_direction = VerticalDirection.UP

        # Elevator has passengers wanting floor 7
        mock_elevator.get_passenger_destinations_in_direction.return_value = [7]

        # Call request exists but is farther away
        elevator_bank.request_elevator(9, VerticalDirection.UP)

        # Act
        elevator_bank.testing_update_ready_elevator(mock_elevator)

        # Should choose passenger destination (7) over farther call request (9)
        mock_elevator.set_destination.assert_called_once()
        call_args = mock_elevator.set_destination.call_args[0][0]
        assert call_args.floor == 7

    def test_ready_elevator_services_closest_destination_first(
        self, elevator_bank: ElevatorBank, mock_elevator: MagicMock, mock_person_factory: PersonFactory
    ) -> None:
        """Test that elevator services closest destination first (proper elevator behavior)"""
        mock_elevator.current_floor_int = 5
        mock_elevator.nominal_direction = VerticalDirection.UP

        # Set up: elevator has passengers wanting to go to floor 8
        mock_elevator.get_passenger_destinations_in_direction.return_value = [8]

        # And there's also a call request for floor 7 (closer)
        elevator_bank.request_elevator(7, VerticalDirection.UP)

        # Act
        elevator_bank.testing_update_ready_elevator(mock_elevator)

        # Assert: Should choose closest destination first (7), not skip to passenger destination (8)
        # This is correct elevator behavior - service requests along the way
        mock_elevator.set_destination.assert_called_once()
        call_args = mock_elevator.set_destination.call_args[0][0]
        assert call_args.floor == 7

        # Should clear the request we're fulfilling
        requests_floor_7 = elevator_bank.get_requests_for_floor(7)
        assert VerticalDirection.UP not in requests_floor_7

        # No request exists for floor 8 (passenger destination), so nothing to clear there
        requests_floor_8 = elevator_bank.get_requests_for_floor(8)
        assert len(requests_floor_8) == 0

    def test_ready_elevator_continues_journey_after_intermediate_stop(
        self, elevator_bank: ElevatorBank, mock_elevator: MagicMock
    ) -> None:
        """Test inductive logic: after serving floor 7, elevator would continue to 8"""
        # Simulate: elevator has now arrived at floor 7, served the request
        mock_elevator.current_floor_int = 7
        mock_elevator.nominal_direction = VerticalDirection.UP

        # Still has passengers wanting floor 8
        mock_elevator.get_passenger_destinations_in_direction.return_value = [8]

        # No more requests at current floor or below

        # Act
        elevator_bank.testing_update_ready_elevator(mock_elevator)

        # Assert: Should now continue to passenger destination
        mock_elevator.set_destination.assert_called_once()
        call_args = mock_elevator.set_destination.call_args[0][0]
        assert call_args.floor == 8

    def test_ready_elevator_continues_current_direction_when_possible(
        self, elevator_bank: ElevatorBank, mock_elevator: MagicMock
    ) -> None:
        """Test that elevator continues in current direction when destinations exist"""
        mock_elevator.current_floor_int = 5
        mock_elevator.nominal_direction = VerticalDirection.UP

        # No passengers in elevator
        mock_elevator.get_passenger_destinations_in_direction.return_value = []

        # But there are call requests in the UP direction
        elevator_bank.request_elevator(7, VerticalDirection.UP)
        elevator_bank.request_elevator(9, VerticalDirection.UP)

        elevator_bank.testing_update_ready_elevator(mock_elevator)

        # Should choose closest floor in travel direction (7, not 9)
        mock_elevator.set_destination.assert_called_once()
        call_args = mock_elevator.set_destination.call_args[0][0]
        assert call_args.floor == 7

        # Should clear the request for floor 7
        requests_floor_7: set[VerticalDirection] = elevator_bank.get_requests_for_floor(7)
        assert VerticalDirection.UP not in requests_floor_7

        # Should not clear the request for floor 9
        requests_floor_9: set[VerticalDirection] = elevator_bank.get_requests_for_floor(9)
        assert VerticalDirection.UP in requests_floor_9

    def test_ready_elevator_reverses_when_no_forward_destinations(
        self, elevator_bank: ElevatorBank, mock_elevator: MagicMock
    ) -> None:
        """Test that elevator reverses direction when no destinations in current direction"""
        mock_elevator.current_floor_int = 8
        mock_elevator.nominal_direction = VerticalDirection.UP

        # No passengers or requests going UP from floor 8
        mock_elevator.get_passenger_destinations_in_direction.return_value = []

        # But there are requests going DOWN
        elevator_bank.request_elevator(5, VerticalDirection.DOWN)
        elevator_bank.request_elevator(3, VerticalDirection.DOWN)

        elevator_bank.testing_update_ready_elevator(mock_elevator)

        # Should choose highest floor below us when going down (5, not 3)
        mock_elevator.set_destination.assert_called_once()
        call_args = mock_elevator.set_destination.call_args[0][0]
        assert call_args.floor == 5

    def test_ready_elevator_stays_put_when_no_destinations_anywhere(
        self, elevator_bank: ElevatorBank, mock_elevator: MagicMock
    ) -> None:
        """Test that elevator doesn't move when no destinations exist"""
        mock_elevator.current_floor_int = 5
        mock_elevator.nominal_direction = VerticalDirection.UP

        # No passengers in elevator
        mock_elevator.get_passenger_destinations_in_direction.return_value = []

        # No call requests anywhere

        elevator_bank.testing_update_ready_elevator(mock_elevator)

        # Should not set any destination
        mock_elevator.set_destination.assert_not_called()

    def test_ready_elevator_chooses_closest_floor_up_ignores_behind(
        self, elevator_bank: ElevatorBank, mock_elevator: MagicMock
    ) -> None:
        """Test UP direction: choose minimum above current floor, ignore floors behind"""
        mock_elevator.current_floor_int = 4
        mock_elevator.nominal_direction = VerticalDirection.UP
        mock_elevator.get_passenger_destinations_in_direction.return_value = []

        # Requests both above AND below current floor
        elevator_bank.request_elevator(2, VerticalDirection.UP)  # Below - should be ignored
        elevator_bank.request_elevator(6, VerticalDirection.UP)  # Above - closest
        elevator_bank.request_elevator(8, VerticalDirection.UP)  # Above - farther
        elevator_bank.request_elevator(7, VerticalDirection.UP)  # Above - middle

        elevator_bank.testing_update_ready_elevator(mock_elevator)

        # Should choose closest above (6), ignore request below (2)
        mock_elevator.set_destination.assert_called_once()
        call_args = mock_elevator.set_destination.call_args[0][0]
        assert call_args.floor == 6

        # Should clear only the request we're fulfilling
        requests_floor_6 = elevator_bank.get_requests_for_floor(6)
        assert VerticalDirection.UP not in requests_floor_6

        # Other requests should remain
        assert VerticalDirection.UP in elevator_bank.get_requests_for_floor(2)
        assert VerticalDirection.UP in elevator_bank.get_requests_for_floor(7)
        assert VerticalDirection.UP in elevator_bank.get_requests_for_floor(8)

    def test_ready_elevator_chooses_closest_floor_down_ignores_ahead(
        self, elevator_bank: ElevatorBank, mock_elevator: MagicMock
    ) -> None:
        """Test DOWN direction: choose maximum below current floor, ignore floors ahead"""
        mock_elevator.current_floor_int = 8
        mock_elevator.nominal_direction = VerticalDirection.DOWN
        mock_elevator.get_passenger_destinations_in_direction.return_value = []

        # Requests both below AND above current floor
        elevator_bank.request_elevator(10, VerticalDirection.DOWN)  # Above - should be ignored
        elevator_bank.request_elevator(3, VerticalDirection.DOWN)  # Below - farther
        elevator_bank.request_elevator(5, VerticalDirection.DOWN)  # Below - closest
        elevator_bank.request_elevator(2, VerticalDirection.DOWN)  # Below - farthest

        elevator_bank.testing_update_ready_elevator(mock_elevator)

        # Should choose closest below (5), ignore request above (10)
        mock_elevator.set_destination.assert_called_once()
        call_args = mock_elevator.set_destination.call_args[0][0]
        assert call_args.floor == 5

        # Should clear only the request we're fulfilling
        requests_floor_5 = elevator_bank.get_requests_for_floor(5)
        assert VerticalDirection.DOWN not in requests_floor_5

        # Other requests should remain
        assert VerticalDirection.DOWN in elevator_bank.get_requests_for_floor(10)
        assert VerticalDirection.DOWN in elevator_bank.get_requests_for_floor(3)
        assert VerticalDirection.DOWN in elevator_bank.get_requests_for_floor(2)

    def test_ready_elevator_mixed_passengers_and_requests(
        self, elevator_bank: ElevatorBank, mock_elevator: MagicMock
    ) -> None:
        """Test complex scenario with both passenger destinations and call requests"""
        mock_elevator.current_floor_int = 5
        mock_elevator.nominal_direction = VerticalDirection.UP

        # Elevator has passengers wanting floors 7 and 9
        mock_elevator.get_passenger_destinations_in_direction.return_value = [7, 9]

        # Also call requests for floors 6 and 8
        elevator_bank.request_elevator(6, VerticalDirection.UP)
        elevator_bank.request_elevator(8, VerticalDirection.UP)

        elevator_bank.testing_update_ready_elevator(mock_elevator)

        # Should choose closest overall destination (6 - call request)
        mock_elevator.set_destination.assert_called_once()
        call_args = mock_elevator.set_destination.call_args[0][0]
        assert call_args.floor == 6

        # Should clear the request we're fulfilling
        requests_floor_6 = elevator_bank.get_requests_for_floor(6)
        assert VerticalDirection.UP not in requests_floor_6

    def test_ready_elevator_direction_reversal_to_stationary_bias(
        self, elevator_bank: ElevatorBank, mock_elevator: MagicMock
    ) -> None:
        """Test that STATIONARY direction gets biased to UP when reversing"""
        mock_elevator.current_floor_int = 5
        mock_elevator.nominal_direction = VerticalDirection.STATIONARY
        mock_elevator.get_passenger_destinations_in_direction.return_value = []

        # Only requests going down
        elevator_bank.request_elevator(3, VerticalDirection.DOWN)

        elevator_bank.testing_update_ready_elevator(mock_elevator)

        # Should find the DOWN request even though we started STATIONARY
        mock_elevator.set_destination.assert_called_once()
        call_args = mock_elevator.set_destination.call_args[0][0]
        assert call_args.floor == 3

    def test_ready_elevator_clears_correct_request(self, elevator_bank: ElevatorBank, mock_elevator: MagicMock) -> None:
        """Test that only the request being fulfilled gets cleared"""
        mock_elevator.current_floor_int = 5
        mock_elevator.nominal_direction = VerticalDirection.UP
        mock_elevator.get_passenger_destinations_in_direction.return_value = []

        # Set up multiple requests
        elevator_bank.request_elevator(7, VerticalDirection.UP)
        elevator_bank.request_elevator(7, VerticalDirection.DOWN)  # Same floor, different direction
        elevator_bank.request_elevator(8, VerticalDirection.UP)

        elevator_bank.testing_update_ready_elevator(mock_elevator)

        # Should go to floor 7 (closest)
        mock_elevator.set_destination.assert_called_once()
        call_args = mock_elevator.set_destination.call_args[0][0]
        assert call_args.floor == 7

        # Should clear UP request for floor 7, but not DOWN request
        requests_floor_7: set[VerticalDirection] = elevator_bank.get_requests_for_floor(7)
        assert VerticalDirection.UP not in requests_floor_7
        assert VerticalDirection.DOWN in requests_floor_7  # Should still exist

        # Floor 8 request should be untouched
        requests_floor_8: set[VerticalDirection] = elevator_bank.get_requests_for_floor(8)
        assert VerticalDirection.UP in requests_floor_8


class TestDestinationCollection:
    """Test the helper methods used by ready elevator logic"""

    def test_collect_destinations_passengers_first(self, elevator_bank: ElevatorBank, mock_elevator: MagicMock) -> None:
        """Test that _collect_destinations includes passenger destinations first"""
        mock_elevator.get_passenger_destinations_in_direction.return_value = [7, 9]

        # Also some call requests
        elevator_bank.request_elevator(6, VerticalDirection.UP)
        elevator_bank.request_elevator(8, VerticalDirection.UP)

        # Use the actual method (assuming you add a testing accessor)
        destinations: Final[list[ElevatorDestination]] = elevator_bank.testing_collect_destinations(
            mock_elevator, floor=5, direction=VerticalDirection.UP
        )

        # Should include both passenger destinations and call requests
        # Extract floors for easier checking
        destination_floors = [dest.floor for dest in destinations]
        assert 7 in destination_floors  # Passenger
        assert 9 in destination_floors  # Passenger
        assert 6 in destination_floors  # Call request
        assert 8 in destination_floors  # Call request

    @pytest.mark.parametrize(
        "direction,floors,expected",
        [
            (VerticalDirection.UP, [6, 8, 7], 6),  # UP: choose minimum
            (VerticalDirection.DOWN, [3, 5, 2], 5),  # DOWN: choose maximum
            (VerticalDirection.UP, [10], 10),  # Single destination
        ],
    )
    def test_select_next_floor_logic(
        self, elevator_bank: ElevatorBank, direction: VerticalDirection, floors: list[int], expected: int
    ) -> None:
        """Test floor selection logic for different directions"""
        # Convert floors to ElevatorDestination objects
        destinations = [ElevatorDestination(floor, direction, True) for floor in floors]
        result = elevator_bank.testing_select_next_floor(destinations, direction)
        assert result.floor == expected


class TestRequestClearing:
    """Test that requests get properly cleared when elevators are assigned"""

    def test_request_cleared_after_destination_set(self, elevator_bank: ElevatorBank, mock_elevator: MagicMock) -> None:
        """Integration test: request should be cleared after elevator is assigned"""
        mock_elevator.current_floor_int = 3
        mock_elevator.nominal_direction = VerticalDirection.UP
        mock_elevator.get_passenger_destinations_in_direction.return_value = []

        # Set up request
        elevator_bank.request_elevator(5, VerticalDirection.UP)
        assert VerticalDirection.UP in elevator_bank.get_requests_for_floor(5)

        # Process the ready elevator
        elevator_bank.testing_update_ready_elevator(mock_elevator)

        # Request should be cleared
        requests: set[VerticalDirection] = elevator_bank.get_requests_for_floor(5)
        assert VerticalDirection.UP not in requests
        assert len(requests) == 0

    def test_only_fulfilled_request_cleared(self, elevator_bank: ElevatorBank, mock_elevator: MagicMock) -> None:
        """Test that only the specific request being fulfilled gets cleared"""
        mock_elevator.current_floor_int = 3
        mock_elevator.nominal_direction = VerticalDirection.UP
        mock_elevator.get_passenger_destinations_in_direction.return_value = []

        # Set up multiple requests on same floor
        elevator_bank.request_elevator(5, VerticalDirection.UP)
        elevator_bank.request_elevator(5, VerticalDirection.DOWN)

        elevator_bank.testing_update_ready_elevator(mock_elevator)

        # Only UP request should be cleared (that's the direction we're going)
        requests: set[VerticalDirection] = elevator_bank.get_requests_for_floor(5)
        assert VerticalDirection.UP not in requests
        assert VerticalDirection.DOWN in requests
