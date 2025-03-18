# game/constants.py
# MyTower - A tower building and management game
# Copyright (C) 2025 [Your Name]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from typing import Final

# Display constants
SCREEN_WIDTH: Final = 800
SCREEN_HEIGHT: Final = 600
FPS: Final = 60
BACKGROUND_COLOR: Final = (240, 240, 240)

# Game grid constants
CELL_WIDTH: Final = 20  # Width of a grid cell in pixels
CELL_HEIGHT: Final = 20  # Height of a grid cell in pixels

# Color constants
UI_BACKGROUND_COLOR: Final = (220, 220, 220)
UI_BORDER_COLOR: Final = (150, 150, 150)
UI_TEXT_COLOR: Final = (0, 0, 0)
BUTTON_COLOR: Final = (200, 200, 200)
BUTTON_HOVER_COLOR: Final = (180, 180, 180)

# Floor colors
LOBBY_COLOR: Final = (200, 200, 200)
OFFICE_COLOR: Final = (150, 200, 250)
APARTMENT_COLOR: Final = (250, 200, 150)
HOTEL_COLOR: Final = (200, 150, 250)
RESTAURANT_COLOR: Final = (250, 150, 200)
RETAIL_COLOR: Final = (150, 250, 200)

# Elevator constants
ELEVATOR_SHAFT_COLOR: Final = (100, 100, 100)
ELEVATOR_CLOSED_COLOR: Final = (50, 50, 200)
ELEVATOR_OPEN_COLOR: Final = (200, 200, 50)

# Game balance constants
STARTING_MONEY: Final = 100000