from unittest.mock import MagicMock
from mytower.game.person import Person
from mytower.game.types import PersonState, HorizontalDirection



class TestPersonBasics:
    """Test basic Person properties and initialization"""


    
    def test_initial_state(self, person: Person) -> None:
        """Test that person initializes with correct values"""
        assert person.state == PersonState.IDLE
        assert person.current_floor_num == 5 # Look at Person factory in conftest.py
        assert person.current_block_float == 10.0
        assert person.destination_floor_num == 5  # Same as current initially
        assert person.direction == HorizontalDirection.STATIONARY
        
    def test_set_destination_valid(self, person: Person) -> None:
        """Test setting valid destination updates internal state"""
        person.set_destination(dest_floor_num=8, dest_block_num=15)
        
        assert person.destination_floor_num == 8
        assert person.testing_confirm_dest_block_is(15)


        
    def test_set_destination_out_of_bounds_clamped(self, person: Person, mock_building_no_floor: MagicMock) -> None:
        """Test that out-of-bounds destinations get clamped to valid range"""
        # Building has 10 floors, 20 width (from fixture)
        person.set_destination(dest_floor_num=15, dest_block_num=25)  # Both too high
        assert person.destination_floor_num == mock_building_no_floor.num_floors  # Clamped to max
        
        assert not person.testing_confirm_dest_block_is(25) # At least it's not wrong
        assert person.testing_confirm_dest_block_is(mock_building_no_floor.floor_width) # At least it's not wrong
        
        person.set_destination(dest_floor_num=-1, dest_block_num=-5)  # Both too low  
        assert person.destination_floor_num == 0   # Clamped to min
        
        assert not person.testing_confirm_dest_block_is(-5) # At least it's not wrong
        assert person.testing_confirm_dest_block_is(0) #  Clamped to min
        
    def test_current_block_property(self, person: Person) -> None:
        """Test current_block getter and setter"""
        assert person.current_block_float == 10.0

        person.testing_set_current_block_float(15.5)
        assert person.current_block_float == 15.5
        
    def test_state_property(self, person: Person) -> None:
        """Test state getter and setter"""
        person.testing_set_current_state(PersonState.WALKING)
        assert person.state == PersonState.WALKING
        
    def test_direction_property(self, person: Person) -> None:
        """Test direction getter and setter"""  
        person.direction = HorizontalDirection.LEFT
        assert person.direction == HorizontalDirection.LEFT
