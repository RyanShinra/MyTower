# Handoff: branch `claude/assess-mytower-modules-Be6cK`

Last updated: 2026-09-18. Update this file at the end of any session that leaves work in flight.

## State of the branch

Five commits ahead of `main`, nothing on `main` that is not here. Working tree clean. Full suite: **498 passed, 0 failed** (was 488 passed, 7 failed on `main`).

| Commit | What |
|---|---|
| `26d12c8` | `docs/ALPHA_ROADMAP.md`: milestones M0–M5 to a playable alpha, linked from README |
| `f08baa1` | Roadmap links each milestone to its GitHub epic |
| `3537674` | **#126** Rate limiting fixed. It had never run: the router overrode `__call__`, which `include_router` never calls. Moved to `run()`, limits bound once, keyed on rightmost `X-Forwarded-For`, GET counted, comment-prefixed mutations classified, WebSocket cap actually enforced |
| `9a435d0` | Lock files regenerated (they predated slowapi). `requirements-dev.lock` added. Dockerfile and `make install` now install from locks |
| (this) | `CLAUDE.md`, this file, Continue rule |

No pull request has been opened. Open one from this branch to `main` when ready; the commits are independent enough to merge as one.

## GitHub state created from the roadmap

- Epics: #119 (M0), #120 (M1), #121 (M2), #122 (M3), #123 (M4), #124 (M5). Each has its checklist as sub-issues.
- 33 new sub-issues #125–#157; 8 pre-existing issues attached to epics; #15 and #27 labeled `post-alpha`.
- Labels: `alpha`, `roadmap:M0` … `roadmap:M5`, `post-alpha`.
- **Not done:** the `0.1.0-alpha` GitHub milestone. The API used could not create milestones. Create it by hand, then filter issues by the `alpha` label and bulk-assign.
- #126 has a comment with the real root cause. It is still open because the fix is on this unmerged branch. Close it when merged.
- #73 was left under its existing parent #72 rather than moved to the M5 epic; it carries the `roadmap:M5` label.

## Verified in this session

- Rate-limit tests pass on both Strawberry 0.285.0 (old server lock) and 0.327.7 (current locks).
- Fresh venvs from `requirements-base.lock` and `requirements-server.lock` import `mytower.api.server`; the server one has no pygame.
- `pip install -r requirements-server.lock` succeeds with the exact Dockerfile command.
- **Not verified:** `docker build .` itself. The sandbox had no docker daemon. Run it locally once; it is expected to pass.

## Things learned that are not written anywhere else

- `httpx2` in the dev requirements is not a typo. It is the pydantic-org successor to httpx by the same author, and Starlette 1.6's TestClient uses it.
- The "KNOWN FAILURE" comments that were in `test_rate_limiting.py` blamed slowapi's hit counting. That was wrong; they have been removed. Trust instrumentation over comments.
- Two of the original 11 issues look stale: #15 ("revisit when object collections are in place") and #27 (European floor numbering). Both are labeled `post-alpha`, not closed.
- `TODO(#123)` in the old server code referenced an issue that did not exist at the time; #123 is now the M4 epic. The TODO was rewritten.
- The Makefile `install` target had pointed at a `requirements.txt` that no longer exists. Fixed.

## Suggested next pick

**#125, add GitHub Actions CI.** The suite is green, so CI can fail on red from day one. After that, the M1 correctness issues in order: #17 (remove_person unwiring), then #130/#131/#132/#133 (bank filtering, elevator hang, protocol gaps, `waiting_passengers`), then #134 (person lifecycle), then #135 (soak test).

The single biggest decision still open is the multi-player model (#152). Everything in M5 depends on it, and it affects how #136 (`NewGameCommand`) should behave.
