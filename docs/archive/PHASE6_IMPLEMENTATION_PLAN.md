# Phase 6 Implementation Plan

> **Created:** February 6, 2026
> **Covers:** Phase 6.1 (Terrain) + Phase 6.2 (Economy)
> **Specs:** `TERRAIN_SPEC.md` (6.1), `ECONOMY_SPEC.md` (6.2)
> **Pre-implementation decisions:** `TERRAIN_SPEC.md` §14

---

## Methodology: Bottom-Up with Integration Tests at Each Layer

### Why This Approach

**Winner: Bottom-Up (data layer first).** This is what both specs already prescribe in their implementation order sections, and it's the right fit for three reasons:

1. **Spec fidelity.** We have 569 + 1025 lines of detailed specs. The implementation order in each spec was written with dependency awareness. Bottom-up follows the spec's own sequencing, reducing the risk of misinterpretation.

2. **Serialization enforcement.** The project's golden rule is "if it exists on the object, it must serialize." Bottom-up means each model field gets added, serialized, and tested before any logic touches it. The existing `test_serialization_enforcement.py` catches gaps automatically — but only if the field exists on the object when the test runs.

3. **Integration bugs are the historical enemy.** The project's bug history shows a pattern: modifiers applied twice, call sites missed, wrong fields updated. Bottom-up with integration tests at EACH layer (not just at the end) catches these early. Each session ends with tests that prove the new layer works with existing code.

**Runner-up: Vertical Slice.** Building one terrain type end-to-end first would catch integration issues sooner. But with 5 `resolve_battle()` call sites and the recklessness/charge interaction, "one slice" would still touch every file. The spec's bottom-up order is already optimized for this codebase — constants first, then model, then combat, then executor, then pathfinding. Each layer is independently testable.

**Rejected: TDD.** AI writing tests for itself creates a circularity problem — the tests encode the AI's assumptions, not ground truth. Better to write implementation from spec, then write tests that verify spec compliance, then run existing tests as regression protection.

**Rejected: Spike-First.** Analysis phase already mapped all integration points. A spike would re-discover what we already know.

---

## Phase 6.1: Terrain (3 sessions)

### Session 6.1.A: Data Layer + Model
- **Model:** Sonnet
- **Spec steps:** 1, 2, 3, 4 (constants, Region field, REGIONS_DATA, computed properties)
- **Files modified:**
  - `backend/models/region.py` — VALID_TERRAINS, terrain constants dicts, terrain field on Region, `__init__`, `to_dict()`, `from_dict()`, computed properties, updated REGIONS_DATA, updated `create_regions()`
  - `tests/test_serialization_enforcement.py` — Add terrain to Region fixture
  - `backend/modding/doc_generator.py` — Add terrain to example Region
- **Commit point:** "Add terrain field to Region with 6 terrain types and constants"
- **Tests to write:**
  - Terrain field serialization roundtrip
  - VALID_TERRAINS validation (invalid terrain raises ValueError)
  - Computed properties return correct values per terrain type
  - create_regions() assigns terrain from REGIONS_DATA
  - Backward compat: Region without terrain field defaults to "plains"
  - All existing tests still pass (regression)
- **Review needed:** No — data layer is straightforward

### Session 6.1.B: Combat Integration + Cavalry Terrain Rules
- **Model:** Sonnet
- **Spec steps:** 5, 6, 7, 8 (terrain defense bonus, executor wiring, cavalry terrain effects, combat messages)
- **Files modified:**
  - `backend/game_logic/combat.py` — Update `_get_terrain_bonus()` to use `TERRAIN_DEFENSE_BONUS` from region.py, add terrain combat messages, add recklessness bonus terrain scaling for cavalry
  - `backend/commands/executor.py` — All 5 `resolve_battle()` call sites get terrain from defender region. Glorious charge terrain blocking in recklessness popup check (~line 1620) and `_execute_glorious_charge()` (~line 5846)
- **Commit point:** "Wire terrain into combat: defense bonuses, cavalry effects, charge blocking"
- **Tests to write:**
  - Each terrain type gives correct defense bonus
  - Executor passes region terrain (not hardcoded "open") to resolve_battle
  - Legacy terrain values ("open", "fortified") still work
  - Cavalry recklessness bonus scaled by terrain (plains boosted, mountains gutted)
  - Glorious charge blocked in mountains/forest/urban
  - Glorious charge allowed in plains/hills/river_crossing
  - Charge blocking message generated correctly
  - Non-cavalry marshals unaffected by terrain cavalry rules
  - All 5 resolve_battle call sites tested (including strategic sally paths)
- **Review needed:** Yes — combat integration is the highest-risk part of terrain. Multiple call sites, recklessness interaction, single-source-of-truth compliance.

### Session 6.1.C: Weighted Pathfinding + Display + Docs
- **Model:** Sonnet
- **Spec steps:** 9, 10, 11, 12 (Dijkstra pathfinding, terrain display, serialization tests, doc updates)
- **Files modified:**
  - `backend/models/world_state.py` — New `find_weighted_path()` (Dijkstra) and `get_weighted_distance()` methods
  - `backend/commands/strategic.py` — MOVE_TO uses weighted pathfinding via `_calculate_initial_path()`
  - `backend/ai/enemy_ai.py` — AI movement decisions use weighted distance where applicable
  - `backend/commands/executor.py` — Status/scout output includes terrain info
  - `docs/MODDING_FORMAT.md` — Document terrain field and valid values
  - `docs/SYSTEMS_REFERENCE.md` — Expand terrain section with implementation details
  - `docs/SAVE_FORMAT_REFERENCE.md` — Add terrain to Region fields
- **Commit point:** "Add weighted pathfinding, terrain display, update docs"
- **Tests to write:**
  - Weighted pathfinding prefers lower-attrition routes
  - Weighted pathfinding works when mountains are the only path
  - PURSUE ignores weighted pathfinding (stays on BFS direct path)
  - get_weighted_distance() returns correct weighted distance
  - find_weighted_path() and find_path() return different routes when terrain varies
  - Status output shows terrain info
  - Terrain serialization complete (run test_serialization_enforcement.py)
- **Review needed:** No — pathfinding is self-contained, lower risk than combat

---

## Phase 6.2: Economy (7 sessions)

### Session 6.2.A: Region Types + Income + Gold
- **Model:** Sonnet
- **Spec steps:** 1, 2 (region types, differentiated income, per-nation gold)
- **Files modified:**
  - `backend/models/region.py` — Add `region_type` field, update REGIONS_DATA with types and new income values, `to_dict()`, `from_dict()`
  - `backend/models/world_state.py` — Replace `self.gold` with `nation_gold` dict, add gold convenience property, update `calculate_turn_income()` to accept nation param, remove +200 capital bonus
  - `tests/test_serialization_enforcement.py` — Add region_type to Region fixture, nation_gold to WorldState fixture
- **Commit point:** "Add region types, differentiated income, per-nation gold tracking"
- **Tests to write:**
  - Region type serialization roundtrip
  - Income by region type (capital=300, major_city=200, etc.)
  - Per-nation gold tracking (set/get for France, Britain, Prussia)
  - gold convenience property reads/writes player nation
  - calculate_turn_income() works for any nation
  - Existing tests pass with new gold system
- **Review needed:** No

### Session 6.2.B: Upkeep + Bankruptcy + Admin AP
- **Model:** Sonnet
- **Spec steps:** 3, 4, 5 (upkeep, bankruptcy, admin AP pool)
- **Files modified:**
  - `backend/models/world_state.py` — `calculate_turn_upkeep()`, `bankruptcy_turns` field, admin AP fields (`admin_actions_remaining`, `max_admin_actions`), `use_admin_action()`, unused AP bonus
  - `backend/commands/executor.py` — Action routing to admin pool for admin actions, AP check uses correct pool
- **Commit point:** "Add upkeep, bankruptcy system, and admin action point pool"
- **Tests to write:**
  - Upkeep formula: (strength // 1000) * 5
  - Net income calculation (income - upkeep + admin bonus)
  - Bankruptcy progression: warning at turn 1, severe at turn 2, desertion at turn 3+
  - Desertion rate: 5% per marshal per turn during bankruptcy
  - Bankruptcy counter resets when solvent
  - Admin AP separate from command AP
  - Admin actions deduct from admin pool
  - Command actions deduct from command pool
  - Unused admin AP generates gold bonus
- **Review needed:** No

### Session 6.2.C: Stability + War Damage
- **Model:** Sonnet
- **Spec steps:** 6, 7 (stability, war damage)
- **Files modified:**
  - `backend/models/region.py` — `stability` field (0-100), `war_damage` field (0.0-0.5), `get_effective_income()` method, stability growth logic
  - `backend/models/world_state.py` — Per-turn stability growth, war damage recovery, battle damage application
  - `backend/game_logic/combat.py` — War damage applied on battle in region
- **Commit point:** "Add region stability and war damage systems"
- **Tests to write:**
  - Stability income modifiers (hostile=0%, unrest=25%, settling=75%, stable=100%)
  - Stability growth per turn (base 5 + garrison 5)
  - War damage income modifier (1.0 - war_damage)
  - War damage from battle (+0.10 normal, +0.20 major)
  - War damage cap at 0.50
  - War damage natural recovery (0.02/turn)
  - Combined income formula: base * stability_mod * damage_mod
- **Review needed:** No

### Session 6.2.D: Recruitment Rework + Morale Dilution
- **Model:** Sonnet
- **Spec steps:** 8, 14 (morale dilution, recruitment location restrictions)
- **Files modified:**
  - `backend/commands/executor.py` — Update `_execute_recruit()`: admin AP cost, morale dilution formula, stability restriction, capital discount
- **Commit point:** "Rework recruitment: admin AP, morale dilution, location restrictions"
- **Tests to write:**
  - Recruitment costs admin AP (not command AP)
  - Morale dilution: weighted average of existing + recruit morale
  - Stability gate: blocked below 50, +50% cost at 51-75
  - Capital discount: 25% less gold
  - "Recruit at [region]" routes to nearest marshal
  - "Recruit for [marshal]" routes to marshal's location
- **Review needed:** No

### Session 6.2.E: Plunder/Secure + Buildings
- **Model:** Sonnet (Opus review after)
- **Spec steps:** 9, 10 (capture choice, buildings)
- **Files modified:**
  - `backend/models/world_state.py` — `pending_capture_choice` field
  - `backend/models/region.py` — `plundered` field, `buildings` list, `building_under_construction` field
  - `backend/commands/executor.py` — Capture choice handling (plunder/secure effects), build action, repair action, construction timer processing
  - `backend/main.py` — New `/capture_choice` endpoint
- **Commit point:** "Add plunder/secure capture choice and building system"
- **Tests to write:**
  - Plunder: immediate gold, stability 10, war damage +0.35, buildings destroyed
  - Secure: no bonus, stability 25, war damage 0, buildings damaged
  - pending_capture_choice blocks other commands
  - AI capture decision by personality
  - Building construction: cost, timer, completion
  - Building effects: supply depot (+50 income, +10k supply), fortification (+25% defense), training ground (55% recruit morale)
  - Building destruction on plunder, damage on secure
  - Construction cancelled on capture
- **Review needed:** Yes — plunder/secure is a new popup pattern (like objection), and buildings add multiple new fields to Region. Integration risk with main.py endpoint.

### Session 6.2.F: Supply Limits + Movement Attrition + Fortification Capture
- **Model:** Sonnet (Opus review after)
- **Spec steps:** 11, 12, 13 (supply limits, movement attrition, contested capture)
- **Files modified:**
  - `backend/models/region.py` — `supply_capacity` computed property
  - `backend/models/world_state.py` — Supply attrition processing per turn
  - `backend/commands/executor.py` — Movement attrition in `_execute_move()` and `_execute_attack()`, harassment attrition through fortified cities, contested capture hold timer
  - `backend/commands/strategic.py` — Movement attrition during strategic movement
- **Commit point:** "Add supply limits, movement attrition, and contested city capture"
- **Tests to write:**
  - Supply capacity by region type
  - Over-limit attrition rates (1%, 3%, 5% by excess ratio)
  - Forced retreat overrides supply limits
  - Movement attrition: 1% base + size penalty
  - Large army attrition scaling
  - Retreat attrition half rate
  - Harassment attrition through fortified cities
  - Contested capture: empty fortified = 1 turn hold, garrisoned = 2 turns
  - Marshal blocked during occupation
- **Review needed:** Yes — movement attrition touches executor, strategic, and AI. Multiple integration points. Contested capture is new mechanic.

### Session 6.2.G: AI Admin Phase + Parser + Display + Docs
- **Model:** Sonnet (Opus review of full Phase 6)
- **Spec steps:** 15, 16, 17, 18 (enemy AI admin, parser, turn summary, docs)
- **Files modified:**
  - `backend/ai/enemy_ai.py` — `execute_admin_phase()`, admin priority logic
  - `backend/game_logic/turn_manager.py` — Call AI admin phase after military
  - `backend/commands/executor.py` — `_execute_economy()` free action, `_execute_build()`, `_execute_repair()`
  - `backend/ai/llm_client.py` — Mock parser keywords for build, repair
  - `backend/commands/parser.py` — Add build, repair to valid_actions
  - `backend/ai/validation.py` — Add build, repair to VALID_ACTIONS
  - `backend/main.py` — Financial summary in end-turn response
  - `docs/MODDING_FORMAT.md` — Document new region fields, nation_gold, admin AP
  - `docs/SYSTEMS_REFERENCE.md` — Economy system reference section
  - `docs/SAVE_FORMAT_REFERENCE.md` — All new serialization fields
- **Commit point:** "Complete Phase 6.2: AI admin phase, new commands, turn summary, docs"
- **Tests to write:**
  - AI recruits when marshal below 40% starting strength
  - AI builds fortification at border cities
  - AI repairs high-income damaged regions
  - AI saves AP for income bonus when nothing to do
  - Economy/treasury/finances free command returns correct data
  - Build/repair parser keywords detected
  - Turn summary shows correct income breakdown
  - Full end-to-end: player turn + enemy turn + income phase
- **Review needed:** Yes — full Phase 6 Opus review. AI admin phase integrates with turn_manager, executor, and economy. This is where all systems come together.

---

## Code Review Checkpoints

1. **After Session 6.1.B** — Combat integration review. Verify: all 5 call sites correct, single-source-of-truth compliance, cavalry boolean logic, charge blocking. This is the highest-risk terrain change.

2. **After Session 6.2.E** — Plunder/secure + buildings review. New popup pattern, new endpoint, multiple new Region fields. Verify serialization, pending state blocking, AI capture personality logic.

3. **After Session 6.2.F** — Supply + attrition + contested capture review. Movement attrition in 3 files (executor, strategic, AI). Supply attrition per-turn processing. Contested capture hold timer.

4. **After Session 6.2.G** — Full Phase 6 review. AI admin phase, turn flow integration, financial summary. Run full test suite. Smoke test via curl.

---

## Stop-and-Test Gates

| Gate | After Session | What to Verify |
|------|---------------|----------------|
| **Terrain data correct** | 6.1.A | `pytest tests/test_serialization_enforcement.py -v` passes. All 13 regions have terrain assigned. |
| **Combat works with terrain** | 6.1.B | Full test suite passes. Curl test: attack command returns terrain in combat result. |
| **Phase 6.1 complete** | 6.1.C | Full test suite. Curl test MOVE_TO avoids mountains. Status shows terrain. |
| **Economy foundations** | 6.2.B | Full test suite. Curl test: end turn shows income/upkeep/net. |
| **Buildings + capture** | 6.2.E | Full test suite. Curl test: build command, capture choice popup. |
| **Phase 6.2 complete** | 6.2.G | Full test suite. Multi-turn curl test: income, upkeep, bankruptcy, AI recruitment. |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Executor resolve_battle site missed | Low | High — silent wrong terrain in combat | Analysis identified all 5 sites. Grep for `resolve_battle` after implementation to verify. |
| Recklessness + terrain interaction bug | Medium | Medium — cavalry bonus wrong | Test each recklessness level (0-4) on each terrain type. Verify plains boosts, mountains guts. |
| Weighted pathfinding breaks strategic orders | Medium | High — marshals take wrong paths | Keep BFS as fallback. Test MOVE_TO through varied terrain. Test PURSUE stays on BFS. |
| Region constructor change breaks tests | Low | Low — tests use kwargs | Pre-existing positional arg bugs in test_objection_v2 and test_strategic_objections won't break (terrain has default). Verify after 6.1.A. |
| Economy gold property breaks existing code | Medium | High — anywhere `world.gold` is used | Search for all `world.gold` references, ensure convenience property covers them. Add backward compat. |
| Supply attrition + movement attrition stacking too harsh | Medium | Medium — armies melt | Playtest balance after 6.2.F. Attrition rates are tuning knobs in constants. |
| AI admin phase infinite loop | Low | High — turn never ends | Admin phase has AP budget and break-on-failure safety. Test with edge cases (0 gold, no valid actions). |
| Pending_capture_choice + pending_objection collision | Low | High — two popups at once | Capture choice check added to blocking checks at top of execute(), same pattern as pending_objection. Only one can be pending at a time. |
| Building serialization circular refs | Medium | Medium — API crash | Use same pattern as executor results: strip `new_state` before API response. Buildings are simple dicts, no circular refs. |

---

## Session Dependency Graph

```
6.1.A (data) ──> 6.1.B (combat) ──> 6.1.C (pathfinding + docs)
                                          │
                                          ▼
6.2.A (region types + gold) ──> 6.2.B (upkeep + admin AP)
         │                              │
         ▼                              ▼
    6.2.C (stability + war damage)  6.2.D (recruitment)
         │                              │
         └──────────┬───────────────────┘
                    ▼
             6.2.E (plunder/secure + buildings)
                    │
                    ▼
             6.2.F (supply + attrition + siege)
                    │
                    ▼
             6.2.G (AI admin + parser + display)
```

**Parallelizable pairs (if context allows):**
- 6.2.C (stability) and 6.2.D (recruitment) are independent of each other
- 6.2.C and 6.2.D both depend on 6.2.A

**Must be sequential:**
- 6.1.A → 6.1.B → 6.1.C (each layer builds on previous)
- 6.2.E requires 6.2.C (stability for capture) AND 6.2.D (recruitment location restrictions)
- 6.2.F requires 6.2.E (buildings for contested capture + fortification harassment)
- 6.2.G requires everything (AI admin uses recruit/build/repair)

---

## Reordering from Spec

Two adjustments to the spec's suggested order:

1. **Economy step 14 (recruitment restrictions) merged into step 8 session (6.2.D).** The spec lists recruitment restrictions as step 14, but they're inseparable from the recruitment rework (step 8). Implementing recruit without location restrictions means rewriting it later. Combine.

2. **Economy step 13 (contested capture) merged with steps 11-12 (supply + attrition) in session 6.2.F.** Contested capture depends on the fortification building from step 10, and harassment attrition is part of the movement attrition system. Grouping these prevents split context.

---

## Total Estimate

- **Sessions:** 10 (3 terrain + 7 economy)
- **Model allocation:** 9 Sonnet sessions + 1 final Opus review pass
- **Review checkpoints:** 4 (after 6.1.B, 6.2.E, 6.2.F, 6.2.G)
- **Stop-and-test gates:** 6

---

## Spec Concerns Discovered During Planning

1. **`world.gold` usage breadth.** The economy spec says "replace `self.gold` directly with `self.nation_gold[self.player_nation]`" and add a convenience property. Before session 6.2.A, grep for ALL `world.gold` references across the codebase (executor, main.py, tests). The convenience property should make this transparent, but verify.

2. **`_execute_recruit()` current implementation.** The economy spec says it "exists" and "costs 200 gold, adds 10,000 troops." The current implementation needs to be read carefully before session 6.2.D — it may have additional logic (nearest marshal routing, etc.) that the spec doesn't account for.

3. **Turn flow ordering.** Economy spec §12 defines a 15-step turn flow. The current flow in `turn_manager.py` and `world_state.py` will need careful integration. Session 6.2.G is where this all comes together — it's the highest risk session.

4. **The economy spec references `terrain` in movement attrition (§10 "Future Hook: Terrain type will multiply movement attrition").** Since terrain ships before economy, session 6.2.F should wire terrain attrition multipliers into movement attrition from the start, not leave it as a "future hook."
