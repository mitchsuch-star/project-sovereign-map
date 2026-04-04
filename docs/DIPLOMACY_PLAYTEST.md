# Comprehensive Diplomacy Playtest Plan

**Purpose:** 100% confidence across all diplomacy features via manual UI testing in Godot.
**Estimated Time:** 120-150 minutes (full run). Can be split into sections.
**Prerequisites:** Backend running on port 8005 with debug mode enabled, Godot client connected.

> **Note on Godot Testing:** Godot has no built-in automated UI test framework. All popup rendering, button clicks, modal stacking, and screen transitions must be verified manually. The backend has 7,755+ tests covering logic — this playtest covers the **UI integration layer** that automated tests cannot reach.

---

## Setup Commands

```bash
# Start backend (with debug mode enabled for cheat/debug commands)
DEBUG_MODE=true ".venv\Scripts\python.exe" backend/main.py

# Two command families (type in Godot terminal):
#   /debug <cmd> — marshal/combat state manipulation (requires DEBUG_MODE=true)
#   cheat <cmd>  — diplomatic state manipulation (requires DEBUG_MODE=true OR LLM_MODE=mock)

# Cheat commands (diplomacy):
cheat give_dp 20                       # Give France DP (capped at max_dp)
cheat set_relation Austria 50          # Set France↔Austria relation
cheat set_threat 65                    # Set coalition threat level
cheat set_diplo_state Austria WAR      # Set diplomatic state
cheat set_war_exhaustion Britain 80    # Set war exhaustion (0-200)
cheat create_vassal Saxony             # Make nation a vassal of France
cheat set_vassal_loyalty Saxony 30     # Set vassal loyalty (0-100)
cheat set_talleyrand_trust 15          # Set Talleyrand trust level
cheat queue_ai_proposal Britain ARMISTICE  # Queue incoming AI proposal
cheat trigger_coalition                # Force coalition formation
cheat clear_dialogue                   # Clear stuck diplomatic dialogue

# Debug commands (combat/state):
/debug set_location Ney Belgium        # Teleport marshal
/debug set_strength Ney 15000          # Set troop strength
/debug set_trust Ney 80               # Set marshal trust
/debug set_authority 60                # Set player authority
/debug freeze_enemies                  # Toggle freeze all enemy AI

# NOTE: No direct debug for war_score or vassal_autonomy.
# War score changes via battles. Autonomy changes via "increase/decrease autonomy" commands.
```

---

## SECTION A: Diplomacy Button / Wizard (F1)

### A1. Wizard Opens — Nation Selection

```
Press F1 (or click [Diplomacy] button)
```

**Expected:**
- Wizard overlay opens (CanvasLayer 110, modal)
- Shows categorized nation list: "At War" (Britain, Prussia), "Treaties" (Saxony under OPEN_BORDERS), "Neutral" (Austria at PEACE)
- Each button shows nation name + current diplomatic state
- Input blocked behind wizard

### A2. Wizard Step 2 — Action Preview

```
Click on "Austria" in the wizard
```

**Expected:**
- Step 2 loads with Talleyrand's Assessment panel at top
- Shows: Current state (PEACE), Relation score + descriptor, 1-2 sentence assessment
- Bottom: Action buttons with DP costs and likelihood words (Favorable/Possible/Unlikely/Hopeless)
- Buttons colored by likelihood (green = Favorable, red = Hopeless)
- Unavailable actions shown disabled with reason text
- [Back] button returns to nation list

### A3. Wizard → Conversational Diplomacy Flow

```
cheat give_dp 10
Press F1 → Select Austria → Click "Propose Non-Aggression (1 DP)"
```

**Expected:**
- Wizard closes
- Terminal shows the command: ► "propose non-aggression with Austria"
- **Talleyrand responds with conversational dialogue** (NOT instant execution)
- Shows assessment text + options (e.g., "Send my terms", "Use Talleyrand's suggestion", "Modify terms")
- Player must type response to proceed
- This confirms wizard triggers conversational diplomacy (not a bypass)

### A4. Wizard — War Declaration

```
Press F1 → Select Austria → Click "Declare War"
```

**Expected:**
- Terminal shows: ► "declare war on Austria"
- Talleyrand may object (if concern level is MODERATE+)
- If no objection: War declared, relation drops, threat increases
- Diplomatic state changes to WAR

### A5. Wizard — Vassal Actions

```
cheat set_diplo_state Saxony VASSAL
Press F1 → Select Saxony
```

**Expected:**
- Step 2 shows vassal-specific info: loyalty %, autonomy level, tribute income
- Action buttons include: Invest, Increase Autonomy, Decrease Autonomy, Release Vassal
- Standard proposal buttons (alliance, etc.) NOT shown for vassals

### A6. Wizard — Back and Cancel

```
Press F1 → Select nation → Press [Back] → Press [Cancel]
```

**Expected:**
- [Back] returns to nation selection (Step 1)
- [Cancel] closes wizard entirely
- Input re-enabled after cancel
- No DP spent, no state changes

### A7. Wizard — Empty/Edge States

```
cheat give_dp 0
# (Start game fresh or ensure DP is 0)
Press F1 → Select Austria → Try any action
```

**Expected:**
- Actions requiring DP show as disabled with "Insufficient DP" reason
- Clicking disabled button does nothing

### A8. Wizard — open_for_nation() Handoff

```
# Requires active war (see Section Q for War Status Panel setup)
cheat set_diplo_state Britain WAR
# Wait for war status panel to show, click Britain war card
# In war detail popup, click [Negotiate Peace]
```

**Expected:**
- Diplomacy wizard opens directly at Step 2 for Britain (skips nation selection)
- Correct nation name shown in wizard header
- Assessment and action buttons load for Britain specifically
- [Back] returns to Step 1 (nation list), not the war detail popup

---

## SECTION B: Diplomatic Proposals (Terminal Commands)

### B1. Propose Peace (From WAR)

```
cheat give_dp 5
propose armistice with Britain
```

**Expected:**
- Talleyrand dialogue appears with assessment
- Shows acceptance likelihood
- Options to send/modify/dismiss
- Type "proceed" → proposal sent
- Result: ACCEPT (relation applied, state → ARMISTICE), COUNTER (new terms shown), or REJECT (cooldown message)

### B2. Propose Alliance Upgrade (Sequential)

```
cheat set_relation Austria 50
cheat give_dp 10
propose alliance with Austria
```

**Expected:**
- If jump transition needed (PEACE → ALLIANCE = 6 DP), shows total cost
- Talleyrand assesses feasibility
- Acceptance formula considers: relation, diplomat skill, personality, war score
- Natural language feedback explains key modifiers

### B3. Counter-Offer Flow

```
# Set up a scenario where counter is likely (score 30-49)
cheat set_relation Prussia -20
cheat give_dp 5
propose armistice with Prussia
# Proceed with proposal
proceed
```

**Expected:**
- AI generates counter-proposal with modified terms
- Counter shows: original terms vs. AI's requested changes
- Player options: Accept counter / Reject / Modify further
- If accept counter: treaty executed with AI's terms

### B4. Rejection + Cooldown

```
# Set up hostile scenario (score < 30)
cheat set_relation Britain -80
propose peace with Britain
proceed
```

**Expected:**
- Proposal rejected
- Cooldown message: "Britain won't consider another proposal for X turns"
- Attempting same proposal type within cooldown shows blocked message

### B5. Proposal with Talleyrand Objection

```
# Set up a scenario where Talleyrand objects (STRONG concern)
cheat set_relation Austria -50
declare war on Austria
```

**Expected:**
- Talleyrand STRONG objection fires (if applicable)
- Options: "Send my terms as ordered" (defiance risk), "Use Talleyrand's suggestion", "Modify"
- If proceed against objection: defiance risk warning shown
- Talleyrand trust may decrease

### B6. Break Treaty

```
cheat set_diplo_state Austria NON_AGGRESSION
break treaty with Austria
```

**Expected:**
- Confirmation dialogue
- On proceed: Treaty terminated, relation drops (-15 to -25), threat increases
- Authority -10, reliability -20
- Notification appears

### B7. Downgrade Relations

```
cheat set_diplo_state Austria ALLIANCE
cheat set_relation Austria 60
downgrade relations with Austria
```

**Expected:**
- Steps down one level: ALLIANCE → DEFENSIVE_ALLIANCE
- Relation penalty applied
- Cannot skip levels (must downgrade adjacently)

### B8. Send Ultimatum

```
cheat give_dp 5
send ultimatum to Austria
```

**Expected:**
- 2 DP cost
- Coercive demand presented to target
- If rejected: casus belli granted, can declare war without DP cost
- Cooldown applied

### B9. Casus Belli — Reduced War Cost

```
# After B8 ultimatum is rejected (casus belli granted):
declare war on Austria
```

**Expected:**
- War declaration costs 0 DP (instead of 1)
- Relation penalty halved: -15 (instead of -30)
- Threat penalty halved: +10 (instead of +20)
- Casus belli flag consumed after use

---

## SECTION C: AI Proposals (Incoming)

### C1. AI Proposes During End Turn

```
# Queue a proposal directly to test popup:
cheat queue_ai_proposal Britain ARMISTICE
end turn
```

**Expected:**
- **Incoming Proposal Popup** appears (CanvasLayer 112)
- Shows: proposal type, terms, AI nation, envoy personality
- Three buttons: [Accept] [Counter] [Reject]
- Game paused until player responds

### C2. Accept AI Proposal

```
# When incoming proposal popup shows:
Click [Accept]
```

**Expected:**
- Treaty executed immediately
- Diplomatic state updated
- Trade income begins (if applicable)
- Relation changes applied
- Popup closes, game resumes

### C3. Counter AI Proposal

```
Click [Counter]
```

**Expected:**
- Counter-offer dialogue shown in terminal
- Player can modify terms
- AI evaluates counter using M3 algorithm
- Result: accept modified, reject, or further counter

### C4. Reject AI Proposal

```
Click [Reject]
```

**Expected:**
- Proposal rejected
- Cooldown applied (3 turns: same nation can't propose again)
- Popup closes
- Relation may decrease slightly

### C5. AI Proposal Anti-Spam

```
# Reject AI proposal, then advance several turns
end turn (x3)
```

**Expected:**
- Same AI nation does NOT propose again within cooldown period
- Max 1 proposal delivered per turn (no spam popups)
- After cooldown expires, AI may propose again if conditions still met

### C6. Multiple AI Proposals Queued

```
# Queue proposals from multiple nations:
cheat queue_ai_proposal Britain ARMISTICE
cheat queue_ai_proposal Prussia NON_AGGRESSION
end turn
```

**Expected:**
- Only 1 proposal delivered per turn (highest priority first)
- Remaining proposals queued for subsequent turns
- Each popup shown individually, not stacked

---

## SECTION D: Coalition System

### D1. Threat Accumulation Display

```
Press D (Diplomatic Ledger) → Threat/Coalition tab
```

**Expected:**
- Shows current threat level (numeric + tier name)
- Tier display: Calm (0-29), Tension (30-39), Murmurs (40-59), Brewing (60-79)
- Lists qualifying coalition members (relation < -10, not vassal, not already at war with France)

### D2. Threat Increases from Actions

```
cheat set_threat 25
declare war on Austria
# Check threat
Press D → Threat tab
```

**Expected:**
- Threat increased by +20 (war declaration on non-belligerent)
- New threat: 45 (Murmurs tier)
- Diplomatic ledger updates to reflect new tier

### D3. Coalition Brewing (3-Turn Countdown)

```
cheat set_threat 62
end turn
```

**Expected:**
- **Persistent notification** appears: "A coalition is brewing against France. [Nations]. 3 turns remain."
- Morning dispatch alert mentions coalition brewing
- Diplomatic ledger Threat tab shows countdown: "3 turns remaining"
- Talleyrand advisory available about defusing

### D4. Coalition Brewing Countdown

```
end turn    # 2 turns remaining
end turn    # 1 turn remaining
```

**Expected:**
- Notification updates each turn with decreasing countdown
- Dispatch mentions remaining turns
- Threat tab updates countdown number
- If player improves relations with all members above -10: brewing cancels

### D5. Coalition Declaration

```
end turn    # Countdown hits 0
```

**Expected:**
- **Coalition Declaration Popup** appears (CanvasLayer 117, informational)
- Shows: coalition members, leader nation, posture
- Single [Continue] button (info-only, not a choice)
- All coalition members enter WAR with France simultaneously
- War cascade notifications
- Threat continues tracking

### D6. Coalition Defusal During Brewing

```
cheat set_threat 62
end turn    # Brewing starts (3 turns)
# Improve relations with ALL qualifying members
cheat set_relation Britain 0
cheat set_relation Prussia 0
cheat set_relation Austria 0
end turn
```

**Expected:**
- If no qualifying nations remain (all relations > -10): brewing cancels
- Notification: "Coalition threat has subsided"
- Alternative: if threat drops below 40, also cancels

### D7. Coalition Momentum Rule

```
cheat set_threat 62
end turn    # Brewing starts
cheat set_threat 55    # Drop below 60 but above 40
end turn
```

**Expected:**
- Brewing CONTINUES (momentum rule: only cancels at <40 or 0 qualifying nations)
- Countdown still decrements
- Coalition will still declare if countdown reaches 0

### D8. Instant Coalition (Threat 80+)

```
cheat set_threat 82
end turn
```

**Expected:**
- Coalition forms IMMEDIATELY (no 3-turn countdown)
- Coalition Declaration Popup appears instantly
- Same effects as D5 but without brewing phase

### D9. Coalition Dissolution

```
# With active coalition:
cheat set_threat 15
end turn
```

**Expected:**
- If threat drops below 20: coalition dissolves
- Notification: "The coalition has dissolved"
- War states remain (members still at war, but no longer coordinated)
- 5-turn cooldown before new coalition can form

### D10. British Subsidy (During Coalition)

```
# With active coalition including Britain:
end turn
```

**Expected:**
- Britain sends 200g/turn to coalition partner with lowest relation (>-20)
- Visible in dispatch or ledger economy section
- +5 relation bonus between Britain and recipient

---

## SECTION E: Vassal System

### E1. Create Vassal (Treaty Path)

```
cheat set_diplo_state Saxony OPEN_BORDERS
cheat set_relation Saxony 40
cheat give_dp 5
propose vassalage to Saxony
proceed
```

**Expected:**
- Talleyrand dialogue about vassalization
- If accepted: Saxony becomes VASSAL
- Loyalty starts at 60 + generosity bonus
- Autonomy defaults to SATELLITE
- Threat +5
- Saxony's marshals transferred to French control (trust = 40)

### E2. Vassal in Diplomatic Ledger

```
Press D → Nations tab
```

**Expected:**
- Saxony shows as "VASSAL" with special formatting
- Shows: loyalty %, autonomy level, tribute income
- Clicking reveals vassal-specific details

### E3. Vassal Loyalty Degradation

```
# With vassal Saxony — decrease autonomy for fastest degradation:
decrease autonomy Saxony
# (Sets to PUPPET if currently SATELLITE)
end turn (x5)
```

**Expected:**
- Loyalty decreases each turn (PUPPET: -4/turn drift)
- Morning dispatch warns at loyalty <40: "unrest in Saxony"
- Warns at loyalty <10: "danger — Saxony near rebellion"
- Diplomatic ledger vassal tab shows current loyalty

### E4. Vassal Investment

```
cheat give_dp 3
invest in Saxony
```

**Expected:**
- Costs 1 DP + 200 gold
- Loyalty +15
- Relations +5
- Talleyrand dialogue confirms investment

### E5. Vassal Autonomy Changes

```
increase autonomy Saxony
# OR
decrease autonomy Saxony
```

**Expected:**
- Autonomy changes: PUPPET ↔ SATELLITE ↔ AUTONOMOUS
- Higher autonomy = slower loyalty drain, less tribute
- Lower autonomy = faster drain, more tribute
- Feedback shows new autonomy level and effects

### E6. Vassal Rebellion Warning Popup

```
# Get vassal loyalty critically low
cheat set_vassal_loyalty Saxony 8
end turn
```

**Expected:**
- **Vassal Rebellion Popup** appears (CanvasLayer 115)
- Shows: vassal name, current loyalty, warning text
- Three buttons:
  - [Invest] — 1 DP + 200g → Loyalty +15, relations +5
  - [Send Garrison] — 2 AP → Loyalty +10 (this turn only)
  - [Accept Risk] — Do nothing
- Choice affects loyalty immediately

### E7. Vassal Rebellion

```
cheat set_vassal_loyalty Saxony 0
end turn
```

**Expected:**
- Vassal rebels: diplomatic state VASSAL → WAR
- Saxony's marshals transferred back to Saxony (trust reset to 40)
- All other vassals: -10 loyalty (cascade)
- Notification: "Saxony has rebelled!"
- Threat -8 (or +15 if viewed as loss)

### E8. Release Vassal

```
release Saxony
```

**Expected:**
- Vassal bond broken
- Diplomatic state: VASSAL → PEACE
- Threat -8
- 5-turn cooldown before re-vassalization
- Removed from Continental System if applicable

### E9. Defection Cascade Warning

```
# Get 2+ vassals with loyalty < 25
cheat create_vassal Bavaria
cheat set_vassal_loyalty Saxony 20
cheat set_vassal_loyalty Bavaria 20
end turn
```

**Expected:**
- "Empire Trembles" notification
- Dispatch event: defection cascade warning
- Both vassals listed as at-risk

---

## SECTION F: Diplomatic Ledger (D Key)

### F1. Open/Close Toggle

```
Press D
```

**Expected:**
- Diplomatic Ledger overlay opens (CanvasLayer 50)
- Press D again: closes
- Other hotkeys (T, G, R) close ledger and open respective screen

### F2. Nations Tab

```
Press D → Nations tab (default)
```

**Expected:**
- Lists all nations with:
  - Diplomatic state (colored: red=WAR, green=ALLIANCE, blue=treaties)
  - Relation score + descriptor (Hostile/Wary/Neutral/Friendly/Loyal)
  - Military strength (fog-filtered: exact if FULL, approximate if PARTIAL, "Unknown" if UNKNOWN)
- France NOT listed (you don't have a relationship with yourself)

### F3. Treaties Tab

```
Press D → Treaties tab (press 2 or click)
```

**Expected:**
- Lists all active treaties with clauses
- Shows: nation pair, treaty type, gold payments, territory clauses, AP clauses
- Active treaties only (not expired)

### F4. Threat/Coalition Tab

```
Press D → Threat tab (press 3 or click)
```

**Expected:**
- Current threat level (number + tier name + color)
- Qualifying coalition members list
- If brewing: countdown display ("2 turns remaining")
- If active coalition: leader, posture, member states
- If cooldown: "Coalition cooldown: X turns remaining"

### F5. Talleyrand Tab

```
Press D → Talleyrand tab (press 4 or click)
```

**Expected:**
- Diplomat information (Talleyrand stats, trust level)
- Ongoing missions list (type, target, turns remaining)
- Sabotage incidents log
- DP generation rate breakdown

### F6. Fog-Filtered Army Strength

```
# With varying fog visibility:
Press D → Nations tab
```

**Expected:**
- FULL visibility: exact troop count (e.g., "45,000")
- PARTIAL visibility: approximate (e.g., "~45,000")
- STALE visibility: named bands ("Considerable Force")
- UNKNOWN visibility: "Unknown"
- Verify no enemy info leaks through fog

### F7. Number Key Sub-Tab Switching

```
Press D → Press 1, 2, 3, 4
```

**Expected:**
- 1 = Nations, 2 = Treaties, 3 = Threat/Coalition, 4 = Talleyrand
- Each switch is instant, no flicker
- Content fully re-renders on tab switch

---

## SECTION G: Diplomatic Advisory (Talleyrand Conversations)

### G1. Nation Assessment

```
what about Austria?
```

**Expected:**
- Talleyrand provides detailed assessment:
  - Diplomatic state, war score, relations
  - Diplomat personality description
  - Military strength (fog-filtered)
  - 1-2 sentence recommendation
  - Action hints (specific proposal suggestions)

### G2. Threat Comparison

```
who is the bigger threat?
```

**Expected:**
- All nations ranked by threat score
- Factors: relation, military strength, diplomatic state
- Clear ranking with explanation

### G3. Action Recommendation

```
what should I do?
```

**Expected:**
- Talleyrand recommends specific diplomatic action
- Context-aware (considers current wars, relations, threat level)
- Actionable suggestion (e.g., "Propose non-aggression with Austria")

### G4. Feasibility Check

```
can we beat Prussia?
```

**Expected:**
- Military comparison (troop counts, marshal quality)
- Fog-filtered (only shows what player can see)
- Confidence level: High/Medium/Low
- Strategic advice on timing

---

## SECTION H: Diplomatic Missions

### H1. Improve Relations Mission

```
cheat give_dp 3
improve relations with Austria
```

**Expected:**
- Talleyrand accepts mission (1 DP)
- Per-turn: +5 relation with Austria
- Shows in Talleyrand tab of diplomatic ledger

### H2. Court Nation Mission

```
court Austria
```

**Expected:**
- 2 DP cost
- Higher risk: 20% per-turn chance of discovery
- +5 relation/turn for 3 turns
- If discovered: sabotage popup, -3 relation damage

### H3. Gather Intel Mission

```
spy on Britain
```

**Expected:**
- 1 DP cost
- Improves fog visibility for British regions for 3 turns
- Shows in ledger Talleyrand tab

### H4. Undermine Alliance Mission

```
undermine alliance between Britain and Prussia
```

**Expected:**
- 2 DP cost
- -3 relation/turn between target pair
- Can target any nation pair (not necessarily involving France)
- 3-turn duration

---

## SECTION I: Talleyrand Sabotage & Defiance

### I1. Sabotage Discovery Popup

```
# Requires: Talleyrand intercepts a proposal (diplomatic_defiance.py triggers)
# Lower Talleyrand trust to increase sabotage chance:
cheat set_talleyrand_trust 25
cheat give_dp 5
propose alliance with Austria
proceed
# May need multiple attempts — sabotage is probabilistic
```

**Expected (if triggered):**
- **Sabotage Discovery Popup** appears (CanvasLayer 116)
- Shows: what Talleyrand modified in the proposal
- Two buttons: [Confront] [Overlook]
- Confront: Trust impact, diplomatic consequences
- Overlook: Talleyrand continues, modified proposal stands

### I2. Talleyrand Redemption Popup

```
# Set Talleyrand trust below 20:
cheat set_talleyrand_trust 15
end turn
```

**Expected (if triggered):**
- **Talleyrand Redemption Popup** appears (CanvasLayer 114)
- Three buttons: [Apologize] [Replace] [Continue]
- Apologize: Trust partially restored (+15 trust, -5 authority)
- Replace: New diplomat assigned (different personality, irreversible)
- Continue: Accept low trust, increased defiance risk (-10 authority)

---

## SECTION J: War System Integration

### J1. Declare War

```
cheat give_dp 3
declare war on Austria
```

**Expected:**
- 1 DP cost
- Diplomatic state → WAR
- Relation drops -20
- Threat +20
- Battle records cleared for this pair
- Notification appears

### J2. War Score Tracking

```
# After some battles in a war:
Press D → Nations tab (check war score indicator)
```

**Expected:**
- War score visible for nations at war with France
- Updates after battles (±3 per battle, ±10 decisive, ±20 capital)
- Decays -2/turn if no battles for 3+ turns

### J3. War Cascade

```
# Requires Austria allied with Britain (non-France alliance).
# This must be set up through gameplay or backend manipulation.
# Then declare war:
declare war on Austria
```

**Expected:**
- Austria enters war with France (direct)
- Britain automatically enters war with France (cascade via alliance)
- Both receive WAR state
- Threat +20 per declaration (may stack)
- Notification explains cascade

### J4. Armistice Expiration

```
cheat set_diplo_state Britain ARMISTICE
# Wait 5 turns:
end turn (x5)
```

**Expected:**
- Armistice timer decrements each turn
- After 5 turns: automatically transitions to PEACE
- Notification: "Armistice with Britain has expired — now at PEACE"
- Trade income begins at PEACE rate (50g/turn)

### J5. Auto-Downgrade from Relation Decay

```
cheat set_diplo_state Austria ALLIANCE
cheat set_relation Austria 39    # Below ALLIANCE threshold of 40
end turn
```

**Expected:**
- Auto-downgrade: ALLIANCE → DEFENSIVE_ALLIANCE
- Notification: "Diplomatic state with Austria downgraded due to poor relations"
- No DP cost (automatic)

---

## SECTION K: Trade Income & Economy

### K1. Trade Income Display

```
Press T → Economy tab (Strategic Ledger)
```

**Expected:**
- Shows trade income per nation pair
- PEACE: 50g/turn, OPEN_BORDERS: 100, NON_AGG: 150, DEF_ALLIANCE: 150, ALLIANCE: 200
- WAR/ARMISTICE: 0
- Diminishing returns visible if multiple alliances

### K2. Trade Income Changes with State

```
cheat set_diplo_state Austria ALLIANCE
end turn
# Check economy
Press T → Economy tab
```

**Expected:**
- Austria trade income shows 200g/turn
- If 2nd alliance: 0.75× rate on second
- Total income visible in economy section

### K3. Vassal Tribute vs Trade

```
# With Saxony as vassal:
Press T → Economy tab
```

**Expected:**
- Vassal tribute shown (not trade income)
- Amount = vassal income × autonomy tribute rate
- PUPPET: 100%, SATELLITE: 75%, AUTONOMOUS: 50%

---

## SECTION L: Save/Load with Diplomatic State

### L1. Save with Active Diplomacy

```
# Set up complex diplomatic state:
cheat set_diplo_state Austria NON_AGGRESSION
cheat set_threat 45
cheat give_dp 5
# Save
/save test_diplo
```

**Expected:**
- Save completes without error
- No crash on serialization of diplomatic fields

### L2. Load Preserves Diplomatic State

```
/load test_diplo
Press D → Check all 4 tabs
```

**Expected:**
- Diplomatic states preserved (Austria = NON_AGGRESSION)
- Threat level preserved (45)
- DP preserved
- Nation relations preserved
- Active treaties preserved
- Vassal states preserved (if any)
- Coalition state preserved (if brewing/active)
- Armistice timers preserved

### L3. Save with Pending Dialogue

```
propose peace with Britain
# Don't respond to Talleyrand dialogue
/save mid_dialogue
/load mid_dialogue
```

**Expected:**
- Pending diplomatic dialogue restored
- Player can still respond after load
- No "stuck state" where dialogue blocks all commands

### L4. Save/Load with War Status Panel

```
# Set up active war with war status panel visible:
cheat set_diplo_state Britain WAR
end turn
# Verify war panel shows, then save/load:
/save test_war_panel
/load test_war_panel
```

**Expected:**
- War status panel (bottom-right HUD) reappears after load
- War cards show correct data
- Clicking cards still opens war detail popup
- Panel visibility state preserved

---

## SECTION M: Edge Cases & Regression

### M1. Proposal to Self

```
propose alliance with France
```

**Expected:**
- Error message: "Cannot propose to yourself" or similar
- No crash, no state change

### M2. Proposal to Nation Already at Same State

```
cheat set_diplo_state Austria PEACE
propose peace with Austria
```

**Expected:**
- Error: "Already at PEACE with Austria" or similar
- No DP spent

### M3. Double War Declaration

```
cheat set_diplo_state Austria WAR
declare war on Austria
```

**Expected:**
- Error: "Already at war with Austria"
- No duplicate threat increase

### M4. Vassal of a Vassal

```
# If Saxony is France's vassal, try to vassalize a nation that's Saxony's vassal (if possible)
```

**Expected:**
- Should be blocked: cannot vassal a nation already vassalized by another

### M5. Release Cooldown Enforcement

```
release Saxony
# Immediately try to re-vassalize:
propose vassalage to Saxony
```

**Expected:**
- Blocked: "Cannot re-vassalize Saxony for X more turns" (5-turn cooldown)

### M6. DP Zero — All Actions Blocked

```
# Ensure DP is 0 (start fresh game or spend all DP)
propose alliance with Austria
```

**Expected:**
- Error: "Insufficient Diplomatic Points"
- No action taken, no dialogue started

### M7. Simultaneous Popups (Priority Order)

```
# Create conditions for multiple popups in one turn:
# Coalition brewing + AI proposal + vassal rebellion
cheat set_threat 62
cheat set_vassal_loyalty Saxony 5
cheat queue_ai_proposal Prussia ARMISTICE
end turn
```

**Expected:**
- Popups appear ONE AT A TIME in priority order (not stacked)
- Priority: Coalition > Diplomatic Objection > Incoming Proposal > Vassal Rebellion
- Each popup must be dismissed before next appears
- No popup lost or skipped

### M8. Hotkey Blocking During Popups

```
# When any popup is showing:
Press D, T, G, F1, R
```

**Expected:**
- All hotkeys blocked while modal popup is active (dialog_manager.is_any_modal_open())
- No screen can open behind popup
- Only popup buttons respond to input

### M9. Rapid F1 Spam

```
Press F1 quickly 5 times
```

**Expected:**
- Wizard opens once, doesn't duplicate
- No crash or visual glitch
- Subsequent presses ignored while wizard is open

### M10. Nation Eliminated

```
# If a nation loses all territory/marshals (eliminated):
Press D → Check eliminated nation
Press F1 → Check eliminated nation in wizard
```

**Expected:**
- Eliminated nation handled gracefully
- Not shown as valid target in wizard
- Treaties with eliminated nation cleared
- No crash when iterating nations

### M11. Fog Leak Prevention

```
# With no visibility on enemy regions:
Press D → Nations tab
what about Prussia?
```

**Expected:**
- Enemy army strength shows "Unknown" (not exact numbers)
- Advisory uses fog-filtered data
- No troop counts revealed through diplomatic channels

### M12. Dialogue Guard — All Commands Blocked

```
propose peace with Britain
# Dialogue pending, now try:
Ney, attack Wellington
```

**Expected:**
- Military command blocked: "Awaiting diplomatic response"
- Must respond to Talleyrand dialogue first (accept/reject/proceed/modify)
- After responding, normal commands resume

### M13. Dialogue Timeout (Next Turn)

```
propose peace with Britain
# Don't respond, just:
end turn
```

**Expected:**
- Pending dialogue cleared on turn advance
- No stuck state
- Player can act normally next turn

### M14. Clear Stuck Dialogue (Debug Recovery)

```
propose peace with Britain
# Dialogue stuck, use cheat to recover:
cheat clear_dialogue
Ney, move to Belgium
```

**Expected:**
- `cheat clear_dialogue` clears pending diplomatic dialogue
- Normal commands resume immediately
- No side effects on diplomatic state

---

## SECTION N: Continental System

> **STATUS: NOT FULLY IMPLEMENTED.** The Continental System trade penalties and vassal auto-enrollment are wired, but there is no player-facing activation command. The tests below document expected behavior when activation is implemented. Skip this section for now.

### N1. Enforce Continental System

```
# NO COMMAND EXISTS YET — activation path not implemented
# Expected future command: enforce continental system on Austria
```

**Expected (when implemented):**
- 1 DP/turn cost
- Target nation loses naval/trade income (-300g/turn)
- Requires 2+ members for full effect
- Shows in Talleyrand tab

---

## SECTION O: Morning Dispatch — Diplomatic Events

### O1. Coalition Threat in Dispatch

```
cheat set_threat 45
end turn
# Check dispatch (should auto-show, or press R)
```

**Expected:**
- Morning dispatch mentions coalition threat level
- "Murmurs of coalition" or similar
- Fog-filtered: only mentions nations player has intel on

### O2. Vassal Loyalty Warning in Dispatch

```
cheat set_vassal_loyalty Saxony 35
end turn
```

**Expected:**
- Dispatch mentions "Unrest in Saxony" (loyalty < 40)
- At loyalty < 10: "Saxony near rebellion"

### O3. Treaty Expiration in Dispatch

```
# With armistice about to expire:
end turn
```

**Expected:**
- Dispatch mentions impending armistice expiration
- "Armistice with Britain expires in X turns"

### O4. War Cascade in Dispatch

```
# After a war cascade:
end turn
```

**Expected:**
- Dispatch explains cascade: "Austria's alliance with Britain has drawn them into war"

---

## SECTION P: Notification Bar — Diplomatic Alerts

### P1. Persistent Notifications

```
# With various diplomatic events:
Check notification bar (top of screen)
```

**Expected notifications for:**
- Coalition threat escalation (Tension → Murmurs → Brewing)
- Coalition declared / dissolved
- Vassal rebellion imminent
- Treaty broken
- Auto-downgrade
- Proposal rejected
- Sabotage discovered

### P2. Notification Dismissal

```
Click on notification to dismiss
```

**Expected:**
- Notification removed from bar
- Doesn't reappear unless new event triggers

---

## SECTION Q: War Status Panel HUD (Bottom-Right)

> **Added DA-4.** Tests the 3-layer war display system: War Status Panel (Layer 25, always-visible HUD) → War Detail Popup (Layer 30, click-through) → Diplomacy Wizard handoff.

### Q1. Panel Appears When at War

```
cheat set_diplo_state Britain WAR
end turn
```

**Expected:**
- War Status Panel appears at bottom-right of screen (CanvasLayer 25)
- Shows war card for Britain with tug-of-war score bar
- War duration shown in turns
- Panel is non-modal — does NOT block input or hotkeys

### Q2. Panel Hides When at Peace

```
# End all wars (propose peace or use cheat):
cheat set_diplo_state Britain PEACE
end turn
```

**Expected:**
- War Status Panel disappears (no active wars to show)
- No orphaned UI elements left behind

### Q3. Multiple War Cards

```
cheat set_diplo_state Britain WAR
cheat set_diplo_state Austria WAR
end turn
```

**Expected:**
- Panel shows 2 war cards, one per belligerent
- Each card has its own tug-of-war bar
- Cards stack vertically
- Panel resizable via drag handles on left/top edges

### Q4. Coalition Grouping in Panel

```
cheat trigger_coalition
end turn
```

**Expected:**
- Coalition header card appears at top of panel (clickable)
- Individual member war cards indented under coalition header
- Coalition card shows coalition name/leader
- Non-coalition wars shown separately below

### Q5. Armistice Cards in Panel

```
cheat set_diplo_state Britain ARMISTICE
end turn
```

**Expected:**
- Armistice card appears in panel
- Shows remaining turns until expiration
- Visually distinct from active war cards

### Q6. Panel Resizing

```
# With war panel visible:
Drag left edge to resize width
Drag top edge to resize height
```

**Expected:**
- Panel resizes smoothly
- Content reflows to fit new size
- Minimum size enforced (panel doesn't collapse to nothing)
- Resize persists during session

---

## SECTION R: War Detail Popup (Click-Through)

> **Added DA-4.** Click on war/coalition/armistice card in War Status Panel to see detailed info.

### R1. War Detail — Bilateral War View

```
# With active war:
cheat set_diplo_state Britain WAR
end turn
# Click Britain's war card in the War Status Panel
```

**Expected:**
- **War Detail Popup** opens (CanvasLayer 30)
- Shows tug-of-war score meter (bilateral war score)
- Score breakdown: territory, battles, decisive, capital components
- War duration in turns
- Enemy war exhaustion level
- Recent battles with outcomes listed
- [Negotiate Peace] button at bottom

### R2. War Detail — Coalition View

```
# With active coalition:
cheat trigger_coalition
end turn
# Click coalition header card in War Status Panel
```

**Expected:**
- Coalition detail view opens
- Shows: coalition leader, posture (AGGRESSIVE/BALANCED/CAUTIOUS)
- Member list with per-member: war exhaustion, army strength
- Coordination quality between pairs
- Weak link indicator (member most likely to break)
- [Target X] buttons for individual coalition members

### R3. War Detail — Armistice View

```
cheat set_diplo_state Britain ARMISTICE
end turn
# Click Britain's armistice card in War Status Panel
```

**Expected:**
- Armistice detail view opens
- Shows: remaining turns, relation score + descriptor
- Trend indicator: rising/falling/stable relations
- [Diplomatic Options] button → opens wizard for that nation

### R4. War Detail — Negotiate Peace Handoff

```
# With active war detail popup open:
Click [Negotiate Peace]
```

**Expected:**
- War detail popup closes (or stays behind)
- Diplomacy Wizard opens at Step 2 for that specific nation (via `open_for_nation()`)
- Wizard shows peace/armistice options for the nation
- This is the Layer 2 → wizard handoff

### R5. War Detail — Target Coalition Member

```
# With coalition detail popup open:
Click [Target X] for a non-leader coalition member
```

**Expected:**
- Emits target_clicked signal for that nation
- Opens diplomacy wizard at Step 2 for that nation (via `open_for_nation()`)
- Player can propose separate peace / armistice with that member

### R6. War Detail — Refresh in Place

```
# With war detail popup open for Britain:
# Fight a battle or end turn (war score changes)
end turn
```

**Expected:**
- War detail popup updates its data without closing
- Score breakdown refreshes to reflect new war score
- Recent battles list updates
- No flicker or popup re-open animation

---

## SECTION S: Alliance Paradox Popup

> **Added Deep Audit S8.** Fires when attacking a marshal whose nation has an active alliance with France.

### S1. Alliance Paradox — Attack Ally's Marshal

```
# Set up alliance with Austria:
cheat set_diplo_state Austria ALLIANCE
cheat set_relation Austria 60
# Move a French marshal adjacent to an Austrian marshal:
/debug set_location Ney Bavaria
# Attack the Austrian:
Ney, attack [Austrian marshal name]
```

**Expected:**
- **Alliance Paradox Popup** appears (CanvasLayer 111)
- Text explains: attacking would violate alliance with Austria
- Two buttons:
  - [Honor Austria] — cancels the attack, alliance preserved
  - [Break Austria Alliance] — alliance broken, attack proceeds
- No other input accepted while popup is showing

### S2. Alliance Paradox — Honor Choice

```
# When alliance paradox popup shows:
Click [Honor Austria]
```

**Expected:**
- Attack cancelled
- Alliance with Austria preserved
- No relation or threat changes
- Normal command input resumes

### S3. Alliance Paradox — Break Choice

```
# When alliance paradox popup shows:
Click [Break Austria Alliance]
```

**Expected:**
- Alliance with Austria immediately broken
- Diplomatic state changes (ALLIANCE → PEACE or appropriate level)
- Relation penalty applied
- Threat increase
- Attack proceeds as normal against the Austrian marshal

---

## SECTION T: Proposal Confirm Popup

> **Added Session 8C.** Final review screen before sending player-initiated diplomatic proposals.

### T1. Proposal Confirm — Terms Review

```
cheat give_dp 5
cheat set_relation Austria 30
propose non-aggression with Austria
# Navigate through Talleyrand dialogue to "send" step
```

**Expected:**
- **Proposal Confirm Popup** appears (CanvasLayer 109)
- Shows: proposed terms summary
- Harshness level indicator (Low/Moderate/High/Very High)
- Acceptance estimate (percentage or qualitative)
- DP cost displayed
- Talleyrand commentary in italic gold text (smart suggestions)

### T2. Proposal Confirm — Send

```
# When proposal confirm popup shows:
Click [Send] (or equivalent confirm button)
```

**Expected:**
- Proposal sent to target nation
- AI evaluates and responds: Accept/Counter/Reject
- DP deducted
- Popup closes

### T3. Proposal Confirm — Cancel

```
# When proposal confirm popup shows:
Click [Cancel] or [Back]
```

**Expected:**
- Proposal cancelled, not sent
- No DP spent
- Returns to dialogue or closes entirely
- No state changes

---

## CHECKLIST SUMMARY

| Section | Tests | Feature Area | Priority |
|---------|-------|-------------|----------|
| A: Diplomacy Wizard | 8 | F1 button, nation/action selection, handoff | HIGH |
| B: Proposals | 9 | All proposal types, counter-offers, casus belli | HIGH |
| C: AI Proposals | 6 | Incoming popups, accept/counter/reject, anti-spam | HIGH |
| D: Coalition | 10 | Threat, brewing, declaration, dissolution, subsidy | HIGH |
| E: Vassal | 9 | Creation, loyalty, rebellion, investment, release | HIGH |
| F: Diplomatic Ledger | 7 | 4 tabs, fog filtering, sub-tab switching | MEDIUM |
| G: Advisory | 4 | Talleyrand conversations | MEDIUM |
| H: Missions | 4 | Improve/court/spy/undermine | MEDIUM |
| I: Sabotage/Defiance | 2 | Sabotage discovery, redemption | LOW (rare triggers) |
| J: War Integration | 5 | Declaration, cascade, armistice, auto-downgrade | HIGH |
| K: Economy | 3 | Trade income, tribute | MEDIUM |
| L: Save/Load | 4 | Diplomatic state persistence, war panel | HIGH |
| M: Edge Cases | 14 | Regression, error handling, fog, priority, recovery | HIGH |
| N: Continental System | 1 | Trade embargo (NOT IMPLEMENTED — skip) | DEFERRED |
| O: Dispatch | 4 | Diplomatic events in morning briefing | MEDIUM |
| P: Notifications | 2 | Persistent alert bar | MEDIUM |
| Q: War Status Panel | 6 | Bottom-right HUD, war/coalition/armistice cards | HIGH |
| R: War Detail Popup | 6 | Click-through detail, score breakdown, handoff | HIGH |
| S: Alliance Paradox | 3 | Honor/break ally choice on attack | HIGH |
| T: Proposal Confirm | 3 | Final terms review before sending | MEDIUM |
| **TOTAL** | **110** | | |

---

## CAN GODOT TEST AI?

**Short answer: Partially, through end turns.**

- **AI proposals:** Yes — advance turns until AI triggers proposal (P1-P7). Or use `cheat queue_ai_proposal` to inject directly.
- **AI counter-offers:** Yes — send proposals AI will counter (score 30-49). Verify M3 algorithm output.
- **Coalition AI posture:** Partially — form coalition via `cheat trigger_coalition`, advance turns, observe AI attack patterns via dispatch/map.
- **AI-AI diplomacy:** Backend only — AI-AI proposals happen invisibly. Check via diplomatic ledger treaties tab.
- **AI diplomatic personality:** Observe via counter-offer terms and rejection messages.
- **AI enemy movement during coalition:** Observe on map — convergence bias should make coalition members approach French territory.

**What requires backend-only testing:**
- Exact acceptance formula values (use pytest)
- Precise cooldown timing (use pytest)
- Coalition friction calculations (use pytest)
- War exhaustion accumulation (use pytest)
- Sweetener cap enforcement (use pytest)

**Recommendation:** Use Godot for integration/UX verification. Use pytest for numerical precision. The 7,755+ backend tests already cover formula correctness — the playtest covers "does the player actually see the right thing."
