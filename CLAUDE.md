# CLAUDE.md

Napoleonic strategy game. Players type commands ("Marshal Ney, attack Wellington") and AI marshals respond based on personality. Godot 4 frontend, FastAPI backend on port 8005. For game vision see `docs/VISION.md`.

## Golden Rules

1. **Combat modifiers: SINGLE SOURCE in `marshal.py`** — `get_attack_modifier()` / `get_defense_modifier()` only. `combat.py` reads them, never recalculates.
2. **All numbers to Godot: `int()`** — Godot crashes on floats.
3. **All marshals in ONE dict:** `world.marshals` (not separate player/enemy).
4. **State clearing: AFTER reading** — get the value, use it, then clear.
5. **Enemy AI uses SAME executor as player** (Building Blocks principle — same systems, different input values. See `docs/SYSTEMS_REFERENCE.md` §23).
6. **LLM never affects mechanics** — parsing only, executor is deterministic.
7. **Port 8005** (not 8000!) — change in BOTH `backend/main.py` AND `godot-client/.../api_client.gd`.
8. **Scale-ready code: NO per-region scans in hot paths** — Map is scaling to full 1805 Europe. Never iterate `world.regions.values()` in loops called multiple times per turn. Use cached helpers (e.g. `get_active_nations()` is per-turn cached, `get_nation_regions()` for region lookups). If adding a new helper that scans regions, cache the result per-turn and invalidate via `invalidate_active_nations_cache()` pattern.
9. **No open-ended deferrals** — any hidden, cut, deferred, later, v2, or polish player-facing work must name a concrete owner row/spec, landing slice, completion definition, STATUS tracking line, and behavior test. If the work is not going to land, remove the player-facing promise explicitly. Do not leave "future work" labels, disabled placeholders, or vague backlog notes in active specs.

## Workflow: work directly on master

This is a single-developer project with pre-commit-hook test gating and Codex audits run by commit SHA. Branch-per-slice / worktree-per-slice creates state-drift bugs (the branch falls behind master between slices, the merge back is noisy, and the audit prompt still ends up referencing master after merge anyway). The workflow is intentionally single-threaded: one local master worktree, one active implementation path, and audit/fix follow-ups recorded by master commit SHA. The default is:

- **Commit directly to master.** No `claude/<slice-id>` feature branch, no worktree.
- **The pre-commit hook runs `ruff check backend/` + the full pytest suite.** If a commit is blocked, fix the underlying lint/test failures — do not bypass with `--no-verify`. The hook source is tracked at `scripts/git-hooks/pre-commit`; since `.git/hooks/` is not version-controlled, install it after a fresh clone with `cp scripts/git-hooks/pre-commit .git/hooks/pre-commit` (PowerShell: `Copy-Item scripts/git-hooks/pre-commit .git/hooks/pre-commit`).
- **Codex audits target master at the slice's commit SHA.** When emitting an audit prompt, write `Audit master at commit <SHA>...` rather than naming a feature branch. The audit prompt should also instruct Codex to verify any follow-up work continues on master.
- **If the harness spawns a worktree on a `claude/...` branch anyway:** finish the slice in the worktree (avoid mid-session churn), push branch-tip-to-master via `git push origin <branch>:master`, and add a note to the session summary recommending the user disable auto-worktree creation in their launcher.
- **Exception:** Use a feature branch only when the slice is genuinely throwaway/experimental and the user explicitly asks for one.

## Current Phase

**Phases 6, 6.5, 7 Core, 7b — COMPLETE.** See `docs/STATUS.md` for full session history.

### Up Next

- **▶ NEXT UP — REAL-MAP CUTOVER (re-sequenced ahead of the settlement queue, user decision June 22, 2026).** The commissioned Europe map art arrived as a layered PSD (`map final1.psd` — hand-made, NOT AI: a 35-layer sketch→`County Colors`→borders project with a `Map_Napoleon_Total_War` reference underlay). A flat region-key (`assets/maps/europe_lookup.png`, **126 provinces**, sea = pure black) + draft `assets/maps/europe.json` registry were generated from the PSD's `County Colors` layer by `tools/build_region_key_from_psd.py` (stdlib-only, repeatable) and **PASS `tools/validate_province_map.py` with 0 findings**. An in-engine smoke scene is wired + committed: `godot-client/project-sovereign/scenes/europe_map_smoke.tscn` (+ `europe_map.gd`) — loads `europe_visual.png` (the terrain export) + the lookup, suppresses marker nodes, shows hover/click province names. **The Map Implementation Plan is CREATED + APPROVED (design gate ✅ June 23, 2026 → `docs/MAP_IMPLEMENTATION_PLAN.md`, 3-pass review in `docs/MAP_PLAN_REVIEW.md`).** ✅ **Slice 1 LANDED (July 1, 2026)** — adjacency auto-derivation (land + sea-gap candidates) + `--inspect-letters` seed + 3 validator checks; `europe.json` regenerated (248 land edges / 144 sea candidates / 5 islands); validator PASS. ✅ **Slice 2 LANDED (July 1, 2026)** — all 126 provinces authored in `europe.json`: unique historical **names** (no `Region_NNN` left), 1805 **`starting_controller`**, **terrain**/**region_type**, image-derived **is_coastal** (86/40), **is_capital**; **discovered roster = 20 nations** (10 majors: France [player]/Britain/Spain/Portugal/Austria/Prussia/Russia/Ottoman/Sweden/Denmark + 10 minors: Naples/Bavaria/Papal States/Sardinia/Holland/Hanover/Hesse/Kingdom of Italy/Switzerland/Saxony), one owned capital each (Britain=real London; Russia/Ottoman/Sweden = frontier/edge proxies); **12 hand-authored sea links**; **M4+M5 validator hardening IMPLEMENTED** (omitted-vs-empty `adjacent`; `DUPLICATE_ADJACENCY_ENTRY` + on-save de-dupe) + Slice-2 gameplay-field validator checks; validator PASS `--strict`; `tests/test_europe_registry_data.py` (24 tests); suite `10560 passed, 1 skipped`; ruff clean. The owner/name assignment is a **first geographic pass** (visually QA'd via an owner-colored overlay; scaffolding deleted), explicitly staged for the gate. ✅ **Slice 2.5 ROSTER DESIGN GATE BLESSED + Slice 3 LANDED (July 1, 2026).** Gate: user chose real historical vassals/masters → **17 independents + 3 French satellite vassals** (Holland/Kingdom of Italy/Switzerland, `satellite`); Bavaria/Saxony/Hanover/Hesse sovereign → independent; proxy capitals accepted as authored (Britain=London, Russia=Vilna, Ottoman=Constantinople, Sweden=Stockholm, Denmark=Copenhagen); Algiers + Egypt sliver Ottoman (no separate Morocco/Tunis/Tripoli on the art). Slice 3 wired the 20-nation roster as a **scenario-scoped** backend surface in `nation_config.py` (`EUROPE_ROSTER`/`EUROPE_NATION_CAPITALS`/`EUROPE_VASSAL_WEB` + `build_europe_*` builders) + `create_europe_diplomats()` (15 new) + additive `.get()`-lookup extensions (`NATION_POWER_TIERS` +8, `NATION_DESIRE_PROFILES` +16, `TALLEYRAND_COMMENTARY` flavor, Godot `NATION_COLORS` +13) — **never touching the legacy 5-nation globals** (N1). `NATION_HONOR_BIAS` deliberately NOT extended (multiplies live reliability math → broke fixtures). `tests/test_europe_roster_config.py` (18 tests) incl. a legacy-immutability guard; suite `10578 passed, 1 skipped`; ruff clean. Live game still runs the 19-region world (no cutover yet). ✅ **Slice 4 LANDED (July 1, 2026)** — `create_europe_regions()` builds the validated 126-province world from `europe.json` (name-keyed, symmetric adjacency, income/supply/garrison derived, `grid_position` via centroid spatial-rank — N4) behind the `WorldState(sovereign_map="legacy"|"europe")` seam (G1); Europe carries its own capital map/roster/diplomats + the 3 French satellite vassals; `WorldState()` still defaults to legacy (fixture untouched → the cutover is a reversible flag flip). Army placement + the 1805 diplomatic matrix are deferred to the 1805 Scenario Setup gate (Europe starts army-less, turn-stable). `Region.grid_position` added (serialized); `resolve_direction` prefers the live region's grid (world-scoped). `tests/test_europe_world_construction.py` (17 tests); suite `10595 passed, 1 skipped`; ruff clean. ✅ **Slice 5 LANDED (July 1, 2026)** — backend game cutover: the bootstrap (module `world` + `_reset_world_state`/`/new_game`) builds the 126-province Europe world via `main._resolve_sovereign_map()` reading the **`SOVEREIGN_MAP` env flag (default `europe`; rollback = `legacy`, no code change — drilled live)**; `/map_topology` serves the ACTIVE world's graph (126 provinces, Britain=London); the three map-contract tests migrated to Europe (`test_map_topology_endpoint.py` incl. rollback case, `test_map_consistency.py` graph integrity over `create_europe_regions()` with map.gd placeholder guards kept until Slice 7, `test_map_bitmap_contract.py` keyed off `europe.json`); new `tests/test_map_slice5_cutover.py` (11 tests) with the **G2 frozen-snapshot legacy-fixture guard** (names/owners/adjacency/capitals); **DEF-2 landed** (`save_manager.FORMAT_VERSION` 2→3, pre-cutover saves fail with a clear versioned message, `test_save_load.py` case); `test_restart_flow.py` pinned legacy via the flag; conftest autouse isolates `SOVEREIGN_MAP`; `SAVE_FORMAT_REFERENCE.md` updated (v3 + `sovereign_map`/`grid_position`/`is_coastal`); **follow-up fold:** `capture_region` R16 threat + `allied_region_restored` lawful-owner lookups re-pointed from the legacy `get_starting_controllers()` global to the world's own `_starting_controllers` (Europe-only names always missed the legacy dict), regression-tested; suite `10609 passed, 1 skipped`; ruff clean; live curl (both flag values) + validator PASS `--strict`. Gameplay tests stay on the untouched legacy `WorldState()` fixture. ✅ **1805 Scenario Setup DESIGN GATE BLESSED (user, July 1, 2026)** — all 8 open decisions approved as recommended (war underway at the Sept 25, 1805 anchor with exactly Britain/Austria/Russia; Sweden+Naples coalition-committed at PEACE; Wellington→Moore + the anachronistic legacy eight dropped from the scenario; Naples double-game neutral, Hanover registry-true armyless, Mack on Bavaria-owned Swabia, Austria↔Russia ALLIANCE as the Russian passage mechanism; full verified draft + folded verifier corrections in `docs/MAP_IMPLEMENTATION_PLAN.md` §"Researched 1805 opening draft"; note the live loader method is `WorldState.from_scenario`, NOT `from_scenario_file`). ✅ **1805 Loader + Constants PRE-SLICE LANDED (July 1, 2026)** — all 8 approved items + the `starting_wars` loader contract: world-scoped scenario runtime validation (`sovereign_map:"europe"` validates against `EUROPE_NATION_CAPITALS` + the Europe diplomat cast; legacy Venice/Milan rejection contract untouched); `from_scenario` injects the 126-province world when a Europe scenario omits `regions` (army-less — no legacy-marshal injection); every `from_dict` omitted-key fallback reads the world's own construction-time value (incl. the 3 satellite vassals; `nation_starting_regions` derives from loaded control); `SOVEREIGN_SCENARIO=<path>` boots a scenario through `_build_new_world()`/`/new_game` (fails loudly; conftest gained the third autouse isolation fixture); `EUROPE_MANPOWER_POOLS` for all 20 nations; Europe `max_turns` 60 (legacy 40); ALL live `NATION_CAPITALS`/`get_starting_controllers()` reads re-pointed at `world.get_nation_capital()`/`world._starting_controllers` (diplomacy.py's 11 sites + war purpose, vassal loyalty, capture classification, settlement ratify/baseline, enemy AI, template capital exclusions, dispatch/ledger display, spawn/retreat, parser/objection heuristics — legacy-identical; Vienna/London captures now move war score, test-pinned); `NATION_HONOR_BIAS` +14 authored (**Russia EXPLICITLY 1.0** — DG-4 spec-closure fixtures pin Russia-breaker deltas at neutral bias; re-biasing Russia is owned by the 1805 balance pass with those fixtures), Austria `EUROPE_BASE_ACTIONS` 3→4, Russia `EUROPE_NATION_GOLD` 1500. Scenario wars seed via the ordered `starting_wars` list through `ensure_war_instance_for_pair` (France-first ordering = ONE shared coalition instance, Britain defender leader) — never raw `war_instance` JSON. `tests/test_map_1805_loader_preslice.py` (40 tests) + 3 mock-world/back-compat test repairs; suite `10649 passed, 1 skipped`; ruff clean. **▶ IMMEDIATE NEXT ACTION: author `europe_1805.json` against the landed loader** (authoring notes in the plan §pre-slice LANDED banner: omit `regions`, `starting_wars` France-first, coalition keys `active_coalition`/`threat_level`/`coalition_count`, boot via `SOVEREIGN_SCENARIO`; incl. the carried `allied_region_restored` Europe behavior test), **then Slice 6 (Godot owner-shape fills) → Slice 7 (Godot game cutover)**. Until Slice 7, the Godot client still renders the 19-region placeholder — set `SOVEREIGN_MAP=legacy` to play end-to-end in the interim. **The settlement Gate 4 smoke + Slice G/G1 below are sequenced AFTER this map cutover.**
- **(Now AFTER the map cutover above) the ONE end-of-queue Gate 4 manual smoke (the queued settlement CH code-health work — CH-1..CH-5 — is ALL LANDED June 10, 2026: CH-1 seven-module split + public door; CH-2 dispatch tables + CH-4 baseline convergence + CH-3 legacy-store deletion in one follow-up slice; CH-5 landed with GT-Slice-1; CH-6 BBCode-palette centralization + CH-7 test-shape rules of thumb remain unqueued recommendations owned by the pre-flight audit ledger), then Slice G/G1. Settlement Guided Terms IMPLEMENTATION is COMPLETE (v0.2 APPROVED June 10, 2026 — D4 confirmed; GT-Slice-1 + GT-Slice-2 + GT-Slice-V + GT-Slice-3 LANDED June 10; GT-Slice-4 LANDED June 10 — the freeform editor is retired per spec §5's complete inventory, session confidence report delivered, awaiting user review); the Gate 4 manual smoke runs ONCE at the END of the queue (user re-sequencing, June 9, 2026). Settlement Conversational Re-front — v0.6 APPROVED May 29, 2026 (design gate cleared; Slice 0 + Slice 1 + REFRONT-V voice LANDED May 30; Slice 2 IMPLEMENTED + audit fold folded on master; Slice 3 IMPLEMENTED May 30 + post-implementation audit fold; Gate-4 pre-flight fix slices PF-1/PF-2/PF-3 LANDED June 9 — ALL implementation slices done; the OQ#4 focused-court breakdown, owned as REFRONT-9, LANDED June 10 inside Guided Terms GT-Slice-3 per GT-A4):** `docs/SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` is now **v0.6** and audited in `docs/SETTLEMENT_CONVERSATIONAL_REFRONT_AUDIT.md` (v0.2 GO-with-changes, 4 folded; v0.3 second run GO; v0.4 third run — Codex **NO-GO**, 1 CRITICAL + 4 MAJOR + 1 MINOR, folded; **v0.5** fourth run — Codex **NO-GO**, 1 CRITICAL (§5 stale "ratification gate = unchanged" vs the per-court gate change in §7/§11.4/§15) + 3 MAJOR (§17 direction read "side-pressure" not `direct_scores[court]`; §11.2 prose listed `feedback`/`top_components` absent from its compact schema; STATUS/audit-note version drift) + Run-#3 items (baseline-target-vs-carry-gate holdout note, `carries` null/hard-stop definition, §17 "conference" shorthand callout), all verified against live code and folded; **v0.6** fifth run — a synthesis of a Claude **NO-GO** (1 CRITICAL: §8 OQ#5 read a `.score` attribute on `select_direct_score`, which returns a `(int, str)` tuple-or-`None`, and neutral-floored a `None` the scorer hard-stops; + 1 MAJOR: direction thresholded by the side-pressure constant `LOSING_SIDE_PRESSURE_THRESHOLD`) with a Codex **GO** (2 MAJOR: §15 band-display row attributed `band`/`top_components` to the raw scorer instead of `_enrich_acceptance_display`; stale STATUS/audit version text; + 1 MINOR), all re-verified against live code and folded — one Claude finding (DWL-SET-SC5R-3 at cleanup `:589`) withdrawn on verification as a correct cite). **Slice 2 IMPLEMENTED May 30 (audit fold folded on master):** Tier-2 intent dials (`settlement_dial_harsher`/`generous` whole-table + focused court via `_redial_settlement_terms`, magnitude/count only — never swaps requested region/payer identity; focused dialing via per-row `dial_actions` Press/Ease — OQ#1/§17), `settlement_cover_add`/`drop` (re-draw baseline for new set + `ignored_participants`/`remaining_wars`), `settlement_focus_court` (presentation-only), live band/`delta_display`, voice-only `targeted_posture_advisory`, the §15 F-5 `balance_projection` memoization param + one-shared-projection aggregator pass, and the structured `action_params` transport for per-row affordances. **Audit fold applied:** the focused-dial seed now honors `MAX_SETTLEMENT_CLAUSE_COUNT` (maxed package → valid no-op redraft, not an over-cap draft) + a symmetric proposer-leader guard. 18 new tests in `tests/test_settlement_refront_slice2.py`; full deterministic + default-random suites `10298 passed, 1 skipped`; ruff clean; Godot 4.4.1 parse 0 failures. **Slice 3 IMPLEMENTED May 30 + audit fold** (V1–V3 cross-court validity in `validate_settlement_terms` + `covered_enemy_participants` threaded into POST-preview/Submit/restage; P2 `_nation_control_options` proposer-side+covered filter for every role + `_side_partitioned_options` disjoint side lists for forced_alliance/liberation; P3 coverage re-filter; **REFRONT-8** Godot editor consumes `enabled`/`disabled_reason_display`; **DWL-SET-SC5R-3** inline merge-conflict Discard/Replace controls; adjust-terms-focused header; **audit fold: ratify gate now re-runs V1–V5 against the live world** via `_normalize_staged_terms_for_validation` + `validate_settlement_terms(enforce_solvency=False)` — a CRITICAL fix, a stale liberation could otherwise release an uncovered party's vassal; 15 tests in `tests/test_settlement_refront_slice3.py`; full deterministic + default-random suites `10314 passed, 1 skipped`; ruff clean; Godot 4.4.1 parse exit 0). **PF-1 + PF-2 + PF-3 LANDED June 9, 2026** (pre-flight defect ledger D1–D6 fixed, D7 latent/owned by CH-5; `settlement_losing` unblocked; +52 tests incl. the standing `tests/test_settlement_baseline_scenario_matrix.py` harness; full suite `10383 passed, 1 skipped`; ruff clean; Godot 4.4.1 parse 0 failures). **The Gate 4 manual smoke is RE-SEQUENCED (user decision June 9, 2026): it runs ONCE at the END of the settlement queue** — after the Guided Terms implementation (gate PASSED June 10) + remaining queued items — and stays the gate for Slice G. **`docs/SETTLEMENT_GUIDED_TERMS_SPEC.md` v0.2 APPROVED June 10, 2026 — D4 (mixed-direction rows: every court row exposes demand AND offer groups, direction picks which leads) EXPLICITLY CONFIRMED by the user on the probe-verified `concession_credit` sweetener rationale. The Run #1 design-gate audit (`docs/SETTLEMENT_GUIDED_TERMS_AUDIT.md`, June 10, 2026 — GO-with-changes, 0 CRITICAL / 9 MAJOR / 6 MINOR, five executed fixture probes) and the GT-A1..4 amendments are FOLDED into v0.2. **GT-Slice-1 + companion CH-5 LANDED June 10, 2026** (the three demand-mutation verbs `settlement_demand_add`/`remove`/`set_magnitude` + §3.4 treasury line + §3.5 `authored_by` tag/dial-composition rule + full §7 wiring, all riding the new CH-5 response-shape wrapper around `handle_settlement_dialogue_action` — failures always re-attach the dialogue + render `error_display`; +47 tests incl. the PF-3 matrix extension; full suite `10430 passed, 1 skipped`; see STATUS.md). **GT-Slice-2 LANDED June 10, 2026** (GT-Slice-1 user-reviewed/approved same day; per-court `demand_suggestions[]` — both D4 groups, direction-led, eligibility-gated, table-scoped §3.4, OQ-1 `region_options[]`/`vassal_options[]`, §4 capacity-bounded `gold_per_turn` pre-fill — + `current_demands[]` with magnitude metadata and verb-ready `remove_action`/`set_magnitude_action`, §3.3 row authoring states `can_author`/`lead_group`/`authoring_disabled_reason_display`, per-court `direct_score`, and the §8 OQ-6 `budget_bound_recommendation` cheapest-signature block; +17 tests; full suite `10447 passed, 1 skipped`; see STATUS.md). GT-Slice-2 USER-APPROVED June 10 (review pause cleared). **GT-Slice-V + GT-Slice-3 LANDED June 10, 2026 (one combined session per the agreed cadence):** V — the DC-4 guard line verbatim ("They are not the ones suing for peace, Sire — but as you wish.") fired on BOTH D5 triggers (explicit demand-group add + focused-Harsher dial seed on a concede-direction court) as one-shot `authoring_voice_beats` on the restaged dialogue; named-court `settlement_multi_court_demand_received`/`offer_received` reactions (resolve_named_diplomat, chancery fallback); the 11 `settlement_guided_reason_*_talleyrand` committed templates replace the plain suggestion reasons; the OQ-6 `recommendation_voice` extends the budget-bound advisory; the §5 incoming-offer revision copy retargeted off the editor; Voice Bible §16.1a updated; SC-32 D5 boundary test extended over all 17 new templates. 3 — `proposal_confirm_popup` three-region layout (header / UX-5 ScrollContainer per-court table / footer): treasury line, `current_demands[]` lines with per-line Remove + clamped magnitude steppers, the inline `Add demand` expansion (§3.3 lead-group ordering, OQ-1 dropdowns, Continental System sub-link, reason lines), all emitting the backend's ready-made `action_params` through `send_dialogue_response_with_params`; **REFRONT-9 LANDED** (rows carry the display-ready 10-component `component_breakdown` from the existing score pass; court-name click round-trips presentation-only `settlement_focus_court`; the focused row expands the full table incl. `concession_credit`); **UX-2** (REVIEW frozen — server rows carry no dial/holdout affordances outside PROPOSE + a STAGED FOR REVIEW render branch with promoted blockers) + **UX-5**; the §9 D4-lesson HTTP-boundary test caught a real dispatch gap (the executor keyed only on `action_params["action"]` while the Godot wire carries the verb in `choice` — fixed with a choice fallback); +19 tests; full suite `10466 passed, 1 skipped` both orderings; ruff clean; Godot 4.4.1 parse harness regenerated 0 failures + headless scene-instantiation check. **GT-Slice-V + GT-Slice-3 APPROVED June 10 under the user-delegated confidence gate (100% contract confidence — landed at `d339dbc`).** **GT-Slice-4 LANDED June 10, 2026** (the freeform editor retired per spec §5's complete inventory — `settlement_editor_popup.tscn`/`.gd` deleted; the identity-picker schema + EDIT payload contract removed with the eligibility/candidate helpers KEPT; the verify-dead `CommandRequest` field pass removed the dead `/command` submit transport — `propose_common_peace` always lands guided PROPOSE, REVIEW only via `submit_settlement_for_review`; the §6 merge dissolution replaced `merge_same_war_settlement_drafts` with mounted-draft-wins refresh semantics; the three editor-mount producers re-point to guided PROPOSE incl. incoming-offer counter-authoring with preserved provenance; the enumerated editor-test disposition executed; REFRONT-7 + UX-3 + UX-8 closed moot; suite `10422 passed, 1 skipped` both orderings; new `tests/test_settlement_gt_slice4.py`). Immediate next action: **the ONE end-of-queue Gate 4 manual smoke (CH-2 + CH-4 + CH-3 LANDED June 10 — the CH ledger is closed)**, then Slice G/G1.** The audit doc also owns the captured recommendation ledgers: design **DC-1..6**, UX **UX-1..9**, code-health **CH-1..7** (the `settlement_preview.py` split is now pre-smoke under the re-sequencing, but never interleaved with the smoke run itself), and diplo-wide **DW-1..5**. **Slice 1 LANDED May 30** (`compute_settlement_baseline` per-court direction + `dialogue_mode="PROPOSE"` payload + per-court ratification gate + PROPOSE surface + REFRONT-V multi-court voice; 22 new tests; full suite green; Godot 4.4.1 parse exit 0 — see STATUS.md). Slice 0 already LANDED. Gate 4 smoke surfaced that the SC-5R-2 editor diverged from the conversational bilateral-diplomacy pattern (only the rawest clause-assembly tier, a blank unguided form allowing invalid combos like self-referential `liberation` rejected only at Submit). The re-front makes common peace work like a bilateral peace proposal: Talleyrand proposes a valid baseline (Tier 1), you steer by intent (Harsher / More generous, whole-table or focused court — Tier 2) with **live per-court acceptance**, and the structured picker editor becomes the **opt-in valid-by-construction deep tier** (Tier 3, reached via `Adjust terms`) — extended to **multi-party** (a multi-court settlement table — one settlement covering a set of enemy courts, each scored independently; per cleanup SC-32 D5 no player-facing "conference"/"veto" copy). Mostly wiring existing machinery (`generate_suggested_terms`, `calculate_common_peace_acceptance` — which already accepts memoized score inputs, the concession-baseline generator, Voice Bible) **plus one deliberate, user-approved mechanics change**: the ratification gate moves from single-`accepting_leader` to **per-covered-court** (`carries` iff every covered court ≥ threshold; holdouts block but offer one-click Ease/Drop), chosen for UX + historical analogue (separate Napoleonic peaces; holdouts fight on). Now approved (May 29, 2026) → Slice 0 + Slice 1 + the REFRONT-V multi-court voice family LANDED (May 30); Slice 2 IMPLEMENTED + audit fold folded on master; Slice 3 IMPLEMENTED May 30 (REFRONT-8 + DWL-SET-SC5R-3 LANDED); PF-1/PF-2/PF-3 LANDED June 9; remaining work is the **Guided Terms implementation (v0.2 APPROVED June 10) + queued settlement items, then the single end-of-queue Gate 4 manual smoke**, then Slice G. The SC-5R-2 editor and the `suspend_settlement_editor` Back Out fix remain LANDED — this re-fronts the front door, it does not revert them. **Interim band-aid = Slice 0 (independent de-risk) — LANDED at master `4ffdfcc` + `3c7a55e`:** shipped the **backend** picker valid-by-construction contract from `SETTLEMENT_UI_CLEANUP_SPEC.md:601` (`_build_clause_control_schema_for_review` now computes per-clause `enabled` + `disabled_reason_display`; liberation offers vassal-only) plus the line-618 test; the Godot editor consumer is **REFRONT-8**, folded into Slice 3. Slice G AI-ally agency stays separate and later.

- **Imperial Settlement routing (updated June 9, 2026; supersedes the May 10 v0.27 handoff):** The cleanup spec is now `docs/SETTLEMENT_UI_CLEANUP_SPEC.md` **v0.32 GO** — the five cleanup slices + the **SC-5R editor** + **SC-32 / Slice G2** are **LANDED** (G2-Slice-1 through G2-Slice-5 + G2-Slice-G2a–G2f; see the SC-5R LANDED paragraph below and `docs/STATUS.md`). **Gate 4 manual smoke (incl. the rejected/losing concession path) is still open, RE-SEQUENCED (user decision June 9, 2026) to run ONCE at the END of the settlement queue** (after the Guided Terms implementation + queued items); it remains the gate for Slice G. The **Settlement Guided Terms implementation is COMPLETE** (v0.2 APPROVED June 10, 2026 — D4 confirmed; **GT-Slice-1 + CH-5 LANDED June 10 at `4c32e59`; GT-Slice-2 LANDED June 10 at `dc40012` and USER-APPROVED; GT-Slice-V + GT-Slice-3 LANDED June 10 (incl. REFRONT-9 + UX-2/UX-5); GT-Slice-4 LANDED June 10 — the freeform editor is retired per spec §5; CH-2/CH-4/CH-3 LANDED June 10 — the next-up forward item is the end-of-queue Gate 4 manual smoke**), following the Settlement Conversational Re-front v0.6 (**APPROVED May 29, 2026; Slices 0–3 + REFRONT-V voice + PF-1/2/3 IMPLEMENTED/LANDED; REFRONT-9 LANDED June 10 inside Guided Terms GT-Slice-3 per GT-A4**), which re-fronts the SC-5R editor. Routing rules that still hold: do not send implementers back to G2-Slice-1; the rejected/losing-side contract is normative in the v0.32 spec (blocked ratification omits `confirm_settlement` from `options[]`; `Revise Terms` only when it opens a real edit-capable route — **per GT-Slice-4 that route is the guided PROPOSE surface**; failed review routes to `Open War Detail`; valid below-threshold drafts Submit into blocked REVIEW but cannot Ratify; losing-side concession authoring re-stages guided PROPOSE seeded from the concession baseline). SC-32 / Slice G2 resolved its agency questions **mostly as cuts**: `Wait for Enemy Offer` / `Ask for terms` were **terminally removed** (D2 — only the distinct `Request Terms` lifecycle survives, owned by Slice G1); AI counterproposals (D1), voluntary alignment (D3), and conference/veto (D5) are cut. The remaining **unbuilt** AI work is **Slice G1** (offer producer + Request Terms), **Slice G2 follow-through**, and **Slice H** (deferred petitions), all owned by the cleanup spec; `Surrender terms` lands in SC-31 / G2-Slice-8. Do not follow older v0.19–v0.27 or Slice E / Final Gate paragraphs as active routing.

  Verification focus: blocked settlement confirmation must not collapse to a lone `Back Out`; losing a war must still permit peace-seeking agency through concessionary treaty authoring; `Open War Detail` is the recovery route for bilateral peace / armistice choices; enemy-offer waiting remains hidden until SC-30 ships; direct pair substitute CTAs remain hidden until SC-29 ships; `Surrender terms` remains hidden until SC-31 ships; and `Revise Terms`, incoming offers, ratification, and War Detail recovery must remain distinct surfaces.

  Manual smoke shortcut: set `SOVEREIGN_SMOKE_START=settlement_multilateral` before Gate 4 manual settlement UI smoke when you want a new game to start directly in one shared France vs Britain + Prussia `war_instance` with Britain as defender leader. Leave it unset for the canonical campaign start.

  The next Imperial Settlement paragraph is retained as historical Slice E context only; do not follow its Final Gate instruction unless `docs/STATUS.md` is later changed back to that gate.

- **Historical Imperial Settlement Slice E handoff (superseded — see current routing above):** B3 lifecycle + Slice C1a/C1b + Slice C2 preview/ratification + Slice D1/D2 settlement & cross-war reaction routing + **Slice E presentation, ledger, and logs** are all landed. Slice E ships `backend/game_logic/settlement_presentation.py` (settlement-only `SETTLEMENT_ROUTES` distinct from `COMMITMENTS_ROUTES` per spec §11.6 line 1290; `is_settlement_event_visible` for the §11.6 fog rule; `cap_settlement_dispatch_lines` + dispatch-side `_enforce_settlement_primary_beat_cap` for the spec §11.6 line 1279 top-four cap with digest overflow; `apply_warning_cap` for spec §16.3; `build_settlement_review` for spec §16.2 Terms / Allies / Warnings / Acceptance sectioning at compact / medium / verbose density; `detect_awe_set_pieces` for spec §20.8; `settlement_notification_meta` for the rail; `recent_settlement_summaries` for the diplomatic ledger; `build_contribution_share_rows` for the war status panel). `dispatch.py` now routes `settlement_summary` / `settlement_digest` events through their own fog filter + formatter and enforces the per-ratification top-four cap on dispatch lines. `campaign_log.py` adds a settlement fog branch routed through the new presentation filter. `diplomatic_ledger.py` exposes `recent_settlements` in the ledger payload. `war_status.py` decorates each war entry with `contribution_share[]` + `contribution_overflow_count` + `war_instance_id`. Godot: `top_bar.gd` wires `ledger_settlements` into `open_diplomatic_ledger_review`; `diplomatic_ledger.gd` adds `open_to_settlements()` and a Recent Settlements block inside the Treaties tab (CanvasLayer 50, one-screen rule preserved); `main.gd` routes `settlement_review` / `diplomatic_ledger` / `ledger_settlements` review targets to the layer-50 ledger; `war_status_panel.gd` extends the war tooltip with the top-five standing list + overflow count. Diplomat Voice Bible 16.1 settlement families remain the contract for final committed copy. Verification at that time: `tests/test_settlement_presentation.py` **`65 passed`**; settlement focused suite **`304 passed`**; full suite **`9736 passed, 1 skipped`**; ruff clean across `backend/`. Treat the old Final Gate routing in this paragraph as historical; the active route is the current routing above (cleanup v0.32 GO + Re-front v0.6 next-up + open Gate 4 smoke).

- **Imperial Settlement Slice C1b context:** `calculate_common_peace_acceptance(world, *, war_id, war_instance, proposer_side, accepting_side, accepting_leader, covered_enemy_participants, settlement_terms, ...)` in `backend/game_logic/settlement_scoring.py` ships the spec §6.acceptance acceptance-component table — C1b shipped these nine (`base_side_pressure`, `settlement_tier_legitimacy`, `term_harshness_penalty`, `burdened_participant_penalty`, `leader_own_losses`, `war_objective_alignment`, `projected_hegemony_mod`, `war_exhaustion`, `abandoned_by_ally_acceptance_mod`); **G2 later added a 10th, `concession_credit`, so live code now sums 10** (`settlement_scoring.py:2070-2081`, docstring step 10 at `:1917`). Acceptance threshold `>= 50` accept, `35-49` near_acceptable with top-2-component feedback, `< 50` hard reject. Each component helper is exported separately (`calculate_base_side_pressure`, `calculate_term_harshness_penalty`, `calculate_settlement_tier_legitimacy`, `calculate_leader_own_losses` (sum-then-clamp `[-25, 5]`, lost-mapped-holdings sub-cap `-10` per spec line 1186), `calculate_burdened_participant_penalty` (per-burden table + aggregate cap `-30 * min(burdened, 2)` floored at `-60`), `calculate_war_objective_alignment` (5-WPS-objective table + selection chain per spec line 1174 — leader-vs-accepting → leader-vs-covered → all-proposers WPS-priority → oldest `created_turn`), `calculate_war_exhaustion_component` (intentional **floor** division per spec line 1120, distinct from `round()` everywhere else), `calculate_abandoned_by_ally_mod` (`+5/defector` last 3 turns, capped `+15`)). New `project_balance_after_settlement(world, *, war_id, settlement_terms)` is the pure projection helper for `projected_hegemony_mod` per spec line 1200-1217 — applies term deltas to in-memory snapshots only, never mutates `world.regions` / `world.diplomatic_states` / `world.vassals` / any cache. New `compute_forced_alliance_threat_preview(...)` exposes the projected `+15/clause` threat delta + crossed coalition thresholds (60 brewing / 80 instant / 90 cooldown-override) per spec line 1273. `calculate_raw_treaty_harshness(treaty)` lands in `backend/game_logic/diplomatic_templates.py` alongside the existing 1.0-clamped `calculate_treaty_harshness()` (bilateral callers unchanged). Britain current-map proxy (`NATION_CAPITALS["Britain"] == "Netherlands"`) is treated as configured scenario data per spec line 1186, not as a separate settlement identity. C1b is pure (no mutation, no ratification, no live wiring into `diplomacy.py` / `diplomatic_templates.py`). Verification: **57 new tests in `tests/test_common_peace_acceptance.py` (component pin tests + 14 tuning-gate fixtures including Pressburg worked example, Tilsit non-leader burden, coalition split, decisive-victory-without-total, total-victory-harsh-terms, minor-power limited, mixed-strength partial-vs-full, full-Europe narrow/full/serial comparison, 6+ participant coalition, Britain-led defense, mapped-home/capital/holdings variants, multi-forced-alliance threat preview, AI-defender alignment ≤ +5, war-exhaustion exploit) + 3 raw-vs-clamped harshness tests in `tests/test_common_peace_harshness.py` + 7 projection / no-mutation tests in `tests/test_settlement_balance_projection.py`** = +69 net. Full suite **`9607 passed, 1 skipped`** (was `9538`); ruff clean. **C1b foundation locked. Remaining: tuning-escalation knobs (only adjust if Slice C2 stress fixtures fail design targets — order: `base_side_pressure` ±0.05 → accept threshold 50→40 → halve `projected_hegemony_mod` for `total_victory` only → bounded `military_supremacy_bonus` → `common_peace_coverage_bonus +3/extra capped +12`, recorded in `SYSTEMS_REFERENCE.md` if any constant changes), then C2 endpoints/dialogue/advisory/Godot routing, then D1/D2 reactions, then E presentation surface.**

- **Scale Readiness Phase 1 — COMPLETE.** 11 new tests, hardcoded `== 19` removed, validator derives from NATION_CAPITALS.
- **Scale Readiness Phase 0 — COMPLETE (7/7 DECIDED).** DG-1 (13 nations, 20+ capable), DG-2 (bilateral + salience filter, 5-row cap), DG-3 (supply deferred), DG-4 (direct-only bilateral call-to-arms, no transitive cascade), DG-5 (raw-count hegemony victory), DG-6 (scenario-configured pacing, `scenario_schema_version: 1`), DG-7 (categorized dispatch). Cross-cutting: `power_tier` is authored scenario data with canonical enum `major / secondary / minor`; `political_status` is runtime state. See `docs/SCALE_READINESS_PLAN.md` §Phase 0 for the canonical taxonomy.
- **Scale Readiness Phase 2 — COMPLETE.** Distance cache, AI spatial-index wiring, live AI fog path, and the `enemy_ai.py` raw scan-conversion pass are landed suite-green. See `docs/STATUS.md` and `docs/SCALE_READINESS_PLAN.md` §Phase 2.
- **Map Readiness Closure Pass — Phase 3 COMPLETE (§§3.1-3.4) + §§4.1-4.4 COMPLETE.** Phase 3: §3.1 (nation config factory — `DEFAULT_NATION_DEFAULTS` fallback + `create_marshals_from_data` / `create_diplomat_from_data` factories; adding a new nation now only needs a capital + diplomat + optional override), §3.2 (shared topology endpoint — backend `GET /map_topology`), §3.3 (centralize nation colors), §3.4 (prompt/parser fallback de-hardcoding). §4.1: province registry schema v2 in `session8_placeholder_provinces.json` — every region carries `province_id`, four per-feature anchors, `wired`/`interactive` flags; renderer parses new fields, gates hover/click on `interactive`, pre-filters `update_all_regions()` on `wired`. §4.2: external bitmap loading — `map_renderer_base.gd` exposes `_get_map_visual_bitmap_path()` / `_get_map_lookup_bitmap_path()` hooks plus `_load_map_images() -> bool`; loader resolves imported bitmap assets via `ResourceLoader`/`Texture2D.get_image()`, validates size + lookup-color compatibility at runtime, latches failures once, and `_build_map_textures()` tries the bitmap loader FIRST before falling back to circle generation. Placeholder `map.gd` does NOT override the hooks — dev mode stays on circles. §4.3: offline color-map validator at `tools/validate_province_map.py` — stdlib-only standalone CLI gating commissioned-art deliveries. Six failure codes (`SENTINEL_COLLISION`, `DUPLICATE_LOOKUP_COLOR`, `SIZE_MISMATCH`, `MISSING_PROVINCE`, `INSUFFICIENT_COVERAGE`, `UNMAPPED_COLOR`) + connected-island `TINY_ISLAND` warning; `--json` and `--strict` CLI modes; header-only visual PNG sizing plus a pure-Python lookup PNG decoder for 8-bit RGB/RGBA + all five scanline filters with malformed-PNG wrapping. 29 tests in `tests/test_province_map_validator.py`. The placeholder JSON is pinned to always pass registry-only checks. §4.4: unwired province support — `_apply_unwired_grey_overlay(visual_image, lookup_image)` lerps `UNWIRED_GREY_COLOR (0.32, 0.32, 0.34)` over unwired lookup pixels by `UNWIRED_GREY_BLEND = 0.7`; called after `province_lookup_image` is set but BEFORE texture creation on BOTH circle-fallback AND bitmap paths, so tint is uniform across art sources. `_is_region_wired()` + `_unwired_lookup_keys()` gate through `province_shapes` (default wired when region is unknown). `MOUSE_BUTTON_LEFT` click handler short-circuits on unwired BEFORE emitting `region_clicked`. `_draw()` routes unwired hovers to `_draw_unwired_region_tooltip()` (renders `"<name>" / "(not yet in play)"` in a dim-panel variant) BEFORE the `region_full_data.has()` branch (which §4.1 excludes unwired regions from). Hover hit-test path (`_lookup_region_from_color_map()`) is unchanged — it still gates only on `interactive`, so unwired-but-interactive provinces remain hoverable. 16 new tests in `tests/test_map_renderer_cutover.py` (source-level) + new `tests/test_map_unwired_overlay.py` (behavioral overlay mirror). All non-art map-readiness items now closed; commissioned art integration + final renderer smoke remain art-blocked. See `docs/STATUS.md` and `docs/SCALE_READINESS_PLAN.md` §§3-4.
- **Memory and Pressure v2.4.3 — COMPLETE.** All slices landed (B-Hegemony, B-B1-lite, B-B3, B-B7, B-B4, C-lite, D3). See `docs/RELIABILITY_IMPLEMENTATION_PLAN.md`.
- **Peace Deals - Settlement UI Cleanup `DWL-SET-SC5R` is LANDED (SC-5R-1 backend + SC-5R-2 Godot editor) — and the editor it shipped is now RETIRED (Guided Terms GT-Slice-4, June 10, 2026): the scene/script, EDIT payload contract, and structured submit transport are deleted; the guided per-court rows are the only authoring tier. What SURVIVES from SC-5R: the scoped `draft_key` persistence + PF-2 war-scoped restore, the non-destructive `suspend_settlement_editor` Back Out (now the PROPOSE rail's), the archived-war `settlement_history` routing, the incoming-offer labels, and the pre-stage/pre-ratify revalidation. The rest of this bullet is historical.** SC-5R-1 backend EDIT payload contract + scoped `draft_key` persistence + `author_gold_indemnity_terms` schema fix + tampered/cut clause-type pre-stage and pre-ratify revalidation landed at commit `e081672` (22 + 6 post-audit tests). SC-5R-2 ships the Godot EDIT-mode editor popup at `godot-client/project-sovereign/scenes/settlement_editor_popup.tscn` + `scripts/settlement_editor_popup.gd` on CanvasLayer 112 (clause add/edit/remove controls + covered-enemy picker + Submit for Review button + Back Out preserving the scoped draft), `_execute_propose_common_peace` calls `load_scoped_settlement_draft(...)` when no explicit terms are passed so War Detail reopen restores the prior authored draft, `_on_war_settlement_clicked` consults the cached active war list and routes previously seen archived wars to `settlement_history` instead of POSTing a stale `propose_common_peace`, and `build_incoming_settlement_offer_popup` labels match behavior (`Review Settlement Offer` / `Reject Offer` instead of `Accept Settlement` / `Reject Settlement` because the handler stages a review rather than ratifying). 41 SC-5R-2 tests after follow-up repair; full deterministic + default-random suite `10252 passed, 1 skipped`. The editor Back Out now sends the non-destructive `suspend_settlement_editor` dialogue action, which pops the staged `settlement_confirm` hard-stop (so ordinary commands are no longer held at the executor gate) while preserving the scoped draft — distinct from `back_out_settlement`, which discards. Inline merge-conflict sub-controls (spec line 589 `Discard new clause` / `Replace active clause` buttons) are queued as follow-up `DWL-SET-SC5R-3`; the editor currently remounts with humanized inline error text on merge conflict. Player-quality gate is **GO pending Gate 4 manual smoke evidence** (including rejected/losing concession path). G2-Slice-1 through G2-Slice-5 plus G2-Slice-G2a-G2f remain landed. Slice G AI-ally settlement agency unblocks after Gate 4 smoke; SC-5R-2 Codex audit repair is complete on `master`.
- **Session 8 Renderer — ART-BLOCKED.** Slices 1-3 complete. Remaining: commissioned art-backed layers + Godot smoke validation. See `docs/STATUS.md`.
- **Architecture Refactoring — Sessions 1-16 COMPLETE.** R19 (modding) remaining. R14a-d deferred. See `docs/ARCHITECTURE_REFACTORING_PLAN.md`.
- **Design Refinement — full queue.** War bargains deferred to Peace Deals phase (`docs/WAR_BARGAIN_SPEC.md`). Period precision items tracked in `docs/DESIGN_REFINEMENT.md` §Historical Precision.
- **Jealousy System — NEEDS DESIGN GATE.** v3.1 spec drafted. DO NOT CODE WITHOUT USER APPROVAL. See `docs/JEALOUSY_SPEC.md`.

### Design Gates

- **Coalition Spec v1.1** — Approved Mar 2, 2026. `docs/COALITION_SPEC.md`
- **Starting Situation Balance** — Approved Mar 2, 2026. 5 changes applied to DIPLOMACY_SPEC.
- **Jealousy System** — v3.1 spec drafted, NEEDS APPROVAL. DO NOT CODE. `docs/JEALOUSY_SPEC.md`
- **Settlement Conversational Re-front** — **v0.6 APPROVED May 29, 2026** (audited five times before approval; Slice 0 + Slice 1 + REFRONT-V voice LANDED May 30 at `ec1081d`; **Slices 2 + 3 IMPLEMENTED May 30 + Slice 3 audit fold; Gate-4 pre-flight fix slices PF-1/PF-2/PF-3 LANDED June 9, 2026 (D1–D6 fixed) — ALL implementation slices done; the REFRONT-9 OQ#4 focused breakdown LANDED June 10 inside Guided Terms GT-Slice-3 per GT-A4; the Gate 4 manual smoke is RE-SEQUENCED to the end of the settlement queue (user decision June 9)**). `docs/SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` + audit `docs/SETTLEMENT_CONVERSATIONAL_REFRONT_AUDIT.md` (common peace as a conversational multi-party settlement table; per-court ratification gate; per-court baseline direction from `direct_scores` via the `select_direct_score` tuple-or-`None` contract; SC-32 D5 no-conference-copy boundary; remaining: end-of-queue Gate 4 manual smoke, then Slice G)
- **Settlement Guided Terms** — **v0.2 APPROVED June 10, 2026 (D4 mixed-direction rows EXPLICITLY CONFIRMED by user). GT-Slice-1 + companion CH-5 LANDED June 10, 2026** (demand-mutation verbs + treasury line + `authored_by`/dial rule + §7 wiring, on the CH-5 response-shape wrapper — D7's orphan class is now structurally cured; user-reviewed/approved June 10). **GT-Slice-2 LANDED June 10, 2026** (per-court `demand_suggestions[]` — both D4 groups, direction-led, eligibility-gated, table-scoped §3.4, OQ-1 dropdowns, §4 capacity-bounded recurring pre-fill — + `current_demands[]` with magnitude metadata + §3.3 row authoring states + the §8 OQ-6 `budget_bound_recommendation`; USER-APPROVED June 10). **GT-Slice-V + GT-Slice-3 LANDED June 10, 2026 (one session)** — V: the verbatim DC-4 guard line on both D5 triggers via one-shot `authoring_voice_beats`, named-court authoring reactions (chancery fallback), the 11 in-character `settlement_guided_reason_*` templates, the OQ-6 `recommendation_voice` advisory extension, the §5 revision-copy retarget, Voice Bible §16.1a updated; 3: the guided per-court Godot UI (treasury line, demand lines + Remove/magnitude steppers, `Add demand` expansion through `send_dialogue_response_with_params`), **REFRONT-9 LANDED** (full 10-component `component_breakdown` on the focused expanded row via `settlement_focus_court`), **UX-2** (REVIEW frozen server+client) + **UX-5** (scroll container), and the §9 HTTP-boundary dispatch fix (executor accepts the verb from `choice`); +19 tests, suite `10466 passed, 1 skipped`. The GT-A1..4 amendments + the Run #1 audit (`docs/SETTLEMENT_GUIDED_TERMS_AUDIT.md`, GO-with-changes, 0 CRITICAL / 9 MAJOR / 6 MINOR, all folded) are IN v0.2. `docs/SETTLEMENT_GUIDED_TERMS_SPEC.md` — replaces the Tier-3 freeform "Adjust terms" editor (blind while authoring — no live acceptance until REVIEW; identity-picker model defaults `France`/`France`; diverges from the bilateral guided `terms_guidance` flow) with **guided per-court demand authoring** folded into the per-court rows (direction-led menus per option, both demand/offer groups per D4; table-scoped valid-by-construction with a visible `treasury_line` per GT-A1; no submit-blob so the merge/replace tension dissolves). **GT-Slice-4 LANDED June 10, 2026 — ALL Guided Terms slices done** (the editor scene/script + identity-picker schema + EDIT payload contract + dead `CommandRequest` submit fields removed after the verify-dead pass; `merge_same_war_settlement_drafts` replaced by §6 mounted-draft-wins refresh; the three editor-mount producers re-pointed to guided PROPOSE incl. counter-authoring provenance; editor tests migrated/deleted/kept per the §9 disposition + new `tests/test_settlement_gt_slice4.py`; REFRONT-7/UX-3/UX-8 closed moot; suite `10422 passed, 1 skipped` both orderings; awaiting user review of the session confidence report). The implementation queue now precedes the end-of-queue Gate 4 smoke with only the CH code-health slices. Two Gate-4 editor transport/validation bugs were fixed at `067e431` (the transport itself is now retired).


---

## File Reference

### Backend Core

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI endpoints, response formatting |
| `backend/commands/executor.py` | Action execution, dispatch, objection routing (~1.5k lines) |
| `backend/commands/combat_executor.py` | Combat execution + coordination: attack, bombardment, charge, garrison, form_square, post-combat pipeline, multi-marshal coordination, reinforcements, overwatch, auto-dispatch combat (~4.7k lines, R10A+R10B) |
| `backend/commands/strategic_executor.py` | Strategic order execution: MOVE_TO, PURSUE, HOLD, SUPPORT, cancel, objection messages, target resolution, first-step blocking (~1.8k lines, R11) |
| `backend/commands/diplomatic_executor.py` | Diplomatic execution: proposals, dialogue state machine, missions, trust reactions, AI proposal accept/reject/counter, terms guidance wizard (~2.3k lines, R11) |
| `backend/commands/economy_executor.py` | Economy execution: economy report, recruit, garrison, build, watchtower, repair (~800 lines, R13A) |
| `backend/commands/tactical_executor.py` | Tactical execution: defend, wait, drill, fortify, unfortify, stance_change, restrain, auto_break_square (~715 lines, R13A) |
| `backend/commands/movement_executor.py` | Movement execution: move, scout, auto_assign_scout, retreat, movement attrition (~680 lines, R13B) |
| `backend/commands/meta_executor.py` | Meta/debug/objection: end_turn, status, help, debug, cheat, handle_objection_response, post_objection (~1.9k lines, R13B) |
| `backend/commands/vassal_executor.py` | Vassal management: invest, change_autonomy, make_vassal, release_vassal (~147 lines, R13A) |
| `backend/commands/capture_executor.py` | Post-capture plunder/secure choice handling (~94 lines, R13A) |
| `backend/commands/parser.py` | Command parsing, fuzzy matching |
| `backend/commands/disobedience.py` | V1 objection system, trust values |
| `backend/commands/objection_v2.py` | V2a objection system (ConcernLevel triggers) |
| `backend/commands/defiance.py` | V2b defiance system (chance calc, fallback table, outcomes) |
| `backend/commands/strategic.py` | Strategic order per-turn executor |
| `backend/commands/vindication.py` | Vindication tracker |
| `backend/models/marshal.py` | Marshal class, combat modifiers, states, serialization |
| `backend/models/world_state.py` | Game state, turn processing, action economy |
| `backend/models/region.py` | 19 regions (REGIONS_DATA source of truth), terrain/region type constants, NATION_CAPITALS, starting_controller, grid_position |
| `backend/models/personality.py` | PersonalityType enum |
| `backend/models/personality_modifiers.py` | Combat bonuses by personality |
| `backend/models/cooldown_manager.py` | CooldownManager (5 auto-decrement cooldowns) + PopupQueue (7 priority-ordered popups) (R6) |
| `backend/models/dialogue_manager.py` | DialogueManager (push/pop/peek, priority queue, clear_stale timeout, promote_if_empty) (R12) |
| `backend/display_names.py` | Single source of truth for all internal→display name translations (R7) |
| `backend/campaign_log.py` | Campaign log fog filter + one-liner formatter |
| `backend/game_logic/combat.py` | Combat resolution, messages |
| `backend/game_logic/battle_report.py` | Post-battle modifier snapshots, report generation, Berthier observations |
| `backend/game_logic/relationship.py` | Win/Loss Relationship Formula (severity, ordered pairs, cooldown) |
| `backend/notifications.py` | Notification system (EU4-style persistent alerts, collector, dismiss) |
| `backend/game_logic/dispatch.py` | Morning Dispatch builder (fog-filtered turn-start briefing), stores last_morning_dispatch on WorldState |
| `backend/game_logic/ledger.py` | Strategic Ledger builder (6 sections: forces, territories, economy, intel, manpower, orders) |
| `backend/game_logic/marshal_overview.py` | Marshal Management builder (player marshal cards with identity, ability, stats, trust, status, relationships) |
| `backend/game_logic/turn_manager.py` | Turn flow, enemy phase |
| `backend/ai/enemy_ai.py` | Enemy AI decision tree (P1-P8) |
| `backend/ai/llm_client.py` | LLM integration (fast parser + Anthropic) |
| `backend/ai/strategic_parser.py` | Strategic command detection |
| `backend/ai/validation.py` | VALID_ACTIONS (single source of truth for LLM) |
| `backend/ai/prompt_builder.py` | Context-aware LLM prompts |
| `backend/intel_report.py` | Berthier Intelligence Report (fog-filtered status view) |
| `backend/models/diplomat.py` | DiplomaticRepresentative class, starting diplomats |
| `backend/game_logic/diplomacy.py` | Diplomacy engine: transitions, war score, acceptance formula, DP, war declaration, cascade, trade income |
| `backend/game_logic/ai_diplomacy.py` | AI proposal generation (P1-P7 triggers), M3 counter-offer, alliance conflict check, anti-spam |
| `backend/game_logic/diplomatic_advisory.py` | Advisory conversations: threat assessment, nation analysis, action recommendations |
| `backend/game_logic/coalition.py` | Coalition system: threat accumulation/decay, formation/brewing/instant, leader/posture, AI friction/convergence, war exhaustion, British subsidy, dissolution/cooldown |
| `backend/game_logic/diplomatic_ledger.py` | Diplomatic Ledger builder (4 tabs: nations, treaties, balance_of_europe, talleyrand) with fog-filtered army strength |
| `backend/game_logic/war_status.py` | War Status Panel data builder: `build_active_wars()` produces war/coalition/armistice data for HUD, embedded in every response via `_include_popup_passthroughs()` |
| `backend/game_logic/vassal.py` | Vassal system: creation, loyalty, rebellion, cascade, tribute, investment, autonomy, marshal assimilation, Continental System |
| `backend/commands/diplomatic_defiance.py` | Talleyrand sabotage: defiance chance, sabotage types, discovery, confrontation, pre-proposal objection, redemption |
| `backend/save_manager.py` | Save/load file I/O, autosave |
| `backend/game_logic/settlement_*.py` | Imperial Settlement package (CH-1 split, June 10, 2026): `settlement_routes` (L0 routing/reopen/recovery) → `settlement_validation` (L1 primitives/eligibility/validator) → `settlement_baseline` (L2 baseline/presets/per-court acceptance) → `settlement_staging` (L3 draft stores/confirm build/stage/guided payload) → `settlement_ratify` (L4 apply/ratify) → `settlement_actions` (L5 dialogue-action dispatch + arms) → `settlement_offers` (L6 offers/petitions/recurring). Each imports lower layers only. `settlement_preview.py` is the public re-export door (production imports true homes). Tests patch the scorer at `settlement_scoring.calculate_common_peace_acceptance` (stable seam). |

### Godot Core

| File | Purpose |
|------|---------|
| `utils.gd` | Shared color palette (19 COLOR_ consts), NATION_COLORS, bbcode_color/format_number helpers (R15) |
| `popup_base.gd` | Base class for modal popups: close_popup, _disable_all_buttons, _apply_standard_theme (R15) |
| `dialog_manager.gd` | Centralized dialog registry: register, get_dialog, is_any_modal_open, hide_all (R16) |
| `api_client.gd` | Backend communication |
| `game_manager.gd` | Game state coordination |
| `map_renderer_base.gd` | Map renderer base: scene layers, Camera2D+SubViewport, province color-map, hover/click, zoom/pan |
| `map.gd` | Session 8 map: extends renderer base, region positions/connections/colors |
| `main.gd` | Terminal UI, response handling |
| `pause_menu.gd` | Pause menu overlay (Phase 6.5) |
| `campaign_log.gd` | Campaign log overlay (Phase 6.5), CanvasLayer 50 |
| `notification_bar.gd` | Notification bar (Phase 6.5), reparented into top bar |
| `top_bar.gd` | Top bar controller (Session A): screen management, hotkeys, notifications, turn counter |
| `dispatch_view.gd` | Dispatch re-read screen (Session A): CanvasLayer 50, BBCode rendering |
| `strategic_ledger.gd` | Strategic Ledger screen (Session B): CanvasLayer 50, 6 sub-tabs, number key switching, Orders tab cancel buttons |
| `marshal_management.gd` | Marshal Management screen: CanvasLayer 50, card-based marshal view, G key toggle |
| `diplomatic_ledger.gd` | Diplomatic Ledger screen (Session 8B): CanvasLayer 50, 4 sub-tabs (Nations/Treaties/Balance of Europe/Talleyrand), D key toggle |
| `*_popup.gd` (7 files) | Modal popups: coalition_declaration, incoming_proposal, talleyrand_objection, sabotage_discovery, talleyrand_redemption, vassal_rebellion, alliance_paradox. CanvasLayer 100-119 |
| `mailbox_panel.gd` | Browsable mailbox inbox: CanvasLayer 119, click-to-activate rows |
| `war_status_panel.gd` | War Status HUD (CanvasLayer 25) + `war_detail_popup.gd` (CanvasLayer 30) |
| `diplomacy_wizard.gd` | Diplomacy Button wizard (Session B): F1 hotkey, 2-step nation→action flow, own HTTPRequest, command handoff, `open_for_nation()` for war panel handoff |

---

## Before Modifying: Required Reading

| If you're modifying... | Read these first |
|------------------------|------------------|
| Combat damage/modifiers | `marshal.py` (get_*_modifier), `combat.py` (resolve_combat), `combat_executor.py` (_execute_attack, _execute_bombardment), `docs/MULTI_MARSHAL_SPEC.md` (coordination bonuses) |
| Multi-marshal coordination | `docs/MULTI_MARSHAL_SPEC.md`, `combat_executor.py` (_calculate_coordination_context, _calculate_reinforcements, _calculate_overwatch), `marshal.py` (transient bonus fields) |
| Combat execution (attack/bombard/charge) | `combat_executor.py` (all _execute_* methods, post-combat pipeline, coordination, reinforcements, overwatch) |
| Marshal abilities | `personality_modifiers.py`, `marshal.py`, `combat.py`, `docs/ADDING_CONTENT.md` (wiring checklist), `marshal_overview.py` (_WIRED_ABILITY_MARSHALS) |
| Fortify/Drill mechanics | `tactical_executor.py` (_execute_fortify/drill), `marshal.py`, `world_state.py` (_process_tactical_states) |
| Disobedience/Trust | `disobedience.py`, `objection_v2.py`, `personality.py`, `docs/V2B_DEFIANCE_SPEC.md` |
| Cavalry limits | `world_state.py` (_check_cavalry_limits), `marshal.py` (cavalry counters) |
| Terrain system | `region.py` (constants, Region class), `combat.py` (_get_terrain_bonus), `combat_executor.py` (resolve_battle calls, charge blocking) |
| Turn processing | `world_state.py` (advance_turn), `meta_executor.py` (_execute_end_turn) |
| Adding new actions | See pattern below |
| Retreat/Broken state | `combat.py` (forced retreat), `marshal.py` (retreat_recovery), `combat_executor.py` (_handle_forced_retreat, _apply_forced_retreat_or_break) |
| Enemy AI behavior | `enemy_ai.py`, `turn_manager.py`, `executor.py` (is_player_action check) |
| Capital garrison | `combat_executor.py` (_resolve_garrison_combat), `world_state.py` (garrison init/regen), `enemy_ai.py` (P4.25) |
| Player garrison | `economy_executor.py` (_execute_garrison), `region.py` (garrison_detachment), `world_state.py` (regen exclusion) |
| Fort degradation | `combat.py` (resolve_combat degradation block), `battle_report.py` (P6c observations) |
| Supply attrition | `world_state.py` (process_supply_attrition), `region.py` (supply_capacity) |
| Strategic commands | `strategic.py`, `strategic_parser.py`, `strategic_executor.py` (_execute_strategic_command, _execute_cancel, objection handling) |
| Objection V2 system | `objection_v2.py`, `docs/OBJECTION_V2.md`, `docs/V2B_DEFIANCE_SPEC.md` |
| Fog of war | `docs/FOG_OF_WAR_SPEC.md`, `intel.py`, `intel_report.py`, `map.gd`. Use `get_visible_enemies()` for player-facing, `get_enemies_of_nation()` for omniscient only |
| Manpower / recruitment | `world_state.py` (manpower constants), `economy_executor.py` (_execute_recruit), `enemy_ai.py` (P1/P4.5/P7) |
| Artillery / bombardment | `marshal.py` (artillery flag), `combat.py` (cavalry counter, fort degradation), `combat_executor.py` (_execute_bombardment, _distribute_casualties), `enemy_ai.py` (_score_artillery_position) |
| Top bar / screen system | `top_bar.gd` (controller), `main.gd` (_on_screen_changed, _is_modal_dialog_open, _is_screen_open, _is_hotkey_blocked), `docs/TOP_BAR_SPEC.md` |
| Morning dispatch / re-read | `dispatch.py` (build + store), `dispatch_view.gd` (render), `main.gd` (_display_morning_dispatch), `world_state.py` (last_morning_dispatch field) |
| Strategic ledger | `ledger.py` (build_strategic_ledger), `strategic_ledger.gd` (render), `world_state.py` (get_manpower_regen_rates), `main.py` (GET /ledger, POST /cancel_order) |
| Marshal management UI | `marshal_overview.py` (build_marshal_overview), `marshal_management.gd` (render), `marshal.py` (biography field), `main.py` (GET /marshal_overview) |
| Win/Loss relationships | `relationship.py` (formulas, participants, process), `combat_executor.py` (_execute_attack wiring), `marshal.py` (modify_relationship, last_relationship_change_turn), `docs/MULTI_MARSHAL_SPEC.md` §9 |
| Square formation / Tactical Triangle | `docs/TACTICAL_TRIANGLE_SPEC.md`, `marshal.py`, `combat.py`, `combat_executor.py`, `tactical_executor.py`, `executor.py` |
| Vassal system | `vassal.py`, `world_state.py` (vassals dict, advance_turn), `diplomacy.py` (AP clause), `turn_manager.py`, `dispatch.py` |
| Diplomatic ledger | `diplomatic_ledger.py` (build_diplomatic_ledger, fog-filtered army strength), `main.py` (GET /diplomatic_ledger, debug endpoints), `world_state.py` (popup fields) |
| Diplomacy wizard / button | `diplomacy_wizard.gd` (wizard UI, `open_for_nation()`), `main.gd` (F1 hotkey, button wiring, command handoff), `main.py` (GET /diplomatic_preview nation list mode), `docs/DIPLOMACY_BUTTON_SPEC.md` |
| War status panel (N4) | `war_status.py` (build_active_wars), `war_status_panel.gd` (HUD), `war_detail_popup.gd` (detail), `main.gd` (_process_active_wars) |
| Suggested terms / smart suggestions | `diplomatic_templates.py` (generate_suggested_terms 5-stage pipeline), `diplomatic_dialogue.py`, `docs/TALLEYRAND_SMART_SUGGESTIONS_SPEC.md` |
| Diplomacy execution | `diplomatic_executor.py` (_execute_diplomatic*, handle_diplomatic_dialogue_response, trust reactions, AI proposal handlers) |
| Dialogue state (R12, PL-27) | `dialogue_manager.py` (push/pop/peek, PL-27 taxonomy: HARD_STOP/SOFT_STOP/HYBRID/LOCAL_PLANNING types), `world_state.py` (transparent properties). Only hard-stop dialogues block commands. Endpoints: `GET /mailbox`, `POST /mailbox/activate` |
| Diplomacy system (Phase 8) | `docs/DIPLOMACY_SPEC.md`, `docs/COALITION_SPEC.md`, `diplomacy.py`, `diplomat.py`, `diplomatic_dialogue.py`, `diplomatic_templates.py`, `ai_diplomacy.py`, `diplomatic_advisory.py`, `vassal.py`, `diplomatic_defiance.py`, `coalition.py` |
| Memory and Pressure substrate (hegemony / betrayal memory / paradox / reliability) | `docs/RELIABILITY_COMMITMENTS_SPEC.md` (v2.4.3 — §8.8 holds the DG-4 call-to-arms episode contract, §8.6.1a authors the Make Amends grievance variant, §8.8.7a authors the existing-alliance termination on defensive refusal; `docs/SCALE_READINESS_PLAN.md` §DG-4 Amendment is the source of truth), `docs/RELIABILITY_IMPLEMENTATION_PLAN.md`, `docs/COMMITMENTS_PRESENTATION_SPEC.md`, `docs/DIPLOMAT_VOICE_BIBLE.md`, `docs/COALITION_SPEC.md`, `diplomacy.py`, `world_state.py` (`betrayal_history`, `next_episode_id`), `commitments` logic within `diplomatic_templates.py`, `campaign_log.py`, `coalition.py` (hegemony engine when landed) |
| Peace Deals / Imperial Settlement | **Active: the end-of-queue Gate 4 manual smoke (the queued CH code-health slices CH-1..CH-5 ALL LANDED June 10, 2026 — the settlement package is `settlement_routes/validation/baseline/staging/ratify/actions/offers.py` + the `settlement_preview.py` public door; CH-2 dispatch tables + CH-4 baseline convergence + CH-3 single scoped draft store landed in the follow-up slice). `docs/SETTLEMENT_GUIDED_TERMS_SPEC.md` implementation is COMPLETE (v0.2 APPROVED June 10, 2026, D4 confirmed; audit `docs/SETTLEMENT_GUIDED_TERMS_AUDIT.md`; GT-Slice-1 + CH-5 LANDED June 10 at `4c32e59`; GT-Slice-2 LANDED June 10; GT-Slice-V + GT-Slice-3 LANDED June 10 incl. REFRONT-9 + UX-2/UX-5; GT-Slice-4 LANDED June 10 — the freeform editor is retired, the guided per-court rows are the only authoring tier); `docs/SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` v0.6 (APPROVED May 29, 2026; Slices 0–3 + REFRONT-V voice + PF-1/2/3 IMPLEMENTED/LANDED; REFRONT-9 LANDED June 10 inside GT-Slice-3; REFRONT-7 closed moot June 10).** Cleanup gate is `docs/SETTLEMENT_UI_CLEANUP_SPEC.md` **v0.32 GO** with the **Gate 4 smoke open, re-sequenced to the end of the settlement queue (June 9, 2026)**, then `docs/STATUS.md`. Older Imperial Settlement plan/spec docs remain historical anchors; do not route active work back to v0.19-v0.27, Slice F, Slice E, or a fresh G2-Slice-1 start. |
| C3-lite presentation (Memory and Pressure final slice) | `docs/COMMITMENTS_PRESENTATION_SPEC.md` (v0.5.2 — v2.4.3 hegemony-aligned; §8.1a owns the bloc-naming contract folded from the retired Block 3 audit; non-normative bulk trimmed per v2.4.2 deep-audit C7; Slice C trims cut spotlight-tier card variant, split-voice `attributed_lines[]`, N+1 Talleyrand aside), `docs/COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` (historical), `docs/DIPLOMAT_VOICE_BIBLE.md`, `commitments_routing.py`, `diplomatic_templates.py`, `notifications.py`, `notification_bar.gd`, `dispatch.py`. Any `speaker="envoy"` / `speaker="foreign_office"` template MUST resolve through `resolve_named_diplomat()` or chancery fallback per Voice Bible. Live notice families include treaty breach, hard-reject posture, Make Amends, Balance of Europe, DG-4 call-to-arms, witness strike, and paradox popup/resolution metadata. |
| Diplomat voice (register rules per named diplomat) | `docs/DIPLOMAT_VOICE_BIBLE.md`, `backend/models/diplomat.py` (cast = Talleyrand, Castlereagh, Hardenberg, Metternich, Einsiedel). Read Voice Bible BEFORE authoring any new line for a named foreign diplomat. |

For detailed system docs: `docs/SYSTEMS_REFERENCE.md`
For Enemy AI details: `docs/ENEMY_AI_REFERENCE.md`

---

## Common Modification Patterns

### Adding a new action

1. Add to `VALID_ACTIONS` in `validation.py` (single source of truth for LLM)
2. Add `_execute_[action]()` in the appropriate sub-executor (see file reference table)
3. Add to `valid_actions` list in `parser.py`
4. Add cost to `_action_costs` in `world_state.py`
5. Add keywords to mock parser in `llm_client.py` (~line 416, search "ADD NEW ACTION")
6. Add few-shot example in `prompt_builder.py` if complex
7. If triggerable by objection, add to `objection_actions` in `disobedience.py`
8. Add to_dict/from_dict if new state fields needed
9. Add to `ACTION_DISPLAY` in `display_names.py`
10. Add to `_DEFIANCE_DISPLAY` + `_OBJECTION_DISPLAY` in `campaign_log.py` (lines ~21, ~43)
11. Add event type to `CAMPAIGN_LOG_TYPES` in `campaign_log.py` (line ~83) + format in `format_event_oneliner()`

### Adding a new marshal state

1. Add field to `marshal.py __init__`
2. Add to `to_dict()` and `from_dict()` (with `.get()` default)
3. Process in `world_state.py _process_tactical_states()` if per-turn
4. Add blocking logic in `executor.py` if it prevents actions
5. Run `pytest tests/test_serialization_enforcement.py -v`

### Adding a new popup/dialog

```
Backend → Frontend data flow:
  sub-executor → main.py → api_client.gd → main.gd
```

1. Sub-executor (e.g., `meta_executor.py`, `combat_executor.py`): Return field in result dict
2. `main.py`: Add early return to pass through the field (most common wiring gap!)
3. `main.gd`: Check for field in `_on_command_result()`
4. Create dialog scene (.tscn) and script (.gd) — assign unique layer in 101-118 range
5. **R16:** Register in `main.gd _ready()` via `dialog_manager.register()` — set `modal=true` (default) for blocking dialogs, `modal=false` for HUD elements
6. **R4:** All POST handlers use `build_base_response()` which structurally guarantees popup passthroughs. No manual `_include_popup_passthroughs()` calls needed.

**Test with curl BEFORE assuming Godot is broken:**
```bash
curl -X POST http://127.0.0.1:8005/command \
  -H "Content-Type: application/json" \
  -d '{"command": "end turn"}' | python -m json.tool
```

**SERIALIZATION WARNING:** Executor results contain `new_state` (WorldState with circular refs). Strip `new_state` before embedding in API responses.

### Adding a new combat modifier

1. Add state field to `marshal.py __init__`
2. Apply in `marshal.py get_attack_modifier()` or `get_defense_modifier()` ONLY
3. Add message in `combat.py` (DO NOT recalculate modifier)
4. Clear state in `combat.py` if consumable (AFTER get_*_modifier call)

---

## Serialization Enforcement (MANDATORY)

**"If it exists on the object, it must serialize."**

For ANY new field on ANY model class:
1. Add to `to_dict()` method
2. Add to `from_dict()` method (with `.get(key, default)`)
3. Run: `pytest tests/test_serialization_enforcement.py -v`
4. Update `docs/SAVE_FORMAT_REFERENCE.md`

Serializable classes: Marshal, StrategicOrder, StrategicCondition, WorldState, Region, Trust, AuthorityTracker, VindicationTracker, RegionIntel

---

## Strategic Commands

Strategic orders (MOVE_TO, PURSUE, HOLD, SUPPORT) cost 2 AP (1 for literal). Key patterns:

- **Tactical objection:** `world.pending_objection` — for per-action objections
- **Strategic objection:** `world.pending_strategic_objection` — for order-issuance objections (different field!)
- **Strategic execution flag:** `command["_strategic_execution"] = True` skips AP cost + objections
- **Cancel:** "cancel/halt/stop/abort" → `_execute_cancel()`, costs 1 AP

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| State cleared too early | Get value, use it, THEN clear (e.g. drill/shock bonus) |
| "No objection pending" | Strategic uses `pending_strategic_objection`, not `pending_objection` |
| Post-objection "Unknown action" | `_execute_post_objection` must handle all actions + strategic routing |
| Enemy AI crash | `game_state` must be dict `{"world": WorldState}`, not WorldState directly |
| Internal names in frontend | Use `display_names.py` maps (R7) — never raw action/state/personality strings. Import from `backend.display_names`, not original files |
| Response key mismatch | curl test the endpoint to verify key names match what Godot reads |
| None crash on parse field | Guard `.lower()`/`.strip()` — parser may return None for optional fields |
| `.get('key', '')` returns None | Use `(d.get('key') or '')` — `.get()` default only applies for MISSING keys, not `None` values |
| Objection on impossible action | Pre-validate BEFORE objection check — see bypass hierarchy in executor.py |
| AP error after objection proceed | AP must be checked in pre-validation BEFORE objection fires, not after |
| Data cleared before capture | Save per-turn lists (e.g. mild_concerns) BEFORE calling advance_turn |
| "build" parsed as drill | Mock parser keyword order matters — "build " must be checked BEFORE "train" (substring in "training") |
| Fog leaks enemy info | Filter to PARTIAL+ visibility for attack suggestions, move destinations, event reports |
| PURSUE/SUPPORT path error | `order.target` is marshal name — resolve to `target_marshal.location` before pathfinding |
| Godot null "pressed" on startup | `@onready` node paths must match FULL scene tree in .tscn — verify intermediate nodes |
| Vassal loyalty unexpected | Check `nation_relations` default — France/Saxony=40, adds +2/turn via relation//20 modifier |
| AP clause wrong nation | `from_nation` is the penalized nation (loses AP), not `to_nation` |
| "Talleyrand awaiting" stuck state | Only hard-stop dialogues block commands. Check `dialogue_manager.py` HARD_STOP_TYPES |
| New diplomatic state missing | Add to `post_break_map` in diplomacy.py AND `validate_transition()` |
| Popup not showing after early return | Use `build_base_response()` or `_build_result_response()` — they structurally guarantee popup passthroughs (R4) |
| Popup not showing after endpoint | Use `build_base_response()` for ALL POST handlers. Only `/command` main path (enemy_phase deferral) calls `_include_popup_passthroughs()` directly |
| New dialogue type shows in terminal | **TWO things:** (1) Add dtype to `main.gd:697` whitelist so Godot shows popup. (2) If dialogue concludes with a result, set `world.proposal_result_popup` so outcome shows as popup. See PL-14 fix |
| Raw internal keys in popup text | Use display maps (FEEDBACK_STRINGS, DEFIANCE_TYPE_DISPLAY, PROPOSAL_TYPE_DISPLAY) — never expose raw component/enum keys to players |
| Fog leak — player sees fogged enemies | Use `world.get_visible_enemies(nation)` for player-facing queries (R5). `get_enemies_of_nation()` is omniscient — only for combat/AI/mechanics |
| Region attribute returns default silently | Region uses `income_value` (not `income`) and `adjacent_regions` (not `connections`). Check `region.py` for exact names |

---

## Don't Do

- Add features outside current phase scope
- Change port without updating api_client.gd
- Make executor LLM-dependent (keep deterministic)
- Store API keys in code (use .env)
- Skip serialization for new fields
- Bypass executor for state changes
- Run objection evaluation before action validation (check bypass hierarchy in executor.py)
- Show raw internal action names to players (use `_ACTION_DISPLAY_NAMES` translation)
- Use `.get('key', default)` when value may be `None` — use `(d.get('key') or default)` instead
- Skip AP check before objection evaluation — player should never see objection then AP failure
- Use `get_enemies_of_nation()` for player-facing queries — use `get_visible_enemies()` instead (R5). `get_enemies_of_nation()` is omniscient and leaks fog
- Add a new nation without updating `NATION_DESIRE_PROFILES` + `TALLEYRAND_COMMENTARY` in `diplomatic_templates.py`
- Iterate `world.regions.values()` in hot paths — use `get_active_nations()` (cached), `get_nation_regions()` instead
- Use `[world.player_nation] + list(world.enemy_nations)` — use `world.get_active_nations()` instead

---

## Commands

**IMPORTANT (Windows/WSL):** Use Windows-style paths with the venv Python. Unix-style `python -m pytest` silently fails on this WSL setup.

```bash
# Backend
".venv\Scripts\python.exe" backend/main.py    # Runs on port 8005

# Tests (MUST use Windows paths — see note above)
cd "C:\Users\User\PycharmProjects\project-sovereign-map"
".venv\Scripts\python.exe" -m pytest tests/ -v                          # Full suite
".venv\Scripts\python.exe" -m pytest tests/ -v --tb=no -q              # Quick count
".venv\Scripts\python.exe" -m pytest tests/test_objection_v2.py -v     # V2 tests only

# Coverage
".venv\Scripts\python.exe" -m pytest tests/ --cov=backend --cov-report=term-missing -v --tb=no -q

# Lint
ruff check backend/                     # Check for issues
ruff check backend/ --fix               # Auto-fix safe issues

# Validate mod
".venv\Scripts\python.exe" -m backend.modding.validator path/to/mod.json
```

---

## Document Map

| Need | Read |
|------|------|
| Session state / what's next | `docs/STATUS.md` |
| **Open bugs (consolidated)** | **`docs/BUG_FIXES.md`** |
| **Design refinement items** | **`docs/DESIGN_REFINEMENT.md`** |
| Phase timeline | `docs/ROADMAP.md` |
| Game systems (combat, trust, disobedience, LLM, cavalry, strategic) | `docs/SYSTEMS_REFERENCE.md` |
| Enemy AI decision tree | `docs/ENEMY_AI_REFERENCE.md` |
| Combat specs (V2b, Multi-Marshal, Tactical Triangle) | `docs/V2B_DEFIANCE_SPEC.md`, `MULTI_MARSHAL_SPEC.md`, `TACTICAL_TRIANGLE_SPEC.md` |
| Diplomacy specs (system, coalition, wizard, suggestions, jealousy) | `docs/DIPLOMACY_SPEC.md`, `COALITION_SPEC.md`, `DIPLOMACY_BUTTON_SPEC.md`, `TALLEYRAND_SMART_SUGGESTIONS_SPEC.md`, `JEALOUSY_SPEC.md` |
| Memory and Pressure (substrate + presentation) | `docs/RELIABILITY_COMMITMENTS_SPEC.md` (v2.4.3), `RELIABILITY_IMPLEMENTATION_PLAN.md`, `COMMITMENTS_PRESENTATION_SPEC.md` (v0.5.2 C3-lite hegemony-aligned; §8.1a owns bloc-naming contract post-Block-3 fold), `COMMITMENTS_PRESENTATION_DESIGNER_AUDIT.md` (historical) |
| Peace Deals (umbrella + sub-specs) | **Active: the end-of-queue Gate 4 smoke (the queued CH code-health slices CH-1..CH-5 ALL LANDED June 10 — CH-2 + CH-4 + CH-3 in the follow-up slice). `docs/SETTLEMENT_GUIDED_TERMS_SPEC.md` implementation is COMPLETE (v0.2 APPROVED June 10, 2026 — D4 confirmed; audit `docs/SETTLEMENT_GUIDED_TERMS_AUDIT.md`; GT-Slices 1/2/V/3/4 ALL LANDED June 10 — the freeform editor is retired); `docs/SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` v0.6 + audit `docs/SETTLEMENT_CONVERSATIONAL_REFRONT_AUDIT.md` (conversational multi-party re-front — APPROVED May 29, 2026; Slices 0–3 + REFRONT-V voice + Gate-4 pre-flight PF-1/2/3 IMPLEMENTED/LANDED; REFRONT-9 LANDED June 10 inside Guided Terms GT-Slice-3; REFRONT-7 closed moot June 10); `docs/SETTLEMENT_GATE4_PREFLIGHT_AUDIT.md` owns the PF/DC/UX/CH/DW ledgers (UX-3 + UX-8 closed moot June 10).** Current cleanup gate: `docs/SETTLEMENT_UI_CLEANUP_SPEC.md` **v0.32 GO** (Gate 4 smoke open — re-sequenced June 9, 2026 to one end-of-queue run), then `docs/STATUS.md`. Historical anchors: `docs/PEACE_DEALS_UMBRELLA_SPEC.md`, `BILATERAL_PEACE_HARDENING_SPEC.md`, `WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`, `WAR_BARGAIN_SPEC.md`, `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md`, and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`. Treat older Slice B / Final Gate notes as historical unless STATUS points back to them. |
| Diplomat voice bible / playtest | `docs/DIPLOMAT_VOICE_BIBLE.md`, `COMMITMENTS_PLAYTEST_SCRIPT.md` |
| UI specs (top bar, fog) | `docs/TOP_BAR_SPEC.md`, `FOG_OF_WAR_SPEC.md` |
| Save format / serialization | `docs/SAVE_FORMAT_REFERENCE.md` |
| Adding content / modding | `docs/ADDING_CONTENT.md`, `MODDING_FORMAT.md` |
| Vision, future design, manual tests | `docs/VISION.md`, `FUTURE_DESIGN.md`, `MANUAL_TEST_PLAN.md`, `TUTORIAL_SCRIPT.md` |
| Architecture (audit + refactoring) | `docs/ARCHITECTURE_AUDIT_REPORT.md`, `ARCHITECTURE_AUDIT_SPEC.md`, `ARCHITECTURE_REFACTORING_PLAN.md` |
| Archived specs & session history | `docs/archive/` |

## Documentation Rules

**If you changed behavior, update the doc that describes it.** Session ends → STATUS.md. Phase completed → ROADMAP.md + STATUS.md. System changed → SYSTEMS_REFERENCE.md. New fields → SAVE_FORMAT_REFERENCE.md.

**Deferred work must have a HOME and a LANDING.** Any item marked hidden, cut, deferred, later, v2, polish, or backlog must name its owner spec/row, landing slice, completion definition, STATUS tracking line, and behavior test in the same table or bullet. If no owner row or landing slice exists, create that contract before implementation continues. Never leave deferred work as vague "later polish," "future work," disabled placeholder copy, or an unowned player-facing promise.

CLAUDE.md "Current Phase" must always list remaining items. Completed items get brief summaries. Never mark a phase complete when items remain in ROADMAP.md.

---

## Environment

`.env`: `LLM_MODE=mock|anthropic|groq`, `ANTHROPIC_API_KEY` if anthropic. Server: `127.0.0.1:8005`, CORS enabled.
