from unittest.mock import MagicMock, Mock
from typing import Callable

import pytest
from mytower.game.entities.person import Person
from mytower.game.core.types import PersonState, HorizontalDirection
from mytower.tests.conftest import BUILDING_DEFAULT_FLOOR_WIDTH, BUILDING_DEFAULT_NUM_FLOORS, PERSON_DEFAULT_BLOCK, PERSON_DEFAULT_FLOOR
from mytower.tests.test_utilities import StateAssertions



class TestPersonBasics:
    """Test basic Person properties and initialization"""

    def test_initial_state(self, person_with_floor: Person, state_assertions: StateAssertions) -> None:
        """Test that person initializes with correct values"""
        state_assertions.assert_person_state(
            person_with_floor,
            expected_state=PersonState.IDLE,
            expected_floor=PERSON_DEFAULT_FLOOR,
            expected_block=PERSON_DEFAULT_BLOCK,
            expected_destination_floor=PERSON_DEFAULT_FLOOR
        )
        assert person_with_floor.direction == HorizontalDirection.STATIONARY
        
        
    def test_set_destination_valid(self, person_with_floor: Person) -> None:
        """Test setting valid destination updates internal state"""
        person_with_floor.set_destination(dest_floor_num=8, dest_block_num=15.0)
        
        assert person_with_floor.destination_floor_num == 8
        assert person_with_floor.testing_confirm_dest_block_is(15.0)


    def test_person_creation_invalid_floor_raises_value_error(
        self, 
        building_factory: Callable[..., Mock], 
        mock_logger_provider: MagicMock, 
        mock_game_config: MagicMock
    ) -> None:
        """Test that creating a person with invalid initial floor raises ValueError"""
        mock_building_with_floor = building_factory(has_floors=True)
        
        # Building has 10 floors (from fixture)
        with pytest.raises(ValueError, match=f"Initial floor {BUILDING_DEFAULT_NUM_FLOORS + 1} is out of bounds"):
            Person(config=mock_game_config, logger_provider=mock_logger_provider, building=mock_building_with_floor, initial_floor_number=BUILDING_DEFAULT_NUM_FLOORS + 1, initial_block_float=5)  # Floor too high
    
        with pytest.raises(ValueError, match="Initial floor -1 is out of bounds"):
            Person(config=mock_game_config, logger_provider=mock_logger_provider, building=mock_building_with_floor, initial_floor_number=-1, initial_block_float=5)  # Floor too low


    def test_person_creation_invalid_block_raises_value_error(self, mock_building_with_floor: MagicMock, mock_logger_provider: MagicMock, mock_game_config: MagicMock) -> None:
        """Test that creating a person with invalid initial block raises ValueError"""
        # Building has 20 width (from fixture)
        with pytest.raises(ValueError, match=f"Initial block {BUILDING_DEFAULT_FLOOR_WIDTH + 2} is out of bounds"):
            Person(config=mock_game_config, logger_provider=mock_logger_provider, building=mock_building_with_floor, initial_floor_number=5, initial_block_float=BUILDING_DEFAULT_FLOOR_WIDTH + 2)  # Block too high

        with pytest.raises(ValueError, match=f"Initial block -5.0 is out of bounds"):
            Person(config=mock_game_config, logger_provider=mock_logger_provider, building=mock_building_with_floor, initial_floor_number=5, initial_block_float=-5.0)  # Block too low
        
        
    def test_set_destination_out_of_bounds_raises_value_error(self, person_with_floor: Person, mock_building_no_floor: MagicMock) -> None:
        """Test that out-of-bounds destinations get clamped to valid range"""
        # Building has 10 floors, 20 width (from fixture)
        with pytest.raises(ValueError, match=f"Destination floor {BUILDING_DEFAULT_NUM_FLOORS + 1} is out of bounds"):
            person_with_floor.set_destination(dest_floor_num=BUILDING_DEFAULT_NUM_FLOORS + 1, dest_block_num=15.0)  # Floor too high
            
        #TODO: This will need be revised if we ever have buildings with negative floor numbers
        with pytest.raises(ValueError, match="Destination floor -1 is out of bounds"):
            person_with_floor.set_destination(dest_floor_num=-1, dest_block_num=15.0)  # Floor too low

        with pytest.raises(ValueError, match=f"Destination block {float(BUILDING_DEFAULT_FLOOR_WIDTH + 2)} is out of bounds"):
            person_with_floor.set_destination(dest_floor_num=5, dest_block_num=float(BUILDING_DEFAULT_FLOOR_WIDTH + 2))  # Block too high
        
        #TODO: We will need to revisit this when buildings don't start at block 0 (the far left edge of the screen)
        with pytest.raises(ValueError, match="Destination block -5.0 is out of bounds"):
            person_with_floor.set_destination(dest_floor_num=5, dest_block_num=-5.0)  # Block too low
        
        
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
