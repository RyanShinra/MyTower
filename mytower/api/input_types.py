# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

"""
GraphQL input types for mutations, and the Pydantic models that validate them.
https://github.com/pydantic/pydantic

Each mutation input is defined twice, and the two classes do different jobs:

- ``AddElevatorBankInputModel(BaseModel)`` is the validator. Each of its fields is annotated with a type
  that should match the same field on ``AddElevatorBankInput`` below. Each ``@field_validator("name")``
  function checks one field's value: is ``max_floor`` in range, is the bank ID valid. These functions run
  each time the model is constructed, either directly with ``AddElevatorBankInputModel(...)`` or by
  ``input.to_pydantic()``, which constructs it from a GraphQL input. Pydantic checks the names in
  ``@field_validator`` when the class is defined, so a misspelled name fails at import.
- ``AddElevatorBankInput``, decorated with
  ``@strawberry.experimental.pydantic.input(model=AddElevatorBankInputModel)``, is the GraphQL interface:
  its fields become the input type in the schema, and it is what a mutation receives. The decorator links
  each field to the model field of the same name. It does not check the names: one the model lacks, such
  as ``mx_floor``, becomes an extra GraphQL-only field, and the model field it was meant to match
  (``max_floor``) disappears from the schema without an error.

The fields are written out on both classes. The decorator has an option, ``all_fields=True``, that copies
every model field onto the GraphQL class at import time, so they need not be written twice. It is not used
here because mypy never runs the decorator; it reads only what is written in the class body. With
``all_fields=True`` that body was empty, so every ``input.max_floor`` in schema.py was an error and a real
typo looked the same as a correct name. With the fields written out, mypy accepts ``input.max_floor`` and
flags ``input.mx_floor``.

TODO(#191): the validators do not run on GraphQL input yet, because no mutation constructs the model.
"""

import strawberry
from pydantic import BaseModel, ConfigDict, field_validator

from mytower.api.graphql_types import FloorTypeGQL
from mytower.api.validation_constants import (
    ELEVATOR_BANK_ID_PATTERN,
    MAX_ELEVATOR_BANK_ID_LENGTH,
    MAX_FLOOR_NUMBER,
    MAX_POSITION_BLOCKS,
    MIN_FLOOR_NUMBER,
    MIN_POSITION_BLOCKS,
)
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

    model_config = ConfigDict(arbitrary_types_allowed=True)

    init_floor: int
    init_horiz_position: Blocks
    dest_floor: int
    dest_horiz_position: Blocks

    @field_validator("init_floor")
    @classmethod
    def validate_init_floor(cls, v: int) -> int:
        """Validate initial floor is in valid range"""
        if not (MIN_FLOOR_NUMBER <= v <= MAX_FLOOR_NUMBER):
            raise ValueError(
                f"Initial floor must be between {MIN_FLOOR_NUMBER} and {MAX_FLOOR_NUMBER}, got {v}"
            )
        return v

    @field_validator("dest_floor")
    @classmethod
    def validate_dest_floor(cls, v: int) -> int:
        """Validate destination floor is in valid range"""
        if not (MIN_FLOOR_NUMBER <= v <= MAX_FLOOR_NUMBER):
            raise ValueError(
                f"Destination floor must be between {MIN_FLOOR_NUMBER} and {MAX_FLOOR_NUMBER}, got {v}"
            )
        return v

    @field_validator("init_horiz_position")
    @classmethod
    def validate_init_position(cls, v: Blocks) -> Blocks:
        """Validate initial horizontal position is in valid range"""
        if not (MIN_POSITION_BLOCKS <= v.value <= MAX_POSITION_BLOCKS):
            raise ValueError(
                f"Initial horizontal position must be between {MIN_POSITION_BLOCKS} "
                f"and {MAX_POSITION_BLOCKS} blocks, got {v.value}"
            )
        return v

    @field_validator("dest_horiz_position")
    @classmethod
    def validate_dest_position(cls, v: Blocks) -> Blocks:
        """Validate destination horizontal position is in valid range"""
        if not (MIN_POSITION_BLOCKS <= v.value <= MAX_POSITION_BLOCKS):
            raise ValueError(
                f"Destination horizontal position must be between {MIN_POSITION_BLOCKS} "
                f"and {MAX_POSITION_BLOCKS} blocks, got {v.value}"
            )
        return v


class AddElevatorBankInputModel(BaseModel):
    """Pydantic model for adding a new elevator bank to the building"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    horiz_position: Blocks
    min_floor: int
    max_floor: int

    @field_validator("horiz_position")
    @classmethod
    def validate_position(cls, v: Blocks) -> Blocks:
        """Validate horizontal position is in valid range"""
        if not (MIN_POSITION_BLOCKS <= v.value <= MAX_POSITION_BLOCKS):
            raise ValueError(
                f"Horizontal position must be between {MIN_POSITION_BLOCKS} "
                f"and {MAX_POSITION_BLOCKS} blocks, got {v.value}"
            )
        return v

    @field_validator("min_floor")
    @classmethod
    def validate_min_floor(cls, v: int) -> int:
        """Validate minimum floor is in valid range"""
        if not (MIN_FLOOR_NUMBER <= v <= MAX_FLOOR_NUMBER):
            raise ValueError(f"Minimum floor must be between {MIN_FLOOR_NUMBER} and {MAX_FLOOR_NUMBER}, got {v}")
        return v

    @field_validator("max_floor")
    @classmethod
    def validate_max_floor(cls, v: int) -> int:
        """Validate maximum floor is in valid range"""
        if not (MIN_FLOOR_NUMBER <= v <= MAX_FLOOR_NUMBER):
            raise ValueError(f"Maximum floor must be between {MIN_FLOOR_NUMBER} and {MAX_FLOOR_NUMBER}, got {v}")
        return v

    def model_post_init(self, _context: object) -> None:
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
        """Validate elevator bank ID (must not have leading/trailing whitespace)"""
        # Validate non-empty (after stripping whitespace)
        if not v.strip():
            raise ValueError("Elevator bank ID cannot be empty")

        # Reject IDs with leading or trailing whitespace
        if v != v.strip():
            raise ValueError("Elevator bank ID must not have leading or trailing whitespace")

        # Validate max length
        if len(v) > MAX_ELEVATOR_BANK_ID_LENGTH:
            raise ValueError(
                f"Elevator bank ID must be {MAX_ELEVATOR_BANK_ID_LENGTH} characters or less, got {len(v)} characters"
            )

        # Validate format: alphanumeric + hyphens/underscores
        if not ELEVATOR_BANK_ID_PATTERN.match(v):
            raise ValueError(
                "Elevator bank ID must contain only alphanumeric characters, hyphens, and underscores"
            )

        return v


# ============================================================================
# Strawberry GraphQL Input Types
# ============================================================================
#
# NOTE: Using strawberry.experimental.pydantic API
#
# This API is marked as experimental and may change in future Strawberry releases.
# To prevent breaking changes, strawberry-graphql is pinned to <1.0.0 in requirements.
#
# Current version: 0.245.0+
# Status: Experimental (as of 2025-11)
#
# Migration plan:
# - Monitor: https://github.com/strawberry-graphql/strawberry/discussions
# - When stable API is released, migrate and remove version pin
# - Check for updates quarterly or when major features are needed


@strawberry.experimental.pydantic.input(model=AddFloorInputModel)
class AddFloorInput:
    """Input for adding a new floor to the building"""
    floor_type: FloorTypeGQL


@strawberry.experimental.pydantic.input(model=AddPersonInputModel)
class AddPersonInput:
    """Input for adding a new person to the building"""
    init_floor: int
    init_horiz_position: Blocks
    dest_floor: int
    dest_horiz_position: Blocks


@strawberry.experimental.pydantic.input(model=AddElevatorBankInputModel)
class AddElevatorBankInput:
    """Input for adding a new elevator bank to the building"""
    horiz_position: Blocks
    min_floor: int
    max_floor: int


@strawberry.experimental.pydantic.input(model=AddElevatorInputModel)
class AddElevatorInput:
    """Input for adding a new elevator to an existing elevator bank"""
    elevator_bank_id: str
