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
6b. [Artillery Unit Type](#6b-artillery-unit-type)
7. [Redemption System](#7-redemption-system)
8. [Economy System](#8-economy-system)
9. [Fog of War](#9-fog-of-war)
10. [Manpower Pools](#10-manpower-pools)
11. [Campaign Log](#11-campaign-log)
12. [Top Bar & Screen Management](#12-top-bar--screen-management)
13. [Reinforcement System](#13-reinforcement-system)
14. [Win/Loss Relationship Formula](#14-winloss-relationship-formula)
15. [Phase 7 UI Integration (Session 66)](#15-phase-7-ui-integration-session-66)

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

# Wellington's "Reverse Slope Defense": +5% defense always
if ability.name == "Reverse Slope Defense":
    modifier *= 1.05
```

### Marshal Signature Abilities

Each marshal has a unique ability defined in `marshal.py` ability dict (4 string fields: name, description, trigger, effect). Abilities are wired in either `marshal.py` (modifier-based) or `combat.py` (post-resolution effects), respecting Golden Rule #1.

| Marshal | Ability | Effect | Trigger | Location | Status |
|---------|---------|--------|---------|----------|--------|
| Ney | Bravest of the Brave | +2 Shock when attacking | `when_attacking` | `combat.py` (shock block) | Wired (Phase 2.3) |
| Drouot | Sage of the Grand Army | Fort degradation 10% → 15% on attack | `when_attacking_fortified` | `combat.py` (degradation block) | Wired (Phase 6.5) |
| Wellington | Reverse Slope Defense | +5% flat defense always | `when_defending` | `marshal.py` `get_defense_modifier()` | Wired (Phase 6.5) |
| Blucher | Vorwärts! | +3k pursuit casualties on retreat, floor 1000 | `when_enemy_retreats` | `combat.py` (pursuit block) | Wired (Phase 6.5) |
| Uxbridge | Pursuit Master | +5k pursuit casualties on retreat (cavalry), floor 1000 | `when_enemy_retreats` | `combat.py` (pursuit block) | Wired (Phase 6.5) |
| Davout | Counter-Punch Mastery | +20% attack after defending (any outcome, any target) | `after_defending` | `marshal.py` `get_attack_modifier()` + `combat.py` (trigger) | Wired |
| Grouchy | Literal Obedience | Never questions orders | `receiving_orders` | `disobedience.py` (partial) | Deferred |
| Gneisenau | Staff Work | +5% atk/def to allies in region | `when_in_same_region_as_ally` | — | Deferred (Phase 7 S58) |
| ArchdukeCharles | Habsburg Resolve | +3% flat defense always | `when_defending` | `marshal.py` `get_defense_modifier()` | Wired (Phase 8 S1B) |
| Schwarzenberg | — | — | — | — | Deferred |
| Reynier | — | — | — | — | Deferred |

**Pursuit system (Phase 6.5):**
- Fires when attacker wins AND defender has `forced_retreat=True` (morale ≤ 25)
- Only attacker's ability applies (no stacking)
- Uxbridge requires `cavalry=True` — infantry with same ability dict won't fire
- Floor: defender strength cannot go below 1000
- Pursuit casualties added to `defender_casualties` in result dict (included in totals)
- Result dict fields: `pursuit_damage` (int), `pursuit_message` (string or None)

**Fort degradation ability (Phase 6.5):**
- Base rates: infantry 5%, artillery 10%, Drouot 15%
- Only fires when `defender.defense_bonus > 0`
- Result dict field: `drouot_ability_triggered` (string or None)

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

### Fortification Degradation (Session 31)

When a fortified defender is attacked, their `defense_bonus` degrades by 5% (0.05) per battle. This represents siege damage wearing down prepared positions.

- Applied in `combat.py` AFTER all combat resolution (damage, retreats, recklessness tracking)
- Only triggers if `defender.defense_bonus > 0`
- Capped at 0 (can't go negative)
- If defense_bonus reaches 0: fortification is destroyed
- Result dict includes: `fortification_degraded`, `fortification_old`, `fortification_new`

**Berthier Observations (Priority 6c):**
- `fort_degraded_attacker/defender`: "The enemy earthworks crumble under our bombardment"
- `fort_destroyed_attacker/defender`: "Their fortifications are reduced to rubble"
- Priority 6c fires between P6 (won/fort held) and P7 (won drilled)

**Key code:** `combat.py::resolve_combat()` (degradation), `battle_report.py::_pick_observation()` (P6c), `battle_report.py::_OBSERVATIONS` (templates)

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

### Battle Report (Berthier's After-Action Report)

After every player-visible combat, `battle_report.py` generates a structured report attached to the battle result.

**Architecture:**
- **Snapshots** taken BEFORE `get_attack_modifier()`/`get_defense_modifier()` (which consume one-shot bonuses like strategic_combat_bonus)
- `snapshot_attacker_modifiers()` — reads stance, drill/shock, strategic bonus (peek only, NOT zeroed), personality, recklessness, exhaustion, cavalry terrain, flanking, glorious charge, counter-punch mastery. Coordination entries (combined arms, per-ally, dedicated, adjacent, total) intentionally omitted (Gate 4) — Berthier's narrative observation handles coordination; detailed numbers deferred to Battle History screen (Phase 8.5).
- `snapshot_defender_modifiers()` — reads stance, fortify bonus, strategic defense (peek only), drilling penalty, personality, recklessness, terrain defense, fortification building. Coordination entries intentionally omitted (Gate 4).
- `generate_battle_report(battle_result, player_nation)` — assembles modifier_breakdown, casualty_summary, observation

**Perspective-aware observations:** Berthier always speaks from Napoleon's side. `_pick_observation()` uses `attacker_nation`/`defender_nation` from the battle result to determine which side is French. When the enemy attacks a French marshal, "we won" means the defender (our marshal) won. Templates use `{marshal}`, `{enemy}`, `{ally}`, `{relationship}`, `{coordination_bonus}`, and `{arrival_score}` placeholders filled via `.replace()` (graceful degradation — unfilled placeholders become empty strings). The `player_nation` param (default "France") is passed from `combat.py`.

**Observation priorities** (first match wins, `random.choice()` from 2-3 templates):

| Priority | Condition (from French perspective) |
|----------|-----------|
| 0.5 | Full combined arms triangle (3 unit types co-located) — Session 65 |
| 0.7 | Reinforcement arrived (ally marched onto field) — Session 65 |
| 0.8 | Reinforcement failed (ally didn't arrive in time) — Session 65 |
| 1 | Mutual destruction (both sides lost >50%) |
| 2 | We lost + enemy had fortification |
| 3 | We lost + bad stance matchup (aggressive into defensive) |
| 4 | We lost + enemy had terrain advantage >= 15% |
| 5 | We won + heavy casualties (>40% of our original strength) |
| 5.5 | Hostile marshal fought alongside under SUPPORT order — Session 65 |
| 6 | We won + broke through enemy fortification |
| 7 | We won + our troops were drilled |
| 8 | We lost + no drill + narrow margin (<15% of our strength) |
| 9 | We won decisively (2:1+ casualty ratio in our favor) |
| 10 | Stalemate |
| 11 | Default combat observation |
| 12 | Hostile marshal stood idle (refused coordination) — Session 65 |
| 13 | Devoted synergy (devoted ally amplified coordination) — Session 65 |
| 15 | Rival relationship improved after shared battle — Session 65 |

**Two-pass observation picking (Session 65):** Initial observation picked inside `resolve_battle()` (combat.py), which has no coordination/reinforcement/relationship data. After `executor.py` injects `coordination_context`, `reinforcement_results_for_report`, and `relationship_changes` into the battle result dict, the observation is re-picked if any coordination data is present. This avoids modifying `combat.py`.

**Data flow:**
```
combat.py (snapshots + generate_battle_report)
  → resolve_battle() return dict includes "battle_report" (initial observation)
  → executor.py injects coordination_context, reinforcement_results_for_report,
    relationship_changes → re-picks observation with full data
  → executor.py (5 passthrough sites: attack, 3 sally, charge)
  → world_state.py (1 passthrough: auto-charge event)
  → main.py (1 passthrough block)
  → Godot main.gd (_display_berthier_report)
```

**Godot display:** BBCode formatted with dark goldenrod header, light gray report lines, goldenrod observation quote. Comma-formatted numbers via `_format_number()`.

**Key code:** `battle_report.py` (snapshots + report), `combat.py:~189` (snapshot insertion point), `combat.py:~561` (return dict), `main.gd::_display_berthier_report()`

### Casualty Distribution (Session 62)

When 2+ same-nation marshals are in the battle region, casualties are distributed proportionally among participants instead of being applied entirely to the primary combatant.

**`resolve_battle(apply_casualties=False)` contract (C1/C2):**
- Computes all combat math (modifiers, dice, casualties) normally
- Returns raw casualties, morale deltas (int), and projected-strength outcome
- Does NOT modify marshal state (except fortification degradation — battle-triggered)
- Caller distributes casualties and applies effects per-participant

**Distribution formula:**
- Each participant's share = `int(raw_casualties * (participant.strength / total_strength))`
- **Artillery rear-position advantage:** When fighting alongside non-artillery units, artillery takes 50% of proportional share (`ARTILLERY_CASUALTY_FACTOR = 0.5`). No reduction when fighting alone or with only other artillery.
- **Cavalry receives NO casualty reduction** in combined arms. Cavalry charges and takes full proportional casualties — their combined arms benefit comes from combat bonuses (+10%/+20% attack, +5%/+10% defense), not reduced losses. This makes cavalry feel powerful but vulnerable: the decisive arm that wins battles at a cost. Infantry absorbs the bulk of casualties as the frontline unit type.
- Remainder (from rounding) assigned to strongest non-artillery marshal (falls back to strongest overall if all artillery)
- Capped at each marshal's current strength

**Participant eligibility:**
- Same-nation, in battle region, alive, not broken/retreating/recovering
- Hostile relationship (-2) WITHOUT SUPPORT order → Non-Participating (0% casualties)
- Hostile relationship (-2) WITH active SUPPORT order → Participating (D3: takes casualties, 0% coordination)

**Per-participant effects:**
- Casualties: proportional by strength
- Morale: UNIFORM delta (same for all on that side — psychological, not physical)
- battles_won/lost: all participants increment

**Primary-only effects:**
- Recklessness increment/reset: primary attacker only
- Counter-punch (cautious): primary defender only
- Counter-Punch Mastery (Davout): primary defender only
- Pursuit damage: primary attacker ability vs primary defender

**Solo battles (1v1):** `apply_casualties=True` (default) — zero behavior change.

**Key code:** `combat.py::_build_deferred_result()`, `executor.py::_distribute_casualties()`, `executor.py::_get_casualty_participants()`, `executor.py::_execute_attack()` coordination branch.

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

#### Excessive Trust Penalty (V2b)

`check_excessive_trust()` runs on every `record_response()`. Uses a 10-turn sliding window:
- **>80% trust** in window (min 3 responses): -3 authority
- **>65% trust** in window (min 3 responses): -2 authority
- Replaces the old trust-ratio branch in `_evaluate_authority()`

#### Authority Major Victory/Defeat (V2b)

Fires ONCE per battle (multiple criteria don't stack):
- **+5 authority**: Outnumbered win (attacker ≤ defender strength) or capital capture
- **-5 authority**: Outnumbering loss (attacker > defender strength) or capital loss

#### Threshold Events

- **Authority 70**: "Some marshals grow bold, sensing leniency."
- **Authority 50**: "The command structure wavers. Marshals question openly."
- **Authority 30**: "Your authority has collapsed. Expect frequent defiance."

### Defiance System (V2b)

Post-insist event: after player sees MODERATE/STRONG/EXTREME objection and insists, the marshal may defy the order.

#### Defiance Chance Formula

`base + vindication_mod + authority_mod + trust_mod + variance` (hard cap 0.40)

| Component | Value |
|-----------|-------|
| Base (MODERATE) | 5% |
| Base (STRONG) | 15% |
| Base (EXTREME) | 35% |
| Vindication | +10% per vindication stack |
| Authority ≥80 | -10% (strong leader suppresses) |
| Authority <50 | +10% (weak leader emboldens) |
| Trust ≤20 | +15% (broken trust) |
| Trust ≥80 | -10% (loyal) |
| Variance | ±8% random |
| **Hard cap** | **40%** |

Special: Literal personality (Grouchy) NEVER defies. Broken/retreating marshals cannot defy. Cooldown prevents re-defiance (3 turns after defiance, 1 turn after failed roll). AP cost follows the defiant action taken (not the original order).

#### Defiance Fallback Table

| Personality | Defiant Action | When Ordered To |
|-------------|---------------|-----------------|
| Aggressive | Attack (bombardment if artillery) | defend, fortify, hold, wait, retreat, SUPPORT, MOVE_TO |
| Cautious | Fortify | attack, SUPPORT, MOVE_TO |
| Literal | Never defies | — |

#### Defiance Outcome Table

| Outcome | Trust | Vindication | Authority | Cooldown |
|---------|-------|-------------|-----------|----------|
| Marshal **RIGHT** (`True`) | +2 | +1 | -5 | 3 turns |
| Marshal **WRONG** (`False`) | -5 | Reset to 0 | +3 | 3 turns |
| **INCONCLUSIVE** sulk (`None`) | 0 | No change | No change | 3 turns |
| Roll **fails**, obeys | -3 | Reset to 0 | No change | 1 turn |

#### Defiance Success Criteria

- **Attack/bombardment**: Won AND casualties < 50% (not pyrrhic)
- **Defend/fortify**: Not broken AND not retreating
- **Retreat**: Marshal survived (strength > 0)
- **Wait/sulk**: Always inconclusive

### Vindication Escalation (V2b)

Inserted between base objection trigger and mood variance:
- `vindication_score > 0` → escalate concern +1 level (e.g. MILD→MODERATE)
- `vindication_score < 0` → de-escalate concern -1 level
- NONE never promotes (prevents fake objections from vindication alone)
- MILD is the floor (never drops to NONE from de-escalation)

#### Vindication Decay

`_process_vindication_decay()` runs each turn in `advance_turn()`:
- -1 per 3 idle turns (no objection), symmetric toward 0
- Timer resets after each decay tick
- Stale defensive vindication entries (>5 turns old, no enemy attack) are cleared

#### Defensive Vindication

Created when player chooses "trust" and marshal's alternative was defend/fortify/hold:
- Stored in `vindication_tracker.pending_defensive_vindication`
- Resolved after enemy phase: held position = +1, broken/retreating = -1
- Stale entries (>5 turns, no attack) are cleared during vindication decay

### Relationship-Based SUPPORT Objection (V2b)

When issuing SUPPORT orders, relationship with the target marshal is checked:
| Personality | Hostile (-2) | Rival (-1) | Neutral+ |
|-------------|-------------|------------|----------|
| Aggressive | STRONG | MILD | NONE |
| Cautious | MODERATE | MILD | NONE |
| Literal | NONE | NONE | NONE |
| Other | MILD | NONE | NONE |

Takes priority if higher than personality-based concern. Includes timed SUPPORT compromise option (`condition.max_turns = 3`).

### V2b Frontend Display (Session 3)

| Data | Display Location | File |
|------|-----------------|------|
| Defiance result (action, outcome, Berthier text, stat changes) | Bordered "DEFIANCE" block in terminal | `main.gd` `_display_defiance_result()` |
| Authority threshold event | Bordered "AUTHORITY" block in terminal | `main.gd` `_display_authority_event()` |
| Authority value + label | Strategic ledger Forces tab header | `ledger.py` + `strategic_ledger.gd` |
| Authority value + label | Morning dispatch SITUATION section | `dispatch.py` + `dispatch_view.gd` + `main.gd` |
| Vindication score | Marshal management cards | `marshal_overview.py` + `marshal_management.gd` (already wired Sessions 1-2) |

### Compromise Rules

#### Basic Action Compromises

| Player Orders | Marshal Wants | Compromise |
|---------------|---------------|------------|
| Attack | Defend | **Move** (approach but don't engage) |
| Defend | Attack | **Move** (advance cautiously) |
| Attack | Move | **Move** |
| Move | Attack | **Defend** (hold ground) |
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
| Defend | Retreat | **Fortify** (dig in) |
| Attack | Retreat | **Defend** |

#### Stance Compromises

| Player Orders | Marshal Wants | Compromise |
|---------------|---------------|------------|
| Defensive Stance | Aggressive Stance | **Neutral Stance** |
| Aggressive Stance | Defensive Stance | **Neutral Stance** |

### Alternative Generation by Personality

All candidates validated via `_can_execute_suggestion()` (Master Rule #1). If entire chain exhausts, returns None → executor demotes to MILD (Master Rule #2).

#### AGGRESSIVE
When ordered to defend/fortify/hold/wait/form_square/drill/retreat/stance_change — unified fallback chain:
1. **Attack** nearest enemy (if target exists)
2. **Move** toward enemy (if valid path)
3. **Drill** (if not the ordered action and can_drill passes)
4. **Aggressive Stance** (if can change)
5. → None (demote to MILD)

#### CAUTIOUS (Context-Aware)
When ordered to attack:
- 3:1+ outnumbered: **Retreat** → **Fortify** → **Defend**
- 2:1 outnumbered: **Fortify** → **Defensive Stance** → **Defend**
- 1.5:1 or default: **Defensive Stance** → **Fortify** → **Defend**

When ordered to move (through enemy): **Fortify** → **Defensive Stance** → **Defend**

When ordered to defend/fortify (artillery streak): **Attack** → **Move** → **Defensive Stance** → None

#### BALANCED/LITERAL/LOYAL
- Attack ordered: **Defend**
- Defend ordered (with enemy nearby): **Attack** → **Move**
- Otherwise: Follow default fallback

### Compromise Generation by Personality

Compromises must differ from BOTH original order AND preferred alternative. Validated via `_can_execute_suggestion()`.

#### AGGRESSIVE
Chain: **Aggressive Stance** → **Drill** (skip if ordered) → **Move toward enemy** → **Defend**

#### CAUTIOUS
Chain: **Defensive Stance** → **Fortify** → **Defend**

#### Other / COMPROMISE_RULES table
Falls through to static table. If no distinct compromise found → None (demote to MILD).

### Master Rule #2: Exhaust→MILD Demotion

After `_generate_alternative` and `_find_compromise` run, executor validates:
- If preferred is None → demote
- If preferred == original → demote
- If preferred == compromise → demote
Demoted concerns become MILD (flavor text, no popup). This catches mood-variance-promoted MILDs that can't produce real popups.

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

### Post-Objection Action Routing (`_execute_post_objection`)

Single choke point for all post-objection execution (trust/insist/compromise). Defiance bypasses this entirely.

| Action | Handler | AP Pool | Signature | Notes |
|--------|---------|---------|-----------|-------|
| attack | `_execute_attack(marshal, target, world, game_state)` | Military | Marshal obj + target name | |
| defend | `_execute_defend(marshal, world, game_state)` | Military | Marshal obj | |
| move | `_execute_move(marshal, target, world, game_state)` | Military | Marshal obj + target name | |
| scout | `_execute_scout(marshal, target, world, game_state)` | Military | Marshal obj + target name | |
| recruit | `_execute_recruit(command, game_state)` | Admin | Command dict | |
| build | `_execute_build(command, game_state)` | Admin | Command dict | |
| repair | `_execute_repair(command, game_state)` | Admin | Command dict | |
| fortify | `_execute_fortify(command, game_state)` | Military | Command dict | |
| drill | `_execute_drill(command, game_state)` | Military | Command dict | |
| unfortify | `_execute_unfortify(command, game_state)` | Military | Command dict | |
| form_square | `_execute_form_square(command, game_state)` | Military | Command dict | |
| break_square | `_execute_break_square(command, game_state)` | Free | Command dict | |
| retreat | `_execute_retreat_action(marshal, world, game_state)` | Free | Marshal obj | |
| stance_change | `_execute_stance_change(command, game_state)` | Military | Command dict | Variable cost (0-2 AP) |
| hold | `_execute_hold(marshal, world, game_state)` | Military | Marshal obj | |
| wait | `_execute_wait(marshal, world, game_state)` | Military | Marshal obj | |
| bombardment | `_execute_bombardment(marshal, target, world, game_state)` | Military | Marshal + nearest enemy | Added Session 7b-audit |
| garrison | `_execute_garrison(command, game_state)` | Military | Command dict | Added Session 7b-audit |
| strategic | `_execute_strategic_command(parsed, command, game_state)` | Military | Via strategic routing | Only if `is_strategic` flag set |

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
- Implementation location: `executor.py` (inline in `execute()` — override handled via direct strategic order cancellation)

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

### Berthier Parse Recovery

When a command can't be parsed (Unknown action, Marshal 'None' not found), Berthier — Napoleon's chief of staff — responds in character instead of showing a raw error.

**Two intercept points in `main.py`:**

| Error | Where | Example |
|-------|-------|---------|
| `"Unknown action"` | Before executor | `"dance with the moon"` |
| `"Marshal 'None' not found"` | After executor | `"scout"`, `"move to Belgium"` (no marshal named) |

**Mock mode:** Template responses from `_berthier_mock_response()` in `llm_client.py`. Three categories (marshal recognised, target recognised, nothing recognised), 2-3 variants each, uses real game-state names.

**Live mode:** One LLM call via `build_berthier_recovery_prompt()` in `prompt_builder.py`. Berthier character: nervous, meticulous, reacts to the Emperor's tone (insults, absurdity, rudeness). Falls back to mock templates on API failure.

**Files:**
- `prompt_builder.py`: `build_berthier_recovery_prompt()` — system + user prompt
- `llm_client.py`: `generate_berthier_recovery()` + `_berthier_mock_response()`
- `parser.py`: `partial_marshal` / `partial_target` fields in failure dicts
- `main.py`: Two early-return blocks (before and after executor)

**Does NOT change:** No new actions, no new popups, no state changes, no serialization, no executor changes. Same `success: False` response shape — Godot needs no changes.

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

## 6b. Artillery Unit Type

Artillery units are a third marshal type alongside infantry and cavalry. They provide powerful bombardment but sacrifice mobility.

### Core Properties

| Property | Value |
|----------|-------|
| `artillery` flag | `True` (mutually exclusive with `cavalry`) |
| `movement_range` | 1 (same as infantry) |
| Attack restriction | Cannot attack the turn they move (`moved_this_turn`) |
| Win behavior | Stay in position after adjacent win — no advance, no capture |
| Banned actions | Glorious Charge, PURSUE auto-promotion |
| Defense penalty | -25% when `moved_this_turn` is True |

### moved_this_turn Lifecycle

1. **Set True** — on successful move in `_execute_move` (after `marshal.move_to()`)
2. **Blocks attack** — early return in `_execute_attack` if artillery + moved_this_turn
3. **Applies defense penalty** — -25% in `get_defense_modifier()` if moved_this_turn
4. **Reset False** — at turn start in `advance_turn()` (with other per-turn resets)

### Combat Interactions

| Interaction | Effect | Location |
|-------------|--------|----------|
| Cavalry vs Artillery | +30% shock_multiplier | `combat.py` (target-type, NOT marshal intrinsic) |
| Fort degradation | 10% per artillery attack (vs 5% for non-artillery) | `combat.py` |
| No advance on win | Artillery stays at origin, target NOT captured | `executor.py` |
| Ranged bombardment | Dedicated `_execute_bombardment()` path when attacker.location != defender.location | `executor.py` |
| Same-region combat | Normal `resolve_battle()` rules apply (full return damage, counter-punch possible) | `executor.py` → `combat.py` |

### Starting Marshals

| Marshal | Nation | Location | Strength | Personality |
|---------|--------|----------|----------|-------------|
| Drouot | France | Paris | 25,000 | cautious |

### Exhaustion Exemption (Session 2)

Artillery is exempt from exhaustion penalties — sustained bombardment is their core function. `_get_exhaustion_penalty()` returns 0.0 for artillery. Combat messages skip exhaustion display. Battle report snapshots skip exhaustion for artillery attackers.

### Bombardment Streak (Session 2)

Tracks consecutive bombardments on the same target:

| Field | Type | Description |
|-------|------|-------------|
| `last_bombardment_target` | string\|null | Region of last bombardment target |
| `bombardment_streak` | int | Consecutive attacks on same target |

- **Increments:** When artillery attacks same target region as previous bombardment
- **Resets to 1:** When artillery attacks a different target
- **Resets to 0:** When artillery moves (`_execute_move`)
- **Cleared:** On broken state recovery

### Berthier Bombardment Advisory (Session 2)

After artillery bombardment, if defender's `defense_bonus <= 0` AND region `fortification_bonus < 0.15`, Berthier advises: "Sire, the enemy fortifications at {location} are crumbling. An infantry assault would now have favorable odds." Returned as `bombardment_advisory` in result dict.

### Personality Objections (Session 51 — BOMBARDMENT_SPEC §7.1)

| Personality | Trigger | Condition | Level |
|-------------|---------|-----------|-------|
| Cautious | `ordered_into_melee` | Artillery attack on enemy in same region | STRONG |
| Cautious | `reckless_repositioning` | Artillery move + streak >= 2 + adjacent target defense_bonus > 0 | MODERATE |
| Cautious | `ordered_to_cease_fire` | Artillery defend/fortify + streak >= 1 + adjacent target defense_bonus > 0.05 | MODERATE |
| Cautious | `wasted_fire` | Artillery attack + target defense_bonus == 0 + target strength < 8000 | MILD |
| Cautious | `last_shot_advisory` | Artillery attack + bombardments_this_turn == 1 + multiple adjacent targets | MILD |
| Aggressive | `wasted_fire` | Artillery attack + target defense_bonus == 0 + target strength < 8000 | MILD |
| Literal | (none) | Never objects | — |

### AI Artillery Behavior (Session 2)

**P2 Screen Check:** If artillery has no friendly infantry screen (same/adjacent region) AND enemy cavalry within 2 regions, retreat toward nearest friendly infantry. Priority 2 (survival).

**P4 Bombardment Sort:** Artillery sorts valid targets by bombardment value: fortified+fort_building > fortified_only > unfortified, then by distance. Cavalry prefers exposed (unscreened) artillery targets.

**P7 Anti-Oscillation:** If artillery has adjacent enemies and hasn't moved this turn, skip P7 strategic movement (stay and bombard). If artillery must move, uses `_score_artillery_position()` for destination evaluation.

**Position Scoring (`_score_artillery_position`):**
- +30 hills terrain
- +25 adjacent fortified enemy
- +20 friendly infantry screen co-located, +10 adjacent
- -30 exposed to enemy cavalry (within 2, no screen)
- +10 own territory
- **Frontline penalty:** -50 if on enemy border without infantry screen, -30 with co-located infantry screen. Prevents artillery advancing to front-line regions.
- **Behind-screen bonus:** +15 if not on front line AND friendly infantry holds an adjacent front-line region. Rewards safe rear positions for bombardment support.

**Helper Functions:**
- `_artillery_has_screen(marshal, nation, world)` — friendly non-cavalry, non-artillery in same/adjacent region
- `_enemy_cavalry_within_range(marshal, nation, world, max_range)` — BFS to depth max_range
- `_score_artillery_position(region, marshal, nation, world)` — position quality score
- `_find_nearest_friendly_infantry(marshal, nation, world)` — BFS for retreat target

### Bombardment Resolution (Session 48)

Ranged bombardment now uses a dedicated `_execute_bombardment()` method in executor.py instead of the old 50% return casualties hack in combat.py.

**Routing rule:** In `_execute_attack()`, after target resolution: if `marshal.artillery` AND `marshal.location != enemy_marshal.location` → route to `_execute_bombardment()`. Same-region artillery combat still uses full `resolve_battle()`.

**Damage formula:**
```
raw_damage = defender.strength × 0.04 × (1.0 + shock_skill/15.0) × terrain_modifier
final_damage = int(raw_damage × uniform(0.80, 1.20))
return_casualties = int(marshal.strength × 0.015 × uniform(0.80, 1.20))
```

**Terrain bombardment modifiers (region.py `TERRAIN_BOMBARDMENT_MODIFIER`):**

| Terrain | Modifier | Reason |
|---------|----------|--------|
| Plains | 1.10 | +10% — open ground, no cover |
| Forest | 0.80 | -20% — trees obscure targets |
| Hills | 0.75 | -25% — defilade behind ridgelines |
| Mountains | 0.60 | -40% — deep cover, hard to range |
| Urban | 0.70 | -30% — buildings provide shelter |
| River Crossing | 1.00 | Neutral — rivers don't help vs shells |

**Per-bombardment effects:**
- Fort degradation: -0.10 (always artillery rate), floors at 0
- Defender morale: -3
- Attacker morale: unchanged
- No winner/loser, no battles_won/lost, no counter-punch
- `bombardments_this_turn` incremented (max 2 per turn)
- `attacks_this_turn` incremented (shares exhaustion counter)
- Bombardment streak tracking (same as Session 43)

**Defender destroyed:** Delegates to `_apply_forced_retreat_or_break()` for consistent break behavior. Region NOT captured (artillery doesn't advance).

**Per-turn limit:** `bombardments_this_turn` field on marshal, reset to 0 in `advance_turn()`. Max 2 bombardments per turn.

### Collateral Damage (Session 49)

After primary bombardment resolves, stray shells can hit other forces in the target region:

```
For each non-primary marshal in target region (strength > 0, not broken/retreating):
  40% chance of hit:
    collateral_raw = primary_raw_damage × 0.25
    collateral_casualties = int(collateral_raw × uniform(0.80, 1.20))
    force.take_casualties(collateral_casualties)
    force.adjust_morale(-1)
```

**Friendly fire:** When collateral hits a marshal of the same nation as the artillery:
- Trust penalty: -5 on the hit marshal
- Relationship penalty: -1 between hit marshal and artillery marshal
- If trust drops to <= 20, normal redemption event triggers

**Region-name targeting:** When player says "bombard Waterloo" (region name, not marshal name), the strongest enemy marshal in that region is auto-selected as the primary target. Other marshals become collateral candidates.

**Scope:** Collateral only affects marshal objects. Capital garrisons and player garrison detachments (region attributes) are NOT affected.

**Collateral array in result dict and event log:**
```python
"collateral": [
    {"name": "Uxbridge", "nation": "Britain", "casualties": 998, "friendly_fire": False},
    {"name": "Davout", "nation": "France", "casualties": 750, "friendly_fire": True},
]
```

### Berthier Bombardment Observations (Session 52)

After each bombardment, Berthier provides a contextual observation embedded in `bombardment_result.berthier_observation`. Selection priority:

| Priority | Condition | Observation Key |
|----------|-----------|----------------|
| P1 | Defender reduced to 0 | `bombardment_target_broken` |
| P2 | Collateral hit friendly force | `bombardment_friendly_fire` |
| P3 | Fort degraded this bombardment | `bombardment_fort_cracking` |
| P4 | Terrain modifier < 0.80 | `bombardment_terrain_difficulty` |
| P5 | Casualties < 3% of defender's pre-bombardment strength | `bombardment_ineffective` |
| P6 | Default | `bombardment_effective` |

Templates use `{marshal}`, `{enemy}`, and `{terrain}` placeholders. Terrain names have underscores replaced with spaces.

**Godot display:** `_display_bombardment_report()` in `main.gd` shows terrain effectiveness, casualties, fort degradation, collateral (with friendly fire highlighting), bombardments remaining, and the observation quote. Separate from the melee `_display_berthier_report()`.

### Strategic HOLD Bombardment (Session 51)

Artillery marshals on strategic HOLD auto-bombard adjacent enemies instead of using personality-specific sally/fortify behavior.

**Routing:** In `_execute_hold()`, if `marshal.artillery == True` and at hold position → dispatch to `_execute_hold_bombardment()`.

**Target selection by personality:**
- **Cautious:** Crack forts first (highest `defense_bonus`), then biggest army
- **Aggressive:** Finish the weak first (lowest `strength`)
- **Literal:** Lock on previous target (`order.bombardment_target`), fall back to default if target left

**Edge cases handled:**
- Enemy enters artillery's region → HOLD breaks, requests orders
- `bombardments_this_turn >= 2` → "already fired today" message, order continues
- No adjacent targets → "maintaining readiness" message, order continues
- Broken/retreating/dead targets excluded from selection
- Executor failure → graceful fallback message, order continues
- Timed expiry and not-at-position checked BEFORE artillery dispatch

**New serialization field:** `bombardment_target` on `StrategicOrder` — stores locked target name for literal personality. Defaults to `None`.

### Key Files

| File | What changed |
|------|-------------|
| `marshal.py` | `artillery` flag, `moved_this_turn`, defense modifier, exhaustion exemption, `bombardment_streak` + `last_bombardment_target`, `bombardments_this_turn`, serialization, starting marshals, **`bombardment_target` on StrategicOrder (Session 51)** |
| `combat.py` | Cavalry counter (+30%), fort degradation (10%), cavalry_counter_message, artillery exhaustion message skip |
| `executor.py` | Can't attack after moving, no advance on win, glorious charge ban, PURSUE block, recruit type logic, bombardment streak tracking, Berthier advisory, broken state cleanup, **`_execute_bombardment()` (Session 48)** |
| `world_state.py` | Artillery constants, pool regen, `get_artillery_regen_rate()`, moved_this_turn reset, **bombardments_this_turn reset (Session 48)** |
| `enemy_ai.py` | moved_this_turn gate, pool-aware recruit, cost-aware admin, P2 screen check, P4 bombardment sort + cavalry preference, P7 anti-oscillation + position scoring, 4 helper functions |
| `strategic.py` | **`_execute_hold_bombardment()` + `_hold_no_targets()` (Session 51)** |
| `battle_report.py` | Artillery observation templates, exhaustion snapshot skip for artillery, **6 bombardment observation categories + `_pick_bombardment_observation()` + `generate_bombardment_report()` (Session 52)** |
| `objection_v2.py` | **5 artillery triggers: ordered_into_melee (STRONG), reckless_repositioning (MODERATE), ordered_to_cease_fire (MODERATE), wasted_fire (MILD), last_shot_advisory (MILD) (Session 51)** |
| `disobedience.py` | **5 artillery flavor text keys under cautious personality (Session 51)** |
| `llm_client.py` | Artillery keywords (bombard, barrage, shell, cannonade), Drouot in known_marshals |
| `prompt_builder.py` | Drouot bombardment few-shot example |

---

## 6b. Square Formation (Session 67 — Tactical Triangle Part A)

Infantry marshals can form a defensive square — highly effective against cavalry but vulnerable to artillery fire. Part of the Tactical Triangle (infantry ↔ cavalry ↔ artillery).

### Actions

| Action | AP | Type | Description |
|--------|-----|------|-------------|
| `form_square` | 1 | Normal | Infantry enters square formation |
| `break_square` | 0 | Free | Returns to line formation |

### Eligibility (form_square)

| Check | Blocks if |
|-------|-----------|
| Unit type | `cavalry == True` or `artillery == True` |
| Already square | `square_formation == True` |
| Fortified | `fortified == True` (mutual exclusion) |
| Broken | `broken == True` |
| Retreating | `retreating == True` |
| Drilling | `drilling == True` or `drilling_locked == True` |

### Combat Interactions

| Attacker Type | Effect | Implementation |
|---------------|--------|----------------|
| Cavalry vs Square | -40% damage (`shock_multiplier *= 0.60`) | `combat.py` |
| Artillery vs Square | +50% damage (`shock_multiplier *= 1.50`) | `combat.py` |
| Infantry vs Square | No special modifier | — |
| Square defense | +5% defense modifier | `marshal.py get_defense_modifier()` |

Both normal and deferred (`apply_casualties=False`) combat paths handle these interactions.

### Bombardment vs Square

- **+50% damage:** `square_bombardment_bonus = 1.50` applied to `raw_damage` in `_execute_bombardment()`
- **-15 extra morale:** Total morale hit = -18 (3 base + 15 square penalty)
- Packed formation is a perfect artillery target

### Auto-Break

Square automatically breaks when marshal receives any active order:

| Breaks on | Does NOT break on |
|-----------|-------------------|
| attack, move, fortify, drill, recruit, garrison, stance_change, glorious_charge | form_square, break_square, wait, end_turn |

`_auto_break_square(marshal, action_name)` called at top of each `_execute_*` method. Returns message string for display.

### Coordination & Reinforcement

| Rule | Effect |
|------|--------|
| Attack coordination | 0% (excluded, same as fortified) |
| Defense coordination | Normal (still contributes) |
| Adjacent support | Excluded from count |
| Reinforcement | Cannot reinforce (Rule #15) |

### Strategic Order Cancellation

Forming square cancels any active strategic order, including HOLD with `holding_position` and `hold_region` clearing.

### Objection Triggers (V2a)

| Personality | Trigger | Level |
|-------------|---------|-------|
| Aggressive | form_square (any) | MODERATE |
| Cautious | form_square when fortified | MILD |
| Cautious | form_square when artillery adjacent, no cavalry | MILD |
| Universal | form_square when both cavalry AND artillery adjacent | MILD |

### Enemy AI (P2.5)

Between P2 (critical survival) and P3 (threat response):

- **Form square:** When infantry + enemy cavalry adjacent/co-located + no enemy artillery adjacent/co-located + cooldown <= 0
- **Break square:** When in square + no enemy cavalry adjacent/co-located. Sets `ai_square_cooldown = 2`
- **Anti-oscillation:** Cooldown decrements per turn in `_process_tactical_states()`. Uses transient `ai_square_cooldown` field (not serialized, managed via `getattr/setattr`)

### Tactical State Clearing

- Square clears on `broken == True` or `retreating == True` (in `_process_tactical_states()`)
- AI cooldown decrements each turn

### Battle Report

3 new Berthier observation categories (Priority 6e):

| Key | Condition | Templates |
|-----|-----------|-----------|
| `square_cavalry_repulsed` | Cavalry attacker + defender in square | 3 templates |
| `square_artillery_punished` | Artillery attacker + defender in square | 3 templates |
| `square_held_defense` | Defender in square + defender won | 3 templates |

Snapshot entries: "Square formation (vs cavalry)" penalty 40%, "Square formation (vs artillery)" bonus 50%, "Square formation" defense bonus 5%.

### Serialization

| Field | Type | Default | Location |
|-------|------|---------|----------|
| `square_formation` | bool | false | `marshal.py` `to_dict()`/`from_dict()` |

### Key Files

| File | What changed |
|------|-------------|
| `marshal.py` | `square_formation` field, +5% defense modifier, serialization |
| `combat.py` | Cavalry -40%, artillery +50%, deferred path params |
| `executor.py` | `_execute_form_square`, `_execute_break_square`, `_auto_break_square`, bombardment bonus, coordination exclusions, reinforcement Rule #15, SUPPORT advisory |
| `world_state.py` | AP costs (1/0), tactical state clearing, AI cooldown decrement |
| `objection_v2.py` | 4 triggers (aggressive, cautious×2, universal) |
| `enemy_ai.py` | P2.5 form/break square logic |
| `battle_report.py` | 3 observations, snapshot entries |
| `validation.py` | `form_square`, `break_square` in VALID_ACTIONS |
| `parser.py` | `form_square`, `break_square` in valid_actions |
| `llm_client.py` | Mock parser keywords |

---

## 16b. Auto-Bombardment & Overwatch (Session 68)

### Auto-Bombardment (SUPPORT Artillery Pre-Fire)

When a marshal attacks, all same-nation artillery on SUPPORT targeting that marshal automatically fire bombardment against the defender BEFORE `resolve_battle()`.

**Timing:** After `_calculate_coordination_context()` and overwatch, before `resolve_battle()`.

**Eligibility (all required):**
- Same nation as the attacker
- `artillery == True`
- Active SUPPORT order targeting the attacker (`strategic_order.command_type == "SUPPORT"` and `strategic_order.target == attacker.name`)
- `bombardments_this_turn < 2`
- `strength > 0`
- NOT `broken`, NOT `retreated_this_turn`, NOT `retreat_recovery > 0`, NOT `moved_this_turn`
- Adjacent to or co-located with battle region

**Behavior:**
- Calls existing `_execute_bombardment()` — same damage formula, collateral, fort degradation, streak
- Does NOT consume player AP
- Fires for BOTH player and AI attacks (Building Blocks principle)
- Only fires when supported marshal is the ATTACKER (not when they're defending)
- Increments `bombardments_this_turn` on the artillery marshal

**Dead-Defender Check:** If bombardment kills the defender (`strength <= 0`):
- Loop breaks (remaining artillery don't fire)
- `resolve_battle()` is skipped entirely
- Defender removed from `world.marshals`
- Attacker advances (unless artillery) and attempts capture

**Fog of War:** When auto-bombardment fires from an adjacent region (not co-located) and the defender is the player nation, the player gets PARTIAL intel on the artillery's source region via `update_intel_from_transit()`.

**Note:** SUPPORT order is cleared post-battle by the reinforcement system (A-C2 step 5) because artillery "arrives" as an adjacent reinforcer. This is existing Session 61a behavior.

### Overwatch (Passive Artillery Defense)

Enemy artillery in the defender's region passively debuffs all attackers by -3% per eligible gun, capped at 3 guns (-9% max).

**Where applied:** `marshal.py get_attack_modifier()` — after coordination bonus, before return.

**Field:** `overwatch_penalty` (transient, NOT serialized). Set via assignment, read via `getattr(m, 'overwatch_penalty', 0.0)`. Cleared after combat via `_COORDINATION_FIELDS`.

**Eligibility (all required):**
- In the defender's region (same location as battle)
- Different nation from attacker
- `artillery == True`
- `strength > 0`
- NOT `broken`, NOT `retreated_this_turn`, NOT `retreat_recovery > 0`, NOT `moved_this_turn`

**Cap:** `min(artillery_count, 3)`, penalty = `capped * 0.03`.

**Does NOT apply to:**
- Bombardment (ranged fire, separate code path)
- Coordination cap (independent of coordination bonus)

### AI Awareness

`_evaluate_target_ratio()` in `enemy_ai.py` factors overwatch into ratio calculation:
- Counts same-nation artillery in target's region
- Applies `(1.0 - capped_art * 0.03)` multiplier to effective ratio
- Eligible checks match executor overwatch checks

### Battle Report

3 new Berthier observation categories:

| Key | Priority | Condition | Templates |
|-----|----------|-----------|-----------|
| `support_bombardment_effective` | 0.6 | Auto-bombardment fired, significant damage | 3 templates with `{artillery}` placeholder |
| `support_bombardment_minimal` | 0.6 | Auto-bombardment fired, minimal damage | 3 templates with `{artillery}` placeholder |
| `overwatch_repelled` | 6f | Overwatch active (≥1 enemy artillery in region) | 3 templates |

Snapshot entries:
- "Artillery overwatch" penalty (int % value) in `snapshot_attacker_modifiers()`
- `{artillery}` placeholder in `_fill()` for support bombardment templates

### Key Files

| File | What changed |
|------|-------------|
| `marshal.py` | `overwatch_penalty` in `get_attack_modifier()` (transient, not serialized) |
| `executor.py` | `_calculate_overwatch()`, auto-bombardment loop in `_execute_attack()`, dead-defender early exit, `overwatch_penalty` in `_COORDINATION_FIELDS` |
| `battle_report.py` | 3 observation categories, snapshot entry, `{artillery}` placeholder |
| `enemy_ai.py` | Overwatch factor in `_evaluate_target_ratio()` |

---

## 7. Redemption System

### Trigger

When trust falls to <=20, a redemption event triggers via `check_redemption_threshold()` in `disobedience.py`. The centralized helper gates on: trust <= 20, not already pending, not autonomous, not administrative, not on cooldown, player nation only. Wired at: V1 objection resolution, tactical defiance success, strategic defiance success, strategic endpoint fallthrough, bombardment collateral, strategic interrupt trust penalties (7 sites), and cavalry forced-stance/unfortify penalties. Godot frontend handles redemption_event in `_on_command_result`, `_on_objection_response`, `_on_interrupt_response`, and deferred through the end-turn dialog chain (`_on_enemy_phase_dismissed`, `_on_strategic_report_dismissed`, `_process_next_interrupt`).

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
5. **5-Turn Cooldown:** After resolving a redemption event, the same marshal cannot trigger another for 5 turns (`redemption_cooldown_until = current_turn + 5`)

### Redemption Choices (from disobedience reference)

| Choice | Effect |
|--------|--------|
| Grant Autonomy | Marshal acts independently for 3 turns, then returns at trust 50 |
| Dismiss | Remove marshal, transfer troops to nearest ally |
| Demand Obedience | Marshal stays but has 80% disobey chance |

### State Fields (Marshal)

```python
marshal.redemption_pending = True       # Redemption event triggered, awaiting choice
marshal.redemption_cooldown_until = 12  # Turn when redemption can next fire
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
- **REGIONS_DATA**: All 19 regions assigned terrain. Distribution: plains(6), hills(4), urban(4), forest(2), mountains(1), river_crossing(1). Note: "urban" counts regions with `terrain: "urban"` (Paris, Berlin, Vienna, Milan).
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
| HOLD | **Weighted (Dijkstra)** | March to hold position avoids expensive terrain |
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
| `recruit` | Economic | 1 Admin AP | Raise 10k troops (uses admin AP, not CP). Cost: 150-300 gold. Morale dilution. |
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

---

## 8. Economy System

### Region Types (Phase 6.2.A)

Each region has a `region_type` field that determines its base income:

| Region Type | Income | Examples |
|-------------|--------|----------|
| `capital` | 300 | Paris, Berlin, Vienna |
| `major_city` | 200 | Lyon |
| `city` | 150 | Milan, Marseille, Saxony, Bohemia |
| `town` | 100 | Belgium, Rhineland, Bavaria, Normandy, Hanover, Dresden, Tyrol |
| `rural` | 50 | Netherlands, Waterloo, Brittany, Bordeaux |

**Constants (single source of truth in `region.py`):**
- `VALID_REGION_TYPES` — set of 5 valid type strings
- `REGION_TYPE_INCOME` — dict mapping region_type → income value

**Important:** `region_type` and `terrain` are independent axes. Terrain affects combat and movement. Region type affects income.

### Per-Nation Gold (Phase 6.2.A)

Gold is tracked per nation in `world_state.nation_gold` dict:

```python
self.nation_gold = {
    "France": 800,   # Player starting gold
    "Britain": 800,  # Naval/trade wealth
    "Prussia": 300,  # Smaller economy
}
```

**Convenience property:** `world.gold` reads/writes `nation_gold[player_nation]`. All existing code referencing `world.gold` continues to work unchanged.

**Income calculation:** `calculate_turn_income(nation=None)` works for any nation. Defaults to player_nation. Uses `region.get_effective_income()` (applies stability + war damage modifiers). Income breakdown includes per-region stability, damage, and effective income details.

**Income application:** `apply_turn_income(nation=None)` wraps `process_income_phase()` which handles income - upkeep + admin bonus.

### Upkeep + Bankruptcy (Phase 6.2.B)

**Upkeep:** `(marshal.strength // 1000) * 5` per marshal. Halved during bankruptcy (mercy mechanic).

**Income phase:** `process_income_phase(nation)` = income - upkeep + admin bonus. Runs for ALL nations during turn resolution.

**Bankruptcy:** `nation_bankruptcy_turns` tracks consecutive turns with negative gold. Turn 1-2: warnings + halved upkeep. Turn 3+: desertion (5% strength loss per marshal).

**Admin AP:** 2/turn, recruit uses admin AP (not CP). Unused admin AP * 75 = gold bonus.

### Region Stability (Phase 6.2.C)

**Stability field:** `region.stability` (int, 0-100). Controls income via tiered modifier.

| Stability | Label | Income Modifier |
|-----------|-------|----------------|
| 0-25 | Hostile | 0% (no income) |
| 26-50 | Unrest | 25% |
| 51-75 | Settling | 75% |
| 76-100 | Stable | 100% |

**Boundary values fall into LOWER tier:** stability=25 → Hostile, stability=50 → Unrest, stability=75 → Settling.

**On capture:** Stability set to 25 (Hostile/Secured). TODO 6.2.E: plunder (10) vs secure (25) choice.

**On battle:** -10 stability per battle in the region.

**Growth per turn:** +5 base, +5 if friendly marshal present (garrison bonus). Capped at 100.

### War Damage (Phase 6.2.C)

**War damage field:** `region.war_damage` (float, 0.0-0.5). Reduces income multiplicatively.

**Sources:**
- Normal battle (<50k combined pre-battle troops): +0.10
- Major battle (50k+ combined): +0.20
- Stacks across multiple battles in same turn
- Capped at 0.50

**Recovery:** -0.02/turn natural recovery. 0.10 damage recovers in 5 turns.

**Combined income formula:**
```python
effective_income = int(income_value * stability_modifier * (1.0 - war_damage))
```

Example: Paris (300 base), Unrest (50 stability = 0.25 mod), 0.10 damage → `int(300 * 0.25 * 0.90)` = 67 gold.

### Turn Resolution Order

```
1. Clear per-turn flags
2. Process tactical states (fortify, drill)
3. Turn counter increment
4. Stability growth (all regions)     ← Phase 6.2.C
5. War damage recovery (all regions)  ← Phase 6.2.C
6. Bankruptcy desertion (all nations) ← Phase 6.2.B
7. Income phase (all nations)         ← Phase 6.2.A+B
8. Reset actions, cavalry limits, trust warnings, reckless cavalry
```

### Serialization

- `nation_gold` serialized as `{"France": 800, "Britain": 800, ...}` in `to_dict()`
- `gold` key still emitted for backward compatibility (player nation's gold)
- `from_dict()` prefers `nation_gold` key; falls back to old `gold` field for pre-6.2 saves
- `region_type` serialized on each Region; defaults to `"town"` if missing (backward compat)
- `stability` defaults to 100, `war_damage` defaults to 0.0 for backward compat

### Recruitment (Phase 6.2.D)

**Morale dilution:** Green conscripts have 40% base morale. Army morale becomes weighted average:
```python
RECRUIT_MORALE = 40
new_morale = int((old_strength * old_morale + 10000 * RECRUIT_MORALE) / (old_strength + 10000))
```

**Cost table:**

| Situation | Gold Cost | Condition |
|-----------|-----------|-----------|
| Capital region | 150 | `region.region_type == "capital"` |
| Settling region (stability 51-75) | 300 | 50% premium |
| Stable region (stability 76+) | 200 | Base cost |
| Hostile/Unrest (stability ≤ 50) | **Blocked** | Cannot recruit |

**Capital discount always wins:** If capital has stability 51-75 (unlikely), capital discount (150) takes priority over settling premium (300).

**Location resolution:**
- `"recruit for Ney"` → recruit at Ney's current location
- `"recruit at Lyon"` → recruit at Lyon, troops go to nearest marshal
- `"recruit"` (default) → recruit at capital (Paris), 150 gold

**Stability gate:** Recruitment blocked when `region.stability <= 50` (entire Unrest tier). Matches tier boundaries from 6.2.C.

**Controller check:** Recruitment location must be controlled by player's nation. Cannot recruit in enemy territory.

**Admin AP:** Uses admin AP pool (not CP). AP deduction handled by executor routing layer, not inside `_execute_recruit()`.

**Event fields:** `morale_before`, `morale_after`, `gold_cost`, `stability_premium`, `capital_discount`, `troops_added`, `new_strength`. All `int()`.

**Morale Warning (Session 31):** Recruitment result includes warning labels when post-recruit morale is dangerously low:
- `[WARNING]` when new morale < 40%: "consider drilling before battle"
- `[DANGER]` when new morale < 25%: "troops may break in combat"

**Key code:** `executor.py::_execute_recruit()`, `executor.py::_calculate_recruit_cost()`

### Plunder/Secure Capture Choice (Phase 6.2.E)

When a **player** captures a region, a popup asks: **Plunder** or **Secure**?

| Choice | Stability | War Damage | Gold | Buildings | Plundered Flag |
|--------|-----------|------------|------|-----------|----------------|
| Plunder | 10 | +0.35 | = base income | Destroyed | True |
| Secure | 25 | +0.00 | 0 | Damaged | False |

- **AI captures** auto-decide by personality: aggressive → plunder, all others → secure
- `pending_capture_choice` blocks commands until resolved (same pattern as `pending_objection`)
- Plundered flag clears when stability recovers above 50
- Endpoint: `POST /capture_choice` with `{"choice": "plunder"}` or `{"choice": "secure"}`
- Key code: `executor.py::handle_capture_choice()`, `executor.py::_apply_plunder()`, `executor.py::_apply_secure()`

### Building System (Phase 6.2.E)

Four building types, constructed via `build <type> at <region>`:

| Building | Cost | Time | Effect |
|----------|------|------|--------|
| Supply Depot | 300g | 2 turns | +50 base income (before modifiers) |
| Fortification | 400g | 3 turns | +25% defense (stacks with terrain) |
| Training Ground | 250g | 2 turns | Recruit morale 55% (instead of 40%) |
| Market | 350g | 2 turns | +25% base income multiplier (after depot, before stability/damage) |

**Building slots:** Capital: 2, Major City/City: 1, Town/Rural: 0

**Validation:** Region must be controlled, stability > 50, sufficient gold, available slots, no duplicate type, no existing construction.

**Construction timers** process during turn resolution (after tactical states, before turn counter advance).

**Battle damage:** Battles damage civilian buildings — markets, supply depots, training grounds (100% if 50k+ troops, 25% chance otherwise). **Fortifications are immune** to battle damage — they're built to withstand combat and provide contested capture holdout value (6.2.F). Plunder destroys all buildings (including forts). Secure damages all buildings (including forts). Construction cancelled on any capture.

**Repair:** `repair <region>` = 150 gold, -0.15 war damage. `repair <building> at <region>` = 150 gold, restores damaged building. Uses admin AP.

**Key code:** `region.py::BUILDING_TYPES`, `executor.py::_execute_build()`, `executor.py::_execute_repair()`, `world_state.py::process_construction_timers()`

### Supply Limits & Attrition (Phase 6.2.F)

**Supply Capacity:** Each region has a max troop capacity derived from region type + buildings + terrain.

| Region Type | Base Capacity |
|-------------|---------------|
| Capital | 50,000 |
| Major City | 40,000 |
| City | 30,000 |
| Town | 25,000 |
| Rural | 15,000 |

Supply depot adds +10,000 to base. Terrain modifier applied (mountains 0.5x, urban 1.2x, etc.). Capacity is a computed property — not serialized.

**Home Territory Supply Bonus:** Marshals in their own nation's territory get 1.5x effective supply capacity. This means defending home territory is more sustainable than invading, and reduces turtling advantage since defenders take less attrition. Calculated per-marshal based on whether the region's controller matches the marshal's nation.

**Supply Attrition:** Runs during turn resolution (after stability/war damage recovery, before bankruptcy). Calculated per-marshal with individual effective capacity. When total troops in a region exceed a marshal's effective capacity, attrition is continuous: `min(0.03, excess_ratio * 0.015)` where `excess_ratio = (total_troops - capacity) / capacity`. This replaces the old tiered system (1%/3%/5%) with a smooth curve that caps at 3%.

**Movement Attrition:** Applied every time a marshal moves. Base rate 1% (retreat 0.5%). Large armies (>20k) get a size penalty: `min(0.02, (strength - 20000) / 500000)` capped at 2%. Total rate on plains: 1% (20k) to 3% (120k+). Terrain multiplier from destination (mountains 2.0x, etc.). Moving through enemy fortified region adds 4% harassment. Enemy garrison detachments add 2% harassment (stacks with fort for 6% total). Capital garrisons do NOT cause harassment. Cavalry 2-tile moves apply attrition for both tiles. Broken army flee to capital: no attrition (already shattered). **Friendly stable territory (own region, stability 76+): no march attrition** — good roads and supply lines eliminate march losses.

**Depot Forward Logistics (Phase 6.2.H):** Supply depots project a logistics benefit to adjacent regions. If the destination or any adjacent region has a friendly undamaged supply depot, movement attrition is halved (0.5x after terrain). Does NOT stack, does NOT affect retreat/harassment/supply attrition. This makes depots an offensive logistics tool: build a depot at the border before pushing into enemy territory.

**Capture Hint (Session 31):** After a player marshal moves, adjacent enemy regions that are undefended (no enemy marshals, no garrison >= 5k, no player-placed garrison) and have FULL or PARTIAL visibility get a `[HINT]` in the move result message. Also adds `capture_hints` list to result dict for Godot UI. Enemy marshals don't receive hints.

**Key code:** `region.py::SUPPLY_BY_TYPE`, `region.py::supply_capacity`, `world_state.py::process_supply_attrition()`, `executor.py::_calculate_movement_attrition()`, `executor.py::_has_depot_supply_bonus()`, `executor.py::_execute_move()` (capture hint block)

### Contested Capture (Phase 6.2.F)

When capturing a region with a **functional fortification** (undamaged), instant capture is blocked. Instead, the marshal starts an **occupation**:
- **Ungarrisoned fort:** 1 turn to capture
- **Garrisoned fort** (defenders beaten this turn): 2 turns to capture
- **Damaged fort:** Instant capture (no holdout)

During occupation:
- Marshal is **blocked** from most actions (only wait/retreat/end_turn/status)
- Occupation ticks at turn start in `_process_tactical_states()`
- If marshal **leaves** the region, occupation is abandoned
- If marshal is **forced to retreat**, occupation is cleared
- AI marshals with occupation in progress are **skipped** by enemy AI evaluator

On occupation completion, capture + plunder/secure choice fires normally.

**Key code:** `marshal.py::occupation_*` fields, `executor.py::_attempt_region_capture()`, `world_state.py::_process_tactical_states()` (occupation progression), `world_state.py::_apply_occupation_capture_effects()`

### Capital Garrison System

Capital regions have a standing garrison that must be defeated before the capital can be captured. This prevents instant capital snipes and makes capital defense meaningful.

**Setup:** All capital regions start with 15,000 garrison troops (`garrison_strength` field on Region). Garrison regenerates +2,000 per turn, capped at 15,000.

**Garrison Combat:** When a marshal moves into a capital with garrison >= 5,000, simplified garrison combat is triggered:
- **Garrison effective defense** = `garrison_strength × (1 + terrain_bonus) × (1 + fort_bonus)` where `fort_bonus = 0.25` if fortification building exists
- **Proportional damage exchange:** Attacker damage ratio capped at 0.35, garrison damage ratio capped at 0.50
- **Minimum losses enforced:** 2% attacker, 10% garrison — prevents stalemates
- **If garrison drops below 5,000:** Garrison destroyed, attacker moves in, capture proceeds normally
- **If garrison holds (>= 5,000):** Attacker stays in place, damage dealt but no capture

**Below threshold:** If garrison is between 0-4,999 when a marshal enters, it collapses immediately (set to 0) and normal capture proceeds.

**AI Integration:**
- **P-1:** AI marshals don't recklessly abandon capitals — garrison check added to retreat logic
- **P4.25:** AI evaluates garrison assault — handles both capital garrisons (>= 5k) and detachment garrisons (any size)
- **P4.5:** AI skips garrisoned regions (>= 5k or detachment) when looking for undefended captures

**Capital Proximity Alerts:** When enemy marshals are adjacent to the player's capital, a warning event is generated in tactical events.

**Key code:** `region.py::garrison_strength`, `executor.py::_resolve_garrison_combat()`, `world_state.py::_setup_initial_control()` (init), `world_state.py::advance_turn()` (regen), `enemy_ai.py::_find_garrison_attack()`, `turn_manager.py::_check_capital_proximity()`

### Player Garrison Command (Session 31)

Players and AI can detach 3,000 troops from a marshal to garrison a controlled region. Uses the same `garrison_strength` field as capital garrisons, distinguished by `garrison_detachment` boolean (renamed from `garrison_player_placed` in AI Garrison session).

**Mechanics:**
- **Cost:** 2 AP (real commitment — unified across player and AI)
- **Troops detached:** 3,000 from marshal
- **Minimum marshal strength:** 8,000 (player), 20,000 (AI — `AI_GARRISON_MIN_STRENGTH`)
- **Nation cap:** Maximum 3 garrisons per nation (`GARRISON_MAX_PER_NATION`), includes capital garrisons. Berthier warning on cap, no AP consumed.
- **Region requirements:** Controlled by marshal's nation, no existing garrison, no enemies present

**Differences from capital garrison:**
| Property | Capital Garrison | Detachment Garrison |
|----------|-----------------|---------------------|
| Regeneration | +2,000/turn (cap 15k) | None |
| Collapse threshold | < 5,000 auto-collapses | Fights to destruction (> 0) |
| `garrison_detachment` | `False` | `True` |

**Garrison combat:** Both types use `_resolve_garrison_combat()`. Detachment garrisons fight until `garrison_strength <= 0`.

**Detachment harassment:** Enemy garrison detachments cause 2% attrition to armies moving through the region (including retreats). Capital garrisons do NOT harass — forts already cover that. Stacks with fort harassment (4% + 2% = 6%). This gives detachments passive area-denial value beyond just blocking capture.

**AI garrison placement (P6.75):** AI uses same `_execute_garrison()` (Building Blocks). Heuristic: garrison border regions with excess strength. Max 1 per nation per turn. See `docs/ENEMY_AI_REFERENCE.md` for full conditions.

**P4.25 garrison awareness:** AI evaluates ALL garrisons for attack — capital garrisons >= 5k AND detachment garrisons of any size. P4.5 (undefended capture) skips detachment garrisons, deferring them to P4.25.

**Serialization:** `garrison_detachment` in `region.py` `to_dict()`/`from_dict()`. Backward compat: `from_dict` accepts both `garrison_detachment` and old `garrison_player_placed` key.

**Key code:** `executor.py::_execute_garrison()`, `region.py::garrison_detachment`, `world_state.py::advance_turn()` (regen exclusion), `enemy_ai.py::_consider_garrison()` (P6.75), `enemy_ai.py::_find_garrison_attack()` (P4.25)

### AI Admin Phase (Phase 6.2.G)

AI nations get an admin phase each turn, using the same executor as the player (Building Blocks principle).

**Admin AP:** 2 per turn (hardcoded, not serialized — computed fresh each turn).

**Priority order** (evaluated top-to-bottom, first valid action wins each AP):

| Priority | Action | Condition |
|----------|--------|-----------|
| 1 | Recruit | Any marshal below 40% strength |
| 2 | Build fortification | At border regions (adjacent to enemy) |
| 3 | Repair building | Any damaged building in controlled region |
| 4 | Repair war damage | Any region with war_damage > 0 |
| 5 | Save AP | No valid action — unused AP converts to +75 gold each |

**Implementation:**
- `enemy_ai.py::execute_admin_phase()` — main entry point (7 methods: main entry + 5 helpers + `_pick_admin_action`)
- `_acting_nation` field in command dict — lets executor check correct nation's control and treasury (not player's)
- Wired in `turn_manager.py` — runs after enemy military phase, before strategic orders

**Economy command:**
- `_execute_economy()` in `executor.py` — free action (0 AP), shows nation's financial summary
- Aliases: `economy`, `treasury`, `finances`
- Wired in parser, validation, mock parser

**Turn summary financial report:**
- `_execute_end_turn()` appends financial report showing income, upkeep, net gold, and balance for the player's nation

**UI wiring:**
- Occupation fields (`occupation_region`, `occupation_turns_held`, `occupation_turns_required`) added to `tactical_state` dict in `main.py::_get_map_data()` for Godot marshal tooltip display

### AI Homeland Defense (P3.7)

When a nation has lost regions it originally controlled, the AI redirects the nearest available marshal to recapture. Evaluated between P3.5 (Fortification Opportunity) and P4 (Attack Opportunity). Tracks claimed targets in `_homeland_recapture_targets` to prevent multiple marshals converging on the same region. Uses `world.nation_starting_regions` to identify lost territory.

**Key code:** `enemy_ai.py::_find_homeland_recapture()`, `world_state.py::nation_starting_regions`

---

## 9. Fog of War

> **Full spec:** `docs/FOG_OF_WAR_SPEC.md` (16 sections)
> **Implementation plan:** `docs/FOG_IMPLEMENTATION_PLAN.md` (Sessions 33-36)
> **Status:** COMPLETE (Sessions 33-36, Feb 2026)

### Core Principle

**"Fog filters information, not mechanics."** Game mechanics (combat, pathfinding decisions, sally ratios) use real world data — the executor is deterministic (Golden Rule #6). Fog only filters what the player sees in messages and UI. The simulation is accurate; the player's view is filtered.

Exceptions where fog affects mechanics:
- **PURSUE pathfinding** uses last-known location from intel store
- **Cautious pathfinding** only avoids PARTIAL+ visible enemies

### Visibility Levels

| Level | Source | What You See |
|-------|--------|-------------|
| **FULL** | Own region w/ army (**ephemeral**), scouted (2 turns), post-battle (2 turns) | Names, exact strength, morale, stance, buildings |
| **PARTIAL** | Adjacent to army, watchtower, own region w/o army, transit | Names, strength band only |
| **STALE** | 3-4 turns since last update | Frozen snapshot, marked with age |
| **LAST_KNOWN** | 5+ turns since last update | Old snapshot, position likely wrong |
| **UNKNOWN** | Never scouted, no adjacency | Region exists, controller known, no military intel |

### Visibility Calculation (`calculate_visibility()`)

Runs at: game init, end of `_advance_turn_internal()`, after save load, **after each player move**.

Priority order (highest wins):
1. **Pre-pass:** Ephemeral marshal_present downgrade — regions FULL from marshal presence lose FULL when marshal leaves (falls back to scout/battle FULL if recent, otherwise drops to PARTIAL for main loop to handle)
2. **Step 0:** Marshal-present → FULL (any region with a friendly marshal)
3. **Step 1:** Own region → PARTIAL military + FULL economic
4. **Step 2:** Adjacent to friendly army → PARTIAL
5. **Step 3:** Adjacent to active watchtower in own region → PARTIAL
6. **Decay:** Regions not refreshed → age from `last_updated_turn`

### FULL Visibility: Ephemeral vs Persistent

- **Ephemeral FULL** (marshal_present): Only while your army stands in the region. When the marshal leaves, FULL is lost immediately. The region drops to whatever the next applicable source provides (PARTIAL from adjacency, own-territory, etc.).
- **Persistent FULL** (scout, battle): Lasts for 2 turns after the scout/battle. Both scout and battle set `last_scouted_turn`. If a marshal was present AND the region was scouted/battled, the persistent FULL survives the marshal leaving.

This makes scouting valuable — it's the only way to lock in detailed intel on a region you don't occupy.

### Decay Timeline

Same for FULL and PARTIAL, offset from `last_updated_turn`:
- Turns 0-2: Stays at current level (FRESH_TURNS = 2)
- Turns 3-4: Degrades to STALE (STALE_TURN_START = 3)
- Turns 5+: Degrades to LAST_KNOWN (LAST_KNOWN_TURN_START = 5)

### Strength Bands (PARTIAL/STALE)

| Band | Range |
|------|-------|
| No forces | 0 |
| Screening force | 1 – 4,999 |
| Small force | 5,000 – 14,999 |
| Substantial force | 15,000 – 39,999 |
| Large force | 40,000 – 69,999 |
| Massive force | 70,000+ |

Multiple enemies in same region: combined total → single aggregate band.

### Key Files

| File | Purpose |
|------|---------|
| `backend/models/intel.py` | RegionIntel class, visibility constants, strength bands |
| `backend/intel_report.py` | Berthier Intelligence Report (fog-filtered status) |
| `backend/models/world_state.py` | `calculate_visibility()`, `decay_intel()`, `get_region_intel()`, `get_last_known_location()`, `get_visible_enemies_in_region()`, `get_filtered_game_state_summary()` |
| `backend/commands/strategic.py` | PURSUE fog validation, cautious pathfinding `fog_aware`, contact interrupt discovery messages |
| `backend/commands/disobedience.py` | Davout PURSUE fog-aware objection |
| `backend/main.py` | `_filter_enemy_phase_by_visibility()`, `_filter_tactical_events_by_visibility()` |

### Intel Sources

Scouts, battles, transit, and adjacency update the intel store:
- **Scout:** `update_intel_from_scout()` → FULL on target region. Watchtower synergy: +1 turn freshness.
- **Battle:** `update_intel_from_battle()` → FULL on battle region. Wired at all 6 `resolve_battle` sites.
- **Transit:** `update_intel_from_transit()` → PARTIAL on regions an army passes through without stopping (cavalry 2-tile moves, strategic multi-step movement). Snapshots enemy names + strength band.
- **Adjacency/watchtower:** Refreshed each turn by `calculate_visibility()`.

### Display Filtering

All API responses go through `get_filtered_game_state_summary()` (replaced 29 call sites):
- Enemy marshals hidden at UNKNOWN
- Strength band only at PARTIAL/STALE
- Exact data at FULL
- Own region economic data always full

Enemy phase: `_filter_enemy_phase_by_visibility()` — battles involving player always shown, FULL actions shown, below-FULL suppressed.

Tactical events: `_filter_tactical_events_by_visibility()` — player events always shown, enemy events require PARTIAL+.

### Strategic Command Fog Interactions

- **PURSUE:** Reads target from intel store via `get_last_known_location()`. UNKNOWN → reject. STALE → pathfind to last known. Empty arrival → auto-cancel with intel age message.
- **SUPPORT:** Safety check uses `get_visible_enemies_in_region()`. Reports only visible enemies.
- **Cautious pathfinding:** `_get_enemy_occupied_regions(fog_aware=True)` for player marshals. Only avoids PARTIAL+ enemies.
- **HOLD sally:** Adjacent-only scan, no fog filter needed (adjacency guarantees PARTIAL).
- **Contact interrupt:** Discovery language for fogged regions ("Enemy forces discovered!"), standard for FULL.
- **Direct MOVE fog-awareness:** Destination enemy check is fog-filtered for player marshals. Below PARTIAL → walk in blind, discover enemies on arrival. FULL/PARTIAL → blocked with "use ATTACK" suggestion.
- **Destination blocked (all personalities):** When enemy holds the destination itself (not mid-path), all personality types halt instead of offering "go around". Literal halts. Aggressive auto-attacks at good odds or halts. Cautious halts. Interrupt type: `destination_blocked`.
- **Attack suggestion fog filter:** Out-of-range attack "Targets in range" and literal pursue popup only list PARTIAL+ visible enemies. Null-target auto-find uses `find_nearest_enemy(filter_fn=...)` for visibility check.

### Watchtower Building

| Property | Value |
|----------|-------|
| Cost | 250 gold, 2 turns |
| Effect | PARTIAL on all adjacent regions |
| Scout synergy | +1 turn FULL freshness |
| Damage | Major battle → damaged. Plunder → destroyed. Under construction + any damage → destroyed. |
| Repair | 150 gold, 2 turns |
| AI priority | P6.5 (after repair, before low-priority recruit) |

Dedicated field on Region (not a building slot). Every region type allowed.

### AI and Fog

AI is omniscient on 19 regions (spec §9.1). Uses `world.marshals` and `get_enemies_in_region()` directly. Only display paths use fog-filtered helpers. Auto-charge ignores fog (spec §9.2 — reckless cavalry finds trouble). Revisit at 80+ regions for EA 1805.

### Objection System + Fog

**V1 (disobedience.py):** Davout PURSUE objection is fog-aware (FULL: exact odds, PARTIAL: band comparison, STALE/UNKNOWN: staleness objection).

**V2a (objection_v2.py) — fog-migrated in V2b Session 2:** All objection helpers now use fog-filtered data. Key behaviors:

- **Step 0 rule:** Own region always FULL visibility (friendly marshal present → sees everything). Enforced in `_get_region_visibility()`.
- **Type A scan queries** (`_check_enemy_adjacent`, `_get_friendly_to_enemy_ratio`, `_path_crosses_enemy`/`_path_has_enemies`): Only detect enemies at PARTIAL+ visibility. STALE/UNKNOWN enemies invisible. Zero visible enemies → ratio 999.0.
- **Type B target queries** (`_get_attack_odds_ratio`, `_check_attack_target_fortified`): FULL=exact data, PARTIAL=band midpoint strength, STALE/UNKNOWN=1.0 odds / no fort info.
- **Band midpoints:** At PARTIAL visibility, exact strength replaced by band midpoint (2500/10000/27500/55000/85000) for ratio calculations.
- **4 fog-specific triggers:**
  - Attack into UNKNOWN: cautious → STRONG, aggressive → no concern
  - Attack on STALE intel: cautious → MODERATE, aggressive → MILD
  - Scout-shows-weakness: handled by fog-filtered ratio (no visible enemies = "defending nothing")
  - PURSUE no intel: cautious → STRONG, aggressive → MILD
- **Auto-propagated functions** (`_get_enemy_to_friendly_ratio`, `_is_outnumbered_2to1`, `_is_actually_threatened`): Fog-aware via delegation — no code changes needed.

### Map Visualization (Godot)

Backend sends `visibility_status` per region in `get_filtered_game_state_summary()`. Godot renders fog:

| Visibility | Region Overlay | Marshal Icon | Region Tooltip |
|-----------|---------------|-------------|----------------|
| **FULL** | No overlay (bright) | Full icon + name | Full detail |
| **PARTIAL** | Slight dim (30% alpha) | Dimmed silhouette + "?" | Full detail + "Intel: Partial" |
| **STALE** | Medium grey (50% alpha) | Faded silhouette + "?" | Full detail + "Intel: Stale" |
| **LAST_KNOWN** | Dark grey (65% alpha) | Not shown | Minimal: name, controller, "Last known (outdated)" |
| **UNKNOWN** | Near-black (75% alpha) | Not shown | Minimal: name, controller, "No intelligence" |

Fogged enemies (PARTIAL/STALE) use `fogged_forces[]` from backend response. Tooltip shows name, nation, strength band, intel quality.

Key files: `map.gd` (`_draw_fogged_force_icons()`, `_draw_fogged_tooltip()`, `FOG_OVERLAYS` const).

---

## 10. Manpower Pools

Nation-level infantry/cavalry/artillery reserve pools that gate recruitment. Cavalry and artillery are precious and slow to rebuild.

### Core Concept

Marshal type (`cavalry: bool`, `artillery: bool`) auto-determines which pool is drawn from. No player choice needed — the strategic choice is *which marshal to reinforce*.

| Marshal type | Pool | Batch | Gold cost | Example |
|-------------|------|-------|-----------|---------|
| `artillery: True` | artillery | 3,000 | 400g base | Drouot |
| `cavalry: True` | cavalry | 5,000 | 300g base | Ney, Uxbridge |
| neither | infantry | 10,000 | 200g base | Davout, Wellington |

### Starting Pools

| Nation | Infantry | Cavalry | Artillery |
|--------|----------|---------|-----------|
| France | 80,000 | 15,000 | 10,000 |
| Britain | 50,000 | 8,000 | 5,000 |
| Prussia | 60,000 | 10,000 | 5,000 |

### Regen (per turn)

- Infantry: 5,000/turn base (no territory dependency)
- Cavalry: 500/turn base + 500 per plains region + 750 per stables building
- Artillery: 300/turn base + 200 per urban region controlled
- Pool caps: 100,000 infantry, 30,000 cavalry, 20,000 artillery
- Damaged/under-construction stables don't contribute
- Nations with 0 regions still get base regen

### Stables Building

| Property | Value |
|----------|-------|
| Gold cost | 300g |
| Build time | 2 turns |
| Allowed in | capital, major_city, city |
| Cavalry regen bonus | +750/turn |

### Cost Modifiers

Same `_calculate_recruit_cost(region, world, base_cost)` for both types:
- Capital: 75% of base (infantry 150g, cavalry 225g)
- Settling (stability 51-75): 150% of base (infantry 300g, cavalry 450g)
- Normal: base (infantry 200g, cavalry 300g)

### Error Messages (Berthier Voice)

All recruitment failures use Berthier's voice. Pool empty error includes regen rate and estimated turns.

### AI Awareness

- `_find_weakest_marshal_for_admin` skips marshals whose pool can't support a recruit
- `_pick_admin_action` uses correct gold cost per marshal type (400g artillery, 300g cavalry, 200g infantry)
- Priority 4.5: Build stables when cavalry pool < 60% cap and nation has cavalry marshals
- Artillery moved_this_turn gate in `_find_attack_opportunity` — AI won't attack with artillery that moved this turn

### HUD Display

Manpower pools are displayed permanently in the Godot status bar alongside Turn, Actions, Admin, and Gold.

- **Location:** StatusSection → ManpowerDisplay (HBoxContainer after GoldDisplay)
- **Format:** `Inf: 80,000  Cav: 15,000` with comma formatting
- **Colors:** Infantry green `(0.6, 0.8, 0.6)`, Cavalry reddish `(0.8, 0.5, 0.5)`
- **Low-pool warnings:** Color shifts to orange then red when pools drop below thresholds
  - Infantry: orange < 40k, red < 20k
  - Cavalry: orange < 10k, red < 5k
- **Data source:** `game_state.manpower_pools.infantry` / `.cavalry` (player nation only)
- **Update sites:** All 10 response handlers in `main.gd` (mirrors gold update pattern)

### Key Files

| File | What changed |
|------|-------------|
| `world_state.py` | Constants, `manpower_pools` field, `_process_manpower_regen()`, `get_cavalry_regen_rate()`, `get_artillery_regen_rate()`, serialization, `get_game_state_summary()` (manpower in API) |
| `region.py` | `"stables"` in `BUILDING_TYPES` |
| `executor.py` | `_execute_recruit` (pool drawing, type-based costs, Berthier voice), `_calculate_recruit_cost(base_cost)`, `_extract_building_type` (stables), `_execute_economy` (manpower section) |
| `enemy_ai.py` | Pool/cost-aware recruit, `_should_build_stables()`, `_find_best_stables_region()`, Priority 4.5 |
| `main.py` | `manpower_pools` in `/test` endpoint response |
| `main.tscn` | ManpowerDisplay nodes (InfLabel, InfValue, CavLabel, CavValue) |
| `main.gd` | `_apply_manpower()`, `_update_manpower_display()`, 10 update sites |
| `llm_client.py` | Optional `requested_type` extraction for soft correction |
| `schemas.py` | `requested_type` field on ParseResult |


## 11. Campaign Log

Fog-filtered event log overlay (Phase 6.5). Player can browse all narrative events grouped by turn.

### Event Types (14)

| Category | Types |
|----------|-------|
| Combat | `battle`, `bombardment`, `retreat`, `marshal_broken`, `marshal_recovered` |
| Territory | `region_captured` |
| Economy | `recruitment`, `building_started`, `building_completed`, `building_damaged`, `bankruptcy`, `desertion` |
| Command | `objection`, `strategic_order` |

### Fog Filtering Rules

| Event type | Rule |
|-----------|------|
| Player-nation events | Always shown |
| `objection`, `strategic_order` | Always shown (player-generated) |
| `battle`, `bombardment` | Player marshal involved OR region FULL visibility |
| `retreat`, `marshal_broken`, `marshal_recovered` | Player marshal involved OR region PARTIAL+ |
| `region_captured` (enemy) | Region PARTIAL+ |
| `bankruptcy` | Always shown (public knowledge) |
| Economy events (enemy) | Region PARTIAL+ |
| `intel_updated`, `intel_decayed`, `target_not_found` | Never shown (not in whitelist) |

### One-Liner Format

All one-liners include nation tags on marshal names: `Ney (France)`, `Wellington (Britain)`.
Missing nation fields gracefully omit the tag.

| Type | Format |
|------|--------|
| battle | `Ney (France) attacked Wellington (Britain) at Waterloo — Ney victory (8,000 / 5,000 casualties)` |
| bombardment | `Drouot (France) bombarded Waterloo — 3,000 casualties` |
| retreat | `Wellington (Britain) retreated from Waterloo to Brussels` |
| marshal_broken | `Wellington (Britain) was broken at Waterloo` |
| marshal_recovered | `Wellington (Britain) recovered at Brussels` |
| region_captured | `Brussels captured by France (secure)` |
| recruitment | `Ney (France) recruited 5,000 infantry` |
| building_started | `Construction started: Stables in Paris` |
| building_completed | `Construction complete: Stables in Paris` |
| building_damaged | `Building damaged: Stables in Waterloo` |
| bankruptcy | `Britain treasury bankrupt — desertion imminent` |
| desertion | `Desertion: Wellington (Britain) lost 2,000 troops` |
| objection | `Ney objected to attack (overruled)` |
| strategic_order | `Ney ordered to move to Brussels` |

### Godot Overlay

- Toggle: L key via top bar. Close: Esc, click outside, or L again.
- CanvasLayer 50 (information screen layer, managed by top bar).
- Turn headers expand/collapse on click. Most recent turn expanded by default.
- Empty turns (0 events after fog filtering) hidden.
- Turn 0 displayed as "Turn 0 — Setup".
- Category-colored BBCode icons: combat (gold X), territory (green >), economy (warm $), command (lavender !).

### Key Files

| File | Purpose |
|------|---------|
| `backend/campaign_log.py` | Type whitelist, fog filter, category map, one-liner formatter |
| `backend/main.py` | `GET /campaign_log` endpoint (groups by turn, strips battle_report, int wrapping) |
| `godot-client/.../campaign_log.gd` | Overlay UI, expand/collapse, BBCode rendering |
| `godot-client/.../campaign_log.tscn` | Scene layout |
| `tests/test_campaign_log.py` | 57 tests (whitelist, fog, format, defaults, endpoint) |

## 12. Top Bar & Screen Management

Unified top bar UI framework (Session A). Controller-based architecture: top bar owns buttons and state tracking, screens are independent CanvasLayers.

### Architecture

| Layer | Contents |
|-------|----------|
| Base | Map (Control node, no CanvasLayer) |
| 50 | Information screens (Event Log, Ledger, Generals, Dispatch) |
| 75 | Top bar + notification expanded detail panel |
| 100 | Modal dialogs (9 existing: objection, redemption, enemy_phase, etc.) |
| 101 | Pause menu |

### Behavior

- **One screen at a time.** Opening a new screen closes the current one.
- **Click active button = toggle off.**
- **All screens close on turn transition** (both manual and auto-advance paths, plus before enemy phase).
- **Terminal input stays active** while screens are open. Map interaction is blocked.

### Hotkeys

| Key | Action |
|-----|--------|
| L | Event Log (campaign log) |
| T | Ledger (strategic overview) |
| G | Generals (placeholder — disabled) |
| D | Dispatch re-read |
| Esc | Close screen first, then pause menu |

### Input Blocking (3 levels)

| State | Map | Map hotkeys | Screen hotkeys | Terminal | Esc |
|-------|-----|-------------|----------------|----------|-----|
| Nothing open | Yes | Yes | Yes | Yes | Opens pause |
| Screen open | Blocked | Blocked | Yes (switches) | Yes | Closes screen |
| Modal open | Blocked | Blocked | Blocked | Blocked | Dialog handles |

### Dispatch Re-read

- Backend stores `last_morning_dispatch` on WorldState each turn (via `build_morning_dispatch()`)
- `GET /dispatch` endpoint returns stored dispatch
- Godot `dispatch_view.gd` renders BBCode (duplicated from main.gd — documented tech debt)
- Empty dispatch shows "No dispatch available yet."

### Strategic Ledger (Session B)

- Backend: `build_strategic_ledger(world)` in `ledger.py` with 5 sections: forces, territories, economy, intel, manpower
- All values `int()` wrapped — no floats to Godot
- Forces: status priority chain (broken > retreating > drilling > fortified > strategic modes > idle), special flags, strategic order summary
- Territories: supply status (OK / Over capacity, no "Strained"), war_damage as `int(war_damage * 100)`, income via `get_effective_income()`, no `fortification_level` field
- Economy: treasury, income, upkeep, net, bankruptcy, construction queue, income breakdown
- Intel: fog-filtered enemy sightings, BAND_MIDPOINTS for estimated strength, nation summaries, unknown region count
- Manpower: `get_manpower_regen_rates(nation)` extracted as single source of truth (used by both `_process_manpower_regen()` and ledger), dynamic regen rates, `turns_until_full` calculation
- `GET /ledger` endpoint
- Godot: sub-tabbed screen (CanvasLayer 50), number keys 1-5 switch tabs, color coding for status/trust/morale/supply/bankruptcy/manpower

### Key Files

| File | Purpose |
|------|---------|
| `godot-client/.../top_bar.gd` | Controller: screen registration, toggle, close, button highlighting |
| `godot-client/.../top_bar.tscn` | CanvasLayer 75, bar layout with buttons + notification area + turn label |
| `godot-client/.../dispatch_view.gd` | Dispatch re-read screen (CanvasLayer 50) |
| `godot-client/.../dispatch_view.tscn` | Dispatch scene layout |
| `godot-client/.../strategic_ledger.gd` | Strategic ledger screen (CanvasLayer 50), 5 sub-tabs |
| `godot-client/.../strategic_ledger.tscn` | Ledger scene layout |
| `backend/game_logic/dispatch.py` | Morning dispatch builder (also stores on WorldState) |
| `backend/game_logic/ledger.py` | Strategic ledger builder (5 sections) |
| `backend/main.py` | `GET /dispatch`, `GET /ledger` endpoints |
| `tests/test_dispatch_view.py` | 8 tests (storage, serialization, endpoint, no-float) |
| `tests/test_ledger.py` | 54 tests (all sections + cross-cutting) |


## 13. Reinforcement System

Adjacent marshals automatically attempt to join ongoing battles before combat resolves. Both attacker and defender sides receive reinforcements independently (Building Blocks — AI uses identical code).

### Eligibility (13 Rules)

A marshal can reinforce if ALL of: same nation, adjacent region (not same region), strength > 0, not broken, not `retreated_this_turn`, `retreat_recovery == 0`, not fortified, not on HOLD (`holding_position`), not engaged (no enemies in their region), not drilling/drilling_locked, not `reinforced_this_turn`, not `moved_this_turn` (A-D2), not Hostile without SUPPORT (A-D4).

### Grouchy Rule (Personality Gate)

Literal-personality marshals are **blocked from reinforcing** unless they have a SUPPORT or PURSUE strategic order targeting a marshal who is **in the battle region** (A-D1 region-match). This is checked BEFORE arrival score — a blocked literal never rolls.

### Arrival Score Formula

```
score = base(50) + logistics*5 + relationship_mod + terrain_mod + personality_mod + support_bonus + variance
```

| Component | Values |
|-----------|--------|
| Base | 50 |
| Logistics | skill × 5 (range 5–50) |
| Relationship mod | -2→-20, -1→-10, 0→0, +1→+10, +2→+20 |
| Terrain penalty (departing) | plains: 0, forest: -10, hills: -5, mountains: -20, urban: 0, river_crossing: -5 |
| Personality mod | aggressive: +5, cautious: -5, literal: 0, balanced: 0, loyal: +3 |
| Support bonus | +10 if SUPPORT order targets primary combatant |
| Variance | random.randint(-8, 8) |

### Variable Threshold

| Condition | Threshold |
|-----------|-----------|
| Has SUPPORT or PURSUE order targeting participant | 60 |
| No relevant order | 65 |

### Fumble Roll (I3)

When score > 80: 5% failure chance (`random.randint(1, 20) == 1`). Prevents guaranteed success even with perfect stats.

### Trust Penalty

Failed reinforcement → -3 trust, UNLESS marshal personality is Literal. (Hostile marshals without SUPPORT are excluded at eligibility by Rule #13 and never enter the pipeline.)

### Physical Relocation & Ordering (A-C2)

On successful arrival:
1. Record `arrived_via_support` flag (if SUPPORT order active)
2. Relocate marshal to battle region (`marshal.location = battle_region`) — **except artillery** (Gate 4: artillery provides fire support from adjacent position, does NOT advance to front line)
3. Set `reinforced_this_turn = True` (all unit types, including artillery)
4. Clear path (but **NOT** strategic order yet)
5. Calculate coordination context (order still active for bonuses)
6. **THEN** clear strategic order (after coordination)
7. Artillery reinforcements explicitly added to casualty distribution participants despite not being in battle region

### Retreat on Loss

Reinforcers who relocated to the battle region return to their pre-arrival location if their side loses (spec: "reinforcer retreats with primary if battle lost"). Implemented via `reinforcer_origin` dict that tracks each reinforcer's location before relocation. After combat:
- If attacker lost: attacker-side reinforcers return to origin
- If defender lost: defender-side reinforcers return to origin
- Artillery never relocated in the first place (stays at origin regardless)
- Morale-based forced retreat (`<= 25`) runs first and takes priority

### Interaction with Coordination

- Arrived reinforcers (non-artillery) are **excluded** from adjacent ally count (`exclude_from_adjacent` parameter) because they relocated to battle region and are now same-region allies
- **Artillery exception (Gate 4):** artillery is NOT added to `arrived_names`/`exclude_from_adjacent` because it stays in its adjacent position — still counts as adjacent ally for +2% attack bonus
- Arrived non-artillery reinforcers **join** same-region coordination (counted as allies in battle region)
- Path B2: Reinforcers who arrived via SUPPORT count for `_has_dedicated_support()` check
- `reinforcement_results` passed through `_calculate_coordination_context()` → `_has_dedicated_support()`

### Serialization

`reinforced_this_turn` (bool, default False) is serialized on Marshal. Cleared at turn start in `world_state.py`.

### Key Files

| File | What changed |
|------|-------------|
| `executor.py` | `_is_reinforcement_eligible()`, `_calculate_arrival_score()`, `_calculate_reinforcements()`, wired into `_execute_attack()` |
| `marshal.py` | `reinforced_this_turn` field + serialization |
| `world_state.py` | Turn-start clearing of `reinforced_this_turn` |
| `objection_v2.py` | §6 SUPPORT objection triggers (aggressive→defensive, cautious→reckless) |
| `tests/test_reinforcement.py` | 49 tests across 12 classes |
| `tests/test_reinforcement_edge_cases.py` | 22 tests: rules 12-13, PURSUE region-match, Berthier advisory, SUPPORT objection triggers |

## 14. Win/Loss Relationship Formula

After a shared battle with 2+ same-nation participants, each ordered pair (A, B) rolls independently to check if A's opinion of B changes. Fires after `resolve_battle()` in `_execute_attack()`, before destruction/retreat processing. Casualties are read from `battle_result["attacker"]["casualties"]` (nested dict — both normal and deferred paths). SUPPORT orders are preserved through relationship processing so Hostile+SUPPORT marshals are correctly detected as Participating.

### Trigger

- 2+ same-nation marshals in the battle region
- Both attacker and defender sides processed independently
- Hostile marshals without SUPPORT order targeting primary are Non-Participating (excluded)

### Battle Severity

Based on winner/loser casualty exchange ratio:

| Severity | Condition |
|----------|-----------|
| Decisive | `ratio < 0.5` (winner took less than half loser's casualties) |
| Standard | `0.5 <= ratio <= 0.8` |
| Narrow | `ratio > 0.8` (nearly even) |

Special case: `loser_casualties == 0` → always decisive.

### WIN Formula (base 30)

```
score = 30 + severity_bonus + relationship_modifier + variance
```

| Component | Values |
|-----------|--------|
| Severity bonus | decisive: +15, standard: 0, narrow: -10 |
| Relationship modifier | Hostile(-2): -20, Rival(-1): 0, Professional(0): 0, Friendly(+1): -10, Devoted(+2): -20 |
| Variance | random.randint(-10, 10) |

**Threshold:** `score > 50` → relationship improves +1.

### LOSS Formula (base 15)

```
score = 15 + severity_bonus + relationship_modifier + variance
```

| Component | Values |
|-----------|--------|
| Severity bonus | decisive: +10, standard: 0, narrow: -5 |
| Relationship modifier | Hostile(-2): +15, Rival(-1): +5, Professional(0): 0, Friendly(+1): 0, Devoted(+2): 0 |
| Variance | random.randint(-10, 10) |

**Threshold:** `score > 50` → relationship degrades -1.

### Intentional Asymmetry

| Scenario | Max Score | Outcome |
|----------|-----------|---------|
| Hostile WIN (decisive) | 30+15-20+10 = **35** | NEVER improves (M1) |
| Devoted WIN (decisive) | 30+15-20+10 = **35** | NEVER improves (M1) |
| Rival WIN (decisive) | 30+15+0+10 = **55** | ~24% chance improvement |
| Hostile LOSS (decisive) | 15+10+15+10 = **50** | NEVER degrades — strict >50 (M2) |
| Professional LOSS (decisive) | 15+10+0+10 = **35** | NEVER degrades |

### Ordered Pairs (D4)

Uses `itertools.permutations(participants, 2)`. 3 marshals = 6 calls. Each direction (A→B, B→A) is independent — different relationships, different cooldowns, may produce different results.

### Cooldown

3 turns per direction. Tracked in `marshal.last_relationship_change_turn[other_name]`. A→B cooldown does NOT block B→A.

### Range & Per-Battle Cap

- Relationship range: [-2, +2] (enforced by `modify_relationship()`)
- Per-battle cap: ±1 maximum change per pair per battle

### Key Files

| File | What changed |
|------|-------------|
| `backend/game_logic/relationship.py` | `calculate_battle_severity()`, `check_shared_battle_relationship()`, `get_battle_participants()`, `process_battle_relationships()` |
| `backend/commands/executor.py` | Wired into `_execute_attack()` after combat notifications; SUPPORT clearing deferred to after relationship processing |
| `tests/test_relationship_formula.py` | 34 tests across 9 classes |
| `tests/test_casualty_distribution.py` | 63 tests (includes W-1 timing + conformance tests) |

## 15. Phase 7 UI Integration (Session 66)

### Coordination Readiness Tooltip (map.gd)

Region tooltips show coordination readiness when 2+ player marshals are co-located:
- **Combined arms count:** Number of distinct unit types (infantry/cavalry/artillery)
- **Co-location pairs:** Per-pair status ("dedicated" if ≥2 turns, "X turns" if accumulating)

Marshal tooltips show color-coded relationship lines: Hostile (red), Rival (orange), Professional (white), Friendly (green), Devoted (gold).

### Inline-Dramatic Reinforcement Display (main.gd)

Gold-bordered BBCode blocks for reinforcement arrival (green) and failure (red). Zero new popup types per MULTI_MARSHAL_SPEC §14.

### First-Time Coordination Tutorial

Fires ONCE per campaign when player's marshals achieve combined arms (type_count >= 2) in attack. Tracked by `coordination_tutorial_shown: bool` on WorldState. Displays Berthier's report explaining combined arms bonuses, relationship-based coordination improvement, and proportional casualty sharing.

### Backend Data for Tooltips

`get_game_state_summary()` includes per-player-marshal:
- `relationships`: dict of marshal_name → {value: int, label: str}
- `co_location_turns`: dict of ally_name → int (turns co-located)

All values `int()`-wrapped for Godot safety.

### Key Files

| File | What changed |
|------|-------------|
| `backend/commands/executor.py` | Tutorial trigger after coordination context calculation |
| `backend/models/world_state.py` | `coordination_tutorial_shown` field + relationship/co-location in game state summary |
| `backend/main.py` | `reinforcement_messages` and `coordination_tutorial` passthrough |
| `godot-client/project-sovereign/scripts/main.gd` | `_display_reinforcement_messages()`, `_display_coordination_tutorial()` |
| `godot-client/project-sovereign/scenes/map.gd` | Relationship lines in marshal tooltip, coordination readiness in region tooltip |
| `godot-client/project-sovereign/scripts/enemy_phase_dialog.gd` | Reinforcement messages in enemy phase battles |
| `tests/test_session66_integration.py` | 32 tests across 7 classes |
