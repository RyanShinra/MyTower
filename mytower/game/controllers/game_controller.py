"""
Controller layer: Coordinates between model and external interfaces
Handles commands, manages update cycles
"""
# mypy: allow-any-explicit

# We don't care what type T the Command[T] is, we're just passing it through. 
# The abstract base class provides the protection we need for what we do 
# (execute and get_description, Also, log errors from the result)

from typing import Any, Final, List, Optional
from mytower.game.controllers.controller_commands import Command, CommandResult
from mytower.game.models.model_snapshots import ElevatorBankSnapshot, FloorSnapshot
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger
from mytower.game.models.game_model import BuildingSnapshot, ElevatorSnapshot, GameModel, PersonSnapshot



class GameController:
    """
    Coordinates game logic, handles commands from various sources
    Acts as the interface between external systems (pygame, GraphQL) and the model
    """
    def __init__(self, model: GameModel, logger_provider: LoggerProvider, fail_fast: bool, print_exceptions: bool) -> None:
        self._fail_fast: bool = fail_fast
        self._print_exceptions: bool = print_exceptions
        self._logger: MyTowerLogger = logger_provider.get_logger("GameController")
        
        self._model: GameModel = model
        self._command_history: List[Command[Any]] = []  # For potential undo functionality

    
    # Command execution
    def execute_command(self, command: Command[Any]) -> CommandResult[Any]:
        """Execute a command and optionally store for history"""
        try:
            result: Final[CommandResult[Any]] = command.execute(self._model)
            
            if result.success:
                self._command_history.append(command)
                self._logger.info(f"Executed: {command.get_description()}")
            else:
                self._logger.warning(f"Failed: {command.get_description()} - {result.error}")
            
            return result
        
        except Exception as e:
            if self._print_exceptions:
                self._logger.exception(f"Command execution crashed: {command.get_description()} - {str(e)}")
            else:
                self._logger.error(f"Command execution crashed: {command.get_description()} - {str(e)}")

            if self._fail_fast:
                raise e
            return CommandResult(success=False, error=f"Command crashed: {str(e)}")
    
    # Query interface
    def get_building_state(self) -> BuildingSnapshot:
        """Get current building state"""
        return self._model.get_building_snapshot()
    
    def get_person_state(self, person_id: str) -> Optional[PersonSnapshot]:
        """Get specific person state"""
        return self._model.get_person_by_id(person_id)
    
    def get_elevator_state(self, elevator_id: str) -> Optional[ElevatorSnapshot]:
        """Get specific elevator state"""
        return self._model.get_elevator_by_id(elevator_id)
    
    def get_all_people(self) -> List[PersonSnapshot]:
        """Get all people in the building"""
        return self._model.get_all_people()
    
    def get_all_elevators(self) -> List[ElevatorSnapshot]:
        """Get all elevators in the building"""
        return self._model.get_all_elevators()

    def get_all_elevator_banks(self) -> List[ElevatorBankSnapshot]:
        """Get all elevator banks in the building"""
        return self._model.get_all_elevator_banks()
    
    def get_all_floors(self) -> List[FloorSnapshot]:
        """Get all floors in the building"""
        return self._model.get_all_floors()

    # Simulation management
    def update(self, dt: float) -> None:
        """Update the game simulation"""
        self._model.update(dt)
    
    def is_paused(self) -> bool:
        """Check if game is currently paused"""
        return self._model.is_paused
    
    def set_paused(self, paused: bool) -> None:
        """Set the paused state of the game"""
        self._model.set_pause_state(paused)

    def set_speed(self, speed: float) -> None:
        """Set the game speed multiplier (0.0 to 10.0)"""
        self._model.set_speed(speed)
        
    @property
    def speed(self) -> float:
        """Get current game speed"""
        return self._model.speed

    def get_game_time(self) -> float:
        """Get current game time"""
        return self._model.current_time
    
    def get_command_history(self) -> List[str]:
        """Get history of executed commands (for debugging/undo)"""
        return [cmd.get_description() for cmd in self._command_history]