# WebSocket Subscription Test Plan

This document outlines a comprehensive test plan for the GraphQL WebSocket subscription functionality added to MyTower.

## 📋 Test Coverage Goals

We aim to test the following components:

1. **Subscription Schema** (`mytower/api/schema.py:103-189`)
   - `building_state_stream()` subscription
   - `game_time_stream()` subscription

2. **Server Configuration** (`mytower/api/server.py:14-19`)
   - WebSocket protocol enablement
   - GraphQLRouter configuration

3. **GameBridge Integration** (existing, but needs thread-safety tests)
   - Thread-safe snapshot retrieval
   - Concurrent subscription access

4. **Type Conversions** (`mytower/api/type_conversions.py`)
   - `convert_building_snapshot()` with WebSocket context

---

## 🔧 Prerequisites

### 1. Add Testing Dependencies

**File:** `requirements-dev.txt`

Add the following dependencies:

```txt
# Async testing support
pytest-asyncio==0.23.7

# WebSocket testing (optional but recommended)
websockets==12.0

# HTTP client for testing (if needed for integration tests)
httpx==0.27.0
```

### 2. Update pytest Configuration

**File:** `pytest.ini`

Add asyncio configuration:

```ini
[pytest]
# Existing configuration...
asyncio_mode = auto

# Add coverage for API module
addopts =
    --showlocals
    --strict-markers
    --cov=mytower.game.entities
    --cov=mytower.game.core
    --cov=mytower.api                    # NEW: Add API coverage
    --cov=mytower.tests.test_protocols
    --cov-report=xml
    --cov-report=html
    --cov-report=term-missing
    --cov-branch
    --cov-context=test

# Mark async tests
markers =
    asyncio: marks tests as async (deselect with '-m "not asyncio"')
```

---

## 📁 Test File Structure

Create the following test files in `mytower/tests/api/`:

```
mytower/tests/api/
├── __init__.py
├── conftest.py                          # Shared fixtures for API tests
├── test_subscriptions.py                # Subscription logic tests (Unit)
├── test_subscription_timing.py          # Timing and interval tests
├── test_subscription_error_handling.py  # Error handling and cancellation
├── test_game_bridge_threading.py        # Thread-safety tests
└── test_subscription_integration.py     # Integration tests (optional)
```

---

## 🧪 Test Cases

### Test File 1: `test_subscriptions.py` (Unit Tests)

**Purpose:** Test subscription logic, parameter validation, and basic yielding behavior.

#### Test Class: `TestBuildingStateStreamSubscription`

| Test Name | Description | Assertions |
|-----------|-------------|------------|
| `test_subscription_yields_snapshot_when_game_running` | Verify subscription yields converted snapshot when game is running | Assert yielded snapshot is `BuildingSnapshotGQL` type, matches expected data |
| `test_subscription_yields_none_when_game_not_running` | Verify subscription yields `None` when `get_building_state()` returns `None` | Assert yielded value is `None` |
| `test_subscription_validates_interval_ms_min_bound` | Verify `ValueError` raised for `interval_ms < 5` | Assert raises `ValueError` with message "must be between 5 and 10000" |
| `test_subscription_validates_interval_ms_max_bound` | Verify `ValueError` raised for `interval_ms > 10000` | Assert raises `ValueError` |
| `test_subscription_accepts_valid_interval_ms` | Verify subscription accepts valid `interval_ms` values (5, 50, 100, 10000) | Assert no exception raised, yields data |
| `test_subscription_converts_snapshot_correctly` | Verify `convert_building_snapshot()` is called with correct args | Mock `convert_building_snapshot`, assert called with snapshot |
| `test_subscription_calls_get_building_state_on_each_iteration` | Verify `get_building_state()` called repeatedly | Assert call count increases with iterations |

#### Test Class: `TestGameTimeStreamSubscription`

| Test Name | Description | Assertions |
|-----------|-------------|------------|
| `test_subscription_yields_time_when_game_running` | Verify subscription yields game time from snapshot | Assert yielded value is `Time` type |
| `test_subscription_yields_zero_when_game_not_running` | Verify subscription yields `Time(0.0)` when no snapshot | Assert yielded value equals `Time(0.0)` |
| `test_subscription_validates_interval_ms_bounds` | Verify parameter validation works | Assert raises `ValueError` for invalid values |
| `test_subscription_extracts_time_from_snapshot` | Verify time extraction from `BuildingSnapshot.time` | Mock snapshot with specific time, assert yielded correctly |

#### Example Test Code

```python
"""
Unit tests for GraphQL WebSocket subscriptions.

File: mytower/tests/api/test_subscriptions.py
"""

import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
import strawberry

from mytower.api.schema import Subscription
from mytower.api.graphql_types import BuildingSnapshotGQL
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
        """Verify parameter validation works."""
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
```

---

### Test File 2: `test_subscription_timing.py`

**Purpose:** Test timing behavior, interval accuracy, and performance.

#### Test Class: `TestSubscriptionTiming`

| Test Name | Description | Assertions |
|-----------|-------------|------------|
| `test_subscription_respects_interval_ms` | Verify subscription waits correct interval between yields | Measure time between yields, assert within tolerance |
| `test_subscription_interval_conversion_to_seconds` | Verify `interval_ms / 1000.0` conversion is correct | Assert sleep duration matches expected value |
| `test_subscription_continues_indefinitely` | Verify subscription loops forever (unless cancelled) | Collect N yields, assert all succeed |
| `test_fast_interval_performance` | Verify subscription handles fast intervals (5ms) | Assert yields happen rapidly, no blocking |
| `test_slow_interval_performance` | Verify subscription handles slow intervals (10000ms) | Assert yields are spaced correctly |

#### Example Test Code

```python
"""
Timing and interval tests for WebSocket subscriptions.

File: mytower/tests/api/test_subscription_timing.py
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
            start = time.time()
            await anext(stream)
            first_yield = time.time()
            await anext(stream)
            second_yield = time.time()

            elapsed = second_yield - first_yield
            expected_interval_s = interval_ms / 1000.0

            # Allow 10% tolerance for timing variations
            tolerance = expected_interval_s * 0.1
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

        with patch("mytower.api.schema.get_building_state", return_value=None):
            stream = subscription.building_state_stream(interval_ms=fast_interval_ms)

            start = time.time()
            for _ in range(10):  # 10 iterations
                await anext(stream)
            elapsed = time.time() - start

            # Should take at least 10 * 5ms = 50ms (0.05s)
            # Allow up to 100ms (0.1s) for overhead
            assert 0.04 < elapsed < 0.2, f"Expected ~0.05s, got {elapsed}s"

    async def test_slow_interval_performance(self) -> None:
        """Verify subscription handles slow intervals (1000ms)."""
        subscription = Subscription()

        with patch("mytower.api.schema.get_building_state", return_value=None):
            stream = subscription.building_state_stream(interval_ms=1000)

            start = time.time()
            await anext(stream)
            first = time.time()
            await anext(stream)
            second = time.time()

            elapsed = second - first
            # Should be approximately 1 second
            assert 0.9 < elapsed < 1.2, f"Expected ~1.0s, got {elapsed}s"
```

---

### Test File 3: `test_subscription_error_handling.py`

**Purpose:** Test error handling, cancellation, cleanup, and edge cases.

#### Test Class: `TestSubscriptionErrorHandling`

| Test Name | Description | Assertions |
|-----------|-------------|------------|
| `test_subscription_handles_cancellation` | Verify subscription raises `asyncio.CancelledError` and cleans up | Assert exception propagates, finally block executes |
| `test_subscription_cleanup_on_cancellation` | Verify finally block executes on cancellation | Mock print, assert cleanup message printed |
| `test_subscription_handles_get_building_state_exception` | Verify exception from `get_building_state()` propagates | Assert exception raised, finally block executes |
| `test_subscription_handles_convert_snapshot_exception` | Verify exception from `convert_building_snapshot()` propagates | Assert exception raised |
| `test_subscription_cleanup_on_exception` | Verify finally block executes even on exception | Assert cleanup happens |
| `test_multiple_concurrent_subscriptions` | Verify multiple subscriptions can run concurrently | Create 3 subscriptions, assert all yield independently |

#### Example Test Code

```python
"""
Error handling and cancellation tests for WebSocket subscriptions.

File: mytower/tests/api/test_subscription_error_handling.py
"""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from mytower.api.schema import Subscription
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

            # Consume one value from each
            results = await asyncio.gather(
                anext(stream1),
                anext(stream2),
                anext(stream3),
            )

            # All should succeed
            assert len(results) == 3
            assert results[0] is None  # building_state_stream yields None
            assert results[1] is None  # building_state_stream yields None
            assert results[2] == 0.0   # game_time_stream yields Time(0.0)
```

---

### Test File 4: `test_game_bridge_threading.py`

**Purpose:** Test thread-safety of GameBridge when accessed by multiple subscriptions.

#### Test Class: `TestGameBridgeThreadSafety`

| Test Name | Description | Assertions |
|-----------|-------------|------------|
| `test_concurrent_snapshot_access` | Verify multiple threads can safely call `get_building_snapshot()` | No exceptions, all get valid data |
| `test_snapshot_lock_prevents_race_conditions` | Verify `_snapshot_lock` prevents concurrent modification | Assert no data corruption |
| `test_subscription_doesnt_block_game_thread` | Verify subscriptions don't block `update_game()` | Measure update latency with active subscriptions |

**Note:** These tests require threading/asyncio coordination and are more complex.

---

### Test File 5: `test_subscription_integration.py` (Optional)

**Purpose:** Full integration tests with real WebSocket connections.

#### Test Class: `TestSubscriptionIntegration`

| Test Name | Description | Assertions |
|-----------|-------------|------------|
| `test_graphql_schema_includes_subscription` | Verify schema has Subscription type | Assert `schema.subscription_type` is not None |
| `test_subscription_field_definitions` | Verify subscription fields are defined correctly | Assert `building_state_stream` and `game_time_stream` exist |
| `test_strawberry_subscription_decorator` | Verify `@strawberry.subscription` is applied | Check field metadata |

---

## 🎯 Fixtures to Add

**File:** `mytower/tests/api/conftest.py`

```python
"""
Shared fixtures for API and subscription tests.

File: mytower/tests/api/conftest.py
"""

from typing import Any
from unittest.mock import MagicMock

import pytest

from mytower.api.graphql_types import (
    BuildingSnapshotGQL,
    FloorSnapshotGQL,
    ElevatorSnapshotGQL,
    PersonSnapshotGQL,
)
from mytower.game.core.types import FloorType, PersonState, ElevatorState
from mytower.game.core.units import Time, Blocks
from mytower.game.models.model_snapshots import (
    BuildingSnapshot,
    FloorSnapshot,
    ElevatorSnapshot,
    PersonSnapshot,
)


@pytest.fixture
def mock_building_snapshot() -> BuildingSnapshot:
    """Create a mock BuildingSnapshot for testing."""
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
                nominal_direction=1,  # UP
                door_open=False,
                passenger_count=2,
                available_capacity=13,
                max_capacity=15,
            )
        ],
        elevator_banks=[],
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
    """Create a mock BuildingSnapshotGQL for testing."""
    return BuildingSnapshotGQL(
        time=Time(123.45),
        money=50000,
        floors=[],
        elevators=[],
        elevator_banks=[],
        people=[],
    )


@pytest.fixture
def mock_game_bridge() -> MagicMock:
    """Create a mock GameBridge."""
    bridge = MagicMock()
    bridge.get_building_snapshot.return_value = None
    return bridge
```

---

## 📊 Coverage Targets

After implementing these tests, we should achieve:

| Module | Current Coverage | Target Coverage |
|--------|------------------|-----------------|
| `mytower.api.schema` (Subscription class) | 0% | 95%+ |
| `mytower.api.server` (WebSocket config) | 0% | 90%+ |
| `mytower.api.game_bridge` (Thread safety) | ~60% | 85%+ |
| `mytower.api.type_conversions` | ~70% | 90%+ |

---

## 🚀 Implementation Order

1. **Phase 1: Setup** (30 minutes)
   - Add `pytest-asyncio` to `requirements-dev.txt`
   - Update `pytest.ini` with `asyncio_mode = auto`
   - Create `mytower/tests/api/` directory structure
   - Create `conftest.py` with fixtures

2. **Phase 2: Core Tests** (2 hours)
   - Implement `test_subscriptions.py` (unit tests)
   - Implement `test_subscription_timing.py` (timing tests)
   - Run tests, verify green

3. **Phase 3: Error Handling** (1 hour)
   - Implement `test_subscription_error_handling.py`
   - Test cancellation and cleanup

4. **Phase 4: Thread Safety** (1 hour)
   - Implement `test_game_bridge_threading.py`
   - Add stress tests for concurrent access

5. **Phase 5: Integration** (Optional, 1 hour)
   - Implement `test_subscription_integration.py`
   - Add end-to-end WebSocket tests

---

## 🔍 Test Execution

Run all subscription tests:
```bash
pytest mytower/tests/api/ -v
```

Run specific test file:
```bash
pytest mytower/tests/api/test_subscriptions.py -v
```

Run async tests only:
```bash
pytest -m asyncio -v
```

Run with coverage:
```bash
pytest mytower/tests/api/ --cov=mytower.api --cov-report=html
```

---

## 📝 Additional Considerations

### Mocking Strategy

Follow existing patterns:
- Use `unittest.mock.patch` for patching imports
- Use `MagicMock` for complex objects
- Use `PropertyMock` for properties
- Use `Mock(spec=Protocol)` for typed mocks

### Async Testing Best Practices

1. **Always mark async tests** with `@pytest.mark.asyncio`
2. **Use `await anext(stream)`** to consume async generators
3. **Use `asyncio.create_task()`** for concurrent execution
4. **Use `asyncio.gather()`** for parallel async operations
5. **Always cancel tasks** in finally blocks to prevent warnings

### Common Pitfalls

1. **Forgetting to await async generators** - Use `await anext(stream)`, not `next(stream)`
2. **Not cancelling tasks** - Uncancelled tasks cause warnings
3. **Timing tests are flaky** - Use generous tolerances (10-20%)
4. **Mock patches must match import location** - Patch where used, not where defined

---

## ✅ Success Criteria

Tests are considered complete when:

- [ ] All test files created and passing
- [ ] Coverage >= 90% for `mytower.api.schema.Subscription`
- [ ] All edge cases covered (validation, errors, cancellation)
- [ ] Timing tests pass consistently (run 10 times)
- [ ] No flaky tests (intermittent failures)
- [ ] Documentation updated with test examples
- [ ] CI/CD pipeline passes all tests

---

## 📚 References

- [pytest-asyncio docs](https://pytest-asyncio.readthedocs.io/)
- [Strawberry GraphQL Testing](https://strawberry.rocks/docs/operations/testing)
- [Python asyncio Testing](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task)
- Existing MyTower test patterns in `mytower/tests/`
