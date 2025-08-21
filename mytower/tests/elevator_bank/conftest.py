# tests/ elevator_bank/ conftest.py

from __future__ import annotations  # Defer type evaluation
import sys
from pathlib import Path
# from typing import Callable #, TYPE_CHECKING
from unittest.mock import MagicMock #, PropertyMock  # , # patch

import pytest

from mytower.game.building import Building
# from mytower.game.elevator import ElevatorCosmeticsProtocol
from mytower.game.elevator_bank import ElevatorBank
# from mytower.game.logger import LoggerProvider
from mytower.game.elevator import Elevator
from mytower.game.types import ElevatorState, VerticalDirection


# from mytower.game.person import PersonProtocol

# if TYPE_CHECKING:
    
# Add the project root to Python path
project_root: Path = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# @pytest.fixture
# def mock_logger_provider() -> MagicMock:
#     provider = MagicMock(spec=LoggerProvider)
#     mock_logger = MagicMock()
#     provider.get_logger.return_value = mock_logger
#     return provider

@pytest.fixture
def mock_building() -> MagicMock:
    building = MagicMock(spec=Building)
    return building    

# @pytest.fixture
# def mock_cosmetics_config() -> MagicMock:
#     config = MagicMock(spec=ElevatorCosmeticsProtocol)
#     config.shaft_color = (100, 100, 100)
#     config.shaft_overhead = (24, 24, 24)
#     config.closed_color = (50, 50, 200)
#     config.open_color = (200, 200, 50)
#     return config

@pytest.fixture
def mock_elevator(mock_logger_provider: MagicMock) -> MagicMock:
    elevator = MagicMock(spec=Elevator)
    
    # Set up reasonable defaults
    elevator.state = ElevatorState.IDLE
    elevator.current_floor_int = 5
    elevator.idle_time = 0.0
    elevator.nominal_direction = VerticalDirection.STATIONARY
    elevator.idle_wait_timeout = 0.5
    
    # Mock method returns
    elevator.get_passenger_destinations_in_direction.return_value = []
    
    return elevator

@pytest.fixture
def elevator_bank(  
        mock_building: MagicMock,
        mock_logger_provider: MagicMock,
        mock_cosmetics_config: MagicMock
) -> ElevatorBank:
    return ElevatorBank(
        building=mock_building,
        logger_provider=mock_logger_provider,
        cosmetics_config=mock_cosmetics_config,
        h_cell=5,
        max_floor=10,
        min_floor=1,
    )