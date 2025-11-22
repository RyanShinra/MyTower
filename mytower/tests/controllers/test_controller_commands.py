# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

from typing import Any, Final
from unittest.mock import MagicMock

from mytower.game.controllers.controller_commands import (
    AddElevatorBankCommand,
    AddElevatorCommand,
    AddFloorCommand,
    AddPersonCommand,
    AdjustSpeedCommand,
    CommandResult,
    TogglePauseCommand,
)
from mytower.game.core.constants import MAX_TIME_MULTIPLIER, MIN_TIME_MULTIPLIER
from mytower.game.core.types import FloorType
from mytower.game.core.units import Blocks
from mytower.game.models.game_model import GameModel


class TestCommandResult:
    """Test CommandResult dataclass"""

    def test_success_result_creation(self) -> None:
        """Test creating successful command result"""
        result: Final[CommandResult[str]] = CommandResult(success=True, data="test_data")

        assert result.success is True
        assert result.data == "test_data"
        assert result.error is None

    def test_failure_result_creation(self) -> None:
        """Test creating failed command result"""
        result: Final[CommandResult[Any]] = CommandResult(success=False, error="test error")

        assert result.success is False
        assert result.data is None
        assert result.error == "test error"

    def test_result_with_all_fields(self) -> None:
        """Test creating result with all fields"""
        result: Final[CommandResult[str]] = CommandResult(success=False, data="partial_data", error="validation failed")

        assert result.success is False
        assert result.data == "partial_data"
        assert result.error == "validation failed"


class TestAddFloorCommand:
    """Test AddFloorCommand functionality"""

    def test_command_creation(self) -> None:
        """Test creating AddFloorCommand"""
        command: Final[AddFloorCommand] = AddFloorCommand(floor_type=FloorType.OFFICE)

        assert command.floor_type == FloorType.OFFICE

    def test_get_description(self) -> None:
        """Test command description generation"""
        command: Final[AddFloorCommand] = AddFloorCommand(floor_type=FloorType.LOBBY)

        description: Final[str] = command.get_description()
        assert "Add a floor of type" in description
        assert "LOBBY" in description


    def test_execute_success(self) -> None:
        """Test successful floor addition"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        mock_model.add_floor.return_value = 5

        command: Final[AddFloorCommand] = AddFloorCommand(floor_type=FloorType.RESTAURANT)
        result: Final[CommandResult[int]] = command.execute(mock_model)

        assert result.success is True
        assert result.data == 5
        assert result.error is None
        mock_model.add_floor.assert_called_once_with(FloorType.RESTAURANT)


    def test_execute_different_floor_types(self) -> None:
        """Test adding different floor types"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        mock_model.add_floor.return_value = 1

        floor_types: Final[list[FloorType]] = [
            FloorType.LOBBY,
            FloorType.OFFICE,
            FloorType.APARTMENT,
            FloorType.HOTEL,
            FloorType.RESTAURANT,
            FloorType.RETAIL,
        ]

        for floor_type in floor_types:
            command: AddFloorCommand = AddFloorCommand(floor_type=floor_type)
            result: CommandResult[int] = command.execute(mock_model)

            assert result.success is True
            assert result.data == 1


class TestAddPersonCommand:
    """Test AddPersonCommand functionality"""


    def test_command_creation(self) -> None:
        """Test creating AddPersonCommand"""
        command: Final[AddPersonCommand] = AddPersonCommand(
            init_floor=1, init_horiz_position=Blocks(2.5), dest_floor=3, dest_horiz_position=Blocks(4.0)
        )

        assert command.init_floor == 1
        assert command.init_horiz_position == Blocks(2.5)
        assert command.dest_floor == 3
        assert command.dest_horiz_position == Blocks(4.0)

    def test_get_description(self) -> None:
        """Test command description generation"""
        command: Final[AddPersonCommand] = AddPersonCommand(
            init_floor=1, init_horiz_position=Blocks(2.5), dest_floor=3, dest_horiz_position=Blocks(4.0)
        )

        description: Final[str] = command.get_description()
        assert "Add person at floor 1.0, horiz_position 2.50" in description
        assert "destination floor 3.0, horiz_position 4.00" in description


    def test_execute_success(self) -> None:
        """Test successful person addition"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        mock_model.add_person.return_value = "person_123"

        command: Final[AddPersonCommand] = AddPersonCommand(
            init_floor=2, init_horiz_position=Blocks(1.0), dest_floor=5, dest_horiz_position=Blocks(3.0)
        )
        result: Final[CommandResult[str]] = command.execute(mock_model)

        assert result.success is True
        assert result.data == "person_123"
        assert result.error is None
        mock_model.add_person.assert_called_once_with(
            init_floor=2, init_horiz_position=Blocks(1.0), dest_floor=5, dest_horiz_position=Blocks(3.0)
        )


    def test_execute_same_source_and_destination_fails(self) -> None:
        """Test that same source and destination causes failure"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)

        command: Final[AddPersonCommand] = AddPersonCommand(
            init_floor=2, init_horiz_position=Blocks(1.0), dest_floor=2, dest_horiz_position=Blocks(1.0)
        )
        result: Final[CommandResult[str]] = command.execute(mock_model)

        assert result.success is False
        assert result.error is not None
        assert "Source and destination cannot be the same" in result.error
        mock_model.add_person.assert_not_called()


    def test_execute_invalid_floor_validation(self) -> None:
        """Test floor validation"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)

        # Invalid source floor
        command: Final[AddPersonCommand] = AddPersonCommand(
            init_floor=0, init_horiz_position=Blocks(1.0), dest_floor=2, dest_horiz_position=Blocks(2.0)
        )
        result: Final[CommandResult[str]] = command.execute(mock_model)
        assert result.success is False
        assert result.error is not None
        assert "Invalid source floor: 0" in result.error

        # Invalid destination floor
        command2: Final[AddPersonCommand] = AddPersonCommand(
            init_floor=1, init_horiz_position=Blocks(1.0), dest_floor=-1, dest_horiz_position=Blocks(2.0)
        )
        result2: Final[CommandResult[str]] = command2.execute(mock_model)
        assert result2.success is False
        assert result2.error is not None
        assert "Invalid destination floor: -1" in result2.error


    def test_execute_invalid_block_validation(self) -> None:
        """Test horiz_position validation"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)

        # Invalid source horiz_position
        command: Final[AddPersonCommand] = AddPersonCommand(
            init_floor=1, init_horiz_position=Blocks(-1.0), dest_floor=2, dest_horiz_position=Blocks(2.0)
        )
        result: Final[CommandResult[str]] = command.execute(mock_model)
        assert result.success is False
        assert result.error is not None
        assert "Invalid source horiz_position: -1.0" in result.error

        # Invalid destination horiz_position
        command2: Final[AddPersonCommand] = AddPersonCommand(
            init_floor=1, init_horiz_position=Blocks(1.0), dest_floor=2, dest_horiz_position=Blocks(-2.0)
        )
        result2: Final[CommandResult[str]] = command2.execute(mock_model)
        assert result2.success is False
        assert result2.error is not None
        assert "Invalid destination horiz_position: -2" in result2.error


class TestAddElevatorBankCommand:
    """Test AddElevatorBankCommand functionality"""

    def test_command_creation(self) -> None:
        """Test creating AddElevatorBankCommand"""
        command: Final[AddElevatorBankCommand] = AddElevatorBankCommand(
            horiz_position=Blocks(5), min_floor=1, max_floor=10
        )

        assert command.horiz_position == Blocks(5)
        assert command.min_floor == 1
        assert command.max_floor == 10

    def test_get_description(self) -> None:
        """Test command description generation"""
        command: Final[AddElevatorBankCommand] = AddElevatorBankCommand(
            horiz_position=Blocks(3), min_floor=2, max_floor=8
        )

        description: Final[str] = command.get_description()
        assert "Add elevator bank at horizontal position 3.0" in description
        assert "from floor 2.0 to 8.0" in description


    def test_execute_success(self) -> None:
        """Test successful elevator bank addition"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        mock_model.add_elevator_bank.return_value = "bank_456"

        command: Final[AddElevatorBankCommand] = AddElevatorBankCommand(
            horiz_position=Blocks(2), min_floor=1, max_floor=5
        )
        result: Final[CommandResult[str]] = command.execute(mock_model)

        assert result.success is True
        assert result.data == "bank_456"
        assert result.error is None
        mock_model.add_elevator_bank.assert_called_once_with(
            horiz_position=Blocks(2), min_floor=1, max_floor=5
        )


    def test_execute_invalid_h_cell_fails(self) -> None:
        """Test that invalid horizontal position causes failure"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)

        command: Final[AddElevatorBankCommand] = AddElevatorBankCommand(
            horiz_position=Blocks(-1), min_floor=1, max_floor=5
        )
        result: Final[CommandResult[str]] = command.execute(mock_model)

        assert result.success is False
        assert result.error is not None
        assert "Invalid horizontal position: -1" in result.error
        mock_model.add_elevator_bank.assert_not_called()


    def test_execute_invalid_min_floor_fails(self) -> None:
        """Test that invalid min floor causes failure"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)

        command: Final[AddElevatorBankCommand] = AddElevatorBankCommand(
            horiz_position=Blocks(1), min_floor=0, max_floor=5
        )
        result: Final[CommandResult[str]] = command.execute(mock_model)

        assert result.success is False
        assert result.error is not None
        assert "Invalid min floor: 0" in result.error
        mock_model.add_elevator_bank.assert_not_called()


    def test_execute_max_floor_less_than_min_fails(self) -> None:
        """Test that max floor less than min floor causes failure"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)

        command: Final[AddElevatorBankCommand] = AddElevatorBankCommand(
            horiz_position=Blocks(1), min_floor=5, max_floor=3
        )
        result: Final[CommandResult[str]] = command.execute(mock_model)

        assert result.success is False
        assert result.error is not None
        assert "max_floor must be >= min_floor: 3.0 < 5.0" in result.error
        mock_model.add_elevator_bank.assert_not_called()


class TestAddElevatorCommand:
    """Test AddElevatorCommand functionality"""

    def test_command_creation(self) -> None:
        """Test creating AddElevatorCommand"""
        command: Final[AddElevatorCommand] = AddElevatorCommand(elevator_bank_id="bank_123")

        assert command.elevator_bank_id == "bank_123"

    def test_get_description(self) -> None:
        """Test command description generation"""
        command: Final[AddElevatorCommand] = AddElevatorCommand(elevator_bank_id="test_bank")

        description: Final[str] = command.get_description()
        assert "Add elevator to bank test_bank" in description


    def test_execute_success(self) -> None:
        """Test successful elevator addition"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        mock_model.add_elevator.return_value = "elevator_789"

        command: Final[AddElevatorCommand] = AddElevatorCommand(elevator_bank_id="bank_456")
        result: Final[CommandResult[str]] = command.execute(mock_model)

        assert result.success is True
        assert result.data == "elevator_789"
        assert result.error is None
        mock_model.add_elevator.assert_called_once_with("bank_456")


    def test_execute_strips_whitespace(self) -> None:
        """Test that whitespace is stripped from bank ID"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        mock_model.add_elevator.return_value = "elevator_789"

        command: Final[AddElevatorCommand] = AddElevatorCommand(elevator_bank_id="  bank_456  ")
        result: Final[CommandResult[str]] = command.execute(mock_model)

        assert result.success is True
        mock_model.add_elevator.assert_called_once_with("bank_456")


    def test_execute_empty_bank_id_fails(self) -> None:
        """Test that empty bank ID causes failure"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)

        command: Final[AddElevatorCommand] = AddElevatorCommand(elevator_bank_id="")
        result: Final[CommandResult[str]] = command.execute(mock_model)

        assert result.success is False
        assert result.error is not None
        assert "elevator_bank_id cannot be empty" in result.error
        mock_model.add_elevator.assert_not_called()


    def test_execute_whitespace_only_bank_id_fails(self) -> None:
        """Test that whitespace-only bank ID causes failure"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)

        command: Final[AddElevatorCommand] = AddElevatorCommand(elevator_bank_id="   ")
        result: Final[CommandResult[str]] = command.execute(mock_model)

        assert result.success is False
        assert result.error is not None
        assert "elevator_bank_id cannot be empty" in result.error
        mock_model.add_elevator.assert_not_called()


    def test_execute_too_long_bank_id_fails(self) -> None:
        """Test that overly long bank ID causes failure"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)

        # Create a string longer than 64 characters
        long_id: Final[str] = "a" * 65
        command: Final[AddElevatorCommand] = AddElevatorCommand(elevator_bank_id=long_id)
        result: Final[CommandResult[str]] = command.execute(mock_model)

        assert result.success is False
        assert result.error is not None
        assert "elevator_bank_id must be less than 64 characters" in result.error
        assert "got 65 characters" in result.error
        mock_model.add_elevator.assert_not_called()


class TestTogglePauseCommand:
    """Test TogglePauseCommand functionality"""

    def test_command_creation(self) -> None:
        """Test creating TogglePauseCommand"""
        command: Final[TogglePauseCommand] = TogglePauseCommand()
        assert command is not None

    def test_get_description(self) -> None:
        """Test command description generation"""
        command: Final[TogglePauseCommand] = TogglePauseCommand()
        description: Final[str] = command.get_description()
        assert "Toggle game pause state" in description

    def test_execute_pause_from_unpaused(self) -> None:
        """Test pausing the game when currently unpaused"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        mock_model.is_paused = False

        command: Final[TogglePauseCommand] = TogglePauseCommand()
        result: Final[CommandResult[bool]] = command.execute(mock_model)

        assert result.success is True
        assert result.data is True
        assert result.error is None
        mock_model.set_pause_state.assert_called_once_with(True)

    def test_execute_unpause_from_paused(self) -> None:
        """Test unpausing the game when currently paused"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        mock_model.is_paused = True

        command: Final[TogglePauseCommand] = TogglePauseCommand()
        result: Final[CommandResult[bool]] = command.execute(mock_model)

        assert result.success is True
        assert result.data is False
        assert result.error is None
        mock_model.set_pause_state.assert_called_once_with(False)

    def test_execute_multiple_toggles(self) -> None:
        """Test multiple consecutive toggles"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        command: Final[TogglePauseCommand] = TogglePauseCommand()

        # Start unpaused
        mock_model.is_paused = False
        result1: CommandResult[bool] = command.execute(mock_model)
        assert result1.success is True
        assert result1.data is True

        # Now paused
        mock_model.is_paused = True
        result2: CommandResult[bool] = command.execute(mock_model)
        assert result2.success is True
        assert result2.data is False


class TestAdjustSpeedCommand:
    """Test AdjustSpeedCommand functionality"""

    def test_command_creation(self) -> None:
        """Test creating AdjustSpeedCommand"""
        command: Final[AdjustSpeedCommand] = AdjustSpeedCommand(delta=0.5)
        assert command.delta == 0.5

    def test_get_description_positive_delta(self) -> None:
        """Test command description for positive delta"""
        command: Final[AdjustSpeedCommand] = AdjustSpeedCommand(delta=0.25)
        description: Final[str] = command.get_description()
        assert "Adjust game speed by +0.25" in description

    def test_get_description_negative_delta(self) -> None:
        """Test command description for negative delta"""
        command: Final[AdjustSpeedCommand] = AdjustSpeedCommand(delta=-0.5)
        description: Final[str] = command.get_description()
        assert "Adjust game speed by -0.50" in description

    def test_execute_success_increase_speed(self) -> None:
        """Test successfully increasing speed"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        mock_model.speed = 1.0

        command: Final[AdjustSpeedCommand] = AdjustSpeedCommand(delta=0.25)
        result: Final[CommandResult[float]] = command.execute(mock_model)

        assert result.success is True
        assert result.data == 1.25
        assert result.error is None
        mock_model.set_speed.assert_called_once_with(1.25)

    def test_execute_success_decrease_speed(self) -> None:
        """Test successfully decreasing speed"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        mock_model.speed = 1.0

        command: Final[AdjustSpeedCommand] = AdjustSpeedCommand(delta=-0.5)
        result: Final[CommandResult[float]] = command.execute(mock_model)

        assert result.success is True
        assert result.data == 0.5
        assert result.error is None
        mock_model.set_speed.assert_called_once_with(0.5)

    def test_execute_at_minimum_boundary(self) -> None:
        """Test adjusting speed exactly at minimum boundary"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        mock_model.speed = MIN_TIME_MULTIPLIER + 0.1

        command: Final[AdjustSpeedCommand] = AdjustSpeedCommand(delta=-0.1)
        result: Final[CommandResult[float]] = command.execute(mock_model)

        assert result.success is True
        assert result.data == MIN_TIME_MULTIPLIER
        mock_model.set_speed.assert_called_once_with(MIN_TIME_MULTIPLIER)

    def test_execute_at_maximum_boundary(self) -> None:
        """Test adjusting speed exactly at maximum boundary"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        mock_model.speed = MAX_TIME_MULTIPLIER - 0.5

        command: Final[AdjustSpeedCommand] = AdjustSpeedCommand(delta=0.5)
        result: Final[CommandResult[float]] = command.execute(mock_model)

        assert result.success is True
        assert result.data == MAX_TIME_MULTIPLIER
        mock_model.set_speed.assert_called_once_with(MAX_TIME_MULTIPLIER)

    def test_execute_below_minimum_fails(self) -> None:
        """Test that speed below minimum causes failure"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        mock_model.speed = MIN_TIME_MULTIPLIER

        command: Final[AdjustSpeedCommand] = AdjustSpeedCommand(delta=-0.1)
        result: Final[CommandResult[float]] = command.execute(mock_model)

        assert result.success is False
        assert result.error is not None
        assert f"below minimum {MIN_TIME_MULTIPLIER:.2f}" in result.error
        mock_model.set_speed.assert_not_called()

    def test_execute_above_maximum_fails(self) -> None:
        """Test that speed above maximum causes failure"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        mock_model.speed = MAX_TIME_MULTIPLIER

        command: Final[AdjustSpeedCommand] = AdjustSpeedCommand(delta=0.5)
        result: Final[CommandResult[float]] = command.execute(mock_model)

        assert result.success is False
        assert result.error is not None
        assert f"exceeds maximum {MAX_TIME_MULTIPLIER:.2f}" in result.error
        mock_model.set_speed.assert_not_called()

    def test_execute_large_negative_delta_fails(self) -> None:
        """Test that large negative delta causes failure"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        mock_model.speed = 1.0

        command: Final[AdjustSpeedCommand] = AdjustSpeedCommand(delta=-5.0)
        result: Final[CommandResult[float]] = command.execute(mock_model)

        assert result.success is False
        assert result.error is not None
        mock_model.set_speed.assert_not_called()

    def test_execute_large_positive_delta_fails(self) -> None:
        """Test that large positive delta causes failure"""
        mock_model: Final[MagicMock] = MagicMock(spec=GameModel)
        mock_model.speed = 1.0

        command: Final[AdjustSpeedCommand] = AdjustSpeedCommand(delta=20.0)
        result: Final[CommandResult[float]] = command.execute(mock_model)

        assert result.success is False
        assert result.error is not None
        mock_model.set_speed.assert_not_called()
