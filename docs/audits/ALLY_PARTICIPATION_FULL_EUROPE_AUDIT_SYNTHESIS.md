# Imperial Settlement Full-Europe Audit Synthesis

Date: 2026-04-29

Resolution note: This synthesis was consumed by `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.16 and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.13. The NO-GO verdict below applies to the pre-amendment v1.15/v1.12 handoff.

Sources synthesized:
- `docs/audits/ALLY_PARTICIPATION_FULL_EUROPE_AUDIT_RUN3.md`
- External full-Europe audit pasted in chat on 2026-04-29
- Spot verification against live code for combat call sites and elimination behavior

Scope:
- `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.15
- `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.12
- Live code: `backend/commands/combat_executor.py`, `backend/models/world_state.py`, `backend/game_logic/diplomacy.py`, `backend/game_logic/vassal.py`, `backend/models/dialogue_manager.py`

## Executive Result

The two audits agree on the broad state:
- Cross-doc consistency is clean for the active Peace Deals suite.
- Run 2 closure items are present in v1.15/v1.12.
- The core design is still strong and full-Europe scale-ready.
- The spec is **not ready for immediate Slice A1** until a small pre-code amendment batch lands.

Combined verdict: **NO-GO for immediate Slice A1.**

Reason: Slice A would lock schema and war-instance invariants. The combined audits identify side-scoped leader metadata, off-map elimination behavior, proposer-side participant revalidation, and canonical fixture ids as pre-A1 issues.

## Consolidated Findings

### A. Must Fix Before Slice A1

**A1: `leader_source` must be side-scoped.**
- Source: Run 3 F-1.
- Severity: MAJOR.
- Problem: `war_instance` has `attacker_leader` and `defender_leader`, but only one `leader_source`. Coalition scoring can leak to the wrong side in coalition-vs-France wars.
- Fix: Replace with `leader_source_by_side` or `leader_meta_by_side`. Coalition scoring applies only to the side whose source is `coalition_leader`.

**A2: Off-map nations need elimination exemption.**
- Source: external audit E1; spot verified live `_is_nation_eliminated()` scans `world.regions.values()` and `WorldState.capture_region()` eliminates old controller when `get_nation_regions()` is empty.
- Severity: MAJOR.
- Problem: Britain can lose Netherlands and appear to have 0 controlled regions, even though it is an off-map settlement identity. Russia has no live regions. Off-map powers must not be eliminated solely by losing continental proxy holdings.
- Fix: In section 7.6, add that `is_off_map_nation(nation)` blocks elimination from continental proxy loss alone. Off-map powers exit only through explicit scenario/scripted conditions or future off-map-power rules.

**A3: `settlement_confirm.confirm` must revalidate proposer-side participant and beneficiary eligibility.**
- Source: external audit E2.
- Severity: MAJOR.
- Problem: Section 7.4 revalidates leaders and covered pairs, but not whether proposer-side participants exited, rebelled, were eliminated, or stopped being eligible beneficiaries between staging and confirm.
- Fix: Confirm must re-read proposer-side active participants, standing, beneficiary eligibility, and term beneficiaries. If a beneficiary left or changed side, return `active_participant_changed` / `beneficiary_ineligible` with `mutated: False`.

**A4: Full-Europe fixtures need canonical roster ids and aliases.**
- Source: Run 3 F-3.
- Severity: MAJOR.
- Problem: The plan says 13+ nations but does not pin ids. Live ids include `Ottoman`, `Naples`, and `Denmark-Norway`; design prose sometimes says `Ottoman Empire` or `Naples/Two Sicilies`.
- Fix: Add `FULL_EUROPE_SETTLEMENT_ROSTER` with internal ids: `France`, `Britain`, `Austria`, `Prussia`, `Russia`, `Spain`, `Ottoman`, `Sweden`, `Naples`, `Bavaria`, `Saxony`, `Portugal`, `Denmark-Norway`; aliases are display data only.

**A5: Slice A file ownership must include `vassal.py`.**
- Source: Run 3 F-4.
- Severity: MINOR but pre-A1.
- Problem: The plan calls out vassal rebellion/release WAR-entry handling, but Slice A Files omit `backend/game_logic/vassal.py`.
- Fix: Add `backend/game_logic/vassal.py` to Slice A Files; add `backend/commands/vassal_executor.py` as conditional if release-command plumbing changes.

### B. Must Fix Before Slice B1 / Contribution Work

**B1: Split total contribution share from material contribution share and guard div/0.**
- Sources: Run 3 F-2 + external audit F1.
- Severity: MAJOR.
- Problem: Section 9.1 uses `current_episode_total` for `standing_share`, while later sections say standing thresholds use battle + occupation + support only. If all contribution is staying-power-only, `total_side_material_contribution == 0`.
- Fix: Define:
  - `total_contribution_share` for display/history, includes staying power.
  - `material_contribution_share` for `seat`, `consult`, threshold dispatches, gratitude, and shut-out gates.
  - If `total_side_material_contribution <= 0`, all material shares are `0` and standing falls to non-contribution rules.

**B2: Correct the battle call-site inventory.**
- Sources: external audit C1/C2; spot verified in `combat_executor.py`.
- Severity: MAJOR.
- Problem: The spec/plan say glorious charge is outside `_post_combat_pipeline()`, but live `_execute_glorious_charge()` routes through the pipeline. `_execute_attack()` is the real inline diplomatic `record_battle()` path, then calls the pipeline with `skip_diplo_record=True`.
- Fix: Remove glorious charge from the non-pipeline list. Add `_execute_attack()` inline diplomatic record as a required theater-attribution wiring path. Keep auto-dispatch charge in `world_state.py` as non-pipeline.

**B3: Access/supply support cap must be per war-instance, not per episode.**
- Source: external audit E3.
- Severity: MODERATE.
- Problem: "per supporter per war" does not say whether re-entry resets the 5-point cap.
- Fix: State that the cap is per `(war_id, supporter, support_kind)` across the whole war instance; re-entry does not reset it.

### C. Must Fix Before Slice C / Implementation Lock

**C1: Clarify `leader_own_losses` clamp timing.**
- Source: external audit F2.
- Severity: WARNING.
- Fix: State that sub-components are summed first, then clamped to `[-25, 5]`.

**C2: Specify normal non-leader burden penalty.**
- Source: external audit F3.
- Severity: WARNING.
- Fix: In section 11 / direct-score gates, state `direct_score >= 20` has `0` burdened-participant penalty unless another rule applies.

**C3: Add the missing `-15` war-objective-alignment mapping.**
- Source: external audit F4.
- Severity: WARNING.
- Fix: Add an "unrelated harsh terms dominate" column to the objective table.

**C4: Tighten `project_balance_after_settlement()` scale contract.**
- Source: external audit S1.
- Severity: SCALE_WARNING.
- Fix: Require starting from cached `get_nation_regions()` / bloc data and applying term deltas. Do not iterate `world.regions.values()` in preview loops.

**C5: Cache invalidation must occur inside merge/ratification transactions.**
- Sources: external audit S2/S3.
- Severity: SCALE_WARNING.
- Fix: Merge transaction Step 8 should invalidate or rebuild `war_instances_by_leader` / `war_instances_by_participant`. Common-peace ratification must rebuild participant indexes before cross-war reaction pass reads them.

**C6: Territory legitimacy must be named as a `direct_scores` consumer.**
- Source: external audit S4.
- Severity: SCALE_WARNING.
- Fix: Add territory legitimacy / `weak_pressure_penalty` to the section 6.3 memoized `direct_scores` consumer list.

**C7: Note `war_exhaustion` integer division is intentional.**
- Source: external audit F5.
- Severity: MINOR.
- Fix: Add a one-line note that `war_exhaustion // 3` intentionally floors unlike rounded military components.

### D. Final-Gate / Nice-To-Have Fixtures

**D1: Add >3 directly affected cross-war reaction fixture.**
- Source: external audit S5.
- Severity: TEST GAP.
- Fix: Prove all directly affected wars fire even when more than three are involved; the cap applies only to secondary adjacency/sphere-only scans.

**D2: Add full-pipeline stress fixture.**
- Source: external audit S5.
- Severity: TEST GAP.
- Fix: Synthetic 13-nation / 20-war fixture with two AI settlements in one `advance_turn()` to prove bounded caches and no stale reaction reads.

**D3: Clarify off-map-only side wording.**
- Source: external audit E4.
- Severity: MINOR.
- Fix: Use "no eligible leader" where the side still has active off-map participants but none can inherit leadership through normal replacement scoring.

**D4: State same-turn multi-declaration ordering.**
- Source: external audit E5.
- Severity: MINOR.
- Fix: Add that same-turn declarations are processed sequentially by executor order; merge/reuse observes the already-mutated prior declaration.

**D5: Add side-size stress language.**
- Source: external audit E6.
- Severity: MINOR.
- Fix: Add a fixture or note for 15+ participant sides. Standing dilution is handled by material contribution and power-tier overrides; UI remains capped/overflowed.

### E. Routing Cleanup

**E1: Update stale active-version references.**
- Source: Run 3 F-5.
- Severity: MINOR.
- Problem: `ROADMAP.md` and save-format references now point at v1.15/v1.12, but `STATUS.md` and `CLAUDE.md` still mention v1.14/v1.11 in active routing.
- Fix: Update active status/routing to v1.15/v1.12 and note Run 2 closure was applied.

## De-Duped Amendment Batch

Apply in this order:

1. Spec section 7.1/section 7.4: side-scoped leader metadata.
2. Spec section 7.6: off-map elimination exemption.
3. Spec section 7.4/section 10.4: proposer-side participant and beneficiary revalidation.
4. Impl plan fixture contract: canonical 13-nation internal roster ids and aliases.
5. Impl plan Slice A Files: add `vassal.py`.
6. Spec section 9.1: total vs material contribution share plus div/0 guard.
7. Spec/plan Slice B: fix battle call-site inventory (`_execute_attack`, auto-dispatch charge; remove glorious charge as non-pipeline).
8. Spec section 9.2: access/supply cap scope.
9. Spec section 11: leader-loss clamp, normal burden penalty, missing `-15` objective mapping, war-exhaustion floor note.
10. Spec/plan scale contracts: projection cache/deltas, direct-scores consumer list, merge/ratification cache invalidation.
11. Final gate fixtures: >3 directly affected wars, 13-nation/20-war/two-settlement stress, 15+ participant side.
12. Routing docs: `STATUS.md` / `CLAUDE.md` v1.15/v1.12.

## Updated Verdict

============================================
IMPERIAL SETTLEMENT FULL-EUROPE SYNTHESIS
Date: 2026-04-29
============================================

METRICS:
  M1 Fun:                    9/10 PASS
  M2 Clarity:                5/10 FAIL
  M3 Work Segmentation:      7/10 PASS
  M4 Contradiction-Freedom:  7/10 PASS
  M5 Completeness:           6/10 FAIL

CRITICAL BLOCKERS:
  None.

MAJOR PRE-A1 BLOCKERS:
  A1, A2, A3, A4.

VERDICT: NO-GO FOR IMMEDIATE SLICE A1.
  Apply A1-A5 plus E1 before coding Slice A1. Batch B1/B2/B3 at the same time if doing one spec-amendment pass, but they are primarily Slice B blockers. Re-run a short readiness audit after amendments.
============================================
