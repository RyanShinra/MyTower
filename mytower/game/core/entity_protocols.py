"""
Protocol definitions for game entities.

Design notes:
- Protocols define interfaces without importing implementations
- Breaks import cycles between config and entities
- TYPE_CHECKING imports for type hints only
"""
from typing import Protocol
from mytower.game.core.types import RGB
from mytower.game.core.units import Meters, Time, Velocity


# pylint: disable=invalid-name
class ElevatorConfigProtocol(Protocol):
    """Config requirements for Elevator class"""

    @property
    def MAX_SPEED(self) -> Velocity: ...

    @property
    def MAX_CAPACITY(self) -> int: ...

    @property
    def PASSENGER_LOADING_TIME(self) -> Time: ...

    @property
    def IDLE_LOG_TIMEOUT(self) -> Time: ...

    @property
    def MOVING_LOG_TIMEOUT(self) -> Time: ...

    @property
    def IDLE_WAIT_TIMEOUT(self) -> Time: ...


class ElevatorCosmeticsProtocol(Protocol):
    """Visual appearance settings for Elevator class"""

    @property
    def SHAFT_COLOR(self) -> RGB: ...

    @property
    def SHAFT_OVERHEAD_COLOR(self) -> RGB: ...

    @property
    def CLOSED_COLOR(self) -> RGB: ...

    @property
    def OPEN_COLOR(self) -> RGB: ...

    @property
    def SHAFT_OVERHEAD_HEIGHT(self) -> Meters: ...
    
    @property
    def ELEVATOR_WIDTH(self) -> Meters: ...
    
    @property
    def ELEVATOR_HEIGHT(self) -> Meters: ...


class PersonConfigProtocol(Protocol):
    """Config requirements for Person class"""

    @property
    def MAX_SPEED(self) -> Velocity: ...

    @property
    def MAX_WAIT_TIME(self) -> Time: ...

    @property
    def IDLE_TIMEOUT(self) -> Time: ...

    @property
    def RADIUS(self) -> Meters: ...


class PersonCosmeticsProtocol(Protocol):
    """Visual appearance settings for Person class"""

    @property
    def ANGRY_MAX_RED(self) -> int: ...

    @property
    def ANGRY_MIN_GREEN(self) -> int: ...

    @property
    def ANGRY_MIN_BLUE(self) -> int: ...

    @property
    def INITIAL_MAX_RED(self) -> int: ...

    @property
    def INITIAL_MAX_GREEN(self) -> int: ...

    @property
    def INITIAL_MAX_BLUE(self) -> int: ...

    @property
    def INITIAL_MIN_RED(self) -> int: ...

    @property
    def INITIAL_MIN_GREEN(self) -> int: ...

    @property
    def INITIAL_MIN_BLUE(self) -> int: ...
# pylint: enable=invalid-name
