# SWEEP 3 — Live economy evidence (Combat Overhaul Phase 4)

**Date:** July 14, 2026 · France / 1805, real backend over HTTP (port 8005) + a real-engine EC-U1 probe. The per-turn economy is **mode-independent** (`calculate_turn_income`/`calculate_turn_upkeep` never call the LLM), so the trajectory below was captured in `LLM_MODE=mock` for determinism; the `LLM_MODE=anthropic` wire was separately spot-checked green (fresh end-turn and a multi-region-build end-turn both HTTP 200; one non-reproducible 500 in the anthropic response-encoding path — a pre-existing edge unrelated to the Phase-4 economy diff, which adds only int fields and runs identically here).

## Prong 1 — live HTTP playthrough (EC-U2 sink + trajectory + transparency)

**Builds issued (EC-U2 — a homeland, conquest-free spend):**
- `build fortification in Paris` → Construction started: Fortification in Paris (3 turns, 400 gold)
- `build supply depot in Paris` → Already constructing fortification in Paris
- `build fortification in Lorraine` → Construction started: Fortification in Lorraine (3 turns, 400 gold)
- `build fortification in Rhineland` → No administrative actions remaining this turn. (Military commands: 4 remaining)

**Per-turn economy (ledger, France):**

| Turn | Treasury | Income | Upkeep base | Surcharge | **Infra** | Army str | Net | Note |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 3400 | 1512 | 236 | 0 | 189000 | +2939 | boot — infra 0 (boot-safe) |
| 1 | 2506 | 3200 | 1512 | 244 | 0 | 189000 | +2556 |  |
| 2 | 5062 | 3200 | 1512 | 244 | 0 | 189000 | +2556 |  |
| 3 | 7397 | 3172 | 1512 | 244 | 80 | 189000 | +2335 | infra 0→80 (structure completed) |
| 4 | 9706 | 3146 | 1512 | 244 | 80 | 189000 | +2309 |  |
| 5 | 12018 | 3149 | 1512 | 244 | 80 | 189000 | +2312 |  |
| 6 | 14142 | 3052 | 1512 | 256 | 80 | 189000 | +2124 |  |
| 7 | 16333 | 2955 | 1376 | 196 | 80 | 172000 | +2191 |  |

**Turn-end financial summaries (the `meta_executor` line — note the new `Infrastructure: -Ng` component once structures complete):**
- T1: Income: 3200g | Upkeep: 1756g (incl. 244g over-limit) | Other: +1062g | Net: +2506g | Spent: 800g | Treasury: 2,506g
- T2: Income: 3200g | Upkeep: 1756g (incl. 244g over-limit) | Other: +1112g | Net: +2556g | Treasury: 5,062g
- T3: Income: 3172g | Infrastructure: -80g | Upkeep: 1756g (incl. 244g over-limit) | Other: +999g | Net: +2335g | Treasury: 7,397g
- T4: Income: 3146g | Infrastructure: -80g | Upkeep: 1756g (incl. 244g over-limit) | Other: +999g | Net: +2309g | Treasury: 9,706g
- T5: Income: 3149g | Infrastructure: -80g | Upkeep: 1756g (incl. 244g over-limit) | Other: +999g | Net: +2312g | Treasury: 12,018g
- T6: Income: 3052g | Infrastructure: -80g | Upkeep: 1768g (incl. 256g over-limit) | Other: +920g | Net: +2124g | Treasury: 14,142g
- T7: Income: 2955g | Infrastructure: -80g | Upkeep: 1572g (incl. 196g over-limit) | Other: +888g | Net: +2191g | Treasury: 16,333g

## Prong 2 — engine probe: EC-U1 non-regressive upkeep (real from_scenario world)

Grind every French corps to 55% strength (a *losing* campaign) and read net income before vs after — WITH the establishment fix, then WITHOUT it (`establishment → 0`, the pre-fix behaviour). Region income is unchanged by attrition, so any net *rise* is the regressive bug.

- French army strength: **189,000 → 103,950** (−85,050, a heavy loss)

| | Upkeep | Net income | Δ net vs pre-attrition |
|---|---|---|---|
| Pre-attrition | 1748 | +1652 | — |
| **After loss — WITH EC-U1 fix** | 1748 | +1652 | **+0** |
| After loss — WITHOUT fix (est→0) | 816 | +2584 | +932 |

**Verdict:** with the fix, net **did NOT rise** under attrition (establishment holds the upkeep bill at 1748 → 1748). Without the fix the same loss makes net **ROSE** (+1652 → +2584, upkeep collapses 1748 → 816) — the original 'losing pays' bug, reproduced and then closed.
