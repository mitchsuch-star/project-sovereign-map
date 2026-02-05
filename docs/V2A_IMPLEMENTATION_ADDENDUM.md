# V2a Implementation Addendum: Review Resolutions & Final Decisions

**Status:** LOCKED — Ready for Claude Code
**Date:** February 5, 2026
**Context:** Resolves all ambiguities from V2a review document, incorporates Mitch's design input

---

## Part 1: Critical Issue Resolutions

### Issue 1: MILD Storage Mechanism

**Decision:** Store on `world.mild_concerns_this_turn` (list of dicts).

```python
# world_state.py — add field
self.mild_concerns_this_turn: List[Dict] = []

# Clear at start of each turn (in turn_manager.py or world_state advance_turn)
world.mild_concerns_this_turn = []

# When MILD fires (in objection_v2.py):
world.mild_concerns_this_turn.append({
    "marshal": marshal.name,
    "message": generate_mild_flavor(marshal, action, context)
})

# main.py — include in turn response
response["mild_concerns"] = world.mild_concerns_this_turn
```

NOT stored on marshal. NOT stored on DisobedienceSystem. World-level list, cleared each turn.

Max 1 MILD per marshal per turn. Check before appending:
```python
if any(m["marshal"] == marshal.name for m in world.mild_concerns_this_turn):
    return  # Already have MILD for this marshal this turn
```

### Issue 2: Scaling Trigger Implementation

**Decision:** Pure functions per personality, NOT nested dicts, NOT lambdas.

```python
def evaluate_aggressive(marshal, action, game_state) -> ConcernLevel:
    """Evaluate aggressive personality concern for given action."""
    if action in ("defend", "fortify", "hold", "wait"):
        enemy_adjacent = _check_enemy_adjacent(marshal, game_state)
        if not enemy_adjacent:
            return ConcernLevel.MILD
        ratio = _get_friendly_to_enemy_ratio(marshal, game_state)
        if ratio >= 3.0:    # Outnumber 3:1+
            return ConcernLevel.EXTREME
        if ratio >= 2.0:    # Outnumber 2:1+
            return ConcernLevel.STRONG
        return ConcernLevel.MODERATE   # Enemy adjacent, roughly equal
    
    if action == "retreat":
        if not _is_actually_threatened(marshal, game_state):
            return ConcernLevel.STRONG
        if not _is_outnumbered_2to1(marshal, game_state):
            return ConcernLevel.MILD
        return ConcernLevel.NONE  # Outnumbered 2:1+, retreat makes sense
    
    if action == "drill" and _check_enemy_adjacent(marshal, game_state):
        return ConcernLevel.MODERATE
    
    return ConcernLevel.NONE

def evaluate_cautious(marshal, action, game_state) -> ConcernLevel:
    """Evaluate cautious personality concern for given action."""
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

Each function is pure, testable, and self-documenting. Strategic triggers (HOLD, PURSUE, MOVE_TO, SUPPORT) get similar functions — see Issue 3.

### Issue 3: Strategic Objection Migration

**Decision:** YES, `check_strategic_objection()` and `calculate_strategic_severity()` are REPLACED by ConcernLevel system. Same pipeline, different trigger entries.

```python
def evaluate_strategic_aggressive(marshal, order_type, target, path, game_state) -> ConcernLevel:
    """Aggressive marshal strategic concerns."""
    if order_type == "HOLD":
        # Same logic as tactical defend, but applied to the HOLD target
        enemy_adjacent = _check_enemy_adjacent_to_region(target, game_state)
        if not enemy_adjacent:
            return ConcernLevel.MILD
        ratio = _get_ratio_at_region(marshal, target, game_state)
        if ratio >= 3.0: return ConcernLevel.EXTREME
        if ratio >= 2.0: return ConcernLevel.STRONG
        return ConcernLevel.MODERATE
    return ConcernLevel.NONE

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

The dangerous path objection (Davout objects to marching through enemy territory) maps cleanly to MODERATE. Safe path compromise is still offered at MODERATE+.

**Migration:** Delete `calculate_strategic_severity()`. Replace `check_strategic_objection()` body with a call to the V2 evaluate functions. Preserve the return dict shape and `pending_strategic_objection` storage field.

### Issue 4: Objection Cap Semantics

**Decision:** Per-marshal cap ONLY. Drop global cap entirely.

**Rationale (from playtesting discussion):** Global cap creates an exploit where giving suicidal orders to N marshals causes marshal N+1's EXTREME concern to downgrade to MILD — silent march to death. Per-marshal cap (max 1 MODERATE+ popup per marshal per turn) already prevents spam. With 3 marshals (Waterloo) = max 3 popups. With 30 marshals (1805), player won't give bad orders to more than a few per turn. If they do, they deserve every popup.

```python
# Per-marshal tracking
if marshal.name in world.objection_popups_this_turn:
    # Already had a popup this turn — additional concerns cap at MILD
    concern = ConcernLevel.MILD

# After showing popup:
world.objection_popups_this_turn.add(marshal.name)
```

`world.objection_popups_this_turn` is a `set()`, cleared at turn start.

### Issue 5: Behavior Change Acknowledgment (1.5:1 → MILD)

**Decision:** Intentional. Acknowledged.

Old: 1.5:1 cautious attack → severity 0.50 → MAJOR popup.
New: 1.5:1 cautious attack → MILD → flavor text in turn log.

This is correct because 1.5:1 odds aren't dangerous enough to interrupt the player with a popup. Davout noting mild concern in the turn log is the right response. The old system was too aggressive at low odds ratios. Real gameplay disruption should start at 2:1+ (MODERATE popup).

### Issue 6: Authority Gap in V2a

**Decision:** Authority has NO mechanical effect in V2a. Documented explicitly.

```python
# V2a: authority is tracked but inert
# It exists as a field (world.authority or world.authority_tracker)
# but is NOT referenced in evaluate_situation() or get_trust_tier()
# V2b gives it purpose in defiance calculations
```

Do NOT fake it. Do NOT add placeholder effects. Just don't touch it.

---

## Part 2: Design Decisions from Mitch's Input

### Decision A: Keep Uncertainty (Variance at Tier Boundaries)

**Rejected:** Full determinism.
**Approved:** Small variance band at ConcernLevel boundaries.

Marshals are humans. A ~15-20% chance that borderline situations shift ±1 level keeps things unpredictable while remaining vastly more predictable than V1.

```python
import random

def apply_mood_variance(concern: ConcernLevel) -> ConcernLevel:
    """
    Small random variance at tier boundaries.
    ~15-20% chance of shifting ±1 level.
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

**IMPORTANT for tests:** Tests must either (a) mock `random.random()` to get deterministic results, or (b) test the pure evaluation function BEFORE variance is applied. Both approaches documented in test plan.

### Decision B: Hide Compliance Chance in V2a

**Decision:** Do NOT show compliance_chance in V2a. Do NOT include it in return dict.

In V2a, insist always works. Showing "60% compliance" that always succeeds is a lie. Remove the field entirely until V2b gives it teeth.

```python
# V2a return dict — NO compliance_chance field
return {
    "type": "objection",
    "concern_level": concern.name,
    "tone": consequences["tone"],
    "message": generate_message(marshal, concern, trust_tier),
    "insist_penalty": consequences["penalty"],
    # "compliance_chance" — OMITTED in V2a, added in V2b
    "options": build_options(concern),
    "popup": True
}
```

**V2b addition:** When defiance is implemented, disobey_chance should have its own variance band (±5-8%) so players can't memorize exact thresholds. Humans aren't perfectly predictable.

### Decision C: Skip Balanced/Loyal Trigger Tables

**Decision:** V2a implements triggers for 3 personalities ONLY:
- Aggressive (Ney, Blucher)
- Cautious (Davout, Wellington)
- Literal (Grouchy — bypass to clarification)

Balanced (Soult) and Loyal (Lannes) stubs are NOT built. When those marshals ship (possibly not until 1805), their trigger tables will be designed and implemented then. EA may ship with just these 3 personality types.

```python
PERSONALITY_EVALUATORS = {
    "aggressive": evaluate_aggressive,
    "cautious": evaluate_cautious,
    "literal": lambda m, a, gs: ConcernLevel.NONE,  # Bypass (uses clarification)
}

def evaluate_situation(marshal, action, game_state) -> ConcernLevel:
    evaluator = PERSONALITY_EVALUATORS.get(marshal.personality.lower())
    if evaluator is None:
        return ConcernLevel.NONE  # Unknown personality = no objection (safe default)
    return evaluator(marshal, action, game_state)
```

Unknown personalities default to NONE. Safe, forward-compatible.

### Decision D: Trust Gain Scaling (Combined Concern × Tier)

**Decision:** Trust gain scales with BOTH concern level AND trust tier.

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

**Combined trust gain = int(base × multiplier):**

| | HOSTILE (1.5x) | WARY (1.2x) | TRUSTING (1.0x) | DEVOTED (0.7x) |
|---|---|---|---|---|
| **MODERATE** (+3) | +5 | +4 | +3 | +2 |
| **STRONG** (+5) | +8 | +6 | +5 | +4 |
| **EXTREME** (+8) | +12 | +10 | +8 | +6 |

**Compare to insist penalties:**

| Trust Tier | Insist Cost | Trust on MODERATE | Trust on EXTREME |
|------------|-------------|-------------------|------------------|
| HOSTILE | -15 | +5 | +12 |
| WARY | -12 | +4 | +10 |
| TRUSTING | -10 | +3 | +8 |
| DEVOTED | -5 | +2 | +6 |

**Gameflow analysis:**
- Insisting always costs more than trusting gains → incentivizes trusting marshals
- At HOSTILE, one EXTREME trust (+12) nearly recovers one insist (-15) → climbable
- At DEVOTED, insisting barely hurts (-5) → no death spiral at high trust
- Trust naturally gravitates toward TRUSTING/DEVOTED range
- Impossible to cheese to max quickly because DEVOTED multiplier is 0.7x
- All values wrapped with int() for Godot compatibility

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
```

---

## Part 3: Conflict Resolutions (from Review Table)

### Conflict 1: Mild Threshold (UX Change)

**Old:** 0.20-0.49 = mild auto-resolve shown immediately.
**New:** MILD = no popup, flavor in turn log at end.
**Resolution:** Intentional UX improvement. MILD was interrupting command flow for trivial concerns. Turn log placement makes it atmosphere, not feedback. This is the design.

### Conflict 2: Objection Cap (Semantic Change)

**Old:** Global max 2 per turn.
**New:** Per-marshal max 1 per turn. No global cap.
**Resolution:** See Issue 4 above. Global cap exploitable. Per-marshal cap is sufficient. Scales to 1805 with 30 marshals.

### Conflict 3: Variance (Partially Removed)

**Old:** ±3-12% random variance on severity float.
**New:** Deterministic base triggers with ~15-20% ±1 level mood variance.
**Resolution:** See Decision A above. Variance is dramatically reduced but not eliminated. The old system had variance baked into the trigger calculation (unreproducible). The new system has variance as a separate, mockable layer applied after evaluation. Tests can mock it. Players still feel unpredictability.

### Conflict 4: 1.5:1 Cautious (Behavior Change)

**Old:** Severity 0.50 = MAJOR popup.
**New:** MILD (turn log flavor).
**Resolution:** See Issue 5 above. Intentional. 1.5:1 is not dangerous enough for a popup.

### Conflict 5: Strategic Objections (Migration Path)

**Old:** `calculate_strategic_severity()` with hardcoded base severities.
**New:** ConcernLevel evaluation functions.
**Resolution:** See Issue 3 above. Full migration. Delete old functions, replace with V2 evaluators.

---

## Part 4: LLM Pipeline Confirmation

**Question from review:** Do LLM-parsed commands still trigger objections?

**Answer:** YES. Objections fire in the executor (step 5 of pipeline), not the parser (steps 1-3). The pipeline is:

```
User Input → Fast Parser or LLM → Strategic Parser → Validation → Executor → Objection Check
```

Whether the command was parsed by keyword matching or Claude API, it arrives at the executor as an identical `{action, marshal, target}` dict. The executor checks objections before executing. LLM parsing is completely decoupled from the objection system. Building Blocks principle.

**No changes needed** to the LLM pipeline for V2a. The LLM layer is upstream of objections.

---

## Part 5: Edge Case Resolutions (from Review Items 12-16)

### Edge 12: Retreat Recovery + Pending Vindication

**Resolution:** No conflict. Combat → vindication resolves → THEN retreat_recovery set. Order of operations is correct. No action needed.

### Edge 13: Two Marshals Same Region Both Ordered to Defend

**Resolution:** With per-marshal cap, both popups fire (1 per marshal). Correct behavior. No global cap to block the second one.

### Edge 14: Strategic HOLD → Insist → Interrupt Next Turn

**Resolution:** No double-firing. Objection fires at issuance (once, via `objection_resolved` flag). Interrupt fires during execution (separate system). If player cancels via interrupt and re-issues, objection CAN fire again — correct, circumstances changed.

### Edge 15: Vindication Decay While Pending

**Resolution:** No conflict. Pending clears at end of enemy phase. Decay ticks every 3 turns. Pending doesn't persist long enough for decay to matter.

### Edge 16a: Multiple Enemies Attack Same Marshal

**Resolution:** First attack resolves vindication, clears pending. Second attack has no pending to resolve. Safe as long as implementation checks `if marshal.name in pending_defensive_vindication`.

### Edge 16b: MILD Max — Per Action or Total?

**Decision:** Total max 1 MILD per marshal per turn, regardless of how many actions. First MILD logged, subsequent ones for that marshal silently dropped. Prevents log noise.

### Edge 16c: Grouchy Accidental Strategic Objection

**Resolution:** Personality check BEFORE storing strategic objection:
```python
if marshal.personality == "literal":
    return None  # Grouchy never enters objection system
```
This check already exists and is preserved in V2a.

### Edge 16d: Authority Inert in V2a

**Resolution:** See Issue 6 above. Documented, no action.

### Edge 16e: Off-by-One in Trust Tier Boundaries

**Decision:** Use consistent `>=` operators:
```python
def get_trust_tier(trust: int) -> TrustTier:
    if trust >= 80: return TrustTier.DEVOTED
    if trust >= 50: return TrustTier.TRUSTING
    if trust >= 30: return TrustTier.WARY
    return TrustTier.HOSTILE
```
Trust of exactly 30 = WARY. Trust of exactly 50 = TRUSTING. Trust of exactly 80 = DEVOTED. No gaps.

---

## Part 6: Return Dict Shape (Backward Compatibility)

### MODERATE+ Objection Return Dict

```python
# V2a return — preserves shape, adds new fields
{
    # PRESERVED (required by existing code):
    "type": "major_objection",         # Keep exact string for Godot compat
    "marshal": str,
    "personality": str,
    "severity": float,                  # DEPRECATED but kept — map ConcernLevel to float
    "order": dict,
    "message": str,
    "options": list,
    "suggested_alternative": dict,
    "compromise": dict,

    # NEW (safe to add — Godot ignores unknown fields):
    "concern_level": str,               # "MODERATE", "STRONG", "EXTREME"
    "tone": str,                        # "respectful", "firm", "challenging", "defiant"
    "insist_penalty": int,              # -5 to -15
    "popup": True,
}
```

**Severity mapping for backward compat:**
```python
CONCERN_TO_SEVERITY = {
    ConcernLevel.MODERATE: 0.55,
    ConcernLevel.STRONG: 0.72,
    ConcernLevel.EXTREME: 0.88,
}
```

### MILD Return Dict

```python
{
    "type": "mild_concern",
    "execute": True,
    "trust_change": 0,
    "popup": False,
    "message": str,    # For turn log storage
    "marshal": str,
}
```

MILD returns are NOT stored in `pending_objection`. They're processed immediately (order executes), then message is appended to `world.mild_concerns_this_turn`.

---

## Part 7: Serialization Changes

### New Fields in WorldState

```python
# world_state.py to_dict() additions:
"mild_concerns_this_turn": self.mild_concerns_this_turn,  # List[Dict]
"objection_popups_this_turn": list(self.objection_popups_this_turn),  # Set → List

# from_dict() additions:
world.mild_concerns_this_turn = data.get("mild_concerns_this_turn", [])
world.objection_popups_this_turn = set(data.get("objection_popups_this_turn", []))
```

### New Fields in VindicationTracker

```python
# vindication.py to_dict() additions:
"pending_defensive_vindication": self.pending_defensive_vindication,

# from_dict() additions:
tracker.pending_defensive_vindication = data.get("pending_defensive_vindication", {})
```

Default `{}` ensures existing saves load without error.

**Update SAVE_FORMAT_REFERENCE.md** with these new fields.

---

## Part 8: Updated Implementation Units (for Claude Code)

### Unit 1: Core Data Structures → **Sonnet**
- `ConcernLevel` enum
- `TrustTier` enum  
- `CONSEQUENCE_TABLE` (tone, insist_penalty per tier)
- `TRUST_GAIN_BASE` and `TRUST_TIER_MULTIPLIER` tables
- `get_trust_tier()` function
- `calculate_trust_gain()` function
- `apply_mood_variance()` with small random band
- Unit tests for all (mock random for variance tests)

### Unit 2: Trigger Evaluation Functions → **Sonnet**
- `evaluate_aggressive()` — tactical triggers
- `evaluate_cautious()` — tactical triggers
- `evaluate_situation()` — main dispatcher
- Helper functions: `_check_enemy_adjacent()`, `_get_ratio()`, etc.
- Literal personality early-exit
- Unit tests: every personality × action × context

### Unit 3: Strategic Trigger Migration → **Opus**
- `evaluate_strategic_aggressive()` — HOLD triggers
- `evaluate_strategic_cautious()` — PURSUE, MOVE_TO, HOLD, SUPPORT triggers
- Replace `check_strategic_objection()` / `calculate_strategic_severity()`
- Preserve safe_path compromise at MODERATE+
- Preserve `pending_strategic_objection` field separation
- **RISK: Multi-system integration, many files touched**

### Unit 4: Main Pipeline Integration → **Opus**
- Wire V2 `evaluate_objection()` into `executor.py`
- Preserve return dict shape with backward compat
- MILD collection on `world.mild_concerns_this_turn`
- Per-marshal popup cap via `world.objection_popups_this_turn`
- Apply mood variance after evaluation
- Trust gain scaling on "trust" response
- Pass mild_concerns through main.py response
- **RISK: executor, disobedience, main.py, world_state all touched**

### Unit 5: Vindication Extension → **Sonnet**
- `pending_defensive_vindication` in VindicationTracker
- `to_dict()` / `from_dict()` with defaults
- Vindication decay (−1 per 3 turns no activity)
- Dead marshal cleanup
- Update SAVE_FORMAT_REFERENCE.md

### Unit 6: Test Migration → **Sonnet**
- Update `test_disobedience.py` for ConcernLevel
- Update `test_strategic_objections.py` — deterministic assertions
- New `test_objection_v2.py`
- Verify 1076+ tests pass

### Unit 7: Godot Frontend → **Sonnet**
- Tone-based styling in `objection_dialog.gd`
- MILD flavor in turn log
- Smoke test

**Code review checkpoints: After Unit 2, After Unit 4, After Unit 6.**

---

## Summary of All Changes from Original V2a Plan

| Item | Original Plan | Updated Decision |
|------|---------------|------------------|
| Global objection cap | "Max 1 MODERATE+ per marshal" (ambiguous) | Per-marshal only. No global cap. |
| Variance | "Deterministic triggers" | Deterministic base + 15-20% mood variance ±1 level |
| Compliance chance | Shown in popup | HIDDEN in V2a. Added in V2b with its own variance. |
| Trust gain | Not specified | Scaled: concern_level base × trust_tier multiplier |
| Balanced/Loyal triggers | Included in tables | SKIPPED. Only aggressive/cautious/literal for V2a. |
| MILD storage | Not specified | `world.mild_concerns_this_turn` list, cleared each turn |
| Trigger implementation | Not specified | Pure functions per personality (not dicts, not lambdas) |
| Strategic migration | "Not addressed" | Full replacement of severity-based strategic system |
| Authority in V2a | Not addressed | Explicitly inert. Documented. |
| 1.5:1 behavior change | Not acknowledged | Acknowledged as intentional improvement |

---

## Part 9: Post-Review Resolutions (Feb 5, 2026)

These answers were provided after the comprehensive code review and resolve all remaining implementation questions.

### Q1: MILD Return Dict Shape

**Question:** What exact fields should MILD return dict contain?

**Answer:** Drop legacy fields, use clean V2 shape:

```python
# MILD return dict — clean V2 shape
{
    "type": "mild_concern",
    "concern_level": "MILD",          # NEW: Always include
    "marshal": str,
    "message": str,
    "execute": True,                  # Order proceeds
    "popup": False,
}
```

**NOT included in MILD:**
- `severity` (no legacy float for MILD)
- `trust_change` (always 0 for MILD, don't bother including)
- `personality` (not needed, marshal name sufficient)
- `order` (not needed, order executes regardless)

### Q2: Strategic Evaluator Function Signatures

**Question:** What are the correct signatures for strategic evaluators?

**Answer:** Use explicit parameters, NOT `order.target`:

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
            return ConcernLevel.MILD
        ratio = _get_ratio_at_region(marshal, target, game_state)
        if ratio >= 3.0: return ConcernLevel.EXTREME
        if ratio >= 2.0: return ConcernLevel.STRONG
        return ConcernLevel.MODERATE
    return ConcernLevel.NONE

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

**Key change:** `order.target` was a typo in earlier drafts. Use explicit `target` parameter passed by caller.

### Q3: MODERATE+ Backward Compatibility

**Question:** Should MODERATE+ return dicts include `pending_objection: True`?

**Answer:** YES. Required for executor AP skip logic.

```python
# executor.py line ~987 checks this:
if result.get("pending_objection"):
    # Skip AP consumption — objection blocks execution
    pass

# Therefore MODERATE+ return dict MUST include:
{
    "pending_objection": True,   # CRITICAL for backward compat
    "type": "major_objection",
    "concern_level": "MODERATE",  # or STRONG, EXTREME
    # ... rest of fields
}
```

**MILD does NOT include `pending_objection`** because MILD doesn't block execution.

### Q4: Compromise Trust Gain

**Question:** Should compromise trust gain scale like trust?

**Answer:** NO. Keep compromise FLAT at +3 regardless of tier.

**Rationale:** Compromise is a "split the difference" option. It shouldn't be the optimal path at any trust level. Flat +3 keeps it as a reasonable middle ground without incentivizing "always compromise" strategies.

```python
def handle_response(response_type, marshal, concern_level, trust_tier):
    if response_type == "trust":
        return calculate_trust_gain(concern_level, trust_tier)  # Scaled
    elif response_type == "compromise":
        return 3  # Flat, always
    elif response_type == "insist":
        return get_insist_penalty(trust_tier)  # Scaled
```

### Q5: Severity Breakdown Migration

**Question:** What happens to `get_severity_breakdown()`?

**Answer:** REWRITE to return ConcernLevel-based breakdown:

```python
def get_concern_breakdown(marshal, action, game_state) -> dict:
    """
    Returns human-readable breakdown of how concern level was determined.
    For debugging and potential future UI display.
    """
    concern = evaluate_situation(marshal, action, game_state)

    return {
        "marshal": marshal.name,
        "personality": marshal.personality,
        "action": action,
        "base_concern": concern.name,
        "factors": _get_evaluation_factors(marshal, action, game_state),
        "final_concern": concern.name,
        # NO severity float — that's V1 legacy
    }

def _get_evaluation_factors(marshal, action, game_state) -> list:
    """Returns list of factors that influenced the evaluation."""
    factors = []

    if marshal.personality == "aggressive" and action in ("defend", "hold"):
        if _check_enemy_adjacent(marshal, game_state):
            ratio = _get_friendly_to_enemy_ratio(marshal, game_state)
            factors.append(f"enemy_adjacent: True, ratio: {ratio:.1f}")

    if marshal.personality == "cautious" and action == "attack":
        ratio = _get_enemy_to_friendly_ratio(marshal, game_state)
        factors.append(f"attack_risk_ratio: {ratio:.1f}")

    return factors
```

The old severity-based breakdown is DELETED. New function focuses on ConcernLevel reasoning.

### Q6: Concern Level in ALL Return Dicts

**Question:** Should `concern_level` appear in ALL objection return dicts?

**Answer:** YES. Every return dict from the V2 objection system includes `concern_level`:

| Return Type | Has `concern_level` | Value |
|-------------|---------------------|-------|
| MILD | ✅ | `"MILD"` |
| MODERATE popup | ✅ | `"MODERATE"` |
| STRONG popup | ✅ | `"STRONG"` |
| EXTREME popup | ✅ | `"EXTREME"` |
| No objection | ✅ | `"NONE"` |

```python
# Even "no objection" returns include concern_level
def evaluate_objection(marshal, action, game_state):
    concern = evaluate_situation(marshal, action, game_state)

    if concern == ConcernLevel.NONE:
        return {
            "type": "no_objection",
            "concern_level": "NONE",
            "execute": True,
        }
    # ... rest of logic
```

This makes the field universally available for logging, debugging, and future UI.

### Q7: Marshal Name Case Sensitivity

**Question:** Should marshal name matching in return dicts be case-sensitive?

**Answer:** Keep AS-IS. Marshal names are proper nouns (`"Ney"`, `"Davout"`), stored with consistent capitalization throughout the codebase. No case normalization needed.

The per-marshal tracking uses exact string match:
```python
if marshal.name in world.objection_popups_this_turn:
    # Exact match, case-sensitive
```

This is fine because `marshal.name` is always the canonical form.

### Additional Resolution: Test Migration Strategy

**Tests requiring structural rewrite (~8-10):**
1. Tests that assert specific severity float values (e.g., `assert severity == 0.72`)
2. Tests that check `severity_breakdown` dict shape
3. Tests that verify global objection cap behavior

**Tests requiring threshold updates (~10-15):**
1. Tests that expect popup at 1.5:1 ratio (now MILD)
2. Tests that check `compliance_chance` field (removed in V2a)
3. Tests that verify specific trust change values (now scaled)

**Approach:** Run full test suite after Unit 4 (pipeline integration). Fix failures incrementally. Most tests should pass unchanged because they test behavior, not implementation.

### Additional Resolution: Implementation Order Confirmation

**Confirmed order:**
1. Unit 1: Core Data Structures (Sonnet) — no dependencies
2. Unit 2: Trigger Evaluators (Sonnet) — depends on Unit 1
3. Unit 3: Strategic Migration (Opus) — depends on Unit 2
4. Unit 4: Pipeline Integration (Opus) — depends on Units 1-3
5. Unit 5: Vindication Extension (Sonnet) — parallel with Unit 4
6. Unit 6: Test Migration (Sonnet) — after Units 4-5
7. Unit 7: Godot Frontend (Sonnet) — after Unit 6

**Checkpoints:** Review after Unit 2, Unit 4, Unit 6.

### Additional Resolution: Regression Checklist

Before marking V2a complete, verify these 8 previously fixed bugs remain fixed:

| # | Bug | Test to Verify |
|---|-----|----------------|
| 1 | Command misattribution (interrupt router hijack) | `test_interrupt_router_other_marshal` |
| 2 | Forced retreat doesn't clear strategic orders | `test_forced_retreat_clears_hold` |
| 3 | Sally battles never reach frontend | `test_sally_combat_result_serializable` |
| 4 | Post-objection "Unknown action" | `test_post_objection_strategic_routing` |
| 5 | Contact interrupt infinite loop | `test_contact_interrupt_suppression` |
| 6 | Strategic objection "No pending" | `test_strategic_objection_stored_correctly` |
| 7 | Strategic objection AP consumed early | `test_strategic_objection_ap_deferred` |
| 8 | HOLD timed expiry nested incorrectly | `test_hold_max_turns_expires` |

Run these tests after Unit 4 integration to ensure V2a didn't regress any of them.

---

**This document + OBJECTION_V2_REFACTOR_PLAN.md = complete implementation spec for Claude Code.**
**No remaining ambiguities. No open questions. Build it.**
