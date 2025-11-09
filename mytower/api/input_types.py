"""
GraphQL input types for mutations.

These input types provide proper GraphQL design patterns where mutations
accept input objects rather than individual parameters. They mirror the
command objects from controller_commands.py but are specifically designed
for the GraphQL API layer.
"""

import strawberry

from mytower.api.graphql_types import FloorTypeGQL
from mytower.game.core.units import Blocks


@strawberry.input
class AddFloorInput:
    """Input for adding a new floor to the building"""

    floor_type: FloorTypeGQL


@strawberry.input
class AddPersonInput:
    """Input for adding a new person to the building"""

    init_floor: int
    init_horiz_position: Blocks
    dest_floor: int
    dest_horiz_position: Blocks


@strawberry.input
class AddElevatorBankInput:
    """Input for adding a new elevator bank to the building"""

    horiz_position: Blocks
    min_floor: int
    max_floor: int


@strawberry.input
class AddElevatorInput:
    """Input for adding a new elevator to an existing elevator bank"""

    elevator_bank_id: str
