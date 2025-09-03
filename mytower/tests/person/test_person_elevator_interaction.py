from unittest.mock import MagicMock
import pytest
from mytower.game.person import Person
from mytower.game.types import PersonState



class TestPersonElevatorInteraction:
    """Test Person interactions with elevators"""



    def test_board_elevator_changes_state(self, person_with_floor: Person) -> None:
        """Test that boarding elevator updates person state correctly"""
        mock_elevator = MagicMock()
        
        person_with_floor.board_elevator(mock_elevator)

        assert person_with_floor.state == PersonState.IN_ELEVATOR
        assert person_with_floor.testing_get_wait_time() == 0.0
        assert person_with_floor.testing_get_current_elevator() == mock_elevator



    def test_disembark_elevator_success(self, person: Person) -> None:
        """Test successful elevator disembarking"""
        mock_elevator = MagicMock()
        mock_elevator.current_floor_int = 5
        mock_elevator.parent_elevator_bank.get_waiting_block.return_value = 3
        
        # Set up person as if they're in elevator (This person version doesn't have a floor)
        person.testing_set_current_state(PersonState.IN_ELEVATOR)
        person.testing_set_current_elevator(mock_elevator)

        # The building is a mock, see the conftest.py
        mock_floor = MagicMock()
        person.building.get_floor_by_number.return_value = mock_floor  # type: ignore

        person.disembark_elevator()
        
        assert person.state == PersonState.IDLE
        assert person.current_floor == mock_floor
        assert person.current_floor_num == 5
        assert person.current_block_float == 3
        mock_floor.add_person.assert_called_once_with(person)
        assert person.testing_get_current_elevator() is None
        assert person.testing_get_next_elevator_bank() is None
        assert person.testing_get_wait_time() == 0.0


    def test_disembark_elevator_not_in_elevator_raises_error(self, person: Person) -> None:
        """Test that a RuntimeError is raised when a person has a current elevator but is not in the IN_ELEVATOR state and attempts to disembark."""                
        mock_elevator = MagicMock()
        mock_elevator.current_floor_int = 8
        mock_elevator.parent_elevator_bank.get_waiting_block.return_value = 3
        
        person.testing_set_current_elevator(mock_elevator)
        person.testing_set_current_state(PersonState.WALKING)  # Wrong state
    
        with pytest.raises(RuntimeError, match="Cannot disembark elevator: person must be in elevator state"):
            person.disembark_elevator()


            
    def test_disembark_elevator_no_current_elevator_raises_error(self, person: Person) -> None:
        """Test that an error is raised when a person is in IN_ELEVATOR state but has no current elevator assigned."""
        person.testing_set_current_state(PersonState.IN_ELEVATOR)
        # No need to set _current_elevator = None as it's None by default
        
        with pytest.raises(RuntimeError, match="Cannot disembark elevator: no elevator is currently boarded"):
            person.disembark_elevator()

