# demo_builder.py
# Creates a demo instance of the game

from typing import Final

from mytower.game.controllers.controller_commands import (
    AddElevatorBankCommand, AddElevatorCommand, AddFloorCommand,
    AddPersonCommand, CommandResult)
from mytower.game.controllers.game_controller import GameController
from mytower.game.entities.floor import FloorType
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger


def build_model_building(controller: GameController, logger_provider: LoggerProvider) -> None:
    """Build a demo instance of the game building."""

    demo_logger: Final[MyTowerLogger] = logger_provider.get_logger("DemoBuilder")

    def add_floor(floor_type: FloorType) -> int:
        result: Final[CommandResult[int]] = controller.execute_command(AddFloorCommand(floor_type=floor_type))
        if result.success and result.data is not None:
            return result.data  # Return the new floor number
        else:
            demo_logger.error(f"Failed to add floor: {result.error}")
            return -1

    def add_elevator_bank(h_cell: int, min_floor: int, max_floor: int) -> str:
        result: Final[CommandResult[str]] = controller.execute_command(
            AddElevatorBankCommand(h_cell=h_cell, min_floor=min_floor, max_floor=max_floor)
        )
        if result.success and result.data is not None:
            return result.data  # Return the new elevator bank ID
        else:
            demo_logger.error(f"Failed to add elevator bank: {result.error}")
            return ""

    def add_elevator(elevator_bank_id: str) -> str:
        result: Final[CommandResult[str]] = controller.execute_command(
            AddElevatorCommand(elevator_bank_id=elevator_bank_id)
        )
        if result.success and result.data is not None:
            return result.data  # Return the new elevator ID
        else:
            demo_logger.error(f"Failed to add elevator: {result.error}")
            return ""

    def add_person(current_floor_num: int, current_block_float: float, dest_floor_num: int, dest_block_num: float) -> str:
        result: Final[CommandResult[str]] = controller.execute_command(
            AddPersonCommand(
                floor=current_floor_num,
                block=current_block_float,
                dest_floor=dest_floor_num,
                dest_block=dest_block_num
            )
        )
        if result.success and result.data is not None:
            return result.data
        else:
            demo_logger.error(f"Failed to add person: {result.error}")
            return ""

    # Initialize with some basic floors and an elevator
    add_floor(FloorType.LOBBY)
    add_floor(FloorType.RETAIL)
    add_floor(FloorType.RETAIL)
    add_floor(FloorType.RETAIL)
    add_floor(FloorType.RESTAURANT)
    add_floor(FloorType.RESTAURANT)
    add_floor(FloorType.OFFICE)
    add_floor(FloorType.OFFICE)
    add_floor(FloorType.OFFICE)
    add_floor(FloorType.OFFICE)
    add_floor(FloorType.HOTEL)
    add_floor(FloorType.HOTEL)
    add_floor(FloorType.HOTEL)
    add_floor(FloorType.HOTEL)
    add_floor(FloorType.APARTMENT)
    add_floor(FloorType.APARTMENT)
    add_floor(FloorType.APARTMENT)
    top_floor: int = add_floor(FloorType.APARTMENT)

    elevator_bank_id: str = add_elevator_bank(h_cell=14, min_floor=1, max_floor=top_floor)
    add_elevator(elevator_bank_id)

    add_person(current_floor_num=1, current_block_float=1.0, dest_floor_num=12, dest_block_num=7.0)
    add_person(current_floor_num=1, current_block_float=3.0, dest_floor_num=3, dest_block_num=7.0)
    add_person(current_floor_num=1, current_block_float=6.0, dest_floor_num=7, dest_block_num=7.0)
    add_person(current_floor_num=12, current_block_float=1.0, dest_floor_num=1, dest_block_num=1.0)

    demo_logger.info("Demo building complete.")
