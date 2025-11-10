"""
GraphQL input types for mutations.

These input types provide proper GraphQL design patterns where mutations
accept input objects rather than individual parameters. They mirror the
command objects from controller_commands.py but are specifically designed
for the GraphQL API layer.
"""

import re
import strawberry

from mytower.api.graphql_types import FloorTypeGQL
from mytower.game.core.units import Blocks


@strawberry.input
class AddFloorInput:
    """Input for adding a new floor to the building"""

    floor_type: FloorTypeGQL

    def validate(self) -> None:
        """Validate floor input. FloorTypeGQL is an enum and already validated by Strawberry."""
        # Floor type is an enum, so no additional validation needed
        pass


@strawberry.input
class AddPersonInput:
    """Input for adding a new person to the building"""

    init_floor: int
    init_horiz_position: Blocks
    dest_floor: int
    dest_horiz_position: Blocks

    def validate(self) -> None:
        """Validate person input parameters."""
        # Validate floor numbers (1-100 range)
        if not (1 <= self.init_floor <= 100):
            raise ValueError(f"Initial floor must be between 1 and 100, got {self.init_floor}")
        if not (1 <= self.dest_floor <= 100):
            raise ValueError(f"Destination floor must be between 1 and 100, got {self.dest_floor}")

        # Validate positions (0-100 blocks range)
        if not (0 <= self.init_horiz_position.value <= 100):
            raise ValueError(
                f"Initial horizontal position must be between 0 and 100 blocks, got {self.init_horiz_position.value}"
            )
        if not (0 <= self.dest_horiz_position.value <= 100):
            raise ValueError(
                f"Destination horizontal position must be between 0 and 100 blocks, got {self.dest_horiz_position.value}"
            )


@strawberry.input
class AddElevatorBankInput:
    """Input for adding a new elevator bank to the building"""

    horiz_position: Blocks
    min_floor: int
    max_floor: int

    def validate(self) -> None:
        """Validate elevator bank input parameters."""
        # Validate horizontal position (0-100 blocks range)
        if not (0 <= self.horiz_position.value <= 100):
            raise ValueError(
                f"Horizontal position must be between 0 and 100 blocks, got {self.horiz_position.value}"
            )

        # Validate floor numbers (1-100 range)
        if not (1 <= self.min_floor <= 100):
            raise ValueError(f"Minimum floor must be between 1 and 100, got {self.min_floor}")
        if not (1 <= self.max_floor <= 100):
            raise ValueError(f"Maximum floor must be between 1 and 100, got {self.max_floor}")

        # Validate max >= min
        if self.max_floor < self.min_floor:
            raise ValueError(
                f"Maximum floor ({self.max_floor}) must be greater than or equal to minimum floor ({self.min_floor})"
            )


@strawberry.input
class AddElevatorInput:
    """Input for adding a new elevator to an existing elevator bank"""

    elevator_bank_id: str

    def validate(self) -> None:
        """Validate elevator input parameters."""
        # Strip whitespace for validation
        stripped_id = self.elevator_bank_id.strip()

        # Validate non-empty
        if not stripped_id:
            raise ValueError("Elevator bank ID cannot be empty")

        # Validate max length (100 characters)
        if len(stripped_id) > 100:
            raise ValueError(
                f"Elevator bank ID must be 100 characters or less, got {len(stripped_id)} characters"
            )

        # Validate format: alphanumeric + hyphens/underscores
        if not re.match(r"^[a-zA-Z0-9_-]+$", stripped_id):
            raise ValueError(
                "Elevator bank ID must contain only alphanumeric characters, hyphens, and underscores"
            )
