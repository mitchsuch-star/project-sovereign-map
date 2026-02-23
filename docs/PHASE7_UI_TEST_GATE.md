# Phase 7 UI Test Gates

Manual testing checklists for Phase 7 coordination features.
Run in Godot client against the backend (`LLM_MODE=mock`).

---

## Gate 1: After Session 60 (All Bonus Sources Live)

Sessions 57-60 add four coordination bonus sources that all flow through
existing combat display and battle report channels. Verify they render correctly.

### Setup

1. Start backend: `.venv\Scripts\python.exe backend/main.py`
2. Launch Godot client
3. Move French marshals to co-locate (need 2+ types in same region)

### Checklist

#### Combined Arms Messages (Session 57)
- [ ] Attack with 2+ unit types co-located — battle text shows "combined arms coordination" with correct % (+10% for 2 types, +20% for 3)
- [ ] Defender with 2+ types also shows their own combined arms line
- [ ] Solo marshal (1 type) shows NO combined arms message
- [ ] Battle report popup includes "Combined arms" modifier entry

#### Per-Ally Coordination (Session 58)
- [ ] Attack with ally in same region — battle text shows coordination bonus
- [ ] Hostile relationship (-2) gives 0% coordination (verify no line or 0% line)
- [ ] Fortified non-artillery ally gives defense coordination only (no attack line)
- [ ] Fortified artillery ally gives BOTH attack and defense coordination
- [ ] Battle report shows per-ally coordination entry

#### Dedicated Coordination (Session 59)
- [ ] Two marshals co-located for 2+ turns — dedicated bonus appears in battle text
- [ ] Battle report shows dedicated coordination entry
- [ ] Bonus appears for BOTH marshals (mutual, not one-directional)

#### Adjacent Support (Session 60)
- [ ] Marshal attacks with friendly marshal in adjacent region — "+2% adjacent support" appears
- [ ] Multiple adjacent allies stack (2 adjacent = +4%)
- [ ] Adjacent bonus appears in battle report

#### General Display
- [ ] Messages are readable — not too cluttered with multiple bonus lines
- [ ] Battle report modifier list doesn't overflow the popup
- [ ] Numbers display as integers (no floats reaching Godot)
- [ ] Enemy AI battles (end turn, watch enemy phase) also show coordination bonuses when applicable

#### Regression Checks
- [ ] Normal 1v1 combat (no coordination) still works and displays correctly
- [ ] Bombardment does NOT show coordination bonuses
- [ ] Save/load preserves game state (coordination is transient, should not persist)

---

## Gate 2: After Session 61b (SUPPORT Command)

### Setup
Same as Gate 1, plus test the new SUPPORT strategic command.

### Checklist

#### SUPPORT Command
- [ ] Type "Marshal X, support Marshal Y" — command is parsed and accepted
- [ ] SUPPORT costs 2 AP (1 for literal Grouchy)
- [ ] Immediate dedicated bonus appears on next attack (no 2-turn wait)
- [ ] Strategic report shows SUPPORT order status
- [ ] "Cancel support" works and costs 1 AP
- [ ] Objection system works with SUPPORT (personality-appropriate objections)

#### Reinforcement / Grouchy Rule (Session 61a)
- [ ] Marshal arriving at battle region mid-combat converts from adjacent (+2%) to full coordination
- [ ] Grouchy Rule: literal marshals may fail to reinforce (per spec)

---

## After Testing

Report results to Claude Code. Mark items that failed with details.
If all pass, say "Gate X passed" and proceed to next session.
