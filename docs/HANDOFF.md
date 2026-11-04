# Handoff: branch `claude/assess-mytower-modules-Be6cK`

Last updated: 2026-11-04. Update this file at the end of any session that leaves work in flight.

## State of the branch

Seven commits ahead of `main`, nothing on `main` that is not here. Open as **PR #158**, reviewed, waiting for the owner to merge. Full suite: **498 passed, 0 failed** on Linux (was 488 passed, 7 failed on `main`). On Windows, 497 passed: `test_subscription_cleanup_on_cancellation` fails on timer resolution. That failure is pre-existing on `main` and untouched by this branch.

| Commit | What |
|---|---|
| `26d12c8` | `docs/ALPHA_ROADMAP.md`: milestones M0–M5 to a playable alpha, linked from README |
| `f08baa1` | Roadmap links each milestone to its GitHub epic |
| `3537674` | **#126** Rate limiting fixed. It had never run: the router overrode `__call__`, which `include_router` never calls. Moved to `run()`, limits bound once, keyed on rightmost `X-Forwarded-For`, GET counted, comment-prefixed mutations classified, WebSocket cap actually enforced |
| `9a435d0` | Lock files regenerated (they predated slowapi). `requirements-dev.lock` added. Dockerfile and `make install` now install from locks |
| `13e6ac3` | `CLAUDE.md`, this file, Continue rule |
| `6991975` | `CLAUDE.md` gains "How code gets written", the collaboration rules adapted from AffinityLog; Docker build verified |
| (this) | One-issue-one-branch-one-PR rule; review outcomes recorded; stale roadmap and handoff lines corrected; #159 and #160 filed |

This branch predates the one-PR-per-issue rule and bundles several issues. It is the grandfathered exception. Everything after it follows the rule.

## PR #158 review and merge

- A high-effort `/code-review` ran on 2026-11-04. Outcomes are in a comment on the PR.
- The two serious findings, a spoofable rate-limit key and WebSocket operations bypassing the limits, are not regressions against `main`, where limiting never ran. They are filed as #160 (load balancer, owner's AWS task) and #159 (code). The rest of the code findings are folded into #159.
- GitHub shows the PR as blocked. That is expected: classic protection wants one approval and an author cannot approve their own PR. The owner merges with the admin override, squash or rebase only, since `main` requires linear history.
- After merge: close #126 if `Fixes` did not, delete this branch, and start the next issue on a fresh branch off `main`.

## GitHub state created from the roadmap

- Epics: #119 (M0), #120 (M1), #121 (M2), #122 (M3), #123 (M4), #124 (M5). Each has its checklist as sub-issues.
- 33 new sub-issues #125–#157; 8 pre-existing issues attached to epics; #15 and #27 labeled `post-alpha`. #159 and #160 added under M5 from the PR review.
- Labels: `alpha`, `roadmap:M0` … `roadmap:M5`, `post-alpha`.
- **Not done:** the `0.1.0-alpha` GitHub milestone. The API used could not create milestones. Create it by hand, then filter issues by the `alpha` label and bulk-assign.
- #126 has a comment with the real root cause. It is still open because the fix is on this unmerged branch.
- #73 was left under its existing parent #72 rather than moved to the M5 epic; it carries the `roadmap:M5` label.
- The epic bodies (#119–#124) link to `docs/ALPHA_ROADMAP.md` on this branch. Those links break when the branch is deleted; repoint them at `main` after merge.

## Verified in earlier sessions

- Rate-limit tests pass on both Strawberry 0.285.0 (old server lock) and 0.327.7 (current locks).
- Fresh venvs from `requirements-base.lock` and `requirements-server.lock` import `mytower.api.server`; the server one has no pygame.
- `pip install -r requirements-server.lock` succeeds with the exact Dockerfile command.
- `docker build .` passes (2026-10-14, Docker Desktop on the PC). The image imports `mytower.api.server`, and pygame is absent from it, as the server lock intends.
- mypy and flake8 add nothing new against `main`: mypy has 10 fewer errors, flake8 has 4 fewer findings.

## Things learned that are not written anywhere else

- `httpx2` in the dev requirements is not a typo. It is the pydantic-org successor to httpx by the same author, and Starlette 1.6's TestClient uses it.
- The "KNOWN FAILURE" comments that were in `test_rate_limiting.py` blamed slowapi's hit counting. That was wrong; they have been removed. Trust instrumentation over comments.
- Strawberry executes queries and mutations sent over a graphql-transport-ws socket, not only subscriptions. Any HTTP-only limit is therefore incomplete; see #159.
- The AWS task runs with a public IP and no load balancer. The ALB is deferred on cost until the project is ready to be a portfolio piece, and must be in place before launch; see #160.
- `requirements-server.lock` is Linux-only. `pip freeze` dropped uvicorn's `sys_platform != 'win32'` marker on uvloop, so the lock will not install on Windows. It exists for the Docker image; use `requirements-dev.lock` on the PC.
- Two of the original 11 issues look stale: #15 ("revisit when object collections are in place") and #27 (European floor numbering). Both are labeled `post-alpha`, not closed.
- `TODO(#123)` in the old server code referenced an issue that did not exist at the time; #123 is now the M4 epic. The TODO was rewritten.
- The Makefile `install` target had pointed at a `requirements.txt` that no longer exists. Fixed.

## Suggested next pick

Merge #158 first. Then **#125, add GitHub Actions CI**, on its own branch. With the suite green, CI can fail on red from day one, and every later PR gets a real check. After that, the M1 correctness issues in order: #17 (remove_person unwiring), then #130/#131/#132/#133 (bank filtering, elevator hang, protocol gaps, `waiting_passengers`), then #134 (person lifecycle), then #135 (soak test).

The single biggest decision still open is the multi-player model (#152). Everything in M5 depends on it, and it affects how #136 (`NewGameCommand`) should behave.
