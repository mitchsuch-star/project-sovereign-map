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
/debug set_location Wellington Rhine
/debug freeze Wellington

Ney, scout Belgium          # 3 AP left
Davout, scout Lyon           # 2 AP left
Grouchy, scout Waterloo      # 1 AP left

Ney, march to Rhine
```
**Expected:** "Not enough actions! Need 2, have 1."

### 1B. Full AP works

```
# Fresh turn (4 AP)
Ney, march to Rhine
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

Ney, march to Rhine
```
**Expected:** Ney auto-attacks Wellington (72k vs 50k, ratio >= 0.7). No popup. If wins, continues to Rhine.

### 2B. Aggressive (Ney) -- bad odds -> popup

```
/debug set_location Ney Paris
/debug set_strength Ney 30000
/debug set_strength Wellington 100000

Ney, march to Rhine
```
**Expected:** Blocked path popup with options: attack, go_around, hold_position, cancel_order.

- Test attack: Ney attacks (bad odds)
- Test go_around: Ney reroutes (Paris->Lyon->Rhine)
- Test hold_position: Ney stops, order paused (-3 trust if mid-march)
- Test cancel_order: Order cancelled

### 2C. Cautious (Davout) -- always asks

```
/debug set_location Davout Paris
/debug set_strength Davout 72000

Davout, march to Rhine
```
**Expected:** Blocked path popup EVEN with good odds (cautious always asks).

### 2D. Literal (Grouchy) -- silent reroute -- PASS

```
/debug set_location Grouchy Paris

Grouchy, march to Rhine
```
**Expected:** NO popup. Grouchy silently reroutes around Belgium (Paris->Lyon->Rhine). Message mentions alternate path.

### 2E. First-step cancel has 0 trust penalty

```
/debug set_location Ney Paris
/debug set_strength Wellington 100000

Ney, march to Rhine
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
Ney, march to Rhine
# End turn so Ney moves
end turn
# Next turn -- if Ney is within 2 regions of a battle, cannon fire triggers
```
**Note:** Cannon fire requires a battle to happen within 2 regions during strategic execution. Hard to trigger deterministically. Alternative: check the log for cannon_fire interrupt type.

### 3B. Literal (Grouchy) -- NEVER interrupts

```
/debug set_location Grouchy Lyon

Grouchy, march to Rhine
end turn
```
**Expected:** Grouchy continues march silently. No cannon fire popup EVER (The Grouchy Moment).

---

## Test 4: PURSUE Completion

### Setup

```
/debug set_location Ney Belgium
/debug set_location Wellington Rhine
/debug freeze Wellington
/debug set_strength Ney 72000
/debug set_strength Wellington 40000
```

### 4A. PURSUE completes after combat

```
Ney, pursue Wellington
end turn
# Ney reaches Rhine, fights Wellington
```
**Expected:** Combat happens. Order shows "completed" regardless of outcome (win/lose/stalemate). NO stalemate popup.

### 4B. Cautious/Literal complete on arrival without attacking

```
/debug set_location Davout Belgium
/debug set_location Wellington Rhine

Davout, pursue Wellington
end turn
```
**Expected:** Davout arrives at Rhine. Message: "Davout has located Wellington at Rhine and awaits orders." Order completed. No auto-attack (cautious).

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
Ney, move to Rhine
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
Ney, march to Rhine
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
| `/debug ai_turn <nation>` | Force AI turn |
| `/debug list_marshals` | Show all positions |
