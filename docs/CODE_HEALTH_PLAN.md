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

**✅ BATCH 2 LANDING RECORD — October 10, 2026 (the head of Pre-Deploy S3,
DD-0's session).**

- **The batch, as defined and as measured.** `backend/game_logic/` modules
  under 3,000 lines hold **138** levers by the census regex; **56 landed in
  October 2026** and keep their session (PRE_DEPLOY §5-4); **83 retired**
  (every one dated August 16 – September 29, 2026): ledger ×9, withdrawal
  ×7, game_end ×7, diplomatic_dialogue ×7, war_status ×5, marshal_overview
  ×4, emergent_designs ×4, dotation ×4, diplomatic_advisory ×4, gazette ×3,
  garrison_report ×3, combat ×3, reforms ×2, recruitment ×2, intent ×2,
  fall ×2, battle_report ×2, and one each in turn_manager, the seven
  settlement layers (validation / scoring / routes / reactions / ratify /
  presentation / helpers), mailbox_payloads, fortunes_of_war,
  diplomatic_ledger, collapse and battle_scale. Every one `True` in
  production. 73 named in a landing record under `docs/` (archives
  included); nine named by their tests alone (SKIRMISH_GATE_ACTIVE,
  MISSION_RAIL_NOTICE, MISSION_LOG_ENDS, TALLEYRAND_TAB_READS_THE_CABINET,
  THE_EMPIRE_CAN_FALL, MISSION_LEDGER_BLOCK, THE_LEDGER_SEES_THE_HALT,
  THE_ORDERS_TAB_KNOWS_ITS_PRISONERS, INCOMING_ASSESSMENT_READS_OUR_BURDEN —
  their slices' STATUS entries name the rows); **one named by nothing**
  (`game_end.THE_HUMBLED_PEACE_IS_MARKED`, from GE-1's commit `975f1f13`,
  no test and no doc) — deleted outright per recipe step 1 with this note.
- **The sites.** 132 production sites rewritten by the tool across **36
  modules** (55 operands removed, 31 bodies dropped, 27 bodies inlined, 14
  ternaries folded, an elif chain stood up as `if`, an elif cut, two names
  left imports, one import deleted; the lever read from four modules outside
  `game_logic/` — `question_desk`, `combat_executor`, `meta_executor`,
  `movement_executor`, `world_state` — followed the same path), **5 by
  hand**: the two the dry run named (`battle_report._at_scale`'s `not X or
  f()` → `f()`, exact because `False or x` IS `x`; `reforms.is_in_force`'s
  `True and a and b` → `a and b`) and **three overlaps the dry run did NOT
  name** — two levers in one statement (`if not (THE_STATE_HAS_LAWS and
  THE_AI_ENACTS)`, `if A and B:` in the prisoner note, the ledger's
  `if not CEILING … elif not TRUTH` chain): the tool applies the first
  rewrite and skips the second as overlapping, printed only at write time.
  **Tool fix in this slice:** the overlap skips now carry their pre-edit
  line and are listed in the closing "the hand's" summary, so batches 3–4
  cannot miss one (ruff's F821 caught these three; a cross-module
  attribute read would not have been caught, hence the summary). One
  `_scan_garrison` ternary fold left a bare `lambda` assignment (E731) —
  made a `def`. The orphaned IQ-6 "flip levers" header comment in
  `emergent_designs.py` re-titled as the rules it documents;
  `VOLTE_FACE_WE_MARK` and `VOLTE_FACE_WINDOW_BEFORE_IQ6` stay (tests read
  them as the measured marks). **75 sweep rows dropped** from 33
  `tools/_sweep_*.json`.
- **The test arms, decided one by one (120 flip lines in 58 files):** **99
  whole deletions** — every `test_lever_down_*` / `test_the_lever_*` /
  control-arm test asserting the old world, the `lever_down` fixture
  (IQ1-2), the IQ-6 `window_down` module fixture and its two tests, the
  `_pre_iq6_*` verbatim copy of the old predicate with its identity-grid
  class, the arm-comparison tests (`test_a_solo_battle_is_byte_identical_in_
  both_arms`, the FA-11 payload-cost comparison, RS-D1's `score(lever)`
  difference, the AI-mirror both-arms twin), and the IQ-2 integration class
  whose autouse fixture pinned the LIST shape under the lever down (its
  PR-X1 guarantee is `TestTheSentenceNamesNothingLost`); **~45 trims** —
  the lever-down tail cut from a test whose head pins the new rule (19 in
  `test_iq2_collapse_war_room.py` alone, the WIN-D3 pins kept on their
  corridor arm only, `test_one_of_many_is_not_held` re-staged on the
  sentence); the IQ-6 "window of 15" negative controls now read the kept
  `VOLTE_FACE_WINDOW_BEFORE_IQ6` constant instead of flipping a lever; the
  LEVERS restore lists (FA-10, FA-11 ×2, IQ-4) and the IQ-2 `_all_levers`
  stack shed the retired names; two classes left empty by the deletions
  (`TestTheLever` in IQ1-SW0 and RF-2) removed with their headers. **Pins
  the dry run cannot list** surfaced only by running: ten that read a lever
  by attribute (`assert M.LEVER is True`), by source text, or through the
  deleted `lever_down` fixture; and one — found by the hook's full run, in a
  file naming no lever at all — a source census asserting the executor
  calls `expectation_for_wins(`, which only the retired lever-down branch
  did (the live path moves the expectation through `raise_expectation`;
  the pin now says so and the dead import went with it). 53 test files
  touched, −1,411 lines net.
- **The reading:** levers **645 → 562** (558 on); functions over 500 lines
  34 → 34; silent handlers 367 → 367; `CLAUDE.md` 61,706 B. **The ratchet**
  lowered to `LEVERS_CAP 562`.
- **Gate:** `BASELINE_SERIES` + M1–M7 byte-identical with no re-record,
  corpus 902/902, `score_run check` against `docs/audits/score_runs/
  2026_10_05_sfr/` identical item for item to the same check on `3277ff27`
  (the check REWRITES the archive's `scores.json` / `checklist.json` /
  `census_by_pillar.json` / `findings_rate.json` as it runs — restore them
  with `git checkout` after each check, as this slice did on both sides);
  the touched test files + the ratchet, tool, series and corpus pins green
  under xdist; the full suite green on the hook.
- **Next batches:** batch 3 = `diplomacy.py`, `vassal.py`, `jealousy.py`,
  `naval.py` (the head of S5); batch 4 = `world_state.py`,
  `combat_executor.py`, `enemy_ai.py`, `main.py`; the October 2026 levers
  of batches 1–2 (26 + 56) join the first batch after October 2026 closes.

**✅ BATCH 3 LANDING RECORD — October 11, 2026 (the head of Pre-Deploy S5,
DD-1's session).**

- **The batch, as defined and as measured.** `diplomacy.py` (26 levers),
  `vassal.py` (24), `jealousy.py` (20) and `naval.py` (8) hold **78** levers
  by the census regex; **12 landed in October 2026** and keep their session
  (PRE_DEPLOY §5-4: diplomacy ×5 — `A_PEACE_EARNS_NO_TRADE`,
  `THE_DEAD_DO_NOT_TRADE`, `A_NEW_WAR_HAS_A_PURPOSE`,
  `A_MEMBER_AT_WAR_LEAVES_THE_SYSTEM`, `THE_SYSTEM_CHARGES_ONLY_THE_TRADE_
  EARNED`; vassal ×6 — the IQ7-X1/X3 and SF5-RV rules; jealousy ×1 —
  `THE_TOP_RUNG_PROMISES_NOTHING_HIGHER`); **66 retired** (every one dated
  August 2 – September 29, 2026, every one `True` in production): diplomacy
  ×21 (the FA slice-17 rulings, RS-1's fresh peace, GE-1's dead court, DP-1
  the bank, the MS playtest re-score ×5, IQ-4 "The Cabinet Is Visible" ×8 —
  `COURT_FAVOUR_ACTIVE` read from eleven sites in two modules — and
  `REASSURE_ONLY_AT_ALLIANCE` read from three), jealousy ×19 (SR-4c's four,
  F4, N52, CA8-D3 `JEALOUSY_RIVAL_MEMORY`, A12, WO-17, VP-R1,
  FA-S16-D4's two, B1, SRX-9, F6, S17-12, B2's two —
  `THE_PETITION_DIES_WITH_ITS_SUBJECT` read from thirteen sites in
  `jealousy.py` and `main.py`), naval ×8 (`HOST_RULE_ACTIVE`, SR-5b's three,
  SR-5c, FA-D16, NUI-2, HC-4a, FA-31), vassal ×18 (IQ-7's eight, SR-5a,
  FA-S17-D8, WO-9's two, GE-V, FA slice 11's three, FA-N73, FA-S17-6,
  SR-2c). 63 named in a landing record under `docs/`; three named by their
  tests alone (`COUNSEL_NAMES_THE_COURT`, `JEALOUSY_SUPPRESS_SAME_PASS_
  REFIRE`, `GLORY_DORMANT_ACTIVE` / `RESTLESSNESS_SLEEPS_IN_SCHOOL`'s slice
  memos name them). **`DEAD_COURTS_CANNOT_BE_FOUGHT` was named by no test** —
  its sweep row alone — and is retired with this note.
- **The sites.** **195 production sites rewritten by the tool across 9
  modules** (`diplomacy.py` 56, `jealousy.py` 44, `vassal.py` 51, `naval.py`
  30, `main.py` 7, `diplomatic_executor.py` 4, `question_desk.py` /
  `naval_executor.py` / `diplomatic_ledger.py` 1 each), **16 by hand**: the
  four the dry run named (`_in_transit = (LEVER and x)` → `x`; `holds =
  courting and LEVER` → `courting`, exact because `courting` is a bool;
  `return LEVER and jealousy_dormant(world)` → `jealousy_dormant(world)`;
  the broken-rival clause's leading operand) plus the two it named as reads
  inside a Dict / a Call (`"lapse_counts_as_refusal": bool(LEVER)` → `True`;
  `petition.get("lapse_counts_as_refusal", LEVER)` → `True`); **five
  overlaps** (two levers in one statement: `if not (COUNSEL_NAMES_THE_COURT
  and COURT_FAVOUR_ACTIVE)`, `_reached and … and COURT_FAVOUR_ACTIVE`, the
  FIRES_SAY_WHY body nested in the CROWN_LOST body, the REBELLION_RETIRES
  body nested in the BREAK_IS_BRIEFED body, and `(THE_ANTECHAMBER or
  THE_PETITION_DIES…)` — that last one the first fold had already consumed,
  the skip was a no-op) — all listed by the batch-2 summary as promised,
  none reached ruff; and **one shape the tool's own parse check stopped
  before a byte was written: an outer `if` whose WHOLE body was the import
  and the lever test** (`mission_rows_for_state`'s DEFENSIVE_ALLIANCE
  block in `diplomatic_dialogue.py` — the two deletions left `if key ==
  "DEFENSIVE_ALLIANCE":` with no body; `ast.parse` raised, the run aborted
  after writing `diplomacy.py` and `question_desk.py`, the rest was applied
  on a second run and the block deleted by hand). The diplomacy levers'
  cross-module reads whose definitions the first run had already deleted
  (`COURT_FAVOUR_ACTIVE` ×3 and `REASSURE_ONLY_AT_ALLIANCE` ×2 in
  `diplomatic_dialogue.py` / `meta_executor.py`) were the hand's too, and
  their sweep rows dropped through the tool's own `drop_sweep_rows`. Two
  dead tails deleted (`mission_effect_text`'s "20% blowback" fallback
  return, the garrison arm's pop-and-return after an inlined `return`);
  `main.py`'s `lever = bool(getattr(…, True))` folded into the one read.
  **The orphaned lever headers** — forty-odd "flip lever … False = the
  prior …" comment blocks the constant deletion leaves standing (the tool
  deletes a block only when it names the lever) — re-titled to the rule they
  document, the "False =" sentences cut; the "(the HOST_RULE_ACTIVE idiom)"
  attributions on OTHER modules' live levers left as written. **77 sweep
  rows dropped** from 31 `tools/_sweep_*.json` (the tool re-serialises each
  file; the diff is a reformat plus the rows).
- **The test arms, decided one by one** (four agents by file group, the
  recipe and the traps as the brief, every file re-run green; 38 test
  files, −1,103 lines net): **88 whole deletions** — every
  `test_lever_down_*` / `test_the_lever_down_*` / `*_reproduces_*` /
  `*_restores_*` / control-arm test and arm comparison, two whole classes
  (`TestTheLever` in SR-5c, `TestTheFlipLever` in WO-9), the FA-S16-D4
  "not folded" source pin and its two-guards comparison, three autouse
  `_restore_levers` / `_levers_at_default` fixtures whose LEVERS tuples held
  only retired names; **19 tails trimmed** (the WO-9 rebellion count keeps
  its `capped == 18` pin and loses the uncapped arm; `test_defensive_
  alliance_has_reassure` keeps its live head); **5 un-parametrized to the
  lever-up arm** (IQ-4's `test_every_pair_on_the_board`, the courted pair,
  the hostile court, the real road, the morning progress); **5 re-pointed**
  (HC-4's lifeline arm now compares against every fleet sunk instead of the
  lever down — sinking Britain's hulls alone still reads "lifeline" because
  `combined_effective` pools the allies; IQ-4's `test_after_completion_
  nothing_is_frozen` marks the mission complete by hand since COURT no
  longer completes); **3 helpers de-armed** (`_drive` in FA-S16-D4,
  `_soult_refusal`'s `price_lever`, WO-9's `_REBELLION_RUNNER` argv slot);
  **5 restore lists shed** (IQ-4's `_LEVERS` loses 9 names and keeps 8
  live; FA slice 11's two; the two IQ-7 tuples removed whole); the
  `"JEALOUSY_SUPPRESS_SAME_PASS_REFIRE" in src` pins (A12, F6) now read
  `cooled_this_pass`; the `is True` attribute pins deleted. **Pins the dry
  run could not list, found by running:** `THE_REBELLION_RETIRES_ITS_
  QUESTION` flipped in `test_fa_s17_5_to_8_…` (a vassal lever in a
  diplomacy-grouped file). Nothing unresolved.
- **The reading:** levers **562 → 496** (492 on, 458 named by a test);
  functions over 500 lines 34 → 34; silent handlers 367 → 367; `CLAUDE.md`
  61.8 KB (the new LIVE STATE row paid for by shortening the S4 row — the
  first edit read 62,116 B and the ratchet said so). **The ratchet** lowered
  to `LEVERS_CAP 496`.
- **Gate:** `BASELINE_SERIES` + M1–M7 byte-identical with no re-record,
  corpus 902/902, the ratchet / tool / series / corpus pins green (1,057);
  every touched test file green; the full suite green on the hook.
  `score_run check` NOT run this batch (the S5 hand-off forbids the
  re-score; batch 2 proved the production rewrite moves no digest).
- **Next batches:** batch 4 = `world_state.py`, `combat_executor.py`,
  `enemy_ai.py`, `main.py` (the head of S6 or S7); **batch 5 — NEW, the
  plan left them unnamed:** the `game_logic/` modules OVER 3,000 lines that
  batch 2's floor excluded and batch 3 did not name hold **116** levers
  (`dispatch.py` 50, `coalition.py` 18, `ai_diplomacy.py` 15, `congress.py`
  13, `settlement_offers.py` 11, `diplomatic_templates.py` 4,
  `settlement_staging.py` 3, `settlement_actions.py` 2); the October 2026
  levers of batches 1–3 (26 + 56 + 12) join the first batch after October
  2026 closes. The plan's "done under 40" needs batches 4 and 5 both.


**✅ BATCH 4 LANDING RECORD — October 12, 2026 (the head of Pre-Deploy S8,
DD-1 Step 3's session).**

- **The batch, as defined and as measured.** `world_state.py` (23 levers),
  `combat_executor.py` (23), `enemy_ai.py` (39) and `main.py` (15) hold
  **100** by the census regex; **32 landed in October 2026** and keep their
  session (PRE_DEPLOY §5-4: world_state ×5 — the supply bite, the three
  SR-5a/economy-gate bills, `DISPERSION_IS_NOT_PUNISHED`; combat_executor
  ×14 — the SF-CL-1 / Step 7 group; enemy_ai ×8 — the economy gate's and
  Step 3's rungs; main ×5 — the interrupt trio, the net's fallback, the
  colours); **one is a decided `False`, not a lever: `LITERALS_DRILL_TO_HEAL`**
  (AIDR-D1, ruled held-out September 28, 2026 with its measured arm kept and
  a written re-open condition — it stays); **67 retired** (every one `True`
  in production, dated January 26 – September 29, 2026): enemy_ai ×30 (the
  FA slice-4 board rungs and their review round, F5's two, the AI drill fix's
  four, AI scoring, the naval AP parity, the spoils deference, the sovereign
  fear), combat_executor ×9 (CQ-30, NP-2's presence, WO-17's two, VP-R1 (a),
  the counter-punch credits, AAR10-X1, SRX-10), main ×10 (FA slice 6's five,
  FA-N44, FA-23, FA-N66, LV-13, the dismissal), world_state ×18 (R1-2,
  IQ-2, AAR4-X1, AAR-16, IQ-4, GE-3 #11, FA-D1 / D4 / D19, FA-S17-2 / 17,
  SR-5a's forecast, PC15-10, WO-17, WO-14, FA-N54, FA-S12-2's two). 61
  named in a landing record under `docs/`; six named by their tests alone
  (`AI_SCORING_ENABLED`, `SOVEREIGN_FEAR_ACTIVE`, `SOVEREIGN_PRESENCE_ACTIVE`,
  `DISMISSAL_IS_NOT_A_DEATH`, `THE_ASSAULT_ON_OUR_GARRISON_IS_REPORTED`,
  `SIEGE_ENDS_WITH_THE_WAR`'s tests are its sweep row and five docs).
- **The sites.** The tool rewrote the production sites across six modules
  (`enemy_ai.py`, `combat_executor.py`, `main.py`, `world_state.py`, plus
  the cross-module reads in `tactical_executor.py` and `war_status.py`) and
  dropped the sweep rows from 31 `tools/_sweep_*.json`; **19 by hand**: the
  three boolean operands outside a test position (`return LEVER and
  bool(broken)` → `bool(broken)`; `(LEVER and _corps_is_drilling(m))` →
  `_corps_is_drilling(m)`; `personality == "cautious" or (LEVER and
  personality == "literal")` → `personality in ("cautious", "literal")`),
  the eleven reads inside a keyword (`include_popup_passthroughs=not
  REFUSAL_ARMS_NEVER_DRAIN` ×9 and `drain_draft_notices=not
  LOAD_KEEPS_THE_DRAFT_NOTICES` ×2 → `False`), and the five overlaps the
  tool named (two `FIELD_PRICES_THE_TARGET_TOO` bodies nested in rewritten
  `if`s, the `EVERY_DEFAULT_LEAVES_THE_DRILL` operand, the
  `ADMIN_RECRUIT_SPARES_THE_SQUARE` import + operand in
  `tactical_executor.py`). `tools/_ai_drill_diag.py`'s read of the
  retired `AI_DRILLS_TO_HEAL` dropped; the attribution scripts that SET
  retired names (`_drill_fix_*`, `_f5_*`) left as written, like batch 3's.
  **The orphaned lever headers** (an agent, comments only): 16 blocks in
  `world_state.py`, 8 in `combat_executor.py`, 12 in `enemy_ai.py`, 4 in
  `main.py` re-titled to the rule they document; two docstrings that
  promised a lever-down arm trimmed by hand. Prior-batch orphans found and
  left for their own batch: `war_status.py`'s IQ-2 / LV-8 / FA-N75 / FA-D2
  blocks and `tactical_executor.py`'s AAR-23 line.
- **The test arms, decided one by one** (three agents by disjoint file
  group, the recipe and the traps as the brief; 43 files; every file re-run
  green): **≈ 60 whole deletions** — every `test_lever_down_*` /
  `test_with_the_lever_down_*` / `test_the_lever_off_arm_*` / control-arm /
  "reproduces the prior" test, a whole class (`TestTheLeversAreRealLevers`
  in WO-17, whose other pin was a source scan for a read that no longer
  exists), FA slice 6's `LEVERS` tuple and its autouse `_levers_at_default`
  fixture, IQ-1's `stale` fixture; **≈ 15 tails trimmed** (the live head
  kept, the flip-and-compare arm cut); **2 re-pointed** (F5's cap pins
  staged on `_check_passes_board()` instead of the boot, where the literal
  check — live now — refuses Deroy the walk-in the old arm needed); **1
  un-conditioned** (FA slice 2's brakes-ship-with-the-resolution pin); the
  `is True` attribute pins shed their retired lines (`test_all_nine_are_up`
  and kin keep the live ones); ≈ 10 restore-list entries and ≈ 12 unused
  imports removed. Nothing unresolved; no genuine regression surfaced.
- **The reading:** levers **496 → 429** (425 on, 392 named by a test);
  functions over 500 lines 34 → 34; silent handlers 367 → 367 (the next
  slice's business). **The ratchet** lowered to `LEVERS_CAP 429`.
- **Gate:** `BASELINE_SERIES` + M1–M7 byte-identical with no re-record
  (`test_ai_intent_threat_migration` / `_variance` / `_assurance`, 121),
  corpus 685 / 685, the ratchet / tool / series / corpus pins green; every
  touched test file green; `ruff` clean; the full suite green on the hook.
- **Next batches:** batch 5 = the `game_logic/` modules over 3,000 lines
  (116 levers — `dispatch.py` 50, `coalition.py` 18, `ai_diplomacy.py` 15,
  `congress.py` 13, `settlement_offers.py` 11, `diplomatic_templates.py` 4,
  `settlement_staging.py` 3, `settlement_actions.py` 2), the head of S7b;
  the October 2026 levers of batches 1–4 (26 + 56 + 12 + 32) join the first
  batch after October 2026 closes. The plan's "done under 40" needs batch 5
  and that November batch.

**✅ BATCH 5 LANDING RECORD — October 12, 2026 (the head of Pre-Deploy S7b,
CODE-3 + DD-C's session).**

- **The batch, as defined and as measured.** The `game_logic/` modules over
  3,000 lines hold **116** levers by the census regex (`dispatch.py` 50,
  `coalition.py` 18, `ai_diplomacy.py` 15, `congress.py` 13,
  `settlement_offers.py` 11, `diplomatic_templates.py` 4,
  `settlement_staging.py` 3, `settlement_actions.py` 2); **44 landed in
  October 2026** and keep their session (PRE_DEPLOY §5-4); of the **72**
  dated before October, **71 retired** and **one kept**:
  `THE_LEAGUE_TREATS_WHEN_SPENT` (SR-1d, September 26) is a STAGING device,
  bundled with four October levers in IQ-6's `_PRE_SR1D_LEAGUE` /
  `_PRE_SR1D_LEAGUE_CLI` (the drives that re-time the Austrian courtship) and
  in IQ-7's `turn6_snapshot` and `_pre_sr1d_league` fixtures — retired alone it
  would re-stage three files' boards twice. **It retires with that bundle in
  the first batch after October** (owner: CODE-1's November batch, named
  here and in STATUS ▶ NEXT UP; done when the bundle's five names are
  retired and the three files re-staged once, the IQ-6 / IQ-7 pins green).
  **Three of the 71 were `False`:** `THE_LEAGUE_GATE_COVERS_EVERY_WAR` and
  `THE_WAR_AGE_IS_THE_PAIRS` (PR-D1d's options (a) and (b), "measured and
  down" in SR-2c's record — no ruling and no re-open condition, unlike
  AIDR-D1's `LITERALS_DRILL_TO_HEAL`, which stays) and
  `INCOMING_OFFERS_DEFERRED` (dead since the SC-5 reversal, May 2026; its
  re-export from `settlement_preview` dropped).
- **The tool's own defect, found by this batch.** `retire_reference` seeded
  every climb with `value = True`: batches 1–4 retired only `True` levers, so
  it never showed. The first apply inlined all three `False` levers' dead
  branches — measured, `handle_incoming_settlement_offer_action` returned its
  deferred short-circuit for every offer. Reverted, fixed
  (`definition_value` reads `X = True` and `X: bool = False`; a `getattr`
  folds to the lever's own value; a definition that is not a bare boolean is
  refused), pinned (`tests/test_retire_lever_tool.py`
  `TestAFalseLeverKeepsItsOwnSide`, eight shapes, and two batch-5 names in the
  driver's refusal list), re-applied.
- **The sites.** The tool rewrote the production sites across ten modules
  (the eight, plus the cross-module reads in `diplomatic_advisory.py`,
  `diplomatic_ledger.py` and `main.py`) and dropped 58 sweep rows from 22
  `tools/_sweep_*.json`; **eight by hand**: the keyword read
  (`skip_nation_cooldown=True`), four boolean operands outside a test
  position (`no_court_left_to_alarm(...)` ×2, `lists_only_what_is_held`,
  `_has_substance = any(...)`), the side-effect fold (the prisoner loop's
  `continue` could never fire — `getattr` is pure — and went), the congress
  overlap (`if not (A and B): return ""` with both retired — the guard went)
  and `settlement_preview`'s re-export. **Dead code the tool leaves behind**,
  found by an AST scan for a statement after a terminator and removed by
  hand: three `return`s after an inlined `return` in `dispatch.py`,
  `settlement_war_age_start`'s unreachable option-(b) tail (it returns
  `int(war.get("created_turn") or 0)` now; its `_player_pair_meta` helper
  went with it), and a `getattr` read folded to a bare `if True:` in
  `congress.alarm_road`. The orphaned lever headers: an agent, comments and
  docstrings only, verified by AST equality against a pre-agent snapshot —
  50 blocks re-titled to the rule they document across seven modules (`dispatch.py` 17, `settlement_offers.py` 9, `ai_diplomacy.py` 8, `coalition.py` 7, `congress.py` 6, `settlement_staging.py` 2, `diplomatic_templates.py` 1), one comment the tool's re-flowed condition had dropped restored (`congress.process_end_of_turn`'s Review #17), and an unreachable lever-down branch in `congress._shut_out_lapse_reason` removed by hand. Prior-batch orphans found and left for their own batch: `diplomatic_advisory.py` (four), `diplomatic_ledger.py` (two), `ai_diplomacy.py` and `dispatch.py` (one each).
- **The test arms, decided one by one** (three agents by disjoint file
  group, the recipe and the traps as the brief; 30 files; every file re-run
  green): **65 whole deletions** (every `test_lever_down_*`, every control
  arm, every `is True` pin left empty), ≈ 12 tails trimmed, five `LEVERS`
  tuples / autouse fixtures and three helpers removed, **one re-staged**
  (`test_congress_of_paris::test_the_refusal_term_reaches_the_intent_weight`
  — its "without" baseline stubs `refusal_weight` and `revanche_weight` to 0
  under `monkeypatch.context()`, which is all the lever did; checked
  non-vacuous, 100 with the term against 85 without). One trim loses its
  sensitivity arm by construction
  (`test_iq2_collapse_dispatch::test_an_ally_is_never_offered_a_downgrade`:
  the old board's downgrade offer is no longer reachable to prove); the
  rule's attribution stays on IQ-2's record. Nothing unresolved; no live
  assertion failed.
- **The reading:** levers **429 → 358** (357 on, 329 named by a test);
  functions over 500 lines 34 → 34; silent handlers 367 → 367 (the session's
  next slice). **The ratchet** lowered to `LEVERS_CAP 358`.
- **Gate:** `BASELINE_SERIES` + M1–M7 byte-identical with no re-record
  (`test_ai_intent_threat_migration` / `_variance` / `_assurance`,
  `test_combat_sweep_metrics`), the CR-1 corpus harness and the tool's pins
  (1,140 together); every touched test file green; `ruff` clean; the full
  suite green on the hook.
- **Next batches** (measured at this session's close, `tools/retire_lever.py
  --list backend`): **batch 6 — NEW, the pre-October levers no batch named:**
  the `backend/ai/` and `backend/commands/` modules OVER 1,500 lines (batch 1
  took the ones under) and the top-level / `models/` modules hold **125**
  (`strategic.py` 19, `clause_guards.py` 15, `question_desk.py` 15,
  `economy_executor.py` 12, `llm_client.py` 11, `executor.py` 9,
  `dialogue_routing.py` 7, `disobedience.py` 7, `parser.py` 7,
  `campaign_log.py` 3, `diplomatic_executor.py` 3, `movement_executor.py` 3,
  `objection_v2.py` 3, `strategic_executor.py` 3, `dialogue_manager.py` 3, and
  one each in `meta_executor.py`, `display_names.py`, `intel_report.py`,
  `authority.py`, `marshal.py`) — the head of S8b; `LITERALS_DRILL_TO_HEAL`
  (AIDR-D1's decided `False`) and `THE_LEAGUE_TREATS_WHEN_SPENT` (above) are
  not in it. Then the October 2026 levers of batches 1–5 (26 + 56 + 12 + 32
  + 44) and `THE_LEAGUE_TREATS_WHEN_SPENT` with its staging bundle — the
  first batch after October 2026 closes. The plan's "done under 40" needs
  both.

**✅ BATCH 6 LANDING RECORD — October 12, 2026 (the head of Pre-Deploy S8b,
CODE-2a's session).**

- **The batch, as defined and as measured.** Every pre-October lever no
  batch had named — the `backend/ai/` and `backend/commands/` modules over
  1,500 lines and the top-level / `models/` modules — holds **126** by
  `tools/retire_lever.py --list backend` (batch 5's hand-off counted 125:
  `llm_client.py` holds 12, not 11): `strategic.py` 19, `clause_guards.py` 15,
  `question_desk.py` 15, `economy_executor.py` 12, `llm_client.py` 12,
  `executor.py` 9, `dialogue_routing.py` 7, `disobedience.py` 7, `parser.py` 7,
  three each in `campaign_log.py` / `diplomatic_executor.py` /
  `movement_executor.py` / `objection_v2.py` / `strategic_executor.py` /
  `dialogue_manager.py`, one each in `meta_executor.py` / `display_names.py` /
  `intel_report.py` / `authority.py` / `marshal.py`. **All 126 retired**, every
  one `True` in production, dated September 1 – 28, 2026; the census fell by
  **127** because `QUESTION_DESK_ACTIVE` was defined twice (`llm_client.py`
  and `question_desk.py`, FA slice 7's pair). Not in the batch and kept:
  `LITERALS_DRILL_TO_HEAL` (AIDR-D1's decided `False`),
  `THE_LEAGUE_TREATS_WHEN_SPENT` (batch 5's staging bundle), every October
  lever. **One named by nothing** — `economy_executor.LEVY_PAYS_THE_HOSTS_PRICE`
  (IQ1-3, no test, no doc, a sweep row's `old` text alone) — retired with this
  note; `llm_client.ACCENTS_NEVER_HIDE_A_NAME` was named by its docs alone
  (CRT-2, `COMMAND_ROBUSTNESS_SPEC.md` §12.10).
- **The tool's run.** The production rewrites across 28 modules; the run
  then died part-way through the sweep-row drops on a transient Windows
  write error (`OSError 22` on `tools/_sweep_sr2e.json` — the file was intact
  JSON, its earlier rows already dropped); the remaining twelve levers' rows
  were dropped through the tool's own `drop_sweep_rows`, and no sweep file
  names a batch-6 lever. **49 `tools/_sweep_*.json`** lost their rows.
- **The sites by hand.** The six the dry run named (`return LEVER and
  bool(…)` → `bool(…)`; `lawful = (not LEVER or f())` → `f()`, exact because
  `False or x` is `x`; the `HYBRIDS_SURVIVE_A_NEW_FLOW` operand; the three
  `_correction_survives(…, LEVER)` reads — **the predicate lost its
  `gate_active` parameter**, whose only purpose was the WO-13 lever, and
  `test_wo_slice10`'s False-arm assert went with it); **the overlaps** the
  tool skipped (`QUESTION_DESK_ACTIVE` paired with
  `THE_DESK_ANSWERS_THE_BOARD` / `THE_DESK_COUNTS_THE_POINTS` at four
  `question_desk` sites and in `llm_client._routes_to_the_desk`, the second
  definition deleted by hand; the objection band's two-lever condition);
  and **the reads no dry run lists** — found by an AST scan for every `Name`,
  `Attribute`, import `alias` and string naming a retired lever, since ruff's
  F821 sees only bare names: four ALIASED imports (`A_MARCH_KEEPS_ITS_TAIL as
  _KEEP_TAIL` in `enemy_ai` and `combat_executor`,
  `THE_DESK_ANSWERS_THE_WAR_QUESTION as _war_lever` and
  `THE_DESK_READS_THE_ODDS as _odds_lever` in `state_desk`,
  `OBJECTION_TRUST_DAMPER_ACTIVE as _DAMPER_ACTIVE` in `strategic_executor`,
  `AN_ANSWER_IS_READ_CLOSED as _CLOSED` in `main.py`) and two attribute reads
  (`_routing.A_QUESTION_NEVER_ANSWERS` in `diplomatic_executor`,
  `_road.THE_ROAD_LAW_IS_READ_WHERE_QUOTED` in `strategic_executor` — its
  `if/else` inlined by hand, the `_road_verdict` block it fed deleted as
  unreachable). The attribution script `tools/_cx_sweep_both_arms.py`, which
  SETS a retired name, left as written (batches 3–4's precedent).
- **Dead code the tool leaves behind**, found by an AST scan for a statement
  after a terminator and a constant test, compared against HEAD: **fourteen
  unreachable tails** after an inlined `return` (`question_desk` ×3,
  `strategic` ×4, `strategic_executor` ×2, `campaign_log`, `economy_executor`,
  `executor`'s old addressee body, and `dialogue_routing`'s 109-line lever-down
  answer reader) and one `if True:` in `parser.py` — removed by hand. What
  the tails orphaned, deleted: `economy_executor._msg_subs_closed` (found by
  an identifier census against HEAD), `CommandExecutor._ADDRESSEE_IS_AN_ORDER_RE`
  and `_NOT_AN_ADDRESS_RE` (read only by the comma-only addressee body CX-7
  replaced), and `diplomatic_executor`'s second `mission_type == "CANCEL"` arm
  (the pre-IQ-4 recall, unreachable once `MISSION_CANCEL_READS_THE_NAME`'s
  arm above it always runs).
- **The orphaned lever headers**: an agent, comments and docstrings only,
  proven by `ast.dump` equality (docstrings blanked) against a pre-agent
  snapshot — ≈ 110 blocks re-titled across 23 of the 28 modules
  (`clause_guards.py` 16, `economy_executor.py` 15, `executor.py` 10,
  `strategic.py` 10, `llm_client.py` 8, `dialogue_routing.py` 7, …). Four
  headers the tool had deleted WITH their constants (it deletes a lever's
  inline comment and any block naming it) carried a slice's record and were
  restored as the rules they list: FA slice 7's six in `llm_client.py` and
  three in `parser.py`, FA slice 5's Road Law seven and FA slice 3's review
  round in `strategic.py`. Two prior-batch orphans in the same files fixed
  (`meta_executor.collapse_turn_end_fields`, `campaign_log`'s coalition
  dissolution); `counsel.py` and `strategic_parser.py` each had one comment
  naming a retired lever, re-worded.
- **The test arms, decided one by one** (three agents by disjoint file group,
  the recipe and the traps as the brief; 60 test files, −2,365 lines net;
  every file re-run green — 1,606 / 1,603 / 878 + 1 xfail): ≈ 180 whole
  deletions (every `test_lever_down_*`, every control arm, every `is True`
  pin, five `LEVERS` / `_restore_*` autouse fixtures whose retired names
  raised `AttributeError` on setup — 689 setup errors in one group alone —
  `TestTheSensitivityArm` (CR-7-1), `TestTheSpawnHelperCannotLie` and
  WO slice 10's `ungated` ambient fixture, `TestTheLevers` (CX-2)); ≈ 35
  trims; five un-parametrized to the lever-up arm; four re-pointed (WO slice
  9's normalisation pin now reads the damped-gain loop, IQ-7's statement-order
  pin runs on the live router, FA-26's census keeps its `stage_redemption`
  half, CN's lever pin reads the marshal's arm). **A dry-run false positive
  to remember:** the tool's test grep matched `A_QUESTION_NEVER_ANSWERS` as a
  prefix of the live `main.A_QUESTION_NEVER_ANSWERS_AN_INTERRUPT`
  (`test_sf5_…` — left as written). Nothing unresolved; no live assertion
  failed; `test_ai_intent_threat_migration.py` untouched (comments only).
- **The reading:** levers **358 → 231** (230 on, 204 named by a test);
  functions over 500 lines 34 → 34; silent handlers 6 → 6. **The ratchet**
  lowered to `LEVERS_CAP 231`.
- **Gate:** `BASELINE_SERIES` + M1–M7 byte-identical with no re-record
  (`test_ai_intent_threat_migration` / `_variance` / `_assurance`,
  `test_combat_sweep_metrics`), the CR-1 corpus harness, the tool's pins, the
  F2 shadow pin, the DD-C census and four of the touched files (1,708
  together); `ruff` clean; the full suite on the hook.
- **Next batch:** the October 2026 levers of batches 1–6 and
  `THE_LEAGUE_TREATS_WHEN_SPENT` with its staging bundle — the first batch
  after October 2026 closes (owner: CODE-1's November batch, STATUS ▶ NEXT
  UP). With it the census reads ≈ 2 (`LITERALS_DRILL_TO_HEAL` and whatever
  November lands): the plan's "done under 40" is met by that batch.

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
regression) — pinned by `tests/test_ep_f2_the_display_name_pass.py::
test_the_humaniser_is_the_module_level_name_in_the_combat_executor` (which
forbids any function-local import inside `_execute_attack`); run it after
every move. *(Corrected October 12, 2026: this line used to name a
`tools/_local_import_census.py`, which does not exist.)*

**Done when:** no function over 500 lines in the eight named; the census pin
caps "functions over 500 lines" at the new count and ratchets down.

**CODE-2a LANDING RECORD — `_execute_attack` (Pre-Deploy S8b, October 12,
2026).** *The stage list, written before the cut (recipe step 1).* The
function (lines 6021–9933 on `3ed94831`, 3,913 lines) is cut at TOP-LEVEL
statement boundaries only — no statement of its body crosses a cut, the
largest single one is 386 lines — into twenty stages, each
`_attack_<stage>(self, ctx)`, in this order:

| # | Stage | Its header in the old body | What it holds |
|---|---|---|---|
| 1 | `_attack_open` | "Auto-break square formation (Session 67)" | the square break, the war-purpose stager, counter-punch, drill and moved-artillery gates |
| 2 | `_attack_reckless_cavalry` | "CAVALRY RECKLESSNESS CHECK (Phase 3)" | the glorious-charge popup or the AI auto-charge |
| 3 | `_attack_nearest_target` | "ESP-EV-4 fix (July 12, 2026)" | a target left open, or a named nation (PT-H3), resolved to the nearest foe |
| 4 | `_attack_resolve_target` | "FUZZY MATCHING" | fuzzy match, EC-9 coalition guard, ESP-EV-4 guessed-target guard |
| 5 | `_attack_range_check` | "RANGE CHECK" | the target's location and the range check |
| 6 | `_attack_engagement_and_crossing` | "NORMAL ATTACK LOGIC" | engagement lock, the DEF-5 crossing gate, NV-9 guns over a strait |
| 7 | `_attack_war_and_bombard_target` | "AUTO WAR DECLARATION" | auto war declaration; region-name bombardment targeting, garrisons, raids |
| 8 | `_attack_routing_and_muster` | "BOMBARDMENT ROUTING (§3)" | opening guidance, bombardment routing, PF-7, the W6-4 muster gate |
| 9 | `_attack_cover_flank_charge` | "ALLY COVERS RETREAT SYSTEM" | the covering ally, the flank origin, Ney's two-region charge |
| 10 | `_attack_reinforce_and_coordinate` | "REINFORCEMENT (Phase 7, Session 61a)" | arrivals, coordination, casualty participants, NP-V presence |
| 11 | `_attack_overwatch_and_auto_bombard` | "ARTILLERY OVERWATCH (Session 68)" | the overwatch count, SUPPORT auto-bombardment |
| 12 | `_attack_dead_defender` | "DEAD-DEFENDER CHECK" | the win without a battle |
| 13 | `_attack_resolve_combat` | "RESOLVE COMBAT" | `resolve_battle`, solo or coordinated, the casualty distribution |
| 14 | `_attack_battle_record` | "COORDINATION CONTEXT FOR BATTLE REPORT" | coordination context, W6-1 counts, W6-2 name, W6-6 voices |
| 15 | `_attack_relationships_and_report` | "WIN/LOSS RELATIONSHIP FORMULA" | relationships, the observation re-pick, kept orders, destruction |
| 16 | `_attack_forced_retreat` | "FORCED RETREAT" | broken armies retreat or break before the advance |
| 17 | `_attack_advance_and_capture` | "ATTACKER MOVEMENT & REGION CONQUEST LOGIC" | the advance, the capture, the R1 pipeline, the result dict |
| 18 | `_attack_compose_result` | "BD (Battle Diorama)" | the diorama and the result's riders |
| 19 | `_attack_tutorial_and_casualty_lines` | "FIRST-TIME COORDINATION TUTORIAL" | the tutorial, IQ-5 / CA8-1 / CO-6 casualty lines, the capture choice |
| 20 | `_attack_trust_and_exhaustion` | "REINFORCEMENT TRUST PENALTIES" | trust penalties, SR-7d doctrine, exhaustion, Berthier's advisory |

**The contract the cut keeps.** One `AttackContext` (`@dataclass(slots=True,
repr=False, eq=False)`, module level) built once at the driver's head and
never on the wire. The six parameters are init fields; a name read or written
in MORE than one stage is a `field(init=False)` with NO default, so reading it
before any stage assigned it raises (`AttributeError`) exactly where the
local raised (`UnboundLocalError`); a name used in one stage stays a plain
local of that stage. The old body's ten `locals().get("x", d)` / `"x" in
locals()` reads of conditionally-assigned names become `getattr(ctx, "x", d)`
/ `hasattr(ctx, "x")` — exact only because the fields have no default. A
non-final stage that falls off its end returns the module sentinel
`_NEXT_STAGE`; every early `return` is kept verbatim, so a `return` of a
value that may be `None` still ends the attack with `None` (the driver tests
`is not _NEXT_STAGE`, not truthiness). A function-local import read by a
later stage is repeated at that stage's head; the nested
`_stage_war_purpose_for_attack` stays in stage 1 and rides `ctx`. The cut is
mechanical (`scratchpad` tool `stage_attack.py`, AST + `symtable`), and
refuses unless every stage's symbol table shows no old local read as a
global.

*The outcome (✅ LANDED October 12, 2026).* Of the old body's 420 locals,
**100 ride the context** (6 of them the parameters) and 320 stayed local to
one stage; 10 of 10 `locals()` reads rewritten; two imports repeated at
stage 18's head (`jealousy as _jealousy`, `build_battle_diorama`). Stage sizes
73 – 414 lines; **functions over 500 lines 34 → 33**, `FUNCTIONS_OVER_500_CAP`
lowered. **One departure from recipe step 4, said so:** the twenty stages
were cut in ONE application of the tool, not one at a time with the fast
gate between — the cut is a single mechanical transform whose proof is the
symbol-table check plus the byte-identical replay, and a per-stage run would
have gated the same transform twenty times. **The net:** `BASELINE_SERIES` +
M1–M7 byte-identical with no re-record, the CR-1 corpus, every test file
naming the combat executor (6,780 with the series and the ratchet) — the
only failures were **30 source-text pins** in 20 files that read "the
attack" as one function's text or named a now-`ctx.` local; each re-pointed,
none weakened (two agents on disjoint files, the rule "same assertion, where
the code now lives"), through the new `tests/_attack_stages.py`
(`attack_stage_names()` read off the driver, `attack_functions()`,
`is_attack_function()`, `attack_source()`, `stage_source()`). The F2 shadow
pin (`test_the_humaniser_is_the_module_level_name_in_the_combat_executor`)
now forbids a bare function-local humaniser import in every stage. One
sharpening found on the way: IQ-2's conquest-stamp anchor `conquest_from =
target_region.controller` also matched the charge's `charge_conquest_from`
line; its `ctx.` form cannot. **The shape is pinned** in
`tests/test_code2a_the_attack_is_staged.py`: the twenty stages in order, the
driver's body nothing but the context, the loop and the last stage, the
identity test `is not _NEXT_STAGE`, no stage over 500, the context's slots
and no-default contract, and an attack's result carrying no `AttackContext`
or sentinel. No rule moved — `SYSTEMS_REFERENCE.md` gains no section. Next
in CODE-2: **CODE-2b** at `PRE_DEPLOY_PLAN.md` §2's S10 (the monster
functions the deep dives did not absorb — DD-1 took `_process_dialogue_choice`
and `_ratify_treaty`); S9 (UXR-2) comes first.

**CODE-2b LANDING RECORD, SLICE 1 — `execute_command` (Pre-Deploy S10,
October 13, 2026).** *A correction first:* the S10 hand-off placed
`execute_command` in `backend/commands/executor.py`. It is the `/command`
route in **`backend/main.py`** (line 3136 on `e6aa24db`, 1,627 lines), under
`@app.post("/command")` and `@_records_transcript`. *The stage list, written
before the cut (recipe step 1).* The function is a 45-line prelude, then ONE
`try:` of 1,581 lines whose `except Exception as e:` is the route's error
reply. So the cut runs at the top-level statement boundaries of the `try`'s
body. The prelude becomes a stage the driver calls BEFORE the `try`, exactly
where it ran, so an exception there still escapes the route's own handler.
The handler stays in the driver verbatim. Each stage is a module-level
`_command_<stage>(ctx)` in `main.py`, so `world`, `parser` and `executor`
stay the module globals the suite's world swaps replace:

| # | Stage | Its header in the old body | What it holds |
|---|---|---|---|
| 0 | `_command_open` | "CR-7-3 rule 5" (the prelude, outside the `try`) | the relay stash popped, the DD-0 trace opened, the CR-7-9 let-go, `_relay_question` |
| 1 | `_command_guards` | "GAME-OVER GUARD" | the war is over, a blank line, the typed `why` |
| 2 | `_command_clarification_answer` | "CR-2: PENDING COMMAND CLARIFICATION" | the clarification and delegation imports, a typed answer to the pending question |
| 3 | `_command_interrupt_answer` | "PENDING STRATEGIC INTERRUPT CHECK" | a typed answer to a marshal's interrupt (SF5-X1/X2, PC15-2) |
| 4 | `_command_pending_answers` | "W6-0 (BUG-CA-1): PENDING-QUESTION ROUTER" | the objection's words (CA9-N5), the capture answer, a dialogue's own option |
| 5 | `_command_carryover_and_lost_name` | "CR-4: CONTEXT CARRYOVER" | shorthand resolved against the history; PC15-4 the fallen or captured name |
| 6 | `_command_parse` | "Parse command" | the SF-CMD-1 premise, `parser.parse`, FA-39 provenance, the request's own fields |
| 7 | `_command_history` | "COMMAND HISTORY" | the history entry, never for a line a dialogue consumed |
| 8 | `_command_delegation` | "CR-5: PERSONALITY-BIASED DISAMBIGUATION" | a delegation verb routed by character: cautious, aggressive or ask |
| 9 | `_command_dialogue_routing` | "DIPLOMATIC DIALOGUE RESPONSE ROUTING" | a pending dialogue takes the line only when it claims it (CA9, PT-A3, WO-7, IQ-7) |
| 10 | `_command_ordinary_road` | `if not _dialogue_took_the_line:` | dialogue-only words, WO-1, CR-2 did-you-mean, PARSE-NEG, Berthier's parse recovery, `executor.execute` |
| 11 | `_command_riders` | "CR-2: parser warnings" | warnings and the typo note, CR-7-3 `_stamp_relay`, CR-5's notes and first-use hint |
| 12 | `_command_executor_recovery` | "BERTHIER EXECUTOR RECOVERY" | no marshal named: the CR-4 focus reissue, CX3-X2, CR-2 marshal choice, Berthier |
| 13 | `_command_question_returns` | "CHECK FOR OBJECTION" | a result carrying a question or popup returns whole |
| 14 | `_command_respond` | "FEEDBACK GENERATION (Phase 5)" | live-mode feedback and the response |

**Three things the attack's cut did not meet.** (1) `_stamp_relay`, a nested
def, declares `nonlocal _relay_obj` and is re-called by a later stage
(stage 12, after the focus reissue rebinds `parsed` and `result`). The name
rides the context, so the `nonlocal` line goes: `ctx._relay_obj = …` is the
same write to the same shared cell. It is the one line the cut deletes rather
than moves. (2) The `try`-body stages lose four columns of indentation. A line
inside a multi-line string is never re-indented, except a nested function's
docstring. (3) The proof is stronger than S8b's. On top of its symbol-table
check, every stage's statements must dump AST-equal to the old body's, once
the shared names are rewritten to `ctx.<name>` and the dropped `nonlocal` is
removed (`scratchpad` tool `stage_fn.py`).

*The outcome (✅ LANDED October 13, 2026).*
- **The context.** Of the old body's 171 locals, **18 ride `CommandContext`**
  (1 of them `request`), and the other 153 stayed local to one stage.
- **What else moved.** Two nested defs ride the context (`_relay_question`,
  `_stamp_relay`). One `nonlocal` line was dropped. Ten import statements are
  repeated at the heads of stages 8 and 10–13, grouped per original statement.
- **Unchanged.** The handler is byte-for-byte the old one, AST-checked.
- **Sizes.** Stages run 41–372 lines (the door 48, the driver 73).
  **Functions over 500 lines 33 → 32**, and `FUNCTIONS_OVER_500_CAP` is
  lowered to match.
- **The F2 class is empty.** No local import in the route binds a name
  `main.py` binds at module level, and now a pin keeps it that way.

**The net:**
- `score_run.py check` against `2026_10_05_sfr` gives stdout identical to the
  same check on `e6aa24db`.
- The full parallel suite: 30,647 passed, 7 failed.
  - **Five** failures were source pins in four files that read the route as
    one function's text, or named a now-`ctx.` local. Each is re-pointed
    through the new `tests/_command_stages.py` (`command_stage_names()` read
    off the driver, `command_source()`, `stage_source()`). The rule is the
    same assertion where the code now lives; none was weakened.
  - **Two** (`test_fa_slice8_…::TestAMutationIsNeverMaskedByStaleBytecode`)
    fail on the unchanged tree whenever the shell carries
    `PYTHONDONTWRITEBYTECODE=1`, as this session's did. They pass with it
    unset. The commit runs without it, as the hook always had.

**The shape is pinned** in `tests/test_code2b_the_command_is_staged.py`:
- the fifteen stages in order;
- the driver's body is `[Assign, Expr, Try]`, the door called before the
  `try`, and the `try` holding only the loop and the last stage;
- the identity test;
- the handler is still the route's one error reply, and a stage that raises
  gets it (driven);
- no stage over 500 lines;
- the context's slots and no-default contract;
- no context or sentinel on the wire;
- no stage-local import shadowing a module name.

No rule moved, so `SYSTEMS_REFERENCE.md` gains no section. **Next in CODE-2b:**
slice 2 `format_event_oneliner`, then slice 3 `_execute_strategic_command`.

**CODE-2b LANDING RECORD, SLICE 2 — `format_event_oneliner` (Pre-Deploy S10,
October 13, 2026).** *The stage list, written before the cut (recipe step 1).*
The function (`backend/campaign_log.py`, line 1847 on `b135a7d0`, 1,538 lines)
is a head and then 160-odd `if event_type == …:` arms, every one of which
returns, and the `Event: …` fall-through. The cut runs at the body's top-level
statement boundaries, at the file's own banners. The one unbannered run
("battle" to "defiance", 587 lines) is cut into three families, and the order
is unchanged. Each stage is a module-level `_oneliner_<stage>(ctx)`:

| # | Stage | Its header in the old body | What it holds |
|---|---|---|---|
| 1 | `_oneliner_head` | `event_type = event.get("type", "")` | the type read, the commitments route, a war that shatters a treaty |
| 2 | `_oneliner_the_field` | `if event_type == "battle":` | battles, bombardments, escalades, retreats, broken and recovered, a province captured |
| 3 | `_oneliner_purse_and_court` | `if event_type == "recruitment":` | levies, works, bankruptcy, desertion; jealousy and glory; petitions, rentes, commissions, substitutes; voided orders, agendas, new nations; dotations and estates |
| 4 | `_oneliner_orders_and_fates` | `if event_type == "objection":` | objections, the campaign's end, the congress, literal fidelity; a marshal captured … released; standing orders, defiance |
| 5 | `_oneliner_diplomacy` | "── Diplomacy events (Session 8D)" | treaties, war aims, settlements, the ally's entry, AI-AI treaties, the D5 counter-instruments, crises, designs |
| 6 | `_oneliner_laws` | "── SR-5r "The Laws"" | a law enacted, repealed or lapsed |
| 7 | `_oneliner_the_sea` | "── DEF-5 naval (NV-0..NV-3)" | fleets, blockades, the Continental System, the straits, the Descent, the expeditions; the flip in play |
| 8 | `_oneliner_allegiance` | "DD-1 S8 Step 3 — the verbs" | the allegiance bid, a province returned, the auction resolved |
| 9 | `_oneliner_cascades_and_coalitions` | "Deep audit fix: new event types" | a war declared, the cascades, a coalition declared or dissolved |
| 10 | `_oneliner_the_fallen_and_the_clients` | "V3 Session 8: new event types" | a nation eliminated, the vassals' moves, the client's petition, a member leaving |
| 11 | `_oneliner_proposals_and_ultimatums` | "── R8 Session 6" | AI proposals and ultimatums, counter-offers, missions, the proposal queue, garrisons, relationships, the peace ratified |
| 12 | `_oneliner_unknown` | `return f"Event: {event_type}"` | the fall-through: an unknown type is named, never dropped |

**The tool needed more than a config entry.** It is slice 1's `stage_fn.py`
(scratchpad), and slices 2–3 found four things in it:
- **A missing import road.** `campaign_log.py` has no `typing` line to
  extend, so the tool now adds its imports after the module's first one. By
  hand, the file then takes `import dataclasses` rather than `from
  dataclasses import dataclass, field`, because `_player_marshal_involved`'s loop
  variable is called `field` (ruff F402).
- **A false refusal.** The `{x=}` refusal read the AST, which cannot tell
  `f"{path=}"` from a literal `path=` followed by `{path}`. It now reads the
  f-string's own text (slice 3, `_execute_strategic_command`'s order print).
- **An honest proof difference.** `world: WorldState = …` becomes
  `ctx.world: WorldState = …`, whose `simple` flag is 0. A function scope
  evaluates neither annotation, and the proof's expected tree now says so.
- **Two new rules (`confine=True`).** Under slice 1's rule, any name used in
  two stages rode the context. Here that would have put 36 fields on it, 33
  of them arm temporaries that only share a spelling (`nation`, `target`,
  `marshal`). Slice 3 refused outright on `_road`, a module alias in one
  stage and an unrelated string in another. A name now stays a plain local
  of each stage that uses it when either rule holds:
  - **confine:** every binding sits in a branch that always ends in
    `return` or `raise`, so no value can leave the statement that bound it;
  - **split:** a conservative definite-assignment pass shows that no stage
    ever reads it before binding it on every path.

  Neither rule applies to a name read in a closure, deleted, named by
  `nonlocal`, or bound by a walrus. A wrong call cannot pass silently either:
  a stage that read such a name unbound would read it as a global, which the
  symtable proof refuses.

*The outcome (✅ LANDED October 13, 2026).*
- **The context.** Of the old body's 195 locals, **4 ride `OnelinerContext`**
  (`event`, `player_nation`, `world`, `event_type`), the first three of them
  the parameters. 32 more names appear in two or more stages but are
  confined, and the rest are local to one stage.
- **Unchanged.** No import is repeated, no nested def or `nonlocal` exists,
  and every stage is AST-equal to the old statements once the four names
  read `ctx.<name>`.
- **Sizes.** Stages run 4–357 lines (the fall-through 4, the head 21, the
  diplomacy family 357), and the driver is 74. **Functions over 500 lines
  32 → 31**, and `FUNCTIONS_OVER_500_CAP` is lowered to match.
- **The F2 class is empty.** Six local imports remain, none binding a
  module-level name of `campaign_log.py`.

**The net:**
- `score_run.py check` against `2026_10_05_sfr` gives stdout identical to the
  same check on `b135a7d0`.
- A before/after sweep (scratchpad, not committed): 178 event types (every
  literal the arms test, the commitments routes, and one unknown), each
  rendered from a bare event and from three populated ones, with and without
  a world. All 1,424 calls are identical, including the 140 that raise on
  synthetic garbage, with the same exception and the same message.
- The 106 test files that name the function or the module (6,220 tests)
  pass. No pin needed re-pointing: none read the function's own text, and
  no test literal stopped matching the file.

**The shape is pinned** in `tests/test_code2b_the_oneliner_is_staged.py`
(23):
- the twelve stages in order, and the driver's body `[Assign, For, Return]`
  with the fall-through last;
- the identity test, and the signature unchanged;
- no stage over 500 lines;
- an unknown type passes every stage to the fall-through (driven);
- the context's slots and no-default contract, and a line is a `str`;
- no stage-local import shadowing a module name.

The generic `tests/_staged_functions.py` reads any staged driver, a module
function or a method.

**CODE-2b LANDING RECORD, SLICE 3 — `_execute_strategic_command` (Pre-Deploy
S10, October 13, 2026).** *The stage list, written before the cut (recipe step
1).* The method (`StrategicExecutor._execute_strategic_command`,
`backend/commands/strategic_executor.py`, line 618 on the slice-2 commit,
1,402 lines) is a straight pipeline with its own `──` banners. It runs
validation, then the road, then the V2a objection, then the order, then the
first step, then the reply. The cut runs at the body's top-level statement
boundaries. Each stage is a method `_strategic_<stage>(self, ctx)` on the same
class, so `self._executor` and the module globals the suite patches are read
exactly as before:

| # | Stage | Its header in the old body | What it holds |
|---|---|---|---|
| 1 | `_strategic_open` | the function's head | the world and the marshal found; the broken and the routed refuse (7A-1, FA-9); the state speaks first (CRT-9); an identical order already carried is a no-op (F10) |
| 2 | `_strategic_square_and_engagement` | "Auto-break square formation (Session 67" | the square breaks; guns cannot chase; no order while engaged; no self-target |
| 3 | `_strategic_generic_target` | "── Resolve generic/vague targets" | a bare march asks where (CX3-R2); a generic target resolved |
| 4 | `_strategic_validate_target` | "── Validate target" | SUPPORT names a friendly marshal; PURSUE an enemy one, at war and sighted |
| 5 | `_strategic_hold` | "── HOLD: default target to current location (Bug #7)" | HOLD defaults to where he stands (CRT-2); a redundant HOLD refused |
| 6 | `_strategic_path` | "── Build path for movement orders" | the road for MOVE_TO, PURSUE, SUPPORT and HOLD, from where our scouts saw the quarry (FA-S17-9) |
| 7 | `_strategic_objection` | "── Strategic objection check (V2a)" | the V2a objection, before any order exists |
| 8 | `_strategic_create_order` | "── Build condition" | the condition, the `StrategicOrder`, the old order cancelled, the event logged |
| 9 | `_strategic_first_step` | "── Execute first step immediately" | PURSUE in the same province, the march's first leg, SUPPORT already beside its friend |
| 10 | `_strategic_response` | "── Build response" | the reply's road, the grounding note (FA-54), the MOVE_TO lines |
| 11 | `_strategic_cost_and_reply` | "CR-7-4 item 6 — THE ECHO" | the condition echoed, the order priced (SR-2e), the acknowledgement, the reply |

*The outcome (✅ LANDED October 13, 2026).*
- **The context.** Of the old body's 163 locals (`self` aside), **22 ride
  `StrategicCommandContext`**: the three parameters, then `world`,
  `marshal`, `strategic_type`, `target`, `path`, `order` and the reply's
  pieces. Slice 2's two rules keep nine more names local. Two are confined
  (`message`, `turns_left`). Seven are split, bound before read in every
  stage that uses them: `_road`, `ally`, `ally_m`, `enemy`, `enemy_m`,
  `existing_order` and `personality`, each checked by hand.
- **What else moved.** One import is repeated:
  `StrategicOrder`/`StrategicCondition` at `_strategic_create_order`'s head.
  The original line stays in `_strategic_open`, where the function's head
  had it.
- **Unchanged.** The three early `return None`s ("fall through to tactical
  routing") still end the call with `None`, because the driver tests the
  sentinel.
- **Sizes.** Stages run 31–298 lines, and the driver is 56. **Functions over
  500 lines 31 → 30**, and `FUNCTIONS_OVER_500_CAP` is lowered to match.
- **The F2 class is empty.** 24 local imports remain across the stages, and
  none binds a module-level name of `strategic_executor.py`.

**The net:**
- `score_run.py check` against `2026_10_05_sfr` gives stdout identical to the
  same check on the slice-2 commit.
- The 184 test files on the strategic road (the executor, the order types,
  the state probe, `march to` / `pursue`), with `BASELINE_SERIES` and M1–M7:
  9,191 passed with no re-record.
- **Four pins were re-pointed before that run.** A scan of every test string
  literal that matched `strategic_executor.py` before the cut but not after
  found three; the fourth reads functions by name. The rule is the same
  assertion where the code now lives:
  - CA9's PURSUE window (`enemy = ctx.world.get_marshal(ctx.target)`);
  - PT-G's acknowledgement call (`marshal_name=ctx.marshal.name`);
  - WO-16's budget reader (`in ctx.world.objection_popups_this_turn`);
  - **the NPC-12 producer census** (`test_sf7_s7_the_name_and_the_rank.py`),
    which selects functions BY NAME. It would have passed *vacuously* over a
    56-line driver, so it now names the stages, read off the driver.
- **A fifth pin was found by the hook, not by the slice's own family run.**
  `test_wo_slice13_corridor_direction.py`'s WO-17 census scans every
  backend `passable_for` pathfind call and requires its start argument to
  EQUAL `marshal.location`. In `_strategic_path` the mover is `ctx.marshal`
  (`pathfinder(ctx.marshal.location, dest, passable_for=ctx.marshal.nation)`),
  so the census now accepts `ctx.marshal.location` as the same man.
  - The literal scan could not see it, because `marshal.location` is still a
    substring of the new text.
  - The family grep missed it because the file names neither the executor
    nor an order type.
  - The class to check next time: **a pin that extracts an expression and
    compares it for equality**, not for containment.
- `state_probe._standing_reason`'s docstring names the stage it mirrors.

**The shape is pinned** in
`tests/test_code2b_the_strategic_order_is_staged.py` (21):
- the eleven stages in order, and the driver's body `[Assign, For,
  Return]`;
- the identity test, and the signature unchanged;
- no stage over 500 lines;
- R11's delegation forwards the driver and no stage;
- a missing world or marshal still answers `None` (driven);
- the context's slots and no-default contract;
- nothing on the wire from a real MOVE_TO;
- no stage-local import shadowing a module name.

**CODE-2b is DONE** (S10 STRUCK, October 13, 2026). None of its three
functions is over 500 lines, and the census reads 30. No rule moved, so
`SYSTEMS_REFERENCE.md` gains no section.

**CODE-2 itself is NOT done. This was found closing S10, by measuring the
eight named functions rather than trusting the routing.** Six of the eight
are under 500 lines:
- `_execute_attack` 76 (CODE-2a);
- `execute_command` 73, `format_event_oneliner` 74 and
  `_execute_strategic_command` 56 (CODE-2b);
- `_parse_with_mock_chain` 38 and `_execute_one` 11 (DD-0).

**Two are not:**
- `DiplomaticExecutor._process_dialogue_choice` at **2,210** lines;
- `WorldState._ratify_treaty` at **1,024**.

`PRE_DEPLOY_PLAN.md` §3.1 had DD-1's structural fix "absorb" both splits.
DD-1 S7 Slice B lifted the ratifier's guard sequence out into
`treaty.can_sign` (1,179 → 1,024), but neither function was staged, and
nothing still owned the split. They are re-homed as **CODE-2c**, below.

**CODE-2c — the two DD-1 left whole (the user's ruling, October 13, 2026:
row S10b, the next session, before UXR-3).**
- **Owner row:** `PRE_DEPLOY_PLAN.md` §2 S10b.
- **Landing slices:** two, one commit each, run straight through: the user's
  October 13 ruling made every decision in advance, so there is no review pause.
  - **Slice 1: `WorldState._ratify_treaty`** (`backend/models/world_state.py`,
    1,024 lines). It runs as top-level statements (a state map, the clause
    loops, the forced-alliance block, the 292-line `if is_player_treaty:`),
    so the tool's body mode cuts it as it stands: `cls="WorldState"`,
    `confine=True`.
  - **Slice 2: `DiplomaticExecutor._process_dialogue_choice`**
    (`backend/commands/diplomatic_executor.py`, 2,210 lines). Past its imports, its body is
    ONE `if action == "dismiss": … elif …` chain of 2,195 lines, a single
    statement that no top-level cut can split. The tool needs an
    **elif-chain mode**, where each run of arms becomes a stage. The proof
    must show three things:
    - the tests are evaluated in the same order;
    - the first true arm alone runs;
    - an arm that falls off its end still returns `None` from the driver.

    It carries 73 local imports, so the F2 check matters most here.

    **Measured October 13, 2026, and the design decided on it:**
    - **The shape.** The chain has 72 arms and its `else` (measured at first
      as "73 arms", the `else` counted as one; corrected by slice 2's own
      pin). The largest is 187 lines
      (`execute_ultimatum`), so none needs a cut of its own. No arm's test binds
      a name (no walrus). The chain ends in its own `else`, the unknown-action
      reply. Its head is three `from … import`s and
      `target_nation = dialogue.get("target_nation", "")`.
    - **The stage.** Each stage is one `if t_k: … elif …` run with a synthetic
      final `else: return _NEXT_STAGE`. The arm bodies move UNTOUCHED: a
      matched arm that falls off its end falls off the stage, which returns
      `None` exactly as the old function did. No `return None` is appended.
    - **The last stage** keeps the original `else` and gets no synthetic one.
    - **The proof** checks four things:
      - every arm body is AST-equal to the old one, with the shared names as
        `ctx.<name>`;
      - the tests appear in the old order;
      - each non-final stage's only addition is the synthetic `else`;
      - the original `else` is in the last stage.
    - **Shared names.** Only one arm runs per call, so no arm can read another
      arm's binding. The context therefore holds only the parameters plus
      `target_nation`, and the head's imports take the tool's existing
      repeat-per-stage road.
    - **Naming.** The prefix is `_choice_` and the context class
      `DialogueChoiceContext`. Runs are cut at the arms' family boundaries
      (settlement, proposal, ultimatum, modify, mission, alliance), each
      stage under 500 lines.

    The ratifier (slice 1) has 76 top-level statements and 61 local imports;
    its largest statement is the 292-line `if is_player_treaty:`. Its prefix is
    `_ratify_`, and its context class `RatifyTreatyContext`.
- **The tool:** `tools/stage_fn.py`, with `tools/pin_scan.py` and
  `tools/oneliner_sweep.py`. They were moved out of S10's scratchpad on
  October 13, 2026, and the moved tool rebuilds slice 3 byte-identical from
  its parent commit.
- **Completion:** neither function is over 500 lines, and
  `FUNCTIONS_OVER_500_CAP` goes 30 → 28. CODE-2's done-when (none of the
  eight named over 500) is then MET.
- **STATUS tracking:** the ▶ NEXT UP S10b line.
- **Behaviour tests:** a shape pin per function (`tests/test_code2c_*`,
  modelled on CODE-2b's), plus the census ratchet. The net is byte-for-byte:
  - DD-1's own instruments (the sign-ability sweep, the exit fuzzer, the
    answer-binding shuffle);
  - `score_run check`, `BASELINE_SERIES` + M1–M7;
  - the settlement suites.

**CODE-2c LANDING RECORD, SLICE 1 — `WorldState._ratify_treaty` (Pre-Deploy
S10b, October 13, 2026).** *The stage list, written before the cut (recipe step
1).* The method (`backend/models/world_state.py`, 1,024 lines, 61 local imports)
runs as 76 top-level statements under their own comment banners. The cut runs at
those statement boundaries. Each stage is a method `_ratify_<stage>(self, ctx)`
on `WorldState`, so `self` and the module globals the suite patches are read
exactly as before:

| # | Stage | Its header in the old body | What it holds |
|---|---|---|---|
| 1 | `_ratify_open` | "# Extract nations from proposal" | the two courts, the target state, the one verdict (`treaty.can_sign`, DD-1 S7 Slice B): a letter naming no court answers `None`, a refused one its refusal dict |
| 2 | `_ratify_snapshot_and_vassal` | "# Build treaty clauses before vassalage validation" | the clauses built; the war's data snapshotted before anything clears it (BPH-D, GE-1); a VASSAL treaty's vassal created first |
| 3 | `_ratify_transition_and_record` | "# Apply state transition (R2: centralized setter)" | the transition (R2), the armistice cooldown (R5b), open borders, the treaty stored and remembered |
| 4 | `_ratify_one_time_clauses` | "# Apply one-time clauses (shared)" | every one-time clause, the gold among them |
| 5 | `_ratify_alliances_and_carves` | "═══ WPS-C: Forced alliance + liberation clause handling ═══" | WPS-C's forced alliance and liberation, the client carved (NA-6c), the Tilsit clause, the war bargains' commitments (WB-A) |
| 6 | `_ratify_titles_and_elimination` | "AI-5b(i) (§3.6): a bilateral treaty that strips a court leaves" | the punitive record, the titles and the Humbled Peace (GE-1), a court eliminated by its cessions (R81) |
| 7 | `_ratify_war_end` | "# War-end cleanup (shared — for both player and AI-AI)." | the war's end cleaned up (WPS-A, WB-B), the clients follow (SR-1b), the forced alliance set (WPS-C §9.2), the corridor (WIN-D3), the volte-face (AI-5b(ii)) |
| 8 | `_ratify_player_events` | "═══ Player-specific events ═══" | France's own treaty: its events, notices and reply |
| 9 | `_ratify_ai_ai_events` | "═══ AI-AI-specific events ═══" | two other courts: relations, the dispatch, the log, the pair's cooldown (R43), the result |

*The outcome (✅ LANDED October 13, 2026).*
- **The context.** Of the old body's 194 locals (`self` aside), **21 ride
  `RatifyTreatyContext`**: `proposal`, then the two courts, the states, the
  clause lists, the war-end snapshots, the treaty and the breach events. Five
  more names are split, bound before read in every stage that uses them, on
  the tool's definite-assignment pass: `applied_clause`, `clause`, `ctype`,
  `event_id`, `result`. None is confined.
- **What else moved.** Four imports are repeated at a stage's head:
  - `treaty_clauses_of` at `_ratify_snapshot_and_vassal`'s;
  - `burden_on_nation` and `_UPGRADE_ORDER` at `_ratify_transition_and_record`'s;
  - `take_status_quo_titled as _take_sq` at `_ratify_player_events`'s.
  Each original line stays where it was.
- **The tool needed one more road.** `world_state.py`'s typing line
  (`from typing import Dict, List, Optional, Tuple, Any, Set`) was not one of
  the four the tool knew, so the dataclasses import now goes above ANY
  one-line `from typing import`, with `Any` added when it is absent. The known
  four keep their old path, so S10's three outputs cannot change.
- **Sizes.** Stages run 41–298 lines, and the driver is 52. **Functions over
  500 lines 30 → 29**, and `FUNCTIONS_OVER_500_CAP` is lowered to match.
- **The F2 class is empty.** None of the 61 local imports binds a
  module-level name of `world_state.py`.

**The net:**
- `score_run.py check` against `2026_10_05_sfr` gives stdout identical to the
  same check on `a0d1b9d1`.
- The 164 test files of the family: DD-1's six (`test_dd1_*`, the sweep, the
  fuzzer, the shuffle among them), the 42 settlement suites, every test
  naming `ratify` or `BASELINE_SERIES`, and the variance arm. Result: 6,362
  passed and 2 failed, the two below; both pass once re-pointed. No re-record.
- **Five pins were re-pointed, each with the same assertion where the code now
  lives.** Three were found before the run:
  - FA slice 10's ally-penalty census reads
    `burden_on_nation(ctx.treaty_clauses, penalty_target)`;
  - the Aug 30 review's corridor order reads the staged source in run order
    (`open_evacuation_corridor(self, ctx.proposer, ctx.target_nation)` still
    after the cessions);
  - the IQ1 chest census names `_ratify_one_time_clauses`. It keys on the
    function holding a `nation_gold` subtraction; it would have failed
    loudly, not vacuously.
- **Two more were found by the family run, not before it.** IGR-D's
  carve-route pin and IQ-3's treaty-elimination pin call
  `inspect.getsource(WorldState._ratify_treaty)` with the function on the
  NEXT line. The one-line grep missed them, and their literals survive
  unchanged in the stages, so the literal scan could not see them either.
  Both now read `tests/_staged_functions.staged_source`. The class to check
  next time: **any reference to the function object**, not only its name as
  a string.

**The shape is pinned** in `tests/test_code2c_the_ratifier_is_staged.py` (18):
- the nine stages in order, and the driver's body `[Assign, For, Return]`;
- the identity test, and the signature unchanged;
- no stage over 500 lines;
- no caller outside `world_state.py` names a stage, and only the driver's
  last call is made with parentheses;
- a letter naming no court answers `None` and writes nothing (driven);
- the context's slots and no-default contract;
- nothing on the wire from a real 1805 France–Prussia peace;
- no stage-local import shadowing a module name.

**CODE-2c LANDING RECORD, SLICE 2 — `DiplomaticExecutor._process_dialogue_choice`
(Pre-Deploy S10b, October 13, 2026).** *The stage list, written before the cut
(recipe step 1).* The method (`backend/commands/diplomatic_executor.py`, 2,210
lines, 73 local imports) is a head (three imports and `target_nation`) and then
ONE chain: `if action == "dismiss": … elif …`, 72 arms and an `else`. The
tool's new **elif mode** cuts it into runs of arms at their families' seams.
Each stage is a method `_choice_<family>(self, ctx)`: one `if … elif …` run
ending in a synthetic `else: return _NEXT_STAGE`. The last stage keeps the
chain's own `else`.

| # | Stage | Its first arm (or banner) | The arms |
|---|---|---|---|
| 1 | `_choice_desk_settlement_and_war` | `if action == "dismiss":` (the head too) | dismiss, ask later, reconsider; the settlement's table, offers and petitions; the ally's entry; a bargain repudiated; a war objective or purpose; a war forced, a treaty broken |
| 2 | `_choice_proposal` | `execute_proposal` / `send` | the proposal sent; `modify_harsh` |
| 3 | `_choice_ultimatum` | `execute_ultimatum` | the ultimatum and its wizard (gold, territory, manpower, start over) |
| 4 | `_choice_generous_and_suggestions` | `modify_generous` | softened, options expanded, a suggestion taken, the terms adjusted |
| 5 | `_choice_terms_wizard` | `territory_yes` | provinces offered or skipped, gold, actions |
| 6 | `_choice_missions_and_ai_letters` | `start_mission` | a mission started or recalled; an AI court's proposal or ultimatum answered; a letter expanded |
| 7 | `_choice_counsel` | "GAP-1: ELABORATE / REVIEW_COUNTER / ACCEPT_WITH_CONFLICT" | GAP-1, sabotage (R37), the drafting pushback (PL-23), the pre-proposal override (R42) |
| 8 | `_choice_counters_and_rebellion` | "R2: COUNTER-OFFER RESPONSE HANDLERS" | the counter-offer (R2), the vassal's rebellion (R74) |
| 9 | `_choice_alliance_paradox` | "R12: ALLIANCE PARADOX HANDLERS" | honour or break (R12), and the chain's `else`: an unknown action refused |

The plan said five to eight stages. The first cut had eight, but
`generous_and_terms` came to 538 lines, so it was cut again at
`territory_yes`, where the terms wizard begins.

*The outcome (✅ LANDED October 13, 2026).*
- **The context is exactly what the design predicted.** Of 223 locals, **5
  ride `DialogueChoiceContext`**: the four parameters and `target_nation`.
  41 names are confined, each bound only inside an arm; none is split.
- **The mode's own refusals found nothing.** No name crosses arms, and no
  stage reads an import that only another stage's arm binds. Five import
  statements are repeated at stage heads, all from the head's three.
- **Sizes.** Stages run 154–349 lines, and the driver is 57. **Functions over
  500 lines 29 → 28**, and `FUNCTIONS_OVER_500_CAP` is lowered to match.
- **F2.** The class lists `copy`. Two arms (`modify_harsh`, `modify_generous`)
  imported `copy` locally before the cut, and still do inside their own
  stages. The symtable proof shows no stage reads `copy` without binding it.
  The shape pin holds that set exactly, so a new shadow fails.
- **The tool.** `tools/stage_fn.py` gained `mode="elif"`. The proof checks
  three things per stage:
  - each run's chain, with its synthetic `else` taken off, is AST-equal to
    the old arms (shared names as `ctx.<name>`);
  - the tests appear in the old order;
  - the last stage ends in the old `else`.

  The `elif` → `if` swap on a run's first arm is the only text the mode
  writes inside the arms.

**The net:**
- `score_run.py check` against `2026_10_05_sfr` gives stdout identical to
  slice 1's.
- **A before/after sweep, `tools/dialogue_choice_sweep.py`.** Every action
  string the chain tests (112, with a no-such action) goes through the method
  with a bare and a filled `selected` / `dialogue`. Each call runs on a fresh
  1805 world with the RNG seeded, recording the reply (or the exception) and
  a digest of the world afterwards. All **224 calls are identical**,
  including the 10 that raise.
  - The sweep's first run was not deterministic: a notification's id is a
    fresh `uuid4`, so the digest blanks UUIDs. It was confirmed on two runs
    of the same tree before it was trusted.
- The 162 test files of the family: DD-1's six, the 42 settlement suites,
  every test naming the executor, a dialogue response or `BASELINE_SERIES`,
  and the variance arm. 6,376 passed, no re-record.
- **Seven pin sites in four files were re-pointed before the run, and the
  family found none more.** Six came from the literal scan. Every arm's test
  now reads `ctx.action`, so these anchor `elif ctx.action …`, the same
  lines:
  - the four dispatch-tuple extractors in `test_godot_parse_harness.py`;
  - the force-declare-war window (`test_ingame_review_fixes_2026_07_25.py`);
  - the harsh-terms window (`test_sr2a_one_verdict_per_screen.py`).

  The seventh came from reading every test that loads the module's text. FA
  slice 17's `record_override(world, …)` regex accepts `ctx.world`, the same
  world. This is the equality class slice 3 of CODE-2b met, found this time
  before the run.

**The shape is pinned** in
`tests/test_code2c_the_dialogue_choice_is_staged.py` (21):
- the nine stages in order, and the driver's body `[Assign, For, Return]`;
- the identity test, and the signature unchanged;
- no stage over 500 lines;
- every stage but the last ends in `return _NEXT_STAGE`, and only the last
  answers an unknown action;
- 72 arms in all, each testing `ctx.action`, no action string claimed twice;
- `dismiss` and an unknown action driven to their answers;
- the context's five fields, no defaults;
- nothing on the wire from a real `reconsider`;
- only the two old `copy` shadows.

**CODE-2c is DONE, and with it CODE-2** (S10b STRUCK, October 13, 2026).
**None of the eight functions CODE-2 named is over 500 lines**, and the census
reads 28. No rule moved, so `SYSTEMS_REFERENCE.md` gains no section.

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

**✅ LANDING RECORD, part 1 — October 12, 2026 (Pre-Deploy S7b, the
session's second commit, beside DD-C — `PRE_DEPLOY_PLAN.md` §3 "DD-C landing
record"; rules `SYSTEMS_REFERENCE.md` §110).**

- **`backend/errors.py`** (stdlib only, so any module imports it without a
  cycle): `report(exc, site, *, every=False)` — WARNING on the
  `sovereign.errors` logger once per site per process (each call with
  `every`), the stack formatted HERE into the record's string (no
  `exc_info`, so a captured record never keeps a world alive) and printed
  WITHOUT Python's "Traceback" header — the score instrument's
  `ai_aliveness.F2` reads that word in an arm's log as a crash and the
  in-process driver sends this logger's stderr into that log (the design
  review's catch); every call counts into a locked process tally,
  display-only and never serialized, that `/debug errors` lists most
  frequent first; `report` never raises (its own guard is the one handler
  that cannot report). `swallow(site, *, notify=None, every=False)` is a
  class-based context manager — the work is in `__exit__`, so it holds no
  bare handler; `notify` is a callable for a rail push. `debug_fields(exc,
  site, enabled)` gives `{"debug_error": {class, site}}` only when the
  CALLER's switch says debug (`main.DEBUG_MODE`; not the environment — the
  dev `.env` sets it and conftest does not pin it).
- **The census** (`tools/_code_health_census.py`): the class **reports** — a
  handler that calls `backend.errors.report`, resolved through the module's
  own imports (a function that merely shares the name does not count), with
  a site in words (a non-empty literal or an f-string); classified before
  the `logs` regex. A broad handler now includes a TUPLE holding `Exception`
  (`list_saves`' `except (json.JSONDecodeError, Exception)` swallowed and was
  invisible). New keys `silent_sites` and `report_calls`.
- **The ratchet** (`tests/test_code_health_ratchet.py`): the key set admits
  `reports`; a namesake arm and a site-in-words arm; `SILENT_HANDLERS_CAP`
  **367 → 345**.
- **The conversion tool, `tools/speak_handlers.py`** (AST; a dry run, then
  `--apply`): `except Exception:` → `as exc` (`_exc`, `_exc2`, … when the
  name appears anywhere in the OUTERMOST enclosing function — Python deletes
  an `as` target at the handler's end); `report(exc, "<module>.<function>:
  <hint>")` before the handler's first statement, a lone `pass` replaced; the
  import added, or an `_errors` alias in a module that binds `report` itself
  (`turn_manager`'s local `report = []`, `combat_executor`, `strategic`,
  `naval`, `main`); identifier-only hints (no quotes, no parentheses — a
  copied literal could meet a test's substring pin); every site unique. **The
  proof, per file:** the insertions taken back out must give the original's
  `ast.dump`, or the file is not written. Run on `main.py` this commit (its
  ten silent helpers; the routes by a script — DD-C's record). Rehearsed on a
  copy of `backend/`: 342 handlers in 67 files, every proof equal, `ruff`
  clean, all 149 modules import.
- **The reading:** silent **367 → 345** (`save_manager.py` 5 + the tuple → 0,
  `main.py` 15 → 0, `notifications.py` 3 → 0, the reporter's own guard +1);
  reports 0 → 39; logs 28 → 14 (`main.py`'s crash handlers report now).
- **Next (this session):** the conversion of the remaining 339 by file, the
  normal-play reading, the residue pin — part 2.

**✅ LANDING RECORD, part 2 — October 12, 2026 (Pre-Deploy S7b, the
session's third commit: the conversion).**

- **The conversion.** `tools/speak_handlers.py --apply` over every
  `backend/` module but the hand-written four (`save_manager.py`, `main.py`,
  `runtime_log.py`, `errors.py`): **339 handlers in 66 files**, every file
  PROVEN before it was written (the insertions taken back out give the
  original `ast.dump`); `ruff` clean; four modules on the `_errors` alias
  (`combat_executor`, `strategic`, `naval`, `turn_manager` — each binds
  `report` itself); one handler named `_exc` (`state_desk.answer_state_question`,
  where `exc` was already a name); one site per handler, unique across
  `backend/`, identifier-only. No handler was narrowed — the review's
  advice (a too-narrow handler is a crash the replay pins cannot see) and
  the readings below agree: nothing fires in ordinary play to narrow for.
- **The reading:** silent **345 → 6** (the plan's done-when: under 60) —
  exactly the residue, named file by file in the ratchet's new
  `TestEveryBroadExceptSpeaks`: `runtime_log.py` 5 (the console tee —
  logging writes to stderr, which IS the tee) and `errors.py` 1 (the
  reporter's own guard). Reports **39 → 378**; every report names its site
  (a literal, an f-string or a `SaveError`'s `.site`) and no two handlers
  share one (both pinned). `SILENT_HANDLERS_CAP` **345 → 6**. 0 silent in
  `save_manager.py`, `world_state.py`, `main.py`, `llm_client.py` and
  `notifications.py` (DD-C's file pins).
- **The normal-play reading** (the plan's triage step): five driver
  campaigns played in-process with the tally dumped after each — the
  default policy (its passive France falls at turn 34), `commanded_full40`,
  `sf_end1_the_peace_holds`, `naval_descent`, and `commanded_full40` with
  `--diplomacy accept` — **0 report sites fired** (a sensitivity arm with
  `--save-faults` read the save path's four sites, so the zero is a
  reading). The suite with a shadow-tally plugin: 36 sites — 17 the save
  path's and the reporter's own deliberate faults, 19 others, every one a
  planted failure ("test crash", "boom", a deliberate mutation) or a stub
  world lacking a method (`_Memo`, `object()`); the hottest,
  `dispatch._front_page_order` (2,039 calls), is one test's stub. Nothing
  filed, nothing narrowed: the silent class was not hiding a live failure on
  any road these campaigns walk — which is what the next one would have been.
- **Found by the suite run, not by the slice:** CRT-9's agreement pin
  (`test_the_probe_refuses_exactly_what_the_executor_refuses[no_admin-attack]`)
  flaked with the worker's dice — its case-blind `\bBROKEN\b` matched an
  attack's own report when the dice broke the ENEMY ("Mack's broken army
  flees"); the pin now reads the refusal's own words (`\[BROKEN\]`, `army is
  broken`). None of the ~60 fixed-window source pins the review warned of
  went red (the full run's only other failure was the ratchet's cap gap).
- **Gate:** the full suite (30,620 + the new pins) green; `BASELINE_SERIES`
  + M1–M7 byte-identical with no re-record (the conversion adds no draw and
  no branch a replay takes); `ruff` clean; the full suite on the hook.
- **Done when** (§CODE-3): 0 silent handlers in `save_manager.py`,
  `world_state.py` serialization, `main.py` save/load routes and
  `llm_client.py` — **MET** (whole files); under 60 elsewhere, each with a
  `report` site string — **MET** (6, each the residue's); DD-C's injected
  faults all reach the player — **MET** (40 of 40). **CODE-3 is DONE.**

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

**Landing (ruled October 13, 2026 under the user's delegation):**
Pre-Deploy S17a–d, after the deploy, one file per session in the order
below. Done when `score_run check` is identical and the re-exports are
removed one session later with the tests re-pointed. The pin is a per-file
line cap in `tests/test_code_health_ratchet.py`.

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

**Landing (ruled October 13, 2026 under the user's delegation):**
Pre-Deploy S16, the first session after the deploy, because the first
post-deploy patches land in the client. Done when the gate below reads clean.
The pin is a `main.gd` line cap in `tests/test_code_health_ratchet.py`.

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

**The byte readings fold CRLF to LF (CODE-X1, October 15, 2026).**
`core.autocrlf=true` writes CRLF in any fresh Windows checkout or worktree, so
`st_size` made `CLAUDE.md` ~430 B heavier there than the same commit in the LF
main checkout (62,329 B CRLF against 61,904 B LF at `4645de5f`), and the cap
failed in a fresh worktree at HEAD. `_code_health_census.text_bytes` reads the
LF-normalised size of both capped docs (`doc_bytes`); the cap values and the
"cap near its reading" pin are unchanged, because the LF reading is the one
they were set at.
