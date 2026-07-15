# COMBAT_OVERHAUL_SPEC.md — Combat Overhaul & Score-Raising Program

**Status:** SCOPE APPROVED July 13, 2026 (user). Direction blessed: additive reinforcement **that still expresses personality** (§0.3 G-1/G-1b), decisiveness + regen counter-pressure, glory-from-attrition, the economy fix, and the parser/play-friction cleanup are all IN. **Balance numbers are not gated separately — they are tuned by the Sweep (§2), data-driven.** Build proceeds by phase (§4); each phase is a self-contained session.
**Authority:** §0 is authoritative where it amends the body.
**Origin:** the `⚔️ Field Review` — a 7-turn live France/1805 playthrough (`LLM_MODE=anthropic`) + a 25-agent adversarially-verified code audit (July 13, 2026). This spec converts that review's problematic scores and every live-found defect into a build-and-measure program.
**Golden Rules in force:** GR1 (combat *modifiers* single-source in `marshal.py`; `combat.py` reads, never recalculates), GR2 (`int()` to Godot), GR5 (enemy uses the SAME executor/combat path), GR8 (scale-ready, no per-region hot-path scans), GR9 (every slice below names owner/landing/completion/STATUS/test).

---

## 0. Purpose & thesis

### 0.1 The keystone finding

**Combat is the load-bearing flaw.** In live play:

- **Reinforcements are non-additive.** Battles resolve on the *lead* marshal's `.strength` (`combat.py:_calculate_effective_strength` :1018 uses `marshal.strength` only; `_calculate_casualties` scales by the lead-vs-lead `strength_ratio` :1067). Reinforcers contribute only a capped coordination modifier (`combat_executor:_calculate_coordination_context`, `min(_,0.25)`). Live proof: massing five corps (~119k) stalemated a dug-in 39k defender, while enlarging **one** corps to 42k flipped the casualty ratio. Concentration — the core Napoleonic verb — is mechanically inert.
- **Defenders are near-unbreakable.** `defender_bonus = 0.2` flat (`combat.py:104`) stacks on terrain/fort/stance; morale loss per stalemate is small (`_scaled_morale_loss` base 5–20) against `FORCED_RETREAT_THRESHOLD = 25` (`combat.py:76`). Mack held Swabia through six assaults at morale ≥75; routs/captures essentially never occur.
- **The AI out-regenerates the attacker.** Mack was ground 52k→21.7k, then reinforced **+10,000 in one turn** while the best assault removed ~5,000. Frontal attrition is *literally unwinnable*.

Because decisive outcomes never occur, four other scores are starved (§3). **Fix combat's decisiveness and they rise with it.**

### 0.2 What this spec is

A **two-part program**:

1. **A repeatable SWEEP (§2)** — a measurement harness (deterministic combat-metric suite + the LLM component-review workflow) that scores the game before/after each change. This is the "run sweeps to raise problematic scores" engine, and it is also how the balance numbers get tuned.
2. **A PHASED build (§4)** — Phases 0–6, each a self-contained session, that move the metrics. Combat is the flagship; the coupled scores (Marshal Drama, Economy, Vassals) and every live-found play-friction bug are folded in.

### 0.3 Design decisions (blessed July 13, 2026)

| ID | Decision | Blessed value / direction |
|---|---|---|
| **G-1** | Committed reinforcing corps add strength to the clash, not just a capped modifier. | YES. Attacker effective strength = lead + `α`·Σ(reinforcer contribution). `α` **sweep-tuned**, start `0.6`. |
| **G-1b** | **Reinforcement still expresses personality & relationships** (user requirement). | YES — a reinforcer's contribution is scaled by their OWN attack side (personality shock/attack modifier via `marshal.get_attack_modifier`, read-only per GR1) AND by the MC-3 relationship coordination factor (×0.0 hostile … ×1.25 devoted). An aggressive reinforcer pushes harder than a cautious one of equal size; a marshal who resents the lead contributes little or nothing. Mass is never a flat number. |
| **G-2** | The muster "odds band" reflects total **committed** force, not lead-only. | YES. |
| **G-3** | Decisiveness: a heavily-outnumbered defender can rout → capture. | YES, via steeper morale loss on lopsided casualty ratios (not by removing the defender edge). Curve **sweep-tuned**. |
| **G-4** | Keep the defender edge meaningful. | YES — keep `defender_bonus` flat `0.2`; the change is decisiveness, not a defender nerf (guarded by metric M6). |
| **G-5** | Cap the AI's per-corps regeneration so sustained superior assault net-reduces a defender. | YES. Cap `R` men/turn (start `3,000`) unless in a friendly depot/capital; symmetric player/AI (GR5). |
| **G-6** | Glory from attrition/occupation so the drama engine isn't 100% win-gated. | YES (§3 root cause). |
| **G-7** | Include the Economy fix. | YES (user: "yes do econ fix"). |
| **G-8** | Include the parser + all other live-found play-friction issues. | YES (user: "include parser and other issues"). Phase 6. |

---

## 1. Baseline scoreboard & targets

Frozen from the July 13, 2026 review — the anchor a sweep is judged against.

| Component | Baseline | Target | Lifted by |
|---|---|---|---|
| Combat System | **5.0** | **7.5** | Phases 1–2 |
| Economy | **5.0** | **6.5** | Phase 4 |
| Marshal Drama | **6.0** | **7.5** | Phase 3 (+ combat) |
| Vassals & Coalition | **6.0** | **6.5** | Phase 5 (+ combat) |
| Narration & Legibility | 7.0 | 7.5 | CO-5/CO-6, PF-3/PF-5 |
| Marshal System | 6.5 | 7.0 | CO-7, PF-4 |
| Command Parsing / NLU | 7.0 | 7.5 | PF-1/PF-2/PF-7 |
| UX / Flow / State | 6.5 | 7.0 | PF-3/PF-6/PF-8 |
| Diplomacy | 8.0 | ≥8.0 | PF-9 (hold) |
| Enemy AI | 8.0 | ≥8.0 | AI-1 (hold; don't regress on the regen cap) |
| Settlement / Peace | 7.0 | ≥7.0 | hold |
| Architecture & Tests | 7.0 | 7.5 | CO-5 integration pin |
| **Overall (weighted)** | **6.4** | **≥7.3** | |

Any non-targeted component dropping ≥0.5 in a sweep is a **build defect**, not an acceptable trade.

---

## 2. THE SWEEP — how we measure & tune

**Half A is the hard gate (deterministic). Half B is the holistic narrative (LLM). Numbers are tuned inside Half A.**

### 2.1 Half A — deterministic combat-metric suite

New module `tests/test_combat_sweep_metrics.py`. Headless Monte-Carlo over fixed seeds against `combat.py` resolution (constructing marshals/regions as existing combat tests do). Prints each metric AND asserts a target. Fully repeatable; runs every slice.

| ID | Metric | Baseline (measure in Phase 0) | Target |
|---|---|---|---|
| **M1** | Concentration monotonicity — P(win) as committed corps 1→5 vs a fixed defender | ~flat | strictly non-decreasing; 3 corps materially > 1 |
| **M1b** | **Personality expression** — an *aggressive* reinforcer of size N raises the force ratio more than a *cautious* one of size N; a *hostile-pair* reinforcer contributes ≈0 | (new) | aggressive > cautious > hostile-pair, all else equal |
| **M2** | Numerical decisiveness — P(defender rout ≤2 turns) at 2:1 & 3:1 effective, equal terrain | ~0 | ≥0.35 @2:1, ≥0.65 @3:1 |
| **M3** | Attrition winnability — net defender Δstrength/turn under sustained ≥2:1 assault, **incl. AI reinforcement** | ≈ +5,000 (defender GAINS) | ≤ −2,000 |
| **M4** | Report consistency — `casualty_summary.attacker_remaining == event.remaining` in multi-marshal battles | 0% | 100% |
| **M5** | Iron Resolve payoff — net atk-modifier of a 3-stack release vs no stacks | +4% (stance-trapped) | ≥ +18% |
| **M6** | Defender still matters (anti-over-nerf) — solo equal-strength attack into fort+mountains stays defender-favorable | strong | remains net-favorable |
| **M7** | Drama liveness — turns until a jealousy trigger fires in a scripted 8-turn roster run | never (∞) | ≤ 8 |

`α`, the morale curve, and `R` are chosen by **sweeping the value that satisfies M1–M7 while holding M6** — that is the number-tuning mechanism.

### 2.2 Half B — LLM component-review sweep

Re-run `<scratchpad>/review_workflow.js` (the 12-component adversarial audit) on **fresh live-play evidence** (a new 6–8 turn playthrough captured with `play.py`) after each **phase**. Record the scoreboard delta vs §1. LLM scores jitter ±0.5, so Half B is *directional*; Half A is *pass/fail*.

### 2.3 Protocol & cadence

```
Every slice:  pytest tests/test_combat_sweep_metrics.py -v        → record M1..M7
Every phase:  boot backend → play 6–8 turns via play.py → LIVE_PLAY_EVIDENCE.md
              Workflow(review_workflow.js) → scoreboard
              write docs/audits/SWEEP_<n>_<date>.md (diff vs baseline + prior sweep)
```
A slice **lands** only when: its behavior test is green, its target Half-A metric moved toward target, and M6 + non-combat regression guards hold. The LLM sweep (~3M tokens) runs once per phase, not per slice.

---

## 3. Root-cause findings (verified against code)

Written into the spec so a fresh session need not re-derive them.

### 3.1 Combat math
- Effective strength = lead marshal only (`combat.py:1018`). Reinforcements are a coordination % (`min(_,0.25)`). → concentration inert.
- Casualties scale by lead-vs-lead `strength_ratio` × `base_rate 0.15`, capped 0.6 (`combat.py:1067–1076`).
- Defender edge = flat `0.2` × terrain/fort/stance (`combat.py:104`).
- Routs gated at morale ≤ `25` (`combat.py:76`) against small `_scaled_morale_loss`; defenders almost never cross it.
- **Survivor two-truths bug:** event `remaining` = `int(marshal.strength)` *after* reinforcement merge vs report `attacker_remaining` = `original − lead-only casualties` (`battle_report.py:865` vs `combat_executor.py:3874`) — contradicts in every multi-marshal battle.

### 3.2 Why Jealousy was DORMANT — the triple lock (verified `jealousy.py`)
The review said "glory needs wins." The real cause is three compounding gates; **all three must be addressed** or the marquee drama engine stays invisible in a normal game:
1. **Stalemate = zero glory.** `record_battle_glory` (jealousy.py:154) only scores when `attacker_won`/`defender_won`. A stalemate (`victor=None`) awards **0 to everyone**, primaries and reinforcing participants alike (:173–208). The combat model produces almost only stalemates ⇒ no glory is ever recorded.
2. **5-turn decay.** `GLORY_WINDOW = 5` (jealousy.py:41); `get_glory_score` sums only events newer than 5 turns (:99–106). Even an occasional point evaporates before it can accumulate into a ladder gap.
3. **High-authority dampening.** `_threshold_for` adds **+1 to every jealousy threshold when `authority > 70`** (`AUTHORITY_SUPPRESS_ABOVE = 70`, jealousy.py:381–384). The player **boots at authority 100** and a competent early game keeps it high — so even a formed gap needs a larger delta to trigger. (Design only lets jealousy accelerate when you are *losing*, `authority < 30`.) Live authority sat 90–100 the whole game.

Consequence: every marshal at glory 0 after 7 turns; the crown churned once (Bernadotte, a lone participant-win) then vacated; no petition ever fired despite Ney's restlessness. Phase 3 fixes all three.

### 3.3 Economy
- **Regressive upkeep:** `cost = (strength // 1000) * rate` (`world_state.py:3869`) scales with surviving strength while income is region-derived ⇒ net income *rose* 1,702→3,250 as the army was attrited (losing pays).
- **All gold sinks conquest-gated** (occupation cost, dotation skim read 0 for a homeland-holding France) ⇒ treasury 800→15,058 unspent; the only firing sink was a 180g rente.

### 3.4 Vassals
- `AUTONOMY_DRIFT = -2` passive with no passive recovery path (`vassal.py:25`); the "war weariness" offset is dead code (always 0) for the player's own satellites (`vassal.py:356`); no lever surfaced in the healthy 100→40 band (`abs(delta)≥3` event gate, `vassal.py:365`). The intended loyalty loop (win battles) is combat-starved.

### 3.5 Parser & play-friction (Phase 6)
Verified locations for each live-found bug are carried in the Phase-6 slice table (§4.7).

---

## 4. THE PHASED PLAN (each phase = one session)

Every phase opens with a **Session Entry** (what to read, what it assumes) and closes with an **Exit / Handoff** (metrics + sweep + STATUS line), so a new session can start at any phase cleanly. Numbers marked *sweep* are chosen in Phase 0 / tuned per §2.

---

### Phase 0 — Baseline & Harness *(no balance change; pure measurement)* — ✅ LANDED July 13, 2026
**Session entry:** read §2, §3. Assumes clean master. No gameplay effect.
- **P0-1** Build `tests/test_combat_sweep_metrics.py` (M1–M7 harness) + a headless battle-sim helper. ✅ Done — deterministic Monte-Carlo (400 fixed seeds) over the REAL `combat.py` / `battle_report.py` / `_distribute_casualties` / `jealousy.py`; 9 tests green.
- **P0-2** Run **Sweep 0**: fill M1–M7 baselines; store `docs/audits/SWEEP_0_2026_07_13.md`. ✅ Done. Half-A baselines: **M1** flat `0.000×5` (concentration inert) · **M1b** `0/0/0` (no personality expression) · **M2** `0.000/0.000` · **M3** `+4251` net (defender GAINS) · **M4** `0.0%` consistency · **M5** `+0.116` payoff · **M6** `0.000` GUARD holds · **M7** `never` (drama dormant). **Half B** = the same-day ⚔️ Field Review scoreboard (§1) — the fresh live evidence Sweep 0 anchors to (no duplicate playthrough; §2.2 re-runs from Sweep 1).
- **Two modelled knobs** (the only forward constants, both at baseline in the harness): `COMMITTED_ALPHA = 0.0` (CO-1 flips it) and `AI_CORPS_REGEN_PER_TURN = 10000` (CO-4 flips it). Everything else is measured from real resolution.
**Exit:** baselines recorded; harness green (asserting *current* values, so later slices flip them). **Test:** the harness itself. **Risk:** none (measurement only).

---

### Phase 1 — Combat core: additive, personality-scaled strength *(the keystone)* — ✅ LANDED July 13, 2026
**Session entry:** read §3.1, Phase 0 baselines. Assumes P0 harness exists.
**Landing (Sweep 1a, `docs/audits/SWEEP_1a_2026_07_13.md`):** α tuned to `COMMITTED_ALPHA = 0.6` (single source `combat_executor.CombatExecutor.COMMITTED_ALPHA`, harness-guarded). M1 flat → `0.000→0.000→0.013→0.355→0.818` (monotonic; 0.82 at 5 corps); M1b `0/0/0` → `41400/36000/0` (aggressive > cautious > hostile); M4 `0%` → `100%`; M6 GUARD held `0.000`; no Phase-2/3 metric regressed. Full suite 13,100/3, ruff clean, no `.gd` touched. New tests `test_combat_overhaul_co1_additive.py` (11) + `..._co5_report_consistency.py` (4); 5 fixtures re-tuned (all confirmed intended — each passes with α=0.0).
- **CO-1 Additive committed strength.** Attacker effective strength = lead effective strength **+ `α`·Σ(committed reinforcer contribution)**, over the muster "WILL JOIN" set (`combat_executor._calculate_reinforcements`). Symmetric for a reinforced defender (GR5). Lives in `combat.py:_calculate_effective_strength` (new `committed` arg); **GR1-safe** (strength, not a modifier).
- **CO-1b Personality- & relationship-scaled contribution (G-1b).** Each reinforcer's contribution = `α · reinforcer.strength · reinforcer.get_combat_effectiveness() · (1 + reinforcer.get_attack_modifier(ratio)) · rel_factor`, where `get_attack_modifier` is READ from the reinforcer (single-source, GR1) and `rel_factor` is the MC-3 coordination scale toward the lead (×0.0 hostile … ×1.25 devoted). Aggressive/high-shock reinforcers push harder; a resentful reinforcer contributes ≈0. Coordination % synergy stays on top.
- **CO-2 Odds band = committed force.** The muster `odds_band` computes on CO-1 committed strength so the read matches resolution.
- **CO-5 Single-source survivor count.** One canonical post-battle strength consumed by BOTH the event and `casualty_summary` (reconcile `battle_report.py:865` ↔ `combat_executor.py:3874`). This is the missing **integration pin**.
**Exit:** ✅ M1 monotonic; **M1b** aggressive>cautious>hostile; M4 = 100% (all met). **Tests:** `test_combat_overhaul_co1_additive.py` (M1 + M1b), `..._co5_report_consistency.py` (solo + multi + reinforced equality). **Sweep 1a** (Half A only) — recorded.

---

### Phase 2 — Decisiveness & counter-pressure — ✅ LANDED July 13, 2026
**Landing (Sweep 1, `docs/audits/SWEEP_1_2026_07_13.md`):** all four slices in.
**CO-3** = `combat.decisiveness_morale_penalty` (out-bled side of a lopsided
casualty exchange breaks faster; pivot 1.75 / slope 22 / cap 55; both morale
paths, GR5; `defender_bonus` untouched, M6 held) → M2 `0.61 @2:1 / 1.00 @3:1`.
**CO-4** = `economy_executor.AI_CORPS_REGEN_CAP = 3000` + `region_has_friendly_supply`;
**SYMMETRIC** (GR5) — ANY corps reinforcing away from a depot/capital recruits a
capped levy, one rule in the shared `_execute_recruit` keyed on the recruit
region's supply (player and enemy alike; the enemy AI needs no special wiring).
Troop `recruit` only — commissioning a new marshal (`_execute_recruit_marshal`)
is untouched (still hires at the capital). Caps troops, gold stays batch price;
harness knob guarded → M3 `−2749`. **CO-6** = the committed effective
strength named in coordinated battles. **CO-7** = Iron Resolve release exempts
the fortify-mandated defensive-stance penalty in `get_attack_modifier` → M5
`+0.24`. Tests: `test_combat_overhaul_phase2.py` (20) + the flipped M2/M3/M5
harness assertions + `test_regen_cap_matches_production`; 3 MC-band fixtures
re-tuned for the deeper decisiveness hit. Suite 13,121/3, ruff clean, no `.gd`.
**Session entry:** read §3.1, Phase 1 landing. Assumes CO-1/CO-2 live.
- **CO-3 Decisiveness → capture.** Steepen defender morale loss on lopsided casualty ratios (tune `_scaled_morale_loss` / `DEFENDER_MORALE_CURVE_FACTOR`, *sweep*) so a heavily-outnumbered defender crosses the rout threshold → forced retreat → the pursuer takes the province (the plunder/secure pipeline finally fires). Do NOT lower `defender_bonus` (M6).
- **CO-4 Cap enemy regeneration.** Shared helper caps per-corps strength regrowth to `R` men/turn (*sweep*, start 3,000) unless in a friendly depot/capital; retreat-recovery & player recruit untouched; applies to the enemy recruit rung (`enemy_ai.py` P1/P4.5/P7) + garrison→corps top-ups. GR5: same helper both sides.
- **CO-6 Reinforcement legibility.** Battle strength breakdown names contributors + summed effective strength (restore the commented reinforcement detail, `battle_report.py:146`).
- **CO-7 Iron Resolve stance fix.** Releasing Iron Resolve is not self-cancelled by the defensive stance the fortify required (auto-restore neutral on unfortify-to-attack, OR exempt the release from the defensive-stance penalty). Net payoff ≥ M5.
**Exit:** M2, M3, M5 at target; M6 held; a scripted 3:1 assault produces a rout + capture choice. **Tests:** `..._co3_decisiveness.py`, `..._co4_regen_cap.py`, `..._co6_reinforce_legible.py`, `..._co7_iron_resolve.py`. **Sweep 1** (Half A + Half B): Combat should reach ≥7.0.

---

### Phase 3 — Un-starve Marshal Drama (break the triple lock) — ✅ COMPLETE July 14, 2026 (Half A + Half B)
**Landing (Half A):** all three locks broken in `jealousy.py`; **M7 flipped `never → turn 1`** (the winnable massed-assault roster run) with M1–M6 held, full suite 13,146/3, ruff clean, no `.gd` touched. New tests `test_drama_glory_from_attrition.py` (15) + `test_drama_ladder_liveness.py` (10); 106 existing jealousy tests unchanged-green. Constants are in-band tunable single sources in `jealousy.py`.
**✅ Sweep 2 (Half B) RAN July 14, 2026 — `docs/audits/SWEEP_2_2026_07_14.md`:** the 12-component LLM review (13 agents / ~1.43M tokens) on a fresh 6-turn `LLM_MODE=anthropic` France/1805 playthrough (`docs/audits/SWEEP_2_LIVE_EVIDENCE_2026_07_14.md`). **Marshal Drama 6.0 → 7.5 (met target, +1.5)**; Narration 7.5→8.0, Marshal System 7.0→7.5, Architecture 7.5→8.0 (all +0.5); 8 pillars held flat, **0 regressions**; overall directional ≈7.15–7.25 (right at the ≥7.3 line). **An organic petition fired FOUR times across three kinds + the Fontainebleau collective beat** (M7 in the wild: turn 2), with DR-1/DR-2/DR-3 all confirmed live and the Jealousy↔ES-7 rente economy interlocked. Two honest caveats (no autonomous glory-attack executed live; the crown never lit on a top tie — both WAD evidence gaps for a differently-driven session, not defects). **Phase 3 EXITS.**
**Session entry:** read §3.2 (the triple lock). Assumes Phases 1–2 landed (wins now reachable).
- **DR-1 Glory from attrition/occupation (G-6).** ✅ `record_battle_glory` now awards `STALEMATE_GLORY = 1` for an **inconclusive** battle where one side **out-bleeds the other ≥2:1** (new `_out_bled` predicate — flawless exchange counts) **or takes a province** — symmetric player/enemy (GR5). A hard-fought grind feeds the ladder before a clean rout. Clean-win scoring is unchanged (regression-pinned).
- **DR-2 Slow glory decay.** ✅ `GLORY_WINDOW` lengthened `5 → 8` (the sole glory-decay lever) so occasional deeds accrete into a ladder gap instead of evaporating at turn 6.
- **DR-3 Authority dampening rework.** ✅ Chose the **"exempt the first rung"** option: the `authority>70 ⇒ +1 threshold` calm now applies **only to rung ≥ 2 (neutral/friendly professionals)**; a marshal who already resents the celebrated man (a Rival −1 / Hostile −2, relationship-base threshold 1) keeps his hair-trigger edge even at the height of empire. Keyed on the *relationship* base (before idle acceleration), so an idle-accelerated professional is still calmed while winning. The `authority<30` death-spiral acceleration is untouched (pinned). The existing professional-pair dampening test is unchanged-green (it uses a rung-2 pair).
  - **Harness note (M7):** the Phase-0 `measure_m7` scenario modeled a *losing* 1:1 assault (attacker out-BLED every turn ⇒ zero glory is correct for losing), which never reproduced the triple lock the spec describes (a player *winning* the attrition earning no glory). Phase 3 re-frames it to the review's **winnable ~3:1 massed assault** into a dug-in defender — the attacker out-damages but the fort resists a clean rout — which is dormant under baseline jealousy constants and lively under Phase 3. Documented in the test docstring.
**Exit:** ✅ **M7** ≤ 8 (jealousy trigger fires turn 1 in the scripted roster run; **turn 2 in the wild**); ✅ a live playthrough surfaced a petition organically (four, across three kinds — Sweep 2). **Tests:** `test_drama_glory_from_attrition.py` ✅, `test_drama_ladder_liveness.py` ✅ (M7). **Sweep 2** (Half B): ✅ Marshal Drama **7.5** (met), 0 regressions — `docs/audits/SWEEP_2_2026_07_14.md`.

---

### Phase 4 — Economy — ✅ COMPLETE July 14, 2026 (Half A + Half B; Economy 5.0 → **6.5**, target MET)
**Landing (Half A):** both slices in, backend + one `.gd`, suite 13,167/3, ruff clean, Godot parse-clean.
- **EC-U1 Non-regressive upkeep.** ⏪ **REVERSED July 14, 2026 (user-directed, after the Sweep-3 economy playthrough).** Upkeep now bills on a corps' **ACTUAL fielded strength** — "you pay for the soldiers you have." The establishment high-water-mark, `Marshal.establishment`, `get_upkeep_strength`, and `_reconcile_establishments` were all removed; `calculate_turn_upkeep` bills `(marshal.strength // 1000) * rate`, and the over-limit + Grande Armée surcharges now key off the live fielded total (a shrinking army sheds its surcharge too). Boot is byte-identical (billed == strength at turn 1), so the E1 band, ES-3, and EC-U3 numbers are untouched; the change only bites after attrition — a battered corps is now cheaper (the demobilization relief the playtest flagged), and the ledger's army total reflects the men actually present, not a phantom peak. Pin: `test_economy_upkeep_fielded_strength.py`. The original establishment design is preserved below for history:
  - ✅ Chose the **establishment high-water-mark** option (not the flat per-corps floor — a floor still leaks in the above-floor band). New serialized `Marshal.establishment`, reconciled once per turn (`WorldState._reconcile_establishments`, GR8 bounded loop); Europe upkeep is billed on `max(strength, establishment)` (`marshal.get_upkeep_strength`, single source) so grinding a corps down no longer LOWERS its bill. Establishment is **0 until the first reconcile**, so every direct-call upkeep test AND the E1 boot band (Austria +18) are byte-unchanged — the change only bites after a turn of play. Era-grounded: the state maintained corps at establishment; losses obliged paid replacements, never a rebate. Legacy world keeps strength-proportional upkeep (N1). Ledger stays transparent (per-marshal `billed_strength` in the upkeep breakdown).
- **EC-U2 A gold sink reachable without conquest.** ✅ Chose **infrastructure/depot upkeep** (the boot-solvency-safe option — ally-subsidy/army-size recurring drains would hit every nation at boot and break Austria +18). New `EUROPE_INFRASTRUCTURE_UPKEEP = 40` g/turn per built structure (depots, forts, training grounds, markets, stables, active/damaged watchtowers), rides the existing per-region income loop (GR8, no new scan), bankruptcy-mercy halved like occupation, its own signed **"Infrastructure"** Net component (threaded through `process_income_phase`, `ledger.py`, `meta_executor`, `dispatch`, `strategic_ledger.gd`, and `NET_GOLD_COMPONENTS`). Boot-safe (the 1805 scenario authors no buildings → 0 at turn 1 for all nations). Symmetric player/AI (GR5). A homeland-only France now decides whether to invest its surplus in infrastructure and carry the recurring bill, or hoard.
**Exit:** ✅ attrition does not increase net income (`test_economy_upkeep_not_regressive.py`, incl. a falsifiable counterfactual that the bug reproduces with the fix removed); ✅ a homeland-only France has a meaningful gold decision reachable without conquest (`test_economy_sink_reachable.py`). **Tests:** `test_economy_upkeep_not_regressive.py` (13), `test_economy_sink_reachable.py` (10), `NET_GOLD_COMPONENTS` extended. **Post-landing refinement `2ce1f1d`:** Sweep 3 caught EC-U1's turn-1 window (establishment seeded 0, first reconcile ran after turn-1 combat) → seeded the boot peak in `from_scenario` (boot-safe, billed==strength at boot). **✅ Sweep 3 (Half B) RAN July 14, 2026 — `docs/audits/SWEEP_3_2026_07_14.md`:** 12-component LLM review (13 agents / ~1.18M tokens). **Economy 5.0 → 6.0 (+1.0), ZERO regressions, 11 pillars held.** The core "losing pays" bug is reproduced-and-closed (engine probe: −85k men → net flat +1652 with the fix vs +2584 without) and the first conquest-free sink exists and is transparent — but **Economy is 0.5 SHORT of the ≥6.5 target**: the loose-gold surplus is structural (homeland income ~+3,400 ≫ upkeep ~+1,748), so the two scoped levers can't force scarcity. **User steer → the gated upkeep-baseline revisit: EC-U3 Grande Armée surcharge LANDED `9d57597`** — a premium upkeep rate (`GRANDE_ARMEE_RATE=18` g/1,000 above the absolute `GRANDE_ARMEE_THRESHOLD=140000`) modelling a supermassive army's diseconomies of scale; at boot it touches ONLY France (189k; Austria +18 byte-unchanged), lifting France's turn-1 absorption 36.9%→55.5% (into the EC-2 aspirational band), cutting the homeland surplus −29%, making a doubled army the edge of sustainability (no death-spiral). **EC-U3 re-score (2-agent adversarial): Economy 6.0 → 6.5, target MET, ZERO regressions** (six checks: boot solvency, GR5 symmetry, ledger reconciliation, doubled-army sustainability, test honesty, no serialization/Godot/scale break). E1 + ES-3 tests re-blessed; ledger/turn-summary split the surcharge into over-limit + Grande Armée. **Phase 4 COMPLETE — Economy 6.5.**

---

### Phase 5 — Vassals — ✅ HALF A LANDED July 14, 2026
**Session entry:** read §3.4.
- **VS-1 Loyalty recovery lever + teach it.** ✅ Landed. The event gate lowered `abs(delta) ≥ 3 → ≥ 2` (`vassal.py`), so the steady satellite bleed (-2/turn) now surfaces every turn instead of hiding until it crossed 20. A **recovery hint** ("Invest, garrison their capital, or grant autonomy to steady them.") rides the `vassal_loyalty` event (new `recovery_hint` field, folded into the dispatch `message`) whenever a vassal is *falling while still in the healthy band* (`delta < 0 and new_loyalty ≥ 40`) — the recovery loop is now discoverable BEFORE the `≤ 10` crisis popup. Talleyrand's `< 35` dispatch advisory also names the three levers. The arresting actions already existed (invest +10, garrison +5..8, grant-autonomy flips drift to +1) — VS-1 makes them *visible and taught*.
- **VS-2 Dead-code cleanup.** ✅ DELETED. The `get_coalition_loyalty_penalty` "war weariness" contribution (`vassal.py`) was always 0 for a lord's own satellite (never a coalition member AGAINST its lord); coalition membership is a diplomatic-acceptance concept, not a loyalty-drift one. Removed; loyalty drift is now independent of coalition state. (The prior `test_deep_audit_session2.py::TestFix17...` pin was flipped to assert the removal.)
**Exit:** ✅ a falling vassal can be arrested by a surfaced action — the recovery hint names the levers on the very turn the slide surfaces. **Tests:** `test_vassal_recovery_lever.py` (9); Fix17 pin re-blessed. Suite 13,177/3, ruff clean, no `.gd`. **✅ Sweep 4 (Half B) RAN July 15, 2026 — `docs/audits/SWEEP_4_2026_07_15.md`:** the 12-component adversarial review (25 agents / ~2.45M tokens) over a deterministic engine probe + live-HTTP surface prong. **Vassals & Coalition 6.0 → 6.5 (target MET, at the floor); UX 6.5 → 7.0; ten pillars held; ZERO regressions.** The July-14 playtest had scored the pillar exactly 6.0, dragged down by VS-1 teaching *broken* levers — the 10 fixes (`016bf71`) removed that drag and VS-R added the real content (the derived-grip crux: live, `authority` stayed 65 "Respected" while `get_imperial_grip` spiralled to 25 when Paris fell → −2 drift, invest blunted ×0.4, spiral hint). Held short of 7 by the unbuilt coalition-defection beat + VS-R being collapse-only + the still-inert garrison lever (VP-D1). Recommendations routed: P0 wire-or-remove garrison (VP-D1), P1 coalition-defection (GR9) + VS-3 land grants, P2 the "grant X **more** autonomy" pre-parse gap (→ Sweep 5) + tribute-cut legibility (VP-D5) + enemy-AI grip-awareness (VP-D6) + dual-derivation reconcile (VP-D7). **Phase 5 COMPLETE. ▶ NEXT: Sweep 5** (Phase 6 already landed at `3c0246a`).

---

### Phase 6 — Parser & Play-Friction Cleanup *(all live-found bugs)* — ✅ LANDED July 15, 2026
**Landing:** all ten fixes in, backend-only (**no `.gd` touched** — every display rides an existing passthrough), suite **13,314/3**, ruff clean. A 4-round adversarial verification (~30 agents) caught **8 real defects**, all fixed before landing: PF-2's printed-phrase alias gap (the literal ASK prints "observe {who}"), PF-3's strategic-execution capture-guard block + multi/cross-marshal single-slot clobber (fixed by scoping the capture to auto-secure during strategic execution with a save-and-restore of any prior `pending_capture_choice`), PF-5's weak production tests (added `_ratify_treaty` / `_process_dotation_state` mutation-verified guards) + a GR9 unowned `changed` flag (removed — the notification-rail dedup is the real fix), PF-7's `"gun"` substring colliding with region "Burgundy" (word-boundary regex), PF-8's PURSUE silent re-stall (mirrored the MOVE_TO break-with-reason). A false-positive round-2 "PF-4 charge gap" was **refuted** and reverted — `charge`/`bombard` are deliberately not in `objection_actions`, so they never raise a tactical objection and need no reachability gate (PF-4 stays scoped to `attack`). Final convergence check: CONVERGED, zero residual defects (the only remaining single-slot overwrite, attack-then-attack, is pre-existing and inherent to the one-slot/one-response design). **Notable design decisions:** PF-3 = direct move-capture pops the choice / strategic-march hop auto-secures like the AI; AI-1 = behavior-preserving *relabel* (P4.78→P7.4) not a reorder, to preserve enemy-AI precedence; PF-6 = announce the 2-AP upgrade, do not re-price (V2-58 stands). **▶ NEXT: Sweep 5 (Half B).**

**Session entry:** read §3.5 + the table. Each is a small, independent fix; batch as one session.

| ID | Bug (live symptom) | Location | Fix / test |
|---|---|---|---|
| **PF-1** | "march **on** Tyrol" → target "On Tyrol"; bare preposition never stripped | `strategic_parser.py` `_clean_target_text` (~:239) | strip leading preposition; `test_pf1_march_on.py` |
| **PF-2** | Delegation ASK offers "give battle"/"observe" but answering "give battle" → "Region 'generic' not found" (target not rebound) | `delegation.py:517–544` vs `clarification.py:300–365`; `main.py:1054` pops clarification before classifying | rebind the ASK's original target to the offered answer; `test_pf2_delegation_ask.py` |
| **PF-3** | Occupying an empty enemy province doesn't capture it and gives **zero** feedback | occupation wiring lives only in the post-combat path | flip control on uncontested occupation (or narrate "occupied — control flips end of turn") + surface it; `test_pf3_occupation_capture.py` |
| **PF-4** | Objection fires for an **unreachable** order (range checked only after INSIST) — wastes a trust-costing decision | pre-objection block in `executor.py` (~:1030) gates AP/fortify/friendly-fire but not reachability; range gate is inside `_execute_attack` (`combat_executor.py:2898`) | pre-validate range/reachability before the objection check; `test_pf4_objection_before_range.py` |
| **PF-5** | Persistent NOTE spam — "Treaty with Y" / "Action Accepted" / "expects reward" re-render every turn | notifications never `dismiss_by_type` for `TREATY_SIGNED`/`DIPLOMATIC_PROPOSAL_RESULT`; the reward roll-up re-renders | dismiss-by-type on consume; suppress unchanged reward roll-up; `test_pf5_notification_dedup.py` |
| **PF-6** | "hold your ground" silently becomes a 2-AP strategic HOLD for non-literal marshals | `strategic_executor.py:1135` | announce the upgrade inline (or price it 1 AP); `test_pf6_hold_cost_legible.py` |
| **PF-7** | `recruit 5000 artillery for Soult` ignores BOTH amount and arm → default 10k infantry; "bombard" with no artillery silently degrades to attack | recruit parser (`llm_client.py` mock + `economy_executor._execute_recruit`) | honor amount + arm, or reject clearly; guard bombard on artillery presence; `test_pf7_recruit_arm_amount.py` |
| **PF-8** | Strategic MOVE_TO routes through **hostile** territory (Artois→Westphalia/Hanover→Flanders) and stalls with no feedback | pathfinder in the strategic-move path | prefer friendly/open-borders routes; on stall, say why; `test_pf8_pathfinding_route.py` |
| **PF-9** | Nations tab shows a treaty counterparty-/war-blind — Russia rendered `[open_borders]` while at WAR (a 3rd-party Russia-Sweden edge) | `diplomatic_ledger.py:267–272` | scope treaty display by counterparty + war state; `test_pf9_treaty_display_scope.py` |
| **AI-1** | Enemy-AI priority tiers decoupled from evaluation order (P4.78 unreachable after P7, both priority 7) — latent tech-debt | `enemy_ai.py:1901/:1908` | renumber/reorder so tiers are reachable; `test_ai1_priority_order.py` |

**Exit:** all PF/AI tests green; a `.gd`-touching fix (PF-3/PF-6 display) boots the engine clean (grep `SCRIPT ERROR`). **Sweep 5** (Half B): Parsing ≥7.5, UX ≥7.0, Narration ≥7.5, Diplomacy held ≥8.0.

---

## 5. Golden-Rule compliance (build-time guardrails)

- **GR1:** CO-1/CO-3/CO-4 change *strength & morale* in `combat.py`; CO-1b **reads** each reinforcer's `get_attack_modifier` (never recomputes it); CO-7 changes stance *state*, reads the existing modifier. No modifier math leaves `marshal.py`.
- **GR2:** new fields to Godot (CO-6 strength breakdown, CO-3 rout flags, PF-3 occupation narration) are `int()`-cast where numeric.
- **GR5:** additive strength, decisiveness, and the regen cap are ONE shared code path for enemy & player (seeded by different inputs). No enemy-only combat branch.
- **GR8:** the reinforcement sum iterates the bounded muster set, not `world.regions.values()`. No new per-region hot-path scan.
- **GR9:** every slice above has owner (this spec), landing (phase/slice id), completion, a STATUS line (§7), and a behavior test.

---

## 6. Serialization impact

- CO-3 rout/decisiveness flags: transient unless persisted across the turn — if persisted, add to `to_dict`/`from_dict` + `tests/test_serialization_enforcement.py` + `docs/SAVE_FORMAT_REFERENCE.md`.
- DR-2 (glory window) touches existing `glory_events` only. CO-4 reads existing supply/depot state — no new field expected.
- Any new persisted field follows the mandatory serialization checklist.

---

## 7. STATUS tracking

| Phase / slice | State | Metric | Landed (SHA) |
|---|---|---|---|
| Phase 0 — harness + Sweep 0 | ✅ **LANDED July 13, 2026** | M1–M7 baseline captured | `9abd89f` |
| CO-1 additive strength | ✅ **LANDED July 13, 2026** | M1 ✅ monotonic | (Phase 1 commit) |
| CO-1b personality/relationship scaling | ✅ **LANDED July 13, 2026** | M1b ✅ agg>cau>hostile | (Phase 1 commit) |
| CO-2 odds band | ✅ **LANDED July 13, 2026** | M1 (committed) | (Phase 1 commit) |
| CO-5 report single-source | ✅ **LANDED July 13, 2026** | M4 ✅ 100% | (Phase 1 commit) |
| CO-3 decisiveness → capture | ✅ **LANDED July 13, 2026** | M2 ✅ 0.61/1.00 | (Phase 2 commit) |
| CO-4 regen cap | ✅ **LANDED July 13, 2026** | M3 ✅ −2749 | (Phase 2 commit) |
| CO-6 reinforcement legibility | ✅ **LANDED July 13, 2026** | Half B | (Phase 2 commit) |
| CO-7 Iron Resolve stance | ✅ **LANDED July 13, 2026** | M5 ✅ +0.24 | (Phase 2 commit) |
| DR-1 glory from attrition | ✅ **LANDED July 14, 2026** | M7 ✅ turn 1 | `38324bf` |
| DR-2 glory decay | ✅ **LANDED July 14, 2026** | M7 ✅ turn 1 | `38324bf` |
| DR-3 authority dampening | ✅ **LANDED July 14, 2026** | M7 ✅ turn 1 | `38324bf` |
| **Sweep 2 (Half B)** | ✅ **RAN July 14, 2026** | Drama 6.0→**7.5** met; 0 regressions | `SWEEP_2_2026_07_14.md` |
| EC-U1 upkeep | ⏪ **REVERSED July 14, 2026** — bills on ACTUAL fielded strength (establishment removed) | attrition lowers the bill; boot byte-identical | `0997eac` + `2ce1f1d` (orig), reversal this session |
| EC-U2 gold sink (infrastructure) | ✅ **LANDED July 14, 2026** | conquest-free sink reachable | `0997eac` |
| EC-U3 Grande Armée surcharge | ✅ **LANDED July 14, 2026** | France absorption 36.9%→55.5% | `9d57597` |
| **Sweep 3 (Half B)** | ✅ **RAN July 14, 2026** | Economy 5.0→6.0→**6.5** (target MET via EC-U3); 0 regressions | `SWEEP_3_2026_07_14.md` |
| VS-1 loyalty lever / VS-2 dead code / VS-R coupling | ✅ **LANDED July 14, 2026** — event gate 3→2, grip-aware recovery hint; war-weariness dead term deleted; VS-R authority↔loyalty coupling + 10 playtest fixes | (Sweep 4 ✅ below) | `4392c30`/`9131df6`/`016bf71` |
| **Sweep 4 (Half B)** | ✅ **RAN July 15, 2026** | Vassals 6.0→**6.5** (target MET, at the floor); UX 6.5→7.0; 0 regressions | `SWEEP_4_2026_07_15.md` |
| PF-1…PF-9 + AI-1 | ✅ **LANDED July 15, 2026** — all 10 live-found fixes; 4-round adversarial verify (8 defects caught + fixed); backend-only, no `.gd` | Sweep 5 (Half B) pending | `3c0246a` |
| Sweep 5 + exit sweep | NOT STARTED | full | — |

Update `docs/STATUS.md` Next Steps and CLAUDE.md Current Phase Queue when Phase 0 begins.

---

## 8. Program exit criteria

- **Half A:** M1–M7 at target (M4=100%, M2/M3 pass, M7≤8, M6 held).
- **Half B:** Combat ≥7.5, Economy ≥6.5, Drama ≥7.5, Vassals ≥6.5, Parsing ≥7.5, Overall ≥7.3, no non-combat component regressed ≥0.5.
- A fair live playthrough can reach a **decisive field victory + a province capture**, and a **jealousy petition fires organically** — the two things the review's live proof showed *never* happened.
- Full pytest suite green; pre-commit gate un-bypassed; `.gd`-touching slices boot clean.

---

## 9. Risk register

- **R1 Over-correction (M6 fails):** additive + decisive offense could trivialize defense. Mitigation: M6 gate; tune `α`/curve conservatively; the AI benefits symmetrically (GR5), so an over-buffed offense also makes the *player* fragile.
- **R2 AI feels punished by the regen cap:** must not make the AI passive/farmable. Mitigation: symmetric cap; depots/capitals exempt; re-run the Enemy-AI lens in Sweep 1 to confirm it holds ≥8.
- **R3 Balance whack-a-mole across coupled systems:** decisiveness cascades into diplomacy/settlement/economy. Mitigation: the full 12-component sweep is the regression net.
- **R4 LLM sweep noise (±0.5):** Half A is the hard gate; Half B is read across two sweeps.
- **R5 Drama over-fires after the triple-lock unlock:** breaking all three gates at once could make jealousy spam. Mitigation: M7 targets a *single* trigger ≤8 turns, not a flood; tune DR-2/DR-3 to a simmer.

---

*Prepared from the ⚔️ Field Review. Scope blessed July 13, 2026; numbers are sweep-tuned. Build order: Phase 0 (Sweep 0) → Phase 1 → Phase 2 (Sweep 1) → Phase 3 (Sweep 2) → Phase 4 (Sweep 3) → Phase 5 (Sweep 4) → Phase 6 (Sweep 5) → exit sweep.*
