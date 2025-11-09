import pytest

from mytower.game.core.types import HorizontalDirection, PersonState
from mytower.game.core.units import Blocks, Time  # Add unit import
from mytower.game.entities.entities_protocol import BuildingProtocol
from mytower.game.entities.person import Person


class TestPersonPhysics:
    """Test Person movement calculations and boundary enforcement"""

    def test_left_is_negative(self) -> None:
        assert 1 * HorizontalDirection.LEFT.value == -1

    def test_right_is_positive(self) -> None:
        assert 1 * HorizontalDirection.RIGHT.value == 1

    def test_stationary_is_zero(self) -> None:
        assert 1 * HorizontalDirection.STATIONARY.value == 0

    @pytest.mark.parametrize(
        "direction,initial_block,dt,target_block",
        [
            (HorizontalDirection.RIGHT, Blocks(5), Time(2.0), Blocks(6)),  # Either-or case, depends on speed
            (HorizontalDirection.RIGHT, Blocks(1), Time(2.0), Blocks(9)),  # Should move but not reach target
            (HorizontalDirection.RIGHT, Blocks(1), Time(10.0), Blocks(3)),  # Should reach target
            (HorizontalDirection.LEFT, Blocks(10), Time(4.0), Blocks(8)),  # Either-or case, depends on speed
            (HorizontalDirection.LEFT, Blocks(10), Time(2.0), Blocks(2)),  # Should move but not reach target
            (HorizontalDirection.LEFT, Blocks(10), Time(10.0), Blocks(7)),  # Should reach target
            (HorizontalDirection.STATIONARY, Blocks(7), Time(3.0), Blocks(7)),  # No movement
        ],
    )


    def test_walking_moves_linear(
        self,
        person_with_floor: Person,
        direction: HorizontalDirection,
        initial_block: Blocks,
        dt: Time,
        target_block: Blocks,
    ) -> None:
        """Test that walking movement is linear and respects direction"""
        person_with_floor.testing_set_current_horiz_position(initial_block)
        person_with_floor.direction = direction
        person_with_floor.testing_set_current_state(PersonState.WALKING)
        person_with_floor.set_destination(
            dest_floor_num=person_with_floor.current_floor_num, dest_horiz_position=target_block
        )

        person_with_floor.update_walking(dt)
        dx: Blocks = (person_with_floor.max_velocity * dt).in_blocks
        total_distance: Blocks = abs(target_block - initial_block)

        if total_distance <= dx:
            # Should reach the target
            assert person_with_floor.current_horizontal_position == target_block
        else:
            # Should move in the correct direction but not reach the target
            expected_block: Blocks = initial_block + (dx * direction.value)
            assert person_with_floor.current_horizontal_position == expected_block


    def test_walking_stops_at_boundaries(self, person_with_floor: Person) -> None:
        """Test that walking respects building boundaries"""
        building: BuildingProtocol = person_with_floor.building
        assert building is not None, "Building should be set in fixture"

        # Test left boundary
        person_with_floor.testing_set_current_horiz_position(Blocks(0.5))
        person_with_floor.direction = HorizontalDirection.LEFT
        person_with_floor.testing_set_current_state(PersonState.WALKING)
        person_with_floor.set_destination(dest_floor_num=person_with_floor.current_floor_num, dest_horiz_position=Blocks(0))

        person_with_floor.update_walking(Time(5.0))
        assert person_with_floor.current_horizontal_position >= Blocks(0), "Person should not move past left boundary"
        assert person_with_floor.direction == HorizontalDirection.STATIONARY
        assert person_with_floor.state == PersonState.IDLE

        # Test right boundary
        right_boundary: Blocks = building.building_width
        person_with_floor.testing_set_current_horiz_position(right_boundary - Blocks(0.5))
        person_with_floor.direction = HorizontalDirection.RIGHT
        person_with_floor.testing_set_current_state(PersonState.WALKING)
        person_with_floor.set_destination(
            dest_floor_num=person_with_floor.current_floor_num, dest_horiz_position=right_boundary
        )

        person_with_floor.update_walking(Time(5.0))
        assert (
            person_with_floor.current_horizontal_position <= right_boundary
        ), "Person should not move past right boundary"
        assert person_with_floor.direction == HorizontalDirection.STATIONARY
        assert person_with_floor.state == PersonState.IDLE
