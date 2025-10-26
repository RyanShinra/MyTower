# Test Utilities Documentation

This document describes the type-safe test utilities introduced to improve test maintainability and type safety in the MyTower project.

## Overview

The test utilities provide three main components:

1. **TypedMockFactory** - Creates properly typed mocks with consistent interfaces
2. **StateAssertions** - Provides clean, readable state validation helpers
3. **BoundaryTestMixin** - Simplifies boundary condition testing

## TypedMockFactory

Creates type-safe mocks that properly implement the protocols/interfaces of the entities they're mocking.

### Usage

```python
def test_with_typed_mocks(typed_mock_factory: TypedMockFactory):
    # Create properly typed mocks
    person_mock = typed_mock_factory.create_person_mock(
        current_floor=5,
        destination_floor=8,
        current_block=15.5,
        person_id="test_person",
        state=PersonState.WALKING
    )

    elevator_mock = typed_mock_factory.create_elevator_mock(
        current_floor=3,
        state=ElevatorState.MOVING,
        passenger_count=7
    )

    building_mock = typed_mock_factory.create_building_mock(
        num_floors=15,
        floor_width=25,
        has_floors=True  # Controls whether get_floor_by_number returns a floor or None
    )
```

### Benefits

- **Type Safety**: All properties and methods are properly typed
- **Consistency**: Standardized mock creation across tests
- **Completeness**: Includes all required methods and properties
- **Flexibility**: Supports overrides for custom behavior

## StateAssertions

Provides clean, readable methods for asserting entity states instead of multiple individual assertions.

### Usage

```python
def test_with_state_assertions(person: Person, state_assertions: StateAssertions):
    # Instead of multiple assert statements:
    # assert person.state == PersonState.IDLE
    # assert person.current_floor_num == 5
    # assert person.current_block_float == 10.0

    # Use one clear assertion:
    state_assertions.assert_person_state(
        person,
        expected_state=PersonState.IDLE,
        expected_floor=5,
        expected_block=10.0
    )

    # Similar for elevators:
    state_assertions.assert_elevator_state(
        elevator,
        expected_state=ElevatorState.ARRIVED,
        expected_floor=7,
        expected_passenger_count=3
    )
```

### Benefits

- **Readability**: Clear intent with descriptive parameter names
- **Maintainability**: Changes to assertion logic happen in one place
- **Better Error Messages**: Descriptive failure messages with context
- **Flexibility**: Optional parameters for partial state checking

## BoundaryTestMixin

Simplifies testing boundary conditions by providing a standard pattern for valid/invalid value testing.

### Usage

```python
class MyTestClass(BoundaryTestMixin):
    def test_boundary_conditions(self, person: Person):
        valid_floors = [1, 5, 10]
        invalid_floors = [-1, 11, 100]

        def set_dest_floor(floor_num: int) -> None:
            person.set_destination(dest_floor_num=floor_num, dest_block_num=10)

        # Tests both valid and invalid values in one call
        self.assert_boundary_validation(
            func=set_dest_floor,
            valid_values=valid_floors,
            invalid_values=invalid_floors,
            exception_type=ValueError
        )
```

### Benefits

- **DRY Principle**: Eliminates repetitive boundary testing code
- **Comprehensive**: Tests both valid and invalid cases
- **Flexible**: Supports any function and exception type
- **Clear Intent**: Separates valid and invalid test cases explicitly

## Migration Guide

### Before (Using Raw MagicMock)

```python
def test_old_way(self):
    mock_person = MagicMock()
    mock_person.current_floor_num = 5
    mock_person.destination_floor_num = 8
    mock_person.state = PersonState.WALKING

    # ... test logic ...

    assert mock_person.state == PersonState.IDLE
    assert mock_person.current_floor_num == 5
    assert mock_person.current_block_float == 10.0
```

### After (Using Typed Utilities)

```python
def test_new_way(self, typed_mock_factory: TypedMockFactory, state_assertions: StateAssertions):
    person_mock = typed_mock_factory.create_person_mock(
        current_floor=5,
        destination_floor=8,
        state=PersonState.WALKING
    )

    # ... test logic ...

    state_assertions.assert_person_state(
        person_mock,
        expected_state=PersonState.IDLE,
        expected_floor=5,
        expected_block=10.0
    )
```

## Fixtures

The following fixtures are available in `conftest.py`:

- `typed_mock_factory: TypedMockFactory` - Factory for creating typed mocks
- `state_assertions: StateAssertions` - State assertion helpers
- `building_factory: Callable[..., Mock]` - Configurable building factory

## Integration with Existing Tests

The utilities are designed to work alongside existing test patterns. You can:

1. **Gradual Migration**: Update tests incrementally
2. **Mix Approaches**: Use utilities where they add value, keep existing patterns where they work
3. **Extend Utilities**: Add new factory methods or assertions as needed

## Future Enhancements

Potential improvements to consider:

1. **Test Data Builders**: Fluent interfaces for complex test object creation
2. **Parameterized Test Helpers**: Utilities for managing test data sets
3. **Assertion Extensions**: Additional domain-specific assertion methods
4. **Mock Validation**: Utilities to verify mock usage and detect unused mocks

## Examples

See `test_utilities_demo.py` for comprehensive examples of all utilities in action.