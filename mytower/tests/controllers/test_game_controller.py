# pyright: reportPrivateUsage=false
# pylint: disable=protected-access
from typing import List
from unittest.mock import MagicMock
import pytest

from mytower.game.controllers.game_controller import GameController
from mytower.game.controllers.controller_commands import Command, CommandResult
from mytower.game.core.units import Time
from mytower.game.models.game_model import GameModel
from mytower.game.models.model_snapshots import BuildingSnapshot, ElevatorBankSnapshot, ElevatorSnapshot, FloorSnapshot, PersonSnapshot


class TestGameControllerBasics:
    """Test basic GameController functionality"""

    def test_initialization(self, mock_logger_provider: MagicMock) -> None:
        """Test GameController initialization"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        
        assert controller._model == mock_model
        assert controller._fail_fast is False
        assert len(controller._command_history) == 0

    def test_initialization_with_fail_fast(self, mock_logger_provider: MagicMock) -> None:
        """Test GameController initialization with fail_fast enabled"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=True, print_exceptions=False)
        
        assert controller._fail_fast is True


class TestCommandExecution:
    """Test command execution functionality"""

    def test_execute_successful_command(self, mock_logger_provider: MagicMock) -> None:
        """Test executing a successful command"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        
        # Create mock command that succeeds
        mock_command: MagicMock = MagicMock(spec=Command)
        mock_command.execute.return_value = CommandResult(success=True, data="test_result")
        mock_command.get_description.return_value = "Test command"
        
        result: CommandResult[str] = controller.execute_command(mock_command)
        
        assert result.success is True
        assert result.data == "test_result"
        assert len(controller._command_history) == 1
        assert controller._command_history[0] == mock_command
        mock_command.execute.assert_called_once_with(mock_model)

    def test_execute_failed_command(self, mock_logger_provider: MagicMock) -> None:
        """Test executing a failed command"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        
        # Create mock command that fails
        mock_command: MagicMock = MagicMock(spec=Command)
        mock_command.execute.return_value = CommandResult(success=False, error="Test error")
        mock_command.get_description.return_value = "Failed command"
        
        result: CommandResult[None] = controller.execute_command(mock_command)
        
        assert result.success is False
        assert result.error == "Test error"
        assert len(controller._command_history) == 0  # Failed commands not added to history
        mock_command.execute.assert_called_once_with(mock_model)

    def test_execute_command_exception_without_fail_fast(self, mock_logger_provider: MagicMock) -> None:
        """Test command execution with exception when fail_fast is False"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        
        # Create mock command that raises exception
        mock_command: MagicMock = MagicMock(spec=Command)
        mock_command.execute.side_effect = RuntimeError("Test exception")
        mock_command.get_description.return_value = "Crashing command"
        
        result: CommandResult[None] = controller.execute_command(mock_command)
        
        assert result.success is False
        # Ensure that the error field is populated when a command crashes and fail_fast is False
        assert result.error is not None
        assert "Command crashed: Test exception" in result.error
        assert len(controller._command_history) == 0

    def test_execute_command_exception_with_fail_fast(self, mock_logger_provider: MagicMock) -> None:
        """Test command execution with exception when fail_fast is True"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=True, print_exceptions=False)
        
        # Create mock command that raises exception
        mock_command: MagicMock = MagicMock(spec=Command)
        mock_command.execute.side_effect = RuntimeError("Test exception")
        mock_command.get_description.return_value = "Crashing command"
        
        with pytest.raises(RuntimeError, match="Test exception"):
            controller.execute_command(mock_command)


class TestQueryInterface:
    """Test query interface methods"""

    def test_get_building_state(self, mock_logger_provider: MagicMock) -> None:
        """Test getting building state"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        mock_building_snapshot: MagicMock = MagicMock()
        mock_model.get_building_snapshot.return_value = mock_building_snapshot
        
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        result: BuildingSnapshot = controller.get_building_state()
        
        assert result == mock_building_snapshot
        mock_model.get_building_snapshot.assert_called_once()

    def test_get_person_state(self, mock_logger_provider: MagicMock) -> None:
        """Test getting person state by ID"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        mock_person_snapshot: MagicMock = MagicMock()
        mock_model.get_person_by_id.return_value = mock_person_snapshot
        
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        result: PersonSnapshot | None = controller.get_person_state("person_123")
        
        assert result == mock_person_snapshot
        mock_model.get_person_by_id.assert_called_once_with("person_123")

    def test_get_person_state_not_found(self, mock_logger_provider: MagicMock) -> None:
        """Test getting person state when person not found"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        mock_model.get_person_by_id.return_value = None
        
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        result: PersonSnapshot | None = controller.get_person_state("nonexistent")
        
        assert result is None
        mock_model.get_person_by_id.assert_called_once_with("nonexistent")

    def test_get_elevator_state(self, mock_logger_provider: MagicMock) -> None:
        """Test getting elevator state by ID"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        mock_elevator_snapshot: MagicMock = MagicMock()
        mock_model.get_elevator_by_id.return_value = mock_elevator_snapshot
        
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        result: ElevatorSnapshot | None = controller.get_elevator_state("elevator_456")
        
        assert result == mock_elevator_snapshot
        mock_model.get_elevator_by_id.assert_called_once_with("elevator_456")

    def test_get_all_people(self, mock_logger_provider: MagicMock) -> None:
        """Test getting all people"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        mock_people_list: List[MagicMock] = [MagicMock(), MagicMock()]
        mock_model.get_all_people.return_value = mock_people_list
        
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        result: List[PersonSnapshot] = controller.get_all_people()
        
        assert result == mock_people_list
        mock_model.get_all_people.assert_called_once()

    def test_get_all_elevators(self, mock_logger_provider: MagicMock) -> None:
        """Test getting all elevators"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        mock_elevators_list: List[MagicMock] = [MagicMock(), MagicMock(), MagicMock()]
        mock_model.get_all_elevators.return_value = mock_elevators_list
        
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        result: List[ElevatorSnapshot] = controller.get_all_elevators()
        
        assert result == mock_elevators_list
        mock_model.get_all_elevators.assert_called_once()

    def test_get_all_elevator_banks(self, mock_logger_provider: MagicMock) -> None:
        """Test getting all elevator banks"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        mock_banks_list: List[MagicMock] = [MagicMock()]
        mock_model.get_all_elevator_banks.return_value = mock_banks_list
        
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        result: List[ElevatorBankSnapshot] = controller.get_all_elevator_banks()
        
        assert result == mock_banks_list
        mock_model.get_all_elevator_banks.assert_called_once()

    def test_get_all_floors(self, mock_logger_provider: MagicMock) -> None:
        """Test getting all floors"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        mock_floors_list: List[MagicMock] = [MagicMock(), MagicMock()]
        mock_model.get_all_floors.return_value = mock_floors_list
        
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        result: List[FloorSnapshot] = controller.get_all_floors()
        
        assert result == mock_floors_list
        mock_model.get_all_floors.assert_called_once()


class TestSimulationManagement:
    """Test simulation management functionality"""

    def test_update(self, mock_logger_provider: MagicMock) -> None:
        """Test updating simulation"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        
        controller.update(1.5)
        
        mock_model.update.assert_called_once_with(Time(1.5))

    def test_is_paused(self, mock_logger_provider: MagicMock) -> None:
        """Test checking if game is paused"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        mock_model.is_paused = True
        
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        result: bool = controller.is_paused()
        
        assert result is True

    def test_set_paused(self, mock_logger_provider: MagicMock) -> None:
        """Test setting paused state"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        
        controller.set_paused(True)
        mock_model.set_pause_state.assert_called_once_with(True)
        
        controller.set_paused(False)
        mock_model.set_pause_state.assert_called_with(False)

    def test_set_speed(self, mock_logger_provider: MagicMock) -> None:
        """Test setting game speed"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        
        controller.set_speed(2.5)
        
        mock_model.set_speed.assert_called_once_with(2.5)

    def test_speed_property(self, mock_logger_provider: MagicMock) -> None:
        """Test getting current speed"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        mock_model.speed = 3.0
        
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        result: float = controller.speed
        
        assert result == 3.0

    def test_get_game_time(self, mock_logger_provider: MagicMock) -> None:
        """Test getting current game time"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        mock_model.current_time = 12345.67
        
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        result: float = controller.get_game_time()
        
        assert result == 12345.67

    def test_get_command_history(self, mock_logger_provider: MagicMock) -> None:
        """Test getting command history"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        
        # Add some successful commands to history
        mock_command1: MagicMock = MagicMock(spec=Command)
        mock_command1.execute.return_value = CommandResult(success=True, data="result1")
        mock_command1.get_description.return_value = "Command 1"
        
        mock_command2: MagicMock = MagicMock(spec=Command)
        mock_command2.execute.return_value = CommandResult(success=True, data="result2")
        mock_command2.get_description.return_value = "Command 2"
        
        controller.execute_command(mock_command1)
        controller.execute_command(mock_command2)
        
        history: List[str] = controller.get_command_history()
        
        assert len(history) == 2
        assert history[0] == "Command 1"
        assert history[1] == "Command 2"

    def test_get_command_history_only_successful_commands(self, mock_logger_provider: MagicMock) -> None:
        """Test that command history only contains successful commands"""
        mock_model: MagicMock = MagicMock(spec=GameModel)
        controller: GameController = GameController(mock_model, mock_logger_provider, fail_fast=False, print_exceptions=False)
        
        # Add successful command
        mock_success_command: MagicMock = MagicMock(spec=Command)
        mock_success_command.execute.return_value = CommandResult(success=True, data="success")
        mock_success_command.get_description.return_value = "Success Command"
        
        # Add failed command
        mock_failed_command: MagicMock = MagicMock(spec=Command)
        mock_failed_command.execute.return_value = CommandResult(success=False, error="failure")
        mock_failed_command.get_description.return_value = "Failed Command"
        
        controller.execute_command(mock_success_command)
        controller.execute_command(mock_failed_command)
        
        history: List[str] = controller.get_command_history()
        
        assert len(history) == 1
        assert history[0] == "Success Command"