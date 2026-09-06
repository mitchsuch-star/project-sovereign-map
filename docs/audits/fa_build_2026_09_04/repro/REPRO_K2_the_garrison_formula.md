# FA-D28 — the garrison formula

**VERDICT: REPRODUCED (headline exact) — but NARROWER than filed in geometry, WIDER in magnitude, and the ruling's own wording has a reading that annihilates the corps.**

⚠ **First, a tree warning.** HEAD is `9ef38da8` but the working tree is **not clean** — another agent is landing FA-D28 + FA-R5 *right now*. `backend/commands/combat_executor.py` gained the FA-D28 floor swap and an FA-R5 `log_event` at **20:16 today**, and by my last check the diff had spread to `campaign_log.py`, `dispatch.py`, `withdrawal.py` and 10 test files. **Every measurement below was taken against the committed code** (each in-memory patch asserted the original line was present and refused otherwise; all ran before 20:16). §8 reviews what actually landed. I wrote nothing to the repo.

---

## 1. What reproduces (exact numbers)

`p1_baseline.py`, `p6_readings.py`, `p10_real_geometry.py`. Kutuzov 40,000, cautious (attack modifier 1.00 at the first blow), Lorraine (plains, no fort), detachment garrison, resolver in a loop.

| garrison | assaults | attacker | lost | % of corps | row says |
|---|---|---|---|---|---|
| 3,000 | **13** | 40,000 → 29,844 | **10,156** | 25.4% | 13 / 29,844 ✅ **exact** |
| 12,000 | **15** | 40,000 → 26,351 | 13,649 | 34.1% | 15 / 24,973 (off 1,378) |
| 25,000 | **16** | 40,000 → 21,076 | 18,924 | 47.3% | 16 / 16,570 (off 4,506) |

All three **assault counts match to the digit**; case A's total matches to the digit. `⌈log₂N⌉+1` holds for a detachment up to ~25,000 (breaks above, where `garrison_damage_ratio` stops hitting its 0.50 cap).

**The row's B and C totals are reachable and the prior repro was wrong to call them unreproducible.** `p9_row_numbers.py` scanned terrain × fort × modifier: hills/mod 0.77 → 24,974 (row: 24,973, off by **1**); plains+fort/mod 0.87 → 16,581 (row: 16,570, off by **11**). The prior repro scanned terrain **at modifier 1.00 only** and concluded "no terrain reaches the row's figures". A sub-1.0 modifier is exactly what the attacker has from his second assault onward — FA-N59's exhaustion ladder (0.90 / 0.80 / 0.70). **The row's numbers are essentially sound.**

**The mechanism, confirmed and sharper than filed** (`p8_modifier_trace.py`): against a 3,000-man detachment, **every man lost in all 13 assaults is paid by the floor, not by the garrison** —

```
 #  atk_before  attacks_this_turn  exhaust  garr_before   lost
 1      40,000                  0     0.00        3,000    800   = int(40000*0.02)
 2      39,200                  1     0.10        1,500    784   = int(39200*0.02)
 3      38,416                  2     0.20          750    768   = int(38416*0.02)
...
13      31,394                 12     0.30            1  1,550   (627 combat + 923 march)
```

The floor binds **iff effective attacker > 12.5× effective garrison** (`p2_model.py`, derived and tabulated) — a pure over-match tax. Confirmed scale-invariant (`p7`):

| attacker vs a 3,000 detachment | 10,000 | 20,000 | 40,000 | 80,000 | 120,000 | 200,000 |
|---|---|---|---|---|---|---|
| lost today | 3,039 | 5,064 | 10,156 | 20,319 | 30,480 | **50,805** |
| % of corps | 30.4 | 25.3 | **25.4** | **25.4** | **25.4** | **25.4** |

A 200,000-man army loses **50,805 men** to 3,000 defenders. The row's *"however large he is"* is exactly right; *"a fifth to a half"* understates the low end — it is a **flat quarter**.

---

## 2. What is false / narrower than filed

**(a) The row's 12,000 and 25,000 cases are geometries the game cannot produce.** `EconomyExecutor.GARRISON_DETACHMENT_SIZE = 3000` is the *only* detachment size in the game — one constant serving both the player's `garrison` verb and the AI's P6.75 `_consider_garrison`. A 12,000 or 25,000 garrison is always a **capital or DEF-6 depot**, which collapses below 5,000 instead of fighting to destruction. Measured for real (`p10`):

| reachable geometry | assaults | attacker loses | vs garrison |
|---|---|---|---|
| **detachment 3,000** (the only one) | **13** | **10,156 (25.4%)** | **ABSURD** |
| capital 10,000 | 2 | 4,971 (12.4%) | ok |
| capital 12,000 | 2 | 5,726 (14.3%) | ok |
| capital 25,000 | 3 | 12,429 (31.1%) | ok |

So **FA-D28 is a one-geometry defect**: a 3,000-man detachment. Storming a real capital costs 2–3 assaults and 12–31%, which is a normal price. The row's "⌈log₂N⌉+1 assaults and a fifth to a half of the ATTACKER" reads as a general indictment of garrison combat; it is not.

**(b) "Lever A (slice 4) now steers the AI into exactly these fights" is not observable.** On the pinned ambient board the AI resolves **6** garrison assaults in 40 turns, **zero** of them against a detachment (`p3`, `p14`). It *does* create six 3,000-man detachments (Silesia, Lithuania, Bohemia, Podolia, Guyenne, Bordelais — Hohenlohe, Kutuzov ×2, Charles, Moore ×2) and never storms one. The row's live sighting came from the slice-4 review round's separate balance sweep.

**(c) The prior repro's "the ODDS half MOVES two assaults, budget a `BASELINE_SERIES` re-record" is REFUTED by measurement.** It moves two `defender_casualties` figures (Milan 2,500→5,000, Flanders 3,000→6,000, `p5`) — and **the series is byte-identical anyway** (§6).

---

## 3. The real seam

`backend/commands/combat_executor.py::CombatExecutor._resolve_garrison_combat`, lines **2947–2966** at HEAD (the row names no line; it names the symbols, correctly):

```python
attacker_damage_ratio = min(0.35, garrison_effective / max(attacker_effective, 1) * 0.25)
garrison_damage_ratio = min(0.50, attacker_effective / max(garrison_effective, 1) * 0.35)
attacker_losses  = int(marshal.strength * attacker_damage_ratio)
garrison_losses  = int(target_region.garrison_strength * garrison_damage_ratio)
attacker_losses  = max(attacker_losses, int(marshal.strength * 0.02))      # ← THE SEAM
garrison_losses  = max(garrison_losses, int(target_region.garrison_strength * 0.10), 1)
```

**Single source — CONFIRMED.** Exactly two production callers: `combat_executor.py:5171` (the no-defenders branch of `_execute_attack`) and `naval_executor.py:403` (a landing against a defended capital). `backend/game_logic/combat.py` contains the string "garrison" **zero** times. No second copy.

**GR5 — CONFIRMED.** `_execute_attack` is the shared path; the AI reaches it through `CommandExecutor.execute` like the player. Measured: the ambient run's 6 assaults are **all AI** (Austria); the existing pins drive the player (Ney/Wellington) and a third party. The AI's decision rung `_find_garrison_attack` gates on `marshal.strength / garrison_effective >= threshold` and **never reads the cost**, so changing the loss arithmetic changes no AI decision.

---

## 4. ⚠ The two readings of the ruling — THE most important thing here

The ruling I was handed says *"floor the attacker's losses **at the garrison's strength**"*. The row's own words are *"floor the attacker's losses **on the GARRISON's size, not his own**"*. These are different instructions and I measured all of them live (`p6_readings.py`, 40,000 attacker):

| reading | g=3,000 | g=12,000 | g=25,000 | complaint gone? |
|---|---|---|---|---|
| today | 13 / −10,156 | 15 / −13,649 | 16 / −18,924 | **no** |
| **RE-BASE the 2% floor** `max(al, int(g*0.02))` | 13 / **−2,814** | 15 / **−7,668** | 16 / **−14,483** | **YES, all three** |
| delete the floor entirely | 13 / −2,814 | 15 / −7,668 | 16 / −14,483 | yes (identical) |
| CAP per-assault at the live garrison | 13 / −4,193 | 15 / −8,684 | 16 / −15,191 | **NO — case A still absurd** |
| CAP cumulative at the original garrison | 13 / −3,000 | 15 / −12,000 | 16 / −17,803 | keeps the whole grind; inert in C; the exactly-equal figure is an obvious artefact |
| **LITERAL "floor AT the garrison's strength"** `max(al, g)` | 13 / −7,021 | 15 / −24,161 | **3 / −40,000 — THE CORPS IS ANNIHILATED** | **catastrophically worse** |

**The ruling must mean the row's own words: re-base the existing `0.02` floor from `marshal.strength` onto `target_region.garrison_strength`.** Read as English, "floor … at the garrison's strength" destroys a 40,000-man corps against a 25,000 garrison in three assaults. Read as a *cap*, it does not fix case A at all. Only the re-basing satisfies the row's stated criterion in every case.

**But note what the ruling does NOT buy:** the grind survives. 13 assaults stays 13 assaults — 13 AP for a player, 13 marshal-actions for the AI. The row has **two** complaints (`⌈log₂N⌉+1 assaults` **and** a quarter of the attacker); the ruling takes only the blood.

---

## 5. What the filed fix would break

The row's `fix_shape` has two halves; the ruling took only the second. I measured both.

**Half 2 (blessed, the re-base): breaks nothing.** Zero of the 2,212 tests across all 54 garrison-touching files flip. Byte-identical on all six ambient assaults.

**Half 1 (the odds arm), and the row's own carve-out is under-specified.** The row says *"≥ 4:1 → the detachment falls in one assault; the 0.50 cap keeps only for a capital's own garrison."* That is **two** buckets for **three** kinds of garrison: the two French DEF-6 depots the ambient board actually assaults (Normandy 12,000, Flanders 12,000) are `is_capital=False` **and** `garrison_detachment=False` — they fall in neither. Confirmed on the live board.

The "≥4:1" also has three defensible definitions and they differ:
- effective/effective (`odds_any`) — fires on **0** of the 6 ambient assaults;
- raw/raw (`odds_raw`, the prior repro's reading) — fires on **2**, doubling `defender_casualties` (2,500→5,000, 3,000→6,000), which feeds `record_campaign_casualties` (PT-J2's `blood` war-score component) and the EC-W3 materiel bill;
- `marshal.strength / garrison_effective` — the AI's own rung already uses this one.

Scoped to detachments (`odds_det`) it is 100% green (2,212/2,212). Applied to **any** garrison (`odds_any`) it reds exactly one pin: `tests/test_garrison_system.py::TestGarrisonCombat::test_garrison_assault_returns_events` — an 80,000 vs 15,000 assault now collapses in one blow and the collapse-with-capture branch emits a bare `conquest` event with **no `garrison_*` event at all**, so `events[0]["type"]` is neither `garrison_assault` nor `garrison_destroyed`. That is a real seam defect the odds arm would expose, not a bad test.

**Two traps for whoever edits this function:**
1. `tests/test_ca8_gate_closeout_2026_08_07.py::test_the_resolver_never_calls_resolve_battle` does `inspect.getsource(_resolve_garrison_combat)`, splits off the docstring, and asserts **`"resolve_battle" not in body`**. A comment in the body mentioning `resolve_battle` reds it. (Verified clear on the landed diff.)
2. `tests/test_creative_audit_ca8_2026_08_04.py:78` and `test_win_campaign_fixes_2026_08_16.py:343` do `inspect.getsource(CombatExecutor._execute_attack)`, which sits *below* this function. These are safe on a real edit (linecache reads the same file) but **red on any in-memory line-shifting patch** — a probe artefact I hit and had to design around.

---

## 6. Pins that flip

**None, under the blessed fix.** Measured, not argued: `fixplug.py` applies each candidate in memory before conftest, line-count-neutral.

| arm | garrison test set (54 files, 2,212 tests) | M1–M7 |
|---|---|---|
| control | 2,212 pass | 11 pass |
| **`floor` (blessed)** | **2,212 pass** | 11 pass |
| `none` (floor deleted) | 2,212 pass | 11 pass |
| `capper` | 2,212 pass | 11 pass |
| `odds_det` | 2,212 pass | 11 pass |
| `odds_any` | **1 fail** (see §5) | 11 pass |

**One existing pin is already vacuous and the fix makes its *name* a lie.** `tests/test_garrison_system.py::TestGarrisonCombat::test_attacker_takes_at_least_2pct_losses` — Wellington 80,000 vs Paris 15,000 urban: the proportional term is 4,500 and the floor is 1,600, so the assertion passes on the proportional term alone. **Mutation-proven:** the `none` arm *deletes the mechanic the test names* and the test stays green. It should be re-sited onto a geometry where the floor actually binds, or deleted.

`test_garrison_takes_at_least_10pct_losses` (`>= 1500`) pins the **garrison's** floor — untouched by any variant.

---

## 7. Series / harness risk

**M1–M7: zero risk, MEASURED not asserted.** `tests/test_combat_sweep_metrics.py` contains the string "garrison" **0** times, and an instrumented run (`countplug.py`) counts **0** calls to `_resolve_garrison_combat` across all 11 tests (control run on `test_garrison_system.py` counts 12, proving the counter works). The gate's own claim is correct.

**`BASELINE_SERIES`: no re-record is needed, and the ruling's "re-record once with flip-arm attribution" is wrong about its own outcome.** My replica of `_emit_series` reproduces `BASELINE_SERIES` byte-for-byte (`p3`, `p4`), and **every arm reproduces it**:

| arm | matches BASELINE_SERIES | garrison calls | attacker losses | France / Austria / Britain |
|---|---|---|---|---|
| control | ✅ | 6 | 15,359 | 5 / 26 / 21 |
| **floor** | ✅ | 6 | 15,359 | 5 / 26 / 21 |
| none · capper · odds_det · odds_any · odds_raw · odds_aieff | ✅ | 6 | 15,359 | 5 / 26 / 21 |

**With the reason measured, so this is evidence and not luck:** the ambient board's 6 assaults run at effective odds 1.51–3.81:1, far under the floor's 12.5:1 threshold, so the floor binds **0 times in 40 turns**; and the six 3,000-man detachments the AI creates are never assaulted. The `odds_raw` arm is **live** (`p5` shows it doubling `defender_casualties` twice) and the series still does not move — because both are collapse assaults either way, the province changes hands identically, and `threat_level` accrues on conquest, not casualties.

So: **arm 0 and arm 1 both reproduce byte-for-byte.** Record byte-identity *with the reason*; do not re-record.

⚠ **A methodological trap I hit and the builder will too.** Wrapping `EconomyExecutor._execute_garrison` with a **wrong-signature** spy moved the series (divergence at index 10) *without the wrapper body ever running* — Python raises at call binding, and something upstream swallows it. `p13_perturb.py` isolates it: `none`/`gar`/`eg_right`/`eg_identity` all reproduce; only `eg_wrong` diverges. The run is otherwise fully deterministic (repeated runs identical). **Match your spy's signature exactly, or you will attribute your own probe to the fix.**

---

## 8. Review of what actually landed (concurrent agent, working tree)

The landed code takes the **correct** reading — `_floor_base = target_region.garrison_strength if GARRISON_LOSS_FLOOR_READS_THE_GARRISON else marshal.strength`, times a new `GARRISON_ASSAULT_LOSS_FLOOR = 0.02`. `p15_constant_inert.py` confirms it is arithmetically identical to my `floor` arm (2,814 / 7,668). Three findings:

**⛔ P1 for the pin — `GARRISON_ASSAULT_LOSS_FLOOR` is INERT and the comment calls it "in-band tunable".** Swept on the landed code:

```
FLOOR   0.000  0.005  0.020  0.050  0.100  0.200  0.250 | 0.300  0.500
g=3000  2,814  2,814  2,814  2,814  2,814  2,814  2,814 | 2,992  4,109
```

**Setting it to zero changes nothing.** It first bites at 0.30. Algebraically the floor binds iff `F > (1+terrain)(1+fort) × 0.25 / modifier`, i.e. `F > 0.25` on open ground — so the blessed 0.02 is dead code, the stated band is empty, **any mutation of `0.02` will come back INERT, and any test asserting the floor's magnitude will be vacuous** — the same trap as the pre-existing `test_attacker_takes_at_least_2pct_losses`. The load-bearing lever is `GARRISON_LOSS_FLOOR_READS_THE_GARRISON` (off → 10,156, on → 2,814); the sweep must mutate **that**.

**P2 — the comment's table is combat-only and two of its three rows are unreachable geometries.** It prints `3,000 → 9,233 → 1,496`, `12,000 → 12,727 → 5,996`, `25,000 → 17,803 → 12,496`. What a player actually loses is **10,156 → 2,814** (the rest is `_calculate_movement_attrition` on the collapse turn). And the 12,000/25,000 rows are the row's own synthetic detachments — the game's only detachment is 3,000 (§2a). A before/after pin built from that table will pin numbers no player can produce.

**P3 — the tree is currently red.** `tests/test_fa_slice11_...::test_the_log_type_count_is_unchanged` fails against the working tree (the FA-R5 `log_event` addition). Seven further failures in the 54-file batch are ordering/cross-file effects that vanish when the files are run alone — they need the other agent's own attribution, not mine. The CA8-19 body census (`"resolve_battle" not in body`) is **clear** on the landed text.

---

## 9. Recommended build shape

1. **Build the re-basing, exactly as landed** — one line, behind `GARRISON_LOSS_FLOOR_READS_THE_GARRISON`. It is the only reading that satisfies the row in all three cases; the literal reading annihilates the corps and the cap reading misses case A.
2. **Say at the seam that the constant is dead.** Either drop `GARRISON_ASSAULT_LOSS_FLOOR` and write `max(attacker_losses, 1)` (mirroring WO-3's defender guarantee, so a landed assault always costs a man), or keep it with a comment stating it is provably unreachable below `0.25 × (1+terrain)(1+fort) / modifier` — but do not call it tunable.
3. **Pin the LEVER, not the number.** Falsifiable before/after on the one reachable geometry (3,000 detachment, 40,000 corps, plains): 13 assaults both ways, **10,156 → 2,814**, `lost <= garrison` after; plus the scale-invariance pin (25.4% flat at 20k–200k before; 9.2%→3.8% after); plus a **negative control** that the three capital geometries (10k/12k/25k) are byte-identical, which is what proves the fix is narrow.
4. **Record `BASELINE_SERIES` and M1–M7 byte-identical WITH the measured reason** (floor binds 0/6 at ≤3.81:1; six detachments created, none assaulted; M1–M7 makes 0 resolver calls). Do not re-record.
5. **Re-site or delete `test_attacker_takes_at_least_2pct_losses`** — it is mutation-proven vacuous and its name will be false.
6. **Send the assault-count half back to the gate with this evidence, not the row's.** It is far cheaper than the row's own risk note claims: scoped to detachments it is 2,212/2,212 green and series-inert, and it turns 13 assaults into 1. It needs one gate decision the row got wrong — **three** buckets (detachment / capital / DEF-6 depot), not two — and one seam fix, because a garrison that falls in a single assault currently emits a bare `conquest` event with no `garrison_*` row at all.

**Probes:** `C:\Users\User\AppData\Local\Temp\claude\C--Users-User-PycharmProjects-project-sovereign-map\d3a697cd-1535-475d-bd1b-457545b1c421\scratchpad\s14\A_garrison\` — `p1_baseline.py` · `p2_model.py` · `p3_series.py`+`p3_report.py` · `p4_series_arms.py` · `p5_pipeline_spy.py` · `p6_readings.py` · `p7_scale_and_detach.py` · `p8_modifier_trace.py` · `p9_row_numbers.py` · `p10_real_geometry.py` · `p11_weak.py` · `p13_perturb.py` · `p14_detach_census.py` · `p15_constant_inert.py` · plugins `fixplug.py` / `countplug.py` / `headplug.py`.