from unittest.mock import MagicMock
import pytest
from mytower.game.entities.person import Person
from mytower.game.core.types import PersonState
from mytower.tests.test_utilities import TypedMockFactory, StateAssertions



class TestPersonElevatorInteraction:
    """Test Person interactions with elevators"""



    def test_board_elevator_changes_state(
        self, 
        person_with_floor: Person, 
        typed_mock_factory: TypedMockFactory,
        state_assertions: StateAssertions
    ) -> None:
        """Test that boarding elevator updates person state correctly"""
        mock_elevator = typed_mock_factory.create_elevator_mock()
        
        person_with_floor.board_elevator(mock_elevator)

        state_assertions.assert_person_state(
            person_with_floor, 
            expected_state=PersonState.IN_ELEVATOR
        )
        assert person_with_floor.testing_get_wait_time() == 0.0
        assert person_with_floor.testing_get_current_elevator() == mock_elevator



    def test_disembark_elevator_success(
        self, 
        person_with_floor: Person,
        typed_mock_factory: TypedMockFactory,
        state_assertions: StateAssertions
    ) -> None:
        """Test successful elevator disembarking"""
        mock_elevator = typed_mock_factory.create_elevator_mock(
            current_floor=5
        )
        mock_elevator.parent_elevator_bank.get_waiting_block.return_value = 3
        
        # Set up person as if they're in elevator
        person_with_floor.testing_set_current_state(PersonState.IN_ELEVATOR)
        person_with_floor.testing_set_current_elevator(mock_elevator)

        # The building is a mock, see the conftest.py
        mock_floor = typed_mock_factory.create_floor_mock(floor_num=5)
        person_with_floor.building.get_floor_by_number.return_value = mock_floor  # type: ignore

        person_with_floor.disembark_elevator()
        
        # Use state assertions for cleaner testing
        state_assertions.assert_person_state(
            person_with_floor,
            expected_state=PersonState.IDLE,
            expected_floor=5,
            expected_block=3.0
        )
        
        assert person_with_floor.current_floor == mock_floor
        mock_floor.add_person.assert_called_once_with(person_with_floor)
        assert person_with_floor.testing_get_current_elevator() is None
        assert person_with_floor.testing_get_next_elevator_bank() is None
        assert person_with_floor.testing_get_wait_time() == 0.0


    def test_disembark_elevator_not_in_elevator_raises_error(self, person_with_floor: Person) -> None:
        """Test that a RuntimeError is raised when a person has a current elevator but is not in the IN_ELEVATOR state and attempts to disembark."""                
        mock_elevator = MagicMock()
        mock_elevator.current_floor_int = 8
        mock_elevator.parent_elevator_bank.get_waiting_block.return_value = 3
        
        person_with_floor.testing_set_current_elevator(mock_elevator)
        person_with_floor.testing_set_current_state(PersonState.WALKING)  # Wrong state
    
        with pytest.raises(RuntimeError, match="Cannot disembark elevator: person must be in elevator state"):
            person_with_floor.disembark_elevator()


            
    def test_disembark_elevator_no_current_elevator_raises_error(self, person_with_floor: Person) -> None:
        """Test that an error is raised when a person is in IN_ELEVATOR state but has no current elevator assigned."""
        person_with_floor.testing_set_current_state(PersonState.IN_ELEVATOR)
        # No need to set _current_elevator = None as it's None by default
        
        with pytest.raises(RuntimeError, match="Cannot disembark elevator: no elevator is currently boarded"):
            person_with_floor.disembark_elevator()

