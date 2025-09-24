from unittest.mock import MagicMock
from mytower.game.entities.person import Person
from mytower.game.core.types import PersonState, HorizontalDirection
from mytower.tests.conftest import PERSON_DEFAULT_BLOCK, PERSON_DEFAULT_FLOOR



class TestPersonBasics:
    """Test basic Person properties and initialization"""

    def test_initial_state(self, person_with_floor: Person) -> None:
        """Test that person initializes with correct values"""
        assert person_with_floor.state == PersonState.IDLE
        assert person_with_floor.current_floor_num == PERSON_DEFAULT_FLOOR # Determined by Person constructor's default behavior when current_floor_num=None
        assert person_with_floor.current_block_float == PERSON_DEFAULT_BLOCK
        assert person_with_floor.destination_floor_num == PERSON_DEFAULT_FLOOR  # Same as current floor, initially
        assert person_with_floor.direction == HorizontalDirection.STATIONARY
        
    def test_set_destination_valid(self, person_with_floor: Person) -> None:
        """Test setting valid destination updates internal state"""
        person_with_floor.set_destination(dest_floor_num=8, dest_block_num=15)
        
        assert person_with_floor.destination_floor_num == 8
        assert person_with_floor.testing_confirm_dest_block_is(15)


        
    def test_set_destination_out_of_bounds_clamped(self, person_with_floor: Person, mock_building_no_floor: MagicMock) -> None:
        """Test that out-of-bounds destinations get clamped to valid range"""
        # Building has 10 floors, 20 width (from fixture)
        person_with_floor.set_destination(dest_floor_num=15, dest_block_num=25)  # Both too high
        assert person_with_floor.destination_floor_num == mock_building_no_floor.num_floors  # Clamped to max
        
        assert not person_with_floor.testing_confirm_dest_block_is(25) # At least it's not wrong
        assert person_with_floor.testing_confirm_dest_block_is(mock_building_no_floor.floor_width) # At least it's not wrong
        
        person_with_floor.set_destination(dest_floor_num=-1, dest_block_num=-5)  # Both too low  
        assert person_with_floor.destination_floor_num == 0   # Clamped to min
        
        assert not person_with_floor.testing_confirm_dest_block_is(-5) # At least it's not wrong
        assert person_with_floor.testing_confirm_dest_block_is(0) #  Clamped to min
        
    def test_current_block_property(self, person_with_floor: Person) -> None:
        """Test current_block getter and setter"""
        assert person_with_floor.current_block_float == PERSON_DEFAULT_BLOCK

        person_with_floor.testing_set_current_block_float(15.5)
        assert person_with_floor.current_block_float == 15.5
        
    def test_state_property(self, person_with_floor: Person) -> None:
        """Test state getter and setter"""
        person_with_floor.testing_set_current_state(PersonState.WALKING)
        assert person_with_floor.state == PersonState.WALKING
        
    def test_direction_property(self, person_with_floor: Person) -> None:
        """Test direction getter and setter"""  
        person_with_floor.direction = HorizontalDirection.LEFT
        assert person_with_floor.direction == HorizontalDirection.LEFT
