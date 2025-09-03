# /tests/conftest.py

import pytest
from typing import Protocol
from unittest.mock import MagicMock, PropertyMock
from mytower.game.person import PersonProtocol, Person
from mytower.game.elevator import Elevator, ElevatorCosmeticsProtocol
from mytower.game.elevator_bank import ElevatorBank
from mytower.game.logger import LoggerProvider
from mytower.game.building import Building
from mytower.game.types import ElevatorState, VerticalDirection


class PersonFactory(Protocol):
    def __call__(self, cur_floor_num: int, dest_floor_num: int) -> PersonProtocol: ...


@pytest.fixture
def mock_person_factory() -> PersonFactory:
    def _person_gen(cur_floor_num: int, dest_floor_num: int) -> PersonProtocol:
        person: MagicMock = MagicMock(spec=PersonProtocol)
        type(person).current_floor_num = PropertyMock(return_value=cur_floor_num)
        type(person).destination_floor_num = PropertyMock(return_value=dest_floor_num)
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


@pytest.fixture
def mock_building_no_floor() -> MagicMock:
    """Standard building mock - For tests where a person does not need to belong to a floor"""
    building = MagicMock(spec=Building)
    building.num_floors = 10
    building.floor_width = 20
    building.get_elevator_banks_on_floor.return_value = []
    building.get_floor_by_number.return_value = None
    return building


@pytest.fixture
def mock_building_with_floor() -> MagicMock:
    """Building mock that returns a floor (for tests where person should be on a floor)"""
    building = MagicMock(spec=Building)
    building.num_floors = 10
    building.floor_width = 20
    building.get_elevator_banks_on_floor.return_value = []
    mock_floor = MagicMock()
    building.get_floor_by_number.return_value = mock_floor
    return building


@pytest.fixture
def mock_game_config() -> MagicMock:
    """Standard game configuration for tests with real integer values"""
    config = MagicMock()
    
    # Person config - use real values, not MagicMock
    config.person.max_speed = 0.5
    config.person.max_wait_time = 90.0
    config.person.idle_timeout = 5.0
    config.person.radius = 5
    
    # Person cosmetics - IMPORTANT: Use real integers for random.randint()
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
def person_without_floor(mock_logger_provider: MagicMock, mock_building_no_floor: MagicMock, mock_game_config: MagicMock) -> Person:
    """Standard person fixture - created with no current floor by default"""
    return Person(
        logger_provider=mock_logger_provider,
        building=mock_building_no_floor,
        current_floor_num=5,
        current_block_float=10.0,
        config=mock_game_config
    )


@pytest.fixture 
def person_with_floor(mock_logger_provider: MagicMock, mock_building_with_floor: MagicMock, mock_game_config: MagicMock) -> Person:
    """Person fixture that starts on a floor"""
    return Person(
        logger_provider=mock_logger_provider,
        building=mock_building_with_floor,
        current_floor_num=5,
        current_block_float=10.0,
        config=mock_game_config
    )


# Elevator-specific fixtures
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


@pytest.fixture
def mock_elevator(mock_logger_provider: MagicMock) -> MagicMock:
    elevator = MagicMock(spec=Elevator)
    elevator.state = ElevatorState.IDLE
    elevator.current_floor_int = 5
    elevator.idle_time = 0.0
    elevator.nominal_direction = VerticalDirection.STATIONARY
    elevator.idle_wait_timeout = 0.5
    elevator.get_passenger_destinations_in_direction.return_value = []
    return elevator


@pytest.fixture
def elevator_bank(
    mock_building_no_floor: MagicMock, 
    mock_logger_provider: MagicMock, 
    mock_cosmetics_config: MagicMock
) -> ElevatorBank:
    return ElevatorBank(
        building=mock_building_no_floor,
        logger_provider=mock_logger_provider,
        cosmetics_config=mock_cosmetics_config,
        h_cell=5,
        max_floor=10,
        min_floor=1,
    )


@pytest.fixture
def elevator(
    mock_logger_provider: MagicMock, 
    mock_elevator_bank: MagicMock, 
    mock_config: MagicMock, 
    mock_cosmetics_config: MagicMock
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