from unittest.mock import MagicMock

from mytower.game.controllers.controller_commands import (
    AddElevatorBankCommand,
    AddElevatorCommand,
    AddFloorCommand,
    AddPersonCommand,
    CommandResult,
)
from mytower.game.controllers.game_controller import GameController
from mytower.game.core.units import Blocks
from mytower.game.entities.floor import FloorType
from mytower.game.utilities.demo_builder import build_model_building


class TestDemoBuilder:
    """Test demo building functionality"""


    def test_build_model_building_success(self, mock_logger_provider: MagicMock) -> None:
        """Test successful demo building creation"""
        mock_controller = MagicMock(spec=GameController)


        # Mock successful command executions
        def mock_execute(command):
            if isinstance(command, AddFloorCommand):
                return CommandResult(success=True, data=1)  # Floor number
            elif isinstance(command, AddElevatorBankCommand):
                return CommandResult(success=True, data="bank_123")  # Bank ID
            elif isinstance(command, AddElevatorCommand):
                return CommandResult(success=True, data="elevator_456")  # Elevator ID
            elif isinstance(command, AddPersonCommand):
                return CommandResult(success=True, data="person_789")  # Person ID
            return CommandResult(success=False, error="Unknown command")

        mock_controller.execute_command.side_effect = mock_execute

        # Call the function
        build_model_building(mock_controller, mock_logger_provider)

        # Verify the controller was called the expected number of times
        assert mock_controller.execute_command.call_count > 0

        # Verify floor types were added correctly
        floor_calls = [
            call for call in mock_controller.execute_command.call_args_list if isinstance(call[0][0], AddFloorCommand)
        ]
        assert len(floor_calls) == 18  # Total floors added

        # Verify specific floor types
        floor_types_added = [call[0][0].floor_type for call in floor_calls]
        assert FloorType.LOBBY in floor_types_added
        assert FloorType.RETAIL in floor_types_added
        assert FloorType.RESTAURANT in floor_types_added
        assert FloorType.OFFICE in floor_types_added
        assert FloorType.HOTEL in floor_types_added
        assert FloorType.APARTMENT in floor_types_added

        # Verify elevator bank was added
        bank_calls = [
            call
            for call in mock_controller.execute_command.call_args_list
            if isinstance(call[0][0], AddElevatorBankCommand)
        ]
        assert len(bank_calls) == 1
        bank_command = bank_calls[0][0][0]
        assert bank_command.horiz_position == Blocks(14)
        assert bank_command.min_floor == 1
        assert bank_command.max_floor == 1  # Based on mocked return value

        # Verify elevator was added
        elevator_calls = [
            call
            for call in mock_controller.execute_command.call_args_list
            if isinstance(call[0][0], AddElevatorCommand)
        ]
        assert len(elevator_calls) == 1
        elevator_command = elevator_calls[0][0][0]
        assert elevator_command.elevator_bank_id == "bank_123"

        # Verify people were added
        person_calls = [
            call for call in mock_controller.execute_command.call_args_list if isinstance(call[0][0], AddPersonCommand)
        ]
        assert len(person_calls) == 4


    def test_build_model_building_with_failures(self, mock_logger_provider: MagicMock) -> None:
        """Test demo building creation with some command failures"""
        mock_controller = MagicMock(spec=GameController)


        # Mock some failures
        def mock_execute_with_failures(command):
            if isinstance(command, AddFloorCommand):
                if command.floor_type == FloorType.LOBBY:
                    return CommandResult(success=True, data=1)
                else:
                    return CommandResult(success=False, error="Floor addition failed")
            elif isinstance(command, AddElevatorBankCommand):
                return CommandResult(success=False, error="Bank addition failed")
            elif isinstance(command, AddElevatorCommand):
                return CommandResult(success=False, error="Elevator addition failed")
            elif isinstance(command, AddPersonCommand):
                return CommandResult(success=False, error="Person addition failed")
            return CommandResult(success=False, error="Unknown command")

        mock_controller.execute_command.side_effect = mock_execute_with_failures

        # Should not raise exceptions even with failures
        build_model_building(mock_controller, mock_logger_provider)

        # Verify it still attempted all operations
        assert mock_controller.execute_command.call_count > 20


    def test_build_model_building_command_types(self, mock_logger_provider: MagicMock) -> None:
        """Test that the correct command types are used"""
        mock_controller = MagicMock(spec=GameController)

        # Mock to return incrementing floor numbers
        floor_counter = [0]  # Use list to modify in closure


        def mock_execute(command):
            if isinstance(command, AddFloorCommand):
                floor_counter[0] += 1
                return CommandResult(success=True, data=floor_counter[0])
            elif isinstance(command, AddElevatorBankCommand):
                return CommandResult(success=True, data="bank_123")
            elif isinstance(command, AddElevatorCommand):
                return CommandResult(success=True, data="elevator_456")
            elif isinstance(command, AddPersonCommand):
                return CommandResult(success=True, data="person_789")
            return CommandResult(success=False, error="Unknown command")

        mock_controller.execute_command.side_effect = mock_execute

        build_model_building(mock_controller, mock_logger_provider)

        # Get all executed commands
        all_commands = [call[0][0] for call in mock_controller.execute_command.call_args_list]

        # Verify command types
        floor_commands = [cmd for cmd in all_commands if isinstance(cmd, AddFloorCommand)]
        bank_commands = [cmd for cmd in all_commands if isinstance(cmd, AddElevatorBankCommand)]
        elevator_commands = [cmd for cmd in all_commands if isinstance(cmd, AddElevatorCommand)]
        person_commands = [cmd for cmd in all_commands if isinstance(cmd, AddPersonCommand)]

        assert len(floor_commands) == 18
        assert len(bank_commands) == 1
        assert len(elevator_commands) == 1
        assert len(person_commands) == 4


    def test_build_model_building_floor_sequence(self, mock_logger_provider: MagicMock) -> None:
        """Test that floors are added in the expected sequence"""
        mock_controller = MagicMock(spec=GameController)

        # Track the order of floor types
        floor_types_order = []


        def mock_execute(command):
            if isinstance(command, AddFloorCommand):
                floor_types_order.append(command.floor_type)
                return CommandResult(success=True, data=len(floor_types_order))
            elif isinstance(command, AddElevatorBankCommand):
                return CommandResult(success=True, data="bank_123")
            elif isinstance(command, AddElevatorCommand):
                return CommandResult(success=True, data="elevator_456")
            elif isinstance(command, AddPersonCommand):
                return CommandResult(success=True, data="person_789")
            return CommandResult(success=False, error="Unknown command")

        mock_controller.execute_command.side_effect = mock_execute

        build_model_building(mock_controller, mock_logger_provider)

        # Verify the expected sequence
        expected_sequence = [
            FloorType.LOBBY,
            FloorType.RETAIL,
            FloorType.RETAIL,
            FloorType.RETAIL,
            FloorType.RESTAURANT,
            FloorType.RESTAURANT,
            FloorType.OFFICE,
            FloorType.OFFICE,
            FloorType.OFFICE,
            FloorType.OFFICE,
            FloorType.HOTEL,
            FloorType.HOTEL,
            FloorType.HOTEL,
            FloorType.HOTEL,
            FloorType.APARTMENT,
            FloorType.APARTMENT,
            FloorType.APARTMENT,
            FloorType.APARTMENT,
        ]

        assert floor_types_order == expected_sequence


    def test_build_model_building_person_placement(self, mock_logger_provider: MagicMock) -> None:
        """Test that people are placed with correct parameters"""
        mock_controller = MagicMock(spec=GameController)

        # Track person commands
        person_commands = []


        def mock_execute(command):
            if isinstance(command, AddFloorCommand):
                return CommandResult(success=True, data=1)
            elif isinstance(command, AddElevatorBankCommand):
                return CommandResult(success=True, data="bank_123")
            elif isinstance(command, AddElevatorCommand):
                return CommandResult(success=True, data="elevator_456")
            elif isinstance(command, AddPersonCommand):
                person_commands.append(command)
                return CommandResult(success=True, data="person_789")
            return CommandResult(success=False, error="Unknown command")

        mock_controller.execute_command.side_effect = mock_execute

        build_model_building(mock_controller, mock_logger_provider)

        # Verify person placements
        assert len(person_commands) == 4

        # Check specific person placements (based on the demo_builder.py code)
        expected_people: list[tuple[int, float, int, float]] = [
            (1, 1.0, 12, 7.0),
            (1, 3.0, 3, 7.0),
            (1, 6.0, 7, 7.0),
            (12, 1.0, 1, 1.0),
        ]

        actual_people = [(cmd.floor, cmd.init_horiz_position.value, cmd.dest_floor, cmd.dest_horiz_position.value) for cmd in person_commands]

        assert actual_people == expected_people


    def test_build_model_building_elevator_bank_parameters(self, mock_logger_provider: MagicMock) -> None:
        """Test that elevator bank is created with correct parameters"""
        mock_controller = MagicMock(spec=GameController)

        # Track elevator bank command
        bank_command = None
        top_floor = 18  # Expected based on the number of floors


        def mock_execute(command):
            nonlocal bank_command
            if isinstance(command, AddFloorCommand):
                return CommandResult(success=True, data=top_floor)  # Return top floor
            elif isinstance(command, AddElevatorBankCommand):
                bank_command = command
                return CommandResult(success=True, data="bank_123")
            elif isinstance(command, AddElevatorCommand):
                return CommandResult(success=True, data="elevator_456")
            elif isinstance(command, AddPersonCommand):
                return CommandResult(success=True, data="person_789")
            return CommandResult(success=False, error="Unknown command")

        mock_controller.execute_command.side_effect = mock_execute

        build_model_building(mock_controller, mock_logger_provider)

        # Verify elevator bank parameters
        assert bank_command is not None
        assert bank_command.horiz_position == Blocks(14)
        assert bank_command.min_floor == 1
        assert bank_command.max_floor == top_floor
