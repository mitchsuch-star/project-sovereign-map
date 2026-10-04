# compare — 2026_09_29_c20d5bba → score_2026_10_04_step6_final

## Item flips

- `agendas.C2` ✓ → · — no AIV per-run records
- `agendas.F1` ✓ → · — the SUITE arm did not run
- `ai_aliveness.F1` ✓ → · — the SUITE arm did not run
- `combat_legibility.C2` ✓ → · — only 3 favorable battles read (need 5)
- `combat_legibility.C3` ✗ → · — no capital taken after a field battle on the arms
- `combat_legibility.F1` ✗ → ✓ — 27 battle lines; missing a side's losses: []
- `combat_legibility.F2` ✓ → · — no arm scouted a capital
- `command.C1` ✓ → · — OP did not run
- `command.C2` ✓ → · — OP did not run
- `command.C3` ✗ → · — HOLD did not run
- `command.C4` ✗ → ✓ — all docked command lines execute or ask
- `command.C5` ✓ → · — TYPED did not run
- `command.F1` ✓ → · — PEVAL did not run
- `command.F2` ✓ → · — PEVAL did not run
- `diplomacy.C3` ✗ → · — VOLTE did not run
- `diplomacy.C4` ✗ → ✓ — 8 phrasings all start a mission or refuse with a price
- `diplomacy.C6` ✗ → ✓ — 0 treaty-refused-after-accept lines
- `diplomacy.F1` ✓ → · — propose arms present: []
- `diplomacy.F2` ✓ → · — ADV did not run
- `economy.C3` ✗ → ✓ — 3 battle-free turns, quoted == billed on 3: (turn, quoted charges, applied, quoted laws, applied): [(10, 1682, 1682, 0, 0), (30, 1227, 1227,
- `ending.C1` ✗ → · — CONG did not run
- `ending.C2` ✗ → · — CONG did not run
- `ending.C3` ✗ → · — CONG did not run
- `ending.C4` ✗ → · — titled counts missing: {'CMD-H': 35}
- `ending.C6` ✗ → ✓ — 4 refusers, each price closing the gap, quoting its turns, or declared unpayable
- `ending.F1` ✓ → · — PRESS did not run
- `ending.F2` ✓ → · — VERDICT did not run
- `first_contact.C1` ✗ → · — HOLD did not run
- `first_contact.C3` ✗ → ✓ — 'where are the Russians?' → answered: Sire — Russia: no word of Buxhowden; no word of Kutuzov. | 'why is Europe alarmed?' → answered: Europe
- `first_contact.C4` ✓ → ✗ — These orders would be carried out today, Sire: / - ↳ end turn — no military actions remain today / For any matter of state, press F1 for the
- `first_contact.C6` ✓ → · — OP did not run
- `first_contact.F1` ✓ → · — FC did not run
- `first_contact.F2` ✓ → · — SCH did not run
- `living_balance.C1` ✗ → · — no AIV summary
- `living_balance.C2` ✗ → · — no AIV summary
- `living_balance.C3` ✓ → · — no AIV summary
- `living_balance.C6` ✓ → · — no AIV per-run records
- `living_balance.F1` ✓ → · — CMD ledgers missing: {'CMD-H': 28}
- `living_balance.F2` ✓ → · — the SUITE arm did not run
- `marshal_drama.C1` ✓ → · — OP did not run
- `marshal_drama.C2` ✓ → · — no Trust alternative naming a man on the arms
- `marshal_drama.C3` ✗ → ✓ — 19 voiced battles, no repeat within three wins
- `marshal_drama.F1` ✓ → · — the FLAG probe did not write its record
- `marshal_drama.F2` ✓ → · — OP did not run
- `naval.C3` ✗ → ✓ — quotes 1; odds named True; lever named True; Munster falls True
- `naval.F1` ✓ → · — the SUITE arm did not run
- `ui_ux.C4` ✗ → · — OP did not run
- `vassals.C1` ✓ → · — CMD arms present: ['CMD-H']
- `vassals.C4` ✗ → · — no satellite fell under 40 on the arms
- `vassals.C5` ✗ → · — no client capital fell to an enemy on the CMD arms
- `vassals.F1` ✓ → · — CMD arms present: ['CMD-H']
- `vassals.F2` ✓ → · — CMDR-H did not run

## Pillars

| pillar | base | run | base median (spread) | run median (spread) | claim |
|---|---|---|---|---|---|
| The ending | 5.00 | NOT EXERCISED | 5.0 (0.25) | None (None) | held |
| Diplomacy | 5.75 | NOT EXERCISED | 5.75 (0.25) | None (None) | held |
| First contact | 7.00–7.50 | NOT EXERCISED | 7.0 (0.0) | None (None) | held |
| Economy | 7.00 | 7.50 | 7.0 (0.0) | None (None) | held |
| Naval | 7.00–8.00 | NOT EXERCISED | 7.25 (0.25) | None (None) | held |
| Living balance | 6.50 | NOT EXERCISED | 6.25 (0.0) | None (None) | held |
| Combat legibility | 5.50–5.75 | NOT EXERCISED | 5.75 (0.25) | None (None) | held |
| Marshal drama | 7.00–8.00 | NOT EXERCISED | 7.0 (0.25) | None (None) | held |
| Vassals | 7.00–7.50 | NOT EXERCISED | 7.0 (0.25) | None (None) | held |
| UI/UX | NOT EXERCISED | NOT EXERCISED | None (None) | None (None) | held |
| Command & parsing | 7.00–7.50 | NOT EXERCISED | 7.0 (0.25) | None (None) | held |
| Narration | 7.00–8.00 | 7.00–8.00 | 6.75 (0.0) | None (None) | held |
| AI aliveness | 8.50 | 6.00–8.50 | 8.5 (0.0) | None (None) | held |
| Agendas & formables | 7.00–8.00 | NOT EXERCISED | 7.0 (0.25) | None (None) | held |

directional: {'value': 6.71, 'over': '13/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"} → {'value': 6.83, 'over': '3/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"}

A move is claimed only when an item flipped AND the median moved by more than the larger spread (§4.5).
