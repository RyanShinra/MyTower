# Handoff

Last updated: 2026-11-09. Update this file at the end of any session that leaves work in flight.

## Where things stand

As of #164 (`dcf855e`), CI runs on every PR and every push to `main`:
`pytest (Python 3.12)`, `pytest (Python 3.13)`, and `flake8 and mypy`. The suite is 498 passed on
Linux. flake8 is clean and blocking. mypy is a ratchet: the build fails above 243 errors, or if mypy itself fails.

| PR | Commit | What |
|---|---|---|
| #158 | `21b73e2` | Alpha roadmap; rate limiting fixed (#126); installs from lock files; CLAUDE.md |
| #161 | `56ff36d` | "Discuss a fix before implementing it" rule |
| #164 | `dcf855e` | GitHub Actions CI, flake8 cleared, mypy ratchet (#125) |

## Owner to-dos

- Add the three CI job names above as required status checks on `main`. Not set as of 2026-11-09.
- Create the `0.1.0-alpha` GitHub milestone, then bulk-assign issues with the `alpha` label.
- On the PC: put three blank lines before a function and check that VS Code shows X303. If it
  doesn't, add that to #165.

## Next

The plan with dates is the "MyTower Alpha Plan" Gantt chart:
https://claude.ai/artifact/34Nqvd5DNTUtK1RW5ngKKF. In order:

1. Rest of M0: #129, #127, #128, #163, #165, then #162 part 1, the mypy errors outside tests.
2. M1, starting with #132.

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
