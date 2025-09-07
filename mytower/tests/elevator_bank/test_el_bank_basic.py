# tests/elevator_bank/test_basic.py
# import pytest
from collections import deque
from typing import Final
from unittest.mock import MagicMock

import pytest



from mytower.game.entities.elevator_bank import ElevatorBank
from mytower.game.entities.person import PersonProtocol
from mytower.game.core.types import VerticalDirection
# from mytower.game.types import VerticalDirection



class TestPassengerQueueing:
    def test_add_passenger_going_up(self, elevator_bank: ElevatorBank) -> None:
        # Test the most basic case - person going up gets added to up queue
        mock_person = MagicMock()
        mock_person.current_floor_num = 3
        mock_person.destination_floor_num = 7

        # Test passes if no exception raised (e.g., ValueError for invalid floor/direction)
        elevator_bank.add_waiting_passenger(mock_person)
        
        upward_queue: deque[PersonProtocol] = elevator_bank.testing_get_upward_queue(3)
        assert len(upward_queue) == 1
        assert upward_queue[0] is mock_person


        
    def test_add_passenger_going_down(self, elevator_bank: ElevatorBank) -> None:
        mock_person = MagicMock()
        mock_person.current_floor_num = 8
        mock_person.destination_floor_num = 2

        # Test passes if no exception raised
        elevator_bank.add_waiting_passenger(mock_person)
        
        # Person on floor 8 wanting to go down should be in floor 8's downward queue
        downward_queue: deque[PersonProtocol] = elevator_bank.testing_get_downward_queue(8)
        assert len(downward_queue) == 1
        assert downward_queue[0] is mock_person
        
        # Verify they're NOT in the upward queue (defensive check)
        upward_queue: deque[PersonProtocol] = elevator_bank.testing_get_upward_queue(8)
        assert len(upward_queue) == 0



    def test_add_passengers_both_directions_same_floor(self, elevator_bank: ElevatorBank) -> None:
        """Test that up/down passengers on same floor go to correct queues"""
        # Person going up from floor 5
        up_person = MagicMock()
        up_person.current_floor_num = 5
        up_person.destination_floor_num = 9

        # Person going down from floor 5
        down_person = MagicMock()
        down_person.current_floor_num = 5
        down_person.destination_floor_num = 2
        
        # Both operations should succeed without raising exceptions
        elevator_bank.add_waiting_passenger(up_person)
        elevator_bank.add_waiting_passenger(down_person)
        
        # Check they ended up in the right queues
        upward_queue: deque[PersonProtocol] = elevator_bank.testing_get_upward_queue(5)
        downward_queue: deque[PersonProtocol] = elevator_bank.testing_get_downward_queue(5)
        
        assert len(upward_queue) == 1
        assert len(downward_queue) == 1
        assert upward_queue[0] is up_person
        assert downward_queue[0] is down_person
        

    @pytest.mark.parametrize("current_floor_num,dest_floor_num,direction,queue_getter", [
        (4, 8, VerticalDirection.UP, "testing_get_upward_queue"),
        (8, 3, VerticalDirection.DOWN, "testing_get_downward_queue"),


    ])
    def test_dequeue_passenger_success(
        self, 
        elevator_bank: ElevatorBank, 
        current_floor_num: int, 
        dest_floor_num: int, 
        direction: VerticalDirection,
        queue_getter: str
    ) -> None:
        """Test successfully dequeuing passengers in both directions"""
        mock_person = MagicMock()
        mock_person.current_floor_num = current_floor_num
        mock_person.destination_floor_num = dest_floor_num

        elevator_bank.add_waiting_passenger(mock_person)
        
        # Act
        dequeued: PersonProtocol | None = elevator_bank.try_dequeue_waiting_passenger(current_floor_num, direction)
        
        # Assert
        assert dequeued is mock_person
        
        # Verify queue is now empty using the appropriate getter
        # this is comparable to `upward_queue = elevator_bank.testing_get_upward_queue(current_floor_num)`
        queue = getattr(elevator_bank, queue_getter)(current_floor_num)
        assert len(queue) == 0


    def test_dequeue_from_empty_queue_returns_none(self, elevator_bank: ElevatorBank) -> None:
        """Test that dequeuing from empty queue returns None"""
        result: PersonProtocol | None = elevator_bank.try_dequeue_waiting_passenger(3, VerticalDirection.UP)
        assert result is None



    def test_dequeue_wrong_direction_returns_none(self, elevator_bank: ElevatorBank) -> None:
        """Test dequeuing wrong direction from populated queue returns None"""
        # Add person going UP
        mock_person = MagicMock()
        mock_person.current_floor_num = 5
        mock_person.destination_floor_num = 9
        elevator_bank.add_waiting_passenger(mock_person)
        
        # Try to dequeue someone going DOWN from same floor
        result: PersonProtocol | None = elevator_bank.try_dequeue_waiting_passenger(5, VerticalDirection.DOWN)
        assert result is None
        
        # Original person should still be in UP queue
        upward_queue: deque[PersonProtocol] = elevator_bank.testing_get_upward_queue(5)
        assert len(upward_queue) == 1



    def test_dequeue_fifo_ordering(self, elevator_bank: ElevatorBank) -> None:
        """Test that passengers are dequeued in FIFO (first-in, first-out) order"""
        current_floor_num: Final[int] = 5
        
        # Add three passengers to the same queue
        first_person = MagicMock()
        first_person.current_floor_num = current_floor_num
        first_person.destination_floor_num = 9

        second_person = MagicMock()
        second_person.current_floor_num = current_floor_num
        second_person.destination_floor_num = 8

        third_person = MagicMock()
        third_person.current_floor_num = current_floor_num
        third_person.destination_floor_num = 7

        # Add them in order
        elevator_bank.add_waiting_passenger(first_person)
        elevator_bank.add_waiting_passenger(second_person)
        elevator_bank.add_waiting_passenger(third_person)
        
        # Dequeue should return them in the same order
        dequeued_1: PersonProtocol | None = elevator_bank.try_dequeue_waiting_passenger(current_floor_num, VerticalDirection.UP)
        dequeued_2: PersonProtocol | None = elevator_bank.try_dequeue_waiting_passenger(current_floor_num, VerticalDirection.UP)
        dequeued_3: PersonProtocol | None = elevator_bank.try_dequeue_waiting_passenger(current_floor_num, VerticalDirection.UP)
        
        assert dequeued_1 is first_person
        assert dequeued_2 is second_person
        assert dequeued_3 is third_person
        
        # Queue should now be empty
        upward_queue: deque[PersonProtocol] = elevator_bank.testing_get_upward_queue(current_floor_num)
        assert len(upward_queue) == 0


    @pytest.mark.parametrize("invalid_floor", [-1, 0, 11, 100])
    def test_dequeue_invalid_floor_raises_error(self, elevator_bank: ElevatorBank, invalid_floor: int) -> None:
        """Test that dequeuing from invalid floor numbers raises appropriate error"""
        # ElevatorBank is configured with floors 1-10, so these should be invalid
        with pytest.raises((KeyError, ValueError)):  # Not sure which exception it throws
            _ = elevator_bank.try_dequeue_waiting_passenger(invalid_floor, VerticalDirection.UP)