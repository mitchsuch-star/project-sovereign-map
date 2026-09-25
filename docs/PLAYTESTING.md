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
`--objection trust|insist|compromise` · `--diplomacy decline|accept|first|propose` · `--declare-war cancel|proceed`
· `--settlement accept|decline` (GE-V, Sept 25 2026: the league's common-peace
table — `incoming_settlement_offer` + its `settlement_confirm` — on its own
dial; absent it mirrors `--diplomacy`. An arm that signs the pacts and the
bilateral sues it is handed can still refuse the turn-4 table that ends every
war at once) · `--decline-from Hanover,Naples` (GE-V: envoys from the named
courts are refused whatever `--diplomacy` says — the arm conquering Hanover
refuses Hanover's armistice; read off the dialogue's own court fields, so the
player's own confirms are never touched)
· `--missions off|advisor` (IQ-4: `advisor` sends Talleyrand on the missions the
game's own counsel names; `off`, the default, mirrors `--diplomacy` — see
[the Cabinet arm](#--missions-advisor--the-cabinet-arm-iq-4-september-14-2026))
(there is no `--ultimatum` flag — `defy` is the policy default, stamped into
every run's `meta.json`)
· `--stop-on-ending` (GE-2: stop at a MARKED ending — the Verdict, a Humbled
Peace — with status `ending-reached`; a Fall stops the run as `game-over`
regardless) · `--cheats` (arms DEBUG_MODE so `cheat …` commands work) · `--strict`
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

**One more was found by row IQ-6 and fixed Sept 14, 2026 (PR-X4 — every
digest dated before Sept 14 carries it):**

- **The digest never showed a MEDIUM or LOW diplomatic row.** The
  dispatch rail keeps HIGH and CRITICAL only, and nothing else of the
  morning dispatch's `diplomatic_events` reached `digest.md` **or**
  `digest.jsonl`. Measured on the commanded historical arm: 30 of 122
  diplomatic rows printed (all 42 MEDIUM and all 50 LOW dropped); 39 of
  148 on ulm — about three rows in four. Among the dropped types: the
  AI-6 routine intent lines (`intent_hardens` MEDIUM, `intent_eases` and
  `intent_movement_tail` LOW) and `agenda_shift` (MEDIUM, 4–10 a run).
  **The rescore memo's "Stage-F intent lines fired 0 times in twelve
  runs" was this blindness, not the engine** — the producer fires on
  every board and the client prints every row. A pre-Sept-14 digest's
  silence about a MEDIUM/LOW type is not evidence it never fired; since
  IQ-6 the `COURTS` / `DIPLO` lines and the `dispatch_row` records carry
  them (see *Reading a run*).

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

**Byte-identical across hash seeds (IQ-8, September 17, 2026).** Until IQ-8
the honest wording was *byte-identical at one hash seed; same board across
seeds*: measured on 12- and 40-turn commanded runs and 20-turn ambient runs at
`PYTHONHASHSEED` 0, 1, 7 and 12345, every treasury, province, threat and army
figure was identical, and the only thing that moved was the ORDER of a
`strait_open` rail row inside one turn — `naval._tracked_links_for` walked a
frozenset, so the emission order of the strait flips (and the key order of the
saved `fleets["__naval__"]["verdicts"]`) followed `str` hashing. The walk is
sorted now, and `digest.jsonl` at hash seeds 0 and 1 is the same file (pinned:
`tests/test_iq8_the_harness_tells_the_truth.py::TestCrossHashSeedSentinel`). The
re-exec pin stays: a hash-order mechanic the sentinel has not met would still
be pinned to one order, and the sentinel is what would find it.

Scope: **Mode A only, mock parser only.** `--http` (Mode B) drives a
separate server process whose RNG the driver cannot reach, and a
`--llm anthropic` run varies with the live parser — both stamp a
`NONDETERMINISTIC` banner in `meta.json`. Trust the banner.

### Provenance — what a run asked for, what it played, and on what (IQ-8)

PR-D4 (a published table that did not reproduce) could not be root-caused,
because the run behind it had no archive and no `meta.json` of the day could
have answered the question anyway. Since IQ-8 every run's `meta.json` carries
four blocks, and the digest header prints the second and third:

| block | what it holds |
|---|---|
| `requested` | `seed`, `scenario`, `from_save`, `llm` — what the flags, the script and the defaults ASKED for. On a `--from-save` run with no seed asked, `seed` is `""`: the save decides. |
| `resolved` | what the world IS, read after `/new_game` or `/load` returned: `campaign_seed`, `scenario_name`, `sovereign_map`, `regions`, `player_nation`, `boot_turn`, `dice_label` (the label every module-RNG reseed uses), and `env` — the game-shaping variables read AFTER `import backend.main`. A default run requests scenario `""` and resolves `The Third Coalition, 1805`. |
| `platform` | `python`, `implementation`, `os`, `machine`, `pythonhashseed`. |
| `engine_revision` | `git_commit` + `dirty` (scoped to `backend/`, the driver and the map folder) when git can answer, else `"unknown"` / `null`; and always `content_hash` — sha256 over every `backend/**/*.py`, the map registry and the two scenario JSONs, line endings normalised to LF — which needs no git at all. |

The header lines read `- played: board … · campaign seed … · dice …` and
`- platform: CPython 3.13.12 · Windows-… · PYTHONHASHSEED 0 · engine … · content … · driver …`.

Four more rules landed with it (each behind a flip lever in the driver):

* **The save owns its seed.** A `--from-save` run plays the save's campaign
  seed and its module dice follow it. An explicit seed (flag or script key)
  that differs is honoured for the dice only, recorded as
  `resolved.dice_label` beside `resolved.campaign_seed`, and the header carries
  a `⚠ WARNING — two seeds` line naming both. Before IQ-8, `--from-save
  fixture_t10 --seed austerlitz` recorded `"seed": "austerlitz"` while the
  world played `historical`, and a flagless load of a `marengo` save rolled
  `historical` dice — a silent hybrid either way.
* **The driver SETS the board variables; it never pops them.**
  `SOVEREIGN_SCENARIO=""`, `SOVEREIGN_SMOKE_START=""`, `SOVEREIGN_MAP=europe`
  are set before the import. `load_dotenv()` fills every variable that is not
  PRESENT, so the old pop was undone by any repo `.env` that named one; a
  present variable is never overridden. `resolved.env` records what the engine
  actually read.
* **`driver_revision` is LF-normalised.** One commit used to stamp two values
  (CRLF on Windows, LF on Linux). ⚠ **This changed every stamp once**: an
  archive dated before September 17, 2026 carries the RAW-bytes hash. To
  attribute one, hash a commit's driver in the line ending of the machine that
  ran it — `cmd-*` / `fix-cmd-*` (Linux, LF) stamp `9f00997bc24a` = the driver
  of `4094eb4a`; `iq7-*` (Windows, CRLF) stamp `edb714263e80` = the driver of
  `7d10e20c`, which is `56e82b4305cd` normalised.
* **Action points are counted.** `counters.ap_available` (each played turn's
  `actions_remaining` when first seen), `ap_spent` (available − what was left
  when the turn ended; a turn the engine auto-ended ended at 0) and
  `cmd_refused` (orders the backend refused, as the jsonl records them). Fed by
  the turn-start and pre-`end turn` `GET /ledger` reads the driver already
  makes and by every POST response's `action_summary`. Admin actions are a
  separate pool and are not counted.

**The table rule (binding since IQ-8).** A measured table in this page, a memo
or a spec carries, per row: **platform** (OS + CPython version), **engine
commit** (+ dirty), **`PYTHONHASHSEED`**, **the flags beyond the script**, and
**the archived digest names**. A figure with no archive is **UNCITABLE** — it
may be quoted as history, never as a measurement.

**The archive is the citable record.** `tools/playtest_runs/` is gitignored
and overwritten — a digest there is a local artifact, not evidence. Run
with `--archive` to copy `digest.md` + `meta.json` (+ `digest.jsonl`) to
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

### The decision dials (FA slice 17 part f, September 11, 2026)

Nine harness rows closed at once (FA-72/75/78/79/85/89/90/102/N35 — landing
record = the boxed SLICE 17 (part f) block in `BUG_FIXES.md`). What changed
for a reader of digests:

* **The mailbox is read whole.** After the letter-book, every remaining
  `/mailbox` item (majors, armistices, settlement offers) is ACTIVATED and
  drained through the ordinary dialogue arm, and the morning prints
  `LAPSED …` / `ENVOYS WAITING …` lines. Before this Britain's settlement
  offer stood ten consecutive turns unseen and no archived arm could
  ratify a settlement. A digest can now say `RATIFIED …` (what was signed).
* **Three decisions that used to be "display-only" are answered**, by
  action id + `dialogue_id` exactly as the client answers them, on their
  own dials: `--paradox honor|break` (default **honor** — chosen and named:
  France keeps her word, which every archived arm effectively did, and it
  writes no betrayal record; under `decline` the old needle "no" matched
  ho-NO-r_defender and DECLARED WAR), `--rebellion accept|invest|garrison`
  (default accept: spends nothing), `--sabotage confront|overlook`.
* **A disabled option is never pressed.** The `propose` arm used to press a
  greyed "Send as suggested" and log WIN-1's honest refusal as an artefact;
  an all-disabled surface is now left standing WITH the engine's reason.
* **`--redemption` defaults to `grant_autonomy`** (self-expiring, no roster
  change) — `dismiss` was the permanent `destroy_marshal` arm. Both replies
  (`/respond_to_redemption`, `/marshal_petition_response`) are digested with
  `↳ refused:` when the engine refused them. `--petition rotate` cycles the
  enabled arms per kind — OPT-IN (it makes every archived digest
  non-regenerable).
* **`--last-stand first|fight|breakout` and `--contact first|attack|around|
  hold|cancel`** exist; defaults stay `first` (= the historical answers) so
  the archive and the FA-D27 balance measurement stay comparable — a
  recorded deviation from the row's "least state-changing arm".
* **`--reward pay`** types the reward rail's own `action_command` once per
  notification (off by default: it spends the admin AP scripts budget).
* **`--reload-every N`** saves and loads at the turn boundary and writes the
  questions the load RE-RAISED into the digest. Contract: byte-identical to
  the no-reload run MODULO the load lines and any re-raised answer, Mode A
  only.
* **`SCHOOL step N (title) — approximate`** on the tutorial scenario, from a
  display-only backend `tutorial_step` key: the latest step whose turn gate
  the turn has reached — a floor on what the overlay shows, never the
  overlay's own state.
* **`⚠ SCRIPT PRECONDITION`** — a script whose every `land`/expedition line
  is refused is stamped so (digest + `meta.script_precondition_failed`);
  the committed `naval_descent.json` now stages Soult at **Bordelais** (a
  yard outside the Descent's camp set; Normandy was never a yard).
* **`meta.driver_revision`** — a content hash of the driver that produced
  the run. The nine pre-slice `audit-*` digests were NOT re-archived; they
  stand as evidence of the driver they name, and this stamp is the
  attribution going forward. ⚠ Since IQ-8 (September 17, 2026) the hash is
  of the LF-normalised driver; older archives carry the raw-bytes hash (see
  *Provenance* above for how to attribute one).

### The COMMANDED arm and `--declare-war` (FA-S17-D6, September 12, 2026)

**Read this before measuring balance on a scripted arm.** Every pre-Phase-4
"fighting France" script spends **9–22 of 160 action points** over forty turns
and its `turns` map ends at loop 22–30, so `Fr@30` and `Fr@40` on those arms
measure a France that has **stopped being played** — which is why the FA-D27
re-open condition could not be read on them. Two things changed:

* **`tools/playtest_scripts/commanded_full40.json`** — the committed COMMANDED
  arm. Forty loops of four scripted lines (160 lines, 18 of them free
  `status` reads — never "160 of 160 AP", see below): it fights
  the opening campaign, keeps its corps concentrated, recruits, and answers the
  table. Pair it with `--diplomacy accept`. It deliberately never orders an
  attack on a court France has just signed with.
* **`--declare-war cancel|proceed` (default `cancel`)** — the player's OWN
  declaration confirm (`force_declare_war_confirmation`). It was in no policy
  table, so it fell through to the generic diplomacy block, where "Proceed —
  break the treaty" matches none of the accept needles and the fallback took
  `options[0]` — which IS Proceed. **Measured: 9 of 10 Phase-3 runs tore up a
  treaty France had just signed.** An unattended camera does not take an
  irreversible diplomatic act the script never named, so the default is
  `cancel`; **`proceed` reproduces every pre-Phase-4 archived digest**, which is
  the arm to pass when re-generating one. ⚠ **Until IQ-3 (September 14, 2026)
  the flag was DEAD**: it was parsed but never copied into the policy
  (`resolve_policy` now carries every dial, pinned), so every run that passed
  `--declare-war proceed` ran `cancel` — and its `meta.json` said so. A
  script's own `"policy": {"declare_war": "proceed"}` did work.

Measured on the commanded arm, three seeds, boot 28 provinces each — France's
provinces at turn 40, **one row per measurement, every row carrying its
provenance** (the IQ-8 table rule, *Provenance* above). All rows are forty loops
of `commanded_full40.json`, mock parser, Mode A; "flags" are the flags beyond the
script's own keys.

| measurement | historical | austerlitz | marengo | platform | engine | `PYTHONHASHSEED` | flags | archive |
|---|---|---|---|---|---|---|---|---|
| Sept 12, published (FA-S17-D6) | 20 | 24 | 22 | unrecorded | unrecorded | unrecorded | unrecorded | **UNCITABLE — no archive** |
| Sept 12 re-measure (playtest re-score) | 23 | 24 | 21 | Linux, CPython 3.11 | the driver of `4094eb4a` (stamp `9f00997bc24a`); engine commit unrecorded | `0` | `--diplomacy accept` | `cmd-historical`, `cmd-austerlitz`, `cmd-marengo` |
| Sept 12, after PR-1 | 29 | 20 | 21 | Linux, CPython 3.11 | the same driver + the PR-1 fix, uncommitted at run time; engine commit unrecorded | `0` | `--diplomacy accept` | `fix-cmd-historical`, `fix-cmd-austerlitz`, `fix-cmd-marengo` |
| Sept 16, IQ-7 grant (petitions granted) | 28 | 28 | 29 | Windows 11, CPython 3.13 | the tree landing IQ-7, `7d10e20c` (driver stamp `edb714263e80`, CRLF) | `0` | `--diplomacy accept` | `iq7-grant-historical`, `iq7-grant-austerlitz`, `iq7-grant-marengo` |
| Sept 16, IQ-7 refuse | 29 | 29 | 29 | Windows 11, CPython 3.13 | as above | `0` | `--diplomacy accept --client-petition refuse` | `iq7-refuse-historical`, `iq7-refuse-austerlitz`, `iq7-refuse-marengo` |
| **Sept 17, IQ-8** | **28** | **28** | **29** | Windows 11, CPython 3.13.12 | `7d10e20c` + the uncommitted IQ-8 tree (content `457e8f82bc61`, driver `641a9fcf2c43`) | `0` | `--diplomacy accept` | `iq8-cmd-historical`, `iq8-cmd-austerlitz`, `iq8-cmd-marengo` |

⚠ **The first row is UNCITABLE, and PR-D4 is CLOSED as "cause unrecoverable, no
archive"** (`DESIGN_REFINEMENT.md`, IQ-8). No digest, `meta.json` or driver stamp
exists for it, and no `meta.json` of that day could have named its tree, platform or
invocation. What IS measured: the hash seed does not move this board (12- and
40-turn commanded runs at `PYTHONHASHSEED` 0, 1, 7 and 12345 carry identical
figures; *Determinism* above), so the gap between rows 1 and 2 is not hash order.
**The ruling's conclusion survives every row: 0 of 3 seeds below 20 provinces at
turn 40.** Cite a row by its archive, and say which.

The IQ-7 rows answer the satellites' petitions (`--client-petition` absent →
mirrors `--diplomacy accept` = grant): Tyrol ceded to the Kingdom of Italy through a
petition on two seeds, all three satellites held; `refuse` loses all three by turns
21–23. The four IQ-7 levers down (in-process) give **29** on historical, satellites
lost at turns 29–31 (`iq7-control`, same platform and flags). The pre-IQ-7 figure the
IQ-7 memo contrasts against — **29 / 29 / 29** on the post-IQ-3 tree, satellites lost
2 / 3 / 3 by turns 30–33 — was measured and **not archived: UNCITABLE as a table
row**. The IQ-8 row IS the IQ-7 grant board: each `iq8-cmd-*` jsonl holds exactly
the lines of its `iq7-grant-*` twin (729 / 751 / 747, all 40 ledger records
identical) and differs only in two `strait_open` rows — the rail line and its
`dispatch_row` — swapping places inside one turn, which is the naval sort.

⚠ **"four military actions every turn, 160 of 160 AP" was the SCRIPT'S LINE COUNT,
never a measurement** — the driver had no action-point counter until IQ-8, and the
script's 160 lines include 18 free `status` reads. Since IQ-8, `meta.json` counts
them: on the IQ-8 row, **85 / 80 / 76** of
**160 / 160 / 160** action points spent, with
**52 / 51 / 57** of 200 commands refused (`counters.ap_spent`,
`ap_available`, `cmd_refused`). The Sept 12 figures — **81 / 77 / 75** spent — were
hand-summed from the archived end-turn warnings (`cmd-*`) and reproduce exactly from
them; they assume every turn starts at 4 AP, which the counter does not. Refusals
are stance locks, fortification state and a court France has just signed with. A
France played at half strength still holds 20–29 provinces, which strengthens the
ruling rather than weakening it. Do not quote 160/160.

⚠ **Honest limit.** On the historical seed four French marshals are destroyed
between turns 30 and 37, so the arm's last ten turns spend roughly half their
orders on dead men and measure a smaller France than the script intends.
**`Fr@30` is the sounder read on this arm**; a script that re-commissions from
the Marshalate bench would fix it and does not exist yet. ⚠ **Dated by IQ-8:**
this was read off the Sept 12 published run, which has no archive — none of the
archived historical runs in the table (`cmd-historical`, `fix-cmd-historical`,
`iq8-cmd-historical`) logs a destroyed French marshal, so the limit is UNCITABLE
until a run that shows it is archived.

~~⚠ `--declare-war` is INERT on this arm.~~ **STRUCK September 14, 2026
(IQ-3): the identical outcomes were the dead flag, not the script.** With the
flag working, `proceed` answers the confirm when the script's attack orders
run into a court France has just signed with, and France re-declares on
Austria at turn 4–5 on all three seeds (arms B vs C of
`docs/audits/IQ3_COALITION_CADENCE_2026_09_14.md`). `--declare-war proceed`
on this arm is IQ-3's completion board.

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

### `--missions advisor` — the Cabinet arm (IQ-4, September 14, 2026)

Before IQ-4 nothing in the harness ever chose a Talleyrand mission — **0
launches in 360 driven turns** (nine arms × 40) — so a digest could not say
whether the mission mix was dead or merely unasked. `--missions off|advisor`
(default `off`) is the dial that asks.

* **`off` MIRRORS `--diplomacy`.** Talleyrand's mission confirm ("Begin
  mission" / "Not now", and the cancel form "Confirm cancel" / "Continue
  mission") has its own row in the answer table, `mission → missions`, and
  with the dial off it falls through to the diplomacy read — exactly the
  answer it got before the row existed (`decline` takes "Not now", `accept`
  takes "Begin mission"). The `missions` key is written into the policy
  **only when it is set** (flag or a script's `"policy": {"missions": …}`),
  because the digest header prints the policy verbatim: every run that does
  not pass it keeps a byte-identical header.
* **`advisor` follows the game's own counsel** (IQ-4 contract §5.2). It runs
  after the script's orders and BEFORE the `--diplomacy propose` overture (an
  overture takes Talleyrand abroad, which shuts every mission row). When
  Talleyrand is idle it takes the first branch that applies, choosing ONLY
  among Cabinet rows `GET /diplomatic_preview?nation=X` marks `available`,
  and types the wizard's own command (`diplomacy_wizard.gd`
  `_action_to_command`, drift-pinned):
  1. **reassure** an ALLIANCE-state court whose relation is below 50;
  2. **follow the counsel** — a court whose preview carries
     `recommended_mission` (COURT or IMPROVE), smallest ACCEPT gap first, so
     the COURT/IMPROVE choice is the game's, not the harness's;
  3. **gather intel** on the at-war enemy holding the most provinces, if no
     intel mission was launched in the last 8 turns;
  4. **undermine** an allied pair of France's enemies (the confirm answers
     the option naming the ally that is also at war with France).

  Limits: no branch holds the desk more than **12** consecutive turns (it
  recalls through the Cabinet's own `recall_command` and that branch sits out
  the next pick); when the treaty a mission prepared (the best of
  non-aggression / open borders / defensive alliance / alliance on the court
  it chose) reads **ACCEPT (score ≥ 50)** it sends it — and recalls
  Talleyrand only once he is home, because a recall in transit forfeits the
  Court's Favour the treaty was priced on. It never ends a mission it did
  not send. If `/ledger` carries no `cabinet` (the IQ-4 ledger lever down)
  it notes `⚠ MISSION ADVISOR blind` once and sends nothing.

  ⚠ **The advisor arm's dice are not the control arm's.** The previews it
  reads jitter the suggested peace gold on the module RNG, so an advisor run
  diverges from a `--missions off` run at the same seed from its first read.
  It is still deterministic seed-for-seed.

The binding measurement (IQ-4 §5): `--missions advisor --diplomacy decline`,
40 turns, seeds `historical`, `austerlitz`, `ulm` — **≥ 2 distinct mission
types with an applied tick on every seed**; the control arm (no
`--missions`) must still launch **0**.

### Reading a run

- `digest.md` — the read. One block per turn: commands with one-line
  results (a live parse is marked `[anthropic 0.62]`; a mock parse is
  unmarked), battles (`Ney (lost 2,173) vs Mack (lost 7,747) — …`), popups
  + the answers taken, the enemy phase (attack lines, a `verbs:` tally,
  `🏴` lines for any province that changed hands, **and the fog
  sentence — including on a turn where nothing at all was visible**),
  `ORDER` rows for standing-order progress, `LEDGER` with
  treasury/net/**threat**/**`provinces N (+d)`**, the dispatch headline,
  its `RAIL` notices and `LOG` rows for the AI-vs-AI beats no other
  surface carries.
- `MISSION` (IQ-4) — one line per turn **while a Talleyrand mission is
  live**, read off `GET /ledger` `cabinet` (the one-source
  `mission_status`): `- MISSION Courting — Prussia · net +7 a turn ·
  ≈5 turns to +100 at the present rate, barring blowback · beat running`
  (type, court, net relation a turn, the remaining note, and the notice
  rail's last beat when the end-turn response carries the row). The turn a
  mission's end record first appears prints `- MISSION ended: Courting —
  Prussia, relations reached +100` once. An idle desk prints nothing, so a
  run that launches no mission has a byte-identical digest. The advisor's
  own choices print as `MISSION ADVISOR …` notes above the command they
  send.
- `COURTS` and `DIPLO` (IQ-6, Sept 14, 2026) — the rest of the morning
  dispatch, after its `RAIL` and `TURN EVENTS` lines. The rail prints HIGH
  and CRITICAL only; before IQ-6 nothing else of `diplomatic_events` reached
  any digest (see *Known-bad digests*). Now:
  - `- COURTS: <text>` — the AI-6 routine intent narration
    (`intent_hardens`, `intent_eases`, `intent_movement_tail`), one line per
    row, e.g. (measured, commanded historical arm, turn 5) `- COURTS: The
    court of Russia eases over Arbiter of Europe — an ultimatum is now the
    length of its tether.` and the tail `- COURTS: And 3 other courts stir
    at their own designs.` The engine caps these at 2 lines plus one tail a
    dispatch, so there is no cap here.
    Read them as Europe's temperature: which courts are moving, and which
    way.
  - `- DIPLO +N medium/low (<types>)` — one tally a turn of the MEDIUM/LOW
    rows the digest did NOT print (a type seen more than once reads
    `agenda_shift ×2`). Printed only when N > 0. The rows themselves are in
    the jsonl as `dispatch_row`.
  - Every row, of every priority and outside every cap, is in the jsonl as
    `kind: "dispatch_row"` (`dtype`, `priority`, full `text`), and meta.json
    carries the run's per-type total as `dispatch_type_counts`. Count from
    those, never by grepping the markdown.
  - The switch is `THE_DIGEST_READS_THE_WHOLE_DISPATCH` in the driver;
    False reproduces the pre-IQ-6 digest byte for byte.
  - The beat-5 (volte-face) arm is `tools/playtest_scripts/
    volte_court_austria.json`: the commanded arm plus Talleyrand courting
    Austria from loop 5 — run it `--turns 40` (its policy already answers
    the table with `accept`); its digest carries `volte_face` once.
- `vassals` on every `LEDGER` row (IQ-7, Sept 16, 2026) — the satellite web as
  the diplomatic ledger's Vassals tab reads it, e.g. `· vassals Holland 88 ·
  Kingdom of Italy 84 · Switzerland 71` (`vassals none` once the web is gone;
  driver lever `THE_DIGEST_SEES_THE_WEB`). Before IQ-7 the digest showed 0 of
  67 loyalty ticks on a 40-turn commanded arm, which is how a row was filed
  on "0 vassal drama" while three satellites drifted to rebellion.
- `POPUP diplomatic_dialogue: <court>, client_petition #N → grant the petition`
  (IQ-7) — a client's petition, answered by the `--client-petition
  {grant,refuse}` dial (absent → mirrors `--diplomacy`: `accept`/`first`/
  `propose` grant, `decline` refuses). The same petition is echoed once more
  as `(stale passthrough — #N already answered this chain)` — the pre-existing
  mailbox cache echo, IQ7-X5, not a second petition; count petitions by the
  `#N →` lines or by `dispatch_type_counts["client_petition_answered"]`.
- `digest.jsonl` — the query surface (one record per event; `kind` =
  turn/command/battle/popup/enemy_phase/order_progress/ledger/dispatch/
  rail/dispatch_row/campaign_log/mission/note).

  > ⚠ **The `enemy_phase` record is the FOGGED view, not the full action
  > list.** An earlier version of this page said otherwise and it was wrong
  > by a factor of twelve: measured on a 40-turn ambient board, 1,185 raw
  > enemy actions produced 93 visible ones (7.8%), and on 12 of the 40 turns
  > nothing was visible at all. What the driver sees is what the PLAYER sees
  > — which is the point of the instrument, but it means an absence in the
  > digest is not evidence of an absence on the board. Every `enemy_phase`
  > record carries the same keys on both arms — `count`, `attacks`,
  > `captures`, `verbs`, `actions`, `fogged` — so `fogged` says how many
  > courts moved out of sight whether or not anything was visible, and
  > `actions` is always a list. (The first cut wrote `actions=0` on the
  > fogged arm and `actions=[…]` on the visible one, under the same `kind`.)
  > A fog block longer than the cap says how many courts it did not list.
- `meta.json` — args, policy, counters, `unknown_blockers`, finish
  status (`completed` / `blocked` / `game-over` / `ending-reached`), and the run's WORLD:
  `scenario`, `script`, `cheats`, `strict` (added by FA-N89 — 52 archived
  runs record none of them, so their board cannot be reconstructed), and
  `dispatch_type_counts` — every diplomatic row the run's dispatches
  carried, by type, all priorities (IQ-6; absent from every earlier run).

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

| file | state | generated at |
|---|---|---|
| `fixture_t10_ambient.json` | turn 10, seed `historical`, ambient France — the boot war developed on its own | `1aa005a2` (Aug 15, 2026), `tools/gen_playtest_fixtures.py` |
| `fixture_t20_ambient.json` | turn 20, same run — late-war shape (blockade bite, exhaustion, offers) | `1aa005a2` (Aug 15, 2026), same run |
| `fixture_ge2_soil_or_sword.json` | turn 1, seed `historical`, **STAGED** (a direct controller write, not played): every French province but Brittany handed to Austria; France at war with the coalition from the boot, so the soil clock ticks from the first end turn and the Empire falls on the fifth | GE-2 (Sept 25, 2026), `tools/gen_ge2_ending_fixtures.py` |
| `fixture_ge2_chains.json` | turn 1, seed `historical`, **STAGED** through the real `capture_marshal` seam: the Emperor a prisoner of Austria; the chains clock ticks from the first end turn, the captor offers its terms on the clock's turns 1, 4 and 7, and under `--diplomacy decline` the regency falls on the tenth | GE-2 (Sept 25, 2026), same tool |
| `fixture_ge3_pressburg.json` | turn 28, seed `historical`, **STAGED**: after Pressburg and Tilsit — Austria and Russia at peace with France AND every satellite (both latched as beaten courts), Austria's cessions titled by treaty, Hanover/Naples/Portugal held fifteen quiet turns, Bavaria/Saxony/Hesse clients, Prussia allied at relation 30, Britain's ports closed; 55 titled, the Congress summonable | GE-3 (Sept 25, 2026), `tools/gen_ge3_congress_fixtures.py` |
| `fixture_ge3_premature.json` | turn 1, seed `historical`, **STAGED**: exactly 50 titled on the boot war (treaty titles written directly), three great powers at war, no preparation | GE-3 (Sept 25, 2026), same tool |

Not a measurement — a starting state. It is dated by the commit that
generated it because a regeneration changes it: a fixture is the board of the
engine that wrote it, played on by the engine that loads it. A `--from-save`
run plays the save's own campaign seed (IQ-8); both fixtures carry
`historical`.

Regenerate (after a `FORMAT_VERSION` bump or a serialization change
`from_dict` can't default — or to refresh to a new balance state):

```bash
.venv/Scripts/python.exe tools/gen_playtest_fixtures.py
```

Commit the refreshed JSONs together with whatever motivated the refresh.

### The endings on the driver (row EP GE-2, September 25, 2026)

Every ending the campaign can reach has a driver arm, and the digest prints
the END SCREEN's own blocks under it — the date and register, THE VERDICT's
tier and three lines, THE RECORD, THE EXILE's paragraphs — read off the same
payload the client renders (`GET /campaign_end`), so a headless run is
evidence about what the screen says, not only that it fired. The four arms,
archived under `docs/audits/playtest_digests/ge2-*`:

| ending | command | reached |
|---|---|---|
| **The Eagle Falls** (the Emperor dead) | `.venv/Scripts/python.exe tools/playtest_driver.py --seed historical --turns 34 --name ge2-eagle-falls --fresh` | the Fall on turn 31 — the Emperor's remnant annihilated at Burgundy by Britain; the funeral epilogue; status `game-over` |
| **The Eagle in Chains** | `.venv/Scripts/python.exe tools/playtest_driver.py --from-save tests/fixtures/playtest_saves/fixture_ge2_chains.json --turns 13 --name ge2-chains --fresh` | the Fall on turn 10 — Olmütz, Metternich's line; `game-over` |
| **The Empire Without Soil or Sword** | `.venv/Scripts/python.exe tools/playtest_driver.py --from-save tests/fixtures/playtest_saves/fixture_ge2_soil_or_sword.json --turns 8 --name ge2-soil-or-sword --fresh` | the Fall on turn 5 — Fontainebleau and Elba; `game-over` |
| **The Verdict of History** | `.venv/Scripts/python.exe tools/playtest_driver.py --seed austerlitz --turns 46 --name ge2-verdict --fresh --stop-on-ending` | the Verdict on turn 44 — an empire contested; status `ending-reached` |

The two clocks are not reached by the ambient board inside a campaign's
length (GE-1 measured 0 soil-or-sword Falls in nine 46-turn runs), so their
arms start from the STAGED fixtures above — starting states for the ending's
surfaces, not measurements of the game's balance. `--stop-on-ending` ends a
run at a MARKED ending (the Verdict, a Humbled Peace) with status
`ending-reached`; a Fall reports `game-over` as before. A Humbled Peace has no
arm of its own: it is stamped by a settlement the player signs, which no
unattended policy does on purpose (`--diplomacy accept` may, and the digest
prints it the same way when it does).

### The Congress on the driver (row EP GE-3, September 25, 2026)

The digest prints the Congress's clock line (`- CONGRESS …`) every turn it
sits, while it cools down, and once the titled count reaches the summons —
open, or blocked by a named term; the END SCREEN block prints THE IMPERIAL
PEACE with its Congress block. The two §2.8 arms, archived under
`docs/audits/playtest_digests/ge3-*` and pinned DRIVEN in
`tests/test_congress_review_round.py::TestTheArmsDriven`:

| arm | command | reached |
|---|---|---|
| **Pressburg** (win) | `.venv/Scripts/python.exe tools/playtest_driver.py --name ge3-pressburg-historical --seed historical --script tools/playtest_scripts/ge3_pressburg.json --from-save tests/fixtures/playtest_saves/fixture_ge3_pressburg.json --diplomacy accept --stop-on-ending --turns 12 --fresh` | THE IMPERIAL PEACE on turn 36 on seeds historical / ulm / austerlitz / marengo — ascendant; `ending-reached` |
| **Premature** (lose) | `.venv/Scripts/python.exe tools/playtest_driver.py --name ge3-premature-historical --seed historical --script tools/playtest_scripts/ge3_premature.json --from-save tests/fixtures/playtest_saves/fixture_ge3_premature.json --diplomacy decline --turns 10 --fresh` | dissolved on turns 4–6 (a titled province lost; Berlin at war after its warning) on seeds historical / ulm / austerlitz |

Both start from STAGED fixtures — the road to them from the 1805 boot is
GE-V's measurement. Add `--archive` to replace the committed digest.

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

### Recording parser cassettes (IQ-9 — the only path that spends the key)

The live-LLM escalation path is pinned KEYLESSLY by
`tests/test_iq9_keyless_parser_gate.py`: a fake SDK client is bound through
`AnthropicProvider.bind_sdk_client` and serves real `anthropic.types.Message`
objects from `tests/data/parser_cassettes/<id>.json`, keyed on
`(kind, utterance, world)` — never on the prompt hash (the prompt changes the
moment one order is in `command_history`; hashes are stored as PROVENANCE).
A cassette miss is a `BaseException` (both catch-alls on the path swallow
`Exception` into a green fallback — measured), and **the suite never
records**: `ReplayMessages.create` has exactly two outcomes, serve or raise,
and an AST pin asserts no test module imports the recorder.

**The committed set ships AUTHORED** (`provenance: "authored"` — hand-written
shapes measured through the real pipeline in the IQ-9 recon; never a model's
answer). To promote them to `recorded` in one run (~17 calls, ≈$0.11 at the
CR-3 measured $0.0065/parse):

```bash
# keyless: list what would be recorded, with the field diff against each existing cassette
.venv/Scripts/python.exe tools/record_parser_cassettes.py --dry-run --ids cr5-deleg-aggressive-ney-resolves-live cr5-deleg-cautious-davout-resolves-live cr5-deleg-literal-soult-asks fa73-live-cover-the-retreat-is-not-a-retreat fa73-live-fix-bayonets-is-not-a-repair --phrasings tests/data/parser_cassettes/phrasings.json
# spends the key (reads .env for ANTHROPIC_API_KEY — the only place the gate does)
.venv/Scripts/python.exe tools/record_parser_cassettes.py --record --ids ... --phrasings tests/data/parser_cassettes/phrasings.json --overwrite
# after a prompt edit: re-record only what drifted
.venv/Scripts/python.exe tools/record_parser_cassettes.py --record --refresh-drifted
```

The recorder refuses without `--record` AND a key; `--no-overwrite` is the
default (an existing cassette is kept unless `--overwrite` or it was selected
by `--refresh-drifted`); it prints the model pin, the SDK version and the cost
before the first call, and a field diff (`action / marshals / target /
stop_reason`) against each existing cassette. Two cassettes are written when
one request also fires Berthier's text-mode recovery (`<id>.recovery`).

**Drift policy** (`tests/data/parser_cassettes/MANIFEST.json`): a
`recorded` cassette whose `prompt_sha256` no longer matches the live prompt
FAILS `TestCassetteHygiene::test_drift_is_acknowledged_or_fails` until the
developer either re-records it (`--refresh-drifted`, needs the key) or
acknowledges it in the manifest (`"drift": {"acknowledged": "<date>", "by":
"...", "note": "..."}` — keyless). Acknowledged drift still raises a
`CassetteDriftWarning` every run so the summary counts it. `authored`
cassettes are exempt: they pin OUR handling of a response shape, not a
model's answer to a prompt. A drifted cassette proves handling of a
PLAUSIBLE answer, not today's answer to today's prompt — the recorder is how
that gap is closed.

The authored set is still pinned INFORMATIONALLY (`drifted == {}` in the same
test), so a change to anything the parse prompt carries — the alphabetical
province list, the roster, the few-shots — fails it until the authored
fingerprints are re-stamped. Attribute the drift first: undo the change in
today's prompt and check that the result hashes to the recorded
`prompt_sha256`. DEF-14 (September 24, 2026) did this for its nine province
renames, undoing the names and re-sorting the province line; all 14 drifted
1805 prompts matched exactly, with the system and tool hashes unchanged. Only
then update `request.prompt_sha256` / `request.prompt_chars` in each cassette
and `prompt_sha256` in `MANIFEST.json`. The responses stay as authored.

The same rows run from the CLI, keyless: `python -m backend.ai.parser_eval
--replay` (the `live_only` corpus rows on the cassettes; exit 2 on a miss).

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
| `SOVEREIGN_SEED` | campaign seed (authored variance bands; `historical`/unset = the byte-pinned boot) | `historical`; on `--from-save`, the save's own seed (IQ-8) |
| `LLM_MODE` | `mock` (deterministic, free) / `anthropic` (live parse, needs key) | `mock` |
| `SOVEREIGN_PORT` | backend port AND client origin (both read it) | — (in-process) |
| `INK_IRON_SAVE_DIR` | where saves land — the driver sandboxes this per run | run dir |
| `DEBUG_MODE` | `true` arms cheat commands (the shipped default is off) | `false` (`--cheats` flips) |
| `SOVEREIGN_SCENARIO` | explicit scenario path / `none` = bare flag world — the driver SETS it to `""` (the engine's no-op) before the import | `""` |
| `SOVEREIGN_SMOKE_START` | settlement smoke presets — set to `""` by the driver | `""` |
| `SOVEREIGN_MAP` | `legacy` = 19-region rollback — set to `europe` by the driver | `europe` |
| `PYTHONHASHSEED` | `0` for byte-identity work (M1–M7/BASELINE_SERIES idiom) | `0` (the driver re-execs itself with it when unset; recorded in `meta.json`) |
| `ANTHROPIC_API_KEY` | required by `--llm anthropic`; **without it that arm cannot run at all** and must be reported as NOT RUN rather than skipped. **The escalation path's HANDLING is gated keylessly by the replay gate** (`tests/test_iq9_keyless_parser_gate.py`, IQ-9 — the 0.7 gate's live arms, the SDK ladder, the `stop_reason` discard, validation, the CR-5 arms, the call count per request); `--llm anthropic` still owes the MODEL'S OWN ANSWERS. The suite itself pins `LLM_MODE=mock` and refuses every non-loopback connection (`tests/conftest.py` T0), so a key in `.env` can no longer make a test go live. | — |

Never set `PYTHONIOENCODING` when running tests (fakes 6 subprocess-test
errors — standing memory).

⚠ **The driver SETS the three board variables; it never pops them (IQ-8,
September 17, 2026).** `backend.main` calls `load_dotenv()` at import, and
dotenv fills every variable that is not PRESENT — so the old pop was undone by
any repo `.env` that named one (demonstrated: popped → `None`, imported →
`settlement_losing`). A present variable is never overridden, `""` is the
engine's own no-op for the scenario and smoke variables, and `europe` is the
map default (an empty map value would print `[WARN] Unknown SOVEREIGN_MAP`
on every boot). `meta.json` `resolved.env` records the six variables as the
engine read them, after the import.

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

- **Never edit a file under `backend/` while the suite is running.** Learned
  September 12, 2026: two full-suite runs failed on *different*
  `inspect.getsource` structural-census pins, each of which passed in
  isolation, and a third run with no concurrent edits was clean at 21,590
  passed / 0 failed. The census idiom reads through `linecache` and is not
  robust to a file changing mid-run — a red census pin during a session that is
  editing sources is an artefact until a quiet run says otherwise.

- **Two arms need things the environment may not have.** `--llm anthropic`
  needs a key; Mode C needs the Godot binary. A session that cannot run them
  must say so and leave the pillar they cover UNSCORED — the prior score
  stands. `unknown_blockers: []` is not coverage, and neither is a pillar
  nobody looked at. **What the keyless gate DOES discharge (IQ-9):** how the
  game HANDLES a live answer — the provider's typed-exception ladder, a
  truncated or refused tool call, hallucinated marshals/actions/targets,
  forbidden diplomatic fields, the strategic-verb remap, the CR-5
  aggressive/cautious/literal arms and the CR-5b register gate, the CR-2
  retry, Berthier's second call, and the NUMBER of live calls per request —
  all replayed from committed cassettes with no key and no network. **What it
  does NOT discharge:** whether today's Haiku answers a phrase the way the
  cassette says (the cassettes ship AUTHORED; a recorded one is a witness of
  one day's answer to one day's prompt), prompt quality, real network
  behaviour, or token cost. `--llm anthropic` remains the only arm that
  scores the MODEL.

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
