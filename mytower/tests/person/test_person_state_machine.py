from unittest.mock import MagicMock, patch
from mytower.game.core.units import Time
from mytower.game.entities.person import Person
from mytower.game.core.types import PersonState



class TestPersonStateMachine:
    """Test Person state machine transitions and update logic"""

    
    def test_update_routes_to_correct_state_method(self, person_with_floor: Person) -> None:
        """Test that update() calls the correct state-specific method"""
        with patch.object(person_with_floor, 'update_idle') as mock_idle:
            person_with_floor.testing_set_current_state(PersonState.IDLE)
            person_with_floor.update(Time(1.0))
            mock_idle.assert_called_once_with(Time(1.0))

        with patch.object(person_with_floor, 'update_walking') as mock_walking:
            person_with_floor.testing_set_current_state(PersonState.WALKING)  
            person_with_floor.update(Time(1.0))
            mock_walking.assert_called_once_with(Time(1.0))

            
    def test_update_waiting_for_elevator_increments_time(self, person_with_floor: Person) -> None:
        """Test that waiting state increments waiting time"""
        person_with_floor.testing_set_current_state(PersonState.WAITING_FOR_ELEVATOR)
        person_with_floor.testing_set_wait_time(Time(5.0))
        initial_wait_time: Time = person_with_floor.testing_get_wait_time()

        person_with_floor.update(Time(2.5))

        assert person_with_floor.testing_get_wait_time() == initial_wait_time + Time(2.5)

        
    def test_update_in_elevator_follows_elevator_position(self, person_with_floor: Person) -> None:
        """Test that person in elevator updates position based on elevator"""
        mock_elevator = MagicMock()
        mock_elevator.vertical_position = 6.7
        mock_elevator.parent_elevator_bank.horizontal_position = 12
        
        person_with_floor.testing_set_current_state(PersonState.IN_ELEVATOR)
        person_with_floor.testing_set_current_elevator(mock_elevator)
        
        person_with_floor.update(Time(1.0))
        
        assert person_with_floor.testing_get_current_vertical_position() == 6.7
        assert person_with_floor.current_horizontal_position == 12

