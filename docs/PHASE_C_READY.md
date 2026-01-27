# Phase 5.2-C: Strategic Executor - Implementation Guide

## Overview

StrategicExecutor runs each turn, processing active strategic orders for player marshals.
It interprets orders based on personality, handles interrupts, and returns results for UI.

## Entry Point

In `turn_manager.py`, at START of player's turn:
```python
# After enemy AI, before tactical state processing:
strategic_reports = strategic_executor.process_strategic_orders(world, game_state)
```

## The 4 Command Handlers

### MOVE_TO
- Move along path toward destination
- Cavalry moves 2 regions/turn, infantry moves 1
- On arrival: complete order
- If target was friendly marshal: report if they're still there
- If blocked by enemy: personality determines response

### PURSUE
- Track enemy each turn (dynamic, no snapshot)
- Move toward target
- Attack when in same region
- Complete when target destroyed

### HOLD
- Stay at position
- AGGRESSIVE: Sally out to attack nearby enemies, return after
- CAUTIOUS: Auto-fortify
- LITERAL: Immovable (+15% defense), never leaves

### SUPPORT
- Move to ally's location
- Follow if ally moves (except cautious asks first)
- Join ally's battles
- Complete when ally safe or battle won

## Key Flags

| Flag | Purpose |
|------|---------|
| `_strategic_execution=True` | Skip action cost — already paid at order creation |
| `_sortie=True` | Don't advance on victory (HOLD sally mechanic) |

## Action Cost

- **2 actions** for most marshals — handled in executor.py `_execute_strategic_command()`
- **1 action** for LITERAL personality (Grouchy follows orders efficiently)
- Per-turn execution is FREE (cost paid upfront)

## Return Format
```python
{
    "marshal": "Grouchy",
    "command": "MOVE_TO",
    "order_status": "continues",  # "completed", "breaks", "requires_input"
    "message": "Grouchy marches to Rhine. 2 regions to Vienna.",
    "regions_moved": ["Belgium", "Rhine"],  # For MOVE_TO/PURSUE

    # If requires_input:
    "requires_input": True,
    "interrupt_type": "contact",
    "options": ["attack", "go_around", "hold_position", "cancel_order"]
}
```

## Personality Behaviors Table

| Situation | AGGRESSIVE | CAUTIOUS | LITERAL |
|-----------|------------|----------|---------|
| Enemy blocking path | Auto-attack if favorable | Ask player | Reroute silently |
| Cannon fire nearby | Rush to battle | Ask: "Investigate?" | **IGNORE** (Grouchy moment) |
| Unfavorable odds | Ask player | Ask player | Report stuck, break |
| Ally needs help | Rush to join | Ask: "Assist?" | Ignore (unless SUPPORT order) |

## Condition Checking

Check at START of each turn's execution:
```python
if order.condition:
    met, reason = _check_condition(marshal, order.condition, world)
    if met:
        return _complete_order(marshal, world, reason)
```

## Combat Loop Prevention

Track last combat to prevent infinite loops:
```python
order.last_combat_enemy = enemy.name
order.last_combat_turn = world.current_turn
order.last_combat_result = outcome

# Before auto-attacking same enemy:
if (order.last_combat_enemy == enemy.name and
    world.current_turn - order.last_combat_turn <= 1):
    # Ask player instead of auto-attacking
```

## Command Override / Cancel Categories

| Category | Commands | Effect on Strategic Order |
|----------|----------|--------------------------|
| **Override** | attack, move, defend, retreat, stance_change | Silently cancels current order |
| **Non-override** | wait, scout, recruit, drill, fortify | Executes alongside, order continues |
| **Explicit cancel** | "halt", "stop", "cancel order" | Cancels order, costs 1 action, -3 trust |

## WorldState Methods Available for Phase C

| Method | Signature | Notes |
|--------|-----------|-------|
| `find_path` | `(start, end, avoid_regions=None)` | BFS, returns path inclusive of start+end |
| `get_enemies_in_region` | `(region, nation)` | Returns enemy marshals with strength > 0 |
| `get_marshals_in_region` | `(region_name)` | All marshals in region |
| `get_marshal` | `(name)` | Single marshal lookup |
| `get_distance` | `(region_a, region_b)` | BFS distance (int) |
| `record_battle` | `(battle_dict)` | Add to battles_this_turn |
| `get_battles_within_range` | `(region, range)` | For cannon fire detection |

Note: `get_adjacent_regions` is NOT a WorldState method. Use `world.regions[name].adjacent_regions` (list attribute).

## Clarification System (Grouchy)

When a LITERAL marshal receives a strategic command with ambiguity > 60:
1. Parser detects generic target (e.g., "pursue the enemy")
2. `_add_interpretation()` picks nearest/most-threatened target
3. Executor's clarification gate returns `awaiting_clarification` with:
   - `interpreted_target` — what Grouchy will do if confirmed
   - `alternatives` — up to 3 other options
   - `interpretation_reason` — why this target was chosen
4. Player confirms or picks alternative (Phase J UI)

## Phase C Implementation Status: ✅ COMPLETE

**Files created:**
- `backend/commands/strategic.py` — StrategicExecutor class (~600 lines)

**Files modified:**
- `backend/ai/schemas.py` — ParseResult interpretation fields
- `backend/ai/strategic_parser.py` — `_add_interpretation()` for generic targets
- `backend/commands/executor.py` — `_strategic_execution`/`_sortie` flags, override logic, clarification gate
- `backend/game_logic/turn_manager.py` — Strategic execution hook before `advance_turn()`

**Tests:** 48 strategic tests + 602 total (0 regressions)

**What's next:** Phase D (Interrupt response handling), Phase E (Explicit cancel command), Phase J (UI)

## Files to Read Before Implementing

1. `docs/PHASE_5_2_IMPLEMENTATION_PLAN.md` — Full design spec (Section 11 has complete executor code)
2. `backend/models/marshal.py` — StrategicOrder, StrategicCondition, Marshal fields
3. `backend/commands/executor.py` — How actions execute, action cost logic
4. `backend/game_logic/turn_manager.py` — Turn flow, where strategic execution hooks in
5. `backend/ai/enemy_ai.py` — Personality handling patterns (reusable for strategic behavior)
6. `backend/ai/strategic_parser.py` — How orders are detected (parser output → executor input)
