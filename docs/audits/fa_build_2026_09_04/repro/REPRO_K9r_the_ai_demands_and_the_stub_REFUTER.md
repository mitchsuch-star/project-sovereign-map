Repo untouched by me; all work under scratch. Here is my refutation report.

---

# REFUTER REPORT — FA-21 / FA-35

**Method.** `git status --porcelain` was **not empty** when I started (27 modified backend/test files, 444 changed backend lines, plus a builder's in-progress `tests/test_fa_slice14_*.py`). The reporter's opening line "Repo verified untouched (`git status --porcelain` empty)" does not hold at the tree I was given. I sidestepped it: every probe ran against a `git archive HEAD` export of `9ef38da8` in scratch (`pristine/`), never the live tree. Narrow pytest selections ran against the live repo because `ai_diplomacy.py` / `diplomacy.py` / `enemy_ai.py` are all unmodified there. **Repo verified untouched by me** at the end (`9ef38da8`, none of my files in it).

---

## FA-21

### 1. The fixture numbers
**CLAIM:** ws 54 · purse 17,487 · built 270 · acceptance 53 · reducer leaves 270 · EC-W4 6,233 (cap 6,994) · cooldown `Britain|harsh_peace` = 5.
**MY MEASUREMENT** (`r1_fa21_fixture.py`, pristine tree): every one, to the digit.
**VERDICT: CONFIRMED.**

### 2. The reducer boundary and purse-blindness
**CLAIM:** ≤491 unchanged, 492–983 halved, ≥984 → 200 + `_force_send`; acceptance identical across six chests.
**MY MEASUREMENT** (`r2_fa21_ceiling.py`): `490→490`, `491→491` (score 20), `492→246` (score 19), `983→491`, `984→200 force=True`. Lump 2,000 scores **−37** at chests 0 / 200 / 2,000 / 17,487 / 100,000 / 900,000. Deliverable ceiling by sweep = **491**.
**Stronger than filed:** a source census of `calculate_acceptance` (554 lines) finds `nation_gold`, `treasury`, `.gold`, `purse` **all ABSENT**. Purse-blindness is structural, not incidental.
**VERDICT: CONFIRMED (and strengthened).**

### 3. The three-arm 40-turn flip
**CLAIM:** P8 fires 5× (t15/17/24/31/38); arm A delivers 200 + `_force_send` all five times, strictly worse than arm 0's 220/352/266/277/243; series byte-identical on all arms.
**MY MEASUREMENT** (`r3_series_flip.py`, own instrumented replica of `_emit_series`):

| t | purse | arm0 | arm A |
|---|---|---|---|
| 15 | 18,108 | 220→**220** | 4,976→**200** force |
| 17 | 15,800 | 352→**352** | 4,750→**200** force |
| 24 | 6,650 | 532→**266** | 2,660→**200** force |
| 31 | 3,571 | 555→**277** | 1,428→**200** force |
| 38 | 3,919 | 487→**243** | 1,567→**200** force |

Arm 0 reproduces `BASELINE_SERIES` verbatim, `France 5 / Austria 26 / Britain 21 / Russia 10`, `fallen {Deroy}`. Series and province map identical on 0/A/B.
**VERDICT: CONFIRMED.** The central recommendation ("do not ship 1 without 2; arm A is the regression") stands.

### 4. "my arm-A war-age term measured 0 — the lookup missed"
**MY MEASUREMENT** (`r4_warage.py`): the ages are **14, 16, 23, 30, 37**. `world.war_instances` holds key **`war_1`**, `created_turn=1` — the reporter looked it up by diplo key, which is why they got 0.
Filed-fix amounts at the real ages: **5,676 / 5,550 / 2,660 / 1,428 / 1,567**. The last three are unchanged (the 0.40× cap binds); only t15 and t17 move.
**VERDICT: REFUTED as a fact, CONFIRMED as a conclusion** — all five still collapse to 200. But two of the report's arm-A figures are wrong, and **the builder needs a fact the report does not carry: there is ONE war instance covering France vs Austria *and* Britain, so a "war age" term is the coalition war's age — identical for every court that sues.**

### 5. Arm B's numbers
**CLAIM:** 2,716 / 2,375 / 1,330 / 714 / 783.
**MY MEASUREMENT:** 2,716 / 2,370 / 997 / 535 / 587 from an equally defensible "purse-aware reducer".
**VERDICT: NOT REPRODUCIBLE.** Arm B is an invention, not a measurement; only the first number agrees. The table must not be read as data.

### 6. The pin list
**CLAIM:** 7 `TestA4GoldFormula` pins + `test_gold_scales_with_war_score` = 8 flip.
**MY MEASUREMENT** (`plugin_armA.py`, live repo, baseline 242 passed → **9 failed / 233 passed**):
the 8 they name, **plus `tests/test_da1_ai_intelligence.py::TestIntegration::test_a1_with_a4_gold`** (`assert 320 == 250`) — a different class, which is why a class-scoped scan missed it.
**VERDICT: NARROWED — the list is incomplete.**

### 7. "seam 3 has no safety net"
**MY MEASUREMENT:** 41 `gold_lump` files, baseline **2,032 passed**; with `DEMAND_VALUES["gold_lump"]` softened 5× (`-0.03 → -0.006`, print-verified applied) → **2,032 passed**.
**VERDICT: CONFIRMED exactly.**

### 8. "a rejected AI proposal costs no relations … `_force_send` is *safe* … blast radius zero"
**MY MEASUREMENT:** `_handle_reject_ai_proposal` (`diplomatic_executor.py:6533`) calls `record_schemer_peace_rejection`, which **plants a coalition-threat marker for `SCHEMER_PEACE_REJECTION_PRESSURE_TURNS = 5`** feeding `_calculate_schemer_peace_rejection_threat`. `harsh_peace` **is** in `PEACE_FAMILY_PROPOSAL_TYPES`. At boot **Austria, Russia and Bavaria are schemers** — and the t15 firing in the very run the report uses **is Austria**.
**VERDICT: REFUTED.** Option 3(a)'s "blast radius zero" is wrong. Relation damage is nil; standing coalition threat is not. The ambient series hides this only because the harness player never answers.

---

## FA-35

### 9. The row's geometry no longer reproduces
**MY MEASUREMENT** (`r5_fa35_colocated.py`, Charles 24,724 + John 7,058 + Mack 22,589 + 500-man Massena at a French Piedmont): actions **[1, 4, 4] = 9**. The row's "four turns / 8–11 actions" is dead.
But my Massena **retreats to Lyonnais and reaches 0 there** — no `MARSHAL CAPTURED`, no `No word came`. The quoted capture text is geometry-specific.
**VERDICT: CONFIRMED in substance, NARROWED in detail** — quote the action count, not the capture line.

### 10. The counterfactual
**CLAIM:** 9 vs 12 actions; 2 provinces.
**MY MEASUREMENT:** stub `[1,4,4]=9`, Austria 14; no-stub `[4,4,4]=12`, Austria 16. **Delta exact: 3 actions, 2 provinces.**
**VERDICT: CONFIRMED.**

### 11. The engaged-arm inertness
**CLAIM:** 4,933 calls, 0 engaged-with-stub, 0 brakes dropped.
**MY MEASUREMENT:** **calls 4,933 ✓, engaged_with_stub 0 ✓, brakes_dropped_stub 2** — which is what the report itself says ("the 2 drops were pair-brake drops"), so the "0 and 0" phrasing in the summary is loose but the substance holds.
**VERDICT: CONFIRMED.**

### 12. The deadlock
**MY MEASUREMENT (reading):** P-1 `enemy_ai.py:1659-1662` (`if not enemies_here and not has_garrison`) and P4.5 `:3757-3761` (`if defenders: continue`) both refuse at any strength — exact line numbers, exact predicates.
**But the deadlock requires the floor at the ENGAGEMENT rungs too.** P0 (`:1710`) reaches a co-located stub through `_engageable_enemies`, not through P4's candidate list. A floor confined to P4's ranged candidates — which is what the row's seam actually is — leaves P0 free to kill a co-located stub, and my arm R confirms co-located cases still resolve.
**VERDICT: NARROWED.** Real, but only under a scope the row does not state. What arm R *actually* produces is worse and different — see 13.

### 13. The ranged-floor series flip — **outcome confirmed, magnitude refuted**
**MY MEASUREMENT** (`r6_fa35_series.py`, one-line lever `RANGED_STUB_FLOOR_ACTIVE` in the scratch tree at the real seam, `enemy_ai.py:3047`):

- arm 0 = `BASELINE_SERIES` ✓
- **first divergence index 21 ✓**
- armR `… 25, 27, 27, 24, 21, 18, 5, 2, 0 …` ✓ character-for-character
- **Austria 26→21 ✓, Britain 21→26 ✓, France 5→6 ✓, Spain 9→10 ✓, Switzerland 1→2 ✓, Holland 3→0 eliminated ✓**

**But "4 refusals in 40 turns" is wrong under every convention** (`r7_refusal_census.py`):

| counting | count |
|---|---|
| raw evaluations | **133** |
| unique (turn, attacker, target) | **45** |
| unique (turn, target) | **16** |
| distinct turns | **16** |
| distinct targets | **3** — Paget, Bernadotte, **Lannes** (unlisted) |
| distinct attackers | **8** |

Bernadotte alone is refused across **turns 24–39**, not "t26 ×2".
**VERDICT: CONFIRMED in effect, REFUTED in magnitude (11×–33×).** "Four decisions, a different Europe" mis-describes the mechanism.

### 14. The mechanism the report's own statistic cannot see
"1 of 117 attack decisions targets a sub-1,000 corps (0.85%)" is measured on the **unpatched** board and used to size the patch. That inference is invalid, and I measured why:

| | arm 0 | arm R |
|---|---|---|
| turns with any sub-1000 live corps | **1** | **26** |
| total corps-turns spent sub-1000 | **1** | **26** |

Paget survives turns 11–17; Bernadotte turns 21–38, bleeding 991→305 by attrition alone, then dying (`fallen` gains **Bernadotte** under arm R). **The floor manufactures the population it refuses to attack.** The reporter's own "only one marshal (Bernadotte, 956, t41) ever ends a turn below 1,000" reproduces exactly for arm 0 — and is precisely the number that stops being true the moment the fix ships.

### 15. Which pins arm R reds — **the report never measured this**
**MY MEASUREMENT:** slice2 + slice2r + slice4 + slice4r + `enemy_ai{,_behavior,_bugs}` in the pristine tree, lever off vs on: **326 passed / 1 failed in BOTH arms** (the one failure is my extraction missing `main.gd`).
**Arm R reds ZERO existing pins** while moving five nations and eliminating Holland. The report lists pins that flip at a *higher* floor; at the row's natural 1,000 floor there is no safety net at all — FA-21's seam-3 problem again.

### 16. Small source claims
- `diplomacy.py:~9420` is the **1,000-casualty** war-score gate (comment verbatim) — **CONFIRMED**, wrong precedent.
- `enemy_ai.py:2739` is a fortify guard, not `enemy.strength > 0`; the real P4 seam is **`:3047`** — **CONFIRMED**.
- `STUB_STRENGTH_FLOOR = 1000` at `:147`; `_engageable_enemies` at `:2785`; four call sites `1710 / 3198 / 4911 / 5013` — **CONFIRMED exactly**.
- M1–M7 harness: 639 lines, **zero** occurrences of `EnemyAI`, `end_turn`, `advance_turn`, `process_nation_turn`, `ai_diplomacy`, `process_diplomatic` — **CONFIRMED**.

---

## What the reporter MISSED that a builder must know

1. **A ninth pin flips under the filed FA-21 fix** — `test_da1_ai_intelligence.py::TestIntegration::test_a1_with_a4_gold`.
2. **The extraction target IS pinned, in two files the report never names.** `tests/test_ca8_gate_closeout_2026_08_07.py:336-347` and `tests/test_settlement_incoming_offers.py:294-324` carry formula assertions on `SETTLEMENT_OFFER_TREASURY_FRACTION` / `MAX_TREASURY_FRACTION` / `PER_WAR_SCORE`. The report's "test_econ_war_coupling.py has no EC-W4 amount pin" is true but reads as "nothing pins it". Arm A leaves both green (83 passed) — a refactor that *moves* the body must keep them so.
3. **The filed fix silently deletes the hawk/dove personality signal.** EC-W4 takes no `gold_mult`, which is why `test_hawk_multiplier` and `test_dove_multiplier` both collapse to the same 320. The report lists them as flipping without noting the signal is gone.
4. **A refused `_force_send` demand is not free** — schemer-court rejection plants 5 turns of coalition threat, and Austria (a schemer) is one of the five firings.
5. **GR5:** `harsh_peace` has one producer (`ai_diplomacy.py:1550`) and passes no `recipient`, so the payer is always the player. A purse-scaled indemnity here is **player-only** — the AI never levies one on another AI.
6. **The war age is real (14–37) and is the coalition war's age, not the pair's** — one `war_instances` entry (`war_1`) covers France vs Austria *and* Britain, so an age term prices every court identically.
7. **FA-35's ranged floor reds nothing in the suite while moving five nations** — it needs a flip-arm and a new pin, not a regression check.
8. **FA-35's real hazard is a feedback loop, not four decisions.** Any pin must assert the *population* (sub-1000 live corps-turns 1 → 26), because a static frequency measured on the unpatched board cannot see it.

**Probe files:** `r1_fa21_fixture.py`, `r2_fa21_ceiling.py`, `r3_series_flip.py`, `r4_warage.py`, `r5_fa35_colocated.py`, `r6_fa35_series.py`, `r7_refusal_census.py`, `r8_schemer.py`, `plugin_armA.py`, `plugin_armR.py`, `plugin_softgold.py`, all under `.../s14/refute_I_ai_demands/`, with `pristine/` = `git archive HEAD`.