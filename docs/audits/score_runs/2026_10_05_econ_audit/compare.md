# compare — 2026_10_05_sfr → 2026_10_05_econ_audit

## Item flips

- `agendas.C6` ✗ → · — EYES: no mark given (--eyes)
- `ai_aliveness.C5` ✗ → ✓ — 29 acts, no dither
- `ai_aliveness.C6` ✗ → ✓ — turns with a visible AI attack over the turns at war: {'CMD-H': '14/18', 'CMD-A': '12/18', 'CMD-M': '19/30'}
- `combat_legibility.C6` ✓ → · — EYES: no mark given (--eyes)
- `command.C6` ✓ → · — the live-parser arm (OP-LIVE) did not run — run --live with an ANTHROPIC_API_KEY
- `economy.C2` ✗ → ✓ — 48 moves of 10% or more, each named by a ledger note
- `first_contact.C2` ✗ → · — EYES: no mark given (--eyes)
- `living_balance.C4` ✓ → ✗ — declarations beyond the fresh-peace floor: [('CMD-H', 'peaces', {'Britain': 39, 'Russia': 40})]
- `marshal_drama.F1` ✗ → ✓ — petition modals 4 (≤ 4), silent losses 0, petition moments 17
- `narration.C6` ✗ → · — EYES: no mark given (--eyes)
- `naval.C6` ✗ → · — EYES: no mark given (--eyes)
- `ui_ux.C1` ✓ → · — the client arm (IQ-10 frames) did not run (score_run run --godot)
- `ui_ux.C2` ✓ → · — the client arm (IQ-10 frames) did not run (score_run run --godot)
- `ui_ux.C3` ✓ → · — the client arm (IQ-10 frames) did not run (score_run run --godot)
- `ui_ux.F1` ✓ → · — the client arm (IQ-10 frames) did not run (score_run run --godot)
- `ui_ux.F2` ✓ → · — the client arm (IQ-10 frames) did not run (score_run run --godot)
- `vassals.C6` ✓ → · — EYES: no mark given (--eyes)

## Pillars

| pillar | base | run | base median (spread) | run median (spread) | claim |
|---|---|---|---|---|---|
| The ending | 7.50 | 7.50 | 7.5 (0.0) | None (None) | held |
| Diplomacy | 8.50 | 8.50 | 8.25 (0.25) | None (None) | held |
| First contact | 8.00 | 8.00–8.50 | 7.75 (0.25) | None (None) | held |
| Economy | 7.00 | 7.50 | 7.0 (0.25) | None (None) | held |
| Naval | 7.50–8.00 | 7.50–8.50 | 7.75 (0.25) | None (None) | held |
| Living balance | 8.50 | 8.00 | 8.5 (0.0) | None (None) | held |
| Combat legibility | 7.00–7.50 | 6.50–7.50 | 7.0 (0.25) | None (None) | held |
| Marshal drama | NOT EXERCISED | NOT EXERCISED | None (None) | None (None) | held |
| Vassals | 7.50–8.00 | 7.00–8.00 | 7.5 (0.0) | None (None) | held |
| UI/UX | 7.50–8.50 | NOT EXERCISED | 7.25 (0.0) | None (None) | held |
| Command & parsing | 6.00 | 7.50–8.00 | 6.0 (0.25) | None (None) | held |
| Narration | 7.50–8.00 | 7.50–8.50 | 7.25 (0.25) | None (None) | held |
| AI aliveness | 7.00 | 8.00 | 7.0 (0.0) | None (None) | held |
| Agendas & formables | 8.00 | 8.00–8.50 | 8.0 (0.0) | None (None) | held |

directional: {'value': 7.5, 'over': '13/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"} → {'value': 7.62, 'over': '12/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"}

A move is claimed only when an item flipped AND the median moved by more than the larger spread (§4.5).
