# Slice 11 review round — R3 — the record against the code

Read-only adversarial review of master `63924903` (FA slice 11, "The
Briefing Tells the Truth"), September 5, 2026.

> **⚠ READ THIS FIRST.** Seventeen of this round's twenty-three agents died
> on a session usage limit mid-run — every refuter for R1 and R2, and two of
> R3's four. The workflow's `survives: false` and its "Findings both refuters
> killed" heading are therefore ARTEFACTS of that failure, **not verdicts**:
> those rows were never judged at all. Every finding below was subsequently
> verified BY HAND against the shipped board, and the dispositions are in the
> boxed SLICE 11 REVIEW ROUND block in `BUG_FIXES.md`. Six of the ten were
> real; two were record errors; the P2 that two lenses found independently
> would have been buried if the empty `killed` list had been read as a
> judgement.


Transcribed verbatim from the agent's structured return value.

## The lens's own summary

I read the full 2,291-line diff and re-derived every numeric and quoted claim against the running tree. Most of the record is true and reproducible: 49 tests collected and green; `len(CAMPAIGN_LOG_TYPES) == 160` is pinned in exactly NINE pre-existing test files (the tenth is this slice's own), so "the row said five; the reproduction counted nine" is right; `vassal_lost` is weight 84; five `.gd` files; parser eval prints 675/675 in mock mode; M1–M7 (11 tests) and the BASELINE_SERIES control arm pass unchanged; serialization enforcement passes and nothing new lands on a model. I reproduced the two headline measurements on the shipped 1805 board: with the lever down the soil ladder really does read T3 "3 turns now" / T4 the base template / T6 "3 turns now" AGAIN, and after the fix it runs 4/5/6; and of France's three boot satellites, Holland (4 provinces) and KingdomOfItaly (2) both take the graceful-independence exit while Switzerland (1) takes the war exit — so "both big satellites" holds. FA-53 is genuinely reverted: dispatch.py has four deletions in the whole slice, all accounted for, no orphan constant, template, accumulator or lever. The `vassal_lost` class really does read all four sources (I fired `vassal_defected`, `vassal_transferred`, `vassal_broke_free` and `nation_eliminated` and got the class each time, with a foreign lord correctly excluded), and the raw-tag concern is a non-issue because `add_output`/`dispatch_view` run the R7 humaniser. Three claims did not survive. One is a mechanical behaviour change the record does not disclose at all (P2); two are documentation assertions that are false against the code (P3, P4). Unverified rather than wrong: "31 mutations, 31 killed, 0 inert" (I may not run the sweep; I read all 31 specs and each names a killer whose assertion the mutation plainly breaks) and "reds five of its pins" for FA-53.

## Findings that reached a verdict (2)

### [P3 → CONFIRMED] FA-N21's status cell and the commit message assert the build logs a `garrison_assault` event row; nothing logs one, and the campaign-log half of FA-N21's own title is silently unfixed

**Seam:** `docs/BUG_FIXES.md` :: `FA-N21 status cell ("the build picked one") — and the same sentence in commit 63924903's body`

**Evidence**

The cell says: "FA-N21's test (1) asserts the assault 'adds 0 rows to world.event_log' while FA-23's fix shape logs a row — FA-23's shape wins, because the campaign log and the briefing both need the row." Against the tree: `inspect.getsource(CombatExecutor._resolve_garrison_combat)` contains ZERO occurrences of `log_event` (308 lines, unchanged by this slice — combat_executor.py is not in the diff at all); `grep -rn garrison_assault backend/` returns exactly two live sites, the producer literal and the new fog carve-out in main.py; and `'garrison_assault' in CAMPAIGN_LOG_TYPES` is False (so is `garrison_destroyed`). What actually shipped is FA-23's *narrowed* fix — a carve-out in `_filter_enemy_phase_by_visibility` — plus the client arms. Consequences: (i) the two rows' tests were never mutually exclusive in the shipped build, since FA-N21's "0 new event_log rows" constraint still holds; (ii) the stated benefit — "the log and the briefing both need the row" — was not delivered, so a garrison assault still reaches neither the campaign log nor the morning briefing; (iii) FA-N21's title names three gaps ("no consumer in any .gd, no campaign-log row and no battle_report") and only the first is closed, with no narrowing note, while the cell simultaneously asserts the log row exists.

**Failure scenario**

A future session opens FA-N21/FA-23 to build the campaign-log surface for garrison combat, reads that the row is already logged and that only the client arm was in question, and either skips the work or writes a consumer for an event type that is never in `world.event_log`. FA-23's own cell is honest about the narrowing; FA-N21's contradicts it.

**Suggested fix**

Rewrite FA-N21's status cell to say what shipped: the fog carve-out plus the two structured client arms; `_resolve_garrison_combat` still logs nothing, `garrison_assault` is not a CAMPAIGN_LOG_TYPE, and the campaign-log / battle_report halves of the row are NOT closed — either re-open them or state the narrowing. Correct the same sentence in the commit-message record if the record is amended anywhere.

**Refuter 1 — CONFIRMED (severity P3)**

CONFIRMED with a narrowing of scope. The claim is false as written and appears in exactly two places: the FA-N21 status cell in docs/BUG_FIXES.md (the sentence "FA-N21's test (1) asserts the assault 'adds 0 rows to world.event_log' while FA-23's fix shape logs a row - FA-23's shape wins, because the campaign log and the briefing both need the row") and the identical claim in commit 63924903's body ("the build picked FA-23's, because the log and the briefing both need the row"). Nothing in the build logs a garrison event: CombatExecutor._resolve_garrison_combat contains zero occurrences of log_event and zero of record_battle across its 308 lines and is not touched by the diff at all; 'garrison_assault' and 'garrison_destroyed' are both absent from CAMPAIGN_LOG_TYPES (len still 160); grep over backend/ finds exactly three live sites - the two producer literals and the new fog carve-out in main._filter_enemy_phase_by_visibility. What shipped is FA-23's NARROWED consumer-side fix (the carve-out plus the client arms), not the producer log_event its Fix field prescribed. Consequences: FA-N21's "0 new event_log rows" constraint still holds exactly, so the two rows' tests were never mutually exclusive in the shipped build; and since both filter_campaign_log and dispatch.py source from world.event_log, a garrison assault still reaches neither the campaign log nor the morning briefing, so the stated benefit was not delivered. FA-N21's title names three gaps (no .gd consumer, no campaign-log row, no battle_report) and only the first is closed - the probe confirms the result dict has keys ['events','message','success'] with no battle_report - yet the cell carries no narrowing note.

CORRECTION TO THE FINDING, in the build's favour: the blast radius is smaller than the finding implies. Three other records of the same work are honest and describe the shipped carve-out correctly - FA-23's own status cell (which carries an explicit "Narrowed on the record" note and never claims a log row), the boxed SLICE 11 landing record in BUG_FIXES.md Final Whole-Game Audit (which CLAUDE.md designates authoritative, and which says only "suppressed by a fog gate keyed on the ASSAULTER's province"), and the new test file's module docstring. The defect is a contradiction between the FA-N21 cell and every other record, not a build-wide misdescription. P3 is the correct severity: no shipped behaviour is wrong, but the row a future session opens asserts a surface that does not exist.

<details><summary>What the refuter ran or read</summary>

Two read-only probes run from the repo root at 63924903 (files written under scratchpad/agent_probes_s11/, INK_IRON_SAVE_DIR pointed at the scratchpad, SOVEREIGN_SCENARIO popped).

Probe 1 - static: inspect.getsource(CombatExecutor._resolve_garrison_combat) then count substrings, plus membership in backend.campaign_log.CAMPAIGN_LOG_TYPES. Output:
  A) _resolve_garrison_combat lines: 308
  A) 'log_event' occurrences in it: 0
  A) 'record_battle' occurrences: 0
  B) 'garrison_assault' in CAMPAIGN_LOG_TYPES: False
  B) 'garrison_destroyed' in CAMPAIGN_LOG_TYPES: False
  B) len(CAMPAIGN_LOG_TYPES): 160

Probe 2 - live resolver, borrowing the fixture idiom from tests/test_ca8_gate_closeout_2026_08_07.py::TestGarrisonParityRuling._assault (legacy WorldState, Berlin flipped to Britain, garrison_detachment False, Ney relocated to Berlin), calling executor._combat._resolve_garrison_combat and measuring len(world.event_log) before/after. Output:
  HOLD path (Ney 12k vs garrison 60k): event_log delta = 0; event types = ['garrison_assault']; 'battle_report' in result = False; keys = ['events','message','success']
  FALL path (Ney 30k vs garrison 6k): event_log delta = 0; event types = ['conquest']

Supporting reads: `grep -rn "garrison_assault\|garrison_destroyed" backend/ --include=*.py` returns 5 lines across 2 files - combat_executor.py:3067/3087/3164 (producer) and main.py:2190-2191 (the new carve-out); `git show --stat 63924903` shows combat_executor.py is not in the diff; `grep -n "event_log" backend/game_logic/dispatch.py` returns five reads, and backend/campaign_log.py:567 defines filter_campaign_log(event_log, world_state) - so both consumers named in the false sentence source from event_log; `git log -1 --format=%B 63924903 | sed -n '55,75p'` shows the claim verbatim in the commit body; `sed -n '498,512p' docs/BUG_FIXES.md` shows the boxed landing record does NOT repeat it.

No mutating git command was run; no repo file was modified; the full suite and mutation_sweep were not run.

</details>

### [P4 → NARROWED] SYSTEMS_REFERENCE §33 says `record_vassal_break` is also called by the VS-6 free-defection arm's caller; it has exactly three call sites, all inside `check_vassal_rebellion`

**Seam:** `docs/SYSTEMS_REFERENCE.md` :: `§33, "A satellite breaking free briefs itself, at the exit it took"`

**Evidence**

§33: "`vassal.record_vassal_break(world, vassal=, lord=, exit_path=)` is called at all THREE exits of `check_vassal_rebellion` — war, armistice, graceful independence — and by the VS-6 free-defection arm's caller." `grep -rn record_vassal_break backend/ --include=*.py` returns the definition plus three call sites, all in `check_vassal_rebellion` (vassal.py ~969, ~1067, ~1115). The VS-6 arm (`_defect_vassal_free_and_hostile`) only removes the false line behind the lever, and its caller `attempt_vassal_bribe` briefs the outcome its own way (`queue_dispatch_event('diplomatic_vassal_defected', ...)` + `log_event({'type': 'vassal_defected', ...})`) — which I confirmed works, so FA-N19 is not a regression. But no defection ever produces a `vassal_broke_free` row or a `record_vassal_break` dispatch line.

**Failure scenario**

A maintainer adding a fourth way a satellite is lost follows §33, wires it through `record_vassal_break`, and expects the defection path to already be covered — or, reading it the other way, assumes a defection writes `vassal_broke_free` and drops the separate `vassal_defected` source from a consumer. Both readings are wrong.

**Suggested fix**

Change the sentence to state that the VS-6 defection path is briefed by `attempt_vassal_bribe`'s own `diplomatic_vassal_defected` dispatch line and `vassal_defected` log row, and that `record_vassal_break` is confined to `check_vassal_rebellion`'s three exits.

**Refuter 1 — NARROWED (severity P4)**

The reviewer's core fact is real and I reproduced it: `record_vassal_break` has exactly three call sites, all inside `check_vassal_rebellion`, and neither VS-6 outcome ever reaches it. The clause in `docs/SYSTEMS_REFERENCE.md` §33 — "…and by the VS-6 free-defection arm's caller" — is false as written.

But the finding is SMALLER than filed in three ways, and one of its two failure readings is refuted by §33 itself:

1. **The second failure reading does not hold.** The reviewer worries a reader "assumes a defection writes `vassal_broke_free` and drops the separate `vassal_defected` source from a consumer." §33 contradicts that two paragraphs below the bad clause: "It reads four sources: `vassal_broke_free`, `vassal_defected`, `vassal_transferred`, and `nation_eliminated`…". I checked this against production — `dispatch._build_headline`'s `vassal_lost` arm tests `etype in ("vassal_broke_free", "vassal_defected", "vassal_transferred")` and branches separately on `vassal_defected`. So the doc correctly and explicitly documents the defection as its own source, and a reader following §33 would not drop it. Only the reviewer's FIRST reading (a maintainer wiring a fourth loss path through `record_vassal_break` and assuming defection is already covered) survives.

2. **The authoritative record is correct.** §33's own opening line names `docs/BUG_FIXES.md` §Final Whole-Game Audit as the landing record. That block says "One helper at all three exits", and the FA-2 disposition says "One helper `vassal.record_vassal_break` at all three exits" — no VS-6 clause anywhere. The FA-N19 disposition correctly describes the VS-6 arm as "Retired behind FA-2's **lever**". So this is one stale clause in one sentence of a secondary reference, not a contradiction across the record.

3. **The true statement, and almost certainly the intended one.** What `_defect_vassal_free_and_hostile` shares with `record_vassal_break` is the LEVER, not the helper: both read `THE_BREAK_IS_BRIEFED_TRUTHFULLY`, the arm using it to gate its own retired `diplomatic_carved_vassal_dissolved` line (its in-code comment says so: "Behind FA-2's lever, so False reproduces the pre-slice briefing on this arm too"). The clause should read "…and the same lever gates the VS-6 free-defection arm's own false line", not "…and by the VS-6 free-defection arm's caller."

Zero behavioural consequence; no code defect; nothing player-visible. **P4 is the correct severity** (the reviewer filed it correctly) — a one-clause doc edit, ideally taken as a drive-by whenever §33 is next touched.

<details><summary>What the refuter ran or read</summary>

READING (repo at 63924903, working tree clean):
* `grep -rn record_vassal_break backend/ docs/ tests/` → definition at `vassal.py` `record_vassal_break`, plus three call sites, ALL inside `check_vassal_rebellion` (armistice exit, war exit, graceful-independence exit). No other module references the symbol, so no dynamic/indirect call site exists.
* Read `_defect_vassal_free_and_hostile` and `attempt_vassal_bribe`: the arm only gates its retired `diplomatic_carved_vassal_dissolved` line behind `THE_BREAK_IS_BRIEFED_TRUTHFULLY`; the caller briefs via `queue_dispatch_event("diplomatic_vassal_defected", …)` + `log_event({"type": "vassal_defected", …})`.
* Read `dispatch.py` `_build_headline` `vassal_lost` arm: it enumerates `("vassal_broke_free", "vassal_defected", "vassal_transferred")` as three distinct types with a separate `elif etype == "vassal_defected"` branch — i.e. the defection path IS covered by the headline, via its own source, exactly as §33's later paragraph says.
* Read the `docs/BUG_FIXES.md` SLICE 11 block and the FA-2 / FA-N19 dispositions — they say "at all three exits" with no VS-6 clause.

PROBE (scratchpad/agent_probes_s11/probe_defect.py and probe_defect_free.py, run with `.venv/Scripts/python.exe` from the repo root; `SOVEREIGN_SCENARIO` popped, `INK_IRON_SAVE_DIR` redirected to the scratchpad, no parser touched so no API billing). Built the shipped 1805 world via `WorldState.from_scenario`, monkeypatched `vassal.record_vassal_break` with a counting spy, then drove `attempt_vassal_bribe(world, "Britain")` against a France-lorded satellite at loyalty 5, seeded RNG:
  - Britain gold 50000 → TRANSFER outcome. `record_vassal_break calls during bribe: []`; new log rows `['vassal_transferred', 'vassal_defected']`; `any vassal_broke_free: False`.
  - Britain gold 450 (below `BRIBE_TRANSFER_COST=600`, above `BRIBE_FREE_COST=300`) → forces the FREE-HOSTILE arm the doc names. Event `('vassal_defected', 'free_hostile', "THE DEFECTION: Britain's gold buys Holland's 'independence' …")`; `record_vassal_break calls during bribe: []`; new log rows contain no `vassal_broke_free`.
  - Contrast, same probe: forcing `check_vassal_rebellion` on a loyalty-0 satellite gives `record_vassal_break calls: [('KingdomOfItaly', 'France', 'vassal_rebellion_independent')]` and one `vassal_broke_free` row.

So both VS-6 outcomes run their caller end to end with ZERO `record_vassal_break` calls. The doc clause is false; everything else the reviewer's second failure reading depends on is contradicted by §33's own next paragraph and by production.

</details>

**Refuter 2 — NARROWED (severity P4)**

The factual core holds and this commit owns it: SYSTEMS_REFERENCE §33's clause "and by the VS-6 free-defection arm's caller" is FALSE. `record_vassal_break` has exactly three call sites (vassal.py 969 / 1067 / 1115), all inside `check_vassal_rebellion` (914-1129); a repo-wide census excluding docs/ finds no fourth, and the commit message itself says "at all three exits". Not pre-existing — `git show 3ee0be90:docs/SYSTEMS_REFERENCE.md` contains zero occurrences of `record_vassal_break`, so §33 is entirely new here. Not guarded and not unreachable — `attempt_vassal_bribe` is live from turn_manager.py:565, and `vassal_broke_free` is written at exactly one site (vassal.py:906, inside the helper), so a defection genuinely never produces that row.

NARROWED on two counts the finder did not weigh. (1) Half the stated failure scenario is already closed by §33 itself: three paragraphs below the false clause, the `vassal_lost` paragraph enumerates "four sources: `vassal_broke_free`, `vassal_defected`, `vassal_transferred`, and `nation_eliminated`", naming the two as DISTINCT — backed by code at dispatch.py:645. A reader of the section cannot come away believing a defection writes `vassal_broke_free`, nor drop `vassal_defected` from a consumer; the in-code FA-N19 comment says the same ("`attempt_vassal_bribe` briefs every landed outcome already"). (2) The clause is a compression rather than an invention: `_defect_vassal_free_and_hostile` DOES share the lever `THE_BREAK_IS_BRIEFED_TRUTHFULLY`, which gates its false "ceased to exist" line — that is what the VS-6 arm actually inherits from this rule. The accurate sentence is "...and the VS-6 free-defection arm's false line is removed behind the same lever."

Residue is one prose clause in a systems-reference section: no code, no test, no serialized field, no player-facing behaviour, and one grep contradicts it. P4 is the right severity; the surviving harm is only the first of the finder's two readings.

<details><summary>What the refuter ran or read</summary>

Read-only, at the checked-out SHA 63924903, from the repo root.

1. Doc claim, verbatim (docs/SYSTEMS_REFERENCE.md §33, "A satellite breaking free briefs itself, at the exit it took"):
   sed -n '4120,4132p' docs/SYSTEMS_REFERENCE.md
   -> "`vassal.record_vassal_break(world, vassal=, lord=, exit_path=)` is called at all THREE exits of `check_vassal_rebellion` - war, armistice, graceful independence - and by the VS-6 free-defection arm's caller."

2. Census (repo-wide, docs and .pyc excluded):
   grep -rn "record_vassal_break" --include=* . | grep -v "^\./docs/" | grep -v "\.pyc"
   -> definition vassal.py:859; a comment at 947; call sites 969, 1067, 1115; two test calls; one mutation-sweep entry; and .git/COMMIT_EDITMSG "at all three exits". No site in `attempt_vassal_bribe`.

3. All three sites are inside the one function:
   grep -n "^def " backend/game_logic/vassal.py | awk -F: '$1>900 && $1<1200'
   -> 914 check_vassal_rebellion, 1130 check_defection_cascade. 969/1067/1115 all fall inside 914-1129.

4. Not pre-existing (this commit owns the sentence):
   git show 3ee0be90:docs/SYSTEMS_REFERENCE.md | grep -c "record_vassal_break"   -> 0
   git show 3ee0be90:docs/SYSTEMS_REFERENCE.md | grep -n "## 33\."               -> no output

5. Path is reachable, so the code fact is live, not academic:
   grep -rn "attempt_vassal_bribe" backend/ --include=*.py   -> turn_manager.py:561/565 imports and calls it.

6. What the VS-6 caller does instead (sed -n '2605,2620p' backend/game_logic/vassal.py):
   world.log_event({"type": "vassal_defected", ...}) plus queue_dispatch_event(world, "diplomatic_vassal_defected", ..., "always") plus a CRITICAL notification when lord == player. The arm itself (sed -n '2314,2340p') shares THE_BREAK_IS_BRIEFED_TRUTHFULLY - it only DROPS its false "ceased to exist" line behind that lever.

7. The narrowing evidence - the section self-corrects the consumer-side reading:
   sed -n '4145,4152p' docs/SYSTEMS_REFERENCE.md  -> "It reads four sources: `vassal_broke_free`, `vassal_defected`, `vassal_transferred`, and `nation_eliminated`..."
   grep -n "vassal_broke_free" backend/game_logic/dispatch.py -> :645 lists the three types separately in the vassal_lost class.
   grep -n "vassal_broke_free" backend/game_logic/vassal.py -> the type is written at exactly one site, :906, inside record_vassal_break.

No probe scripts were needed and none were written; no test suite was run; no mutating git command was issued.

</details>

## Findings whose refuters DIED (1) — unjudged, not killed

The workflow labels these "killed". They were not: both refuters
errored on the usage limit, so `survives` computed False over an
empty verdict list. Each was verified by hand instead; see the
landing record for the disposition.

### [P2] The armistice exit's new `continue` silently drops four mechanical tail effects; the record accounts for only the two copy effects

Refuter output: (none — both agents errored)
