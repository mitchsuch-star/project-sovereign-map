# War Settlement Ally Participation Implementation Plan

> **Status:** v1.5 READY FOR SLICE A - v1.8 synthesis-closure hardening applied
> **Last Updated:** April 28, 2026
> **Source spec:** `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.8

This plan is the coding handoff for Imperial Settlement / Ally Participation. It assumes BPH, WPS, and WB are landed and keeps the settlement system additive over pairwise `diplomatic_states`, `war_scores`, and WPS `war_objectives`.

## Scale Rules

- Target 13-20 active nations, 100+ regions, 78+ bilateral pairs, and 20 simultaneous pairwise wars.
- No settlement slice may add a per-turn scan of all regions for every war.
- Hot paths use active participants, direct term targets, direct beneficiaries, live bargain indexes, and affected regions only.
- Presentation emits one popup/rail beat per settlement family, not one per participant.
- A `diplo_key` can appear in at most one active `war_instance`; duplicate active instances are a hard stop.
- `war_id` values come from `world.next_war_instance_id`; never derive them from turn number, side names, or `diplo_key`.
- `diplo_key_meta[pair]["pair_status"]` is canonical for `war` / `armistice` / `resolved`; ARMISTICE pairs remain suspended in their existing `war_id` and do not archive the war.
- Cross-war reaction checks are bounded by affected term beneficiaries and at most three affected active `war_instances`, not all nations by all wars.
- Focused tests must include synthetic full-Europe fixtures because the current map data is still smaller than the target: at least 13 nations, one 6+ participant side, and off-map Britain.

## Slice A - War Identity And Grouping

Files:
- `backend/models/world_state.py`
- `backend/game_logic/diplomacy.py`
- `backend/game_logic/war_status.py`
- `docs/SAVE_FORMAT_REFERENCE.md`
- `tests/test_war_settlement_instances.py`

Build:
- Add `world.next_war_instance_id: int = 1`, `world.war_instances: Dict[str, Dict] = {}`, and `world.archived_war_instances: List[Dict] = []` with save/load defaults.
- Create a skeleton `war_instance` when a pair enters `WAR` before `_process_war_cascade()`; allocate `war_id = f"war_{world.next_war_instance_id}"`, store `created_sequence`, then increment the counter.
- Implement `ensure_war_instance_for_pair(...)` and call it from every declaration/cascade seam: player/AI declarations, coalition declarations, vassal rebellions, commitment-paradox outcomes, scripted war entry, and combat-triggered auto-war.
- Add direct-entry helpers (`attach_pair_to_war_instance(...)` / `attach_participant_to_war_instance(...)`) for WAR transitions that bypass `_process_war_cascade()`: `resolve_join_opportunity()`, `accept_counter_bargain()`, vassal-release rebellion, armistice collapse, scripted/debug war entry, and combat-triggered auto-war fallbacks.
- Store pairwise ownership in `active_diplo_keys`, `resolved_diplo_keys`, and `diplo_key_meta`. `objective_keys` remains historical WPS references only.
- Add `diplo_key_meta[pair]["pair_status"] = "war" | "armistice" | "resolved"`. `ARMISTICE -> WAR` reuses the same `war_id`; `ARMISTICE -> PEACE` moves the pair to `resolved_diplo_keys`; common peace never creates ARMISTICE.
- Populate attackers, defenders, active participants, side metadata, and participant episodes as cascade / vassal / ally entry resolves.
- Enforce one-active-`war_instance` per `diplo_key`; reuse compatible instances and merge same-declaration instances rather than creating overlaps.
- Implement transitive merge in the spec order: validate side assignments without mutation, choose the oldest surviving `war_id`, merge participant/pair/episode data in memory, choose leaders, rewrite absorbed `war_id` references on war bargains, contribution events, pending settlement dialogues, dispatch routes, and ledger payloads, then atomically replace/remove records.
- Treat transitive merge as a rare correctness transaction, not a hot path. Full-Europe fixtures should prove correctness for connected-component merges, but no extra optimization is required unless profiling shows repeated merges.
- Store side leaders, participants, `participant_meta`, active episode ids, and re-entry episode ids.
- Use `war_leader_score()` for non-coalition leader replacement; use coalition leadership scoring only for active coalition-leader wars.
- Add elimination exit: stamp `exited_turn`, freeze contribution, remove from active participants, replace leader if needed, and avoid separate-peace reaction.
- Ended instances get `ended_turn` / `end_reason`, remain queryable for 10 turns, then move to `archived_war_instances`.
- Readers tolerate missing WPS `war_objectives` records for historical `objective_keys`.
- Do not replace pairwise diplomacy. `war_instance` groups existing pairs.

Gate:
- 38-44 focused tests.
- Old saves load with `1` for `next_war_instance_id`, `{}` for `war_instances`, and `[]` for `archived_war_instances`.
- Vassal rebellion and a synthetic three-instance chain merge attach to exactly one surviving `war_instance`.
- Direct ally-entry, accepted counter-bargain, vassal-release rebellion, armistice collapse, and scripted/debug war-entry fixtures attach to an existing or new `war_instance`.
- ARMISTICE pair-status tests prove suspended pairs do not archive the war and reuse the same `war_id` if hostilities resume.
- Synthetic 13+ nation war-instance fixture covers 6+ participants on one side without relying on live map data.
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
- Add episode-scoped `world.war_contribution_scores: Dict[str, Dict[str, Dict]] = {}` with `current_episode_id`, `episodes`, and `historical_total`.
- Add theater battle-record emission in `combat_executor.py` through the central `_post_combat_pipeline()` where possible, plus any direct field/garrison/charge paths that bypass it: `battle_region`, `attacker_participants`, `defender_participants`, `nation_theater_strength`, optional casualty-exposure data, and `war_id`.
- Add battle attribution adapter using `battle_region`, then `location`, then `region` for old records.
- Accrue battle, occupation, support, and staying-power buckets from events. Battle contribution is stored at battle-resolution time in `war_contribution_scores`; never reconstruct historical settlement contribution by scanning pruned raw `battle_records`.
- Emit and ingest `war_occupation_event` records for enemy region capture, enemy capital capture, allied-region restoration, and liberated-region restoration; attribute occupation contribution by `actor_nation`.
- Contribution readers filter records by the active episode's `joined_turn <= event.turn <= exited_turn` range.
- Enforce event ordering for same-turn exits: battle/occupation/support contribution events are emitted before elimination, separate-peace, or settlement exits stamp `exited_turn`.
- Canonicalize contribution episode ids as `{nation_slug}_{war_sequence}_{episode_index}`; `exited_turn` is inclusive.
- On re-entry, create a new episode and leave old episode totals available only for history panels; settlement standing uses the current episode.
- Add `war_support_delivered` event ingestion with dedupe by `episode_id`.
- Existing British coalition subsidy emits one `war_support_delivered` event per turn per recipient with `source="coalition_subsidy"` from `backend/game_logic/coalition.py` advance-turn processing.
- Treaty-clause gold / AP / manpower transfers emit `war_support_delivered` at ratification from `_ratify_treaty()` with `source="treaty_clause"`.
- Access/supply support is capped per supporter per war.
- Apply material-contribution gate: staying power alone cannot create seat-level grievance or threshold dispatch.

Gate:
- 48-55 focused tests.
- Contribution accrual does not scan all regions per turn.
- Old battle records with only attacker/defender/location remain valid.
- Raw battle-record pruning does not reduce stored contribution totals.
- Synthetic contribution fixture covers off-map Britain as a low-battle, low-occupation, seat-level major contributor through support/power-tier standing.

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
- Implement common-peace acceptance with the v1.8 constants table, including normalized treaty harshness (`term_harshness_penalty = -min(45, round(total_harshness * 45))`).
- Add deterministic Slice C tuning gate fixtures before locking constants: Pressburg-style accepting-leader losses, Tilsit-style non-leader burden, coalition split, decisive French win without total victory, minor-power limited common peace, and a heavily tilted 6+ participant coalition war. Pin the Pressburg-style worked example from the spec as one fixture seed.
- Add monotonicity coverage proving acceptance does not worsen as `side_pressure_score` increases with all other components fixed.
- If decisive-victory fixtures fail acceptance, first try raising `base_side_pressure` scaling from `0.5` to `0.6`; record any chosen knob in tests and implementation notes.
- Implement `project_balance_after_settlement(world, war_id, terms)` and use projected post-settlement bloc share for `projected_hegemony_mod`, distinct from bilateral `hegemony_target_mod`.
- Implement `abandoned_by_ally_acceptance_mod` as `+5` per same-side enemy separate peace in the last 3 turns, capped at `+15`.
- Normalize territory terms to canonical `from` / `to`; accept `from_nation` / `to_nation` only at input boundaries.
- Enforce direct-score gates for burdened non-leader enemies.
- Implement pressure-basis warnings for unoccupied or barely fought regions.
- Support single-covered-enemy common peace when ally-beneficiary terms, standing, or war-level settlement logic is required.
- Support partial common peace: accepted packages resolve covered hostile pairs to PEACE/treaty states only, while uncovered hostile or ARMISTICE pairs remain in the same `war_instance` until the section 7.3 end condition is met.
- Parameterize scoring by `proposer_side` so defending-side common peace is symmetric.

Build C2 - endpoints, dialogue, advisory, and Godot routing:
- Add settlement endpoint/dialogue contracts: no-terms `GET /diplomatic_preview`, draft-terms `POST /diplomatic_preview`, `settlement_preview`, mandatory hard-stop `settlement_confirm`, typed `POST /respond_to_diplomatic_dialogue` actions for `confirm`, `back_out`, and `revise_terms`, and the exact no-mutation response shapes from the spec.
- Verify the already-registered `settlement_confirm` entries in `DialogueManager.HARD_STOP_TYPES`, backend dialogue priority, Godot dialogue routing, command-response keyword handling, and `tests/test_dialogue_manager.py`; extend behavior rather than re-adding the type.
- `POST /command` may stage common peace terms but must not ratify directly; `confirm` revalidates live leaders, active pair keys, hard stops, and acceptance before mutation.
- Void the staged settlement if the proposer-side leader changes; re-score if only the accepting-side leader changes.
- Implement two-pass standing: draft advisory from draft terms, final confirmation standing from locked terms.
- AI-to-player common-peace offers create an incoming settlement-review dialogue; accepting that offer then uses the same confirm executor instead of direct mutation.
- AI-vs-AI common peace emits one fog-eligible Diplomatic Affairs dispatch line and one `settlement_summary` campaign-log entry, with no participant spam.

Gate:
- C1: 30-35 focused tests.
- C2: 25-30 focused tests.
- Rejection feedback names the top two objectionable components.
- Existing bilateral peace acceptance remains unchanged.
- `settlement_confirm` blocks ordinary commands and handles proposer-leader-change voiding.
- `POST /diplomatic_preview` with draft terms performs no mutation.
- Partial common peace leaves uncovered hostile or ARMISTICE pairs active in the same `war_instance`.
- Common peace cannot create an ARMISTICE pair status.
- AI-vs-AI common peace produces one campaign-log summary and one fog-eligible dispatch line.
- Godot smoke after C2: launch the client, open the settlement review from a synthetic payload, confirm `settlement_confirm` blocks ordinary commands, and back out/revise without mutation.

## Slice D - Settlement Reaction Pass

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
- Add `settlement_gratitude_mod` for eligible later deep-treaty, war-entry, and war-bargain / ally-entry proposals.
- Wire War Bargain fulfillment/breach through existing WB-B lifecycle helpers.
- Within the common-peace ratification transaction, run lifecycle in this order: validate confirm, ratify terms, mutate ownership/alignment, run WB-B fulfillment/breach, run settlement reactions, invalidate hegemony/bloc caches, then build dispatch/log/ledger payloads.
- Add canonical acceptance-doc amendments for `settlement_gratitude_mod`: positive `+5`, not part of the clamped political subtotal, cannot bypass hard stops or political floors, refreshes rather than stacks.
- Document combined separate-peace relation impact: BPH-C base penalty plus settlement shut-out penalty, with no duplicate BPH-C application.
- Implement `compute_local_balance_warning()` from live relation/bloc/adjacency/desire-profile data only.
- `rival_strengthened` alone promotes only major/secondary nations to consult; minors need material contribution or direct interests.
- Trigger cross-war reaction checks only for affected participants and at most three affected active wars.
- Add settlement-memory cleanup for expired transient records after active modifiers are read; writes are idempotent by `(memory_type, actor, subject, counterparty, war_id, episode_id)`.
- Enforce turn lifecycle placement from spec section 17.5: event-time contribution, war-state mutation, WB-B lifecycle, staying power, leader/end checks, memory reads, memory cleanup, then presentation payloads.

Gate:
- 46-54 focused tests.
- No duplicate BPH-C separate-peace relation penalty.
- Balance of Europe beats fire only through existing threshold/hegemon-swap seams.
- `settlement_gratitude_mod` appears in canonical acceptance docs and proposal debug components.

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
- Add settlement route metadata separate from commitment routes.
- Dispatch top four settlement beats plus one digest overflow line.
- Notification rail spotlights only major settlement outcomes.
- Campaign log emits one `settlement_summary` entry per common peace with structured `participant_reactions`.
- War status panel shows contribution share and standing with top-five default rows plus overflow.
- WARNING and HARD_STOP concerns always surface above the capped standing list.
- Use the deterministic `rank_diplomatic_salience()` tuple from the spec for all default-row ordering.
- Settlement review is a CanvasLayer 50 information-screen surface and must close/hide existing layer-50 screens through the top-bar one-screen-at-a-time rule before opening.
- Advisory rows show projected ally fallout costs and per-term marginal acceptance costs where available.
- Split into E1 backend presentation payloads and E2 Godot rendering if the Godot surface exceeds the slice gate.

Gate:
- 34-42 focused tests.
- Large 6+ participant settlement emits one campaign-log one-liner, not per-participant spam.
- Settlement review CanvasLayer 50 renders top-five rows plus "View all participants" on a synthetic 6+ participant full-Europe payload with no overlapping text.
- Notification buttons route to the settlement review or ledger target specified by backend route metadata.
- Godot surfaces remain usable on both the current 19-region map and a synthetic full-Europe participant payload.
- Manual Godot smoke after E2 verifies settlement review, war status rows, notification route, and ledger route on both current map data and the synthetic full-Europe payload.

## Final Gate

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_war_settlement_instances.py tests/test_war_contribution_scores.py tests/test_common_peace_acceptance.py tests/test_settlement_reactions.py tests/test_settlement_presentation.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_war_objectives.py tests/test_wb_a_bargain_model.py tests/test_wb_b_lifecycle.py tests/test_wb_c_war_entry.py tests/test_wb_d_presentation.py tests/test_wpsb_power_cap.py tests/test_bph_c_fallout_conflicts.py tests/test_bph_d_ratification_summary.py -q
.\.venv\Scripts\python.exe -m ruff check backend tests
```

Full-suite run is required before merging Slice E because it touches shared diplomacy, campaign log, dispatch, ledger, serialization, and Godot contracts.
