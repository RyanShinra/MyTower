# game/types.py
# MyTower - A tower building and management game
# Copyright (C) 2025 [Your Name]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from typing import Tuple, TypeAlias, Union, NewType
import pygame
from enum import Enum
from game.logger import LoggerProvider

# We'll initialize the logger properly in main.py
logger_provider = LoggerProvider()
logger = logger_provider.get_logger("types")

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
Money = NewType('Money', int)

# Grid position
GridPosition: TypeAlias = Tuple[int, int]  # (x, y) coordinates in grid cells