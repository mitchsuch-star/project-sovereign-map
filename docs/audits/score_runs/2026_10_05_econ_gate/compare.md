# compare — audit_v11_base → 2026_10_05_econ_gate

## Item flips

- `ai_aliveness.C1` ✗ → ✓ — laws enacted abroad (enacted, lapsed) per seed: {'CMD-H': (17, 0), 'CMD-A': (13, 0), 'CMD-M': (17, 0)}
- `ai_aliveness.C6` ✓ → ✗ — turns with a visible AI attack over the turns at war: {'CMD-H': '9/15', 'CMD-A': '13/18', 'CMD-M': '14/39'}
- `combat_legibility.C3` · → ✗ — 1 capital captures after a battle; garrison neither fought nor named: ['CMD-H t6 Munich']
- `command.C6` · → ✓ — 1 of 145 lines read by the model (anthropic, key connected); misreads 0: []; rescued 0: []; lost on both 1: ['\'yes\': live \'Sire, I confes
- `economy.C1` ✓ → ✗ — the Staff was never enacted on the LAW arm
- `first_contact.C4` ✓ → ✗ — These orders would be carried out today, Sire: / - ↳ end turn — no military actions remain today / For any matter of state, press F1 for the
- `living_balance.F1` ✓ → ✗ — France at turn 40: {'CMD-H': 26, 'CMD-A': 7, 'CMD-M': 29}
- `narration.C1` ✓ → ✗ — worst class in any 10-turn window: {'CMD-H': ('estate_eroding', 4), 'CMD-A': ('home_captured', 9), 'CMD-M': ('enemy_on_our_soil', 4)}
- `narration.C4` ✓ → ✗ — 74 intel rows; disagreeing with the store: ['CMD-M t20: Kutuzov shown at Vienna, store says Bohemia']
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
| First contact | 8.00 | 7.50 | None (None) | None (None) | held |
| Economy | 8.00 | 7.50 | None (None) | None (None) | held |
| Naval | 7.50–8.00 | 7.50–8.00 | None (None) | None (None) | held |
| Living balance | 8.00 | 6.00 | None (None) | None (None) | held |
| Combat legibility | 7.00–7.50 | 7.00 | None (None) | None (None) | held |
| Marshal drama | 6.50–7.50 | 6.50–7.50 | None (None) | None (None) | held |
| Vassals | 7.50–8.00 | 7.50–8.00 | None (None) | None (None) | held |
| UI/UX | NOT EXERCISED | 7.50 | None (None) | None (None) | held |
| Command & parsing | 7.50–8.00 | 8.00 | None (None) | None (None) | held |
| Narration | 7.50–8.00 | 6.50–7.00 | None (None) | None (None) | held |
| AI aliveness | 8.00 | 8.00 | None (None) | None (None) | held |
| Agendas & formables | 8.50 | 8.50 | None (None) | None (None) | held |

directional: {'value': 7.69, 'over': '13/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"} → {'value': 7.43, 'over': '14/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"}

A move is claimed only when an item flipped AND the median moved by more than the larger spread (§4.5).
