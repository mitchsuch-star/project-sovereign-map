# Adding New Strategic Command Types

**Purpose:** Step-by-step guide for adding new strategic commands (e.g., PATROL, ESCORT, FLANK).
**Difficulty:** 6/10 — Requires touching 6+ files but the pattern is well-established.

---

## Checklist

### 1. Define the Command Type

Add to the valid types set:

| File | Location | Change |
|------|----------|--------|
| `backend/ai/validation.py:117` | `VALID_STRATEGIC_TYPES` | Add `"PATROL"` to set |
| `backend/ai/strategic_parser.py:32` | `STRATEGIC_KEYWORDS` | Add keyword→type mapping |

### 2. Parser Detection

**File:** `backend/ai/strategic_parser.py`

Add detection in `_detect_strategic_type()` (line 189):
```python
# Add keywords that trigger this command type
STRATEGIC_KEYWORDS = {
    ...
    "PATROL": ["patrol", "sweep", "patrol between", "guard route"],
}
```

If the command has a unique target classification (e.g., PATROL needs TWO regions), extend `_classify_target()` (line 264) or add a new classifier.

### 3. Fast Parser Keywords

**File:** `backend/ai/llm_client.py`

Add keyword detection in `_parse_with_mock()` (~line 408):
```python
elif "patrol" in command_lower or "sweep" in command_lower:
    action = "move"  # Strategic parser will upgrade to PATROL
```

### 4. Command Handler

**File:** `backend/commands/strategic.py`

Add a new handler method following the established pattern:

```python
def _execute_patrol(self, marshal, order, world, game_state):
    """PATROL: Move between waypoints in a loop."""
    # 1. Get current waypoint from order
    # 2. Move one step toward it
    # 3. On arrival, switch to next waypoint
    # 4. Check for enemies encountered en route
    # 5. Return result dict

    result = self.executor.execute(
        {"command": {
            "marshal": marshal.name,
            "action": "move",
            "target": next_waypoint,
            "_strategic_execution": True,  # REQUIRED: skips action cost
        }},
        game_state
    )
    return {
        "marshal": marshal.name,
        "command": "PATROL",
        "action_taken": "move",
        "moved_to": next_waypoint,
        "order_status": "active",  # or "completed"
    }
```

Wire it into `_execute_strategic_turn()` (line 74):
```python
elif order.command_type == "PATROL":
    return self._execute_patrol(marshal, order, world, game_state)
```

### 5. Executor Initial Setup

**File:** `backend/commands/executor.py`

In `_execute_strategic_command()` (line 1984), add any PATROL-specific setup when creating the StrategicOrder:

```python
if strategic_type == "PATROL":
    # PATROL may need multiple waypoints stored
    order = StrategicOrder(
        command_type="PATROL",
        target=waypoints[0],  # First waypoint
        target_type="region",
        path=initial_path,
        conditions=condition,
        # Store full waypoint list in a custom field if needed
    )
```

### 6. Condition Support (if needed)

If PATROL has unique completion conditions, add them to:
- `backend/models/marshal.py` — `StrategicCondition` dataclass (line 37)
- `backend/commands/strategic.py` — `_check_condition()` (line 792)

### 7. Serialization

If you added new fields to `StrategicOrder` or `StrategicCondition`:
- Update `to_dict()` and `from_dict()` in `backend/models/marshal.py`
- Test roundtrip: `order == StrategicOrder.from_dict(order.to_dict())`

### 8. Tests

Add tests in `tests/` covering:
- Parser detects PATROL keywords
- Executor creates correct StrategicOrder
- Handler moves between waypoints
- Personality affects behavior (aggressive patrols wider, cautious sticks to safe zones)
- Condition completion
- Serialization roundtrip

---

## Worked Example: PATROL Command

**Player says:** "Ney, patrol between Belgium and Netherlands"

### What happens:

1. **llm_client.py** — Fast parser sees "patrol" → `action="move"`
2. **strategic_parser.py** — `_detect_strategic_type()` sees "patrol" → `PATROL`
3. **strategic_parser.py** — `_classify_target()` needs to handle TWO region targets (new logic)
4. **parser.py** — Injects `is_strategic=True`, `strategic_type="PATROL"`
5. **validation.py** — `"PATROL" in VALID_STRATEGIC_TYPES` → passes
6. **executor.py** — Intercepts, creates StrategicOrder with waypoints, executes first move
7. **strategic.py** — Each turn, moves to next waypoint; on arrival, reverses direction
8. **Personality:**
   - Aggressive: Auto-attacks enemies encountered on patrol route
   - Cautious: Avoids enemy regions, reports contact, asks player
   - Literal: Follows exact route, ignores nearby battles

### Difficulty Breakdown

| Step | Effort | Notes |
|------|--------|-------|
| Keywords & validation | Easy | 2 lines each |
| Parser detection | Easy | Add to existing keyword dict |
| Target classification | Medium | PATROL needs multi-target support (new) |
| Handler | Medium | Movement loop exists, add waypoint cycling |
| Personality behavior | Medium | Reuse `_get_personality_aware_path()` and `_handle_blocked_path()` |
| Serialization | Easy | Add waypoints field to StrategicOrder |
| Tests | Medium | ~15-20 tests for full coverage |

**Total estimated difficulty: 6/10** — Most infrastructure exists. The main new work is multi-waypoint targeting and the cycling behavior.

---

## Common Pitfalls

1. **Always use `_strategic_execution=True`** in executor calls from handlers — otherwise it deducts player actions
2. **Always use `_get_personality_aware_path()`** for pathfinding — don't call `world.find_path()` directly
3. **Return `order_status`** in result dict — `"active"`, `"completed"`, or `"paused"`
4. **Handle retreat recovery** — check at top of handler, not just in `_execute_strategic_turn()`
5. **Test serialization** — if you add fields to StrategicOrder, they MUST survive to_dict/from_dict roundtrip
