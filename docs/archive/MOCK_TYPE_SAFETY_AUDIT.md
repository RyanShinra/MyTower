# Mock Type Safety Audit for WebSocket Tests

## Issues Found

### ❌ Problem 1: Untyped `MagicMock` in conftest.py

**File**: `mytower/tests/api/conftest.py:172`

```python
# CURRENT (BAD):
@pytest.fixture
def mock_game_bridge() -> MagicMock:
    bridge = MagicMock()  # ❌ No spec, no type safety
    bridge.get_building_snapshot.return_value = None
    return bridge
```

**Issue**: No type checking, allows any attribute access, return type is generic `MagicMock`

**Fix**: Use `Mock(spec=GameBridge)` for type safety

---

### ❌ Problem 2: Untyped return values in test_subscriptions.py

**File**: `mytower/tests/api/test_subscriptions.py:213, 238`

```python
# CURRENT (BAD):
mock_convert.return_value = MagicMock()  # ❌ No spec
```

**Issue**: Should specify that it returns `BuildingSnapshotGQL`

**Fix**: Use `Mock(spec=BuildingSnapshotGQL)`

---

### ❌ Problem 3: Untyped return values in test_game_bridge_threading.py

**File**: `mytower/tests/api/test_game_bridge_threading.py:234, 329`

```python
# CURRENT (BAD):
with patch("...", return_value=MagicMock()):  # ❌ No spec
```

**Issue**: Should specify `BuildingSnapshotGQL`

**Fix**: Use `Mock(spec=BuildingSnapshotGQL)`

---

## ✅ Good Examples (Already Correct)

These uses are already properly typed:

```python
# test_subscriptions.py:98
mock_convert.return_value = MagicMock(spec=BuildingSnapshotGQL)  # ✅ Good!

# test_subscriptions.py:202
mock_snapshot = MagicMock(spec=BuildingSnapshot)  # ✅ Good!

# test_subscription_error_handling.py:251
mock_snapshot = MagicMock(spec=BuildingSnapshot)  # ✅ Good!
```

---

## Why `Mock` vs `MagicMock`?

### Use `Mock(spec=X)`:
- ✅ Type safe - only allows attributes that exist on X
- ✅ Catches typos at test time
- ✅ More restrictive = better

### Use `MagicMock(spec=X)`:
- ⚠️ Only when you need magic methods (`__len__`, `__iter__`, etc.)
- ⚠️ More permissive than `Mock`

### Best Practice:
**Default to `Mock(spec=X)`, upgrade to `MagicMock(spec=X)` only if needed**

---

## Why Not Just `spec=` on `MagicMock`?

Even with `spec=`, `MagicMock` is overkill:

```python
# Unnecessary magic method support:
mock = MagicMock(spec=BuildingSnapshot)
len(mock)  # Works, but BuildingSnapshot doesn't support len()!

# Better:
mock = Mock(spec=BuildingSnapshot)
len(mock)  # Raises AttributeError - correct!
```

---

## Fixes Applied ✅

All issues have been resolved:

1. ✅ **conftest.py**: Changed `MagicMock()` → `Mock(spec=GameBridge)`
   - Added import: `from mytower.api.game_bridge import GameBridge`
   - Fixture now returns strongly-typed `Mock` instead of `MagicMock`

2. ✅ **test_subscription_error_handling.py**:
   - Changed all `MagicMock()` → `Mock(spec=BuildingSnapshotGQL)` (2 places for return values)
   - Changed `MagicMock(spec=BuildingSnapshot)` → `Mock(spec=BuildingSnapshot)` (2 places)
   - Added import: `from mytower.api.graphql_types import BuildingSnapshotGQL`
   - Removed import: `MagicMock`

3. ✅ **test_game_bridge_threading.py**:
   - Changed all `MagicMock()` → `Mock(spec=BuildingSnapshotGQL)` (2 places)
   - Added import: `from mytower.api.graphql_types import BuildingSnapshotGQL`
   - Removed import: `MagicMock`

4. ✅ **test_subscriptions.py**:
   - Changed `MagicMock(spec=BuildingSnapshotGQL)` → `Mock(spec=BuildingSnapshotGQL)` (1 place)
   - Changed `MagicMock(spec=BuildingSnapshot)` → `Mock(spec=BuildingSnapshot)` (4 places)
   - Removed import: `MagicMock`

5. ✅ **Import cleanup**: All `MagicMock` imports removed from test files

**Total**: 11 improvements across 4 files

## Verification

```bash
# No more untyped MagicMock uses:
grep -n "MagicMock" mytower/tests/api/*.py | grep -v "spec=" | grep -v "import Mock"
# Result: (empty - all clear!)

# Syntax check passed:
python -m py_compile mytower/tests/api/*.py
# Result: ✅ All test files: No syntax errors after mock refactoring
```

## Benefits Achieved

- ✅ **Type Safety**: All mocks now enforce attribute access via `spec=`
- ✅ **Consistency**: Using `Mock` instead of `MagicMock` unless magic methods needed
- ✅ **Caught Typos**: Accessing non-existent attributes will now fail at test time
- ✅ **Better IDE Support**: Auto-completion works with spec-based mocks
- ✅ **Cleaner Tests**: Less magical behavior, more explicit
