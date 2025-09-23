import pytest
from unittest.mock import MagicMock
from mytower.game.entities.person import Person
from mytower.game.core.types import HorizontalDirection, PersonState
from mytower.game.core.constants import BLOCK_FLOAT_TOLERANCE



class TestPersonPhysics:
    """Test Person movement calculations and boundary enforcement"""
    
    def test_left_is_negative(self) -> None:
        assert 1 * HorizontalDirection.LEFT.value == -1
    
    @pytest.mark.parametrize("direction,initial_block,dt,expected_block", [
        (HorizontalDirection.RIGHT, 5, 2.0, 6),  # 5 + (2.0 * 0.5 * 1) = 6
        (HorizontalDirection.LEFT, 10, 4.0, 8),  # 10 + (4.0 * 0.5 * -1) = 8  
        (HorizontalDirection.STATIONARY, 7, 3.0, 7),  # No movement


    ])
    def test_walking_movement_calculation(
        self, person_with_floor: Person, direction: HorizontalDirection, initial_block: int, dt: float, expected_block: int
    ) -> None:
        """Test that walking movement calculations are correct"""
        person_with_floor.testing_set_current_block_float(initial_block)
        person_with_floor.direction = direction
        person_with_floor.testing_set_current_state(PersonState.WALKING)
        person_with_floor.set_destination(dest_floor_num=5, dest_block_num=expected_block)
        
        person_with_floor.update_walking(dt)
        
        assert abs(person_with_floor.current_block_float - expected_block) < BLOCK_FLOAT_TOLERANCE  # Allow for floating point precision


        
    def test_walking_respects_building_boundaries(self, person_with_floor: Person, mock_building_no_floor: MagicMock) -> None:
        """Test that person movement is constrained by building boundaries"""
        mock_building_no_floor.floor_width = 20
        
        # Test right boundary
        person_with_floor.testing_set_current_block_float(19.5)
        person_with_floor.direction = HorizontalDirection.RIGHT
        person_with_floor.testing_set_current_state(PersonState.WALKING)
        person_with_floor.set_destination(dest_floor_num=5, dest_block_num=25)  # Beyond building width
        
        person_with_floor.update_walking(10.0)  # Large dt
        
        assert person_with_floor.current_block_float <= 20  # Clamped to building width

        # Test left boundary
        person_with_floor.testing_set_current_block_float(0.5)
        person_with_floor.direction = HorizontalDirection.LEFT
        person_with_floor.set_destination(dest_floor_num=5, dest_block_num=-5)  # Below 0
        
        person_with_floor.update_walking(10.0)
        
        assert person_with_floor.current_block_float >= 0  # Clamped to 0

