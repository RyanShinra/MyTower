# game/building.py
from game.constants import STARTING_MONEY
class Building:
    """
    The main building class that contains all floors, elevators, and people.
    """
    def __init__(self, width=20):
        self.width = width  # Width in grid cells
        self.floors = {}    # Dictionary with floor number as key
        self.elevators = [] # List of elevator objects
        self.people = []    # List of people in the building
        self.time = 0       # Game time in minutes
        self.money = STARTING_MONEY # Starting money
        
        # Add ground floor by default
        self.add_floor(0, "LOBBY")
    
    def add_floor(self, floor_num, floor_type):
        """Add a new floor to the building"""
        from game.floor import Floor
        
        if floor_num in self.floors:
            raise ValueError(f"Floor {floor_num} already exists")
        
        self.floors[floor_num] = Floor(self, floor_num, floor_type)
        return self.floors[floor_num]
    
    def add_elevator(self, elevator):
        """Add a new elevator to the building"""
        self.elevators.append(elevator)
    
    def update(self, dt):
        """Update the building simulation by dt time"""
        pass  # To be implemented
    
    def draw(self, surface):
        """Draw the building on the given surface"""
        # Draw floors from bottom to top
        for floor_num in sorted(self.floors.keys()):
            self.floors[floor_num].draw(surface)
        
        # Draw elevators
        for elevator in self.elevators:
            elevator.draw(surface)
        
        # Draw people
        for person in self.people:
            if hasattr(person, 'draw'):
                person.draw(surface)