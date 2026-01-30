# Ink & Iron: Technical Reference

> **Code patterns, development rules, and session workflow.**  
> **Read before implementing anything.**

---

## Critical Rules

### 1. Port 8005 (NOT 8000!)

```python
uvicorn.run(app, host="127.0.0.1", port=8005)
```

Change in BOTH `backend/main.py` AND `godot-client/.../api_client.gd`.

### 2. Int Wrapping for Godot

Godot 4.3 crashes on floats. Wrap ALL numeric returns:

```python
# ✅ CORRECT
return {"strength": int(marshal.strength), "trust": int(marshal.trust.value)}

# ❌ WRONG - crashes Godot
return {"strength": marshal.strength * modifier}
```

### 3. Unified Marshal Storage

Single dict for ALL marshals (player + enemy):

```python
# ✅ CORRECT
self.marshals = {}  # Ney, Davout, Grouchy, Wellington, Blucher

# ❌ WRONG
self.player_marshals = {}
self.enemy_marshals = {}
```

### 4. Building Blocks (Executor Pattern)

ALL actions through executor. Player AND AI use same code:

```python
# ✅ CORRECT
result = executor.execute(parsed_command, game_state)

# ❌ WRONG - bypasses validation
world.marshals[name].location = new_location
```

### 5. Trust Modification

```python
# These exist:
marshal.trust.value          # Property (read-only)
marshal.trust.modify(+10)    # Relative change
marshal.trust._value = 50    # Direct set (use sparingly)
```

### 6. getattr for Optional Fields

```python
# ✅ CORRECT
recklessness = getattr(marshal, 'recklessness', 0)
is_admin = getattr(marshal, 'administrative', False)

# ❌ WRONG - AttributeError if field doesn't exist
recklessness = marshal.recklessness
```

### 7. Serialization is MANDATORY

Every new field MUST have:
- `to_dict()` serialization
- `from_dict()` deserialization
- Roundtrip test

```python
# marshal.py
def to_dict(self):
    return {
        "new_field": self.new_field,  # ADD THIS
        ...
    }

@classmethod
def from_dict(cls, data):
    obj.new_field = data.get("new_field", default_value)  # AND THIS
```

---

## Session Workflow

### Starting a Session

```
1. Read STATUS.md (30 seconds)
   - Current test count
   - What's in progress
   - Any blockers

2. If needed, read ROADMAP.md
   - What phase are we in?
   - What's next?

3. Verify starting state:
   cd backend
   pytest tests/ -v --tb=short | tail -20
```

### Ending a Session

```
1. Run full test suite
   pytest tests/ -v

2. Update STATUS.md
   - New test count
   - What was completed
   - What's next

3. If phase completed, update ROADMAP.md

4. If new system completed, update COMPLETED.md
```

### Claude Model Selection

| Use Sonnet For | Use Opus For |
|----------------|--------------|
| Single-file changes | Multi-system integration (5+ files) |
| Bug fixes with clear cause | Architecture decisions |
| Following established patterns | Code reviews |
| Most implementations | Debugging complex issues |

### Code Reviews

Do a code review:
- End of each phase
- After major systems
- When something feels wrong
- When tests fail unexpectedly

---

## Smoke Test Checklist

Run after major changes to verify Godot↔Backend integration.

### Prerequisites
```bash
# Terminal 1: Backend
cd backend && python main.py

# Terminal 2: Godot
# Open project, press F5
```

### Tests

| Test | Steps | Expected |
|------|-------|----------|
| **1. Tactical Command** | Type: "Ney, attack Wellington" | Combat resolves, actions consumed |
| **2. Strategic MOVE_TO** | Type: "Grouchy, march to Vienna" | Acknowledged as strategic, executes over turns |
| **3. Strategic PURSUE** | Type: "Ney, pursue Blücher" | Tracks and follows target |
| **4. Grouchy Clarification** | Type: "Grouchy, pursue the enemy" | Clarification popup (ambiguity > 60) |
| **5. Strategic HOLD** | Type: "Davout, hold Belgium" | Persists across turns |
| **6. Override** | Give strategic order, then tactical | Strategic cancelled, tactical executes |
| **7. End Turn** | Click end turn | Enemy phase runs, no errors |

### If Tests Fail

| Symptom | Check |
|---------|-------|
| API format mismatch | `backend/main.py` response format |
| Strategic not detected | `strategic_parser.py` keywords |
| Godot type error | Missing `int()` wrapper |
| Enemy AI does nothing | Check retreat state, fortify state |

---

## Adding New Features

### Adding New Action

1. `parser.py` — Add to valid_actions
2. `executor.py` — Add `_execute_[action]()` method
3. `world_state.py` — Add action cost
4. `llm_client.py` — Add keywords to mock parser
5. `disobedience.py` — Add to objection_actions if applicable

### Adding New Marshal State

1. `marshal.py` — Add field to `__init__`
2. `marshal.py` — Add to `to_dict()` and `from_dict()`
3. `world_state.py` — Process in `_process_tactical_states()` if per-turn
4. `executor.py` — Block logic if prevents actions

### Adding New Popup

1. Backend: Return with `type` field
2. Godot: Create scene (.tscn) and script (.gd)
3. Godot: Wire signals
4. `main.py`: Pass through popup fields in response

### Adding New Personality

See MARSHAL_GUIDE.md for full instructions.

---

## File Reference

### Backend Core

| File | Purpose |
|------|---------|
| `main.py` | FastAPI endpoints, response formatting |
| `commands/executor.py` | All action execution |
| `commands/parser.py` | Command parsing, fuzzy matching |
| `commands/strategic.py` | Strategic order executor |
| `models/marshal.py` | Marshal class, states, serialization |
| `models/world_state.py` | Game state, turn processing |
| `game_logic/combat.py` | Combat resolution |
| `game_logic/turn_manager.py` | Turn flow, enemy phase |
| `ai/enemy_ai.py` | Enemy decision tree |
| `ai/llm_client.py` | LLM integration |
| `ai/strategic_parser.py` | Strategic command detection |

### Godot Core

| File | Purpose |
|------|---------|
| `api_client.gd` | Backend communication |
| `game_manager.gd` | Game state coordination |
| `map.gd` | Map rendering |
| `command_input.gd` | Command entry |
| `popup_*.gd` | Various popup handlers |

---

## Common Bugs

| Bug | Cause | Fix |
|-----|-------|-----|
| Trust not updating | Using `trust.set()` | Use `trust.modify()` |
| Marshal disappears | Deleted from dict | Use `administrative = True` |
| Godot crashes silently | Float instead of int | Wrap with `int()` |
| Enemy AI does nothing | In retreat/fortified | Check state flags |
| Action not recognized | Not in valid_actions | Add to parser.py |

---

## Configuration

### Environment Variables (.env)

```bash
LLM_MODE=mock              # "mock" | "anthropic" | "groq"
ANTHROPIC_API_KEY=sk-ant-... # Only for live mode
```

### Test Commands

```bash
# All tests
pytest tests/ -v

# Specific file
pytest tests/test_enemy_ai.py -v

# Quick count
pytest tests/ -v 2>&1 | grep "passed"

# With output
pytest tests/ -v -s
```

---

## Don't Do

- ❌ Return floats to Godot (wrap with `int()`)
- ❌ Separate player/enemy marshal dicts
- ❌ Add features outside current phase
- ❌ Change port without updating api_client.gd
- ❌ Skip serialization for new fields
- ❌ Bypass executor for state changes
- ❌ Store API keys in code
