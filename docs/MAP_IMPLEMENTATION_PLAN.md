# Map Implementation Plan — Real-Map Cutover (126-province Europe)

> **Status: DESIGN GATE — awaiting user sign-off. No implementation code until the gate below is approved.**
> Owner: Map cutover. Supersedes the "After the smoke passes → create the Map Implementation Plan" action in `docs/STATUS.md` (▶ NEXT UP: Real-Map Cutover).

> **Reviewed June 22, 2026 — verdict GO WITH CHANGES.** An independent review verified every claim against
> the real assets (PSD byte-inspection, validator run, registry parse, test grep, lookup measurement).
> Full findings + the session-by-session roadmap live in [`MAP_PLAN_REVIEW.md`](MAP_PLAN_REVIEW.md). Six
> amendments are folded into this plan:
> 1. **Naming (decision #3):** the PSD has **no text layers** — `letters` is **rasterized single-character
>    glyphs** on only 83/126 provinces (absent from Iberia). Naming is a **manual geography pass** against
>    the `Map_Napoleon_Total_War` underlay + an 1805 atlas, verified by an annotated overlay — NOT
>    letters-layer extraction (the layer is at most a weak initial-letter hint).
> 2. **Adjacency (decision #5):** measured inter-province gaps are cleanly bimodal (land ≤~15px = 72.6%,
>    sea ≥41px = 24.4%). **Auto-derive land; hand-author the ~10–20 real sea links** from a generated
>    candidate list — no auto sea-heuristic (it connects every coast-facing pair).
> 3. **Owner fills (Slice 6):** the §4.4 overlay it's modeled on early-outs on all-wired maps (never
>    load-tested here) and is a 4.1M-px per-pixel loop. Use a **fragment shader (≤126-entry owner palette)**
>    or cached per-province pixel-index — NOT a per-turn full-image mirror.
> 4. **Roster (DEF-4):** the art supports **~14–16 independents + ~10 vassals**. Promote DEF-4 to its **own
>    session** (§5.2 dispatch / §5.3 coalition friction / §5.6 trade-income cache) *before* the playtest,
>    and add a **roster design gate** after Slice 2. Britain can take a **real London** (its isles are
>    on-map); Russia/Ottoman/Sweden are the genuine proxy cases.
> 5. **Slice 2 is the critical path** — a manual historical-research pass (budget **1–2 sessions**), not an
>    ordinary slice.
> 6. **`grid_position` at 126** needs explicit pixel→grid bucketing design (Slice 4); the legacy reference
>    count is corrected below. Net roadmap ≈ **10–11 sessions**.

## Goal

Cut the game over from the 19-region placeholder map to the **full commissioned 126-province Europe map** — rendered as a real political map, owned by nations, clickable, and playable. The smoke scene (`europe_map_smoke.tscn`) already proves the art loads and hit-testing works; this plan turns that art into the live game map.

## Locked decisions (interview, June 22, 2026)

| # | Decision | Choice |
|---|----------|--------|
| 1 | Wiring scope | **All 126 provinces playable in v1** (no greyed core) |
| 2 | Nation roster | **Every sovereign on the map, historically accurate, tiered** — great/secondary powers independent (France [player], Britain, Austria, Prussia, Russia, Spain, Ottoman, Sweden, Naples, Bavaria, Saxony, Portugal, Denmark + any other genuine 1805 sovereigns the 126 provinces cover, e.g. Papal States / Sardinia-Piedmont / Swiss); minor German/Italian statelets modeled as **historically-accurate vassals/satellites** of their 1805 patron via the existing vassal system. **Not capped at 13** — the exact roster is discovered while authoring 1805 ownership in Slice 2. |
| 3 | Province naming | **Historical names, hand-authored from geography** (the PSD `letters` layer is rasterized single-char glyphs, not names — weak initial-letter hint at most; see Review amendment 1) |
| 4 | Ownership render | **Province-shape fills via the lookup mask** (new renderer pass, mirrors the §4.4 grey overlay) |
| 5 | Adjacency | **Auto-derive land adjacency; hand-author sea links** from a generated >40px candidate list (see Review amendment 2) |
| 6 | Cutover | **Replace the 19-region placeholder outright** as the game map |
| 7 | Per-province data | **Author owner / terrain / region_type / is_coastal**; income, supply, garrison, buildings, grid derive from existing tables |

The `major / secondary / minor` power-tier taxonomy and France-as-player are already DECIDED in `docs/SCALE_READINESS_PLAN.md` §Phase 0; this plan implements them. The roster extends **beyond DG-1's illustrative 13 to every sovereign the map covers** — tiered exactly as DG-1's architecture already anticipates (it lists Netherlands/Batavia, Duchy of Warsaw, Württemberg, and Switzerland as vassals, not independents). Independents get full diplomatic agency; minors are client states of their real 1805 patron. The goal is an accurate map: every province owned by its real sovereign, every client-parent relationship modeled.

---

## The one reconciliation the gate must bless: "replace outright" vs. a green test suite

`WorldState.__init__` builds **every** world from `create_regions()` → `REGIONS_DATA` (`backend/models/world_state.py:128`). **Verified ≈8,463 references to the 19 region names span 273 test files** (≈6,887 / 232 even after excluding the `Saxony` nation/region name collision; the plan's earlier "2,462 / 190" materially under-counted), and the pre-commit hook runs the full suite and must stay green (no `--no-verify`). The larger true footprint only **strengthens** the legacy-as-fixture decision below.

A literal "delete `REGIONS_DATA`, swap in 126 provinces" detonates the suite. So **"replace outright" is honored at the _game_ level, not the _test-fixture_ level**:

- **The game ships only Europe.** The new-game bootstrap (`/new_game` → `_reset_world_state`, and the module-load `world`) builds the 126-province Europe world. The 19-region map is unreachable in play. `main.tscn` renders only Europe. This is the user's "replace outright."
- **The 19-region dataset survives as a test-only fixture.** `create_regions()` keeps returning the legacy 19 as the default `WorldState()` constructor path, so the ~190 gameplay test files that incidentally use Paris/Berlin/Vienna stay green **untouched**. Only the handful of *map-contract* tests (those that assert properties of "the game's map": `test_map_consistency.py`, `test_map_topology_endpoint.py`, `test_map_bitmap_contract.py`) migrate/extend to Europe.

This is the engineering reconciliation of decision #6 with the hook. **If the user instead wants the 2,462 references rewritten onto Europe (a multi-thousand-edit migration), that is a different, much larger plan — flag at sign-off.** Default assumption: legacy-as-fixture.

---

## Open verification items for the gate (answer before Slice 2)

1. **Real-roster discovery + capital coverage + the patron web.** The roster is whatever the *real 1805 ownership* of the 126 provinces turns out to be — discovered while authoring Slice 2, not pre-counted. Three things to confirm there: (a) the art is "Europe" but may not extend to Russia's heartland (St. Petersburg/Moscow), the Ottoman Balkans (Constantinople), Scandinavia (Stockholm/Copenhagen), or all of Iberia (Madrid/Lisbon) — every **independent** needs ≥1 owned province and a real-or-proxy capital (precedent: `NATION_CAPITALS["Britain"] = "Netherlands"`); (b) every **minor** state needs a historically-correct **patron** so no province is orphaned and the vassal graph is accurate; (c) any sovereign whose heartland is off-map gets a proxy capital **or** an owner-row entry — it does not silently vanish.
2. **Named diplomat voices.** The Voice Bible cast is 5 (Talleyrand/Castlereagh/Hardenberg/Metternich/Einsiedel = France/Britain/Prussia/Austria/Saxony). The 8 new nations get the **chancery fallback voice** in v1 (functional, per the `resolve_named_diplomat()` → chancery rule). Named-voice authoring is a tracked owner row (DEF-1), not a v1 blocker.
3. **Save compatibility.** Replacing the map invalidates pre-cutover saves (region keys won't match). Acceptable for a prototype; recorded as owner row DEF-2 with a version bump + a clear "incompatible saves" message rather than a silent crash.

---

## Scope / non-goals

**In scope (v1):** 126 named provinces; 13-nation 1805 ownership; auto-derived adjacency; province-shape political fills; backend region expansion + game cutover; Godot renderer cutover; scale-ready hot-path audit at 126 regions; a manual playtest smoke.

**Non-goals (owner-rowed below, not silently dropped):** named diplomat voices for the 8 new nations (DEF-1); save migration (DEF-2); per-province historical income hand-tuning beyond region_type defaults (DEF-3); coalition/dispatch/diplomacy density retune beyond what the full roster forces (DEF-4 → Phase 5.2/5.3/5.6); naval movement rules beyond adjacency (DEF-5).

## Cross-cutting constraints (honored in every slice)

- **Golden Rule #8 — no per-region scans in hot paths.** 126 regions is the whole point; any new helper that scans `world.regions` caches per-turn and invalidates via the `invalidate_active_nations_cache()` pattern. Slice 8 audits this explicitly.
- **One province source of truth.** The backend region set and the Godot renderer both read the **same `europe.json` registry**, so the map can never drift between them (the exact failure CLAUDE.md guards against). Slice 2 extends the registry with the gameplay fields; the backend loads them in Slice 4.
- **All numbers to Godot via `int()`**; single `world.marshals` dict; backend port 8005.
- **Workflow:** commit directly to master; the pre-commit hook (`ruff check backend/` + full pytest) stays green every slice.
- **No open-ended deferrals** (Golden Rule #9): the owner-row table below gives every deferred item a landing slice, completion definition, STATUS line, and test.

---

## DESIGN GATE — sign-off checklist

Approve these before any implementation code lands:

- [ ] **Decisions #1–#7** as tabled above.
- [ ] **Legacy-as-fixture reconciliation** (game = Europe only; 19-region survives as a test fixture; gameplay tests untouched; map-contract tests migrate). *Or* explicitly request the full 2,462-reference migration instead.
- [ ] **Open verification items 1–3** (geographic coverage / chancery-fallback voices / save-incompat) accepted as scoped.
- [ ] **Slice ordering** (low-risk-first; Slice 1 lands then pauses for review).
- [ ] **Owner-row table** (DEF-1..5) accepted as the home for non-v1 work.

---

## Slices (ordered low-risk-first)

Each slice: **Scope · Files · Tests · STATUS line · Completion definition.** Slices 1–2 touch only `tools/` + `assets/` (zero game logic, zero suite risk). The cutover risk is concentrated in Slices 5 and 7, each preceded by a fully-tested, un-wired build-up slice.

### Slice 1 — Adjacency derivation + registry/validator tooling *(tools/assets only — LAND FIRST, then pause for review)*

- **Scope:** Extend the offline pipeline so the registry can carry a derived adjacency graph and the new gameplay fields, with validation. **No backend, no Godot, no game logic.**
  - `build_region_key_from_psd.py`: add an adjacency pass — for each province, scan the lookup image for the nearest distinct province color across the black moats (border-dilation / nearest-non-black within a tunable gap radius) to produce land adjacency; add a coarse **sea-gap heuristic** (coastal provinces within a larger radius across black get a candidate sea edge, tagged `sea: true`). Emit symmetric `adjacent` lists into `europe.json`.
  - Add a **`letters`-layer inspection** mode: reuse the existing PSD layer parser (`extract_layer`) to dump the `letters` layer (bbox +, if it is a real type layer, its text; else export a crop) as naming seeds for Slice 2. Investigative — does not block if the layer is rasterized.
  - `validate_province_map.py`: add `ADJACENCY_ASYMMETRY` (A→B but not B→A), `ADJACENCY_UNKNOWN_TARGET` (edge to a non-existent province), and `ISOLATED_PROVINCE` (no land edges) checks; tolerate the new authored fields.
- **Files:** `tools/build_region_key_from_psd.py`, `tools/validate_province_map.py`, `tools/mapgen_out/europe.json` → promote to `godot-client/project-sovereign/assets/maps/europe.json`. New `tests/test_province_adjacency_derivation.py`.
- **Tests:** unit-test the adjacency deriver on a tiny synthetic lookup (two provinces sharing a moat → symmetric edge; a province across a wide sea gap → tagged sea candidate; an isolated blob → no edges); extend `tests/test_province_map_validator.py` with the three new failure codes; regenerate + re-run `validate_province_map.py` → `PASS`.
- **STATUS line:** `Map Slice 1 LANDED — adjacency auto-derivation (land + sea-gap heuristic) + letters-layer seed extraction + 3 new validator checks; europe.json regenerated with symmetric adjacency; validator PASS.`
- **Completion:** `europe.json` carries a symmetric, validated 126-node adjacency graph; the validator gates it; suite green; ruff clean. **PAUSE for user review here.**

### Slice 2 — Province data authoring *(registry data + validation — no game logic)*

- **Scope:** The big hand-authoring pass, all into `europe.json`: **historical name** per province (cross-checked vs the Slice 1 letters-layer seeds), **starting_controller** = the province's **real 1805 sovereign** (authoring this across all 126 provinces is what *discovers the full roster* and which states are minors), **terrain**, **region_type**, **is_coastal**, and each nation's **capital** (`is_capital`). Hand-correct the derived adjacency where the heuristic erred. Output the canonical roster list — independents vs. minors-needing-a-patron — that Slice 3 consumes. Resolve verification item #1 (every province → a real sovereign; every independent has a capital/proxy). This is the heaviest authoring slice; it is pure registry data + validation, no game logic.
- **Files:** `godot-client/project-sovereign/assets/maps/europe.json`; `tools/validate_province_map.py` (add gameplay-field schema checks: every province has a unique non-placeholder name; `starting_controller` ∈ the 13-nation set; `terrain` ∈ `VALID_TERRAINS`; `region_type` ∈ `VALID_REGION_TYPES`; every nation in the roster owns ≥1 province; every `NATION_CAPITALS` capital exists and is owned by that nation). New `tests/test_europe_registry_data.py`.
- **Tests:** registry-completeness test (126 named provinces, no `Region_NNN` left, all owners known, all terrains/types valid, adjacency symmetric, 13 capitals present + correctly owned); `validate_province_map.py --strict` → `PASS`.
- **STATUS line:** `Map Slice 2 LANDED — 126 provinces authored (historical names, 13-nation 1805 ownership, terrain/type/coastal, capitals); registry data-validated; validator + data tests PASS.`
- **Completion:** `europe.json` is the complete, validated province source (render + gameplay fields); no placeholder names; coverage of all 13 nations confirmed; suite green.

### Slice 3 — 13-nation roster backend data *(no map wiring yet)*

- **Scope:** Make the backend *know* the full roster Slice 2 discovered so Slice 4's Europe world can reference it. **3a:** `NATION_CAPITALS` (every independent, matching the registry capitals/proxies), authored `power_tier` (`major`/`secondary`/`minor`) per nation, `NATION_HONOR_BIAS` as needed, gold/AP/authority config (so `RUNTIME_NATIONS` resolves to the full set), and `Utils.NATION_COLORS` extended to cover every nation rendered (Russia/Spain/Saxony already present; add the rest). **3b:** the **historically-accurate vassal/satellite (client-parent) web** seeded into the world's vassal state (`vassal.py` / `world.vassals`) at build time; starting diplomats for each new independent (chancery-fallback voice — DEF-1 owns named voices); marshals via the `create_marshals_from_data` factory; `NATION_DESIRE_PROFILES` + `TALLEYRAND_COMMENTARY` per independent (CLAUDE.md "Don't Do" requires these); and 1805 starting diplomatic states/relationships.
- **Files:** `backend/nation_config.py`, `backend/models/region.py` (`NATION_CAPITALS`), `backend/models/diplomat.py`, `backend/game_logic/diplomatic_templates.py` (desire profiles + commentary), `backend/game_logic/diplomacy.py` (starting relations), `godot-client/project-sovereign/scripts/utils.gd` (`NATION_COLORS`). Tests in `tests/test_nation_config_factory.py`, new `tests/test_thirteen_nation_roster.py`.
- **Tests:** `get_runtime_nations()` returns the full roster; every independent has a capital/color/diplomat/desire-profile/commentary (parametrized "no nation missing its required config" test — the standing guard against the CLAUDE.md gap); every minor resolves to a valid patron in the vassal web; power tiers authored for all; `test_gdscript_color_centralization.py` stays green with the expanded color set.
- **STATUS line:** `Map Slice 3 LANDED — full map roster wired into backend config (every independent: capital, power_tier, color, diplomat w/ chancery fallback, desire profile + commentary; minors seeded as historical vassals/satellites; 1805 relations); roster-completeness + patron-validity tests guard every required field.`
- **Completion:** the backend roster is the full map set, fully configured (independents + historical vassal web), suite green — but the live game still runs the 19-region/5-nation world (no cutover yet).

### Slice 4 — Europe region set as an alternate backend world *(built + tested, NOT yet the game's map)*

- **Scope:** `create_europe_regions()` builds 126 `Region` objects from `europe.json` (owner, terrain, region_type, is_coastal, adjacency authored; income/supply/garrison/building-slots derived from `REGION_TYPE_INCOME`/`SUPPLY_BY_TYPE`/`BUILDING_SLOT_LIMITS`; `grid_position` derived from the registry anchor). `create_regions()` (legacy 19) is **untouched** — `WorldState()` still defaults to it. Add a `WorldState(region_factory=…)` seam so a Europe world can be constructed in tests/bootstrap without changing the default. Run the Golden-Rule-#8 hot-path check at 126 regions.
- **Files:** `backend/models/region.py` (`create_europe_regions`, registry loader), `backend/models/world_state.py` (region-factory seam, default unchanged). New `tests/test_europe_world_construction.py`.
- **Tests:** construct the Europe world → 126 regions, ownership matches the registry, adjacency symmetric and matches the registry, derived income/supply/garrison/grid correct, every independent present with its capital and the vassal web matching the authored patrons; a turn advances on the Europe world without error; spot-check no new per-region scan regressed a hot path (reuse `tests/test_scale_readiness_phase2.py` patterns).
- **STATUS line:** `Map Slice 4 LANDED — create_europe_regions() builds the validated 126-province world from europe.json (derived income/supply/garrison/grid); WorldState region-factory seam added, legacy default unchanged; Europe world constructs + advances a turn; suite green.`
- **Completion:** the Europe world is constructable and turn-stable in tests; legacy default and all gameplay tests untouched.

### Slice 5 — Backend game cutover *(the backend "replace outright" flip)*

- **Scope:** Repoint the **game bootstrap** to Europe: the module-load `world` and `_reset_world_state()` (`/new_game`) build `create_europe_regions()` with the full map roster (independents + vassal web) and `player_nation = France`. `/map_topology` now serves the 126-province graph automatically. Migrate the **map-contract** tests to Europe (`test_map_consistency.py`, `test_map_topology_endpoint.py`, `test_map_bitmap_contract.py`); leave gameplay tests on the legacy default fixture. Land save-incompat handling (DEF-2: version bump + clear message, no silent crash).
- **Files:** `backend/main.py` (startup `world` + `_reset_world_state`), `backend/save_manager.py` (version/incompat guard), the three map-contract test files. Possibly `backend/models/world_state.py` reset path.
- **Tests:** `/new_game` → 126-region Europe world (curl-verifiable); `/map_topology` returns 126 provinces with symmetric adjacency; the migrated map-contract tests pass against Europe; loading a pre-cutover save returns the incompat message rather than crashing; full suite green (gameplay tests still on the legacy fixture).
- **STATUS line:** `Map Slice 5 LANDED — backend game cutover: /new_game + startup build the 126-province Europe world (full map roster, France player); /map_topology serves Europe; map-contract tests migrated; save-incompat guarded; legacy 19 retained as gameplay-test fixture.`
- **Completion:** a fresh backend game **is** Europe end-to-end at the API layer; suite green; old saves fail gracefully.

### Slice 6 — Godot province-shape ownership fills *(renderer feature, tested on the smoke scene)*

- **Scope:** New renderer pass that tints each province by its owner's `NATION_COLORS` color through the lookup mask — directly modeled on `_apply_unwired_grey_overlay()` (per-pixel lookup→owner→blend). Driven by the ownership data already flowing through `update_all_regions(map_data)`. Markers stay for marshals/garrisons/forces only (not ownership). Build and verify against `europe_map_smoke.tscn` before any game wiring.
- **Files:** `godot-client/project-sovereign/scenes/map_renderer_base.gd` (owner-fill pass + a refresh hook on ownership change), `scenes/europe_map.gd` (un-suppress ownership fills in the smoke). Tests in the existing source-level renderer suites.
- **Tests:** source-level test (mirroring `tests/test_map_renderer_cutover.py` / `test_map_unwired_overlay.py`) that the owner-fill pass maps lookup color → region → owner color and blends only owned-province pixels; Godot 4.4.1 parse harness → 0 failures; manual: the smoke scene shows provinces filled by owner.
- **STATUS line:** `Map Slice 6 LANDED — province-shape political fills (owner-tint via lookup mask, mirrors §4.4 grey overlay) added to the renderer base + verified on the Europe smoke; parse harness 0 failures.`
- **Completion:** ownership renders as real political-map fills on the smoke scene; markers reserved for forces; parse clean.

### Slice 7 — Godot game cutover *(the frontend "replace outright" flip)*

- **Scope:** Point the live `MapArea` at the Europe renderer (the `map.gd` node in `main.tscn` either becomes the Europe renderer or has its asset/definition paths swapped to `europe.*`), so the running game renders the 126-province map with owner fills, hover, and click. Ensure `update_all_regions`, `set_region_topology`, focus/zoom, strategic-ledger, and hotkey consumers all work against the new region set. Retire the 19-region placeholder scene from the game path (owner-rowed as DEF-3 if any test still pins it).
- **Files:** `godot-client/project-sovereign/scenes/main.tscn`, `scenes/map.gd` (or replace with a Europe map script extending the base), `scripts/main.gd` (any 19-region assumptions). Godot parse harness + headless scene-instantiation check.
- **Tests:** Godot 4.4.1 parse harness → 0 failures; headless instantiation of `main.tscn` renders the Europe map; manual smoke (F6/F5): map renders with owner fills, hover names provinces, clicks route, a turn end re-tints ownership.
- **STATUS line:** `Map Slice 7 LANDED — Godot game cutover: main.tscn renders the 126-province Europe map with owner-shape fills, hover, and click; 19-region placeholder retired from the game path; parse harness 0 failures + headless instantiation OK.`
- **Completion:** the running game **is** the full Europe map, frontend + backend; the placeholder is no longer in the game path.

### Slice 8 — Scale & balance validation + manual playtest smoke

- **Scope:** Prove 126 regions × the full roster is performant and playable. Golden-Rule-#8 audit (grep/verify no per-region scan entered a hot path; turn-time check); AI sanity at 126 regions (`enemy_ai.py` spatial paths); coalition/dispatch density (apply Phase 5.2/5.3 collapse only if 126 regions force it — DEF-4); economy/balance sanity (incomes, supply, manpower at scale). A real playtest: start a game, issue orders, fight, run diplomacy, end several turns.
- **Files:** `tests/test_scale_readiness_phase2.py` (extend to 126), possibly `backend/ai/enemy_ai.py`, `backend/game_logic/coalition.py`/`dispatch.py` if density forces it. `docs/MANUAL_TEST_PLAN.md` (Europe smoke script).
- **Tests:** scale test at 126 regions (turn advances within budget, no hot-path scan regression); manual playtest checklist passes.
- **STATUS line:** `Map Slice 8 LANDED — scale + balance validated at 126 regions / full roster (hot-path audit clean, AI + economy sane); Europe manual playtest smoke PASS.`
- **Completion:** the full map is performant and playable; playtest smoke recorded.

### Slice 9 — Cleanup & docs

- **Scope:** Retire placeholder map assets with owner rows; finalize `docs/SAVE_FORMAT_REFERENCE.md` (region-key change), `docs/STATUS.md`, `CLAUDE.md` Current Phase, `docs/SCALE_READINESS_PLAN.md` §4/§5 closeout; close DEF rows that landed; confirm the deferred ones still have homes.
- **Files:** docs + any dead placeholder assets/scenes.
- **Tests:** suite green; no dangling `Region_NNN`; docs reflect shipped behavior.
- **STATUS line:** `Map Slice 9 LANDED — placeholder assets retired (owner-rowed), docs reconciled, save-format + STATUS + CLAUDE updated; real-map cutover COMPLETE.`
- **Completion:** the cutover is closed out; every deferred item has a live owner row.

---

## Deferred / owner-row table (Golden Rule #9 — every item has a home)

| ID | Deferred item | Landing slice | Completion definition | STATUS tracking | Behavior test |
|----|---------------|---------------|-----------------------|-----------------|---------------|
| DEF-1 | Named diplomat voices for the 8 new nations (Russia, Spain, Ottoman, Sweden, Naples, Bavaria, Portugal, Denmark-Norway) | Post-cutover follow-up slice "Roster Voices" | Each new nation resolves a named diplomat per the Voice Bible (or an explicit authored chancery persona), not the bare fallback | New STATUS line when authored | A voice test per nation that the diplomat resolves + emits in-register copy |
| DEF-2 | Save migration / incompatibility | Slice 5 (guard) → optional later migrator | Pre-cutover saves either migrate or fail with a clear versioned message (no crash) | Slice 5 STATUS line | `test_save_load.py` case: old-format save → graceful incompat message |
| DEF-3 | Per-province historical income tuning beyond region_type defaults | Post-cutover "Economy Pass" slice | Authored income overrides where history diverges from the region_type default, validated | New STATUS line | Registry test that overridden incomes are within sane bounds |
| DEF-4 | Coalition friction, dispatch density, and bilateral-diplomacy O(N²) retune at the full roster | Slice 8 if forced, else Phase 5.2/5.3/5.6 | Per `docs/SCALE_READINESS_PLAN.md` §5.2/§5.3/§5.6; no perpetual-war spiral, dispatch stays navigable, pair iteration stays per-turn cached | Slice 8 / Phase 5 STATUS | Dense-adjacency friction test + 40-event dispatch collapse test + per-turn trade-income cache test |
| DEF-5 | Naval movement rules beyond sea adjacency | Post-prototype "Naval" spec | Sea edges carry movement semantics (not just graph edges) per a future spec | Future STATUS line | Movement test across a `sea: true` edge |

---

## Validation commands (run after any asset or code change)

```bash
# Regenerate the region key + draft registry from the PSD (only if the PSD redelivers or the deriver changes)
.venv\Scripts\python.exe tools/build_region_key_from_psd.py

# Validate the registry + bitmaps (Slice 1+ adds adjacency/gameplay-field checks)
.venv\Scripts\python.exe -m tools.validate_province_map \
  --registry godot-client/project-sovereign/assets/maps/europe.json \
  --visual   godot-client/project-sovereign/assets/maps/europe_visual.png \
  --lookup   godot-client/project-sovereign/assets/maps/europe_lookup.png --strict

# Full suite (pre-commit gate) + lint
.venv\Scripts\python.exe -m pytest tests/ -q --tb=no
ruff check backend/

# Godot parse harness (Slices 6–7) — 0 failures required
```

---

## Sequencing note

Land **Slice 1, then pause for user review** (per the slice-review cadence — first low-risk slice, then checkpoint before the big ones). Slices 2–9 proceed after that review. The two genuine "replace outright" flips (Slice 5 backend, Slice 7 frontend) are each preceded by a fully-tested, un-wired build-up slice (4 and 6) so the cutover itself is a small, reversible change rather than a big bang.
