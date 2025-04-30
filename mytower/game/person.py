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

from game.constants import BLOCK_WIDTH, BLOCK_HEIGHT, PERSON_INIT_BLUE, PERSON_INIT_GREEN, PERSON_INIT_RED, PERSON_MAX_RED, PERSON_MAX_WAIT_TIME, PERSON_MIN_BLUE, PERSON_MIN_GREEN, PERSON_MIN_RED, PERSON_RADIUS
from game.types import HorizontalDirection, PersonState
from game.elevator import Elevator
from game.logger import get_logger

logger = get_logger("person")

if TYPE_CHECKING:
    from pygame import Surface
    from game.building import Building
    from game.elevator_bank import ElevatorBank
    

class Person:
    """
    A person in the building who moves between floors and has needs.
    """
    def __init__(self, building: Building, current_floor: int, current_block: float, max_velocity: float) -> None:
        self._building: Building = building
        self._current_floor_float: float = float(current_floor)
        self._current_block: float = current_block
        self._dest_block: int = int(current_block)
        self._dest_floor: int = current_floor
        self._state: PersonState = "IDLE"  # IDLE, WALKING, WAITING_FOR_ELEVATOR, IN_ELEVATOR
        self._direction: HorizontalDirection = HorizontalDirection.STATIONARY
        self._max_velocity: float = max_velocity
        self._next_elevator_bank: ElevatorBank | None = None
        self._idle_timeout: float = 0
        self._current_elevator: Elevator | None = None
        self._waiting_time: float = 0  # How long have we been waiting for elevator (or something else, I suppose)
                
        # Appearance (for visualization)
        self._original_red: Final[int] = random.randint(PERSON_MIN_RED, PERSON_INIT_RED) # let's save some red for being mad at the elevator
        self._original_green: Final[int] = random.randint(PERSON_MIN_GREEN, PERSON_INIT_GREEN)
        self._original_blue: Final[int] = random.randint(PERSON_MIN_BLUE, PERSON_INIT_BLUE)

        
    @property
    def building(self) -> Building:
        return self._building
        
    @property
    def current_floor(self) -> int:
        return int(self._current_floor_float)
    
    @property
    def current_block(self) -> float:
        return self._current_block
        
    @current_block.setter
    def current_block(self, value: float) -> None:
        self._current_block = value
    
    @property
    def destination_floor(self)-> int:
        return self._dest_floor
        
    @property
    def state(self) -> PersonState:
        return self._state
        
    @state.setter
    def state(self, value: PersonState) -> None:
        self._state = value
        
    @property
    def direction(self) -> HorizontalDirection:
        return self._direction
        
    @direction.setter
    def direction(self, value: HorizontalDirection) -> None:
        self._direction = value
        
    @property
    def max_velocity(self) -> float:
        return self._max_velocity
    
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
            # TODO: Add logic to skip elevator banks that don't go to dest floor
            dist: float = abs(elevator.horizontal_block - self._current_block)
            if (dist < closest_dist) :
                closest_dist = dist
                closest_el = elevator
                
        return closest_el

    def board_elevator(self, elevator: Elevator) -> None:
        self._current_elevator = elevator
        self._waiting_time = 0.0
        self.state = "IN_ELEVATOR"
    
    def disembark_elevator(self) -> None:
        if self._current_elevator is None:
            raise RuntimeError("Cannot disembark elevator: no elevator is currently boarded.")
        
        self._current_block = self._current_elevator.parent_elevator_bank.get_waiting_block()
        self._current_floor_float = float(self._current_elevator.current_floor_int)
        self._waiting_time = 0.0
        self._current_elevator = None
        self._next_elevator_bank = None
        self.state = "IDLE"
    
    
    def update(self, dt: float) -> None:
        """Update person's state and position"""
        match self.state:
            case "IDLE":
                self.update_idle(dt)

            case "WALKING":
                self.update_walking(dt)
            
            case "WAITING_FOR_ELEVATOR":
                # Later on, we can do the staggered line appearance here
                self._waiting_time += dt
                # Eventually, we can handle "Storming off to another elevator / stairs / managers office" here
            
            case "IN_ELEVATOR":
                if self._current_elevator:
                    self._waiting_time += dt
                    self._current_floor_float = self._current_elevator.fractional_floor
                    self._current_block = self._current_elevator.parent_elevator_bank.horizontal_block
            
            case _:
                # Handle unexpected states
                logger.warning(f"Unknown state: {self.state}")
             
            
    def update_idle(self, dt: float) -> None:
        self.direction = HorizontalDirection.STATIONARY
        
        self._idle_timeout = max(0, self._idle_timeout - dt)
        if self._idle_timeout > 0.0:
            return
        
        current_destination_block: float = float(self._dest_block)
        
        if self._dest_floor != self.current_floor:
            # Find the nearest elevator, go in that direction
            self._next_elevator_bank = self.find_nearest_elevator_bank()
            if self._next_elevator_bank:
                current_destination_block = float(self._next_elevator_bank.get_waiting_block())
                logger.trace(f'IDLE Person: Destination fl. {self.destination_floor} != current fl. {self.current_floor} -> WALKING to Elevator block: {current_destination_block}')
                self.state = "WALKING" # This is technically redundant (I think), I may remove it soon...
            else:
                # There's no elevator on this floor, maybe one is coming soon...
                current_destination_block = self._current_block # why move? There's nowhere to go
                logger.trace(f'IDLE Person: Destination fl. {self.destination_floor} != current fl. {self.current_floor} -> IDLE b/c no Elevator on this floor')
                self.state = "IDLE" # This is also prob's redundant (Since we were already idle)
                # Set a timer so that we don't run this constantly (like every 5 seconds)
                self._idle_timeout = 5.0
        
        if current_destination_block < self._current_block:
            # Already on the right floor (or walking to elevator?)
            logger.trace(f'IDLE Person: Destination is on this floor: {self.destination_floor}, WALKING LEFT to block: {current_destination_block}')
            self.state = "WALKING"
            self.direction = HorizontalDirection.LEFT    
        
        elif current_destination_block > self._current_block:
            logger.trace(f'IDLE Person: Destination is on this floor: {self.destination_floor}, WALKING RIGHT to block: {current_destination_block}')
            self.state = "WALKING"
            self.direction = HorizontalDirection.RIGHT

    def update_walking(self, dt: float) -> None:
        done: bool = False
        
        waypoint_block = self._dest_block
        if self._next_elevator_bank:
            # TODO: Probably need a next_block_this_floor or some such for all these walking directions
            waypoint_block = self._next_elevator_bank.get_waiting_block()
            pass
        
        if waypoint_block < self._current_block:
            self.direction = HorizontalDirection.LEFT    
        
        elif waypoint_block > self._current_block:
            self.direction = HorizontalDirection.RIGHT

        next_block: float = self._current_block + dt * self._max_velocity * self.direction.value
        if self.direction == HorizontalDirection.RIGHT:
            if next_block >= waypoint_block:
                done = True
        elif self.direction == HorizontalDirection.LEFT:
            if next_block <= waypoint_block:
                done = True
        
        if done:
            self.direction = HorizontalDirection.STATIONARY
            next_block = waypoint_block
            if self._next_elevator_bank:
                self._next_elevator_bank.add_waiting_passenger(self)
                self.state = "WAITING_FOR_ELEVATOR"
            else:
                self.state = "IDLE"    
            logger.debug(f'WALKING Person: Arrived at destination (fl {self.current_floor}, bk {waypoint_block}) -> {self.state}')
        
        # TODO: Update these once we have building extents
        next_block = min(next_block, self.building.floor_width)
        next_block = max(next_block, 0)
        self._current_block = next_block    

    
    def draw(self, surface: Surface) -> None:
        """Draw the person on the given surface"""
        # Calculate position and draw a simple circle for now
        screen_height = surface.get_height()
        
        # Note: this needs to be the private, float _current_floor
        apparent_floor:float = self._current_floor_float - 1.0
        y_bottom: float = apparent_floor * BLOCK_HEIGHT
        y_centered:int = int(y_bottom + (BLOCK_HEIGHT / 2))
        
        # Need to invert y coordinates
        y_pos: int = screen_height - y_centered
        
        x_left: float = self._current_block * BLOCK_WIDTH
        x_centered: float = int(x_left + (BLOCK_WIDTH / 2))
        x_pos: int = x_centered
        
        # How mad ARE we??
        mad_fraction: float = self._waiting_time / PERSON_MAX_WAIT_TIME
        draw_red: int = self._original_red + int(abs(PERSON_MAX_RED - self._original_red) * mad_fraction)
        draw_green: int = self._original_green - int(abs(self._original_green - PERSON_MIN_GREEN) * mad_fraction)
        draw_blue: int = self._original_blue - int(abs(self._original_blue - PERSON_MIN_BLUE) * mad_fraction)
        
        # Clamp the draw colors to the range 0 to 254
        draw_red = max(0, min(254, draw_red))
        draw_green = max(0, min(254, draw_green))
        draw_blue = max(0, min(254, draw_blue))
        
        draw_color = (draw_red, draw_green, draw_blue)
        # logger.debug(f"Person color: {draw_color}, person location: {(int(x_pos), int(y_pos))}")
        
        pygame.draw.circle(
            surface,
            draw_color,
            (int(x_pos), int(y_pos)),
            PERSON_RADIUS  # radius  
        )