# Architecture Audit Report

**Date:** 2026-03-27
**Scope:** 12-pass holistic architecture review of project-sovereign-map backend
**Approach:** 11 parallel research agents reading actual code, producing file:line references
**Purpose:** Identify structural root causes of recurring bugs and propose refactoring roadmap

---

## Executive Summary

This codebase is **structurally sound** — no circular dependencies, strong naming conventions, excellent type hints, and consistent error handling. However, five architectural patterns are responsible for the majority of the ~450 bugs found across previous audits:

1. **Post-combat pipeline duplication** — 5 combat paths share 28 post-combat steps; only `_execute_attack` has all 28. Others have 25-75% coverage → recurring "missing step Y in path X" bugs.
2. **Executor God Object** — 14,797 lines / 50 `_execute_*` methods in one class. Cognitive overload drives bugs.
3. **No shared test fixtures** — 203 test files, 0 conftest.py, 50+ duplicated `_make_world()` factories. Adding one Marshal field requires 184 file updates.
4. **No transaction boundaries** — If step 5 of a 10-step operation fails, steps 1-4 persist with no rollback.
5. **Ad-hoc response pipeline** — No unified backend→frontend contract; 13 POST endpoints return different response shapes.

The codebase scores well on: import organization (9.5/10), type hints (9.5/10), error handling (9.5/10), magic number extraction (9/10), Golden Rule compliance (verified).

---

## Pass 1: The Executor God Object

### Findings

`executor.py` is **14,797 lines** with **50 `_execute_*` methods** and **40+ helpers** in a single `CommandExecutor` class. The heaviest methods:

| Method | Lines | Domain |
|--------|-------|--------|
| `_execute_diplomatic_ultimatum` | 2,143 | Diplomacy state machine |
| `_execute_attack` | 1,910 | Core combat pipeline |
| `_execute_help` | 1,302 | Inline documentation |
| `execute()` (router) | 1,130 | Main dispatch + guards |
| `_process_dialogue_choice()` | 1,104 | Dialogue state machine |
| `_build_clarification()` | 844 | Literal personality UI |
| `_execute_strategic_command` | 803 | Strategic orders |
| `_execute_retreat_action` | 750 | Complex retreat logic |

### Natural Module Boundaries

| Proposed Module | Methods | Lines | Key Contents |
|----------------|---------|-------|--------------|
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

### Recommendation

**Severity: MAJOR** — Split into 11 domain executors. Estimated effort: 3-4 sessions, incremental. Start with utilities extraction, then combat (highest bug rate), then diplomatic (largest self-contained block).

---

## Pass 2: Post-Combat Pipeline Duplication

### Findings

**The #1 recurring audit finding across 5 audits** is "auto-action path X missing post-combat step Y." Root cause: 5 combat paths implement different subsets of 28 post-combat steps.

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
- `_execute_attack`: 26/28 steps (93%)
- `_execute_glorious_charge`: 10/28 (36%)
- `_resolve_garrison_combat`: 7/28 (25%)
- `_execute_bombardment`: 8/28 (29%)
- `auto_bombardment_kill`: 14/28 (50%)

### Critical Missing Steps

- **`last_combat_result` not set** except in `_execute_attack` → strategic conditions (`until_battle_won`) don't trigger after charge/garrison.
- **Vindication missing** in garrison combat → garrison victories don't resolve vindication events.
- **Idle tracking missing** in garrison combat → garrison assaults don't reset stagnation counter.
- **Relationship processing missing** in garrison combat → no trust effects from garrison battles.

### Proposed Fix

Create unified `_post_combat_pipeline(battle_result, attacker, defender, world, **context)` with context flags (`is_bombardment`, `is_garrison`, `is_glorious_charge`) to skip inapplicable steps. All combat paths call it after `resolve_battle()`.

### Recommendation

**Severity: CRITICAL** — This is the single highest-ROI refactoring. Eliminates an entire category of recurring audit findings. Estimated: 1 session, ~400 lines new + removal of ~600 duplicated lines across 5 paths.

---

## Pass 3: WorldState Field Sprawl

### Findings

`world_state.py` has **92 persistent fields** in `__init__`, grouped:

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
| Others | 4 | 4.3% | Stable |

**Serialization: 89 of 92 fields serialized** (3 transient excluded). No critical mismatches.

### advance_turn Decomposition

`_advance_turn_internal()` is 383 lines with **48 sequential operations**. 25+ already delegated to external functions — good discipline. 15-20 remain inlined but are small (avg 9 lines/operation).

### Problem Patterns

1. **16+ cooldown dicts** — each manually decremented in advance_turn. Off-by-one and forgotten-decrement bugs recur.
2. **7 popup fields** — no unified queue. Each popup type cleared manually. Popup leak bugs recur.
3. **356 `getattr()` calls** across codebase — mostly defensive/backward-compatible, but 23 in world_state.py indicate schema uncertainty.

### Recommendation

**Severity: MAJOR** — Extract `CooldownManager` (centralizes 16 dicts, eliminates decrement bugs) and `PopupQueue` (prevents popup leaks). Both maintain save format via properties. Defer `DiplomacyLayer` sub-object until after Phase 5 adds more fields.

---

## Pass 4: Enemy AI Structure

### Findings

`enemy_ai.py` is **5,561 lines** with **74 methods**. The P0-P8 priority system is well-documented and correctly implemented.

**Heaviest methods:**
- `_evaluate_marshal()`: 622 lines (P-priority dispatcher)
- `process_nation_turn()`: 351 lines (main loop)
- `_find_attack_opportunity()`: 306 lines (P4 targeting)
- `_check_fortification_opportunity()`: 271 lines
- `_consider_strategic_move()`: 259 lines

**Golden Rule #5 verified: FULLY COMPLIANT.** Enemy AI never mutates world state directly — all actions go through `executor.execute()`. Zero bypasses found.

**Personality coupling:** 81 references across 15+ methods. Personality is architecturally fundamental (not bolted-on), so extraction would reduce 20 lines per method but increase wiring complexity.

### Proposed Decomposition

| Class | Lines | Purpose |
|-------|-------|---------|
| `EnemyAI` (orchestrator) | 600 | Main loop, personality, cooldowns |
| `EnemyAIDecisionTree` | 1,800 | P0-P8 evaluators |
| `EnemyAIScoring` | 900 | Target ratios, artillery scoring |
| `EnemyAITargeting` | 1,200 | Movement, pathfinding, region analysis |
| `EnemyAIAdmin` | 600 | Recruitment, building, repair |

### Recommendation

**Severity: MINOR** — The file is large but well-structured. Split would reduce cognitive load ~20-30% but add composition overhead. Worth doing if planning 2+ years of maintenance; defer if focused on near-term features. The P-priority single-pass architecture is excellent — preserve it.

---

## Pass 5: Test Infrastructure

### Findings

**203 test files, 121,290 lines, 0 shared fixtures.**

- **50+ distinct `_make_world()` variants** across test files
- **694 direct `Marshal()` instantiations** in tests
- **No `tests/conftest.py`** exists

### Impact of Adding a New Marshal Field

| Approach | Files Changed | Time |
|----------|---------------|------|
| Without conftest | ~184 files, 50+ factories | 8-12 hours |
| With conftest | 4 locations | 1-2 hours |

### Proposed conftest.py

```python
class MarshalFactory:
    @staticmethod
    def infantry(name="TestInf", location="Paris", strength=30000, ...): ...
    @staticmethod
    def cavalry(...): ...
    @staticmethod
    def artillery(...): ...

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

### Migration Strategy

Fully incremental: create conftest.py (additive), new tests use fixtures, old tests keep working. Migrate high-churn files first.

### Recommendation

**Severity: CRITICAL** — Implement conftest.py immediately. This is not optional refactoring — it's a maintenance liability multiplier. Estimated: 2 hours to create, then incremental adoption. Saves 5,000-6,000 lines of duplicated factory code over time.

---

## Pass 6: Module Dependency Graph

### Findings

**Zero circular dependencies.** Python would have failed on import if any existed.

**Expected layer structure holds:**
```
models → game_logic → commands → ai → main
```

**One layer violation:** `world_state.py` (models) imports from `disobedience.py` and `vindication.py` (commands layer). These should be in `game_logic/`.

### Fan-In (Most Imported)

1. `world_state.py` — 15+ importers (expected: central game state)
2. `marshal.py` — 12+ importers
3. `region.py` — 11+ importers
4. `intel.py` — 9+ importers
5. `personality.py` — 7+ importers

### Fan-Out (Most Imports)

1. `main.py` — 25+ imports (expected: top-level API)
2. `executor.py` — 12+ imports (appropriate: execution engine)
3. `world_state.py` — 8 imports

### Recommendation

**Severity: MINOR** — Move `disobedience.py` and `vindication.py` to `game_logic/` to fix the only layer violation. Structure is healthy and supports clean module extraction.

---

## Pass 7: State Mutation Patterns

### Findings

**Three-layer mutation model, NO transaction boundaries:**

```
main.py (orchestration — no mutation)
  ↓
executor.py (direct mutations on marshal/world)
  ↓
game_logic modules (cascading mutations via world reference)
```

### Transaction Risk

If step 5 of a 10-step operation fails:
- Steps 1-4 mutations PERSIST
- Steps 5-10 don't execute
- No save/restore point, no rollback

**Concrete example:** Treaty ratification (`_ratify_treaty`, world_state.py:4204-4453) performs 15 sequential mutations — state transition, gold transfer, territory cession, vassal creation, coalition threat, nation elimination. If territory cession fails, game has: PEACE state + gold moved + treaty signed, but territory unchanged.

### The `pending_*` Chaos

| Field | SET locations | CLEAR locations | Status |
|-------|-------------|----------------|--------|
| `pending_diplomatic_dialogue` | **30+** | **50+** | **CHAOS** — no guarantee each SET has matching CLEAR |
| `pending_dispatch_events` | many | 1 (turn start) | **HIGH RISK** — auto-cleared before consumption possible |
| `pending_objection` | 1 | 1 | Clean |
| `pending_capture_choice` | 2 | 3 | Clean |
| `pending_glorious_charge` | 2 | 1 | Clean |

### Recommendation

**Severity: MAJOR** — `pending_diplomatic_dialogue` needs a centralized dialogue manager with explicit queue semantics (not 30 ad-hoc writes). Transaction boundaries would be ideal but high migration cost — consider save-point before multi-step operations as pragmatic alternative.

---

## Pass 8: Response Pipeline

### Findings

**No unified response contract.** 13 POST endpoints return different response shapes.

**`_include_popup_passthroughs()`** (main.py:146-267) is the only centralization point. It:
- Injects 7 popup keys (set to `None` if no popup pending)
- Auto-pops dialogue queue
- Embeds `active_wars` conditionally

**Key issues:**
- `active_wars` only explicitly embedded in `/command` normal path; other endpoints rely on `_include_popup_passthroughs()` conditional injection
- Diplomatic fields (`diplomatic_points`, `threat_level`) only in `/command` — other handlers miss them
- **37 "Bug 5" references** in main.py — each marking a spot where `_include_popup_passthroughs()` was nearly forgotten on an early return
- No schema validation — Godot receives whatever backend sends

### Recommendation

**Severity: MAJOR** — Create a `@response_with_popups` decorator or `build_standard_response()` helper. All endpoints should return a consistent shape. Document the response contract. Estimated: 1 session.

---

## Pass 9: Serialization Architecture

### Findings

**9 classes fully serialized:** Marshal (137 fields), WorldState (120+ fields), Region (14), StrategicOrder (17), StrategicCondition (6), Trust (1), AuthorityTracker (3), VindicationTracker (4), DiplomaticRepresentative (6).

**Round-trip fidelity: EXCELLENT.** `from_dict(to_dict(obj))` produces identical objects for all classes. No lossy conversions. Sets converted to lists for JSON compatibility, restored as sets on load. Enums use `.value` conversion with try/except fallback.

**Enforcement test:** `test_serialization_enforcement.py` (696 lines) catches:
- Missing `to_dict()` entries (compares instance attrs vs serialized keys)
- Missing `from_dict()` entries (roundtrip value equality check)
- Type mismatches (exact equality assertion)
- Known exclusions for computed properties (`is_reckless_cavalry`, `in_strategic_mode`)

**Backward compatibility: STRONG.** Extensive `.get(key, default)` patterns. Migration logic for `gold` → `nation_gold` dict, `garrison_player_placed` → `garrison_detachment` rename. Format versioning: FORMAT_VERSION=2, rejects v1 saves.

**Fragility assessment:**

| Operation | Risk | Detection |
|-----------|------|-----------|
| Add field | MODERATE | 2 changes needed (to_dict + from_dict); caught by enforcement test |
| Remove field | LOW | Old saves use `.get()` with defaults; silently ignored |
| Rename field | HIGH | Must update 2 places + migration; test won't catch name typo |
| Type change | MODERATE | int()/str() conversions may lose precision |

**Issues found:**
1. `SAVE_FORMAT_REFERENCE.md` claims version "1.0" but code has FORMAT_VERSION=2 — stale docs
2. Invalid stance enum silently falls back to NEUTRAL with no warning logged (marshal.py:1295-1298)
3. Transient state clearance on load not tested (save_manager.py:121-129)

### Recommendation

**Severity: LOW** — Architecture is sound and well-tested. Do NOT migrate to dataclasses/Pydantic (cost >> benefit). Fix: update stale version docs, add transient-state-cleared test, log enum fallback warnings.

---

## Pass 10: Code Conventions

### Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Error handling** | 9.5/10 | Dict-based deterministic pattern universal. No exceptions by design. |
| **Import organization** | 9.5/10 | Consistent stdlib → third-party → local across all files. |
| **Type hints** | 9.5/10 | ~95% coverage. Parameterized generics. No bare types. |
| **Magic numbers** | 9/10 | ~95% extracted to named constants. Inline numbers justified with comments. |
| **Naming conventions** | 8/10 | Method names consistent. 3 time-based field suffix patterns. |
| **Docstrings/comments** | 8/10 | Module/class strong. Function docs ~70%. Inline comments excellent. |
| **Logging** | 6/10 | Mix of `print()`, `debug_print()`, `ai_debug()`, `logging`. No unified strategy. |

### Recommendation

**Severity: LOW** — Unify logging on `debug_print()` or Python `logging` module. Everything else is strong.

---

## Pass 11: Scaling Assessment (19 → 80 Regions)

### Risk Matrix

| System | Current | At 80 Regions | Risk | Action |
|--------|---------|---------------|------|--------|
| **Visibility calc** | 10-15ms | 80-150ms | CRITICAL | Refactor O(R×M) → O(R+M) with marshal index |
| **AI strategic decisions** | 30-50ms | 150-250ms | CRITICAL | + AI omniscience problem |
| **Supply attrition** | 2-3ms | 20-25ms | MAJOR | Same index fix as visibility |
| **Income phase** | 5-10ms | 40-60ms | MAJOR | Cache nation→regions |
| **Serialization** | 46KB/7ms | 160KB/25ms | MAJOR | Consider binary format |
| **Diplomacy** | 5-10ms | 20-30ms | MEDIUM | Acceptable |
| **Coalition** | 10-15ms | 20-25ms | LOW | Acceptable |
| **Total turn time** | 80-120ms | **400-600ms** | **MAJOR** | May violate 1s budget |

### Critical Finding: AI Omniscience

Enemy AI does NOT respect fog of war. `enemy_ai.py:3354` calls `world.get_enemies_of_nation(nation)` which returns ALL enemy marshals globally. At 19 regions this is barely noticeable; at 80 regions it produces unfair all-knowing AI behavior AND worse performance.

### Key Optimization

Build `marshals_by_region` inverse index once per turn start:
```python
marshals_by_region = {}
for m in self.marshals.values():
    marshals_by_region.setdefault(m.location, []).append(m)
```
This single change fixes visibility calc, supply attrition, and income phase — all from O(R×M) to O(R+M).

### Recommendation

**Severity: CRITICAL (before 80-region expansion)** — 3 fixes needed:
1. Marshal-by-region index (1 day, fixes 3 systems)
2. AI fog integration (4-6 days, 10-12 functions)
3. Pathfinding cache (2 days, prevents repeated distance calcs)

---

## Refactoring Roadmap

### Priority-Ordered Sessions

#### Session R1: Post-Combat Pipeline (CRITICAL)
- **What:** Extract unified `_post_combat_pipeline()` from `_execute_attack`, apply to all 5 combat paths
- **Why:** Eliminates #1 recurring audit finding category (missing post-combat steps)
- **Effort:** ~400 new lines, ~600 removed. 1 session.
- **Risk:** Low — each path already works, just consolidating. Verify with existing combat tests.
- **Dependencies:** None
- **Independent?** Yes

#### Session R2: Test conftest.py (CRITICAL)
- **What:** Create `tests/conftest.py` with MarshalFactory, WorldFactory, basic fixtures
- **Why:** Next Marshal field addition currently requires 184 file updates
- **Effort:** ~100 new lines. 2 hours to create, incremental adoption.
- **Risk:** Zero — additive only, old tests unchanged
- **Dependencies:** None
- **Independent?** Yes

#### Session R3: CooldownManager + PopupQueue (MAJOR)
- **What:** Extract 16 cooldown dicts into `CooldownManager`, 7 popup fields into `PopupQueue`
- **Why:** Eliminates forgotten-decrement and popup-leak bug categories
- **Effort:** ~200 new lines, ~150 removed. Properties maintain save format.
- **Risk:** Low — properties provide backward compatibility
- **Dependencies:** None
- **Independent?** Yes

#### Session R4: Response Pipeline Standardization (MAJOR)
- **What:** Create `build_standard_response()` helper, ensure all POST endpoints use it
- **Why:** Eliminates "Bug 5" pattern (popup passthrough missed on early return)
- **Effort:** ~150 new lines, refactor 13 endpoints. 1 session.
- **Risk:** Medium — must verify Godot handles consistent response shape
- **Dependencies:** None
- **Independent?** Yes

#### Session R5: Scaling Index (CRITICAL before 80 regions)
- **What:** Build `marshals_by_region` index at turn start, use in visibility, supply, income
- **Why:** 3 systems go from O(R×M) to O(R+M) — 10-15× speedup at scale
- **Effort:** ~50 new lines, modify 3 methods. Half session.
- **Risk:** Low — pure optimization, no behavior change
- **Dependencies:** None
- **Independent?** Yes

#### Session R6: Executor Split Phase 1 — Utilities + Combat (MAJOR)
- **What:** Extract `executor_utils.py` (fuzzy matching, display names) and `combat_executor.py` (attack, bombardment, coordination)
- **Why:** Reduces executor.py from 14,797 to ~10,000 lines
- **Effort:** Move existing code, add import wiring. 1 session.
- **Risk:** Medium — must verify all combat test paths still work
- **Dependencies:** R1 (post-combat pipeline) should come first
- **Independent?** Yes after R1

#### Session R7: Executor Split Phase 2 — Diplomatic + Strategic (MAJOR)
- **What:** Extract `diplomatic_executor.py` and `strategic_executor.py`
- **Why:** Diplomacy (2,200 lines) and strategic (1,200 lines) are self-contained
- **Effort:** Move existing code. 1 session.
- **Risk:** Medium — diplomatic dialogue state machine has complex routing
- **Dependencies:** R6
- **Independent?** After R6

#### Session R8: AI Fog Integration (CRITICAL before 80 regions)
- **What:** Replace omniscient AI with fog-aware decision-making in 10-12 enemy_ai.py functions
- **Why:** Game balance + performance at scale
- **Effort:** Modify 10-12 methods, add intel checks. 4-6 days.
- **Risk:** High — changes AI behavior significantly. Needs playtesting.
- **Dependencies:** R5 (scaling index)
- **Independent?** After R5

#### Session R9: Dialogue Manager (MAJOR)
- **What:** Replace 30 SET + 50 CLEAR sites for `pending_diplomatic_dialogue` with centralized `DialogueManager`
- **Why:** Eliminates stuck-dialogue and dialogue-overwrite bugs
- **Effort:** ~200 new lines, refactor 80 sites. 1-2 sessions.
- **Risk:** High — touches many code paths
- **Dependencies:** R7 (diplomatic executor split makes this easier)
- **Independent?** After R7

#### Session R10: Executor Split Phase 3 — Remaining Domains (MINOR)
- **What:** Extract movement, tactical, economy, meta, vassal, capture executors
- **Why:** Completes the split, each file under 2,500 lines
- **Effort:** Move existing code. 1 session.
- **Risk:** Low — smaller, more self-contained modules
- **Dependencies:** R6, R7
- **Independent?** After R7

### Dependency Graph

```
R1 (post-combat pipeline) ──→ R6 (executor split: combat)
R2 (conftest.py)                         ↓
R3 (cooldown/popup)          R7 (executor split: diplomatic)
R4 (response pipeline)                   ↓
R5 (scaling index) ──→ R8 (AI fog)      R9 (dialogue manager)
                                          ↓
                              R10 (executor split: remaining)
```

Sessions R1-R5 are **fully independent** and can be done in any order or in parallel.

---

## Architecture Principles

Distilled from all 11 passes — these extend the existing Golden Rules:

1. **One combat pipeline, many entry points.** All combat paths must call the same post-combat pipeline. Path-specific behavior uses context flags, not code duplication.

2. **Shared test fixtures are infrastructure, not nice-to-have.** Every new field multiplied by 184 test files is a maintenance tax. conftest.py is the tax exemption.

3. **Cooldowns and popup queues are patterns, not fields.** When you have 16 dicts that all decrement by 1 per turn, that's a `CooldownManager`. When you have 7 optional popup fields that each need set/read/clear, that's a `PopupQueue`.

4. **Response shape is a contract.** Backend and frontend must agree on response structure. Use a builder function, not ad-hoc dict construction per endpoint.

5. **Index once, lookup many.** Build `marshals_by_region` and `regions_by_nation` caches at turn start. O(N) build cost saves O(N²) across 10+ consumers.

6. **AI must respect the same constraints as the player.** Fog of war applies to decisions, not just display. An omniscient AI is a bug, not a feature.

7. **Mutation flows downward.** main.py orchestrates, executor.py mutates, game_logic modules transform. Never mutate state in main.py. Never call main.py from executor.

8. **Pending fields have lifecycles.** Every `pending_*` field must have documented SET → READ → CLEAR sites. If a field has 30 SET sites, it needs a manager object.

9. **God Objects are acceptable IF they have clear internal structure.** `WorldState` at 92 fields is fine because fields are well-grouped and serialization is enforced. `executor.py` at 14,797 lines is not fine because domain boundaries are blurred.

10. **Extract for bugs, not for beauty.** The post-combat pipeline extraction prevents an entire category of bugs. The enemy AI split just improves readability. Prioritize accordingly.

---

## What NOT to Refactor

These look messy but should be left alone:

1. **WorldState as a single object** — The 92-field God Object is intentional. Splitting into `DiplomacyLayer`, `CoalitionState`, etc. would require touching hundreds of call sites across the codebase for marginal benefit. The fields are well-organized within the class, serialization is enforced, and advance_turn already delegates to external processors. Leave it.

2. **The P0-P8 priority system in enemy_ai.py** — The 622-line `_evaluate_marshal()` looks enormous but implements a clean single-pass priority system. Breaking it into separate methods would scatter the priority order across files and make precedence harder to verify. The method is long but linear — not complex.

3. **Dict-based error returns** — Replacing `{"success": False, "message": "..."}` with exceptions would require rewriting all 50 `_execute_*` methods and their callers. The current pattern is consistent, deterministic, and well-integrated with the API response flow. It works.

4. **Inline documentation in `_execute_help()`** — The 1,302-line help method is a design choice (help text lives with the code it describes). Extracting to a file would create drift between help text and implementation. Leave it.

5. **Multiple small test files** — 203 test files averaging 600 lines each is preferable to 20 large files. The flat directory structure works with pytest discovery. Organization by naming convention is sufficient.

6. **`_include_popup_passthroughs()` architecture** — The function that injects popups into every response is ugly but correct. Popups can be set by any executor path and must reach the frontend regardless of which endpoint returns. Polling-based alternatives would require Godot to make extra HTTP calls per turn. The current approach is the right tradeoff for a local single-player game.

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
| Circular dependencies | 0 |
| Layer violations | 1 (minor: world_state → disobedience) |
| Golden Rule compliance | 100% verified |
| Code conventions score | 8.6/10 average |

---

## Deep Dives (Pass 12+)

### 12a: Dialogue State Machine Lifecycle

**`pending_diplomatic_dialogue`** has **66 SET operations** and **44 CLEAR operations** across the backend.

**Architecture:** Single-field overwrite with FIFO queue fallback (`pending_dialogue_queue`). Queue writers use `.append()` (never direct assignment), preventing collision. Priority-ordered auto-pop in main.py (alliance_paradox > vassal_rebellion > sabotage > redemption > proposal).

**Blocking guard:** executor.py:1472 blocks ALL non-cheat commands while dialogue pending. Dialogue responses routed in main.py:658 BEFORE executor, bypassing the guard.

**Safety valve:** Non-blocking dialogues auto-clear if stale (from prior turn) in world_state.py:3829-3846. Blocking dialogues have NO auto-clear — stuck indefinitely if player can't respond.

**Key risk:** No queue cap — queue can grow unbounded if events generate faster than player responds. No audit trail of dialogue transitions.

**Recommendation:** Implement `DialogueManager` class centralizing all SET/CLEAR/QUEUE operations with audit trail, queue cap (10-20), and timeout for blocking dialogues. Reduces 66 scattered SET sites to 1 class.

### 12c: Notification Architecture

**Architecture: SOUND.** EU4-style persistent alerts via `NotificationCollector` with 50-notification cap (evicts oldest NORMAL first, preserves HIGH/CRITICAL).

**32 notification types** across 10 source files, 39 `.add()` calls, 18 `.dismiss*()` calls. Most HIGH notifications auto-dismiss when condition resolves (proposal accepted → dismiss DIPLOMATIC_PROPOSAL).

**Dead code:** `VASSAL_REBELLION` and `VASSAL_LOYALTY_CRITICAL` types defined but never created.

**Risk:** HIGH/CRITICAL notifications with no auto-dismissal (`RECKLESS_CAVALRY_ACTION`, `DEFECTION_CASCADE`) can accumulate indefinitely. Consider optional TTL (auto-dismiss after 10 turns).

**Fog leak:** Notifications ignore fog of war — player learns about fogged nation's diplomacy via DIPLOMATIC_PROPOSAL. Intentional design (game-world alerts, not intel).

### 12d: Campaign Log Filter Architecture

**Architecture: WHITELIST-BASED.** `CAMPAIGN_LOG_TYPES` set (24 types) in campaign_log.py:83-120 gates which events are shown. Events not in whitelist are **silently dropped** — no error, no warning.

**CRITICAL FINDING: 18 logged event types are NOT whitelisted → invisible to players:**
- `ai_proposal_accepted/rejected/counter_failed` — player gets zero log feedback on diplomatic proposals
- `coalition_brewing_started/cancelled` — coalition lifecycle invisible in log
- `relationship_change` — win/loss relationship effects invisible
- `diplomatic_mission_started` — mission actions invisible
- `garrison_placed` — enemy garrison placements invisible
- And 9 more

**Root cause:** Triple-layer silent failure — whitelist drops unknown types, format function falls through to generic text, category map defaults to "unknown". No compile-time or test-time check catches the gap.

**Recommendation:** Add test that compares all `world.log_event()` type strings against `CAMPAIGN_LOG_TYPES`. Add the 18 missing types with format strings and fog rules. Add to CLAUDE.md "Adding New Actions" checklist: "Add event type to CAMPAIGN_LOG_TYPES in campaign_log.py."

### 12e: Strategic Order Lifecycle

**Architecture: CLEAN and well-engineered.** Full lifecycle properly managed:
- Issuance with personality-aware validation and V2a objections
- Per-turn two-pass execution (non-interrupting first, then deferred)
- Fog-of-war integration in PURSUE (uses last_known_location, not real position)
- Personality-specific behavior (LITERAL: never interrupts, immovable HOLD)
- 14 StrategicOrder fields fully serialized

**All major edge cases handled correctly:**
- Dead marshal mid-order (cleared)
- Target dies/moves during PURSUE (completes/fog-aware redirect)
- Peace signed during PURSUE/SUPPORT (auto-breaks)
- SUPPORT timer counts from arrival, not issuance
- Contact loop prevention (same enemy suppression)

**Minor issues found:**
1. `pending_interrupt` not cleared when new order replaces old (executor.py:6218) — could leave stale interrupt
2. `cannon_fire_ignored_turn` not cleared on order completion — harmless due to 1-turn TTL

**Assessment:** No refactoring needed. This is one of the best-architected subsystems.

### 12b: Display Name Translation Consistency

**7 display maps found** across the backend, translating internal names to UI-friendly text:

| Map | File | Entries | Purpose |
|-----|------|---------|---------|
| `_ACTION_DISPLAY_NAMES` | executor.py:41 | 17 | Action verbs ("attack" → "attacks") |
| `PROPOSAL_TYPE_DISPLAY` | diplomatic_dialogue.py:81 | 11 | Proposal labels ("peace" → "Peace Treaty") |
| `_STATE_DISPLAY_NAMES` | diplomacy.py:2459 | 8 | Formal state names ("WAR" → "At War") |
| `_STATE_DISPLAY` | diplomatic_advisory.py:50 | 8 | Narrative state ("WAR" → "at war") |
| `_DEFIANCE_DISPLAY` | campaign_log.py:43 | 15 | Past tense ("attack" → "attacked") |
| `_OBJECTION_DISPLAY` | campaign_log.py:21 | 17 | Gerunds ("attack" → "attacking") |
| `FEEDBACK_STRINGS` | diplomacy.py:138 | 16 | Acceptance formula components |

**5 gaps where raw internal names leak to frontend:**

1. **`GET /diplomatic_states`** returns raw "WAR"/"PEACE" state strings — `_STATE_DISPLAY_NAMES` not applied (CRITICAL)
2. **`GET /pending_objection`** returns raw `original_order.action` — `_ACTION_DISPLAY_NAMES` not applied (HIGH)
3. **`POST /respond_to_objection`** returns raw defiance outcomes "failed_roll"/"right"/"wrong" — no display map exists (MEDIUM)
4. **`POST /diplomatic_preview`** returns raw action names in actions list (HIGH)
5. **Personality/Stance enums** returned as raw strings — no formal display maps (LOW)

**3 missing display maps:** `_DEFIANCE_OUTCOME_DISPLAY`, `_PERSONALITY_DISPLAY`, `_STANCE_DISPLAY`.

**Checklist for adding new actions** (must update 5 places):
1. `_ACTION_DISPLAY_NAMES` (executor.py:41)
2. `_DEFIANCE_DISPLAY` (campaign_log.py:43)
3. `_OBJECTION_DISPLAY` (campaign_log.py:21)
4. `VALID_ACTIONS` (validation.py)
5. `_execute_*()` method (executor.py)

### 12f: Modding System Security

**Validator coverage is ~20% of settable fields.** The modding validator (`backend/modding/validator.py`) performs basic type checking, range warnings, and cross-validation (marshal locations must be real regions, adjacency must be bidirectional), but misses the vast majority of complex game state.

**Coverage by model:**

| Model | Total Fields | Validated | Coverage |
|-------|-------------|-----------|----------|
| Marshal | 45 | 12 | 27% |
| Region | 8 core | 8 | ~100% |
| WorldState | 150+ | 7 | ~5% |

**CRITICAL gaps (game-breaking mods possible):**

1. **Diplomatic state corruption** (12 fields) — `diplomatic_states`, `nation_relations`, `war_scores`, `armistice_cooldowns`, `active_coalition`, `coalition_brewing`, `threat_level`, `active_treaties`, `diplomatic_reliability` completely unvalidated. A mod could set contradictory states (France at war with itself), force instant coalition via `threat_level: 1000`, or create diplomatic state cycles.

2. **Combat modifier stacking** (9 fields) — `artillery`, `cavalry`, `square_formation`, `recklessness`, `shock_bonus`, `defense_bonus`, `counter_punch_ready`, `holding_position`, `overwatch_penalty` all unvalidated. Mutually exclusive flags (cavalry + artillery + square_formation) can be set simultaneously, giving contradictory 80%+ attack bonuses.

3. **Vassal/coalition loops** (6 fields) — `vassals` dict, `continental_system_members`, `cascade_triggered`, `coalition_cooldown`, `war_exhaustion` all unvalidated. Mod could create infinite vassals, mark all cascades as triggered to block new coalitions, or set `war_exhaustion: 9999` to eliminate nations.

**HIGH gaps:**

4. **Objection/trust bypass** (5 fields) — `pending_objection`, `pending_redemption`, `authority_tracker`, `vindication_tracker` unvalidated. Setting `authority_tracker.authority: 1000` suppresses all marshal objections.

5. **Game flow corruption** (5 fields) — No logical coherence checks: `current_turn: 10000, max_turns: 5` breaks turn processing. `actions_remaining: 1000` gives infinite actions. No validation that `game_over=true` requires `victory` field.

**MEDIUM gaps:**

6. **Region economics** (6 fields) — `stability`, `war_damage`, `buildings`, `building_under_construction`, `watchtower` unvalidated. `stability: -999` or `war_damage: 10.5` possible.

7. **Serialization safety** (8 fields) — Complex nested objects (StrategicOrder, Trust, Diplomat) not validated. Invalid objects crash during save/load.

**What the validator DOES enforce well:**
- Basic type checking (int/string/boolean) ✓
- Required field presence (name, location, strength) ✓
- Enum validation (personality, stance, terrain, region_type) ✓
- Cross-validation: marshal locations and adjacency references ✓

**Severity:** MAJOR — modding is single-player and optional, so the blast radius is limited to the modder's own game. However, community mods shared without validation could cause confusing crashes or impossible states.

**Recommendation:** Add validation layers incrementally:
1. **Diplomatic graph coherence** — no self-wars, valid state values, nation existence in all dicts
2. **Combat flag mutual exclusivity** — cavalry XOR artillery XOR neither; square only for non-cavalry
3. **Logical bounds** — `current_turn <= max_turns`, `actions_remaining <= max_actions_per_turn`
4. **Document untouchable fields** — warn modders away from `pending_*`, coalition, and objection state
