# Dependency Injection Refactoring for WebSocket Tests

## Overview

This document describes the refactoring from monkey patching to Protocol-based dependency injection for WebSocket subscription tests.

## Problem

The original tests used `with patch("mytower.api.schema.get_building_state")` to mock the GameBridge access. This approach had several issues:

❌ **Monkey Patching**: Modifies modules at runtime
❌ **Import Path Coupling**: Tests break when imports are refactored
❌ **No Type Safety**: `patch()` bypasses the type system
❌ **Violates Architecture**: MyTower uses Protocol-driven design everywhere else
❌ **Hidden Dependencies**: Not clear what the Subscription depends on

## Solution

Refactor to use Protocol-based dependency injection following MyTower's existing patterns.

---

## Implementation

### 1. Created `GameBridgeProtocol`

**File**: `mytower/api/game_bridge_protocol.py`

```python
from typing import Protocol
from mytower.game.models.model_snapshots import BuildingSnapshot

class GameBridgeProtocol(Protocol):
    """Protocol for accessing game state in a thread-safe manner."""

    def get_building_snapshot(self) -> BuildingSnapshot | None:
        """Get latest building state snapshot (thread-safe)."""
        ...
```

**Benefits**:
- ✅ Defines the contract for game state access
- ✅ Allows mocking without patching
- ✅ Type-safe and explicit

---

### 2. Refactored `Subscription` Class

**File**: `mytower/api/schema.py`

```python
@strawberry.type
class Subscription:
    def __init__(self, game_bridge: GameBridgeProtocol | None = None) -> None:
        """
        Initialize with optional game bridge dependency.

        Args:
            game_bridge: Bridge to access game state. If None, uses global singleton.
        """
        self._game_bridge = game_bridge or get_game_bridge()

    @strawberry.subscription
    async def building_state_stream(self, interval_ms: int = 50):
        snapshot = self._game_bridge.get_building_snapshot()  # ← Injected!
        # ...
```

**Key Changes**:
- Added `__init__()` accepting optional `GameBridgeProtocol`
- Stores as `self._game_bridge`
- Falls back to singleton if not provided (production use)
- Both subscriptions now use `self._game_bridge`

---

### 3. Updated Test Fixtures

**File**: `mytower/tests/api/conftest.py`

```python
from mytower.api.game_bridge_protocol import GameBridgeProtocol  # ← Protocol

@pytest.fixture
def mock_game_bridge() -> Mock:
    """Type-safe mock GameBridge for testing subscriptions."""
    bridge = Mock(spec=GameBridgeProtocol)  # ← Uses Protocol
    bridge.get_building_snapshot.return_value = None
    return bridge
```

**Benefits**:
- ✅ Uses Protocol (not concrete GameBridge class)
- ✅ More flexible for testing
- ✅ Easier to maintain

---

### 4. Refactored Tests

**Before** (Monkey Patching):
```python
async def test_subscription_yields_snapshot(mock_building_snapshot):
    subscription = Subscription()

    with patch("mytower.api.schema.get_building_state", return_value=mock_building_snapshot):
        stream = subscription.building_state_stream(interval_ms=50)
        result = await anext(stream)
        assert result is not None
```

**After** (Dependency Injection):
```python
async def test_subscription_yields_snapshot(
    mock_game_bridge,  # ← Injected fixture
    mock_building_snapshot,
):
    # Arrange: Configure mock
    mock_game_bridge.get_building_snapshot.return_value = mock_building_snapshot

    # Act: Inject dependency
    subscription = Subscription(game_bridge=mock_game_bridge)
    stream = subscription.building_state_stream(interval_ms=50)
    result = await anext(stream)

    # Assert
    assert result is not None
```

**Key Differences**:
| Aspect | Before (Patching) | After (DI) |
|--------|-------------------|------------|
| **Dependency** | Implicit | Explicit |
| **Mocking** | `patch()` string path | Direct fixture injection |
| **Type Safety** | ❌ No | ✅ Yes |
| **Clarity** | Hidden | Obvious |
| **Refactoring** | Breaks on renames | Safe |

---

## Progress

### ✅ Completed (Part 1/2)

1. ✅ Created `GameBridgeProtocol`
2. ✅ Refactored `Subscription` class
3. ✅ Updated `conftest.py`
4. ✅ Refactored `test_subscriptions.py` (17 tests)
   - All `patch("mytower.api.schema.get_building_state")` removed
   - All tests now use dependency injection

### 🚧 In Progress (Part 2/2)

Remaining files to refactor:

| File | Patches to Remove | Status |
|------|-------------------|--------|
| `test_subscription_timing.py` | 11 | Pending |
| `test_subscription_error_handling.py` | 13 | Pending |
| `test_game_bridge_threading.py` | 14 | Pending |
| `test_subscription_integration.py` | 3 | Pending |
| **Total** | **41** | **0% done** |

---

## Pattern Reference

### Arranging Test with Mock

```python
async def test_example(mock_game_bridge, mock_building_snapshot):
    # Configure mock
    mock_game_bridge.get_building_snapshot.return_value = mock_building_snapshot

    # Inject dependency
    subscription = Subscription(game_bridge=mock_game_bridge)
```

### Multiple Return Values

```python
async def test_example(mock_game_bridge):
    # Mock returns different values on successive calls
    mock_game_bridge.get_building_snapshot.side_effect = [
        snapshot1,
        snapshot2,
        snapshot3,
    ]

    subscription = Subscription(game_bridge=mock_game_bridge)
```

### Validation Tests (No Mock Needed)

```python
async def test_validates_parameter():
    # No dependency needed for validation
    subscription = Subscription()  # Uses singleton

    with pytest.raises(ValueError):
        stream = subscription.building_state_stream(interval_ms=-1)
        await anext(stream)
```

---

## Benefits Summary

| Benefit | Description |
|---------|-------------|
| **Type Safety** | `Mock(spec=GameBridgeProtocol)` enforces correct method names |
| **Explicit Dependencies** | Clear what each test depends on |
| **Refactoring Safety** | No string paths to break |
| **Architecture Alignment** | Matches MyTower's Protocol pattern |
| **Better IDE Support** | Autocomplete works |
| **Testability** | Easier to test in isolation |

---

## What Remains as Patches?

Some patches are still acceptable:

### 1. `convert_building_snapshot()`
```python
with patch("mytower.api.schema.convert_building_snapshot"):
    # This is acceptable - testing implementation details
```

**Why**: Type conversion is a utility function, not a core dependency. Could be refactored later with a conversion protocol.

### 2. `asyncio.sleep()`
```python
with patch("mytower.api.schema.asyncio.sleep"):
    # This is acceptable - testing timing behavior
```

**Why**: Testing framework/timing behavior. Not a business logic dependency.

---

## Next Steps

1. Complete Part 2/2: Refactor remaining 4 test files
2. Run full test suite to verify
3. Optional: Create conversion protocol for `convert_building_snapshot`
4. Document patterns for future tests

---

## References

- MyTower Protocol Pattern: `mytower/game/entities/entities_protocol.py`
- Python Protocols: [PEP 544](https://peps.python.org/pep-0544/)
- Dependency Injection: [Martin Fowler](https://martinfowler.com/articles/injection.html)
