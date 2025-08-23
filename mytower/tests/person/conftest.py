from __future__ import annotations
import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from mytower.game.building import Building
from mytower.game.person import Person
# from mytower.game.types import PersonState, HorizontalDirection

# Add the project root to Python path
project_root: Path = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def mock_building() -> MagicMock:
    building = MagicMock(spec=Building)
    building.num_floors = 10
    building.floor_width = 20
    building.get_elevator_banks_on_floor.return_value = []
    return building

@pytest.fixture
def mock_game_config() -> MagicMock:
    config = MagicMock()
    
    # Person config
    config.person.max_speed = 0.5
    config.person.max_wait_time = 90.0
    config.person.idle_timeout = 5.0
    config.person.radius = 5
    
    # Person cosmetics
    config.person_cosmetics.angry_max_red = 192
    config.person_cosmetics.angry_min_green = 0
    config.person_cosmetics.angry_min_blue = 0
    config.person_cosmetics.initial_max_red = 32
    config.person_cosmetics.initial_max_green = 128
    config.person_cosmetics.initial_max_blue = 128
    config.person_cosmetics.initial_min_red = 0
    config.person_cosmetics.initial_min_green = 0
    config.person_cosmetics.initial_min_blue = 0
    
    return config

@pytest.fixture
def person(mock_logger_provider: MagicMock, mock_building: MagicMock, mock_game_config: MagicMock) -> Person:
    return Person(
        logger_provider=mock_logger_provider,
        building=mock_building,
        current_floor=5,
        current_block=10.0,
        config=mock_game_config
    )
