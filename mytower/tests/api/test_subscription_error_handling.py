# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

"""
Error handling and cancellation tests for WebSocket subscriptions.

Tests cover:
- CancelledError handling
- Cleanup on cancellation
- Exception propagation
- Concurrent subscriptions
- Edge cases and error scenarios
"""

import asyncio
import logging
from collections.abc import AsyncGenerator
from unittest.mock import Mock, patch

import pytest

from mytower.api.graphql_types import BuildingSnapshotGQL
from mytower.api.schema import Subscription
from mytower.game.core.units import Time
from mytower.game.models.model_snapshots import BuildingSnapshot


async def _consume_and_signal(stream: AsyncGenerator[object, None], first_item: asyncio.Event) -> None:
    """
    Consume stream indefinitely, setting first_item once an item has arrived.

    It has no sleep of its own, so the only place it can be suspended is inside the generator. A
    consumer suspended in its own sleep leaves the generator sitting at its yield, where a
    cancellation never reaches it; with a 1 ms sleep that is what happened on Windows, whose timers
    tick about every 15.6 ms (#163).

    The stream's item type is object so that both building_state_stream and game_time_stream fit:
    AsyncGenerator is covariant in what it yields, and the items are never looked at.
    """
    async for _ in stream:
        first_item.set()


@pytest.mark.asyncio
class TestSubscriptionErrorHandling:
    """Test error handling and cancellation behavior."""

    async def test_subscription_handles_cancellation(self, mock_game_bridge) -> None:
        """Verify subscription raises CancelledError and cleans up."""
        mock_game_bridge.get_building_snapshot.return_value = None
        subscription = Subscription(game_bridge=mock_game_bridge)

        stream = subscription.building_state_stream(interval_ms=50)

        # Wait for the first item, not for a timer, so the consumer is parked inside the generator
        # when the cancel arrives; test_subscription_cleanup_on_cancellation explains why (#163).
        first_item = asyncio.Event()
        task = asyncio.create_task(_consume_and_signal(stream, first_item))
        await asyncio.wait_for(first_item.wait(), timeout=5.0)

        # Cancel the task
        task.cancel()

        # Should raise CancelledError
        with pytest.raises(asyncio.CancelledError):
            await task

    async def test_subscription_cleanup_on_cancellation(
        self,
        mock_game_bridge,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Verify finally block executes on cancellation."""
        mock_game_bridge.get_building_snapshot.return_value = None
        subscription = Subscription(game_bridge=mock_game_bridge)

        with caplog.at_level(logging.INFO, logger="mytower.api.schema"):
            stream = subscription.building_state_stream(interval_ms=50)

            first_item = asyncio.Event()
            task = asyncio.create_task(_consume_and_signal(stream, first_item))

            # The timeout only stops a broken stream from hanging the suite; the test does not rely on it.
            await asyncio.wait_for(first_item.wait(), timeout=5.0)

            # No extra yield to the loop is needed before cancelling. set() only schedules this test
            # to resume; the consumer keeps running in the same step, goes straight back into anext,
            # and does not give up control until the generator's own asyncio.sleep(interval). So when
            # this line runs, the consumer is parked inside the generator, and the CancelledError is
            # thrown there, where its except and finally can see it.
            task.cancel()

            # The finally block runs while the CancelledError unwinds through the generator, which is
            # before the task finishes, so the log record exists as soon as this await returns.
            with pytest.raises(asyncio.CancelledError):
                await task

            # Verify cleanup message was logged
            assert any(
                "Building State Subscription cleaned up" in record.getMessage() for record in caplog.records
            ), "Cleanup message not logged"

    async def test_subscription_handles_get_building_state_exception(self, mock_game_bridge) -> None:
        """Verify exception from get_building_state() propagates."""
        mock_game_bridge.get_building_snapshot.side_effect = RuntimeError("GameBridge not initialized")
        subscription = Subscription(game_bridge=mock_game_bridge)

        stream = subscription.building_state_stream(interval_ms=50)

        with pytest.raises(RuntimeError, match="GameBridge not initialized"):
            await anext(stream)

    async def test_subscription_handles_convert_snapshot_exception(
        self,
        mock_game_bridge,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify exception from convert_building_snapshot() propagates."""
        mock_game_bridge.get_building_snapshot.return_value = mock_building_snapshot
        subscription = Subscription(game_bridge=mock_game_bridge)

        with patch(
            "mytower.api.schema.convert_building_snapshot",
            side_effect=ValueError("Invalid snapshot structure"),
        ):
            stream = subscription.building_state_stream(interval_ms=50)

            with pytest.raises(ValueError, match="Invalid snapshot structure"):
                await anext(stream)

    async def test_subscription_cleanup_on_exception(
        self,
        mock_game_bridge,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Verify finally block executes even on exception."""
        mock_game_bridge.get_building_snapshot.side_effect = RuntimeError("Test error")
        subscription = Subscription(game_bridge=mock_game_bridge)

        with caplog.at_level(logging.INFO, logger="mytower.api.schema"):
            stream = subscription.building_state_stream(interval_ms=50)

            try:
                await anext(stream)
            except RuntimeError:
                pass  # Expected

            # Give finally block time to execute
            await asyncio.sleep(0.01)

            # Verify cleanup happened
            assert any("cleaned up" in record.getMessage() for record in caplog.records)

    async def test_multiple_concurrent_subscriptions(self, mock_game_bridge) -> None:
        """Verify multiple subscriptions can run concurrently."""
        mock_game_bridge.get_building_snapshot.return_value = None
        subscription = Subscription(game_bridge=mock_game_bridge)

        # Create 3 concurrent subscriptions
        stream1 = subscription.building_state_stream(interval_ms=50)
        stream2 = subscription.building_state_stream(interval_ms=100)
        stream3 = subscription.game_time_stream(interval_ms=75)

        # Consume one value from each concurrently
        results = await asyncio.gather(
            anext(stream1),
            anext(stream2),
            anext(stream3),
        )

        # All should succeed
        assert len(results) == 3
        assert results[0] is None  # building_state_stream yields None
        assert results[1] is None  # building_state_stream yields None
        assert results[2] == Time(0.0)  # game_time_stream yields Time(0.0)

    async def test_game_time_stream_handles_cancellation(
        self,
        mock_game_bridge,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Verify game_time_stream sees the cancellation and cleans up."""
        mock_game_bridge.get_building_snapshot.return_value = None
        subscription = Subscription(game_bridge=mock_game_bridge)

        with caplog.at_level(logging.INFO, logger="mytower.api.schema"):
            stream = subscription.game_time_stream(interval_ms=100)

            # Wait for the first item, not for a timer; test_subscription_cleanup_on_cancellation
            # explains why (#163).
            first_item = asyncio.Event()
            task = asyncio.create_task(_consume_and_signal(stream, first_item))
            await asyncio.wait_for(first_item.wait(), timeout=5.0)
            task.cancel()

            with pytest.raises(asyncio.CancelledError):
                await task

            # The task raises CancelledError wherever the cancel lands. These two records are what
            # show it landed inside the generator, in its except and then its finally.
            messages = [record.getMessage() for record in caplog.records]
            assert any("Game time subscription cancelled" in message for message in messages)
            assert any("Game time subscription cleaned up" in message for message in messages)

    async def test_exception_in_middle_of_stream(
        self,
        mock_game_bridge,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify exception during stream (not first yield) is handled."""
        # First call succeeds, second call raises
        mock_game_bridge.get_building_snapshot.side_effect = [
            mock_building_snapshot,  # First call succeeds
            RuntimeError("Unexpected error"),  # Second call fails
        ]
        subscription = Subscription(game_bridge=mock_game_bridge)

        stream = subscription.building_state_stream(interval_ms=5)

        # First yield should succeed
        result1 = await anext(stream)
        assert isinstance(result1, BuildingSnapshotGQL)  # Converted snapshot

        # Second yield should raise
        with pytest.raises(RuntimeError, match="Unexpected error"):
            await anext(stream)


@pytest.mark.asyncio
class TestSubscriptionEdgeCases:
    """Test edge cases and unusual scenarios."""

    async def test_subscription_with_none_and_snapshot_alternating(
        self,
        mock_game_bridge,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify subscription handles alternating None and snapshot values."""
        # Alternate between None and snapshot
        mock_game_bridge.get_building_snapshot.side_effect = [
            None,
            mock_building_snapshot,
            None,
            mock_building_snapshot,
        ]
        subscription = Subscription(game_bridge=mock_game_bridge)

        stream = subscription.building_state_stream(interval_ms=5)

        result1 = await anext(stream)
        assert result1 is None  # None snapshot

        result2 = await anext(stream)
        assert isinstance(result2, BuildingSnapshotGQL)  # Converted snapshot

        result3 = await anext(stream)
        assert result3 is None  # None again

        result4 = await anext(stream)
        assert isinstance(result4, BuildingSnapshotGQL)  # Converted snapshot again

    async def test_subscription_handles_empty_snapshot(
        self,
        mock_game_bridge,
        mock_empty_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify subscription handles empty snapshot (no floors, elevators, people)."""
        mock_game_bridge.get_building_snapshot.return_value = mock_empty_snapshot
        subscription = Subscription(game_bridge=mock_game_bridge)

        stream = subscription.building_state_stream(interval_ms=50)
        result = await anext(stream)

        # Should still convert and yield, with nothing in any list
        assert isinstance(result, BuildingSnapshotGQL)
        assert result.floors == []
        assert result.elevators == []
        assert result.elevator_banks == []
        assert result.people == []

    async def test_subscription_with_zero_time(self, mock_game_bridge) -> None:
        """Verify game_time_stream handles snapshot with time=0."""
        mock_snapshot = Mock(spec=BuildingSnapshot)
        mock_snapshot.time = Time(0.0)
        mock_game_bridge.get_building_snapshot.return_value = mock_snapshot
        subscription = Subscription(game_bridge=mock_game_bridge)

        stream = subscription.game_time_stream(interval_ms=100)
        result = await anext(stream)

        assert result == Time(0.0)

    async def test_subscription_handles_negative_time(self, mock_game_bridge) -> None:
        """Verify subscription can handle negative time values (edge case)."""
        mock_snapshot = Mock(spec=BuildingSnapshot)
        mock_snapshot.time = Time(-10.0)  # Unusual but possible
        mock_game_bridge.get_building_snapshot.return_value = mock_snapshot
        subscription = Subscription(game_bridge=mock_game_bridge)

        stream = subscription.game_time_stream(interval_ms=100)
        result = await anext(stream)

        assert result == Time(-10.0)

    async def test_cancel_immediately_after_creation(self, mock_game_bridge) -> None:
        """Verify subscription can be cancelled before first yield."""
        mock_game_bridge.get_building_snapshot.return_value = None
        subscription = Subscription(game_bridge=mock_game_bridge)

        stream = subscription.building_state_stream(interval_ms=50)

        # Create task and cancel immediately
        task = asyncio.create_task(anext(stream))
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task

    async def test_multiple_cancellations(self, mock_game_bridge, caplog: pytest.LogCaptureFixture) -> None:
        """Verify multiple concurrent subscriptions can all be cancelled, and each one cleans up."""
        mock_game_bridge.get_building_snapshot.return_value = None
        subscription = Subscription(game_bridge=mock_game_bridge)

        with caplog.at_level(logging.INFO, logger="mytower.api.schema"):
            # Create 5 concurrent subscriptions
            streams = [
                subscription.building_state_stream(interval_ms=50)
                for _ in range(5)
            ]

            # One Event per stream, so every consumer is parked inside its generator before any
            # cancel; test_subscription_cleanup_on_cancellation explains why (#163).
            events = [asyncio.Event() for _ in streams]
            tasks = [
                asyncio.create_task(_consume_and_signal(stream, event))
                for stream, event in zip(streams, events, strict=True)
            ]
            await asyncio.wait_for(asyncio.gather(*(event.wait() for event in events)), timeout=5.0)

            # Cancel all
            for task in tasks:
                task.cancel()

            # All should raise CancelledError
            results = await asyncio.gather(*tasks, return_exceptions=True)
            assert all(isinstance(r, asyncio.CancelledError) for r in results)

            # One cleanup record per stream shows that every cancel reached its generator.
            cleanups = [
                record for record in caplog.records
                if "Building State Subscription cleaned up" in record.getMessage()
            ]
            assert len(cleanups) == 5
