# test_el_bank_state_machine.py 

from unittest.mock import MagicMock




from mytower.game.entities.elevator_bank import ElevatorBank
from mytower.game.core.types import VerticalDirection
from mytower.tests.conftest import PersonFactory



class TestIdleElevatorLogic:
    def test_idle_elevator_waits_when_timeout_not_reached(self, elevator_bank: ElevatorBank, mock_elevator: MagicMock) -> None:
        """Test that idle elevator doesn't do anything when idle_time < idle_wait_timeout"""
        
        # Set up: elevator has been idle for 0.3 seconds, timeout is 0.5
        mock_elevator.idle_time = 0.3
        mock_elevator.idle_wait_timeout = 0.5
        
        # Act: simulate 0.1 seconds passing (still under timeout)
        elevator_bank.testing_update_idle_elevator(mock_elevator, 0.1)
        
        # Assert: idle_time increases but no other actions taken
        assert mock_elevator.idle_time == 0.4
        mock_elevator.request_load_passengers.assert_not_called()

    
    
    def test_idle_elevator_loads_waiting_passengers_same_floor(self, elevator_bank: ElevatorBank, mock_elevator: MagicMock, mock_person_factory: PersonFactory) -> None:
        """Test that elevator loads passengers from the floor it is currently at, but none others"""
        
        mock_elevator.current_floor_int = 5
        mock_elevator.idle_time = 0.6 # It's been waiting longer than the idle time-out
        mock_elevator.idle_wait_timeout = 0.5 # A real elevator would probably sit idle for more than 500ms before trying to load passengers

        elevator_bank.add_waiting_passenger(mock_person_factory(cur_floor_num=5, dest_floor_num=8))
        assert len(elevator_bank.testing_get_upward_queue(5))  == 1 # Make sure this is set before we run the test
        
        elevator_bank.testing_update_idle_elevator(mock_elevator, 0.1) # 100 ms
        
        # Only one passenger (or floor?) either way, it should only be called once
        mock_elevator.request_load_passengers.assert_called_once_with(VerticalDirection.UP)        


        
    def test_idle_elevator_moves_to_request_when_no_local_passengers(self, elevator_bank: ElevatorBank, mock_elevator: MagicMock) -> None:
        """Test that idle elevator looks for requests on other floors when no local passengers"""
        mock_elevator.current_floor_int = 5
        mock_elevator.idle_time = 0.6  # Past timeout
        mock_elevator.idle_wait_timeout = 0.5
        mock_elevator.nominal_direction = VerticalDirection.UP
        
        # No passengers waiting on floor 5, but request on floor 8
        elevator_bank.request_elevator(8, VerticalDirection.UP)
        
        elevator_bank.testing_update_idle_elevator(mock_elevator, 0.1)
        
        # Should not try to load passengers locally
        mock_elevator.request_load_passengers.assert_not_called()
        # Should set destination to floor 8
        mock_elevator.set_destination_floor.assert_called_once_with(8)


        
    def test_idle_elevator_stays_idle_when_no_passengers_or_requests(self, elevator_bank: ElevatorBank, mock_elevator: MagicMock) -> None:
        """Test that idle elevator does nothing when no passengers or requests exist"""
        mock_elevator.current_floor_int = 5
        mock_elevator.idle_time = 0.6  # Past timeout
        mock_elevator.idle_wait_timeout = 0.5
        
        # No passengers, no requests anywhere
        
        elevator_bank.testing_update_idle_elevator(mock_elevator, 0.1)
        
        mock_elevator.request_load_passengers.assert_not_called()
        mock_elevator.set_destination_floor.assert_not_called()


        
    def test_idle_elevator_continues_checking_after_reset(self, elevator_bank: ElevatorBank, mock_elevator: MagicMock) -> None:
        # First cycle - past timeout, nothing to do
        mock_elevator.idle_time = 0.6
        elevator_bank.testing_update_idle_elevator(mock_elevator, 0.1)
        assert mock_elevator.idle_time == 0.0
        
        # Second cycle - accumulating time again
        elevator_bank.testing_update_idle_elevator(mock_elevator, 0.3)
        assert mock_elevator.idle_time == 0.3  # Should be accumulating again


        
    def test_idle_elevator_resets_timer_when_no_destinations(self, elevator_bank: ElevatorBank, mock_elevator: MagicMock) -> None:
        mock_elevator.idle_time = 0.6  # Past timeout
        mock_elevator.idle_wait_timeout = 0.5
        
        # No passengers, no requests
        elevator_bank.testing_update_idle_elevator(mock_elevator, 0.1)
        
        # idle_time should be reset to 0 (restarting the idle loop)
        assert mock_elevator.idle_time == 0.0        