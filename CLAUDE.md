# CLAUDE.md

Napoleonic strategy game. Players type commands ("Marshal Ney, attack Wellington") and AI marshals respond based on personality. Godot 4 frontend, FastAPI backend on port 8005. For game vision see `docs/VISION.md`.

## Golden Rules

1. **Combat modifiers: SINGLE SOURCE in `marshal.py`** — `get_attack_modifier()` / `get_defense_modifier()` only. `combat.py` reads them, never recalculates.
2. **All numbers to Godot: `int()`** — Godot crashes on floats.
3. **All marshals in ONE dict:** `world.marshals` (not separate player/enemy).
4. **State clearing: AFTER reading** — get the value, use it, then clear.
5. **Enemy AI uses SAME executor as player** (Building Blocks principle).
6. **LLM never affects mechanics** — parsing only, executor is deterministic.
7. **Port 8005** (not 8000!) — change in BOTH `backend/main.py` AND `godot-client/.../api_client.gd`.

## Current Phase

**Phase 6: Core Campaign Systems — IN PROGRESS (2 items remaining)**

### Remaining (must build before Phase 6.5)

| Feature | Complexity | Notes |
|---------|------------|-------|
| **Manpower Pools** | Medium | Separate: Infantry, Cavalry, Artillery |
| **Artillery Unit Type** | Medium | Combat buffs like cavalry |

### Completed in Phase 6

Terrain (6.1), Economy (6.2 audited), Save/Load, Berthier Parse Recovery, Post-Battle Analysis, Turn Events Log, Reinforcements, Attrition, City Fortification, Fog of War (COMPLETE: Sessions 33-36 — intel model, visibility engine, scout persistence, battle reveal, intel report, filtered game state, PURSUE/SUPPORT/cautious pathfinding fog-aware, enemy phase filtering, tactical event filtering, watchtower building, contact interrupt discovery messages, Davout PURSUE fog-aware objection, V2b TODO markers, 157 fog-specific tests). See `docs/STATUS.md` for details.

### Deferred from Phase 6

- Sieges → deferred to 1805 (current fort + contested capture sufficient for 13-region map)
- Pause menu → Phase 6.5

See `docs/STATUS.md` for session state, `docs/ROADMAP.md` for timeline.

---

## File Reference

### Backend Core

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI endpoints, response formatting |
| `backend/commands/executor.py` | All action execution (_execute_*) |
| `backend/commands/parser.py` | Command parsing, fuzzy matching |
| `backend/commands/disobedience.py` | V1 objection system, trust values |
| `backend/commands/objection_v2.py` | V2a objection system (ConcernLevel triggers) |
| `backend/commands/strategic.py` | Strategic order per-turn executor |
| `backend/commands/vindication.py` | Vindication tracker |
| `backend/models/marshal.py` | Marshal class, combat modifiers, states, serialization |
| `backend/models/world_state.py` | Game state, turn processing, action economy |
| `backend/models/region.py` | 13 regions with adjacency |
| `backend/models/personality.py` | PersonalityType enum |
| `backend/models/personality_modifiers.py` | Combat bonuses by personality |
| `backend/game_logic/combat.py` | Combat resolution, messages |
| `backend/game_logic/battle_report.py` | Post-battle modifier snapshots, report generation, Berthier observations |
| `backend/game_logic/turn_manager.py` | Turn flow, enemy phase |
| `backend/ai/enemy_ai.py` | Enemy AI decision tree (P1-P8) |
| `backend/ai/llm_client.py` | LLM integration (fast parser + Anthropic) |
| `backend/ai/strategic_parser.py` | Strategic command detection |
| `backend/ai/validation.py` | VALID_ACTIONS (single source of truth for LLM) |
| `backend/ai/prompt_builder.py` | Context-aware LLM prompts |
| `backend/intel_report.py` | Berthier Intelligence Report (fog-filtered status view) |
| `backend/save_manager.py` | Save/load file I/O, autosave |

### Godot Core

| File | Purpose |
|------|---------|
| `api_client.gd` | Backend communication |
| `game_manager.gd` | Game state coordination |
| `map.gd` | Map rendering, fog overlay, fogged enemy icons |
| `main.gd` | Terminal UI, response handling |

---

## Before Modifying: Required Reading

| If you're modifying... | Read these first |
|------------------------|------------------|
| Combat damage/modifiers | `marshal.py` (get_*_modifier), `combat.py` (resolve_combat) |
| Marshal abilities | `personality_modifiers.py`, `marshal.py`, `combat.py` |
| Fortify/Drill mechanics | `executor.py` (_execute_fortify/drill), `marshal.py`, `world_state.py` (_process_tactical_states) |
| Disobedience/Trust | `disobedience.py`, `objection_v2.py`, `personality.py` |
| Cavalry limits | `world_state.py` (_check_cavalry_limits), `marshal.py` (cavalry counters) |
| Terrain system | `region.py` (constants, Region class), `combat.py` (_get_terrain_bonus), `executor.py` (5 resolve_battle calls, charge blocking) |
| Turn processing | `world_state.py` (advance_turn), `executor.py` (_execute_end_turn) |
| Adding new actions | See pattern below |
| Retreat/Broken state | `combat.py` (forced retreat), `marshal.py` (retreat_recovery), `executor.py` |
| Enemy AI behavior | `enemy_ai.py`, `turn_manager.py`, `executor.py` (is_player_action check) |
| Strategic commands | `strategic.py`, `strategic_parser.py`, `executor.py` |
| Objection V2 system | `objection_v2.py`, `docs/OBJECTION_V2.md` |
| Fog of war | `docs/FOG_OF_WAR_SPEC.md`, `docs/FOG_IMPLEMENTATION_PLAN.md`, `backend/models/intel.py`, `backend/intel_report.py`, `map.gd` (fog overlay + fogged icons) |
| Strategic commands + fog | `docs/FOG_OF_WAR_SPEC.md` §5, `docs/FOG_IMPLEMENTATION_PLAN.md` Session 34B, `backend/commands/strategic.py` |

For detailed system docs: `docs/SYSTEMS_REFERENCE.md`
For Enemy AI details: `docs/ENEMY_AI_REFERENCE.md`

---

## Common Modification Patterns

### Adding a new action

1. Add to `VALID_ACTIONS` in `validation.py` (single source of truth for LLM)
2. Add `_execute_[action]()` in `executor.py`
3. Add to `valid_actions` list in `parser.py`
4. Add cost to `_action_costs` in `world_state.py`
5. Add keywords to mock parser in `llm_client.py` (~line 416, search "ADD NEW ACTION")
6. Add few-shot example in `prompt_builder.py` if complex
7. If triggerable by objection, add to `objection_actions` in `disobedience.py`
8. Add to_dict/from_dict if new state fields needed

### Adding a new marshal state

1. Add field to `marshal.py __init__`
2. Add to `to_dict()` and `from_dict()` (with `.get()` default)
3. Process in `world_state.py _process_tactical_states()` if per-turn
4. Add blocking logic in `executor.py` if it prevents actions
5. Run `pytest tests/test_serialization_enforcement.py -v`

### Adding a new popup/dialog

```
Backend → Frontend data flow:
  executor.py → main.py → api_client.gd → main.gd
```

1. `executor.py`: Return field in result dict
2. `main.py`: Add early return to pass through the field (most common wiring gap!)
3. `main.gd`: Check for field in `_on_command_result()`
4. Create dialog scene (.tscn) and script (.gd)

**Test with curl BEFORE assuming Godot is broken:**
```bash
curl -X POST http://127.0.0.1:8005/command \
  -H "Content-Type: application/json" \
  -d '{"command": "end turn"}' | python -m json.tool
```

**SERIALIZATION WARNING:** Executor results contain `new_state` (WorldState with circular refs). NEVER embed raw executor results in dicts that reach the API response. Strip first:
```python
cleaned = {k: v for k, v in result.items() if k != "new_state"}
```

### Adding a new combat modifier

1. Add state field to `marshal.py __init__`
2. Apply in `marshal.py get_attack_modifier()` or `get_defense_modifier()` ONLY
3. Add message in `combat.py` (DO NOT recalculate modifier)
4. Clear state in `combat.py` if consumable (AFTER get_*_modifier call)

---

## Serialization Enforcement (MANDATORY)

**"If it exists on the object, it must serialize."**

For ANY new field on ANY model class:
1. Add to `to_dict()` method
2. Add to `from_dict()` method (with `.get(key, default)`)
3. Run: `pytest tests/test_serialization_enforcement.py -v`
4. Update `docs/SAVE_FORMAT_REFERENCE.md`

Serializable classes: Marshal, StrategicOrder, StrategicCondition, WorldState, Region, Trust, AuthorityTracker, VindicationTracker, RegionIntel

---

## Key Code Patterns

```python
# Early returns over deep nesting
if not world:
    return {"success": False, "message": "No world state"}

# getattr for optional fields
recklessness = getattr(marshal, 'recklessness', 0)

# Trust modification
marshal.trust.modify(+10)   # Relative change
marshal.trust.value          # Read-only property

# Enemy actions don't consume player budget
if executing_marshal.nation != world.player_nation:
    is_player_action = False
```

---

## Strategic Commands

Strategic orders (MOVE_TO, PURSUE, HOLD, SUPPORT) cost 2 AP (1 for literal). Key patterns:

- **Tactical objection:** `world.pending_objection` — for per-action objections
- **Strategic objection:** `world.pending_strategic_objection` — for order-issuance objections (different field!)
- **Strategic execution flag:** `command["_strategic_execution"] = True` skips AP cost + objections
- **Cancel:** "cancel/halt/stop/abort" → `_execute_cancel()`, costs 1 AP

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Godot float→int error | Wrap all numeric returns with `int()` |
| Modifier applied twice | Check single source in marshal.py, not combat.py |
| Fortify bonus too small | Check `(1.0 + bonus)` not `(1.0 + bonus * 0.10)` |
| Drill bonus not applying | State cleared AFTER `get_attack_modifier()` call? |
| Display shows wrong % | `* 100` not `* 10` for percentage |
| "No objection pending" | Strategic uses `pending_strategic_objection`, not `pending_objection` |
| Post-objection "Unknown action" | `_execute_post_objection` must handle all actions + strategic routing |
| Strategic detection skipped | Verify `world` is passed to `parser.parse()` |
| Command executes wrong marshal | Interrupt router checks if command names different marshal |
| Sally battles missing | Use direct attack (adjacent), not move→attack (blocked) |
| Strategic reports missing | Auto-advance path must copy ALL turn_result fields |
| AI fortify loop | P0 engagement check at start of `_evaluate_marshal` |
| AI stagnation never resets | Result dicts have action under `ai_action` key, not `action` |
| Enemy AI crash | `game_state` must be dict `{"world": WorldState}`, not WorldState directly |
| Internal names in frontend | Use `_ACTION_DISPLAY_NAMES` or `_action_display_name()` — never raw action strings |
| Response key mismatch | curl test the endpoint to verify key names match what Godot reads |
| None crash on parse field | Guard `.lower()`/`.strip()` — parser may return None for optional fields |
| `.get('key', '')` returns None | Use `(d.get('key') or '')` — `.get()` default only applies for MISSING keys, not `None` values |
| Objection on impossible action | Pre-validate BEFORE objection check — see bypass hierarchy in executor.py |
| AP error after objection proceed | AP must be checked in pre-validation BEFORE objection fires, not after |
| Post-objection wrong AP cost | `_execute_post_objection` must handle `variable_action_cost` (stance 0-2 AP) |
| Data cleared before capture | Save per-turn lists (e.g. mild_concerns) BEFORE calling advance_turn |
| "build" parsed as drill | Mock parser keyword order matters — "build " must be checked BEFORE "train" (substring in "training") |
| Event data missing in Godot | Check if advance_turn return value is captured AND added to tactical_events/events list |

---

## Don't Do

- Return floats to Godot (always `int()`)
- Separate player/enemy marshal dicts
- Add features outside current phase scope
- Change port without updating api_client.gd
- Make executor LLM-dependent (keep deterministic)
- Store API keys in code (use .env)
- Skip serialization for new fields
- Bypass executor for state changes
- Run objection evaluation before action validation (check bypass hierarchy in executor.py)
- Show raw internal action names to players (use `_ACTION_DISPLAY_NAMES` translation)
- Use `.get('key', default)` when value may be `None` — use `(d.get('key') or default)` instead
- Skip AP check before objection evaluation — player should never see objection then AP failure

---

## Commands

```bash
# Backend
python backend/main.py                    # Runs on port 8005

# Tests
pytest tests/ -v                          # Full suite
pytest tests/ -v --tb=no -q              # Quick count
pytest tests/test_objection_v2.py -v     # V2 tests only

# Coverage
pytest tests/ --cov=backend --cov-report=term-missing -v --tb=no -q

# Lint
ruff check backend/                     # Check for issues
ruff check backend/ --fix               # Auto-fix safe issues

# Validate mod
python -m backend.modding.validator path/to/mod.json
```

---

## Document Map

| Need | Read |
|------|------|
| Session state / what's next | `docs/STATUS.md` |
| Phase timeline | `docs/ROADMAP.md` |
| Game systems (combat, trust, disobedience, LLM, cavalry, strategic) | `docs/SYSTEMS_REFERENCE.md` |
| Enemy AI decision tree | `docs/ENEMY_AI_REFERENCE.md` |
| V2 objection refactor | `docs/OBJECTION_V2.md` |
| Save format / serialization | `docs/SAVE_FORMAT_REFERENCE.md` |
| Modding guide | `docs/MODDING_FORMAT.md` |
| Adding marshals or strategic commands | `docs/ADDING_CONTENT.md` |
| Fog of war spec + plan | `docs/FOG_OF_WAR_SPEC.md`, `docs/FOG_IMPLEMENTATION_PLAN.md` |
| Future design concepts | `docs/FUTURE_DESIGN.md` |
| Phase 6 implementation plan | `docs/PHASE6_IMPLEMENTATION_PLAN.md` |
| Game vision | `docs/VISION.md` |
| Manual test plan | `docs/MANUAL_TEST_PLAN.md` |
| Tutorial content / what to teach | `docs/TUTORIAL_SCRIPT.md` |

## Documentation Rules

**If you changed behavior, update the doc that describes it.**

| Event | Update |
|-------|--------|
| Session ends | `docs/STATUS.md` (test count, completed work, next steps) |
| Phase completed | `docs/ROADMAP.md`, `docs/STATUS.md` |
| System behavior changed | `docs/SYSTEMS_REFERENCE.md` |
| New fields added | `docs/SAVE_FORMAT_REFERENCE.md` |

**Phase Status Rules:**
- The "Current Phase" section in CLAUDE.md must ALWAYS list remaining/unbuilt items for the current phase. Completed items get a brief summary. Remaining items are the priority — they must be impossible to miss.
- When completing a session, if the current phase still has unfinished items in ROADMAP.md, CLAUDE.md must say "Phase X IN PROGRESS" with remaining items listed. NEVER let it read as complete when items remain.
- STATUS.md "Current Phase" quick stat must include remaining item count: e.g., "Phase 6: IN PROGRESS (3 items remaining: Fog of War, Manpower, Artillery)"
- When a phase is truly complete (all ROADMAP items done or explicitly deferred), BOTH CLAUDE.md and STATUS.md must be updated to point to the next phase and its first items.
- Any item marked "Deferred" in ROADMAP.md doesn't count as remaining — only "Planned" items that are still in-scope for the current phase.

---

## Environment

```bash
# .env
LLM_MODE=mock              # mock | anthropic | groq
ANTHROPIC_API_KEY=sk-ant-... # Required if LLM_MODE=anthropic
```

Server: `127.0.0.1:8005`, CORS enabled for Godot client.
