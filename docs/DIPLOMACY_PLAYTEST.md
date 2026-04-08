# Diplomacy Playtest Results

**Purpose:** Manual UI testing of all diplomacy features in Godot. Contains PASS/FAIL results from live playtesting.
**Prerequisites:** Backend running on port 8005 with debug mode enabled, Godot client connected.

> **Note on Godot Testing:** Godot has no built-in automated UI test framework. All popup rendering, button clicks, modal stacking, and screen transitions must be verified manually. The backend has 7,900+ tests covering logic — this playtest covers the **UI integration layer** that automated tests cannot reach.
> **Template archived:** `docs/archive/DIPLOMACY_PLAYTEST_PLAN.md`

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
- PASS
- Each button shows nation name + current diplomatic state
- PASS
- Input blocked behind wizard
- PASS
- ONLY NOTE IS I CANNOT TELL THEIR RELATIONSHIPS WITH EACHOTHER ANY WAY TO DO THIS? PERHAPS A WAY TO SEE NATIONS ENEMIES ALLIES ETC LIKE EUIV

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

### B8. Send Ultimatum — Conversational Flow (PL-14)

```
cheat give_dp 5
send ultimatum to Austria
```

**Expected:**
- Talleyrand presents ultimatum terms in conversational dialogue (NOT instant execution)
- Shows auto-generated demands (gold, territory if adjacent, manpower if troop advantage)
- Shows acceptance estimate with military threat bonus
- Shows diplomatic cost preview: relation penalty, splash damage, threat increase
- Options: [Deliver Ultimatum] [Customize Demands] [Reconsider]
- Delivering costs 2 DP
- If accepted: demands applied immediately, no diplomatic state change, +20 threat total
- If rejected: casus belli granted, -15 total relation, +15 threat
- 5-turn global cooldown applied (blocks ALL nations, not per-target)

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
| Z: Session 5 Balance | 6 | Bombardment, defense, supply, AP warning | MEDIUM |
| Z2: Cavalry Momentum | 4 | Momentum bonus, infantry exhaustion, artillery exempt | MEDIUM |
| Z3: Ultimatum Flow (PL-14) | 6 | Conversational preview, splash, escalation, cooldown | HIGH |
| Z4: Demand Wizard (PL-15) | 8 | Gold/territory/manpower wizard, confirm, guards | HIGH |
| Z5: Dynamic Penalty (PL-19) | 7 | Scaling relation/splash/rejection/threat penalties | HIGH |
| Z6: Territory Scaling (PL-20) | 9 | Escalating cost, income weight, elimination guards | HIGH |
| Z7: Typed Manpower (PL-18) | 6 | Infantry/cavalry/artillery demands, pool caps | MEDIUM |
| Z8: Harshness Fix (PL-12) | 2 | Harsher decreases acceptance, generous increases | HIGH |
| Z9: Snapshot Fix (PL-13) | 2 | Surpassed false-reject prevention, result popup | HIGH |
| Z10: Tolerance Band (PL-9) | 2 | Borderline warning, marginal drop tolerance | MEDIUM |
| Z11: Type Preserve (PL-10) | 1 | Generous doesn't downgrade proposal type | MEDIUM |
| Z12: Proposal Feedback (PL-5) | 3 | Result popup, AI dedup, cooldown both sides | HIGH |
| Z13: Counter-Offer UX (PL-8) | 1 | Visual distinction for counter-offers | LOW |
| Z14: Type-Aware Harsh (PL-6) | 2 | Friendship no territory, war allows territory | MEDIUM |
| **TOTAL** | **163** | | |

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

**Recommendation:** Use Godot for integration/UX verification. Use pytest for numerical precision. The 8,000+ backend tests already cover formula correctness — the playtest covers "does the player actually see the right thing."

---

## SECTION Z: Bug Fix Session 5 — Playtest Verification (Apr 6, 2026)

Items from Session 5 that need manual playtest confirmation. Automated tests cover logic; these verify player-facing UX.

### Z1. m3: Bombardment Morale Floor
**Goal:** Confirm bombardment cannot collapse an army below 25% morale.
```
/debug set_location Drouot Belgium
/debug set_location Wellington Belgium
cheat set_diplo_state Britain WAR
/debug set_strength Wellington 25000
# Bombard repeatedly
Drouot, bombard Wellington
end turn
Drouot, bombard Wellington
Drouot, bombard Wellington
end turn
# Repeat until Wellington's morale is low
```
**Verify:** Wellington's morale never drops below 25%. Status should show morale pinned at 25, not 0 or negative. If Wellington has square formation, verify the -18 penalty still floors at 25.

**Edge case:** At exactly 25% morale, does combat (not bombardment) trigger forced retreat? It should — `<= 25` is the retreat check. Bombardment pins at 25, combat pushes past.

### Z2. PT-3: Emoji Replacement Renders Correctly
**Goal:** Verify text markers render cleanly in Godot terminal.
```
# Trigger cavalry warnings
/debug set_location Ney Belgium
/debug set_stance Ney defensive
# Wait 3 turns for cavalry stance warning
end turn
end turn
end turn
```
**Verify:** Messages show `[Cavalry]`, `[!]`, `[Combat]` etc. instead of garbled characters or boxes. No surrogate pair errors in Godot console.

Also check:
- Attack a broken army → should show `[BROKEN]` not `💀`
- Trigger glorious charge → should show `[Cavalry][Combat] GLORIOUS CHARGE!`
- Forced retreat message → should show `[!]` not `⚠️`

### Z3. B1: Wellington Defense Stack Reduced
**Goal:** Confirm Wellington is no longer nearly invincible.
```
cheat set_diplo_state Britain WAR
/debug set_location Ney Belgium
/debug set_location Wellington Belgium
/debug set_strength Ney 40000
/debug set_strength Wellington 20000
# Let Wellington fortify
end turn
end turn
end turn
# Attack with 2:1 advantage
Ney, attack Wellington
```
**Verify:** With 2:1 numbers, Ney should deal meaningful casualties. Wellington's defense should not exceed ~50-60% total modifier (was 75-85% before). Fortification should cap at 12% for cautious personality (was 20%).

### Z4. B2: Supply Attrition Reduced
**Goal:** Confirm Belgium staging no longer destroys armies.
```
/debug set_location Ney Belgium
/debug set_location Davout Belgium
/debug set_strength Ney 30000
/debug set_strength Davout 30000
end turn
```
**Verify:** With 60k troops in a town (cap now 35k), attrition should be modest (~1-2% per marshal, not 4k+ per turn). Home territory bonus (1.5x) makes French Belgium even more sustainable.

### Z5. PT-6: AP Warning on End Turn
**Goal:** Confirm warning appears when ending turn with actions remaining.
```
# Fresh turn (4 AP)
end turn
```
**Verify:** Message should include "(Warning: 4 action(s) unused)" before "Turn X begins!"

```
# Use all AP then end turn
Ney, scout Belgium
Davout, scout Lyon
Ney, scout Belgium
Davout, scout Lyon
end turn
```
**Verify:** No warning in message (0 AP remaining).

### Z6. m1: "trust" Without Dialogue
**Goal:** Confirm typing "trust" alone gives clear feedback.
```
trust
```
**Verify:** Returns Berthier message about no pending diplomatic matter. Does NOT show a parse error or "Unknown action".

---

## SECTION Z2: Cavalry Momentum (B5 Balance)

### Z2-1. Cavalry Gets Momentum Bonus on Repeated Attacks
**Goal:** Verify cavalry gains attack bonus from repeated attacks instead of exhaustion penalty.
```
/debug set_location Ney Belgium
/debug set_strength Ney 20000
/debug freeze_enemies
# Attack an enemy twice in one turn
Ney, attack [enemy in adjacent region]
Ney, attack [same enemy]
```
**Verify:** Second attack message includes "cavalry builds momentum! (2nd charge: +5%)". Damage should be slightly HIGHER on second attack, not lower. No exhaustion penalty shown.

### Z2-2. Cavalry Momentum Cap at +10%
**Goal:** Verify momentum caps at +10% on 3rd+ attacks.
```
# Attack 3+ times in one turn (needs enough AP)
Ney, attack [enemy]
Ney, attack [enemy]
Ney, attack [enemy]
```
**Verify:** Third attack shows "+10%" momentum. Fourth+ attack also shows "+10%" (cap, not increasing).

### Z2-3. Infantry Still Gets Exhaustion
**Goal:** Verify infantry marshals still suffer exhaustion penalties (unchanged).
```
Davout, attack [enemy]
Davout, attack [enemy]
```
**Verify:** Second attack shows "exhausted from repeated attacks! (2nd attack: -10%)". Damage is LOWER on second attack.

### Z2-4. Artillery Still Exempt
**Goal:** Verify artillery shows neither exhaustion nor momentum.
```
Drouot, bombard [enemy]
Drouot, bombard [enemy]
```
**Verify:** No exhaustion or momentum message on second bombardment. Damage unchanged.

---

## SECTION Z3: Ultimatum Conversational Flow — PL-14 (Session 12, Apr 7)

Ultimatums now route through conversational diplomacy with preview, acceptance estimate, and splash damage. Automated tests cover formula correctness; these verify player-facing UX.

### Z3-1. Ultimatum Shows Preview Before Delivery
**Goal:** Confirm ultimatum is NOT instant — player sees terms, acceptance, and consequences before committing.
```
cheat give_dp 5
send ultimatum to Austria
```
**Verify:** Talleyrand presents dialogue with: (1) auto-generated demands listed (gold amount, territory if applicable), (2) acceptance estimate %, (3) relation penalty preview, (4) splash damage to bystanders listed by nation, (5) threat increase preview. Options: [Deliver Ultimatum] [Customize Demands] [Reconsider]. Clicking [Reconsider] cancels without spending DP.

### Z3-2. Ultimatum Delivery — Accepted
**Goal:** Confirm accepted ultimatum transfers resources with no state change.
```
cheat give_dp 5
cheat set_relation Austria 40
send ultimatum to Austria
# Choose "Deliver Ultimatum"
```
**Verify:** If accepted: (1) gold transferred (check via strategic ledger K tab), (2) diplomatic state unchanged (still PEACE, not upgraded or downgraded), (3) relation dropped by dynamic penalty amount, (4) threat increased (+15 delivery +5 acceptance = +20 minimum), (5) 5-turn global cooldown shown.

### Z3-3. Ultimatum Delivery — Rejected
**Goal:** Confirm rejection grants casus belli and applies penalties.
```
cheat set_relation Austria -50
cheat give_dp 5
send ultimatum to Austria
# Choose "Deliver Ultimatum"
```
**Verify:** (1) Rejection message shown, (2) casus belli granted — check via F1 wizard (war declaration should show 0 DP), (3) additional relation hit applied (-5 base, more for harsh demands), (4) threat still increased (+15), (5) cooldown applied.

### Z3-4. Ultimatum Splash Damage Preview
**Goal:** Verify splash damage to bystanders is shown and applied.
```
cheat set_diplo_state Austria ALLIANCE
cheat set_diplo_state Prussia OPEN_BORDERS
cheat give_dp 5
send ultimatum to Saxony
# Check splash preview before delivering
```
**Verify:** Preview shows splash damage: nations with treaties toward Saxony (Austria as ALLIANCE: higher penalty, Prussia as OPEN_BORDERS: lower penalty). After delivery, check diplomatic ledger — Austria and Prussia relations with France should have dropped.

### Z3-5. Ultimatum Escalation Cap
**Goal:** Verify "Harsher Demands" is capped at 2 rounds.
```
cheat give_dp 5
send ultimatum to Austria
# Click "Customize Demands" or "Harsher Demands" 3 times
```
**Verify:** After 2 escalation rounds, further escalation blocked with message "Cannot escalate further, Sire." Acceptance should decrease with each escalation round.

### Z3-6. Ultimatum Global Cooldown
**Goal:** Verify cooldown blocks ALL nations, not just the target.
```
cheat give_dp 10
send ultimatum to Austria
# Deliver ultimatum
send ultimatum to Prussia
```
**Verify:** Second ultimatum blocked with message showing turns remaining (e.g., "Next ultimatum available in 5 turns").

---

## SECTION Z4: Ultimatum Demand Wizard — PL-15 (Session A, Apr 8)

Full demand wizard replacing blind escalation. Player picks gold → territory → manpower → confirm. Same UX pattern as armistice terms_guidance wizard.

### Z4-1. Wizard Entry — Customize Demands
**Goal:** Confirm wizard opens when player chooses to customize.
```
cheat give_dp 5
send ultimatum to Austria
# Choose "Customize Demands"
```
**Verify:** Wizard starts at gold step. Shows: "How much gold should we demand, Sire?" with options [Demand X gold] [More] [Less] [Skip gold]. Gold type shown: "per turn" if target has income, "one-time tribute" if income is 0.

### Z4-2. Gold Step — More/Less/Skip
**Goal:** Verify gold adjustments work.
```
# In wizard gold step:
# Click "More" — gold increases (1.5×)
# Click "Less" — gold decreases (0.7×)
# Click "Skip" — no gold demand, advance to territory
```
**Verify:** Gold amount changes with each click. Floor is 25. Cap is 300/turn or 500 lump. After choosing, wizard advances to territory step (if eligible) or manpower step.

### Z4-3. Territory Step — Region Picker
**Goal:** Verify territory picker shows eligible regions with ranking.
```
# Setup: France controls Belgium (adjacent to Austrian territory)
cheat give_dp 5
/debug set_strength Ney 40000
send ultimatum to Austria
# Customize → skip gold → territory step
```
**Verify:** Territory step only appears if France has military superiority (>1.2×). Shows "Shall we demand territory?" with [Yes] [No]. If Yes: lists target regions adjacent to France-controlled territory, ranked by strategic value. Player picks region-by-region: [Demand this region] [Not this one] [Enough territory].

### Z4-4. Territory — Elimination Guard
**Goal:** Verify wizard won't auto-suggest demands that would eliminate a nation.
```
cheat give_dp 5
send ultimatum to Saxony
# Saxony has 2 regions — wizard should not suggest both
```
**Verify:** Auto-generated terms skip territory for nations with ≤2 regions. If player reaches territory step via customize, regions that would leave target with ≤1 region should be filtered out or warned about.

### Z4-5. Manpower Step — Typed Demands (PL-18)
**Goal:** Verify manpower wizard shows unit type selection.
```
# In wizard manpower step:
```
**Verify:** Shows target's available pools: "Infantry: X | Cavalry: Y | Artillery: Z". Types with <300 pool are hidden. Player picks type → amount with [More] [Less] [Skip]. Multiple types can be demanded (e.g., infantry + cavalry). After manpower, proceeds to confirm step.

### Z4-6. Confirm Step — Full Preview
**Goal:** Verify confirm step shows all demands with acceptance and diplomatic cost.
```
# After completing gold/territory/manpower steps:
```
**Verify:** Confirm step displays: (1) all chosen demands listed, (2) acceptance estimate %, (3) diplomatic cost with severity label (mild/moderate/severe/extreme), (4) splash damage preview, (5) threat increase preview, (6) Talleyrand territory warning if applicable. Options: [Deliver Ultimatum] [Start Over] [Reconsider].

### Z4-7. Empty Demands — Floor Enforced
**Goal:** Verify player can't send an empty ultimatum.
```
# Skip gold, skip territory, skip manpower
```
**Verify:** If all demands skipped, a minimum symbolic tribute is injected (100 gold lump). Talleyrand says "We must demand something, Sire — at minimum a symbolic tribute."

### Z4-8. Use Suggested Terms — Bypass Wizard
**Goal:** Verify "Use Suggested Terms" skips the wizard entirely.
```
cheat give_dp 5
send ultimatum to Austria
# Choose "Use Suggested Terms"
```
**Verify:** Skips gold/territory/manpower steps. Goes straight to delivery with auto-generated demands. Shows acceptance estimate. Same result as PL-14 original flow but with visible terms.

---

## SECTION Z5: Dynamic Relation Penalty — PL-19 (Session B, Apr 8)

Ultimatum delivery penalty now scales -10 to -60 based on demand severity. Territory is income-weighted. Splash damage scales with penalty severity.

### Z5-1. Gold-Only Demand — Mild Penalty
**Goal:** Confirm small demands produce small penalties.
```
cheat give_dp 5
cheat set_relation Austria 30
send ultimatum to Austria
# Customize: demand 100 gold/turn, skip territory, skip manpower
# Deliver
```
**Verify:** Relation hit to Austria is approximately -15 (base -10 + gold penalty). Diplomatic cost label shows "mild." Check diplomatic ledger for new relation value.

### Z5-2. Territory Demand — Income-Weighted
**Goal:** Confirm territory penalty scales with region income.
```
# Demand a rural region (income ~50) vs a city (income ~150)
# Compare relation hits
```
**Verify:** Rural region causes less relation damage than city. Capital region costs ×2 on top of income weight. E.g., demanding Vienna (capital, high income) should cause much larger penalty than demanding a border town.

### Z5-3. Multi-Demand Stacking
**Goal:** Verify penalties stack from gold + territory + manpower.
```
cheat give_dp 5
send ultimatum to Austria
# Customize: demand gold + 2 territories + manpower
# Check diplomatic cost preview before delivering
```
**Verify:** Diplomatic cost preview shows a "severe" or "extreme" label. After delivery, relation drops significantly (closer to -40 to -60 range). Compare against gold-only demand (Z5-1) — should be much worse.

### Z5-4. Splash Damage Scales with Severity
**Goal:** Confirm bystander splash multiplied by penalty severity.
```
cheat set_diplo_state Prussia ALLIANCE
cheat set_relation Prussia 40
cheat give_dp 5
send ultimatum to Austria
# Demand heavy terms (territory + gold + manpower) — high severity
# Deliver
```
**Verify:** Prussia (allied with Austria) takes a larger splash hit than with mild demands. Splash multiplier ranges 1.0× (mild) to 2.5× (extreme). Check Prussia's relation change in diplomatic ledger.

### Z5-5. Rejection Penalty Scales
**Goal:** Verify rejection penalty scales from -5 to -15 based on demand severity.
```
cheat set_relation Austria -50
cheat give_dp 5
send ultimatum to Austria
# Heavy demands → deliver → rejected
```
**Verify:** Rejection relation hit is more than flat -5 for heavy demands. Total relation change (delivery + rejection) should be significant.

### Z5-6. Penalty Floor and Cap
**Goal:** Verify penalty range is -10 to -60.
```
# Test floor: send ultimatum with minimal demands (100 gold only)
# Test cap: send ultimatum with max demands (territory + gold + manpower)
```
**Verify:** Minimum penalty is -10 (base alone). Maximum is capped at -60 regardless of how many demands. Check via diplomatic ledger relation values.

### Z5-7. Dynamic Threat Scaling
**Goal:** Confirm delivery threat scales with demand severity.
```
cheat set_threat 10
cheat give_dp 5
send ultimatum to Austria
# Light demands → deliver
# Check threat
Press D → Threat tab
```
**Verify:** Light demands add ~10-15 threat. Heavy demands add ~25-30 threat. Territory demands add additional per-region threat (+8 each) plus count-based bonus (+5 for 2-3 regions, +12 for 4+, +18 for rump, +25 for annex attempt).

---

## SECTION Z6: EU4-Style Territory Cost Scaling — PL-20 (Session B, Apr 8)

Escalating per-region acceptance cost (-5, -8, -11, -14...) plus income weighting and elimination guards. Applies to ALL proposal types (ultimatums + peace treaties).

### Z6-1. First Region — Baseline Cost
**Goal:** Confirm single region demand has reasonable acceptance penalty.
```
cheat give_dp 5
cheat set_relation Austria 40
send ultimatum to Austria
# Customize: demand 1 border region, skip gold/manpower
# Note acceptance estimate
```
**Verify:** Single region demand reduces acceptance by roughly -5 to -10 depending on region income. Rural regions (income ~50) cost less than cities (income ~150).

### Z6-2. Escalating Cost — 2nd+ Region
**Goal:** Verify each additional region costs more than the last.
```
# Demand 1 region → note acceptance
# Start over → demand 2 regions → note acceptance
# Start over → demand 3 regions → note acceptance
```
**Verify:** Acceptance drops faster with each additional region. Not a flat -5 per region. Pattern should be roughly: -5 first, -8 second, -11 third, -14 fourth (base escalation before income weighting).

### Z6-3. Capital Region — Double Cost
**Goal:** Confirm capital regions cost ×2.
```
# Compare: demand a non-capital region vs demand the capital region (same target)
```
**Verify:** Demanding a capital causes roughly double the acceptance penalty compared to a similarly-valued non-capital region. The capital penalty stacks with income weight — a high-income capital is extremely expensive.

### Z6-4. Full Annexation Blocked — Acceptance Guard
**Goal:** Verify full annexation is near-impossible diplomatically.
```
cheat give_dp 5
send ultimatum to Saxony
# Try to demand ALL of Saxony's territory (2 regions)
```
**Verify:** Acceptance estimate shows very low % (near 0%). The -60 elimination guard makes full annexation via diplomacy practically impossible. Talleyrand warning text appears about erasing them from the map.

### Z6-5. Rump State — Heavy Penalty
**Goal:** Verify demanding all but 1 region triggers rump state penalty.
```
cheat give_dp 5
send ultimatum to Austria
# Demand 3 of 4 regions (leaving only capital)
```
**Verify:** Acceptance drops significantly due to -30 rump state guard. Talleyrand warning about reducing them to their capital. Much harder than demanding 2 of 4 regions.

### Z6-6. Application Guard — Cannot Eliminate via Demands
**Goal:** Verify `_apply_ultimatum_demands` refuses transfers that would eliminate a nation.
```
# This is a safety net — even if acceptance somehow passes, the application blocks elimination
# Test via backend: pytest tests covering this guard
```
**Verify:** Backend test confirms: if target has 1 region and territory demand exists, transfer is refused. This is a safety net on top of the acceptance penalty.

### Z6-7. Auto-Generation Skips Elimination Demands
**Goal:** Verify auto-generated ultimatum terms don't propose elimination-level territory.
```
cheat give_dp 5
send ultimatum to Saxony
# Check auto-generated terms (Use Suggested)
```
**Verify:** For Saxony (2 regions), auto-generated terms should NOT include territory demands. Gold and/or manpower only. For larger nations, territory is offered but never enough to reduce to ≤1 region.

### Z6-8. Treaty Cession Guard — War Score < 90
**Goal:** Verify peace treaties block elimination at low war scores.
```
# After a war with moderate war score (~50-70):
cheat set_diplo_state Austria WAR
# Win some battles to get war score
# Propose peace with territory demands that would eliminate
```
**Verify:** Treaty ratification blocks territory cessions that would eliminate a nation if war_score < 90. Territory clauses stripped, other clauses (gold, AP) still apply.

### Z6-9. Wizard Territory Warning — Count-Based
**Goal:** Verify Talleyrand shows appropriate warnings based on demand count.
```
# In ultimatum wizard, demand varying numbers of regions:
# 2-3 regions → "substantial territorial demand"
# 4+ regions → "extraordinary claim" warning
# All-but-1 → "reducing them to their capital" warning
# All regions → "erase them from the map" warning
```
**Verify:** Warning text matches demand severity. Warnings appear in the confirm step before delivery.

---

## SECTION Z7: Typed Manpower Demands — PL-18 (Session A, Apr 8)

Manpower demands now specify unit type (infantry/cavalry/artillery) with different acceptance costs. Scarcity pricing: artillery > cavalry > infantry.

### Z7-1. Manpower Type Selection in Wizard
**Goal:** Verify wizard shows typed manpower pools.
```
cheat give_dp 5
send ultimatum to Austria
# Customize → skip gold → skip territory → manpower step
```
**Verify:** Shows Austria's available pools: "Infantry: X | Cavalry: Y | Artillery: Z". Types with pool < 300 are hidden. Player picks type first, then amount.

### Z7-2. Typed Transfer — Infantry
**Goal:** Confirm infantry manpower transfers from correct pool.
```
# Demand 2000 infantry from Austria → deliver → accepted
# Check strategic ledger manpower section
```
**Verify:** France gains 2000 infantry. Austria loses 2000 infantry. Cavalry and artillery pools unchanged.

### Z7-3. Typed Transfer — Cavalry (Higher Cost)
**Goal:** Confirm cavalry demands cost more acceptance than infantry.
```
# Compare: demand 2000 infantry vs 2000 cavalry (same target, same amount)
# Note acceptance estimates for each
```
**Verify:** 2000 cavalry demand reduces acceptance more than 2000 infantry demand. Cavalry is scarcer → higher penalty.

### Z7-4. Typed Transfer — Artillery (Highest Cost)
**Goal:** Confirm artillery demands cost the most.
```
# Compare: demand 2000 artillery vs 2000 cavalry vs 2000 infantry
```
**Verify:** Artillery demand reduces acceptance the most. Order: artillery > cavalry > infantry for same amount.

### Z7-5. Multiple Types — Stacking
**Goal:** Verify demanding multiple manpower types stacks correctly.
```
# Demand 1000 infantry + 500 cavalry + 300 artillery
```
**Verify:** All three types demanded. Acceptance reflects combined penalty. Each type transferred from correct pool on acceptance.

### Z7-6. Pool Cap — Can't Demand More Than Target Has
**Goal:** Verify demands are capped at target's actual pool size.
```
# Demand manpower for a type where target has very few (e.g., 200 artillery)
```
**Verify:** Transfer capped at target's actual pool. Can't demand 5000 artillery if target only has 200.

---

## SECTION Z8: Harshness + Acceptance Formula — PL-12 (Session 11, Apr 7)

Harshness penalty now feeds into acceptance. Harsher terms decrease acceptance (was inverted before).

### Z8-1. Harsher Terms Decrease Acceptance
**Goal:** Confirm clicking "Even Harsher" reduces acceptance, not increases.
```
cheat give_dp 5
cheat set_relation Saxony 40
propose non-aggression with Saxony
# Note acceptance estimate
# Click "Even Harsher"
# Note new acceptance estimate
```
**Verify:** Acceptance goes DOWN after clicking "Even Harsher." This was the core PL-12 bug — it used to go UP.

### Z8-2. Generous Terms Increase Acceptance
**Goal:** Confirm "More Generous" still increases acceptance.
```
cheat give_dp 5
propose alliance with Austria
# Note acceptance
# Click "More Generous"
```
**Verify:** Acceptance goes UP after clicking "More Generous." This is the expected inverse of Z8-1.

---

## SECTION Z9: Acceptance Snapshot + Surpassed Fix — PL-13 (Session 11, Apr 7)

Proposals now snapshot diplomatic state at send time. Surpassed check uses snapshot, preventing false rejections.

### Z9-1. High-Acceptance Proposal Not Falsely Rejected
**Goal:** Confirm proposals with good odds don't fail as "surpassed."
```
cheat set_diplo_state Saxony OPEN_BORDERS
cheat set_relation Saxony 50
cheat give_dp 10
propose non-aggression with Saxony
proceed
end turn
```
**Verify:** Proposal resolves based on actual acceptance formula, NOT rejected as "surpassed." Proposal result popup shows the real outcome (accept/reject based on score, not false "situation changed").

### Z9-2. Proposal Result Popup Shows Outcome
**Goal:** Confirm proposal results appear as popup, not just buried in dispatch.
```
cheat give_dp 5
propose non-aggression with Austria
proceed
end turn
```
**Verify:** Proposal Result Popup appears showing: target nation, proposal type, outcome (ACCEPT/REJECT), explanation text. [Continue] button dismisses. Result also appears in morning dispatch (both is correct — different purposes).

---

## SECTION Z10: Acceptance Mismatch Tolerance — PL-9 (Session 10, Apr 6)

Acceptance snapshot with tolerance band prevents marginal rejections.

### Z10-1. Borderline Proposal Shows Warning
**Goal:** Confirm Talleyrand warns about borderline proposals (50-75% range).
```
# Set up a scenario where acceptance is ~60-70%
cheat set_relation Saxony 30
cheat give_dp 5
propose non-aggression with Saxony
```
**Verify:** Talleyrand's assessment includes a warning about changing conditions: something like "Much may change during my journey." This sets expectations that the % is a snapshot.

### Z10-2. Marginal Drop Doesn't Cause Rejection
**Goal:** Confirm small score changes during transit don't reject the proposal.
```
# Send proposal at ~65% acceptance
# End turn (conditions may shift slightly)
```
**Verify:** Proposal still resolves as ACCEPT unless score dropped by more than 15 points from the snapshot. A 65% proposal that drops to 55% should still succeed (within tolerance band).

---

## SECTION Z11: Proposal Type Preservation — PL-10 (Session 10, Apr 6)

"More Generous" no longer downgrades proposal type below current relationship.

### Z11-1. Generous Alliance Stays Alliance
**Goal:** Confirm "More Generous" on alliance proposal doesn't downgrade to peace treaty.
```
cheat set_diplo_state Saxony OPEN_BORDERS
cheat set_relation Saxony 40
cheat give_dp 10
propose alliance with Saxony
# Click "More Generous"
```
**Verify:** Proposal type remains "Alliance" after clicking generous. Does NOT downgrade to "Peace Treaty" or "Non-Aggression." Sweeteners are added (gold, protection) while keeping the alliance proposal type.

---

## SECTION Z12: Proposal Feedback + Race Condition — PL-5 (Sessions 7-8, Apr 6)

Proposal results now show as popup. AI dedup prevents race conditions.

### Z12-1. Proposal Result Popup
**Goal:** Confirm result is shown as a modal popup, not just in dispatch.
```
cheat give_dp 5
propose non-aggression with Austria
proceed
end turn
```
**Verify:** **Proposal Result Popup** appears with outcome (ACCEPT/REJECT). Shows target nation, proposal type, result. [Continue] button. Not just text in morning dispatch.

### Z12-2. AI Doesn't Race Player Proposal
**Goal:** Confirm AI doesn't propose same type while player proposal is in transit.
```
# Send proposal to a nation the AI is likely to approach
cheat give_dp 5
propose non-aggression with Saxony
proceed
end turn
```
**Verify:** AI does NOT generate a competing proposal to Saxony while player's is in transit. No confusing double-proposal. After resolution, AI may propose in subsequent turns (after cooldown).

### Z12-3. Rejection Cooldown Blocks Both Sides
**Goal:** Confirm rejection sets cooldowns for both player and AI.
```
# Send proposal → rejected
# Try same proposal immediately (player blocked)
# End turn (AI also blocked)
```
**Verify:** Player cannot re-propose within cooldown. AI also does not re-propose same type within cooldown period.

---

## SECTION Z13: Counter-Offer UX — PL-8 (Session 9, Apr 6)

Counter-offers visually differentiated from initial proposals.

### Z13-1. Counter-Offer Visual Distinction
**Goal:** Verify counter-offer popup looks different from initial proposals.
```
# Set up borderline acceptance (score 30-49 for counter-offer)
cheat set_relation Prussia -10
cheat give_dp 5
propose armistice with Prussia
proceed
end turn
```
**Verify:** If AI counters: popup shows distinct "COUNTER-OFFER" header (blue, not default), context line ("In response to your X proposal..."), steel-blue border. Buttons adapted for counter context.

---

## SECTION Z14: Harsher Terms Type-Aware — PL-6 (Session 7, Apr 6)

"Harsher" terms now respect proposal type. Friendship proposals can't demand territory.

### Z14-1. Friendship Proposal — No Territory Demands
**Goal:** Confirm harsher terms on non-aggression don't add territory.
```
cheat give_dp 5
cheat set_relation Saxony 30
propose non-aggression with Saxony
# Click "Even Harsher"
```
**Verify:** Harsher terms add modest gold demand (100g). Does NOT add territory_cede. Second "Even Harsher" click blocked with message about friendship proposal limits.

### Z14-2. War Resolution — Territory Allowed
**Goal:** Confirm peace/armistice proposals CAN add territory on harsher terms.
```
cheat set_diplo_state Britain WAR
cheat give_dp 5
propose armistice with Britain
# Click "Even Harsher"
```
**Verify:** Harsher terms add gold (round 1) then territory (round 2). Both rounds available. Territory makes thematic sense for war reparations.
