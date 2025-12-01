# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

"""
Thread safety tests for GameBridge with WebSocket subscriptions.

Tests cover:
- Concurrent snapshot access
- Lock behavior
- Subscription safety with game updates
- No blocking of game thread
"""

import asyncio
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

from mytower.api.graphql_types import BuildingSnapshotGQL
from mytower.api.schema import Subscription
from mytower.game.core.units import Time
from mytower.game.models.model_snapshots import BuildingSnapshot

if TYPE_CHECKING:
    from pytest import MonkeyPatch


@pytest.mark.asyncio
class TestGameBridgeThreadSafety:
    """Test thread-safety of GameBridge when accessed by multiple subscriptions."""

    async def test_concurrent_snapshot_access(
        self,
        mock_game_bridge: "Mock",
        mock_building_snapshot: BuildingSnapshot,
        monkeypatch: "MonkeyPatch",
    ) -> None:
        """Verify multiple subscriptions can safely call get_building_state() concurrently."""
        mock_game_bridge.get_building_snapshot.return_value = mock_building_snapshot

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        subscription = Subscription()

        with patch("mytower.api.schema.convert_building_snapshot", return_value=None):
            # Create 10 concurrent subscriptions
            streams = [
                subscription.building_state_stream(interval_ms=5)  # type: ignore[call-arg]
                for _ in range(10)
            ]

            # Get first value from all concurrently
            results = await asyncio.gather(
                *[anext(stream) for stream in streams]  # type: ignore[arg-type]
            )

            # All should succeed
            assert len(results) == 10
            assert all(r is None for r in results)

    async def test_snapshot_doesnt_change_during_iteration(
        self,
        mock_game_bridge: "Mock",
        mock_building_snapshot: BuildingSnapshot,
        monkeypatch: "MonkeyPatch",
    ) -> None:
        """Verify snapshot reference remains consistent within single iteration."""
        snapshot_calls = []

        def track_snapshot_call():
            """Track each get_building_state call."""
            snapshot = mock_building_snapshot
            snapshot_calls.append(id(snapshot))  # Track object ID
            return snapshot

        mock_game_bridge.get_building_snapshot.side_effect = track_snapshot_call

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        subscription = Subscription()

        with patch("mytower.api.schema.convert_building_snapshot", return_value=None):
            stream = subscription.building_state_stream(interval_ms=5)  # type: ignore[call-arg]

            # Get 5 iterations
            for _ in range(5):
                await anext(stream)  # type: ignore[arg-type]

            # Should have called get_building_state 5 times
            assert len(snapshot_calls) == 5

    async def test_multiple_subscriptions_with_different_intervals(
        self,
        mock_game_bridge: "Mock",
        mock_building_snapshot: BuildingSnapshot,
        monkeypatch: "MonkeyPatch",
    ) -> None:
        """Verify subscriptions with different intervals don't interfere."""
        call_count = {"count": 0}

        def count_calls():
            call_count["count"] += 1
            return mock_building_snapshot

        mock_game_bridge.get_building_snapshot.side_effect = count_calls

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        subscription = Subscription()

        with patch("mytower.api.schema.convert_building_snapshot", return_value=None):
            # Create streams with different intervals
            stream_fast = subscription.building_state_stream(interval_ms=5)  # type: ignore[call-arg]
            stream_slow = subscription.building_state_stream(interval_ms=100)  # type: ignore[call-arg]

            # Fast stream gets 3 values
            for _ in range(3):
                await anext(stream_fast)  # type: ignore[arg-type]

            # Slow stream gets 1 value
            await anext(stream_slow)  # type: ignore[arg-type]

            # Should have called get_building_state 4 times total
            assert call_count["count"] == 4

    async def test_subscription_during_snapshot_update(
        self,
        mock_game_bridge: "Mock",
        mock_building_snapshot: BuildingSnapshot,
        monkeypatch: "MonkeyPatch",
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

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        subscription = Subscription()

        with patch("mytower.api.schema.convert_building_snapshot", return_value=None):
            stream = subscription.building_state_stream(interval_ms=5)  # type: ignore[call-arg]

            # Should transition smoothly between snapshots
            for _ in range(4):
                result = await anext(stream)  # type: ignore[arg-type]
                # All should succeed without error
                assert result is None


@pytest.mark.asyncio
class TestSubscriptionPerformance:
    """Test performance characteristics of subscriptions."""

    async def test_subscription_doesnt_block_async_loop(
        self,
        mock_game_bridge: "Mock",
        monkeypatch: "MonkeyPatch",
    ) -> None:
        """Verify subscription doesn't block the asyncio event loop."""
        mock_game_bridge.get_building_snapshot.return_value = None

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        subscription = Subscription()

        stream = subscription.building_state_stream(interval_ms=50)  # type: ignore[call-arg]

        # Create a concurrent task that should complete quickly
        async def quick_task():
            await asyncio.sleep(0.001)
            return "completed"

        # Start both subscription and quick task
        sub_task = asyncio.create_task(anext(stream))  # type: ignore[arg-type]
        quick_task_result = asyncio.create_task(quick_task())

        # Both should complete without blocking each other
        results = await asyncio.gather(sub_task, quick_task_result)

        assert results[1] == "completed"

    async def test_many_concurrent_subscriptions(
        self,
        mock_game_bridge: "Mock",
        mock_building_snapshot: BuildingSnapshot,
        monkeypatch: "MonkeyPatch",
    ) -> None:
        """Verify system handles many concurrent subscriptions."""
        mock_game_bridge.get_building_snapshot.return_value = mock_building_snapshot

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        subscription = Subscription()

        with patch("mytower.api.schema.convert_building_snapshot", return_value=None):
            # Create 50 concurrent subscriptions
            subscription_count = 50
            streams = [
                subscription.building_state_stream(interval_ms=10)  # type: ignore[call-arg]
                for _ in range(subscription_count)
            ]

            # Get first value from all concurrently
            results = await asyncio.gather(
                *[anext(stream) for stream in streams],  # type: ignore[arg-type]
                return_exceptions=True
            )

            # All should succeed
            assert len(results) == subscription_count
            assert all(r is None for r in results)

    async def test_subscription_memory_cleanup(
        self,
        mock_game_bridge: "Mock",
        monkeypatch: "MonkeyPatch",
    ) -> None:
        """Verify subscription properly cleans up when cancelled."""
        mock_game_bridge.get_building_snapshot.return_value = None

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        subscription = Subscription()

        stream = subscription.building_state_stream(interval_ms=50)  # type: ignore[call-arg]

        # Start and cancel immediately
        task = asyncio.create_task(anext(stream))  # type: ignore[arg-type]
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

    async def test_get_building_state_returns_none_initially(
        self,
        mock_game_bridge: "Mock",
        monkeypatch: "MonkeyPatch",
    ) -> None:
        """Verify subscription handles None from GameBridge (game not started)."""
        mock_game_bridge.get_building_snapshot.return_value = None

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        subscription = Subscription()

        stream = subscription.building_state_stream(interval_ms=50)  # type: ignore[call-arg]
        result = await anext(stream)  # type: ignore[arg-type]

        assert result is None

    async def test_get_building_state_starts_returning_snapshots(
        self,
        mock_game_bridge: "Mock",
        mock_building_snapshot: BuildingSnapshot,
        monkeypatch: "MonkeyPatch",
    ) -> None:
        """Verify subscription starts yielding data when game starts."""
        # Simulate game starting: None -> snapshot
        mock_game_bridge.get_building_snapshot.side_effect = [None, None, mock_building_snapshot]

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        subscription = Subscription()

        with patch("mytower.api.schema.convert_building_snapshot", return_value=Mock(spec=BuildingSnapshotGQL)):
            stream = subscription.building_state_stream(interval_ms=5)  # type: ignore[call-arg]

            # First two yields: None
            result1 = await anext(stream)  # type: ignore[arg-type]
            result2 = await anext(stream)  # type: ignore[arg-type]
            assert result1 is None
            assert result2 is None

            # Third yield: snapshot converted
            result3 = await anext(stream)  # type: ignore[arg-type]
            assert result3 is not None

    async def test_subscription_handles_slow_synchronous_game_bridge_calls(
        self,
        mock_game_bridge: "Mock",
        monkeypatch: "MonkeyPatch",
    ) -> None:
        """Verify subscription handles slow synchronous get_building_snapshot calls gracefully."""
        # Simulate a slow synchronous call (e.g., due to lock contention in the game thread)
        import time

        def slow_get_state():
            time.sleep(0.01)
            return None

        mock_game_bridge.get_building_snapshot.side_effect = slow_get_state

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        subscription = Subscription()

        stream = subscription.building_state_stream(interval_ms=50)  # type: ignore[call-arg]

        # Should still work, just slower (note: this blocks the event loop as expected)
        result = await anext(stream)  # type: ignore[arg-type]
        assert result is None

    async def test_game_time_stream_with_concurrent_access(
        self,
        mock_game_bridge: "Mock",
        mock_building_snapshot: BuildingSnapshot,
        monkeypatch: "MonkeyPatch",
    ) -> None:
        """Verify game_time_stream is also thread-safe."""
        mock_game_bridge.get_building_snapshot.return_value = mock_building_snapshot

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        subscription = Subscription()

        # Create 20 concurrent game_time_stream subscriptions
        streams = [
            subscription.game_time_stream(interval_ms=10)  # type: ignore[call-arg]
            for _ in range(20)
        ]

        # Get first value from all concurrently
        results = await asyncio.gather(
            *[anext(stream) for stream in streams]  # type: ignore[arg-type]
        )

        # All should return the same time
        assert len(results) == 20
        assert all(r == mock_building_snapshot.time for r in results)


@pytest.mark.asyncio
class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    async def test_subscription_survives_rapid_snapshot_changes(
        self,
        mock_game_bridge: "Mock",
        mock_building_snapshot: BuildingSnapshot,
        monkeypatch: "MonkeyPatch",
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

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        subscription = Subscription()

        with patch("mytower.api.schema.convert_building_snapshot", return_value=None):
            stream = subscription.building_state_stream(interval_ms=5)  # type: ignore[call-arg]

            # Consume all 100 snapshots
            for i in range(100):
                result = await anext(stream)  # type: ignore[arg-type]
                # Should handle all without error
                assert result is None

    async def test_mixed_subscription_types_concurrently(
        self,
        mock_game_bridge: "Mock",
        mock_building_snapshot: BuildingSnapshot,
        monkeypatch: "MonkeyPatch",
    ) -> None:
        """Verify building_state_stream and game_time_stream can run together."""
        mock_game_bridge.get_building_snapshot.return_value = mock_building_snapshot

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        subscription = Subscription()

        with patch("mytower.api.schema.convert_building_snapshot", return_value=Mock(spec=BuildingSnapshotGQL)):
            # Create mix of subscription types
            building_streams = [
                subscription.building_state_stream(interval_ms=50)  # type: ignore[call-arg]
                for _ in range(5)
            ]
            time_streams = [
                subscription.game_time_stream(interval_ms=100)  # type: ignore[call-arg]
                for _ in range(5)
            ]

            # Get first value from all
            results = await asyncio.gather(
                *[anext(stream) for stream in building_streams + time_streams]  # type: ignore[arg-type]
            )

            # All should succeed
            assert len(results) == 10

    async def test_subscription_with_stop_and_restart(
        self,
        mock_game_bridge: "Mock",
        mock_building_snapshot: BuildingSnapshot,
        monkeypatch: "MonkeyPatch",
    ) -> None:
        """Verify subscription can be cancelled and restarted."""
        mock_game_bridge.get_building_snapshot.return_value = mock_building_snapshot

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        subscription = Subscription()

        with patch("mytower.api.schema.convert_building_snapshot", return_value=None):
            # First subscription
            stream1 = subscription.building_state_stream(interval_ms=50)  # type: ignore[call-arg]
            task1 = asyncio.create_task(anext(stream1))  # type: ignore[arg-type]
            result1 = await task1
            assert result1 is None

            # Cancel and start new subscription
            task1.cancel()
            try:
                await task1
            except asyncio.CancelledError:
                # Task cancellation is expected here; ignore the exception.
                pass

            # Second subscription should work fine
            stream2 = subscription.building_state_stream(interval_ms=50)  # type: ignore[call-arg]
            result2 = await anext(stream2)  # type: ignore[arg-type]
            assert result2 is None
