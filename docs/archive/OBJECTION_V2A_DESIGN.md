# V2a Objection System — Archived Design

> **ARCHIVED:** V2a is fully implemented. This document preserves the original design spec.
> For current V2b plans, see `docs/OBJECTION_V2.md`.
> For implemented behavior, see `docs/SYSTEMS_REFERENCE.md` Section 2.

---

## 1. Overview

### The Fundamental Flaw

The V1 objection system has a fundamental flaw: **trust modifies WHETHER marshals speak, when it should modify HOW they speak**. High-trust marshals go silent about objectively dangerous situations, killing the game's core differentiator (marshal personality) as the game progresses.

```python
# V1 (Broken): Trust reduces objection PROBABILITY
severity = base_severity * trust_mod * vindication * authority * variance
if severity >= 0.50: OBJECTION

# Davout (trust=85, cautious) facing 10:1 odds:
# Base: 0.68 * trust_mod(0.7) = 0.476 < 0.50
# Result: NO OBJECTION (silent march to death)
```

### Why This Is Wrong

1. **High-trust marshals give LEAST feedback** -- the opposite of realistic command relationships
2. **Core gameplay loop fades** -- as trust builds, objections disappear
3. **Personality becomes irrelevant** -- cautious marshal stays quiet about suicidal odds
4. **Player loses strategic feedback** -- no warning about bad decisions

### The Fix

Separate situational triggers (deterministic) from trust consequences (variable). Marshals ALWAYS voice concerns when situations match their personality; trust determines tone, penalties, and compliance.

```python
# V2 (Fixed): Situation determines IF marshal speaks, trust determines HOW
concern = evaluate_situation(personality, action, context)  # Deterministic
if concern >= MODERATE:
    tone, penalty, compliance = get_trust_consequences(trust_tier)
    show_objection(tone, penalty, compliance)
```

| Principle | Old System (V1) | New System (V2) |
|-----------|-----------------|-----------------|
| When marshal speaks | Trust x Severity (probabilistic) | Situation x Personality (deterministic) |
| What trust affects | Probability of speaking | Tone, penalty, compliance |
| Randomness | In trigger calculation | Only in mood variance (15-20% band) and defiance/compliance rolls (V2b) |
| High trust meaning | "Stays silent" | "Respectful advice, low penalty" |

---

## 2. V2a Design

V2a fixes the core problem without adding complexity. Ship this first.

### 2.1 ConcernLevel Enum

```python
class ConcernLevel(Enum):
    NONE = 0      # No concern -> nothing happens
    MILD = 1      # Minor -> flavor text only, NO popup, NO trust impact
    MODERATE = 2  # Clear -> popup, player must respond
    STRONG = 3    # Serious -> emphatic popup + defiance chance (V2b)
    EXTREME = 4   # Crisis -> near-refusal + high defiance (V2b)
```

| ConcernLevel | What Happens | Popup? | Trust Impact? | Defiance? |
|--------------|--------------|--------|---------------|-----------|
| NONE | Order executes normally | No | No | No |
| MILD | Flavor text in end-of-turn log only | No | No | No |
| MODERATE | Popup: Trust / Insist / Compromise | Yes | Yes | No (V2a). Yes (V2b) only at STRONG+ |
| STRONG | Emphatic popup + defiance chance | Yes | Yes | V2b only |
| EXTREME | Crisis popup + high defiance chance | Yes | Yes | V2b only |

In V2a, STRONG and EXTREME behave identically to MODERATE (popup with choices, no defiance). Defiance is V2b scope.

### 2.2 TrustTier Enum and Consequences

Trust no longer modifies WHETHER a marshal speaks. Trust modifies HOW they speak -- their tone, the penalty for insisting, and compliance probability.

```python
class TrustTier(Enum):
    HOSTILE = 0   # <30
    WARY = 1      # 30-49
    TRUSTING = 2  # 50-79
    DEVOTED = 3   # 80+

def get_trust_tier(trust: int) -> TrustTier:
    if trust >= 80: return TrustTier.DEVOTED
    if trust >= 50: return TrustTier.TRUSTING
    if trust >= 30: return TrustTier.WARY
    return TrustTier.HOSTILE
```

| Tier | Trust Range | Tone | Insist Penalty | Compliance |
|------|-------------|------|----------------|------------|
| DEVOTED | 80+ | Respectful | -5 | 100% |
| TRUSTING | 50-79 | Firm | -10 | 95% |
| WARY | 30-49 | Challenging | -12 | 80% |
| HOSTILE | <30 | Defiant | -15 | 60% |

A DEVOTED Ney and a HOSTILE Ney both object to defending when enemies are nearby. The DEVOTED Ney says it respectfully and costs -5 to override. The HOSTILE Ney says it with contempt and costs -15. Same trigger, different consequences.

**Compliance chance is HIDDEN in V2a.** In V2a, insist always works. Showing "60% compliance" that always succeeds is a lie. The field is omitted from return dicts until V2b gives it teeth.

### 2.3 Trust Gain Scaling

Trust gain scales with BOTH concern level AND trust tier.

**Base gain from concern level (when player trusts marshal's advice):**

| Concern Level | Base Trust Gain |
|---------------|-----------------|
| MODERATE | +3 |
| STRONG | +5 |
| EXTREME | +8 |
| MILD | +0 (no popup, no choice, no gain) |

**Tier multiplier (rubber-band effect):**

| Trust Tier | Multiplier | Effect |
|------------|------------|--------|
| HOSTILE (<30) | 1.5x | Rebuilding rewarded |
| WARY (30-49) | 1.2x | Recovery encouraged |
| TRUSTING (50-79) | 1.0x | Baseline |
| DEVOTED (80+) | 0.7x | Diminishing returns |

**Combined trust gain = int(base x multiplier)** (truncation, not rounding)**:**

| | HOSTILE (1.5x) | WARY (1.2x) | TRUSTING (1.0x) | DEVOTED (0.7x) |
|---|---|---|---|---|
| **MODERATE** (+3) | +4 | +3 | +3 | +2 |
| **STRONG** (+5) | +7 | +6 | +5 | +3 |
| **EXTREME** (+8) | +12 | +9 | +8 | +5 |

**Compare to insist penalties:**

| Trust Tier | Insist Cost | Trust on MODERATE | Trust on EXTREME |
|------------|-------------|-------------------|------------------|
| HOSTILE | -15 | +4 | +12 |
| WARY | -12 | +3 | +9 |
| TRUSTING | -10 | +3 | +8 |
| DEVOTED | -5 | +2 | +5 |

**Compromise is FLAT at +3 regardless of tier.** This prevents "always compromise" from being the optimal strategy. Known: compromise (+3) slightly beats trust (+2) at DEVOTED+MODERATE. Acceptable — 1 point delta. Revisit in V2b.

```python
TRUST_GAIN_BASE = {
    ConcernLevel.MODERATE: 3,
    ConcernLevel.STRONG: 5,
    ConcernLevel.EXTREME: 8,
}

TRUST_TIER_MULTIPLIER = {
    TrustTier.HOSTILE: 1.5,
    TrustTier.WARY: 1.2,
    TrustTier.TRUSTING: 1.0,
    TrustTier.DEVOTED: 0.7,
}

def calculate_trust_gain(concern: ConcernLevel, tier: TrustTier) -> int:
    base = TRUST_GAIN_BASE.get(concern, 0)
    multiplier = TRUST_TIER_MULTIPLIER.get(tier, 1.0)
    return int(base * multiplier)

def handle_response(response_type, concern_level, trust_tier):
    if response_type == "trust":
        return calculate_trust_gain(concern_level, trust_tier)  # Scaled
    elif response_type == "compromise":
        return 3  # Flat, always
    elif response_type == "insist":
        return get_insist_penalty(trust_tier)  # Scaled by tier
```

### 2.4 MILD Flavor Text Rules

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

**Storage:** `world.mild_concerns_this_turn` (list of dicts), cleared at turn start.

```python
# When MILD fires (in objection_v2.py):
world.mild_concerns_this_turn.append({
    "marshal": marshal.name,
    "message": generate_mild_flavor(marshal, action, context)
})

# Check before appending (max 1 per marshal):
if any(m["marshal"] == marshal.name for m in world.mild_concerns_this_turn):
    return  # Already have MILD for this marshal this turn
```

### 2.5 Popup Frequency Cap

Per-marshal cap ONLY. No global cap.

- Max 1 MODERATE+ popup per marshal per turn
- If a marshal already triggered a popup this turn, additional concerns cap at MILD
- Tracked via `world.objection_popups_this_turn` (a `set()`), cleared at turn start

```python
# Per-marshal tracking
if marshal.name in world.objection_popups_this_turn:
    concern = ConcernLevel.MILD  # Downgrade to turn log flavor

# After showing popup:
world.objection_popups_this_turn.add(marshal.name)
```

**Rationale (from playtesting discussion):** A global cap creates an exploit where giving suicidal orders to N marshals causes marshal N+1's EXTREME concern to downgrade to MILD. Per-marshal cap is sufficient. With 3 marshals (Waterloo) = max 3 popups. With 30 marshals (1805 campaign), the player won't give bad orders to more than a few per turn.

### 2.6 Mood Variance

Marshals are humans. A ~15-20% chance that borderline situations shift +/-1 level keeps things unpredictable while remaining vastly more predictable than V1.

```python
import random

def apply_mood_variance(concern: ConcernLevel) -> ConcernLevel:
    """
    Small random variance at tier boundaries.
    ~15-20% chance of shifting +/-1 level.
    Represents day-to-day mood of a human commander.
    """
    if concern == ConcernLevel.NONE:
        return concern  # Never promote NONE to MILD randomly

    roll = random.random()
    if roll < 0.10:
        # 10% chance to go UP one level (cap at EXTREME)
        return ConcernLevel(min(concern.value + 1, ConcernLevel.EXTREME.value))
    elif roll < 0.25:
        # 15% chance to go DOWN one level (floor at MILD, never to NONE)
        new_val = max(concern.value - 1, ConcernLevel.MILD.value)
        return ConcernLevel(new_val)
    return concern  # 75% stays at evaluated level
```

**Rules:**
- NONE never promotes to MILD randomly (no fake concerns)
- Variance never drops below MILD (if base was MILD+, it stays at least MILD)
- 75% of the time, trigger is exactly as evaluated
- Apply AFTER the pure evaluation function, BEFORE the popup/MILD routing
- This is the ONLY source of randomness in V2a triggers

**For tests:** Either (a) mock `random.random()` to get deterministic results, or (b) test the pure evaluation function BEFORE variance is applied.

### 2.7 Vindication Rules

Vindication only changes based on battle outcomes. No combat = no vindication change. Ever.

**Timing depends on what the marshal advocated for:**

**Aggressive marshal trusted** (Ney says "let me attack," player trusts, Ney attacks):
- Vindication evaluates on the outcome of the attack during that same PLAYER TURN
- Win = vindication +1, Loss = vindication -1
- Result is immediate because aggressive action creates an immediate provable outcome

**Cautious marshal trusted** (Davout says "don't attack, defend instead," player trusts):
- Vindication evaluates during the NEXT ENEMY PHASE only
- Enemy attacks Davout and Davout holds/wins = vindication +1
- Enemy attacks Davout and Davout loses = vindication -1
- Enemy does NOT attack Davout = inconclusive, vindication unchanged

**Implementation:** Store `pending_defensive_vindication` in VindicationTracker (NOT on Marshal model -- keep marshal clean).

**Vindication decay:** -1 per 3 turns of no objection activity from that marshal. Single universal decay rate for all personalities. Prevents permanent vindication escalation from early-game lucky streaks.

**Vindication escalation (V2b ONLY -- do NOT implement in V2a):**
- Vindication stacks can escalate a concern by maximum +1 level
- MILD -> MODERATE: yes. MILD -> STRONG: never.
- MODERATE -> STRONG: yes. MODERATE -> EXTREME: never.

### 2.8 Grouchy (Literal Personality)

Grouchy's literal personality is already correctly implemented and does NOT need changes for V2:

- Never objects. Uses clarification system instead (already working).
- Never defies. Not in V2a, not in V2b. This is permanent.
- Not affected by vindication. The vindication system does not apply to literal personality.
- Precision bonuses for clear orders already exist (+15% combat modifier).
- Grouchy's gameplay identity is inverted: Other marshals are rewarded for being trusted. Grouchy is rewarded for receiving clear, specific orders.

| Other Marshals | Grouchy (Literal) |
|----------------|-------------------|
| Object (refuse orders) | Clarify (ask questions) |
| Trust/Insist/Compromise popup | Clarify/Confirm/Cancel popup |
| Trust penalty for insisting | No trust penalty |
| Can disobey (V2b) | NEVER disobeys |
| Affected by vindication | Gets precision bonuses instead |

```python
# In evaluate_objection() -- preserve this bypass
if personality == "literal":
    return None  # Grouchy uses clarification system, not objection
```

### 2.9 Authority in V2a

Authority has NO mechanical effect in V2a. It is tracked but inert.

```python
# V2a: authority is tracked but inert
# It exists as a field (world.authority or world.authority_tracker)
# but is NOT referenced in evaluate_situation() or get_trust_tier()
# V2b gives it purpose in defiance calculations
```

Do NOT fake it. Do NOT add placeholder effects. Just don't touch it.

---

## 3. Trigger Tables

Triggers MUST scale with situational context. A flat "aggressive always objects to defend at MODERATE" feels worse than V1. Both directions need gradation.

### 3.1 Aggressive Personality (Ney, Blucher)

**Tactical Triggers:**

| Action | Condition | ConcernLevel |
|--------|-----------|--------------|
| defend, fortify, hold, wait | No enemy nearby | MILD |
| defend, fortify, hold, wait | Enemy ADJACENT | MODERATE |
| defend, fortify, hold, wait | Weak enemy adjacent (outnumber 2:1+) | STRONG |
| defend, fortify, hold, wait | Nearly destroyed enemy adjacent (outnumber 3:1+) | EXTREME |
| retreat | Not actually threatened | STRONG |
| retreat | Threatened but not outnumbered 2:1 | MILD |
| retreat | Outnumbered 2:1+ AND low morale | NONE |
| drill | Enemy adjacent | MODERATE |

**Implementation:**

```python
def evaluate_aggressive(marshal, action, order, game_state) -> ConcernLevel:
    if action in ("defend", "fortify", "hold", "wait"):
        enemy_adjacent = _check_enemy_adjacent(marshal, game_state)
        if not enemy_adjacent:
            return ConcernLevel.MILD
        ratio = _get_friendly_to_enemy_ratio(marshal, game_state)
        if ratio >= 3.0:
            return ConcernLevel.EXTREME
        if ratio >= 2.0:
            return ConcernLevel.STRONG
        return ConcernLevel.MODERATE

    if action == "retreat":
        if not _is_actually_threatened(marshal, game_state):
            return ConcernLevel.STRONG
        if not _is_outnumbered_2to1(marshal, game_state):
            return ConcernLevel.MILD
        return ConcernLevel.NONE  # Outnumbered 2:1+, retreat makes sense

    if action == "drill" and _check_enemy_adjacent(marshal, game_state):
        return ConcernLevel.MODERATE

    return ConcernLevel.NONE
```

### 3.2 Cautious Personality (Davout, Wellington)

**Tactical Triggers:**

| Action | Condition | ConcernLevel |
|--------|-----------|--------------|
| attack | Outnumbered 5:1+ | EXTREME |
| attack | Outnumbered 3:1+ | STRONG |
| attack | Outnumbered 2:1+ | MODERATE |
| attack | Outnumbered 1.5:1+ | MILD |
| attack | Attacking fortified target | +1 level |
| move | Path crosses enemy region | MODERATE |
| aggressive stance | Enemy adjacent | MILD |

**Implementation:**

```python
def evaluate_cautious(marshal, action, order, game_state) -> ConcernLevel:
    if action == "attack":
        ratio = _get_enemy_to_friendly_ratio(marshal, game_state)
        if ratio >= 5.0:     return ConcernLevel.EXTREME
        if ratio >= 3.0:     return ConcernLevel.STRONG
        if ratio >= 2.0:     return ConcernLevel.MODERATE
        if ratio >= 1.5:     return ConcernLevel.MILD
        return ConcernLevel.NONE

    if action == "move":
        if _path_crosses_enemy(marshal, game_state):
            return ConcernLevel.MODERATE
        return ConcernLevel.NONE

    if action == "stance_change" and _check_enemy_adjacent(marshal, game_state):
        return ConcernLevel.MILD  # Aggressive stance with enemy near

    return ConcernLevel.NONE
```

### 3.3 Literal Personality (Grouchy)

Always returns `ConcernLevel.NONE`. Uses clarification system, not objection system.

### 3.4 Balanced Personality (Future)

Not implemented in V2a. No current marshals use this type.

| Action | Condition | ConcernLevel |
|--------|-----------|--------------|
| attack | Outnumbered 3:1+ | STRONG |
| attack | Outnumbered 5:1+ | EXTREME |
| move | Exposes capital | MODERATE |

### 3.5 Loyal Personality (Future)

Not implemented in V2a. No current marshals use this type.

| Action | Condition | ConcernLevel |
|--------|-----------|--------------|
| attack | Outnumbered 5:1+ | MODERATE |
| attack | Outnumbered 10:1+ | STRONG |

### 3.6 Personality Evaluator Dispatch

```python
PERSONALITY_EVALUATORS = {
    "aggressive": evaluate_aggressive,
    "cautious": evaluate_cautious,
    "literal": lambda m, a, o, gs: ConcernLevel.NONE,  # Bypass
}

def evaluate_situation(marshal, action, order, game_state) -> ConcernLevel:
    evaluator = PERSONALITY_EVALUATORS.get(marshal.personality.lower())
    if evaluator is None:
        return ConcernLevel.NONE  # Unknown personality = no objection (safe default)
    return evaluator(marshal, action, order, game_state)
```

---

## 4. Strategic Triggers

`check_strategic_objection()` and `calculate_strategic_severity()` are REPLACED by ConcernLevel functions. Same pipeline, different trigger entries.

### 4.1 Strategic Aggressive

```python
def evaluate_strategic_aggressive(marshal, order_type, target, path, game_state) -> ConcernLevel:
    """
    Aggressive marshal strategic concerns.

    Args:
        marshal: The marshal receiving the order
        order_type: "HOLD", "PURSUE", "MOVE_TO", "SUPPORT"
        target: Target region name or marshal name
        path: List of regions to traverse (may be empty for HOLD)
        game_state: Full game state dict {"world": WorldState}
    """
    if order_type == "HOLD":
        enemy_adjacent = _check_enemy_adjacent_to_region(target, game_state)
        if not enemy_adjacent:
            return ConcernLevel.MODERATE
        ratio = _get_ratio_at_region(marshal, target, game_state)
        if ratio >= 3.0: return ConcernLevel.EXTREME
        if ratio >= 2.0: return ConcernLevel.STRONG
        return ConcernLevel.MODERATE
    return ConcernLevel.NONE
```

### 4.2 Strategic Cautious

```python
def evaluate_strategic_cautious(marshal, order_type, target, path, game_state) -> ConcernLevel:
    """Cautious marshal strategic concerns."""
    if order_type == "PURSUE":
        ratio = _get_target_strength_ratio(marshal, target, game_state)
        if ratio >= 5.0: return ConcernLevel.EXTREME
        if ratio >= 3.0: return ConcernLevel.STRONG
        if ratio >= 2.0: return ConcernLevel.MODERATE
        if ratio >= 1.5: return ConcernLevel.MILD
        return ConcernLevel.NONE

    if order_type in ("MOVE_TO", "HOLD", "SUPPORT"):
        if _dangerous_path(path, game_state):
            return ConcernLevel.MODERATE
        return ConcernLevel.NONE

    return ConcernLevel.NONE
```

The dangerous path objection (Davout objects to marching through enemy territory) maps to MODERATE. Safe path compromise is still offered at MODERATE+.

### 4.3 Strategic Literal

Always returns `ConcernLevel.NONE`. Uses clarification system.

### 4.4 Strategic Dispatcher

```python
def evaluate_strategic_situation(marshal, order_type, target, path, game_state) -> ConcernLevel:
    # Same dispatch pattern as tactical
    ...
```

### 4.5 Migration

Delete `calculate_strategic_severity()`. Replace `check_strategic_objection()` body with a call to the V2 evaluate functions. Preserve the return dict shape and `pending_strategic_objection` storage field.

---

## 5. Implementation Status

### Units Complete

**Unit 1: Core Data Structures (53 tests)**
File: `backend/commands/objection_v2.py`

- `ConcernLevel` enum: NONE, MILD, MODERATE, STRONG, EXTREME
- `TrustTier` enum: HOSTILE (<30), WARY (30-49), TRUSTING (50-79), DEVOTED (80+)
- `get_trust_tier(trust)` -- Returns TrustTier from trust value
- `calculate_trust_gain(concern, tier)` -- Scaled trust gain when player trusts marshal
- `get_insist_penalty(tier)` -- Trust penalty when player insists
- `get_objection_tone(tier)` -- "defiant", "challenging", "firm", "respectful"
- `apply_mood_variance(concern)` -- 15-20% chance of +/-1 level shift
- `handle_objection_response(response_type, concern, tier)` -- Returns trust change
- Backward compat helpers: `concern_to_legacy_severity()`, `is_popup_concern()`, `is_blocking_concern()`

**Unit 2: Tactical Trigger Evaluators (36 tests)**
File: `backend/commands/objection_v2.py`

- `evaluate_aggressive(marshal, action, order, game_state)` -- MILD to EXTREME by context
- `evaluate_cautious(marshal, action, order, game_state)` -- MILD to EXTREME by odds
- `evaluate_literal(marshal, action, order, game_state)` -- Always NONE
- `evaluate_situation(marshal, action, order, game_state)` -- Main dispatcher

**Unit 3: Strategic Trigger Evaluators (30 tests)**
File: `backend/commands/objection_v2.py`

- `evaluate_strategic_aggressive(marshal, order_type, target, path, game_state)`
- `evaluate_strategic_cautious(marshal, order_type, target, path, game_state)`
- `evaluate_strategic_literal(...)` -- Always NONE
- `evaluate_strategic_situation(...)` -- Main strategic dispatcher

**Unit 4: Pipeline Integration (6 tests)**
Files: `backend/commands/executor.py`, `backend/models/world_state.py`, `backend/main.py`

- Replaced `world.disobedience_system.evaluate_order()` with V2 `evaluate_situation()`
- Added `apply_mood_variance()` call after evaluation
- MILD concerns: append to `world.mild_concerns_this_turn`, continue execution
- MODERATE+: check per-marshal cap, create popup with tone/insist_penalty
- Added `mild_concerns_this_turn: List[Dict]` and `objection_popups_this_turn: Set[str]` to WorldState
- Fields clear at turn start, serialize in `to_dict()`/`from_dict()` with backward compat
- `main.py` passes `mild_concerns` through response dict

**Unit 5: Vindication Extension (2 tests)**
File: `backend/commands/vindication.py`

- Added `pending_defensive_vindication: Dict[str, Dict]` field
- Full `to_dict()` / `from_dict()` serialization
- Backward compatible with old saves (defaults to empty dict)

**Unit 6: Integration Wiring + Test Migration (13 tests) ✓**
Files: `executor.py`, `disobedience.py`, `marshal.py`, `world_state.py`

6 gaps resolved:
- Gap 1 (Doc): Compromise math note for DEVOTED+MODERATE
- Gap 2 (`idle_turns`): New Marshal field — increments per idle turn, resets on attack/move, serialized
- Gap 3 (V2 trust scaling): `calculate_trust_gain()`, `get_insist_penalty()`, `COMPROMISE_TRUST_GAIN` wired into tactical + strategic objection dicts, replacing hard-coded +12/-10/-15/+3
- Gap 4 (Insist bypass): V1 disobedience roll removed from `handle_response()`. Insist always succeeds.
- Gap 5 (V1 evaluate_order shim): Replaced with direct `_generate_alternative()` + `_find_compromise()` calls
- Gap 6 (Strategic V2 wiring): `evaluate_strategic_situation()` + `apply_mood_variance()` replace `check_strategic_objection()`. Per-marshal popup cap, MILD path. V1 retained only for option extraction.

Test migration: 9 V1 tests updated (mock mood variance, relaxed assertions), 1 bugfix test updated. 13 new integration tests (tactical trust/insist/compromise, strategic path, MILD no-popup, idle turns).

**Unit 7: Godot Frontend ✓**
Files: `objection_dialog.gd`, `main.gd`

- Tone-based styling: border color + header text change by tone (respectful=gold, firm=orange, challenging=red, defiant=dark red)
- Trust change previews on tactical buttons: "Trust Davout: fortify (+2 trust)" / "Proceed as Ordered (-5 trust)" / "Compromise: move (+3 trust)"
- V2 fields passthrough in `_show_objection_dialog`: tone, concern_level, trust_gain, insist_penalty, compromise_gain
- MILD "Field Dispatches" section in turn log after enemy phase (warm gold color, atmosphere text)
- Dispatches shown both with and without enemy phase dialog

### V2a Complete

All 7 units implemented. Backend fully wired. Frontend displays tone-based styling and MILD dispatches.

### Test Counts

- V2 tests: 140 (53 + 36 + 30 + 6 + 2 + 13)
- Total project tests: 1216 passed, 3 skipped

### Implementation Order

1. Unit 1: Core Data Structures -- no dependencies ✓
2. Unit 2: Trigger Evaluators -- depends on Unit 1 ✓
3. Unit 3: Strategic Migration -- depends on Unit 2 ✓
4. Unit 4: Pipeline Integration -- depends on Units 1-3 ✓
5. Unit 5: Vindication Extension -- parallel with Unit 4 ✓
6. Unit 6: Integration Wiring + Test Migration -- after Units 4-5 ✓
7. Unit 7: Godot Frontend -- after Unit 6 ✓

**Code review checkpoints:** After Unit 2 ✓, After Unit 4 ✓, After Unit 6 ✓.

---

## 6. Resolved Ambiguities

These answers resolve all remaining implementation questions from the design review.

### Q1: MILD Return Dict Shape

Drop legacy fields, use clean V2 shape:

```python
{
    "type": "mild_concern",
    "concern_level": "MILD",
    "marshal": str,
    "message": str,
    "execute": True,    # Order proceeds
    "popup": False,
}
```

NOT included in MILD: `severity` (no legacy float), `trust_change` (always 0), `personality`, `order`.

### Q2: Strategic Evaluator Function Signatures

Use explicit parameters, NOT `order.target`:

```python
def evaluate_strategic_aggressive(marshal, order_type, target, path, game_state) -> ConcernLevel:
def evaluate_strategic_cautious(marshal, order_type, target, path, game_state) -> ConcernLevel:
```

### Q3: MODERATE+ Backward Compatibility

MODERATE+ return dicts MUST include `pending_objection: True` for executor AP skip logic:

```python
{
    "pending_objection": True,       # CRITICAL for backward compat
    "type": "major_objection",       # Keep exact string for Godot compat
    "concern_level": "MODERATE",     # or STRONG, EXTREME
    "tone": str,
    "insist_penalty": int,
    "marshal": str,
    "personality": str,
    "severity": float,               # DEPRECATED -- mapped from ConcernLevel
    "order": dict,
    "message": str,
    "options": list,
    "suggested_alternative": dict,
    "compromise": dict,
    "popup": True,
}
```

Severity mapping for backward compat:
```python
CONCERN_TO_SEVERITY = {
    ConcernLevel.MODERATE: 0.55,
    ConcernLevel.STRONG: 0.72,
    ConcernLevel.EXTREME: 0.88,
}
```

MILD does NOT include `pending_objection` because it doesn't block execution.

### Q4: Compromise Trust Gain

Flat +3 regardless of tier. Compromise is a "split the difference" option that should not be the optimal path at any trust level.

### Q5: Severity Breakdown Migration

Rewrite `get_severity_breakdown()` to return ConcernLevel-based breakdown:

```python
def get_concern_breakdown(marshal, action, game_state) -> dict:
    concern = evaluate_situation(marshal, action, game_state)
    return {
        "marshal": marshal.name,
        "personality": marshal.personality,
        "action": action,
        "base_concern": concern.name,
        "factors": _get_evaluation_factors(marshal, action, game_state),
        "final_concern": concern.name,
    }
```

The old severity-based breakdown is DELETED.

### Q6: Concern Level in ALL Return Dicts

YES. Every return dict from the V2 system includes `concern_level`:

| Return Type | Has `concern_level` | Value |
|-------------|---------------------|-------|
| MILD | Yes | `"MILD"` |
| MODERATE popup | Yes | `"MODERATE"` |
| STRONG popup | Yes | `"STRONG"` |
| EXTREME popup | Yes | `"EXTREME"` |
| No objection | Yes | `"NONE"` |

### Q7: Marshal Name Case Sensitivity

Keep AS-IS. Marshal names are proper nouns (`"Ney"`, `"Davout"`), stored with consistent capitalization. `marshal.name` is always the canonical form. No case normalization needed.

---

## 7. Key Design Decisions

> **These decisions are LOCKED. Not suggestions. Not open questions.**

| Decision | Rationale |
|----------|-----------|
| Split V2a/V2b | Lower risk, fix core problem first. V2b deferred to Phase 7. |
| Deterministic triggers + mood variance | Predictable base = testable = debuggable. Small 15-20% variance for human feel. |
| MILD as end-of-turn flavor only | Reduces popup fatigue, feels like war dispatches |
| Grouchy clarification separate | Preserves "never objects" personality. Grouchy NEVER defies, even in V2b. |
| No feature flag | Git history is rollback. No parallel system maintenance. Replace directly. |
| Trust affects consequences only | Core design fix -- the whole point of V2 |
| Atomic migration (tactical + strategic) | They share `calculate_objection_severity()` and `DisobedienceSystem.evaluate_order()` -- you can't split them. |
| Preserve return dict shape | Minimizes test breakage. Add new fields, don't remove old ones (except in MILD). |
| Vindication in VindicationTracker | Keep Marshal model clean |
| Defiance hard cap 40% (V2b) | Prevent degenerate spirals |
| Per-marshal popup cap only | Global cap is exploitable. Per-marshal (max 1 per turn) is sufficient. |
| Authority inert in V2a | V2b gives it purpose. Do not add placeholder effects. |
| Compliance chance hidden in V2a | Insist always works in V2a. Showing a percentage that always succeeds is a lie. V2a bypasses disobedience roll (`calculate_obedience_chance()` preserved for V2b defiance mechanic). |
| Skip Balanced/Loyal triggers | No current marshals use these types. Build when they ship. |
| 1.5:1 cautious attack = MILD (not popup) | Intentional. 1.5:1 is not dangerous enough for a popup. Old behavior was too aggressive. |
| Trust floor: 5 | Trust can never drop below 5. Existing redemption systems handle low-trust recovery. |

