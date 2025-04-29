# game/game_state.py
import pygame
from pygame import Surface
from game.building import Building
from game.elevator import Elevator
from game.constants import ELEVATOR_DEFAULT_CAPACITY, ELEVATOR_MAX_SPEED, PERSON_MAX_SPEED
from game.person import Person
from game.elevator_bank import ElevatorBank
from game.logger import get_logger

logger = get_logger("game_state")

class GameState:
    """
    Manages the overall game state including the building, UI, and game controls.
    """
    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.building = Building(width=20)

        # Initialize with some basic floors and an elevator
        self.building.add_floor("RETAIL")
        self.building.add_floor("RETAIL")
        self.building.add_floor("RETAIL")
        self.building.add_floor("RESTAURANT")
        self.building.add_floor("RESTAURANT")
        self.building.add_floor("OFFICE")
        self.building.add_floor("OFFICE")
        self.building.add_floor("OFFICE")
        self.building.add_floor("OFFICE")
        self.building.add_floor("OFFICE")
        self.building.add_floor("HOTEL")
        self.building.add_floor("HOTEL")
        self.building.add_floor("HOTEL")
        self.building.add_floor("HOTEL")
        self.building.add_floor("APARTMENT")
        self.building.add_floor("APARTMENT")
        self.building.add_floor("APARTMENT")
        self.building.add_floor("APARTMENT")

        # Add one elevator
        
        self.test_elevator_bank = ElevatorBank(
            self.building, h_cell=14, min_floor=1,
            max_floor=self.building.num_floors
        )
        
        self.test_elevator = Elevator(
            self.test_elevator_bank, h_cell=14, min_floor=1,
            max_floor=self.building.num_floors, max_velocity=ELEVATOR_MAX_SPEED,
            max_capacity=ELEVATOR_DEFAULT_CAPACITY
        )
        
        self.test_elevator_bank.add_elevator(self.test_elevator)
        self.building.add_elevator_bank(self.test_elevator_bank)

        # Add a sample person
        self.test_person = Person(building = self.building, current_floor = 1, current_block = 1, max_velocity=PERSON_MAX_SPEED)
        self.test_person.set_destination(dest_floor = 9, dest_block = 7)
        self.test_person2 = Person(building = self.building, current_floor = 1, current_block = 3, max_velocity=PERSON_MAX_SPEED)
        self.test_person2.set_destination(dest_floor = 3, dest_block = 7)
        self.test_person3 = Person(building = self.building, current_floor = 1, current_block = 6, max_velocity=PERSON_MAX_SPEED)
        self.test_person3.set_destination(dest_floor = 7, dest_block = 7)
        self.test_person4 = Person(building = self.building, current_floor = 12, current_block = 1, max_velocity=PERSON_MAX_SPEED)
        self.test_person4.set_destination(dest_floor = 1, dest_block = 1)
        self.building.add_person(self.test_person)
        self.building.add_person(self.test_person2)
        self.building.add_person(self.test_person3)
        self.building.add_person(self.test_person4)

        # Game time tracking
        self.time: float = 0.0  # Game time in seconds
        self.speed: float = 1.0  # Game speed multiplier

        # UI state
        self.paused = False

    def update(self, dt: float) -> None:
        """Update game state by time increment dt (in seconds)"""
        if not self.paused:
            # Scale dt by game speed
            game_dt = dt * self.speed
            self.time += game_dt

            # Update building and all its components
            self.building.update(game_dt)

    def draw(self, surface: Surface) -> None:
        """Draw the entire game state"""
        # Draw building
        # logger.debug("I want to draw a building")
        self.building.draw(surface)

        # Draw UI elements
        self._draw_ui(surface)

    def _draw_ui(self, surface: Surface) -> None:
        """Draw UI elements like time, money, etc."""
        # Draw time
        font = pygame.font.SysFont(None, 24)

        # Convert time to hours:minutes
        hours = int(self.time // 3600) % 24
        minutes = int(self.time // 60) % 60
        seconds = int(self.time) % 60
        time_str = f"Time: {hours:02d}:{minutes:02d}:{seconds:02d}"

        text = font.render(time_str, True, (0, 0, 0))
        surface.blit(text, (10, 10))

        # Draw money
        money_str = f"Money: ${self.building.money:,}"
        text = font.render(money_str, True, (0, 0, 0))
        surface.blit(text, (10, 40))
