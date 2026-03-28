# Architecture Refactoring Plan

**Source:** `docs/ARCHITECTURE_AUDIT_REPORT.md` (12-pass + 35 deep dives + 6 extended audits)
**Scope:** 20 refactoring items (R1-R20) → 21 implementation sessions across 7 phases
**Goal:** Eliminate 10 structural root causes responsible for ~240 of ~450 historical bugs
**Estimated Total Effort:** ~55-65 hours

---

## Table of Contents

1. [Dependency Graph](#dependency-graph)
2. [Phase A: Foundations (Sessions 1-3)](#phase-a-foundations-sessions-1-3)
3. [Phase B: Response & Data Access (Sessions 4-6)](#phase-b-response--data-access-sessions-4-6)
4. [Phase C: Infrastructure (Sessions 7-9)](#phase-c-infrastructure-sessions-7-9)
5. [Phase D: Executor Split (Sessions 10-13)](#phase-d-executor-split-sessions-10-13)
6. [Phase E: Godot Frontend (Sessions 14-16)](#phase-e-godot-frontend-sessions-14-16)
7. [Phase F: AI Fog Integration (Sessions 17-20)](#phase-f-ai-fog-integration-sessions-17-20)
8. [Phase G: Modding (Session 21)](#phase-g-modding-session-21)
9. [Summary Table](#summary-table)
10. [Verification Strategy](#verification-strategy)
11. [Documentation Updates](#documentation-updates)

---

## Dependency Graph

```
R1 (post-combat pipeline) ──→ R10 (executor split: combat)
R2 (war-state helpers)                    ↓
R3 (conftest.py)             R11 (executor split: diplomatic+strategic)
R4 (response pipeline)                    ↓
R5 (fog-filtered access)    R12 (dialogue manager)
R6 (cooldown/popup)                       ↓
R7 (display registry)       R13 (executor split: remaining)
R8 (campaign log test)
R9 (scaling index) ──→ R14 (AI fog, 4 sessions)
R15, R17, R19-R20 fully independent of each other and backend sessions
R16 depends on R15 (popup base class needed first)
R18 depends on R7+R8 (display/log maps needed for enforcement)
```

**Parallelism:** Sessions 1-8, 14-15, 21 have no inter-dependencies and can be done in any order. Sessions 10-13 are strictly sequential. Sessions 17-20 are sequential and depend on Session 8.

---

## Phase A: Foundations (Sessions 1-3)

### Session 1: R3 — Test conftest.py

| Field | Value |
|-------|-------|
| **Root Cause** | RC-5: No Shared Test Fixtures |
| **Priority** | CRITICAL |
| **Effort** | ~2 hours |
| **Risk** | ZERO — purely additive |
| **Bugs Prevented** | ~22 serialization + maintenance multiplier on ALL future changes |
| **Dependencies** | None. Do this first so all subsequent sessions benefit. |

**Problem:** 79 of 94 test files duplicate `_make_world()` / `_make_marshal()` factories. ~2,460 lines of duplicated factory code across 3 different patterns. Adding ONE new Marshal field requires updating factories in ~79+ files.

**Files to Create:**
- `tests/conftest.py`

**Files to Reference (read-only):**
- `backend/models/marshal.py` — Marshal constructor signature, all current fields
- `backend/models/world_state.py` — WorldState constructor, 92 persistent fields
- `backend/commands/executor.py` — CommandExecutor constructor
- `tests/test_adjacent_support.py:22-52` — Pattern 1: keyword-override helper with skills dict
- `tests/test_artillery.py:40-60` — Pattern 2: setattr-based world factory + typed marshal factories
- `tests/test_battle_report.py:27-31` — Pattern 3: minimal kwargs passthrough
- `tests/test_bombardment.py:25-53` — Pattern 4: scenario-level setup helpers

**Implementation Steps:**

1. **Create `MarshalFactory` class** with static methods. Each method provides sensible defaults and accepts `**overrides` for test-specific customization:
   ```python
   class MarshalFactory:
       @staticmethod
       def infantry(name="TestInf", location="Paris", strength=30000,
                    nation="France", personality="cautious", **overrides):
           """Standard infantry marshal with balanced skills."""
           defaults = {
               "movement_range": 1, "tactical_skill": 7,
               "skills": {"tactical": 7, "shock": 7, "defense": 7,
                          "logistics": 7, "administration": 7, "command": 7},
               "cavalry": False, "artillery": False,
               "spawn_location": location,
           }
           defaults.update(overrides)
           return Marshal(name=name, location=location, strength=strength,
                          personality=personality, nation=nation, **defaults)

       @staticmethod
       def cavalry(name="TestCav", location="Paris", strength=8000,
                   nation="France", personality="aggressive", **overrides): ...

       @staticmethod
       def artillery(name="TestArt", location="Paris", strength=5000,
                     nation="France", personality="cautious", **overrides): ...

       @staticmethod
       def enemy(name="TestEnemy", location="Berlin", strength=30000,
                 nation="Prussia", personality="cautious", **overrides): ...
   ```

2. **Create `WorldFactory` class** with static methods:
   ```python
   class WorldFactory:
       @staticmethod
       def basic(player_nation="France", **overrides):
           """Minimal world with default regions. No marshals added."""
           world = WorldState()
           world.player_nation = player_nation
           for k, v in overrides.items():
               setattr(world, k, v)
           return world

       @staticmethod
       def with_marshals(marshal_list, player_nation="France", **overrides):
           """World with provided marshals registered."""
           world = WorldFactory.basic(player_nation=player_nation, **overrides)
           for m in marshal_list:
               world.marshals[m.name] = m
           return world

       @staticmethod
       def with_war(nation_a="France", nation_b="Prussia", **overrides):
           """World with WAR state between two nations."""
           world = WorldFactory.basic(**overrides)
           key = tuple(sorted([nation_a, nation_b]))
           world.diplomatic_states[key] = "WAR"
           world.war_start_turns[key] = world.current_turn
           return world

       @staticmethod
       def diplomatic(player_nation="France", **overrides):
           """World with diplomacy infrastructure (diplomats, DP, etc.)."""
           ...
   ```

3. **Create standard pytest fixtures** (auto-discovered by all test files):
   ```python
   @pytest.fixture
   def world():
       return WorldFactory.basic()

   @pytest.fixture
   def executor():
       return CommandExecutor()

   @pytest.fixture
   def game_state(world):
       return {"world": world}

   @pytest.fixture
   def combat_resolver():
       return CombatResolver()
   ```

4. **Write 10-15 factory validation tests** ensuring factories produce valid objects:
   - `test_marshal_factory_infantry_defaults` — correct type, strength, nation, skills
   - `test_marshal_factory_cavalry_flags` — cavalry=True, movement_range=2
   - `test_marshal_factory_artillery_flags` — artillery=True
   - `test_marshal_factory_overrides_work` — kwargs override any default
   - `test_marshal_factory_enemy_defaults` — different nation, location
   - `test_world_factory_basic_has_regions` — 19 regions present
   - `test_world_factory_with_war_state` — diplomatic state is WAR
   - `test_world_factory_with_marshals_registers_correctly`
   - `test_game_state_fixture_shape` — has "world" key, world is WorldState
   - `test_factories_serialize_roundtrip` — to_dict/from_dict works for factory outputs

5. **Migrate 5 high-churn test files** as proof of concept. Replace local `_make_marshal`/`_make_world` with conftest fixtures. Selected files (frequently modified in prior audits):
   - `tests/test_battle_report.py`
   - `tests/test_coordination_bonus.py`
   - `tests/test_relationship_formula.py`
   - `tests/test_vindication_system.py`
   - `tests/test_fog_of_war.py`

6. **Add migration guide** as docstring at top of conftest.py:
   ```python
   """
   Shared test factories and fixtures.

   MIGRATION GUIDE:
   Old pattern:  def _make_marshal(name="X", ...): return Marshal(...)
   New pattern:  from conftest import MarshalFactory
                 marshal = MarshalFactory.infantry(name="X")

   Or use fixtures directly:
     def test_something(world, executor):
         marshal = MarshalFactory.infantry()
         world.marshals[marshal.name] = marshal
         ...

   Migration is FULLY INCREMENTAL. Old tests keep working unchanged.
   Convert high-churn files first; convert others as you touch them.
   """
   ```

**Expected Changes:** +200-250 lines (conftest.py), -30-50 lines (5 migrated files). Net ~+180 lines.

**Verification:**
- Full test suite passes: `.venv\Scripts\python.exe -m pytest tests/ -v`
- `pytest --collect-only` shows no import errors
- Verify conftest fixtures are importable in a new test file
- All 7,281+ existing tests pass unchanged

---

### Session 2: R1 — Post-Combat Pipeline Unification

> **NOTE: This session contains 2 live CRITICAL gameplay bugs** (auto-bombardment decisive_victory unconditional at executor.py:4598, war score inflation at executor.py:4581). These affect coalition/diplomatic balance in every game. Prioritize this session accordingly.

| Field | Value |
|-------|-------|
| **Root Cause** | RC-1: Post-Combat Pipeline Duplication |
| **Priority** | CRITICAL |
| **Effort** | ~3 hours |
| **Risk** | MEDIUM — most complex refactor in roadmap |
| **Bugs Prevented** | ~75 recurring (the single most repeated finding across all audits) |
| **Dependencies** | None (but Session 1 conftest makes tests easier) |

**Problem:** 5 combat paths share 28 post-combat steps. Only `_execute_attack` has all 28 (93% coverage). Others implement 25-50%. Every audit finds "path X missing step Y."

**Current Completeness (from audit report):**
- `_execute_attack` (executor.py:3543-5050): 26/28 steps (93%)
- `_execute_glorious_charge` (executor.py:10428-10800): 10/28 steps (36%)
- `_resolve_garrison_combat` (executor.py:2772-2987): 7/28 steps (25%)
- `_execute_bombardment` (executor.py:3191-3450): 8/28 steps (29%)
- auto-bombardment kill (executor.py:4522-4655): 14/28 steps (50%)

**Known Bugs to Fix:**
1. **CRITICAL:** Auto-bombardment kill adds `decisive_victory` threat (+5) unconditionally — no casualty ratio check (executor.py:4597-4598)
2. **CRITICAL:** Auto-bombardment kill inflates war score using full defender strength as casualties (executor.py:4581)
3. **MAJOR:** Garrison combat missing vindication, relationships, idle reset (executor.py:2772+)
4. **MAJOR:** Coordination fields never cleared after combat in any path
5. **MAJOR:** Bombardment doesn't record diplomacy at all
6. **MODERATE:** Pursuit damage floor: 0 (coordinated) vs 1000 (solo)
7. **MODERATE:** `FORCED_RETREAT_THRESHOLD` duplicated as constant AND local variable

**Files to Modify:**
- `backend/commands/executor.py` (14,797 lines) — primary target

**Files to Reference (read-only):**
- `backend/game_logic/combat.py` — `resolve_battle()` at line 152
- `backend/game_logic/relationship.py` — `process_battle_relationships()`
- `backend/game_logic/coalition.py` — `add_threat()`, `add_war_exhaustion_from_battle()`, `add_coalition_shock()`
- `backend/game_logic/diplomacy.py` — `record_battle()` (called as `record_diplo_battle`)
- `backend/game_logic/battle_report.py` — `_pick_observation()`
- `backend/commands/vindication.py` — vindication tracker
- `docs/ARCHITECTURE_AUDIT_REPORT.md` lines 45-137 — completeness matrix

**Implementation Steps:**

1. **Document the canonical 28 post-combat steps.** Using the completeness matrix, create a definitive ordered list. For each step, determine:
   - Which combat paths currently implement it
   - What the conditional gating should be (universal vs flag-gated)
   - The canonical implementation from `_execute_attack`

2. **Create `_post_combat_pipeline()` method** on CommandExecutor:
   ```python
   def _post_combat_pipeline(self, battle_result, attacker, defender, world,
                             game_state, **context):
       """Unified post-combat pipeline. Called by ALL combat resolution paths.

       Context flags control path-specific behavior:
         is_bombardment: bool — ranged attack (no war damage, no movement, no retreat)
         is_garrison: bool — garrison assault (defender is not a Marshal)
         is_glorious_charge: bool — cavalry charge (reset recklessness)
         is_coordinated: bool — multi-marshal battle
         is_auto_bombardment_kill: bool — defender killed by preparatory bombardment
         pre_battle_attacker_strength: int
         pre_battle_defender_strength: int
         actual_casualties: int — real casualties for war score (not full strength)
         battle_region: str
         atk_participants: list
         def_participants: list
         reinforcer_origin: dict
         coord_context: dict
       """
   ```

3. **Implement universal steps** (always run regardless of combat path):
   - `_clear_coordination_fields(attacker, world)` — FIX: currently missing from 4 of 5 paths
   - `_log_battle_event(battle_result, world)` — FIX: currently missing from garrison
   - `world.update_intel_from_battle(battle_result)` — already in 3/5 paths
   - `world.record_battle(battle_result)` — already in 4/5 paths (cannon fire detection)
   - `record_diplo_battle(battle_result, world)` — FIX: currently missing from bombardment + auto-kill
   - `_process_authority(battle_result, world)` — FIX: currently missing from bombardment + auto-kill
   - `_apply_coalition_threat(battle_result, world)` — FIX: currently missing from bombardment + auto-kill; FIX decisive_victory to require casualty ratio check
   - `attacker.last_combat_result = outcome` — FIX: currently missing from 4 of 5 paths

4. **Implement conditional steps** (flag-gated, not path-duplicated):
   ```python
   # War damage to region
   if not context.get('is_bombardment'):
       self._apply_battle_effects_to_region(battle_result, world)

   # Win/loss relationships
   if not context.get('is_bombardment') and not context.get('is_garrison'):
       process_battle_relationships(battle_result, world)

   # Forced retreat
   if not context.get('is_bombardment'):
       self._handle_forced_retreat(battle_result, world)

   # Attacker movement and conquest
   if (not context.get('is_bombardment')
       and not context.get('is_auto_bombardment_kill')
       and battle_result.get('outcome') in ('attacker_wins', 'decisive_victory')):
       self._attempt_region_capture(attacker, battle_region, world, game_state)

   # Vindication
   if not context.get('is_bombardment') and not context.get('is_garrison'):
       self._process_vindication(battle_result, world)

   # Notifications
   if not context.get('is_bombardment'):
       self._process_combat_notifications(battle_result, world)

   # Recklessness reset (mandatory after charge)
   if context.get('is_glorious_charge'):
       attacker.recklessness = 0

   # Coordination-specific
   if context.get('is_coordinated'):
       self._process_reinforcement_penalties(battle_result, context, world)
       self._maybe_send_coordination_tutorial(world)

   # Idle tracking
   if not context.get('is_garrison'):
       attacker.idle_turns = 0
       attacker.acted_this_turn = True

   # Re-pick observation
   if not context.get('is_bombardment'):
       self._repick_observation(battle_result, world)

   # Exhaustion tracking
   if not context.get('is_bombardment'):
       self._track_exhaustion(attacker, world)

   # Remove destroyed marshals
   if battle_result.get('defender_destroyed'):
       self._remove_destroyed_marshal(defender, world)
   ```

5. **Fix RC-1b: Unify post-combat diplomacy.** Extract `_apply_post_combat_diplomacy()` as a helper called inside the pipeline:
   - **Auto-bombardment decisive_victory fix:** Add casualty ratio check — only grant `decisive_victory` if casualties exceed threshold (currently unconditional at executor.py:4597-4598)
   - **Auto-bombardment war score fix:** Use `context['actual_casualties']` not `pre_battle_defender_strength` (currently inflated at executor.py:4581)
   - **Garrison fix:** Add vindication, relationship processing, idle reset

6. **Fix RC-1c: Solo vs coordinated path merge.** Currently ~140 lines of duplicated post-combat logic (executor.py:4672-4810):
   - **Pursuit damage floor:** Coordinated uses `max(0, ...)` while solo uses `max(1000, ...)` in combat.py:694. Unify to `max(1000, ...)` (solo behavior is correct — prevents trivial kills)
   - **FORCED_RETREAT_THRESHOLD:** Remove local variable duplication, use constant only
   - Coordinated path calls `resolve_battle(apply_casualties=False)` then manually handles ~140 lines — merge into pipeline with `is_coordinated` flag

7. **Wire all 5 combat paths** to call `_post_combat_pipeline()`:
   - `_execute_attack` (lines ~4850-5200): Replace inline post-combat block with pipeline call. Pass `is_coordinated` flag based on reinforcement state.
   - `_execute_glorious_charge` (lines ~10568-10800): Replace inline post-combat with pipeline call. Pass `is_glorious_charge=True`.
   - `_resolve_garrison_combat` (lines ~2823-2987): Replace inline post-combat with pipeline call. Pass `is_garrison=True`.
   - `_execute_bombardment` (lines ~3360-3450): Replace inline post-combat with pipeline call. Pass `is_bombardment=True`.
   - Auto-bombardment kill (lines ~4522-4655): Replace inline post-combat with pipeline call. Pass `is_auto_bombardment_kill=True`, `actual_casualties=actual_damage_dealt`.

8. **Write completeness enforcement test** `tests/test_post_combat_pipeline.py` (~40-50 tests):
   - Test each combat path calls the pipeline (mock pipeline, verify call + context flags)
   - Test universal steps run for ALL paths (attack, charge, garrison, bombardment, auto-kill)
   - Test conditional steps correctly gated (bombardment skips war damage, garrison skips relationships, etc.)
   - Test auto-bombardment decisive_victory requires casualty ratio check
   - Test auto-bombardment war score uses actual casualties not full strength
   - Test garrison now has vindication and relationship processing
   - Test coordinated pursuit damage floor matches solo (max 1000)
   - Test coordination fields cleared after ALL combat paths
   - Test `last_combat_result` set for ALL paths

**Expected Changes:** +400-500 lines (pipeline method + tests), -600-800 lines (removed duplicated post-combat code from 5 paths). Net -200 to -300 lines in executor.py.

**Verification:**
- Run completeness matrix check: For each of the 28 steps, write a test verifying the pipeline handles it
- Run all combat-related test files: `test_battle_report.py`, `test_coordination_bonus.py`, `test_relationship_formula.py`, `test_vindication_system.py`, `test_artillery.py`, `test_bombardment.py`, `test_garrison_command.py`, `test_glorious_charge.py`
- curl-test via backend: attack, glorious charge, bombardment, garrison assault scenarios
- Full test suite — all 7,281+ tests pass
- Run between each path conversion (wire one path at a time, test, then wire next)

---

### Session 3: R2 — War-State Helper Layer

| Field | Value |
|-------|-------|
| **Root Cause** | RC-2: No Centralized War-State Filtering |
| **Priority** | CRITICAL |
| **Effort** | ~2-3 hours |
| **Risk** | LOW — helper methods are additive, migration is mechanical |
| **Bugs Prevented** | ~49 recurring (missing validation/war-state checks) |
| **Dependencies** | None |

**Problem:** 50+ manual `nation !=` comparisons and `diplomatic_states.get()` checks scattered across the codebase. Every new action path must independently remember to check war state. Systems Audit V3 found 40+ places that forgot in a single audit.

**Files to Modify:**
- `backend/models/world_state.py` (6,023 lines) — add helper methods
- `backend/game_logic/diplomacy.py` (2,968 lines) — centralize `set_diplomatic_state()`
- `backend/commands/executor.py` — migrate highest-churn call sites
- `backend/ai/enemy_ai.py` — migrate call sites
- `backend/commands/strategic.py` — migrate call sites

**Files to Reference:**
- `backend/game_logic/ai_diplomacy.py` — AI proposal validation uses war state
- `backend/game_logic/coalition.py` — coalition war state checks

**Implementation Steps:**

1. **Verify existing `is_at_war()` method** in world_state.py (~line 1195). Document it, ensure it handles key ordering correctly (sorted tuple).

2. **Add new helper methods to WorldState:**
   ```python
   def are_allies(self, nation_a: str, nation_b: str) -> bool:
       """Check ALLIANCE or DEFENSIVE_PACT between nations."""
       key = tuple(sorted([nation_a, nation_b]))
       return self.diplomatic_states.get(key) in ("ALLIANCE", "DEFENSIVE_PACT")

   def can_interact_diplomatically(self, nation_a: str, nation_b: str) -> bool:
       """Check if diplomatic proposals/missions are permitted between nations.
       Blocked during active WAR (must use peace proposals instead)."""
       key = tuple(sorted([nation_a, nation_b]))
       state = self.diplomatic_states.get(key, "PEACE")
       return state != "WAR"

   def get_diplomatic_state(self, nation_a: str, nation_b: str) -> str:
       """Get diplomatic state between two nations. Returns 'PEACE' if not set."""
       key = tuple(sorted([nation_a, nation_b]))
       return self.diplomatic_states.get(key, "PEACE")

   def get_hostile_marshals_in_region(self, region_name: str, nation: str) -> list:
       """Marshals in region that are at war with nation. Strength > 0.
       Always checks is_at_war() — callers cannot forget."""
       return [m for m in self.get_marshals_in_region(region_name)
               if m.nation != nation and m.strength > 0
               and self.is_at_war(nation, m.nation)]

   def get_friendly_marshals_in_region(self, region_name: str, nation: str) -> list:
       """Marshals in region belonging to nation or allied nations."""
       return [m for m in self.get_marshals_in_region(region_name)
               if m.nation == nation or self.are_allies(nation, m.nation)]

   def get_nations_at_war_with(self, nation: str) -> list:
       """All nations currently at war with the given nation."""
       result = []
       for key, state in self.diplomatic_states.items():
           if state == "WAR":
               n1, n2 = key
               if n1 == nation:
                   result.append(n2)
               elif n2 == nation:
                   result.append(n1)
       return result
   ```

3. **Create `set_diplomatic_state()` in diplomacy.py.** Currently 5+ sites directly modify `diplomatic_states` without centralized bookkeeping:
   ```python
   def set_diplomatic_state(world, nation_a: str, nation_b: str,
                           new_state: str, reason: str = "") -> str:
       """Centralized diplomatic state change with automatic bookkeeping.

       Handles:
       - war_start_turns tracking (set on WAR entry, clear on WAR exit)
       - armistice_turns cleanup (clear when leaving ARMISTICE)
       - Active treaty removal (clear treaties on WAR declaration)
       - Debug logging of all state transitions

       Returns: previous state
       """
       key = tuple(sorted([nation_a, nation_b]))
       old_state = world.diplomatic_states.get(key, "PEACE")

       # Set new state
       world.diplomatic_states[key] = new_state

       # War start tracking
       if new_state == "WAR" and old_state != "WAR":
           world.war_start_turns[key] = world.current_turn
       elif new_state != "WAR" and old_state == "WAR":
           world.war_start_turns.pop(key, None)

       # Armistice cleanup
       if new_state != "ARMISTICE":
           world.armistice_turns.pop(key, None)
           world.armistice_cooldowns.pop(key, None)

       # Debug logging
       debug_print(f"DIPLO STATE: {nation_a}-{nation_b}: {old_state} → {new_state}"
                   f"{' (' + reason + ')' if reason else ''}")

       return old_state
   ```

4. **Catalog all manual war-state check sites.** Search for these patterns across the codebase:
   - `diplomatic_states.get(` — direct dict access
   - `diplomatic_states[` — direct dict write
   - `nation != ` + `marshal.nation` — manual hostile checks without `is_at_war()`
   - `== "WAR"` — string comparison without helper

5. **Migrate the 20 highest-churn sites** (prioritize files with most prior audit fixes):
   - `executor.py`: Target validation in `_execute_attack`, `_execute_move`, `_execute_bombardment` — use `get_hostile_marshals_in_region()`
   - `enemy_ai.py`: Target selection in `_find_attack_targets`, `_evaluate_marshal` — use `get_hostile_marshals_in_region()`
   - `strategic.py`: Target resolution in `_resolve_pursue_target` — use helpers
   - `diplomacy.py`: Replace all direct `diplomatic_states[key] = new_state` with `set_diplomatic_state()` — approximately 5+ sites including `declare_war()`, `_ratify_treaty()`, `process_armistice_expiry()`

6. **Write ~25-30 tests** in `tests/test_war_state_helpers.py`:
   - `test_is_at_war_returns_true_for_war_state`
   - `test_is_at_war_returns_false_for_peace`
   - `test_is_at_war_symmetric` (nation_a, nation_b same as nation_b, nation_a)
   - `test_are_allies_alliance`
   - `test_are_allies_defensive_pact`
   - `test_are_allies_false_for_peace`
   - `test_can_interact_diplomatically_during_peace`
   - `test_can_interact_diplomatically_blocked_during_war`
   - `test_can_interact_diplomatically_during_armistice`
   - `test_get_hostile_marshals_filters_by_war_state`
   - `test_get_hostile_marshals_excludes_dead_marshals`
   - `test_get_friendly_marshals_includes_allies`
   - `test_get_nations_at_war_with_returns_correct_set`
   - `test_set_diplomatic_state_tracks_war_start`
   - `test_set_diplomatic_state_clears_war_start_on_peace`
   - `test_set_diplomatic_state_cleans_armistice_fields`
   - `test_set_diplomatic_state_returns_old_state`
   - `test_set_diplomatic_state_removes_treaties_on_war`
   - Integration tests: verify migrated call sites behave identically

**Expected Changes:** +150-200 lines (helpers + set_diplomatic_state + tests), -50-100 lines (simplified call sites). Net +80-120.

**Verification:**
- Grep for remaining direct `diplomatic_states[` writes (excluding `to_dict`/`from_dict` and `set_diplomatic_state`) — should find zero
- Grep for remaining manual `== "WAR"` checks in migrated files — should find zero
- Run full test suite
- Run diplomacy-specific tests: `test_diplomatic_war_gating.py`, `test_session6_diplomacy.py`, `test_coalition_system.py`

---

## Phase B: Response & Data Access (Sessions 4-6)

### Session 4: R4 — Response Pipeline Standardization

| Field | Value |
|-------|-------|
| **Root Cause** | RC-4: Ad-Hoc Response Pipeline |
| **Priority** | MAJOR |
| **Effort** | ~2-3 hours |
| **Risk** | MEDIUM — must verify Godot handles consistent response shape |
| **Bugs Prevented** | ~9 popup passthrough misses + stale top-bar during popups |
| **Dependencies** | None |

**Problem:** 15 POST endpoints return different response shapes. No shared response builder. `_include_popup_passthroughs()` must be manually called in every response path — 37 "Bug 5" comments mark spots where it was nearly forgotten. Diplomatic top-bar fields (`diplomatic_points`, `threat_level`, etc.) only appear in `/command` response; during objection/popup interactions the top bar goes stale.

**Files to Modify:**
- `backend/main.py` (2,463 lines)

**Files to Reference (read-only):**
- `godot-client/project-sovereign/scripts/main.gd` — `_on_command_result()` response reading
- `godot-client/project-sovereign/scripts/api_client.gd` — response handling
- `docs/ARCHITECTURE_AUDIT_REPORT.md` lines 222-268 — response shape comparison table

**Implementation Steps:**

1. **Create `build_base_response()` function** in main.py (near line 146, before `_include_popup_passthroughs()`):
   ```python
   def build_base_response(world, success: bool = True, message: str = "",
                           events: list = None, **extra) -> dict:
       """Standard response builder. ALL POST endpoints must use this.

       Structurally guarantees:
       - Popup passthroughs (impossible to forget — called inside builder)
       - Diplomatic top-bar fields (always present, never stale)
       - Game state summary (always present)
       - Notifications (always present)

       Endpoint-specific fields passed as **extra.
       """
       response = {
           "success": success,
           "message": message,
           "game_state": _serialize_game_state(world),
           "events": events or [],
           # Diplomatic top-bar fields (previously only in /command)
           "diplomatic_points": int(world.nation_dp.get(world.player_nation, 0)),
           "max_diplomatic_points": int(world.max_dp),
           "threat_level": int(getattr(world, 'france_threat', 0)),
           "coalition_brewing": getattr(world, 'coalition_brewing', None) is not None,
           "coalition_brewing_turns": int(
               world.coalition_brewing.get("turns_remaining", 0)
           ) if getattr(world, 'coalition_brewing', None) else None,
           "talleyrand_state": _get_talleyrand_trust_label(world),
           "talleyrand_mission_summary": _get_talleyrand_mission_summary(world),
           "pending_envoy_count": int(len(getattr(world, 'diplomatic_queue', []))),
           "notifications": _get_notifications(world),
       }
       response.update(extra)
       _include_popup_passthroughs(response, world)  # Structurally guaranteed
       return response
   ```

2. **Migrate all 15 POST endpoints** to use `build_base_response()`. For each endpoint:
   - Replace ad-hoc `{"success": ..., "message": ..., "game_state": ...}` dict construction with `build_base_response(world, success=..., message=..., **extra_fields)`
   - Remove manual `_include_popup_passthroughs(response, world)` calls
   - Remove "Bug 5" reminder comments
   - Keep endpoint-specific fields as `**extra`

   Endpoints and their current locations:
   - `/command` (line 541) — most complex, has many response paths
   - `/respond_to_objection` (line 1135)
   - `/respond_to_diplomatic_dialogue` (line 1221)
   - `/capture_choice` (line 1267)
   - `/respond_to_redemption` (line 1305)
   - `/respond_to_glorious_charge` (line 1408)
   - `/strategic_response` (line 1466)
   - `/save` (line 1744) — may not need full base response
   - `/load` (line 1761)
   - `/delete_save` (line 1791) — may not need full base response
   - `/cancel_order` (line 1976)
   - `/notifications/dismiss` (line 2050)
   - `/debug/set_trust` (line 2080)
   - `/debug/set_authority` (line 2209)
   - `/debug/acceptance_preview` (line 2300)

3. **Verify Godot compatibility.** The Godot client reads response keys conditionally:
   - `main.gd` uses `.has("key")` checks for optional fields
   - `main.gd` uses `.get("key", default)` for defaultable fields
   - Adding previously-absent keys (like `diplomatic_points` to `/respond_to_objection`) should be safe since Godot ignores keys it doesn't read
   - Verify: no Godot code crashes on unexpected extra keys
   - Verify: `events: []` default doesn't break Godot array iteration for endpoints that previously didn't return `events`

4. **Write ~15-20 tests** in `tests/test_response_pipeline.py`:
   - `test_build_base_response_includes_all_required_keys`
   - `test_build_base_response_includes_popup_passthroughs`
   - `test_build_base_response_extra_fields_merge`
   - `test_build_base_response_success_false`
   - `test_build_base_response_events_default_empty_list`
   - `test_all_numeric_fields_are_int` (Golden Rule #2)
   - Endpoint integration tests verifying diplomatic fields present in non-command responses

**Expected Changes:** +80-100 lines (builder + tests), -200-250 lines (removed ad-hoc dicts, manual passthrough calls, Bug 5 comments). Net -120 to -170 in main.py.

**Verification:**
- curl-test EVERY POST endpoint before and after. Save response JSONs and diff
- Verify all popup keys present in every response (even if None)
- Verify diplomatic top-bar fields present in objection/redemption/capture responses
- Run Godot manual smoke test: complete one full turn cycle including combat, objection, capture choice
- Full test suite

---

### Session 5: R5 — Fog-Filtered Data Access

| Field | Value |
|-------|-------|
| **Root Cause** | RC-6: Fog-of-War Filter Scatter |
| **Priority** | MAJOR |
| **Effort** | ~2 hours |
| **Risk** | LOW-MEDIUM — strategic parser behavior change is intentional |
| **Bugs Prevented** | ~18 recurring (most consistently recurring category across ALL 6 audits) |
| **Dependencies** | None |

**Problem:** Fog filtering is implemented correctly in ~6 locations, but every NEW code path must independently remember to filter. `get_enemies_of_nation()` returns ALL enemies omnisciently. 18 bugs across 6 audits prove new paths forget to filter.

**Known Leaks:**
- **MAJOR:** Strategic parser reveals fogged enemy positions (strategic_parser.py:88, 577, 610)
- **MINOR:** map_data in LLM game state lists ALL marshals with no fog check (main.py:88-98)

**Files to Modify:**
- `backend/models/world_state.py` — add `get_visible_enemies()`
- `backend/ai/strategic_parser.py` (621 lines) — fix 3 fog leaks
- `backend/main.py` — fix map_data fog leak

**Files to Reference:**
- `backend/models/intel.py` — visibility levels (NONE, RUMOR, PARTIAL, FULL)
- `backend/intel_report.py` — existing fog filtering patterns
- `docs/FOG_OF_WAR_SPEC.md` — fog rules

**Implementation Steps:**

1. **Add `get_visible_enemies()` to WorldState:**
   ```python
   def get_visible_enemies(self, nation: str) -> List[Marshal]:
       """Returns enemies visible through fog. PREFERRED method for player-facing queries.

       Only returns enemies in regions with PARTIAL or FULL visibility.
       Use get_enemies_of_nation() only for omniscient operations
       (combat resolution, save/load, AI — until R14).
       """
       from backend.models.intel import PARTIAL
       return [
           m for m in self.get_enemies_of_nation(nation)
           if self.get_region_intel(m.location).visibility_at_least(PARTIAL)
       ]
   ```

2. **Fix strategic parser fog leaks (3 sites):**
   - **Line 88** — "the front" direction resolution: `world.get_enemies_of_nation(nation)` → `world.get_visible_enemies(nation)` (only for player nation; AI keeps omniscient for now)
   - **Line 577** — PURSUE target selection: Same fix. If no visible enemies found, return "No visible enemy targets" instead of omnisciently finding one
   - **Line 610** — SUPPORT target resolution: Same fix

   Guard: Only apply fog filter for player nation. AI uses omniscient version (R14 handles AI fog later):
   ```python
   if nation == world.player_nation:
       enemies = world.get_visible_enemies(nation)
   else:
       enemies = world.get_enemies_of_nation(nation)
   ```

3. **Fix main.py map_data fog leak (lines 88-98):**
   ```python
   # In get_llm_game_state() or wherever map_data is built
   marshals_here = world.get_marshals_in_region(region_name)
   visible_marshals = [
       m for m in marshals_here
       if m.nation == world.player_nation
       or world.get_region_intel(region_name).visibility_at_least(PARTIAL)
   ]
   ```

4. **Audit all `get_enemies_of_nation()` callers** (26 call sites). For each, classify:
   - **Player-facing query → migrate to `get_visible_enemies()`:** strategic parser (3 sites done above), LLM prompt hints, suggestion generator
   - **Combat resolution → keep omniscient:** `_execute_attack` target matching, `resolve_battle` participants
   - **AI decision → keep omniscient for now:** enemy_ai.py (R14 handles this)
   - **Save/load/serialization → keep omniscient**

5. **Write ~15-20 tests** in `tests/test_fog_filtered_access.py`:
   - `test_get_visible_enemies_filters_by_fog`
   - `test_get_visible_enemies_includes_partial_visibility`
   - `test_get_visible_enemies_includes_full_visibility`
   - `test_get_visible_enemies_excludes_none_visibility`
   - `test_get_visible_enemies_excludes_rumor_visibility`
   - `test_get_visible_enemies_returns_empty_when_all_fogged`
   - `test_strategic_parser_direction_uses_fog_for_player`
   - `test_strategic_parser_pursue_uses_fog_for_player`
   - `test_strategic_parser_uses_omniscient_for_ai`
   - `test_map_data_filters_fogged_enemy_marshals`
   - `test_map_data_shows_player_marshals_regardless_of_fog`

**Expected Changes:** +100-120 lines (helper + fixes + tests), -10-20 lines (simplified). Net +90.

**Verification:**
- Test with a world where some enemies are in fogged regions: verify `get_visible_enemies()` excludes them
- Test strategic parser with fogged and visible enemies: verify player can't target fogged enemies for PURSUE
- Run fog test suite: `test_fog_of_war.py`, `test_fog_34b.py`, `test_fog_endpoint_filters.py`, `test_fog_session36.py`
- curl-test `/command` with `"pursue nearest enemy"` when enemies are fogged
- Full test suite

---

### Session 6: R7+R8 — Display Name Registry + Campaign Log Enforcement

| Field | Value |
|-------|-------|
| **Root Cause** | RC-9: Display Name Translation Gaps + RC-10: Campaign Log Silent Drop |
| **Priority** | MODERATE |
| **Effort** | ~2-3 hours |
| **Risk** | LOW — both are additive |
| **Bugs Prevented** | ~6 display leaks + ~6 invisible events + future prevention |
| **Dependencies** | None |

#### Part A: R7 — Display Name Registry

**Problem:** 7 display maps scattered across 5 files. 5 known gaps where raw internal names reach the frontend. 3 missing display maps.

**Files to Create:**
- `backend/display_names.py`

**Files to Modify:**
- `backend/commands/executor.py` — import from display_names.py, remove local `_ACTION_DISPLAY_NAMES` (line 41)
- `backend/game_logic/diplomatic_dialogue.py` — import `PROPOSAL_TYPE_DISPLAY` from display_names.py (line 81)
- `backend/game_logic/diplomacy.py` — import `STATE_DISPLAY_NAMES` (line 2459), `FEEDBACK_STRINGS` (line 138)
- `backend/game_logic/diplomatic_advisory.py` — import `STATE_DISPLAY` (line 50)
- `backend/campaign_log.py` — import `DEFIANCE_DISPLAY`, `OBJECTION_DISPLAY` (lines 21, 43)
- `backend/main.py` — fix 5 known gaps (apply display maps to endpoint responses)

**Steps:**

1. **Create `display_names.py`** consolidating all 7 existing maps:
   ```python
   """Single source of truth for all internal→display name translations.

   All display maps live here. Backend modules import from here.
   Never return raw internal names to the frontend.
   """

   # From executor.py:41
   ACTION_DISPLAY = {
       "attack": "attacks", "move": "marches to", "bombardment": "bombards",
       "fortify": "fortifies", "drill": "drills", "recruit": "recruits",
       # ... all 17 entries
   }

   # From diplomatic_dialogue.py:81
   PROPOSAL_TYPE_DISPLAY = {
       "peace": "Peace Treaty", "alliance": "Alliance",
       # ... all 11 entries
   }

   # From diplomacy.py:2459
   STATE_DISPLAY = {
       "WAR": "At War", "PEACE": "At Peace", "ALLIANCE": "Allied",
       # ... all 8 entries
   }

   # From diplomatic_advisory.py:50
   STATE_NARRATIVE_DISPLAY = {
       "WAR": "at war", "PEACE": "at peace", "ALLIANCE": "allied",
       # ... all 8 entries (Talleyrand's voice — lowercase narrative form)
   }

   # From campaign_log.py:21
   OBJECTION_DISPLAY = { ... }  # 19 entries — gerund form

   # From campaign_log.py:43
   DEFIANCE_DISPLAY = { ... }  # 19 entries — past tense

   # From diplomacy.py:138
   FEEDBACK_STRINGS = { ... }  # 17 major keys with nested feedback phrases

   # NEW — currently missing
   DEFIANCE_OUTCOME_DISPLAY = {
       "failed_roll": "Failed", "right": "Vindicated", "wrong": "Misguided",
       "spectacular": "Spectacular Success", "disaster": "Disaster",
   }

   PERSONALITY_DISPLAY = {
       "aggressive": "Aggressive", "cautious": "Cautious",
       "reckless": "Reckless", "methodical": "Methodical",
       # ... all personality types
   }

   STANCE_DISPLAY = {
       "AGGRESSIVE": "Aggressive", "DEFENSIVE": "Defensive",
       "BALANCED": "Balanced",
   }

   def display(category: str, internal_name: str, fallback: str = None) -> str:
       """Universal translator. Never returns raw internal name.

       If internal_name not found in the map, returns fallback or
       auto-formatted version (Title Case with underscores removed).
       """
       maps = {
           "action": ACTION_DISPLAY,
           "state": STATE_DISPLAY,
           "proposal": PROPOSAL_TYPE_DISPLAY,
           "defiance_outcome": DEFIANCE_OUTCOME_DISPLAY,
           "personality": PERSONALITY_DISPLAY,
           "stance": STANCE_DISPLAY,
       }
       display_map = maps.get(category, {})
       result = display_map.get(internal_name)
       if result:
           return result
       if fallback:
           return fallback
       return internal_name.replace("_", " ").title()
   ```

2. **Migrate existing modules** to import from display_names.py. Keep backward-compatible aliases in original files during migration:
   ```python
   # In executor.py (temporary until full migration)
   from backend.display_names import ACTION_DISPLAY as _ACTION_DISPLAY_NAMES
   ```

3. **Fix 5 known display name gaps:**
   - `/diplomatic_states` GET endpoint: Apply `STATE_DISPLAY` to returned states
   - `/pending_objection` GET endpoint: Apply `ACTION_DISPLAY` to `original_order.action`
   - `/respond_to_objection` POST: Add `DEFIANCE_OUTCOME_DISPLAY` to defiance outcomes
   - `/diplomatic_preview` GET: Apply `ACTION_DISPLAY` to actions list
   - All personality/stance returns: Apply `PERSONALITY_DISPLAY` and `STANCE_DISPLAY`

#### Part B: R8 — Campaign Log Enforcement

**Problem:** 29 types whitelisted in `CAMPAIGN_LOG_TYPES` (3 dead entries that use dispatch events: `diplomatic_alliance_cascade`, `diplomatic_vassal_rebellion`, `diplomatic_war_declared`) but 41 event types actually logged via `log_event()`. 16 event types silently dropped — invisible to players.

**Files to Modify:**
- `backend/campaign_log.py` (594 lines) — `CAMPAIGN_LOG_TYPES` at lines 83-120, `format_event_oneliner()` function

**Files to Create:**
- `tests/test_campaign_log_enforcement.py`

**Steps:**

1. **Catalog all logged event types.** Search all `log_event({"type":` and `world.log_event(` calls. The 19+ missing types include:
   - `ai_proposal_accepted`, `ai_proposal_rejected`, `ai_proposal_counter_failed`
   - `coalition_brewing_started`, `coalition_brewing_cancelled`
   - `relationship_change`
   - `diplomatic_mission_started`, `diplomatic_mission_cancelled_eliminated`
   - `garrison_placed`
   - `proposal_sent`, `proposal_voided_by_coalition`
   - `diplomatic_discrepancy`, `diplomatic_downgrade`, `auto_downgrade`
   - `counter_offer_accepted`, `counter_offer_rejected`

2. **Add all missing types to `CAMPAIGN_LOG_TYPES`** with:
   - Format string in `format_event_oneliner()`
   - Fog visibility rule (FULL, PARTIAL, or ALWAYS based on event nature)
   - Category classification for filtering

3. **Consolidate duplicate event types:**
   - `diplomatic_war_declared` + `war_declaration` → keep `war_declaration`
   - Update all `log_event()` callers to use the canonical type

4. **Write enforcement test** `tests/test_campaign_log_enforcement.py`:
   ```python
   import ast
   import os

   def test_all_event_types_whitelisted():
       """Every event type used in log_event() must be in CAMPAIGN_LOG_TYPES.
       Prevents the silent-drop bug pattern."""
       # Grep all backend .py files for log_event calls
       logged_types = set()
       backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
       for root, dirs, files in os.walk(backend_dir):
           for f in files:
               if f.endswith('.py'):
                   # Parse and find log_event type strings
                   ...

       from backend.campaign_log import CAMPAIGN_LOG_TYPES
       for event_type in logged_types:
           assert event_type in CAMPAIGN_LOG_TYPES, \
               f"Event type '{event_type}' is logged but not in CAMPAIGN_LOG_TYPES — invisible to players"

   def test_all_whitelisted_types_have_format_strings():
       """Every whitelisted type must have a handler in format_event_oneliner()."""
       ...

   def test_no_duplicate_event_type_semantics():
       """No two event types should represent the same game event."""
       ...
   ```

**Expected Changes (combined R7+R8):** +250-300 lines (display_names.py + enforcement test + new campaign log entries), -50-80 lines (removed duplicated maps from original files). Net +200.

**Verification:**
- Run new enforcement test — should pass with zero missing types
- curl-test endpoints with display name gaps — verify no raw internal names
- Run `test_campaign_log.py` and new enforcement tests
- Full test suite

---

## Phase C: Infrastructure (Sessions 7-9)

### Session 7: R6 — CooldownManager + PopupQueue

| Field | Value |
|-------|-------|
| **Root Cause** | RC-7: Cooldown/Popup Field Sprawl |
| **Priority** | MAJOR |
| **Effort** | ~3 hours |
| **Risk** | MEDIUM — save format compatibility is critical |
| **Bugs Prevented** | ~7 cooldown/popup bugs + structural prevention of new popup leaks |
| **Dependencies** | None |

**Problem:** 14 cooldown dictionaries decremented in 4 different ways across 3 different files. 7 popup fields with no unified queue. Adding a new cooldown or popup type requires knowing which pattern to follow. `_decrement_ai_proposal_cooldowns()` has a hidden side effect.

**Cooldown Inventory (from audit):**
| Cooldown | Type | Decrement Location |
|----------|------|-------------------|
| `player_proposal_cooldowns` | Dict[str, int] | world_state.py:3768 |
| `ai_proposal_cooldowns` | Dict[str, int] | world_state.py:3773 (hidden side effect: expires queued proposals) |
| `proactive_suggestion_cooldowns` | Dict[str, int] | world_state.py:3774 |
| `ultimatum_cooldowns` | Dict[str, int] | world_state.py:3775 |
| `talleyrand_defiance_cooldown` | int (scalar) | world_state.py:3781 (inline -=1) |
| `vassal_investment_cooldowns` | Dict[str, int] | vassal.py via world_state.py:3803 |
| `vassal_release_cooldowns` | Dict[str, int] | vassal.py via world_state.py:3803 |
| `armistice_cooldowns` | Dict[str, int] | diplomacy.py (process_diplomacy_turn) |
| `armistice_turns` | Dict[str, int] | diplomacy.py (process_diplomacy_turn) |
| `coalition_cooldown` | int (scalar) | coalition.py (process_coalition_turn) |
| `ai_failed_action_cooldowns` | Dict[str, Dict[str, int]] | turn_manager.py (nested) |
| `ai_refortify_cooldown` | Dict[str, int] | turn_manager.py |
| `ai_stagnation_turns` | Dict[str, int] | turn_manager.py |
| `nation_bankruptcy_turns` | Dict[str, int] | world_state.py (auto-reset in _update_bankruptcy) |

**Popup Inventory:**
| Field | Type | Purpose |
|-------|------|---------|
| `pending_objection` | Optional[Dict] | Action objection dialog |
| `pending_redemption` | Optional[Dict] | Disobedience redemption |
| `pending_strategic_objection` | Optional[Dict] | Strategic order objection |
| `pending_capture_choice` | Optional[Dict] | Region capture choice |
| `pending_diplomatic_dialogue` | Optional[Dict] | Talleyrand conversation |
| `pending_talleyrand_sabotage` | Optional[Dict] | Active sabotage record |
| `pending_dialogue_queue` | List[Dict] | Queued dialogues (FIFO) |

**Files to Create:**
- `backend/models/cooldown_manager.py`

**Files to Modify:**
- `backend/models/world_state.py` — integrate CooldownManager, simplify advance_turn decrement block
- `backend/main.py` — simplify `_include_popup_passthroughs()` to use PopupQueue

**Implementation Steps:**

1. **Create `CooldownManager` class:**
   ```python
   class CooldownManager:
       """Centralizes all cooldown dictionaries. One decrement_all() per turn."""

       def __init__(self):
           self._dict_cooldowns = {}   # name -> {key: turns_remaining}
           self._scalar_cooldowns = {}  # name -> turns_remaining

       def set_dict(self, name: str, key: str, turns: int):
           """Set a keyed cooldown (e.g., player_proposal["Prussia"] = 5)."""
           if name not in self._dict_cooldowns:
               self._dict_cooldowns[name] = {}
           self._dict_cooldowns[name][key] = turns

       def get_dict(self, name: str, key: str = None) -> int or dict:
           """Get cooldown value. If key=None, returns entire dict."""
           cd = self._dict_cooldowns.get(name, {})
           if key is None:
               return cd
           return cd.get(key, 0)

       def set_scalar(self, name: str, turns: int):
           """Set a scalar cooldown (e.g., talleyrand_defiance = 3)."""
           self._scalar_cooldowns[name] = turns

       def get_scalar(self, name: str) -> int:
           return self._scalar_cooldowns.get(name, 0)

       def decrement_all(self):
           """Called ONCE in advance_turn. All cooldowns tick uniformly."""
           # Dict cooldowns
           for name in list(self._dict_cooldowns):
               cd = self._dict_cooldowns[name]
               for key in list(cd):
                   cd[key] -= 1
                   if cd[key] <= 0:
                       del cd[key]
           # Scalar cooldowns
           for name in list(self._scalar_cooldowns):
               self._scalar_cooldowns[name] -= 1
               if self._scalar_cooldowns[name] <= 0:
                   del self._scalar_cooldowns[name]

       def to_dict(self) -> dict:
           """Serialize to save format. Produces same shape as existing fields."""
           return {
               "dict_cooldowns": dict(self._dict_cooldowns),
               "scalar_cooldowns": dict(self._scalar_cooldowns),
           }

       @classmethod
       def from_dict(cls, data: dict) -> 'CooldownManager':
           mgr = cls()
           mgr._dict_cooldowns = data.get("dict_cooldowns", {})
           mgr._scalar_cooldowns = data.get("scalar_cooldowns", {})
           return mgr
   ```

2. **Create `PopupQueue` class** (in same file or separate):
   ```python
   class PopupQueue:
       """Priority-ordered popup queue. One pop per response cycle."""

       PRIORITY_ORDER = [
           "coalition_popup",
           "diplomatic_sabotage_popup",
           "vassal_rebellion_imminent_popup",
           "talleyrand_redemption_popup",
           "diplomatic_objection_popup",
           "incoming_proposal_popup",
           "alliance_paradox_popup",
       ]

       def __init__(self):
           self._queue = {}  # popup_type -> data

       def push(self, popup_type: str, data: dict):
           """Add popup to queue. Overwrites same-type popup."""
           self._queue[popup_type] = data

       def pop_highest(self) -> tuple:
           """Returns (popup_type, data) for highest-priority pending popup, or (None, None)."""
           for ptype in self.PRIORITY_ORDER:
               if ptype in self._queue:
                   data = self._queue.pop(ptype)
                   return ptype, data
           return None, None

       def has_pending(self) -> bool:
           return len(self._queue) > 0

       def clear_type(self, popup_type: str):
           self._queue.pop(popup_type, None)

       def to_dict(self) -> dict:
           return dict(self._queue)

       @classmethod
       def from_dict(cls, data: dict) -> 'PopupQueue':
           q = cls()
           q._queue = dict(data)
           return q
   ```

3. **Add backward-compatible properties on WorldState** so existing code doesn't break:
   ```python
   # In WorldState
   @property
   def player_proposal_cooldowns(self):
       return self._cooldown_manager.get_dict("player_proposal")

   @player_proposal_cooldowns.setter
   def player_proposal_cooldowns(self, value):
       self._cooldown_manager._dict_cooldowns["player_proposal"] = value
   ```
   Repeat for all 14 cooldown fields. This allows incremental migration — existing code reads/writes properties, new code uses CooldownManager directly.

4. **Replace decrement calls in advance_turn.** Currently lines 3768-3804 have 6 separate decrement calls plus inline `talleyrand_defiance_cooldown -= 1`. Replace with:
   ```python
   # In _advance_turn_internal(), replace lines 3768-3804:
   self._cooldown_manager.decrement_all()
   ```
   **Note:** `_decrement_ai_proposal_cooldowns()` has a hidden side effect (expires old queued proposals). This must be preserved as a separate call or integrated into the manager.

5. **Simplify `_include_popup_passthroughs()`** in main.py to use PopupQueue:
   ```python
   popup_type, popup_data = world._popup_queue.pop_highest()
   if popup_type:
       response[popup_type] = popup_data
   # Ensure all popup keys present (None if not set)
   for ptype in PopupQueue.PRIORITY_ORDER:
       if ptype not in response:
           response[ptype] = None
   ```

6. **Serialization compatibility.** CooldownManager/PopupQueue must produce same save format:
   - Option A: Manager stores internal structure, properties expose old shape for to_dict/from_dict
   - Option B: Manager's to_dict/from_dict directly use old field names
   - Choose Option A for cleaner separation. WorldState's to_dict/from_dict delegates to manager.

**Tests to Write (~20-25)** in `tests/test_cooldown_popup_manager.py`:
- CooldownManager: `test_set_get_dict_cooldown`, `test_set_get_scalar_cooldown`, `test_decrement_all_removes_expired`, `test_decrement_all_preserves_remaining`, `test_to_dict_from_dict_roundtrip`, `test_backward_compatible_property_read`, `test_backward_compatible_property_write`
- PopupQueue: `test_push_pop_priority_order`, `test_pop_highest_returns_highest`, `test_pop_returns_none_when_empty`, `test_clear_type`, `test_to_dict_from_dict_roundtrip`
- Integration: `test_advance_turn_decrements_all_cooldowns`, `test_popup_passthrough_uses_queue`

**Expected Changes:** +300-350 lines (new classes + backward-compat properties + tests), -150-200 lines (removed manual decrement code). Net +150.

**Verification:**
- Run `test_serialization_enforcement.py` — MUST pass
- Save/load cycle test: save game, load, verify all cooldowns preserved
- Run full test suite
- Verify all cooldown-dependent behavior still works (proposal cooldowns, armistice timers, etc.)

---

### Session 8: R9+R20 — Scaling Index + advance_turn Guard

| Field | Value |
|-------|-------|
| **Root Cause** | Scaling A + Game Loop atomicity |
| **Priority** | CRITICAL (pre-80-region) + MAJOR |
| **Effort** | ~2 hours |
| **Risk** | LOW — both are additive |
| **Bugs Prevented** | Performance degradation at scale + double-processing on retry |
| **Dependencies** | None |

#### Part A: R9 — Marshal-by-Region Index

**Problem:** O(R×M) performance for visibility calc, supply attrition, income phase. At 80 regions this becomes O(6400) per query instead of O(100).

**Files to Modify:**
- `backend/models/world_state.py`

**Steps:**

1. **Add `_marshals_by_region` cache:**
   ```python
   # In WorldState.__init__
   self._marshals_by_region: Dict[str, List[Marshal]] = {}

   def _build_marshal_index(self):
       """Build inverse index. Called at turn start and after movement."""
       self._marshals_by_region = {}
       for m in self.marshals.values():
           if m.strength > 0:
               self._marshals_by_region.setdefault(m.location, []).append(m)

   def get_marshals_in_region_indexed(self, region_name: str) -> List[Marshal]:
       """O(1) lookup using pre-built index. Falls back to linear scan if stale."""
       return self._marshals_by_region.get(region_name, [])
   ```

2. **Call `_build_marshal_index()`** at:
   - Start of `_advance_turn_internal()`
   - After `_execute_end_turn()` enemy phase
   - Optionally: after any `marshal.move_to()` call (or just rebuild per-phase)

3. **Replace 3 highest-churn linear scans** with indexed lookup:
   - Visibility calculation in intel recalc
   - Supply attrition processing
   - Income phase (garrison/control checks)

4. **Do NOT serialize** `_marshals_by_region` — it's a transient cache rebuilt each turn.

#### Part B: R20 — advance_turn Idempotency Guard

**Problem:** `advance_turn()` is 383 lines. If crash at step 25 of 48, steps 1-24 already committed. Retrying "end turn" double-processes (double income, double treaty costs).

**Files to Modify:**
- `backend/models/world_state.py`

**Steps:**

1. **Add idempotency guard field:**
   ```python
   # In WorldState.__init__
   self._last_advanced_turn: int = 0
   ```

2. **Guard `_advance_turn_internal()`:**
   ```python
   def _advance_turn_internal(self):
       if self._last_advanced_turn >= self.current_turn:
           debug_print(f"WARN: advance_turn already ran for turn {self.current_turn}")
           return
       # ... existing 48 steps ...
       self._last_advanced_turn = self.current_turn
   ```

3. **Add to serialization:**
   ```python
   # to_dict
   "last_advanced_turn": self._last_advanced_turn,
   # from_dict
   self._last_advanced_turn = data.get("last_advanced_turn", 0)
   ```

**Tests to Write (~15 total):**
- R9: `test_marshal_index_built_correctly`, `test_marshal_index_excludes_dead`, `test_indexed_lookup_matches_linear_scan`, `test_index_rebuilt_after_movement`, `test_index_empty_region_returns_empty`
- R20: `test_advance_turn_runs_once`, `test_advance_turn_rejects_double_call`, `test_advance_turn_works_on_new_turn`, `test_idempotency_survives_save_load`, `test_idempotency_field_serialized`

**Expected Changes (combined):** +100-120 lines. Net +80.

**Verification:**
- Run `test_serialization_enforcement.py`
- Run full suite
- Performance: time a turn cycle with 19 regions (baseline), verify index doesn't regress

---

### Session 9: R18 — Test Enforcement Suite

| Field | Value |
|-------|-------|
| **Root Cause** | Missing enforcement tests across 5 categories |
| **Priority** | MAJOR |
| **Effort** | ~1-2 hours |
| **Risk** | ZERO — read-only tests |
| **Bugs Prevented** | ~18 per category per future audit |
| **Dependencies** | R7+R8 (Session 6) should be done first for display/log maps |

**Problem:** Only serialization round-trip is enforced. 5 other categories of consistency are unchecked, leading to recurring bugs where a new action/event/proposal is added to one map but not another.

**Files to Create:**
- `tests/test_enforcement_suite.py`

**Files to Reference:**
- `backend/ai/validation.py` — `VALID_ACTIONS` set
- `backend/commands/executor.py` — `_ACTION_DISPLAY_NAMES` (or `display_names.py` after R7)
- `backend/models/world_state.py` — `_action_costs` dict
- `backend/commands/parser.py` — `valid_actions` list
- `backend/campaign_log.py` — `CAMPAIGN_LOG_TYPES` set
- `backend/game_logic/diplomatic_dialogue.py` — `PROPOSAL_TYPE_DISPLAY` dict

**Enforcement Tests:**

1. **All valid actions have AP costs:**
   ```python
   def test_all_actions_have_ap_costs():
       """Every action in VALID_ACTIONS must have a cost in _action_costs."""
       from backend.ai.validation import VALID_ACTIONS
       from backend.models.world_state import WorldState
       ws = WorldState()
       for action in VALID_ACTIONS:
           assert action in ws._action_costs, \
               f"Action '{action}' in VALID_ACTIONS but missing AP cost"
   ```

2. **All valid actions have display names:**
   ```python
   def test_all_actions_have_display_names():
       """Every valid action must have a UI-friendly display name."""
       from backend.ai.validation import VALID_ACTIONS
       from backend.display_names import ACTION_DISPLAY  # or executor import
       for action in VALID_ACTIONS:
           assert action in ACTION_DISPLAY, \
               f"Action '{action}' missing display name — raw name would leak to UI"
   ```

3. **All logged event types are whitelisted (complements R8 enforcement test):**
   ```python
   def test_all_event_types_whitelisted():
       """Every log_event() type string must be in CAMPAIGN_LOG_TYPES."""
       # Parse all backend .py files, extract log_event type arguments
       # Compare against CAMPAIGN_LOG_TYPES
       ...
   ```

4. **All proposal types have display strings:**
   ```python
   def test_all_proposal_types_have_display():
       """Every proposal type in use must have PROPOSAL_TYPE_DISPLAY entry."""
       # Find all proposal type strings used in diplomatic_dialogue.py, diplomacy.py
       # Verify each has a display entry
       ...
   ```

5. **VALID_ACTIONS consistent across modules:**
   ```python
   def test_valid_actions_consistent():
       """VALID_ACTIONS in validation.py must match parser + executor."""
       from backend.ai.validation import VALID_ACTIONS
       from backend.commands.parser import valid_actions as parser_actions
       # Also check executor has _execute_{action} for each
       ...
   ```

**Expected Changes:** +150-200 lines.

**Verification:**
- All 5 tests pass. If they fail, they've found latent bugs to fix (budget 30 minutes for fixes).
- Full test suite.

---

## Phase D: Executor Split (Sessions 10-13)

### Session 10: R10 — Executor Split Phase 1: Combat

| Field | Value |
|-------|-------|
| **Root Cause** | RC-3: Executor God Object |
| **Priority** | MAJOR |
| **Effort** | ~3 hours |
| **Risk** | MEDIUM — pure code movement, but import resolution needs care |
| **Impact** | executor.py 14,797 → ~12,300 lines |
| **Dependencies** | **Session 2 (R1) MUST be complete** — post-combat pipeline must be unified first |

**Files to Create:**
- `backend/commands/combat_executor.py` (~2,500 lines)

**Files to Modify:**
- `backend/commands/executor.py` — extract methods, add delegation wiring

**Methods to Extract:**
- `_execute_attack` + all attack sub-helpers
- `_execute_glorious_charge`
- `_execute_bombardment` + bombardment helpers
- `_resolve_garrison_combat`
- `_post_combat_pipeline` (from Session 2)
- `_handle_forced_retreat` + `_apply_forced_retreat_or_break`
- `_distribute_casualties`
- `_calculate_coordination_context` + 13 coordination helpers (~1,400 lines)
- `_log_battle_event`, `_process_combat_notifications`
- `_apply_battle_effects_to_region`
- `_attempt_region_capture`

**Steps:**

1. **Create `CombatExecutor` class:**
   ```python
   class CombatExecutor:
       """Handles all combat-related execution: attack, charge, bombardment, garrison."""

       def __init__(self, parent_executor):
           self._executor = parent_executor
           self.combat_resolver = parent_executor.combat_resolver
   ```

2. **Move methods one at a time.** For each:
   - Copy method to CombatExecutor
   - Replace `self.xxx` references to shared state with `self._executor.xxx`
   - Add import wiring
   - Run tests
   - Delete original from executor.py
   - Run tests again

3. **Wire main executor delegation:**
   ```python
   # In CommandExecutor.__init__
   self._combat = CombatExecutor(self)

   # In dispatch method
   if action == "attack":
       return self._combat._execute_attack(marshal, target, world, game_state)
   elif action == "glorious_charge":
       return self._combat._execute_glorious_charge(marshal, target, world, game_state)
   # etc.
   ```

4. **Handle cross-cutting concerns:**
   - Objection system can intercept combat — keep objection routing in main executor
   - `_execute_post_objection` must delegate to CombatExecutor for combat actions
   - AP accounting stays in main executor

**Verification:**
- Run full test suite after EACH method move (not batch)
- Run combat-specific tests: all `test_*attack*`, `test_*bombardment*`, `test_*garrison*`, `test_*coordination*`, `test_*glorious_charge*`
- Verify no circular imports
- Verify all test paths still work

---

### Session 11: R11 — Executor Split Phase 2: Diplomatic + Strategic

| Field | Value |
|-------|-------|
| **Root Cause** | RC-3: Executor God Object |
| **Priority** | MAJOR |
| **Effort** | ~3 hours |
| **Risk** | MEDIUM |
| **Impact** | executor.py ~12,300 → ~9,100 lines |
| **Dependencies** | Session 10 (R10) complete |

**Files to Create:**
- `backend/commands/diplomatic_executor.py` (~2,000 lines)
- `backend/commands/strategic_executor.py` (~1,200 lines)

**Diplomatic methods to extract:** All `_execute_propose_*`, `_execute_respond_*`, dialogue state machine methods, diplomatic validation helpers, `_execute_send_diplomat`, `_execute_recall_diplomat`.

**Strategic methods to extract:** `_execute_strategic_order`, `_execute_cancel`, strategic pathfinding helpers, condition evaluation.

**Same pattern as Session 10.** Create `DiplomaticExecutor(parent)` and `StrategicExecutor(parent)`. Wire through main executor delegation. Move one method at a time, test after each.

---

### Session 12: R12 — DialogueManager

| Field | Value |
|-------|-------|
| **Root Cause** | RC-8: Dialogue State Machine Chaos |
| **Priority** | MAJOR |
| **Effort** | ~3 hours |
| **Risk** | HIGH — 139 occurrences across 12 files |
| **Bugs Prevented** | "Talleyrand awaiting" stuck state, dialogue overwrite, queue overflow |
| **Dependencies** | **Session 11 (R11) SHOULD be complete** — reduces blast radius since diplomatic executor is separated |

**Problem:** `pending_diplomatic_dialogue` has 22 SET and 48 CLEAR operations across 12 files. No queue cap. No auto-clear for blocking dialogues. No audit trail.

**Files to Create:**
- `backend/models/dialogue_manager.py`

**Files to Modify:**
- `backend/models/world_state.py` — integrate DialogueManager
- `backend/commands/diplomatic_executor.py` (post-R11) — migrate SET/CLEAR sites
- `backend/main.py` — migrate routing
- `backend/game_logic/turn_manager.py` — migrate queue pop

**Steps:**

1. **Create `DialogueManager` class:**
   ```python
   class DialogueManager:
       """Centralizes all dialogue SET/CLEAR/QUEUE operations.

       Replaces scattered pending_diplomatic_dialogue = ... assignments
       with structured push/pop/peek operations.
       """
       QUEUE_CAP = 20
       BLOCKING_TIMEOUT_TURNS = 3

       def __init__(self):
           self._current: Optional[Dict] = None
           self._queue: List[Dict] = []
           self._blocking: bool = False
           self._blocking_since_turn: int = 0

       def push(self, dialogue_data: dict, blocking: bool = False):
           """Add dialogue. If current slot occupied, queue it."""
           if self._current is None:
               self._current = dialogue_data
               self._blocking = blocking
           else:
               if len(self._queue) < self.QUEUE_CAP:
                   self._queue.append(dialogue_data)

       def pop(self) -> Optional[Dict]:
           """Remove and return current dialogue. Promote from queue if available."""
           result = self._current
           self._current = None
           self._blocking = False
           if self._queue:
               self._current = self._queue.pop(0)
           return result

       def peek(self) -> Optional[Dict]:
           """Read current dialogue without removing."""
           return self._current

       def is_blocking(self) -> bool:
           return self._blocking and self._current is not None

       def clear_stale(self, current_turn: int):
           """Auto-clear blocking dialogues older than BLOCKING_TIMEOUT_TURNS."""
           if (self._blocking and self._current
               and current_turn - self._blocking_since_turn > self.BLOCKING_TIMEOUT_TURNS):
               self.pop()

       def to_dict(self) -> dict: ...
       @classmethod
       def from_dict(cls, data: dict) -> 'DialogueManager': ...
   ```

2. **Backward-compatible property on WorldState:**
   ```python
   @property
   def pending_diplomatic_dialogue(self):
       return self._dialogue_manager.peek()

   @pending_diplomatic_dialogue.setter
   def pending_diplomatic_dialogue(self, value):
       if value is None:
           self._dialogue_manager.pop()
       else:
           self._dialogue_manager.push(value)

   @property
   def pending_dialogue_queue(self):
       return self._dialogue_manager._queue

   @pending_dialogue_queue.setter
   def pending_dialogue_queue(self, value):
       self._dialogue_manager._queue = value
   ```

3. **Migrate incrementally.** Property-based access means ALL existing code keeps working immediately. Then migrate highest-churn SET/CLEAR sites in diplomatic_executor.py and main.py to use `push()`/`pop()`/`peek()` directly.

4. **Add `clear_stale()` call** in `advance_turn` — prevents permanently stuck blocking dialogues.

**Tests to Write (~20-25):**
- `test_push_pop_basic`, `test_push_queues_when_occupied`, `test_queue_cap_enforced`, `test_pop_promotes_from_queue`, `test_peek_does_not_remove`, `test_is_blocking`, `test_clear_stale_removes_old_blocking`, `test_serialization_roundtrip`, `test_backward_compat_property_read`, `test_backward_compat_property_write`, `test_backward_compat_property_none_clears`

**Verification:**
- Run `test_serialization_enforcement.py`
- Run all dialogue-related tests
- Test blocking guard: verify commands blocked during dialogue, unblocked after response
- Full test suite

---

### Session 13: R13 — Executor Split Phase 3: Remaining

| Field | Value |
|-------|-------|
| **Root Cause** | RC-3: Executor God Object |
| **Priority** | MINOR |
| **Effort** | ~3 hours |
| **Risk** | LOW-MEDIUM (pattern well-established by now) |
| **Impact** | executor.py ~9,100 → ~1,500 lines (router + guards + AP) |
| **Dependencies** | Session 11 (R11) complete |

**Files to Create:**
- `backend/commands/movement_executor.py` (~1,000 lines): `_execute_move`, `_execute_scout`, retreat handling, attrition
- `backend/commands/tactical_executor.py` (~900 lines): `_execute_fortify`, `_execute_drill`, `_execute_form_square`, `_execute_change_stance`
- `backend/commands/economy_executor.py` (~400 lines): `_execute_recruit`, `_execute_build`, `_execute_repair`
- `backend/commands/capture_executor.py` (~400 lines): `_execute_plunder`, `_execute_secure`, AI capture choice
- `backend/commands/vassal_executor.py` (~200 lines): `_execute_invest_vassal`, `_execute_set_autonomy`, `_execute_make_vassal`, `_execute_release_vassal`
- `backend/commands/meta_executor.py` (~1,500 lines): `_execute_end_turn`, `_execute_help`, `_execute_debug_*`, `_execute_cheat_*`

**Same pattern as Sessions 10-11.** By this point the extraction pattern is well-practiced. Move one module at a time, test between each.

**Final executor.py structure (~1,500 lines):**
- Class definition + `__init__` with sub-executor creation
- `execute_command()` router — dispatches to appropriate sub-executor
- Guard methods: objection check, AP check, bypass hierarchy
- AP accounting
- `_execute_post_objection` routing to sub-executors

---

## Phase E: Godot Frontend (Sessions 14-16)

### Session 14: R17 — HTTP Timeout + api_client Consolidation

| Field | Value |
|-------|-------|
| **Root Cause** | Integration: no timeout mechanism |
| **Priority** | CRITICAL |
| **Effort** | ~1-2 hours |
| **Risk** | LOW — mechanical refactoring |
| **Bugs Prevented** | Infinite client hang on server timeout (CRITICAL gap) |
| **Dependencies** | None |

**Problem:** NO timeout in api_client.gd. If server hangs, Godot hangs indefinitely. `_request_in_flight` never clears. All subsequent requests fail with "Request already in progress." Additionally, 25+ HTTP methods with identical boilerplate (~250 of 347 lines).

**Files to Modify:**
- `godot-client/project-sovereign/scripts/api_client.gd` (347 lines)

**Steps:**

1. **Add timeout to HTTPRequest** (Godot 4's built-in property):
   ```gdscript
   func _ready():
       http_request = HTTPRequest.new()
       http_request.timeout = 30.0  # 30-second timeout
       add_child(http_request)
       http_request.request_completed.connect(_on_request_completed)
   ```

2. **Create generic request helpers:**
   ```gdscript
   func _post(endpoint: String, body: Dictionary, callback: Callable):
       """Generic POST request. All POST methods delegate here."""
       if _request_in_flight:
           callback.call({"success": false, "message": "Request already in progress"})
           return
       pending_callback = callback
       var url = API_URL + endpoint
       var headers = ["Content-Type: application/json"]
       var error = http_request.request(url, headers, HTTPClient.METHOD_POST,
                                        JSON.stringify(body))
       if error != OK:
           push_error("HTTP POST failed: " + str(error))
           callback.call({"success": false, "message": "Request failed to send"})
       else:
           _request_in_flight = true

   func _get(endpoint: String, callback: Callable):
       """Generic GET request. All GET methods delegate here."""
       if _request_in_flight:
           callback.call({"success": false, "message": "Request already in progress"})
           return
       pending_callback = callback
       var url = API_URL + endpoint
       var error = http_request.request(url)
       if error != OK:
           callback.call({"success": false, "message": "Request failed to send"})
       else:
           _request_in_flight = true
   ```

3. **Refactor all 25+ methods** to use generic helpers. Each becomes 1-2 lines:
   ```gdscript
   func send_command(command: String, callback: Callable):
       _post("/command", {"command": command}, callback)

   func send_objection_response(choice: String, callback: Callable):
       _post("/respond_to_objection", {"choice": choice}, callback)

   func get_campaign_log(callback: Callable):
       _get("/campaign_log", callback)
   ```

4. **Add timeout error handling** in `_on_request_completed`:
   ```gdscript
   func _on_request_completed(result, response_code, headers, body):
       _request_in_flight = false  # Always clear — prevents permanent lock

       if result == HTTPRequest.RESULT_TIMEOUT:
           if pending_callback:
               pending_callback.call({
                   "success": false,
                   "message": "Server timeout — please try again"
               })
           return

       # ... existing response handling ...
   ```

5. **Add `_request_in_flight` safety reset.** If timeout fires, clear the flag so future requests aren't permanently blocked.

**Expected Changes:** 347 → ~150-180 lines (-170 to -200 lines).

**Verification:**
- Test normal requests work (send command, get campaign log)
- Test timeout: stop the backend server, send a command from Godot, verify timeout error message appears after 30s and subsequent requests still work
- Test all endpoint methods still function correctly

---

### Session 15: R15 — Extract utils.gd + PopupBase

| Field | Value |
|-------|-------|
| **Root Cause** | Frontend: code duplication + inconsistent signals |
| **Priority** | MAJOR |
| **Effort** | ~2-3 hours |
| **Risk** | MEDIUM — Godot scene tree wiring can be fragile |
| **Bugs Prevented** | Color inconsistency, signal mismatch, 250+ duplicate lines |
| **Dependencies** | None |

**Problem:** Color palettes duplicated across 15 .gd files (~50 lines copy-paste). 27 CanvasLayer popups with no base class. Inconsistent signal interfaces (`choice_made(String)` vs `choice_made(String, Dictionary)` vs `dismissed()`).

**Files to Create:**
- `godot-client/project-sovereign/scripts/utils.gd` — shared constants + helpers
- `godot-client/project-sovereign/scripts/popup_base.gd` — base class for all popups

**Files to Modify:**
- 15 .gd files with duplicated color constants (replace with Utils reference)
- 3 simple popup .gd files (migrate to extend PopupBase as proof of concept)

**Steps:**

1. **Create `utils.gd` as autoload:**
   ```gdscript
   extends Node
   class_name Utils

   # === Shared Color Palette ===
   const COLOR_GOLD = "d9c08c"
   const COLOR_COMMAND = "7eb8da"
   const COLOR_SUCCESS = "8fbc8f"
   const COLOR_ERROR = "cd6b6b"
   const COLOR_BATTLE = "daa06d"
   const COLOR_INFO = "a0a0a8"
   const COLOR_MARSHAL = "c9b8e0"
   const COLOR_CONQUEST = "90d890"
   const COLOR_FEEDBACK = "b8a0d9"
   const COLOR_DISPATCH = "c9b878"
   const COLOR_BERTHIER = "B8860B"
   const COLOR_OBSERVATION = "DAA520"
   const COLOR_TEXT = "eee"
   const COLOR_DIMMED = "808080"

   # === Nation Colors ===
   const NATION_COLORS = {
       "France": Color(0.255, 0.412, 0.882),
       "Prussia": Color(0.2, 0.2, 0.5),
       "Austria": Color(0.7, 0.2, 0.2),
       "Russia": Color(0.2, 0.5, 0.2),
       "Britain": Color(0.7, 0.1, 0.1),
       "Saxony": Color(0.4, 0.6, 0.3),
       "Spain": Color(0.8, 0.6, 0.1),
   }

   # === Formatting Helpers ===
   static func format_number(n: int) -> String:
       # Thousands separator
       ...

   static func bbcode_color(text: String, color: String) -> String:
       return "[color=#" + color + "]" + text + "[/color]"
   ```

2. **Create `PopupBase` class:**
   ```gdscript
   class_name PopupBase extends CanvasLayer

   signal popup_closed(result)

   func show_popup(data: Dictionary):
       """Override in subclass. Called with popup data from backend."""
       show()

   func close_popup(result = null):
       """Standard close. Emits popup_closed signal."""
       hide()
       popup_closed.emit(result)

   func _apply_standard_theme(panel: PanelContainer):
       """Apply consistent theme to panel."""
       var style = StyleBoxFlat.new()
       style.bg_color = Color(0.1, 0.1, 0.18, 0.95)
       style.border_color = Color(0.85, 0.75, 0.55, 0.6)
       style.set_border_width_all(2)
       style.set_corner_radius_all(8)
       panel.add_theme_stylebox_override("panel", style)
   ```

3. **Migrate 3 simplest popups** as proof of concept:
   - `coalition_declaration_popup.gd` — simple "dismissed" signal, display-only
   - `alliance_paradox_popup.gd` — two-choice with String result
   - `interrupt_popup.gd` — simple display-only

   For each: change `extends CanvasLayer` to `extends PopupBase`, replace color constants with `Utils.COLOR_*`, replace signal with `popup_closed`.

4. **Register `utils.gd` as autoload** in Godot project settings.

**Verification:**
- Open Godot, verify no scene tree errors
- Test each migrated popup: trigger the scenario, verify display and behavior unchanged
- Verify color consistency (visual inspection)

---

### Session 16: R16 — Dialog Manager + Layer Subdivision

| Field | Value |
|-------|-------|
| **Root Cause** | Frontend: Layer 100 collision zone + main.gd god object |
| **Priority** | MAJOR |
| **Effort** | ~2-3 hours |
| **Risk** | MEDIUM-HIGH — scene tree changes can break Godot |
| **Impact** | main.gd -280 lines, Layer 100 collision eliminated |
| **Dependencies** | Session 15 (R15) — PopupBase class needed |

**Problem:** 11 popups at Layer 100 with no depth ordering — if two fire simultaneously, last added wins. 27 dialog instantiations in main.gd `_ready()` (~100+ lines of identical boilerplate).

**Files to Create:**
- `godot-client/project-sovereign/scripts/dialog_manager.gd`

**Files to Modify:**
- `godot-client/project-sovereign/scripts/main.gd` — extract dialog instantiation, remove boilerplate
- 11 popup .tscn files — change CanvasLayer from 100 to subdivided values

**Steps:**

1. **Subdivide Layer 100** into 100-110 range based on priority:
   ```
   100: coalition_declaration_popup (highest priority)
   101: sabotage_discovery_popup
   102: vassal_rebellion_popup
   103: talleyrand_redemption_popup
   104: talleyrand_objection_popup
   105: incoming_proposal_popup
   106: alliance_paradox_popup
   107: objection_dialog
   108: redemption_dialog
   109: glorious_charge_dialog
   110: capture_choice_dialog, clarification_popup, other minor dialogs
   ```

2. **Create `dialog_manager.gd`:**
   ```gdscript
   extends Node
   class_name DialogManager

   var _dialogs: Dictionary = {}  # name -> dialog node

   func register(dialog_name: String, scene_path: String, layer: int) -> Node:
       """Load, instantiate, and register a dialog."""
       var scene = load(scene_path)
       if not scene:
           push_error("Failed to load dialog: " + scene_path)
           return null
       var instance = scene.instantiate()
       instance.layer = layer
       get_tree().root.add_child(instance)
       instance.hide()
       _dialogs[dialog_name] = instance
       return instance

   func get_dialog(dialog_name: String) -> Node:
       return _dialogs.get(dialog_name)

   func show_dialog(dialog_name: String, data: Dictionary = {}):
       var dialog = _dialogs.get(dialog_name)
       if dialog:
           dialog.show_popup(data)

   func hide_all():
       for dialog in _dialogs.values():
           dialog.hide()
   ```

3. **Move dialog instantiation from main.gd `_ready()`** (currently ~100+ lines of identical preload → instantiate → error check → add_child → connect) into dialog_manager.gd registrations:
   ```gdscript
   # In main.gd _ready(), replace 100+ lines with:
   dialog_manager = DialogManager.new()
   add_child(dialog_manager)

   objection_dialog = dialog_manager.register("objection",
       "res://scenes/objection_dialog.tscn", 107)
   objection_dialog.choice_made.connect(_on_objection_choice)

   # ... etc for each dialog
   ```

4. **Test each popup** individually after migration — trigger the scenario, verify layer ordering, verify signals still fire.

**Verification:**
- Open Godot, verify no scene tree errors on startup
- Test EVERY popup type: objection, redemption, capture choice, glorious charge, coalition declaration, incoming proposal, sabotage discovery, vassal rebellion, talleyrand objection, talleyrand redemption, alliance paradox
- Verify no two popups overlap incorrectly (layer subdivision test)
- Verify main.gd `_ready()` is significantly shorter

---

## Phase F: AI Fog Integration (Sessions 17-20)

### Session 17: R14a — AI Fog Foundation

| Field | Value |
|-------|-------|
| **Root Cause** | Scaling B: AI Omniscience |
| **Priority** | CRITICAL (pre-80-region) |
| **Effort** | ~3 hours |
| **Risk** | HIGH — changes AI behavior significantly |
| **Dependencies** | **Session 8 (R9 scaling index) must be complete** |

**Problem:** Enemy AI calls `get_enemies_of_nation()` which returns ALL enemies globally with no fog filtering. At 80 regions this is both unfair and slow.

**Files to Modify:**
- `backend/ai/enemy_ai.py` (5,561 lines)
- `backend/models/world_state.py` — add `get_ai_visible_enemies()`

**Steps:**

1. **Add AI visibility method:**
   ```python
   def get_ai_visible_enemies(self, nation: str, difficulty: str = "normal") -> List[Marshal]:
       """Fog-filtered enemy lookup for AI. Difficulty controls visibility range.

       - "easy": Only FULL visibility (AI barely knows anything)
       - "normal": PARTIAL+ visibility (same as player)
       - "hard": RUMOR+ visibility (AI has better intel network)
       - "omniscient": ALL enemies (legacy behavior)
       """
       if difficulty == "omniscient":
           return self.get_enemies_of_nation(nation)

       min_visibility = {
           "easy": FULL, "normal": PARTIAL, "hard": RUMOR,
       }.get(difficulty, PARTIAL)

       return [m for m in self.get_enemies_of_nation(nation)
               if self.get_region_intel_for_nation(m.location, nation)
                   .visibility_at_least(min_visibility)]
   ```

2. **Start with 3 lowest-risk AI methods** (methods that DON'T directly choose attack targets):
   - `_find_retreat_targets` — where to retreat when broken
   - `_evaluate_supply_risk` — supply chain vulnerability assessment
   - `_score_defensive_position` — how defensible is a position

3. **Add fog parameter to AI initialization:**
   ```python
   class EnemyAI:
       def __init__(self, difficulty="normal"):
           self.difficulty = difficulty
   ```

4. **Write 10+ tests** verifying AI behavior changes are correct:
   - AI doesn't retreat toward fogged enemies (safety improvement)
   - AI doesn't know about fogged supply vulnerabilities
   - AI defensive scoring ignores fogged threats
   - AI with "omniscient" difficulty behaves identically to current (regression check)

**Verification:**
- Run full test suite (regression check — AI tests must all pass)
- Playtest 3 turns: verify AI still makes reasonable retreat/defensive decisions
- Verify "omniscient" difficulty produces identical behavior to current code

---

### Session 18: R14b — AI Attack Target Selection

| Effort | ~3 hours | Risk | HIGH |
|--------|----------|------|------|

Migrate `_find_attack_targets` and `_evaluate_marshal` target selection to use fog-filtered access. These are the core decision methods — AI can only attack enemies it can see.

**Tests:** 10+ tests verifying AI attack targeting respects fog. Regression suite.

---

### Session 19: R14c — AI Strategic Decisions

| Effort | ~3 hours | Risk | HIGH |
|--------|----------|------|------|

Migrate `_evaluate_strategic_position`, `_choose_movement_target`, and remaining methods. AI movement and positioning now fog-aware.

**Tests:** 10+ tests. Regression suite.

---

### Session 20: R14d — AI Fog Integration Test + Tuning

| Effort | ~3 hours | Risk | HIGH |
|--------|----------|------|------|

Full integration test session:
1. Play full 20-turn game with fog-aware AI
2. Verify AI still plays competently (doesn't degrade into random moves)
3. Tune difficulty levels if needed
4. Verify AI nations with better intel networks (more scouts) get better visibility
5. Write comprehensive integration tests (~15-20 tests)
6. Update `docs/ENEMY_AI_REFERENCE.md` with fog behavior documentation

---

## Phase G: Modding (Session 21)

### Session 21: R19 — Modding Validator Extension

| Field | Value |
|-------|-------|
| **Root Cause** | Modding: ~30% validator coverage |
| **Priority** | MAJOR |
| **Effort** | ~3 hours |
| **Risk** | LOW — additive validation only |
| **Dependencies** | None |

**Problem:** Validator covers ~30% of fields. Game-breaking mod scenarios (WAR with self, vassal circular dependencies, zombie marshals) are unvalidated.

**Files to Modify:**
- `backend/modding/validator.py` (477 lines)

**Files to Reference:**
- `backend/game_logic/diplomacy.py` — valid diplomatic states
- `backend/game_logic/vassal.py` — vassal structure
- `backend/game_logic/coalition.py` — coalition structure
- `docs/MODDING_FORMAT.md` — current mod format documentation

**Steps:**

1. **Add diplomatic state graph validation:**
   ```python
   def _validate_diplomatic_states(self, states: dict) -> List[str]:
       errors = []
       valid_states = {"WAR", "PEACE", "ALLIANCE", "DEFENSIVE_PACT",
                       "NON_AGGRESSION", "OPEN_BORDERS", "ARMISTICE", "TRADE_AGREEMENT"}
       for key, state in states.items():
           nations = key.split("-") if isinstance(key, str) else list(key)
           # No WAR with self
           if len(nations) == 2 and nations[0] == nations[1]:
               errors.append(f"Nation '{nations[0]}' cannot have diplomatic state with itself")
           # Valid enum
           if state not in valid_states:
               errors.append(f"Invalid diplomatic state '{state}' for {key}")
       return errors
   ```

2. **Add vassal circular dependency detection:**
   ```python
   def _validate_vassals(self, vassals: dict) -> List[str]:
       errors = []
       # Check circular: A vassal of B, B vassal of A
       for vassal_name, vassal_data in vassals.items():
           overlord = vassal_data.get("overlord")
           if overlord and overlord in vassals:
               if vassals[overlord].get("overlord") == vassal_name:
                   errors.append(f"Circular vassal: {vassal_name} ↔ {overlord}")
           # Loyalty bounds
           loyalty = vassal_data.get("loyalty", 50)
           if not (0 <= loyalty <= 100):
               errors.append(f"Vassal '{vassal_name}' loyalty {loyalty} out of 0-100 range")
       return errors
   ```

3. **Add coalition state validation:**
   - Leader must be a known nation
   - All members must be known nations
   - Leader must be a member
   - Target must be a known nation
   - Target cannot be a member

4. **Extend Marshal validation** from 27% → ~80%:
   - Strength bounds (0 to 100000)
   - Location must be a valid region
   - Nation must be a known nation
   - Skills in valid range (1-10)
   - No duplicate marshal names
   - Trust bounds (-100 to 100)

5. **Extend WorldState validation** from ~5% → ~50%:
   - Authority bounds per nation
   - Economic fields non-negative
   - Player nation exists and is valid
   - Current turn ≥ 1
   - Region controllers are valid nations or "Neutral"

6. **Write 15+ tests** for game-breaking scenarios:
   - `test_rejects_self_war`
   - `test_rejects_vassal_loop`
   - `test_rejects_invalid_coalition_leader`
   - `test_rejects_negative_strength`
   - `test_rejects_unknown_region_location`
   - `test_rejects_authority_out_of_bounds`
   - `test_accepts_valid_mod` (positive case)

**Expected Changes:** +300-400 lines. Net +300.

**Verification:**
- Run validator on existing scenarios (all should pass)
- Run validator with deliberately broken mods (all should fail with clear messages)
- Full test suite
- Update `docs/MODDING_FORMAT.md` with new validation rules

---

## Summary Table

| Session | R-Items | Root Cause | Priority | Effort | Risk | Depends On | Bugs Prevented |
|---------|---------|-----------|----------|--------|------|-----------|----------------|
| 1 | R3 | RC-5: No test fixtures | CRITICAL | 2h | ZERO | — | ~22 + maintenance × |
| 2 | R1 | RC-1: Post-combat duplication | CRITICAL | 3h | MEDIUM | — | ~75 recurring |
| 3 | R2 | RC-2: No war-state filtering | CRITICAL | 2-3h | LOW | — | ~49 recurring |
| 4 | R4 | RC-4: Ad-hoc response pipeline | MAJOR | 2-3h | MEDIUM | — | ~9 + stale top-bar |
| 5 | R5 | RC-6: Fog filter scatter | MAJOR | 2h | LOW-MED | — | ~18 recurring |
| 6 | R7+R8 | RC-9+RC-10: Display + log | MODERATE | 2-3h | LOW | — | ~12 + prevention |
| 7 | R6 | RC-7: Cooldown/popup sprawl | MAJOR | 3h | MEDIUM | — | ~7 + popup leaks |
| 8 | R9+R20 | Scaling + atomicity | CRIT/MAJ | 2h | LOW | — | perf + double-proc |
| 9 | R18 | Missing enforcement tests | MAJOR | 1-2h | ZERO | S6 | ~18/category |
| 10 | R10 | RC-3: Executor god object | MAJOR | 3h | MEDIUM | S2 | cognitive load |
| 11 | R11 | RC-3: Executor god object | MAJOR | 3h | MEDIUM | S10 | cognitive load |
| 12 | R12 | RC-8: Dialogue chaos | MAJOR | 3h | HIGH | S11 | stuck dialogue |
| 13 | R13 | RC-3: Executor god object | MINOR | 3h | LOW-MED | S11 | cognitive load |
| 14 | R17 | Integration: no timeout | CRITICAL | 1-2h | LOW | — | infinite hang |
| 15 | R15 | Frontend: duplication | MAJOR | 2-3h | MEDIUM | — | signal consistency |
| 16 | R16 | Frontend: Layer 100 collision | MAJOR | 2-3h | MED-HIGH | S15 | popup collision |
| 17 | R14a | Scaling: AI omniscience | CRITICAL | 3h | HIGH | S8 | balance + perf |
| 18 | R14b | Scaling: AI omniscience | CRITICAL | 3h | HIGH | S17 | balance + perf |
| 19 | R14c | Scaling: AI omniscience | CRITICAL | 3h | HIGH | S18 | balance + perf |
| 20 | R14d | Scaling: AI omniscience | CRITICAL | 3h | HIGH | S19 | balance + perf |
| 21 | R19 | Modding: low coverage | MAJOR | 3h | LOW | — | game-breaking mods |

**Total: 21 sessions. ~55-65 hours. Prevents ~240 historical bugs + future recurrences.**

---

## Deferred Findings

These individual findings from the audit are acknowledged but NOT addressed by any R-item. Rationale provided for each.

| # | Finding | Severity | Rationale for Deferral |
|---|---------|----------|----------------------|
| 1-2 | Auto-bombardment decisive_victory + war score | CRITICAL | Addressed in Session 2 (R1) — bundled with pipeline unification |
| 6 | Trust/authority death spiral | MAJOR | Balance tuning — address during Jealousy system implementation or dedicated balance pass |
| 7 | Combat modifier snapshot drift | MAJOR | Low recurrence risk — battle_report snapshot is display-only, doesn't affect gameplay |
| 15 | Capital capture blocks AI proposals | MODERATE | Intentional design — prevents AI peace spam during conquest. Revisit if player feedback indicates issue |
| 17 | Recklessness preserved through break/respawn | MODERATE | Edge case — recklessness only affects AI cavalry. Monitor during playtesting |
| 22 | LLM fallback threshold | MODERATE | Only affects anthropic mode (not mock). Tune when LLM mode is primary |
| 23 | Fixed AI nation order (Britain first-mover) | LOW | Minimal gameplay impact at 4 nations. Address during 80-region expansion (more nations = bigger effect) |
| 24 | Notification lifecycle (no expiry/dedup) | LOW | No player-reported issues. Address if notification bar becomes cluttered |
| 29 | BALANCED/LOYAL personalities unimplemented | LOW | These personalities aren't assigned to any marshal. Implement when adding new marshals |
| 31 | Dispatch hardcoded "France" | LOW | Player is always France in current game. Fix when adding faction selection |
| 33 | Region name substring matching | LOW | Works correctly for current 19 regions. Fix during 80-region expansion |
| 34 | Talleyrand turn_number fallback | LOW | Defensive fallback — no crash, just uses 0. Fix during next Talleyrand work |

### Finding → R-Item Cross-Reference

| Finding # | Addressed By | Status |
|-----------|-------------|--------|
| 1-2 | R1 (Session 2) | Planned |
| 3 | R1 (Session 2) | Planned |
| 4 | R5 (Session 5) | Planned |
| 5 | R4 (Session 4) | Planned |
| 6 | — | Deferred (balance tuning) |
| 7 | — | Deferred (display-only) |
| 8 | R1 (Session 2) | Planned |
| 9 | R1 (Session 2) | Planned |
| 10 | R1 (Session 2) | Planned |
| 11 | R6 (Session 7) | Planned |
| 12 | R1 (Session 2) | Planned — advance_turn documentation |
| 13 | R8 (Session 6) | Planned |
| 14 | — | Dead code — remove during R1 |
| 15 | — | Deferred (intentional design) |
| 16 | R2 (Session 3) | Planned |
| 17 | — | Deferred (edge case) |
| 18 | R1 (Session 2) | Planned |
| 19 | — | Dead code — remove during R11 |
| 20 | R19 (Session 21) | Planned |
| 21 | — | Low priority, mock parser |
| 22 | — | Deferred (LLM mode only) |
| 23 | — | Deferred (80-region expansion) |
| 24 | — | Deferred (no player reports) |
| 25 | R4 (Session 4) | Planned |
| 26 | — | Quick fix candidate |
| 27 | — | Quick fix candidate (docstring) |
| 28 | R8 (Session 6) | Planned |
| 29 | — | Deferred (no marshals use it) |
| 30 | R5 (Session 5) | Planned |
| 31 | — | Deferred (single-faction game) |
| 32 | — | Low priority, cosmetic |
| 33 | — | Deferred (80-region expansion) |
| 34 | — | Quick fix candidate |

---

## Verification Strategy

**Every session must pass ALL of these before marking complete:**

1. **Full test suite:** `.venv\Scripts\python.exe -m pytest tests/ -v` — all 7,281+ tests pass
2. **Serialization enforcement:** `test_serialization_enforcement.py` if ANY model field added/changed
3. **Endpoint testing:** curl-test affected POST endpoints when modifying main.py
4. **Godot smoke test:** Manual test in Godot when modifying .gd files
5. **Pattern verification:** Grep for remaining raw patterns after migration (e.g., direct `diplomatic_states[` writes after R2, manual `_include_popup_passthroughs()` calls after R4)
6. **New enforcement tests pass:** After R18, the enforcement suite catches future regressions

---

## Documentation Updates

**After each session, update:**

| What Changed | Update |
|-------------|--------|
| Session completed | `docs/STATUS.md` — add session summary |
| System behavior changed | `docs/SYSTEMS_REFERENCE.md` — update affected system |
| New serializable fields | `docs/SAVE_FORMAT_REFERENCE.md` — add field documentation |
| New files created | `CLAUDE.md` File Reference table — add new modules |
| Executor split | `CLAUDE.md` "Before Modifying" table — update file references |
| Phase progress | `CLAUDE.md` "Current Phase" — update remaining items |
| Modding validation | `docs/MODDING_FORMAT.md` — add new validation rules |
| AI fog behavior | `docs/ENEMY_AI_REFERENCE.md` — document fog integration |
| All complete | `docs/ROADMAP.md` — mark Architecture Refactoring complete |
