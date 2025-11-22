# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

from mytower.game.core import constants, primitive_constants
from mytower.game.core.types import Money
from mytower.game.core.units import Blocks, Pixels  # Add unit import


class TestDisplayConstants:
    """Test display-related constants"""

    def test_screen_dimensions(self) -> None:
        """Test screen dimension constants"""
        assert constants.SCREEN_WIDTH == 1600
        assert constants.SCREEN_HEIGHT == 1200
        assert constants.SCREEN_WIDTH > 0
        assert constants.SCREEN_HEIGHT > 0


    def test_performance_constants(self) -> None:
        """Test performance-related constants"""
        assert constants.FPS == 60
        assert constants.FPS > 0

        assert constants.MIN_TIME_MULTIPLIER == 0.1
        assert constants.MAX_TIME_MULTIPLIER == 10.0
        assert constants.MIN_TIME_MULTIPLIER < constants.MAX_TIME_MULTIPLIER
        assert constants.MIN_TIME_MULTIPLIER > 0

    def test_background_color(self) -> None:
        """Test background color constant"""
        assert constants.BACKGROUND_COLOR == (240, 240, 240)
        assert isinstance(constants.BACKGROUND_COLOR, tuple)
        assert len(constants.BACKGROUND_COLOR) == 3
        assert all(isinstance(c, int) and 0 <= c <= 255 for c in constants.BACKGROUND_COLOR)


class TestGameGridConstants:
    """Test game grid-related constants"""

    def test_block_dimensions(self) -> None:
        """Test block dimension constants"""
        assert constants.BLOCK_WIDTH == Blocks(1.0)  # Wrap in Blocks
        assert constants.BLOCK_HEIGHT == Blocks(1.0)  # Wrap in Blocks
        assert constants.BLOCK_WIDTH > Blocks(0)  # Compare Blocks to Blocks
        assert constants.BLOCK_HEIGHT > Blocks(0)  # Compare Blocks to Blocks

    def test_metric_float_tolerance(self) -> None:
        """Test metric float tolerance constant"""
        assert primitive_constants.METRIC_FLOAT_TOLERANCE == 0.01  # 1 cm tolerance for metric values
        assert primitive_constants.METRIC_FLOAT_TOLERANCE > 0
        assert primitive_constants.METRIC_FLOAT_TOLERANCE < 1.0


class TestFloorConstants:
    """Test floor-related constants"""


    def test_floor_colors(self) -> None:
        """Test that all floor colors are valid RGB tuples"""
        floor_colors = [
            constants.LOBBY_COLOR,
            constants.OFFICE_COLOR,
            constants.APARTMENT_COLOR,
            constants.HOTEL_COLOR,
            constants.RESTAURANT_COLOR,
            constants.RETAIL_COLOR,
            constants.FLOORBOARD_COLOR,
            constants.DEFAULT_FLOOR_COLOR,
        ]

        for color in floor_colors:
            assert isinstance(color, tuple)
            assert len(color) == 3
            assert all(isinstance(c, int) and 0 <= c <= 255 for c in color)


    def test_floor_dimensions(self) -> None:
        """Test floor dimension constants"""
        assert constants.FLOORBOARD_HEIGHT == Pixels(4)  # Wrap in Pixels
        assert constants.DEFAULT_FLOOR_HEIGHT == Blocks(1)  # Wrap in Blocks
        assert constants.DEFAULT_FLOOR_LEFT_EDGE == Blocks(0)  # Wrap in Blocks
        assert constants.DEFAULT_FLOOR_WIDTH == Blocks(20)  # Wrap in Blocks

        # All dimensions should be positive (except left edge which can be 0)
        assert constants.FLOORBOARD_HEIGHT > Pixels(0)  # Compare Pixels to Pixels
        assert constants.DEFAULT_FLOOR_HEIGHT > Blocks(0)  # Compare Blocks to Blocks
        assert constants.DEFAULT_FLOOR_LEFT_EDGE >= Blocks(0)  # Compare Blocks to Blocks
        assert constants.DEFAULT_FLOOR_WIDTH > Blocks(0)  # Compare Blocks to Blocks


    def test_floor_heights(self) -> None:
        """Test floor height constants"""
        floor_heights = [
            constants.LOBBY_HEIGHT,
            constants.OFFICE_HEIGHT,
            constants.APARTMENT_HEIGHT,
            constants.HOTEL_HEIGHT,
            constants.RESTAURANT_HEIGHT,
            constants.RETAIL_HEIGHT,
        ]

        for height in floor_heights:
            assert height == Blocks(1)  # All are 1 block high for now - compare to Blocks
            assert height > Blocks(0)  # Compare Blocks to Blocks

    def test_floor_height_consistency(self) -> None:
        """Test that floor heights are consistent with default"""
        assert constants.LOBBY_HEIGHT == constants.DEFAULT_FLOOR_HEIGHT
        assert constants.OFFICE_HEIGHT == constants.DEFAULT_FLOOR_HEIGHT


class TestGameBalanceConstants:
    """Test game balance-related constants"""

    def test_starting_money(self) -> None:
        """Test starting money constant"""
        assert constants.STARTING_MONEY == Money(1000000)  # Updated to actual value
        assert isinstance(constants.STARTING_MONEY, int)  # Money is NewType based on int
        assert constants.STARTING_MONEY > Money(0)

    def test_money_value_reasonable(self) -> None:
        """Test that starting money is a reasonable amount"""
        # Should be enough to build something, but not unlimited
        assert Money(1000) < constants.STARTING_MONEY <= Money(10000000)  # Updated upper bound


class TestConstantTypes:
    """Test that constants have correct types"""


    def test_integer_constants(self) -> None:
        """Test that integer constants are actually integers"""
        int_constants = [
            constants.SCREEN_WIDTH,
            constants.SCREEN_HEIGHT,
            constants.FPS,
        ]

        for const in int_constants:
            assert isinstance(const, int)

        # Unit types are not plain integers - test separately
        assert isinstance(constants.BLOCK_WIDTH, Blocks)  # Changed from Pixels
        assert isinstance(constants.BLOCK_HEIGHT, Blocks)  # Changed from Pixels
        assert isinstance(constants.FLOORBOARD_HEIGHT, Pixels)
        assert isinstance(constants.DEFAULT_FLOOR_HEIGHT, Blocks)
        assert isinstance(constants.DEFAULT_FLOOR_LEFT_EDGE, Blocks)
        assert isinstance(constants.DEFAULT_FLOOR_WIDTH, Blocks)


    def test_float_constants(self) -> None:
        """Test that float constants are actually floats"""
        float_constants = [
            constants.MIN_TIME_MULTIPLIER,
            constants.MAX_TIME_MULTIPLIER,
            constants.BLOCK_FLOAT_TOLERANCE,
        ]

        for const in float_constants:
            assert isinstance(const, float)


    def test_rgb_constants(self) -> None:
        """Test that RGB constants are tuples of 3 integers"""
        rgb_constants = [
            constants.BACKGROUND_COLOR,
            constants.LOBBY_COLOR,
            constants.OFFICE_COLOR,
            constants.APARTMENT_COLOR,
            constants.HOTEL_COLOR,
            constants.RESTAURANT_COLOR,
            constants.RETAIL_COLOR,
            constants.FLOORBOARD_COLOR,
            constants.DEFAULT_FLOOR_COLOR,
        ]

        for rgb in rgb_constants:
            assert isinstance(rgb, tuple)
            assert len(rgb) == 3
            assert all(isinstance(c, int) for c in rgb)
