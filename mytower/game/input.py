# game/input.py
# MyTower - A tower building and management game
# Copyright (C) 2025 [Your Name]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# from typing import Tuple, List, Dict, Any, Protocol, cast # type: ignore
from typing import List

import pygame

from mytower.game.logger import LoggerProvider, MyTowerLogger
from mytower.game.types import MouseButtons, MousePos


class MouseState:
    """Class to store and manage mouse state"""

    def __init__(self, logger_provider: LoggerProvider) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("input")
        self._position: MousePos = (0, 0)
        self._buttons: MouseButtons = (False, False, False)
        # Store additional button states if needed
        self._extended_buttons: List[bool] = []
        self._wheel_y: int = 0  # Vertical scroll
        self._wheel_x: int = 0  # Horizontal scroll (if supported)

    def update(self) -> None:
        """Update mouse state from pygame"""
        # Get mouse position
        self._position = pygame.mouse.get_pos()

        # Get button states
        # Convert to our stable format
        button_states = pygame.mouse.get_pressed()

        # Handle the basic three buttons which are guaranteed in our type
        self._buttons = (
            button_states[0] if len(button_states) > 0 else False,
            button_states[1] if len(button_states) > 1 else False,
            button_states[2] if len(button_states) > 2 else False,
        )

        # Store extended buttons if pygame returns more than 3
        self._extended_buttons = [button_states[i] for i in range(3, len(button_states))]

    def get_pressed(self) -> MouseButtons:
        """Get the current state of the mouse buttons"""
        return self._buttons

    def get_extended_pressed(self) -> List[bool]:
        """Get the state of additional mouse buttons beyond the standard three"""
        return self._extended_buttons

    def get_pos(self) -> MousePos:
        """Get the current mouse position"""
        return self._position

    def is_button_pressed(self, button_idx: int) -> bool:
        """
        Check if a specific button is pressed

        Args:
            button_idx: Button index (0 = left, 1 = middle, 2 = right, 3+ = extra buttons)

        Returns:
            True if the button is pressed, False otherwise
        """
        if button_idx < 3:
            return self._buttons[button_idx]
        elif button_idx - 3 < len(self._extended_buttons):
            return self._extended_buttons[button_idx - 3]
        return False


# Global mouse state instance
# This will be initialized properly in main.py
mouse = MouseState(LoggerProvider())
