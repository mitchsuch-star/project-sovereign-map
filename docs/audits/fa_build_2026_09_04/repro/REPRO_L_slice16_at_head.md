# REPRO L - slice 16, the copy sweep, re-reproduced at HEAD `3e43d89b`

Eight read-only agents, one per file group, run **after** the slice-15 review
round landed. This supersedes `REPRO_J6_copy_sweep_N.md` and
`REPRO_J7_copy_sweep_FA.md` wherever it disagrees with them - those were
written at `a1ed5c9d`, before fifteen slices and seven review rounds.

Nothing in the repo was modified. Every verdict below is backed by a probe
line or a source line the agent actually read, at today's line numbers,
navigated by symbol.

## Verdicts at a glance

| row | verdict |
|---|---|
| **FA-45** | REPRODUCED — and WIDER than its own arithmetic |
| **FA-51** | REPRODUCED verbatim, both halves |
| **FA-58** | REPRODUCED verbatim — and the reachability is WIDER than the row's own case, while the row's own boot repro is wrong |
| **FA-59** | REPRODUCED verbatim — and there is a FOURTH consumer the row does not name, which must NOT be fixed |
| **FA-64** | REPRODUCED-BUT-NARROWER — half of it was already closed by slice 14 part 2b (FA-31), which also made the filed fix shape actively harmful |
| **FA-N27** | REPRODUCED |
| **FA-N28** | REPRODUCED |
| **FA-N29** | REPRODUCED |
| **FA-N30** | REPRODUCED |
| **FA-N36** | WIDER-THAN-FILED |
| **FA-N58** | REPRODUCED |
| **FA-N65** | REPRODUCED-BUT-NARROWER |
| **FA-72** | WIDER-THAN-FILED |
| **FA-78** | REPRODUCED-BUT-NARROWER (on the count) and WIDER (on the seams) |
| **FA-79** | WIDER-THAN-FILED |
| **FA-75** | WIDER-THAN-FILED (and half the filed fix is unnecessary) |
| **FA-85** | REPRODUCED (and REPRO_J5's own recommended yard is wrong) |
| **FA-102** | REPRODUCED (contract hazard now larger than when filed) |
| **FA-90** | REPRODUCED-BUT-NARROWER (a roll-up, one third already owned elsewhere) |
| **FA-89** | REPRODUCED-BUT-NARROWER (slice 8 closed the sharper half; the row's 'one source' is not achievable) |
| **FA-56** | REPRODUCED |
| **FA-67** | REFUTED (headline) — a narrower row survives, and one surviving clause is NEW and unfiled |
| **FA-61** | REPRODUCED (verbatim, to the digit) — WIDER-THAN-FILED: two causes, and the row's own fix_shape ships a NEW shown!=applied |
| **FA-49** | REPRODUCED — WIDER-THAN-FILED on scope (two files, ~11 builders, one CONDITIONAL cost) |
| **FA-52** | REPRODUCED verbatim — J7's "substantially a duplicate of FA-49" CONFIRMED for the trust-tax half; three residues survive, one of them decisive and new |
| **FA-44** | REPRODUCED-BUT-NARROWER |
| **FA-65** | REPRODUCED-BUT-NARROWER |
| **FA-69** | WIDER-THAN-FILED |
| **FA-93** | REPRODUCED |
| **FA-95** | REPRODUCED |
| **FA-98** | REPRODUCED |
| **FA-100** | REPRODUCED |
| **FA-N47** | WIDER-THAN-FILED |
| **FA-N50** | REPRODUCED |
| **FA-N57** | REPRODUCED |
| **FA-N70** | REPRODUCED |
| **FA-N55** | REPRODUCED |
| **FA-N64** | REPRODUCED |
| **FA-N69** | REPRODUCED |
| **FA-N71** | REPRODUCED-BUT-NARROWER |
| **FA-N31** | ALREADY-FIXED |
| **FA-N32** | WIDER-THAN-FILED |
| **FA-N35** | REPRODUCED |
| **FA-N51** | REPRODUCED-BUT-NARROWER |
| **FA-N52** | REPRODUCED-BUT-NARROWER |
| **FA-N53** | REPRODUCED |
| **FA-N66** | REPRODUCED-BUT-NARROWER |
| **FA-N81** | REPRODUCED-BUT-NARROWER |
| **FA-N85** | REPRODUCED |
| **FA-N88** | REPRODUCED |
| **FA-70** | REPRODUCED |
| **FA-82** | REPRODUCED |
| **FA-94** | REPRODUCED-BUT-NARROWER |
| **FA-81** | REPRODUCED-BUT-NARROWER |
| **FA-101** | REPRODUCED-BUT-NARROWER |
| **FA-63** | REPRODUCED |
| **FA-9** | WIDER-THAN-FILED |


---

## Group: FA-45, FA-51, FA-58, FA-59, FA-64

### Recommended landing order

FA-58 → FA-59 → FA-45 → FA-51 → FA-64.

FA-58 first: one line, zero pins in either direction, and it is the only row with a series question — settle it and it is settled. FA-59 second: it is the largest blast radius (three text sites + two dispatch templates) and it establishes the shared-source discipline (`own_ships_lost`) that FA-45's `readiness_before` then mirrors. FA-45 and FA-51 are both `naval_executor.py` message/gate work and can land in one edit. FA-64 last and smallest — one clause, and it should be written only after somebody has read the FA-31 code that already sits at that seam.

### Cross-row findings

**BASELINE_SERIES: no attribution work is owed, and this is MEASURED, not asserted.** J7 flagged FA-58 as the AI-decision risk on the grounds that readiness is read by `derive_ai_postures` and the AI build rung. Both halves of that are wrong at HEAD: `derive_ai_postures` (naval.py:1713-1738) never reads readiness at all, and `find_ai_build_fleet` (naval.py:3141) reads `effective_strength` only in its *non*-blockaded branch — for a blockaded nation `want = is_blockaded(...)` short-circuits before any readiness read. The real exposure is indirect, through `effective_strength` → `blockader_against` / `crossing_check`.

So I measured it. I ran an instrumented replica of the exact `BASELINE_SERIES` recipe (`WorldState.from_scenario`, `TurnManager.end_turn` ×40, `random.seed(10_000 + turn)`, `PYTHONHASHSEED=0 SOVEREIGN_SEED=historical LLM_MODE=mock`, subprocess) in two arms — arm 0 unpatched, arm 1 with FA-58's one-line fix applied inside the tick:

- arm 0 reproduces `BASELINE_SERIES` byte-for-byte: `[70, 68, 66, 64, 62, 68, 66, 63, 60, 58, 45, …, 2, 0, …]`
- **arm 0 lifts recorded: 0. arm 0 sub-50 blockaded states: 0** (three blockaded nations × 40 turns).
- arm 1 series == arm 0 series: **True**. arm 1 province counts == arm 0: **True**.

The reason, and it is worth putting in the landing record rather than leaving as a bare byte-identity claim: the ambient board rots each blockaded fleet monotonically down to exactly 50 and parks it there (France 65,60,55,50,50…; Holland the same; Spain climbs back to 100 once its blockade lifts at turn 14). Nothing on the passive board ever pushes a blockaded fleet below the floor — the AI never runs the diversion and never lays a keel on a small blockaded navy. The fix is inert *on that instrument*, and it is inert for a stated reason, not by luck. It is emphatically **not** inert in play: I reached the lift by hand two ways (a post-turn-4 failed diversion, and Holland laying a single keel at 12 sail).

Also measured for the same question: the lift does not flip a crossing verdict at the reachable state (France Normandy→London reads `shut` at readiness 40 and at 50 alike, mover_effective 40.3 vs 44.8 against coverage 100.0 at floor 1.25) — but it does change the number printed in that refusal ("against our 40" vs "against our 45"), so it is a shown-value change downstream, not only an internal one.

**FA-51 has no AI path at all.** `find_ai_expedition` (naval.py:3024-3070) pre-filters candidates on `strength <= EXPEDITION_MAX_TROOPS` AND `location in yards`, so the AI never reaches either refusal. The reorder is player-path only.

**Three cross-row facts for whoever writes this slice:**

1. Every one of the five is backend-only. Zero `.gd`, zero serialized fields, zero new save keys. FA-59 adds keys to a transient result dict (`resolve_fleet_action`'s return), which rides `outcome["fleet_action"]` into a response and is never persisted.

2. **Four of the five rows carry stale line numbers, and three of them are stale by the same constant** — `naval_executor.py` has drifted **+83** (FA-51's :207/:221/:225 → :290/:304/:308) and **+58** at the diversion (FA-64), while `naval.py` has drifted +168/+180/+408/+419 at different points. Navigate by symbol; the +83 coincidence will tempt someone into arithmetic.

3. **The through-line is real and it is one sentence: the naval surface reports the smaller of two true causes, or the larger of two true figures, and in both directions it flatters the wrong actor.** FA-45 credits a fall to the keel when the blockade did 5/6 of it (and on turns 3-4, all of it). FA-59 credits France with losses two allies took. FA-58 credits the enemy's blockade with healing the fleet it beat. FA-51 and FA-64 both state the smaller of two refusals/warnings the game already knows. That argues for landing them as one slice with one rule written at the top of it — *a naval figure names whose it is, and a naval refusal states every gate it already knows it will hit* — rather than as five independent copy patches, which is the pattern the FA-59 refuter and the Sept-2 note both flag.

**One correction to the J7 report itself**, which the build will otherwise inherit: J7 said FA-64's remaining work is the whole chip note. It is not — slice 14 part 2b (commit `a18806bf`, FA-31) landed `window_forecast_clause` into BOTH the chip and the typed confirm on 2026-09-06, one day after J7 was written. The confirm and the chip now agree on the forecast sentence verbatim. Only the camp clause remains, and following FA-64's filed fix shape today would ship a duplicated forecast sentence. J7's other four naval findings all survive unchanged.


### FA-45 - REPRODUCED — and WIDER than its own arithmetic

**Mechanism.** `NavalExecutor._execute_build_fleet` (naval_executor.py:51) prints the POST-fold readiness at :90-93 with one causal clause — "(new crews come aboard green at 40; only sea-time makes a navy)" — and never names the blockade. `naval.lay_down_ship` (naval.py:2349) returns only `{ships, readiness}`, so the executor has no `readiness_before` to quote a delta from; the −5/turn rot is applied separately by `_readiness_tick` (naval.py:1741, blockaded arm :1753). Row line numbers are stale: :63→:90 (+27), naval.py:1941→:2349 (+408), :1573→:1741 (+168).

**Evidence.**

Four consecutive keels on the shipped 1805 boot, France `self_blockaded_by: Britain`:
  t1 before=70 → after_fold=69 (fold −1)  "…readiness 69 (new crews come aboard green at 40…)"  → rot tick → 64
  t2 before=64 → 63 (fold −1)            "…readiness 63 …"                                    → 58
  t3 before=58 → 58 (fold **0**)         "…readiness 58 …"                                    → 53
  t4 before=53 → 53 (fold **0**)         "…readiness 53 …"                                    → 50
The player-visible sequence 69/63/58/53 is exactly the archived digest. **The row understates itself**: it says the fall is "5/6 blockade rot" and the fold "~1 point". Measured, the fold is −1 on the first two keels and **0 on the third and fourth** — on turns 3 and 4 the message prints an UNCHANGED readiness and blames green crews for a fall the keel did not cause at all. The rot is 100% of it by turn 3.

**WARNING - what the row's own fix_shape would break.** TWO breakages. (a) `lay_down_ship` has a second return arm at naval.py:2355-2362 (the `ships <= 0` rebuild-from-nothing path) that returns a 2-key dict — and I measured `check_build_fleet` returns **None** on a 0-ship France, so that arm IS executor-reachable: adding `readiness_before` to the main return only makes `outcome['readiness_before']` KeyError on the first keel after a fleet is annihilated. (b) The fix says "adds the rot clause from the same single source the blockade order uses". The only such source is `naval.blockade_forecast_sentence` (naval.py:619), measured to return a THREE-clause paragraph — "Austria and Russia are closed — their ports watched and their trade halved. Britain is beyond our reach: 32 sail-effective against her, where 125 is needed. And we are blockaded ourselves…" — which would dump Continental-System trade copy into a shipbuilding receipt, and whose self-blockade clause never states the −5 number the fix's own quoted sentence promises. A new clause is required, not a reuse.

**Minimal fix.** One seam plus one signature. (1) `naval.lay_down_ship` adds `"readiness_before": readiness` to BOTH return dicts. (2) `_execute_build_fleet` quotes the real delta (`before − after`, which may be 0 — say "no cost to the crews this time") and, when `naval.blockade_forecast(world, actor).get('self_blockaded_by')` is truthy, appends a NEW short clause naming the blockader and `READINESS_TICK` ("…and Britain's blockade rots her 5 a turn at anchor — that is the number to fix"). Do not reuse `blockade_forecast_sentence`.

**Tests.** None. `grep 'only sea-time'/'come aboard green'/'A keel is laid' tests/` = **0 hits**. `test_naval_substrate.py::TestBuildFleet::test_build_costs_gold_and_folds_green_crews` (:237-249) asserts the fold ARITHMETIC (`int(round((ships0*r0+40)/(ships0+1)))`), never the sentence, and stays green. No pin asserts the defect.

**Flags.** none


### FA-51 - REPRODUCED verbatim, both halves

**Mechanism.** `NavalExecutor._execute_naval_expedition` (naval_executor.py:259) runs the embark-position gate at :290-296 (`if loc_controller == marshal.nation and location not in yards`) strictly before the lift gate at :308-317 (`if troops > naval.EXPEDITION_MAX_TROOPS` → `naval.over_lift_refusal`, naval.py:689), and `over_lift_refusal` reads only `marshal.strength`, never `location`. `troops = int(marshal.strength)` at :304 is unconditional and nothing in the parse chain extracts a troop figure. Row lines are stale by a constant **+83**: :207→:290, :225→:308, :221→:304; naval.py:567→:689.

**Evidence.**

Shipped boot, Soult at Lorraine with 30,000 (EXPEDITION_MAX_TROOPS 15,000), typed `land Soult in Munster with 12,000 men`:
  NOT at a yard → "An expedition assembles at a dockyard, Sire — Soult must stand at one of our yards: Bordelais, Brittany, Flanders, Provence."
  Soult moved to Brittany, same command → "The transports lift 15,000 men; Soult commands 30,000 — 15,000 too many. He cannot be lightened…"
The "12,000" never appears in either answer. The road offered leads to a wall.

**WARNING - what the row's own fix_shape would break.** TWO. (a) The fix says only "evaluate the lift before the embark position". Hoisting it blind puts the lift ABOVE the **inland-abroad** arm at :298-302 ("stands inland at X — the boats cannot reach him"), so a 30,000-man corps standing inland on foreign soil is told about the lift and never about the coast — the identical defect mirrored. The lift must go above the YARD arm only. (b) The echo must NOT go inside `over_lift_refusal`: `test_wo_slice6_the_admiralty_speaks_plainly.py:367` asserts `res["message"] == naval.over_lift_refusal(world, soult)` **byte-for-byte**, and the function has a second caller — `naval.expedition_blocked_reasons` at naval.py:2896, the region panel — which has no raw command text to read. Putting the echo in the shared refusal either reds that pin or requires threading a raw string into a pure predicate.

**Minimal fix.** Hoist the `troops > EXPEDITION_MAX_TROOPS` block from :308 to just ABOVE the yard gate at :290, leaving the inland-abroad arm (:298-302) where it is — final order: target resolve → lift → inland → yard. Add the detachment echo in the EXECUTOR (not in `over_lift_refusal`): when `re.search(r'with\s+([\d,]+)\s*(men|troops)', raw)` matches, append "— the transports take a whole corps; there is no verb to embark 12,000 of 30,000."

**Tests.** None, if the two hazards above are respected. `test_wo_slice6_the_admiralty_speaks_plainly.py:356-367` stages Soult AT a yard (so the reorder is invisible to it) and passes no `raw_command` (so the echo does not fire) — green. `:309-350`, `:555`, `:601-647` all call `over_lift_refusal` directly and are untouched. `test_naval_ui_clarity.py:184` shares the same source. `grep 'must stand at one of our yards' tests/` = 0 hits, so nothing pins the yard sentence for an over-lift corps. No pin asserts the defect.

**Flags.** none


### FA-58 - REPRODUCED verbatim — and the reachability is WIDER than the row's own case, while the row's own boot repro is wrong

**Mechanism.** `naval._readiness_tick`'s blockaded arm, naval.py:1753-1755: `readiness = max(READINESS_BLOCKADE_FLOOR, readiness - READINESS_TICK)` with FLOOR 50 (:81) and TICK 5 (:80). For any blockaded fleet already below 50 the `max` LIFTS it to 50. Row line :1573 → today **:1753** (+180).

**Evidence.**

Boot 1805, blockaded = ['France','Holland','Spain']:
  France readiness  40 → **50**  (effective_strength 18.00 → 22.50)
  France readiness  45 → **50**
  France readiness  49 → **50**
  France readiness  52 →   50  (correct)
  France readiness  70 →   65  (correct)
**A second, ordinary channel the row never names:** Holland (12 sail) blockaded at readiness 50 lays ONE keel → `lay_down_ship` folds to **49** → next tick lifts it back to **50**. No diversion needed; a small blockaded navy is healed by building. **The row's own repro is wrong on the shipped board:** France boots at readiness 70, so `diversion_failure_readiness` = 60 and the next tick correctly takes 60 → 55. The row's headline case becomes reachable only from turn 4, once the blockade has rotted France to 50 — then `diversion_failure_readiness(50)` = 40 and the tick refunds all ten points.

**WARNING - what the row's own fix_shape would break.** Nothing. I hand-checked every existing tick fixture against the new expression: from 70 the six-tick walk is 65,60,55,50,50,50 under both the old and new forms.

**Minimal fix.** The one line as filed: `readiness = max(min(readiness, READINESS_BLOCKADE_FLOOR), readiness - READINESS_TICK)`.

**Tests.** None, and **no pin asserts the defect**. `test_naval_substrate.py::TestReadinessTick` (:198-229) has four tick pins, all starting at ≥50 (70, 70, 50-unblockaded, 50-at-peace) — green under the fix. `test_naval_descent.py::TestAdvanceTurnWiring` asserts `r0 - READINESS_TICK` from 70 — green. `test_naval_reach_gate.py:290` sets Holland readiness to 40 but never calls the tick. The new behaviour is therefore entirely uncovered today.

**Flags.** none


### FA-59 - REPRODUCED verbatim — and there is a FOURTH consumer the row does not name, which must NOT be fixed

**Mechanism.** `naval._apply_side_losses` (naval.py:1337) returns a per-MEMBER dict; `resolve_fleet_action` (:1265, stores at :1295-1298) files that whole dict under one SIDE key. Three text consumers then `sum(...)` it under a single nation's name: `_log_fleet_action`'s `loser_ships_lost` at **naval.py:1386** (feeding the dispatch templates at dispatch.py:4164-4172), `resolve_diversion`'s `ships_lost` at **naval.py:1692** (message :1702), and the expedition-intercept sentence at **naval_executor.py:453**. Row lines stale: :1264→:1386, :1516→:1692, :370→:453, dispatch :3954/3959→:4164/4171. `grep own_ships_lost backend/` = 0 — no helper exists.

**Evidence.**

Forced diversion failure on the shipped boot:
  losses = {'France': {'France': 25, 'Spain': 17, 'Holland': 7}, 'Britain': {'Britain': 4, 'Russia': 1}}
  ships France 45 → 20 (own loss **25**)
  message: "…the fleet is brought to battle at bad readiness and **loses 49 sail**."
  dispatch beat: "TRAFALGAR: Nelson's line has shattered the **France** fleet — **49 sail lost** in a decisive action."
Both the figure and the R7 half of the row confirm live. `nation_adjective` exists and returns 'French'/'Dutch'/'Italian' (display_names.py:113).

**WARNING - what the row's own fix_shape would break.** TWO, one severe. (a) **The fourth consumer is deliberate and must be left alone.** `naval_diorama._side` (naval_diorama.py:65-101) computes `casualties_total` as the whole SIDE's sum BY DESIGN — measured 49, and its observation reads "49 sail lost against 5" — because the tableau disaggregates per squadron beside it (the NV-9 comment at :70-76 says so explicitly). Two pins assert that whole-side sum: `test_naval_diorama.py:140-143` and `test_naval_reach_gate.py:299`. A "make it the own figure everywhere" sweep reds both and reverses a landed design decision. (b) The fix shape's literal `own_lost = losses[loser].get(loser, 0)` is **insufficient for two of the three sites**: `resolve_diversion` reads `losses.get(nation)` where `nation` is the DIVERTING court, which is not necessarily the loser (the arm runs whoever wins), and `naval_executor.py:453` reads `losses.get(marshal.nation)`. A loser-keyed field alone leaves those two reading the wrong side. The helper must be nation-parameterised, exactly as the Sept-2 note says.

**Minimal fix.** ONE pure helper in naval.py — `own_ships_lost(action, nation) -> int` (find whichever side-dict contains `nation`, return that member's own entry) plus `allied_ships_lost(action, nation) -> Dict[str,int]` — called by all three text sites. Diversion message and both dispatch templates then read "France loses 25 sail; Spain 17 and Holland 7 beside her", with `nation_adjective(loser)` in the templates.

**Tests.** None on the text side. `grep 'loses .* sail'/'loser_ships_lost' tests/` finds nothing asserting the message or the beat. The two pins named above are the trap, not a flip — they stay green only if the diorama is untouched. No pin asserts the defect.

**Flags.** none


### FA-64 - REPRODUCED-BUT-NARROWER — half of it was already closed by slice 14 part 2b (FA-31), which also made the filed fix shape actively harmful

**Mechanism.** `naval.build_admiralty_report`'s chip note (naval.py:2712-2723) is now built in THREE parts: the 45% prefix (:2712), the camp clause `"; no army is staged to use the open water"` when `not camp_staged` (:2713-2714), and `window_forecast_clause` (:2719-2721). The typed confirm in `NavalExecutor._execute_naval_diversion` (naval_executor.py:576-632) gained the forecast half at :593 when FA-31 landed, so `window_forecast_clause` is ALREADY a shared source. The residual gap is exactly one clause: the confirm still never reads `camp_staged`. Row lines stale: naval.py:2293→:2712 (+419), naval_executor.py:518-527→:576-632 (+58).

**Evidence.**

Shipped boot, `camp_staged(France) = False`:
  CONFIRM: "The Grand Diversion is drawn up, Sire — once, and once only, this war. … 45 times in 100 the strait opens for 2 turns; otherwise she is caught coming home and fights at readiness 60. **And mark this, Sire: a success opens London-Normandy for both turns of the window.** Sail? (yes / no)"
  CHIP note: "45% — and once only, this war**; no army is staged to use the open water**; a success opens London-Normandy for both turns of the window"
The forecast sentence is now identical on both surfaces; only the camp clause is missing from the confirm.

**WARNING - what the row's own fix_shape would break.** The filed fix shape is now a REGRESSION. "Factor the chip's note builder into `naval.diversion_note(world, actor)` and have `_execute_naval_diversion` append it" would append the whole chip note — which since FA-31 already ends with the same forecast sentence the confirm now carries — producing a confirm that states the 45% figure twice and the forecast clause twice. Also note the chip's note reads `player` (build_admiralty_report is player-scoped) while the confirm reads `actor`; the confirm arm is gated on `actor == world.player_nation` so they agree today, but a shared helper taking `actor` must keep the AI path from ever building it (the AI confirms implicitly and never renders a note). Secondary: `test_wo_slice6_the_admiralty_speaks_plainly.py:436` is a SOURCE census reading the 900 characters BEFORE the literal "The Grand Diversion is drawn up" and asserting `'"marshal": "The Admiralty"'` sits inside them — safe if the clause is computed before the return dict (as FA-31 did), red if anything is inserted between the `"marshal"` key and the message literal.

**Minimal fix.** One predicate, one line. Add `camp_clause = "" if naval.camp_staged(world, actor) else " No army is staged to use the open water."` beside the existing `forecast_clause` at naval_executor.py:593, and interpolate it into the message before `forecast_line`. Do NOT build a composite `diversion_note`.

**Tests.** None. `test_naval_host_rule.py:461` (`"no army is staged" in diversion["note"]`) and `:477` (absent once the camp is staged) pin the CHIP both directions and stay green as long as the chip's string is preserved. `test_fa_slice14b_the_purse_and_the_window_2026_09_06.py:423` renders `window_forecast_clause` across states — untouched. No pin asserts the defect: nothing anywhere tests the confirm's text for the camp clause.

**Flags.** none


---

## Group: FA-N27, FA-N28, FA-N29, FA-N30, FA-N36, FA-N58, FA-N65

### Recommended landing order

N28 -> N29 -> N36 + N65, then N58, N30, N27 (the last three are independent and can land in any order or in parallel).

### Cross-row findings

ORDERING CLAIM (J6): VERIFIED, but for a narrower reason than J6 gives, and I found a stronger one.\n\nJ6's reason holds literally: at HEAD the dispatch's pending-decision read is `_pending = getattr(marshal, \"pending_interrupt\", None)` at dispatch.py:2785, still nested inside `if marshal.in_strategic_mode:` at :2776, so \"extract the dispatch's own predicate\" (FA-N36's fix_shape) before FA-N28 copies the nesting into ledger.py. BUT the dependency only binds if the builder follows that phrasing — FA-N36's own SUMMARY names \"ONE seam, ledger.py:86\", and a head arm written as `if getattr(marshal,'pending_interrupt',None): return \"awaiting_decision\"` carries no dependency at all.\n\nThe stronger reason, which J6 does not state: if FA-N36 lands FIRST, it creates a NEW cross-surface contradiction in the opposite direction. The ledger arm sits at the head of `_derive_status`, so an order-free `last_stand` marshal would read `awaiting_decision` on the ledger while the dispatch — still nesting its own read — reads `awaiting`, 'Awaiting orders.' for the same man on the same turn. N28 first removes that window entirely.\n\nTHE CLUSTER HAS DIVERGED SINCE a1ed5c9d, and \"one shared predicate\" is now the wrong ambition. Slice 11 (FA-32) gave `ledger._derive_status` a captivity head arm returning `\"captured\"`; the dispatch has no captivity arm at all and instead EXCLUDES prisoners from the roster at `_build_marshal_status`:2701. Those are deliberately different policies for two different surfaces. The only thing worth sharing is the narrow decision test, and it already lives in a module both files can import without either owning the other: `strategic.standalone_decision` (strategic.py:211), which returns None for order-bound types by construction — exactly the discrimination FA-N28 needs.\n\nSTALE LINE NUMBERS, measured on this family: FA-N27 :1181 -> :1378 (setter) / :1131 (producer); FA-N28 :2579 -> :2776; FA-N29 :3158 -> :3355; FA-N30 :4306 -> :4520; FA-N36 :86 -> :97; FA-N58 :2733 -> :2930, :2836 -> :3031, :2856 -> :3053; FA-N65 :76 -> :81. Seven of seven stale — navigate by symbol.\n\nTWO PINS ASSERT A DEFECT OR BLOCK A ROW'S OWN WORDING, and both must be flipped or worked around consciously:\n  - FA-N58: tests/test_creative_audit_ca9_2026_08_08.py:2081 `assert \"retreat_recovered\" not in _DISPATCH_EVENT_TYPES`.\n  - FA-N65: tests/test_fa_slice11_…:508 `assert rows[0][\"status\"] == \"captured\"` forbids the row's prescribed `'prisoner'`.\n\nTHE MOST DANGEROUS ROW IS FA-N27, and its danger is silent. `_select_headline`'s escalation block wraps `variants[step].format(**fmt)` in `except (KeyError, IndexError): continue`, so switching the variants to `{age}` without a matching field does not raise — it quietly stops escalating and re-renders the authored line forever. I measured it: distinct sub-beat lines over six turns 5 -> 1. One extra line at the same seam, `fmt.setdefault(\"age\", _run)`, keeps both CA9 pins green AND lets the producer's real age through; verified in-memory both ways.\n\nBLAST RADIUS: all seven rows are display-only. No row touches a `.gd` file under the recommended fixes (FA-N28's glyph arm and FA-N65's visible-ORDERS-row variant are the two optional exceptions, both avoidable). No row adds or moves a serialized field — FA-N27 READS `Marshal.expectation_grace_turn`, already serialized and confirmed present in `to_dict()`. No row can move an AI decision: `_derive_marshal_status` has exactly one caller and feeds only Berthier's note; `ledger._derive_status` has exactly one caller and one `.gd` reader; `_build_turn_events` and `_build_diplomatic_events_section` are pure renderers. So NO `BASELINE_SERIES` or M1-M7 attribution work is owed by this cluster.\n\nTWO DEFECTS FOUND IN PASSING, NEITHER FILED:\n  1. The `break` at dispatch.py:1133 caps `estate_eroding` at one candidate per turn. Measured: Davout eroded from turn 4 and the briefing did not mention him ONCE until turn 12, when Ney was settled. FA-N27 fixes the number on a man the page had hidden for eight turns; the row should say so or drop the `break`.\n  2. `settlement_offer_arrival`'s producer (turn_manager.py:667) composes a complete, correct sentence into the event's `message` key and the formatter never reads it. FA-N30's filed fix (return '' and drop) would DELETE that information rather than deliver it.\n\nHARNESS NOTES for the builder: `build_morning_dispatch(world)['marshals']` is the roster key, not `marshal_status`; `dispatch['headline']` is a dict `{class, weight, text, sub_beats}`, not a string; `_build_turn_events(events_list, player_nation)` takes the event LIST, not the world; `StrategicOrder` lives in `backend.models.marshal`, not a module of its own.


### FA-N27 - REPRODUCED

**Mechanism.** The producer `_add("estate_eroding", identity=…, marshal=m.name)` at dispatch.py:1131-1132 (followed by `break` at :1133 — at most ONE eroding candidate per turn) passes no age; the shared escalation block at dispatch.py:1378 sets `fmt["turns"] = _run`, the consecutive-turns-reported counter, and the three variants in `_STANDING_ESCALATION["estate_eroding"]` (dispatch.py:264) interpolate it into claims about the ARREARS. Offset is a constant −3 (`GRACE_TURNS`−1) in the one-marshal case and unbounded in the two-marshal case, because the `break` starves the second man's run until the first is settled.

**Evidence.**

Arm (a), one eroding marshal, `expectation_grace_turn = 0`:
  turn  6 age= 6 -> 'Sire — Marshal Ney has now gone unrewarded 3 turns. …'
  turn 17 age=17 -> "Sire — Marshal Ney's grievance is 14 turns old …"
Arm (b), Ney and Davout both eroding from t4, Ney settled with a rente at t12 (probe p4_estate_armb.py):
  t 4..t11 the page never mentions Davout at all (the `break`)
  t14 A_age=14 B_age=14 -> 'Sire — Marshal Davout has now gone unrewarded 3 turns. …'

**WARNING - what the row's own fix_shape would break.** SEVERE, and measured. The filed fix ("the three variants interpolate `{age}` instead of `{turns}`") is silently swallowed by the `except (KeyError, IndexError): continue` guard three lines below the setter: any candidate whose `fields` dict lacks `age` renders the AUTHORED line forever instead of escalating. Two existing pins build exactly that shape and both go RED — measured in-memory (p5_n27_fixshape.py): distinct sub-beat lines over 6 turns falls 5 -> 1, and the legacy-save pin's text becomes "…household goes unpaid." which it asserts must NOT appear. In production the same failure mode is a silent no-op, not a crash. Also incomplete: the `break` means the SECOND eroding marshal is invisible until the first is settled, so `{age}` fixes the number on a man who was never mentioned for eight turns.

**Minimal fix.** ONE seam plus one guard line, both in `_select_headline`'s standing block: (1) producer passes `age=max(0, world.current_turn - int(getattr(m, 'expectation_grace_turn', world.current_turn)))` at dispatch.py:1131; (2) beside `fmt["turns"] = _run` at :1378 add `fmt.setdefault("age", _run)`. Measured: with the setdefault, the two CA9 pins stay GREEN (distinct lines 5) and a supplied `age=17` renders "grievance is 17 turns old". Decide the `break` consciously (drop it, or state the one-candidate limit on the row).

**Tests.** With the setdefault: NONE. Without it, RED: tests/test_creative_audit_ca9_2026_08_08.py::TestN47EscalationCanActuallyFire::test_a_demoted_standing_crisis_no_longer_repeats_itself and ::test_a_pre_ca9_save_keeps_counting_rather_than_restarting (both green today; 105/105 in the pinned set pass at HEAD). No pin asserts the defect. grep for 'unrewarded' / 'without settlement' / 'grievance is' in tests/ returns only unrelated files.

**Flags.** none


### FA-N28 - REPRODUCED

**Mechanism.** `dispatch._derive_marshal_status` (dispatch.py:2750; the row's :2579 is stale by +197). The pending-decision read `_pending = getattr(marshal, "pending_interrupt", None)` sits at :2785, INSIDE `if marshal.in_strategic_mode:` at :2776, and `Marshal.in_strategic_mode` is `self.strategic_order is not None`. `strategic.STANDALONE_DECISION_TYPES = {"last_stand", "muster_confirm"}` (strategic.py:52) is by definition the set that never has an order, so both fall through to `return "awaiting", "Awaiting orders."` at :2837.

**Evidence.**

probe p1_dispatch_ledger.py, 1805 boot, Massena with `strategic_order = None`:
  A1 order-free last_stand  -> ('awaiting', 'Awaiting orders.')
  A1 published row: {'name': 'Massena', 'status': 'awaiting', 'status_note': 'Awaiting orders.'}
  A1b order-free muster_confirm -> ('awaiting', 'Awaiting orders.')
Control (order + contact_bad_odds): ('awaiting_decision', 'HALTED at Swabia — Mack bars the way. Awaiting your word.')

**WARNING - what the row's own fix_shape would break.** Nothing breaks, but the filed shape ("hoist the pending-decision block OUT of the branch") is coarser than needed and its renderer half is over-stated. (i) Prefer ADDING a `strategic.standalone_decision(marshal)` arm above :2776 rather than MOVING the existing block: `standalone_decision` (strategic.py:211) returns None for order-bound types by design, so the order-bound arm stays where the TUT-F4a/slice-3 invariants put it and an order-bound interrupt with no order cannot start reporting through a new path. (ii) The row's "read by no .gd" is a narrowing, not a fact: `awaiting_decision` is not a KEY in any .gd, but it falls through `match m_status:` to `_: icon = "-"` in both main.gd:3604+ and dispatch_view.gd:188-206, i.e. it renders the SAME glyph as "awaiting" — and the NOTE already renders correctly. The glyph half is cosmetic and optional.

**Minimal fix.** One arm at dispatch.py, immediately above :2776: `if strategic.standalone_decision(marshal): return ("awaiting_decision", f"HALTED at {marshal.location} — awaiting your word.")` (reuse the existing enemy/`where` copy). Backend only.

**Tests.** None. tests/test_creative_audit_2026_07_19.py::test_marshal_with_pending_interrupt_is_not_reported_as_marching hard-sets `in_strategic_mode = True` on a `_FakeMarshal`, so it stays green; its falsifiable control ::test_marshal_without_interrupt_still_reports_its_order also stays green. test_mc_q3_command_rally / test_pc3_pc9_composition / test_w6_literal_doctrine all exercise other arms and set no `pending_interrupt`. No pin asserts the defect. All verified green at HEAD.

**Flags.** none


### FA-N29 - REPRODUCED

**Mechanism.** `non_ready_statuses = {"broken", "retreating", "drilling", "idle_restless"}` at dispatch.py:3355 (row's :3158 stale by +197) and `all_ready = all(m["status"] not in non_ready_statuses …)` at :3356. `awaiting_decision`, produced at :2790/:2793, was never taught to the readiness list beside the status deriver — the same one-word omission CA8-8 had to fix once for `idle_restless`.

**Evidence.**

probe p1_dispatch_ledger.py section B, 1805 boot, Ney holding MOVE_TO Swabia + a `contact_bad_odds` interrupt:
  roster statuses: {'Massena':'awaiting', …, 'Ney':'awaiting_decision', …}
  berthier_note: 'Your armies stand ready, Sire. The initiative is ours.'

**WARNING - what the row's own fix_shape would break.** Nothing. The filed one-word set extension is correct and is precedented. One interaction worth stating on the row: FA-N28 WIDENS this fix's reach — after the hoist, order-free `last_stand`/`muster_confirm` marshals also carry `awaiting_decision`, so N29 alone silences the note only for the order-bound case. That is the right outcome, but it means N29's own acceptance test should not be written as "the only way to get awaiting_decision".

**Minimal fix.** Add `"awaiting_decision"` to the set at dispatch.py:3355. Do NOT add `"arrived"` — arrived is a legitimately ready state.

**Tests.** None. tests/test_creative_audit_ca8_2026_08_04.py:1115 (`assert "stand ready" not in note.lower()`) and tests/test_fa_slice14_the_rulings_and_the_singles_2026_09_05.py:306 (`assert dispatch.get("berthier_note") != "Your armies stand ready…"`) both pin the SAME direction and stay green. No pin asserts the defect.

**Flags.** none


### FA-N30 - REPRODUCED

**Mechanism.** `_format_dispatch_event_text` (dispatch.py:4465) ends `return f"Diplomatic event: {event_type}"` at :4520 (row's :4306 stale by +214). `turn_manager.py:660-669` appends a BARE dict for `settlement_offer_arrival` with a fully composed `message` but no `fog_rule`/`template_vars`; `_is_dispatch_event_visible` defaults `fog_rule = event.get("fog_rule", "always")` at :4413 and returns True, and `is_settlement_event_type('settlement_offer_arrival')` is False so it takes the template branch with `template_vars = {}`. `hegemony_relaxation_aside` (coalition.py:634) and `diplomatic_mission_blowback` (diplomacy.py:10151) go through `queue_dispatch_event` but have no template either.

**Evidence.**

Played board, TestClient + mock parser, 14 end-turns on the shipped 1805 boot (probe p6_played.py, SOVEREIGN_SEED='repro16'):
  RAW-KEY dispatch lines seen: [(4, 'Diplomatic event: settlement_offer_arrival')]
The row's "on screen at turn 4 of the shipped 1805 boot" is EXACT, and reproduces under a different seed.
Direct: `_format_dispatch_event_text(t, {})` -> 'Diplomatic event: <t>' for all three; section row = {'type':'settlement_offer_arrival','text':'Diplomatic event: settlement_offer_arrival','priority':'MEDIUM'}.

**WARNING - what the row's own fix_shape would break.** Real. The filed fix — "return '' and have `_build_diplomatic_events_section` drop rows whose text is empty" — would DELETE the only dispatch mention of an incoming settlement offer, because `turn_manager.py:667` already composed a perfectly good sentence into the event's own `message` key ('Austria has offered terms to settle …. Asking N gold.') and the formatter never reads it. The player goes from a bad line to no line. It also removes the only signal a future producer's author would ever get, which is why the row's own AST-census test must land in the same slice or the class goes quiet instead of getting fixed.

**Minimal fix.** ONE seam, dispatch.py:4520, three arms in order: (1) fall back to the event's own composed `message` when present — this alone fixes the measured turn-4 case with zero new copy; (2) otherwise return '' and drop the row in `_build_diplomatic_events_section` (dispatch.py:4553); (3) add the AST census over literal `queue_dispatch_event` types and literal `"type"` dicts appended to `pending_dispatch_events`. Real templates for the other two are optional polish. NB the formatter's signature takes `template_vars`, not the event — the message arm needs the event passed in (the settlement branch at :4574 already passes the whole event).

**Tests.** None. grep 'Diplomatic event:' in tests/ = 0 hits; no test asserts a `len(diplomatic_events)`. Producers are pinned only for emission (test_bugfix_session4.py:355 etc., test_hegemony_engine.py:670). No pin asserts the defect.

**Flags.** none


### FA-N36 - WIDER-THAN-FILED

**Mechanism.** `ledger._derive_status` (ledger.py:81) has a captivity head arm (slice 11) but still no `pending_interrupt` arm — `grep -c pending_interrupt backend/game_logic/ledger.py` = 0 — so :97 `if marshal.in_strategic_mode:` returns the raw order status. `_derive_strategic_order_summary` (:112) is equally blind. The row names those two seams; there is a THIRD: `_build_orders` (:741) puts the halted marshal in `active_orders` with `path_remaining: 1`, and `strategic_ledger.gd:908/917` composes "(1 regions left)" from `path_remaining` directly, NOT from `condition`.

**Evidence.**

probe p1_dispatch_ledger.py section C, same Ney the dispatch calls `awaiting_decision`:
  forces row: {'name':'Ney','location':'Rhineland','status':'moving_to','strategic_order':'March Swabia (1 turns left)','captured':False}
  orders row: {'marshal':'Ney','order_type':'March','condition':'1 region(s) left','path_remaining':1,'has_order':True}
  _derive_status(ney) = moving_to
Rendered: FORCES prints "Order: March Swabia (1 turns left)" (strategic_ledger.gd:299); ORDERS prints "MARCH Swabia (1 regions left) │ 1 region(s) left".

**WARNING - what the row's own fix_shape would break.** Two. (1) "Best done by extracting the dispatch's own predicate" is still WRONG at HEAD — I confirmed the dispatch's read of `pending_interrupt` is at dispatch.py:2785, inside `if marshal.in_strategic_mode:` at :2776, so an extraction copies the nesting into a second file. Since slice 11, the two chains have DIVERGED further, not converged: the ledger has a `captured` head arm the dispatch does not (the dispatch excludes prisoners at `_build_marshal_status`:2701 instead), so a shared `_derive_status` would now have to reconcile three vocabularies. The shared unit that IS safe already exists and belongs to neither file: `strategic.standalone_decision` / a raw `pending_interrupt` test in `strategic.py`. (2) A backend-only fix at the two named seams leaves the ORDERS tab still printing "(1 regions left)" — the client composes that clause itself.

**Minimal fix.** Backend only, ledger.py: (a) `if getattr(marshal, "pending_interrupt", None): return "awaiting_decision"` at the head of `_derive_status`, below the captivity arm — `strategic_ledger.gd:267` renders it as "Awaiting decision" with no client edit; (b) `_derive_strategic_order_summary` appends "— HALTED, awaiting your word" instead of a turns-left count; (c) in `_build_orders`, emit `path_remaining: 0` for a marshal holding an interrupt, which makes the client's own `if path_left > 0:` suppress the false progress clause with zero .gd change.

**Tests.** None. `_derive_status` has exactly one caller (ledger.py:157) and one .gd reader (strategic_ledger.gd:247). tests/test_ledger.py's six status pins (broken/retreating/drilling/holding/pursuing/idle) set no `pending_interrupt`; `grep pending_interrupt tests/test_ledger.py` = 0. `path_remaining` is asserted only at tests/test_systems_audit_session5.py:228 for an active PURSUE with no interrupt. No pin asserts the defect.

**Flags.** none


### FA-N58 - REPRODUCED

**Mechanism.** `world_state._process_tactical_states` emits `retreat_recovery` only under `if new_stage < 3:` (world_state.py:11955) and emits `retreat_recovered` at :11981 on completion. `retreat_recovery` is in `_DISPATCH_EVENT_TYPES` (dispatch.py:2925); `retreat_recovered` is NOT, while the broken sibling has BOTH `broken_recovery` (:2934) and `broken_recovered` (:2930). `_build_turn_events` drops it at the whitelist (:3005), and because the producer's guard caps the emitted stage at 2, the ladder at :3053 `severity = "good" if int(event.get("stage",0)) >= 3 else "info"` is provably unreachable in production.

**Evidence.**

probe p2_events.py, 1805 boot, Ney retreating:
  raw tactical events: [('retreat_recovered', None)]
  built turn events: []
  full recovery event sequence: [('retreat_recovery', 1), ('retreat_recovery', 2), ('retreat_recovered', None)]
  'retreat_recovered' in _DISPATCH_EVENT_TYPES: False | 'broken_recovered': True

**WARNING - what the row's own fix_shape would break.** The whitelist half is safe. The second half — "delete the now-provably-dead `>= 3` arm" — REDS a live pin if done by hardcoding `info`: tests/test_creative_audit_ca9_2026_08_08.py::TestN37RoutRecovery::test_a_still_broken_corps_is_not_good_news feeds synthetic stages (1,2,3) and asserts stage 3 -> "good". Either keep the unreachable `>= 3` arm (costs nothing) or re-bless that pin in the same commit. Also note `retreat_recovered` carries a `nation` key (required by the :3009 filter) and a ready `message` — no new copy needed.

**Minimal fix.** ONE line: add `"retreat_recovered"` beside `"broken_recovered"` in `_DISPATCH_EVENT_TYPES` (dispatch.py:2930) and in the `good`-severity tuple at :3031-3036. Leave the `>= 3` arm alone, or delete it and re-bless the pin consciously.

**Tests.** A PIN ASSERTS THE DEFECT: tests/test_creative_audit_ca9_2026_08_08.py::TestN37RoutRecovery::test_stage_three_must_stay_good line 2081 — `assert "retreat_recovered" not in _DISPATCH_EVENT_TYPES`. It goes RED and must be flipped consciously (its docstring's premise, "the final stage of THIS event is the only recovery news the player ever gets", is exactly what the fix retires). ::test_a_still_broken_corps_is_not_good_news reds only if the `>= 3` arm is deleted. Both green at HEAD.

**Flags.** none


### FA-N65 - REPRODUCED-BUT-NARROWER

**Mechanism.** The FORCES half is ALREADY FIXED by slice 11 (FA-32, commit 63924903): `ledger._derive_status` gained a captivity head arm at ledger.py:83 returning `"captured"`, `_build_forces` publishes `captured`/`captured_by` (:167-169), and `strategic_ledger.gd:272-274` renders "Held by Austria at Vienna". The ORDERS half is untouched: `_build_orders` (ledger.py:741) still filters on nation only and appends the prisoner to `idle_marshals` with `order_type: "No active orders"`, `condition: "idle"` (:769-781), and `strategic_ledger.gd:945` hard-codes the literal `" │ No active orders"` without ever reading `order_type`.

**Evidence.**

probe p1_dispatch_ledger.py section D, Ney captured by Austria on the 1805 boot:
  FORCES row: {'status':'captured','location':'Vienna','strength':0,'captured':True,'captured_by':'Austria'}   <- FIXED
  ORDERS row: {'marshal':'Ney','location':'Vienna','order_type':'No active orders','condition':'idle','has_order':False}   <- STILL OPEN
So one screen says "Held by Austria at Vienna" on the FORCES tab and "Ney at Vienna │ No active orders" on the ORDERS tab. Slice 11's own test docstring names 'No active orders' as a symptom and never asserts against it (tests/test_fa_slice11_…:501).

**WARNING - what the row's own fix_shape would break.** Two, both now decisive. (1) The row prescribes `return 'prisoner'` from `_derive_status` — that seam is OCCUPIED and the word is `'captured'`; following the row literally REDS tests/test_fa_slice11_the_briefing_tells_the_truth_2026_09_05.py:508 `assert rows[0]["status"] == "captured"` (and :518's lever-down control). Do not rename. (2) The row's "which strategic_ledger.gd:267 already renders … with zero .gd change" is TRUE for FORCES and FALSE for ORDERS: the ORDERS row's string is a client literal at :945, so setting `order_type: 'Prisoner of Austria'` in the payload changes nothing on screen.

**Minimal fix.** Backend only, one edit: in `_build_orders` (ledger.py:749) `continue` on `getattr(marshal, 'captured_by', '')` — the prisoner leaves the ORDERS tab entirely, which is correct (he is on the FORCES tab under 'Held by Austria' and in the dispatch's PRISONERS OF WAR block) and needs no .gd change. If the build prefers a visible row instead, it must touch strategic_ledger.gd:945.

**Tests.** None for the recommended fix (nothing asserts the prisoner is in `ledger['orders']`). A PIN BLOCKS THE ROW'S OWN WORD: tests/test_fa_slice11_…py:508 and :518 pin `status == "captured"`; `THE_LEDGER_KNOWS_ITS_PRISONERS` (ledger.py:79) is the slice-11 flip lever and is pinned in that file's lever census at :84. All green at HEAD.

**Flags.** none


---

## Group: FA-72, FA-78, FA-79, FA-75, FA-85, FA-102, FA-90, FA-89

### Recommended landing order

Determinism governs the order. `seed_module_rng` is called only at the turn boundary from `(seed, world_turn)` (driver:1832, :1863, nowhere else, and only when not `--http`). Adding GETs and digest LINES changes nothing; adding or changing any POST shifts every subsequent draw in that turn and makes the nine archived `audit-*` digests non-regenerable. So:

1. **FA-75 A-half** — print `morning["lapsed_offers"]` and `morning["pending_envoys"]`. Zero backend change, zero POSTs, and it is the cheapest way to make the biggest blind spot measurable (16 of 38 item-turns unreachable, Britain's settlement offer standing 10 turns).
2. **FA-79 A-third** — write the `/respond_to_redemption` and `/marshal_petition_response` reply messages into the digest. Also zero POSTs. Do this BEFORE FA-79's policy flip, because it is what makes the FA-N76 silent-refusal case visible at all.
3. — archive a fresh digest set here, so everything below is attributable —
4. **FA-72** — the paradox. Safety-first: it is the only row where the default policy takes an irreversible diplomatic action. Must land before FA-N35 un-skips the popup family.
5. **FA-78** — same function, same seam as FA-72; land them together or back to back so `_pick_dialogue_choice` is opened once.
6. **FA-79 B-half** — the `grant_autonomy` default + `--redemption` flag. `petition: rotate` opt-in only, never bundled.
7. **FA-75 B-half** — the `/mailbox/activate` loop. Last of the answering changes because it opens the settlement ladder and will move the most digest text.
8. **FA-85** — script edit (`Soult, march to Bordelais`) + the SCRIPT PRECONDITION guard.
9. **FA-102** — `--reload-every N` at the turn boundary, with the corrected contract.
10. **FA-89** — the display-only `tutorial_step` backend key (group C, GR6).
11. **FA-90** — only (i) the `peace_ratification_summary` digest line and (ii) the `--reward` arm, and only after FA-75; arm (2)'s fate-word half is NOT to be built and arm (3) is already shipped.

### Cross-row findings

**1. Three of the eight fix_shapes would ship a regression or a false close, and a fourth is dead weight.**
- FA-78's filter is a measured NO-OP on its own headline case (the `proposal_confirm` branch returns a LITERAL when `find()` misses), and its "take the first enabled option" alternative would press `cancel_proposal` — an artefact withdrawal, worse than an artefact refusal.
- FA-72's token-match fixes 1 of 4 diplomacy modes.
- FA-90 arm (2) tells the build to type last-stand words that slice 2 made unnecessary and slice 0's FA-N2 router makes hazardous.
- FA-75's backend tuple edit is unnecessary — and its premise ("no `/command` layer forwards `lapsed_offers`") is false; the key is on `/dispatch`, which the driver already fetches. Its cited line (main.py:554) is also stale; `_COMMAND_RESULT_SIMPLE_FIELDS` is at :719.

**2. Two corrections to REPRO_J5, which is otherwise accurate and should be read.**
- FA-78's count: J5 corrected the row's "twelve" to "three" by grepping only the Austria wording. Measured at HEAD, `grep -c "refused: Making peace with" audit-propose/digest.md` = **7** — exactly the row's own seven cited lines. `audit-latewar-t20:41` is a stale passthrough, not a disabled press. The truthful figure is **7**.
- FA-85's yard: J5 says "Brittany is the safe yard". Brittany is a `camp_provinces` entry (`['Flanders','Artois','Normandy','Brittany']`), and `naval.camp_strength` sums every friendly marshal standing in one, so parking Soult's 30,000 there perturbs the Descent staging the script exists to measure. **Bordelais** is the safe yard — Atlantic, controlled at boot, outside the camp set.

**3. FA-72 is NOT gated behind FA-N35.** J5's cross-row note 2 says un-skipping the paradox popup makes the war declaration live. Measured: `commitment_paradox_popup` in `DISPLAY_ONLY_KEYS` hides only the POPUP render; the answerable DIALOGUE reaches `response["diplomatic_dialogue"]` via main.py:1554 and is answered `honor_defender` today, under every diplomacy policy. The ordering constraint stands (FA-72 before FA-N35) but the urgency is higher than filed: it is live now, not latent behind another row.

**4. Nothing here can move `BASELINE_SERIES` or M1–M7.** Verified: `tests/test_combat_sweep_metrics.py` and `tests/test_ai_intent_assurance.py` contain zero references to `playtest_driver` or `playtest_scripts`. No re-record is owed. What DOES move is the nine archived `audit-*` digests, which become non-regenerable after step 4 — so the memo citing one must name the driver revision that produced it, and `meta.json` is the place (slice 15b already added `meta["scenario"]`; `test_the_meta_records_the_runs_world` pins it).

**5. No pin in the tree asserts any of these eight defects.** `tests/test_playtest_driver_instrument.py` (23 tests) pins `_option_id` preference order, `_enabled` on the capture/clarification arms, and the RNG derivation — never the dialogue needle sets, never `POLICY_DEFAULTS["redemption"]`, never the literal fallbacks. Every row is a green-field pin. That also means every one of these fixes can be shipped inert; write the pin to red under the row's own stated mutation before writing the fix.

**6. Zero `.gd` writes, zero serialized fields, across all eight.** FA-89 READS `tutorial_overlay.gd` for its census but the fix is a backend key plus a digest line. If a `.gd` census pin is written for FA-89, scope it to the CALL SITES, not the file — slice 14c's lesson (a `const` Dictionary is read-only at runtime and invisible to the parse harness) and slice 13's (three of 23 sweep mutations came back inert because the pin matched a COMMENT) both bite here.

**7. Found in passing, not filed and not mine.** `POST /respond_to_diplomatic_dialogue` with `choice: honor_defender` returns `success: True` while the message body contains a FAILURE — `"France honors its alliance with Austria and declares war on Prussia! Cannot declare war: war_instance_side_conflict (both nations live in war_instance…"`. The driver's `if reply.get("success") is False` refusal note (driver:1461) therefore never fires, and the digest would record a signed war declaration that did not happen. That is the FA-N4 / shown-vs-applied family one layer out, on the paradox route. Worth a row.

**8. Environment note for the builder.** The `.env` sets `LLM_MODE=anthropic`, but `backend.main`'s module-level parser is built from the env at import, so setting `os.environ["LLM_MODE"] = "mock"` BEFORE `import backend.main` is sufficient — there is no `CommandParser` symbol in `backend.ai.llm_client` to swap, and a probe that tries to import one dies before printing anything. Also: a bare end-turn loop on the shipped board wedges at turn 4 on the Swabia capture question ("You must decide how to handle the captured region first!"), so any hand probe must answer `/capture_choice` or it will silently measure the same turn seven times.


### FA-72 - WIDER-THAN-FILED

**Mechanism.** `Answerer._pick_dialogue_choice` (tools/playtest_driver.py:1542) has no arm for `commitment_paradox`, so it falls to the generic mode block at :1626-1638. Under `decline` (the DEFAULT) the needle `"no"` substring-matches ho-NO-r_defender at :1595-1600 `find()`; under `accept`/`propose` the accept needles miss and the `picked is None` fallback at :1636 takes `options[0]`, which IS honor_defender; under `first` options[0] is taken by design. So the driver answers `honor_defender` under ALL FOUR diplomacy policies, not just `decline` as the row's title says. The paradox dialogue does reach the arm: `diplomacy.py:8453-8492` pushes it via `mount_over_mail` with `blocking: True` and options[0].action == `honor_defender`, and `main.py:1554` stamps `response["diplomatic_dialogue"] = world.pending_diplomatic_dialogue`. (`commitment_paradox_popup` being in DISPLAY_ONLY_KEYS at driver:216 hides only the POPUP render — the answerable DIALOGUE is live, so FA-72 is NOT gated behind FA-N35 as REPRO_J5's cross-row note 2 implies.)

**Evidence.**

Probe p6/p7 (TestClient, mock, `cheat trigger_commitment_paradox Prussia Austria`):
```
@@ response.diplomatic_dialogue.type: commitment_paradox
@@ options: [('honor_defender','Honor alliance with Austria'), ('break_defender_alliance','Side with Prussia')]
@@ blocking: True dialogue_id: 1
@@   driver answers under diplomacy=decline:  honor_defender
@@   driver answers under diplomacy=accept:   honor_defender
@@   driver answers under diplomacy=first:    honor_defender
@@   driver answers under diplomacy=propose:  honor_defender
@@ choice='honor_defender': success=True | France honors its alliance with Austria and declares war on Prussia! Cannot declare war: war_instance_side_conflict (both nations live in war_instance…
@@ choice='break_defender_alliance': success=True | France abandons its alliance with Austria.  France-Austria ALLIANCE -> PEACE
```
The driver's real POST body is `{"choice": …, "dialogue_id": …}` (driver:1391-1394) and it IS accepted; `{"action": …}` is refused ("Please choose an option (1-2), Sire."), so a probe using `action` proves nothing. Producer source, `backend/game_logic/diplomacy.py:8476-8481`: `"description": f"Go to war with {aggressor} in defense of {target}", "action": "honor_defender"`. Latency unchanged: `grep -rl commitment_paradox docs/audits/playtest_digests/` = 0 files.

**WARNING - what the row's own fix_shape would break.** The row's fix_shape — token-match the needles — fixes ONE of four modes and leaves three declaring war. Measured: with `"no"` deleted, `decline` falls through to the `mode == "decline"` branch of :1636 and takes `options[-1]` = break_defender_alliance (fine), but `accept`/`first`/`propose` still take `options[0]` = honor_defender by the SAME fallback line. Building only the needle change and closing the row would leave the war declaration standing on the accepting modes — which is the arm `--diplomacy propose` and every accept-arm run uses. Second hazard: token-splitting is safe for the ids observed (accept_settlement_offer, confirm_pair_substitute, defy_ultimatum all survive), but only because their needles are already whole tokens — re-check the needle sets against the live option vocabulary rather than assuming.

**Minimal fix.** ONE seam, `_pick_dialogue_choice`. (1) Add an explicit `paradox` policy key with a stated default and answer `commitment_paradox` from it BEFORE the generic mode block — this is the only change that covers all four modes. (2) Separately, split needles on `_` and compare whole tokens, and drop `"no"` (it earns nothing: decline/reject/refuse cover the live vocabulary; verified `find("decline","reject","refuse")` returns None on this payload). (3) Say in docs/PLAYTESTING.md which arm each standalone family defaults to. NB neither paradox arm is state-neutral — `honor_defender` declares war, `break_defender_alliance` sets France-Austria ALLIANCE→PEACE and writes a betrayal — so the default must be CHOSEN and named on the record, not called 'least state-changing'.

**Tests.** None. No test in tests/ imports or asserts `_pick_dialogue_choice`'s needle list; `tests/test_playtest_driver_instrument.py` (23 tests) pins `_option_id` preference order and the clarification/envoy arms only. Nothing pins POLICY_DEFAULTS' diplomacy needles. No pin asserts the defect.

**Flags.** none


### FA-78 - REPRODUCED-BUT-NARROWER (on the count) and WIDER (on the seams)

**Mechanism.** `_enabled` (driver:1030) is consulted at exactly TWO sites at HEAD — the strategic-interrupt arm (driver:1210) and the marshal-petition arm (driver:1296). `_pick_dialogue_choice` never consults it in EITHER branch: the `proposal_confirm` type-table branch (driver:1602-1605) does `return find("confirm","yes","proceed","send") or "confirm"` — a LITERAL fallback that cannot be removed by filtering the options list — and the generic mode block scans `keywords` built at :1545 from every option regardless of `enabled`. Backend side unchanged: `diplomatic_dialogue.py:886-896` sets `_opt["enabled"] = False` / `available: False` / `unavailable_reason` on `execute_proposal` under WIN-1, and the refusal re-attaches the same dialogue (the code comment at :877-881 says so), so the same disabled option is re-offered every turn forever. Slice 8's stale-retry bound (`MAX_STALE_ATTEMPTS`, driver:237/1368) does NOT catch it: that bound is keyed on `reply["stale_dialogue"]`, and a WIN-1 refusal is an ordinary `success: False`.

**Evidence.**

Probe p1 against the shipped driver module:
```
proposal_confirm diplomacy=accept   -> confirm
proposal_confirm diplomacy=decline  -> confirm
proposal_confirm diplomacy=propose  -> confirm
_enabled(options[0]) = False
generic accept-arm diplomacy=accept -> accept_settlement_offer   <-- disabled, and NOT in the row
_enabled call sites: 1030 (def), 1210, 1296
```
Count corrected TWICE. The row says twelve; REPRO_J5 corrected it to three by grepping only the Austria wording. Measured at HEAD: `grep -c "refused: Making peace with" audit-propose/digest.md` = **7** (lines 9,23,59,74,100,123,149 — exactly the row's own citations, Austria ×2 + Britain ×5) and audit-latewar-t20 = 1, but latewar:41 is `POPUP diplomatic_dialogue: proposal_confirm → (stale passthrough — #26 already answered this chain)`, a different phenomenon. **Truthful figure: 7 disabled pressings, all in audit-propose.**

**WARNING - what the row's own fix_shape would break.** The row's fix_shape says only "filter `options` through `_enabled` before the type table and keyword scans". Followed literally that is a NO-OP for the headline case: the `proposal_confirm` branch returns the string `"confirm"` when `find()` misses, so filtering the list makes `find()` miss and the driver POSTs `"confirm"` anyway — the same seven refusals, now with the filter in place and the row marked closed. The literal fallbacks must be gated too. Second hazard: the fix_shape's alternative "take the first enabled option" would, on `proposal_confirm`, silently press `cancel_proposal` — turning an artefact refusal into an artefact WITHDRAWAL, which is worse because it looks like a decision.

**Minimal fix.** In `_pick_dialogue_choice`, build `options`/`keywords` from enabled options only at :1544-1545, AND make the two literal fallbacks conditional: `return find(...) or ("confirm" if any_enabled else None)`, same for the `keep`/`defy` literals at :1614-1624 and the keyword fallback at :1637-1641. When nothing is enabled, log `(disabled: <options[0].description>)` and return `None` so the surface is left standing with its reason — the digest then carries WIN-1's honest-availability text instead of an artefact refusal.

**Tests.** None assert the literal fallback. `tests/test_playtest_driver_instrument.py` clarification/envoy tests build enabled-by-default payloads and stay green; `test_no_actionable_options_left_standing` (:210) is the clarification arm, not this one. Slice 8's `TestAStaleRefusalIsNotAnAnswer` / `TestTheRetryIsBounded` are keyed on `stale_dialogue` and are unaffected. No pin asserts the defect.

**Flags.** none


### FA-79 - WIDER-THAN-FILED

**Mechanism.** Three parts, all live at HEAD. (a) `POLICY_DEFAULTS["redemption"] = "dismiss"` (driver:153) and the arm at driver:1337-1343 POSTs it blind; `disobedience.handle_redemption_response`'s dismiss arm (backend/commands/disobedience.py:1870-1910) calls `world.destroy_marshal(marshal_name, cause="dismissed", log=False)` at :1894 — the PC15-1 single removal seam, a permanent `fallen_marshals` tombstone. (b) `petition: first_enabled` (driver:156) → driver:1291-1300 takes the first `_enabled` option, which by construction is the free arm. (c) Neither arm reads its reply: `followups.append(self.t.post(...))` with no `success`/`message` handling, and the `↳ refused:` note exists only in the dialogue arm (:1461-1464). **The widening:** slice 14's FA-N76 added `REDEMPTION_ANSWER_MUST_BE_OFFERED` (disobedience.py:1786-1798), which refuses a choice the audience did not offer and deliberately leaves the question STANDING (no latch cleared). Since the driver never reads the reply, a blind `dismiss` against a Last-Marshal-Protection audience is now a silent, permanent no-op that re-raises every turn — invisible in the digest.

**Evidence.**

Probe p8 on the shipped 1805 boot:
```
A. full roster, options offered: ['grant_autonomy','administrative_role','dismiss']
B. last marshal, options offered: ['grant_autonomy']
B. POST dismiss -> False | That is not among the courses open to you, Sire. Ney awaits one of: grant_autonomy.
B. Ney still on the roster? True | redemption_pending still standing? True
C. POST dismiss on full roster -> True | Ney has been relieved of command. 24,000 troops transferred to Davout…
C. Ney still on the roster? False | fallen_marshals: ['Ney']
```
Archive at HEAD: `grep -rn "POPUP redemption" docs/audits/playtest_digests/*/digest.md` = exactly ONE line — `audit-flagship-mock/digest.md:208: - POPUP redemption: Bernadotte, 9 → dismiss` — with no outcome line and no later mention of Bernadotte. Petition answers in that same run: 10 acknowledge / 2 accept_breach / 2 concede / 2 detach, all free arms. `--redemption` has no argparse entry (driver:2055-2087 lists only --objection and --diplomacy among policy flags), so the default is unreachable from the CLI.

**WARNING - what the row's own fix_shape would break.** Two. (1) The row's `petition: rotate` (cycle enabled arms per kind) makes every archived digest non-regenerable AND makes the reward economy depend on petition order — deterministic within a seed, but nothing in the archive can be reproduced. Ship it OPT-IN, never as the default, and say so in the digest header. (2) `paid_first` (prefer arms with `ap_cost`) spends AP the scripted commands were budgeted for, which changes refusal counts on every downstream command in the turn — it is not a logging change and must not be bundled with (A).

**Minimal fix.** Two pieces, land (A) first. (A, no behaviour change, determinism-free): write the `/respond_to_redemption` and `/marshal_petition_response` reply `message` into the digest — one `self.d.note(...)` per arm — so a refusal or an outcome is legible. This alone converts the FA-N76 silent no-op into evidence. (B, behaviour): flip `POLICY_DEFAULTS["redemption"]` to `grant_autonomy` (self-expiring in 3 turns, no roster change, no permanent AP grant — the arm ranking is grant_autonomy < administrative_role < dismiss, and `administrative_role` permanently adds `world.bonus_actions += 1` and zeroes the corps) and add a `--redemption` flag.

**Tests.** None. Grep found no test asserting `POLICY_DEFAULTS["redemption"]` or naming `"dismiss"` as a driver default; `tests/test_autonomy.py` tests the redemption ARMS through the backend, not the policy. No pin asserts the defect.

**Flags.** none


### FA-75 - WIDER-THAN-FILED (and half the filed fix is unnecessary)

**Mechanism.** The driver's only mailbox read is `(transport.get("/mailbox") or {}).get("envoy_digest")` at driver:1873, answered by `answer_envoy_digest` (driver:1474-1500) which walks `envoy_digest["items"]` and POSTs `/mailbox/respond`. `envoy_digest` is built by `is_routine_small_court`, which excludes majors by tier — so anything a major court sends sits in `/mailbox` `items` untouched forever. `mailbox/activate` and `pending_envoy` occur 0× in the driver. The row's headline understates it: the offer does not merely go unseen, it NEVER LAPSES — Britain's settlement offer (mailbox_id 8) stood in the mailbox from turn 4 to turn 13 on the shipped board, ten consecutive turns, and would stand for the whole campaign. That is the structural reason no archived arm has ever ratified a settlement (FA-90 arm 1's premise).

**Evidence.**

Probe p4, shipped 1805 boot, seed `repro16`, 12 driven turns answering only the capture question:
```
t4:  mailbox=3  letter-book=2  NOT-in-letter-book=[('Britain','settlement_offer',8)]
t5:  mailbox=3  letter-book=1  NOT-in-letter-book=[('Britain','settlement_offer',8), ('Prussia','open_borders',9)]
…
t13: mailbox=5  letter-book=2  NOT-in-letter-book=[('Britain','settlement_offer',8), ('Britain','armistice_losing',26), ('Austria','armistice_losing',27)]
TOTAL over 12 turns: mailbox items seen=38  letter-book rows=22
courts the driver can NEVER answer: {('Britain','settlement_offer'):10, ('Prussia','open_borders'):4, ('Britain','armistice_losing'):1, ('Austria','armistice_losing'):1}
```
16 of 38 item-turns unreachable, including armistice offers from BOTH courts France is at war with. And the evidence half is already on the wire — probe p2, same board:
```
t3: dispatch.lapsed_offers: [{'nation':'Prussia','proposal_type':'open borders'}, {'nation':'Ottoman','proposal_type':'friendly gift'}, {'nation':'Naples','proposal_type':'friendly gift'}]
t2: dispatch.pending_envoy_count: 3  pending_envoys: [Prussia open borders ACTIVE, Ottoman open borders WAITING, Naples open borders WAITING]
```
(`dispatch.py:2373-2392` writes both; `GET /dispatch` is already fetched every turn into `morning` at driver:1949.)

**WARNING - what the row's own fix_shape would break.** The row's backend half is dead weight and its premise is FALSE: it says "no `/command` layer forwards `lapsed_offers` … add it to `_COMMAND_RESULT_SIMPLE_FIELDS` (main.py:554)". `lapsed_offers` is already on the morning dispatch (`dispatch.py:2373`) and `pending_envoys`/`pending_envoy_count` at `:2382-2392`, and the driver already fetches `/dispatch` every turn. Adding the key to `_COMMAND_RESULT_SIMPLE_FIELDS` (which is at main.py:719 today, not :554) is a truthy-copy that is `[]` on almost every turn — harmless but pointless, and it would make the row look built while the digest still says nothing. Skip the backend edit entirely.

**Minimal fix.** (A-half, no behaviour change, determinism-free — ship first) print `morning["lapsed_offers"]` and `morning["pending_envoys"]`/`pending_envoy_count` as digest lines in the block at driver:1949-1981. Zero backend change. This alone turns the blind spot into a measured one. (B-half, behaviour) after `answer_envoy_digest`, walk `(GET /mailbox)["items"]` for any `mailbox_id` not in the digest, `POST /mailbox/activate {mailbox_id}` and drain the returned payload through the existing dialogue arm.

**Tests.** None. No test reads `answer_envoy_digest`'s coverage or the `morning` block's line set. `tests/test_igr_f_envoy_digest.py` (83) tests the BACKEND letter-book, not the driver. No pin asserts the defect.

**Flags.** none


### FA-85 - REPRODUCED (and REPRO_J5's own recommended yard is wrong)

**Mechanism.** `tools/playtest_scripts/naval_descent.json` turn 2 is still `["Soult, march to Normandy", "build ships"]` and turns 12/13 type `land Soult in Munster with 12,000 men`. `naval_executor._execute_naval_expedition` at backend/commands/naval_executor.py:289-295 refuses when `loc_controller == marshal.nation and location not in naval.controlled_dockyards(...)`. Normandy is a `camp_provinces` entry, not a dockyard, so the script's only expedition commands can never fire and the archived naval digest carries zero expedition evidence.

**Evidence.**

Probe p5, shipped boot, seed `historical`:
```
controlled_dockyards(France) at boot: ['Bordelais','Brittany','Flanders','Provence']
camp_provinces: ['Flanders','Artois','Normandy','Brittany']
yards NOT in camp: ['Provence','Bordelais']
camp_strength at boot: 0     DESCENT_CAMP_STAGED_TURNS = 2
Soult location: Lorraine strength: 30000
```
Archive unchanged: `audit-naval/digest.md:164` and `:183` both carry `X An expedition assembles at a dockyard, Sire — Soult must stand at one of our yards: Brittany, Flanders, Provence`; `grep -in "expedition" audit-naval/digest.md` returns only those two refusals. (All four yards ARE controlled at boot, so the three-yard refusal text means Bordelais had been lost by turn 12 in that run — a fixer must read `controlled_dockyards`, never the authored list.)

**WARNING - what the row's own fix_shape would break.** The row's own alternative — "use Ney, already at Flanders, as the landing marshal" — collides with the script's turns 6/8/11/14 (`Ney, march to London`): Ney IS the Descent arm, and taking him off it deletes the thing the script exists to measure. REPRO_J5's correction ("Brittany is the safe yard") is ALSO wrong: `camp_provinces` = ['Flanders','Artois','Normandy','Brittany'], so Brittany is a camp province too, and `naval.camp_strength` (naval.py:1545-1558) sums every friendly marshal standing in one — parking Soult's 30,000 there changes the Descent staging gate and `_pick_crossing`'s camp-first tiebreak (naval.py:2006-2020). The only French yards outside the camp set are **Provence** (Mediterranean — absurd for a Munster landing) and **Bordelais** (Atlantic). Bordelais is the safe yard.

**Minimal fix.** Script edit: turn 2 → `Soult, march to Bordelais`, keeping the `land` at 12/13 (verify arrival in the digest, or slip `land` a turn). Plus the driver guard the row asks for: mark a run `SCRIPT PRECONDITION` when every `land`/`naval_expedition` line in a script is refused, so a naval digest can never again be filed as evidence of a mechanic that never ran.

**Tests.** None. Nothing pins `naval_descent.json`; `tests/test_naval_descent.py` and `tests/test_naval_free_ireland.py` test the mechanic. The only script drift pin in the tree, `tests/test_fa_slice8_the_instrument_2026_09_02.py::TestTheTutorialScriptMirrorsTheShippedLesson`, is scoped to `tutorial_lesson*.json`. No pin asserts the defect.

**Flags.** none


### FA-102 - REPRODUCED (contract hazard now larger than when filed)

**Mechanism.** `reload` occurs 0× in tools/playtest_driver.py. `--save-at` POSTs `/save` at driver:1904; `--from-save` POSTs `/load` at driver:1837, once, at boot. The module RNG is reseeded ONLY at the top of each turn from `(seed, world_turn)` — `seed_module_rng` is called at driver:1832 (boot) and :1863 (per turn) and nowhere else, and only `if not args.http`.

**Evidence.**

`grep -c reload tools/playtest_driver.py` → `0`. Loop shape read at driver:1855-1945: reseed(:1863) → letter-book → scripted commands → optional /save(:1904) → `end turn` → digest → drain → optional retry → /ledger → next iteration reseeds. `/load`'s re-attach block at backend/main.py (the `@app.post("/load")` body) is explicitly NON-draining and fills `pending_capture_choice`, `capture_data`, `pending_interrupt` and (WO-41) `pending_redemption` back onto the response.

**WARNING - what the row's own fix_shape would break.** The row's own contract is unachievable as written and would be closed on a false pin. It promises "with `--reload-every 1` the digest must be byte-identical to the no-reload run of the same script and seed, load lines aside." Two reasons it will not be: (i) the RNG is reseeded only at the turn boundary, so ANY POST inserted mid-turn shifts every draw after it in that turn — the placement above fixes this, but only for Mode A, since `seed_module_rng` is skipped entirely under `--http`; (ii) `/load` re-attaches pending questions and the row wants them drained, and a drain POSTs ANSWERS — extra state changes the no-reload run never made. Slice 6 and slice 9 both ADDED attach keys since the row was written, so (ii) is bigger now than when filed. State the contract as "byte-identical modulo the load lines AND any answer the load re-raises", and scope the determinism claim to Mode A.

**Minimal fix.** `--reload-every N` inserted at the TURN BOUNDARY — after the `/ledger` read at the end of the loop body, before the next iteration's `seed_module_rng` at :1863 — POSTing `/save` then `/load` of the same file into the run's sandboxed SAVE_DIR, stamping the round trip in the digest, and putting the set of re-raised questions INTO the digest so a transparency defect is legible rather than silently absorbed.

**Tests.** None. No pin asserts the defect.

**Flags.** none


### FA-90 - REPRODUCED-BUT-NARROWER (a roll-up, one third already owned elsewhere)

**Mechanism.** Every cited key is real and unread. `peace_ratification_summary` is stamped by `_include_peace_ratification_summary` (backend/main.py:770-779) and occurs 0× in the driver; `response["notifications"] = world.notifications.get_pending()` (main.py:595, :1644) occurs 0× in the driver; the reward rail's `"action_command": f"grant {marshal.name} a rente"` lives at backend/game_logic/dotation.py:1096 and occurs 0× in main.py AND 0× in the driver. Neither of the two proposed scripts exists (`ls tools/playtest_scripts/` shows 28 files, none homeland/gauntlet).

**Evidence.**

```
peace_ratification_summary     driver=0  main.py=10   (def at main.py:770, set at :779)
notifications                  driver=0  main.py=19   (response stamps at :595, :1644)
action_command                 driver=0  main.py=0    (dotation.py:1096)
tools/playtest_scripts/{homeland*,gauntlet*} -> 0 files
```
But arm (1)'s `/pending_envoy` + `mailbox/activate` loop IS FA-75's B-half, and arm (3)'s per-command parse provenance was BUILT by slice 15b (`tests/test_fa_slice15b_…::TestTheRunRecordsWhoParsedItAndOnWhatBoard`, six tests incl. `test_the_backend_stamps_the_players_parse_only` and `test_the_provenance_is_display_only`). Only three things here are genuinely unowned: (i) the `peace_ratification_summary` digest line, (ii) the `--reward` notification-driven arm, (iii) the two committed scripts.

**WARNING - what the row's own fix_shape would break.** Arm (2) is now actively harmful. It says the reward arm should also "type the rail's last-stand words ('fight to the last'/'attempt breakout') so a parked fate question (FA-36) is answered when raised". FA-36 was CLOSED by slice 2 — the order-free ask now reaches `strategic_reports` with `order_status: awaiting_response` and is promoted to `pending_interrupt`, and the driver's interrupt arm answers it by POST at driver:1206-1224. Typing those words as a COMMAND would race the popup answer and re-enter the FA-N2 typed-answer router that slice 0 exists to guard. Do not build arm (2)'s fate-word half. Second, smaller hazard: arm (3)'s provenance half is already shipped — re-building it re-opens slice 15b.

**Minimal fix.** Build only (i) and (ii), and only AFTER FA-75's B-half lands — arm (1) is that loop plus a settlement ladder, and building it here duplicates FA-75. (i) is a one-line `Digest` addition reading `response["peace_ratification_summary"]`. (ii) is a `--reward pay|ignore` policy that reads `response["notifications"]` and types the row's own `details.action_command` verbatim (the UX23-A grant-a-rente string, already a pinned corpus row). File the two scripts as separate work.

**Tests.** None for the unowned pieces. Slice 15b's `TestTheRunRecordsWhoParsedItAndOnWhatBoard` would flip if the build re-implemented arm (3)'s provenance. No pin asserts the defect.

**Flags.** none


### FA-89 - REPRODUCED-BUT-NARROWER (slice 8 closed the sharper half; the row's 'one source' is not achievable)

**Mechanism.** `grep -n scenario_name backend/main.py` returns NOTHING — the field is serialized (`world_state.py`) and read by `dotation.py` / `jealousy.py` / `save_manager.py`, but never reaches a response, and main.py's only tutorial awareness is `SCENARIO_ALLOWLIST = {"tutorial": TUTORIAL_SCENARIO_PATH}` at :123 and an autosave skip at :4584. The lesson's progression is entirely client-side: `tutorial_overlay.gd` `STEPS` (:52), `_derive_step_for_turn` (:350), `observe` (:366), `_advance_one` (:447). So no unattended run can assert a beat FIRED. Slice 8's FA-40 already closed the row's sharper half: `tutorial_lesson.json` now carries `"scenario": "tutorial"`, the bombard at loop 2 (not 4), `"policy": {"objection": "insist"}` and a `_note` naming its drift pin; `args.scenario = args.scenario or script.get("scenario") or ""` at driver:1776.

**Evidence.**

```
$ grep -n "scenario_name" backend/main.py     -> (no output)
$ grep -n '"advance":' tutorial_overlay.gd    -> 15 predicates, e.g.
   "_pred_objection_pending", "_pred_objection_resolved", "_pred_bombardment",
   "_pred_capture_pending", "_pred_capture_resolved", "_pred_recruited"
```
Several of those read CROSS-RESPONSE latches the backend does not have: `_note_observations` sets `_saw_objection`/`_saw_capture`, `_note_kienmayer(response)` latches a kill, and `_pred_recruited` compares against `_last_infantry_pool` carried from the previous response (overlay `observe`, :366-390). Slice 14c also recorded that `turn_gate` gates DISPLAY, not ADVANCE, and that a `const` Dictionary is READ-ONLY at runtime in Godot 4 and invisible to the parse harness.

**WARNING - what the row's own fix_shape would break.** Two. (1) The row's `--strict` clause — "fails when a scripted beat's precondition is refused" — would turn slice 8's DELIBERATE refusal into a run failure; the slice-8 record states "the only refusal left in either arm is the one the card explicitly TEACHES". Do not build that clause. (2) The row's phrase "derived from the SAME payload predicates … so the overlay and the driver consume one source" is not achievable and will mislead the builder: the advance predicates are fifteen named GDScript functions over per-client latches that persist ACROSS responses (`_saw_objection`, `_saw_capture`, `_last_infantry_pool`, the Kienmayer latch). A backend key is necessarily a SECOND, approximate source — say so on the record and pin it as approximate, or the build will either re-implement the latches wrongly or claim a single source it does not have.

**Minimal fix.** A display-only `tutorial_step` key on `/command` responses gated on `world.scenario_name == "tutorial"` (or `GET /tutorial_state`), plus one `SCHOOL: step N (<beat name>)` digest line. Strictly GR6 — nothing mechanical may read it, and the overlay must KEEP deriving its own step.

**Tests.** None if the fix is the display-only key. `tests/test_fa_slice8_the_instrument_2026_09_02.py::TestTheTutorialScriptMirrorsTheShippedLesson::test_every_suggested_command_is_issued_at_its_own_gate` and `::test_the_driver_reads_the_scripts_scenario` own the static half and would flip only if the build edited `tutorial_lesson.json`'s turn keys or the overlay's `turn_gate`s. No pin asserts the defect.

**Flags.** none


---

## Group: FA-56, FA-67, FA-61, FA-49, FA-52

### Recommended landing order

1. FA-56 FIRST — one word, control-proven in both directions, zero blast radius, no pin flips, no `.gd`, no new field, and its filed fix is the only correct one in the set. Add the missing behavioural pin (the row's shape is sound, including the from_dict round-trip arm) since nothing currently exercises the pause.

2. FA-67 SECOND — one message + one lying comment, backend only. Re-word to state the objection dependency; do NOT delete the battle clause and do NOT touch the "at 20" clause (FA-26 landed and a pin asserts the "20"). Correct the comment to name `VindicationTracker`. Worth adding the third, unfiled clause: `get_trust_gain_modifier` (authority.py:133-153) cuts the +3 to +1 for a player who trusts on more than 4 of 5 objections — the advice's first clause degrades its own second clause.

3. FA-61 THIRD — backend only, no `.gd`. Add `ceiling_strength` as a NEW key computed on the resolver's own modifier basis (aura included) and append a second clause only when the key is present; leave `committed_strength` and `odds_band` byte-identical or the CA9-row-2 muster gate moves with them. The three label pins hand-build a preview with no `ceiling_strength`, so an additive clause keeps them green — do not rename the phrase.

4. FA-49 + FA-52 LAST, AS ONE SLICE — the only `.gd` touch, the only serialized-dict addition (`option_costs` inside the opaque `pending_interrupt`, marshal.py:1737/:1946 — needs a SAVE_FORMAT_REFERENCE row beside the FA-slice-2 `location` precedent at :631, and a pre-fix save must render with no suffix), and the only one carrying a design question. Build the three safe halves without a ruling: the flavor-branched copy (0 pins), the DERIVED cost table across both files, and the `.gd` suffix. Put the tax to the user with the slice-3 precedent attached — `_respond_combat_stalemate` already prices an order-preserving "Continue as Ordered" at 0 — and note that scoping the change to HOLD/SUPPORT flips no pin because all twelve cannon-fire fixtures in `test_strategic_executor.py` are MOVE_TO. File the nation-blind trigger as its own row (it has none today) rather than folding it into the payment.

### Cross-row findings

SHARED FACT THAT KILLS ONE CAUTION IN THE PRIOR REPORT. J7 wrote of FA-52 "I did NOT verify whether the AI ever reaches `_respond_cannon_fire`". It cannot. `process_strategic_orders` iterates `[m for m in world.marshals.values() if m.nation == world.player_nation and m.in_strategic_mode]` (strategic.py:869-871), and `strategic_exec.handle_response` has exactly two callers, both player endpoints (`backend/main.py:2693` typed route, `:4268` /strategic_response). **The cannon-fire trust write is structurally player-only, so neither FA-49 nor FA-52 can move `BASELINE_SERIES` or M1-M7.** Likewise FA-56 (the Vindicated Garrison block returns early on `marshal.nation != self.player_nation`, world_state.py:2951) and FA-67 (`_check_trust_warnings` skips non-player marshals, ~:12290). FA-61 is series-safe ONLY while `committed_strength` is left byte-untouched.

FA-49 + FA-52 ARE ONE SLICE AT ONE FUNCTION. Confirmed. Land together, file once. Between them they need: one copy branch, one derived cost table across ~11 builders in TWO files, one `.gd` suffix, and (design) one tax ruling. Nothing else in this set touches `.gd`.

REACHABILITY IS MEASURED, NOT ASSUMED. `_check_interrupts` returns None for `literal` and auto-redirects for `aggressive`, so the ask reaches exactly three French marshals at boot — Davout and Bernadotte (cautious) and Napoleon (sovereign, who falls into the `else` branch). The archived audit digests contain 19 organic asks distributed exactly that way (Davout 15 / Napoleon 3 / Bernadotte 1), and `docs/BUG_FIXES.md:1833` records an unattended run where "Bernadotte picked up an organic `cannon_fire` ask at t4". Every archived answer is `investigate` because `tools/playtest_driver.py` has no interrupt-policy flag and always answers `investigate` — so the corpus proves the ASK's frequency but has never recorded a payment. A frequency probe of the tax needs a driver flag, not another read.

SIDE-EFFECT NOBODY FILED: Napoleon is charged −2 trust (off 100) for continuing his OWN order. His voice is already correct (`marshal_voice.py:361` routes the interrupt to Berthier — a recorded NP-V decision, and ~~NPC-22~~ was struck over it); only the price is odd. One line, rides FA-52's tax arm.

STALE-LINE TALLY FOR THIS SET: 5 of 5 rows carry a stale primary line number. FA-56 :2884→:2959 · FA-67 :12097→:12321 · FA-61 :1493→:1488/:1498 · FA-49 and FA-52 :568/:596→:1356/:1384 (stale by ~660) and interrupt_popup.gd :69→:70. Navigate by symbol.

`fix_shape` CONTRADICTS THE CORRECTED SUMMARY IN ONE ROW HERE: FA-67. Its summary's whole evidence chain ("no combat seam adds trust") is refuted, and its fix ("delete the battle clause") deletes the only true half. Its FA-26 escape clause is also stale — FA-26 landed in slice 9.

TWO MORE FIX SHAPES WOULD SHIP A REGRESSION IF FOLLOWED LITERALLY: FA-61 (prints a 90,172 "ceiling" the resolver exceeds at 96,789 — a shown!=applied fix that ships a new shown!=applied, measured) and FA-49 (a static cost table would print −3 where the first-step charge is 0). FA-52's copy prescription produces ungrammatical output for its own headline case. **So 4 of these 5 rows cannot be built as filed. Only FA-56 can.**


### FA-56 - REPRODUCED

**Mechanism.** `WorldState.calculate_visibility`'s Vindicated Garrison block gates the fog lift on `if getattr(marshal, "_literal_intel_paused_turn", None) == turn:` — **world_state.py:2959** (row says :2884, stale by 75). The only writer anywhere is `jealousy.py:2724` `marshal.literal_intel_paused_turn = int(world.current_turn) + 1`, the PUBLIC serialized field (marshal.py:715 init / :1720 to_dict / :1927 from_dict). Nothing in the repository ever sets the underscore name, so the Rebuke's promised one-turn intel pause has never fired.

**Evidence.**

Control probe on the 1805 boot, both directions: `BASELINE (no pause) scouted: ['Swabia', 'Brabant']` / `PUBLIC field == turn scouted: ['Swabia', 'Brabant']` (the pause does nothing) / `UNDERSCORE field == turn scouted: []`. Source line read at HEAD: `            if getattr(marshal, "_literal_intel_paused_turn", None) == turn:`

**WARNING - what the row's own fix_shape would break.** Nothing. This is the one row in the set whose filed `fix_shape` is exactly right (modulo the stale line number). It even names the `-1` default correctly.

**Minimal fix.** ONE word at world_state.py:2959 → `if getattr(marshal, "literal_intel_paused_turn", -1) == turn:`. Two things the build should keep from this pass: the default must be `-1` (matching marshal.py:715), not `None`, so a fresh object cannot accidentally match; and the writer's `+1` is CORRECT because `_advance_turn_internal` increments `current_turn` at world_state.py:9581 BEFORE calling `calculate_visibility()` at :10035 — a stamp made on turn N is honoured inside the same advance.

**Tests.** None. `grep -rn "literal_intel" tests/` returns only `tests/test_ca9_row3_phase_a.py` (lines 310/315/321/326/373/376) and two playtest fixtures. The A10 pin at :373-377 asserts `"literal_intel_paused_turn" in vars(m)` and `"_literal_intel_paused_turn" not in vars(m)` — it is what PROVES the reader is dead, and it stays green under the fix because the fix changes the READER, not the field. **No test drives the pause behaviourally**, so nothing currently asserts the defect and nothing flips. A behavioural pin should be added (the row's `behaviour_test` shape is sound, including the from_dict round-trip arm).

**Flags.** none


### FA-67 - REFUTED (headline) — a narrower row survives, and one surviving clause is NEW and unfiled

**Mechanism.** The warning is at **world_state.py:12321-12325** (row says :12097, stale by ~225) with the false comment at :12316-12319. **A won battle DOES add trust**: `combat_executor.py:2646` (post-combat pipeline step 11) calls `world.vindication_tracker.resolve_battle(...)` → `VindicationTracker.resolve_battle` (vindication.py:69) → the 'trust'/'victory' arm sets `trust_change = +3` (:118-121) → `marshal.modify_trust(...)` (:~194). The row's census missed it because it looked for a trust write INSIDE the combat files; the write is one call out. The warning's two clauses are not two pieces of advice, they are the two STAGES of one mechanic, in the right order.

**Evidence.**

Probe on the 1805 boot: `has_pending(Davout): True` → `resolve_battle victory -> Davout's judgment was vindicated! Victory proves the wisdom of trust.` → `trust 85 -> 88   delta 3`. Negative control: `has_pending(Bernadotte): False` → `resolve_battle -> None` → `trust 40 -> 40`. Expectation half: `Lannes get_expectation  0 -> 40  (battles_won 1)`. Warning verbatim: `[!] Lannes's trust is faltering (38). Trust his judgment when he objects, and give him a battle he can win — at 20 he will ask to be released.`

**WARNING - what the row's own fix_shape would break.** TWO, both material — this is one of the rows whose `fix_shape` contradicts its own corrected reading. (1) "delete the battle clause" would delete the ONLY TRUE HALF: `resolve_battle` is the sole consumer of `pending`, so trusting an objection with no subsequent battle resolves nothing and pays nothing — deleting the battle clause leaves the warning naming a lever that by itself never fires, which is the exact defect the row says it is fixing. (2) "say 'he will ask to be released the next time you order him' **unless FA-26 lands**" — **FA-26 LANDED** (slice 9, Sept 5, 2026; its net is inside this very function, ~world_state.py:12335: "every player marshal at trust <= 20 is put the question"). So "at 20 he will ask to be released" is now TRUE and must NOT be reworded — and `tests/test_pt_f_jealousy_channel.py:274` asserts `"20" in mine[0]["message"]`, so rewording it REDS a pin.

**Minimal fix.** ONE seam, the message at :12321-12325 — state the DEPENDENCY rather than delete the clause (e.g. "…and let him win the battle he asked for — a vindicated objection is the only thing that pays"), append `dotation.reward_remedy_phrase(self, marshal.nation, marshal)` when `dotation.is_eroding(marshal, self)` (both exist: dotation.py:1193 and :297), and correct the comment at :12316-12319 to NAME `VindicationTracker` so the next census does not repeat FA-67's own mistake. Keep the "at 20" clause.

**Tests.** `grep -rn "give him a battle he can win" tests/` = 0 hits — **nothing asserts the defect**. Two pins sit on this block, both survive an in-dict re-word: `tests/test_pt_f_jealousy_channel.py:256-263` scrapes `src.split("trust is faltering")[1].split("})")[0]` and asserts `"more independence" not in block` (fragile scrape — keep the message construction inside the same dict literal), and `:265-275` asserts "faltering" and "20" are in the message. `tests/test_fa26_the_question_is_asked_2026_09_05.py:871` indexes `src.index("def _check_trust_warnings")` — do not rename the function.

**Flags.** none


### FA-61 - REPRODUCED (verbatim, to the digit) — WIDER-THAN-FILED: two causes, and the row's own fix_shape ships a NEW shown!=applied

**Mechanism.** `CombatExecutor._format_muster_lines` (**combat_executor.py:1488**, label built :1498-1503) prints `preview['attacker']['committed_strength']` under the words "if all march". That figure is built at :1219 from `_committed_reinforcement_strength(..., expected_at=battle_region)` (:452; the `expected_at` arm at :505-509), which multiplies every eligible joiner by `_expected_arrival_weight` (:1597) — a probability-weighted MEAN, not a ceiling. **The second cause the row does not name:** the sovereign aura. `combat_executor.py:672-682` stamps `m.sovereign_presence = sovereign_aura_strength(...)` on every participant at RESOLVE time only, and `get_attack_modifier` reads it, so at preview time every joiner is under-priced by 10% whenever the Emperor marches.

**Evidence.**

Live `/command {"command": "Marshal Ney, attack Mack"}` on the shipped board (mock parser, swapped world): `MUSTER — Ney (24,000; 78,676 if all march) vs Mack (large force) at Swabia — the balance of force looks favorable.` … `WILL JOIN — Murat …` … then `Massed effective strength: 24,000 (lead) + 60,266 committed (Davout, Lannes, Napoleon) = 84,266.` — resolved 84,266 EXCEEDS the printed 78,676 with Murat absent. Direct measurement of the candidate ceilings at HEAD: `PREVIEW (expected_at=region): 54676.7 -> total 78676` · `CEILING (expected_at=None): 66172.5 -> total 90172` · `sovereign_aura_strength(France) = 1.0` · `CEILING with aura stamped: 72789.8 -> total 96789` · arrival weights `Davout 0.976 / Lannes 0.95 / Murat 0.176 / Napoleon 0.95`. Note the SAME block already prints `The Emperor commands in person — every corps on this field fights +10% harder, if he marches.` — the panel names the +10% and then prints a number that omits it.

**WARNING - what the row's own fix_shape would break.** THREE. (1) The prescribed `expected_at=None` ceiling prints **90,172** while the resolver with all four arriving under the aura reaches **96,789** — a 7% over-run. The row's fix would print a "ceiling" the game can exceed, re-creating the exact defect one layer up. Measured, not argued. (2) The row treats `committed_strength` as display-only. It is not: `objection_v2.muster_gate_arms` (:990-1007) reads the `odds_band` that combat_executor.py:5490 derives from it — the CA9-row-2 attack-confirm gate. **The number must not move**; only an additional, separately-keyed figure may be added. (3) WO slice 8 already RECORDED (test_wo_slice8_panel_states_its_terms.py:16 and :232) that `committed_strength` is α-scaled arrival-priced **combat weight, not a headcount** — so even a perfect ceiling is not "men marching". If the copy is opened at all, say effective strength.

**Minimal fix.** In `_build_muster_preview`, compute the ceiling on the SAME modifier basis the resolver uses (stamp or pass the aura, then call `_committed_reinforcement_strength(marshal, will_join_marshals, world)` with `expected_at=None`), thread it as a NEW key `preview['attacker']['ceiling_strength']`, LEAVE `committed_strength` byte-untouched, and in `_format_muster_lines` append a second clause only when that key is present (`"; ~78,676 expected, up to 96,790 if every corps arrives"`).

**Tests.** Three pins assert the literal phrase: `tests/test_creative_audit_ca9_2026_08_08.py:857` and `tests/test_enemy_phase_presentation.py:291` both `assert "41,000 if all march" in text`, and `tests/test_enemy_phase_presentation.py:297` asserts `"if all march" not in text` for the solo case. **Both call `_format_muster_lines` with a hand-built preview dict that carries NO `ceiling_strength` key** (ca9:846-856, enemy_phase:271-275) — so an additive clause behind an optional key keeps them green, while J7's fallback suggestion (rename the label to "expected") REDS both. `tests/test_pt_a_regressions.py:325-333` and `:405-417` pin `committed_strength < certain` — green as long as the number is untouched. **No pin asserts the defect.**

**Flags.** none


### FA-49 - REPRODUCED — WIDER-THAN-FILED on scope (two files, ~11 builders, one CONDITIONAL cost)

**Mechanism.** `StrategicOrderProcessor._respond_cannon_fire` (**strategic.py:1231**) charges `trust_change = -2  # Non-literal acting literal` at **:1356** for `continue_order`, `-3` at **:1384** for `hold_position`, and 0 for `investigate`. The cautious ask builder at **:3510-3520** emits `"options": ["investigate", "continue_order", "hold_position"]` and no cost key of any kind; the renderer `interrupt_popup.gd` sets `btn.text = OPTION_LABELS.get(option_id, ...)` at **:70** from the label map at **:23-36**. The re-ask window is `ignored_turn >= world.current_turn - 1` (:3327), so a marshal answered on turn N is suppressed on N+1 and asked again on N+2 — every other turn, as filed. Row's backend line numbers are stale by ~660; the `.gd` fix line :69 is now :70.

**Evidence.**

Probe on the 1805 boot, Davout under a HOLD with a battle two provinces away: `pending_interrupt keys: ['battle_location', 'command', 'interrupt', 'interrupt_type', 'marshal', 'message', 'options', 'requires_input']` / `options: ['investigate', 'continue_order', 'hold_position']` / `any cost key? []`, then `trust 85 -> 83 | trust_change -2`. Reachability is MEASURED, not theoretical: the archived audit digests carry **19 organic cannon-fire asks** — `POPUP strategic_interrupt: Davout, cannon_fire, Davout: 'Cannon fire at Franconia, Sire. Investigate?' → investigate` ×8 and 11 more (Davout ×15, Napoleon ×3, Bernadotte ×1) — exactly the three French marshals who reach the ask.

**WARNING - what the row's own fix_shape would break.** THREE, one of them severe. (1) **The row scopes the fix to "the interrupt report builders in strategic.py". Three more live in `strategic_executor.py` (:2129, :2355, :2406) — and those are the ONLY builders that set `is_first_step: True`, where `_respond_blocked_path`'s hold/cancel charge is genuinely 0 (`trust_change = 0 if is_first_step else -3`, strategic.py:1586 and :1605).** A static `option_costs` table emitted only from strategic.py would print "−3" on a first-step interrupt that charges nothing — a NEW shown!=applied of exactly the class the row exists to close. The costs must be DERIVED from `is_first_step`, not hard-coded. (2) `tests/test_wo_slice8_panel_states_its_terms.py:1104-1109` pins the literal string `'"attack_anyway": "Commit the Attack"'` inside `interrupt_popup.gd`; restructuring `OPTION_LABELS` into a dict-of-dicts to carry costs REDS it — costs must ride a separate payload key. (3) `options` is a list of strings, validated by `choice not in pending["options"]` at strategic.py:1199-1202 and looped as `for option_id in options` in the `.gd`; converting it to a list of dicts breaks both. Also `test_wo_slice8...:1050-1055` pins that MessageLabel is a plain `Label` — `Button.text` is plain too, so no markup in the suffix.

**Minimal fix.** Extract the four inline literals to module constants, add ONE pure `interrupt_option_costs(interrupt_type, is_first_step) -> dict` in `strategic.py`, and call it from every ask builder in BOTH files (`strategic_executor.py` already imports from `strategic` at :25). Then `interrupt_popup.gd:70`: append ` (trust −N)` from `interrupt_data.get("option_costs", {})`, plain text, no BBCode.

**Tests.** Nothing flips for the additive display fix. `tests/test_strategic_executor.py::test_cannon_fire_continue` (line **1271**) asserts the payment (`result["trust_change"] == -2` :1293, `davout.trust.value == trust_before - 2` :1296) but the display fix does not move the payment. Two `.gd` census pins in `test_wo_slice8_panel_states_its_terms.py` constrain the shape (see hazard). No pin asserts the ABSENCE of costs.

**Flags.** touches `.gd`, serialized field


### FA-52 - REPRODUCED verbatim — J7's "substantially a duplicate of FA-49" CONFIRMED for the trust-tax half; three residues survive, one of them decisive and new

**Mechanism.** Same function as FA-49. The unique halves: (i) the copy at **strategic.py:1367-1368** is a FIXED `f"{marshal.name} reluctantly continues the march, ignoring cannon fire at {battle_location}."` regardless of `order.command_type` — the only arm in the function that does not call `_strategic_command_flavor` (the `investigate` arm does at :1239, `hold_position` at :1379); (ii) the trigger is NATION-BLIND — `_check_interrupts` scans `world.get_battles_within_range(marshal.location, 2)` at :3331 and skips only battles the marshal himself is IN (:3336-3338), with no nation filter anywhere; (iii) the price map is internally incoherent: obeying (order STANDS) costs −2, abandoning-to-hold costs −3, abandoning-for-the-guns costs 0.

**Evidence.**

Probe verbatim: `Davout reluctantly continues the march, ignoring cannon fire at Franconia. Davout fortifies Rhineland.` / `trust 85 -> 83 | trust_change -2` / `order_cleared: False | order still: HOLD` — and the battle recorded was `Blucher vs Hohenlohe`, a Prussian pair neither of whose sides is France. **THE NEW FINDING: slice 3 already decided this exact question the other way.** `_respond_combat_stalemate` (strategic.py:1682) prices `continue_order`/`attack_again` at **0** with `"order_cleared": False` and the copy `f"{marshal.name} presses on — {_strategic_command_flavor(order.command_type)} continues."` — the SAME popup, the SAME `OPTION_LABELS` entry "Continue as Ordered", the SAME semantics (the order stands), for free, and pinned at `tests/test_fa_slice3_the_order_tells_the_truth_2026_09_04.py:483` (`assert ney.trust.value == trust`). So FA-52's mechanics half is follow-through on a landed decision, not a fresh design call.

**WARNING - what the row's own fix_shape would break.** TWO. (1) **The row's own copy prescription does not work.** `_strategic_command_flavor` (strategic.py:28-36) returns NOUN phrases — `MOVE_TO`→"his march", `PURSUE`→"the pursuit", `HOLD`→**"his position"**, `SUPPORT`→"reinforcement orders" — so `continues {flavor}` yields *"reluctantly continues his position"* for the very HOLD case the row exists to fix. The row quotes 'keeps his position'/'continues the march' as though the helper produced verbs; it does not. A second verb arm or a re-phrase ("holds to his position") is required. (2) The fix_shape bundles "charges 0 … **for battles with no enemy participant**" into the payment. That is the nation-blind trigger, a different mechanic; pricing it at the payment leaves the ask still FIRING for a war France is not in, which is the part the player actually sees.

**Minimal fix.** One function, three separable parts. (a) COPY: branch the sentence on HOLD/SUPPORT vs MOVE_TO/PURSUE with its own verb — this is the safe half and flips nothing. (b) TAX (optional, design): `trust_change = 0` when `order.command_type in ("HOLD", "SUPPORT")`, matching the stalemate arm. (c) NATION-BLIND: a one-line filter at :3331-3338 skipping a battle where neither side's nation is at war with the marshal's — **and this half is UNFILED**: the row says "(separate finding)" but no such row exists anywhere in `docs/BUG_FIXES.md`.

**Tests.** `grep -rn "reluctantly continues" tests/` = **0 hits** — the copy fix flips nothing. `tests/test_strategic_executor.py::test_cannon_fire_continue` (line 1271) asserts the defect twice (`trust_change == -2` :1293, `trust.value == trust_before - 2` :1296) — **but its fixture is MOVE_TO, and so is every one of the twelve cannon-fire/blocked-path fixtures in that file** (`_set_strategic_order(... "MOVE_TO" ...)` at 1242/1276/1306/1338/1366/1393/1477/1495/1511/1538/1562/1614; not one HOLD or SUPPORT). So the HOLD/SUPPORT-scoped tax fix flips **nothing**; only the row's alternative "drop the tax entirely" reds :1293/:1296. That narrows J7's "treat the number as a design question" — the risk is design, not regression.

**Flags.** none


---

## Group: FA-44, FA-65, FA-69, FA-93, FA-95, FA-98, FA-100

### Recommended landing order

FA-100 half (a) FIRST — three line deletions, no copy judgement, no sibling, no pin at risk, and it is the only row in the batch whose defect silently corrupts a loaded world's state rather than its prose. Then FA-95 (two f-strings, zero pins, the correct sibling idiom is 40 lines away in the same file). Then FA-69 (largest census; do it before anyone else touches `capture_executor`, and sweep `dotation.py:355` with it). Then FA-93 AS ONE EDIT WITH FA-N50 AND FA-N47 — they share the string, and FA-93 alone leaves "MOVE TO" on screen while FA-N47 alone decides whether anyone sees the string at all. Then FA-65 (needs the pin-preserving redesign, not the filed fix). Then FA-44 (needs the floor-consistency ruling against WO-16's constant). FA-98 LAST, and put its beat-vs-state question and the `campaign_log` half to the user in one line before landing — PC15-D3's precedent is closed but it points the other way.

### Cross-row findings

SEVEN ROWS, ALL STILL LIVE AT HEAD (`3e43d89b`). None was closed by slices 8/1/2/3/4/5/6/7/9/10/11/12/13/14/15 or the six review rounds. Zero of the seven can move `BASELINE_SERIES` or M1-M7: FA-44/93/95/98 are pure copy; FA-65's `recovery_hint` is a display string on an event dict; FA-69 adds display-only keys; FA-100's three fields are read only by display/advisory surfaces (the AI reads `threat_by_target`, never `threat_sources_this_turn`) and the series never loads mid-turn. Say that in the landing record rather than asserting byte-identity as evidence.

STALE LINE NUMBERS MEASURED, not assumed. FA-44 cites `diplomacy.py:9418-9420` (really :9441) and `coalition.py:1433-1436` (really :1436). FA-93 cites `tactical_executor.py:480-481` (really :496-497), `executor.py:2493` (really :2717) and `display_names.py:16-19` (still current). FA-95 cites `:686/:695` (really :694/:703) and `world_state.py:10179` (the write is now `diplomatic_executor.py:5555/5557` + `turn_manager.py:184/187`). FA-98's line numbers are the ONLY set in this batch that are all current. FA-100 cites `world_state.py:9253/9257/9263` (really :9446/:9450/:9456) and `:7850` (really :7761/:8043). FA-69's :225/:236 are current; its `.gd` cite of ":56-61" is loose (the holder lands in `region_label` at :60; :59 is a static title). Navigate by symbol.

THREE ROWS' `fix_shape` WOULD SHIP A REGRESSION OR A DEAD FIX IF FOLLOWED LITERALLY. FA-44 (position above the fort arms; `{n}` is not a `_fill` placeholder). FA-65 (dropping the `>= 40` clause reds a standing pin and duplicates the ledger sentence). FA-93 (its "and {display}" option contradicts its open sibling FA-N50 and produces "breaks formation and March"). FA-100 is the sixth `fix_shape`-vs-`_corrected` member the verification pass named, and here the trap runs the other way: `_corrected` describes half (b) and explicitly rejects half (a)'s seam, which is the half the whole rest of the row is about. Build half (a); file half (b) separately.

TWO ROWS ARE WIDER THAN FILED. FA-69 has SIX backend sites, not the two in the row or the four in J7 — the two J7 missed are the confiscate and respect OUTCOME sentences (`capture_executor.py:276`, `:299`), so the raw key survives the answer as well as the question; plus `dotation.py:355` one function over. FA-98's routing note is stale: PC15-D3 was ruled and built on Aug 15, so the gate it defers to is closed — but it was ruled "gate the STATE, not the beats", and FA-98 is the first tutorial gate that suppresses a beat while leaving the state deliberately alive.

ONE PIN ASSERTS ITS ROW'S DEFECT: `tests/test_vassal_recovery_lever.py::TestVS1RecoveryHint::test_no_hint_below_healthy_band` (:107-114) asserts `recovery_hint == ""` at loyalty 30, and its docstring's stated reason ("Below 40 the crisis advisories take over") is FALSE — Talleyrand's advisory does not start until <35. The recommended FA-65 fix leaves that pin green by moving the remedy onto the `diplomatic_vassal_unrest` beat instead of widening the gate; if the build prefers to widen the gate, flip that pin CONSCIOUSLY and correct the docstring.

LAND TOGETHER: FA-93 + FA-N50 (one string, two producers, mutually exclusive frames) + FA-N47 (the notice is dropped on a refused action at `executor.py:2717`, so a copy-only fix is invisible on exactly the arms that fire above their own validation). FA-69 wants `dotation.py:355` in the same sweep or the endow surface still reads as the same bug.

ONE `.gd` IN THE BATCH: `capture_choice_dialog.gd` (FA-69), which also needs `Utils.display_nation_name()` on `estate_holder_nation` at :57/:62/:63. ONE SERIALIZED DICT GAINS KEYS: `world.pending_capture_choice` round-trips (`world_state.py:7122` / `:7725`), so every new key must be `.get()`-safe on a pre-fix save and `estate_holder` MUST stay the machine key (`_handle_estate_choice` re-reads it at `capture_executor.py:256` and a humanised value returns "The estate question has lapsed.").

FA-44's `player_consequence` is now MOSTLY OWNED BY A LANDED SIBLING and the build should not re-fix it: WO-16's `dispatch.OWN_MAULED_MIN_CASUALTIES = 500` already suppresses the sub-500 briefing headline, so the "drowning the real headline" half is gone. What survives is the battle report's own verdict. That also creates a consistency question the record must answer: WO-16's constant carries a written dissent ("if 500 is tuned TWICE, take the fraction-of-national-strength form"), and FA-44 proposes a SECOND absolute floor at 1,000 for the same question. Pick one of the two existing floors and justify the choice; do not mint a third.


### FA-44 - REPRODUCED-BUT-NARROWER

**Mechanism.** `battle_report._pick_observation` (def at :617) has no battle-size gate anywhere in its ladder. Casualties are bound at :634-635 and never consulted again. Priority 4 is two bare conditions — `if we_lost and _mod_value(their_mods,"terrain","bonus") >= 15` (:835) and the `our_mods` mirror (:837) — so a 1-vs-58 exchange draws the `lost_despite_terrain` bank (:338-342) verbatim. NARROWER than the row because the row's `player_consequence` ("eleven grave verdicts drowning the real headline") is now largely owned by WO-16: `dispatch.OWN_MAULED_MIN_CASUALTIES = 500` (:1949, gate at :873) already suppresses the *briefing headline* for a sub-500 loss. What survives is the battle report's own Berthier line, which still calls a 58-man skirmish "a grim day, Sire".

**Evidence.**

Probe against HEAD: `_pick_observation({atk_cas:1, def_cas:58, def_orig:58, defender mod {label:'terrain (hills)', type:'bonus', value:20}}, 'France')` → "Even the favorable ground could not save Massena, Sire. Archduke Charles overcame the terrain." and "Massena held superior ground, yet Archduke Charles prevailed. A grim day, Sire." — byte-identical to the digest quote. Source at :835-838 confirmed unchanged.

**WARNING - what the row's own fix_shape would break.** THREE things break if followed literally. (1) The stated position — "at the top of the loss ladder ... before :818" — sits ABOVE the two fortification arms (:818/:821) and the stance arm (:825). A sub-floor loss against a fort would then print a skirmish line instead of the strictly more informative "you attacked works and bounced" verdict. (2) The prescribed copy interpolates `{n}`, and `_fill` (:680-704) substitutes only an explicit whitelist — `{marshal} {enemy} {ally} {failed_ally} {relationship} {coordination_bonus} {arrival_score} {artillery} {failed_was}` — so "{n} men, Sire" would render the braces literally on screen. (3) The copy assumes a REMNANT ("the remnant of {marshal}'s corps"), but the gate it prescribes is a casualty-scale gate; the two are only coincidentally the same (a losing corps takes >=15% by `_calculate_casualties`, combat.py:1160-1170, so <1000 total does imply a loser under ~6,600 — call that "the remnant" only if you accept a 6,000-man corps being described that way). Also note `_corrected` says "before line 815, priority 2" and `fix_shape` says "before :818": J7 read these as disagreeing by a priority tier. They do not — 813-814 is priority 1 and 816 is the priority-2 comment, so both name the same slot. The slot is the problem, not the disagreement.

**Minimal fix.** In `_pick_observation`, immediately BEFORE the priority-4 pair (i.e. between :831 and :835, after the fort and stance arms), add `if we_lost and (attacker_casualties + defender_casualties) < SKIRMISH_FLOOR: return _fill(random.choice(_OBSERVATIONS["lost_skirmish"]))` with a new bank whose copy uses only whitelisted placeholders. Do not touch priorities 1-3. Cite ONE existing floor rather than inventing a third: either `diplomacy.py:9441` (`total_casualties < 1000`, the war-score gate the row names) or WO-16's `OWN_MAULED_MIN_CASUALTIES = 500` — and say in the record why the report's floor differs from the briefing's if you pick 1000. WO-16 carries a written dissent ("if 500 is tuned TWICE, take the fraction-of-national-strength form"); a second absolute constant for the same question "was this a battle?" is the consistency risk.

**Tests.** None. `tests/test_battle_report.py::test_lost_terrain_disadvantage` (:395) and `::test_enemy_attacker_wins_triggers_loss_observation` (:903) both run through `_make_result` whose defaults are atk_cas=5000/def_cas=8000 = 13,000 total, far above any floor in 500-1000. `test_lost_into_fortification` (:376) same. No test asserts the defect. No `_OBSERVATIONS` bank-count census exists that a new key would red (the counts in `test_bombardment_report.py`/`test_auto_bombardment_overwatch.py` are per-key `>= 2` assertions, not a total).

**Flags.** none


### FA-65 - REPRODUCED-BUT-NARROWER

**Mechanism.** `vassal.process_vassal_loyalty` gates the recovery hint at `vassal.py:711` — `if delta < 0 and new_loyalty >= 40:` — on the POST-delta value, so it switches off the turn loyalty first crosses 40, while `BRIBE_ELIGIBLE_LOYALTY = 35` / `BRIBE_SPIRAL_LOYALTY = 50` (:73-74) open the AI bribe window below it. The row's central claim that 35-39 is "a full dead zone ... zero hint from either producer" is REFUTED at HEAD: there are THREE producers and the third has the inverse gate — `diplomatic_ledger.py:688` attaches `recovery_hint_for_grip(grip) if loyalty < 40 else ""`. Talleyrand's advisory is `elif loyalty < 35` (`dispatch.py:3632`). So the true defect is narrower and cleaner than filed: the two PASSIVE surfaces go silent in 11-39 while the remedy survives only on a ledger tab the player must open — and the dispatch beat that DOES fire there, `diplomatic_vassal_unrest` (queued at `vassal.py:737` for `10 < loyalty < 40`), is the remedy-less "Talleyrand reports unrest in {nation}." (`dispatch.py:4014`).

**Evidence.**

Probe on the shipped 1805 boot, Switzerland: `loy 45 -> 43  hint=YES  dispatch=[]` / `loy 41 -> 39  hint=no  dispatch=['diplomatic_vassal_unrest']` / `loy 36 -> 34  hint=no  dispatch=['diplomatic_vassal_unrest']`. Message at 39: "Switzerland loyalty 39 (-2): satellite drift" — no remedy. Source at :710-712 and :735-738 read verbatim; `diplomatic_ledger.py:687-688` read verbatim.

**WARNING - what the row's own fix_shape would break.** "Drop the >= 40 clause" fires the hint on EVERY negative delta at ANY loyalty — including a satellite at 8 the same turn the CRITICAL rebellion notification and popup fire (`vassal.py:740+`) — and it duplicates the ledger row's sentence verbatim in the band the ledger already covers. It also REDS a standing pin: `tests/test_vassal_recovery_lever.py::TestVS1RecoveryHint::test_no_hint_below_healthy_band` (:107-114) asserts `e["recovery_hint"] == ""` at loyalty 30. That pin ASSERTS THE DEFECT and its docstring ("Below 40 the crisis advisories take over") encodes the false premise FA-65 attacks — Talleyrand's advisory does not start until <35. J7's alternative (raise the gate to `BRIBE_SPIRAL_LOYALTY` = 50 plus an urgent sub-40 variant) reds the same pin.

**Minimal fix.** Do not touch the `>= 40` gate at all. The two bands already partition cleanly: `>= 40` = the healthy-drift reminder, `10 < loyalty < 40` = the unrest dispatch beat. Attach the remedy to the beat that already fires in the lower band — pass `recovery_hint_for_grip(get_imperial_grip(world, lord))` into the `template_vars` at `vassal.py:737-738` and extend the template at `dispatch.py:4014` to render it. One seam, no gate change, no new producer, no duplicate sentence, and the `test_no_hint_below_healthy_band` pin stays GREEN because the per-tick event is untouched. Flag in the record that the beat already repeats every turn in-band, so the hint adds length, not frequency.

**Tests.** With the recommended fix: none. `tests/test_vassal_recovery_lever.py:105` and `:114` (both `recovery_hint == ""`) stay green; `tests/test_ui6_interaction_sweep.py:224-226` (ledger tab, `rows[50] == ""`, lower bands non-empty) untouched; `tests/test_vassal_authority_coupling.py:379/391` drive loyalty-60 vassals. With the FILED fix: `test_no_hint_below_healthy_band` reds. Grep any new pin against `dispatch.py`'s template-var rendering, not the event dict.

**Flags.** none


### FA-69 - WIDER-THAN-FILED

**Mechanism.** `CaptureExecutor._maybe_mount_estate_choice` stamps `"estate_holder": holder.name` raw at `capture_executor.py:225` and interpolates it raw at :236, in the same f-string that routes the NATION through `formed_display_name` at :244/:246. J7 counted four sites; there are SIX backend + one `.gd`. The two J7 missed are inside `_handle_estate_choice`: the confiscate outcome at :276 ("Marshal ArchdukeCharles's title is extinguished") and the respect outcome at :299 ("Marshal ArchdukeCharles's title stands") — i.e. the raw key survives the answer, not just the question. A seventh, one function over in the same blast radius, is `dotation.py:355` `check_estate_eligibility` ("{region} already sustains Marshal {claimant.name}'s household"), also an ENEMY holder. `dotation.py:697`'s sibling reads the player's own marshal, so 1805's single-word French names hide it there.

**Evidence.**

Probe on the shipped 1805 boot (Charles endowed with Bohemia, Ney takes it): mount → "Sire — Bohemia sustains Marshal ArchdukeCharles's household (the Duchy of Bohemia). Confiscate the estate (+400 gold; Austria will not forgive it)..."; `_pending_prompt` → "the fate of Marshal ArchdukeCharles's estate at Bohemia awaits your word"; confiscate → "Marshal ArchdukeCharles's title is extinguished — Austria will not forgive it."; respect → "Marshal ArchdukeCharles's title stands". `capture_choice_dialog.gd:56/60` reads `estate_holder` verbatim; :57/62/63 render `estate_holder_nation` without `Utils.display_nation_name()`.

**WARNING - what the row's own fix_shape would break.** Nothing, PROVIDED `estate_holder` stays the machine key — `_handle_estate_choice` re-reads it at `capture_executor.py:256` (`world.marshals.get(pending.get("estate_holder",""))`) and a humanised value fails that lookup and returns "The estate question has lapsed." The row's fix_shape says exactly that, so it is safe. Two real gaps in it though: it enumerates only :236 and the `.gd`, missing the two outcome sentences and `executor.py:1103`, so following it literally leaves four of seven surfaces printing the raw key; and it says nothing about pre-fix saves.

**Minimal fix.** One producer seam: in `_maybe_mount_estate_choice` add `estate_holder_display = humanize_entity_name(holder.name)` and `estate_holder_nation_display = formed_display_name(world, holder.nation)` to `estate_pending`, keeping `estate_holder` as the machine key. Then read `pending.get('estate_holder_display') or pending.get('estate_holder')` at the five backend sentences — `capture_executor.py:186, :236, :276, :299` and `executor.py:1103` — and have `capture_choice_dialog.gd:56-57` read the `_display` keys with a fallback to the raw ones plus `Utils.display_nation_name()` on the nation fallback. Sweep `dotation.py:355` in the same pass or it will read as the same bug on the endow surface. Note the two outcome sentences are built from the live `holder` object, not from `pending`, so they can call `humanize_entity_name(holder.name)` directly.

**Tests.** None found. `grep 'sustains Marshal' tests/` returns only a COMMENT at `tests/test_w6_estate_confiscation.py:241`; the assertion beside it is `holder.name in reason` against `dotation.py:355`, which stays green if that site uses the display form only when it differs — check it, it is the one pin at risk. Key-shape pins (`test_w6_estate_confiscation.py:132-133`, `test_igr_e_plunder_prompt.py:828-829`, `test_wo_slice15_capture_question_holds.py:512`) all assert `estate_holder == holder.name`, which the fix preserves; added keys are additive.

**Flags.** touches `.gd`, serialized field


### FA-93 - REPRODUCED

**Mechanism.** `TacticalExecutor._auto_break_square` builds `f"\n[Square broken — {marshal.name} breaks formation to {display}]"` at `tactical_executor.py:497` with `display = _action_display_name(action_name)` (:496), and `ACTION_DISPLAY` (`display_names.py:16-38`) is third-person present. Ten call sites feed it seven action names plus the four strategic order enums via `strategic_executor.py:525` (`strategic_type or "strategic order"`).

**Evidence.**

Probe on the 1805 boot, driving `_auto_break_square` directly: `'\n[Square broken — Ney breaks formation to attacks]'`, `'...to moves to]'`, `'...to fortifies]'`, `'...to recruits]'`, `'...to garrisons]'`, `'...to drills]'`, `'...to charges]'`, and from the strategic path `'...to MOVE TO]'`, `'...to PURSUE]'`, `'...to strategic order]'`.

**WARNING - what the row's own fix_shape would break.** The row's SECOND option — rephrase to "breaks formation and {display}" — CONTRADICTS its open sibling FA-N50, and landing both as written ships "Ney breaks formation and March". FA-N50 (OPEN, same string, same line) prescribes routing strategic types through `get_strategic_display`, and `STRATEGIC_ORDER_DISPLAY` (`display_names.py:243-248`) is `{MOVE_TO: 'March', PURSUE: 'Pursue', HOLD: 'Hold', SUPPORT: 'Support'}` — infinitive/noun forms that need the "to" frame, while ACTION_DISPLAY needs the "and" frame. Exactly one frame can survive. FA-N50's own fix_shape already assumes the "to" frame plus "the small infinitive map FA-93 already proposes", so the row's first option is the compatible one and its second is the trap. The row's FIRST option is also mildly hazardous as stated ("a tiny infinitive map beside ACTION_DISPLAY in display_names.py") — a second same-shaped map in the shared single source invites a future caller picking the wrong one; scope it to this seam or name it unambiguously. Separately: a copy-only fix is INVISIBLE on the refused arms until FA-N47 lands — `executor.py:2717` emits the notice only `if ... result.get("success")`, and every call site fires above its own validation.

**Minimal fix.** Keep the "to" frame and give the seam an infinitive on both sides, in one edit shared with FA-N50: in `_auto_break_square`, if `action_name` is one of the four strategic order types use `get_strategic_display(action_name).lower()` ("to march", "to pursue", "to hold", "to support"), otherwise look it up in a closed infinitive map covering the seven reachable action names — attack, move, fortify, drill, recruit, garrison, stance_change — with the existing `"act"` default absorbing the `"strategic order"` fallback. Consider `humanize_entity_name(marshal.name)` on the same line for the AI copy (off-screen today, live in the digests).

**Tests.** None. `grep -rn "breaks formation" tests/` and `grep -rn "Square broken" tests/` = 0 hits. No pin asserts the defect and none asserts the fixed form either, so the new pin is the only coverage — write it over all ten call-site action names, not just "attack".

**Flags.** none


### FA-95 - REPRODUCED

**Mechanism.** `DiplomaticExecutor._execute_diplomatic_propose` reads the decrementing cooldown at `diplomatic_executor.py:689-691` and prints it as elapsed time in two f-strings: `:694` ("{target_nation} rejected our last proposal only {remaining} turns ago.") and the per-type sibling `:703`. `player_proposal_cooldowns` is a `CooldownManager` slot (`world_state.py:2170-2175`) written at rejection (`diplomatic_executor.py:5555/:5557`, `turn_manager.py:184/187`) and decremented to zero, so `remaining` is turns UNTIL you may ask again. Both strings also print the raw nation key.

**Evidence.**

Source read at HEAD, :689-704 verbatim. Every other reader treats the value as remaining — `diplomatic_ledger.py:407-415` (`nation_cd`/`proposal_cooldowns`), `diplomatic_advisory.py:548,559` (`if int(cooldowns.get(nation,0)) > 0: continue`), `settlement_validation.py:431` — and the correct sibling idiom is 40 lines up the same file at `:3124-3125`: "we must wait {int(ult_cd)} more turns".

**WARNING - what the row's own fix_shape would break.** Nothing. I checked the one thing J7 flagged as unresolved: the Make Amends sibling that shares the "only N turns ago" idiom (`display_names.AMENDS_REFUSAL_DISPLAY['cooldown_active']`, :608-610) computes `turns_since = MAKE_AMENDS_COOLDOWN_TURNS - (cooldown_expiry - current_turn)` at `diplomatic_executor.py:1193-1196` and `:1585-1588` — genuinely elapsed, NOT inverted. So `tests/test_bb4_grievance.py:579` (`assert "only" in ... and "turns ago" in ...`) is pinning a correct message and does not flip, and that sibling must NOT be swept along with this one.

**Minimal fix.** Both f-strings at `:694` and `:703`, using `remaining` for what it is and pluralising: "Talleyrand advises patience, Sire. {formed_display_name(world, target_nation)} refused us; the court will not receive another envoy for {remaining} more turn{'s' if remaining != 1 else ''}." `formed_display_name` is already imported inside this same function at `:637` (for the no-target arm), which makes the raw-key half a free consistency fix rather than a new dependency.

**Tests.** None. `grep -rn "advises patience\|rejected our last proposal" tests/` = 0 hits. No pin asserts the defect.

**Flags.** none


### FA-98 - REPRODUCED

**Mechanism.** `dispatch._compose_reversal_line` (`dispatch.py:1486`) builds the crown appositive at `:1509-1513` with no tutorial awareness — `dispatch.py` contains ZERO `scenario_name` references, and so does `campaign_log.py`. `jealousy.recompute_crowns` (:529) is called unconditionally from `process_turn` at `:3428` and is correctly ungated by design (`jealousy_dormant`'s own docstring, :204-212, says glory must keep accruing so the Generals screen stays honest), so the crown state genuinely exists in the School and the arc builder narrates it with jargon the twelve-turn syllabus never introduces.

**Evidence.**

Probe: `WorldState.from_scenario(tutorial_1805.json)` → `scenario_name = 'tutorial'`, `jealousy_dormant = True`, `dotation_dormant = True`; `_compose_reversal_line(w, Ney, crown_turn=2, ..., consecutive=1)` returns "Ney, crowned four turns ago, has been beaten in the field." on BOTH the tutorial and the campaign world — byte-identical to the archived `docs/audits/playtest_digests/audit-tutorial/digest.md:55`. That digest is confirmed a real tutorial run: its header line "Your campaign autosave is untouched" is emitted only when `autosave_result['skipped'] == 'tutorial'` (`main.py:4583-4587`).

**WARNING - what the row's own fix_shape would break.** Two. (1) "the crown-fall headline producer consults jealousy_dormant before emitting" — if read as gating the whole line or the whole arc, it also silences the estate arm (`elif estate_noun:`, :1514) and the legitimate fall clause; in a tutorial world where `crown_turn` is treated as None the existing `else: rise = who` arm already produces the correct "Ney has been beaten in the field." Gate the CROWN value, not the line. (2) "optionally the same for the 'crowned' arc beats in campaign_log" is the riskier half: `campaign_log.py:1615-1619` is the campaign LOG's factual one-liner for a real, deliberately-live state that the Generals screen shows with a ★. Suppressing it makes the log disagree with the Generals screen — the exact contradiction `jealousy_dormant`'s docstring exists to prevent. Also STALE ROUTING: the row says land this behind PC15-D3. PC15-D3 was RULED AND BUILT Aug 15 2026 (`dotation.dotation_dormant`, :193-217), so the gate is closed — but it was ruled "gate the STATE, not the beats", and FA-98 is the first tutorial gate that suppresses a BEAT while leaving the state alive. That is a new shape, not a covered precedent; say so in the record rather than citing PC15-D3 as cover.

**Minimal fix.** In `_compose_reversal_line`, treat `crown_turn` as `None` when `jealousy.jealousy_dormant(world)` — one line at the head of the ascent block (before :1509). Leave `campaign_log.py:1618` alone unless the user rules otherwise, and record the reason.

**Tests.** None. `tests/test_creative_audit_ca8_2026_08_04.py:795` (`assert "three turns ago" in line`) and `:1230` (the run-on appositive pin) both build their world with `WorldFactory` (`_world` at :724, `_arc` at :1213), which sets no `scenario_name`, so `jealousy_dormant` is False and both stay green. `tests/test_tutorial_position7.py` / `test_tutorial_school_fixes_2026_08_08.py` own the dormancy family and none of them touches the dispatch arc.

**Flags.** none


### FA-100 - REPRODUCED

**Mechanism.** CHIMERA CONFIRMED, and both halves still reproduce. Half (a) — what the title, summary, repro, behaviour_test and fix_shape all describe: `save_manager.load_game` wipes three per-turn stores AFTER `from_dict` restored them, at `save_manager.py:217` (`mild_concerns_this_turn`), `:218` (`gold_spent_this_turn`) and `:240` (`threat_sources_this_turn`), inside a block whose own comment documents FIVE deliberate NON-clears citing exactly the contract these three violate. All three are serialized (`world_state.py:7131/7136/7294`, restored at `:7761/:7763/:8043`) and all three are cleared at the real boundary in `_advance_turn_internal` (`:9446/:9450/:9456` — the row's `:9253/:9257/:9263` is stale by ~193). Half (b) — what `_corrected` describes instead, and which rejects the fix_shape printed below it: a `command_clarification` survives `from_dict` and `/load` raises nothing for it.

**Evidence.**

Probe on the shipped 1805 boot after one `TurnManager.end_turn`: `live: threat_sources=4 ... ledger rows=2` / `after load: threat_sources=0 ... ledger rows=0` / `from_dict alone: threat_sources=4`. Half (b): pushing `{"type":"command_clarification"}` and round-tripping through `WorldState.from_dict(w.to_dict())` leaves `peek()['type'] == 'command_clarification'`; `/load`'s tail (`main.py:4632-4686`) attaches `pending_capture_choice`, `pending_interrupt` and `redemption_event` and nothing from the dialogue queue.

**WARNING - what the row's own fix_shape would break.** Nothing for half (a) — deleting the three lines is correct and consistent with the block's five existing non-clears, and no reader can be harmed: `threat_sources_this_turn` is APPEND-only in `coalition.py:791/819/2090` and read only by display/advisory surfaces (`diplomatic_ledger.py:996/1109`, `diplomatic_advisory.py:726`, `dispatch.py:3947`, `main.py:5905`); `gold_spent_this_turn` is read by `economy_executor.py:330` and save/restored around post-objection (`executor.py:2740`, `meta_executor.py:177`); `mild_concerns_this_turn` is a per-marshal DEDUPE list (`executor.py:2072/2088/2144`), so the wipe is not merely cosmetic — it lets a mid-turn save/load re-fire a mild concern for a marshal who already raised one, the WO-23 budget-refresh shape. The hazard is in the ROW, not the fix: `_corrected` asserts "world_state.py:7718-7725 ... is the correct seam, NOT save_manager.py:217-240", which reads as an instruction to skip half (a) entirely. It is describing half (b). Do not let the standing "read `_corrected` first" rule silence the half the row is titled for.

**Minimal fix.** Half (a): delete `save_manager.py:217`, `:218` and `:240`, and extend the block comment with the sixth/seventh/eighth entries citing the same contract (serialized under the mid-turn-save contract, restored by `from_dict`, cleared at the real boundary by `_advance_turn_internal`). Half (b): file as its own row at low severity — the shipped client cannot reach it (the clarification popup is a registered modal that disables the terminal and both pause-menu routes, manual save is blocked, autosave fires at turn start, and `DialogueManager.clear_stale` dismisses a lingering `command_clarification` at the next boundary, so the window is API-only and within one turn).

**Tests.** None, and one pin actively protects the fix. `tests/test_ai_intent_threat_migration.py:1129-1133` round-trips `threat_sources_this_turn` through `from_dict` and asserts it survives; `:1087` (`assert world.threat_sources_this_turn == []`) is a zero-amount-noop pin on a fresh world, not a load pin. `tests/test_objection_v2.py:1419-1433` pins `mild_concerns_this_turn` serialization through `from_dict`. `tests/test_audit_part2.py:124-131` builds sources directly. Nothing anywhere asserts the load-time wipe.

**Flags.** none


---

## Group: FA-N47, FA-N50, FA-N57, FA-N70, FA-N55, FA-N64, FA-N69, FA-N71

### Recommended landing order

Square family FIRST and as ONE landing: FA-N47 (it decides whether N50's string is visible at all — today the notice is destroyed on every strategic order whose first step moves, so the raw enum is only seen on the minority path) -> FA-N50 + FA-N70 sharing one display helper (and fold in the unfiled third site strategic_executor.py:2757) -> FA-N57 (independent, but same file and same mechanism). Then the parity family: FA-N64's backend half can land alone; FA-N64's renderer half + FA-N69 + FA-N71 land together behind ONE comment-stripped, source-census parity pin that forbids the class. FA-N55 is standalone and can go anywhere (one file, four `* 100` deletions). FA-N71 is the only row whose value is contingent — check with the user whether it is worth a slot before FA-D4.

### Cross-row findings

THE FOURTH SILENT KEY (J6's bonus finding): CONFIRMED as a census fact, SEVERITY REFUTED. `talleyrand_discovery` is written at dispatch.py:2324/:3743 and read by 0 .gd (comment-stripped) — but J6 calls it "a bigger loss than FA-N71's war-objectives section" and that is wrong. The SAME block (dispatch.py:3740-3800) also pushes the confrontation onto `world.dialogue_manager`, sets `world.diplomatic_sabotage_popup` at :3785 — which cooldown_manager.py:168 maps to the response key `diplomatic_sabotage`, which main.gd:2091/2654-2662 routes to `sabotage_discovery_popup.gd` — AND queues a `diplomatic_sabotage_discovered` dispatch event plus a `SABOTAGE_DISCOVERED` notification. No information is lost. Correct disposition: DELETE the unread key or allowlist it; do not build a renderer. Same for `talleyrand_redemption`, which is written ONLY as `None` at dispatch.py:2326 (PL-23 deleted the trust system) — a permanently dead key with no other writer.

THE PARITY PIN, definitively (comment-stripped, source-census, run at HEAD): the producer's own `dispatch[...] =` statements name 16 keys. MAIN-ONLY: `coalition_status`, `talleyrand_report`, `turn_limit_warning`. NO RENDERER: `talleyrand_discovery`, `talleyrand_override_note`, `talleyrand_redemption`, `war_objectives`. Everything else is rendered by both. Two traps the pin must avoid, both measured: (a) a raw substring scan over .gd is satisfied by COMMENTS — `talleyrand_redemption` looks main.gd-present until comments are stripped, and the two existing precedent pins (`tests/test_fa_slice11_the_briefing_tells_the_truth_2026_09_05.py:490-497` and `tests/test_pt_c_numbers_on_buttons.py:341`) are exactly that raw idiom; (b) a pin built off a RUNTIME boot payload sees only 13 keys and structurally cannot see `war_objectives`, `prisoners`, `peace_settlements`, `lapsed_offers` or `headline` — the very keys the row exists to catch. Census from the SOURCE (assignment keys union the initial dict literal), strip comments on the client side.

THE THIRD RAW-ENUM SITE, unfiled: `strategic_executor.py:2757` prints `_action_display_name(strategic_type)` into a HIGH-priority defiance NOTIFICATION body; `strategic_type` is the uppercase enum (stamped "PURSUE"/"MOVE_TO" at eight sites). Same class as FA-N50/FA-N70, and it is live. `strategic_executor.py:1674` (`f"...received strategic order: {strategic_type}."`) is the same shape but unreachable — all four types are branch-covered at :1597/:1605/:1615/:1626. FA-N70's own claim that combat_executor.py:7433 and strategic.py:2961 "are the only two" is wrong in both directions: the second does not exist, and a real third is unnamed.

STALE LINE NUMBERS, measured on these eight rows: FA-N47 :905->:997 and :2493->:2717 and tactical :483->:499; FA-N50 :480->:496 and :512->:525; FA-N57 :512->:525 and :1562->:1667; FA-N70 :7433->:7750; FA-N55 all four (:382->:438, :520->:576, main.gd :3074->:3306); FA-N64 :5419->:5467; FA-N69 :352->:368/:370, main.gd :3574->:3825; FA-N71 :2137->:2336 and :3611->:3817. Eight of eight carry at least one stale number.

DRIVE-BY on the exact lines FA-N69/N71/N64's renderer half will edit: main.gd:3811 and :3823 carry committed cp1252 mojibake in their banner comments (`# â•â•â• TALLEYRAND REPORT â•â•â•` — bytes `c3 a2 e2 80 a2 c2 90`, i.e. `═` round-tripped through cp1252). 12 occurrences on those 2 lines, both comments, nowhere else in the repo. Harmless functionally; fix them while you are in `_display_morning_dispatch`, and do not let a PowerShell round-trip add more.

IRONY WORTH ONE LINE: `tools/playtest_driver.py` reads `morning.get("coalition_status")` — the harness reads the key the dispatch re-read screen drops.

RISK PROFILE: none of the eight adds a serialized field (FA-N64 mutates the existing serialized `talleyrand_override_history`), none touches a mechanic, and none can move `BASELINE_SERIES` or M1-M7. Four touch `.gd` and force the Godot parse harness + boot smoke: FA-N55 (enemy_phase_dialog.gd), FA-N69 (dispatch_view.gd), FA-N71 (main.gd + dispatch_view.gd), FA-N64's renderer half (main.gd + dispatch_view.gd).

WHAT NO PIN ASSERTS: across all eight rows, zero existing tests assert the defect and zero flip. That is itself the pattern — the producer side is pinned everywhere (fort percent int, override note "good"/"bad", `_auto_break_square` sets the flag) and the consumer side is pinned nowhere, which is exactly how eight of these shipped.


### FA-N47 - WIDER-THAN-FILED

**Mechanism.** `_auto_break_square` (tactical_executor.py:461; msg built :496-499) parks the notice on the SHARED singleton field `self._executor._pending_square_break_msg`. Two consumers only: `executor.execute` CLEARS it at :997 (top of EVERY call, nested included) and EMITS at :2717 gated on `result.get("success") and result.get("message")`. So (a) every refusal drops it, and (b) — wider than filed — every strategic order whose first step actually MOVES drops it too, because the nested `execute()` wipes it at :997 before the inner action even runs. The row's arm list is right; its census of 10 call sites is right (combat_executor 4395/4759/7914, economy_executor 519/1093, movement_executor 368, strategic_executor 525, tactical_executor 187/310/636) — J6's "12" over-counted the executor.py delegate list at :135 and the comment at :996.

**Evidence.**

Refused march: `success: False / MSG: "Region 'Moscow' not found. Did you mean 'Oslo'?" / post square: False / '[Square broken' in msg: False / events: []`. Refused attack: `"No intelligence on Kutuzov's position, Sire..."`, square False, silent. ORGANIC refused drill (Mack adjacent at Swabia on the boot board): `'Soult cannot drill with enemy forces nearby! Mack is at Swabia, just one region away.'`, square False, silent — so the row's third arm DOES reproduce; J6 refuted it only because it picked `drilling_locked`, the ONE drill refusal that fires above the break via an executor-level pre-block. Refused garrison: same. WIDER, traced: `('ENTER',1,''), ('ENTER',2,"'\\n[Square broken — Soult breaks formati"), ('EXIT',2,''), ('EXIT',1,'')` — march to Rhineland and to Franche-Comte are both SILENT; march to Swabia (blocked by Mack, no nested move) shows the line. The default case is silence.

**WARNING - what the row's own fix_shape would break.** TWO breaks, one of them new. (1) J6's, confirmed: making only the CLEAR depth-aware lets the nested frame reach its own emit at :2717 with the notice set and prepend it onto `move_result["message"]` — which strategic_executor.py:1555-1573 DISCARDS, rebuilding `first_step_msg = f" Moves to {moved_regions[0]}."`. Same loss, one frame down, now looking fixed. The EMIT must be outermost-only in the same edit. (2) NEW, mine: the notice field is a singleton on the shared executor and the ENEMY AI runs NESTED inside the player's end-turn frame. Measured with Mack put in square: `max execute depth during end turn: 2` / `square breaks during end turn: [(2, 'Mack', 'Austria', 'attack')]`. Today the depth-2 clear confines it (measured: `'[Square broken' anywhere in the end-turn RESPONSE: False`). Under the row's literal fix — clear outermost-only + emit unconditional — Mack's break notice survives to the outermost frame and is prepended to the PLAYER's end-turn message: wrong-side, fog-relevant copy the enemy-phase surface deliberately never renders. That is why the notice must be keyed to a marshal, not to the executor.

**Minimal fix.** Do NOT keep a singleton string. Store `(marshal_name, msg)` on the executor; clear at depth 0 on ENTRY (never remove that clear, or the notice leaks into the next command); emit + consume ONLY at depth 0 on exit, and only when `marshal_name` equals the outermost command's own marshal; drop `result.get("success")` from the condition. Optionally append a `square_broken` entry to `result["events"]` (no such type exists anywhere in the backend today; `_DISPATCH_EVENT_TYPES` filters it out of the dispatch, so no log-type pin moves).

**Tests.** None. `grep -rn "Square broken" tests/` = 0; `_pending_square_break_msg` in tests/ = 0. `tests/test_square_formation.py:245-279` calls `_auto_break_square` in isolation and asserts only `square_formation is False` / `msg == ""` — it never enters `execute()`, so it cannot see the channel. No pin asserts the defect. Note the row's own proposed parametrised test names `drilling_locked` as the drill arm; write it on the ADJACENT-ENEMY refusal instead or the arm is green about nothing.

**Flags.** none


### FA-N50 - REPRODUCED

**Mechanism.** tactical_executor.py:496 `display = _action_display_name(action_name) if action_name else "act"`; strategic_executor.py:525 calls `_auto_break_square(marshal, strategic_type or "strategic order")` with the ORDER enum. `action_display_name` falls through to `action.replace("_"," ")` (display_names.py:1110) because `ACTION_DISPLAY` has no strategic keys. The correct map is imported on the SAME line of the same file (strategic_executor.py:24 imports `get_strategic_display` beside `action_display_name`).

**Evidence.**

Live `/command`: `'\n[Square broken — Soult breaks formation to MOVE TO]\nSoult begins march to Lorraine. ...'`. And measured directly: `MOVE_TO  action_display='MOVE TO'  strategic_display='March'` · `'MOVE_TO' in ACTION_DISPLAY: False` · `STRATEGIC_ORDER_DISPLAY: {'MOVE_TO':'March','PURSUE':'Pursue','HOLD':'Hold','SUPPORT':'Support'}`.

**WARNING - what the row's own fix_shape would break.** Nothing — but the row understates the coupling: this string is TODAY only visible on the minority path where the first step does not move (see FA-N47). Fixing N47 makes this line the normal case, so N50 must land in the same slice or the sweep makes the copy defect more prominent, not less. Separately, the row's framing that there are two sites of this class is wrong: a THIRD, unfiled, live site is `strategic_executor.py:2757` — `f"{marshal_name} defied your order to {_action_display_name(strategic_type)} and chose to {_action_display_name(defiant_action)} instead."` in a HIGH-priority notification body, where `strategic_type` is the raw enum (stamped "PURSUE"/"MOVE_TO" at 8 sites). strategic_executor.py:1674 (`f"...received strategic order: {strategic_type}."`) is the same shape but unreachable — all four types are branch-covered at :1597/:1605/:1615/:1626.

**Minimal fix.** One seam, tactical_executor.py:496: if `action_name` is a strategic order type, route it through `get_strategic_display(action_name).lower()`; otherwise the existing ACTION_DISPLAY map. `get_strategic_display` title-cases unknown keys, so the fallback is safe.

**Tests.** None. `grep -rn "MOVE TO\b" tests/*.py` = 0; no pin asserts the string.

**Flags.** none


### FA-N57 - REPRODUCED

**Mechanism.** `_execute_strategic_command` calls `_auto_break_square` at strategic_executor.py:525, which sets `square_formation = False`; the advisory `elif getattr(marshal, 'square_formation', False):` sits at :1667 — 1,142 lines later inside the SAME call, and inside the SUPPORT branch only. `square_formation` occurs exactly once in the whole file, at that dead branch. `_execute_form_square` is the only writer of True and is not on this path. The row's `:1562` and `:512` are both stale.

**Evidence.**

`Soult, form square` then `Soult, support Ney` → `advisory mentions square: False`, `square now: False`, message ends `...name a duration to hold him to it.` Control with `Soult, fortify` then `Soult, support Ney` → the sibling fires: `Berthier: "Sire, Soult is ordered to support Ney but is fortified — they cannot march to reinforce from their current position. Consider unfortifying..."`

**WARNING - what the row's own fix_shape would break.** The row says the copy 'has to change too'. It is worse than that and the build must not treat it as tense-fixing: BOTH clauses become false. The square is already gone, so 'they cannot march to reinforce' is untrue (he can) and 'Consider breaking square first' is impossible (there is nothing left to break). Capturing `was_in_square` and keeping the sentence ships a NEW lie in place of silence. It must become a consequence line — he has broken square to take the order, the anti-cavalry formation is gone.

**Minimal fix.** `was_in_square = getattr(marshal, 'square_formation', False)` immediately above :525; branch the `elif` at :1667 on the local; rewrite the body.

**Tests.** None found; no pin asserts either the presence or the absence of the advisory.

**Flags.** none


### FA-N70 - REPRODUCED

**Mechanism.** `combat_executor._execute_form_square`, line 7750 (row says :7433): `strategic_cancel_msg = f" Strategic order ({old_order.command_type}) cancelled."` — the sole hit for `"Strategic order ("` in the whole backend, appended to the message at :7765.

**Evidence.**

All three order types driven through real `/command`: `'Strategic order (MOVE_TO) cancelled.'` · `'Strategic order (HOLD) cancelled.'` · `'Strategic order (SUPPORT) cancelled.'`

**WARNING - what the row's own fix_shape would break.** Nothing at the seam itself. But the row's census is wrong in BOTH directions and would send the build chasing a ghost while missing a live one: `strategic.py:2961` does NOT exist as described (that line is inside `_execute_hold_bombardment`; the nearest raw-enum string is strategic.py:1872 `f"Unknown strategic command: {order.command_type}"`, an unreachable error path — do not chase it), and the real unnamed third site is `strategic_executor.py:2757`, a player-visible defiance NOTIFICATION body printing `_action_display_name(strategic_type)`.

**Minimal fix.** One seam, combat_executor.py:7750 — `from backend.display_names import get_strategic_display` and emit `f" His {get_strategic_display(old_order.command_type).lower()} order is cancelled."`. Share the helper with FA-N50's edit so the two do not become a third and fourth implementation of the rule.

**Tests.** None. `grep -rln "Strategic order (" tests/` returns only `test_serialization.py:446`, an unrelated comment.

**Flags.** none


### FA-N55 - REPRODUCED

**Mechanism.** Producers all emit INT percent: combat.py:1005, :1090, :1447, :1508 (FOUR sites — the row names two) `"fortification_old": int(fortification_old * 100)`, and combat_executor.py:4241 (bombardment event) / :4294 (`bombardment_result`). combat_executor.py:4265-4266 deliberately passes the RAW fraction to `generate_bombardment_report`, so the two shapes coexist by design. Consumers: main.gd:3306-3307 `int(result.get("fort_old", 0))` — correct; enemy_phase_dialog.gd:438,439 and 576,577 `int(event.get(..., 0) * 100)` — re-scaled. Both client arms are live: the battle event carries `fortification_degraded/old/new` (combat_executor.py:7248-7250) and the bombardment event carries `fort_degraded/old/new` (:4241). Every line number in the row is stale (:382→:438, :520→:576, main.gd :3074→:3306).

**Evidence.**

Executed at HEAD: `.venv/Scripts/python.exe -m pytest tests/test_bombardment.py -k fort_degradation_applies` → `1 passed`, asserting `br["fort_old"] == 20` for a defender at `defense_bonus = 0.20`. The client then renders `int(20 * 100)` = `Fort degraded: 2000% -> 1000%`.

**WARNING - what the row's own fix_shape would break.** Nothing, and the row's 'do NOT instead divide in the backend' is load-bearing — combat_executor.py:4265-4266 feeds `generate_bombardment_report` the raw fraction and a backend change would break the Berthier report. One correction: the row's named test file `tests/test_fa25_neighbourhood.py` DOES NOT EXIST, so its 'two-directional pin' has to be created, not extended.

**Minimal fix.** One file, one rule: drop the `* 100` from all four reads in `enemy_phase_dialog.gd` (:438, :439, :576, :577), matching main.gd.

**Tests.** None. The producer half is already pinned green — `tests/test_final_audit_s1.py:191-211` (`isinstance(result["fortification_old"], int)`, `== 25`, plus the log event) and `tests/test_fort_degradation.py:52` (`== 16`), `:196` (`== 12`). No pin reads the client side, so nothing asserts the defect and nothing flips.

**Flags.** touches `.gd`


### FA-N64 - REPRODUCED

**Mechanism.** Both halves. Writer: `diplomatic_executor.py:5467` (row says :5419) is the ONLY production caller of `record_override` and passes the literal `"override"`. Reader: `get_override_dispatch_note` (diplomatic_defiance.py:614) branches only on `override_result == "good"` (:632) and `== "bad"` (:637), else `return None` (:643). Second, independent break: `dispatch["talleyrand_override_note"]` (written at dispatch.py:3812) is read by 0 of 55 `.gd` files.

**Evidence.**

`history: [{'proposal_type': 'peace', 'override_result': 'override', 'turn': 1}]` / `get_override_dispatch_note: None` / substituting `'good'`: `"Talleyrand's assessment appears to have been... pessimistic. The proposal succeeded despite his warnings."` / `dispatch['talleyrand_override_note']: None`. Comment-stripped census over all 55 .gd: `talleyrand_override_note  main=False  view=False  others=[]`.

**WARNING - what the row's own fix_shape would break.** Nothing structural. One caution: `talleyrand_override_history` IS a serialized store (to_dict/from_dict pinned at tests/test_session6_diplomacy.py:713-736), so a `"pending"` value will appear in saves and in old saves' absence — tolerate it on read rather than adding a field. And the renderer half must land in the same slice or the backend fix is invisible (the row says so and is right).

**Minimal fix.** Send-time writes `"pending"`; the resolution path rewrites the latest history entry to `"good"`/`"bad"`; add the render block to both dispatch renderers. Ordering VERIFIED: `_process_proposal_in_transit` (world_state.py:10079, called from :9670 inside the turn advance) has the accept/reject outcome in hand (two `proposal_result_popup` branches), and `build_morning_dispatch` runs AFTER it (meta_executor.py:477 / executor.py:2935), so the rewrite is visible on the same dispatch. The `latest.turn >= current_turn - 1` window still passes if the rewrite leaves `turn` at the send turn.

**Tests.** None — and that is the finding. `tests/test_session6_diplomacy.py::test_good_override_note` / `::test_bad_override_note` / `::test_old_override_no_note` / `::test_history_capped_at_5` all pass `"good"`/`"bad"` DIRECTLY to `record_override`; they are exactly the vacuity the row names and they stay green in both directions. The new pin must drive the real send→resolve path (`handle_diplomatic_dialogue_response('send_override', ...)` then advance a turn), not the helper.

**Flags.** touches `.gd`


### FA-N69 - REPRODUCED

**Mechanism.** The producer writes both keys unconditionally. `main.gd:3825-3852` renders `DIPLOMATIC STATUS` from `data.get("talleyrand_report")` and `COALITION THREAT` from `data.get("coalition_status")`. `dispatch_view.gd._on_dispatch_received` reads 14 keys between :65 and :372 and neither is among them; it has no 'COALITION'/'THREAT' string at all. Both are non-empty on turn 1 of the shipped board. The row's `:352` is stale — the DIPLOMATIC EVENTS block ends at :368 and DEFEAT WARNING/BERTHIER'S NOTE run :370-383.

**Evidence.**

Comment-stripped source census over all 55 .gd at HEAD: `coalition_status  main=True  view=False  MAIN-ONLY` · `talleyrand_report  main=True  view=False  MAIN-ONLY` (`turn_limit_warning` is the third, and is the row's own intended allowlist entry). Boot payload: `talleyrand_report rows: 2` and `coalition_status: {'threat_level': 70, 'tier': 'Formed', 'active_coalition': {'name': 'Third Coalition', 'leader': 'Britain', 'posture': 'aggressive', ...}}`.

**WARNING - what the row's own fix_shape would break.** 'Two blocks COPIED from main.gd' will not compile. `dispatch_view.gd` has ZERO `add_output` calls — it accumulates a `bbcode` string and assigns `content_label.text = Utils.humanize_nation_keys_in_text(bbcode)` at :384. The blocks must be translated to `bbcode +=`. TWO hazards for the parity PIN the row asks for: (1) a raw-substring scan over .gd is satisfied by COMMENTS — `talleyrand_redemption` reads as main.gd-present until comments are stripped (all three hits are PL-23 'popup removed' comments at main.gd:259/467/5600), and the existing precedent pins (`tests/test_fa_slice11_...py:490-497`, `tests/test_pt_c_numbers_on_buttons.py:341`) are exactly that raw-substring idiom; (2) a pin built from a RUNTIME boot payload misses every conditional key — the boot dispatch carries 13 top-level keys while the producer's own `dispatch[...] =` statements name 16, and `war_objectives`/`peace_settlements`/`prisoners`/`lapsed_offers`/`headline` are all conditional. The pin must be a SOURCE census over dispatch.py (assignment keys ∪ initial dict literal), comment-stripped on the .gd side.

**Minimal fix.** One seam, `dispatch_view.gd`: insert the two blocks after the DIPLOMATIC EVENTS block (after :368, before :370), under the same gates (array non-empty; `threat_level > 0`). Zero backend change.

**Tests.** None. No pin references either key on the client side.

**Flags.** touches `.gd`


### FA-N71 - REPRODUCED-BUT-NARROWER

**Mechanism.** `dispatch["war_objectives"]` is written at dispatch.py:2336 (row says :2137) under `if war_objective_lines:`; the builder `_build_war_objective_section` is at :3817 (row says :3611). Read by 0 of 55 .gd files. Narrower than the title suggests: the section is EMPTY on the shipped board from turn 1, so today the missing renderer costs nothing.

**Evidence.**

`boot: 'war_objectives' in dispatch: False` with `boot world.war_objectives: {}` — despite SIX standing wars on the boot board (`Britain|France`, `Austria|France`, `France|Russia`, `Britain|Spain`, `Britain|Holland`, `Austria|Bavaria`). Seeded, the builder works: `[{"text": "War Purpose: Conquest vs Austria — Swabia [not held]  |  Settlement: White Peace (+0)", "target_nation": "Austria", "objective_type": "conquest"}]`. Comment-stripped .gd census: `war_objectives  main=False  view=False  NO RENDERER`.

**WARNING - what the row's own fix_shape would break.** Nothing. But confirm the row's own caveat before spending the slot: it is correct and unobservable on the boot board. The objective is created only when a PLAYER-declared war's purpose HARD STOP is answered (diplomatic_executor.py:2555) — measured, `declare war on Prussia` returns `war_purpose_popup` with the conquest option and `world.war_objectives` stays `{}` until the answer. The boot wars create none, which is FA-D4. Land it with FA-D4 or accept that it renders nothing in ordinary play.

**Minimal fix.** One block in each renderer, beside COALITION THREAT (main.gd ~:3852; dispatch_view.gd after :368), rendering the `text` field of each row. Zero backend change.

**Tests.** None on the renderer side. The `war_objectives` hits in tests/ (test_ai_intent_war_decision.py, test_common_peace_*.py, etc.) all seed or read the world store, not the dispatch key.

**Flags.** touches `.gd`


---

## Group: FA-N31, FA-N32, FA-N35, FA-N51, FA-N52, FA-N53, FA-N66, FA-N81, FA-N85, FA-N88

### Recommended landing order

Land in three groups, cheapest and least entangled first.

GROUP A — STRIKES AND CORRECTIONS, no code (do this before writing a line):
1. **FA-N31 → ALREADY-FIXED.** Strike the row and J6's bonus armistice finding with it. Cite vassal.py:1229-1231 and :1074-1097.
2. **FA-N51 → REFUTED BY EVENTS / re-homed.** FA-21 landed without it. The surviving content is FA-21's own recorded "Seam 3 DECIDED, not touched" — leave it there; do not re-open a balance gate inside a copy sweep.
3. **FA-N32 → re-price P4 back to P3** with the evidence above, so the build does not skip it on J6's narrowing.

GROUP B — THE ONE-SEAM BACKEND FIXES, in this order (each is independent, none touches `.gd`, none moves the series):
4. **FA-N53** (jealousy.py, two strings + one derived constant). Smallest, zero risk, and its pin already exists and stays green — a good first commit to prove the slice's mutation sweep.
5. **FA-N66** (main.py, one tuple entry). One line, and the A/B control is already written: `occupation_started` 0 kept vs `garrison_assault` 1 kept on the same province.
6. **FA-N85** (europe_1805.json, one integer) — bundle the `test_europe_1805_scenario.py:347` re-bless into the same commit with the reason on the line.
7. **FA-N52** (gazette.py, three keys) + the subset pin. Do the re-keys; put `glory_crown_lost` / `marshal_petition` to a stated decision on the row instead of deleting.
8. **FA-N88** (world_state.py, the `rate=None` parameter) + the sentinel join pin. Pure hygiene, but the join pin is the thing that stops the docstring lying again.
9. **FA-N81** (diplomacy.py, one post-pass over an explicit id set). Last of the backend group because it needs the enumeration above rather than a prefix, and the id set should be derived from executor.py:2436-2451 so the two lists cannot drift.

GROUP C — THE TWO THAT NEED A MEASUREMENT BEFORE A LINE IS WRITTEN:
10. **FA-N32** (the shared `combat.rout_survivors` helper across three sites). Ship behind a flip lever; run the series arm; pin the pure helper AND one forced-surround behaviour arm. This is the only row in the batch that can move `BASELINE_SERIES`.
11. **FA-N35** (the harness). Do it LAST, and measure today's delivery first: slices 0, 6 and 10 all moved when a popup rides beside its dialogue, so run one Mode-A arm that actually reaches a rebellion and read whether `diplomatic_dialogue` arrives alongside `vassal_rebellion_imminent` before choosing between "trim DISPLAY_ONLY_KEYS" and "add a DIALOGUE_TYPE_ANSWERS entry". Send WITH the payload's `dialogue_id`, against the row's own instruction.

Rationale for the split: groups A and B are nine rows that can land in one commit each with a mutation sweep and no attribution work, which keeps the slice's risk concentrated in exactly two places — the one row that touches combat state (N32) and the one that touches the instrument the whole audit is measured on (N35). That is also the reason N35 goes last: fixing the harness mid-slice would change what every later measurement in the slice sees.

### Cross-row findings

SCOPE CORRECTION FIRST: **FA-N51 and FA-N88 are not in `docs/BUG_FIXES.md` at all** — they are DESIGN rows in `docs/DESIGN_REFINEMENT.md` (lines 22 and 26). And there is no "September-2 verification verdict" for any of my ten rows: the FA-N family IS the September-2 verification pass's own findings (FA-N2..FA-N89), so they are absent from `docs/audits/final_audit_2026_09_01_findings.json`, which holds only FA-1..FA-102. Nobody has adversarially attacked these ten; this pass is the first.

WHAT CHANGED SINCE THE J6/J7 REPORTS (master a1ed5c9d → 3e43d89b):
* **FA-N31 is dead** — slice 11's review round fixed BOTH the filed defect and J6's separately-filed bonus armistice double-emit. Two of J6's rows collapse into one strike.
* **FA-N32 is the opposite: J6's narrowing is wrong and the row is a live net-gain bug.** J6 detected the shatter arm by looking for `marshal_broken` in the RETURNED events list; that type is written by `self.log_event`, so their detector could not see the arm fire. Forcing the surround the arm exists for gives `pre 900 → post 1000` at four consecutive seeds. J6's re-pricing to "P4 hygiene, not a P3 player-facing bug" should be reverted to P3.
* **FA-N51 is refuted by events** — FA-21 landed on September 6 without its "precondition".
* **FA-N52 shrinks 6 keys → 5** (FA-N74 took `vassal_rebellion` in slice 11).
* **FA-N66's critique of FA-23 is moot** — FA-23 shipped the filter-side fix this row recommends, just scoped to two garrison types, so FA-N66 is now a one-line tuple extension rather than a design correction.
* **FA-N35's fix_shape was inverted by slice 0.** The row's emphatic "post WITHOUT a `dialogue_id`" is the exact opposite of what the client now does.

THE PATTERN WORTH CARRYING INTO SLICE 16: four of these ten rows (N31, N51, N52, N66) were partly or wholly resolved by a LATER slice that never touched the row, and two more (N35, N32) have fix advice that a later slice made wrong. Every row in this batch was written before slices 0/11/14 landed. **Read the row, then read `git log` on the file, then reproduce — in that order.**

THREE FIX SHAPES WOULD SHIP A REGRESSION IF FOLLOWED LITERALLY:
1. **FA-N35** — posting without a `dialogue_id` now exercises the FA-N5 stale-dialogue rejection path, which FA-10/FA-74 then blacklist, so the surface stays unanswered and the run still looks green.
2. **FA-N81** — a `propose_*` prefix rule falsely disables `propose_white_peace` and `open_settlement`, which route around the IN_TRANSIT gate (executor.py:2457/2463) and genuinely work; eight of the fourteen enabled rows are honestly enabled.
3. **FA-N52** — deleting `glory_crown_lost` on the stated premise that it "has no producer of any kind" is false (jealousy.py:570, with a dispatch severity arm at dispatch.py:2961) and forecloses the better fix.

TWO PINS TO HANDLE EXPLICITLY:
* `tests/test_europe_1805_scenario.py:347` **asserts the FA-N85 defect** (`coalition_count == 1`) and must be re-blessed to 3 in the same commit.
* `tests/test_systems_v3_session5.py:466 test_pursuit_floor_zero_not_thousand` looks like FA-N32's guard and is VACUOUS — it asserts on a local `max(0, 500-5000)` and executes zero production lines. It would stay green with both defective sites deleted.

ATTRIBUTION / BLAST RADIUS:
* Only **FA-N32** can move `BASELINE_SERIES` (it changes a marshal's post-rout strength, which the AI reads). Ship it behind a flip lever and run the arm; the harness may never reach the surround, in which case say so as a fact about the harness rather than as evidence of safety.
* **FA-N51** would move the series if ever built (bilateral acceptance), which is why FA-21 decided it instead.
* The other eight are series-inert: N31 already landed, N35 is `tools/`, N52/N53/N66/N81/N88 are display or read-only paths, N85 is a naming constant with no AI reader.
* **Zero `.gd` files** and **zero new serialized fields** across all ten. N85 changes an authored scenario value that loads into the already-serialized `coalition_count` — pre-change saves keep 1, so state the save-compat limit rather than claiming saves are fixed.

COUNT DRIFT J6 DID NOT SEE: `assert len(CAMPAIGN_LOG_TYPES) == 161` is now pinned in **eleven** files, not nine (FA-R5 added `garrison_assault`; slice 14d and slice 11 added their own copies). Only relevant if slice 16 adds a log type; the FA-N52 collector-set fix touches none of them.


### FA-N31 - ALREADY-FIXED

**Mechanism.** `vassal.check_vassal_rebellion`'s CRITICAL notification block — now at backend/game_logic/vassal.py:1229-1241, NOT the row's :988-999 — was lord-gated by the slice-11 review round: `if (not THE_BREAK_IS_BRIEFED_TRUTHFULLY or lord == str(getattr(world, "player_nation", "") or "")):` at :1230-1231, with a comment naming this exact defect. J6's separately-filed BONUS defect (the armistice arm falling through to the WAR tail and emitting BOTH `vassal_rebellion_armistice` and `vassal_rebellion`) was fixed in the same slice: the ARMISTICE branch at vassal.py:1074-1097 now calls `complete_vassal_break` and `continue`s.

**Evidence.**

Probe (1805 boot, three arms). ARM A, Switzerland transferred to Austria then loyalty 0: `ARM A events: [(None, None), (None, None), ('vassal_rebellion', 'Austria')]` and the only notifications are two `alliance_cascade_war` rows — **no `vassal_rebellion` notification on the French rail**. ARM C control, Switzerland left under France: `ARM C NOTIF: vassal_rebellion | Switzerland REBELLED! | Switzerland has rebelled against France! War declared.` ARM B, France-lorded under ARMISTICE: `events: ['vassal_rebellion_armistice']` and exactly ONE notification, `Switzerland breaks free … The armistice holds — no war is declared.` — one event, one notice, no contradiction.

**WARNING - what the row's own fix_shape would break.** Following it literally would ADD A SECOND, redundant guard around a block that already has one (the filed line numbers :988-999 now land inside the granted_regions/WAR-cascade body, ~240 lines above the real block) — i.e. a builder navigating by LINE rather than by symbol would wrap the wrong code. The row also says to 'deliberately NOT silence' the events.append and queue_dispatch_event, which is still correct advice and is what shipped.

**Minimal fix.** None. Strike the row as ALREADY-FIXED by the slice-11 review round, and strike J6's bonus finding with it. Do not re-file: the guard is present with its reason and the arms are pinned by the slice-11 tests.

**Tests.** None. `tests/test_session8c_popups_notifications.py:79-86` only asserts the CONSTANT strings (`VASSAL_REBELLION == "vassal_rebellion"`); `tests/test_audit_part2.py` imports it for priority ordering. Neither asserts the defect. No pin asserts the defect today.

**Flags.** none


### FA-N32 - WIDER-THAN-FILED

**Mechanism.** `WorldState._process_reckless_cavalry_turn_start`'s two 'Surrounded — broken army' arms still read the unclamped `max(1000, int(x * survival_rate))` — at world_state.py:12688 (defender) and :12730 (attacker), NOT the row's :12429/:12471 — while the maintained sibling `combat_executor.py:3841` reads `survivors = min(old_strength, max(1000, int(old_strength * survival_rate)))` with a comment naming this exact case. **J6's narrowing ('the branch was NOT reachable in 62 staged charges') is WRONG and I can show the arm firing.** J6 detected the arm by looking for a `marshal_broken` entry in the returned `events` list — but that type is written by `self.log_event`, not appended to `events`, so their detector was structurally blind.

**Evidence.**

Probe over the auto-charge path with `get_safe_retreat_destination` forced to None (the surround the arm exists for), printing the defender's post-battle strength directly: `(1200, 900, 0, 1000, True, '')` — attacker 1,200, defender **pre 900 → post 1000**, `broken=True`. Same at seeds 1,2,3 and at `(1200, 2500, …)`. A 900-man corps ends its rout with 1,000 men: **net +100**. Separately, the necessary pre-state is common at the combat level, not rare: 240 direct `resolve_battle` calls left the defender alive in the 1..999 band with `forced_retreat=True` in **90 of 240**.

**WARNING - what the row's own fix_shape would break.** Nothing in the fix itself. The hazard is in the row's TEST: 'assert `defender.strength <= 800` over the seed range that reaches the shatter arm'. On the shipped board a surrounded 800-man defender is normally annihilated to 0 first, and the arm is only reachable when `get_safe_retreat_destination` returns falsy — which no staged fixture produces without help. Pin the pure helper directly, plus ONE behaviour arm that forces the surround (monkeypatch `get_safe_retreat_destination` to None, defender 900, attacker 1200) and asserts post <= pre. J6's own advice to 'pin the pure helper instead' stands; my correction is that the behaviour arm IS writable once you force the surround, so do not skip it.

**Minimal fix.** Exactly the row's fix_shape, and it is safe: extract `combat.rout_survivors(old_strength, rate) -> min(old_strength, max(1000, int(old_strength * rate)))` and call it from combat_executor.py:3841 and world_state.py:12688 / :12730. A function-level import is the established idiom in that block (there is already one ~120 lines above for REGION_FORTIFICATION_DEFENSE_BONUS). Design note to record rather than fix: the clamp means a sub-1000 corps routs with ZERO losses (min(900, 1000) = 900); that is the maintained sibling's behaviour, so the fix makes the three sites consistent — it does not make the arithmetic right.

**Tests.** None flip. `tests/test_systems_v3_session5.py:466 test_pit_pursuit_floor_zero_not_thousand` looks like a pin on this class and is VACUOUS — it computes `max(0, 500-5000)` on a local variable inside the test and executes zero production lines; it would stay green with both sites deleted. `tests/test_creative_audit_ca8_2026_08_04.py:279` mentions 'the rare no-retreat-route SHATTERED branch' in a docstring only. No pin asserts the defect.

**Flags.** **could move an AI decision / BASELINE_SERIES**


### FA-N35 - REPRODUCED

**Mechanism.** `DISPLAY_ONLY_KEYS` at tools/playtest_driver.py:216-224 still contains `diplomatic_sabotage`, `vassal_rebellion_imminent` and `commitment_paradox_popup`; `Answerer.scan` (:1141-1145) logs them with the literal `'display-only'` and posts nothing. `DIALOGUE_TYPE_ANSWERS` (:193-212) has no entry for any of the three, so even when the dialogue DOES arrive under `diplomatic_dialogue` the keyword-less payload has nothing to answer with.

**Evidence.**

`grep -n 'DISPLAY_ONLY_KEYS' -A 9 tools/playtest_driver.py` → the three keys, unchanged. Across the committed digests: 11 occurrences of `vassal_rebellion_imminent`, 9 of them `→ display-only`, and exactly two answered — both the same run mirrored (`1b-tyrant-historical-r1/digest.md:433` and `weird-tyrant/digest.md:433`), and both via `POPUP diplomatic_dialogue: vassal_rebellion_imminent → accept_vassal_rebellion`. `grep -rl 'commitment_paradox' docs/audits/playtest_digests/` → 0 files. A fresh 18-turn Mode-A run from `fixture_t20_ambient` reached no rebellion, so the archived digests remain the evidence.

**WARNING - what the row's own fix_shape would break.** **The row's fix_shape is now WRONG on its most emphatic clause.** It says to post 'critically, WITHOUT a `dialogue_id`, so the harness reproduces the client's real wire shape rather than a safer one.' Slice 0 (FA-N5/FA-N37) inverted that: all four client sites now SEND the id — `main.gd:5616` `api_client.send_dialogue_response(action, _on_command_result, int(data.get("dialogue_id", -1)))` for the rebellion popup, and :5630/:5633 for the paradox's bare option indices, each with a comment saying why. Building it as filed would make the harness reproduce a shape the client no longer uses, and would exercise the FA-N5 delivery gate's REJECTION path (`stale_dialogue`) as the normal case — which FA-10/FA-74 then blacklist, so the surface stays unanswered anyway and the run looks green. Also: verify on today's delivery before writing pins — slices 0, 6 (`_result_carries_question`) and 10 (`_attach_modal_for_the_carried_question`, main.py:429-455) all moved when a popup rides beside its dialogue, so the 'arrives only via its PopupQueue key' premise needs one measured turn, not a re-read of the 2026-09-04 digests.

**Minimal fix.** Two edits, not one: (a) remove the three keys from `DISPLAY_ONLY_KEYS`; (b) give each a `DIALOGUE_TYPE_ANSWERS` entry with a stated policy key, so `_pick_dialogue_choice`'s keyword-less fallback can answer a payload that ships no `options` list. Post through the EXISTING answerable arm at :1379-1392, which already sends `body['dialogue_id'] = did` when the payload carries one — and the payload does: `vassal.py:812` now stamps `rebellion_popup['dialogue_id'] = rebellion_dialogue.get('dialogue_id')` (slice 0's FA-N5), and `dialogue_manager._assign_dialogue_id` (:241-246) copies the id into the payload for every push.

**Tests.** None. `tests/test_playtest_driver_instrument.py:101` merely treats the literal `'display-only'` as a non-answer when counting; it does not assert the three keys belong to that set. No pin asserts the defect.

**Flags.** none


### FA-N51 - REPRODUCED-BUT-NARROWER

**Mechanism.** The mechanism survives: `DEMAND_VALUES['gold_lump'] = -3/100` (diplomacy.py:312) enters `deal_balance = sweetener_total + demand_total` (:7307) and the score (:7499) linear, purse-blind and UNCLAMPED, while the settlement path caps its equivalent at `-min(45, …)` (diplomatic_templates.py:4497-4498). **But the row's own framing — 'FA-21 needs a second half before it can land' — is REFUTED BY EVENTS: FA-21 LANDED on September 6 without touching the acceptance term** (slice 14 part 2b), by pricing BOTH the builder and `_reduce_p8_demands`'s two floors off `_p8_purse_floor`. The 200g fallback the row is about is gone: ai_diplomacy.py:1017-1029 now delivers `max(200, min(purse_floor, original_lump))`.

**Evidence.**

Probe on `fixture_t20_ambient`: `DEMAND_VALUES[gold_lump] = -0.03`, and `calculate_acceptance` returns `deal_balance` of exactly −6.0 / −8.1 / −12.2 / −30.0 / −60.0 / −78.7 / −90.0 / −187.0 for lumps of 200 / 270 / 405 / 1000 / 2000 / 2623 / 3000 / 6233 — a perfectly linear −0.03·x with no ceiling anywhere. Against that, `diplomatic_templates.py:4498` reads `term_harshness_penalty = -min(45, round((min(raw_total_harshness, 1.5) / 1.5) * 45))`. FA-21's landing record already names this as **'Seam 3 DECIDED, not touched'**, with the cost stated (a real indemnity is a demand the player may REFUSE) and the observation that it 'is pinned by nothing (a 5× softening leaves 2,032/2,032 green)'.

**WARNING - what the row's own fix_shape would break.** Following it literally would BLOCK slice 16 on a precondition that no longer exists ('FA-21 needs a second half before it can land'), and its proposed test — 'after `_reduce_p8_demands` the surviving gold_lump is >= 0.15 × France's treasury AND `_force_send` is falsy' — is now partly SATISFIED and partly unsatisfiable: FA-21 made the fallback purse-scaled but deliberately kept `_force_send = True` on that arm, and its landing record states explicitly that 'the LOW end stays purse-blind, so the row's proposed negative control is unsatisfiable'. Writing the test as filed reds a consciously-shipped behaviour.

**Minimal fix.** None as a defect row. Re-file or strike: the only live content is a DESIGN question already answered on FA-21's row — should the bilateral acceptance formula's gold term mirror the settlement path's −45 ceiling? Building it is a balance change to every bilateral gold demand on both boards and needs a gate, not a slice-16 copy fix. If the build wants anything here, the cheap honest deliverable is the pin FA-21's record says is missing: a monotonicity/cap pin on `deal_balance`'s gold term so the asymmetry cannot drift further unobserved.

**Tests.** Capping the gold term would move `tests/test_econ_war_coupling.py` (FA-21's own exact-amount pins, 7 `calculate_state_charges` sites aside) and the bilateral acceptance families broadly — this is the reason it was DECIDED rather than built. No pin asserts the defect; that is the row's one surviving true claim.

**Flags.** **could move an AI decision / BASELINE_SERIES**


### FA-N52 - REPRODUCED-BUT-NARROWER

**Mechanism.** `gazette.compose_issue` filters only `filter_campaign_log(...)` output, and `campaign_log.py` drops any type outside `CAMPAIGN_LOG_TYPES`, so a collector key that is not a log type is dead by construction. The collectors are at gazette.py:31-55 (`_WAR_TYPES` / `_COURT_TYPES` / `_ARMY_TYPES`). **FIVE dead keys, not six**: `vassal_rebellion` was already retired by FA-N74 in slice 11 and replaced with the live `vassal_broke_free` (the comment at gazette.py:44-49 says so, and flags `vassal_created` as knowingly left alone).

**Evidence.**

Probe: `collector keys: 31` / `NOT in CAMPAIGN_LOG_TYPES: ['coalition_formed', 'glory_crown_lost', 'incoming_ultimatum', 'marshal_petition', 'vassal_created']`. J6's correction holds and is confirmed: `glory_crown_lost` DOES have a producer — `jealousy.py:570` writes `"type": "glory_crown_lost"` and it is listed in `dispatch.py:2961` with a `warning` severity arm — it is simply never written to the campaign log. Same shape for `incoming_ultimatum` (ai_diplomacy/dialogue_manager) and `marshal_petition` (jealousy/cooldown_manager). All four replacement types exist WITH `format_event_oneliner` arms: `coalition_declared` (campaign_log.py:166, arm at :2298), `ultimatum_issued` (:194), `vassal_transferred` (:173, arm at :2335), `vassal_defected` (:174).

**WARNING - what the row's own fix_shape would break.** Two. (1) The row instructs 'delete `glory_crown_lost`/`marshal_petition`, which have no producer of any kind' — that premise is FALSE for both, and deleting forecloses the better fix. (2) The row still lists `vassal_rebellion` as one of the six; it is not in the collectors any more, so a builder editing by the row's list will not find it and may 'restore' a type FA-N74 deliberately retired.

**Minimal fix.** ONE seam, gazette.py:31-55: `coalition_formed` → `coalition_declared`; `incoming_ultimatum` → `ultimatum_issued` + `ai_ultimatum_accepted`; `vassal_created` → `vassal_transferred`. Then a structural pin that the union of the three collector sets is a SUBSET of `CAMPAIGN_LOG_TYPES`, which forbids the class recurring. Decide `glory_crown_lost` and `marshal_petition` consciously (the crown changing heads is gazette-worthy and already has a producer and a dispatch severity arm — the better fix is to log it, not to delete the key), and say so on the row rather than deleting on the row's false premise.

**Tests.** None for the collector-set-only fix. **Attribution warning, and the count has MOVED since J6:** `assert len(CAMPAIGN_LOG_TYPES) == 161` (was 160) is now pinned in **ELEVEN** files — test_bph_a_term_ownership.py:303, test_ca9_row3_a7_jealousy_note.py:456, test_ca9_row3_phase_a.py:154, test_ca9_row3_q2_council_command.py:433, test_campaign_log.py:138, test_fa_slice11_the_briefing_tells_the_truth_2026_09_05.py:238, test_fa_slice14d_the_door_and_the_fallen_lord_2026_09_06.py:408, test_igr_a_honest_copy.py:197, test_igr_b_campaign_log_readable.py:546, test_igr_f_envoy_digest.py:824, test_wo_slice4_the_capital_speaks.py:785. If the builder instead ADDS a log type (e.g. to make `glory_crown_lost` live), all eleven must be re-blessed in the same commit. No pin asserts the defect.

**Flags.** none


### FA-N53 - REPRODUCED

**Mechanism.** `FONTAINEBLEAU_PROMISE_GRACE = 3` (jealousy.py:118) is printed verbatim by the option `detail` at :2236 and the confirmation at :2995, but the MECHANIC at :2991-2992 writes `marshal.expectation_grace_turn = int(world.current_turn) + FONTAINEBLEAU_PROMISE_GRACE` and erosion only resumes at `current_turn - grace_start >= dotation.GRACE_TURNS` (=4) — a 7-turn total. `dotation.build_unmet_marshals` (dotation.py:1018-1019) computes `max(0, GRACE_TURNS - (current_turn - grace_start))` = 4 − (−3) = 7, and `dispatch_view.gd:166` renders it as ' — patience holds 7 more turns'.

**Evidence.**

Probe on the 1805 board at turn 20, real petition via `queue_fontainebleau_petition` with three genuinely eroding French marshals, then `_apply_fontainebleau_choice(w, 'promise', …)`: `OPTION detail: Their patience extends 3 turns…` / `CONFIRM: "The next conquest is yours." Their patience extends 3 turns…` / `expectation_grace_turn now: 23 (current_turn 20)` / `UNMET row: Ney grace_turns_left 7 eroding False` / `erosion resumes at turn 27 => the promise bought 7 turns`. Two surfaces contradict on the same turn and the one saying 7 is right.

**WARNING - what the row's own fix_shape would break.** Nothing — the row is explicitly right to leave the mechanic alone, and that instruction is load-bearing. Changing :2991 instead would (a) red the mechanic pin below and (b) move a balance number, since the dispatch and the erosion tick already agree on 7.

**Minimal fix.** Exactly J6's: add `FONTAINEBLEAU_PROMISE_WINDOW = dotation.GRACE_TURNS + FONTAINEBLEAU_PROMISE_GRACE` beside the constant at jealousy.py:118 (or a one-line helper if the import ordering is awkward) and use it in the TWO strings only — :2236 and :2995. Leave the mechanic at :2991-2992 alone.

**Tests.** None. `tests/test_estate_riders_esp.py:135-136` asserts `m.expectation_grace_turn == world.current_turn + J.FONTAINEBLEAU_PROMISE_GRACE` — it pins the MECHANIC and stays green under the copy-only fix. It is also the pin that reds if anyone 'fixes' the mechanic instead, which is the useful signal. No pin asserts the defect.

**Flags.** none


### FA-N66 - REPRODUCED-BUT-NARROWER

**Mechanism.** `_filter_enemy_phase_by_visibility` (backend/main.py:2102) has exactly TWO own-soil carve-outs: the PT-E5 `captured_from == player_nation` test at :2199, and — new since the row was filed — FA-23's slice-11 arm at :2217-2229, which is precisely the region-ownership predicate this row asked for but is scoped to `("garrison_assault", "garrison_destroyed")` only. `occupation_started` is in neither, so an enemy beginning a siege on a French province at PARTIAL is dropped and the court reads as 'beyond our sight'. Both producers still emit a `region` key and no ownership key: combat_executor.py:3164-3168 (post-garrison) and :5336-5340 (the unopposed march inside `_execute_attack`).

**Evidence.**

A/B on the shipped 1805 boot, same French province (`Berry`, controller France, PARTIAL), same synthetic enemy action, only the event type changed: `occupation_started -> actions kept: 0` vs `garrison_assault -> actions kept: 1`. One line of code separates them.

**WARNING - what the row's own fix_shape would break.** The row's critique of FA-23 is now MOOT and would mislead: it says 'do not stamp ownership producer-side (FA-23 proposes that, and it reaches only one of the two producers)'. FA-23 actually SHIPPED a filter-side fix in slice 11, so a builder reading FA-N66 as a correction-to-FA-23 will go looking for a producer stamp that was never written. The remaining risk in the row's own shape is the opposite one: a named `OWN_SOIL_EVENT_TYPES` set that ships WITHOUT the region-ownership half would leak — the row does flag this ('note the region-ownership half is required') and it is still true.

**Minimal fix.** One-line extension of the arm that already exists: add `"occupation_started"` to the type tuple at main.py:2222-2223. Its region-ownership test (`evt.get("region") or evt.get("defender_location")` → `region.controller == player_nation`) is already exactly right for this event, and the region genuinely IS still the player's at the moment the event fires (the occupation has not completed), so the predicate has a live truth to read. If the build prefers the row's shared `_event_is_on_player_soil` helper, extract it from the FA-23 arm rather than adding a third block.

**Tests.** None. No test asserts `occupation_started` behaviour in the fog filter — every hit (`test_supply_movement_contested.py:534/551/572`, `test_fa_slice14_…:316/334`, `test_fa_slice4r_…:559-562`, `test_counter_punch_ap_gate.py:268`) is on the CAPTURE result's boolean, not on the enemy-phase filter. No pin asserts the defect.

**Flags.** none


### FA-N81 - REPRODUCED-BUT-NARROWER

**Mechanism.** `diplomacy.get_available_diplomatic_actions` computes `tal_state` once (diplomacy.py:10974) and reads it in exactly one place, `_mission_action`'s opener at :10989. The gate that actually refuses is inside `DiplomaticExecutor._execute_diplomatic` at diplomatic_executor.py:139 — `if talleyrand_state == "IN_TRANSIT" and action != "diplomatic_feasibility": return {success: False, …}` — sited before the dispatch table at :156+. So every wizard chip whose action reaches `_execute_diplomatic` is drawn enabled and refused on click.

**Evidence.**

Probe, 1805 boot, `world.talleyrand_state = 'IN_TRANSIT'`, target Prussia: `propose_open_borders available=True`, `declare_war available=True`, `send_ultimatum available=True`, while all four `mission_*` rows read `available=False reason=Talleyrand in transit`. Swept over all 20 courts with a 90,000g treasury, the rows shown available in transit are: `declare_war`, `send_ultimatum`, `downgrade`, `propose_armistice`, `propose_open_borders`, `propose_vassal`, `propose_white_peace`, `open_settlement`, `release_vassal`, `increase_autonomy`, `decrease_autonomy`, `sponsor_design`, `buy_off_design`, `guarantee_nation`.

**WARNING - what the row's own fix_shape would break.** **A prefix rule is the trap, and the row's fix_shape reaches for one ('the `propose_*` f…').** Of the fourteen rows shown available, EIGHT are honestly available because they route around `_execute_diplomatic` entirely: `sponsor_design` / `buy_off_design` / `guarantee_nation` dispatch at executor.py:2481+ (D5 instruments), `release_vassal` / `increase_autonomy` / `decrease_autonomy` at :2468+ (vassal executor), and — the sharp one — **`propose_white_peace` (executor.py:2463) and `open_settlement` / `propose_common_peace` (:2457) are `propose_`-prefixed settlement verbs that DO work in transit.** Disabling by prefix ships a false refusal on the two rows a beaten France most needs. Also do not blanket `diplomatic_feasibility` or the advisory rows the gate exempts.

**Minimal fix.** ONE post-pass immediately before `return actions` (diplomacy.py, end of `get_available_diplomatic_actions`) that, when `tal_state == "IN_TRANSIT"`, sets `available=False` / `disabled_reason="Talleyrand in transit"` on an EXPLICIT id set — and the set must be derived from the executor tuple at executor.py:2436-2451 minus `diplomatic_feasibility`, i.e. the eleven `propose_*` rows (which map to `diplomatic_proposal`), `declare_war`, `send_ultimatum`, `break_treaty`, `downgrade`, and any advisory chip mapping to `diplomatic_advisory`. Best shape: a named module constant beside the gate so the two lists cannot drift.

**Tests.** None. `tests/test_da2_player_feedback.py` has no `IN_TRANSIT` assertion at all, and none of the seven test files that mention `IN_TRANSIT` touch `get_available_diplomatic_actions`. No pin asserts the defect. The function is read only by `diplomatic_ledger.py:704` — a player-facing surface, no AI caller — so nothing in the series can move.

**Flags.** none


### FA-N85 - REPRODUCED

**Mechanism.** `godot-client/project-sovereign/assets/maps/europe_1805.json:69` authors `"coalition_count": 1` three lines above `"name": "Third Coalition"` at :72, inside the same authored `active_coalition` block. `world_state.py:8049` loads it; the only production consumer is `coalition.form_coalition` at :1549-1556 (`world.coalition_count += 1`; `_ORDINALS.get(...)`; `if world.coalition_count == 1: name = f"The {leader} Coalition" else: …`), so the NEXT coalition is minted as the Second.

**Evidence.**

Probe on the 1805 boot: `boot coalition_count: 1` / `boot active_coalition name: Third Coalition`; then `dissolve_coalition(w,'test')`, `coalition_cooldown = 0`, `form_coalition(['Austria','Britain','Russia'], w)` → `after re-form: count = 2 name = The Second Austria Coalition`.

**WARNING - what the row's own fix_shape would break.** Nothing wrong with the fix. The row's own claim that 'BASELINE_SERIES and M1-M7 are untouched by const…' should be VERIFIED not assumed: `coalition_count` is read by `form_coalition` only for NAMING, and the name is not read by any AI predicate I could find — so it should hold, but it is a one-line flip-arm check, not a free assertion.

**Minimal fix.** ONE authored value: `"coalition_count": 3` at europe_1805.json:69, so `coalition.py:1552` resolves `_ORDINALS[4] == "Fourth"`. No code change; the field is scenario-scoped and the legacy 19-region world authors no `active_coalition` and keeps 0, so N1 holds. Save-compat note the row does not make: `coalition_count` is serialized, so campaigns saved before the change keep 1 and will still mint 'The Second' — acceptable, but say so rather than claiming saves are fixed.

**Tests.** **One pin asserts the defect and must be re-blessed in the same commit:** `tests/test_europe_1805_scenario.py:347` — `assert world1805.coalition_count == 1`, in `test_third_coalition_seeded`. Three other files set `world.coalition_count = 1` by hand as local fixtures and stay green (test_da2_player_feedback.py:468, test_session7_coalition.py:319 and :745, test_systems_audit_session5.py:349).

**Flags.** none


### FA-N88 - REPRODUCED

**Mechanism.** `WorldState.calculate_state_charges` — at world_state.py:5577, NOT the row's :5434 — carries the docstring 'the SINGLE source for the income phase, the treasury report and the ledger (shown = applied)' at :5586-5588, and has ZERO production callers. `calculate_turn_income` re-derives the identical arithmetic inline at :5764-5770 (`_chest = int(self.nation_gold.get(nation, 0)) - CHARGES_HOARD_FLOOR`; `state_charges = int(_chest * charges_rate["rate"] // WAR_EFFORT_DIVISOR)`), and both downstream readers — `economy_executor.py:142` and `ledger.py:309` — take `income_data.get("state_charges")`, i.e. the inline copy's output. The documented single source is documentation only.

**Evidence.**

AST census over every `.py` under backend/, tests/ and tools/, matching `ast.Call` on `func.attr`/`func.id`: `tests 12 calls in 3 files` (test_econ_balance_eb.py ×4, test_econ_war_coupling.py ×7, test_tutorial_scenario.py ×1) and `backend: 0 CALLERS`. `grep -n CHARGES_HOARD_FLOOR backend/models/world_state.py` returns the helper at :5593 and the inline copy at :5767 and nothing else.

**WARNING - what the row's own fix_shape would break.** Nothing, given the `rate=None` default: the 12 existing test call sites pass only `nation` and stay byte-identical. The one thing to keep is the default — dropping it and making `rate` positional reds all twelve.

**Minimal fix.** Exactly the row's fix_shape, and I verified the one thing that could have broken it: give `calculate_state_charges` an optional `rate=None` defaulting to `self.get_state_charges_rate(nation)["rate"]`, and have the income path call `self.calculate_state_charges(nation, rate=charges_rate["rate"])`. The rate is passed in, so the G4 'never walk the nation's regions twice' note the inline copy exists to honour is preserved. The two Europe guards are the SAME predicate — the helper's `getattr(self, "sovereign_map", "legacy") != "europe"` at :5591 and the caller's `europe = getattr(self, "sovereign_map", "legacy") == "europe"` at :5618 — so folding them is byte-neutral.

**Tests.** None flip, but all twelve currently pin the DEAD copy — that is the row's real content. Add the join pin the row proposes: monkeypatch `WorldState.calculate_state_charges` to a sentinel and assert `calculate_turn_income(nation)['state_charges']`, `process_income_phase(nation)['state_charges']` and the applied treasury delta all carry it, so the applied number is PRODUCED BY the documented source rather than merely equal to it. That pin fails today.

**Flags.** none


---

## Group: FA-70, FA-82, FA-94, FA-81, FA-101, FA-63, FA-9

### Recommended landing order

Land as three landings, not seven rows.

1. THE `.gd` SLICE — FA-70, then FA-82, then FA-94, in that order (ascending risk), one boot smoke and one parse harness for all three at the end.
   • FA-70 first: two lines moved, zero behavioural reach, and it warms the harness loop.
   • FA-82 second: one line, but it must land in `_launch` (:471), not `_on_tutorial_pressed`, and the new pin must be scoped to `_launch`'s body or it cannot catch the wrong-function version.
   • FA-94 last and largest: default `esc_control()` returns null; press the BUTTON HANDLER, never `close_popup()`; wire only `proclamation_popup` and `mailbox_panel`; leave `battle_diorama` (it overrides `_unhandled_input` already) and the three forced-choice modals alone.

2. THE DOCS PAIR — FA-81 + FA-101 together, both docs-only, no code, no pins flipped. Take FA-101's docs arm ONLY (never the parenthetical attach). While in FA-81, strengthen `test_prebuild_fixes_2026_08_14.py:241` in place to derive the roster from `europe_1805.json` rather than adding a pin beside a vacuous one.

3. FA-63 + FA-9 LAST, together, because they share the tutorial board and the same measurement instrument.
   • FA-63 is the cheap half: rewrite `tutorial_1805.json`'s `_comment` (line 2) and `TUTORIAL_SCRIPT.md:350-351`, correct the stale comment at `tests/test_tutorial_scenario.py:100-101`, add the missing first-contact-turn pin. Do NOT attempt either mechanical option — one is measured inert, the other buys one turn.
   • FA-9 is the only row here that needs a flip lever and a `BASELINE_SERIES` arm. Build ONLY half (i) — extend `_corps_is_limited` to the recovery window — pin it beside `TestCA814RetreatedMarshalCannotCapture`, and correct (not flip) the docstring of `test_kienmayer_has_no_friendly_exit`. Route the beta-arm rampage to the FA-D27 gate with the 7,655-man / morale-100 measurement attached, and say on the row that the filed fix would not have touched it. Reproduce the `FORCED RETREAT!` Franche-Comte capture before writing the census that claims the seam is closed.

### Cross-row findings

SIX OF SEVEN REPRODUCE; NONE IS REFUTED. Only FA-70 carried exact line numbers — the other six drifted, three of them badly (FA-82 `_on_tutorial_pressed` 409->438 and its setter 452->556; FA-9 `movement_executor` 588->702 and `executor.py` 1490->1702; FA-101 `main.py` 4120->4487->**4664**, i.e. it has moved twice since the audit and once since J7). Navigate by symbol.

FIVE OF THE SEVEN FILED `fix_shape`s WOULD SHIP A DEFECT OR A NO-OP IF FOLLOWED LITERALLY, which is a higher hit rate than any prior slice in this build:
 - FA-9  — the prescribed predicate misses the WORSE measured case entirely (a healthy 7,655-man corps).
 - FA-82 — the prescribed function is not on the path a saved player takes.
 - FA-94 — the prescribed default arms ESC on a −3-trust decision button; and the obvious `close_popup()` wiring soft-locks the command line.
 - FA-101 — the prescribed alternative attach re-creates the buttonless modal WO-35 refused to build.
 - FA-63 — both prescribed mechanical options are dead: one buys a single turn, the other is MEASURED INERT (the AI unfortifies inside turn 1).
Only FA-70 and FA-81 have fix shapes that are safe as written.

J7 WAS WRONG IN ONE PLACE THAT MATTERS. It reported that FA-63's "authored HOLD/fortify posture" has "no authoring hook I could find in the scenario schema". The hook EXISTS — `Marshal.from_dict` reads `fortified`, `turns_fortified` and `stance`, `from_scenario` builds through it, and I landed the flag at boot. The option still fails, but for the opposite reason (the AI strips it in the first enemy phase), and the build should record the measured reason rather than the absent-hook one. A related drive-by nobody has filed: the validator's `MARSHAL_OPTIONAL_FIELDS` accepts `stance` / `morale` / `trust`, but `create_marshal_from_data` passes every key straight into `Marshal(**kwargs)` and the constructor takes none of them — a validator-legal scenario would `TypeError` on that path. (Scenario worlds are safe today because they route through `from_dict`.)

THE `.gd` SLICE IS FA-70 + FA-82 + FA-94 — one boot smoke, one parse harness. Baseline verified clean at HEAD before I started: harness EXIT=0, 47 scripts, 0 failures, and all six files in scope (`popup_base`, `war_detail_popup`, `main_menu`, `tutorial_overlay`, `mailbox_panel`, `proclamation_popup`) are inside the harness's script list. ⚠ Running the harness rewrote the timestamp line of `tools/godot_parse_report.json` (a one-line diff, content otherwise identical). I was forbidden from mutating the tree with git, so I left it; the build should regenerate or discard it.

ONLY FA-9 CAN MOVE `BASELINE_SERIES`, and it almost certainly will. Measured on a fresh 15-turn ambient 1805 run: the walk-in seam fires **22 times**, along the same corridor the tutorial uses (`Munich -> Franche-Comte -> Nivernais -> Orleanais`), and passive France ends at 15 provinces. So any change to `_corps_is_limited` or to the `movement_executor` predicate needs a flip lever with arm 0 reproducing the current series byte-for-byte. Nothing else in this set touches the backend's decision path; FA-81 and FA-101 are pure docs, FA-63 is docs + one scenario comment.

TWO OBSERVATIONS THE ROWS DO NOT CARRY, both worth a line in the landing record:
 1. 25 of 28 French provinces on the SHIPPED 1805 board are walk-in-takeable (no fortification, garrison < 5,000). FA-9 is not a tutorial defect that happens to be reachable early; it is a campaign-wide door that the tutorial's own beats open on turn 3.
 2. FA-9 seed `beta` shows Franche-Comte — the ONE province the tutorial garrisons at 12,000 — captured by a message beginning `FORCED RETREAT!`. That is a second capture producer (`combat_executor.py:7044`/`:7108`), not the walk-in predicate, and the build must reproduce that step itself before claiming one seam covers the row.

PROBE ARTEFACTS: all under the scratchpad `repro16/`; four driver runs under `tools/playtest_runs/repro16-*` (these are gitignored run outputs, not repo edits). No repo file was edited and no mutating git command was run.


### FA-70 - REPRODUCED

**Mechanism.** `war_detail_popup.gd::_render_war_detail` — `if we != null:` at **:424** closes at **:431** with NO else; the `else:` at **:439** binds to `if naval_line != "":` at **:437**, so the "Unknown" exhaustion line is emitted on the FLEETLESS branch. Line numbers are EXACT as filed — this is the one row of my seven with zero drift. The sibling site at **:472** (`_render_coalition_detail`) has the correct shape (omits WE when null) and must not be touched.

**Evidence.**

Source at HEAD, verbatim:
```
424	if we != null:
431		bbcode += "Enemy War Exhaustion: [color=" + we_color + "]" + str(we_int) + "[/color]\n"
437	if naval_line != "":
438		bbcode += "Their fleet: " + Utils.humanize_nation_keys_in_text(naval_line) + "\n"
439	else:
440		bbcode += "Enemy War Exhaustion: [color=" + COLOR_DIMMED + "]Unknown[/color]\n"
```
BOTH branches proven live on the shipped 1805 boot by driving `war_status.build_active_wars` and re-running the .gd branch structure by hand:
- NONE branch (live TODAY, the only war row at boot): `opponent=Britain we=None naval_line='100 sail of the line — readiness 100, on blockade'` -> `WE lines emitted: 0 <<< NONE`.
- DOUBLE branch inputs live at boot: `_naval_line(w,'Austria')` is `""` (ships 0) while `_get_nation_visibility('Austria', w) == 'partial'`, which `war_status.py:135-136` turns into `war_exhaustion = int(raw_we)` = 0 (non-None) -> both emits fire. Same for Prussia. Reachability: `_collapse_shared_war_instance_rows` folds all three boot courts into the Britain row, so Austria reaches `_render_war_detail` only once she has her own war instance (separate peace, or a fresh bilateral war).

**WARNING - what the row's own fix_shape would break.** The filed `fix_shape` is CORRECT and complete — it already says both halves ("move the else back under `if we != null:` AND make the naval block a standalone if with no else"). The one hazard is a lazier reading of it: naively NESTING the naval block inside `if we != null:` would hide `Their fleet:` for every fogged opponent — which is exactly Britain at boot, the only war row the shipped board has. That is the reverse regression.

**Minimal fix.** ONE seam. Move the `else:` + Unknown emit up to be the else of `if we != null:` (insert after :431); leave :436-438 as a standalone `if naval_line != ""` with no else. Two lines moved, no logic change.

**Tests.** None. The only pin touching this file is `tests/test_naval_ui_clarity.py::TestClientSurfaces::test_war_detail_consumes_naval_line` (:273-276), a text census asserting `"naval_line" in gd` and `"Their fleet:" in gd` — green before and after. Grep of the whole test tree for `Enemy War Exhaustion` returns exactly one hit and it is not this. No pin asserts the defect.

**Flags.** touches `.gd`


### FA-82 - REPRODUCED

**Mechanism.** `TutorialOverlay._conclude` (`tutorial_overlay.gd:556`) is the ONLY `set_tutorial_done` call anywhere in the client; `on_world_swap` (**:327**) does `if name != "tutorial" or UiSettings.get_tutorial_done(): _active = false; hide(); return`. Nothing ever writes false, and `MainMenu._on_tutorial_pressed` (**:438-456**) launches the scenario without touching the latch — so the second School boots the Danube map with no tutor card.

**Evidence.**

Census at HEAD (`grep -rn 'tutorial_done' godot-client/**/*.gd`) returns exactly five hits, one of them the setter call:
```
tutorial_overlay.gd:327	if name != "tutorial" or UiSettings.get_tutorial_done():
tutorial_overlay.gd:556	UiSettings.set_tutorial_done(true)      <- the ONLY setter call
ui_settings.gd:109 get_tutorial_done / :113 set_tutorial_done  (per-machine ConfigFile)
```
DRIFT: setter 452 -> **556**, gate 280 -> **327**, `_on_tutorial_pressed` 409 (filed) -> **438**. Line 409 today is `func _close_settings()`. The menu button is registered unconditionally enabled: `_add_menu_button("tutorial", "The School of War — a guided campaign", _on_tutorial_pressed, false)` at :258 (the 4th arg is `prominent`, not `disabled`).

**WARNING - what the row's own fix_shape would break.** YES, and it is the whole point of reading this row twice. The filed fix says `_launch('tutorial')` **or** `_on_tutorial_pressed`. Putting it in `_on_tutorial_pressed` SILENTLY DOES NOTHING for the majority case: that function only calls `_launch("tutorial")` in its `else` arm (:456). When `_saves.size() > 0 or MenuBoot.came_from_game` (:442) — i.e. any player who has ever saved, which is every player who would hit this bug — it merely shows the confirm row, and the launch happens later via the Yes button's `_launch(_confirm_action)`. Put the clear in `_launch` only.

**Minimal fix.** ONE line in `MainMenu._launch` (`main_menu.gd:471`): when `action == "tutorial"`, call `UiSettings.set_tutorial_done(false)` before `MenuBoot.pending_action = action`. `_launch` is the single funnel — the confirm arm reaches it through the Yes button's `_launch(_confirm_action)` at :248.

**Tests.** None. `grep -rn 'tutorial_done' tests/` returns exactly two hits, both in `tests/test_tutorial_position7.py:239-240`, and both are source-string censuses (`assert "static func set_tutorial_done" in settings`) that stay green. No pin asserts the defect, and no pin would catch a fix that lands in the wrong function — so the new pin must be a regex over `main_menu.gd` scoped to the body of `_launch`, not a bare file-level `"set_tutorial_done(false)" in src`.

**Flags.** touches `.gd`


### FA-94 - REPRODUCED-BUT-NARROWER

**Mechanism.** `popup_base.gd` is 71 lines and defines NO input handler at all (`_unhandled_input` / `_input` / `ui_cancel` / `KEY_ESCAPE`: zero hits). `main.gd::_unhandled_input` (**:1055**, ESC block **:1060-1085**) has four arms — wizard, top-bar screen, region panel, pause menu — and the last two are guarded `not _is_modal_dialog_open()`, so a registered modal is never reached; :1084 then calls `set_input_as_handled()` unconditionally. Of the five named surfaces only `proclamation_popup.gd` extends PopupBase; the other four extend CanvasLayer directly.

**Evidence.**

Census at HEAD:
```
popup_base.gd : 71 lines, 0 hits for _unhandled_input|_input|ui_cancel|KEY_ESCAPE
mailbox_panel.gd 0 · proclamation_popup.gd 0 · sabotage_discovery_popup.gd 0
vassal_rebellion_popup.gd 0 · capture_choice_dialog.gd 0 · interrupt_popup.gd 0
battle_diorama.gd 2   <- the ONE PopupBase subclass that already has its own
```
STRUCTURAL FACT the row does not state, and the fix depends on it: `DialogManager.register` does `get_parent().add_child(instance)` (:50) and DialogManager is `add_child`ed to Main (`main.gd:364`), so every popup is a LATER CHILD of Main. Godot delivers `_unhandled_input` in reverse tree order, so a new `PopupBase._unhandled_input` IS reached before main.gd's ESC ladder — proven empirically by `battle_diorama.gd:1306-1315`, which works today. It must call `get_viewport().set_input_as_handled()` when it acts and must NOT consume when it declines.

**WARNING - what the row's own fix_shape would break.** TWO, and the second is the more dangerous because nobody has filed it. (1) The filed default — "the single/rightmost non-destructive button" — arms ESC on `interrupt_popup.gd`, whose buttons are BUILT FROM `interrupt_data['options']` (:60-79) and whose rightmost cannon-fire option is `hold_position`: −3 trust and a cancelled standing order (FA-49's own measurement). It also arms `commitment_paradox_popup.gd`, whose decision state is honor/break (:54-55). The default must be null. (2) FAR WORSE: ESC must not call `close_popup()`. `PopupBase.close_popup` (:40-48) hides and disables buttons and emits NOTHING, while `proclamation_popup._on_acknowledge_pressed` (:105-107) does `close_popup(); dismissed.emit()` — and `main.gd::_on_proclamation_dismissed` (:2417-2429) is a control-return TAIL: it raises the queued proclamation / envoy digest / redemption / petition and then calls `set_input_enabled(true)`. An ESC that closes without emitting hides the card, leaves the command line DISABLED and orphans every stashed surface — a soft-lock of the FA-N4 / slice-6 class. Same shape for `mailbox_panel._on_close` -> `panel_closed` -> `main.gd:6000-6008`.

**Minimal fix.** `popup_base.gd` gains `func _unhandled_input(event)` mapping `ui_cancel` to an overridable `esc_control() -> Button` returning **null by default** (ESC does nothing); it must press the button's own handler, never call `close_popup()` directly (see hazard). `proclamation_popup.gd` overrides it to the Acknowledge button. `mailbox_panel.gd` (a CanvasLayer) wires `ui_cancel` -> its existing `_on_close` (:319). `battle_diorama.gd` already overrides `_unhandled_input`, so GDScript method override shadows the base and it is unaffected — do not 'help' it. Leave sabotage/vassal-rebellion/capture-choice alone (UI-2d-1's forced-choice class).

**Tests.** None found. `tests/test_popup_routing_registry.py` censuses main.gd's route table and inline `*_popup.show_*(` calls, not input handlers. The one pin reading `popup_base.gd` is `tests/test_ux23b_the_desk_is_quiet.py::test_popup_base_stops_what_a_subclass_CLAIMED` (:185-193), which asserts on `claim_cue` and the ordering inside `close_popup` — untouched by adding a new function. `tests/test_ui_visual_foundation.py` / `test_ui2_part2_color_and_map.py` are string censuses. No pin asserts the defect. The parse harness must be re-run.

**Flags.** touches `.gd`


### FA-81 - REPRODUCED-BUT-NARROWER

**Mechanism.** `deploy/README_TESTER.txt` line **111** reads "Seven marshals stand ready in the east" and the YOUR MARSHALS block (**:108-141**) lists seven; the 1805 boot fields EIGHT French pieces. `docs/TUTORIAL_SCRIPT.md` contains zero occurrences of "Napoleon" and zero of "Emperor". The row's PC clause "does not know why battles near him go better" is REFUTED — the battle report names it.

**Evidence.**

Boot roster measured at HEAD (`WorldState.from_scenario(europe_1805.json)`):
```
French pieces at boot: 8
  ('Bernadotte','Franconia','cautious',17000)  ('Davout','Rhineland','cautious',26000)
  ('Lannes','Franche-Comte','aggressive',18000) ('Massena','Milan','aggressive',42000)
  ('Murat','Franche-Comte','aggressive',22000)  ('Napoleon','Lorraine','sovereign',10000)
  ('Ney','Rhineland','aggressive',24000)        ('Soult','Lorraine','literal',30000)
```
Doc counts at HEAD: `grep -ci napoleon docs/TUTORIAL_SCRIPT.md` -> 0; `grep -ci emperor` -> 0. README line 111 verbatim: `Seven marshals stand ready in the east; more can be raised`.
REFUTING the aura clause — `backend/game_logic/battle_report.py:145-161` emits a labelled modifier row the player reads on every battle: `mods.append({"label": ("The Emperor commands in person" if _pres_a >= 0.999 else "The Emperor commands in person (his star dims)"), "value": _pct_a, "type": "bonus"})`. So the surviving PC clauses are only 'can be marched' and 'can be captured'.
Second narrowing worth stating: the TUTORIAL WORLD IS SOVEREIGN-FREE — `WorldState.from_scenario(tutorial_1805.json)` gives 4 French pieces `['Davout','Ney','Senarmont','Soult']`. So the School gap is missing *inventory* documentation, not a lesson in which the tester meets him. DRIFT: :100 -> **:111**, block :103-130 -> **:108-141**.

**WARNING - what the row's own fix_shape would break.** Nothing breaks — but the row's own additional finding is the trap and it is right: `tests/test_prebuild_fixes_2026_08_14.py:241 test_current_roster_present` hardcodes the stale seven (`for name in ("NEY","DAVOUT","SOULT","LANNES","MURAT","BERNADOTTE","MASSENA")`) and PASSES today with the gap shipped. Adding a paragraph does not flip it. Strengthen that pin IN PLACE to derive the French roster from `europe_1805.json` at test time rather than adding a second pin beside a vacuous one.

**Minimal fix.** Docs-only, as filed: a THE EMPEROR paragraph in the README's YOUR MARSHALS block and 'Seven' -> 'Seven marshals and the Emperor himself'; NP inventory rows in TUTORIAL_SCRIPT.md. Land it with FA-101 (also docs-only).

**Tests.** None flips. `test_current_roster_present` (:241) stays green either way — it is the vacuous pin, not a red one. `test_hotkeys_match_main_gd` and `test_appdata_saves_documented` read the same file and are unaffected. No pin asserts the defect; no pin covers TUTORIAL_SCRIPT.md content at all.

**Flags.** none


### FA-101 - REPRODUCED-BUT-NARROWER

**Mechanism.** The 'owner = row WO slice 12' claim for the `pending_objection`-at-load legibility gap is carried by FOUR FILES / SIX strings at HEAD, and slice 12's landing record contains no objection work while row WO is build-complete. The row's own 'two documents' undercounts, and its `main.py` citation has drifted twice: filed `:4120`, J7 measured `:4487`, HEAD is **`:4664`**.

**Evidence.**

Census at HEAD (`grep -rn 'owner = row WO slice 12'`, excluding .git and the audit reports):
```
backend/main.py:4664                                   # comment in the /load attach block
tests/test_wo_slice15_capture_question_holds.py:808    # comment
tests/test_wo_slice15_capture_question_holds.py:816    # DATA, inside KNOWN_SILENT_AT_LOAD
docs/WEIRD_OUTCOMES_SPEC.md:4419  ('owned by slice 12') and :4446 ('its owner named (slice 12)')
docs/BUG_FIXES.md:5326            (the WO-35 status cell)
```
The reachability argument still holds at HEAD: `OBJECTION_FREE_READS = frozenset({"status","help","economy","treasury","finances"})` at `executor.py:56-58`, consulted at `:1054` — `end_turn` is not in it, so the autosave cannot carry a standing tactical objection.
J7 left one question open and I closed it: the census at `:836-851` classifies by KEY membership only (`if key in QUEUE_DELIVERED or ... or key in KNOWN_SILENT_AT_LOAD: continue`) — it never reads the VALUE string. So editing `:816`'s text does NOT flip the test.

**WARNING - what the row's own fix_shape would break.** YES — the parenthetical alternative in the filed fix. "Or, if an owner is wanted, the 3-line attach guarded by `response.get('objection', {}).get('options')`" would attach the TACTICAL objection modal on load for a world that also carries `pending_strategic_objection`: the two share one response key and, by the census's own comment at :810-813, the saved dict records no tactical/strategic discriminator. That is precisely the buttonless-modal soft-lock WO-35 refused to build. Take the docs arm only.

**Minimal fix.** Docs-only, six strings across four files: replace 'owner = row WO slice 12' with 'ACCEPTED-UNREACHABLE' plus the one-line reachability argument (the objection dialog is modal; `end_turn` is refused by the executor's objection block and is not in `OBJECTION_FREE_READS`; the block prints its own answer words). Land beside FA-81.

**Tests.** None. `tests/test_wo_slice15_capture_question_holds.py::test_blocking_state_surface_census` reads only the KEY set of `KNOWN_SILENT_AT_LOAD` (verified by reading the loop at :836-851), so a value-text edit is invisible to it. If the build wants the row's behaviour_test (every KNOWN_SILENT entry names an OPEN owner or carries an 'accepted-unreachable' reason), that is a NEW assertion on the value string and must be added deliberately.

**Flags.** none


### FA-63 - REPRODUCED

**Mechanism.** `tutorial_1805.json` `_comment` (line **2**, not :1) claims starting Charles at Hungary "delays the combined-strength attack into the designed turn-8+ free-play window", and `TUTORIAL_SCRIPT.md:350-351` teach the counter-blow at ~T8-10. Measured on the driver at HEAD: Archduke Charles attacks Senarmont at Munich in the **turn-2** enemy phase, and the combined Charles + Schwarzenberg + Kienmayer assault lands in the **turn-3** phase.

**Evidence.**

`playtest_driver.py --script tools/playtest_scripts/tutorial_lesson.json --scenario tutorial --turns 10 --objection insist` (seed `historical`), digest verbatim:
```
## Turn 2 — enemy phase: 4 actions, 1 attacks — ArchdukeCharles engages in solid combat...
  ⚔ Archduke Charles (lost 1925) vs Senarmont (lost 2217)
## Turn 3 — enemy phase: 4 actions, 3 attacks
  ⚔ Archduke Charles (lost 1608) vs Senarmont (lost 2034)
  ⚔ Schwarzenberg  (lost 1219) vs Senarmont (lost 2147)
  ⚔ Kienmayer      (lost 1024) vs Senarmont (lost 822)
```
I did NOT reproduce the Sept-2 'mis-attributes the attacker' narrowing: Charles IS first, exactly as filed. The PC's '50,000 Austrians' is the authored pair total (Charles 26,000 + Schwarzenberg 24,000) and is fair by T3.

**WARNING - what the row's own fix_shape would break.** BOTH mechanical options in the filed fix are hazards, and I measured the second one. (a) 'Start Charles one march further east': he covers Hungary -> Tyrol in ONE enemy phase, so a province buys at most one turn and cannot reach T8. (b) 'Give the pair an authored HOLD/fortify posture' — J7 said no authoring hook exists; **that is wrong**, `Marshal.from_dict` reads `fortified` / `turns_fortified` / `stance` (`marshal.py` ~:1958 / :1973 / :1847) and `from_scenario` builds through it. I authored `"fortified": true, "turns_fortified": 1` on both and it LANDS at boot (`ArchdukeCharles fortified=True ... loc=Hungary`, control arm `False`) — and then the AI UNDOES IT INSIDE TURN 1: after one `end_turn` both read `fortified: False` and both have marched off their authored provinces (Charles to Bohemia). The enemy AI unfortifies at three rungs (INTENT `:1603-1606`, P-1 `:1664-1666`, P3.5). So option (b) is INERT — measured, not argued. Only the doc rewrite lands.

**Minimal fix.** Rewrite the `_comment` (line 2) and `TUTORIAL_SCRIPT.md:350-351` to say what the engine does — the reserve is on you by turn 2-3 — and add the timing pin the file has never had.

**Tests.** None. `tests/test_tutorial_scenario.py:102-119` pins only the authored start/strength/personality of the pair; the ONLY 'turn-8+' text in the whole test file is a COMMENT at :100-101 that repeats the false claim (`grep -c 'turn 8|T8|counter-blow'` -> 1, that comment). No timing assertion exists, so nothing flips and the new behaviour pin is additive. Note the sibling `test_kienmayer_has_no_friendly_exit` (:180-189) belongs to FA-9.

**Flags.** none


### FA-9 - WIDER-THAN-FILED

**Mechanism.** The walk-in capture predicate in `movement_executor._execute_move` (**:702-711**, filed as :588-596) checks controller / at-war / `discovered_enemies` / fortification / garrison>=5000 and never `retreating`, `broken` or a strength floor. Slice 4's new limiter `enemy_ai._corps_is_limited` (**:2756-2772**) covers `retreated_this_turn` and `broken` — NOT the multi-turn `retreating` / `retreat_recovery` recovery, which is FA-9's exact state. So a beaten remnant is handed `move` into an ungarrisoned French province and takes it.

**Evidence.**

1) The row's own deterministic sibling still fires at HEAD: with Senarmont at Munich and Davout+Ney at Swabia, `world.get_safe_retreat_destination('Kienmayer','Swabia')` -> **'Rhineland'** (French soil); at the untouched boot layout the same call -> `None` (ENCIRCLED). Slice 5's road law did not close it.
2) The AI half, driven directly (Kienmayer at Franche-Comte, 1,218 men, `retreating=True, retreat_recovery=1, broken=False`, Lorraine controller France / garrison 0 / no fortification):
```
_corps_is_limited(Kienmayer) = False
_evaluate_marshal -> ({'marshal':'Kienmayer','action':'move','target':'Lorraine'}, 1)
decide_single_action -> 'Kienmayer moves from Franche-Comte to Lorraine. Lorraine falls to Austria! (was France) (12 lost to march)'
Lorraine controller after = Austria
```
3) PLAYED, and this is the correction the build needs. Four seeds of the tutorial script under `--objection insist`, 10 turns each:
 - seed `historical` and `alpha`: provinces **28 -> 28**, Kienmayer CAPTURED at Swabia on T4. The row's headline does NOT reproduce on the default seed.
 - seed `gamma`: the row's chain verbatim — `Kienmayer moves from Franche-Comte to Lorraine. Lorraine falls to Austria!` then Rhineland, then Orleanais +2 more in one phase. **28 -> 23** (five, not six).
 - seed `beta`: **28 -> 12** by turn 10 — Franche-Comte, Nivernais, Burgundy, Limousin, Berry, Gascony, Guyenne, Anjou, Maine, Brittany, Normandy, Artois, Champagne, all 'marches ... unopposed! Captured: France -> Austria', two per phase, and still going. Ney's pursuit dies as `Order cancelled: No intelligence on Kienmayer's position, Sire.`
4) **THE DECISIVE MEASUREMENT.** Saves from the beta arm (`--save-at 4,5,6`):
```
t4 loc Nivernais str 7655 retreating False rr 0 broken False rtt False morale 100
t5 loc Burgundy   str 7579 retreating False rr 0 broken False rtt False morale 100
t6 loc Berry      str 7429 retreating False rr 0 broken False rtt False morale 100
```
The corps that eats sixteen French provinces is a HEALTHY 7,655-man corps at morale 100 — not retreating, not broken, not under 1,000.
5) Why the door is open everywhere: garrison census — TUTORIAL **26 of 28** French provinces are walk-in-takeable (only Paris 25,000 and Franche-Comte 12,000 have any garrison); shipped 1805 **25 of 28** (Paris, Normandy 12,000, Flanders 12,000).
6) The GR5 note holds at HEAD with drift: the retreat block is `executor.py:1694+` (`allowed_during_retreat = ['move','wait','recruit','retreat']` at :1702) nested under `if marshal and marshal.nation == world.player_nation:` at **:1563** (filed :1484-1502/:1490).
7) One step I could NOT attribute and the build must reproduce before assuming one seam: beta's first loss is `FORCED RETREAT! Kienmayer advances into Franche-Comte. (78 lost to march) Franche-Comte has been captured by Austria!` — Franche-Comte carries the scenario's 12,000 garrison, which the walk-in predicate would refuse. The message's producer is the attack-advance pair `combat_executor.py:7044` + `:7108`, not `movement_executor`.

**WARNING - what the row's own fix_shape would break.** THE LARGEST IN THIS SET. The filed fix — refuse a walk-in capture by a corps that is `retreating`/`broken` or under the 1,000-man threshold — **does not touch the worse case at all**: beta's Kienmayer is none of those three things (7,655 men, retreating False, broken False, morale 100), so building FA-9 exactly as written closes the gamma arm, ships a green pin, and leaves a 28 -> 12 tutorial standing. Second hazard: the row asserts the pin `tests/test_tutorial_scenario.py:180-189` is FALSE — it is NOT. `test_kienmayer_has_no_friendly_exit` asserts only geography (no Austria-controlled and no enterable neighbour of Swabia) and those assertions are TRUE and pass today. Only its DOCSTRING ("so a beaten Kienmayer breaks in place or dies") is false. The pin needs a corrected docstring, not a flip — and note the same file already asserts `can_enter_territory(w, "Austria", "France")` at :178, i.e. the lesson's own test documents the hole. Third: the row's headline magnitude was measured on ONE seed and is not the default board's behaviour.

**Minimal fix.** Two seams, and they are not the same defect. (i) The reproducible P1: extend `enemy_ai._corps_is_limited` (:2770-2772) from `retreated_this_turn`/`broken` to the whole recovery window (`retreating` or `retreat_recovery > 0`), behind its own flip lever beside `BROKEN_AI_CORPS_IS_LIMITED`, exactly as slice 4 did for FA-N6. That kills the gamma chain and the deterministic probe. (ii) The beta rampage is NOT closable there and should not be forced into this row — a healthy 7,655-man corps behind an empty front is arguably legitimate play, and it is the same shape as the open gate **FA-D27**. Route it there rather than inventing a predicate. The authoring alternative (garrison two tutorial provinces) closes one seed's path and leaves 24 open — do not take it as the fix.

**Tests.** No pin asserts the defect. The sibling guard is `tests/test_creative_audit_ca8_2026_08_04.py::TestCA814RetreatedMarshalCannotCapture::test_p_minus_1_respects_the_retreat_limiter` (:579-582), which covers `retreated_this_turn` only — the new pin should sit beside it in the same shape (slice 4's own idiom for FA-N6). `tests/test_tutorial_scenario.py:180-189` stays green and needs a docstring correction only. `grep -rn '_corps_is_limited' tests/` returns zero hits, so slice 4's own predicate is currently unpinned by name.

**Flags.** **could move an AI decision / BASELINE_SERIES**
