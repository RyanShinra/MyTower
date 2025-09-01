# game/game_state.py
import pygame
from pygame import Surface

from mytower.game.building import Building
from mytower.game.config import GameConfig
from mytower.game.elevator import Elevator
from mytower.game.elevator_bank import ElevatorBank
from mytower.game.floor import FloorType
from mytower.game.logger import LoggerProvider, MyTowerLogger
from mytower.game.person import Person


class GameState:
    """
    Manages the overall game state including the building, UI, and game controls.
    """

    def __init__(self, logger_provider: LoggerProvider, screen_width: int, screen_height: int) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("GameState")

        self._screen_width: int = screen_width
        self._screen_height: int = screen_height
        self._building = Building(logger_provider, width=20)

        self._config = GameConfig()

        # Initialize with some basic floors and an elevator
        self._building.add_floor(FloorType.RETAIL)
        self._building.add_floor(FloorType.RETAIL)
        self._building.add_floor(FloorType.RETAIL)
        self._building.add_floor(FloorType.RESTAURANT)
        self._building.add_floor(FloorType.RESTAURANT)
        self._building.add_floor(FloorType.OFFICE)
        self._building.add_floor(FloorType.OFFICE)
        self._building.add_floor(FloorType.OFFICE)
        self._building.add_floor(FloorType.OFFICE)
        self._building.add_floor(FloorType.HOTEL)
        self._building.add_floor(FloorType.HOTEL)
        self._building.add_floor(FloorType.HOTEL)
        self._building.add_floor(FloorType.HOTEL)
        self._building.add_floor(FloorType.APARTMENT)
        self._building.add_floor(FloorType.APARTMENT)
        self._building.add_floor(FloorType.APARTMENT)
        self._building.add_floor(FloorType.APARTMENT)

        # Add one elevator

        self._test_elevator_bank = ElevatorBank(
            logger_provider,
            self._building,
            h_cell=14,
            min_floor=1,
            max_floor=self._building.num_floors,
            cosmetics_config=self._config.elevator_cosmetics,
        )

        self._test_elevator = Elevator(
            logger_provider,
            self._test_elevator_bank,
            h_cell=14,
            min_floor=1,
            max_floor=self._building.num_floors,
            config=self._config.elevator,
            cosmetics_config=self._config.elevator_cosmetics,
        )

        self._test_elevator_bank.add_elevator(self._test_elevator)
        self._building.add_elevator_bank(self._test_elevator_bank)

        # Add a sample person
        self._test_person = Person(
            logger_provider, building=self._building, current_floor_num=1, current_block_float=1, config=self._config
        )  # Pass the whole GameConfig object
        self._test_person.set_destination(dest_floor_num=9, dest_block_num=7)
        
        self._test_person2 = Person(
            logger_provider, building=self._building, current_floor_num=1, current_block_float=3, config=self._config
        )  # Pass the whole GameConfig object
        self._test_person2.set_destination(dest_floor_num=3, dest_block_num=7)
        
        self._test_person3 = Person(
            logger_provider, building=self._building, current_floor_num=1, current_block_float=6, config=self._config
        )  # Pass the whole GameConfig object
        self._test_person3.set_destination(dest_floor_num=7, dest_block_num=7)
        
        self._test_person4 = Person(
            logger_provider, building=self._building, current_floor_num=12, current_block_float=1, config=self._config
        )  # Pass the whole GameConfig object
        self._test_person4.set_destination(dest_floor_num=1, dest_block_num=1)
        
        self._building.add_person(self._test_person)
        self._building.add_person(self._test_person2)
        self._building.add_person(self._test_person3)
        self._building.add_person(self._test_person4)

        # Game time tracking
        self._time: float = 0.0  # Game time in seconds
        self._speed: float = 1.0  # Game speed multiplier

        # UI state
        self._paused = False

    @property
    def building(self) -> Building:
        return self._building

    @property
    def screen_width(self) -> int:
        return self._screen_width

    @property
    def screen_height(self) -> int:
        return self._screen_height

    @property
    def time(self) -> float:
        return self._time

    @property
    def speed(self) -> float:
        return self._speed

    def set_speed(self, value: float) -> None:
        self._speed = value

    @property
    def paused(self) -> bool:
        return self._paused

    @paused.setter
    def paused(self, value: bool) -> None:
        self._paused = value

    def update(self, dt: float) -> None:
        """Update game state by time increment dt (in seconds)"""
        if not self._paused:
            # Scale dt by game speed
            game_dt: float = dt * self._speed
            self._time += game_dt

            # Update building and all its components
            self._building.update(game_dt)

    def draw(self, surface: Surface) -> None:
        """Draw the entire game state"""
        # Draw building
        # self._logger.debug("I want to draw a building")
        self._building.draw(surface)

        # Draw UI elements
        self._draw_ui(surface)

    def _draw_ui(self, surface: Surface) -> None:
        """Draw UI elements like time, money, etc."""
        # Draw time
        font = pygame.font.SysFont(None, 24)

        # Convert time to hours:minutes
        hours = int(self._time // 3600) % 24
        minutes = int(self._time // 60) % 60
        seconds = int(self._time) % 60
        time_str = f"Time: {hours:02d}:{minutes:02d}:{seconds:02d}"

        text = font.render(time_str, True, (0, 0, 0))
        surface.blit(text, (10, 10))

        # Draw money
        money_str = f"Money: ${self._building.money:,}"
        text = font.render(money_str, True, (0, 0, 0))
        surface.blit(text, (10, 40))
