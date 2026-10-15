# CLAUDE.md

Guidance for AI assistants and new contributors working in this repo. Read this before touching code. For where the project is headed, see `docs/ALPHA_ROADMAP.md`; for the state of in-flight work, see `docs/HANDOFF.md`.

## What this is

MyTower is a SimTower-inspired elevator and building simulation in Python 3.13. A single `GameModel` runs a frame-based simulation; a typed command bus mutates it; two clients render it: a pygame desktop view (developer tool) and a Svelte web client talking GraphQL and WebSocket subscriptions to a FastAPI/Strawberry server (the product). Deployment target is a headless GraphQL service on AWS.

## Setup

Python 3.13 is the target and 3.12 is the floor (`requires-python = ">=3.12"` in `pyproject.toml`). `typing.override` needs 3.12.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.lock       # exact pins; or requirements-dev.txt for a fresh resolve
pip install -e flake8_max_blank_lines/     # custom flake8 plugin, see Style below
pre-commit install
```

`uv` works too: `uv venv -p 3.13 .venv && uv pip install -r requirements-dev.lock`.

Web client:

```bash
cd web && npm install && npm run dev       # Vite dev server
npm run codegen                            # regenerate src/generated/graphql.ts after schema changes
```

## Run

```bash
python -m mytower.main --demo                        # desktop only, demo building
python -m mytower.main --demo --with-graphql         # desktop + GraphQL on :8000 (hybrid)
python -m mytower.main --demo --headless --port 8000 # server only, what Docker runs
```

Useful flags: `--fail-fast` (raise instead of catch), `--print-exceptions`, `--log-level`, `--log-file`, `--fps`.

## Test, lint, type-check

```bash
pytest                       # pytest.ini adds coverage flags; full suite is ~7s
pytest --no-cov -q           # faster, no coverage output
make check                   # flake8 + mypy
```

- The suite is green at every commit and at handoff (498 passed on Linux; on Windows one subscription-cancellation test fails on timer resolution, a known pre-existing issue). Red *mid-change* is fine when it is explained; see "How code gets written" below.
- mypy is strict (`mypy.ini`): no untyped defs, no explicit `Any`, `warn_unused_ignores`. Some legacy code violates this; do not add new violations, and do not add `type: ignore` without a code in brackets.
- Tests use `Mock(spec=SomeProtocol)`; never bare `MagicMock()`. Entities expose `testing_*` accessors for internal state; use those rather than reaching into private attributes.
- Tests that reload `mytower.api.server` (rate limiting, CORS) do so on purpose so env vars are re-read; keep that pattern if you add config-driven tests.

## Style

- Line length 120. Ruff config is in `pyproject.toml`, flake8 in `.flake8`.
- **Blank lines are non-PEP8 on purpose.** Two blank lines before any function whose body is longer than five lines, one before shorter ones, none between a decorator or leading comment and its function. The `flake8_max_blank_lines` plugin (rule X303) enforces this and `E30x` are disabled. Black will want to reformat; do not let it. Details in `FORMATTING_NOTES.md`.
- Protocol-driven: entities are typed against `mytower/game/entities/entities_protocol.py`, and production vs testing protocols are separate. Add methods to the protocol when you add them to the implementation (a missing `invert()` on the direction protocol was a latent bug).
- Units are wrapped types (`Blocks`, `Meters`, `Time`, `Velocity` in `mytower/game/core/units.py`). Do not pass raw floats where a unit type is expected.
- State machines use `match`/`case` on an enum. Keep transitions explicit; the elevator hang in `READY_TO_MOVE` came from an implicit else.
- Commands (`mytower/game/controllers/controller_commands.py`) validate arguments and return `CommandResult`; they do not raise into callers. New mutations go through a command, then a GraphQL mutation in `mytower/api/schema.py`, then `npm run codegen`.

## Architecture you must not break

- **GameBridge** (`mytower/api/game_bridge.py`) is the only path from any client into the model. Commands are queued and drained on the game thread; never mutate the model from a request handler.
- **Snapshots** are the only path out. GraphQL types in `mytower/api/graphql_types.py` mirror `mytower/game/models/model_snapshots.py` and are kept in sync by hand.
- **Rate limiting** lives in `RateLimitedGraphQLRouter.run()` in `mytower/api/server.py`. Overriding `__call__` on a router does nothing under `app.include_router()`; that was a real bug. Query and mutation limits are bound once to two probe functions; do not decorate per request.
- **Dependencies**: `.txt` files state intent, `.lock` files are what gets installed (`Dockerfile` uses `requirements-server.lock`, `make install` uses `requirements-dev.lock`). When you change a `.txt`, regenerate its lock per the header in the lock file. A change to base means all three.

## Repo map

```
mytower/game/entities/     Building, Floor, Person, Elevator, ElevatorBank (+ protocols)
mytower/game/models/       GameModel, snapshots, snapshot builders
mytower/game/controllers/  GameController, commands
mytower/game/core/         units, types, config, constants
mytower/game/views/        pygame desktop view and renderers
mytower/game/utilities/    demo_builder (the only initialization path today), simulation loop, cli args, logger
mytower/api/               FastAPI app, GraphQL schema/types, GameBridge, rate limiting
mytower/tests/             mirrors the above; api/ has the most tests
web/                       Svelte + TypeScript client
docs/                      roadmap, handoff, design notes (some are historical)
```

Root-level `*.md` files other than README, CLAUDE, and TODO are working notes from past sessions; M0 of the roadmap archives them.

## Working conventions for AI sessions

- Branch work stays on the branch you were given; never push elsewhere.
- Do not open a pull request unless asked.
- Every roadmap checkbox has a GitHub issue under an epic (#119 through #124). Reference the issue number in commits. Comment on the issue with the real root cause when it differs from the issue body, and leave closing to the human.
- Verify claims by running things. Two "known failure" comments and one issue body in this repo were confidently wrong; the fix was found by instrumenting the code.
- Update `docs/HANDOFF.md` at the end of a session that leaves work in flight.

### How code gets written (read this before writing any)

These rules were worked out on the owner's other project, AffinityLog, and learned the hard way there.
They are not preferences to optimise away.

The owner is a senior engineer (C++ and TypeScript primary, Python developing). MyTower is partly a
vehicle for learning professional Python: strict typing, protocols, `match`, the async server. So *how*
the work happens matters as much as what ships.

- **Discuss the approach before building it.** For anything past a trivial edit, propose the plan, name
  the decision points, and wait. Building first pre-empts the owner's input and wastes the time spent
  reading a diff that was never agreed to.
- **Show the code before it lands. The default is to write nothing to the tree.** Put a *locale list*
  in the reply: for each edit, the file, where in it (a line number, or the `def`/`class` it follows),
  and the exact code in a fenced block. New files go in whole. The owner then either types it in or says
  "apply it", and Claude lands it verbatim. Either way the code has been read and understood before it
  is in the tree, which is the point, and a locale list is reviewable in a way a finished diff is not.
  This applies to boilerplate too: typing it is how the Python sticks.
- **Explain the Python where it differs from TypeScript or C++.** A `Protocol` is not an interface,
  `match` is not `switch`, `@override` and `Final` exist for reasons. One sentence on *why* the idiom
  is shaped that way, next to the code, is worth more than the code.
- **The judgment-carrying pieces are the owner's to write.** State-machine transitions, elevator
  scheduling, command validation, what a snapshot exposes. Mark the spot with a `TODO`, name the
  trade-offs, and wait.
- **Claude's by default:** tests (the owner has said so, including writing them first so there is
  something to code against), and mechanical fallout a change already made has decided: a rename's
  call sites, an import that went dead, a protocol method the implementation now needs. When in doubt,
  show rather than land. Landing it and reporting clearly is the fallback, not the default.
- **Consult the linter before saying "run it."** `make check` is the pre-run gate. Reason about the
  installed library's real signatures, not remembered ones: Strawberry moved from 0.285 to 0.327 on
  this branch and its API surface moved with it.
- **A red suite mid-change is fine when the red is explicable.** From the owner's software-testing
  lecturer: *"Some of you seem to think that debugging is like finding the bottom of the hill. Fix one
  thing and the number of errors increases, so you did the wrong thing. Sometimes the number of errors
  goes up, on the way to the correct solution."* Do not split a coherent change into commits chosen to
  keep `pytest` green at every step, and do not narrow a refactor to dodge tests you are about to
  update anyway. Let the count rise, say why it rose, and bring it back down before the commit. What is
  not acceptable is unexplained red, or red nobody noticed.
- **Never start, stop, or restart Docker, and never run the `aws-*` or `deploy-*` scripts.** Docker
  Desktop is a VM and a real battery and memory commitment on a laptop. The AWS scripts spend money and
  touch a live deployment. If a task needs either, say so and hand over the command.
- **A probing question is a real question.** "What's the bonehead case here?" asks for the failure
  mode, not for reassurance.
