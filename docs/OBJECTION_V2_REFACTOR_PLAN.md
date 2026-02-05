# Objection System V2: Complete Refactor Plan

**Status:** DESIGN FINALIZED
**Author:** Claude Code Design Session
**Date:** 2026-02-05
**Estimated Effort:** V2a (7-11 days), V2b (deferred to Phase 7)

---

## Executive Summary

The current objection system has a fundamental flaw: **trust modifies WHETHER marshals speak, when it should modify HOW they speak**. High-trust marshals go silent about objectively dangerous situations, killing the game's core differentiator (marshal personality) as the game progresses.

**The Fix:** Separate situational triggers (deterministic) from trust consequences (variable). Marshals ALWAYS voice concerns when situations match their personality; trust determines tone, penalties, and compliance.

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Design Decisions (Finalized)](#2-design-decisions-finalized) ← **NEW: All decisions locked**
3. [Design Philosophy](#3-design-philosophy)
4. [V2a Core System](#4-v2a-core-system)
5. [V2b Defiance System](#5-v2b-defiance-system)
6. [Grouchy Integration](#6-grouchy-integration-already-implemented)
7. [Edge Cases & Bypasses](#7-edge-cases--bypasses)
8. [Regression Prevention](#8-regression-prevention)
9. [Migration Strategy](#9-migration-strategy)
10. [Test Plan](#10-test-plan)
11. [Frontend Changes](#11-frontend-changes)
12. [Implementation Checklist](#12-implementation-checklist)

---

## 1. Problem Statement

### Current Behavior (Broken)

```python
# Current: Trust reduces objection PROBABILITY
severity = base_severity × trust_mod × vindication × authority × variance
if severity >= 0.50: OBJECTION

# Davout (trust=85, cautious) facing 10:1 odds:
# Base: 0.68 × trust_mod(0.7) = 0.476 < 0.50
# Result: NO OBJECTION (silent march to death)
```

### Why This Is Wrong

1. **High-trust marshals give LEAST feedback** - the opposite of realistic command relationships
2. **Core gameplay loop fades** - as trust builds, objections disappear
3. **Personality becomes irrelevant** - cautious marshal stays quiet about suicidal odds
4. **Player loses strategic feedback** - no warning about bad decisions

### Desired Behavior

```python
# New: Situation determines IF marshal speaks, trust determines HOW
concern = evaluate_situation(personality, action, context)  # Deterministic
if concern >= MODERATE:
    tone, penalty, compliance = get_trust_consequences(trust_tier)
    show_objection(tone, penalty, compliance)
```

---

## 2. Design Decisions (Finalized)

> **These decisions are LOCKED. Not suggestions. Not open questions.**
> All edge cases resolved in design session Feb 5, 2026.

### 2.1 ConcernLevel System (V2a)

Replace the current severity float (0.0-0.95) with a deterministic ConcernLevel enum. Personality × situation → ConcernLevel. No trust modifier on the trigger. No randomness in triggers.

| ConcernLevel | What Happens | Popup? | Trust Impact? | Defiance? |
|--------------|--------------|--------|---------------|-----------|
| NONE | Order executes normally | No | No | No |
| MILD | Flavor text in end-of-turn log only | No | No | No |
| MODERATE | Popup: Trust / Insist / Compromise | Yes | Yes | No (V2a). Yes (V2b) only at STRONG+ |
| STRONG | Emphatic popup + defiance chance | Yes | Yes | V2b only |
| EXTREME | Crisis popup + high defiance chance | Yes | Yes | V2b only |

In V2a, STRONG and EXTREME behave identically to MODERATE (popup with choices, no defiance). Defiance is V2b scope.

### 2.2 Trust Tier Consequences (V2a)

This is the core fix. Trust no longer modifies WHETHER a marshal speaks. Trust modifies HOW they speak — their tone, the penalty for insisting, and compliance probability.

| Tier | Trust Range | Tone | Insist Penalty | Compliance |
|------|-------------|------|----------------|------------|
| DEVOTED | 80+ | Respectful | -5 | 100% |
| TRUSTING | 50-79 | Firm | -10 | 95% |
| WARY | 30-49 | Challenging | -12 | 80% |
| HOSTILE | <30 | Defiant | -15 | 60% |

A DEVOTED Ney and a HOSTILE Ney both object to defending when enemies are nearby. The DEVOTED Ney says it respectfully and costs -5 to override. The HOSTILE Ney says it with contempt and costs -15. Same trigger, different consequences. That's the design.

### 2.3 MILD Flavor Text Rules (V2a)

MILD is atmosphere, not feedback. It should feel like reading war dispatches in the turn log, not like the game judging the player's command.

**How it works:**
1. Player types "Ney, defend Belgium"
2. Order executes immediately, no comment, no popup
3. At end of turn, the turn log includes flavor like "Ney was restless on the defensive line" alongside other events
4. Player notices it if they're paying attention. It's color, not a challenge.

**How it's different from V1 grumble:**
- V1 grumble (severity 0.20-0.49): Shows immediately as a response to the command. Feels like feedback on the player's decision.
- V2a MILD: Shows later in the turn log alongside all other events. Feels like atmosphere.

**Rules:**
- Max 1 MILD message per marshal per turn (prevents log noise)
- MILD never produces a popup, never affects trust, never triggers defiance

### 2.4 Popup Frequency Cap (V2a)

- Max 1 MODERATE+ popup per marshal per turn
- If a marshal already triggered a MODERATE/STRONG/EXTREME popup this turn, any additional concerns from that same marshal cap at MILD (turn log flavor only)
- This prevents one marshal from generating 3 popups in one turn when the player gives multiple orders

### 2.5 Trigger Table Scaling Requirement (V2a — CRITICAL)

Concern levels MUST scale with situational context. A flat "aggressive always objects to defend at MODERATE" feels worse than V1. Both directions need gradation:

**Cautious (Davout) objecting to attack — scales with how outnumbered:**

| Situation | ConcernLevel |
|-----------|--------------|
| Attack at ~1.5:1 odds against | MILD |
| Attack at ~2:1 odds against | MODERATE |
| Attack at ~3:1 odds against | STRONG |
| Attack at ~5:1+ odds against | EXTREME |

**Aggressive (Ney) objecting to defend/hold — scales with enemy proximity AND enemy weakness:**

| Situation | ConcernLevel |
|-----------|--------------|
| Defend/hold, no enemy nearby | MILD |
| Defend/hold, enemy in adjacent region | MODERATE |
| Defend/hold, weak enemy adjacent (outnumber 2:1+) | STRONG |
| Defend/hold, nearly destroyed enemy adjacent (outnumber 3:1+) | EXTREME |

### 2.6 Vindication Evaluation Rules (V2a tracks, V2b uses for escalation)

Vindication only changes based on battle outcomes. No combat = no vindication change. Ever.

**Timing depends on what the marshal advocated for:**

**Aggressive marshal trusted** (example: Ney says "let me attack," player trusts, Ney attacks):
- Vindication evaluates on the outcome of the attack during that same PLAYER TURN
- Win = vindication +1
- Loss = vindication -1
- Result is immediate because aggressive action creates an immediate provable outcome

**Cautious marshal trusted** (example: Davout says "don't attack, defend instead," player trusts):
- Vindication evaluates during the NEXT ENEMY PHASE only
- Enemy attacks Davout and Davout holds/wins = vindication +1
- Enemy attacks Davout and Davout loses = vindication -1
- Enemy does NOT attack Davout = inconclusive, vindication unchanged

**Implementation:** Store `pending_defensive_vindication` in VindicationTracker (NOT on Marshal model — keep marshal clean).

**Why this asymmetry is intentional:** Cautious marshals naturally build vindication slower because they depend on the enemy to create the test. Aggressive marshals create provable outcomes immediately.

Trusting a vindicated marshal does NOT further increase vindication. You're agreeing with someone already proven right — that's not new evidence.

### 2.7 Vindication Decay (V2a)

- Vindication decays by 1 per 3 turns of no objection activity from that marshal
- Single universal decay rate for all personalities — no per-personality differences
- Prevents permanent vindication escalation from one early-game lucky streak

### 2.8 Vindication Escalation (V2b ONLY — do NOT implement in V2a)

- Vindication stacks can escalate a concern by maximum +1 level
- MILD → MODERATE: yes. MILD → STRONG: never.
- MODERATE → STRONG: yes. MODERATE → EXTREME: never.
- This cap prevents vindication from creating crisis events from minor situations

### 2.9 Defiance Mechanics (V2b ONLY — do NOT implement in V2a)

- Triggers only at STRONG and EXTREME concern levels
- Base defiance chance: STRONG 15%, EXTREME 35%
- **Hard cap: 40%** per marshal regardless of all modifier stacking
- 3-turn cooldown after any defiance (success or failure). Cannot defy again during cooldown.
- Successful defiance DOES grant vindication +1. The marshal was right, everyone saw it, this creates the growing "losing control" tension.
- Successful defiance still costs -5 authority. Even correct insubordination destabilizes command.
- Failed defiance resets vindication to 0. One bad call humbles them completely.
- Failed defiance: 3-turn cooldown + trust drop + increased compliance for several turns
- Marshal's defiance action = their personality-preferred action (Ney charges, Davout fortifies)
- Grouchy NEVER defies. Not in V2a. Not in V2b. Ever.

### 2.10 Hostile Trust Handling

- Trust floor: 5. Trust can never drop below 5.
- Trust tier always visible in marshal UI tooltip — show DEVOTED / TRUSTING / WARY / HOSTILE with appropriate color coding
- No new redemption event needed. The existing advisor role and grant autonomy systems already handle low-trust recovery.

### 2.11 Grouchy (Literal Personality)

- Never objects. Uses clarification system instead (already implemented and working).
- Never defies. Not in V2a, not in V2b. This is permanent.
- Not affected by vindication. The vindication system does not apply to literal personality.
- Precision bonuses for clear orders already exist (+15% combat modifier). This doesn't need new work.
- Grouchy's gameplay identity is inverted: Other marshals are rewarded for being trusted. Grouchy is rewarded for receiving clear, specific orders.

### 2.12 Migration Approach

- **No feature flag.** Replace the existing system directly. Do not maintain two parallel systems.
- Git history is the rollback. We're not running production with users.
- **Atomic migration:** Both tactical and strategic objections move to V2 at the same time. They share `calculate_objection_severity()` and `DisobedienceSystem.evaluate_order()` — you can't split them without maintaining two severity systems simultaneously.
- **Preserve `evaluate_objection()` return dict shape.** Replace internals, not interface. This minimizes test breakage.

---

## 3. Design Philosophy

> Note: The locked design decisions in Section 2 take precedence. This section provides context.

### Core Principles

| Principle | Old System | New System |
|-----------|------------|------------|
| When marshal speaks | Trust × Severity (probabilistic) | Situation × Personality (deterministic) |
| What trust affects | Probability of speaking | Tone, penalty, compliance |
| Randomness | In trigger calculation | Only in defiance/compliance rolls |
| High trust meaning | "Stays silent" | "Respectful advice, low penalty" |

### ConcernLevel Enum

```python
class ConcernLevel(Enum):
    NONE = 0      # No concern → nothing happens
    MILD = 1      # Minor → flavor text only, NO popup, NO trust impact
    MODERATE = 2  # Clear → popup, player must respond
    STRONG = 3    # Serious → emphatic popup + defiance chance (V2b)
    EXTREME = 4   # Crisis → near-refusal + high defiance (V2b)
```

### TrustTier Consequences

| Trust Tier | Range | Tone | Insist Penalty | Compliance |
|------------|-------|------|----------------|------------|
| DEVOTED | 80+ | respectful | -5 | 100% |
| TRUSTING | 50-79 | firm | -10 | 95% |
| WARY | 30-49 | challenging | -12 | 80% |
| HOSTILE | <30 | defiant | -15 | 60% |

---

## 4. V2a Core System

V2a fixes the core problem without adding complexity. Ship this first.

### 4.1 Situational Triggers (Deterministic)

> **Important:** See Section 2.5 for scaling requirements. Triggers must scale with context severity.

**AGGRESSIVE personality (Ney, Blucher):**

| Action | Condition | ConcernLevel |
|--------|-----------|--------------|
| defend, fortify, hold, wait | No enemy nearby | MILD |
| defend, fortify, hold, wait | Enemy ADJACENT | MODERATE |
| defend, fortify, hold, wait | Weak enemy adjacent (outnumber 2:1+) | STRONG |
| defend, fortify, hold, wait | Nearly destroyed enemy adjacent (outnumber 3:1+) | EXTREME |
| retreat | Not actually threatened | STRONG |
| retreat | Threatened but not outnumbered 2:1 | MILD |
| drill | Enemy adjacent | MODERATE |

**CAUTIOUS personality (Davout, Wellington):**

| Action | Condition | ConcernLevel |
|--------|-----------|--------------|
| attack | Outnumbered 5:1+ | EXTREME |
| attack | Outnumbered 3:1+ | STRONG |
| attack | Outnumbered 2:1+ | MODERATE |
| attack | Outnumbered 1.5:1+ | MILD |
| move | Path crosses enemy region | MODERATE |
| aggressive stance | Enemy adjacent | MILD |

**BALANCED personality:** *(future — no current marshals, not tested in V2a)*

| Action | Condition | ConcernLevel |
|--------|-----------|--------------|
| attack | Outnumbered 3:1+ | STRONG |
| attack | Outnumbered 5:1+ | EXTREME |
| move | Exposes capital | MODERATE |

**LOYAL personality:** *(future — no current marshals, not tested in V2a)*

| Action | Condition | ConcernLevel |
|--------|-----------|--------------|
| attack | Outnumbered 5:1+ | MODERATE |
| attack | Outnumbered 10:1+ | STRONG |

**LITERAL personality (Grouchy):**
- See [Section 6: Grouchy Integration](#6-grouchy-integration-already-implemented)

### 4.2 MILD Handling (End-of-Turn Flavor Text Only)

```python
# MILD = turn log message at END OF TURN, NO popup, NO trust impact
if concern == ConcernLevel.MILD:
    return {
        "type": "mild_concern",
        "message": generate_mild_flavor(marshal, action),  # Dispatch-style
        "execute": True,  # Order proceeds immediately
        "trust_change": 0,
        "popup": False
    }
```

**Turn log display (appears with other end-of-turn events):**
> Ney was restless on the defensive line.
> Davout expressed reservations about the attack odds.

**NOT immediate response.** See Section 2.3 for full rules.

### 4.3 MODERATE+ Handling (Popup)

```python
if concern >= ConcernLevel.MODERATE:
    trust_tier = get_trust_tier(marshal)
    consequences = CONSEQUENCE_TABLE[trust_tier]

    return {
        "type": "objection",
        "concern_level": concern.name,
        "tone": consequences["tone"],
        "message": generate_message(marshal, concern, trust_tier),
        "insist_penalty": consequences["penalty"],
        "compliance_chance": consequences["compliance"],
        "options": build_options(concern, consequences),
        "popup": True
    }
```

### 4.4 New File Structure

```
backend/commands/
├── objection_v2.py          # NEW: Core V2 system
│   ├── ConcernLevel enum
│   ├── TrustTier enum
│   ├── SITUATIONAL_TRIGGERS dict
│   ├── CONSEQUENCE_TABLE dict
│   ├── evaluate_situation()
│   ├── get_trust_tier()
│   ├── evaluate_objection()  # Main entry point
│   └── generate_message()
├── disobedience.py          # MODIFY: Route to V2
├── severity.py              # DEPRECATE: Keep for reference
└── vindication.py           # EXTEND: V2b integration
```

---

## 5. V2b Defiance System

V2b adds the defiance/vindication/authority feedback loop. **Deferred to Phase 7 — do NOT implement in V2a.**

### 5.1 Defiance Mechanic (STRONG/EXTREME only)

```python
# Only at STRONG and EXTREME concern levels
if concern >= ConcernLevel.STRONG:
    defiance_chance = calculate_defiance_chance(marshal, world)
    if random() < defiance_chance:
        # Marshal ignores order, does preferred action
        return execute_preferred_action(marshal, world)
```

### 5.2 Defiance Chance Calculation

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

    # Calculate and cap — HARD CAP 40%
    final = base + vindication_mod + authority_mod + trust_mod
    return min(0.40, max(0.0, final))  # Cap at 40% per Section 2.9
```

### 5.3 Defiance Outcome Feedback Loop

**If defiance SUCCEEDS (marshal's action works):**
- Vindication +1 (they were right to defy)
- Player authority -5 (other marshals notice)
- Trust +2 (grudging respect)

**If defiance FAILS (marshal's action goes badly):**
- Vindication reset to 0 (humbled)
- Player authority +3 (player was right)
- Trust -5 (embarrassment)
- Defiance cooldown: 3 turns (too ashamed to defy again)

### 5.4 Authority as Global Stat

```python
# Authority affects ALL marshals' defiance chances
class AuthorityTracker:
    authority: int = 100  # Napoleon starts fully authoritative

    def get_defiance_modifier(self):
        if self.authority >= 80:
            return -0.10  # Strong leader, less defiance
        elif self.authority >= 50:
            return 0.0    # Normal
        else:
            return +0.10  # Weak leader, more defiance
```

**Authority changes from:**
- Defiance outcomes (success: -5, failure: +3)
- Vindication events
- Major victories: +5
- Major defeats: -5
- Trusting too often: -2 per trust choice above 60%

---

## 6. Grouchy Integration (ALREADY IMPLEMENTED)

### Current State: Already Working

Grouchy's literal personality is **already correctly implemented** and does NOT need changes for V2:

**Working Features:**
- ✅ Clarification popups for vague strategic targets (ambiguity ≥ 61)
- ✅ Ambiguity-scaled combat bonuses (+15%/+10%/+5% based on order clarity)
- ✅ Precision Execution (+1 to all skills for 3 turns when ambiguity ≤ 20)
- ✅ HOLD Immovable ability (+15% defense when holding_position=True)
- ✅ Never-object bypass in `check_strategic_objection()`
- ✅ Strategic command cost reduction (1 AP instead of 2)
- ✅ "The Grouchy Moment" - Strategic HOLD never interrupts for cannon fire

### How Grouchy Differs from Other Marshals

| Other Marshals | Grouchy (Literal) |
|----------------|-------------------|
| Object (refuse orders) | Clarify (ask questions) |
| Trust/Insist/Compromise popup | Clarify/Confirm/Cancel popup |
| Trust penalty for insisting | No trust penalty |
| Can disobey (V2b) | NEVER disobeys |
| Affected by vindication | Gets precision bonuses instead |

### V2 Requirements for Grouchy

**V2 must preserve these behaviors:**

1. **Bypass objection system entirely** - Grouchy skips `evaluate_objection()`
2. **Keep clarification separate** - Clarification is NOT an objection
3. **Keep precision bonuses** - Already work via ambiguity scoring
4. **No defiance** (V2b) - Grouchy never defies, even at HOSTILE trust

```python
# In evaluate_objection() - preserve this bypass
if personality == "literal":
    return None  # Grouchy uses clarification system, not objection
```

### Future Enhancement (NOT V2)

The following are **not implemented** but could be added in a future phase:
- Clarification for tactical commands (currently only strategic)
- Order history tracking for contradiction detection
- Frequent order change detection

These are **out of scope for V2** - Grouchy already has meaningful interplay.

---

## 7. Edge Cases & Bypasses

The objection system must handle these edge cases. **V2 must preserve ALL existing bypasses.**

### 7.1 Bypass Hierarchy (Check Order)

```python
def should_check_objection(marshal, action, world):
    # 1. Broken state - TOTAL lockdown
    if getattr(marshal, 'broken', False):
        return False  # Only recruit allowed

    # 2. Retreat recovery - compliant
    if getattr(marshal, 'retreat_recovery', 0) > 0:
        return False  # Demoralized, accepts orders

    # 3. Autonomous - AI controlled
    if getattr(marshal, 'autonomous', False):
        return False  # Player cannot command

    # 4. Administrative role - not in field
    if getattr(marshal, 'administrative', False):
        return False  # Cannot command

    # 5. Drilling locked - committed to training
    if getattr(marshal, 'drilling_locked', False):
        return False  # Hard block

    # 6. Fortified + move/attack - must unfortify first
    if getattr(marshal, 'fortified', False) and action in ['move', 'attack']:
        return False  # Validation error, not objection

    # 7. Non-objectionable action
    if action not in OBJECTION_ACTIONS:
        return False

    # 8. Enemy marshal
    if marshal.nation != world.player_nation:
        return False

    return True  # Proceed to objection check
```

### 7.2 Major Objections Per Turn Cap

```python
MAX_MAJOR_OBJECTIONS_PER_TURN = 2

# If cap reached, downgrade to MILD
if world.disobedience_system.major_objections_this_turn >= MAX_MAJOR_OBJECTIONS_PER_TURN:
    return create_mild_concern(marshal, action)  # Auto-resolve
```

**Why:** Prevents decision fatigue from popup spam.

### 7.3 Strategic vs Tactical Objection

| Type | When | Storage | Handler |
|------|------|---------|---------|
| Tactical | During execute() | `world.pending_objection` | `handle_objection_response()` |
| Strategic | At order creation | `world.pending_strategic_objection` | `_handle_strategic_objection_from_endpoint()` |

**CRITICAL:** Always check `pending_strategic_objection` BEFORE `pending_objection` in response handler.

### 7.4 Cavalry Limits (Not Subject to Objection)

Cavalry auto-switch at 3 turns is **automatic**, not negotiable:

```python
# Happens at turn start, bypasses objection system
if cavalry and turns_in_defensive_stance >= 3:
    marshal.stance = AGGRESSIVE
    marshal.trust.modify(-3)  # Penalty, not objection
```

### 7.5 Pending Objection Blocking

While objection awaits response, ALL commands blocked:

```python
if world.pending_objection is not None:
    return {
        "success": False,
        "message": "A marshal awaits your response!",
        "awaiting_response": True
    }
```

---

## 8. Regression Prevention

These bugs were fixed before. **V2 must not re-introduce them.**

### 8.1 CRITICAL Regressions to Prevent

| Bug | What Happened | Prevention |
|-----|---------------|------------|
| #2 Redemption spam | Redemption popup triggered every turn | Check `redemption_pending` flag BEFORE triggering |
| #6 AP double-charge | AP consumed on objection trigger AND response | Skip AP when `pending_objection=True`, charge on response |
| #7 Strategic routing | Strategic objection used wrong pending field | Use `pending_strategic_objection`, not `pending_objection` |
| #8 Type mismatch | Checked `"major"` but system returns `"major_objection"` | Use correct string constant |
| #15 Strategic probability | Strategic used flat 50% instead of severity chain | Apply full modifier chain to strategic too |
| #16 Strategic AP timing | Strategic AP charged before response | Same fix as tactical: skip on trigger |

### 8.2 Pattern Checklist

Before merging V2, verify:

- [ ] Trust and Authority are INDEPENDENT (not coupled)
- [ ] AP consumed ONLY on response, never on trigger
- [ ] Objection type string matches check (`"major_objection"`)
- [ ] Strategic uses `pending_strategic_objection`
- [ ] Retreat recovery checked BEFORE objection
- [ ] All alternatives are LEGAL (validate against game state)
- [ ] Clarification gates disobedience for literal
- [ ] Variance preserved for borderline cases (MILD)

### 8.3 Test Coverage Requirements

These tests MUST pass before merge:

```python
# From test_disobedience.py - verify these still work
test_trust_initialization()
test_trust_modify_clamping()
test_high_trust_guaranteed_obedience()
test_authority_record_response()
test_severity_calculation_basic()
test_vindication_recorded_on_choice()

# New V2 tests
test_high_trust_still_objects_to_bad_odds()  # THE KEY TEST
test_same_situation_different_trust_both_object()
test_trust_affects_penalty_not_probability()
test_mild_concern_no_popup()
test_strong_concern_always_voices()
test_grouchy_clarification_not_objection()
test_bypass_hierarchy_correct_order()
```

---

## 9. Migration Strategy

> **No feature flag.** Replace directly. Git history is the rollback. See Section 2.12.

### 9.1 Migration Approach

**Atomic replacement:** Replace the existing severity-based system directly. Do not maintain two parallel systems. Both tactical and strategic objections move to V2 at the same time since they share core functions.

**Interface preservation:** Keep `evaluate_objection()` return dict shape unchanged. Replace internals, not interface. This minimizes test breakage.

### 9.2 Migration Phases

**Phase 1: V2a Backend (3-4 days)**
1. Create `objection_v2.py` with core logic
2. Implement `ConcernLevel` enum and situational triggers
3. Implement `TrustTier` enum and consequence table
4. Wire into `executor.py` directly (no feature flag)
5. Update `disobedience.py` to route through V2

**Phase 2: V2a Tests (2-3 days)**
1. Write new tests for deterministic triggers
2. Write tests for trust tier consequences
3. Update existing tests that assert on severity values
4. Verify all tests pass

**Phase 3: V2a Frontend (1-2 days)**
1. Update objection_dialog.gd for tone-based styling
2. Add MILD flavor text to tactical_events
3. Test full flow

**Phase 4: V2a Stabilization (1-2 days)**
1. Playtest extensively
2. Tune trigger thresholds
3. Fix edge cases discovered

**V2b deferred to Phase 7** (defiance, vindication escalation)

### 9.3 Rollback Plan

If V2 has critical issues:
1. `git revert` the V2 commits
2. Restore previous severity-based system
3. No data migration needed (fields are additive)

---

## 10. Test Plan

### 10.1 Unit Tests (objection_v2.py)

```python
class TestSituationalTriggers:
    def test_aggressive_defend_enemy_in_region_is_strong()
    def test_aggressive_defend_enemy_adjacent_is_moderate()
    def test_aggressive_defend_no_enemies_is_none()
    def test_cautious_attack_3x_outnumbered_is_extreme()
    def test_cautious_attack_even_odds_is_none()
    def test_literal_never_triggers_objection()

class TestTrustTiers:
    def test_trust_85_is_devoted()
    def test_trust_60_is_trusting()
    def test_trust_35_is_wary()
    def test_trust_20_is_hostile()

class TestConsequences:
    def test_devoted_low_penalty()
    def test_hostile_high_penalty()
    def test_same_situation_different_trust_both_object()

class TestMildHandling:
    def test_mild_no_popup()
    def test_mild_no_trust_change()
    def test_mild_order_executes()

class TestGrouchyClarification:
    def test_grouchy_generic_target_triggers_clarification()
    def test_grouchy_clarification_no_trust_penalty()
    def test_grouchy_clear_order_precision_bonus()
```

### 10.2 Integration Tests

```python
class TestExecutorIntegration:
    def test_objection_ap_not_consumed_on_trigger()
    def test_objection_ap_consumed_on_response()
    def test_strategic_objection_uses_correct_pending_field()
    def test_bypass_hierarchy_correct_order()

class TestFrontendFlow:
    def test_objection_data_reaches_godot()
    def test_mild_appears_in_turn_log()
    def test_clarification_popup_for_grouchy()
```

### 10.3 Regression Tests

All existing tests in `test_disobedience.py` must pass with feature flag OFF.

---

## 11. Frontend Changes

### 11.1 Objection Dialog Updates

```gdscript
# objection_dialog.gd
func show_objection(data: Dictionary):
    var tone = data.get("tone", "firm")

    # Tone-based styling
    match tone:
        "respectful":
            panel.add_theme_color_override("border", Color.GOLD)
            header_label.text = "Marshal's Advice"
        "firm":
            panel.add_theme_color_override("border", Color.ORANGE)
            header_label.text = "Marshal's Concern"
        "challenging":
            panel.add_theme_color_override("border", Color.RED)
            header_label.text = "Marshal Objects"
        "defiant":
            panel.add_theme_color_override("border", Color.DARK_RED)
            header_label.text = "Marshal Refuses"
```

### 11.2 MILD Flavor Text

```gdscript
# main.gd - in process_command_result()
if result.has("mild_concern"):
    var msg = result.mild_concern.message
    turn_log.add_text("[color=yellow]%s[/color]\n" % msg)
    # No popup, order proceeds
```

### 11.3 Clarification Popup (Existing)

```gdscript
# clarification_popup.gd (NEW FILE)
extends CanvasLayer

signal choice_made(choice: String, target: String)

func show_clarification(data: Dictionary):
    marshal_label.text = data.marshal
    message_label.text = data.message

    # Build interpretation buttons
    for interp in data.suggested_interpretations:
        var btn = Button.new()
        btn.text = interp.label
        btn.pressed.connect(func(): choice_made.emit("clarify", interp.target))
        interpretations_container.add_child(btn)

    # Confirm as-is button
    confirm_button.pressed.connect(func(): choice_made.emit("confirm", ""))

    # Cancel button (free action)
    cancel_button.pressed.connect(func(): choice_made.emit("cancel", ""))
```

### 11.4 Defiance Outcome Popup (V2b — deferred)

```gdscript
# defiance_outcome_dialog.gd (NEW FILE)
func show_defiance(data: Dictionary):
    marshal_label.text = "%s Defied Orders!" % data.marshal

    if data.outcome == "success":
        outcome_label.text = "...and it worked!"
        outcome_label.add_theme_color_override("font_color", Color.GREEN)
    else:
        outcome_label.text = "...and it failed."
        outcome_label.add_theme_color_override("font_color", Color.RED)

    message_label.text = data.message
    vindication_label.text = "Vindication: %+d" % data.vindication_change
    authority_label.text = "Authority: %+d" % data.authority_change
```

---

## 12. Implementation Checklist

### V2a Checklist

- [ ] Create `backend/commands/objection_v2.py`
- [ ] Implement `ConcernLevel` enum
- [ ] Implement `TrustTier` enum
- [ ] Implement `SITUATIONAL_TRIGGERS` for Aggressive, Cautious, Literal
- [ ] Implement `CONSEQUENCE_TABLE`
- [ ] Implement `evaluate_situation()` - deterministic
- [ ] Implement `get_trust_tier()` - simple tier lookup
- [ ] Implement `evaluate_objection()` - preserve return dict shape!
- [ ] Implement `generate_message()` - tone-aware messages
- [ ] Wire into `executor.py` directly (no feature flag)
- [ ] Route `disobedience.py` through V2
- [ ] Update `objection_dialog.gd` for tone styling
- [ ] Add MILD flavor text to `tactical_events`
- [ ] Add `pending_defensive_vindication` to VindicationTracker
- [ ] Write unit tests for triggers
- [ ] Write unit tests for consequences
- [ ] Write integration tests
- [ ] Update existing severity tests
- [ ] Verify all regression tests pass
- [ ] Playtest and tune thresholds

### V2b Checklist (Deferred to Phase 7)

- [ ] Add `defiance_chance` calculation (40% hard cap)
- [ ] Add `defiance_cooldown` field to Marshal
- [ ] Implement defiance outcome handling
- [ ] Implement vindication escalation (+1 level max)
- [ ] Create `defiance_outcome_dialog.gd`
- [ ] Write tests for defiance mechanics
- [ ] Write tests for feedback loop stability
- [ ] Playtest for degenerate loops
- [ ] Tune defiance chances and caps

### Grouchy Checklist (Preserve Existing Behavior)

Grouchy (literal personality) is already implemented correctly. V2a must preserve:

- [x] Clarification popups for vague strategic targets (ALREADY WORKING)
- [x] Precision execution bonuses (ALREADY WORKING)
- [x] Never objects — uses clarification instead (ALREADY WORKING)
- [ ] Verify Grouchy bypasses `evaluate_objection()` in V2
- [ ] Verify Grouchy NEVER shows objection popup
- [ ] Verify Grouchy NEVER defies (permanent, not even in V2b)

---

## Appendix A: File Change Summary

| File | Change Type | Effort |
|------|-------------|--------|
| `backend/commands/objection_v2.py` | NEW | High |
| `backend/commands/disobedience.py` | MODIFY (routing) | Medium |
| `backend/commands/severity.py` | DEPRECATE | Low |
| `backend/commands/executor.py` | MODIFY (integration) | Medium |
| `backend/commands/vindication.py` | EXTEND (pending_defensive_vindication) | Low |
| `backend/main.py` | MINOR (pass-through) | Low |
| `godot-client/.../objection_dialog.gd` | MODIFY (styling) | Medium |
| `godot-client/.../clarification_popup.gd` | EXISTING (no changes) | None |
| `godot-client/.../defiance_outcome_dialog.gd` | NEW (V2b — deferred) | Medium |
| `tests/test_objection_v2.py` | NEW | High |

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| ConcernLevel | How strongly situation matches personality concern (NONE→EXTREME) |
| TrustTier | Categorization of trust value (DEVOTED, TRUSTING, WARY, HOSTILE) |
| Defiance | Marshal ignores order and does preferred action (V2b) |
| Vindication | Track record of being right/wrong, affects future defiance |
| Clarification | Grouchy asking for specifics (not objection) |
| Precision Execution | Bonus Grouchy gets for crystal-clear orders |

---

## Appendix C: Decision Log

| Decision | Rationale |
|----------|-----------|
| Split V2a/V2b | Lower risk, fix core problem first. V2b deferred to Phase 7. |
| Deterministic triggers | Predictable = testable = debuggable |
| MILD as flavor only | Reduces popup fatigue, feels like war dispatches |
| Grouchy clarification separate | Preserves "never objects" personality |
| No feature flag | Git history is rollback. No parallel system maintenance. |
| Trust affects consequences only | Core design fix — the whole point of V2 |
| Preserve return dict shape | Minimizes test breakage |
| Vindication in VindicationTracker | Keep Marshal model clean |
| Defiance hard cap 40% | Prevent degenerate spirals |

---

**Document Version:** 2.0 (Design Finalized)
**Last Updated:** 2026-02-05
**Status:** Ready for implementation
**Next Review:** After V2a implementation
