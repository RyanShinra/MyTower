# MyTower — Roadmap to 0.x Alpha

**Goal:** a public URL where a stranger can play a simplified SimTower for ten minutes, make a few decisions that matter, and tell us what was fun and what was broken.

**Status:** draft, September 2026. Nothing below has started. Baseline numbers come from a fresh read of the repo at commit `cba8dde`.

---

## 1. What "Alpha" means here

Alpha is not "feature complete". It is the smallest version that is a *game* rather than a *simulation demo*. Concretely, a player can:

1. Start a new game on an empty lot without restarting the server.
2. Build floors (the six existing floor types), place one or more elevator banks, and add cars to them.
3. Watch people spawn on their own, ride elevators, and reach destinations. People who wait too long leave.
4. Spend money to build and earn money from tenants. Run out of money and the game ends.
5. Pause, change speed, and see money, population, and time in a HUD.
6. Do all of the above in the **web client**. The pygame desktop client stays a developer tool.

Everything else in the old "Future Plans" list (stairs, express elevators, multiple scheduling algorithms, rooms inside floors, building services, save/load, Unreal migration) is **out of scope** for alpha. See section 6.

---

## 2. Where the repo actually is

A full assessment lives in the session that produced this document; the short version:

| Area | State |
|---|---|
| Version | `0.1.0` in `pyproject.toml`, never tagged or released |
| Tests | 495 collected. **488 pass, 7 fail** under Python 3.13. All 7 failures are in `mytower/tests/api/test_rate_limiting.py` (limiter never returns 429). Likely dependency drift, not a logic regression. |
| Coverage | 83% of statements in `mytower/game` per the built-in coverage config. Building 100%, Person 95%, Floor 91%, Elevator 87%, ElevatorBank 85%. |
| CI | **None.** No `.github/` directory. Pre-commit only runs whitespace hooks; black, ruff, mypy hooks are commented out. |
| Open GitHub issues | 11, all from Sept to Nov 2025. Mapped to milestones in section 5. |
| Simulation core | Person and Elevator state machines work. ElevatorBank scheduling works. Demo runs end to end in both clients. |
| Game lifecycle | No new game, no reset, no game over. The only initialization is the hardwired short-building demo. |
| Economy | `STARTING_MONEY` is set once and **never changes**. Money is displayed but nothing costs or earns anything. |
| People | Spawned only by explicit command or demo. On arrival a person goes IDLE forever. Nothing ever removes a person. |
| Web client | Real Svelte app (~1.6k lines). Buttons exist for add floor / bank / elevator / person, but bank placement is hardcoded (`App.svelte:56`) and there are no pause or speed mutations in the GraphQL schema. |
| Server | Single global game instance per process. No auth. Known unbounded dict in `GameBridge._command_results`. Graceful shutdown is documented but unverified. |

The engineering underneath is in good shape: typed command bus, thread-safe bridge between pygame, sim loop, and GraphQL, protocol-driven entities, and a real test suite. The missing pieces are almost all *game* pieces, not infrastructure pieces.

---

## 3. Milestones

Each milestone ends with something you can show someone. Sizes are in **focused days** (a day where MyTower is the only thing you work on). Convert to calendar time using whatever pace is honest for you. The main risk this project has faced is months of zero progress, so milestones are cut small enough that one weekend moves the needle.

### M0 — Make the repo trustworthy (2–3 days)

Nothing here is gameplay. It exists so that every later milestone can be merged with confidence.

- [ ] Add GitHub Actions: Python 3.13, `pytest`, `mypy`, `flake8`. Fail the build on red.
- [ ] Fix or pin the 7 rate-limiting failures. Start by installing from `requirements-server.lock` and rerunning; if green, the fix is pinning `requirements-dev.txt`. If still red, the limiter is not wired into the test client and that is a real bug.
- [ ] Re-enable black and ruff (or flake8) in `.pre-commit-config.yaml`.
- [ ] Finish the dependency-injection cleanup in `docs/DI_REFACTORING_REMAINING_WORK.md` (two test files, documented at ~35 minutes).
- [ ] Move root-level scratch files (`COMMAND_QUEUE_FIX.md`, `UPDATE_CORS.md`, `WEBSOCKET_DEBUGGING.md`, `FORMATTING_NOTES.md`, `REQUIREMENTS_MIGRATION.md`, `DEPLOY_SCRIPT_EDGE_CASES.md`, `Hi, let's continue my project from.txt`, `requirements.txt.backup`, `create`) into `docs/archive/` or delete them.

**Exit:** `main` has a green CI badge and a contributor can run `make check test` from a fresh clone.

### M1 — Simulation correctness (4–6 days)

The core loop must survive an hour of play without corrupting itself. Every item below is a known defect found in the assessment.

- [ ] **#17** `GameModel.remove_person` only pops the dict. Unwire the person from its floor, elevator, and any bank queue. Same audit for `remove_*` on elevators and banks if those exist by then.
- [ ] `Person.find_nearest_elevator_bank` (person.py ~179) picks the nearest bank regardless of whether it serves the destination floor. Filter by served range.
- [ ] `Elevator._update_ready_to_move` (elevator.py ~464–476) can hang when the destination equals the current floor and passengers are aboard. Add the missing transition and a test.
- [ ] `ElevatorBank` calls `VerticalDirection.invert()` (elevator_bank.py ~363) which the protocol does not declare, and unpacks a namedtuple positionally (~213). Declare `invert()` in the protocol, use the field name.
- [ ] `ElevatorBank.waiting_passengers` returns only the UP queue. Rename or return both.
- [ ] **Person lifecycle:** on reaching the destination, either despawn or pick a new destination after a dwell time. Today people go IDLE forever, which makes population meaningless.
- [ ] **Soak test:** a headless pytest that builds a 10-floor building, spawns people at random every few sim-seconds for 10 sim-minutes at max speed, and asserts no exceptions, every queue eventually drains, and every removed person is absent from every floor and elevator.

**Exit:** the soak test passes in CI. That single test is the alpha's safety net.

### M2 — Game lifecycle and configurable building (3–5 days)

- [ ] `NewGameCommand` and `GameModel.reset()`. Demo builder becomes an optional preset, not the only path.
- [ ] Building extents become data, not `0` and a hardcoded width (building.py ~57, person.py ~158, elevator_bank.py ~314). Alpha can keep a fixed lot width, but it must live in one config value.
- [ ] Config extraction issues **#23**, **#29**, **#52**, **#53**: floor heights and floor cap come from config and flow into snapshots so renderers stop hardcoding them. This is what makes a two-block-tall lobby render correctly.
- [ ] Snapshot completeness: elevator references in `model_snapshots.py` (~42) and the building snapshot TODO in `game_model.py` (~295).
- [ ] Add `togglePause` and `adjustSpeed` GraphQL mutations. The commands already exist in `controller_commands.py`; only the schema is missing.

**Exit:** from the web client you can start a fresh game, build, pause, and speed up, all without touching the server.

### M3 — Minimum gameplay loop (6–10 days)

This is the milestone that turns the simulation into a game. Keep every mechanic to its dumbest workable version.

- [ ] **Economy v0.** A build-cost table per floor type and per elevator car. Deduct on build; reject the command if unaffordable. Income tick: each occupied non-lobby floor pays rent every sim-day. Money can go negative; below a threshold the game ends.
- [ ] **Auto-spawn.** A per-floor spawner driven by floor type and a day clock (the model already tracks time). Simplest version: every N sim-seconds each apartment or office floor emits a person with a random destination on another floor. No commute realism yet.
- [ ] **Satisfaction v0.** The angry-color timer already exists on Person. Add a max-wait threshold: past it the person despawns and the floor loses that day's rent. Surface a single 0–100 satisfaction number in the snapshot.
- [ ] **Day/night.** A sim-day length in config, a clock in the HUD, spawn rates that differ between "day" and "night". Two rates is enough.
- [ ] **Win/lose.** Lose when money is below the threshold for a full sim-day. "Win" for alpha is a score screen at a fixed day count (say day 30) showing population, money, and satisfaction.

**Exit:** a ten-minute session contains at least one decision with a visible consequence (overbuilt and broke, underbuilt elevators and tenants left).

### M4 — Player-facing web UI (6–10 days)

- [ ] Click-to-place for floors and elevator banks; choose a bank's floor range instead of the hardcoded `(3, 0, 20)`.
- [ ] HUD: money, population, satisfaction, day and clock, pause and speed controls.
- [ ] Show costs before building; disable buttons you cannot afford.
- [ ] Surface errors in the page instead of the console (already in `TODO.md`).
- [ ] New game and game over screens.
- [ ] Server URL from environment, not hardcoded (**#72**, **#76**).
- [ ] The existing `TODO.md` items from the PR #107 review (focus styles, render order comment, `addFloor` error propagation).
- [ ] Desktop client: either remove the demo-only limits (one bank, eight cars) or accept them and say so. Do not add new features there.

**Exit:** someone who has never seen the code can play from a URL with a one-paragraph explanation.

### M5 — Ship 0.1.0-alpha (3–5 days)

- [ ] **Decide the multi-player model** (see section 4). The recommended alpha answer is one shared tower per server with a scheduled daily reset and a "the tower resets at midnight UTC" note in the UI.
- [ ] Bound `GameBridge._command_results` (TTL or max size) and switch command IDs to a sequential counter. Both are flagged in the code.
- [ ] Verify graceful shutdown against a real `docker stop` (docs exist, behavior unverified).
- [ ] **#73** bind address from config; **#74** WebSocket reconnect in the client.
- [ ] Protect the reset and any admin mutation with a shared token. No user accounts for alpha.
- [ ] Rewrite `README.md` for players: what it is, how to play, known limits, where to report bugs. Move the Python 3.13 rationale into `docs/`.
- [ ] Tag `v0.1.0-alpha`, cut a GitHub release, add a bug-report issue template.

**Exit:** public URL, tagged release, and at least three people outside the project have played it.

---

## 4. Decisions to make before starting

These are not tasks. They change what the tasks are.

1. **One tower or many?** The server runs one global `GameModel`. Two players on the same URL build the same tower. Options: (a) shared tower with periodic reset, chaotic but zero work; (b) one game per WebSocket session, real work in `GameBridge` and the subscription layer; (c) a single-player lock where the second visitor is a spectator. Recommendation: (a) for alpha, (b) for beta.
2. **Web is the product.** The README calls the deployment goal a headless GraphQL service, and the web client is where the UI work is. Freeze the desktop client at "developer tool" so effort is not split.
3. **How simplified is simplified?** The M3 numbers (rent per day, spawn every N seconds, day 30 scoring) are placeholders. Pick them once, put them in `config.py`, tune by playing. Do not design a balance system before there is a game to balance.
4. **Auth.** None for alpha. Rate limiting plus an admin token is the whole security model, and the README should say so.

---

## 5. Open issues mapped to milestones

| Issue | Title (abridged) | Milestone |
|---|---|---|
| #17 | Remove person must unwire floor/elevator ownership | M1 |
| #15 | Revisit when object collections are in place | Close as stale, or fold into M2 snapshot work |
| #23 | Move desktop UI settings into a config protocol | M2 |
| #27 | Basements and European floor numbering | Out of scope, label `post-alpha` |
| #29 | Make the 64-floor cap a config value | M2 |
| #52 | Floor height should come from FloorSnapshot | M2 |
| #53 | Create a centering function | M2 |
| #72 | Update Vite IP addresses | M4 |
| #73 | Binding to 0.0.0.0 exposes the server | M5 |
| #74 | Improve WebSocket stability | M5 |
| #76 | GraphQL endpoint as environment variable | M4 |

Suggested new issues: one per unchecked box above, each labeled with its milestone, plus a `0.1.0-alpha` GitHub milestone so progress is visible without reading this file.

---

## 6. Explicitly not in alpha

Stairs and escalators. Express or multi-bank routing decisions by people. Selectable elevator scheduling algorithms. Rooms, tenants as entities, or anything inside a floor. Building services (power, water). Basements (#27). Save and load. User accounts. Per-player game instances. Performance work for large buildings. The C++/Unreal migration. Mobile layout.

If any of these feels essential while building M3 or M4, write down why before adding it. The alpha's job is to find out whether the core loop is fun, and every extra system delays that answer.

---

## 7. Effort summary

| Milestone | Focused days | Demoable outcome |
|---|---|---|
| M0 Trustworthy repo | 2–3 | Green CI |
| M1 Sim correctness | 4–6 | Soak test passes |
| M2 Lifecycle & config | 3–5 | New game from the web client |
| M3 Gameplay loop | 6–10 | Decisions with consequences |
| M4 Web UI | 6–10 | Playable from a URL |
| M5 Ship | 3–5 | Tagged public alpha |
| **Total** | **24–39** | |

At one focused day a week that is six to nine months. At three a week it is two to three months. Order matters more than pace: M0 and M1 first, because everything after them is built on a loop that currently leaks state.
