# Enemy AI System Technical Reference

This document provides a comprehensive technical reference for the enemy AI system in Project Sovereign.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Decision Tree](#decision-tree)
4. [Personality Behaviors](#personality-behaviors)
5. [Action Processing](#action-processing)
6. [Integration Points](#integration-points)
7. [State Checks](#state-checks)
8. [Combat Integration](#combat-integration)
9. [Configuration Reference](#configuration-reference)
10. [TODOs and Future Work](#todos-and-future-work)
11. [Troubleshooting](#troubleshooting)

---

## System Overview

The Enemy AI system provides decision-making for enemy nations during their turn phase. It follows the **Building Blocks Principle** - enemies use the SAME executor as player commands, ensuring identical game mechanics.

### Key Principles

| Principle | Description |
|-----------|-------------|
| **Building Blocks** | All actions flow through `executor.execute()` |
| **Real Generals** | Enemy marshals have same combat modifiers, abilities, states |
| **Personality-Driven** | Aggressive vs Cautious behavior affects all decisions |
| **No Disobedience** | Enemies don't use objection system (AI decides = AI executes) |
| **Nation-Based Actions** | 4 actions per NATION, not per marshal |

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| EnemyAI | `backend/ai/enemy_ai.py` | Decision tree, action selection |
| TurnManager | `backend/game_logic/turn_manager.py` | Calls AI during end_turn |
| CommandExecutor | `backend/commands/executor.py` | Executes AI actions (same as player) |
| WorldState | `backend/models/world_state.py` | Stores `enemy_nations`, `nation_actions` |

---

## Architecture

### Turn Flow

```
Player ends turn
       |
       v
+-------------------------------+
| turn_manager.end_turn()       |
+-------------------------------+
       |
       v
+-------------------------------+
| _process_autonomy_countdown() |  <-- Player autonomous marshals
+-------------------------------+
       |
       v
+-------------------------------+
| _process_enemy_turns()        |  <-- ENEMY AI PHASE
|   |                           |
|   +-> For each enemy nation:  |
|       |                       |
|       +-> EnemyAI.process_nation_turn()
|           |                   |
|           +-> For each action:|
|               - Evaluate all marshals
|               - Pick best action
|               - Execute via executor
+-------------------------------+
       |
       v
+-------------------------------+
| world.advance_turn()          |  <-- Tactical states, turn increment
+-------------------------------+
       |
       v
+-------------------------------+
| _check_victory_conditions()   |  <-- Win/loss check
+-------------------------------+
```

### Class Structure

```python
class EnemyAI:
    # Attack thresholds by personality (MC-V-3: dead balanced/loyal rows
    # removed post-MC-4; .get(_, 1.0) is the save-compat floor)
    ATTACK_THRESHOLDS = {
        "aggressive": 0.7,   # Attacks even slightly outnumbered
        "cautious": 1.3,     # Needs clear advantage
        "literal": 1.0,      # Even odds — by the book
    }

    # Survival threshold (% of starting strength)
    SURVIVAL_THRESHOLD = 0.25

    def __init__(self, executor): ...
    def process_nation_turn(self, nation, world, game_state) -> List[Dict]: ...
    def _find_best_action(self, marshals, nation, world) -> Optional[Dict]: ...
    def _evaluate_marshal(self, marshal, nation, world) -> Tuple[Optional[Dict], int]: ...

    # Priority handlers (P1-P8)
    def _get_recovery_action(self, marshal, world) -> Optional[Dict]: ...
    def _get_survival_action(self, marshal, nation, world) -> Optional[Dict]: ...
    def _check_threats(self, marshal, nation, world) -> Optional[Dict]: ...
    def _find_attack_opportunity(self, marshal, nation, world) -> Optional[Dict]: ...
    def _consider_fortify(self, marshal, world) -> Optional[Dict]: ...
    def _consider_drill(self, marshal, world) -> Optional[Dict]: ...
    def _consider_strategic_move(self, marshal, nation, world) -> Optional[Dict]: ...
    def _get_default_action(self, marshal, world) -> Dict: ...
```

---

## Decision Tree

### Priority System

The AI evaluates each marshal and assigns a **priority score** (lower = more urgent). The action with the lowest priority across all marshals is executed.

| Priority | Name | Score | Trigger Condition |
|----------|------|-------|-------------------|
| P0 | Combat Engagement | 50 | Enemy in SAME region — MUST fight/retreat/wait |
| P1 | Retreat Recovery | 60 | `retreat_recovery > 0` |
| P2 | Critical Survival | 70 | `strength < 25% of starting` |
| P3 | Threat Response / Attack | 75 | Meets personality threshold |
| P3.25 | Counter-punch | — | Cautious: free attack after defense |
| P3.5 | Fortification Check | 77 | Unfortify if opportunity exists |
| P3.7 | Homeland Defense | 77 | Nation has lost originally-controlled regions — redirect nearest available marshal to recapture (capital=priority 2, range 6/unlimited, deathball split, enemy pathfinding for capitals) |
| P4 | Attack (standard) | 75 | Valid target + meets threshold |
| P4.25 | Garrison Assault | 77 | Adjacent garrisoned capital — strength ratio vs threshold |
| P4.5 | Capture Undefended | 80 | Adjacent undefended enemy region (skips garrisoned capitals) |
| P4.6 | Coordinated Attack Setup | 78 | Combined > 1.5x but solo < 1.5x, relationship >= Rival |
| P4.75 | Ally Support | 78 | Move toward outnumbered/engaged ally (relationship >= Rival, Devoted priority) |
| P4.8 | Consolidation | 78 | Weak marshal joins strong ally within 3 distance |
| P5 | Fortification | 85 | Cautious + no attack target |
| P6 | Drilling | 90 | Aggressive + position secure |
| P6.5 | Supply Awareness | 91 | Supply excess > 50% — mildly relocate to better-supplied region |
| P6.75 | Garrison Placement | 91 | Place capital garrison (max 1 per nation per turn) |
| P7 | Strategic Movement | 92 | Can advance toward enemy (P4.76 co-location guard, P4.77 cross-nation scoring) |
| P4.78 | Defensive Reinforcement | 92 | Move adjacent to threatened Rival+ ally for reinforcement readiness |
| P7.5 | Stagnation Breaker | 93 | Graduated escalation: Turn 2 unfortify, Turn 3+ lowered attack threshold |
| P8 | Default | 95 | Stance adjustment or wait |

### Priority 6.5: Supply Awareness

Low-priority supply relocation check. The AI prioritizes combat, threats, and attacks first — supply relocation only happens when there is nothing more important to do. If attrition weakens the marshal, normal recruitment handles rebuilding.

Triggered when marshal is in a region where supply excess exceeds 50% and no higher-priority action is available.

**Behavior:**
- Scans adjacent friendly/neutral regions for better supply margin
- Picks the region with best `supply_capacity - total_troops_there` margin
- Will not move if no adjacent region has positive net margin (stays and takes attrition)
- This is a mild optimization, not a panic reaction — the AI will not abandon combat positions or skip attacks to avoid attrition

### Priority 4.6: Coordinated Attack Setup (Session 63)

Stages coordinated attacks when the marshal can't attack alone but combined force with nearby allies would succeed.

**Trigger:** Adjacent enemy exists AND solo ratio < 1.5x AND nearby allies (within 2 distance) with relationship >= Rival would push combined ratio > 1.5x.

**Behavior:**
- Scans adjacent enemy-held regions for defenders
- Excludes undefended regions (P4.5 handles those)
- Counts co-located + nearby allies with relationship >= Rival (-1)
- Hostile (-2) allies excluded from combined strength
- Returns MOVE toward nearest eligible ally to co-locate
- Once co-located, P4 (normal attack) handles the actual attack using combined strength

### Priority 4.75: Ally Support — Relationship Filtering (Session 63)

Enhanced existing ally support with relationship awareness.

**Changes from base P4.75:**
- Hostile (-2) allies filtered out — will not receive support
- Candidates sorted by relationship: Devoted (+2) → Friendly (+1) → Professional (0) → Rival (-1)
- Ties broken by threat level (existing behavior preserved)

### Priority 4.76: Co-Location Persistence Guard (Session 63)

**Not a standalone priority** — implemented as an early-return guard inside `_consider_strategic_move()`.

**Trigger:** Marshal co-located with same-nation ally AND hasn't moved this turn (settled) AND enemy threat in current or adjacent region.

**Behavior:**
- Returns None from `_consider_strategic_move()`, preventing P7 movement
- Marshal falls through to P7.5/P8 (typically waits)
- Prevents AI from moving away from a beneficial co-located position near threats
- Does NOT fire if marshal just arrived (moved_this_turn = True) or if no threat nearby

### Priority 4.77: Cross-Nation Adjacency Scoring (Session 63)

**Not a standalone priority** — scoring modifier inside `_consider_strategic_move()`.

**Scoring bonuses for candidate movement positions:**
- Adjacent to Devoted (+2) ally: +10 score
- Adjacent to Professional (0) or Friendly (+1) ally: +5 score
- Adjacent to Rival (-1) or Hostile (-2): 0 bonus
- Applied as tiebreaker alongside combined arms awareness (+20 for completing triangle)
- Works for same-nation and coalition allies (not player nation)

### Priority 4.78: Defensive Reinforcement Positioning (Session 63)

Moves adjacent to a threatened ally for reinforcement readiness. Fires after P7, before P7.5.

**Trigger:** Ally with relationship >= Rival is threatened (enemy in or adjacent to their region) AND marshal is NOT already adjacent to or co-located with that ally.

**Behavior:**
- Finds all threatened allies (enemy adjacent), filtered by relationship >= Rival
- If already adjacent to any threatened ally, returns None (already positioned)
- Among reachable positions adjacent to ally, prefers those also adjacent to enemy
- Returns MOVE to best position, or None if unreachable

### Attack Threshold +8% Coordination Estimate (Session 63)

In `_find_attack_opportunity()`, the effective strength ratio is inflated by +0.08 per co-located ally. Additive: solo ratio 1.1 + 2 allies = 1.26. Makes AI slightly more willing to attack when it has friends nearby. Personality thresholds (cautious 1.3, balanced 1.0, aggressive 0.7) are NOT changed.

### Artillery Stagnation Override (Session 63)

In `_score_artillery_position()`, when `ai_stagnation_turns >= 3`, frontline avoidance penalties are reduced:
- Unscreened frontline: -50 → -20
- Screened frontline: -30 → -10
- Non-artillery marshals unaffected (they don't use this scoring method)
- Prevents artillery paralysis when the front line collapses around it

### Priority 1: Retreat Recovery

When a marshal is in retreat recovery, they have limited options:

```python
# Allowed during recovery
allowed = ["move", "wait", "defend", "defensive_stance", "neutral_stance"]

# Blocked during recovery
blocked = ["attack", "fortify", "drill", "scout", "aggressive_stance"]
```

**AI Behavior:** Switch to defensive stance if not already, then wait.

### Priority 2: Critical Survival

Triggered when `marshal.strength < 25% of starting_strength`.

**AI Behavior:**
- If enemy adjacent: Retreat to safety
- If no enemy adjacent: Defend/wait

### Priority 3: Threat Response

Triggered when a stronger enemy is adjacent.

**AI Behavior by Personality:**
- **Cautious:** Switch to defensive stance, then fortify
- **Aggressive:** May still attack (handled in P4)

### Priority 3.7: Homeland Defense (Recapture System)

When a nation has lost regions it originally controlled (tracked via `world.nation_starting_regions`), available marshals are redirected to recapture.

**Capital Elevation:** When the nation's capital is lost, homeland defense fires BEFORE P3 threat response at priority 2 (survival-level). This ensures capital recapture is never blocked by cautious marshals fortifying.

**Range:** 6 hops for normal regions, unlimited for capitals (was: 3 hops for all).

**P3 Throttling:** When 2+ regions are lost, only 1 marshal per nation stays on P3 threat defense. The rest fall through to P3.7 homeland recapture, preventing the entire army from turtling while territory is lost.

**Deathball Prevention:** The "someone closer" check now requires the closer marshal to be *available* (not fortified, drilling, broken, or recovering). Marshals track their assigned recapture target (`_recapture_marshal_assignments`) so multiple marshals split across different lost regions instead of all converging on one.

**Enemy Pathfinding:** For capital recapture only, marshals can path through enemy-occupied regions if they have at least 50% of the enemy's strength (P0 engagement handles the fight on arrival). Non-capital recapture still blocks enemy-occupied regions.

**Stagnation Fixes:**
- Skipped marshals (priority 999) now have their stagnation counter incremented
- Stagnation breaker returns `wait` instead of `None` (makes marshal visible to tracker)
- Cautious advance fallback allows non-friendly territory at stagnation >= 3

### Priority 4: Attack Opportunity

Evaluates all enemies in range against personality threshold.

**Attack Thresholds:**

| Personality | Threshold | Meaning |
|-------------|-----------|---------|
| Aggressive | 0.7 | Attacks at 70% strength ratio |
| Cautious | 1.3 | Only attacks with 30% advantage |
| Others | 1.0 | Only attacks at even odds or better |

**Target Selection:**
- **Aggressive:** Prefer weakest enemy (easy kill)
- **Cautious/Others:** Prefer nearest enemy

**Pre-Attack Actions:**
- If has drill bonus (`shock_bonus > 0`): Attack immediately to use it
- If aggressive and not in aggressive stance: Change stance first

### Priority 5: Fortification (Cautious Only)

Cautious marshals fortify when:
- Not already fortified at max
- Not drilling
- In defensive stance (or will switch first)

### Priority 6: Drilling (Aggressive Only)

Aggressive marshals drill when:
- Not already drilling or have bonus
- No enemy adjacent (vulnerable during drill)
- Position is secure

### Priority 7: Strategic Movement

**Aggressive:** Move toward nearest enemy
**Cautious:** Stay put (no movement action)

### Priority 8: Default

**Aggressive:**
1. Switch to aggressive stance if not already
2. Wait

**Cautious:**
1. Switch to defensive stance if not already
2. Defend

---

## Personality Behaviors

### Wellington (Britain - Cautious)

| Situation | Behavior |
|-----------|----------|
| Default stance | DEFENSIVE |
| Attack threshold | 1.3 (needs 30% advantage) |
| Enemy adjacent | Fortify if possible |
| No threats | Maintain position |
| Outnumbered | Never attacks |

**Typical Turn:**
1. stance_change -> defensive
2. fortify
3. defend
4. defend

### Blucher (Prussia - Aggressive)

| Situation | Behavior |
|-----------|----------|
| Default stance | AGGRESSIVE |
| Attack threshold | 0.7 (attacks when outnumbered) |
| Enemy in range | Attack immediately |
| No enemy | Drill for shock bonus |
| After drill | Move toward enemy |

**Typical Turn:**
1. stance_change -> aggressive
2. attack (uses shock bonus if available)
3. attack or move
4. drill (if safe) or wait

### Mack / Buxhowden / AI-run Deroy (Literal) — MC-V-2, July 11 2026

Enemy-nation literal marshals play LITERAL (previously aliased to cautious).
Single source: module-level `get_effective_ai_personality` in `enemy_ai.py` —
the literal→cautious conversion now applies ONLY to the player's own literal
marshals gone autonomous.

| Situation | Behavior |
|-----------|----------|
| Attack threshold | 1.0 (even odds), mood variance ±8% (most predictable) |
| Stronger enemy adjacent | NO defensive-stance/fortify reflex (P3 passes through) |
| Threatened in P7 | NO fall-back — stands his ground |
| Unthreatened in P7 | Holds his standing disposition; the stagnation breaker (turn 2+) is what finally moves him ("new orders arrive") |
| P5 fortify / P6 drill | Never on his own initiative (cautious-only / aggressive-only) |
| P8 default | wait (no stance fiddling) |

Net read: Mack sits at Ulm and gives battle at fair odds without ever
improvising; Buxhowden is always late. Combat kit (Immovable hold) was always
GR5-clean; this decision fixed the DECISION layer. Pins:
`tests/test_mc_personality_assurance.py` (threshold divergence, stands-where-
cautious-falls-back, attacks-even-odds-where-cautious-declines).

---

## Action Processing

### Action Budget

Each nation gets a fixed action budget per turn:

```python
# world_state.py
self.nation_actions = {
    "Britain": 4,
    "Prussia": 4,
}
```

### Free vs Paid Actions

```python
# Free actions (don't consume budget)
free_actions = ["status", "help", "end_turn", "unknown", "retreat", "debug", "wait"]

# Variable cost actions (stance_change)
# Any → Neutral: FREE (0 actions)
# Neutral → Defensive/Aggressive: 1 action
# Defensive ↔ Aggressive: 2 actions

# All other actions cost 1 point
```

### Variable Action Cost Handling (January 2026 Fix)

The AI now properly handles variable action costs from the executor:

```python
# Check for variable_action_cost in result
variable_cost = result.get("variable_action_cost")
if variable_cost is not None:
    # Use actual cost from executor (0, 1, or 2)
    actual_cost = variable_cost
else:
    # Standard action - 1 if not free, 0 if free
    actual_cost = 1 if not is_free_action else 0

# Consume correct number of actions
actions_remaining -= actual_cost
```

### Safeguards Against Infinite Loops

```python
# enemy_ai.py
max_free_actions = 2        # Max free actions per turn
max_total_actions = actions_remaining * 2  # Absolute limit
```

### Action Execution

```python
def _execute_action(self, action: Dict, game_state: Dict) -> Dict:
    command = {
        "command": {
            "marshal": action["marshal"],
            "action": action["action"],
            "target": action.get("target"),
            "type": "specific"
        }
    }
    result = self.executor.execute(command, game_state)
    return result
```

**CRITICAL:** Same executor as player. No special enemy combat code.

---

## Integration Points

### WorldState Requirements

```python
# Required fields in WorldState
self.enemy_nations = ["Britain", "Prussia"]
self.nation_actions = {"Britain": 4, "Prussia": 4}
self.marshals = {}  # Unified dict (player + enemy)
```

### Nation-Aware Methods Used by AI

| Method | Purpose |
|--------|---------|
| `get_marshals_by_nation(nation)` | Get all marshals for a nation |
| `get_enemies_of_nation(nation)` | Get enemies from nation's perspective |
| `get_enemy_at_location_for_nation(loc, nation)` | Find enemy at location |
| `get_region(name)` | Get region data |
| `get_distance(a, b)` | BFS pathfinding |

### Executor Integration

**CRITICAL FIX (January 2025):** Enemy actions must NOT consume player's action economy.

```python
# executor.py - Check if player action before consuming
is_player_action = True
marshal_name = command.get("marshal")
if marshal_name:
    executing_marshal = world.get_marshal(marshal_name)
    if executing_marshal and executing_marshal.nation != world.player_nation:
        is_player_action = False  # Enemy AI action

if result.get("success") and action_costs_point and is_player_action:
    # Only consume player actions for player marshals
    action_result = world.use_action(action)
```

---

## State Checks

### Before Attack

```python
def _find_attack_opportunity(self, marshal, nation, world):
    # Cannot attack if drilling
    if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
        return None

    # Cannot attack if fortified (must unfortify first)
    if getattr(marshal, 'fortified', False):
        return None

    # Cannot attack if broken
    if getattr(marshal, 'broken', False):
        return None
```

### Before Drill

```python
def _consider_drill(self, marshal, world):
    # Cannot drill if already drilling
    if getattr(marshal, 'drilling', False) or getattr(marshal, 'drilling_locked', False):
        return None

    # Cannot drill if already have bonus
    if getattr(marshal, 'shock_bonus', 0) > 0:
        return None

    # Cannot drill with enemy adjacent
    for enemy in world.get_enemies_of_nation(marshal.nation):
        if enemy.location in marshal_region.adjacent_regions:
            return None
```

### Before Fortify

```python
def _consider_fortify(self, marshal, world):
    # Cannot fortify if already fortified at max
    if getattr(marshal, 'fortified', False):
        return None

    # Cannot fortify if drilling
    if getattr(marshal, 'drilling', False):
        return None

    # Must be in defensive stance
    if marshal.stance != Stance.DEFENSIVE:
        return stance_change action first
```

---

## Combat Integration

### Same Combat Resolver

Enemy attacks use `combat.resolve_battle()` - identical to player attacks.

### Modifier Application

Enemy marshals get same personality modifiers:

| Marshal | Attack Modifier | Defense Modifier |
|---------|-----------------|------------------|
| Wellington | -5% (cautious) | +20% (defensive stance + cautious) |
| Blucher | +15% (aggressive stance) | -10% (aggressive stance) |

### Forced Retreat

At 25% morale, enemies forced to retreat - same rules as player:
- Find safe retreat destination
- Enter 3-turn recovery
- Broken if surrounded

### Flanking

Flanking bonus applies automatically via `world.record_attack()`:
- Multiple enemies attacking same target from different regions = bonus
- AI doesn't explicitly coordinate, but can achieve flanking naturally

---

## Configuration Reference

### Constants

| Constant | Value | Location |
|----------|-------|----------|
| `ATTACK_THRESHOLDS["aggressive"]` | 0.7 | `enemy_ai.py:32` |
| `ATTACK_THRESHOLDS["cautious"]` | 1.3 | `enemy_ai.py:33` |
| `SURVIVAL_THRESHOLD` | 0.25 | `enemy_ai.py:41` |
| `LOW_STRENGTH_THRESHOLD` | 0.50 | `enemy_ai.py:44` |
| `max_free_actions` | 2 | `enemy_ai.py:93` |

### Nation Configuration

```python
# world_state.py
self.enemy_nations = ["Britain", "Prussia"]
self.nation_actions = {"Britain": 4, "Prussia": 4}
```

---

## Round-Robin System

Prevents single marshal monopolizing actions.

```python
_marshals_done_this_turn: set  # Tracks who acted

# After marshal takes non-critical action:
if priority > 60:  # Not survival-critical
    _marshals_done_this_turn.add(marshal.name)
    # Skip this marshal until others have acted

# Critical override (priority <= 60):
# Survival actions bypass round-robin
```

---

## Stagnation Counter

Prevents marshals getting stuck doing nothing. Persisted on `world.ai_stagnation_turns`.

| Stagnation Turns | Escalation |
|------------------|------------|
| 0-1 | Normal behavior |
| 2 | Allow drill even with adjacent enemies |
| 1+ | Cautious marshals: advance toward nearest enemy if not threatened/fortified |
| 3 | Unfortify + move toward nearest ally |
| 4 | Lower attack threshold by 20% |
| 5+ | Lower threshold by 10% more (floor 0.3) |
| 3+ (surrounded) | Attack weakest adjacent enemy if no safe move exists |

**Resets on:** Attack (win/lose), capture region, move toward enemy, consolidation move.
**NOT meaningful:** defend, drill, wait.
**Stagnation fix:** Fortify only counts as meaningful (resets stagnation) if an enemy is within 2 regions. Fortifying with no nearby threat is treated as stagnation.

### Re-Fortify Cooldown

Every unfortify path sets a 2-turn **re-fortify cooldown** on the marshal. This prevents the fortify→unfortify oscillation loop.

- **Set by:** Stagnation breaker (P7.5), P3.5 CHECK 0 (engaged), CHECK 1 (capture opportunity), CHECK 2 (reposition), CHECK 3 (ally support)
- Stored in `world.ai_refortify_cooldown` (Dict[str, int])
- Blocks P3 (threat fortify), P5 (fortification), and P8 (default fortify) when cooldown > 0
- Also blocked when marshal is in `_unfortified_this_turn` set (same-turn guard)
- Decremented at start of each `process_nation_turn()`
- Removed when it reaches 0
- **Artillery exemption:** Artillery marshals skip P3 fortify entirely (fall through to P4 bombardment)
- **P8 wait fallback:** When refortify is blocked and marshal isn't fortified, P8 returns `wait` instead of `None` (prevents all-marshals-skip-→-0-actions pattern)

### Attack Futility Tracker

Prevents AI from endlessly attacking an impregnable fortified position (e.g., Wellington attacking Davout's fortress 10+ times).

- Stored in `world.ai_attack_futility` (Dict[str, int]), key format `"attacker:defender"`
- After each nation's actions, battle events are scanned: victories reset the counter, losses increment it
- When counter >= 3 AND target is still fortified, `_find_attack_opportunity()` filters that target out
- If target unfortifies, the filter is bypassed (situation changed — retry is reasonable)
- Resets on: victory, region conquest, enemy destroyed
- Persists across turns (serialized)

### Cautious Advance

Cautious AI marshals (Wellington, Blucher) now advance toward the nearest enemy when:
1. Not threatened (no enemy in same region or adjacent)
2. Not fortified
3. Stagnation counter >= 1

This prevents the cautious AI from camping indefinitely. The marshal finds an adjacent region that is closer to the nearest enemy and moves there. This is evaluated during P7 (Strategic Movement).

**Fallback:** When no distance-reducing move exists and stagnation >= 2, the marshal falls back to any safe adjacent friendly region rather than staying stuck. This handles map topologies where the shortest path requires moving laterally first.

### Garrison Assault (P4.25)

AI marshals evaluate whether to attack a garrisoned region. Handles both capital garrisons (>= 5k) and detachment garrisons (any size, `garrison_detachment=True`). The decision is based on:
- **Strength ratio** = marshal strength / garrison effective defense (includes terrain + fort bonuses)
- **Threshold** = personality attack threshold, adjusted by mood (anger lowers it, satisfaction raises it)
- If ratio >= threshold, the AI attacks the garrison
- **Artillery skip:** Artillery marshals are excluded entirely from P4.25 — garrison combat requires same-region presence, and artillery cannot bombard garrisons (Session 50)

Aggressive marshals will assault garrisons more readily (threshold 0.7), while cautious marshals need a stronger advantage (threshold 1.3).

### AI Garrison Placement (P6.75)

AI marshals can detach 3,000 troops to garrison a controlled border region (same `_execute_garrison` as player — Building Blocks principle). Defensive luxury, not a combat priority.

**Conditions (all must be true):**
- Marshal strength >= 20,000 (`AI_GARRISON_MIN_STRENGTH`, tunable)
- Current region controlled by marshal's nation
- No existing garrison in region
- No enemy marshal in current region or adjacent (safe to split)
- No other friendly marshal in current region (they can defend instead)
- Region is adjacent to at least 1 non-friendly region (vulnerable border)
- Max 1 garrison per nation per turn (`_garrison_placed_this_turn` flag)

**Behavior:** AI garrisons use `garrison_detachment=True` — no regen, fight to destruction (same as player garrisons).

### Artillery AI Bombardment (Session 50)

AI artillery behavior for ranged bombardment. The executor routes artillery attacks to the dedicated `_execute_bombardment()` path transparently — the AI just issues "attack" commands and the routing handles the rest (Building Blocks principle).

**Bombardment-Specific AI Checks (in `_find_attack_opportunity`):**
- **Limit pre-check:** If `bombardments_this_turn >= 2`, skip P4 entirely (fall through to P5+)
- **Broken/retreating skip:** Skip targets with `broken=True` or `retreating=True` at range — waste of ammunition
- **Ratio bypass:** Artillery bypasses personality threshold for ranged targets. Bombardment costs only 1.5% own strength, making it favorable at any ratio. Same-region combat (P0) still uses normal thresholds.
- **Enhanced target sort:** Fort tier (building+fortify > fortify > none) → force density in region (collateral opportunity) → distance → terrain bombardment modifier (plains > forest > mountains)

**P4.25 Garrison Exclusion:** Artillery cannot assault garrisons — garrison combat requires physical presence.

**P2 Screen Check:** Exposed artillery (no infantry in same/adjacent region) retreats toward nearest friendly infantry when enemy cavalry is within 2 tiles.

**P7 Anti-Oscillation:** Artillery with adjacent targets stays put (skips P7 movement) to continue bombarding.

**P7 Frontline Avoidance:** Artillery position scoring penalizes front-line regions (adjacent to enemy territory): -50 without infantry screen, -30 with co-located infantry. Non-frontline positions behind infantry on the front line get +15 bonus. Prevents artillery advancing into freshly-conquered contested regions.

---

## Admin Phase

The AI performs an admin phase each turn (before combat actions) using admin AP. Actions are evaluated in strict priority order — the AI spends admin AP on the highest-priority action available, then moves to the next.

### Admin Priority Chain

| Priority | Action | Details |
|----------|--------|---------|
| 1 | Urgent recruit | Marshals below 50% starting strength — critical reinforcement |
| 2 | Build market | At highest-income region |
| 3 | Build supply depot | At capital or major city; within each tier, prefers regions adjacent to enemy territory (forward logistics, Phase 6.2.H) |
| 4 | Build fortification | At border regions |
| 5 | Repair damaged buildings | Restore buildings damaged by war |
| 6 | Repair war damage | Fix war damage on regions |
| 7 | Rebuild recruit | Marshals at 50%-100% starting strength — enemies can reach full strength |
| 8 | Save AP | +75g per unused admin AP |

**Notes:**
- The AI uses the same admin commands as the player (Building Blocks principle)
- Recruitment is split into two tiers: urgent (below 50%, top priority) and rebuild (50%-100%, low priority) so enemies can reach full strength over time without sacrificing building and repair
- Building priorities reflect economic strategy: income first (market), then logistics (supply depot), then defense (fortification)
- Saving AP for gold is always the lowest priority — the AI prefers to spend

---

## Test Files

| File | Tests | Coverage |
|------|-------|----------|
| test_enemy_ai.py | 53 | Core decisions |
| test_enemy_ai_priority.py | 5 | Priority ordering |
| test_enemy_ai_action_budget.py | 4 | Action counting |
| test_ai_scoring.py | 24 | Strategic scoring |
| test_enemy_ai_bugs.py | 5 | Regression tests |
| test_ai_garrison.py | 29 | AI garrison placement + P4.25 awareness |

---

## TODOs and Future Work

All TODOs are tied to specific ROADMAP.md phases. Nothing is orphaned.

### Done (remove on next doc cleanup)

| Item | Status | When |
|------|--------|------|
| Undefended region capture | DONE | P4.5 |
| Enemy recruiting | DONE | Phase 6 (economy + admin phase) |
| Round-robin action distribution | DONE (partial) | `_marshals_done_this_turn` prevents monopolization |
| Defending key regions | DONE | P3.7 homeland defense + capital elevation |
| Allied coordination (basic) | DONE (partial) | P4.6/P4.75/P4.77 cross-nation (Session 63) |

### Phase 7b (Tactical Triangle)

| Item | Roadmap | Notes |
|------|---------|-------|
| Square formation AI (P2.5) | Session 67 | AI forms square when cavalry threatens |
| Auto-bombardment + overwatch AI | Session 68 | AI SUPPORT artillery auto-bombards |

### Phase 8 (Diplomacy)

| Item | Roadmap | Notes |
|------|---------|-------|
| Full alliance coordination | Phase 8: Alliances | Britain/Prussia share intel, coordinate strategy |
| Nation surrender conditions | Phase 8: Peace Treaties | Nations sue for peace when losing |
| Coalition trigger awareness | Phase 8: Coalition Trigger | AI reacts to threat level |

### Phase 8.5 (Events & National Identity)

| Item | Roadmap | Notes |
|------|---------|-------|
| Strategic objectives | Phase 8.5: National Goals | "Capture Belgium" drives multiple marshals |
| LLM-enhanced decisions | Phase 8.5: Marshal Voice Tier 2 | LLM for high-drama AI moments |

### 1805 Campaign

| Item | Roadmap | Notes |
|------|---------|-------|
| AP scaling per nation | 1805: AI Enhancements for Scale | France 5, Russia 3, etc. |
| Nation-level strategy layer | 1805: Tiered Nation AI | Above-marshal resource allocation |
| AI fog of war | 1805: AI Fog of War | Softer fog, `get_visible_enemies_near()` toggle |
| Proper capital system | 1805 | Replace hardcoded capitals with region data |
| Encirclement handling | 1805 | Surrender/last stand when surrounded |
| `_are_allied()` check | 1805 | Replace hardcoded coalition assumption |
| Dynamic nation relevance | 1805 | Portugal becomes important mid-game |
| Enemy cavalry limits | 1805 | 3-turn defensive/fortified caps (same as player) |

### Post-EA

| Item | Roadmap | Notes |
|------|---------|-------|
| Deliberate flanking coordination | Post-EA: Advanced AI | Multiple marshals attack from different directions |
| Strategic retreat | Post-EA: Advanced AI | Use retreat to reposition |
| Full round-robin | Post-EA: Advanced AI | Each marshal gets 1 action, then cycle |

---

## Troubleshooting

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Turn advances too fast | Enemy actions consuming player budget | Check `is_player_action` flag in executor |
| Enemy drills with adjacent threat | Nation-aware check missing | Use `get_enemies_of_nation()` not `get_enemy_marshals()` |
| Infinite loop on wait | Free action doesn't decrement budget | Check `max_free_actions` safeguard |
| Fortified enemy attacks | Missing state check | Add `fortified` check in `_find_attack_opportunity()` |
| Region not captured | No defender to defeat | Design issue - need explicit capture action |
| Fortify→unfortify loop | P3 re-fortifies without checking cooldown | Fixed: P3 now checks `_unfortified_this_turn` + `ai_refortify_cooldown` |
| Artillery never bombards | P3 catches artillery before P4 | Fixed: Artillery exempt from P3 fortify |
| Enemy 0 actions per turn | All marshals return None from P8 | Fixed: P8 returns `wait` when refortify blocked |
| Enemy battles not in popup | Fog filter dict/string comparison | Fixed: Extract `.get("name")` from attacker/defender dicts |
| Enemy bombardment not shown | Fog filter + dialog miss bombardment type | Fixed: Check `"bombardment"` event type in both |
| Wellington attacks same fort forever | No futility tracking | Fixed: `ai_attack_futility` tracker skips fortified targets after 3+ failed attacks |
| Uxbridge permanently idle | Aggressive P8 returned wait with no enemies | Fixed: Aggressive P8 returns None (end turn early) when no adjacent enemies |
| Trust objection "Marshal None" | Alternative/compromise dicts missing marshal name | Fixed: Inject `marshal_name` before execution in `_execute_post_objection` |

### Debug Commands

```python
# Test enemy AI directly
from backend.models.world_state import WorldState
from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor

world = WorldState(player_nation='France')
executor = CommandExecutor()
ai = EnemyAI(executor)
game_state = {'world': world}

# Process one nation's turn
results = ai.process_nation_turn('Britain', world, game_state)
for r in results:
    print(f"{r['ai_action']['marshal']} -> {r['ai_action']['action']}: {r['success']}")
```

### Verifying Personality Behavior

**Wellington should:**
- Prefer defensive stance
- Fortify when safe
- Only attack with 30%+ advantage
- Never attack when outnumbered

**Blucher should:**
- Prefer aggressive stance
- Attack at 70% strength ratio
- Drill when position secure
- Move toward enemies

---

## Quick Reference: AI Decision Summary

| Situation | Aggressive (Blucher) | Cautious (Wellington) |
|-----------|---------------------|----------------------|
| Enemy in range, even odds | **ATTACK** | Wait |
| Enemy in range, 30% advantage | **ATTACK** | **ATTACK** |
| Enemy in range, outnumbered | **ATTACK** (if ratio > 0.7) | Fortify |
| No enemy adjacent | Drill | Fortify |
| After drilling | Move toward enemy | Maintain position |
| Under attack | Stay aggressive | Defensive stance |
| Low morale | Keep fighting | Retreat |
| Retreat recovery | Wait | Defensive stance + wait |

---

*Last updated: February 2026*
*Recent additions: P3.7 homeland defense, P4.6 coordinated attack, P4.75 hostile exclusion, P4.76 co-location persistence, P4.77 cross-nation adjacency, P4.78 defensive positioning, +8% coordination estimate, artillery stagnation override, stagnation fortify fix, cautious advance fallback*
