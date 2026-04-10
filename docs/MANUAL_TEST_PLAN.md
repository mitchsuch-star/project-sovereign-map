# Manual Test Plan (Godot + Backend)

## Setup (every test session)

```bash
# Start backend
python backend/main.py

# Verify connection in Godot
# Should see "Connected" or similar
```

---

## Test 1: Strategic Command Costs

### 1A. Standard marshal costs 2 AP -- PASS

```
/debug set_location Ney Belgium
/debug set_location Wellington Rhineland
/debug freeze Wellington

Ney, scout Belgium          # 3 AP left
Davout, scout Lyon           # 2 AP left
Grouchy, scout Waterloo      # 1 AP left

Ney, march to Rhineland
```
**Expected:** "Not enough actions! Need 2, have 1."

### 1B. Full AP works

```
# Fresh turn (4 AP)
Ney, march to Rhineland
```
**Expected:** Success, 2 AP remaining. Ney starts marching.

### 1C. Literal costs 1 AP

```
# Fresh turn, use 3 AP first
Ney, scout Belgium
Davout, scout Lyon
Ney, scout Belgium
# 1 AP left

Grouchy, march to Lyon
```
**Expected:** Success. Grouchy starts marching (literal = 1 AP).

### 1D. Auto-upgrade attack->PURSUE costs 2 AP -- PASS

```
/debug set_location Ney Belgium
/debug set_location Wellington Bavaria
/debug freeze Wellington

# Fresh turn, use 2 AP
Davout, scout Lyon
Grouchy, scout Waterloo
# 2 AP left

Ney, attack Wellington
```
**Expected:** Success. Auto-upgrades to PURSUE (target out of range). Costs 2 AP (same as explicit strategic).

---

## Test 2: Blocked Path -- Personality Differences

### Setup (use before each sub-test)

```
/debug set_location Wellington Belgium
/debug freeze Wellington
/debug set_strength Wellington 50000
```

### 2A. Aggressive (Ney) -- good odds -> auto-attack

```
/debug set_location Ney Paris
/debug set_strength Ney 72000

Ney, march to Rhineland
```
**Expected:** Ney auto-attacks Wellington (72k vs 50k, ratio >= 0.7). No popup. If wins, continues to Rhineland.

### 2B. Aggressive (Ney) -- bad odds -> popup

```
/debug set_location Ney Paris
/debug set_strength Ney 30000
/debug set_strength Wellington 100000

Ney, march to Rhineland
```
**Expected:** Blocked path popup with options: attack, go_around, hold_position, cancel_order.

- Test attack: Ney attacks (bad odds)
- Test go_around: Ney reroutes (Paris->Lyon->Rhineland)
- Test hold_position: Ney stops, order paused (-3 trust if mid-march)
- Test cancel_order: Order cancelled

### 2C. Cautious (Davout) -- always asks

```
/debug set_location Davout Paris
/debug set_strength Davout 72000

Davout, march to Rhineland
```
**Expected:** Blocked path popup EVEN with good odds (cautious always asks).

### 2D. Literal (Grouchy) -- silent reroute -- PASS

```
/debug set_location Grouchy Paris

Grouchy, march to Rhineland
```
**Expected:** NO popup. Grouchy silently reroutes around Belgium (Paris->Lyon->Rhineland). Message mentions alternate path.

### 2E. First-step cancel has 0 trust penalty

```
/debug set_location Ney Paris
/debug set_strength Wellington 100000

Ney, march to Rhineland
# Popup appears -> click cancel_order
```
**Expected:** Order cancelled, 0 trust penalty (first step, not mid-march).

---

## Test 3: Cannon Fire Interrupt

### Setup

```
/debug set_location Ney Lyon
/debug set_location Wellington Belgium
/debug set_location Blucher Belgium
/debug freeze Wellington
/debug freeze Blucher
```

### 3A. Aggressive -- gets interrupt

```
Ney, march to Rhineland
# End turn so Ney moves
end turn
# Next turn -- if Ney is within 2 regions of a battle, cannon fire triggers
```
**Note:** Cannon fire requires a battle to happen within 2 regions during strategic execution. Hard to trigger deterministically. Alternative: check the log for cannon_fire interrupt type.

### 3B. Literal (Grouchy) -- NEVER interrupts

```
/debug set_location Grouchy Lyon

Grouchy, march to Rhineland
end turn
```
**Expected:** Grouchy continues march silently. No cannon fire popup EVER (The Grouchy Moment).

---

## Test 4: PURSUE Completion

### Setup

```
/debug set_location Ney Belgium
/debug set_location Wellington Rhineland
/debug freeze Wellington
/debug set_strength Ney 72000
/debug set_strength Wellington 40000
```

### 4A. PURSUE completes after combat

```
Ney, pursue Wellington
end turn
# Ney reaches Rhineland, fights Wellington
```
**Expected:** Combat happens. Order shows "completed" regardless of outcome (win/lose/stalemate). NO stalemate popup.

### 4B. Cautious/Literal complete on arrival without attacking

```
/debug set_location Davout Belgium
/debug set_location Wellington Rhineland

Davout, pursue Wellington
end turn
```
**Expected:** Davout arrives at Rhineland. Message: "Davout has located Wellington at Rhineland and awaits orders." Order completed. No auto-attack (cautious).

---

## Test 5: HOLD and Defense Bonus

### Setup

```
/debug set_location Grouchy Belgium
```

### 5A. HOLD grants +15% defense

```
Grouchy, hold Belgium
```
**Expected:** Grouchy holds position. +15% holding_position defense bonus active.

### 5B. Cancel clears defense bonus

```
Grouchy, cancel
```
**Expected:** Order cancelled. holding_position = False. No lingering +15%.

### 5C. HOLD completion clears bonus

```
Grouchy, hold Belgium until battle won
# Trigger battle and win
```
**Expected:** Order completes. holding_position cleared.

---

## Test 6: Grouchy Clarification Popup

### 6A. Generic target

```
Grouchy, attack
```
**Expected:** Clarification popup (free, 0 AP). "Which enemy shall I engage, Sire?" Options list nearest enemies.

### 6B. Generic strategic target

```
Grouchy, pursue the enemy
```
**Expected:** Clarification popup with strategic_type=PURSUE. Options list enemy marshals.

### 6C. Non-literal skips clarification

```
Ney, attack
```
**Expected:** NO popup. Ney auto-resolves to nearest enemy.

---

## Test 7: Cancel Command

### Setup

```
/debug set_location Ney Belgium
/debug set_location Wellington Vienna
/debug freeze Wellington
```

```
Ney, march to Vienna
```

### 7A. Mid-march cancel (-3 trust)

```
end turn
# Ney moves one region
Ney, cancel
```
**Expected:** Order cancelled. -3 trust penalty. Message: "Ney halts his march and awaits new orders."

### 7B. Same-turn cancel (0 trust)

```
# Fresh setup
Ney, march to Vienna
Ney, cancel
```
**Expected:** Order cancelled. 0 trust penalty (first step).

### 7C. Cancel keywords

Test each: "halt", "stop", "cancel", "abort", "stand down", "belay that"

**Expected:** All work as cancel command.

---

## Test 8: Objection System

### 8A. Aggressive objects to defensive order

```
/debug set_location Ney Belgium
/debug set_location Wellington Belgium
/debug freeze Wellington

Ney, defend
```
**Expected:** Objection popup. Ney protests defending. Options: Trust (+12), Insist (-10), Compromise (+3).

### 8B. Cautious objects to risky attack

```
/debug set_location Davout Paris
/debug set_location Wellington Paris
/debug freeze Wellington
/debug set_strength Davout 20000
/debug set_strength Wellington 80000

Davout, attack Wellington
```
**Expected:** Objection popup. Davout protests attacking at 1:4 odds.

### 8C. Insist override

```
# From any objection popup -> click Insist
```
**Expected:** Original order executes. Trust penalty applied.

---

## Test 9: Redemption

### 9A. Trust floor trigger

```
/debug set_trust Ney 21

# Issue an order Ney will object to, then Insist (-10 to -15 trust)
Ney, defend
# Insist -> trust drops to <=20
```
**Expected:** Redemption popup. Options depend on field marshal count.

### 9B. Last marshal protection

```
# Dismiss/admin the other two marshals first, or set strength to 0
/debug set_strength Davout 0
/debug set_strength Grouchy 0
/debug set_trust Ney 15
```
**Expected:** Only "Grant Autonomy" available (last marshal).

---

## Test 10: Glorious Charge

### Setup

```
/debug set_location Ney Belgium
/debug set_location Wellington Belgium
/debug freeze Wellington
/debug cavalry Ney
/debug set_recklessness Ney 3
```

### 10A. Popup appears at recklessness 3

```
Ney, attack Wellington
```
**Expected:** Glorious Charge popup. Two options: CHARGE (2x damage dealt AND taken) or RESTRAIN (normal attack).

### 10B. Charge resets recklessness

```
# Choose CHARGE
```
**Expected:** 2x damage multiplier. Recklessness resets to 0 after.

### 10C. Restrain keeps recklessness

```
# Choose RESTRAIN
```
**Expected:** Normal damage. Recklessness stays at 3 (increments to 4 on next attack win).

---

## Test 11: Enemy Phase Display

```
/debug set_location Wellington Belgium
/debug set_location Ney Belgium
# Don't freeze -- let AI act

end turn
```
**Expected:** Enemy phase popup shows all actions per nation. Battle details if combat occurred. Conquest events highlighted. Scrollable if many actions.

---

## Test 12: Enemy Marshals Visible on Map

```
# Fresh game start -- no debug needed
```
**Expected:** Wellington, Uxbridge at Waterloo. Blucher, Gneisenau at Netherlands. All visible on map with correct nation colors.

---

## Test 13: AI Fortify Loop Fixed

```
# Watch Prussia's turn in enemy phase
end turn
end turn
end turn
end turn
end turn
```
**Expected:** Gneisenau does NOT burn all actions on unfortify->fortify->unfortify->fortify. Should take meaningful actions (move, capture, drill) instead.

---

## Test 14: Cavalry Limits

### 14A. Auto-switch after 3 turns

```
/debug set_location Ney Paris
/debug cavalry Ney

Ney, defend
end turn
end turn
end turn
```
**Expected:** Turn 3: "Ney's cavalry is too restless! Auto-switched to AGGRESSIVE. Trust -3"

### 14B. Auto-unfortify after 3 turns

```
/debug cavalry Ney
Ney, fortify
end turn
end turn
end turn
```
**Expected:** Turn 3: "Ney's horses cannot stay still! Auto-unfortified. Trust -3"

---

## Test 15: SUPPORT Command

### Setup

```
/debug set_location Davout Lyon
/debug set_location Ney Belgium

Davout, support Ney
```
**Expected:** Davout begins marching toward Ney's location. Order continues per turn.

### 15A. Ally moves -- cautious asks

```
# Move Ney after Davout starts supporting
Ney, move to Rhineland
end turn
```
**Expected:** If Davout is cautious, ally_moving interrupt popup. Options: follow, hold_current, cancel_support.

---

## Test 16: Strategic Progress Display

```
/debug set_location Ney Belgium
/debug set_location Wellington Vienna
/debug freeze Wellington

Ney, march to Vienna
end turn
```
**Expected:** After enemy phase, strategic report shows: "Ney: MOVE_TO Vienna -- continues (X regions remaining)."

---

## Test 17: Strategic Auto-Attack Stalemate Cap (NEW)

Verifies that aggressive marshals on strategic orders don't get infinite free attacks.

### Setup

```
/debug set_location Ney Paris
/debug set_location Wellington Belgium
/debug freeze Wellington
/debug set_strength Ney 60000
/debug set_strength Wellington 55000
```

### 17A. First encounter -- auto-attack

```
Ney, march to Rhineland
```
**Expected:** Ney auto-attacks Wellington (ratio >= 0.7). If victory, continues. If stalemate, shows interrupt popup: "Ney attacked Wellington during march but the battle was inconclusive."

### 17B. After stalemate -- no more auto-attacks

```
# From 17A stalemate popup -> choose "continue_order"
end turn
# Ney encounters Wellington again
```
**Expected:** Popup asks player what to do (NOT auto-attack). Message: "Wellington still blocks the path. Previous assault was inconclusive. Orders?" Options: attack_anyway, go_around, hold_position, cancel_order.

### 17C. Player-chosen attack resets nothing

```
# From 17B popup -> choose "attack_anyway"
# If stalemate again...
end turn
```
**Expected:** Still asks player (no auto-attack). Each stalemate requires explicit player decision.

### 17D. Victory resets counter

```
# From any popup -> choose "attack_anyway" -> win
end turn
# Hit another enemy on the path
```
**Expected:** Auto-attack resumes for the new enemy (counter reset on victory).

---

## Test G: Garrison System (Session 37)

> **Estimated time:** 15-20 min. G1-G3 critical path (~8 min), G4-G6 visual (~10 min).

### G1. Garrison Placement + AP Cost

#### G1A. Successful garrison (message + overlay)

```
/debug set_location Grouchy Lyon
/debug set_strength Grouchy 50000
Grouchy, garrison
```

**Expected:**
- Message: "Grouchy detaches 3,000 troops to garrison Lyon. Army strength: 47,000."
- Map: Blue shield icon appears below Lyon circle, text "3k"
- Hover Lyon: tooltip shows "Garrison: 3,000 [Detachment]" in bronze text after Supply line

#### G1B. Garrison blocked with 1 AP

```
# Fresh turn (4 AP)
Ney, scout Belgium           # 3 AP
Davout, scout Lyon            # 2 AP
Grouchy, scout Waterloo       # 1 AP

Ney, garrison
```

**Expected:** "Not enough actions! Need 2, have 1."

#### G1C. Garrison succeeds with exactly 2 AP

```
# Fresh turn (4 AP)
Ney, scout Belgium            # 3 AP
Davout, scout Lyon             # 2 AP

Ney, garrison
```

**Expected:** Success. 0 AP remaining.

---

### G2. Garrison Cap (3 per nation)

#### G2A. Capital counts toward cap — fill to 3

```
# Paris already has capital garrison (1/3 used)
/debug set_location Grouchy Lyon
/debug set_strength Grouchy 50000
Grouchy, garrison
end turn

/debug set_location Davout Waterloo
/debug set_strength Davout 50000
Davout, garrison
end turn
```

**Expected:** Both succeed. France now at 3/3 (Paris + Lyon + Waterloo).

#### G2B. Cap blocks 4th garrison

```
/debug set_location Ney Belgium
/debug set_strength Ney 50000
Ney, garrison
```

**Expected:** "Berthier shakes his head. 'We already maintain 3 garrisons, Your Majesty. Our supply lines cannot support another. Maximum 3 garrisons per nation.'"

#### G2C. No AP consumed on cap rejection

Check AP counter before and after — should be unchanged.

---

### G3. Garrison Failure Cases

#### G3A. Not enough troops (needs 8k)

```
/debug set_strength Ney 5000
Ney, garrison
```

**Expected:** "Ney's forces are too depleted to spare a garrison...need at least 8,000 men..."

#### G3B. Enemy territory

```
/debug set_location Ney Vienna
/debug set_strength Ney 50000
Ney, garrison
```

**Expected:** "We do not control Vienna, Your Majesty."

#### G3C. Enemy present in region

```
/debug set_location Ney Belgium
/debug set_location Wellington Belgium
/debug freeze Wellington
Ney, garrison
```

**Expected:** "Enemy forces contest Belgium. We cannot garrison while under threat..."

#### G3D. Already garrisoned

```
# Lyon already garrisoned from G2A
/debug set_location Ney Lyon
/debug set_strength Ney 50000
Ney, garrison
```

**Expected:** "A garrison already holds Lyon, Your Majesty."

---

### G4. Map Overlay Visuals

#### G4A. Shield appearance

After placing a garrison (G1A), verify:
- Blue rectangle below Lyon circle (France color)
- White border
- "3k" text centered, white, small font

#### G4B. Hover tooltip — player garrison

Hover over Lyon (player-placed garrison):
- Tooltip shows "Garrison: 3,000 [Detachment]" in bronze/brown color
- Line appears after "Supply:" and before "War Damage" (if any)

#### G4C. Hover tooltip — capital garrison

Hover over Paris:
- Tooltip shows "Garrison: 15,000" (no [Detachment] tag)

---

### G5. Fog of War Interaction

#### G5A. Enemy garrison in fogged region

End several turns to let AI place garrisons. Find an enemy region with PARTIAL/STALE visibility that has a garrison:
- Shield should appear dimmed with "?" text
- Tooltip shows "Garrison: Present (unknown strength)"

#### G5B. UNKNOWN region hides garrison

Enemy garrison in UNKNOWN visibility region should NOT show shield at all. Tooltip shows "No intelligence".

#### G5C. Own garrison always visible

Player garrisons in own territory always show exact strength regardless of fog state.

---

### G6. Garrison Persistence

#### G6A. Survives turn processing

```
# After placing garrison in G1A
end turn
```

**Expected:** Garrison still visible on map. Shield icon persists with same strength.

#### G6B. Capital regens, detachment doesn't

- End several turns
- Paris capital garrison should regen toward 15k if damaged
- Player garrison at Lyon should NOT regen (stays at 3,000)

---

## Test M: Manpower Pools (Session 41)

> **Estimated time:** 15-20 min. M1-M3 critical path (~8 min), M4-M6 visual/HUD (~10 min).

### M1. HUD Display — Initial State

```
# Fresh game start, verify connection
```

**Expected:**
- Status bar shows: `Turn: 1  Actions: 4/4  Admin: 2/2  Gold: 1,200  Inf: 80,000  Cav: 15,000`
- Inf value is green, Cav value is reddish
- No layout clipping — all 6 items visible in status bar

---

### M2. Recruitment Draws from Pool

#### M2A. Infantry recruit (Davout)

```
Davout, recruit
```

**Expected:**
- Message: "Davout receives 10,000 infantry reinforcements" (Berthier voice)
- Message includes "Infantry reserves: 70,000 remaining"
- HUD: Inf drops from 80,000 → 70,000
- HUD: Gold drops by recruit cost (200g base, 150g if at capital)

#### M2B. Cavalry recruit (Ney)

```
Ney, recruit
```

**Expected:**
- Message: "Ney receives 5,000 cavalry reinforcements"
- Message includes "Cavalry reserves: 10,000 remaining"
- HUD: Cav drops from 15,000 → 10,000
- HUD: Gold drops by 300g base (or 225g if at capital)

#### M2C. Pool empty blocks recruit

```
# Drain cavalry pool
/debug set_manpower France cavalry 0
Ney, recruit
```

**Expected:**
- Berthier voice error: "no cavalry reserves remaining"
- Message includes regen rate and estimated turns to refill
- No gold deducted, no troops added

---

### M3. Regen After Turn

```
# After recruiting in M2
end turn
```

**Expected:**
- HUD: Inf increases by ~5,000 (base regen per controlled region)
- HUD: Cav increases by base + plains bonuses
- Economy command shows exact regen breakdown

#### M3A. Economy report shows pools

```
economy
```

**Expected:**
- MANPOWER section visible with:
  - Infantry Pool: X (+5,000/turn)
  - Cavalry Pool: X (+Y/turn) where Y depends on plains/stables
- Low cavalry warning if applicable

---

### M4. HUD Color Warnings

#### M4A. Low cavalry — orange

```
/debug set_manpower France cavalry 8000
```

**Expected:** Cav value turns orange

#### M4B. Critical cavalry — red

```
/debug set_manpower France cavalry 3000
```

**Expected:** Cav value turns red

#### M4C. Low infantry — orange

```
/debug set_manpower France infantry 35000
```

**Expected:** Inf value turns orange

#### M4D. Critical infantry — red

```
/debug set_manpower France infantry 15000
```

**Expected:** Inf value turns red

#### M4E. Healthy pools — normal colors

```
/debug set_manpower France infantry 80000
/debug set_manpower France cavalry 15000
```

**Expected:** Colors return to green (inf) and reddish (cav)

---

### M5. Stables Building

```
/debug set_location Davout Lyon
Davout, build stables
end turn
end turn
```

**Expected:**
- Build starts: "Construction of stables in Lyon has begun (2 turns)"
- After 2 turns: stables complete
- Economy report: cavalry regen increases by 750
- If Lyon is plains: even higher cavalry regen

---

### M6. Save/Load Persistence

#### M6A. Save with depleted pools

```
# After several recruits
save
```

#### M6B. Load restores pools

```
load
# Select the save
```

**Expected:**
- HUD shows correct manpower values from save
- Economy report matches saved state
- Pools round-trip correctly

---

### M7. HUD Updates Across All Flows

Verify manpower HUD updates after each interaction type:

| Flow | How to trigger | Check HUD updates? |
|------|---------------|-------------------|
| Normal command | `Davout, recruit` | Inf/Cav change |
| Objection → Proceed | Object then Insist on recruit | Inf/Cav change |
| Capture choice | Capture region → Plunder/Secure | No pool change, but HUD refreshes |
| Strategic response | Strategic report popup → Continue | HUD refreshes |
| End turn | `end turn` | Regen visible |
| Load game | `load` → select save | Pools from save |
| Connection test | Restart Godot client | Initial pools shown |

---

## Debug Command Quick Reference

| Command | Purpose |
|---------|---------|
| `/debug set_location <marshal> <region>` | Teleport any marshal |
| `/debug freeze <marshal>` | Toggle AI freeze (stays put) |
| `/debug set_strength <marshal> <N>` | Set troop count |
| `/debug set_morale <marshal> <0-100>` | Set morale |
| `/debug set_trust <marshal> <0-100>` | Set trust |
| `/debug set_recklessness <marshal> <0-4>` | Set cavalry recklessness |
| `/debug set_recovery <marshal> <0-3>` | Set retreat recovery |
| `/debug set_fortified <marshal>` | Toggle fortified |
| `/debug cavalry <marshal>` | Toggle cavalry status |
| `/debug hold <marshal>` | Set holding_position |
| `/debug counter_punch <marshal>` | Set counter-punch ready |
| `/debug set_manpower <nation> <infantry\|cavalry> <amount>` | Set manpower pool |
| `/debug ai_turn <nation>` | Force AI turn |
| `/debug list_marshals` | Show all positions |

## Top Bar Smoke Tests (Session A)

### TB1. Top bar renders on startup
**Expected:** Top bar visible at top of screen with buttons (Event Log, Ledger, Generals, Dispatch), notification area, turn counter.

### TB2. Event Log toggle (L key + button)
1. Press L — campaign log opens (centered panel)
2. Press L again — closes
3. Click "Event Log" button — opens
4. Click "Event Log" button again — closes
**Expected:** One-at-a-time toggling, button highlights when active.

### TB3. Dispatch re-read (R key + button)
1. End a turn (enemy phase + morning dispatch fires)
2. Press R — dispatch re-read screen opens showing last dispatch
3. Press R again — closes
4. Click Dispatch button — opens
**Expected:** Same BBCode formatting as terminal dispatch. "No dispatch available yet." on turn 1 before first end turn.

### TB4. Screen switching
1. Press L (event log opens)
2. Press R (event log closes, dispatch opens)
3. Press Esc (dispatch closes)
**Expected:** Only one screen at a time. Esc closes active screen.

### TB5. Terminal active during screen
1. Open event log (L)
2. Type a command in terminal and press Enter
**Expected:** Command executes normally while screen is open.

### TB6. Map blocked during screen
1. Open event log (L)
2. Try arrow key panning — should not pan
3. Try clicking on map — should not interact
4. Close screen (L) — panning and clicks work again

### TB7. Screens close on turn transition
1. Open event log (L)
2. Press E (end turn)
**Expected:** Screen closes before enemy phase dialog.

### TB8. Generals button opens marshal management
1. Press G — marshal management screen opens
2. Press G again — closes
**Expected:** Card-based marshal view with all player marshals.

### TB9. Notification bar in top bar
**Expected:** Notification icons appear in the right section of the top bar (not floating separately at top-right). Expanded panel drops below correctly.

### TB10. Turn counter updates
1. Note turn counter in top bar
2. End a turn
**Expected:** Turn counter updates to match new turn number.

## Strategic Ledger Smoke Tests (Session B)

### LG1. Forces tab renders
1. Press T — ledger opens on FORCES tab
2. Verify all player marshals listed with name, type, location, strength, morale, trust, status
**Expected:** All 4 French marshals visible. Trust/morale color coded (red < 30/40, orange < 55/60).

### LG2. Territories tab renders
1. Open ledger (T), press 2 — TERRITORIES tab
2. Verify player-controlled regions listed with income, stability, supply status
**Expected:** French-controlled regions shown. Supply "Over capacity" in red if applicable.

### LG3. Economy tab renders
1. Open ledger (T), press 3 — ECONOMY tab
2. Verify treasury, income, upkeep, net, income breakdown
**Expected:** Net shown in green (positive) or red (negative). Bankruptcy in red if active.

### LG4. Intelligence tab renders
1. Open ledger (T), press 4 — INTELLIGENCE tab
2. Verify known enemies listed with visibility tier labels
**Expected:** Visibility color coding: confirmed (green), partial (grey), stale (orange), last known (red).

### LG5. Manpower tab renders
1. Open ledger (T), press 5 — MANPOWER tab
2. Verify infantry, cavalry, artillery pools with regen rates and turns to full
**Expected:** Depleted pools (0) in red, low pools in orange.

### LG6. Sub-tab switching (1-5 keys)
1. Open ledger (T)
2. Press 1, 2, 3, 4, 5 — tabs switch
3. Press 1-5 while ledger is closed — nothing happens
**Expected:** Number keys only work when ledger is visible.

### LG7. T key toggles ledger
1. Press T — ledger opens
2. Press T — ledger closes
3. Open event log (L), press T — log closes, ledger opens
**Expected:** One screen at a time. Toggle behavior.

### LG8. Screen closes on turn change
1. Open ledger (T)
2. Press E (end turn)
**Expected:** Ledger closes before enemy phase dialog.

## Diplomatic Ledger Smoke Tests (Session 8B)

> **Estimated time:** 15-20 min.

### DL1. D key opens diplomatic ledger
1. Press D — diplomatic ledger opens (centered panel, CanvasLayer 50)
2. Press D again — closes
3. Click "Diplomacy" button in top bar — opens
4. Click "Diplomacy" button again — closes
**Expected:** Toggle behavior, button highlights when active.

### DL2. Nations tab renders (Tab 1)
1. Open diplomatic ledger (D), should default to Nations tab
2. Verify all non-France nations listed with name, diplomatic state, relation value, army strength
**Expected:** WAR in red, ALLIANCE in blue, neutral in white. Negative relations in red, positive in green. Army strength fog-filtered ("~25,000" or "Unknown").

### DL3. Treaties tab renders (Tab 2)
1. Open diplomatic ledger (D), press 2 — Treaties tab
2. Verify active treaties listed with nation pair, type, clauses, duration
**Expected:** Empty list if no treaties. Duration shown as turns or "Permanent". Cancel cost "1 DP" shown.

### DL4. Threat & Coalition tab renders (Tab 3)
1. Open diplomatic ledger (D), press 3 — Threat & Coalition tab
2. Verify threat bar (20 chars wide), tier label, brewing status
**Expected:** Threat bar uses filled/empty characters. Tier colored: LOW=green, MODERATE=amber, HIGH=red, CRITICAL=red+pulsing. Coalition brewing shows turns remaining.

### DL5. Talleyrand tab renders (Tab 4)
1. Open diplomatic ledger (D), press 4 — Talleyrand tab
2. Verify trust label, DP remaining/max, active mission, envoy count
**Expected:** Trust label colored (Loyal=green, Treacherous=red). DP format "X/Y". "Idle" if no mission.

### DL6. Sub-tab switching (1-4 keys)
1. Open diplomatic ledger (D)
2. Press 1, 2, 3, 4 — tabs switch, button highlights update
3. Press 1-4 while ledger is closed — nothing happens
**Expected:** Number keys only work when diplomatic ledger is visible.

### DL7. Screen switching with other screens
1. Press T (strategic ledger opens)
2. Press D (strategic ledger closes, diplomatic ledger opens)
3. Press L (diplomatic ledger closes, event log opens)
**Expected:** Only one screen at a time.

### DL8. Top bar DP counter
**Expected:** "DP: X/Y" always visible in top bar right section. Updates after every command.

### DL9. Top bar threat indicator
1. Start game (threat 0) — threat indicator hidden
2. Raise threat above 30 — indicator appears in amber
3. Raise threat above 60 — indicator turns red
**Expected:** Threshold-based visibility and coloring.

### DL10. Top bar envoy indicator
1. Start game (no envoys) — envoy indicator hidden
2. Get diplomatic proposal from AI — envoy indicator appears with count
3. Click envoy indicator — auto-types advisory command in terminal
**Expected:** Clickable, amber badge, hidden when count is 0.

### DL11. R key opens dispatch (rebind from D)
1. Press R — dispatch re-read opens
2. Press D — should NOT open dispatch (opens diplomatic ledger instead)
**Expected:** D=Diplomatic Ledger, R=Dispatch. No conflict.

---

## Diplomacy Gameplay Tests

> **Estimated time:** 45-60 min total. Can be broken into individual test groups.

### DP1. War Declaration End-to-End

#### DP1A. Declare war via command

```
/debug set_relation France Prussia PEACE
declare war on Prussia
```

**Expected:**
- Talleyrand objection popup appears: [Proceed][Modify][Cancel]
- Choose Proceed → war declared
- Message confirms "France declares war on Prussia"
- Diplomatic ledger (D) Nations tab shows Prussia as WAR (red)
- Map updates if regions change control

#### DP1B. Cascade war declaration

```
/debug set_relation France Austria PEACE
/debug set_relation Prussia Austria ALLIANCE
declare war on Prussia
```

**Expected:**
- After declaring war on Prussia, cascade triggers
- Austria joins war against France (allied with Prussia)
- Both Prussia and Austria show WAR in diplomatic ledger

#### DP1C. Cancel war declaration

```
/debug set_relation France Saxony PEACE
declare war on Saxony
# Talleyrand popup → choose Cancel
```

**Expected:** War not declared. No state change. No DP spent.

---

### DP2. Peace Proposal Lifecycle

#### DP2A. Propose peace

```
/debug set_relation France Prussia WAR
propose peace to Prussia
```

**Expected:**
- Command accepted, DP deducted
- Message confirms proposal sent
- Proposal visible in Treaties tab or Talleyrand tab

#### DP2B. AI responds to peace proposal

```
# After DP2A
end turn
end turn
```

**Expected:**
- AI evaluates proposal based on acceptance formula
- If accepted: relation changes, treaty created, shown in ledger
- If rejected: message in dispatch or notification
- If counter-offer: incoming proposal popup with [Accept][Counter][Reject]

---

### DP3. AI Proposal Incoming

#### DP3A. Receive AI proposal popup

```
# Play several turns to let AI generate proposals
end turn
end turn
end turn
end turn
end turn
```

**Expected:**
- When AI proposes, incoming_proposal_popup appears
- Shows: from_nation, diplomat name/personality, clauses, Talleyrand assessment
- Three buttons: [Accept] [Counter] [Reject]

#### DP3B. Accept AI proposal

```
# From DP3A popup → click Accept
```

**Expected:** Treaty created. Diplomatic ledger updates. Relation improves.

#### DP3C. Reject AI proposal

```
# From new AI proposal → click Reject
```

**Expected:** Proposal dismissed. No state change. Relation may decrease slightly.

#### DP3D. Counter AI proposal

```
# From new AI proposal → click Counter
```

**Expected:** Counter-offer generated by AI with modified terms. New popup appears with `is_counter_offer` flag. Can Accept or Reject the counter.

---

### DP4. Diplomacy Wizard (F1 Button)

#### DP4A. Open wizard

```
# Press F1
```

**Expected:** Diplomacy wizard opens. Shows categorized nation list (At War, Allied, Neutral). Each nation shows current state and relation value.

#### DP4B. Select nation and view actions

```
# Press F1, click on a nation (e.g., Prussia)
```

**Expected:**
- Step 2: Action list appears for selected nation
- Actions filtered by current diplomatic state (e.g., can't propose alliance if at war)
- Each action shows likelihood (Likely/Possible/Unlikely) with color coding
- Assessment text panel shows Talleyrand's analysis

#### DP4C. Execute action from wizard

```
# Select nation → select action (e.g., "Propose Non-Aggression")
```

**Expected:**
- Wizard closes
- Command auto-typed in terminal
- Command executes normally (objections, DP cost, etc.)
- Diplomatic ledger reflects change

#### DP4D. Wizard shows correct likelihood colors

```
# Press F1, check likelihood colors for various nations
```

**Expected:**
- Green: Likely (acceptance > 60)
- Yellow/Amber: Possible (acceptance 30-60)
- Red: Unlikely (acceptance < 30)
- Grey: Unavailable actions

---

### DP5. Coalition Formation Cycle

#### DP5A. Raise threat to brewing

```
/debug set_threat 55
end turn
```

**Expected:**
- Threat indicator appears in top bar (amber)
- Diplomatic ledger Threat tab shows threat bar filling
- Tier label updates (MODERATE → HIGH)

#### DP5B. Coalition brewing warning

```
/debug set_threat 75
end turn
```

**Expected:**
- Morning dispatch warns about coalition brewing
- Threat tab shows "Coalition brewing" with turns remaining
- Threat indicator turns red in top bar

#### DP5C. Coalition declares

```
/debug set_threat 100
end turn
```

**Expected:**
- Coalition declaration popup appears (CanvasLayer 100)
- Shows coalition members, leader, casus belli
- [Continue] button dismisses
- Diplomatic ledger shows active coalition
- Coalition nations now at WAR with France

#### DP5D. Coalition dissolution

```
# Win battles against coalition members, reduce threat
# Or wait for war exhaustion
end turn
end turn
end turn
end turn
end turn
```

**Expected:** Coalition dissolves when conditions met (war exhaustion, threat reduction). Notification confirms dissolution. Nations may negotiate separate peace.

---

### DP6. Vassal Management

#### DP6A. Create vassal via conquest

```
/debug set_relation France Saxony WAR
/debug capture_all Saxony
end turn
```

**Expected:**
- Option to vassalize Saxony appears
- Vassal created with starting loyalty
- Diplomatic ledger Nations tab shows VASSAL state
- Tribute income begins

#### DP6B. Invest in vassal

```
# After DP6A (Saxony is vassal)
invest in Saxony
```

**Expected:**
- Gold deducted
- Vassal loyalty increases
- Message confirms investment

#### DP6C. Vassal rebellion warning

```
/debug set_vassal_loyalty Saxony 20
end turn
```

**Expected:**
- Vassal rebellion popup appears: [Invest][Garrison][Accept]
- Morning dispatch warns about low loyalty
- Choose Invest → gold spent, loyalty increases
- Choose Garrison → troops deployed, loyalty stabilizes
- Choose Accept → risk rebellion next turn

#### DP6D. Vassal rebellion

```
/debug set_vassal_loyalty Saxony 5
end turn
```

**Expected:**
- Vassal rebels
- Saxony breaks free, relation changes
- Cascade check — other vassals may defect
- Notification confirms rebellion

---

### DP7. Talleyrand Sabotage Discovery

#### DP7A. Sabotage occurs on proposal

```
/debug set_talleyrand_trust 30
propose alliance with Austria
end turn
```

**Expected:**
- Low trust increases sabotage chance
- If sabotaged: proposal terms modified without player knowledge
- Discovery may happen later

#### DP7B. Sabotage discovery popup

```
# After sabotage in DP7A, on a later turn
end turn
```

**Expected:**
- Sabotage discovery popup appears: [Confront][Overlook]
- Shows what was changed
- Confront → trust penalty, Talleyrand defends himself
- Overlook → slight trust gain, sabotage continues

---

### DP8. Talleyrand Redemption Event

#### DP8A. Trust drops to redemption threshold

```
/debug set_talleyrand_trust 15
end turn
```

**Expected:**
- Talleyrand redemption popup appears: [Apologize][Replace][Continue]
- Apologize → trust partially restored, Talleyrand grateful
- Replace → new diplomat assigned (if available)
- Continue → risk continued sabotage

---

### DP9. Counter-Offer Flow

#### DP9A. AI generates counter-offer

```
# Propose something with low acceptance
/debug set_relation France Austria NON_AGGRESSION
propose alliance with Austria
end turn
end turn
```

**Expected:**
- If acceptance is 30-49, AI generates counter-offer instead of rejecting
- Incoming proposal popup appears with `is_counter_offer` flag
- Shows modified terms
- [Accept][Reject] buttons (no counter-counter)

---

## Diplomacy Playtest Session D — New Tests Needed (Apr 10, 2026)

These tests verify PL-26/27/28/29 findings and the PL-23/24/25 fixes.

### DP10. Harsher = Lower Odds (PL-23 verification)

```
# Start fresh game, propose armistice with Britain
Talleyrand, propose armistice with Britain
# Note acceptance_estimate (baseline)
# Choose "harsh" via /respond_to_diplomatic_dialogue
# Note acceptance_estimate (should be LOWER)
# Reconsider, re-propose, choose "generous"
# Note acceptance_estimate (should be HIGHER)
```

**Expected:**
- Baseline estimate recorded
- Each "harsh" click: estimate decreases or stays at 0
- Each "generous" click: estimate increases
- `type` field stays `armistice_winning` or `armistice_losing`, never bare `armistice`

### DP11. Diplomatic Ledger shows authority not trust (PL-24 verification)

```
curl -s http://127.0.0.1:8005/diplomatic_ledger | python -m json.tool
```

**Expected:**
- `talleyrand` section has `authority` (number) and `authority_label` (string)
- No `trust` field or `"Wary"` label anywhere in talleyrand section

### DP12. Insist on original costs authority (PL-23 verification)

```
# Set authority low to increase pushback chance
/debug set_authority 30
# Propose armistice, click harsh twice to trigger pushback
Talleyrand, propose armistice with Britain
# harsh → harsh → if pushback_confirm appears:
# Choose "insist on original"
# Check /authority_status — should decrease by exactly 3
```

**Expected:**
- Pushback fires as `pushback_confirm` dialogue type
- "Insist on original" option present with "[Authority -3]" description
- Authority decreases by exactly 3 after insisting

### DP13. Sabotage popup uses authority keys (PL-24 verification)

```
# Trigger sabotage discovery (probabilistic — may need multiple proposals at low authority)
# Check diplomatic_sabotage field in response
```

**Expected:**
- Contains `authority_bonus_if_confronted` and `authority_penalty_if_overlooked`
- Does NOT contain `trust_penalty_if_confronted` or `trust_bonus_if_overlooked`

### DP14. Save/load preserves authority (PL-24 verification)

```
/debug set_authority 65
curl -X POST http://127.0.0.1:8005/save -d '{"save_name": "test_auth"}'
/debug set_authority 40
curl -X POST http://127.0.0.1:8005/load -d '{"filename": "test_auth.json"}'
curl http://127.0.0.1:8005/authority_status
```

**Expected:**
- Authority after load matches pre-save value (65), not the modified value (40)

### DP15. AI proposal spam rate (PL-27 investigation)

```
# Play 10 turns, count how many AI proposals arrive
# Track: which nations propose, what types, how often after rejection
```

**Expected (ideal):**
- No more than 1 AI proposal per 2-3 turns
- Rejected proposals have 3+ turn cooldown before same nation re-proposes
- Player can at minimum check status while proposal is pending
- Currently FAILS — proposals arrive nearly every turn and block all commands

### DP16. Defeat warning before game over (PL-28 investigation)

```
# Play aggressively, lose territory
# Track region count each turn
# Note: is there any warning before "The war is over"?
```

**Expected (ideal):**
- Warning notification when France controls ≤ 4 regions (1 above defeat threshold?)
- Morning dispatch mentions critical territory loss
- Currently FAILS — no warning, sudden "The war is over"

### DP17. Combat winnable scenario (PL-26 investigation)

```
# Test if player can win battles under any conditions:
# 1. Ney (aggressive) vs weaker enemy on plains (no terrain bonus)
# 2. Multi-marshal coordination (Ney + Davout attacking same target)
# 3. Bombardment + attack combo
# 4. Defensive victory (let enemy attack fortified Davout)
```

**Expected (ideal):**
- At least some attack configurations should produce attacker victories
- Player should have a viable combat strategy, not just "throw troops and lose"
- Currently UNCLEAR — no attacker victories observed in 2 full playtests

