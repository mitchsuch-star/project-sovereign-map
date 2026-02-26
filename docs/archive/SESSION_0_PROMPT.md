# Session 0: Prerequisite Bug Fix — Wire `record_response()` in V2a Path

## Context

You are working on a Napoleonic strategy game. The V2a objection system lets marshals object to orders — player responds with "trust", "insist", or "compromise". The `AuthorityTracker` class tracks these responses to penalize excessive trusting (pushover behavior). But there's a **bug**: the V2a executor path never calls `authority_tracker.record_response()`. The authority system is inert for V2a objections.

This is a prerequisite fix for V2b (Defiance system). Do NOT implement any V2b features — just fix this wiring gap.

## The Bug

`AuthorityTracker.record_response(choice)` is defined at `backend/models/authority.py:52`. It records the player's choice and evaluates authority changes.

**Where it IS called (V1 path only):** `backend/commands/disobedience.py:1121`
```python
authority.record_response(choice)
```

**Where it is NOT called but SHOULD be (V2a path):**

1. **Tactical objections:** `executor.py:handle_objection_response()` (line 10398). This method handles player responses to `world.pending_objection`. After the player's choice is processed and trust is modified, `record_response()` should be called. It is not.

2. **Strategic objections:** `executor.py:_handle_strategic_objection_from_endpoint()` (line 10079). This method handles player responses to `world.pending_strategic_objection`. It delegates to `_handle_strategic_objection_response()` (line 5881) which applies trust changes. `record_response()` is never called in this flow either.

## What to Do

### Step 1: Read the relevant code

Read these files/sections to understand the flow:
- `backend/models/authority.py` — full file (small, ~235 lines). Understand `record_response()`, `_evaluate_authority()`, `recent_responses`.
- `backend/commands/executor.py:10398-10607` — `handle_objection_response()`. Find where trust is modified and where `record_response()` should go.
- `backend/commands/executor.py:10079-10164` — `_handle_strategic_objection_from_endpoint()`. This delegates to `_handle_strategic_objection_response()`.
- `backend/commands/executor.py:5881-5960` — `_handle_strategic_objection_response()`. Find where trust is modified for each response type (proceed/preferred/compromise).

### Step 2: Wire `record_response()`

**Tactical path** — In `handle_objection_response()`, after the choice is processed and trust is modified, add:
```python
# Record response in authority tracker (V2a wiring — was only in V1 path)
world.authority_tracker.record_response(choice)
```
Place it AFTER `world.pending_objection = None` (line 10458) and BEFORE the disobey/redemption checks. This ensures the choice is recorded regardless of whether the marshal disobeys or a redemption event fires.

**Strategic path** — In `_handle_strategic_objection_from_endpoint()`, after the response is processed but before return. The choice variable maps: "trust"→"preferred", "insist"→"proceed", "compromise"→"compromise". Use the ORIGINAL `choice` variable (not `strategic_response`) for `record_response()` since authority tracks "trust"/"insist"/"compromise", not "preferred"/"proceed".

Add after line 10136 (`world.pending_strategic_objection = None`):
```python
# Record response in authority tracker (V2a wiring)
world.authority_tracker.record_response(choice)
```

### Step 3: Write tests

Create `tests/test_session0_authority_wiring.py` with ~5 tests:

1. **Tactical trust response records:** Set up a `pending_objection`, call `handle_objection_response("trust", ...)`, verify `world.authority_tracker.recent_responses` contains "trust".

2. **Tactical insist response records:** Same but with "insist". Verify it's in `recent_responses`.

3. **Tactical compromise response records:** Same but with "compromise".

4. **Strategic response records:** Set up a `pending_strategic_objection`, call `handle_objection_response("trust", ...)` (which routes to `_handle_strategic_objection_from_endpoint`), verify `recent_responses` contains "trust".

5. **Authority threshold event fires:** Call `handle_objection_response` with "trust" enough times (need 5+ responses) to trigger authority penalty via `_evaluate_authority()`. Verify authority drops below starting value of 100.

**Test setup pattern** — For tactical objection tests, you need:
```python
world.pending_objection = {
    "marshal": "Ney",
    "original_order": {"action": "attack", "target": "Wellington", "marshal": "Ney"},
    "concern_level": "MODERATE",
    "suggested_alternative": {"action": "defend", "marshal": "Ney"},
    "compromise": None,
    "insist_penalty": -10,
    "trust_gain": 3,
    "tone": "firm",
}
```

For strategic objection tests, you need:
```python
world.pending_strategic_objection = {
    "marshal_name": "Ney",
    "original_command": {"action": "move", "target": "Rhine", "marshal": "Ney"},
    "parsed_command": {"command": {"action": "move", "target": "Rhine", "marshal": "Ney"}, "is_strategic": True},
    "strategic_type": "MOVE_TO",
    "path": ["Belgium", "Rhine"],
    "target": "Rhine",
    "options": [...],  # Need valid options structure
    "insist_penalty": -10,
    "trust_gain": 3,
    "compromise_gain": 3,
}
```

Look at existing test files (especially `tests/test_objection_v2.py` and `tests/test_executor.py`) for setup patterns. Use the same fixtures/helpers they use.

### Step 4: Run full test suite

```bash
".venv\Scripts\python.exe" -m pytest tests/ -v --tb=short
```

Confirm zero regressions. Report exact count.

### Step 5: Confidence Report

After completing, report:

```
SESSION 0 CONFIDENCE REPORT
═══════════════════════════
Tests written: X passed / Y total
Edge cases verified:
  - [ ] Tactical trust/insist/compromise all record
  - [ ] Strategic trust/insist/compromise all record
  - [ ] record_response() uses original choice string ("trust"/"insist"/"compromise"), not mapped strategic string
  - [ ] Authority threshold event dict returned when threshold crossed
  - [ ] Full existing test suite passes (X tests, 0 failures)
Regressions checked: full test suite
Confidence: XX%
Blockers for Session 1: [none / list]
```

## Rules

- Do NOT start any V2b work (no defiance, no vindication changes, no new marshal fields)
- Do NOT change `record_response()` signature (keep it as `choice: str`)
- Do NOT modify `authority.py` at all — only modify `executor.py` and create the test file
- Follow project conventions: `int()` all numbers to Godot, use `getattr` for optional fields
- Use Windows-style paths for pytest: `".venv\Scripts\python.exe" -m pytest`
