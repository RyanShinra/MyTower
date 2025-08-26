from unittest.mock import MagicMock
import pytest
from mytower.game.person import Person
from mytower.game.types import PersonState


class TestPersonElevatorInteraction:
    """Test Person interactions with elevators"""
    
    def test_board_elevator_changes_state(self, person: Person) -> None:
        """Test that boarding elevator updates person state correctly"""
        mock_elevator = MagicMock()
        
        person.board_elevator(mock_elevator)
        
        assert person.state == PersonState.IN_ELEVATOR
        assert person.testing_get_wait_time() == 0.0
        assert person.testing_get_current_elevator() == mock_elevator
        
    def test_disembark_elevator_success(self, person: Person) -> None:
        """Test successful elevator disembarking"""
        mock_elevator = MagicMock()
        mock_elevator.current_floor_int = 8
        mock_elevator.parent_elevator_bank.get_waiting_block.return_value = 3
        
        # Set up person as if they're in elevator
        person.state = PersonState.IN_ELEVATOR
        person.testing_set_current_elevator(mock_elevator)
        
        person.disembark_elevator()
        
        assert person.state == PersonState.IDLE
        assert person.current_floor == 8
        assert person.current_block == 3
        assert person.testing_get_current_elevator() is None
        assert person.testing_get_next_elevator_bank() is None
        
    def test_disembark_elevator_not_in_elevator_raises_error(self, person: Person) -> None:
        """Test the /serious/ error that the character is in an elevator, but also not IN_ELEVATOR"""                
        mock_elevator = MagicMock()
        mock_elevator.current_floor_int = 8
        mock_elevator.parent_elevator_bank.get_waiting_block.return_value = 3
        
        person.testing_set_current_elevator(mock_elevator)
        person.state = PersonState.WALKING  # Wrong state
    
        with pytest.raises(RuntimeError, match="Cannot disembark elevator: person must be in elevator state"):
            person.disembark_elevator()
            
    def test_disembark_elevator_no_current_elevator_raises_error(self, person: Person) -> None:
        """Test the /serious/ error that the character thinks they are IN_ELEVATOR, but are in-fact, not (current elevator is NONE)"""
        person.state = PersonState.IN_ELEVATOR
        # No need to set _current_elevator = None as it's None by default
        
        with pytest.raises(RuntimeError, match="Cannot disembark elevator: no elevator is currently boarded"):
            person.disembark_elevator()

