# compare — 2026_09_29_c20d5bba → 2026_10_02_step3

## Item flips

- `agendas.C3` ✗ → ✓ — gate terms flipping to met between saves: ['CMD-H t40: Ireland — at war with Britain', 'CMD-M t40: Ireland — at war with Britain']
- `agendas.F1` ✓ → · — the SUITE arm did not run
- `ai_aliveness.C1` ✓ → ✗ — laws enacted abroad (enacted, lapsed) per seed: {'CMD-H': (17, 3), 'CMD-A': (17, 0), 'CMD-M': (19, 0)}
- `ai_aliveness.F1` ✓ → · — the SUITE arm did not run
- `combat_legibility.C3` ✗ → · — no capital taken after a field battle on the arms
- `combat_legibility.F1` ✗ → ✓ — 71 battle lines; missing a side's losses: []
- `combat_legibility.F2` ✓ → · — every capital scout was a board refusal: ['OP t4: Ney is recovering from retreat and cannot scout. Recovery: 2 turns remaining.', 'FLD t4: N
- `command.C3` ✗ → · — HOLD did not run
- `command.C5` ✓ → · — TYPED did not run
- `command.F1` ✓ → · — PEVAL did not run
- `command.F2` ✓ → · — PEVAL did not run
- `diplomacy.C3` ✗ → ✓ — - RAIL volte_face: THE VOLTE-FACE: Austria, beaten and then courted, takes France's hand. Her court turns its gaze to The Eastern Question.
- `diplomacy.C6` ✗ → ✓ — 0 treaty-refused-after-accept lines
- `diplomacy.F1` ✓ → · — propose arms present: []
- `diplomacy.F2` ✓ → · — ADV did not run
- `economy.C1` ✓ → · — LAW did not run
- `ending.C1` ✗ → · — CONG did not run
- `ending.C2` ✗ → · — CONG did not run
- `ending.C3` ✗ → · — CONG did not run
- `ending.C6` ✗ → ✓ — 4 refusers, each price closing the gap, quoting its turns, or declared unpayable
- `ending.F1` ✓ → · — PRESS did not run
- `ending.F2` ✓ → · — VERDICT did not run
- `first_contact.C1` ✗ → · — HOLD did not run
- `first_contact.C3` ✗ → ✓ — 'where are the Russians?' → answered: Sire — Russia: no word of Buxhowden; no word of Kutuzov. | 'why is Europe alarmed?' → answered: Europe
- `first_contact.F1` ✓ → · — FC did not run
- `first_contact.F2` ✓ → · — SCH did not run
- `living_balance.C4` ✗ → ✓ — declarations beyond the fresh-peace floor: [('CMD-H', 'peaces', {'Austria': 35, 'Britain': 36}), ('CMD-A', 'Austria', 5, 40)]
- `living_balance.F1` ✓ → ✗ — France at turn 40: {'CMD-H': 26, 'CMD-A': 28, 'CMD-M': 19}
- `living_balance.F2` ✓ → · — the SUITE arm did not run
- `marshal_drama.C1` ✓ → ✗ — petition modals 5, audiences 9
- `marshal_drama.C3` ✗ → ✓ — 86 voiced battles, no repeat within three wins
- `marshal_drama.F1` ✓ → · — the FLAG probe did not write its record
- `naval.C1` ✓ → · — SEA did not run
- `naval.C2` ✓ → · — no fleet action on the naval arms
- `naval.C3` ✗ → · — DESC did not run
- `naval.C4` ✓ → · — shut-out arms present: []
- `naval.F1` ✓ → · — the SUITE arm did not run
- `naval.F2` ✓ → · — SEA did not run
- `vassals.C4` ✗ → · — no satellite fell under 40 on the arms
- `vassals.C5` ✗ → · — no client capital fell to an enemy on the CMD arms
- `vassals.F2` ✓ → · — CMDR-H did not run

## Pillars

| pillar | base | run | base median (spread) | run median (spread) | claim |
|---|---|---|---|---|---|
| The ending | 5.00 | NOT EXERCISED | 5.0 (0.25) | None (None) | held |
| Diplomacy | 5.75 | 6.00–8.00 | 5.75 (0.25) | None (None) | held |
| First contact | 7.00–7.50 | NOT EXERCISED | 7.0 (0.0) | None (None) | held |
| Economy | 7.00 | 6.50–7.00 | 7.0 (0.0) | None (None) | held |
| Naval | 7.00–8.00 | NOT EXERCISED | 7.25 (0.25) | None (None) | held |
| Living balance | 6.50 | 5.75 | 6.25 (0.0) | None (None) | held |
| Combat legibility | 5.50–5.75 | NOT EXERCISED | 5.75 (0.25) | None (None) | held |
| Marshal drama | 7.00–8.00 | NOT EXERCISED | 7.0 (0.25) | None (None) | held |
| Vassals | 7.00–7.50 | NOT EXERCISED | 7.0 (0.25) | None (None) | held |
| UI/UX | NOT EXERCISED | NOT EXERCISED | None (None) | None (None) | held |
| Command & parsing | 7.00–7.50 | NOT EXERCISED | 7.0 (0.25) | None (None) | held |
| Narration | 7.00–8.00 | 7.00–8.00 | 6.75 (0.0) | None (None) | held |
| AI aliveness | 8.50 | 6.00–8.00 | 8.5 (0.0) | None (None) | held |
| Agendas & formables | 7.00–8.00 | NOT EXERCISED | 7.0 (0.25) | None (None) | held |

directional: {'value': 6.71, 'over': '13/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"} → {'value': 6.25, 'over': '5/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"}

A move is claimed only when an item flipped AND the median moved by more than the larger spread (§4.5).
