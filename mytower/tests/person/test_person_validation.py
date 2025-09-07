import pytest
from unittest.mock import MagicMock
from mytower.game.entities.person import Person



class TestPersonValidation:
    """Test Person input validation and error handling"""
    
    def test_testing_set_dest_floor_valid(self, person_without_floor: Person) -> None:
        """Test that setting valid destination floor works"""
        person_without_floor.testing_set_dest_floor_num(7)
        assert person_without_floor.destination_floor_num == 7


        
    def test_testing_set_dest_floor_out_of_bounds(self, person_without_floor: Person, mock_building_no_floor: MagicMock) -> None:
        """Test that setting invalid destination floor raises error"""
        with pytest.raises(ValueError, match=".*out of bounds.*"):
            person_without_floor.testing_set_dest_floor_num(15)  # Above building height
            
        with pytest.raises(ValueError, match=".*out of bounds.*"):
            person_without_floor.testing_set_dest_floor_num(-1)  # Below ground

