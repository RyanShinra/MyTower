import pytest
from unittest.mock import MagicMock
from mytower.game.person import Person


class TestPersonValidation:
    """Test Person input validation and error handling"""
    
    def test_testing_set_dest_floor_valid(self, person: Person) -> None:
        """Test that setting valid destination floor works"""
        person.testing_set_dest_floor(7)
        assert person.destination_floor == 7
        
    def test_testing_set_dest_floor_out_of_bounds(self, person: Person, mock_building: MagicMock) -> None:
        """Test that setting invalid destination floor raises error"""
        with pytest.raises(ValueError, match=".*out of bounds.*"):
            person.testing_set_dest_floor(15)  # Above building height
            
        with pytest.raises(ValueError, match=".*out of bounds.*"):
            person.testing_set_dest_floor(-1)  # Below ground

