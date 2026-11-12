# Formatting Rules and Linters

## The blank-line convention

The project deviates from PEP 8 on blank lines, on purpose:

- **Two blank lines** before a class, and before a function or method whose body is longer than five lines.
- **One blank line** before a function or method of five lines or fewer.
- **No blank line** between a decorator, or a comment that belongs to a function, and that function.

## What the tools check

flake8 is the only linter, run by the pre-commit hook and in CI (`.pre-commit-config.yaml` is the one
definition). mypy runs separately; see CLAUDE.md.

**X303** comes from the project's own plugin, `flake8-max-blank-lines/`. It flags a `def` or `class` line,
at any indentation and including decorated ones, with **more than two** consecutive blank lines before it.
That is all it checks. It does not check:

- the first `def` or `class` in a file;
- one blank line versus two by function size; that part of the convention is kept by hand and in review;
- blank lines above a comment: a comment ends the count, so three blank lines followed by a comment and
  then a `def` are not flagged.

It also treats a line inside a triple-quoted string that starts with `def ` or `class ` as a definition.

`.flake8` turns off `E301`-`E306` (X303 replaces them), `D100`-`D104` and `B007`, and allows `E704`
(one-line `def ...: ...`) in the four files listed under `per-file-ignores`.

## No formatter

black, `ruff format` and autopep8 all rewrite blank lines to PEP 8, against the convention above, so none is
installed. In VS Code `editor.defaultFormatter` is `null` for Python and the ruff extension is turned off;
Format Document asking for a formatter is expected.

## Running the checks

```bash
flake8 mytower               # or python -m flake8 mytower; both load the plugin
pre-commit run --all-files   # what the commit hook and CI run
make check                   # flake8 + mypy
```

## Suppressing a check

```python
value = compute()  # noqa: E501        one code, one line; prefer this
value = compute()  # noqa              every code on the line; avoid
```

For a whole file, add it under `per-file-ignores` in `.flake8`, the way the protocol files allow `E704`.

Do not write `# flake8: noqa: E704` in a file. flake8 reads any `# flake8: noqa` comment as "skip this file"
and ignores the codes after it, so it turns off every check in the file, X303 included, not only the code
named and not only the block below it.

For mypy, use `# type: ignore[code]` with the code in brackets (CLAUDE.md).
