# Fog of War Implementation Plan

> **Session 32 Deliverable — Architectural review + implementation roadmap**
> **Spec:** `docs/FOG_OF_WAR_SPEC.md` (508 lines, 16 sections)
> **Created:** February 11, 2026
> **Author:** Claude (Opus), Session 32

---

## Part 1: Spec Review — Issues Found

Issues categorized by severity. **CRITICAL** = blocks implementation or causes crashes. **HIGH** = will cause bugs if not addressed. **MEDIUM** = design gap needing a decision. **LOW** = minor polish.

### CRITICAL Issues

**C1: `get_game_state_summary()` exposes ALL enemy data — 12+ API endpoints affected**

The spec correctly identifies that API responses need filtering (§4, §11.1), but underestimates the scope. `world_state.py:get_game_state_summary()` builds `map_data` with ALL marshals visible and an `"enemies"` dict that exposes every enemy marshal's location, strength, morale, and stance. This single function is called by 12+ endpoints (all `/command` responses, `/status`, `/get_state`, etc.).

**Pre-implementation fix needed:**
- Create a `get_filtered_game_state_summary(intel_store)` wrapper or add an `intel` parameter to the existing function
- The filtering must happen at THIS level, not at each of the 12+ call sites
- Existing tests that assert on `get_game_state_summary()` output will need updating

**C2: Scout action does NOT persist intel to WorldState**

The spec (§4.3) says "No changes to scout mechanics needed." This is incorrect. `executor.py:_execute_scout()` currently returns intel in the `events` dict but does NOT write anything to the world state. Scout reveals are ephemeral — they exist only in the API response for that command. The fog system requires scout results to persist as FULL visibility in the `intel` store.

**Pre-implementation fix needed:**
- Add `world.update_intel_from_scout(region_name, turn)` call in `_execute_scout()` for both targeted and adjacent scout
- This is listed in §12 Session 32 but incorrectly described as "wire scout action" — it's not wiring, it's new behavior

**C3: Enemy phase display reveals ALL enemy actions**

`main.py` lines 441-468 cleans up the enemy phase result but sends ALL enemy actions/targets to Godot. The spec (§4.2) acknowledges this but the implementation plan (§12) places it in Session 34. This must be wired in Session 33 alongside the status command filter, not later — otherwise Sessions 32-33 have a broken game where fog is applied to status but enemy phase leaks everything.

**Pre-implementation fix needed:**
- Move enemy phase filtering to Session 33 (alongside status command filtering)
- Or accept that Sessions 32-33 will have inconsistent fog behavior (status filtered, enemy phase not)

### HIGH Issues

**H1: Watchtower NOT in `_extract_building_type()` keywords or `BUILDING_TYPES`**

The spec (§7.2) proposes watchtower as a dedicated field on Region, separate from the building slot system. However, `executor.py:_extract_building_type()` uses keyword matching to parse "build watchtower in Paris" — the keyword "watchtower" is not in the keyword list. `BUILDING_TYPES` in `region.py` also doesn't include watchtower.

**Design decision needed:**
- Option A: Add "watchtower" to `_extract_building_type()` alongside existing buildings, but route to a separate `_execute_build_watchtower()` handler that uses the dedicated field instead of slot system
- Option B: Create a new parse keyword entirely (e.g., "build watchtower" as a distinct action from "build")
- **Recommendation: Option A** — reuse existing build command infrastructure, branch internally based on building type

**H2: Watchtower field design conflicts with existing building patterns**

The spec proposes `watchtower: str` with states "none"/"under_construction"/"active"/"damaged" plus `watchtower_turns_remaining: int`. This is a different pattern from existing buildings (list of dicts with `type`, `status`, `turns_remaining`). The repair command (`_execute_repair()`) specifically iterates the `buildings` list to find damaged buildings.

**Pre-implementation fix needed:**
- `_execute_repair()` must be extended to check the watchtower field in addition to the buildings list
- `_execute_build()` must check watchtower state in addition to building slots
- Construction timer processing (`process_construction_timers()`) must handle watchtower countdown alongside building countdowns
- Battle damage logic must include watchtower alongside civilian buildings

**H3: PURSUE/SUPPORT in `strategic.py` have 5+ direct enemy location accesses**

`strategic.py:_execute_pursue()` calls `world.get_marshal(order.target)` and reads `target.location` directly — bypassing fog. `_execute_support()` does the same for ally marshals (correct for SUPPORT, but the same pattern is used for target validation).

The spec (§5.1) says PURSUE needs "known or stale" target location. The implementation must:
- Check intel store for target's last known location before pathfinding
- If STALE/LAST_KNOWN: use `known_marshals[].location` from intel (may be wrong)
- If UNKNOWN: reject order with "No intelligence on target"
- On arrival at empty region: generate `target_not_found` interrupt

**H4: Objection system has 8+ fog-unaware enemy data access points**

`objection_v2.py` helper functions directly access enemy data without fog filtering:
- `_check_enemy_adjacent()` — sees all enemies regardless of fog
- `_get_friendly_to_enemy_ratio()` — exact enemy strength
- `_get_enemy_to_friendly_ratio()` — exact enemy strength
- `_is_outnumbered_2to1()` — exact comparison
- `_path_crosses_enemy()` — sees all enemy positions
- `_check_attack_target_fortified()` — sees enemy fort status
- `_get_attack_odds_ratio()` — exact odds calculation

**Design decision needed (spec §6.3 partially addresses this):**
- At FULL visibility: use exact values (current behavior)
- At PARTIAL: use strength bands for ratio calculations (e.g., treat "substantial army" as 25,000)
- At STALE/LAST_KNOWN/UNKNOWN: cannot calculate ratios, different trigger logic
- This is primarily V2b scope (Phase 7), but the data access pattern must be fog-aware NOW to avoid hardening debt later
- **Recommendation:** Add a `get_visible_enemies_near()` helper that returns only fog-appropriate data. Objection helpers call this instead of raw `world.get_enemies_in_region()`. In Phase 6, return actual data (fog not applied to objections yet). In V2b, switch to filtered data. This is a TODO marker + helper function, not full implementation.

**H5: `calculate_visibility()` execution timing not specified in turn pipeline**

The spec (§3.3) says "each turn, before player actions, recalculate visibility." The actual turn pipeline in `world_state.py:_advance_turn_internal()` has many phases. The spec's §12 says Session 33 should "wire `calculate_visibility()` into turn processing (before player phase)" — but the turn pipeline processes enemy phase, strategic orders, cavalry, occupation, morale recovery, supply, stability, war damage, bankruptcy, income, and disobedience reset. Visibility must be recalculated at a specific point.

**Pre-implementation fix needed:**
- `calculate_visibility()` should run at the START of `_advance_turn_internal()`, BEFORE all other processing
- `decay_intel()` should run immediately after `calculate_visibility()`
- This ensures the new turn starts with fresh visibility data
- Additionally: recalculate after each player action that affects visibility (scout, battle, move) — or just recalculate before reading intel

### MEDIUM Issues

**M1: Stale intel degradation granularity not specified for PARTIAL**

The spec (§2.2) defines decay for FULL intel: turns 0-2 = FULL, 3-4 = STALE, 5+ = LAST_KNOWN. But §3.3 step 5 says "Previously PARTIAL but no longer adjacent → starts aging from last_updated_turn." The decay timeline for PARTIAL-sourced intel is not explicitly defined.

**Design decision needed:**
- Should PARTIAL degrade directly to LAST_KNOWN (skipping STALE)?
- Or follow the same 2-turn-fresh → STALE → LAST_KNOWN timeline?
- **Recommendation:** PARTIAL degrades to STALE at turn 2 after losing adjacency, then LAST_KNOWN at turn 4. Same timeline but with less data to start with (no exact strength, morale, stance). This matches the user's refinement in Session 31c about gradual degradation.

**M2: Watchtower construction timer needs dedicated processing**

Existing `process_construction_timers()` iterates `region.buildings`. Watchtower is a separate field. Either:
- Extend `process_construction_timers()` to also check watchtower field
- Create `process_watchtower_construction()` as a separate timer
- **Recommendation:** Extend existing function — keeps construction processing in one place

**M3: Multiple enemies in same region — spec covers aggregate band but not individual names**

The spec (§2.1) says "Combined forces in the same region show aggregate band." The user's Session 31c refinement says "Multiple enemies show all names + combined band." This is clear for PARTIAL visibility, but at FULL: should individual strengths be shown, or just the aggregate? And at STALE: are individual names preserved from the last scouting?

**Recommendation:** At FULL: show individual details (current behavior). At PARTIAL: show all names + combined band. At STALE: show names from last scout + degraded combined band. At LAST_KNOWN: show names from last known + "last seen X turns ago." This matches the conversation design.

**M4: `get_game_state_summary()` returns `map_data` with per-region marshal lists**

The `map_data` dict includes marshal positions for rendering on the map. With fog, enemy marshals should only appear in `map_data` for regions with PARTIAL+ visibility. This is a subset of C1 but worth calling out separately because `map_data` is what Godot uses to draw marshal icons on the map.

**M5: Watchtower AI building priority needs insertion point**

The spec (§7.1) says "AI builds on border regions, priority below fortification but above market." Current AI admin priority chain is: recruit (P1) > market (P2) > depot (P3) > fortification (P4) > repair (P5). The spec places watchtower below fort but above market — this contradicts the current chain where market is P2 and fort is P4.

**Recommendation:** Insert watchtower at P3.5 (between depot and fort), or adjust to: recruit (P1) > market (P2) > depot (P3) > watchtower (P4) > fortification (P5) > repair (P6). The spec's intent is clear: watchtower is less important than economic buildings but provides strategic value.

**M6: Own region PARTIAL military intel — what exact data?**

The spec (§2.3) says own regions without friendly army get PARTIAL (name + band). But own regions always have FULL economic data. The `RegionIntel` class combines military and economic intel. Implementation must split the response: always return full economic data for own regions, but only return military data based on presence/adjacency rules.

### LOW Issues

**L1: `RegionIntel` class vs dict pattern**

The spec (§3.1) defines `RegionIntel` as a class with typed fields. The codebase patterns use dicts for most data (events, building data, etc.). Using a class is fine and cleaner for this case, but it must follow the serialization enforcement pattern (to_dict/from_dict).

**L2: Intel source tracking overlap**

`RegionIntel.intel_source` can be "scout", "adjacent", "battle", "own_territory", "watchtower". Multiple sources can apply simultaneously (e.g., own_territory + adjacent). The field should either be a list of sources or just store the "best" source.

**Recommendation:** Store only the highest-priority source. Priority: own_territory > scout > battle > watchtower > adjacent. This simplifies serialization and display.

**L3: Backward compatibility for old saves**

The spec (§3.4) correctly notes old saves should default to UNKNOWN. However, the first time a save is loaded after fog is implemented, ALL regions will be UNKNOWN — including the player's own regions. The `calculate_visibility()` function must run immediately after loading a save to populate correct visibility.

**L4: Event log types not in existing event type list**

The spec (§10) adds 3 new event types: `intel_updated`, `intel_decayed`, `target_not_found`. These need to be documented alongside the existing 13 event types in STATUS.md and SYSTEMS_REFERENCE.md.

---

## Part 2: Implementation Plan

### Session 33: Intel Data Layer + Visibility Core (Sonnet)

**Goal:** RegionIntel model, intel store on WorldState, visibility calculation, decay, serialization.

**Pre-work (spec fixes from Part 1):**
- [ ] Address C1: Design `get_filtered_game_state_summary()` approach (parameter vs wrapper)
- [ ] Address C2: Confirm scout persistence is part of this session
- [ ] Address H5: Document exact insertion point for `calculate_visibility()` in turn pipeline

**Implementation:**
- [ ] Create `backend/models/intel.py` — `RegionIntel` class
  - Fields: region_name, visibility, known_marshals, strength_band, exact_strength, morale, stance, economic_intel, last_scouted_turn, last_updated_turn, intel_source
  - `to_dict()` / `from_dict()` with full serialization
  - `get_strength_band(strength)` static helper
  - Visibility constants: FULL, PARTIAL, STALE, LAST_KNOWN, UNKNOWN
- [ ] Add `intel: dict` to `WorldState.__init__()` (empty dict default)
  - Backward compat: missing field = empty dict
  - Add to `to_dict()` / `from_dict()`
- [ ] Implement `calculate_visibility(world)` — runs each turn
  - Step 1: Own regions → FULL economic, military based on army presence
  - Step 2: Adjacent to friendly army → PARTIAL
  - Step 3: Adjacent to watchtower → PARTIAL (placeholder, watchtower comes later)
  - Step 4: Check intel age → FULL/STALE/LAST_KNOWN
  - Step 5: Previously PARTIAL no longer adjacent → age from last_updated_turn
  - Step 6: Best visibility wins when multiple sources apply
- [ ] Implement `get_region_intel(region_name)` — returns current intel for a region
- [ ] Implement `update_intel_from_scout(region_name, turn)` — scout sets FULL
- [ ] Implement `update_intel_from_battle(region_name, turn)` — battle sets FULL
- [ ] Implement `decay_intel()` — called each turn, degrades old intel
- [ ] Implement strength band calculation (5 bands from spec §2.1)
- [ ] Wire `calculate_visibility()` into `_advance_turn_internal()` (FIRST thing, before all other processing)
- [ ] Wire `decay_intel()` immediately after `calculate_visibility()`
- [ ] Wire `calculate_visibility()` to run after save load (backward compat, L3)
- [ ] Serialization enforcement tests for RegionIntel and WorldState.intel
- [ ] Unit tests: visibility calculation, decay timeline, strength bands, own region rules, serialization roundtrip

**Tests expected:** ~40-50
**Complexity:** Sonnet
**Smoke test gate:** `pytest tests/ -v --tb=no -q` green, test count = 2036 + new tests

### Session 34: Command Integration + Status Filtering (Sonnet)

**Goal:** Status command filtered, scout persists intel, battle reveals, PURSUE validation, enemy phase filtering.

**Implementation:**
- [ ] Wire scout action → `update_intel_from_scout()` in `_execute_scout()` (C2 fix)
  - Targeted scout: update intel for target region
  - Adjacent scout: update intel for all scouted regions
- [ ] Wire battle resolution → `update_intel_from_battle()` in `_log_battle_event()` or alongside it
  - All 6 resolve_battle paths: 5 in executor + 1 auto-charge in world_state
- [ ] Filter status command output by visibility (§4.1 — Berthier's Intelligence Report)
  - Group enemies by visibility tier
  - Show exact data for FULL, band for PARTIAL/STALE, "last seen" for LAST_KNOWN, nothing for UNKNOWN
- [ ] Filter enemy phase display by visibility (§4.2) — moved from Session 34 per C3
  - Actions in FULL regions: show full display
  - Actions in other regions: suppress
  - Exception: arrival into visible region shows "appears at [region]"
- [ ] Filter `get_game_state_summary()` by visibility (C1 fix)
  - Enemy marshals only appear in map_data for PARTIAL+ regions
  - Strength data filtered based on visibility tier
  - Own region economic data always full
- [ ] PURSUE validation: require known/stale target location (§5.2)
  - Check `intel` for target marshal's last known location
  - If UNKNOWN: reject with message
  - If STALE/LAST_KNOWN: allow but use last known position
- [ ] PURSUE empty-arrival interrupt: "target not found" when arriving at stale location (§5.2)
  - Check if target is actually in the destination region
  - If not: generate interrupt event, clear strategic order
- [ ] SUPPORT validation: confirm friendly target always visible (§5.3 — no change needed, just verify)
- [ ] Filter tactical events by visibility (end-turn tactical events sent to Godot)
- [ ] Event log: `intel_updated`, `intel_decayed`, `target_not_found` event types (§10)
- [ ] Unit tests: filtered status, PURSUE into fog, scout persistence, battle reveals, enemy phase filtering, response filtering

**Tests expected:** ~35-45
**Complexity:** Sonnet
**Smoke test gate:** `pytest tests/ -v --tb=no -q` green, curl test `/command` endpoint to verify filtered responses

### Session 35: Watchtower Building (Sonnet)

**Goal:** Watchtower as dedicated building, construction, visibility effect, scout synergy, AI building, repair.

**Implementation:**
- [ ] Add `watchtower` and `watchtower_turns_remaining` fields to Region model (§7.2)
  - `watchtower: str` — "none", "under_construction", "active", "damaged"
  - `watchtower_turns_remaining: int` — countdown during construction/repair
  - Add to `to_dict()` / `from_dict()` with backward compat defaults
- [ ] Add "watchtower" keyword to `_extract_building_type()` in executor.py (H1 fix)
- [ ] Add watchtower build handler in `_execute_build()` — branch based on building type
  - Cost: 250 gold, 2 turns construction
  - No slot required (dedicated field)
  - Validation: region already has watchtower check, gold check, region control check
  - Does NOT check building slots
- [ ] Extend `process_construction_timers()` to handle watchtower countdown (M2)
  - When timer completes: watchtower → "active"
- [ ] Wire watchtower into `calculate_visibility()` — active watchtower provides PARTIAL on adjacent
- [ ] Watchtower scout synergy: scouting watchtower-visible region → 3 turns FULL instead of 2 (§7.4)
- [ ] Battle damage: watchtower damaged same as civilian buildings (§7.1)
- [ ] Plunder destroys watchtower, secure damages it
- [ ] Extend `_execute_repair()` to handle watchtower repair (H2 fix)
  - Same cost as building repair: 1 admin AP + 150 gold
  - Damaged → triggers repair timer → active
- [ ] AI watchtower building logic (§7.1, M5)
  - Add to `_pick_admin_action()` priority chain
  - `_find_best_watchtower_region()`: own border regions without watchtower
  - Priority: below depot, above fortification
- [ ] Add `watchtower` to ADMIN_ACTIONS set if needed (or keep under "build")
- [ ] Update mock parser to handle "watchtower" keyword
- [ ] Serialization enforcement tests
- [ ] Unit tests: watchtower construction, visibility effect, scout synergy, damage/repair, AI building, serialization

**Tests expected:** ~30-35
**Complexity:** Sonnet
**Smoke test gate:** `pytest tests/ -v --tb=no -q` green

### Session 36: Polish + Smoke Test + Edge Cases (Sonnet)

**Goal:** Edge cases, Godot smoke test, Davout PURSUE fix, V2b TODO markers, doc updates.

**Implementation:**
- [ ] Edge cases:
  - Broken marshal in fog (retreating/broken marshal position should be known to player — it's your marshal)
  - Retreat into fog (forced retreat sends your marshal into unknown region — reveal on arrival)
  - Auto-charge in fog (auto-charge happens at turn start, target may have moved since last scout)
  - Own-region behind enemy lines: PARTIAL military (§2.3 special case)
  - Multiple enemies in same region: combined band calculation (M3)
  - Occupied own region: standard PARTIAL per spec §2.3 edge case
- [ ] Davout PURSUE objection update (§6.3, existing TODO at `disobedience.py:1609`)
  - If target FULL visibility: object as now (sees odds)
  - If target PARTIAL: object based on strength band comparison
  - If target STALE/LAST_KNOWN/UNKNOWN: cannot object on odds, may object on staleness
- [ ] Add V2b TODO markers at fog-aware objection wiring points (§6.1)
  - `objection_v2.py`: comment block at each helper noting fog integration needed for V2b
  - `disobedience.py`: update existing TODO at line 1609
  - Add `get_visible_enemies_near()` helper (H4 recommendation) — returns actual data now, fog-filtered in V2b
- [ ] Smoke test: play through 5+ turns in Godot
  - Verify status command shows filtered intel
  - Verify enemy phase shows only visible actions
  - Verify scout reveals FULL intel
  - Verify intel decays over turns
  - Verify watchtower provides adjacency visibility
  - Verify PURSUE into fog chase mechanics
- [ ] Update test_serialization_enforcement.py fixture if needed
- [ ] Integration tests: full turn cycle with fog, multi-turn decay, scout→stale→last_known

**Tests expected:** ~15-25
**Complexity:** Sonnet
**Smoke test gate:** Full Godot smoke test + `pytest tests/ -v --tb=no -q` green

### Code Review Gate (Opus)

**After Session 36, before moving to Manpower Pools / Artillery.**

Fog touches many systems — review integration points:
- [ ] Verify all 12+ API endpoints properly filtered
- [ ] Verify no enemy data leaks in tactical events, strategic reports, or turn results
- [ ] Verify AI is completely unaffected by fog (omniscient, no filtered data paths)
- [ ] Verify serialization roundtrip for all new fields
- [ ] Verify backward compat with old saves
- [ ] Verify combat.py still accesses zero world state (confirmed safe in Session 32 audit)
- [ ] Check for float values in any fog-related data sent to Godot
- [ ] Review V2b TODO markers for completeness

---

## Part 3: File Modification Reference

### New Files

| File | Session | Purpose |
|------|---------|---------|
| `backend/models/intel.py` | 33 | RegionIntel class, visibility constants, strength bands |
| `tests/test_fog_of_war.py` | 33-34 | Intel model, visibility, decay, filtering tests |
| `tests/test_watchtower.py` | 35 | Watchtower building, visibility, AI tests |

### Modified Files

| File | Session | Changes |
|------|---------|---------|
| `backend/models/world_state.py` | 33 | intel dict, calculate_visibility(), decay_intel(), get_region_intel() |
| `backend/models/region.py` | 35 | watchtower, watchtower_turns_remaining fields |
| `backend/commands/executor.py` | 34-35 | scout→intel update, battle→intel update, _extract_building_type watchtower, _execute_build watchtower branch, _execute_repair watchtower |
| `backend/commands/strategic.py` | 34 | PURSUE validation against visibility, target_not_found interrupt |
| `backend/commands/disobedience.py` | 36 | Davout PURSUE fog-aware check |
| `backend/commands/objection_v2.py` | 36 | V2b TODO markers, get_visible_enemies_near() helper |
| `backend/game_logic/turn_manager.py` | 33 | Call calculate_visibility() + decay_intel() in turn pipeline |
| `backend/main.py` | 34 | Filter API responses by visibility, enemy phase filtering |
| `backend/ai/enemy_ai.py` | 35 | Watchtower building logic |
| `backend/ai/llm_client.py` | 35 | "watchtower" keyword in mock parser |
| `backend/save_manager.py` | 33 | Automatic via WorldState.to_dict (no explicit changes needed) |

### Docs Updated

| Doc | Session | Changes |
|-----|---------|---------|
| `CLAUDE.md` | 36 | Current Phase updated, fog of war in required reading |
| `STATUS.md` | 33-36 | Session entries, test counts |
| `ROADMAP.md` | 36 | Fog of War marked COMPLETE |
| `SYSTEMS_REFERENCE.md` | 36 | New fog of war section |
| `TUTORIAL_SCRIPT.md` | 36 | Fog of war teaching moments |
| `FUTURE_DESIGN.md` | 32 (this session) | Fog sketches → "implemented, see spec", AI fog notes for 80+ |
| `SAVE_FORMAT_REFERENCE.md` | 33, 35 | RegionIntel, watchtower field serialization format |
| `OBJECTION_V2.md` | 32 (this session) | V2b fog-of-war triggers noted |
| `ADDING_CONTENT.md` | 35 | Watchtower building type |

---

## Part 4: Test Estimates

| Category | Session | Count |
|----------|---------|-------|
| Intel model + serialization | 33 | ~10 |
| Visibility calculation | 33 | ~15 |
| Intel decay | 33 | ~10 |
| Strength bands | 33 | ~5 |
| Own region rules | 33 | ~5 |
| Status filtering | 34 | ~10 |
| Scout persistence | 34 | ~5 |
| Battle reveals | 34 | ~5 |
| PURSUE fog | 34 | ~10 |
| Response filtering (API, enemy phase, tactical events) | 34 | ~10 |
| Event log (intel_updated, intel_decayed, target_not_found) | 34 | ~5 |
| Watchtower construction | 35 | ~8 |
| Watchtower visibility + scout synergy | 35 | ~8 |
| Watchtower damage/repair | 35 | ~5 |
| Watchtower AI building | 35 | ~5 |
| Watchtower serialization | 35 | ~4 |
| Edge cases (broken, retreat, auto-charge, own region) | 36 | ~10 |
| Davout PURSUE fog check | 36 | ~3 |
| Integration (full turn cycle) | 36 | ~5 |
| **Total estimated** | | **~138-155** |

**Final test count estimate:** 2036 (current) + ~138-155 = **~2174-2191**

---

## Part 5: Dependencies and Risk

### Dependencies

| Dependency | Status | Impact if Missing |
|------------|--------|-------------------|
| Event log system (Session 30) | COMPLETE | New event types build on existing infrastructure |
| Save/Load (Session 27) | COMPLETE | Serialization patterns established |
| Building system (6.2.E) | COMPLETE | Watchtower follows building patterns |
| Scout action (Phase 2) | COMPLETE | Scout persistence builds on existing action |
| Strategic commands (5.2) | COMPLETE | PURSUE fog validation extends existing logic |
| Objection V2a (complete) | COMPLETE | V2b fog triggers documented, not implemented |

### Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| 12+ endpoint filtering scope | HIGH | Single filtering function called from one point, not 12 |
| Existing test breakage from filtered responses | MEDIUM | Tests that check `get_game_state_summary()` need updating |
| AI accidentally reading filtered data | LOW | AI confirmed omniscient, uses `world.marshals` directly |
| Performance of per-turn visibility calculation | LOW | 13 regions × 7 marshals = trivial. Revisit at 80+ regions. |
| Watchtower field pattern diverges from building list | MEDIUM | Documented in implementation plan, repair/damage handlers noted |

---

## Part 6: Session Breakdown Summary

| Session | Scope | Complexity | Tests | Cumulative |
|---------|-------|------------|-------|------------|
| 33 | Intel model + visibility + serialization | Sonnet | ~45 | ~2081 |
| 34 | Command filtering + status + PURSUE + enemy phase | Sonnet | ~45 | ~2126 |
| 35 | Watchtower building + AI + repair | Sonnet | ~30 | ~2156 |
| 36 | Edge cases + smoke test + Davout fix + V2b markers | Sonnet | ~20 | ~2176 |
| Review | Opus code review gate | Opus | 0 | ~2176 |

All sessions are Sonnet-level except the code review gate (Opus).
