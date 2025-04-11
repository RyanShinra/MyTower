# game/person.py
# This file is part of MyTower. 
# Copyright (C) 2025 [Your Name]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from __future__ import annotations  # Defer type evaluation
from typing import TYPE_CHECKING, Final, List

import random
import pygame
from game.constants import BLOCK_WIDTH, BLOCK_HEIGHT, PERSON_INIT_BLUE, PERSON_INIT_GREEN, PERSON_INIT_RED, PERSON_MAX_RED, PERSON_MAX_WAIT_TIME, PERSON_MIN_BLUE, PERSON_MIN_GREEN, PERSON_MIN_RED
from game.types import HorizontalDirection, PersonState
from mytower.game.elevator import Elevator

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
        self._current_floor: float = float(current_floor)
        self.current_block: float = current_block
        self._dest_block: int = int(current_block)
        self._dest_floor: int = current_floor
        self.state: PersonState = "IDLE"  # IDLE, WALKING, WAITING_FOR_ELEVATOR, IN_ELEVATOR
        self.direction: HorizontalDirection = HorizontalDirection.STATIONARY
        self.max_velocity: float = max_velocity
        self._next_elevator_bank: ElevatorBank | None = None
        self.__idle_timeout: float = 0
        self.__current_elevator: Elevator | None = None
        self.__waiting_time: float = 0  # How long have we been waiting for elevator (or something else, I suppose)
                
        # Appearance (for visualization)
        self.__original_red: Final[int] = random.randint(PERSON_MIN_RED, PERSON_INIT_RED) # let's save some red for being mad at the elevator
        self.__original_green: Final[int] = random.randint(PERSON_MIN_GREEN, PERSON_INIT_GREEN)
        self.__original_blue: Final[int] = random.randint(PERSON_MIN_BLUE, PERSON_INIT_BLUE)

        
    @property
    def current_floor(self) -> int:
        return int(self._current_floor)
    
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

    def board_elevator(self, elevator: Elevator) -> None:
        self.__current_elevator = elevator
        self.__waiting_time = 0.0
        self.state = "IN_ELEVATOR"
    
    def disembark_elevator(self) -> None:
        if self.__current_elevator is None:
            raise RuntimeError("Cannot disembark elevator: no elevator is currently boarded.")
        
        self.current_block = self.__current_elevator.parent_elevator_bank.get_waiting_block()
        self._current_floor = float(self.__current_elevator.current_floor)
        self.__waiting_time = 0.0
        self.__current_elevator = None
        self.state = "WALKING"
    
    
    def update(self, dt: float) -> None:
        """Update person's state and position"""
        match self.state:
            case "IDLE":
                self.update_idle(dt)

            case "WALKING":
                self.update_walking(dt)
            
            case "WAITING_FOR_ELEVATOR":
                # Later on, we can do the staggered line appearance here
                self.__waiting_time += dt
                # Eventually, we can handle "Storming off to another elevator / stairs / managers office" here
            
            case "IN_ELEVATOR":
                if self.__current_elevator:
                    self.__waiting_time += dt
                    self._current_floor = self.__current_elevator.fractional_floor
                    self.current_block = self.__current_elevator.parent_elevator_bank.horizontal_block
            
            case _:
                # Handle unexpected states
                # print(f"Unknown state: {self.state}")
                pass
             
    def update_idle(self, dt: float) -> None:
        self.direction = HorizontalDirection.STATIONARY
        
        self.__idle_timeout = max(0, self.__idle_timeout - dt)
        if self.__idle_timeout > 0.0:
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
                self.__idle_timeout = 5.0
        
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
        # Note: this needs to be the private, float _current_floor
        y_pos: int = screen_height - int(((self._current_floor - 1.0) * BLOCK_HEIGHT) - (BLOCK_HEIGHT / 2))
        x_pos: int = int(self.current_block * BLOCK_WIDTH + BLOCK_WIDTH / 2)
        
        # How mad ARE we??
        mad_fraction: float = self.__waiting_time / PERSON_MAX_WAIT_TIME
        draw_red: int = self.__original_red + int(abs(PERSON_MAX_RED - self.__original_red) * mad_fraction)
        draw_green: int = self.__original_green - int(abs(self.__original_green - PERSON_MIN_GREEN) * mad_fraction)
        draw_blue: int = self.__original_blue - int(abs(self.__original_blue - PERSON_MIN_BLUE) * mad_fraction)
        
        
        
        pygame.draw.circle(
            surface,
            (draw_red, draw_green, draw_blue),
            (int(x_pos), int(y_pos)),
            5  # radius
        )