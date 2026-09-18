---
description: MyTower project conventions for AI-assisted editing
alwaysApply: true
---

Read `CLAUDE.md` at the repo root before making changes; it is the single source of project conventions. Read `docs/HANDOFF.md` for the state of in-flight work and `docs/ALPHA_ROADMAP.md` for priorities.

Non-negotiables:

- Python 3.13. Strict mypy: no untyped defs, no explicit `Any`, no bare `type: ignore`.
- Blank-line rules are intentionally non-PEP8 (two before functions longer than five lines, one before shorter, none after a decorator or leading comment). Enforced by the `flake8_max_blank_lines` plugin. Do not apply Black's blank-line changes.
- Line length 120.
- Mutate the model only through commands queued on `GameBridge`. Read only through snapshots.
- Tests use `Mock(spec=Protocol)` and the entities' `testing_*` accessors.
- Install from `.lock` files. When a `.txt` changes, regenerate its lock per the header in the lock file.
- Keep the suite green (498 passed at last handoff). Run `pytest --no-cov -q` before committing.
