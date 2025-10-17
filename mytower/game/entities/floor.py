# game/floor.py
from __future__ import annotations  # Defer type evaluation


from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Final, override



from mytower.game.core.units import Blocks
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger
from mytower.game.core.types import Color, FloorType

from mytower.game.core.constants import (
    APARTMENT_COLOR,
    APARTMENT_HEIGHT,
    DEFAULT_FLOOR_LEFT_EDGE,
    DEFAULT_FLOOR_WIDTH,
    FLOORBOARD_COLOR,
    HOTEL_COLOR,
    HOTEL_HEIGHT,
    LOBBY_COLOR,
    LOBBY_HEIGHT,
    OFFICE_COLOR,
    OFFICE_HEIGHT,
    RESTAURANT_COLOR,
    RESTAURANT_HEIGHT,
    RETAIL_COLOR,
    RETAIL_HEIGHT,
)

from mytower.game.entities.entities_protocol import FloorProtocol


if TYPE_CHECKING:
    from mytower.game.entities.entities_protocol import PersonProtocol, BuildingProtocol


class Floor(FloorProtocol):
    """
    A floor in the building that can contain various room types
    """
    # TODO: #27 Consider what we will want for basements and European floor numbering schemes
    @dataclass
    class FloorInfo:
        """
        Struct to hold information about a floor's appearance and dimensions.
        """
        color: Color
        height: Blocks

    # Available floor types
    LOBBY_INFO: Final = FloorInfo(LOBBY_COLOR, LOBBY_HEIGHT)
    FLOOR_TYPES: Dict[FloorType, FloorInfo] = {
        FloorType.LOBBY: FloorInfo(LOBBY_COLOR, LOBBY_HEIGHT),
        FloorType.OFFICE: FloorInfo(OFFICE_COLOR, OFFICE_HEIGHT),
        FloorType.APARTMENT: FloorInfo(APARTMENT_COLOR, APARTMENT_HEIGHT),
        FloorType.HOTEL: FloorInfo(HOTEL_COLOR, HOTEL_HEIGHT),
        FloorType.RESTAURANT: FloorInfo(RESTAURANT_COLOR, RESTAURANT_HEIGHT),
        FloorType.RETAIL: FloorInfo(RETAIL_COLOR, RETAIL_HEIGHT),
    }

    def __init__(
        self, 
        logger_provider: LoggerProvider, 
        building: BuildingProtocol, 
        floor_num: int, 
        floor_type: FloorType, 
        floor_left_edge: Blocks = DEFAULT_FLOOR_LEFT_EDGE, 
        floor_width: Blocks = DEFAULT_FLOOR_WIDTH,   
    ) -> None:
        self._logger: MyTowerLogger = logger_provider.get_logger("floor")
        self._building: BuildingProtocol = building
        # Floors are 1 indexed
        self._floor_num: int = floor_num

        self._floor_left_edge: Blocks = floor_left_edge
        self._floor_width: Blocks = floor_width

        self._floor_type: FloorType = floor_type
        self._color: Color = self.FLOOR_TYPES[floor_type].color
        self._floorboard_color: Color = FLOORBOARD_COLOR
        self._height: Blocks = self.FLOOR_TYPES[floor_type].height

        self._people: Dict[str, PersonProtocol] = {}  # People currently on this floor    
        
    # Grid of rooms/spaces on this floor

    @property
    def building(self) -> BuildingProtocol:
        return self._building

    @property
    @override
    def floor_num(self) -> int:
        return self._floor_num

    @property
    @override
    def floor_type(self) -> FloorType:
        return self._floor_type

    @property
    @override
    def floor_width(self) -> Blocks:
        return self._floor_width

    @property
    @override
    def floor_height(self) -> Blocks:
        return self._height

    @property
    @override
    def left_edge(self) -> Blocks:
        return self._floor_left_edge

    @property
    @override
    def number_of_people(self) -> int:
        return len(self._people)

    @property
    @override
    def color(self) -> Color:
        return self._color

    @property
    @override
    def floorboard_color(self) -> Color:
        return self._floorboard_color

    @property
    def people(self) -> Dict[str, PersonProtocol]:
        return dict(self._people)
    
    @override
    def add_person(self, person: PersonProtocol) -> None:
        """Add a person to the floor"""
        self._people[person.person_id] = person
        
    @override
    def remove_person(self, person_id: str) -> PersonProtocol:
        """Remove a person from the floor, returns the person if found, throws if not"""
        # This is fairly reasonable since only a person should be removing themselves from the floor
        # If it throws, then it's a pretty serious problem
        person: PersonProtocol | None = self._people.pop(person_id, None)
        if not person:
            raise KeyError(f"Person not found: {person_id}")
        return person
        
            
    def update(self, dt: float) -> None:
        """Update floor simulation"""
        pass  # To be implemented

