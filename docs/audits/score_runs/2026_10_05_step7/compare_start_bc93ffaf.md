# compare — score_2026_10_04_step7_start → score_2026_10_05_step7_final

## Item flips

- `ai_aliveness.C5` ✓ → ✗ — 23 fortify/unfortify acts; fortify→unfortify→fortify within 3 turns: ['CMD-H ArchdukeCharles t8–t11', 'CMD-H ArchdukeCharles t33–t36']
- `combat_legibility.C2` ✗ → ✓ — favorable out-bleeds 12/12 = 1.00; even 2/3; unfavorable 0/5
- `combat_legibility.C3` ✓ → · — no capital taken after a field battle on the arms
- `command.C3` ✗ → ✓ — 20/20 orders executed as meant; misses: []
- `diplomacy.C3` ✗ → ✓ — - RAIL volte_face: THE VOLTE-FACE: Austria, beaten and then courted, takes France's hand. Her court turns its gaze to The Eastern Question.
- `economy.C1` ✓ → ✗ — the Staff enacted at loop 10: The Grand Quartier Général (Berthier's Imperial Headquarters, expanded 1805–07): Berthier's headquarters grown
- `first_contact.C4` ✗ → ✓ — These orders would be carried out today, Sire: / - ↳ end turn — no military actions remain today / build supply depot in Paris — 300g
- `marshal_drama.C5` ✓ → · — no marshal's expectation eroded on the arms
- `marshal_drama.F1` ✓ → ✗ — petition modals 5 (≤ 4), silent losses 0, petition moments 19
- `ui_ux.C4` ✗ → ✓ — most blocking popups one end turn raised: 3 (turn 9) ['marshal_petition:jealousy_confrontation, Marsha', 'diplomatic_dialogue:incoming_settl

## Pillars

| pillar | base | run | base median (spread) | run median (spread) | claim |
|---|---|---|---|---|---|
| The ending | 7.50 | 7.50 | None (None) | None (None) | held |
| Diplomacy | 8.00 | 8.50 | None (None) | None (None) | held |
| First contact | 7.50–8.00 | 8.00–8.50 | None (None) | None (None) | held |
| Economy | 7.50 | 7.00 | None (None) | None (None) | held |
| Naval | NOT EXERCISED | NOT EXERCISED | None (None) | None (None) | held |
| Living balance | 6.00–8.00 | 6.00–8.00 | None (None) | None (None) | held |
| Combat legibility | 6.50–7.00 | 6.50–7.50 | None (None) | None (None) | held |
| Marshal drama | 7.00–8.00 | NOT EXERCISED | None (None) | None (None) | held |
| Vassals | 7.00–8.00 | 7.00–8.00 | None (None) | None (None) | held |
| UI/UX | NOT EXERCISED | NOT EXERCISED | None (None) | None (None) | held |
| Command & parsing | 7.50–8.00 | 8.00–8.50 | None (None) | None (None) | held |
| Narration | 5.75–6.00 | 5.75–6.00 | None (None) | None (None) | held |
| AI aliveness | 6.00–7.50 | 5.75–7.00 | None (None) | None (None) | held |
| Agendas & formables | 6.00–8.50 | 6.00–8.50 | None (None) | None (None) | held |

directional: {'value': 6.85, 'over': '12/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"} → {'value': 6.91, 'over': '11/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"}

A move is claimed only when an item flipped AND the median moved by more than the larger spread (§4.5).
