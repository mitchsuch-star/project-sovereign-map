# Phase M: Strategic Objections — Design Document

> **Status:** Designed, not yet implemented
> **Last Updated:** February 2, 2026
> **Prerequisite:** Phase 5.2 (Strategic Commands) core complete

---

## Overview

Marshals can object to strategic commands at issuance based on personality. This extends the existing disobedience system to multi-turn orders.

**Core principle:** Objections are RARE. Strategic commands cost 2 AP — constant objections would be frustrating. Uses existing objection probability system (personality × context × authority). Most orders are followed.

---

## Who Objects to What

| Marshal | Personality | Objects to | Rationale |
|---------|-------------|-----------|-----------|
| Ney | Aggressive | HOLD (no enemies adjacent) | "You want me to guard nothing?" |
| Davout | Cautious | PURSUE (bad odds), MOVE_TO (dangerous path) | "This is reckless" |
| Grouchy | Literal | Nothing | Questions clarity, not tactics (handled by clarification popup) |

**Total scenarios:** 3

### Trigger Conditions

**Ney objects to HOLD:**
- Only if NO enemies adjacent to target region
- If enemies adjacent → sally behavior = constant fighting → Ney loves it → no objection

**Davout objects to PURSUE:**
- Only if target strength ≥ 1.2× marshal strength
- Davout wants an edge before committing to chase

**Davout objects to MOVE_TO:**
- Only if path crosses ANY region with enemy marshal present
- Not just enemy-controlled territory — actual troops in the way

---

## Response Options

### Ney Objects to HOLD

| Option | Action | Trust | AP Cost |
|--------|--------|-------|---------|
| **Proceed** | HOLD executes as ordered | -10 | 2 (strategic) |
| **Preferred** | Best aggressive action (see fallback chain) | +12 | 1 (tactical) |
| **Compromise** | Timed HOLD — 3 turns then auto-cancels | +3 | 2 (strategic) |

**Preferred fallback chain** (first valid option wins):
1. Attack adjacent enemy — if one exists in adjacent region
2. PURSUE nearest enemy — if enemy marshal within 3 regions
3. Aggressive stance — if not already aggressive
4. Drill — if not already drilling and no shock_bonus
5. *(skip preferred option)* — if none available, only show Proceed/Compromise

**Compromise details:**
- Sets `strategic_order.conditions.max_turns = 3`
- Still gets +15% immovable bonus and sally behavior during those 3 turns
- After 3 turns: "Ney grows restless and abandons the position"

### Davout Objects to PURSUE

| Option | Action | Trust | AP Cost |
|--------|--------|-------|---------|
| **Proceed** | PURSUE executes as ordered | -10 | 2 (strategic) |
| **Preferred** | Fortify current position | +12 | 1 (tactical) |
| **Compromise** | Cautious PURSUE — auto-cancels if odds drop below 0.8:1 | +3 | 2 (strategic) |

**Preferred:** Always valid (fortify is always available).

**Compromise details:**
- Sets condition: `auto_cancel_below_ratio = 0.8`
- Each turn before moving, check `marshal.strength / target.strength`
- If ratio < 0.8, cancel with message: "Davout breaks off pursuit — the odds have turned against us"

### Davout Objects to MOVE_TO

| Option | Action | Trust | AP Cost |
|--------|--------|-------|---------|
| **Proceed** | Original path through danger | -10 | 2 (strategic) |
| **Preferred** | Stay and fortify | +12 | 1 (tactical) |
| **Compromise** | MOVE_TO with safe pathfinding | +3 | 2 (strategic) |

**Preferred:** Always valid.

**Compromise details:**
- Uses existing cautious pathfinding (`avoid_enemies=True`)
- Only offered if a safe path actually exists
- If ALL paths cross enemies, only show Proceed/Preferred

---

## Bypass Conditions

Strategic objections are SKIPPED entirely when:

1. **Retreat recovery:** Marshal is in retreat recovery (demoralized, compliant)
2. **Already checked:** Post-objection execution (player already responded)
3. **Grouchy:** Literal personality never objects to strategic commands

---

## Implementation Notes

### Replaces Tactical Objection

If `is_strategic=True`, skip the tactical objection check entirely. Strategic objection handles it with context-aware messaging. Prevents double-objection.

### Popup Options Are Dynamic

Only show options that can actually execute:
```python
options = [("proceed", "Proceed as ordered", proceed_description)]

preferred = get_preferred_action(marshal, world, command_type)
if preferred:
    options.append(("trust", preferred.description, preferred.detail))

compromise = get_compromise_action(marshal, world, command_type)
if compromise:
    options.append(("compromise", compromise.description, compromise.detail))
```

### Action Cost Handling

- **Proceed/Compromise:** 2 AP (strategic command cost)
- **Preferred:** 1 AP (becomes tactical action)

The objection popup must track which cost applies based on selection.

---

## Message Templates

**Ney HOLD objection:**
> "Hold position? While there's glory to be won? Give me a real order, sire!"

**Ney timed HOLD (compromise accepted):**
> "Very well — I'll hold for now. But not forever."

**Ney timed HOLD expires:**
> "Ney grows restless and abandons the position at [region]."

**Davout PURSUE objection:**
> "Pursue [target]? Their forces outnumber us. This is reckless."

**Davout cautious PURSUE cancel:**
> "Davout breaks off pursuit of [target] — the odds have turned against us."

**Davout MOVE_TO objection:**
> "That route passes through [enemy region]. We'd be walking into danger."

**Davout safe path (compromise):**
> "I'll find a safer route, even if it takes longer."

---

## Edge Cases to Verify

- [ ] Ney HOLD with enemies adjacent → no objection, sally works
- [ ] Ney HOLD with no enemies anywhere → preferred chain exhausts, shows only Proceed/Compromise
- [ ] Davout PURSUE target that retreats mid-order → ratio check uses current positions
- [ ] Davout MOVE_TO where all paths are dangerous → Compromise hidden
- [ ] Marshal in retreat recovery → no objection fires
- [ ] Grouchy given any strategic command → no objection (clarification popup separate)
- [ ] Player picks Preferred → 1 AP charged, tactical action executes
- [ ] Player picks Proceed → 2 AP charged, strategic order created
- [ ] Timed HOLD expires → order clears, message shown, no trust penalty
- [ ] Marshal dies during timed HOLD → order auto-clears
- [ ] Preferred option target moves before player responds → re-validate on submit
- [ ] Safe path compromise is excessively long → don't offer if > 2x original path

---

## Critical Implementation Notes (from edge case analysis)

### Issue #1: Prevent Double Objection

Tactical objection system must NOT fire on strategic commands. Add check in executor.py:

```python
# BEFORE tactical objection check
is_strategic_command = command.get("is_strategic", False)
if is_strategic_command:
    should_check_objection = False
    # Strategic objection handled separately by _execute_strategic_command
```

### Issue #2: Grouchy Bypass

Literal personality already handled — Grouchy never triggers strategic objection because he's not in the trigger list (only Ney/Davout). The existing clarification popup (ambiguity > 40) remains separate and fires first during parsing, not during objection check.

**Flow for Grouchy:**
1. Parse command → if ambiguous, clarification popup (existing Phase G)
2. After clarification resolved → create StrategicOrder
3. No objection check (Grouchy not in trigger list)
4. Execute

### Issue #4: Timed HOLD Expiry

Add to `StrategicOrder`:
```python
issued_turn: int = 0  # Track when order was created
```

Add to `_execute_strategic_turn()`:
```python
if order.conditions and order.conditions.max_turns:
    turns_elapsed = world.current_turn - order.issued_turn
    if turns_elapsed >= order.conditions.max_turns:
        marshal.strategic_order = None
        return {
            "order_status": "expired",
            "message": f"{marshal.name} grows restless and abandons the position at {marshal.location}."
        }
```

### Issue #5: Davout PURSUE Ratio Clarification

Compare **current** strengths each turn (not snapshot). This lets Davout respond to changing battlefield:

```python
# In _execute_pursue() before moving
if order.conditions and order.conditions.auto_cancel_below_ratio:
    target = world.get_marshal(order.target)
    if target:
        ratio = marshal.strength / max(target.strength, 1)
        if ratio < order.conditions.auto_cancel_below_ratio:
            marshal.strategic_order = None
            return {
                "order_status": "cancelled",
                "message": f"{marshal.name} breaks off pursuit — the odds have turned against us."
            }
```

### Issue #8: Response Routing

Expand `/objection_response` endpoint in main.py to handle both types:
```python
objection_type = request.get("objection_type", "tactical")
if objection_type == "strategic":
    # Route to strategic handler
else:
    # Existing tactical handler
```

### Issue #9: Already-Checked Flag

Add to `StrategicOrder`:
```python
objection_resolved: bool = False  # True after player responds to objection
```

Check before firing objection:
```python
if marshal.strategic_order and marshal.strategic_order.objection_resolved:
    # Skip objection, already handled
```

### Issue #15: Objection Timing

**Objection fires BEFORE first-step execution.** Flow:
1. Parse command → detect strategic
2. Check objection trigger conditions
3. If objection → return pending_objection, DO NOT create order yet
4. Player responds → create order based on choice
5. Execute first step

This prevents "moved then objected" weirdness.

---

## Files to Modify

| File | Changes |
|------|---------|
| `disobedience.py` | Add `check_strategic_objection()` function |
| `executor.py` | Call strategic objection BEFORE `_execute_strategic_command()`, skip tactical objection if `is_strategic=True` |
| `strategic.py` | Add timed HOLD expiry check, cautious PURSUE ratio check, `issued_turn` field |
| `marshal.py` | Add `objection_resolved` field to StrategicOrder, add `issued_turn` field |
| `main.py` | Handle strategic objection response routing (expand `/objection_response`) |
| `schemas.py` | Add `auto_cancel_below_ratio` to StrategicCondition |

---

## Test Plan (TDD Approach)

### Phase 1: Write Tests First (RED)

**File:** `tests/test_strategic_objections.py`

```python
# Trigger condition tests
def test_ney_objects_to_hold_no_enemies_adjacent():
def test_ney_no_objection_hold_enemies_adjacent():
def test_davout_objects_to_pursue_bad_odds():
def test_davout_no_objection_pursue_good_odds():
def test_davout_objects_to_move_dangerous_path():
def test_davout_no_objection_move_safe_path():
def test_grouchy_never_objects_to_strategic():

# Bypass tests
def test_no_objection_during_retreat_recovery():
def test_no_objection_if_already_resolved():
def test_tactical_objection_skipped_for_strategic():

# Response execution tests
def test_ney_hold_proceed_executes_hold():
def test_ney_hold_preferred_attacks_adjacent():
def test_ney_hold_preferred_pursues_if_no_adjacent():
def test_ney_hold_preferred_stance_if_no_targets():
def test_ney_hold_preferred_drill_fallback():
def test_ney_hold_compromise_timed_hold():
def test_davout_pursue_proceed_executes():
def test_davout_pursue_preferred_fortifies():
def test_davout_pursue_compromise_cautious():
def test_davout_move_proceed_dangerous_path():
def test_davout_move_preferred_fortifies():
def test_davout_move_compromise_safe_path():

# Timed HOLD expiry tests
def test_timed_hold_expires_after_3_turns():
def test_timed_hold_clears_on_marshal_death():

# Cautious PURSUE tests
def test_cautious_pursue_cancels_below_ratio():
def test_cautious_pursue_continues_above_ratio():

# Edge case tests
def test_preferred_target_moved_revalidates():
def test_safe_path_too_long_hides_compromise():
def test_preferred_chain_exhausted_shows_two_options():

# AP cost tests
def test_proceed_costs_2_ap():
def test_preferred_costs_1_ap():
def test_compromise_costs_2_ap():

# Trust tests
def test_proceed_trust_minus_10():
def test_preferred_trust_plus_12():
def test_compromise_trust_plus_3():
```

### Phase 2: Implement (GREEN)

Order of implementation:
1. `StrategicOrder` fields (`issued_turn`, `objection_resolved`)
2. `StrategicCondition` fields (`max_turns`, `auto_cancel_below_ratio`)
3. `check_strategic_objection()` in disobedience.py
4. Executor integration (skip tactical, call strategic objection)
5. Response handlers in executor.py
6. Timed HOLD expiry in strategic.py
7. Cautious PURSUE ratio check in strategic.py
8. main.py routing

### Phase 3: Refactor (REFACTOR)

- Extract preferred chain logic to helper function
- Consolidate objection message templates
- Add serialization for new fields
