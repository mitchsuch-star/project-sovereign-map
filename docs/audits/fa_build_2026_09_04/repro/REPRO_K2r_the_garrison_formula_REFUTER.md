Checked my own candidate finding and killed it: `_garrison_refusal_probe` refuses when `region.garrison_strength > 0`, so no overwrite is possible. Writing up.

---

# Refutation of the FA-D28 reproduction report

Probes: `…/scratchpad/s14/refute_A_garrison/` — `r1_resolver.py` · `r2_landed_trace.py` · `r3_fixture.py` · `r4_player_path.py` · `r5_misc.py` · `r6_fixtures.py` · plugins `zeroplug.py` / `countplug.py`. Working tree is dirty (the builder's FA-D28 + FA-R5 landed at 20:16); I reproduced **both arms** via the landed flip levers — `GARRISON_LOSS_FLOOR_READS_THE_GARRISON=False, GARRISON_ASSAULT_LOSS_FLOOR=0.02` is byte-identical to HEAD's `max(attacker_losses, int(marshal.strength * 0.02))`. I wrote nothing to the repo.

---

## 1. The headline — CONFIRMED, to the digit

**CLAIM** 40,000 cautious vs a 3,000 detachment on plains: 13 assaults, 40,000 → 29,844, lost 10,156 (25.4%); per-assault 800/784/768…/1,550 with the last split "627 combat + 923 march".

**MY MEASUREMENT** (`r1_resolver.py`, real resolver on the real 1805 board, Lorraine = plains, no fort): 13 assaults, 40,000 → 29,844, **lost 10,156, 25.4%**, trace `800, 784, 768, 752, 737, 723, 708, 694, 680, 667, 653, 640, 1550`. Combat-only sum = **9,233**, matching the resolver comment; 10,156 − 9,233 = **923** march.

**VERDICT: CONFIRMED.** And stronger than they claimed: it is **fixture-independent**. Real Kutuzov gives 10,156; real Ney (aggressive, modifier 1.15 → 1.035 → 0.92) also gives **10,156** — because in this regime every man is paid by the floor `int(strength*0.02)`, which does not read the modifier.

## 2. The mechanism — CONFIRMED and it is the key to everything else

**CLAIM** the floor binds iff effective attacker > 12.5× effective garrison.

**MY MEASUREMENT** Derived: floor binds iff `0.02 > min(0.35, g_eff/a_eff*0.25)`, i.e. `a_eff > 12.5·g_eff`. Observed in the trace. **CONFIRMED** — and it is the diagnostic that explains every number dispute below: *where the floor binds, the figure is modifier-independent and we agree exactly; where the proportional term binds, the figure is modifier- and placement-dependent and we differ.*

## 3. ⛔ "GARRISON_ASSAULT_LOSS_FLOOR is INERT" (§8 P1) — **REFUTED**

**CLAIM** "Setting it to zero changes nothing. It first bites at 0.30… algebraically the floor binds iff `F > (1+terrain)(1+fort) × 0.25 / modifier`, i.e. `F > 0.25` on open ground — so the blessed 0.02 is dead code, the stated band is empty, **any mutation of `0.02` will come back INERT, and any test asserting the floor's magnitude will be vacuous**."

**MY MEASUREMENT** That derivation silently drops the `min(0.35, …)` **cap** on `attacker_damage_ratio`. There are two regimes:

| regime | condition | proportional term | floor binds iff |
|---|---|---|---|
| uncapped | `g_eff < 1.4·a_eff` | `strength · g_eff/a_eff · 0.25` | `F > 0.25(1+t)(1+f)/mod` — their case, 0.02 never binds |
| **capped** | `g_eff ≥ 1.4·a_eff` | `strength · 0.35` | **`garrison/strength > 0.35/F` = 17.5 at F=0.02** |

Measured end-to-end through the **player's own typed `attack Vienna`** (`r4_player_path.py`, `CommandExecutor.execute`, shipped board, Vienna capital garrison 25,000, `reached_resolver=True` asserted on every row):

```
atk=  500   F=0.00 -> 175    F=0.02 -> 500    DIFFERS
atk=1,000   F=0.00 -> 350    F=0.02 -> 500    DIFFERS
atk=1,400   F=0.00 -> 489    F=0.02 -> 500    DIFFERS
atk=1,500   F=0.00 -> 525    F=0.02 -> 525    same     <- crossover at 25,000/17.5 = 1,428
atk=40,000  F=0.00 -> 5,328  F=0.02 -> 5,328  same     <- their regime
```

And the **landed test file already pins it**: `TestTheGarrisonFloorReadsTheGarrison::test_the_floor_still_binds_for_a_weak_attacker` (1,000 vs 25,000, asserts `after > before`). Under my `zeroplug` `FLOOR_ARM=none` (F=0.0) that test goes **RED**, along with four siblings.

**VERDICT: REFUTED.** The constant is load-bearing, player-reachable, currently pinned, and mutation-killable. It is inert only in the over-match regime the reporter swept.

**Consequence for the build:** §9 recommendation 2 — *"drop `GARRISON_ASSAULT_LOSS_FLOOR` and write `max(attacker_losses, 1)`"* — is **a live balance change, not a cleanup**. It cuts a 500-man remnant's assault on Vienna from 500 to **175 (−65%)**, deletes the pin above, and makes the anti-stalemate guarantee one-sided. Do not take it.

## 4. The "after" numbers 2,814 / 7,668 / 14,483 — **REFUTED (unreproducible in any fixture)**

**CLAIM** §4 and §8: the re-base gives 2,814 / 7,668 / 14,483, and `p15` "confirms [the landed code] is arithmetically identical to my floor arm (2,814 / 7,668)".

**MY MEASUREMENT** Four number-sets exist for "case A", all internally correct:

| fixture | HEAD | LANDED |
|---|---|---|
| Europe board / Lorraine (plains) — *the resolver comment's fixture* | 10,156 · 12,830 · 17,003 | **2,486 · 6,363 · 11,903** |
| resolver comment, combat-only | 9,233 · 12,727 · 17,803 | 1,496 · 5,996 · 12,496 ✓ consistent with mine |
| legacy world / Paris (urban) — *the landed pins' fixture* | 10,234 · 14,156 · 20,184 | **2,942 · 8,180 · 15,962** (reproduced to the digit) |
| **the reporter's** | 10,156 · 13,649 · 18,924 | **2,814 · 7,668 · 14,483** — matches nothing |

Sensitivity measured directly: real Ney gives **2,354**; adjacent start provinces give **2,542–2,752** (Brabant/Franche-Comté/Nivernais/Orléanais/Rhineland/Swabia). `_calculate_movement_attrition` has **no RNG** (`int(marshal.strength * rate)`), so this is fixture drift, not noise.

**VERDICT: REFUTED.** §9 recommendation 3's pin *"10,156 → 2,814"* would be written on a figure that exists on neither fixture. **The 10,156 half is safe to pin; the 2,814 half must not be.** Their §1 HEAD figures for garrison 12,000 / 25,000 (13,649 / 18,924) are likewise NARROWED to fixture-specific — I get 12,830 / 17,003.

## 5. "25.4% flat at 20k–200k" (§9 rec 3) — **REFUTED at the low end**

**CLAIM** scale-invariance pin over 20k–200k.

**MY MEASUREMENT** (`r5_misc.py`): 10,000 → **28.1%**; 20,000 → **24.6%**; 40,000/80,000/120,000/200,000 → **25.4% exactly** (50,805 at 200,000, matching them). Reason: 20,000/3,000 = 6.7× is **below** the 12.5× threshold, so those rows are proportional-driven and fixture-dependent — their own §1 table already prints 25.3% there, contradicting §9's "flat".

**VERDICT: NARROWED.** The flat region starts at 40,000, not 20,000. Headline ("a 200,000-man army loses 50,805 men to 3,000 defenders", "a flat quarter") **CONFIRMED**.

## 6. "the three capital geometries are byte-identical" negative control (§9 rec 3) — **REFUTED as worded**

**MY MEASUREMENT** (`r6_fixtures.py`, legacy Paris urban, one assault):

```
capital 10,000 vs 250,000 : HEAD 5,000  LANDED 3,000   *** DIFFERS ***
capital 12,000 vs 250,000 : HEAD 5,000  LANDED 3,600   *** DIFFERS ***
capital 10/12/25,000 vs 40,000 and 120,000 : identical
```

**VERDICT: REFUTED.** Byte-identity on a capital is a property of the **attacker's size** (over-match < 12.5×), not of the garrison's kind. The landed pin `test_the_lever_down_restores_the_attacker_s_own_strength` uses exactly the 250,000-vs-10,000 case — the right choice, and the direct counterexample to the proposed control.

## 7. Claims I re-measured and CONFIRMED

| claim | my measurement |
|---|---|
| M1–M7 makes **0** resolver calls | `countplug` over `test_combat_sweep_metrics.py`: **0**; control `test_garrison_system.py`: **12**. `grep -c garrison` on M1–M7 = 0. **CONFIRMED** |
| single source, two callers | `combat_executor.py:5171`, `naval_executor.py:403`; `game_logic/combat.py` has **0** "garrison"; one floor site at HEAD:2954. **CONFIRMED** |
| `test_attacker_takes_at_least_2pct_losses` is vacuous | **CONFIRMED and wider** — the *whole* 34-test file is green under all four arms including `none_head` (mechanic entirely deleted) |
| 3,000 is the only detachment size | **CONFIRMED and strengthened** — `_garrison_refusal_probe` refuses when `region.garrison_strength > 0`, so no overwrite path exists. Boot board: 0 detachments; capitals 10k×11 / 15k×4 / 25k×5; exactly two non-capital non-detachment 12,000 (Normandy, Flanders) |
| ⌈log₂N⌉+1 assaults | holds 1,000–25,000; breaks at 50,000 (**18** vs 17); at 100,000 the 40,000 corps is annihilated. **CONFIRMED** |
| literal reading annihilates the corps | F=1.0: 3,000 → 7,021 · 12,000 → 24,161 · 25,000 → **3 assaults, 40,000 lost**. Exact match. **CONFIRMED** |
| AI rung never reads the cost | `_find_garrison_attack` gates on `strength/garrison_effective >= threshold` only. **CONFIRMED** (see §9b for the caveat) |

## 8. Stale

§8 P3 *"the tree is currently red — `test_the_log_type_count_is_unchanged` fails"*: **now passes** (checked 20:49; `combat_executor.py` unchanged since 20:16). The builder took `CAMPAIGN_LOG_TYPES` 160 → 161 for `garrison_assault` and updated the ten pins. **STALE, not wrong at the time.**

## 9. Not verified by me — do not treat as established

The entire ambient-board section (§2b, §7): "6 garrison assaults in 40 turns, zero against a detachment", "effective odds 1.51–3.81:1", "`BASELINE_SERIES` byte-identical across all arms", "17 turn-backs", the `p13` wrong-signature-spy perturbation. **I ran no 40-turn campaign**: the tree carries another agent's in-flight FA-D28/FA-R5 diff, so any series number I took would be attributable to their edit, not to the fix. Two things a builder should carry:

- **(a) Their byte-identity reason is one-directional and fragile.** It rests on no ambient assault exceeding 12.5× effective over-match. But they also report the AI *creating six 3,000-man detachments*. A 40,000-man corps against one of those is **13.3×** — the floor binds and the series moves. Byte-identity here is a property of one seed's routing, not of the fix. (In the *other* direction they are structurally safe: `ATTACK_THRESHOLDS` bottom out near 0.6, far above 1/17.5, so an AI assault can never enter the weak regime where the *landed* floor binds.)

## 10. What the reporter missed — a builder must know

1. **The `min(0.35, …)` cap.** It is the whole of §3 above, and it invalidates their §8 P1, their §9 rec 2, and their §9 rec 3 sweep advice.
2. **`naval_executor.py:403` has no ratio gate at all** — unlike the AI rung, and unlike nothing on the player path. A small landing force put ashore against a ≥5,000 capital garrison enters the resolver directly and is the *likeliest* way into the weak regime. Neither their derivation nor their sweep touched this caller.
3. **The slice currently quotes two different fixtures in one commit.** The resolver comment's table is Europe/Lorraine/plains **combat-only** (9,233 → 1,496); the test docstring's table is legacy/Paris/urban **totals** (10,234 → 2,942). Both reproduce exactly on their own fixture; together they read as a contradiction. Any figure in the landing record must name world × terrain × marshal × start province.
4. **A probe that never reaches the resolver reports "INERT".** My first `r4` pass "proved" the constant inert on every row with `reached_resolver=False` — the command dict shape is `{"command": {"marshal": …}}`, not `{"marshal": …}`. Any arm comparison or sweep over this seam must *assert the resolver was entered*, or it manufactures the reporter's conclusion.
5. **"GR5 by construction" is true of the arithmetic and false of the reachability.** The resolver is shared, but the AI reaches it through a `ratio >= threshold` gate the player and the naval landing do not have. So the *floor's binding regime* is player/naval-only. The landed comment should say so.
6. **What the ruling still does not buy** (they say this and it is worth repeating): the assault COUNT is untouched. 13 assaults remain 13 AP / 13 marshal-actions, and after the re-base they now cost the corps almost nothing (assaults 11 and 12 cost a 38,674-man corps **0 men each**). The grind half of FA-D28 is fully open.