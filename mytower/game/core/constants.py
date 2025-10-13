# game/constants.py
# MyTower - A tower building and management game
# Copyright (C) 2025 [Your Name]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from typing import Final

from mytower.game.core.units import Blocks, Pixels
from mytower.game.core.primitive_constants import BLOCK_FLOAT_TOLERANCE
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger
from mytower.game.core.types import RGB, Money

# We'll initialize this logger properly in main.py
logger_provider = LoggerProvider()
logger: MyTowerLogger = logger_provider.get_logger("constants")

# Display constants
SCREEN_WIDTH: Final[int] = 1600
SCREEN_HEIGHT: Final[int] = 1200

FPS: Final[int] = 60
MIN_TIME_MULTIPLIER: Final[float] = 0.1
MAX_TIME_MULTIPLIER: Final[float] = 10.0

BACKGROUND_COLOR: Final[RGB] = (240, 240, 240)

# Game grid constants

BLOCK_WIDTH: Final[Blocks] = Blocks(1.0)  # Width of a grid cell in meters
BLOCK_HEIGHT: Final[Blocks] = Blocks(1.0)  # Height of a grid cell in meters

BLOCK_FLOAT_TOLERANCE: Final[float] = 0.1  # We comparing two positions to be in the same block
# TODO: We should definitely re-imagine how the colors and heights are organized.
# Floor colors
LOBBY_COLOR: Final[RGB] = (200, 200, 200)
OFFICE_COLOR: Final[RGB] = (150, 200, 250)
APARTMENT_COLOR: Final[RGB] = (250, 200, 150)
HOTEL_COLOR: Final[RGB] = (200, 150, 250)
RESTAURANT_COLOR: Final[RGB] = (250, 150, 200)
RETAIL_COLOR: Final[RGB] = (150, 250, 200)
FLOORBOARD_COLOR: Final[RGB] = (10, 10, 10)
DEFAULT_FLOOR_COLOR: Final[RGB] = (180, 180, 180)

# Floor dimensions
FLOORBOARD_HEIGHT: Final[int] = 4  # Height of the floorboard in pixels
DEFAULT_FLOOR_HEIGHT: Final[Blocks] = Blocks(1)  # Default height of a floor in blocks
DEFAULT_FLOOR_LEFT_EDGE: Final[Blocks] = Blocks(0)  # Default left edge of a floor in blocks
DEFAULT_FLOOR_WIDTH: Final[Blocks] = Blocks(20)  # Default width of a floor in blocks

# Floor heights
# Floors are one block high for now
LOBBY_HEIGHT: Final[Blocks] = Blocks(1)
OFFICE_HEIGHT: Final[Blocks] = Blocks(1)
APARTMENT_HEIGHT: Final[Blocks] = Blocks(1)
HOTEL_HEIGHT: Final[Blocks] = Blocks(1)
RESTAURANT_HEIGHT: Final[Blocks] = Blocks(1)
RETAIL_HEIGHT: Final[Blocks] = Blocks(1)

# Game balance constants
STARTING_MONEY: Final[Money] = Money(100000)
