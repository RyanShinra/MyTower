# Handoff

Last updated: 2026-11-12. Update this file at the end of any session that leaves work in flight.

## Where things stand

As of #184 (`1cd2d46`), CI runs on every PR and every push to `main`:
`pytest (Python 3.12)`, `pytest (Python 3.13)`, and `flake8 and mypy`. All three are required checks in
the **Protect Main** ruleset since 2026-11-12, so a red PR cannot merge. The suite is 505 passed on
Linux. The lint job runs `pre-commit run --all-files`, the same hooks a local commit runs
(`.pre-commit-config.yaml` is the one definition): trailing whitespace, final newline, line endings, and
flake8 with the X303 plugin and bugbear (B007 ignored), scoped to `mytower/`. mypy is a ratchet: the build
fails above 243 errors (`MAX_ERRORS` in `tools/mypy_ratchet.py`), or if mypy itself fails, and it still
runs when the pre-commit step fails. `make lint` and `make check` run the same hooks and the same ratchet.

| PR | Commit | What |
|---|---|---|
| #158 | `21b73e2` | Alpha roadmap; rate limiting fixed (#126); installs from lock files; CLAUDE.md |
| #161 | `56ff36d` | "Discuss a fix before implementing it" rule |
| #164 | `dcf855e` | GitHub Actions CI, flake8 cleared, mypy ratchet (#125) |
| #166 | `392b754` | Handoff refresh |
| #167 | `21f7c76` | Root scratch files archived, moved to `docs/`, or deleted (#129) |
| #170 | `544ca76` | Trailing whitespace and final newlines fixed in 24 non-Python files, so the hooks pass on the whole tree |
| #171 | `f592de7` | flake8 as a pre-commit hook; CI runs the hooks; bugbear and pre-commit added to the dev requirements (#127) |
| #172 | `2346268` | Handoff refresh after #170 and #171 |
| #173 | `d1d01e2` | #128 notes in the handoff corrected |
| #174 | `2d19bc9` | Converter and logger patches replaced in the subscription tests (no issue; ahead of #128) |
| #175 | `9736d29` | Plugin folder renamed to `flake8-max-blank-lines/` so nothing shadows it (#165) |
| #177 | `ec52a6b` | X303 reads the source flake8 passes, not the file on disk (#176) |
| #178 | `437106a` | CI test job installs the plugin; collection had been failing |
| #179 | `fd2ba2c` | `.claude/settings.local.json` untracked and ignored |
| #180 | `fb595f5` | Editor parity: VS Code matches flake8 and CI, no Python formatter (#169) |
| #182 | `779ac9a` | Handoff refresh; CLAUDE.md no longer claims X303 enforces the whole convention |
| #184 | `1cd2d46` | One mypy ratchet script for CI and `make typecheck`, so `make check` passes locally (#183) |

## Editor setup (#169, done in #180)

VS Code now shows the same flake8 findings as CI, on open and save (the Flake8 extension does not lint
while typing). If X303 ever goes quiet again, check the Flake8 output log for `FailedToLoadPlugin` first:
one plugin failing to load drops every flake8 diagnostic, not only X303.

Still open, no issue yet: Format Document has no Python formatter on purpose. The options are none
(current), ruff on a selection only, or an X303-aware fixer as its own issue.

## #128 in flight (branch `128-finish-di-test-cleanup`)

Done on the branch, no PR yet:

- All 14 tests in `test_game_bridge_threading.py` use `Subscription(game_bridge=...)`; no `_bridge`
  monkeypatch is left in that file.
- `docs/DI_REFACTORING_REMAINING_WORK.md` moved to `docs/archive/`; the roadmap points at the new path.
- `test_subscription_integration.py`: two of its three `_bridge` patches removed (owner's edit). Those two
  tests never iterate the generator, and an async generator's body does not run until the first
  `anext()`, so the bridge lookup never happened. `test_multiple_subscription_instances` iterates, so it
  keeps its patch.

Found along the way: under Strawberry, `self` in a root-type resolver is the **root value**, and the
router sets none, so `self` is `None`. Strawberry never constructs `Subscription`. That is why
`building_state_stream` and `game_time_stream` use `getattr(self, '_game_bridge', None)`: writing
`self._game_bridge` raises `AttributeError` on every real subscription, and the suite stays green
because no test subscribes through the schema. Checked by probing `schema.subscribe` on 2026-11-12. The
`Subscription.__init__` docstring (`schema.py`, "Strawberry creates instances ... with no arguments")
was wrong about this; corrected on the branch.

Also done: `TestSubscriptionThroughSchema` in `test_subscription_integration.py` subscribes through
`schema.subscribe(..., root_value=None)` and fails against the `self._game_bridge` version. The
`Subscription.__init__` docstring and the two resolver comments now say why `self` is `None`.

Left before the PR:

1. In the PR body, list each patch the tracking doc never counted as legitimate or worth converting,
   and change none (grep on 2026-11-12): `test_input.py` 10, `test_game_bridge_queue.py` 8,
   `test_subscription_integration.py` 6, `test_subscription_timing.py` 5, `test_building_basic.py` 3,
   `test_subscriptions.py` 3, `test_person_state_machine.py` 2, `test_rate_limiting.py` 1. Still
   unread. Keep the converter patch in `test_subscription_error_handling.py` (see "Good ideas").

## Owner to-dos

- Create the `0.1.0-alpha` GitHub milestone, then bulk-assign issues with the `alpha` label.
- On the PC after pulling: `rm -rf flake8_max_blank_lines` (git leaves the ignored egg-info behind and it
  still shadows the plugin), then `pip install -e flake8-max-blank-lines/`. The pull also deletes
  `.claude/settings.local.json`, which is now untracked (#179).
- On the PC: `pip install -r requirements-dev.lock` again (it now has `pre-commit` and `flake8-bugbear`),
  then `pre-commit install`. Commit with the venv active; the hook calls the `flake8` on your `PATH`.

## Next

The plan with dates is the "MyTower Alpha Plan" Gantt chart:
https://claude.ai/artifact/34Nqvd5DNTUtK1RW5ngKKF. In order:

1. Rest of M0: #128 (in flight, see above), #163, #181, then #162 part 1, the mypy errors outside tests.
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
- **#165** Done in #175: the plugin folder was renamed, since a src layout would still have shadowed it.
- **#176** Done in #177: X303 reads the source flake8 passes, not the file on disk.
- **#169** Done in #180: VS Code matches flake8 and CI; no Python formatter; ruff removed.
- **#183** Done in #184: `make check` runs the same mypy ratchet as CI (`tools/mypy_ratchet.py`).
- **#181** File-level `# flake8: noqa: CODE` comments turn off flake8 for seven whole files, hiding 14
  E501s and a W293. Move them to `per-file-ignores`, then fix the lines. M0.

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
  (historical, not current). The DI tracking doc went to the archive in #128; its patch counts were
  stale by then.
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
