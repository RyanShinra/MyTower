# Handoff

Last updated: 2026-11-12. Update this file at the end of any session that leaves work in flight.

## Where things stand

As of #171 (`f592de7`), CI runs on every PR and every push to `main`:
`pytest (Python 3.12)`, `pytest (Python 3.13)`, and `flake8 and mypy`. The suite is 498 passed on
Linux. The lint job runs `pre-commit run --all-files`, the same hooks a local commit runs
(`.pre-commit-config.yaml` is the one definition): trailing whitespace, final newline, line endings, and
flake8 with the X303 plugin and bugbear (B007 ignored), scoped to `mytower/`. mypy is a ratchet: the build
fails above 243 errors, or if mypy itself fails, and it still runs when the pre-commit step fails.
`make lint` and `make check` run the same hooks.

| PR | Commit | What |
|---|---|---|
| #158 | `21b73e2` | Alpha roadmap; rate limiting fixed (#126); installs from lock files; CLAUDE.md |
| #161 | `56ff36d` | "Discuss a fix before implementing it" rule |
| #164 | `dcf855e` | GitHub Actions CI, flake8 cleared, mypy ratchet (#125) |
| #166 | `392b754` | Handoff refresh |
| #167 | `21f7c76` | Root scratch files archived, moved to `docs/`, or deleted (#129) |
| #170 | `544ca76` | Trailing whitespace and final newlines fixed in 24 non-Python files, so the hooks pass on the whole tree |
| #171 | `f592de7` | flake8 as a pre-commit hook; CI runs the hooks; bugbear and pre-commit added to the dev requirements (#127) |

## In flight: #169 editor parity (branch `claude/cool-ptolemy-hw37pc`, no PR yet)

Two commits are pushed: `46e3a81` (VS Code settings: no Python formatter, ruff off, flake8 severities for
`B` and `X`, mypy extension from the venv, ruff dropped from `extensions.json`, `make format` removed) and
`043c190` (ruff config and dev dependency removed from `pyproject.toml`). Not run in a real editor from the
cloud; the owner is finishing and testing it on the Mac.

What the Mac showed (2026-11-12):

- Mypy squiggles work (mypy-type-checker extension, errors on save). Pylance works on typing.
- **X303 never reaches the Problems panel, and there is no squiggle, on `main` and on this branch alike.**
  So it predates #169. A toast appears on save instead, and `make check` does show the errors.
- Format Document asks for a default formatter. Expected: `editor.defaultFormatter` is `null` on purpose.
  The owner has not yet chosen between no formatter (current), ruff on a selection only, or an X303 fixer
  as its own issue.

Leading hypothesis, **not confirmed**: the Flake8 extension runs `python -m flake8` with `flake8.cwd` at the
repo root, so the `flake8_max_blank_lines/` folder shadows the installed plugin (the CLAUDE.md warning;
this is #165). A flake8 that fails to load a plugin reports no diagnostics at all. To confirm: read the
toast text, or `Output` then `Flake8`, after saving a file with three blank lines before a function; look
for the command line it ran and any plugin-load error. Also check that an unused import shows `F401`.

Candidate fixes, nothing applied: (1) `"flake8.path": ["${workspaceFolder}/.venv/bin/flake8"]` in
`.vscode/settings.json`, so the extension uses the console script (untested; `.venv/bin` is the Mac and
Linux path, the PC needs `.venv/Scripts/flake8.exe`); (2) #165, the src layout, after which the setting
goes away. Then open the PR with `Fixes #169`, run `/code-review`, and update `docs/FORMATTING_NOTES.md`,
which still describes the removed ruff and black config (lines 35, 43-49, 65-70, 84-96, and the per-line
and per-file exception sections from 135).

## Owner to-dos

- Add the three CI job names above as required status checks on `main`. Not set as of 2026-11-09.
- Create the `0.1.0-alpha` GitHub milestone, then bulk-assign issues with the `alpha` label.
- X303 does not show in VS Code on the Mac, so it will not on the PC either; see the #169 section above.
  Add the finding to #165 once the cause is confirmed.
- On the PC: `pip install -r requirements-dev.lock` again (it now has `pre-commit` and `flake8-bugbear`),
  then `pre-commit install`. Commit with the venv active; the hook calls the `flake8` on your `PATH`.

## Next

The plan with dates is the "MyTower Alpha Plan" Gantt chart:
https://claude.ai/artifact/34Nqvd5DNTUtK1RW5ngKKF. In order:

1. Rest of M0: #128, #163, #165, #169, then #162 part 1, the mypy errors outside tests.
2. M1, starting with #132.

Also on the list, with no issue yet: **regenerate `requirements-dev.lock`** as its own small PR, per the
header in the lock file. #171 added `flake8-bugbear` and `pre-commit` by hand-merging 11 lines, so no
existing pin moved. A full regenerate will bump strawberry (0.327 to about 0.341), fastapi and pydantic.
Run the whole suite against the new pins, and note that CLAUDE.md warns the Strawberry API surface moved
between versions. A natural fit with #162.

Decisions the owner makes before the work that depends on them:

- **#134**, what a person does on arriving: despawn or pick a new destination. Needed mid-M1.
- **#152**, the multi-player model. Needed at the start of M2, because it shapes `reset()` in #136.
- **#140**, the starting numbers for costs, rent, spawn rates, and day length. Needed at the start of M3.

## Issues filed after the roadmap

- **#159** Rate-limit queries and mutations sent over WebSocket; smaller limiter hardening. M5.
- **#160** Load balancer in front of the ECS service. Owner task; about $16 a month, so it goes last. M5.
- **#162** Get mypy to zero, lowering the ratchet as it goes. M0. Its comments record two `mypy.ini` problems.
- **#163** The Windows timer-resolution test failure; Windows joins CI after. M0.
- **#165** Move the flake8 plugin to a src layout so `python -m flake8` works. M0.
- **#169** Editor parity: the VS Code ruff extension is the default formatter and shows ruff lint CI never
  checks; `make format` still runs black, which is not in the dev requirements. M0.

## Good ideas (not filed)

Low priority; no issue on purpose. Pick up when the trigger fires.

- **Cache the pre-commit hook repo in CI.** An `actions/cache` step on `~/.cache/pre-commit`, keyed on
  `hashFiles('.pre-commit-config.yaml')`, in the `lint` job. Each run now re-clones `pre-commit-hooks`.
  For a much later date: worth doing when CI minutes or clone flakiness start to matter, not before.
- **A `test_type_conversions.py` for the snapshot converters.** `mytower/api/type_conversions.py` has no
  tests of its own: `convert_building_snapshot` and its floor, elevator, elevator-bank and person helpers
  are only exercised indirectly by the subscription tests, which check the result's type and empty lists,
  not field values. Build a snapshot with known values, convert it, and assert the fields. Tests are
  Claude's by default (CLAUDE.md). **Check this when we reach the end of M0**, before starting M1.
- **An injectable converter on `Subscription`.** One `patch("mytower.api.schema.convert_building_snapshot",
  side_effect=ValueError(...))` remains, in `test_subscription_handles_convert_snapshot_exception`
  (`test_subscription_error_handling.py`). Valid data cannot make the real converter fail, so removing it
  means a production change in `mytower/api/schema.py`: a `converter: Callable[[BuildingSnapshot],
  BuildingSnapshotGQL] = convert_building_snapshot` parameter next to `game_bridge` in
  `Subscription.__init__`, with `building_state_stream` calling `self._convert(...)`. The default keeps
  Strawberry's no-argument construction working. Gets the two subscription test files to no patches at all.
  **Check this when we reach the end of M0**, after #128.

## Things learned that are not written anywhere else

- Strawberry executes queries and mutations sent over a graphql-transport-ws socket, not only
  subscriptions. HTTP-only rate limits are incomplete until #159.
- The AWS task runs with a public IP and no load balancer. The rate limiter keys on the rightmost
  `X-Forwarded-For` entry, which is only trustworthy behind one (#160).
- `mypy.ini`: `warn_possibly_undefined` is not a mypy 1.15 option and is ignored. An invalid value
  anywhere in `[mypy]` makes mypy drop the whole section with only a warning, so the error count
  falls and the ratchet still passes. Both are on #162.
- `requirements-server.lock` is Linux-only: `pip freeze` dropped uvloop's Windows marker. It is for
  the Docker image; use `requirements-dev.lock` on the PC.
- `httpx2` in the dev requirements is not a typo. It is the pydantic-org successor to httpx, and
  Starlette 1.6's TestClient uses it.
- Cloud sessions cannot use GitHub GraphQL; use REST. This session's permission settings blocked
  changing a PR's draft status, so open PRs ready for review, or add a permission rule for it.
- `docker build .` passed on 2026-10-14 from `requirements-server.lock`; the image imports
  `mytower.api.server` without pygame. Not rerun since.
- Two of the original 11 issues look stale: #15 and #27. Both are labeled `post-alpha`, not closed.
- Docs layout since #167: guides and design notes in `docs/`, past-session notes in `docs/archive/`
  (historical, not current). `docs/DI_REFACTORING_REMAINING_WORK.md` stays in `docs/`: it is the
  work list for #128, but it is partly stale. The converter and logger patches the doc never counted
  were removed in their own PR (real snapshots instead of a patched `convert_building_snapshot`, `caplog`
  instead of a patched `schema.logger`). Counts from a grep on 2026-11-11, after that PR:
  - `test_subscription_error_handling.py`: the bridge conversion is done (14 tests use
    `Subscription(game_bridge=...)`). One patch is left on purpose, `schema.convert_building_snapshot` with
    `side_effect=ValueError` in `test_subscription_handles_convert_snapshot_exception`: forcing a converter
    failure that valid data cannot produce needs an injectable converter, a production change.
  - `test_game_bridge_threading.py`: the doc's 14 is right. All 14 tests still build `Subscription()` and swap
    the bridge with `monkeypatch.setattr(game_bridge, "_bridge", ...)`. This is the main work left in #128.
  - `test_subscription_integration.py`: the doc calls it complete, but it still has 3
    `monkeypatch.setattr(game_bridge, ...)` and 9 `Subscription()`. Some may be deliberate (default
    construction); not checked.
- Do not run `pre-commit run --all-files` just to check: its fixers rewrite files. Use `git stash` or
  `git checkout --` afterwards if you did not mean to change them.
- `docs/subscription_example.py` has 6 flake8 findings and is deliberately not linted (the hook is scoped
  to `mytower/`; the files in `docs/` are examples).
- `agents.md` became `docs/prompts/design-archaeologist.md` because several agent tools auto-load a
  root `AGENTS.md`, and on macOS and Windows the lowercase name matches.
- The Gantt chart's only source is the artifact itself. Read it back with the Artifact tool before
  changing it; a fresh publish makes a new link.
- Mechanical M0 issues (#165) suit a Sonnet session. Keep tool output small: `--stat` and a
  narrow `grep`, not whole files or diffs.
