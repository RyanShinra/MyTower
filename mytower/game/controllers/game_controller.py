"""
Controller layer: Coordinates between model and external interfaces
Handles commands, manages update cycles
"""
# from typing import Any, Dict, List, Optional
from typing import Optional
from mytower.game.logger import LoggerProvider, MyTowerLogger
from mytower.game.models.game_model import BuildingSnapshot, ElevatorSnapshot, GameModel, PersonSnapshot

class GameController:
    """
    Coordinates game logic, handles commands from various sources
    Acts as the interface between external systems (pygame, GraphQL) and the model
    """
    def __init__(self, model: GameModel, logger_provider: LoggerProvider) -> None:
        self._model: GameModel = model
        self._logger: MyTowerLogger = logger_provider.get_logger("GameController")
    
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
    
    
    # # Command interface
    # def execute_command(self, command: str, **kwargs: Any) -> Dict[str, Any]:
    #     """
    #     Execute a command and return result
    #     Returns: {"success": bool, "data": Any, "error": Optional[str]}
    #     """
    #     try:
    #         match command:
    #             case "add_floor":
    #                 floor_type = kwargs.get("floor_type")
    #                 success = self._model.add_floor(floor_type)
    #                 return {"success": success, "data": None, "error": None}
                
    #             case "add_person":
    #                 person_id = self._model.add_person(
    #                     kwargs["floor"], kwargs["block"], 
    #                     kwargs["dest_floor"], kwargs["dest_block"]
    #                 )
    #                 return {
    #                     "success": person_id is not None, 
    #                     "data": {"person_id": person_id}, 
    #                     "error": None
    #                 }
                
    #             case "set_speed":
    #                 success = self._model.set_game_speed(kwargs["speed"])
    #                 return {"success": success, "data": {"speed": kwargs["speed"]}, "error": None}
                
    #             case "toggle_pause":
    #                 paused = self._model.toggle_pause()
    #                 return {"success": True, "data": {"paused": paused}, "error": None}
                
    #             case _:
    #                 return {"success": False, "data": None, "error": f"Unknown command: {command}"}
        
    #     except Exception as e:
    #         self._logger.error(f"Command execution failed: {command}, error: {e}")
    #         return {"success": False, "data": None, "error": str(e)}
    
    # Simulation management
    def update(self, dt: float) -> None:
        """Update the game simulation"""
        self._model.update(dt)
    
    def is_paused(self) -> bool:
        """Check if game is currently paused"""
        return self._model.is_paused
    
    def get_game_time(self) -> float:
        """Get current game time"""
        return self._model.current_time