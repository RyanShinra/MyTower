import pytest
from unittest.mock import MagicMock
from mytower.game.person import Person
from mytower.game.types import HorizontalDirection, PersonState
from mytower.game.constants import BLOCK_FLOAT_TOLERANCE

class TestPersonPhysics:
    """Test Person movement calculations and boundary enforcement"""
    
    @pytest.mark.parametrize("direction,initial_block,dt,expected_block", [
        (HorizontalDirection.RIGHT, 5.0, 2.0, 6.0),  # 5 + (2 * 0.5 * 1) = 6
        (HorizontalDirection.LEFT, 10.0, 4.0, 8.0),  # 10 + (4 * 0.5 * -1) = 8  
        (HorizontalDirection.STATIONARY, 7.0, 3.0, 7.0),  # No movement
    ])
    def test_walking_movement_calculation(
        self, person: Person, direction: HorizontalDirection, initial_block: float, dt: float, expected_block: float
    ) -> None:
        """Test that walking movement calculations are correct"""
        person.current_block = initial_block
        person.direction = direction
        person.testing_set_current_state(PersonState.WALKING)
        person.set_destination(dest_floor=5, dest_block=int(expected_block))
        
        person.update_walking(dt)
        
        assert abs(person.current_block - expected_block) < BLOCK_FLOAT_TOLERANCE  # Allow for floating point precision
        
    def test_walking_respects_building_boundaries(self, person: Person, mock_building: MagicMock) -> None:
        """Test that person movement is constrained by building boundaries"""
        mock_building.floor_width = 20
        
        # Test right boundary
        person.current_block = 19.5
        person.direction = HorizontalDirection.RIGHT
        person.testing_set_current_state(PersonState.WALKING)
        person.set_destination(dest_floor=5, dest_block=25)  # Beyond building width
        
        person.update_walking(10.0)  # Large dt
        
        assert person.current_block <= 20  # Clamped to building width
        
        # Test left boundary  
        person.current_block = 0.5
        person.direction = HorizontalDirection.LEFT
        person.set_destination(dest_floor=5, dest_block=-5)  # Below 0
        
        person.update_walking(10.0)
        
        assert person.current_block >= 0  # Clamped to 0

