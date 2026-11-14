# Handoff

Last updated: 2026-11-14. Update this file at the end of any session that leaves work in flight.

## Where things stand

As of #189 (`a302289`), CI runs on every PR and every push to `main`:
`pytest (Python 3.12)`, `pytest (Python 3.13)`, and `flake8 and mypy`. All three are required checks in
the **Protect Main** ruleset since 2026-11-12, so a red PR cannot merge. Since #189 the test job also
runs on Windows, as `pytest (Python 3.12, Windows)` and `pytest (Python 3.13, Windows)`; those two are
not required checks until the owner adds them to the ruleset. The suite is 509 passed on Linux and on
Windows. The lint job runs `pre-commit run --all-files`, the same hooks a local commit runs
(`.pre-commit-config.yaml` is the one definition): trailing whitespace, final newline, line endings, and
flake8 with the X303 plugin and bugbear (B007 ignored), scoped to `mytower/`. mypy is a ratchet: the build
fails above 225 errors (`MAX_ERRORS` in `tools/mypy_ratchet.py`), or if mypy itself fails, and it still
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
| #185 | `dce09d6` | DI test cleanup finished; schema and WebSocket tests for the `self is None` path; blank-line counts are ceilings (#128) |
| #186 | `7b3cb8f` | First-line whitespace fix: one blank line above each class's first method and each short function (no issue) |
| #187 | `c16dd75` | Handoff refresh after #186 |
| #188 | `e485794` | Seven file-level `# flake8: noqa: CODE` comments removed; two `per-file-ignores` added; 14 long lines wrapped (#181) |
| #190 | `ddae93d` | 18 mypy errors outside tests cleared; ratchet 243 to 225 (#162 part 1) |
| #189 | `a302289` | Cancellation tests wait on an event, not a timer; Windows legs join CI (#163) |

## Editor setup (#169, done in #180)

VS Code now shows the same flake8 findings as CI, on open and save (the Flake8 extension does not lint
while typing). If X303 ever goes quiet again, check the Flake8 output log for `FailedToLoadPlugin` first:
one plugin failing to load drops every flake8 diagnostic, not only X303.

Still open, no issue yet: Format Document has no Python formatter on purpose. The options are none
(current), ruff on a selection only, or an X303-aware fixer as its own issue.

## #128 (done in #185)

Worth keeping from it: under Strawberry, `self` in a root-type resolver is the operation's root value,
which defaults to `None`, and `graphql_app` provides none, so Strawberry never constructs `Subscription`.
Writing `self._game_bridge` instead of `getattr(self, '_game_bridge', None)` breaks every real
subscription. `TestSubscriptionThroughSchema` and `TestSubscriptionThroughRouter` now catch that, and
the `Subscription.__init__` docstring explains it. The root cause is also on #128.

The #185 body classifies every patch left in the suite. Two groups are worth converting later: the
converter patches in `test_subscriptions.py` (tests only, like #174) and the `Floor` patches in
`test_building_basic.py` (needs a floor factory on `Building`). The `global_game_bridge` fixture in
`mytower/tests/api/conftest.py` is the one place the module-level bridge is patched.

## Done: first-line whitespace fix (#186, no issue)

Merged as #186 (`7b3cb8f`). It removed 82 blank lines across 45 files; the census now finds none. Nothing
else is pending from it.

**The rule applied.** Blank-line counts are ceilings (CLAUDE.md, Style). On top of that, the owner's
preference: inside a class, at most one blank line before the first method, which should usually be
`__init__`. This preference is guidance, not a written rule; the owner chose not to encode it.

**Scope**, measured over `mytower/` on 2026-11-14:

1. **72 first methods** with two blank lines between the class line, or the class docstring, and the
   method. Reduce each to one. 13 are `__init__`; 59 are other methods, mostly the first test in a test
   class.
2. **10 short functions**, bodies of five lines or fewer with the docstring excluded, that have two blank
   lines before them, across 6 files. Reduce each to one.

**Definitions, for finding them with an `ast` walk:** count blank lines upward from the first decorator
if there is one, else from the `def` line. Body length is `end_lineno` minus the line of the first
statement after any docstring, plus one.

**Leave alone:** blank lines before classes; before long methods other than a class's first; between a
decorator or leading comment and its function. Do not move methods to put `__init__` first: that is not
whitespace.

**Ask the owner first:** test classes have no `__init__`. Proposed: their first test method gets the
same one-blank-line limit.

**Done when:**
- `git diff --ignore-blank-lines --stat` prints nothing, which proves the diff is whitespace only.
- `pytest` passes with the same count as `main`, and `make check` is clean.
- The `ast` census shows zero in both groups. X303 only flags more than two blank lines, so a clean
  `make check` does not prove the fix.

## #163 (done in #189)

The failure was a race in the test, not in `building_state_stream`. The consumer helper slept 1 ms between
items. Windows timers tick about every 15.6 ms, so the test's cancel landed in the helper's own sleep, the
generator sat at its `yield`, and its `finally` did not run before the assertion. The fixed tests wait on an
`asyncio.Event` set on the first item and use a consumer with no sleep of its own
(`_consume_and_signal`), so the only place it can be suspended is inside the generator. The root cause is
in the #189 body.

Two `_consume_stream` helpers with a sleep remain in `test_subscription_error_handling.py`, used at two
call sites that were not reviewed for the same race.

## Next issue: the rest of #162

#190 cleared 18 of the 40 errors outside tests. The ratchet is at 225: 22 outside tests and 203 in tests.
The 22 need the owner's decision before any code; the options, with code, are in the #190 body.

- **18 `attr-defined` in `mytower/api/schema.py`.** The four input classes in `mytower/api/input_types.py`
  have empty bodies under `strawberry.experimental.pydantic.input(..., all_fields=True)`, so mypy sees no
  fields. Strawberry's mypy plugin does not fix this and adds 4 errors. Recommended: declare the fields
  on each class with their real types; the generated SDL is unchanged.
- **4 `explicit-any` on the `class ...Model(BaseModel):` lines in `input_types.py`.** The `Any` is
  Pydantic's own. Recommended: `plugins = pydantic.mypy` with `init_forbid_extra = True` and
  `init_typed = True`, measured at 225 down to 221.
- **#191 belongs with the first decision.** The Pydantic validators never run on GraphQL input, because
  nothing calls `to_pydantic()`. One of its fixes is the same change as an option for the 18 errors.

Then the 203 errors in tests, most of them in five API test files. Before starting, the owner decides
whether tests keep `disallow_any_explicit`. The plan: one branch per file, in parallel, with none of them
touching `MAX_ERRORS`, then one small PR that lowers it to zero and makes mypy blocking. That work also
takes the two `mypy.ini` fixes in the #162 comments.

## Owner to-dos

- Create the `0.1.0-alpha` GitHub milestone, then bulk-assign issues with the `alpha` label.
- Add `pytest (Python 3.12, Windows)` and `pytest (Python 3.13, Windows)` to the required checks in the
  **Protect Main** ruleset, or say that one Windows leg is enough and drop the other from `ci.yml`.
- Attach #191 to the M1 epic (#120) as a sub-issue, if M1 is the right milestone for it.
- On the PC after pulling: `rm -rf flake8_max_blank_lines` (git leaves the ignored egg-info behind and it
  still shadows the plugin), then `pip install -e flake8-max-blank-lines/`. The pull also deletes
  `.claude/settings.local.json`, which is now untracked (#179).
- On the PC: `pip install -r requirements-dev.lock` again (it now has `pre-commit` and `flake8-bugbear`),
  then `pre-commit install`. Commit with the venv active; the hook calls the `flake8` on your `PATH`.

## Next

The plan with dates is the "MyTower Alpha Plan" Gantt chart:
https://claude.ai/artifact/34Nqvd5DNTUtK1RW5ngKKF. In order:

1. Rest of M0: the remainder of #162 (see above), then the lock regenerate and the two end-of-M0 checks
   under "Good ideas".
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
- **#162** Get mypy to zero, lowering the ratchet as it goes. M0. Part 1 done in #190; still open. Its
  comments record two `mypy.ini` problems.
- **#163** Done in #189: the cancellation tests no longer depend on timer resolution; Windows is in CI.
- **#165** Done in #175: the plugin folder was renamed, since a src layout would still have shadowed it.
- **#176** Done in #177: X303 reads the source flake8 passes, not the file on disk.
- **#169** Done in #180: VS Code matches flake8 and CI; no Python formatter; ruff removed.
- **#183** Done in #184: `make check` runs the same mypy ratchet as CI (`tools/mypy_ratchet.py`).
- **#181** Done in #188: the seven file-level `# flake8: noqa: CODE` comments are gone. Only `config.py`
  and `desktop_ui.py` needed a `per-file-ignores` entry, both for E704.
- **#191** The Pydantic input validators never run on GraphQL mutations. The commands still reject some
  bad input when they execute, but check no upper bounds, and the client is not told. Labeled M1.

## Good ideas (not filed)

Low priority; no issue on purpose. Pick up when the trigger fires.

- **A hook that fails on a file-level `# flake8: noqa: CODE`.** A `pygrep` hook in
  `.pre-commit-config.yaml` matching `^\s*#\s*flake8:\s*noqa:` under `mytower/`, so #181 cannot come
  back. The bare `# flake8: noqa` in `test_input.py` does not match. From the #188 review.
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
- `make check` does not run in a git worktree: the Makefile calls `.venv/bin/pre-commit` and
  `.venv/bin/python`, and a worktree has no `.venv`. Put the main checkout's `.venv/bin` on `PATH` and run
  `pre-commit run --all-files` and `python tools/mypy_ratchet.py` directly.
- Parallel sub-agents in worktrees worked for #163, #181 and #162 part 1 on 2026-11-14: one issue each,
  no shared files beyond `entities_protocol.py`, and only one branch allowed to change `MAX_ERRORS`.
- Mechanical M0 issues (#165) suit a Sonnet session. Keep tool output small: `--stat` and a
  narrow `grep`, not whole files or diffs.
