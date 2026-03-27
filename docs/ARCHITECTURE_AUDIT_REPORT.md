# Architecture Audit Report

**Date:** 2026-03-27 (initial), 2026-03-27 (extended)
**Scope:** 12-pass holistic review + 35 extended deep dives across 5 domains
**Approach:** 11 initial agents + 5 parallel deep-dive agents reading actual code, producing file:line references
**Purpose:** Identify structural root causes of recurring bugs and propose refactoring roadmap
**Total findings:** 34 (2 CRITICAL, 9 MAJOR, 13 MODERATE, 12 LOW)

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

*First 6 deep dives from initial audit. Extended deep dives (13+) follow in the next section.*

### 12a: Dialogue State Machine Lifecycle

**`pending_diplomatic_dialogue`** has **66 SET operations** and **44 CLEAR operations** across the backend.

**Architecture:** Single-field overwrite with FIFO queue fallback (`pending_dialogue_queue`). Queue writers use `.append()` (never direct assignment), preventing collision. Priority-ordered auto-pop in main.py (alliance_paradox > vassal_rebellion > sabotage > redemption > proposal).

**Blocking guard:** executor.py:1472 blocks ALL non-cheat commands while dialogue pending. Dialogue responses routed in main.py:658 BEFORE executor, bypassing the guard.

**Safety valve:** Non-blocking dialogues auto-clear if stale (from prior turn) in world_state.py:3829-3846. Blocking dialogues have NO auto-clear — stuck indefinitely if player can't respond.

**Key risk:** No queue cap — queue can grow unbounded if events generate faster than player responds. No audit trail of dialogue transitions.

**Recommendation:** Implement `DialogueManager` class centralizing all SET/CLEAR/QUEUE operations with audit trail, queue cap (10-20), and timeout for blocking dialogues. Reduces 66 scattered SET sites to 1 class.

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

**Recommendation:** Add test that compares all `world.log_event()` type strings against `CAMPAIGN_LOG_TYPES`. Add the 18 missing types with format strings and fog rules.

### 12e: Strategic Order Lifecycle

**Architecture: CLEAN and well-engineered.** Full lifecycle properly managed:
- Issuance with personality-aware validation and V2a objections
- Per-turn two-pass execution (non-interrupting first, then deferred)
- Fog-of-war integration in PURSUE (uses last_known_location, not real position)
- Personality-specific behavior (LITERAL: never interrupts, immovable HOLD)
- 14 StrategicOrder fields fully serialized

**All major edge cases handled correctly.** No refactoring needed. This is one of the best-architected subsystems.

**Minor issues:** `pending_interrupt` not cleared when new order replaces old (executor.py:6218). `cannon_fire_ignored_turn` not cleared on order completion — harmless due to 1-turn TTL.

### 12f: Modding System Security

**Validator coverage is ~20% of settable fields.** The modding validator (`backend/modding/validator.py`) performs basic type checking, range warnings, and cross-validation, but misses the vast majority of complex game state.

| Model | Total Fields | Validated | Coverage |
|-------|-------------|-----------|----------|
| Marshal | 45 | 12 | 27% |
| Region | 8 core | 8 | ~100% |
| WorldState | 150+ | 7 | ~5% |

**CRITICAL gaps:** Diplomatic state corruption (12 fields), combat modifier stacking (9 fields), vassal/coalition loops (6 fields). **HIGH gaps:** Objection/trust bypass (5 fields), game flow corruption (5 fields). **MEDIUM gaps:** Region economics (6 fields), serialization safety (8 fields).

**Severity:** MAJOR — modding is single-player, blast radius limited to modder's own game. Add validation incrementally: diplomatic graph coherence, combat flag mutual exclusivity, logical bounds, document untouchable fields.

---

## Extended Deep Dives (Pass 13+)

*5-agent parallel code review. Each agent read 5-10 source files thoroughly, producing findings with file:line references. 35 additional deep dives across 5 domains.*

---

### 13: Combat Pipeline

#### 13a: Combat Modifier Chain

**Files analyzed:** marshal.py (lines 832-988), combat.py (lines 152-500), battle_report.py (lines 21-231)

**Architecture assessment:** The modifier chain respects Golden Rule #1 (single source in marshal.py) but combat.py applies several target-type modifiers (cavalry counter, square formation, cavalry terrain) directly to `shock_multiplier` outside the single-source methods, creating a de facto secondary modifier layer.

**Key findings:**

1. **Golden Rule #1 partial violation** (combat.py:383-403). Cavalry-vs-artillery +30%, square formation -40%/+50%, and cavalry terrain adjustments applied directly in `resolve_battle()`, NOT in `get_attack_modifier()`. Code calling `get_attack_modifier()` outside of `resolve_battle()` (e.g., garrison combat at executor.py:2795) will NOT include these bonuses.

2. **Consume-on-read side effects** (marshal.py:867,889). `get_attack_modifier()` zeroes `strategic_combat_bonus` and `counter_punch_ready` on read. No guard prevents double-call — second call silently returns a lower modifier.

3. **Drill state cleared in BOTH combat.py AND marshal.py** (combat.py:341-345 vs marshal.py:858-861). `combat.py` clears drill fields after reading; `get_attack_modifier()` reads but does NOT clear. Intentional but fragile.

4. **Battle report snapshot duplicates modifier knowledge** (battle_report.py:21-231). `snapshot_attacker_modifiers` re-derives every modifier independently of `get_attack_modifier()`. If a new modifier is added to one but not the other, they drift.

5. **Defense cap 1.75x not reflected in snapshot** (marshal.py:986 vs battle_report.py:143-231). Report shows uncapped total while combat uses capped value.

6. **Exhaustion penalty accessed via getattr+lambda fallback** (battle_report.py:78). Would silently return 0 if method renamed.

**Recommendation:** MAJOR. Create shared modifier registry/builder used by both `get_attack_modifier()` and snapshot functions. Add consumed flag to prevent double-read of strategic/counter-punch bonuses.

#### 13b: Casualty Distribution in Multi-Marshal Battles

**Files analyzed:** executor.py (lines 746-856, 4420-4812), combat.py (lines 1019-1212)

**Key findings:**

1. **Two entirely separate post-combat paths** (executor.py:4672-4810). Coordinated battles call `resolve_battle(apply_casualties=False)` then manually handle ~140 lines of post-combat effects. Solo battles handle everything inside `resolve_battle()`. This is ~140 lines of duplicated game logic.

2. **Pursuit damage floor inconsistency** — Solo path floors at `max(1000, ...)` (combat.py:694). Coordinated path floors at `max(0, ...)` (executor.py:4788). **Coordinated pursuit can kill defenders; solo pursuit cannot.**

3. **FORCED_RETREAT_THRESHOLD duplicated** — Defined as constant in combat.py:74 AND redefined as local variable in executor.py:4745.

4. **`_get_casualty_participants` vs `get_battle_participants` near-duplicate** (executor.py:746-790 vs relationship.py:109-149). Nearly identical logic, could drift.

5. **Morale applied uniformly in coordinated path** (executor.py:4699,4708). A 1000-troop reinforcer gets the same morale hit as the 30000-troop primary.

**Recommendation:** MAJOR. Fix pursuit floor inconsistency. Extract shared post-combat helpers. Consolidate participant functions.

#### 13c: Battle Report Generation

**Key findings:**

1. **Double observation generation** — combat.py:833 creates initial observation, executor.py:4913-4916 re-picks. Re-pick replaces but never augments — can lose relevant first-pass info.

2. **Re-pick priorities favor coordination over combat-critical events** (battle_report.py:561-602). Combined arms triangle (P0.5) fires before mutual destruction (P1) or fortification loss (P2).

3. **Bombardment path skips battle_report entirely** (executor.py:3191-3500). No Berthier observations for bombardment-heavy strategies.

**Recommendation:** MINOR/MODERATE. Re-order priorities so mutual destruction fires before coordination.

#### 13d: Forced Retreat and Movement After Combat

**Key findings:**

1. **Recklessness preserved through army break/respawn** (marshal.py:525-551). `clear_combat_transient_state()` does NOT clear recklessness. Broken cavalry keep momentum through the break cycle.

2. **Reinforcer retreat bypasses `move_to()`** (executor.py:5028). Direct `p.location = origin` skips state clearing that `move_to()` handles (holding_position, cavalry defensive tracking).

3. **Broken army teleportation has NO attrition** while normal retreat has halved attrition. Intentional (broken armies at 3-10% strength) but undocumented.

**Recommendation:** MODERATE. Reset recklessness on army break. Use `move_to()` for reinforcer retreat.

#### 13e: Combat → Diplomacy Interaction (CRITICAL)

**Files analyzed:** executor.py (lines 4950-5258, 10585-10790, 4573-4607), diplomacy.py, coalition.py

**Key findings:**

1. **CRITICAL: Auto-bombardment kill adds decisive_victory threat unconditionally** (executor.py:4597-4598). Does `add_threat(world, 5, "decisive_victory")` without checking casualty ratio > 2:1 or total > 10k. Every bombardment kill inflates coalition threat by +5 extra.

2. **CRITICAL: Auto-bombardment kill inflates war score** (executor.py:4581). Passes `defender_casualties=int(pre_battle_defender_strength)` (the entire army, not actual casualties) to `record_diplo_battle`.

3. **MAJOR: Garrison combat has zero diplomacy wiring** (executor.py:2772+). `_resolve_garrison_combat` does NOT call `record_diplo_battle`, `add_threat`, or `add_war_exhaustion_from_battle`. Capturing a capital via garrison assault produces no war score or threat change.

4. **Three separate implementations of post-combat diplomacy** across `_execute_attack`, `_execute_glorious_charge`, and auto-bombardment kill. Each reimplements war score, threat, and exhaustion independently.

5. **Authority modification simplified in bombardment** (executor.py:4586-4590). Uses fixed +5/-5 without outnumbered/capital checks that the other paths apply.

**Recommendation:** CRITICAL. Extract `_apply_post_combat_diplomacy()` shared function. Fix unconditional decisive victory. Fix inflated war score. Add diplomacy wiring to garrison combat.

---

### 14: Diplomacy Engine

#### 14a: Diplomatic State Machine

**Files analyzed:** diplomacy.py (lines 16-268, 1346-1501, 1773-1856, 2042-2182)

**Key findings:**

1. **Asymmetric upgrade vs downgrade** (diplomacy.py:28-39). Upgrades allow non-adjacent jumps (PEACE to ALLIANCE in one step); downgrades must be strictly adjacent. Building is fast, dismantling is slow.

2. **ARMISTICE has no voluntary exit** (diplomacy.py:34-39). Only auto-expires after 5 turns. Player cannot voluntarily break armistice early.

3. **War cascade bypasses relation penalties** (diplomacy.py:1209,1269). Cascade-joined wars skip the -30 direct relation penalty, -15 indirect penalty, and threat generation that `declare_war()` applies. Only a -20 relation penalty is applied.

4. **5+ sites directly modify `diplomatic_states`** without centralized helper. Each site must independently handle war_start_turns, active treaty removal, and armistice cleanup.

**Recommendation:** MODERATE. Extract `set_diplomatic_state()` helper for common bookkeeping across all state change sites.

#### 14b: Acceptance Formula

**Files analyzed:** diplomacy.py (lines 107-206, 631-882)

**Key findings:**

1. **War score sign handling** (diplomacy.py:666-672). Adjusts sign based on alphabetical key ordering. Correct but subtle — previously a bug source.

2. **Relation modifier dampened during war** — from /2 to /4, capping at +/-10 instead of +/-30. Only documented in comments, no named constant.

3. **Diplomat skill bonus uncapped upward** (diplomacy.py:758). `max(-8, (proposer_skill - target_skill) * 2)`. Talleyrand (skill 10) vs Einsiedel (skill 4) = +12 permanent advantage.

4. **Sweetener cap at 60, demands uncapped** (diplomacy.py:223,733). Arbitrarily harsh demands always win.

**Recommendation:** LOW. Formula is well-tested (145+ tests). Document effective ranges of each component.

#### 14c: AI Diplomacy Decision-Making

**Files analyzed:** ai_diplomacy.py (lines 573-757, 1300-1568)

**Key findings:**

1. **Exploitable priority order** (ai_diplomacy.py:652-724). P1 (losing) checked before all others. Keeping war score between -39 and -11 avoids P1 while still winning, preventing AI from suing for peace.

2. **Stalemate counter easily reset** (ai_diplomacy.py:354-365). Win a single battle to push war_score above 10, resetting the counter. Repeat indefinitely.

3. **Capital capture blocks ALL AI proposals** (ai_diplomacy.py:604-610). Defeated nations can't negotiate, creating diplomatic deadlocks.

4. **AI-AI diplomacy simplified** (ai_diplomacy.py:1550-1565). Uses acceptance formula with empty sweeteners/demands/clauses. No AI-AI term negotiation.

5. **P8 harsh demands self-defeating** (ai_diplomacy.py:720-731). Dominant AI generates harsh demands, then `_reduce_p8_demands()` iteratively weakens them when acceptance < 20. Fallback is "minimal peace + 200g" with `_force_send=True`.

**Recommendation:** MODERATE. Allow capital-captured nations to propose at P1. Document stalemate counter as intentional or add minimum floor.

#### 14d: Coalition Lifecycle

**Files analyzed:** coalition.py (lines 95-1141)

**Key findings:**

1. **Brewing can be canceled and restarted indefinitely** (coalition.py:978-986). No "brewing cooldown" — player oscillating threat around 40-60 can perpetually prevent formation.

2. **Instant override at 80+ during brewing** (coalition.py:993-994). Good design preventing cheese during 3-turn countdown.

3. **War exhaustion +8/turn** (coalition.py:944). Max 200. Coalition loyalty penalty fully negated at WE=150 (~19 turns). Self-limiting design.

4. **British subsidy goes to LOWEST-relation partner** (coalition.py:344-356). Counterintuitive but represents buying loyalty from most reluctant ally.

5. **Member friction -2/turn per pair** (coalition.py:950-955). Post-coalition relations severely damaged, making repeat coalitions harder.

**Recommendation:** LOW. Well-balanced system. Brewing oscillation exploit partially mitigated by BREWING_CANCEL_THRESHOLD.

#### 14e: War Score Calculation

**Files analyzed:** diplomacy.py (lines 319-468, 1506-1561)

**Key findings:**

1. **Territory score is position-based, not cumulative** (diplomacy.py:335-343). Reflects CURRENT control, not historical. Recapturing immediately resets score.

2. **POTENTIAL DEAD CODE: War score decay value manipulation** (diplomacy.py:419-438). `apply_war_score_decay()` modifies `world.war_scores`, then `recalculate_war_scores()` overwrites with fresh calculation. The direct score value decay is effectively a no-op. However, the battle record pruning at 10 turns (lines 411-417) IS useful as the actual decay mechanism.

3. **Decisive battle cap of 2 per war** — each adds +/-10 (cap 20 total). Requires > 10k casualties and > 2:1 ratio.

4. **Minimum 1k casualty threshold** (diplomacy.py:1532-1534). Small skirmishes don't register for war score.

**Recommendation:** MODERATE. Remove the dead score value manipulation (lines 419-438) or document why it exists. Keep battle record pruning.

#### 14f: Talleyrand Sabotage System

**Files analyzed:** diplomatic_defiance.py (lines 1-769)

**Key findings:**

1. **Cooldown fully suppresses defiance** (diplomatic_defiance.py:50-52). Returns 0.0 during cooldown, bypassing SCHEMER_FLOOR of 2%. Comment says "never fully tamed" but cooldown fully tames him temporarily.

2. **Sabotage type selection is deterministic** (diplomatic_defiance.py:193-243). Priority-based with no randomness. Experienced players can predict and avoid specific sabotage types.

3. **Discovery reaches 100% by turn 6** (diplomatic_defiance.py:283-290). 40% base + 10%/turn. Sabotage ALWAYS discovered eventually.

4. **Replace-with-Loyalist is irreversible** (diplomatic_defiance.py:585-600). Skill drops from 10 to 6, permanently reducing acceptance formula bonus by 8 points.

5. **Confront/overlook trust asymmetry** (-10 confront vs +3 overlook). Creates downward spiral toward redemption event (trust <= 20).

6. **`turn_number` fallback at lines 493, 612** — references non-existent field, falls back to `current_turn`. Dead defensive code from early development.

**Recommendation:** LOW. Well-designed system. Remove `turn_number` fallback. Consider adding randomness to sabotage type selection.

---

### 15: Turn Processing & World State

#### 15a: Turn Processing Order (44 Steps)

**Files analyzed:** world_state.py (lines 3622-4005), turn_manager.py (lines 44-243), executor.py (lines 1080-1104)

**Complete step sequence of `_advance_turn_internal()`:**

| # | Step | Key Ordering Dependency |
|---|------|------------------------|
| 1-9 | Clear per-turn flags, snapshot history | — |
| 10 | Process tactical states (drill/fortify) | Sees OLD turn number |
| 11-12 | Vindication decay, construction | — |
| 13 | **INCREMENT TURN COUNTER** | Steps above see old turn, below see new |
| 14-17 | Stability, supply attrition, garrison regen, bankruptcy | Bankruptcy uses PREVIOUS turn counter |
| 18-19 | Diplomacy processing, proposal resolution | — |
| 20 | Cooldown decrements | — |
| 21-22 | Vassal processing, clear battle tracking | **Vassal reads battles_this_turn BEFORE clear** |
| 23-24 | Coalition, AI-AI diplomacy | — |
| 25-26 | Dialogue auto-dismiss | — |
| 27-32 | Income, trade, continental system, reset AP, treaty clauses, tribute | **AP reset BEFORE treaty penalty** |
| 33-36 | Bankruptcy check, manpower, admin reset, attack tracking | Bankruptcy AFTER all income |
| 37-43 | AI futility, disobedience, cavalry, fog, snapshots | — |

**Key findings:**

1. **Turn counter increment splits pipeline** (world_state.py:3695). Steps 1-12 see old turn, steps 14+ see new turn. Only one comment documents this. Moving steps across boundary silently breaks behavior.

2. **5+ ordering dependencies documented only by inline comments** — e.g., "Fix 3" at line 3805 (vassal reads battles before clear), "Deep Audit Session 4 Fix 1" at line 3877 (AP reset before treaty clauses).

3. **Victory check in turn_manager runs BEFORE enemy phase** but `advance_turn()` still runs in game-over state, processing supply attrition, income, etc. for a game that's already over.

4. **Strategic orders execute BEFORE advance_turn** (turn_manager.py:132-141). Required for cannon fire detection (advance_turn clears battles_this_turn at step 22).

**Recommendation:** MEDIUM. Document ordering dependencies in a manifest at method top. Consider grouping related steps into sub-methods.

#### 15b: Action Economy

**Key findings:** Clean dual-pool design (combat AP 4 + admin AP 2). Treaty AP clauses correctly applied after reset. AI nations use single `nation_actions` dict. `_strategic_execution=True` correctly bypasses AP cost. No issues found.

**Recommendation:** LOW. Well-designed, no changes needed.

#### 15c: Enemy AI Turn Processing

**Files analyzed:** turn_manager.py (lines 548-640), enemy_ai.py (lines 627-900)

**Key findings:**

1. **Fixed nation order** — `["Britain", "Prussia", "Austria", "Saxony"]`. Britain always acts first, getting first pick of undefended regions. Systematic first-mover advantage.

2. **Cooldown decrement fixed at once-per-turn** (turn_manager.py:581). Previously was inside per-nation loop (4x tick bug), V2-20/21 fix.

3. **New EnemyAI() created each turn** (turn_manager.py:570-571). All per-turn tracking fresh. Cross-turn state persists only through WorldState.

4. **Three safety valves** in action loop: max_consecutive_skips, max_total_actions, max_free_actions. Prevents infinite loops.

5. **Aggressive stance change skipped on last AP** (enemy_ai.py:750-758). Good design — no follow-up budget to use the stance.

**Recommendation:** LOW-MEDIUM. Consider rotating nation processing order each turn for fairness.

#### 15d: Strategic Order Execution

**Key findings:** Clean two-pass system (non-interrupting first, then deferred). Only 1 interrupt per turn — reasonable UX limit. "Investigate" cannon fire cancels order and attacks with no AP cost. Trust penalty (-2) for "continue" after cannon fire.

**Recommendation:** LOW. Well-designed. No changes needed.

#### 15e: Supply Attrition

**Key findings:**

1. **Home territory 50% bonus** (world_state.py:2410-2411). French regions get 1.5x supply capacity.
2. **Death-ball penalty** — +1% per marshal beyond first, triggers at 3+ marshals even under capacity.
3. **6% hard cap** on total attrition.
4. **0-strength elimination is permanent** (world_state.py:2437-2448). Unlike combat (broken state), attrition skips to death. Harsh for player marshals in remote regions.

**Recommendation:** LOW. Clean formula. Consider warning players via dispatch when marshals are in high-attrition zones.

#### 15f: Manpower Regeneration

**Key findings:** Clean single-source in `get_manpower_regen_rates()`. Infantry 2500/turn (affected by war exhaustion), cavalry 250+terrain, artillery 150+urban. Pools capped at 100k/30k/20k. Nations missing from `DEFAULT_MANPOWER_POOLS` silently skipped (no warning).

**Recommendation:** LOW. Add warning log for skipped nations.

#### 15g: Cooldown Management (14 Dictionaries)

**Complete catalog:**

| # | Cooldown | Decremented By | Location |
|---|----------|---------------|----------|
| 1 | `ai_failed_action_cooldowns` | `ai.decrement_all_cooldowns()` | turn_manager |
| 2 | `ai_refortify_cooldown` | `ai.decrement_all_cooldowns()` | turn_manager |
| 3 | `ai_attack_futility` | Inline -1/turn + reset | advance_turn |
| 4 | `armistice_cooldowns` | `process_diplomacy_turn()` | External |
| 5 | `armistice_turns` | `process_diplomacy_turn()` | External |
| 6 | `player_proposal_cooldowns` | `_decrement_proposal_cooldowns()` | advance_turn |
| 7 | `ai_proposal_cooldowns` | `_decrement_ai_proposal_cooldowns()` | advance_turn |
| 8 | `proactive_suggestion_cooldowns` | `_decrement_proactive_cooldowns()` | advance_turn |
| 9 | `vassal_investment_cooldowns` | `decrement_vassal_cooldowns()` | advance_turn |
| 10 | `vassal_release_cooldowns` | `decrement_vassal_cooldowns()` | advance_turn |
| 11 | `talleyrand_defiance_cooldown` | Inline `-= 1` | advance_turn |
| 12 | `coalition_cooldown` | `process_coalition_turn()` | External |
| 13 | `ultimatum_cooldowns` | `_decrement_ultimatum_cooldowns()` | advance_turn |
| 14 | `turns_below_threshold` | `process_diplomacy_turn()` | External |

**Key findings:**

1. **4 different decrement patterns:** inline, helper method, external module, AI module. Adding a new cooldown requires knowing which pattern to follow.
2. **`_decrement_ai_proposal_cooldowns()` has side effect** — also expires queued proposals older than 3 turns (world_state.py:4573). Hidden in a method named "decrement cooldowns."
3. **`talleyrand_defiance_cooldown` is the only inline decrement** — all 4 diplomatic cooldowns use dedicated helpers. Inconsistent.
4. **No cooldown decremented twice per turn** — verified across all sites. V2-20/21 fix is correct.

**Recommendation:** MEDIUM. Centralize at least the 5 advance_turn cooldown decrements into one method. Document the complete catalog in a comment.

#### 15h: Morning Dispatch Generation

**Key findings:**

1. **Runs AFTER all processing** (executor.py:1095-1096). Sees fully processed new-turn state — correct timing.
2. **`player_nation = "France"` HARDCODED** (dispatch.py:51). TODO comment for post-EA.
3. **Dispatch event whitelist** (`_DISPATCH_EVENT_TYPES`, dispatch.py:378). Only 22 event types pass through. New types silently dropped.
4. **Fog-filtered enemy strength estimation** — uses RegionIntel snapshots, not live data. Correct.

**Recommendation:** LOW. Document the dispatch event whitelist more prominently. Add test for event type coverage.

---

### 16: Fog of War, Intel, LLM, Parsing

#### 16a: Fog of War Consistency

**Files analyzed:** intel.py, intel_report.py, campaign_log.py, main.py, strategic_parser.py, diplomatic_ledger.py

**Key findings:**

1. **MAJOR FOG LEAK: Strategic parser reveals enemy positions** (strategic_parser.py:88,577,610). `resolve_direction()` and `_add_interpretation()` call `world.get_enemies_of_nation()` which returns ALL enemies omnisciently. When player says "march to the front," the parser resolves using actual positions of fogged enemies. `interpreted_target` and `alternatives` list flow back via clarification popup, revealing enemy names/locations the player shouldn't know.

2. **MINOR FOG LEAK: map_data in LLM game state** (main.py:88-98). Lists ALL marshals in every region with NO fog check. Only used for LLM prompt context, not displayed directly, but transmits data that shouldn't be available.

3. **Fog filtering is CORRECT in:** intel_report.py (tiers by visibility), campaign_log.py (per-event fog checks), main.py:384-438 (tactical event filtering), main.py:72-86 (LLM enemies), diplomatic_ledger.py:67-98 (nation visibility aggregation).

4. **Campaign log timing subtlety** (campaign_log.py:249-252). Uses CURRENT visibility, not event-time visibility. A battle at FULL visibility last turn could be invisible in the log after decay to PARTIAL.

**Recommendation:** MAJOR. Filter `get_enemies_of_nation` through fog in strategic_parser.py functions resolving generic/directional targets. Filter map_data marshals in LLM game state.

#### 16b: Intel System Architecture

**Key findings:** Clean dual-path design (REFRESH only upgrades, DECAY only downgrades). 10 fields fully serialized. Intel source priority well-ordered. Strength band system works correctly.

**Recommendation:** LOW. Solid architecture. No changes needed.

#### 16c: Mock Parser vs Real LLM Coverage

**Files analyzed:** llm_client.py (mock parser lines 442-919), prompt_builder.py, validation.py

**Key findings:**

1. **Mock handles but LLM doesn't teach:** cheat commands, save/load, debug, form_square/break_square. Harmless since these would never reach the LLM.

2. **37 VALID_ACTIONS but mock handles ~30 paths.** 7 actions (diplomatic_feasibility, diplomatic_advisory, diplomatic_error, etc.) only reachable through the diplomatic sub-parser.

3. **Confidence threshold prevents LLM help** (llm_client.py:48). Threshold is 0.7, but action-only matches score 0.8. Commands like "attack" (no marshal/target) never reach the LLM even though it could provide better interpretation.

4. **Vassal keywords hardcoded to specific nations** (llm_client.py:778-797). New vassal nations from modding won't be recognized by mock parser, and the high confidence prevents LLM fallback.

**Recommendation:** MEDIUM. Raise LLM fallback threshold to 0.85. Add diplomatic few-shot examples to LLM prompt.

#### 16d: Command Parsing Edge Cases

**Key findings:**

1. **Keyword ordering fragile** (llm_client.py:650-800). ~150 lines of `elif` chain where order determines priority. Adding a keyword in the wrong position breaks existing parsing.

2. **"hold" always becomes strategic** (strategic_parser.py:202-205). Always upgraded to 2 AP strategic HOLD. Players wanting 1AP hold must use "defend."

3. **Possessive form breaks marshal matching** (llm_client.py:583-586). `\b` regex means "Davout's attack" won't match "Davout."

4. **Region names use substring matching without word boundaries** (llm_client.py:834-871). "berlin" matches any word containing "berlin."

**Recommendation:** MEDIUM. Add word-boundary matching for regions. Add integration tests verifying keyword ordering.

#### 16e: Vassal System Architecture

**Files analyzed:** vassal.py

**Key findings:**

1. **7-modifier loyalty formula** — autonomy drift, garrison, gold investment, shared enemy, battle wins/losses, relation modifier, coalition penalty. Clean and well-documented.
2. **Rebellion cascade** (vassal.py:486-489). One rebellion costs all other vassals -10 loyalty.
3. **Armistice-safe rebellion** (vassal.py:453-463). Rebels become independent without war if in ARMISTICE.
4. **Garrison loyalty docstring mismatch** (vassal.py:228 vs 255). Docstring says "+2 base" but code is "+5 base." Code gives much higher bonuses than documented.
5. **Battle result matching uses fragile string parsing** (vassal.py:293-298). Checks `"attacker" in result.lower() and "victory" in result.lower()`.

**Recommendation:** MINOR. Fix docstring mismatch. String-based battle matching works but could benefit from structured result format.

#### 16f: Campaign Log Event Lifecycle (Extended)

**Key findings:**

1. **40 event types logged, 24 whitelisted, 16 invisible.** Most important invisible types: `coalition_brewing_started`, `diplomatic_proposal_sent`, `ai_proposal_accepted/rejected`, `diplomatic_mission_started`.
2. **Event log rolling cap** at 500 events (world_state.py:583). Sufficient for 60-turn games.
3. **Duplicate event types:** `diplomatic_war_declared` and `war_declaration` both whitelisted with identical formatters. Consolidate.

**Recommendation:** MEDIUM. Add 5 most important invisible types to whitelist with fog filtering and formatting.

#### 16g: LLM Prompt Construction

**Key findings:** Clean prompt builder with ~300 token input target. Enemy data fog-filtered correctly. Geographic layout hardcoded (won't work with modded regions). No diplomatic few-shot examples. Good Berthier recovery prompt design.

**Recommendation:** LOW. Add 1-2 diplomatic examples. Filter map_data enemy marshals.

---

### 17: API Layer, Response Pipeline, Trust System

#### 17a: API Endpoint Audit (35 Endpoints)

**Files analyzed:** main.py (2,464 lines)

**Key findings:**

1. **13 POST endpoints, 22 GET endpoints.** Only POST endpoints consistently call `_include_popup_passthroughs`. GET endpoints never deliver pending popups.

2. **`/test` GET endpoint builds active_wars manually** (main.py:509-538) but never calls `_include_popup_passthroughs`. If client uses `/test` for heartbeat and a popup is pending, it's never delivered.

3. **No error handling on most GET endpoints.** `/status`, `/authority_status`, `/marshal_trust/{name}` would return 500 with stack trace on any error.

4. **`/load` endpoint has no try/except** (main.py:1761-1781). Load success + subsequent processing failure is unhandled.

5. **Mixed async/sync handlers.** `/respond_to_diplomatic_dialogue` is `async def` while peer handlers are `def`. FastAPI handles both, but inconsistency suggests copy-paste divergence.

6. **Popup delivery blocked during enemy_phase** (main.py:1056). Deferred popup only delivered on NEXT POST request. If next request is GET, popup stays stuck.

**Recommendation:** MODERATE. Add try/except to all GET endpoints. Standardize handler definitions.

#### 17b: Trust / Authority / Vindication Interaction

**Key findings:**

1. **Death spiral potential.** Low trust + low authority become self-reinforcing. Trust gains are double-modified: `base * trust_tier_multiplier * authority.get_trust_gain_modifier()`. With both low, recovery is severely penalized.

2. **Authority asymmetry** — drops -5 per right defiance, recovers +1/turn at best. A single defiance-right event takes 5+ turns of balanced play to recover.

3. **Vindication score feeds defiance at +10% per point** (defiance.py:55-56) but is capped at 40% total defiance chance. Vindication above +3 has zero marginal impact in most scenarios.

4. **`VindicationTracker.last_change_turn` tracked but decay never applied in vindication.py.** Decay logic may live in world_state.py advance_turn, but the tracker itself doesn't use the field.

5. **Two separate authority modifier systems** — `AuthorityTracker.get_obedience_modifier()` (authority.py:155) and defiance.py:61-67 authority tier system. Low authority gets double-penalized: more severe objections AND higher defiance chance.

**Recommendation:** MAJOR. Verify vindication decay is applied somewhere. Consider minimum trust gain floor to prevent permanent unrecoverable states.

#### 17c: Objection Layers (V1 + V2a + V2b)

**Key findings:**

1. **V1 `CONCERN_TO_SEVERITY` map marked "will be removed in V2b"** (objection_v2.py:120-126). V2b is complete. This is dead code.

2. **V1's `PERSONALITY_TRIGGERS` for literal are ALL empty/TODO** (personality.py:141-145). V2a's `evaluate_literal` has working triggers. The V1 path is dead for literal personality.

3. **Per-turn objection caps exist in TWO systems** — V1: global count (disobedience.py:27). V2a: per-marshal set. Both can fire on the same turn.

4. **Defiance uses hardcoded personality strings** (defiance.py:99-122). Checks `personality == 'aggressive'` rather than using Personality enum.

**Recommendation:** MODERATE. Remove dead `CONCERN_TO_SEVERITY`. Remove empty V1 literal triggers. Use Personality enum in defiance.py.

#### 17d: Personality System Architecture

**Key findings:**

1. **Personality stored as string, not enum.** Marshal objects store `self.personality = "aggressive"` but `personality.py` defines `Personality(Enum)`. Only `disobedience.py` uses the enum. All other systems use raw string comparisons.

2. **BALANCED and LOYAL personalities have no implementation anywhere.** `personality_modifiers.py:99-104` returns `{}`. `objection_v2.py:1138-1141` returns `ConcernLevel.NONE`. Future marshals with these personalities would be completely inert.

3. **Personality modifier lookup by name, not marshal** (personality_modifiers.py:88-105). Maps "aggressive" to `NEY_MODIFIERS`. A second aggressive marshal (e.g., Blucher) would get Ney-specific labels.

4. **Inline personality descriptions in main.py:1617** diverge from canonical `PERSONALITY_DESCRIPTIONS` in personality.py.

**Recommendation:** LOW-MODERATE. Use enum consistently. Reference canonical descriptions instead of inline duplicates.

#### 17e: Save/Load Robustness

**Key findings:**

1. **No schema validation on load** (save_manager.py:91-141). Checks format_version and `world_state` presence only. Corrupted marshal data passes load check, crashes during gameplay.

2. **Hard version break at v1→v2 only.** No migration path for future version 3.

3. **Transient state clearing is hardcoded** (save_manager.py:121-129). 7 specific fields cleared manually. New transient fields not in the list persist across save/load.

4. **`list_saves` reads ALL save files fully** (save_manager.py:153-180). No size limit protection.

**Recommendation:** MODERATE. Add transient field registry for auto-detection. Consider reading only metadata in list_saves.

#### 17f: Notification Lifecycle

**Key findings:**

1. **HIGH/CRITICAL notifications accumulate without limit.** Cap only evicts NORMAL priority. Long games can build up undismissable HIGH notifications.

2. **No deduplication.** Same notification type on consecutive turns creates separate entries.

3. **No expiry.** Turn 1 notifications persist at turn 100.

4. **`from_list` bypasses cap enforcement** (notifications.py:177-182). Corrupted saves with 1000+ notifications all loaded.

**Recommendation:** LOW-MODERATE. Add auto-expiry for NORMAL notifications. Add deduplication by type. Enforce cap in `from_list`.

#### 17g: War Status Panel Pipeline

**Key findings:**

1. **`build_active_wars` called TWICE per `/command` response.** Once in `_include_popup_passthroughs` (main.py:264-266), once explicitly (main.py:1039-1040). Second overwrites first. Wasteful but not buggy.

2. **`ARMISTICE_DURATION = 5` hardcoded** (war_status.py:5) with "must match diplomacy.py" comment. Cross-file constant that could drift.

3. **War score sign convention depends on diplo key ordering** (war_status.py:73-74). Fragile but correct.

**Recommendation:** MODERATE. Cache `build_active_wars` result. Extract shared ARMISTICE_DURATION constant.

#### 17h: Response Shape Analysis (MAJOR)

**Compared 5 POST endpoint responses:**

| Key | `/command` | `/respond_to_objection` | `/capture_choice` | `/respond_to_redemption` | `/cancel_order` |
|-----|:----------:|:-----------------------:|:------------------:|:------------------------:|:---------------:|
| `success` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `message` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `game_state` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `events` | ✓ | ✓ | ✓ | ✗ | ✗ |
| `action_summary` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `diplomatic_points` | ✓ | ✗ | ✗ | ✗ | ✗ |
| `threat_level` | ✓ | ✗ | ✗ | ✗ | ✗ |
| `notifications` | conditional | conditional | ✗ | ✗ | ✗ |
| popup keys (7) | ✓ | ✓ | ✓ | ✓ | ✓ |

**Key finding:** Diplomatic top-bar fields (`diplomatic_points`, `max_diplomatic_points`, `threat_level`, `coalition_brewing`, `pending_envoy_count`) are ONLY in `/command` response. During objection/popup interactions, the top bar goes stale.

**Recommendation:** MAJOR. Define `build_base_response(world)` containing all universal keys. Each endpoint adds specific fields on top.

---

## Extended Severity Summary

### All Findings by Severity

#### CRITICAL (2)

| # | Finding | Location |
|---|---------|----------|
| 1 | Auto-bombardment kill adds decisive_victory threat unconditionally (+5 every kill) | executor.py:4597-4598 |
| 2 | Auto-bombardment kill inflates war score using full defender strength as casualties | executor.py:4581 |

#### MAJOR (9)

| # | Finding | Location |
|---|---------|----------|
| 3 | Garrison combat has zero diplomacy/war score/threat wiring | executor.py:2772+ |
| 4 | Strategic parser leaks fogged enemy positions via direction resolution | strategic_parser.py:88,577,610 |
| 5 | No base response type — diplomatic top-bar fields missing from popup endpoints | main.py (13 endpoints) |
| 6 | Trust/authority death spiral — double-modified trust gains, asymmetric recovery | authority.py, defiance.py |
| 7 | Combat modifier chain — snapshot drifts from actual calculation | battle_report.py vs marshal.py |
| 8 | Three separate post-combat diplomacy implementations | executor.py (3 locations) |
| 9 | ~140 lines duplicated post-combat logic (solo vs coordinated) | executor.py:4672-4810 |

#### MEDIUM/MODERATE (13)

| # | Finding | Location |
|---|---------|----------|
| 10 | Pursuit damage floor 0 (coordinated) vs 1000 (solo) | executor.py:4788 vs combat.py:694 |
| 11 | 14 cooldown dicts across 4 decrement patterns, no centralized catalog | world_state.py |
| 12 | 44-step turn pipeline with 5+ undocumented ordering dependencies | world_state.py:3622-4005 |
| 13 | 16 campaign log event types invisible (including coalition brewing) | campaign_log.py:83-120 |
| 14 | War score decay value manipulation is dead code | diplomacy.py:419-438 |
| 15 | Capital capture blocks all AI proposals (diplomatic deadlock) | ai_diplomacy.py:604-610 |
| 16 | Diplomatic state machine has 5+ direct modification sites | diplomacy.py |
| 17 | Recklessness preserved through army break/respawn | marshal.py:525-551 |
| 18 | Reinforcer retreat bypasses move_to() | executor.py:5028 |
| 19 | Dead backward-compat code in objection system | objection_v2.py:120-126 |
| 20 | Save/load no schema validation, manual transient field list | save_manager.py |
| 21 | Mock parser keyword ordering fragile (~150-line elif chain) | llm_client.py:650-800 |
| 22 | LLM fallback threshold prevents borderline commands from reaching LLM | llm_client.py:48 |

#### LOW/MINOR (12)

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

---

## Updated Refactoring Roadmap

*Original R1-R10 sessions preserved. New sessions R11-R16 added from extended deep dives.*

#### Session R11: Post-Combat Diplomacy Unification (CRITICAL)
- **What:** Extract `_apply_post_combat_diplomacy(marshal, enemy, battle_result, world, conquered, battle_region)` shared function
- **Why:** Fixes 2 CRITICAL bugs (auto-bombardment threat inflation + war score inflation) and 1 MAJOR (garrison diplomacy gap). Eliminates triple-implementation drift.
- **Effort:** ~200 new lines, refactor 3 combat paths + add garrison wiring. 1 session.
- **Risk:** Low — each path already computes the values, just needs consolidation.
- **Dependencies:** Benefits from R1 (post-combat pipeline) but can be done independently.
- **Independent?** Yes

#### Session R12: Strategic Parser Fog Fix (MAJOR)
- **What:** Filter `get_enemies_of_nation` through fog in `resolve_direction()` and `_add_interpretation()`. Filter map_data marshals in `_build_game_state_for_llm()`.
- **Why:** Fixes exploitable fog leak where players discover enemy positions through direction resolution.
- **Effort:** ~30 new lines, modify 3 functions. Half session.
- **Risk:** Low — may reduce parser usefulness for vague commands (fewer targets to resolve against).
- **Dependencies:** None
- **Independent?** Yes

#### Session R13: Response Pipeline Standardization (MAJOR)
- **What:** Create `build_base_response(world)` returning all universal keys (success, message, game_state, diplomatic_points, threat_level, notifications, popup keys). All 13 POST endpoints build on top of this base.
- **Why:** Eliminates stale top-bar during popup interactions. Prevents response shape inconsistencies. Supersedes R4.
- **Effort:** ~150 new lines, refactor 13 endpoints. 1 session.
- **Risk:** Medium — must verify Godot handles consistent response shape.
- **Dependencies:** None
- **Independent?** Yes

#### Session R14: Trust Recovery Floor (MAJOR)
- **What:** Add minimum trust gain floor to prevent unrecoverable death spiral. Verify vindication decay is applied. Document authority modifier interaction.
- **Why:** Low trust + low authority creates self-reinforcing death spiral with no recovery path.
- **Effort:** ~50 new lines, modify 2-3 files. Half session.
- **Risk:** Low — balance change only.
- **Dependencies:** None
- **Independent?** Yes

#### Session R15: Combat Modifier Registry (MAJOR)
- **What:** Create shared modifier registry used by both `get_attack_modifier()` and `snapshot_attacker_modifiers()`. Add consumed flags to prevent double-read.
- **Why:** Eliminates drift between actual combat modifiers and battle report display.
- **Effort:** ~100 new lines, refactor marshal.py + battle_report.py. 1 session.
- **Risk:** Medium — must verify all 5 combat paths still produce correct modifiers.
- **Dependencies:** Benefits from R1 but independent.
- **Independent?** Yes

#### Session R16: Campaign Log + Cleanup (MEDIUM)
- **What:** Add 5 most important invisible event types to CAMPAIGN_LOG_TYPES. Remove dead code (war score decay, CONCERN_TO_SEVERITY, turn_number fallback). Fix vassal docstring. Consolidate duplicate war declaration events.
- **Why:** Completes the campaign log narrative. Removes maintenance traps.
- **Effort:** ~80 new lines, modify 4 files. Half session.
- **Risk:** Low — additive changes + dead code removal.
- **Dependencies:** None
- **Independent?** Yes

### Updated Dependency Graph

```
R1 (post-combat pipeline) ──→ R6 (executor split: combat)
R2 (conftest.py)                         ↓
R3 (cooldown/popup)          R7 (executor split: diplomatic)
R4 → SUPERSEDED BY R13                   ↓
R5 (scaling index) ──→ R8 (AI fog)      R9 (dialogue manager)
                                          ↓
R11 (combat→diplo unify) ←── R1         R10 (executor split: remaining)
R12 (parser fog fix)
R13 (response pipeline v2)
R14 (trust recovery floor)
R15 (modifier registry)
R16 (campaign log + cleanup)
```

Sessions R1-R3, R5, R11-R16 are **fully independent** and can be done in any order or in parallel.

### Priority Ordering (All 16 Sessions)

| Priority | Session | Severity | Effort |
|----------|---------|----------|--------|
| 1 | **R11** Post-combat diplomacy unification | CRITICAL | 1 session |
| 2 | **R1** Post-combat pipeline | CRITICAL | 1 session |
| 3 | **R12** Strategic parser fog fix | MAJOR | ½ session |
| 4 | **R2** Test conftest.py | CRITICAL | 2 hours |
| 5 | **R13** Response pipeline standardization | MAJOR | 1 session |
| 6 | **R14** Trust recovery floor | MAJOR | ½ session |
| 7 | **R15** Combat modifier registry | MAJOR | 1 session |
| 8 | **R5** Scaling index | CRITICAL (pre-80) | ½ session |
| 9 | **R3** CooldownManager + PopupQueue | MAJOR | 1 session |
| 10 | **R16** Campaign log + cleanup | MEDIUM | ½ session |
| 11 | **R6** Executor split phase 1 | MAJOR | 1 session |
| 12 | **R7** Executor split phase 2 | MAJOR | 1 session |
| 13 | **R8** AI fog integration | CRITICAL (pre-80) | 4-6 days |
| 14 | **R9** Dialogue manager | MAJOR | 1-2 sessions |
| 15 | **R10** Executor split phase 3 | MINOR | 1 session |

---

## Extended Metrics Summary

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
| API endpoints | 35 (13 POST, 22 GET) |
| Display name translation maps | 7 |
| Invisible campaign log event types | 16 |
| Circular dependencies | 0 |
| Layer violations | 1 (minor) |
| Golden Rule compliance | 100% (with documented exceptions for target-type modifiers) |
| Fog of war leaks found | 2 (strategic parser MAJOR, map_data MINOR) |
| Dead code sites | 3 (war score decay, CONCERN_TO_SEVERITY, turn_number fallback) |
| Code conventions score | 8.6/10 average |
| **Total findings this audit** | **34** (2 CRITICAL, 9 MAJOR, 13 MODERATE, 12 LOW) |
