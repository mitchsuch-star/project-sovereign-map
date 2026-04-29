# Imperial Settlement Full-Europe Spec Audit - Run 3

Date: 2026-04-29

Resolution note: Findings from this run were consumed by `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.16 and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.13. The verdict below describes the pre-amendment v1.15/v1.12 handoff.

Scope:
- Active next-work spec: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.15.
- Coding handoff: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.12.
- Cross-doc checks: `docs/PEACE_DEALS_UMBRELLA_SPEC.md`, `docs/BILATERAL_PEACE_HARDENING_SPEC.md`, `docs/WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`, `docs/WAR_BARGAIN_SPEC.md`, `docs/DIPLOMACY_SPEC.md`, `docs/COALITION_SPEC.md`, `docs/RELIABILITY_COMMITMENTS_SPEC.md`, `docs/SAVE_FORMAT_REFERENCE.md`, `docs/ROADMAP.md`, `docs/STATUS.md`, and `CLAUDE.md`.
- Live-code checks: `backend/game_logic/diplomacy.py`, `backend/models/world_state.py`, `backend/game_logic/coalition.py`, `backend/game_logic/vassal.py`, `backend/models/dialogue_manager.py`, `backend/models/region.py`, `backend/nation_config.py`, and `backend/game_logic/diplomatic_templates.py`.

Method:
- Used `sovereign-map-workflow` preflight and repo routing.
- Used the `peace-deals-spec-audit` scoring model, adapted to the active Ally Participation / Common Peace handoff.
- Re-ran the full-Europe lens after Run 2 closure: 13-20 active nations, 100+ region ids, 20 active pair keys, 6+ participant sides, map-absent Britain/Russia, bounded scans, and synthetic fixture suitability for the planned European roster.

## Metrics

| Metric | Score | Result | Notes |
|--------|-------|--------|-------|
| M1 Fun | 9/10 | PASS | Ally standing, common peace, forced-alliance threat spikes, serial separate-peace fallout, and bargain fallout still create strong agency/consequence loops. |
| M2 Clarity | 6/10 | FAIL | The design is mostly buildable, but A1 leader-source schema and B1 contribution-share naming can be implemented incorrectly from the current wording. |
| M3 Work Segmentation | 7/10 | PASS | A/B/C/D/E gates are sized well; file ownership and fixture roster pinning need tightening before workers split safely. |
| M4 Contradiction-Freedom | 7/10 | PASS | No hard formula/code contradiction remains from Run 2. The remaining issues are soft schema/terminology conflicts inside the active handoff and stale routing docs. |
| M5 Completeness | 7/10 | PASS | Full-Europe mechanics are covered, but the synthetic fixture contract still does not pin the actual DG-1 roster or internal id/display aliases. |

## Findings

F-1: `leader_source` is global even though leader replacement is side-specific.
  Severity: MAJOR
  Location: `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` section 7.1 / section 7.4; `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Slice A
  Problem: The `war_instance` schema has separate `attacker_leader` and `defender_leader`, but only one `leader_source`. Section 7.4 says to use `coalition_leadership_score()` only when `leader_source == "coalition_leader"`, which can leak coalition-specific scoring to the wrong side in a full-Europe war. Example: a coalition declares on France; the attacker side is coalition-led, but defender-side replacement must still use normal `war_leader_score()` and the defender-side anchor. A single global source cannot express that.
  Fix: Replace the single field with side-scoped leader metadata, e.g. `leader_source_by_side = {"attackers": "originator|coalition_leader|scripted", "defenders": "origin_target|coalition_target|scripted"}` or a richer `leader_meta_by_side`. Update section 7.4 so coalition scoring applies only to the side whose source is `coalition_leader`. Add an A1/A3 fixture proving coalition-side replacement uses coalition scoring while the opposite side uses `war_leader_score()` with its own same-side anchor.
  Affected metrics: M2, M4, M5

F-2: Standing-share formula conflicts with the material-contribution threshold rule.
  Severity: MAJOR
  Location: `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` section 9.1, section 8.3, section 9.2
  Problem: Section 9.1 defines `standing_share[nation] = current_episode_total(nation) / total_side_current_episode_contribution`, but `current_episode_total` includes `staying_power`. Later, section 8.3 and section 9.2 correctly say seat/consult thresholds, contribution dispatches, and major shut-out eligibility use `material_contribution_share` only (`battle + occupation + support`). At full-Europe scale, using the section 9.1 formula literally lets staying-power padding dilute real fighters or inflate passive participants.
  Fix: In section 9.1, define two names explicitly: `total_contribution_share` for display/history and `material_contribution_share = material_contribution_points / total_side_material_contribution` for standing thresholds, dispatch thresholds, gratitude, and shut-out grievance gates. In payload examples and memory shape, either rename `contribution_share` to `material_contribution_share` where it drives standing or include both fields with distinct semantics.
  Affected metrics: M2, M4

F-3: Full-Europe fixture contract does not pin the actual European roster or id aliases.
  Severity: MAJOR
  Location: `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Full-Europe Test Fixture Contract
  Problem: The plan now requires an explicit 13+ nation roster, but does not name it. Cross-doc and live-code names are not identical: `SCALE_READINESS_PLAN.md` uses display names like `Ottoman Empire` and `Naples/Two Sicilies`, while live `NATION_POWER_TIERS` uses internal ids like `Ottoman`, `Naples`, and `Denmark-Norway`. A worker can satisfy "13+ nations" with arbitrary or display-name ids and miss the exact all-Europe pressure cases.
  Fix: Add a canonical `FULL_EUROPE_SETTLEMENT_ROSTER` fixture contract with internal ids and display aliases. Minimum internal ids: `France`, `Britain`, `Austria`, `Prussia`, `Russia`, `Spain`, `Ottoman`, `Sweden`, `Naples`, `Bavaria`, `Saxony`, `Portugal`, `Denmark-Norway`. Add aliases for player-facing labels (`Ottoman Empire`, `Naples/Two Sicilies`) and require explicit power tiers/desire profiles for each fixture id.
  Affected metrics: M2, M5

F-4: Slice A file ownership omits `vassal.py` despite direct WAR-entry requirements.
  Severity: MINOR
  Location: `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Slice A Files / Build
  Problem: Slice A's file list names `world_state.py`, `diplomacy.py`, `war_status.py`, save docs, and tests. The Build section correctly calls out `backend/game_logic/vassal.py` rebellion handling and vassal-release rebellion, and live code shows `check_vassal_rebellion()` sets `WAR` then calls `_process_war_cascade()`. Missing the file in the ownership list is a split-work hazard.
  Fix: Add `backend/game_logic/vassal.py` to Slice A Files. If the implementation touches release UI plumbing, add `backend/commands/vassal_executor.py` as a conditional file note.
  Affected metrics: M2, M3

F-5: Session routing docs still point at v1.14/v1.11.
  Severity: MINOR
  Location: `docs/STATUS.md`; `CLAUDE.md`
  Problem: `ROADMAP.md`, the spec, implementation plan, and save-format reference point to v1.15/v1.12, but `STATUS.md` and `CLAUDE.md` still route active settlement work to v1.14/v1.11. The files are correct, but cold-start agents may think Run 2 closure did not land.
  Fix: Update `STATUS.md` and `CLAUDE.md` active-phase references to `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.15 and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.12, noting that Run 2 full-Europe audit closure has been applied.
  Affected metrics: M2, M4

## Passed Full-Europe Checks

- Run 2 closure items are present: map-absent Britain/Russia handling, map-absent leader guard, vassal/forced-origin standing clause, formula guards, memoized local-balance warning guidance, delta-projection note, and connected-component merge bound.
- `side_pressure_score` no longer has the empty-generator `max()` gap and computes direct scores once per preview/confirm evaluation.
- Common-peace acceptance uses raw treaty harshness from `diplomatic_templates.py` while preserving the existing 1.0-clamped bilateral helper.
- Britain proxy-capital handling is documented in spec, plan, and save-format notes: `NATION_CAPITALS["Britain"] == "Netherlands"` is not a true settlement capital.
- The implementation plan explicitly requires map-absent Britain and Russia fixtures with zero active army strength.
- Direct WAR-entry seam inventory is durable in `tests/test_war_settlement_instances.py` and covers cascade, direct joins, counter-bargains, vassal rebellion, vassal-release rebellion, armistice collapse, scripted/debug entry, and combat-triggered fallback.
- Contribution accrual remains event-driven, with staying power as the only per-turn settlement accrual and no all-region scan in `advance_turn()`.
- `settlement_confirm` and `incoming_settlement_offer` are already present in `DialogueManager` taxonomy; the plan correctly owns the missing mailbox label/route work in Slice C2.
- UI density gates still cover synthetic 6+ participant payloads, sectioned settlement review, scroll/overflow behavior, and no text overlap.

## Improvement Steps

Step 1: Fix F-1.
  File: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md`
  Section: section 7.1 and section 7.4
  Action: Replace/Add
  Content:
  ```text
  Replace `leader_source` with side-scoped metadata:
  leader_source_by_side = {
      "attackers": "originator",       # originator | coalition_leader | scripted
      "defenders": "origin_target",    # origin_target | coalition_leader | scripted
  }

  Coalition leadership scoring applies only to the side whose
  `leader_source_by_side[side] == "coalition_leader"` and whose active
  coalition target matches this political conflict. The opposite side always
  uses `war_leader_score()` unless its own source is also `coalition_leader`.
  ```

Step 2: Fix F-1 tests.
  File: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`
  Section: Slice A Gate
  Action: Add
  Content:
  ```text
  Coalition leader-source fixture proves side-scoped leader metadata:
  attacker-side coalition replacement uses coalition scoring, defender-side
  replacement in the same war uses `war_leader_score()` with the defender
  `origin_target` anchor, and neither side reads the other side's source.
  ```

Step 3: Fix F-2.
  File: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md`
  Section: section 9.1
  Action: Replace formula block
  Content:
  ```text
  total_contribution_share[nation] =
      current_episode_total(nation) / total_side_current_episode_contribution

  material_contribution_points[nation] = battle + occupation + support
  material_contribution_share[nation] =
      material_contribution_points[nation] / total_side_material_contribution

  Use `material_contribution_share` for seat/consult thresholds,
  contribution-threshold dispatches, major shut-out grievance eligibility,
  and reusable `settlement_gratitude`. Use `total_contribution_share` only for
  display/history rows that intentionally include staying power.
  ```

Step 4: Fix F-3.
  File: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`
  Section: Full-Europe Test Fixture Contract
  Action: Add
  Content:
  ```text
  Canonical fixture roster ids:
  France, Britain, Austria, Prussia, Russia, Spain, Ottoman, Sweden, Naples,
  Bavaria, Saxony, Portugal, Denmark-Norway.

  Display aliases are data, not fixture ids: `Ottoman` may display as
  `Ottoman Empire`; `Naples` may display as `Naples/Two Sicilies`.
  Fixture helpers must use internal ids for `NATION_POWER_TIERS`,
  `NATION_DESIRE_PROFILES`, war participants, contribution records, and
  settlement terms.
  ```

Step 5: Fix F-4.
  File: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`
  Section: Slice A Files
  Action: Add
  Content: Add `backend/game_logic/vassal.py` to the files list, with `backend/commands/vassal_executor.py` as conditional if release-command plumbing changes.

Step 6: Fix F-5.
  File: `docs/STATUS.md`, `CLAUDE.md`
  Section: active Peace Deals / Imperial Settlement routing
  Action: Replace stale versions
  Content: Replace active v1.14/v1.11 references with v1.15/v1.12 and note that full-Europe audit Run 2 closure is applied.

## Verdict

============================================
IMPERIAL SETTLEMENT FULL-EUROPE AUDIT - RUN 3
Date: 2026-04-29
============================================

METRICS:
  M1 Fun:                    9/10 PASS
  M2 Clarity:                6/10 FAIL
  M3 Work Segmentation:      7/10 PASS
  M4 Contradiction-Freedom:  7/10 PASS
  M5 Completeness:           7/10 PASS

FINDINGS: 5 total (0 critical, 3 major, 2 minor)

CRITICAL BLOCKERS:
  None

PRE-SLICE-A1 FIXES REQUIRED:
  F-1: side-scoped leader-source schema.
  F-3: canonical full-Europe fixture roster ids.
  F-4: Slice A file ownership for vassal WAR-entry paths.

BEFORE SLICE B:
  F-2: split total contribution share from material contribution share.

DOC ROUTING CLEANUP:
  F-5: update STATUS/CLAUDE version references.

VERDICT: NO-GO FOR IMMEDIATE SLICE A1.
  The core design remains strong, but A1 would lock the wrong schema shape if
  `leader_source` stays global. Apply F-1, F-3, and F-4, then rerun a short
  Slice A readiness audit. F-2 can land before B1 if A1 needs to proceed
  after the schema/fixture fixes.
============================================
