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
from unittest.mock import Mock, patch

import pytest

from mytower.api.graphql_types import BuildingSnapshotGQL
from mytower.api.schema import Subscription
from mytower.game.core.units import Time
from mytower.game.models.model_snapshots import BuildingSnapshot


@pytest.mark.asyncio
class TestSubscriptionErrorHandling:
    """Test error handling and cancellation behavior."""

    async def test_subscription_handles_cancellation(self) -> None:
        """Verify subscription raises CancelledError and cleans up."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
            stream = subscription.building_state_stream(interval_ms=50)

            # Start consuming stream in a task
            task = asyncio.create_task(self._consume_stream(stream))
            await asyncio.sleep(0.01)  # Let it start

            # Cancel the task
            task.cancel()

            # Should raise CancelledError
            with pytest.raises(asyncio.CancelledError):
                await task

    async def _consume_stream(self, stream):
        """Helper to consume stream indefinitely."""
        async for _ in stream:
            await asyncio.sleep(0.001)

    async def test_subscription_cleanup_on_cancellation(self) -> None:
        """Verify finally block executes on cancellation."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
            with patch("builtins.print") as mock_print:
                stream = subscription.building_state_stream(interval_ms=50)

                task = asyncio.create_task(self._consume_stream(stream))
                await asyncio.sleep(0.01)
                task.cancel()

                try:
                    await task
                except asyncio.CancelledError:
                    pass

                # Give finally block time to execute
                await asyncio.sleep(0.01)

                # Verify cleanup message was printed
                cleanup_calls = [
                    call for call in mock_print.call_args_list
                    if "Building State Subscription stream cleaned up" in str(call)
                ]
                assert len(cleanup_calls) > 0, "Cleanup message not printed"

    async def test_subscription_handles_get_building_state_exception(self) -> None:
        """Verify exception from get_building_state() propagates."""
        subscription = Subscription()

        with patch(
            "mytower.api.schema.get_building_state",
            side_effect=RuntimeError("GameBridge not initialized"),
        ):
            stream = subscription.building_state_stream(interval_ms=50)

            with pytest.raises(RuntimeError, match="GameBridge not initialized"):
                await anext(stream)

    async def test_subscription_handles_convert_snapshot_exception(
        self,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify exception from convert_building_snapshot() propagates."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=mock_building_snapshot):
            with patch(
                "mytower.api.schema.convert_building_snapshot",
                side_effect=ValueError("Invalid snapshot structure"),
            ):
                stream = subscription.building_state_stream(interval_ms=50)

                with pytest.raises(ValueError, match="Invalid snapshot structure"):
                    await anext(stream)

    async def test_subscription_cleanup_on_exception(self) -> None:
        """Verify finally block executes even on exception."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", side_effect=RuntimeError("Test error")):
            with patch("builtins.print") as mock_print:
                stream = subscription.building_state_stream(interval_ms=50)

                try:
                    await anext(stream)
                except RuntimeError:
                    pass  # Expected

                # Give finally block time to execute
                await asyncio.sleep(0.01)

                # Verify cleanup happened
                cleanup_calls = [
                    call for call in mock_print.call_args_list
                    if "cleaned up" in str(call)
                ]
                assert len(cleanup_calls) > 0

    async def test_multiple_concurrent_subscriptions(self) -> None:
        """Verify multiple subscriptions can run concurrently."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
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

    async def test_game_time_stream_handles_cancellation(self) -> None:
        """Verify game_time_stream also handles cancellation correctly."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
            stream = subscription.game_time_stream(interval_ms=100)

            task = asyncio.create_task(self._consume_stream(stream))
            await asyncio.sleep(0.01)
            task.cancel()

            with pytest.raises(asyncio.CancelledError):
                await task

    async def test_exception_in_middle_of_stream(
        self,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify exception during stream (not first yield) is handled."""
        subscription = Subscription()

        # First call succeeds, second call raises
        with patch("mytower.api.schema.get_building_state") as mock_get_state:
            mock_get_state.side_effect = [
                mock_building_snapshot,  # First call succeeds
                RuntimeError("Unexpected error"),  # Second call fails
            ]

            with patch("mytower.api.schema.convert_building_snapshot", return_value=None):
                stream = subscription.building_state_stream(interval_ms=5)

                # First yield should succeed
                result1 = await anext(stream)
                assert result1 is None  # Converted snapshot

                # Second yield should raise
                with pytest.raises(RuntimeError, match="Unexpected error"):
                    await anext(stream)


@pytest.mark.asyncio
class TestSubscriptionEdgeCases:
    """Test edge cases and unusual scenarios."""

    async def test_subscription_with_none_and_snapshot_alternating(
        self,
        mock_building_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify subscription handles alternating None and snapshot values."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state") as mock_get_state:
            # Alternate between None and snapshot
            mock_get_state.side_effect = [
                None,
                mock_building_snapshot,
                None,
                mock_building_snapshot,
            ]

            with patch("mytower.api.schema.convert_building_snapshot") as mock_convert:
                mock_convert.return_value = Mock(spec=BuildingSnapshotGQL)

                stream = subscription.building_state_stream(interval_ms=5)

                result1 = await anext(stream)
                assert result1 is None  # None snapshot

                result2 = await anext(stream)
                assert result2 is not None  # Converted snapshot

                result3 = await anext(stream)
                assert result3 is None  # None again

                result4 = await anext(stream)
                assert result4 is not None  # Converted snapshot again

    async def test_subscription_handles_empty_snapshot(
        self,
        mock_empty_snapshot: BuildingSnapshot,
    ) -> None:
        """Verify subscription handles empty snapshot (no floors, elevators, people)."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=mock_empty_snapshot):
            with patch("mytower.api.schema.convert_building_snapshot") as mock_convert:
                mock_convert.return_value = Mock(spec=BuildingSnapshotGQL)

                stream = subscription.building_state_stream(interval_ms=50)
                result = await anext(stream)

                # Should still convert and yield
                assert result is not None
                mock_convert.assert_called_once_with(mock_empty_snapshot)

    async def test_subscription_with_zero_time(self) -> None:
        """Verify game_time_stream handles snapshot with time=0."""
        subscription = Subscription()

        mock_snapshot = Mock(spec=BuildingSnapshot)
        mock_snapshot.time = Time(0.0)

        with patch("mytower.api.schema.get_building_state", return_value=mock_snapshot):
            stream = subscription.game_time_stream(interval_ms=100)
            result = await anext(stream)

            assert result == Time(0.0)

    async def test_subscription_handles_negative_time(self) -> None:
        """Verify subscription can handle negative time values (edge case)."""
        subscription = Subscription()

        mock_snapshot = Mock(spec=BuildingSnapshot)
        mock_snapshot.time = Time(-10.0)  # Unusual but possible

        with patch("mytower.api.schema.get_building_state", return_value=mock_snapshot):
            stream = subscription.game_time_stream(interval_ms=100)
            result = await anext(stream)

            assert result == Time(-10.0)

    async def test_cancel_immediately_after_creation(self) -> None:
        """Verify subscription can be cancelled before first yield."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
            stream = subscription.building_state_stream(interval_ms=50)

            # Create task and cancel immediately
            task = asyncio.create_task(anext(stream))
            task.cancel()

            with pytest.raises(asyncio.CancelledError):
                await task

    async def test_multiple_cancellations(self) -> None:
        """Verify multiple concurrent subscriptions can all be cancelled."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
            # Create 5 concurrent subscriptions
            streams = [
                subscription.building_state_stream(interval_ms=50)
                for _ in range(5)
            ]

            # Start tasks
            tasks = [
                asyncio.create_task(self._consume_stream(stream))
                for stream in streams
            ]

            await asyncio.sleep(0.01)  # Let them start

            # Cancel all
            for task in tasks:
                task.cancel()

            # All should raise CancelledError
            results = await asyncio.gather(*tasks, return_exceptions=True)
            assert all(isinstance(r, asyncio.CancelledError) for r in results)

    async def _consume_stream(self, stream):
        """Helper to consume stream indefinitely."""
        async for _ in stream:
            await asyncio.sleep(0.001)
