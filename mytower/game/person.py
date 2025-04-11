# game/person.py
# This file is part of MyTower. 
# Copyright (C) 2025 [Your Name]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from __future__ import annotations  # Defer type evaluation
from typing import TYPE_CHECKING, List

import random
import pygame
from game.constants import BLOCK_WIDTH, BLOCK_HEIGHT
from game.types import HorizontalDirection, PersonState

if TYPE_CHECKING:
    from pygame import Surface
    from game.building import Building
    from game.elevator_bank import ElevatorBank
    

class Person:
    """
    A person in the building who moves between floors and has needs.
    """
    def __init__(self, building: Building, current_floor: int, current_block: float, max_velocity: float) -> None:
        self.building: Building = building
        self._current_floor: int = current_floor
        self.current_block: float = current_block
        self._dest_block: int = int(current_block)
        self._dest_floor: int = current_floor
        self.state: PersonState = "IDLE"  # IDLE, WALKING, WAITING_FOR_ELEVATOR, IN_ELEVATOR
        self.direction: HorizontalDirection = HorizontalDirection.STATIONARY
        self.max_velocity: float = max_velocity
        self._next_elevator_bank: ElevatorBank | None = None
        self.__idle_timout: float = 0
                
        # Appearance (for visualization)
        self.color = (
            random.randint(0, 32), # let's save some red for being mad at the elevator
            random.randint(0, 128),
            random.randint(0, 128)
        )
        
    @property
    def current_floor(self) -> int:
        return self._current_floor
    
    @property
    def destination_floor(self)-> int:
        return self._dest_floor
                
    def set_destination(self, dest_floor: int, dest_block: int) -> None:
        dest_floor = min(dest_floor, self.building.num_floors)
        dest_floor = max(dest_floor, 0)
        self._dest_floor = dest_floor
        
        dest_block = min(dest_block, self.building.floor_width)
        dest_block = max(dest_block, 0)
        self._dest_block = dest_block
        
    def find_nearest_elevator_bank(self) -> None | ElevatorBank:
        elevator_list: List[ElevatorBank] = self.building.get_elevator_banks_on_floor(self.current_floor)
        closest_el = None
        closest_dist: float = float(self.building.floor_width + 5)
        
        for elevator in elevator_list :
            dist: float = abs(elevator.horizontal_block - self.current_block)
            if (dist < closest_dist) :
                closest_dist = dist
                closest_el = elevator
                
        return closest_el

        
    def update(self, dt: float) -> None:
        """Update person's state and position"""
        match self.state:
            case "IDLE":
                self.update_idle(dt)

            case "WALKING":
                self.update_walking(dt)
                pass
            case "WAITING_FOR_ELEVATOR":
                # Handle waiting for elevator
                pass
            case "IN_ELEVATOR":
                # Handle in elevator state
                pass
            case _:
                # Handle unexpected states
                # print(f"Unknown state: {self.state}")
                pass
             
    def update_idle(self, dt: float) -> None:
        self.direction = HorizontalDirection.STATIONARY
        
        self.__idle_timout = max(0, self.__idle_timout - dt)
        if self.__idle_timout > 0.0:
            return
        
        current_destination_block: float = float(self._dest_block)
        
        if self._dest_floor != self.current_floor:
            # Find the nearest elevator, go in that direction
            self._next_elevator_bank = self.find_nearest_elevator_bank()
            if self._next_elevator_bank:
                # TODO: Bounds wrap this to block 1 (i.e. have them board on the right)
                current_destination_block = float(self._next_elevator_bank.get_waiting_block())
                self.state = "WALKING" # This is technically redundant (I think), I may remove it soon...
            else:
                # There's no elevator on this floor, maybe one is coming soon...
                current_destination_block = self.current_block # why move? There's nowhere to go
                self.state = "IDLE" # This is also prob's redundant (Since we were already idle)
                # Set a timer so that we don't run this constantly (like every 5 seconds)
                self.__idle_timout = 5.0
        
        if current_destination_block < self.current_block:
            # Already on the right floor (or walking to elevator?)
            self.state = "WALKING"
            self.direction = HorizontalDirection.LEFT    
        
        elif current_destination_block > self.current_block:
            self.state = "WALKING"
            self.direction = HorizontalDirection.RIGHT

    def update_walking(self, dt: float) -> None:
        done: bool = False
        
        current_destination_block = self._dest_block
        if self._next_elevator_bank:
            # TODO: Probably need a next_block_this_floor or some such for all these walking directions
            current_destination_block = self._next_elevator_bank.get_waiting_block()
            pass
        
        if current_destination_block < self.current_block:
            self.direction = HorizontalDirection.LEFT    
        
        elif current_destination_block > self.current_block:
            self.direction = HorizontalDirection.RIGHT

        next_block: float = self.current_block + dt * self.max_velocity * self.direction.value
        if self.direction == HorizontalDirection.RIGHT:
            if next_block >= current_destination_block:
                done = True
        elif self.direction == HorizontalDirection.LEFT:
            if next_block <= current_destination_block:
                done = True
        
        if done:
            self.direction = HorizontalDirection.STATIONARY
            next_block = current_destination_block
            if self._next_elevator_bank:
                self._next_elevator_bank.add_waiting_passenger(self)
                self.state = "WAITING_FOR_ELEVATOR"
            else:
                self.state = "IDLE"    
        
        # TODO: Update these once we have building extents
        next_block = min(next_block, self.building.floor_width)
        next_block = max(next_block, 0)
        self.current_block = next_block    

    
    def draw(self, surface: Surface) -> None:
        """Draw the person on the given surface"""
        # Calculate position and draw a simple circle for now
        screen_height = surface.get_height()
        y_pos = screen_height - ((self.current_floor - 1) * BLOCK_HEIGHT) - (BLOCK_HEIGHT / 2)
        x_pos = self.current_block * BLOCK_WIDTH + BLOCK_WIDTH / 2
        
        # Print coordinates for debugging
        
        
        pygame.draw.circle(
            surface,
            self.color,
            (int(x_pos), int(y_pos)),
            5  # radius
        )