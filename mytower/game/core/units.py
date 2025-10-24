from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import overload, override  # Add overload

from mytower.game.core.primitive_constants import (
    BLOCK_FLOAT_TOLERANCE,
    METERS_PER_BLOCK,
    METRIC_FLOAT_TOLERANCE,
    PIXELS_PER_METER,
    TIME_FLOAT_TOLERANCE,
)


@dataclass(frozen=True, slots=True, order=True)
class Meters:
    """
    Physical distance measurement in SI units.

    Design notes:
    - frozen=True: Immutable value semantics (like C++ const)
    - slots=True: No __dict__ overhead (~70% memory reduction)
    - order=True: Auto-generates __lt__, __le__, __gt__, __ge__
    - Custom __eq__: Floating-point tolerance for physics calculations
    """

    value: float = field(
        metadata={"unit": "meters", "si_base": True, "description": "Physical measurement for collision detection"}
    )

    def __post_init__(self) -> None:
        """Validate finite value for physics safety"""
        # Coerce to float to ensure consistent internal type (even if initialized with int)
        object.__setattr__(self, "value", float(self.value))
        if not math.isfinite(self.value):
            raise ValueError(f"Meters value must be finite, got {self.value}")

    def __add__(self, other: Meters) -> Meters:
        return Meters(self.value + other.value)

    def __sub__(self, other: Meters) -> Meters:
        return Meters(self.value - other.value)

    def __mul__(self, factor: float) -> Meters:
        return Meters(self.value * factor)

    # flake8: noqa: E704
    @overload
    def __truediv__(self, divisor: float) -> Meters: ...

    @overload
    def __truediv__(self, divisor: Time) -> Velocity: ...

    @overload
    def __truediv__(self, divisor: Velocity) -> Time: ...

    def __truediv__(self, divisor: float | Time | Velocity) -> Meters | Velocity | Time:
        """
        Meters / scalar = Meters
        Meters / Time = Velocity (dimensional analysis!)
        Meters / Velocity = Time (dimensional analysis!)
        """
        if isinstance(divisor, Time):
            return Velocity(self.value / divisor.value)
        if isinstance(divisor, Velocity):
            return Time(self.value / divisor.value)
        return Meters(self.value / divisor)

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Meters):
            return NotImplemented
        return abs(self.value - other.value) < METRIC_FLOAT_TOLERANCE

    @override
    def __repr__(self) -> str:
        return f"Meters({self.value})"

    @property
    def in_pixels(self) -> Pixels:
        return Pixels(int(self.value * PIXELS_PER_METER))

    @property
    def in_blocks(self) -> Blocks:
        blocks_per_meter: float = 1.0 / METERS_PER_BLOCK
        return Blocks(self.value * blocks_per_meter)  # 1 block = 3.2 meters

    def __int__(self) -> int:
        return int(self.value)

    def __float__(self) -> float:
        return float(self.value)

    def __abs__(self) -> Meters:
        """Return absolute value while preserving type"""
        return Meters(abs(self.value))


@dataclass(frozen=True, slots=True, order=True)
class Pixels:
    """
    Integer screen-space coordinate for rendering.

    Design notes:
    - Integer precision (no floating-point tolerance needed)
    - order=True: Auto-generates __lt__, __le__, __gt__, __ge__
    - Optimized for high allocation rate during frame rendering
    - Converts to Meters/Blocks for physics calculations
    """

    value: int = field(
        metadata={"unit": "pixels", "rendering": True, "description": "Screen coordinate for UI/sprite positioning"}
    )

    def __post_init__(self) -> None:
        """Validate pixel coordinates are reasonable"""
        if not isinstance(self.value, int):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f"Pixels requires int, got {type(self.value)}")

    def __add__(self, other: Pixels) -> Pixels:
        return Pixels(self.value + other.value)

    def __sub__(self, other: Pixels) -> Pixels:
        return Pixels(self.value - other.value)

    def __mul__(self, factor: float) -> Pixels:
        return Pixels(int(self.value * factor))

    def __truediv__(self, divisor: float) -> Pixels:
        return Pixels(int(self.value / divisor))

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pixels):
            return NotImplemented
        return self.value == other.value  # Integer comparison - no tolerance needed

    @override
    def __repr__(self) -> str:
        return f"Pixels({self.value})"

    @property
    def in_meters(self) -> Meters:
        meters_per_pixel: float = 1.0 / PIXELS_PER_METER
        return Meters(self.value * meters_per_pixel)

    @property
    def in_blocks(self) -> Blocks:
        pixels_per_block: float = PIXELS_PER_METER * METERS_PER_BLOCK
        blocks_per_pixel: float = 1.0 / pixels_per_block
        return Blocks(self.value * blocks_per_pixel)

    def __int__(self) -> int:
        return self.value

    def __float__(self) -> float:
        return float(self.value)

    def __abs__(self) -> Pixels:
        """Return absolute value while preserving type"""
        return Pixels(abs(self.value))


@dataclass(frozen=True, slots=True, order=True)
class Blocks:
    """
    Building grid coordinate system.

    Design notes:
    - Logical game coordinate (not physical measurement)
    - order=True: Auto-generates __lt__, __le__, __gt__, __ge__
    - Floor numbers are discrete (int), positions are continuous (float)
    - Supports fractional values during elevator movement
    """

    value: float = field(
        metadata={"unit": "blocks", "grid_based": True, "description": "Vertical position in building floor system"}
    )

    def __post_init__(self) -> None:
        """Validate finite value for simulation safety"""
        # Coerce to float to ensure consistent internal type (even if initialized with int)
        object.__setattr__(self, "value", float(self.value))
        if not math.isfinite(self.value):
            raise ValueError(f"Blocks value must be finite, got {self.value}")

    def __add__(self, other: Blocks) -> Blocks:
        return Blocks(self.value + other.value)

    def __sub__(self, other: Blocks) -> Blocks:
        return Blocks(self.value - other.value)

    def __mul__(self, factor: float) -> Blocks:
        return Blocks(self.value * factor)

    def __truediv__(self, divisor: float) -> Blocks:
        return Blocks(self.value / divisor)

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Blocks):
            return NotImplemented
        return abs(self.value - other.value) < BLOCK_FLOAT_TOLERANCE

    @override
    def __repr__(self) -> str:
        return f"Blocks({self.value})"

    @property
    def in_meters(self) -> Meters:
        return Meters(self.value * METERS_PER_BLOCK)

    @property
    def in_pixels(self) -> Pixels:
        pixels_per_block: float = PIXELS_PER_METER * METERS_PER_BLOCK
        return Pixels(int(self.value * pixels_per_block))

    def __int__(self) -> int:
        return int(self.value)

    def __float__(self) -> float:
        return float(self.value)

    def __abs__(self) -> Blocks:
        """Return absolute value while preserving type"""
        return Blocks(abs(self.value))


def rect_from_pixels(x: Pixels, y: Pixels, width: Pixels, height: Pixels) -> tuple[int, int, int, int]:
    """Convert Pixels to pygame rect tuple (int, int, int, int)"""
    return (int(x), int(y), int(width), int(height))


@dataclass(frozen=True, slots=True, order=True)
class Time:
    value: float = field(metadata={"unit": "seconds", "description": "Time duration in seconds"})

    def __post_init__(self) -> None:
        """Validate finite value for simulation safety"""
        # Coerce to float to ensure consistent internal type (even if initialized with int)
        object.__setattr__(self, "value", float(self.value))
        if not math.isfinite(self.value):
            raise ValueError(f"Time value must be finite, got {self.value}")

    def __add__(self, other: Time) -> Time:
        return Time(self.value + other.value)

    def __sub__(self, other: Time) -> Time:
        return Time(self.value - other.value)

    def __mul__(self, factor: float) -> Time:
        return Time(self.value * factor)

    @overload
    def __truediv__(self, divisor: float) -> Time: ...

    @overload
    def __truediv__(self, divisor: Time) -> float: ...

    def __truediv__(self, divisor: float | Time) -> Time | float:
        """
        Time / scalar = Time (scaling)
        Time / Time = float (dimensionless ratio)
        """
        if isinstance(divisor, Time):
            return self.value / divisor.value  # Returns dimensionless float
        return Time(self.value / divisor)  # Returns scaled Time

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Time):
            return NotImplemented
        return abs(self.value - other.value) < TIME_FLOAT_TOLERANCE  # Small tolerance for time comparison

    @override
    def __repr__(self) -> str:
        return f"Time({self.value})"

    def __int__(self) -> int:
        return int(self.value)

    def __float__(self) -> float:
        return float(self.value)

    def __abs__(self) -> Time:
        """Return absolute value while preserving type"""
        return Time(abs(self.value))

    @property
    def in_milliseconds(self) -> int:
        """Convert time to integer milliseconds"""
        return int(self.value * 1000)

    @property
    def in_seconds(self) -> float:
        """Return time in seconds as float"""
        return self.value

    @property
    def in_minutes(self) -> float:
        """Return time in minutes as float"""
        return self.value / 60.0

    @property
    def in_hours(self) -> float:
        """Return time in hours as float"""
        return self.value / 3600.0

    @property
    def in_days(self) -> float:
        """Return time in days as float"""
        return self.value / 86400.0  # 86400 seconds in a day


@dataclass(frozen=True, slots=True, order=True)
class Velocity:
    """
    Velocity measurement in meters per second.

    Design notes:
    - Derived unit: meters/second
    - Used for person walking speed, elevator speed
    - Can be multiplied by Time to get Meters
    - Can be divided into Meters to get Time
    """

    value: float = field(
        metadata={"unit": "meters_per_second", "derived": True, "description": "Speed of movement (m/s)"}
    )

    def __post_init__(self) -> None:
        # Coerce to float to ensure consistent internal type (even if initialized with int)
        object.__setattr__(self, "value", float(self.value))
        if not math.isfinite(self.value):
            raise ValueError(f"Velocity value must be finite, got {self.value}")

    def __add__(self, other: Velocity) -> Velocity:
        return Velocity(self.value + other.value)

    def __sub__(self, other: Velocity) -> Velocity:
        return Velocity(self.value - other.value)

    @overload
    def __mul__(self, time: Time) -> Meters: ...

    @overload
    def __mul__(self, time: float) -> Velocity: ...

    def __mul__(self, time: Time | float) -> Meters | Velocity:
        """
        Velocity × Time = Distance (dimensional analysis)
        Velocity × scalar = Velocity (scaling)
        """
        if isinstance(time, Time):
            return Meters(self.value * time.value)
        return Velocity(self.value * time)

    @overload
    def __rmul__(self, time: Time) -> Meters: ...

    @overload
    def __rmul__(self, time: float) -> Velocity: ...

    def __rmul__(self, time: Time | float) -> Meters | Velocity:
        """Support reversed multiplication: 2.0 * velocity"""
        return self.__mul__(time)

    def __truediv__(self, divisor: float) -> Velocity:
        """Scale velocity"""
        return Velocity(self.value / divisor)

    def __abs__(self) -> Velocity:
        return Velocity(abs(self.value))

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Velocity):
            return NotImplemented
        return abs(self.value - other.value) < METRIC_FLOAT_TOLERANCE

    @override
    def __repr__(self) -> str:
        return f"Velocity({self.value} m/s)"

    def __float__(self) -> float:
        return float(self.value)
