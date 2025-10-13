from __future__ import annotations
from dataclasses import dataclass, field
from typing import override
import math

from mytower.game.core.primitive_constants import BLOCK_FLOAT_TOLERANCE, METRIC_FLOAT_TOLERANCE, PIXELS_PER_METER, METERS_PER_BLOCK


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
        metadata={
            "unit": "meters",
            "si_base": True,
            "description": "Physical measurement for collision detection"
        }
    )
    
    def __post_init__(self) -> None:
        """Validate finite value for physics safety"""
        if not math.isfinite(self.value):
            raise ValueError(f"Meters value must be finite, got {self.value}")
    
    def __add__(self, other: Meters) -> Meters:
        return Meters(self.value + other.value)

    def __sub__(self, other: Meters) -> Meters:
        return Meters(self.value - other.value)

    def __mul__(self, factor: float) -> Meters:
        return Meters(self.value * factor)

    def __truediv__(self, divisor: float) -> Meters:
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
        return self.value


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
        metadata={
            "unit": "pixels",
            "rendering": True,
            "description": "Screen coordinate for UI/sprite positioning"
        }
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
        metadata={
            "unit": "blocks",
            "grid_based": True,
            "description": "Vertical position in building floor system"
        }
    )
    
    def __post_init__(self) -> None:
        """Validate finite value for simulation safety"""
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
        return self.value

def rect_from_pixels(x: Pixels, y: Pixels, width: Pixels, height: Pixels) -> tuple[int, int, int, int]:
    """Convert Pixels to pygame rect tuple (int, int, int, int)"""
    return (int(x), int(y), int(width), int(height))
