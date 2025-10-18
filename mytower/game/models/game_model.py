"""
Model layer: Pure business logic and data management
No pygame dependencies, no rendering logic
"""
from __future__ import annotations
from typing import Dict, Final, List, Optional

from pygame import Surface

from mytower.game.core.units import Blocks, Time
from mytower.game.entities.entities_protocol import (
    ElevatorProtocol,
    FloorProtocol,
    PersonProtocol,
    ElevatorBankProtocol
)

from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger
from mytower.game.models.model_snapshots import BuildingSnapshot, ElevatorBankSnapshot, ElevatorSnapshot, FloorSnapshot, PersonSnapshot
from mytower.game.models.snapshot_builders import build_elevator_bank_snapshot, build_elevator_snapshot, build_floor_snapshot, build_person_snapshot
from mytower.game.entities.person import Person
from mytower.game.core.types import FloorType
from mytower.game.entities.building import Building
from mytower.game.core.config import GameConfig
from mytower.game.core.constants import STARTING_MONEY, MIN_TIME_MULTIPLIER, MAX_TIME_MULTIPLIER
from mytower.game.entities.elevator_bank import ElevatorBank
from mytower.game.entities.elevator import Elevator

class GameModel:
    """
    Pure business logic layer - manages game state
    Provides clean interfaces for external consumption


    """
    def __init__(self, logger_provider: LoggerProvider) -> None:
        self._logger_provider: LoggerProvider = logger_provider
        self._logger: MyTowerLogger = logger_provider.get_logger('GameModel')
        
        # Use protocols for internal storage - allows for future flexibility
        self._people: Dict[str, PersonProtocol] = {}
        self._elevator_banks: Dict[str, ElevatorBankProtocol] = {}
        self._elevators: Dict[str, ElevatorProtocol] = {}
        self._floors: Dict[int, FloorProtocol] = {}
        
        self._building: Building = Building(logger_provider, width=20)
        self._config: GameConfig = GameConfig()

        self._money: int = STARTING_MONEY  # Starting money
        self._time: Time = Time(0.0)
        self._speed: float = self._config.initial_speed
        self._paused: bool = False
        

    
    @property
    def is_paused(self) -> bool:
        return self._paused
    
    @property
    def current_time(self) -> Time:
        return self._time

    @property
    def money(self) -> int:
        return self._money
    
    @property
    def speed(self) -> float:
        return self._speed

    def set_speed(self, value: float) -> None:
        if MIN_TIME_MULTIPLIER <= value <= MAX_TIME_MULTIPLIER:
            self._speed = value
        else:
            self._logger.warning(f"Attempted to set invalid speed: {value}")
    
    # Command Methods (for GraphQL mutations)
    def add_floor(self, floor_type: FloorType) -> int:
        """Add a new floor to the building"""
        try:
            # The floor may be a different height depending on type, we'll need to account for that in the building function
            new_floor_num: int = self._building.add_floor(floor_type)
            new_floor: FloorProtocol | None = self._building.get_floor_by_number(new_floor_num)
            
            if new_floor is None:
                raise RuntimeError(f"Failed to retrieve newly added floor {new_floor_num}")
            
            self._floors[new_floor_num] = new_floor
            return new_floor_num
        except Exception as e:
            self._logger.exception(f"Failed to add floor of type {floor_type}: {e}")
            raise RuntimeError(f"Failed to add floor of type {floor_type.name}: {str(e)}") from e



    def add_elevator_bank(self, h_cell: int, min_floor: int, max_floor: int) -> str:
        """Add a new elevator bank to the building"""
        try:
            elevator_bank = ElevatorBank(
                logger_provider=self._logger_provider,
                cosmetics_config=self._config.elevator_cosmetics,
                building=self._building,
                horizontal_position=h_cell,
                min_floor=min_floor,
                max_floor=max_floor
            )
            self._building.add_elevator_bank(elevator_bank)
            
            el_bank_id: Final[str] = elevator_bank.elevator_bank_id
            self._elevator_banks[el_bank_id] = elevator_bank  # Stored as protocol
            return el_bank_id

        except Exception as e:
            self._logger.exception(f"Failed to add elevator bank: {e}")
            raise RuntimeError(f"Failed to add elevator bank: {str(e)}") from e



    def add_elevator(self, el_bank_id: str) -> str:
        """Add a new elevator to the specified elevator bank"""
        try:
            el_bank: ElevatorBankProtocol | None = self._elevator_banks.get(el_bank_id)  # Protocol type
            if el_bank is None:
                raise ValueError(f"Elevator bank {el_bank_id} does not exist")

            # Concrete construction still happens here
            elevator = Elevator(
                logger_provider=self._logger_provider,
                elevator_bank=el_bank,
                min_floor=el_bank.min_floor,
                max_floor=el_bank.max_floor,
                config=self._config.elevator,
                cosmetics_config=self._config.elevator_cosmetics
            )
            el_bank.add_elevator(elevator)
            
            self._elevators[elevator.elevator_id] = elevator  # Stored as protocol
            return elevator.elevator_id

        except Exception as e:
            self._logger.exception(f"Failed to add elevator to bank {el_bank_id}: {e}")
            raise RuntimeError(f"Failed to add elevator to bank {el_bank_id}: {str(e)}") from e



    def add_person(self, floor: int, block: float, dest_floor: int, dest_block: float) -> str:
        """Add a new person to the building, returns person ID if successful"""
        try:
            # Concrete construction
            new_person: Final[Person] = Person(
                logger_provider=self._logger_provider,
                building=self._building,
                initial_floor_number=floor,
                initial_block_float=block,
                config=self._config
            )

            new_person.set_destination(dest_floor_num=dest_floor, dest_horiz_pos=Blocks(dest_block))

            self._people[new_person.person_id] = new_person  # Stored as protocol
            return new_person.person_id

        except Exception as e:
            self._logger.exception(f"Failed to add person: {e}")
            raise RuntimeError(f"Failed to add person at floor {floor}, block {block}: {str(e)}") from e



    # TODO: #17 The person will likely have dependencies such as being owned by a floor or elevator. We should make sure they are removed from it during this. Other remove methods will also have this issue.
    def remove_person(self, person_id: str) -> None:
        """Remove a person from the building"""
        try:
            self._people.pop(person_id, None)
            
        except Exception as e:
            self._logger.exception(f"Failed to remove person {person_id}: {e}")
            raise RuntimeError(f"Failed to remove person {person_id}: {str(e)}") from e

    def get_all_people(self) -> List[PersonSnapshot]:
        """Get all people in the building"""
        try:
            return [build_person_snapshot(person) for person in self._people.values()]
        except Exception as e:
            self._logger.exception(f"Failed to get all people: {e}")
            raise RuntimeError(f"Failed to get all people: {str(e)}") from e

    def get_all_elevators(self) -> List[ElevatorSnapshot]:
        """Get all elevators in the building"""
        try:
            return [build_elevator_snapshot(elevator) for elevator in self._elevators.values()]
        except Exception as e:
            self._logger.exception(f"Failed to get all elevators: {e}")
            raise RuntimeError(f"Failed to get all elevators: {str(e)}") from e

    def get_all_elevator_banks(self) -> List[ElevatorBankSnapshot]:
        """Get all elevator banks in the building"""
        try:
            return [build_elevator_bank_snapshot(bank) for bank in self._elevator_banks.values()]
        except Exception as e:
            self._logger.exception(f"Failed to get all elevator banks: {e}")
            raise RuntimeError(f"Failed to get all elevator banks: {str(e)}") from e

    def get_all_floors(self) -> List[FloorSnapshot]:
        """Get all floors in the building"""
        try:
            # Somewhere, we may need to build these in order so that the floor heights are accounted for correctly
            return [build_floor_snapshot(floor) for floor in self._floors.values()]
        except Exception as e:
            self._logger.exception(f"Failed to get all floors: {e}")
            raise RuntimeError(f"Failed to get all floors: {str(e)}") from e

    def set_game_speed(self, speed: float) -> bool:
        """Set game simulation speed"""
        try:
            if 0.0 <= speed <= 10.0:  # Reasonable bounds
                self._speed = speed
                return True

            self._logger.warning(f"Attempted to set invalid game speed: {speed}")
            return False
        except Exception as e:
            self._logger.exception(f"Failed to set game speed to {speed}: {e}")
            raise RuntimeError(f"Failed to set game speed to {speed}: {str(e)}") from e



    def set_pause_state(self, paused: bool) -> None:
        """Set game pause state"""
        try:
            self._paused = paused
            self._logger.info(f"Set pause state to {paused}")

        except Exception as e:
            self._logger.exception(f"Failed to set pause state to {paused}: {e}")
            raise RuntimeError(f"Failed to set pause state to {paused}: {str(e)}") from e



    def toggle_pause(self) -> bool:
        """Toggle game pause state, returns new state"""
        try:
            self.set_pause_state(not self._paused)
            return self._paused
        except Exception as e:
            self._logger.exception(f"Failed to toggle pause state: {e}")
            raise RuntimeError(f"Failed to toggle pause state: {str(e)}") from e


    # Simulation Methods
    def update(self, dt: Time) -> None:
        """Update game simulation"""
        try:
            if not self._paused:
                game_dt: Time = dt * self._speed
                self._time += game_dt

                # First, we do the elevators
                for elevator in self._elevators.values():
                    elevator.update(game_dt)

                # Next the elevator banks, they will further modify the elevators
                for bank in self._elevator_banks.values():
                    bank.update(game_dt)  
                    
                # Next, we update the people
                for person in self._people.values():
                    person.update(game_dt)  # Now properly typed as Time

                # Finally, we update the building
                self._building.update(game_dt)
                
        except Exception as e:
            self._logger.exception(f"Failed to update game simulation with dt={dt}: {e}")
            raise RuntimeError(f"Failed to update game simulation: {str(e)}") from e


    def get_building_snapshot(self) -> BuildingSnapshot:
        """Get complete building state as immutable snapshot"""
        try:
            # TODO: Implement snapshot creation from self._building
            return BuildingSnapshot(
                time=self._time,
                money=self._money,
                floors=self.get_all_floors(),
                elevators=self.get_all_elevators(),
                people=self.get_all_people(),
                elevator_banks=self.get_all_elevator_banks()
            )
        except Exception as e:
            self._logger.exception(f"Failed to get building snapshot: {e}")
            raise RuntimeError(f"Failed to get building snapshot: {str(e)}") from e

    def get_person_by_id(self, person_id: str) -> Optional[PersonSnapshot]:
        """Get specific person state by ID"""
        try:
            person: PersonProtocol | None = self._people.get(person_id)
            if person:
                return build_person_snapshot(person)
            
            return None
        
        except Exception as e:
            self._logger.exception(f"Failed to get person by id {person_id}: {e}")
            raise RuntimeError(f"Failed to get person by id {person_id}: {str(e)}") from e



    def get_elevator_by_id(self, elevator_id: str) -> Optional[ElevatorSnapshot]:
        """Get specific elevator state by ID"""
        try:
            elevators: Final[List[ElevatorProtocol]] = self._building.get_elevators()
            for elevator in elevators:
                if elevator.elevator_id == elevator_id:
                    return build_elevator_snapshot(elevator)
            return None
        except Exception as e:
            self._logger.exception(f"Failed to get elevator by id {elevator_id}: {e}")
            raise RuntimeError(f"Failed to get elevator by id {elevator_id}: {str(e)}") from e



    def get_floor_info(self, floor_number: int) -> Optional[FloorSnapshot]:
        """Get specific floor information"""
        try:
            floor: FloorProtocol | None = self._building.get_floor_by_number(floor_number)
            if floor:
                return build_floor_snapshot(floor)
            return None
        except Exception as e:
            self._logger.exception(f"Failed to get floor info for floor {floor_number}: {e}")
            raise RuntimeError(f"Failed to get floor info for floor {floor_number}: {str(e)}") from e

    def temp_draw_building(self, surface: Surface) -> None:
        """Draw the building on the given surface"""
        self._building.draw(surface)
