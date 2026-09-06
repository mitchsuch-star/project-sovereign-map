# FA-R3 — "the strategic AP charge keys off the base verb"

**VERDICT: WIDER — and ⛔ ALREADY BUILT IN THE WORKING TREE, in the exact shape that ships a measured regression.**

> **⚠ READ THIS FIRST.** Partway through this pass the working tree stopped being clean. A sibling slice-14 agent has **already landed FA-R3** as an uncommitted edit to `backend/commands/executor.py` (+39 lines, lever `STRATEGIC_ORDERS_ARE_PRICED_BY_THE_ORDER = True`, md5 `1dd7c8a0…`), and 20 other files are modified. I touched nothing in the repo. My early probes measured the pre-fix board; my late ones measured the landed one, and I re-ran the decisive cases against **both positions of the sibling's own lever** so the before/after is clean.
>
> **The landed fix charges 1 AP for a general retreat, and refuses it outright at 0 AP.** Details below under *What The Filed Fix Would Break* — it is not hypothetical, it is running.

---

## What Reproduces

All three filed sentences reproduce on the pre-fix board through the real `POST /command` (TestClient, mock parser, fresh 1805 boot, France, turn 1, AP 4) — and the shape is **seven typed sentences, not two**, plus two personality tiers and a ninth route:

| | sentence | parse | AP | result |
|---|---|---|---|---|
| 1 | `Davout, hold Rhineland and wait` | `wait` / HOLD | **4→4** | `HOLD:Rhineland` standing; reply says *"(2 AP — a standing strategic order…)"* |
| 2 | `Ney, march to Lorraine and wait there` | `wait` / MOVE_TO | **4→4** | `MOVE_TO:Lorraine` standing **and Ney marched Rhineland→Lorraine** |
| 3 | `Davout, support Ney and wait` | `wait` / SUPPORT | **4→4** | `SUPPORT:Ney` standing |
| 4 | `Ney, wait, march to Lorraine` | `wait` / MOVE_TO | **4→4** | order + march — **a LEADING wait, not a suffix** |
| 5 | `Davout, hold Rhineland, wait for orders` | `wait` / HOLD | **4→4** | order |
| 6 | `Davout, support Ney and stand by` | `wait` / SUPPORT | **4→4** | order — `stand by` is the second keyword |
| 7 | `Ney, march to Lorraine and wait for reinforcements` | `wait` / MOVE_TO | **4→4** | order + march |
| 8 | `Soult, hold Lorraine and wait` (**literal**) | `wait` / HOLD | **4→4** | should be 1 AP |
| 9 | `Napoleon, hold Lorraine and wait` (**sovereign**) | `wait` / HOLD | **4→4** | should be 1 AP |
| 10 | CR-4 focus route: `Davout, fortify` then bare `hold Rhineland and wait` | `wait` / HOLD | **2→2** | order via `try_focus_reissue` |

Controls: `Davout, hold Rhineland` 4→2 · `Ney, march to Lorraine` 4→2 · `Soult, hold Lorraine` 4→3 · `Napoleon, hold Lorraine` 4→3 · `Davout, hold Rhineland and stay put` **4→2 (already fixed, as the row predicts)** · `Ney, pursue Mack and wait` 4→2 (parses `attack`, unaffected).

**The row understates the severity by a category.** It is not a 2-AP leak — it is a **total bypass of the AP pre-gate**. Measured at **AP = 0**:

```
AP=0  ok=True  'Ney, march to Lorraine and wait there'
AP=0  ok=True  'Davout, march to Franche-Comte and wait there'
AP=0  ok=True  'Lannes, march to Burgundy and wait there'
AP=0  ok=True  'Murat, march to Lorraine and wait there'
AP=0  ok=True  'Bernadotte, march to Swabia and wait there'
AP=0  ok=True  'Soult, hold Lorraine and wait'
FINAL AP = 0 · 5 standing orders created · 4 marshals MARCHED a province each
```
A player with a spent turn can still set every standing order **and move the army one hop**, unbounded. The non-free twin answers `Not enough actions! Need 2, have 0.`

## What Is False / Incomplete in the Row

- **"HOLD and MOVE_TO"** — SUPPORT is a third type, and there are **seven** typed shapes plus the CR-4 focus route (the row and the prior repro name 2 and 3).
- **The row frames it as the trailing `"and wait"` suffix.** It is not a suffix: `Ney, wait, march to Lorraine` (leading) and `…, wait for orders` / `…and stand by` all fire. The seam is `free_actions` membership, nothing about position.
- **The row's `already_filed`/scope misses the tiers.** The literal's and the sovereign's 1-AP discount is bypassed too — `strategic_order_ap()` is never consulted.
- **The row's own `fix_shape` is wrong in both halves** (the prior repro is right about this and I confirm it by measurement): option 1 double-charges, option 2 contradicts the row's own done-when. **And a third thing the row does not say: the naive reading of its ruling ships a regression** (below).
- **"add corpus rows"** is outstanding: the golden corpus (436 rows) has **0** rows for `and wait` / `wait there` / `wait for orders`. `stand by, Ney, move to Paris` and `Ney, wait for reinforcements` are the only neighbours, and neither carries a strategic type.

## The Real Seam

`backend/commands/executor.py :: CommandExecutor.execute`, the action-economy block:

```python
free_actions = ["status", "help", "end_turn", "unknown", "retreat", "wait", ...]   # 33 entries
action_costs_point = action not in free_actions      # <-- THE SEAM
if is_strategic_execution:
    action_costs_point = False
```

`action_costs_point` gates **both** the AP pre-gate (whose strategic branch is the only reader of `Marshal.strategic_order_ap`, `backend/models/marshal.py:847`) and the charge block (the only reader of `variable_action_cost`). `strategic_executor._execute_strategic_command` already returns `"variable_action_cost": strategic_cost` — **the order is priced correctly and the outer block never looks.**

**Blast-radius arithmetic (measured, not grepped).** Of the 33 `free_actions`, **30 are blocked at the parser** by `validation.NEVER_STRATEGIC_ACTIONS`. Only three can reach the executor with a `strategic_type`: **`wait`, `retreat`, `break_square`**. An exhaustive census of 2,357 command-shaped strings from `tests/*.py` + the golden corpus (589 of them parse strategic) finds **5** that are free-and-strategic — one `wait`, four `retreat`, zero `break_square`.

**Every path that reaches `_execute_strategic_command`, and its price today:**

| # | site | price today | must be |
|---|---|---|---|
| 1 | `executor.CommandExecutor.execute:2290` (typed player route) | **broken — the defect** | charge |
| 2 | `meta_executor.MetaExecutor._execute_post_objection:2124` | reads `variable_action_cost` but gated on a **verbatim duplicate** of `free_actions` | charge — but **measured unreachable**: `should_check_objection` excludes `is_strategic_command`, so a strategic parse never enters the tactical objection (instrumented across many geometries: the only calls carry `action='fortify', is_strategic=None`) |
| 3 | `strategic_executor._handle_strategic_objection_from_endpoint:2878` | **already correct** — `result.get("variable_action_cost", 2)`, no `free_actions` read at all | unchanged |
| 4 | `combat_executor._execute_attack:4911` (attack→PURSUE upgrade) | base verb `attack`, not free; has its own pre-check | unchanged |
| 5 | `movement_executor:541/568` + all `strategic.py` sites | carry `_strategic_execution: True` | **stay FREE** — measured: issue at 4→2, one per-turn tick leaves AP 2→2 |
| 6 | `jealousy.py:3684` | `_strategic_execution: True` | stay free |
| 7 | `enemy_ai.py:961/5734/7161` | `is_ai_command`; AI charges from its own `variable_action_cost` read at `enemy_ai.py:1268` | **already GR5-correct** |

Site 3 is the precedent: **the ruling is already implemented once, in the objection route.** Measured — `Davout, march to Swabia and wait there` and `Davout, march to Swabia` behave *identically* through `/respond_to_objection` (4→4→3, `MOVE_TO:Swabia`).

## What The Filed Fix Would Break — ⛔ AND DOES, RIGHT NOW

I simulated the naive shape (`strategic parse ⇒ action_costs_point = True`) before the sibling landed it, and then measured the **landed code** against its own lever. They are the same shape and produce the same result.

**`retreat` is the free verb the fix must not touch, and it does.** Six of 22 retreat phrasings parse `action == "retreat"` **with** a `strategic_type`:

| sentence | pre-fix | **shipped fix** | what it actually does |
|---|---|---|---|
| `withdraw from the alliance` | 4→**4** | 4→**3** | **a GENERAL RETREAT of all eight French marshals** (it does not break a treaty — WO-11 pinned `withdraw from` out of the break predicate) |
| `withdraw from the alliance` **at 0 AP** | 0→0, **retreat executes** | 0→0, **`ok=False`, `Not enough actions! Need 2, have 0`** | ⛔ **the army cannot retreat** |
| `fall back south` | 4→4 | 4→3 | `MOVE_TO:Franche-Comte` on Soult + march |
| `withdraw south` | 4→4 | 4→3 | same |
| `Ney, fall back south` | 4→4 | 4→3 | `MOVE_TO:Swabia` (toward the enemy — a separate pre-existing wart) |
| `Ney, withdraw south` | 4→4 | 4→3 | same |
| `Ney, fall back and observe Mack` | 4→4 | 4→3 | same |

`retreat` is the one entry in `free_actions` with an explicit design comment at the list itself (`executor.py:1199`, *"retreat is FREE (costs 0 actions - strategic withdrawal)"*). **Retreat exists for the moment you are out of options; the landed fix makes it unavailable exactly then.** Two of these six (`hold on, Ney, retreat`, `withdraw from the alliance`) live in `tests/test_wo_slice11_typed_route_residue.py` and the golden corpus — but **only as parse-level assertions**, which is why no pin catches this.

**Everything else the fix could have broken is measured clean.** Comparing each free-verb sentence with its non-free twin, these arms are byte-identical before and after (the charge only runs on `success`, and every one of these returns early or refuses):

- CR-2 clarification (`hold Rhineland and wait` → *"Which marshal shall hold Rhineland, Sire?"*, 4→4 in both)
- broken / retreat-recovery refusals · the road-law closed-destination refusal (`Ney, march to Brunswick and wait there`)
- F10 identical re-issue (`variable_action_cost: 0`) · PF-6 `hold your ground` · `scout … and remain there`
- `_strategic_execution` (the per-turn tick) — free by the ordering, which the landed edit gets right
- the counter-punch waiver (already excludes `is_strategic` and `attack` is never free)
- the AI (`is_player_action_check` / `is_player_action` are False; the AI's own charge already reads the order's price)

**One hazard the landed code leaves open even after the retreat exemption:** `_execute_strategic_command` returns `None` on no-world / no-marshal-name / marshal-not-found, and the command then falls through to ordinary routing where the charge would spend `world.use_action(action)` on a free verb with no `variable_action_cost`. That is precisely the mechanism of the `withdraw from the alliance` regression. Any future free verb that can carry a strategic type re-opens it.

## Pins That Flip

**ZERO — measured, not argued.** Sweep of **91 test files / 4,869 tests** (every file mentioning `actions_remaining`, `use_action`, `action_summary` or `admin_actions_remaining`, plus all `test_command_robustness_*`, `test_strategic*`, `test_wo_slice11*`, `test_fa_slice7*`, `test_pf*`, and the golden-corpus harness), run with the sibling's own lever ON and OFF in the child process:

```
LEVER=on : 3 failed, 4866 passed, 3 skipped
LEVER=off: 3 failed, 4866 passed, 3 skipped
diff of the FAILED/ERROR sets:  (empty)   -> NO PIN DIFFERENCE
```
The 3 failures are pre-existing cross-file pollution (`test_pt_a_regressions.py::TestTheHardStopRefusalThroughTheEndpoint` ×2 + one more); that file passes 31/31 in isolation.

This is also the reason the defect survived: **not one existing test drives any of the ten shapes.** The prior repro's table of "tests that would flip" is correct in its verdicts and I confirm it by execution rather than by reading.

⚠ Two methodology notes for whoever writes the pins:
- `action_info["cost"]` **under-reports every variable-cost action as 1** (measured: `Davout, hold Rhineland` spends 2, reports `{'cost': 1}`) because the charge loop overwrites `action_result` each iteration. Pin `world.actions_remaining`, never `action_info["cost"]`.
- The `_emit_series` replica is only deterministic with **`PYTHONHASHSEED=0` set in the parent environment**. Setting it inside the script is too late and produced a false divergence in my first run.

## Series / Harness Risk

**None, and the reason is measured.**

- `BASELINE_SERIES` reproduces **byte-for-byte** with the lever ON and OFF (40 turns, `SOVEREIGN_SEED=historical`, `PYTHONHASHSEED=0`, per-turn `random.seed(10_000+turn)`). Instrumented on `CommandExecutor.execute`: **1,157 calls, of which `strategic_AND_free` = 0**. The AI issues 290 `wait`, 4 `retreat` and 2 `break_square` commands and **not one carries a strategic type** — `grep -c "is_strategic\|strategic_type" backend/ai/enemy_ai.py` = **0**; the AI builds command dicts and never parses text. And the change is gated on `is_player_action_check` / `is_player_action`, both False for the AI, so it is player-only by construction as well as by measurement.
- **M1–M7**: `tests/test_combat_sweep_metrics.py` contains **zero** occurrences of `CommandExecutor`, `executor.execute`, `is_strategic`, `actions_remaining`, `end_turn` or `advance_turn` — it drives `CombatResolver` / `CombatExecutor` directly. Structurally unable to see the change. `test_combat_sweep_metrics.py` + `test_ai_intent_threat_migration.py` = **29 passed under both lever positions**.

## Recommended Build Shape

The landed block is right in its rule, its siting (above the `is_strategic_execution` override) and its lever. **It needs one more clause and three more things.**

1. **Add the retreat exemption** — `and action != "retreat"`. Measured on the landed code: this restores all six retreat phrasings to 4→4 and the 0-AP general retreat to `ok=True`, while keeping **every** intended positive (7 sentences 4→2, Soult/Napoleon 4→3, the 1-AP and 0-AP refusals). Exactly four lines differ from the shipped behaviour, all of them the regression. State the rule in the comment rather than listing a verb: *a standing order is priced by the order — except a retreat, which is free by design even when the strategic layer reads a march out of it* (`executor.py:1199`; and see `A_BARE_RETREAT_IS_A_RETREAT` in `parser.py`, which already de-upgrades only the **generic**-target case and is why these six slip through).
2. **Pin all ten shapes on the real route**, AP before/after, plus the four controls, the two tiers, `is_strategic_execution` staying free, the six retreat phrasings staying free, **and the 0-AP arms** (`bypass@0AP` refused; `withdraw from the alliance` at 0 AP still executing). The 0-AP arms are the ones that make the pins falsifiable — the AP-4 arms pass under a fix that only touches the charge and leaves the pre-gate open, which would create the order and *then* refuse.
3. **Add the corpus rows** the ruling asks for — there are none today.
4. **`meta_executor._execute_post_objection:2086` holds a verbatim duplicate of the 33-entry `free_actions` literal.** It is measured unreachable with a strategic type, so patch it for one rule or **state the reason on the row** — do not leave it silently divergent. (A single shared constant would be the honest fix, and `strategic_executor:2878` is the third copy of this pricing decision that already gets it right.)

**Filed in passing, not FA-R3:** `Davout, hold your ground and wait` is *refused* (*"I could not make out a destination"*) while `Davout, hold your ground` alone creates a 2-AP HOLD — the trailing wait clause defeats PF-6's stand-fast idiom at the destination read. And `withdraw from the alliance` executing a general retreat rather than a treaty action is a live wart of its own.

---

**Probes** (all read-only, all under `…/scratchpad/s14/B_free_verb/`): `p1_repro.py` (the three sentences + controls) · `p2_blast.py` (set arithmetic + 22-sentence battery) · `p3_holes.py` (six free-vs-non-free twin comparisons) · `p4_zeroap_and_objection.py` (the 0-AP exploit) · `p5_objection_route.py` (both objection routes) · `p7_census.py` (2,357-string exhaustive census) · `p8_retreat_hole.py` (**the regression**) · `p9_series.py` / `p11_series_lever.py` (instrumented 40-turn series) · `p12_final.py` (before/after on the landed fix) · `p13_retreat_scan.py` (22 retreat phrasings) · `p15_recommended.py` (the recommended shape) · harnesses `far3_lever.py` (flips the sibling's lever in the child — the safe idiom), `far3_patch.py`, `far3_fixarm.py` (read-source-and-patch-in-memory module loaders; the repo was never written to).