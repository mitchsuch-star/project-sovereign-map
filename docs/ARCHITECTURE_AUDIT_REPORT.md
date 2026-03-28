# Architecture Audit Report

**Date:** 2026-03-27 (initial), 2026-03-27 (extended)
**Scope:** 12-pass holistic review + 35 deep dives + 6 extended audits (frontend, integration, game loop, error recovery, tests, modding)
**Approach:** 11 initial agents + 5 deep-dive agents + 7 verification/extension agents reading actual code
**Purpose:** Identify structural root causes of recurring bugs and propose refactoring roadmap that eliminates entire categories of audit findings
**Total individual findings:** 34 backend (2 CRITICAL, 9 MAJOR, 13 MODERATE, 12 LOW) + frontend/integration findings

---

## Executive Summary

Six previous audits found **~450 bugs**. This audit asks: **why do those bugs keep appearing?**

The answer is **10 structural root causes** — architectural patterns that generate bugs faster than audits can fix them. One-off bug fixes treat symptoms; the refactors below eliminate causes.

### Cross-Audit Bug Pattern Analysis

| Bug Category | Systems V1 | Systems V2 | Systems V3 | Deep Audit | Final | Diplomacy | **Total** | Root Cause |
|---|---|---|---|---|---|---|---|---|
| **Post-combat step missing** | 48 | 12 | 15 | 0 | 0 | 0 | **75** | RC-1 |
| **Missing validation / war-state** | 2 | 1 | 40+ | 2 | 2 | 2 | **49** | RC-2 |
| **Duplicate logic drift** | 10 | 12 | 15 | 1 | 0 | 0 | **38** | RC-1, RC-3 |
| **Serialization miss** | 2 | 4 | 10+ | 5 | 0 | 1 | **~22** | RC-5 |
| **Fog of war leak** | 5 | 1 | 2 | 6 | 2 | 2 | **18** | RC-6 |
| **Formula error** | 3 | 2 | 2 | 7 | 1 | 3 | **18** | — (irreducible) |
| **Edge case unhandled** | 2 | 2 | 2 | 5 | 1 | 3 | **15** | — (irreducible) |
| **Hardcoded value** | 2 | 2 | 1 | 3 | 0 | 4 | **12** | — |
| **Popup passthrough miss** | 0 | 1 | 1 | 2 | 1 | 4 | **9** | RC-4 |
| **Display name leak** | 0 | 0 | 3 | 0 | 0 | 3 | **6** | RC-9 |
| **Campaign log invisible** | 0 | 0 | 4 | 2 | 0 | 0 | **6** | RC-10 |
| **Cooldown/decrement bug** | 0 | 3 | 1 | 1 | 0 | 0 | **5** | RC-7 |
| **State cleared before use** | 1 | 0 | 1 | 0 | 0 | 0 | **2** | RC-7 |

**~240 of ~450 bugs trace to the 10 root causes below.** Fixing those root causes doesn't just fix 240 past bugs — it prevents the next 240.

### What's Working Well

The codebase scores highly on: import organization (9.5/10), type hints (9.5/10), error handling (9.5/10), magic number extraction (9/10), Golden Rule compliance (verified), zero circular dependencies, strong serialization enforcement. The problems are structural duplication and missing centralization, not code quality.

Extended audits cover 6 additional areas: Godot frontend architecture (main.gd god object, Layer 100 collision zone, signal inconsistency), backend↔frontend integration (no HTTP timeout, manual popup delivery), game loop (no crash recovery, non-atomic advance_turn), error recovery (8 try/except blocks in 14,797 lines), test infrastructure (2,460 lines duplicated factories, 5 missing enforcement tests), and modding system (~30% validator coverage, game-breaking mod scenarios unvalidated).

---

## Root Cause 1: Post-Combat Pipeline Duplication

**Bug category:** Post-combat step missing (75 findings), Duplicate logic drift (38 findings)
**Audits affected:** Systems V1, V2, V3 — the single most repeated finding across all audits

### The Problem

5 combat paths share 28 post-combat steps. Only `_execute_attack` has all 28. The other 4 paths implement 25-75% of the steps. Every audit finds "path X missing step Y."

### Completeness Matrix

| Step | attack | glorious_charge | garrison | bombardment | auto_bombard_kill |
|------|:------:|:---------------:|:--------:|:-----------:|:-----------------:|
| Clear coordination fields | ✓ | ✗ | ✗ | ✗ | ✓ |
| Log battle event | ✓ | ✓ | ✗ | ✓ | ✓ |
| Process notifications | ✓ | ✗ | ✗ | ✗ | ✗ |
| Relationship processing | ✓ | ✓ | ✗ | ✗ | ✓ |
| Re-pick observation | ✓ | ✗ | ✗ | ✗ | ✗ |
| Clear reinforcement orders | ✓ | ✗ | ✗ | ✗ | ✗ |
| Update intel from battle | ✓ | ✓ | ✓ | ✓ | ✓ |
| War damage to region | ✓ | ✓ | ✓ | ✗ | ✓ |
| Reset idle tracking | ✓ | ✓ | ✗ | ✓ | ✗ |
| Record for cannon fire | ✓ | ✓ | ✓ | ✓ | ✓ |
| Record for diplomacy | ✓ | ✓ | ✓ | ✗ | ✓ |
| Set last_combat_result | ✓ | ✗ | ✗ | ✗ | ✗ |
| Remove destroyed marshals | ✓ | ✓ | ✗ | ✗ | ✓ |
| Forced retreat handling | ✓ | ✓ | ✗ | ✗ | ✗ |
| Attacker movement/conquest | ✓ | ✓ | partial | ✗ | partial |
| Vindication system | ✓ | ✓ | ✗ | ✗ | ✗ |
| Authority victory/defeat | ✓ | ✓ | ✓ | ✗ | ✓ |
| Coalition threat/exhaustion | ✓ | ✓ | ✓ | ✗ | ✓ |
| Coordination tutorial | ✓ | ✗ | ✗ | ✗ | ✗ |
| Reinforcement trust penalties | ✓ | ✗ | ✗ | ✗ | ✗ |
| Exhaustion tracking | ✓ | ✓ | ✗ | ✓ | ✗ |

**Coverage rates:**
- `_execute_attack`: 26/28 (93%)
- `_execute_glorious_charge`: 10/28 (36%)
- `_resolve_garrison_combat`: 7/28 (25%)
- `_execute_bombardment`: 8/28 (29%)
- `auto_bombardment_kill`: 14/28 (50%)

### The Refactor: Unified Post-Combat Pipeline

```python
def _post_combat_pipeline(self, battle_result, attacker, defender, world, **context):
    """Single pipeline called by ALL combat paths after resolve_battle().

    Context flags control path-specific behavior:
      is_bombardment, is_garrison, is_glorious_charge, is_coordinated,
      conquered_region, reinforcers, etc.
    """
    # 1. Universal steps (always run)
    self._clear_coordination_fields(attacker, world)
    self._log_battle_event(battle_result, world)
    self._update_intel_from_battle(battle_result, world)
    self._record_for_diplomacy(battle_result, world)
    self._apply_post_combat_diplomacy(battle_result, world)  # RC-1b below
    self._process_authority(battle_result, world)

    # 2. Conditional steps (flag-gated, not path-duplicated)
    if not context.get('is_bombardment'):
        self._apply_war_damage(battle_result, world)
    if context.get('is_coordinated'):
        self._process_reinforcement_penalties(battle_result, world)
    if battle_result.get('defender_destroyed'):
        self._remove_destroyed_marshals(battle_result, world)
    # ... etc
```

**Why this works:** Adding a new post-combat step means adding it in ONE place. All 5 paths get it. The completeness matrix becomes 100% across all paths by construction.

**Estimated effort:** 1 session. ~400 new lines, ~600 removed (net -200). Low risk — each path already works, just consolidating.

### Sub-Refactor RC-1b: Post-Combat Diplomacy Unification

Three separate implementations of post-combat diplomacy exist (`_execute_attack`, `_execute_glorious_charge`, auto-bombardment kill). Each reimplements war score, threat, and exhaustion independently. This causes:

- **CRITICAL:** Auto-bombardment kill adds `decisive_victory` threat (+5) unconditionally — no casualty ratio check (executor.py:4597-4598)
- **CRITICAL:** Auto-bombardment kill inflates war score using full defender strength as casualties (executor.py:4581)
- **MAJOR:** Garrison combat has limited diplomacy wiring — calls `record_diplo_battle()` and coalition threat but missing vindication, relationship processing, idle reset, and several other post-combat steps (executor.py:2772+)

Extract `_apply_post_combat_diplomacy(battle_result, world)` as a shared function inside the pipeline.

### Sub-Refactor RC-1c: Solo vs Coordinated Path Merge

Two entirely separate post-combat paths exist (executor.py:4672-4810). Coordinated battles call `resolve_battle(apply_casualties=False)` then manually handle ~140 lines of post-combat effects. Solo battles handle everything inside `resolve_battle()`.

This has already caused:
- Pursuit damage floor 0 (coordinated) vs 1000 (solo) — coordinated pursuit can kill defenders; solo cannot
- `FORCED_RETREAT_THRESHOLD` duplicated as constant AND local variable
- Morale applied uniformly in coordinated path (1000-troop reinforcer gets same hit as 30000-troop primary)

---

## Root Cause 2: No Centralized War-State Filtering

**Bug category:** Missing validation (49 findings)
**Audits most affected:** Systems V3 (40+ bugs in one audit)

### The Problem

Actions that should be blocked during wartime (or allowed only during wartime) are checked with manual `nation !=` comparisons scattered across 50+ sites. Every new action or interaction path must independently remember to check war state. V3 found 40+ places that forgot.

### The Refactor: War-State Helper Layer

```python
# In world_state.py or a new helpers module
def is_at_war(self, nation_a, nation_b):
    """Single source of truth for war state between two nations."""
    key = tuple(sorted([nation_a, nation_b]))
    return self.diplomatic_states.get(key) == "WAR"

def get_hostile_marshals_in_region(self, region, nation):
    """Returns marshals in region that are at war with nation. Fog-filtered."""
    ...

def can_interact_diplomatically(self, nation_a, nation_b):
    """Checks if diplomatic actions are permitted between nations."""
    ...
```

Then replace 50+ manual checks with calls to these helpers. New code uses helpers by default — the correct check is the easy path.

**Estimated effort:** 1 session. Create helpers + migrate highest-churn call sites. Incremental adoption for rest.

### Sub-Refactor: Diplomatic State Change Centralization

5+ sites directly modify `diplomatic_states` without a centralized helper. Each site must independently handle `war_start_turns`, active treaty removal, and armistice cleanup. Extract `set_diplomatic_state(world, nation_a, nation_b, new_state)` to handle common bookkeeping.

---

## Root Cause 3: Executor God Object

**Bug category:** Duplicate logic drift, cognitive overload driving missed steps
**Scale:** 14,797 lines, 50 `_execute_*` methods, 40+ helpers in ONE class

### The Problem

When a developer needs to modify combat behavior, they must navigate a 14,797-line file to find the right method, understand its relationship to 4 other combat methods, and remember which helpers are shared vs local. This cognitive overload is a bug generator.

### Natural Module Boundaries

| Proposed Module | Methods | Est. Lines | Key Contents |
|----------------|---------|------------|--------------|
| `executor.py` (router) | 3 | ~1,500 | Router, guards, AP accounting |
| `combat_executor.py` | 9+13 helpers | ~2,500 | Attack, bombardment, coordination, casualties |
| `movement_executor.py` | 5+3 helpers | ~1,000 | Move, scout, retreat, attrition |
| `tactical_executor.py` | 7+2 helpers | ~900 | Fortify, drill, stance, square |
| `diplomatic_executor.py` | 10+11 helpers | ~2,000 | Proposals, dialogue state machine |
| `economy_executor.py` | 5 | ~400 | Recruit, build, repair |
| `strategic_executor.py` | 1+3 helpers | ~1,200 | Strategic orders, pathfinding |
| `objection_executor.py` | 7 | ~1,500 | Objection response, deferred execution |
| `capture_executor.py` | 6 | ~400 | Plunder vs secure, AI choice |
| `vassal_executor.py` | 4 | ~200 | Invest, autonomy, make, release |
| `meta_executor.py` | 5 | ~1,500 | End turn, help, debug, cheat |

### Cross-Cluster Dependencies

- **Objection system** is a crosscutter — can intercept ANY action. Needs callback pattern or stays in router.
- **Combat ↔ Movement** — forced retreat, movement attrition after combat.
- **Combat → Capture** — region ownership changes post-battle.
- **Coordination system** (13 helpers, 1,400 lines) — shared across all multi-marshal battles.

### The Refactor: 3-Phase Incremental Split

**Phase 1 (R6):** Extract utilities + combat executor. Reduces file from 14,797 to ~10,000 lines. Highest bug-rate domain moves first.
**Phase 2 (R7):** Extract diplomatic + strategic executors. Both are self-contained blocks.
**Phase 3 (R10):** Extract remaining domains. Each file under 2,500 lines.

**Prerequisite:** RC-1 (post-combat pipeline) should come first — it's easier to extract combat when the pipeline is already unified.

**Estimated effort:** 3 sessions across 3 phases. Move existing code + add import wiring. Medium risk — must verify all test paths still work.

---

## Root Cause 4: Ad-Hoc Response Pipeline

**Bug category:** Popup passthrough miss (9 findings), stale top-bar data
**Audits affected:** Systems V2, V3, Deep Audit, Final Audit, Diplomacy Audit — appeared in 5 of 6 audits

### The Problem

15 POST endpoints return different response shapes. There's no shared response builder. `_include_popup_passthroughs()` must be manually called in every response path — **37 "Bug 5" comments** in main.py mark spots where it was nearly forgotten on early returns.

Diplomatic top-bar fields (`diplomatic_points`, `max_diplomatic_points`, `threat_level`, `coalition_brewing`) only appear in the `/command` response. During objection/popup interactions, the top bar goes stale.

**Response shape comparison across endpoints:**

| Key | `/command` | `/respond_to_objection` | `/capture_choice` | `/respond_to_redemption` | `/cancel_order` |
|-----|:----------:|:-----------------------:|:------------------:|:------------------------:|:---------------:|
| `success` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `message` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `game_state` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `events` | ✓ | ✓ | ✓ | ✗ | ✗ |
| `diplomatic_points` | ✓ | ✗ | ✗ | ✗ | ✗ |
| `threat_level` | ✓ | ✗ | ✗ | ✗ | ✗ |
| `notifications` | conditional | conditional | ✗ | ✗ | ✗ |
| popup keys (7) | ✓ | ✓ | ✓ | ✓ | ✓ |

### The Refactor: Standard Response Builder

```python
def build_base_response(world, success=True, message="", **extra):
    """Every POST endpoint builds on this. Popups, diplomatic data,
    and game_state are ALWAYS included — can't be forgotten."""
    response = {
        "success": success,
        "message": message,
        "game_state": _serialize_game_state(world),
        "diplomatic_points": int(world.nation_dp.get(world.player_nation, 0)),
        "max_diplomatic_points": int(world.max_dp),
        "threat_level": int(getattr(world, 'france_threat', 0)),
        "coalition_brewing": getattr(world, 'coalition_brewing', False),
        "notifications": _get_notifications(world),
    }
    response.update(extra)
    _include_popup_passthroughs(response, world)  # Always called — structurally impossible to forget
    return response
```

All 15 POST endpoints call `build_base_response()`. Endpoint-specific fields passed as `**extra`. The popup passthrough is **structurally guaranteed** — it's inside the builder, not a manual call site.

**Estimated effort:** 1 session. ~150 new lines, refactor 13 endpoints. Medium risk — must verify Godot handles consistent response shape.

---

## Root Cause 5: No Shared Test Fixtures

**Bug category:** Serialization miss (22 findings), maintenance multiplier for all new fields
**Scale:** 203 test files, 121,290 lines, 0 conftest.py, 50+ duplicated `_make_world()` factories, 694 direct `Marshal()` instantiations

### The Problem

Adding ONE new field to Marshal requires updating `to_dict`, `from_dict`, AND ~184 test files that construct marshals directly. The serialization enforcement test catches the to_dict/from_dict miss, but the 184 test factories each construct Marshal with positional/keyword args that may or may not include the new field — causing test failures or silent defaults.

### Impact of Adding a New Marshal Field

| Approach | Files Changed | Time |
|----------|---------------|------|
| Without conftest | ~184 files, 50+ factories | 8-12 hours |
| With conftest | 4 locations | 1-2 hours |

### The Refactor: conftest.py with Factories

```python
# tests/conftest.py
class MarshalFactory:
    @staticmethod
    def infantry(name="TestInf", location="Paris", strength=30000, **overrides): ...
    @staticmethod
    def cavalry(name="TestCav", location="Paris", strength=8000, **overrides): ...
    @staticmethod
    def artillery(name="TestArt", location="Paris", strength=5000, **overrides): ...

class WorldFactory:
    @staticmethod
    def basic(**overrides): ...
    @staticmethod
    def with_marshals(marshal_list, **overrides): ...
    @staticmethod
    def diplomatic(**overrides): ...

@pytest.fixture
def world(): return WorldFactory.basic()
@pytest.fixture
def executor(): return CommandExecutor()
@pytest.fixture
def game_state(world): return {"world": world}
```

**Migration is fully incremental:** Create conftest.py (additive), new tests use fixtures, old tests keep working unchanged. Migrate high-churn files first over time.

**Estimated effort:** 2 hours to create. Zero risk — purely additive.

---

## Root Cause 6: Fog-of-War Filter Scatter

**Bug category:** Fog of war leak (18 findings)
**Audits affected:** ALL 6 audits — the most consistently recurring category

### The Problem

Fog filtering is implemented correctly in ~6 locations (intel_report.py, campaign_log.py, diplomatic_ledger.py, main.py tactical events, main.py LLM enemies). But every NEW code path that touches enemy data must independently remember to filter. 18 bugs across 6 audits prove this doesn't happen.

**Current leaks:**
- **MAJOR:** Strategic parser reveals fogged enemy positions via direction resolution (strategic_parser.py:88,577,610) — `get_enemies_of_nation()` returns ALL enemies omnisciently
- **MINOR:** map_data in LLM game state lists ALL marshals with NO fog check (main.py:88-98)

### The Refactor: Fog-Filtered Data Access Layer

Instead of requiring callers to filter, make the **default access path** fog-filtered:

```python
# In world_state.py
def get_visible_enemies(self, nation):
    """Returns enemies visible through fog. DEFAULT method for enemy queries."""
    return [m for m in self.get_enemies_of_nation(nation)
            if self.get_visibility(m.location, nation) >= PARTIAL]

def get_enemies_of_nation_omniscient(self, nation):
    """Returns ALL enemies. ONLY for use by combat resolution and save/load.
    Name makes the bypass explicit."""
    ...
```

Rename the current `get_enemies_of_nation` to `get_enemies_of_nation_omniscient`. Create `get_visible_enemies` as the new default. All callers that don't explicitly need omniscience use the filtered version. The name `_omniscient` makes bypasses visible in code review.

**Estimated effort:** 1 session. Rename + add filtered version + migrate callers. Low risk.

---

## Root Cause 7: Cooldown/Popup Field Sprawl

**Bug category:** Cooldown/decrement bug (5 findings), State cleared before use (2 findings), popup leaks
**Scale:** 14 cooldown dicts across 4 different decrement patterns, 7 popup fields with no unified queue

### The Problem: Cooldowns

14 cooldown dictionaries, decremented in 4 different ways:

| Pattern | Cooldowns Using It | Where |
|---------|-------------------|-------|
| Inline `-= 1` | `talleyrand_defiance_cooldown` | advance_turn |
| Dedicated helper method | `player_proposal_cooldowns`, `ai_proposal_cooldowns`, `proactive_suggestion_cooldowns`, `ultimatum_cooldowns` | advance_turn |
| External module call | `armistice_cooldowns`, `armistice_turns`, `coalition_cooldown`, `turns_below_threshold` | process_diplomacy_turn / process_coalition_turn |
| AI module call | `ai_failed_action_cooldowns`, `ai_refortify_cooldown` | turn_manager |

Adding a new cooldown requires knowing which pattern to follow. `_decrement_ai_proposal_cooldowns()` has a hidden side effect — it also expires queued proposals older than 3 turns (world_state.py:4573).

### The Problem: Popups

7 popup fields with no unified queue. Each popup type cleared manually. Popup leak bugs recur when new popup types are added without matching clear logic.

`pending_diplomatic_dialogue` alone has **76 SET operations** and **57 CLEAR operations** across the backend (see RC-8).

### The Refactor: CooldownManager + PopupQueue

```python
class CooldownManager:
    """Centralizes all cooldown dicts. One decrement_all() per turn."""
    def __init__(self):
        self._cooldowns = {}  # name -> {key: turns_remaining}

    def set(self, name, key, turns): ...
    def get(self, name, key): ...
    def decrement_all(self):
        """Called once in advance_turn. All cooldowns tick uniformly."""
        for cd in self._cooldowns.values():
            for key in list(cd):
                cd[key] -= 1
                if cd[key] <= 0:
                    del cd[key]

    def to_dict(self): ...  # Maintains save format via properties
    def from_dict(self, data): ...

class PopupQueue:
    """FIFO queue with priority. One check-and-pop per response."""
    def push(self, popup_type, data, priority=NORMAL): ...
    def pop(self): ...  # Returns highest-priority pending popup
    def clear_type(self, popup_type): ...
```

Both maintain save format compatibility via properties that map to the existing field names.

**Estimated effort:** 1 session. ~200 new lines, ~150 removed. Low risk — properties provide backward compatibility.

---

## Root Cause 8: Dialogue State Machine Chaos

**Bug category:** "Talleyrand awaiting" stuck state, dialogue overwrite
**Scale:** 66 SET operations, 44 CLEAR operations for `pending_diplomatic_dialogue`

### The Problem

`pending_diplomatic_dialogue` is a single-field overwrite with FIFO queue fallback. 66 scattered SET sites and 57 CLEAR sites make it impossible to verify that every SET has a matching CLEAR. The blocking guard (executor.py:1472) blocks ALL non-cheat commands while dialogue is pending. Dialogue responses are routed in main.py BEFORE the executor, bypassing the guard.

Risks:
- No queue cap — queue can grow unbounded
- Blocking dialogues have NO auto-clear — stuck indefinitely if player can't respond
- No audit trail of dialogue transitions

### The Refactor: DialogueManager

```python
class DialogueManager:
    """Centralizes all dialogue SET/CLEAR/QUEUE operations."""
    QUEUE_CAP = 20
    BLOCKING_TIMEOUT_TURNS = 3

    def push(self, dialogue_data, blocking=False): ...
    def pop(self): ...
    def is_blocking(self): ...
    def clear_stale(self, current_turn): ...
    def get_pending(self): ...
```

Reduces 76 SET sites to calls to `dialogue_manager.push()`. Reduces 57 CLEAR sites to calls to `dialogue_manager.pop()`. Adds queue cap, timeout, and audit trail.

**Estimated effort:** 1-2 sessions. ~200 new lines, refactor 80 sites. High risk — touches many code paths. Should come after RC-3 Phase 2 (diplomatic executor split) to reduce blast radius.

---

## Root Cause 9: Display Name Translation Gaps

**Bug category:** Display name leak (6 findings)
**Scale:** 7 display maps across the backend, 5 known gaps where raw internal names reach frontend

### The Problem

7 separate display maps translate internal names to UI-friendly text:

| Map | File | Purpose |
|-----|------|---------|
| `_ACTION_DISPLAY_NAMES` | executor.py:41 | Action verbs ("attack" → "attacks") |
| `PROPOSAL_TYPE_DISPLAY` | diplomatic_dialogue.py:81 | Proposal labels |
| `_STATE_DISPLAY_NAMES` | diplomacy.py:2459 | Formal state names |
| `_STATE_DISPLAY` | diplomatic_advisory.py:50 | Narrative state names |
| `_DEFIANCE_DISPLAY` | campaign_log.py:43 | Past tense actions |
| `_OBJECTION_DISPLAY` | campaign_log.py:21 | Gerund actions |
| `FEEDBACK_STRINGS` | diplomacy.py:138 | Acceptance formula components |

**5 gaps where raw internal names leak to frontend:**
1. `GET /diplomatic_states` returns raw "WAR"/"PEACE" — `_STATE_DISPLAY_NAMES` not applied
2. `GET /pending_objection` returns raw `original_order.action` — `_ACTION_DISPLAY_NAMES` not applied
3. `POST /respond_to_objection` returns raw defiance outcomes "failed_roll"/"right"/"wrong" — no display map exists
4. `POST /diplomatic_preview` returns raw action names in actions list
5. Personality/Stance enums returned as raw strings

**3 missing display maps:** `_DEFIANCE_OUTCOME_DISPLAY`, `_PERSONALITY_DISPLAY`, `_STANCE_DISPLAY`.

### The Refactor: Display Registry

Consolidate into a single `display_names.py` module:

```python
# backend/display_names.py
"""Single source of truth for all internal→display name translations."""

ACTION_DISPLAY = {"attack": "attacks", "move": "marches to", ...}
STATE_DISPLAY = {"WAR": "At War", "PEACE": "At Peace", ...}
DEFIANCE_OUTCOME_DISPLAY = {"failed_roll": "Failed", "right": "Vindicated", ...}
# ... all 7+ maps in one place

def display(category, internal_name, fallback=None):
    """Universal translator. Never returns raw internal name."""
    maps = {ACTION: ACTION_DISPLAY, STATE: STATE_DISPLAY, ...}
    return maps[category].get(internal_name, fallback or internal_name.replace("_", " ").title())
```

All endpoints call `display()` before returning user-facing strings. The fallback auto-formats unknown keys (Title Case with underscores removed) so new values are never completely raw.

**Estimated effort:** Half session. Low risk.

---

## Root Cause 10: Campaign Log Silent Drop

**Bug category:** Campaign log invisible (6 findings)
**Scale:** 40+ event types logged, 36 whitelisted (expanded from 24 during prior audits), remaining types invisible

### The Problem

`CAMPAIGN_LOG_TYPES` is a whitelist set (campaign_log.py:83-120). Events not in the whitelist are **silently dropped** — no error, no warning, no test. Triple-layer silent failure: whitelist drops unknown types, format function falls through to generic text, category map defaults to "unknown".

**16 invisible event types include:**
- `ai_proposal_accepted/rejected/counter_failed` — player gets zero log feedback on diplomatic proposals
- `coalition_brewing_started/cancelled` — coalition lifecycle invisible
- `relationship_change` — win/loss relationship effects invisible
- `diplomatic_mission_started` — mission actions invisible
- `garrison_placed` — enemy garrison placements invisible

### The Refactor: Compile-Time Whitelist Enforcement

```python
# Add test that compares all log_event() type strings against CAMPAIGN_LOG_TYPES
def test_all_event_types_whitelisted():
    """Every event type used in world.log_event() must be in CAMPAIGN_LOG_TYPES."""
    logged_types = set()  # grep all log_event("type_name" calls
    for type_name in logged_types:
        assert type_name in CAMPAIGN_LOG_TYPES, \
            f"Event type '{type_name}' is logged but not whitelisted — invisible to players"
```

Plus: add the 16 missing types with format strings and fog rules. Add duplicate event type consolidation (`diplomatic_war_declared` + `war_declaration` → one type).

**Estimated effort:** Half session. Zero risk.

---

## Scaling Concerns (Pre-80-Region Expansion)

These aren't recurring bug patterns but architectural limits that will break at scale.

### Risk Matrix

| System | Current (19 regions) | At 80 Regions | Risk |
|--------|---------------------|---------------|------|
| **Visibility calc** | 10-15ms | 80-150ms | CRITICAL |
| **AI strategic decisions** | 30-50ms | 150-250ms | CRITICAL |
| **Supply attrition** | 2-3ms | 20-25ms | MAJOR |
| **Income phase** | 5-10ms | 40-60ms | MAJOR |
| **Serialization** | 46KB/7ms | 160KB/25ms | MAJOR |
| **Total turn time** | 80-120ms | **400-600ms** | **MAJOR** |

### Scaling Refactor A: Marshal-by-Region Index

Build `marshals_by_region` inverse index once per turn start. This single change fixes visibility calc, supply attrition, and income phase — all from O(R×M) to O(R+M).

```python
# Built once at turn start
marshals_by_region = {}
for m in self.marshals.values():
    marshals_by_region.setdefault(m.location, []).append(m)
```

**Estimated effort:** Half session. ~50 new lines, modify 3 methods. Zero behavior change.

### Scaling Refactor B: AI Fog Integration

Enemy AI does NOT respect fog of war. `enemy_ai.py:3354` calls `world.get_enemies_of_nation(nation)` which returns ALL enemy marshals globally. At 80 regions this produces unfair all-knowing AI AND worse performance.

**Estimated effort:** 4-6 days. Modify 10-12 methods. High risk — changes AI behavior significantly. Needs playtesting.

---

## Additional Architectural Observations

### WorldState Field Sprawl (Pass 3)

92 persistent fields grouped by domain:

| Domain | Fields | % | Trend |
|--------|--------|---|-------|
| Diplomacy | 29 | 31.5% | Growing |
| Coalition | 9 | 9.8% | Growing |
| Popups/UI | 9 | 9.8% | Growing |
| Disobedience | 9 | 9.8% | Stable |
| Enemy AI | 8 | 8.7% | Stable |
| Core | 7 | 7.6% | Stable |
| Action Economy | 5 | 5.4% | Stable |
| Vassal | 5 | 5.4% | Stable |
| Combat | 4 | 4.3% | Stable |
| Economy | 3 | 3.3% | Stable |

The `pending_*` field lifecycle is the main risk (see RC-7, RC-8). The field count itself is manageable.

### `advance_turn` Pipeline (Pass 3)

383 lines, 48 sequential operations, 25+ already delegated to external functions. Turn counter increment at step 13 splits the pipeline — steps 1-12 see old turn, steps 14+ see new turn. 5+ ordering dependencies documented only by inline comments.

**Not a refactor target** — the delegation is already good. Needs better documentation of ordering constraints.

### Enemy AI Structure (Pass 4)

5,561 lines, 74 methods. P0-P8 priority system well-documented and correctly implemented. **Golden Rule #5 verified: FULLY COMPLIANT** — all actions go through executor. Split would reduce cognitive load ~20-30% but add composition overhead. Worth doing only if planning 2+ years of maintenance.

### Module Dependency Graph (Pass 6)

**Zero circular dependencies.** Expected layer structure holds: `models → game_logic → commands → ai → main`. One minor layer violation: `world_state.py` (models) imports from `disobedience.py` and `vindication.py` (commands layer).

### Serialization Architecture (Pass 9)

Round-trip fidelity: EXCELLENT. Backward compatibility: STRONG. Enforcement test: comprehensive. **Do NOT migrate to dataclasses/Pydantic** — cost >> benefit.

### Code Conventions (Pass 10)

| Dimension | Score |
|-----------|-------|
| Error handling | 9.5/10 |
| Import organization | 9.5/10 |
| Type hints | 9.5/10 |
| Magic numbers | 9/10 |
| Naming conventions | 8/10 |
| Docstrings/comments | 8/10 |
| Logging | 6/10 — mix of print/debug_print/ai_debug/logging |

---

## Refactoring Roadmap

### Priority-Ordered Sessions

| Priority | Session | Root Cause | Severity | Effort | Bugs Prevented |
|----------|---------|------------|----------|--------|----------------|
| 1 | **R1** Post-combat pipeline unification | RC-1 | CRITICAL | 1 session | ~75 recurring |
| 2 | **R2** War-state helper layer | RC-2 | CRITICAL | 1 session | ~49 recurring |
| 3 | **R3** Test conftest.py | RC-5 | CRITICAL | 2 hours | ~22 + maintenance multiplier |
| 4 | **R4** Response pipeline standardization | RC-4 | MAJOR | 1 session | ~9 + stale top-bar |
| 5 | **R5** Fog-filtered data access | RC-6 | MAJOR | 1 session | ~18 recurring |
| 6 | **R6** CooldownManager + PopupQueue | RC-7 | MAJOR | 1 session | ~7 + popup leaks |
| 7 | **R7** Display name registry | RC-9 | MODERATE | ½ session | ~6 + future leaks |
| 8 | **R8** Campaign log enforcement test | RC-10 | MODERATE | ½ session | ~6 + silent drops |
| 9 | **R9** Scaling index | Scaling A | CRITICAL (pre-80) | ½ session | performance |
| 10 | **R10** Executor split Phase 1 (combat) | RC-3 | MAJOR | 1 session | cognitive load |
| 11 | **R11** Executor split Phase 2 (diplomatic) | RC-3 | MAJOR | 1 session | cognitive load |
| 12 | **R12** DialogueManager | RC-8 | MAJOR | 1-2 sessions | stuck dialogue |
| 13 | **R13** Executor split Phase 3 (remaining) | RC-3 | MINOR | 1 session | cognitive load |
| 14 | **R14** AI fog integration | Scaling B | CRITICAL (pre-80) | 4-6 days | balance + perf |
| 15 | **R15** Godot: Extract utils.gd + PopupBase class | Frontend | MAJOR | 1 session | signal consistency + 250 lines dedup |
| 16 | **R16** Godot: Dialog manager + Layer 100 subdivision | Frontend | MAJOR | 1 session | collision zone + main.gd -280 lines |
| 17 | **R17** Godot: HTTP timeout + api_client consolidation | Integration | CRITICAL | ½ session | infinite hang prevention |
| 18 | **R18** Test enforcement suite (5 new enforcement tests) | Tests | MAJOR | ½ session | ~18 bugs prevented per category |
| 19 | **R19** Modding validator extension (diplomatic/vassal/coalition) | Modding | MAJOR | 1 session | game-breaking mod scenarios |
| 20 | **R20** advance_turn idempotency guard | Game Loop | MAJOR | ½ session | double-processing prevention |

### Dependency Graph

```
R1 (post-combat pipeline) ──→ R10 (executor split: combat)
R2 (war-state helpers)                    ↓
R3 (conftest.py)             R11 (executor split: diplomatic)
R4 (response pipeline)                    ↓
R5 (fog-filtered access)    R12 (dialogue manager)
R6 (cooldown/popup)                       ↓
R7 (display registry)       R13 (executor split: remaining)
R8 (campaign log test)
R9 (scaling index) ──→ R14 (AI fog)
```

**R1-R9, R15-R20 are fully independent** — can be done in any order or in parallel.
**R10-R13 are sequential** (each split phase depends on the previous).
**R14 depends on R9** (scaling index needed for AI fog).
**R15-R16** (Godot) are independent of all backend sessions.
**R17** (HTTP timeout) should be done early — prevents hung client.

### Estimated Total Effort

| Phase | Sessions | What |
|-------|----------|------|
| **Phase A** (independent, any order) | 6-7 sessions | R1-R9 (backend root causes) |
| **Phase B** (sequential) | 3-4 sessions | R10-R13 (executor split) |
| **Phase C** (pre-80-region) | 4-6 days | R14 (AI fog) |
| **Phase D** (frontend, independent) | 2-3 sessions | R15-R17 (Godot + integration) |
| **Phase E** (infrastructure, independent) | 1-2 sessions | R18-R20 (tests, modding, game loop) |

---

## Architecture Principles

Distilled from all 12 passes + 35 deep dives + cross-audit analysis:

1. **One combat pipeline, many entry points.** All combat paths must call the same post-combat pipeline. Path-specific behavior uses context flags, not code duplication.

2. **The correct check must be the easy path.** War-state filtering, fog filtering, and display name translation should be the DEFAULT method. Bypasses should require explicitly-named methods (`_omniscient`, `_raw`).

3. **Shared test fixtures are infrastructure, not nice-to-have.** Every new field multiplied by 184 test files is a maintenance tax. conftest.py is the tax exemption.

4. **Response shape is a contract.** Backend and frontend must agree on response structure. Use a builder function, not ad-hoc dict construction per endpoint.

5. **Cooldowns and popup queues are patterns, not fields.** When you have 14 dicts that all decrement by 1 per turn, that's a `CooldownManager`. When you have 7 optional popup fields that each need set/read/clear, that's a `PopupQueue`.

6. **Index once, lookup many.** Build `marshals_by_region` and `regions_by_nation` caches at turn start. O(N) build cost saves O(N²) across 10+ consumers.

7. **AI must respect the same constraints as the player.** Fog of war applies to decisions, not just display. An omniscient AI is a bug, not a feature.

8. **Mutation flows downward.** main.py orchestrates, executor.py mutates, game_logic modules transform. Never mutate state in main.py. Never call main.py from executor.

9. **Pending fields have lifecycles.** Every `pending_*` field must have documented SET → READ → CLEAR sites. If a field has 30+ SET sites, it needs a manager object.

10. **Extract for bugs, not for beauty.** The post-combat pipeline extraction prevents 75 recurring bugs. The enemy AI split just improves readability. Prioritize accordingly.

---

## What NOT to Refactor

These look messy but should be left alone:

1. **WorldState as a single object** — 92 fields is manageable. Splitting into `DiplomacyLayer`, `CoalitionState`, etc. would touch hundreds of call sites for marginal benefit. Fields are well-organized, serialization is enforced, advance_turn delegates properly.

2. **The P0-P8 priority system in enemy_ai.py** — The 622-line `_evaluate_marshal()` is long but linear — not complex. Breaking it apart would scatter priority order across files.

3. **Dict-based error returns** — `{"success": False, "message": "..."}` is consistent, deterministic, and well-integrated. Replacing with exceptions would rewrite 50 methods for no gain.

4. **Inline documentation in `_execute_help()`** — 1,302 lines of help text living with the code it describes. Extracting creates drift.

5. **Multiple small test files** — 203 files averaging 600 lines is preferable to 20 large files.

6. **`_include_popup_passthroughs()` architecture** — Ugly but correct for a local single-player game. R4 makes it structurally impossible to forget, not architecturally different.

7. **Serialization via manual to_dict/from_dict** — The enforcement test is strong. Pydantic/dataclass migration cost exceeds benefit.

---

## Appendix: All Individual Findings

### CRITICAL (2)

| # | Finding | Location |
|---|---------|----------|
| 1 | Auto-bombardment kill adds decisive_victory threat unconditionally (+5 every kill) | executor.py:4597-4598 |
| 2 | Auto-bombardment kill inflates war score using full defender strength as casualties | executor.py:4581 |

### MAJOR (9)

| # | Finding | Location |
|---|---------|----------|
| 3 | Garrison combat has limited diplomacy wiring (missing vindication, relationships, idle reset) | executor.py:2772+ |
| 4 | Strategic parser leaks fogged enemy positions via direction resolution | strategic_parser.py:88,577,610 |
| 5 | No base response type — diplomatic top-bar fields missing from popup endpoints | main.py (13 endpoints) |
| 6 | Trust/authority death spiral — double-modified trust gains, asymmetric recovery | authority.py, defiance.py |
| 7 | Combat modifier chain — snapshot drifts from actual calculation | battle_report.py vs marshal.py |
| 8 | Three separate post-combat diplomacy implementations | executor.py (3 locations) |
| 9 | ~140 lines duplicated post-combat logic (solo vs coordinated) | executor.py:4672-4810 |

### MODERATE (13)

| # | Finding | Location |
|---|---------|----------|
| 10 | Pursuit damage floor 0 (coordinated) vs 1000 (solo) | executor.py:4788 vs combat.py:694 |
| 11 | 14 cooldown dicts across 4 decrement patterns | world_state.py |
| 12 | 44-step turn pipeline with 5+ undocumented ordering dependencies | world_state.py:3622-4005 |
| 13 | 16 campaign log event types invisible | campaign_log.py:83-120 |
| 14 | War score decay value manipulation is dead code | diplomacy.py:419-438 |
| 15 | Capital capture blocks all AI proposals (diplomatic deadlock) | ai_diplomacy.py:604-610 |
| 16 | Diplomatic state machine has 5+ direct modification sites | diplomacy.py |
| 17 | Recklessness preserved through army break/respawn | marshal.py:525-551 |
| 18 | Reinforcer retreat bypasses move_to() | executor.py:5028 |
| 19 | Dead backward-compat code in objection system | objection_v2.py:120-126 |
| 20 | Save/load no schema validation, manual transient field list | save_manager.py |
| 21 | Mock parser keyword ordering fragile (~150-line elif chain) | llm_client.py:650-800 |
| 22 | LLM fallback threshold prevents borderline commands from reaching LLM | llm_client.py:48 |

### LOW (12)

| # | Finding | Location |
|---|---------|----------|
| 23 | Fixed AI nation order (Britain first-mover advantage) | turn_manager.py:584 |
| 24 | Notification lifecycle: no expiry, no dedup, unbounded HIGH | notifications.py |
| 25 | build_active_wars double computation per request | main.py |
| 26 | ARMISTICE_DURATION hardcoded cross-file | war_status.py:5 |
| 27 | Vassal garrison loyalty docstring mismatch (+2 vs +5 base) | vassal.py:228 vs 255 |
| 28 | Duplicate event types: diplomatic_war_declared + war_declaration | campaign_log.py |
| 29 | BALANCED/LOYAL personalities unimplemented | personality_modifiers.py |
| 30 | map_data fog leak in LLM game state | main.py:88-98 |
| 31 | Dispatch hardcoded "France" player_nation | dispatch.py:51 |
| 32 | Battle report re-pick priorities favor coordination over mutual destruction | battle_report.py:561-602 |
| 33 | Region name substring matching without word boundaries | llm_client.py:834-871 |
| 34 | Talleyrand turn_number fallback to non-existent field | diplomatic_defiance.py:493,612 |

### Deep Dive Findings (Pass 12+)

#### Combat Pipeline Deep Dives

**13a: Combat Modifier Chain** — Golden Rule #1 partial violation. combat.py:383-403 applies cavalry-vs-artillery +30%, square formation -40%/+50%, and cavalry terrain adjustments directly in `resolve_battle()`, NOT in `get_attack_modifier()`. `get_attack_modifier()` has consume-on-read side effects (zeroes `strategic_combat_bonus` and `counter_punch_ready`) with no double-call guard. Battle report snapshot (`snapshot_attacker_modifiers`) re-derives modifiers independently — if new modifier added to one but not other, they drift. Defense cap 1.75x not reflected in snapshot.

**13b: Casualty Distribution** — Two separate post-combat paths for solo vs coordinated (executor.py:4672-4810). Pursuit damage floor inconsistency. `_get_casualty_participants` near-duplicates `get_battle_participants` in relationship.py.

**13c: Battle Report Generation** — Double observation generation (combat.py:833 creates initial, executor.py:4913-4916 re-picks). Bombardment path skips battle_report entirely.

**13d: Forced Retreat** — Recklessness preserved through army break/respawn. Reinforcer retreat bypasses `move_to()` (direct location assignment). Broken army teleportation has no attrition (intentional but undocumented).

**13e: Combat → Diplomacy Interaction** — Three separate implementations of post-combat diplomacy. Auto-bombardment decisive_victory unconditional. War score inflation. Garrison zero wiring. Authority simplified in bombardment path.

#### Diplomacy Engine Deep Dives

**14a: State Machine** — Asymmetric upgrade vs downgrade (fast build, slow dismantle). ARMISTICE has no voluntary exit. War cascade bypasses relation penalties. 5+ sites directly modify `diplomatic_states`.

**14b: Acceptance Formula** — Well-tested (145+ tests). Diplomat skill bonus uncapped upward (Talleyrand +12 permanent). Sweetener cap at 60 but demands uncapped.

**14c: AI Decision-Making** — Exploitable priority order. Stalemate counter easily reset. Capital capture blocks all AI proposals. P8 harsh demands self-defeating.

**14d: Coalition Lifecycle** — Brewing oscillation exploit partially mitigated. War exhaustion self-limiting at ~19 turns. Member friction damages post-coalition relations.

**14e: War Score** — Territory score position-based (not cumulative). War score decay value manipulation is dead code. Decisive battle cap of 2 per war.

**14f: Talleyrand Sabotage** — Cooldown fully suppresses defiance (contradicts "never fully tamed"). Sabotage type selection deterministic. Discovery reaches 100% by turn 6.

#### Turn Processing Deep Dives

**15a: Turn Processing Order** — 44 steps, turn counter increment at step 13 splits pipeline. 5+ ordering dependencies documented only by inline comments. Victory check runs before enemy phase but advance_turn still runs in game-over state.

**15b: Action Economy** — Clean dual-pool design. No issues.

**15c: Enemy AI Turn Processing** — Fixed nation order (Britain always first). New EnemyAI() created each turn. Three safety valves prevent infinite loops.

**15d: Strategic Order Execution** — Clean two-pass system. No changes needed.

**15e: Supply Attrition** — Clean formula. 0-strength elimination is permanent (harsher than combat broken state).

**15f: Manpower Regeneration** — Clean single-source. Nations missing from `DEFAULT_MANPOWER_POOLS` silently skipped.

**15g: Cooldown Management** — 14 dictionaries, 4 patterns (detailed in RC-7 above).

**15h: Morning Dispatch** — Correct timing. "France" hardcoded. Dispatch event whitelist has same silent-drop pattern as campaign log.

#### Fog/Intel/Parsing Deep Dives

**16a: Fog Consistency** — Strategic parser fog leak (MAJOR). map_data fog leak (MINOR). Fog filtering correct in 6 other locations. Campaign log uses current visibility, not event-time.

**16b: Intel System** — Clean dual-path design. No changes needed.

**16c: Mock Parser** — 37 VALID_ACTIONS but mock handles ~30 paths. Confidence threshold prevents LLM fallback for borderline commands.

**16d: Command Parsing** — Keyword ordering fragile. "hold" always becomes strategic. Possessive form breaks matching.

**16e: Vassal System** — 7-modifier loyalty formula. Garrison loyalty docstring mismatch. Battle result matching uses fragile string parsing.

**16f: Campaign Log Extended** — 40 logged, 24 whitelisted, 16 invisible. Duplicate `diplomatic_war_declared` + `war_declaration`.

**16g: LLM Prompt** — Clean prompt builder. No diplomatic few-shot examples.

#### API/Trust/Objection Deep Dives

**17a: API Endpoints** — 35 endpoints (13 POST, 22 GET). No error handling on most GETs. Mixed async/sync handlers.

**17b: Trust/Authority/Vindication** — Death spiral potential with double-modified trust gains. Authority asymmetry (-5 per defiance, +1/turn recovery). Vindication cap makes scores above +3 marginal.

**17c: Objection Layers** — V1 CONCERN_TO_SEVERITY dead code. V1 literal triggers empty/TODO. Defiance uses hardcoded personality strings instead of enum.

**17d: Personality System** — Personality stored as string, not enum. BALANCED/LOYAL unimplemented. Modifier lookup by name, not marshal (second aggressive marshal gets Ney-specific labels).

**17e: Save/Load** — No schema validation on load. Hard version break v1→v2 only. Transient state clearing hardcoded.

**17f: Notification Lifecycle** — HIGH/CRITICAL accumulate without limit. No deduplication. No expiry.

**17g: War Status Panel** — `build_active_wars` called twice per response. ARMISTICE_DURATION hardcoded cross-file.

**17h: Response Shape Analysis** — Diplomatic top-bar fields only in `/command` — stale during popup interactions (detailed in RC-4).

---

## Extended Audit: Godot Frontend Architecture

**Rating: NEEDS REFACTORING** — Playable but architecturally fragile. High coupling to main.gd; scattered responsibilities; implicit contracts.

### File Inventory (30 GDScript files, ~10,140 LOC)

| File | Lines | Category | Status |
|------|-------|----------|--------|
| main.gd | 3,175 | Core Controller | **GOD OBJECT** |
| diplomatic_ledger.gd | 758 | Screen (Layer 50) | Growing |
| strategic_ledger.gd | 588 | Screen (Layer 50) | Healthy |
| diplomacy_wizard.gd | 538 | Modal Wizard (Layer 100) | Healthy |
| war_detail_popup.gd | 427 | Popup (Layer 30) | Healthy |
| enemy_phase_dialog.gd | 411 | Dialog (Layer 100) | Healthy |
| marshal_management.gd | 379 | Screen (Layer 50) | Healthy |
| api_client.gd | 347 | HTTP Client | **REPETITIVE** |
| top_bar.gd | 307 | Controller (Layer 75) | Healthy |
| war_status_panel.gd | 304 | HUD (Layer 25) | Healthy |
| 16 small popups | 67-185 each | Modal Dialogs (Layer 100) | Healthy |

### CanvasLayer Stacking — ARCHITECTURAL DEBT

| Layer | Count | Scripts |
|-------|-------|---------|
| 25 | 1 | war_status_panel (HUD always-visible) |
| 30 | 1 | war_detail_popup (above HUD) |
| 50 | 5 | campaign_log, dispatch_view, strategic_ledger, marshal_management, diplomatic_ledger |
| 75 | 1 | top_bar (button bar) |
| **100** | **11** | **ALL modal popups — NO depth ordering, collision zone** |
| 101 | 1 | pause_menu (top-level modal) |

**11 popups at Layer 100 with no depth ordering.** If two fire simultaneously, last added to scene tree wins. Backend logic provides mutual exclusion (only one popup per response), but no rendering-level safety.

### Signal Architecture — NEEDS WORK

Inconsistent signal interfaces across popups:
- `choice_made(String)` — objection, redemption, glorious_charge
- `choice_made(String, Dictionary)` — incoming_proposal, sabotage, talleyrand, vassal_rebellion
- `dismissed()` — coalition_declaration, strategic_report
- `negotiate_clicked(nation)` / `target_clicked(nation)` — war_detail_popup

No base popup class. 20+ manual `.connect()` calls in main.gd `_ready()`. No centralized signal registry.

### Code Duplication

- **Color palettes duplicated 5x** across main.gd, dispatch_view.gd, strategic_ledger.gd, marshal_management.gd, diplomatic_ledger.gd (~50 lines copy-paste, comments say "duplicated from main.gd")
- **HTTP boilerplate duplicated 16x** in api_client.gd (identical request wrapper pattern)
- **Tab switching boilerplate** duplicated between strategic_ledger and diplomatic_ledger
- **Dialog instantiation** repeated 20x in main.gd `_ready()` (load scene, instantiate, add_child, connect signal)

### Input Handling — NEEDS WORK

Hotkeys scattered across 7 files with 3 different guard functions:
- `_is_modal_dialog_open()` — checks objection/redemption/pause
- `_is_hotkey_blocked()` — checks pause/text input (doesn't check wizards)
- `_is_screen_open()` — checks top_bar state

Guard logic is duplicated and inconsistent. No centralized hotkey registry or input map.

### State Management — NEEDS WORK

Game state exists in 4 places simultaneously:
- main.gd local variables (turn, actions, gold)
- Response dicts (stored in `pending_*` fields)
- `_last_command_response` cache (workaround for war panel refresh)
- Each screen's own `cached_data` dict

No single source of truth. No refresh strategy when modals close. Implicit mutual exclusion for popups (backend guarantees only one is true per response; no rendering-time guard).

### Frontend Refactoring Roadmap

| Session | What | Impact |
|---------|------|--------|
| F1 | Extract `utils.gd` (shared colors, formatting) | 50+ duplicated lines removed |
| F2 | Create base `PopupBase` class; standardize signal interface | Signal consistency across 18 popups |
| F3 | Create `dialog_manager.gd`; factory + queue pattern | main.gd lines 140-420 removed |
| F4 | Centralize input handling; unified guard function | Scatter reduced by 80% |
| F5 | Sub-divide Layer 100 into 100-109 for popup depth | Collision zone eliminated |
| F6 | Consolidate api_client.gd into 2-3 generic helpers | 200+ boilerplate lines removed |

---

## Extended Audit: Backend↔Frontend Integration

**Rating: ADEQUATE** — Functional and reasonably defensive, but relies on developer discipline.

### API Contract

**Implicit — no formal documentation.** Contract is inferred from code patterns:
- Godot expects response dict with `success` bool, optional popup keys, `game_state` with `map_data`
- Backend `_include_popup_passthroughs()` ensures all popup keys are always present (None if not set)
- All numeric values wrapped in `int()` (Golden Rule #2)
- No schema validation on either side

### Communication Model

**Synchronous request-response with single-request-in-flight guard:**
- api_client.gd: `_request_in_flight` flag prevents concurrent requests
- No polling, no long-polling, no WebSocket
- UI blocks on every network request (intentional — prevents double-taps)
- Diplomacy wizard has its own dedicated HTTPRequest to avoid ERR_BUSY conflicts

### Error Handling

| Error | Detection | Recovery | Status |
|-------|-----------|----------|--------|
| 500 error | response_code != 200 | Display error, retry | WORKING |
| Network down | HTTPRequest error | Display error, retry | WORKING |
| Malformed JSON | JSON.parse fails | Error callback | WORKING |
| **Server timeout** | **None — indefinite hang** | **Manual restart** | **BROKEN** |
| Missing popup key | .has() check | Silent skip | WORKING |

**CRITICAL: No timeout mechanism.** If server hangs, Godot hangs indefinitely. `_request_in_flight` never clears. All subsequent requests fail with "Request already in progress."

### Popup Delivery Chain

```
executor.py sets popup on world
  → main.py _include_popup_passthroughs() extracts ONE popup (priority-ordered)
  → api_client.gd passes response to callback
  → main.gd _on_command_result() checks 16+ popup keys in sequence
  → popup script displays data
```

**Data loss points:**
1. Endpoint missing `_include_popup_passthroughs()` call → popup silently lost (the "Bug 5" pattern, 37 references in main.py)
2. Enemy phase modal blocks popup delivery → deferred until next request
3. Multiple popups queued but only one delivered per response cycle (by design — others persist on world)

### Reconnection

**No reconnection support.** If server restarts mid-game:
- Godot detects on next request attempt (passive detection)
- No session tracking — can't detect which commands executed before crash
- No heartbeat or background ping
- Recovery: User manually reloads from autosave

### Recommendations

1. **CRITICAL:** Add HTTP request timeout (10s) with error callback
2. **MAJOR:** Add `_include_popup_passthroughs()` enforcement (decorator or lint rule)
3. **MAJOR:** Add `api_version` field to responses for frontend/backend version mismatch detection

---

## Extended Audit: Game Loop Architecture

**Rating: HAS GAPS** — Sound in design but lacking crash recovery and atomicity.

### Complete Turn Cycle

```
Player types "end turn"
  → executor._execute_end_turn()
    → turn_manager.end_turn()
      → Pre-enemy VICTORY CHECK
      → ENEMY PHASE: Each AI nation gets action budget via same executor
      → AI DIPLOMATIC PHASE: P1-P7 proposal triggers, vassal courting
      → STRATEGIC ORDER EXECUTION: Multi-turn orders, can trigger combat
      → world.advance_turn() — 48 sequential steps:
          [A] Clear per-turn flags
          [B] Process tactical states (drill/fortify/retreat)
          [C] Vindication decay
          [D] Construction timers
          [E] **TURN COUNTER INCREMENTS** (steps above see old turn, below see new)
          [F-I] Stability, supply attrition, garrison regen, bankruptcy
          [J-K] Diplomacy processing, proposal resolution
          [L-M] Cooldown decrements, Talleyrand defiance
          [N-O] Vassal processing, **clear battle tracking** (AFTER vassals read it)
          [P-Q] Coalition processing, AI-AI diplomacy
          [R-S] Dialogue auto-dismiss, blocking safety valve
          [T-W] Income, trade, treaty clauses, vassal tribute
          [X-Y] Bankruptcy check (after all income), manpower regen
          [Z] **AP RESET** (after treaty clause penalties)
          [AA-BB] Utility resets, **FOG RECALCULATION** (final step)
      → Pop dialogue queue (priority-ordered)
      → Post-advance VICTORY CHECK (3rd checkpoint)
    → Filter tactical events by fog
    → Build financial summary
  → Response sent to Godot
```

### Critical Timing Dependencies

1. **Turn counter increment at step E** splits the pipeline — steps A-D see old turn, steps F+ see new turn. Moving steps across this boundary silently breaks behavior.
2. **Battle tracking cleared at step O** AFTER vassal processing reads it (documented dependency, one line comment).
3. **AP reset at step Z** happens AFTER treaty clause penalties applied — ensures correct budget.
4. **Fog recalculation at step BB** is the FINAL step — ensures all state changes reflected.
5. **Strategic orders execute BEFORE advance_turn** — required for cannon fire detection (advance_turn clears `battles_this_turn`).

### Atomicity — NOT GUARANTEED

`advance_turn()` is a monolithic 383-line function. If crash at step 25 of 48:
- Steps 1-24 already committed (turn counter advanced, income applied, etc.)
- Steps 25-48 never execute (manpower, AP reset, fog recalc missing)
- **No checkpoint/rollback mechanism**
- Player retrying "end turn" would **double-process** steps 1-24 (double income, double treaty costs)
- Recovery: Manual save/load only

### Victory/Defeat Timing

Checked THREE times: (1) before enemy phase, (2) after enemy phase, (3) after advance_turn. If any triggers, `game_over=True`. Pending dialogues flushed to result so frontend can show victory screen. Sound design.

### Enemy Phase Architecture

Each AI nation gets action budget, uses same executor as player (Golden Rule #5 verified). Actions affect shared world state immediately — no sandboxing between nations. Fixed nation order (Britain always first — systematic first-mover advantage).

---

## Extended Audit: Error Recovery

**Rating: NO ROLLBACK** — Functions succeed or leave partial state. No crash recovery for multi-step operations.

### Traced Failure Scenarios

**Scenario 1: Attack succeeds, territory capture fails**
- Combat result applied (strength reduced, enemy destroyed, marshal moved)
- `capture_region()` silently returns False if region not found
- State: Marshal at uncaptured region (visual inconsistency). Game continues.

**Scenario 2: Treaty ratification partial failure**
- `_ratify_treaty()` performs 15 sequential mutations: state transition → gold transfer → territory cession → vassal creation → coalition threat → nation elimination
- If territory cession fails (region doesn't exist): state transition already applied, gold already transferred, but territory unchanged
- Threat calculation wrong (based on `transferred_count` which is incomplete)
- Game continues with inconsistent diplomatic/territorial state

**Scenario 3: advance_turn crashes at step 25**
- Turn counter already advanced (step E). Income already applied (step T).
- Manpower, AP reset, fog recalc never execute
- Retrying "end turn" double-processes income, treaty costs
- No detection of partial advance

### Error Handling Patterns in Executor

**8 productive try/except blocks** in 14,797 lines. Almost no error handling in core business logic:
- No try/except around `resolve_battle()`, `capture_region()`, `_ratify_treaty()`
- No try/except around `_advance_turn_internal()`
- Acceptance calculation catches ALL exceptions and silently defaults to 20 (too broad)
- Sabotage/redemption handlers properly log exceptions and return gracefully

### Recommendations

1. **Pre-flight validation** before multi-step operations (validate all regions exist before treaty ratification)
2. **Idempotency guards** in advance_turn (detect "already advanced this turn" to prevent double-processing)
3. **Wrap advance_turn steps** in try/except with logging — graceful degradation over crash

---

## Extended Audit: Test Architecture

**Rating: ADEQUATE** — Substantial coverage but structural weaknesses.

### Test Suite Structure

- **203 test files, ~121,290 lines, ~7,281 tests**
- Flat directory structure (no subdirectories)
- Session-based naming (test_session_2_diplomacy, test_audit_part1, etc.)
- **NO conftest.py** (confirmed)

### Duplication Analysis

- **82 files** contain `_make_world()` or similar factory functions
- **~2,460 lines** of duplicated factory code (estimated: `_make_world` ~10 lines × 82 + `_make_marshal` ~15 lines × 82)
- 3 different factory patterns across files (inline construction, keyword overrides, constructor parameters)
- Adding one Marshal field requires updating factories in ~184 files

### Coverage by System

| System | Test Files | Code Lines | Proportional? |
|--------|-----------|------------|---------------|
| Diplomacy | 17 | ~14,000 | Adequate |
| AI | 9 | ~7,200 | Adequate |
| Audit fixes | 10 | ~8,000 | Strong |
| Serialization | 2 | ~1,100 | Strong (enforcement) |
| Combat | 4 | ~3,200 | **WEAK for ~2,500-line combat engine** |
| **world_state.py** | **0 dedicated** | — | **No standalone tests** |
| **turn_manager.py** | **0 dedicated** | — | **No standalone tests** |
| **main.py endpoints** | **0 dedicated** | — | **No endpoint tests** |

### Enforcement Test Gaps

**Enforced (CI gate):**
- Serialization: all model fields must round-trip through to_dict/from_dict

**NOT enforced:**
- All actions in VALID_ACTIONS have AP costs in `_action_costs`
- All actions have display names in `_ACTION_DISPLAY_NAMES`
- All event types logged are in CAMPAIGN_LOG_TYPES whitelist
- All proposal types have display strings in `PROPOSAL_TYPE_DISPLAY`
- VALID_ACTIONS matches between parser, executor, and validation.py

### Recommended Enforcement Tests

```python
def test_all_actions_have_costs():
    """Every valid action must have an AP cost defined."""
    for action in VALID_ACTIONS:
        assert action in _action_costs, f"{action} missing AP cost"

def test_all_actions_have_display_names():
    """Every valid action must have a UI-friendly display name."""
    for action in VALID_ACTIONS:
        assert action in _ACTION_DISPLAY_NAMES, f"{action} missing display name"

def test_all_event_types_whitelisted():
    """Every log_event() type must be in CAMPAIGN_LOG_TYPES."""
    # Grep all log_event("type") calls, compare against whitelist
    ...
```

These 3 tests alone would have prevented ~18 bugs across prior audits.

---

## Extended Audit: Modding System

**Rating: PROTOTYPE** — Acceptable for EA with documented limitations; needs hardening for 1.0.

### Validator Coverage

| Model | Total Fields | Validated | Coverage |
|-------|-------------|-----------|----------|
| Marshal | 45 | 12 | 27% |
| Region | 8 core | 8 | ~100% |
| WorldState | 150+ | 7 | **~5%** |

**Critically unvalidated:** Diplomatic state graph (WAR with self possible), vassal circular dependencies, coalition state consistency, trust/authority bounds, combat modifier stacking.

### Game-Breaking Mod Scenarios (Unvalidated)

1. **WAR with self:** `diplomatic_states["France-France"] = "WAR"` → crashes is_at_war() checks
2. **Vassal loop:** Saxony vassal to Austria, Austria vassal to Saxony → infinite recursion in cascade code
3. **Invalid coalition:** Leader is non-existent nation → coalition code crashes
4. **Negative authority:** `nation_authority["Britain"] = -200` → inverts diplomacy checks
5. **Zombie marshals:** Strength 0 marshals allowed by validator (warns but permits) → treated as "destroyed" but not cleaned up

### Loading Architecture

```
Modder writes JSON → Validator checks (~30% of fields) → from_scenario merges defaults → from_dict deserializes (NO re-validation) → Game runs → Runtime errors if state invalid
```

**Critical gap:** `from_dict()` accepts ANY values with no bounds checking. Validation is optional and occurs before default merging, not after.

### Save Compatibility

- **No mod metadata in save files** — saves don't track which mod was loaded
- Loading a save from modded game without the mod: custom regions/marshals silently lost
- No format versioning beyond FORMAT_VERSION=2

### Recommendations

| Priority | Fix | Effort |
|----------|-----|--------|
| CRITICAL | Validate diplomatic state graph (no self-WAR, valid enums) | 1-2 hours |
| CRITICAL | Validate vassal system (no circular deps, loyalty 0-100) | 1-2 hours |
| MAJOR | Add bounds checks to from_dict for authority, relations, war scores | 2-3 hours |
| MAJOR | Add mod metadata to save format | 1 hour |
| MAJOR | Document extensibility limits in MODDING_FORMAT.md | 30 min |

---

## Metrics Summary

| Metric | Value |
|--------|-------|
| Backend Python files | 58 |
| Total backend lines | ~45,000 |
| Test files | 203 |
| Total test lines | ~121,000 |
| Total tests | ~7,281 |
| Largest file | executor.py (14,797 lines) |
| WorldState fields | 92 |
| `_execute_*` methods | 50 |
| Enemy AI methods | 74 |
| Cooldown dictionaries | 14 |
| API endpoints | 37 (15 POST, 22 GET) |
| Display name translation maps | 7 |
| Campaign log event types (whitelisted/total) | 36/40+ |
| Circular dependencies | 0 |
| Layer violations | 1 (minor) |
| Golden Rule compliance | 100% (with documented exceptions for target-type modifiers) |
| Code conventions score | 8.6/10 average |
| **Total findings this audit** | **34** (2 CRITICAL, 9 MAJOR, 13 MODERATE, 12 LOW) |
| **Cross-audit bugs traced to root causes** | **~240 of ~450** |
| Godot .gd files | 30 (~10,140 lines) |
| Largest Godot file | main.gd (3,175 lines) |
| CanvasLayer 100 collisions | 11 popups at same layer |
| Duplicated factory code in tests | ~2,460 lines |
| Enforcement test coverage | Serialization only (5 more recommended) |
| Modding validator coverage | ~30% of fields |
| Error recovery (try/except in executor) | 8 blocks in 14,797 lines |
| HTTP timeout handling | None (CRITICAL gap) |
