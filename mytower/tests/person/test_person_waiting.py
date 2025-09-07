from unittest.mock import MagicMock, patch
from mytower.game.entities.person import Person
from mytower.game.core.types import PersonState



class TestPersonWaitingBehavior:
    """Test Person waiting and timeout behavior"""


    
    def test_idle_timeout_prevents_constant_checking(self, person_without_floor: Person, mock_building_no_floor: MagicMock) -> None:
        """Test that idle timeout prevents person from constantly searching for elevators"""
        mock_building_no_floor.get_elevator_banks_on_floor.return_value = []
        
        person_without_floor.set_destination(dest_floor_num=8, dest_block_num=15)
        
        # First call should set timeout
        # The default idle timeout is 5.0 seconds (see Person.IDLE_TIMEOUT). 6.0 is used to ensure we are past the initial timeout.
        person_without_floor.update_idle(6.0)
        assert person_without_floor.state == PersonState.IDLE
        
        # Subsequent calls within timeout should not search again
        person_without_floor.update_idle(1.0)  # Still within new timeout period
        # get_elevator_banks_on_floor should only be called once from first update
        assert mock_building_no_floor.get_elevator_banks_on_floor.call_count == 1


        
    def test_waiting_time_affects_anger_color(self, person_without_floor: Person, mock_game_config: MagicMock) -> None:
        """Test that waiting time changes person's visual appearance"""
        # Mock pygame surface for drawing
        mock_surface = MagicMock()
        mock_surface.get_height.return_value = 600
        
        # Test calm state (no waiting)
        person_without_floor.testing_set_wait_time(0.0)
        with patch('pygame.draw.circle') as mock_draw:
            person_without_floor.draw(mock_surface)
            # Color should be close to original (low red values)
            color = mock_draw.call_args[0][1]  # Second argument is color
            assert color[0] <= 32  # Red component should be low
            
        # Test angry state (long waiting)  
        person_without_floor.testing_set_wait_time(person_without_floor.testing_get_max_wait_time())  # Max wait time
        with patch('pygame.draw.circle') as mock_draw:
            person_without_floor.draw(mock_surface)
            color = mock_draw.call_args[0][1]
            assert color[0] >= 150  # Red component should be high when angry
