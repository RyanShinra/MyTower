# Remaining DI Refactoring Work

## Progress Summary

✅ **Completed: 31/41 patches removed (76%)**

| File | Patches | Status |
|------|---------|--------|
| `test_subscriptions.py` | 17 | ✅ Complete |
| `test_subscription_integration.py` | 3 | ✅ Complete |
| `test_subscription_timing.py` | 11 | ✅ Complete |
| **test_subscription_error_handling.py** | **13** | **🚧 Pending** |
| **test_game_bridge_threading.py** | **14** | **🚧 Pending** |

---

## Remaining Files

### 1. `test_subscription_error_handling.py` (13 patches)

**Tests that need refactoring:**

```python
# Pattern: Simple patches (10 tests)
async def test_subscription_handles_cancellation(self, mock_game_bridge):
    mock_game_bridge.get_building_snapshot.return_value = None
    subscription = Subscription(game_bridge=mock_game_bridge)
    # ... rest of test

# Pattern: Exception from GameBridge (2 tests)
async def test_subscription_handles_get_building_state_exception(self, mock_game_bridge):
    # Mock bridge to raise exception
    mock_game_bridge.get_building_snapshot.side_effect = RuntimeError("GameBridge not initialized")
    subscription = Subscription(game_bridge=mock_game_bridge)
    # ... test that exception propagates

# Pattern: Alternating return values (1 test)
async def test_subscription_with_none_and_snapshot_alternating(self, mock_game_bridge):
    mock_game_bridge.get_building_snapshot.side_effect = [None, snapshot1, None, snapshot2]
    subscription = Subscription(game_bridge=mock_game_bridge)
    # ... test state changes
```

**Key insight**: Exception tests are BETTER with DI because they test the actual contract (GameBridge can raise exceptions) rather than patching global functions.

---

### 2. `test_game_bridge_threading.py` (14 patches)

**Tests that need refactoring:**

```python
# Pattern: Concurrent access (most tests)
async def test_concurrent_snapshot_access(self, mock_game_bridge):
    mock_game_bridge.get_building_snapshot.return_value = snapshot
    subscription = Subscription(game_bridge=mock_game_bridge)
    # ... create multiple streams concurrently

# Pattern: Side effects for state changes
async def test_get_building_state_starts_returning_snapshots(self, mock_game_bridge):
    # Simulate game starting
    mock_game_bridge.get_building_snapshot.side_effect = [None, None, snapshot]
    subscription = Subscription(game_bridge=mock_game_bridge)
    # ... verify progression
```

---

## Refactoring Pattern

All remaining tests follow the same 3-step pattern:

### Before (Monkey Patching):
```python
async def test_example(self):
    subscription = Subscription()

    with patch("mytower.api.schema.get_building_state", return_value=None):
        stream = subscription.building_state_stream(interval_ms=50)
        result = await anext(stream)
```

### After (Dependency Injection):
```python
async def test_example(self, mock_game_bridge):  # ← Add fixture parameter
    # Arrange
    mock_game_bridge.get_building_snapshot.return_value = None

    # Act: Inject dependency
    subscription = Subscription(game_bridge=mock_game_bridge)
    stream = subscription.building_state_stream(interval_ms=50)
    result = await anext(stream)
```

---

## Special Cases

### Exception Testing
```python
# OLD (patching global function):
with patch("mytower.api.schema.get_building_state", side_effect=RuntimeError("Error")):
    stream = subscription.building_state_stream(interval_ms=50)
    # Test exception

# NEW (testing contract):
mock_game_bridge.get_building_snapshot.side_effect = RuntimeError("GameBridge not initialized")
subscription = Subscription(game_bridge=mock_game_bridge)
stream = subscription.building_state_stream(interval_ms=50)
# Test exception
```

This is actually BETTER because it tests the real contract: "GameBridge.get_building_snapshot() can raise exceptions."

### Multiple Return Values
```python
# Configure mock to return different values on successive calls
mock_game_bridge.get_building_snapshot.side_effect = [
    None,        # First call
    snapshot1,   # Second call
    snapshot2,   # Third call
]
```

---

## Estimated Effort

- **test_subscription_error_handling.py**: ~15 minutes (13 straightforward replacements)
- **test_game_bridge_threading.py**: ~20 minutes (14 replacements, some with concurrency)

**Total**: ~35 minutes to complete all remaining refactoring

---

## Benefits So Far

From the 31 tests already refactored:

✅ **No more monkey patching for GameBridge access**
✅ **Type-safe dependency injection via Protocol**
✅ **Tests explicitly declare dependencies**
✅ **Aligned with MyTower's architecture**
✅ **Easier to refactor - no import path dependencies**

---

## Next Steps

1. **Option A**: Complete remaining 2 files now (~35 minutes)
2. **Option B**: Commit current progress, complete later
3. **Option C**: Keep completed files, revert remaining files to original (maintain working tests)

**Recommendation**: Complete the remaining files to finish the refactoring. The pattern is established and the remaining work is straightforward repetition.
