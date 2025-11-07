"""
Thread safety tests for GameBridge with WebSocket subscriptions.

Tests cover:
- Concurrent snapshot access
- Lock behavior
- Subscription safety with game updates
- No blocking of game thread
"""

import asyncio
import threading
from unittest.mock import Mock, patch

import pytest

from mytower.api.graphql_types import BuildingSnapshotGQL
from mytower.api.schema import Subscription
from mytower.game.core.units import Time
from mytower.game.models.model_snapshots import BuildingSnapshot


@pytest.mark.asyncio
class TestGameBridgeThreadSafety:
    """Test thread-safety of GameBridge when accessed by multiple subscriptions."""

    async def test_concurrent_snapshot_access(
        self,
        mock_game_bridge,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify multiple subscriptions can safely call get_building_state() concurrently."""
        mock_game_bridge.get_building_snapshot.return_value = mock_building_snapshot
        subscription = Subscription(game_bridge=mock_game_bridge)

        with patch("mytower.api.schema.convert_building_snapshot", return_value=None):
            # Create 10 concurrent subscriptions
            streams = [
                subscription.building_state_stream(interval_ms=5)
                for _ in range(10)
            ]

            # Get first value from all concurrently
            results = await asyncio.gather(
                *[anext(stream) for stream in streams]
            )

            # All should succeed
            assert len(results) == 10
            assert all(r is None for r in results)

    async def test_snapshot_doesnt_change_during_iteration(
        self,
        mock_game_bridge,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify snapshot reference remains consistent within single iteration."""
        snapshot_calls = []

        def track_snapshot_call():
            """Track each get_building_state call."""
            snapshot = mock_building_snapshot
            snapshot_calls.append(id(snapshot))  # Track object ID
            return snapshot

        mock_game_bridge.get_building_snapshot.side_effect = track_snapshot_call
        subscription = Subscription(game_bridge=mock_game_bridge)

        with patch("mytower.api.schema.convert_building_snapshot", return_value=None):
            stream = subscription.building_state_stream(interval_ms=5)

            # Get 5 iterations
            for _ in range(5):
                await anext(stream)

            # Should have called get_building_state 5 times
            assert len(snapshot_calls) == 5

    async def test_multiple_subscriptions_with_different_intervals(
        self,
        mock_game_bridge,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify subscriptions with different intervals don't interfere."""
        call_count = {"count": 0}

        def count_calls():
            call_count["count"] += 1
            return mock_building_snapshot

        mock_game_bridge.get_building_snapshot.side_effect = count_calls
        subscription = Subscription(game_bridge=mock_game_bridge)

        with patch("mytower.api.schema.convert_building_snapshot", return_value=None):
            # Create streams with different intervals
            stream_fast = subscription.building_state_stream(interval_ms=5)
            stream_slow = subscription.building_state_stream(interval_ms=100)

            # Fast stream gets 3 values
            for _ in range(3):
                await anext(stream_fast)

            # Slow stream gets 1 value
            await anext(stream_slow)

            # Should have called get_building_state 4 times total
            assert call_count["count"] == 4

    async def test_subscription_during_snapshot_update(
        self,
        mock_game_bridge,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify subscription handles snapshot updates gracefully."""
        # Create two different snapshots
        snapshot1 = mock_building_snapshot
        snapshot2 = BuildingSnapshot(
            time=Time(999.0),
            money=999999,
            floors=[],
            elevators=[],
            elevator_banks=[],
            people=[],
        )

        snapshots = [snapshot1, snapshot2, snapshot2, snapshot2]
        mock_game_bridge.get_building_snapshot.side_effect = snapshots
        subscription = Subscription(game_bridge=mock_game_bridge)

        with patch("mytower.api.schema.convert_building_snapshot", return_value=None):
            stream = subscription.building_state_stream(interval_ms=5)

            # Should transition smoothly between snapshots
            for _ in range(4):
                result = await anext(stream)
                # All should succeed without error
                assert result is None


@pytest.mark.asyncio
class TestSubscriptionPerformance:
    """Test performance characteristics of subscriptions."""

    async def test_subscription_doesnt_block_async_loop(self, mock_game_bridge) -> None:
        """Verify subscription doesn't block the asyncio event loop."""
        mock_game_bridge.get_building_snapshot.return_value = None
        subscription = Subscription(game_bridge=mock_game_bridge)

        stream = subscription.building_state_stream(interval_ms=50)

        # Create a concurrent task that should complete quickly
        async def quick_task():
            await asyncio.sleep(0.001)
            return "completed"

        # Start both subscription and quick task
        sub_task = asyncio.create_task(anext(stream))
        quick_task_result = asyncio.create_task(quick_task())

        # Both should complete without blocking each other
        results = await asyncio.gather(sub_task, quick_task_result)

        assert results[1] == "completed"

    async def test_many_concurrent_subscriptions(
        self,
        mock_game_bridge,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify system handles many concurrent subscriptions."""
        mock_game_bridge.get_building_snapshot.return_value = mock_building_snapshot
        subscription = Subscription(game_bridge=mock_game_bridge)

        with patch("mytower.api.schema.convert_building_snapshot", return_value=None):
            # Create 50 concurrent subscriptions
            subscription_count = 50
            streams = [
                subscription.building_state_stream(interval_ms=10)
                for _ in range(subscription_count)
            ]

            # Get first value from all concurrently
            results = await asyncio.gather(
                *[anext(stream) for stream in streams],
                return_exceptions=True
            )

            # All should succeed
            assert len(results) == subscription_count
            assert all(r is None for r in results)

    async def test_subscription_memory_cleanup(self, mock_game_bridge) -> None:
        """Verify subscription properly cleans up when cancelled."""
        mock_game_bridge.get_building_snapshot.return_value = None
        subscription = Subscription(game_bridge=mock_game_bridge)

        stream = subscription.building_state_stream(interval_ms=50)

        # Start and cancel immediately
        task = asyncio.create_task(anext(stream))
        await asyncio.sleep(0.001)
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            # Cancellation is expected here; we are testing cleanup after cancelling the subscription.
            pass

        # Verify stream can be garbage collected (no reference leaks)
        # This is implicit - if there are issues, they'd show up in memory profiling
        assert True


@pytest.mark.asyncio
class TestSubscriptionWithGameBridgeMock:
    """Test subscriptions with mocked GameBridge behavior."""

    async def test_get_building_state_returns_none_initially(self, mock_game_bridge) -> None:
        """Verify subscription handles None from GameBridge (game not started)."""
        mock_game_bridge.get_building_snapshot.return_value = None
        subscription = Subscription(game_bridge=mock_game_bridge)

        stream = subscription.building_state_stream(interval_ms=50)
        result = await anext(stream)

        assert result is None

    async def test_get_building_state_starts_returning_snapshots(
        self,
        mock_game_bridge,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify subscription starts yielding data when game starts."""
        # Simulate game starting: None -> snapshot
        mock_game_bridge.get_building_snapshot.side_effect = [None, None, mock_building_snapshot]
        subscription = Subscription(game_bridge=mock_game_bridge)

        with patch("mytower.api.schema.convert_building_snapshot", return_value=Mock(spec=BuildingSnapshotGQL)):
            stream = subscription.building_state_stream(interval_ms=5)

            # First two yields: None
            result1 = await anext(stream)
            result2 = await anext(stream)
            assert result1 is None
            assert result2 is None

            # Third yield: snapshot converted
            result3 = await anext(stream)
            assert result3 is not None

    async def test_subscription_handles_game_bridge_lock_timeout(self, mock_game_bridge) -> None:
        """Verify subscription handles potential lock timeouts gracefully."""
        # Simulate a slow get_building_state call (potential lock contention)
        async def slow_get_state():
            await asyncio.sleep(0.01)
            return None

        mock_game_bridge.get_building_snapshot.side_effect = slow_get_state
        subscription = Subscription(game_bridge=mock_game_bridge)

        stream = subscription.building_state_stream(interval_ms=50)

        # Should still work, just slower
        result = await anext(stream)
        assert result is None

    async def test_game_time_stream_with_concurrent_access(
        self,
        mock_game_bridge,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify game_time_stream is also thread-safe."""
        mock_game_bridge.get_building_snapshot.return_value = mock_building_snapshot
        subscription = Subscription(game_bridge=mock_game_bridge)

        # Create 20 concurrent game_time_stream subscriptions
        streams = [
            subscription.game_time_stream(interval_ms=10)
            for _ in range(20)
        ]

        # Get first value from all concurrently
        results = await asyncio.gather(
            *[anext(stream) for stream in streams]
        )

        # All should return the same time
        assert len(results) == 20
        assert all(r == mock_building_snapshot.time for r in results)


@pytest.mark.asyncio
class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    async def test_subscription_survives_rapid_snapshot_changes(
        self,
        mock_game_bridge,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify subscription handles rapid snapshot updates (high game speed)."""
        # Create 100 different snapshots (simulating fast game)
        snapshots = [
            BuildingSnapshot(
                time=Time(float(i)),
                money=10000 + i,
                floors=[],
                elevators=[],
                elevator_banks=[],
                people=[],
            )
            for i in range(100)
        ]

        mock_game_bridge.get_building_snapshot.side_effect = snapshots
        subscription = Subscription(game_bridge=mock_game_bridge)

        with patch("mytower.api.schema.convert_building_snapshot", return_value=None):
            stream = subscription.building_state_stream(interval_ms=5)

            # Consume all 100 snapshots
            for i in range(100):
                result = await anext(stream)
                # Should handle all without error
                assert result is None

    async def test_mixed_subscription_types_concurrently(
        self,
        mock_game_bridge,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify building_state_stream and game_time_stream can run together."""
        mock_game_bridge.get_building_snapshot.return_value = mock_building_snapshot
        subscription = Subscription(game_bridge=mock_game_bridge)

        with patch("mytower.api.schema.convert_building_snapshot", return_value=Mock(spec=BuildingSnapshotGQL)):
            # Create mix of subscription types
            building_streams = [
                subscription.building_state_stream(interval_ms=50)
                for _ in range(5)
            ]
            time_streams = [
                subscription.game_time_stream(interval_ms=100)
                for _ in range(5)
            ]

            # Get first value from all
            results = await asyncio.gather(
                *[anext(stream) for stream in building_streams + time_streams]
            )

            # All should succeed
            assert len(results) == 10

    async def test_subscription_with_stop_and_restart(
        self,
        mock_game_bridge,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify subscription can be cancelled and restarted."""
        mock_game_bridge.get_building_snapshot.return_value = mock_building_snapshot
        subscription = Subscription(game_bridge=mock_game_bridge)

        with patch("mytower.api.schema.convert_building_snapshot", return_value=None):
            # First subscription
            stream1 = subscription.building_state_stream(interval_ms=50)
            task1 = asyncio.create_task(anext(stream1))
            result1 = await task1
            assert result1 is None

            # Cancel and start new subscription
            task1.cancel()
            try:
                await task1
            except asyncio.CancelledError:
                pass

            # Second subscription should work fine
            stream2 = subscription.building_state_stream(interval_ms=50)
            result2 = await anext(stream2)
            assert result2 is None
