# tests/person/test_person_floor_ownership.py
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from mytower.game.core.types import PersonState
from mytower.game.entities.person import Person


class TestPersonFloorOwnership:
    """Test Person floor ownership during elevator interactions"""

    def test_board_elevator_removes_from_current_floor(self, person_with_floor: Person) -> None:
        """Test that boarding elevator removes person from their current floor"""
        mock_elevator = MagicMock()
        mock_current_floor = MagicMock()

        # Setup: person is on a floor
        person_with_floor.testing_set_current_floor(mock_current_floor)

        person_with_floor.board_elevator(mock_elevator)

        # Should remove person from current floor
        mock_current_floor.remove_person.assert_called_once_with(person_with_floor.person_id)

        # Person should no longer have a current floor
        assert person_with_floor.current_floor is None
        assert person_with_floor.state == PersonState.IN_ELEVATOR

    def test_disembark_elevator_nonexistent_floor_raises_error(self, person_with_floor: Person, mock_building_with_floor: MagicMock) -> None:
        """Test that disembarking onto non-existent floor raises RuntimeError"""
        mock_elevator = MagicMock()
        mock_elevator.current_floor_int = 99  # Non-existent floor
        mock_elevator.parent_elevator_bank.get_waiting_position.return_value = 3

        # Building returns None for non-existent floor
        mock_building_with_floor.get_floor_by_number.return_value = None

        # Setup: person is in elevator
        person_with_floor.testing_set_current_state(PersonState.IN_ELEVATOR)
        person_with_floor.testing_set_current_elevator(mock_elevator)

        with pytest.raises(RuntimeError, match="Cannot disembark elevator: floor 99 does not exist"):
            person_with_floor.disembark_elevator()

    def test_floor_ownership_transfer_during_elevator_journey(self, person_with_floor: Person, mock_building_with_floor: MagicMock) -> None:
        """Test complete floor ownership transfer: floor A → elevator → floor B"""
        mock_elevator = MagicMock()
        mock_elevator.current_floor_int = 7
        mock_elevator.parent_elevator_bank.get_waiting_position.return_value = 5

        mock_origin_floor = MagicMock()
        mock_destination_floor = MagicMock()

        # Setup: person starts on origin floor
        person_with_floor.testing_set_current_floor(mock_origin_floor)

        # Step 1: Board elevator (should remove from origin floor)
        person_with_floor.board_elevator(mock_elevator)

        mock_origin_floor.remove_person.assert_called_once_with(person_with_floor.person_id)
        assert person_with_floor.current_floor is None
        assert person_with_floor.state == PersonState.IN_ELEVATOR

        # Step 2: Disembark elevator (should add to destination floor)
        person_with_floor.testing_set_current_state(PersonState.IN_ELEVATOR)  # Ensure correct state
        mock_building_with_floor.get_floor_by_number.return_value = mock_destination_floor

        person_with_floor.disembark_elevator()

        mock_destination_floor.add_person.assert_called_once_with(person_with_floor)
        assert person_with_floor.current_floor == mock_destination_floor
        assert person_with_floor.state == PersonState.IDLE

        # Verify no additional calls to origin floor
        pass  # Assertion moved to a separate test to avoid mypy unreachable warning

    def test_origin_floor_remove_person_called_once(self, person_with_floor: Person, mock_building_with_floor: MagicMock) -> None:
        """Test that remove_person is called exactly once on origin floor during elevator journey"""
        mock_elevator = MagicMock()
        mock_elevator.current_floor_int = 7
        mock_elevator.parent_elevator_bank.get_waiting_position.return_value = 5

        mock_origin_floor = MagicMock()
        mock_destination_floor = MagicMock()

        # Setup: person starts on origin floor
        person_with_floor.testing_set_current_floor(mock_origin_floor)

        # Board elevator (should remove from origin floor)
        person_with_floor.board_elevator(mock_elevator)

        # Disembark elevator (should add to destination floor)
        person_with_floor.testing_set_current_state(PersonState.IN_ELEVATOR)
        mock_building_with_floor.get_floor_by_number.return_value = mock_destination_floor
        person_with_floor.disembark_elevator()

        # Now check the call count
        assert mock_origin_floor.remove_person.call_count == 1


class TestPersonFloorOwnershipEdgeCases:
    """Test edge cases in floor ownership"""

    def test_board_elevator_floor_removal_fails_handled_gracefully(self, person_with_floor: Person) -> None:
        """Test behavior when floor removal fails during boarding"""
        mock_elevator = MagicMock()
        mock_current_floor = MagicMock()
        mock_current_floor.remove_person.side_effect = KeyError("Person not found")

        person_with_floor.testing_set_current_floor(mock_current_floor)

        # This might depend on your error handling strategy
        # For now, let's assume the KeyError should propagate
        with pytest.raises(KeyError):
            person_with_floor.board_elevator(mock_elevator)

    def test_disembark_elevator_floor_addition_fails_handled_gracefully(self, person_with_floor: Person, mock_building_with_floor: MagicMock) -> None:
        """Test behavior when floor addition fails during disembarking"""
        mock_elevator = MagicMock()
        mock_elevator.current_floor_int = 8
        mock_elevator.parent_elevator_bank.get_waiting_position.return_value = 3

        mock_destination_floor = MagicMock()
        mock_destination_floor.add_person.side_effect = Exception("Floor is full")  # Hypothetical error
        mock_building_with_floor.get_floor_by_number.return_value = mock_destination_floor

        person_with_floor.testing_set_current_state(PersonState.IN_ELEVATOR)
        person_with_floor.testing_set_current_elevator(mock_elevator)

        # Should propagate the floor addition error
        with pytest.raises(Exception, match="Floor is full"):
            person_with_floor.disembark_elevator()


class TestPersonCurrentFloorProperty:
    """Test the current_floor property behavior"""

    def test_current_floor_set_during_initialization_when_floor_exists(
        self,
        mock_building_with_floor: MagicMock,
        mock_game_config: MagicMock,
        mock_logger_provider: MagicMock
    ) -> None:
        """Test that current_floor gets set if building has the floor"""

        new_person = Person(
            logger_provider=mock_logger_provider,
            building=mock_building_with_floor,
            initial_floor_number=5,
            initial_horiz_position=10.0,
            config=mock_game_config
        )

        assert new_person.current_floor == mock_building_with_floor.get_floor_by_number.return_value
        mock_building_with_floor.get_floor_by_number.assert_called_with(5)