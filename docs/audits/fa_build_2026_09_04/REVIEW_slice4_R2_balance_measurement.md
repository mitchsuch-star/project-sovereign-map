# Review S4 round 2 — measuring the balance warning of FA slice 4 "The AI Reads the Board" (read at master 85130a6f)

> Transcribed verbatim from the reviewer's return (the harness refused the report-file write). Every table also lives on disk in the session scratch directory as analysis output — `reviewS4_R2/ambient_tables.md`, `reviewS4_R2/driver_tables.md`, the raw per-run JSON under `reviewS4_R2/ambient/` (60) and `reviewS4_R2/driver_out/` (35), the driver digests under `reviewS4_R2/driver_runs/<name>/digest.md`, and the probes (`ambient_probe.py`, `driver_probe.py`, `orchestrate*.py`, `analyze_*.py`, `hold_the_frontier.json`, `garrison_repro.py`, `seed_probe.py`). Findings were disposed by the slice-4 review round "The Board Reads Back" — see the boxed block in `docs/BUG_FIXES.md` §Final Whole-Game Audit; the balance verdict and the garrison-assault pathology are put to the user as a gate there.

Reviewer lens: the warning the slice-4 landing record (BUG_FIXES.md, boxed SLICE 4 block; the ELEVEN-arm attribution above `BASELINE_SERIES` in `tests/test_ai_intent_threat_migration.py`) recorded but could not measure — *"on a board where France issues no orders, an AI that reads the board now overruns it by turn 32 … whether a PLAYED France can hold is the question the next played campaign (and the AI-V ten-seed sweep) must answer."*

Trees (extracted with `git archive`, never the working tree): **before** = `d2ca0228^` (16921a6b), **mid** = `d2ca0228` (slice 4 alone), **after** = `85130a6f` (slice 4 + the slice-3 review round). Every probe ran with `cwd`/`sys.path[0]` inside the extracted tree, `PYTHONHASHSEED=0`, `LLM_MODE=mock`, `SOVEREIGN_SCENARIO`/`SOVEREIGN_MAP` unset, the seed in `SOVEREIGN_SEED`. `ambient_probe.py` reproduces the pinned 40-turn idiom verbatim (`WorldState.from_scenario`, `TurnManager(world, executor=CommandExecutor())`, `random.seed(10000+turn)` then `tm.end_turn(game_state)` × 40) with read-only wrappers on `EnemyAI.process_nation_turn`/`_execute_action`, `CombatExecutor._resolve_garrison_combat`, `CombatResolver.resolve_battle`, `WorldState.destroy_marshal`/`capture_marshal`; `driver_probe.py` puts the same wrappers around an in-process `tools/playtest_driver.py` `run()`.

The nine levers are set as module globals in the CHILD (the WO-9 idiom, no source edit): A `P425_SKIPS_A_HELD_FIELD`, B `SQUARE_FORMS_AFTER_THE_STRIKES`, C `BROKEN_AI_CORPS_IS_LIMITED`, D `COUNTER_PUNCH_PRICES_THE_FIELD`, E `STAGNATION_READS_THE_CROSSING` (all `backend.ai.enemy_ai`), F `backend.models.world_state.CAVALRY_LIMITS_ALL_NATIONS`, G `CombatExecutor.GARRISON_ASSAULT_COUNTS`, H `ALLY_SUPPORT_FIGHTS_ONLY_ENEMIES`, I `DRILL_RUNG_READS_FORTIFIED`. "Battle" below = every `CombatResolver.resolve_battle` call (the `apply_casualties=False` path is the coordinated-battle path, not a preview — there is no dry-run caller). "Destroyed" counts only calls that returned True (a refused call on a prisoner is the death-guard working).

## 0. Honesty checks on the runner (seed `historical`)

| check | result |
|---|---|
| before tree series == the before tree's own `BASELINE_SERIES` pin | **True** |
| after tree series == the after tree's own `BASELINE_SERIES` pin | **True** |
| after tree with all nine levers False (arm 0) == before tree series | **True** (byte-for-byte, 41 points) |
| mid tree (slice 4 alone) == after tree series | **True** — and identical on all 8 seeds (every task-1 row for `mid` equals `after`) |
| after tree levers-none vs before tree, same driver script, per-turn (provinces, army, threat) | **IDENTICAL** on all three played scripts |

So the second confound in the extraction — 85130a6f's slice-3 review round (`strategic.py`, `strategic_executor.py`, `combat_executor.py`) — is inert on the passive board across all eight seeds and on all three played boards: **everything below that differs between before and after is slice 4.**

The driver itself changed between the trees (R2-F6: answer EVERY strategic interrupt per response, not the first). Both trees were driven with the AFTER driver (copied into `before/tools/`, the original kept as `playtest_driver_orig.py`). Control: on `np_campaign_emperor` the two drivers are per-turn identical; on `hold_the_frontier` they diverge at world turn 19 and the SAME tree ends **27 provinces (new driver) vs 4 provinces, Paris fallen t30, the Emperor captured t38 (old driver)**. That is the harness answering one interrupt a turn later. Keep it in mind when reading any single played arm.

## 1. The passive board across seeds (task 1)

40 turns, France issues no orders. `Fr@N` = French province count after N end-turns (boot = 28).

| tree | seed | Fr@10 | Fr@20 | Fr@30 | Fr@40 | Paris fell | Napoleon | threat [35..40] | final board (top 4) | Fr battles W/L/D | Fr corps destroyed / captured |
|---|---|---|---|---|---|---|---|---|---|---|---|
| before | historical | 29 | 30 | 13 | 8 | — | captured t40 | 44 41 38 35 32 29 | Britain 26, Austria 19, Ottoman 14, Russia 10 | 20/22/5 | 0 / 4 |
| before | ulm | 29 | 18 | 13 | 6 | — | captured t32 | 0 0 0 0 0 0 | Britain 33, Ottoman 14, Austria 14, Russia 10 | 14/17/6 | 1 / 7 |
| before | austerlitz | 29 | 16 | 10 | 6 | — | captured t34 | 0 0 0 0 0 0 | Britain 25, Austria 20, Ottoman 14, Russia 10 | 18/20/7 | 1 / 5 |
| before | jena | 29 | 30 | 13 | 8 | — | captured t40 | 48 45 42 39 36 33 | Britain 26, Austria 19, Ottoman 14, Russia 10 | 20/22/5 | 0 / 4 |
| before | marengo | 29 | 16 | 10 | 6 | — | captured t34 | 0 0 0 0 0 0 | Britain 25, Austria 20, Ottoman 14, Russia 10 | 18/20/7 | 1 / 5 |
| before | eylau | 29 | 29 | 28 | 21 | — | captured t34 | 46 43 40 37 34 31 | France 21, Ottoman 14, Russia 13, Austria 12 | 18/28/3 | 0 / 4 |
| before | friedland | 29 | 29 | 28 | 11 | — | captured t24 | 30 27 24 21 8 5 | Austria 20, Britain 18, Ottoman 14, France 11 | 12/11/5 | 3 / 6 |
| before | wagram | 29 | 30 | 15 | 10 | — | free (1,308 men) | 36 33 30 27 24 21 | Britain 22, Austria 18, Ottoman 14, Russia 10 | 18/10/4 | 1 / 0 |
| after | historical | 28 | 17 | 3 | 2 | — | captured t35 | 0 0 0 0 0 0 | Britain 28, Austria 23, Ottoman 14, Russia 11 | 9/22/7 | 0 / 8 |
| after | ulm | 28 | 18 | 5 | 2 | — | free (2,015) | 0 0 0 0 0 0 | Britain 33, Austria 19, Ottoman 14, Russia 10 | 19/18/7 | 0 / 3 |
| after | austerlitz | 28 | 13 | 4 | 4 | — | free (3,439) | 0 0 2 0 0 2 | Britain 28, Austria 18, Ottoman 14, Russia 12 | 15/8/3 | 0 / 2 |
| after | jena | 28 | 17 | 5 | 1 | **t40 (Britain)** | captured t38 | 0 0 0 0 0 0 | Britain 31, Austria 23, Ottoman 14, Russia 10 | 12/27/7 | 0 / 7 |
| after | marengo | 28 | 13 | 5 | 2 | — | free (883) | 0 0 0 0 0 0 | Britain 35, Austria 16, Ottoman 14, Russia 11 | 13/18/5 | 0 / 5 |
| after | eylau | 28 | 14 | 3 | 3 | — | free (2,341) | 0 0 0 0 0 0 | Britain 31, Austria 20, Ottoman 14, Russia 10 | 15/9/9 | 0 / 3 |
| after | friedland | 28 | 17 | 3 | 2 | — | captured t35 | 0 0 0 0 0 0 | Britain 28, Austria 23, Ottoman 14, Russia 11 | 9/22/7 | 0 / 8 |
| after | wagram | 28 | 17 | 3 | 2 | — | captured t35 | 0 0 0 0 0 0 | Britain 28, Austria 23, Ottoman 14, Russia 11 | 9/22/7 | 0 / 8 |

Seed means: **Fr@30 16.2 → 3.9, Fr@40 9.5 → 2.2** (lower after on 8/8 seeds at both marks). When the collapse arrives:

| tree | first turn France ≤ 14 (half its boot) | first turn ≤ 5 | first turn threat == 0 |
|---|---|---|---|
| before | 29, 26, 27, 29, 27, never, 35, 31 | never on any seed | 3 of 8 seeds (32–34) |
| after | 21, 22, 20, 21, 20, 20, 21, 21 | 23, 27, 27, 23, 27, 24, 23, 23 | 8 of 8 (28–33) |

**"France overrun by ~turn 32" is the norm on a passive board, not one seed's path** — on every one of eight seeds France is at or below five provinces by turn 23–27 and the threat series decays to zero by turn 28–33. The record's historical end state (France 2 / Austria 23 / Britain 28, the Emperor captured t35) reproduces exactly, and `friedland`/`wagram` end in the identical state. Two things the record did not say: the passive board was already lost BEFORE the slice (the Emperor captured on 7/8 seeds, t24–t40, France at 6–21 provinces at turn 40); and after the slice the Emperor is captured LESS often (4/8) because on the other four seeds his corps simply evaporates by attrition (883–3,439 men left) with nothing to fight.

## 2. A defended France (task 2)

Three scripts through `tools/playtest_driver.py` (in-process, mock parser, default answer policy; explicit `--llm mock`, `--seed`): the two existing fighting arms `np_campaign_emperor` (22 loops) and `weird_tyrant` (30 loops), also run to 40 with the scripts' orders exhausted, and my own `hold_the_frontier.json` (40 loops: the Guard holds Paris, the Rhine corps fortify, Bernadotte pulled back, two massed blows at Mack then re-dig; see Caveats for what the marshals did with those orders).

| run | tree | Fr@10 | Fr@20 | Fr@30 | Fr@end | army@10 | army@20 | army@end | Paris | Napoleon | Fr battles W/L/D (as attacker won/total) | Fr corps captured | AI refused | garrison ord/resolved | AI squares | AI corps captured | final board top 3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| emperor@22 | before | 29 | 33 | — | **29** | 137,658 | 94,642 | 92,086 | held | free | 14/1/4 (11/13) | 0 | 5 | 3/3 | 6 | 3 | France 29, Ottoman 14, Britain 12 |
| emperor@22 | after | 29 | 28 | — | **26** | 137,649 | 93,043 | 84,347 | held | free | 13/7/3 (8/9) | 0 | 1 | 3/3 | 3 | 5 | France 26, Ottoman 14, Britain 14 |
| emperor@40 | before | 29 | 33 | 30 | **27** | 137,658 | 94,642 | 22,031 | held | captured t25 (see note) | 19/2/9 (14/17) | 1 (+5 interned) | 8 | 17/16 | 8 | 3 | France 27, Ottoman 14, Russia 12 |
| emperor@40 | after | 29 | 28 | 18 | **14** | 137,649 | 93,043 | 32,773 | held | free (99 men) | 14/15/4 (8/9) | 3 | 5 | 3/3 | 7 | 5 | Britain 23, Ottoman 14, France 14 |
| tyrant@30 | before | 29 | 30 | 30 | **30** | 124,593 | 96,523 | 81,988 | held | free | 24/1/3 (10/11) | 0 | 5 | 2/1 | 12 | 6 | France 30, Ottoman 14, Britain 11 |
| tyrant@30 | after | 28 | 25 | 16 | **16** | 121,516 | 77,337 | 31,484 | held | free (72 men) | 21/15/5 (10/13) | 4 (t20–23) | 3 | 0/0 | 1 | 1 | Britain 25, France 16, Ottoman 14 |
| tyrant@40 | before | 29 | 30 | 30 | **29** | 124,593 | 96,523 | 46,092 | held | free | 24/10/4 (10/11) | 3 | 7 | 3/2 | 13 | 6 | France 29, Ottoman 14, Russia 11 |
| tyrant@40 | after | 28 | 25 | 16 | **8** | 121,516 | 77,337 | 29,404 | held | free (62 men) | 21/15/5 (10/13) | 4 | 6 | 0/0 | 1 | 1 | Britain 33, Ottoman 14, Russia 11 |
| hold@40 | before | 28 | 28 | 28 | **27** | 149,999 | 93,223 | 72,250 | held | free@Paris 10,000 | 19/6/5 (11/11) | 3 | 15 | 3/3 | 2 | 3 | France 27, Ottoman 14, Russia 12 |
| hold@40 | after | 28 | 28 | 27 | **11** | 149,848 | 117,854 | 57,322 | **fell t41 (Russia)** | routed to Champagne, 986 men | 16/13/9 (7/7) | 3 | 5 | 5/4 | 2 | 4 | Russia 19, Austria 16, Ottoman 14 |
| hold@40 `ulm` | before | 29 | 27 | 23 | **16** | 140,979 | 103,854 | 50,655 | held | free | 25/16/10 (6/10) | 4 | 32 | 2/2 | 20 | 2 | Austria 20, France 16, Ottoman 14 |
| hold@40 `ulm` | after | 23 | 15 | 7 | **6** | 143,205 | 121,868 | 67,045 | held | free@Paris 10,000 | 8/18/4 (4/11) | 2 | 6 | 4/4 | 3 | 2 | Austria 29, Ottoman 14, Britain 13 |
| hold@40 `austerlitz` | before | 28 | 27 | 27 | **27** | 127,030 | 113,415 | 112,309 | held | free@Paris 10,000 | 4/2/3 (3/4) | 0 | 3 | 2/2 | 4 | 3 | France 27, Ottoman 14, Britain 13 |
| hold@40 `austerlitz` | after | 28 | 26 | 14 | **10** | 150,483 | 134,880 | 69,450 | held | free@Paris 9,482 | 8/10/7 (2/6) | 2 | 5 | 5/5 | 4 | 2 | Britain 28, Ottoman 14, Russia 10 |

Note on emperor@40/before: the script's own `offer peace to Austria` (loop 22) was accepted; the road-home safe passage then lapsed at world turn 25 and **five corps were interned where they stood** (Ney at Lithuania "by Russia" — a court France was still fighting, on a province Murat had taken that same phase) and the Emperor was captured by Russia through the same lapse (army 88,486 → 34,447 in one turn). That is the design of record (`withdrawal.py::_intern`, the enclave/encircling-power rule; the sovereign conversion noted Aug 30), not a defect — but it, not the AI, shaped that arm's late board, and the after tree never reached that peace.

Per-turn France province counts (world turn = index+1), the arms that matter:

- hold@40 before: 28…29…28 ×30 … 27 27 27 27 — flat.
- hold@40 after: 28 … 28 (t21) 27 ×10 (t22–31) **24 24 24 24 19 16 14 11** (t32–40) — the fall starts at t32.
- tyrant@40 before: 28…30 ×18 … 29 ×6 — flat. after: 28 (t1–11) 27 (t12–17) 26 25 **22 22 22 18 16** (t21–25) 16 ×9 **15 12 10 10 8 8** (t34–40).
- emperor@40 after: 29–30 to t17, then 27 26 24 23 21 21 21 21 19 18 16 16 15 14 ×7.

Who takes the provinces (capture lines by nation, 40-turn digests): emperor@40 before {Austria 8, Russia 3, Spain 2, Britain 1} → after {**Britain 12**, Austria 9, Russia 5, Spain 4}; tyrant@40 before {Bavaria 4, Britain 1, Russia 1} → after {**Britain 19**, Bavaria 2, Spain 2, Russia 2, Austria 1}; hold@40 before {Austria 5, Bavaria 3, Russia 2} → after {**Austria 12, Russia 10**, Spain 4, Bavaria 3, Britain 1}; hold `austerlitz` after {**Britain 16**, Austria 7, Bavaria 5, Spain 1}; hold `ulm` after {**Austria 26**}.

The biggest single difference attributable to the slice on a played board is on **tyrant@30**: 30 → 16 provinces, army 81,988 → 31,484, French defeats 1 → 15, four corps captured at t20–23 — and the lever arms say which half: B alone reproduces most of it (10 provinces), all-but-B does not (27). On **hold@40** it is the opposite half: A is byte-inert (never binds), B alone 27 → 17, but **D alone → 8** (Austria 23; France 17W/23L) and **F alone → 3** (Britain 32, Paris fallen t36, the Emperor captured t35 — with France winning 17 and losing only 4 battles: Paget's horse leaves its line and Britain walks past the army), all-but-B → 6.

## 3. Which lever does the work (task 3)

Passive board, seed `historical`, after tree, one lever True at a time; divergence index against arm 0 (= the before series byte-for-byte):

| arm | first divergence vs arm 0 | Fr@20 | Fr@30 | Fr@40 | Napoleon captured | threat[40] | AI refused | garrison ord/resolved |
|---|---|---|---|---|---|---|---|---|
| 0 (none) | — | 30 | 13 | 8 | t40 | 29 | 23 | 11/9 |
| A | **5** | 25 | 17 | 8 | t37 | 27 | 7 | 3/2 |
| B | **4** | 25 | 14 | 6 | — | 0 | 3 | 7/2 |
| C | inert | 30 | 13 | 8 | t40 | 29 | 23 | 11/9 |
| D | **14** | 29 | 28 | 20 | — | 57 | 4 | 8/3 |
| E | inert | 30 | 13 | 8 | t40 | 29 | 23 | 11/9 |
| F | **13** | 27 | 23 | 7 | — | 22 | 25 | 10/9 |
| G | inert | 30 | 13 | 8 | t40 | 29 | 23 | 11/9 |
| H | **24** | 30 | 12 | 7 | — | 23 | 20 | 11/9 |
| I | **29** | 30 | 10 | 8 | — | 26 | 9 | 11/9 |
| all-but-B | 5 | 29 | 27 | **27** | — | 46 | 5 | 5/5 |
| ALL | **4** (with B) | 17 | 3 | 2 | t35 | 0 | 7 | 8/8 |

**Confirmed:** A forks at [5], B at [4], D at [14], F at [13], H at [24], I at [29], C/E/G byte-inert, the full tree forks at [4] with B, arm 0 reproduces the pre-slice series byte-for-byte — every index in the record's attribution is right. The turn-4 fork itself: in arm 0 Austria's phase is Charles `form_square` → `attack Murat` (lost, Murat wins) → `stance_change`; with B, Charles fortifies and Mack's `attack Munich` (a field battle against Lannes, lost) runs instead — a different corps spends the nation's actions, and the boards never meet again.

**What the record could not see:** B alone does NOT overrun France on this seed (Fr@40 = 6 vs 8) and the other eight together make France STRONGER (27 at t40, threat 46) — the collapse is the JOINT effect, and it is not additive. Across the eight seeds (after tree): arm 0 mean Fr@40 **9.5**, B-only **6.4**, all-but-B **12.5**, ALL **2.2**; Napoleon captured 7/8, 5/8, 5/8, 4/8. Without B the AI spends its freed actions on squares (all-but-B: 33–51 `form_square` per run, attacks 57–103); with B it strikes and marches (ALL on `historical`: `move` 113 → 167, attacks 85 → 82, squares 14 → 12, refused 23 → 7, AI corps captured 7 → 2, French corps captured 4 → 8, French battles won 20 → 9 at the same 22 lost). On played boards the dominant lever is a property of the board (B on tyrant; D and F on hold; A inert on hold).

## 4. What the AI does with its freed actions (task 4)

Whole 40-turn passive board, all AI nations, per tree per seed:

| tree | seed | AI actions | refused | attacks issued | attacks refused | garrison ordered | resolved as garrison combat | fought the field instead | squares | counter-punches fired | drills ordered | drills refused | AI corps destroyed | AI corps captured | field battles |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| before | historical | 1100 | 23 | 85 | 2 | 11 | 9 | 2 | 14 | 1 | 28 | 14 | 0 | 7 | 47 |
| before | ulm | 1065 | 8 | 72 | 2 | 3 | 1 | 2 | 7 | 1 | 12 | 2 | 0 | 7 | 37 |
| before | austerlitz | 1063 | 6 | 79 | 2 | 2 | 0 | 2 | 7 | 1 | 7 | 1 | 0 | 7 | 45 |
| before | jena | 1100 | 23 | 85 | 2 | 11 | 9 | 2 | 14 | 1 | 28 | 14 | 0 | 7 | 47 |
| before | marengo | 1063 | 6 | 79 | 2 | 2 | 0 | 2 | 7 | 1 | 7 | 1 | 0 | 7 | 45 |
| before | eylau | 1062 | 10 | 75 | 5 | 15 | 9 | 6 | 6 | 2 | 13 | 1 | 1 | 6 | 49 |
| before | friedland | 1103 | 15 | 58 | 2 | 7 | 4 | 3 | 13 | 1 | 18 | 7 | 2 | 6 | 28 |
| before | wagram | 1114 | 19 | 66 | 2 | 7 | 5 | 2 | 14 | 1 | 19 | 9 | 0 | 7 | 32 |
| after | historical | 1098 | 7 | 82 | 1 | 8 | 8 | 0 | 12 | 2 | 18 | 0 | 0 | 2 | 38 |
| after | ulm | 1075 | 9 | 86 | 0 | 6 | 6 | 0 | 6 | 0 | 17 | 0 | 1 | 2 | 44 |
| after | austerlitz | 1078 | 8 | 67 | 1 | 6 | 6 | 0 | 16 | 0 | 17 | 0 | 0 | 2 | 26 |
| after | jena | 1083 | 9 | 93 | 1 | 8 | 8 | 0 | 13 | 2 | 18 | 0 | 0 | 2 | 46 |
| after | marengo | 1077 | 7 | 87 | 1 | 6 | 6 | 0 | 8 | 0 | 16 | 0 | 0 | 4 | 36 |
| after | eylau | 1102 | 5 | 79 | 0 | 6 | 6 | 0 | 12 | 3 | 11 | 0 | 1 | 3 | 33 |
| after | friedland | 1098 | 7 | 82 | 1 | 8 | 8 | 0 | 12 | 2 | 18 | 0 | 0 | 2 | 38 |
| after | wagram | 1098 | 7 | 82 | 1 | 8 | 8 | 0 | 12 | 2 | 18 | 0 | 0 | 2 | 38 |

Seed means before → after: refused **13.8 → 7.4**; garrison orders (region-targeted attacks on a garrison > 0) 7.2 → 7.0, of which "fought the field instead" **2–6 per seed → 0 on every seed** (FA-8 holds); squares 10.2 → 11.4; counter-punches 1.1 → 1.4; drills refused **6.1 → 0.0** (FA-R2 holds); AI corps destroyed 0.4 → 0.2; **AI corps captured 6.8 → 2.4** (the AI stops throwing corps against fortified Frenchmen and keeps its army); French corps captured 4.4 → 5.5. The record's "garrison orders 15 → 27" is its `[GARRISON ASSAULT]` decision-print count — reproduced exactly (15 / 27, arm 0 = 15); its "refused 23 → 6" in the BUG_FIXES block is 23 → 7 by both my count and its own series comment.

## VERDICT

Answering the record's own question with numbers: **no — a played France does not hold, by any script I could drive, on the after tree.** On the passive board the overrun is the new norm, not one seed's path: France is at ≤ 5 provinces by turn 23–27 on 8 of 8 seeds (0 of 8 before) and the threat series is zero by turn 28–33 on 8 of 8 (3 of 8 before); seed means Fr@30 16.2 → 3.9, Fr@40 9.5 → 2.2. A scripted, fighting France that wins most of its battles fares the same way one phase later: across the five 40-turn played arms France's turn-40 province count went **{27, 29, 27, 16, 27} → {14, 8, 11, 6, 10}** (lower on 5/5, mean 25.2 → 9.8) while its battle record barely moved (hold@40 19W/6L → 16W/13L; tyrant@40 24W/10L → 21W/15L) and its army at turn 40 stayed the same order (hold 72k → 57k): the AI no longer feeds corps to the fortified line (AI corps captured per seed 6.8 → 2.4), it declines the free blows it used to lose, strikes before it squares, and marches — `move` orders 113 → 167 on `historical` — so Britain (23–33 provinces in the emperor/tyrant arms) and Austria/Russia (16–19 in hold) take the provinces the army is not standing on. Through turn 22–30 a played France still holds (emperor@22 26 provinces; tyrant@30 16); the collapse begins between turns 20 and 32 in every arm, once the scripts' initiative is spent and the corps are deep in Austria. The slice's arithmetic is exactly as recorded (arm 0 byte-identical, every divergence index confirmed, the review round inert), but the record's "forks at [4] with B" is where the fork STARTS, not what overruns France: B alone ends `historical` at 6 provinces and the other eight alone at 27; only the nine together end it at 2, and on a played board the dominant lever is D or F (hold) or B (tyrant). Nothing here says the AI is now "too strong" rather than "finally not wasting a third of its actions" — but the warning is real, general across seeds and scripts, and the next in-game review should expect a France that must react every turn from about turn 20.

## Caveats (what these scripts cannot show)

- **No script here reacts.** A human recalls the Rhine corps when Britain lands at Normandy, answers a Russian column at Lorraine, and keeps the Guard's 10,000 out of a losing defence of Paris; the scripts cannot, and after loop 22 (emperor) / 30 (tyrant) France is passive. The 40-turn played numbers measure a France that fights well early and then stops thinking, not a played campaign.
- **My "hold the frontier" script did not hold a frontier on either tree.** The fortified aggressive corps left their works on their own — jealousy autonomous glory-attacks ("AUTONOMOUS: Lannes leads the charge!", Ney found at Moravia when ordered to unfortify) walked Ney/Lannes/Massena to Moravia/Podolia where all three were captured (before: t17–18; after: t21). That is Jealousy v3.2 working as designed, and it means a static defensive script measures "defensive orders", not a defended frontier.
- **Single-arm outcomes are chaotic.** The same tree, same script, driven by the pre-R2-F6 driver (one interrupt answered a turn later) ends 4 provinces instead of 27; A on `hold` is byte-inert while F alone costs 24 provinces; tyrant all-but-B = 27 though A alone = 19 and D alone = 15. Trust the multi-seed and multi-arm directions above, not any one row's magnitude.
- **The seed pool is thinner than it looks.** `historical` and `wagram` boot with different banded relations (Denmark|France 10 vs 8, France|Naples −30 vs −19; `seed_probe.py`) yet produce byte-identical 41-point threat series and identical final boards on the after tree; `friedland` ends in the same final state by a different path. Eight seed strings gave seven distinct passive trajectories after and eight before — a ten-seed sweep is not ten independent draws of this board.
- Mock parser only; the LLM path was never exercised. The default answer policy declines every treaty, so the peace-and-internment shape of emperor@40/before came only from the script's own line; no arm measures a France that sues for peace when losing.
- The "garrison ordered" count in §4 is region-targeted attacks with a garrison > 0 at execution; the record counts decision prints (15 → 27) — both are reported, they are not the same quantity.

## DEFECTS tripped over while measuring

1. **A detachment garrison costs ⌈log₂ N⌉+1 assaults and a fifth to a half of the attacker, however large he is** (pre-existing; `combat_executor.py::_resolve_garrison_combat`, `garrison_damage_ratio = min(0.50, …)` with `attacker_losses = max(…, 2 % of the attacker's own strength)` — WO-3 fixed only the 1-man stall). Lever A now steers the AI into exactly these fights (garrisons "standing alone"; decision prints 15 → 27). Measured live in `after_hold_t40_allbutB`: **thirteen assaults over two turns by three corps of two nations** (Dokhturov ×5, Charles ×4, John ×4) to clear a 3,000-man French detachment at Podolia — "Garrison: 3 → 2 (−1)", "2 → 1 (−1)", "1 → 0", each costing the attacker 46–226 men. Repro (`garrison_repro.py <after tree>`, `PYTHONHASHSEED=0`): a 40,000-man Kutuzov vs a French detachment of 3,000 → **13 assaults, 40,000 → 29,844**; of 12,000 → 15 assaults, → 24,973; of 25,000 → 16 assaults, → 16,570. A corps that outnumbers the garrison 13:1 loses more men than the garrison had.
2. **Observation, filed as design of record, not a defect:** the road-home lapse interns a corps standing on a province its own army captured that phase, names the enemy it is at WAR with as the interning power, and converts the Emperor into that enemy's prisoner (`before_emperor_t40`, world turn 25: `Ney@Lithuania interned by Russia`, Napoleon captured by Russia; `withdrawal.py::_intern` says this is the intended enclave rule). It decided that arm's late board; anyone comparing emperor-arm end states across trees needs to know it.
3. **Record nit:** the BUG_FIXES block says refused actions "23 → 6"; the series attribution and this measurement say 23 → 7. The record's "garrison orders 15 → 27" is a decision-print count, confirmed as such.
