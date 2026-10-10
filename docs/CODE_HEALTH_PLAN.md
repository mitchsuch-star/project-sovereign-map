# Code Health Plan — make the next fifty fixes cheaper

> **Status: PLAN, October 8, 2026.** Ordered by `docs/PRE_DEPLOY_PLAN.md` §2.
> Rows CODE-1 … CODE-6. **No row changes what the game does.** The gate on every
> slice is byte-identity: `BASELINE_SERIES` and M1–M7 unchanged with no
> re-record, the parser corpus identical, the last score reading's arm digests
> identical (`tools/score_run.py check` against
> `docs/audits/score_runs/2026_10_05_sfr/` — items unchanged, not a score), the
> full suite green. A slice that moves any of them is wrong, not "attributed".
>
> **Instrument:** `tools/_code_health_census.py` (read-only; functions over N
> lines with their `if` counts, levers and which a test names, `except
> Exception` split silent / logging / re-raising, silent handlers by file). Run
> it before and after every slice and put both readings in the landing record.

## 0. The reading on `4680b361` (October 8, 2026)

| Measure | Value |
|---------|-------|
| Backend lines | 247,116 in `backend/` |
| Files over 3,000 lines | 26 — `world_state.py` 15,716 · `diplomacy.py` 13,468 · `combat_executor.py` 11,784 · `enemy_ai.py` 8,259 · `dispatch.py` 7,861 · `diplomatic_executor.py` 7,723 · `main.py` 7,403 (56 endpoints) · `strategic.py` 5,402 · `vassal.py` 5,326 · `jealousy.py` 5,101 |
| Functions over 500 lines | **34** (86 over 300) |
| The eight largest | `_execute_attack` 3,945 / 382 ifs · `_process_dialogue_choice` 2,215 / 190 · `executor._execute_one` 2,173 / 242 · `_parse_with_mock_chain` 1,644 / 174 · `main.execute_command` 1,533 / 119 · `format_event_oneliner` 1,525 / 255 · `_execute_strategic_command` 1,474 / 172 · `_ratify_treaty` 1,179 / 110 |
| Module-level flip levers | **665**, 661 `True`, 624 named by a test; **748** test arms set one `False`, 19 set one `True`; 73 of 188 `tools/_sweep_*.json` reference one |
| `except Exception` | **397**: 368 neither log nor re-raise, 28 log, 1 re-raises |
| Silent handlers by file | `state_desk.py` 36 · `game_end.py` 20 · `counsel.py` 18 · `diplomacy.py` 17 · `world_state.py` 17 · `main.py` 15 · `llm_client.py` 15 · `congress.py` 12 · `settlement_scoring.py` 12 |
| Client | `main.gd` 8,655 lines (largest functions 432 / 424 / 378); `map_renderer_base.gd` 3,196 |
| Session docs | `CLAUDE.md` 524 KB · `STATUS.md` 1.6 MB · `BUG_FIXES.md` 2.2 MB · `SYSTEMS_REFERENCE.md` 892 KB · `DESIGN_REFINEMENT.md` 450 KB; `docs/` 844 MB on disk (frames and run archives) |

The pasted analysis the user brought (634 levers, 240 silent handlers, 46 MB
of docs) was taken on an earlier tree with a looser handler rule; the numbers
above supersede it. The shape is the same.

## CODE-1 — Retire the levers (≈ 2.5 sessions, spread as batches)

**What a lever is here.** `THE_COORDINATION_IS_READ_ON_THE_FIELD = True` at
module level; the fix reads it, the old branch lives under `else`, a pin flips
it `False` to prove the attribution, the driver's `--lever MODULE:NAME=0|1`
re-runs the series without it. That is the right way to LAND a change. It is
the wrong way to KEEP one: 661 levers ON means ~700 dead branches in
production, every one a place a later fix can land on the wrong side.

**The rule after CODE-1.** A lever lives for one session after its attribution
is recorded, then it is retired. The retirement is part of the NEXT slice's
head, not a backlog.

**Recipe, per lever** (`tools/retire_lever.py`, new, AST-based, dry-run first):

1. Confirm the lever is `True` in production and named in the landing record
   (grep `docs/` for the name; the record is the attribution). A lever named in
   NO record and NO test is deleted outright with a note.
2. Inline the `True` branch: `if LEVER:` → the body; `if not LEVER:` → the
   `else` body or nothing; `x if LEVER else y` → `x`; a `getattr(mod, "LEVER",
   True)` read → `True`. The tool prints every site it could not rewrite
   mechanically (a lever read into a variable, a lever passed as an argument);
   those are done by hand.
3. Tests: every `monkeypatch.setattr(mod, "LEVER", False)` arm is DELETED
   together with the assertions that describe the old behaviour; an arm that
   asserts the NEW behaviour under the lever ON keeps its assertions and loses
   the setattr. The tool lists the arms; the author decides each. A test that
   does nothing but flip the lever and assert the old world is deleted whole.
4. Sweep JSONs that mutate the lever (`tools/_sweep_*.json`, 73 files) lose
   that row; the sweep's other rows still run.
5. Delete the constant and its comment.
6. The batch gate: full suite, series, M1–M7, corpus, the score arms' digests,
   all byte-identical. The driver's `--lever` for a retired name must FAIL
   loudly (it already does: "has no lever").

**Batches** (smallest, most-covered modules first so the tool is proven before
the monsters): batch 1 = `backend/ai/` + `backend/commands/` modules under
1,500 lines (~100 levers); batch 2 = the game_logic modules under 3,000 lines;
batch 3 = `diplomacy.py`, `vassal.py`, `jealousy.py`, `naval.py`; batch 4 =
`world_state.py`, `combat_executor.py`, `enemy_ai.py`, `main.py`. Levers landed
after October 1, 2026 keep one more session (PRE_DEPLOY §5-4).

**What is NOT a lever and stays:** scenario/config constants (`GLORY_WINDOW`,
`COMMITTED_ALPHA`, prices), the N1 legacy-world branches (`is_dotation_world`
and kin — those are scenario scope, not attribution), the `sandbox_mode`
toggle, the debug gate.

**Done when:** `_code_health_census.py` reports under 40 levers, every one
dated within two sessions; a new pin `tests/test_code_health_ratchet.py`
caps the count and fails on growth.

**✅ BATCH 1 LANDING RECORD — October 9, 2026 (Pre-Deploy S2, slice 2; the
tool `tools/retire_lever.py`, its shape pins `tests/test_retire_lever_tool.py`,
the ratchet `tests/test_code_health_ratchet.py`).**

- **The tool.** AST-based; `--list DIR … --max-lines N` censuses a tree with
  each lever's blame date, test / sweep / doc counts; `NAME …` is a dry run
  that prints every production site with the rewrite it would make or HAND;
  `--apply` writes the production rewrites, drops the sweep rows and deletes
  the constant with its own comment block. The rewrites: `not X` flips the
  value; a neutral `and`/`or` operand is removed (an absorbing one folds the
  whole op only when the operands before it are pure); `if` / `elif` inline
  the body or keep the else, dedented, an `elif` becoming the chain's `else`
  or leaving it; a ternary keeps its branch WITH the parentheses the AST
  span stops inside (the first cut dropped them on a multi-line branch and
  the file no longer parsed — found by the tool's own parse check before a
  byte was written); `getattr(mod, "X", d)` → `True`; the name leaves an
  import. A boolean operand outside a test position is HAND (`A and True`
  is `A` only under truthiness). Tests are never edited: the dry run lists
  every arm with its enclosing test, the author decides each.
- **The batch, as defined and as measured.** `backend/ai/` +
  `backend/commands/` modules under 1,500 lines hold **46** levers by the
  census regex, not the plan's ~100; **26 landed in October 2026** and keep
  their session under PRE_DEPLOY §5-4; **20 retired**: counsel.py ×6
  (`COUNSEL_IS_DERIVED_FROM_THE_BOARD`, `THE_COUNSEL_READS_THE_ACTION_POINTS`,
  `…READS_THE_REFUSALS`, `…SPREADS_THE_ORDERS`, `…READS_THE_CROSSING`,
  `THE_LEVY_LINE_IS_THE_QUOTE`), first_contact.py ×3, prompt_builder.py ×2
  (`THE_PROMPT_IS_STATIC_FIRST`, `THE_RECOVERY_PROMPT_NAMES_THE_COUNSEL`),
  strategic_parser.py (`GUARDING_A_MARSHAL_IS_SUPPORT`), delegation.py ×3
  (`AGGRESSIVE_ATTACK_ARM_ENABLED`, `KEYLESS_DELEGATION_READS_THE_MATCH`,
  `THE_QUOTE_IS_THE_PLAYERS_OWN`), diplomatic_defiance.py, naval_executor.py,
  prisoners.py (`PRISONERS_ARE_NAMED`, read from four modules),
  tactical_executor.py, vindication.py (`THE_VERDICT_IS_BOUND_TO_ITS_ORDER`,
  read from three). Every one `True` and named in a landing record
  (`docs/` grep; the four with no doc mention — the FA slice-7 trio and
  the L-D witness — are named in their slices' STATUS entries). **55
  production sites rewritten by the tool, 1 by hand** (the recovery
  prompt's multi-line f-string body, which no dedent can touch), plus the
  pre-quote tail of `_levy_terms` that the inlined `return` made dead
  (deleted; its `except Exception: return None` is the one silent handler
  the census lost). **18 sweep rows dropped** from 9 `tools/_sweep_*.json`.
- **The test arms, decided one by one:** 13 `False` arms deleted whole with
  their old-world assertions (CRT-7 ×5, the exit residue ×2, CX-2, first
  contact, L-1, FA-S17-14b, FA-S17-e, SR-2e); 4 lever-off tails trimmed
  (FA slice 7's admiralty / pursue / province / fog cases); 3 tails that
  re-asked under the mode gate trimmed (CR-5, CR-5b, PC15-8); 2
  parametrized pins kept on the lever-up arm alone (the IQ-9 recovery
  cassette drift, the L-1 re-stamp); the L-D `TestAnOrdinaryOrderIsUntouched`
  class deleted (its only pin compared the two arms); the FA slice-7 LEVERS
  restore list and the two `is True` asserts shed the retired names.
  1,384 tests in the 15 touched files pass.
- **The reading:** levers **665 → 645** (641 on, 605 named by a test);
  functions over 500 lines 34 → 34; silent handlers 368 → **367**;
  `CLAUDE.md` 61,562 B. **The ratchet** caps all four at the reading
  (`LEVERS_CAP 645`, `FUNCTIONS_OVER_500_CAP 34`, `SILENT_HANDLERS_CAP 367`,
  `CLAUDE_MD_BYTES_CAP 62,000`, `STATUS 200,000`), lower-only, reading the
  census as data (`_code_health_census.census()`), never a grep; a "cap
  near its reading" pin keeps a cap honest; the driver's `--lever` refuses a
  retired name by `SystemExit` (pinned on three of the twenty).
- **Gate:** `BASELINE_SERIES` + M1–M7 byte-identical, corpus 902/902,
  `score_run check` against the final reading's archive identical item for
  item to the pre-slice check; full suite green on the parallel hook.
- **Next batches** (the head of S3 … S13, one each): batch 2 = the
  game_logic modules under 3,000 lines; the October 2026 levers of batch 1
  (26) join the first batch after October 2026 closes.

## CODE-2 — Split the monster functions into named stages (1 session each)

**Order:** `_execute_attack` → `_process_dialogue_choice` → `_execute_one` →
`_parse_with_mock_chain`; then `execute_command`, `format_event_oneliner`,
`_execute_strategic_command`, `_ratify_treaty` as sessions allow.

**Recipe (pure extract-method, no behaviour change):**

1. Read the function once and write its stage list in the landing record
   BEFORE editing — for `_execute_attack` the pipeline is already documented in
   the file's own comments (pre-validation → crossing gate → objection →
   coordination → reinforcements → resolve → post-combat pipeline steps 1–12 →
   capture → report → events). Each stage becomes `_attack_<stage>(ctx)`.
2. One context object (`@dataclass class AttackContext`) carries what the
   stages share; it is built once at the head and never reaches the wire. No
   stage reads a local it did not receive.
3. Move code, do not rewrite it. A stage body is a cut-and-paste with its
   locals renamed to `ctx.<name>`. Early `return`s become stage results the
   driver loop checks (`if result.done: return result.response`).
4. After each stage extraction, run the fast gate: `tests/test_combat_sweep_metrics.py`
   (M1–M7), the series pin, and the combat test files. After the whole
   function: the full gate.
5. The function's docstring becomes the stage index; the file's "Before
   Modifying" row in `CLAUDE.md` names the stage, not the line.

**Risk and its control.** The replay pins are the net: M1–M7 and
`BASELINE_SERIES` cover both combat copies, the corpus covers the parser chain,
the score arms cover the executor and `main.py`. A split that passes all of
them byte-for-byte has not changed behaviour. The one hazard the record warns
about is the function-local import that shadows a module name (F2's
regression) — the tool `tools/_local_import_census.py` already pins it; run it
after every move.

**Done when:** no function over 500 lines in the eight named; the census pin
caps "functions over 500 lines" at the new count and ratchets down.

## CODE-3 — Every broad except speaks (1 session, with DD-C)

**The rule.** `except Exception` is allowed only through
`backend/errors.py`:

```python
with swallow("save_game: writing the autosave", notify=world):
    ...
# or
except Exception as exc:
    report(exc, "intel_surfaces: the garrison snapshot")  # logs once per site at WARNING with the stack
    return fallback
```

`report` logs at WARNING with the site string and the traceback, de-duplicated
per site per process (so a per-turn loop logs once, not 500 times), and
counts into `world.error_tally` (display-only, never serialized) so the debug
command can list them. `notify=` pushes a rail notice through the existing
`NotificationCollector` for the classes the player must see: **save, load,
autosave, the export, the LLM key**.

**Recipe.**

1. Land `errors.py` + the ratchet pin (`test_code_health_ratchet.py` counts
   bare `except Exception` bodies with no `report`/`swallow`/`raise`; the count
   starts at 368 and must fall every slice; a new one fails the suite).
2. Convert by file, largest first: `state_desk.py` (36), `game_end.py` (20),
   `counsel.py` (18), `diplomacy.py` (17), `world_state.py` (17), `main.py`
   (15), `llm_client.py` (15). Where the exception type is obvious
   (`KeyError`, `ValueError`, `json.JSONDecodeError`, the SDK's typed errors)
   narrow it; where it guards a display line, keep the breadth and `report`.
3. **The save path is the deep dive (DD-C):** `save_manager.save_game` /
   `autosave` / `load_game` RAISE a typed `SaveError` the route turns into a
   `success: False` WITH a `message` the client renders; the client's save
   dialog and the autosave both show it; fault injection pins each arm.
4. `main.py`'s route-level handlers return the error's class and site in the
   JSON under `debug_error` when `debug_mode` is on, never in production.

**Done when:** the census reads 0 silent handlers in `save_manager.py`,
`world_state.py` serialization, `main.py` save/load routes and `llm_client.py`;
under 60 elsewhere, each with a `report` site string; DD-C's injected faults
all reach the player.

## CODE-4 — The docs diet (0.5 session)

Every session reads `CLAUDE.md` (524 KB ≈ 130k tokens) before its first tool
call. Most of it is history that `STATUS.md` and the specs already hold.

1. **`CLAUDE.md` → ~40 KB:** Golden Rules, Workflow, the "Load-bearing
   operational facts", the File Reference, Before Modifying, patterns,
   serialization, troubleshooting, Don't Do, Commands, Document Map,
   Environment — unchanged. "Current Phase" becomes **one screen**: the routing
   authority (a file name), the three most recent landed rows (one line each),
   the open user decisions, and a pointer to the archive. The whole "queue in
   one line" paragraph and the LIVE STATE scroll move verbatim to
   `docs/archive/CLAUDE_CURRENT_PHASE_2026.md`.
2. **`STATUS.md` → the NEXT UP block + the last five session entries.**
   Everything older moves verbatim to `docs/archive/STATUS_2026_Q3.md` (and
   earlier quarters as they fall out), with a header line in STATUS naming each
   archive. The routing convention ("STATUS ▶ NEXT UP is the authority") is
   unchanged.
3. **`BUG_FIXES.md` / `DESIGN_REFINEMENT.md`:** CLOSED rows older than the
   current quarter move to `docs/archive/BUG_FIXES_2026_Q{n}.md`;
   `tools/defect_census.py` and `tools/fa_row_tally.py` read the archives too,
   so every count stays whole (pinned: the census total is unchanged by the
   move). OPEN and PARTIAL rows never move.
4. **`docs/` on disk:** the 844 MB is frames and `score_runs/` archives; the
   untracked `_probe_saves/` and `arms/AIV/` directories in the git status are
   added to `.gitignore` or committed deliberately — decided in the slice, not
   left as noise.
5. **A pin** caps `CLAUDE.md` at 60 KB and `STATUS.md` at 200 KB so the diet
   holds.

**Done when:** a fresh session's first read is under 15k tokens of
instructions and the three "where am I" questions (what is next, what landed
last, what the user still owes) are answered on the first screen of STATUS.

**✅ LANDING RECORD — October 9, 2026 (Pre-Deploy S2, slice 1; pins
`tests/test_code4_docs_diet.py`, helper `tests/_ledgers.py`).**

| Doc | Before | After | Where it went |
|-----|--------|-------|---------------|
| `CLAUDE.md` | 523,156 B (2,850 lines) | **61,405 B** (426 lines) | the whole "Current Phase" (2,429 lines) → `docs/archive/CLAUDE_CURRENT_PHASE_2026.md`; the one-screen replacement names the routing authority, the three last rows, the open user decisions and the archives; the "Load-bearing operational facts" stay verbatim |
| `docs/STATUS.md` | 1,593,361 B (14,534 lines) | **21,845 B** (90 lines) | the ▶ NEXT UP block keeps the last five entries; 71 older entries + the re-staged session log + the settlement-era sections → `STATUS_2026_Q4.md` (29 October entries), `STATUS_2026_Q3.md`, `STATUS_2026_Q2.md`, each named under `## Archives` |
| `docs/BUG_FIXES.md` | 2,232,588 B | **274,194 B** | 63 of 85 sections (12,260 lines), every one dated before Q4 and holding no OPEN/PARTIAL row, → `BUG_FIXES_2026_Q3.md`; the 22 kept are the October sections, the undated structural ones and anything with an open row |
| `docs/DESIGN_REFINEMENT.md` | 451,210 B | **113,531 B** | 31 of 53 sections → `DESIGN_REFINEMENT_2026_Q3.md` + `_Q2.md` (the April audit) |

- **The rule that moved a section:** dated before the current quarter in its
  heading AND no row in it reads OPEN or PARTIAL under the census's own
  classifier. Whole sections moved verbatim, heading and prose included, so
  the census's by-heading / by-table rules read the archived rows exactly as
  before; undated sections stayed. OPEN and PARTIAL rows never moved.
- **The count is unchanged by the move, proven not asserted:**
  `tools/defect_census.py` and `tools/fa_row_tally.py` read the live ledger
  then its `docs/archive/<STEM>_<year>_Q<n>.md` archives (`LEDGERS` is built
  from both; `closed_elsewhere` reads the diet's archives beside `docs/*.md`).
  Before and after on this tree: defect 86 OPEN / 1,154 closed / 37 disposed
  = 1,277 ids; design 8 / 182 / 16 = 206; FA tally 267, 0 open — and every
  one of the 1,483 ids carries the same state, severity, pillar, step, slice
  and ledger (`--json` compared id by id); the 20 `*` stale marks identical.
- **The doc pins:** 84 test files read one of the four docs; 13 pins in 11
  files read a row or a record that moved. They read through
  `tests._ledgers.doc_text(name)` now (the live file, then its archives), the
  same text they read before. No pin was weakened; none was deleted.
- **Deviation, recorded:** the plan's 60 KB cap for `CLAUDE.md` assumed the
  unchanged sections were under that; measured, they are 59 KB (File
  Reference, Before Modifying, patterns, troubleshooting, Commands, Document
  Map, Environment — all kept verbatim as item 1 requires), so the dieted file
  reads **61,405 B** with a 2.2 KB Current Phase. The ratchet pin caps it at
  the reading and ratchets down; nothing else was cut to make the number.
- **Item 4, the untracked bulk:** `.gitignore` now excludes the regenerable
  per-run artefacts under `docs/audits/score_runs/` (`_probe_saves/`, the
  per-arm `arms/AIV/arm*.json`, `arms/CLI/`, `attribution/`, `frames/`); a
  reading's `run.json`, checklist, scores, digests and the AI-V `summary.json`
  stay committed, and the three summaries the convention had missed
  (`2026_10_02_step3`, `2026_10_03_sf_cl1`, `2026_10_03_sf_lb2`) are committed
  with this slice. A frame a landing record names is force-added. The tree's
  `git status` is clean of noise.
- **Gate:** `BASELINE_SERIES` + M1–M7 byte-identical (14 passed), the corpus
  902/902, `score_run check` against the final reading's archive with all 112
  items identical to the same check on the pre-diet commit `78d9653a` (seven
  probes read CMD saves the archive never held and are unmeasured on both —
  a fact about the archive, not this slice), the code-health census unchanged
  (34 / 665 / 368; docs, tools and tests only); full suite green on the hook. **Done-when:** a fresh session's first read is `CLAUDE.md`
  61 KB + `STATUS.md` 22 KB ≈ 21k tokens of which the rules are ~15k, and
  STATUS's first screen answers next / last / owed.

## CODE-5 — File splits (1 session each, after CODE-2)

Only after the functions are staged; splitting a file around a 3,945-line
function moves the problem. Candidates and their natural seams:

- `world_state.py` 15,716 → `world_state.py` (the class, queries, caches),
  `world_turn.py` (`_advance_turn_internal` and the per-turn processors),
  `world_serialization.py` (`to_dict` / `from_dict` / the migrations).
- `diplomacy.py` 13,468 → the state machine, the acceptance formula, the
  war/peace transitions, the missions.
- `main.py` 7,403 → FastAPI routers by family (`routes_command.py`,
  `routes_diplomacy.py`, `routes_screens.py`, `routes_saves.py`), the response
  builder staying the one seam (`build_base_response`).
- `combat_executor.py` 11,784 → after CODE-2a, the attack stages into
  `combat_attack.py`, coordination/reinforcement into `combat_muster.py`.

Each split is import-only (re-exports at the old path for one session so the
tests' patch targets keep working, then the tests are re-pointed). The
monkeypatch-singleton rule holds: patch `type(obj)`, never a method on the
module's executor instance.

## CODE-6 — The client's `main.gd` (1 session, after UXR-2)

8,655 lines, one script, every route's result rendering and every popup's
stash-and-raise tail. The split follows the surfaces: `command_road.gd`
(input, completer, send), `result_renderer.gd` (`_display_*`),
`control_return.gd` (the ONE stash + raise chain from B4b), `screen_router.gd`
(top bar + hotkeys). The parse harness (`tools/godot_parse_check`) and the
driven harnesses (`tools/ep_f3_client_layout_harness.gd`,
`tools/mode_c_driven_session.py`) are the gate; the boot smoke must read 0
`SCRIPT ERROR`. Do it after UXR-2 so the layout law lands once, in the new
files.

## The ratchet pin (lands with CODE-1 batch 1)

`tests/test_code_health_ratchet.py` reads `_code_health_census.py` and caps:
levers, functions over 500 lines, silent handlers, `CLAUDE.md` bytes. Each cap
is the current reading and may only be lowered. This is what keeps the plan's
gains from leaking back.
