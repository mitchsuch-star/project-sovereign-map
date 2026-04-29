# Imperial Settlement Full-Europe Spec Audit - Run 1

Date: 2026-04-29

Scope:
- Active next-work spec: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.14.
- Coding handoff: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.11.
- Cross-doc and live-code checks: `docs/STATUS.md`, `docs/ROADMAP.md`, `docs/SAVE_FORMAT_REFERENCE.md`, `docs/DIPLOMACY_SPEC.md`, `docs/COALITION_SPEC.md`, `docs/PEACE_DEALS_UMBRELLA_SPEC.md`, `docs/WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`, `docs/WAR_BARGAIN_SPEC.md`, `backend/models/world_state.py`, `backend/game_logic/diplomacy.py`, `backend/game_logic/coalition.py`, `backend/game_logic/diplomatic_templates.py`, `backend/nation_config.py`, `backend/models/region.py`, `backend/models/dialogue_manager.py`, and Godot dialogue routing.

Method:
- Used `sovereign-map-workflow` preflight and repo routing.
- Used the `peace-deals-spec-audit` scoring model where it applies, adapted to the active Ally Participation / Common Peace handoff rather than re-auditing the completed BPH/WPS/WB suite.
- Added explicit full-Europe checks for 13-20 nations, 100+ regions, 20 pairwise wars, 6+ participant sides, map-absent Britain, bounded scans, and synthetic fixture requirements.

## Metrics

| Metric | Score | Result | Notes |
|--------|-------|--------|-------|
| M1 Fun | 9/10 | PASS | Common peace, ally standing, war bargains, serial separate-peace fallout, forced-alliance threat spikes, and defensive-settlement copy create agency and consequences. |
| M2 Clarity | 7/10 | PASS | The active spec and plan are detailed enough for Slice A1. Clarity drops because the synthetic full-Europe fixture strategy and legacy harshness-doc ownership still need tightening. |
| M3 Work Segmentation | 8/10 | PASS | A1/A2/A3, B1/B2/B3, C1/C2, D1/D2, and E have test budgets below the observed session ceiling. One inventory artifact should be made persistent. |
| M4 Contradiction-Freedom | 7/10 | PASS | No hard contradiction in the active settlement spec/plan. Stale Roadmap and DIPLOMACY_SPEC harshness text conflict with current code and the active handoff. |
| M5 Completeness | 8/10 | PASS | Full-Europe scale, map-absent Britain, turn-order, AI offers, serial settlements, UI density, and save/load are covered. Fixture authoring needs a more exact contract. |

## Findings

F-1: Full-Europe synthetic fixture contract is underspecified.
  Severity: MAJOR
  Location: `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Scale Rules; Slice A gate; Slice B/C/E gates
  Problem: The plan requires synthetic full-Europe fixtures with at least 13 nations, 100+ region ids, 20 active pair keys, a 6+ participant side, and map-absent Britain. It also correctly says not to rely on live `NATION_CAPITALS`, `REGIONS_DATA`, or marshal data. But it does not define the test-helper contract for creating those synthetic nations, capitals/proxies, diplomats, power tiers, region ownership, and `WorldState.get_active_nations()` compatibility without accidentally expanding production data or letting unknown nations fall through the `secondary` fallback.
  Fix: Add a "Full-Europe Test Fixture Contract" to the implementation plan. Name the helper module, the synthetic roster, the explicit power-tier map, the region-id generator, the map-absent Britain setup, and the rule that fixture tests must not depend on production `REGIONS_DATA` growing beyond 19 regions.
  Affected metrics: M2, M3, M5

F-2: DIPLOMACY_SPEC harshness ownership contradicts live code and the settlement handoff.
  Severity: MAJOR
  Location: `DIPLOMACY_SPEC.md` harshness calculation section; `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` section 11.2; `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Slice C1
  Problem: `DIPLOMACY_SPEC.md` still says harshness is single-sourced in `diplomacy.py` via `calculate_harshness()`. Live code uses `backend/game_logic/diplomatic_templates.py::calculate_treaty_harshness()`, and the settlement spec/plan correctly require Slice C to add `calculate_raw_treaty_harshness()` or an explicit raw/clamp option in `diplomatic_templates.py`. An implementer reading the companion docs can put the raw helper in the wrong module or revive the obsolete signed harshness formula.
  Fix: Mark the old DIPLOMACY_SPEC harshness paragraph as superseded by the live `calculate_treaty_harshness()` helper, or replace it with a current note that bilateral harshness remains 1.0-clamped in `diplomatic_templates.py` while Imperial Settlement Slice C adds a raw 1.5-ceiling path there.
  Affected metrics: M2, M4

F-3: Roadmap and save-format version references are stale against the active handoff.
  Severity: MINOR
  Location: `ROADMAP.md` top status and Ally Participation queue; `SAVE_FORMAT_REFERENCE.md` Pending Imperial Settlement fields
  Problem: `STATUS.md` routes current work to spec v1.14 and plan v1.11, but `ROADMAP.md` still says v1.9/v1.6. `SAVE_FORMAT_REFERENCE.md` pending-field text says v1.13 while the active spec is v1.14. The file names are correct, so this is not a blocker, but it creates unnecessary uncertainty in cold starts.
  Fix: Update the Roadmap references to v1.14/v1.11 and the save-format pending-field note to v1.14.
  Affected metrics: M2, M4

F-4: Slice A war-entry inventory is not tied to a durable artifact.
  Severity: MINOR
  Location: `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Slice A Build
  Problem: The plan says to write the WAR-entry code-path inventory in "Slice A PR notes or implementation comments." This repo workflow often proceeds without a PR artifact, and implementation comments are easy to scatter or delete. The seam inventory is important because full-Europe correctness depends on no direct WAR-entry path bypassing `war_instance` ownership.
  Fix: Add a small tracked checklist requirement, either in the Slice A section itself or in `tests/test_war_settlement_instances.py` as a module-level `WAR_ENTRY_SEAMS_UNDER_TEST` list asserted by tests.
  Affected metrics: M2, M3

## Passed Full-Europe Checks

- Scale target is explicit: 13-20 active nations, 100+ regions, 78+ pair keys, 20 simultaneous pairwise wars, and 6-8 participant coalition sides.
- Hot paths are bounded to active participants, direct terms, direct beneficiaries, bargain parties, affected territorial-interest nations, active major powers, and per-turn `war_instances_by_leader` / `war_instances_by_participant` indexes.
- Common peace remains rationally distinct from serial bilateral peace through narrow/full/serial tuning fixtures and serial separate-peace fallout.
- Map-absent Britain is explicitly modeled as a settlement identity, and `NATION_CAPITALS["Britain"] == "Netherlands"` is treated as a proxy holding rather than true capital status.
- Contribution is event-driven and explicitly avoids reconstructing historical settlement contribution from pruned `battle_records`.
- Sub-1000 casualty battles, non-pipeline charge paths, theater attribution, British subsidy support, and same-turn exit ordering are all covered by plan gates.
- UI density is covered: top-five rows, "View all participants", Terms/Allies/Warnings/Acceptance sectioning, scroll or pagination, and Godot smoke on synthetic 6+ participant payloads.
- Existing pairwise diplomacy remains authoritative for state, score, objectives, and treaty ratification; the new `war_instance` layer is additive.

## Improvement Steps

Step 1: Fix F-1.
  File: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`
  Section: Scale Rules
  Action: Add
  Content:
  ```text
  Full-Europe Test Fixture Contract:
  - Add shared helpers in `tests/helpers/full_europe_settlement_fixtures.py`.
  - Synthetic fixtures must define an explicit 13+ nation roster, explicit `major / secondary / minor` tiers, 100+ region ids when territory logic is tested, and at least one 6+ participant side.
  - Do not expand production `REGIONS_DATA`, `NATION_CAPITALS`, or `STARTING_DIPLOMATS` solely to satisfy settlement tests.
  - Tests that need active nations must either attach synthetic regions/controllers to the `WorldState` fixture or monkeypatch the specific active-nation helper under test; they must not rely on the current 5-nation runtime roster.
  - Unknown synthetic nations must not silently rely on the `secondary` fallback when a test is asserting standing, side pressure, leader selection, or major-power consultation behavior.
  - Britain fixtures must include both the live proxy case (`NATION_CAPITALS["Britain"] == "Netherlands"`) and a map-absent identity case where Britain has no true home-capital region.
  ```

Step 2: Fix F-2.
  File: `docs/DIPLOMACY_SPEC.md`
  Section: Harshness calculation
  Action: Replace
  Content:
  ```text
  Current implementation note:
  Live treaty harshness is calculated by `backend/game_logic/diplomatic_templates.py::calculate_treaty_harshness()`, which returns the existing bilateral 0.0-1.0 clamped value used by proposal preview and acceptance callers. The older signed `calculate_harshness()` sketch in this section is historical design context only and must not be used for new implementation.

  Imperial Settlement Slice C adds a raw common-peace harshness path in the same module, either as `calculate_raw_treaty_harshness(treaty)` or as an explicit raw/clamp option, while preserving all current bilateral callers' 1.0-clamped behavior.
  ```

Step 3: Fix F-3.
  File: `docs/ROADMAP.md`
  Section: top status and Ally Participation queue
  Action: Replace stale version references
  Content: Change `v1.9` to `v1.14` and `v1.6` to `v1.11` where referring to `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`.

Step 4: Fix F-3.
  File: `docs/SAVE_FORMAT_REFERENCE.md`
  Section: Pending Imperial Settlement WorldState Fields
  Action: Replace stale version reference
  Content: Change `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md v1.13` to `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md v1.14`.

Step 5: Fix F-4.
  File: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`
  Section: Slice A - War Identity And Grouping
  Action: Add
  Content:
  ```text
  Durable WAR-entry seam inventory:
  - Slice A must maintain a tracked seam checklist in `tests/test_war_settlement_instances.py` named `WAR_ENTRY_SEAMS_UNDER_TEST`.
  - The checklist must include player declaration, AI declaration, coalition declaration, vassal rebellion, vassal-release rebellion, commitment-paradox outcome, scripted/debug war entry, join-opportunity acceptance, counter-bargain acceptance, armistice collapse, and combat-triggered auto-war fallback.
  - The Slice A invariant test must fail if a listed seam is missing focused coverage.
  ```

## Verdict

============================================
IMPERIAL SETTLEMENT FULL-EUROPE AUDIT - RUN 1
Date: 2026-04-29
============================================

METRICS:
  M1 Fun:                    9/10 PASS
  M2 Clarity:                7/10 PASS
  M3 Work Segmentation:      8/10 PASS
  M4 Contradiction-Freedom:  7/10 PASS
  M5 Completeness:           8/10 PASS

FINDINGS: 4 total (0 critical, 2 major, 2 minor)

CRITICAL BLOCKERS:
  None

VERDICT: GO FOR SLICE A1
  The active spec and implementation plan are ready to start A1 containers/defaults/index scaffolding.
  Fix F-1 before relying on full-Europe synthetic fixture coverage as proof.
  Fix F-2 before Slice C common-peace acceptance work.
============================================
