# V2 Objection System

> **V2a is COMPLETE and implemented.** For V2a design details, see `docs/archive/OBJECTION_V2A_DESIGN.md`.
> For implemented V2a behavior, see `docs/SYSTEMS_REFERENCE.md` Section 2 (Disobedience/Trust).
> This document covers **V2b plans** (Phase 7) and the **Quick Reference** for the current system.

---

## Table of Contents

1. [V2b Preview](#1-v2b-preview)
2. [Quick Reference](#2-quick-reference)

---

## 1. V2b Preview

V2b adds the defiance/vindication/authority feedback loop. **Deferred to Phase 7 -- do NOT implement in V2a.**

### Fog-of-War Objection Triggers (V2b Scope)

> **Designed in `docs/FOG_OF_WAR_SPEC.md` §6.** These triggers require fog of war (Phase 6) + V2b (Phase 7) to be implemented.

| Situation | Cautious (Davout) | Aggressive (Ney) | Literal (Grouchy) |
|-----------|-------------------|-------------------|--------------------|
| Attack into UNKNOWN region | MODERATE -> STRONG | No concern | Follows orders |
| Attack on STALE intel (3+ turns) | MODERATE | MILD at most | Follows orders |
| Refuse to attack when scout shows weakness | No concern | MODERATE -> STRONG | No concern |
| PURSUE target with no intel | STRONG | MILD | Depends on order clarity |

**Existing Davout PURSUE fix (disobedience.py:1609):** Currently Davout objects to PURSUE with bad odds against ANY enemy regardless of distance. With fog:
- FULL visibility: object as now (sees odds)
- PARTIAL: object based on strength band comparison only
- STALE/LAST_KNOWN/UNKNOWN: cannot object on odds, may object on staleness ("Three-day-old intelligence, Sire.")

**Implementation note:** `objection_v2.py` has 8+ helper functions that access enemy data without fog awareness (`_check_enemy_adjacent`, `_get_friendly_to_enemy_ratio`, etc.). Phase 6 fog adds a `get_visible_enemies_near()` helper that returns actual data now. V2b switches these helpers to use fog-filtered data. See `docs/FOG_IMPLEMENTATION_PLAN.md` issue H4.

### Defiance Mechanic (STRONG/EXTREME Only)

```python
if concern >= ConcernLevel.STRONG:
    defiance_chance = calculate_defiance_chance(marshal, world)
    if random() < defiance_chance:
        return execute_preferred_action(marshal, world)  # Marshal ignores order
```

### Defiance Chance Calculation

```python
def calculate_defiance_chance(marshal, world):
    # Base chances
    if concern == ConcernLevel.STRONG:
        base = 0.15  # 15%
    elif concern == ConcernLevel.EXTREME:
        base = 0.35  # 35%

    # Modifiers
    vindication_mod = marshal.vindication_score * 0.10  # +10% per stack
    authority_mod = -0.10 if world.authority >= 80 else (+0.10 if world.authority < 50 else 0)
    trust_mod = +0.15 if trust_tier == HOSTILE else (-0.10 if trust_tier == DEVOTED else 0)

    # HARD CAP 40%
    final = base + vindication_mod + authority_mod + trust_mod
    return min(0.40, max(0.0, final))
```

### Defiance Outcomes

**If defiance SUCCEEDS (marshal's action works):**
- Vindication +1 (they were right to defy)
- Player authority -5 (other marshals notice)
- Trust +2 (grudging respect)
- Successful defiance still costs -5 authority. Even correct insubordination destabilizes command.

**If defiance FAILS (marshal's action goes badly):**
- Vindication reset to 0 (humbled)
- Player authority +3 (player was right)
- Trust -5 (embarrassment)
- 3-turn cooldown (too ashamed to defy again)
- Increased compliance for several turns

### Defiance Rules

- 3-turn cooldown after any defiance (success or failure)
- Marshal's defiance action = their personality-preferred action (Ney charges, Davout fortifies)
- Grouchy NEVER defies. Not in V2a. Not in V2b. Ever.
- V2b disobey_chance should have its own variance band (+/-5-8%) so players can't memorize exact thresholds

### Authority as Global Stat (V2b)

```python
class AuthorityTracker:
    authority: int = 100  # Napoleon starts fully authoritative

    def get_defiance_modifier(self):
        if self.authority >= 80:
            return -0.10  # Strong leader, less defiance
        elif self.authority >= 50:
            return 0.0
        else:
            return +0.10  # Weak leader, more defiance
```

Authority changes from: defiance outcomes (success: -5, failure: +3), vindication events, major victories (+5), major defeats (-5), trusting too often (-2 per trust choice above 60%).

---

## 2. Quick Reference

### File Locations

| File | Purpose |
|------|---------|
| `backend/commands/objection_v2.py` | Core V2 system: enums, triggers, evaluators, consequence table |
| `backend/commands/disobedience.py` | Routing layer (modified to call V2) |
| `backend/commands/executor.py` | Pipeline integration (V2 wiring, message generators) |
| `backend/commands/vindication.py` | Extended with `pending_defensive_vindication` |
| `backend/models/world_state.py` | New fields: `mild_concerns_this_turn`, `objection_popups_this_turn` |
| `backend/main.py` | `mild_concerns` passthrough in response dict |
| `tests/test_objection_v2.py` | V2 unit tests (127 tests) |
| `tests/test_disobedience.py` | Existing tests (V1 behavior, compatible with V2) |
| `tests/test_strategic_objections.py` | Strategic objection tests (Unit 6: migrated to V2 semantics) |
| `docs/SAVE_FORMAT_REFERENCE.md` | Updated with new serialization fields |

### Test Commands

```bash
# Run V2 tests only
pytest tests/test_objection_v2.py -v

# Run all tests
pytest tests/ -v --tb=no -q

# Quick count
pytest tests/ -v --tb=no -q 2>&1 | tail -3
```

### Bypass Hierarchy (Check Order)

Before entering the V2 objection system, these bypasses are checked in order.
**Key principle: Objection evaluation must run AFTER action validation — if the action would fail validation anyway, there's nothing to object to.**

```python
def should_check_objection(marshal, action, world):
    # 1. Broken state - TOTAL lockdown
    if getattr(marshal, 'broken', False): return False
    # 2. Retreat recovery - compliant
    if getattr(marshal, 'retreat_recovery', 0) > 0: return False
    # 3. Autonomous - AI controlled
    if getattr(marshal, 'autonomous', False): return False
    # 4. Administrative role - not in field
    if getattr(marshal, 'administrative', False): return False
    # 5. Drilling locked - committed to training
    if getattr(marshal, 'drilling_locked', False): return False
    # 6. Fortified + move/attack - validation error, not objection
    if getattr(marshal, 'fortified', False) and action in ['move', 'attack']: return False
    # 7. Non-objectionable action
    if action not in OBJECTION_ACTIONS: return False
    # 8. Enemy marshal
    if marshal.nation != world.player_nation: return False
    return True  # Proceed to V2 objection check

# ADDITIONAL pre-validation (returns failure BEFORE objection):
# - Already in target stance → stance_change fails (no objection)
# - Already defensive + fortified → defend fails (no objection)
# - Already fortified → fortify fails (no objection)
# - Already drilling → drill fails (no objection)
# - Aggressive stance → fortify/drill blocked (no objection)
# - Not in danger → retreat blocked (no objection)
```

### Strategic vs Tactical Objection Storage

| Type | When | Storage | Handler |
|------|------|---------|---------|
| Tactical | During execute() | `world.pending_objection` | `handle_objection_response()` |
| Strategic | At order creation | `world.pending_strategic_objection` | `_handle_strategic_objection_from_endpoint()` |

**CRITICAL:** Always check `pending_strategic_objection` BEFORE `pending_objection` in response handler.

### Key Design Decisions (Locked)

| Decision | Rationale |
|----------|-----------|
| ConcernLevel replaces severity float | Deterministic, testable, personality-specific |
| TrustTier determines TONE, not WHETHER | Core V2 innovation — high trust = respectful tone, not silence |
| MILD = no popup (flavor only) | Atmosphere without interruption |
| Vindication in VindicationTracker | Keep Marshal model clean |
| Defiance hard cap 40% (V2b) | Prevent degenerate spirals |
| Per-marshal popup cap only | Global cap is exploitable. Per-marshal (max 1 per turn) is sufficient. |
| Authority inert in V2a | V2b gives it purpose. Do not add placeholder effects. |
| Trust floor: 5 | Trust can never drop below 5. Existing redemption systems handle low-trust recovery. |
