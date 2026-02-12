# Fog of War Implementation Plan

> **Session 32 Deliverable — Architectural review + implementation roadmap**
> **Spec:** `docs/FOG_OF_WAR_SPEC.md` (16 sections)
> **Created:** February 11, 2026
> **Author:** Claude (Opus), Session 32
> **Reviewed:** Session 32b (Opus) — fresh-eyes review, 6 design decisions resolved, session 34 split into 34A/34B
> **Updated:** Session 32c — 5 implementation issues resolved: marshal-present visibility (H6), calculate_visibility() timing (H5 revised), PARTIAL decay timeline (M1), refresh vs decay path separation, stale snapshot semantics

---

## Part 1: Spec Review — Issues Found

Issues categorized by severity. **CRITICAL** = blocks implementation or causes crashes. **HIGH** = will cause bugs if not addressed. **MEDIUM** = design gap needing a decision. **LOW** = minor polish.

### CRITICAL Issues

**C1: `get_game_state_summary()` exposes ALL enemy data — 23 call sites across 8 endpoints** ✅ RESOLVED

The spec correctly identifies that API responses need filtering (§4, §11.1), but underestimates the scope. `world_state.py:get_game_state_summary()` builds `map_data` with ALL marshals visible and an `"enemies"` dict that exposes every enemy marshal's location, strength, morale, and stance. Session 32b code exploration confirmed **23 call sites across 8 endpoints** (not "12+" as originally estimated).

**Resolution:** Create `get_filtered_game_state_summary()` wrapper on WorldState. Single filtering function replaces all 23 call sites. Assigned to Session 34A.

**C2: Scout action does NOT persist intel to WorldState** ✅ SPEC UPDATED

The spec (§4.3) said "No changes to scout mechanics needed." This is incorrect. `executor.py:_execute_scout()` currently returns intel in the `events` dict but does NOT write anything to the world state. Scout reveals are ephemeral — they exist only in the API response for that command. The fog system requires scout results to persist as FULL visibility in the `intel` store.

**Resolution:** Spec §4.3 updated to clarify scout persistence. Only targeted region gets FULL; intermediate regions unaffected. Assigned to Session 34A.

**C3: Enemy phase display reveals ALL enemy actions** ✅ RESOLVED

`main.py` lines 441-468 cleans up the enemy phase result but sends ALL enemy actions/targets to Godot. The spec (§4.2) acknowledges this but the original plan placed it too late.

**Resolution:** Enemy phase filtering assigned to Session 34B. Status filtering is in 34A. The split means 34A may have status filtered but enemy phase not — acceptable for 1 session gap since 34B follows immediately.

### HIGH Issues

**H1: Watchtower NOT in `_extract_building_type()` keywords or `BUILDING_TYPES`** ✅ RESOLVED

The spec (§7.2) proposes watchtower as a dedicated field on Region, separate from the building slot system. However, `executor.py:_extract_building_type()` uses keyword matching to parse "build watchtower in Paris" — the keyword "watchtower" is not in the keyword list. `BUILDING_TYPES` in `region.py` also doesn't include watchtower.

**Resolution:** Option A — add "watchtower" keyword to `_extract_building_type()`, branch to dedicated handler in `_execute_build()`. Watchtower bypasses slot system and `allowed_in` checks. Assigned to Session 35.

**H2: Watchtower field design conflicts with existing building patterns** ✅ RESOLVED

The spec proposes `watchtower: str` with states "none"/"under_construction"/"active"/"damaged" plus `watchtower_turns_remaining: int`. This is a different pattern from existing buildings (list of dicts with `type`, `status`, `turns_remaining`). The repair command (`_execute_repair()`) specifically iterates the `buildings` list to find damaged buildings.

**Resolution:** Watchtower as dedicated field is the correct design (not a slot building). All 4 integration points documented in Session 35 checklist: `_execute_repair()`, `_execute_build()`, `process_construction_timers()`, battle damage logic.

**H3: PURSUE/SUPPORT in `strategic.py` have 5+ direct enemy location accesses** ✅ RESOLVED

`strategic.py:_execute_pursue()` calls `world.get_marshal(order.target)` and reads `target.location` directly — bypassing fog. `_execute_support()` does the same for ally marshals (correct for SUPPORT, but the same pattern is used for target validation).

**Resolution:** PURSUE reads target location from intel store (not raw marshal data). Empty-arrival simplified: no new interrupt type needed — if no enemies adjacent, order auto-cancels with report message; if enemies adjacent, existing personality contact vectors handle the encounter. SUPPORT safety check also fog-aware. All assigned to Session 34B.

**H4: Objection system has 8+ fog-unaware enemy data access points** ✅ DEFERRED TO V2b (Phase 7)

`objection_v2.py` helper functions directly access enemy data without fog filtering:
- `_check_enemy_adjacent()` — sees all enemies regardless of fog
- `_get_friendly_to_enemy_ratio()` — exact enemy strength
- `_get_enemy_to_friendly_ratio()` — exact enemy strength
- `_is_outnumbered_2to1()` — exact comparison
- `_path_crosses_enemy()` — sees all enemy positions
- `_check_attack_target_fortified()` — sees enemy fort status
- `_get_attack_odds_ratio()` — exact odds calculation

**Resolution:** Full fog-aware objection logic is V2b scope (Phase 7). For Phase 6, Session 36 adds: (1) `get_visible_enemies_near()` helper that returns actual data now but can be switched to fog-filtered in V2b, (2) TODO markers at all 12 helper functions, (3) Davout PURSUE fog-aware objection as first concrete fog+objection integration.

**H5: `calculate_visibility()` execution timing not specified in turn pipeline** ✅ RESOLVED (Session 32c)

The spec (§3.3) says "each turn, before player actions, recalculate visibility." The actual turn pipeline in `world_state.py:_advance_turn_internal()` has many phases.

**Resolution (updated Session 32c):** `calculate_visibility()` + `decay_intel()` run at the END of `_advance_turn_internal()`, AFTER all processing (tactical states, construction, turn increment, stability, supply, bankruptcy, income). This ensures broken marshal retreats, auto-charges, and strategic movements are all resolved before visibility recalculates. The player sees a clean, accurate picture at the start of their next action phase. Also runs at game init (end of `__init__`) and after save load. Assigned to Session 33.

**H6: Marshal-present visibility not in calculate_visibility() steps** ✅ RESOLVED (Session 32c)

The original `calculate_visibility()` steps only handled "own regions" (Step 1) and "adjacent to friendly army" (Step 2). Neither covered enemy-controlled regions where a friendly marshal is physically present. Example: Grouchy starts in Waterloo (British territory) alongside Wellington and Uxbridge — he can see them, but no rule granted FULL visibility there.

**Resolution:** New Step 0 added to `calculate_visibility()`: "Any region containing a friendly marshal → FULL military intel." Runs before own-region and adjacency checks. Priority order is now: marshal-present (Step 0) → own region (Step 1) → adjacent to army (Step 2) → watchtower (Step 3) → decay (Step 4-5) → best-wins (Step 6).

### MEDIUM Issues

**M1: Stale intel degradation granularity not specified for PARTIAL** ✅ RESOLVED (Session 32c)

The spec (§2.2) defines decay for FULL intel: turns 0-2 = FULL, 3-4 = STALE, 5+ = LAST_KNOWN. But §3.3 step 5 says "Previously PARTIAL but no longer adjacent → starts aging from last_updated_turn." The decay timeline for PARTIAL-sourced intel was not explicitly defined.

**Resolution:** Same decay timeline for both FULL and PARTIAL, offset from `last_updated_turn`. PARTIAL was less detailed (bands not exact numbers), but the freshness of the observation is the same — a cavalry screen saw them yesterday whether they counted heads or not. Making PARTIAL decay faster adds complexity for minimal gameplay value. Same clock: 2 turns fresh → STALE at 3-4 → LAST_KNOWN at 5+.

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

> **Session 32 = spec design. Session 32b = fresh-eyes review. Implementation = Sessions 33-36 (34 split into 34A/34B).**

### Session 33: Intel Data Layer + Visibility Core (Sonnet)

**Goal:** RegionIntel model, intel store on WorldState, visibility calculation, decay, serialization. After this session, the data layer exists but nothing reads it yet — the game is functionally unchanged.

**Key design decisions (confirmed Session 32c):**
- **Marshal-present → FULL:** Any region with a friendly marshal gets FULL military intel, regardless of controller (Grouchy in Waterloo sees Wellington)
- **Placement:** `calculate_visibility()` + `decay_intel()` run at END of `_advance_turn_internal()`, after ALL processing (tactical states, broken retreats, auto-charges, income, etc.). Player sees clean picture at start of next action phase.
- **PARTIAL decay:** Same timeline as FULL, offset from `last_updated_turn`. 2 turns fresh → STALE at 3-4 → LAST_KNOWN at 5+.
- **Refresh vs decay separation:** Refresh path (FULL/PARTIAL) queries `world.get_marshals_in_region()` for live data, updates `known_marshals`, resets `last_updated_turn`. Decay path (STALE/LAST_KNOWN) does NOT query live data — keeps snapshot frozen, only changes visibility level and strength band precision.
- **Stale snapshots are intentionally wrong:** When enemies leave a scouted region, STALE/LAST_KNOWN intel still shows them there. `known_marshals` and `strength_band` stay frozen from last refresh. Player must re-scout or move through to discover the region is empty.

**Implementation: ✅ COMPLETE (Session 33, Feb 12 2026)**
- [x] Create `backend/models/intel.py` — `RegionIntel` class
- [x] Add `intel: dict` to `WorldState.__init__()` with to_dict/from_dict
- [x] Implement `calculate_visibility()` (Steps 0-3: marshal-present → own region → adjacent → watchtower placeholder)
- [x] Implement `get_region_intel()`, `update_intel_from_scout()`, `update_intel_from_battle()`
- [x] Implement `decay_intel()` with refresh/decay path separation
- [x] Implement strength band calculation (6 bands)
- [x] Game init: `calculate_visibility()` at end of `__init__()`
- [x] Wire at END of `_advance_turn_internal()` after all processing
- [x] Wire after save load in `save_manager.py`
- [x] Serialization enforcement tests
- [x] 55 unit tests: visibility calculation, decay timeline, strength bands, own region rules, marshal-present rules, game init visibility, refresh vs decay path separation, stale snapshot persistence, serialization roundtrip, multi-turn integration

**Tests:** 55 new (2091 total passing, 3 skipped)
**Smoke test gate:** ✅ PASSED

---

### Session 34A: Intel Report + Filtering Infrastructure (Sonnet)

**Goal:** Berthier Intelligence Report, filtered game state summary, scout persistence, battle reveal wiring. After this session, the status command shows fog-filtered intel and scout/battle results persist.

**Ordering dependency:** `get_filtered_game_state_summary()` FIRST — everything else depends on it.

**Implementation:**
- [ ] Create `backend/intel_report.py` — Berthier Intelligence Report module
  - `generate_intel_report(world)` → structured report grouped by visibility tier
  - Sections: YOUR FORCES, CONFIRMED (FULL), RECENT REPORTS (PARTIAL/STALE), LAST KNOWN, NO INTELLIGENCE (UNKNOWN)
  - Show exact data for FULL, strength band for PARTIAL/STALE, "last seen X turns ago" for LAST_KNOWN, region name only for UNKNOWN
  - Reusable by Campaign Briefing (Phase 6.5)
- [ ] Create `get_filtered_game_state_summary()` on WorldState (C1 fix)
  - Wrapper that calls `get_game_state_summary()` then filters by visibility
  - Enemy marshals only appear in `map_data` for PARTIAL+ regions
  - `enemies` dict: only PARTIAL+ visible enemies with appropriate data (exact for FULL, band for PARTIAL/STALE)
  - Own region economic data always full regardless of military visibility
  - Replace all 23 call sites across 8 endpoints with filtered version
- [ ] Wire status command to `intel_report.py`
  - "status" is a free_action in `executor.py:732` — no `_execute_status()` exists
  - Route status action to call `generate_intel_report()` and return result
  - Update `/status` GET endpoint in `main.py:514` to use filtered report
- [ ] Wire scout action → `update_intel_from_scout()` in `_execute_scout()` (C2 fix)
  - Targeted scout: update intel for target region → FULL
  - Adjacent scan: adjacent regions get PARTIAL (not FULL)
  - Davout +1 range: only target gets FULL, intermediates untouched
- [ ] Wire battle resolution → `update_intel_from_battle()` at all 6 resolve_battle sites
  - `executor.py`: 5 sites (main attack:2529, general attack:4601, sally 2:4749, sally 3:4882, glorious charge:7169)
  - `world_state.py`: 1 site (auto-charge in `_process_reckless_cavalry_turn_start()`)
  - All battles grant FULL on the battle region
- [ ] Unit tests: intel report format, filtered game state, scout persistence, battle reveals, status command output

**Tests expected:** ~30
**Smoke test gate:** `pytest tests/ -v --tb=no -q` green, curl test `/status` and `/command` to verify filtered responses

---

### Session 34B: Strategic Commands + Display Filtering (Sonnet)

**Goal:** PURSUE fog validation, SUPPORT visibility, cautious pathfinding fog-awareness, enemy phase filtering, tactical/strategic report filtering. After this session, fog is fully functional — all API responses respect visibility.

**Implementation:**
- [ ] PURSUE validation: read target location from intel store, not raw marshal data (§5.2)
  - `world.get_marshal(target).location` → `intel.get_last_known_location(target)`
  - If UNKNOWN: reject with "No intelligence on [target]'s position"
  - If STALE/LAST_KNOWN: allow, use last known position for pathfinding
- [ ] PURSUE empty-arrival: detect target not at destination (§5.2)
  - Marshal arrives → target not in region → check adjacent via PARTIAL
  - No enemies adjacent: order auto-cancels, message "[Marshal] arrives at [region] but finds no sign of [target]. Awaiting orders, Sire."
  - Enemies adjacent: existing personality contact vectors handle encounter (no new interrupt type needed)
- [ ] SUPPORT safety check: fog-aware (spec §5.3 note)
  - `_execute_support()` adjacent enemy scan only sees PARTIAL+ visible enemies
- [ ] Cautious pathfinding: fog-aware (spec §9.3)
  - `_get_enemy_occupied_regions()` filters by PARTIAL+ visibility from intel store
  - Cautious marshals only avoid enemies they can see
- [ ] HOLD sally logic: fog-aware
  - Sally only targets enemies visible at PARTIAL+ in adjacent regions
- [ ] Filter enemy phase display by visibility (§4.2) in `main.py`
  - Actions in FULL regions: show full display
  - Actions in PARTIAL regions: show vague "movement reported near [region]"
  - Actions in STALE/LAST_KNOWN/UNKNOWN: suppress
  - Exception: arrival into visible region shows "[forces] appear at [region]"
- [ ] Filter tactical events by visibility (end-turn events sent to Godot)
  - Only show events in regions with PARTIAL+ visibility
  - Supply attrition for enemy nations: suppress if region not visible
- [ ] Filter strategic reports by visibility
  - Reports about events in fogged regions: suppress or redact
- [ ] Event log: `intel_updated`, `intel_decayed` event types (§10)
  - `target_not_found` becomes an order completion message, not a separate event type
- [ ] Unit tests: PURSUE into fog, PURSUE empty arrival (both cases), SUPPORT fog, cautious pathfinding, enemy phase filtering, tactical event filtering, strategic report filtering

**Tests expected:** ~25
**Smoke test gate:** `pytest tests/ -v --tb=no -q` green, curl test end-turn flow to verify all filtering

---

### Session 35: Watchtower Building (Sonnet)

**Goal:** Watchtower as dedicated building, construction, visibility effect, scout synergy, AI building, repair.

**Implementation:**
- [ ] Add `watchtower` and `watchtower_turns_remaining` fields to Region model (§7.2)
  - `watchtower: str` — "none", "under_construction", "active", "damaged"
  - `watchtower_turns_remaining: int` — countdown during construction/repair
  - Add to `to_dict()` / `from_dict()` with backward compat defaults ("none", 0)
- [ ] Add "watchtower" keyword to `_extract_building_type()` in executor.py (H1 fix)
- [ ] Add watchtower build handler in `_execute_build()` — branch based on building type
  - Cost: 250 gold, 2 turns construction
  - No slot required (dedicated field) — bypass slot check AND `allowed_in` check
  - Buildable in ALL region types (rural, town, city, major_city, capital)
  - Validation: region already has watchtower check, gold check, region control check, not already constructing
- [ ] Extend `process_construction_timers()` on **WorldState** (not Region — it's at `world_state.py:1562`)
  - Add watchtower countdown alongside building countdown
  - When timer completes: watchtower → "active"
- [ ] Wire watchtower into `calculate_visibility()` — active watchtower in own region provides PARTIAL on adjacent
  - Only player-owned watchtowers affect fog (AI is omniscient, doesn't need them for visibility)
- [ ] Watchtower scout synergy: scouting watchtower-visible region → FULL expires turn 3 instead of turn 2 (§7.4)
- [ ] Battle damage: active watchtower → "damaged" (same as civilian buildings)
  - Under construction + battle → "none" (destroyed, consistent with `building_under_construction = None`)
- [ ] Plunder destroys watchtower ("none"), secure damages it ("damaged")
- [ ] Extend `_execute_repair()` to handle watchtower repair (H2 fix)
  - Same cost as building repair: 1 admin AP + 150 gold
  - Damaged → under_construction (repair timer) → active
- [ ] AI watchtower building logic (§7.1, M5)
  - Add to `_pick_admin_action()` between depot (P3) and fortification (P4)
  - `_find_best_watchtower_region()`: own border regions without watchtower
  - Score by: border adjacency (heavy bonus) + income value
- [ ] Update mock parser to handle "watchtower" keyword in `llm_client.py`
- [ ] Serialization enforcement tests
- [ ] Unit tests: watchtower construction, visibility effect, scout synergy, damage/repair, AI building, serialization

**Tests expected:** ~30
**Smoke test gate:** `pytest tests/ -v --tb=no -q` green

---

### Session 36: Polish + Smoke Test + Edge Cases (Sonnet)

**Goal:** Edge cases, Godot smoke test, Davout PURSUE fix, V2b TODO markers, doc updates.

**Implementation:**
- [ ] Edge cases:
  - Broken marshal in fog (position always known — it's your marshal)
  - Retreat into fog (forced retreat sends your marshal into unknown region — FULL on arrival)
  - Own-region behind enemy lines: PARTIAL military (§2.3 special case)
  - Multiple enemies in same region: combined band calculation at PARTIAL/STALE
  - Occupied own region: standard PARTIAL per spec §2.3 edge case
  - ~~Auto-charge in fog~~ **No changes needed** — auto-charge ignores fog per spec §9.2 decision
- [ ] Davout PURSUE objection update (§6.3, existing TODO at `disobedience.py:1609`)
  - If target FULL visibility: object as now (sees odds)
  - If target PARTIAL: object based on strength band comparison
  - If target STALE/LAST_KNOWN/UNKNOWN: cannot object on odds, may object on staleness
- [ ] Add V2b TODO markers at fog-aware objection wiring points (§6.1)
  - `objection_v2.py`: comment block at each of the 12 helper functions noting fog integration needed for V2b
  - `disobedience.py`: update existing TODO at line 1609
  - Add `get_visible_enemies_near()` helper — returns actual data now, fog-filtered in V2b
- [ ] Smoke test: play through 5+ turns in Godot
  - Verify status command shows Berthier Intelligence Report format
  - Verify enemy phase shows only visible actions
  - Verify scout reveals FULL intel that persists across turns
  - Verify intel decays over turns (FULL → STALE → LAST_KNOWN)
  - Verify watchtower provides adjacency visibility
  - Verify PURSUE uses last-known intel, handles empty arrival
  - Verify cautious pathfinding only avoids visible enemies
  - Verify reckless cavalry auto-charge works unchanged
- [ ] Update test_serialization_enforcement.py fixture if needed
- [ ] Integration tests: full turn cycle with fog, multi-turn decay, scout→stale→last_known
- [ ] Doc updates:
  - SYSTEMS_REFERENCE.md: new fog of war section
  - TUTORIAL_SCRIPT.md: fog of war teaching moments
  - FUTURE_DESIGN.md: fog sketches → "implemented, see spec", AI fog notes
  - SAVE_FORMAT_REFERENCE.md: RegionIntel + watchtower fields
  - ROADMAP.md: mark Fog of War COMPLETE
  - CLAUDE.md: update current phase

**Tests expected:** ~20
**Smoke test gate:** Full Godot smoke test + `pytest tests/ -v --tb=no -q` green

---

### Code Review Gate (Opus)

**After Session 36, before moving to Manpower Pools / Artillery.**

Fog touches many systems — review integration points:
- [ ] Verify all 23 call sites across 8 endpoints use `get_filtered_game_state_summary()`
- [ ] Verify no enemy data leaks in tactical events, strategic reports, or turn results
- [ ] Verify AI is completely unaffected by fog (omniscient, reads `world.marshals` directly)
- [ ] Verify reckless cavalry auto-charge works unchanged (no fog filtering)
- [ ] Verify serialization roundtrip for all new fields (RegionIntel, watchtower)
- [ ] Verify backward compat with old saves (empty intel → calculate_visibility on load)
- [ ] Verify combat.py still accesses zero world state (confirmed safe in Session 32 audit)
- [ ] Check for float values in any fog-related data sent to Godot
- [ ] Review V2b TODO markers at all 12 objection helper functions
- [ ] Verify intel_report.py produces correct tiered output
- [ ] Verify refresh vs decay path separation — no `get_marshals_in_region()` calls in decay path, no snapshot freezing in refresh path

---

## Part 3: File Modification Reference

### New Files

| File | Session | Purpose |
|------|---------|---------|
| `backend/models/intel.py` | 33 | RegionIntel class, visibility constants, strength bands |
| `backend/intel_report.py` | 34A | Berthier Intelligence Report (fog-filtered status view) |
| `tests/test_fog_of_war.py` | 33-34B | Intel model, visibility, decay, filtering tests |
| `tests/test_intel_report.py` | 34A | Intel report format, tiered display tests |
| `tests/test_watchtower.py` | 35 | Watchtower building, visibility, AI tests |

### Modified Files

| File | Session | Changes |
|------|---------|---------|
| `backend/models/world_state.py` | 33, 34A | intel dict, calculate_visibility() + decay_intel() at END of `_advance_turn_internal()`, get_region_intel(), get_filtered_game_state_summary() |
| `backend/models/region.py` | 35 | watchtower, watchtower_turns_remaining fields |
| `backend/commands/executor.py` | 34A, 35 | scout→intel update, battle→intel update (6 sites), status→intel_report, _extract_building_type watchtower, _execute_build watchtower branch, _execute_repair watchtower |
| `backend/commands/strategic.py` | 34B | PURSUE reads intel store, empty-arrival handling, cautious pathfinding fog-aware, SUPPORT safety fog-aware, HOLD sally fog-aware |
| `backend/commands/disobedience.py` | 36 | Davout PURSUE fog-aware check |
| `backend/commands/objection_v2.py` | 36 | V2b TODO markers at 12 helpers, get_visible_enemies_near() helper |
| `backend/main.py` | 34A, 34B | 23 call sites → get_filtered_game_state_summary(), /status → intel report, enemy phase filtering, tactical/strategic report filtering |
| `backend/ai/enemy_ai.py` | 35 | Watchtower building logic (AI remains omniscient) |
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
| Own region rules + game init visibility | 33 | ~5 |
| Intel report format + tiered display | 34A | ~8 |
| Filtered game state summary | 34A | ~8 |
| Scout persistence (target + adjacent) | 34A | ~5 |
| Battle reveals (6 sites) | 34A | ~5 |
| Status command output | 34A | ~4 |
| PURSUE fog validation + empty arrival | 34B | ~8 |
| SUPPORT + HOLD sally fog-aware | 34B | ~4 |
| Cautious pathfinding fog-aware | 34B | ~4 |
| Enemy phase filtering | 34B | ~4 |
| Tactical/strategic report filtering | 34B | ~3 |
| Event log (intel_updated, intel_decayed) | 34B | ~2 |
| Watchtower construction | 35 | ~8 |
| Watchtower visibility + scout synergy | 35 | ~8 |
| Watchtower damage/repair | 35 | ~5 |
| Watchtower AI building | 35 | ~5 |
| Watchtower serialization | 35 | ~4 |
| Edge cases (broken, retreat, own region behind lines) | 36 | ~8 |
| Davout PURSUE fog check | 36 | ~3 |
| V2b helper + TODO marker validation | 36 | ~4 |
| Integration (full turn cycle with fog) | 36 | ~5 |
| **Total estimated** | | **~142-160** |

**Final test count estimate:** 2036 (current) + ~142-160 = **~2178-2196**

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

### Internal Dependencies (Session Order)

| Session | Depends On | Critical Path |
|---------|-----------|---------------|
| 33 | — (foundation) | RegionIntel model, calculate_visibility(), serialization |
| 34A | 33 | Uses intel store for filtering; builds `get_filtered_game_state_summary()` |
| 34B | 34A | Uses `get_filtered_game_state_summary()` for display filtering |
| 35 | 33 | Uses `calculate_visibility()` for watchtower PARTIAL adjacency |
| 36 | 34A, 34B, 35 | Edge cases + integration across all systems |

**Note:** Sessions 34B and 35 are independent of each other and could theoretically run in parallel, but serial execution is recommended to avoid merge conflicts in executor.py.

### Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| 23 endpoint filtering scope (was 12+) | HIGH | Single `get_filtered_game_state_summary()` wrapper, not per-site filtering |
| Existing test breakage from filtered responses | MEDIUM | Tests that check `get_game_state_summary()` need updating |
| AI accidentally reading filtered data | LOW | AI confirmed omniscient, uses `world.marshals` directly |
| Performance of per-turn visibility calculation | LOW | 13 regions × 7 marshals = trivial. Revisit at 80+ regions. |
| Watchtower field pattern diverges from building list | MEDIUM | All 4 integration points documented in Session 35 checklist |
| Reckless cavalry auto-charge bypassing fog | RESOLVED | Design decision: auto-charge ignores fog (thematically correct for reckless cavalry) |
| PURSUE empty-arrival complexity | RESOLVED | Simplified: no new interrupt type; auto-cancel if empty, existing personality vectors if adjacent |
| Cannon fire fog interaction | RESOLVED | Non-issue: every battle involves a player marshal, fogged cannon fire is impossible in 2-faction design |
| Marshal-present visibility gap | RESOLVED (32c) | Step 0 added: any region with friendly marshal → FULL military. Covers Grouchy in Waterloo at game start. |
| calculate_visibility() timing | RESOLVED (32c) | Runs at END of `_advance_turn_internal()` after all processing. Broken retreats, auto-charges resolved first. |
| PARTIAL decay timeline | RESOLVED (32c) | Same timeline as FULL, offset from `last_updated_turn`. Freshness of observation is the same regardless of detail level. |
| Stale snapshot data integrity | RESOLVED (32c) | Refresh path (FULL/PARTIAL) queries live data. Decay path (STALE/LAST_KNOWN) freezes snapshot. Two clearly separated code paths. |

---

## Part 6: Session Breakdown Summary

| Session | Scope | Complexity | Tests | Cumulative |
|---------|-------|------------|-------|------------|
| 33 | Intel model + visibility + decay + serialization + game init | Sonnet | ~45 | ~2081 |
| 34A | Intel report + filtered game state + scout persistence + battle reveals | Sonnet | ~30 | ~2111 |
| 34B | PURSUE fog + SUPPORT/HOLD fog + cautious pathfinding + display filtering | Sonnet | ~25 | ~2136 |
| 35 | Watchtower building + visibility + AI + repair + synergy | Sonnet | ~30 | ~2166 |
| 36 | Edge cases + Davout PURSUE + V2b markers + smoke test + docs | Sonnet | ~20 | ~2186 |
| Review | Opus code review gate — verify all 23 endpoints + no data leaks | Opus | 0 | ~2186 |

All sessions are Sonnet-level except the code review gate (Opus).

**Session 34 split rationale (Session 32b decision):** Original session 34 had ~12 work items spanning filtering infrastructure AND strategic command fog-awareness. Split into 34A (data flow: intel report, filtered summary, scout/battle persistence) and 34B (behavior: strategic commands, display filtering, event log) to reduce risk. 34A must complete before 34B — `get_filtered_game_state_summary()` is a dependency for display filtering.
