# game/constants.py
# MyTower - A tower building and management game
# Copyright (C) 2025 [Your Name]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from typing import Final

from mytower.game.logger import LoggerProvider
from mytower.game.types import RGB, Money

# We'll initialize this logger properly in main.py
logger_provider = LoggerProvider()
logger = logger_provider.get_logger("constants")

# Display constants
SCREEN_WIDTH: Final[int] = 1600
SCREEN_HEIGHT: Final[int] = 1200
FPS: Final[int] = 60
BACKGROUND_COLOR: Final[RGB] = (240, 240, 240)

# Game grid constants
BLOCK_WIDTH: Final[int] = 40  # Width of a grid cell in pixels, 3.0m
BLOCK_HEIGHT: Final[int] = 40  # Height of a grid cell in pixels, 3.0m

# TODO: We should definitely re-imagine how the colors and heights are organized.
# Floor colors
LOBBY_COLOR: Final[RGB] = (200, 200, 200)
OFFICE_COLOR: Final[RGB] = (150, 200, 250)
APARTMENT_COLOR: Final[RGB] = (250, 200, 150)
HOTEL_COLOR: Final[RGB] = (200, 150, 250)
RESTAURANT_COLOR: Final[RGB] = (250, 150, 200)
RETAIL_COLOR: Final[RGB] = (150, 250, 200)
FLOORBOARD_COLOR: Final[RGB] = (10, 10, 10)

# Floor heights
LOBBY_HEIGHT: Final[int] = 1
OFFICE_HEIGHT: Final[int] = 1
APARTMENT_HEIGHT: Final[int] = 1
HOTEL_HEIGHT: Final[int] = 1
RESTAURANT_HEIGHT: Final[int] = 1
RETAIL_HEIGHT: Final[int] = 1

# Game balance constants
STARTING_MONEY: Final[Money] = Money(100000)
