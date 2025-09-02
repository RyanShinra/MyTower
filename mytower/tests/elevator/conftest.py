# conftest.py
from __future__ import annotations  # Defer type evaluation
import sys
from pathlib import Path
# from typing import Callable #, TYPE_CHECKING
from unittest.mock import MagicMock #, PropertyMock  # , # patch

import pytest

# from mytower.game.logger import LoggerProvider
# from mytower.game.elevator import Elevator, ElevatorCosmeticsProtocol
from mytower.game.elevator import Elevator
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
def mock_elevator_bank() -> MagicMock:
    mock_bank = MagicMock()
    mock_bank.horizontal_block = 5
    return mock_bank


@pytest.fixture
def mock_config() -> MagicMock:
    config = MagicMock()
    config.max_speed = 0.75
    config.max_capacity = 15
    config.passenger_loading_time = 1.0
    config.idle_log_timeout = 0.5
    config.moving_log_timeout = 0.5
    config.idle_wait_timeout = 0.5
    return config

# @pytest.fixture
# def mock_cosmetics_config() -> MagicMock:
#     config = MagicMock(spec=ElevatorCosmeticsProtocol)
#     config.shaft_color = (100, 100, 100)
#     config.shaft_overhead = (24, 24, 24)
#     config.closed_color = (50, 50, 200)
#     config.open_color = (200, 200, 50)
#     return config

# @pytest.fixture
# def mock_person_factory() -> Callable[[int], PersonProtocol]:
#     def _person_gen(destination_floor: int) -> PersonProtocol:
#         person: MagicMock = MagicMock(spec=PersonProtocol)
#         type(person).destination_floor = PropertyMock(return_value=destination_floor)
#         person.board_elevator = MagicMock()
#         person.disembark_elevator = MagicMock()
#         return person
#     return _person_gen


@pytest.fixture
def elevator(
    mock_logger_provider: MagicMock,
    mock_elevator_bank: MagicMock,
    mock_config: MagicMock,
    mock_cosmetics_config: MagicMock,
) -> Elevator:
    return Elevator(
        mock_logger_provider,
        mock_elevator_bank,
        h_cell=5,
        min_floor=1,
        max_floor=10,
        config=mock_config,
        cosmetics_config=mock_cosmetics_config,
    )