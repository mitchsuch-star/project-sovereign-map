# Ink & Iron: Systems Reference

Consolidated reference for all game systems. Read when modifying related code.

---

## Table of Contents

1. [Combat System](#1-combat-system)
2. [Disobedience & Trust](#2-disobedience--trust)
3. [Marshal State Machine](#3-marshal-state-machine)
4. [Strategic Commands](#4-strategic-commands)
5. [LLM Integration](#5-llm-integration)
6. [Cavalry Limits](#6-cavalry-limits)
7. [Redemption System](#7-redemption-system)

---

## 1. Combat System

### Single-Source-of-Truth Pattern (CRITICAL!)

Combat modifiers are calculated in ONE place only. This prevents bugs where bonuses apply twice.

```
marshal.py                          combat.py
-----------------------------------  ---------------------------------
get_attack_modifier()               Uses marshal's modifier
  - Personality base bonus          Generates messages about bonuses
  - Stance modifier                 Handles state changes (drill consumed)
  - Drill/shock bonus               DOES NOT recalculate modifiers
  - Returns final multiplier

get_defense_modifier()              Uses marshal's modifier
  - Personality base bonus          Generates messages about bonuses
  - Stance modifier                 DOES NOT recalculate modifiers
  - Fortify bonus
  - Outnumbered bonus (Davout)
  - Returns final multiplier
```

### Attack Modifier Formula

From `marshal.py` `get_attack_modifier()`:

```python
modifier = 1.0

# Stance modifiers
if stance == AGGRESSIVE:
    modifier *= 1.15  # +15%
elif stance == DEFENSIVE:
    modifier *= 0.90  # -10%

# Drill/shock bonus
if shock_bonus > 0:
    modifier *= (1.0 + shock_bonus * 0.10)  # +20% if shock_bonus=2

# Strategic combat bonus (if any)
if strategic_combat_bonus > 0:
    modifier *= (1.0 + strategic_combat_bonus / 100.0)

# Personality modifiers (see get_attack_modifier_for_personality)
# - Aggressive: +15% base, +5% if aggressive stance, +5% if drill
# - Cautious: -5% if aggressive stance, -10% if bad odds
# - Literal: no special attack modifiers

# Recklessness bonus (aggressive + cavalry only)
modifier *= (1.0 + recklessness_attack_bonus)

# Exhaustion penalty (multiple attacks per turn)
modifier *= (1.0 - exhaustion_penalty)

return modifier
```

### Defense Modifier Formula

From `marshal.py` `get_defense_modifier()`:

```python
modifier = 1.0

# Stance modifiers
if stance == DEFENSIVE:
    modifier *= 1.15  # +15%
elif stance == AGGRESSIVE:
    modifier *= 0.90  # -10%

# Fortify bonus (stored as decimal)
if fortify_bonus > 0:
    modifier *= (1.0 + fortify_bonus)  # 0.16 = +16%

# Drilling penalty (caught drilling = vulnerable)
if drilling or drilling_locked:
    modifier *= 0.75  # -25%

# Personality modifiers (see get_defense_modifier_for_personality)
# - Aggressive: -5% if aggressive stance, -5% off defensive bonus
# - Cautious: +5% if defensive stance, +10% if outnumbered
# - Literal: +15% if holding position

# Recklessness penalty (aggressive + cavalry only)
modifier *= (1.0 - recklessness_defense_penalty)

return modifier
```

### Combat Modifier Tables by Personality

#### NEY (Aggressive) -- "Bravest of the Brave"

| Modifier | Value | Condition | Code Reference |
|----------|-------|-----------|----------------|
| Base attack bonus | +15% | Always | `NEY_MODIFIERS["base_attack_bonus"] = 0.15` |
| Aggressive stance attack | +5% additional | `stance == AGGRESSIVE` | `NEY_MODIFIERS["aggressive_stance_attack_bonus"] = 0.05` |
| **Total aggressive stance attack** | **+20%** | Combined | |
| Aggressive stance defense | -5% | `stance == AGGRESSIVE` | `NEY_MODIFIERS["aggressive_stance_defense_penalty"] = 0.05` |
| Defensive stance defense | +10% only | `stance == DEFENSIVE` | `NEY_MODIFIERS["defensive_stance_defense_penalty"] = 0.05` (reduces from +15% to +10%) |
| Drill synergy | +5% additional | `shock_bonus > 0` | `NEY_MODIFIERS["drill_shock_bonus"] = 0.05` |
| Max fortify cap | 10% | Impatient | `NEY_MODIFIERS["max_fortify_bonus"] = 0.10` |

**Behavioral Traits:**
- Objects to defensive orders (defend, wait, hold, retreat, fortify)
- Objects less if outnumbered 2:1+ AND morale <=40%
- Trust bonus for attack orders, penalty for prolonged defense

#### DAVOUT (Cautious) -- "Iron Marshal"

| Modifier | Value | Condition | Code Reference |
|----------|-------|-----------|----------------|
| Defensive stance defense | +5% additional | `stance == DEFENSIVE` | `DAVOUT_MODIFIERS["defensive_stance_defense_bonus"] = 0.05` |
| **Total defensive stance defense** | **+20%** | Combined with base +15% | |
| Outnumbered defense | +10% | `strength < attacker_strength` | `DAVOUT_MODIFIERS["outnumbered_defense_bonus"] = 0.10` |
| Aggressive stance attack | -5% | `stance == AGGRESSIVE` | `DAVOUT_MODIFIERS["aggressive_stance_attack_penalty"] = 0.05` |
| Bad odds attack | -10% | `strength_ratio < 1.0` | `DAVOUT_MODIFIERS["bad_odds_attack_penalty"] = 0.10` |
| Fortify rate | +3%/turn | Instead of +2% | `DAVOUT_MODIFIERS["fortify_rate_bonus"] = 0.01` |
| Max fortify cap | 20% | Patient defender | `DAVOUT_MODIFIERS["max_fortify_bonus"] = 0.20` |
| Instant fortify | +5% | First fortify turn | `DAVOUT_MODIFIERS["instant_fortify_bonus"] = 0.05` |
| Scout range | +1 region | Extended recon | `DAVOUT_MODIFIERS["scout_range_bonus"] = 1` |

**Special Ability: Counter-Punch**
- **Trigger:** After successfully defending against an attack
- **Effect:** `counter_punch_available = True`, grants one FREE attack
- **Duration:** Must be used within 1 turn or expires
- **Implementation:** Set in `combat.py`, checked in `executor.py`

**Behavioral Traits:**
- Objects to risky attacks (outnumbered, bad odds)
- Trust bonus for defensive actions
- Penalty for attacking at bad odds

#### GROUCHY (Literal)

| Modifier | Value | Condition | Code Reference |
|----------|-------|-----------|----------------|
| Hold position defense | +15% | `holding_position == True` | `GROUCHY_MODIFIERS["hold_position_defense_bonus"] = 0.15` |

**Special Ability: Immovable**
- **Trigger:** Player issues `hold` command
- **Effect:** Sets `holding_position = True`, `hold_region = current_location`
- **Bonus:** +15% defense while holding
- **Breaks when:** Marshal moves or attacks
- **Implementation:** `marshal.py` fields, `executor.py` hold handler

**Behavioral Traits:**
- Never improvises or takes initiative
- Follows orders exactly (the "Grouchy Moment")
- May require clarification for vague orders
- Strategic commands cost 1 action (not 2)
- +15% effectiveness for explicit, unambiguous orders

#### BALANCED Personality

**Current marshals:** None (placeholder for future)

- No special bonuses or penalties
- Uses baseline stance modifiers only
- Standard fortify rate (+2%/turn, max 15%)
- Moderate objection thresholds; will object to suicidal orders (3:1+ odds)

#### LOYAL Personality

**Current marshals:** None (placeholder for future, e.g., Lannes)

- Extreme obedience (only objects at 5:1+ odds)
- Always obeys on INSIST
- Potential: Inspiring Presence affects nearby marshals

### Fortify Mechanics

- Stored as decimal: `0.16` = 16%
- Display: `int(value * 100)` = "16%"
- Rate: +2%/turn standard, +3%/turn for cautious (Davout)
- Max: 15% standard, 10% for aggressive (Ney), 20% for cautious (Davout)
- Instant fortify: +5% on first turn for cautious (Davout)

### Drill/Shock Bonus

- 2-turn drill process: `drilling` (turn 1) -> `drilling_locked` (turn 2) -> `shock_bonus` set
- Shock bonus: +20% attack modifier when consumed (shock_bonus=2, * 0.10 = +20%)
- Consumed after first attack (cleared AFTER `get_attack_modifier()` reads it)
- Drilling penalty: -25% defense while drilling or drilling_locked

### Example Calculations

**Ney (aggressive cavalry) in aggressive stance with drill bonus:**
```
Base: 1.0
x 1.15 (aggressive stance)
x 1.20 (drill shock_bonus=2)
x 1.15 (aggressive personality base)
x 1.05 (aggressive stance personality bonus)
x 1.05 (drill synergy personality bonus)
= ~1.81x attack modifier (+81%)
```

**Davout (cautious infantry) in defensive stance, outnumbered, fortified 16%:**
```
Base: 1.0
x 1.15 (defensive stance)
x 1.16 (fortify bonus)
x 1.05 (defensive stance personality bonus)
x 1.10 (outnumbered personality bonus)
= ~1.54x defense modifier (+54%)
```

### Source File Reference (Combat)

| Mechanic | Primary File | Secondary Files |
|----------|--------------|-----------------|
| Personality modifiers | `personality_modifiers.py` | `marshal.py` (applies them) |
| Objection triggers | `personality.py` | `disobedience.py` |
| Counter-Punch | `combat.py` (sets flag) | `executor.py` (uses it) |
| Immovable | `marshal.py` | `executor.py` (hold command) |
| Recklessness | `marshal.py` | `executor.py`, `world_state.py` |
| Cavalry limits | `world_state.py` | `marshal.py` (counters) |
| Combat calculation | `combat.py` | `marshal.py` (modifiers) |

---

## 2. Disobedience & Trust

### System Overview

The disobedience system creates dynamic tension between player orders and marshal personalities. Marshals don't just blindly follow orders -- they evaluate them based on their personality, trust in the player, and situational context.

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| DisobedienceSystem | `disobedience.py` | Main orchestrator, objection creation/handling |
| Severity Calculator | `severity.py` | Calculates objection severity (0.0-0.95) |
| Personality System | `personality.py` | Defines personality triggers and base severities |
| Trust System | `trust.py` | Manages trust values and obedience probability |
| Authority Tracker | `authority.py` | Tracks player authority to prevent sycophancy |
| Vindication Tracker | `vindication.py` | Tracks who was proven right/wrong |

### Order Processing Flow

```
1. Player issues command
   |
2. CommandExecutor calls DisobedienceSystem.evaluate_order()
   |
3. analyze_order_situation() determines situation type
   |
4. get_base_severity() gets personality-specific base severity
   |
5. Apply multiplicative modifiers:
   - Trust modifier (0.7 to 1.6x)
   - Vindication modifier (0.85 to 1.15x)
   - Performance modifier (0.85 to 1.15x)
   - Override modifier (1.0 to 1.3x)
   - Authority modifier (1.0 to 1.25x)
   |
6. Apply random variance (tiered by severity level)
   |
7. Cap at 0.95
   |
8. Determine objection type:
   - < 0.20: No objection -> execute order normally
   - 0.20-0.49: Mild objection -> auto-resolve with grumbling
   - 0.50-0.95: Major objection -> present player with choices
```

### Severity Thresholds

| Severity | Type | Result |
|----------|------|--------|
| 0.00 - 0.19 | None | Marshal obeys without comment |
| 0.20 - 0.49 | Mild | Marshal grumbles but obeys |
| 0.50 - 0.95 | Major | Player must choose: Trust, Insist, or Compromise |

### Modifier Application

All modifiers are **multiplicative**, applied in this order:

1. **Trust Modifier** - Based on marshal's trust in player
2. **Vindication Modifier** - Based on track record of being right
3. **Performance Modifier** - Based on recent battle outcomes
4. **Override Modifier** - Based on how often this marshal is overridden
5. **Authority Modifier** - Based on player's overall authority

### Variance System

Random variance is applied based on severity level:

| Severity Range | Variance | Purpose |
|----------------|----------|---------|
| 0.00 - 0.19 | None | Below threshold, no variance needed |
| 0.20 - 0.34 | +/-3% | Predictable for mild objections |
| 0.35 - 0.59 | +/-8% | Moderate variance |
| 0.60+ | +/-12% | High unpredictability for major decisions |

### Personality Triggers

#### AGGRESSIVE (Ney, Blucher, Murat)

| Trigger | Severity | Type | Description |
|---------|----------|------|-------------|
| `defend` | 0.60 | Major | Ordered to defend |
| `wait` | 0.50 | Major | Ordered to wait/hold |
| `wait_with_enemy_nearby` | 0.65 | Major | Wait when enemy adjacent |
| `retreat` | 0.70 | Major | Ordered to retreat |
| `hold_position` | 0.60 | Major | Hold position (alias for defend) |
| `fortify` | 0.55 | Major | Dig trenches |
| `drill_enemy_nearby` | 0.45 | Mild | Drill when enemy is close |
| `defensive_stance` | 0.55 | Major | Adopt defensive stance |
| `neutral_stance_from_aggressive` | 0.35 | Mild | Stand down from aggressive |

#### CAUTIOUS (Davout, Wellington)

| Trigger | Severity | Type | Description |
|---------|----------|------|-------------|
| `certain_death` | 0.80 | Major | Attack at 5:1+ odds |
| `attack_outnumbered_3to1` | 0.70 | Major | Attack at 3:1 odds |
| `attack_outnumbered_2to1` | 0.60 | Major | Attack at 2:1 odds |
| `attack_outnumbered_1_5to1` | 0.50 | Major | Attack at 1.5:1 odds |
| `attack_without_intel` | 0.55 | Major | Attack unknown enemy (TODO) |
| `attack_fortified` | 0.60 | Major | Attack fortified position |
| `forced_march` | 0.45 | Mild | Forced march order |
| `aggressive_stance` | 0.40 | Mild | Adopt aggressive stance |
| `aggressive_stance_outnumbered` | 0.60 | Major | Aggressive stance when outnumbered |

#### LITERAL (Grouchy)

| Trigger | Severity | Type | Description |
|---------|----------|------|-------------|
| `ambiguous_order` | 0.50 | Major | Unclear command (TODO: Phase 3) |
| `contradictory_orders` | 0.60 | Major | Conflicts with previous order (TODO) |
| `change_of_plans` | 0.35 | Mild | Frequent order changes (TODO) |

#### BALANCED (Soult)

| Trigger | Severity | Type | Description |
|---------|----------|------|-------------|
| `certain_death` | 0.70 | Major | Attack at 5:1+ odds |
| `expose_capital` | 0.55 | Major | Leave capital undefended |
| `suicidal_order` | 0.65 | Major | Certain death order (TODO: expand) |
| `attack_outnumbered_3to1` | 0.60 | Major | Very bad odds |
| `abandon_allies` | 0.50 | Major | Leave ally exposed (TODO) |

#### LOYAL (Lannes)

| Trigger | Severity | Type | Description |
|---------|----------|------|-------------|
| `suicidal_order` | 0.40 | Mild | Even suicidal orders = mild |
| `certain_death` | 0.55 | Major | Even loyal marshals object to 5:1+ |
| `betray_emperor` | 0.95 | Major | Orders harming Napoleon (TODO) |
| `expose_capital` | 0.35 | Mild | Trusts Emperor's judgment |

### Quick Reference: Who Objects to What

| Order | Ney (Aggressive) | Davout (Cautious) | Grouchy (Literal) |
|-------|------------------|-------------------|-------------------|
| Attack | Happy | Objects if outnumbered | Obeys |
| Defend | **Objects** (0.60) | Happy | Obeys |
| Hold | Mild objection (0.45) | Happy | Obeys |
| Wait | **Objects** (0.50-0.65) | Happy | Obeys |
| Fortify | **Objects** (0.55) | Happy | Obeys |
| Drill | Mild if enemy nearby (0.45) | Happy | Obeys |
| Retreat | **Strongly objects** (0.70) | Happy if losing | Obeys |
| Aggressive Stance | Happy | Objects (mild/major) | Obeys |
| Defensive Stance | **Objects** (0.55) | Happy | Obeys |
| Move | Usually fine | Usually fine | Obeys |

### Trust Change Values

| Choice | Trust Change | Authority Change |
|--------|--------------|------------------|
| **Trust** | +12 | -3 |
| **Insist (obeys)** | -10 | +2 |
| **Insist (disobeys)** | -15 | +0 |
| **Compromise** | +3 | -1 |

### Trust -> Severity Multiplier (4-Tier Steep Curve)

| Trust Level | Range | Multiplier | Effect |
|-------------|-------|------------|--------|
| Very High | 80+ | 0.7x | Much less likely to object |
| Neutral | 40-79 | 1.0x | Baseline |
| Low | 20-39 | 1.3x | More likely to object |
| Very Low | <20 | 1.6x | Much more likely to object |

### Trust -> Obedience Chance (when player insists)

| Trust Level | Range | Obedience Chance | Description |
|-------------|-------|------------------|-------------|
| Loyal | 80+ | 100% | Guaranteed obedience |
| Reliable | 60-79 | 90-99.5% | Very likely to obey |
| Questioning | 40-59 | 70-89.5% | May question orders |
| Strained | 20-39 | 50-69.5% | Significant disobey risk |
| Broken | <20 | 30-49.5% | Very likely to refuse |

### Vindication System

#### Vindication Score Effects (3-Tier System)

| Score | Range | Multiplier | Meaning |
|-------|-------|------------|---------|
| Proven Wrong | <=-2 | 0.85x | Marshal was wrong, less bold |
| Neutral | -1 to +2 | 1.0x | No strong track record |
| Proven Right | >=+3 | 1.15x | Marshal was right, bolder |

#### Score Changes

| Choice | Battle Outcome | Vindication Change |
|--------|----------------|-------------------|
| Trust | Victory | +1 (marshal was right) |
| Trust | Defeat | -1 (marshal was wrong) |
| Insist | Victory | -1 (marshal was wrong to object) |
| Insist | Defeat | +1 (marshal was right) |
| Compromise | Any | 0 (shared responsibility) |

### Authority System

#### Authority Thresholds

| Authority | Level | Severity Modifier | Trust Gain Modifier |
|-----------|-------|-------------------|---------------------|
| 80+ | High | 1.0x | 1.0x |
| 50-79 | Moderate | 1.1x | 0.8x |
| <50 | Low | 1.25x | 0.5x |

#### Authority Changes

| Pattern | Effect | Reason |
|---------|--------|--------|
| Always Trust | -5 per response | Sycophancy detected |
| Mostly Trust (60-80%) | -2 per response | Leaning too soft |
| Balanced (30-60%) | +1 per response | Good leadership |
| Mostly Insist | +1 (maintain) | Firm leadership |

#### Threshold Events

- **Authority 70**: "Some marshals grow bold, sensing leniency."
- **Authority 50**: "The command structure wavers. Marshals question openly."
- **Authority 30**: "Your authority has collapsed. Expect frequent defiance."

### Compromise Rules

#### Basic Action Compromises

| Player Orders | Marshal Wants | Compromise |
|---------------|---------------|------------|
| Attack | Defend | **Move** (approach but don't engage) |
| Defend | Attack | **Move** (advance cautiously) |
| Attack | Move | **Move** |
| Move | Attack | **Move** |
| Move | Defend | **Defend** |
| Defend | Move | **Move** |

#### Tactical Action Compromises

| Player Orders | Marshal Wants | Compromise |
|---------------|---------------|------------|
| Fortify | Attack | **Defend** (hold but stay mobile) |
| Fortify | Move | **Defend** |
| Fortify | Drill | **Drill** (active preparation) |
| Attack | Fortify | **Defend** |
| Drill | Attack | **Defend** |
| Drill | Move | **Defend** |
| Drill | Defend | **Defend** |
| Attack | Drill | **Defend** |

#### Retreat Compromises

| Player Orders | Marshal Wants | Compromise |
|---------------|---------------|------------|
| Retreat | Defend | **Defend** (hold, don't flee) |
| Retreat | Attack | **Defend** (neither attack nor flee) |
| Defend | Retreat | **Defend** |
| Attack | Retreat | **Defend** |

#### Stance Compromises

| Player Orders | Marshal Wants | Compromise |
|---------------|---------------|------------|
| Defensive Stance | Aggressive Stance | **Neutral Stance** |
| Aggressive Stance | Defensive Stance | **Neutral Stance** |

### Alternative Generation by Personality

#### AGGRESSIVE
When ordered to defend/wait/fortify:
- If enemy in range: Suggest **Attack**
- If no enemy but can move toward one: Suggest **Move**
- If neither: Suggest **Defend** (fallback)

When ordered to fortify:
- If enemy in range: Suggest **Attack**
- Otherwise: Suggest **Drill** (at least builds shock bonus)

#### CAUTIOUS (Context-Aware)
When ordered to attack:
- If 3:1+ outnumbered: Suggest **Retreat** (too dangerous to hold)
- If 2:1 outnumbered: Suggest **Fortify** (dig in for maximum defense)
- If 1.5:1 outnumbered: Suggest **Defensive Stance** (careful posture)
- Otherwise: Suggest **Defend**

| Odds Against | Suggested Alternative | Rationale |
|--------------|----------------------|-----------|
| 3:1+ outnumbered | **RETREAT** | Too dangerous to hold |
| 2:1 outnumbered | **FORTIFY** | Dig in for maximum defense |
| 1.5:1 outnumbered | **DEFENSIVE STANCE** | Careful posture |

#### BALANCED/LITERAL/LOYAL
- Attack ordered: Suggest **Defend**
- Defend ordered (with enemy nearby): Suggest **Attack**
- Otherwise: Follow default fallback

### Strategic Command Objections (Phase M)

Strategic commands (HOLD, MOVE_TO, PURSUE, SUPPORT) have their own objection system, separate from tactical objections. These fire at command **issuance**, not during execution.

#### Strategic Objection Triggers

| Personality | Strategic Type | Trigger | Base Severity | Compromise |
|-------------|---------------|---------|---------------|------------|
| Aggressive (Ney) | HOLD | No enemies adjacent to hold position | 0.72 | Timed HOLD (3 turns) |
| Cautious (Davout) | PURSUE | Target ratio < 1.2 (bad odds) | 0.68 | Auto-cancel below ratio |
| Cautious (Davout) | MOVE_TO | Path crosses enemy-occupied region | 0.65 | Safe route if available |
| Cautious (Davout) | HOLD (distant) | Path crosses enemy-occupied region | 0.65 | Safe route if available |
| Cautious (Davout) | SUPPORT | Path crosses enemy-occupied region | 0.65 | Safe route if available |
| Literal (Grouchy) | Any | **Never objects** | N/A | Uses clarification popup for vague orders |

#### Strategic vs Tactical Objections

| Aspect | Tactical | Strategic |
|--------|----------|-----------|
| When | Action execution | Command issuance |
| Storage | `world.pending_objection` | `world.pending_strategic_objection` |
| Trigger | Personality vs action type | Personality vs situation |
| Recovery bypass | No objections during retreat_recovery | No objections during retreat_recovery |

#### Dangerous Path Objection (Cautious Only)

Cautious marshals (like Davout) object to any strategic command that requires marching through enemy-occupied territory:

1. **MOVE_TO through danger** - "That path passes through [enemy region]. We would be walking into danger, Sire."
2. **HOLD (distant) through danger** - "To hold [target], we must march through [enemy region]. A dangerous gambit, Sire."
3. **SUPPORT through danger** - "To reach [ally], we must pass through [enemy region]. That path invites disaster, Sire."

If a safe path exists (no longer than 2x the direct path), compromise offers "Accept: Safe route" option.

### Disobedience Triggers by Action

| Action | Aggressive | Cautious | Literal |
|--------|------------|----------|---------|
| `defend` | 0.60 (Major) | No trigger | No trigger |
| `hold` | 0.45 (Mild) | No trigger | No trigger |
| `wait` | 0.50 (Major) | No trigger | No trigger |
| `wait` (enemy nearby) | 0.65 (Major) | No trigger | No trigger |

### Configuration Constants

| Constant | Value | Location |
|----------|-------|----------|
| MAX_MAJOR_OBJECTIONS_PER_TURN | 2 | `disobedience.py:25` |
| SEVERITY_CAP | 0.95 | `severity.py:94` |
| NO_OBJECTION_THRESHOLD | 0.20 | `disobedience.py:403` |
| MILD_OBJECTION_THRESHOLD | 0.50 | `disobedience.py:407` |
| VINDICATION_MIN/MAX | -5/+5 | `vindication.py` |
| TRUST_MIN/MAX | 0/100 | `trust.py` |
| AUTHORITY_MIN/MAX | 0/100 | `authority.py` |

### Known Limitations

**Phase 3 Features (Not Yet Implemented):**
1. **Ambiguous Order Detection** - Requires LLM to detect unclear commands
2. **Contradictory Orders** - Requires order history tracking
3. **Frequent Order Changes** - Requires order history tracking
4. **Fog of War** - `attack_without_intel` cannot trigger
5. **Ally Abandonment** - Requires ally position tracking
6. **Political Intrigue** - `betray_emperor` cannot trigger
7. **Suicidal Order Expansion** - Currently only checks ratios

**Design Decisions:**
1. **Variance can cross thresholds** - A 0.22 severity can become 0.19 with bad variance roll. This is intentional to avoid predictability.
2. **Compromise not always available** - If no compromise rule exists for an action pair, the compromise button is hidden. This is by design.
3. **Authority bonus ineffective at high trust** - High-trust marshals already have 100% obedience, so authority modifier has no effect. This is a known limitation.
4. **LITERAL personality rarely triggers** - Most LITERAL triggers require Phase 3 features.

---

## 3. Marshal State Machine

### States (Multiple Can Be Active Simultaneously)

```
+-------------+     +-------------+     +-------------+     +-------------+
|   STANCE    |     |  TACTICAL   |     |  RECOVERY   |     |   COMBAT    |
|  (1 of 3)   |     |  (flags)    |     |  (blocking) |     |  (temp)     |
+-------------+     +-------------+     +-------------+     +-------------+
| AGGRESSIVE  |     | fortified   |     | retreat_    |     | broken      |
| NEUTRAL     |     | drilling    |     | recovery=N  |     | (morale<25%)|
| DEFENSIVE   |     | drilling_   |     | (blocks     |     |             |
|             |     |   locked    |     |  attack,    |     | Triggers    |
| Affects:    |     | holding_    |     |  fortify,   |     | forced      |
| -attack mod |     |   position  |     |  drill,     |     | retreat     |
| -defense mod|     |             |     |  scout,     |     |             |
|             |     | Affects:    |     |  aggr.stance|     |             |
|             |     | -defense    |     |             |     |             |
|             |     | -attack     |     | Decrements  |     |             |
|             |     | -mobility   |     | each turn   |     |             |
+-------------+     +-------------+     +-------------+     +-------------+
```

### State Interactions
- `retreat_recovery` BLOCKS: fortify, drill, attack, scout, aggressive_stance
- `drilling_locked` BLOCKS: attack, move (until drill completes)
- `fortified` + move = lose fortify bonus
- `broken` -> forced retreat -> `retreat_recovery=3`

### State Tracking Fields (from `marshal.py`)

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `personality` | str | required | Determines objection triggers and modifiers |
| `cavalry` | bool | False | Enables cavalry mechanics |
| `movement_range` | int | 1 | Attack range (1=infantry, 2=cavalry) |
| `stance` | Stance | NEUTRAL | Current stance |
| `drilling` | bool | False | In turn 1 of drill |
| `drilling_locked` | bool | False | In turn 2 of drill |
| `shock_bonus` | int | 0 | Attack bonus from drill (2 = +20%) |
| `fortified` | bool | False | Currently fortified |
| `defense_bonus` | float | 0 | Fortify percentage as decimal |
| `counter_punch_available` | bool | False | Free attack available (cautious) |
| `counter_punch_turns` | int | 0 | Turns remaining to use |
| `holding_position` | bool | False | Immovable active (literal) |
| `hold_region` | str | "" | Where holding |
| `recklessness` | int | 0 | Recklessness level 0-4 |
| `turns_in_defensive_stance` | int | 0 | Cavalry limit counter |
| `turns_fortified` | int | 0 | Cavalry limit counter |

### Retreat and Broken State

When morale drops to 25% in combat, the marshal is "broken":
- Forced retreat triggers automatically (bypasses objection system)
- `retreat_recovery = 3` (decrements each turn)
- Blocked actions during recovery: attack, fortify, drill, scout, aggressive_stance
- Allowed actions during recovery: move, wait, recruit, defend, defensive_stance, neutral_stance
- No objections during recovery -- marshals are demoralized and compliant

### Ally Covers Retreat

```
retreated_this_turn: True if marshal retreated THIS turn

When attacked while retreated_this_turn=True:
  1. Check for covering ally (same region, same nation, not retreated)
  2. If ally exists -> ALLY fights instead (swapped defender)
  3. If no ally -> EXPOSED (+30% AI targeting bonus)

Cleared at: START of next player turn (protection lasts enemy phase)
Set by: Forced retreat, manual retreat
```

### Recklessness System (Aggressive + Cavalry)

#### Prerequisites

The Recklessness System only activates when BOTH conditions are met:
- `personality == "aggressive"`
- `cavalry == True`

**Property check:** `marshal.is_reckless_cavalry` (computed property in `marshal.py`)

#### Current Marshals with Recklessness

- **Ney** (France) - aggressive + cavalry

#### Recklessness Levels

| Level | Attack Bonus | Defense Penalty | Stance Restrictions | Special |
|-------|--------------|-----------------|---------------------|---------|
| 0 | - | - | None | Normal combat |
| 1 | +5% | - | None | Can use `charge` command |
| 2 | +10% | -5% | Cannot use DEFENSIVE stance | Warning message |
| 3 | +15% | -10% | Cannot use DEFENSIVE or NEUTRAL | Popup before attack |
| 4+ | +20% | -15% | Cannot use DEFENSIVE or NEUTRAL | Auto-charge at turn start |

#### How Recklessness Changes

**Increases (+1):**
- Win a battle AS ATTACKER
- Capped at level 4

**Resets to 0:**
- Lose any battle (as attacker or defender)
- Execute Glorious Charge

#### Glorious Charge (Level 3+)

When attacking at recklessness 3+, player receives popup:

| Choice | Effect |
|--------|--------|
| "Let him charge!" | 2x casualties both sides, -20 enemy morale, recklessness resets to 0 |
| "Restrain attack" | Normal attack, -5 trust, recklessness follows normal rules |

**Terrain blocking (Phase 6.1.B):** If the target is on charge-blocked terrain (mountains/forest/urban):
1. Executor scans for alternative enemies within cavalry range (2 regions) on allowed terrain
2. Alternatives sorted by `(distance, strength)` — nearest first, weakest as tiebreaker
3. If alternatives found: redirect popup offers best alternative target (`pending_glorious_charge=True, charge_redirected=True`)
4. If no alternatives: falls through to normal attack (no charge bonus), recklessness preserved
5. Recklessness does NOT reset when terrain blocks the charge

#### Auto-Charge (Level 4)

At turn start, before player input:
1. Check for enemies in range (2 regions for cavalry)
2. If enemy found -> Attack weakest enemy automatically (free action)
3. If no enemy -> March toward nearest enemy
4. If movement blocked -> "strains at the reins" message, stays at level 4
5. If target on charge-blocked terrain -> downgrade to normal attack, recklessness preserved (does NOT reset)

#### AI Behavior

AI marshals at recklessness 3+ always charge (no popup decision needed).

#### Code Locations (Recklessness)

| Functionality | File | Key Functions |
|--------------|------|---------------|
| Recklessness state | `marshal.py` | `is_reckless_cavalry`, `_get_recklessness_attack_bonus()` |
| Combat bonuses | `marshal.py` | `get_attack_modifier()`, `get_defense_modifier()` |
| Stance restrictions | `marshal.py` | `can_use_stance()` |
| Glorious Charge | `executor.py` | `_execute_charge()`, `_execute_restrain()` |
| Charge redirect | `executor.py` | Charge terrain blocked section (~line 1617) |
| Cavalry terrain msg | `combat.py`, `executor.py`, `main.py`, `main.gd` | Passthrough chain + Godot display |
| Auto-charge | `world_state.py` | `_process_reckless_cavalry_turn_start()` |

---

## 4. Strategic Commands

### Pipeline Overview

```
Player Input ("Ney, march to Belgium")
    |
    v
1. FAST PARSER          llm_client.py:441      Keywords -> action="move"
    |
    v
2. STRATEGIC DETECTION  parser.py:316          detect_strategic_command()
    |                   strategic_parser.py:81  -> returns is_strategic, strategic_type, etc.
    |
    v
3. VALIDATION           validation.py:117      VALID_STRATEGIC_TYPES check
    |
    v
4. EXECUTOR INTERCEPT   executor.py:863        if is_strategic -> _execute_strategic_command()
    |                   executor.py:1984       Creates StrategicOrder
    |                   executor.py:2118       marshal.strategic_order = order
    |                   executor.py:872        _skip_routing = True (bypass tactical)
    |
    v
5. FIRST STEP           executor.py:~2080      Executes first move/action immediately
    |                                          (costs 2 actions, 1 for LITERAL)
    |
    v
6. TURN-END PROCESSING  turn_manager.py:140    StrategicExecutor.process_strategic_orders()
    |                   strategic.py:40        Iterates marshals with active orders
    |                   strategic.py:74        _execute_strategic_turn() per marshal
    |
    v
7. COMMAND HANDLERS     strategic.py:127       _execute_move_to()
                        strategic.py:274       _execute_pursue()
                        strategic.py:398       _execute_hold()
                        strategic.py:573       _execute_support()
```

### Stage 1: Fast Parser (Keyword Detection)

**File:** `backend/ai/llm_client.py`
- **Line 262:** `parse_command()` -- entry point
- **Line 408-442:** Strategic keyword detection in `_parse_with_mock()`
  - "march", "advance", "move to" -> action="move" (MOVE_TO)
  - "pursue", "chase", "hunt" -> action="move" (PURSUE)
  - "reinforce", "support" -> action="move" (SUPPORT)
  - "hold position", "hold the line" -> action="hold" (HOLD)
- **Key:** Fast parser sets `action="move"`. It does NOT set `is_strategic`. That's Stage 2.

### Stage 2: Strategic Detection

**File:** `backend/ai/strategic_parser.py`
- **Line 81:** `detect_strategic_command(text, marshals, regions, world)` -- main entry
- **Line 189:** `_detect_strategic_type(text)` -- classifies: MOVE_TO, PURSUE, HOLD, SUPPORT
- **Line 264:** `_classify_target(target, regions, marshals, world)` -- target_type: region, marshal, battle, generic
- **Line 348:** `_parse_condition(text)` -- parses: until_marshal_arrives, until_marshal_destroyed, max_turns, until_battle_won

**File:** `backend/commands/parser.py`
- **Line 314-326:** Injection block -- calls `detect_strategic_command()` and injects:
  - `result["is_strategic"] = True`
  - `result["strategic_type"]` = "MOVE_TO" | "PURSUE" | "HOLD" | "SUPPORT"
  - `result["target_snapshot_location"]` (for friendly marshal targets)
  - `result["strategic_condition"]` (StrategicCondition dict)
  - `result["attack_on_arrival"]` (bool)
  - `result["command"]["target_type"]` (str)

### Stage 3: Validation

**File:** `backend/ai/validation.py`
- **Line 117:** `VALID_STRATEGIC_TYPES = {"MOVE_TO", "PURSUE", "HOLD", "SUPPORT"}`
- **Line 118-123:** If `is_strategic=True` and `strategic_type` not in valid set -> falls back to tactical (clears `is_strategic`, `strategic_type`)

### Stage 4: Executor Interception

**File:** `backend/commands/executor.py`
- **Line 863-876:** Strategic interception block:
  ```python
  if is_strategic and strategic_type:
      result = self._execute_strategic_command(command, world, game_state)
      _skip_routing = True
  ```
- **Line 1984:** `_execute_strategic_command()` method:
  1. Validates marshal has actions (costs 2, or 1 for LITERAL)
  2. Builds path using personality-aware pathfinding (cautious avoids enemies)
  3. Creates `StrategicOrder` dataclass (line 2118)
  4. Sets `marshal.strategic_order = order` (line 2133)
  5. Executes first step (move or action)
  6. Returns result dict with `strategic_order_set: True`

**Key flags:**
- `_skip_routing` (line 872): Prevents falling through to tactical action routing
- `_strategic_execution` (line 456): When True, skips action cost, objections, override checks
- `_sortie` (line 457): Prevents advancing into conquered region on victory (HOLD sally)

### Stage 5: Turn-End Processing

**File:** `backend/game_logic/turn_manager.py`
- **Line 140-144:** After enemy phase, before `advance_turn()`:
  ```python
  strategic_exec = StrategicExecutor(self.executor)
  strategic_results = strategic_exec.process_strategic_orders(world, game_state)
  ```

**File:** `backend/commands/strategic.py`
- **Line 40:** `process_strategic_orders(world, game_state)` -- iterates all marshals
- **Line 74:** `_execute_strategic_turn(marshal, order, world, game_state)`:
  1. **Line ~81:** Retreat recovery check (pauses order if recovering)
  2. **Line ~91:** Condition check via `_check_condition()`
  3. **Line ~100:** Interrupt check via `_check_interrupts()`
  4. Routes to command-specific handler

### Stage 6: Command Handlers

#### MOVE_TO (strategic.py:127)
- Moves one step along path per turn
- Recalculates path if stale (personality-aware)
- Completes when marshal reaches destination
- If `attack_on_arrival=True`, attacks first enemy at destination

#### PURSUE (strategic.py:274)
- Recalculates path to enemy marshal each turn (target moves)
- Uses personality-aware pathfinding
- Attacks when in same region as target
- Completes on victory or target destroyed

#### HOLD (strategic.py:398)
- Sets `holding_position=True` (Grouchy gets +15% defense)
- **Sally mechanic:** Aggressive marshals attack adjacent enemies then return
  - Move to adjacent -> attack (with `_sortie=True`) -> return to hold position
- Completes when condition met (max_turns, etc.)

#### SUPPORT (strategic.py:573)
- Moves toward ally marshal
- If `follow_if_moves=True`, tracks ally movement
- If `join_combat=True`, joins ally's battles
- Completes when `until_battle_won` condition triggers

### Data Structures

#### StrategicOrder (marshal.py:75)
```python
@dataclass
class StrategicOrder:
    command_type: str          # "MOVE_TO", "PURSUE", "HOLD", "SUPPORT"
    target: str                # Region name or marshal name
    target_type: str           # "region", "marshal", "battle", "generic"
    path: List[str]            # BFS path from current to target
    conditions: StrategicCondition
    turns_active: int = 0
    attack_on_arrival: bool = False
    follow_if_moves: bool = False
    join_combat: bool = False
    target_snapshot_location: str = ""
    last_combat_result: str = ""
    last_combat_turn: int = 0
```

#### StrategicCondition (marshal.py:37)
```python
@dataclass
class StrategicCondition:
    max_turns: Optional[int] = None
    until_marshal_arrives: Optional[str] = None
    until_marshal_destroyed: Optional[str] = None
    until_battle_won: bool = False
    until_relieved: bool = False
    auto_cancel_below_ratio: Optional[float] = None
```

#### Key Marshal Fields (Strategic)
- `marshal.strategic_order` (marshal.py:299) -- active order or None
- `marshal.in_strategic_mode` (marshal.py:492) -- property, True if order exists
- `marshal.precision_execution_active` -- Grouchy clarity bonus flag
- `marshal.strategic_combat_bonus` -- consumed in combat
- `marshal.strategic_defense_bonus` -- consumed in combat

### Cross-Cutting Systems

#### Personality-Aware Pathfinding
**File:** `backend/commands/strategic.py`
- **Line 1046:** `_get_personality_aware_path(marshal, destination, world)`
- **Line 1038:** `_get_enemy_occupied_regions(nation, world)`
- Cautious: avoids enemy-occupied regions (falls back to direct if no safe route)
- Aggressive/Literal/Others: direct path

#### Blocked Path Handling
**File:** `backend/commands/strategic.py`
- **Line 881:** `_handle_blocked_path(marshal, next_region, order, world, game_state)`
- Literal: silently reroutes around obstacle
- Aggressive: auto-attacks at >=0.7 ratio, otherwise asks player
- Cautious: always asks player for decision

#### Interrupt Detection
**File:** `backend/commands/strategic.py`
- **Line 707:** `_check_interrupts(marshal, order, world, game_state)`
- Uses `world.get_battles_within_range()` (world_state.py:864)
- LITERAL personality skips cannon fire interrupts ("The Grouchy Moment")

#### Condition Evaluation
**File:** `backend/commands/strategic.py`
- **Line 792:** `_check_condition(marshal, order, world)`
- Evaluates: `max_turns`, `until_marshal_arrives`, `until_battle_won`, `until_marshal_destroyed`
- `until_battle_won` triggers on both victory AND stalemate

### Battle Tracking (for Cannon Fire)

**File:** `backend/models/world_state.py`
- **Line 59:** `self.battles_this_turn: List[Dict] = []`
- **Line 849:** `record_battle(region, attacker, defender)` -- called by combat resolver
- **Line 864:** `get_battles_within_range(location, range)` -- BFS distance check
- **Line 873:** `clear_turn_battles()` -- called at turn start

### Strategic Objection Pattern

**CRITICAL:** Strategic objections use `world.pending_strategic_objection`, NOT `world.pending_objection` (which is for tactical objections).

**Flow:**
```
1. User issues strategic command (HOLD, PURSUE, MOVE_TO, SUPPORT)
2. _execute_strategic_command() calls check_strategic_objection()
3. If objection triggers:
   a. Store objection data in world.pending_strategic_objection
   b. Return {pending_objection: True, objection: {...}}
4. Frontend shows popup, user chooses trust/insist/compromise
5. Frontend calls /respond_to_objection endpoint
6. handle_objection_response() checks for pending_strategic_objection FIRST
7. Routes to _handle_strategic_objection_from_endpoint()
8. Maps choices (trust->preferred, insist->proceed) and re-executes
```

### Override & Cancel

When a player issues a tactical command to a marshal with an active strategic order:
- **Override actions** (attack, move, defend): Silently cancel strategic order, execute tactical
- **Non-override actions** (wait, scout): Execute alongside strategic order
- **Explicit cancel** ("halt", "cancel"): Cost 1 action, -3 trust
- Implementation location: `executor.py _check_strategic_override()` (planned)

---

## 5. LLM Integration

### Command Parsing Pipeline

```
User Input: "Ney, attack Wellington"
                |
                v
+===============================================+
|           LLMClient.parse_command()           |
|              (llm_client.py)                  |
+===============================================+
                |
                | STEP 1: Always run fast parser first
                v
+-----------------------------------------------+
|        Fast Parser (keyword matching)         |
|        _parse_with_mock()                     |
|                                               |
|  Returns ParseResult with confidence score:   |
|  - 0.95 = marshal + action + target           |
|  - 0.9  = action + one identifier             |
|  - 0.8  = action only                         |
|  - 0.5  = unknown (couldn't parse)            |
+-----------------------------------------------+
                |
                | STEP 2: Check if LLM fallback needed
                |
                | Skip LLM if:
                |   - Mock mode (LLM_MODE=mock)
                |   - High confidence (>= 0.7)
                |   - No game_state provided
                |   - Meta command (help, debug, etc.)
                |
                v
        [confidence < 0.7 AND live mode?]
               /              \
              NO              YES
              |                |
              v                v
     Return fast result   +-----------------------------------+
                          |   AnthropicProvider.parse()       |
                          |        (providers.py)             |
                          +-----------------------------------+
                                        |
                                        | HTTP POST to Anthropic
                                        v
                          +-----------------------------------+
                          |   validation.validate_parse_result|
                          |   (catches hallucinations)        |
                          +-----------------------------------+
                                        |
                              Return validated result
```

### LLM Files Reference

| File | Purpose |
|------|---------|
| `backend/ai/llm_client.py` | Main entry point. Fast parser + LLM fallback logic |
| `backend/ai/providers.py` | Provider abstraction (Anthropic, Groq stub) |
| `backend/ai/schemas.py` | ParseResult, ProviderConfig dataclasses |
| `backend/ai/validation.py` | Validates LLM output against game rules |
| `backend/ai/prompt_builder.py` | Builds context-aware prompts |

### Configuration

```bash
# .env file
LLM_MODE=mock          # mock | anthropic | groq (groq not yet implemented)
ANTHROPIC_API_KEY=sk-ant-api03-...   # Required if LLM_MODE=anthropic
```

### Cost Estimation (Anthropic Haiku)
- Per request: ~500 input + ~200 output tokens = **~$0.0004**
- 1,000 ambiguous commands = **~$0.40**
- Fast parser catches 90%+, so real cost is much lower

### Strategic Score & Ambiguity

ParseResult scoring fields drive gameplay mechanics:
- `strategic_score` (0-100): How complex/strategic the command is
- `ambiguity` (0-100): How unclear the command was

**Active effects:**

| Score | Effect |
|-------|--------|
| Ambiguity 0-20 | +15% combat buff (Grouchy explicit order bonus) |
| Ambiguity 21-40 | +10% combat buff |
| Ambiguity 41-60 | +5% combat buff + warning |
| Ambiguity 61+ | No buff, triggers Grouchy clarification popup |
| High strategic | +authority, +morale (Napoleon in his element) |

### Key Insight

**Executor stays rule-based.** LLM helps with parsing ambiguous commands, but game mechanics are 100% deterministic. No LLM randomness in combat, movement, or AI decisions.

---

## 6. Cavalry Limits

### Mechanics

Cavalry units (like Ney) cannot hold defensive positions for extended periods. Horses need to move.

| Counter | Triggers At | Effect | Trust Penalty |
|---------|-------------|--------|---------------|
| `turns_in_defensive_stance` | 3 turns | Auto-switch to AGGRESSIVE | -3 |
| `turns_fortified` | 3 turns | Auto-unfortify | -3 |

**Maximum penalty per turn:** -6 (if both trigger simultaneously)

### Unit Type Comparison

#### CAVALRY (`cavalry=True`, `movement_range=2`)

**Movement:**
- Can attack enemies up to 2 regions away
- Still only moves 1 region per turn (attack range != movement)

**Defensive Limits (from `world_state.py`):**

| Counter | Trigger | Effect | Trust Penalty |
|---------|---------|--------|---------------|
| `turns_in_defensive_stance` | 3+ turns in DEFENSIVE stance | Auto-switch to AGGRESSIVE | -3 |
| `turns_fortified` | 3+ turns fortified | Auto-unfortify, defense_bonus = 0 | -3 |

#### INFANTRY (`cavalry=False`, `movement_range=1`)

**Movement:**
- Can only attack adjacent regions
- Standard 1-region movement

**No Defensive Limits:**
- Can hold defensive stance indefinitely
- Can stay fortified indefinitely
- No automatic stance changes

### Turn Flow

```
TURN START
    |
    +-> _check_cavalry_limits()
    |       |
    |       +-> If cavalry in defensive stance for 3+ turns:
    |       |       - Switch to AGGRESSIVE
    |       |       - Reset turns_in_defensive_stance = 0
    |       |       - trust.modify(-3)
    |       |       - Return "cavalry_stance_forced" event
    |       |
    |       +-> If cavalry fortified for 3+ turns:
    |               - Set fortified = False
    |               - Reset defense_bonus = 0
    |               - Reset turns_fortified = 0
    |               - trust.modify(-3)
    |               - Return "cavalry_fortify_forced" event
    |
    +-> Events shown in tactical messages at turn start

TURN END (in _process_tactical_states)
    |
    +-> For cavalry in defensive stance:
            turns_in_defensive_stance += 1
        For cavalry that is fortified:
            turns_fortified += 1
```

### Counter Resets

- Both counters reset when marshal moves (`move_to()` method)
- `turns_in_defensive_stance` resets when switching to non-defensive stance
- `turns_fortified` resets when unfortifying

```python
# marshal.py move_to()
if getattr(self, 'cavalry', False):
    self.turns_in_defensive_stance = 0
    self.turns_fortified = 0
```

### Event Types

| Event Type | Message Example |
|------------|-----------------|
| `cavalry_stance_forced` | "Ney's cavalry is too restless! Auto-switched to AGGRESSIVE. Trust -3" |
| `cavalry_fortify_forced` | "Ney's horses cannot stay still! Auto-unfortified. Trust -3" |
| `cavalry_restless_warning` | "Warning: Ney's cavalry growing restless (turn 3 of 3)..." |

---

## 7. Redemption System

### Trigger

When trust falls to <=20, a redemption event triggers.

### Available Options

| Option | Troops | Marshal | Bonus | Availability |
|--------|--------|---------|-------|--------------|
| **Grant Autonomy** | Keep | 3 turns independent, uses AI | Trust +5 to +40 based on performance | Always |
| **Administrative Role** | Frozen (stored) | Sidelined, restorable in Phase 4 | +1 action/turn | If >=2 field marshals AND no existing admin |
| **Dismiss** | Transfer to ally <=3 regions OR disband | Gone forever | +10 authority | If >=2 field marshals |

### Key Rules

1. **Last Marshal Protection:** If only 1 field marshal remains, ONLY Grant Autonomy is available
2. **Admin Cap:** Maximum 1 marshal can be in administrative role at a time
3. **Admin Troops Frozen:** Troops stay with admin marshal (stored in `administrative_strength`)
4. **Dismiss Range Limit:** Troops only transfer to ally within 3 regions, otherwise disband

### Redemption Choices (from disobedience reference)

| Choice | Effect |
|--------|--------|
| Grant Autonomy | Marshal acts independently for 3 turns, then returns at trust 50 |
| Dismiss | Remove marshal, transfer troops to nearest ally |
| Demand Obedience | Marshal stays but has 80% disobey chance |

### State Fields (Marshal)

```python
marshal.administrative = True           # In admin role
marshal.administrative_strength = 72000 # Stored troop count
marshal.administrative_location = "Belgium"  # Stored location
```

### State Fields (WorldState)

```python
world.bonus_actions = 1                 # From admin role transfer
world.calculate_max_actions()           # Returns 4 + bonus_actions
```

### Helper Methods (WorldState)

```python
world.get_field_marshals()              # French marshals not in admin
world.get_admin_marshals()              # French marshals in admin role
world.find_nearest_marshal_within_range(from_location, nation, max_distance)
```

---

## Terrain System (Phase 6.1)

**Status: Sessions 6.1.A + 6.1.B + 6.1.C COMPLETE. Phase 6.1 Terrain fully implemented.**

See `docs/TERRAIN_SPEC.md` for full spec. Implementation details:

### Terrain Types (6)

| Terrain | Defense | Movement | Supply | Cavalry Eff. | Charge Blocked |
|---------|---------|----------|--------|-------------|----------------|
| plains | 0% | 1.0x | 1.0x | 1.2x | No |
| forest | 10% | 1.3x | 0.8x | 0.5x | Yes |
| hills | 15% | 1.2x | 0.9x | 0.8x | No |
| mountains | 25% | 2.0x | 0.5x | 0.3x | Yes |
| urban | 20% | 1.0x | 1.2x | 0.5x | Yes |
| river_crossing | 15% | 1.5x | 1.0x | 0.6x | No |

### Architecture

- **Constants** (single source): `region.py` — `VALID_TERRAINS`, `TERRAIN_DEFENSE_BONUS`, `TERRAIN_MOVEMENT_COST`, `TERRAIN_SUPPLY_MODIFIER`, `TERRAIN_CAVALRY_EFFECTIVENESS`, `TERRAIN_CAVALRY_ATTRITION_BONUS`, `CHARGE_BLOCKED_TERRAIN`
- **Region model**: `terrain` field with validation, 4 computed properties (`defense_bonus`, `movement_cost`, `supply_modifier`, `cavalry_effectiveness`)
- **Combat**: `combat.py` reads `TERRAIN_DEFENSE_BONUS` for defender bonus, `TERRAIN_CAVALRY_EFFECTIVENESS` to scale recklessness attack bonus. Legacy terrain values ("open", "fortified", "mountain", "river") still work.
- **Executor**: All 5 `resolve_battle()` call sites in `executor.py` read terrain from defender's region. Charge blocking at two layers: popup suppression (with redirect to alternatives) + safety net fallthrough to normal attack.
- **Charge redirect**: When charge blocked by terrain at recklessness 3, executor scans for alternative enemies within cavalry range on allowed terrain. Offers redirect popup if found, falls through to normal attack if not. `cavalry_terrain_message` forwarded as separate field through `main.py`.
- **Auto-charge**: `world_state.py` auto-charge at recklessness 4+ reads terrain and blocks charge bonus on mountains/forest/urban (downgrades to normal attack, recklessness preserved).
- **REGIONS_DATA**: All 13 regions assigned terrain. Distribution: plains(4), hills(3), urban(3), mountains(1), forest(1), river_crossing(1).
- **Serialization**: `terrain` field roundtrips through `to_dict()`/`from_dict()`. Missing terrain defaults to "plains" (backward compat).

### Weighted Pathfinding (6.1.C)

Two new methods on `WorldState` alongside existing BFS:

- **`find_weighted_path(start, end, avoid_regions=None)`** — Dijkstra using `TERRAIN_MOVEMENT_COST` as edge weight. Edge weight = destination region's cost. Returns start-inclusive path or None.
- **`get_weighted_distance(start, end)`** — Returns total weighted cost of optimal path. Returns `float('inf')` if unreachable.

**Which commands use which pathfinding:**

| Command | Pathfinding | Rationale |
|---------|------------|-----------|
| MOVE_TO | **Weighted (Dijkstra)** | Strategic marches should pick lower-attrition routes |
| PURSUE | BFS (hop count) | Chasing doesn't pick scenic routes |
| HOLD | BFS | Short-range repositioning |
| SUPPORT | BFS | Following allies directly |
| AI retreat | **Weighted** | Retreat destination sort by weighted distance to capital |
| AI movement (P7, stagnation) | BFS | Single-hop adjacent comparisons |
| Scout range | BFS | Hop count is the right metric for range checks |

**Terrain display:** Scout output includes terrain name and defense bonus (e.g., "Terrain: Hills (+15% defense)"). `get_game_state_summary()` map_data includes `terrain` field for Godot frontend.

### Remaining (Phase 6.2+)

- Movement cost enforcement in executor (AP cost scaling by terrain — Phase 6.2 Economy)
- Supply modifier wiring (Phase 6.2 Economy)
- Cavalry attrition bonus in combat

### Known TODOs

- `backend/full_game.py` (dead code, 3 sites): `resolve_battle()` calls still use hardcoded `terrain="open"`. Marked with TODO comments — wire from region if file is revived.

---

## Action System Reference

### Action Types

| Action | Type | Cost | Description |
|--------|------|------|-------------|
| `attack` | Combat | 1 | Engage enemy forces |
| `defend` | Tactical | 1 | Smart defend - shifts to defensive stance or fortifies |
| `hold` | Tactical | 1 | **Alias for defend** - same mechanics, different flavor |
| `wait` | Free | 0 | **Free action** - marshal passes turn, no state change |
| `move` | Movement | 1 | Move to adjacent region |
| `retreat` | Movement | 1 | Withdraw from combat |
| `scout` | Intel | 1 | Gather intelligence |
| `recruit` | Economic | 1 | Raise new troops |
| `reinforce` | Movement | 1 | Move to ally marshal |
| `fortify` | Tactical | 1 | Dig in for defense bonus |
| `unfortify` | Tactical | 1 | Abandon fortifications |
| `drill` | Training | 1 | Train troops for shock bonus |
| `stance_change` | Tactical | 0-2 | Change combat stance |
| `help` | Meta | 0 | Show help |
| `end_turn` | Meta | 0 | End current turn |

### Hold vs Wait vs Defend

| Action | Mechanics | Stance Change | Bonus | When to Use |
|--------|-----------|---------------|-------|-------------|
| **defend** | Smart routing | Yes (to defensive) | Defense + fortify | Want maximum defense |
| **hold** | Same as defend | Yes (to defensive) | Defense + fortify | Prefer "hold the line" wording |
| **wait** | None | No | None | Conserve actions, maintain position |

**Key Difference:** `hold` and `defend` change the marshal's stance and potentially fortify, costing actions. `wait` does nothing and costs nothing.

### Action Addition Policy

**DO NOT ADD NEW ACTIONS WITHOUT EXPLICIT APPROVAL.**

Actions must be coordinated across multiple files and systems:
- `parser.py` - Valid actions list
- `executor.py` - Execution handlers
- `llm_client.py` - Keyword detection
- `personality.py` - Disobedience triggers
- `disobedience.py` - Message templates and routing

Adding an action without updating all systems will cause silent failures, dead code, or runtime errors.

---

## Example Scenarios

### Scenario 1: Ney Ordered to Fortify

```
You: "Ney, fortify your position"

Ney (Aggressive, Trust 75):
"Dig trenches? You want me to dig trenches like a coward?!"
[MAJOR OBJECTION - Severity 0.55]

Suggested Alternative: Attack Wellington

Your Choices:
1. TRUST - Let Ney attack instead (+12 trust, -3 authority)
2. INSIST - Force Ney to fortify (-10 trust, +2 authority)
3. COMPROMISE - Ney defends (holds position but stays mobile) (+3 trust, -1 authority)
```

### Scenario 2: Davout Ordered to Attack Superior Force (2:1 odds)

```
You: "Davout, attack Wellington" (Wellington has 96k, Davout has 48k)

Davout (Cautious, Trust 85):
"The odds are not in our favor. May I suggest we dig in and fortify?"
[MAJOR OBJECTION - Severity 0.60]

Suggested Alternative: Fortify current position
```

### Scenario 3: Grouchy Given Clear Orders

```
You: "Grouchy, move to Belgium"

Grouchy (Literal, Trust 65):
[NO OBJECTION - Grouchy follows orders exactly]
```
