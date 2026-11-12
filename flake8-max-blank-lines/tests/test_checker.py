import ast

from flake8_max_blank_lines import MaxBlankLinesChecker


def _check(source: str) -> list[tuple[int, int, str, type]]:
    # A filename that doesn't exist: the checker must never touch the disk.
    checker = MaxBlankLinesChecker(ast.parse(source), "not-on-disk.py", source.splitlines(keepends=True))
    return list(checker.run())

def test_three_blank_lines_between_functions_reports_x303() -> None:
    results = _check("def f():\n    pass\n\n\n\ndef g():\n    pass\n")
    assert [(row, text[:4]) for row, _, text, _ in results] == [(6, "X303")]

def test_two_blank_lines_is_allowed() -> None:
    assert _check("def f():\n    pass\n\n\ndef g():\n    pass\n") == []

def test_crlf_line_endings() -> None:
    results = _check("def f():\r\n    pass\r\n\r\n\r\n\r\ndef g():\r\n    pass\r\n")
    assert [row for row, _, _, _ in results] == [6]
