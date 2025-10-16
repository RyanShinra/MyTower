from __future__ import annotations

from typing import Final
from unittest.mock import MagicMock

from mytower.game.core.types import HorizontalDirection, PersonState
from mytower.game.core.units import Blocks, Time
from mytower.game.entities.entities_protocol import ElevatorBankProtocol
from mytower.game.entities.person import Person


class TestPersonMovement:
    """Test Person movement and path finding logic"""


    
    def test_no_movement_when_already_at_destination(self, person_with_floor: Person) -> None:
        """Test that person stays idle when already at destination"""
        # Use the person's current location as their destination 
        original_floor: Final[int] = person_with_floor.current_floor_num
        original_block: Final[Blocks] = person_with_floor.current_block_float
        
        person_with_floor.set_destination(dest_floor_num=original_floor, dest_block_num=original_block)

        person_with_floor.update_idle(Time(1.0))

        # Should stay idle since already on correct floor
        assert person_with_floor.state == PersonState.IDLE
        assert person_with_floor.direction == HorizontalDirection.STATIONARY
        assert person_with_floor.current_block_float == original_block
        assert person_with_floor.current_floor_num == original_floor

        
    def test_update_idle_different_floor_no_elevator(self, person_with_floor: Person, mock_building_with_floor: MagicMock) -> None:
        """Test person behavior when needing different floor but no elevator available"""
        mock_building_with_floor.get_elevator_banks_on_floor.return_value = []  # No elevators

        person_with_floor.set_destination(dest_floor_num=8, dest_block_num=Blocks(15.0))  # Wrap in Blocks
        person_with_floor.update_idle(Time(6.0))  # Past idle timeout
        
        # Should stay idle since no elevator available
        assert person_with_floor.state == PersonState.IDLE

        
    def test_update_idle_finds_elevator_starts_walking(self, person_with_floor: Person, mock_building_with_floor: MagicMock) -> None:
        """Test that person starts walking toward elevator when one is available"""
        # Person defaults to block 10, floor 5 - be sure to double check conftest 
        
        elevator_waiting_block = Blocks(5)  # Wrap in Blocks
        mock_elevator_bank = MagicMock()
        mock_elevator_bank.get_waiting_block.return_value = elevator_waiting_block
        mock_elevator_bank.horizontal_block = elevator_waiting_block  # Person starts at initial_block
        mock_building_with_floor.get_elevator_banks_on_floor.return_value = [mock_elevator_bank]

        person_with_floor.set_destination(dest_floor_num=8, dest_block_num=Blocks(15.0))  # Wrap in Blocks
        person_with_floor.update_idle(Time(6.0))  # Past idle timeout
        
        # Be sure to check the `config.person.max_speed = 0.5` in conftest
        # It's currently 0.5 blocks / second (the destination is elevator_waiting_block - initial_block blocks away)
        assert person_with_floor.state == PersonState.WALKING
        assert person_with_floor.direction == HorizontalDirection.LEFT  # Moving from block {initial_block} to {elevator_waiting_block}

        
    def test_update_walking_same_floor_reaches_destination_block(self, person_with_floor: Person) -> None:
        """Test walking state reaches destination and becomes idle"""

        # Person Initial floor: 5, initial block: 10 - be sure to double check conftest
        person_with_floor.set_destination(dest_floor_num=person_with_floor.current_floor_num, dest_block_num=Blocks(15.0))  # Already wrapped
        person_with_floor.testing_set_current_state(PersonState.WALKING)
        person_with_floor.direction = HorizontalDirection.RIGHT
        
        # Large dt to ensure we reach destination
        person_with_floor.update_walking(Time(30.0))
        
        assert person_with_floor.current_block_float == Blocks(15)  # Wrap in Blocks
        assert person_with_floor.state == PersonState.IDLE
        assert person_with_floor.direction == HorizontalDirection.STATIONARY

        
        
    def test_update_walking_reaches_selected_elevator_waits(self, person_with_floor: Person, mock_building_with_floor: MagicMock) -> None:
        """Test walking to elevator triggers waiting state"""
        mock_elevator_bank = MagicMock()
        mock_elevator_bank.get_waiting_block.return_value = Blocks(5)  # Wrap in Blocks
        mock_building_with_floor.get_elevator_banks_on_floor.return_value = [mock_elevator_bank]
        
        # Set up person walking toward elevator
        # Person Initial floor: 6, initial block: 10 - be sure to double check conftest
        person_with_floor.set_destination(dest_floor_num=8, dest_block_num=Blocks(15.0)) 
        person_with_floor.direction = HorizontalDirection.LEFT
        person_with_floor.testing_set_current_block_float(Blocks(6.0)) 
        person_with_floor.testing_set_next_elevator_bank(mock_elevator_bank)  # Simulate finding elevator

        person_with_floor.update_walking(Time(5.0))  # Large dt to reach destination

        # TODO: When we get more sophisticated, we should make sure the person is facing the elevator
        assert person_with_floor.state == PersonState.WAITING_FOR_ELEVATOR
        mock_elevator_bank.add_waiting_passenger.assert_called_once_with(person_with_floor)



    def test_find_nearest_elevator_bank_chooses_closest(self, person_with_floor: Person, mock_building_with_floor: MagicMock) -> None:
        """Test that person finds the closest elevator bank"""
        # Set up multiple elevator banks at different distances
        far_elevator = MagicMock()
        far_elevator.horizontal_block = Blocks(2)  # Wrap in Blocks - Distance: |10 - 2| = 8
        
        close_elevator = MagicMock()  
        close_elevator.horizontal_block = Blocks(12)  # Wrap in Blocks - Distance: |10 - 12| = 2
        
        mock_building_with_floor.get_elevator_banks_on_floor.return_value = [far_elevator, close_elevator]
        
        # Person Initial floor: 5, initial block: 10 - be sure to double check conftest 
        result: None | ElevatorBankProtocol = person_with_floor.find_nearest_elevator_bank()
        
        assert result == close_elevator



    def test_update_idle_finds_elevator_walks_there(self, person_with_floor: Person, mock_building_with_floor: MagicMock) -> None:
        """Larger tests, person wakes from idle, walks all the way to elevator"""
        
        # Person Initial floor: 5, initial block: 10 - be sure to double check conftest 
        person_with_floor.set_destination(dest_floor_num=8, dest_block_num=Blocks(15.0))  # Already wrapped
        person_with_floor.testing_set_current_state(PersonState.WALKING)
        person_with_floor.direction = HorizontalDirection.RIGHT # Facing away from the elevator
        
        mock_elevator_bank = MagicMock()
        mock_elevator_bank.horizontal_block = Blocks(3) # Already wrapped - Person starts at block 10
        elevator_waiting_block: Final[Blocks] = Blocks(2)  # Already wrapped
        mock_elevator_bank.get_waiting_block.return_value = elevator_waiting_block
        mock_building_with_floor.get_elevator_banks_on_floor.return_value = [mock_elevator_bank]
        
        person_with_floor.update_idle(Time(6.0)) # default idle timeout is 5.0 (verify conftest configuration)
        assert person_with_floor.state == PersonState.WALKING
        assert person_with_floor.direction == HorizontalDirection.LEFT


        person_with_floor.update_walking(Time(2.0)) # Person has to walk 8 blocks in total, should be 1.5 closer now
        assert person_with_floor.state == PersonState.WALKING # Definitely shouldn't be there yet (unless you create super sprinters)
        assert person_with_floor.direction == HorizontalDirection.LEFT

        # Calculate time needed to walk to elevator: distance / speed (+ small buffer)
        blocks_to_walk: Blocks = abs(person_with_floor.current_block_float - elevator_waiting_block)  # Should be 8.0

        assert float(person_with_floor.max_velocity) > 0.0  # Just to be sure we don't divide by zero
        walking_time: Time = blocks_to_walk.in_meters / person_with_floor.max_velocity + Time(2.0)  # Add 2s buffer
        person_with_floor.update_walking(walking_time)
        mock_elevator_bank.add_waiting_passenger.assert_called_once_with(person_with_floor)
        assert person_with_floor.current_block_float == elevator_waiting_block
        assert person_with_floor.state == PersonState.WAITING_FOR_ELEVATOR


