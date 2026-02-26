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

## Gate 6: After V2b (Defiance/Vindication/Authority)

V2b upgrades STRONG/EXTREME concerns to defiance events. Sessions 0-2 implemented backend mechanics; Session 3 wired the frontend.

### Setup

1. Start backend with `LLM_MODE=mock`: `.venv\Scripts\python.exe backend/main.py`
2. Launch Godot client
3. To trigger defiance: need a STRONG/EXTREME objection + insist. Use aggressive marshal (Ney) with low trust + high vindication, or cautious marshal with hostile relationship SUPPORT order.

### Defiance Display
- [ ] STRONG/EXTREME objection → player insists → defiance message appears (bordered "DEFIANCE" block, distinct from objection popup)
- [ ] Defiance RIGHT: outcome shows "VINDICATED — Marshal was right" in green, trust +2 visible
- [ ] Defiance WRONG: outcome shows "FAILURE — Marshal was wrong" in red, trust -5 visible
- [ ] Defiance INCONCLUSIVE (sulk): message shows "INCONCLUSIVE — No clear result"
- [ ] Failed roll: normal message includes "discipline held" Berthier flavor text (no defiance block)
- [ ] Berthier flavor text appears in defiance block (goldenrod color)
- [ ] Authority change shown in defiance block when applicable (-5 right, +3 wrong)
- [ ] MODERATE objection → insist: NO defiance possible (regression check)
- [ ] MILD concern: flavor text only, no popup, no defiance (regression check)

### Vindication Display
- [ ] Marshal management screen (G key) shows vindication score for each marshal
- [ ] Positive vindication shown in green with + sign
- [ ] Negative vindication shown in red
- [ ] Zero vindication shown in neutral color
- [ ] Vindication score updates visible after defiance resolution (reload marshal management)
- [ ] Vindication decay observable over 3+ turns of no objections (score decrements toward 0)

### Authority Display
- [ ] Authority value + label visible in strategic ledger (T key → Forces tab) header
- [ ] Authority visible in morning dispatch SITUATION section
- [ ] Authority visible in dispatch re-read screen (D key) SITUATION section
- [ ] Authority color: green at ≥80 (Strong), neutral at 50-79 (Normal), red at <50 (Weak)
- [ ] Authority threshold event ("Whispers of Weakness" etc.) appears as bordered block when threshold crossed
- [ ] Excessive trust pattern shows authority decline over multiple objection responses

### Relationship SUPPORT
- [ ] Order hostile marshal to SUPPORT rival → objection popup fires
- [ ] Aggressive + hostile target: STRONG concern, defiance possible after insist
- [ ] Cautious + hostile target: MODERATE concern, no defiance
- [ ] Compromise: timed 3-turn SUPPORT → auto-expires after 3 turns
- [ ] Literal + hostile target: no objection (regression check)

### Fog-Aware Objections
- [ ] Attack into UNKNOWN region: cautious marshal objects (STRONG), aggressive doesn't
- [ ] Attack with STALE intel (3+ turns old): cautious shows MODERATE concern
- [ ] No objections about enemies the marshal can't see (fog leak regression)

### Notification & Log
- [ ] Defiance notification appears in notification bar (HIGH priority, red)
- [ ] Defiance event appears in campaign log with correct one-liner
- [ ] Dismissing defiance notification works
- [ ] Authority threshold notification appears when authority crosses 70/50/30

### Regression Checks
- [ ] Normal 1v1 combat still works
- [ ] Save/load preserves all new fields (vindication, cooldown, authority, recent_responses format)
- [ ] Old saves load correctly (backward-compatible defaults)
- [ ] Marshal management screen loads without errors
- [ ] All 10 existing notification types still work
- [ ] Strategic orders (SUPPORT/PURSUE/HOLD/MOVE_TO) still function normally
- [ ] V1 disobedience path still works (disobeyed flag)
- [ ] Redemption dialog still triggers at critical trust levels
- [ ] Battle reports display correctly (no V2b interference)

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
