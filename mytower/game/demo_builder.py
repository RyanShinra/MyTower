# demo_builder.py
# Creates a demo instance of the game

from mytower.game.building import Building
from mytower.game.config import GameConfig
from mytower.game.elevator import Elevator
from mytower.game.elevator_bank import ElevatorBank
from mytower.game.floor import FloorType
from mytower.game.logger import LoggerProvider
from mytower.game.person import Person


def build_model_building(logger_provider: LoggerProvider) -> Building:
    """Build a demo instance of the game building."""

    building = Building(logger_provider, width=20)
    config = GameConfig()
    
    # Initialize with some basic floors and an elevator
    building.add_floor(FloorType.RETAIL)
    building.add_floor(FloorType.RETAIL)
    building.add_floor(FloorType.RETAIL)
    building.add_floor(FloorType.RESTAURANT)
    building.add_floor(FloorType.RESTAURANT)
    building.add_floor(FloorType.OFFICE)
    building.add_floor(FloorType.OFFICE)
    building.add_floor(FloorType.OFFICE)
    building.add_floor(FloorType.OFFICE)
    building.add_floor(FloorType.HOTEL)
    building.add_floor(FloorType.HOTEL)
    building.add_floor(FloorType.HOTEL)
    building.add_floor(FloorType.HOTEL)
    building.add_floor(FloorType.APARTMENT)
    building.add_floor(FloorType.APARTMENT)
    building.add_floor(FloorType.APARTMENT)
    building.add_floor(FloorType.APARTMENT)
    
    # Add one elevator

    test_elevator_bank = ElevatorBank(
        logger_provider,
        building,
        h_cell=14,
        min_floor=1,
        max_floor=building.num_floors,
        cosmetics_config=config.elevator_cosmetics,
    )

    test_elevator = Elevator(
        logger_provider,
        test_elevator_bank,
        h_cell=14,
        min_floor=1,
        max_floor=building.num_floors,
        config=config.elevator,
        cosmetics_config=config.elevator_cosmetics,
    )


    test_elevator_bank.add_elevator(test_elevator)
    building.add_elevator_bank(test_elevator_bank)

    # Add a sample person
    test_person = Person(
        logger_provider, building=building, current_floor_num=1, current_block_float=1, config=config
    )  # Pass the whole GameConfig object
    test_person.set_destination(dest_floor_num=9, dest_block_num=7)
    
    test_person2 = Person(
        logger_provider, building=building, current_floor_num=1, current_block_float=3, config=config
    )  # Pass the whole GameConfig object
    test_person2.set_destination(dest_floor_num=3, dest_block_num=7)
    
    test_person3 = Person(
        logger_provider, building=building, current_floor_num=1, current_block_float=6, config=config
    )  # Pass the whole GameConfig object
    test_person3.set_destination(dest_floor_num=7, dest_block_num=7)
    
    test_person4 = Person(
        logger_provider, building=building, current_floor_num=12, current_block_float=1, config=config
    )  # Pass the whole GameConfig object
    test_person4.set_destination(dest_floor_num=1, dest_block_num=1)
    
    building.add_person(test_person)
    building.add_person(test_person2)
    building.add_person(test_person3)
    building.add_person(test_person4)
    
    return building