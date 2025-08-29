from abc import ABC, abstractmethod
from dataclasses import dataclass

from mytower.game.models.game_model import GameModel
from typing import Optional, TypeVar, Generic, override

from mytower.game.types import FloorType

T = TypeVar('T')

@dataclass
class CommandResult(Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    

class Command(ABC, Generic[T]):
    @abstractmethod
    def execute(self, model: GameModel) -> CommandResult[T]:
        """Execute the command against the game model"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get human-readable description of the command"""
        pass


@dataclass
class AddFloorCommand(Command[bool]):
    floor_type: FloorType
    
    @override
    def execute(self, model: GameModel) -> CommandResult[bool]:
        success = model.add_floor(self.floor_type)
        return CommandResult(success=success)