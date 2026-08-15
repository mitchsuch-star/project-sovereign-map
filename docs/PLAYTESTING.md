# PLAYTESTING.md — how to playtest Ink & Iron

> **The document of record for driving the game.** Written Aug 15, 2026
> ("make the test easier" session). If you are a future session asked to
> playtest, evaluate, or live-verify anything: **start here, use Mode A
> unless the task needs the wire or the screen.** The old way — hand-driving
> a live server over HTTP and reading raw JSON (the Aug-9 CA9 playtest was
> 108 request/response pairs) — is retired for everything except what
> Modes B/C exist for.

## TL;DR

```bash
# A seeded, unattended, popup-answering 20-turn campaign whose whole
# story lands in ONE readable file:
.venv/Scripts/python.exe tools/playtest_driver.py --turns 20 --name myrun --fresh
# then read: tools/playtest_runs/myrun/digest.md
```

---

## Mode A — the driver (default; in-process, seeded, digested)

`tools/playtest_driver.py` plays the game through the **same HTTP surface
the Godot client uses** (`POST /command` → parser → executor → response
formatting → popup passthroughs) via FastAPI TestClient — no server
process, no port, no stale-backend trap. It answers blocking popups and
dialogues by a **stated policy**, logs every answer, and writes a compact
per-turn digest.

**Why this is the default:** you read `digest.md` (a few KB) instead of a
hundred raw JSON payloads; runs are seeded and reproducible; the player's
real saves are untouchable (the driver sandboxes `INK_IRON_SAVE_DIR`
before the backend import — `/new_game`'s autosave lands in the run dir).

### Commands

```bash
# Ambient observation (France issues no orders — watch Europe act):
.venv/Scripts/python.exe tools/playtest_driver.py --turns 12 --name ambient --fresh

# Scripted campaign:
.venv/Scripts/python.exe tools/playtest_driver.py --script tools/playtest_scripts/smoke_battle.json --turns 8 --fresh

# Start MID-CAMPAIGN from a committed fixture (skip the opening grind):
.venv/Scripts/python.exe tools/playtest_driver.py --from-save tests/fixtures/playtest_saves/fixture_t10_ambient.json --turns 10 --name late --fresh

# Live-parse (Anthropic) instead of the mock parser — costs real tokens:
.venv/Scripts/python.exe tools/playtest_driver.py --llm anthropic --script ... --fresh

# Snapshot saves at chosen turns (how the fixtures are made):
.venv/Scripts/python.exe tools/playtest_driver.py --turns 20 --save-at 10,20 --name snap --fresh
```

Useful flags: `--seed <name>` (campaign seed, default `historical`) ·
`--objection trust|insist|compromise` · `--diplomacy decline|accept|first`
· `--cheats` (arms DEBUG_MODE so `cheat …` commands work) · `--strict`
(unknown blocking shapes fail the run, exit 3) · `--verbose` (backend
console to stdout instead of `server_console.log`).

### Script files

`tools/playtest_scripts/*.json`:

```json
{
  "name": "danube-opening",
  "seed": "historical",
  "llm": "mock",
  "turns": {"1": ["Murat, scout Swabia", "Davout, attack Mack"],
             "3": ["Talleyrand, assess our situation"]},
  "policy": {"objection": "trust", "diplomacy": "decline"}
}
```

Turns not listed just end. The driver always ends the turn after a
turn's list runs.

### The answer policy (what an unattended run does at each fork)

Every default is logged in the digest next to the popup it answered —
an unattended run hides nothing. Defaults: objections → **trust** ·
incoming proposals/settlement offers → **decline** (a robot must not
sign treaties nobody scripted) · capture → **secure**, estate →
**respect** · glorious charge → **restrain** · Talleyrand's objection →
**proceed** · petitions → **first enabled option** (usually the free
acknowledge) · war-purpose gate → **1 = Conquest** (the script ordered
the attack; backing out would contradict it) · ultimatums → **defy** ·
the player's own confirm dialogs → **confirm**. Anything unrecognized is
left standing, logged as `⚠ UNKNOWN BLOCKER`, and — if it blocks `end
turn` — the run STOPS with status `blocked` rather than spinning.

### Reading a run

- `digest.md` — the read. One block per turn: commands with one-line
  results, battles (`Ney (lost 2,173) vs Mack (lost 7,747) — …`), popups
  + the answers taken, enemy-phase attack lines, treasury/net, the
  dispatch headline.
- `digest.jsonl` — the query surface (one record per event; `kind` =
  turn/command/battle/popup/enemy_phase/ledger/dispatch/note).
- `meta.json` — args, policy, counters, `unknown_blockers`, finish
  status (`completed` / `blocked` / `game-over`).
- `server_console.log` — the backend's full console, when you need the
  underlying trace for one moment.
- `saves/` — the sandboxed SAVE_DIR (autosave + `--save-at` snapshots).

### Fixtures (start mid-campaign)

`tests/fixtures/playtest_saves/` — committed, loadable via
`--from-save`:

| file | state |
|---|---|
| `fixture_t10_ambient.json` | turn 10, seed `historical`, ambient France — the boot war developed on its own |
| `fixture_t20_ambient.json` | turn 20, same run — late-war shape (blockade bite, exhaustion, offers) |

Regenerate (after a `FORMAT_VERSION` bump or a serialization change
`from_dict` can't default — or to refresh to a new balance state):

```bash
.venv/Scripts/python.exe tools/gen_playtest_fixtures.py
```

Commit the refreshed JSONs together with whatever motivated the refresh.

---

## Mode B — a live server over HTTP (the wire test)

Use when the thing under test is the wire itself (endpoint shapes,
client/server integration, a bug that only reproduces under uvicorn) —
not for routine campaign evaluation.

```bash
# Second server on its own port — NEVER fight the player's 8005 session:
SOVEREIGN_PORT=8006 .venv/Scripts/python.exe -m backend.main
# then drive it with the same driver, same digest:
.venv/Scripts/python.exe tools/playtest_driver.py --http http://127.0.0.1:8006 --turns 5 --name wire
```

Rules:
- **`SOVEREIGN_PORT` moves BOTH sides** — `backend/main.py` reads it, and
  every Godot script derives its origin from `Utils.backend_url()`, which
  reads the same variable. Launch a paired test client by setting the env
  var before starting Godot.
- **The target server's state IS modified** — `/new_game` refreshes that
  server's autosave. The driver prints this warning; believe it.
- **Stale-backend hygiene:** a failed restart leaves the OLD process
  serving. Before trusting any live result, verify the process StartTime
  (`Get-Process | Where-Object {$_.ProcessName -like "*python*"} |
  Select-Object Id,StartTime`) or hit `GET /test` and check a value you
  just changed. A fresh backend answers what you just built; a stale one
  answers yesterday's build.

---

## Mode C — the full client (the visual pass)

Use for visual sign-offs, popup rendering, map/piece checks — the things
only the screen can verify.

```bash
# Backend (module form is mandatory post-cutover):
.venv/Scripts/python.exe -m backend.main
# Client (the Godot exe is nested one level deep in Downloads):
"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe\Godot_v4.4.1-stable_win64.exe" --path godot-client/project-sovereign
```

- If the player might have their own session open, run the WHOLE pair on
  another port: set `SOVEREIGN_PORT=8006` in the environment of **both**
  processes.
- Desktop automation care: confirm the Godot window (not the user's
  Chrome) is frontmost before any synthetic input; front via
  SetForegroundWindow, never clicks (see the standing memory).
- After ANY `.gd`-touching change: run the parse harness
  (`Godot…exe --headless --quit --path godot-client/project-sovereign
  --script ../../tools/godot_parse_check.gd`, expect EXIT=0) and a
  ~15s headless boot grepping `SCRIPT ERROR` (expect none) — the XR-1
  rule.
- Per-surface screenshot scenes exist for repeatable visual evidence:
  `tools/settlement_popup_screenshot.gd`, `main_menu_screenshot.gd`,
  `tutorial_screenshot.gd`, `naval_diorama_screenshot.gd`. New surfaces:
  copy that pattern (deterministic payload in, PNG out under
  `docs/audits/`). Extend on demand — there is deliberately no
  all-surfaces harness; each visual pass adds the scene it needs.

---

## Environment variables (the complete set that shapes a run)

| var | effect | driver default |
|---|---|---|
| `SOVEREIGN_SEED` | campaign seed (authored variance bands; `historical`/unset = the byte-pinned boot) | `historical` |
| `LLM_MODE` | `mock` (deterministic, free) / `anthropic` (live parse, needs key) | `mock` |
| `SOVEREIGN_PORT` | backend port AND client origin (both read it) | — (in-process) |
| `INK_IRON_SAVE_DIR` | where saves land — the driver sandboxes this per run | run dir |
| `DEBUG_MODE` | `true` arms cheat commands (the shipped default is off) | `false` (`--cheats` flips) |
| `SOVEREIGN_SCENARIO` | explicit scenario path / `none` = bare flag world — the driver POPS it (ambient leaks reshape the boot) | popped |
| `SOVEREIGN_SMOKE_START` | settlement smoke presets — popped by the driver | popped |
| `SOVEREIGN_MAP` | `legacy` = 19-region rollback — popped by the driver | popped |
| `PYTHONHASHSEED` | `0` for byte-identity work (M1–M7/BASELINE_SERIES idiom) | inherit |

Never set `PYTHONIOENCODING` when running tests (fakes 6 subprocess-test
errors — standing memory).

---

## What a playtest session should produce

1. The run directory's `digest.md` (attach or quote from it — never paste
   raw response JSON into a memo again).
2. A short observations memo under `docs/audits/` if the playtest is an
   evaluation (naming idiom: `PLAYTEST_<topic>_<date>.md`), with defects
   routed to `docs/BUG_FIXES.md` and design items to
   `docs/DESIGN_REFINEMENT.md` — the standing routing discipline.
3. If the playtest discharges a visual sign-off, screenshots under
   `docs/audits/` (Mode C pattern).

## Known limits (deliberate)

- The driver's policy plays a PASSIVE, honest France — it is a camera
  with reflexes, not a strategist. Campaign-quality evaluation still
  wants a scripted or hand-driven arc; the driver's job is to make that
  cheap (script file) or to fast-forward to it (fixtures).
- `--llm anthropic` spends real tokens on every sub-gate parse; use for
  parser evaluation, not ambient observation.
- The driver exercises the HTTP surface, not the Godot renderer — Mode C
  owns everything visual, including the popup dtype whitelist in
  `main.gd` (a dialogue type can work on the wire and still not render;
  see the dialogue-popup-wiring memory).
