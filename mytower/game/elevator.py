# game/elevator.py
# This file is part of MyTower.
#
# MyTower is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MyTower is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MyTower. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations  # Defer type evaluation
from typing import List, TYPE_CHECKING

import pygame
from game.constants import (
    BLOCK_WIDTH, BLOCK_HEIGHT,
    ELEVATOR_CLOSED_COLOR, ELEVATOR_OPEN_COLOR, PASSENGER_LOADING_TIME
)
from game.types import ElevatorState, VerticalDirection
from pygame import Surface


if TYPE_CHECKING:
    from game.elevator_bank import ElevatorBank
    from game.person import Person

class Elevator:
    """
    An elevator in the building that transports people between floors.
    """
    def __init__(self, elevator_bank: ElevatorBank, h_cell: int, min_floor: int, max_floor: int, max_velocity: float, max_capacity: int) -> None:
        """
        Initialize a new elevator
        
        Args:
            building: The Building object this elevator belongs to
            x_pos: X position in grid cells
            min_floor: Lowest floor this elevator serves
            max_floor: Highest floor this elevator serves
            max_velocity: Speed in floors per second
        """
        self._parent_elevator_bank: ElevatorBank = elevator_bank
        self.horizontal_block: int = h_cell
        self.min_floor: int = min_floor
        self.max_floor: int = max_floor
        self.max_velocity: float = max_velocity
        self.__max_capacity: int = max_capacity
        
        # Current state
        self._current_floor_pos: float = float(min_floor)  # Floor number (can be fractional when moving)
        self.destination_floor: int = min_floor # Let's not stop between floors
        self.door_open: bool = False
        self._state: ElevatorState = "IDLE"
        self._motion_direction: VerticalDirection = VerticalDirection.STATIONARY  # -1 for down, 0 for stopped, 1 for up
        
        # Used for assignments; What people say: "is this elevator going up or down?"
        # It's only updated when a new destination is assigned
        self._nominal_direction: VerticalDirection = VerticalDirection.STATIONARY 
        self.__passengers: List[Person] = []  # People inside the elevator
        
        self.__unloading_timeout: float = 0.0
        self.__loading_timeout: float = 0.0
        
    @property
    def state(self) -> ElevatorState:
        return self._state
    
    @property
    def avail_capacity(self) -> int:
        return self.__max_capacity - len(self.__passengers)
    
    @property
    def is_empty(self) -> bool:
        return len(self.__passengers) == 0
    
    @property
    def motion_direction(self) -> VerticalDirection:
        return self._motion_direction
        
    @property
    def nominal_direction(self) -> VerticalDirection:
        return self._nominal_direction
    
    @property
    def current_floor(self) -> int:
        return int(self._current_floor_pos)
    
    @property
    def fractional_floor(self) -> float:
        return self._current_floor_pos
    
    @property
    def parent_elevator_bank(self) -> ElevatorBank:
        return self._parent_elevator_bank
    
    def set_destination_floor(self, dest_floor: int) -> None:
        if (dest_floor > self.max_floor) or (dest_floor < self.min_floor):
            raise ValueError(f"Destination floor {dest_floor} is out of bounds. Valid range: {self.min_floor} to {self.max_floor}.")
        
        if self.current_floor < dest_floor:
            self._motion_direction = VerticalDirection.UP
            self._nominal_direction = VerticalDirection.UP
        elif self.current_floor > dest_floor:
            self._motion_direction = VerticalDirection.DOWN
            self._nominal_direction = VerticalDirection.DOWN
        else:
            self._motion_direction = VerticalDirection.STATIONARY
            self._nominal_direction = VerticalDirection.STATIONARY
            
        self.destination_floor = dest_floor

    def request_load_passengers(self) -> None:
        if self.state == "IDLE":
            self._state = "LOADING"
        else:
            raise RuntimeError(f"Cannot load passengers while elevator is in {self.state} state")

    def passengers_who_want_off(self) -> List[Person]:
        answer: List[Person] = []
        for p in self.__passengers:
            if p.destination_floor == self.current_floor:
                answer.append(p)
                
        return answer
    
    def get_passenger_destinations_in_direction(self, floor: int, direction: VerticalDirection) -> List[int]:
        """ Returns sorted list of floors in the direction of travel"""
        
        if direction == VerticalDirection.STATIONARY:
            raise ValueError(f"Cannot get passenger requests for STATIONARY direction from floor {floor}")
        
        floors_set: set[int] = set()
        for p in self.__passengers:
            if direction == VerticalDirection.UP and p.destination_floor > floor:
                floors_set.add(p.destination_floor)
            
            elif direction == VerticalDirection.DOWN and p.destination_floor < floor:
                floors_set.add(p.destination_floor)
        
        sorted_floors: List[int] = list(floors_set)
        if direction == VerticalDirection.UP:
            sorted_floors.sort()
        elif direction == VerticalDirection.DOWN:
            sorted_floors.sort(reverse=True)
        
        return sorted_floors
        
    def update(self, dt: float) -> None:
        """Update elevator status over time increment dt (in seconds)"""
        match self._state:
            case "IDLE":
                self.door_open = False
                self._motion_direction = VerticalDirection.STATIONARY
            
            case "MOVING":
                # Continue moving towards the destination floor
                self.door_open = False
                self.update_moving(dt)
            
            case "ARRIVED":
                self.update_arrived(dt)
            
            case "UNLOADING":
                # Allow people to exit the elevator
                self.door_open = True
                self.update_unloading(dt)
            
            case "LOADING":
                # Allow people to enter or exit the elevator
                self.door_open = True
                self.update_loading(dt)

            case _:
                raise ValueError(f"Unknown elevator state: {self._state}")
        
        
    def update_moving(self, dt: float) -> None:
        cur_floor: float = self.current_floor + dt * self.max_velocity * self.motion_direction.value
              
        done: bool = False
        
        if self.motion_direction == VerticalDirection.UP:
            if cur_floor >= self.destination_floor:
                done = True
        elif self.motion_direction == VerticalDirection.DOWN:
            if cur_floor <= self.destination_floor:
                done = True
                
        if done:
            cur_floor = self.destination_floor
            self._state = "ARRIVED"
            self._motion_direction = VerticalDirection.STATIONARY
        
        cur_floor = min(self.max_floor, cur_floor)
        cur_floor = max(self.min_floor, cur_floor)
        self._current_floor_pos = cur_floor
        
    def update_arrived(self, dt: float) -> None:
        who_wants_off: List[Person] = self.passengers_who_want_off()
        
        if len(who_wants_off) > 0:
            self._state = "UNLOADING"
        else:
            self._state = "IDLE"
    
    def update_unloading(self, dt: float) -> None:
        self.__unloading_timeout += dt
        if self.__unloading_timeout < PASSENGER_LOADING_TIME:
            return
        
        self.__unloading_timeout = 0.0
        who_wants_off: List[Person] = self.passengers_who_want_off()
        
        if len(who_wants_off) > 0:
            disembarking_passenger: Person = who_wants_off.pop()
            self.__passengers.remove(disembarking_passenger)
            disembarking_passenger.disembark_elevator()
        else:
            self._state = "LOADING"
        return    
    
    def update_loading(self, dt: float) -> None:
        self.__loading_timeout += dt
        if self.__loading_timeout < PASSENGER_LOADING_TIME:
            return
        
        self.__loading_timeout = 0.0
        
        # We could have an "Overstuffed" option here in the future
        if self.avail_capacity <= 0:
            self._state = "IDLE" # We're full, get ready to move
            self.door_open = False
            return
        
        # There is still room, add a person
        who_wants_on: Person | None = self.parent_elevator_bank.dequeue_waiting_passenger(self.current_floor, self.nominal_direction)
        if who_wants_on is not None:
            who_wants_on.board_elevator(self)
            self.__passengers.append(who_wants_on)
        else:
            self._state = "IDLE" # Nobody else wants to get on
            self.door_open = False
        return
    
    
    def draw(self, surface: Surface) -> None:
        """Draw the elevator on the given surface"""
        # Calculate positions
        screen_height = surface.get_height()
        #   450 = 480 - (1.5 * 20) 
        # We want the private member here since it's a float and we're computing pixels
        car_top = screen_height - int(self._current_floor_pos * BLOCK_HEIGHT)
        shaft_left = self.horizontal_block * BLOCK_WIDTH
        width = BLOCK_WIDTH
        
        # Draw shaft from min to max floor
        #     420 = 480 - (3 * 20)
        # shaft_top = screen_height - (self.max_floor * BLOCK_HEIGHT)
        # shaft_overhead = screen_height - ((self.max_floor + 1) * BLOCK_HEIGHT)
        #     480 = 480 - ((1 - 1) * 20)
        # shaft_bottom = screen_height - ((self.min_floor - 1) * BLOCK_HEIGHT)
        # pygame.draw.rect(
        #     surface,
        #     ELEVATOR_SHAFT_COLOR,
        #     (shaft_left, shaft_top, width, shaft_bottom - shaft_top)
        # )
        
        # pygame.draw.rect(
        #     surface,
        #     UI_TEXT_COLOR,
        #     (shaft_left, shaft_overhead, width, shaft_top - shaft_overhead)
        # )
        
        # Draw elevator car
        color = ELEVATOR_OPEN_COLOR if self.door_open else ELEVATOR_CLOSED_COLOR
        pygame.draw.rect(
            surface,
            color,
            (shaft_left, car_top, width, BLOCK_HEIGHT)
        )
        
        # Draw any passengers or other elements after the elevator
        # to make them appear on top of the elevator
        # TODO: Depending on the size of the passenger icon, we can add judder here later to make it look crowded
        for p in self.__passengers:
            p.draw(surface)
        