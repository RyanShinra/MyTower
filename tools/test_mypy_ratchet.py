# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

from mypy_ratchet import error_count


def test_plural_errors() -> None:
    assert error_count("Found 243 errors in 19 files (checked 98 source files)", 1) == 243


def test_single_error() -> None:
    assert error_count("Found 1 error in 1 file (checked 98 source files)", 1) == 1


def test_clean_run_is_zero() -> None:
    assert error_count("Success: no issues found in 98 source files", 0) == 0


def test_unreadable_summary_with_errors_is_none() -> None:
    assert error_count("something mypy never prints", 1) is None
