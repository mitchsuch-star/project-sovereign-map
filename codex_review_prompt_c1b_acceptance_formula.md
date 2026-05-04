# Codex code review — Imperial Settlement Slice C1b acceptance formula

You are reviewing commit **`2cc8b1c` on branch `master`** of `mitchsuch-star/project-sovereign-map` (Napoleonic strategy game; FastAPI backend, Godot frontend). Pull that exact SHA and review against parent `993fda8`.

```
git fetch origin && git checkout 2cc8b1c
git diff 993fda8..2cc8b1c --stat
```

## What this commit does

Lands the **Slice C1b common-peace acceptance formula** sub-gate of `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §6.acceptance lines 1095-1147. C1b layers the nine-component acceptance pipeline on top of the C1a side-pressure helpers without any mutation, ratification, or live wiring into `diplomacy.py` / `diplomatic_templates.py`. C2 (endpoints / dialogue / Godot routing) will wire preview/confirm against this helper in a later slice.

Prior Slice C landings:

1. **C1a side-pressure foundation** (commits `f55ee1a` + `993fda8`) — `compute_direct_scores_by_enemy`, `select_direct_score`, `compute_side_pressure_score` (spec §6.3 power-weighted average), hard stops `no_covered_enemy_participants` / `no_direct_war_score_for_covered_enemy`. Already landed.
2. **C1b acceptance formula (this commit)** — the full nine-component formula plus tuning fixtures.

This commit ships nine pure component helpers + the pipeline composer + the projection helper + the threat-preview helper:

- `backend/game_logic/settlement_scoring.py`:
  - `calculate_base_side_pressure(score) -> {score, raw_score, side_pressure_score, scale}` — `round(score * 0.65)` half-away-from-zero, clamp `[-50, 60]` (spec line 1113).
  - `calculate_term_harshness_penalty(raw) -> {score, raw_total_harshness, capped_at_ceiling, normalized, magnitude, ceiling}` — `-min(45, round((min(raw, 1.5)/1.5) * 45))`. Half-away-from-zero rounding at component boundary, then negate, then floor at -45 (spec line 1115).
  - `calculate_settlement_tier_legitimacy(side_pressure_score, raw_total_harshness, terms) -> {score, raw_score, tier, tier_base, ceiling, exceeded_ceiling, mismatch_penalty, raw_total_harshness}` — tier from existing `diplomacy.get_settlement_tier()` keyed on `abs(side_pressure_score)`; base `+15 / +10 / +5 / 0 / -10` for `total_victory / harsh_peace / dictated_terms / favorable_terms / white_peace`; subtract `-10` if package raw harshness exceeds the tier ceiling (`white_peace=0.10 / favorable_terms=0.25 / dictated_terms=0.45 / harsh_peace=0.70 / total_victory=1.00`); white_peace + any non-trivial term auto-mismatch; clamp `[-20, 15]` (spec lines 1099, 1114, 1188-1196).
  - `calculate_leader_own_losses(world, *, accepting_leader, settlement_terms, accepting_leader_regions_at_evaluation=None, accepting_leader_mapped_holdings_at_entry=None) -> {score, raw_score, regions_ceded_count, ceded_regions, capital_lost, home_capital, kept_all_with_holdings, has_regions_at_evaluation, lost_mapped_holdings_count, lost_mapped_holdings_subtotal, forced_aligned_against_leader, components, clamp}` — sum sub-components BEFORE clamping `[-25, 5]`; lost-mapped-holdings sub-component internally capped at `-10` (spec line 1186); treats `forced_alliance` against the leader as capital-equivalent sovereignty loss; reads `world.get_settlement_home_capital()` and skips capital-loss subcomponent on `None` per spec line 1117.
  - `calculate_burdened_participant_penalty(world, *, accepting_leader, proposer_side_participants, covered_enemy_participants, settlement_terms, direct_scores, war_objectives_by_enemy=None) -> {score, raw_penalty, burdened_count, per_burden, aggregate_cap, applied_floor}` — accepting leader excluded (spec line 1125); per-burden `-30` for `direct_score < 0` / `-15` for `0 <= direct_score < 20` / `+0` for `>= 20`; major-tier extra `-10` unless capital occupied OR term matches war objective (spec line 1229); aggregate cap `-30 * min(burdened_count, 2)` floored at `-60` (spec line 1139).
  - `calculate_war_objective_alignment(world, *, war_id, proposer_side_leader, proposer_side_participants, accepting_leader, covered_enemy_participants, settlement_terms) -> {score, selected_objective, alignment_label, war_id}` — selects relevant objective per spec line 1174 chain (leader-vs-accepting → leader-vs-covered → all-proposers WPS-priority `subjugation/forced_alliance/conquest/liberation/defense` → oldest `created_turn`); evaluates against the per-type table at lines 1176-1183; defense uses partial detection (some target_regions restored = +5, all = +15); returns `score=0, label='no_objective'` when no live record (spec line 1174); clamp `[-20, 15]`.
  - `calculate_war_exhaustion_component(world, *, accepting_leader, war_id=None, covered_enemy_participants=None, apply_relevance_cap=False) -> {score, raw_per_nation_exhaustion, relevant_exhaustion, unrelated_exhaustion, applied_relevance_cap}` — INTENTIONAL **floor** division `min(20, raw // 3)` per spec line 1120 (distinct from `round()` everywhere else); `apply_relevance_cap=False` is the C1b ship default per plan line 218 ("may adopt the spec's relevance cap only if the multi-war exploit fixture proves unrelated cheap wars make settlements absurdly cheap"); raw + relevance-split inputs ALWAYS exposed in debug output per plan line 222.
  - `calculate_abandoned_by_ally_mod(war_instance, *, accepting_side, current_turn) -> {score, raw_score, recent_defectors, applied_cap, lookback_turns}` — counts `war_instance["separate_peaced"]` records on `accepting_side` within `ABANDONED_LOOKBACK_TURNS=3`; `+5/defector` capped `+15` (spec line 1121, 786-793).
  - `project_balance_after_settlement(world, *, war_id, settlement_terms) -> {pre_hegemon, post_hegemon, pre_share, post_share, crossed_band, deepened_band, hegemon_swap, modifier}` — pure projection helper for `projected_hegemony_mod` (spec lines 1200-1217); reads cached `get_active_nations`, `get_nation_regions`, `get_diplomatic_state`, `world.vassals`, `get_power_tier` only; applies term deltas in-memory only (deterministic order: liberation → forced_alliance → territory → vassalage); recomputes max-bloc-share against the projected snapshot; modifier `-20/-10/-5` per crossed/deepened `60% / 50% / 33%` band, `+10` for de-escalation, clamp `[-20, 10]`.
  - `compute_forced_alliance_threat_preview(world, *, settlement_terms) -> {forced_alliance_clauses, projected_threat_delta, current_threat, projected_threat, crossed_thresholds}` — `+15/clause` projected delta + crossed coalition thresholds (60 brewing / 80 instant / 90 cooldown-override) per spec line 1273.
  - `calculate_common_peace_acceptance(world, *, war_id, war_instance, proposer_side, accepting_side, accepting_leader, covered_enemy_participants, settlement_terms, ...) -> {score, verdict, components, component_debug, side_pressure_score, side_pressure_result, direct_scores, direct_score_sources, hard_stops, feedback, raw_total, raw_total_harshness, near_acceptable_threshold, accept_threshold, ...}` — composes the nine components in deterministic order, builds memoized `direct_scores` from C1a, bubbles up hard stops with `score=None, verdict='reject'`, applies acceptance threshold `>= 50` accept / `35-49` near_acceptable / `< 35` reject, builds top-2-component feedback by absolute negative magnitude, surfaces forced-alliance threat preview in debug.

- `backend/game_logic/diplomatic_templates.py`:
  - Refactored: `_accumulate_raw_treaty_harshness(treaty)` extracted as the shared clause + demand iteration. Existing `calculate_treaty_harshness(treaty)` (1.0-clamped, bilateral) preserved — bilateral callers unchanged. **NEW** `calculate_raw_treaty_harshness(treaty)` returns the unclamped sum exclusively for common-peace acceptance per spec line 1115.

- `tests/test_common_peace_acceptance.py` (new, 57 tests):
  - **Component unit tests:** parametrized `base_side_pressure` (5 cases including Pressburg 70→46 and clamps), parametrized `term_harshness_penalty` (5 cases including the 1.5 ceiling and over-ceiling clamp), 5 `settlement_tier_legitimacy` tests (Pressburg harsh_peace, total_victory within ceiling, dictated_terms exceeded ceiling, white_peace zero terms = -10 only, white_peace with non-trivial term = -20), 5 `leader_own_losses` tests (Pressburg two regions kept capital, capital ceded triggers -15 + clamp to -25, keeps_all bonus +5, zero-region leader no bonus, lost_mapped_holdings capped at -10), 4 `burdened_participant_penalty` tests (low direct_score minor, major uncovered stacks -10, aggregate cap -60 for 2+, accepting leader excluded), 3 `war_objective_alignment` tests (no live → 0, conquest satisfied = +15, clamp bounds), parametrized `war_exhaustion` (5 floor-division cases including `41 // 3 = 13` ≠ `round(41/3) = 14`), 3 `abandoned_by_ally_mod` tests (count, cap at 15, lookback exclusion).
  - **Hard-stop bubble:** 2 tests (empty covered → score=None, no direct war score → score=None).
  - **14 tuning-gate fixtures:** Pressburg worked example, Tilsit non-leader burden, coalition split via separate-peace abandoned-mod boost, decisive-victory-without-total-victory, total-victory-harsh-terms-not-hopeless, minor-power limited common peace, mixed-strength partial-vs-full coverage, full-Europe narrow-vs-full-vs-serial comparison, 6+ participant coalition, Britain-led defense (`NATION_CAPITALS["Britain"] == "Netherlands"`), mapped-home / capital-cession / restoration variants, multi-forced-alliance threat preview projecting +30 with crossed thresholds, AI-defender alignment ≤ +5 reaches accept band, war-exhaustion exploit exposes inputs.
  - **Monotonicity + cross-formula:** 3 tests (monotonic side_pressure, one-covered-enemy uses full formula, final clamp pinned).
  - **Debug exposure:** 5 tests (all nine components, chosen objective diplo_key/declaring/target/type, raw + relevance-split exhaustion, forced-alliance threat delta + crossed thresholds, top-2 feedback components on rejection).

- `tests/test_common_peace_harshness.py` (new, 3 tests): bilateral 1.0-clamped behavior preserved, raw helper returns unclamped, raw and clamped agree below 1.0.

- `tests/test_settlement_balance_projection.py` (new, 7 tests): canonical shape, modifier clamp `[-20, 10]`, no-terms zero modifier, **3 no-mutation regression tests pinning `world.regions` / `world.diplomatic_states` / `world.vassals` are never touched** (plan line 228), territory-transfer increases recipient share.

**Out of scope (must NOT be invented in this commit):**

- Any C2 endpoint / dialogue / Godot routing (`settlement_preview`, `settlement_confirm`, `incoming_settlement_offer`, mailbox ordering, density modes, `pending_settlement_dialogues`, `ai_settlement_cooldowns`, AI package-construction guard).
- Any partial common-peace ratification path (touches `diplomacy.py` / `diplomatic_templates.py` — Slice D's job).
- Any forced-alliance lifecycle / WPS state-jump / `cleanup_war_end()` extension.
- Any defender-side 5-fixture coverage (Slice C2 needs).
- Any Slice D1/D2 settlement memory / cross-war reaction routing / serial bilateral fallout.
- Any change to the C1a contract (`compute_direct_scores_by_enemy`, `select_direct_score`, `compute_side_pressure_score`, hard stops).
- Any change to the existing 1.0-clamped `calculate_treaty_harshness()` for bilateral callers.
- Any change to `world.threat_level` / `world.coalition_state` substrate (the threat preview is read-only).
- Any change to `world.war_instances` / `world.war_objectives` / `world.war_exhaustion` substrate.

## Authoritative spec / plan / context

Read these in this order before reviewing the code:

1. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` — specifically:
   - **§6.acceptance line 1095-1147** — the canonical formula table including all nine components + acceptance thresholds + `>=50/35-49/<35` band semantics.
   - **§6.acceptance line 1149-1162** — the Pressburg worked example (`+46 / +10 / -11 / 0 / -10 / +15 / -5 / +13 / 0 = 58 acceptable`). Note that the spec total assumes a full-Europe context where projected hegemony hits the 33% band; the synthetic 5-nation seed in WorldState() amplifies band crossings, so the Pressburg fixture asserts components individually + verdict band + score >= 50 rather than total = 58 exactly.
   - **§6.acceptance line 1164** — "at least one decisive French win must accept meaningful common-peace terms without requiring `total_victory`."
   - **§6.acceptance line 1166** — "at least one total-victory package with harsh but legal terms must not be reduced to a hopeless score by stacked downside modifiers alone."
   - **§6.acceptance line 1170** — cross-formula validation: "A package that is accepted as a bilateral peace must not be rejected as an equivalent one-covered-enemy common peace unless the debug output names a common-peace-only component."
   - **§6.acceptance line 1172** — tuning escalation order (one knob per rerun, recorded in `SYSTEMS_REFERENCE.md`).
   - **§6.acceptance line 1174** — war-objective alignment selection chain (leader-vs-accepting → leader-vs-covered → WPS-priority → oldest `created_turn`).
   - **§6.acceptance line 1176-1183** — the 5-WPS-objective table (`conquest`, `subjugation`, `forced_alliance`, `defense`, `liberation`).
   - **§6.acceptance line 1184** — final clamp `[-100, 100]`, integerize at component boundary.
   - **§6.acceptance line 1186** — Britain `NATION_CAPITALS["Britain"] == "Netherlands"` is configured scenario data, NOT a separate identity. Lost-mapped-holdings sub-cap `-10`.
   - **§6.acceptance line 1188-1196** — settlement-tier harshness ceilings table.
   - **§6.acceptance line 1200-1217** — `project_balance_after_settlement(world, war_id, terms)` shape contract + no-mutation requirement + cached helpers only.
   - **§6.acceptance line 1221** — feedback names top 1-2 objectionable components by absolute penalty.
   - **§6.acceptance line 1223-1234** — burdened-participant penalty rule order + aggregate cap.
   - **§6.acceptance line 1273** — forced-alliance threat preview `+15/clause` + crossed coalition thresholds (60/80/90).

2. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` — specifically the **Slice C1** build bullets (lines 217-240). Note that line 217 is the formula constants lock; line 218 mentions the war-exhaustion relevance cap as an opt-in only if exploit fixture forces it; line 219 is the 11+ tuning-gate fixtures requirement; line 220 is monotonicity; line 222 is debug exposure; line 224 is tuning escalation order; line 228 is the `project_balance_after_settlement` no-mutation test requirement; line 229 is the abandoned-by-ally formula; line 260 is the C1: 34-40 focused tests target.

3. `docs/PEACE_DEALS_UMBRELLA_SPEC.md` — cross-slice gating, especially §4.2 (acceptance source of truth — umbrella overrides any drift in sub-specs).

4. `CLAUDE.md` — golden rules. Especially:
   - **Rule 8** (no per-region scans in hot paths). The projection helper walks `world.get_active_nations()` (cached) and `world.get_nation_regions(n)` (cached) — never `world.regions.values()`.
   - **Rule 6** (LLM never affects mechanics). The acceptance helper is fully deterministic.
   - **Rule 4** (state clearing AFTER reading). N/A — C1b is pure (no clears).

5. The C1a foundation file `backend/game_logic/settlement_scoring.py` (top half of the module) and the prior C1a review prompt (if it exists) for context on what's already pinned.

## Files changed (7 files, +3106 / -8)

```
CLAUDE.md                                          ← "Up Next" peace deals bullet updated to reflect C1b landing + 9-vs-8 component note
backend/game_logic/diplomatic_templates.py         ← _accumulate_raw_treaty_harshness extracted + new calculate_raw_treaty_harshness
backend/game_logic/settlement_scoring.py           ← +9 component helpers + project_balance_after_settlement + compute_forced_alliance_threat_preview + calculate_common_peace_acceptance pipeline
docs/STATUS.md                                     ← Last Updated entry for C1b landing
tests/test_common_peace_acceptance.py              ← NEW 57 tests (component pin + 14 tuning-gate fixtures + monotonicity + debug)
tests/test_common_peace_harshness.py               ← NEW 3 raw-vs-clamped harshness tests
tests/test_settlement_balance_projection.py        ← NEW 7 projection + no-mutation regression tests
```

## What to verify (priority-ordered)

### 1 — `calculate_base_side_pressure()` half-away-from-zero rounding

Look at `backend/game_logic/settlement_scoring.py::calculate_base_side_pressure`. Confirm:

- Reuses the C1a `_round_half_away_from_zero` helper (defined earlier in the module). Python's built-in `round()` uses banker's rounding so `round(45.5) = 46` but `round(46.5) = 46` (not 47) — the spec table at line 1153 implies Pressburg `score=70 * 0.65 = 45.5` should round to **46** (matching the worked example). Walk through `_round_half_away_from_zero(45.5)` and confirm it returns 46. The parametrized test `test_base_side_pressure_clamp_and_rounding` includes the `(70, 46)` case AND `(10, 7)` (where `10 * 0.65 = 6.5` → 7).
- Clamp `[-50, 60]`. The parametrized test exercises both bounds (`100 → 60`, `-100 → -50`).
- **Concern:** what if `side_pressure_score` is non-int (float)? The helper does `int(side_pressure_score) * 0.65`, which forces int on the input. Verify this is intentional (side pressure score from C1a is already an int but a future caller might pass a float via debug paths).

### 2 — `calculate_term_harshness_penalty()` 1.5 normalization ceiling

Look at `calculate_term_harshness_penalty`. Confirm:

- Formula: `clipped = min(1.5, max(0.0, raw))`, then `normalized = clipped / 1.5`, then `magnitude = round_half_away(normalized * 45)`, then `penalty = -min(45, magnitude)`. Pressburg case: `raw=0.36 → clipped=0.36 → normalized=0.24 → 0.24*45=10.8 → round_half_away(10.8)=11 → penalty=-min(45,11)=-11`. ✓
- Clamp at `-45`: at `raw=1.5`, the formula gives `-min(45, round(45)) = -45`. Above `1.5`, the clip preserves `-45` (penalty cannot worsen past the ceiling). The parametrized test covers `(1.5, -45)` and `(3.0, -45)`.
- **Concern:** the spec wording at line 1115 reads `-min(45, round((min(raw, 1.5)/1.5) * 45))`. My implementation does the rounding outside the negate. Walk through both interpretations and confirm the result is identical: `round()` is monotonic, the `min(45, ...)` is applied to the magnitude, and the negation flips sign last. There's no edge case where the rounding-vs-negation order changes the answer.
- **Concern:** what if `raw_total_harshness` is `None`? The helper does `max(0.0, float(raw_total_harshness or 0.0))`, which converts None to 0.0. Verify this is intentional (caller must NEVER pass None except for the test fixtures that don't populate it).

### 3 — `calculate_settlement_tier_legitimacy()` tier classification + ceiling mismatch

Look at `calculate_settlement_tier_legitimacy`. Confirm:

- **Tier from existing helper:** Imports `get_settlement_tier` from `backend.game_logic.diplomacy` and keys on `int(side_pressure_score)`. The existing helper takes `abs(war_score)` so negative scores resolve to the same tier as positive; this is intentional per `get_settlement_tier()` itself. Walk through whether common-peace acceptance should ever evaluate a NEGATIVE `side_pressure_score` (proposer is losing). The current implementation just uses `abs()` indirectly — argue whether that's right or whether negative scores should produce a different tier behavior (e.g., always white_peace from the loser's perspective).
- **Base mapping:** `TIER_LEGITIMACY_BASE = {total_victory: 15, harsh_peace: 10, dictated_terms: 5, favorable_terms: 0, white_peace: -10}`. Verify against spec line 1114.
- **Ceiling mapping:** `TIER_HARSHNESS_CEILING = {white_peace: 0.10, favorable_terms: 0.25, dictated_terms: 0.45, harsh_peace: 0.70, total_victory: 1.00}`. Verify against spec line 1188-1196.
- **Strict `>` ceiling check:** `if raw_h > ceiling: mismatch = -10`. Strict greater-than means a package at exactly `harsh_peace` ceiling 0.70 is within tier (no penalty). Spec line 1114 says "exceeds the tier's maximum" — argue that "exceeds" means strictly greater than (otherwise the boundary is unreachable), not ≥. Pressburg case: `raw=0.36 ≤ 0.70`, no mismatch, score=10. ✓
- **White peace + any non-trivial term:** Spec line 1114 says "any non-trivial term exceeds the tier maximum; a zero-term white peace receives only the -10 base." My implementation has a special branch:
  ```python
  if tier == "white_peace":
      if _has_non_trivial_terms(terms_list):
          mismatch = -10
          exceeded_ceiling = True
  ```
  `_has_non_trivial_terms` returns True if any territory term has regions, OR any term type ∈ `{forced_alliance, liberation, vassalage, subjugation}`, OR any term has `amount` / `value`. Walk through whether this matches spec intent. **Concern:** what about a `gold_lump` term with `amount=0`? The helper would return False (the `amount` check is `t.get("amount") or t.get("value")` which is falsy for 0). Verify whether 0-amount terms are realistic in white-peace packages.
- **Clamp [-20, 15]:** raw_score = base + mismatch can be at most `+15` (total_victory base, no mismatch). Can be at most `-20` (white_peace base + mismatch = -10 + -10 = -20). The clamp is technically redundant but defends against future spec changes. Verify the clamp is applied at the end.
- **Test surface:** 5 dedicated tests cover each tier band + the white-peace zero-term case + the white-peace non-trivial case + a ceiling-exceeded case (dictated_terms with raw=0.50 > 0.45 → -5).

### 4 — `calculate_leader_own_losses()` sum-then-clamp invariant

Look at `calculate_leader_own_losses`. Confirm:

- **Sub-component summation order:** All four sub-components are computed independently, summed into `raw_score`, THEN clamped. The `lost_mapped_holdings_subtotal` is INTERNALLY capped at `-10` per spec line 1186 BEFORE summing into raw_score. No other sub-component is internally clamped.
  ```python
  components = {
      "regions_ceded": len(ceded_regions) * LEADER_LOSS_PER_REGION,
      "capital_loss": LEADER_LOSS_CAPITAL if capital_lost else 0,
      "kept_all_bonus": LEADER_KEEPS_ALL_BONUS if keeps_all else 0,
      "lost_mapped_holdings": lost_mapped_holdings_subtotal,  # already capped at -10
  }
  raw_score = sum(components.values())
  score = _clamp(raw_score, LEADER_OWN_LOSSES_CLAMP)  # [-25, 5]
  ```
  The test `test_leader_own_losses_capital_ceded_triggers_penalty` proves Vienna + Bohemia ceded = `-5*2 + -15 = -25 raw → clamped to -25`. The test `test_leader_own_losses_lost_mapped_holdings_capped_at_minus_10` proves three holdings ceded = `-5*3 + -10 (cap) = -25 raw → clamped to -25`. Verify the raw_score is ALSO returned in the debug dict so callers see why the clamp triggered.

- **`capital_lost` detection:** `home_capital = world.get_settlement_home_capital(accepting_leader)`. If `home_capital is None` (e.g., unmapped nation), `capital_lost = False` and the sub-component is 0 — per spec line 1117 "if it returns None, skip the capital-loss subcomponent rather than crashing." Verify the helper short-circuits.
  - Capital is "lost" when `home_capital in ceded_regions OR forced_aligned`. The forced-alliance branch comes from `_accepting_leader_forced_aligned` which returns True when any term has `type == "forced_alliance" AND from_nation == accepting_leader AND to_nation != accepting_leader`. **Concern:** is this the right semantic? Spec line 1117 says "ceded/forced-aligned" without elaborating. My interpretation: forced_alliance against the leader = capital-equivalent sovereignty loss = -15 capital penalty. Argue.

- **`kept_all_bonus`:** Three conditions must all hold:
  - `has_regions_at_eval` — the leader has at least one controlled region.
  - `not cedes_any_owned_region` — no terms cede any of those regions.
  - `not forced_aligned` — no forced-alliance term targets the leader.
  - Zero-region accepting leader: `has_regions_at_eval = False`, bonus = 0 (spec line 1186). Test: `test_leader_own_losses_zero_region_leader_no_bonus`.
  - **Concern:** the third condition is my own addition (spec line 1117 doesn't mention forced_aligned for the keeps_all bonus). Walk through and argue whether forced_alliance against the leader should also disqualify keeps_all bonus. My reasoning: a forced-aligned leader hasn't "kept" full sovereignty even if territory is intact. If the spec author intended forced_aligned to NOT disqualify keeps_all, my implementation over-penalizes by `5` in that case. Note: this is unreachable in well-formed packages (forced_aligned + keeps_all = capital_lost = -15, so the +5 bonus would already be canceled by the -15). Argue whether the explicit guard is fail-safe or over-cautious.

- **`lost_mapped_holdings`:** Caller-supplied snapshot (`accepting_leader_mapped_holdings_at_entry`) since C1b doesn't have access to a war-entry stamp on the war_instance. Spec line 1186: "If the leader had mapped holdings at war entry and the package permanently cedes, forced-aligns, or recognizes the loss of those holdings". My implementation:
  ```python
  if holding in ceded_set:
      lost_mapped_holdings_raw += 1
  elif forced_aligned:
      # Forced alliance over the leader implicitly compromises
      # the holding. Spec line 1186 lists "forced-aligns" as a
      # qualifying loss.
      lost_mapped_holdings_raw += 1
  ```
  **Concern:** the `forced_aligned` branch counts EVERY mapped holding as lost when ANY forced_alliance term targets the leader, even if specific holdings aren't named in the term. Spec line 1186 says "forced-aligns ... those holdings" implying specific holdings. Walk through and argue whether the all-holdings interpretation is too aggressive. Counter-argument: forced_alliance over the leader compromises ALL sovereignty including all holdings. Argue.
  - `lost_mapped_holdings_subtotal = max(LEADER_LOST_MAPPED_HOLDING_CAP, LEADER_LOST_MAPPED_HOLDING_PER * raw)`. The `max()` with negatives gives `max(-10, -15) = -10` — correct cap. Verify `LEADER_LOST_MAPPED_HOLDING_CAP = -10` is the ceiling on the SUB-component (not the whole leader_loss).

### 5 — `calculate_burdened_participant_penalty()` rule order + aggregate cap

Look at `calculate_burdened_participant_penalty`. Confirm:

- **Accepting leader excluded:** `covered = [str(e) for e in covered_enemy_participants if e != accepting_leader]`. Spec line 1125: "do not double-charge the leader as a burdened participant." Test: `test_burdened_participant_penalty_excludes_accepting_leader`.
- **Burden detection:** `_enemy_pays_burden_term(enemy, terms)` returns the list of burden term types where the enemy is `from_nation`. Burden types: `(territory, territory_cede, forced_alliance, liberation, vassalage, subjugation)`. **Concern:** what about `liberation` where the enemy is the freed vassal (`to_nation`)? The helper only checks `from_nation == enemy`, which means a vassal liberation pulls from the OVERLORD (the original `from_nation`). The vassal itself isn't "burdened" by liberation — they're benefitting. Argue whether this is the right semantic.
- **Per-burden rule order:**
  ```python
  if direct_score < 0:
      sub_penalty += BURDEN_PENALTY_NEGATIVE_DIRECT  # -30
  elif direct_score < BURDEN_DIRECT_LOW_THRESHOLD:    # < 20
      sub_penalty += BURDEN_PENALTY_LOW_DIRECT        # -15
  if tier == "major":
      if not capital_occupied AND not term_matches_objective:
          sub_penalty += BURDEN_PENALTY_MAJOR_EXTRA   # -10
  ```
  The major-power -10 STACKS on the direct-score branch (spec line 1229: "add an additional -10"). The test `test_burdened_participant_penalty_major_uncovered_stacks_minus_10` proves a major with `direct_score=30` (>=20, base 0) still gets -10 when capital uncovered + no objective match.
- **Aggregate cap:** `cap = -30 * min(burdened_count, 2)` — `-30` for 1 burdened, `-60` for 2+. `final = max(raw_penalty, cap, BURDEN_PENALTY_AGGREGATE_FLOOR)` with floor `-60`. The `max()` with negatives picks the LEAST negative (closest to 0), which is the right semantic for "cap the penalty at its least painful bound." Test: `test_burdened_participant_penalty_aggregate_cap_neg_60_for_two_plus` proves three burdened enemies with raw=`-70` cap to `-60`.
- **`_capital_occupied_by_proposer_side`:** Reads `world.regions[capital].controller in proposer_set`. **Concern:** what if `world.regions` is None or the capital region is missing? The helper has defensive guards (`if not regions or capital not in regions: return False`). Verify the synthetic test fixtures don't populate `regions` for the synthetic nations like `Bavaria` / `Saxony`, so the helper returns False for those — meaning the major-power exception fires. Test fixture is intentional.
- **`_term_matches_objective`:** Heuristic — checks if any term aligns with the proposer-side objective for that enemy. Walk through the matching rules. **Concern:** the helper is a heuristic, not an exact match. False positives mean the major-power -10 doesn't stack when it should; false negatives mean it stacks when the term DOES match the objective. Walk through whether the heuristic is conservative (favors stacking the -10) or liberal (favors waiving it). Argue.
- **Hard-stop fallthrough:** when `select_direct_score(per_member)` returns None (no active proposer-side war pair), the helper sets `direct_score = -1` and applies the -30 worst-case branch. **Concern:** by the time `calculate_burdened_participant_penalty` runs in the pipeline, the C1a hard-stop has already bubbled up via `compute_side_pressure_score`. So this fallback is unreachable in production. But it's defensive code for direct-test invocation. Argue whether it's fail-safe.

### 6 — `calculate_war_objective_alignment()` selection chain + 5-objective table

Look at `calculate_war_objective_alignment` and `_select_relevant_objective`. Confirm:

- **Selection chain (spec line 1174):**
  1. Side leader's objective vs accepting_leader (primary).
  2. Side leader's objective vs harshest-term target (secondary primary).
  3. Side leader's objective vs other covered enemies in TERM ORDER.
  4. WPS priority order over all proposer participants × covered enemies, then oldest `created_turn`, then alphabetical declarer/target.
- **`harshest_target` heuristic:** Sums per-enemy harshness (territory: 0.3 × regions count, forced_alliance: 0.4, liberation: 0.3, vassalage/subjugation: 0.5). Picks `max(enemy_costs.items(), key=lambda kv: (kv[1], kv[0]))` — highest cost, alphabetical tie-break. **Concern:** the cost weights are local to this helper (not reusing `_accumulate_raw_treaty_harshness`). Walk through whether this is a problem. Counter-argument: the harshest-target heuristic only needs to identify which enemy bears the most package weight; the exact weight doesn't matter, just the relative ranking. Argue.
- **`_objective_at(declarer, target)` filter:** Skips records with `concluded_turn is not None` (already-resolved objectives). Verify against the live `create_war_objective` shape from `backend/game_logic/diplomacy.py:3188`.
- **5-objective table:** Walk through `_classify_objective_alignment` for each type. The spec table at lines 1176-1183 has four columns per type: `+15 satisfies`, `+5 partial`, `-15 unrelated harsh`, `-20 contradicts`. My implementation:
  - `conquest`: territory ceded by target = +15 (or partial); territory returned to target = -20; unrelated harsh on other covered enemies = -15.
  - `subjugation`: vassalage/subjugation OF target = +15; liberation OF target = -20; unrelated harsh = -15.
  - `forced_alliance`: forced_alliance term FROM target = +15; liberation OF target = -20; unrelated harsh = -15.
  - `defense` (special partial detection): walk every term, count restored = `set(restored_regions)`. If `restored == target_regions` = +15. If `restored ⊊ target_regions` AND restored non-empty = +5. If contradicts (defender cedes objective regions) = -20. Else -15 (unrelated harsh) or partial (default).
  - `liberation`: liberation term = +15; vassalage/subjugation TO target = -20; unrelated harsh = -15.
- **Concern:** the conquest branch has a wide "satisfies" condition: ANY territory ceded by target counts. Spec line 1178 says "+15 satisfies = `Objective enemy accepts material territorial, gold, alignment, or military concessions after the proposer controls the target capital / objective region`". My implementation doesn't gate on "after the proposer controls the target capital." That gate would require reading current region controllers, which violates pure-function purity. Walk through and argue whether the implementation is permissive (always grants +15 on any concession) and whether C2 should add the capital-control gate as a precondition before the package even reaches scoring.
- **Concern:** the subjugation branch returns `+15` on `vassalage` OR `forced_alliance` — but spec line 1179 says +5 partial for "lesser dependency." My implementation uses +15 for any matching concession (no partial distinction). Walk through whether the partial vs satisfies distinction in subjugation requires WPS power-cap data (which isn't in C1b scope). Argue whether this is acceptable for C1b ship and a known follow-up for C2.
- **Defense partial detection:** the special-cased loop is correct per spec line 1181 (+15 = ALL restored, +5 = SOME). The test `test_tuning_gate_ai_defender_alignment_not_15` proves a defense objective with `target_regions=["Vienna", "Bohemia"]` and a term restoring only Vienna lands at +5 partial.
- **No-objective fallback:** Spec line 1174 says "score this component as `0` rather than guessing from terms." My implementation returns `score=0, label='no_objective'`. Test: `test_war_objective_alignment_no_live_objective_returns_zero`.

### 7 — `calculate_war_exhaustion_component()` floor division + relevance split

Look at `calculate_war_exhaustion_component`. Confirm:

- **Floor division:** `score = min(20, raw_we // 3)` per spec line 1120 ("intentionally uses floor division while the other common-peace components use round() at their component boundary"). The parametrized test includes `(41, 13)` which distinguishes floor (`41 // 3 = 13`) from `round(41/3) = 14`. Walk through and confirm the helper does NOT use Python's `round()`.
- **Relevance split:** When `covered_enemy_participants` and `war_id` are both supplied, the helper computes:
  ```python
  has_active = any(world.is_at_war(accepting_leader, e) for e in covered)
  if has_active:
      relevant = raw_we
      unrelated = 0
  else:
      relevant = 0
      unrelated = raw_we
  ```
  This is a v0.1 heuristic (spec line 1123 defers the precise definition until the exploit fixture proves a cap is needed). **Concern:** the heuristic is binary (all-or-nothing) — if the leader has ANY active war against ANY covered enemy, ALL exhaustion is treated as relevant. A future cap might want a finer split (e.g., per-pair exhaustion contribution). Argue whether the v0.1 heuristic is good enough for C1b ship.
- **`apply_relevance_cap=False` default:** Per plan line 218, C1b ships with the cap OFF. The exploit fixture (`test_tuning_gate_war_exhaustion_exploit_exposes_inputs`) only verifies the debug exposure, not the cap behavior. **Concern:** the cap is implementable but never tested with `apply_relevance_cap=True` in this commit. Walk through whether the cap formula `min(20, relevant//3 + unrelated//10)` is correct per spec line 1123 (`min(20, relevant_war_exhaustion // 3 + unrelated_war_exhaustion // 10)`). Verify the constants `WAR_EXHAUSTION_DIVISOR=3` / `WAR_EXHAUSTION_UNRELATED_DIVISOR=10` match.
- **Always-on debug exposure:** Spec plan line 222 mandates raw + relevance-split inputs ALWAYS exposed. Verify the debug dict carries `raw_per_nation_exhaustion`, `relevant_exhaustion`, `unrelated_exhaustion`, `applied_relevance_cap` even when the cap is off. Test: `test_debug_exposes_raw_and_relevance_split_exhaustion`.

### 8 — `project_balance_after_settlement()` no-mutation contract

Look at `project_balance_after_settlement` and the `_projected_max_bloc_share` private helper. Confirm:

- **Reads cached helpers only:** `world.get_active_nations()` (per-turn cached), `world.get_nation_regions(n)` (per-turn cached), `world.get_diplomatic_state(n, m)` (read-only), `getattr(world, "vassals", None)` (read-only dict), `world.get_power_tier(n)` (read-only). NEVER iterates `world.regions.values()` (CLAUDE.md golden rule 8). Walk through every read in the helper and confirm.
- **Snapshot construction:** Three local dicts are built — `nation_regions: Dict[str, set]`, `alignments: Dict[Tuple[str, str], str]`, `vassal_of: Dict[str, str]`. Each is populated by **iterating** the cached helpers' return values and **copying** into local mutable structures. NEVER references the live `world.regions` / `world.diplomatic_states` / `world.vassals` dicts after snapshot construction. Walk through and confirm.
- **Term application order:**
  1. Liberation (release vassal). Drops from `vassal_of`.
  2. Forced alliance (set ALLIANCE pair). Updates `alignments`.
  3. Territory transfer. `discard` from old owner's region set, `add` to new owner's. **Concern:** the helper does `nation_regions.setdefault(str(to_n), set()).add(r)` — mutates the local dict, which is fine, but the `setdefault` adds previously-untracked nations to the dict. Walk through whether this could affect the bloc-share computation by counting a nation that wasn't `active` at projection time. Counter-argument: `_projected_max_bloc_share` only iterates `actives`, so the new nation key is harmless.
  4. Vassalage / subjugation. Updates `vassal_of`.
- **`_projected_max_bloc_share` re-runs the live `_identify_max_bloc_share` algorithm** but reads from the snapshot dicts. Walk through:
  - `_power_score_proj(nation)` reads `nation_regions_proj.get(nation, set())` and `world.get_power_tier(nation)` — the live tier is used (tiers don't change with settlement). Verify.
  - `_top_overlord_proj(nation)` walks `vassal_of_proj` with cycle detection. Mirrors the live `_top_overlord` semantics.
  - `_bloc_members_proj(leader)` includes leader + vassal-chain-resolved-to-leader + alliance/defensive_alliance pair partners. Mirrors live `get_bloc_members` semantics.
  - `european_power = sum(_power_score_proj(n) for n in actives)` — projected total.
  - Tie-break: highest share, then highest projected bloc_power, then alphabetical.
- **No-mutation regression tests** (plan line 228): three explicit tests in `tests/test_settlement_balance_projection.py` covering `world.regions`, `world.diplomatic_states`, `world.vassals`. Walk through each — they snapshot the live state, run the projection with concrete terms, and assert the post-projection live state is byte-identical. **Concern:** the regions test compares only `region.controller` (not the full Region object). Walk through whether other Region attributes could be mutated. The projection helper only reads `nation_regions` (which goes through `world.get_nation_regions(n)`), never the Region objects directly. Argue.
- **Modifier bands:** `_share_band(share)` mirrors `coalition.py::_hegemony_signal_band` exactly (`< 0.33 → 0`, `< 0.50 → 1`, `< 0.60 → 2`, else 3). Modifier:
  ```python
  if crossed_band == 60 or deepened_band == 60: -20
  elif crossed_band == 50 or deepened_band == 50: -10
  elif crossed_band == 33 or deepened_band == 33: -5
  elif post_band < pre_band and pre_band > 0: +10  # de-escalation
  else: 0
  ```
  Clamp `[-20, 10]`. **Concern:** the de-escalation branch only fires when `pre_band > 0` — a pre-band of 0 (below 33%) cannot de-escalate further. Walk through and verify this is correct.
- **`crossed_band` vs `deepened_band`:** crossed = pre_band < target_band ≤ post_band. Deepened = pre_band == post_band > 0 AND post_share > pre_share. **Concern:** if both pre and post are in the same band (e.g., both at 35% in band 1) but post_share is HIGHER, deepened_band = 33 and modifier = -5. If pre = 35% and post = 30% (de-escalates from band 1 to band 0), the de-escalation branch fires (+10). Walk through the deepened-band semantic and confirm the spec intent is "package strengthens an existing band" not "package raises share within band."

### 9 — `calculate_common_peace_acceptance()` pipeline composition

Look at the main pipeline composer. Confirm:

- **Hard-stop bubble (early return):** Step 2 runs `compute_side_pressure_score` and checks for hard stops. If present, returns immediately with `score=None, verdict='reject', hard_stops=[...]` without computing components 3-11. Tests `test_acceptance_bubbles_no_covered_enemy_hard_stop` + `test_acceptance_bubbles_no_direct_war_score_hard_stop`.
- **Component computation order** (lines after the hard-stop bubble):
  1. `base_side_pressure` from `side_pressure_score`.
  2. `tier_legitimacy + harshness_penalty` share `raw_total_harshness` — when the caller doesn't supply it, the pipeline computes it via `calculate_raw_treaty_harshness(treaty)` where `treaty["demands"] = list(_iter_terms(settlement_terms))`. **Concern:** the pipeline routes settlement_terms through `treaty["demands"]`, NOT `treaty["clauses"]`. The harshness helper iterates BOTH clauses and demands. Walk through whether all term shapes are recognized via the demands path. Looking at `_accumulate_raw_treaty_harshness`: demands handle `gold_per_turn`, `territory_cede`/`territory`, `ap_per_turn`, `manpower_per_turn`, `gold_lump`, `manpower_*`, `forced_alliance`, `liberation`. Settlement terms are typed `territory`, `territory_cede`, `forced_alliance`, `liberation`, `vassalage`, `subjugation` (the C1b helpers' burden detection). **Critical concern:** `vassalage` and `subjugation` are NOT in the harshness helper's case list. Walk through and confirm: (a) does this matter for C1b accuracy? (b) should `vassalage` map to forced_alliance weight (0.4) or higher? Argue.
  3. `leader_own_losses` — uses caller-supplied `accepting_leader_regions_at_evaluation` and `accepting_leader_mapped_holdings_at_entry` (both default to None / read from world.get_nation_regions when absent).
  4. `burdened_participant_penalty` — uses memoized `direct_scores_map` from C1a + collected `war_objectives_by_enemy`. The collection loop iterates `proposer_participants × covered`, reading `world.war_objectives.get(diplo_key, {}).get(declarer)`. **Concern:** the helper only stores the FIRST non-concluded objective per enemy (via `setdefault`). If multiple proposer-side declarers have objectives against the same covered enemy, only one is captured. Walk through and argue whether this is correct (the burden-penalty helper uses war_objectives only for the major-power exception heuristic, not for the alignment scoring).
  5. `projected_hegemony` from `project_balance_after_settlement`.
  6. `war_objective_alignment` — uses caller-supplied `proposer_side_leader` (defaults to first proposer participant if not supplied). **Concern:** the default-to-first behavior could pick the WRONG leader for a multi-attacker war. The C1a helpers thread `attacker_leader` through `make_synthetic_war_instance` but the C1b acceptance helper reads `proposer_side_leader` as a separate kwarg. The caller (C2) MUST pass the correct leader from the war_instance. Argue whether the default fallback is fail-safe or footgun.
  7. `war_exhaustion` — accepts `apply_war_exhaustion_relevance_cap` flag (default False).
  8. `abandoned_by_ally_acceptance_mod` — uses `current_turn` (defaults to `world.current_turn`).
- **Aggregation:**
  ```python
  components = {
      "base_side_pressure": ...,
      "settlement_tier_legitimacy": ...,
      "term_harshness_penalty": ...,
      "leader_own_losses": ...,
      "burdened_participant_penalty": ...,
      "projected_hegemony_mod": ...,
      "war_objective_alignment": ...,
      "war_exhaustion": ...,
      "abandoned_by_ally_acceptance_mod": ...,
  }
  raw_total = sum(components.values())
  score = _clamp(int(raw_total), ACCEPTANCE_FINAL_CLAMP)  # [-100, 100]
  ```
  Verify all nine components are summed (none accidentally dropped).
- **Verdict bands:** `>= 50` accept, `35-49` near_acceptable, `< 35` reject. Verify the boundary semantics (`>= 50` not `> 50`; `>= 35` not `> 35`).
- **Feedback construction:** Top 1-2 components by absolute negative magnitude. The sort key is `(component_value, component_name)` — most negative first, alphabetical tie-break. Verify the final `feedback` list has at most 2 entries.
- **Forced-alliance threat preview** is computed last and folded into `component_debug["projected_forced_alliance_threat_delta"]` + `["crossed_coalition_thresholds"]` + `["forced_alliance_threat_preview"]`. Walk through and confirm the values surface in the debug dict.

### 10 — `calculate_raw_treaty_harshness()` extraction safety

Look at `backend/game_logic/diplomatic_templates.py`. Confirm:

- **Refactor preserves bilateral behavior:** `calculate_treaty_harshness(treaty)` is now `return min(1.0, _accumulate_raw_treaty_harshness(treaty))`. Walk through whether any bilateral caller path could be affected by the refactor. The shared helper iterates the same clauses + demands as before, with the same weights. The only behavioral change is that the new `calculate_raw_treaty_harshness` returns the unclamped sum.
- **Test surface:** `tests/test_common_peace_harshness.py` has 3 tests — bilateral 1.0-clamped, raw unclamped (1.9 case), agreement below 1.0. **Concern:** there's no test that pins `calculate_treaty_harshness()` is byte-identical to its pre-refactor behavior. The full test suite (9607 passed, was 9538) is the regression net. Walk through whether the existing bilateral test suite (`test_audit*`, `test_diplomacy*`) covers the relevant bilateral acceptance paths.
- **Hidden cost: `_accumulate_raw_treaty_harshness` is now a public function in the module** (not technically private — it's the underscore-prefix convention but Python doesn't enforce). Walk through whether any external caller could accidentally import the underscore-prefixed helper.

### 11 — Tuning-gate fixture coverage (plan line 219)

Walk through `tests/test_common_peace_acceptance.py` Section 3. Plan line 219 lists 11+ required fixtures. My implementation has 14. Walk each:

- **Pressburg-style accepting-leader losses** — `test_tuning_gate_pressburg_worked_example`. Spec line 1149-1162. Asserts components individually + verdict in accept band. **Concern:** the test does NOT assert exact total = 58 because the synthetic 5-nation seed amplifies the projected_hegemony band crossing (the spec example assumes full-Europe context where Austria's regions transferring to France crosses only the 33% band, not 50% in the small fixture). The test asserts `components["projected_hegemony_mod"] <= 0` (any negative or zero) and `score >= ACCEPTANCE_THRESHOLD`. Walk through and argue whether this is acceptable (the spec example is a fixture seed, not a balance target — quote spec line 1164).
- **Tilsit-style non-leader burden** — `test_tuning_gate_tilsit_non_leader_burden`. Asserts burden = -25 (low direct + major uncovered).
- **Coalition split** — `test_tuning_gate_coalition_split_abandoned_mod_boost`. Compares two fixtures; asserts split version has +10 abandoned mod.
- **Decisive victory without total_victory** — `test_tuning_gate_decisive_victory_without_total_victory`. Asserts `tier_legitimacy = +10` (harsh_peace) and verdict accept. Spec line 1164 mandate.
- **Total-victory harsh terms** — `test_tuning_gate_total_victory_harsh_terms_not_hopeless`. Asserts `tier_legitimacy = +15` and verdict NOT below near_acceptable (>= 35). Spec line 1166 mandate.
- **Minor-power limited** — `test_tuning_gate_minor_power_limited_common_peace`. Bavaria-led defenders, asserts base_side_pressure = 20 (`30*0.65 = 19.5 → round_half_away = 20`).
- **Mixed-strength partial-vs-full** — `test_tuning_gate_mixed_strength_partial_vs_full_coverage`. Anti-farming property: full coverage MUST NOT regress from accept to reject. Asserts conditional `if partial verdict == accept, full verdict in (accept, near_acceptable)`.
- **Full-Europe narrow-vs-full-vs-serial** — `test_tuning_gate_full_europe_narrow_vs_full_vs_serial_comparison`. Asserts full common peace `score >= NEAR_ACCEPTANCE_FLOOR` (>= 35) — not strictly dominated by serial. **Concern:** the spec line 247 mandate is stronger ("full common peace is not dominated by serial separate settlements"). My fixture only verifies common peace reaches near_acceptable, not that serial bilateral would reach a HIGHER score. Walk through whether this is sufficient or if the fixture should compare serial vs full quantitatively.
- **6+ participant coalition** — `test_tuning_gate_six_plus_participant_coalition`. Heavily tilted (all war scores at 80). Asserts `base_side_pressure >= 50` and verdict accept.
- **Britain-led defense** — `test_tuning_gate_britain_led_defense_netherlands_home`. Asserts `home_capital == "Netherlands"` and `capital_lost == True` when Netherlands is in the ceded set. Spec line 1186 mandate.
- **Mapped-home/capital cession/restoration** — `test_tuning_gate_mapped_home_capital_holdings_variants`. Three sub-cases (lost, kept, restored).
- **Multi-forced-alliance threat preview** — `test_tuning_gate_multi_forced_alliance_threat_preview`. Asserts `projected_forced_alliance_threat_delta >= 30` and `60 in crossed_coalition_thresholds`. Spec line 1273 mandate.
- **AI-defender alignment ≤ +5** — `test_tuning_gate_ai_defender_alignment_not_15`. Defense objective with 2 target_regions, term restores 1 of 2 → +5 partial. Plan line 227 mandate.
- **War-exhaustion exploit** — `test_tuning_gate_war_exhaustion_exploit_exposes_inputs`. Plan line 218 / spec line 1123. Asserts debug exposes raw + relevance-split + applied_relevance_cap=False (the C1b ship default).

**Concern: tuning escalation order is documented in CLAUDE.md but not yet exercised** by any fixture asserting a constant change. The spec line 1172 escalation is contingency-only — fixtures pass with default constants, so no knob has been moved. Walk through and argue whether this is correct C1b posture (constants locked at default, escalation deferred to C2 stress fixtures).

### 12 — Monotonicity + cross-formula validation (plan line 220, spec line 1170)

Look at Section 4 of `tests/test_common_peace_acceptance.py`. Confirm:

- **`test_monotonic_side_pressure_does_not_worsen_acceptance`** — runs side_pressure ∈ {10, 30, 50, 70} with all other components fixed; asserts each step's score is `>= prev`. Spec line 246 / plan line 220 mandate.
- **`test_one_covered_enemy_common_peace_uses_full_formula`** — asserts the result has all NINE components (proves bilateral shortcut is NOT used). Spec line 1170 cross-formula validation.
- **`test_acceptance_final_score_clamped_to_minus_100_to_100`** — asserts the constants. Spec line 1184.

### 13 — Debug-exposure pin tests (plan line 222)

Look at Section 5 of `tests/test_common_peace_acceptance.py`. Confirm:

- **`test_debug_exposes_all_nine_components`** — asserts `expected_keys.issubset(component_debug.keys())`.
- **`test_debug_names_chosen_objective_diplo_key_and_target`** — asserts the alignment debug names declaring/target/type per spec line 1174.
- **`test_debug_exposes_raw_and_relevance_split_exhaustion`** — pin per plan line 222.
- **`test_debug_exposes_forced_alliance_threat_delta_and_crossed_thresholds`** — pin per spec line 1273.
- **`test_feedback_names_top_two_components_when_rejected`** — pin per spec line 1146 / 1221. **Concern:** the test fixture sets `raw_total_harshness=1.4` and asserts feedback has 1-2 entries with negative values. Walk through whether the fixture reliably produces a near_acceptable / reject verdict (it should, given low side_pressure + heavy harshness + leader losses).

### 14 — Out-of-scope guard

Confirm the commit does NOT modify:

- `backend/main.py` (no new endpoints).
- Any Godot script under `godot-client/` (no Slice C2 wiring).
- `backend/game_logic/diplomacy.py` other than the `from_dict` / `to_dict` paths if any (verify with `git diff`).
- `backend/game_logic/diplomatic_templates.py` callers — only the `calculate_treaty_harshness` refactor + `calculate_raw_treaty_harshness` addition.
- `backend/game_logic/settlement_helpers.py` (no Slice C2 ratification path).
- Any save format change beyond what's already in the spec for Slices A/B (no new persistent state).

Walk through `git diff 993fda8..2cc8b1c -- backend/` and confirm only `settlement_scoring.py` and `diplomatic_templates.py` are touched in `backend/`.

## Test verification commands

After pulling commit `2cc8b1c`:

```bash
# Focused C1b suite — must all pass
.venv/Scripts/python.exe -m pytest tests/test_common_peace_acceptance.py tests/test_common_peace_harshness.py tests/test_settlement_balance_projection.py -v --tb=short

# Component-level smoke (tested independently)
.venv/Scripts/python.exe -c "
from backend.game_logic.settlement_scoring import (
    calculate_base_side_pressure,
    calculate_term_harshness_penalty,
    calculate_settlement_tier_legitimacy,
)
print('base@70:', calculate_base_side_pressure(70)['score'])             # expect 46
print('harshness@0.36:', calculate_term_harshness_penalty(0.36)['score']) # expect -11
print('tier@70+0.36:', calculate_settlement_tier_legitimacy(70, 0.36, [])['score']) # expect +10
print('exhaustion floor: 41//3 =', 41//3, 'rounded would be', round(41/3)) # 13 vs 14
"

# Full Python suite — must be at least 9607 passed
.venv/Scripts/python.exe -m pytest tests/ --tb=short -q

# Ruff
.venv/Scripts/python.exe -m ruff check backend/game_logic/settlement_scoring.py backend/game_logic/diplomatic_templates.py tests/test_common_peace_acceptance.py tests/test_common_peace_harshness.py tests/test_settlement_balance_projection.py
```

## What to flag

Report findings in priority order:

1. **Spec divergence:** any place where the implementation diverges from `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §6.acceptance lines 1095-1273 in a way that would break the Pressburg worked example, the 5-objective alignment table, the burden rule order, the projection helper shape contract, the no-mutation invariant, or the tuning escalation order.
2. **Hidden mutation:** any path through the code that could mutate `world.regions`, `world.diplomatic_states`, `world.vassals`, `world.war_instances`, `world.war_exhaustion`, `world.war_objectives`, or any cache. The projection helper is contractually pure — flag any read that goes through a reference into the live structure rather than a snapshot copy.
3. **Off-by-one:** clamp boundaries (especially `> ceiling` vs `>= ceiling` in tier legitimacy, `< 0` vs `<= 0` in burden rules, `pre_band > 0` in de-escalation), rounding cases (Pressburg `round_half_away(45.5) = 46`, exhaustion `41 // 3 = 13` not 14).
4. **Missing test coverage:** any C1b component or behavior pinned in the spec but not asserted by a test in the three new test files. Specifically: (a) tuning escalation knob assertions (currently unexercised), (b) negative `side_pressure_score` tier behavior (current implementation uses abs via `get_settlement_tier`), (c) full-Europe quantitative serial-vs-full comparison (currently only asserts full reaches near_acceptable).
5. **Performance:** any helper that scans `world.regions.values()` or otherwise violates CLAUDE.md golden rule 8.
6. **Pure-function purity:** any helper that reads from `world` in a way that could leak state across calls (e.g., caching a reference into a mutable dict).
7. **Out-of-scope creep:** any change touching files not listed in the "Files changed" section above.

Be specific. Quote spec line numbers. Quote my code. If you cannot reproduce the Pressburg components or the floor-vs-round war_exhaustion distinction, that is a critical finding.
