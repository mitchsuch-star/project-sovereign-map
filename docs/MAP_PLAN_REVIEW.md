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
| **9** | **Scale + balance validation + manual playtest** (hot-path audit at 126: trade income, coalition sums, grid_position; AI at 126; economy; full playtest) | Slice 8 | Prove 126 regions × full roster is performant + playable | playtest checklist | scale test at 126 within budget; playtest PASS |
| **10** | **Cleanup & docs** (retire placeholder assets; SAVE_FORMAT/STATUS/CLAUDE/§4–§5 closeout; close DEF rows) | Slice 9 | Close-out | docs reflect shipped behavior | suite green; no dangling `Region_NNN` |

**Dependency graph (critical path in bold):**
`S1 → S2 → S2.5 → **S3 → S4 → S5 → S6 → S8 → S9 → S10**`, with **S7 branching off after S3** (frontend-only,
reads `europe.json` + `NATION_COLORS`) and rejoining at S8. S2 may be **2 sessions** (West / Central+East).
So **10–11 sessions** total; the long pole is S2 (human research), not any code slice.

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
