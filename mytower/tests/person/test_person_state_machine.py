from unittest.mock import MagicMock, patch
from mytower.game.person import Person
from mytower.game.types import PersonState



class TestPersonStateMachine:
    """Test Person state machine transitions and update logic"""


    
    def test_update_routes_to_correct_state_method(self, person_without_floor: Person) -> None:
        """Test that update() calls the correct state-specific method"""
        with patch.object(person_without_floor, 'update_idle') as mock_idle:
            person_without_floor.testing_set_current_state(PersonState.IDLE)
            person_without_floor.update(1.0)
            mock_idle.assert_called_once_with(1.0)
            
        with patch.object(person_without_floor, 'update_walking') as mock_walking:
            person_without_floor.testing_set_current_state(PersonState.WALKING)  
            person_without_floor.update(1.0)
            mock_walking.assert_called_once_with(1.0)


            
    def test_update_waiting_for_elevator_increments_time(self, person_without_floor: Person) -> None:
        """Test that waiting state increments waiting time"""
        person_without_floor.testing_set_current_state(PersonState.WAITING_FOR_ELEVATOR)
        person_without_floor.testing_set_wait_time(5.0)
        initial_wait_time: float = person_without_floor.testing_get_wait_time()
        
        person_without_floor.update(2.5)
        
        assert person_without_floor.testing_get_wait_time() == initial_wait_time + 2.5


        
    def test_update_in_elevator_follows_elevator_position(self, person_without_floor: Person) -> None:
        """Test that person in elevator updates position based on elevator"""
        mock_elevator = MagicMock()
        mock_elevator.fractional_floor = 6.7
        mock_elevator.parent_elevator_bank.horizontal_block = 12
        
        person_without_floor.testing_set_current_state(PersonState.IN_ELEVATOR)
        person_without_floor.testing_set_current_elevator(mock_elevator)
        
        person_without_floor.update(1.0)
        
        assert person_without_floor.testing_get_current_floor_float() == 6.7
        assert person_without_floor.current_block_float == 12

