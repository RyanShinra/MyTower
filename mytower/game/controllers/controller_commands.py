from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING, TypeVar, Generic, override

if TYPE_CHECKING:
    from mytower.game.models.game_model import GameModel
    from mytower.game.core.types import FloorType

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
class AddFloorCommand(Command[int]):
    floor_type: FloorType
    
    @override
    def execute(self, model: GameModel) -> CommandResult[int]:
        new_floor_num: int = model.add_floor(self.floor_type)
        return CommandResult(success=True, data=new_floor_num)
    
    @override
    def get_description(self) -> str:
        return f"Add a floor of type {self.floor_type}"

    
@dataclass
class AddPersonCommand(Command[str]):
    floor: int
    block: float
    dest_floor: int
    dest_block: int

    @override
    def execute(self, model: GameModel) -> CommandResult[str]:
        if self.floor == self.dest_floor and self.block == self.dest_block:
            return CommandResult(success=False, error="Source and destination cannot be the same")
        # NOTE: We will need to revisit this validation if we add basement floors
        if self.floor < 1:
            return CommandResult(success=False, error=f"Invalid source floor: {self.floor}")
        if self.dest_floor < 1:
            return CommandResult(success=False, error=f"Invalid destination floor: {self.dest_floor}")
        if self.dest_block < 0.0:
            return CommandResult(success=False, error=f"Invalid destination block: {self.dest_block}")
        if self.block < 0.0:
            return CommandResult(success=False, error=f"Invalid source block: {self.block}")
        
        person_id: str = model.add_person(
            floor=self.floor,
            block=self.block,
            dest_floor=self.dest_floor,
            dest_block=self.dest_block
        )
        return CommandResult(success=True, data=person_id)
    
    @override
    def get_description(self) -> str:
        return (
            f"Add person at floor {self.floor}, block {self.block} "
            f"with destination floor {self.dest_floor}, block {self.dest_block}"
        )


@dataclass
class AddElevatorBankCommand(Command[str]):
    h_cell: int
    min_floor: int
    max_floor: int

    @override
    def execute(self, model: GameModel) -> CommandResult[str]:
        if self.h_cell < 0:
            return CommandResult(success=False, error=f"Invalid horizontal cell: {self.h_cell}")
        
        # NOTE: This will need to be revisited if we add basement floors
        if self.min_floor < 1:
            return CommandResult(success=False, error=f"Invalid min floor: {self.min_floor}")
        if self.max_floor < self.min_floor:
            return CommandResult(success=False, error=f"max_floor must be >= min_floor: {self.max_floor} < {self.min_floor}")
         
        el_bank_id: str = model.add_elevator_bank(
            h_cell=self.h_cell,
            min_floor=self.min_floor,
            max_floor=self.max_floor
        )
        return CommandResult(success=True, data=el_bank_id)

    @override
    def get_description(self) -> str:
        return (
            f"Add elevator bank at horizontal cell {self.h_cell} "
            f"from floor {self.min_floor} to {self.max_floor}"
        )


@dataclass
class AddElevatorCommand(Command[str]):
    elevator_bank_id: str

    @override
    def execute(self, model: GameModel) -> CommandResult[str]:
        stripped_id: str = self.elevator_bank_id.strip()
        if not stripped_id or len(stripped_id) == 0:
            return CommandResult(success=False, error="elevator_bank_id cannot be empty")
        
        if len(stripped_id) > 64:
            return CommandResult(success=False, error=f"elevator_bank_id must be less than 64 characters, got {stripped_id}")
        
        el_id: str = model.add_elevator(stripped_id)
        return CommandResult(success=True, data=el_id)

    @override
    def get_description(self) -> str:
        return f"Add elevator to bank {self.elevator_bank_id}"
