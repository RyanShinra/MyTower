# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

# MyTower - A tower building and management game

from enum import Enum
from typing import NewType, TypeAlias

# pylint: disable=c0103
# Type definitions for colors
# RGB color type as a tuple of three integers
RGB: TypeAlias = tuple[int, int, int]
# RGBA color type as a tuple of four integers
RGBA: TypeAlias = tuple[int, int, int, int]
# Either RGB or RGBA
Color: TypeAlias = RGB | RGBA

# Pygame-specific types
MousePos: TypeAlias = tuple[int, int]
MouseButtons: TypeAlias = tuple[bool, bool, bool]

# Floor types as an Enum
class FloorType(Enum):
    LOBBY = "LOBBY"
    OFFICE = "OFFICE"
    APARTMENT = "APARTMENT"
    HOTEL = "HOTEL"
    RESTAURANT = "RESTAURANT"
    RETAIL = "RETAIL"


# Direction types using Enum
class VerticalDirection(Enum):
    DOWN = -1
    STATIONARY = 0
    UP = 1

    def invert(self) -> "VerticalDirection":  # More compatible type annotation
        if self == VerticalDirection.UP:
            return VerticalDirection.DOWN
        elif self == VerticalDirection.DOWN:
            return VerticalDirection.UP
        else:
            return VerticalDirection.STATIONARY


# HorizontalDirection can also be defined similarly if needed
class HorizontalDirection(Enum):
    LEFT = -1
    STATIONARY = 0
    RIGHT = 1


# Person state as an Enum
class PersonState(Enum):
    IDLE = "IDLE"
    WALKING = "WALKING"
    WAITING_FOR_ELEVATOR = "WAITING_FOR_ELEVATOR"
    IN_ELEVATOR = "IN_ELEVATOR"


# Elevator state as an Enum
class ElevatorState(Enum):
    IDLE = "IDLE"
    MOVING = "MOVING"
    ARRIVED = "ARRIVED"
    LOADING = "LOADING"
    UNLOADING = "UNLOADING"
    READY_TO_MOVE = "READY_TO_MOVE"

# Money type (for stronger typing)
Money = NewType("Money", int)

# Grid position
GridPosition: TypeAlias = tuple[int, int]  # (x, y) coordinates in grid cells
