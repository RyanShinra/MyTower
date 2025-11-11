"""
Validation constants for GraphQL API input types.

These constants define the acceptable ranges and formats for mutation inputs
to prevent invalid data, DoS attacks, and other security issues.
"""

from typing import Final
import re

# Floor number validation
MIN_FLOOR_NUMBER: Final[int] = 1
MAX_FLOOR_NUMBER: Final[int] = 100

# Position validation (in blocks)
MIN_POSITION_BLOCKS: Final[int] = 0
MAX_POSITION_BLOCKS: Final[int] = 100

# Elevator bank ID validation
MAX_ELEVATOR_BANK_ID_LENGTH: Final[int] = 100
ELEVATOR_BANK_ID_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[a-zA-Z0-9_-]+$")
