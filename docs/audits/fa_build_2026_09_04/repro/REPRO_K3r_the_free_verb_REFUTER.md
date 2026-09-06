I have enough measurements. Writing up.

---

# REFUTATION — FA-R3 "the strategic AP charge keys off the base verb"

**Overall: the report's core is CONFIRMED and its headline regression is REAL — but its central quantitative claim about that regression is a ~2.5× UNDERCOUNT, and its "the ruling is already implemented once" precedent is a mis-read of the site it cites.** Nothing in the report is fabricated; two things in it are wrong in ways a builder would act on.

---

## CLAIM 1 — "the three filed sentences reproduce at AP 4→4; ten shapes, not two; total AP-gate bypass at 0 AP"

**MY MEASUREMENT** (`r2_behav.py`, real `POST /command`, TestClient with all three of `M.world`/`M.game_state["world"]`/`M.parser` swapped, fresh 1805 boot, lever forced OFF in-process):

```
--- FILED (AP=4), lever OFF ---
  4->4 ok=True 'Davout, hold Rhineland and wait'          orders=['Davout:Rhineland']
  4->4 ok=True 'Ney, march to Lorraine and wait there'    orders=['Ney:Lorraine']  MOVED=[Ney Rhineland->Lorraine]
  4->4 ok=True 'Davout, support Ney and wait'             orders=['Davout:Ney']
--- CONTROLS ---
  4->2 'Davout, hold Rhineland'   4->2 'Ney, march to Lorraine'
  4->3 'Soult, hold Lorraine'     4->3 'Napoleon, hold Lorraine'
  4->2 'Davout, hold Rhineland and stay put'   (already fixed, as filed)
--- ZERO AP, lever OFF ---
  AP0 ok=True orders=1 'Davout, hold Rhineland and wait'
  AP0 ok=True orders=1 moved=1 'Ney, march to Lorraine and wait there'
  AP0 ok=False 'Davout, hold Rhineland'  -> "Not enough actions! Need 2, have 0."
```

All six EXTRA shapes (leading `wait`, `wait for orders`, `stand by`, `wait for reinforcements`, Soult-literal, Napoleon-sovereign) reproduce at 4→4. Shape 10 independently reproduced (`r11_focus.py`): `Davout, fortify` → AP 2, then bare `hold Rhineland and wait` → **2→2**, order created.

**VERDICT: CONFIRMED**, all ten shapes, including the 0-AP total bypass and the literal/sovereign tier bypass.

---

## CLAIM 2 — "already built in the working tree, lever `STRATEGIC_ORDERS_ARE_PRICED_BY_THE_ORDER = True`"

**MY MEASUREMENT**: `git status` shows 27 modified/untracked paths at HEAD `9ef38da8`. `git diff backend/commands/executor.py` shows +45 lines: the lever at `executor.py:64` and the guarded block at `executor.py:1241`, sited above the `is_strategic_execution` override. Grep finds the symbol at exactly two production sites.

**VERDICT: CONFIRMED.** The block's siting is correct — I measured the per-turn tick separately (`r10_exemption.py`): issue at 4→2, `end turn`, order still standing, tick charged nothing.

---

## CLAIM 3 — "the retreat regression: 6 of 22 phrasings; `withdraw from the alliance` is the general-retreat case"

⛔ **This is the report's one materially wrong number.**

**MY MEASUREMENT** (`r6b_seeded.py` — 54 phrasings × 6 verbs × 4 compass directions, `random.seed(4242)` per command, both lever positions, AP 4 and AP 0):

```
CHANGED AT AP4: 15 of 54
LOST AT 0 AP:   15 of 54
['fall back north','fall back south','Ney, fall back south','fall back east',
 'fall back west','Ney, fall back west','withdraw north','withdraw south',
 'Ney, withdraw south','withdraw east','withdraw west','Ney, withdraw west',
 'withdraw from the alliance','withdraw from the coalition',
 'Ney, fall back and observe Mack']
```

The report's six are a strict subset. It tested only the `south` direction and missed north/east/west entirely, and missed `withdraw from the coalition`.

**The general-retreat blast radius is 8×, not 1×.** Eight of the fifteen move all eight French marshals and every one is refused at 0 AP:

```
'fall back north'   OFF: ok=True  moved=8  "General retreat ordered! Ney falling back! Davout falling ba…"
                    ON : ok=False moved=0  "Not enough actions! Need 2, have 0."
'withdraw east'     OFF: ok=True  moved=8   ON: ok=False "Not enough actions! Need 2, have 0."
```
(same for `fall back east/west`, `withdraw north/west`, `withdraw from the alliance`, `withdraw from the coalition`)

**VERDICT: CONFIRMED IN KIND, REFUTED IN MAGNITUDE.** The regression is real, deterministic and worse than filed: **15 phrasings, 8 of them whole-army retreats, all 15 unavailable at 0 AP.**

⚠ **And three rows a naive re-run would add are RNG, not the fix.** My first unseeded pass reported 18. An 8-seed determinism check (`r7_determinism.py`) shows `Ney, retreat north`, `Ney, retreat west` and `Ney, pull back west` are **IDENTICAL** under both levers (`[(0, True, 1)]` both ways) — they differ only because the disobedience roll is unseeded. A builder pinning those gets a flaky test.

---

## CLAIM 4 — "site 3 (`strategic_executor:2878`) is already correct — the precedent; the ruling is already implemented once, in the objection route"

**MY MEASUREMENT** (`r3_objection.py`, `r4_charge.py` — spy on `_handle_strategic_objection_from_endpoint` and on `WorldState.use_action`):

```
choice=insist      'Davout, march to Swabia and wait there'   TOTAL SPENT = 1
   handler: {'vac': 1, 'success': True}      use_action calls: ['MOVE_TO']
choice=insist      'Davout, march to Swabia'   (CONTROL)      TOTAL SPENT = 1
choice=trust  … 1     choice=compromise … 1     (all six combinations)
```

Reading the symbol: `strategic_executor.py:1847/1866/1889` **overwrite** `result["variable_action_cost"] = 1` on every arm, per the WO-37 comment (*"the trust arm is priced at 1 AP on the button"*). The charge at `:2880` then reads that 1.

So the site is immune **not because it prices by the order** — it never consults the order's price at all, and never reads `free_actions` — but because a flat, deliberate 1-AP objection discount is stamped over whatever the strategic executor returned.

**VERDICT: NARROWED.** The report's *table* row is right ("no `free_actions` read at all"). Its *prose* — "the ruling is already implemented once, in the objection route", "site 3 is the precedent" — is a mis-characterisation, and its own quoted evidence (4→4→3, i.e. 1 AP for a 2-AP order) shows the site does not implement the ruling. A builder who copies "the precedent" copies a flat discount, not a price-by-the-order rule.

---

## CLAIM 5 — "`meta_executor._execute_post_objection` holds a verbatim duplicate but is measured unreachable with a strategic type"

**MY MEASUREMENT**: byte-comparison of `executor.py:1209` against `meta_executor.py:2085` → `IDENTICAL: True`, both 33 entries. Instrumented spy on `MetaExecutor._execute_post_objection` across four geometries (wait-suffixed MOVE_TO, wait-suffixed HOLD, `fortify`, `attack`) → **`post_objection calls seen: []`**.

**VERDICT: CONFIRMED**, with one correction: the report cites *one* `variable_action_cost` reader in that function. There are **two** — `meta_executor.py:2129` and `:2244`, both inside `_execute_post_objection` (2063–2282). Whoever patches the duplicate must patch or reason about both.

---

## CLAIM 6 — "33 free_actions, 30 blocked at the parser, only wait/retreat/break_square reachable"

**MY MEASUREMENT** (`r1_sets.py`, live import of `validation.NEVER_STRATEGIC_ACTIONS`):
```
free_actions count: 33 · NEVER_STRATEGIC_ACTIONS: 44 · blocked at parser: 30
free AND can-be-strategic: ['retreat', 'wait', 'break_square']
```
`break_square` probed with four strategic-shaped phrasings (`r10_exemption.py`) → **no seam hit on any**.

**VERDICT: CONFIRMED exactly.**

---

## CLAIM 7 — "ZERO pins flip" (asserted over 4,869 tests)

**MY MEASUREMENT**: 14 highest-risk files under a child-process lever plugin (the safe idiom — never writes a repo file), `-p no:randomly`:
```
LEVER=off  678 passed, 1 skipped
LEVER=on   678 passed, 1 skipped
```
Files included `test_retreat_system.py`, `test_retreat_system_comprehensive.py`, `test_w6_retreat_doctrine.py`, `test_wo_slice11_typed_route_residue.py`, `test_strategic_{executor,order,objections}.py`, `test_counter_punch_ap_gate.py`, `test_fa_slice{3,5,7}*`, CR-2/CR-4.

**VERDICT: CONFIRMED on the highest-risk subset.** I did not re-run the 4,869-test sweep, so I confirm the *conclusion*, not the number.

**This is also the most alarming corroboration in the pass**: two dedicated retreat test files and 678 tests are structurally blind to a change that makes the whole army's retreat unavailable at 0 AP.

---

## CLAIM 8 — "BASELINE_SERIES / M1–M7 cannot move; 1,157 executor calls, `strategic_AND_free` = 0"

The report's number did **not** reproduce under my first harness — `advance_turn()` reaches the executor **zero** times. The AI phase runs through `TurnManager.end_turn`, which is what `_emit_series` (`test_ai_intent_threat_migration.py:1111`) actually calls.

**MY MEASUREMENT** (`r9_series_tm.py`, correct entry, `SOVEREIGN_SEED=historical`, `PYTHONHASHSEED=0`, per-turn `random.seed(10_000+t)`, 20 turns, both levers):
```
LEVER=OFF turns=20 threat=25   execute calls = 667   strategic=0   free=127
  FREE-action histogram = {'wait': 123, 'retreat': 3, 'break_square': 1}
  *** strategic AND free (the seam) = 0
  FP = 101e88c7b2 e0ed0dbe47 … 06a0dccce8
LEVER=ON  turns=20 threat=25   (byte-identical on every field, incl. all 20 fingerprints)
```
Structural backing I verified by reading: `grep -c "is_strategic\|strategic_type" backend/ai/enemy_ai.py` = **0**; the AP pre-gate is `if action_costs_point and is_player_action_check and not counter_punch_waiver:` (`executor.py:1334`) and the charge is `and is_player_action` (`:2580`) — both player-gated. `test_combat_sweep_metrics.py` contains **0** of `CommandExecutor|executor.execute|is_strategic|actions_remaining|advance_turn|end_turn`.

**VERDICT: CONFIRMED** (conclusion independently measured; the report's per-40-turn histogram 290/4/2 is proportionally consistent with my 20-turn 123/3/1). **NARROWED on method**: the "1,157 calls" figure is unverified — reproduce it through `TurnManager.end_turn`, not `advance_turn`.

---

## CLAIM 9 — the recommended shape, `and action != "retreat"`

**MY MEASUREMENT** (`r10_exemption.py`, spy capturing the parsed tuple at the seam):
```
THE 15 REGRESSIONS:  action=retreat, strat_type=MOVE_TO  — all 15
  ALL 15 parse action=='retreat'? YES
THE 9 POSITIVES:     action=wait — all 9
  any positive parses 'retreat'? NO — exemption is safe
```

**VERDICT: CONFIRMED, and now exact.** The exemption is a perfect cut: 15 in, 0 positives touched, zero overlap. It restores all 15 (not the 6 the report scoped it to).

---

## CLAIM 10 — corpus coverage, and the `action_info` warning

**MY MEASUREMENT**: 436 entries, byte-identical to HEAD. `and wait` = 0, `wait there` = 0, `wait for orders` = 0; `stand by, Ney, move to Paris` and `Ney, wait for reinforcements` exist as the only neighbours. **Extending it: zero corpus rows anywhere carry a `strategic_type` with a free base action** — the corpus is structurally blind to this entire class, not merely missing these phrasings.

`action_info` under-report reproduced: `hold Rhineland` spends 2, reports `{'cost': 1, 'remaining': 0}`.

**VERDICT: CONFIRMED, slightly extended.**

---

## CLAIM 11 — line numbers

Checked against **HEAD** (several cited files are dirty, so working-tree numbers mislead):

| report | HEAD actual | verdict |
|---|---|---|
| `marshal.py:847` `strategic_order_ap` | **847** | correct |
| `executor.py:1199` "retreat is FREE" | **1199** | correct |
| `strategic_executor.py:2878` | def at 2524, charge comment 2878, read 2880 | correct enough |
| `meta_executor.py:2124` | **2129** | off by 5 |
| `combat_executor.py:4911` | **4882** | **stale by 29** |
| `executor.py:2290` (site 1, "the typed player route") | charge read at **2550** | **stale by 260** |

**VERDICT: NARROWED.** Mostly HEAD-anchored and sound; two anchors will send a builder to the wrong place. Navigate by symbol.

---

## What the reporter MISSED that a builder must know

1. **The regression is 15 phrasings, and 8 of them are whole-army retreats.** Scope the fix and every pin to `{fall back, withdraw} × {north, south, east, west}` plus `withdraw from the {alliance, coalition}` plus `Ney, fall back and observe Mack`. Testing `south` only, as the report did, hides two-thirds of it.
2. **Three retreat rows are RNG, not the fix.** `Ney, retreat north`, `Ney, retreat west`, `Ney, pull back west` differ run-to-run because the disobedience roll is unseeded; under 8 fixed seeds they are identical on both levers. Seed every retreat pin or it flakes.
3. **`Ney, fall back and observe Mack` creates a strategic order whose target is the phantom province `"And Observe Mack"`** (measured, both levers). The report named the sentence but not that it mints garbage state — file it separately; the FA-R3 fix does not touch it.
4. **The PF-6 "stand-fast + wait" refusal family has three members, not one.** The report filed `Davout, hold your ground and wait`; I also measure `Ney, hold position and wait` and `Davout, stand fast and wait` refused (`ok=False`, 0 AP) while their bare forms cost 2 AP. Pre-existing, unchanged by the lever.
5. **`_execute_post_objection` has two `variable_action_cost` readers (2129 and 2244), not one** — a single-site patch of the duplicated `free_actions` leaves the second half divergent.
6. **The objection route is a 1-AP road to a 2-AP order on all three arms.** Deliberate (WO-37), but it means the report's "precedent" is not a precedent, and any pin written as *"the wait-suffixed and bare forms behave identically through the objection route"* is green regardless of whether FA-R3 is fixed — it was green pre-fix too.
7. **Reproduce the series through `TurnManager.end_turn`.** `advance_turn()` reaches the executor zero times and will make any seam-reachability probe trivially "prove" 0.