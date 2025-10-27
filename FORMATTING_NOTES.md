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
- **Status**: Should pass (uses custom X303 plugin)
- **Custom plugin**: `flake8_max_blank_lines` enforces the custom blank line rules
- **Configuration file**: `.flake8`
- **Suppressions**:
  - `E303`: Built-in blank line check (replaced by custom X303)
  - Other formatting rules as documented in `.flake8`

## Summary of Changes

### Configuration Files Modified
1. **pyproject.toml**:
   - Added note to `[tool.black]` explaining the intentional conflict
   - Updated `[tool.ruff.lint].ignore` to suppress `UP046` and `I001`

2. **.vscode/settings.json**:
   - Added comment explaining Black's blank line formatting conflicts
   - Documents that Black's E30x errors should be ignored

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
   python -m flake8 mytower  # Should pass (if custom plugin is active)
   ```

## Rationale

The custom blank line rules provide:
- Enhanced visual separation for large, complex functions (>5 lines)
- Standard PEP8 compliance for small utility functions (≤5 lines)
- Consistent formatting across the codebase
- Improved code readability and navigation

These rules are intentionally configured and should be maintained across the project.
