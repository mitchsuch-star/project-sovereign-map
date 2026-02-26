# V2b: Defiance / Vindication / Authority — Implementation Spec

> **Status:** DESIGN LOCKED. Ready for implementation.
> **Prerequisite:** V2a complete (1216 tests). All scaffolding in place.
> **Model:** Sonnet — patterns clear from V2a, well-specified, mostly wiring.
> **Estimated:** 2 sessions (1: mechanics, 2: fog + triggers + polish).

---

## Design Philosophy

"Disobedience as negotiation, not RNG." V2a fixed the original flaw where trust suppressed objections (high-trust marshals went silent). Now: situation determines IF a marshal speaks, trust determines HOW they speak. V2b adds the final layer: marshals can occasionally ACT on their objections.

---

## 1. Defiance Mechanic

### When It Fires

Defiance is a post-insist event. The player sees an objection popup, chooses "Insist" (proceed), and THEN the defiance roll occurs. The flow:

```
Objection popup → Player clicks "Insist" → Defiance roll
  → If succeeds: "Despite your insistence, Ney charges anyway!"
  → If fails: "Ney's hand trembles... but discipline holds."
```

Defiance ONLY fires on STRONG (`ConcernLevel.STRONG = 3`) or EXTREME (`ConcernLevel.EXTREME = 4`). MILD and MODERATE never trigger defiance.

### Defiance Chance Formula

```python
def calculate_defiance_chance(marshal, concern_level, world):
    """Calculate probability of marshal defying a direct order.

    Only fires on STRONG/EXTREME concerns after player insists.
    Returns 0.0-0.40 (hard-capped).
    """
    if concern_level < ConcernLevel.STRONG:
        return 0.0

    # Cooldown check
    if world.current_turn < marshal.defiance_cooldown_until:
        return 0.0

    # Literal personality never defies (Grouchy bypass)
    if marshal.personality_type == PersonalityType.LITERAL:
        return 0.0

    # Base chances
    if concern_level == ConcernLevel.STRONG:
        base = 0.15  # 15%
    else:  # EXTREME
        base = 0.35  # 35%

    # Vindication modifier: +10% per stack (marshal.vindication_score, range -5 to +5)
    vindication_mod = marshal.vindication_score * 0.10

    # Authority modifier (simpler tiers than AuthorityTracker methods)
    # Uses world.authority_tracker.authority (int, 0-100)
    authority = world.authority_tracker.authority
    if authority >= 80:
        authority_mod = -0.10  # Strong leader suppresses defiance
    elif authority < 50:
        authority_mod = +0.10  # Weak leader emboldens defiance
    else:
        authority_mod = 0.0

    # Trust tier modifier (narrower thresholds than V2a's TrustTier enum)
    # V2a TrustTier.HOSTILE = trust < 30. Defiance uses ≤20 for tighter range.
    # V2a TrustTier.DEVOTED = trust >= 80. Defiance matches.
    trust = marshal.trust.value
    if trust <= 20:
        trust_mod = +0.15
    elif trust >= 80:
        trust_mod = -0.10
    else:
        trust_mod = 0.0

    # Variance band: prevents memorized thresholds
    variance = random.uniform(-0.08, 0.08)

    # Hard cap at 40%
    final = base + vindication_mod + authority_mod + trust_mod + variance
    return min(0.40, max(0.0, final))
```

### Defiance Action — Fallback Table

Marshals only defy orders they'd object to. Half the cells are naturally empty.

| Personality | Defying Defend/Fortify/Hold/Wait | Defying Attack | Defying Retreat | Defying SUPPORT | Defying MOVE_TO |
|---|---|---|---|---|---|
| **Aggressive** | Attack nearest enemy | — (wouldn't object) | Attack (stay and fight) | Attack nearest enemy | Attack nearest enemy |
| **Cautious** | — (wouldn't object) | Fortify (dig in) | — (wouldn't object) | Fortify | Fortify |
| **Literal** | — (never defies) | — (never defies) | — (never defies) | — (never defies) | — (never defies) |

**Aggressive defiance targeting:** Uses `_execute_auto_assign_attack()` targeting logic (finds nearest enemy marshal, no named target required).

**If preferred action is blocked** (no enemy to attack, already fortified, etc.): fallback = `wait` (sulk). Still costs AP. Defiance outcome = inconclusive (no vindication change, no authority change, just cooldown).

**AP cost:** Original action's AP cost is charged. Already pre-checked before objection fired (executor.py bypass hierarchy runs AP check at step 13, objection at step 14).

### Defiance Success Definition

```python
def defiance_succeeded(marshal, defiance_action, battle_result, pre_battle_strength):
    """Determine if a marshal's defiant action proved correct.

    Returns True if the marshal's unauthorized action had a good outcome.
    Used to determine vindication/authority/trust changes.
    """
    if defiance_action == "attack":
        won = battle_result["attacker"]["won"]
        casualties = battle_result["attacker"]["casualties"]
        casualty_pct = casualties / pre_battle_strength if pre_battle_strength > 0 else 1.0
        return won and casualty_pct < 0.50  # Won AND not pyrrhic
    elif defiance_action in ("defend", "fortify", "wait"):
        return not marshal.is_broken and not marshal.is_retreating
    elif defiance_action == "retreat":
        return marshal.strength > 0  # Survived
    else:
        return False  # Sulking/wait-fallback = inconclusive, never vindicated
```

### Defiance Outcome Table

| Outcome | Trust | Vindication | Authority | Cooldown |
|---------|-------|-------------|-----------|----------|
| Defiance succeeds, marshal **RIGHT** | +2 | +1 | -5 | 3 turns |
| Defiance succeeds, marshal **WRONG** | -5 | Reset to 0 | +3 | 3 turns |
| Roll **fails**, marshal obeys | -3 | Reset to 0 | No change | 1 turn |

**Cooldown:** Set `marshal.defiance_cooldown_until = world.current_turn + N` (N=3 for success, N=1 for failed roll).

---

## 2. Vindication System

### Vindication Score

Per-marshal integer. Existing field: `marshal.vindication_score` (range -5 to +5, clamped in `vindication.py:173-177`).

- +1 on successful defiance where marshal was right
- Reset to 0 on failed defiance (marshal wrong) or failed roll (marshal backed down)
- Each stack adds +10% to future defiance chance (at +3 the modifier already hits 40% cap in most configs)

### Vindication Decay

**-1 per 3 turns of no objection activity** from that marshal.

New field: `marshal.last_objection_turn` (int, default 0). Updated whenever an objection fires for this marshal (any concern level, including MILD).

Decay check runs during `advance_turn()` in `world_state.py`. **Symmetric:** both positive and negative scores decay toward 0.

```python
# In _process_tactical_states() or dedicated _process_vindication_decay()
for marshal in self.marshals.values():
    if marshal.nation == self.player_nation and marshal.strength > 0:
        turns_idle = self.current_turn - marshal.last_objection_turn
        if turns_idle >= 3 and marshal.vindication_score != 0:
            if marshal.vindication_score > 0:
                marshal.vindication_score -= 1  # Proven-right fades
            else:
                marshal.vindication_score += 1  # Proven-wrong also fades
            # Reset timer so next decay is 3 turns from now
            marshal.last_objection_turn = self.current_turn
```

### Vindication Escalation / De-escalation

Vindication stacks shift a concern by ±1 level (max one step):

**Positive vindication (marshal proven right) → escalation:**
- MILD → MODERATE: yes
- MODERATE → STRONG: yes
- MILD → STRONG: **never** (single step only)
- MODERATE → EXTREME: **never** (single step only)

**Negative vindication (marshal proven wrong) → de-escalation ("boy who cried wolf"):**
- MODERATE → MILD: yes
- STRONG → MODERATE: yes (removes defiance eligibility)
- EXTREME → STRONG: yes
- MILD → NONE: **never** (even a discredited marshal still gets to grumble)

**Ordering:** `base trigger → vindication shift (+1 or -1 max) → mood variance (±1)`.

Maximum possible escalation from base = +2 levels (vindication +1, then mood +1). MILD can reach STRONG (vindication → MODERATE, mood → STRONG). MODERATE can reach EXTREME (vindication → STRONG, mood → EXTREME). These are rare compound events — correct behavior.

Maximum possible de-escalation from base = -2 levels (vindication -1, then mood -1). STRONG can drop to MILD. EXTREME can drop to MODERATE.

**Trigger condition:** `marshal.vindication_score > 0` enables escalation. `marshal.vindication_score < 0` enables de-escalation. Score of 0 = no shift.

### Defensive Vindication

Existing scaffolding: `VindicationTracker.pending_defensive_vindication` (dict, serialized, currently unwired).

Wire into `turn_manager.py` enemy phase: when enemy attacks a marshal with pending defensive vindication and that marshal holds → vindication +1. If marshal loses → vindication -1. If no attack → cleared after 1 turn (stale).

---

## 3. Authority System

### Overview

Global stat per player. Existing class: `AuthorityTracker` in `backend/models/authority.py`. Field: `authority_tracker.authority` (int, 0-100, starts at 100).

**Authority tiers for defiance:**

| Range | Label | Defiance Modifier |
|-------|-------|-------------------|
| ≥80 | Strong leader | -10% |
| 50-79 | Normal | 0% |
| <50 | Weak leader | +10% |

**Note:** These tiers are SEPARATE from `AuthorityTracker`'s existing methods (`get_obedience_modifier`, `get_severity_modifier`, `get_trust_gain_modifier`). The existing methods continue to serve their V2a purposes (trust gain scaling, future severity scaling). The defiance formula uses the simpler tier system above. Two systems, two purposes — comment the distinction in code.

### Authority Changes

| Event | Authority Change | Hook Point |
|-------|-----------------|------------|
| Defiance succeeds, marshal right | -5 | Post-defiance resolution |
| Defiance succeeds, marshal wrong | +3 | Post-defiance resolution |
| Major victory | +5 | `executor.py` after `resolve_battle()` |
| Major defeat | -5 | `executor.py` after `resolve_battle()` |
| Excessive trusting | -2 or -3 | `authority_tracker.record_response()` |

**Major victory definition:** Won battle while outnumbered (pre-battle attacker strength < defender strength) OR captured an enemy capital region.

**Major defeat definition:** Lost battle while outnumbering enemy (pre-battle attacker strength > defender strength) OR lost a capital region.

**Hook timing:** Authority check runs in `executor.py` after advance-after-win logic (not immediately after `resolve_battle()`), so territory capture is visible when evaluating "major victory." The battle_result dict + region controller change are both available at this point.

**Authority clamped 0-100.** Enforce in `AuthorityTracker` when modifying.

### Excessive Trust Penalty — Ratio-Based

Track trust/insist/compromise responses with turn numbers. Penalty fires based on trust RATIO, not count.

**Enriched `recent_responses` format:**

```python
# Current (V2a): ["trust", "insist", "compromise"]
# V2b:           [{"choice": "trust", "turn": 5}, {"choice": "insist", "turn": 6}, ...]
```

**Migration:** `from_dict` treats bare strings as legacy format (assign turn 0). No save-breaking.

**Penalty calculation:**

```python
def check_excessive_trust(authority_tracker, current_turn):
    """Check if player is trusting too often (pushover behavior).

    Returns authority penalty (0, -2, or -3).
    Called after each objection response via record_response().
    """
    recent = [r for r in authority_tracker.recent_responses
              if r["turn"] >= current_turn - 10]

    total = len(recent)
    if total < 3:  # Not enough data to judge
        return 0

    trust_count = sum(1 for r in recent if r["choice"] == "trust")
    ratio = trust_count / total

    if ratio > 0.80:    # 80%+ = egregious pushover
        return -3
    elif ratio > 0.65:  # 65%+ = concerning pattern
        return -2
    else:
        return 0
```

**Why ratio-based:** Scales naturally to any roster size (5 marshals or 20). A global count threshold breaks at 1805 scale.

---

## 4. Fog-of-War Helper Migration

Switch 8+ helpers in `objection_v2.py` from raw `world.marshals` access to fog-filtered data via `get_visible_enemies_near()` / `world.get_intel()`.

| Helper Function | Current Behavior | V2b Change |
|-----------------|-----------------|------------|
| `_check_enemy_adjacent()` | Raw world data | `get_visible_enemies_near()` (PARTIAL+ visibility) |
| `_get_friendly_to_enemy_ratio()` | Raw counts | Fog-filtered counts, strength bands at PARTIAL |
| `_get_enemy_to_friendly_ratio()` | Raw counts | Fog-filtered counts |
| `_is_actually_threatened()` | Raw enemy check | Visible enemies only |
| `_is_outnumbered_2to1()` | Raw counts | Fog-filtered |
| `_path_crosses_enemy()` | Raw region check | Fog-filtered region check |
| `_path_has_enemies()` (strategic) | Raw path check | Fog-aware path danger check |
| `_get_attack_odds_ratio()` | Raw strength | Strength bands at PARTIAL, exact at FULL |
| `_check_attack_target_fortified()` | Raw fort check | Fortification visible at FULL only |

### New Fog-Specific Objection Triggers

| Situation | Cautious | Aggressive | Literal |
|-----------|----------|------------|---------|
| Attack into UNKNOWN region | MODERATE→STRONG | No concern | Follows orders |
| Attack on STALE intel (3+ turns old) | MODERATE | MILD at most | Follows orders |
| Refuse attack when scout shows weakness | No concern | MODERATE→STRONG | No concern |
| PURSUE with no intel on target | STRONG | MILD | Depends on order clarity |

These integrate into the existing `evaluate_cautious_*` and `evaluate_aggressive_*` functions as additional checks.

---

## 5. Relationship-Based SUPPORT Objection

### Gap Filled

Current SUPPORT objections are personality-based only. No relationship-based check exists. A hostile marshal ordered to SUPPORT their enemy never gets a chance to object at issuance.

### New Trigger

| Personality | Target Relationship | ConcernLevel | Message Template |
|---|---|---|---|
| Aggressive | Hostile (-2) | **STRONG** | "You ask me to bleed for {target}? That man would see me destroyed!" |
| Cautious | Hostile (-2) | **MODERATE** | "Supporting {target}... I have reservations, but I will comply." |
| Literal | Hostile (-2) | **NONE** | Follows orders regardless |
| Any | Rival (-1) | **MILD** | Grumble only, no popup |

### Integration

Fires at **order issuance** via `evaluate_strategic_situation()` → `pending_strategic_objection` (not `pending_objection`). Relationship check runs BEFORE personality-specific evaluation (relationship concern takes priority if higher than personality concern).

### Player Choices (STRONG — Aggressive + Hostile)

| Choice | Effect |
|--------|--------|
| **Insist** | SUPPORT order executes. Trust penalty per CONSEQUENCE_TABLE (HOSTILE tier = -15). Defiance can fire (15% base + mods). |
| **Trust** | Order cancelled, AP refunded. Trust +5/+8 (STRONG gain). Marshal stays put. |
| **Compromise** | Timed SUPPORT — 3 turns then auto-cancels. Trust +3. Implementation: set `order.cancel_after_turn = current_turn + 3`, check in `strategic.py` per-turn execution (matches existing timed HOLD pattern from Phase M). |

### Defiance Interaction

If aggressive marshal's concern reaches STRONG (hostile target) and player insists, defiance can fire. Defiant action per fallback table: attack nearest enemy instead of supporting.

### SUPPORT Order Lifecycle (Reference)

SUPPORT orders **persist indefinitely by default**. They clear via:

| Trigger | Type | File |
|---------|------|------|
| Ally reached + ally safe (no adjacent enemies) | Auto-complete | `strategic.py` |
| Ally wins battle (if `until_battle_won` condition set) | Auto-complete | `strategic.py` |
| Ally destroyed | Auto-break | `strategic.py` |
| Marshal reinforces into battle | Auto-clear | `executor.py` |
| Player overrides with another action | Manual | `executor.py` |
| Player cancels (cancel/halt/stop/abort) | Manual | `executor.py` |
| Forced retreat | Auto-clear | `executor.py` |
| Form square | Manual | `executor.py` |
| Path permanently blocked | Auto-break | `executor.py` |

The timed SUPPORT compromise (3-turn auto-cancel) adds a 10th path via `order.cancel_after_turn`.

### Forced SUPPORT Consequences

No additional penalty beyond existing systems:
- V2a insist penalty: -15 trust at HOSTILE tier (already the harshest in the game)
- D3 rule: Hostile+SUPPORT = 0% coordination (existing Phase 7 Core behavior)
- Casualty participation: marshal takes proportional casualties (existing Phase 7b behavior)

If hostile marshal takes >30% casualties while on forced SUPPORT: campaign log narrative entry only, no mechanical effect. Berthier observation material.

---

## 6. Notifications and Logging

### Notification Type

Add to `backend/notifications.py`:

```python
MARSHAL_DEFIED_ORDER = "marshal_defied_order"  # HIGH priority
```

Template: `"{marshal} defied your order to {action}!"`

### Campaign Log Event

Add `"defiance"` to the event type whitelist in `backend/campaign_log.py`.

One-liner format: `"Turn {turn}: {marshal} defied orders and {defiance_action} instead."`

### Berthier Flavor Text (6 minimum)

**Defiance success, marshal right (2 variants):**
- "Despite your express command, {marshal} {action}... and proved the wiser for it."
- "Your orders went unheeded by {marshal}. The outcome suggests they knew something you did not."

**Defiance success, marshal wrong (2 variants):**
- "{marshal} defied your authority and {action}. The results speak for themselves — poorly."
- "Acting against your express command, {marshal} {action}. It did not go well."

**Failed roll, complied reluctantly (2 variants):**
- "{marshal}'s hand trembled on the hilt, but discipline held... barely."
- "For a moment, {marshal} hesitated — then obeyed. The tension in the air was palpable."

---

## 7. Serialization Requirements

### New Fields on Marshal

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `last_objection_turn` | `int` | `0` | Vindication decay timer |
| `defiance_cooldown_until` | `int` | `0` | Cooldown: turn when defiance is available again |

Standard pattern:
- Add to `__init__` in `marshal.py`
- Add to `to_dict()`: `"last_objection_turn": int(self.last_objection_turn)`
- Add to `from_dict()`: `marshal.last_objection_turn = data.get("last_objection_turn", 0)`
- Run: `pytest tests/test_serialization_enforcement.py -v`
- Update: `docs/SAVE_FORMAT_REFERENCE.md`

### Modified Fields on AuthorityTracker

`recent_responses` format changes from `List[str]` to `List[Dict]`:

```python
# to_dict() — already serialized, format changes
"recent_responses": [r if isinstance(r, dict) else {"choice": r, "turn": 0}
                     for r in self.recent_responses]

# from_dict() — backward compatible
raw = data.get("recent_responses", [])
self.recent_responses = [
    r if isinstance(r, dict) else {"choice": r, "turn": 0}
    for r in raw
]
```

### Existing Fields (No Changes Needed)

- `marshal.vindication_score` — already serialized (range -5 to +5)
- `world_state.authority_tracker` — already serialized via `AuthorityTracker.to_dict()`
- `world_state.vindication_tracker` — already serialized via `VindicationTracker.to_dict()`
- `world_state.pending_objection` / `pending_strategic_objection` — already serialized

---

## 8. Existing System Interactions

### V1 Popup Cap

Rename `MAX_MAJOR_OBJECTIONS_PER_TURN` → `MAX_OBJECTION_POPUPS_PER_TURN` in `disobedience.py`. Keep value at **2**. This is the ultimate cascade breaker — do NOT remove it. MILD concerns (flavor text, no popup) remain uncapped.

### Bypass Hierarchy (executor.py)

Defiance fires AFTER the existing bypass hierarchy. The player has already passed all validation checks (AP, broken state, fortified, etc.) and the objection was evaluated. Defiance is purely a post-insist event within `_execute_post_objection()`.

```
Steps 1-13: Pre-validation (autonomous, strategic override, drilling,
            fortified, retreat, broken, AP check, etc.)
Step 14:    Objection evaluation (V2a: ConcernLevel)
Step 14b:   Vindication escalation (+1 max if vindication_score > 0)  [NEW]
Step 14c:   Mood variance (±1, existing)
Step 15:    Popup shown to player (MODERATE+)
Step 16:    Player response (insist/trust/compromise)
Step 17:    If insist + STRONG/EXTREME: defiance roll  [NEW]
Step 18:    Execute original order or defiant action
```

### Strategic Orders

- Defiance fires on **order issuance** only (when the strategic command is given)
- `_strategic_execution = True` flag bypasses objections during per-turn execution — no mid-execution defiance
- If marshal defies a SUPPORT order, the SUPPORT is never registered; marshal does fallback action instead
- If marshal defies a MOVE_TO order, the MOVE_TO is never registered; marshal does fallback action instead

### Coordination Impact

If marshal A defies and attacks instead of supporting marshal B:
- Marshal B loses expected coordination bonus (SUPPORT not registered)
- Combat proceeds with fewer participants in `_calculate_coordination_context()`
- This is the intended design — defiance has tactical consequences

### Square Formation

If a marshal in square formation triggers an objection and defies:
- Aggressive defiance action = attack → auto-breaks square (existing auto-break rule)
- The defiant attack proceeds normally after square breaks

---

## 9. Implementation Plan

### Session 1: Core Mechanics

1. **New marshal fields:** `last_objection_turn`, `defiance_cooldown_until` + serialization
2. **`calculate_defiance_chance()`** — new function in `objection_v2.py` or new `defiance.py`
3. **Defiance roll** — wire into `_execute_post_objection()` in `executor.py` after "insist" response
4. **Defiant action execution** — fallback table lookup, execute via existing `_execute_*` methods
5. **`defiance_succeeded()`** — outcome evaluation after defiant action resolves
6. **Outcome application** — trust/vindication/authority changes per outcome table
7. **Vindication escalation** — insert between base trigger and mood variance in `evaluate_situation()`
8. **Vindication decay** — add to `advance_turn()` in `world_state.py`
9. **Defensive vindication wiring** — connect `pending_defensive_vindication` in `turn_manager.py`
10. **Authority major victory/defeat** — hook in `executor.py` after `resolve_battle()`
11. **Excessive trust penalty** — ratio-based check in `AuthorityTracker.record_response()`
12. **`recent_responses` format migration** — enrich with turn numbers, backward-compatible deserialize
13. **Rename V1 cap** — `MAX_MAJOR_OBJECTIONS_PER_TURN` → `MAX_OBJECTION_POPUPS_PER_TURN`
14. **Notification** — add `MARSHAL_DEFIED_ORDER` type
15. **Campaign log** — add `"defiance"` event type
16. **Berthier flavor text** — 6 templates
17. **Serialization enforcement** — run `test_serialization_enforcement.py`

### Session 2: Fog Migration + Triggers + Polish

1. **Fog helper migration** — 8+ functions in `objection_v2.py`
2. **New fog-specific triggers** — 4 situations per personality
3. **Relationship-based SUPPORT objection** — new trigger in `evaluate_strategic_situation()`
4. **Compromise: timed SUPPORT** — 3-turn auto-cancel variant
5. **`main.py` passthrough** — defiance result fields in POST /command response
6. **Godot integration** — defiance message display in `main.gd`
7. **Full test suite**
8. **Doc updates** — STATUS.md, SYSTEMS_REFERENCE.md, SAVE_FORMAT_REFERENCE.md, CLAUDE.md

### Code Review Checkpoint

After Session 1, before fog migration. Fog changes are highest-risk (8+ function modifications in a 1390-line file). Review Session 1's test coverage and defiance flow before proceeding.

---

## 10. Test Plan Outline

### Defiance Mechanics (~30 tests)

- `calculate_defiance_chance`: base rates for STRONG/EXTREME
- Hard cap at 40% with max modifiers
- Returns 0.0 for MILD/MODERATE
- Grouchy (literal) always returns 0.0
- Cooldown blocks defiance
- Vindication modifier (+10% per stack)
- Authority modifier (-10%/0%/+10%)
- Trust tier modifier (+15%/0%/-10%)
- Authority clamped 0-100

### Defiance Actions (~15 tests)

- Aggressive fallback table (defend→attack, retreat→attack, SUPPORT→attack, MOVE_TO→attack)
- Cautious fallback table (attack→fortify, SUPPORT→fortify, MOVE_TO→fortify)
- Blocked preferred action → wait (sulk)
- AP charged from original action

### Defiance Outcomes (~20 tests)

- Success + right: trust +2, vindication +1, authority -5, 3-turn cooldown
- Success + wrong: trust -5, vindication reset, authority +3, 3-turn cooldown
- Failed roll: trust -3, vindication reset, no authority change, 1-turn cooldown
- Pyrrhic victory (>50% casualties) = not vindicated
- Defend/fortify success = not broken and not retreating
- Retreat success = survived (strength > 0)
- Sulk/wait = inconclusive (no vindication change)

### Vindication (~20 tests)

- Positive decay: -1 per 3 idle turns toward 0
- Negative decay: +1 per 3 idle turns toward 0 (symmetric)
- Decay timer resets on any objection
- Escalation: MILD→MODERATE with positive vindication
- Escalation: MODERATE→STRONG with positive vindication
- No double-step escalation (MILD cannot reach STRONG via vindication alone)
- De-escalation: MODERATE→MILD with negative vindication ("boy who cried wolf")
- De-escalation: STRONG→MODERATE with negative vindication (removes defiance eligibility)
- MILD never drops to NONE (floor)
- Ordering: vindication shift before mood variance
- Defensive vindication wiring (hold = +1, lose = -1, no attack = cleared)

### Authority (~15 tests)

- Major victory: +5 (outnumbered win or capital capture)
- Major defeat: -5 (outnumbering loss or capital loss)
- Excessive trust ratio >0.65 in 10 turns: -2
- Excessive trust ratio >0.80 in 10 turns: -3
- Minimum 3 responses before penalty fires
- Authority clamp 0-100
- `recent_responses` format migration (bare strings → dicts)

### Relationship SUPPORT Objection (~10 tests)

- Aggressive + hostile target → STRONG
- Cautious + hostile target → MODERATE
- Literal + hostile target → NONE
- Any + rival target → MILD
- Relationship check runs before personality evaluation
- Compromise: timed 3-turn SUPPORT
- Defiance from hostile SUPPORT → attack instead

### Fog Migration (~20 tests)

- Each migrated helper returns fog-filtered results
- Attack into UNKNOWN: cautious MODERATE→STRONG, aggressive no concern
- Attack on STALE intel: cautious MODERATE
- PURSUE with no intel: cautious STRONG
- Strength bands used at PARTIAL visibility, exact at FULL

### Integration (~10 tests)

- Full defiance flow: objection → insist → defiance roll → defiant action → outcome
- Defiance + strategic order cancellation
- Defiance + coordination disruption
- Defiance + square formation auto-break
- Serialization round-trip with all new fields
- Notification fires on defiance
- Campaign log entry on defiance

**Estimated total: ~140 tests across 2 sessions.**

---

## Appendix A: Existing Scaffolding Reference

| Component | File | Status |
|-----------|------|--------|
| `ConcernLevel` enum | `objection_v2.py:33-47` | Production (V2a) |
| `TrustTier` enum | `objection_v2.py:50-62` | Production (V2a) |
| `CONSEQUENCE_TABLE` | `objection_v2.py:72-114` | Production (V2a) |
| `AuthorityTracker` class | `authority.py` | Wired for trust gain modifier, severity modifier |
| `VindicationTracker` class | `vindication.py` | Wired for choice recording + battle resolution |
| `vindication_score` field | `marshal.py:281` | Serialized, range -5 to +5 |
| `pending_defensive_vindication` | `vindication.py:38` | Serialized, **unwired** (TODO V2b) |
| `pending_objection` field | `world_state.py:188` | Serialized, production |
| `pending_strategic_objection` field | `world_state.py:190` | Serialized, production |
| `MAX_MAJOR_OBJECTIONS_PER_TURN` | `disobedience.py:25` | Value 2, rename to `MAX_OBJECTION_POPUPS_PER_TURN` |
| `mood_variance()` | `objection_v2.py:242-280` | Production, ±1 level (10% up, 15% down) |
| `objection_resolved` field | `StrategicOrder` in `marshal.py` | Exists, not yet wired |

## Appendix B: Files Modified by V2b

| File | Scope | Risk |
|------|-------|------|
| `objection_v2.py` | 8 fog helpers + vindication escalation + relationship trigger | **HIGH** (1390 lines, core objection logic) |
| `executor.py` | Post-objection defiance flow + authority hooks | MEDIUM (large file, well-structured insertion points) |
| `world_state.py` | Vindication decay in advance_turn | LOW (small addition) |
| `turn_manager.py` | Defensive vindication wiring | LOW (small addition) |
| `marshal.py` | 2 new int fields + serialization | LOW (standard pattern) |
| `authority.py` | Authority clamp + enriched recent_responses + excessive trust check | LOW-MEDIUM |
| `vindication.py` | Remove TODOs (logic moves to world_state/turn_manager) | LOW |
| `disobedience.py` | Rename constant | LOW |
| `notifications.py` | 1 new notification type | LOW |
| `campaign_log.py` | 1 new event type in whitelist | LOW |
| `main.py` | Passthrough defiance result fields | LOW |
| `main.gd` | Display defiance messages | LOW (frontend) |

## Appendix C: Decision Rationale Log

| Decision | Options Considered | Chosen | Rationale |
|----------|-------------------|--------|-----------|
| Hard cap | 30%, 40%, 50% | **40%** | Prevents cascade while allowing dramatic moments |
| Failed roll trust | -5, -3, 0 | **-3** | Gradient: reluctant obey (-3) < defy+fail (-5) < defy+right (+2) |
| Failed roll cooldown | 0, 1, 3 turns | **1 turn** | Prevents grinding while preserving "didn't act" distinction |
| Success cooldown | 1, 3, 5 turns | **3 turns** | Prevents same-marshal defiance spam |
| Pyrrhic check | None, 50% own casualties, 30% | **50%** | Clean threshold — destroyed your army ≠ vindication |
| Trust penalty model | Count-based, per-marshal, ratio-based | **Ratio-based** | Scales to any roster size; >65% = -2, >80% = -3 |
| Trust penalty window | 5, 10, 15 turns | **10 turns** | Short enough to reward change, long enough to detect patterns |
| Hostile SUPPORT (aggressive) | MODERATE, STRONG | **STRONG** | Historical resonance (Bernadotte at Jena). Defiance can fire. |
| Hostile SUPPORT (cautious) | MILD, MODERATE, STRONG | **MODERATE** | Professional reluctance, no defiance risk. Personality distinction. |
| Cooperation floor | Hard block at trust 0, no floor | **No floor** | Soft costs self-regulate; hard floor removes agency in desperate situations |
| Escalation ordering | Mood→vindication, vindication→mood | **Vindication→mood** | Rare compound events (MODERATE→EXTREME) are correct behavior |
| Authority bounds | Unbounded, 0-100, 0-150 | **0-100** | Simple, clean, starting value is ceiling |
| Defiance AP cost | Defiant action's cost, original action's cost | **Original action's cost** | Player budgeted for it; already pre-checked |
| Negative vindication decay | No decay, symmetric decay | **Symmetric** | Marshal proven wrong 15 turns ago shouldn't carry that forever |
| Negative vindication de-escalation | No effect, symmetric de-escalation | **Symmetric ("boy who cried wolf")** | Discredited marshal's concerns carry less weight. MILD floors at MILD. |
| Timed SUPPORT implementation | New `turns_remaining` field, `cancel_after_turn` check | **`cancel_after_turn`** | Matches existing timed HOLD pattern from Phase M. No new fields. |
| Defiant attack targeting | Named target required, auto-assign | **Auto-assign** | Uses existing `_execute_auto_assign_attack()`. No named target needed. |
