# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

"""mypy ratchet: fail if mypy finds more errors than the baseline (#162).

CI and `make typecheck` both run this, so the baseline lives in one place. Lower MAX_ERRORS as #162
burns the count down; at zero, replace this script with plain `mypy mytower/`.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Final

MAX_ERRORS: Final = 243
REPO_ROOT: Final = Path(__file__).resolve().parent.parent


def error_count(summary: str, returncode: int) -> int | None:
    """Read the error count from mypy's last line, or None if it can't be read."""
    found = re.match(r"Found (\d+) errors? in ", summary)
    if found:
        return int(found.group(1))
    return 0 if returncode == 0 else None


def main() -> int:
    # sys.executable is the Python running this script, so the venv's mypy runs, not one on PATH.
    result = subprocess.run(
        [sys.executable, "-m", "mypy", "mytower/"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)

    # mypy exits 0 when clean, 1 when it found type errors, 2 when it failed to run at all.
    if result.returncode > 1:
        print(f"mypy itself failed (exit {result.returncode})", file=sys.stderr)
        return result.returncode

    lines = result.stdout.strip().splitlines()
    summary = lines[-1] if lines else ""
    count = error_count(summary, result.returncode)
    if count is None:
        print(f"could not read the error count from {summary!r}", file=sys.stderr)
        return 2

    verdict = "ok" if count <= MAX_ERRORS else "FAIL"
    report = f"mypy ratchet: {count} errors, limit {MAX_ERRORS} (#162): {verdict}"
    print(report)
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as f:
            f.write(report + "\n")
    return 0 if count <= MAX_ERRORS else 1


if __name__ == "__main__":
    sys.exit(main())
