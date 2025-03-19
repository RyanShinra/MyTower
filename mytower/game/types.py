# game/types.py
# MyTower - A tower building and management game
# Copyright (C) 2025 [Your Name]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from typing import Tuple, Literal, TypeAlias, Union, NewType

# Type definitions for colors
# RGB color type as a tuple of three integers
RGB: TypeAlias = Tuple[int, int, int]
# RGBA color type as a tuple of four integers
RGBA: TypeAlias = Tuple[int, int, int, int]
# Either RGB or RGBA
Color: TypeAlias = Union[RGB, RGBA]

# Floor types with string literals
FloorType: TypeAlias = Literal["LOBBY", "OFFICE", "APARTMENT", "HOTEL", "RESTAURANT", "RETAIL"]

# Direction types
Direction: TypeAlias = Literal[-1, 0, 1]  # -1 for down, 0 for stationary, 1 for up

# Person state type
PersonState: TypeAlias = Literal["IDLE", "WALKING", "WAITING_FOR_ELEVATOR", "IN_ELEVATOR"]

# Elevator state type
ElevatorState: TypeAlias = Literal["IDLE", "MOVING", "LOADING", "UNLOADING"]

# Money type (for stronger typing)
Money = NewType('Money', int)

# Grid position
GridPosition: TypeAlias = Tuple[int, int]  # (x, y) coordinates in grid cells