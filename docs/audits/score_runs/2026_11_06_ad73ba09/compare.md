# compare — 2026_10_05_sfr → score_head

## Item flips

- `agendas.C6` ✗ → · — EYES: no mark given (--eyes)
- `ai_aliveness.C5` ✗ → ✓ — 21 acts, no dither
- `combat_legibility.C2` ✓ → · — only 4 favorable battles read (need 5)
- `combat_legibility.C4` ✗ → ✓ — The order would be refused, Sire: Davout is fortified — unfortify first. Nothing spent. / 
- `combat_legibility.C5` ✗ → ✓ — raw keys in combat/muster/enemy-phase lines: 0 {}
- `combat_legibility.C6` ✓ → · — EYES: no mark given (--eyes)
- `command.C3` ✗ → ✓ — 19/20 orders executed as meant; misses: ["'Tell Massena to fortfy at Milan in case ' → Massena firmly objects: 'I would rather attack than s
- `command.C6` ✓ → · — the live-parser arm (OP-LIVE) did not run — run --live with an ANTHROPIC_API_KEY
- `diplomacy.C3` ✓ → ✗ — no volte_face on the volte arm
- `economy.C2` ✗ → ✓ — 41 moves of 10% or more, each named by a ledger note
- `economy.C5` ✗ → ✓ — Davout recruits 3,000 infantry at Rhineland (field levy — no depot; capped at 3,000) - Cost: 615 gold (×3 at war) (×1.21 over the ordinance)
- `first_contact.C2` ✗ → · — EYES: no mark given (--eyes)
- `living_balance.C6` ✓ → ✗ — an AI court takes another's last province (eliminations, the proxy the run records) per seed: {"armC_00_historical": ["Bavaria", "KingdomOfI
- `marshal_drama.F1` ✗ → ✓ — petition modals 2 (≤ 4), silent losses 0, petition moments 14
- `narration.C1` ✓ → ✗ — worst class in any 10-turn window: {'CMD-H': ('home_captured', 6), 'CMD-A': ('realm_league', 4), 'CMD-M': ('supply_strain', 4)}
- `narration.C6` ✗ → · — EYES: no mark given (--eyes)
- `naval.C4` ✓ → ✗ — Britain sues at turn {'SHUT-H': None, 'SHUT-A': None, 'SHUT-M': 11}
- `naval.C6` ✗ → · — EYES: no mark given (--eyes)
- `naval.F2` ✓ → ✗ — status completed; blockers []; preconditions present
- `ui_ux.C1` ✓ → · — the client arm (IQ-10 frames) did not run (score_run run --godot)
- `ui_ux.C2` ✓ → · — the client arm (IQ-10 frames) did not run (score_run run --godot)
- `ui_ux.C3` ✓ → · — the client arm (IQ-10 frames) did not run (score_run run --godot)
- `ui_ux.F1` ✓ → · — the client arm (IQ-10 frames) did not run (score_run run --godot)
- `ui_ux.F2` ✓ → · — the client arm (IQ-10 frames) did not run (score_run run --godot)
- `vassals.C4` ✗ → ✓ — CMDR-H t14: Switzerland at 33 → remedy named | CMDR-H t19: Holland at 37 → remedy named
- `vassals.C6` ✓ → · — EYES: no mark given (--eyes)

## Pillars

| pillar | base | run | base median (spread) | run median (spread) | claim |
|---|---|---|---|---|---|
| The ending | 7.50 | 7.50 | 7.5 (0.0) | None (None) | held |
| Diplomacy | 8.50 | 8.00 | 8.25 (0.25) | None (None) | held |
| First contact | 8.00 | 8.00–8.50 | 7.75 (0.25) | None (None) | held |
| Economy | 7.00 | 8.00 | 7.0 (0.25) | None (None) | held |
| Naval | 7.50–8.00 | 5.75–6.00 | 7.75 (0.25) | None (None) | held |
| Living balance | 8.50 | 8.00 | 8.5 (0.0) | None (None) | held |
| Combat legibility | 7.00–7.50 | NOT EXERCISED | 7.0 (0.25) | None (None) | held |
| Marshal drama | NOT EXERCISED | NOT EXERCISED | None (None) | None (None) | held |
| Vassals | 7.50–8.00 | 7.50–8.50 | 7.5 (0.0) | None (None) | held |
| UI/UX | 7.50–8.50 | NOT EXERCISED | 7.25 (0.0) | None (None) | held |
| Command & parsing | 6.00 | 8.00–8.50 | 6.0 (0.25) | None (None) | held |
| Narration | 7.50–8.00 | 7.00–8.00 | 7.25 (0.25) | None (None) | held |
| AI aliveness | 7.00 | 7.50 | 7.0 (0.0) | None (None) | held |
| Agendas & formables | 8.00 | 8.00–8.50 | 8.0 (0.0) | None (None) | held |

directional: {'value': 7.5, 'over': '13/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"} → {'value': 7.57, 'over': '11/14', 'note': "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged"}

A move is claimed only when an item flipped AND the median moved by more than the larger spread (§4.5).
