# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

"""
Unit tests for GraphQL WebSocket subscriptions.

Tests cover:
- Subscription logic and parameter validation
- Snapshot yielding behavior
- Type conversion correctness
- Iteration patterns

Uses dependency injection instead of monkey patching for better type safety.
"""

from unittest.mock import Mock, patch

import pytest

from mytower.api.graphql_types import BuildingSnapshotGQL
from mytower.api.schema import Subscription
from mytower.game.core.units import Time
from mytower.game.models.model_snapshots import BuildingSnapshot


@pytest.mark.asyncio
class TestBuildingStateStreamSubscription:
    """Test building_state_stream subscription logic."""

    async def test_subscription_yields_snapshot_when_game_running(
        self,
        mock_game_bridge: Mock,
        mock_building_snapshot: BuildingSnapshot,
        mock_building_snapshot_gql: BuildingSnapshotGQL,
    ) -> None:
        """Verify subscription yields converted snapshot when game is running."""
        # Arrange: Set up mock to return snapshot
        mock_game_bridge.get_building_snapshot.return_value = mock_building_snapshot

        with patch("mytower.api.schema.convert_building_snapshot", return_value=mock_building_snapshot_gql):
            # Act: Inject dependency (NO PATCHING!)
            subscription = Subscription(game_bridge=mock_game_bridge)
            stream = subscription.building_state_stream(interval_ms=50)
            result = await anext(stream)

            # Assert
            assert result is mock_building_snapshot_gql
            assert isinstance(result, BuildingSnapshotGQL)

    async def test_subscription_yields_none_when_game_not_running(
        self,
        mock_game_bridge: Mock,
    ) -> None:
        """Verify subscription yields None when get_building_snapshot() returns None."""
        # Arrange: Mock returns None (game not started)
        mock_game_bridge.get_building_snapshot.return_value = None

        # Act: Inject dependency
        subscription = Subscription(game_bridge=mock_game_bridge)
        stream = subscription.building_state_stream(interval_ms=50)
        result = await anext(stream)

        # Assert
        assert result is None

    async def test_subscription_validates_interval_ms_min_bound(self, mock_game_bridge: Mock) -> None:
        """Verify ValueError raised for interval_ms < 5."""
        # Arrange: No dependency needed for validation test
        subscription = Subscription(game_bridge=mock_game_bridge)

        # Act & Assert
        with pytest.raises(ValueError, match="interval_ms must be between 5 and 10000"):
            stream = subscription.building_state_stream(interval_ms=4)
            await anext(stream)

    async def test_subscription_validates_interval_ms_max_bound(self, mock_game_bridge: Mock) -> None:
        """Verify ValueError raised for interval_ms > 10000."""
        subscription = Subscription(game_bridge=mock_game_bridge)

        with pytest.raises(ValueError, match="interval_ms must be between 5 and 10000"):
            stream = subscription.building_state_stream(interval_ms=10001)
            await anext(stream)

    @pytest.mark.parametrize("interval_ms", [5, 50, 100, 1000, 10000])
    async def test_subscription_accepts_valid_interval_ms(
        self,
        mock_game_bridge: Mock,
        interval_ms: int,
    ) -> None:
        """Verify subscription accepts valid interval_ms values."""
        # Arrange
        mock_game_bridge.get_building_snapshot.return_value = None

        # Act: Should not raise
        subscription = Subscription(game_bridge=mock_game_bridge)
        stream = subscription.building_state_stream(interval_ms=interval_ms)
        result = await anext(stream)

        # Assert
        assert result is None

    async def test_subscription_converts_snapshot_correctly(
        self,
        mock_game_bridge: Mock,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify convert_building_snapshot() is called with correct args."""
        # Arrange
        mock_game_bridge.get_building_snapshot.return_value = mock_building_snapshot

        with patch("mytower.api.schema.convert_building_snapshot") as mock_convert:
            mock_convert.return_value = Mock(spec=BuildingSnapshotGQL)

            # Act: Inject dependency
            subscription = Subscription(game_bridge=mock_game_bridge)
            stream = subscription.building_state_stream(interval_ms=50)
            await anext(stream)

            # Assert convert_building_snapshot was called with the snapshot
            mock_convert.assert_called_once_with(mock_building_snapshot)

    async def test_subscription_calls_get_building_state_on_each_iteration(
        self,
        mock_game_bridge: Mock,
    ) -> None:
        """Verify get_building_snapshot() called repeatedly in loop."""
        # Arrange
        mock_game_bridge.get_building_snapshot.return_value = None

        # Act: Inject dependency
        subscription = Subscription(game_bridge=mock_game_bridge)
        stream = subscription.building_state_stream(interval_ms=5)

        # Get 3 iterations
        await anext(stream)
        await anext(stream)
        await anext(stream)

        # Assert: Should have been called 3 times
        assert mock_game_bridge.get_building_snapshot.call_count == 3

    async def test_subscription_handles_changing_snapshot_state(
        self,
        mock_game_bridge: Mock,
        mock_building_snapshot: BuildingSnapshot,
        mock_building_snapshot_gql: BuildingSnapshotGQL,
    ) -> None:
        """Verify subscription picks up changes in snapshot state across iterations."""
        # Arrange: Create two different snapshots
        snapshot1 = mock_building_snapshot
        snapshot2 = BuildingSnapshot(
            time=Time(999.0),
            money=999999,
            floors=[],
            elevators=[],
            elevator_banks=[],
            people=[],
        )

        # Mock will return different snapshots on successive calls
        mock_game_bridge.get_building_snapshot.side_effect = [snapshot1, snapshot2]

        with patch("mytower.api.schema.convert_building_snapshot") as mock_convert:
            mock_convert.side_effect = [mock_building_snapshot_gql, mock_building_snapshot_gql]

            # Act: Inject dependency
            subscription = Subscription(game_bridge=mock_game_bridge)
            stream = subscription.building_state_stream(interval_ms=5)

            # First iteration
            await anext(stream)
            assert mock_game_bridge.get_building_snapshot.call_count == 1
            mock_convert.assert_called_with(snapshot1)

            # Second iteration
            await anext(stream)
            assert mock_game_bridge.get_building_snapshot.call_count == 2
            mock_convert.assert_called_with(snapshot2)


@pytest.mark.asyncio
class TestGameTimeStreamSubscription:
    """Test game_time_stream subscription logic."""

    async def test_subscription_yields_time_when_game_running(
        self,
        mock_game_bridge: Mock,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify subscription yields game time from snapshot."""
        # Arrange
        mock_game_bridge.get_building_snapshot.return_value = mock_building_snapshot

        # Act: Inject dependency
        subscription = Subscription(game_bridge=mock_game_bridge)
        stream = subscription.game_time_stream(interval_ms=100)
        result = await anext(stream)

        # Assert
        assert result == mock_building_snapshot.time
        assert isinstance(result, Time)

    async def test_subscription_yields_zero_when_game_not_running(
        self,
        mock_game_bridge: Mock,
    ) -> None:
        """Verify subscription yields Time(0.0) when no snapshot."""
        # Arrange
        mock_game_bridge.get_building_snapshot.return_value = None

        # Act: Inject dependency
        subscription = Subscription(game_bridge=mock_game_bridge)
        stream = subscription.game_time_stream(interval_ms=100)
        result = await anext(stream)

        # Assert
        assert result == Time(0.0)

    @pytest.mark.parametrize("invalid_interval", [4, 10001, -1, 0])
    async def test_subscription_validates_interval_ms_bounds(
        self, mock_game_bridge: Mock, invalid_interval: int
    ) -> None:
        """Verify parameter validation works for invalid values."""
        subscription = Subscription(game_bridge=mock_game_bridge)

        with pytest.raises(ValueError, match="interval_ms must be between 5 and 10000"):
            stream = subscription.game_time_stream(interval_ms=invalid_interval)
            await anext(stream)

    async def test_subscription_extracts_time_from_snapshot(
        self,
        mock_game_bridge: Mock,
    ) -> None:
        """Verify time extraction from BuildingSnapshot.time."""
        # Arrange: Create mock snapshot with specific time
        mock_snapshot = Mock(spec=BuildingSnapshot)
        mock_snapshot.time = Time(123.456)
        mock_game_bridge.get_building_snapshot.return_value = mock_snapshot

        # Act: Inject dependency
        subscription = Subscription(game_bridge=mock_game_bridge)
        stream = subscription.game_time_stream(interval_ms=100)
        result = await anext(stream)

        # Assert
        assert result == Time(123.456)

    async def test_subscription_tracks_time_progression(
        self,
        mock_game_bridge: Mock,
    ) -> None:
        """Verify subscription tracks time as it progresses."""
        # Arrange: Create snapshots with progressing time
        snapshot1 = Mock(spec=BuildingSnapshot)
        snapshot1.time = Time(10.0)
        snapshot2 = Mock(spec=BuildingSnapshot)
        snapshot2.time = Time(20.0)
        snapshot3 = Mock(spec=BuildingSnapshot)
        snapshot3.time = Time(30.0)

        mock_game_bridge.get_building_snapshot.side_effect = [snapshot1, snapshot2, snapshot3]

        # Act: Inject dependency
        subscription = Subscription(game_bridge=mock_game_bridge)
        stream = subscription.game_time_stream(interval_ms=5)

        result1 = await anext(stream)
        result2 = await anext(stream)
        result3 = await anext(stream)

        # Assert
        assert result1 == Time(10.0)
        assert result2 == Time(20.0)
        assert result3 == Time(30.0)

    @pytest.mark.parametrize("interval_ms", [5, 100, 1000, 10000])
    async def test_subscription_accepts_valid_intervals(
        self,
        mock_game_bridge: Mock,
        interval_ms: int,
    ) -> None:
        """Verify subscription accepts all valid interval values."""
        # Arrange
        mock_game_bridge.get_building_snapshot.return_value = None

        # Act: Inject dependency
        subscription = Subscription(game_bridge=mock_game_bridge)
        stream = subscription.game_time_stream(interval_ms=interval_ms)
        result = await anext(stream)

        # Assert
        assert result == Time(0.0)
