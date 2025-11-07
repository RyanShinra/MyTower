"""
Timing and interval tests for WebSocket subscriptions.

Tests cover:
- Interval accuracy and timing
- Sleep duration correctness
- Continuous streaming behavior
- Fast and slow interval performance
"""

import asyncio
import time
from unittest.mock import patch

import pytest

from mytower.api.schema import Subscription


@pytest.mark.asyncio
class TestSubscriptionTiming:
    """Test timing behavior of subscriptions."""

    async def test_subscription_respects_interval_ms(self) -> None:
        """Verify subscription waits correct interval between yields."""
        subscription = Subscription()
        interval_ms = 100  # 100ms = 0.1s

        with patch("mytower.api.schema.get_building_state", return_value=None):
            stream = subscription.building_state_stream(interval_ms=interval_ms)

            # Measure time between first and second yield
            await anext(stream)
            start = time.time()
            await anext(stream)
            elapsed = time.time() - start

            expected_interval_s = interval_ms / 1000.0

            # Allow 50ms (0.05s) tolerance for timing variations
            tolerance = 0.05
            assert abs(elapsed - expected_interval_s) < tolerance, (
                f"Expected ~{expected_interval_s}s interval, got {elapsed}s"
            )

    async def test_subscription_interval_conversion_to_seconds(self) -> None:
        """Verify interval_ms / 1000.0 conversion is correct."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
            with patch("mytower.api.schema.asyncio.sleep") as mock_sleep:
                stream = subscription.building_state_stream(interval_ms=250)
                await anext(stream)

                # Verify sleep was called with correct seconds value
                mock_sleep.assert_called_once_with(0.250)

    async def test_subscription_continues_indefinitely(self) -> None:
        """Verify subscription loops forever (unless cancelled)."""
        subscription = Subscription()
        iteration_count = 10

        with patch("mytower.api.schema.get_building_state", return_value=None):
            stream = subscription.building_state_stream(interval_ms=5)

            # Collect N yields
            results = []
            for _ in range(iteration_count):
                result = await anext(stream)
                results.append(result)

            # All should succeed (return None)
            assert len(results) == iteration_count
            assert all(r is None for r in results)

    async def test_fast_interval_performance(self) -> None:
        """Verify subscription handles fast intervals (5ms minimum)."""
        subscription = Subscription()
        fast_interval_ms = 5
        iteration_count = 10

        with patch("mytower.api.schema.get_building_state", return_value=None):
            stream = subscription.building_state_stream(interval_ms=fast_interval_ms)

            start = time.time()
            for _ in range(iteration_count):
                await anext(stream)
            elapsed = time.time() - start

            # Should take at least 10 * 5ms = 50ms (0.05s)
            # Allow up to 200ms (0.2s) for overhead
            expected_min = (iteration_count * fast_interval_ms) / 1000.0
            assert elapsed >= expected_min * 0.8, f"Too fast: {elapsed}s < {expected_min}s"
            assert elapsed < 0.3, f"Too slow: {elapsed}s > 0.3s"

    async def test_slow_interval_performance(self) -> None:
        """Verify subscription handles slow intervals (1000ms)."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
            stream = subscription.building_state_stream(interval_ms=1000)

            # Get first yield (no wait)
            await anext(stream)

            # Measure second yield (should wait ~1s)
            start = time.time()
            await anext(stream)
            elapsed = time.time() - start

            # Should be approximately 1 second
            assert 0.9 < elapsed < 1.2, f"Expected ~1.0s, got {elapsed}s"

    async def test_game_time_stream_interval_accuracy(self) -> None:
        """Verify game_time_stream also respects interval timing."""
        subscription = Subscription()
        interval_ms = 100

        with patch("mytower.api.schema.get_building_state", return_value=None):
            stream = subscription.game_time_stream(interval_ms=interval_ms)

            await anext(stream)
            start = time.time()
            await anext(stream)
            elapsed = time.time() - start

            expected = interval_ms / 1000.0
            tolerance = 0.05
            assert abs(elapsed - expected) < tolerance, f"Expected ~{expected}s, got {elapsed}s"

    async def test_multiple_intervals_in_same_stream(self) -> None:
        """Verify consistent interval timing across multiple yields."""
        subscription = Subscription()
        interval_ms = 50

        with patch("mytower.api.schema.get_building_state", return_value=None):
            stream = subscription.building_state_stream(interval_ms=interval_ms)

            # Collect timing data for 5 intervals
            await anext(stream)  # First yield (no wait)

            timings = []
            for _ in range(5):
                start = time.time()
                await anext(stream)
                elapsed = time.time() - start
                timings.append(elapsed)

            # All intervals should be approximately 50ms
            expected = interval_ms / 1000.0
            tolerance = 0.03  # 30ms tolerance
            for i, timing in enumerate(timings):
                assert abs(timing - expected) < tolerance, (
                    f"Interval {i}: Expected ~{expected}s, got {timing}s"
                )

    async def test_sleep_called_after_each_yield(self) -> None:
        """Verify asyncio.sleep is called after each yield, not before."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
            with patch("mytower.api.schema.asyncio.sleep") as mock_sleep:
                stream = subscription.building_state_stream(interval_ms=100)

                # First yield should happen immediately (no prior sleep)
                await anext(stream)
                mock_sleep.assert_called_once_with(0.1)

                # Second yield should sleep again
                await anext(stream)
                assert mock_sleep.call_count == 2

                # Third yield
                await anext(stream)
                assert mock_sleep.call_count == 3


@pytest.mark.asyncio
class TestTimingEdgeCases:
    """Test edge cases in subscription timing."""

    async def test_minimum_interval_boundary(self) -> None:
        """Verify minimum interval (5ms) works correctly."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
            with patch("mytower.api.schema.asyncio.sleep") as mock_sleep:
                stream = subscription.building_state_stream(interval_ms=5)
                await anext(stream)

                # Should sleep for exactly 0.005 seconds
                mock_sleep.assert_called_once_with(0.005)

    async def test_maximum_interval_boundary(self) -> None:
        """Verify maximum interval (10000ms) works correctly."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
            with patch("mytower.api.schema.asyncio.sleep") as mock_sleep:
                stream = subscription.building_state_stream(interval_ms=10000)
                await anext(stream)

                # Should sleep for exactly 10.0 seconds
                mock_sleep.assert_called_once_with(10.0)

    async def test_different_intervals_for_different_subscriptions(self) -> None:
        """Verify different subscription instances can have different intervals."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
            with patch("mytower.api.schema.asyncio.sleep") as mock_sleep:
                # Create two streams with different intervals
                stream1 = subscription.building_state_stream(interval_ms=50)
                stream2 = subscription.building_state_stream(interval_ms=200)

                # Consume one from each
                await anext(stream1)
                assert mock_sleep.call_args_list[-1][0][0] == 0.05

                await anext(stream2)
                assert mock_sleep.call_args_list[-1][0][0] == 0.20
