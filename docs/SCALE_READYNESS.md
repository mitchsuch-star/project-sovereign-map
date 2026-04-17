# Scale Readiness — Europe Audit Report

> Last Updated: April 16, 2026
> Audit Date: April 16, 2026

---

## 1. Baseline Snapshot

| Field | Value |
|-------|-------|
| Audit date | April 16, 2026 |
| Branch | master |
| Commit | 0e42688 |
| Tree status | Clean |
| Audited | Clean HEAD |
| Claimed test count | ~3799 (STATUS.md, verified Feb 24) + 17 renderer regression tests |
| Region count | 19 (REGIONS_DATA in region.py) |
| Nation count | 5 (France, Britain, Prussia, Austria, Saxony) |
| Marshal count | 11 (4 French + 7 enemy) |
| Map-scale assumption | 19-region shell; EA target is "Partial Europe" (ROADMAP.md Phase EA) |

---

## 2. Executive Verdict

**Is the project structurally ready to start full-Europe wiring now?**

No. Three categories of blocker must be addressed first: pathfinding cost, AI omniscience, and content-model coupling. The codebase is stable and well-tested at 19 regions, but multiple systems assume a small, fixed map in ways that would cause correctness failures, unfair AI behavior, and unacceptable turn times at 80-120 regions.

**Top 3 blockers:**

1. **Uncached BFS pathfinding in AI hot loop** — 32 distance calls per marshal per turn with no caching. At 100 regions and 40 marshals, estimated 2-4 seconds per turn in Python. Clear performance blocker.
2. **Omniscient AI bypasses fog of war** — 40+ direct `world.marshals.values()` scans in enemy_ai.py see all marshals regardless of visibility. Both unfair and expensive at scale.
3. **5-nation roster hardcoded across 5 config surfaces** — Adding nation 6 triggers cascading validation failures. Marshal/diplomat creation is manual, not data-driven.

**Which smaller-map assumptions are most dangerous?**

- Turn limit hardcoded at 40 (0.3 turns/region at Europe scale — unwinnable)
- Frontend adjacency table manually duplicated from backend (drift guaranteed at 80+ regions)
- Nation colors scattered across 3+ Godot files with no backend source
- Marshal management UI designed for 5-10 marshals (keyboard shortcuts cap at 9)

**Which parts are already good enough to carry forward?**

- Backend region data model (REGIONS_DATA) is centralized and data-driven
- Nation config validation (`validate_runtime_nation_support()`) catches missing config early
- Serialization enforcement tests are comprehensive
- Map consistency tests catch backend/frontend region drift
- Cached helpers exist (`get_active_nations()`, `get_nation_regions()`) — pattern is established
- Parser derives known_regions dynamically from REGIONS_DATA
- Modding validator has strong schema enforcement

---

## 3. Findings

### F1. Uncached BFS Pathfinding in AI Hot Loop

- **Severity:** Critical
- **Category:** AI efficiency / hot-path problem
- **Visibility:** Acceptable now but certain to break at Europe scale
- **Evidence:** `world_state.py:2029-2054` — pure BFS with `queue.pop(0)` (O(n) deque op), no memoization, no symmetry exploitation. Called from `enemy_ai.py` at 32+ call sites per marshal evaluation (lines 2189, 2502, 2533, 2613, 2927, 2946, 2996, 3012, 3076, 3120, 3145, 3161, 3177, 3472, 3481, 3498, 3590, 3607, 3743, 4266, 4267, 4274, 4347, 5015, 5036, 5167, 5184, 5203, 5204).
- **Counter-evidence:** `find_path()` at `world_state.py:2099-2197` uses Dijkstra, which is better. But `get_distance()` is the hot call and uses naive BFS.
- **Scale impact:** 19 regions: ~16K BFS steps/turn. 100 regions: ~256K steps/turn (16x). At Python speed (~50-100us/step): 2-4 seconds per AI turn.
- **Fix direction:** LRU cache on `get_distance()` (static graph, only invalidated on capture). Replace `queue.pop(0)` with `collections.deque.popleft()`. Consider all-pairs precomputation at load time for maps under 150 regions.
- **Blocker class:** Must fix before Europe wiring

### F2. Omniscient AI — 40+ Unfogged Marshal Scans

- **Severity:** Critical
- **Category:** AI quality / fairness problem
- **Visibility:** Already visible now (AI sees fogged enemies), certain to worsen at scale
- **Evidence:** `enemy_ai.py` has 40+ direct `world.marshals.values()` iterations without fog filtering. Examples: line 1200 (defender detection), 2375 (force density), 2604 (blocking enemies), 2843 (ally threats), 4031 (adjacent strength). The fog-aware path (`_get_enemy_contacts()` at line 485) only applies to the player nation; enemy nations use omniscient `get_enemies_of_nation()`.
- **Counter-evidence:** Comment at line 452-464 acknowledges this: "current intel model is player-perspective only." Infrastructure exists (`get_visible_enemies()` at `world_state.py:1534`).
- **Scale impact:** Fairness asymmetry grows with map size (more hidden information). Cost: 40 marshals x 40 scans x 80 items = 128K list ops per AI turn.
- **Fix direction:** Build spatial index (`marshals_by_region` dict, O(1) lookup). Extend fog model to all nations, not just player. Smallest viable: index + fog-aware queries for all enemy AI paths.
- **Blocker class:** Must fix before Europe wiring

### F3. 5-Nation Roster Hardcoded Across 5 Config Surfaces

- **Severity:** Critical
- **Category:** Data-model / content-coupling problem
- **Visibility:** Not a problem at 19 regions, breaks immediately at Europe scale
- **Evidence:** `nation_config.py:19-53` defines DEFAULT_NATION_GOLD, BASE_NATION_ACTIONS, DEFAULT_NATION_AUTHORITY for exactly 5 nations. `diplomat.py:59-95` has 5 named diplomats. `marshal.py:1357-1779` hardcodes 11 marshals in two 470-line functions. `validate_runtime_nation_support()` at `nation_config.py:157-181` enforces ALL 5 surfaces must have every nation — adding nation 6 without all 5 entries crashes.
- **Counter-evidence:** The validation function itself is good design — it catches missing config early. The problem is content creation cost, not architecture.
- **Scale impact:** Adding 3-5 new nations for Europe requires ~40 new marshals (each manually authored with personality, ability, biography, relationships) plus 5 config entries per nation.
- **Fix direction:** Data-driven marshal/diplomat factories. Nation config extensible with sensible defaults for new nations.
- **Blocker class:** Must fix before Europe wiring

### F4. Frontend Region Adjacency Duplication

- **Severity:** Critical
- **Category:** Data-model / content-coupling problem
- **Visibility:** Already a maintenance risk now, guaranteed drift at 80+ regions
- **Evidence:** Backend: `region.py:328-500` (REGIONS_DATA, authoritative). Frontend: `map.gd:30-50` hardcodes identical REGION_CONNECTIONS dict. Both must be edited for any region change. `test_map_consistency.py` catches drift, but the duplication itself is the problem.
- **Counter-evidence:** The test catches it — drift won't go silently. But at 80+ regions, maintaining two copies is error-prone and slow.
- **Scale impact:** Adding one region requires editing 6-7 files (region.py, map.gd adjacencies, map.gd positions, prompt_builder fallback, potentially parser, renderer base).
- **Fix direction:** Frontend loads adjacency from backend API or shared JSON asset, not hardcoded dict.
- **Blocker class:** Must fix before Europe wiring

### F5. Nation Colors Scattered Across 3+ Godot Files

- **Severity:** Critical
- **Category:** Data-model / content-coupling problem
- **Visibility:** Already visible now, worsens linearly with nation count
- **Evidence:** Nation colors duplicated in `map.gd:52-61`, `utils.gd` (NATION_COLORS), `war_detail_popup.gd`. No backend source. Adding one nation requires 3+ independent Godot edits.
- **Counter-evidence:** utils.gd is intended as the shared source, but other files duplicate rather than import.
- **Fix direction:** Single NATION_COLORS source (utils.gd or backend config), all other files import.
- **Blocker class:** Fix during first Europe prototype

### F6. Full Map Rebuild on Every Update

- **Severity:** Major
- **Category:** Renderer / UI density problem
- **Visibility:** Acceptable now, performance risk at Europe scale
- **Evidence:** `map.gd:1631-1670` `update_all_regions()` iterates all regions. `map_renderer_base.gd:603-627` `_rebuild_dynamic_nodes()` clears and recreates force_layer and garrison_layer entirely (lines 604-605 call `_clear_children()`, then rebuild all). Called from `main.gd` at 10+ response handler sites.
- **Counter-evidence:** At 100 regions with 2-5 nodes each, this is ~200-500 node recreations per update — likely still under 16ms in Godot. May not be a hard blocker.
- **Scale impact:** 200-500 new nodes per update. Tooltip rebuild on hover includes O(n^2) relationship scan (`map.gd:1553-1579`).
- **Fix direction:** Region-scoped update (only rebuild changed regions). Cache tooltip text.
- **Blocker class:** Fix during first Europe prototype

### F7. Marshal Management UI Designed for 5-10 Marshals

- **Severity:** Major
- **Category:** Renderer / UI density problem
- **Visibility:** Breaks at Europe scale
- **Evidence:** `marshal_management.gd:32-64` binds number keys 1-9 (hard cap). Line 61: 320px card height hardcoded. Lines 268-276: all relationships expanded inline (at 40 marshals = 300+ relationship lines).
- **Counter-evidence:** Scroll still works; it just becomes unnavigable. Not a crash.
- **Scale impact:** 40+ marshals: keyboard shortcuts defunct, scroll misaligned, relationship sections unreadable.
- **Fix direction:** Paginated cards, lazy-load relationships, responsive card height.
- **Blocker class:** Fix during first Europe prototype

### F8. Turn Limit Hardcoded at 40

- **Severity:** Major
- **Category:** Pacing / scenario-tuning problem
- **Visibility:** Only at Europe scale
- **Evidence:** `world_state.py:125` `self.max_turns: int = 40`. `turn_manager.py:922-935` checks turn limit for time victory. At 19 regions: 2.1 turns/region (tight but playable). At 100 regions: 0.4 turns/region (unwinnable).
- **Counter-evidence:** `max_turns` is an instance field, not a constant — easily changed per scenario.
- **Scale impact:** Campaign becomes unwinnable at current length.
- **Fix direction:** Scale max_turns with region count or make it scenario-configured.
- **Blocker class:** Must fix before Europe wiring

### F9. Strategic Ledger Monolithic Rendering

- **Severity:** Major
- **Category:** Renderer / UI density problem
- **Visibility:** Acceptable now, degrades at Europe scale
- **Evidence:** `strategic_ledger.gd:169-258` renders all marshals in one BBCode string. No section collapse, no pagination. At 40+ marshals: 1000+ lines of BBCode in single RichTextLabel.
- **Fix direction:** Split by location/status, collapse by default, lazy-render visible sections.
- **Blocker class:** Fix during first Europe prototype

### F10. Action Economy Doesn't Scale with Map Size

- **Severity:** Major
- **Category:** Pacing / scenario-tuning problem
- **Visibility:** Only at Europe scale
- **Evidence:** `nation_config.py:27-33` — France/Britain/Prussia get 4 APs, Austria 3, Saxony 2. `world_state.py:151` `self.max_actions_per_turn: int = 4`. At 80-120 regions, 4 APs cannot manage distributed warfare.
- **Counter-evidence:** This is a tuning knob, not a structural problem. Increasing AP is trivial.
- **Fix direction:** Scale APs with map size or nation power. Decision needed before expansion.
- **Blocker class:** Must fix before Europe wiring

### F11. Prompt Fallback Hardcodes 19 Regions

- **Severity:** Moderate
- **Category:** Data-model / content-coupling problem
- **Visibility:** Both (brittle now, breaks at scale)
- **Evidence:** `prompt_builder.py:567` returns hardcoded string of all 19 region names as fallback. `parser.py:103-108` hardcodes 8 enemy marshal names.
- **Counter-evidence:** Fallback is rarely hit if game_state is correct. Parser derives regions dynamically (line 100).
- **Fix direction:** Import from REGIONS_DATA.keys() instead of hardcoded string.
- **Blocker class:** Fix during first Europe prototype

### F12. Victory Fraction 75% Becomes Unachievable

- **Severity:** Moderate
- **Category:** Pacing / scenario-tuning problem
- **Visibility:** Only at Europe scale
- **Evidence:** `world_state.py:60` `VICTORY_REGION_FRACTION = 0.75`. At 120 regions: 90 regions needed (requires dominating all of Europe).
- **Fix direction:** Dynamic fraction based on map size, or alternative victory conditions.
- **Blocker class:** Fix during first Europe prototype

### F13. Coalition Dynamics Assume 5-Nation Equilibrium

- **Severity:** Moderate
- **Category:** Pacing / scenario-tuning problem
- **Visibility:** Only at Europe scale
- **Evidence:** `coalition.py:138-164` threat decay capped at 3. Friction at `coalition.py:408-425` scales 1.0-0.25. At 10+ potential coalition members, formation becomes trivial.
- **Fix direction:** Scale threat/friction parameters with nation count.
- **Blocker class:** Defer until after expansion starts

### F14. No Nation Config Completeness Test

- **Severity:** Moderate
- **Category:** Tooling / test / workflow problem
- **Visibility:** Both
- **Evidence:** No test verifies all 5 config surfaces (gold, actions, authority, diplomats, marshals) are complete for every nation. Adding a nation to NATION_CAPITALS without all 5 entries fails at runtime.
- **Counter-evidence:** `validate_runtime_nation_support()` catches this at startup — but no test exercises it.
- **Fix direction:** Add `test_nation_config_completeness.py`.
- **Blocker class:** Must fix before Europe wiring

### F15. Hardcoded Region Count in Tests

- **Severity:** Moderate
- **Category:** Tooling / test / workflow problem
- **Visibility:** Both
- **Evidence:** `test_conftest_factories.py:124` and `test_economy_foundations.py:148` assert `len(world.regions) == 19`. Would break on any map expansion.
- **Fix direction:** Replace with `assert len(world.regions) == len(REGIONS_DATA)`.
- **Blocker class:** Must fix before Europe wiring

### F16. Validator VALID_NATIONS Mismatches nation_config.py

- **Severity:** Low
- **Category:** Tooling / test / workflow problem
- **Visibility:** Now
- **Evidence:** `backend/modding/validator.py:71` includes "Spain" and "Russia" in VALID_NATIONS, but `nation_config.py:19-25` only has 5 nations. Validator accepts mods for nations the runtime doesn't support.
- **Fix direction:** Derive VALID_NATIONS from NATION_CAPITALS.keys() at import time.
- **Blocker class:** Fix during first Europe prototype

### F17. No Adjacency Connectivity Test

- **Severity:** Low
- **Category:** Tooling / test / workflow problem
- **Visibility:** Only at Europe scale
- **Evidence:** `test_map_consistency.py` validates bilateral adjacency but doesn't check for isolated regions or disconnected graph components.
- **Fix direction:** Add connected-component test for REGIONS_DATA adjacency graph.
- **Blocker class:** Must fix before Europe wiring

---

## 4. Prior Findings Delta

Cross-check against prior claims in the original SCALE_READYNESS.md:

### "Distance and pathfinding hot paths"
- **Status:** Confirmed
- **Evidence:** 32 uncached BFS calls per marshal per turn in enemy_ai.py. `get_distance()` at `world_state.py:2029` uses naive BFS with `queue.pop(0)`. No caching, no symmetry exploitation.
- **Matters:** Both (acceptable now, clear blocker at scale)
- **Prior assessment:** Correctly sized. This is the #1 performance blocker.

### "Static map and nation coupling"
- **Status:** Confirmed, narrowed
- **Evidence:** Backend region data (REGIONS_DATA) is actually well-centralized. The coupling is in frontend duplication (adjacencies in map.gd, colors in 3+ files), prompt fallback (prompt_builder.py:567), and parser enemy list (parser.py:103-108). Adding one region requires 6-7 file edits.
- **Matters:** Both
- **Prior assessment:** Slightly overrated for backend (which is mostly data-driven), underrated for frontend (which has severe duplication).

### "Omniscient AI outside player-side fog"
- **Status:** Confirmed
- **Evidence:** 40+ `world.marshals.values()` scans in enemy_ai.py without fog. Only player nation uses fog-aware path. Comment at line 452-464 acknowledges this.
- **Matters:** Both (fairness issue now, cost issue at scale)
- **Prior assessment:** Correctly sized. Infrastructure exists but is bypassed.

### "Small-list UI assumptions"
- **Status:** Confirmed
- **Evidence:** Marshal management caps at 9 keyboard shortcuts (marshal_management.gd:32-64). Strategic ledger renders all marshals in one BBCode string (strategic_ledger.gd:169-258). Diplomatic ledger expands all relations inline.
- **Matters:** Mainly at Europe scale
- **Prior assessment:** Correctly sized.

### "Full map refresh and node rebuilds"
- **Status:** Confirmed, slightly overrated
- **Evidence:** `map_renderer_base.gd:603-627` does full clear+rebuild. But at 100 regions with 2-5 nodes each, Godot's node creation is likely still under 16ms. The tooltip hover rebuild (`map.gd:1553-1579` with O(n^2) relationship scan) is the real performance concern.
- **Matters:** Mainly at Europe scale
- **Prior assessment:** Slightly overrated as a blocker — it's a performance concern, not a crash risk.

### "Hardcoded roster and pacing defaults"
- **Status:** Confirmed, underrated
- **Evidence:** Turn limit at 40 (world_state.py:125), victory at 75% (world_state.py:60), AP budget at 4 (nation_config.py:27), manpower pools for only 5 nations (world_state.py:63-69). Adding nation 6 triggers cascading config failures. Marshal/diplomat creation requires manual 470-line functions.
- **Matters:** Breaks immediately at Europe scale
- **Prior assessment:** Underrated. This is not just a rebalance — it's a content creation pipeline problem. Marshal authoring doesn't scale.

### "Metadata drift between systems"
- **Status:** Confirmed, partially mitigated
- **Evidence:** `test_map_consistency.py` catches region/adjacency drift. But color metadata has no cross-system test. Validator VALID_NATIONS includes nations that nation_config doesn't support.
- **Matters:** Both
- **Prior assessment:** Correctly sized. Drift detection exists for regions but not for colors or nation config.

### Missing risks not in prior doc
- **Status:** New missing risk — **no nation config completeness test**. Validator and runtime enforce coverage, but no test exercises this path. Adding a nation to one surface but not all 5 causes runtime crash.
- **Status:** New missing risk — **hardcoded region count in tests** (2 tests assert `== 19`). Would break on any map expansion.
- **Status:** New missing risk — **no adjacency connectivity test**. Could introduce isolated regions in a larger map without detection.

---

## 5. Blocker Ranking

Ranked from highest to lowest expansion risk:

| Rank | Finding | Why |
|------|---------|-----|
| 1 | **F1: Uncached BFS pathfinding** | 2-4 second AI turns at 100 regions. Hard performance wall. |
| 2 | **F2: Omniscient AI (40+ unfogged scans)** | Unfair + expensive. Fairness breaks at any scale; cost compounds. |
| 3 | **F3: 5-nation roster hardcoded** | Cannot add nations without cascading config + content work. |
| 4 | **F4: Frontend adjacency duplication** | 6-7 files per region. Drift guaranteed at 80+ regions. |
| 5 | **F8: Turn limit hardcoded at 40** | Campaign unwinnable at Europe scale. Trivial to fix but must be decided. |
| 6 | **F10: Action economy doesn't scale** | 4 APs insufficient for 80-120 regions. Tuning decision needed. |
| 7 | **F14/F15/F17: Test gaps** | Silent regression when map changes. Quick to fix. |
| 8 | **F5: Nation colors scattered** | 3+ edits per nation. Linear cost growth. |
| 9 | **F6: Full map rebuild** | Performance concern, not a crash risk. |
| 10 | **F7/F9: UI density (marshal mgmt, ledger)** | Unusable at 40+ marshals but doesn't block wiring. |

---

## 6. Phased Roadmap

### Before Europe Wiring

These must be done before adding regions beyond 19:

1. **Cache `get_distance()`** — LRU cache with invalidation on capture. Replace `queue.pop(0)` with `deque.popleft()`. (~2 hours)
2. **Build spatial index for AI** — `marshals_by_region` dict for O(1) lookups instead of 40 O(N) scans. (~4 hours)
3. **Extend fog model to all AI nations** — Replace omniscient `get_enemies_of_nation()` calls in enemy_ai.py with fog-aware queries. (~4-6 hours)
4. **Make nation config extensible** — Sensible defaults for new nations in all 5 config surfaces. Factory pattern for marshals/diplomats. (~1 session)
5. **Eliminate frontend adjacency duplication** — Frontend loads adjacency from backend API or shared JSON asset. (~4 hours)
6. **Scale turn limit and AP with map size** — Make `max_turns` and base AP scenario-configured. Decision: formula or per-scenario constant? (~2 hours)
7. **Add test guardrails** — Nation config completeness test, parametric region count test, adjacency connectivity test. (~1 hour)
8. **Fix hardcoded region count in tests** — Replace `== 19` with `== len(REGIONS_DATA)`. (~15 min)

### During First Europe Prototype

These should be addressed while building the first 80+ region map:

9. **Centralize nation colors** — Single source (utils.gd or backend), all files import. (~2 hours)
10. **Fix prompt fallback** — Import from REGIONS_DATA.keys() instead of hardcoded string. (~30 min)
11. **Align validator VALID_NATIONS** — Derive from NATION_CAPITALS at import time. (~15 min)
12. **Incremental map updates** — Region-scoped rebuild instead of full clear+recreate. (~4 hours)
13. **Marshal management pagination** — Paginated cards, lazy-load relationships. (~1 session)
14. **Strategic ledger sectioning** — Split by location/status, collapse by default. (~4 hours)
15. **Victory condition scaling** — Dynamic fraction or alternative conditions for larger maps. (~2 hours)

### After Europe Map Exists

These can wait until after the first playable Europe prototype:

16. **Tooltip caching** — Cache tooltip text, regenerate only on data change. (~2 hours)
17. **Coalition parameter scaling** — Adjust threat/friction for 10+ nations. (~2 hours)
18. **All-pairs distance precomputation** — Floyd-Warshall at load time for O(1) lookup. (~4 hours)
19. **Save file migration** — Handle loading 19-region saves into 80-region world. (~4 hours)
20. **Diplomatic ledger collapsibles** — Collapsible AI relations sections. (~2 hours)

---

## 7. Confidence Statement

### Directly Verified

- BFS implementation and lack of caching (`world_state.py:2029-2054`)
- `get_distance()` call count in enemy_ai.py (32+ sites counted)
- Omniscient `world.marshals.values()` scan count in enemy_ai.py (40+)
- Fog-aware path only for player nation (`enemy_ai.py:485-487`)
- Nation config limited to 5 nations across all 5 surfaces
- Frontend adjacency hardcoded separately from backend
- Nation colors duplicated in 3+ Godot files
- Marshal management keyboard shortcuts capped at 9
- Turn limit at 40, victory at 75%, AP at 4
- Test hardcoded region count `== 19` in 2 files
- Validator VALID_NATIONS mismatch with nation_config

### Strong Inference

- Turn time estimate of 2-4 seconds at 100 regions (based on BFS step count x Python overhead; not benchmarked)
- Full map rebuild staying under 16ms at 100 regions in Godot (based on node count estimate; not benchmarked)
- Marshal authoring not scaling (based on 470-line function structure; no automated alternative exists)
- Coalition formation becoming trivial at 10+ nations (based on threshold analysis; not simulated)

### Not Verified

- Actual Godot frame-time impact of 200-500 node rebuilds (no Godot runtime in audit environment)
- Whether tooltip O(n^2) relationship scan causes visible frame drops at scale
- Whether save file loading handles region expansion gracefully (no migration test exists to run)
- Whether `find_path()` Dijkstra performance is acceptable at 100 regions (only BFS was analyzed in detail)
- Exact LRU cache hit rate for `get_distance()` under realistic AI play patterns

---

## Working Assumption

Session 8 renderer work can continue on the current 19-region shell. Full Europe wiring should not start until items 1-8 from the "Before Europe Wiring" roadmap have been completed. Estimated effort for the pre-wiring items: 2-3 focused sessions.
