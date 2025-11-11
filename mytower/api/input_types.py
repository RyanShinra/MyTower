"""
GraphQL input types for mutations.

These input types provide proper GraphQL design patterns where mutations
accept input objects rather than individual parameters. They mirror the
command objects from controller_commands.py but are specifically designed
for the GraphQL API layer.

Uses Pydantic for robust input validation with field validators.
"""

import re
import strawberry
from pydantic import BaseModel, field_validator

from mytower.api.graphql_types import FloorTypeGQL
from mytower.game.core.units import Blocks


# ============================================================================
# Pydantic Models with Validation
# ============================================================================


class AddFloorInputModel(BaseModel):
    """Pydantic model for adding a new floor to the building"""

    floor_type: FloorTypeGQL

    # Floor type is an enum, validated automatically by Pydantic


class AddPersonInputModel(BaseModel):
    """Pydantic model for adding a new person to the building"""

    init_floor: int
    init_horiz_position: Blocks
    dest_floor: int
    dest_horiz_position: Blocks

    @field_validator("init_floor")
    @classmethod
    def validate_init_floor(cls, v: int) -> int:
        """Validate initial floor is in valid range (1-100)"""
        if not (1 <= v <= 100):
            raise ValueError(f"Initial floor must be between 1 and 100, got {v}")
        return v

    @field_validator("dest_floor")
    @classmethod
    def validate_dest_floor(cls, v: int) -> int:
        """Validate destination floor is in valid range (1-100)"""
        if not (1 <= v <= 100):
            raise ValueError(f"Destination floor must be between 1 and 100, got {v}")
        return v

    @field_validator("init_horiz_position")
    @classmethod
    def validate_init_position(cls, v: Blocks) -> Blocks:
        """Validate initial horizontal position is in valid range (0-100 blocks)"""
        if not (0 <= v.value <= 100):
            raise ValueError(f"Initial horizontal position must be between 0 and 100 blocks, got {v.value}")
        return v

    @field_validator("dest_horiz_position")
    @classmethod
    def validate_dest_position(cls, v: Blocks) -> Blocks:
        """Validate destination horizontal position is in valid range (0-100 blocks)"""
        if not (0 <= v.value <= 100):
            raise ValueError(f"Destination horizontal position must be between 0 and 100 blocks, got {v.value}")
        return v


class AddElevatorBankInputModel(BaseModel):
    """Pydantic model for adding a new elevator bank to the building"""

    horiz_position: Blocks
    min_floor: int
    max_floor: int

    @field_validator("horiz_position")
    @classmethod
    def validate_position(cls, v: Blocks) -> Blocks:
        """Validate horizontal position is in valid range (0-100 blocks)"""
        if not (0 <= v.value <= 100):
            raise ValueError(f"Horizontal position must be between 0 and 100 blocks, got {v.value}")
        return v

    @field_validator("min_floor")
    @classmethod
    def validate_min_floor(cls, v: int) -> int:
        """Validate minimum floor is in valid range (1-100)"""
        if not (1 <= v <= 100):
            raise ValueError(f"Minimum floor must be between 1 and 100, got {v}")
        return v

    @field_validator("max_floor")
    @classmethod
    def validate_max_floor(cls, v: int) -> int:
        """Validate maximum floor is in valid range (1-100)"""
        if not (1 <= v <= 100):
            raise ValueError(f"Maximum floor must be between 1 and 100, got {v}")
        return v

    def model_post_init(self, __context) -> None:
        """Validate that max_floor >= min_floor after all fields are set"""
        if self.max_floor < self.min_floor:
            raise ValueError(
                f"Maximum floor ({self.max_floor}) must be greater than or equal to minimum floor ({self.min_floor})"
            )


class AddElevatorInputModel(BaseModel):
    """Pydantic model for adding a new elevator to an existing elevator bank"""

    elevator_bank_id: str

    @field_validator("elevator_bank_id")
    @classmethod
    def validate_elevator_bank_id(cls, v: str) -> str:
        """Validate elevator bank ID is non-empty, reasonable length, and valid format"""
        # Strip whitespace for validation
        stripped_id = v.strip()

        # Validate non-empty
        if not stripped_id:
            raise ValueError("Elevator bank ID cannot be empty")

        # Validate max length (100 characters)
        if len(stripped_id) > 100:
            raise ValueError(f"Elevator bank ID must be 100 characters or less, got {len(stripped_id)} characters")

        # Validate format: alphanumeric + hyphens/underscores
        if not re.match(r"^[a-zA-Z0-9_-]+$", stripped_id):
            raise ValueError(
                "Elevator bank ID must contain only alphanumeric characters, hyphens, and underscores"
            )

        return stripped_id


# ============================================================================
# Strawberry GraphQL Input Types
# ============================================================================


@strawberry.experimental.pydantic.input(model=AddFloorInputModel, all_fields=True)
class AddFloorInput:
    """Input for adding a new floor to the building"""
    pass


@strawberry.experimental.pydantic.input(model=AddPersonInputModel, all_fields=True)
class AddPersonInput:
    """Input for adding a new person to the building"""
    pass


@strawberry.experimental.pydantic.input(model=AddElevatorBankInputModel, all_fields=True)
class AddElevatorBankInput:
    """Input for adding a new elevator bank to the building"""
    pass


@strawberry.experimental.pydantic.input(model=AddElevatorInputModel, all_fields=True)
class AddElevatorInput:
    """Input for adding a new elevator to an existing elevator bank"""
    pass
