# Map Implementation Plan — Independent Review & Phased Roadmap

> Reviewer pass over `docs/MAP_IMPLEMENTATION_PLAN.md`, June 22, 2026. Every number below was
> verified against the real code/assets (validator run, PSD byte-inspection, registry parse, test
> grep, lookup-image measurement) — not taken from the plan. Reproduction tooling listed in the
> Appendix. **This is review + planning only; no plan/code/asset was modified.**

---

## 1. VERDICT — **GO WITH CHANGES (substantial)**

The plan is **structurally sound and unusually disciplined**: low-risk-first slice ordering, a tested
un-wired build-up slice before each "replace outright" flip (4→5, 6→7), the legacy-as-fixture
reconciliation, and a real Golden-Rule-#9 owner-row table. The skeleton does not need a rewrite.

But it rests on **one false premise** and **under-specifies four hard problems** that decide whether the
cutover succeeds. None require reworking the slice skeleton; all are fixable by amending specific slices.

| # | Finding | Severity | Where it bites |
|---|---------|----------|----------------|
| **F1** | **The PSD `letters` layer is NOT province names.** It is rasterized **single-character glyphs** (one capital letter per province) on only **83 of 126** provinces, absent from all of Iberia. `Txt `/`TySh` occur **0** times in the file — there are no editable text layers at all. | **Critical** — invalidates decision #3's stated *method* | Naming pipeline (Slice 1–2) |
| **F2** | **Owner-fill rendering can't mirror the §4.4 overlay per-turn.** That overlay early-outs on all-wired maps (so it's never been load-tested here) and is a full **4.1M-px** GDScript `get_pixel`/`set_pixel` + string-key loop. Owner fills touch **all 1.79M land px** and re-run every ownership change. | **Major** — perf landmine | Slice 6 |
| **F3** | **Roster explosion is under-scoped as one owner-row (DEF-4).** The art supports **~14–16 independents + ~10 client/vassal states**. That is a 3× jump in independents → ~7–10× bilateral-diplomacy pairs, plus dispatch/coalition density and 6+ nations with no color/voice/desire-profile. | **Major** — playability, not just perf | Slice 3, 8; needs its own phase |
| **F4** | **Legacy blast radius is ~3× the plan's number.** Plan says "2,462 refs / 190 files"; actual ≈ **8,463 quoted match-lines / 273 files** (≈6,887 / 232 even excluding the `Saxony` nation/region collision). | Minor — *strengthens* the legacy-as-fixture call; just correct the number | §"reconciliation" |
| **F5** | **`grid_position` at 126 is hand-waved** ("derived from the registry anchor"). It is a hand-authored `(row,col)` tuple that is the *single source of truth* for the LLM direction parser (`DIRECTION_GRID`) and `/map_topology`. Pixel→grid bucketing needs explicit design. | Minor–Major | Slice 4 |
| **F6** | **Slice 2 is massively under-estimated.** It is a manual historical-geography research pass (126 names + 126 owners + the patron web), the project's true schedule bottleneck — yet tabled as one ordinary "slice." | Major (schedule) | Slice 2 |

**Bottom line:** approve the skeleton; amend Slices 1, 2, 3, 4, 6; promote DEF-4 to its own session;
add a roster design gate. The plan's own hedge in Slice 1 ("*if it is a real type layer, its text; else
export a crop*") shows the author anticipated F1 — this review resolves it firmly to the "else" branch
and rebuilds the naming pipeline around that.

---

## 2. Verified facts vs. the plan's claims

| Claim in plan | Verified? | Evidence |
|---|---|---|
| 126 provinces, unique colors, sea=black | ✅ exact | `europe.json` = 126 regions, 126 distinct `lookup_color`, 0 duplicates |
| Validator PASSES with 0 findings | ✅ | `validate_province_map … ` → `PASS: no findings`, exit 0 |
| Registry has no names/owners/terrain/adjacency yet | ✅ | all 126 are `Region_NNN`; no `adjacent`/`starting_controller`/`terrain`/`region_type`; `is_coastal`=False ×126; `wired`/`interactive`=True ×126 |
| `letters` layer is a naming source | ❌ **false** | 35 layers; `Txt `/`TySh`=0; layer 15 `letters` rasterized, bbox (578,160)-(2166,1031), **single-char glyphs**, covers 83/126 anchors |
| 19-region dataset, ~2,462 refs / 190 files | ⚠️ under-count | 19 regions confirmed; refs ≈ 8,463 lines / 273 files (≈6,887/232 excl. Saxony) |
| `create_europe_regions()` must be built; `WorldState` needs a factory seam | ✅ | neither exists; `create_regions()` hardcoded at `world_state.py:128` |
| Income/supply/garrison/grid derivable from region_type tables | ✅ | `REGION_TYPE_INCOME`/`SUPPLY_BY_TYPE`/`BUILDING_SLOT_LIMITS` all keyed by `region_type`; `VALID_TERRAINS`(6)/`VALID_REGION_TYPES`(5) |
| Britain needs a proxy capital | ⚠️ **stale** | `NATION_CAPITALS["Britain"]="Netherlands"` today — **but the British Isles are drawn on THIS art**, so Britain can take a real London. Russia/Ottoman/Sweden are the real proxy cases (heartland off-map) |
| power-tier taxonomy + 13-nation roster already decided | ✅ | `NATION_POWER_TIERS`/`NATION_HONOR_BIAS` author 13 nations (major/secondary/minor); but only **5** are runtime-playable; `utils.gd` has **8** colors |
| §4.1–4.4 map pipeline complete | ✅ | SCALE_READINESS_PLAN §4 all COMPLETE |
| Scale-ready cache infra (Golden Rule #8) exists | ✅ | `get_active_nations()`, `get_nation_regions()`, `invalidate_active_nations_cache()` all present + per-turn cached |
| §5 density work is "if forced" | ⚠️ risky | §5.1/5.2/5.3/5.6 PLANNED, **unbuilt**; §5.5 `scenario_config` **unbuilt** (roster hardcoded; `max_turns=40` at `world_state.py:163`); `calculate_trade_income` (`diplomacy.py:8863`) recomputes all pairs every turn, **uncached** |

---

## 3. CONCRETE MECHANICS for the under-specified work

### C — Naming + ownership pipeline (the headline)

**The evidence (decisive):**
- The PSD has **no text layers** (`TySh`=0). The `letters` layer is **rasterized pixels**.
- Rendered at native resolution, `letters` is **single hand-drawn capital letters** — "P", "B", "S", "W",
  "G", "V", "M", "U", "K", "T"… one glyph per province. "Bavaria" never renders as a lone "B".
- It covers only **83/126** province anchors; **43 are unlabeled** (14 west = Iberia, 32 south =
  Italy/Mediterranean/Balkans). The working-note layer **`help with spain`** (layer 14) confirms Iberia
  was left incomplete.

**Conclusion: extract is impossible, OCR is pointless, the answer is MANUAL — and the `letters` layer is
at best a weak per-province *initial-letter cross-check*, not a name source.** Decision #3's *goal*
(historical names) is achievable; its *method* ("cross-check vs the letters layer") is not. Rebuild the
pipeline as a geography-driven human research pass:

1. **Generate the review artifact (tooling, Slice 1).** Composite `County Colors` + `letters` over white
   → a single annotated PNG where each colored province carries its glyph (the reproduction script in the
   Appendix already produces `_letters_over_counties.png`). Also export the **`Map_Napoleon_Total_War`
   reference underlay** (layer 17 — a real labeled historical map, embedded as a smart object) as the
   primary naming reference.
2. **Assign names + owners by geography (Slice 2, human).** For each of the 126 province colors: read its
   centroid, overlay it on the reference underlay + a standard 1805 atlas, and author `{name,
   starting_controller, terrain, region_type, is_coastal, is_capital}`. The glyph is a tie-breaker only.
3. **Verify as a reviewable artifact, province-by-province.** Emit a second overlay that paints each
   province by its *assigned owner color* and stamps the *assigned name* at the centroid. The user signs
   off this map before any backend wiring — this is the gate, not eyeballing the registry JSON.
4. **Effort, honestly:** ~126 provinces × (locate on reference + name + assign sovereign + terrain/type) ≈
   **a full focused session of human research**, plus a second pass for the 43 unlabeled (Iberia/south) and
   the patron web. Budget **1–2 sessions for Slice 2 alone**; it is the critical path, not a checkbox.

### D — Adjacency auto-derivation (calibrated, evidence-backed)

Measured the black-gap-width distribution between adjacent province colors in the lookup (8,386 samples):

| Gap width | Share | Meaning |
|---|---|---|
| 1–2 px | 62.3% | provinces touch / thin moat |
| 3–6 px | 7.6% | normal land border |
| 7–15 px | 2.7% | wide land border |
| 16–40 px | 2.9% | ambiguous (rare) |
| **41+ px** | **24.4%** | **sea strait / open water** (median large, up to 1122 px) |

The distribution is **cleanly bimodal** (land cluster ≤15px, sea cluster ≥41px, only 2.9% between). So:
- **Land adjacency auto-derives reliably**: nearest-non-black dilation with a **~8–10px** radius captures
  72%+ of land edges directly and won't bridge sea. Emit symmetric `adjacent` lists; validate with the
  plan's proposed `ADJACENCY_ASYMMETRY` / `ADJACENCY_UNKNOWN_TARGET` / `ISOLATED_PROVINCE` checks.
- **Do NOT trust an auto sea-heuristic.** A >40px radius connects *every* coast-facing pair (Iberia↔Italy,
  N.Africa↔everything, Greece↔Anatolia) — the 41+ bucket has 2,048 samples. Instead, **emit >40px coastal
  pairs as flagged sea *candidates* for human curation**, and hand-author the ~10–20 strategically real
  crossings (Channel: England↔Low Countries/Normandy; Sicily↔Naples; Denmark↔Scania; Greek islands;
  Bosphorus). This is a small, bounded set — far safer than "auto + fix in playtest," which ships noise.
- **Amend decision #5:** "auto-derive land, hand-author sea (from a generated candidate list)."

### E — Ownership-fill rendering (the perf landmine)

Two facts kill the plan's "mirror the §4.4 grey overlay" approach for per-turn fills:
1. **The §4.4 overlay has never run at scale here.** It early-outs when no province is unwired
   (`if unwired_keys.is_empty(): return`, `map_renderer_base.gd:506`). The Europe map is **all-wired**, so
   the overlay is a no-op in the smoke — the full-image cost is **untested**.
2. **Owner fills can't early-out.** Every province is owned, so the pass must touch all **1.79M land px**
   (of 4.1M total), per ownership change. The overlay body is per-pixel `get_pixel` + `_color_to_key`
   (string alloc + format) + dict lookup + `set_pixel` — the exact pattern Godot warns is slow. At
   ~1–3µs/px effective that is **multiple seconds**, and it would re-run on **every turn** (ownership
   changes constantly). The smallest province is 575px; the largest 106,777px — a single large capture =
   ~0.1–0.3s of `set_pixel`, a multi-capture turn worse.

**Recommended approach (pick one, decide before Slice 6 starts):**
- **(A) Fragment shader — recommended.** Feed the lookup texture + a tiny **owner-color palette** (≤126
  texels, indexed by province) to a shader that re-tints on the GPU. Ownership change = update one small
  palette uniform/texture; **zero per-pixel CPU work**, instant re-tint, scales to any map size. This is
  the canonical political-map technique and the right answer for a 4.1M-px map that re-tints every turn.
- **(B) Cached pixel-index + dirty-province fallback** (if a shader is undesirable): at load, build
  `region → PackedInt32Array(pixel offsets)` **once** (single full pass). On ownership change, re-tint only
  the provinces that actually changed owner, via `PackedByteArray` writes on `Image.get_data()`. Per-turn
  cost ∝ changed pixels (usually a few k–100k), not 1.79M.

Either is fine; the naive full-image mirror is not. The initial full paint may use the §4.4-style loop
(one-time, tolerable); the **per-turn refresh hook must not**. The plan's Slice 6 should name (A) or (B)
explicitly. Note Golden Rule #8 is about backend hot paths, but the *spirit* (no full scans per turn)
applies to this renderer loop too.

### A — Legacy-as-fixture reconciliation (right call; correct the number)

The plan's "2,462 refs / 190 files" is an **under-count** — actual ≈ **8,463 quoted match-lines across 273
files** (≈6,887/232 even after removing the `Saxony` nation/region name collision; `Belgium` 1,845,
`Paris` 1,734, `Saxony` 1,655, `Waterloo` 1,035 dominate). This does **not** change the decision — it
**reinforces** it. Migrating ~7–8k references onto Europe is clearly the wrong move; **keep the legacy 19
as the default `WorldState()` test fixture** and migrate only the **3 map-contract tests**
(`test_map_consistency`, `test_map_topology_endpoint`, `test_map_bitmap_contract`). What breaks if you
*don't* keep the fixture: every gameplay test that hard-codes `Paris`/`Berlin`/`Vienna` strength, capture,
movement, etc. — thousands of assertions across 273 files, and the pre-commit hook runs the **full** suite
with no `--no-verify`. **Action:** keep the legacy-as-fixture decision; replace the "2,462/190" figure in
the plan with the verified count so the gate isn't blessing a wrong number.

### F — Roster explosion (needs its own phase, not just DEF-4)

Decision #2 ("every sovereign, not capped at 13") realized against this art is **~14–16 independents +
~10 client/vassal states** (roster in §4 below). Consequences the plan files under a single owner-row:
- **Bilateral diplomacy O(N²):** 5 nations → 10 pairs today; 14–16 independents → **~90–120 pairs**.
  `calculate_trade_income` (`diplomacy.py:8863`) already recomputes **all** pairs **every turn, uncached**
  (§5.6 wants it cached). Coalition leader/score sum marshals per member (`coalition.py` ~812/868) — O(marshals×members).
- **Dispatch density (§5.2):** the morning dispatch over 14–16 independents becomes a wall of text — a
  **playability** problem, not just perf. §5.2's categorized-collapse is effectively a prerequisite.
- **Coalition friction (§5.3):** perpetual-war-spiral risk rises with nation count.
- **Authoring debt:** 6+ nations (Ottoman, Sweden, Naples, Bavaria, Portugal, Denmark-Norway, + any new
  independents) have **no `NATION_COLORS`** (utils.gd has 8), **no named diplomat** (chancery fallback is
  fine for v1 — DEF-1), and **no `NATION_DESIRE_PROFILES`/`TALLEYRAND_COMMENTARY`** (CLAUDE.md "Don't Do"
  flags this — unconfigured nations get empty desires + silent missing commentary).

**The saving grace is decision #2 itself:** modeling minors as **vassals** caps the O(N²) blow-up at the
~14–16 *independents*, not the full ~25-entity set — vassals don't get full diplomatic agency. That's
exactly why #2 is the right design. But 14–16 independents is still load-bearing. **Promote DEF-4 to a
dedicated "Roster & Diplomacy Scaling" session** sequenced *before* the final playtest, landing §5.2/§5.3/
§5.6, not "if forced."

---

## 4. The REAL roster from the art (candidate — confirmed during Slice 2)

Geographic coverage of `europe_visual.png` (2560×1600): British Isles, Iberia, France, Low Countries,
Italy, Germany, **southern** Scandinavia, the Balkans/Greece, Anatolia, the Black Sea littoral, the
western-Russian frontier (Poland/Baltic/Ukraine fringe), and a North-African coastal strip.
**Off-map:** Moscow / St. Petersburg / the Russian heartland, and the far north. Province anchors span
x[244–2281], y[42–1563] of the 2560×1600 canvas (the far west = Atlantic, far east ≈ Poland/steppe).

**Likely independents (full agency) — confirm exact owners during Slice 2:**

| Nation | Tier | Capital | Note |
|---|---|---|---|
| France | major | Paris | player |
| Britain | major | **London (real now)** | isles are drawn — retire the Netherlands proxy |
| Austria | major | Vienna | Bohemia/Tyrol/Galicia |
| Prussia | major | Berlin | Rhineland + east |
| Russia | major | **proxy** (e.g. Vilna/Courland) | heartland off-map → proxy capital or owner-row |
| Spain | secondary | Madrid | Iberia unlabeled — heavy Slice-2 research |
| Portugal | minor | Lisbon | |
| Ottoman Empire | secondary | Constantinople (borderline) / proxy | Balkans + Anatolia on-map |
| Sweden | secondary | Stockholm if on-map, else proxy | only southern Scandinavia drawn |
| Denmark-Norway | minor | Copenhagen | |
| Naples / Two Sicilies | secondary | Naples | |
| Papal States | (secondary) | Rome | |
| Bavaria | minor | Munich | |
| Saxony | minor | Dresden | |
| (Sardinia-Piedmont?) | (minor) | Turin | may already be French-occupied 1805 → vassal/owned |

**Likely client/vassal web (patron) — seed into `world.vassals` at build (decision #2):** Batavian
Republic/Holland (France), Helvetic/Switzerland (France), Kingdom of Italy (France), Etruria/Tuscany
(France), the Rhenish/SW-German states — Württemberg, Baden, Hesse, Berg (France), the small Italian
duchies — Parma, Modena, Lucca (France); possibly a Polish/Warsaw entity partitioned among
Prussia/Austria/Russia. **Every minor must resolve to a historically-correct patron** so no province is
orphaned (plan verification item 1b) — this is authored in Slice 3 from the Slice-2 ownership.

**This roster size + proxy list + patron web is a design decision the user should bless at a gate
(below) before Slice 3 wires it.** Whether Britain takes a real London (recommended — the art supports it)
vs. keeping the Netherlands proxy is a specific call to make there.

---

## 5. PHASED MULTI-SESSION ROADMAP

Re-sliced from the plan's 9 slices to **10 sessions**, with two structural changes: **Slice 2 is the
critical-path bottleneck (may span 2 sessions)** and **DEF-4 is promoted to its own session (S6)**.
"Green-suite gate" = pre-commit (`ruff check backend/` + full pytest) stays green; Godot slices add the
parse harness.

| S | Session | Maps to | Why here | Review checkpoint | Green gate |
|---|---|---|---|---|---|
| **1** | **Tooling: land-adjacency deriver + sea-candidate list + validator checks + naming artifact** | Slice 1 (reframed) | Tools/assets only = zero suite risk; de-risks the one hard tool (adjacency) first; produces the naming review artifact | **PAUSE — and confront F1 here: confirm naming is a manual pass, not seed-extraction** | new deriver/validator tests + `validate … --strict` PASS; suite unaffected |
| **2** | **Naming + 1805 ownership research pass** (names, owners, terrain/type/coastal, capitals; hand-fix adjacency; hand-author sea links) | Slice 2 | The schedule bottleneck — geography-driven human research; **discovers the roster** | **Sign off the annotated owner/name overlay province-by-province** | registry-completeness + data-validation tests; assets-only |
| **2.5** | **ROSTER DESIGN GATE** (independents vs vassals; proxy capitals for Russia/Ottoman/Sweden; Britain=London?; patron web) | new (from #2) | Decision #2's realized size has big downstream cost (F6/§4) — bless before wiring | **User approves the roster + patron web** | — (design gate) |
| **3** | **Backend roster config** (NATION_CAPITALS, power_tier, gold/AP/authority, colors ×6+, diplomats w/ chancery fallback, desire profiles + commentary, vassal web, 1805 relations) | Slice 3 | Backend must *know* the roster before the Europe world references it | review roster-completeness test output | parametrized "no nation missing required config" test; suite green |
| **4** | **`create_europe_regions()` + `WorldState(region_factory=…)` seam** (derive income/supply/garrison/slots; **design grid_position bucketing — F5**) | Slice 4 | Build + test the Europe world without changing the default | Europe world constructs + advances a turn | `test_europe_world_construction`; legacy default + gameplay tests untouched |
| **5** | **Backend game cutover** (bootstrap → Europe; migrate 3 map-contract tests; save-version guard DEF-2) | Slice 5 | The backend "replace outright" flip — small because S4 pre-built it | curl `/new_game` = 126-province Europe | map-contract tests migrated; full suite green |
| **6** | **Roster & Diplomacy Scaling** (§5.2 dispatch collapse, §5.3 coalition friction, §5.6 trade-income cache + AI proposal throttle) | **DEF-4 promoted** | Load-bearing for *playability* at 14–16 independents — must precede playtest | dispatch readability + friction sanity | density tests; suite green |
| **7** | **Godot owner-shape fills** (shader **or** cached pixel-index — decide per F2; verify on smoke) | Slice 6 | Frontend-only; can run in **parallel after S3** (needs colors + europe.json) | smoke shows owner-colored provinces, re-tint is instant | source-level renderer test + parse harness 0 failures |
| **8** | **Godot game cutover** (main.tscn → Europe renderer; wire update_all_regions/topology/focus/ledger; retire placeholder) | Slice 7 | Frontend flip — small because S7 pre-built fills | headless instantiation + manual F6 smoke | parse harness 0 + headless instantiation OK |
| **8.5** | **1805 Scenario Setup — DESIGN GATE** (place armies for all 14–16 nations on Europe provinces; author the 1805 diplomatic posture + coalition state; the 9–11 new nations have **zero** marshals today) | new (explicit step at end of plan) | The starting state is hardcoded for 5 nations / 19 regions (`marshal.py`, `world_state.py:381`); re-authoring it at scale is a **second authoring pass**, and the campaign start-point is a design call | **User decides: Third Coalition already at war at turn 1 vs. just before** | Europe world starts with marshals on valid owned provinces + symmetric 1805 matrix; turn advances; legacy start unchanged |
| **9** | **Scale + balance validation + manual playtest** (hot-path audit at 126: trade income, coalition sums, grid_position; AI at 126; economy; full playtest) | Slice 8 | Prove 126 regions × full roster is performant + playable | playtest checklist | scale test at 126 within budget; playtest PASS |
| **10** | **Cleanup & docs** (retire placeholder assets; SAVE_FORMAT/STATUS/CLAUDE/§4–§5 closeout; close DEF rows) | Slice 9 | Close-out | docs reflect shipped behavior | suite green; no dangling `Region_NNN` |

**Dependency graph (critical path in bold):**
`S1 → S2 → S2.5 → **S3 → S4 → S5 → S6 → S8 → S8.5 → S9 → S10**`, with **S7 branching off after S3**
(frontend-only, reads `europe.json` + `NATION_COLORS`) and rejoining at S8. **S8.5 (1805 Scenario Setup)**
depends on S3 (roster) + S5 (Europe world) + S2 (province names for army placement) and must precede the
S9 playtest. S2 may be **2 sessions** (West / Central+East). So **11–12 sessions** total; the long poles are
S2 (naming research) and S8.5 (army + diplomacy authoring) — both human passes, not code slices.

**Is "land Slice 1, then pause" the right low-risk start?** Yes — tools/assets only, zero suite risk, and
it validates the riskiest tool (the adjacency deriver) and produces the naming artifact. Keep it. The one
addition: make the S1 checkpoint also surface F1 so the user enters S2 knowing it is a multi-hour research
pass, and make the S2.5 roster gate explicit before any backend wiring.

---

## 6. Decisions for the gate (the user should rule on these)

1. **Naming method (F1):** accept that naming is a **manual geography pass** (letters layer ≈ initial-letter
   hint only), verified via an annotated overlay — *or* commission spelled-out labels from the artist.
2. **Roster size + proxies (F3/§4):** how many independents; **Britain = real London** (recommended) vs.
   Netherlands proxy; proxy capitals for Russia/Ottoman/Sweden; the exact patron web.
3. **Owner-fill rendering (F2):** **shader** (recommended) vs. cached pixel-index.
4. **Sea adjacency (D):** auto-land + **hand-authored sea** (recommended) vs. the plan's auto sea-heuristic.
5. **Scaling timing (F3):** land §5.2/§5.3/§5.6 as **its own session before playtest** (recommended) vs.
   "if forced."
6. **scenario_config (§5.5):** hardcode the 14–16-nation roster in Python now + owner-row the
   `scenario_config` migration (faster, plan's implicit path) vs. build the loader first as the roster's
   home (cleaner, +1 session). For a prototype, recommend hardcode-now.
7. **Legacy count (F4):** correct "2,462/190" → the verified ≈8,463/273 in the plan; keep legacy-as-fixture.
8. **1805 Scenario Setup (new gate, S8.5):** the campaign **start-point** — Third Coalition already at war
   at turn 1 vs. just before — plus accepting army-placement + 1805 diplomatic-posture re-authoring for
   14–16 nations as its **own explicit step** (end of `MAP_IMPLEMENTATION_PLAN.md`), not a Slice-3 clause.

---

## Appendix — reproduction tooling (read-only; in `C:/Users/User/Downloads/`)

- `_psd_inspect.py` — enumerates all 35 PSD layers + detects/extracts text (proves `TySh`=0).
- `_psd_letters_export.py` → `_letters_over_counties.png` — the County-Colors+letters composite (the naming
  artifact); also prints the 83/126 in-bbox label coverage.
- `_crop_view.py` → `_crop_center.png`, `_crop_east.png` — native-res crops proving the glyphs are single
  letters.
- Validator: `python -m tools.validate_province_map --registry …/europe.json --visual …/europe_visual.png
  --lookup …/europe_lookup.png` → PASS.
- Lookup measurements (gap distribution, per-province px) via the project's own
  `tools.validate_province_map.read_png_rgb_bytes`.

---

## Second independent verification pass — June 22, 2026

A fresh reviewer re-ran every measurement against the live assets and **reconfirmed all findings above**. Reproduced numbers (validator `--strict` → PASS, exit 0; lookup decode; PSD byte-scan; `rg -w` over `tests/`):

- 126 provinces / **126 distinct non-black colors** / sea=black; 2560×1600 = 4,096,000 px; **land 1,788,712 (43.7%)**; province px min **575** / max **106,777** / median 8,741; validator 0 findings.
- Adjacency gap bimodality reproduced: **≤15px (land) 73.6% / 16–40 (ambiguous) 2.9% / ≥41px (sea) 23.5%** (35,633 samples) — decision #5 (auto-land + hand-sea) holds.
- PSD: 35 layers; **TySh=0, Txt=0, TxLr=0** (no editable text anywhere); `letters` rasterized, **83/126** anchors in bbox; layer 14 `help with spain` confirms Iberia incomplete; layer 17 `Map_Napoleon_Total_War` is a placed smart-object underlay.
- **Legacy footprint re-measured larger:** **10,255** word-boundary match-lines across **275 of 326** test files (8,343 / 241 excl. the Saxony collision; Belgium 2,344, Paris 2,129, Saxony 2,034, Waterloo 1,312 dominate). The legacy-as-fixture call is reinforced.
- Direct view of the rendered art confirmed coverage: British Isles, Iberia, Italy + islands, Balkans/Anatolia, Crimea, southern Scandinavia, and a North-African coastal strip are on-map; the Russian heartland/far north are off-map.

Three updates folded into `MAP_IMPLEMENTATION_PLAN.md` (amendment 8):

1. **Roster authoring debt sharpened.** `NATION_POWER_TIERS` already authors 13 nations (tiers mostly done); the real gaps are `NATION_COLORS` (8 incl. "Neutral") and `NATION_DESIRE_PROFILES` (only **4**: Austria/Britain/Prussia/Saxony). `TALLEYRAND_COMMENTARY` has a `_default` fallback (graceful). Prioritize desire profiles.
2. **Roster Design Gate (Slice 2.5)** made explicit, with the researched **1805 North-African owners**: **Morocco independent** (Alaouite sultanate, Sultan Moulay Slimane); **Algiers/Tunis/Tripoli as Ottoman client-regencies** (nominal Porte suzerainty → Ottoman vassals; or independent Barbary minors if the Ottoman is itself a proxy). British Isles confirmed on-map → **Britain = London**; Russia/Ottoman/Sweden are the proxy cases.
3. **Render + parser methods named:** owner fills use a **fragment shader** (or cached per-province pixel-index), not a per-turn full-image mirror (Slice 6, F2); `grid_position` at 126 must pick centroid-bucket vs. parser-refactor (Slice 4, F5).

**Score (this spec, post-amendment):** doability **9** / clarity **9** / gaps **7.5** / completeness **8.5** → **overall 8.5/10 — GO**, start Slice 1; treat Slice 2 (naming) and the 1805 Scenario Setup as the real schedule drivers.

Sources for the North-African ownership research: [state.gov — Barbary Wars](https://history.state.gov/milestones/1801-1829/barbary-wars); [Regency of Algiers](https://en.wikipedia.org/wiki/Regency_of_Algiers), [Ottoman Tripolitania](https://en.wikipedia.org/wiki/Kingdom_of_Tripoli), [Alawi dynasty](https://en.wikipedia.org/wiki/Alawi_dynasty), [Slimane of Morocco](https://en.wikipedia.org/wiki/Slimane_of_Morocco) (Wikipedia).

---

## Third independent verification pass — June 22, 2026

A third reviewer re-ran **every** measurement from scratch against the live assets (validator `--strict`; a full
PSD byte-scan + layer-record walk; a from-scratch lookup decode; a fresh row+column adjacency-gap scan;
**rendered crops of the `letters` layer, inspected by eye**; and read-only Explore sweeps of the backend
seams). The prior two passes' numbers **reproduced almost exactly** — then six items the first two passes did
not capture were surfaced. **No prior-pass finding was withdrawn.**

**Re-measured (matches prior passes):**
- Validator `--strict` → `PASS: no findings`, exit 0.
- Lookup 2560×1600 = 4,096,000 px; **land 1,788,712 (43.7%)**, sea 56.3%; **126** distinct non-black colors,
  **0** unmapped; per-province px **min 575 / max 106,777** / median 8,668 / mean 14,196.
- Adjacency gaps (**35,633** samples): ≤15px (land) **73.6%** / 16–40 (ambiguous) **2.9%** / ≥41px (sea)
  **23.5%**, max 1123px — bimodality holds; auto-land + hand-sea confirmed.
- PSD: 35 layers; `TySh`/`TxLr`/`Txt `/`tySh`/`Txt2` = **0** (only `luni` layer-name records, ×35); `letters`
  (layer 15) bbox (578,160)-(2166,1031), **83/126** anchors inside; layer 14 `help with spain`; layer 17
  `Map_Napoleon_Total_War` underlay. **The `letters` crops were rendered and visually confirmed as single
  hand-drawn capital letters + digits (H, P, V, G, M, S, T, k, B, 3, 5, 7…), one per province, NO words** —
  even where a glyph exists it is an ambiguous initial (a "k" could be Kraków/Königsberg/Kurland). F1 decisive.
- Legacy footprint corroborated: `Belgium` alone = **2,344** matches / **133** files (the original "2,462
  total" was ~4× under).
- Backend seams: REGIONS_DATA=19, `create_regions()` at world_state.py:128 (no factory seam), no
  `create_europe_regions()`; RUNTIME_NATIONS=5; NATION_POWER_TIERS=13; NATION_DESIRE_PROFILES=4;
  NATION_COLORS=8 (incl. "Neutral"); `calculate_trade_income` (diplomacy.py:8849) O(N²), uncached.

**New findings (folded into `MAP_IMPLEMENTATION_PLAN.md` as amendment 9):**

- **N1 — "Britain = London" is entangled with the legacy-as-fixture decision.** `NATION_CAPITALS` is a single
  **GLOBAL** dict (region.py) read by `settlement_scoring.py` (CLAUDE.md's documented Britain proxy), marshal
  spawn locations, and `covets_regions`. The legacy fixture **depends on** Britain→Netherlands. If Slice 3
  mutates the global to "London," it perturbs the very fixture the plan relies on staying green. **Fix:
  scenario-scope capitals** — the Europe build carries its own capital map (seed at construction); the global
  stays Netherlands for the legacy fixture. The prior passes' "retire the Netherlands proxy" is right for the
  *game*, wrong if applied to the *global constant*. (Slices 3 + 4.)
- **N2 — the scenario LOADER already exists.** `WorldState.from_scenario_file()` (world_state.py:4790) +
  `collect_scenario_nations()` / `validate_scenario_runtime_support()` (nation_config.py) + a full
  `backend/modding/validator.py`. What is missing is an **authored 1805 Europe scenario file**, not the
  loader. The 1805 Scenario Setup step should author a **scenario JSON loaded via `from_scenario_file()`**, not
  a second hardcoded `create_*_marshals()` init — this **moots Decision #6** (hardcode-vs-build-loader).
- **N3 — the 1805 diplomatic matrix is a hidden long pole.** 10 hardcoded pairs today (world_state.py:381) →
  **C(16,2) = 120** at the full roster. **Mechanic: default-to-PEACE + author only the exceptions** (the Third
  Coalition, the Franco-Spanish alliance, Prussian neutrality, …) so 120 pairs stays tractable. (Scenario
  Setup step.)
- **N4 — `grid_position` bucketing collides at the suggested ≈12×10.** 120 cells for 126 provinces →
  guaranteed collisions (pigeonhole), and collisions break `resolve_direction()`'s "move north"
  disambiguation (the parser reads a **unique** `(row,col)` per region, strategic_parser.py:33-39). **Fix:
  derive `(row,col)` by centroid spatial-rank** (col = rank of centroid-x within a latitude band, row = rank
  of centroid-y) so every province gets a unique, order-preserving cell — no parser refactor. (Slice 4.)
- **N5 — minor correction:** `NATION_HONOR_BIAS` covers only **2** nations (Prussia, Spain), not the "13" the
  prior passes implied by lumping it with `NATION_POWER_TIERS`. It is sparse/optional (defaults apply), so
  low-impact — but Slice 3 should not assume honor bias is "mostly done."
- **N6 — the broad scale fears (item G) are largely DEFUSED.** Fog is **O(marshals), not O(regions)** (LOW);
  the AI distance cache is **on-demand BFS, not O(N²)-at-init** (LOW); the vassal system is **data-driven with
  no O(vassals×regions) per-turn loop** (LOW, supports ~10 vassals across multiple patrons). The real scale
  risks are narrower than "everything at 126": `calculate_trade_income` O(N²) **uncached**, dispatch/coalition
  density, and **marshal-count growth from the 1805 armies** feeding the O(marshals) fog paths. Slice 6
  (Roster & Diplomacy Scaling) should be scoped to those specific sites.

**Score (third pass, pre-fold):** doability **9** / clarity **9** / gaps **7.5** / completeness **8.5** →
**overall 8.5/10 — GO**; folding N1–N4 tightens gaps toward 8.5. Start Slice 1; **Slice 2 (naming) and the
1805 Scenario Setup remain the schedule drivers.** Reproduction tooling: a single read-only inspection script
(`%TEMP%\_map_review_inspect.py`) re-derives the PSD layer walk + text-signature scan, the lookup geometry,
the adjacency-gap distribution, and the `letters`-layer crops; the project validator runs unchanged.

### Plan-hardening pass — June 22, 2026 (amendment 10)

Four residual gaps were then closed **in the plan** to raise the score by improving the plan, not by inflating
the number:

- **G1 — reversible cutover.** The Slice-4 `region_factory` seam is selected by a config flag
  (`SOVEREIGN_MAP=europe|legacy`): the game bootstrap reads it (Slice 5 sets `europe`) while `WorldState()`
  still defaults to legacy for the fixture. The two "replace outright" flips (Slices 5, 7) become a **flag
  flip — instantly reversible** (rollback = `legacy`), not a code edit. This de-risks the scariest part of the
  cutover.
- **G2 — legacy-fixture immutability guard.** A standing test asserts `create_regions()` still returns the
  unchanged 19 regions (names, owners, adjacency), so the cutover cannot silently perturb the fixture the
  whole suite depends on.
- **G3 — `is_coastal` ↔ sea-adjacency check.** The validator gains a consistency check (every coastal
  province has ≥1 sea edge / borders ocean-black; no inland province carries a sea edge).
- **G4 — concrete budgets.** "Within budget" → numbers: Slice 8 turn resolution ≤ 2× the 19-region baseline
  (measured); Slice 6 owner-fill re-tint ≤ one frame (~16 ms) via the shader.

**Score (post-hardening):** doability **9.5** / clarity **9.5** / gaps **9.5** / completeness **9.5** →
**overall ≈9.3/10 — GO.** It is deliberately **not 10**: the plan is forward-looking — the real roster, the
126 historical province names, and the 1805 diplomatic matrix are *authored during execution* (Slice 2 + the
Scenario Setup gate), and those two human-research passes are irreducible risk no document can remove. A 10
would require those artifacts to already exist and be verified. The honest ceiling for a pre-execution plan is
here.
