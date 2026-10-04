# compare — 2026_09_29_c20d5bba → score_2026_10_04_step5_final

## Item flips

- `agendas.C3` ✗ → ✓ — gate terms flipping to met between saves: ['CMD-A t40: Ireland — at war with Britain', 'CMD-M t40: Ireland — at war with Britain', 'CMD-ULM 
- `agendas.C5` · → ✓ — carve terms stated 3x (Duchy of Warsaw from Prussia: Posen); Proclamation cards 1 (DuchyOfWarsaw); gate flipped to met in play (AGD_t1.json)
- `agendas.F1` ✓ → · — the SUITE arm did not run
- `ai_aliveness.C1` ✓ → ✗ — laws enacted abroad (enacted, lapsed) per seed: {'CMD-H': (17, 0), 'CMD-A': (19, 0), 'CMD-M': (17, 0)}
- `ai_aliveness.C6` ✓ → ✗ — turns with a visible AI attack over the turns at war: {'CMD-H': '10/11', 'CMD-A': '9/16', 'CMD-M': '6/13'}
- `ai_aliveness.F1` ✓ → · — the SUITE arm did not run
- `combat_legibility.C2` ✓ → ✗ — favorable out-bleeds 10/11 = 0.91; even 2/2; unfavorable 1/6
- `combat_legibility.C3` ✗ → · — no capital taken after a field battle on the arms
- `combat_legibility.F1` ✗ → ✓ — 39 battle lines; missing a side's losses: []
- `command.C4` ✗ → ✓ — all docked command lines execute or ask
- `command.C5` ✓ → · — TYPED did not run
- `command.F1` ✓ → · — PEVAL did not run
- `command.F2` ✓ → · — PEVAL did not run
- `diplomacy.C4` ✗ → ✓ — 8 phrasings all start a mission or refuse with a price
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
- `first_contact.C1` ✗ → ✓ — 20 questions; shrugs 0: []
- `first_contact.C3` ✗ → ✓ — 'where are the Russians?' → answered: Sire — Russia: no word of Buxhowden; no word of Kutuzov. | 'why is Europe alarmed?' → answered: Europe
- `first_contact.C4` ✓ → ✗ — These orders would be carried out today, Sire: / - ↳ end turn — no military actions remain today / For any matter of state, press F1 for the
- `first_contact.F1` ✓ → · — FC did not run
- `first_contact.F2` ✓ → · — SCH did not run
- `living_balance.C1` ✗ → ✓ — AI-vs-AI wars per seed: {'00_historical_k10000': 1, '01_ulm_k17919': 1, '02_austerlitz_k25838': 1, '03_jena_k33757': 1, '04_marengo_k41676':
- `living_balance.C2` ✗ → ✓ — standalone third-party settlements per seed: {'00_historical_k10000': 1, '01_ulm_k17919': 1, '02_austerlitz_k25838': 1, '03_jena_k33757': 1,
- `living_balance.C4` ✗ → ✓ — declarations beyond the fresh-peace floor: [('CMD-H', 'peaces', {'Austria': 11}), ('CMD-M', 'Russia', 9, 39)]
- `living_balance.F2` ✓ → · — the SUITE arm did not run
- `marshal_drama.C1` ✓ → ✗ — petition modals 3, audiences 2
- `marshal_drama.C3` ✗ → ✓ — 59 voiced battles, no repeat within three wins
- `marshal_drama.F1` ✓ → · — the FLAG probe did not write its record
- `naval.C1` ✓ → · — SEA did not run
- `naval.C2` ✓ → · — no fleet action on the naval arms
- `naval.C3` ✗ → · — DESC did not run
- `naval.C4` ✓ → · — shut-out arms present: []
- `naval.F1` ✓ → · — the SUITE arm did not run
- `naval.F2` ✓ → · — SEA did not run
- `vassals.C5` ✗ → · — no client capital fell to an enemy on the CMD arms

## Pillars

| pillar | base | run | base median (spread) | run median (spread) | claim |
|---|---|---|---|---|---|
| The ending | 5.00 | NOT EXERCISED | 5.0 (0.25) | None (None) | held |
| Diplomacy | 5.75 | 6.00–8.00 | 5.75 (0.25) | None (None) | held |
| First contact | 7.00–7.50 | NOT EXERCISED | 7.0 (0.0) | None (None) | held |
| Economy | 7.00 | 6.50–7.00 | 7.0 (0.0) | None (None) | held |
| Naval | 7.00–8.00 | NOT EXERCISED | 7.25 (0.25) | None (None) | held |
| Living balance | 6.50 | 6.00–8.00 | 6.25 (0.0) | None (None) | held |
| Combat legibility | 5.50–5.75 | 6.00–7.00 | 5.75 (0.25) | None (None) | held |
| Marshal drama | 7.00–8.00 | NOT EXERCISED | 7.0 (0.25) | None (None) | held |
| Vassals | 7.00–7.50 | 7.00–8.00 | 7.0 (0.25) | None (None) | held |
| UI/UX | NOT EXERCISED | NOT EXERCISED | None (None) | None (None) | held |
| Command & parsing | 7.00–7.50 | NOT EXERCISED | 7.0 (0.25) | None (None) | held |
| Narration | 7.00–8.00 | 7.00–8.00 | 6.75 (0.0) | None (None) | held |
| AI aliveness | 8.50 | 6.00–7.50 | 8.5 (0.0) | None (None) | held |
| Agendas & formables | 7.00–8.00 | 6.00–8.50 | 7.0 (0.25) | None (None) | held |

directional: {'value': 6.71, 'over': '13/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"} → {'value': 6.31, 'over': '8/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"}

A move is claimed only when an item flipped AND the median moved by more than the larger spread (§4.5).
