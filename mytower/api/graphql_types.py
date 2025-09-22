
from enum import Enum
from typing import List
import strawberry



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
    current_block_float: float
    destination_floor_num: int
    destination_block_num: int
    state: PersonStateGQL
    waiting_time: float
    mad_fraction: float
    draw_color: tuple[int, int, int]
    draw_color_red: int
    draw_color_green: int
    draw_color_blue: int

@strawberry.type
class ElevatorSnapshotGQL:
    id: str
    current_floor: float
    current_block: float
    destination_floor: int
    state: ElevatorStateGQL
    nominal_direction: VerticalDirectionGQL
    door_open: bool
    passenger_count: int
    available_capacity: int
    max_capacity: int

@strawberry.type
class ElevatorBankSnapshotGQL:
    horizontal_block: int
    min_floor: int
    max_floor: int

@strawberry.type
class FloorSnapshotGQL:
    floor_type: FloorTypeGQL
    floor_number: int  # NOTE: We'll need to think about what this means with multiple height floors
    floor_height_blocks: int  
    left_edge_block: int
    floor_width_blocks: int
    person_count: int 
    floor_color: ColorGQL  # RGB color for rendering
    floorboard_color: ColorGQL  # RGB color for rendering

@strawberry.type
class BuildingSnapshotGQL:
    time: float
    money: int
    floors: List[FloorSnapshotGQL]
    elevators: List[ElevatorSnapshotGQL]
    people: List[PersonSnapshotGQL]