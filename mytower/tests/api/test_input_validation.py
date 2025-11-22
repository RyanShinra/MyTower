# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

"""
Unit tests for GraphQL input type validation.

Tests cover all validation rules for mutation inputs, including:
- Floor number validation
- Position validation
- Elevator bank ID validation
- Cross-field validation (e.g., min_floor <= max_floor)
"""

import pytest
from pydantic import ValidationError

from mytower.api.graphql_types import FloorTypeGQL
from mytower.api.input_types import (
    AddElevatorBankInputModel,
    AddElevatorInputModel,
    AddFloorInputModel,
    AddPersonInputModel,
)
from mytower.api.validation_constants import (
    MAX_ELEVATOR_BANK_ID_LENGTH,
    MAX_FLOOR_NUMBER,
    MAX_POSITION_BLOCKS,
    MIN_FLOOR_NUMBER,
    MIN_POSITION_BLOCKS,
)
from mytower.game.core.units import Blocks


class TestAddFloorInputModel:
    """Tests for AddFloorInputModel validation"""

    def test_valid_floor_type(self) -> None:
        """Should accept valid floor type"""
        model = AddFloorInputModel(floor_type=FloorTypeGQL.OFFICE)
        assert model.floor_type == FloorTypeGQL.OFFICE

    def test_all_floor_types(self) -> None:
        """Should accept all valid floor types"""
        for floor_type in FloorTypeGQL:
            model = AddFloorInputModel(floor_type=floor_type)
            assert model.floor_type == floor_type


class TestAddPersonInputModel:
    """Tests for AddPersonInputModel validation"""

    # Floor validation tests

    def test_valid_floors(self) -> None:
        """Should accept valid floor numbers"""
        model = AddPersonInputModel(
            init_floor=5,
            init_horiz_position=Blocks(10),
            dest_floor=10,
            dest_horiz_position=Blocks(20),
        )
        assert model.init_floor == 5
        assert model.dest_floor == 10

    def test_min_floor_boundary(self) -> None:
        """Should accept minimum floor number"""
        model = AddPersonInputModel(
            init_floor=MIN_FLOOR_NUMBER,
            init_horiz_position=Blocks(10),
            dest_floor=MIN_FLOOR_NUMBER,
            dest_horiz_position=Blocks(20),
        )
        assert model.init_floor == MIN_FLOOR_NUMBER
        assert model.dest_floor == MIN_FLOOR_NUMBER

    def test_max_floor_boundary(self) -> None:
        """Should accept maximum floor number"""
        model = AddPersonInputModel(
            init_floor=MAX_FLOOR_NUMBER,
            init_horiz_position=Blocks(10),
            dest_floor=MAX_FLOOR_NUMBER,
            dest_horiz_position=Blocks(20),
        )
        assert model.init_floor == MAX_FLOOR_NUMBER
        assert model.dest_floor == MAX_FLOOR_NUMBER

    def test_init_floor_below_min(self) -> None:
        """Should reject initial floor below minimum"""
        with pytest.raises(ValidationError) as exc_info:
            AddPersonInputModel(
                init_floor=MIN_FLOOR_NUMBER - 1,
                init_horiz_position=Blocks(10),
                dest_floor=10,
                dest_horiz_position=Blocks(20),
            )
        assert "Initial floor must be between" in str(exc_info.value)

    def test_init_floor_above_max(self) -> None:
        """Should reject initial floor above maximum"""
        with pytest.raises(ValidationError) as exc_info:
            AddPersonInputModel(
                init_floor=MAX_FLOOR_NUMBER + 1,
                init_horiz_position=Blocks(10),
                dest_floor=10,
                dest_horiz_position=Blocks(20),
            )
        assert "Initial floor must be between" in str(exc_info.value)

    def test_dest_floor_below_min(self) -> None:
        """Should reject destination floor below minimum"""
        with pytest.raises(ValidationError) as exc_info:
            AddPersonInputModel(
                init_floor=5,
                init_horiz_position=Blocks(10),
                dest_floor=MIN_FLOOR_NUMBER - 1,
                dest_horiz_position=Blocks(20),
            )
        assert "Destination floor must be between" in str(exc_info.value)

    def test_dest_floor_above_max(self) -> None:
        """Should reject destination floor above maximum"""
        with pytest.raises(ValidationError) as exc_info:
            AddPersonInputModel(
                init_floor=5,
                init_horiz_position=Blocks(10),
                dest_floor=MAX_FLOOR_NUMBER + 1,
                dest_horiz_position=Blocks(20),
            )
        assert "Destination floor must be between" in str(exc_info.value)

    def test_floor_zero(self) -> None:
        """Should reject floor number zero"""
        with pytest.raises(ValidationError) as exc_info:
            AddPersonInputModel(
                init_floor=0,
                init_horiz_position=Blocks(10),
                dest_floor=10,
                dest_horiz_position=Blocks(20),
            )
        assert "Initial floor must be between" in str(exc_info.value)

    def test_negative_floor(self) -> None:
        """Should reject negative floor numbers"""
        with pytest.raises(ValidationError) as exc_info:
            AddPersonInputModel(
                init_floor=-5,
                init_horiz_position=Blocks(10),
                dest_floor=10,
                dest_horiz_position=Blocks(20),
            )
        assert "Initial floor must be between" in str(exc_info.value)

    # Position validation tests

    def test_valid_positions(self) -> None:
        """Should accept valid positions"""
        model = AddPersonInputModel(
            init_floor=5,
            init_horiz_position=Blocks(10),
            dest_floor=10,
            dest_horiz_position=Blocks(20),
        )
        assert model.init_horiz_position == Blocks(10)
        assert model.dest_horiz_position == Blocks(20)

    def test_min_position_boundary(self) -> None:
        """Should accept minimum position"""
        model = AddPersonInputModel(
            init_floor=5,
            init_horiz_position=Blocks(MIN_POSITION_BLOCKS),
            dest_floor=10,
            dest_horiz_position=Blocks(MIN_POSITION_BLOCKS),
        )
        assert model.init_horiz_position == Blocks(MIN_POSITION_BLOCKS)
        assert model.dest_horiz_position == Blocks(MIN_POSITION_BLOCKS)

    def test_max_position_boundary(self) -> None:
        """Should accept maximum position"""
        model = AddPersonInputModel(
            init_floor=5,
            init_horiz_position=Blocks(MAX_POSITION_BLOCKS),
            dest_floor=10,
            dest_horiz_position=Blocks(MAX_POSITION_BLOCKS),
        )
        assert model.init_horiz_position == Blocks(MAX_POSITION_BLOCKS)
        assert model.dest_horiz_position == Blocks(MAX_POSITION_BLOCKS)

    def test_init_position_below_min(self) -> None:
        """Should reject initial position below minimum"""
        with pytest.raises(ValidationError) as exc_info:
            AddPersonInputModel(
                init_floor=5,
                init_horiz_position=Blocks(MIN_POSITION_BLOCKS - 1),
                dest_floor=10,
                dest_horiz_position=Blocks(20),
            )
        assert "Initial horizontal position must be between" in str(exc_info.value)

    def test_init_position_above_max(self) -> None:
        """Should reject initial position above maximum"""
        with pytest.raises(ValidationError) as exc_info:
            AddPersonInputModel(
                init_floor=5,
                init_horiz_position=Blocks(MAX_POSITION_BLOCKS + 1),
                dest_floor=10,
                dest_horiz_position=Blocks(20),
            )
        assert "Initial horizontal position must be between" in str(exc_info.value)

    def test_dest_position_below_min(self) -> None:
        """Should reject destination position below minimum"""
        with pytest.raises(ValidationError) as exc_info:
            AddPersonInputModel(
                init_floor=5,
                init_horiz_position=Blocks(10),
                dest_floor=10,
                dest_horiz_position=Blocks(MIN_POSITION_BLOCKS - 1),
            )
        assert "Destination horizontal position must be between" in str(exc_info.value)

    def test_dest_position_above_max(self) -> None:
        """Should reject destination position above maximum"""
        with pytest.raises(ValidationError) as exc_info:
            AddPersonInputModel(
                init_floor=5,
                init_horiz_position=Blocks(10),
                dest_floor=10,
                dest_horiz_position=Blocks(MAX_POSITION_BLOCKS + 1),
            )
        assert "Destination horizontal position must be between" in str(exc_info.value)

    def test_negative_position(self) -> None:
        """Should reject negative positions"""
        with pytest.raises(ValidationError) as exc_info:
            AddPersonInputModel(
                init_floor=5,
                init_horiz_position=Blocks(-10),
                dest_floor=10,
                dest_horiz_position=Blocks(20),
            )
        assert "Initial horizontal position must be between" in str(exc_info.value)


class TestAddElevatorBankInputModel:
    """Tests for AddElevatorBankInputModel validation"""

    def test_valid_elevator_bank(self) -> None:
        """Should accept valid elevator bank parameters"""
        model = AddElevatorBankInputModel(
            horiz_position=Blocks(50), min_floor=1, max_floor=10
        )
        assert model.horiz_position == Blocks(50)
        assert model.min_floor == 1
        assert model.max_floor == 10

    # Position validation tests

    def test_min_position_boundary(self) -> None:
        """Should accept minimum position"""
        model = AddElevatorBankInputModel(
            horiz_position=Blocks(MIN_POSITION_BLOCKS), min_floor=1, max_floor=10
        )
        assert model.horiz_position == Blocks(MIN_POSITION_BLOCKS)

    def test_max_position_boundary(self) -> None:
        """Should accept maximum position"""
        model = AddElevatorBankInputModel(
            horiz_position=Blocks(MAX_POSITION_BLOCKS), min_floor=1, max_floor=10
        )
        assert model.horiz_position == Blocks(MAX_POSITION_BLOCKS)

    def test_position_below_min(self) -> None:
        """Should reject position below minimum"""
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorBankInputModel(
                horiz_position=Blocks(MIN_POSITION_BLOCKS - 1), min_floor=1, max_floor=10
            )
        assert "Horizontal position must be between" in str(exc_info.value)

    def test_position_above_max(self) -> None:
        """Should reject position above maximum"""
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorBankInputModel(
                horiz_position=Blocks(MAX_POSITION_BLOCKS + 1), min_floor=1, max_floor=10
            )
        assert "Horizontal position must be between" in str(exc_info.value)

    # Floor range validation tests

    def test_min_floor_boundary(self) -> None:
        """Should accept minimum floor number"""
        model = AddElevatorBankInputModel(
            horiz_position=Blocks(50), min_floor=MIN_FLOOR_NUMBER, max_floor=10
        )
        assert model.min_floor == MIN_FLOOR_NUMBER

    def test_max_floor_boundary(self) -> None:
        """Should accept maximum floor number"""
        model = AddElevatorBankInputModel(
            horiz_position=Blocks(50), min_floor=1, max_floor=MAX_FLOOR_NUMBER
        )
        assert model.max_floor == MAX_FLOOR_NUMBER

    def test_min_floor_below_min(self) -> None:
        """Should reject min_floor below minimum"""
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorBankInputModel(
                horiz_position=Blocks(50), min_floor=MIN_FLOOR_NUMBER - 1, max_floor=10
            )
        assert "Minimum floor must be between" in str(exc_info.value)

    def test_min_floor_above_max(self) -> None:
        """Should reject min_floor above maximum"""
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorBankInputModel(
                horiz_position=Blocks(50), min_floor=MAX_FLOOR_NUMBER + 1, max_floor=MAX_FLOOR_NUMBER + 2
            )
        assert "Minimum floor must be between" in str(exc_info.value)

    def test_max_floor_below_min(self) -> None:
        """Should reject max_floor below minimum"""
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorBankInputModel(
                horiz_position=Blocks(50), min_floor=MIN_FLOOR_NUMBER, max_floor=MIN_FLOOR_NUMBER - 1
            )
        assert "Maximum floor must be between" in str(exc_info.value)

    def test_max_floor_above_max(self) -> None:
        """Should reject max_floor above maximum"""
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorBankInputModel(
                horiz_position=Blocks(50), min_floor=1, max_floor=MAX_FLOOR_NUMBER + 1
            )
        assert "Maximum floor must be between" in str(exc_info.value)

    # Cross-field validation tests

    def test_max_equal_to_min(self) -> None:
        """Should accept max_floor equal to min_floor"""
        model = AddElevatorBankInputModel(
            horiz_position=Blocks(50), min_floor=5, max_floor=5
        )
        assert model.min_floor == 5
        assert model.max_floor == 5

    def test_max_less_than_min(self) -> None:
        """Should reject max_floor less than min_floor"""
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorBankInputModel(
                horiz_position=Blocks(50), min_floor=10, max_floor=5
            )
        assert "Maximum floor" in str(exc_info.value)
        assert "must be greater than or equal to minimum floor" in str(exc_info.value)

    def test_large_floor_range(self) -> None:
        """Should accept large but valid floor range"""
        model = AddElevatorBankInputModel(
            horiz_position=Blocks(50),
            min_floor=MIN_FLOOR_NUMBER,
            max_floor=MAX_FLOOR_NUMBER,
        )
        assert model.min_floor == MIN_FLOOR_NUMBER
        assert model.max_floor == MAX_FLOOR_NUMBER


class TestAddElevatorInputModel:
    """Tests for AddElevatorInputModel validation"""

    def test_valid_elevator_bank_id(self) -> None:
        """Should accept valid elevator bank ID"""
        model = AddElevatorInputModel(elevator_bank_id="elevator-bank-123")
        assert model.elevator_bank_id == "elevator-bank-123"

    def test_alphanumeric_id(self) -> None:
        """Should accept alphanumeric IDs"""
        model = AddElevatorInputModel(elevator_bank_id="Bank123")
        assert model.elevator_bank_id == "Bank123"

    def test_id_with_hyphens(self) -> None:
        """Should accept IDs with hyphens"""
        model = AddElevatorInputModel(elevator_bank_id="bank-123-abc")
        assert model.elevator_bank_id == "bank-123-abc"

    def test_id_with_underscores(self) -> None:
        """Should accept IDs with underscores"""
        model = AddElevatorInputModel(elevator_bank_id="bank_123_abc")
        assert model.elevator_bank_id == "bank_123_abc"

    def test_id_with_mixed_separators(self) -> None:
        """Should accept IDs with both hyphens and underscores"""
        model = AddElevatorInputModel(elevator_bank_id="bank-123_abc")
        assert model.elevator_bank_id == "bank-123_abc"

    def test_max_length_id(self) -> None:
        """Should accept ID at maximum length"""
        max_length_id = "a" * MAX_ELEVATOR_BANK_ID_LENGTH
        model = AddElevatorInputModel(elevator_bank_id=max_length_id)
        assert model.elevator_bank_id == max_length_id

    def test_id_with_leading_whitespace(self) -> None:
        """Should reject ID with leading whitespace"""
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorInputModel(elevator_bank_id="  bank-123")
        assert "must not have leading or trailing whitespace" in str(exc_info.value)

    def test_id_with_trailing_whitespace(self) -> None:
        """Should reject ID with trailing whitespace"""
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorInputModel(elevator_bank_id="bank-123  ")
        assert "must not have leading or trailing whitespace" in str(exc_info.value)

    def test_id_with_leading_and_trailing_whitespace(self) -> None:
        """Should reject ID with leading and trailing whitespace"""
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorInputModel(elevator_bank_id="  bank-123  ")
        assert "must not have leading or trailing whitespace" in str(exc_info.value)

    # Negative tests

    def test_empty_id(self) -> None:
        """Should reject empty ID"""
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorInputModel(elevator_bank_id="")
        assert "Elevator bank ID cannot be empty" in str(exc_info.value)

    def test_whitespace_only_id(self) -> None:
        """Should reject whitespace-only ID"""
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorInputModel(elevator_bank_id="   ")
        assert "Elevator bank ID cannot be empty" in str(exc_info.value)

    def test_id_too_long(self) -> None:
        """Should reject ID exceeding maximum length"""
        too_long_id = "a" * (MAX_ELEVATOR_BANK_ID_LENGTH + 1)
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorInputModel(elevator_bank_id=too_long_id)
        assert f"Elevator bank ID must be {MAX_ELEVATOR_BANK_ID_LENGTH} characters or less" in str(
            exc_info.value
        )

    def test_id_with_special_characters(self) -> None:
        """Should reject ID with special characters"""
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorInputModel(elevator_bank_id="bank@123")
        assert "must contain only alphanumeric characters, hyphens, and underscores" in str(
            exc_info.value
        )

    def test_id_with_spaces(self) -> None:
        """Should reject ID with spaces"""
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorInputModel(elevator_bank_id="bank 123")
        assert "must contain only alphanumeric characters, hyphens, and underscores" in str(
            exc_info.value
        )

    def test_id_with_dots(self) -> None:
        """Should reject ID with dots"""
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorInputModel(elevator_bank_id="bank.123")
        assert "must contain only alphanumeric characters, hyphens, and underscores" in str(
            exc_info.value
        )

    def test_id_with_emoji(self) -> None:
        """Should reject ID with emoji"""
        with pytest.raises(ValidationError) as exc_info:
            AddElevatorInputModel(elevator_bank_id="bank🏢")
        assert "must contain only alphanumeric characters, hyphens, and underscores" in str(
            exc_info.value
        )
