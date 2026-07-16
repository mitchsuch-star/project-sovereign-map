# COMBAT OVERHAUL — EXIT SWEEP (Program Close-Out)

**Date:** July 16, 2026
**Owner:** `docs/COMBAT_OVERHAUL_SPEC.md` §1 (baseline & targets) + §2 (sweep protocol).
**Basis:** the Sweep-5 measurement (`SWEEP_5_2026_07_16.md` — 12-component adversarial
review, 28 agents, fresh live evidence, all targets met, zero regressions) + the
**exit-run**: the two conditions the Sweep-5 synthesis set for program close, both
honored same-session.

The exit sweep deliberately does NOT re-run a 13th full review of the same code state —
Sweep 5 measured current master + the session fixes hours earlier; a re-run would
re-measure identical bytes inside LLM jitter. The exit sweep is the **program verdict**:
the baseline→final table, the zero-regression audit trail across all six sweeps, and the
scripted exit scenarios Sweep 5 required.

---

## 1. The program table — baseline (July 13) → final (July 16)

| Component | Baseline | Target | **Final** | Verdict |
|---|---|---|---|---|
| Combat System | **5.0** | 7.5 | **7.5** | ✅ MET (Sweep 1; held through 4 subsequent sweeps) |
| Economy | **5.0** | 6.5 | **6.5** | ✅ MET (Sweep 3 + EC-U3 re-score; held) |
| Marshal Drama | **6.0** | 7.5 | **7.5** | ✅ MET (Sweep 2; both WAD evidence gaps closed live at Sweep 5) |
| Vassals & Coalition | **6.0** | 6.5 | **7.5** | ✅ **EXCEEDED** (Sweep 4 met at the floor; the Vassal Depth track then landed the entire rec ladder) |
| Narration & Legibility | 7.0 | 7.5 | **8.0** | ✅ EXCEEDED |
| Marshal System | 6.5 | 7.0 | **8.0** | ✅ EXCEEDED |
| Command Parsing / NLU | 7.0 | 7.5 | **7.5** | ✅ MET (Sweep 5 — five live-found defect classes fixed in-sweep) |
| UX / Flow / State | 6.5 | 7.0 | **7.0** | ✅ MET (Sweep 4; held at Sweep 5 with three wedge classes killed + the P0 500 landed) |
| Diplomacy | 8.0 | ≥8.0 | **8.5** | ✅ EXCEEDED (hold target; rose on real acceptance-path fixes) |
| Enemy AI | 8.0 | ≥8.0 | **8.0** | ✅ MET (held all six sweeps; the regen cap never became farmable) |
| Settlement / Peace | 7.0 | ≥7.0 | **7.5** | ✅ EXCEEDED (VS-5 vassal_transfer + two acceptance-path bug fixes) |
| Architecture & Tests | 7.0 | 7.5 | **8.0** | ✅ EXCEEDED |
| **Overall (directional mean)** | **6.4** | **≥7.3** | **≈7.6** | ✅ **MET** |

**Every target met or exceeded; zero program regressions** — each sweep's regression
check returned NONE, and every claimed regression across all six sweeps was either
adversarially refuted or verified pre-existing at the measured commit.

## 2. The sweep audit trail

| Sweep | Date | Phase measured | Target result | Regressions |
|---|---|---|---|---|
| 0 | July 13 | baseline harness | M1–M7 baselines pinned | — |
| 1a | July 13 | Phase 1 (additive committed strength) | M1/M1b/M4 flipped to target | 0 |
| 1 | July 13 | Phase 2 (decisiveness/regen/Iron Resolve) | **Combat 5.0→7.5 MET**; M2/M3/M5 to target | 0 |
| 2 | July 14 | Phase 3 (drama triple lock) | **Drama 6.0→7.5 MET**; M7 never→turn 1 (turn 2 wild) | 0 |
| 3 | July 14 | Phase 4 (economy) | **Economy 5.0→6.0→6.5 MET** (EC-U3 re-score) | 0 |
| 4 | July 15 | Phase 5 (vassals) | **Vassals 6.0→6.5 MET**; UX 6.5→7.0 | 0 |
| 5 | July 16 | Phase 6 (parser/friction) + delta | **Parsing 7.0→7.5 MET**; UX/Narration/Diplomacy targets held; +5 pillars rose | 0 |

Half-A state at close: M1–M7 byte-identical since Sweep 1's flips (`M1 0.000→0.818`
monotone, `M2 0.613/1.000`, `M3 −2749`, `M4 100%`, `M5 +0.240`, `M6 0.000` guard,
`M7 turn 1`); full suite **13,551 passed / 3 skipped**; ruff clean; corpus mock 433/433 +
live 432/432.

## 3. The two exit conditions (set by the Sweep-5 synthesis) — both honored

**Condition 1 — the P0 end-turn 500 lands before the exit run: DONE.**
`_build_result_response` now routes `enemy_phase` through `_build_visible_enemy_phase`
(strip per-action `new_state` + fog-filter) — the poison (tuple-keyed WorldState caches
crashing `jsonable_encoder` after the turn advanced) was reproduced in isolation, then
killed; `tests/test_sweep5_end_turn_500.py` (4). **Exit-run proof:** six end turns with
capture choices pending during strategic processing — the exact live crash shape —
**zero 500s** (turns 3 and 4 surfaced their capture choices cleanly and the ledger line
rendered every turn).

**Condition 2 — the three live-evidence gaps scripted into the exit run**
(fresh 1805 boot, `LLM_MODE=anthropic`, debug cheats staging the states real play
reaches slowly; capture: scratchpad `exit_evidence.jsonl`):

- **A. Reward-economy transactional half — FULLY EXERCISED.** `endow Ney with the Duchy
  of Swabia` → *"By Imperial decree, Marshal Ney is endowed with Swabia and styled Duke
  of Swabia. Its revenues (93g/turn) now sustain his household, not the treasury.
  Investiture: 200 gold. His expectation is met — his loyalty will bleed no further."*
  The ledger then carries a live **"Dotations: −96g"** component growing with the
  province (−96→−108 across five turns). `grant Ney a pension` → the rente instrument
  priced honestly (*"a rente of 64g/turn... it will cost the crown 96g/turn — paper is
  dearer than land, Sire, and it buys no title"*) with a live **"Rentes: −96g"** ledger
  component every subsequent turn. Grant → redirect → recurring cost → expectation state:
  the whole transactional loop live.
- **C. Low-loyalty vassal arc — FIRED LIVE.** Switzerland staged to loyalty 30 (below
  both VS-4 tiers and the VS-6 band); a fresh Prussian war declared. End of turn 2: the
  **`vassal_rebellion` event fired** — the disaffected satellite left the Empire into
  open war (Talleyrand, turn 5: *"Against Switzerland: the war hangs in the balance"*),
  with per-turn `vassal_loyalty` bleed events before it. The enemy-side beats that are
  probabilistic (VS-6 bribe) or boot-dormant (VP-D6 — no AI lord holds a satellite in
  1805) remain covered by their unit tests; recorded honestly, not claimed live.
- **B. Settlement flow — OPENED, not ratified.** `propose peace to Austria` → *"I have
  prepared terms appropriate to the current military situation"* — the terms-guidance
  flow opens live. A full live ratification exercising the VS-5 `vassal_transfer` clause
  through the F1 wizard (the real player surface) is **routed to 8.EVAL** — the seam
  itself is end-to-end covered by the VS-5 test set (31) incl. ratify-side pricing
  parity, per the Sweep-5 settlement review.

## 4. Routed forward (nothing orphaned)

- `BUG_FIXES.md` §Sweep-5: S5-1 Moore AI loop (P1), S5-2 camelCase R7 leaks (P1),
  S5-3 stale dotation rail (P2), S5-4 preempt QUEUE_CAP overflow (P2), S5-5 PF-7 lows (P2).
- `DESIGN_REFINEMENT.md` §Sweep-5: S5-D1 bare-"attack" gate inversion (P1 — CR-6 gate
  candidate), S5-D2 PF-8 issuance honesty (P2), S5-D3 architecture hygiene (P3).
- **8.EVAL** additionally owns: the live wizard-path settlement ratification w/
  vassal_transfer (exit gap B), plus its standing war-LLM/diplomacy triage
  (DWL-DIP-E7, DWL-DIP-METTERNICH, DESIGN_REFINEMENT queue items 5-6).

## 5. Verdict — THE COMBAT OVERHAUL & SCORE-RAISING PROGRAM IS CLOSED

Six phases built, six sweeps measured, every §1 target met or exceeded, zero program
regressions, and the two exit conditions honored with live proof. The program lifted the
game's directional mean from **6.4 to ≈7.6** in three days of build-and-measure, and its
worst live moment (the end-turn 500) was found by its own final sweep and fixed before
close. **Next per the queue: 8.EVAL → Phase 8.5.**
