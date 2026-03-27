# Architecture Audit Specification

**Created:** 2026-03-27
**Purpose:** Holistic architecture review producing actionable refactoring recommendations.
**Approach:** Multi-pass looping audit. Each pass covers one architectural concern, reads the actual code, and produces concrete recommendations with file/line references. Loop until context is exhausted.

---

## How This Audit Works

This is NOT a bug hunt. Previous audits found ~450 bugs. This audit asks: **why do those bugs keep appearing, and what structural changes would prevent entire categories?**

Each pass below is self-contained. The auditor should:
1. Read the specified files thoroughly
2. Analyze the architectural concern described
3. Produce findings with concrete file:line references
4. Rate severity: CRITICAL (causes recurring bugs) / MAJOR (maintenance burden) / MINOR (code smell)
5. Produce a specific, actionable recommendation with estimated scope (files touched, lines changed)
6. Move to the next pass

After all passes complete, produce a **Refactoring Roadmap** — ordered sessions that could be executed independently, with dependencies noted.

---

## Pass 1: The Executor God Object

**Read:** `backend/commands/executor.py` (full file scan — note method boundaries, line counts, duplication)

**Question:** executor.py is 14,736 lines with 51 `_execute_*` methods in a single class. What are the natural module boundaries?

**Analyze:**
1. **Method grouping** — Which `_execute_*` methods share state, helpers, or domain concepts? Map the natural clusters:
   - Combat domain (attack, glorious_charge, bombardment, charge, general_attack, general_defensive, garrison)
   - Movement domain (move, retreat, scout, auto_assign_*)
   - Tactical domain (fortify, unfortify, drill, form_square, break_square, defend, stance_change)
   - Diplomacy domain (diplomatic_*, make_vassal, release_vassal, invest_vassal, change_autonomy)
   - Economy domain (recruit, build, build_watchtower, repair, economy)
   - Meta domain (end_turn, help, status, debug, cheat, wait, cancel, post_objection, restrain)
   - Strategic domain (strategic_command)
2. **Shared helper usage** — Which helpers are used by which clusters? Are any helpers only used by one cluster?
3. **Cross-cluster dependencies** — If we extracted DiplomacyExecutor, what would it need from the combat cluster? Map the dependency edges.
4. **The `execute()` router** — How does the top-level dispatch work? Could it delegate to sub-executors cleanly?

**Deliverable:** A proposed module split with dependency diagram. For each proposed module: which methods move, which helpers move, what interface it needs from the parent.

---

## Pass 2: Post-Combat Pipeline Duplication

**Read:** These specific sections of `backend/commands/executor.py`:
- `_execute_attack` (the full ~1,900 lines — identify every post-combat step)
- `_execute_glorious_charge` (the full ~400 lines)
- `_process_reckless_cavalry` or the reckless auto-charge path
- `_resolve_garrison_combat`
- Auto-bombardment kill path (inside `_execute_bombardment`)
- Auto-charge path (inside `_execute_attack` after movement)

**Question:** The #1 recurring audit finding across 5 audits is "auto-action path X missing post-combat step Y." What would a unified post-combat pipeline look like?

**Analyze:**
1. **Catalog every post-combat step** in `_execute_attack` (the most complete path). Number them 1-N.
2. **For each other combat path**, check which steps are present, missing, or different. Build a matrix:
   ```
   Step                    | attack | glorious | auto-charge | garrison | auto-bombard
   log_battle_event        |   Y    |    Y     |     ?       |    ?     |     ?
   update_intel             |   Y    |    Y     |     ?       |    ?     |     ?
   battle_effects_region   |   Y    |    Y     |     ?       |    ?     |     ?
   ...
   ```
3. **Identify which steps are universal** vs path-specific (e.g., reinforcement processing only applies to coordinated attacks).
4. **Propose the pipeline interface** — What arguments would `_post_combat_pipeline(battle_result, attacker, defender, world, **context)` need?

**Deliverable:** The completeness matrix, the proposed pipeline function signature, and a list of path-specific exceptions that can't be unified.

---

## Pass 3: WorldState Field Sprawl & advance_turn

**Read:** `backend/models/world_state.py` — focus on `__init__`, `advance_turn`/`_advance_turn_internal`, `_process_tactical_states`, `to_dict`, `from_dict`

**Question:** WorldState has ~108 fields. Which fields naturally group into sub-objects, and would extracting them improve or hurt the codebase?

**Analyze:**
1. **Field clustering** — Group the 108 fields by domain:
   - Core game (turn, gold, victory, game_over)
   - Action economy (AP fields)
   - Diplomacy (states, relations, proposals, dialogue, war scores, treaties...)
   - Coalition (threat, brewing, active, cooldowns...)
   - Vassal (vassals dict, loyalty, rebellion...)
   - Combat tracking (active_battle, battle_history...)
   - Fog/Intel (region_intel, intel_sources...)
   - UI/Popup (pending_*, popup_*)
   Count fields per cluster.

2. **advance_turn decomposition** — The 384-line method has ~35 sequential steps. Which steps could be extracted into domain-specific processors without creating circular dependencies?
   - Could diplomacy steps call `diplomacy.process_turn(world)` (already partially done)?
   - Could coalition steps call `coalition.process_turn(world)`?
   - What's the ordering constraint graph between steps?

3. **Serialization impact** — If fields were grouped into sub-objects (e.g., `world.diplomacy.states` instead of `world.diplomatic_states`), what's the migration cost? How many files reference these fields directly?

4. **The getattr epidemic** — Count `getattr(world, ...)` calls across the codebase. These indicate fields that callers aren't sure exist. Are they all for backward compatibility, or do they reveal schema uncertainty?

**Deliverable:** Field cluster map with counts, advance_turn step dependency graph, and a recommendation on whether sub-objects are worth the migration cost.

---

## Pass 4: Enemy AI Structure

**Read:** `backend/ai/enemy_ai.py` (full scan — method inventory, size distribution, decision flow)

**Question:** At 5,556 lines and 76 methods, is this file maintainable? What's the natural decomposition?

**Analyze:**
1. **Decision tree mapping** — The P0-P8 priority system is documented. Trace the actual code flow from `process_nation_turn()` → `decide_single_action()` → P-level evaluators. Is the code organized to match the documented decision tree?
2. **Method size distribution** — Histogram of method sizes. How many are >100 lines? >200?
3. **Personality coupling** — How deeply do personality checks permeate? Could personality logic be extracted into a strategy pattern, or is it too interleaved?
4. **Duplication with player executor** — Golden Rule #5 says "Enemy AI uses SAME executor as player." Verify this is true. Does enemy_ai.py ever bypass the executor to modify state directly?
5. **Natural split candidates:**
   - Evaluation/scoring methods → `EnemyAIScoring`
   - Target selection/pathfinding → `EnemyAITargeting`
   - Decision orchestration → stays in `EnemyAI`

**Deliverable:** Proposed split with method assignments. Assessment of whether the split would actually reduce cognitive load or just move it.

---

## Pass 5: Test Infrastructure

**Read:** 5-10 test files sampling different areas: one combat test, one diplomacy test, one audit test, one integration test, one small test. Also check for `tests/conftest.py`.

**Question:** 200 test files with 120K lines and no shared fixtures. What's the maintenance cost, and what would a `conftest.py` look like?

**Analyze:**
1. **Factory function census** — How many distinct `_make_world()` variants exist? How do they differ? Could they be unified with keyword arguments?
2. **Setup duplication cost** — If Marshal.__init__ adds a new required field, how many test files break? Estimate from import patterns.
3. **Fixture design** — Propose a `conftest.py` with:
   - `world()` fixture (configurable via params)
   - `executor()` fixture
   - `game_state()` fixture
   - `marshal_factory()` for custom marshals
   - `diplomatic_world()` for tests needing full diplomacy setup
4. **Migration feasibility** — Could conftest be adopted incrementally (new tests use it, old tests keep working)?
5. **Test organization** — Is there a pattern to which tests cover which systems? Could tests be reorganized into subdirectories?

**Deliverable:** Proposed conftest.py interface, migration strategy, effort estimate.

---

## Pass 6: Module Dependency Graph

**Read:** Import statements across all `backend/` Python files.

**Question:** What does the dependency graph look like? Are there circular imports, God-node imports, or layering violations?

**Analyze:**
1. **Build the import graph** — For each backend .py file, list what it imports from other backend files. Note any `from X import Y` inside functions (lazy imports, often hiding circular deps).
2. **Identify circles** — Any A→B→A import cycles? Any longer cycles?
3. **Layer violations** — The expected layer is: models → game_logic → commands → ai → main. Do any lower layers import from higher layers?
4. **Fan-in analysis** — Which modules are imported by the most others? (Likely world_state, marshal, region). Are these stable enough to be high-fan-in?
5. **Fan-out analysis** — Which modules import the most others? (Likely executor, main). Is this appropriate for their role?

**Deliverable:** Dependency graph (text format), identified circles, layer violation list, and whether the current structure supports clean module extraction.

---

## Pass 7: State Mutation Patterns

**Read:** Trace how state changes flow through the system. Pick 3 scenarios:
1. A simple attack command
2. An end-turn cycle
3. A diplomatic proposal acceptance

**Question:** Who mutates WorldState, and is there a consistent pattern?

**Analyze:**
1. **Mutation sites** — For each scenario, list every point where `world.X = Y` or `world.X.append(Y)` happens. Who does it — executor, game_logic module, model method, or main.py?
2. **Consistency** — Is there one pattern (e.g., "only executor mutates world") or is mutation scattered?
3. **Transaction boundaries** — If step 5 of a 10-step operation fails, is state partially mutated? Are there any rollback mechanisms?
4. **The pending_* pattern** — Count all `pending_*` fields on WorldState. These represent deferred state transitions. Is the lifecycle (set → read → clear) consistent? Any fields that are set but never cleared, or cleared before being read?

**Deliverable:** Mutation pattern map, consistency assessment, identified risks.

---

## Pass 8: Response Pipeline (Backend → Frontend)

**Read:** `backend/main.py` response construction, `_include_popup_passthroughs()`, and a sample of Godot `.gd` files that consume responses.

**Question:** Is the backend→frontend contract well-defined, or is it ad-hoc per endpoint?

**Analyze:**
1. **Response shape consistency** — Compare response dicts across 5+ POST endpoints. Is there a common structure, or does each endpoint return a different shape?
2. **The popup passthrough pattern** — `_include_popup_passthroughs()` injects 7+ popup fields into every response. Is this the right architecture, or should popups be a separate polling mechanism?
3. **Error response consistency** — When an endpoint fails, is the error shape consistent? Does Godot handle all error shapes?
4. **Embedded state** — How much game state is embedded in every response? Could responses be smaller if Godot cached state and only received deltas?
5. **The active_wars embedding** — War status is embedded in every response. Is this necessary, or could it be a separate GET endpoint that Godot polls?

**Deliverable:** Response contract analysis, consistency issues, and whether a response schema/builder would help.

---

## Pass 9: Serialization & Save Format Architecture

**Read:** `to_dict()`/`from_dict()` across Marshal, WorldState, Region, StrategicOrder, Trust, AuthorityTracker, VindicationTracker. Also `save_manager.py` and `test_serialization_enforcement.py`.

**Question:** Is the serialization architecture robust, or held together by convention and one enforcement test?

**Analyze:**
1. **Round-trip fidelity** — Does `from_dict(to_dict(obj))` produce an identical object for all serializable classes? Are there any lossy conversions?
2. **Backward compatibility** — How are old save formats handled? Is there versioning? What happens if a field is added, removed, or renamed?
3. **The enforcement test** — How does `test_serialization_enforcement.py` work? Does it catch all field types (including nested objects, enums, dicts-of-dicts)?
4. **Fragility assessment** — If someone adds a field to Marshal.__init__ but forgets to_dict/from_dict, what breaks? How quickly is it caught?
5. **Alternative approaches** — Would dataclasses, Pydantic models, or attrs reduce the serialization boilerplate? What's the migration cost?

**Deliverable:** Serialization robustness rating, gap analysis, and whether a schema-driven approach is worth pursuing.

---

## Pass 10: Code Conventions & Consistency

**Read:** Sample methods across 6+ files. Look at naming, error handling, logging, docstrings.

**Question:** Are there consistent conventions, or does each file follow its own style?

**Analyze:**
1. **Naming conventions** — Are method names consistent? (`get_X` vs `calculate_X` vs `X` for getters). Field names (`X_cooldown` vs `X_cooldowns` vs `cooldown_X`)?
2. **Error handling** — Is there a consistent pattern? (Return dict vs raise exception vs return None). How are errors communicated to the frontend?
3. **Logging** — Is there a consistent logging approach? (print vs debug_print vs logging module). Are there leftover debug prints?
4. **Magic numbers** — Are constants defined and named, or are there bare numbers in logic?
5. **Import organization** — stdlib → third-party → local? Consistent across files?
6. **Type hints** — Present? Consistent? Useful?

**Deliverable:** Convention inventory, inconsistency list, proposed style guide additions.

---

## Pass 11: Scaling Assessment

**Read:** Consider the current 19-region, 4-nation, ~12-marshal game scope vs the planned 80-region expansion.

**Question:** What architectural decisions are fine at 19 regions but will break at 80?

**Analyze:**
1. **O(n) patterns** — Find loops that iterate all regions, all marshals, all nations. What's the current cost vs 80-region cost?
2. **AI omniscience** — Enemy AI currently sees everything. At 80 regions with fog, what changes?
3. **State size** — WorldState serialized size at 19 regions. Projected at 80. Save/load performance?
4. **Turn processing time** — advance_turn with 19 regions. What steps scale linearly, quadratically, or worse?
5. **Diplomacy scaling** — 4 nations = 6 bilateral relationships. 8 nations = 28. Formula/loop impact?

**Deliverable:** Scaling risk matrix (which systems need refactoring before 80-region expansion).

---

## Pass 12+: Deep Dives (If Context Remains)

If context budget allows after Passes 1-11, do targeted deep dives into:

- **Dialogue state machine lifecycle** — The `pending_diplomatic_dialogue` single-field overwrite pattern. How many writers, what's the collision risk, is a queue the right fix?
- **The `_ACTION_DISPLAY_NAMES` pattern** — How consistently are internal names translated before reaching the frontend?
- **Notification system architecture** — Is the EU4-style persistent notification approach scaling well?
- **Campaign log filter architecture** — Whitelist vs blacklist, and why new events keep being invisible.
- **Strategic order lifecycle** — From issuance through multi-turn execution to completion/cancellation.
- **Modding system architecture** — Is the validator comprehensive? What can mods break?

---

## Final Deliverable: Refactoring Roadmap

After all passes, produce:

### Priority-Ordered Refactoring Sessions

For each proposed session:
- **What:** Concrete scope (e.g., "Extract _post_combat_pipeline from executor.py")
- **Why:** Which recurring problem it eliminates
- **Effort:** Estimated lines changed, files touched, test impact
- **Risk:** What could break, how to verify
- **Dependencies:** Which sessions must come first
- **Independent?** Can this be done without blocking other work?

### Architecture Principles

Distill findings into 5-10 architecture principles that should guide future development. These go beyond the current Golden Rules.

### What NOT to Refactor

Explicitly list things that look messy but should be left alone, with rationale. (e.g., "WorldState as a God Object is intentional and the migration cost exceeds the benefit.")

---

## Audit Execution Instructions

**For the auditor (Claude agent):**

1. Start with Pass 1. Complete it fully before moving to Pass 2.
2. For each pass, READ THE ACTUAL CODE. Do not rely on summaries or assumptions.
3. Produce findings with specific file:line references.
4. After each pass, write a brief summary (3-5 sentences) before moving on.
5. If a pass reveals something that changes a previous pass's findings, note it.
6. **LOOP:** After completing all numbered passes, continue with deep dives until context is exhausted.
7. **ALWAYS** end with the Refactoring Roadmap, even if you ran out of context mid-pass — summarize what you have.
8. Be honest about what's "good enough" vs what truly needs changing. Not everything messy is worth fixing.
9. Prefer recommendations that reduce the CATEGORY of bugs (structural fixes) over ones that fix individual instances.
10. Consider the game's current scope (19 regions, single-player, local server) when assessing urgency.
