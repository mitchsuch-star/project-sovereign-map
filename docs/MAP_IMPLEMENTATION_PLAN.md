# Map Implementation Plan — Real-Map Cutover (126-province Europe)

> **Status: DESIGN GATE — ✅ APPROVED by the user June 23, 2026. Slice 1 may begin (tools/assets only). The Roster Design Gate (Slice 2.5) and the 1805 Scenario Setup gate remain *in-execution* gates, due later.**
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
>    count is corrected below.
> 7. **1805 Scenario Setup is its own design-gate step** (end of this plan): re-authoring armies + the 1805
>    diplomatic posture for 14–16 nations is a second authoring pass, not a Slice-3 clause, and it carries
>    the campaign start-point decision. Net roadmap ≈ **11–12 sessions**.
> 8. **Second independent verification pass (June 22, 2026)** re-ran every measurement against the live
>    assets and reconfirmed all findings, then folded the remaining gaps: the legacy footprint re-measured
>    at **10,255 match-lines across 275 of 326 test files** (even larger than prior figures — the
>    fixture call is reinforced); `NATION_POWER_TIERS` already authors **13 nations**, so the roster gaps
>    are **`NATION_COLORS` + `NATION_DESIRE_PROFILES` (only 4 today)**, not tiers; `TALLEYRAND_COMMENTARY`
>    has a graceful `_default` fallback; the **Roster Design Gate is now an explicit step** (Slice 2.5);
>    Slice 6 names a **fragment shader** for per-turn owner fills; Slice 4 must **decide the `grid_position`
>    method**; and the **1805 North-African owners are authored** (Morocco independent; Algiers/Tunis/Tripoli
>    as Ottoman client-regencies — see Slice 2.5).
> 9. **Third independent verification pass (June 22, 2026)** re-ran every measurement from scratch and
>    reconfirmed all prior numbers (validator PASS; land 1,788,712 px / 43.7%; gap bimodality
>    73.6% / 2.9% / 23.5% over 35,633 samples; `letters` = single glyphs, **visually confirmed**; legacy
>    `Belgium` alone 2,344 / 133 files). Four new design items folded — none block Slice 1, all are
>    pre-Slice-3: **(N1)** `NATION_CAPITALS` is a **global** dict the legacy fixture depends on, so
>    "Britain = London" must be **scenario-scoped capitals**, not a mutation of the global (Slices 3 + 4);
>    **(N2)** `WorldState.from_scenario_file()` **already exists** (world_state.py:4790) — author the 1805
>    setup as a **scenario JSON via that loader**, not a second hardcoded init (Scenario Setup step; this
>    moots the hardcode-vs-loader question); **(N3)** the 1805 diplomatic matrix is C(16,2)=120 pairs —
>    author via **default-to-PEACE + exceptions only** (Scenario Setup step); **(N4)** `grid_position` must
>    derive `(row,col)` by **centroid spatial-rank** (unique, order-preserving), NOT a ≈12×10 coarse bucket
>    (which collides for 126 provinces and breaks `resolve_direction`) (Slice 4). Minor: `NATION_HONOR_BIAS`
>    covers only 2 nations (not 13). The broad scale fears are defused (fog is O(marshals); the distance
>    cache is on-demand; vassals are data-driven). Net roadmap unchanged at ≈11–12 sessions.
> 10. **Plan-hardening pass (June 22, 2026)** closes four residual gaps to make the cutover reversible and
>     the budgets measurable: **(G1)** the Slice-4 `region_factory` seam is selected by a config flag
>     (`SOVEREIGN_MAP=europe|legacy`); the game **bootstrap** reads it (Slice 5 sets `europe`) while
>     `WorldState()` still defaults to **legacy** for the test fixture — so the Slice-5/7 "replace outright"
>     flips become a **flag flip, instantly reversible without a code change** (rollback = `legacy`).
>     **(G2)** a standing **legacy-fixture immutability guard** test asserts `create_regions()` still
>     returns the unchanged 19 regions (names, owners, adjacency), so no future edit can silently perturb
>     the fixture the suite depends on. **(G3)** a validator **`is_coastal` ↔ sea-adjacency consistency
>     check** (every coastal province has ≥1 `sea: true` edge or borders ocean-black; no inland province
>     carries a sea edge). **(G4)** concrete budgets replace "within budget": Slice 8 turn resolution
>     **≤ 2× the 19-region baseline** (measured), Slice 6 owner-fill re-tint **≤ one frame (~16 ms)** on
>     ownership change via the shader. Net roadmap unchanged at ≈11–12 sessions.

(Review-outcome list updated from six to ten amendments: the June 22 scenario-setup follow-up (7), the second independent verification pass (8), the third independent verification pass (9), and the plan-hardening pass (10).)

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

`WorldState.__init__` builds **every** world from `create_regions()` → `REGIONS_DATA` (`backend/models/world_state.py:128`). **Re-measured: 10,255 word-boundary match-lines for the 19 region names span 275 of the 326 test files** (8,343 / 241 even after excluding the `Saxony` nation/region name collision — `Belgium` 2,344, `Paris` 2,129, `Saxony` 2,034, `Waterloo` 1,312 dominate), and the pre-commit hook runs the full suite and must stay green (no `--no-verify`). The plan's original "2,462 / 190" under-counted ~4×; the larger true footprint only **strengthens** the legacy-as-fixture decision below.

A literal "delete `REGIONS_DATA`, swap in 126 provinces" detonates the suite. So **"replace outright" is honored at the _game_ level, not the _test-fixture_ level**:

- **The game ships only Europe.** The new-game bootstrap (`/new_game` → `_reset_world_state`, and the module-load `world`) builds the 126-province Europe world. The 19-region map is unreachable in play. `main.tscn` renders only Europe. This is the user's "replace outright."
- **The 19-region dataset survives as a test-only fixture.** `create_regions()` keeps returning the legacy 19 as the default `WorldState()` constructor path, so the ~275 gameplay test files that incidentally use Paris/Berlin/Vienna stay green **untouched**. Only the handful of *map-contract* tests (those that assert properties of "the game's map": `test_map_consistency.py`, `test_map_topology_endpoint.py`, `test_map_bitmap_contract.py`) migrate/extend to Europe.

This is the engineering reconciliation of decision #6 with the hook. **If the user instead wants the ~10,255 references rewritten onto Europe (a multi-thousand-edit migration), that is a different, much larger plan — flag at sign-off.** Default assumption: legacy-as-fixture.

---

## Open verification items for the gate (answer before Slice 2)

1. **Real-roster discovery + capital coverage + the patron web.** The roster is whatever the *real 1805 ownership* of the 126 provinces turns out to be — discovered while authoring Slice 2, not pre-counted. Three things to confirm there: (a) the art is "Europe" but may not extend to Russia's heartland (St. Petersburg/Moscow), the Ottoman Balkans (Constantinople), Scandinavia (Stockholm/Copenhagen), or all of Iberia (Madrid/Lisbon) — every **independent** needs ≥1 owned province and a real-or-proxy capital (precedent: `NATION_CAPITALS["Britain"] = "Netherlands"`); (b) every **minor** state needs a historically-correct **patron** so no province is orphaned and the vassal graph is accurate; (c) any sovereign whose heartland is off-map gets a proxy capital **or** an owner-row entry — it does not silently vanish. **(d) Confirmed from the rendered art (second pass):** the British Isles, Iberia, Italy + islands, the Balkans/Anatolia, Crimea, **southern** Scandinavia, and a **North-African coastal strip** are all on-map; **only the Russian heartland and far north are off-map**. So **Britain takes a real London** (retire the `Netherlands` proxy); **Russia is the clear proxy case** (frontier-province capital), with **Ottoman** (Constantinople sits at the map edge) and **Sweden** (only southern Scandinavia drawn) confirmed real-or-proxy at the **Roster Design Gate (Slice 2.5)**. **(N1, third pass) Britain=London is authored as a *scenario-scoped* capital, NOT by mutating the global `NATION_CAPITALS` dict** — that global is read by `settlement_scoring.py` (CLAUDE.md's documented Britain proxy), marshal spawns, and `covets_regions`, and the legacy 19-region test fixture depends on Britain→Netherlands. The Europe build carries its own capital map; the global stays Netherlands for the legacy fixture (see Slice 3 + Slice 4). **(e) 1805 North-African owners are authored** there too: **Morocco independent** (Alaouite sultanate, coastal proxy capital), and **Algiers / Tunis / Tripoli as Ottoman client-regencies** (nominal Porte suzerainty → modeled as Ottoman vassals; or independent Barbary minors if the Ottoman is itself a proxy).
2. **Named diplomat voices.** The Voice Bible cast is 5 (Talleyrand/Castlereagh/Hardenberg/Metternich/Einsiedel = France/Britain/Prussia/Austria/Saxony). The 8 new nations get the **chancery fallback voice** in v1 (functional, per the `resolve_named_diplomat()` → chancery rule). Named-voice authoring is a tracked owner row (DEF-1), not a v1 blocker.
3. **Save compatibility.** Replacing the map invalidates pre-cutover saves (region keys won't match). Acceptable for a prototype; recorded as owner row DEF-2 with a version bump + a clear "incompatible saves" message rather than a silent crash.

---

## Scope / non-goals

**In scope (v1):** 126 named provinces; **full-roster 1805 ownership (~14–16 independents + ~10 client/vassal states, incl. the North-African regencies)**; auto-derived land adjacency + hand-authored sea links; province-shape political fills; backend region expansion + game cutover; Godot renderer cutover; scale-ready hot-path audit at 126 regions; a manual playtest smoke.

**Non-goals (owner-rowed below, not silently dropped):** named diplomat voices for the new independents (DEF-1); save migration (DEF-2); per-province historical income hand-tuning beyond region_type defaults (DEF-3); coalition/dispatch/diplomacy density retune beyond what the full roster forces (DEF-4 → Phase 5.2/5.3/5.6); naval movement rules beyond adjacency (DEF-5).

## Cross-cutting constraints (honored in every slice)

- **Golden Rule #8 — no per-region scans in hot paths.** 126 regions is the whole point; any new helper that scans `world.regions` caches per-turn and invalidates via the `invalidate_active_nations_cache()` pattern. Slice 8 audits this explicitly.
- **One province source of truth.** The backend region set and the Godot renderer both read the **same `europe.json` registry**, so the map can never drift between them (the exact failure CLAUDE.md guards against). Slice 2 extends the registry with the gameplay fields; the backend loads them in Slice 4.
- **All numbers to Godot via `int()`**; single `world.marshals` dict; backend port 8005.
- **Workflow:** commit directly to master; the pre-commit hook (`ruff check backend/` + full pytest) stays green every slice.
- **No open-ended deferrals** (Golden Rule #9): the owner-row table below gives every deferred item a landing slice, completion definition, STATUS line, and test.

---

## DESIGN GATE — sign-off checklist — ✅ APPROVED (user, June 23, 2026)

Initial gate approved; **Slice 1 may begin.** The two downstream gates below are *in-execution* gates that come due later (notes inline).

- [x] **Decisions #1–#7** as tabled above — APPROVED.
- [x] **Legacy-as-fixture reconciliation** (game = Europe only; 19-region survives as a test fixture; gameplay tests untouched; map-contract tests migrate) — APPROVED (default; **not** the full ~10,255-reference migration).
- [x] **Open verification items 1–3** (geographic coverage / chancery-fallback voices / save-incompat) — accepted as scoped.
- [x] **Slice ordering** (low-risk-first; Slice 1 lands then pauses for review) — APPROVED.
- [x] **Render + parser method choices** — APPROVED approach: owner-fill **fragment shader** (finalize at Slice 6) + `grid_position` by **centroid spatial-rank** (finalize at Slice 4).
- [x] **Owner-row table** (DEF-1..5) — accepted as the home for non-v1 work.
- [ ] **Roster Design Gate (Slice 2.5)** — *in-execution gate*, due after Slice 2 discovers the roster and before Slice 3 wires it: independents vs. vassals, proxy capitals (Russia/Ottoman/Sweden; Britain=London), the patron web incl. the North-African regencies.
- [ ] **1805 Scenario Setup gate** — *in-execution gate*, due after Slice 5 and before the Slice 8 playtest: the campaign **start-point decision** (Third Coalition already at war vs. just before) + the army/diplomacy re-authoring scope.

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

- **Scope:** The big hand-authoring pass, all into `europe.json`: **historical name** per province (cross-checked vs the Slice 1 letters-layer seeds), **starting_controller** = the province's **real 1805 sovereign** (authoring this across all 126 provinces is what *discovers the full roster* and which states are minors), **terrain**, **region_type**, **is_coastal**, and each nation's **capital** (`is_capital`). Hand-correct the derived adjacency where the heuristic erred. Output the canonical roster list — independents vs. minors-needing-a-patron (including the North-African coastal strip — Morocco independent, the Algiers/Tunis/Tripoli regencies as Ottoman client states; see Slice 2.5) — that Slice 3 consumes. Resolve verification item #1 (every province → a real sovereign; every independent has a capital/proxy). This is the heaviest authoring slice; it is pure registry data + validation, no game logic.
- **Files:** `godot-client/project-sovereign/assets/maps/europe.json`; `tools/validate_province_map.py` (add gameplay-field schema checks: every province has a unique non-placeholder name; `starting_controller` ∈ the authored roster set; `terrain` ∈ `VALID_TERRAINS`; `region_type` ∈ `VALID_REGION_TYPES`; every nation in the roster owns ≥1 province; every `NATION_CAPITALS` capital exists and is owned by that nation; **(G3) `is_coastal` ↔ sea-adjacency consistency — every `is_coastal` province has ≥1 `sea: true` edge or borders ocean-black, and no inland province carries a sea edge**). New `tests/test_europe_registry_data.py`.
- **Tests:** registry-completeness test (126 named provinces, no `Region_NNN` left, all owners known, all terrains/types valid, adjacency symmetric, every capital present + correctly owned); `validate_province_map.py --strict` → `PASS`.
- **STATUS line:** `Map Slice 2 LANDED — 126 provinces authored (historical names, full-roster 1805 ownership, terrain/type/coastal, capitals); registry data-validated; validator + data tests PASS.`
- **Completion:** `europe.json` is the complete, validated province source (render + gameplay fields); no placeholder names; coverage of the full roster confirmed; suite green.

### Slice 2.5 — ROSTER DESIGN GATE *(decision step — no code; bless before Slice 3 wires it)*

> Added by the second review pass. Decision #2's realized size (≈14–16 independents + ≈10 client/vassal states) carries large downstream cost (bilateral O(N²), dispatch/coalition density, per-nation colors/voices/desire-profiles), so the **exact roster is blessed here — after Slice 2 discovers it, before Slice 3 wires it.**

**Bless at this gate:**

- **Independents (full agency) vs. vassals (client states of a patron).** Modeling minors as vassals is what caps the O(N²) blow-up at the ~14–16 independents — decision #2's whole point.
- **Proxy capitals.** Britain takes a **real London** (the British Isles are drawn — retire `NATION_CAPITALS["Britain"]="Netherlands"`). **Russia** is the clear proxy case (heartland off-map → a frontier province, e.g. Vilna/Courland). **Ottoman** (Constantinople sits at the map edge) and **Sweden** (only southern Scandinavia drawn) are confirmed real-capital-or-proxy here.
- **The patron web** (seeded into `world.vassals` at build, Slice 3): e.g. Batavia, Helvetia/Switzerland, Kingdom of Italy, Etruria, the SW-German states (Württemberg, Baden, Hesse, Berg), the small Italian duchies (Parma, Modena, Lucca), a Polish/Warsaw entity. Every minor resolves to a historically-correct patron so no province is orphaned.
- **1805 North-African owners** (researched; the coastal strip is on-map):

  | Province area | 1805 sovereign | Model as |
  |---|---|---|
  | Morocco (Atlantic/Med. coast) | Sultanate of Morocco (Alaouite; Sultan Moulay Slimane) — **fully independent**, never Ottoman | independent **minor** (coastal proxy capital; Fez/Marrakesh are inland/off-map) |
  | Algiers | Regency of Algiers (Dey) — autonomous under **nominal Ottoman suzerainty** | **Ottoman** vassal/satellite |
  | Tunis | Regency of Tunis (Husainid Bey) — nominal Ottoman suzerainty | **Ottoman** vassal/satellite |
  | Tripoli (Tripolitania) | Regency of Tripoli (Karamanli Pasha) — nominal Ottoman suzerainty | **Ottoman** vassal/satellite |

  If the gate makes the **Ottoman** a proxy/owner-row rather than a live independent, model Algiers/Tunis/Tripoli instead as **independent Barbary minors** (they ran their own foreign policy — e.g. Tripoli's 1801–1805 war with the United States). Egypt's heartland is off-map (Ottoman; Muhammad Ali as Wāli from 1805); any coastal sliver that appears is Ottoman-owned.

- **Authoring debt the roster creates** (drives Slice 3 + DEF-1/DEF-4): `power_tier` is **already authored for 13 nations**, so tiers are mostly done; the real gaps are **`Utils.NATION_COLORS`** (8 today incl. "Neutral" → +6–9) and **`NATION_DESIRE_PROFILES`** (only 4 today: Austria/Britain/Prussia/Saxony → +9–11, else AI proposals degrade to empty desires). `TALLEYRAND_COMMENTARY` already has a `_default` fallback, so commentary degrades gracefully — **prioritize desire profiles over commentary**.
- **Completion:** the user approves the independents/vassals split, proxy capitals, patron web, and North-African owners. This is the design input Slice 3 wires; **no code lands at this gate.**

### Slice 3 — full-roster backend data *(no map wiring yet)*

- **Scope:** Make the backend *know* the full roster Slice 2 discovered so Slice 4's Europe world can reference it. **3a:** **scenario-scoped** capitals (every independent, matching the registry capitals/proxies — **N1, third pass: seed a per-Europe-world capital map at construction rather than mutating the global `NATION_CAPITALS`, which the legacy fixture + `settlement_scoring.py` depend on; the global stays Netherlands for the legacy world**), authored `power_tier` (`major`/`secondary`/`minor`) per nation, `NATION_HONOR_BIAS` as needed, gold/AP/authority config (so `RUNTIME_NATIONS` resolves to the full set), and `Utils.NATION_COLORS` extended to cover every nation rendered (Russia/Spain/Saxony already present; add ~6–9 more). **Note (second pass): `NATION_POWER_TIERS` already authors 13 nations, so `power_tier` is mostly done — the real authoring load is `NATION_COLORS` (8 today incl. "Neutral") and `NATION_DESIRE_PROFILES` (only 4 today: Austria/Britain/Prussia/Saxony → add ~9–11, else AI proposals degrade to empty desires). `TALLEYRAND_COMMENTARY` already has a `_default` fallback, so commentary degrades gracefully — prioritize desire profiles.** **3b:** the **historically-accurate vassal/satellite (client-parent) web** seeded into the world's vassal state (`vassal.py` / `world.vassals`) at build time; starting diplomats for each new independent (chancery-fallback voice — DEF-1 owns named voices); marshals via the `create_marshals_from_data` factory; `NATION_DESIRE_PROFILES` + `TALLEYRAND_COMMENTARY` per independent (CLAUDE.md "Don't Do" requires these); and 1805 starting diplomatic states/relationships.
- **Files:** `backend/nation_config.py`, `backend/models/region.py` (`NATION_CAPITALS`), `backend/models/diplomat.py`, `backend/game_logic/diplomatic_templates.py` (desire profiles + commentary), `backend/game_logic/diplomacy.py` (starting relations), `godot-client/project-sovereign/scripts/utils.gd` (`NATION_COLORS`). Tests in `tests/test_nation_config_factory.py`, new `tests/test_thirteen_nation_roster.py`.
- **Tests:** `get_runtime_nations()` returns the full roster; every independent has a capital/color/diplomat/desire-profile/commentary (parametrized "no nation missing its required config" test — the standing guard against the CLAUDE.md gap); every minor resolves to a valid patron in the vassal web; power tiers authored for all; `test_gdscript_color_centralization.py` stays green with the expanded color set.
- **STATUS line:** `Map Slice 3 LANDED — full map roster wired into backend config (every independent: capital, power_tier, color, diplomat w/ chancery fallback, desire profile + commentary; minors seeded as historical vassals/satellites; 1805 relations); roster-completeness + patron-validity tests guard every required field.`
- **Completion:** the backend roster is the full map set, fully configured (independents + historical vassal web), suite green — but the live game still runs the 19-region/5-nation world (no cutover yet).

### Slice 4 — Europe region set as an alternate backend world *(built + tested, NOT yet the game's map)*

- **Scope:** `create_europe_regions()` builds 126 `Region` objects from `europe.json` (owner, terrain, region_type, is_coastal, adjacency authored; income/supply/garrison/building-slots derived from `REGION_TYPE_INCOME`/`SUPPLY_BY_TYPE`/`BUILDING_SLOT_LIMITS`; `grid_position` derived from the registry anchor — **decide the method here (F5/second pass): the LLM direction parser (`strategic_parser.resolve_direction` via `REGION_POSITIONS`) reads a hand-authored `(row,col)` grid and Europe is not a grid; choose (a) bucket province centroids into a coarse grid (≈12×10) or (b) refactor the parser to real centroid bearings (cleaner, but touches a tested parser)**). **N4 (third pass) — recommend a third option (a′): derive a *unique* `(row,col)` per province by centroid spatial-rank** (col = rank of centroid-x within a latitude band, row = rank of centroid-y). A coarse ≈12×10 grid is only 120 cells for 126 provinces → guaranteed collisions, and a collision breaks `resolve_direction()`'s "move north" disambiguation (it reads a unique `(row,col)` per region, strategic_parser.py:33-39). Spatial-rank preserves N/S/E/W ordering, gives unique cells, and needs **no parser refactor**. `create_regions()` (legacy 19) is **untouched** — `WorldState()` still defaults to it. Add a `WorldState(region_factory=…)` seam so a Europe world can be constructed in tests/bootstrap without changing the default. **(G1) The factory is selected by a config flag `SOVEREIGN_MAP=europe|legacy` that the game *bootstrap* reads (Slice 5 sets `europe`); `WorldState()` still defaults to `legacy` for the test fixture. This makes the Slice-5/7 cutover a flag flip, instantly reversible (rollback = `legacy`), rather than a code edit.** Run the Golden-Rule-#8 hot-path check at 126 regions.
- **Files:** `backend/models/region.py` (`create_europe_regions`, registry loader), `backend/models/world_state.py` (region-factory seam, default unchanged). New `tests/test_europe_world_construction.py`.
- **Tests:** construct the Europe world → 126 regions, ownership matches the registry, adjacency symmetric and matches the registry, derived income/supply/garrison/grid correct, every independent present with its capital and the vassal web matching the authored patrons; a turn advances on the Europe world without error; spot-check no new per-region scan regressed a hot path (reuse `tests/test_scale_readiness_phase2.py` patterns).
- **STATUS line:** `Map Slice 4 LANDED — create_europe_regions() builds the validated 126-province world from europe.json (derived income/supply/garrison/grid); WorldState region-factory seam added, legacy default unchanged; Europe world constructs + advances a turn; suite green.`
- **Completion:** the Europe world is constructable and turn-stable in tests; legacy default and all gameplay tests untouched.

### Slice 5 — Backend game cutover *(the backend "replace outright" flip)*

- **Scope:** Repoint the **game bootstrap** to Europe: the module-load `world` and `_reset_world_state()` (`/new_game`) build `create_europe_regions()` with the full map roster (independents + vassal web) and `player_nation = France`. `/map_topology` now serves the 126-province graph automatically. Migrate the **map-contract** tests to Europe (`test_map_consistency.py`, `test_map_topology_endpoint.py`, `test_map_bitmap_contract.py`); leave gameplay tests on the legacy default fixture. Land save-incompat handling (DEF-2: version bump + clear message, no silent crash).
- **Files:** `backend/main.py` (startup `world` + `_reset_world_state`), `backend/save_manager.py` (version/incompat guard), the three map-contract test files. Possibly `backend/models/world_state.py` reset path.
- **Tests:** `/new_game` → 126-region Europe world (curl-verifiable); `/map_topology` returns 126 provinces with symmetric adjacency; the migrated map-contract tests pass against Europe; loading a pre-cutover save returns the incompat message rather than crashing; **(G2) a standing legacy-fixture immutability guard asserts `create_regions()` still returns the unchanged 19 regions (names, owners, adjacency); (G1) rollback drill: `SOVEREIGN_MAP=legacy` restores the 19-region game without a code change;** full suite green (gameplay tests still on the legacy fixture).
- **STATUS line:** `Map Slice 5 LANDED — backend game cutover: /new_game + startup build the 126-province Europe world (full map roster, France player); /map_topology serves Europe; map-contract tests migrated; save-incompat guarded; legacy 19 retained as gameplay-test fixture.`
- **Completion:** a fresh backend game **is** Europe end-to-end at the API layer; suite green; old saves fail gracefully.

### Slice 6 — Godot province-shape ownership fills *(renderer feature, tested on the smoke scene)*

- **Scope:** New renderer pass that tints each province by its owner's `NATION_COLORS` color through the lookup mask. The one-time **initial paint** may mirror `_apply_unwired_grey_overlay()` (per-pixel lookup→owner→blend), but the **per-turn re-tint must NOT** (F2/second pass): the §4.4 overlay early-outs on all-wired maps (so its full-image cost is untested) and a naive 1.79M-land-px `get_pixel`/`set_pixel` mirror every ownership change is multi-second. Use a **fragment shader (lookup texture + a ≤126-entry owner-color palette uniform) — recommended — or a cached per-province pixel-index with dirty-only repaint**. The existing per-region `Panel` stylebox fill (`_refresh_region_visual`) cannot fill arbitrary province polygons, so this pass is genuinely net-new. Driven by the ownership data already flowing through `update_all_regions(map_data)`. Markers stay for marshals/garrisons/forces only (not ownership). Build and verify against `europe_map_smoke.tscn` before any game wiring.
- **Files:** `godot-client/project-sovereign/scenes/map_renderer_base.gd` (owner-fill pass + a refresh hook on ownership change), `scenes/europe_map.gd` (un-suppress ownership fills in the smoke). Tests in the existing source-level renderer suites.
- **Tests:** source-level test (mirroring `tests/test_map_renderer_cutover.py` / `test_map_unwired_overlay.py`) that the owner-fill pass maps lookup color → region → owner color and blends only owned-province pixels; Godot 4.4.1 parse harness → 0 failures; manual: the smoke scene shows provinces filled by owner.
- **STATUS line:** `Map Slice 6 LANDED — province-shape political fills (owner-tint via lookup mask, mirrors §4.4 grey overlay) added to the renderer base + verified on the Europe smoke; parse harness 0 failures.`
- **Completion:** ownership renders as real political-map fills on the smoke scene; markers reserved for forces; parse clean; **(G4) re-tint budget: an ownership change re-tints in ≤ one frame (~16 ms) via the shader palette uniform — no per-pixel CPU pass.**

### Slice 7 — Godot game cutover *(the frontend "replace outright" flip)*

- **Scope:** Point the live `MapArea` at the Europe renderer (the `map.gd` node in `main.tscn` either becomes the Europe renderer or has its asset/definition paths swapped to `europe.*`), so the running game renders the 126-province map with owner fills, hover, and click. Ensure `update_all_regions`, `set_region_topology`, focus/zoom, strategic-ledger, and hotkey consumers all work against the new region set. Retire the 19-region placeholder scene from the game path (owner-rowed as DEF-3 if any test still pins it).
- **Files:** `godot-client/project-sovereign/scenes/main.tscn`, `scenes/map.gd` (or replace with a Europe map script extending the base), `scripts/main.gd` (any 19-region assumptions). Godot parse harness + headless scene-instantiation check.
- **Tests:** Godot 4.4.1 parse harness → 0 failures; headless instantiation of `main.tscn` renders the Europe map; manual smoke (F6/F5): map renders with owner fills, hover names provinces, clicks route, a turn end re-tints ownership.
- **STATUS line:** `Map Slice 7 LANDED — Godot game cutover: main.tscn renders the 126-province Europe map with owner-shape fills, hover, and click; 19-region placeholder retired from the game path; parse harness 0 failures + headless instantiation OK.`
- **Completion:** the running game **is** the full Europe map, frontend + backend; the placeholder is no longer in the game path.

### Slice 8 — Scale & balance validation + manual playtest smoke

- **Scope:** Prove 126 regions × the full roster is performant and playable. Golden-Rule-#8 audit (grep/verify no per-region scan entered a hot path; turn-time check); AI sanity at 126 regions (`enemy_ai.py` spatial paths); coalition/dispatch density (apply Phase 5.2/5.3 collapse only if 126 regions force it — DEF-4); economy/balance sanity (incomes, supply, manpower at scale). A real playtest: start a game, issue orders, fight, run diplomacy, end several turns.
- **Files:** `tests/test_scale_readiness_phase2.py` (extend to 126), possibly `backend/ai/enemy_ai.py`, `backend/game_logic/coalition.py`/`dispatch.py` if density forces it. `docs/MANUAL_TEST_PLAN.md` (Europe smoke script).
- **Tests:** scale test at 126 regions (**(G4) turn resolution — enemy phase + advance — ≤ 2× the 19-region baseline, measured**; no hot-path scan regression); manual playtest checklist passes.
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
| DEF-1 | Named diplomat voices for the new independents (Russia, Spain, Ottoman, Sweden, Naples, Bavaria, Portugal, Denmark-Norway, Papal States, Morocco, + any others Slice 2 discovers) | Post-cutover follow-up slice "Roster Voices" | Each new nation resolves a named diplomat per the Voice Bible (or an explicit authored chancery persona), not the bare fallback | New STATUS line when authored | A voice test per nation that the diplomat resolves + emits in-register copy |
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

Land **Slice 1, then pause for user review** (per the slice-review cadence — first low-risk slice, then checkpoint before the big ones). Slices 2–9 proceed after that review. The two genuine "replace outright" flips (Slice 5 backend, Slice 7 frontend) are each preceded by a fully-tested, un-wired build-up slice (4 and 6) so the cutover itself is a small, reversible change rather than a big bang. The **1805 Scenario Setup design gate** (explicit step below) runs after the roster (Slice 3) and backend cutover (Slice 5) and **before the Slice 8 playtest** — its start-point decision is a prerequisite for a meaningful playtest.

---

## 1805 Scenario Setup — DESIGN GATE (explicit step)

> Added June 22, 2026 (review follow-up). **Sequence position:** after Slice 3 (roster config) + Slice 5 (backend cutover), **before Slice 8 (playtest)** — the Europe world cannot be meaningfully playtested until it is populated with the correct 1805 armies + diplomatic posture. Captured here as an explicit step + design gate so it is **never folded silently into Slice 3**.

**Why this is its own step.** Today the entire starting state is hardcoded for the 5-nation / 19-region world: `create_starting_marshals()` + `create_enemy_marshals()` (`backend/models/marshal.py`, ~11 marshals whose `location` is an old 19-region name) and the 10-pair `diplomatic_states` / `nation_relations` matrices (`backend/models/world_state.py:381` / `:394`) plus coalition state. The Europe cutover must **re-author all of it** at the new scale — a second authoring/design pass comparable to the naming pass, not two clauses in Slice 3.

**Scope:**
- **Army placement:** every marshal `location` re-mapped to the new province names; **author marshals for the 9–11 new nations** (Russia, Spain, Ottoman, Sweden, Naples, Portugal, Denmark-Norway, Bavaria-as-independent, …) which have **zero** today — who / where / strength / personality / ability / relationships — via the data-driven `create_marshals_from_data`, not the hardcoded functions.
- **Diplomatic posture:** the 1805 state matrix across all 14–16 independents (the Third Coalition vs. France + Spain, Prussian neutrality, Ottoman stance, …), numeric relations, and any pre-formed coalition / war state. **N3 (third pass): C(16,2) = 120 pairs is too many to hand-author safely (today's matrix is 10 hardcoded pairs at `world_state.py:381`) — author it as default-to-PEACE + only the explicit exceptions** (the coalition, the Franco-Spanish alliance, active wars), not 120 literal entries.
- **The seam:** the Europe world gets its **own** marshal-placement + diplomacy-init path (parallel to the legacy `create_starting_marshals`/`create_enemy_marshals`), wired into `create_europe_regions` / bootstrap — the legacy 5-nation init stays the test fixture. Ideally this lives in the `scenario_config` loader (SCALE_READINESS_PLAN §5.5) rather than a second hardcoded init. **N2 (third pass): the loader substrate already EXISTS — `WorldState.from_scenario_file()` (`world_state.py:4790`) + `collect_scenario_nations()` / `validate_scenario_runtime_support()` (`nation_config.py`) + `backend/modding/validator.py`.** So author the 1805 setup as a **scenario JSON loaded via `from_scenario_file()`**, not a second hardcoded `create_*_marshals()` path; what is missing is the authored Europe scenario file, not the loader. This moots the "hardcode-now vs. build-the-loader" question (prior-review Decision #6).

**THE DESIGN DECISION (this gate — decide here, do not default silently):** **does the campaign start with the War of the Third Coalition already underway** (France ↔ Britain / Austria / Russia / Sweden / Naples at war at turn 1, coalition pre-seeded) **or just before it** (armed peace; the coalition forms in play)? This drives the entire starting matrix, whether a coalition is pre-formed, and where the armies sit.

- **Files:** `backend/models/marshal.py` (or a Europe scenario module / `scenario_config`), `backend/models/world_state.py` (Europe diplomacy/relations/coalition init seam), `backend/game_logic/diplomacy.py` (starting relations), possibly `backend/game_logic/coalition.py` (pre-seeded coalition). Legacy fixtures untouched.
- **Tests:** Europe world starts with every nation's marshals placed on valid **owned** provinces; the 1805 diplomatic matrix is symmetric + valid; a turn advances without error; the legacy 5-nation start is unchanged.
- **STATUS line:** `Map 1805 Scenario Setup LANDED — armies placed for all 14–16 nations on Europe provinces; 1805 diplomatic posture + coalition state authored (<start-point decision>); legacy 5-nation start retained as fixture.`
- **Completion:** a fresh Europe game opens in a correct, playable 1805 situation — armies, diplomacy, and coalition state authored and turn-stable — ready for the Slice 8 playtest.
