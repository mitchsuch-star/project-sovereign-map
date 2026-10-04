# compare — score_2026_10_03_step5_head → score_2026_10_04_step5_final

## Item flips

- `agendas.C5` · → ✓ — carve terms stated 3x (Duchy of Warsaw from Prussia: Posen); Proclamation cards 1 (DuchyOfWarsaw); gate flipped to met in play (AGD_t1.json)
- `ai_aliveness.C5` ✗ → ✓ — 19 acts, no dither
- `ai_aliveness.C6` ✓ → ✗ — turns with a visible AI attack over the turns at war: {'CMD-H': '10/11', 'CMD-A': '9/16', 'CMD-M': '6/13'}
- `diplomacy.C3` ✓ → ✗ — no volte_face on the volte arm

## Pillars

| pillar | base | run | base median (spread) | run median (spread) | claim |
|---|---|---|---|---|---|
| The ending | NOT EXERCISED | NOT EXERCISED | None (None) | None (None) | held |
| Diplomacy | 6.00–8.50 | 6.00–8.00 | None (None) | None (None) | held |
| First contact | NOT EXERCISED | NOT EXERCISED | None (None) | None (None) | held |
| Economy | 6.50–7.00 | 6.50–7.00 | None (None) | None (None) | held |
| Naval | NOT EXERCISED | NOT EXERCISED | None (None) | None (None) | held |
| Living balance | 6.00–8.00 | 6.00–8.00 | None (None) | None (None) | held |
| Combat legibility | 6.00–7.00 | 6.00–7.00 | None (None) | None (None) | held |
| Marshal drama | NOT EXERCISED | NOT EXERCISED | None (None) | None (None) | held |
| Vassals | 7.00–8.00 | 7.00–8.00 | None (None) | None (None) | held |
| UI/UX | NOT EXERCISED | NOT EXERCISED | None (None) | None (None) | held |
| Command & parsing | NOT EXERCISED | NOT EXERCISED | None (None) | None (None) | held |
| Narration | 7.00–8.00 | 7.00–8.00 | None (None) | None (None) | held |
| AI aliveness | 6.00–7.50 | 6.00–7.50 | None (None) | None (None) | held |
| Agendas & formables | NOT EXERCISED | 6.00–8.50 | None (None) | None (None) | held |

directional: {'value': 6.36, 'over': '7/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"} → {'value': 6.31, 'over': '8/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"}

A move is claimed only when an item flipped AND the median moved by more than the larger spread (§4.5).
