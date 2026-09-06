Repo clean. Report:

---

# FA-31 — "The Grand Diversion is quoted blind"

## VERDICT: **NARROWED — but the Sept-2 verification and the Sept-4 prior repro each over-corrected, and I am correcting both.**

The outcome reproduces. The mechanism is inverted. **And two of the prior repro's own corrections are themselves wrong** — the row's arithmetic is *reachable*, and the row is *not* about a dead arc, it is about a chip that warns in the safe state and falls silent in the trap.

Probes: `…/scratchpad/s14/H_diversion/probe_{1,2,3,4,5,6,8,9,11,12,13}*.py`, series child `probe_7b_series_child.py`, pytest plugins `fa31_patch.py` (row's filed fix), `fa31_rec.py` (recommended shape), `fa31_redrive.py` (behaviour lever). Repo untouched (`git status` empty at `9ef38da8`).

---

## 1. What reproduces

### The row's boot arithmetic — EXACT (`probe_1_boot.py`)

```
France  45 sail @70 posture=guard   eff=31.50
Britain 100 sail @100 posture=blockade island=True
blockaded_nations: ['France','Holland','Spain']      camp_strength(France)=0
sea links touching London: [('London','Normandy')]     <- the only one

Normandy->London, no window          : shut   cov=100.0  mover=53.8 ratio=0.54 floor=1.25
   + window_turns=2, no re-derive    : window cov= 50.0  mover=53.8 ratio=1.08 floor=0.9  ALLOWED
   + window_turns=2, derive_postures : window cov= 55.2  mover=53.8 ratio=0.97 floor=0.9  ALLOWED
UNROUNDED mover=53.82 coverage=55.2 ratio=0.975
```
Pool: `31.5 + 0.8×19.5 + 0.8×8.4 = 53.82`. The row's "53.8 vs 55.2 = 0.97 OPEN" is exact.

### The row's *own repro recipe* — EXACT, and **REACHABLE** (`probe_12`, `probe_13`)

```
ROW'S RECIPE (ships=49, all three @50): allowed=False verdict=shut
                                        coverage=55.2 mover=41.3 ratio=0.75
```
**and the state is reachable by the exact play the archived digest records** — build one keel a turn under blockade (`build_rate`=1) for 2,000g:
```
45@70 -> 46@69 ->tick 64 -> 47@63 ->58 -> 48@58 ->53 -> 49@53 ->50
turn 5 start: 49 sail @ readiness 50     <- the row's "70→69→64→63→58→58→53→50", exact
```

### The headline outcome — REPRODUCES at the natural timing (`probe_3` (b), `probe_4`, `probe_5`)

Marching Soult (30k) + Napoleon (10k) from Lorraine to Normandy is **4 hops**; Ney/Davout **5**. With four marching turns of rot, then two camp ticks:
```
t=6 read=50 camp=2 staged=True GB=blockade blk=Y | SAME 0.7860 False | NEXT 0.7018 False
```
**At the earliest realistic staging turn a WON roll leaves London–Normandy SHUT both ways.** The row's headline sentence is true.

---

## 2. What is FALSE — in the row, in the Sept-2 verdict, and in the prior repro

| Claim | Source | Verdict |
|---|---|---|
| "staging the camp … four turns of blockade rot … SHUT even inside the window" — as a *terminal* state | FA-31 | **INVERTED.** Staging the camp is the CURE. |
| "the Descent's marquee arc is dead on the natural timing" | FA-31 `player_consequence` | **FALSE.** Delayed 3 turns, then permanently open. |
| "by the time the camp is staged, a WON roll leaves London–Normandy SHUT" is FALSE | **Sept-2 verification** | **OVER-CORRECTED.** Measured true (0.786 / 0.702). Only the *causality* is wrong. |
| "its quoted numbers (41.3 vs 55.2) are unreachable on the shipped board — the board's number is 39.3" | **prior repro (b)-4** | **FALSE.** 39.3 is the no-build number; the row builds keels, and 49@50 → 41.3 reproduces exactly (`probe_13`). The prior repro never built. |
| `naval.py:958ff` / `:1573` / `:2091` / `:2293` | FA-31 | **all four stale.** 958=`_fleet_covers_link`; 1573=`resolve_diversion` docstring; 2091=the blockade-effects loop; 2293=`report["expedition_terms"]`. |

### The camp is the cure — measured over 13 ticks (`probe_2_camp_arc.py`)

```
ARM A (no camp)            ARM B (50,000 at Normandy from tick 0)
t  read blk    ratio       t  read blk campT staged GB       SAME  NEXT
0   65  Y      1.00/0.90   0   65  Y     1  False  blockade  1.00  0.90
1   60  Y      0.92/0.82   1   60  Y     2  True   blockade  0.92  0.82
2   55  Y      0.84/0.75   2   65  n     3  True   guard     0.89  0.89
3   50  Y      0.79/0.70   3   70  n     4  True   guard     0.96  0.96  ALLOWED
…  50  Y      0.79/0.70   4   75  n     5  True   guard     1.03  1.03
12  50  Y      0.79/0.70   5+  75  n            guard        1.05  1.05
```
`derive_ai_postures` pulls the island fleet to `guard` at `camp_turns>=2`, `blockader_against` stops returning Britain, France leaves `blockaded_nations`, and `_readiness_tick` switches from −5 rot to +5 toward `NAVY_DRILL_CEILING` 75.

---

## 3. The real seam — by symbol

`resolve_diversion` **does NOT call `derive_ai_postures`** (verified by reading `naval.py::resolve_diversion`; the success arm sets `window_turns` and returns). Consequence, measured (`probe_3` (c/d)):

```
Britain posture=blockade -> combined_effective(match_posture="blockade") = 100.00 -> halved 50.00
Britain posture=guard    -> combined_effective(match_posture="guard")    = 110.40 -> halved 55.20
                            parts = [Britain 100.0, Russia 10.4]   (0.8 × 20 sail @65)
```
**The window's second turn is 10–12% WORSE than its first, because the player's own success flips Britain to `guard` and thereby recruits Russia's guard squadron into the coverage pool.** One tick of rot in (readiness 65) the second turn closes by **0.0027**: `0.8973021582733813` against floor `0.90`.

| symbol | file | role |
|---|---|---|
| `build_admiralty_report` — the local `diversion_terms` list (**:2193**) and the Diversion entry in `chips` (**:2394**) | `backend/game_logic/naval.py` | the two display surfaces |
| `NavalExecutor._execute_naval_diversion`, the `if not confirmed:` arm (**:568-620**) | `backend/commands/naval_executor.py` | the third |
| `resolve_diversion` (**:1568**) | naval.py | sets `window_turns`, never re-derives |
| `covering_fleets` (**:966**) + `combined_effective` `match_posture` (**:370**) | naval.py | why the flip *raises* coverage |
| `derive_ai_postures` (**:1639**), `_readiness_tick` (**:1662**), `_camp_tick` (**:1693**) | naval.py | the cure |
| `find_ai_diversion` (**:2765**) | naval.py | GR5 sibling — **gates ON `camp_staged`**, i.e. steers the AI into the trap state |
| `blockade_forecast` (**:492**) | naval.py | the idiom to copy |

### The chip's warning is inverted — measured verbatim (`probe_4_surfaces.py`)

| state | ratio | chip `note` |
|---|---|---|
| SAFE — boot, no camp, readiness 70 | 1.08 / 0.97 **open** | `45% — and once only, this war; no army is staged to use the open water` ← **warns** |
| TRAP — camp staged t6, readiness 50 | 0.786 / 0.702 **shut** | `45% — and once only, this war` ← **silent** |

`diversion_terms` is identical in both states (three `met: true` booleans). The typed confirm differs only in the *failure* readiness (60 vs 40):

> `The Grand Diversion is drawn up, Sire — once, and once only, this war. The fleet sails to draw the enemy squadrons off station: 45 times in 100 the strait opens for 2 turns; otherwise she is caught coming home and fights at readiness 40. Sail? (yes / no)`

The Crossings line is the no-window verdict (`London–Normandy: SHUT — the Royal Navy at 2.6×`), so it says nothing about what the card buys.

`find_ai_diversion` returns `None` in SAFE and a candidate in TRAP — the AI is *steered into* the worthless state.

---

## 4. What the filed fix would break — **three separate regressions, measured**

**(a) "the island fleet's derived-guard posture" makes the forecast LIE on the diversion turn** (`probe_6`, last block):
```
tick 0: TRUE same-turn allowed=True r=1.00 | row's forecast (guard) allowed=False r=0.90  <-- CONTRADICTS
tick 1: TRUE same-turn allowed=True r=0.92 | row's forecast (guard) allowed=False r=0.82  <-- CONTRADICTS
tick 2: TRUE same-turn allowed=False r=0.84| row's forecast          allowed=False r=0.75
tick 3: TRUE same-turn allowed=False r=0.79| row's forecast          allowed=False r=0.70
```
A shown≠applied fix shipping a new shown≠applied — and it would tell the player *not* to spend the card in the only two turns of the campaign where spending it opens the strait.

**(b) "make it a fourth `diversion_terms` row" disables the verb and DELETES the odds** (`probe_6`, middle block). `report["diversion_available"] = all(t["met"] …)`:
```
SAFE boot : forecast met=True  -> diversion_available True  -> True
TRAP staged: forecast met=False -> diversion_available True  -> False
   chip enabled True -> False; note '45% — and once only, this war' DELETED
```
Measured against `strategic_ledger.gd::_render_admiralty_orders`: `note` renders **only on an enabled chip**, `reason` **only on a disabled one**. So the fix trades the odds and the once-per-war warning for the forecast, and contradicts the recorded design decision at the chip ("A warning, never a lie: it stays clickable, because it works"). It also contradicts the executor, which never reads `diversion_available` — the verb would still work while the chip is dark.

**(c) `London–Normandy` hardcoded, and "island fleet" is the wrong scope** (`probe_9`):
```
France  boot links: [('Normandy','London')]                 <- right by accident
Britain boot links: [('London','Normandy')] verdict=landing 2.05  -> window 4.10 ALLOWED
_island_war_enemies(Britain) = []   <- an ISLAND-scoped scan yields NOTHING for the mirror actor
```
`covering_fleets` halves **every** coverer, not only an island's, so the scan must be "sea links from my provinces to a war-holder's".

**(d) a bonus the row missed — a window WAIVES the NV-4 host rule.** `crossing_check`'s landing arm is `if allowed and not window_open`. Proven with the RN cut to 5 sail: `landing`/refused → `window`/allowed. The forecast has a second true thing to say that no surface knows.

### The isolation question, answered by experiment (`probe_8_isolation.py`)

Three shapes, identical verdicts. Under a deliberate exception mid-forecast:
```
A  (mutate + try/finally) : world unchanged = True
A' (mutate, no finally)   : world unchanged = FALSE
     LEAK: France.window_turns=2  Britain.posture=guard  blockaded=[]
           <-- a free 2-turn window and a lifted blockade, granted by OPENING A SCREEN
B  (swap world.fleets for a deepcopy) : world unchanged = True
cost: A 0.075 ms/call · B 0.182 ms/call
```
**What must be copied: `world.fleets` — all of it, and nothing else.** Every naval read in the crossing path goes through `get_fleets(world)` (`iter_fleets` / `get_fleet` / `_meta`), plus the read-only `world.regions`, `world.is_at_war`, `world.player_nation`, `world.sovereign_map`. `crossing_check` itself is **pure** (verified: 8 calls, fleet store byte-identical, event_log unchanged). One attribute swap in a `try/finally` is complete isolation and cannot leak; the per-record posture save/restore can. `build_admiralty_report` is reached **only** from `build_strategic_ledger` ← `GET /ledger`, which the player hits on every L-press — so exception safety is not academic.

---

## 5. Pins that flip

**Zero — under all three candidate shapes.** Measured by running the narrow selection under pytest plugins that install each shape (`tests/test_naval_host_rule.py test_naval_descent.py test_naval_ui_clarity.py test_wo_slice6_the_admiralty_speaks_plainly.py test_naval_diorama.py test_hc4_naval_balance_duo.py test_pc15_fix_slice_2026_08_15.py`, `-p no:randomly`):

| arm | result |
|---|---|
| baseline (6 files) | **190 passed** |
| baseline (7 files, +pc15) | **243 passed** |
| `-p fa31_patch` — the **row's own filed fix** (4th gate row) | **243 passed** |
| `-p fa31_rec` — the recommended note-only shape | **243 passed** |
| `-p fa31_redrive` — `resolve_diversion` re-derives postures | **243 passed** |

**That is the finding, not a reassurance.** Every diversion pin is written at *boot readiness 70*, where the forecast is met — so the row's own fix would silently disable the chip in the reachable trap state and **243 green tests would say nothing**. There is also **no purity pin** on `build_admiralty_report` or `build_strategic_ledger`, so the A'-shape leak would ship unseen.

Pins the build must consciously touch or extend:
- `test_naval_host_rule.py::test_the_diversion_chip_warns_about_the_trap_it_cannot_gate` — `enabled is True`, `"no army is staged" in note`, `str(45) in note`. Survives a note-append; **must gain a positive forecast assertion or it stays a lie-detector for the wrong lie.**
- `::test_the_warning_clears_once_the_camp_is_staged` — asserts the *absence* of a string. It is exactly the pin that certifies today's inversion; it needs a positive counterpart.
- `::test_every_term_carries_both_phrasings`, `::test_a_withheld_chip_states_why`, `::test_a_withheld_chip_reads_forwards_not_backwards` — all bind if a gate row is added; do not add one.
- `test_naval_ui_clarity.py::TestClientConsumesThePayload` — the file's standing contract is *"a payload nothing renders is a lie waiting to be filed; every new field names its consumer."* A new `report["diversion_forecast"]` key therefore obliges a `.gd` edit → parse harness → boot smoke. `strategic_ledger.gd` renders `detail` on `expedition_terms` but **not** on `diversion_terms` (verified in source), so a per-term detail is also a `.gd` edit.
- `test_naval_descent.py::TestA4WorkedExample` (0.53 / 1.07 / 0.74) — all three use `_at_drill_ceiling`, which already forces Britain to `guard`; unaffected by either lever. **A boot-readiness pin must be added beside them** — the absence of one is why this was invisible for a month.
- `test_pc15_fix_slice_2026_08_15.py::test_bare_diversion_quotes_and_does_not_burn_the_attempt` / `::test_confirmed_diversion_resolves` — the confirm text changes; the `diversion_used` assertions hold.

---

## 6. Series / harness risk

**Series: none, structurally — and measured.** Ran the *committed* `_emit_series` recipe (`PYTHONHASHSEED=0 SOVEREIGN_SEED=historical LLM_MODE=mock`) with counters injected (`probe_7b_series_child.py`):

```
MATCHES_BASELINE = True
find_ai_diversion_calls : 446      find_ai_diversion_hits : 0
resolve_diversion       : 0        build_admiralty_report : 0
process_naval_turn      : 40       camp_ticks_nonzero     : 0
crossing_check          : 5190     derive_ai_postures     : 41
```
- The three display surfaces are called **0 times** in 40 turns (`build_admiralty_report` is `GET /ledger`-only).
- `resolve_diversion` fires **0 times**, so even the behaviour lever (re-derive postures on success) is **inert with a stated reason** and pinnable by construction.
- `camp_staged` is never True and `window_turns` is never > 0 on any nation-turn; `strait_open`/`boulogne_camp` events = 0.
- A stricter `find_ai_diversion` gate cannot move it: the rung already returns `None` on **446/446** evaluations.
- **The one thing that WOULD move it: `crossing_check` fires 5,190 times.** So the forecast must be a *new pure reader*; it must not alter `crossing_check`, `covering_fleets`, `combined_effective` or `derive_ai_postures` themselves.

**M1–M7: none, structurally.** `tests/test_combat_sweep_metrics.py` contains **zero** occurrences of `naval` / `fleet` / `crossing`; it calls `resolve_battle` directly and drives marshals by object.

---

## 7. Recommended build shape

**Zero new payload keys, zero `.gd`, zero gate rows, 0 pins flipped — verified by running the selection under it (`fa31_rec.py`, 243 passed).**

1. **ONE pure `naval.window_forecast(world, actor)`** — the `blockade_forecast` idiom (*a pure function both producers read*), but implemented by **swapping `world.fleets` for a `copy.deepcopy` inside a `try/finally`**, not by mutate-and-restore. Set `window_turns` on the copy, call `derive_ai_postures`, then call the **real `crossing_check`** — never a second implementation of the crossing rule (that is the CA9 through-line the audit exists to close). Scan sea links from provinces the actor holds *or has a corps standing on* to any province held by a court it is at war with — **not** `_island_war_enemies` (measured: yields nothing for Britain, the GR5 mirror actor).
2. **Resolve the same-turn/next-turn ambiguity, don't paper over it.** Prefer having `resolve_diversion`'s success arm call `derive_ai_postures` immediately, so both window turns are one honest number — a **conscious behaviour flip** (boot same-turn 1.08 → 0.97, still open; the one-tick-of-rot case 1.00 → 0.90 flips SHUT by 0.0027), series-inert with a written reason, and it needs its own flip lever + measured record. If that flip is not wanted, the forecast must quote the **worse** of the two and say why.
3. **Three readers, none of them a gate.** Append the forecast clause to the **existing** chip `note` and the **existing** confirm message. Reuse `blockade_forecast`'s precision-escalation idiom (`row["render"]`, 0→1→2 dp until the pair separates) — at boot the raw render reads "54 against 55", which is 0.97 and looks shut. Leave `diversion_terms` as three booleans and `diversion_available` a three-boolean product.
4. **Say the remedy, since it exists.** When shut *and* blockaded: staging the camp lifts the blockade and readiness recovers +5/turn to 75 — the measured arc t6 0.79 → t9 0.91 → t10 0.98. That turns the row from a warning into the tutorial the Descent never had.
5. **GR5.** Gate `find_ai_diversion` on the same forecast (it currently *requires* the trap state). Series-safe by arithmetic: the rung already returns `None` 446/446.
6. **Add the pin the suite never had** — a crossing measured at a readiness the player actually holds during the run-up, beside the three `_at_drill_ceiling` anchors — and **a purity pin** on `build_admiralty_report` / `GET /ledger` (snapshot `world.fleets` before and after; measured to red on the no-`finally` shape).

Sample output of the recommended shape across the four campaign phases (`probe_11_copy.py`):

```
PHASE 1  t1  read 70, unstaged : 45% — and once only, this war; no army is staged to use the
                                 open water; a success opens London–Normandy (54 against 55…)
PHASE 2  t5  read 50, unstaged : …; even a success leaves London–Normandy shut (39 against 56…)
PHASE 3  t7  read 50, STAGED   : 45% — and once only, this war; even a success leaves
             <== THE TRAP        London–Normandy shut (39 against 56, where 0.9 is needed)
PHASE 4  t11 read 70, recovered: …; a success opens London–Normandy (55 against 56…)
```

**Siblings to land in the same slice** — both were filed *by the FA-31 sweep* and both sit inside this exact machinery: **FA-N82** (`_camp_tick` runs on `iter_fleets`, so a 0-ship France's camp stops ticking and the un-blockade cure can never fire) and **FA-N83** (`diversion_used` clears only at *total* peace while six surfaces say "this war").