# compare — 2026_09_29_c20d5bba → score_2026_10_05_step7b_final

## Item flips

- `agendas.C3` ✗ → ✓ — gate terms flipping to met between saves: ['CMD-A t40: Ireland — at war with Britain', 'CMD-M t40: Ireland — at war with Britain']
- `agendas.C5` · → ✓ — carve terms stated 3x (Duchy of Warsaw from Prussia: Posen); Proclamation cards 1 (DuchyOfWarsaw); gate flipped to met in play (AGD_t1.json)
- `agendas.F1` ✓ → · — the SUITE arm did not run
- `ai_aliveness.C1` ✓ → ✗ — laws enacted abroad (enacted, lapsed) per seed: {'CMD-H': (16, 0), 'CMD-A': (17, 0), 'CMD-M': (15, 2)}
- `ai_aliveness.C5` ✓ → ✗ — 23 fortify/unfortify acts; fortify→unfortify→fortify within 3 turns: ['CMD-H ArchdukeCharles t8–t11', 'CMD-H ArchdukeCharles t33–t36']
- `ai_aliveness.C6` ✓ → ✗ — turns with a visible AI attack over the turns at war: {'CMD-H': '15/24', 'CMD-A': '5/19', 'CMD-M': '11/39'}
- `ai_aliveness.F1` ✓ → · — the SUITE arm did not run
- `combat_legibility.C3` ✗ → · — no capital taken after a field battle on the arms
- `combat_legibility.F1` ✗ → ✓ — 58 battle lines; missing a side's losses: []
- `command.C3` ✗ → ✓ — 20/20 orders executed as meant; misses: []
- `command.C4` ✗ → ✓ — all docked command lines execute or ask
- `diplomacy.C3` ✗ → ✓ — - RAIL volte_face: THE VOLTE-FACE: Austria, beaten and then courted, takes France's hand. Her court turns its gaze to The Eastern Question.
- `diplomacy.C4` ✗ → ✓ — 8 phrasings all start a mission or refuse with a price
- `diplomacy.C6` ✗ → ✓ — 0 treaty-refused-after-accept lines
- `economy.C1` ✓ → ✗ — the Staff enacted at loop 10: The Grand Quartier Général (Berthier's Imperial Headquarters, expanded 1805–07): Berthier's headquarters grown
- `economy.C3` ✗ → ✓ — 4 battle-free turns, quoted == billed on 4: (turn, quoted charges, applied, quoted laws, applied): [(10, 1316, 1316, 0, 0), (20, 366, 366, 0
- `ending.C1` ✗ → ✓ — dissolved for a named cause at turn 28: - CONGRESS THE CONGRESS OF PARIS — dissolved on turn 28 — a titled province fell (Moravia, Carniola 
- `ending.C2` ✗ → ✓ — summons: The Emperor summons the powers of Europe to Paris. The Congress sits for 8 turns, to the end of turn 32. Britain REFUSES — at war w
- `ending.C3` ✗ → ✓ — the table forecasts a net of +1 a turn ('rising 1 a turn: our bloc's weight in Europe +3, the designs we deny +…'); the quiet ticks on the C
- `ending.C6` ✗ → ✓ — 4 refusers, each price closing the gap, quoting its turns, or declared unpayable
- `first_contact.C1` ✗ → ✓ — 20 questions; shrugs 0: []
- `first_contact.C3` ✗ → ✓ — 'where are the Russians?' → answered: Sire — Russia: no word of Buxhowden; no word of Kutuzov. | 'why is Europe alarmed?' → answered: Europe
- `living_balance.C1` ✗ → ✓ — AI-vs-AI wars per seed: {'00_historical_k10000': 1, '01_ulm_k17919': 1, '02_austerlitz_k25838': 1, '03_jena_k33757': 1, '04_marengo_k41676':
- `living_balance.C2` ✗ → ✓ — standalone third-party settlements per seed: {'00_historical_k10000': 1, '01_ulm_k17919': 1, '02_austerlitz_k25838': 1, '03_jena_k33757': 1,
- `living_balance.C4` ✗ → ✓ — declarations beyond the fresh-peace floor: [('CMD-H', 'peaces', {'Austria': 34}), ('CMD-M', 'Austria', 10, 34)]
- `living_balance.C5` ✗ → ✓ — after the peace: 1 sponsorships against France, 1 on the page; 4 great powers newly free to join, 4 on the page; 22 quoted keep-out levers o
- `living_balance.F2` ✓ → · — the SUITE arm did not run
- `marshal_drama.C1` ✓ → ✗ — petition modals 6, audiences 2
- `marshal_drama.C3` ✗ → ✓ — 59 voiced battles, no repeat within three wins
- `marshal_drama.C5` ✓ → · — no marshal's expectation eroded on the arms
- `marshal_drama.F1` ✓ → ✗ — petition modals 5 (≤ 4), silent losses 0, petition moments 19
- `narration.C1` ✗ → ✓ — worst class in any 10-turn window: {'CMD-H': ('realm_league', 4), 'CMD-A': ('league_fuse', 3), 'CMD-M': ('enemy_on_our_soil', 4)}
- `naval.C3` ✗ → ✓ — quotes 1; odds named True; lever named True; Munster falls True
- `naval.F1` ✓ → · — the SUITE arm did not run
- `ui_ux.C4` ✗ → ✓ — most blocking popups one end turn raised: 3 (turn 9) ['marshal_petition:jealousy_confrontation, Marsha', 'diplomatic_dialogue:incoming_settl
- `vassals.C5` ✗ → · — no client capital fell to an enemy on the CMD arms

## Pillars

| pillar | base | run | base median (spread) | run median (spread) | claim |
|---|---|---|---|---|---|
| The ending | 5.00 | 7.50 | 5.0 (0.25) | None (None) | held |
| Diplomacy | 5.75 | 8.50 | 5.75 (0.25) | None (None) | held |
| First contact | 7.00–7.50 | 8.00–8.50 | 7.0 (0.0) | None (None) | held |
| Economy | 7.00 | 7.00 | 7.0 (0.0) | None (None) | held |
| Naval | 7.00–8.00 | NOT EXERCISED | 7.25 (0.25) | None (None) | held |
| Living balance | 6.50 | 6.00–8.50 | 6.25 (0.0) | None (None) | held |
| Combat legibility | 5.50–5.75 | 6.50–7.50 | 5.75 (0.25) | None (None) | held |
| Marshal drama | 7.00–8.00 | NOT EXERCISED | 7.0 (0.25) | None (None) | held |
| Vassals | 7.00–7.50 | 7.00–8.00 | 7.0 (0.25) | None (None) | held |
| UI/UX | NOT EXERCISED | NOT EXERCISED | None (None) | None (None) | held |
| Command & parsing | 7.00–7.50 | 8.00–8.50 | 7.0 (0.25) | None (None) | held |
| Narration | 7.00–8.00 | 7.50–8.50 | 6.75 (0.0) | None (None) | held |
| AI aliveness | 8.50 | 5.75–7.00 | 8.5 (0.0) | None (None) | held |
| Agendas & formables | 7.00–8.00 | 6.00–8.50 | 7.0 (0.25) | None (None) | held |

directional: {'value': 6.71, 'over': '13/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"} → {'value': 7.07, 'over': '11/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"}

A move is claimed only when an item flipped AND the median moved by more than the larger spread (§4.5).
