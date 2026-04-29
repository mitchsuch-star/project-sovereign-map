# Imperial Settlement Full-Europe Spec Audit - Run 2

Date: 2026-04-29

Scope:
- Active next-work spec: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.14.
- Coding handoff: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.11.
- Cross-doc checks: `DIPLOMACY_SPEC.md`, `COALITION_SPEC.md`, `WAR_BARGAIN_SPEC.md`, `WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md`.
- Live code checks: `backend/game_logic/diplomacy.py`, `backend/models/world_state.py`, `backend/game_logic/coalition.py`, `backend/models/dialogue_manager.py`, `backend/models/region.py`, `backend/nation_config.py`, `backend/game_logic/diplomatic_templates.py`.

Method:
- Three parallel audit agents: (1) scale formula correctness, (2) cross-doc consistency, (3) nation roster coverage.
- Full-Europe stress targets: 13-20 active nations, 100+ regions, 78+ bilateral pairs, 20 simultaneous pairwise wars, 6+ participant sides, off-map Britain and Russia.
- Builds on Run 1 findings (F-1 through F-4 from the same date).

## Metrics

| Metric | Score | Result | Notes |
|--------|-------|--------|-------|
| M1 Fun | 9/10 | PASS | Unchanged from Run 1. |
| M2 Clarity | 6/10 | PASS | Pseudocode formulas omit guards that the prose specifies; off-map generalization is Britain-specific when Russia needs the same treatment; vassal standing rules are implicit. |
| M3 Work Segmentation | 8/10 | PASS | Unchanged from Run 1. |
| M4 Contradiction-Freedom | 8/10 | PASS | Cross-doc audit found no new contradictions beyond Run 1's F-2 (stale DIPLOMACY_SPEC harshness). |
| M5 Completeness | 7/10 | PASS | Off-map nation generalization, vassal auto-join standing, desire-profile coverage for rival_strengthened, and preview memoization guidance all missing. |

## Findings

### Scale Formula Issues

**F-S1: `side_pressure_score` max() on empty generator — division guard missing from pseudocode**
- Severity: MAJOR
- Location: Spec §6.3, `pressure_terms` formula (line ~183)
- Problem: The inner `max(get_war_score_for(...) for side_member ... if world.is_at_war(side_member, enemy))` will raise `ValueError` if no proposer-side member is at war with a covered enemy. The spec says this is a "hard stop" in prose (line 200), but the pseudocode formula passes the generator directly into `max()` without a `default` argument or pre-check. At full-Europe scale, partial-coverage common peace where some enemies have no direct pair against the proposer side is plausible through coalition cascade. An implementer following the pseudocode literally will hit `ValueError`.
- Fix: Add a guard to the formula block: `if no active pair exists for covered enemy → hard stop no_direct_war_score_for_covered_enemy` BEFORE the `max()` call. This makes the prose and pseudocode agree.

**F-S2: `compute_local_balance_warning()` call-site multiplier needs memoization guidance**
- Severity: MAJOR
- Location: Spec §8.3 (lines 471-478), §17.3 (line 1695)
- Problem: `rival_strengthened[nation] = compute_local_balance_warning(nation, settlement_terms)` is called per participant (6-8 times per settlement preview). Each call scans all terms, beneficiaries, and their adjacent regions. With 10+ terms across 100 regions, adjacency lookups total `participants × terms × avg_adjacency ≈ 6 × 10 × 6 = 360`. This multiplies again during draft revision (the player iterates). The spec does not require memoizing the per-term beneficiary/adjacency map across participant calls.
- Fix: Add implementation guidance to §17.3: "Build the term-beneficiary-adjacency map once per settlement evaluation and pass it into each per-nation `compute_local_balance_warning()` call. Do not re-derive region adjacency per participant."

**F-S3: `bucket_points` normalization div/0 when `side_bucket_raw == 0`**
- Severity: MINOR
- Location: Spec §9.2, formula line ~584
- Problem: `bucket_points[nation] = round((nation_bucket_raw / side_bucket_raw) * bucket_weight)` — the prose on line 587 says zero-raw buckets award zero points, but the formula pseudocode has no guard. In an early-war settlement with no support events, `side_bucket_raw` for support is zero.
- Fix: Add a guard to the formula: `if side_bucket_raw <= 0: bucket_points[nation] = 0` or add a comment referencing the prose rule.

**F-S4: `project_balance_after_settlement()` needs delta-projection guidance**
- Severity: MINOR
- Location: Spec §11 Step 4 (line ~1121), implementation plan Slice C1
- Problem: The spec says "never mutates WorldState during preview" but doesn't specify how to project post-settlement bloc share. At full scale (13-20 nations), a full `WorldState` deep copy is wasteful. The implementation needs delta projection (modify only the affected alignment/ownership relationships in a copy), not a full state clone.
- Fix: Add one line to §11 or §17.3: "`project_balance_after_settlement()` uses lightweight delta projection on affected alignment/ownership data, not a full `WorldState` deep copy."

**F-S5: Merge connected-component lacks explicit termination statement**
- Severity: MINOR
- Location: Spec §7.2, merge rule (line ~285)
- Problem: The spec says "compute the full connected component of `war_instances` linked by the cascade" but does not specify cycle detection or termination. At 20 active wars the bound is small (max 20 visits), but missing explicitness could allow a naive recursive implementation to re-visit.
- Fix: Add: "Connected component discovery visits each active `war_instance` at most once; bounded by the number of active instances (typically < 20)."

**F-S6: Burdened participant penalty cap needs tuning fixture for 5+ enemies**
- Severity: INFO
- Location: Spec §11 Step 4 (line ~1139)
- Problem: The cap is `min(burdened_count, 2) * -30 = -60`. Burdening participants 3/4/5 is mechanically free beyond -60. The spec acknowledges this is intentional but doesn't require a tuning fixture proving `term_harshness_penalty` stacking alone makes 5-enemy packages cost more than 2-enemy packages.
- Fix: Add to Slice C tuning gate: "Include a 4-5 burdened non-leader fixture proving the total formula rejects imperial over-reach packages that would pass if only burdened_participant_penalty were evaluated."

### Nation Roster Issues

**F-A1: `war_leader_score()` allows off-map nations to become war leaders through replacement**
- Severity: MAJOR
- Location: Spec §7.4 `war_leader_score` formula
- Problem: Off-map Britain (and Russia) have `active_army_strength = 0`. Their score is `300 + 0 + relation_bias`. A drawn-down Austria with 500 troops and negative relation could lose leadership to Britain. The spec does not guard against off-map nations becoming replacement leaders for continental wars they cannot fight. This creates nonsensical common-peace flows where an off-map leader "accepts" packages it cannot enforce.
- Fix: Add an explicit rule: "A candidate with no home-capital region on the live map AND zero `active_army_strength` cannot be promoted to leader through `war_leader_score()` replacement. Only originator status, explicit coalition-leader source, or direct side-anchor precedence can make an off-map nation a war leader."

**F-A2: Off-map generalization is Britain-specific — Russia needs the same treatment**
- Severity: MAJOR
- Location: Spec §0, §6.3 (off-map Britain), §7.4 (leader scoring), §11 (`leader_own_losses`)
- Problem: Russia is a `major` in `NATION_POWER_TIERS` but has no capital, no regions, no marshals in the live map — the same situation as Britain. The spec's off-map rules, `is_off_map_capital_proxy()` helper, and `get_settlement_home_capital()` helper are described only for Britain. Russia (and any future off-map major) needs the same treatment for capital-loss scoring, leader replacement, and contribution theater attribution.
- Fix: Generalize §0 language from "Off-map Britain" to "any nation with no home-capital region on the live map." The fixture contract should include Russia as a second off-map major alongside Britain.

**F-A3: Vassal auto-join standing is unspecified**
- Severity: MODERATE
- Location: Spec §8.2 standing classification
- Problem: Nations like Saxony, Bavaria, Naples may START as French vassals and auto-join wars via cascade. The spec says `minor/vassal/liberated state receiving or losing a direct outcome` gets `beneficiary_only`, but never specifies: (a) whether vassal auto-joins have the same standing rules as voluntary allies, (b) whether vassal contribution counts independently in the side total, (c) whether forced-alliance nations (with forced origin) share voluntary-ally standing rules. In the France campaign, 3-4 vassals plus forced-allied minors will routinely auto-join.
- Fix: Add a vassal/forced-origin clause to §8.2: "Vassal auto-joins receive at most `beneficiary_only` unless they independently meet material-contribution thresholds. Forced-alliance co-belligerents (with forced origin) share the same standing rules as voluntary allies. Vassal contribution counts independently in the side total."

**F-A4: `NATION_DESIRE_PROFILES` coverage gap blocks `rival_strengthened` for most nations**
- Severity: MODERATE
- Location: Spec §8.3 input #7; live `diplomatic_templates.py`
- Problem: `compute_local_balance_warning()` depends on `covets_regions` from desire profiles. Only 4 of 13 planned nations have profiles (Prussia, Austria, Britain, Saxony). At full scale, `rival_strengthened` will silently never fire for Spain, Ottoman, Sweden, Naples, Bavaria, Portugal, Denmark-Norway, or Russia because they have no `covets_regions` data. The spec uses this as a standing input and cross-war reaction trigger.
- Fix: Add to the synthetic fixture contract (extending Run 1 F-1): "Full-Europe test fixtures must include synthetic desire profiles with non-empty `covets_regions` for all 13 test nations so `rival_strengthened` paths exercise non-trivial data." Also add an implementation note that the helper must still produce valid results (the adjacency and bloc checks) when `covets_regions` is empty.

**F-A5: Russia has no `NATION_CAPITALS` entry — cannot resolve settlement home capital**
- Severity: MODERATE
- Location: `backend/models/region.py` NATION_CAPITALS (5 entries only)
- Problem: Russia is major but has no entry. The spec requires `get_settlement_home_capital(nation)` to distinguish proxy holdings from true capitals. Russia cannot be resolved through this helper without a NATION_CAPITALS entry or an explicit off-map exemption.
- Fix: The off-map generalization from F-A2 handles this — any nation absent from NATION_CAPITALS or with a documented proxy is treated as off-map. The fixture contract must include Russia. No spec change needed beyond F-A2.

### Cross-Doc Consistency Issues

**F-C1: DIPLOMACY_SPEC harshness ownership contradicts live code (confirms Run 1 F-2)**
- Severity: MAJOR (confirmed, not new)
- Location: `DIPLOMACY_SPEC.md` harshness section
- Problem: Already flagged in Run 1. DIPLOMACY_SPEC says `calculate_harshness()` lives in `diplomacy.py`. Live code uses `calculate_treaty_harshness()` in `diplomatic_templates.py`. Settlement spec correctly references the live location.
- Fix: Per Run 1 F-2 recommendation.

**F-C2: All other cross-doc references verified clean**
- Severity: PASS
- Details: COALITION_SPEC has zero `threat_coalition` references and `+15` forced-alliance matches exactly. WAR_BARGAIN_SPEC confirms France-claim scope. WPS objective types match the five settlement spec uses. `settlement_confirm` is already in `HARD_STOP_TYPES`. `incoming_settlement_offer` is already in `CURRENT_TURN_OFFER_TYPES`. All live code seams exist: `_process_war_cascade()` at diplomacy.py:7675, `record_battle()` at diplomacy.py:8254, `_ratify_treaty()` at world_state.py:5298, `_process_treaty_clauses()` at world_state.py:5961, `_process_british_subsidy()` at coalition.py:969.

## Passed Full-Europe Checks

- All formulas terminate with finite results when guards are added per findings above.
- Merge transaction order is well-specified with abort semantics.
- Theater attribution one-hop rule correctly bounds battle credit at scale.
- Leader replacement is rare-event only (elimination, separate peace), not a hot-path.
- `risk_adjusted_theater_strength` is numerically stable: `max(1, ...)` + `min(0.5, ...)` bounds the multiplier to `[1.0, 1.5]`.
- Cross-war reaction checks correctly bound secondary scans at 3 wars while allowing all directly affected wars.
- Contribution accrual is event-driven (battle, occupation, support) plus one bounded per-turn pass (staying power over active participants only).
- `war_instances_by_participant` index correctly prevents repeated all-instance filtering.
- Common-peace ratification iterates only covered active pairs, not all war pairs.
- AI common-peace anti-spam correctly separates per-`war_id` cooldowns from bilateral cooldowns.

## Improvement Steps

Step 1: Fix F-S1.
  File: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md`
  Section: §6.3, `side_pressure_score` formula block
  Action: Add guard before `max()` call
  Content: Add a line before the generator: `# Pre-filter: if no proposer_side_participants is_at_war with enemy, hard stop no_direct_war_score_for_covered_enemy` and wrap the `max()` with an explicit empty-check or `default` parameter note.

Step 2: Fix F-S2.
  File: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md`
  Section: §17.3 derived-at-settlement-time
  Action: Add memoization guidance
  Content: "Build the term-beneficiary-adjacency map once per settlement evaluation and pass it into each per-nation `compute_local_balance_warning()` call. Do not re-derive region adjacency per participant."

Step 3: Fix F-A1 + F-A2 (combined off-map leader guard).
  File: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md`
  Section: §0 (Scale and Ownership Contract) and §7.4 (War leaders)
  Action: Generalize off-map rules and add leader guard
  Content:
  - §0: Replace "Off-map Britain" framing with "any nation with no home-capital region on the live map (currently Britain and Russia)."
  - §7.4: Add rule: "A candidate with no home-capital region on the live map AND zero `active_army_strength` cannot be promoted to leader through `war_leader_score()` replacement. Only originator status, explicit coalition-leader source, or direct side-anchor precedence can make an off-map nation a war leader."

Step 4: Fix F-A3.
  File: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md`
  Section: §8.2 standing classification rules
  Action: Add vassal/forced-origin clause
  Content: "Vassal auto-joins receive at most `beneficiary_only` unless they independently meet material-contribution thresholds for `consult` or `seat`. Forced-alliance co-belligerents (nations with `forced_origin=True`) share the same standing rules as voluntary allies. Vassal contribution counts independently in the side total."

Step 5: Fix F-A4.
  File: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`
  Section: Scale Rules / Full-Europe Test Fixture Contract
  Action: Add desire-profile requirement
  Content: "Full-Europe test fixtures must include synthetic `NATION_DESIRE_PROFILES` entries with non-empty `covets_regions` for all 13 test nations so `rival_strengthened` paths exercise non-trivial data. `compute_local_balance_warning()` must still produce valid results (adjacency and bloc checks) when `covets_regions` is empty."

Step 6: Fix F-S3.
  File: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md`
  Section: §9.2, formula block after `bucket_points`
  Action: Add div/0 guard to pseudocode
  Content: Add `# Guard: if side_bucket_raw <= 0, award 0 points (see prose rule below)` above the formula line.

Step 7: Fix F-S4.
  File: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md`
  Section: §11, after `project_balance_after_settlement()` description
  Action: Add delta-projection note
  Content: "Implementation must use lightweight delta projection on affected alignment/ownership data, not a full `WorldState` deep copy."

Step 8: Fix F-S5.
  File: `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md`
  Section: §7.2, merge rule
  Action: Add termination statement
  Content: "Connected component discovery visits each active `war_instance` at most once; bounded by the count of active instances (typically < 20) and terminates when no new linked instances are discovered."

## Verdict

============================================
IMPERIAL SETTLEMENT FULL-EUROPE AUDIT - RUN 2
Date: 2026-04-29
============================================

METRICS:
  M1 Fun:                    9/10 PASS
  M2 Clarity:                6/10 PASS
  M3 Work Segmentation:      8/10 PASS
  M4 Contradiction-Freedom:  8/10 PASS
  M5 Completeness:           7/10 PASS

FINDINGS: 12 total (0 critical, 5 major, 4 moderate, 3 minor)
  New major:    F-S1, F-S2, F-A1, F-A2 (plus F-C1 confirms Run 1)
  New moderate: F-A3, F-A4, F-A5
  New minor:    F-S3, F-S4, F-S5

CRITICAL BLOCKERS:
  None

PRE-SLICE-A1 FIXES RECOMMENDED:
  F-A1 + F-A2: Off-map leader guard (affects §7.4 war_leader_score design)
  F-A3: Vassal standing clause (affects §8.2 standing classification)
  F-S1: Formula guard (affects §6.3 pseudocode correctness)

BEFORE SLICE B:
  F-S2: Memoization guidance for compute_local_balance_warning
  F-A4: Desire-profile fixture requirement

BEFORE SLICE C:
  F-S4: Delta projection guidance
  F-S6 (INFO): 5-enemy burdened fixture

VERDICT: GO FOR SLICE A1 after applying Steps 1, 3, 4.
  The three pre-A1 fixes affect formula pseudocode and standing rules that
  A1 scaffolding will implement. Fix them in the spec before coding starts
  so the implementation matches the corrected design intent.

  Run 1 F-1 (fixture contract) and F-2 (DIPLOMACY_SPEC harshness) remain
  open and should be fixed concurrently.
============================================
