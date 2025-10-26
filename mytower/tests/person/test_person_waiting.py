from unittest.mock import MagicMock

from mytower.game.core.types import PersonState
from mytower.game.core.units import Blocks, Time
from mytower.game.entities.person import Person


class TestPersonWaitingBehavior:
    """Test Person waiting and timeout behavior"""

    def test_idle_timeout_prevents_constant_checking(
        self, person_with_floor: Person, mock_building_with_floor: MagicMock
    ) -> None:
        """Test that idle timeout prevents person from constantly searching for elevators"""
        mock_building_with_floor.get_elevator_banks_on_floor.return_value = []

        person_with_floor.set_destination(dest_floor_num=8, dest_horiz_pos=Blocks(15.0))

        # First call should set timeout
        # The default idle timeout is 5.0 seconds (see Person.IDLE_TIMEOUT). 6.0 is used to ensure we are past the initial timeout.
        person_with_floor.update_idle(Time(6.0))
        assert person_with_floor.state == PersonState.IDLE

        # Subsequent calls within timeout should not search again
        person_with_floor.update_idle(Time(1.0))  # Still within new timeout period
        # get_elevator_banks_on_floor should only be called once from first update
        assert mock_building_with_floor.get_elevator_banks_on_floor.call_count == 1

    def test_waiting_time_affects_anger_color(self, person_with_floor: Person, mock_game_config: MagicMock) -> None:
        """Test that waiting time changes person's visual appearance (red component)"""
        # Test calm state (no waiting)
        person_with_floor.testing_set_wait_time(Time(0.0))
        red_calm: int = person_with_floor.draw_color_red
        assert red_calm <= 32  # Red component should be low

        # Test angry state (long waiting)
        person_with_floor.testing_set_wait_time(person_with_floor.testing_get_max_wait_time())  # Max wait time
        red_angry: int = person_with_floor.draw_color_red
        assert red_angry >= 150  # Red component should be high when angry
