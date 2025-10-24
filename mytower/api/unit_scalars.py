# type: ignore
# TODO: There's some idioms in here that mypy / pyright doesn't like; fix them later.
"""
GraphQL scalar types for dimensional units.

Design philosophy:
- Scalars serialize core unit types directly (no wrappers)
- Type annotations use actual game types
- Self-documenting schema with physical meanings
"""

import strawberry

from mytower.game.core.units import Blocks as BlocksCore
from mytower.game.core.units import Meters as MetersCore
from mytower.game.core.units import Pixels as PixelsCore
from mytower.game.core.units import Time as TimeCore
from mytower.game.core.units import Velocity as VelocityCore

# Serialize the actual core types directly
Blocks = strawberry.scalar(
    BlocksCore,
    serialize=lambda v: float(v.value),
    parse_value=lambda v: BlocksCore(float(v)),
    description="Vertical position in building grid coordinates (1 block ≈ 3.2 meters). "
    "Examples: Floor 1 = 1.0, elevator between floors = 2.5",
)

Meters = strawberry.scalar(
    MetersCore,
    serialize=lambda v: float(v.value),
    parse_value=lambda v: MetersCore(float(v)),
    description="Physical distance in SI units (meters). " "Examples: Elevator shaft height = 64.0",
)

Pixels = strawberry.scalar(
    PixelsCore,
    serialize=lambda v: int(v.value),
    parse_value=lambda v: PixelsCore(int(v)),
    description="Screen-space coordinates for rendering (integer pixels). "
    "Note: Clients may compute their own screen positions.",
)

Velocity = strawberry.scalar(
    VelocityCore,
    serialize=lambda v: float(v.value),
    parse_value=lambda v: VelocityCore(float(v)),
    description="Speed in meters per second (m/s). "
    "Examples: Person walking speed = 1.4 m/s, elevator speed = 2.0 m/s",
)

Time = strawberry.scalar(
    TimeCore,
    serialize=lambda v: float(v.value),
    parse_value=lambda v: TimeCore(float(v)),
    description="Time duration in seconds. "
    "Examples: Elevator wait time = 30.0 seconds, person wait time = 120.0 seconds",
)
