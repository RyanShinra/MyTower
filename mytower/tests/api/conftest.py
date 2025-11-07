"""
Shared fixtures for API and subscription tests.

Provides mock objects for:
- BuildingSnapshot (domain model)
- BuildingSnapshotGQL (GraphQL type)
- GameBridge
- GraphQL schema components
"""

from typing import Any
from unittest.mock import Mock

import pytest

from mytower.api.game_bridge_protocol import GameBridgeProtocol
from mytower.api.graphql_types import (
    BuildingSnapshotGQL,
    ElevatorBankSnapshotGQL,
    ElevatorSnapshotGQL,
    FloorSnapshotGQL,
    PersonSnapshotGQL,
)
from mytower.game.core.types import ElevatorState, FloorType, PersonState, VerticalDirection
from mytower.game.core.units import Blocks, Time
from mytower.game.models.model_snapshots import (
    BuildingSnapshot,
    ElevatorBankSnapshot,
    ElevatorSnapshot,
    FloorSnapshot,
    PersonSnapshot,
)


@pytest.fixture
def mock_building_snapshot() -> BuildingSnapshot:
    """
    Create a mock BuildingSnapshot for testing.

    Provides a realistic snapshot with:
    - 1 floor (lobby)
    - 1 elevator
    - 1 person
    - Game time: 123.45s
    - Money: $50,000
    """
    return BuildingSnapshot(
        time=Time(123.45),
        money=50000,
        floors=[
            FloorSnapshot(
                floor_type=FloorType.LOBBY,
                floor_number=1,
                floor_height=Blocks(5.0),
                left_edge_block=Blocks(0.0),
                floor_width=Blocks(20.0),
                person_count=3,
                floor_color=(200, 200, 200),
                floorboard_color=(150, 150, 150),
            )
        ],
        elevators=[
            ElevatorSnapshot(
                id="elevator_123",
                vertical_position=Blocks(10.0),
                horizontal_position=Blocks(5.0),
                destination_floor=5,
                elevator_state=ElevatorState.MOVING,
                nominal_direction=VerticalDirection.UP,
                door_open=False,
                passenger_count=2,
                available_capacity=13,
                max_capacity=15,
            )
        ],
        elevator_banks=[
            ElevatorBankSnapshot(
                id="bank_456",
                h_cell=5,
                min_floor=1,
                max_floor=10,
                elevator_ids=["elevator_123"],
            )
        ],
        people=[
            PersonSnapshot(
                person_id="person_456",
                current_floor_num=1,
                current_vertical_position=Blocks(5.0),
                current_horizontal_position=Blocks(10.0),
                destination_floor_num=5,
                destination_horizontal_position=Blocks(15.0),
                state=PersonState.WAITING_FOR_ELEVATOR,
                waiting_time=Time(10.5),
                mad_fraction=0.3,
                draw_color=(255, 200, 100),
            )
        ],
    )


@pytest.fixture
def mock_building_snapshot_gql() -> BuildingSnapshotGQL:
    """
    Create a mock BuildingSnapshotGQL for testing.

    This is the GraphQL representation returned to clients.
    """
    return BuildingSnapshotGQL(
        time=Time(123.45),
        money=50000,
        floors=[
            FloorSnapshotGQL(
                floor_type=FloorType.LOBBY,
                floor_number=1,
                floor_height=Blocks(5.0),
                left_edge_block=Blocks(0.0),
                floor_width=Blocks(20.0),
                person_count=3,
                floor_color=(200, 200, 200),
                floorboard_color=(150, 150, 150),
            )
        ],
        elevators=[
            ElevatorSnapshotGQL(
                id="elevator_123",
                vertical_position=Blocks(10.0),
                horizontal_position=Blocks(5.0),
                destination_floor=5,
                elevator_state=ElevatorState.MOVING,
                nominal_direction=VerticalDirection.UP,
                door_open=False,
                passenger_count=2,
                available_capacity=13,
                max_capacity=15,
            )
        ],
        elevator_banks=[
            ElevatorBankSnapshotGQL(
                id="bank_456",
                h_cell=5,
                min_floor=1,
                max_floor=10,
                elevator_ids=["elevator_123"],
            )
        ],
        people=[
            PersonSnapshotGQL(
                person_id="person_456",
                current_floor_num=1,
                current_vertical_position=Blocks(5.0),
                current_horizontal_position=Blocks(10.0),
                destination_floor_num=5,
                destination_horizontal_position=Blocks(15.0),
                state=PersonState.WAITING_FOR_ELEVATOR,
                waiting_time=Time(10.5),
                mad_fraction=0.3,
                draw_color=(255, 200, 100),
            )
        ],
    )


@pytest.fixture
def mock_game_bridge() -> Mock:
    """
    Create a type-safe mock GameBridge for testing subscriptions.

    Uses GameBridgeProtocol for maximum flexibility and type safety.
    By default, returns None (game not running).

    Usage in tests:
        subscription = Subscription(game_bridge=mock_game_bridge)
        mock_game_bridge.get_building_snapshot.return_value = snapshot
    """
    bridge = Mock(spec=GameBridgeProtocol)
    bridge.get_building_snapshot.return_value = None
    return bridge


@pytest.fixture
def mock_empty_snapshot() -> BuildingSnapshot:
    """Create an empty BuildingSnapshot (no floors, elevators, or people)."""
    return BuildingSnapshot(
        time=Time(0.0),
        money=10000,
        floors=[],
        elevators=[],
        elevator_banks=[],
        people=[],
    )
