# game/person.py
# This file is part of MyTower.
# Copyright (C) 2025 [Your Name]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# flake8: noqa: E701

from __future__ import annotations  # Defer type evaluation

import random
from typing import TYPE_CHECKING, Final, List, Protocol, override

from mytower.game.core.config import GameConfig
from mytower.game.entities.elevator import Elevator

from mytower.game.utilities.logger import MyTowerLogger
from mytower.game.core.types import HorizontalDirection, PersonState


from mytower.game.core.id_generator import IDGenerator


if TYPE_CHECKING:
    from mytower.game.entities.building import Building
    from mytower.game.entities.elevator_bank import ElevatorBank
    from mytower.game.entities.floor import Floor
    from mytower.game.utilities.logger import LoggerProvider



# pylint: disable=invalid-name
class PersonConfigProtocol(Protocol):
    """Config requirements for Person class"""

    @property
    def MAX_SPEED(self) -> float: ...

    @property
    def MAX_WAIT_TIME(self) -> float: ...

    @property
    def IDLE_TIMEOUT(self) -> float: ...

    @property
    def RADIUS(self) -> int: ...



class PersonCosmeticsProtocol(Protocol):
    """Visual appearance settings for Person class"""

    @property
    def ANGRY_MAX_RED(self) -> int: ...

    @property
    def ANGRY_MIN_GREEN(self) -> int: ...

    @property
    def ANGRY_MIN_BLUE(self) -> int: ...

    @property
    def INITIAL_MAX_RED(self) -> int: ...

    @property
    def INITIAL_MAX_GREEN(self) -> int: ...

    @property
    def INITIAL_MAX_BLUE(self) -> int: ...

    @property
    def INITIAL_MIN_RED(self) -> int: ...

    @property
    def INITIAL_MIN_GREEN(self) -> int: ...

    @property
    def INITIAL_MIN_BLUE(self) -> int: ...
# pylint: enable=invalid-name



class PersonProtocol(Protocol):
    """This is currently only for some of the elevator tests, expand it as needed"""
    
    @property
    def current_floor_num(self) -> int: ...
    
    @property
    def current_floor_float(self) -> float: ...

    @property
    def destination_floor_num(self) -> int: ...
    
    @property
    def current_block_float(self) -> float: ...
    
    @property
    def current_floor(self) -> Floor | None: ...
    
    
    @property
    def destination_block_num(self) -> float: ...
    
    @property
    def person_id(self) -> str: ...
    
    @property
    def state(self) -> PersonState: ...
    
    # Let's keep this read-only for now
    
    @property
    def direction(self) -> HorizontalDirection: ...
    
    @direction.setter
    def direction(self, value: HorizontalDirection) -> None: ...
    
    @property
    def max_velocity(self) -> float: ...
    
    @property
    def building(self) -> Building: ...
    
    @property
    def waiting_time(self) -> float: ...        

    def set_destination(self, dest_floor_num: int, dest_block_num: float) -> None: ...
    
    def find_nearest_elevator_bank(self) -> None | ElevatorBank: ...
    
    def board_elevator(self, elevator: Elevator) -> None: ...
    
    def disembark_elevator(self) -> None: ...
    
    def update(self, dt: float) -> None: ...
    
    def update_idle(self, dt: float) -> None: ...
    
    def update_walking(self, dt: float) -> None: ...
    
    def testing_set_dest_floor_num(self, dest_floor: int) -> None: ...
    

    @property
    def mad_fraction(self) -> float: ...
    
    @property
    def draw_color(self) -> tuple[int, int, int]: ...   
    
    # End PersonProtocol

    

class Person(PersonProtocol):
    """
    A person in the building who moves between floors and has needs.
    """
    NULL_PERSON_ID:Final[int] = 0
    _id_generator: IDGenerator = IDGenerator("person")

    def __init__(
        self,
        logger_provider: LoggerProvider,
        building: Building,
        initial_floor_number: int,
        initial_block_float: float,
        config: GameConfig,
    ) -> None:
        # Assign unique ID and increment counter
        self._person_id: str = Person._id_generator.get_next_id()
        
        self._logger: MyTowerLogger = logger_provider.get_logger("person")
        self._building: Building = building
        self._current_floor_float: float = float(initial_floor_number)
        self._current_block_float: float = initial_block_float
        self._dest_block_num: float = initial_block_float
        self._dest_floor_num: int = initial_floor_number
        self._state: PersonState = PersonState.IDLE
        self._direction: HorizontalDirection = HorizontalDirection.STATIONARY
        self._config: Final[GameConfig] = config
        self._cosmetics: Final[PersonCosmeticsProtocol] = config.person_cosmetics
        self._next_elevator_bank: ElevatorBank | None = None
        self._idle_timeout: float = 0
        self._current_elevator: Elevator | None = None
        self._waiting_time: float = 0  # How long have we been waiting for elevator (or something else, I suppose)
        
        if initial_floor_number < 0 or initial_floor_number > building.num_floors:
            raise ValueError(f"Initial floor {initial_floor_number} is out of bounds (0-{building.num_floors})")
        
        if initial_block_float < 0 or initial_block_float > building.floor_width:
            raise ValueError(f"Initial block {initial_block_float} is out of bounds (0-{building.floor_width})")

        self._current_floor: Floor | None = None
        self._assign_floor(initial_floor_number)

        # Appearance (for visualization)
        # Use cosmetics_config for initial color ranges
        self._original_red: Final[int] = random.randint(
            self._cosmetics.INITIAL_MIN_RED, self._cosmetics.INITIAL_MAX_RED
        )
        self._original_green: Final[int] = random.randint(
            self._cosmetics.INITIAL_MIN_GREEN, self._cosmetics.INITIAL_MAX_GREEN
        )
        self._original_blue: Final[int] = random.randint(
            self._cosmetics.INITIAL_MIN_BLUE, self._cosmetics.INITIAL_MAX_BLUE
        )
                
        self._red_range: int = abs(self._cosmetics.ANGRY_MAX_RED - self._original_red)
        self._green_range: int = abs(self._cosmetics.ANGRY_MIN_GREEN - self._original_green)
        self._blue_range: int = abs(self._cosmetics.ANGRY_MIN_BLUE - self._original_blue)
        

    @property
    @override
    def person_id(self) -> str:
        """Get the unique person ID"""
        return self._person_id
    
    @property
    @override
    def building(self) -> Building:
        return self._building

    @property
    @override
    def current_floor_num(self) -> int:
        return int(self._current_floor_float)
    
    @property
    @override
    def current_floor_float(self) -> float:
        return self._current_floor_float

    @property
    @override
    def destination_block_num(self) -> float:
        return self._dest_block_num

    @property
    @override
    def current_block_float(self) -> float:
        return self._current_block_float

    @property
    @override
    def current_floor(self) -> Floor | None:
        return self._current_floor
    

    @property
    @override
    def destination_floor_num(self) -> int:
        return self._dest_floor_num

    @property
    @override
    def state(self) -> PersonState:
        return self._state
    

    @property
    @override
    def direction(self) -> HorizontalDirection:
        return self._direction

    @direction.setter
    def direction(self, value: HorizontalDirection) -> None:
        self._direction = value

    @property
    @override
    def max_velocity(self) -> float:
        return self._config.person.MAX_SPEED
       
    @property
    @override
    def waiting_time(self) -> float:
        return self._waiting_time


    @override
    def set_destination(self, dest_floor_num: int, dest_block_num: float) -> None:
        # Check if destination values are out of bounds and raise warnings
        # TODO: This will need be revised if we ever have buildings with negative floor numbers
        if dest_floor_num < 0 or dest_floor_num > self.building.num_floors:
            raise ValueError(f"Destination floor {dest_floor_num} is out of bounds (0-{self.building.num_floors})")

        # TODO: We will need to revisit this when buildings don't start at block 0 (the far left edge of the screen)
        if dest_block_num < 0 or dest_block_num > self.building.floor_width:
            raise ValueError(f"Destination block {dest_block_num} is out of bounds (0-{self.building.floor_width})")

        dest_floor_num = min(dest_floor_num, self.building.num_floors)
        dest_floor_num = max(dest_floor_num, 0)
        self._dest_floor_num = dest_floor_num

        dest_block_num = min(dest_block_num, self.building.floor_width)
        dest_block_num = max(dest_block_num, 0)
        self._dest_block_num = dest_block_num


    @override
    def find_nearest_elevator_bank(self) -> None | ElevatorBank:
        elevator_list: List[ElevatorBank] = self.building.get_elevator_banks_on_floor(self.current_floor_num)
        closest_el: ElevatorBank | None = None
        closest_dist: float = float(self.building.floor_width + 5)

        for elevator in elevator_list:
            # TODO: Add logic to skip elevator banks that don't go to dest floor
            dist: float = abs(elevator.horizontal_block - self._current_block_float)
            if dist < closest_dist:
                closest_dist = dist
                closest_el = elevator

        return closest_el

    def _assign_floor(self, floor_num: int) -> None:
        self._current_floor = self.building.get_floor_by_number(floor_num)
        if not self._current_floor:
            raise RuntimeError(f"Cannot assign person to floor {floor_num} , the floor does not exist.")

        self._current_floor.add_person(self)


    def _clear_floor(self) -> None:
        if not self._current_floor:
            raise RuntimeError("Cannot clear floor: person is not currently on a floor.")

        self._current_floor.remove_person(self._person_id)
        self._current_floor = None

    @override
    def board_elevator(self, elevator: Elevator) -> None:
        self._current_elevator = elevator
        self._waiting_time = 0.0
        self._state = PersonState.IN_ELEVATOR
        
        try:
            self._clear_floor()
        except RuntimeError as e:
            raise RuntimeError(f"Person {self._person_id} is not on a floor but is trying to board an elevator.") from e

    @override
    def disembark_elevator(self) -> None:
        if self._current_elevator is None:
            raise RuntimeError("Cannot disembark elevator: no elevator is currently boarded.")

        if self.state != PersonState.IN_ELEVATOR:
            raise RuntimeError("Cannot disembark elevator: person must be in elevator state.")

        self._current_block_float = self._current_elevator.parent_elevator_bank.get_waiting_block()
        self._current_floor_float = float(self._current_elevator.current_floor_int)
        
        try:
            self._assign_floor(self._current_elevator.current_floor_int)
        except RuntimeError as e:
            raise RuntimeError(f"Cannot disembark elevator: floor {self._current_elevator.current_floor_int} does not exist.") from e

        self._waiting_time = 0.0
        self._current_elevator = None
        self._next_elevator_bank = None
        self._state = PersonState.IDLE


    @override
    def update(self, dt: float) -> None:
        """Update person's state and position"""
        match self.state:
            case PersonState.IDLE:
                self.update_idle(dt)

            case PersonState.WALKING:
                self.update_walking(dt)

            case PersonState.WAITING_FOR_ELEVATOR:
                # Later on, we can do the staggered line appearance here
                self._waiting_time += dt
                # Eventually, we can handle "Storming off to another elevator / stairs / managers office" here

            case PersonState.IN_ELEVATOR:
                if self._current_elevator:
                    self._waiting_time += dt
                    self._current_floor_float = self._current_elevator.fractional_floor
                    self._current_block_float = self._current_elevator.parent_elevator_bank.horizontal_block

            case _:
                # Handle unexpected states
                self._logger.warning(f"Unknown state: {self.state}")  # type: ignore[unreachable]
                raise ValueError(f"Unknown state: {self.state}")


    @override
    def update_idle(self, dt: float) -> None:
        self.direction = HorizontalDirection.STATIONARY

        self._idle_timeout = max(0, self._idle_timeout - dt)
        if self._idle_timeout > 0.0:
            return

        current_destination_block: float = float(self._dest_block_num)

        if self._dest_floor_num != self.current_floor_num:
            # Find the nearest elevator, go in that direction
            self._next_elevator_bank = self.find_nearest_elevator_bank()
            if self._next_elevator_bank:
                current_destination_block = float(self._next_elevator_bank.get_waiting_block())
                self._logger.trace(
                    f"IDLE Person: Destination fl. {self.destination_floor_num} != current fl. {self.current_floor_num} -> WALKING to Elevator block: {current_destination_block}"
                )
                self._state = PersonState.WALKING
            else:
                # There's no elevator on this floor, maybe one is coming soon...
                current_destination_block = self._current_block_float  # why move? There's nowhere to go
                self._logger.trace(
                    f"IDLE Person: Destination fl. {self.destination_floor_num} != current fl. {self.current_floor_num} -> IDLE b/c no Elevator on this floor"
                )
                self._state = PersonState.IDLE
                # Set a timer so that we don't run this constantly (like every 5 seconds)
                self._idle_timeout = self._config.person.IDLE_TIMEOUT

        if current_destination_block < self._current_block_float:
            # Already on the right floor (or walking to elevator?)
            self._logger.trace(
                f"IDLE Person: Destination is on this floor: {self.destination_floor_num}, WALKING LEFT to block: {current_destination_block}"
            )
            self._state = PersonState.WALKING
            self.direction = HorizontalDirection.LEFT

        elif current_destination_block > self._current_block_float:
            self._logger.trace(
                f"IDLE Person: Destination is on this floor: {self.destination_floor_num}, WALKING RIGHT to block: {current_destination_block}"
            )
            self._state = PersonState.WALKING
            self.direction = HorizontalDirection.RIGHT


    @override
    def update_walking(self, dt: float) -> None:
        done: bool = False

        # TODO: Probably need a next_block_this_floor or some such for all these walking directions
        waypoint_block: Final[float] = self._next_elevator_bank.get_waiting_block() if self._next_elevator_bank else self._dest_block_num        

        if waypoint_block < self._current_block_float:
            self.direction = HorizontalDirection.LEFT

        elif waypoint_block > self._current_block_float:
            self.direction = HorizontalDirection.RIGHT

        next_block: float = self._current_block_float + dt * self._config.person.MAX_SPEED * self.direction.value
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
                self._state = PersonState.WAITING_FOR_ELEVATOR
            else:
                self._state = PersonState.IDLE
            self._logger.debug(
                f"WALKING Person: Arrived at destination (fl {self.current_floor_num}, bk {waypoint_block}) -> {self.state}"
            )

        # TODO: Update these once we have building extents
        next_block = min(next_block, self.building.floor_width)
        next_block = max(next_block, 0)
        self._current_block_float = next_block

    # TESTING ONLY: Set the destination floor directly (for unit tests)
    @override
    def testing_set_dest_floor_num(self, dest_floor: int) -> None:
        if dest_floor < 0 or dest_floor > self.building.num_floors:
            self._logger.warning(f"[TEST] Destination floor {dest_floor} is out of bounds (0-{self.building.num_floors})")
            raise ValueError(f"[TEST] Destination floor {dest_floor} is out of bounds (0-{self.building.num_floors})")
        self._dest_floor_num = min(max(dest_floor, 0), self.building.num_floors)

    def testing_confirm_dest_block_is(self, block: float) -> bool:
        return self._dest_block_num == block

    def testing_set_next_elevator_bank(self, next_bank: ElevatorBank) -> None:
        self._next_elevator_bank = next_bank

    def testing_set_wait_time(self, time: float) -> None:
        self._waiting_time = time
        
    def testing_get_wait_time(self) -> float:
        return self._waiting_time
        
    def testing_set_current_elevator(self, elevator: Elevator) -> None:
        self._current_elevator = elevator

    def testing_get_current_elevator(self) -> Elevator | None:
        return self._current_elevator
    
    def testing_get_next_elevator_bank(self) -> ElevatorBank | None:
        return self._next_elevator_bank
    
    def testing_set_current_floor_float(self, cur_floor: float) -> None:
        self._current_floor_float = cur_floor
        
    def testing_get_current_floor_float(self) -> float:
        return self._current_floor_float

    def testing_set_current_block_float(self, cur_block: float) -> None:
        self._current_block_float = cur_block

    def testing_set_current_state(self, state: PersonState) -> None:
        self._state = state
        
    def testing_get_max_wait_time(self) -> float:
        return self._config.person.MAX_WAIT_TIME
    
    def testing_set_current_floor(self, floor: Floor) -> None:
        self._current_floor = floor


    @property
    @override
    def mad_fraction(self) -> float:
        return (self._waiting_time / self._config.person.MAX_WAIT_TIME) if self._config.person.MAX_WAIT_TIME > 0.0 else 0.0

    @property
    def draw_color_red(self) -> int:
        """As the person becomes more upset, they become more red"""
        color_red: int = self._original_red + int(self._red_range * self.mad_fraction)
        return max(0, min(254, color_red))


    @property
    def draw_color_green(self) -> int:
        """As the person becomes more upset, they become less green"""
        color_green: int = self._original_green - int(self._green_range * self.mad_fraction)
        return max(0, min(254, color_green))


    @property
    def draw_color_blue(self) -> int:
        """As the person becomes more upset, they become less blue"""
        color_blue: int = self._original_blue - int(self._blue_range * self.mad_fraction)
        return max(0, min(254, color_blue))


    @property
    @override
    def draw_color(self) -> tuple[int, int, int]:
        """Get the color for the person based on their current state"""
        return (
            self.draw_color_red,
            self.draw_color_green,
            self.draw_color_blue
        )