Repo verified untouched (`git status --porcelain` empty, HEAD still `9ef38da8`). All probes live under the scratch dir.

---

# FA-21 and FA-35 — reproduction report

Probe directory: `C:/Users/User/AppData/Local/Temp/claude/C--Users-User-PycharmProjects-project-sovereign-map/d3a697cd-1535-475d-bd1b-457545b1c421/scratchpad/s14/I_ai_demands/`

---

## FA-21 — purse-blind bilateral P8 demands

### VERDICT: **REPRODUCED, and WIDER than the row or the review round says.** The defect is real and every cited number is exact. But the fix needs **three** seams, not one, and the third one — the acceptance formula's gold pricing — is the one that actually caps the demand, is named nowhere, and is **completely unpinned by the suite**.

### What Reproduces (`probe_fa21_a.py`)

On `tests/fixtures/playtest_saves/fixture_t20_ambient.json`, every figure in `_corrected` is exact:

| quantity | measured |
|---|---|
| `_get_war_score_for_nation("Britain","France")` | **54** |
| `world.gold` / `nation_gold["France"]` | **17,487** |
| `_build_proposal_terms(... "harsh_peace" ...)["demands"]` | `[{'type':'gold_lump','value':270}]` |
| `calculate_acceptance` score | **53** |
| after `_reduce_p8_demands` | **270**, unchanged, `_force_send` absent |
| `_settlement_offer_build_terms` (EC-W4) same state, age 19 | **6,233** (cap `0.40×17,487` = **6,994**) |
| `ai_proposal_cooldowns["Britain\|harsh_peace"]` | **5** — the arm did fire in the ambient run |

The row's line numbers hold too: `ai_diplomacy.py:893-897` is verbatim `gold_demand = max(200, int(war_score * 5 * gold_mult))`; `:913-960` is `_reduce_p8_demands`; `:1546-1552` is the P8 gate; `:3230-3255` the constants; `:3387-3396` the purse formula.

### The review round's reducer claim: **TRUE, and here is the exact boundary** (`probe_fa21_b.py`, `probe_fa21_c.py`)

`_reduce_p8_demands` halves **once**, not iteratively. On the t20 state:

```
L <=  491  ->  unchanged            (acc 20 at 491; acc 19 at 492)
492..983   ->  halved and kept      (983 -> 491)
L >=  984  ->  200 + _force_send=True
```

Verified at the boundary: `L=983 -> 491`, `L=984 -> [{'gold_lump': 200}] force_send=True`.

And **`calculate_acceptance` never reads the payer's treasury at all.** Lump 2,000 scores **−37** at treasury 0, 200, 2,000, 17,487, 100,000 *and* 900,000 — six chests, one score. Lump 6,233 → 200 + `_force_send` at every one of them. So the review round's "identically at a 200g chest and a 900,000g one" is confirmed, and its cause is bigger than stated: purse-blindness is in the *scorer*, not just the builder.

### What Is False / missing from the row

1. **`fix_shape` ships a SMALLER demand, measured in the wild 5 times out of 5** (see the flip experiment below). This is FA-N51, now quantified.
2. **The row calls it "ONE seam". It is three.** The third is the binding one and nobody has named it.
3. The row's `behaviour_test` says "tests/test_econ_war_coupling.py: … assert gold_lump ≥ 0.15×France treasury". That file has **no EC-W4 amount pin at all** — grep finds only a `# EC-W4 (player-ask fraction)` section header. The test would be brand new, and as written it is unsatisfiable (see #4).
4. **The bilateral channel cannot deliver a purse-scaled indemnity at all.** `DEMAND_VALUES["gold_lump"] = -3/100` (`diplomacy.py:312`) is linear and **uncapped**, while every other harsh term saturates (`harshness_penalty` caps at −40). Against the AI's own `score < 20` self-filter (`ai_diplomacy.py:1761`) that puts a hard ceiling of **491 gold** on any deliverable bilateral lump on this state — 2.8% of the treasury, below the row's own 0.15× floor of 2,623. Even at war score **100** the stock formula's 500 already scores 18 and gets halved.
   The multilateral path escapes this because its harshness **saturates**: gold weighs `0.08/100` into raw harshness, `HARSHNESS_NORMALIZATION_CEILING = 1.5`, `HARSHNESS_PENALTY_MAX = 45` — so the settlement scorer stops caring above **1,875 gold** and 6,233 is free. `deal_balance` on the bilateral side never saturates. *That asymmetry is the whole defect.*

### The Real Seams (by symbol)

| # | symbol | file | what it owns |
|---|---|---|---|
| 1 | `_build_proposal_terms`, `harsh_peace` arm | `backend/game_logic/ai_diplomacy.py` | the amount |
| 2 | `_reduce_p8_demands` | same | the floor it collapses to (`200`, `_force_send`) |
| 3 | **`DEMAND_VALUES["gold_lump"]`** + the `score < 20` self-filter | `backend/game_logic/diplomacy.py:312`, `ai_diplomacy.py:1761` | **the ceiling** |

Shared helper the row wants: extract the EC-W4 body out of `_settlement_offer_build_terms` (lines `3387-3396`) into e.g. `ai_diplomacy.purse_scaled_indemnity(world, payer, war_score, war_age)` and call it from both. That is correct and cheap — but inert without seams 2 and 3.

### What The Filed Fix Would Break — the three-arm flip experiment (`series_flip_fa21.py`)

40-turn ambient board, `SOVEREIGN_SEED=historical`, `PYTHONHASHSEED=0`. **P8 fires 5 times** — turns 15, 17, 24, 31, 38 — so this is not vacuous evidence.

| turn | payer purse | arm 0 built → delivered | arm A (filed fix) built → delivered | arm B (fix + purse-aware reducer) |
|---|---|---|---|---|
| 15 | 18,108 | 220 → **220** | 4,976 → **200** ⛔ | 4,976 → **2,716** |
| 17 | 15,800 | 352 → **352** | 4,750 → **200** ⛔ | 4,750 → **2,375** |
| 24 | 6,650 | 532 → **266** | 2,660 → **200** ⛔ | 2,660 → **1,330** |
| 31 | 3,571 | 555 → **277** | 1,428 → **200** ⛔ | 1,428 → **714** |
| 38 | 3,919 | 487 → **243** | 1,567 → **200** ⛔ | 1,567 → **783** |

**Arm A is strictly worse than the status quo on all five occasions.** (My arm-A war-age term measured 0 — the probe's `war_instances` lookup missed. The real fix adds `age × 50`, which makes the amounts *larger* and pushes them further above the 984 collapse boundary. The conclusion only hardens.)

Also worth knowing before choosing arm B: a rejected AI proposal costs no relations — `_handle_reject_ai_proposal` (`diplomatic_executor.py:6533`) applies a cooldown, a DD8 schemer marker and a refusal record, nothing else. So a `_force_send` demand the player refuses is *safe* — but it silently converts harsh_peace from "a cheap peace the player might take" into "a demand the player refuses". That is a design change the row does not raise.

### Pins That Flip (`probe_pins.py`; narrow selections run)

Baseline: `test_da1_ai_intelligence.py + test_diplo_refinement_wave2.py + test_econ_war_coupling.py + test_wpsd_legibility_ai.py + test_common_peace_acceptance.py` → **242 passed**.

`TestA4GoldFormula` uses `make_world()` = legacy `WorldState(player_nation="France")`, whose France chest is **800**. EC-W4 on 800: scaled = `500 + ws×40 + 120`, cap = `0.40×800` = **320**. The cap binds in every case:

| test | pinned | EC-W4 | flips |
|---|---|---|---|
| `test_floor_200` (ws 30) | 200 | 320 | **YES** |
| `test_scaling_at_50` | 250 | 320 | **YES** |
| `test_scaling_at_80` | 400 | 320 | **YES** |
| `test_scaling_at_100` | 500 | 320 | **YES** |
| `test_hawk_multiplier` | 375 | 320 | **YES** |
| `test_dove_multiplier` | 300 | 320 | **YES** |
| `test_floor_with_low_war_score` (ws 10) | 200 | 320 | **YES** |
| `test_old_formula_would_give_different_values` | `< 500` | 320 | survives (by accident) |

Plus **`tests/test_diplo_refinement_wave2.py::test_gold_scales_with_war_score`**, which is the important one: it asserts `gold_50 == 250`, `gold_80 == 400` **and `gold_80 > gold_50`**. Under the filed fix both are 320 — **the demand stops being monotonic in war score on a poor payer.** That is a design bug, not test churn: the purse cap eats the entire war-score signal.

`TestA1Reduction`'s five fallback/floor pins survive an arm-B reducer on the legacy world (`0.15 × 800 = 120`, `max(200,120) = 200`).

**And a warning for the builder: seam 3 has no safety net.** Loading a read-only pytest plugin that softens `DEMAND_VALUES["gold_lump"]` 5× (−0.03 → −0.006, verified applied: `RATE_IS -0.006`) and running all **41** `gold_lump`-touching test files leaves **2,032 / 2,032 passing**. Nothing in the suite pins how the bilateral acceptance formula prices gold.

### Series / Harness Risk

- **`BASELINE_SERIES`: byte-identical on arms 0, A and B**, and the province map is identical too. Instrumentation faithfulness proven — an untouched instrumented run reproduces `[70, 68, …, 0]` exactly, plus `PROVINCES France 5 / Austria 26 / Britain 21 / Russia 10` and `FALLEN {Deroy}`, matching the record in the test file's own comment block.
- **Why it does not move, stated rather than assumed:** the ambient player never answers a diplomatic proposal, so the demand amount is never applied; and `_force_send` keeps the delivery count at 5 in every arm. **No re-record needed** — and this time the byte-identity is *evidence*, because the changed path fires five times with amounts moving 20×.
- **M1–M7: unreachable.** `tests/test_combat_sweep_metrics.py` (639 lines) contains **zero** occurrences of `EnemyAI`, `end_turn`, `advance_turn`, `process_nation_turn`, `ai_diplomacy` or `process_diplomatic`. Byte-identity there is structural and worth nothing as evidence.

### Recommended Build Shape

Three levers, one slice, flip-attributed:

1. `PURSE_SCALED_BILATERAL_INDEMNITY` — extract `purse_scaled_indemnity(world, payer, war_score, war_age)` from `_settlement_offer_build_terms:3387-3396`; both call it. Re-bless the 8 exact-value pins **and add a monotonicity pin** (`demand(80) > demand(50)` on a purse where the cap does not bind) that the old formula also satisfied.
2. `P8_REDUCER_READS_THE_PURSE` — `_reduce_p8_demands`'s halve floor and fallback become `max(200, int(payer_treasury × SETTLEMENT_OFFER_TREASURY_FRACTION))` rather than a flat 200. Keep the flat 200 when the payer is broke, so the five `TestA1Reduction` fallback pins stay green.
3. **Decide seam 3 explicitly and write the decision down.** Either (a) accept that a real indemnity is a demand the player refuses (`_force_send` carries it; no scorer change; blast radius zero) — the cheap, honest option; or (b) make `gold_lump` price relative to the payer's purse in `calculate_acceptance`, which is the *correct* model but touches 2,032 unpinned tests and every diplomatic surface. **Do not do (b) silently** — the fact that a 5× rate change reds nothing means a mistake there is invisible.

Do not ship 1 without 2. Arm A is the regression.

---

## FA-35 — the P4 target-worth floor

### VERDICT: **REFUTED as filed; a smaller residual is REAL but at a different seam — and the row's own fix shape would ship a deadlock.**

### What Reproduces (`probe_fa35_repro.py`, `probe_fa35_colocated_cf.py`)

On the row's own geometry (1805 board; Charles 24,724 + John 7,058 + Mack 22,589 all at a French-held Piedmont with a 500-man Massena), current tree:

```
turn 2:  1 action.  Charles attacks Massena 500 -> 249.  The other two corps do nothing.
turn 3:  4 actions. Charles kills him on the SECOND battle -
         "No word came for Massena, cornered at Piedmont - the enemy did not wait.
          [!] MARSHAL CAPTURED - Massena is taken by Austria at Piedmont!"
         then John takes Rome, Mack takes Milan, Charles takes Provence.
```

**Two battles, two turns.** The slice-2 note ("with FA-1 landed the stub resolves in ≤2 battles") is confirmed by measurement. The row's "three Austrian corps spent four turns killing 58 men", "8–11 full AI actions", and "only AFTER he was destroyed did John march" **do not reproduce**.

### The residual, measured with a counterfactual

Identical board, 3 turns, everything else held:

| arm | actions/turn | total actions | Austria's provinces at the end |
|---|---|---|---|
| a 500-man stub co-located | 1, 4, 4 | **9** | **13** |
| no French corps at all | 4, 4, 4 | **12** | **15** |

**One 500-man remnant costs Austria 3 of 12 actions and 2 provinces — all of it in the first turn.** That is real, and it is a third of what the row claims.

### The Real Seam (and it is not P4)

Not `enemy_ai.py:2739` (`enemy.strength > 0`) and not `_pick_personality_target`'s `max(attackable, key=ratio)`. Slice 2 already stopped the other corps *attacking* — `_engageable_enemies` (`enemy_ai.py:2785`) carries the STUB latch against `STUB_STRENGTH_FLOOR = 1000` and is consumed at all four engagement seams (`:1710` P0, `:3198` P4's engaged block, `:4911` and `:5013` P8's engaged arms).

What freezes them is the **engaged rule in the executor**, which computes `enemies_here` with `strength > 0` as its only floor:

- `MovementExecutor._execute_move` — `movement_executor.py:230-242` ("Cannot advance while engaged with enemy forces")
- same, strategic-march arm — `movement_executor.py:326-332`
- `CombatExecutor._execute_attack` — `combat_executor.py:4960-4986` ("Cannot attack elsewhere while engaged")
- `strategic_executor.py:561`
- `TacticalExecutor` fortify — `tactical_executor.py:335-348`
- and `enemy_ai.py:1714-1731`, whose own `P0_BRAKED_CORPS_HOLDS` comment says exactly this: *"the executor's engaged rule refuses every attack-elsewhere and every advance while ANY at-war corps shares the province — remnant included"*.

Teaching **that** rule the floor is GR5-symmetric — it would also free the player's corps from being pinned by a 58-man enemy remnant. That is a genuine player-facing rule change and deserves a gate line, not a quiet AI tweak.

### What The Filed Fix Would Break — **it deadlocks**

The row: *"an enemy below a floor … is not a battle target but a CAPTURE: the co-located corps secures the province (the existing `_attempt_region_capture`/capitulation path)"*.

Both capture rungs refuse while **any** hostile marshal stands there, at **any** strength:

- **P-1**, `_evaluate_marshal` `enemy_ai.py:1659-1662`: `enemies_here = world.get_live_visible_enemies_in_region(...)` … `if not enemies_here and not has_garrison:`
- **P4.5**, `_find_undefended_capture` `enemy_ai.py:3757-3761`: `defenders = self._get_hostile_marshals_in_region(...)` … `if defenders: skip`

So routing a sub-floor enemy away from the attack rung and toward a capture that will not fire leaves the stub **alive forever and the province permanently un-takeable**. That is the direct answer to "can an enemy stub below the floor now be un-killable, so a province never changes hands" — **yes, exactly that**, unless the capture rungs learn the same floor in the same slice, which is a *new* rule (taking a province off a living defender without a battle), not "the existing path".

### The ranged arm reproduces but is not a defect (`probe_fa35_counterfactual.py`, `probe_fa35_ranged.py`)

P4 picks the stub in **6 of 6** combinations (aggressive and cautious × stub 500/58/5,000 × alternative = undefended province or a 12,000-man corps). But the counterfactual says it costs nothing:

| | end owners | Charles ends | men |
|---|---|---|---|
| 58-man stub at Bohemia | Bohemia **Austria**, Franconia France | Franconia | 35,499 |
| no stub | Bohemia **Austria**, Franconia France | Franconia | 35,381 |

Identical outcome, 118 more men lost. The stub was standing on the province he wanted; killing it *is* taking it. The row's premise — that the stub is a detour from an open road — holds only for the **co-located** case.

### Corrections to the row

- **Wrong seam** (as the Sept-2 verification already flagged): P4's `strength > 0` and the max-ratio pick are not the cause on the current tree.
- **`already_filed` is stale**: the row is already CLOSED at its real seam by slice 2, and `STUB_STRENGTH_FLOOR = 1000` exists.
- **The cited precedent is the wrong quantity**: "the same floor war-score already uses at `diplomacy.py:9418-9420`" is the **1,000-casualty** war-score gate (*"Only battles with >= 1000 total casualties count for war score"*), a casualty threshold, not an army-size floor.

### Pins That Flip

Baseline: `test_fa_slice2_no_word_came + test_fa_slice2r + test_fa_slice4 + test_fa_slice4r + test_enemy_ai{,_behavior,_bugs}` → **327 passed**.

- `test_fa_slice2…::test_a_real_army_is_not_a_stub` pins **5,000** as above the floor → any raise past 5,000 reds it.
- `test_fa_slice4…::test_a_strike_outranks_the_square` pins a **4,000**-man stub as a legitimate P4 strike → a floor above 4,000 reds it.
- `test_fa_slice4…::test_the_range_arm_prices_the_field` already handles the ranged-stub concern for the stagnation breaker by **pricing the field**, not by flooring (FA-8's rider) — that is the precedent to follow.
- `test_fa_slice2…::test_the_stub_latch_frees_the_rest_of_the_nation` asserts only that the second corps does **not attack**. It never asserts he does anything useful. **That is why this residual survived slice 2's own pin**, and the new pin must assert a move/capture, not an absence.

### Series / Harness Risk — the two candidate fixes differ completely

**Engaged-arm fix (the real residual): measurably INERT.** Over 40 ambient turns, `_engageable_enemies` is called **4,933** times; `engaged_with_stub` = **0** and `brakes_dropped_stub` = **0** (the stub latch has *never fired* on the ambient board; the 2 drops were pair-brake drops). A direct end-of-turn state scan agrees: **4** `(turn, corps)` pairs are co-located with any hostile, **0** pinned only by sub-1,000 remnants. `BASELINE_SERIES` cannot move — honest zero, written predicate.

**Ranged-arm fix (the row's filed seam): MOVES THE SERIES, materially.** Flip arm R refuses a P4 attack on a sub-1,000 target at range — **4 refusals in 40 turns** (Castanos→Paget 875 t11, →431 t12; Charles→Bernadotte 991 t26 ×2):

```
arm 0: ... 25, 22, 19, 16,  3,  0,  0, 0, 0, 0, 2, 0 ...
arm R: ... 25, 27, 27, 24, 21, 18,  5, 2, 0, 0, 0, 0 ...   diverges at index 21
```

and the board changes hands: **Austria 26 → 21, Britain 21 → 26, France 5 → 6, Spain 9 → 10, Switzerland 1 → 2, Holland (3 provinces) eliminated entirely.** Four decisions, a different Europe. That is a re-record *and* a balance swing that belongs beside FA-D27.

Context from the same instrumented run: of **117** AI attack decisions in 40 turns, exactly **one** targets a sub-1,000 corps (0.85%); none below 500; only one marshal (Bernadotte, 956, t41) ever ends a turn below 1,000.

**M1–M7: unreachable**, same structural reason as FA-21.

### Recommended Build Shape

**Do not build the filed P4 floor.** It deadlocks the capture path, it fires 4 times in 40 turns, and those 4 firings cost Austria five provinces.

If slice 14 wants the residual closed, build it at the engaged rule, behind one lever, as the *smallest* thing that is true:

- `ENGAGED_RULE_READS_THE_STUB` — a corps whose only at-war co-residents are **all** below `STUB_STRENGTH_FLOOR` **and** already engaged this turn by a fellow of its own nation is not "engaged": the five executor seams above let it march, advance or capture. Symmetric (it frees the player too — say so in the record), zero new fields, single source (a predicate beside `_engageable_enemies` that all five seams import).
- Then `P0_BRAKED_CORPS_HOLDS` can fall through to P4.5/P7 as slice 2 originally intended, because the executor will no longer refuse the order — which is the exact reason the review round had to make him hold.
- Pin it on the counterfactual, not on an absence: three corps co-located with a 500-man stub must produce **≥ 3 actions** and take **≥ 1 adjacent province** in the same turn (measured today: 1 action, 0 provinces).
- Series: no re-record expected, with the measured predicate above written on the row (0 of 4,933). Verify with a flip arm anyway.

If the ranged pick is to be touched at all, follow `test_the_range_arm_prices_the_field`: **price** the target's field rather than floor its strength — and budget a `BASELINE_SERIES` re-record with a flip-arm attribution, because arm R already shows it is worth five provinces.

---

### Probe files

| file | what it measures |
|---|---|
| `probe_fa21_a.py` | FA-21 on the t20 fixture — every cited number |
| `probe_fa21_b.py` | the reducer's collapse; acceptance is purse-blind (6 chests, one score) |
| `probe_fa21_c.py` | the 491 / 984 boundaries; EC-W4 vs the deliverable ceiling |
| `series_flip_fa21.py` | three-arm 40-turn flip (0 / filed fix / purse-aware reducer) |
| `probe_pins.py` | the 7 `TestA4GoldFormula` pins that flip and what to |
| `plugin_softgold.py` | read-only blast-radius probe: the gold rate is unpinned (2,032/2,032 green at 5× softer) |
| `series_probe.py` | faithful instrumented replica of `_emit_series` (reproduces `BASELINE_SERIES`) |
| `series_probe_fa35.py` | 117 attacks / 1 sub-1,000 target over 40 turns |
| `series_probe_engaged.py` | 4,933 brake calls, 0 engaged-with-stub |
| `series_probe_engaged_state.py` | end-of-turn state scan: 0 stub-pinned corps |
| `probe_fa35_repro.py` | the row's own geometry — 2 battles, 2 turns, captured |
| `probe_fa35_colocated_cf.py` | the counterfactual: 3 actions and 2 provinces |
| `probe_fa35_ranged.py` | P4 picks the stub 6/6 combinations |
| `probe_fa35_counterfactual.py` | …and it costs 118 men and nothing else |
| `series_flip_fa35.py` | ranged floor moves the series at index 21; Austria −5, Britain +5 |