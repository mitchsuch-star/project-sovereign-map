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

# France ACTIVELY sues for peace (WO slice 5) — the bilateral-peace path:
.venv/Scripts/python.exe tools/playtest_driver.py --turns 20 --diplomacy propose --fresh

# Live-parse (Anthropic) instead of the mock parser — costs real tokens:
.venv/Scripts/python.exe tools/playtest_driver.py --llm anthropic --script ... --fresh

# Snapshot saves at chosen turns (how the fixtures are made):
.venv/Scripts/python.exe tools/playtest_driver.py --turns 20 --save-at 10,20 --name snap --fresh
```

Useful flags: `--seed <name>` (campaign seed, default `historical`) ·
`--objection trust|insist|compromise` · `--diplomacy decline|accept|first|propose`
(there is no `--ultimatum` flag — `defy` is the policy default, stamped into
every run's `meta.json`)
· `--cheats` (arms DEBUG_MODE so `cheat …` commands work) · `--strict`
(unknown blocking shapes fail the run, exit 3) · `--verbose` (backend
console to stdout instead of `server_console.log`) · `--archive` (copy
`digest.md` + `meta.json` to `docs/audits/playtest_digests/<name>/` — the
committed record a memo may cite).

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

> **⚠ `turns` keys are the driver's own 1-based LOOP INDEX, not world
> turn numbers** (PC15-H — this cost one probe run). With `--from-save`
> the world may already be at turn 20 while the script's `"1"` fires on
> the first loop; blocking popups answered mid-loop can also let the
> world turn drift ahead of the index. Anchor a script to loop order,
> never to the calendar; the digest prints both.

### Known-bad digests (read this before trusting an old run)

Two harness defects were found by the Aug-16 win campaign and fixed then;
both had degraded **every earlier** unattended evaluation:

- **The enemy-phase attack counter always read `0`.** The verb lives at
  `row["ai_action"]["action"]`; the driver read `row["action"]`, which
  does not exist. Any digest dated **before Aug 16, 2026** reports
  `0 attacks` regardless of what the AI did — do not draw conclusions
  about AI aggression from one.
- **Interrupts raised during end-turn were invisible** (NPC-16), so a
  marshal under a strategic order could freeze and take the turn loop
  with him. Runs that stalled at a fixed `current_turn` were hitting
  this, not a game hang.

**Four more were found by the Aug-16 weird campaigns and fixed Aug 21, 2026
(WO-H slice 1 — every digest dated before Aug 21 carries all four):**

- **WO-H1 — ceremonies "succeeded" that never executed.** `_option_id`
  could not read `action`-keyed options (the ally-entry review's shape), so
  the driver's literal-`"confirm"` fallback answered a word the endpoint's
  keyword list does not contain. The World Burns arm ran **fifteen complete
  declare-war ceremonies and declared war on ZERO nations**, every one
  logged as a success. Any pre-Aug-21 digest's record of a multi-stage
  ceremony (declare-war, ally-entry, settlement confirm) may describe a
  campaign that never happened — verify against the run's own save.
- **WO-H2 — the `battles` counter was blind** to autonomous jealousy
  attacks (`jealousy_attacks[*]`, a key the driver never read) and to
  enemy-phase battle rows. The Pacifist arm's centrepiece — 11 autonomous
  attacks, 12 battles — was structurally invisible to its own digest.
  Pre-Aug-21 `battles` counts are undercounts; `0` means nothing.
- **WO-H3 — the estate stage wedged the campaign.** `pending_capture_choice`
  arrives as a bare `True` with the detail on the sibling `capture_data`;
  the driver lost the `stage`, answered the ESTATE question with the
  plunder/secure token, the executor refused **without clearing**, and every
  later command returned *"You must decide the fate of…"*. A pre-Aug-21 run
  that ends `blocked` after a capture may be this, not an engine lock.
- **Run-to-run nondeterminism.** The module RNG was never seeded — the same
  script at the same seed ended at **30 / 28 / 27 provinces** across three
  invocations. **No pre-Aug-21 digest is a reproducible measurement**; its
  numbers are one draw, not the value.

A further one is a *reading* trap rather than a defect: a run can finish
`blocked` because the answer policy went in circles, not because the
engine locked. `drain()` now stops on the second identical answer to one
surface and writes `⚠ ANSWER CYCLE` plus an `unknown_blockers` entry —
**an `answer-cycle` entry means the harness gave up, not that the game
is broken.** Check it before filing a P1.

**The method rule (binding, from the WO eval):** *a passing full test suite
is not evidence that a change leaves `BASELINE_SERIES` alone* — the pin
runs in a fresh hash-seeded subprocess, so an in-process suite pass is
vacuous for it. A byte-identity claim requires a real source-edit run
through `_run_series_subprocess`
(`tests/test_ai_intent_threat_migration.py`).

### Determinism (Mode A only) and the archive

Since Aug 21, 2026 (WO-H slice 1) a Mode A mock-parser run is
**deterministic**: the driver reseeds the module RNG at boot and at every
turn boundary from `sha256(f"{seed}:{world_turn}")` (sufficient because the
backend holds zero `random.Random()` instances — all twenty consuming
modules share the module RNG the in-process driver owns), and `main()`
re-execs itself with `PYTHONHASHSEED=0` when the variable is unset. Two
invocations of the same script at the same seed produce **byte-identical
digests** (verified at landing). `meta.json` records the scheme and the
hash seed under `"rng"`.

Scope: **Mode A only, mock parser only.** `--http` (Mode B) drives a
separate server process whose RNG the driver cannot reach, and a
`--llm anthropic` run varies with the live parser — both stamp a
`NONDETERMINISTIC` banner in `meta.json`. Trust the banner.

**The archive is the citable record.** `tools/playtest_runs/` is gitignored
and overwritten — a digest there is a local artifact, not evidence. Run
with `--archive` to copy `digest.md` + `meta.json` to
`docs/audits/playtest_digests/<name>/` (committed). **A memo may only cite
an archived digest** — a memo citing an unarchived digest is citing
nothing (the WO memos' own lesson; their surviving digests were archived
retroactively on Aug 21, 2026).

**Precedence rule (same landing):** an explicit CLI flag beats the
script's own key, which beats the built-in default. The old rule — script
always wins — silently ignored `--seed` (making seed sweeps over committed
scripts impossible) and redirected `--name` into the script's canonical
run dir, where `--fresh` then deleted the original evidence digest (it
cost the Aug-16 `weird-tyrant` and `weird-world-burns` originals, which is
why those two are absent from the retroactive archive).

### The answer policy (what an unattended run does at each fork)

Every default is logged in the digest next to the popup it answered —
an unattended run hides nothing. Defaults: objections → **trust** ·
incoming proposals/settlement offers → **decline** (a robot must not
sign treaties nobody scripted) · capture → **secure**, estate →
**respect** · glorious charge → **restrain** · Talleyrand's objection →
**proceed** · petitions → **first enabled option** (usually the free
acknowledge) · war-purpose gate → **1 = Conquest** (the script ordered
the attack; backing out would contradict it) · ultimatums → **defy** ·
the player's own confirm dialogs → **confirm** · clarification questions
(`awaiting_clarification` — CR-2 asks, naval confirms, pursuit asks) →
**the first offered option**, answered as the typed index "1" so the
server's own interpreter resolves it · the IGR-F letter-book (routine
small-court asks) → **decline**, answered explicitly through
`POST /mailbox/respond` once per turn instead of silently lapsing
(`--diplomacy accept` accepts them; ⚠ an explicit decline is NOT a
lapse — it writes the serialized refusal record and a 3-turn court
cooldown where a lapse wrote none and 2 turns, so a per-decline cadence
shift vs a pre-Aug-21 digest is the harness's doing, not the game's).
Anything unrecognized is
left standing, logged as `⚠ UNKNOWN BLOCKER`, and — if it blocks `end
turn` — the run STOPS with status `blocked` rather than spinning.

### `--diplomacy propose` — the arm that asks (WO slice 5)

Every other policy is REACTIVE: it answers what arrives. Across every WO
campaign that meant the bilateral-peace path was never pressed once, so a
France|Russia war both courts would have signed out of sat open for thirty
turns and no digest could say whether the engine or the harness was at
fault.

`propose` makes France sue. Per turn, before the script's own orders, it
sends **one** overture, round-robin over the courts France is at war with,
choosing off the game's own honest-availability field rather than a copy of
its rules:

* the row's LEADER with `request_terms_state == "available"` →
  `request terms from <court>`
* everyone else → `propose peace with <court>`

Both are golden-corpus phrasings. The overture is sent AFTER the turn's
scripted orders, because it costs 3 DP and takes Talleyrand out of the
country — sending it first made a script's own `propose peace to Austria`
fail for want of points the harness had just spent. The driver keeps typed
diplomacy on purpose (the slice-7 Cabinet redirect lives in `main.gd`,
client-side; `POST /command` is the surface under test).

Incoming is answered as `--diplomacy accept` answers it — an arm that sues
for peace and then declines the peace it is handed measures nothing —
**with one exception: an ULTIMATUM is answered by the `ultimatum` policy
(`defy` by default), never by the diplomacy dial.** It has to be spelled
out because an ultimatum arrives in the same shape as a peace offer (no
`type`, no options), and until August 22 an accepting policy silently
YIELDED to one: measured, Hanover ceded to Prussia with 300g/turn tribute
and 5,000 conscripts, while the run's own `meta.json` said `defy`. Note
also that `propose` signs *whatever* it is handed, not only peace — an
`open_borders` or an `alliance` is accepted with the same word.

⚠ **A defied ultimatum is not a lapsed one.** A lapse plants no pressure
marker; an explicit refusal calls `record_ultimatum_rejection`, the fifth
coalition-threat contributor. That is the driver's stated policy applied
consistently, but it is a harness change to game state — so a run that
receives an ultimatum is not comparable to a pre-August-22 run that let one
lapse.

Measured on the 18-turn `austerlitz` ambient board: **turn 16 WAR →
ARMISTICE with Austria** (from accepting Austria's own offer — France's
peace to Austria was rejected that same turn), **turn 18 WAR → PEACE with
Britain**, and, in that turn's enemy phase, **Russia accepting France's own
Peace Treaty** — the pair the whole arm exists to reach. DP shortage,
per-court cooldowns and flat refusals all land in the digest as evidence
rather than being engineered around: a choice the executor refuses is
printed with its reason and never re-sent, and the driver moves to the next
option. (Before that memory existed, `propose` ended `blocked` on 3 of 7
seeds — the arm spent the DP its own answer then needed.)

**Two digest deltas this arm introduced (both driver-side, both wanted):**

* **The AI's own peace offer is now answered.** It arrives as the
  incoming-proposal POPUP payload (`mailbox_payloads.
  build_pending_envoy_popup_from_terms`, which also renders `counter_offer`,
  `counter_offer_response` and `incoming_ultimatum`) — no `type`, no
  options, but a `dialogue_id` — which the type table and both keyword
  searches missed, so it was logged `(left standing)` seven times in
  eighteen turns, including Russia's answer to France's own overture. It is
  now answered the way the client answers it (a bare `accept`/`reject` plus
  the payload's `dialogue_id`), except for the ultimatum case above.
  ⚠ Same shape as the letter-book's delta: a run that used to LAPSE these
  now refuses them explicitly.
* **A refused answer says so.** The digest used to render a refused answer
  exactly like a signed one — measured on the archived propose run, 16 of
  28 answers were refused (alliance paradox, stale dialogue, insufficient
  DP) and every one printed as `→ accept` / `→ confirm`. Each now carries
  a `↳ refused: …` line with the engine's own words, and `0 (left
  standing)` no longer implies that anything was signed.
* **A stale passthrough is no longer answered twice.** Every POST rebuilds
  the popup passthroughs, so a response generated before an answer lands
  re-carries the dialogue that answer popped; `drain()` now opens each
  chain with `Answerer.begin_post()` and skips a `dialogue_id` already
  answered in that post. Without it, a turn raising a petition AND a
  proposal confirm answered dialogue #27 twice and the cycle guard stopped
  the chain — nine of eighteen turns under `propose`, zero under every
  other policy, which is why it had never been seen.

**No `ANSWER CYCLE` warning is expected any more.** One used to fire on
every long `propose` run and was recorded as a documented reading trap; the
August 22 review measured it and the explanation was wrong. It was ONE
dialogue rendered twice, because the settlement→bilateral carry stamped the
`dialogue_id` on a throwaway copy and returned the un-stamped original — so
the same popup reached Godot with no identity at all. That is fixed at the
producer, the guard's signature now carries the identity, and a skipped
stale passthrough is logged rather than dropped. A surviving `ANSWER CYCLE`
is now a real finding.

Determinism is unaffected: two `propose` runs at the same seed produce
byte-identical digests, and a default-policy digest is byte-identical
across the slice's driver edits.

### Reading a run

- `digest.md` — the read. One block per turn: commands with one-line
  results, battles (`Ney (lost 2,173) vs Mack (lost 7,747) — …`), popups
  + the answers taken, the enemy phase (attack lines, a `verbs:` tally,
  and `🏴` lines for any province that changed hands), `LEDGER` with
  treasury/net/**`provinces N (+d)`**, and the dispatch headline.
- `digest.jsonl` — the query surface (one record per event; `kind` =
  turn/command/battle/popup/enemy_phase/ledger/dispatch/note). The
  `enemy_phase` record carries the FULL action list (nation, verb,
  marshal, message) — the markdown is a summary, the jsonl is not.
- `meta.json` — args, policy, counters, `unknown_blockers`, finish
  status (`completed` / `blocked` / `game-over`).

> **`provinces` is the conquest scoreboard** and the first thing to read
> in any campaign that is trying to gain ground. It is the player's own
> region count (fog-free). The Aug-16 win campaign annihilated Austria's
> army and went 28 → 30 provinces in 23 turns while an ALLY went 3 → 9;
> without this row that never showed up in any digest.
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
# Second server on its own port AND its own save dir — never fight the
# player's 8005 session, and never touch their saves:
SOVEREIGN_PORT=8006 INK_IRON_SAVE_DIR=/tmp/ink_wire .venv/Scripts/python.exe -m backend.main
# then drive it with the same driver, same digest:
.venv/Scripts/python.exe tools/playtest_driver.py --http http://127.0.0.1:8006 --turns 5 --name wire
```

Rules:
- **`SOVEREIGN_PORT` moves BOTH sides** — `backend/main.py` reads it, and
  every Godot script derives its origin from `Utils.backend_url()`, which
  reads the same variable. Launch a paired test client by setting the env
  var before starting Godot.
- ⚠ **ALWAYS set `INK_IRON_SAVE_DIR` for Mode B too.** Mode A sandboxes it
  for you; Mode B does not. A backend started from the repo root writes to
  the real `saves/`, and **merely BOOTING it refreshes `saves/autosave.json`**
  — which is what the main menu's *Continue* row reads. Learned the
  expensive way on Aug 16, 2026: a wire session opened on 8006 to verify
  payloads silently replaced the player's Early-October-1805 autosave with a
  fresh Turn 1. The driver's `--http` banner warns that `/new_game` will do
  this; the boot doing it as well was undocumented.
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
| `PYTHONHASHSEED` | `0` for byte-identity work (M1–M7/BASELINE_SERIES idiom) | `0` (the driver re-execs itself with it when unset; recorded in `meta.json`) |

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

- **Heavy process concurrency can FREEZE a driver child** (seen Aug 21,
  2026: five of ninety sweep children blocked in asyncio's Windows
  socketpair fallback — `accept()` in `_make_self_pipe` — under ~25
  concurrent python processes). This is an OS-level race, not a game or
  driver defect: the frozen run's trajectory was verified a byte-prefix
  of its completed sibling repeat. A wedged child still carries
  `rng.deterministic: true` in `meta.json` — that field describes the
  SEEDING REGIME, not a completion certificate; check `status` before
  citing a run. Keep sweep concurrency modest (`wo_1b_sweep.py --jobs 4`)
  and don't run sweeps while an 18k-test suite is hammering the machine.

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
