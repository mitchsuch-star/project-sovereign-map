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
- **Counter-evidence:** `find_weighted_path()` at `world_state.py:2140` uses Dijkstra, which is better. But `find_path()` (line 2099) is also BFS, and `get_distance()` is the hot call — both use naive BFS with `queue.pop(0)`. *(Corrected in Verification Pass: original audit incorrectly stated find_path uses Dijkstra.)*
- **Scale impact:** 19 regions: ~16K BFS steps/turn. 100 regions: ~256K steps/turn (16x). At Python speed (~50-100us/step): 2-4 seconds per AI turn.
- **Fix direction:** LRU/manual cache on `get_distance()` with symmetric keys. Replace `queue.pop(0)` with `collections.deque.popleft()`. Treat the cache as adjacency-topology-only: ordinary controller changes do **not** invalidate it, and any future invalidation seam should be tied to adjacency edits rather than capture. Consider all-pairs precomputation at load time for maps under 150 regions.
- **Blocker class:** Must fix before Europe wiring

### F2. Omniscient AI — 69 Direct Marshal Scans Bypassing Fog

- **Severity:** Critical
- **Category:** AI quality / fairness problem
- **Visibility:** Already visible now (AI sees fogged enemies), certain to worsen at scale
- **Evidence:** As of April 17, 2026, `backend/ai/enemy_ai.py` has 69 direct `world.marshals.values()` / `marshals.values()` scans. Examples include defender detection, force density, blocking enemies, ally threats, and adjacent-strength checks. The fog-aware seam (`_get_enemy_contacts()`) exists, but `_should_use_fog_aware_enemy_query()` still only activates it for the player nation; enemy nations fall back to omniscient `get_enemies_of_nation()`.
- **Counter-evidence:** The seam already acknowledges that the current intel model is player-perspective only. Infrastructure exists for player-facing fog, but the live AI visibility path is not generalized yet.
- **Scale impact:** Fairness asymmetry grows with map size (more hidden information). Cost remains high because dozens of AI paths still linearly rescan the full marshal set.
- **Fix direction:** Build spatial index access through helper seams, not private-cache reads from AI code. Then add a lightweight nation-perspective **live** visibility helper for AI decision-making; do **not** expand this phase into a serialized per-nation intel/history system.
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
- **Evidence:** 6 hardcoded `== 19` assertions across 4 test files: `test_conftest_factories.py:124,162`, `test_economy_foundations.py:148`, `test_systems_audit_session8.py:280`, `test_terrain_data_layer.py:253,290`. *(Verification Pass correction: original audit found only 2 in 2 files.)*
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

### F18. War Cascade Has No Depth Limit *(Verification Pass)*

- **Severity:** Major
- **Category:** Game design / pacing problem
- **Visibility:** Only at Europe scale (5 nations can't form deep alliance chains)
- **Evidence:** `diplomacy.py:2242-2341` — `_process_war_cascade()` recurses through alliance chains. Loop protection via `processed` set (line 2256) prevents revisiting a nation, but there is no depth limit. At 10+ nations with interlocking alliances (A allied with B, B allied with C, C allied with D…), a single `declare_war()` can cascade through the entire diplomatic graph in one turn. Each cascade step calls `set_diplomatic_state()` (line 2290) and can trigger sub-cascades (lines 2341, 2417). Comment at line 2254 acknowledges: "max cascade depth = number of nations."
- **Counter-evidence:** The `processed` set prevents infinite loops. At 5 nations cascade is bounded. The problem is not correctness but gameplay coherence at 10+ nations.
- **Scale impact:** One war declaration → 8-12 new wars in a single turn → player loses control of diplomatic situation. Combined with CC1 (dispatch spam), one action produces 30-50 events.
- **Fix direction:** Design decision: cap cascade depth at 2 levels? Batch cascade notifications ("Coalition forms: X, Y, Z join war against France" instead of N separate events)? Require ally confirmation before joining cascade (1-turn delay)?
- **Blocker class:** Must fix before Europe wiring

### F19. Dispatch Has No Event Volume Cap *(Verification Pass)*

- **Severity:** Major
- **Category:** Renderer / UI density problem + Game design / pacing problem
- **Visibility:** Only at Europe scale
- **Evidence:** `dispatch.py` — `queue_dispatch_event()` appends to `pending_dispatch_events` with no size cap. `_build_diplomatic_events_section()` iterates all queued events. At 10+ nations, each turn can generate: AI-AI proposals, cascade notifications, rivalry shifts, trade income changes, coalition friction updates, vassal loyalty changes. Combined with F18 (war cascade), a single active turn can produce 30-50 dispatch lines.
- **Counter-evidence:** At 5 nations, dispatch volume is 5-10 events per turn — readable and useful.
- **Scale impact:** Morning dispatch becomes a wall of text. Player can't find what matters. JSON payload balloons to 50KB+.
- **Fix direction:** Cap dispatch queue at ~20 events/turn. Batch similar events ("3 nations join coalition" not 3 separate lines). Add priority filtering: show Critical events always, collapse Minor events into a summary line.
- **Blocker class:** Fix during first Europe prototype

### F20. Coalition Adjacency Friction Tuned for Sparse Maps *(Verification Pass)*

- **Severity:** Major
- **Category:** Pacing / scenario-tuning problem
- **Visibility:** Only at Europe scale
- **Evidence:** `coalition.py:408-425` applies friction (relation degradation) between adjacent enemy nations. The friction value was tuned for 19 regions where most nations have 1-2 adjacencies. At 80+ regions with 10+ nations, most nations border 3-5 others. Every adjacent non-allied pair degrades toward conflict every turn.
- **Counter-evidence:** Friction has scaling factors (1.0-0.25 range). But the base rate assumes sparse adjacency.
- **Scale impact:** At Europe density, friction creates a perpetual war machine. The player cannot diplomatically stabilize neighbors because adjacency friction constantly degrades relations faster than diplomacy can repair them.
- **Fix direction:** Scale friction inversely with adjacency count (more neighbors = less friction per neighbor). Or cap total friction received per nation per turn. Design decision needed.
- **Blocker class:** Fix during first Europe prototype

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
- **Evidence:** As of April 17, 2026, `backend/ai/enemy_ai.py` still has 69 direct marshal scans bypassing fog-aware helper seams. Only the player nation currently uses the fog-aware contact path; the AI generalization still needs a nation-perspective live visibility helper.
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
- **Status:** New missing risk — **hardcoded region count in tests** (6 assertions in 4 files, not 2 as originally reported). Would break on any map expansion.
- **Status:** New missing risk — **no adjacency connectivity test**. Could introduce isolated regions in a larger map without detection.
- **Status:** New missing risk (Verification Pass) — **war cascade has no depth limit** (F18). Recursive alliance cascade at `diplomacy.py:2242` can turn one war declaration into world war at 10+ nations.
- **Status:** New missing risk (Verification Pass) — **dispatch has no event volume cap** (F19). At 10+ nations, morning dispatch becomes unreadable wall of text.
- **Status:** New missing risk (Verification Pass) — **coalition adjacency friction tuned for sparse maps** (F20). At Europe density, friction creates perpetual war between all neighbors.

---

## 5. Blocker Ranking

Ranked from highest to lowest expansion risk *(updated by Verification Pass)*:

| Rank | Finding | Why | Status |
|------|---------|-----|--------|
| 1 | **F1: Uncached BFS pathfinding** | 2-4 second AI turns at 100 regions. Hard performance wall. | NOT DONE — no cache on `get_distance()` |
| 2 | **F2: Omniscient AI (69 direct scans bypassing fog)** | Unfair + expensive. Dozens of raw marshal scans still bypass indexed/fog-aware seams. | PARTIAL — `_marshals_by_region` index exists at `world_state.py:1249` but enemy_ai.py doesn't use it and AI fog still needs a live visibility helper |
| 3 | **F3: 5-nation roster hardcoded** | Cannot add nations without cascading config + content work. | NOT DONE |
| 4 | **F18: War cascade no depth limit** | One `declare_war()` → world war at 10+ nations. Design decision needed. | NOT DONE *(Verification Pass addition)* |
| 5 | **F4: Frontend adjacency duplication** | 6-7 files per region. Drift guaranteed at 80+ regions. | NOT DONE |
| 6 | **F8: Turn limit hardcoded at 40** | Campaign unwinnable at Europe scale. Trivial to fix but must be decided. | NOT DONE |
| 7 | **F10: Action economy doesn't scale** | 4 APs insufficient for 80-120 regions. Design decision, not code blocker. | NOT DONE — downgraded to "Fix during prototype" |
| 8 | **F14/F15/F17: Test gaps** | Silent regression when map changes. 6 hardcoded `== 19` assertions. | NOT DONE |
| 9 | **F19: Dispatch event volume** | Morning dispatch becomes unreadable at 10+ nations. | NOT DONE *(Verification Pass addition)* |
| 10 | **F20: Coalition friction tuning** | Adjacency friction creates perpetual war on dense maps. | NOT DONE *(Verification Pass addition)* |
| 11 | **F5: Nation colors scattered** | 3+ edits per nation. Linear cost growth. | NOT DONE |
| 12 | **F6: Full map rebuild** | Performance concern, not a crash risk. | NOT DONE |
| 13 | **F7/F9: UI density (marshal mgmt, ledger)** | Unusable at 40+ marshals but doesn't block wiring. | NOT DONE |

---

## 6. Phased Roadmap

*(Status column added by Verification Pass — April 16, 2026)*

### Before Europe Wiring

These must be done before adding regions beyond 19:

1. **Add test guardrails FIRST** — Nation config completeness test, parametric region count test, adjacency connectivity test. Safety net before structural changes. (~1 hour) **NOT DONE**
2. **Fix hardcoded region count in tests** — Replace `== 19` with `== len(REGIONS_DATA)` in 6 assertions across 4 files. (~30 min) **NOT DONE**
3. **Cache `get_distance()`** — LRU/manual cache with symmetric keys. Replace `queue.pop(0)` with `deque.popleft()`. Tie invalidation to adjacency/topology edits, not ordinary region capture. (~2 hours) **NOT DONE**
4. **Wire spatial index into AI** — `_marshals_by_region` index already exists (`world_state.py:1249`). Replace the current 69 direct marshal scans in `backend/ai/enemy_ai.py` with indexed lookups via AI-safe region helpers, not direct private-cache reads. (~4 hours) **PARTIAL — index exists, AI doesn't use it**
5. **Extend live visibility to all AI nations** — Replace omniscient `get_enemies_of_nation()` usage on scale-sensitive AI paths with a nation-perspective live visibility helper. Do **not** expand this phase into a serialized per-nation intel/history system. (~4-6 hours) **NOT DONE**
6. **Make nation config extensible** — Sensible defaults for new nations in all 5 config surfaces. Factory pattern for marshals/diplomats. (~1 session) **NOT DONE**
7. **Eliminate frontend adjacency duplication** — Frontend loads adjacency from backend API or shared JSON asset. (~4 hours) **NOT DONE**
8. **Design decision: turn limit, AP, and victory scaling** — Make `max_turns` and base AP scenario-configured. Decide formula or per-scenario constant. This is a design gate, not just code. (~2 hours for code, design decision needed first) **NOT DONE**
9. **Design decision: war cascade depth policy** — Cap cascade depth at 2 levels, or add 1-turn ally confirmation delay, or batch cascade into single event. Affects gameplay feel at 10+ nations. (~2 hours for code, design decision needed first) **NOT DONE** *(Verification Pass addition)*

### During First Europe Prototype

These should be addressed while building the first 80+ region map:

10. **Centralize nation colors** — Single source (utils.gd or backend), all files import. (~2 hours) **NOT DONE**
11. **Fix prompt fallback** — Import from REGIONS_DATA.keys() instead of hardcoded string. (~30 min) **NOT DONE**
12. **Align validator VALID_NATIONS** — Derive from NATION_CAPITALS at import time. (~15 min) **NOT DONE**
13. **Incremental map updates** — Region-scoped rebuild instead of full clear+recreate. (~4 hours) **NOT DONE**
14. **Marshal management pagination** — Paginated cards, lazy-load relationships. (~1 session) **NOT DONE**
15. **Strategic ledger sectioning** — Split by location/status, collapse by default. (~4 hours) **NOT DONE**
16. **Victory condition scaling** — Dynamic fraction or alternative conditions for larger maps. (~2 hours) **NOT DONE**
17. **Dispatch event batching + cap** — Cap dispatch queue at ~20 events/turn. Batch similar events. Priority filtering for Critical vs Minor. (~4 hours) **NOT DONE** *(Verification Pass addition)*
18. **Coalition friction density scaling** — Scale adjacency friction inversely with neighbor count, or cap total friction per nation per turn. (~2 hours) **NOT DONE** *(Verification Pass addition)*

### After Europe Map Exists

These can wait until after the first playable Europe prototype:

19. **Tooltip caching** — Cache tooltip text, regenerate only on data change. (~2 hours) **NOT DONE**
20. **Coalition parameter scaling** — Adjust threat/friction for 10+ nations (beyond F20 friction fix). (~2 hours) **NOT DONE**
21. **All-pairs distance precomputation** — Floyd-Warshall at load time for O(1) lookup. (~4 hours) **NOT DONE**
22. **Save file migration** — Handle loading 19-region saves into 80-region world. (~4 hours) **NOT DONE**
23. **Diplomatic ledger collapsibles** — Collapsible AI relations sections. (~2 hours) **NOT DONE**

---

## 7. Confidence Statement

### Directly Verified

- BFS implementation and lack of caching (`world_state.py:2029-2054`)
- `get_distance()` call count in enemy_ai.py (32+ sites counted)
- Omniscient `world.marshals.values()` scan count in enemy_ai.py (59)
- Fog-aware path only for player nation (`enemy_ai.py:485-487`)
- Nation config limited to 5 nations across all 5 surfaces
- Frontend adjacency hardcoded separately from backend
- Nation colors duplicated in 3+ Godot files
- Marshal management keyboard shortcuts capped at 9
- Turn limit at 40, victory at 75%, AP at 4
- Test hardcoded region count `== 19` in 4 files (6 assertions)
- Validator VALID_NATIONS mismatch with nation_config
- Current renderer builds placeholder visual + lookup textures from circle metadata rather than loading commissioned bitmap assets
- Current province-definition schema only includes `anchor`, `radius`, `lookup_color`, and `visual_tint`

### Strong Inference

- Turn time estimate of 2-4 seconds at 100 regions (based on BFS step count x Python overhead; not benchmarked)
- Full map rebuild staying under 16ms at 100 regions in Godot (based on node count estimate; not benchmarked)
- Marshal authoring not scaling (based on 470-line function structure; no automated alternative exists)
- Coalition formation becoming trivial at 10+ nations (based on threshold analysis; not simulated)

### Not Verified

- Actual Godot frame-time impact of 200-500 node rebuilds (no Godot runtime in audit environment)
- Whether tooltip O(n^2) relationship scan causes visible frame drops at scale
- Whether save file loading handles region expansion gracefully (no migration test exists to run)
- Whether `find_weighted_path()` Dijkstra performance is acceptable at 100 regions (note: `find_path()` is BFS, not Dijkstra — see Verification §Spot-Check F1)
- Exact LRU cache hit rate for `get_distance()` under realistic AI play patterns
- Whether a commissioned visual map + province lookup image pair will survive the real asset pipeline without dimension/export mismatches

---

## 8. Verification Pass

> Date: April 16, 2026
> Verifier: Independent review of 6-agent parallel audit
> Method: Spot-checked 5 critical/major findings against source code, searched for cross-cutting risks and game design gaps

### Spot-Check Results

**F1 (Uncached BFS) — CONFIRMED with factual error.**
The BFS at `world_state.py:2029` with `queue.pop(0)` is real. 32 `get_distance()` call sites in enemy_ai.py confirmed. However, the audit's counter-evidence is **wrong**: it states "`find_path()` at `world_state.py:2099-2197` uses Dijkstra." In fact, `find_path()` (line 2099) also uses BFS with `queue.pop(0)` (line 2126). The Dijkstra implementation is a separate method: `find_weighted_path()` at line 2140. The "Not Verified" entry at line 370 ("Whether `find_path()` Dijkstra performance is acceptable") is based on a false premise — there is no Dijkstra in `find_path()`. **Situation is slightly worse than stated**: both primary pathfinding methods are naive BFS.

**F2 (Omniscient AI) — CONFIRMED, underestimated.**
The audit claims "40+ direct `world.marshals.values()` scans." As of April 17, 2026, the current count is **69 direct scans** (grep-verified). The fog-aware `_get_enemy_contacts()` cache exists but only covers the enemy-contacts query path, and `_should_use_fog_aware_enemy_query` still limits that path to the player nation. The direct scans are spread across scoring, movement eval, targeting, and formation code, so the audit correctly identified the seam but underestimated the scope of bypass.

**F3 (5-nation hardcoding) — CONFIRMED, fairly stated.**
`nation_config.py:43-53` builds `RUNTIME_NATIONS` from all 5 config surfaces — the validation architecture (`validate_runtime_nation_support()`) is sound. The real blocker is content authoring: `create_player_marshals()` and `create_enemy_marshals()` are 470-line hand-authored functions. Confirmed as-described.

**F8 (Turn limit at 40) — CONFIRMED.**
`world_state.py:125`: `self.max_turns: int = 40`. Instance field, trivially changeable. Correctly identified.

**F10 (AP doesn't scale) — CONFIRMED but severity overstated.**
`nation_config.py:27-33` defines AP per nation. The audit ranks this "Must fix before Europe wiring" — but it's a design decision plus a trivial config change, not a structural blocker. Should be "Fix during first Europe prototype" (decision gate, not code gate).

### Cross-Cutting Risks Missed

These risks only appear at the intersection of areas the parallel agents audited independently.

**CC1. War cascade × dispatch spam compound.**
War cascade at `diplomacy.py:2242` is recursive with no depth limit (only loop protection via `processed` set, line 2256). Each cascade step generates dispatch events. At 10+ nations with interlocking alliance chains, a SINGLE `declare_war()` call could cascade into 8-12 new wars, each producing 3-5 dispatch events. The dispatch system (`dispatch.py`) has no queue size cap. Combined: one player action → 30-50 dispatch events in a single turn → UI overwhelm + JSON payload bloat. Neither the AI agent nor the UI agent caught this because cascade lives in diplomacy and dispatch lives in the morning-briefing pipeline.

**CC2. Bilateral diplomacy pair explosion × AI per-turn processing.**
At 5 nations: 10 bilateral pairs. At 15 nations: 105 pairs. Each pair maintains `diplomatic_states`, `war_scores`, `nation_relations`, `armistice_cooldowns`, and `proposal_metadata`. Trade income at `diplomacy.py:2823` iterates all pairs. AI diplomacy (`ai_diplomacy.py:570`) runs full proposal evaluation per AI nation per turn. Coalition rivalry (`ai_diplomacy.py:1211`) checks all AI-AI pairs for adjacency degradation. Combined: 10 AI nations × (war score + proposal eval + cooldown check) × coalition member checks = hundreds of function calls per turn. The pathfinding agent flagged get_distance cost; the scenario agent flagged AP tuning; neither caught that **diplomacy itself** is O(N²) per turn.

**CC3. Vassal count × war cascade recursion.**
No vassal count limit exists in `vassal.py:50-97`. France historically had 10+ satellite states; the code allows unlimited. Vassals auto-enlist in their lord's wars (`diplomacy.py:2350`). With 10+ vassals, each potentially having their own alliance chains, a single war declaration triggers recursive cascade through vassal→alliance→vassal chains. Combined with CC1, this is the most explosive single-action risk at Europe scale.

### Game Design Gaps Not Considering Europe

The audit focused on code scaling but missed several places where the **game design itself** was built for 5 nations and won't produce coherent gameplay at Europe scale, regardless of performance:

**GD1. No supply-line mechanic — breaks Napoleonic core at 80+ regions.**
Supply at `world_state.py:2661-2728` is purely local: `base_cap = region.supply_capacity`. No distance-from-capital penalty, no supply-route vulnerability, no interdiction. At 80+ regions, a 50K army sustains identically whether adjacent to Paris or deep in Russia. This removes the central strategic tension of Napoleonic warfare (overextension). The audit flagged supply_capacity as a tuning value but missed that the design lacks the distance dimension entirely.

**GD2. Diplomacy assumes the player manages all bilateral relationships.**
The diplomatic ledger, Talleyrand advisory, and proposal system present every nation as an individual bilateral relationship. At 5 nations this is 4 relationships to track. At 15 nations it's 14 — and the AI generates proposals from each one. The player drowns in individual nation-by-nation diplomacy when the historical period featured regional blocs, spheres of influence, and Congress-system collective diplomacy. No grouping, no regional bloc mechanics, no "deal with all of Iberia at once."

**GD3. Coalition rivalry tuned for sparse maps becomes pathological on dense maps.**
Coalition friction at `coalition.py:408-425` applies -3 relation per turn for adjacent enemy nations. At 19 regions, most nations have 1-2 adjacencies. At 80+ regions with 10+ nations, most nations border 3-5 others. The friction mechanism assumes sparse adjacency; at Europe density, ALL non-allied neighbors degrade toward war every turn, creating a perpetual war machine that the player cannot diplomatically stabilize.

**GD4. Victory conditions assume a single dominant adversary.**
Victory at 75% regions (`world_state.py:60`) and the capital-capture/army-elimination checks (`turn_manager.py:867-942`) assume France vs. a coalition. At 10+ nations with independent wars, the player could control 40% of Europe and still be nowhere near victory while 3 AI nations fight each other over the other 60%. The victory model needs "hegemony" or "Congress peace" conditions, not raw territorial percentage.

**GD5. Morning dispatch becomes a news ticker, not a strategic briefing.**
Dispatch (`dispatch.py`) collects all turn events and presents them. At 5 nations: 5-10 events, readable. At 10+ nations with active diplomacy: 30-50 events per turn including AI-AI proposals, cascade notifications, rivalry shifts, trade income changes. The dispatch design assumes "few important events per turn" — at Europe scale it's a wall of text where the player can't find what matters.

**GD6. Talleyrand advisory becomes generic at 10+ nations.**
Talleyrand's threat assessment and action recommendations (`diplomatic_advisory.py`) evaluate each nation individually. At 5 nations, "I recommend we approach Prussia" is actionable advice. At 15 nations, Talleyrand recommends 8 different approaches and the advice loses strategic clarity. The advisory system has no concept of prioritization or "these 3 nations matter most right now."

### Blocker Ranking Challenges

| Finding | Audit Rank | Verification Assessment | Reason |
|---------|-----------|------------------------|--------|
| F1 (BFS) | #1 Critical | **Confirmed #1** | Worse than stated (find_path also BFS, 59 not 40 marshal scans) |
| F2 (Omniscient AI) | #2 Critical | **Confirmed #2** | 59 scans, not 40+. Underestimated. |
| F10 (AP scaling) | #6, "Must fix" | **Downgrade to "Fix during prototype"** | Design decision, not code blocker. Trivial config change. |
| War cascade depth | Not ranked | **Should be Major, rank 5-6** | Recursive with no depth limit. World-war-in-one-turn at 10+ nations. |
| Bilateral O(N²) | Not ranked | **Should be Major, rank 6-7** | 105 pairs at 15 nations, each with per-turn processing. |
| Supply design gap | Not ranked | **Should be noted as design gate** | No supply-line mechanic breaks Napoleonic core. Not a code fix. |

### Roadmap Ordering Issues

1. **Item 7 (test guardrails) should come FIRST, not 7th.** Adding regression tests before structural changes (BFS caching, spatial index, fog extension) is basic safety. Refactoring pathfinding without tests covering current behavior invites silent breakage.

2. **Item 6 (scale turn limit/AP) is a design decision, not an implementation task.** The AP and turn-limit choices affect how aggressively AI optimization (items 1-3) needs to perform. If turns double from 40→80, AI turn time tolerance also doubles. This decision should be a gate BEFORE optimization work, not after.

3. **Item 4 (nation config extensible) is blocked on game design decisions** not in the roadmap: which nations, how many marshals each, what starting relationships. The code factory pattern is straightforward; the content design is the actual dependency.

4. **Missing: design gate for Europe-scale diplomacy model.** The roadmap assumes the current bilateral diplomacy system carries forward unchanged. Before items 1-8, the project needs a design decision: does Europe use the same bilateral N² model, or does it need regional blocs / spheres of influence? This decision affects how many nations the code must support, which determines the urgency of items 1-3.

### Most Dangerous Assumption

**The audit treats Europe scaling as a code problem. It is fundamentally a game design problem.**

The audit's implicit frame: "The game mechanics work correctly at 5 nations; we just need faster code and more extensible data for 15 nations." This is wrong. Several core mechanics — bilateral diplomacy, war cascade, supply, victory conditions, dispatch volume, advisory clarity, coalition rivalry friction — were **designed** for a 5-nation theater. Making the code run efficiently on 100 regions doesn't help if:

- The diplomacy system presents 105 bilateral relationships to manage (GD2)
- Every war declaration cascades into world war (CC1/CC3)
- Supply lines don't exist so geography is irrelevant (GD1)
- The morning dispatch is unreadable (GD5)
- Coalition friction makes perpetual war inevitable (GD3)

The most dangerous path is optimizing BFS and extending fog (the audit's top recommendations) while leaving the game design unchanged — producing a fast, fair, and completely unplayable Europe campaign.

**Recommendation:** Before the "Before Europe Wiring" roadmap begins, add a **Design Gate: Europe Diplomacy & Pacing Model** that decides: bilateral vs. bloc diplomacy, supply-line existence, cascade depth policy, victory condition type, and dispatch prioritization strategy. The code roadmap should follow from those design decisions, not precede them.

---

## 9. EU4-Style Bitmap Map Readiness Addendum

> Date: April 16, 2026
> Scope: Compare the current Session 8 placeholder renderer with the intended EU4-style bitmap province pipeline.

### External Reference Check

The online cross-check matches the project's internal roadmap direction:

- EU4 modding tutorials consistently treat `provinces.bmp`, `definition.csv`, and `positions.txt` as separate but paired map inputs. The province bitmap carries the unique RGB regions; the definition file maps those RGB values; the positions data separately places units/labels/cities.
- The EU4 community map references also warn against anti-aliasing and blurred brush edges on province maps because stray colors break province identification.

Reference links:

- Steam guide: https://steamcommunity.com/sharedfiles/filedetails/?id=681319197
- Xylozi EU4 tutorial (adding provinces): https://xylozi.wordpress.com/eu4/adding-provinces/
- Xylozi EU4 tutorial (`positions.txt`): https://xylozi.wordpress.com/eu4/reference-positions-txt/
- EU4 community wiki mirror (map files): https://www.eu4cn.com/wiki/%E5%9C%B0%E5%9B%BE%E4%BF%AE%E6%94%B9
- EU4 community wiki mirror (mod file structure): https://www.eu4cn.com/wiki/Mod%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84

### What Is Already Ready

- **The color-map hover model is already correct.** `map_renderer_base.gd:1067-1079` samples `province_lookup_image.get_pixel(...)` and resolves a region through `province_color_lookup`. That is the right O(1) interaction pattern for a Paradox-style province map.
- **The camera/input architecture is already good enough to keep.** The current renderer already uses `SubViewport` + `Camera2D`, so zoom/pan/input do not need another architectural reset before commissioned art lands.
- **The placeholder asset tests do prove the basic lookup contract.** `tests/test_map_placeholder_assets.py` verifies 19-region coverage, unique lookup colors, and anchor alignment against the fallback map positions.

### New Map Findings

**M1. The renderer proves the lookup concept, not the production asset pipeline.**

- **Severity:** Critical
- **Category:** Renderer / asset-pipeline readiness
- **Evidence:** `map.gd:3` still hardcodes `session8_placeholder_provinces.json`. `map_renderer_base.gd:261-282` synthesizes both the visible map and the lookup image by drawing circles from `anchor` + `radius`; it does not load an artist-delivered visual map plus a pixel-aligned province bitmap.
- **Why it matters:** The real EU4-style failure cases are asset-ingest failures: wrong dimensions, stray RGB values, bad export settings, and artist/backend drift. The current placeholder path bypasses all of them.
- **Fix direction:** Replace generated textures with external visual + lookup image loading while preserving the current `get_pixel()` lookup path.
- **Blocker class:** Must fix before commissioned Europe map integration

**M2. The province metadata schema is too thin for Europe-density presentation.**

- **Severity:** Critical
- **Category:** Renderer / content-schema readiness
- **Evidence:** `_build_province_shapes()` only reads `anchor`, `radius`, `lookup_color`, and `visual_tint` (`map_renderer_base.gd:235-245`). Grep verification found no `province_id`, `playable`/`unplayable`, or separate label/unit/garrison anchor fields in the renderer, placeholder JSON, or map tests.
- **External reference:** EU4-style map tooling keeps province definition separate from positions data; the `positions.txt` tutorial shows distinct coordinates for city, unit, and province-name text.
- **Why it matters:** A Europe map with 80-100 playable provinces and greyed-out edge provinces cannot reliably place stacks, garrisons, labels, buildings, and future ports off one shared anchor.
- **Fix direction:** Expand the province registry before art handoff: stable `province_id`, `unit_anchor`, `label_anchor`, `garrison_anchor`, `building_anchor`, and an `interactive`/`wired` flag at minimum.
- **Blocker class:** Must fix before commissioned Europe map integration

**M3. There is no automated validation for final bitmap deliverables.**

- **Severity:** Critical
- **Category:** Tooling / asset-validation readiness
- **Evidence:** `tests/test_map_placeholder_assets.py` only checks JSON coverage, anchor alignment, and unique lookup colors. `tests/test_map_renderer_cutover.py` asserts that the sampling code exists, but it never inspects a real bitmap asset pair.
- **External reference:** EU4 map references warn that province RGB values must exactly match the definition data and that anti-aliasing / blurred brush edges create invalid province pixels.
- **Why it matters:** A single anti-aliased border, wrong export mode, or unexpected RGB pixel can create silent hover holes or misidentified provinces.
- **Fix direction:** Implement the roadmap's planned validator before artist integration: verify exact dimension match, every bitmap color exists in the JSON, every JSON province appears in the bitmap, no unexpected colors exist, no province uses the sentinel color, and tiny stray pixel islands are flagged as likely export artifacts.
- **Blocker class:** Must fix before commissioned Europe map integration

**M4. Greyed-out non-playable provinces are a design requirement, but not yet represented in runtime data.**

- **Severity:** Major
- **Category:** Renderer / UX readiness
- **Evidence:** `docs/ROADMAP.md` explicitly plans 120-150 outlined provinces with only 80-100 wired for EA v1 and expects greyed-out unwired provinces. Current renderer data is keyed off active backend region names plus the placeholder JSON; there is no province-level `interactive`/`wired` state in the schema or `update_all_regions()` contract (`map_renderer_base.gd:1631-1669`).
- **Why it matters:** The commissioned Europe map is supposed to show more geography than the first gameplay build actually supports. That distinction does not exist yet.
- **Fix direction:** Add province registry metadata for `wired`, `visible`, and `ignore_input`, then make hover/click logic explicitly reject unwired provinces while still rendering them.
- **Blocker class:** Must fix before Europe art integration

**M5. Shared province topology is still split across frontend placeholder data and backend gameplay data.**

- **Severity:** Major
- **Category:** Data-model / content-coupling problem
- **Evidence:** `map.gd:30-69` still hardcodes `REGION_CONNECTIONS` and fallback positions, while the backend remains authoritative for actual gameplay region data. This was already a risk at 19 regions; it becomes worse once the art contains visible straits, coastline cues, and greyed-out provinces that the frontend can "see" but gameplay may not support.
- **Why it matters:** On a Paradox-style map, visible geography feels authoritative. If straits, coast touches, or border contact disagree with gameplay adjacency, the map teaches the player the wrong rules.
- **Fix direction:** Finish F4 and move adjacency / strait / topology data to a shared province registry or backend-fed payload before the Europe map lands.
- **Blocker class:** Must fix before Europe wiring

### Map-Specific Roadmap Insert

Add these items before commissioned Europe art integration:

1. **Introduce a production province registry schema** — stable province IDs, separate anchors, unwired-province flags, label metadata. (~2-4 hours)
2. **Load external visual + lookup images instead of generating circle textures** — keep the current pixel-sampling logic, replace only the placeholder asset path. (~1 session)
3. **Ship the color-map validator before artist handoff** — fail fast on unknown RGBs, dimension mismatch, sentinel misuse, and anti-alias artifacts. (~2 hours)
4. **Support greyed-out visible-but-unwired provinces in the renderer contract** — render them, ignore clicks, and keep them out of `map_data`. (~2 hours)
5. **Unify adjacency/topology data before Europe map import** — no second hardcoded frontend graph. (~4 hours)

### Updated Readiness Statement

The project is directionally aligned with an EU4-style province map: hidden color-map hit detection, camera-based navigation, and placeholder province definitions are already in place. But it is **not yet ready to ingest a commissioned Europe bitmap map safely**. The missing work is not "figure out hover by color" -- that part is already done. The missing work is the production pipeline: real asset loading, richer province metadata, automated bitmap validation, unwired-province handling, and a single shared topology source.

---

## 10. Working Assumption

Session 8 renderer work can continue on the current 19-region shell. Full Europe wiring should not start until items 1-9 from the "Before Europe Wiring" roadmap have been completed. Estimated effort for those pre-wiring items remains 2-3 focused sessions.

**Verification addendum:** The pre-wiring roadmap should be preceded by a Europe design gate covering diplomacy model, supply mechanics, cascade policy, and victory conditions. Without design decisions first, the code changes risk optimizing toward a game model that doesn't work at scale.

**Renderer addendum:** Commissioned Europe art should not be integrated until the province registry, bitmap validator, and unwired-province contract from Section 9 exist. Otherwise the team will be debugging asset-pipeline failures at the same time it is trying to validate first-pass Europe gameplay.

---

## 11. Verification Delta — April 19, 2026

> Independent re-audit of HEAD (master @ Phase 2 closeout). Supersedes the stale
> "NOT DONE" / "PARTIAL" status labels in §§3, 5, 6 for the Phase 2 items.

### What changed on HEAD since the April 16 audit

- **F1 (Uncached BFS) — RESOLVED.** `backend/models/world_state.py:2116` now ships a symmetric-keyed distance cache (`_distance_cache` at line 105, `_make_distance_cache_key` at line 2151, explicit `invalidate_distance_cache()` at line 2157). `queue.pop(0)` is gone — `popleft()` is used in `get_distance` (line 2134), `find_path` (line 2098), and `find_weighted_path` (line 2231). Plan §2.1's 100-region synthetic benchmark now ships as `tools/benchmark_distance_cache.py` (10x10 4-neighbor grid) and measured ~34x speedup cached vs. uncached on developer hardware. The adjacency-topology-only invariance contract is pinned by three new tests in `tests/test_scale_readiness_phase2.py` (`test_distance_cache_scales_to_100_region_synthetic_graph`, `test_distance_cache_is_adjacency_topology_only_on_100_region_graph`, `test_distance_cache_measurably_faster_on_100_region_graph`, 2x conservative lower bound).
- **F2 (Omniscient AI, 69/59 direct scans) — RESOLVED on `enemy_ai.py`.** Grep of `backend/ai/enemy_ai.py` for `world.marshals.values()` / `marshals.values()` returns **0** matches. AI-safe indexed helpers on `WorldState` (`_get_marshals_in_region_indexed` at line 1301, `get_marshals_in_region_indexed` at line 1310, `get_marshals_by_nation` at line 1562, `refresh_marshal_indexes` at line 1269) are the wired call path. Live-visibility seam (`get_live_visible_regions_for_nation` at line 1618, `get_live_visible_enemies` at line 1632) routes scale-sensitive AI contact queries through nation-perspective rules; no serialized per-nation intel history was added, matching the plan's narrow scope. §5 blocker ranking row 2 ("PARTIAL") and §7 "Directly Verified" scan counts are now stale.
- **F11/F16 partial — VALID_NATIONS derivation complete.** `backend/modding/validator.py:73` now derives `VALID_NATIONS` from `NATION_CAPITALS.keys()` (Phase 1 bonus item). `prompt_builder.py:567` and `parser.py:103-108` remain hardcoded — those are Phase 3.4.

### Phase 2 closeout verdict

Phase 2 §§2.1-2.3 are complete on HEAD: code, correctness tests, and plan-required benchmark all land. `enemy_ai.py` is at 0 raw marshal scans. Incremental Phase 2 verification (28 tests) is green; last full-suite verification was `8410 passed, 2 skipped` prior to the benchmark addition.

### Still not done — non-art real-map blockers (Phase 3 + Phase 4)

These items are untouched on HEAD and are the next prerequisites for commissioned Europe-map integration. `SCALE_READINESS_PLAN.md` holds the per-item contract; the short form:

- **Phase 3.1 nation config factory — NOT DONE.** `backend/nation_config.py:19-35` still uses three parallel dicts; `backend/models/marshal.py:1509` still defines hand-authored `create_enemy_marshals()`. No `DEFAULT_NATION_DEFAULTS` dict, no `create_marshals_from_data()` helper.
- **Phase 3.2 shared topology — NOT DONE.** `godot-client/project-sovereign/scenes/map.gd:30-50` still hardcodes a full `REGION_CONNECTIONS` dict duplicated from backend; `map.gd:7-27` still hardcodes all 19 region positions. No `/map_data` endpoint, no shared JSON asset.
- **Phase 3.3 centralize nation colors — NOT DONE.** `map.gd:53-61` still defines a local `COLORS` dict alongside `utils.gd` NATION_COLORS.
- **Phase 3.4 prompt/parser fallback hardcoding — NOT DONE.** `backend/ai/prompt_builder.py:567` still returns the hardcoded 19-region string; `backend/commands/parser.py:103-108` still hardcodes 8 enemy marshal names.
- **Phase 4.1 province registry schema — NOT DONE.** Only `session8_placeholder_provinces.json` exists. No stable `province_id`, no `unit_anchor` / `label_anchor` / `garrison_anchor` / `building_anchor`, no `wired` / `interactive` flags anywhere.
- **Phase 4.2 external bitmap loading — NOT DONE.** No `_load_map_images()` method, no `europe_visual.png` / `europe_provinces.png` assets. Renderer still generates circle textures as the only path.
- **Phase 4.3 color-map validator — NOT DONE.** No `tools/validate_province_map.py`, no `tests/test_province_map_assets.py`.
- **Phase 4.4 unwired province support — NOT DONE.** No `wired` / `interactive` state plumbed through renderer or data contract.

### Out-of-strict-Phase-2-scope follow-ups (surfaced during audit)

- `backend/ai/strategic_parser.py:596` still iterates `world.marshals.values()` in the `SUPPORT` literal-interpretation path. Plan §2.2 explicitly scopes the scan conversion to `backend/ai/enemy_ai.py`, so this is not a Phase 2 contract violation — but it is the one remaining ally enumeration in the AI module that should move to `get_marshals_by_nation()` when Phase 3 work revisits scale-sensitive helpers.
- `strategic_parser.py:585` also falls back to omniscient `get_enemies_of_nation()` for AI nations. Phase 2.3 scopes the fog generalization narrowly to `enemy_ai.py`; this one is a candidate for the same later pass.
