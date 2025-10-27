# Custom Formatting Rules and Linter Configuration

## Overview
This project uses custom blank line formatting rules that intentionally deviate from PEP8 in specific ways. These rules are enforced by a custom Flake8 plugin.

## Custom Blank Line Rules

### Class Definitions
- **Rule**: Two blank lines before class definitions
- **Standard**: PEP8 compliant ✓
- **Applied to**: All class definitions

### Function Definitions
- **Rule for large functions** (>5 lines in body): Two blank lines before the function
  - **Standard**: Non-PEP8 (PEP8 requires only 1 blank line)
  - **Rationale**: Custom requirement for improved readability of large functions
  - **Applied to**: Functions/methods with more than 5 lines in the body

- **Rule for small functions** (≤5 lines in body): One blank line before the function
  - **Standard**: PEP8 compliant ✓
  - **Applied to**: Functions/methods with 5 or fewer lines in the body

### Decorators and Comments
- **Rule**: Zero blank lines between decorators and their functions
- **Standard**: PEP8 compliant ✓

- **Rule**: Zero blank lines between comments (including TODO comments) and their associated functions
- **Standard**: Ensures comments stay attached to their relevant code

## Linter Configuration and Suppressions

### Black Formatter
- **Status**: Reports formatting conflicts but **should not be applied**
- **Issue**: Black wants to normalize blank lines to PEP8 standard (1 blank line before all functions)
- **Suppression**: Cannot be configured in Black; documented in `pyproject.toml` and `.vscode/settings.json`
- **Recommendation**: Use Black for checking other issues (line length, string formatting, etc.) but **ignore blank line suggestions**
- **Expected output**: `57 files would be reformatted` - This is **expected and intentional**

### AutoPep8
- **Status**: ✓ Passes with no issues
- **Configuration**: Uses default settings from `pyproject.toml`

### Ruff
- **Status**: ✓ Passes with all checks
- **Suppressions added**:
  - `E303`: Too many blank lines (using custom X303 Flake8 plugin instead)
  - `UP046`: Generic class syntax (style preference for clarity)
  - `I001`: Import block sorting (imports organized manually for readability)
- **Configuration file**: `pyproject.toml` under `[tool.ruff.lint]`

### Flake8
- **Status**: ✓ Passes with all checks
- **Custom plugin**: `flake8_max_blank_lines` enforces the custom blank line rules (X303)
- **Configuration file**: `.flake8`
- **Suppressions**:
  - `E301-E306`: Standard blank line checks (replaced by custom rules)
  - `E303`: Too many blank lines (using custom X303 plugin instead)
  - `E712`: Comparison to True/False (explicitly testing bool values in tests)
  - Other formatting rules as documented in `.flake8`

## Summary of Changes

### Configuration Files Modified
1. **pyproject.toml**:
   - Added note to `[tool.black]` explaining the intentional conflict
   - Updated `[tool.ruff.lint].ignore` to suppress `UP046` and `I001`

2. **.vscode/settings.json**:
   - Added comment explaining Black's blank line formatting conflicts
   - Documents that Black's E30x errors should be ignored

3. **.flake8**:
   - Added suppressions for `E301-E306` (blank line checks)
   - Added suppression for `E712` (comparison to True/False)

### Files Formatted
- **57 files** modified with custom blank line rules
- **5 files** modified to attach comments to their functions

## Development Workflow

When running linters:

1. **Black**: Expect to see "would reformat" messages - **DO NOT apply these changes**
   ```bash
   python -m black --check mytower  # Will report conflicts (expected)
   ```

2. **AutoPep8**: Should show no changes needed
   ```bash
   python -m autopep8 --diff mytower  # Should be clean
   ```

3. **Ruff**: Should pass all checks
   ```bash
   python -m ruff check mytower  # Should pass
   ```

4. **Flake8**: Should pass with custom plugin
   ```bash
   python -m flake8 mytower  # Should pass
   ```

## Per-Line and Per-Block Exception Examples

When you need to suppress linter errors for specific lines or blocks of code, use the following syntax for each formatter:

### Flake8 Per-Line Exceptions

```python
# Suppress a single error on a specific line
long_string = "This is a very long string that exceeds the line length limit"  # noqa: E501

# Suppress multiple errors on a specific line
x = {1, 2, 3}  # noqa: E501, E231

# Suppress all errors on a line (use sparingly!)
problematic_line = "something"  # noqa
```

### Flake8 Per-Block Exceptions

```python
# Disable for a section of code (e.g., protocol interface declarations)
# flake8: noqa: E704
class MyProtocol(Protocol):
    def method1(self) -> int: ...
    def method2(self) -> str: ...
    def method3(self) -> bool: ...

# Re-enable after the block (not automatic, just document the end)
# Normal linting resumes here
```

### Black Per-Line Exceptions

Black doesn't support per-line exceptions, but you can disable formatting for blocks:

```python
# fmt: off
custom_formatted_dict = {
    'key1':    'value1',
    'key2':    'value2',
    'longer':  'value3',
}
# fmt: on
```

### Ruff Per-Line Exceptions

```python
# Suppress a single rule on a specific line
from typing import List  # noqa: UP035

# Suppress multiple rules
x = foo()  # noqa: F841, E501

# Type-specific ignore (Ruff-specific syntax)
x = foo()  # type: ignore[assignment]
```

### Ruff Per-File Exceptions

Add to `pyproject.toml`:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/*.py" = ["F841"]  # Allow unused variables in tests
"**/entities_protocol.py" = ["E701", "E702"]  # Allow one-line methods in protocols
```

### Pylint Per-Line Exceptions

```python
# Disable specific rule for one line
long_variable_name = "value"  # pylint: disable=invalid-name

# Disable multiple rules
x = foo()  # pylint: disable=invalid-name,unused-variable
```

### Pylint Per-Block Exceptions

```python
# pylint: disable=invalid-name,too-many-locals
def complex_function():
    VeryLongVariableName = 1
    AnotherLongName = 2
    # ... many more variables
# pylint: enable=invalid-name,too-many-locals
```

### Example: Protocol Interface with Multiple One-Line Methods

```python
# flake8: noqa: E704
# fmt: off
class ElevatorProtocol(Protocol):
    @property
    def elevator_id(self) -> str: ...
    
    @property
    def elevator_state(self) -> ElevatorState: ...
    
    @property
    def current_floor_int(self) -> int: ...
    
    def set_destination(self, destination: ElevatorDestination) -> None: ...
# fmt: on
```

### Example: Switch Statement with Custom Formatting

```python
# fmt: off
match state:
    case State.IDLE:    return "idle"
    case State.ACTIVE:  return "active"
    case State.ERROR:   return "error"
    case _:             return "unknown"
# fmt: on
```

## Rationale

The custom blank line rules provide:
- Enhanced visual separation for large, complex functions (>5 lines)
- Standard PEP8 compliance for small utility functions (≤5 lines)
- Consistent formatting across the codebase
- Improved code readability and navigation

These rules are intentionally configured and should be maintained across the project.
