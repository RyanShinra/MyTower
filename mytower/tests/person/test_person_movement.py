from __future__ import annotations
from typing import Final
from unittest.mock import MagicMock

from mytower.game.elevator_bank import ElevatorBank
from mytower.game.person import Person
from mytower.game.types import PersonState, HorizontalDirection
import math

class TestPersonMovement:
    """Test Person movement and path finding logic"""
    
    def test_no_movement_when_already_at_destination(self, person: Person) -> None:
        """Test that person stays idle when already at destination"""
        # Use the person's current location as their destination 
        original_floor: Final[int] = person.current_floor
        original_block: Final[int] = math.floor(person.current_block)
        
        person.set_destination(dest_floor=original_floor, dest_block=original_block)
        
        person.update_idle(1.0)
        
        # Should stay idle since already on correct floor
        assert person.state == PersonState.IDLE
        assert person.direction == HorizontalDirection.STATIONARY
        assert person.current_block == original_block
        assert person.current_floor == original_floor
        
        
    def test_update_idle_different_floor_no_elevator(self, person: Person, mock_building: MagicMock) -> None:
        """Test person behavior when needing different floor but no elevator available"""
        mock_building.get_elevator_banks_on_floor.return_value = []  # No elevators
        
        person.set_destination(dest_floor=8, dest_block=15)
        person.update_idle(6.0)  # Past idle timeout
        
        # Should stay idle since no elevator available
        assert person.state == PersonState.IDLE
        
        
    def test_update_idle_finds_elevator_starts_walking(self, person: Person, mock_building: MagicMock) -> None:
        """Test that person starts walking toward elevator when one is available"""
        mock_elevator_bank = MagicMock()
        mock_elevator_bank.get_waiting_block.return_value = 5
        mock_elevator_bank.horizontal_block = 5 # Person starts at block 10
        mock_building.get_elevator_banks_on_floor.return_value = [mock_elevator_bank]
        
        # Person Initial floor: 5, initial block: 10 - be sure to double check conftest 
        person.set_destination(dest_floor=8, dest_block=15)
        person.update_idle(6.0)  # Past idle timeout
        
        # Be sure to check the `config.person.max_speed = 0.5` in conftest
        # It's currently 0.5 blocks / second (the destination is -5 blocks away)
        assert person.state == PersonState.WALKING
        assert person.direction == HorizontalDirection.LEFT  # Moving from block 10 to 5
        
        
    def test_update_walking_same_floor_reaches_destination_block(self, person: Person) -> None:
        """Test walking state reaches destination and becomes idle"""
        
        # Person Initial floor: 5, initial block: 10 - be sure to double check conftest 
        person.set_destination(dest_floor=5, dest_block=15)  # Same floor, different block
        person.testing_set_current_state(PersonState.WALKING)
        person.direction = HorizontalDirection.RIGHT
        
        # Large dt to ensure we reach destination
        # traverse 5 blocks in 15 seconds at 0.5 blocks / second
        person.update_walking(20.0)
        
        assert person.current_block == 15
        assert person.state == PersonState.IDLE
        assert person.direction == HorizontalDirection.STATIONARY
        
        
    def test_update_walking_reaches_selected_elevator_waits(self, person: Person, mock_building: MagicMock) -> None:
        """Test walking to elevator triggers waiting state"""
        mock_elevator_bank = MagicMock()
        mock_elevator_bank.get_waiting_block.return_value = 5
        mock_building.get_elevator_banks_on_floor.return_value = [mock_elevator_bank]
        
        # Set up person walking toward elevator
        # Person Initial floor: 5, initial block: 10 - be sure to double check conftest 
        person.set_destination(dest_floor=8, dest_block=15)
        person.testing_set_current_state(PersonState.WALKING)
        person.direction = HorizontalDirection.LEFT
        person.current_block = 6.0  # Close to elevator waiting block
        person.testing_set_next_elevator_bank(mock_elevator_bank)  # Simulate finding elevator
        
        person.update_walking(5.0)  # Large dt to reach destination
        
        # TODO: When we get more sophisticated, we should make sure the person is facing the elevator
        assert person.state == PersonState.WAITING_FOR_ELEVATOR
        mock_elevator_bank.add_waiting_passenger.assert_called_once_with(person)
        
        
    def test_find_nearest_elevator_bank_chooses_closest(self, person: Person, mock_building: MagicMock) -> None:
        """Test that person finds the closest elevator bank"""
        # Set up multiple elevator banks at different distances
        far_elevator = MagicMock()
        far_elevator.horizontal_block = 2  # Distance: |10 - 2| = 8
        
        close_elevator = MagicMock()  
        close_elevator.horizontal_block = 12  # Distance: |10 - 12| = 2
        
        mock_building.get_elevator_banks_on_floor.return_value = [far_elevator, close_elevator]
        
        # Person Initial floor: 5, initial block: 10 - be sure to double check conftest 
        result: None | ElevatorBank = person.find_nearest_elevator_bank()
        
        assert result == close_elevator


    def test_update_idle_finds_elevator_walks_there(self, person: Person, mock_building: MagicMock) -> None:
        """Larger tests, person wakes from idle, walks all the way to elevator"""
        
        # Person Initial floor: 5, initial block: 10 - be sure to double check conftest 
        person.set_destination(dest_floor=8, dest_block=15)
        person.testing_set_current_state(PersonState.WALKING)
        person.direction = HorizontalDirection.RIGHT # Facing away from the elevator
        
        mock_elevator_bank = MagicMock()
        mock_elevator_bank.horizontal_block = 3 # Person starts at block 10
        elevator_waiting_block: Final[int] = 2
        mock_elevator_bank.get_waiting_block.return_value = elevator_waiting_block
        mock_building.get_elevator_banks_on_floor.return_value = [mock_elevator_bank]
        
        person.update_idle(6.0) # default idle timeout is 5.0 (double check conftest)
        assert person.state == PersonState.WALKING
        assert person.direction == HorizontalDirection.LEFT

        
        person.update_walking(2.0) # Person has to walk 8 blocks in total, should be 1.5 closer now
        assert person.state == PersonState.WALKING # Definitely shouldn't be there yet (unless you create super sprinters)
        assert person.direction == HorizontalDirection.LEFT
        
        person.update_walking(30.0) # 8 blocks / 0.5 blocks / second = 16 seconds
        mock_elevator_bank.add_waiting_passenger.assert_called_once_with(person)
        assert person.current_block == elevator_waiting_block
        assert person.state == PersonState.WAITING_FOR_ELEVATOR
        
        
        