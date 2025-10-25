from enum import Enum
from typing import List

import strawberry

import mytower.api.unit_scalars  # Ensure custom scalars are registered
from mytower.game.core.units import Blocks  # Use core types directly!
from mytower.game.core.units import Meters, Pixels, Time

mytower.api.unit_scalars  # noqa  # Prevent unused import warning

@strawberry.enum
class FloorTypeGQL(Enum):
    LOBBY = "LOBBY"
    OFFICE = "OFFICE"
    APARTMENT = "APARTMENT"
    HOTEL = "HOTEL"
    RESTAURANT = "RESTAURANT"
    RETAIL = "RETAIL"

@strawberry.enum
class PersonStateGQL(Enum):
    IDLE = "IDLE"
    WALKING = "WALKING"
    WAITING_FOR_ELEVATOR = "WAITING_FOR_ELEVATOR"
    IN_ELEVATOR = "IN_ELEVATOR"

@strawberry.enum
class ElevatorStateGQL(Enum):
    IDLE = "IDLE"
    MOVING = "MOVING"
    ARRIVED = "ARRIVED"
    LOADING = "LOADING"
    UNLOADING = "UNLOADING"
    READY_TO_MOVE = "READY_TO_MOVE"

@strawberry.enum
class VerticalDirectionGQL(Enum):
    DOWN = -1
    STATIONARY = 0
    UP = 1

    def invert(self) -> "VerticalDirectionGQL":  # More compatible type annotation
        if self == VerticalDirectionGQL.UP:
            return VerticalDirectionGQL.DOWN
        elif self == VerticalDirectionGQL.DOWN:
            return VerticalDirectionGQL.UP
        else:
            return VerticalDirectionGQL.STATIONARY

@strawberry.enum
class HorizontalDirectionGQL(Enum):
    LEFT = -1
    STATIONARY = 0
    RIGHT = 1

@strawberry.type
class ColorGQL:
    red: int
    green: int
    blue: int
    alpha: int = 255  # Default to fully opaque

    @classmethod
    def from_tuple(cls, color: tuple[int, ...]) -> "ColorGQL":
        if len(color) == 3:
            r, g, b = color
            a = 255
        elif len(color) == 4:
            r, g, b, a = color
        else:
            raise ValueError("Color tuple must have 3 (RGB) or 4 (RGBA) elements.")
        return cls(red=r, green=g, blue=b, alpha=a)

    def as_rgba_tuple(self) -> tuple[int, int, int, int]:
        return (self.red, self.green, self.blue, self.alpha)

    def as_rgb_tuple(self) -> tuple[int, int, int]:
        return (self.red, self.green, self.blue)

@strawberry.type
class PersonSnapshotGQL:
    person_id: str
    current_floor_num: int
    current_vertical_position: Blocks  # Core type
    current_horizontal_position: Blocks  # Core type
    destination_floor_num: int
    destination_horizontal_position: Blocks  # Core type
    state: PersonStateGQL
    waiting_time: Time  # Core type
    mad_fraction: float
    _draw_color: tuple[int, int, int]

    @strawberry.field
    def draw_color(self) -> ColorGQL:
        return ColorGQL.from_tuple(self._draw_color)

@strawberry.type
class ElevatorSnapshotGQL:
    id: str
    vertical_position: Blocks  # This is now mytower.game.core.units.Blocks
    horizontal_position: Blocks  # Same type, no conversion needed!
    destination_floor: int
    state: ElevatorStateGQL
    nominal_direction: VerticalDirectionGQL
    door_open: bool
    passenger_count: int
    available_capacity: int
    max_capacity: int

    # Optional: Provide multiple unit representations
    @strawberry.field
    def vertical_position_meters(self) -> Meters:
        """Current position in meters for physics calculations"""
        return self.vertical_position.in_meters  # Direct property access, type-safe!

    @strawberry.field
    def vertical_position_pixels(self) -> Pixels:
        """Current position in pixels for rendering hint"""
        return self.vertical_position.in_pixels  # Type checker knows this returns Pixels

@strawberry.type
class ElevatorBankSnapshotGQL:
    id: str
    horizontal_position: Blocks  # Core type
    min_floor: int
    max_floor: int

@strawberry.type
class FloorSnapshotGQL:
    floor_type: FloorTypeGQL
    floor_number: int
    floor_height: Blocks  # Core type
    left_edge_block: Blocks      # Core type
    floor_width: Blocks   # Core type
    person_count: int
    floor_color: ColorGQL
    floorboard_color: ColorGQL

    @strawberry.field
    def floor_height_meters(self) -> Meters:
        """Floor height in real-world units"""
        return self.floor_height.in_meters  # Type-safe conversion

@strawberry.type
class BuildingSnapshotGQL:
    time: Time  # Core type
    money: int
    floors: List[FloorSnapshotGQL]
    elevators: List[ElevatorSnapshotGQL]
    people: List[PersonSnapshotGQL]