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

---

## Gate 3: After Session 62 (Casualty Distribution)

Session 62 changes the `resolve_battle()` contract so allied marshals take proportional casualties instead of the primary absorbing everything.

### Checklist

#### Per-Marshal Casualty Display
- [ ] Multi-marshal battle — each ally's losses shown separately in combat output
- [ ] Hostile relationship ally takes 0% casualties (excluded from distribution)
- [ ] Primary combatant still shows as main attacker/defender in battle text
- [ ] Battle report popup shows per-marshal casualty breakdown

#### Regression Checks
- [ ] 1v1 combat (no allies) unchanged — single casualty line
- [ ] AI multi-marshal battles display correctly during enemy phase
- [ ] Save/load after multi-marshal battle preserves all marshal strengths

---

## Gate 4: After Session 65 (Battle Reports & Berthier Observations)

Session 65 adds 5 coordination observation categories and pre-battle coordination preview.

### Checklist

#### Coordination Observations
- [ ] Battle report includes Berthier coordination observations when coordination bonuses active
- [ ] Observations reflect actual bonuses (combined arms, per-ally, dedicated, adjacent)
- [ ] No observations appear for 1v1 battles without coordination

#### Pre-Battle Preview
- [ ] Pre-battle coordination preview appears before combat resolves (if implemented as popup)
- [ ] Preview shows expected coordination bonuses

#### Regression Checks
- [ ] Existing battle report fields still display (modifier list, casualties, outcome)
- [ ] Bombardment reports unaffected
- [ ] Reports readable — not cluttered with too many observation lines

---

## Gate 5: After Tactical Triangle (Linked Group — Square Formation + Artillery SUPPORT + Overwatch)

These 3 features ship together. Test after all 3 are complete.

### Checklist

#### Square Formation
- [ ] Infantry can enter square formation (new stance or command)
- [ ] Square formation reduces cavalry damage (-40%) — visible in combat text
- [ ] Square formation increases artillery vulnerability (+50%) — visible in combat text
- [ ] AI uses square formation appropriately

#### Artillery SUPPORT Auto-Bombardment
- [ ] Artillery on SUPPORT order auto-bombards before supported marshal's combat
- [ ] Auto-bombardment appears in combat output with clear attribution
- [ ] Collateral damage rules still apply

#### Artillery Overwatch
- [ ] Passive -3% attack debuff on enemies in same region as friendly artillery
- [ ] Debuff visible in battle report modifier list

#### Regression Checks
- [ ] Regular bombardment still works
- [ ] Artillery can't-attack-after-move still enforced
- [ ] Cavalry counter vs artillery still works

---

## Gate 6: After V2b (Defiance/Vindication)

V2b upgrades STRONG/EXTREME concerns to defiance events.

### Checklist

#### Defiance Popup
- [ ] STRONG/EXTREME objections show defiance popup (different from MODERATE objection popup)
- [ ] Defiance popup offers appropriate choices
- [ ] Trust consequences display correctly

#### Vindication
- [ ] Vindication score changes visible in marshal management screen
- [ ] Vindication decay works over turns (if displayed)

#### Regression Checks
- [ ] MILD concerns still appear as flavor text only (no popup)
- [ ] MODERATE objections still work as before (proceed/accept alternative)
- [ ] Marshal management screen still loads without errors

---

## Gate 7: After Coalition Trigger

Coalition formation mechanics — threat level drives war declarations.

### Checklist

#### Coalition Notifications
- [ ] Threat level increase triggers notification (EU4-style alert)
- [ ] War declaration appears in campaign log
- [ ] Morning dispatch mentions coalition status

#### Display
- [ ] Threat level visible somewhere (ledger, notification, or dispatch)
- [ ] Coalition members listed when coalition forms

#### Regression Checks
- [ ] Notification system still works for all existing 9 triggers
- [ ] Campaign log doesn't break with new event types

---

## Gate 8: Session 66 (Final UI Audit)

Session 66 IS the comprehensive UI integration audit. No separate gate — the session itself is the gate. Claude Code will produce a full audit checklist covering all Phase 7 Core + 7b features across tooltips, tutorial, display formatting, and cross-system consistency.

---

## After Testing

Report results to Claude Code. Mark items that failed with details.
If all pass, say "Gate X passed" and proceed to next session.
