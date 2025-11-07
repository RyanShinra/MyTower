"""
Unit tests for GraphQL WebSocket subscriptions.

Tests cover:
- Subscription logic and parameter validation
- Snapshot yielding behavior
- Type conversion correctness
- Iteration patterns
"""

from unittest.mock import MagicMock, patch

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
        mock_building_snapshot: BuildingSnapshot,
        mock_building_snapshot_gql: BuildingSnapshotGQL,
    ) -> None:
        """Verify subscription yields converted snapshot when game is running."""
        # Arrange
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=mock_building_snapshot):
            with patch(
                "mytower.api.schema.convert_building_snapshot",
                return_value=mock_building_snapshot_gql,
            ):
                # Act: Get first yielded value
                stream = subscription.building_state_stream(interval_ms=50)
                result = await anext(stream)

                # Assert
                assert result is mock_building_snapshot_gql
                assert isinstance(result, BuildingSnapshotGQL)

    async def test_subscription_yields_none_when_game_not_running(self) -> None:
        """Verify subscription yields None when get_building_state() returns None."""
        # Arrange
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
            # Act
            stream = subscription.building_state_stream(interval_ms=50)
            result = await anext(stream)

            # Assert
            assert result is None

    async def test_subscription_validates_interval_ms_min_bound(self) -> None:
        """Verify ValueError raised for interval_ms < 5."""
        # Arrange
        subscription = Subscription()

        # Act & Assert
        with pytest.raises(ValueError, match="interval_ms must be between 5 and 10000"):
            stream = subscription.building_state_stream(interval_ms=4)
            await anext(stream)  # Force execution of generator

    async def test_subscription_validates_interval_ms_max_bound(self) -> None:
        """Verify ValueError raised for interval_ms > 10000."""
        subscription = Subscription()

        with pytest.raises(ValueError, match="interval_ms must be between 5 and 10000"):
            stream = subscription.building_state_stream(interval_ms=10001)
            await anext(stream)

    @pytest.mark.parametrize("interval_ms", [5, 50, 100, 1000, 10000])
    async def test_subscription_accepts_valid_interval_ms(self, interval_ms: int) -> None:
        """Verify subscription accepts valid interval_ms values."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
            # Should not raise
            stream = subscription.building_state_stream(interval_ms=interval_ms)
            result = await anext(stream)
            assert result is None  # None because no game running

    async def test_subscription_converts_snapshot_correctly(
        self,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify convert_building_snapshot() is called with correct args."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=mock_building_snapshot):
            with patch("mytower.api.schema.convert_building_snapshot") as mock_convert:
                mock_convert.return_value = MagicMock(spec=BuildingSnapshotGQL)

                stream = subscription.building_state_stream(interval_ms=50)
                await anext(stream)

                # Assert convert_building_snapshot was called with the snapshot
                mock_convert.assert_called_once_with(mock_building_snapshot)

    async def test_subscription_calls_get_building_state_on_each_iteration(self) -> None:
        """Verify get_building_state() called repeatedly in loop."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None) as mock_get_state:
            stream = subscription.building_state_stream(interval_ms=5)  # Fast interval

            # Get 3 iterations
            await anext(stream)
            await anext(stream)
            await anext(stream)

            # Should have been called 3 times
            assert mock_get_state.call_count == 3

    async def test_subscription_handles_changing_snapshot_state(
        self,
        mock_building_snapshot: BuildingSnapshot,
        mock_building_snapshot_gql: BuildingSnapshotGQL,
    ) -> None:
        """Verify subscription picks up changes in snapshot state across iterations."""
        subscription = Subscription()

        # Create two different snapshots
        snapshot1 = mock_building_snapshot
        snapshot2 = BuildingSnapshot(
            time=Time(999.0),  # Different time
            money=999999,
            floors=[],
            elevators=[],
            elevator_banks=[],
            people=[],
        )

        with patch("mytower.api.schema.get_building_state") as mock_get_state:
            # First call returns snapshot1, second returns snapshot2
            mock_get_state.side_effect = [snapshot1, snapshot2]

            with patch("mytower.api.schema.convert_building_snapshot") as mock_convert:
                mock_convert.side_effect = [mock_building_snapshot_gql, mock_building_snapshot_gql]

                stream = subscription.building_state_stream(interval_ms=5)

                # First iteration
                await anext(stream)
                assert mock_get_state.call_count == 1
                mock_convert.assert_called_with(snapshot1)

                # Second iteration
                await anext(stream)
                assert mock_get_state.call_count == 2
                mock_convert.assert_called_with(snapshot2)


@pytest.mark.asyncio
class TestGameTimeStreamSubscription:
    """Test game_time_stream subscription logic."""

    async def test_subscription_yields_time_when_game_running(
        self,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify subscription yields game time from snapshot."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=mock_building_snapshot):
            stream = subscription.game_time_stream(interval_ms=100)
            result = await anext(stream)

            assert result == mock_building_snapshot.time
            assert isinstance(result, Time)

    async def test_subscription_yields_zero_when_game_not_running(self) -> None:
        """Verify subscription yields Time(0.0) when no snapshot."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
            stream = subscription.game_time_stream(interval_ms=100)
            result = await anext(stream)

            assert result == Time(0.0)

    @pytest.mark.parametrize("invalid_interval", [4, 10001, -1, 0])
    async def test_subscription_validates_interval_ms_bounds(self, invalid_interval: int) -> None:
        """Verify parameter validation works for invalid values."""
        subscription = Subscription()

        with pytest.raises(ValueError, match="interval_ms must be between 5 and 10000"):
            stream = subscription.game_time_stream(interval_ms=invalid_interval)
            await anext(stream)

    async def test_subscription_extracts_time_from_snapshot(self) -> None:
        """Verify time extraction from BuildingSnapshot.time."""
        subscription = Subscription()

        # Create mock snapshot with specific time
        mock_snapshot = MagicMock(spec=BuildingSnapshot)
        mock_snapshot.time = Time(123.456)

        with patch("mytower.api.schema.get_building_state", return_value=mock_snapshot):
            stream = subscription.game_time_stream(interval_ms=100)
            result = await anext(stream)

            assert result == Time(123.456)

    async def test_subscription_tracks_time_progression(self) -> None:
        """Verify subscription tracks time as it progresses."""
        subscription = Subscription()

        # Create snapshots with progressing time
        snapshot1 = MagicMock(spec=BuildingSnapshot)
        snapshot1.time = Time(10.0)
        snapshot2 = MagicMock(spec=BuildingSnapshot)
        snapshot2.time = Time(20.0)
        snapshot3 = MagicMock(spec=BuildingSnapshot)
        snapshot3.time = Time(30.0)

        with patch("mytower.api.schema.get_building_state") as mock_get_state:
            mock_get_state.side_effect = [snapshot1, snapshot2, snapshot3]

            stream = subscription.game_time_stream(interval_ms=5)

            result1 = await anext(stream)
            result2 = await anext(stream)
            result3 = await anext(stream)

            assert result1 == Time(10.0)
            assert result2 == Time(20.0)
            assert result3 == Time(30.0)

    @pytest.mark.parametrize("interval_ms", [5, 100, 1000, 10000])
    async def test_subscription_accepts_valid_intervals(self, interval_ms: int) -> None:
        """Verify subscription accepts all valid interval values."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
            stream = subscription.game_time_stream(interval_ms=interval_ms)
            result = await anext(stream)
            assert result == Time(0.0)
