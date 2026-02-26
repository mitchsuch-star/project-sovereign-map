# V2b: Defiance / Vindication / Authority — Implementation Spec

> **Status:** COMPLETE. All 4 sessions shipped (0-3) + audit pass 2. 4165 tests passing. All confidence gates 100%.
> **Prerequisite:** V2a complete (1216 tests). All scaffolding in place.
> **Model:** Sonnet — patterns clear from V2a, well-specified, mostly wiring.
> **Delivered:** 4 sessions (0: prerequisite fix, 1: core mechanics, 2: fog migration, 3: frontend + UI tests).
> **Confidence protocol:** Each session ends with a confidence report. All 4 sessions reached 100%.

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

Defiance fires on MODERATE (`ConcernLevel.MODERATE = 2`), STRONG (`ConcernLevel.STRONG = 3`), or EXTREME (`ConcernLevel.EXTREME = 4`). MILD never triggers defiance. MODERATE has a low 5% base to add tension to every override without making defiance routine.

### Defiance Chance Formula

```python
def calculate_defiance_chance(marshal, concern_level, world):
    """Calculate probability of marshal defying a direct order.

    Fires on MODERATE/STRONG/EXTREME concerns after player insists.
    Returns 0.0-0.40 (hard-capped).
    """
    if concern_level < ConcernLevel.MODERATE:
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

**Aggressive defiance targeting:** Uses `world.find_nearest_enemy()` to resolve target, then calls `_execute_attack()` with the nearest enemy name. **Exception:** If defiant marshal has `artillery=True`, uses bombardment instead (artillery can't melee attack). If no enemy found or attack fails, falls back to `wait` (sulk).

**If preferred action is blocked** (no enemy to attack, already fortified, etc.): fallback = `wait` (sulk). Still costs AP. Defiance outcome = inconclusive (no vindication change, no authority change, just cooldown).

**AP cost:** The defiant action's AP cost is charged (not the original order's cost). The defiant action is what actually executes, so AP follows what was done. Broken/retreating marshals cannot defy (guard check before defiance roll).

### Defiance Success Definition

```python
def defiance_succeeded(marshal, defiance_action, battle_result, pre_battle_strength):
    """Determine if a marshal's defiant action proved correct.

    Returns:
        True  — marshal was RIGHT (won cleanly, held position, survived retreat)
        False — marshal was WRONG (lost, pyrrhic victory, broken)
        None  — INCONCLUSIVE (sulked/waited, no testable outcome)

    Used to determine vindication/authority/trust changes via 4-row outcome table.
    """
    if defiance_action == "attack":
        won = battle_result["attacker"]["won"]
        casualties = battle_result["attacker"]["casualties"]
        casualty_pct = casualties / pre_battle_strength if pre_battle_strength > 0 else 1.0
        return won and casualty_pct < 0.50  # Won AND not pyrrhic
    elif defiance_action in ("defend", "fortify"):
        return not marshal.is_broken and not marshal.is_retreating
    elif defiance_action == "retreat":
        return marshal.strength > 0  # Survived
    elif defiance_action == "wait":
        return None  # Sulk/wait-fallback = inconclusive
    else:
        return None  # Unknown action = inconclusive
```

### Defiance Outcome Table

| Outcome | `defiance_succeeded()` | Trust | Vindication | Authority | Cooldown |
|---------|----------------------|-------|-------------|-----------|----------|
| Defiance succeeds, marshal **RIGHT** | `True` | +2 | +1 | -5 | 3 turns |
| Defiance succeeds, marshal **WRONG** | `False` | -5 | Reset to 0 | +3 | 3 turns |
| Defiance succeeds, **INCONCLUSIVE** (sulk) | `None` | 0 | No change | No change | 3 turns |
| Roll **fails**, marshal obeys | N/A | -3 | Reset to 0 | No change | 1 turn |

**Cooldown:** Set `marshal.defiance_cooldown_until = world.current_turn + N` (N=3 for any defiance that fires, N=1 for failed roll).

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
- NONE → MILD: **never** (vindication never creates fake objections about orders the marshal is fine with)
- MILD → MODERATE: yes
- MODERATE → STRONG: yes
- MILD → STRONG: **never** (single step only)
- MODERATE → EXTREME: **never** (single step only)

**Negative vindication (marshal proven wrong) → de-escalation ("boy who cried wolf"):**
- MODERATE → MILD: yes
- STRONG → MODERATE: yes (reduces defiance from 15% to 5% base)
- EXTREME → STRONG: yes
- MILD → NONE: **never** (even a discredited marshal still gets to grumble)

**Ordering:** `base trigger → vindication shift (+1 or -1 max) → mood variance (±1)`.

Maximum possible escalation from base = +2 levels (vindication +1, then mood +1). MILD can reach STRONG (vindication → MODERATE, mood → STRONG). MODERATE can reach EXTREME (vindication → STRONG, mood → EXTREME). These are rare compound events — correct behavior.

Maximum possible de-escalation from base = -2 levels (vindication -1, then mood -1). STRONG can drop to MILD. EXTREME can drop to MODERATE.

**Trigger condition:** `marshal.vindication_score > 0` enables escalation. `marshal.vindication_score < 0` enables de-escalation. Score of 0 = no shift.

### Defensive Vindication

Existing scaffolding: `VindicationTracker.pending_defensive_vindication` (dict, serialized, currently unwired).

**Creation:** When player chooses "trust" on an objection where the marshal's preferred alternative was defend/fortify/hold, add entry: `pending_defensive_vindication[marshal_name] = {"turn": current_turn}`.

**Resolution:** Wire into `turn_manager.py` enemy phase. When enemy attacks a marshal with pending defensive vindication:
- Marshal holds (not broken, not retreating) → vindication +1, entry cleared
- Marshal loses (broken or retreating) → vindication -1, entry cleared
- **First battle only** — if multiple enemies attack, first battle result resolves the entry

**Staleness:** Entries >5 turns old with no enemy attack are cleared during `advance_turn()`. The marshal's caution was neither proven right nor wrong — threat never materialized.

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

**Major victory definition:** Won battle while outnumbered (pre-battle attacker strength < defender strength) OR captured an enemy capital region. Authority change fires **ONCE per battle** — multiple qualifying criteria do not stack (+5, not +10).

**Major defeat definition:** Lost battle while outnumbering enemy (pre-battle attacker strength > defender strength) OR lost a capital region. Same once-per-battle rule (-5, not -10).

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

**IMPORTANT:** `check_excessive_trust()` **REPLACES** the trust-ratio penalty branch in `_evaluate_authority()`. Remove the old `trust_ratio > 0.80 → -5` and `trust_ratio > 0.60 → -2` lines from `_evaluate_authority()`. Keep the insist recovery (`insist_ratio > 0.80 → +1`) and balanced recovery (`0.30 ≤ trust_ratio ≤ 0.60 → +1`) branches. Single source of truth — do not allow both old and new penalties to stack.

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
| **Trust** | SUPPORT order not created. Marshal executes preferred tactical action instead (1 AP). Trust +5/+8 (STRONG gain). |
| **Compromise** | Timed SUPPORT — 3 turns then auto-cancels. Trust +3. Implementation: set `condition.max_turns = 3` with `order.started_turn = current_turn`. Existing `strategic.py` per-turn expiry code handles the rest (same pattern as timed HOLD/PURSUE). |

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

The timed SUPPORT compromise (3-turn auto-cancel) adds a 10th path via `condition.max_turns` expiry (same mechanism as timed HOLD/PURSUE).

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

### Berthier Flavor Text (8 minimum)

**Defiance success, marshal right (2 variants):**
- "Despite your express command, {marshal} {action}... and proved the wiser for it."
- "Your orders went unheeded by {marshal}. The outcome suggests they knew something you did not."

**Defiance success, marshal wrong (2 variants):**
- "{marshal} defied your authority and {action}. The results speak for themselves — poorly."
- "Acting against your express command, {marshal} {action}. It did not go well."

**Defiance inconclusive — sulk (2 variants):**
- "{marshal} defied your order... and then stood idle. The army watched in bewildered silence."
- "{marshal} refused to act on your command, yet offered no alternative. A wasted day."

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
Step 17:    If insist + MODERATE/STRONG/EXTREME: defiance roll  [NEW]
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

### Confidence Reporting Protocol

After EACH session, the implementer must report:

```
SESSION N CONFIDENCE REPORT
═══════════════════════════
Tests written: X passed / Y total
Edge cases verified: [list each EC-# tested]
Regressions checked: [list existing test suites re-run]
Confidence: XX% (explain any <100%)
Blockers for next session: [none / list]
```

Do NOT proceed to the next session until confidence = 100% on the current one.
If confidence < 100%, identify what's blocking and fix it before moving on.

---

### Session 0: Prerequisite Bug Fix (15 min)

**Goal:** Fix pre-existing V2a wiring gap. Authority system is inert without this.

1. **Wire `record_response()` in V2a path** — add `world.authority_tracker.record_response(choice)` to the V2a objection response handler in `executor.py` (`handle_objection_response()`). Currently only called from V1 path in `disobedience.py`.
2. **Test:** Write 3 tests confirming `record_response()` is called on trust/insist/compromise responses via V2a path and `recent_responses` list populates correctly.
3. **Run full existing test suite** — confirm zero regressions.

**Confidence gate:** All existing tests pass + 3 new tests pass. This is a bug fix, not a feature.

**Edge cases to verify:**
- Strategic objection responses also call `record_response()` (both `pending_objection` and `pending_strategic_objection` paths)
- `record_response()` returns threshold event dict when authority crosses 70/50/30 — verify event is passed through to API response

---

### Session 1: Core Mechanics — Defiance + Vindication + Authority

**Goal:** Full defiance/vindication/authority mechanics, testable without fog or UI.

**Part A — Infrastructure (low risk)**

1. **New marshal fields:** `last_objection_turn` (int, 0), `defiance_cooldown_until` (int, 0) + to_dict/from_dict
2. **`recent_responses` format migration** — `List[str]` → `List[Dict]` with `{"choice": str, "turn": int}`. Backward-compatible from_dict. Update `record_response(choice, current_turn=0)` signature.
3. **Excessive trust penalty** — `check_excessive_trust()` in `authority.py`. **REPLACES** the trust-ratio branch in `_evaluate_authority()` (remove old `trust_ratio > 0.80` → `-5` and `trust_ratio > 0.60` → `-2` lines). Keep insist/balanced recovery branches.
4. **Rename V1 cap** — `MAX_MAJOR_OBJECTIONS_PER_TURN` → `MAX_OBJECTION_POPUPS_PER_TURN`
5. **Notification** — add `MARSHAL_DEFIED_ORDER` type (HIGH priority)
6. **Campaign log** — add `"defiance"` event type to whitelist
7. **Serialization enforcement** — run `test_serialization_enforcement.py`

**Part B — Defiance Core (medium risk)**

8. **`calculate_defiance_chance()`** — new function in `defiance.py` (new file). Formula from §1. Hard cap 0.40.
9. **Defiance fallback table** — `get_defiant_action(marshal, original_action)` in `defiance.py`. Returns action string. Artillery marshals route to `_execute_auto_assign_bombardment()`, not `_execute_auto_assign_attack()`.
10. **`defiance_succeeded()`** — returns `True` (right), `False` (wrong), or `None` (inconclusive/sulk). Three-way return, not boolean.
11. **Defiance roll** — wire into `_execute_post_objection()` in `executor.py` after "insist" + MODERATE/STRONG/EXTREME
12. **Defiant action execution** — execute via existing `_execute_*` methods
13. **Outcome application** — 4-row outcome table:

| Outcome | Trust | Vindication | Authority | Cooldown |
|---------|-------|-------------|-----------|----------|
| Marshal **RIGHT** (`True`) | +2 | +1 | -5 | 3 turns |
| Marshal **WRONG** (`False`) | -5 | Reset to 0 | +3 | 3 turns |
| **INCONCLUSIVE** sulk (`None`) | 0 | No change | No change | 3 turns |
| Roll **fails**, obeys | -3 | Reset to 0 | No change | 1 turn |

**Part C — Vindication + Authority (medium risk)**

14. **Vindication escalation** — insert between base trigger and mood variance in executor.py objection flow. Guards: NONE never promotes (same principle as mood variance). `vindication_score > 0` → escalate +1. `vindication_score < 0` → de-escalate -1. MILD floor (never drops to NONE).
15. **Vindication decay** — add `_process_vindication_decay()` to `advance_turn()` in `world_state.py`. -1 per 3 idle turns, symmetric, timer resets.
16. **Defensive vindication creation** — when player chooses "trust" and marshal's alternative was defend/fortify/hold, add entry to `pending_defensive_vindication` as `{marshal_name: {"turn": current_turn}}`.
17. **Defensive vindication resolution** — wire in `turn_manager.py` enemy phase. First battle resolves (+1 hold / -1 lose). Stale entries (>5 turns, no attack) cleared.
18. **Authority major victory/defeat** — hook in `executor.py` after `resolve_battle()` + advance-after-win. +5 outnumbered win or capital capture. -5 outnumbering loss or capital loss. Fires ONCE per battle (multiple criteria don't stack).
19. **Berthier flavor text** — 8 templates (2 right, 2 wrong, 2 failed roll, 2 inconclusive/sulk)

**Part D — Relationship SUPPORT Objection (low risk, no fog dependency)**

20. **Relationship-based trigger** — add to `evaluate_strategic_situation()` in `objection_v2.py`. Aggressive+hostile → STRONG. Cautious+hostile → MODERATE. Literal → NONE. Rival → MILD. Runs BEFORE personality evaluator, takes priority if higher.
21. **Timed SUPPORT compromise** — use `condition.max_turns = 3` with `order.started_turn = current_turn`. Existing strategic.py expiry code handles the rest. Do NOT use `cancel_after_turn` (field doesn't exist).
22. **`main.py` passthrough** — defiance result fields in POST /command response

**Edge cases to verify in Session 1:**
- EC-1: Sulk returns `None` from `defiance_succeeded()`, outcome = INCONCLUSIVE row
- EC-2: NONE concern + positive vindication stays NONE (no fake objections)
- EC-4: Old trust-ratio penalty removed from `_evaluate_authority()`, only `check_excessive_trust()` applies
- EC-5: Battle meeting multiple authority criteria → fires once (+5 or -5, not +10)
- EC-6: Timed SUPPORT uses `condition.max_turns`, not `cancel_after_turn`
- EC-8: Defensive vindication created on "trust" when alternative was defend/fortify/hold
- EC-9: Artillery marshal defiance routes to `_execute_auto_assign_bombardment()`
- Vindication score at boundaries (-5, +5) — clamp works correctly
- Defiance chance with all modifiers maxed — hard cap holds at 0.40
- Cooldown math: turn 10 + 3 = cooldown_until 13, turn 13 can defy (< not <=)

**Confidence gate:** All Session 1 tests pass + full existing suite passes + all EC-# items verified.

---

### Session 2: Fog-of-War Migration

**Goal:** Switch objection helpers from omniscient to fog-filtered. Pure fog work, nothing else.

**Step 1 — Infrastructure (2 helpers)**

1. **Update `get_visible_enemies_near()`** — swap from raw `world.marshals` scan to fog-filtered via `world.get_intel()` / `world.get_visible_enemies_in_region()`. Only returns enemies at PARTIAL+ visibility.
2. **Add `get_target_intel_level(target_name, marshal, world)`** — new helper for Type B queries (specific named target). Returns visibility level (UNKNOWN/STALE/PARTIAL/FULL) for a given enemy marshal from the perspective of the querying marshal.

**Step 2 — Type A: Scan Queries (3 leaf changes → 3 auto-propagate)**

3. **`_check_enemy_adjacent()`** — route through `get_visible_enemies_near()`. LEAF.
4. **`_get_friendly_to_enemy_ratio()`** — route through `get_visible_enemies_near()`. At PARTIAL, use strength band midpoint. At UNKNOWN, enemy contributes 0. LEAF.
5. **`_path_crosses_enemy()` / `_path_has_enemies()`** — per-region fog check along path. Only detect PARTIAL+ enemies. LEAF.
6. Auto-propagated (no code changes needed):
   - `_get_enemy_to_friendly_ratio()` — delegates to `_get_friendly_to_enemy_ratio()`
   - `_is_outnumbered_2to1()` — delegates to `_get_enemy_to_friendly_ratio()`
   - `_is_actually_threatened()` — delegates to `_check_enemy_in_region()` + `_check_enemy_adjacent()`

**Step 3 — Type B: Target Info Queries (2 functions)**

7. **`_get_attack_odds_ratio()`** — use `get_target_intel_level()`. FULL = exact strength. PARTIAL = band midpoint. STALE/UNKNOWN = return 1.0 (can't assess).
8. **`_check_attack_target_fortified()`** — use `get_target_intel_level()`. FULL = real fort status. Anything less = return False (don't know).

**Step 4 — New Fog-Specific Triggers (4 situations)**

9. **Attack into UNKNOWN region** — cautious: MODERATE→STRONG. Aggressive: no concern.
10. **Attack on STALE intel (3+ turns old)** — cautious: MODERATE. Aggressive: MILD at most.
11. **Refuse attack when scout shows weakness** — cautious: no concern. Aggressive: MODERATE→STRONG.
12. **PURSUE with no intel on target** — cautious: STRONG. Aggressive: MILD. Literal: depends on clarity.

These integrate as additional checks in `evaluate_cautious_*` and `evaluate_aggressive_*`.

**Edge cases to verify in Session 2:**
- EC-3: Multi-battle defensive vindication — first battle resolves, entry cleared
- Marshal's own region always FULL (Step 0 rule) — enemies in same region always visible
- STALE threshold: `current_turn - last_updated_turn >= 3`
- Cautious attacks fortified target at PARTIAL visibility — no fort bump (can't see fort)
- Fog-filtered ratios: 0 visible enemies → ratio 999.0 (no enemies nearby), not 0
- Path with mix of PARTIAL/UNKNOWN regions — only PARTIAL+ enemies detected
- `_check_enemy_in_region()` unchanged (own region = FULL, always sees co-located enemies)
- Aggressive marshal attacking into UNKNOWN → no objection (aggressive doesn't care about fog)

**Confidence gate:** All Session 2 tests pass + Session 1 tests still pass + full existing suite passes.

---

### Session 3: Frontend + Polish + UI Tests

**Goal:** Wire everything to Godot, generate Gate 6 UI test checklist, update docs.

1. **Godot integration** — defiance message display in `main.gd`. Show defiant action result, Berthier text, trust/authority changes.
2. **Marshal management screen** — vindication score visible on marshal cards (if not already).
3. **Authority display** — authority level visible in strategic ledger or dispatch.
4. **Doc updates** — STATUS.md, SYSTEMS_REFERENCE.md, SAVE_FORMAT_REFERENCE.md, CLAUDE.md
5. **Generate Gate 6 UI test checklist** — comprehensive manual test plan (see §10.8)

**Confidence gate:** Docs updated + UI test checklist generated + curl test of all new API fields confirms correct data reaches frontend.

---

## 10. Test Plan Outline

### 10.1 Session 0: Prerequisite Fix (~5 tests)

- `record_response()` called on V2a tactical "trust" response
- `record_response()` called on V2a tactical "insist" response
- `record_response()` called on V2a strategic objection response
- `recent_responses` list populates correctly after multiple responses
- Threshold event returned when authority crosses 70/50/30

### 10.2 Defiance Mechanics (~30 tests)

- `calculate_defiance_chance`: base rates for MODERATE (5%) / STRONG (15%) / EXTREME (35%)
- Hard cap at 40% with all modifiers maxed positive
- Returns 0.0 for MILD only
- Grouchy (literal) always returns 0.0
- Cooldown blocks defiance (turn < cooldown_until)
- Cooldown boundary: turn == cooldown_until → CAN defy (< not <=)
- Vindication modifier (+10% per stack, tested at 0, +3, +5, -5)
- Authority modifier (-10% at ≥80 / 0% at 50-79 / +10% at <50)
- Trust tier modifier (+15% at ≤20 / 0% at 21-79 / -10% at ≥80)
- Negative vindication makes chance go to 0 (clamped, not negative)
- Authority clamped 0-100 after all modifications

### 10.3 Defiance Actions (~18 tests)

- Aggressive fallback: defend→attack, fortify→attack, hold→attack, wait→attack, retreat→attack, SUPPORT→attack, MOVE_TO→attack
- Cautious fallback: attack→fortify, SUPPORT→fortify, MOVE_TO→fortify
- Literal: ALL actions → never defies (returns None)
- Blocked preferred action → wait (sulk)
- AP charged = original action's AP cost (not defiant action's cost)
- Artillery aggressive defiance routes to `_execute_auto_assign_bombardment()` (EC-9)
- Non-artillery aggressive defiance routes to `_execute_auto_assign_attack()`

### 10.4 Defiance Outcomes (~25 tests)

- RIGHT (True): trust +2, vindication +1, authority -5, 3-turn cooldown
- WRONG (False): trust -5, vindication reset to 0, authority +3, 3-turn cooldown
- **INCONCLUSIVE (None):** trust 0, vindication unchanged, authority unchanged, 3-turn cooldown (EC-1)
- Failed roll: trust -3, vindication reset to 0, no authority change, 1-turn cooldown
- Pyrrhic victory (>50% casualties) = WRONG not RIGHT
- Defend/fortify success = not broken and not retreating → RIGHT
- Defend/fortify but broken → WRONG
- Retreat success = survived (strength > 0) → RIGHT
- Sulk/wait fallback = INCONCLUSIVE (None), not WRONG (EC-1)
- Defiance + square formation: aggressive attack auto-breaks square, attack proceeds

### 10.5 Vindication (~25 tests)

- Positive decay: -1 per 3 idle turns toward 0
- Negative decay: +1 per 3 idle turns toward 0 (symmetric)
- Decay at boundary: score 1 → 0, score -1 → 0 (stops at zero)
- Decay timer resets on any objection (including MILD)
- No decay when vindication_score == 0
- No decay for dead marshals (strength <= 0)
- Escalation: MILD→MODERATE with positive vindication
- Escalation: MODERATE→STRONG with positive vindication
- **NONE never escalates** — NONE + positive vindication stays NONE (EC-2)
- No double-step: MILD cannot reach STRONG via vindication alone
- De-escalation: MODERATE→MILD with negative vindication
- De-escalation: STRONG→MODERATE with negative vindication (reduces defiance from 15% to 5% base)
- EXTREME→STRONG de-escalation works
- **MILD never drops to NONE** (floor, both vindication and mood)
- Ordering: base trigger → vindication shift → mood variance
- Compound event: MILD + vindication(+1) + mood(+1) → STRONG (rare but correct)
- Defensive vindication creation: "trust" on defend/fortify/hold alternative → entry added
- Defensive vindication resolution: hold → +1, lose → -1
- Defensive vindication stale: >5 turns no attack → cleared (EC-8)
- Defensive vindication multi-battle: first battle resolves, entry cleared (EC-3)

### 10.6 Authority (~20 tests)

- Major victory: +5 (outnumbered win)
- Major victory: +5 (capital capture)
- Major victory: both criteria met → +5 once, not +10 (EC-5)
- Major defeat: -5 (outnumbering loss)
- Major defeat: -5 (capital loss)
- Excessive trust ratio >0.65 in 10-turn window: -2
- Excessive trust ratio >0.80 in 10-turn window: -3
- Minimum 3 responses before penalty fires (< 3 → 0)
- Old trust-ratio penalty in `_evaluate_authority()` REMOVED (EC-4)
- Insist/balanced recovery in `_evaluate_authority()` still works
- Authority clamp: never below 0, never above 100
- `recent_responses` format migration: bare strings → dicts with turn 0
- `recent_responses` time window: entries from >10 turns ago excluded
- Old save with string responses loads correctly and decays naturally

### 10.7 Relationship SUPPORT Objection (~12 tests)

- Aggressive + hostile (-2) target → STRONG
- Cautious + hostile (-2) target → MODERATE
- Literal + hostile target → NONE
- Any personality + rival (-1) target → MILD (no popup)
- Relationship check runs BEFORE personality evaluator
- Higher of relationship/personality concern wins (max, not replace)
- Compromise: timed 3-turn SUPPORT uses `condition.max_turns = 3` (EC-6)
- Timed SUPPORT auto-expires after 3 turns via existing strategic.py code
- Defiance from hostile SUPPORT (aggressive): attacks nearest enemy instead
- Defiance from hostile SUPPORT (cautious, MODERATE): low defiance chance (5% base)
- Forced hostile SUPPORT: 0% coordination (existing D3 rule, regression check)
- Hostile SUPPORT >30% casualties: campaign log entry, no mechanical effect

### 10.8 Fog Migration (~25 tests)

- `get_visible_enemies_near()` returns only PARTIAL+ enemies
- `get_visible_enemies_near()` excludes UNKNOWN/STALE enemies
- `get_target_intel_level()` returns correct level for FULL/PARTIAL/STALE/UNKNOWN targets
- `_check_enemy_adjacent()`: no false positives from fogged enemies
- `_get_friendly_to_enemy_ratio()`: PARTIAL uses strength band midpoint
- `_get_friendly_to_enemy_ratio()`: UNKNOWN enemies = 0 contribution
- `_get_attack_odds_ratio()`: FULL = exact, PARTIAL = band midpoint, STALE/UNKNOWN = 1.0
- `_check_attack_target_fortified()`: FULL = real status, other = False
- `_path_crosses_enemy()`: only detects PARTIAL+ enemies along path
- Marshal's own region: always FULL (co-located enemies always visible)
- `_check_enemy_in_region()`: unchanged (own region = FULL)
- Fog trigger: cautious attack into UNKNOWN → MODERATE→STRONG
- Fog trigger: aggressive attack into UNKNOWN → no concern
- Fog trigger: cautious attack on STALE intel → MODERATE
- Fog trigger: aggressive attack on STALE → MILD at most
- Fog trigger: aggressive, scout shows weakness → MODERATE→STRONG
- Fog trigger: cautious PURSUE no intel → STRONG
- Fog trigger: aggressive PURSUE no intel → MILD
- Delegation chain: `_is_outnumbered_2to1()` inherits fog from `_get_enemy_to_friendly_ratio()`
- Delegation chain: `_is_actually_threatened()` inherits fog from `_check_enemy_adjacent()`

### 10.9 Integration (~12 tests)

- Full defiance flow: objection → insist → defiance roll → defiant action → outcome → trust/vindication/authority changes
- Full defiance flow with INCONCLUSIVE (sulk): same flow, no stat changes, cooldown applied
- Defiance + strategic order: SUPPORT defied → order never registered → ally loses coordination
- Defiance + square formation: auto-break square → defiant attack proceeds
- Serialization round-trip with all new fields (marshal, authority_tracker)
- Serialization round-trip with old save format (backward compat migration)
- Notification fires on defiance event (MARSHAL_DEFIED_ORDER, HIGH priority)
- Campaign log entry on defiance
- Berthier flavor text selection: right/wrong/inconclusive/failed — correct template category
- API response contains defiance fields (curl test)
- Authority event passthrough to API when threshold crossed during response

### 10.10 Gate 6 UI Test Checklist (Generated After Session 3)

To be generated as update to `docs/PHASE7_UI_TEST_GATE.md` Gate 6 section.

Covers:

#### Defiance Display
- [ ] MODERATE/STRONG/EXTREME objection → player insists → defiance message appears (distinct from objection popup)
- [ ] Defiance RIGHT: Berthier text shows marshal was vindicated, trust +2 visible
- [ ] Defiance WRONG: Berthier text shows marshal failed, trust -5 visible
- [ ] Defiance INCONCLUSIVE (sulk): message shows marshal refused but did nothing
- [ ] Failed roll: "discipline held" message appears, no defiance
- [ ] MODERATE defiance rare (~5% base) but possible
- [ ] MILD concern: flavor text only, no popup, no defiance (regression check)

#### Vindication Display
- [ ] Marshal management screen shows vindication score for each marshal
- [ ] Vindication score updates visible after defiance resolution
- [ ] Vindication decay observable over 3+ turns of no objections

#### Authority Display
- [ ] Authority level visible in strategic ledger or dispatch
- [ ] Authority threshold event ("Whispers of Weakness" etc.) appears as notification
- [ ] Excessive trust pattern shows authority decline over multiple objection responses

#### Relationship SUPPORT
- [ ] Order hostile marshal to SUPPORT rival → objection popup fires
- [ ] Aggressive + hostile: STRONG concern, defiance possible after insist
- [ ] Cautious + hostile: MODERATE concern, low defiance chance (5% base)
- [ ] Compromise: timed 3-turn SUPPORT → auto-expires, notification sent
- [ ] Literal + hostile: no objection (regression check)

#### Fog-Aware Objections
- [ ] Attack into UNKNOWN region: cautious marshal objects, aggressive doesn't
- [ ] Attack with STALE intel: cautious shows concern
- [ ] Objection text references fog state ("we know nothing of that region")
- [ ] No objections about enemies the marshal can't see (fog leak regression)

#### Notification & Log
- [ ] Defiance notification appears in notification bar (HIGH priority)
- [ ] Defiance event appears in campaign log with correct one-liner
- [ ] Dismissing defiance notification works

#### Regression Checks
- [ ] Normal 1v1 combat still works
- [ ] Save/load preserves all new fields (vindication, cooldown, authority, recent_responses)
- [ ] Old saves load correctly (backward-compatible defaults)
- [ ] Marshal management screen loads without errors
- [ ] All 10 existing notification types still work
- [ ] Strategic orders (SUPPORT/PURSUE/HOLD/MOVE_TO) still function normally

**Estimated total: ~172 tests across 3 sessions + UI gate checklist.**

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

| File | Scope | Risk | Session |
|------|-------|------|---------|
| `defiance.py` (NEW) | `calculate_defiance_chance()`, fallback table, `defiance_succeeded()` | LOW (new file, no conflicts) | 1 |
| `objection_v2.py` | 8 fog helpers + vindication escalation + relationship trigger | **HIGH** (1390 lines, core objection logic) | 1 (escalation + relationship) + 2 (fog) |
| `executor.py` | Post-objection defiance flow + authority hooks + `record_response()` wiring | MEDIUM (large file, well-structured insertion points) | 0 + 1 |
| `world_state.py` | Vindication decay + stale defensive vindication cleanup in advance_turn | LOW (small addition) | 1 |
| `turn_manager.py` | Defensive vindication resolution in enemy phase | LOW (small addition) | 1 |
| `marshal.py` | 2 new int fields + serialization | LOW (standard pattern) | 1 |
| `authority.py` | Replace trust-ratio penalty + enriched recent_responses + excessive trust check | LOW-MEDIUM | 1 |
| `vindication.py` | Remove TODOs (logic moves to world_state/turn_manager) | LOW | 1 |
| `disobedience.py` | Rename constant | LOW | 1 |
| `notifications.py` | 1 new notification type | LOW | 1 |
| `campaign_log.py` | 1 new event type in whitelist | LOW | 1 |
| `main.py` | Passthrough defiance result fields | LOW | 1 |
| `main.gd` | Display defiance messages | LOW (frontend) | 3 |

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
| Hostile SUPPORT (cautious) | MILD, MODERATE, STRONG | **MODERATE** | Professional reluctance, low defiance risk (5% base). Personality distinction. |
| Cooperation floor | Hard block at trust 0, no floor | **No floor** | Soft costs self-regulate; hard floor removes agency in desperate situations |
| Escalation ordering | Mood→vindication, vindication→mood | **Vindication→mood** | Rare compound events (MODERATE→EXTREME) are correct behavior |
| Authority bounds | Unbounded, 0-100, 0-150 | **0-100** | Simple, clean, starting value is ceiling |
| Defiance AP cost | Defiant action's cost, original action's cost | **Defiant action's cost** | AP follows the action actually taken, not the order that was disobeyed |
| Negative vindication decay | No decay, symmetric decay | **Symmetric** | Marshal proven wrong 15 turns ago shouldn't carry that forever |
| Negative vindication de-escalation | No effect, symmetric de-escalation | **Symmetric ("boy who cried wolf")** | Discredited marshal's concerns carry less weight. MILD floors at MILD. |
| Timed SUPPORT implementation | New `turns_remaining` field, `cancel_after_turn` check, `condition.max_turns` | **`condition.max_turns`** | Reuses existing timed HOLD/PURSUE pattern. Zero new fields or infrastructure. |
| Defiant attack targeting | Named target required, auto-assign | **Auto-assign** | Uses existing `_execute_auto_assign_attack()`. No named target needed. |
