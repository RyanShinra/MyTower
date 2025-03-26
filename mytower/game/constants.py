# game/constants.py
# MyTower - A tower building and management game
# Copyright (C) 2025 [Your Name]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from typing import Final
from game.types import  RGB, Money

# Display constants
SCREEN_WIDTH: Final[int] = 1600
SCREEN_HEIGHT: Final[int] = 1200
FPS: Final[int] = 60
BACKGROUND_COLOR: Final[RGB] = (240, 240, 240)

# Game grid constants
CELL_WIDTH: Final[int] = 40  # Width of a grid cell in pixels
CELL_HEIGHT: Final[int] = 40  # Height of a grid cell in pixels

# Color constants
UI_BACKGROUND_COLOR: Final[RGB] = (220, 220, 220)
UI_BORDER_COLOR: Final[RGB] = (150, 150, 150)
UI_TEXT_COLOR: Final[RGB] = (0, 0, 0)
BUTTON_COLOR: Final[RGB] = (200, 200, 200)
BUTTON_HOVER_COLOR: Final[RGB] = (180, 180, 180)

# Floor colors
LOBBY_COLOR: Final[RGB] = (200, 200, 200)
OFFICE_COLOR: Final[RGB] = (150, 200, 250)
APARTMENT_COLOR: Final[RGB] = (250, 200, 150)
HOTEL_COLOR: Final[RGB] = (200, 150, 250)
RESTAURANT_COLOR: Final[RGB] = (250, 150, 200)
RETAIL_COLOR: Final[RGB] = (150, 250, 200)

# Floor heights
LOBBY_HEIGHT: Final[int] = 1
OFFICE_HEIGHT: Final[int] = 1
APARTMENT_HEIGHT: Final[int] = 1
HOTEL_HEIGHT: Final[int] = 1
RESTAURANT_HEIGHT: Final[int] = 1
RETAIL_HEIGHT: Final[int] = 1

# Elevator constants
ELEVATOR_SHAFT_COLOR: Final[RGB] = (100, 100, 100)
ELEVATOR_CLOSED_COLOR: Final[RGB] = (50, 50, 200)
ELEVATOR_OPEN_COLOR: Final[RGB] = (200, 200, 50)

# Game balance constants
STARTING_MONEY: Final[Money] = Money(100000)