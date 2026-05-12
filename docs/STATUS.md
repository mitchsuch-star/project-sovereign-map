# Ink & Iron: Current Status

> **Updated every session by Claude Code.**
## Active Settlement Gate

**Current gate (May 12, 2026):** `docs/SETTLEMENT_UI_CLEANUP_SPEC.md` v0.27 is **GO-pending-verification** after Codex + Claude follow-up repair session `codex-2026-05-12-settlement-ux-v0.27` on target branch `codex/settlement-smoke-start`. The current docs branch passed the v0.27 version/current-gate scan and parent-doc false-affordance supersession check in this session. The spec contract is binding, but implementation remains blocked until branch-target reconciliation is recorded, the SC-27 scan and v0.27 binding-compatibility table are rerun on the chosen integration/smoke target, executable Godot evidence exists for SC-1 / SC-10b / SC-28, both rejected and losing recovery fixtures are verified, and Gate 4 manual smoke passes.

**Canonical follow-up edits now folded:** rejected-popup substitute CTAs now have an explicit SC-29 timeline and post-SC-29 action ordering; `Ask for terms` cannot ship as a clickable copy-only refusal; attempt-4 stale recovery must run the War Detail actionability probe and terminal-close when War Detail is dead; helper payload schemas, helper ownership, disabled-vs-hidden refusal-code taxonomy, and clause picker schema are normative; `ClauseControlSchema` is the backend source of truth and hidden clause types must not leak as disabled labels; losing-side concession baseline has first-paint visibility, click-time revalidation, no silent overwrite through `re_author_with_concessions`, and still-rejected next-step tests; typed one-to-one common-peace entry is rejected in the executor; `forced_alliance` requires Balance/threat cost differential preview; parent incoming-offer promote-time tests are conditional on explicit SC-5 reversal; parent row-focus language now treats route-id auto-expand as required; Gate 4 requires both `settlement_losing` and `settlement_rejected`; `gold_per_turn`, `vassalage`, `subjugation`, and `liberation` remain interim-hidden until their landing rows close.

## Last Recorded Spec Review Result

**May 12, 2026 Codex + Claude v0.27 follow-up synthesis:** Review session `codex-2026-05-12-settlement-ux-v0.27` re-scored the cleanup spec after folding the latest settlement / peace UX findings and the follow-up repair pass. Scores: Fun 8/10, Clarity 8/10, Work Segmentation 8/10, Contradiction-Freedom 8/10, Completeness 8/10. Verdict: **GO-pending-verification**. No unresolved P0/P1 spec blockers remain after the destructive re-authoring fix, SC-10b/actionability-gated War Detail recovery table, disabled-vs-hidden policy, typed one-to-one rejection, SC-22/pre-smoke evidence reconciliation, post-SC-29 button ordering, concession click-time revalidation, same-war different-scope rejection default, helper ownership table, parent-doc v0.27 alignment, and v0.27 STATUS alignment. Implementation remains blocked on branch reconciliation, executable Godot evidence, chosen-target SC-27 re-scan, v0.27 compatibility verification, pre-smoke verification, and expanded Gate 4 smoke.

## Branch Reconciliation Notes

Settlement UI Cleanup implementation commits exist as referenced objects (`b699f4c`, `4310903` / `0761284`, `052c5d0`, `4884e93`, and `b2a4d7b`), but the current `codex/settlement-smoke-start` branch is a docs/smoke-start repair branch and `b2a4d7b` is not an ancestor of `HEAD`. Do not restart old G2-Slice-1 work from this docs branch; first choose the smoke/integration target where the landed implementation commits are reachable or explicitly record that they must be merged/cherry-picked.

## Manual Smoke Fixture Variants

Before Gate 4 manual settlement UI smoke, set `SOVEREIGN_SMOKE_START=settlement_multilateral` for the shared France vs Britain + Prussia war. Run `SOVEREIGN_SMOKE_START=settlement_losing` for concession-baseline and losing-side authoring paths, and run `SOVEREIGN_SMOKE_START=settlement_rejected` separately for blocked-popup, SC-10b / SC-28 / SC-28b recovery, scoped-draft, no-direct-pair-action, and actionability-gated War Detail paths. Use `SOVEREIGN_SMOKE_START=settlement_multiwar_ambiguity` for the required same-nation multi-war ambiguity check; Gate 4 step 1 cannot close unless smoke evidence names this fixture and records the rendered disambiguation or hidden-action outcome. The losing and rejected fixtures are both required; one cannot stand in for the other.

## Verification Snapshot

Slice G / AI-ally settlement agency remains blocked until the updated v0.27 checks are consumed on the chosen integration/smoke target, both rejected and losing smoke paths pass, SC-29 / SC-30 / SC-31 / SC-32 / SC-33 landing ownership remains tracked rather than open-ended, SC-27 doc scans are rerun on that target, SC-22 Godot evidence is recorded per slice, and SC-10b plus the War Detail actionability helper are proven before `Open War Detail` recovery is treated as a valid blocked-review escape.
> **Previously:** May 5, 2026 (**IMPERIAL SETTLEMENT SLICE F UI WIRING + PRESENTATION IMPLEMENTED** — commit `0b9289e` (`Wire settlement UI routing and presentation`) is on `origin/master`. Slice F now closes the normal-UI common-peace reachability gaps found in the combined Codex/Claude audit: war-detail and coalition `Open Settlement` CTAs preserve `war_id` through Godot -> `/command` -> backend staging; notification/dispatch settlement review routes preserve `route_id` + `war_id` into the diplomatic ledger and focus/expand the matching Recent Settlement row; settlement_confirm now uses the typed `options[]` action schema with `debug_action_ids` instead of legacy player-facing `actions[]`; incoming AI settlement-offer actions (`accept_settlement_offer`, `reject_settlement_offer`, `request_settlement_revision`) are routed and accept rebuilds a fresh live `settlement_confirm` rather than ratifying stale mailbox payload; disabled reasons, acceptance bands/phrases, acceptance components, and awe tags are humanized from backend display maps; the settlement popup is reorganized around comprehension (awe/decision header -> scope/covered enemies -> allies/standing -> acceptance/top pressure -> warnings -> terms); ledger recent-settlement rows use humanized awe displays and route-focused expansion; Godot settlement surfaces were scanned clean for the audited raw enum strings. Verification after implementation: full suite `9761 passed, 1 skipped`; `ruff check backend tests` clean; focused source/contract tests updated for the new routing/action schema. **Next:** run manual in-game smoke for F1 wizard -> Open Settlement -> confirm -> ledger, war-score row -> war detail -> Open Settlement, coalition detail -> whole-war settlement / multi-war explainer, incoming AI offer if feasible, stale-war-state path, and CanvasLayer 50 one-screen routing. After smoke, proceed to Slice G AI/ally settlement agency (AI war-leader packages and non-leader ally petition/advisory pressure, preserving the design call that side leader decides and allies pressure/react).)
> **Previously:** May 5, 2026 (**IMPERIAL SETTLEMENT SLICE F SECOND AUDIT SYNTHESIZED / FINAL UI CLOSURE CONTRACT HARDENED** — common peace must be reachable from the normal diplomacy wizard, not only by typed command. Current audit result: backend command execution for `propose_common_peace` is live, but Godot `diplomacy_wizard.gd::_build_command(...)` has no `open_settlement` mapping, so the wizard can surface `Open Settlement` and then fail with `Unknown diplomatic action: open_settlement`; backend `get_available_diplomatic_actions(...)` checks only existing shared `war_instances`, so default-start `Britain|France = WAR` can show `inactive_war_instance` even though command execution would lazy-backfill a settlement war; wizard display still marks `Open Settlement` as `1 DP` even though opening the C2 dialogue is now free and ratification owns the cost. Also note default-start Britain and Prussia are separate starting WAR pairs, with `Britain|Prussia = ALLIANCE`; lazy backfill of a Britain settlement does not automatically make Prussia part of that settlement unless a real shared war instance/cascade already exists. The combined Codex/Claude Slice F audits are now folded into `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.33 and implementation plan v1.31: one typed settlement dialogue action schema with no legacy player `actions[]`, concrete `reopen_target` stale/revise routing with draft preservation, named settlement result feedback, staging-time stable non-empty `route_id` continuity, wizard/detail entry signatures that preserve `war_id`, war row/detail routing that emits `war_instance_id`, guarded settlement popup fallback, side/outcome-first settlement comprehension with partial/uncovered scopes, pending-envoy/mailbox routing plus backend response handlers for `incoming_settlement_offer`, cross-war settlement collision behavior, player-defender entry coverage, notification route metadata widening, and expanded raw-enum/source-guard tests are all mandatory before smoke. Specs continue to make Slice F mandatory before final smoke and explicitly track post-F Slice G for AI/ally settlement agency: AI war leaders use `incoming_settlement_offer`, while non-leader allies need petition/advisory actions without gaining veto or treaty authorship. `ROADMAP.md` now also inserts a Pre-8.5 Evaluation Gate after settlement closure and before Phase 8.5 so buried war-LLM improvements and diplomacy-refinement items are audited instead of skipped. **Next:** implement Slice F wizard/UI closure from the hardened v1.31 plan. After Slice F/final smoke, take Slice G AI/ally settlement agency; after final settlement gate, run the Pre-8.5 evaluation against `DESIGN_REFINEMENT.md`, LLM war/narration/creative-command notes, the LLM cost/toggle table, and AI agenda/ultimatum/trade/Talleyrand Desk candidates.)
> **Previously:** May 4, 2026 (**IMPERIAL SETTLEMENT D1/D2 REACTION ROUTING + AUDIT FIXES LANDED** — commit `59e2c06` landed D1/D2 settlement and cross-war reaction routing: `ratify_settlement_confirm(...)` now invokes `route_settlement_reactions(...)` after war-instance / bloc / active-nation cache invalidation and before dialogue pop; `backend/game_logic/settlement_reactions.py` owns `settlement_memories`, proposer-side reward / shut-out reactions, enemy-side `sold_out_by_war_leader`, WB-B French-claim breach routing, bounded cross-war scans through `war_instances_by_participant`, `settlement_summary` / `settlement_digest` events, and the `settlement_gratitude_mod` acceptance hook. Follow-up commit `5a9614d` closed the audit findings: expired gratitude no longer applies, cross-war affected nations are no longer widened to all proposer-side members, WB-B breach routing is limited to French promiser claims, and the invalidation-ordering test observes the fresh participant index inside the reaction call before dialogue pop. Verification: `tests/test_settlement_reactions_d1_d2.py` **`33 passed`**; full suite **`9671 passed, 1 skipped`**; `ruff check backend tests` clean. **D1/D2 re-audit verdict:** GO. **Next:** Slice E presentation, ledger, and logs — backend presentation payloads, settlement review / war status panel rows, Talleyrand voice copy, advisory warning rendering, notification/ledger routes, campaign-log/dispatch surfacing, and Godot smoke per `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Slice E. After E, there is no Slice F in the plan; proceed to the Final Gate.)
> **Previously:** May 4, 2026 (**IMPERIAL SETTLEMENT C2 RATIFICATION REVIEW FIXES LANDED** — common-peace ratification now covers the audit blockers on commit `f9af6f2`: vassalage/subjugation terms are pair-planned and applied through existing vassal helpers so the affected pair resolves with final `VASSAL`; forced-alliance plus territory packages transfer territory once and keep the final pair state at `ALLIANCE`; per-pair treaty records now write to `active_treaties` / `previous_treaties` using the bilateral treaty shape; pre-cleanup snapshots are proposer-pair-perspective instead of France-only while preserving legacy `french_casualties` keys; territory cessions mirror bilateral elimination guard / allied-region-restored contribution accrual; liberation mirrors bilateral liberated-region-restored contribution accrual. `tests/test_common_peace_c2_ratification.py` now has 19 tests, including forced-alliance+territory, subjugation from WAR and ARMISTICE, non-France proposer snapshot, and contribution side-effect regressions. Verification: focused C2 preview+ratification **`26 passed`**; full suite **`9634 passed, 1 skipped`**; `ruff check backend tests` clean. **C2 re-audit verdict:** GO. **Next:** D1/D2 reactions remain the next implementation slice.)
> **Previously:** May 3, 2026 (**IMPERIAL SETTLEMENT C2 RATIFICATION MUTATION LANDED** — `settlement_confirm.confirm` now ratifies live state per spec §10.5 / §11 / §11.1 instead of returning `ratification_deferred`. New surface in `backend/game_logic/settlement_preview.py`: `ratify_settlement_confirm(world, dialogue)` runs the full mutation transaction with helpers `_build_pair_ratification_plan(...)` (per-pair target_state computation; `ALLIANCE` only when a `forced_alliance` term has `from=covered_enemy` AND `to=proposer_member` of THAT pair; otherwise `PEACE`; ARMISTICE pairs travel through the same path), `_capture_pre_cleanup_snapshots(...)` (per-pair `war_duration` / `war_score` / French / enemy casualties via `_capture_pre_cleanup_war_data` BEFORE any cleanup, per spec §11 line 1239), `_apply_settlement_terms(...)` (package-level: territory cessions transfer regions + invalidate active-nation cache + accrue / reduce coalition threat for France-side cessions; gold lumps clamp to payer balance with same-side recipient credit; liberation calls `release_vassal(reduce_threat_on_release=False)`, sets `DEFENSIVE_ALLIANCE` between liberator and freed vassal, applies `-20` / `+30` relations, reduces threat when France was the lord, logs `vassal_liberated`), and `_resolve_pair_state_transitions(...)` (per pair: WAR/ARMISTICE → `set_diplomatic_state(PEACE)` → `cleanup_war_end(conclude_objectives=True)` so the bilateral peace closure path runs — `resolve_pair_to_resolved` moves the pair from `active_diplo_keys` to `resolved_diplo_keys`, stamps `pair_status="resolved"` / `resolved_turn`, closes contribution episodes, and stamps `ended_turn` / `end_reason="all_pairs_resolved"` only when no hostile pairs remain; for `ALLIANCE`-target pairs the helper then re-sets `set_diplomatic_state(ALLIANCE, "common_peace_forced_alliance")`, resets relation to 0, stamps `alliance_origins[pair] = "forced"`, adds the covered enemy to `continental_system_members` (default-on per the bilateral forced-alliance pattern unless `includes_continental_system=False`), generates `+15` coalition threat ONLY when the imposer is `world.player_nation`, and logs `forced_alliance_imposed`). Cache invalidation per spec §11 line 1239: `invalidate_war_instance_indexes()` + `invalidate_bloc_members_cache()` + `invalidate_active_nations_cache()` BEFORE any reaction reader. The `confirm_settlement` dialogue action in `handle_settlement_dialogue_action` now calls `ratify_settlement_confirm(...)` instead of returning `ratification_deferred`. **Settlement and cross-war reaction routing (D1/D2) is intentionally NOT wired** in this slice — the returned summary exposes `resolved_pairs`, `applied_clauses`, and `pre_cleanup_snapshots` so the next slice can route them. Failed `revalidate_staged_settlement` (proposer leader change, inactive war instance, active-pair mid-flight change), inactive war instance after staging, or unresolvable plan (empty cross-side coverage) all return `mutated=False`, pop the dialogue, and surface the appropriate error. Test surface: 14 new tests in `tests/test_common_peace_c2_ratification.py` covering full-settlement war-end, partial settlement keeping uncovered pairs active and non-ended, ARMISTICE pair → PEACE clearing armistice tracking + cooldown, territory transfer applied once with cache invalidation, gold-lump clamp to payer balance, forced-alliance pair ending in `ALLIANCE` with origin / Continental System / `+15` threat / `forced_alliance_imposed` event AND `Austria|Saxony` (a non-imposer proposer-side pair) still going to PEACE per spec §10.5 line 1038, war-score / war-start clear ONLY for resolved pairs, per-pair pre-cleanup snapshot data, war-instance index post-mutation correctness (Austria deindexed from `war_1`, France/Prussia still indexed via uncovered pair), dialogue pop on success, three guard cases (`proposer_leader_changed`, `inactive_war_instance`, `active_pair_changed`) all mutating nothing, and liberation freeing a vassal + creating `DEFENSIVE_ALLIANCE` with the liberator + emitting `vassal_liberated`. Verification: full suite **`9629 passed, 1 skipped`** (was `9615`); `ruff check backend/ tests/` clean. **Next:** D1/D2 reactions — settlement-side ally / enemy-leader / Europe-at-large reaction routing reading the `resolved_pairs` + `applied_clauses` + `pre_cleanup_snapshots` summary plus war-instance fresh indexes; cross-war reaction scan bounded by `affected_nations` per spec §11.5 line 1241; settlement memories / grievance flag writes through the existing `grievance_modifier` path per spec line 1245; settlement_summary / settlement_digest dispatch + campaign log + ledger payloads per §11.6.)
> **Previously:** May 3, 2026 (**IMPERIAL SETTLEMENT C1b REVIEW FIX + C2 PREVIEW FOUNDATION LANDED** — follow-up commit `963adaa` fixed common-peace dependency harshness: raw treaty harshness now scores `vassalage` / `subjugation` demands at `0.5` each, so C1b `term_harshness_penalty` and tier-ceiling mismatch no longer under-score dependency packages; `tests/test_common_peace_harshness.py::test_raw_helper_scores_dependency_demands` pins the regression. Commit `cda009b` lands the first Slice C2 backend foundation without ratification mutation: new `backend/game_logic/settlement_preview.py` provides Open Settlement eligibility (`inactive_war_instance`, `not_side_leader`, `no_unresolved_hostile_pairs`, `no_coverable_enemy`, `settlement_dialogue_active`), non-mutating `build_settlement_preview(...)` over the C1b acceptance formula, `stage_settlement_confirm(...)`, and `settlement_confirm` dialogue handling for `back_out`, `revise_terms`, and confirm-time live revalidation. `/diplomatic_preview` now supports `GET ?mode=settlement&war_id=...` for no-terms war-scoped preview and `POST {"mode":"settlement", ...}` for draft terms; both are preview-only and return `mutated=False`. `get_available_diplomatic_actions()` now exposes `Open Settlement` in WAR state with deterministic eligibility/grey-out payload and normal DP gating. `WorldState` now has C2 save/load defaults for `pending_settlement_dialogues: []` and `ai_settlement_cooldowns: {}`. `settlement_confirm.confirm` currently validates and returns `ratification_deferred` without changing diplomatic state; actual common-peace ratification/reaction mutation remains the next slice. Verification for C2 foundation: full suite **`9615 passed, 1 skipped`**; ruff clean on touched files.)
> **Previously:** May 3, 2026 (**IMPERIAL SETTLEMENT SLICE C1b COMMON-PEACE ACCEPTANCE FORMULA LANDED** — the C1b sub-gate of `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §6.acceptance lines 1095-1147 closed. New pipeline `calculate_common_peace_acceptance(world, *, war_id, war_instance, proposer_side, accepting_side, accepting_leader, covered_enemy_participants, settlement_terms, ...)` in `backend/game_logic/settlement_scoring.py` ships the spec **nine-component table** (CLAUDE.md "Up Next" listed eight components but the spec's Pressburg worked example at line 1162 totals 58 only when all nine — including `settlement_tier_legitimacy` at line 1099 — are summed; verified by `test_tuning_gate_pressburg_worked_example` reproducing components `+46 / +10 / -11 / 0 / -10 / +15 / -5..-10 / +13 / 0`). C1b is pure (no mutation, no ratification, no live wiring into `diplomacy.py` / `diplomatic_templates.py` yet). Verification: full suite **`9607 passed, 1 skipped`**; ruff clean on every C1b-touched file.)
> **Previously:** May 3, 2026 (**IMPERIAL SETTLEMENT SLICE C1a SIDE-PRESSURE FOUNDATION LANDED** - the first sub-gate of Slice C / `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §6.3. New module `backend/game_logic/settlement_scoring.py` exports the pure helpers consumed by common-peace acceptance, direct-score gates, territory legitimacy `weak_pressure_penalty` checks, and advisory rows: `compute_direct_scores_by_enemy(world, war_instance, *, proposer_side, covered_enemy_participants)` builds the `{enemy: {side_member: war_score}}` map filtered by `world.is_at_war(...)` so ARMISTICE / PEACE / non-WAR pairs are excluded; `select_direct_score(per_member)` picks `max()` with deterministic alphabetical tie-break and names the chosen `direct_score_source` per spec line 243; `compute_side_pressure_score(...)` returns the spec §6.3 power-weighted average (`{"major": 3, "secondary": 2, "minor": 1}` with `DEFAULT_POWER_TIER = "secondary"` fallback for unauthored nations), uses traditional half-away-from-zero `round()` so the Pressburg worked example (line 1153) reproduces exactly, clamps to `[-100, 100]` per spec line 239, and accepts a caller-supplied memoized `direct_scores` map per spec line 238 so settlement preview / confirm walks war scores at most once per `(war_id, proposer_side, covered_enemy_participants, current_turn, draft_terms_hash)`. Hard stops surfaced: `no_covered_enemy_participants` (empty covered set) and `no_direct_war_score_for_covered_enemy` (per-enemy when no proposer-side member is at war with that enemy). 16 C1a tests in `tests/test_settlement_side_pressure.py`: empty-cover hard stop, per-enemy no-pair hard stop, `direct_scores` built before `max()`, alphabetical tie-break, ARMISTICE pairs excluded, power-tier weights + `secondary` fallback, Pressburg worked example with `round()` not floor, post-aggregate clamp to range, defender-side symmetry, mixed-strength minor-dilution, minor-ally-outshines-leader source attribution, monotonicity in direct score, caller-supplied memoization trust contract, PEACE separate-peaced ally exclusion, deterministic covered-enemy debug ordering, invalid `proposer_side` raises ValueError. Verification: full suite `9538 passed, 1 skipped` (up from 9522); ruff clean. **C1a is foundation-only — no acceptance formula, no tuning constants, no live wiring into `diplomacy.py` or `diplomatic_templates.py` yet.** **Next:** C1b acceptance formula (`base_side_pressure = round(side_pressure_score * 0.65)` clamped `[-50, 60]`, `term_harshness_penalty` over raw 1.5, leader-own-loss clamp, burdened-participant penalty, projected-hegemony / forced-alliance threat, war-objective alignment for all 5 WPS objectives, war exhaustion, abandoned-by-ally) plus the 11+ tuning-gate fixtures and tuning escalation order.)
> **Previously:** May 3, 2026 (**IMPERIAL SETTLEMENT SLICE B3 REVIEW FIX LANDED / SLICE C HANDOFF READY** - follow-up commit `be93a32` closes the debug diplomacy lifecycle seam found in B3 review. `backend/commands/meta_executor.py` now runs lifecycle cleanup when debug `set_diplo_state` leaves WAR/ARMISTICE: WAR to PEACE resolves the owned pair and closes contribution episodes; WAR to ARMISTICE marks the pair `armistice` while preserving open episodes. `tests/test_war_settlement_instances.py` adds regressions for debug WAR to PEACE and WAR to ARMISTICE. Verification: focused settlement/B3 suite `228 passed`; full Python suite `9522 passed, 1 skipped`; `ruff check backend tests` clean. **Next:** Slice C - common-peace term legitimacy, settlement standing readers, and dispatch / ledger / paradox routing consuming B3 contribution lifecycle data.)
> **Previously:** May 3, 2026 (**IMPERIAL SETTLEMENT SLICE B3 LIFECYCLE LANDED** - the B3 sub-gate of `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §7.5 / §9.2 line 612 / §9.5 line 178 closed. `backend/game_logic/war_contribution.py` adds `STAYING_POWER_PER_TURN = 5` / `STAYING_POWER_TURN_CAP = 10` / `STAYING_POWER_RAW_CAP = 50` constants, `accrue_staying_power_for_war(world, war_id, *, current_turn)` (per-war walker, idempotent per `(war_id, nation, current_turn)` via `last_staying_power_turn` + `staying_power_credited_turns` counters on each episode), `accrue_staying_power_all_wars(world, *, current_turn)` (active war_instance walker — skips `ended_turn`-stamped instances), and `compact_war_contribution_for_archive(world, war_id, *, archived_turn)` (drops episode detail, sums per-bucket finals + episode_count + first_joined/last_exited turns, moves to the new `world.archived_war_contribution_scores` container). `backend/game_logic/settlement_helpers.py` adds idempotent `_open_contribution_episode_for_participant(...)` / `_close_contribution_episode_for_participant(...)` and wires them into every WAR-entry / exit seam: `_create_skeleton_instance` opens episodes for originator + origin target; `attach_pair_to_war_instance` opens at the CURRENT attach turn so re-entered participants get fresh episode_ids per spec §7.5; `attach_participant_to_war_instance` opens at the same turn; `mark_participant_eliminated_in_all_wars` closes episodes per spec §7.4 line 453; `resolve_pair_to_resolved` exits participants whose last active pair just resolved (separate-peace exit) AND closes every still-active participant when `end_reason="all_pairs_resolved"` stamps (war-end exit). `cleanup_war_end(conclude_objectives=True)` (the PEACE outcome path in `backend/game_logic/diplomacy.py`) calls `resolve_pair_to_resolved(...)` so player- and AI-driven peace ratifications close episodes through the same path armistice expiration already used (idempotent against the existing `_process_armistice_expiration` call). `archive_terminal_war_instances(...)` calls `compact_war_contribution_for_archive(...)` for every archived war_id once it has cleared the 10-turn retention window. Per-turn staying-power is wired as step 7b in `process_diplomacy_turn` BEFORE the armistice expiration step so episodes about to close on this turn still capture the turn's credit under the inclusive `event.turn <= exited_turn` boundary (spec §9.5 line 740). `WorldState` adds `archived_war_contribution_scores: Dict[str, Dict[str, Any]]` with save/load round-trip and pre-B3 default `{}`. New fixtures in `tests/helpers/full_europe_settlement_fixtures.py`: `build_three_theater_full_europe_fixture` (9-participant Coalition spanning German + Iberian + Russian theaters), `build_concurrent_war_lifecycle_fixture` (Russia bridges two independent wars), `build_archive_retention_fixture` (terminal France-vs-Austria war with controllable `ended_turn` / `current_turn` for boundary tests). 27 new B3 tests in `tests/test_war_contribution_scores.py` (144 total in file, was 117): staying-power per-turn (`+5`), 10-turn / 50-raw cap, same-turn idempotency, closed-episode skip, ended-war-instance skip, all-wars walker; open-episode wiring at every attach seam (skeleton, pair, participant, idempotent re-attach, post-exit re-entry); close-episode wiring at every exit seam (elimination, separate-peace participant exit, all-pairs-resolved war-end, cleanup_war_end PEACE, cleanup_war_end ARMISTICE no-op); same-turn separate-peace battle-credit ordering; per-turn staying-power same-turn ordering; concurrent-war independence (staying-power, exit isolation); three-theater distant-front exclusion; archive retention boundary at 9 turns (no compact) / 10 turns (compact) / multiple-episodes-per-nation compaction / save-load round trip / no-op when no contribution record. Verification: full suite `9520 passed, 1 skipped`; ruff clean. **Next:** Slice C/D presentation surface — common-peace term legitimacy, settlement standing readers, dispatch / ledger / paradox routing consuming the new lifecycle data.)
> **Previously:** May 3, 2026 (**IMPERIAL SETTLEMENT SLICE B2 NON-BATTLE REVIEW FIXES LANDED** - treaty support attribution now emits only for AP actually removed from the payer, so AP floor clamps no longer create support contribution without payment. One-time and recurring treaty-clause support event ids include the source clause index, so duplicate same-type clauses accrue separately while same-turn replays remain idempotent. Added regressions for duplicate `gold_lump`, duplicate `gold_per_turn`, and AP-floor blocked payment. Verification: full suite `9493 passed, 1 skipped`; ruff clean. **Next:** B3 lifecycle / per-turn staying-power / war-entry seam wiring of `open_episode` / `close_episode_for_exit` / archive compaction / retention / full-Europe fixtures.)
> **Previously:** May 2, 2026 (**IMPERIAL SETTLEMENT SLICE B2 RECORD_BATTLE ORDERING GUARD LANDED** - the B2 sub-gate that pins settlement contribution accrual position before the B2 emitter wiring expands to all combat call sites. `backend/game_logic/war_contribution.py` adds `accrue_battle_contribution(world, *, attacker_nation, defender_nation, winner_nation, attacker_casualties, defender_casualties, location, war_id, attacker_participants, defender_participants, nation_theater_strength, turn)` — the canonical battle-bucket accrual entrypoint per spec §9.2 / §9.4. Resolves `war_id` via `world.get_war_instances_by_participant()` (cached) when omitted, validates side membership (no-op if both nations land on same side), uses `adapt_legacy_battle_record(...)` to fill theater defaults so legacy single-attacker/single-defender callers work without theater data, and accrues `episode["battle"]` + `episode["total"]` distributed by `nation_theater_strength` share with the spec §9.4 line 622 floor-of-1 for participants with non-positive strength. `_battle_side_raw(inflicted_casualties, suffered_casualties, decisive_win)` implements the spec §9.2 formula (`inflicted // 100 + suffered // 250 + decisive * 25`); `_is_decisive_battle` mirrors the war-score decisive criterion (ratio > 2:1 AND total > 10,000). No per-war decisive cap on the settlement side because the episode boundary already bounds it. `backend/game_logic/diplomacy.py::record_battle()` now calls `accrue_battle_contribution(...)` AFTER the `is_at_war` precondition but BEFORE the 1000-casualty war-score early return, so sub-1000 battles still accrue settlement contribution per spec §9.4 line 713. 8 new B2 ordering-guard tests in `tests/test_war_contribution_scores.py` (63 total in file): source-order assertion via `inspect.getsource` proving the accrue call appears before the gate, behavioral sub-1000 fixture proving accrual happens with empty `battle_records`, regression test proving above-1000 battles still produce both records, and 4 function-safety tests (no-op when no active war_instance, no-op same-side, skip participants without active episode, theater-strength distribution when explicit). Verification: full suite `9439 passed, 1 skipped` (up from 9431); ruff clean. **B2 emitter call-site wiring is the next sub-gate** — theater-aware updates to `_post_combat_pipeline()` / `_execute_attack()` inline path / auto-dispatch charge path / glorious-charge pipeline, plus occupation events, treaty-clause / British-subsidy support events, and one-hop adjacency participant detection.)
> **Previously:** May 2, 2026 (**IMPERIAL SETTLEMENT A3 REVIEW FIXES + SLICE B SPEC CLEANUP LANDED** - commit `d5bcefc` fixed A3 cascade merge retargeting and event-log / ledger absorbed-`war_id` rewrites. `merge_war_instances(...)` now rewrites nested `war_id` fields in event-log / ledger payloads, and `assert_war_instance_invariants(..., context="post_merge")` checks those fields. `_process_war_cascade(...)` now refreshes `CascadeContext.war_id` after a cascade attach retargets to a merge survivor. Verification: focused settlement suite `82 passed`, full suite `9376 passed, 1 skipped`, ruff clean. Follow-up doc cleanup marks `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.27 and implementation plan v1.24 ready for Slice B1, with B1 scoped to contribution store/current-episode math/material-share helpers and pure contribution-derived standing inputs only; common-peace term legitimacy, War Bargain settlement classification, and Slice C/D reactions remain out of B1.)
> **Previously:** May 2, 2026 (**IMPERIAL SETTLEMENT SLICE A3 MERGE/ARCHIVE/LEADER INVARIANTS LANDED** - Slice A3 of `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §7.4 / §7.5 / §7.6 closed. New surface in `backend/game_logic/settlement_helpers.py`: `merge_war_instances(world, *, candidate_war_ids, ctx=None)` runs the full transitive merge transaction (compute connected component → validate sides without mutation → pick oldest `war_id` by `created_sequence` → fold participant/pair/episode data → side-scoped leader replacement → rewrite absorbed `war_id` references on `diplomatic_commitments` + `pending_dispatch_events` → no-op-safe rewrite hooks for absent `war_contribution_scores` / `pending_settlement_dialogues` / `settlement_route_payloads` → atomic swap → invalidate indexes → always-on `assert_war_instance_invariants(..., context="post_merge")`); `war_leader_score(world, nation, *, war_id, side)` settlement-specific scorer (power tier × 30/15/5 + Slice B contribution defaulted to 0 + ally/consult/beneficiary bumps); `_choose_leader_for_side` side-scoped chooser (coalition source delegates to `coalition.select_coalition_leader`, non-coalition uses `war_leader_score`, tie-break preserves current leader if eligible else alphabetical); `mark_participant_eliminated_in_all_wars` (stamps `participant_meta[nation].exited_turn` + `exit_path="eliminated"` per spec line 452, no separate-peace reaction); `archive_terminal_war_instances` (10-turn retention then move to `archived_war_instances`). Live wiring: `validate_war_declaration` returns `merge_required=True` advisory instead of hard-stop; `ensure_war_instance_for_pair` runs merge then re-validates; `attach_pair_to_war_instance` triggers merge when pair owned by different active instance and retargets `war_id` to survivor; `create_war_bargain_commitment` snapshots `war_id` / `side_at_creation` / `side_leader_at_creation` per spec §11.3 line 1573 (rewritten on merge but `side_*` preserved); `_eliminate_nation` calls `mark_participant_eliminated_in_all_wars` BEFORE diplomatic-state teardown; `_advance_turn_internal` calls `archive_terminal_war_instances` once per turn after the idempotency guard; `resolve_pair_to_resolved` stamps `ended_turn` + `end_reason="all_pairs_resolved"` when last active pair resolves. `assert_war_instance_invariants(world, *, context="post_merge")` extended with no-op-safe walks over `diplomatic_commitments`, `pending_dispatch_events`, optional Slice B/C containers (`war_contribution_scores`, `pending_settlement_dialogues`, `settlement_route_payloads`), and rejects any `war_id` that does not resolve to active or archived state. Test surface: 23 new A3 tests in `tests/test_war_settlement_merge.py` (merge core, multi-objective preservation, bargain merge context, leader replacement / `war_leader_score`, elimination exit, terminal retention + archive at `ARCHIVE_RETENTION_TURNS=10` boundary, post-merge invariants + no-op-safe Slice B/C); 3 new fixtures in `tests/helpers/full_europe_settlement_fixtures.py` (`build_three_instance_chain_merge_fixture`, `build_multi_objective_merge_fixture`, `build_side_scoped_leader_source_fixture`); 4 A2 hard-stop tests migrated in `tests/test_war_settlement_instances.py` (true `side_conflict` cases stay; cross-instance attach now triggers merge). Full suite green at `9373 passed, 1 skipped`; ruff clean. **Slice B contribution tracker is the next gate.**)
> **Previously:** May 2, 2026 (**IMPERIAL SETTLEMENT A2 REVIEW FIXES LANDED / A3 SPEC READY** - follow-up commit `497791d` closed the A2 hard-stop review findings: cascade attach failures now block before WAR mutation, debug `set_diplo_state WAR` allocates ownership, armistice WAR resumption honors `ensure_war_instance_for_pair(...)` failures, counter-bargain WAR validation happens before bargain side effects, and duplicate pair ownership now returns merge-required. Verification: full pytest suite `9350 passed, 1 skipped`; `ruff check backend/ tests/` clean. Spec/plan/status are aligned for Slice A3: connected-component merge, absorbed-reference rewrites against current containers plus no-op-safe future hooks, leader replacement, elimination exits, terminal retention/archive compaction, and always-on post-merge invariants.)
> **Previously:** May 1, 2026 (**IMPERIAL SETTLEMENT SLICE A2 WAR-ENTRY THREADING LANDED** - every WAR seam now allocates / reuses a `war_instance` per `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.24 §7.2 / §7.3 and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.21 Slice A "A2 war-entry threading" bullets. Landed in `backend/game_logic/settlement_helpers.py`: `CascadeContext` dataclass (avoids pushing `_process_war_cascade()` past nine positional args), pre-commit `validate_war_declaration(...)` (`war_instance_side_conflict` + `war_instance_merge_required` hard-stops), `ensure_war_instance_for_pair(...)` (skeleton allocation, pair / participant reuse, ARMISTICE → WAR resumption that reuses the same `war_id`), narrower `attach_pair_to_war_instance(...)` / `attach_participant_to_war_instance(...)` direct-entry helpers, and pair-status transitions via `mark_pair_armistice(...)` / `resolve_pair_to_resolved(...)`. Live wiring: `declare_war(...)` validates + allocates the `war_id` BEFORE `set_diplomatic_state(..., "WAR", ...)` and replaces the legacy episode-derived `war_{episode_id}` ledger placeholder with the real allocated id; `_process_war_cascade(...)` accepts `ctx: CascadeContext` and attaches every defensive / offensive / vassal cascade pair to the root war's `war_id`; `backend/game_logic/vassal.py` `check_vassal_rebellion(...)` and `release_vassal(rebellion=True)` now allocate / reuse a `war_instance` before mutating diplomatic_states; `resolve_join_opportunity(..., "accept")`, `accept_counter_bargain(...)`, and `_process_armistice_expiration(...)` (both ARMISTICE → WAR reuse and ARMISTICE → PEACE pair-resolved transition) thread through `ensure_war_instance_for_pair(...)`. Test surface: 31 new A2 tests in `tests/test_war_settlement_instances.py` (48 total settlement tests including A1 foundation file) covering the durable `WAR_ENTRY_SEAMS_UNDER_TEST` checklist (player/AI/coalition/scripted declaration, vassal rebellion + vassal-release rebellion, paradox outcome routed through `declare_war`, join-opportunity accept, counter-bargain accept, armistice collapse, combat-triggered auto-war, defensive/offensive/vassal cascade attach), plus `war_instance_side_conflict` and `war_instance_merge_required` hard-stop guards, concurrent-war independence, recursive-cascade single-`war_id` proof, full combined cascade + vassal fixture invariant pass, and CascadeContext legacy-kwarg propagation. Full pytest suite green at 9342 passed (1 skipped); ruff clean. **A3 connected-component merge / archive / leader replacement remains the next gate** — A2 hard-stops on merge required so A3 can swap the diagnostic for the merge transaction.)
> **Previously:** May 1, 2026 (**IMPERIAL SETTLEMENT SLICE A1 FOUNDATION GATE LANDED** - foundation-only scaffolding for Imperial Settlement / Ally Participation per `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.24 §0/§7 and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.21 Slice A "A1 foundation gate" bullets. Landed: `WorldState.next_war_instance_id`/`war_instances`/`archived_war_instances` containers with save/load defaults of `1`/`{}`/`[]`; empty-safe `get_war_instances_by_leader()` + `get_war_instances_by_participant()` with single dirty-flag `invalidate_war_instance_indexes()` hook + lazy rebuild; the touched `_is_nation_eliminated` helper refactored from raw `world.regions.values()` scan onto cached `get_nation_regions(...)`; new `backend/game_logic/settlement_helpers.py` module exporting `assert_war_instance_invariants(world, *, context=...)` covering pair-ownership uniqueness, side disjointness, and `pair_status`/`diplomatic_states` agreement (`WarInstanceInvariantError` for downstream load-repair tooling). Test surface: 13 new foundation tests added to `tests/test_war_settlement_foundation.py` (17 total — 4 pre-A1 + 13 A1) including a synthetic full-Europe 20-active-`war_instance` fixture covering the canonical 13 DG-1 nation roster + 6+ participant coalition side, cache-invalidation idempotence proof, post-merge invariant pass + bad-fixture failure cases, and an explicit Britain-Netherlands mapped-rule fixture. Shared fixtures live in `tests/helpers/full_europe_settlement_fixtures.py` per the Full-Europe Test Fixture Contract. `SAVE_FORMAT_REFERENCE.md` documents the three new fields. Full pytest suite green at 9311 passed; ruff clean. **A1 strictly foundation-only — no behavioral settlement work shipped.** A2 war-entry threading is the next gate.)
> **Previously:** May 1, 2026 (**IMPERIAL SETTLEMENT SPEC v1.24 FUTURE-AUDIT HARDENING READY** - `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.24 and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.21 are aligned for Slice A1 foundation coding and future full-Europe expansion. A1 remains mapped-nation-only: it starts with capital helper safety, settlement containers, old-save defaults, empty index/cache scaffolding, cache invalidation hooks, and a 20-`war_instance` cache/index proof before A1 closes. v1.24 keeps the v1.23 gates and additionally defines forced-alliance common-peace pair lifecycle, hardens the full-Europe narrow/full/serial incentive gate, adds compact/medium/verbose settlement-review fallbacks, adds AI-defender viability and war-exhaustion exploit fixtures, documents `settlement_gratitude_mod` intent, and gives Slice E explicit awe set-piece targets.)
> **Previously:** April 30, 2026 (**IMPERIAL SETTLEMENT SPEC v1.23 REVIEW SHARPENING READY** - `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.23 and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.20 are aligned for Slice A1 foundation coding and future full-Europe expansion. A1 remains mapped-nation-only: it starts with capital helper safety, settlement containers, old-save defaults, empty index/cache scaffolding, cache invalidation hooks, and a 20-`war_instance` cache/index proof before A1 closes. Future nations such as Russia enter settlement one by one through `docs/ADDING_CONTENT.md` plus a focused settlement readiness fixture, not through settlement-specific hard-coding; synthetic fixtures must extend the active roster before adding future-nation regions/controllers. v1.23 adds pre-A2 `CascadeContext` guidance, a B2 `record_battle()` ordering guard, concrete `request_revision` cooldown/no-counter-loop semantics, a spec-naive pre-D1 settlement-review comprehension gate, a stronger narrow/full/serial tuning commitment, and D2 profiling for 5+ directly affected cross-war reactions.)
> **Previously:** April 30, 2026 (**IMPERIAL SETTLEMENT SPEC v1.22 SYNTHESIS HARDENING READY** - `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.22 and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.19 are aligned for Slice A1 foundation coding and future full-Europe expansion. A1 remains mapped-nation-only: it starts with capital helper safety, settlement containers, old-save defaults, empty index/cache scaffolding, cache invalidation hooks, and a 20-`war_instance` cache/index proof before A1 closes. Future nations such as Russia enter settlement one by one through `docs/ADDING_CONTENT.md` plus a focused settlement readiness fixture, not through settlement-specific hard-coding; synthetic fixtures must extend the active roster before adding future-nation regions/controllers. v1.22 adds explicit common-peace tuning escalation for the narrow/full/serial risk, a manual 4+ participant settlement-review comprehension gate before D1, and always-on post-merge war-instance invariant assertions in A3.)
> **Previously:** April 29, 2026 (**IMPERIAL SETTLEMENT SPEC v1.21 MAPPED-FOUNDATION READY** - `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.21 and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.18 are aligned for Slice A1 foundation coding and future full-Europe expansion. A1 remains mapped-nation-only: it starts with capital helper safety, settlement containers, old-save defaults, empty index/cache scaffolding, cache invalidation hooks, and a 20-`war_instance` cache/index proof before A1 closes. Future nations such as Russia enter settlement one by one through `docs/ADDING_CONTENT.md` plus a focused settlement readiness fixture, not through settlement-specific hard-coding; synthetic fixtures must extend the active roster before adding future-nation regions/controllers. C2 now owns serialized settlement cooldowns and deterministic dialogue-overflow retry storage.)
> **Previously:** April 29, 2026 (**IMPERIAL SETTLEMENT SPEC v1.20 FUTURE-NATION ONBOARDING READY** - `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.20 and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.17 are aligned for Slice A1 foundation coding and future full-Europe expansion. A1 remains mapped-nation-only: it starts with capital helper safety, settlement containers, old-save defaults, empty index/cache scaffolding, and cache invalidation hooks. Future nations such as Russia enter settlement one by one through `docs/ADDING_CONTENT.md` plus a focused settlement readiness fixture, not through settlement-specific hard-coding.)
> **Previously:** April 29, 2026 (**IMPERIAL SETTLEMENT SPEC v1.17 PRE-A1 FOUNDATION GATE READY** - `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.17 and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.14 are aligned for Slice A1 foundation coding after Codex/Claude reconciliation. Closure hardening pinned A1 to mapped-capital helper APIs, settlement containers, old-save defaults, empty index/cache scaffolding, and normal mapped-nation elimination behavior before any A2 `war_id` threading, B contribution tracking, C common-peace scoring, or D reaction work; superseded by v1.18 mapped-nation simplification.)
> **Previously:** April 29, 2026 (**IMPERIAL SETTLEMENT SPEC v1.16 FULL-EUROPE AUDIT SYNTHESIS READY** - `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.16 and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` v1.13 are aligned for Slice A1 after the Run 3 / cross-audit synthesis. Closure hardening now owns side-scoped leader-source metadata, mapped-nation elimination behavior, proposer-side participant and beneficiary confirm revalidation, material-share zero guards, corrected combat call-site inventory, per-war-instance access/supply caps, cache invalidation timing, canonical full-Europe fixture ids, and final stress fixtures.)
> **Previously:** April 29, 2026 (**IMPERIAL SETTLEMENT SPEC v1.13 FULL-EUROPE AUDIT RECONCILIATION READY** - `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` are aligned for Slice A1 coding after the latest Codex/Claude full-Europe synthesis. Closure hardening now preserves per-originator objectives through merges, uses post-merge contribution denominators, makes common-peace pair/state resolution explicit, requires `war_instances_by_participant`, adds narrow/full/serial common-peace incentive fixtures, requires AI package-acceptance construction, adds three-theater and same-turn exit ordering tests, splits Slice A gates, expands Britain fixtures, tightens WB impossible classification, and names defensive/settlement Voice Bible families.)
> **Previously:** April 29, 2026 (**IMPERIAL SETTLEMENT SPEC v1.12 CLAUDE RECONCILIATION CLOSURE READY** - `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` are aligned for Slice A coding after reconciling the latest Claude formula/integration audit. Closure hardening now locks common-peace base pressure at `0.65` / `[-50, 60]`, expands common-peace harshness normalization to raw `1.5`, adds five-objective alignment mapping, requires a Britain-led defense tuning fixture, gates reusable `settlement_gratitude` on material contribution, inventories non-pipeline battle call sites, flags `vassal.py` and armistice expiration `war_id` threading, adds turn-lifecycle bloc-cache invalidation, and updates CLAUDE routing to the active settlement handoff.)
> **Previously:** April 29, 2026 (**IMPERIAL SETTLEMENT SPEC v1.11 AUDIT SYNTHESIS CLOSURE READY** - `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` are aligned for Slice A coding after Codex/Claude follow-up synthesis. Closure hardening now explicitly separates settlement contribution from the 1000-casualty war-score gate, scales burdened-participant caps for full-Europe sellouts, starts Pressburg tuning at `0.65`, expands defender-side fixtures, adds serial separate-peace fallout, cross-validates acceptance formulas, reduces zero-material major severity, emits recurring treaty support from `_process_treaty_clauses()`, revalidates pair status with `active_pair_changed`, fixes mapped-home leader-loss scoring, documents projected-hegemony floor asymmetry, gives `sold_out_by_war_leader` a posture consequence, names competing-claim bases, splits Slice D into D1/D2, and adds settlement-specific Voice Bible coverage.)
> **Previously:** April 28, 2026 (**IMPERIAL SETTLEMENT SPEC v1.10 FULL-EUROPE SYNTHESIS CLOSURE READY** - `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` are aligned for Slice A coding after the Codex/Claude full-map audit synthesis. Closure hardening now fixes defender-side war-leader relation anchoring, documents no-congress/no-neutral-mediation scope, expands Slice C tuning fixtures for mixed-strength partial-vs-full coverage and total-victory harsh terms, exposes common-peace debug components, evaluates all directly affected cross-war reactions, routes settlement grievances through the existing `grievance_modifier` path, adds competing ally-claim rules, makes the bargain settlement classifier explicitly pure, and requires sectioned settlement review UI.)
> **Previously:** April 28, 2026 (**IMPERIAL SETTLEMENT SPEC v1.7 FINAL AUDIT CLOSURE READY** - `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` are aligned for Slice A coding after the combined Codex/Claude full-Europe audit and final synthesis fixes. Closure hardening now includes the live War Bargain acceptance formula in `DIPLOMACY_SPEC.md`, explicit partial common-peace continuation, draft `POST /diplomatic_preview`, event-time contribution vs battle-record pruning, same-turn lifecycle ordering, transitive merge transaction order, absent-major shut-out precedence, AI-to-player settlement review routing, expanded Slice C tuning/monotonicity fixtures, synthetic full-Europe tests, Slice C split guidance, and Godot smoke gates.)
> **Previously:** April 28, 2026 (**IMPERIAL SETTLEMENT SPEC v1.6 AUDIT CLOSURE READY** - `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` are aligned for Slice A coding after the combined Codex/Claude full-Europe audit. Closure hardening adds hard-stop `settlement_confirm` taxonomy, leader-change revalidation/voiding, normalized common-peace harshness math, two-pass standing, zero-contribution major-power precedence, transitive war-instance merge with absorbed-`war_id` rewrites, explicit WAR-entry seams, occupation contribution events, support-emitter ownership, `projected_hegemony_mod`, bounded cross-war reaction scans, deterministic advisory salience, CanvasLayer 50 ownership, idempotent settlement memories, AI internal confirm routing, and canonical `settlement_gratitude_mod` acceptance-doc amendments.)
> **Previously:** April 28, 2026 (**IMPERIAL SETTLEMENT SPEC v1.5 HANDOFF READY** - `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` are aligned for Slice A coding. Handoff hardening adds unique war-instance ID allocation, active pair-key ownership separate from WPS `objective_keys`, episode-scoped contribution storage, mandatory `settlement_confirm`, `settlement_gratitude_mod`, AI common-peace decision rules, a common-peace acceptance tuning gate, concrete Godot/file ownership, and a Britain coastal-income scale fix using authored `is_coastal` metadata.)
> **Previously:** April 28, 2026 (**PEACE DEALS FULL-EUROPE HARDENING COMPLETE** - War-score territory scoring no longer scans all regions per active war; national-power checks use live ownership indexes, per-turn cache, and authored `is_coastal` region/province metadata; terminal war bargains archive out of the hot commitment store after 10 turns with live promiser indexes for breach detection; Ally Participation spec advanced to v1.3 for 100+ regions with exact common-peace constants, canonical `from` / `to` term ownership, live `location` battle compatibility, support-event schema, campaign-log aggregation, and a new implementation plan.)
> **Previously:** April 28, 2026 (**ALLY PARTICIPATION SPEC FULL-EUROPE SYNTHESIS** — `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` revised to v1.2 for 13-20 nations, 50+ regions, multiple simultaneous wars, and 6-8 participant coalitions. Added the top-level scale/ownership contract, rival-strengthened local-balance warnings, secondary co-belligerent standing floor, theater-level battle attribution, late-joiner rules, salience-filtered advisory, rejection diagnostics, cross-war reaction checks, reaction digest caps, material sold-out threshold, live grievance-flag signature, settlement-memory serialization ownership, and an expanded ~200-test implementation sequence. Coding remains gated on the implementation plan, but the design gaps from the full-Europe audit are owned in the spec.)
> **Last Updated:** April 27, 2026 (**WAR BARGAINS LEDGER TAB WIRED** — Gate 2 smoke test (`tools/gate2_smoke_test.py`) built and passed 59/59 checks covering all 11 Gate 2 criteria. Identified missing Godot surface: diplomatic ledger had no 5th tab for war bargains despite backend sending `war_bargains` data. Fix: added `BargainsTab` button to `diplomatic_ledger.tscn`, wired `bargains_tab` @onready ref + KEY_5 input + tab index 4 + `open_to_war_bargains()` method + `_render_war_bargains()` renderer (live/completed split, status colors, badge display, cooldown) in `diplomatic_ledger.gd`, and added `ledger_war_bargains` review-target routing in `top_bar.gd::open_diplomatic_ledger_review()`. Notification "View Bargains" button now opens the correct tab.)
> **Last Updated:** April 27, 2026 (**WB-D AUDIT FOLLOW-UP COMPLETE** — Codex audit gaps closed for War Bargain presentation: live void reasons now have committed period-copy phrases, player-facing counterparty-breach label no longer uses modern/legalistic "counterparty" wording, and war-bargain ledger `created_turn` fields are `int()`-wrapped for Godot payload safety. `tests/test_wb_d_presentation.py` expanded to 37 tests. Verification: focused WB-D suite `37 passed`; full suite `9280 passed, 1 skipped`; `ruff check backend tests` green. **War Bargains track COMPLETE (WB-A through WB-D).**)
> **Last Updated:** April 27, 2026 (**WB-D COMPLETE** — War Bargain presentation extension. 5 bargain event types added to `COMMITMENTS_ROUTES` (fulfilled/breached/voided/ratified/triggered) with icons, labels, voiced Talleyrand/diplomat templates, and speaker assignments. Witness scope classification upgraded: `_get_bargain_witnesses()` now returns scope-classified list via `_classify_witness_scope()` with dominant scope propagated to dispatch/notification. Terminal bargain states (fulfilled/breached/voided) emit persistent notifications via `_emit_bargain_notification()`. Breach events include scope-branched witness aside (ally/rival/shared_enemy/region_observer). Counterparty breach route override (NORMAL priority, Talleyrand speaker). Response route for French breach: `review_target="diplomacy_wizard"` + `review_label="Propose Redress"`. Ledger extended via `get_all_bargains_for_ledger()` to show completed bargains with badge field (honoured/broken/lapsed). Codex audit prompt at `tools/codex_audit_wb_d.md`. 29 new tests in `tests/test_wb_d_presentation.py`. Verification: full suite `9272 passed, 1 skipped`; ruff green. **War Bargains track COMPLETE (WB-A through WB-D).**)
> **Last Updated:** April 27, 2026 (**WB-C AUDIT FOLLOW-UP COMPLETE** — War-entry integration now uses the WB-C ally-entry review before declarations instead of silently auto-cascading offensive allies; accepted/rejected/backed-out review choices feed the declaration transaction and trigger matching bargains. Directional betrayal checks are pinned to `_betrayal_key(actor=breaker, victim=beneficiary)`, including hard-reject posture and Bargain Review forecasting. Counter-bargain reroll memory now hashes the material score inputs, accepted counter-bargains emit `bargain_ratified` and `bargain_triggered`, and legacy force-declare dialogues recover by selecting an available war objective. Bargain Review is wired into `proposal_confirm`, AI bargain gates honor WB-C hard blocks, `repudiate_bargain` costs 1 AP after confirmation, campaign-log WB-C event types are formatted, and save-format docs match the serialized WB-C fields. `tests/test_wb_c_war_entry.py` now has 63 tests. Verification: full suite `9243 passed, 1 skipped`; `ruff check backend tests` green. **Next: WB-D.**)
> **Last Updated:** April 27, 2026 (**WB-B AUDIT FOLLOW-UP COMPLETE** — War Bargain lifecycle is now wired through production treaty-break, downgrade, and ratification paths instead of helper-only paths. France-caused source treaty loss, named-enemy peace/armistice, and normalization now resolve as `bargain_breached`; valid same-treaty claim transfers can still fulfill via war-end co-belligerence snapshotting. Betrayal memory now uses actor-to-victim keys, list-safe categories, and active-only same-episode caps. Dormant bargains emit a low-priority dispatch reminder, and peace previews include unresolved bargain-breach warnings. `tests/test_wb_b_lifecycle.py` now has 50 tests. Verification: full suite `9162 passed, 1 skipped`; `ruff check backend tests` green. **Next: WB-C.**)
> **Last Updated:** April 27, 2026 (**WB-A AUDIT FOLLOW-UP COMPLETE** — War Bargain ratification now preserves `named_enemy` / `claim_region`, validates projected same-treaty alliances before state mutation, rejects invalid bargain clauses, blocks multiple bargain clauses and same-treaty claim-region cessions, and creates commitments only after validation. `validate_war_bargain()` now also enforces beneficiary-side opposition, strategic-interest basis, and participation-access gates. Region-observer scope uses direct claim-region lookup instead of per-region scans. `diplomatic_commitments` serialization now deep-copies nested terms. `tests/test_wb_a_bargain_model.py` expanded to 32 tests. Verification: full suite `9104 passed, 1 skipped`; ruff green. **Next: WB-B.**)
> **Last Updated:** April 26, 2026 (**`threat_coalition` retirement COMPLETE** — legacy compatibility payload removed from `build_diplomatic_ledger()`. Unique data (threat sources with labels, active coalition member details with WE/trends, threat projection, dissolution thresholds) merged into `_build_balance_of_europe()`. `_build_threat_coalition()` deleted (132 lines). Godot `_render_threat_coalition()` renamed to `_render_balance_of_europe()` and updated to read exclusively from `balance_of_europe` payload. 8 test files updated to assert on `balance_of_europe` keys only. No `threat_coalition` references remain in Python or GDScript outside of historical documentation. Verification: full suite `9071 passed, 1 skipped`; ruff green on all touched files. **Next: WB-A.**)
> **Last Updated:** April 26, 2026 (Peace Deals **WPS-D COMPLETE** — War score legibility + AI + surface polish. Settlement tier classification and display already existed from WPS-A. NEW: Peace preview extension (`build_war_context_snapshot`) now includes `war_objective`, `settlement_tier`, `settlement_tier_display`, and `tier_mismatch_warnings`. Tier mismatch warning system detects when proposed terms exceed current settlement tier (forced_alliance requires harsh_peace, ap_per_turn requires harsh_peace, 4+ territory demands require harsh_peace, 2+ require dictated_terms). AI ticking pressure modifier shifts P1 peace threshold by `(opponent_ticking - own_ticking) // 5` clamped ±10. AI power cap pre-check utility (`ai_check_vassalage_power_cap`) gates future vassalage proposals. AI liberation peace evaluation refuses peace without liberation clauses when war score supports it. Enemy AI P3.8 liberation priority targets vassal capitals for coalition members with liberation objectives. Dispatch enhanced with forced alliance/liberation event highlighting in peace settlements. 18 new tests in `tests/test_wpsd_legibility_ai.py`. Verification: full suite `9062 passed, 1 skipped`; ruff check pending. **WPS phase complete. Next: Gate 1 verification or WB-A.**)
> **Last Updated:** April 26, 2026 (Peace Deals **WPS-C COMPLETE** — Forced alliance + liberation clause types. Forced alliance imposes ALLIANCE + Continental System on defeated nation with relation reset to 0, -10/turn drift, +15 coalition threat, and `alliance_origins` tracking. Liberation releases French vassals via `release_vassal()`, creates DEFENSIVE_ALLIANCE with liberator, adjusts relations (-20 lord, +30 liberator), reduces threat by 8. Acceptance formula: forced_alliance overrides base_disposition to -15 and adds -20 demand penalty; liberation adds -15 demand penalty. New `alliance_origins` field serialized with round-trip. Demand→clause conversion now carries `vassal_nation`/`lord_nation`/`liberator` extra fields. Campaign log: `forced_alliance_imposed` and `vassal_liberated` event types with fog filtering. 26 new tests in `tests/test_wpsc_forced_alliance.py`. Verification: full suite `9034 passed, 1 skipped`; `ruff check backend tests` green. **Next coding slice: WPS-D or audit follow-up.**)
> **Last Updated:** April 26, 2026 (Peace Deals **WPS-B AUDIT FOLLOW-UP COMPLETE** — Closed the vassalage power-cap audit gaps. Treaty ratification now hard-stops over-cap vassalage before any `VASSAL` state change, uses projected same-package territory cessions for real `territory_cede` proposal shapes, and no longer ignores `create_vassal_treaty()` failure. Typed/send proposal paths now block over-cap vassalage before DP loss. `project_power_after_terms()` handles normalized treaty clauses, raw proposal dicts, duplicate transfers, non-territory skips, and no-mutation projection. Edge coverage now includes zero-power lord, eliminated target, self-vassalage, real post-cession ratification, command bypass, and wizard action existence. Spec stale Britain ratio/naval wording fixed. `tests/test_wpsb_power_cap.py` now has 35 tests. Verification: focused WPS-B suite `35 passed`; focused cross-section `355 passed`; full suite `9004 passed, 1 skipped`; `ruff check backend tests` green. **Next coding slice: WPS-C** (forced alliance + liberation).)
> **Last Updated:** April 26, 2026 (Peace Deals **WPS-A AUDIT FOLLOW-UP COMPLETE** — Closed the WPS-A audit findings before moving on: stored `world.war_scores` now recalculates after ticking accumulation; armistice pauses objectives without concluding them and ARMISTICE→PEACE concludes them; campaign-log filtering preserves WPS-A events; Godot renders War Purpose content plus objective/ticking/settlement status details; combat-initiated player auto-wars stage War Purpose selection instead of bypassing it; parser/direct-set paths validate `set_war_purpose`; coalition liberation and AI-AI conquest objectives are assigned; and the France-on-defense spec contradiction is resolved in favor of auto-defense with one upgrade. `tests/test_war_objectives.py` expanded to 50 tests. Verification: focused WPS-A suite `50 passed`; cross-cutting focused suite `239 passed`; serialization enforcement `19 passed`; full suite `8969 passed, 1 skipped`; `ruff check backend tests` green. **Next coding slice: WPS-B** (vassalage power cap gating).)
> **Last Updated:** April 26, 2026 (Peace Deals **WPS-A COMPLETE** — War Purpose popup + objective state + ticking score. War declarations now require choosing an objective (conquest/subjugation/forced_alliance) via a blocking War Purpose dialogue before proceeding. Defenders auto-receive a defense objective. Ticking score is the 5th war score component (+2/turn conquest, +3 subjugation, +2 forced_alliance, +1/turn defense/liberation) capped at 25, paused during armistice. Settlement tiers (white_peace through total_victory) computed from war score. `set_war_purpose` action allows upgrading auto-defense on defensive wars. War status panel extended with objective + settlement tier data. Morning Dispatch gains war objective section. Campaign log types: `war_objective_declared`, `war_objective_ticking_started`. Godot `PROPOSAL_CONFIRM_DIALOGUE_TYPES` updated. 38 new tests in `tests/test_war_objectives.py`. Verification: full suite `8957 passed, 1 skipped`; serialization enforcement green. **Next coding slice: WPS-B** (power cap gating).)
> **Last Updated:** April 26, 2026 (Peace Deals **BPH PHASE CLOSURE FOLLOW-UP PUSHED** — Closed the remaining BPH integration gaps after the BPH-D audit: successful incoming AI peace and counter-offer accepts now pass `peace_ratification_summary` through `/command` and `/respond_to_diplomatic_dialogue`; delayed player-proposal acceptances attach the same summary to `proposal_result`; Godot renders immediate ratification summaries, incoming AI peace preview data, Morning Dispatch `peace_settlements`, and recent peace ratifications in the Diplomatic Ledger Treaties tab with expandable details. Added regression/static coverage across `tests/test_bph_d_ratification_summary.py`, `tests/test_bph_c_fallout_conflicts.py`, and `tests/test_session8b_ledger_ui.py`. Verification: full suite `8915 passed, 1 skipped`; `ruff check backend tests` green. **BPH phase audit verdict: GO. Next coding slice: WPS-A**.)
> **Last Updated:** April 26, 2026 (Peace Deals **BPH-D AUDIT FOLLOW-UP PUSHED** — Ratification summary now snapshots war data before diplomatic-state cleanup, uses `display_label` terms, reports incoming AI peace against the player counterpart instead of France, stores only formal PEACE ratifications in `peace_ratification_log`, and summarizes actual applied gold/territory transfers. Added 5 regression tests in `tests/test_bph_d_ratification_summary.py`. Verification: full suite `8906 passed, 1 skipped`; `ruff check backend tests` green. **Next coding slice: WPS-A**.)
> **Last Updated:** April 26, 2026 (Peace Deals **BPH-D COMPLETE** — Ratification summary + dispatch. `build_peace_ratification_summary()` in `diplomacy.py` produces the full war outcome summary (war outcome classification, territory/gold changes, casualties, terms ratified, political aftermath) with pre-cleanup data capture so battle records and war scores survive `cleanup_war_end`. `_ratify_treaty()` returns `peace_ratification_summary` in the result dict and stores it in the new `peace_ratification_log` field (capped at 5). Campaign log one-liner upgraded from `"Peace ratified: X and Y (N terms)"` to `"Peace with Prussia (French victory) — gained Rhineland, +500 gold"`. Morning Dispatch gains a `peace_settlements` section filtered to previous-turn ratifications with Treaty-of-Capital headline. New `peace_ratification_log` field added to WorldState with full to_dict/from_dict round-trip and SAVE_FORMAT_REFERENCE.md documentation. 21 new tests in `tests/test_bph_d_ratification_summary.py`. Verification: full suite `8901 passed, 1 skipped`; ruff green. **Next coding slice: WPS-A** (War Purpose popup at declaration time).)
> **Previously:** April 26, 2026 (Peace Deals **BPH-B COMPLETE + REVIEW FOLLOW-UP PUSHED** — Peace preview now uses the exact proposal terms that will be sent, the canonical proposal-confirm popup renders the frozen war-context snapshot, preview outcome spelling is normalized to the BPH-B contract (`COUNTER` instead of internal `COUNTER_OFFER`), and war-score trend uses a serialized three-turn history. The duplicate Godot wizard Step 3 peace-preview path was removed so the confirmation popup is the only send/reconsider surface. Commit `bd3b484` pushed after the follow-up audit. Verification: `tests/test_bph_b_peace_preview.py` `41 passed`; full suite `8849 passed, 1 skipped`; `ruff check backend tests` green. Godot headless parse was not run because `godot` / `godot4` are not on PATH. **Next coding slice: BPH-C READY** (Fallout preview + commitment conflicts).)
> **Previously:** April 26, 2026 (Peace Deals **BPH-A AUDIT FOLLOW-UP COMPLETE** — Closed the term-ownership/display-label audit findings. `annotate_peace_terms()` now assigns correct ownership for protection guarantees and Continental System clauses, renders military-access labels, includes vassal-territory qualifiers, suppresses duplicate `territory_*` special-desire markers when an explicit cession already exists, and tolerates missing/nonstandard term fields more defensively. `peace_ratified` campaign-log filtering now recognizes proposer/target fields, and `ARMISTICE_TO_PEACE` one-liners render as peace rather than armistice. Added 8 regression tests across `tests/test_bph_a_term_ownership.py` and `tests/test_campaign_log.py`. Verification: focused BPH/campaign-log suite `100 passed`; full suite `8808 passed, 1 skipped`; `ruff check backend tests` green. Next coding slice was BPH-B.)
> **Previously:** April 26, 2026 (Peace Deals Run #5 cleanup landed. Audit verdict is **GO** with M1 Fun 9, M2 Clarity 8, M3 Work Segmentation 9, M4 Contradiction-Freedom 9, M5 Completeness 9, and zero CRITICAL/MAJOR findings. Minor WPS/WB clarifications are folded in, live coalition records now include `active_coalition.target_nation` for WB overlap checks, and the next coding slice is **BPH-A**. Verification: full suite `8776 passed, 1 skipped`; ruff green.)
> **Last Updated:** April 25, 2026 (D3 Balance/ledger row clarity **IMPLEMENTED**. The Nations tab now receives a transient `nations[*].bloc_stamp` payload from `build_diplomatic_ledger()` and renders it beside each court name in Godot. Stamps reuse `describe_hegemon_bloc(...)` and keep the D3 priority order: `Coalition Member` dominates, then proper bloc names at `50%+`, descriptive bloc labels at `33-49%`, then `Vassal of {Overlord}`, then `Neutral`. The payload is display-only and never serialized. Focused verification: `tests/test_session8a_ledger_debug.py tests/test_session8b_ledger_ui.py tests/test_c_lite_presentation_closure.py tests/test_bugfix_session4.py::TestDLF1VassalizableIcon -q` => `134 passed`; full suite `8775 passed, 1 skipped`; ruff green.)
> **Last Updated:** April 25, 2026 (Peace Deals deferred carry-forward gate clarified. The future Peace Deals umbrella spec must include a named "Deferred Carry-Forward Checklist" before approval, covering WB-D bargain presentation, response routes, bargain icons, fulfillment/breach badges, region-observer witness scope, scope-branched witness copy, and any callback/aftermath architecture it needs. Each item must be assigned to a concrete Peace Deals slice, explicitly deferred again with rationale, or marked out-of-scope; none may vanish as vague later polish.)
> **Last Updated:** April 25, 2026 (Deferred-item routing plan added. D3 per-row bloc stamps/member badges are the only Memory and Pressure deferred item that is reasonable to do as a small pre-Peace polish pass, and only if Balance of Europe playtest readability needs it. WB-* bargain presentation, response routes, region-observer witness depth, bargain icons, and richer callback architecture should move inside the Peace Deals umbrella spec instead of being reopened as standalone Memory and Pressure follow-ups. D1 advisory-first strategy and D2 non-France-hegemon generalization remain later strategic/scale work unless a new scenario or Peace Deals spec explicitly needs them.)
> **Last Updated:** April 25, 2026 (Post-C-lite smoke workflow **CLOSED** — in-game follow-up fixes landed after the C-lite closeout: major/secondary powers no longer show the vassalizable marker, Saxony/minor eligibility mirrors the actual `make_vassal` command gate, Balance of Europe copy now says active European bloc power with score/member context, same-war cascade Balance beats defer until cascade resolution, `cheat trigger_commitment_paradox ...` opens the commitment popup for smoke testing, and the popup choices now read `Honor {defender}` / `Side with {attacker}`. Project-local workflow skill added at `.agents/skills/sovereign-map-workflow/`. **Next workflow:** run D3 Balance/ledger clarity follow-up first if we want per-row bloc stamps/member badges; otherwise move to Peace Deals only after a dedicated Peace Deals implementation spec is written and approved. `docs/WAR_BARGAIN_SPEC.md` covers the War Bargains sub-slice, not the whole Peace Deals phase.)
> **Last Updated:** April 25, 2026 (Memory and Pressure v2.4.3 **C-lite closeout COMPLETE** — combined audit follow-up closed the remaining presentation/spec gaps: §8.1 routing now covers `amends_offered`, hard-reject posture, treaty breakage, paradox resolution, Balance of Europe, witness, and all DG-4 call-to-arms families; Make Amends, treaty-broken, hard-reject, dispatch, campaign-log, and notification details route through the shared commitments metadata; `resolve_named_diplomat()` is live with named-envoy and chancery fallback behavior; generic British advisory fallback no longer hardcodes Castlereagh; stale `commitment_paradox_resolved` dispatch callbacks were removed; Godot notification review now opens the commitments review target in the Diplomatic Ledger; the notification rail caps above-fold commitments notices per turn; `cascade_profile` is serialized and consumed for DG-4 severity/cooldown knobs; Balance of Europe assertions were added beside legacy `threat_coalition` compatibility tests. **Deferred closeout note:** evaluate deferred items after we code the spec — keep D1 advisory-first strategy, D2 non-France-hegemon generalization, D3 per-row bloc stamps, WB-* bargain-era presentation, and richer callback architecture deferred; do not reopen for this phase. New focused coverage lives in `tests/test_c_lite_presentation_closure.py`.)
> **Last Updated:** April 25, 2026 (Memory and Pressure v2.4.3 **DG-4 spec-closure fixes COMPLETE** — follow-up audit gaps closed: call-to-arms cascade is now DG-4 direct-only with root-principal vassal auto-entry and no transitive ally/vassal propagation; `war_entry_ledger` records direct ally and vassal paths; `call_to_arms_refused_offensive`, `call_to_arms_refused_defensive`, and `call_to_arms_honored_costly` now emit CRITICAL rail notices through a shared commitments routing table used by dispatch/campaign-log copy; defensive refusal uses envoy/victim-diplomat attribution; defensive-refusal coalition memory stores refusal-moment treaty-partner snapshots; severity scaling now exposes `honor_bias`, aggressor `power_tier`, and war-exposure factors; same-episode witness dispatch rows collapse into one summarized presentation row; `balance_of_europe` now ships in the diplomatic ledger beside the legacy `threat_coalition` compatibility payload; Godot notification icons/review routing and Balance headline rendering are wired. New focused coverage lives in `tests/test_dg4_spec_closure.py`.)
> **Previously (April 25, 2026):** Memory and Pressure v2.4.3 **DG-4 completion audit fixes COMPLETE** — closed the remaining DG-4 substrate gaps found in that pass. Superseded by the C-lite closeout entry above.
> **Last Updated:** April 23, 2026 (Memory and Pressure v2.4.3 **B-B4 review follow-up COMPLETE** — the substrate-level gaps flagged in the B-B4 code review are now closed. Parser: the loose `"abandoned alliance"` bare-substring disambiguator is removed from `backend/ai/llm_client.py`; only explicit `for the abandoned alliance` / `for abandoning the alliance` / `for the abandoned call` / `for refusing the defensive call` / `grievance variant` phrases now route to `amends_variant="grievance"`, closing the `"I abandoned the alliance, make amends"` false-positive vector. **§8.8.3 wider witness scope landed.** New `WITNESS_SCOPE_TREATY_PARTNER_OF_BREAKER = "treaty_partner_of_breaker"` constant + `DG4_WITNESS_SCOPE_PRECEDENCE` tuple + `_ACTIVE_TREATY_STATES_FOR_DG4_WITNESS` frozenset (OPEN_BORDERS / NON_AGGRESSION / DEFENSIVE_ALLIANCE / ALLIANCE / VASSAL — WAR excluded as not-a-treaty, PEACE excluded as default-absent, ARMISTICE excluded as belligerent-adjacent). `_classify_dg4_refused_defensive_witness_scope` resolves per-witness role under the `ally > rival > treaty_partner_of_breaker > shared_enemy > region_observer` precedence; `_get_dg4_refused_defensive_witness_scope` returns the `{witnesses, dominant_scope, label, count, sample}` shape that mirrors `_get_breach_witness_scope`. The emitter now computes witness scope AFTER same-turn alliance termination so `treaty_partner_of_breaker` reflects post-termination geometry, then emits one `witness_strike_recorded` dispatch per witness with `scope_reason`, `source_episode_type="call_to_arms_refused_defensive"`, and `relation_delta: 0` / `reliability_delta: 0` (matching the existing substrate-wide pattern; numeric witness effects per §8.8.2 remain a broader substrate question deferred uniformly across all betrayal events). **§8.8.7a cascade gate.** `_record_treaty_breach` now skips its own witness emission when the breach is a `defensive_refusal_termination` cascade (checked via `trigger_context["refusal_episode_type"]` or the `end_reason_family`), so the refusal episode is the single authoritative emitter under its wider scope — no double-counted witnesses on the same `episode_id`. **§8.8.7 anti-renewal cooldown live.** New `anti_renewal_cooldown: Dict[str, int]` field on `WorldState` with to_dict/from_dict round-trip and pre-B-B4 `{}` default; `ANTI_RENEWAL_COOLDOWN_TURNS = 15` constant; `is_anti_renewal_active(world, a, b)` + `get_anti_renewal_turns_remaining(world, a, b)` public helpers; `_set_anti_renewal_cooldown` internal. Emitter sets `anti_renewal_cooldown[diplo_key] = current_turn + 15` on every refusal regardless of prior-alliance presence. **Mechanical gate in `calculate_acceptance`:** mirrors the `hard_reject_posture` `-100` score-clamp pattern — `anti_renewal_block = -100` + `score = min(score, 0)` for ALLIANCE / DEFENSIVE_ALLIANCE proposals between the pair while cooldown is active; NON_AGGRESSION / OPEN_BORDERS / PEACE unaffected per §8.8.7 "Peace and non-aggression remain available during the window"; no survival-exception branch per "Blocking is mechanical, not advisory." `components` dict gains `anti_renewal_block` / `anti_renewal_active` / `anti_renewal_turns_remaining` debug rows; `SAVE_FORMAT_REFERENCE.md` documents the new field. **§8.6 category hygiene** — `_remove_oldest_grievance_flag` now discards `"grievance"` from the pair's `categories` when the final flag clears but strikes remain, so strike-only pairs after repair no longer surface under grievance-category queries (pair-prune path already cleaned fully-cleared pairs). **Copy tightening:** `FEEDBACK_STRINGS["composite_floor_adjustment"]` "negative" copy changed from the misleading "the floor absorbed additional pressure" to "the composite floor lifted the political subtotal back to -60" (the adjustment is non-negative by construction); `anti_renewal_block` / `anti_renewal_active` / `anti_renewal_turns_remaining` gain FEEDBACK_STRINGS entries so the component-key completeness test stays green (none are in `_generate_feedback` trackable — debug rows only). **`test_bb4_grievance.py` grows to 89 tests** (+26 net: 4 TestParserFalsePositives regression cases, 9 TestDG4WitnessScope covering precedence / exclusions / scope-role precedence / treaty-partner role / WAR / PEACE edge cases / dispatch emission count + delta contract, 10 TestAntiRenewalCooldown covering 15-turn window + no-alliance-needed path + expiry + self-pair guard + unaffected-pair isolation + ALLIANCE block + DEFENSIVE_ALLIANCE block + NON_AGGRESSION allowed + save-load round-trip + pre-B-B4 migration, 2 TestCategoriesCleanup, 1 TestEndToEndGrievanceVariant for natural-language → parser → CommandExecutor routing). `test_refusal_when_at_war` assertion re-based from the brittle `"ransom"` substring to the stable nation-name + no-resources-spent + flag-intact contract. **Full suite:** `8720 passed, 1 skipped` (was `8694 passed, 1 skipped` pre-follow-up; +26 tests net). Ruff clean on every follow-up-touched file (`diplomacy.py` / `world_state.py` / `llm_client.py` / `display_names.py` / `test_bb4_grievance.py`); pre-existing lint in `diplomatic_executor.py:1393,1868` + `dispatch.py:113` still predates B-B4 per `git blame`. **Next at that time:** Slice `C-lite`; superseded by the April 25 C-lite closeout entry above.)
>
> **Previously (April 23, 2026 earlier):** Memory and Pressure v2.4.3 **B-B4 COMPLETE** — DG-4 call-to-arms follow-through landed per spec §8.6.1a + §8.8 + §8.8.7a + §8.8.9 + §9.3. Three substrate pieces shipped together: (1) `grievance_flags` are now first-class entries on `betrayal_history` pair records with their own canonical schema `{grievance_type, episode_id, turn, source_episode_type}` plus round-trip serialization in `world_state.py::to_dict` / `from_dict`; four helpers in `backend/game_logic/diplomacy.py` (`_get_grievance_flags`, `_get_active_grievance_flag_count`, `_get_capped_grievance_flag_count`, `_add_grievance_flag`, `_remove_oldest_grievance_flag`) encapsulate read / write / FIFO removal with deterministic `(turn, episode_id)` tie-break; pair records prune when both strikes and flags are empty. (2) `grievance_modifier(asker, target, world) -> int` returns `-30 * min(3, active_count)` and saturates at the 3-flag stacking cap (max `-90`) per §8.8.4 / §8.8.9; the raw (uncapped) count surfaces separately as `grievance_flag_count_raw` in `calculate_acceptance` components so the ledger can distinguish "3 grievances" from "4+ grievances" distinctly. (3) `calculate_acceptance` reintroduces the `-60` composite floor per spec §9.3 with-DG-4 clause: `political_subtotal = hegemony_target_mod + bilateral_betrayal_mod + grievance_modifier` is clamped at `-60`, with `composite_floor` / `composite_floor_applied` / `composite_floor_adjustment` synthetic debug rows preserved in `components` so the full "hegemony -20, betrayal -18, grievance -90, composite floor applied at -60" debug line survives the clamp. `END_REASON_FAMILY_DEFENSIVE_REFUSAL_TERMINATION = "defensive_refusal_termination"` added as a fourth §9.9 family with a dedicated display label in `END_REASON_FAMILY_DISPLAY` (`"Ended by refusal of the defensive call"`), plus `_REASON_ACTION_PHRASES["defensive_refusal"] = "by refusing the defensive call"` for treaty-broken reason phrasing; `_resolve_end_reason` preserves the new family when `end_reason_action == "defensive_refusal"`. `emit_call_to_arms_refused_defensive(world, *, breaker, victim, severity="high", call_context, episode_id)` is the programmatic substrate seam that (a) records the `+2` victim-side strike, (b) appends a durable `grievance_type="defensive_call_refused"` flag, (c) applies `-10` to breaker reliability clamped `[-100, 100]`, (d) when a binding `ALLIANCE` / `DEFENSIVE_ALLIANCE` exists, downgrades it to `PEACE` in the same call via `set_diplomatic_state` (which handles bloc-cache invalidation + hegemony band-crossing checks), emits `diplomatic_treaty_broken` with `end_reason_family = defensive_refusal_termination` through `_record_treaty_breach` (no additional strike/reliability delta per §8.8.7a cascade clause), and (e) records and dispatches the episode itself with `foreign_office` speaker attribution, `breaker` / `victim` keys wired into the `partial_on_nation` fog-visibility rule. Make Amends grievance variant (§8.6.1a) lands in `diplomatic_executor.py` as `_execute_make_amends_grievance_variant`: parser disambiguation in `backend/ai/llm_client.py` routes `"for the abandoned alliance"` / `"for abandoning the alliance"` / `"for refusing the defensive call"` / `"abandoned alliance"` to `amends_variant="grievance"` in `diplomatic_data` while the default `"make amends with {nation}"` phrasing stays `amends_variant="standard"`; the executor branches at top of `_execute_make_amends` on the variant. Grievance-variant costs are `400g + 2 DP` (double the standard) per §8.6.1a; on success it removes the oldest grievance flag (FIFO by turn, episode_id tie-break), applies `+3` reliability clamped `[-100, 100]` and `+8` nation_relation, spends the resources, and sets the SHARED `reparations_cooldown[diplo_key]` to `current_turn + 10` (one Make Amends of ANY variant per pair per 10 turns per §8.6.1a "shared" clause). Refusal paths: explicit `no_active_grievance` Talleyrand advisory (distinct from `no_active_strikes` — grievance variant fails on zero flags even when strikes exist), plus the four inherited §8.6.1 conditions (cooldown, WAR/ARMISTICE, insufficient gold, insufficient DP) with the grievance-variant cost displayed in shortfall messages. The two variants are STRICTLY distinct invocations — clearing a grievance does NOT touch strikes, and clearing a strike does NOT touch grievances (§8.6.1a "Standalone strikes coexisting" clause). `amends_offered` emission across campaign log, dispatch queue, and notification rail now carries `amends_variant: "standard" | "grievance"` + `grievance_variant: bool` + grievance-variant-specific lineage (`cleared_grievance_episode_id` / `cleared_grievance_type` / `cleared_grievance_turn` / `cleared_grievance_source_episode_type`) or strike-variant lineage; the standard path explicitly emits `amends_variant="standard"` + empty grievance fields, the grievance path emits `amends_variant="grievance"` + empty strike fields, so consumers disambiguate by flag OR by presence. Campaign log one-liner in `campaign_log.py::format_event_oneliner` branches on variant: grievance reads `"France offered amends to Austria for the abandoned alliance (400g, 2 DP)"`, standard reads `"France offered amends to Austria (200g, 1 DP)"`. New dispatch event `call_to_arms_refused_defensive` with its own commitments-routed template + `CRITICAL` priority + `partial_on_nation` fog rule; `CAMPAIGN_LOG_TYPES` grows to 57 (+ `call_to_arms_refused_defensive` under `"diplomacy"` `CATEGORY_MAP`). `AMENDS_REFUSAL_DISPLAY` gains the `no_active_grievance` Talleyrand advisory; `FEEDBACK_STRINGS` gains `grievance_modifier` player-voiced copy (`"their grievance over abandoned alliances"` / `"no grievance over abandoned alliances"`) plus neutral composite-floor debug entries (not in `_generate_feedback` `trackable` set so they never drive player-facing hints). 37 new tests in `tests/test_bb4_grievance.py` cover: grievance helpers (add / count / FIFO-remove / capped-count / pair-pruning with-and-without residual strikes / save-load round-trip with lineage intact); grievance_modifier (linear accrual `-30 / -60 / -90`, saturation at `-90` with 4+ flags, zero on clean / self / empty inputs); composite floor (clean-pair no-clamp, 3-grievance clamp with `composite_floor_applied=True` + `composite_floor=-60` + `composite_floor_adjustment=+30`, raw-terms-preserved when strikes + grievances stack to `-108`, 5-flag raw count distinct from capped modifier); `emit_call_to_arms_refused_defensive` (records strike + grievance + reliability `-10`, alliance `DEFENSIVE_ALLIANCE → PEACE` termination, non-alliance no-op preserves `NON_AGGRESSION`, `diplomatic_treaty_broken` carries `end_reason_family=defensive_refusal_termination` + zero applied_reliability_delta, bloc cache invalidation shrinks `get_bloc_members` same-turn, episode-id reuse honored, self-target ValueError); Make Amends grievance variant (success path deducts 400g/2DP/sets +3/+8/cooldown/removes-flag, coexistent-strike untouched, refusal-on-no-grievance with strike still present, refusal-on-cooldown shared with standard, refusal-on-WAR, refusal-on-insufficient-400g, refusal-on-insufficient-2DP, `amends_offered` on all three surfaces with `amends_variant="grievance"` + grievance lineage, result message names variant explicitly); parser disambiguation (default→standard, `"for the abandoned alliance"`→grievance, non-amends→default `"standard"`); display labels (`END_REASON_FAMILY_DISPLAY` carries new family, `AMENDS_REFUSAL_DISPLAY` carries `no_active_grievance`, campaign-log one-liner distinguishes variants). Three pre-existing enforcement tests updated for new substrate: `test_campaign_log.py::test_fortyfive_types_in_constant` count `56 → 57`, `test_serialization_enforcement.py::test_world_state_roundtrip_preserves_betrayal_history_and_episode_counter` fixture gains `grievance_flags: []` (new canonical record shape), `test_bugfix_proposal_flow.py::test_all_component_keys_in_feedback_strings` naturally satisfied by new FEEDBACK_STRINGS entries. **Full suite:** `8694 passed, 1 skipped` (was `8655 passed, 1 skipped` pre-B-B4; +39 tests net: 37 B-B4 + 2 pre-existing adjustments). Ruff clean on every B-B4-touched file (`diplomacy.py` / `display_names.py` / `world_state.py` / `campaign_log.py` / `llm_client.py` / `test_bb4_grievance.py`); pre-existing lint noise in `diplomatic_executor.py:1393,1868` + `dispatch.py:113` predates this slice per `git blame`. `docs/SAVE_FORMAT_REFERENCE.md` line 229 updated to document the `grievance_flags` per-pair schema with pre-B-B4 default. **Next at that time:** Slice `C-lite`; superseded by the April 25 C-lite closeout entry above.)

> **Previously (April 23, 2026 earlier):** Memory and Pressure v2.4.3 **B-B7 COMPLETE** — standard Make Amends active-redemption verb shipped per spec §8.6.1, with the review follow-up now closed as well. `make_amends` is wired through the full dispatch pipeline: added to `VALID_ACTIONS` (`backend/ai/validation.py`) + `META_ACTIONS`, to the parser's `valid_actions` (`backend/commands/parser.py`), to the LLM mock parser's target-required list + `_parse_diplomatic_command` routing + `diplomatic_keywords` (`backend/ai/llm_client.py` — `make amends`, `offer amends`, `amends with`, `amends to`, `repair relations`, `offer reparations`, `send reparations`), to both `free_actions` mirrors in `backend/commands/executor.py` + `backend/commands/meta_executor.py`, and to the diplomatic action tuple that routes into `DiplomaticExecutor._execute_diplomatic`. New `_execute_make_amends` in `backend/commands/diplomatic_executor.py` handles pre-validation for every §8.6.1 refusal condition (missing target, self-use, WAR/ARMISTICE, cooldown, insufficient DP, insufficient gold, no active strikes), selects the strike to remove per the §8.6 rule (oldest matured `decays_on_turn` first; else lowest-severity with oldest-creation-turn tiebreaker — reading the pair's full `record["strikes"]`, NOT the stricter `_get_active_betrayal_strikes` filter, so matured-but-not-yet-decayed strikes stay reachable), then on success spends `200g + 1 DP`, removes the strike (and prunes the pair record if empty, matching passive-decay cleanup), `diplomatic_reliability["France"] += 2` clamped `[-100, 100]`, `world.modify_nation_relation(France, target, +5)`, and sets `reparations_cooldown[diplo_key] = current_turn + 10`. New `reparations_cooldown: Dict[str, int]` field on `WorldState` with `to_dict`/`from_dict` round-trip. `amends_offered` now carries its own emitted `episode_id` plus the cleared strike lineage and deterministic deltas across all three surfaces per spec — campaign log (`world.log_event` with `episode_id`, `actor_nation`, `target_nation`, `target_diplomat`, gold/DP deltas, reliability before/after, `reliability_delta`, `relation_delta`, `cleared_strike_episode_id` / `severity` / `turn`, `cooldown_turns`, `cooldown_expires_on_turn`, `speaker_attribution="envoy"`), dispatch queue (`queue_dispatch_event` with the same lineage/delta payload under `partial_on_nation`, and `actor_nation`/`target_nation` added to the fog-check key list in `backend/game_logic/dispatch.py::_is_dispatch_event_visible`), and notification rail (`NotificationPriority.NORMAL`, new `AMENDS_OFFERED` constant in `backend/notifications.py`, with matching `details` payload). Result text carries both Talleyrand's gesture frame AND the target court's Voice-Bible committed acknowledgment line — Castlereagh (Britain), Hardenberg (Prussia), Metternich (Austria), Einsiedel (Saxony), with a chancery fallback for non-cast nations per COMMITMENTS_PRESENTATION_SPEC §10.3. `AMENDS_REFUSAL_DISPLAY` map in `backend/display_names.py` authors five Talleyrand-voiced advisory templates (`no_active_strikes`, `cooldown_active`, `war_or_armistice`, `insufficient_gold`, `insufficient_dp`) with `{nation}` / `{turns_since}` / `{required}` / `{available}` slots; `ACTION_DISPLAY["make_amends"] = "offers amends to"`, `OBJECTION_DISPLAY["make_amends"] = "offering amends"`, `DEFIANCE_DISPLAY["make_amends"] = "offered amends"` complete the R7 contract. `campaign_log.py` adds `amends_offered` to `CAMPAIGN_LOG_TYPES` (+`"diplomacy"` in `CATEGORY_MAP`) and a `format_event_oneliner` branch that surfaces the deterministic gold/DP cost. `dispatch.py` adds the event to `_DIPLOMATIC_EVENT_TEMPLATES` and `_DIPLOMATIC_EVENT_PRIORITY` (MEDIUM) with committed prose now overlaid by the shared commitments routing table. The grievance variant (§8.6.1a) and `commitments_notice_amends_offered` template family later landed in B-B4 + C-lite respectively. 27 new tests in `tests/test_make_amends.py` cover: success path (cost deduction, strike removal, reliability +2 with 100-clamp, relation +5, cooldown set); pair-isolation (Austria amends don't touch Prussia strikes); named-diplomat acknowledgment for all four foreign courts (parametrized); all three emit surfaces (campaign log + whitelist + CATEGORY_MAP, dispatch queue + fog rule + template vars, notification + priority + details, now with emitted `episode_id` + delta metadata pinned on each surface); one-liner format rendering; seven refusal paths (no strikes, cooldown active, WAR, ARMISTICE, insufficient gold, insufficient DP, missing target, self-targeted); serialization round-trip + empty-field round-trip + cooldown-blocks-reinvocation-after-save-load with turn-advance unblock; strike-selection (matured-first with fresh-strike-isolation, lowest-severity fallback with severity-ordinal tiebreaker); and display-name contract (ACTION_DISPLAY entry + AMENDS_REFUSAL_DISPLAY shape). Three pre-existing enforcement tests updated for the new action: `tests/test_campaign_log.py::test_fortyfive_types_in_constant` count 55→56, `tests/test_enforcement_suite.py::_get_free_actions` mirror, OBJECTION_DISPLAY + DEFIANCE_DISPLAY entries close the R7 contract. **Full suite:** `8655 passed, 1 skipped` (was `8625 passed, 1 skipped` pre-B-B7; +30 tests net: 27 B-B7 + 3 enforcement updates). Ruff clean on every file B-B7 touched (pre-existing lint noise in `diplomatic_executor.py:1011` lambda, `:1486` ambiguous `l`, `meta_executor.py:148` missing import, `dispatch.py:113` ambiguous `l` all pre-date this slice per `git blame`). `docs/SAVE_FORMAT_REFERENCE.md` line 233 updated from **Planned (B-B7)** to **landed** with the full field contract. **Next at that time:** B-B4, then Slice C-lite; both are superseded by the April 25 C-lite closeout entry above.)
>
> **Previously (April 23, 2026 earlier):** Memory and Pressure v2.4.3 **B-B1-lite COMPLETE** [commits `5a5a265` + `ad3b582` + `341b22a`] and **B-B3 COMPLETE** this session. B-B3 retired the last alliance_paradox surface seams per spec: deleted legacy `alliance_paradox_popup.tscn` + `alliance_paradox_popup.gd` + `.gd.uid` from `godot-client/project-sovereign/`, updated `dialog_manager.gd:21` layer-registry comment to `commitment_paradox_popup`, cleared the obsolete `TestM10AllianceParadoxTodo` skip stub in `tests/test_audit_major_2026_03.py` (M10 TODO was superseded by this slice; now a doc-only note), and added 9 focused regressions in new `tests/test_commitment_paradox_rename.py` covering: (a) rename smoke — `declare_war` paradox path emits canonical `commitment_paradox` dialogue type + `commitment_paradox_popup` field only, dialogue carries `origin_episode_id` threaded through for §6.5 replay; (b) alias load gate — `WorldState.from_dict` migrates legacy `alliance_paradox_popup` save key to canonical, canonical wins when both present, and `DialogueManager` replays legacy `"alliance_paradox"` dialogue type as hard-stop through dual-registration in `HARD_STOP_TYPES` + `DIALOGUE_PRIORITY`; (c) no double-emit — paradox pushes exactly one dialogue with empty queue, fills only the canonical popup slot, and `to_dict()` never re-serializes the legacy `alliance_paradox_popup` key (canonical-only round-trip). The substrate-side rename (push-side type at `backend/game_logic/diplomacy.py:2330`, canonical `world.commitment_paradox_popup` + load-side alias at `backend/models/world_state.py:741-755, 3791-3794`, `DIALOGUE_PRIORITY` + `HARD_STOP_TYPES` dual-registration at `backend/models/dialogue_manager.py:42-47, 82-90`, `PopupQueue.LEGACY_ALIASES` + `RESPONSE_KEYS` at `backend/models/cooldown_manager.py:136-162`, Godot handler registration + routing at `godot-client/project-sovereign/scripts/main.gd:100, 226-228, 726, 774-782`, new `commitment_paradox_popup.{tscn,gd}` scene) was already live from prior slices; this slice closes the retirement + regression surface the spec explicitly called out. `docs/SAVE_FORMAT_REFERENCE.md:14, 111, 113, 194, 232` already documents the alias-on-load migration policy. **Full suite:** `8625 passed, 1 skipped` (was `8572 passed, 2 skipped` pre-B-B1-lite; +53 tests net from B-B1-lite + B-B3 + obsolete skip removal). Ruff clean on touched files (`tests/test_commitment_paradox_rename.py` + `tests/test_audit_major_2026_03.py`). **Repo reality:** the substrate rename is now fully landed. Next in merge order is **B-B7** (Make Amends active-redemption verb — standard variant only; grievance variant stays with B-B4 under the B-B1-lite ↔ B-B4 merge gate).)
> **Previously (April 22, 2026):** Memory and Pressure v2.4.3 **B-Hegemony COMPLETE** and verified. `backend/game_logic/coalition.py` now ships bloc-share detection, the `0 / 1 / 3 / 5 / 8` hegemony ladder, surfaced `33 / 50 / 60` bands, `balance_of_europe_shifted` beat emission, same-band hegemon-swap detection, end-of-turn relaxation-aside dedupe, and legacy anonymous clue retirement via gate+dismiss. `backend/models/world_state.py` now seeds `hegemony_signal_high_water` / `hegemony_signal_hegemon` from opening geometry; `backend/game_logic/vassal.py`, `backend/game_logic/diplomacy.py`, and `WorldState._eliminate_nation()` now invalidate bloc caches on the critical seams; `backend/game_logic/ai_diplomacy.py` now honors the `50%+` bandwagon trigger. Review-driven hardening closed the stale vassal-removal / elimination cache bug, made hegemony seam failures log contextual diagnostics, and added direct regressions for vassal-removal invalidation, true `52 -> 49 -> 51` oscillation, relaxation dispatch failure safety, and deterministic bandwagon trigger/block behavior. Full suite `8572 passed, 2 skipped`. Repo reality is partial migration: `backend/game_logic/diplomatic_ledger.py` still returns `threat_coalition`, `backend/game_logic/diplomacy.py` still computes legacy `threat_modifier` / `coalition_penalty`, and Slice C-lite ledger/render work is still pending.
> **Previously (April 22, 2026):** Memory and Pressure v2.4.3 §7.3 + §11.1 re-audit follow-up. **Per-row bloc stamps re-deferred** back out of v2.4.3 scope to `RELIABILITY_IMPLEMENTATION_PLAN.md` Slice D3 — the locked baseline keeps the naming layer concentrated on four surfaces (Balance of Europe headline, `balance_of_europe_shifted` threshold beats, proposal-preview `hegemony` warnings, coalition-declaration contrast copy). Spec alignment: `RELIABILITY_COMMITMENTS_SPEC.md` §11.1 now states stamps are deferred, tightens the non-France-hegemon suppression rule to name BOTH Case 3 brewing AND Case 4 formal-coalition lines, adds a reassurance about brewing visibility via popup/HUD, extends the non-player-hegemon honesty clause across the full 0-59 threat band to close the Case 2 voice-intent mismatch, marks the declaration contrast copy as the peak dramatic moment, adds an explicit same-band hegemon-swap beat rule, and clarifies the dispatch event-line vs state-summary distinction in §11.4. `COMMITMENTS_PRESENTATION_SPEC.md` matches: top scope note now pulls stamps out and adds a repo-reality check; §8.1a.2 authors the `30-32%` pre-noticed label-free band explicitly; §8.1a.4 mirrors the non-France-hegemon guard onto the declaration contrast copy, ranks declaration copy above the Case 4 ledger line, and adds the same-band-swap beat requirement; §11 payload contract adds the dual-`cooldown_turns_remaining` synchronization rule and defers the `nations[*].bloc_stamp` payload; §16 acceptance gate closes the 30-33% label-erasure hole and adds the same-band-swap criterion. `COALITION_SPEC.md` §3e/§3f require the bloc-vs-coalition contrast subline on the declaration popup (with v0.1 non-France-hegemon guard), §8a/§8d mark the Tension/Murmurs clue chain legacy yielding to `balance_of_europe_shifted`, the `coalition_brewing` / `coalition_declared` template slots now carry `{target_nation}` / `{bloc_label}` explicitly, and §9b/§9d update the notification matrix + declaration popup example. `RELIABILITY_IMPLEMENTATION_PLAN.md` moves Slice E-Cards → Slice D3 in deferred; test budget drops to ~54-63 critical path (~79-92 with DG-4); execution order no longer runs stamps. `DIPLOMAT_VOICE_BIBLE.md` scope note + minimum-coverage text re-align stamps as deferred. `docs/audits/MP_V243_BLOCK3_BLOC_NAMING.md` supersession note updated to reflect the re-deferral. **Historical repo reality at that point (superseded by the April 25 C-lite closeout):** `backend/game_logic/diplomatic_ledger.py` still shipped `threat_coalition` and the Nations tab still rendered `NATION OVERVIEW`; `backend/game_logic/coalition.py:1098-1132` still emitted anonymous `Diplomatic Tension` / `European Courts Concerned`; `hegemony_pressure` was still a label over legacy coalition-threat math. B-Hegemony + B-B1-lite + Slice C-lite are a substrate swap, not additive copy. Tests in `tests/test_session8a_ledger_debug.py` + `tests/test_session8b_ledger_ui.py` asserted the legacy payloads and are now supplemented with Balance of Europe assertions. **Closeout rule:** evaluate deferred items after we code the spec.)
> **Previously (April 21, 2026):** Memory and Pressure v2.4.3 doc follow-up. Closed the remaining doc seams from the latest §7.3 / §11.1 audit: `COMMITMENTS_PRESENTATION_SPEC.md` §11 now owns the `nations[*].bloc_stamp` payload contract directly instead of leaving it only in the implementation plan; `RELIABILITY_COMMITMENTS_SPEC.md` now says `50%` / `60%` re-entries within one epoch do not re-fire beats and tightens the quiet Case-2 flavor line so low-band tension reads alive rather than inert; `COALITION_SPEC.md` now restates that `70%+` is scalar-only intensification (no fourth naming band) and that brewing copy stays anchored to `world.player_nation` while foreign-hegemon pressure sub-lines remain suppressed in v0.1; the historical Block 3 audit doc now explicitly marks its old badge-deferral line as superseded. British generic-fallback cleanup was later closed by the April 25 C-lite entry above.
> **Previously (April 21, 2026):** Memory and Pressure v2.4.3 follow-up tightening pass. Folded the latest Claude audit items into the live docs: §7.3 now says **current hegemon's bloc** rather than "player's bloc," upward beats always carry one legible counter-play hint (with an "avoid another major ally" floor), the planned band-memory field is renamed to `hegemony_signal_high_water`, opening scenarios seed that high-water state so turn 1 does not fake a fresh 33% revelation, downward `60 -> 59` / `50 -> 49` relaxations are deduped per equilibrium epoch and explicitly use the post-drop label, the `50%` Case-2 headline echo line is now committed in-spec, and the v0.1 non-France-hegemon headline / scalar asymmetry is explicitly documented rather than left implicit. `DIPLOMAT_VOICE_BIBLE.md` and `RELIABILITY_IMPLEMENTATION_PLAN.md` were tightened to match (hegemon-agnostic register note, crisis-only cooldown clause, current-share helper vs stored high-water distinction). Doc-only edits — B-Hegemony remains the next implementation slice.
> **Previously (April 21, 2026 earlier):** Memory and Pressure v2.4.3 §7.3 + §11.1 tightening pass. Merged audit findings from two parallel reviews against `RELIABILITY_COMMITMENTS_SPEC.md` §7.3 (Hegemony detection) + §11.1 (Diplomatic Ledger) and the surrounding clue chain. Doc-only edits — engine implementation remains the pending B-Hegemony slice. Fourteen findings landed: (1) **Ladder ↔ beat alignment.** `_hegemony_pressure_for_share` gates moved from `30 / 40 / 50 / 60` to `33 / 50 / 60 / 70` with values `1 / 3 / 5 / 8`, eliminating the 30-33% silent-tax band and the unbeated +1→+3 jump at 40%. Pressure-floor `if share < 0.33: return {}` and the "falling below resets memory" reset both moved to 33% so beat memory and accrual eligibility move together. (2) **Defensive fallback hardened.** §7.3's "evaluate every active nation" fallback replaced with the canonical 5-major safe-list `(France, Britain, Russia, Austria, Prussia)` so v0.1 stays correct even when scenario `power_tier` data has not yet been authored; expansion to all-actives is reserved as last-resort safety for unknown rosters. (3) **§11.1 opening example replaced.** Old example mixed BREWING + Castlereagh-line + bare "France" — three contracts violated on the same prose block. New worked example is a clean Case 4 (DECLARED) with `describe_hegemon_bloc` applied identically across all three lines. (4) **Beat surface ≠ headline ≠ Morning Dispatch.** §7.3 + §11.1 now require `balance_of_europe_shifted` to fire as a named-diplomat *notification* (the upstream event), not as the headline or dispatch line themselves (which display state). (5) **R3 mitigation list fixed.** Removed "nation rows show bloc membership badges" — badges are deferred per §11.1; mitigation now correctly cites headline + threshold beats + preview warnings only. (6) **§11.2 'new hegemony band' disambiguated** to `_hegemony_signal_band` (bands `1 / 2 / 3` ↔ `33% / 50% / 60%`), and inline-slot collision policy specified: hegemony warning displaces lowest-severity slot rather than overflowing on band-cross turns. (7) **Counter-play hint contract tightened.** Hints must now name *which* bloc members account for the share contribution — generic *"consider releasing a vassal"* reads as random advice. (8) **Fail-loud guard for `system` speaker** added to `COMMITMENTS_PRESENTATION_SPEC.md` §10.3 — render path MUST raise `ValueError` when `speaker == "system"` reaches a rail or notice surface. Documentation is not enforcement. (9) **Voice Bible cross-refs** added to §8.1a.5 — Talleyrand bloc-naming guardrail (dry acknowledgment, never pride) + forbidden-jargon list now visible to template authors working from the presentation spec alone. (10) **AI bandwagon trigger moved from `~45%+` to `50%+`** in `RELIABILITY_IMPLEMENTATION_PLAN.md` B-Hegemony — aligns with the player-facing proper-noun reveal threshold so AI doesn't react to "the French System" before the player can see the name. (11) **`COALITION_SPEC.md` §3a Murmurs notification rewritten** — generic *"European courts are concerned"* anonymous line was contradicting the v2.4.3 voice contract; now points to `balance_of_europe_shifted` named-diplomat clue chain. (12) **R8 prescription tightened** — same-turn beat as N+1-lag mitigation is now the canonical answer that ships with B-Hegemony, not a menu item. (13) **§7.8.4 pacing contract gained explicit baseline assumptions** (starting threat = 0, no competing event-based threat, decay still draining) plus a B-Hegemony acceptance check that asserts `threat_level >= 60` by turn 16 in a deterministic 50%-share scenario. (14) **`docs/RELIABILITY_COMMITMENTS_SPEC.md`, `docs/COMMITMENTS_PRESENTATION_SPEC.md`, `docs/RELIABILITY_IMPLEMENTATION_PLAN.md`, `docs/COALITION_SPEC.md` updated.** No code changes — B-Hegemony engine + `balance_of_europe_shifted` notification + `describe_hegemon_bloc` helper + Balance-of-Europe ledger headline remain the next implementation slice.)
> **Previously (April 20, 2026):** Memory and Pressure v2.4.3 Block 3 fold. The Block 3 audit doc is SUPERSEDED — its bloc-naming contract (D1-D10) and CF1-CF4 post-Block-2 closure items have been folded back into their owning specs: `COMMITMENTS_PRESENTATION_SPEC.md` §8.1a (bloc-naming contract: terminology guard, `33 / 50 / 60` activation gate, hegemon→label taxonomy, required surfaces), `DIPLOMAT_VOICE_BIBLE.md` "Bloc-naming voice contract" subsection, and the parent slices in `RELIABILITY_IMPLEMENTATION_PLAN.md` (CF1 → C-lite, CF2 → B-B7, CF3 → B-B4, CF4 → B-B4 per the B-B1-lite merge gate). No separate Block 3 consumption pass is required; the remaining B-Hegemony / B-B1-lite / B-B3 / B-B4 / B-B7 / C-lite slices may now proceed directly, with the B-B1-lite ↔ B-B4 merge-ordering gate still in force.
> **Previously (April 20, 2026):** Memory and Pressure v2.4.3 Block 2 substrate alignment complete and pushed. Deterministic bloc naming adopted for v2.4.3 on the constrained headline/beat/warning/declaration surfaces; member badges deferred. (Badges were briefly promoted to live scope on April 21 and then re-deferred on April 22 back to Slice D3 — see top entries above.)
> **Previously (April 19, 2026):** Map Readiness §4.4 audit fixes landed. Three findings resolved: (1) Stale routing in `STATUS.md` lines 123-131 + `SCALE_READYNESS.md` §2 / §§4.1-4.4 that still pointed readers at §4.4 as "next slice" or "NOT DONE." `STATUS.md` now flags `SCALE_READYNESS.md` as a historical audit snapshot and marks the next-slice block as "none — art-blocked only." `SCALE_READYNESS.md` gained a bold "HISTORICAL SNAPSHOT — do not use for current routing" banner and the per-phase list now shows §§3.1 + 4.1-4.4 as DONE. (2) Unwired tooltip visual distinctness. The panel now uses a dedicated warm-sepia palette (`UNWIRED_TOOLTIP_PANEL := Color(0.14, 0.11, 0.08, 0.95)`, border `(0.55, 0.42, 0.28, 0.9)`, title + suffix colors in the same warmth range) instead of the near-identical cold blue-grey that previously only differed from the fogged tooltip by 0.02 on one channel. A new `test_unwired_tooltip_palette_distinct_from_fogged` enforces the warmth contract programmatically (R must beat B by > 0.03 on panel and > 0.2 on border). (3) Alpha-preservation coverage. `tests/test_map_unwired_overlay.py` gained an `_apply_overlay_rgba()` mirror that explicitly carries the alpha channel, a `test_overlay_preserves_alpha_channel_under_rgba_mirror` fixture test covering alpha = 0 / 128 / 255 on unwired pixels, and a `test_renderer_source_explicitly_restores_alpha_after_lerp` source-level pin that fails if a future edit drops the `tinted.a = base.a` line — the exact regression the audit flagged as invisible to the old RGB-only mirror. Full Python suite now `8506 passed, 2 skipped` (was `8503`; +3 new tests). Ruff clean.
> **Previously (April 19, 2026):** Map Readiness Closure Pass — §4.4 unwired province support is COMPLETE. Renderer gained three coordinated seams: a single `_apply_unwired_grey_overlay(visual_image, lookup_image)` helper that lerps `UNWIRED_GREY_COLOR (0.32, 0.32, 0.34, 1.0)` over every visual pixel whose lookup color belongs to an unwired province, with `UNWIRED_GREY_BLEND = 0.7`, invoked from BOTH the circle-fallback AND the bitmap-loader path; `_is_region_wired(region_name)` + `_unwired_lookup_keys()` helpers routing the gate through `province_shapes`; and a dedicated `_draw_unwired_region_tooltip()` rendering `"<Province Name>" / "(not yet in play)"`. `MOUSE_BUTTON_LEFT` click handler short-circuits on unwired before `region_clicked` emit.

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Tests Passing** | **Last confirmed backend baseline in this status file:** `9755 passed, 1 skipped`; `ruff check backend/` clean after Imperial Settlement audit fixes. Later implementation commits are referenced above but are not reachable from this docs branch, so their recorded test baseline must be verified on the chosen integration/smoke target. Current v0.27 changes are docs-only and have not rerun the suite. Godot runtime smoke remains manual-only unless a Godot executable is available. |
| **Current Phase** | **Peace Deals - Settlement UI Cleanup v0.27 GO-pending-verification + chosen-target SC-27 re-scan + v0.27 compatibility verification + executable pre-smoke verification + branch-target reconciliation + expanded Gate 4 smoke.** The next work is to choose or create the branch where the implementation commits are reachable, rerun STATUS/SC-27 scans across both settlement plan/spec docs on that target, resolve the v0.27 binding compatibility table, verify SC-1 editor floor plus SC-10b / SC-28 / SC-28b rejected/losing recovery with executable evidence rather than tooling-block notes alone, and run manual smoke including both losing and rejected fixtures. Do not restart old G2-Slice-1 work from this docs branch, and do not start Slice G AI/ally settlement agency until v0.27 is reconciled, Gate 4 smoke evidence is recorded, and SC-29 / SC-30 / SC-31 / SC-32 / SC-33 ownership remains explicit rather than open-ended. |
| **Next Roadmap Gate** | After Settlement UI Cleanup, Slice G, final settlement gate, and smoke, run the new `ROADMAP.md` **8.EVAL Pre-8.5 War LLM + Diplomacy Refinement Evaluation**. It must recover/triage buried war-LLM improvements, battle/war narration and creative-command war uses, LLM cost/toggle implications, and `DESIGN_REFINEMENT.md` diplomacy candidates before Phase 8.5 begins. |
| **Blockers** | Settlement UI Cleanup implementation remains blocked until branch-target reconciliation, chosen-target SC-27 re-scan, v0.27 binding compatibility verification, SC-1 / SC-10b / SC-28 executable evidence, per-slice SC-22 Godot parse/load or explicit tooling-block accounting that keeps evidence rows open, SC-28 / SC-28b recovery evidence, Deferred Work Landing Ledger ownership check, and expanded 18-step Gate 4 smoke, including both rejected and losing smoke fixtures, are recorded. Commissioned-art renderer smoke remains blocked on art assets. |
| **Code Coverage** | ~71% (backend/) |

---

## Next Steps

### 1. Bug Fixes - COMPLETE

Sessions 1-5 + follow-up + offer lifetime refactor are COMPLETE. No OPEN PL items remain in the current fix scope.

| Priority | ID | Summary |
|----------|-----|---------|
| ~~P1 - CRASH~~ | ~~PL-30~~ | ~~Godot null instance crash on diplomacy button after missed proposal result~~ **FIXED** |
| ~~P1 - DESIGN~~ | ~~PL-31~~ | ~~Capital-loss instant defeat still live + broken regression test~~ **FIXED** |
| ~~P2 - UX~~ | ~~PL-26~~ | ~~Combat feels hopeless, no clear path to winning~~ **FIXED** |
| ~~P2 - UX~~ | ~~PL-27~~ | ~~Diplomacy interrupt contract broken~~ **FIXED** (hard-stop/soft-stop taxonomy + mailbox panel) |
| ~~P2 - UX~~ | ~~PL-28~~ | ~~No warning before defeat, sudden game over~~ **FIXED** |
| ~~P2 - UX~~ | ~~PL-32~~ | ~~Raw diplomacy labels can leak into popups~~ **FIXED** |
| ~~P2 - UX~~ | ~~PL-33~~ | ~~"status" blocked by dialogue guard~~ **CLOSED** (duplicate of PL-27, verified) |
| ~~P2 - UX~~ | ~~PL-34~~ | ~~Queued diplomatic proposals can expire unseen~~ **FIXED** (eliminated; mailbox inbox) |
| ~~P3 - QOL~~ | ~~PL-29~~ | ~~No new game / restart endpoint~~ **FIXED** |
 
**Actionable now (no blockers):**

1. **Memory and Pressure v2.4.3 — B-Hegemony + B-B1-lite + B-B3 + B-B7 COMPLETE (April 22-23, 2026).** B-Hegemony substrate is live (bloc geometry, `power_score` / `bloc_power`, `describe_hegemon_bloc`, `33 / 50 / 60` surfaced-band memory, `balance_of_europe_shifted` beats, non-France-hegemon threat suppression, AI bandwagon at `50%+`, coalition leadership `bloc_share_against`, transient/save-field wiring). B-B1-lite (commits `5a5a265` + `ad3b582` + `341b22a`) shipped `hegemony_target_mod` + acceptance decoupling + proposal-preview `hegemony` warnings without leaking B-B4's grievance/composite-floor work. B-B3 retired the last alliance_paradox surface seams: deleted legacy `alliance_paradox_popup.{tscn,gd,gd.uid}` from Godot, updated `dialog_manager.gd:21` layer-registry comment, cleared the obsolete `TestM10AllianceParadoxTodo` skip stub, and added 9 focused regressions in `tests/test_commitment_paradox_rename.py`. **B-B7** shipped the standard Make Amends active-redemption verb per spec §8.6.1 and its review follow-up is closed: `make_amends` is wired through `VALID_ACTIONS`, parser, mock-LLM keyword routing (`make amends`, `offer amends`, `amends with`, `amends to`, `repair relations`, `offer reparations`, `send reparations`), both `free_actions` mirrors, the diplomatic executor routing tuple, and `_execute_make_amends` in `backend/commands/diplomatic_executor.py`. Pre-validation covers all seven refusal paths (missing target, self-use, WAR/ARMISTICE, cooldown, insufficient DP, insufficient gold, no active strikes); on success, deduct `200g + 1 DP`, remove the strike per the §8.6 rule (oldest matured `decays_on_turn` first; else lowest-severity with oldest-creation-turn tiebreaker — reading the pair's full `record["strikes"]` so matured-but-not-yet-decayed strikes stay reachable), prune empty pair records, `diplomatic_reliability["France"] += 2` clamped `[-100, 100]`, `world.modify_nation_relation(France, target, +5)`, and set `reparations_cooldown[diplo_key] = current_turn + 10`. New `reparations_cooldown: Dict[str, int]` field on `WorldState` with round-trip. `amends_offered` now carries its own emitted `episode_id` plus the cleared strike lineage and deterministic deltas across campaign log, dispatch queue, and notification details. Result text combines a Talleyrand frame with the target court's Voice-Bible committed acknowledgment line for all four cast diplomats (Castlereagh / Hardenberg / Metternich / Einsiedel), with a chancery fallback for non-cast nations per `COMMITMENTS_PRESENTATION_SPEC` §10.3. `AMENDS_REFUSAL_DISPLAY` map + `ACTION_DISPLAY` / `OBJECTION_DISPLAY` / `DEFIANCE_DISPLAY` entries close the R7 contract. `dispatch.py` `partial_on_nation` fog-check key list extended with `actor_nation` / `target_nation` for the new event. `SAVE_FORMAT_REFERENCE.md` line 233 updated from **Planned (B-B7)** to **landed**. 27 new tests in `tests/test_make_amends.py` + 3 enforcement-suite count adjustments now pin the surface metadata as well. Full suite `8655 passed, 1 skipped` (was `8625 passed, 1 skipped`; +30 net). Ruff clean on every B-B7-touched file.
2. **Memory and Pressure v2.4.3 — DG-4 + C-lite closure COMPLETE.** DG-4 call-to-arms is direct-only with root attacker/defender allies and direct vassals only; `war_entry_ledger` records honored/refused/vassal paths; all commitment notice families now use the shared §8.1 routing metadata; `resolve_named_diplomat()` is live; stale paradox-resolution dispatch callbacks are removed; notification review opens the commitments ledger target; the rail caps same-turn commitments notices above the fold; `balance_of_europe` is the live ledger payload and the legacy `threat_coalition` compatibility payload is retired.
3. **Scale Readiness Phase 2 — COMPLETE (April 19, 2026).** Distance cache, indexed helper seam, live AI fog path, indexed autonomous-evaluation scope, target-ratio attack-path cleanup, live-visibility cache, the `enemy_ai.py` raw scan-conversion pass, and plan §2.1's 100-region synthetic benchmark (`tools/benchmark_distance_cache.py`, pinned by 3 scale tests in `test_scale_readiness_phase2.py`) have all landed suite-green. Audit gaps the April 19 closeout surfaced are captured in `docs/SCALE_READYNESS.md` §11 (Verification Delta).
4. **Map Readiness Closure Pass — Phase 3 COMPLETE (April 19, 2026).**
   - **§3.1 Nation config factory — DONE.** `backend/nation_config.py` ships `DEFAULT_NATION_DEFAULTS` (gold=800, actions=3, authority=60) as the fallback baseline; per-nation override dicts retain current France/Britain/Prussia/Austria/Saxony entries. Helpers `_resolve_gold` / `_resolve_actions` / `_resolve_authority` route through override → default. `validate_runtime_nation_support()` accepts a nation with only a capital + diplomat (no economy override), but still errors on missing capital or diplomat. `backend/models/marshal.py` ships `create_marshal_from_data()` + `create_marshals_from_data()` factories fed by new `FRENCH_MARSHALS_DATA` / `ENEMY_MARSHALS_DATA` data lists; the legacy `create_starting_marshals()` / `create_enemy_marshals()` are now one-line wrappers preserving exact skills, abilities, biographies, and the cross-nation relationship matrix (including the intentional Uxbridge ↔ Austria non-entries the original code left unset). `backend/models/diplomat.py` ships `DIPLOMAT_DEFINITIONS` + `create_diplomat_from_data()`; `STARTING_DIPLOMATS` + `create_starting_diplomats()` are factory-derived. New `tests/test_nation_config_factory.py` (15 tests) pins factory behavior, default fallback semantics, validator acceptance of default-only new nations, and preservation of explicit overrides for the current roster.
   - **§3.2 Shared topology endpoint — DONE.** Backend `GET /map_topology` returns authored static topology (`adjacent`, `terrain`, `region_type`, `is_capital`, `starting_controller`, `grid_position`) plus `nation_capitals` from `REGIONS_DATA` / `NATION_CAPITALS`. Godot `map.gd` no longer defines `const REGION_CONNECTIONS`; adjacency is populated at runtime via `set_region_topology()` after `main.gd` fetches the payload. New `tests/test_map_topology_endpoint.py` (7 tests) pins endpoint parity; `tests/test_map_consistency.py` now rejects renamed or inline hardcoded adjacency tables (`test_map_gd_has_no_hardcoded_connections`).
   - **§3.3 Centralize nation colors — DONE.** `utils.gd` NATION_COLORS is now single-source; `map.gd`, `war_detail_popup.gd`, and `war_status_panel.gd` read from `Utils.NATION_COLORS` + `Utils.COLOR_ENEMY_DEFAULT` / `Utils.COLOR_CONNECTION` instead of local dicts. New `tests/test_gdscript_color_centralization.py` guards against drift (3 tests).
   - **§3.4 Prompt / parser / validator hardcoding — DONE.** `prompt_builder._get_regions_list()` now derives from `map_data` → `world.regions` → `REGIONS_DATA` instead of a 19-region string literal. `parser.CommandParser` now computes its fallback enemy roster via `create_enemy_marshals()` and reads live rosters from `world.marshals` when available, instead of a hardcoded 8-name list. (`validator.py VALID_NATIONS` was already derived from `NATION_CAPITALS` in Phase 1.)
5. **Map Readiness Closure Pass — §4.1 Province Registry Schema COMPLETE (April 19, 2026).**
   - **Placeholder JSON bumped to `schema_version: 2`.** `godot-client/project-sovereign/assets/maps/session8_placeholder_provinces.json` now carries `province_id`, `unit_anchor`, `label_anchor`, `garrison_anchor`, `building_anchor`, `wired`, and `interactive` on every region entry. All 19 current regions are `wired: true` + `interactive: true` with per-feature anchors collapsed to `anchor` for now — commissioned Europe art will author real per-feature offsets.
   - **Renderer consumes the new schema.** `map_renderer_base.gd::_build_province_shapes()` parses all new fields onto `province_shapes`. `_lookup_region_from_color_map()` returns `""` for non-interactive regions. `_refresh_hover_state()` also skips non-interactive entries in the distance-fallback path so hover and click agree. `update_all_regions()` pre-filters `map_data` into a `wired_data` dict before populating gameplay state (controllers, visibility, marshals, fogged forces, garrisons) — unwired provinces still render via the static-visuals path but never receive gameplay data. `update_region()` short-circuits on unwired regions for consistency.
   - **Test coverage.** `tests/test_map_placeholder_assets.py` grew from 4 → 12 tests pinning schema version, `province_id` presence + uniqueness, all four anchor fields, `wired` / `interactive` flag presence + types, current-roster invariants, and renderer-side consumption of both the new flags and the new anchor fields. Four §4.1-specific tests in `tests/test_map_renderer_cutover.py` now pin `region_full_data = wired_data` plus the `wired` gate inside `update_all_regions()`, the unwired-dict erasure block inside `update_all_regions()`, the unwired early return inside `update_region()`, and the non-interactive skip in `_refresh_hover_state()`'s distance fallback.
6. **Map Readiness Closure Pass — §4.2 External Bitmap Loading COMPLETE (April 19, 2026).**
   - **Renderer gained bitmap-ingest seam.** `map_renderer_base.gd` now declares two subclass hooks (`_get_map_visual_bitmap_path()` + `_get_map_lookup_bitmap_path()`, both default `""`) and `_load_map_images() -> bool`. The loader now resolves imported bitmap assets through `ResourceLoader` / `Texture2D.get_image()` rather than `Image.load(res://...)`, rejects visual/lookup size mismatches, validates that lookup-map colors match `province_color_lookup`, and on success binds `visual_map_texture` + `province_lookup_image` while overriding `map_origin = Vector2.ZERO` + `map_canvas_size = bitmap.get_size()` so authored anchors are interpreted in bitmap-pixel coords.
   - **Fallback preserved, but failures stay loud.** `_build_map_textures()` calls the loader first and returns early on success; on failure the existing circle-generation block runs unchanged. Explicit bitmap opt-in failures now `push_error()` once per unique message instead of spamming every `_ready()`. `map.gd` does NOT override the bitmap hooks, so the 19-region placeholder scene always runs on circles.
   - **Hit-test path unchanged.** `_lookup_region_from_color_map()` still reads `province_lookup_image.get_pixel()` keyed into `province_color_lookup`, with the §4.1 `interactive`/`wired` gates intact.
   - **Test coverage.** `tests/test_map_renderer_cutover.py` now pins the hook declarations, exported-build-safe resource loading, runtime lookup-color validation, failure latching, and loader ordering inside `_build_map_textures()`. `tests/test_map_placeholder_assets.py` still pins that placeholder `map.gd` never opts into bitmap mode. New `tests/test_map_bitmap_contract.py` adds fixture-driven behavioral coverage for missing-file fallback, lookup-color rejection, size mismatch rejection, and hit-test round-trips with `map_origin = Vector2.ZERO`.
7. **Map Readiness Closure Pass — §4.3 Color-Map Validator COMPLETE (April 19, 2026).**
   - **Tool shipped.** `tools/validate_province_map.py` is a standalone offline acceptance gate for commissioned art deliveries. Invoke as `.venv\Scripts\python.exe -m tools.validate_province_map --registry <json> [--visual <png> --lookup <png>]`. Stdlib-only (no Pillow / no project imports beyond the registry JSON), so it can run in CI without backend dependencies and before any backend code loads.
   - **Six failure codes, two severities.** Errors: `SENTINEL_COLLISION`, `DUPLICATE_LOOKUP_COLOR`, `SIZE_MISMATCH`, `MISSING_PROVINCE`, `INSUFFICIENT_COVERAGE` (default minimum 50 pixels per province), `UNMAPPED_COLOR` (with pixel count and sample `(x, y)` coordinate). Warning: `TINY_ISLAND` (each connected color island, mapped or not, with `1 <= count < tiny_island_threshold`; default threshold 5). Sentinel pixels (`no_province_color`) never produce findings. Errors collected per-pass instead of bailing on the first failure, so a commissioned-art delivery triages in one report.
   - **Differs from the §4.2 runtime loader on purpose.** `SIZE_MISMATCH` mirrors the runtime check but reports both sizes for art-pipeline triage. `UNMAPPED_COLOR` collects ALL strays + counts where the runtime stops at the first. `TINY_ISLAND`, `INSUFFICIENT_COVERAGE`, `MISSING_PROVINCE` (distinct from "exists but tiny"), and `DUPLICATE_LOOKUP_COLOR` have no runtime equivalent.
   - **CLI contract.** `--registry` required; `--visual` + `--lookup` paired or omitted (registry-only mode is the cheapest gate, runs without any PNG). Empty registries now fail fast in that mode. `--min-coverage-pixels` and `--tiny-island-threshold` tune the two thresholds per delivery. `--json` emits `{ok, error_count, warning_count, failures[]}` for CI; `--strict` promotes warnings to a non-zero exit. Exit codes: `0` pass / `1` validation failure / `2` bad input.
   - **PNG decoder scope.** Pure-Python (`zlib` + `struct`); supports 8-bit RGB (color_type 2) + RGBA (color_type 6) with all five PNG scanline filters (None / Sub / Up / Average / Paeth). The visual PNG size check is header-only to avoid wasteful full-image decode; the lookup PNG path still fully decodes and now wraps malformed IHDR payloads, truncated chunk bodies, and corrupt IDAT streams as clear `PNGDecodeError`s. Pillow intentionally NOT a dep — stays inside the project's existing `requirements.txt`.
   - **Test coverage (29 tests, `tests/test_province_map_validator.py`).** Registry checks (placeholder passes; sentinel collision; duplicate colors; loader rejects malformed inputs and empty registries); image checks (clean baseline; size mismatch; missing province; insufficient coverage; connected tiny islands still fire when repeated specks of the same stray color exceed the threshold in aggregate; high-pixel-count unmapped stays error-only; sentinel pixels ignored; alpha is dropped before comparison; RGB-only PNGs decode); CLI exit codes 0/1/2 + `--json` + `--strict`; PNG decoder rejects interlaced + non-PNG signatures, supports multiple IDAT chunks, rejects malformed IHDR payloads / corrupt streams, and round-trips a 5-row RGBA fixture exercising all five filter types.
   - **Verification.** Focused map suite: **65 passed** (`tests/test_map_renderer_cutover.py tests/test_map_placeholder_assets.py tests/test_map_bitmap_contract.py tests/test_province_map_validator.py -q`). Full Python suite: **8487 passed, 2 skipped** (was `8453`). Ruff clean on the new files. The shipped placeholder JSON passes registry-only checks (pinned by `test_placeholder_registry_passes_registry_only_checks`).
   - **Suggested next cold-start sequencing:** §4.4 (unwired province support — grey-tint + "(not yet in play)" hover copy now that the schema carries the flag). A fresh session only needs CLAUDE.md + this STATUS.md + `SCALE_READINESS_PLAN.md` §4.
8. **Map Readiness Closure Pass — §4.4 Unwired Province Support COMPLETE (April 19, 2026).**
   - **Overlay seam in `map_renderer_base.gd`.** Three coordinated additions: (a) constants `UNWIRED_GREY_COLOR := Color(0.32, 0.32, 0.34, 1.0)`, `UNWIRED_GREY_BLEND: float = 0.7`, `UNWIRED_TOOLTIP_SUFFIX := "(not yet in play)"` pin the visual contract in one place; (b) `_is_region_wired(region_name) -> bool` + `_unwired_lookup_keys() -> Dictionary` resolve the gate through `province_shapes` and default to wired when a region is unknown, preserving legacy callsites; (c) `_apply_unwired_grey_overlay(visual_image, lookup_image)` stamps a straight `base.lerp(UNWIRED_GREY_COLOR, UNWIRED_GREY_BLEND)` over every visual pixel whose lookup key belongs to an unwired province, with size-mismatch + empty-set short-circuits keeping the placeholder path zero-cost.
   - **Overlay runs on BOTH texture-build paths.** `_build_map_textures()` now calls the overlay AFTER `province_lookup_image = color_map` but BEFORE `visual_map_texture = ImageTexture.create_from_image(visual_image)` in the circle fallback, and `_load_map_images()` does the same for the bitmap path (after `province_lookup_image = lookup_image`, before texture creation). Unwired tint therefore applies uniformly regardless of whether art is commissioned or dev-mode circles.
   - **Click gate lives in `MOUSE_BUTTON_LEFT`.** The handler still resolves `clicked_region` via `_lookup_region_from_color_map(...)` (then the `hovered_region` fallback), but now short-circuits on `not _is_region_wired(clicked_region)` BEFORE emitting `region_clicked`. The existing `interactive` gate inside `_lookup_region_from_color_map()` is untouched — hover identification for unwired-but-interactive provinces keeps working.
   - **Tooltip dispatch has a dedicated unwired branch.** `_draw()` evaluates `elif hovered_region != "" and not _is_region_wired(hovered_region):` BEFORE the existing `region_full_data.has(hovered_region)` branch, because §4.1's `update_all_regions()` deliberately excludes unwired regions from `region_full_data`. `_draw_unwired_region_tooltip()` renders the province name + `UNWIRED_TOOLTIP_SUFFIX` against a distinct dim panel so authors never mistake an unwired province for a fogged one.
   - **Test coverage (16 tests).** `tests/test_map_renderer_cutover.py` gains 10: constants pinned, `_is_region_wired` contract, `_apply_unwired_grey_overlay` body shape, `_unwired_lookup_keys` construction, overlay-before-texture ordering in both paths, click-gate precedence (guard before `emit`), `_draw()` branch order (unwired before `region_full_data.has`), the unwired tooltip helper renders both lines, and a negative assertion that `_lookup_region_from_color_map()` never gates on `wired`. New `tests/test_map_unwired_overlay.py` adds 6 behavioral fixture tests: constants mirror, all-wired no-op, selective blend, pure-tint target, sentinel ignored, and a source-level guarantee that `_unwired_lookup_keys()` cannot emit the sentinel by construction (it only iterates `province_color_lookup`, which `_build_province_shapes()` never seeds with the sentinel).
   - **Verification.** Focused map suite: **94 passed** (`tests/test_map_renderer_cutover.py tests/test_map_placeholder_assets.py tests/test_map_bitmap_contract.py tests/test_map_unwired_overlay.py tests/test_map_consistency.py tests/test_map_topology_endpoint.py tests/test_province_map_validator.py`). Full Python suite: **8503 passed, 2 skipped** (was `8487`). Ruff clean on the modified + new files.
   - **Suggested next cold-start sequencing:** Map readiness is now art-blocked only. The last remaining map-readiness work is commissioned art + final renderer smoke validation. A fresh session working on diplomacy should pick up the Memory and Pressure v2.4.3 implementation slices directly.
9. **Memory and Pressure v2.4.3 — Block 3 folded; implementation closure current.** `docs/audits/MP_V243_BLOCK1_DOC_CLEANUP.md` and `docs/audits/MP_V243_BLOCK2_SUBSTRATE.md` are complete. `docs/audits/MP_V243_BLOCK3_BLOC_NAMING.md` is SUPERSEDED — its bloc-naming contract was folded into `COMMITMENTS_PRESENTATION_SPEC.md` §8.1a, its per-band voice contract was folded into `DIPLOMAT_VOICE_BIBLE.md`, and its CF1-CF4 closure items have now landed in their owning slices. No separate Block 3 consumption pass is required.

## Real Map Readiness Gate

**Definition:** "Real map ready" means the project can safely start a commissioned Europe-map integration or a full-Europe wiring pass without knowingly carrying unresolved scale or asset-pipeline blockers. It does **not** mean only "Phase 2 is done," and it does **not** mean only "art has arrived."

**Do not call the project real-map ready until all of the following are true:**

1. **Phase 2 spatial-index conversion is complete.**
   - `backend/ai/enemy_ai.py` has no remaining scale-sensitive hot-path scans that still depend on broad `world.marshals.values()` / `marshals.values()` iteration where indexed region helpers are the intended path.
   - Full Python verification stays green after the final conversion batch.

2. **Scale-facing nation / region data flow is fully data-driven.**
   - Adding nations or regions no longer depends on lingering hand-authored factory duplication or shell-sized prompt / parser assumptions.
   - Prompt/parser fallback strings, nation-color ownership, and adjacency ownership are now data-driven. Nation/runtime config factory work (§3.1) is the last remaining Phase 3 gap before this gate is satisfied.

3. **Frontend/backend topology has one authoritative source.** ✅ DONE (April 19, 2026 — §3.2).
   - `map.gd` no longer carries a hardcoded gameplay adjacency graph. Shared topology comes from backend `GET /map_topology` (authored from `REGIONS_DATA`) as described in `SCALE_READINESS_PLAN.md` §3.2.

4. **The renderer has a production province registry schema.** ✅ DONE (April 19, 2026 — §4.1).
   - Province metadata includes stable `province_id`, separate anchors for unit / label / garrison / building placement, and explicit `wired` / `interactive` flags. Placeholder JSON is at `schema_version: 2`; renderer parses all new fields and gates hover/click/gameplay-state on `interactive` / `wired` respectively.
   - Placeholder-only `anchor` + `radius` data is no longer the limiting runtime contract for Europe-density map content.

5. **The renderer can load external bitmap assets.** ✅ DONE (April 19, 2026 — §4.2).
   - `map_renderer_base.gd` now exposes `_get_map_visual_bitmap_path()` / `_get_map_lookup_bitmap_path()` hooks plus `_load_map_images()` loader; `_build_map_textures()` prefers bitmaps when both paths resolve and fall back to circle generation otherwise. Hit detection still goes through `province_lookup_image.get_pixel()` keyed into `province_color_lookup` as §4.1 established.
   - Placeholder circle generation remains available as the dev-mode fallback (the placeholder scene never opts in to bitmap mode), but it is no longer the only renderer path.

6. **Bitmap validation exists and runs before art integration.** ✅ DONE (April 19, 2026 — §4.3).
   - `tools/validate_province_map.py` checks dimension match, unknown colors, missing provinces, sentinel misuse, duplicate lookup colors, insufficient coverage, and connected tiny pixel islands. CLI emits human-readable or `--json` reports with exit code `0`/`1`/`2`; `--strict` promotes warnings.
   - The validator is stdlib-only (no Pillow), so it runs in CI and before any backend code loads. The shipped placeholder JSON passes all registry-only checks.

7. **Unwired province support exists in the runtime contract.**
   - The renderer can show visible-but-not-yet-playable provinces in a greyed-out / non-interactive state.
   - Hover/click behavior and `update_all_regions(map_data)` explicitly ignore unwired provinces for gameplay.

8. **Commissioned-art integration and smoke verification are closed once assets exist.**
   - After art delivery, the project still needs the art-backed renderer cutover plus final Godot smoke validation.
   - This step is the one genuinely blocked on art assets; the prerequisites above are not.

**Important routing clarification:** completing Scale Readiness Phase 2 should move the project from "engine hot path still incomplete" to "ready for the non-art map-readiness closure pass." It should **not** be read as "safe to start commissioned Europe map integration immediately."

**Complete:**

- **Scale Readiness Phase 0 — Design Gates + Implementation-Closure Pass.** COMPLETE (April 17, 2026; DG-4 amended April 25). `DG-1` current 1805 draft roster = 13 independent nations with 20+ headroom, but that roster is authored scenario content rather than an engine cap; `DG-2` bilateral diplomacy with force-expand salience rules, weighted-sum salience score, and locked 5-row expanded cap; `DG-3` supply lines deferred; `DG-4` direct-only bilateral call-to-arms with no transitive cascade, qualifying-treaty list locked (`ALLIANCE`, `DEFENSIVE_ALLIANCE`, vassal), concrete DG-4 event families (`call_to_arms_refused_offensive`, `call_to_arms_refused_defensive`, `call_to_arms_honored_costly`, `war_entry_ledger`); `DG-5` no mandatory hard victory condition for Europe-map readiness, with any future objectives authored per scenario; `DG-6` scenario-configured pacing with `scenario_schema_version: 1`, hybrid `base_ap.by_nation` + `base_ap.by_tier_default`, optional `objectives_profile`, and structured `cascade_profile`; `DG-7` categorized dispatch with priority escalation. Cross-cutting taxonomy is now canonical and single-sourced to `SCALE_READINESS_PLAN.md` §"Phase 0 Cross-Cutting Taxonomy": `power_tier` is authored scenario data with enum `major / secondary / minor`, never runtime-derived; runtime numeric strength signals use a separate `power_score` field. Older `great_power / secondary_power / minor_power` language in historical design docs carries supersede markers pointing to the canonical section; current settlement specs use `major / secondary / minor`.
- **Scale Readiness Phase 1 — Test Safety Net.** COMPLETE (April 17, 2026). 11 new tests (8 nation config + 3 adjacency), all hardcoded `== 19` removed from test assertions, validator VALID_NATIONS derives from NATION_CAPITALS.
- **Scale Readiness implementation-closure clarification pass.** COMPLETE (April 17, 2026). `SCALE_READINESS_PLAN.md` now explicitly requires authored scenario records (`player_nation`, `home_capital`, `player_sphere`, `nations`, `counts_for_strategic_power`), defines `protectorate` as a DG-2 subject state but not a DG-4 auto-entry state, locks DG-2's shared salience helper + tiebreak order, aligns DG-4 with a later surfaced attacker-side ally-entry seam, removes any implied 13-nation engine cap, and makes hard campaign objectives optional scenario content rather than a required Europe prototype dependency.

**Blocked:**

- **Session 8 Renderer — final art-backed cutover.** Commissioned art-backed renderer swap and Godot smoke validation. Blocked on art assets.
- **Real map readiness final sign-off.** Blocked on both the remaining non-art map-readiness gate items above and, after those land, the commissioned art-backed cutover.

**Audit context:** `docs/SCALE_READYNESS.md` is the historical snapshot of the original 17-finding Europe-scale audit (audit date April 16, 2026). Current non-art map-readiness closure state is tracked in the "Actionable now" block above (§§3.1-3.4 + §§4.1-4.4 are all DONE). Treat the `SCALE_READYNESS.md` "NOT DONE" entries for §§3.1, 4.1-4.4 as frozen audit context, not current routing — the `SCALE_READINESS_PLAN.md` per-item contract + `STATUS.md` closure entries are the source of truth.

**Next diplomacy workflow:** **Slice B3 lifecycle (per-turn staying-power + war-entry seam wiring + archive compaction + retention + full-Europe fixtures).** Slices A1 + A2 + A3 + B1 + B2 (ordering guard + battle emitter wiring + non-battle emitters) are landed. B2 non-battle emitters shipped May 2-3, 2026: `accrue_occupation_event(...)` for the four kinds (`enemy_region_captured` 20 / `enemy_capital_captured` 40 / `allied_region_restored` 15 / `liberated_region_restored` 15; `treaty_transfer` is logged with 0 points per spec §9.2 line 641), `emit_capture_occupation_event(...)` capture-path wrapper (classifies via `NATION_CAPITALS` and `get_starting_controllers()`), `accrue_support_event(...)` for gold/subsidy/AP/manpower/access/supply with per-`(war_id, supporter, support_kind)` access/supply cap of 5 raw and deterministic episode-id dedupe, and `resolve_british_subsidy_war_id(...)` (`unique_eligible` / `matching_coalition_target` / `highest_overlap` / `oldest_sequence` / `unattributed_subsidy`). Wired call sites: `world_state.capture_region()`, `world_state._ratify_treaty()` (`gold_lump` support + `territory_cede` allied restoration + vassal liberation per-region), `world_state._process_treaty_clauses()` (per-turn gold/manpower/AP), `coalition._process_british_subsidy()`. 33 new tests in `tests/test_war_contribution_scores.py`; verification `9490 passed, 1 skipped`; ruff clean. Active settlement work continues from `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` Slice B "B3 lifecycle, retention, and full-Europe fixtures" and `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §9.5 + §7.5.

**Peace Deals deferred carry-forward gate:** CLOSED by the approved Peace Deals umbrella spec. The "Deferred Carry-Forward Checklist" in `docs/PEACE_DEALS_UMBRELLA_SPEC.md` assigns or explicitly defers WB-D bargain presentation, response routes, bargain icons, fulfillment/breach badges, region-observer witness scope, scope-branched witness copy, and callback/aftermath architecture.

**Deferred-item routing plan (reviewed Apr 26 after WPS-A audit follow-up):**

| Deferred item | When to do it | Why / gate |
|---------------|---------------|------------|
| D3 per-row bloc stamps / member badges | **DONE Apr 25 as the pre-Peace polish pass.** Keep future work limited to smoke/playtest copy or color tweaks unless a new readability problem appears. | Live payload is transient `nations[*].bloc_stamp`, never serialized, and reuses `describe_hegemon_bloc(...)`. Priority is `[Coalition Member] > proper bloc name > descriptive bloc > Vassal > Neutral`. |
| D1 advisory-first strategic focus + deeper AI integration | Later Nation Agendas / Motive Legibility or Talleyrand Desk work, not before Peace Deals. | This is strategic behavior and advisory framing, not a missing closure item from Memory and Pressure. It needs a spec that owns AI motives and recommendation surfaces. |
| D2 non-France-hegemon / per-target coalition generalization | Later scale or scenario-generalization pass, or inside a Peace Deals spec only if that spec requires per-target pressure for settlement logic. | Current v0.1 Balance pressure is honest for the player-nation target. Generalizing the scalar is wider than badges and should not be pulled forward for presentation polish alone. |
| WB-D bargain presentation, response routes, bargain icons, fulfillment / breach badges | During War Bargains WB-D inside the Peace Deals track, after Bilateral Peace Hardening, War Purpose + Score Semantics, and WB-A/WB-B/WB-C are specified and implemented. | These surfaces depend on live bargain records and settlement/war-purpose semantics. Doing the presentation layer before the mechanic would create placeholder UI with no durable state behind it. |
| Region-observer witness scope and scope-branched witness copy | During WB-D or the same Peace Deals slice that introduces bargain/claim observer state. | `region_observer` is intentionally inactive until the bargain/claim store exists. The witness copy should branch on real bargain/claim relationships, not invented presentation-only context. |
| Richer callback / N+1 aftermath architecture | Only if Peace Deals / War Bargains playtest proves same-turn notices are too flat for bargain breach, fulfillment, or settlement fallout. | Memory and Pressure closed with same-turn routing and advisory review targets. Delayed callbacks should be justified by new Peace Deals events with real follow-up choices. |
| Retroactive campaign-log renaming and compound member-list bloc names | Archive / expansion polish after D3, not part of Peace Deals entry criteria. | These improve historical display texture but do not unblock diplomacy mechanics, peace terms, or player decisions. |

**Current Session 7 progress:** COMPLETE. `backend/nation_config.py` now centralizes scenario/runtime nation defaults, non-France campaigns preserve their player nation through world init + `/new_game` reset paths, diplomacy/advisory/template/defiance flows now derive state and proposal ownership from `world.player_nation`, enemy AI scale-sensitive contact scans route through cached fog-aware helper seams, and modding/scenario validation now fails unsupported nation rosters before load.

**Current Scale Readiness Phase 2 progress:** COMPLETE. `backend/models/world_state.py` ships deque-based `get_distance()`/`find_path()`, a symmetric distance cache plus explicit invalidation seam, AI-safe indexed region helpers, and a live-visible-region cache that invalidates with marshal-index rebuilds. `backend/ai/enemy_ai.py` refreshes marshal indexes at evaluation-scope boundaries, guards direct-entry helpers against stale indexed reads, routes non-player nation contact queries through live nation-perspective visibility while letting long-range P7/stagnation movement steer off hostile-controlled regions instead of hidden marshal positions, enters indexed scope for `decide_single_action()`, uses indexed marshal-priority helpers for turn ordering, and covers the late artillery / coordination helper band plus the ally-support / fortification / stagnation / attack-ratio / homeland-defense / undefended-capture / consolidation / default-retreat follow-up band with indexed same-region / adjacent-region lookups. `enemy_ai.py` has `0` remaining direct `world.marshals.values()` / `marshals.values()` scans. Plan §2.1's 100-region synthetic benchmark now ships as `tools/benchmark_distance_cache.py` (10x10 4-neighbor grid, ~34x cached vs. uncached on typical hardware, invariance contract asserted) and is pinned by three new scale tests in `tests/test_scale_readiness_phase2.py` (now 28 tests, all green). Suite-level regression verification remains green (`8410 passed, 2 skipped` pre-benchmark; incremental Phase 2 file verified post-benchmark).

**Current Session 8 progress:** Cutover slices 1-3 + §§4.1-4.4 COMPLETE. The map renderer now builds shared scene-node layers behind `map_renderer_base.gd`, keeps the existing `map.gd` data wrapper and `update_all_regions(map_data)` contract stable for `main.gd`, includes a placeholder province-definition asset plus hidden color-map lookup path for the current 19-region map, isolates the map world inside a `SubViewport` with native `Camera2D` zoom/pan plus world-bound clamping, carries the production province-registry schema (`province_id`, per-feature anchors, `wired`, `interactive`), can ingest imported bitmap assets through an exported-build-safe loader with runtime lookup-color validation plus circle fallback, ships an offline color-map validator (`tools/validate_province_map.py`, 29 tests) that gates commissioned-art deliveries on sentinel collisions, duplicate colors, dimension mismatches, missing/insufficient province coverage, connected tiny pixel islands, and unmapped colors, and paints unwired provinces with a grey-tint overlay + dedicated "(not yet in play)" tooltip while short-circuiting clicks before `region_clicked` is emitted. All non-art Session 8 work is closed. Remaining art-dependent work is the commissioned art-backed renderer swap and final Godot runtime smoke validation.

**Routing note:** later references in this file to older "Session 7", "Session 8", or "Session 8A" Phase 8 diplomacy milestones are archival implementation history. They do not override the active post-bug routing above, which is currently: (1) Scale Readiness Phase 2 — DONE, (2) non-art map-readiness closure pass (§§3.1-3.4 + §§4.1-4.4) — DONE, (3) art-backed renderer cutover — blocked on art assets. Real-map readiness as a whole is therefore art-blocked only.

**Implementation sessions in current order:**

| Session | Scope | Items | Status |
|---------|-------|-------|--------|
| Session 1 | Stability + defeat truth | `PL-30`, `PL-31` | **COMPLETE** |
| Session 2 | Diplomacy interrupt contract | `PL-27`, `PL-34`, `PL-33` duplicate check | **COMPLETE** |
| Session 2 follow-up | Mailbox inbox + queue elimination | `PL-27`/`PL-34` hardening | **COMPLETE** |
| Session 2 refactor follow-up | Current-turn diplomatic offer lifetime | `PL-27`/`PL-34` follow-up | **COMPLETE** |
| Pre-Session 3 | Informational notices + light UI polish | `docs/INFORMATIONAL_UI_PLAN.md` | **COMPLETE** |
| Session 3 | Diplomacy display contract | `PL-32` | **COMPLETE** |
| Session 4 | First-hour pressure cleanup | `PL-28`, `PL-26` | **COMPLETE** |
| Session 5 | Restart flow | `PL-29` | **COMPLETE** |
| Session 6 | Response and popup contract hardening | `/command` response pipeline, typed dialogue migration, popup routing registry, turn-manager popup flush workaround cleanup, `/command` follow-up reduction | **COMPLETE** |

### 2. Completed Diplomacy Foundations (reference for future planning)

These changes are live. Treat them as the baseline when planning follow-up diplomacy work.

| Foundation | What shipped |
|------------|--------------|
| Diplomacy interrupt contract | `PL-27` split hard-stop vs soft-stop diplomacy, stopped ordinary commands from being blocked by envoy decisions, and moved recovery onto typed flows instead of parser-only fallbacks. |
| Envoys inbox / mailbox flow | Session 2 follow-up shipped the browsable Envoys inbox/mailbox panel, `GET /mailbox`, `POST /mailbox/activate`, stable mailbox identity, and consolidated pending-count ownership under `dialogue_manager.get_mailbox_count()`. |
| Queue elimination + offer lifetime refactor | `world.diplomatic_queue` is gone. The follow-up refactor replaced cross-turn mailbox persistence with current-turn envoy items: `Not Now`, same-turn reopen, and end-turn lapse instead of silent long-lived queue state. |
| Diplomacy display contract | `PL-32` centralized proposal/clause display ownership in backend formatters (`backend/display_names.py`) so popups and recovery payloads no longer maintain divergent token maps. |
| Response / popup refactors | Session 6 moved `/command` onto `build_base_response()`, finished typed dialogue migration for remaining diplomacy popups, and replaced hand-ordered modal routing with the popup registry/dispatcher path in `main.gd`. |

**Planning note:** do not assume the old pre-mailbox model still exists. Diplomacy refinement should build on Envoys inbox + same-turn lapse + backend-owned popup labels, not on the removed `diplomatic_queue` / cross-turn mailbox behavior.

### 3. Architecture Hardening (before full-map work)

GPT audit confirmed the codebase is "fragile but manageable" at 19 regions but NOT ready for 80-100 region expansion. These items need a plan before full-map implementation starts:

| Item | Summary | Current Home |
|------|---------|-------------|
| Map renderer replacement | Circle-based prototype won't scale | ROADMAP.md (art-blocked) |
| `/command` response pipeline | **FIXED Apr 12, 2026 (Session 6 slice 1).** Main path now starts from `build_base_response()` with explicit popup/notification deferral flags. | This session |
| AI fog-aware queries | **FIXED Apr 12, 2026 (Session 7).** Scale-sensitive AI contact scans now route through cached fog-aware helper seams. | This session |
| Hardcoded nation defaults | **FIXED Apr 12, 2026 (Session 7).** Shared nation config now owns runtime defaults and non-France campaign resets. | This session |
| Popup routing registry | **FIXED Apr 12, 2026 (Session 6 slice 3).** `main.gd` now routes modal response precedence through ordered registries plus a shared dispatcher. | This session |
| Typed dialogue migration | **FIXED Apr 12, 2026 (Session 6 slice 2).** Remaining diplomacy popups now route through typed endpoints/actions, including a dedicated typed objection path. | This session |

**Needs:** A consolidated pre-expansion plan that sequences these items after Sessions 1-5. `docs/SCALE_READYNESS.md` now holds the current risk register and smaller-map assumption list for that planning pass. The GPT audit priority roadmaps in `docs/GPT_AUDIT_PLAN_RESULTS.md` now cover both the broader architecture audit and the focused diplomacy attention / legitimacy audit. No item from this list moved earlier as a full prerequisite for the current bug sessions.

**Post-bug architecture sessions:**

| Session | Scope | Items |
|---------|-------|-------|
| Session 6 | Response and popup contract hardening | `/command` response pipeline **COMPLETE**; typed dialogue migration **COMPLETE**; popup routing registry **COMPLETE**; turn-manager popup flush workaround cleanup **COMPLETE**; `/command` follow-up reduction **COMPLETE** |
| Session 7 | Scale-sensitive backend hardening | AI fog-aware queries, hardcoded nation defaults, config-completeness and large-scenario validation tests **COMPLETE** |
| Session 8 | Renderer cutover prep and replacement | Map renderer replacement on the current 19-region map or placeholder assets; keep `update_all_regions(map_data)` stable during swap |

These are existing audit items broken into implementation order. They stay after the current bug sessions and before any full-map expansion work.

### 4. Design Refinement (next diplomacy spec queue)

`docs/DESIGN_REFINEMENT.md` is now a post-fix planning doc, not a blocked-during-bugs list. The old prerequisites are complete: `PL-27`, `PL-34`, `PL-32`, the Envoys inbox/mailbox follow-up, the current-turn offer lifetime refactor, and the Session 6 response/popup refactors are all live. The next diplomacy work should be spec-first.

| Order | Spec Track | Bundles / Source Items | Note |
|-------|------------|------------------------|------|
| 1 | Memory and Pressure v2.4.3 | `R160`, `R119` | First diplomacy follow-up closure block. Blocks 1 and 2 are complete; Block 3 is SUPERSEDED; DG-4 reliability, C-lite presentation closure, the April 25 post-closeout smoke fixes, and D3 Balance/ledger row stamps are now live. Remaining work is commissioned-art smoke outside this diplomacy gate. |
| 2 | Bilateral Peace Hardening | separate peace UX, bilateral peace term ownership, promise-breach warnings, peace-preview clarity | Must land before any ally-aware settlement flow OR before war bargains. **Needs dedicated spec.** |
| 3 | War Purpose + Score Semantics | War Objectives + Ticking War Score, Vassalage Power Cap, Forced Alliance, Liberation | Define why wars start, what score means, and what settlements can legitimately do. Do **not** bundle this directly with common peace. **Needs dedicated spec.** |
| 3.5 | War Bargains | `R151`, full `war_bargain` mechanic split out of `Reliability + Commitments` v1.0 in April 16 rescope | The bilateral named-enemy promise mechanic. `docs/WAR_BARGAIN_SPEC.md` v1.0. All slices COMPLETE: WB-A (data + creation), WB-B (lifecycle), WB-C (war-entry contract + AI rules + `repudiate_bargain`), WB-D (presentation: commitments routing, notifications, witness scope, voiced templates, response routes, ledger badges). **Depends on items 1-3.** ~160 tests. |
| 4 | Ally Participation + Common Peace | ally beneficiaries, contribution / consultation rights, common peace routing, settlement fallout | Post-bargains track. `docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` and implementation plan own the full-Europe handoff. **Slice A1 foundation and Slice A2 war-entry threading are landed.** Next work is Slice A3 merge/archive/leader invariants. |
| 5 | Nation Agendas + Motive Legibility | `R155`, `R156`, `A3`, `R123`, `R124` | Make nations feel nation-smart, not threshold-smart: agendas, diplomacy-vs-war choice, visible motives, and isolation behavior. **Needs dedicated spec.** |
| 6 | Talleyrand Desk + Explanation Layer | `R131`, `R132`, `R17d`, `R17e`, `R17f`, `R157`, `R159` | Unify cooldown warnings, relationship/vassal trends, mission projections, and explanatory advisory text into one desk/explanation surface. **Needs dedicated spec.** |
| 7 | Economic Diplomacy | `R161` plus B4 diplomacy-facing gold-sink candidates | Build the non-coercive diplomatic economy around reciprocal trade, subsidies, and pressure, not disconnected one-off features. **Needs dedicated spec.** |

**Peace Deals spec gate (May 2):** BPH-A through BPH-D, WPS-A through WPS-D, and WB-A through WB-D are landed. Ally Participation/Common Peace has `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` and `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` covering full-Europe scale. **Slice A1 foundation gate and Slice A2 war-entry threading are landed:** A1 shipped settlement containers, save/load defaults, empty-safe indexes, cache invalidation, cached-helper elimination refactor, invariant assertions, and the 20-active-`war_instance` synthetic fixture; A2 shipped `war_id` create/reuse/attach ownership across inventoried WAR-entry seams, with review follow-up commit `497791d` closing cascade/debug/armistice/counter-bargain hard-stop gaps. Full pytest suite at `9350 passed, 1 skipped`; ruff clean. Next is Slice A3 merge/archive/leader invariants.

**Audit call (Apr 13):** the existing conversational diplomacy wizard should remain the home for normal diplomacy, separate peace, bilateral commitment review, and the future bilateral peace-hardening pass. Common peace, ally beneficiaries, and conference-style settlement allocation should route through a dedicated wartime settlement flow instead of being overloaded into the nation -> proposal -> terms loop.

**Audit amendment (May 5):** typed diplomacy is no longer an acceptable primary path for common peace. The diplomacy wizard should be the entry point that opens the dedicated wartime settlement flow. The current gap is routing, not design intent: wizard `open_settlement` must stage `settlement_confirm`, and the backend wizard availability check must recognize default-start WAR pairs through the same lazy backfill used by `propose_common_peace`.

**Common-peace UI audit expansion (May 5):** war-score HUD/detail surfaces also need settlement-aware polish. Clicking a bilateral war-score row opens `war_detail_popup.gd` and then `[Negotiate Peace]` opens the diplomacy wizard, so the wizard fix should make the bilateral path usable. But multi-participant wars are still presented as bilateral rows from `diplomatic_states`, with `war_instance_id` only attached opportunistically; there is no explicit "Open Settlement" CTA on the war-detail popup, no coalition/whole-war settlement CTA in the coalition detail view, and the coalition detail currently offers only `Target X` buttons for non-leader members. Backend `war_status.py` contribution rows are empty for default-start WAR pairs until a war_instance is created, which can make the settlement standing tooltip look absent at exactly the moment the player is deciding whether to negotiate. Ledger recent-settlement rows are wired, but `diplomatic_ledger.gd` still renders `terms_summary[0]` and expanded term `type` values directly, so raw `territory_cede` / underscored settlement codes can leak there even after dispatch/campaign-log one-liners were humanized. Next closure should cover F1 wizard, war-score detail handoff, coalition detail handoff, and ledger term humanization together.

**Follow-up note:** `R162` (AI ultimatums to player) is no longer blocked by the old attention contract, but it should still wait until the commitment and agenda specs above exist. It adds interruption surface before the underlying diplomacy has enough political weight.

**Mechanical substrate note (Apr 15):** the live diplomacy layer now records treaty rupture as a remembered political event when war shatters an active commitment, including the injured party, breach reason family, witness scope, actor personality, and pre/post reliability. The declare-war objection path also previews the reliability drop before confirmation. This is not full `Reliability + Commitments` implementation yet; it is targeted hardening so the current engine produces more legible material for the downstream commitments/presentation work.

**Mechanical substrate follow-up (Apr 16):** the commitments-substrate audit's remaining high- and medium-severity gaps are now fixed in-engine. Shipped:

- **Cascade attribution (H-1):** forced cascade ruptures are classified `end_reason_family=obsolescence_or_external` with `fault_nation=aggressor`; cascaded nations no longer lose reliability for treaties they did not voluntarily break (Â§9.9.B).
- **`episode_id` threading (H-2):** `world.next_episode_id` serialized; one ID is allocated per root-cause declaration / break / paradox resolution and shared across all breach, cascade, and witness-strike emits so `C3` aftermath and witness-collapse can key off it (Â§6.5).
- **Per-witness `scope_reason` + dominant scope (H-3):** each witness carries one of `ally | rival | shared_enemy | region_observer` resolved by Â§8.4 precedence (region_observer deferred to bargain layer); `dominant_witness_scope` is computed per rupture and passed through to presentation (scope-branched copy deferred from C3-lite to `WAR_BARGAIN_SPEC.md` slice WB-D per the April 16 rescope).
- **Duplicate-surface collapse (H-4):** war-on-partner no longer fires both a `TREATY_BROKEN` and a `WAR_DECLARED` notification, nor both a `diplomatic_treaty_broken` and a `diplomatic_war_declared` dispatch event. The war event owns the moment; breach metadata survives in the event log.
- **`end_reason_family` vs `end_reason_action` split (H-6):** fault axis (`french_breach | counterparty_reversal | obsolescence_or_external`) and action axis (`manual_break | war_declaration | paradox_choice | cascade_forced`) are now separate fields, matching Â§9.9.
- **Pre-choice legibility for all three breach paths (M-1):** manual `break_treaty` on a commitment state now prompts `force_break_treaty_confirmation` with a reliability + warnings preview; `alliance_paradox` now carries deterministic fallout for both branches before the player chooses.
- **Structured `warnings[]` (M-2):** declare-war, paradox, and player-authored `proposal_confirm` dialogues now expose a typed `warnings[]` payload (`severity` + `category` + `text`) the C3-lite preview scaffolding can sort and filter; the proposal confirm popup now surfaces the top warnings under `Political Context`.
- **Applied vs intended reliability delta (M-5):** breach previews carry both values so presentation can distinguish "delta truncated at -100 floor" from "fully applied"; applied delta is authoritative for the scalar update.
- **Witness-scope label vs scope enum disambiguated (M-6):** audience-size flavor label is preserved as `witness_scope_label`; the per-witness enum sits on `witnesses[].scope_reason`.
- **Bilateral `betrayal_history` + hard reject posture (M-4 / B2b):** remembered breach strikes now persist per actor/victim pair with severity-scaled decay; the third active strike triggers `hard_reject_posture_triggered`, decay back to two strikes emits `hard_reject_posture_cleared`, and deep-treaty acceptance/preview paths respect that posture.
- **`commitment_paradox` registered in `HARD_STOP_TYPES` (H-5 backend):** taxonomy entry in place so the forthcoming Slice C Godot surfaces (per `COMMITMENTS_PRESENTATION_SPEC.md` §14) can land without a second backend pass.
- **AI `decision_reason` follow-through (M-3b):** AI-authored proposals, counterparty responses, campaign-log entries, incoming proposal popups, and proposal-result popups now carry a deterministic `decision_reason` plus player-facing display text. The enum set is still a subset of the full commitments spec, but motive legibility is no longer breach-only.
- **AI `decision_reason` surface (M-3 partial):** breach payload now exposes `end_reason_family` + `end_reason_action` + `fault_nation` as mechanical motive metadata; full AI-side proposal-generation `decision_reason` enum (Â§11.1) remains `C2` scope.
- **Previewâ†’resolution `episode_id` continuity (H-7):** `force_declare_war`, `force_break_treaty`, and alliance-paradox confirmations now reuse the preview's `origin_episode_id` instead of silently minting a second root event on confirm.
- **Durable paradox-resolution memory (H-8):** alliance-paradox choices now emit `commitment_paradox_resolved` with `chosen_nation`, `spurned_nation`, deterministic fallout preview, and the same origin `episode_id` that keyed the blocking choice.
- **Campaign-log legibility follow-through (M-7):** campaign-log formatting now preserves shattered-treaty wording, target/reason/fault distinctions for breach events, and a direct one-liner for `commitment_paradox_resolved` rather than collapsing back to ledger-generic phrasing.

Deferred (April 16 rescope finalized scope; remaining items are now part of either `Memory and Pressure` final implementation slice or `WAR_BARGAIN_SPEC.md`):

**Current `Memory and Pressure` next-work routing (v2.4.3):**

- Block 1 doc cleanup is complete: `docs/audits/MP_V243_BLOCK1_DOC_CLEANUP.md` closed the canonical-spec cleanup pass, including the commitments routing join-table, hegemony / Balance of Europe naming, and cross-doc drift closures from the combined audits.
- Block 2 substrate fixes are complete: `docs/audits/MP_V243_BLOCK2_SUBSTRATE.md` closed the code / serialization / test hardening pass, including the `commitment_paradox` pull-forward.
- Block 3 is SUPERSEDED: `docs/audits/MP_V243_BLOCK3_BLOC_NAMING.md` has been folded back into its owning specs. Bloc-naming contract lives in `COMMITMENTS_PRESENTATION_SPEC.md` §8.1a (terminology guard, `33 / 50 / 60` activation gate, hegemon→label taxonomy with fallback, required surfaces, worked-copy examples, playtest feel gates). Per-band voice contract lives in `DIPLOMAT_VOICE_BIBLE.md` "Bloc-naming voice contract" subsection. CF1-CF4 closure items are folded into their parent slices in `RELIABILITY_IMPLEMENTATION_PLAN.md` (CF1 → C-lite, CF2 → B-B7, CF3 → B-B4, CF4 → B-B4 per the B-B1-lite merge gate). No separate Block 3 consumption pass is required.
- Live implementation order after the now-complete B-Hegemony substrate is: B-B1-lite, then B-B3 / B-B7 / B-B4 per the dependency + merge gates, then C-lite (trimmed).
- Canonical references for this phase are `docs/RELIABILITY_COMMITMENTS_SPEC.md` v2.4.3, `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` v2.4.3, `docs/COMMITMENTS_PRESENTATION_SPEC.md` v0.5.2, and `docs/DIPLOMAT_VOICE_BIBLE.md` v1.2.

**Moved to `WAR_BARGAIN_SPEC.md` (Peace Deals phase):**

- `war_bargain` clause type, creation, lifecycle, Bargain Review surface, counter-bargain flow, `join_opportunity` + `pending_declaration` + `AllyEntryPipeline`, dedicated `compute_war_entry_score()` formula, `bargain_value_mod` acceptance modifier, `fulfillment_snapshot` extended contract.
- Bargain-specific `decision_reason` enum entries (`claim_trade`, `claim_obsolete`, full `counterparty_reversal` paths beyond what substrate already covers).
- WB-D bargain-era presentation extension: `bargain_*` spotlights, scope-branched witness reaction copy, response routes (`Propose redress`, `Deepen the bond`, `Attempt to reopen the chancery`, `Denounce the refusal`), 5-beat paradox staging when rivalry-driven ratification paradox fires the new triggers, N+5 fallback grievance slot.

Focused follow-up suite: 220 passed (`test_phase2b_diplomacy`, `test_playtest_bugfixes`, `test_session8c_popups_notifications`, `test_session8d_dispatch_polish`, `test_campaign_log`, `test_diplomacy_display_contract`). Full baseline suite not rerun in this pass. Ruff: not rerun in this pass.

### Independent Tracks

- **Jealousy System** â€” v3.1 spec drafted. NEEDS DESIGN GATE. Separate track. See `docs/JEALOUSY_SPEC.md`.
- **Phase 6.5 remaining** â€” Map Renderer cutover only. Placeholder bitmap/color-map lookup and Camera2D cutover are live; commissioned art-backed layers plus final Godot smoke validation still remain. Tutorial deferred to Pre-EA.

### Completed (Reference Only)

- ~~Bug Fixes Sessions 1-12 + A + B + C~~ â€” 25 bugs resolved (PL-1 through PL-25), 8093 tests
- ~~Adversarial Audit (Apr 8)~~ â€” 12 FAILs + 19 WARNINGs, PL-21/PL-22 fixed in code
- ~~Architecture Refactoring Sessions 1-16~~ â€” R19 (modding) remaining. R14a-d deferred
- ~~Phase 8: Diplomacy~~ - Implementation complete (1A through 8D), but stabilization / legitimacy refinement is still active via `BUG_FIXES.md` + `DESIGN_REFINEMENT.md`
- ~~Diplomacy Audits~~ â€” Code (20 bugs), Creative (7.8/10), Comprehensive (6.5/10), Deep (43 bugs)
- ~~Diplomacy Refinement Phases 1-4~~ â€” 55 items, 326 tests
- ~~All prior audit/fix plans~~ â€” Systems V1/V2/V3, Deep, Final â€” all complete

---

## Phase 6 Summary

All major Phase 6 features shipped:

- **Terrain (6.1):** 6 terrain types, weighted pathfinding, cavalry terrain scaling, charge blocking
- **Economy (6.2):** Region types, income/upkeep, stability, war damage, recruitment rework, buildings (4 types), supply limits, movement attrition, contested capture, AI admin phase â€” audited and balanced
- **Save/Load:** Manual save/load + autosave
- **Berthier Parse Recovery:** In-character error messages for unparseable commands
- **Battle Reports:** Template-based post-battle analysis with modifier snapshots, perspective-aware observations
- **Turn Events Log:** 13 event types, structured logging, hardened (EL1-EL5)
- **Fog of War:** Intel data model, visibility tiers, decay, watchtower building, strategic fog filtering, scout persistence, map visualization with fog overlay + fogged icons
- **Reinforcements, Attrition, City Fortification**
- **Player Garrison Command:** 2 AP, cap 3/nation, map overlay
- **Enemy AI Garrison (P6.75):** Building Blocks, 20k threshold, 1/nation/turn, P4.25 sub-5k awareness
- **Manpower Pools:** Nation-level infantry/cavalry/artillery reserves gate recruitment. Stables building. AI pool/cost awareness.
- **Artillery Unit Type:** Third marshal type (Drouot). Can't attack after moving, no advance on win, cavalry counter, 2x fort degradation. Bombardment system with terrain modifiers, collateral damage, AI bombardment. 127+ tests.

---

## Infrastructure Sessions

### Architecture Audit (Mar 27-28, 2026)

**Holistic architecture review:** 12-pass spec + 35 deep dives + 6 extended audits (frontend, integration, game loop, error recovery, tests, modding). 11 initial agents + 5 deep-dive agents + 7 verification agents.

**Findings:** 34 individual findings (2 CRITICAL, 9 MAJOR, 13 MODERATE, 12 LOW). 10 structural root causes identified responsible for ~240 of ~450 historical bugs.

**Deliverables:**
- `docs/ARCHITECTURE_AUDIT_SPEC.md` â€” 12-pass audit methodology
- `docs/ARCHITECTURE_AUDIT_REPORT.md` â€” complete findings + cross-audit analysis
- `docs/ARCHITECTURE_REFACTORING_PLAN.md` â€” 20 R-items, 22 sessions, 7 phases, ~55-68h estimated

**Top root causes:** Post-combat pipeline duplication (RC-1, 75 bugs), missing war-state filtering (RC-2, 49 bugs), no test conftest (RC-5, 22 bugs + maintenance multiplier), ad-hoc response pipeline (RC-4, 9 bugs), fog filter scatter (RC-6, 18 bugs).

### Apr 7 â€” Bug Fix Session 12: Ultimatum Rework (PL-14, 23 new tests)

**PL-14 FIXED.** Replaced blind one-shot `_execute_diplomatic_ultimatum` with full conversational diplomacy flow: dialogue push â†’ preview (`_enrich_ultimatum_dialogue`) â†’ deliver/escalate/reconsider. Key changes:

- **Conversational flow:** Ultimatum now routes through dialogue state machine. Player sees terms preview with acceptance estimate before delivery. `modify_harsh_ultimatum` handler caps escalation at 2 rounds (not unlimited like proposals).
- **Deterministic acceptance:** `calculate_acceptance()` gains `ultimatum_bonus` component. Acceptance reflects coercive pressure, not just diplomatic warmth.
- **`generate_ultimatum_terms()`:** New helper produces gold-only demands (no AP clauses, no sweeteners) with a gold cap. Terms are calibrated to be harsh but not absurd.
- **Splash relation damage:** Bystander nations with OPEN_BORDERS+ toward target take -5 to -15 relation hit with France on delivery.
- **Global cooldown migration:** `ultimatum_cooldown` migrated from per-nation dict to scalar on WorldState (one active ultimatum at a time).
- **`proposal_result_popup` passthrough:** Result delivered via existing Godot popup infrastructure â€” no new frontend scene required.

**Files:** `diplomatic_executor.py`, `diplomatic_templates.py`, `diplomacy.py`, `diplomatic_dialogue.py`, `world_state.py`, `cooldown_manager.py`, `display_names.py`, `campaign_log.py`.
**7980 tests passing** (7980 passed, 1 skipped, 0 regressions).

### Mar 24 â€” Systems Audit Sessions 11-12: Cleanup + QoL (12 fixes, 39 new tests)

**Session 11 (Cleanup/Placeholders/Docs):** Removed BALANCED/LOYAL personality descriptions and triggers (kept enum for serialization). Archived enemy AI bug fix history to `docs/archive/`. Added 50-notification cap with auto-dismiss of oldest NORMAL. Extracted `_build_tactical_prefix()` helper eliminating combat.py duplication. Added DiplomaticRepresentative roundtrip serialization tests. 19 new tests.

**Session 12 (Quality of Life):** Futility filter now decays per-turn instead of every 3 turns. Victory threshold extracted to `VICTORY_REGION_FRACTION = 0.75` constant (shared between world_state.py and turn_manager.py). British naval income scales with coastal regions (150 + 50/coastal, max 300). Infantry manpower regen reduced by war exhaustion (halved at 100 WE, floor 1000). Admin AP gold reduced from 35g to 25g. AI stagnation fallback uses random.choice instead of deterministic first. 20 new tests, 9 existing updated.

**Files modified:** personality.py, notifications.py, combat.py, world_state.py, turn_manager.py, enemy_ai.py + 2 new test files + 6 existing test files + 1 archived doc.
**6904 tests passing** (6904 passed, 3 skipped, 0 regressions).

### Mar 22 â€” N4 War Status Panel (DA-4: 3-layer HUD, 10 files, 32 tests)

Three-layer EU4-style war status system. Always-visible HUD cards â†’ click-to-inspect detail popup â†’ diplomacy wizard handoff.

**Backend:** `backend/game_logic/war_status.py` â€” `build_active_wars(world)` produces `{wars: [...], coalition: {...} | None}`. War score from France's perspective (sign-flipped), trend detection via `previous_war_scores`, fog-filtered WE/army strength, coalition coordination quality (friction â†’ Good/Strained/Poor), weak link detection, armistice with relation/descriptor/trend. Embedded in every response via `_include_popup_passthroughs()` + GET `/test` + GET `/status`.

**Godot Layer 1 â€” HUD Cards:** `war_status_panel.gd` (CanvasLayer 25). Bottom-right panel with coalition header, member rows, bilateral war cards (with score bars), armistice cards. Hides when no wars/armistices. Current signal is `card_clicked(nation, status)`; Slice F must widen settlement-safe routing to `card_clicked(nation, status, war_instance_id)` plus `coalition_header_clicked()`.

**Godot Layer 2 â€” Detail Popup:** `war_detail_popup.gd` (CanvasLayer 30). Three modes: `show_war()` (score breakdown, WE, recent battles), `show_coalition()` (members, coordination, weak link), `show_armistice()` (remaining turns, relations, trend). `refresh_if_open()` updates in-place without closing. Close via X/Escape/overlay click.

**Godot Layer 3 â€” Wizard Handoff:** Added `open_for_nation(nation)` to `diplomacy_wizard.gd`. Negotiate/Target buttons emit signals â†’ `main.gd` handlers â†’ wizard opens pre-populated for that nation.

**Wiring in main.gd:** `_process_active_wars(response)` called from `_on_command_result()`, `_on_enemy_phase_dismissed()`, and `_on_connection_test()`. War panel hidden when screens open via `_update_war_panel_visibility()`.

**Files:** war_status.py (new), main.py, war_status_panel.tscn/.gd (new), war_detail_popup.tscn/.gd (new), diplomacy_wizard.gd, main.gd, test_war_status.py (new, 32 tests), test_bugfix_proposal_flow.py (1 test updated).
**6529 tests passing** (6529 passed, 3 skipped, 0 regressions).

### Mar 9 â€” Dialogue Gap Fix (6 gaps, 7 files, 19 tests)

Fixed all remaining broken dialogue routing paths. 6 gaps closed:

1. **GAP-1 (keyword routing):** 4 template actions (`elaborate`, `review_counter`, `accept_with_conflict`, `expand_to_proposal`) had no keyword routing. Added 5 keywords + 7 action_map entries + 3 handler branches.
2. **GAP-2 (popup type filter):** Mission/Feasibility/Advisory/WarConfirm/ConflictAlert dialogue types were ignored by Godot popup router. Expanded type filter + added 5 type-aware content builders in proposal_confirm_popup.gd.
3. **GAP-3 (nation picker):** Nation-picker popup always selected first option. Added fallback label-matching in main.py + index-based button binding in proposal_confirm_popup.gd.
4. **GAP-4 (objection override):** `send_override`/`send_suggested` unreachable via keyword. Added `proceedâ†’send_override`, `trustâ†’send_suggested` routes.
5. **GAP-5 (objection popup terms):** Objection popup didn't show proposal terms or acceptance estimate. Enriched popup dict with terms list + acceptance score + color-coded display.
6. **GAP-6 (cancel_mission):** `cancel_mission` had no keyword routing, `begin` missing from keyword list. Fixed both. Objection cancel button now sends `dismiss` to clear backend state.

**Files modified:** main.py, executor.py, diplomatic_dialogue.py, main.gd, proposal_confirm_popup.gd, talleyrand_objection_popup.gd
**New tests:** `tests/test_dialogue_gaps.py` (19 tests across 6 sections)
**6091 tests passing** (6091 passed, 3 skipped, 0 regressions).

### Mar 9 â€” Diplomatic Screen Update (30 changes, 35 tests)

Major enrichment of the Diplomatic Ledger (D key) and Diplomacy Wizard (F1 key). Backend already computed many fields that the frontend silently ignored â€” now all rendered. Plus new backend fields for missing context.

**Ledger Tab 1 â€” Nations (N1-N7):** AI-AI relations colored by state, war score breakdown, proposal cooldowns, vassal eligibility badge, trade income, relation descriptor, relation trend arrows (â†‘â†“â†’ via new `relation_history` WorldState field).

**Ledger Tab 2 â€” Treaties (T1-T4):** Gold flow per turn, treaty age (turn signed), player vs AI-AI distinction (dimmed grey), armistice countdown.

**Ledger Tab 3 â€” Threat & Coalition (TH1-TH4):** Critical pulse animation (was empty `pass`), coalition cooldown display, human-readable threat source labels (18 keys), dissolution conditions text.

**Ledger Tab 4 â€” Talleyrand (TA1-TA5):** Diplomatic history (last 10, colored by type), reliability with descriptor, DP breakdown (base/skill/authority/capital), mission effect text + cost, remaining turns for fixed-duration missions.

**Wizard Step 1 (W1-W2):** Relation score + descriptor on nation buttons, [MISSION] indicator for active missions.

**Wizard Step 2 (W3-W5):** KEY FACTORS section (top 3 positive/negative acceptance components), cooldown pre-check warning (Talleyrand quote), mission effect text on action buttons.

**Edge case audit:** 4 bugs found and fixed â€” authority_tracker source for DP breakdown, `int(round(val or 0))` None guard, isinstance check on active_mission dict, variable shadow in Godot loop.

**Files modified:** diplomatic_ledger.py, world_state.py, main.py, diplomacy.py, diplomatic_ledger.gd, diplomacy_wizard.gd, test_diplo_screen_update.py (35 tests), SAVE_FORMAT_REFERENCE.md. 6038 total tests passing.

### Mar 9 â€” Playtest Bugfixes (4 fixes, 12 tests)

Creative playtesting revealed 4 bugs:
1. **Game-over enforcement:** Game continued after defeat. Added game-over guard to 8 action endpoints + blocked AI diplomacy after game over. Read-only endpoints still work.
2. **Capital-loss defeat removed (PL-31, fixed Apr 10):** The capital-loss defeat branch has been removed from `_check_victory_conditions()`. Capital can be lost without ending the campaign. The original regression test targeted the wrong region key (`Ile-de-France` instead of `Paris`) and passed vacuously.
3. **Empty command rejection:** Empty/whitespace commands no longer trigger the parser. Returns clean error.
4. **LLM parse fields:** `requested_type`, `diplomatic_data`, `cheat_type`, `cheat_args` were missing from `json_to_parse_result()` in providers.py. Recruit type parsing now works in LLM mode.
5. **Treaty war warning:** Declaring war on a treaty ally now shows a Talleyrand warning dialogue. Player must confirm via `force_declare_war` to proceed.

### Mar 9 â€” Wave 2.5: Wartime Peace Rebalance (R141-R150) + territory_cede Bugfix

Wartime peace deals were impossible â€” France proposing armistice to Prussia scored ~4 (REJECT). Root causes: relation weight dominated wartime acceptance, no war weariness modifier, sweetener values too low, territory cession never generated, P2 trigger too restrictive. 32 new tests. 5933 total tests passing.

**R141-R150 implemented:**
- R141: Relation dampened during WAR (div 4, cap +-10 vs peacetime div 2, cap +-30)
- R142: War weariness modifier (+2/turn at war, cap +20) via new `war_start_turns` field on WorldState
- R143: Stalemate duration modifier (+1/stalemate turn, cap +15)
- R144-R146: Territory sweetener 5â†’8, gold lump rate doubled (1/200â†’1/100), sweetener cap 30â†’40
- R147: Territory cession in `generate_suggested_terms()` when losing (non-capital only)
- R148: AP sweetener when war_score < -50, manpower when < -30
- R149: P2 stalemate trigger `war_score <= 10` (was `<= 0`, supersedes R121)
- R150: Armistice sweeteners (gold lump + territory) when losing

**Bugfixes found during investigation:**
- `territory_cede` sweetener type missing from `SWEETENER_VALUES` â€” acceptance value was 0 (added at 8/region)
- `generate_suggested_terms()` used `"region"` (singular) but `_ratify_treaty()` checks `"regions"` (plural) â€” territory cession silently did nothing. Fixed to `"regions": [region]`.

**Worked example:** Franceâ†’Prussia armistice (relation -40, 8 turns at war, stalemate 5, 1 territory offered): score went from 1 (REJECT) to ~40 (COUNTER_OFFER).

**Files modified:** diplomacy.py, diplomatic_templates.py, ai_diplomacy.py, vassal.py, world_state.py, DIPLOMACY_SPEC.md, DIPLO_REFINEMENT.md, SAVE_FORMAT_REFERENCE.md + 4 updated test files

### Mar 8 â€” Diplomacy Button: Final Edge Case Fixes (Confidence 10/10)

Deep-dive audit found 5 remaining gaps after initial audit pass. 2 genuine bugs fixed, 2 hardening items applied, 1 confirmed no-op. 5901 total tests passing.

**Fixes:**
- **BUG:** Ultimatum shown in WAR state but executor rejects â€” removed from wizard action list
- **BUG:** Proposal DP cost ignored Talleyrand skill penalty (+1/+2) â€” wizard now calls `get_dp_cost()` with skill
- **HARDENING:** `dialogue_pending` not enforced in backend `get_available_diplomatic_actions()` â€” added early return
- **POLISH:** HTTP timeout on wizard's HTTPRequest â€” set 30s timeout
- **NO-OP:** Downgrade path validation â€” confirmed state routing already handles it

### Mar 8 â€” Diplomacy Button Session B: Godot Wizard UI Complete

Godot wizard UI for the Diplomacy Button. [Diplomacy] button + F1 hotkey opens guided 2-step wizard. 5886 total tests passing, 0 failures.

**Deliverables:**
- `diplomacy_wizard.gd` (427 lines) + `diplomacy_wizard.tscn` â€” CanvasLayer 100 modal, own HTTPRequest (Â§9b)
- [Diplomacy] button in InputSection between Execute and End Turn
- F1 hotkey wired in both `_on_command_input_gui_input` (text focus) and `_unhandled_input` (global)
- Step 1: categorized nation list (at_war/treaties/vassals/neutral) from `/diplomatic_preview`
- Step 2: Talleyrand's assessment panel + colored likelihood action buttons from `/diplomatic_preview?nation=X`
- Step 3: command handoff â€” wizard builds command string, emits signal, main.gd sends via `/command`
- All Â§9 wiring: modal registration (Â§9a), dedicated HTTPRequest (Â§9b), dialogue guard (Â§9c), screen close (Â§9d)
- `/diplomatic_preview` endpoint extended: returns nation list when no `?nation` param

### Mar 8 â€” Diplomacy Button Session A: Backend Complete

Full backend for the Diplomacy Button wizard. 93 new tests in `test_diplomacy_button.py`. 5886 total tests passing, 0 failures.

**Deliverables:**
- `GET /diplomatic_preview` endpoint in `main.py` â€” returns nation assessment, available actions with likelihood words, recommendation, vassal details
- `get_available_diplomatic_actions()` â€” builds action list per Â§2b/2c tables with all Â§2d filters (DP, cooldowns, gold, autonomy extremes, relation requirements)
- `get_likelihood_descriptor()` â€” 6-tier scale (Hopeless â†’ Almost Certain) mapped from acceptance scores
- `get_assessment_text()` â€” 17 templates keyed by diplomatic state + relation/war_score/loyalty ranges, plus fallback
- `_build_recommendation()` â€” 4-tier logic: 0 DP â†’ resource advice, low vassal loyalty â†’ invest, favorable action â†’ recommend, else strategic advice
- Â§4a: Proposal-at-or-below-current-state pre-check (blocks proposing what you already have)
- Â§4b: `ultimatum_cooldowns` on WorldState â€” 5-turn cooldown per nation, serialized, decremented in `advance_turn()`
- Â§4c: Break-treaty-without-treaty Talleyrand-voiced rejection
- Â§4d: Downgrade-at-minimum-state Talleyrand-voiced rejection
- Â§4e: Declare-war-during-armistice shows remaining turns
- Mock parser coverage for all 11 wizard command strings (4 had gaps â€” fixed)

**Edge case fixes discovered during implementation:**
- `release_vassal` had NO parser keyword or executor method anywhere â€” added both (new `_execute_release_vassal`)
- `increase/decrease autonomy` had no parser keywords â€” added direction-based parsing
- `propose vassalization` was routing to vassal section instead of diplomatic parser â€” reordered keywords
- Â§4d downgrade pre-check now fires before DP check â€” updated 1 existing test in `test_phase4_batch5_popups.py`

**Impact on future sessions:**
- **Session B (Godot wizard):** Backend validates/blocks all invalid actions now. Godot wizard should display error messages from these validation responses. The `/diplomatic_preview` endpoint returns the full action list with likelihood â€” Godot just needs to render it.
- **Wave 3 R118 (acceptance preview):** Now uses unified `get_likelihood_descriptor()` from this session. No separate implementation needed.
- **Phase 5 items:** `release_vassal` executor and direction-based autonomy changes are now available â€” any Phase 5 items touching these won't need to add the plumbing.

### Mar 7 â€” Comprehensive Creative Audit: Phase 5 Design Depth Approved

6-agent deep creative audit of entire diplomacy system. Scored 6.5/10 overall. Audited: core mechanics (diplomacy.py), AI behavior (ai_diplomacy.py), coalition & vassal (coalition.py, vassal.py), dialogue & templates (all dialogue/template/advisory/defiance files), command parsing (parser/executor/main), system coherence (specs vs implementation).

**Key findings:**
- Talleyrand voice is monotone (template fatigue after 5 conversations)
- AI proposals lack personality (Schemer = Hawk = Dove in behavior)
- Diplomacy strategically optional (military conquest always faster)
- Coalition defensive posture calculated but never read by enemy AI
- No aggressive dominance AI trigger (AI never demands harsh terms when winning)
- Marriage alliances entirely missing (major Napoleonic mechanic)
- Garrison trivializes vassal loyalty (15k troops = loyalty solved forever)
- DP use-it-or-lose-it discourages saving for big moves
- Continental System still a trap choice even after R18

**Result:** 41 new items (R115-R140 + promoted deferred). All added to Phase 5 in DIPLO_REFINEMENT.md. Design-first prioritization: 5A core features â†’ 5B AI intelligence â†’ 5C narrative â†’ 5D fixes â†’ 5E promoted deferred.

### Mar 6 â€” Phase 2A Diplomacy Core Cleanup: 17 Fixes Implemented

17 bug fixes across 5 batches. 69 new tests (`test_phase2a_batch1-5.py`). 5396 total tests passing. 2 new serialized fields.

**Fixes implemented:**
- R54: Canonical `get_war_score_for()` helper â€” single source of truth, replaces 5 inline implementations
- R7: `defensive_alliance: 25` added to BASE_DISPOSITION
- R56: Self-relation guard in `modify_nation_relation()`
- R44: `nation_dp` field â€” AI nation DP stored and serialized
- R67: `copy.deepcopy()` for coalition serialization (prevents shared-reference corruption)
- R1a: Battle records >10 turns old pruned in `apply_war_score_decay()`
- R1b/R49/R47: `cleanup_war_end()` helper â€” clears battle_records, decisive_battles, war_scores, war_exhaustion, cancels PURSUE orders
- R45: `active_treaties` removed on `execute_downgrade()`
- R5a: Armistice expiration implemented (5 turns â†’ PEACE or WAR based on relations)
- R5b: Armistice cooldowns set on entry, block AI proposals
- R3: Gold floor in treaty clauses (never negative, dispatch event on inability to pay)
- R80: Auto-downgrade fires dispatch event + notification
- R82: `{rejection_reaction}` template slot resolved (cold fury / displeasure / composure)
- R83: Coalition dispatch templates + `queue_dispatch_event()` in form/dissolve/brewing
- R51: Pending dialogue voided when target joins coalition
- R50: Continental System membership cleared on vassal release
- R48: Vassal diplomacy reconciled on vassalization (auto-armistice/peace with conflicting states)
- R57: Threat level wired in diplomatic dialogue context (was hardcoded 0)
- R53: Sweetener value floor (min 5) in `_try_add_desired_clauses()`

**Files modified:** diplomacy.py, world_state.py, ai_diplomacy.py, diplomatic_advisory.py, vassal.py, coalition.py, dispatch.py, diplomatic_templates.py, diplomatic_dialogue.py, notifications.py

### Mar 5 â€” Phase 1 Critical Wiring: 16 Fixes Implemented

16 bug fixes across 7 batches. 37 new tests (`test_phase1_critical_wiring.py`). 5327 total tests passing.

**Fixes implemented:**
- R40: Coalition loyalty penalty formula inverted (`min` â†’ `max`, WE subtracts)
- R96: VASSAL added to OPEN_MOVEMENT_STATES (lord traversal fixed)
- R109: defensive_alliance type no longer overwritten to "alliance"
- R66: Dispatch fog rule reads correct `target` key (was `target_nation`)
- R61: original_nation serialized on Marshal (to_dict/from_dict)
- R62: Rebellion clears original_nation and resets Trust
- R63: break_treaty() now adds coalition threat (+25 alliance, +15 other)
- R64: Continental System called from turn loop (duplicate in vassal.py removed)
- R65: Advisory uses fog-filtered strength (unknown/stale/partial/full tiers)
- R43: AI-AI per-pair proposal cooldown (5 turns after ratification)
- R37/R41: Sabotage confrontation & redemption dialogue handlers wired
- R42: Pre-proposal objection send_override/send_suggested handlers with terms preservation
- R55: "continue" keyword added to dialogue guard
- R74/R75: Vassal rebellion imminent sets pending_diplomatic_dialogue with invest/garrison/accept
- R2: Counter-offer system activated (COUNTER_OFFER generates terms, accept/reject handlers)

**Files modified:** coalition.py, diplomacy.py, ai_diplomacy.py, dispatch.py, marshal.py, vassal.py, diplomatic_advisory.py, diplomatic_dialogue.py, executor.py, world_state.py, main.py

### Mar 5 â€” Deep Audit II: 54 New Refinement Findings

6-agent deep code audit targeting wiring gaps, state cleanup, cross-system interactions, and popup architecture. 1 file modified (DIPLO_REFINEMENT.md, +755 lines).

**54 new findings (R61-R114):** 9 HIGH severity, 27 MEDIUM, 18 LOW. Phase 2 split into 2A (diplomacy core, 19 fixes) and 2B (vassal/AI-AI/war, 23 fixes).

**6 systemic trends identified:**
1. Vassal system most under-wired (11 findings) â€” rebellion cleanup, coalition membership, Continental System
2. Popup early-return cascade (9 findings) â€” Godot `_on_command_result()` returns early on popup, drops all other data
3. Continental System entirely dead â€” code exists but never called from turn loop
4. State cleanup on war/peace transitions incomplete â€” treaties, battle records, stalemate counters persist
5. AI-AI plays by different rules â€” bypasses `validate_transition()`, skips `active_treaties`, no armistice
6. Fog of war has 2 leak points â€” advisory exact strength, dispatch wrong key

**Most impactful findings:**
- R61: `original_nation` not serialized (save/load data loss)
- R96: VASSAL not in OPEN_MOVEMENT_STATES (lord can't traverse vassal territory)
- R97: `declare_war` doesn't clean `active_treaties` (treaty clauses execute during war)
- R109: `defensive_alliance` overwritten to `"alliance"` (entire tier unreachable)
- R64: Continental System never called from turn loop
- R65: Advisory leaks exact enemy strength through fog

**Updated refinement plan:** 114 total items. 7-row phase table. All items design-gate approved.

### Mar 4 â€” Diplomacy Creative Audit + Refinement Doc

5-agent parallel deep analysis of diplomacy system design quality. Scored 7.8/10 overall. Created `docs/DIPLOMACY_CREATIVE_AUDIT.md` (full findings) and `docs/DIPLO_REFINEMENT.md` (36 ranked items with fix proposals, including new feature suggestions like marriages, ultimatums, secret treaties). 5 files modified, 106 lines added.

**Findings:** 8 critical/high bugs (war score decay no-op, battle records persist across wars, counter-offer stubbed as reject, treaty gold unenforced, armistice unimplemented), 10 balance issues (COURT_NATION speed, no relation decay, trade income snowball, coalition stalemate), 18 design gaps (missing commands, ledger info gaps), 6 AI issues, 7 edge cases.

**Easy Fixes Applied (3):**
- **GAP-3:** Wired `break_treaty()` command â€” keywords: "break/cancel/renounce/end treaty". 1 DP cost.
- **GAP-5:** Wired `execute_downgrade()` command â€” keywords: "downgrade/reduce commitment/step down". 1 DP cost.
- **GAP-6:** Added AI-AI diplomatic states to ledger nations tab, fog-filtered (PARTIAL+ intel).

**5290 tests passing** (0 regressions).

### Mar 4 â€” Diplomacy Audit Part 3 (AI Proposal Spam Fixes)

Playtest-discovered bug: AI nations (especially Saxony) repeatedly offering the same deals. 2 files modified, 1 new test file, 19 new tests.

**Bugs Fixed (3):**
- **MEDIUM (SPAM-1):** No acceptance cooldown â€” after accepting a proposal, the same nation could propose again next turn. Now applies a 2-turn nation cooldown on acceptance (vs 3 turns on rejection).
- **MEDIUM (SPAM-2):** No pending-proposal deduplication â€” `process_diplomatic_phase` didn't check if a nation already had a proposal in the active dialogue or queue. Added `_has_pending_proposal_from()` guard.
- **LOW (SPAM-3):** P7 opportunistic trigger proposed NON_AGGRESSION regardless of current diplomatic state â€” could fire even at ALLIANCE. Now only fires when current state is PEACE or OPEN_BORDERS.

**19 new tests** in `tests/test_audit_part3.py`: 5 acceptance cooldown (constant, blocking, expiry, executor wiring), 6 deduplication (dialogue, queue, empty, blocking, allow-other-nation), 5 P7 state validation (peace, open_borders, non_aggression, alliance, defensive_alliance), 3 integration (accept-then-no-followup, accept-chain-with-cooldowns, alliance-cap).

**5263 tests passing** (5244 + 19 new, 3 skipped, 0 regressions).

### Mar 4 â€” Diplomacy Audit Part 2 (Sections 7-15)

Comprehensive audit of remaining Phase 8 diplomacy sections. 2 files modified, 1 new test file, 57 new tests.

**Bugs Fixed (3):**
- **MEDIUM (AA-5):** AI-AI alliance conflict check missing. AI nations could form alliances even when one was at war with the other's ally (violating Â§5b.3). Fixed: added alliance conflict check in `_ratify_ai_ai_treaty()`.
- **LOW (AL-2a):** `cheat set_war_exhaustion` clamped to 100 instead of WAR_EXHAUSTION_MAX (200). Fixed: updated clamp to 200.
- **LOW (AL-2b):** `cheat set_vassal_loyalty` had no bounds checking â€” could set negative or >100. Fixed: added `max(0, min(100, ...))` clamp.

**Verified Clean (93 items across 9 sections):**
- Section 7 (Coalition): 33/33 PASS â€” threat accumulation, decay, formation, warfare, dissolution all correct
- Section 8 (Vassal): 17/17 PASS â€” creation, loyalty drift, rebellion all correct. 3 checklist spec errors corrected (garrison=+8 not +15, shared enemy=+2 not +10, popup at <=10 not <15)
- Section 9 (AI Proposals): 14/15 PASS â€” P1-P7 triggers, M3 counter-offer, AI-AI diplomacy correct
- Section 10 (Ledger): 8/8 PASS â€” 4 tabs, fog filtering, data accuracy
- Section 11 (Dispatch): 6/6 PASS â€” 21 event types, fog filtering, Talleyrand's Report, vassal warnings
- Section 12 (Serialization): 12/12 PASS â€” all 42 diplomatic fields roundtrip, popup/dialogue/coalition/vassal/mission
- Section 13 (Cross-System): 17/17 PASS â€” combat/movement/economy/enemy AI Ã— diplomacy
- Section 14 (Notifications): 10/10 PASS â€” all 19 diplomatic notification types verified
- Section 15 (Debug): 5/6 PASS â€” 11 cheat commands, 8 debug endpoints

**Design Notes:**
- AH-4: No marshal auto-ejection on diplomatic state downgrade (known limitation)

**57 new tests** in `tests/test_audit_part2.py`: 4 threat accumulation, 2 threat decay, 8 formation thresholds, 3 coalition warfare, 2 dissolution, 7 vassal creation, 2 loyalty drift, 2 rebellion, 5 alliance conflict fix, 2 AI-AI diplomacy, 4 ledger tabs, 7 serialization roundtrip, 1 DP economy, 3 movement, 1 notifications, 5 cheat bug fixes, 1 cheat parsing.

**5244 tests passing** (5187 + 57 new, 3 skipped, 0 regressions).

### Mar 4 â€” Diplomacy Audit Part 1 (Sections 1-6)

Comprehensive audit of Phase 8 diplomacy. 4 files modified, 1 new test file, 42 new tests.

**Bugs Fixed (7):**
- **CRITICAL (A-1):** Enemy phase hidden when incoming_proposal popup returns early in Godot. Fixed: main.py defers all popups when `enemy_phase` present.
- **CRITICAL (A-2):** Diplomatic early return skipped popup pass-throughs. Fixed: early return now calls `_include_popup_passthroughs()`.
- **CRITICAL (A-3):** No safety valve for cleared popup with pending dialogue. Fixed: re-derives `incoming_proposal` from `pending_diplomatic_dialogue`.
- **CRITICAL (A-4):** Inconsistent popup pass-through handling. Fixed: new `_include_popup_passthroughs()` helper handles all 6 popups consistently.
- **CRITICAL (B-3):** Godot popup callbacks send to `/command` but executor guard blocks ALL commands when dialogue pending. Fixed: main.py routes dialogue keywords to `handle_diplomatic_dialogue_response()` before executor.
- **Safety Valve (C-1/C-2):** No way to clear stale blocking dialogue. Fixed: auto-clear in `advance_turn()` after 2 turns + `cheat clear_dialogue` command.
- **Missing State (L-4):** VASSAL missing from `post_break_map` in diplomacy.py. Fixed: added `"VASSAL": "NON_AGGRESSION"`.

**Verified Clean (Sections 3-4):** Turn flow integration all PASS. Acceptance formula all PASS. War score all PASS.

**Design Notes (not bugs, for future consideration):**
- J-5: Armistice expiration is a placeholder (no-op)
- K-5/K-6: No alliance conflict check in war declaration
- L-3: Treaty break cooldown not implemented (spec says 5 turns)
- O-5: Redemption during active mission not explicitly handled

**42 new tests** in `tests/test_audit_part1.py`: 8 popup flow, 7 blocking lifecycle, 3 acceptance formula, 10 state transitions, 8 Talleyrand defiance, 3 queue lifecycle, 2 serialization, 1 war score.

**5187 tests passing** (5145 + 42 new, 3 skipped, 0 regressions).

### Mar 4 â€” Session 8A: Backend Ledger + Debug Arsenal

Phase 8 Session 8A implementation. 1 new backend file, 1 new test file, 6 modified files, 82 new tests.

- **`backend/game_logic/diplomatic_ledger.py`** (NEW): `build_diplomatic_ledger(world)` returns 4 tabs: nations (per-nation diplomatic state, relation, diplomat, fog-filtered army strength, regions, treaties, vassal eligibility), treaties (active treaty list), threat_coalition (threat level/tier, qualifying nations, brewing/active coalition with fog-filtered member strengths), talleyrand (trust/label, skill, DP, mission, envoy count, sabotage warnings). Fog-filtered army strength: UNKNOWNâ†’"Unknown", STALEâ†’named bands (Negligible/Minor/Considerable/Powerful/Dominant), PARTIALâ†’~rounded to 5k, FULLâ†’exact. National visibility = best marshal visibility across nation.
- **`backend/main.py`** (MODIFIED): GET `/diplomatic_ledger` endpoint. 7 top-bar fields in `/test` response (diplomatic_points, max_diplomatic_points, talleyrand_state, talleyrand_mission_summary, threat_level, coalition_brewing, coalition_brewing_turns, pending_envoy_count). Pass-through wiring for 3 popup fields (coalition_popup, diplomatic_sabotage, vassal_rebellion_imminent) with readâ†’includeâ†’clear pattern. 8 debug endpoints (/debug/diplomatic_status, war_scores, acceptance_preview, coalition_status, threat_sources, proposal_cooldowns, vassal_loyalty/{nation}, proposal_queue).
- **`backend/models/world_state.py`** (MODIFIED): 3 new popup fields (coalition_popup, diplomatic_sabotage_popup, vassal_rebellion_imminent_popup). Serialized with backward-compat `.get()` defaults.
- **`backend/ai/llm_client.py`** (MODIFIED): "cheat " prefix detection in mock parser. Returns ParseResult with cheat_type and cheat_args.
- **`backend/ai/schemas.py`** (MODIFIED): cheat_type and cheat_args fields added to ParseResult dataclass.
- **`backend/commands/executor.py`** (MODIFIED): Cheat command routing + `_execute_cheat()` method with 10 commands (set_threat, set_relation, give_dp, trigger_coalition, set_war_exhaustion, set_diplo_state, create_vassal, set_vassal_loyalty, set_talleyrand_trust, queue_ai_proposal). Guard: only available in mock/debug mode.
- **`backend/game_logic/diplomacy.py`** (MODIFIED): `calculate_war_score()` extended with `return_components` parameter. When True, returns dict with total/territory/battles/decisive/capital breakdown.
- **`godot-client/.../api_client.gd`** (MODIFIED): `get_diplomatic_ledger()` method added.
- **82 new tests** in `tests/test_session8a_ledger_debug.py`: 11 test classes covering diplomatic ledger nations (8), army strength fog (12), treaties (3), threat/coalition (9), Talleyrand (9), cheat commands (16), debug endpoints (8), pass-throughs (6), top-bar fields (4), ledger endpoint (3), war score components (3).
- **5027 tests passing** (4945 + 82 new, 3 skipped, 0 regressions).

### Mar 4 â€” Session 7 Gap Closure: Coalition Polish

Closed 4 spec gaps + 1 comment cleanup from Session 7 confidence report. 5 files modified, 10 new tests.

- **Gap 1 (vassal.py):** Voluntary vassal release now calls `reduce_threat(world, 8, "voluntary_vassal_release")`. Only fires for player nation lord; rebellion path already handled separately.
- **Gap 2 (world_state.py):** Generous peace detection in `_ratify_treaty()`. When France signs peace while winning (war_score > 20) with sweeteners but no territory demands, applies -3 threat (`generous_peace`).
- **Gap 3 / EC-2 (coalition.py):** `form_coalition()` now voids in-transit proposals to joining nations. Restores Talleyrand state, refunds DP, logs event.
- **Gap 4 / EC-9 (executor.py + enemy_ai.py):** Coalition members blocked from attacking each other. Hard check in `_execute_attack()` + AI target filter skips coalition allies.
- **Gap 5 (coalition.py):** Replaced confusing 5-line comment about declare_war threat with clear one-liner.
- **10 new tests** in TestGapFixes class covering all 4 gaps with positive and negative cases.
- **4945 tests passing** (4935 + 10 new, 3 skipped, 0 regressions).

### Mar 4 â€” Session 7: Coalition System

Phase 8 Session 7 implementation. 1 new file, 9 modified files, 80 new tests.

- **`backend/game_logic/coalition.py`** (NEW): Complete coalition engine (~530 lines). Threat accumulation (add_threat/reduce_threat, 0-100 clamped). Threat decay (1 base + peaceful nations cap 3, Continental System uncapped). Coalition formation: brewing at â‰¥60 (3-turn countdown), instant at â‰¥80, cooldown override at â‰¥90. Qualifying nations (relation < -10, not vassal, not at war). Leader selection (military//1000 + hostility + authority, tiebreak marshals then alpha). Strategic posture (aggressive/defensive/cautious, leader personality override). Coalition friction (4 tiers: 1.0/0.75/0.5/0.25 by mutual relation). Loyalty penalty (min(-15 + WE//10, 0), wedge halving). War exhaustion (+casualties//1000 per battle cap 20, +5/turn at war, -5/turn at peace, coalition shock +5). British subsidy (200g/turn to lowest-relation partner). Dissolution (<2 members, all peace, or threat <20), 5-turn cooldown. Master per-turn processor (9 steps).
- **`backend/models/world_state.py`** (MODIFIED): 7 new fields (threat_level, threat_sources_this_turn, active_coalition, coalition_brewing, coalition_cooldown, coalition_count, war_exhaustion). Serialized with backward compat .get() defaults. advance_turn hook after vassal processing calls process_coalition_turn(). Per-turn clearing of threat_sources_this_turn. Treaty ratification wires add_threat(8/region annexed) and reduce_threat(5/region returned). Coalition member removal on separate peace.
- **`backend/commands/executor.py`** (MODIFIED): Threat wiring after battle resolution. France wins: +3 battle, +5 decisive (ratio >2:1 AND casualties >10k), +15 capital capture. War exhaustion for losing nation. Coalition shock on decisive defeat.
- **`backend/game_logic/diplomacy.py`** (MODIFIED): War declaration +20 threat. Diplomatic downgrade threat per DOWNGRADE_PENALTIES. Acceptance formula: threat_mod uses real threat_level (was stub), coalition_penalty via get_coalition_loyalty_penalty() added as new component.
- **`backend/game_logic/vassal.py`** (MODIFIED): Replaced direct threat_level writes with add_threat() calls (treaty vassalization +5, conquest +25, rebellion -10).
- **`backend/ai/enemy_ai.py`** (MODIFIED): Replaced TODO-1805 is_ally hack with is_coalition_member() check. Coalition friction applied to cross-nation adjacency bonus. New _get_convergence_bias_score() method (+12/+4/0 toward French territory by posture). Posture threshold adjustment in _find_attack_opportunity (aggressive -0.15, cautious +0.15).
- **`backend/game_logic/dispatch.py`** (MODIFIED): New _build_coalition_section() function. Returns threat level/tier/sources, brewing info, active coalition details (name, leader, posture, per-member stats). Wired into build_morning_dispatch() as dispatch["coalition_status"].
- **`backend/game_logic/diplomatic_templates.py`** (MODIFIED): 7 new template categories (T28-T34): coalition_murmur, coalition_brewing, coalition_declared, coalition_member_weak, coalition_advice_split, coalition_dissolved, coalition_harsh_warning. New slot resolvers for threat_level, coalition_name, leader, member_list.
- **`backend/notifications.py`** (MODIFIED): 7 new coalition notification constants (COALITION_THREAT_TENSION through COALITION_COOLDOWN_ENDED).
- **80 new tests** in `tests/test_session7_coalition.py`: 12 test classes covering threat accumulation (10), threat decay (5), qualifying nations (7), coalition formation (12), coalition structure (8), coalition AI (8), coalition breaking (11), dissolution (5), British subsidy (3), edge cases (6), serialization (2), process_coalition_turn (4).
- **4935 tests passing** (4855 + 80 new, 3 skipped, 0 regressions).

### Mar 4 â€” Session 6: Talleyrand Defiance + Diplomatic Objections

Phase 8 Session 6 implementation. 1 new file, 4 modified files, 76 new tests.

- **`backend/commands/diplomatic_defiance.py`** (NEW): Complete Talleyrand defiance system (Â§3a-Â§3e). Defiance probability curve mirroring V2b combat defiance (base 0.05, authority/trust modifiers, 2% Schemer floor, 30% hard cap, Loyalist immune). 5 sabotage types (softened, hardened, stalled, ap_downgrade, unit_overpay) based on proposal harshness. Discovery mechanism (40% base + 10%/turn cumulative). Confrontation dialogue with confront/overlook choices. Redemption event at trust â‰¤ 20 with 3 choices (apologize, replace with loyalist, continue). Pre-proposal V2a objection (MILD/MODERATE/STRONG based on harshness+trust). Override history tracking with dispatch honesty notes.
- **`backend/game_logic/diplomatic_templates.py`** (MODIFIED): 19 new template entries (T21-T27). T21 pre-proposal objections, T22 sabotage confrontation, T23 sabotage overlook. T24-T27 enemy diplomat voice templates (HAWK/SCHEMER/DOVE/LOYALIST Ã— ACCEPT/COUNTER/REJECT). Enemy voice resolution functions mapping diplomat personality to template selection.
- **`backend/game_logic/diplomatic_dialogue.py`** (MODIFIED): Pre-proposal objection merge into dialogue flow. MILD = flavor text prepended, MODERATE/STRONG = inline options replacing standard dialogue choices.
- **`backend/game_logic/dispatch.py`** (MODIFIED): 3 new dispatch fields (talleyrand_discovery, talleyrand_override_note, talleyrand_redemption). Discovery check during Morning Dispatch with confrontation dialogue routing. Override dispatch notes ("pessimistic"/"prescient"). Redemption event triggering.
- **`backend/models/world_state.py`** (MODIFIED): 3 new fields (talleyrand_defiance_cooldown, pending_talleyrand_sabotage, talleyrand_override_history). Serialized with backward compat. Cooldown decrement + sabotage turns_hidden tracking in advance_turn.
- **76 new tests** in `tests/test_session6_diplomacy.py`: 15 test classes covering defiance probability (7), sabotage types (6), discovery (4), confrontation (2), cooldown (3), pre-proposal objection (7), honesty problem (4), redemption (9), enemy diplomat voices (12), template slots (7), serialization (5), proposal harshness (4), dialogue merge (2), sabotage tracking (2), loyalist floor (2).
- **4855 tests passing** (4779 + 76 new, 3 skipped, 0 regressions).

### Mar 4 â€” Session 4: AI Proposals + Counter-Offers + Advisory + Proactive Suggestions

Phase 8 Session 4 implementation. 2 new files, multiple modified files, 43 new tests.

- **`backend/ai/ai_diplomacy.py`:** AI diplomatic proposal engine. P1-P7 trigger table (war exhaustion, opportunity, relationship thresholds, trade potential, threat response, alliance building, subsidy requests). Anti-spam cooldowns per nation per action type. Queue system: max 3 pending proposals, 3-turn expiry for unanswered proposals.
- **Counter-Offer Algorithm (M3):** AI evaluates player counter-offers: remove worst clause from player perspective â†’ recalculate acceptance â†’ add cheapest desired clause â†’ accept/reject based on updated score. Accept/Reject/Counter-offer actions wired into dialogue handler.
- **`backend/ai/diplomatic_advisory.py`:** Advisory conversation system. `detect_advisory_type()` classifies player queries (relationship status, proposal evaluation, strategic advice, treaty analysis, general). `generate_advisory()` produces context-aware Talleyrand responses. Wired into executor for "ask Talleyrand" command routing.
- **Proactive Suggestions (Talleyrand's Report):** New section in Morning Dispatch. 5 trigger types (expiring treaty, deteriorating relationship, diplomatic opportunity, threat warning, trade potential). Frequency caps to prevent spam. Integrated into `dispatch.py` builder.
- **Templates T11-T20:** 10 new diplomatic templates added to `diplomatic_templates.py` covering AI proposal presentations, counter-offer responses, advisory responses, and proactive suggestion formatting.
- **WorldState:** 4 new fields serialized (ai_proposal_queue, ai_proposal_cooldowns, advisory_history, proactive_suggestion_cooldowns). All with backward-compatible `.get()` defaults.
- **Turn Manager Integration:** AI diplomatic phase wired into `turn_manager.py` after enemy turns, before `advance_turn`. AI nations evaluate and generate proposals each turn.
- **Conflicting Alliance Resolution (Â§5b.3):** When AI proposes alliance conflicting with existing commitments, system detects and resolves per spec.
- **43 new tests** covering: AI trigger evaluation, cooldown enforcement, queue limits/expiry, M3 counter-offer algorithm, advisory type detection, advisory generation, proactive suggestion triggers, frequency caps, conflicting alliance resolution, serialization.
- **4697 tests passing** (4654 + 43 new, 3 skipped, 0 regressions).

### Mar 4 â€” Audit 4: Session 4 Verification

Post-Session 4 audit covering AI diplomatic proposals, M3 counter-offers, advisory system, Talleyrand's Report, and turn_manager integration.

- **Known gap resolved:** Integration test confirms end_turn â†’ AI diplomatic phase â†’ result dict wiring works correctly. AI proposal appears in result["ai_proposal"] when P1 trigger conditions are met.
- **27 new tests** in `tests/test_audit_session4.py`: turn_manager integration (3), cooldown lifecycle (4), counter-offer edge cases (3), advisory boundaries (7), dispatch Talleyrand edges (4), old save compatibility (1), conflict alert wiring (3), dead code detection (2).
- **Findings:** 0 bugs. 3 smells flagged (dead `tick_cooldowns()` function, Talleyrand war score trigger uses magnitude proxy instead of per-turn shift, `_try_add_desired_clauses` narrative mismatch). No blockers for Session 5.
- **Verdict: PASS.**
- **3 smells fixed (cleanup pass):** (1) Deleted dead `tick_cooldowns()` from ai_diplomacy.py. (2) Added `previous_war_scores` to WorldState for per-turn delta tracking; Trigger 2 now uses `abs(current - previous) >= 15` instead of magnitude proxy. (3) Clarified NATION_DESIRES / `_try_add_desired_clauses` intent via comments. 4 new tests for delta + serialization.
- **4728 tests passing** (4697 + 31 audit, 3 skipped, 0 regressions).

### Mar 4 â€” Audit 2+3: Sessions 2+3 Verification

Post-Session 3 audit covering diplomatic states, acceptance formula, diplomat class, Talleyrand commands, and conversational dialogue foundation. Full report: `docs/AUDIT_SESSION_2_3.md`.

- **3 structural checks** (1F, 1I, 1J): All PASS. POST route confirmed. Executor ordering correct (objection â†’ capture â†’ dialogue). advance_turn matches Â§7f (minor deviation: auto-downgrade before income â€” no functional impact).
- **29 new coverage gap tests** appended to `tests/test_audit_2_3.py`: Template fallback chain (9 tests), suggested terms generation (6 tests), resolve_template_text_with_type (2 tests), resolve_nation_name (3 tests), get_game_bucket branches (4 tests), get_transition_dp_cost paths (5 tests).
- **Diplomat table** added to `docs/SYSTEMS_REFERENCE.md` Â§16.
- **0 bugs found.** 4654 tests passing (4625 + 29 new, 0 regressions).
- **Verdict: PASS â€” ready for Session 4.**

### Mar 3 â€” Session 3: Talleyrand Commands + Conversational Dialogue Foundation

Phase 8 Session 3 implementation. 2 new files, 5 modified files, 76 new tests.

- **`backend/commands/diplomatic_dialogue.py`:** Conversation state machine (~300 lines). Handles 5 diplomatic action types (PROPOSE_TREATY, BREAK_TREATY, DEMAND_TRIBUTE, NEGOTIATE_TRADE, OFFER_SUBSIDY). Per-action state tracking (pending, accepted, rejected, counteroffered). Action prerequisites + validation (at_war, diplomatic_points, existing_treaty). Treaty history to prevent re-proposing. Berthier flavor text keyed by action + outcome.
- **`backend/commands/diplomatic_templates.py`:** 27 mock diplomat response templates (~500 lines). Templated by nation, action, diplomatic_points, military_advantage, relationship_delta. 5 placeholder slots: {name}, {nation}, {amount}, {treaty_type}, {reason}. Proper slot resolution with diplomatic context (DP costs, acceptance thresholds, breakdown analysis). Integration with `diplomatic_dialogue.py` for real-world flow.
- **WorldState:** 7 new fields (pending_diplomatic_action, diplomatic_action_state, current_dialogue, dialogue_history, treaty_history, diplomatic_ui_data, pending_counteroffter). All serialized with backward compat. Diplomatic processing wired into `advance_turn()`. Mission tracking for AI execution.
- **Parser:** Diplomatic command routing added to `parser.py`. Detects "propose treaty", "break treaty", "demand tribute", "negotiate trade", "offer subsidy" command patterns. Routes to diplomatic executor methods. Fuzzy matching on diplomat name and treaty type.
- **LLM client:** Diplomat response routing in `llm_client.py`. Context-aware prompt builder for diplomatic negotiations. Mock mode returns template-based responses per nation/action/advantage.
- **Executor:** 5 new `_execute_diplomatic_*()` methods for each diplomatic action. Validates state, charges DP costs, updates treaty history, generates dialogue via `diplomatic_dialogue.py`, propagates to frontend via `diplomatic_ui_data`.
- **Main.py:** `POST /diplomatic_action` endpoint. Accepts action type + target nation + diplomats involved. Returns diplomatic_ui_data for rendering.
- **Schemas.py:** Added `diplomatic_data` field to command response schema for frontend rendering.
- **76 new tests** (`test_diplomatic_dialogue.py`, `test_diplomatic_templates.py`, `test_diplomatic_commands.py`) covering: action prerequisites, state transitions, treaty history blocking, DP cost validation, template slot resolution, dialogue flow integration, AI mission execution, serialization.
- **4467 tests passing** (4391 + 76 new, 0 regressions).

### Mar 3 â€” Session 2: Diplomatic States + Acceptance Formula + Diplomat Class

Phase 8 Session 2 implementation. 2 new files, 3 modified files, 111 new tests.

- **`backend/models/diplomat.py`:** DiplomaticRepresentative class. 5 starting diplomats (Talleyrand/Castlereagh/Hardenberg/Metternich/Einsiedel) with personality/skill/trust/biography. Factory function for initialization.
- **`backend/game_logic/diplomacy.py`:** Core diplomatic engine (pure/deterministic). State transition validation (adjacency enforced, VASSAL requires OPEN_BORDERS+), war score calculation (territory Â±40, battles Â±30, decisive Â±20, capital Â±30, total Â±100), acceptance formula (7 components + military supremacy/battlefield diplomacy + special bonuses), DP economy (generation formula, cost table with skill penalties), war declaration + DEFENSIVE_ALLIANCE cascade, downgrade transitions with auto-downgrade tracking, trade income, movement restriction validation, battle recording for war score.
- **WorldState:** 10 new fields (diplomats, diplomatic_points, max_diplomatic_points, nation_authority, war_scores, battle_records, decisive_battles, armistice_cooldowns, previous_treaties, turns_below_threshold). All serialized with backward compat. Trade income + diplomatic processing wired into advance_turn.
- **Executor:** Diplomatic movement restriction in _execute_move. Auto-war-declaration in _execute_attack. Battle recording for war score after combat.
- **Gate criteria:** 13/13 met. Acceptance formula reproduces Â§6c (score < 30 â†’ REJECT). Trade income matches Â§1d for all 5 nations. Cascade: attack Austria â†’ Prussia enters WAR.
- **4389 tests passing** (4278 + 111 new, 0 regressions).

### Mar 3 â€” Post-1B Audit: War Gating Hardening

Audit of Sessions 1A+1B before proceeding to Session 2. Found 1 HIGH + 3 MEDIUM issues:

- **H1 (HIGH):** `get_enemies_in_region()` used `m.nation != nation` without `is_at_war()` check â€” neutral nations (Austria, Saxony) treated as enemies in 30+ call sites. **Fixed:** Added `self.is_at_war(nation, m.nation)` filter.
- **M1:** Enemy AI ~25 inline `m.nation != nation` checks in enemy_ai.py lacked war gating. **Fixed:** All inline checks now include `world.is_at_war(nation, m.nation)`.
- **M2:** `_find_nearest_enemy_for_nation()` (used for reckless cavalry) lacked war check. **Fixed:** Added war state filter.
- **M3:** Test fixtures for `test_ai_coordination.py` (synthetic "Coalition" nation) and `test_strategic_executor.py` (Austria as path blocker) needed diplomatic state entries. **Fixed.**
- **16 new regression tests** in `test_diplomatic_war_gating.py` covering: get_enemies_in_region war awareness, _find_nearest_enemy war filtering, AI neutral nation behavior (3 tests incl. 5-turn smoke), strategic path blocking.
- **4280 tests passing** (up from 4264).

### Mar 2 â€” Master Pre-Implementation Audit (All 3 Diplomacy Specs)

Final adversarial audit across DIPLOMACY_SPEC.md v2.2, CONVERSATIONAL_DIPLOMACY_DESIGN.md v1.2, and COALITION_SPEC.md v1.1. All specs approved for implementation.

- **Audit scope:** 5,514 lines across 3 specs. 14 edge cases stress-tested. Fun score: 81/100 (no blockers).
- **4 CRITICAL findings fixed:**
  - C1: `war_exhaustion` field was used in COALITION_SPEC Â§6a formula but never defined â€” added to Â§10a + DIPLOMACY_SPEC Â§13.
  - C2: Session plan mismatch (7 vs 8 sessions) â€” DIPLOMACY_SPEC Â§14 and CONV_DESIGN Â§14c updated to 8-session plan.
  - C3: Â§7f missing coalition processing â€” steps 9a-9d added (war exhaustion, threat accumulation, decay, coalition check).
  - C4: 5 coalition WorldState fields missing from DIPLOMACY_SPEC Â§13 â€” cross-reference block added.
- **4 MAJOR findings fixed:**
  - M1: "Coalition war score" undefined â€” formula defined in COALITION_SPEC Â§4c (army-weighted average).
  - M2: CONV_DESIGN Â§14c wrong session mapping â€” Dâ†’Session 8 (was 7).
  - M3: British subsidy dependency â€” moved from Session 8 deferred to Session 7 (Coalition) scope.
  - M4: Battlefield Diplomacy bonus missing from Â§6b â€” added as 9th acceptance component (+10 when war_score > 20).
- **5 minor fixes:** Instant overrides brewing note (Â§3d), alliance threat clarification (Â§2a), bilateral wars note (Â§5), universal dismiss option, mission-pause-during-confrontation.
- **Stale references cleaned:** 5 outdated session numbers corrected across DIPLOMACY_SPEC.
- **Design gates approved:** Coalition Spec v1.1 and Starting Situation Balance (R1-R5) both approved. Jealousy remains separate track.
- **DIPLOMACY_SPEC bumped to v2.3.** COALITION_SPEC confidence report updated.
- **Verdict: GO for Session 1A.**

### Mar 1 â€” COALITION_SPEC.md v1.1 (Drafted + Audit-Revised)

Coalition system design spec created as companion to DIPLOMACY_SPEC.md v2.2. Comprehensive adversarial audit applied same session.

- **COALITION_SPEC.md v1.1 â€” AUDIT-REVISED.** 16 sections (+Â§16 Balance Analysis), 15 edge cases, 95/100 confidence. Covers: threat accumulation (9 sources including per-path vassalage, 7 reductions), coalition formation (40/60/80 thresholds with 3-turn brewing window + processing order), Option B leader system (leader sets strategic posture), coalition AI (no shared fog, convergence bias, historical friction), 4 breaking methods (separate peace, decisive victory, diplomatic wedge, Continental System), dissolution rules (2+ member persistence, 5-turn cooldown), implementation file locations (Â§10e).
- **v1.1 audit fixes (10 findings):** 3 CRITICAL (loyalty penalty formula, vassalage threat mismatch, decisive battle threshold), 4 MAJOR (leadership score units, British subsidy criteria, session naming, decay self-count, processing order), 3 MINOR (friction int(), worked example, edge cases).
- **Balance analysis (Â§16):** 5 diplomatic paths analyzed (Saxony/Prussia/Austria/Britain/diplomatic victory). 5 recommendations (R1-R5): Saxony 18k, Austria-Britain NON_AGGRESSION, Prussia -40, battlefield diplomacy bonus, Saxony OPEN_BORDERS starting state. R1/R2/R4/R5 APPLIED to DIPLOMACY_SPEC Â§1c/Â§1e. R3 specified but pending Â§6b addition. Design gate required for all.
- **DIPLOMACY_SPEC edits:** Â§1c Reynier 10kâ†’18k, manpower pools updated, force balance updated. Â§1d economy tables updated (France +50 income from Saxony OB, Saxony upkeep recalculated). Â§1e starting states: France-Saxony PEACEâ†’OPEN_BORDERS, Britain-Austria DEF_ALLIANCEâ†’NON_AGGRESSION, France-Prussia -60â†’-40.
- **Session plan:** Coalition features in Session 7 (unified numbering with DIPLOMACY_SPEC). ~35-45 tests estimated.
- **STATUS.md, ROADMAP.md, CLAUDE.md updated.**

### Mar 1 â€” Diplomacy Readiness Audit + Design Gate Approvals

Comprehensive audit of diplomacy implementation readiness. Both specs approved for implementation.

- **DIPLOMACY_SPEC.md v2.2 â€” APPROVED.** Fixed Â§1b heading (18â†’19 regions), removed duplicate Milan from ASCII art.
- **CONVERSATIONAL_DIPLOMACY_DESIGN.md v1.2 â€” APPROVED.** Session plan unified with DIPLOMACY_SPEC.
- **Session plan reconciled:** Merged DIPLOMACY_SPEC's 6 sessions + CONV_DESIGN's 4 sessions into unified 7-session plan (eliminated duplication where conversation layer builds on mechanical sessions).
- **ADDING_CONTENT.md expanded** (+586 lines): New sections for Adding Diplomatic Representatives, Adding Diplomatic Actions, Adding Dialogue Templates. Expanded "Adding New Nations" from 3 steps â†’ 12 steps with validation checklist.
- **CLAUDE.md updated:** Design gate approved, conversation layer files added to file reference table.
- **No code changes.** Documentation-only session.

### Mar 1 â€” Region Data Rationalization

Centralized hardcoded region data into `region.py` REGIONS_DATA (single source of truth). Added `starting_controller`, `grid_position`, `NATION_CAPITALS`, `get_starting_controllers()`. Files that previously required manual sync now auto-derive: `parser.py` (known_regions), `strategic_parser.py` (REGION_POSITIONS), `world_state.py` (_setup_initial_control), `enemy_ai.py` (capital lookups), `turn_manager.py` (victory thresholds), `executor.py`/`disobedience.py` (capital references). New `tests/test_map_consistency.py` validates Godot map.gd stays in sync with backend. Files-to-touch for map expansion reduced from ~10 to ~3. Updated ADDING_CONTENT.md throughout. **4211 tests passing.**

---

## Phase 7b Sessions

### Feb 26 â€” Strategic Order UI (Orders Tab in Strategic Ledger)

**4208 tests (3 skipped). New "Orders" tab (tab 6) in Strategic Ledger with consolidated order view and cancel buttons.**

- **Backend `_build_orders()`:** New section builder in `ledger.py`. Returns active orders (marshal, order type, target, path remaining, condition text, issued/arrived turn) followed by idle marshals. Helper functions: `_derive_order_display_name()`, `_derive_condition_text()` (reads StrategicCondition for human-readable status).
- **`POST /cancel_order` endpoint:** New endpoint in `main.py`. Takes `{"marshal": "Ney"}`, calls existing `_execute_cancel()`. AP pre-check rejects at 0 AP. Deducts 1 AP on success (matches typed cancel cost). Respects `no_action_cost` for graceful cancels (no active order).
- **Godot Orders tab:** 6th tab button in `strategic_ledger.tscn`. `strategic_ledger.gd` updated: `@onready` ref, `tab_buttons` array, `KEY_6` handler, `_render_orders()` with BBCode `[url=cancel:MarshalName]` meta links for cancel buttons. Cancel buttons greyed out (non-clickable) when AP = 0. `meta_clicked` signal wired for cancel â†’ refresh flow.
- **`cancel_strategic_order()`:** New POST function in `api_client.gd`.

**Files modified:** `ledger.py` (_build_orders + helpers + return dict), `main.py` (POST /cancel_order), `strategic_ledger.tscn` (OrdersTab node), `strategic_ledger.gd` (tab 6 + render + cancel wiring), `api_client.gd` (cancel_strategic_order).

### Feb 26 â€” Strategic Compromise First-Step + Timed SUPPORT Timer Fix

**4208 tests (3 skipped). Fixed two bugs in strategic compromise orders.**

- **Bug 1: Compromise orders skip first-step execution.** All compromise paths in `_handle_strategic_objection_response` created the `StrategicOrder` but never executed immediate movement. Normal strategic orders move on issuance turn; compromise orders sat idle for a turn. Fixed by adding first-step movement block to the compromise handler. Affects all 4 order types (MOVE_TO, PURSUE, HOLD, SUPPORT).
- **Bug 2: Timed SUPPORT timer counts travel time.** `_check_condition` used `started_turn` for `max_turns` expiry. A 3-turn timed SUPPORT issued 2 hops away gave only 1 turn of actual support. Fixed by adding `arrived_turn` field to `StrategicOrder` â€” set when SUPPORT marshal first co-locates with ally, used as timer anchor in `_check_condition` for SUPPORT orders. Timer doesn't start until arrival.
- **Compromise message fix:** Timed SUPPORT compromise previously said "agrees to hold position" â€” now says "agrees to support {target}".
- **V2B spec fix:** Trust choice incorrectly said "AP refunded" â€” AP is never charged during objection (deferred). Fixed to accurate description.

**Files modified:** `marshal.py` (arrived_turn field + serialization), `strategic.py` (_check_condition SUPPORT timer, _execute_support arrival recording), `executor.py` (compromise first-step block, normal SUPPORT arrived_turn recording), `V2B_DEFIANCE_SPEC.md`, `SAVE_FORMAT_REFERENCE.md`, `test_strategic_bugfixes.py` (+7 tests).

### Feb 26 â€” V2b: Redemption Frontend Wiring + Integration Tests

**4201 tests (3 skipped). Audited all redemption paths, fixed Godot frontend gaps, added integration tests.**

- **Godot `_on_command_result`:** Added missing `redemption_event` check for bombardment friendly fire and non-end-turn commands. Previously, redemption dialog was never shown for these paths.
- **Godot end-turn chain:** Added deferred redemption checks at all 3 terminal points: `_on_enemy_phase_dismissed`, `_on_strategic_report_dismissed`, `_process_next_interrupt`. Cavalry trust penalty redemption now shows after enemy phase/reports/interrupts.
- **Godot `_on_interrupt_response`:** Added `redemption_event` check for fresh strategic interrupt responses where trust penalty crosses threshold.
- **Morning dispatch fix:** Added missing `_show_pending_dispatch()` calls in interruptâ†’redemption exit paths (Locations 4+5).
- **Administrative guard:** `check_redemption_threshold()` now blocks administrative marshals (out of play, strength=0).
- **3 integration tests:** Full executor-level verification that `_execute_bombardment` and `_execute_end_turn` propagate `redemption_event` to top-level result dict.

**Files modified:** `main.gd` (5 insertion points + 2 dispatch fixes), `disobedience.py` (admin guard), `test_redemption_v2b.py` (+4 tests: admin guard + 3 integration).

### Feb 26 â€” V2b: Redemption Audit Fixes (B2/B5/F1/F2)

**4197 tests (3 skipped). Fixed all audit findings from redemption V2b review.**

- **B2 (autonomous guard):** `check_redemption_threshold()` now returns None for autonomous marshals â€” prevents redundant popup during autonomy.
- **B5 (multi-marshal bombardment):** Replaced `or`-chain with first-wins guard (`if not friendly_fire_redemption`). Second marshal's trust still drops but doesn't get stuck with `redemption_pending = True`.
- **F1 (strategic interrupt wiring):** All 7 trust-penalty return sites in `strategic.py` now call `_attach_redemption_if_needed()`. Added `redemption_event` pass-through to `/strategic_response` endpoint in `main.py`.
- **F2 (cavalry wiring):** Both cavalry forced-stance and forced-unfortify `-3` penalties in `world_state.py` now call `check_redemption_threshold()`. Events hoisted through `tactical_events` in `_execute_end_turn`.
- **7 new tests:** Autonomous guard, strategic cancel triggers/doesn't trigger, cavalry stance/fortify/no-trigger, multi-marshal first-wins.

**Files modified:** `disobedience.py` (autonomous guard), `executor.py` (bombardment first-wins + tactical_events hoist), `strategic.py` (helper + 7 return sites), `world_state.py` (2 cavalry sites), `main.py` (/strategic_response pass-through), `test_redemption_v2b.py` (+7 tests).

### Feb 26 â€” V2b: Redemption System Interaction Gaps + 5-Turn Cooldown

**4190 tests (3 skipped). Fixed V2b defiance paths bypassing redemption event propagation. Added centralized helper + 5-turn cooldown.**

- **Bug:** V2b defiance early-return branches in executor.py bypassed redemption propagation â€” `redemption_pending` got stuck True because events were created but never delivered to frontend.
- **Centralized helper:** `check_redemption_threshold()` in `disobedience.py` â€” single gate for trust <= 20, not pending, not on cooldown, player-only. Replaces 7-line inline checks.
- **3 executor.py insertion points:** Tactical defiance success (Gap 1-2), strategic defiance success (Gap 3), strategic endpoint fallthrough (Gaps 4-5).
- **Bombardment refactor:** Replaced inline bombardment collateral check with centralized helper call.
- **5-turn cooldown:** `redemption_cooldown_until = current_turn + 5` set on resolution. Prevents rapid re-trigger spam.
- **18 new tests:** `test_redemption_v2b.py` â€” threshold helper (8 tests), cooldown lifecycle (3), tactical defiance (1), strategic defiance (2), bombardment regression (2), serialization (2).

**Files modified:** `marshal.py` (new field), `disobedience.py` (helper + cooldown), `executor.py` (3 wiring points + bombardment refactor), `SAVE_FORMAT_REFERENCE.md`, `SYSTEMS_REFERENCE.md`, `test_redemption_v2b.py` (new).

### Feb 26 â€” V2b Audit Pass 4: Post-Objection Routing Audit

**4172 tests (3 skipped). Audited `_execute_post_objection()` â€” the OUTPUT side of objection resolution. 1 BUG fixed, 2 GAPs closed, routing table documented.**

- **BUG (AP pre-check):** Admin actions (recruit/build/repair) in `_execute_post_objection` were gated on military AP pool (`world.actions_remaining`). With 0 military AP but >0 admin AP, these would be wrongly rejected. Split pre-check: admin actions check `admin_actions_remaining`, military actions check `actions_remaining`.
- **GAP (bombardment handler):** Added bombardment to the elif chain â€” finds nearest enemy, calls `_execute_bombardment`. Unreachable today (no personality generates bombardment as alternative) but prevents silent "Unknown action" if reached.
- **GAP (garrison handler):** Added garrison to the elif chain â€” routes to `_execute_garrison(command, game_state)`. Same rationale.
- **Verified clean:** Defiance signature parity (tactical/strategic identical), trust change timing (intentionally before execution), `_trust_penalty_applied` flag scoping, re-entrant objection prevention, marshal field injection, `target_stance` field preservation.
- **7 new tests:** `TestPostObjectionRoutingAudit` â€” admin AP gate (recruit/build/repair at 0 military AP), military AP gate, admin AP exhaustion, bombardment handler, garrison handler.
- **Routing table added to SYSTEMS_REFERENCE.md** â€” 19-row table covering all action handlers, AP pools, and signatures.

**Files modified:** `executor.py` (AP pre-check split + bombardment/garrison handlers), `test_objection_v2.py` (7 new tests), `SYSTEMS_REFERENCE.md` (routing table), `STATUS.md`.

### Feb 26 â€” V2b Audit Pass 3: Master Rules + Exhaustive Combo Audit

**4165 tests (3 skipped). Exhaustive audit of every personality Ã— action combination through V2 trigger + V1 alternative/compromise. Two master rules implemented. 10 flagged issues fixed, 4 design notes documented.**

**Master Rule #1 â€” Validate before suggesting:** New `_can_execute_suggestion()` helper validates every fallback candidate. New `can_fortify()` helper. `can_drill()` now checks aggressive stance. All fallback chains loop through candidates, skip invalid options, return first valid.

**Master Rule #2 â€” Exhaustâ†’MILD demotion:** Post-alternative-generation check in executor. If preferred==compromise, or preferred==original, or no valid alternatives exist â†’ demote to MILD (grumble, no popup). Never show popup with fake choices.

**10 issues fixed:** âš ï¸1 (aggressive preferred==compromise across 6 actions), âš ï¸2 (already in aggressive stance), âš ï¸3 (drill suggested but blocked by aggressive stance), âš ï¸4 (cautious fortify both=defend), âš ï¸5 (aggressive retreat mood variance), âš ï¸6 (aggressive stance_change mood variance), âš ï¸8 (cautious move already fortified), âš ï¸9 (cautious defend all-buttons-identical), âš ï¸10 (cautious fortify artillery both=defend).

**4 design notes documented:** D1 (fog disconnect V2â†”V1 â€” TODO comment added), D2 (balanced/loyal V1 triggers orphaned â€” comment added), D3 (universal form_square MILD suppresses aggressive MODERATE â€” intentional, comment added), D4 (COMPROMISE_RULES gaps â€” caught by Master Rule #2).

**Files modified:** `disobedience.py` (`_can_execute_suggestion`, `can_fortify`, `can_drill` stance check, `_generate_alternative` rewrite, `_find_compromise` rewrite), `executor.py` (Master Rule #2 demotion block), `objection_v2.py` (design comments D2/D3).

### Feb 26 â€” V2b Audit Pass 2: Objection Table Gaps + Defiance Wiring

**1 new test (updated), 4165 total (3 skipped). Comprehensive audit of objection alternative tables, defiance wiring, and trust modification paths. 23 issues found and fixed.**

- **C1 (CRITICAL):** `stance` action name â†’ `stance_change` with `target_stance` field in disobedience.py alternative generation.
- **C2 (CRITICAL):** `form_square` added to `objection_actions` in executor.py with pre-validation guards (already in square, cavalry, artillery).
- **H1 (HIGH):** Defiant attack now resolves nearest enemy target via `world.find_nearest_enemy()` instead of calling `_execute_auto_assign_attack()` with no target. Falls back to wait if no enemy found or attack fails.
- **M1-M4:** Scout target resolves marshal nameâ†’region. Aggressive+drill preferred diversified (move toward enemy/stance_change). No-enemies aggressive fallback returns `stance_change(aggressive)` instead of `defend`. Drill suggestions check prerequisites.
- **L1-L3:** Strategic trust paths use `_execute_post_objection()` to avoid re-entrant objections. `trust.modify()` â†’ `modify_trust()` in defiance.py (3 locations) and executor.py (4 locations) to preserve redemption clearing.
- **N1-N7:** Free actions synced in post-objection. Admin AP routing in post-objection. Defiance AP charges for defiant action (not original). Broken/retreating guard before defiance roll. Dead code removed from objection_v2.py.
- **Final re-audit (6 additional):** Empty popups when V2 triggers MODERATE+ but V1 has no handler (aggressive HOLD+enemies, SUPPORT defensive target). Hold/wait/form_square aggressive handlers added. Compromise dedup logic prevents Trust=Compromise duplicates.
- **Compromise rules updated:** `(move, attack)â†’defend` (hold ground), `(defend, retreat)â†’fortify` (dig in).

**Files modified:** `disobedience.py` (12+ edits), `executor.py` (14+ edits), `defiance.py` (3 edits), `objection_v2.py` (dead code removal), `test_v2b_session1.py` (MockMarshal fix), `test_objection_v2.py` (updated expectation).

### Feb 25 â€” V2b Session 3: Frontend + Polish + UI Tests

**0 new tests (frontend-only session), 4164 total (3 skipped). V2b fully wired to Godot â€” defiance, authority, and vindication visible in-game. Gate 6 UI test checklist expanded.**

- **Defiance display (main.gd):** Bordered "DEFIANCE" block in terminal output when marshal defies. Shows defiance action, outcome label (VINDICATED/FAILURE/INCONCLUSIVE/DISCIPLINE HELD), Berthier flavor text, trust/authority stat changes. Color-coded by outcome (green right, red wrong, neutral inconclusive). Authority threshold events displayed as separate bordered "AUTHORITY" block.
- **Authority display (ledger + dispatch):** Authority value + label (Strong/Normal/Weak) added to strategic ledger Forces tab header (`ledger.py` + `strategic_ledger.gd`), morning dispatch SITUATION section (`dispatch.py` + `main.gd`), and dispatch re-read screen (`dispatch_view.gd`). Color-coded: green â‰¥80, neutral 50-79, red <50.
- **Vindication display:** Already wired in Sessions 1-2 (marshal management cards show vindication score with color coding). No changes needed.
- **Gate 6 UI test checklist:** Expanded from ~10 items to 45+ items across 8 categories: Defiance Display, Vindication Display, Authority Display, Relationship SUPPORT, Fog-Aware Objections, Notification & Log, Regression Checks.
- **Doc updates:** STATUS.md, SYSTEMS_REFERENCE.md (V2b frontend display table), SAVE_FORMAT_REFERENCE.md (version bump), CLAUDE.md (phase status), PHASE7_UI_TEST_GATE.md (Gate 6 expanded).

**Files modified:** `main.gd` (defiance + authority display, objection response handling), `strategic_ledger.gd` (authority in forces header), `dispatch_view.gd` (authority in situation), `ledger.py` (authority fields), `dispatch.py` (authority fields).

### Feb 25 â€” V2b Session 2: Fog-of-War Migration

**88 new tests, 4164 total (3 skipped). Objection system now fog-aware â€” marshals object based on what they can see, not omniscient data.**

- **Step 1 â€” Fog infrastructure:** Added `_get_region_visibility()` helper (Step 0 rule: own region always FULL). Added `get_target_intel_level()` for Type B target queries. Rewrote `get_visible_enemies_near()` to return fog-filtered dicts (name, strength, visibility, location) instead of raw marshal objects. At PARTIAL, strength replaced by band midpoint (2500/10000/27500/55000/85000).
- **Step 2 â€” Type A scan queries (3 leaf â†’ 3 auto-propagate):** Rewrote `_check_enemy_adjacent()`, `_get_friendly_to_enemy_ratio()`, `_path_crosses_enemy()`/`_path_has_enemies()` to use fog-filtered data. Only PARTIAL+ enemies detected. Zero visible enemies â†’ ratio 999.0. Auto-propagated: `_get_enemy_to_friendly_ratio()`, `_is_outnumbered_2to1()`, `_is_actually_threatened()`.
- **Step 3 â€” Type B target queries (2 functions):** Rewrote `_get_attack_odds_ratio()` (FULL=exact, PARTIAL=band midpoint, STALE/UNKNOWN=1.0) and `_check_attack_target_fortified()` (only True at FULL visibility).
- **Step 4 â€” Fog-specific triggers (4 new):** #9: Cautious attack UNKNOWN â†’ STRONG. #10: Attack STALE â†’ cautious MODERATE, aggressive MILD. #11: Scout-shows-weakness handled by fog-filtered ratio logic (no visible enemies = "defending nothing"). #12: PURSUE no intel â†’ cautious STRONG, aggressive MILD.
- **MockWorld upgraded:** Added `_MockRegionIntel`, `get_region_intel()`, `set_region_visibility()` to test mock, defaulting to FULL visibility to preserve all pre-fog tests.
- **Edge cases verified:** Step 0 own-region rule, PARTIAL band midpoints, UNKNOWNâ†’999.0 ratio, mixed-visibility paths, fortification hidden below FULL, `_check_enemy_in_region()` unchanged, aggressive ignores fog for attacks.

**Files modified:** `objection_v2.py` (9 functions rewritten + 4 new triggers + fog imports/helpers), `test_objection_v2.py` (MockWorld fog support).
**Files created:** `tests/test_v2b_fog_migration.py` (88 tests, 19 classes).

### Feb 25 â€” Session 67: Square Formation (Tactical Triangle Part A)

**48 new tests, 3926 total (3 skipped). Infantry can now form square â€” devastating vs cavalry, vulnerable to artillery.**

- **Form Square action (1 AP):** Infantry-only (not cavalry, not artillery). Sets `square_formation = True`. Mutually exclusive with fortified. Cancels active strategic orders (including HOLD with holding_position/hold_region clearing). Blocked when broken, retreating, drilling, already in square.
- **Break Square action (0 AP, free):** Clears `square_formation`. Free action â€” doesn't consume AP.
- **Auto-break:** Square automatically breaks on any active order (attack, move, fortify, drill, recruit, garrison, stance_change, glorious_charge). Preserves immersion â€” marshals don't stay in square while marching.
- **Combat interactions:** Cavalry attacking square suffers -40% damage (`shock_multiplier *= 0.60`). Artillery attacking square deals +50% damage (`shock_multiplier *= 1.50`). Square provides +5% defense modifier. Both normal and deferred casualty paths handle these.
- **Bombardment:** +50% bombardment damage vs square (`square_bombardment_bonus = 1.50`). Extra -15 morale penalty (total -18: 3 base + 15 square). Packed formation = perfect artillery target.
- **Coordination:** Square marshals contribute defense-only coordination (0% attack, same as fortified). Excluded from adjacent ally support count. Cannot reinforce while in square (Rule #15).
- **V2a objections (4 triggers):** Aggressive objects to form_square â†’ MODERATE ("Let me CHARGE them!"). Cautious objects when fortified â†’ MILD. Cautious objects when artillery adjacent but no cavalry â†’ MILD. Universal: both cavalry AND artillery adjacent â†’ MILD.
- **Enemy AI (P2.5):** Between P2 (survival) and P3 (threats). Infantry forms square when enemy cavalry adjacent + no enemy artillery + cooldown expired. Breaks square when no cavalry threat. Anti-oscillation cooldown of 2 turns after breaking.
- **Battle report:** 3 new Berthier observation categories (square_cavalry_repulsed, square_artillery_punished, square_held_defense). Snapshot entries for cavalry penalty, artillery bonus, and defense bonus.
- **Serialization:** `square_formation` field in `to_dict()`/`from_dict()` with `.get()` default False.
- **Tactical state clearing:** Square clears on broken/retreat in `_process_tactical_states()`. AI cooldown decrements per turn.

**Files modified:** `marshal.py` (field, defense modifier, serialization), `combat.py` (cavalry -40%, artillery +50%, deferred path fix), `executor.py` (form_square, break_square, auto-break, bombardment bonus, coordination exclusions, reinforcement rule, SUPPORT advisory), `world_state.py` (AP costs, tactical state clearing), `objection_v2.py` (4 triggers), `enemy_ai.py` (P2.5), `battle_report.py` (3 observations, snapshots), `validation.py`, `parser.py`, `llm_client.py` (mock keywords).
**Files created:** `tests/test_square_formation.py` (48 tests, 12 classes).

### Feb 25 â€” Session 68: Auto-Bombardment + Overwatch (Tactical Triangle Part B)

**54 new tests, 3980 total (3 skipped). Artillery on SUPPORT auto-bombards before supported marshal's attack. Enemy artillery passively debuffs attackers (overwatch).**

- **Auto-Bombardment:** Artillery with SUPPORT order targeting attacker X fires `_execute_bombardment()` against defender BEFORE `resolve_battle()`. Same damage formula, collateral, fort degradation. Fires for both player and AI (Building Blocks). Does NOT consume AP. Increments `bombardments_this_turn`. Dead-defender early exit skips resolve_battle entirely.
- **Overwatch:** Enemy artillery in defender's region applies -3% attack per gun, capped at 3 guns (-9% max). Transient `overwatch_penalty` field on marshal, applied in `get_attack_modifier()` after coordination bonus. NOT serialized. Cleared via `_COORDINATION_FIELDS` after combat.
- **AI awareness:** `_evaluate_target_ratio()` factors overwatch into ratio calculation â€” discourages attacking well-defended positions with artillery overwatch.
- **Battle report:** 3 new Berthier observation categories (support_bombardment_effective, support_bombardment_minimal, overwatch_repelled). Overwatch penalty snapshot entry. `{artillery}` placeholder in `_fill()`.
- **Fog of war:** Auto-bombardment from adjacent region gives defender PARTIAL intel on source region via `update_intel_from_transit()`.

**Files modified:** `marshal.py` (overwatch_penalty in get_attack_modifier), `executor.py` (_calculate_overwatch, auto-bombardment loop, dead-defender check, _COORDINATION_FIELDS), `battle_report.py` (3 observations, snapshot, placeholder), `enemy_ai.py` (overwatch factor).
**Files created:** `tests/test_auto_bombardment_overwatch.py` (54 tests, 7 classes).

### Feb 25 â€” AI Recapture + Quality Fixes (Hotfix)

**35 new tests, 3877 total (3 skipped). Fixes AI failure to recapture lost territory ("Southern Bypass" exploit).**

Playtesting revealed the AI fails to recapture lost territory â€” the player could capture 5+ enemy regions completely unopposed. Seven fixes applied to `enemy_ai.py`:

1. **Capital-Elevated Homeland Defense:** When capital lost, P3.7 fires BEFORE P3 at priority 2 (survival-level). Capital recapture can't be blocked by cautious fortifying.
2. **Extended Range:** Homeland defense range increased from 3 to 6 hops; unlimited for capitals.
3. **P3 Throttling:** When 2+ regions lost, only 1 marshal per nation stays on P3 threat defense. Rest fall through to P3.7 recapture.
4. **Deathball Fix:** "Someone closer" check now requires the closer marshal to be *available* (not fortified/drilling/broken). Marshalâ†’target assignments tracked to split across multiple lost regions.
5. **Enemy Pathfinding:** Capital recapture allows movement through enemy-occupied regions if marshal has 50%+ of enemy strength.
6. **Stagnation Fix:** Skipped marshals (priority 999) now increment stagnation. Stagnation breaker returns `wait` instead of `None`.
7. **Cautious Advance Fix:** At stagnation >= 3, cautious advance fallback allows non-friendly territory (untraps map-edge marshals).

New helpers: `_is_capital_lost()`, `_count_lost_regions()`, `_nation_has_threat_responder()`. New tracking fields: `_recapture_marshal_assignments`, `_threat_responder_assigned`.

### Feb 24 â€” Session 66: Godot UI + Integration Audit

**32 new tests, 3799 total (3 skipped). UI integration for Phase 7 coordination features + cross-system audit + confidence report.**

- **Coordination readiness tooltip (map.gd):** Region tooltip now shows combined arms count and co-location status (dedicated vs accumulating) for player marshal pairs. Marshal tooltip shows color-coded relationship lines (Hostile=red, Rival=orange, Professional=white, Friendly=green, Devoted=gold).
- **Inline-dramatic reinforcement display (main.gd):** Gold-bordered BBCode blocks for reinforcement arrival (green) and failure (red). Zero new popup types per MULTI_MARSHAL_SPEC Â§14.
- **First-time coordination tutorial (executor.py + world_state.py):** Fires ONCE per campaign on first player combined arms attack (type_count >= 2). Tracked by `coordination_tutorial_shown: bool` on WorldState. Displays Berthier's report explaining combined arms, coordination improvement, and casualty sharing.
- **Enemy phase reinforcement display (enemy_phase_dialog.gd):** Reinforcement messages shown in enemy phase battle summaries.
- **Backend data for tooltips (world_state.py):** `get_game_state_summary()` now includes per-player-marshal `relationships` dict (value + label) and `co_location_turns` dict. All values `int()`-wrapped.
- **API passthrough (main.py):** `reinforcement_messages` and `coordination_tutorial` fields wired through POST /command response.
- **Reinforcement message polish:** Replaced internal reason codes (`literal_personality`, `fate_intervened`, `low_score`) with Berthier-voice narrative text. Removed raw score/threshold from arrival messages.
- **Integration audit:** Full cross-system confidence report. All Phase 7 areas scored â‰¥97%. No bugs found.

**Files modified:** `executor.py` (tutorial trigger), `world_state.py` (field + summary data), `main.py` (passthrough), `main.gd` (reinforcement + tutorial display), `map.gd` (tooltips), `enemy_phase_dialog.gd` (reinforcement display).
**Files created:** `tests/test_session66_integration.py` (32 tests: 7 classes covering serialization, tutorial trigger, game state summary, reinforcement messages, edge cases, full battle integration, filtered summary).

### Feb 24 â€” Gate 4 Remaining Fixes + Berthier Reinforcement Naming

**23 gate4 tests + 4 new observation tests, 3767 total (3 skipped). Two critical combat path bugs fixed + Berthier now names all reinforcers.**

- **Issue 4 â€” General attack bypasses Phase 7:** `_execute_general_attack_combat()` called `resolve_battle()` directly, skipping coordination/reinforcements/casualty distribution/relationships/reports. Rewritten to delegate to `_execute_attack()` (same pattern as auto-assign fix). Eliminated ~100 lines of duplicated combat code.
- **Issue 5 â€” Reinforcer stalemate stranding:** Reinforcers stayed in battle region after stalemate (neither `atk_lost` nor `atk_won` matched). Changed `if atk_lost:` â†’ `if not atk_won:` and `if atk_won:` â†’ `if not def_won:` so both sides' reinforcers return on any non-win.
- **Berthier reinforcement naming:** P0.7 observation now names ALL marshals who arrived and ALL who failed. New "mixed" template category for when some arrived and some didn't. E.g. "Davout arrived to reinforce Ney, but Grouchy failed to reach the field in time."
- **Test isolation fixes:** 2 pre-existing tests fixed to isolate marshals (Uxbridge at Waterloo contaminated force ratios).

### Feb 24 â€” Gate 4 Fixes (Post-Session 65)

**15 new tests, 3756 total (3 skipped). Three UI testing issues + reinforcer retreat-on-loss fixed before Session 66.**

- **Issue 1 â€” Berthier narrative voice:** Removed coordination modifier entries (Combined arms, Per-ally coordination, Dedicated coordination, Adjacent support, Coordination total) from `snapshot_attacker_modifiers()` and `snapshot_defender_modifiers()`. Coordination info now conveyed only through Berthier's narrative observation templates (already prose). Removed dead `coordination_preview` generation from executor. Detailed coordination numbers deferred to Battle History screen (Phase 8.5).
- **Issue 2 â€” Auto-routed attack missing coordination:** Rewrote `_execute_auto_assign_attack()` to delegate to `_execute_attack()` after finding nearest marshal (Building Blocks principle). Eliminated ~300 lines of duplicated combat logic. All attack paths now include full coordination, reinforcement, relationship, and battle report support.
- **Issue 3 â€” Artillery advancing on reinforcement:** Artillery reinforcing from adjacent no longer relocates to battle region. Provides fire support from adjacent position (not advance). Still gets `reinforced_this_turn` flag. Explicitly added to casualty distribution participants despite not being in battle region. **Coordination gap fix:** artillery NOT added to `arrived_names` (which becomes `exclude_from_adjacent`), so artillery still counts as adjacent ally for +2% attack bonus.
- **Issue 3b â€” Reinforcer retreat-on-loss:** Reinforcers who relocated to battle region now return to their origin if their side lost (spec: "reinforcer retreats with primary if battle lost"). Tracks pre-arrival locations in `reinforcer_origin` dict. After combat, if `atk_lost`, attacker-side reinforcers return; if `atk_won`, defender-side reinforcers return. Morale-based forced retreat (<=25) still runs first for broken armies.

**Files modified:** `battle_report.py` (removed coordination from modifier snapshots), `executor.py` (auto-assign delegation, artillery no-advance + coordination gap, reinforcer retreat-on-loss, coordination preview removal).
**Files created:** `tests/test_gate4_fixes.py` (15 tests: 3 Berthier narrative, 3 auto-assign delegation, 6 artillery reinforcement, 3 retreat-on-loss).
**Files updated:** `test_auto_assign_attack.py` (1 assertion fix), `test_battle_report.py` (4 tests), `test_combined_arms.py` (4 tests), `test_coordination_bonus.py` (2 tests).

### Feb 24 â€” Session 65: Full Battle Reports + Berthier Coordination Observations

**24 new tests (89 total in test_battle_report.py), 3741 total (3 skipped). Berthier now comments on coordination, reinforcements, relationships, and hostile dynamics.**

- **7 new observation categories** added to `_pick_observation()` priority chain:
  - P0.5: Full combined arms triangle (infantry + cavalry + artillery)
  - P0.7: Reinforcement arrival (ally marched onto the field)
  - P0.8: Reinforcement failure (ally failed to arrive)
  - P5.5: Hostile forced (hostile marshal fought alongside under SUPPORT order)
  - P12: Hostile refused (hostile marshal stood idle)
  - P13: Devoted synergy (devoted ally coordination bonus)
  - P15: Rival improved (relationship improvement after shared battle)
- **`_fill()` template system** converted from `.format()` to `.replace()` for graceful degradation. 4 new placeholders: `{ally}`, `{relationship}`, `{coordination_bonus}`, `{arrival_score}`.
- **Snapshot extensions:** `snapshot_attacker_modifiers()` and `snapshot_defender_modifiers()` originally captured per-ally coordination and dedicated coordination bonuses. **Removed in Gate 4 fixes** â€” coordination conveyed via narrative observation only; detailed numbers deferred to Battle History screen (Phase 8.5).
- **Coordination context injection:** `executor.py` injects `coordination_context`, `reinforcement_results_for_report`, and `relationship_changes` into `battle_result` dict after `resolve_battle()`. Observation re-picked with full data.
- **Pre-battle coordination preview:** Originally showed coordination bonus breakdown before battle resolves. **Removed in Gate 4 fixes** â€” Godot never consumed it; narrative observation handles coordination storytelling.
- **Reinforcement notification messages:** Added to executor result dict for Godot rendering (deferred to S66).
- **Two-pass observation picking:** Initial pick inside `resolve_battle()` (no coordination data), re-pick in `executor.py` after all data injected.

**Files modified:** `battle_report.py` (7 templates, `_fill()` rewrite, 7 priority levels, 2 snapshot extensions), `executor.py` (coordination injection, observation re-pick, preview, reinforcement messages).
**Files modified (tests):** `test_battle_report.py` (+24 tests in `TestCoordinationObservations` class).

### Feb 24 â€” Session 63: AI Coordination Enhancements

**35 new tests, 3720 total (3 skipped). AI now uses relationships and coordination awareness for smarter multi-marshal behavior.**

- **P4.6 Coordinated Attack Setup:** AI marshals move to stage coordinated attacks when solo ratio < 1.5x but combined with nearby allies (within 2 distance, relationship >= Rival) would exceed 1.5x. Returns MOVE toward nearest eligible ally.
- **P4.75 Relationship Filtering:** Ally support now excludes Hostile (-2) allies and prioritizes by relationship (Devoted > Friendly > Professional > Rival). Sorting ensures best relationships supported first.
- **P4.76 Co-Location Persistence Guard:** Inside `_consider_strategic_move()`, prevents marshal from moving away when co-located with ally near enemy threat and settled (not moved this turn). Falls through to wait/P8.
- **P4.77 Cross-Nation Adjacency Scoring:** Strategic movement now scores candidate positions by ally adjacency: Devoted +10, Professional/Friendly +5, Rival/Hostile 0. Applied as tiebreaker in aggressive, cautious fallback, and cautious advance paths. TODO-1805 comment for coalition detection.
- **P4.78 Defensive Reinforcement:** After P7, before P7.5. Moves adjacent to threatened Rival+ ally for reinforcement readiness. Prefers positions also adjacent to enemy. Returns None if already adjacent or ally not threatened.
- **Attack Threshold +8%:** `_find_attack_opportunity()` inflates effective ratio by +0.08 per co-located ally. Additive: solo 1.1 + 2 allies = 1.26. Personality thresholds unchanged.
- **Stagnation Override:** Artillery frontline penalty reduced when stagnation >= 3: unscreened -50 â†’ -20, screened -30 â†’ -10. Non-artillery unaffected.
- **Combined Arms Awareness:** +20 score bonus in P7 for positions completing the infantry/cavalry/artillery triangle (2 types present, marshal is 3rd).

**Files modified:** `enemy_ai.py` (5 new methods, 3 modified methods, 2 helper methods), `SYSTEMS_REFERENCE.md`, `STATUS.md`, `ENEMY_AI_REFERENCE.md`.
**Files created:** `tests/test_ai_coordination.py` (35 tests, 9 classes).

### Feb 23 â€” Post-S62 Hotfix: Artillery Positioning + Casualty Reduction

**22 new tests, 3685 total (3 skipped). Two artillery fixes from playtest observation.**

- **Artillery AI frontline avoidance:** `_score_artillery_position()` now penalizes front-line regions (adjacent to enemy territory). Unscreened frontline: -50. Screened frontline (co-located infantry): -30. New "behind-screen" bonus (+15) for non-frontline positions with adjacent infantry holding the front line. Fixes observed behavior of artillery advancing into freshly-conquered regions instead of staying in rear bombardment positions.
- **Artillery casualty reduction in combined arms:** `_distribute_casualties()` now applies 50% casualty reduction to artillery when fighting alongside non-artillery units (rear-position advantage). Remainder goes to strongest non-artillery marshal. No reduction when artillery fights alone or with only other artillery. `ARTILLERY_CASUALTY_FACTOR = 0.5` class constant.
- **Session 63 decisions resolved:** (1) Frontline penalty values (-50/-30): **Keep current values.** Tuning deferred to 1805 region wiring â€” more rear positions available at 80+ regions. (2) Stagnation breaker vs frontline avoidance: **Stagnation overrides with reduced penalty.** When artillery idle 3+ turns (stagnation counter active), reduce frontline penalty from -50 to -20 (reluctant but willing). Prevents artillery paralysis when front line collapses around it. (3) Cavalry screens and frontline penalty: **Already handled.** Screened frontline is -30 (vs unscreened -50), cavalry counts as screen. No further reduction needed.

**Files modified:** `enemy_ai.py` (`_score_artillery_position` frontline penalty + behind-screen bonus), `executor.py` (`_distribute_casualties` artillery reduction + `ARTILLERY_CASUALTY_FACTOR`).
**Files created:** `tests/test_artillery_hotfix.py` (22 tests, 5 classes).

### Feb 23 â€” Session 62: Casualty Distribution

**63 tests (47 original + 16 post-review), 3663 total (3 skipped). Multi-marshal battles now distribute casualties proportionally among participants. First Phase 7b session.**

- **`resolve_battle(apply_casualties=False)`:** New contract per C1/C2. Computes all combat math but defers 5 side effect categories (casualties, morale, battles_won/lost, counter-punch, recklessness) to caller. Returns raw casualties, morale deltas (as int), and projected-strength outcome.
- **Fortification degradation KEPT** inside resolve_battle (battle-triggered per C1).
- **C2 projected-strength victor:** Uses `attacker.strength - casualties` for outcome determination. 1.5 threshold matches normal path.
- **`_distribute_casualties()`:** Proportional by strength fraction. Remainder to strongest marshal. Cap at marshal strength. Sum matches raw total exactly.
- **`_get_casualty_participants()`:** Mirrors `get_battle_participants()` for D3 Hostile+SUPPORT detection. Must run BEFORE strategic orders cleared.
- **Per-participant effects:** Uniform morale delta (psychological), individual battles_won/lost, independent forced retreat check.
- **Primary-only effects:** Recklessness (attacker), counter-punch (defender), counter-punch mastery (Davout).
- **Pursuit damage** handled in executor for coordinated battles (primary attacker ability vs primary defender).

**Files modified:** `combat.py` (apply_casualties parameter + `_build_deferred_result`), `executor.py` (`_distribute_casualties`, `_get_casualty_participants`, `_execute_attack` coordination branch).
**Files created:** `tests/test_casualty_distribution.py` (63 tests, 8 classes).

**Post-review fixes (Opus code review):**
- **C-1 (CRITICAL):** Fixed `relationship.py` reading non-existent top-level `"attacker_casualties"` key. Now reads from nested `battle_result["attacker"]["casualties"]` (correct for both normal and deferred paths). Removed fake top-level keys from test helper `_make_battle_result()`.
- **W-1 (WARNING):** Moved SUPPORT order clearing in `executor.py` from before combat to after `process_battle_relationships()`, so Hostile+SUPPORT reinforcements participate in relationship checks.
- **W-2 (WARNING):** Documented rounding cap limitation in `_distribute_casualties()` (excess from overkill on small units not redistributed â€” acceptable as overkill).
- **16 new tests:** TG1 (primary destroyed), TG2 (asymmetric 2v1), TG3 (AI participants), TG5 (Davout non-primary), TG6 (conformance: nested keys, no top-level keys, deferred raw keys, relationship reads nested), W-1 timing (3 tests).

---

## Phase 7 Core Sessions

### Feb 23 â€” Session 64: Win/Loss Relationship Formula

**34 new tests, 3600 total (3 skipped). Shared battles now trigger relationship checks between co-located same-nation marshals. Phase 7 Core COMPLETE.**

- **`calculate_battle_severity()`:** Categorizes battles as decisive (ratio < 0.5), standard (0.5â€“0.8), or narrow (> 0.8) based on winner/loser casualty ratio.
- **`check_shared_battle_relationship()`:** WIN formula (base 30 + severity + rel_mod + variance Â±10) and LOSS formula (base 15 + severity + rel_mod + variance Â±10). Threshold strict `> 50` (M2). Returns Â±1 or 0.
- **Ordered pairs (D4):** Uses `itertools.permutations` â€” 3 marshals = 6 independent checks. Cooldown is per-direction (Aâ†’B independent of Bâ†’A).
- **Intentional asymmetry (M1/M2):** Hostile WIN max=35 (never improves). Devoted WIN max=35 (never improves). Hostile LOSS max=50 (never degrades â€” strict > 50). Rival decisive WIN ~24% improvement chance.
- **Cooldown:** 3 turns per direction, tracked in `last_relationship_change_turn` (serialized in S59).
- **Participants:** Same-nation marshals in battle region, excluding Hostile without SUPPORT. Primary always included.
- **Event logging:** Relationship changes logged via `world.log_event()` with type `"relationship_change"`.
- **Files created:** `backend/game_logic/relationship.py`, `tests/test_relationship_formula.py` (34 tests).
- **Files modified:** `backend/commands/executor.py` (wired into `_execute_attack()` after combat notifications, before destruction check).

### Feb 23 â€” Session 61b: Reinforcement Edge Cases + SUPPORT Objection Triggers

**22 new tests, 3566 total (3 skipped). Edge cases for reinforcement eligibility, Grouchy Rule upgrade, Berthier advisory, and SUPPORT objection triggers.**

- **Rule #12 â€” moved_this_turn (A-D2):** Marshals that already moved this turn cannot reinforce (prevents force-marching twice). Blocks artillery that moved from reinforcing.
- **Rule #13 â€” Hostile exclusion (A-D4):** Hostile marshals (relationship -2) without a SUPPORT order targeting the primary combatant are excluded from auto-reinforcement. Hostile WITH SUPPORT still passes eligibility (arrives for casualties, 0% coordination per D3).
- **Grouchy Rule PURSUE region-match (A-D1):** Upgraded from name-match to region-match. Grouchy with `PURSUE Wellington` now arrives at a battle where Wellington is present, even if the primary defender is Blucher.
- **Berthier fortified SUPPORT advisory (A-M3):** When SUPPORT is issued to a fortified marshal, Berthier warns they cannot march to reinforce. Informational only â€” does not block the order.
- **Â§6 SUPPORT objection triggers:** Two new triggers in `objection_v2.py`: aggressive personality objects to defensive SUPPORT (target fortified/cautious/broken â†’ MODERATE), cautious personality objects to reckless SUPPORT (target aggressive + recklessness â‰¥ 2 â†’ MODERATE).
- **Files modified:** `executor.py` (rules 12-13, PURSUE region-match, Berthier advisory), `objection_v2.py` (SUPPORT triggers), `test_reinforcement.py` (updated hostile trust test for A-D4).
- **Files created:** `tests/test_reinforcement_edge_cases.py` (22 tests across 7 classes).

### Feb 23 â€” Session 61a: Adjacent Reinforcement (Arrival Score & Base Reinforcement)

**49 new tests, 3544 total (3 skipped, 1 pre-existing flaky). Adjacent marshals physically reinforce into ongoing battles.**

- **Reinforcement system:** Adjacent same-nation marshals automatically attempt to join ongoing battles. 11 eligibility rules (same nation, adjacent, strength > 0, not broken, not retreated, not recovering, not fortified, not on HOLD, not engaged, not drilling, not already reinforced).
- **Grouchy Rule (personality gate):** Literal-personality marshals CANNOT reinforce unless they have a SUPPORT or PURSUE order targeting a battle participant. Checked before arrival score.
- **Arrival score formula:** `base(50) + logistics*5 + relationship_mod + terrain_mod + personality_mod + support_bonus + variance(Â±8)`. Variable threshold: 60 with SUPPORT/PURSUE order, 65 without.
- **Fumble roll (I3):** 5% failure chance even when score > 80 (`random.randint(1,20) == 1`).
- **Physical relocation:** Successful reinforcers move to battle region, set `reinforced_this_turn = True`, join coordination calculation. Strategic orders preserved through coordination, then cleared after (A-C2 ordering).
- **Path B2 dedicated support:** Arrived-via-SUPPORT reinforcers count for `_has_dedicated_support()` coordination check.
- **Trust penalty:** -3 trust on failed reinforcement (except Literal and Hostile personalities).
- **Both sides reinforced:** Attacker and defender independently receive reinforcements (Building Blocks â€” AI uses identical code).
- **Serialization (M4):** `reinforced_this_turn` field serialized, cleared at turn start.
- **Files modified:** `executor.py` (+`_is_reinforcement_eligible`, `_calculate_arrival_score`, `_calculate_reinforcements`, extended `_execute_attack`, extended `_calculate_coordination_context`, extended `_has_dedicated_support`), `marshal.py` (+`reinforced_this_turn`), `world_state.py` (turn-start clearing).
- **Files created:** `tests/test_reinforcement.py` (49 tests across 12 classes).
- **Regression fixes:** 3 existing integration tests needed isolation from reinforcement side effects (reinforcement pulls adjacent marshals during AI attacks). Fixed by marking test-specific marshals as `reinforced_this_turn = True` or relocating enemies.

### Feb 23 â€” Session 60: Adjacent Support

**23 new tests, 3495 total (3 skipped). Adjacent-region coordination bonus (attack-only).**

- **Adjacent support bonus:** Marshals in regions adjacent to a battle provide +2% attack per ally. Purely positional â€” NOT relationship-scaled. Fortified and HOLD marshals count (physically present). Same eligibility as coordination (not broken, not retreating, not recovering, strength > 0).
- **Attack-only (A-M2):** Adjacent support adds to `raw_atk` ONLY. Defenders benefit only from same-region allies, not adjacent ones.
- **Pipeline integration:** `_count_adjacent_allies()` calculates ONCE per battle (shared value for all marshals in region), added to coordination sum BEFORE hard cap. Display field `_display_adjacent_atk` set on all eligible marshals, already in `COORDINATION_FIELDS` cleanup list.
- **Future-proofing (S61):** `exclude_names` parameter on `_count_adjacent_allies()` for Session 61 reinforcement (arriving marshals removed from adjacent count).
- **Combat message:** Adjacent support displays in tactical prefix when active.
- **Battle report:** `_display_adjacent_atk` captured in attacker snapshot as "Adjacent support" modifier.
- **Files modified:** `executor.py` (+`_count_adjacent_allies`, extended `_calculate_coordination_context`), `combat.py` (adjacent support message), `battle_report.py` (adjacent support snapshot).
- **Files created:** `tests/test_adjacent_support.py` (23 tests across 7 test classes).

### Feb 23 â€” Session 59: Dedicated Coordination

**31 new tests, 3472 total (3 skipped). Co-location tracking + dedicated coordination bonus.**

- **Co-location tracking:** `_update_co_location_tracking()` in `world_state.py` runs per-turn BEFORE turn increment (A-D7). Tracks `co_location_turns` dict on each marshal: ally_name â†’ start_turn of co-location streak. Clears on separation, death, or broken status.
- **Dedicated bonus (Path A):** After 2+ consecutive co-located turns (`current_turn - start_turn >= 2`), marshal earns flat +5% attack / +5% defense. Doesn't scale with relationship or stack with multiple qualifying allies.
- **Dedicated bonus (Path B):** Active SUPPORT order targeting a marshal grants immediate +5%/+5%. One-directional per A-D3 â€” only the target gets the bonus, not the supporter. Mutual SUPPORT (4 AP) gives both.
- **Pipeline integration:** Dedicated bonus added to raw sum in `_calculate_coordination_context()` (combined arms + per-ally + dedicated), then hard-capped at +25% atk / +20% def. Display fields `_display_dedicated_atk`/`_display_dedicated_def` set on marshal, already in cleanup list.
- **Forward-compatibility field:** `last_relationship_change_turn` dict added to marshal (empty until Session 64 populates it). Serialization-enforced.
- **Files modified:** `marshal.py` (2 new Dict fields in `__init__`/`to_dict`/`from_dict`), `world_state.py` (+`_update_co_location_tracking`, call site in `_process_tactical_states`), `executor.py` (+`_has_dedicated_support`, extended `_calculate_coordination_context`), `tests/test_serialization_enforcement.py` (fixture updated).
- **Files created:** `tests/test_dedicated_coordination.py` (31 tests across 8 test classes).

### Feb 23 â€” Session 58: Per-Ally Coordination Bonuses

**44 new tests, 3438 total (3 skipped). Per-ally relationship-scaled coordination.**

- **Per-ally coordination:** Each eligible ally contributes +3% attack / +5% defense, scaled by relationship: Hostile(0.0) â†’ Rival(0.5) â†’ Professional(1.0) â†’ Friendly(1.25) â†’ Devoted(1.5). Asymmetric â€” each marshal gets their OWN total based on their relationships.
- **Fortification rule:** Fortified non-artillery allies give defense coordination only (0% attack). Fortified artillery gives both.
- **Hard cap enforced:** Combined arms + per-ally coordination summed, then capped at +25% attack / +20% defense. 3/3 France CA (20%) + 2 Professional allies (6%) = 26% â†’ capped at 25%.
- **S57 tests updated:** 4 tests updated to account for per-ally coordination being additive with combined arms.
- **Files modified:** `executor.py` (+`_calculate_per_ally_coordination`, `_RELATIONSHIP_SCALING`, extended `_calculate_coordination_context` for per-marshal asymmetric calculation), `tests/test_combined_arms.py` (4 updated tests).
- **Files created:** `tests/test_coordination_bonus.py` (44 tests across 11 test classes).

### Feb 23 â€” Session 57: Combined Arms Detection

**43 new tests, 3394 total (3 skipped). Phase 7 Core begins.**

- **Combined arms detection:** Count distinct unit types (infantry/cavalry/artillery) among eligible same-nation marshals in a region. 2 types = +10% atk / +5% def. 3 types = +20% atk / +10% def. France is the only nation capable of 3/3 (structural player advantage).
- **Transient field pattern (D5):** Coordination bonuses set dynamically via `_calculate_coordination_context()`, read via `getattr(self, field, 0.0)`, cleared after combat. NOT in `__init__`, NOT serialized.
- **Single multiplier (A-C1):** `total_coordination_attack_bonus` / `total_coordination_defense_bonus` â€” one line each in `get_attack_modifier()` / `get_defense_modifier()`. All future coordination sources (per-ally, dedicated, adjacent) sum into this single field, then cap at +25% atk / +20% def.
- **Both sides calculated (A-C3):** `_calculate_coordination_context()` called for attacker AND defender independently before `resolve_battle()`.
- **Bombardment excluded (A-D6):** Coordination not wired into bombardment path.
- **Files modified:** `executor.py` (+`_count_unit_types`, `_get_combined_arms_bonus`, `_calculate_coordination_context`, `_clear_coordination_fields`, attack wiring), `marshal.py` (1 line each in atk/def modifiers), `combat.py` (combined arms tactical_prefix message), `battle_report.py` (snapshot captures CA + total coordination).
- **Files created:** `tests/test_combined_arms.py` (43 tests across 8 test classes).

---

## Phase 6.5 Sessions

### Feb 22 (Davout Counter-Punch Mastery + Special Abilities Evaluation)

**Davout's "Counter-Punch Mastery" ability wired. 22 new tests, 3351 total.**

- **Ability:** +20% attack on next attack after Davout is attacked (any combat outcome, any target). Boolean `counter_punch_ready` field â€” set when defender in combat (if survived), consumed on next `get_attack_modifier()` call, cleared at turn end if unused.
- **Files modified:** `marshal.py` (field + ability definition + modifier), `combat.py` (trigger + result flag), `battle_report.py` (snapshot label), `marshal_overview.py` (`_WIRED_ABILITY_MARSHALS` + unit specifics), `world_state.py` (turn-end clearing + game state summary), `executor.py` (broken state clearing).
- **6 wired abilities total:** Ney (+2 shock), Davout (+20% counter-punch), Drouot (15% fort degradation), Wellington (+5% defense), Blucher (+3k pursuit), Uxbridge (+5k pursuit).
- **Special Abilities Evaluation complete:** `docs/SPECIAL_ABILITIES_EVALUATION.md` â€” 3 Davout designs proposed, existing abilities reviewed (all balanced for Phase 7), UI surface audit (5 manual / 6 auto), 1805 roster planning principles and candidate lists documented.
- **ADDING_CONTENT.md expanded:** "Wiring a Special Ability" 16-step checklist, common mistakes table, file audit.

---

### Feb 22 (Phase 6.5 UI Audit)

**Code quality audit of all Phase 6.5 menu systems. 9 new tests, 1 pre-existing fix, 3354 total.**

- **Audit scope:** Pause Menu, Campaign Log, Morning Dispatch, Notification Bar, Top Bar, Strategic Ledger, Marshal Management. Checked int() wrapping, serialization, input blocking, CanvasLayer ordering, edge cases, endpoints, test coverage, consistency.
- **Fixes (bugs):** `/campaign_log` endpoint missing `"success"` key + game state guard. `GET /notifications` missing game state guard. `test_marshal_overview.py::test_endpoint_no_game_returns_error` called `game_state.clear()` without restore, poisoning subsequent tests (caused pre-existing `test_recklessness_2_blocks_defensive_stance` failure).
- **Fixes (comments):** `campaign_log.gd` layer comment corrected (102 -> 50).
- **New tests:** 5 endpoint tests for `/campaign_log`, 4 endpoint tests for `/notifications`.
- **Tech debt documented:** `_format_number()` duplication (3 files), color palette duplication (3+ files), marshal scroll hardcoded 320px/card. All tagged for Map Renderer refactor. Added to ROADMAP.md Tech Debt table.
- **Hooks fix:** `.claude/settings.local.json` PostToolUse/PreToolUse hooks had bash `$(...)` quoting bug with nested Python parentheses â€” split into variable assignments.

---

### Feb 21 (Marshal Management UI)

**Card-based read-only marshal management screen. 68 new tests, 3320 total.**

- `backend/game_logic/marshal_overview.py` â€” `build_marshal_overview(world)` returns per-marshal data cards (identity, ability, combat stats, trust/standing, status, unit specifics, relationships). All values int()-wrapped.
- `backend/models/marshal.py` â€” `biography` field added to `__init__`, `to_dict()`, `from_dict()`. Historical blurbs set for all 9 marshals (Berthier's voice).
- `marshal_management.gd/tscn` â€” CanvasLayer 50, vertical scrollable card list, BBCode rendering, number keys 1-N jump to marshal.
- `main.py`: `GET /marshal_overview` endpoint.
- `api_client.gd`: `get_marshal_overview()` method.
- `top_bar.gd`: Generals button enabled, wired to marshal management screen.
- `main.gd`: Marshal management scene loaded and registered with top bar.
- Ability active derivation hardcoded by name (Ney/Drouot/Wellington/Blucher/Uxbridge = active). TODO: Replace with proper `Marshal.ability_wired` field (Phase 7b or Pre-EA).

---

### Feb 21 (Session B: Strategic Ledger)

**5-section strategic ledger backend + sub-tabbed Godot screen. 54 new tests, 3252 total.**

- `backend/game_logic/ledger.py` â€” forces, territories, economy, intel, manpower sections. Fog-filtered intel. `BAND_MIDPOINTS` for estimated strength.
- `strategic_ledger.gd/tscn` â€” CanvasLayer 50, 5 sub-tabs (number keys 1-5), color coding.
- `world_state.py`: `get_manpower_regen_rates(nation)` extracted as single source of truth.
- `main.py`: `GET /ledger` endpoint.

---

### Feb 21 (Session A: Top Bar Framework + Dispatch)

**Unified top bar UI framework. 8 new tests, 3198 total.**

- `top_bar.gd/tscn` â€” CanvasLayer 75 controller (Event Log, Ledger, Generals, Dispatch), notification area, turn counter.
- `dispatch_view.gd/tscn` â€” CanvasLayer 50 dispatch re-read (D key). `last_morning_dispatch` stored on WorldState.
- Campaign log refactored to layer 50, notification bar reparented into top bar.
- Input refactor: `_is_modal_dialog_open()`, `_is_screen_open()`, `_is_hotkey_blocked()`.
- Hotkeys: L (Event Log), T (Ledger), G (Generals placeholder), D (Dispatch).

---

### Feb 21 (Notification System + Audit)

**EU4-style persistent notification bar. 9 triggers, 3 priority tiers. 70 tests total (51 + 19 audit).**

- `backend/notifications.py` â€” NotificationCollector, 10 notification types, priority enum.
- `notification_bar.gd/tscn` â€” color-coded icons, expand/dismiss, backend sync.
- 9 triggers: strategic complete, forced retreat, friendly fire, reckless cavalry, counter-punch, manpower, elimination, bankruptcy, drill cancelled.
- Audit fixes: whitelist mismatch, missing passthrough (3 endpoints), accumulation prevention, auto-dismiss.

### Feb 20 (Morning Dispatch)

**Berthier's Morning Dispatch: structured turn-start briefing. 57 new tests, 3120 total.**

- `backend/game_logic/dispatch.py` â€” SITUATION, MARSHAL STATUS, INTELLIGENCE, Berthier note.
- Fog-filtered enemy strength ratio. Tactical events absorbed into dispatch. Both end-turn paths wired.

### Feb 20 (Campaign Log + Polish)

**Fog-filtered campaign event log with Godot overlay. 57 tests.**

- `backend/campaign_log.py` â€” 14-type whitelist, fog filter, one-liner formatter.
- `campaign_log.gd/tscn` â€” CanvasLayer overlay, turn-grouped expandable sections, L key toggle.
- Polish: nation tags on names, both-sides casualties, expand/collapse fix, empty turn hiding.

### Feb 20 (Wire Marshal Abilities + Phase 7 Prep)

- Drouot 15% fort degradation, Wellington +5% defense, Blucher 3k pursuit, Uxbridge 5k pursuit.
- Phase 7 pre-implementation audit: 20 findings (3 critical, 7 design gaps). `PHASE7_SPEC_AMENDMENTS.md` created.
- Phase 7 scoped to 6-session Core + deferred 7b.

### Feb 19 (Session 56: Pause Menu)

- Smart Esc pause menu overlay (CanvasLayer 101). Save/Load/Settings stub/Quit.

---

## Known Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| V1 global objection cap still active for strategic path | Low | `disobedience.py:25` MAX_MAJOR_OBJECTIONS_PER_TURN=2. Remove in V2b cleanup. |
| No mid-objection save/load roundtrip test | Low | Serialization enforcement confirms fields exist, but no test with populated V2 pending_objection. |
| Missing AI test coverage for P3, P4.75, P7 | Medium | P3 (threat response), P4.75 (ally support), P7 (strategic movement) have zero direct unit tests. |
| Residual 2-turn fortify oscillation possible | Low | `_unfortified_this_turn` only prevents same-turn re-fortify. Stagnation counter is backstop. |
| `requires_input` interrupt blocks later marshals | Low | `strategic.py:119` stops processing ALL further marshals when one requires input. |
| `full_game.py` dead code with stale terrain | Low | 3 `resolve_battle()` calls hardcode `terrain="open"`. File is dead code. |
| France hardcoded as player nation | Low | Multiple systems assume France. Post-EA multi-nation play requires threading player_nation. |
| `ability_active` hardcoded by marshal name | Low | `marshal_overview.py` derives ability_active from `_WIRED_ABILITY_MARSHALS` set. Replace with proper `Marshal.ability_wired` field. Pre-EA or Phase 7b. |
| `resolve_battle()` has 5 categories of side effects | High | Phase 7 `apply_casualties=False` must defer all 5. See `PHASE7_SPEC_AMENDMENTS.md` C1. |
| Cross-nation coordination impossible (Britain/Prussia) | Medium | Deferred to Phase 7b with Coalition Trigger. See `PHASE7_SPEC_AMENDMENTS.md` C3. |
| Missing SUPPORT objection triggers | Low | Add in Phase 7 Session 59. |

---

## Quick Commands

```bash
.\.venv\Scripts\python.exe -m pytest tests/ -v                      # Full suite
.\.venv\Scripts\python.exe -m pytest tests/ -v --tb=no -q          # Quick count
.\.venv\Scripts\python.exe -m pytest tests/test_objection_v2.py -v # V2 tests only
.\.venv\Scripts\python.exe backend/main.py                          # Backend on port 8005
```

---

## Document Map

| Need | Read |
|------|------|
| Phase timeline | `ROADMAP.md` |
| Phase 7 spec | `MULTI_MARSHAL_SPEC.md` |
| Phase 7 audit amendments | `PHASE7_SPEC_AMENDMENTS.md` |
| Game systems reference | `SYSTEMS_REFERENCE.md` |
| Enemy AI | `ENEMY_AI_REFERENCE.md` |
| V2b objection preview | `OBJECTION_V2.md` |
| Save format | `SAVE_FORMAT_REFERENCE.md` |
| Fog of war spec | `FOG_OF_WAR_SPEC.md` |
| Adding content | `ADDING_CONTENT.md` |
| Game vision | `VISION.md` |
| Future concepts | `FUTURE_DESIGN.md` |
| Modding | `MODDING_FORMAT.md` |
| Manual testing | `MANUAL_TEST_PLAN.md` |
| Tutorial content | `TUTORIAL_SCRIPT.md` |
| Playtest prompt | `PLAYTEST_EVALUATION_PROMPT.md` |
| Session history (archived) | `archive/SESSION_HISTORY.md` |
