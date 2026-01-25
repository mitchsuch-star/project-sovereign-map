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
    # Attack thresholds by personality
    ATTACK_THRESHOLDS = {
        "aggressive": 0.7,   # Attacks even slightly outnumbered
        "cautious": 1.3,     # Needs clear advantage
        "literal": 1.0,      # Even odds
        "balanced": 1.0,
        "loyal": 1.0,
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

| Priority | Name | Trigger Condition |
|----------|------|-------------------|
| 1 | Retreat Recovery | `retreat_recovery > 0` |
| 2 | Critical Survival | `strength < 25% of starting` |
| 3 | Threat Response | Stronger enemy adjacent |
| 4 | Attack Opportunity | Valid target + meets threshold |
| 4.5 | Capture Undefended | Adjacent undefended enemy region |
| 5 | Fortification | Cautious + no attack target |
| 6 | Drilling | Aggressive + position secure |
| 7 | Strategic Movement | Can advance toward enemy |
| 8 | Default | Stance adjustment or wait |

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

## TODOs and Future Work

### High Priority

```python
# TODO: Flanking coordination
# AI should explicitly coordinate attacks for flanking bonus
# Currently relies on natural occurrence

# DONE: Undefended region capture
# AI now uses "attack" action on undefended enemy regions to capture them
# Added _find_undefended_capture() method at Priority 4.5
# Future: Region fortifications (buildings) could slow capture

# TODO: Enemy recruiting
# Requires economy system (gold, income, upkeep)
# Currently enemies cannot recruit
```

### Medium Priority

```python
# TODO: Round-robin action distribution
# Currently greedy (best action wins)
# Should distribute actions more evenly across marshals

# TODO: Defending key regions
# AI should prioritize defending capitals and last regions
# Currently only threat response (adjacent enemies)

# TODO: Enemy cavalry limits
# Cavalry should have 3-turn defensive/fortified caps like player
# Currently not checked for enemies
```

### Low Priority (Early Access)

```python
# TODO: Dynamic relevance
# Portugal can become important mid-game
# Currently all nations have fixed behavior

# TODO: Allied coordination
# Multiple nations should coordinate strategy
# Currently each nation acts independently

# TODO: LLM-enhanced decisions
# Use LLM for strategic decisions, not just rules
# Currently pure decision tree

# TODO: Nation surrender conditions
# Nations should sue for peace when losing badly
# Currently fight to the last marshal

# TODO: Fog of war for enemies
# Enemies should have limited information
# Currently perfect information
```

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

*Last updated: January 2025*
*Bugs fixed: Turn advancement, fortified attack, infinite loop, drill self-detection*
