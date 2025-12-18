# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

# /tests/conftest.py

from collections.abc import Callable
from typing import Final, Protocol
from unittest.mock import MagicMock, Mock, PropertyMock

import pytest

from mytower.game.core.config import ElevatorCosmeticsProtocol
from mytower.game.core.types import ElevatorState, VerticalDirection
from mytower.game.core.units import Blocks, Meters, Time, Velocity
from mytower.game.entities.elevator import Elevator
from mytower.game.entities.elevator_bank import ElevatorBank

# Import protocols for type hints in production code, not for Mock return types
from mytower.game.entities.entities_protocol import (
    BuildingProtocol,
    ElevatorBankProtocol,
    ElevatorProtocol,
    FloorProtocol,
    PersonProtocol,
)
from mytower.game.entities.person import Person
from mytower.game.utilities.logger import LoggerProvider, MyTowerLogger
from mytower.tests.test_protocols import TestableElevatorBankProtocol, TestableElevatorProtocol, TestablePersonProtocol

# Import new type-safe test utilities
from mytower.tests.test_utilities import StateAssertions, TypedMockFactory


class PersonFactory(Protocol):

    def __call__(self, cur_floor_num: int, dest_floor_num: int) -> Mock: ...  # [OK] Honest return type


@pytest.fixture
def mock_person_factory() -> PersonFactory:


    def _person_gen(cur_floor_num: int, dest_floor_num: int) -> Mock:  # [OK] Returns Mock
        person: Final[MagicMock] = MagicMock(spec=PersonProtocol)
        type(person).current_floor_num = PropertyMock(return_value=cur_floor_num)
        type(person).destination_floor_num = PropertyMock(return_value=dest_floor_num)
        person.board_elevator = MagicMock()
        person.disembark_elevator = MagicMock()
        return person

    return _person_gen


@pytest.fixture
def mock_cosmetics_config() -> MagicMock:
    config = MagicMock(spec=ElevatorCosmeticsProtocol)
    config.SHAFT_COLOR = (100, 100, 100)
    config.SHAFT_OVERHEAD_COLOR = (24, 24, 24)
    config.CLOSED_COLOR = (50, 50, 200)
    config.OPEN_COLOR = (200, 200, 50)
    return config

@pytest.fixture
def mock_logger_provider() -> MagicMock:
    provider = MagicMock(spec=LoggerProvider)
    mock_logger = MagicMock(spec=MyTowerLogger)
    provider.get_logger.return_value = mock_logger
    return provider


BUILDING_DEFAULT_NUM_FLOORS = 10
BUILDING_DEFAULT_FLOOR_WIDTH = 20.0  # Needs to be float for Person initial_block_float

# New type-safe test utilities fixtures
@pytest.fixture
def typed_mock_factory() -> TypedMockFactory:
    """Fixture providing type-safe mock creation"""
    return TypedMockFactory()

@pytest.fixture
def state_assertions() -> StateAssertions:
    """Fixture providing common state assertion helpers"""
    return StateAssertions()


@pytest.fixture
def building_factory(typed_mock_factory: TypedMockFactory) -> Callable[..., Mock]:  # [OK]
    """Factory for creating building mocks with configurable floor behavior"""

    def _create_building(
        has_floors: bool = True,
        num_floors: int = BUILDING_DEFAULT_NUM_FLOORS,
        floor_width: float = BUILDING_DEFAULT_FLOOR_WIDTH,
    ) -> Mock:  # [OK] Returns Mock
        return typed_mock_factory.create_building_mock(
            num_floors=num_floors, floor_width=floor_width, has_floors=has_floors
        )

    return _create_building


@pytest.fixture
def mock_building_no_floor() -> Mock:  # [OK]
    """Standard building mock - For tests where a person does not need to belong to a floor"""
    building = MagicMock(spec=BuildingProtocol)
    building.num_floors = BUILDING_DEFAULT_NUM_FLOORS
    building.building_width = Blocks(BUILDING_DEFAULT_FLOOR_WIDTH)
    building.get_elevator_banks_on_floor.return_value = []
    building.get_floor_by_number.return_value = None
    return building


@pytest.fixture
def mock_building_with_floor() -> Mock:  # [OK]
    """Building mock that returns a floor (for tests where person should be on a floor)"""
    building = MagicMock(spec=BuildingProtocol)
    building.num_floors = BUILDING_DEFAULT_NUM_FLOORS
    building.building_width = Blocks(BUILDING_DEFAULT_FLOOR_WIDTH)
    building.get_elevator_banks_on_floor.return_value = []
    mock_floor = MagicMock(spec=FloorProtocol)
    building.get_floor_by_number.return_value = mock_floor
    return building


@pytest.fixture
def mock_game_config() -> MagicMock:
    """Standard game configuration for tests with real integer values"""
    from mytower.game.core.config import GameConfig, PersonConfigProtocol, PersonCosmeticsProtocol

    config = MagicMock(spec=GameConfig)

    # Create properly typed sub-mocks for person config
    person_config = MagicMock(spec=PersonConfigProtocol)
    person_config.MAX_SPEED = Velocity(1.35)  # Approx 3 mph
    person_config.MAX_WAIT_TIME = Time(90.0)
    person_config.IDLE_TIMEOUT = Time(5.0)
    person_config.RADIUS = Meters(1.75)
    config.person = person_config

    # Create properly typed sub-mocks for person cosmetics - IMPORTANT: Use real integers for random.randint()
    person_cosmetics = MagicMock(spec=PersonCosmeticsProtocol)
    person_cosmetics.ANGRY_MAX_RED = 192
    person_cosmetics.ANGRY_MIN_GREEN = 0
    person_cosmetics.ANGRY_MIN_BLUE = 0
    person_cosmetics.INITIAL_MAX_RED = 32
    person_cosmetics.INITIAL_MAX_GREEN = 128
    person_cosmetics.INITIAL_MAX_BLUE = 128
    person_cosmetics.INITIAL_MIN_RED = 0
    person_cosmetics.INITIAL_MIN_GREEN = 0
    person_cosmetics.INITIAL_MIN_BLUE = 0
    person_cosmetics.COLOR_PALETTE = (
        (0, 0, 0),  # Black
        (64, 0, 0),  # Dark Red
        (0, 160, 0),  # Green
        (0, 0, 160),  # Blue
        (64, 160, 0),  # Yellow-Green
        (64, 0, 160),  # Purple
        (0, 160, 160),  # Cyan
        (64, 160, 160),  # Light Cyan
        (32, 80, 80),  # Teal
        (16, 40, 120),  # Dark Blue
    )
    config.person_cosmetics = person_cosmetics

    return config

PERSON_DEFAULT_FLOOR: Final[int] = 6
PERSON_DEFAULT_BLOCK: Final[Blocks] = Blocks(11.0)


@pytest.fixture
def person_with_floor(
    mock_logger_provider: MagicMock,
    mock_building_with_floor: Mock,  # [OK] Changed - was BuildingProtocol
    mock_game_config: MagicMock,
) -> TestablePersonProtocol:  # [OK] This is correct - returns real Person
    """Person fixture that starts on a floor"""
    return Person(
        logger_provider=mock_logger_provider,
        building=mock_building_with_floor,
        initial_floor_number=PERSON_DEFAULT_FLOOR,
        initial_horiz_position=PERSON_DEFAULT_BLOCK,
        config=mock_game_config,
    )

# Elevator-specific fixtures
@pytest.fixture
def mock_elevator_bank() -> Mock:  # [OK]
    mock_bank = MagicMock(spec=ElevatorBankProtocol)
    mock_bank.horizontal_position = Blocks(5)
    return mock_bank


@pytest.fixture
def mock_elevator_config() -> MagicMock:
    config = MagicMock()
    config.MAX_SPEED = Velocity(3.5)
    config.MAX_CAPACITY = 15
    config.PASSENGER_LOADING_TIME = Time(1.0)
    config.IDLE_LOG_TIMEOUT = Time(0.5)
    config.MOVING_LOG_TIMEOUT = Time(0.5)
    config.IDLE_WAIT_TIMEOUT = Time(0.5)
    return config


@pytest.fixture
def mock_elevator(mock_logger_provider: MagicMock) -> Mock:  # [OK]
    elevator = MagicMock(spec=ElevatorProtocol)
    elevator.elevator_state = ElevatorState.IDLE
    elevator.current_floor_int = 5
    elevator.idle_time = Time(0.0)
    elevator.nominal_direction = VerticalDirection.STATIONARY
    elevator.idle_wait_timeout = Time(0.5)
    elevator.get_passenger_destinations_in_direction.return_value = []
    return elevator


@pytest.fixture
def elevator_bank(
    mock_building_no_floor: Mock,  # [OK] Changed - was BuildingProtocol
    mock_logger_provider: MagicMock,
    mock_cosmetics_config: MagicMock,
) -> TestableElevatorBankProtocol:  # [OK] This is correct - returns real ElevatorBank
    return ElevatorBank(
        building=mock_building_no_floor,
        logger_provider=mock_logger_provider,
        cosmetics_config=mock_cosmetics_config,
        horizontal_position=Blocks(5),
        max_floor=10,
        min_floor=1,
    )


@pytest.fixture
def elevator(
    mock_logger_provider: MagicMock,
    mock_elevator_bank: Mock,  # [OK] Changed - was ElevatorBankProtocol
    mock_elevator_config: MagicMock,
    mock_cosmetics_config: MagicMock,
) -> TestableElevatorProtocol:  # [OK] This is correct - returns real Elevator
    """Fixture returns type that supports both production and testing interfaces"""
    return Elevator(
        mock_logger_provider,
        mock_elevator_bank,
        min_floor=1,
        max_floor=10,
        config=mock_elevator_config,
        cosmetics_config=mock_cosmetics_config,
    )


# TODO: Fix Person construction with building floor dependencies (#thisIsAProblemForFutureRyan)
# PROBLEM: Real Person objects call building.get_floor_by_number() during __init__
# - person_without_floor needs building mock to return None during construction
# - person_with_floor needs building mock to return mock_floor during construction
# - Current approach requires separate building fixtures pre-configured for each case
# - PersonFactory creates mock persons, but we need real Person objects for integration tests
#
# CURRENT WORKAROUND: Separate fixtures
# - mock_building_no_floor: get_floor_by_number returns None
# - mock_building_with_floor: get_floor_by_number returns mock_floor
# - person_without_floor: uses mock_building_no_floor
# - person_with_floor: uses mock_building_with_floor
#
# BETTER SOLUTION: PersonFactory that handles real Person construction
# def real_person_factory(cur_floor_num, dest_floor_num, has_floor=False):
#     # Create building mock with appropriate floor return value
#     building = MagicMock(spec=Building)
#     building.get_floor_by_number.return_value = mock_floor if has_floor else None
#     # Create real Person with properly mocked building
#     return Person(logger_provider, building, cur_floor_num, current_block_float, config)
#
# IMPACT: High - eliminates fixture duplication, makes test intent clearer
# EFFORT: ~45 minutes to refactor fixtures and update all test files
# DEPENDENCIES: Complete MVC refactor first - this is test infrastructure cleanup
