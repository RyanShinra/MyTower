# game/building.py
from __future__ import annotations  # Defer type evaluation
from typing import Dict, List, TYPE_CHECKING
from game.constants import STARTING_MONEY
from game.person import Person
from game.floor import Floor
from game.types import FloorType
from pygame import Surface

if TYPE_CHECKING:
    from game.elevator import Elevator
class Building:
    """
    The main building class that contains all floors, elevators, and people.
    """
    def __init__(self, width: int = 20):
        self.width: int = width  # Width in grid cells
        self.floors: Dict[int, Floor] = {}    # Dictionary with floor number as key
        self.elevators: List[Elevator] = [] # List of elevator objects
        self.people: List[Person] = []    # List of people in the building
        self.time: float = 0       # Game time in minutes
        self.money: int = STARTING_MONEY # Starting money
        
        # Add ground floor by default
        self.add_floor("LOBBY")
    
    @property
    def num_floors(self) -> int:
        """Return the number of floors in the building."""
        return len(self.floors)
    
    def add_floor(self, floor_type: FloorType) -> Floor:
        """Add a new floor to the building"""    
        next_floor = self.num_floors + 1
        self.floors[next_floor] = Floor(self, next_floor, floor_type)
        return self.floors[next_floor]
    
    def add_elevator(self, elevator: Elevator):
        """Add a new elevator to the building"""
        self.elevators.append(elevator)
    
    def add_person(self, person: Person) -> None:
        self.people.append(person)
    

    def update(self, dt: float):
        """Update the building simulation by dt time"""
        for elevator in self.elevators:
            if hasattr(elevator, 'update'):
                elevator.update(dt)
        
    
    def draw(self, surface: Surface):
        """Draw the building on the given surface"""
        # Draw floors from bottom to top
        for floor_num in sorted(self.floors.keys()):
            self.floors[floor_num].draw(surface)
        
        for elevator in self.elevators:
            if hasattr(elevator, 'draw'):
                elevator.draw(surface)
        
        for person in self.people:
            if hasattr(person, 'draw') and callable(person.draw):
                person.draw(surface)