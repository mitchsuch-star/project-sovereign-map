# Europe Scale Readiness — Implementation Plan

> Derived from `SCALE_READYNESS.md` audit (April 16, 2026).
> This document replaces the audit's phased roadmap with a concrete, ordered work plan.
> Each item has files to touch, what to change, dependencies, and estimated effort.

---

## How to Use This Document

Work top-to-bottom within each phase. Phase 0 (design gates) must be complete before Phase 1 code work begins. Within code phases, items are ordered by dependency — later items may depend on earlier ones.

**Estimated total effort:** 8-12 focused sessions across all phases.

---

## Phase 0: Design Gates

These are decisions, not code. Each one affects downstream implementation. Answer them in a short design doc or inline in this file before writing code. No code should be written until all gates in this phase are resolved.

### DG-1. Nation Roster & Starting Situation

**Decision needed:** Which nations ship in EA? How many marshals per nation? What starting diplomatic relationships?

**Why first:** Every other decision (diplomacy model, cascade depth, AP budget, victory conditions) depends on knowing whether this is 8 nations or 15.

**Options to evaluate:**
- **Option A: 8-10 nations** — France, Britain, Prussia, Austria, Russia, Spain, Ottoman Empire, Sweden, plus 1-2 minor (Saxony, Bavaria). Keeps diplomacy manageable.
- **Option B: 12-15 nations** — Add Denmark, Netherlands, Naples, Portugal, Poland. More historically accurate, but diplomacy UI must change.

**Downstream impact:** Determines urgency of bilateral pair explosion fix (CC2), coalition retuning, UI density work.

**DECIDED — April 17, 2026: 13 independent nations, architecture supports 20+.**

Ship with 13 independent nations in three tiers. All systems (diplomacy, dispatch, UI, cascade, AI) must be architected to handle 20+ nations so the roster can grow post-EA without structural rework.

**Tier 1 — Major Powers (5):** France, Britain, Austria, Prussia, Russia. Core antagonists, full marshal rosters, full diplomatic agency.

**Tier 2 — Active Secondary Powers (4):** Spain (French ally → enemy, Peninsular War), Ottoman Empire (eastern tension, Russian pressure), Sweden (Third Coalition, Bernadotte), Naples/Two Sicilies (Italian theater, Murat).

**Tier 3 — Key Minors (4):** Bavaria (France's key German ally, later defection), Saxony (already in-game), Portugal (British ally, invasion target), Denmark-Norway (French ally post-1807).

**As vassals, not independent nations:** Netherlands/Batavian Republic, Poland/Duchy of Warsaw, Württemberg, Switzerland. The existing vassal system handles these — the player creates them through conquest and diplomacy.

**Scale note:** 13 nations = 78 bilateral pairs. Smart filtering (DG-2) keeps this manageable. At 20 nations = 190 pairs — the filtering and dispatch systems (DG-7) must handle this without UI changes.

---

### DG-2. Diplomacy Model — Bilateral vs. Regional Blocs

**Decision needed:** Does the player manage every bilateral relationship, or do nations group into blocs the player interacts with as units?

**Why it matters:** At 5 nations = 4 relationships. At 15 nations = 14 relationships + AI proposals from each. The current Talleyrand advisory, diplomatic ledger, and proposal system all assume individual bilateral management.

**Options:**
- **Option A: Keep bilateral, add smart filtering.** Talleyrand prioritizes top 3-4 threats. Ledger groups nations by relevance. Player still manages individual relationships but the UI helps them focus. Cheaper to implement.
- **Option B: Regional bloc system.** Nations belong to blocs (Iberian, Germanic, etc.). Player proposes to blocs. More historically authentic. Major new system.
- **Option C: Hybrid.** Major powers are bilateral. Minor nations follow their patron's diplomacy automatically (extend vassal-like behavior). Middle ground.

**Affected files if bilateral stays:** `diplomatic_advisory.py` (add prioritization), `diplomatic_ledger.gd` (add grouping/collapse), `ai_diplomacy.py` (throttle AI-AI proposal volume).

**Affected files if blocs:** New `bloc.py` system, rewrite `diplomatic_templates.py`, redesign `diplomatic_ledger.gd`, new bloc proposal flow in `diplomatic_executor.py`.

**Record decision here:** _____________

---

### DG-3. Supply Lines

**Decision needed:** Does supply gain a distance-from-capital dimension?

**Why it matters:** Current supply is purely local (`region.supply_capacity`). A 50K army in Moscow sustains identically to one adjacent to Paris. At 80+ regions this removes the central Napoleonic tension of overextension.

**Options:**
- **Option A: Distance penalty.** Supply capacity degrades with pathfinding distance from nearest friendly supply depot or capital. Simple formula, big gameplay impact.
- **Option B: Supply route vulnerability.** Supply follows a traced path; enemies can interdict it. More complex, more interesting.
- **Option C: Defer to post-EA.** Ship Europe without supply lines, tune attrition higher to simulate. Cheapest but weakest.

**Affected files:** `world_state.py` (process_supply_attrition), `region.py` (supply_capacity), `enemy_ai.py` (AI must consider supply), `strategic_ledger.gd` (show supply status).

**DECIDED — April 17, 2026: Deferred. Build after Europe map is playable.**

Supply lines is a gameplay feature, not a scaling prerequisite. The current local `supply_capacity` per region already applies attrition — armies in distant regions take losses. Distance-from-capital supply would make the game *better* but does not block having a functional Europe map.

**Plan:** Ship Europe with current local supply. After first Europe playtest, evaluate whether the game *feels* like it needs overextension pressure or whether attrition + economy already create it. If needed, implement as a "Campaign Feel" pass — likely Option A (distance penalty) as the simplest high-impact choice.

**No code changes required for map scaling.** The existing `process_supply_attrition` and `region.supply_capacity` work at any region count.

---

### DG-4. War Cascade Depth Policy

**Decision needed:** What happens when declaring war triggers alliance chains at 10+ nations?

**Why it matters:** Current cascade (`diplomacy.py:2242`) is recursive with no depth limit. One `declare_war()` can trigger 8-12 new wars in a single turn, each generating dispatch events. Combined with vassal auto-enlistment, this is the most explosive single-action risk.

**Options:**
- **Option A: Cap cascade depth at 2.** Direct allies join immediately. Allies-of-allies get a "call to arms" that resolves next turn. Simple, predictable.
- **Option B: 1-turn delay for all cascade.** Direct allies get a "call to arms" popup. Player and AI can see it coming. More interactive.
- **Option C: Batch cascade into single event.** All cascade happens instantly but is presented as one "Coalition forms" event instead of N separate war declarations. Keeps mechanics, fixes UX.

**Affected files:** `diplomacy.py` (_process_war_cascade), `dispatch.py` (event batching), `vassal.py` (auto-enlistment depth).

**Record decision here:** _____________

---

### DG-5. Victory Conditions

**Decision needed:** What replaces 75% territory control at 100+ regions?

**Current:** `VICTORY_REGION_FRACTION = 0.75` requires 90/120 regions — dominating all of Europe.

**Options:**
- **Option A: Lower fraction + prestige.** 40% territory + war score thresholds + capital control = hegemony victory.
- **Option B: Congress peace.** After enough wars won, trigger a peace congress event. Player wins by negotiating favorable terms.
- **Option C: Multiple victory types.** Domination (territory), Diplomatic (alliances + peace), Military (defeat all major powers). Like Civ victory conditions.

**Affected files:** `world_state.py` (VICTORY_REGION_FRACTION), `turn_manager.py` (victory checks at line 867-942).

**Record decision here:** _____________

---

### DG-6. Pacing — Turn Limit, AP Budget, Campaign Length

**Decision needed:** How long is a Europe campaign? How many actions per turn?

**Current:** 40 turns, 4 AP. At 100 regions: 0.4 turns/region (unwinnable), 4 AP to manage distributed warfare (impossible).

**Options:**
- **Option A: Scale linearly.** `max_turns = region_count * 2`, `base_AP = 4 + (nation_marshal_count // 3)`. Simple.
- **Option B: Scenario-configured.** Each scenario (19-region, Europe) defines its own turn limit and AP. More control.
- **Option C: Remove turn limit.** Victory/defeat by conditions only. AP scales with controlled territory.

**Affected files:** `world_state.py` (max_turns), `nation_config.py` (BASE_NATION_ACTIONS), `turn_manager.py` (time victory check).

**Record decision here:** _____________

---

### DG-7. Dispatch & Information Density

**Decision needed:** How does the player parse 30-50 events per turn?

**Current:** Morning dispatch presents all events in a flat list. At 5 nations this is 5-10 events. At 10+ nations with active diplomacy, war cascades, rivalry shifts, trade income, coalition friction — it's a wall of text.

**Options:**
- **Option A: Priority filtering + cap.** Critical events always shown. Minor events collapsed into summary line ("3 minor diplomatic shifts occurred"). Cap at ~20 visible events.
- **Option B: Categorized sections.** Military events, diplomatic events, economic events — each collapsible. Player reads the section they care about.
- **Option C: Urgent/routine split.** "Urgent" tab (wars, proposals, threats) shown by default. "Routine" tab (trade income, relation drift) available on click.

**Affected files:** `dispatch.py` (queue_dispatch_event, build), `dispatch_view.gd` (rendering), `diplomatic_advisory.py` (Talleyrand prioritization).

**DECIDED — April 17, 2026: Categorized sections with priority escalation. Must handle 20+ nations.**

Hybrid of Options A + B. Dispatches are grouped into themed sections with period-appropriate voices, and events within sections are filtered by priority. This matches how Napoleon actually received information — through different channels and aides.

**Four dispatch sections:**

| Section | Voice | Contains |
|---------|-------|----------|
| **Military Affairs** | Berthier | Battles, movements, retreats, garrison events, attrition, reinforcements |
| **Diplomatic Affairs** | Talleyrand | Proposals, treaty changes, war declarations, coalition shifts, rivalry events |
| **Imperial Treasury** | Narrator | Income, trade, bankruptcy warnings, upkeep, building completion |
| **Intelligence** | Berthier | Fog reveals, scouting results, enemy sightings, watchtower reports |

**Priority tiers (per event, not per section):**

| Priority | Behavior | Examples |
|----------|----------|----------|
| **CRITICAL** | Always shown, expanded | Wars declared on player, proposals requiring response, battles involving player marshals, capital threats, coalition formation |
| **MAJOR** | Shown, collapsed | AI-AI wars near player borders, relation shifts with neighbors, coalition brewing, ally requests |
| **MINOR** | Summarized as count | Distant AI-AI diplomacy, minor trade income, routine relation drift, minor attrition |

**Collapse rules:**
- Sections with zero events are hidden entirely
- MINOR events within a section collapse into a summary line: *"3 minor diplomatic developments occurred"* with expand option
- Cap: if a section exceeds 15 events after filtering, collapse MAJOR events too and show *"8 military developments — expand to review"*
- Empty sections don't render at all (at 5 nations, Treasury and Intelligence may be empty most turns)

**Scale behavior at 20+ nations:**
- At 13 nations: ~15-25 events/turn, most sections have 3-8 items. Manageable.
- At 20 nations: ~30-50 events/turn. MINOR collapse kicks in heavily. Player sees ~12-18 expanded items across 4 sections. Distant AI-AI noise vanishes into summary lines.
- At 30+ nations: Same structure holds. MAJOR collapse may trigger in Diplomatic Affairs. Player focuses on CRITICAL items, drills into sections on demand.

**Implementation approach:**
1. Add `category` field (`military`, `diplomatic`, `treasury`, `intelligence`) and `priority` field (`critical`, `major`, `minor`) to dispatch events in `dispatch.py`
2. `build()` groups events by category, sorts by priority within each group
3. `dispatch_view.gd` renders sections with headers, collapse/expand per section
4. No new UI screens — this replaces the flat list inside the existing dispatch view

**Affected files:** `dispatch.py` (event category/priority fields, grouped build), `dispatch_view.gd` (sectioned rendering, collapse/expand), `campaign_log.py` (event types may need category mapping).

---

## Phase 1: Test Safety Net — Session Spec

**When:** Immediately after Phase 0 decisions are recorded.
**Why:** Regression safety before any structural changes. If BFS caching or fog extension breaks something, these tests catch it.
**Estimated effort:** 1-2 hours.
**Acceptance criteria:** All new tests pass. Full test suite still passes. No hardcoded `19` remains in any test assertion about region/world count.

---

### 1.1 Nation Config Completeness Test

**Create:** `tests/test_nation_config_completeness.py`

**Imports needed:**
```python
from backend.models.region import NATION_CAPITALS, REGIONS_DATA
from backend.nation_config import (
    DEFAULT_NATION_GOLD, BASE_NATION_ACTIONS, DEFAULT_NATION_AUTHORITY,
    RUNTIME_NATIONS, validate_runtime_nation_support,
)
from backend.models.diplomat import STARTING_DIPLOMATS
from backend.models.marshal import create_enemy_marshals
from backend.models.world_state import WorldState
```

**Tests to write (7 tests):**

1. **`test_all_capital_nations_have_gold_config`**
   - For every nation in `NATION_CAPITALS.keys()`, assert it exists in `DEFAULT_NATION_GOLD`
   - Error message: `f"{nation} in NATION_CAPITALS but missing from DEFAULT_NATION_GOLD"`

2. **`test_all_capital_nations_have_action_config`**
   - Same pattern against `BASE_NATION_ACTIONS`

3. **`test_all_capital_nations_have_authority_config`**
   - Same pattern against `DEFAULT_NATION_AUTHORITY`

4. **`test_all_capital_nations_have_diplomat`**
   - For every nation in `NATION_CAPITALS.keys()`, assert it exists in `STARTING_DIPLOMATS`
   - Error message: `f"{nation} has a capital but no starting diplomat"`

5. **`test_all_capital_nations_have_marshals`**
   - Create a fresh `WorldState()` (which calls `create_player_marshals` + `create_enemy_marshals`)
   - For every nation in `NATION_CAPITALS.keys()`, assert at least one marshal has that nation
   - `marshal_nations = {m.nation for m in world.marshals.values()}`
   - Error message: `f"{nation} has a capital but no marshals in default setup"`

6. **`test_validate_runtime_support_passes_current_roster`**
   - `errors = validate_runtime_nation_support(NATION_CAPITALS.keys())`
   - `assert errors == [], f"Current roster fails validation: {errors}"`

7. **`test_runtime_nations_matches_capitals`**
   - `assert set(RUNTIME_NATIONS) == set(NATION_CAPITALS.keys())`
   - Catches case where a nation is added to one surface but not `NATION_CAPITALS`

8. **`test_all_config_surfaces_consistent`**
   - Collect all 5 sets: `NATION_CAPITALS.keys()`, `DEFAULT_NATION_GOLD.keys()`, `BASE_NATION_ACTIONS.keys()`, `DEFAULT_NATION_AUTHORITY.keys()`, `STARTING_DIPLOMATS.keys()`
   - Assert all 5 sets are identical
   - Error message lists which sets differ and which nations are missing where

**Edge case — no false positive on current 5-nation roster:** Every test should pass on the current codebase before any changes. Run the test file first to confirm.

---

### 1.2 Fix Hardcoded Region Count in Tests

**8 assertions across 5 files** (the audit said 6 in 4 files — it missed 2):

| # | File | Line | Current | Replace With |
|---|------|------|---------|--------------|
| 1 | `tests/test_conftest_factories.py` | 124 | `assert len(world.regions) == 19` | `assert len(world.regions) == len(REGIONS_DATA)` |
| 2 | `tests/test_conftest_factories.py` | 162 | `assert len(world.regions) == 19` | `assert len(world.regions) == len(REGIONS_DATA)` |
| 3 | `tests/test_economy_foundations.py` | 148 | `assert len(REGIONS_DATA) == 19` | DELETE this line (the `for` loop on line 149 already validates every region) |
| 4 | `tests/test_systems_audit_session8.py` | 280 | `assert total_regions == 19` | `assert total_regions == len(REGIONS_DATA)` |
| 5 | `tests/test_terrain_data_layer.py` | 253 | `assert len(REGIONS_DATA) == 19` | DELETE this line (the `for` loop on line 254 already validates every region) |
| 6 | `tests/test_terrain_data_layer.py` | 290 | `assert len(regions) == 19` | `assert len(regions) == len(REGIONS_DATA)` |

**Additional hardcoded 19 references (not count assertions but still brittle):**

| # | File | Line | Current | Fix |
|---|------|------|---------|-----|
| 7 | `tests/test_systems_audit_session8.py` | 274 | `assert int(19 * VICTORY_REGION_FRACTION) == 14` | `region_count = len(REGIONS_DATA)` then `assert int(region_count * VICTORY_REGION_FRACTION) == int(region_count * 0.75)` |
| 8 | `tests/test_systems_audit_session12.py` | 70-72 | `threshold = max(1, int(19 * VICTORY_REGION_FRACTION))` / `assert threshold == 14` | `region_count = len(REGIONS_DATA)` then `threshold = max(1, int(region_count * VICTORY_REGION_FRACTION))` / `assert threshold == max(1, int(region_count * 0.75))` |

**Import to add** where needed: `from backend.models.region import REGIONS_DATA`

**Also rename test methods** that reference 19 in their name:
- `test_basic_has_19_regions` → `test_basic_has_all_regions` (`test_conftest_factories.py:122`)
- `test_all_19_regions_have_region_type` → `test_all_regions_have_region_type` (`test_economy_foundations.py:146`)
- `test_all_19_regions_have_terrain` → `test_all_regions_have_terrain` (`test_terrain_data_layer.py:252`)
- `test_threshold_calculation_19_regions` → `test_threshold_calculation_current_regions` (`test_systems_audit_session12.py:69`)

**Terrain distribution test — flag but don't fix now:**
`test_terrain_data_layer.py:267-272` hardcodes exact terrain counts (`plains == 7`, `hills == 4`, etc.). These will break when regions are added, but they're validating current map data, not a structural assumption. Leave them and let them break intentionally when new regions are added — that's what they're for. Add a comment: `# These counts are intentional for the current 19-region map. Update when regions are added.`

**Verification step:** After all edits, run:
```bash
".venv\Scripts\python.exe" -m pytest tests/test_conftest_factories.py tests/test_economy_foundations.py tests/test_systems_audit_session8.py tests/test_terrain_data_layer.py tests/test_systems_audit_session12.py -v
```

---

### 1.3 Adjacency Connectivity Test

**Add to:** `tests/test_map_consistency.py` (existing file, 79 lines currently)

**Tests to write (3 tests):**

1. **`test_adjacency_graph_is_connected`**
   - BFS from any region (e.g., `"Paris"`) using `REGIONS_DATA[region]["adjacent"]`
   - Assert all regions in `REGIONS_DATA` are reachable
   - Error message: `f"Disconnected regions: {unreachable}"`

   ```python
   def test_adjacency_graph_is_connected():
       start = next(iter(REGIONS_DATA))
       visited = set()
       queue = [start]
       while queue:
           current = queue.pop(0)
           if current in visited:
               continue
           visited.add(current)
           for neighbor in REGIONS_DATA[current]["adjacent"]:
               if neighbor not in visited:
                   queue.append(neighbor)
       unreachable = set(REGIONS_DATA.keys()) - visited
       assert not unreachable, f"Regions not reachable from {start}: {unreachable}"
   ```

2. **`test_adjacency_is_bilateral`**
   - Already tested by `test_godot_connections_match_backend_adjacency` for Godot, but not for backend self-consistency
   - For every region A with neighbor B, assert B also lists A as neighbor
   - Error message: `f"{a} lists {b} as adjacent, but {b} does not list {a}"`

   ```python
   def test_adjacency_is_bilateral():
       for name, data in REGIONS_DATA.items():
           for neighbor in data["adjacent"]:
               assert neighbor in REGIONS_DATA, f"{name} lists unknown region {neighbor}"
               assert name in REGIONS_DATA[neighbor]["adjacent"], (
                   f"{name} lists {neighbor} as adjacent, but {neighbor} does not list {name}"
               )
   ```

3. **`test_no_self_adjacency`**
   - No region should list itself as adjacent
   - `assert name not in data["adjacent"], f"{name} lists itself as adjacent"`

**Verification step:** After adding, run:
```bash
".venv\Scripts\python.exe" -m pytest tests/test_map_consistency.py -v
```

---

### 1.4 Validator VALID_NATIONS Fix (bonus — 2 minutes)

While touching test infrastructure, fix the trivial validator drift:

**File:** `backend/modding/validator.py:71`

**Current:**
```python
VALID_NATIONS = {"France", "Britain", "Prussia", "Austria", "Russia", "Spain", "Saxony"}
```

**Replace with:**
```python
from backend.models.region import NATION_CAPITALS
VALID_NATIONS = set(NATION_CAPITALS.keys())
```

**Verify:** Check that the import doesn't create a circular dependency. `validator.py` imports from `region.py`, which has no imports from `modding/`. Safe.

---

### Session Execution Order

1. Write `test_nation_config_completeness.py` (item 1.1)
2. Run it — all 8 tests should pass on current codebase
3. Fix the `== 19` assertions (item 1.2) — all 8 edits + 4 renames
4. Run those 5 test files — all should still pass
5. Add adjacency tests to `test_map_consistency.py` (item 1.3)
6. Run it — all 3 new + 3 existing tests should pass
7. Fix `validator.py` VALID_NATIONS (item 1.4)
8. Run full test suite: `".venv\Scripts\python.exe" -m pytest tests/ -v --tb=short -q`
9. Commit

**Expected new test count:** ~14 new tests (8 config + 3 adjacency + 3 existing map consistency remain)

**Done-done criteria:**
- [x] All new tests pass (11 new: 8 config + 3 adjacency)
- [x] Full suite passes (8,385 passed, 0 failures)
- [x] No hardcoded `19` in any test assertion about region/world count
- [x] `VALID_NATIONS` derives from `NATION_CAPITALS`
- [x] Test method names don't reference `19`

---

## Phase 2: Performance Infrastructure

**When:** After Phase 1 tests pass.
**Why:** The #1 and #2 blockers from the audit. Without these, AI turns take 2-4 seconds at 100 regions, and AI cheats by seeing through fog.
**Estimated effort:** 1-2 sessions.

### 2.1 Cache `get_distance()` + Fix BFS

**Problem:** 32 `get_distance()` calls per marshal per turn, no caching, `queue.pop(0)` is O(n).

**Changes in `world_state.py`:**
1. Replace `queue.pop(0)` with `collections.deque.popleft()` in `get_distance()` (~line 2029) and `find_path()` (~line 2099)
2. Add `@lru_cache` or manual dict cache on `get_distance()`. Key: `(origin, destination)` tuple. The graph is static per turn — only invalidate on region capture (inside `_capture_region()` or wherever controller changes).
3. Add `invalidate_distance_cache()` method, call it from capture logic

**Test:** Benchmark before/after with 100-region synthetic graph. Verify cache invalidation on capture.

**Depends on:** Phase 1 (safety net tests passing)

---

### 2.2 Wire Spatial Index Into AI

**Problem:** 59 `world.marshals.values()` scans in `enemy_ai.py`. `_marshals_by_region` index already exists at `world_state.py:1249` but AI doesn't use it.

**Changes in `enemy_ai.py`:**
1. Identify the 59 scan sites (grep for `world.marshals.values()` and `marshals.values()`)
2. Categorize each: needs all marshals? needs marshals in a region? needs marshals of a nation?
3. Replace region-specific scans with `world._marshals_by_region[region_name]`
4. For nation-specific scans, add `get_nation_marshals(nation)` helper to `world_state.py`
5. For "all enemy marshals" scans, add `get_marshals_of_nations(nation_list)` helper

**Changes in `world_state.py`:**
- Add `get_nation_marshals(nation)` — returns list filtered from `self.marshals.values()`, cached per-turn
- Add `get_marshals_of_nations(nation_list)` — union of above
- Ensure `_marshals_by_region` updates when marshals move (check `_move_marshal()` and combat retreat logic)

**Test:** Run full test suite after each batch of replacements. Spot-check AI behavior in a few turns.

---

### 2.3 Extend Fog to All AI Nations

**Problem:** Only player nation uses fog-aware path. Enemy AI sees everything.

**Changes in `enemy_ai.py`:**
1. Replace omniscient `get_enemies_of_nation()` calls with `get_visible_enemies()` (already exists at `world_state.py:1534`)
2. For AI-vs-AI decisions, each AI nation should only "see" marshals within its fog range

**Changes in `world_state.py`:**
- Ensure `get_visible_enemies(nation)` works for any nation, not just player
- If intel model is player-only (comment at `enemy_ai.py:452-464` acknowledges this), extend it to track per-nation visibility

**Design note:** AI can be "smarter" than fog allows in limited ways (e.g., knowing its own marshals' locations). But it should not see enemy positions it hasn't scouted.

**Depends on:** 2.2 (spatial index should be in place first)

---

## Phase 3: Data Pipeline

**When:** After Phase 2 performance work.
**Why:** Cannot add nations or regions without this. Currently adding one region requires 6-7 file edits.
**Estimated effort:** 1-2 sessions.

### 3.1 Nation Config Factory Pattern

**Problem:** 5 nations hardcoded across 5 config surfaces. Marshal/diplomat creation is 470-line hand-authored functions.

**Changes in `nation_config.py`:**
- Add `DEFAULT_NATION_DEFAULTS` dict with sensible fallback values for gold, AP, authority
- New nations only need to override what differs from defaults
- `validate_runtime_nation_support()` checks defaults + overrides

**Changes in `marshal.py`:**
- Create `create_marshals_from_data(nation, marshal_definitions)` factory
- `marshal_definitions` is a list of dicts: `{name, personality, ability, troops, cavalry, ...}`
- Keep existing `create_player_marshals()` / `create_enemy_marshals()` as wrappers that feed data into the factory
- New nations add a data list, not a 100-line function

**Changes in `diplomat.py`:**
- Similar factory: `create_diplomat_from_data(nation, diplomat_def)`
- Diplomat definitions: `{name, voice_style, ...}`

**Depends on:** DG-1 (need to know which nations to add)

---

### 3.2 Frontend Loads Adjacency From Backend

**Problem:** `map.gd:30-50` hardcodes `REGION_CONNECTIONS` separately from backend `REGIONS_DATA`.

**Option A — Backend API endpoint:**
- Add `GET /map_data` to `main.py` returning `{regions: {name: {adjacencies, position, terrain, ...}}}`
- `map.gd` fetches on game start instead of hardcoding
- Remove `REGION_CONNECTIONS` dict from `map.gd`

**Option B — Shared JSON asset:**
- Generate `assets/map/region_topology.json` from `REGIONS_DATA` at build time
- Both backend and frontend read the same file
- Add a test that verifies the JSON matches `REGIONS_DATA`

**Recommendation:** Option A is simpler and already fits the existing `api_client.gd` pattern.

**Files:** `main.py` (new endpoint), `map.gd` (remove hardcoded dict, add fetch), `api_client.gd` (new request)

---

### 3.3 Centralize Nation Colors

**Problem:** Nation colors duplicated in `map.gd:52-61`, `utils.gd` (NATION_COLORS), `war_detail_popup.gd`.

**Fix:**
1. `utils.gd` NATION_COLORS is the single source (it's already intended to be)
2. `map.gd` and `war_detail_popup.gd` import from `utils.gd` instead of defining their own
3. Add a test that greps for `Color(` + nation name patterns outside `utils.gd` to catch future drift

---

### 3.4 Fix Prompt Fallback & Parser Hardcoding

**Files:**
- `prompt_builder.py:567` — Replace hardcoded 19-region string with `', '.join(REGIONS_DATA.keys())`
- `parser.py:103-108` — Replace hardcoded 8 enemy marshal names with dynamic lookup from world state
- `backend/modding/validator.py:71` — Replace `VALID_NATIONS` set with `NATION_CAPITALS.keys()`

**Effort:** ~30 minutes total.

---

## Phase 4: Map Art Pipeline

**When:** Before artist handoff / commissioned Europe art integration.
**Why:** The current renderer proves the color-lookup concept but can't ingest real bitmap art. Without this phase, debugging asset pipeline failures happens at the same time as validating Europe gameplay.
**Estimated effort:** 1-2 sessions.

### 4.1 Province Registry Schema

**Problem:** Province metadata only has `anchor`, `radius`, `lookup_color`, `visual_tint`. Europe needs separate anchors for units/labels/garrisons, plus wired/unwired flags.

**Create:** `assets/map/province_registry.json` (or expand the existing placeholder JSON)

**Schema per province:**
```json
{
  "province_id": "paris",
  "lookup_color": [255, 0, 0],
  "visual_tint": [0.8, 0.2, 0.2],
  "anchor": [400, 300],
  "unit_anchor": [410, 310],
  "label_anchor": [400, 280],
  "garrison_anchor": [390, 320],
  "building_anchor": [420, 310],
  "wired": true,
  "interactive": true
}
```

**Changes in `map_renderer_base.gd`:**
- `_build_province_shapes()` reads new fields
- Hover/click rejects provinces where `interactive == false`
- `update_all_regions()` skips unwired provinces for gameplay data but still renders them

**Test:** Update `tests/test_map_placeholder_assets.py` to validate new schema fields.

---

### 4.2 External Bitmap Loading

**Problem:** `map_renderer_base.gd:261-282` generates circle textures instead of loading artist-delivered images.

**Changes in `map_renderer_base.gd`:**
1. Add `_load_map_images()` method that loads:
   - `assets/map/europe_visual.png` — the pretty map players see
   - `assets/map/europe_provinces.png` — the hidden color-map for hit detection
2. Fall back to current circle generation if files don't exist (preserves 19-region dev mode)
3. Keep the existing `province_lookup_image.get_pixel()` path unchanged

---

### 4.3 Color-Map Validator

**Create:** `tools/validate_province_map.py` (or `tests/test_province_map_assets.py`)

**What it validates:**
- Visual and lookup images have identical dimensions
- Every RGB color in the lookup image exists in `province_registry.json`
- Every province in the registry appears in the lookup image (at least N pixels)
- No unexpected colors exist (catches anti-aliasing artifacts)
- No province uses the sentinel/background color
- Flags tiny pixel islands (< 5 pixels of a color) as likely export artifacts

**Run:** Before integrating any new art delivery. Also runs in CI.

---

### 4.4 Unwired Province Support

**Problem:** Roadmap plans 120-150 outlined provinces with only 80-100 wired for EA v1.

**Changes:**
- `map_renderer_base.gd`: Render unwired provinces in grey tint. Hover shows "Province Name (not yet in play)". Click does nothing.
- `map.gd`: `update_all_regions()` skips unwired provinces for gameplay data
- Province registry: `wired: false` provinces have lookup colors for hover identification but no gameplay data

---

## Phase 5: Gameplay Scaling

**When:** During first Europe prototype (after regions are added).
**Why:** Game mechanics designed for 5 nations need retuning, not just performance fixes.
**Estimated effort:** 2-3 sessions.
**Depends on:** Phase 0 design decisions.

### 5.1 War Cascade Depth Cap

**Implements:** DG-4 decision.

**File:** `diplomacy.py` (~line 2242, `_process_war_cascade`)

**Changes (assuming Option A — depth cap at 2):**
- Add `depth` parameter to `_process_war_cascade()`, default 0
- At depth >= 2, queue remaining allies for "call to arms" next turn instead of instant cascade
- Batch cascade dispatch events: "France's declaration of war draws Prussia and Austria into the conflict" instead of 3 separate events

**File:** `vassal.py` — Add vassal cascade to same depth tracking

**Test:** Synthetic test with 10-nation alliance chain verifying cascade stops at depth 2.

---

### 5.2 Dispatch Event Batching & Cap

**Implements:** DG-7 decision.

**File:** `dispatch.py`

**Changes (assuming Option A — priority filtering):**
- Add `priority` field to dispatch events: `CRITICAL`, `MAJOR`, `MINOR`
- War declarations, proposals directed at player, capital threats = CRITICAL (always shown)
- AI-AI diplomatic shifts, trade income changes, relation drift = MINOR
- Cap visible dispatch at ~20 events. If over cap, collapse MINOR events: "5 minor diplomatic developments occurred"
- Add `get_dispatch_summary()` method that returns the filtered view

**File:** `dispatch_view.gd` — Render collapsed MINOR section with expand option.

---

### 5.3 Coalition Friction Density Scaling

**File:** `coalition.py` (~line 408-425)

**Changes:**
- Count each nation's number of adjacent enemy nations
- Scale friction inversely: `friction_per_neighbor = base_friction / max(1, adjacency_count - 1)`
- Cap total friction received per nation per turn at a reasonable ceiling (e.g., -6 total, not -3 per neighbor x 5 neighbors = -15)

**Test:** Synthetic test with dense adjacency graph verifying friction doesn't create perpetual war spiral.

---

### 5.4 Victory Condition Alternatives

**Implements:** DG-5 decision.

**Files:** `world_state.py` (VICTORY_REGION_FRACTION), `turn_manager.py` (lines 867-942)

**Changes depend on decision.** If Option A (lower fraction + prestige):
- Reduce `VICTORY_REGION_FRACTION` to `0.40` for Europe scenarios
- Add prestige/war-score threshold as secondary condition
- Add capital-control requirement (must hold own capital + N enemy capitals)

---

### 5.5 Turn Limit & AP Scaling

**Implements:** DG-6 decision.

**Files:** `world_state.py` (max_turns), `nation_config.py` (BASE_NATION_ACTIONS)

**Changes depend on decision.** If Option B (scenario-configured):
- Add `scenario_config` dict loaded at game start with `max_turns`, `base_ap`, etc.
- Default 19-region scenario keeps current values
- Europe scenario gets its own values
- `world_state.py __init__` reads from scenario config

---

### 5.6 Bilateral Diplomacy O(N^2) Mitigation

**Problem:** At 15 nations = 105 bilateral pairs. Trade income, AI proposals, coalition checks all iterate pairs.

**File:** `diplomacy.py` (~line 2823, trade income iteration)
- Cache trade income per-turn, only recalculate on treaty change

**File:** `ai_diplomacy.py` (~line 570, proposal evaluation)
- Throttle: each AI nation evaluates proposals for at most 3 target nations per turn (prioritized by relationship + threat)
- Skip proposal evaluation for nations with active proposals pending

**File:** `ai_diplomacy.py` (~line 1211, coalition rivalry)
- Only check adjacency degradation for nations currently at peace (skip nations already at war)

---

## Phase 6: UI Density

**When:** During first Europe prototype, after gameplay scaling.
**Why:** UIs designed for 5-10 items break at 40+. Not crash bugs, but unnavigable.
**Estimated effort:** 1-2 sessions.

### 6.1 Marshal Management Pagination

**File:** `marshal_management.gd`

**Changes:**
- Replace single scrollable list with paginated view (10 marshals per page)
- Page navigation via arrow keys or prev/next buttons
- Number keys 1-9 select within current page, 0 = next page
- Filter buttons: "All / By Region / By Status"
- Lazy-load relationship sections (collapsed by default, expand on click)
- Reduce card height from 320px to responsive sizing

---

### 6.2 Strategic Ledger Sectioning

**File:** `strategic_ledger.gd` (~line 169-258)

**Changes:**
- Split marshal list by location or status (e.g., "In Combat / Marching / Idle")
- Each section collapsible, collapsed by default except "In Combat"
- Lazy-render: only build BBCode for expanded sections
- Keep existing number-key sub-tab switching

---

### 6.3 Incremental Map Updates

**File:** `map_renderer_base.gd` (~line 603-627, `_rebuild_dynamic_nodes()`)

**Changes:**
- Track which regions changed since last update (dirty-region set)
- Only rebuild force/garrison nodes for dirty regions
- `update_all_regions()` accepts optional `changed_regions` list; if provided, only updates those
- Full rebuild remains available for turn transitions

---

### 6.4 Diplomatic Ledger Collapsibles

**File:** `diplomatic_ledger.gd`

**Changes:**
- AI-AI relations section collapsed by default
- Each nation's relations expandable independently
- "Show major powers only" toggle to hide minor nations
- Group nations by relevance (at war with player, allied, neutral, minor)

---

### 6.5 Talleyrand Advisory Prioritization

**Implements:** GD6 from audit.

**File:** `diplomatic_advisory.py`

**Changes:**
- Rank nations by threat + relevance to player
- Top 3 recommendations shown by default, rest collapsed under "Other nations..."
- Add "Most urgent" framing: "Your Majesty, the most pressing matter is Prussia's mobilization..."
- Advisory text acknowledges when it's deliberately omitting minor nations

---

## Phase 7: Post-Prototype Polish

**When:** After first playable Europe prototype exists and has been playtested.
**Why:** These are real improvements but don't block a working prototype.
**Estimated effort:** 1-2 sessions.

### 7.1 Tooltip Caching

**File:** `map.gd` (~line 1553-1579)

Cache tooltip text per region. Regenerate only when region data changes (capture, battle, marshal movement). Eliminates O(n^2) relationship scan on every hover.

### 7.2 All-Pairs Distance Precomputation

**File:** `world_state.py`

Floyd-Warshall at map load time for O(1) distance lookup. Invalidate and recompute on region capture. Only worth doing if LRU cache from Phase 2.1 shows insufficient hit rate.

### 7.3 Save File Migration

**File:** `save_manager.py`

Handle loading 19-region saves into 80-region world. New regions initialize with default controller, no marshals. Warn player that saved game is from smaller map.

### 7.4 Coalition Full Retuning

**File:** `coalition.py`

After playtesting with real Europe prototype: adjust threat thresholds, friction rates, formation criteria, and dissolution timers for the actual nation count and density.

---

## Tracking Checklist

| # | Item | Phase | Status | Session |
|---|------|-------|--------|---------|
| DG-1 | Nation roster decision | 0 | DECIDED | April 17, 2026 |
| DG-2 | Diplomacy model decision | 0 | | |
| DG-3 | Supply lines decision | 0 | DEFERRED | April 17, 2026 |
| DG-4 | War cascade policy | 0 | | |
| DG-5 | Victory conditions | 0 | | |
| DG-6 | Pacing (turns, AP) | 0 | | |
| DG-7 | Dispatch density | 0 | DECIDED | April 17, 2026 |
| 1.1 | Nation config test | 1 | DONE | April 16, 2026 |
| 1.2 | Fix hardcoded `== 19` | 1 | DONE | April 16, 2026 |
| 1.3 | Adjacency connectivity test | 1 | DONE | April 16, 2026 |
| 2.1 | Cache `get_distance()` | 2 | | |
| 2.2 | Wire spatial index into AI | 2 | | |
| 2.3 | Extend fog to all AI nations | 2 | | |
| 3.1 | Nation config factory | 3 | | |
| 3.2 | Frontend loads adjacency from backend | 3 | | |
| 3.3 | Centralize nation colors | 3 | | |
| 3.4 | Fix prompt/parser/validator hardcoding | 3 | | |
| 4.1 | Province registry schema | 4 | | |
| 4.2 | External bitmap loading | 4 | | |
| 4.3 | Color-map validator | 4 | | |
| 4.4 | Unwired province support | 4 | | |
| 5.1 | War cascade depth cap | 5 | | |
| 5.2 | Dispatch event batching | 5 | | |
| 5.3 | Coalition friction scaling | 5 | | |
| 5.4 | Victory condition alternatives | 5 | | |
| 5.5 | Turn limit & AP scaling | 5 | | |
| 5.6 | Bilateral diplomacy O(N^2) | 5 | | |
| 6.1 | Marshal management pagination | 6 | | |
| 6.2 | Strategic ledger sectioning | 6 | | |
| 6.3 | Incremental map updates | 6 | | |
| 6.4 | Diplomatic ledger collapsibles | 6 | | |
| 6.5 | Talleyrand advisory prioritization | 6 | | |
| 7.1 | Tooltip caching | 7 | | |
| 7.2 | All-pairs distance precomputation | 7 | | |
| 7.3 | Save file migration | 7 | | |
| 7.4 | Coalition full retuning | 7 | | |

---

## Key Principle

> The audit's most important finding: **Europe scaling is a game design problem first, code problem second.** Optimizing BFS and extending fog while leaving game mechanics unchanged produces a fast, fair, and completely unplayable Europe campaign. Phase 0 design gates exist because the code roadmap must follow from design decisions, not precede them.
