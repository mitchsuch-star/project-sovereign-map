# Strategic Command Flow — Implementation Trace

**Purpose:** Exact file:line reference for every stage of strategic command processing.
**Last Updated:** January 2026 (Post-Phase C, all 7 bugs fixed)

---

## Pipeline Overview

```
Player Input ("Ney, march to Belgium")
    │
    ▼
1. FAST PARSER          llm_client.py:441      Keywords → action="move"
    │
    ▼
2. STRATEGIC DETECTION  parser.py:316          detect_strategic_command()
    │                   strategic_parser.py:81  → returns is_strategic, strategic_type, etc.
    │
    ▼
3. VALIDATION           validation.py:117      VALID_STRATEGIC_TYPES check
    │
    ▼
4. EXECUTOR INTERCEPT   executor.py:863        if is_strategic → _execute_strategic_command()
    │                   executor.py:1984       Creates StrategicOrder
    │                   executor.py:2118       marshal.strategic_order = order
    │                   executor.py:872        _skip_routing = True (bypass tactical)
    │
    ▼
5. FIRST STEP           executor.py:~2080      Executes first move/action immediately
    │                                          (costs 2 actions, 1 for LITERAL)
    │
    ▼
6. TURN-END PROCESSING  turn_manager.py:140    StrategicExecutor.process_strategic_orders()
    │                   strategic.py:40        Iterates marshals with active orders
    │                   strategic.py:74        _execute_strategic_turn() per marshal
    │
    ▼
7. COMMAND HANDLERS     strategic.py:127       _execute_move_to()
                        strategic.py:274       _execute_pursue()
                        strategic.py:398       _execute_hold()
                        strategic.py:573       _execute_support()
```

---

## Stage 1: Fast Parser (Keyword Detection)

**File:** `backend/ai/llm_client.py`
- **Line 262:** `parse_command()` — entry point
- **Line 408-442:** Strategic keyword detection in `_parse_with_mock()`
  - "march", "advance", "move to" → action="move" (MOVE_TO)
  - "pursue", "chase", "hunt" → action="move" (PURSUE)
  - "reinforce", "support" → action="move" (SUPPORT)
  - "hold position", "hold the line" → action="hold" (HOLD)
- **Key:** Fast parser sets `action="move"`. It does NOT set `is_strategic`. That's Stage 2.

## Stage 2: Strategic Detection

**File:** `backend/ai/strategic_parser.py`
- **Line 81:** `detect_strategic_command(text, marshals, regions, world)` — main entry
- **Line 189:** `_detect_strategic_type(text)` — classifies: MOVE_TO, PURSUE, HOLD, SUPPORT
- **Line 264:** `_classify_target(target, regions, marshals, world)` — target_type: region, enemy_marshal, friendly_marshal, generic
- **Line 348:** `_parse_condition(text)` — parses: until_arrives, until_destroyed, max_turns, until_battle_won

**File:** `backend/commands/parser.py`
- **Line 314-326:** Injection block — calls `detect_strategic_command()` and injects:
  - `result["is_strategic"] = True`
  - `result["strategic_type"]` = "MOVE_TO" | "PURSUE" | "HOLD" | "SUPPORT"
  - `result["target_snapshot_location"]` (for friendly marshal targets)
  - `result["strategic_condition"]` (StrategicCondition dict)
  - `result["attack_on_arrival"]` (bool)
  - `result["command"]["target_type"]` (str)

## Stage 3: Validation

**File:** `backend/ai/validation.py`
- **Line 117:** `VALID_STRATEGIC_TYPES = {"MOVE_TO", "PURSUE", "HOLD", "SUPPORT"}`
- **Line 118-123:** If `is_strategic=True` and `strategic_type` not in valid set → falls back to tactical (clears `is_strategic`, `strategic_type`)

## Stage 4: Executor Interception

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

## Stage 5: Turn-End Processing

**File:** `backend/game_logic/turn_manager.py`
- **Line 140-144:** After enemy phase, before `advance_turn()`:
  ```python
  strategic_exec = StrategicExecutor(self.executor)
  strategic_results = strategic_exec.process_strategic_orders(world, game_state)
  ```

**File:** `backend/commands/strategic.py`
- **Line 40:** `process_strategic_orders(world, game_state)` — iterates all marshals
- **Line 74:** `_execute_strategic_turn(marshal, order, world, game_state)`:
  1. **Line ~81:** Retreat recovery check (pauses order if recovering)
  2. **Line ~91:** Condition check via `_check_condition()`
  3. **Line ~100:** Interrupt check via `_check_interrupts()`
  4. Routes to command-specific handler

## Stage 6: Command Handlers

### MOVE_TO (strategic.py:127)
- Moves one step along path per turn
- Recalculates path if stale (personality-aware)
- Completes when marshal reaches destination
- If `attack_on_arrival=True`, attacks first enemy at destination

### PURSUE (strategic.py:274)
- Recalculates path to enemy marshal each turn (target moves)
- Uses personality-aware pathfinding
- Attacks when in same region as target
- Completes on victory or target destroyed

### HOLD (strategic.py:398)
- Sets `holding_position=True` (Grouchy gets +15% defense)
- **Sally mechanic:** Aggressive marshals attack adjacent enemies then return
  - Move to adjacent → attack (with `_sortie=True`) → return to hold position
- Completes when condition met (max_turns, etc.)

### SUPPORT (strategic.py:573)
- Moves toward ally marshal
- If `follow_if_moves=True`, tracks ally movement
- If `join_combat=True`, joins ally's battles
- Completes when `until_battle_won` condition triggers

---

## Cross-Cutting Systems

### Personality-Aware Pathfinding
**File:** `backend/commands/strategic.py`
- **Line 1046:** `_get_personality_aware_path(marshal, destination, world)`
- **Line 1038:** `_get_enemy_occupied_regions(nation, world)`
- Cautious: avoids enemy-occupied regions (falls back to direct if no safe route)
- Aggressive/Literal/Others: direct path

### Blocked Path Handling
**File:** `backend/commands/strategic.py`
- **Line 881:** `_handle_blocked_path(marshal, next_region, order, world, game_state)`
- Literal: silently reroutes around obstacle
- Aggressive: auto-attacks at ≥0.7 ratio, otherwise asks player
- Cautious: always asks player for decision

### Interrupt Detection
**File:** `backend/commands/strategic.py`
- **Line 707:** `_check_interrupts(marshal, order, world, game_state)`
- Uses `world.get_battles_within_range()` (world_state.py:864)
- LITERAL personality skips cannon fire interrupts ("The Grouchy Moment")

### Condition Evaluation
**File:** `backend/commands/strategic.py`
- **Line 792:** `_check_condition(marshal, order, world)`
- Evaluates: `max_turns`, `until_marshal_arrives`, `until_battle_won`, `until_destroyed`
- `until_battle_won` triggers on both victory AND stalemate

---

## Data Structures

### StrategicOrder (marshal.py:75)
```python
@dataclass
class StrategicOrder:
    command_type: str          # "MOVE_TO", "PURSUE", "HOLD", "SUPPORT"
    target: str                # Region name or marshal name
    target_type: str           # "region", "enemy_marshal", "friendly_marshal"
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

### StrategicCondition (marshal.py:37)
```python
@dataclass
class StrategicCondition:
    max_turns: Optional[int] = None
    until_marshal_arrives: Optional[str] = None
    until_battle_won: bool = False
    until_destroyed: bool = False
```

### Key Marshal Fields
- `marshal.strategic_order` (marshal.py:299) — active order or None
- `marshal.in_strategic_mode` (marshal.py:492) — property, True if order exists
- `marshal.precision_execution_active` — Grouchy clarity bonus flag
- `marshal.strategic_combat_bonus` — consumed in combat
- `marshal.strategic_defense_bonus` — consumed in combat

---

## Battle Tracking (for Cannon Fire)

**File:** `backend/models/world_state.py`
- **Line 59:** `self.battles_this_turn: List[Dict] = []`
- **Line 849:** `record_battle(region, attacker, defender)` — called by combat resolver
- **Line 864:** `get_battles_within_range(location, range)` — BFS distance check
- **Line 873:** `clear_turn_battles()` — called at turn start

---

## Override & Cancel (Phase E — Not Yet Implemented)

When a player issues a tactical command to a marshal with an active strategic order:
- **Override actions** (attack, move, defend): Silently cancel strategic order, execute tactical
- **Non-override actions** (wait, scout): Execute alongside strategic order
- **Explicit cancel** ("halt", "cancel"): Cost 1 action, -3 trust
- Implementation location: `executor.py _check_strategic_override()` (planned)
