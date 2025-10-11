from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, override, Final

from mytower.game.core.constants import BLOCK_FLOAT_TOLERANCE



PIXELS_PER_METER: Final[int] = 20  # 20 pixels = 1 meter
METERS_PER_BLOCK: Final[float] = 3.2  # 1 block = 3.2 meters

if TYPE_CHECKING:
    pass

@dataclass(frozen=True)
class Meters:
    value: float

    def __add__(self, other: Meters) -> Meters:
        return Meters(self.value + other.value)

    def __sub__(self, other: Meters) -> Meters:
        return Meters(self.value - other.value)

    def __mul__(self, factor: float) -> Meters:
        return Meters(self.value * factor)

    def __truediv__(self, divisor: float) -> Meters:
        return Meters(self.value / divisor)

    def __lt__(self, other: Meters) -> bool:
        return self.value < other.value

    def __le__(self, other: Meters) -> bool:
        return self.value <= other.value

    def __gt__(self, other: Meters) -> bool:
        return self.value > other.value

    def __ge__(self, other: Meters) -> bool:
        return self.value >= other.value

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Meters):
            return NotImplemented
        return abs(self.value - other.value) < BLOCK_FLOAT_TOLERANCE

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


@dataclass(frozen=True)
class Pixels:
    value: int

    def __add__(self, other: Pixels) -> Pixels:
        return Pixels(self.value + other.value)

    def __sub__(self, other: Pixels) -> Pixels:
        return Pixels(self.value - other.value)

    def __mul__(self, factor: float) -> Pixels:
        return Pixels(int(self.value * factor))

    def __truediv__(self, divisor: float) -> Pixels:
        return Pixels(int(self.value / divisor))

    def __lt__(self, other: Pixels) -> bool:
        return self.value < other.value

    def __le__(self, other: Pixels) -> bool:
        return self.value <= other.value

    def __gt__(self, other: Pixels) -> bool:
        return self.value > other.value

    def __ge__(self, other: Pixels) -> bool:
        return self.value >= other.value

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


@dataclass(frozen=True)
class Blocks:
    value: float

    def __add__(self, other: Blocks) -> Blocks:
        return Blocks(self.value + other.value)

    def __sub__(self, other: Blocks) -> Blocks:
        return Blocks(self.value - other.value)

    def __mul__(self, factor: float) -> Blocks:
        return Blocks(self.value * factor)
    
    def __truediv__(self, divisor: float) -> Blocks:
        return Blocks(self.value / divisor)

    def __lt__(self, other: Blocks) -> bool:
        return self.value < other.value

    def __le__(self, other: Blocks) -> bool:
        return self.value <= other.value

    def __gt__(self, other: Blocks) -> bool:
        return self.value > other.value

    def __ge__(self, other: Blocks) -> bool:
        return self.value >= other.value

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
