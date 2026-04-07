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
```

---

## SECTION A: Diplomacy Button / Wizard (F1)

### A1. Wizard Opens — Nation Selection
Press F1 (or click [Diplomacy] button)
**Expected:** Wizard overlay opens (CanvasLayer 110, modal). Shows categorized nation list: "At War" (Britain, Prussia), "Treaties" (Saxony under OPEN_BORDERS), "Neutral" (Austria at PEACE). Each button shows nation name + current diplomatic state. Input blocked behind wizard.

### A2. Wizard Step 2 — Action Preview
Click on "Austria" in the wizard
**Expected:** Step 2 loads with Talleyrand's Assessment panel at top. Shows: Current state (PEACE), Relation score + descriptor, 1-2 sentence assessment. Bottom: Action buttons with DP costs and likelihood words. Buttons colored by likelihood. Unavailable actions shown disabled with reason text. [Back] button returns to nation list.

### A3. Wizard → Conversational Diplomacy Flow
cheat give_dp 10 → Press F1 → Select Austria → Click "Propose Non-Aggression (1 DP)"
**Expected:** Wizard closes. Terminal shows command. Talleyrand responds with conversational dialogue (NOT instant execution). Shows assessment text + options. Player must type response to proceed.

### A4. Wizard — War Declaration
Press F1 → Select Austria → Click "Declare War"
**Expected:** Terminal shows command. Talleyrand may object. If no objection: War declared, relation drops, threat increases.

### A5. Wizard — Vassal Actions
cheat set_diplo_state Saxony VASSAL → Press F1 → Select Saxony
**Expected:** Step 2 shows vassal-specific info: loyalty %, autonomy level, tribute income. Action buttons include: Invest, Increase Autonomy, Decrease Autonomy, Release Vassal.

### A6. Wizard — Back and Cancel
Press F1 → Select nation → Press [Back] → Press [Cancel]
**Expected:** [Back] returns to Step 1. [Cancel] closes wizard. Input re-enabled. No DP spent.

### A7. Wizard — Empty/Edge States
cheat give_dp 0 → Press F1 → Select Austria → Try any action
**Expected:** Actions requiring DP show as disabled with "Insufficient DP" reason.

### A8. Wizard — open_for_nation() Handoff
cheat set_diplo_state Britain WAR → Click Britain war card in war panel → Click [Negotiate Peace]
**Expected:** Diplomacy wizard opens directly at Step 2 for Britain (skips nation selection).

---

## SECTION B: Diplomatic Proposals (Terminal Commands)

### B1. Propose Peace (From WAR)
cheat give_dp 5 → propose armistice with Britain
**Expected:** Talleyrand dialogue with assessment. Options to send/modify/dismiss. Type "proceed" → proposal sent. Result: ACCEPT, COUNTER, or REJECT.

### B2. Propose Alliance Upgrade (Sequential)
cheat set_relation Austria 50, cheat give_dp 10 → propose alliance with Austria
**Expected:** Shows total DP cost for jump transition. Talleyrand assesses feasibility.

### B3. Counter-Offer Flow
cheat set_relation Prussia -20, cheat give_dp 5 → propose armistice with Prussia → proceed
**Expected:** AI generates counter-proposal. Player options: Accept counter / Reject / Modify further.

### B4. Rejection + Cooldown
cheat set_relation Britain -80 → propose peace with Britain → proceed
**Expected:** Proposal rejected. Cooldown message. Same proposal type blocked within cooldown.

### B5. Proposal with Talleyrand Objection
cheat set_relation Austria -50 → declare war on Austria
**Expected:** Talleyrand STRONG objection fires. Options shown. Defiance risk warning if proceed.

### B6. Break Treaty
cheat set_diplo_state Austria NON_AGGRESSION → break treaty with Austria
**Expected:** Confirmation. Treaty terminated, relation drops, threat increases, authority -10, reliability -20.

### B7. Downgrade Relations
cheat set_diplo_state Austria ALLIANCE, cheat set_relation Austria 60 → downgrade relations with Austria
**Expected:** Steps down one level: ALLIANCE → DEFENSIVE_ALLIANCE. Relation penalty applied.

### B8. Send Ultimatum
cheat give_dp 5 → send ultimatum to Austria
**Expected:** 2 DP cost. Coercive demand. If rejected: casus belli granted.

### B9. Casus Belli — Reduced War Cost
After B8 ultimatum rejected → declare war on Austria
**Expected:** War costs 0 DP, relation penalty halved, threat penalty halved. Casus belli consumed.

---

## SECTION C: AI Proposals (Incoming)

### C1. AI Proposes During End Turn
cheat queue_ai_proposal Britain ARMISTICE → end turn
**Expected:** Incoming Proposal Popup (CanvasLayer 112). Shows proposal type, terms, AI nation. Three buttons: [Accept] [Counter] [Reject]. Game paused.

### C2. Accept AI Proposal
Click [Accept]
**Expected:** Treaty executed. Diplomatic state updated. Popup closes.

### C3. Counter AI Proposal
Click [Counter]
**Expected:** Counter-offer dialogue in terminal. AI evaluates counter.

### C4. Reject AI Proposal
Click [Reject]
**Expected:** Proposal rejected. Cooldown applied (3 turns). Popup closes.

### C5. AI Proposal Anti-Spam
Reject → end turn (x3)
**Expected:** Same AI nation doesn't re-propose within cooldown. Max 1 proposal per turn.

### C6. Multiple AI Proposals Queued
cheat queue_ai_proposal Britain ARMISTICE, cheat queue_ai_proposal Prussia NON_AGGRESSION → end turn
**Expected:** Only 1 proposal per turn. Remaining queued for subsequent turns.

---

## SECTION D: Coalition System

### D1. Threat Accumulation Display
Press D → Threat/Coalition tab
**Expected:** Shows current threat level + tier name. Lists qualifying coalition members.

### D2. Threat Increases from Actions
cheat set_threat 25 → declare war on Austria → Press D → Threat tab
**Expected:** Threat increased by +20. New tier shown.

### D3. Coalition Brewing (3-Turn Countdown)
cheat set_threat 62 → end turn
**Expected:** Persistent notification: "A coalition is brewing." Dispatch alert. Diplomatic ledger shows countdown.

### D4. Coalition Brewing Countdown
end turn (x2 more)
**Expected:** Notification updates each turn. If relations improve with all members: brewing cancels.

### D5. Coalition Declaration
end turn (countdown hits 0)
**Expected:** Coalition Declaration Popup. Shows members, leader, posture. [Continue] button. All members enter WAR with France.

### D6. Coalition Defusal During Brewing
cheat set_threat 62, end turn → cheat set_relation Britain/Prussia/Austria 0 → end turn
**Expected:** If no qualifying nations: brewing cancels.

### D7. Coalition Momentum Rule
cheat set_threat 62, end turn → cheat set_threat 55 → end turn
**Expected:** Brewing CONTINUES (momentum: only cancels at <40).

### D8. Instant Coalition (Threat 80+)
cheat set_threat 82 → end turn
**Expected:** Coalition forms IMMEDIATELY (no countdown).

### D9. Coalition Dissolution
With active coalition → cheat set_threat 15 → end turn
**Expected:** If threat < 20: coalition dissolves. 5-turn cooldown.

### D10. British Subsidy (During Coalition)
With active coalition including Britain → end turn
**Expected:** Britain sends 200g/turn to lowest-relation coalition partner.

---

## SECTION E: Vassal System

### E1. Create Vassal (Treaty Path)
cheat set_diplo_state Saxony OPEN_BORDERS, cheat set_relation Saxony 40, cheat give_dp 5 → propose vassalage to Saxony → proceed
**Expected:** Saxony becomes VASSAL. Loyalty 60+. Autonomy SATELLITE. Marshals transferred.

### E2. Vassal in Diplomatic Ledger
Press D → Nations tab
**Expected:** Saxony shows as "VASSAL" with loyalty %, autonomy, tribute.

### E3. Vassal Loyalty Degradation
decrease autonomy Saxony → end turn (x5)
**Expected:** Loyalty decreases each turn. Dispatch warns at <40 and <10.

### E4. Vassal Investment
cheat give_dp 3 → invest in Saxony
**Expected:** 1 DP + 200 gold. Loyalty +15, Relations +5.

### E5. Vassal Autonomy Changes
increase/decrease autonomy Saxony
**Expected:** Autonomy changes: PUPPET ↔ SATELLITE ↔ AUTONOMOUS.

### E6. Vassal Rebellion Warning Popup
cheat set_vassal_loyalty Saxony 8 → end turn
**Expected:** Vassal Rebellion Popup. [Invest][Send Garrison][Accept Risk].

### E7. Vassal Rebellion
cheat set_vassal_loyalty Saxony 0 → end turn
**Expected:** Vassal rebels: VASSAL → WAR. Marshals transferred back. Other vassals: -10 loyalty.

### E8. Release Vassal
release Saxony
**Expected:** VASSAL → PEACE. Threat -8. 5-turn cooldown.

### E9. Defection Cascade Warning
Create 2 vassals with loyalty < 25 → end turn
**Expected:** "Empire Trembles" notification. Dispatch event.

---

## SECTION F: Diplomatic Ledger (D Key)

### F1-F7: Open/close toggle, Nations tab, Treaties tab, Threat/Coalition tab, Talleyrand tab, Fog-filtered army strength, Number key sub-tab switching (1-4)

### F8. Nations Tab — AI Relations Filtering (BF4/DLF-3)
`cheat set_diplo_state Prussia PEACE` then open ledger, Nations tab.
**Expected:** Prussia's AI relations list only shows notable states (WAR, ALLIANCE, DEFENSIVE_ALLIANCE, OPEN_BORDERS, NON_AGGRESSION). PEACE relations are hidden.

### F9. Nations Tab — Vassal Icon State Check (BF4/DLF-1)
`cheat set_relation Prussia -20` with Prussia at PEACE state, open ledger.
**Expected:** No vassalizable icon for Prussia (PEACE is not in VASSAL_MIN_STATES). Change to WAR: `cheat set_diplo_state Prussia WAR` — icon should now appear.

---

## SECTION G: Diplomatic Advisory

### G1-G4: "what about Austria?", "who is the bigger threat?", "what should I do?", "can we beat Prussia?"

---

## SECTION H: Diplomatic Missions

### H1-H4: improve relations, court nation, spy on, undermine alliance

### H5. COURT_NATION Blowback (BF4/DLF-4)
`cheat give_dp 20`, start COURT_NATION mission on Austria. End several turns.
**Expected:** +8 relation/turn (skill 10). Occasionally (20% per turn) a blowback event fires: "Diplomatic blowback! Austria discovered our scheming. (-3 relation)". Blowback penalty is always -3 regardless of skill. Check Morning Dispatch for `diplomatic_mission_blowback` event.

### H6. GATHER_INTEL Visibility Grant (BF4/DLF-5)
`cheat give_dp 20`, start GATHER_INTEL mission on Prussia. End 3 turns.
**Expected:** On completion, message shows regions revealed count. Map should show FULL visibility on all Prussia-controlled regions for 5 turns. After 5 more turns, visibility should decay normally. Save/load during grant window — verify grants persist.

### H7. UNDERMINE_ALLIANCE Ally Selection (BF4/DLF-2)
Setup: `cheat set_diplo_state Prussia ALLIANCE` (with only Austria allied).
Start UNDERMINE_ALLIANCE mission on Prussia.
**Expected (single ally):** Dialogue auto-selects Austria. Shows "undermine the alliance between Prussia and Austria".
Setup (multiple): also `cheat set_diplo_state Prussia DEFENSIVE_ALLIANCE` with Britain.
**Expected (multiple allies):** Dialogue presents ally selection options (Austria, Britain).
Setup (no allies): clear all Prussia alliances.
**Expected (no allies):** Dialogue shows "Prussia has no alliances to undermine."

### H8. UNDERMINE_ALLIANCE Per-Turn Effect (BF4/DLF-2)
Start UNDERMINE_ALLIANCE on Prussia targeting Austria alliance. End turns.
**Expected:** Relation between Prussia and Austria decreases by ~4-5/turn (skill-scaled). Check diplomatic ledger Talleyrand tab — should show both nations ("Undermining alliance between Prussia and Austria"). When alliance breaks (relation drops below threshold), mission auto-completes with "alliance has collapsed" message.

### H9. UNDERMINE_ALLIANCE Ledger Display (BF4/DLF-2)
During active UNDERMINE_ALLIANCE mission, press D to open Diplomatic Ledger, Talleyrand tab.
**Expected:** Active mission shows target AND target_ally (both nations in the pair).

---

## SECTION I: Talleyrand Sabotage & Defiance

### I1-I2: Sabotage discovery popup, Talleyrand redemption popup

---

## SECTION J: War System Integration

### J1-J5: Declare war, war score tracking, war cascade, armistice expiration, auto-downgrade

---

## SECTION K: Trade Income & Economy

### K1-K3: Trade income display, changes with state, vassal tribute

---

## SECTION L: Save/Load with Diplomatic State

### L1-L4: Save with diplomacy, load preserves state, save with pending dialogue, save/load with war panel

---

## SECTION M: Edge Cases & Regression

### M1-M14: Proposal to self, duplicate state, double war declaration, vassal of vassal, release cooldown, DP zero, simultaneous popups, hotkey blocking during popups, rapid F1 spam, nation eliminated, fog leak prevention, dialogue guard, dialogue timeout, clear stuck dialogue

---

## SECTION N: Continental System (DEFERRED — not implemented)

---

## SECTION O: Morning Dispatch — Diplomatic Events

### O1-O4: Coalition threat in dispatch, vassal loyalty warning, treaty expiration, war cascade

---

## SECTION P: Notification Bar — Diplomatic Alerts

### P1-P2: Persistent notifications, notification dismissal

---

## SECTION Q: War Status Panel HUD

### Q1-Q6: Panel appears/hides, multiple war cards, coalition grouping, armistice cards, panel resizing

---

## SECTION R: War Detail Popup

### R1-R6: Bilateral war view, coalition view, armistice view, negotiate peace handoff, target coalition member, refresh in place

---

## SECTION S: Alliance Paradox Popup

### S1-S3: Attack ally's marshal, honor choice, break choice

---

## SECTION T: Proposal Confirm Popup

### T1-T3: Terms review, send, cancel

---

## CHECKLIST SUMMARY

| Section | Tests | Priority |
|---------|-------|----------|
| A: Diplomacy Wizard | 8 | HIGH |
| B: Proposals | 9 | HIGH |
| C: AI Proposals | 6 | HIGH |
| D: Coalition | 10 | HIGH |
| E: Vassal | 9 | HIGH |
| F: Diplomatic Ledger | 7 | MEDIUM |
| G: Advisory | 4 | MEDIUM |
| H: Missions | 4 | MEDIUM |
| I: Sabotage/Defiance | 2 | LOW |
| J: War Integration | 5 | HIGH |
| K: Economy | 3 | MEDIUM |
| L: Save/Load | 4 | HIGH |
| M: Edge Cases | 14 | HIGH |
| N: Continental System | 1 | DEFERRED |
| O: Dispatch | 4 | MEDIUM |
| P: Notifications | 2 | MEDIUM |
| Q: War Status Panel | 6 | HIGH |
| R: War Detail Popup | 6 | HIGH |
| S: Alliance Paradox | 3 | HIGH |
| T: Proposal Confirm | 3 | MEDIUM |
| **TOTAL** | **110** | |
