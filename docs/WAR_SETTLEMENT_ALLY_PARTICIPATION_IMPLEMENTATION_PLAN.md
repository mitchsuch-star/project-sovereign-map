# War Settlement Ally Participation Implementation Plan

> **Status:** v1.16 READY FOR SLICE A1 FOUNDATION GATE - v1.19 mapped-scope audit hardening applied
> **Last Updated:** April 29, 2026
> **Source spec:** `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.19

This plan is the coding handoff for Imperial Settlement / Ally Participation. It assumes BPH, WPS, and WB are landed and keeps the settlement system additive over pairwise `diplomatic_states`, `war_scores`, and WPS `war_objectives`.

## Scale Rules

- Target 13-20 active nations, 100+ regions, 78-190 bilateral pairs, 20 simultaneous pairwise wars, and cache/index fixtures with 20 active `war_instance` records.
- No settlement slice may add a per-turn scan of all regions for every war.
- Hot paths use active participants, direct term targets, direct beneficiaries, live bargain indexes, and affected regions only.
- Repeated leader-scoped war-instance queries must use a dirty-flag per-turn `war_instances_by_leader` / side-leader cache rather than repeatedly filtering all active instances.
- Repeated participant-scoped war-instance queries, especially cross-war settlement reactions, must use a dirty-flag per-turn `war_instances_by_participant` cache rather than filtering all active instances for each affected nation. Common-peace ratification must mark this cache dirty and rebuild it at most once before cross-war reaction readers run.
- Presentation emits one popup/rail beat per settlement family, not one per participant.
- A `diplo_key` can appear in at most one active `war_instance`; duplicate active instances are a hard stop.
- `war_id` values come from `world.next_war_instance_id`; never derive them from turn number, side names, or `diplo_key`.
- `diplo_key_meta[pair]["pair_status"]` is canonical for `war` / `armistice` / `resolved`; ARMISTICE pairs remain suspended in their existing `war_id` and do not archive the war.
- Cross-war reaction checks evaluate every directly affected active `war_instance`, then bound only secondary adjacency/sphere-only scans to at most three active `war_instances`; never scan all nations by all wars.
- A2/B/D code must use the spec's pair-key convention table: sorted diplomatic pair keys for pairwise state, directional `actor|victim` keys for `betrayal_history`, composite `promiser|beneficiary::target_enemy` keys for War Bargain cooldowns, and `war_id` only as a grouping identity.
- Slice A1 is foundation-only. It must land mapped-nation capital helper safety, settlement containers, old-save defaults, empty index/cache scaffolding, and cache invalidation hooks before any A2 `war_id` threading, B contribution tracking, C common-peace scoring, or D reaction work begins.
- Focused tests must include synthetic full-Europe fixtures because the current map data is still smaller than the target: at least the canonical 13 DG-1 internal nation ids (`France`, `Britain`, `Austria`, `Prussia`, `Russia`, `Spain`, `Ottoman`, `Sweden`, `Naples`, `Bavaria`, `Saxony`, `Portugal`, `Denmark-Norway`), 100+ region ids for territory logic, 20 active `WAR` pair keys, one cache/index fixture with 20 active `war_instance` records, and one 6+ participant side. Build these fixtures in test helpers; do not assume live `NATION_CAPITALS`, `REGIONS_DATA`, or marshal data already contains the full-Europe roster. Display labels such as `Ottoman Empire` or `Naples/Two Sicilies` are aliases, not fixture ids.
- Britain-specific settlement tests must include the live current-map home condition `NATION_CAPITALS["Britain"] == "Netherlands"` and prove it behaves as configured mapped scenario data, not as an off-map settlement identity.
- `compute_local_balance_warning()` is called per participant (6-8 times per preview). Build the term-beneficiary-adjacency map once per settlement evaluation and pass it into each per-nation call. Do not re-derive region adjacency per participant.

### Full-Europe Test Fixture Contract

- Add shared helpers in `tests/helpers/full_europe_settlement_fixtures.py`.
- Synthetic fixtures must define the canonical 13 DG-1 nation roster above, explicit `major / secondary / minor` tiers, 100+ region ids when territory logic is tested, and at least one 6+ participant side.
- A1/A2 cache/index fixtures must create 20 active `war_instance` records directly in the synthetic world state, not merely 20 pair keys, so `war_instances_by_leader` and `war_instances_by_participant` rebuild behavior is tested at target scale.
- Do not expand production `REGIONS_DATA`, `NATION_CAPITALS`, or `STARTING_DIPLOMATS` solely to satisfy settlement tests.
- Tests that need active nations must either attach synthetic regions/controllers to the `WorldState` fixture or monkeypatch the specific active-nation helper under test; they must not rely on the current 5-nation runtime roster.
- Unknown synthetic nations must not silently rely on the `secondary` fallback when a test is asserting standing, side pressure, leader selection, or major-power consultation behavior. Explicit tiers are required.
- Settlement fixtures must not invent off-map identities. Every evaluated participant must exist in the fixture scenario/map data. Missing capital data may be used only in a targeted capital-helper safety fixture, where capital-dependent scoring must skip or warn rather than infer off-map status.
- Full-Europe test fixtures must include synthetic `NATION_DESIRE_PROFILES` entries with non-empty `covets_regions` for all 13 test nations so `rival_strengthened` paths exercise non-trivial data. `compute_local_balance_warning()` must still produce valid results (adjacency and bloc checks) when `covets_regions` is empty.
- Vassal auto-join fixtures must include at least two vassals entering via cascade and prove they receive at most `beneficiary_only` standing unless they independently meet material-contribution thresholds.

## Slice A - War Identity And Grouping

Files:
- `backend/models/world_state.py`
- `backend/game_logic/diplomacy.py`
- `backend/game_logic/war_status.py`
- `backend/game_logic/vassal.py`
- `backend/commands/vassal_executor.py` if the vassal-release rebellion path owns a direct WAR mutation
- `docs/SAVE_FORMAT_REFERENCE.md`
- `tests/test_war_settlement_instances.py`

Build:
- A1 opens with foundation work only. Do not begin live WAR-entry threading, common-peace scoring, contribution accrual, settlement dialogue mutation, or reaction logic until the A1 foundation gate below is green.
- Add a settlement helper API, either in `backend/game_logic/settlement_helpers.py` or an equivalent shared backend helper module, with:
  - `get_settlement_home_capital(world, nation: str) -> Optional[str]` or equivalent `WorldState.get_settlement_home_capital(self, nation) -> Optional[str]`
  The helper returns the configured mapped capital/home region from `NATION_CAPITALS` when present and returns `None` only as a safe fallback for incomplete fixture/scenario data. `None` never means off-map. Capital-dependent scoring must skip or score `0` for the capital-specific subcomponent when the helper returns `None`, and tests should fail/warn when a real mapped major is unexpectedly missing capital data.
- Add `world.next_war_instance_id: int = 1`, `world.war_instances: Dict[str, Dict] = {}`, and `world.archived_war_instances: List[Dict] = []` with save/load defaults.
- Add empty-safe `war_instances_by_leader` and `war_instances_by_participant` lookup/cache helpers plus a single dirty-flag invalidation hook. In A1 these helpers may return empty indexes, but they must establish the API later slices use and must not rebuild more than once per turn phase. Add a synthetic 20-active-`war_instance` cache fixture before closing A1 or as the first A2 cache test so the helper contract is proven beyond empty-state behavior.
- Keep elimination on the current mapped-nation rule before behavioral settlement work starts, but refactor any touched elimination helper to use cached nation-region lookups instead of raw `world.regions.values()` scans. A1 must not add off-map non-elimination behavior.
- Before coding A2/A3, write a durable WAR-entry seam inventory as a tracked checklist in `tests/test_war_settlement_instances.py` named `WAR_ENTRY_SEAMS_UNDER_TEST`. The checklist must include player declaration, AI declaration, coalition declaration, vassal rebellion, vassal-release rebellion, commitment-paradox outcome, scripted/debug war entry, join-opportunity acceptance, counter-bargain acceptance, armistice collapse, and combat-triggered auto-war fallback. The Slice A2 invariant test must fail if a listed seam is missing focused coverage. Map every live seam to either `_process_war_cascade(...)` war-id threading or a direct `attach_pair_to_war_instance(...)` call.
- Split Slice A into mandatory implementation gates:
  - **A1 foundation gate:** mapped capital helper safety, save/load fields, `next_war_instance_id`, empty-safe index/cache helpers, cache invalidation scaffolding, cached elimination helper use where touched, and invariant assertions.
  - **A2 war-entry threading:** cascade/direct-entry `war_id` ownership for every inventoried WAR seam, including vassal and armistice paths.
  - **A3 merge/archive/leader invariants:** connected-component merge, objective preservation, contribution-reference rewrites, leader replacement, elimination exits, terminal retention, and archive compaction.
  Do not start A2 until A1 is green. Do not start A3 merge support until A2 tests prove every direct and cascade-created `WAR` pair owns exactly one active `war_id`.
- Validate side assignment and active-instance compatibility before any declaration mutates `diplomatic_states` to `WAR`. Add `validate_war_declaration(...)` or make `ensure_war_instance_for_pair(...)` perform the pre-commit validation; `war_instance_side_conflict` must hard-stop before state mutation.
- Create a skeleton `war_instance` when a pair enters `WAR` before `_process_war_cascade()`; allocate `war_id = f"war_{world.next_war_instance_id}"`, store `created_sequence`, then increment the counter.
- Implement `ensure_war_instance_for_pair(...)` and call it from every declaration/cascade seam: player/AI declarations, coalition declarations, vassal rebellions, commitment-paradox outcomes, scripted war entry, and combat-triggered auto-war.
- Thread `war_id` through the existing recursive `_process_war_cascade(...)` path. The current function already carries `root_episode_id`, `war_entry_entries`, and `ally_entry_decisions`; add war identity as explicit context rather than deriving ledger ids from `episode_id`, and update all call sites if the parameter count changes.
- Update `backend/game_logic/vassal.py` rebellion handling explicitly: the current path sets `WAR` and then calls `_process_war_cascade(world, vassal_name, lord)` with default cascade context. It must call `ensure_war_instance_for_pair(...)` before the state mutation, pass the allocated `war_id` into cascade, and prove the vassal-rebellion pair is owned by exactly one active `war_instance`.
- Replace the current episode-derived `war_entry_ledger` placeholder shape (`war_{episode_id}`) with the allocated `war_id` and add a regression fixture for same-turn declarations so ledger entries, bargain attachment, and war-instance ownership agree.
- Add direct-entry helpers (`attach_pair_to_war_instance(...)` / `attach_participant_to_war_instance(...)`) for WAR transitions that bypass `_process_war_cascade()`: `resolve_join_opportunity()`, `accept_counter_bargain()`, vassal-release rebellion, armistice collapse, scripted/debug war entry, and combat-triggered auto-war fallbacks.
- Update `_process_armistice_expiration()` so `ARMISTICE -> WAR` reuses the existing `war_id` and sets `diplo_key_meta[pair]["pair_status"] = "war"`, while `ARMISTICE -> PEACE` moves the pair to resolved ownership and sets `pair_status = "resolved"` before any archive/end-condition reader runs.
- Before any treaty path calls `cleanup_war_end()` for a pair, including forced-alliance ratification, snapshot or attach the pair's war-instance data first so battle records, decisive battles, war scores, war-score history, start turns, objective references, and contribution linkage are not lost before archival. Common-peace cleanup must process all covered pairs as one transaction, not expose a partially cleaned multi-pair war to settlement readers.
- Add or extend a per-turn cache for `get_nations_at_war_with(nation)` before settlement call sites start using it repeatedly. Settlement code should not introduce new O(pair_count) scans inside contribution routing, standing classification, or common-peace validation.
- Store pairwise ownership in `active_diplo_keys`, `resolved_diplo_keys`, and `diplo_key_meta`. `objective_keys` remains historical WPS references only.
- Add `diplo_key_meta[pair]["pair_status"] = "war" | "armistice" | "resolved"`. `ARMISTICE -> WAR` reuses the same `war_id`; `ARMISTICE -> PEACE` moves the pair to `resolved_diplo_keys`; common peace never creates ARMISTICE.
- Populate attackers, defenders, active participants, side metadata, and participant episodes as cascade / vassal / ally entry resolves. Side metadata stores `leader_source_by_side`, not a single global `leader_source`; coalition-source scoring on one side must never imply coalition-source scoring for the other side.
- Enforce one-active-`war_instance` per `diplo_key`; reuse compatible instances and merge same-declaration instances rather than creating overlaps.
- Treat a late coalition member, ally, bargain entrant, or vassal joining an existing coalition war as participant/pair attachment to the existing `war_id`. Run merge only when the entrant or new pair is already owned by a different active compatible `war_instance`.
- Implement transitive merge in the spec order: validate side assignments without mutation, choose the oldest surviving `war_id`, merge participant/pair/episode data in memory, choose leaders, rewrite absorbed `war_id` references on war bargains, contribution events, pending settlement dialogues, dispatch routes, and ledger payloads, then atomically replace/remove records and invalidate `war_instances_by_leader` / `war_instances_by_participant` before any reader observes the merged state.
- When attaching a war bargain to a `war_instance`, snapshot `side_at_creation` and `side_leader_at_creation` separately from the current `attacker_leader` / `defender_leader`. Merge rewrites the `war_id`, but leader replacement must not rewrite the original bargain context used by settlement advisory/fulfillment classification.
- Preserve every absorbed instance's WPS objective references as independent objective contexts. A merge must not select one dominant objective; later common-peace scoring picks the relevant proposer-side objective against the covered enemy.
- Rewrite contribution references to the surviving `war_id`, but do not preserve pre-merge contribution percentages as settlement standing. Post-merge standing uses the merged current-episode side denominator.
- Treat transitive merge as a correctness transaction, not a hot path. Full-Europe fixtures should prove correctness for connected-component merges, including multi-objective merges, but no extra optimization is required unless profiling shows repeated merges.
- Store side leaders, participants, `participant_meta`, active episode ids, and re-entry episode ids.
- Persist all `participant_meta` fields needed by later slices, including `contribution_signals_fired`, in `war_instances` serialization so contribution-threshold dispatches do not repeat after save/load.
- Use `war_leader_score()` for non-coalition leader replacement; use coalition leadership scoring only for active coalition-leader wars.
- Add the deterministic `war_leader_score()` tie-break from the spec: preserve the current leader if still eligible, otherwise choose alphabetical stable nation id.
- Add elimination exit: stamp `exited_turn`, freeze contribution, remove from active participants, replace leader if needed, and avoid separate-peace reaction.
- Do not add off-map elimination exemption in A1/A3. Nations absent from scenario/map data are not active settlement participants. Britain follows the normal mapped-nation rules in the current runtime.
- Ended instances get `ended_turn` / `end_reason`, remain queryable for 10 turns, then move to `archived_war_instances`.
- Readers tolerate missing WPS `war_objectives` records for historical `objective_keys`.
- Do not replace pairwise diplomacy. `war_instance` groups existing pairs.
- Add an invariant helper/test assertion: every `diplomatic_states[diplo_key] == "WAR"` must appear in exactly one active `war_instance.active_diplo_keys` with `pair_status == "war"`. No active `war_instance` may claim a non-WAR pair as `pair_status == "war"`.

Gate:
- A1: 10-14 focused tests for old-save defaults, monotonic `war_id` allocation, empty-safe lookup/cache helpers, cache invalidation idempotence, mapped capital helper safety, cached elimination helper use where touched, and invariant assertions.
- A2: 18-22 focused tests for cascade/direct-entry ownership across every inventoried WAR seam, including vassal rebellion and armistice collapse.
- A3: 18-22 focused tests for merge/archive/leader/elimination behavior, including multi-objective merge preservation and post-merge contribution denominator rules.
- Old saves load with `1` for `next_war_instance_id`, `{}` for `war_instances`, and `[]` for `archived_war_instances`.
- Britain fixture proves `get_settlement_home_capital("Britain")` returns the current configured mapped home/spawn region (`Netherlands`) and does not create an off-map settlement identity.
- Missing-capital fixture proves a synthetic mapped nation with no `NATION_CAPITALS` entry does not crash capital-dependent scoring, but also does not become an active off-map participant.
- Empty war-instance index fixtures prove `war_instances_by_leader` and `war_instances_by_participant` build and invalidate safely before any active `war_instance` exists.
- Elimination fixture proves the mapped-nation rule is explicit: a nation with no controlled regions and no vassals exits normally, while absent future nations are ignored rather than evaluated as settlement participants.
- Vassal rebellion and a synthetic three-instance chain merge attach to exactly one surviving `war_instance`.
- Vassal rebellion fixture covers the live `backend/game_logic/vassal.py` call site and proves `ensure_war_instance_for_pair(...)` runs before `_process_war_cascade(...)`.
- Recursive cascade fixture proves honored allies, refused allies, and vassal auto-joins all receive the same allocated `war_id` without relying on the old episode-derived ledger id.
- Direct ally-entry, accepted counter-bargain, vassal-release rebellion, armistice collapse, and scripted/debug war-entry fixtures attach to an existing or new `war_instance`.
- Coalition-declaration fixtures cover every inventoried coalition entry path and prove `ensure_war_instance_for_pair(...)` runs before cascade expansion.
- Invariant test scans live diplomatic state after each Slice A fixture: no dangling WAR pair without a `war_instance`, no duplicate active `diplo_key` ownership.
- ARMISTICE pair-status tests prove suspended pairs do not archive the war and reuse the same `war_id` if hostilities resume.
- Synthetic 13+ nation war-instance fixture covers 20 active pair keys and 6+ participants on one side without relying on live map data.
- Multi-objective merge fixture connects at least two existing wars with different WPS objectives and proves the surviving `war_instance` keeps all objective contexts without selecting one global objective.
- Post-merge contribution fixture proves rewritten contribution records use the surviving `war_id` while advisory standing uses post-merge side totals.
- Side-scoped leader-source fixture proves a coalition-origin attacker with a non-coalition defender, and the inverse case, choose leaders using each side's own source metadata.
- Pairwise war declarations and cleanup still pass existing WPS/WB tests.

## Slice B - Contribution Tracker

Files:
- `backend/models/world_state.py`
- `backend/commands/combat_executor.py`
- `backend/game_logic/diplomacy.py`
- `backend/game_logic/coalition.py`
- `backend/game_logic/dispatch.py`
- `docs/SAVE_FORMAT_REFERENCE.md`
- `tests/test_war_contribution_scores.py`

Build:
- Split Slice B into mandatory implementation gates before coding:
  - **B1 contribution store and standing math:** data model, canonical store, save/load defaults, old-record adapter, current-episode model, standing classification, material-contribution gate, contribution-share query helpers.
  - **B2 event emitters and theater attribution:** battle, occupation, support, treaty-support, British subsidy, sub-1000 battle contribution, `_execute_attack()` inline diplo records, auto-dispatch charge records, and the glorious-charge pipeline fixture.
  - **B3 lifecycle, retention, and full-Europe fixtures:** turn-order/exits, same-turn separate peace, archive compaction, concurrent-war independence, contribution threshold signals, and three-theater / support-only major fixtures.
- Add episode-scoped `world.war_contribution_scores: Dict[str, Dict[str, Dict]] = {}` with `current_episode_id`, `episodes`, and `historical_total`.
- Add theater battle-record emission in `backend/commands/combat_executor.py` through the central `_post_combat_pipeline()` where possible, plus any direct field/garrison/charge paths that bypass it: `battle_region`, `attacker_participants`, `defender_participants`, `nation_theater_strength`, optional casualty-exposure data, and `war_id`.
- Use raw `nation_theater_strength` as the Slice B v1 battle-contribution baseline. If later combat output includes per-nation casualty exposure, it may adjust theater strength, but B2 must not depend on a new per-nation casualty map.
- If the full-Europe map has authored theater/front metadata, include optional `campaign_theater_id` and credit active same-side marshals in that theater. The one-hop adjacency rule remains the baseline; whole-war participant credit remains forbidden.
- Concrete call-site inventory before coding: central path `backend/commands/combat_executor.py::_post_combat_pipeline()` currently calls diplomatic `record_battle()` from the post-combat pipeline, and `_execute_glorious_charge()` already routes through that pipeline. The non-pipeline inventory is `_execute_attack()`'s inline diplomatic `record_battle()` path, which later calls `_post_combat_pipeline(..., skip_diplo_record=True)`, plus the auto-dispatch charge path in `backend/models/world_state.py`. Route those non-pipeline emitters through the same theater-attribution helper or give them equivalent participant/war detection.
- Extend the canonical long-term battle writer `backend/game_logic/diplomacy.py::record_battle()` to store those fields. `WorldState.record_battle()` is only the transient `battles_this_turn` signal path and must not be treated as the contribution source of truth.
- Accrue settlement battle contribution before the existing `record_battle()` 1000-casualty war-score gate returns. Sub-1000-casualty battles stay invisible to pairwise war-score battle records but still produce contribution when they have valid theater participants and `war_id`.
- Add battle attribution adapter using `battle_region`, then `location`, then `region` for old records.
- Accrue battle, occupation, support, and staying-power buckets from events. Battle contribution is stored at battle-resolution time in `war_contribution_scores`; never reconstruct historical settlement contribution by scanning pruned raw `battle_records`.
- Emit and ingest `war_occupation_event` records for enemy region capture, enemy capital capture, allied-region restoration, and liberated-region restoration; attribute occupation contribution by `actor_nation`.
- Contribution readers filter records by the active episode's `joined_turn <= event.turn <= exited_turn` range.
- Enforce event ordering for same-turn exits: battle/occupation/support contribution events are emitted before elimination, separate-peace, or settlement exits stamp `exited_turn`.
- Before coding exit stamping, audit the live `advance_turn()` / diplomacy turn pipeline and document where AI separate-peace, combat, elimination, treaty ratification, and settlement mutation currently run. If the live order can interleave an exit before same-turn battle contribution, refactor or stage events so contribution accrues first.
- Canonicalize contribution episode ids as `{nation_slug}_{war_sequence}_{episode_index}`; `exited_turn` is inclusive.
- On re-entry, create a new episode and leave old episode totals available only for history panels; settlement standing uses the current episode.
- Add `war_support_delivered` event ingestion with dedupe by `episode_id`.
- Existing British coalition subsidy emits one `war_support_delivered` event per turn per recipient with `source="coalition_subsidy"` from `backend/game_logic/coalition.py` advance-turn processing. Because `_process_british_subsidy()` has no `war_id` context today, attribution must rank eligible active wars deterministically: unique eligible war, then matching active coalition target, then highest coalition/war participant overlap, then oldest `created_sequence`; otherwise emit an unattributed logging event that does not accrue contribution.
- Treaty-clause gold / AP / manpower transfers emit `war_support_delivered` at ratification from `WorldState._ratify_treaty()` in `backend/models/world_state.py` with `source="treaty_clause"`; recurring `gold_per_turn`, `ap_per_turn`, and future recurring support clauses emit from `WorldState._process_treaty_clauses()` when each payment is actually applied. Account for current callers in `backend/commands/diplomatic_executor.py` and `backend/game_logic/ai_diplomacy.py`.
- Access/supply support is capped per `(war_id, supporter, support_kind)` across the whole war instance. Re-entry into the same `war_id` does not reset the cap.
- Apply material-contribution gate: staying power alone cannot create seat-level grievance or threshold dispatch.
- Compute standing thresholds from material contribution share, not total contribution share including staying power.
- If total contribution is positive but total material contribution is zero, material shares default to `0` and standing falls back to non-contribution rules; never divide by zero.
- A nation active in two concurrent `war_instance` records accrues staying power, support, and current-episode totals independently per `war_id`; only a merge transaction rewrites those records together.
- Retain `war_contribution_scores[war_id]` while the war is active and through the 10-turn terminal `war_instance` retention window. On archive, compact to final per-nation totals unless a live dialogue, dispatch route, ledger row, campaign-log detail, or settlement memory still references episode detail.

Gate:
- B1: 18-22 focused tests.
- B2: 20-24 focused tests.
- B3: 18-22 focused tests.
- No Slice B sub-gate may exceed the project's observed 50-55 test single-session ceiling; B2 must not start until B1 is green, and B3 must not start until B2 event-emitter coverage is green.
- Contribution accrual does not scan all regions per turn.
- Old battle records with only attacker/defender/location remain valid.
- Raw battle-record pruning does not reduce stored contribution totals.
- Synthetic contribution fixture covers support-only Britain or another major as a low-battle, low-occupation, seat-level major contributor through support/power-tier standing.
- British coalition subsidy fixtures prove `_process_british_subsidy()` emits `war_support_delivered` with `source="coalition_subsidy"` in addition to the existing dispatch/event summary, including a multi-war recipient tie-break and an unattributed/no-accrual fallback.
- Treaty-clause support fixtures prove `WorldState._ratify_treaty()` one-time emission and `WorldState._process_treaty_clauses()` recurring emission accrue support contribution without requiring a nonexistent diplomacy-module ratification hook.
- Sub-1000-casualty minor-power battle fixture proves settlement contribution accrues while pairwise war-score battle records stay unchanged.
- `_execute_attack()` inline-record and auto-dispatch charge fixtures prove non-pipeline battle records emit theater participants and `war_id` for settlement contribution; the glorious-charge fixture proves its pipeline-routed record receives the same fields.
- Three-theater full-Europe fixture proves a 6+ participant war across distant fronts does not create zero contribution for a front's real fighters and does not credit all same-side participants across unrelated fronts.
- Same-turn AI separate-peace plus battle fixture proves the exiting nation keeps that turn's battle contribution before `exited_turn` is stamped.
- Concurrent-war fixture covers one nation active in two `war_instance` records and proves each war's staying-power/support totals advance independently.
- Archive-retention fixture proves contribution totals survive raw battle-record pruning and compact after the terminal retention window.

## Slice C - Common Peace Scoring And Term Legitimacy

Files:
- `backend/main.py`
- `backend/game_logic/diplomacy.py`
- `backend/game_logic/diplomatic_templates.py`
- `godot-client/project-sovereign/scripts/diplomacy_wizard.gd`
- `godot-client/project-sovereign/scripts/war_status_panel.gd`
- `godot-client/project-sovereign/scripts/main.gd`
- New settlement review script/scene if the existing wizard shell cannot host CanvasLayer 50 cleanly
- `tests/test_common_peace_acceptance.py`
- `tests/test_settlement_term_legitimacy.py`

Slice C is mandatory two-part work. Do not combine C1 and C2 in one implementation session unless C1 is already green and the remaining C2 scope is below the session test ceiling.

Build C1 - backend scoring and legitimacy:
- Implement `compute_side_pressure_score(war_instance)`.
- Build and reuse one memoized `direct_scores` map per settlement preview/confirm evaluation; side pressure, direct-score gates, burden penalties, territory-legitimacy `weak_pressure_penalty` checks, and advisory rows must not recalculate the same pairwise war score repeatedly inside one draft preview.
- Implement common-peace acceptance with the current spec constants table, including `base_side_pressure = round(side_pressure_score * 0.65)` clamped to `[-50, 60]` and common-peace harshness normalized over the `1.5` ceiling (`term_harshness_penalty = -min(45, round((min(raw_total_harshness, 1.5) / 1.5) * 45))`). Add `calculate_raw_treaty_harshness(treaty)` in `backend/game_logic/diplomatic_templates.py` or extend the existing helper with an explicit raw / `clamp_max=1.5` option. Existing bilateral callers must keep the current 1.0-clamped `calculate_treaty_harshness()` behavior.
- Implement formula edge cases exactly: sum `leader_own_losses` sub-components before clamping to `[-25, 5]`; `direct_score >= 20` adds `0` burdened-participant penalty for non-leader covered enemies unless another burden rule applies; `war_objective_alignment` includes the `-15` unrelated-harsh-terms-dominates column for all five WPS objective types; and `war_exhaustion` intentionally uses the existing per-nation cumulative `min(20, enemy_leader_war_exhaustion // 3)` rather than per-war partitioning or `round()`.
- Add deterministic Slice C tuning gate fixtures before locking constants: Pressburg-style accepting-leader losses, Tilsit-style non-leader burden, coalition split, decisive French win without total victory, total-victory harsh terms, minor-power limited common peace, mixed-strength partial-vs-full coverage, narrow-vs-full-vs-serial settlement incentive comparison, a heavily tilted 6+ participant coalition war, Britain-led defense using current mapped holdings/home-region scoring, mapped-home/capital cession/restoration cases, a live-code Britain current-map case where `NATION_CAPITALS["Britain"] == "Netherlands"` is treated as configured scenario data rather than off-map identity, a full-Europe harshness calibration fixture for plausible 5-8 region packages, a multi-forced-alliance package that projects `+30` or more threat and names crossed coalition thresholds, and an AI-defender package where the only WPS objective is `defense` and `war_objective_alignment <= +5`. Pin the Pressburg-style worked example from the spec as one fixture seed.
- Add monotonicity coverage proving acceptance does not worsen as `side_pressure_score` increases with all other components fixed.
- Add side-pressure source/dilution coverage: one fixture where the selected `direct_score` for a covered enemy comes from a minor ally while the side leader is losing or weak, and one fixture where many minor covered enemies dilute a strong major-vs-major pressure score. Debug output must name `direct_score_source` for each covered enemy.
- Expose common-peace acceptance debug components in preview/test output: `base_side_pressure`, `term_harshness_penalty`, `leader_own_losses`, `burdened_participant_penalty`, `projected_hegemony_mod`, `projected_forced_alliance_threat_delta`, crossed coalition thresholds, `war_exhaustion`, and `abandoned_by_ally_acceptance_mod`.
- Add final stress coverage for more than three directly affected cross-war reactions firing in one settlement pass, plus a full-pipeline `advance_turn()` fixture with two AI-generated settlements, 20 active wars, and all 13 canonical DG-1 nations.
- If decisive-victory, total-victory harsh-terms, Britain-led defense, narrow/full/serial, mixed-strength partial-vs-full, multi-forced-alliance threat, or AI-defender fixtures fail their design targets, adjust exactly one primary knob from the spec constants list and record the chosen knob in tests and implementation notes.
- Add cross-formula validation tests comparing bilateral acceptance, war-entry score, and common-peace acceptance for monotonic military pressure and equivalent one-covered-enemy package sanity.
- Implement the spec's war-objective alignment mapping table for all five WPS objective types; no live objective record yields component `0`. In merged wars, preserve all proposer-side objective contexts and select the objective relevant to the covered enemy / harshest term; debug output must name selected `diplo_key`, declaring nation, target nation, and objective type.
- AI defender common-peace package construction must not assume `war_objective_alignment == +15`; defensive-objective fixtures must prove packages can be accepted or rejected by the whole formula when objective alignment is `0` or `+5`.
- Implement `project_balance_after_settlement(world, war_id, terms)` as a pure projection helper and use projected post-settlement bloc share for `projected_hegemony_mod`, distinct from bilateral `hegemony_target_mod`. Start from cached nation-region/bloc state such as `get_nation_regions()`, apply term deltas, and never iterate `world.regions.values()` inside preview loops. Add a no-mutation test around world regions, relations, diplomatic states, vassals, and bloc cache state.
- Implement `abandoned_by_ally_acceptance_mod` as `+5` per same-side enemy separate peace in the last 3 turns, capped at `+15`.
- Normalize territory terms to canonical `from` / `to`; accept `from_nation` / `to_nation` only at input boundaries.
- Enforce direct-score gates for burdened non-leader enemies.
- Implement pressure-basis warnings for unoccupied or barely fought regions.
- Support single-covered-enemy common peace when ally-beneficiary terms, standing, or war-level settlement logic is required.
- Support partial common peace: accepted packages resolve covered hostile pairs to PEACE/treaty states only, while uncovered hostile or ARMISTICE pairs remain in the same `war_instance` until the section 7.3 end condition is met.
- If confirm revalidation removes every covered enemy participant because pairs resolved, expired, rebelled, or otherwise changed while the dialogue was open, void the staged settlement with `no_covered_enemy_participants` and no mutation.
- Ratify common peace by iterating `war_instance.active_diplo_keys`: resolve only pairs between proposer-side participants and covered enemy participants, leave all uncovered hostile/suspended pairs untouched, and route forced-alliance outcomes through the existing WPS state-jump path instead of a generic `PEACE` write.
- Parameterize scoring by `proposer_side` so defending-side common peace is symmetric.
- Defender-side coverage must include at least five fixtures: contribution attribution while France is defender leader, standing classification for defender allies, sold-out attacker-side ally reaction, a Pressburg-inverse acceptance example, and defensive-settlement advisory copy.

Build C2 - endpoints, dialogue, advisory, and Godot routing:
- Add Open Settlement eligibility / grey-out rules from spec section 10.3 (`inactive_war_instance`, `not_side_leader`, `no_unresolved_hostile_pairs`, `no_coverable_enemy`, `settlement_dialogue_active`).
- Add settlement endpoint/dialogue contracts: no-terms `GET /diplomatic_preview`, draft-terms `POST /diplomatic_preview`, `settlement_preview`, mandatory hard-stop `settlement_confirm`, typed `POST /respond_to_diplomatic_dialogue` actions for `confirm`, `back_out`, and `revise_terms`, and the exact no-mutation response shapes from the spec.
- Add `incoming_settlement_offer` response contract and dialogue taxonomy entry for AI-to-player common peace: register it as a `CURRENT_TURN_OFFER_TYPES` / mailbox-browseable offer, not a hard stop; actions are `accept`, `reject`, `request_revision`; accept must promote to a `settlement_confirm` hard stop and never mutate directly from the incoming offer payload.
- Settlement dialogues must be serialized. If multiple `settlement_confirm` or `incoming_settlement_offer` payloads would be created while the dialogue queue is at or near cap, keep the later settlement payloads in a settlement-owned pending list or retry next turn rather than dropping them through generic queue overflow.
- Add `DialogueManager.DIALOGUE_PRIORITY["incoming_settlement_offer"]` at the normal incoming-proposal tier and `DialogueManager.MAILBOX_SUMMARY_LABELS["incoming_settlement_offer"] = "Incoming settlement offer"`; cover backend mailbox ordering/activation plus Godot mailbox row rendering. Do not rely on generic proposal ordering or labels for settlement offers.
- Verify the already-registered `settlement_confirm` entries in `DialogueManager.HARD_STOP_TYPES`, backend dialogue priority, Godot dialogue routing, command-response keyword handling, and `tests/test_dialogue_manager.py`; extend behavior rather than re-adding the type.
- `POST /command` may stage common peace terms but must not ratify directly; `confirm` revalidates live leaders, every covered pair's active `war_id` and `pair_status`, proposer-side participant membership, standing inputs, term beneficiaries, beneficiary eligibility, hard stops, and acceptance before mutation. Armistice expiry or same-turn pair resolution returns `active_pair_changed`; proposer-side participant exits/rebellions/eliminations return `active_participant_changed`; beneficiary invalidation returns `beneficiary_ineligible`.
- Void the staged settlement if the proposer-side leader changes; re-score if only the accepting-side leader changes.
- Implement two-pass standing: draft advisory from draft terms, final confirmation standing from locked terms.
- AI-to-player common-peace offers create an incoming settlement-review dialogue; accepting that offer then uses the same confirm executor instead of direct mutation.
- Add AI package-construction guard: AI common peace can surface only after it builds a concrete package that scores `>= 50` through the accepting side's common-peace acceptance formula. Losing-side AI offers must include enough concessions/returns to pass that check or record `package_unacceptable` and stay silent.
- Add AI common-peace anti-spam: one active incoming settlement offer at a time, one new player-facing settlement offer per turn, and a 3-turn per-`war_id` cooldown after reject/request-revision/expiry/live-state void. Store this in a common-peace namespace separate from bilateral proposal cooldowns unless the action also sends a bilateral proposal.
- AI-vs-AI common peace emits one fog-eligible Diplomatic Affairs dispatch line and one `settlement_summary` campaign-log entry, with no participant spam.

Gate:
- C1: 34-40 focused tests.
- C2: 27-32 focused tests.
- Rejection feedback names the top two objectionable components.
- Existing bilateral peace acceptance remains unchanged.
- `settlement_confirm` blocks ordinary commands and handles proposer-leader-change voiding.
- Open Settlement grey-out reasons match the spec enum and non-leaders cannot stage common-peace terms.
- `POST /diplomatic_preview` with draft terms performs no mutation.
- Partial common peace leaves uncovered hostile or ARMISTICE pairs active in the same `war_instance`.
- Common peace cannot create an ARMISTICE pair status.
- Common peace with mixed `territory_cede` and `forced_alliance` terms against one covered enemy ends in the forced-alliance treaty state, not an accidental `PEACE` overwrite.
- Multi-objective merged-war acceptance fixture proves the chosen objective context follows the covered enemy / harshest term selection rule.
- Narrow/full/serial comparison fixture proves full common peace is not dominated by serial separate settlements under the locked tuning constants.
- AI-vs-AI common peace produces one campaign-log summary and one fog-eligible dispatch line.
- AI-to-player common-peace offer tests cover current-turn/mailbox taxonomy, accept/reject/request_revision response shapes, confirm-executor promotion with no mutation on offer accept, and cooldown/one-active-offer gating.
- Mailbox tests prove `incoming_settlement_offer` has its own `DIALOGUE_PRIORITY`, `MAILBOX_SUMMARY_LABELS` entry, and Godot route.
- Confirm-revalidation tests prove an empty covered-enemy set voids with `no_covered_enemy_participants` and no mutation.
- Raw harshness tests prove common-peace scoring uses unclamped `1.5` normalization while landed bilateral callers still receive the 1.0-clamped `calculate_treaty_harshness()` value.
- Formula edge-case tests cover zero material contribution denominators, post-sum `leader_own_losses` clamping, normal non-leader burden as a `0` penalty, the `-15` objective-alignment column, and intentional war-exhaustion floor division.
- Britain current-map home tests prove `NATION_CAPITALS["Britain"] == "Netherlands"` is treated as configured scenario data for the current map and does not create a separate off-map settlement identity.
- Multi-forced-alliance threat-preview tests prove projected `+30` or greater threat and crossed coalition thresholds are visible before confirm.
- AI defender objective-alignment tests prove defensive packages with `war_objective_alignment <= +5` are evaluated by the full common-peace formula.
- AI package-construction tests prove unacceptable losing-side white-peace offers are suppressed before surfacing.
- Cooldown tests prove common-peace per-`war_id` cooldowns do not consume existing bilateral proposal cooldowns.
- Godot smoke after C2: launch the client, open the settlement review from a synthetic payload, confirm `settlement_confirm` blocks ordinary commands, and back out/revise without mutation.

## Slice D1 - Settlement Memories And Direct Reactions

Files:
- `backend/game_logic/diplomacy.py`
- `backend/campaign_log.py`
- `backend/game_logic/coalition.py`
- `backend/models/world_state.py`
- `docs/SAVE_FORMAT_REFERENCE.md`
- `tests/test_settlement_reactions.py`

Build:
- Apply `settlement_shut_out` grievance flags through existing `betrayal_history`.
- Add `settlement_memories` for `settlement_gratitude`, `sold_out_by_war_leader`, and `settlement_context`.
- Add `settlement_gratitude_mod` for eligible later deep-treaty, war-entry, and war-bargain / ally-entry proposals; creating the memory requires `material_contribution_points > 0` in the current episode.
- Apply zero-material major severity reduction: seat/warning remains, full major shut-out grievance requires material contribution or a direct stake.
- Add `sold_out_by_war_leader` posture gating for deep treaties and war-entry asks from the former leader unless redress or high relation exists.
- Add combined posture-gate precedence for `sold_out_by_war_leader`, DG-4 `anti_renewal_cooldown`, hard-reject posture, oathbreaker posture, and state-transition hard stops: list every active blocker in preview/debug, compute effective unblock turn as the max active expiry, and allow concrete redress / relation `>= 50` to bypass only the sold-out gate.
- Add serial bilateral settlement fallout for third-plus separate peaces in one `war_instance` using a rolling five-turn lookback.
- Within the common-peace ratification transaction, run lifecycle in this order: validate confirm, snapshot every covered pair's war-instance data and contribution linkage, ratify terms, mutate ownership/alignment, call `cleanup_war_end()` for covered pairs only after all snapshots exist, run WB-B fulfillment/breach, invalidate `war_instances_by_leader` / `war_instances_by_participant` and hegemony/bloc caches, run settlement and cross-war reactions from fresh indexes, then build dispatch/log/ledger payloads.
- Add canonical acceptance-doc amendments for `settlement_gratitude_mod`: positive `+5`, not part of the clamped political subtotal, cannot bypass hard stops or political floors, refreshes rather than stacks.
- Document combined separate-peace relation impact: BPH-C base penalty plus settlement shut-out penalty, with no duplicate BPH-C application.
- Add settlement-memory cleanup for expired transient records after active modifiers are read; writes are idempotent by `(memory_type, actor, subject, counterparty, war_id, episode_id)`.
- Enforce turn lifecycle placement from spec section 17.5: event-time contribution, war-state mutation, WB-B lifecycle, staying power, leader/end checks, memory reads, memory cleanup, then presentation payloads.

Gate:
- 24-30 focused tests.
- No duplicate BPH-C separate-peace relation penalty.
- `settlement_gratitude_mod` appears in canonical acceptance docs and proposal debug components.
- Gratitude farming fixture proves a zero-material ally beneficiary can receive an immediate relation reward but no reusable `settlement_gratitude_mod`.
- Zero-material major exclusion produces reduced warning/fallout instead of major shut-out grievance.
- Serial bilateral settlement tests cover three or more separate peaces in five turns.
- `sold_out_by_war_leader` posture gate blocks deep asks from the former leader during the memory window unless redress/high relation exists.
- Combined posture-gate fixture proves sold-out and anti-renewal can stack without adding durations, previews both reasons, and rejects redress bypass while `anti_renewal_cooldown` remains active.

## Slice D2 - Bargain Integration And Cross-War Reactions

Files:
- `backend/game_logic/diplomacy.py`
- `backend/campaign_log.py`
- `backend/game_logic/coalition.py`
- `backend/models/world_state.py`
- `docs/SAVE_FORMAT_REFERENCE.md`
- `tests/test_settlement_reactions.py`

Build:
- Wire War Bargain fulfillment/breach through existing WB-B lifecycle helpers.
- Implement `classify_bargain_settlement_status(...)` from spec section 15.2 as a pure function before wiring reactions, then use it for advisory rows and settlement-confirm breach/void routing.
- Treat named-enemy coverage as the boundary between `dormant` and `at_risk`: active attached bargains with covered named enemies and unresolved claims are `at_risk`; bargains whose named enemy is not covered remain `dormant`.
- Treat the bargain as `impossible` when `claim_region` is controlled by a third party outside the covered settlement, by a same-side ally, or by a party from whom no legal term can transfer the claim to France in this package.
- Implement `compute_local_balance_warning()` from live relation/bloc/adjacency/desire-profile data only.
- `rival_strengthened` alone promotes only major/secondary nations to consult; minors need material contribution or direct interests.
- Trigger cross-war reaction checks for every directly affected active war; build `affected_nations` first and early-exit when it is empty, then use `war_instances_by_participant` to union candidate wars and cap only secondary adjacency/sphere-only scans at three affected active wars.
- Add competing ally-claim reactions for same-region awards: recipient gratitude, non-recipient warnings, and grievance/bargain routing only when standing, active bargain, direct stake, or material contribution gates are met.
- Competing-claim warning copy names each claim basis: war bargain, occupation, restoration, former ownership, local sphere, or contribution.
- Cross-war settlement grievance flags feed subsequent bilateral acceptance through the existing `grievance_modifier` path and composite-floor rules; do not add a separate cross-war acceptance modifier.

Gate:
- 28-34 focused tests.
- Balance of Europe beats fire only through existing threshold/hegemon-swap seams.
- Bargain settlement status tests cover `dormant`, `fulfillable`, `fulfilled_by_terms`, `at_risk`, `impossible`, and `breach_if_confirmed`, including the named-enemy-covered vs not-covered boundary.
- Bargain settlement status tests cover third-party and same-side-controller `impossible` cases where no legal package term can transfer the claim region to France.
- Bargain classifier purity test proves advisory/confirmation calls do not mutate bargains, treaties, memories, logs, dispatch, or dialogue queues.
- Cross-war reaction tests prove all directly affected wars are evaluated even when more than three exist, while adjacency/sphere-only scans stay capped at three.
- Cross-war reaction tests prove the implementation uses participant-indexed candidate wars rather than repeated all-active-war filtering.
- Competing-claim warning tests prove every visible claimant row includes the claim basis.

## Slice E - Presentation, Ledger, And Logs

Files:
- `backend/game_logic/dispatch.py`
- `backend/campaign_log.py`
- `backend/game_logic/diplomatic_ledger.py`
- `godot-client/project-sovereign/scripts/war_status_panel.gd`
- `godot-client/project-sovereign/scripts/diplomatic_ledger.gd`
- `godot-client/project-sovereign/scripts/notification_bar.gd`
- `godot-client/project-sovereign/scripts/main.gd`
- `tests/test_settlement_presentation.py`

Build:
- Extend `docs/DIPLOMAT_VOICE_BIBLE.md` with settlement-specific coverage before authoring final copy. Minimum key families: `settlement_advisory_common_peace_*`, `settlement_advisory_defensive_*`, `settlement_acceptance_*`, `settlement_rejection_*`, `settlement_sold_out_by_leader_*`, `settlement_rewarded_ally_*`, and `settlement_excluded_ally_*`.
- Add settlement route metadata separate from commitment routes.
- Implement the `settlement_summary` / `settlement_digest` event contract from spec section 11 Step 6, including payload minimums, one-liners, fog filtering, `event_family="settlement"`, `review_target`, and stable `route_id`.
- Dispatch top four settlement beats plus one digest overflow line.
- Notification rail spotlights only major settlement outcomes.
- Campaign log emits one `settlement_summary` entry per common peace with structured `participant_reactions`.
- Presentation copy must distinguish War Bargain fulfillment from ally-beneficiary rewards: show "Bargain: France secures {claim} (FULFILLED)" separately from "Settlement: {region} awarded to {ally} (REWARD)" when both are involved in one settlement.
- War status panel shows contribution share and standing with top-five default rows plus overflow.
- WARNING and HARD_STOP concerns always surface above the capped standing list.
- Warning rendering follows the spec section 16.3 cap: all hard stops inline, top two warnings inline, info/additional warnings behind "View all concerns."
- Use the deterministic `rank_diplomatic_salience()` tuple from the spec for all default-row ordering. Compute it once per preview/confirm evaluation and pass the ranked rows through the response/UI payload; do not recompute the ordering for every UI refresh.
- Settlement review is a CanvasLayer 50 information-screen surface and must close/hide existing layer-50 screens through the top-bar one-screen-at-a-time rule before opening.
- Settlement review separates Terms, Allies, Warnings, and Acceptance sections using tabs, segmented controls, or collapsible sections; no full-Europe payload should require rendering all participant rows, warnings, bargain rows, and acceptance components in one undifferentiated list.
- Full-Europe settlement review must support scrolling or paginated overflow inside sections; fixed-position label walls are not acceptable for 6-8 participant payloads.
- Advisory rows show projected ally fallout costs and per-term marginal acceptance costs where available.
- Split into E1 backend presentation payloads and E2 Godot rendering if the Godot surface exceeds the slice gate.

Gate:
- 36-44 focused tests.
- Large 6+ participant settlement emits one campaign-log one-liner, not per-participant spam.
- Settlement review CanvasLayer 50 renders top-five rows plus "View all participants" on a synthetic 6+ participant full-Europe payload with no overlapping text.
- Settlement review sectioning smoke verifies Terms, Allies, Warnings, and Acceptance are separately reachable and each section fits without overlapping text on synthetic 6+ participant payloads.
- Defensive-settlement copy smoke includes at least two fixtures proving the copy frames coalition preservation / allied defensive claims rather than imperial overreach.
- Notification buttons route to the settlement review or ledger target specified by backend route metadata.
- `settlement_summary` and `settlement_digest` event tests verify route metadata, fog filtering, one-liner participant cap, and digest overflow.
- Godot surfaces remain usable on both the current 19-region map and a synthetic full-Europe participant payload.
- Manual Godot smoke after E2 verifies settlement review, war status rows, notification route, and ledger route on both current map data and the synthetic full-Europe payload.

## Final Gate

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_war_settlement_foundation.py tests/test_war_settlement_instances.py tests/test_war_contribution_scores.py tests/test_common_peace_acceptance.py tests/test_settlement_term_legitimacy.py tests/test_settlement_reactions.py tests/test_settlement_presentation.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_war_objectives.py tests/test_wb_a_bargain_model.py tests/test_wb_b_lifecycle.py tests/test_wb_c_war_entry.py tests/test_wb_d_presentation.py tests/test_wpsb_power_cap.py tests/test_bph_c_fallout_conflicts.py tests/test_bph_d_ratification_summary.py -q
.\.venv\Scripts\python.exe -m ruff check backend tests
```

Full-suite run is required before merging Slice E because it touches shared diplomacy, campaign log, dispatch, ledger, serialization, and Godot contracts.
