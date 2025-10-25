"""
Primitive constants with no dependencies.
These are used by the units system and should have no imports from game modules.
"""
from typing import Final

# Unit conversion factors
PIXELS_PER_METER: Final[int] = 15
METERS_PER_BLOCK: Final[float] = 3.2

# Tolerance for floating-point comparisons in block coordinates
METRIC_FLOAT_TOLERANCE: Final[float] = 0.01  # 1 cm tolerance for metric values
BLOCK_FLOAT_TOLERANCE: Final[float] = METRIC_FLOAT_TOLERANCE / METERS_PER_BLOCK
TIME_FLOAT_TOLERANCE: Final[float] = 0.01  # 10 ms tolerance for time values