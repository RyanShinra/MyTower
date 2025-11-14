from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar

from typing_extensions import override

from mytower.game.core.units import Blocks

if TYPE_CHECKING:
    from mytower.game.core.types import FloorType
    from mytower.game.models.game_model import GameModel

T = TypeVar("T")


@dataclass
class CommandResult(Generic[T]):
    success: bool
    data: T | None = None
    error: str | None = None


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
    init_floor: int
    init_horiz_position: Blocks
    dest_floor: int
    dest_horiz_position: Blocks


    @override
    def execute(self, model: GameModel) -> CommandResult[str]:
        if self.init_floor == self.dest_floor and self.init_horiz_position == self.dest_horiz_position:
            return CommandResult(success=False, error="Source and destination cannot be the same")
        # NOTE: We will need to revisit this validation if we add basement floors
        if self.init_floor < 1:
            return CommandResult(success=False, error=f"Invalid source floor: {self.init_floor:.1f}")
        if self.dest_floor < 1:
            return CommandResult(success=False, error=f"Invalid destination floor: {self.dest_floor:.1f}")
        if self.dest_horiz_position < Blocks(0.0):
            return CommandResult(
                success=False, error=f"Invalid destination horiz_position: {self.dest_horiz_position.value:.2f}"
            )
        if self.init_horiz_position < Blocks(0.0):
            return CommandResult(
                success=False, error=f"Invalid source horiz_position: {self.init_horiz_position.value:.2f}"
            )

        person_id: str = model.add_person(
            init_floor=self.init_floor,
            init_horiz_position=self.init_horiz_position,
            dest_floor=self.dest_floor,
            dest_horiz_position=self.dest_horiz_position,
        )
        return CommandResult(success=True, data=person_id)

    @override
    def get_description(self) -> str:
        return (
            f"Add person at floor {self.init_floor:.1f}, horiz_position {self.init_horiz_position.value:.2f} "
            f"with destination floor {self.dest_floor:.1f}, horiz_position {self.dest_horiz_position.value:.2f}"
        )


@dataclass
class AddElevatorBankCommand(Command[str]):
    horiz_position: Blocks
    min_floor: int
    max_floor: int


    @override
    def execute(self, model: GameModel) -> CommandResult[str]:
        if self.horiz_position < Blocks(0):
            return CommandResult(success=False, error=f"Invalid horizontal position: {self.horiz_position.value:.6f}")

        # NOTE: This will need to be revisited if we add basement floors
        if self.min_floor < 1:
            return CommandResult(success=False, error=f"Invalid min floor: {self.min_floor:.1f}")
        if self.max_floor < self.min_floor:
            return CommandResult(
                success=False, error=f"max_floor must be >= min_floor: {self.max_floor:.1f} < {self.min_floor:.1f}"
            )
        el_bank_id: str = model.add_elevator_bank(
            horiz_position=self.horiz_position, min_floor=self.min_floor, max_floor=self.max_floor
        )
        return CommandResult(success=True, data=el_bank_id)

    @override
    def get_description(self) -> str:
        return (
            f"Add elevator bank at horizontal position {self.horiz_position.value:.2f} "
            f"from floor {self.min_floor:.1f} to {self.max_floor:.1f}"
        )


@dataclass
class AddElevatorCommand(Command[str]):
    elevator_bank_id: str


    @override
    def execute(self, model: GameModel) -> CommandResult[str]:
        stripped_id: str = self.elevator_bank_id.strip()
        if not stripped_id:
            return CommandResult(success=False, error="elevator_bank_id cannot be empty")

        # TODO: #29 Make 64 a config value somewhere
        if len(stripped_id) > 64:
            return CommandResult(
                success=False,
                error=f"elevator_bank_id must be less than 64 characters, got {len(stripped_id)} characters",
            )

        el_id: str = model.add_elevator(stripped_id)
        return CommandResult(success=True, data=el_id)

    @override
    def get_description(self) -> str:
        return f"Add elevator to bank {self.elevator_bank_id}"
