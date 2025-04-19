# game/building.py
from __future__ import annotations  # Defer type evaluation
from typing import Dict, List, TYPE_CHECKING
from game.constants import STARTING_MONEY
from game.person import Person
from game.floor import Floor
from game.types import FloorType
from pygame import Surface
from game.logger import get_logger

if TYPE_CHECKING:
    from game.elevator_bank import ElevatorBank

logger = get_logger("building")

class Building:
    """
    The main building class that contains all floors, elevators, and people.
    """
    def __init__(self, width: int = 20) -> None:
        self.__floor_width: int = width  # Width in grid cells
        self.__floors: Dict[int, Floor] = {}    # Dictionary with floor number as key
        self.__elevator_banks: List[ElevatorBank] = [] # List of elevator objects
        self.__people: List[Person] = []    # List of people in the building
        self.__time: float = 0.0       # Game time in minutes
        self.__money: int = STARTING_MONEY # Starting money
        
        # Add ground floor by default
        self.add_floor("LOBBY")
    
    @property
    def num_floors(self) -> int:
        """Return the number of floors in the building."""
        return len(self.__floors)
    
    @property
    def money(self) -> int:
        return self.__money
    
    @property
    def floor_width(self) -> int:
        return self.__floor_width
    
    def add_floor(self, floor_type: FloorType) -> Floor:
        """Add a new floor to the building"""    
        next_floor = self.num_floors + 1
        self.__floors[next_floor] = Floor(self, next_floor, floor_type)
        return self.__floors[next_floor]
    
    def add_elevator_bank(self, elevator_bank: ElevatorBank) -> None:
        """Add a new elevator to the building"""
        self.__elevator_banks.append(elevator_bank)
    
    def add_person(self, person: Person) -> None:
        self.__people.append(person)
    
    def get_elevator_banks_on_floor(self, floor_num: int) -> List[ElevatorBank]:
        """Returns a list of all elevators that are currently on the specified floor"""
        return [
            bank for bank in self.__elevator_banks
            if (
                hasattr(bank, 'min_floor') and
                hasattr(bank, 'max_floor') and
                (bank.min_floor <= floor_num <= bank.max_floor)
            )
        ]
        

    def update(self, dt: float) -> None:
        """Update the building simulation by dt time"""
        self.__time += dt
        
        for elevator in self.__elevator_banks:
            if hasattr(elevator, 'update'):
                elevator.update(dt)
                
        for person in self.__people:
            if hasattr(person, 'update'):
                person.update(dt)
        
    
    def draw(self, surface: Surface) -> None:
        """Draw the building on the given surface"""
        # Draw floors from bottom to top
        for floor_num in sorted(self.__floors.keys()):
            self.__floors[floor_num].draw(surface)
        
        for elevator in self.__elevator_banks:
            logger.debug("I want to draw an elevator bank")
            if hasattr(elevator, 'draw'):
                elevator.draw(surface)
        
        for person in self.__people:
            logger.debug("I want to draw a person")
            if hasattr(person, 'draw') and callable(person.draw):
                person.draw(surface)