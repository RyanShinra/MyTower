# game/types.py
# MyTower - A tower building and management game
# Copyright (C) 2025 [Your Name]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from typing import Tuple, Literal, TypeAlias, Union, NewType
import pygame
from enum import Enum

# Type definitions for colors
# RGB color type as a tuple of three integers
RGB: TypeAlias = Tuple[int, int, int]
# RGBA color type as a tuple of four integers
RGBA: TypeAlias = Tuple[int, int, int, int]
# Either RGB or RGBA
Color: TypeAlias = Union[RGB, RGBA]

# Pygame-specific types
MousePos: TypeAlias = Tuple[int, int]
MouseButtons: TypeAlias = Tuple[bool, bool, bool]
PygameSurface: TypeAlias = pygame.Surface

# Floor types with string literals
FloorType: TypeAlias = Literal["LOBBY", "OFFICE", "APARTMENT", "HOTEL", "RESTAURANT", "RETAIL"]


# Direction types using Enum
class VerticalDirection(Enum):
    DOWN = -1
    STATIONARY = 0
    UP = 1

# HorizontalDirection can also be defined similarly if needed
class HorizontalDirection(Enum):
    LEFT = -1
    STATIONARY = 0
    RIGHT = 1
    
# Person state type
PersonState: TypeAlias = Literal["IDLE", "WALKING", "WAITING_FOR_ELEVATOR", "IN_ELEVATOR"]

# Elevator state type
ElevatorState: TypeAlias = Literal["IDLE", "MOVING", "ARRIVED", "LOADING", "UNLOADING", "READY_TO_MOVE"]

# Money type (for stronger typing)
Money = NewType('Money', int)

# Grid position
GridPosition: TypeAlias = Tuple[int, int]  # (x, y) coordinates in grid cells