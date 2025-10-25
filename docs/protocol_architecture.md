# Protocol Architecture Guide

## Overview

MyTower uses Python protocols for dependency injection and type safety. This document explains the pattern and best practices.

## Protocol Types

### Production Protocols (`entities_protocol.py`)
Define interfaces for production code. Never depend on concrete implementations.

```python
class PersonProtocol(Protocol):
    @property
    def current_floor_num(self) -> int: ...

    def board_elevator(self, elevator: ElevatorProtocol) -> None: ...
```

**Usage:** All production code depends on these.

### Testing Protocols (`entities_protocol.py`)
Expose internal state for unit tests. Prefixed with `testing_`.

```python
class PersonTestingProtocol(Protocol):
    def testing_set_current_floor(self, floor: FloorProtocol) -> None: ...
    def testing_get_current_elevator(self) -> ElevatorProtocol | None: ...
```

**Usage:** Only test code depends on these.

### Combined Test Protocols (`tests/test_protocols.py`)
Combine production + testing for test fixtures.

```python
class TestablePersonProtocol(PersonProtocol, PersonTestingProtocol, Protocol):
    pass
```

**Usage:** Type hints for test fixtures returning real objects.

## Type Guidelines

### ✅ Correct Patterns

```python
# Production code - depend on protocols
def process_person(person: PersonProtocol) -> None: ...

# Test fixtures - real objects use Testable protocols
@pytest.fixture
def person() -> TestablePersonProtocol:
    return Person(...)

# Test fixtures - mocks return Mock
@pytest.fixture
def mock_person() -> Mock:
    return MagicMock(spec=PersonProtocol)

# Test code - cast Mock to protocol when needed
mock = create_mock()
protocol: PersonProtocol = cast(PersonProtocol, mock)
```

### ❌ Anti-Patterns

```python
# ❌ Production code depending on concrete class
def process_person(person: Person) -> None: ...

# ❌ Mock fixture claiming to return protocol
@pytest.fixture
def mock_person() -> PersonProtocol:  # Lying!
    return MagicMock(spec=PersonProtocol)

# ❌ Test depending on concrete class
def test_something(person: Person) -> None: ...
```

## Benefits

1. **Dependency Injection**: Easy to swap implementations
2. **Testing**: Mock dependencies without complex setup
3. **AWS/GraphQL Ready**: API layer depends only on protocols
4. **Type Safety**: Compiler catches interface violations
5. **Documentation**: Protocols are living API documentation

## Adding New Entities

When creating a new entity:

1. Define protocol in `entities_protocol.py`
2. Add testing protocol if needed
3. Implement with `@override` decorators
4. Create `Testable*Protocol` in `test_protocols.py`
5. Update mock factory in `test_utilities.py`

## Further Reading

- PEP 544: Protocols (structural subtyping)
- MyTower Architecture Doc (`notes/control_loop.md`)
- Test Utilities Demo (`tests/test_utilities_demo.py`)
