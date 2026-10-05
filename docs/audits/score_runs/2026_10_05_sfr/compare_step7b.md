# compare — 2026_10_05_step7b → score_2026_10_05_sfr

## Item flips

- `agendas.F1` · → ✓ — agenda + formables tests: test_nation_agendas.py → 184 passed, 1 warning in 1.80s; test_nation_agendas_formables.py → 225 passed, 1 warning 
- `ai_aliveness.F1` · → ✓ — AI-intent assurance: test_ai_intent_assurance.py → 54 passed, 1 warning in 18.34s
- `command.C3` ✓ → ✗ — 11/20 orders executed as meant; misses: ['"Ney, if Mack\'s still in Swabia, attack h" → Berthier sets down his pen. "Sire, that is a conting
- `command.C6` · → ✓ — 1 of 145 lines read by the model (anthropic, key connected); misreads 0: []; rescued 0: []; lost on both 1: ['\'yes\': live \'Sire, I must c
- `living_balance.F2` · → ✓ — M1–M7 + BASELINE_SERIES: test_combat_sweep_metrics.py → 11 passed, 1 warning in 1.76s; test_ai_intent_threat_migration.py → 18 passed, 1 war
- `naval.F1` · → ✓ — naval gate: test_naval_channel_gate.py → 35 passed, 1 warning in 1.18s; test_naval_substrate.py → 50 passed, 1 warning in 1.27s
- `ui_ux.C1` · → ✓ — 262 frames; with buttons_offscreen: 0 []
- `ui_ux.C2` · → ✓ — 262 frames; with clipped_text: 0 []
- `ui_ux.C3` · → ✓ — 262 frames; with a raw key, <null> or (s): 0 []
- `ui_ux.F1` · → ✓ — 131 shots, 262 frames; engine exit 0, SCRIPT ERROR 0; not ok []; blank []
- `ui_ux.F2` · → ✓ — parse harness exit 0; boot smoke exit 0, SCRIPT ERROR 0 (523 bytes of log)

## Pillars

| pillar | base | run | base median (spread) | run median (spread) | claim |
|---|---|---|---|---|---|
| The ending | 7.50 | 7.50 | None (None) | None (None) | held |
| Diplomacy | 8.50 | 8.50 | None (None) | None (None) | held |
| First contact | 8.00–8.50 | 8.00–8.50 | None (None) | None (None) | held |
| Economy | 7.00 | 7.00 | None (None) | None (None) | held |
| Naval | NOT EXERCISED | 7.50–8.50 | None (None) | None (None) | held |
| Living balance | 6.00–8.50 | 8.50 | None (None) | None (None) | held |
| Combat legibility | 6.50–7.50 | 6.50–7.50 | None (None) | None (None) | held |
| Marshal drama | NOT EXERCISED | NOT EXERCISED | None (None) | None (None) | held |
| Vassals | 7.00–8.00 | 7.00–8.00 | None (None) | None (None) | held |
| UI/UX | NOT EXERCISED | 7.50–8.50 | None (None) | None (None) | held |
| Command & parsing | 8.00–8.50 | 8.00 | None (None) | None (None) | held |
| Narration | 7.50–8.50 | 7.50–8.50 | None (None) | None (None) | held |
| AI aliveness | 5.75–7.00 | 7.00 | None (None) | None (None) | held |
| Agendas & formables | 6.00–8.50 | 8.00–8.50 | None (None) | None (None) | held |

directional: {'value': 7.07, 'over': '11/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"} → {'value': 7.58, 'over': '13/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"}

A move is claimed only when an item flipped AND the median moved by more than the larger spread (§4.5).
