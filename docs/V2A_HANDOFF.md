# V2a Implementation Handoff

**Date:** February 5, 2026
**Status:** Units 1-3 complete, Units 4-7 remaining
**Tests:** 1195 passed, 3 skipped

---

## What Was Completed

### Unit 1: Core Data Structures (53 tests)
**File:** `backend/commands/objection_v2.py`

- `ConcernLevel` enum: NONE, MILD, MODERATE, STRONG, EXTREME
- `TrustTier` enum: HOSTILE (<30), WARY (30-49), TRUSTING (50-79), DEVOTED (80+)
- `get_trust_tier(trust)` - Returns TrustTier from trust value
- `calculate_trust_gain(concern, tier)` - Scaled trust gain when player trusts marshal
- `get_insist_penalty(tier)` - Trust penalty when player insists
- `get_objection_tone(tier)` - "defiant", "challenging", "firm", "respectful"
- `apply_mood_variance(concern)` - 15-20% chance of ±1 level shift
- `handle_objection_response(response_type, concern, tier)` - Returns trust change
- Backward compat helpers: `concern_to_legacy_severity()`, `is_popup_concern()`, `is_blocking_concern()`

### Unit 2: Tactical Trigger Evaluators (36 tests)
**File:** `backend/commands/objection_v2.py`

- `evaluate_aggressive(marshal, action, order, game_state)` - Returns ConcernLevel for aggressive personality
  - defend/fortify/hold/wait: MILD (no enemy) to EXTREME (3:1+ advantage)
  - retreat: STRONG (not threatened) to NONE (outnumbered 2:1 + low morale)
  - drill with enemy adjacent: MODERATE
- `evaluate_cautious(marshal, action, order, game_state)` - Returns ConcernLevel for cautious personality
  - attack: MILD (1.5:1) to EXTREME (5:1+), +1 level if fortified
  - move through enemy: MODERATE
  - aggressive stance with enemy: MILD
- `evaluate_literal(marshal, action, order, game_state)` - Always NONE (uses clarification)
- `evaluate_situation(marshal, action, order, game_state)` - Main dispatcher

### Unit 3: Strategic Trigger Evaluators (30 tests)
**File:** `backend/commands/objection_v2.py`

- `evaluate_strategic_aggressive(marshal, order_type, target, path, game_state)`
  - HOLD no enemies: MODERATE
  - HOLD with 2:1+ advantage: STRONG/EXTREME (wants to attack)
- `evaluate_strategic_cautious(marshal, order_type, target, path, game_state)`
  - PURSUE bad odds: MILD (1.2-1.5:1) to EXTREME (5:1+)
  - MOVE_TO/HOLD/SUPPORT through enemy: MODERATE
- `evaluate_strategic_literal(...)` - Always NONE
- `evaluate_strategic_situation(...)` - Main strategic dispatcher

---

## What Remains

### Unit 4: Pipeline Integration (REVIEW NEEDED)

**Goal:** Wire V2 evaluators into `executor.py`, replacing V1 severity-based system.

**Key changes needed:**

1. **In `executor.py`:**
   - Import V2 functions from `objection_v2.py`
   - Replace calls to `check_objection()` with V2 `evaluate_situation()`
   - Replace calls to `check_strategic_objection()` with V2 `evaluate_strategic_situation()`
   - Handle MILD concerns: append to `world.mild_concerns_this_turn`, execute order
   - Handle MODERATE+: create popup, store in `world.pending_objection` or `world.pending_strategic_objection`
   - Add `concern_level` field to all return dicts

2. **In `world_state.py`:**
   - Add `mild_concerns_this_turn: List[Dict] = []` field
   - Add `objection_popups_this_turn: Set[str] = set()` field (per-marshal cap)
   - Clear both at turn start
   - Add to `to_dict()` / `from_dict()`

3. **In `main.py`:**
   - Pass `mild_concerns` through in response dict

4. **Return dict shapes (from V2A_IMPLEMENTATION_ADDENDUM.md Part 9):**

```python
# MILD return dict
{
    "type": "mild_concern",
    "concern_level": "MILD",
    "marshal": str,
    "message": str,
    "execute": True,
    "popup": False,
}

# MODERATE+ return dict (must include pending_objection for executor AP skip)
{
    "pending_objection": True,  # CRITICAL for backward compat
    "type": "major_objection",
    "concern_level": "MODERATE",  # or STRONG, EXTREME
    "severity": float,  # Legacy compat via concern_to_legacy_severity()
    "marshal": str,
    "personality": str,
    "message": str,
    "tone": str,
    "insist_penalty": int,
    "options": list,
    # ... other existing fields
}
```

5. **Per-marshal popup cap:**
```python
# Before showing popup:
if marshal.name in world.objection_popups_this_turn:
    # Already had popup this turn - cap at MILD
    concern = ConcernLevel.MILD

# After showing popup:
world.objection_popups_this_turn.add(marshal.name)
```

**Files to modify:**
- `backend/commands/executor.py` - Main integration point
- `backend/commands/disobedience.py` - Keep for response handling, but V1 evaluators deprecated
- `backend/models/world_state.py` - New fields
- `backend/main.py` - Pass through mild_concerns

**Risk:** Multi-system integration. Recommend incremental approach: tactical first, then strategic.

---

### Unit 5: Vindication Extension (IMPLEMENT)

**Goal:** Add `pending_defensive_vindication` to VindicationTracker for defensive vindication.

**File:** `backend/commands/vindication.py`

**Changes needed:**

1. Add field to VindicationTracker:
```python
self.pending_defensive_vindication: Dict[str, Dict] = {}
# Format: {"Davout": {"order": {...}, "timestamp": turn}}
```

2. Add to `to_dict()`:
```python
"pending_defensive_vindication": self.pending_defensive_vindication,
```

3. Add to `from_dict()`:
```python
tracker.pending_defensive_vindication = data.get("pending_defensive_vindication", {})
```

4. Update `docs/SAVE_FORMAT_REFERENCE.md` with new field

**Tests needed:**
- Serialization roundtrip for new field
- Default empty dict on load

---

### Unit 6: Test Migration

Update existing tests in:
- `tests/test_disobedience.py` - Replace severity float assertions with ConcernLevel
- `tests/test_strategic_objections.py` - Update for deterministic triggers

Most tests should pass unchanged since they test behavior, not implementation.

---

### Unit 7: Godot Frontend

- Tone-based styling in `objection_dialog.gd`
- MILD flavor in turn log
- Smoke test

---

## Key Design Documents

1. **`docs/OBJECTION_V2_REFACTOR_PLAN.md`** - Full V2a design spec
2. **`docs/V2A_IMPLEMENTATION_ADDENDUM.md`** - Resolved ambiguities, Part 9 has Q1-Q7 answers
3. **`docs/STATUS.md`** - Current progress

---

## Quick Test Commands

```bash
# Run V2 tests only
pytest tests/test_objection_v2.py -v

# Run all tests
pytest tests/ -v --tb=no -q

# Quick count
pytest tests/ -v --tb=no -q 2>&1 | tail -3
```

---

## Next Session Tasks

1. **Review Unit 4** - Read executor.py and disobedience.py to understand integration points
2. **Implement Unit 5** - Add pending_defensive_vindication (straightforward)
3. **If time:** Start Unit 4 tactical integration
