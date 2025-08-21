# /tests/conftest.py

import pytest
# from typing import Callable, Protocol
from typing import Protocol
from unittest.mock import MagicMock, PropertyMock
from mytower.game.person import PersonProtocol
from mytower.game.elevator import ElevatorCosmeticsProtocol
from mytower.game.logger import LoggerProvider

class PersonFactory(Protocol):
    def __call__(self, cur_floor: int, dest_floor: int) -> PersonProtocol: ...
    
@pytest.fixture
# def mock_person_factory() -> Callable[[int, int], PersonProtocol]:
def mock_person_factory() -> PersonFactory:
    def _person_gen(cur_floor: int, dest_floor: int) -> PersonProtocol:
        person: MagicMock = MagicMock(spec=PersonProtocol)
        type(person).current_floor = PropertyMock(return_value=cur_floor)
        type(person).destination_floor = PropertyMock(return_value=dest_floor)
        person.board_elevator = MagicMock()
        person.disembark_elevator = MagicMock()
        return person
    return _person_gen

@pytest.fixture
def mock_cosmetics_config() -> MagicMock:
    config = MagicMock(spec=ElevatorCosmeticsProtocol)
    config.shaft_color = (100, 100, 100)
    config.shaft_overhead = (24, 24, 24)
    config.closed_color = (50, 50, 200)
    config.open_color = (200, 200, 50)
    return config

@pytest.fixture
def mock_logger_provider() -> MagicMock:
    provider = MagicMock(spec=LoggerProvider)
    mock_logger = MagicMock()
    provider.get_logger.return_value = mock_logger
    return provider