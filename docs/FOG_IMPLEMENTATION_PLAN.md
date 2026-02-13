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

**Implementation: COMPLETE (Session 34A, Feb 12 2026)**
- [x] Create `backend/intel_report.py` — Berthier Intelligence Report module
- [x] Create `get_filtered_game_state_summary()` on WorldState (C1 fix)
  - Wrapper that calls `get_game_state_summary()` then filters by visibility
  - Enemy marshals hidden at UNKNOWN, strength_band only at PARTIAL/STALE, exact at FULL
  - Own region economic data always full; enemy economic data only at FULL
  - Replaced all 29 call sites (26 in main.py, 3 in executor.py) — actual count higher than estimated 23
- [x] Wire status command to `intel_report.py`
  - Created `_execute_status()` in executor.py
  - Routed "status" action in command routing block
  - Updated `/status` GET endpoint to return intel report + filtered game state
- [x] Wire scout action → `update_intel_from_scout()` in `_execute_scout()` (C2 fix)
  - Targeted scout → FULL on target region
  - Adjacent scan → PARTIAL refresh on each adjacent region
- [x] Wire battle resolution → `update_intel_from_battle()` at all 6 resolve_battle sites
  - `executor.py`: 5 sites (main attack, general attack, sally 2, sally 3, glorious charge)
  - `world_state.py`: 1 site (auto-charge in `_process_reckless_cavalry_turn_start()`)
- [x] 39 unit tests: intel report format/tiers, filtered game state (enemy hiding, fogged_forces separation, FULL shown, economic data, float check), scout persistence (targeted + adjacent + persistence across turns), battle reveals (attack + auto-charge), status command wiring, edge cases, full-path integration (executor.execute)

**Tests:** 39 new (2130 total passing, 3 skipped)
**Smoke test gate:** PASSED

---

### Session 34B: Strategic Commands + Display Filtering (Sonnet)

**Goal:** PURSUE fog validation, SUPPORT visibility, cautious pathfinding fog-awareness, enemy phase filtering, tactical/strategic event filtering. After this session, fog is fully functional — all API responses respect visibility.

**Status:** NOT YET STARTED. Sessions 33 + 34A + 35 complete. 34B is next.

> **Session 34B-prep review (Feb 13, 2026):** Thorough audit confirmed zero 34B code exists. All 34B items below are unstarted. `RegionIntel` missing from serialization enforcement. Cavalry fog interaction researched (see §34B-R below). No contradictions found between spec and implementation plan — all issues are gaps, not conflicts.

**Design principle (confirmed Session 34B review):** Game mechanics use real world data — the executor is deterministic (Golden Rule #6). Fog only filters what the PLAYER sees in messages and UI. Same principle as AI omniscience: the simulation is accurate, the player's view is filtered. This means sally ratio checks, combat resolution, and pathfinding *decisions* use real data. Only the *display* of those decisions is fog-filtered. **Document this in a comment at the top of any fog-filtering function:** "Fog filters information, not mechanics."

**Pre-implementation fix (do BEFORE any 34B code):**
- [ ] Add `RegionIntel` to `SERIALIZABLE_CLASSES` in `tests/test_serialization_enforcement.py` (line 557). Currently missing — prevents regression detection if someone adds a field to RegionIntel without serializing it. Add a `TestRegionIntelSerializationEnforcement` class mirroring the pattern for other classes.
- [ ] Add `RegionIntel` to the serializable classes list in `CLAUDE.md` (line 167, currently lists 8 classes).

**§34B-R: Cavalry Fog Interaction Research (completed Feb 13 pre-review)**

Cavalry has movement_range=2 (infantry=1). This creates fog interactions at several points:

| Feature | Range | Fog Impact | Action Needed |
|---------|-------|-----------|---------------|
| **MOVE_TO movement** | 2 regions/turn | Intermediate region check uses `world.get_enemies_in_region()` (omniscient). Cavalry can "sense" hidden enemies in middle region. | **ACCEPTED for Phase 6.** Intermediate region contact is a physical encounter, not information. The marshal physically passes through the region. The contact interrupt is correct — you can't walk through an army you don't know about. The fog breach is that you get blocked BEFORE arriving (should discover on arrival). Acceptable because: (a) changing intermediate-check to fog-aware requires handling "surprise encounter mid-move" which is complex, (b) on 13 regions the impact is minimal, (c) the contact interrupt already handles the gameplay gracefully. **Add TODO for 1805:** fog-aware intermediate checks with surprise encounter interrupt. |
| **Cavalry charge** | 2 regions away | Middle-region enemy check uses `world.get_marshals_in_region()` (omniscient). Blocks charge if enemies in middle. | **ACCEPTED for Phase 6.** Same reasoning as MOVE_TO — physically passing through a region means encountering forces there. The "leapfrog" block is a physical constraint, not an intelligence one. |
| **Auto-charge (reckless 4+)** | `marshal.movement_range` (=2) | `_find_nearest_enemy_for_nation()` scans ALL enemies omnisciently. Already documented in spec §9.2: "auto-charge ignores fog." | **NO CHANGES NEEDED.** By design (spec §9.2). Reckless cavalry finds trouble. |
| **PURSUE movement** | 2 regions/turn | Same intermediate-check issue as MOVE_TO. PLUS: target location read from `world.get_marshal(target).location` (the core 34B fix). | **34B fixes target location (7 sites).** Intermediate-check omniscience accepted same as MOVE_TO. |
| **Sally (HOLD)** | Adjacent only | `region.adjacent_regions` loop — no cavalry range extension. | **NO CHANGES NEEDED.** Adjacency guarantees PARTIAL (Step 2 of calculate_visibility). Confirmed: sally does NOT use cavalry 2-range. |

**Summary:** Cavalry 2-range does NOT create new fog-filtering requirements beyond what's already planned in 34B. The intermediate-region omniscience is accepted as a physical encounter constraint. The only 34B cavalry issue is PURSUE target location (already planned). Sally is adjacent-only (confirmed safe).

**Prerequisites (build FIRST — everything else depends on these):**
- [ ] `get_last_known_location(marshal_name)` helper on WorldState
  - Scans all RegionIntel objects in `self.intel`
  - Returns `(region_name, last_updated_turn, visibility)` tuple, or `None` if never scouted
  - Finds the RegionIntel whose `known_marshals` list contains an entry with matching name, picks the one with the most recent `last_updated_turn`
  - Handles: never scouted → returns None; marshal in multiple stale regions → return most recent; marshal destroyed → last intel entry persists (player's last knowledge is that the marshal existed there)
- [ ] `get_visible_enemies_in_region(region_name, nation)` helper on WorldState
  - Wraps `get_enemies_in_region()`, filters by `get_region_intel(region).visibility`
  - FULL: return full enemy data (exact strength, morale, stance)
  - PARTIAL/STALE: return name + strength band only (no exact numbers)
  - LAST_KNOWN/UNKNOWN: return empty list (enemies not confirmed visible)
  - Does NOT replace `get_enemies_in_region()` — AI needs omniscient access, too many callsites

**Implementation:**

**1. PURSUE fog validation (HIGH RISK):** read target location from intel store, not raw marshal data (§5.2)
- [ ] Replace `world.get_marshal(target).location` → `world.get_last_known_location(target)` at strategic.py lines 850, 880, 901, 945, 963, 985, 992
  - If returns None (UNKNOWN, never scouted): reject with "No intelligence on [target]'s position, Sire."
  - If STALE/LAST_KNOWN: allow, use last known position for pathfinding — pursuer heads toward outdated location
  - Target destroyed mid-pursuit in fog: pursuer continues toward last known position, discovers truth on arrival. Identical to "target moved away" — auto-cancel, report. Needs explicit test.
  - Multi-region sighting edge case: if Wellington appears in stale intel at both Waterloo (turn 2) and Brussels (turn 5), `get_last_known_location()` returns Brussels (most recent `last_updated_turn`). The older Waterloo entry keeps stale data but the search finds the freshest sighting.

**2. PURSUE empty-arrival (MEDIUM RISK):** detect target not at destination (§5.2)
- [ ] Marshal arrives → target not in region → check surroundings
  - **Arrival timing:** Strategic orders execute during `process_strategic_orders()` (turn_manager.py:144) BEFORE `advance_turn()` (line 154). `calculate_visibility()` runs at END of `_advance_turn_internal()` (line 2688). So at arrival moment, intel store is stale from previous turn. **Resolution:** On arrival, use raw `world.get_marshals_in_region(current_region)` for the current region (marshal is physically there, this is legitimate) and raw `world.get_enemies_in_region(adj, nation)` for adjacent regions (marshal just arrived and can see surroundings). This is an implicit mini-refresh, not a fog breach — the formal intel store catches up when `calculate_visibility()` runs at turn end.
  - No enemies in region AND no enemies adjacent: order auto-cancels, message "[Marshal] arrives at [region] but finds no sign of [target]. Last intelligence was [X] turns old. Awaiting orders, Sire."
  - Enemies in region or adjacent: existing personality contact vectors handle encounter — aggressive charges, cautious reports/scouts, literal continues as ordered (no new interrupt type needed)

**3. SUPPORT safety check (LOW RISK):** fog-aware (spec §5.3 note)
- [ ] `_execute_support()` adjacent enemy scan at lines 1277-1281: replace `world.get_enemies_in_region()` with `world.get_visible_enemies_in_region()`
  - Only reports enemies the player can see. If enemies are hidden in fog, SUPPORT cannot assess safety.
  - Message change: if enemies only at PARTIAL visibility, say "forces reported near [ally]" with band, not exact counts

**4. Cautious pathfinding (LOW RISK):** fog-aware (spec §9.3)
- [ ] Add `fog_aware=False` parameter to `_get_enemy_occupied_regions()` at strategic.py
  - When `fog_aware=True`: filter by PARTIAL+ visibility from intel store. `world.get_region_intel(region_name).visibility in (FULL, PARTIAL)` before checking enemies.
  - When `fog_aware=False` (default): existing omniscient behavior (preserves AI pathfinding).
  - Set `fog_aware=True` for player marshals, `fog_aware=False` for AI (check `marshal.nation == world.player_nation`).
  - Affects ALL callers (shared function): MOVE_TO (line 685 via `_get_personality_aware_path`), PURSUE (line 880), SUPPORT (line 1313), go_around reroutes (line 375), literal silent reroutes (line 1733). All 5+ callers must pass correct fog_aware value.
  - Cautious marshals only avoid enemies they can see. Walking into a trap because intel was bad is a fog moment — existing contact interrupt handles the surprise encounter.

**5. HOLD sally logic (NO CHANGES NEEDED — verified):**
- Sally scan at strategic.py line 1148-1149 iterates `region.adjacent_regions` ONLY — strictly adjacent, no cavalry extended range
  - Adjacency guarantees PARTIAL visibility (Step 2 of `calculate_visibility()` — any region adjacent to friendly marshal is PARTIAL)
  - Therefore all sally targets are always visible to the holding marshal. No fog filter needed on targeting.
  - Ratio check at line 1151 uses `enemy.strength` (exact data). Per design principle above: game mechanics use real data, fog filters display. The sally *decision* is deterministic; the *message shown to player* uses fog-appropriate language.
  - Note for 1805: if cavalry gets extended sally range in the future, this needs fog filtering for non-adjacent targets.

**6. Enemy phase display filtering (HIGH RISK, MOST COMPLEX):** (§4.2) in `main.py`
- [ ] Create `_filter_enemy_phase_by_visibility(enemy_phase, world)` function in main.py
  - For each action in each nation's action list:
    1. **Involves player marshal?** Check if `ai_action.target` matches a player marshal name, OR if action `events[]` contain a battle with player nation involved → **ALWAYS SHOW** (player was in the battle, they know about it)
    2. **Extract action region:** From `ai_action.target` (for attack/move) or from action result `events[].location`. If no clean region field, infer from marshal's post-action location via action result.
    3. **Check visibility:** `world.get_region_intel(action_region).visibility`
    4. FULL → show as-is (full action display)
    5. Below FULL → **suppress** for initial implementation
    6. **Arrival exception (deferred to polish):** If enemy moves INTO a visible region, show "[forces] appear at [region]". Requires checking destination visibility, not origin. Deferred because: extracting destination reliably from heterogeneous action dicts is fragile. Core suppression is sufficient for Phase 6.
  - **Do NOT parse message strings** to extract regions. Use structured `ai_action` fields only. If a field is missing or unrecognized → **suppress** (safe side — never show more than intended).
  - **PARTIAL "reports of movement" tier: DEFERRED** — spec §4.2 explicitly calls this a "polish tier (not in initial implementation)". Implement after core fog is stable.
  - Must be bulletproof on: direct attacks, general attacks, sallies, auto-charges against player, admin actions (recruit/build/repair)

**7. Tactical event filtering (MEDIUM RISK):**
- [ ] Filter tactical events by visibility before sending to client (main.py line 490-491)
  - Player nation events → always show (drill, fortify, retreat, construction — all player marshal events)
  - Enemy nation events → check region visibility:
    - Occupation events ("Enemy occupies [region]"): suppress if region below PARTIAL — player doesn't know enemy is there
    - Supply attrition for enemy nations: suppress if region not visible
    - Auto-charge results: always involve player marshal → always show
  - Key: check `event.get("nation")` or `event.get("marshal")` → determine if player or enemy → if enemy, check `event.get("location")` against intel visibility

**8. Strategic report filtering (NO CHANGES NEEDED — verified):**
- Strategic reports are about player marshals executing their own orders
  - All involve the player's marshal, so location is automatically FULL (Step 0 of `calculate_visibility()`)
  - Hold-battle reports: player marshal involved → FULL. Movement progress: player marshal → known. Cannon fire interrupts: non-issue per spec §9.4 (every battle involves a player marshal).
  - If a report mentions enemy by name in context of battle: the battle itself grants FULL visibility. Not a leak.

**9. Event log types (LOW RISK):**
- [ ] Emit `intel_updated` events in `calculate_visibility()` when visibility CHANGES for a region
  - Data: `{type: "intel_updated", region, new_visibility, old_visibility, source}`
  - Only emit on actual change (not every turn refresh)
- [ ] Emit `intel_decayed` events in `decay_intel()` when intel downgrades
  - Data: `{type: "intel_decayed", region, old_visibility, new_visibility}`
- [ ] `target_not_found` is NOT a separate event type — it's the PURSUE auto-cancel message (item 2 above)
- These events are always player-visible (player caused the visibility change). No filtering needed on the events themselves. They feed Campaign Log (6.5) and Gazette (8.5).

**10. Cross-cutting notes (for implementer reference):**
- **Attack targeting (Issue C):** `_fuzzy_match_enemy()` in executor.py searches `world.marshals` directly. A player typing "attack Kutuzov" when Kutuzov was never scouted gets a match. This is ACCEPTED for 13 regions (small map, players know all marshals). **Add TODO note for 1805:** fuzzy matching should be filtered by known marshals at 80+ regions.
- **`_build_marshal_snapshot()` confirmed** at world_state.py:483. Handles `full=True` (exact) and `full=False` (band only). Ready for use.
- **`get_enemies_in_region()` stays omniscient.** Do NOT add fog parameter. AI and executor internals need unfiltered access. Only display/UI paths use `get_visible_enemies_in_region()`.

**Tests (all items):**

*Pre-implementation fix:*
- [ ] RegionIntel in SERIALIZABLE_CLASSES → enforcement test passes

*Helpers:*
- [ ] `get_last_known_location()`: never scouted → None
- [ ] `get_last_known_location()`: multiple stale regions → most recent `last_updated_turn` wins
- [ ] `get_last_known_location()`: destroyed marshal → last intel entry persists
- [ ] `get_visible_enemies_in_region()`: FULL → full data returned
- [ ] `get_visible_enemies_in_region()`: PARTIAL → name + band only
- [ ] `get_visible_enemies_in_region()`: UNKNOWN → empty list

*PURSUE fog:*
- [ ] PURSUE into UNKNOWN target → reject with "No intelligence on [target]'s position, Sire."
- [ ] PURSUE into STALE target → use last known position, pathfinding proceeds
- [ ] PURSUE target destroyed in fog → pursuer arrives, auto-cancels same as "target moved"
- [ ] PURSUE multi-region sighting → uses most recent `last_updated_turn`
- [ ] PURSUE empty arrival, no adjacent enemies → auto-cancel message with intel age
- [ ] PURSUE empty arrival, enemies adjacent → personality contact vector fires
- [ ] PURSUE arrival timing → raw world data check on arrival is correct (not stale intel store)

*SUPPORT + Pathfinding:*
- [ ] SUPPORT safety check only sees visible enemies
- [ ] SUPPORT message uses band language for PARTIAL enemies
- [ ] Cautious pathfinding avoids only visible enemies (fog_aware=True for player)
- [ ] Cautious walks into trap when enemy in fogged region → contact interrupt
- [ ] AI pathfinding still omniscient (fog_aware=False)
- [ ] `_get_enemy_occupied_regions(fog_aware=True)` consistent across MOVE_TO, PURSUE, SUPPORT, reroutes

*Display filtering:*
- [ ] Enemy phase: battle involving player always shown regardless of fog
- [ ] Enemy phase: action in FULL region shown
- [ ] Enemy phase: action in UNKNOWN/STALE region suppressed
- [ ] Enemy phase: admin action (recruit/build) in fogged region suppressed
- [ ] Enemy phase: missing/unrecognized action field → suppressed (safe default)
- [ ] Tactical events: player nation events always shown
- [ ] Tactical events: enemy occupation in fogged region suppressed
- [ ] Tactical events: enemy supply attrition in fogged region suppressed

*Event log:*
- [ ] Event log: `intel_updated` emitted on visibility change (not on every turn refresh)
- [ ] Event log: `intel_decayed` emitted on decay
- [ ] Event log: `target_not_found` logged when PURSUE arrives at empty region (data: marshal, target, region, intel_age)

**Tests expected:** ~35
**Smoke test gate:** `pytest tests/ -v --tb=no -q` green, curl test end-turn flow to verify all filtering

---

### Session 35: Watchtower Building (Sonnet)

**Goal:** Watchtower as dedicated building, construction, visibility effect, scout synergy, AI building, repair.

**Implementation: COMPLETE (Session 35, Feb 12 2026)**
- [x] Add `watchtower` and `watchtower_turns_remaining` fields to Region model (§7.2)
- [x] Add "watchtower" keyword to `_extract_building_type()` in executor.py (H1 fix)
- [x] Add watchtower build handler `_execute_build_watchtower()` — bypasses slot system
  - Cost: 250 gold, 2 turns. All region types. Dedicated field, not building slots.
- [x] Extend `process_construction_timers()` for watchtower countdown
- [x] Wire watchtower into `calculate_visibility()` Step 3 — PARTIAL on adjacent
- [x] Watchtower scout synergy: +1 turn freshness via `_has_watchtower_coverage()` helper
- [x] Battle damage: active → damaged (major always, normal 25%), under_construction → destroyed
- [x] Plunder destroys watchtower, secure damages active / destroys under_construction
- [x] Extend `_execute_repair()` for watchtower: damaged → under_construction (2t, 150g)
- [x] AI watchtower building: P6.5 in `_pick_admin_action()` (after repair, before rebuild recruit)
  - `_find_best_watchtower_region()`: border regions scored by enemy adjacency + income
  - `_find_damaged_building_region()`: also detects damaged watchtowers
- [x] Mock parser: watchtower routes through existing "build " keyword → `_extract_building_type()`
- [x] Serialization enforcement tests pass (14/14)
- [x] Debug command `add_building` updated for watchtower
- [x] `get_game_state_summary()` and `get_filtered_game_state_summary()` include watchtower data
- [x] 53 unit tests: construction, visibility, scout synergy, damage, repair, AI, serialization, edge cases

**Tests:** 53 new (2183 total passing, 3 skipped)
**Smoke test gate:** PASSED

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
- [ ] Verify all 29 call sites across 8 endpoints use `get_filtered_game_state_summary()`
- [ ] Verify no enemy data leaks in tactical events, enemy phase, or turn results
- [ ] Verify strategic reports don't need filtering (all player marshal events, confirmed 34B review)
- [ ] Verify AI is completely unaffected by fog (omniscient, reads `world.marshals` directly)
- [ ] Verify reckless cavalry auto-charge works unchanged (no fog filtering)
- [ ] Verify serialization roundtrip for all new fields (RegionIntel, watchtower)
- [ ] Verify backward compat with old saves (empty intel → calculate_visibility on load)
- [ ] Verify combat.py still accesses zero world state (confirmed safe in Session 32 audit)
- [ ] Check for float values in any fog-related data sent to Godot
- [ ] Review V2b TODO markers at all 12+ objection helper functions
- [ ] Verify intel_report.py produces correct tiered output
- [ ] Verify refresh vs decay path separation — no `get_marshals_in_region()` calls in decay path, no snapshot freezing in refresh path
- [ ] Verify `get_last_known_location()` handles: never scouted, multi-region sighting, destroyed marshal
- [ ] Verify `get_visible_enemies_in_region()` is not called by AI or executor internals (only display paths)
- [ ] Verify HOLD sally uses adjacent-only scan (no cavalry extended range) — if future change adds extended range, fog filter needed
- [ ] Verify `_fuzzy_match_enemy()` TODO note exists for 1805 (filter by known marshals at 80+ regions)
- [ ] Verify PURSUE arrival uses raw world data for current region (justified: marshal physically present)

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
| `backend/models/world_state.py` | 33, 34A, 34B | intel dict, calculate_visibility() + decay_intel() at END of `_advance_turn_internal()`, get_region_intel(), get_filtered_game_state_summary(), get_last_known_location(), get_visible_enemies_in_region() |
| `backend/models/region.py` | 35 | watchtower, watchtower_turns_remaining fields |
| `backend/commands/executor.py` | 34A, 35 | scout→intel update, battle→intel update (6 sites), status→intel_report, _extract_building_type watchtower, _execute_build watchtower branch, _execute_repair watchtower |
| `backend/commands/strategic.py` | 34B | PURSUE reads intel store (7 sites), empty-arrival handling, cautious pathfinding fog-aware (`_get_enemy_occupied_regions` affects MOVE_TO/PURSUE/SUPPORT/reroutes), SUPPORT safety fog-aware. HOLD sally: no changes (adjacent-only scan, adjacency guarantees PARTIAL) |
| `backend/commands/disobedience.py` | 36 | Davout PURSUE fog-aware check |
| `backend/commands/objection_v2.py` | 36 | V2b TODO markers at 12 helpers, get_visible_enemies_near() helper |
| `backend/main.py` | 34A, 34B | 29 call sites → get_filtered_game_state_summary(), /status → intel report, enemy phase filtering (`_filter_enemy_phase_by_visibility`), tactical event filtering. Strategic reports: no changes (player marshals only). |
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
| `get_last_known_location()` helper | 34B | ~3 |
| PURSUE fog validation (UNKNOWN/STALE/destroyed target) | 34B | ~5 |
| PURSUE empty-arrival (both branches + timing) | 34B | ~3 |
| SUPPORT fog-aware safety check + band messaging | 34B | ~3 |
| Cautious pathfinding fog-aware (all callers) | 34B | ~4 |
| Enemy phase filtering (player battles, FULL, suppression) | 34B | ~5 |
| Tactical event filtering (player vs enemy, visibility) | 34B | ~3 |
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
| **Total estimated** | | **~148-168** |

**Final test count estimate:** 2036 (current) + ~148-168 = **~2184-2204**

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
| 33 | Intel model + visibility + decay + serialization + game init | Sonnet | 55 | 2091 |
| 34A | Intel report + filtered game state + scout persistence + battle reveals + fogged_forces | Sonnet | 39 | 2130 |
| 34B | PURSUE fog + SUPPORT fog + cautious pathfinding + enemy phase/tactical filtering + event log | Sonnet | ~35 | ~2218 |
| 35 | Watchtower building + visibility + AI + repair + synergy | Opus | 53 | 2183 |
| 36 | Edge cases + Davout PURSUE + V2b markers + smoke test + docs | Sonnet | ~20 | ~2238 |
| Review | Opus code review gate — verify all 29 endpoints + no data leaks | Opus | 0 | ~2238 |

All sessions are Sonnet-level except the code review gate (Opus).

**Session 34 split rationale (Session 32b decision):** Original session 34 had ~12 work items spanning filtering infrastructure AND strategic command fog-awareness. Split into 34A (data flow: intel report, filtered summary, scout/battle persistence) and 34B (behavior: strategic commands, display filtering, event log) to reduce risk. 34A must complete before 34B — `get_filtered_game_state_summary()` is a dependency for display filtering.
