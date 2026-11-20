# Handoff

Last updated: 2026-11-20. Update this file at the end of any session that leaves work in flight.

## Start here

1. **#191 is next, and its first piece is the owner's to write.** The branch `191-validate-mutation-input` is
   pushed, cut from `main` at `46a8515`, with no commits yet. The brief is under "Next issue: #191" below.
2. **#196 is open and green**: the CLAUDE.md rules on learning versus tedium and on briefing tests. Read
   it before working; it changes who writes what.
3. After #191: the rest of #162 (see "After #191").

## Where things stand

CI runs on every PR and every push to `main`: `pytest` on Python 3.12 and 3.13, on Ubuntu and on Windows,
plus `flake8 and mypy`. All five are required checks in the **Protect Main** ruleset; the two Windows legs
became required on 2026-11-14. The suite is 509 passed. The lint job runs `pre-commit run --all-files`
(`.pre-commit-config.yaml` is the one definition). mypy is a ratchet: the build fails above 205 errors
(`MAX_ERRORS` in `tools/mypy_ratchet.py`). `make lint` and `make check` run the same hooks and ratchet.

The `0.1.0-Alpha` milestone (capital A) holds every `alpha` issue, open and closed.

| PR | Commit | What |
|---|---|---|
| #158 to #192 | | M0 so far; see `git log`. Bodies carry the root causes |
| #193 | `ab714bb` | `pyproject.toml` names the custom LICENSE (`LicenseRef-MyTower-Portfolio`), not GPL-3 |
| #194 | `49fbef6` | All three lock files regenerated: strawberry 0.341.2, fastapi 0.163.1, starlette 1.10.0, pydantic 2.14.3 |
| #195 | `352708a` | Two more cancellation tests wait on an event and assert the generator's log lines (#163 follow-up) |
| #197 | `46a8515` | The four GraphQL input classes declare their fields; 18 mypy errors gone; ratchet 225 to 205 (#162 part 2) |
| #196 | open | CLAUDE.md: the work split is learning versus tedium; tests are briefed before they are written |

## Next issue: #191

The Pydantic validators in `mytower/api/input_types.py` never run on GraphQL input, because no mutation
constructs the model. The owner chose on 2026-11-15 to validate at the API (the issue's option 1), not in
the commands only.

**Split, per #196:** the owner writes the first mutation, because the idiom and the error-handling choice
are new. Claude then does the other seven to match, and the tests, each briefed before it is written.
Suggested first: `add_elevator_bank` in `mytower/api/schema.py`, since it matches the input class the owner
wrote in #197 and has the cross-field check (`max_floor >= min_floor`).

**Decision points for the first mutation:**

1. **How to build the model.** `input.to_pydantic()` works at runtime, but mypy cannot see it either: one
   new `attr-defined` error per call, and it returns `Any`. Constructing it directly is mypy-clean and runs
   the same validators: `AddElevatorBankInputModel(horiz_position=input.horiz_position, ...)`. Measured on
   2026-11-15 in a scratch copy.
2. **What the client sees on bad input.** Left alone, `pydantic.ValidationError` becomes a GraphQL error
   whose message is Pydantic's raw multi-line text, including the input value and an `errors.pydantic.dev`
   URL, and the server logs a full traceback. Options: let it propagate; catch it and raise a short message;
   or a Strawberry error-masking extension. This is the judgment call.
3. The `max_floor < min_floor` check in `model_post_init` also arrives as a `ValidationError`, so one
   handler covers it. Checked 2026-11-20.

**There are eight mutations:** four that queue a command and return its ID (`add_floor`, `add_person`,
`add_elevator_bank`, `add_elevator`) and four `_sync` versions that call `GameBridge` directly.

**Done when:** all eight validate; the `TODO(#191)` line at the end of the `input_types.py` docstring is
removed or rewritten; tests run real mutations through the schema with a mocked bridge, as the
reproduction in the #191 body does, and show bad input rejected and good input queued; mypy does not rise.

**Out of scope, still true:** the commands check no upper bounds and no bank ID pattern, so the pygame
client, which never goes through GraphQL, is not covered.

## After #191: the rest of #162

205 errors: 4 outside tests, 201 in tests.

- **4 `explicit-any`** on the `class ...Model(BaseModel):` lines in `input_types.py`. The `Any` is
  Pydantic's own. Recommended: `plugins = pydantic.mypy` with `init_forbid_extra = True` and
  `init_typed = True` in `mypy.ini`; measured earlier as removing these 4 and adding nothing. Owner decision.
- **201 in tests.** The owner decided on 2026-11-15 that tests keep `disallow_any_explicit`. By code, on
  2026-11-15 (203 then): `no-untyped-def` 59, `call-overload` 59, `unused-ignore` 30, `call-arg` 28,
  `explicit-any` 15, other 12. By file now: `test_subscription_error_handling.py` 50,
  `test_subscription_timing.py` 46, `test_game_bridge_threading.py` 41, `test_game_bridge_queue.py` 20,
  `test_subscription_integration.py` 18, `test_utilities.py` 12.
- **Settle one pattern first.** Most of the `call-overload` and `call-arg` errors are tests calling a
  Strawberry subscription field as if it were a function; mypy types it as `StrawberryField`. 24 of the 30
  `unused-ignore` sit on a line whose ignore names the wrong code. Agree one fix pattern with the owner,
  then fan out one branch per file. If each branch invents its own, the owner reviews four answers to one
  question. Only one branch changes `MAX_ERRORS`.
- **Then** one small PR lowers it to zero and makes mypy blocking, with the two `mypy.ini` fixes in the
  #162 comments.

## Parked work

- **`type-conversion-tests`**, a local branch only, in the worktree
  `.claude/worktrees/agent-aa9f1cc09634f1888`, commit `697f94c`: `mytower/tests/api/test_type_conversions.py`,
  36 cases for the snapshot converters. Verified on 2026-11-14: 545 passed, flake8 clean, no mypy errors.
  It was written before the briefing rule in #196, so brief the owner on it before opening a PR, and rebase
  it onto `main` (it sits on `ab714bb`). It found two things: `ElevatorBankSnapshot.floor_requests` is
  dropped by the converter (belongs to #138), and the `mock_building_snapshot_gql` fixture in
  `mytower/tests/api/conftest.py` builds GraphQL types with model enums and raw tuples, unlike real
  converter output.

## Owner to-dos

- Merge #196.
- After pulling `main` on each machine: `pip install -r requirements-dev.lock`, since #194 moved the pins.
- On the PC: `rm -rf flake8_max_blank_lines` (an ignored egg-info that shadows the plugin), then
  `pip install -e flake8-max-blank-lines/` and `pre-commit install`. Commit with the venv active.
- Attach #191 to the M1 epic (#120) as a sub-issue, or move it to M0, since it is being done now.
- Decide the stale comment above the Strawberry classes in `input_types.py`: it says "Current version:
  0.245.0+", and the lock pins 0.341.2.

## Decisions the owner makes before the work that depends on them

- **#134**, what a person does on arriving: despawn or pick a new destination. Needed mid-M1.
- **#152**, the multi-player model. Needed at the start of M2, because it shapes `reset()` in #136.
- **#140**, the starting numbers for costs, rent, spawn rates, and day length. Needed at the start of M3.
- **Format Document** has no Python formatter on purpose. The options are none (current), ruff on a
  selection only, or an X303-aware fixer as its own issue. Can stay open past M0.

The plan with dates is the "MyTower Alpha Plan" Gantt chart: https://claude.ai/artifact/34Nqvd5DNTUtK1RW5ngKKF.
It has not been updated for this session's work.

## Good ideas (not filed)

Low priority; no issue on purpose. Pick up when the trigger fires.

- **Replace `strawberry.scalar(cls)` in `mytower/api/unit_scalars.py`.** Five places pass a class, which
  Strawberry reports as deprecated in favour of `StrawberryConfig.scalar_map`. The most likely thing to
  break in a later Strawberry release. Worth an issue before the next lock regenerate.
- **Three empty or no-op tests**, found in the #195 review: `test_subscription_memory_cleanup`
  (`test_game_bridge_threading.py`) cancels a task that has already finished and ends in `assert True`;
  the same file near line 389 cancels a task after awaiting it; `test_subscription_cleanup_on_exception`
  has a 10 ms sleep it does not need. Natural to fix in the mypy branch for each file.
- **`.github/workflows/ci.yml`** comment on the `test` job names only the two Ubuntu checks as required;
  all five are now. One line; fold into the next CI change.
- **A hook that fails on a file-level `# flake8: noqa: CODE`**, so #181 cannot come back: a `pygrep` hook
  matching `^\s*#\s*flake8:\s*noqa:` under `mytower/`.
- **Cache the pre-commit hook repo in CI** (`actions/cache` on `~/.cache/pre-commit`). Not before CI
  minutes or clone flakiness matter.
- **An injectable converter on `Subscription`**, to remove the last `patch` in the subscription tests
  (`test_subscription_handles_convert_snapshot_exception`): a `converter` parameter next to `game_bridge`
  in `Subscription.__init__`, defaulting to `convert_building_snapshot`. A production change in
  `schema.py`. **Check this at the end of M0.**

## Things learned that are not written anywhere else

- **Strawberry's `@...pydantic.input` does not check field names.** A name the Pydantic model lacks becomes
  an extra GraphQL-only field, and the model field it was meant to match leaves the schema with no error.
  mypy catches the misuse in `schema.py`; Pydantic's own `@field_validator("name")` rejects an unknown name
  at import. The `input_types.py` docstring explains the two halves.
- **One unexplained suite failure, 2026-11-15:** one local run on the #195 change reported `1 failed, 508
  passed`; the test was not captured. The suite then passed 44 times in a row and CI passed. Save the output
  of any failing run rather than rerunning blind.
- **Do not load the laptop's CPU** to provoke a flake (stress processes, long suite loops) without asking.
  Like Docker, the laptop's battery and responsiveness are the owner's.
- The repo is public with a custom portfolio-only LICENSE. Commits from 2025-03-18 to #104 (2025-12-01)
  were published under GPL-3 and stay in the history. GitHub has no "public but not cloneable" setting.
- `docker build .` passed on 2026-11-15 on the new server lock, and `import mytower.api.server` works
  inside the image.
- Lock regenerate: follow the header in each lock file. pip 26.1's `freeze` writes some names with
  underscores (`pydantic_core`, `typing_extensions`); that is expected noise in the diff.
- Strawberry executes queries and mutations sent over a graphql-transport-ws socket, not only
  subscriptions. HTTP-only rate limits are incomplete until #159.
- The AWS task runs with a public IP and no load balancer. The rate limiter keys on the rightmost
  `X-Forwarded-For` entry, which is only trustworthy behind one (#160).
- `mypy.ini`: `warn_possibly_undefined` is not a mypy 1.15 option and is ignored. An invalid value anywhere
  in `[mypy]` makes mypy drop the whole section with only a warning, so the error count falls and the
  ratchet still passes. Both are on #162.
- Under Strawberry, `self` in a root-type resolver is the operation's root value, which defaults to `None`.
  Write `getattr(self, '_game_bridge', None)`, not `self._game_bridge`; see the `Subscription.__init__`
  docstring (#128).
- `requirements-server.lock` is for the Docker image; use `requirements-dev.lock` on the PC.
- `httpx2` in the dev requirements is not a typo. It is the pydantic-org successor to httpx, and Starlette's
  TestClient uses it.
- Cloud sessions cannot use GitHub GraphQL; use REST.
- Two of the original 11 issues look stale: #15 and #27. Both are labeled `post-alpha`, not closed.
- Docs layout: guides and design notes in `docs/`, past-session notes in `docs/archive/` (historical).
- Do not run `pre-commit run --all-files` just to check: its fixers rewrite files.
- `docs/subscription_example.py` has 6 flake8 findings and is deliberately not linted.
- `agents.md` became `docs/prompts/design-archaeologist.md` because several agent tools auto-load a root
  `AGENTS.md`, and on macOS and Windows the lowercase name matches.
- The Gantt chart's only source is the artifact itself. Read it back with the Artifact tool before
  changing it; a fresh publish makes a new link.
- `make check` does not run in a git worktree (no `.venv` there). Put the main checkout's `.venv/bin` on
  `PATH` and run `pre-commit run --all-files` and `python tools/mypy_ratchet.py` directly.
- Parallel sub-agents in worktrees suit read-only investigation and drafts; the owner's review is the
  bottleneck, so fan out work that informs a decision, not work waiting on one.
