"""Common-peace settlement preview, dialogue staging, and ratification helpers.

Slice C2 foundation introduced the Open Settlement eligibility / preview /
dialogue staging contracts around the pure C1b acceptance formula.

Slice C2 ratification (this slice) closes ``settlement_confirm.confirm`` so
the staged package mutates state per spec §10.5 / §11 / §11.1: covered
active hostile pairs resolve to ``PEACE`` (or ``ALLIANCE`` for
forced-alliance pairs), territory / gold / liberation outcomes apply,
forced-alliance pairs end in ``ALLIANCE`` with origin metadata + threat,
covered pairs move to ``resolved_diplo_keys`` (closing contribution
episodes via ``resolve_pair_to_resolved``), uncovered hostile / armistice
pairs stay active, and ``war_instances_by_*`` / bloc / active-nation
caches invalidate before any reaction reader runs. Settlement / cross-war
reaction routing remains a later slice.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Tuple

from backend.display_names import (
    SETTLEMENT_DISABLED_REASON_DISPLAY,
    acceptance_band_display,
    acceptance_band_phrase,
    acceptance_component_display,
    settlement_disabled_reason_display,
)
from backend.game_logic.diplomatic_templates import (
    calculate_raw_treaty_harshness,
    calculate_treaty_harshness,
    resolve_multi_court_settlement_voice,
    resolve_named_diplomat,
    resolve_settlement_voice_line,
)
from backend.game_logic import settlement_scoring
from backend.game_logic.settlement_scoring import (
    ACCEPTANCE_THRESHOLD,
    calculate_common_peace_acceptance,
    CANONICAL_CLAUSE_TYPES,
    CLAUSE_CONFLICT_MATRIX,
    compute_direct_scores_by_enemy,
    compute_side_pressure_score,
    CONCESSION_GOLD_CAP,
    CONCESSION_GOLD_DIVISOR,
    GOLD_PER_TURN_MAX_TURNS,
    GOLD_PER_TURN_MIN_AMOUNT,
    GOLD_PER_TURN_MIN_TURNS,
    HARD_STOP_NO_DIRECT_WAR_SCORE,
    MAX_SETTLEMENT_CLAUSE_COUNT,
    NEAR_ACCEPTANCE_FLOOR,
    project_balance_after_settlement,
    select_direct_score,
    SETTLEMENT_HARD_STOP_CODES,
    SETTLEMENT_LIVE_CLAUSE_TYPES,
    SETTLEMENT_MVP_CLAUSE_TYPES,
)
from backend.game_logic.settlement_presentation import (
    _term_display,
    build_contribution_share_rows,
    build_settlement_review,
    detect_awe_set_pieces,
)
from backend.game_logic.settlement_routes import (
    SETTLEMENT_ERROR_DISPLAY,
    SETTLEMENT_FAMILY_DIALOGUE_TYPES,
    SETTLEMENT_REOPEN_MAX_ATTEMPTS,
    SETTLEMENT_ROUTE_NAMESPACE,
    _error_display,
    _mounted_settlement_dialogue,
    _no_reopen_target_payload,
    _normalize_nation_list,
    _reopen_attempt_store,
    _reopen_target,
    _safe_reopen_response,
    _settlement_dialogue_active,
    _settlement_history_route,
    _terminal_recovery_copy,
    _war_detail_recovery_route,
    _war_label,
    derive_settlement_review_target,
    evaluate_war_detail_actionability,
    get_reopen_attempts,
    is_war_archived,
    is_war_known,
    mint_settlement_route_id,
    record_reopen_attempt,
    reopen_attempt_cap_exceeded,
    resolve_settlement_route_click,
)
from backend.game_logic.settlement_validation import (
    LOSING_SIDE_PRESSURE_THRESHOLD,
    PAIR_SUBSTITUTE_ACTIONS,
    PAIR_SUBSTITUTE_REFUSAL_CODES,
    PAIR_SUBSTITUTE_TEMPORAL_REFUSAL_CODES,
    RATIFY_LEGACY_APPLY_CLAUSE_TYPES,
    VALID_SIDES,
    _CROSS_SIDE_TRANSFER_CLAUSE_TYPES,
    _active_cross_side_pairs,
    _blocked_payload,
    _check_gold_payment_budget_conflict,
    _check_vassalage_state,
    _clause_role_nations,
    _clause_touches_court,
    _dependency_eligibility_payload,
    _estimate_payer_net_income_per_turn,
    _has_material_concession_terms,
    _infer_actor_side,
    _normalize_staged_terms_for_validation,
    _other_side,
    _pair_nations,
    _resolve_war_sides,
    _side_for_nation,
    _side_leader,
    _term_lists_equal,
    _terms_equal,
    _territory_term_regions,
    evaluate_liberation_eligibility,
    evaluate_open_settlement_eligibility,
    evaluate_pair_peace_substitute_eligibility,
    evaluate_subjugation_eligibility,
    evaluate_vassalage_eligibility,
    get_coverable_enemy_participants,
    is_common_settlement_worth_showing,
    validate_settlement_terms,
)
from backend.game_logic.settlement_baseline import (
    CONCESSION_BASELINE_BFS_MAX_DEPTH,
    CONCESSION_BASELINE_GOLD_FLOOR,
    CONCESSION_BASELINE_GOLD_HARD_CAP,
    CONCESSION_BASELINE_TREASURY_RESERVE,
    DEMAND_TERRITORY_DIRECT_SCORE,
    DIRECT_SCORE_DIRECTION_MARGIN,
    SETTLEMENT_DIAL_GOLD_STEP,
    _GOLD_PER_TURN_PREFILL_TURNS,
    _acceptance_component_breakdown,
    _compute_concession_baseline,
    _compute_recurring_gold_preset,
    _compute_surrender_preset,
    _concession_baseline_bfs_distance,
    _concession_baseline_payer_balance,
    _concession_baseline_select_transferable_region,
    _concession_baseline_transferable_candidates,
    _concession_terms_for_court,
    _court_direction_from_selection,
    _court_direction_summary,
    _degrade_generated_baseline_to_valid,
    _demand_baseline_region_candidates,
    _demand_baseline_select_region,
    _demand_terms_for_court,
    _enrich_acceptance_display,
    _format_concession_reasoning,
    _gold_per_turn_prefill,
    _guided_gold_offer_default,
    _guided_region_offer_candidate,
    _payer_net_income_estimate,
    _promised_regions_in_terms,
    _proposer_paid_gold_committed,
    _relax_baseline_demands_for_package_harshness,
    _score_court_for_baseline,
    compute_per_court_acceptance,
    compute_settlement_baseline,
    compute_settlement_treasury_line,
)
from backend.game_logic.settlement_staging import (
    SETTLEMENT_COOLDOWN_TURNS,
    SETTLEMENT_EDITOR_CALLER_KIND,
    _DEMAND_CLAUSE_CAP_REASON,
    _build_settlement_scope_replace_confirm_dialogue,
    _court_current_demand_lines,
    _court_demand_suggestions,
    _demand_hard_stop_reason,
    _dialogue_scope_values,
    _discard_scoped_settlement_draft_for_dialogue,
    _guided_line_display,
    _guided_magnitude_meta,
    _guided_suggestion,
    _join_court_names,
    _redial_settlement_terms,
    _restage_settlement_after_redraw,
    _scope_changed,
    _scope_display,
    _scoped_settlement_drafts,
    _settlement_budget_bound_constraint,
    _settlement_budget_bound_recommendation,
    _settlement_collision_payload,
    _settlement_propose_carry_hint,
    _settlement_remaining_war_courts,
    _settlement_targeted_posture_advisory,
    build_settlement_confirm_dialogue,
    build_settlement_preview,
    compute_settlement_draft_key,
    discard_scoped_settlement_draft,
    load_scoped_settlement_draft,
    revalidate_staged_settlement,
    save_scoped_settlement_draft,
    stage_settlement_confirm,
)
from backend.game_logic.settlement_ratify import (
    _apply_settlement_terms,
    _blocked_ratify_reattach,
    _build_pair_ratification_plan,
    _capture_pair_pre_cleanup_war_data,
    _capture_pre_cleanup_snapshots,
    _failed_ratification_reaction_summary,
    _record_common_peace_treaties,
    _resolve_pair_state_transitions,
    _stage_replacement_settlement_terms,
    ratify_settlement_confirm,
)


ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE = "ally_settlement_petition"
ALLY_SETTLEMENT_PETITION_REQUEST_OPEN = "request_open_settlement"
ALLY_SETTLEMENT_PETITION_WARN_SELLOUT = "warn_against_sellout"
ALLY_SETTLEMENT_PETITION_SHIPPED_TYPES = frozenset({
    ALLY_SETTLEMENT_PETITION_REQUEST_OPEN,
    ALLY_SETTLEMENT_PETITION_WARN_SELLOUT,
})
ALLY_SETTLEMENT_PETITION_SOLICITED_TRIGGERS = frozenset({
    "open_settlement",
    "stage_settlement",
    "reject_settlement_offer",
})
ALLY_SETTLEMENT_PETITION_ACK_ACTION = "acknowledge_ally_settlement_petition"

# SC-5 reversal (May 15, 2026 / Slice G1 commit 1): incoming settlement
# offers are produced by the AI settlement-offer phase (`ai_diplomacy.
# process_settlement_offer_phase`) and consumed by `handle_incoming_
# settlement_offer_action`. The handler is no longer short-circuited.
# Produced offers live in `world.pending_settlement_dialogues` only;
# the dialogue-manager taxonomy / mailbox / Godot UI wiring lands in
# the immediately following commit, so the flag below stays as a
# named constant for stale-save defensive paths and audit-trail
# clarity but defaults to False.
INCOMING_OFFERS_DEFERRED: bool = False

def _build_settlement_replace_confirm_dialogue(
    dialogue: Mapping[str, Any],
    *,
    replacement_terms: Iterable[Mapping[str, Any]],
    apply_action: str,
    apply_label: str,
    replacement_kind: str,
    message: str,
    concession_baseline: Optional[Mapping[str, Any]] = None,
    surrender_preset_payload: Optional[Mapping[str, Any]] = None,
    recurring_gold_preset_payload: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    current_terms = [
        dict(t)
        for t in (dialogue.get("settlement_terms") or [])
        if isinstance(t, Mapping)
    ]
    confirm = copy.deepcopy(dict(dialogue))
    confirm.update({
        "type": "settlement_confirm",
        "dialogue_type": "settlement_confirm",
        "replace_confirm": True,
        "replacement_kind": replacement_kind,
        "replacement_terms": [
            dict(t) for t in (replacement_terms or []) if isinstance(t, Mapping)
        ],
        "preserved_terms": current_terms,
        "available_action_ids": [apply_action, "keep_current_settlement_draft"],
        "can_ratify": False,
        "options": [
            {
                "label": apply_label,
                "action": apply_action,
                "description": "Replace the current draft without mutating the world.",
            },
            {
                "label": "Keep my draft",
                "action": "keep_current_settlement_draft",
                "description": "Return to the current draft unchanged.",
            },
        ],
        "message": message,
        "talleyrand_text": message,
        "terminal_recovery_copy": "",
        "mutated": False,
        "blocking": True,
    })
    if concession_baseline is not None:
        confirm["concession_baseline"] = copy.deepcopy(concession_baseline)
    if surrender_preset_payload is not None:
        confirm["surrender_preset_payload"] = copy.deepcopy(surrender_preset_payload)
    if recurring_gold_preset_payload is not None:
        confirm["recurring_gold_preset_payload"] = copy.deepcopy(
            recurring_gold_preset_payload
        )
    return confirm


def _restore_scope_replace_current_dialogue(
    world: Any,
    dialogue: Mapping[str, Any],
    *,
    action: str,
) -> Dict[str, Any]:
    current_dialogue = copy.deepcopy(dict(dialogue.get("current_dialogue") or {}))
    war_id = str(dialogue.get("war_id") or current_dialogue.get("war_id") or "")
    if current_dialogue:
        world.dialogue_manager.replace(current_dialogue)
    else:
        world.dialogue_manager.pop()
    return {
        "success": True,
        "dialogue_type": str(
            current_dialogue.get("dialogue_type")
            or current_dialogue.get("type")
            or "settlement_confirm"
        ),
        "action": action,
        "war_id": war_id,
        "diplomatic_dialogue": current_dialogue,
        "awaiting_diplomatic_response": bool(current_dialogue),
        "scope_replaced": False,
        "mutated": False,
        "message": "Keeping the current settlement draft unchanged.",
        "suppress_proposal_result_popup": True,
    }


def _apply_scope_replace_confirm(
    world: Any,
    dialogue: Mapping[str, Any],
) -> Dict[str, Any]:
    current_dialogue = copy.deepcopy(dict(dialogue.get("current_dialogue") or {}))
    incoming_request = dict(dialogue.get("incoming_request") or {})
    war_id = str(dialogue.get("war_id") or incoming_request.get("war_id") or "")
    current_selected, current_covered = _dialogue_scope_values(current_dialogue)
    incoming_covered = _normalize_nation_list(
        incoming_request.get("covered_enemy_participants") or []
    )
    incoming_selected = str(
        incoming_request.get("selected_target_nation") or ""
    ).strip() or (incoming_covered[0] if incoming_covered else "")
    current_key = compute_settlement_draft_key(war_id, current_selected, current_covered)
    incoming_key = compute_settlement_draft_key(
        war_id, incoming_selected, incoming_covered,
    )
    if current_key == incoming_key:
        restored = _restore_scope_replace_current_dialogue(
            world, dialogue, action="replace_current_scope_draft",
        )
        restored["scope_revalidation"] = "same_scope_no_replace"
        restored["message"] = "The settlement scope is already current."
        return restored
    if incoming_selected and incoming_selected not in incoming_covered:
        restored = _restore_scope_replace_current_dialogue(
            world, dialogue, action="replace_current_scope_draft",
        )
        restored.update({
            "success": False,
            "error": "selected_target_not_covered",
            "error_display": _error_display("selected_target_not_covered"),
            "scope_revalidation": "invalid_incoming_scope",
        })
        return restored

    incoming_terms = [
        dict(t)
        for t in (incoming_request.get("settlement_terms") or [])
        if isinstance(t, Mapping)
    ]
    preview = build_settlement_preview(
        world,
        war_id=war_id,
        proposer_side=str(incoming_request.get("proposer_side") or ""),
        settlement_terms=incoming_terms,
        covered_enemy_participants=incoming_covered,
        actor_nation=incoming_request.get("actor_nation"),
        density=str(incoming_request.get("density") or "medium"),
        ignore_active_dialogue=True,
    )
    if not preview.get("success"):
        restored = _restore_scope_replace_current_dialogue(
            world, dialogue, action="replace_current_scope_draft",
        )
        restored.update({
            "success": False,
            "error": preview.get("error") or "scope_replace_failed_preview",
            "error_display": preview.get("error_display") or (
                "The replacement scope could not be previewed."
            ),
            "scope_revalidation": "preview_failed",
        })
        return restored
    covered = list(preview["settlement_preview"].get("covered_enemy_participants") or [])
    resolved_target = incoming_selected or (covered[0] if covered else "")
    if not resolved_target or resolved_target not in covered:
        restored = _restore_scope_replace_current_dialogue(
            world, dialogue, action="replace_current_scope_draft",
        )
        restored.update({
            "success": False,
            "error": "selected_target_not_covered",
            "error_display": _error_display("selected_target_not_covered"),
            "scope_revalidation": "invalid_preview_scope",
        })
        return restored
    new_dialogue = build_settlement_confirm_dialogue(
        world,
        preview,
        selected_target_nation=resolved_target,
        caller_kind=str(incoming_request.get("caller_kind") or "player_editor"),
        white_peace=bool(incoming_request.get("white_peace", False)),
        surrender_preset=bool(incoming_request.get("surrender_preset", False)),
    )
    drafts = getattr(world, "pending_settlement_drafts", None)
    if drafts is None:
        world.pending_settlement_drafts = {}
        drafts = world.pending_settlement_drafts
    for key in (current_key, str(dialogue.get("current_draft_key") or ""), war_id):
        if key in drafts:
            del drafts[key]
    if incoming_terms:
        drafts[war_id] = [dict(t) for t in incoming_terms]
    # SC-5R-1 scoped store: clear the prior scope's scoped draft (the
    # chooser is the explicit "replace this scope's draft" path) and
    # write the incoming scope's draft under its own scoped key so a
    # reopen of either scope can read its own draft without collision.
    scoped_drafts = getattr(world, "pending_settlement_drafts_by_key", None)
    if isinstance(scoped_drafts, dict):
        scoped_drafts.pop(current_key, None)
    if incoming_terms:
        save_scoped_settlement_draft(
            world,
            war_id=war_id,
            selected_target_nation=resolved_target,
            covered_enemy_participants=covered,
            settlement_terms=incoming_terms,
        )
    world.dialogue_manager.replace(new_dialogue)
    return {
        "success": True,
        "dialogue_type": "settlement_confirm",
        "action": "replace_current_scope_draft",
        "war_id": war_id,
        "diplomatic_dialogue": new_dialogue,
        "settlement_preview": preview["settlement_preview"],
        "awaiting_diplomatic_response": True,
        "scope_replaced": True,
        "cleared_draft_key": current_key,
        "draft_key": new_dialogue.get("draft_key"),
        "mutated": False,
        "message": "The replacement settlement scope has been staged for review.",
        "suppress_proposal_result_popup": True,
    }


def _handle_settlement_tier2_action(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Mapping[str, Any],
) -> Dict[str, Any]:
    """Re-front Slice 2 — Tier-2 intent dials, coverage edits, and court focus
    on the conversational PROPOSE surface (spec §11.3).

    All five verbs are PLAYER-ONLY (the Slice-G boundary): a non-player
    staging never reaches an authoring redraw. Dials and coverage edits re-draft + re-score live over one shared
    score pass and preserve PROPOSE mode; ``settlement_focus_court`` is
    presentation-only (no term mutation, no re-score).
    """
    war_id = str(dialogue.get("war_id") or "")
    caller_kind = str(dialogue.get("caller_kind") or "")
    if caller_kind != SETTLEMENT_EDITOR_CALLER_KIND:
        # Slice-G boundary: only the player authors / steers a settlement.
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": action,
            "war_id": war_id,
            "error": "settlement_action_not_player_authored",
            "error_display": "This settlement is not yours to steer, Sire.",
            "mutated": False,
            "suppress_proposal_result_popup": True,
        }
    proposer_side = str(dialogue.get("proposer_side") or "")
    accepting_side = str(dialogue.get("accepting_side") or "") or _other_side(proposer_side)
    covered = sorted({str(n) for n in (dialogue.get("covered_enemy_participants") or []) if n})
    terms = [
        dict(t) for t in (dialogue.get("settlement_terms") or [])
        if isinstance(t, Mapping)
    ]
    war_instance = (getattr(world, "war_instances", {}) or {}).get(war_id) or {}
    staged_leaders = dialogue.get("staged_leaders") or {}
    proposer_leader = (
        staged_leaders.get(proposer_side) or _side_leader(war_instance, proposer_side)
    )

    if action == "settlement_focus_court":
        # OQ#1 / §11.3: presentation-only focus. No terms change, no re-score —
        # focusing a row just scopes the next dial click to that court.
        raw_nation = action_params.get("nation")
        focused = str(raw_nation).strip() if raw_nation else None
        if focused and focused not in covered:
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": action,
                "war_id": war_id,
                "error": "focused_court_not_covered",
                "error_display": f"{focused} is not part of this settlement, Sire.",
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        updated = dict(dialogue)
        updated["focused_court"] = focused
        world.dialogue_manager.replace(updated)
        return {
            "success": True,
            "dialogue_type": "settlement_confirm",
            "action": action,
            "war_id": war_id,
            "diplomatic_dialogue": updated,
            "focused_court": focused,
            "mutated": False,
            "message": (f"Focused on {focused}." if focused else "Focus cleared."),
            "suppress_proposal_result_popup": True,
        }

    if action in ("settlement_dial_harsher", "settlement_dial_generous"):
        direction = "harsher" if action.endswith("harsher") else "generous"
        scope = str(action_params.get("scope") or "table").strip() or "table"
        if scope == "table":
            scope_courts = list(covered)
        elif scope in covered:
            scope_courts = [scope]
        else:
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": action,
                "war_id": war_id,
                "error": "dial_scope_not_covered",
                "error_display": f"{scope} is not part of this settlement, Sire.",
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        protected_notes: List[str] = []
        seeded_events: List[Dict[str, str]] = []
        new_terms = _redial_settlement_terms(
            terms=terms,
            scope_courts=scope_courts,
            direction=direction,
            proposer_side_leader=proposer_leader,
            protected_notes=protected_notes,
            seeded_events=seeded_events,
        )
        verb = "Pressed" if direction == "harsher" else "Eased"
        target_label = "the whole table" if scope == "table" else scope
        message = f"{verb} {target_label}."
        if protected_notes:
            # §3.5: a protected player-authored line is never invisible — the
            # skip/floor is named in the dial's own response message.
            message = " ".join([message, *protected_notes])
        # GT-Slice-V / DC-4 (D5): the focused-Harsher seed can author a
        # demand on a court that is beating France (press-past-zero — legal
        # agency; the scorer prices it). Talleyrand no longer authors it
        # wordlessly: the guard line rides the restaged dialogue exactly as
        # it does on the explicit demand-group add.
        direction_by_court = {
            str(r.get("nation") or ""): str(r.get("direction") or "")
            for r in (dialogue.get("per_court_acceptance") or [])
            if isinstance(r, Mapping)
        }
        voice_beats: List[Dict[str, str]] = [
            {
                "kind": "talleyrand_caution",
                "speaker": "Talleyrand",
                "nation": str(event.get("court") or ""),
                "line": resolve_settlement_voice_line(
                    "settlement_demand_on_concede_court_caution_talleyrand",
                ),
            }
            for event in seeded_events
            if event.get("group") == "demand"
            and direction_by_court.get(str(event.get("court") or "")) == "concede"
        ]
        return _restage_settlement_after_redraw(
            world,
            dialogue,
            action=action,
            new_terms=new_terms,
            new_covered=covered,
            message=message,
            extra={"authoring_voice_beats": voice_beats} if voice_beats else None,
        )

    # settlement_cover_add / settlement_cover_drop
    nation = str(action_params.get("nation") or "").strip()
    if not nation:
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": action,
            "war_id": war_id,
            "error": "no_coverage_nation",
            "error_display": "No court was named to add or drop, Sire.",
            "mutated": False,
            "suppress_proposal_result_popup": True,
        }
    if action == "settlement_cover_add":
        coverable = set(get_coverable_enemy_participants(war_instance, proposer_side))
        if nation not in coverable:
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": action,
                "war_id": war_id,
                "error": "nation_not_coverable",
                "error_display": f"{nation} cannot be brought to this settlement, Sire.",
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        new_covered = sorted(set(covered) | {nation})
    else:  # settlement_cover_drop
        new_covered = sorted(set(covered) - {nation})
        if not new_covered:
            # V5 coverage floor — at least one covered enemy must remain.
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": action,
                "war_id": war_id,
                "error": "no_covered_enemy_participants",
                "error_display": _error_display("no_covered_enemy_participants"),
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
    # §11.3: a coverage edit re-draws the baseline for the new set (this drops
    # any clause that referenced a removed court — V2 — and authors a fresh
    # slice for an added court), then re-scores.
    baseline = compute_settlement_baseline(
        world,
        war_id=war_id,
        war_instance=war_instance,
        proposer_side=proposer_side,
        accepting_side=accepting_side,
        proposer_side_leader=proposer_leader,
        covered_enemy_participants=new_covered,
    )
    new_terms = baseline["settlement_terms"]
    ignored, remaining = _settlement_remaining_war_courts(
        world,
        war_id=war_id,
        proposer_side=proposer_side,
        covered_enemy_participants=new_covered,
    )
    verb = "Added" if action == "settlement_cover_add" else "Dropped"
    return _restage_settlement_after_redraw(
        world,
        dialogue,
        action=action,
        new_terms=new_terms,
        new_covered=new_covered,
        message=f"{verb} {nation}; the settlement was re-drafted.",
        extra={"ignored_participants": ignored, "remaining_wars": remaining},
    )


# GT-Slice-1 (Guided Terms §3.1/§4): the per-court demand-mutation verbs.
# Direction is fixed PER OPTION (D3/D4) — the verb derives every from/to
# from (court, group); no identity ever arrives in `action_params`.
SETTLEMENT_DEMAND_VERB_ACTION_IDS = (
    "settlement_demand_add",
    "settlement_demand_remove",
    "settlement_demand_set_magnitude",
)
# Clause types the guided `Add demand` may author (§4 — `peace` is the
# shared package clause, never a per-court line).
_DEMAND_ADDABLE_CLAUSE_TYPES = frozenset({
    "territory_cede", "gold_indemnity", "gold_per_turn",
    "vassalage", "subjugation", "forced_alliance", "liberation",
})
# Types with an OFFER arm (France → court). Dependency / forced-alliance /
# liberation clauses are demand-only per the §4 mapping (a losing player
# cannot force the victor; France self-vassalage is not a player verb).
_DEMAND_OFFERABLE_CLAUSE_TYPES = frozenset({
    "territory_cede", "gold_indemnity", "gold_per_turn",
})
_DEMAND_GOLD_MAGNITUDE_CLAUSE_TYPES = frozenset({
    "gold_indemnity", "gold_per_turn",
})


def _demand_clause_label(clause: Mapping[str, Any]) -> str:
    """A short player-facing line for one clause, used in restage messages
    ("Struck the cession of Silesia."). Full voice beats land in GT-Slice-V."""
    ttype = str(clause.get("type") or "")
    if ttype == "territory_cede":
        return f"the cession of {clause.get('region')}"
    if ttype in ("gold_indemnity", "gold_lump"):
        return f"{int(clause.get('amount', 0) or 0)} gold from {clause.get('from')}"
    if ttype == "gold_per_turn":
        return (
            f"{int(clause.get('amount', 0) or 0)} gold a turn for "
            f"{int(clause.get('turns', 0) or 0)} turns from {clause.get('from')}"
        )
    if ttype == "vassalage":
        return f"the vassalage of {clause.get('from')}"
    if ttype == "subjugation":
        return f"the subjugation of {clause.get('from')}"
    if ttype == "forced_alliance":
        return f"the alliance forced upon {clause.get('from')}"
    if ttype == "liberation":
        return f"the liberation of {clause.get('vassal_nation')}"
    return ttype.replace("_", " ") or "the clause"


def _handle_settlement_demand_action(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Mapping[str, Any],
) -> Dict[str, Any]:
    """GT-Slice-1 — guided per-court demand authoring on the PROPOSE surface
    (Guided Terms spec §3.1/§3.2/§4/§7).

    Three mutation verbs against the staged ``settlement_confirm``:

    - ``settlement_demand_add`` — author one fully-formed clause on a covered
      court. ``group`` picks the arm: ``demand`` (court → France) or ``offer``
      (France → court, the D4 sweetener lever); omitted, it defaults to the
      court's direction-led group (§3.3 — a losing court leads with offers).
      Options are valid-by-construction at TABLE scope (§3.4): eligibility
      gates run before authoring, gold defaults cap at the shared-treasury
      ``remaining``, region defaults exclude already-promised regions.
    - ``settlement_demand_remove`` — strike one line by ``clause_index``
      (the shared ``peace`` clause is not a line and cannot be struck).
    - ``settlement_demand_set_magnitude`` — adjust gold ``amount`` /
      ``turns`` on one line; identity (payer / payee / region) is immutable
      (remove + add is the identity verb).

    Every mutation routes through ``_restage_settlement_after_redraw``
    (validate → re-preview → re-stage → persist the scoped draft), so the
    validator stays the authority and the §11.2 live re-score is automatic.
    Guards (§7 / GT-R1-5): player-only (the Slice-G boundary) AND
    ``dialogue_mode == "PROPOSE"`` — REVIEW is a frozen staged-decision
    surface, guarded server-side here rather than by absent buttons.
    Failures rely on the CH-5 wrapper for the dialogue re-attach +
    ``error_display`` invariant, with arm-rendered reasons provided here.
    """
    war_id = str(dialogue.get("war_id") or "")

    def _fail(error: str, error_display: str = "", **extra: Any) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": action,
            "war_id": war_id,
            "error": error,
            "error_display": error_display or _error_display(error),
            "mutated": False,
            "suppress_proposal_result_popup": True,
        }
        payload.update(extra)
        return payload

    caller_kind = str(dialogue.get("caller_kind") or "")
    if caller_kind != SETTLEMENT_EDITOR_CALLER_KIND:
        # Slice-G boundary: only the player authors / steers a settlement.
        return _fail(
            "settlement_action_not_player_authored",
            "This settlement is not yours to steer, Sire.",
        )
    if str(dialogue.get("dialogue_mode") or "") != "PROPOSE":
        # §7 guard: REVIEW is the frozen staged-decision surface. Today's
        # dials rely on absent buttons; the mutation verbs guard explicitly.
        return _fail(
            "settlement_demand_requires_propose",
            "The terms are staged for review, Sire — return to shaping "
            "before changing them.",
        )

    proposer_side = str(dialogue.get("proposer_side") or "")
    covered = sorted({
        str(n) for n in (dialogue.get("covered_enemy_participants") or []) if n
    })
    terms = [
        dict(t) for t in (dialogue.get("settlement_terms") or [])
        if isinstance(t, Mapping)
    ]
    war_instance = (getattr(world, "war_instances", {}) or {}).get(war_id) or {}
    staged_leaders = dialogue.get("staged_leaders") or {}
    proposer_leader = str(
        staged_leaders.get(proposer_side)
        or _side_leader(war_instance, proposer_side)
        or ""
    )

    if action == "settlement_demand_remove":
        try:
            clause_index = int(action_params.get("clause_index"))
        except (TypeError, ValueError):
            return _fail(
                "invalid_clause_index", "No clause was named to strike, Sire.",
            )
        if clause_index < 0 or clause_index >= len(terms):
            return _fail(
                "invalid_clause_index",
                "That clause is no longer in the draft, Sire.",
            )
        clause = terms[clause_index]
        expected_type = str(action_params.get("expected_type") or "")
        if expected_type and str(clause.get("type") or "") != expected_type:
            return _fail(
                "clause_index_stale",
                "The draft changed under that click, Sire — review the "
                "terms again.",
            )
        if str(clause.get("type") or "") == "peace":
            return _fail(
                "peace_clause_not_removable",
                "The peace itself is not a line to strike, Sire — back out "
                "of the settlement instead.",
            )
        new_terms = [t for i, t in enumerate(terms) if i != clause_index]
        return _restage_settlement_after_redraw(
            world,
            dialogue,
            action=action,
            new_terms=new_terms,
            new_covered=covered,
            message=f"Struck {_demand_clause_label(clause)}.",
        )

    if action == "settlement_demand_set_magnitude":
        try:
            clause_index = int(action_params.get("clause_index"))
        except (TypeError, ValueError):
            return _fail(
                "invalid_clause_index", "No clause was named to adjust, Sire.",
            )
        if clause_index < 0 or clause_index >= len(terms):
            return _fail(
                "invalid_clause_index",
                "That clause is no longer in the draft, Sire.",
            )
        clause = dict(terms[clause_index])
        ttype = str(clause.get("type") or "")
        expected_type = str(action_params.get("expected_type") or "")
        if expected_type and ttype != expected_type:
            return _fail(
                "clause_index_stale",
                "The draft changed under that click, Sire — review the "
                "terms again.",
            )
        if ttype not in _DEMAND_GOLD_MAGNITUDE_CLAUSE_TYPES:
            # Identity is immutable (D3): region / payer changes are
            # remove + add, never an in-place swap.
            return _fail(
                "magnitude_not_adjustable",
                "Only gold lines carry an adjustable magnitude, Sire — "
                "strike the clause and author another instead.",
            )
        raw_amount = action_params.get("amount")
        raw_turns = action_params.get("turns")
        if raw_amount is None and raw_turns is None:
            return _fail(
                "no_magnitude_given", "No new magnitude was named, Sire.",
            )
        if raw_amount is not None:
            try:
                amount = int(raw_amount)
            except (TypeError, ValueError):
                return _fail(
                    "invalid_magnitude", "That is not a sum of gold, Sire.",
                )
            floor = GOLD_PER_TURN_MIN_AMOUNT if ttype == "gold_per_turn" else 1
            if amount < floor:
                return _fail(
                    "invalid_magnitude",
                    f"The sum must be at least {floor} gold, Sire.",
                )
            clause["amount"] = int(amount)
        if raw_turns is not None and ttype == "gold_per_turn":
            try:
                turns = int(raw_turns)
            except (TypeError, ValueError):
                return _fail(
                    "invalid_magnitude", "That is not a term of turns, Sire.",
                )
            if not (GOLD_PER_TURN_MIN_TURNS <= turns <= GOLD_PER_TURN_MAX_TURNS):
                return _fail(
                    "invalid_magnitude",
                    f"The term must run between {GOLD_PER_TURN_MIN_TURNS} "
                    f"and {GOLD_PER_TURN_MAX_TURNS} turns, Sire.",
                )
            clause["turns"] = int(turns)
        # A hand-set magnitude is player intent — §3.5: the dial sweep now
        # protects this line like any hand-authored one.
        clause["authored_by"] = "player"
        new_terms = [dict(t) for t in terms]
        new_terms[clause_index] = clause
        return _restage_settlement_after_redraw(
            world,
            dialogue,
            action=action,
            new_terms=new_terms,
            new_covered=covered,
            message=f"Set {_demand_clause_label(clause)}.",
        )

    # settlement_demand_add
    court = str(action_params.get("nation") or "").strip()
    if not court:
        return _fail(
            "no_demand_court", "No court was named for the demand, Sire.",
        )
    if court not in covered:
        return _fail(
            "demand_court_not_covered",
            f"{court} is not part of this settlement, Sire.",
        )
    if len(terms) >= MAX_SETTLEMENT_CLAUSE_COUNT:
        # §3.1 — mirror of the Slice-2 focused-seed fold: never author an
        # over-cap draft for the restage validator to bounce. Copy shared
        # with the GT-Slice-2 row payload's pre-click disabled state.
        return _fail("max_clause_count_exceeded", _DEMAND_CLAUSE_CAP_REASON)
    direction = ""
    for row in dialogue.get("per_court_acceptance") or []:
        if isinstance(row, Mapping) and str(row.get("nation") or "") == court:
            direction = str(row.get("direction") or "")
            break
    if direction == "hard_stop":
        # §3.3 — no clause can move a `total=null` court; the scorer
        # hard-stops it. The row exposes Drop only. Copy shared with the
        # GT-Slice-2 row payload's disabled state.
        return _fail(
            "demand_court_hard_stopped", _demand_hard_stop_reason(court),
        )
    clause_type = str(action_params.get("clause_type") or "").strip()
    if clause_type not in _DEMAND_ADDABLE_CLAUSE_TYPES:
        return _fail("invalid_clause_type")
    group = str(action_params.get("group") or "").strip().lower()
    if not group:
        # §3.3: the court's direction picks which group leads — and which
        # arm an unqualified add lands on (a losing court leads with offers).
        group = "offer" if direction == "concede" else "demand"
    if group not in ("demand", "offer"):
        return _fail(
            "invalid_demand_group",
            "Terms are either demanded of a court or offered to it, Sire.",
        )
    if not proposer_leader:
        return _fail(
            "no_proposer_leader",
            "The proposing side has no leader to carry the terms, Sire.",
        )
    if group == "offer" and clause_type not in _DEMAND_OFFERABLE_CLAUSE_TYPES:
        return _fail(
            "offer_group_not_available",
            "That term can only be demanded of a court, Sire — never "
            "offered.",
        )

    promised = _promised_regions_in_terms(terms)
    proposer_participants = [
        str(n) for n in (war_instance.get(proposer_side) or []) if n
    ]
    clause: Dict[str, Any]
    if clause_type == "territory_cede":
        region = str(action_params.get("region") or "").strip()
        if group == "demand":
            try:
                court_regions = {str(r) for r in world.get_nation_regions(court)}
            except Exception:
                court_regions = set()
            if not region:
                region = str(
                    _demand_baseline_select_region(
                        world,
                        court=court,
                        proposer_side_participants=proposer_participants,
                        excluded_regions=promised,
                    )
                    or ""
                )
            if not region or region not in court_regions:
                return _fail(
                    "no_transferable_region",
                    f"{court} holds no region we may demand, Sire."
                    if not region
                    else f"{court} does not hold {region}, Sire.",
                )
            payer, payee = court, proposer_leader
        else:
            if not region:
                region = _guided_region_offer_candidate(
                    world,
                    court=court,
                    proposer_side_participants=proposer_participants,
                    settlement_terms=terms,
                )
            proposer_holdings: Set[str] = set()
            for participant in proposer_participants:
                try:
                    proposer_holdings.update(
                        str(r) for r in world.get_nation_regions(participant)
                    )
                except Exception:
                    continue
            if not region or region not in proposer_holdings:
                return _fail(
                    "no_transferable_region",
                    "We hold no region left to offer, Sire."
                    if not region
                    else f"We do not hold {region}, Sire.",
                )
            payer, payee = proposer_leader, court
        if region in promised:
            # Table-scoped V1, pre-checked so the suggestion path never
            # authors a draft the restage validator must bounce.
            return _fail(
                "region_double_promised",
                f"{region} is already promised elsewhere in this "
                "settlement, Sire.",
            )
        clause = {
            "type": "territory_cede", "from": payer, "to": payee,
            "region": region,
        }
    elif clause_type == "gold_indemnity":
        raw_amount = action_params.get("amount")
        if raw_amount is None:
            if group == "demand":
                court_balance = _concession_baseline_payer_balance(world, court)
                amount = min(
                    court_balance - CONCESSION_BASELINE_TREASURY_RESERVE,
                    CONCESSION_BASELINE_GOLD_FLOOR,
                )
            else:
                # §3.4: the offer default caps at the TABLE-scoped remaining
                # treasury, never the row-local balance.
                amount = _guided_gold_offer_default(
                    world,
                    proposer_side_leader=proposer_leader,
                    settlement_terms=terms,
                )
            if amount <= 0:
                return _fail(
                    "no_affordable_gold",
                    f"{court} has no gold to yield, Sire."
                    if group == "demand"
                    else "The treasury has nothing left to offer, Sire.",
                )
        else:
            try:
                amount = int(raw_amount)
            except (TypeError, ValueError):
                return _fail(
                    "invalid_magnitude", "That is not a sum of gold, Sire.",
                )
            if amount < 1:
                return _fail(
                    "invalid_magnitude",
                    "The sum must be at least 1 gold, Sire.",
                )
        payer, payee = (
            (court, proposer_leader) if group == "demand"
            else (proposer_leader, court)
        )
        clause = {
            "type": "gold_indemnity", "from": payer, "to": payee,
            "amount": int(amount),
        }
    elif clause_type == "gold_per_turn":
        # Slice-1 contract: recurring gold takes explicit magnitude (the §4
        # capacity-bounded PRE-FILL is the GT-Slice-2 suggestion payload).
        try:
            amount = int(action_params.get("amount"))
            turns = int(action_params.get("turns"))
        except (TypeError, ValueError):
            return _fail(
                "invalid_magnitude",
                "Name the rate and the term of turns, Sire.",
            )
        if amount < GOLD_PER_TURN_MIN_AMOUNT:
            return _fail(
                "invalid_magnitude",
                f"The rate must be at least {GOLD_PER_TURN_MIN_AMOUNT} "
                "gold a turn, Sire.",
            )
        if not (GOLD_PER_TURN_MIN_TURNS <= turns <= GOLD_PER_TURN_MAX_TURNS):
            return _fail(
                "invalid_magnitude",
                f"The term must run between {GOLD_PER_TURN_MIN_TURNS} and "
                f"{GOLD_PER_TURN_MAX_TURNS} turns, Sire.",
            )
        payer, payee = (
            (court, proposer_leader) if group == "demand"
            else (proposer_leader, court)
        )
        clause = {
            "type": "gold_per_turn", "from": payer, "to": payee,
            "amount": int(amount), "turns": int(turns),
        }
    elif clause_type in ("vassalage", "subjugation"):
        evaluator = (
            evaluate_vassalage_eligibility
            if clause_type == "vassalage"
            else evaluate_subjugation_eligibility
        )
        eligibility = evaluator(
            world,
            war_instance=war_instance,
            lord_nation=proposer_leader,
            target_nation=court,
        )
        if not eligibility.get("eligible"):
            return _fail(
                str(eligibility.get("refusal_code") or "dependency_invalid"),
                str(eligibility.get("disabled_reason_display") or ""),
            )
        clause = {"type": clause_type, "from": court, "to": proposer_leader}
    elif clause_type == "forced_alliance":
        clause = {
            "type": "forced_alliance", "from": court, "to": proposer_leader,
        }
        if action_params.get("includes_continental_system"):
            clause["includes_continental_system"] = True
    else:  # liberation
        vassals = getattr(world, "vassals", {}) or {}
        court_vassals = sorted(
            str(v) for v, s in vassals.items()
            if isinstance(s, Mapping)
            and str(s.get("lord") or s.get("lord_nation") or "") == court
        )
        vassal_nation = str(action_params.get("vassal_nation") or "").strip()
        if not vassal_nation:
            if not court_vassals:
                return _fail(
                    "liberation_target_not_vassal",
                    f"{court} holds no vassal to free, Sire.",
                )
            vassal_nation = court_vassals[0]
        eligibility = evaluate_liberation_eligibility(
            world,
            war_instance=war_instance,
            vassal_nation=vassal_nation,
            lord_nation=court,
            liberator=proposer_leader,
        )
        if not eligibility.get("eligible"):
            return _fail(
                str(eligibility.get("refusal_code") or "liberation_invalid"),
                str(eligibility.get("disabled_reason_display") or ""),
            )
        clause = {
            "type": "liberation",
            "vassal_nation": vassal_nation,
            "lord_nation": court,
            "liberator": proposer_leader,
        }

    # §3.5: hand-authored lines carry provenance — the dial sweep protects
    # them; per-line Remove is the player's deletion verb.
    clause["authored_by"] = "player"
    new_terms = [dict(t) for t in terms] + [clause]
    arm = "Demanded" if group == "demand" else "Offered"
    # GT-Slice-V — authoring voice beats ride the restaged dialogue:
    # the DC-4 guard line when a demand lands on a court that is beating
    # France (D5 press-past-zero stays legal; Talleyrand prices it), and
    # the affected court's named-diplomat reaction (§16.1a resolver rule —
    # named envoy via `resolve_named_diplomat`, chancery fallback, never
    # an anonymous beat).
    clause_label = _demand_clause_label(clause)
    voice_beats: List[Dict[str, str]] = []
    if group == "demand" and direction == "concede":
        voice_beats.append({
            "kind": "talleyrand_caution",
            "speaker": "Talleyrand",
            "nation": court,
            "line": resolve_settlement_voice_line(
                "settlement_demand_on_concede_court_caution_talleyrand",
            ),
        })
    reaction_speaker = resolve_named_diplomat("envoy", court, world)
    voice_beats.append({
        "kind": "court_reaction",
        "speaker": reaction_speaker,
        "nation": court,
        "line": resolve_settlement_voice_line(
            "settlement_multi_court_demand_received"
            if group == "demand"
            else "settlement_multi_court_offer_received",
            speaker=reaction_speaker,
            court=court,
            demand_label=clause_label,
            offer_label=clause_label,
        ),
    })
    return _restage_settlement_after_redraw(
        world,
        dialogue,
        action=action,
        new_terms=new_terms,
        new_covered=covered,
        message=f"{arm} {clause_label}.",
        extra={"authoring_voice_beats": voice_beats},
    )


def _handle_settlement_dialogue_action_inner(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Handle C2 settlement dialogue actions (the per-action dispatch arms).

    Callers use the public ``handle_settlement_dialogue_action`` wrapper,
    which enforces the CH-5 response-shape invariant on every arm's result —
    arms here may return bare failures and rely on the wrapper to re-attach
    the mounted dialogue and render ``error_display``.

    ``confirm_settlement`` runs the live ratification mutation through
    ``ratify_settlement_confirm``. ``back_out`` / ``revise_terms`` remain
    pure (no mutation, dialogue popped).

    ``action_params`` carries the clicked affordance's structured fields (e.g.
    a dial's ``scope`` or a coverage edit's ``nation``) for the Re-front Slice 2
    PROPOSE actions (``settlement_dial_*`` / ``settlement_cover_*`` /
    ``settlement_focus_court``), which ride on per-court rows and rail buttons
    rather than the keyword-matched ``options[]`` surface.
    """
    action_params = dict(action_params or {})
    war_id = str(dialogue.get("war_id") or "")
    dialogue_type = str(dialogue.get("type") or dialogue.get("dialogue_type") or "")
    if dialogue_type == "settlement_scope_replace_confirm":
        if action == "keep_current_scope_draft":
            return _restore_scope_replace_current_dialogue(
                world, dialogue, action=action,
            )
        if action == "back_out_settlement":
            return _restore_scope_replace_current_dialogue(
                world, dialogue, action=action,
            )
        if action == "replace_current_scope_draft":
            return _apply_scope_replace_confirm(world, dialogue)
        return {
            "success": False,
            "dialogue_type": "settlement_scope_replace_confirm",
            "action": action,
            "war_id": war_id,
            "error": "unknown_settlement_action",
            "mutated": False,
        }
    if action in (
        "settlement_dial_harsher",
        "settlement_dial_generous",
        "settlement_cover_add",
        "settlement_cover_drop",
        "settlement_focus_court",
    ):
        # CH-5: the old per-arm re-show safety net that lived here (re-attach
        # the mounted dialogue on a bare Tier-2 failure) is subsumed by the
        # `_enforce_settlement_response_shape` wrapper, which applies it to
        # EVERY arm — not just these five verbs.
        return _handle_settlement_tier2_action(
            world, action=action, dialogue=dialogue, action_params=action_params,
        )
    if action in SETTLEMENT_DEMAND_VERB_ACTION_IDS:
        # GT-Slice-1 (§7 wiring point 1): the guided demand-mutation verbs
        # join the dispatch INSIDE the CH-5 wrapper — their failure contract
        # (re-attached dialogue + error_display, never neither) is enforced
        # by `_enforce_settlement_response_shape`, not a per-arm net.
        return _handle_settlement_demand_action(
            world, action=action, dialogue=dialogue, action_params=action_params,
        )
    if action == "suspend_settlement_editor":
        # SC-5R-2 follow-up: the client-side settlement editor's Back Out
        # closes the staged settlement_confirm hard-stop so ordinary
        # commands are no longer held by the executor hard-stop gate,
        # while PRESERVING the scoped draft so the player can reopen the
        # same war/scope and resume. Unlike `back_out_settlement` (which
        # discards by the SC-2 contract), this is a non-destructive
        # suspend modelled on the `open_war_detail` preserve path: no
        # mutation, no recovery navigation, drafts kept.
        terms = [
            dict(t)
            for t in (dialogue.get("settlement_terms") or [])
            if isinstance(t, Mapping)
        ]
        covered = list(dialogue.get("covered_enemy_participants") or [])
        selected_target = str(dialogue.get("selected_target_nation") or "")
        if terms:
            # PF-2 / D4 + CH-3: the scoped store is the ONE draft store for
            # the suspend→reopen promise. The legacy war_id-keyed dual-write
            # is gone — it was never consulted on reopen, and two stores with
            # one reader is exactly how the "Settlement draft kept" promise
            # broke.
            save_scoped_settlement_draft(
                world,
                war_id=war_id,
                selected_target_nation=selected_target,
                covered_enemy_participants=covered,
                settlement_terms=terms,
            )
        world.dialogue_manager.pop()
        return {
            "success": True,
            "dialogue_type": "settlement_confirm",
            "action": "suspend_settlement_editor",
            "war_id": war_id,
            "draft_preserved": bool(terms),
            "mutated": False,
            "message": "Settlement draft kept. Reopen Settlement to continue editing.",
            "suppress_proposal_result_popup": True,
        }
    if action == "back_out_settlement":
        # SC-2: discard-confirm semantics. Non-empty drafts signal the
        # frontend to confirm discard; empty drafts pop immediately.
        terms = list(dialogue.get("settlement_terms") or [])
        has_draft = bool(terms)
        world.dialogue_manager.pop()
        # Clear persisted draft on back-out.
        drafts = getattr(world, "pending_settlement_drafts", {})
        if war_id in drafts:
            del drafts[war_id]
        _discard_scoped_settlement_draft_for_dialogue(world, dialogue)
        return {
            "success": True,
            "dialogue_type": "settlement_confirm",
            "action": "back_out",
            "cancelled": True,
            "mutated": False,
            "had_draft": has_draft,
            "message": "Settlement review cancelled.",
            "talleyrand_text": (
                resolve_settlement_voice_line(
                    "settlement_discard_confirm_talleyrand",
                    war_label=str(dialogue.get("war_label") or war_id or "this war"),
                )
                if has_draft
                else ""
            ),
            "suppress_proposal_result_popup": True,
        }
    if action == "submit_settlement_for_review":
        # Re-front Slice 1 §3a: PROPOSE -> REVIEW. Lock in the conversational
        # draft and re-stage it as the blocking REVIEW surface so the per-court
        # ratification gate (§11.4) runs against the authored package. Empty
        # drafts cannot be submitted (mirrors the editor's non-empty gate).
        terms = [
            dict(t) for t in (dialogue.get("settlement_terms") or [])
            if isinstance(t, Mapping)
        ]
        covered = list(dialogue.get("covered_enemy_participants") or [])
        selected_target = str(dialogue.get("selected_target_nation") or "")
        if not terms:
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": "submit_settlement_for_review",
                "war_id": war_id,
                "error": "empty_authored_draft",
                "error_display": _error_display("empty_authored_draft"),
                "mutated": False,
                "talleyrand_text": (
                    "Sire, there are no terms to submit. Shape the settlement first."
                ),
            }
        # PF-1 / D1-D2: the submit arm is a staging point — validate the draft
        # (generated baseline or dialed) BEFORE popping PROPOSE, so an invalid
        # package can never reach the REVIEW ratification gate. On failure the
        # still-mounted PROPOSE dialogue is re-attached (the Tier-2 net
        # pattern) with the failure rendered, never a silent dead end.
        submit_validation = validate_settlement_terms(
            terms,
            proposer_side=str(dialogue.get("proposer_side") or ""),
            covered_enemy_participants=covered,
            world=world,
            war_instance=(getattr(world, "war_instances", {}) or {}).get(war_id) or {},
        )
        if not submit_validation.get("valid"):
            blocker = str(
                submit_validation.get("disabled_reason_display")
                or _error_display(str(submit_validation.get("error") or ""))
            )
            talleyrand_line = resolve_settlement_voice_line(
                "settlement_submit_failed_validation_talleyrand",
                war_label=str(dialogue.get("war_label") or war_id or "this war"),
                blocker=blocker,
            )
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": "submit_settlement_for_review",
                "war_id": war_id,
                "error": "submitted_terms_failed_revalidation",
                "error_display": blocker
                or _error_display("submitted_terms_failed_revalidation"),
                "validation_error": submit_validation.get("error"),
                "validation_error_index": submit_validation.get("error_index"),
                "mutated": False,
                "diplomatic_dialogue": dict(dialogue),
                "awaiting_diplomatic_response": True,
                "talleyrand_text": talleyrand_line,
                "message": talleyrand_line or blocker,
                "suppress_proposal_result_popup": True,
            }
        # Drop the non-blocking PROPOSE surface, then stage REVIEW fresh.
        world.dialogue_manager.pop()
        return stage_settlement_confirm(
            world,
            war_id=war_id,
            settlement_terms=terms,
            selected_target_nation=selected_target or (covered[0] if covered else None),
            covered_enemy_participants=covered,
            actor_nation=str(getattr(world, "player_nation", "France") or "France"),
            caller_kind="player_editor",
            dialogue_mode="REVIEW",
        )
    if action == "return_to_settlement_terms":
        # Re-front UX follow-up: REVIEW -> PROPOSE. Re-stage the conversational
        # authoring surface (whole-table dials + per-court rows) with the current
        # draft so a blocked REVIEW is recoverable without discarding it. Mirrors
        # `submit_settlement_for_review` in reverse; the blocked REVIEW surfaces
        # this so a non-carrying package is never a dead end.
        terms = [
            dict(t) for t in (dialogue.get("settlement_terms") or [])
            if isinstance(t, Mapping)
        ]
        covered = list(dialogue.get("covered_enemy_participants") or [])
        selected_target = str(dialogue.get("selected_target_nation") or "")
        world.dialogue_manager.pop()
        return stage_settlement_confirm(
            world,
            war_id=war_id,
            settlement_terms=terms,
            selected_target_nation=selected_target or (covered[0] if covered else None),
            covered_enemy_participants=covered,
            actor_nation=str(getattr(world, "player_nation", "France") or "France"),
            caller_kind="player_editor",
            dialogue_mode="PROPOSE",
        )
    if action == "revise_settlement_terms":
        # SC-2: Revise Terms is hidden until a real editor exists.
        # If somehow called, treat as a no-op re-show.
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": "revise_terms",
            "war_id": war_id,
            "error": "revision_not_available",
            "error_display": "Term revision is not yet available.",
            "mutated": False,
        }
    if action == "author_gold_indemnity_terms":
        selected_target = str(dialogue.get("selected_target_nation") or "")
        actor = str(getattr(world, "player_nation", "France") or "France")
        if not selected_target:
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": action,
                "war_id": war_id,
                "error": "no_selected_target_nation",
                "error_display": _error_display("no_selected_target_nation"),
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        # SC-5R-1 audit punch list fix: `gold_indemnity` schema per
        # CANONICAL_CLAUSE_TYPES is {type, from, to, amount} with no
        # optional keys. The previous draft included `"turns": 0` which
        # `validate_settlement_terms` rejects as `invalid_clause_schema`
        # (unknown_keys=["turns"]) at Submit/ratify time. Use
        # gold_per_turn for recurring obligations; gold_indemnity is a
        # single-payment lump sum.
        authored_terms = [
            {"type": "peace"},
            {
                "type": "gold_indemnity",
                "from": selected_target,
                "to": actor,
                "amount": 200,
            },
        ]
        return _stage_replacement_settlement_terms(
            world,
            dialogue,
            action="author_gold_indemnity_terms",
            terms=authored_terms,
            message="A gold-indemnity demand has been drafted for review.",
        )
    if action == "author_gold_per_turn_terms":
        selected_target = str(dialogue.get("selected_target_nation") or "")
        actor = str(getattr(world, "player_nation", "France") or "France")
        if not selected_target:
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": action,
                "war_id": war_id,
                "error": "no_selected_target_nation",
                "error_display": _error_display("no_selected_target_nation"),
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        authored_terms = [
            {"type": "peace"},
            {
                "type": "gold_per_turn",
                "from": selected_target,
                "to": actor,
                "amount": 50,
                "turns": 3,
            },
        ]
        return _stage_replacement_settlement_terms(
            world,
            dialogue,
            action="author_gold_per_turn_terms",
            terms=authored_terms,
            message="A recurring-gold demand has been drafted for review.",
        )

    def _fresh_recurring_gold_preset(
        action_id: str,
    ) -> Tuple[Optional[Mapping[str, Any]], List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        covered = list(dialogue.get("covered_enemy_participants") or [])
        actor = getattr(world, "player_nation", "France")
        fresh_empty_preview = build_settlement_preview(
            world,
            war_id=war_id,
            proposer_side=str(dialogue.get("proposer_side") or ""),
            settlement_terms=[],
            covered_enemy_participants=covered,
            actor_nation=actor,
            ignore_active_dialogue=True,
        )
        if not fresh_empty_preview.get("success"):
            return None, [], {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": action_id,
                "war_id": war_id,
                "error": fresh_empty_preview.get("error") or "recurring_gold_preset_unavailable",
                "error_display": fresh_empty_preview.get("error_display") or (
                    "No recurring-gold draft is available now."
                ),
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        fresh_preview = fresh_empty_preview["settlement_preview"]
        preset_payload = fresh_preview.get("recurring_gold_preset")
        preset_terms = (
            [dict(t) for t in (preset_payload.get("terms") or []) if isinstance(t, Mapping)]
            if isinstance(preset_payload, Mapping)
            else []
        )
        if (
            not fresh_preview.get("recurring_gold_preset_visible")
            or not any(t.get("type") == "gold_per_turn" for t in preset_terms)
        ):
            return None, [], {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": action_id,
                "war_id": war_id,
                "error": "recurring_gold_preset_unavailable",
                "error_display": "No recurring-gold draft is available now.",
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        return preset_payload, preset_terms, None

    if action == "keep_current_settlement_draft":
        preserved_terms = [
            dict(t)
            for t in (
                dialogue.get("preserved_terms")
                or dialogue.get("settlement_terms")
                or []
            )
            if isinstance(t, Mapping)
        ]
        return _stage_replacement_settlement_terms(
            world,
            dialogue,
            action="keep_current_settlement_draft",
            terms=preserved_terms,
            message="Keeping the current settlement draft unchanged.",
            surrender_preset=bool(dialogue.get("surrender_preset", False)),
        )
    if action == "apply_recurring_gold_preset_replacement":
        preset_payload, preset_terms, error_payload = _fresh_recurring_gold_preset(action)
        if error_payload is not None:
            return error_payload
        return _stage_replacement_settlement_terms(
            world,
            dialogue,
            action=action,
            terms=preset_terms,
            message="Talleyrand's recurring-gold draft has replaced the current draft.",
        )
    if action == "apply_concession_baseline_replacement":
        # GT-Slice-4 (§5 re-point): the applied concession baseline re-stages
        # the guided PROPOSE surface (no editor mount) — the player lands on
        # the per-court authoring rows seeded with Talleyrand's baseline.
        covered = list(dialogue.get("covered_enemy_participants") or [])
        actor = getattr(world, "player_nation", "France")
        fresh_empty_preview = build_settlement_preview(
            world,
            war_id=war_id,
            proposer_side=str(dialogue.get("proposer_side") or ""),
            settlement_terms=[],
            covered_enemy_participants=covered,
            actor_nation=actor,
            ignore_active_dialogue=True,
        )
        if not fresh_empty_preview.get("success"):
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": action,
                "war_id": war_id,
                "error": fresh_empty_preview.get("error") or "concession_baseline_unavailable",
                "error_display": fresh_empty_preview.get("error_display") or (
                    "No concession baseline is available now."
                ),
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        fresh_preview = fresh_empty_preview["settlement_preview"]
        baseline = fresh_preview.get("concession_baseline")
        baseline_terms = (
            [dict(t) for t in (baseline.get("terms") or []) if isinstance(t, Mapping)]
            if isinstance(baseline, Mapping)
            else []
        )
        if (
            not fresh_preview.get("concession_baseline_visible")
            or not _has_material_concession_terms(baseline_terms)
        ):
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": action,
                "war_id": war_id,
                "error": "concession_baseline_unavailable",
                "error_display": "No concession baseline is available now.",
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        return _stage_replacement_settlement_terms(
            world,
            dialogue,
            action=action,
            terms=baseline_terms,
            message="Talleyrand's concession baseline has replaced the current draft.",
            dialogue_mode="PROPOSE",
        )
    if action == "apply_surrender_preset_replacement":
        covered = list(dialogue.get("covered_enemy_participants") or [])
        actor = getattr(world, "player_nation", "France")
        fresh_empty_preview = build_settlement_preview(
            world,
            war_id=war_id,
            proposer_side=str(dialogue.get("proposer_side") or ""),
            settlement_terms=[],
            covered_enemy_participants=covered,
            actor_nation=actor,
            ignore_active_dialogue=True,
        )
        if not fresh_empty_preview.get("success"):
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": action,
                "war_id": war_id,
                "error": fresh_empty_preview.get("error") or "surrender_preset_unavailable",
                "error_display": fresh_empty_preview.get("error_display") or (
                    "No surrender preset is available now."
                ),
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        fresh_preview = fresh_empty_preview["settlement_preview"]
        preset_payload = fresh_preview.get("surrender_preset")
        preset_terms = (
            [dict(t) for t in (preset_payload.get("terms") or []) if isinstance(t, Mapping)]
            if isinstance(preset_payload, Mapping)
            else []
        )
        if (
            not fresh_preview.get("surrender_preset_visible")
            or not any(
                isinstance(t, Mapping) and t.get("type") in ("vassalage", "subjugation")
                for t in preset_terms
            )
        ):
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": action,
                "war_id": war_id,
                "error": "surrender_preset_unavailable",
                "error_display": "No surrender preset is available now.",
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        return _stage_replacement_settlement_terms(
            world,
            dialogue,
            action=action,
            terms=preset_terms,
            message="Talleyrand's surrender preset has replaced the current draft.",
            surrender_preset=True,
        )
    if action == "re_author_with_concessions":
        covered = list(dialogue.get("covered_enemy_participants") or [])
        selected_target = str(dialogue.get("selected_target_nation") or "")
        actor = getattr(world, "player_nation", "France")
        current_terms = [
            dict(t)
            for t in (dialogue.get("settlement_terms") or [])
            if isinstance(t, Mapping)
        ]
        fresh_empty_preview = build_settlement_preview(
            world,
            war_id=war_id,
            proposer_side=str(dialogue.get("proposer_side") or ""),
            settlement_terms=[],
            covered_enemy_participants=covered,
            actor_nation=actor,
            ignore_active_dialogue=True,
        )
        if not fresh_empty_preview.get("success"):
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": "re_author_with_concessions",
                "war_id": war_id,
                "error": fresh_empty_preview.get("error") or "concession_baseline_unavailable",
                "error_display": fresh_empty_preview.get("error_display") or (
                    "No concession baseline is available now."
                ),
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        fresh_preview = fresh_empty_preview["settlement_preview"]
        baseline = fresh_preview.get("concession_baseline")
        baseline_terms = (
            [dict(t) for t in (baseline.get("terms") or []) if isinstance(t, Mapping)]
            if isinstance(baseline, Mapping)
            else []
        )
        if (
            not fresh_preview.get("concession_baseline_visible")
            or not _has_material_concession_terms(baseline_terms)
        ):
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": "re_author_with_concessions",
                "war_id": war_id,
                "error": "concession_baseline_unavailable",
                "error_display": "No concession baseline is available now.",
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        if current_terms:
            if _term_lists_equal(current_terms, baseline_terms):
                refreshed = copy.deepcopy(dict(dialogue))
                refreshed["options"] = [
                    dict(opt)
                    for opt in (refreshed.get("options") or [])
                    if opt.get("action") != "re_author_with_concessions"
                ]
                refreshed["available_action_ids"] = [
                    str(a)
                    for a in (refreshed.get("available_action_ids") or [])
                    if str(a) != "re_author_with_concessions"
                ]
                refreshed["message"] = "Talleyrand's concession baseline is already drafted."
                refreshed["talleyrand_text"] = refreshed["message"]
                world.dialogue_manager.replace(refreshed)
                return {
                    "success": True,
                    "dialogue_type": "settlement_confirm",
                    "action": "re_author_with_concessions",
                    "war_id": war_id,
                    "diplomatic_dialogue": refreshed,
                    "awaiting_diplomatic_response": True,
                    "mutated": False,
                    "message": refreshed["message"],
                    "suppress_proposal_result_popup": True,
                }
            replace_dialogue = _build_settlement_replace_confirm_dialogue(
                dialogue,
                replacement_terms=baseline_terms,
                apply_action="apply_concession_baseline_replacement",
                apply_label="Discard draft and apply Talleyrand baseline",
                replacement_kind="concession_baseline",
                message=(
                    "This draft is not empty. Replace it with Talleyrand's "
                    "concession baseline?"
                ),
                concession_baseline=baseline,
            )
            world.dialogue_manager.replace(replace_dialogue)
            return {
                "success": True,
                "dialogue_type": "settlement_confirm",
                "action": "re_author_with_concessions",
                "war_id": war_id,
                "requires_replace_confirm": True,
                "replacement_terms": baseline_terms,
                "diplomatic_dialogue": replace_dialogue,
                "awaiting_diplomatic_response": True,
                "concession_baseline": copy.deepcopy(baseline),
                "mutated": False,
                "message": "Confirm replacing the current draft with Talleyrand's concession baseline.",
                "suppress_proposal_result_popup": True,
            }
        baseline_preview = build_settlement_preview(
            world,
            war_id=war_id,
            proposer_side=str(dialogue.get("proposer_side") or ""),
            settlement_terms=baseline_terms,
            covered_enemy_participants=covered,
            actor_nation=actor,
            ignore_active_dialogue=True,
        )
        if not baseline_preview.get("success"):
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": "re_author_with_concessions",
                "war_id": war_id,
                "error": baseline_preview.get("error") or "concession_baseline_failed_preview",
                "error_display": baseline_preview.get("error_display") or (
                    "The concession baseline could not be previewed."
                ),
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        # GT-Slice-4 (§5 re-point): the rail action survives; only its
        # destination changes — the concession baseline re-stages the guided
        # PROPOSE surface seeded from the baseline (no editor mount).
        new_dialogue = build_settlement_confirm_dialogue(
            world,
            baseline_preview,
            selected_target_nation=selected_target or None,
            caller_kind=str(dialogue.get("caller_kind") or "player_editor"),
            white_peace=False,
            dialogue_mode="PROPOSE",
        )
        drafts = getattr(world, "pending_settlement_drafts", None)
        if drafts is None:
            world.pending_settlement_drafts = {}
            drafts = world.pending_settlement_drafts
        drafts[war_id] = [dict(t) for t in baseline_terms]
        save_scoped_settlement_draft(
            world,
            war_id=war_id,
            selected_target_nation=selected_target,
            covered_enemy_participants=covered,
            settlement_terms=baseline_terms,
        )
        world.dialogue_manager.replace(new_dialogue)
        result = {
            "success": True,
            "dialogue_type": "settlement_confirm",
            "action": "re_author_with_concessions",
            "war_id": war_id,
            "diplomatic_dialogue": new_dialogue,
            "settlement_preview": baseline_preview["settlement_preview"],
            "awaiting_diplomatic_response": True,
            "concession_baseline": copy.deepcopy(baseline),
            "mutated": False,
            "message": "Talleyrand's concession baseline has been drafted for review.",
            "suppress_proposal_result_popup": True,
        }
        return result
    if action == "author_recurring_gold_terms":
        selected_target = str(dialogue.get("selected_target_nation") or "")
        current_terms = [
            dict(t)
            for t in (dialogue.get("settlement_terms") or [])
            if isinstance(t, Mapping)
        ]
        preset_payload, preset_terms, error_payload = _fresh_recurring_gold_preset(action)
        if error_payload is not None:
            error_payload["preserved_terms"] = current_terms
            return error_payload
        if current_terms:
            if _term_lists_equal(current_terms, preset_terms):
                refreshed = copy.deepcopy(dict(dialogue))
                refreshed["options"] = [
                    dict(opt)
                    for opt in (refreshed.get("options") or [])
                    if opt.get("action") != "author_recurring_gold_terms"
                ]
                refreshed["available_action_ids"] = [
                    str(a)
                    for a in (refreshed.get("available_action_ids") or [])
                    if str(a) != "author_recurring_gold_terms"
                ]
                refreshed["message"] = "Talleyrand's recurring-gold draft is already drafted."
                refreshed["talleyrand_text"] = refreshed["message"]
                world.dialogue_manager.replace(refreshed)
                return {
                    "success": True,
                    "dialogue_type": "settlement_confirm",
                    "action": "author_recurring_gold_terms",
                    "war_id": war_id,
                    "diplomatic_dialogue": refreshed,
                    "awaiting_diplomatic_response": True,
                    "mutated": False,
                    "message": refreshed["message"],
                    "suppress_proposal_result_popup": True,
                }
            replace_dialogue = _build_settlement_replace_confirm_dialogue(
                dialogue,
                replacement_terms=preset_terms,
                apply_action="apply_recurring_gold_preset_replacement",
                apply_label="Discard draft and apply recurring gold",
                replacement_kind="recurring_gold_preset",
                message=(
                    "This draft is not empty. Replace it with Talleyrand's "
                    "recurring-gold draft?"
                ),
                recurring_gold_preset_payload=preset_payload,
            )
            world.dialogue_manager.replace(replace_dialogue)
            return {
                "success": True,
                "dialogue_type": "settlement_confirm",
                "action": "author_recurring_gold_terms",
                "war_id": war_id,
                "requires_replace_confirm": True,
                "replacement_terms": preset_terms,
                "diplomatic_dialogue": replace_dialogue,
                "awaiting_diplomatic_response": True,
                "recurring_gold_preset": copy.deepcopy(preset_payload),
                "mutated": False,
                "message": "Confirm replacing the current draft with Talleyrand's recurring-gold draft.",
                "suppress_proposal_result_popup": True,
            }
        return _stage_replacement_settlement_terms(
            world,
            dialogue,
            action="author_recurring_gold_terms",
            terms=preset_terms,
            message="Talleyrand's recurring-gold draft has been drafted for review.",
        )
    if action == "author_surrender_terms":
        # SC-31 / G2-Slice-8 - Apply Talleyrand's surrender preset.
        # Mirrors `re_author_with_concessions`: re-runs POST preview
        # against an empty draft to revalidate the surrender preset, and
        # only stages a fresh `settlement_confirm` with the preset terms
        # after a click-time re-check. On stale failure the current
        # draft is preserved verbatim, no mutation, no popup, and the
        # caller-side popup remains mounted so the player can choose
        # another recovery route.
        covered = list(dialogue.get("covered_enemy_participants") or [])
        selected_target = str(dialogue.get("selected_target_nation") or "")
        actor = getattr(world, "player_nation", "France")
        current_terms = [
            dict(t)
            for t in (dialogue.get("settlement_terms") or [])
            if isinstance(t, Mapping)
        ]
        fresh_empty_preview = build_settlement_preview(
            world,
            war_id=war_id,
            proposer_side=str(dialogue.get("proposer_side") or ""),
            settlement_terms=[],
            covered_enemy_participants=covered,
            actor_nation=actor,
            ignore_active_dialogue=True,
        )
        if not fresh_empty_preview.get("success"):
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": "author_surrender_terms",
                "war_id": war_id,
                "error": fresh_empty_preview.get("error") or "surrender_preset_unavailable",
                "error_display": fresh_empty_preview.get("error_display") or (
                    "No surrender preset is available now."
                ),
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        fresh_preview = fresh_empty_preview["settlement_preview"]
        preset_payload = fresh_preview.get("surrender_preset")
        preset_terms = (
            [dict(t) for t in (preset_payload.get("terms") or []) if isinstance(t, Mapping)]
            if isinstance(preset_payload, Mapping)
            else []
        )
        if (
            not fresh_preview.get("surrender_preset_visible")
            or not any(
                t.get("type") in ("vassalage", "subjugation") for t in preset_terms
            )
        ):
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": "author_surrender_terms",
                "war_id": war_id,
                "error": "surrender_preset_unavailable",
                "error_display": "No surrender preset is available now.",
                "mutated": False,
                "preserved_terms": current_terms,
                "suppress_proposal_result_popup": True,
            }
        if current_terms:
            if _term_lists_equal(current_terms, preset_terms):
                refreshed = copy.deepcopy(dict(dialogue))
                refreshed["options"] = [
                    dict(opt)
                    for opt in (refreshed.get("options") or [])
                    if opt.get("action") != "author_surrender_terms"
                ]
                refreshed["available_action_ids"] = [
                    str(a)
                    for a in (refreshed.get("available_action_ids") or [])
                    if str(a) != "author_surrender_terms"
                ]
                refreshed["message"] = "Talleyrand's surrender preset is already drafted."
                refreshed["talleyrand_text"] = refreshed["message"]
                world.dialogue_manager.replace(refreshed)
                return {
                    "success": True,
                    "dialogue_type": "settlement_confirm",
                    "action": "author_surrender_terms",
                    "war_id": war_id,
                    "diplomatic_dialogue": refreshed,
                    "awaiting_diplomatic_response": True,
                    "mutated": False,
                    "message": refreshed["message"],
                    "suppress_proposal_result_popup": True,
                }
            replace_dialogue = _build_settlement_replace_confirm_dialogue(
                dialogue,
                replacement_terms=preset_terms,
                apply_action="apply_surrender_preset_replacement",
                apply_label="Discard draft and apply surrender preset",
                replacement_kind="surrender_preset",
                message=(
                    "This draft is not empty. Replace it with Talleyrand's "
                    "surrender preset?"
                ),
                surrender_preset_payload=preset_payload,
            )
            world.dialogue_manager.replace(replace_dialogue)
            return {
                "success": True,
                "dialogue_type": "settlement_confirm",
                "action": "author_surrender_terms",
                "war_id": war_id,
                "requires_replace_confirm": True,
                "replacement_terms": preset_terms,
                "diplomatic_dialogue": replace_dialogue,
                "awaiting_diplomatic_response": True,
                "surrender_preset": copy.deepcopy(preset_payload),
                "mutated": False,
                "message": "Confirm replacing the current draft with Talleyrand's surrender preset.",
                "suppress_proposal_result_popup": True,
            }
        preset_preview = build_settlement_preview(
            world,
            war_id=war_id,
            proposer_side=str(dialogue.get("proposer_side") or ""),
            settlement_terms=preset_terms,
            covered_enemy_participants=covered,
            actor_nation=actor,
            ignore_active_dialogue=True,
        )
        if not preset_preview.get("success"):
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": "author_surrender_terms",
                "war_id": war_id,
                "error": preset_preview.get("error") or "surrender_preset_failed_preview",
                "error_display": preset_preview.get("error_display") or (
                    "The surrender preset could not be previewed."
                ),
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        new_dialogue = build_settlement_confirm_dialogue(
            world,
            preset_preview,
            selected_target_nation=selected_target or None,
            caller_kind=str(dialogue.get("caller_kind") or "player_editor"),
            white_peace=False,
            surrender_preset=True,
        )
        drafts = getattr(world, "pending_settlement_drafts", None)
        if drafts is None:
            world.pending_settlement_drafts = {}
            drafts = world.pending_settlement_drafts
        drafts[war_id] = [dict(t) for t in preset_terms]
        save_scoped_settlement_draft(
            world,
            war_id=war_id,
            selected_target_nation=selected_target,
            covered_enemy_participants=covered,
            settlement_terms=preset_terms,
        )
        world.dialogue_manager.replace(new_dialogue)
        return {
            "success": True,
            "dialogue_type": "settlement_confirm",
            "action": "author_surrender_terms",
            "war_id": war_id,
            "diplomatic_dialogue": new_dialogue,
            "settlement_preview": preset_preview["settlement_preview"],
            "awaiting_diplomatic_response": True,
            "surrender_preset": copy.deepcopy(preset_payload),
            "mutated": False,
            "message": "Talleyrand's surrender preset has been drafted for review.",
            "suppress_proposal_result_popup": True,
        }
    if action == "open_war_detail":
        terms = [dict(t) for t in (dialogue.get("settlement_terms") or []) if isinstance(t, Mapping)]
        covered = list(dialogue.get("covered_enemy_participants") or [])
        selected_target = str(dialogue.get("selected_target_nation") or "")
        actionability = evaluate_war_detail_actionability(
            world,
            war_id=war_id,
            selected_target_nation=selected_target,
            covered_enemy_participants=covered,
            source_route_id=str(dialogue.get("route_id") or ""),
        )
        if not actionability.get("actionable"):
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": "open_war_detail",
                "war_id": war_id,
                "error": actionability.get("error") or "no_peace_seeking_control",
                "error_display": actionability.get("error_display") or _error_display("no_peace_seeking_control"),
                "war_detail_actionability": actionability,
                "terminal_recovery_copy": _terminal_recovery_copy(war_id),
                "mutated": False,
                "suppress_proposal_result_popup": True,
            }
        if terms:
            drafts = getattr(world, "pending_settlement_drafts", None)
            if drafts is None:
                world.pending_settlement_drafts = {}
                drafts = world.pending_settlement_drafts
            drafts[war_id] = terms
            save_scoped_settlement_draft(
                world,
                war_id=war_id,
                selected_target_nation=selected_target,
                covered_enemy_participants=covered,
                settlement_terms=terms,
            )
        world.dialogue_manager.pop()
        route = dict(actionability.get("recovery_route") or {})
        return {
            "success": True,
            "dialogue_type": "settlement_confirm",
            "action": "open_war_detail",
            "war_id": war_id,
            "recovery_route": route,
            "war_detail_actionability": actionability,
            "draft_preserved": bool(terms),
            "mutated": False,
            "message": "Opening war detail.",
            "talleyrand_text": resolve_settlement_voice_line(
                "settlement_open_war_detail_recovery_talleyrand",
                war_label=str(dialogue.get("war_label") or war_id or "this war"),
            ),
            "suppress_proposal_result_popup": True,
        }
    # SC-29 / G2-Slice-7 pair-scoped peace substitute CTAs. Two explicit
    # branches per action id satisfy the Gate 3 action-id whitelist test
    # that scans `settlement_preview.py` for `action == "..."` strings.
    if action == "seek_bilateral_peace":
        return _handle_pair_peace_substitute_action(
            world, action="seek_bilateral_peace", dialogue=dialogue
        )
    if action == "seek_armistice_instead":
        return _handle_pair_peace_substitute_action(
            world, action="seek_armistice_instead", dialogue=dialogue
        )
    if action == "confirm_settlement":
        return ratify_settlement_confirm(world, dialogue)
    return {"success": False, "error": "unknown_settlement_action", "mutated": False}


def _enforce_settlement_response_shape(
    result: Any,
    dialogue: Mapping[str, Any],
) -> Any:
    """CH-5 (pre-flight audit §9) — the ONE structural invariant for every
    settlement dialogue arm: a failed/blocked action returns a re-attached
    ``diplomatic_dialogue`` AND a rendered ``error_display`` — never neither.

    Every settlement defect class found at the Gate-4 pre-flight (the
    drop-stranding orphan, D2's "Response processed", D3's silent dials, and
    D7's latent replacement-stage orphan) was this invariant violated at a
    different arm. Enforcing it once at the dispatch boundary replaces the
    retired per-arm Tier-2 re-attach net and covers every arm — including
    the replacement-stage preset family (`re_author_with_concessions` /
    `author_*` / `apply_*_replacement` / `keep_current_settlement_draft`)
    that the old net never reached, and every future arm by construction.

    - Failure + no ``diplomatic_dialogue`` while a PLAYER-editor dialogue is
      mounted → re-attach the unchanged mounted dialogue (the failure left it
      mounted; the popup re-mounts on its current state). A non-player caller
      has no popup to strand (Slice-G boundary), so it is not re-attached.
    - Failure + no ``error_display`` → synthesize one from the ``error`` code
      via the settlement display map (humanized fallback for unknown codes),
      so a failure is never silent.
    - Successes — including dialogue-closing ones (back out, suspend,
      ratify) — pass through untouched.
    """
    if not isinstance(result, Mapping):
        return result
    if result.get("success"):
        return result
    shaped = dict(result)
    if (
        not shaped.get("diplomatic_dialogue")
        and isinstance(dialogue, Mapping)
        and dialogue
        and str(dialogue.get("caller_kind") or "") == SETTLEMENT_EDITOR_CALLER_KIND
    ):
        shaped["diplomatic_dialogue"] = dict(dialogue)
        shaped.setdefault("awaiting_diplomatic_response", True)
    if not shaped.get("error_display"):
        shaped["error_display"] = _error_display(str(shaped.get("error") or ""))
    return shaped


def handle_settlement_dialogue_action(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Public settlement dialogue dispatch — the per-action arms live in
    ``_handle_settlement_dialogue_action_inner``.

    CH-5: every result passes through ``_enforce_settlement_response_shape``,
    so a failed arm always re-attaches the mounted player dialogue and always
    renders an ``error_display`` — one wrapper instead of accreting per-arm
    safety nets (the structural cure for the D2/D3/D7 orphan class).
    """
    result = _handle_settlement_dialogue_action_inner(
        world, action=action, dialogue=dialogue, action_params=action_params,
    )
    return _enforce_settlement_response_shape(result, dialogue)


def _handle_pair_peace_substitute_action(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
) -> Dict[str, Any]:
    """SC-29 / G2-Slice-7 dialogue handler for `seek_bilateral_peace` and
    `seek_armistice_instead`.

    Click-time re-runs `evaluate_pair_peace_substitute_eligibility(...)`;
    if the pair has become ineligible between render and click, the
    settlement dialogue stays mounted, no scoped draft is mutated, no
    pair route opens, and a humanized no-longer-eligible response is
    returned with the normal recovery options preserved.

    On positive re-validation, the handler pops the settlement dialogue,
    flags any scoped settlement draft whose covered scope includes the
    target pair as stale (per the War Detail recovery contract), then
    stages a `proposal_confirm` dialogue for the underlying
    `propose_armistice` / `propose_peace` flow with `target_nation =
    selected_target_nation`. The handler does not deduct DP or set
    proposal cooldowns; those happen when the player confirms / sends
    the proposal through the existing executor.
    """
    war_id = str(dialogue.get("war_id") or "")
    selected_target = str(dialogue.get("selected_target_nation") or "")
    actor = str(getattr(world, "player_nation", "France") or "France")
    proposal_type = "armistice" if action == "seek_armistice_instead" else "peace"
    voice_key = (
        "settlement_seek_armistice_instead_talleyrand"
        if action == "seek_armistice_instead"
        else "settlement_seek_bilateral_peace_instead_talleyrand"
    )
    war_label = str(dialogue.get("war_label") or war_id or "this war")

    eligibility = evaluate_pair_peace_substitute_eligibility(
        world,
        war_id=war_id,
        actor_nation=actor,
        target_nation=selected_target,
        action=action,
    )
    if not eligibility.get("eligible"):
        refusal = eligibility.get("refusal_code") or "malformed_route"
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": action,
            "war_id": war_id,
            "selected_target_nation": selected_target,
            "scope": "selected_pair",
            "error": refusal,
            "error_display": eligibility.get("disabled_reason_display")
            or _error_display(refusal),
            "pair_substitute_eligibility": eligibility,
            "mutated": False,
            "suppress_proposal_result_popup": True,
        }

    # SC-29 / War Detail recovery contract: a successful pair substitute
    # makes any preserved scoped settlement draft that covers the target
    # stale. Cleanup default for cleanup-stage `pending_settlement_drafts`
    # is keyed by `war_id`; mark the entry stale via removal here, and
    # re-preview is required on the next settlement entry per the spec.
    drafts = getattr(world, "pending_settlement_drafts", None) or {}
    covered = list(dialogue.get("covered_enemy_participants") or [])
    draft_invalidated = False
    if war_id in drafts and selected_target in covered:
        try:
            del drafts[war_id]
            draft_invalidated = True
        except Exception:  # pragma: no cover - defensive
            draft_invalidated = False
    if selected_target in covered:
        draft_invalidated = (
            _discard_scoped_settlement_draft_for_dialogue(world, dialogue)
            or draft_invalidated
        )

    # Stage the proposal dialogue through the existing classification +
    # template path so the substitute hands off into the standard
    # propose_armistice / propose_peace flow on confirm.
    try:
        from backend.game_logic.diplomatic_dialogue import (
            classify_diplomatic_intent,
            generate_dialogue,
        )
    except Exception:  # pragma: no cover - defensive
        classify_diplomatic_intent = None  # type: ignore[assignment]
        generate_dialogue = None  # type: ignore[assignment]

    proposal_dialogue: Optional[Dict[str, Any]] = None
    if classify_diplomatic_intent is not None and generate_dialogue is not None:
        diplomatic_data = {
            "target_nation": selected_target,
            "proposal_type": proposal_type,
            "raw_text": f"propose {proposal_type} with {selected_target}",
            "has_diplomatic_keywords": True,
            "is_question": False,
            "clauses": [],
        }
        try:
            intent = classify_diplomatic_intent(diplomatic_data, world)
            proposal_dialogue = generate_dialogue(intent, diplomatic_data, world)
        except Exception:  # pragma: no cover - defensive
            proposal_dialogue = None

    world.dialogue_manager.pop()
    if isinstance(proposal_dialogue, Mapping):
        world.dialogue_manager.replace(dict(proposal_dialogue))

    talleyrand_text = resolve_settlement_voice_line(
        voice_key,
        war_label=war_label,
        target_nation=selected_target,
    )

    return {
        "success": True,
        "dialogue_type": "settlement_confirm",
        "action": action,
        "war_id": war_id,
        "selected_target_nation": selected_target,
        "scope": "selected_pair",
        "proposal_type": proposal_type,
        "voice_family": voice_key,
        "talleyrand_text": talleyrand_text,
        "message": talleyrand_text,
        "draft_invalidated": draft_invalidated,
        "pair_substitute_eligibility": eligibility,
        "diplomatic_dialogue": proposal_dialogue
        if isinstance(proposal_dialogue, Mapping)
        else None,
        "recovery_route": {
            "surface": "proposal_confirm",
            "target": "proposal_confirm",
            "war_id": war_id,
            "selected_target_nation": selected_target,
            "target_nation": selected_target,
            "scope": "selected_pair",
            "proposal_type": proposal_type,
        },
        "mutated": False,
        "suppress_proposal_result_popup": True,
    }


def _remove_pending_settlement_offer(
    world: Any,
    *,
    offer_id: str,
    war_id: str,
) -> Optional[Dict[str, Any]]:
    """Remove and return the matching incoming-offer entry from
    `world.pending_settlement_dialogues`.

    SC-5 reversal commit 1: produced offers live in
    `world.pending_settlement_dialogues` until the UI layer (commit 2)
    promotes them into `dialogue_manager`. Accept / reject must remove
    the entry so the one-active-offer-per-war guard re-opens for the
    next producer tick. Matches by `offer_id` when present (canonical);
    `war_id` fallback is reserved for stale-save entries that predate
    stable offer ids.
    """
    pending = getattr(world, "pending_settlement_dialogues", None)
    if not isinstance(pending, list):
        return None
    if offer_id:
        for index, entry in enumerate(pending):
            if not isinstance(entry, Mapping):
                continue
            if entry.get("type") != "incoming_settlement_offer":
                continue
            if str(entry.get("offer_id") or "") == offer_id:
                return pending.pop(index)
    if not offer_id and war_id:
        for index, entry in enumerate(pending):
            if not isinstance(entry, Mapping):
                continue
            if entry.get("type") != "incoming_settlement_offer":
                continue
            if str(entry.get("offer_id") or ""):
                continue
            if str(entry.get("war_id") or "") == war_id:
                return pending.pop(index)
    return None


def _is_offer_active_dialogue(world: Any, dialogue: Mapping[str, Any]) -> bool:
    """True when the supplied incoming-offer dialogue is also the active
    `dialogue_manager._current` slot. SC-5 reversal commit 1 keeps the
    UI layer dormant; the active-dialogue check stays so that commit 2's
    promotion step (which pushes offers into `dialogue_manager`) does
    not require a second handler rewrite.
    """
    dm = getattr(world, "dialogue_manager", None)
    if dm is None:
        return False
    current = getattr(dm, "_current", None)
    if not isinstance(current, Mapping):
        return False
    if str(current.get("type") or current.get("dialogue_type") or "") != "incoming_settlement_offer":
        return False
    if str(current.get("offer_id") or "") and str(current.get("offer_id") or "") == str(dialogue.get("offer_id") or ""):
        return True
    return str(current.get("war_id") or "") == str(dialogue.get("war_id") or "")


def _is_offer_known_to_dialogue_manager(
    world: Any, *, offer_id: str
) -> bool:
    """True when an incoming-offer dialogue with `offer_id` already lives
    in the active dialogue slot or the queue. Used by the promotion step
    so save-loaded saves never duplicate-push the same offer."""
    dm = getattr(world, "dialogue_manager", None)
    if dm is None or not offer_id:
        return False
    current = dm.peek() if hasattr(dm, "peek") else getattr(dm, "_current", None)
    if (
        isinstance(current, Mapping)
        and current.get("type") == "incoming_settlement_offer"
        and str(current.get("offer_id") or "") == offer_id
    ):
        return True
    queued = dm.iter_queue() if hasattr(dm, "iter_queue") else (getattr(dm, "_queue", None) or [])
    for queued_dialogue in queued:
        if (
            isinstance(queued_dialogue, Mapping)
            and queued_dialogue.get("type") == "incoming_settlement_offer"
            and str(queued_dialogue.get("offer_id") or "") == offer_id
        ):
            return True
    return False


def _are_treaty_allies(world: Any, nation_a: str, nation_b: str) -> bool:
    if not nation_a or not nation_b or nation_a == nation_b:
        return False
    if hasattr(world, "get_diplomatic_state"):
        state = str(world.get_diplomatic_state(nation_a, nation_b) or "")
    else:
        key = world._make_diplo_key(nation_a, nation_b)
        state = str((getattr(world, "diplomatic_states", {}) or {}).get(key) or "")
    return state in {"ALLIANCE", "DEFENSIVE_ALLIANCE"}


def _active_war_id_for_diplo_key(world: Any, diplo_key: str) -> str:
    for war_id, war in (getattr(world, "war_instances", {}) or {}).items():
        if not isinstance(war, Mapping) or war.get("ended_turn") is not None:
            continue
        if str(diplo_key or "") in set(war.get("active_diplo_keys") or []):
            return str(war_id)
    return ""


def _objective_has_material_claim(objective: Mapping[str, Any]) -> bool:
    obj_type = str(objective.get("type") or "")
    if obj_type == "defense":
        return False
    if objective.get("target_regions") or objective.get("vassal_nations"):
        return True
    return obj_type in {"conquest", "forced_alliance", "subjugation", "liberation"}


def _objective_claim_region(objective: Mapping[str, Any]) -> str:
    target_regions = list(objective.get("target_regions") or [])
    if target_regions:
        return str(target_regions[0])
    vassals = list(objective.get("vassal_nations") or [])
    if vassals:
        return str(vassals[0])
    target = str(objective.get("target_nation") or "")
    return target or "the claimed objective"


def _war_label_for_id(world: Any, war_id: str) -> str:
    war = (getattr(world, "war_instances", {}) or {}).get(str(war_id or ""))
    if isinstance(war, Mapping):
        return _war_label(str(war_id or ""), war)
    return str(war_id or "settlement")


def _active_objective_claims_for_ally(
    world: Any,
    ally_nation: str,
    *,
    target_enemy: str = "",
    required_war_id: str = "",
    excluded_war_id: str = "",
) -> List[Dict[str, Any]]:
    claims: List[Dict[str, Any]] = []
    objectives_by_pair = getattr(world, "war_objectives", {}) or {}
    if not isinstance(objectives_by_pair, Mapping):
        return claims
    for diplo_key, nation_objectives in objectives_by_pair.items():
        if not isinstance(nation_objectives, Mapping):
            continue
        objective = nation_objectives.get(ally_nation)
        if not isinstance(objective, Mapping):
            continue
        if objective.get("concluded_turn") is not None:
            continue
        if not _objective_has_material_claim(objective):
            continue
        claim_war_id = _active_war_id_for_diplo_key(world, str(diplo_key))
        if not claim_war_id:
            continue
        if required_war_id and claim_war_id != required_war_id:
            continue
        if excluded_war_id and claim_war_id == excluded_war_id:
            continue
        objective_target = str(objective.get("target_nation") or "")
        pair_nations = set(_pair_nations(str(diplo_key)))
        if target_enemy and target_enemy not in pair_nations:
            continue
        if target_enemy and objective_target and objective_target != target_enemy:
            continue
        target = objective_target or (
            target_enemy
            if target_enemy
            else next((n for n in pair_nations if n != ally_nation), "")
        )
        claims.append({
            "ally_nation": ally_nation,
            "claim_war_id": claim_war_id,
            "claim_war_label": _war_label_for_id(world, claim_war_id),
            "objective_type": str(objective.get("type") or ""),
            "target_enemy": target,
            "claim_region": _objective_claim_region(objective),
            "objective": dict(objective),
        })
    return claims


def _settlement_terms_satisfy_ally_claim(
    settlement_terms: Iterable[Mapping[str, Any]],
    claim: Mapping[str, Any],
) -> bool:
    ally = str(claim.get("ally_nation") or "")
    target_enemy = str(claim.get("target_enemy") or "")
    claim_region = str(claim.get("claim_region") or "")
    objective_type = str(claim.get("objective_type") or "")
    for term in settlement_terms or []:
        if not isinstance(term, Mapping):
            continue
        term_type = str(term.get("type") or "")
        to_nation = str(term.get("to") or term.get("lord_nation") or "")
        from_nation = str(term.get("from") or term.get("vassal_nation") or "")
        if term_type == "territory_cede" and to_nation == ally:
            regions = [
                str(region)
                for region in (
                    term.get("regions")
                    or ([term.get("region")] if term.get("region") else [])
                )
            ]
            if not claim_region or claim_region in regions:
                return True
        if (
            term_type == "forced_alliance"
            and objective_type == "forced_alliance"
            and to_nation == ally
            and (not target_enemy or from_nation == target_enemy)
        ):
            return True
        if (
            term_type in {"vassalage", "subjugation"}
            and objective_type == "subjugation"
            and to_nation == ally
            and (not target_enemy or from_nation == target_enemy)
        ):
            return True
        if term_type == "liberation" and objective_type == "liberation":
            liberated = str(term.get("vassal_nation") or term.get("from") or "")
            if liberated and liberated == claim_region:
                return True
    return False


def _find_request_open_settlement_petition_context(
    world: Any,
    *,
    war_id: str,
) -> Optional[Dict[str, Any]]:
    player = str(getattr(world, "player_nation", "France") or "France")
    war = (getattr(world, "war_instances", {}) or {}).get(str(war_id or ""))
    if not isinstance(war, Mapping) or war.get("ended_turn") is not None:
        return None
    participants = set(war.get("active_participants") or [])
    known_nations = set(getattr(world, "enemy_nations", []) or [])
    known_nations.add(player)
    for nation_objectives in (getattr(world, "war_objectives", {}) or {}).values():
        if isinstance(nation_objectives, Mapping):
            known_nations.update(str(nation) for nation in nation_objectives.keys())
    for ally in sorted(known_nations):
        if ally in participants or not _are_treaty_allies(world, player, ally):
            continue
        claims = _active_objective_claims_for_ally(
            world,
            ally,
            excluded_war_id=str(war_id or ""),
        )
        if claims:
            claim = claims[0]
            claim.update({
                "war_id": str(war_id or ""),
                "war_label": _war_label_for_id(world, str(war_id or "")),
            })
            return claim
    return None


def _find_warn_sellout_petition_context(
    world: Any,
    *,
    war_id: str,
    covered_enemy_participants: Iterable[str],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    player = str(getattr(world, "player_nation", "France") or "France")
    war = (getattr(world, "war_instances", {}) or {}).get(str(war_id or ""))
    if not isinstance(war, Mapping) or war.get("ended_turn") is not None:
        return None
    player_side = _side_for_nation(war, player)
    if player_side not in VALID_SIDES:
        return None
    same_side = [
        str(nation)
        for nation in (war.get(player_side) or [])
        if str(nation) and str(nation) != player
    ]
    for ally in sorted(same_side):
        if not _are_treaty_allies(world, player, ally):
            continue
        for enemy in covered_enemy_participants or []:
            claims = _active_objective_claims_for_ally(
                world,
                ally,
                target_enemy=str(enemy),
                required_war_id=str(war_id or ""),
            )
            for claim in claims:
                if _settlement_terms_satisfy_ally_claim(settlement_terms, claim):
                    continue
                claim.update({
                    "war_id": str(war_id or ""),
                    "war_label": _war_label_for_id(world, str(war_id or "")),
                })
                return claim
    return None


def _ally_petition_voice_family(petition_type: str, ally_nation: str) -> str:
    suffix = {
        "Britain": "castlereagh",
        "Prussia": "hardenberg",
        "Austria": "metternich",
        "Saxony": "einsiedel",
    }.get(str(ally_nation or ""), "chancery")
    return f"settlement_ally_petition_{petition_type}_{suffix}"


def _ally_petition_summary_text(petition: Mapping[str, Any]) -> str:
    ally = str(petition.get("ally_nation") or "An ally")
    ptype = str(petition.get("petition_type") or "")
    claim_region = str(petition.get("claim_region") or "a claim")
    target_enemy = str(petition.get("target_enemy") or "the enemy")
    if ptype == ALLY_SETTLEMENT_PETITION_REQUEST_OPEN:
        return f"{ally} asks to be heard before {claim_region} is left outside peace."
    if ptype == ALLY_SETTLEMENT_PETITION_WARN_SELLOUT:
        return f"{ally} warns that {claim_region} against {target_enemy} is omitted."
    return f"{ally} petitions over settlement scope."


def build_ally_settlement_petition_dialogue(
    world: Any,
    *,
    petition_type: str,
    context: Mapping[str, Any],
    trigger_action: str,
) -> Dict[str, Any]:
    war_id = str(context.get("war_id") or "")
    ally_nation = str(context.get("ally_nation") or "")
    claim_war_id = str(context.get("claim_war_id") or "")
    target_enemy = str(context.get("target_enemy") or "")
    claim_region = str(context.get("claim_region") or "the claimed objective")
    petition_key = (
        f"ally_petition:{petition_type}:{war_id}:{ally_nation}:"
        f"{claim_war_id}:{target_enemy}:{claim_region}"
    )
    voice_slots = {
        "ally_nation": ally_nation or "the ally",
        "war_label": str(context.get("war_label") or _war_label_for_id(world, war_id)),
        "claim_war_label": str(
            context.get("claim_war_label") or _war_label_for_id(world, claim_war_id)
        ),
        "target_enemy": target_enemy or "the enemy",
        "claim_region": claim_region,
    }
    ally_voice = resolve_settlement_voice_line(
        _ally_petition_voice_family(petition_type, ally_nation),
        **voice_slots,
    )
    if not ally_voice:
        ally_voice = resolve_settlement_voice_line(
            f"settlement_ally_petition_{petition_type}_chancery",
            **voice_slots,
        )
    talleyrand_text = resolve_settlement_voice_line(
        "settlement_ally_petition_talleyrand",
        **voice_slots,
    )
    options = [{
        "label": "Acknowledge",
        "description": "Record the allied petition without changing the settlement draft.",
        "action": ALLY_SETTLEMENT_PETITION_ACK_ACTION,
        "available": True,
    }]
    dialogue: Dict[str, Any] = {
        "type": ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE,
        "dialogue_type": ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE,
        "petition_type": str(petition_type or ""),
        "petition_id": petition_key,
        "petition_key": petition_key,
        "trigger_action": str(trigger_action or ""),
        "blocking": False,
        "war_id": war_id,
        "war_label": voice_slots["war_label"],
        "claim_war_id": claim_war_id,
        "claim_war_label": voice_slots["claim_war_label"],
        "claim_region": claim_region,
        "target_enemy": target_enemy,
        "ally_nation": ally_nation,
        "objective_type": str(context.get("objective_type") or ""),
        "turn_created": int(getattr(world, "current_turn", 0) or 0),
        "ally_voice": ally_voice or "",
        "talleyrand_text": talleyrand_text or "",
        "summary_text": "",
        "options": options,
        "available_action_ids": [ALLY_SETTLEMENT_PETITION_ACK_ACTION],
    }
    dialogue["summary_text"] = _ally_petition_summary_text(dialogue)
    dialogue["popup_payload"] = build_ally_settlement_petition_popup(dialogue)
    return dialogue


def build_ally_settlement_petition_popup(
    dialogue: Mapping[str, Any],
) -> Dict[str, Any]:
    options = [
        dict(opt)
        for opt in (dialogue.get("options") or [])
        if isinstance(opt, Mapping)
    ]
    if not options:
        options = [{
            "label": "Acknowledge",
            "description": "Record the allied petition without changing the draft.",
            "action": ALLY_SETTLEMENT_PETITION_ACK_ACTION,
            "available": True,
        }]
    return {
        "type": ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE,
        "dialogue_type": ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE,
        "petition_type": str(dialogue.get("petition_type") or ""),
        "petition_id": str(dialogue.get("petition_id") or ""),
        "petition_key": str(dialogue.get("petition_key") or ""),
        "war_id": str(dialogue.get("war_id") or ""),
        "war_label": str(dialogue.get("war_label") or "settlement"),
        "claim_war_id": str(dialogue.get("claim_war_id") or ""),
        "claim_war_label": str(dialogue.get("claim_war_label") or ""),
        "claim_region": str(dialogue.get("claim_region") or ""),
        "target_enemy": str(dialogue.get("target_enemy") or ""),
        "ally_nation": str(dialogue.get("ally_nation") or ""),
        "objective_type": str(dialogue.get("objective_type") or ""),
        "trigger_action": str(dialogue.get("trigger_action") or ""),
        "blocking": False,
        "ally_voice": str(dialogue.get("ally_voice") or ""),
        "talleyrand_text": str(dialogue.get("talleyrand_text") or ""),
        "summary_text": str(dialogue.get("summary_text") or ""),
        "options": options,
        "available_action_ids": [str(opt.get("action") or "") for opt in options],
    }


def _is_ally_petition_known_to_dialogue_manager(
    world: Any,
    *,
    petition_key: str,
) -> bool:
    if not petition_key:
        return False
    dm = getattr(world, "dialogue_manager", None)
    if dm is not None:
        current = dm.peek() if hasattr(dm, "peek") else getattr(dm, "_current", None)
        if (
            isinstance(current, Mapping)
            and current.get("type") == ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE
            and str(current.get("petition_key") or "") == petition_key
        ):
            return True
        queued = (
            dm.iter_queue()
            if hasattr(dm, "iter_queue")
            else (getattr(dm, "_queue", None) or [])
        )
        for queued_dialogue in queued:
            if (
                isinstance(queued_dialogue, Mapping)
                and queued_dialogue.get("type") == ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE
                and str(queued_dialogue.get("petition_key") or "") == petition_key
            ):
                return True
    for entry in getattr(world, "pending_settlement_dialogues", []) or []:
        if (
            isinstance(entry, Mapping)
            and entry.get("type") == ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE
            and str(entry.get("petition_key") or "") == petition_key
        ):
            return True
    return False


def _emit_ally_settlement_petition_notification(
    world: Any,
    petition: Mapping[str, Any],
) -> None:
    notifications = getattr(world, "notifications", None)
    if notifications is None or not hasattr(notifications, "add"):
        return
    from backend.notifications import (
        ALLY_SETTLEMENT_PETITION,
        NotificationPriority,
        create_notification,
    )

    ally = str(petition.get("ally_nation") or "Ally")
    notifications.add(create_notification(
        ALLY_SETTLEMENT_PETITION,
        NotificationPriority.HIGH,
        f"{ally} petitions over settlement scope",
        str(petition.get("summary_text") or ""),
        int(getattr(world, "current_turn", 0) or 0),
        details={
            "review_target": "ally_settlement_petition_popup",
            "review_label": "Open Envoys",
            "war_id": str(petition.get("war_id") or ""),
            "petition_id": str(petition.get("petition_id") or ""),
            "petition_type": str(petition.get("petition_type") or ""),
            "ally_nation": ally,
        },
    ))


def _queue_ally_settlement_petition(
    world: Any,
    *,
    petition_type: str,
    context: Optional[Mapping[str, Any]],
    trigger_action: str,
) -> Optional[Dict[str, Any]]:
    if petition_type not in ALLY_SETTLEMENT_PETITION_SHIPPED_TYPES:
        return None
    if trigger_action not in ALLY_SETTLEMENT_PETITION_SOLICITED_TRIGGERS:
        return None
    if not isinstance(context, Mapping):
        return None
    dialogue = build_ally_settlement_petition_dialogue(
        world,
        petition_type=petition_type,
        context=context,
        trigger_action=trigger_action,
    )
    petition_key = str(dialogue.get("petition_key") or "")
    if _is_ally_petition_known_to_dialogue_manager(
        world,
        petition_key=petition_key,
    ):
        return None
    dm = getattr(world, "dialogue_manager", None)
    if dm is None or not hasattr(dm, "push"):
        return None
    dm.push(dialogue)
    _emit_ally_settlement_petition_notification(world, dialogue)
    return dialogue


def queue_ally_settlement_petitions_for_player_action(
    world: Any,
    *,
    trigger_action: str,
    war_id: str,
    covered_enemy_participants: Optional[Iterable[str]] = None,
    settlement_terms: Optional[Iterable[Mapping[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    if trigger_action not in ALLY_SETTLEMENT_PETITION_SOLICITED_TRIGGERS:
        return []
    if trigger_action == "open_settlement":
        context = _find_request_open_settlement_petition_context(
            world,
            war_id=str(war_id or ""),
        )
        petition = _queue_ally_settlement_petition(
            world,
            petition_type=ALLY_SETTLEMENT_PETITION_REQUEST_OPEN,
            context=context,
            trigger_action=trigger_action,
        )
        return [petition] if petition is not None else []
    if trigger_action in {"stage_settlement", "reject_settlement_offer"}:
        context = _find_warn_sellout_petition_context(
            world,
            war_id=str(war_id or ""),
            covered_enemy_participants=covered_enemy_participants or [],
            settlement_terms=settlement_terms or [],
        )
        petition = _queue_ally_settlement_petition(
            world,
            petition_type=ALLY_SETTLEMENT_PETITION_WARN_SELLOUT,
            context=context,
            trigger_action=trigger_action,
        )
        return [petition] if petition is not None else []
    return []


def handle_ally_settlement_petition_action(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
) -> Dict[str, Any]:
    if action != ALLY_SETTLEMENT_PETITION_ACK_ACTION:
        return {
            "success": False,
            "message": f"Unknown ally petition action: {action}",
        }
    petition_key = str(dialogue.get("petition_key") or "")
    dm = getattr(world, "dialogue_manager", None)
    removed = 0
    if dm is not None and hasattr(dm, "remove_matching"):
        removed = dm.remove_matching(
            lambda item: (
                isinstance(item, Mapping)
                and item.get("type") == ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE
                and (
                    not petition_key
                    or str(item.get("petition_key") or "") == petition_key
                )
            )
        )
    return {
        "success": True,
        "message": "The allied petition has been recorded.",
        "mutated": False,
        "removed_dialogues": int(removed),
        "pending_envoy_count": int(
            dm.get_mailbox_count()
            if dm is not None and hasattr(dm, "get_mailbox_count")
            else 0
        ),
        "suppress_proposal_result_popup": True,
    }


def _incoming_offer_summary_text(offer: Mapping[str, Any]) -> str:
    """One-line dispatch / mailbox summary for an incoming settlement offer."""
    proposer = str(offer.get("proposer_nation") or "Unknown")
    war_id = str(offer.get("war_id") or "")
    amount = 0
    for term in offer.get("settlement_terms") or []:
        if isinstance(term, Mapping) and term.get("type") == "gold_indemnity":
            try:
                amount = int(term.get("amount") or 0)
            except (TypeError, ValueError):
                amount = 0
            break
    parts = [f"Settlement offer from {proposer}"]
    if war_id:
        parts.append(f"({war_id})")
    if amount:
        parts.append(f"— {amount} gold for peace")
    return " ".join(parts)


def build_incoming_settlement_offer_popup(
    world: Any, offer: Mapping[str, Any]
) -> Dict[str, Any]:
    """Return a popup-safe payload for an incoming settlement offer.

    The payload uses the `proposal_confirm` popup schema (label,
    description, action per option) so Godot's existing dialogue popup
    can render the offer alongside ordinary diplomatic confirms; the
    `incoming_settlement_offer` arm in `proposal_confirm_popup.gd`
    knows how to format the offered settlement_terms and Voice Bible
    incoming-offer copy. The package is read-only; click handlers route
    back through `/respond_to_diplomatic_dialogue` so backend
    revalidation runs before any mutation.
    """
    war_id = str(offer.get("war_id") or "")
    offer_id = str(offer.get("offer_id") or "")
    proposer_nation = str(offer.get("proposer_nation") or "")
    accepting_side = str(offer.get("accepting_side") or "")
    covered = list(offer.get("covered_enemy_participants") or [])
    settlement_terms = [
        dict(t) for t in offer.get("settlement_terms") or []
        if isinstance(t, Mapping)
    ]
    war_instances = getattr(world, "war_instances", None) or {}
    war = war_instances.get(war_id) if isinstance(war_instances, Mapping) else None
    if isinstance(war, Mapping):
        war_label = _war_label(war_id, war) if war_id else "settlement"
    else:
        war_label = war_id or "settlement"

    amount = 0
    for term in settlement_terms:
        if term.get("type") == "gold_indemnity":
            try:
                amount = int(term.get("amount") or 0)
            except (TypeError, ValueError):
                amount = 0
            break

    # Voice routing per Voice Bible §16.1 incoming-offer families. Named
    # diplomats use their own register; non-cast courts fall back to the
    # chancery variant.
    diplomat_family = {
        "Britain": "settlement_incoming_offer_arrival_castlereagh",
        "Prussia": "settlement_incoming_offer_arrival_hardenberg",
        "Austria": "settlement_incoming_offer_arrival_metternich",
        "Saxony": "settlement_incoming_offer_arrival_einsiedel",
    }
    proposer_family = diplomat_family.get(
        proposer_nation,
        "settlement_incoming_offer_arrival_chancery",
    )
    proposer_voice = resolve_settlement_voice_line(
        proposer_family,
        war_label=war_label,
        proposer_leader=proposer_nation or "their leader",
        amount=str(amount or 0),
    )
    talleyrand_voice = resolve_settlement_voice_line(
        "settlement_incoming_offer_arrival_talleyrand",
        war_label=war_label,
        proposer_leader=proposer_nation or "their leader",
        amount=str(amount or 0),
    )

    # May 24, 2026 audit punch list Tier 3 P2: every non-gold clause is
    # rendered with structured copy so a region cession, forced alliance,
    # vassalage, subjugation, liberation, or recurring-gold offer cannot
    # show up in the popup as a bare title-cased token. Gold indemnity
    # keeps its existing amount-leading form because the popup leads with
    # the offered gold value; everything else delegates to the canonical
    # `_term_display(...)` helper used by the settlement review + applied
    # clauses preview, so the incoming-offer popup and the editor agree
    # on what a clause reads as.
    terms_summary: List[str] = []
    for term in settlement_terms:
        ttype = str(term.get("type") or "")
        if not ttype:
            continue
        if ttype == "peace":
            terms_summary.append("Peace")
            continue
        if ttype == "gold_indemnity":
            terms_summary.append(
                f"{term.get('amount', 0)} gold ({term.get('from', '')} → {term.get('to', '')})"
            )
            continue
        if ttype == "gold_per_turn":
            amount = int(term.get("amount", 0) or 0)
            turns = int(term.get("turns", 0) or 0)
            terms_summary.append(
                f"{amount} gold/turn for {turns} turns "
                f"({term.get('from', '')} → {term.get('to', '')})"
            )
            continue
        if ttype == "forced_alliance":
            cs_suffix = (
                ", incl. Continental System"
                if bool(term.get("includes_continental_system"))
                else ""
            )
            terms_summary.append(
                f"Forced alliance ({term.get('from', '')} → {term.get('to', '')}"
                f"{cs_suffix})"
            )
            continue
        terms_summary.append(_term_display(term))

    # SC-5R-2: action labels must match behavior. `accept_settlement_offer`
    # stages a fresh `settlement_confirm` review (not an immediate
    # ratification); the player still has to ratify on the next popup.
    # Calling the button "Accept Settlement" with description "Ratify the
    # offered package" overclaimed the action. The label / description are
    # rewritten to read as "open this offer for review", which is what the
    # backend handler actually does.
    options = [
        {
            "label": "Review Settlement Offer",
            "description": (
                "Open the offered terms for ratification review. "
                "Ratification still requires a final confirm."
            ),
            "action": "accept_settlement_offer",
            "available": True,
        },
        {
            "label": "Request Revision",
            "description": (
                "Open the offered terms in the editor and answer with a counter draft."
            ),
            "action": "request_settlement_revision",
            "available": True,
        },
        {
            "label": "Reject Offer",
            "description": "Decline the offer without further negotiation.",
            "action": "reject_settlement_offer",
            "available": True,
        },
    ]

    return {
        "type": "incoming_settlement_offer",
        "dialogue_type": "incoming_settlement_offer",
        "offer_id": offer_id,
        "war_id": war_id,
        "war_label": war_label,
        "proposer_nation": proposer_nation,
        "accepting_side": accepting_side,
        "covered_enemy_participants": list(covered),
        "settlement_terms": settlement_terms,
        "terms_summary": terms_summary,
        "amount": int(amount),
        "talleyrand_text": talleyrand_voice or "",
        "proposer_voice": proposer_voice or "",
        "options": options,
        "available_action_ids": [opt["action"] for opt in options],
    }


def promote_pending_settlement_offers(world: Any) -> List[Dict[str, Any]]:
    """Drain `world.pending_settlement_dialogues` of `incoming_settlement_offer`
    entries and push them into the dialogue_manager mailbox queue.

    SC-5 reversal commit 2 / SC-30 Slice G1: the AI producer writes
    offers into `world.pending_settlement_dialogues`; this helper is
    the one place that promotes them onto the mailbox so the
    Godot popup and `/pending_envoy` / `/mailbox` paths see them. The
    helper is idempotent: an offer whose `offer_id` already lives in
    the dialogue manager is skipped and pruned from pending storage so
    save/load and multi-call paths do not duplicate-push or preserve
    stale copies. Returns the list of newly promoted dialogues for
    logging / notification routing.
    """
    pending = getattr(world, "pending_settlement_dialogues", None)
    if not isinstance(pending, list) or not pending:
        return []
    dm = getattr(world, "dialogue_manager", None)
    if dm is None:
        return []
    promoted: List[Dict[str, Any]] = []
    remaining: List[Dict[str, Any]] = []
    pruned_offer = False
    for entry in pending:
        if not isinstance(entry, dict):
            remaining.append(entry)
            continue
        if entry.get("type") != "incoming_settlement_offer":
            remaining.append(entry)
            continue
        offer_id = str(entry.get("offer_id") or "")
        if _is_offer_known_to_dialogue_manager(world, offer_id=offer_id):
            # Already promoted (e.g. by an earlier promote call on the
            # same response cycle). Drop from pending so the storage
            # does not grow.
            pruned_offer = True
            continue
        # Build the mailbox-ready dialogue. The offer dict already has
        # all the contract fields plus `turn_created`; we copy them
        # forward verbatim so save/load round-trips through dialogue
        # manager identically.
        dialogue = copy.deepcopy(entry)
        dialogue.setdefault("type", "incoming_settlement_offer")
        dialogue.setdefault("dialogue_type", "incoming_settlement_offer")
        dialogue.setdefault("blocking", False)
        # Attach the popup payload so the mailbox-activate endpoint can
        # return it without rebuilding from scratch. The popup payload
        # is regenerated through `build_incoming_settlement_offer_popup`
        # on demand for save-loaded dialogues.
        dialogue["popup_payload"] = build_incoming_settlement_offer_popup(
            world, entry
        )
        dm.push(dialogue)
        promoted.append(dialogue)
        pruned_offer = True
    if pruned_offer:
        world.pending_settlement_dialogues = remaining
    return promoted


def handle_incoming_settlement_offer_action(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
) -> Dict[str, Any]:
    """Handle player responses to AI-produced incoming settlement offers.

    SC-5 reversal (May 15, 2026 / Slice G1 commit 1):

    - Producer (`ai_diplomacy.process_settlement_offer_phase`) creates the
      offer entry in `world.pending_settlement_dialogues` with the canonical
      shape `{type, dialogue_type, offer_id, war_id, proposer_nation,
      proposer_side, accepting_side, covered_enemy_participants,
      settlement_terms, turn_created, ...}`.
    - This handler removes the matching entry on accept / reject, and on
      accept calls `stage_settlement_confirm(...)` forwarding the offered
      `settlement_terms`, `covered_enemy_participants`, and a
      `selected_target_nation` derived from the covered scope. It
      deliberately does not forward the offer's `proposer_side`: the
      player is accepting the package, so the staged review infers the
      proposer side from `actor_nation=player`. The staged review
      therefore preserves the exact offered package through live
      re-preview, per the spec §G2-Slice-4 package-preservation
      requirement.
    - `dialogue_manager.pop()` is only invoked when the offer is also the
      active dialogue slot (i.e. promoted by commit 2). Backend-only
      callers — including commit 1's tests — pass the offer dialogue dict
      directly and the manager slot stays untouched.
    - `request_settlement_revision` is acknowledged with a counter / edit
      hint that points back into the same war's editor route. The real
      counter / edit wiring lands with the UI layer (commit 2); for now
      we explicitly do NOT mutate state.
    - The stale-save defensive flag `INCOMING_OFFERS_DEFERRED` stays as a
      named constant and is checked here as a safety belt: if a future
      session ever flips it back to True (e.g. emergency disable), the
      handler returns the legacy short-circuit without touching state.
    """
    war_id = str(dialogue.get("war_id") or "")
    offer_id = str(dialogue.get("offer_id") or "")
    if INCOMING_OFFERS_DEFERRED:
        return {
            "success": False,
            "dialogue_type": "incoming_settlement_offer",
            "action": action,
            "war_id": war_id,
            "offer_id": offer_id,
            "error": "incoming_offer_deferred",
            "error_display": _error_display("incoming_offer_deferred"),
            "must_reopen": False,
            "mutated": False,
            "suppress_proposal_result_popup": True,
        }

    actor = getattr(world, "player_nation", "France")

    if action == "reject_settlement_offer":
        offered_terms = [
            dict(term)
            for term in (dialogue.get("settlement_terms") or [])
            if isinstance(term, Mapping)
        ]
        covered_enemies = list(dialogue.get("covered_enemy_participants") or [])
        _remove_pending_settlement_offer(world, offer_id=offer_id, war_id=war_id)
        if _is_offer_active_dialogue(world, dialogue):
            world.dialogue_manager.pop()
        ally_petitions = queue_ally_settlement_petitions_for_player_action(
            world,
            trigger_action="reject_settlement_offer",
            war_id=war_id,
            covered_enemy_participants=covered_enemies,
            settlement_terms=offered_terms,
        )
        return {
            "success": True,
            "dialogue_type": "incoming_settlement_offer",
            "action": "reject_settlement_offer",
            "war_id": war_id,
            "offer_id": offer_id,
            "ally_settlement_petitions": [
                copy.deepcopy(petition) for petition in ally_petitions
            ],
            "mutated": False,
            "message": "Settlement offer rejected.",
            "suppress_proposal_result_popup": True,
        }

    if action == "request_settlement_revision":
        # SC-5 reversal commit 2 + GT-Slice-4 (OQ-4(b)): counter-authoring
        # lands on the guided PROPOSE surface seeded with the exact offered
        # terms. The player reshapes the package on the per-court rows and
        # submits as a counter, or backs out without sending one. The
        # original offer entry is removed because the player has explicitly
        # chosen to counter (rather than leaving the offer open in the
        # mailbox alongside a counter draft). Click-time revalidation
        # still runs through `stage_settlement_confirm`, so a
        # state-changed war returns a humanized error instead of
        # opening a stale counter surface.
        offered_terms = list(dialogue.get("settlement_terms") or [])
        covered_enemies = list(dialogue.get("covered_enemy_participants") or [])
        offer_proposer_nation = dialogue.get("proposer_nation")
        selected_target = (
            dialogue.get("selected_target_nation")
            or (
                offer_proposer_nation
                if offer_proposer_nation and offer_proposer_nation in covered_enemies
                else (covered_enemies[0] if covered_enemies else None)
            )
        )

        # SC-7b: empty / invalid / archived war_id surface humanized
        # copy and DO NOT open the editor. The offer entry is still
        # removed defensively so the mailbox does not keep referencing
        # an offer that points nowhere.
        defensive_fail: Optional[Dict[str, Any]] = None
        if not war_id:
            defensive_fail = {
                "error": "invalid_war_id",
                "error_display": _error_display("invalid_war_id"),
            }
        elif not is_war_known(world, war_id):
            defensive_fail = {
                "error": "incoming_offer_war_invalid",
                "error_display": _error_display("incoming_offer_war_invalid"),
            }
        elif is_war_archived(world, war_id):
            defensive_fail = {
                "error": "incoming_offer_war_archived",
                "error_display": _error_display("incoming_offer_war_archived"),
                "war_archived": True,
            }
        if defensive_fail is not None:
            _remove_pending_settlement_offer(world, offer_id=offer_id, war_id=war_id)
            if _is_offer_active_dialogue(world, dialogue):
                world.dialogue_manager.pop()
            result = {
                "success": False,
                "dialogue_type": "incoming_settlement_offer",
                "action": "request_settlement_revision",
                "war_id": war_id,
                "offer_id": offer_id,
                "mutated": False,
                "must_reopen": False,
                **defensive_fail,
            }
            if defensive_fail["error"] == "invalid_war_id":
                result.update(
                    _no_reopen_target_payload(
                        war_id, error="no_reopen_target_available"
                    )
                )
                result["error"] = "invalid_war_id"
                result["error_display"] = _error_display("invalid_war_id")
            else:
                result["reopen_target"] = {
                    "surface": "war_detail",
                    "target": "war_detail",
                    "war_id": war_id,
                    "nation": "",
                    "target_nation": "",
                }
            return result

        # Remove the offer first so the mailbox no longer renders it and
        # the one-active-offer-per-war producer guard re-opens for the
        # next AI tick. Editor state lives in
        # `world.pending_settlement_drafts[war_id]` from `stage_settlement_confirm`.
        _remove_pending_settlement_offer(world, offer_id=offer_id, war_id=war_id)
        if _is_offer_active_dialogue(world, dialogue):
            world.dialogue_manager.pop()

        stage_kwargs: Dict[str, Any] = {
            "war_id": war_id,
            "actor_nation": actor,
            "density": "medium",
            # Player caller kind so the authoring controls (per-court
            # demand rows, dials, Submit for Review, Back Out) appear the
            # way they do for the standard player-authored settlement.
            # The offered terms become the initial draft, and PROPOSE is
            # the landing surface (GT-Slice-4: guided counter-authoring,
            # no editor mount).
            "caller_kind": "player_editor",
            "dialogue_mode": "PROPOSE",
        }
        if offered_terms:
            stage_kwargs["settlement_terms"] = offered_terms
        if covered_enemies:
            stage_kwargs["covered_enemy_participants"] = covered_enemies
        if selected_target:
            stage_kwargs["selected_target_nation"] = selected_target

        result = stage_settlement_confirm(world, **stage_kwargs)
        result["dialogue_type"] = "settlement_confirm"
        result["action"] = "request_settlement_revision"
        result["offer_id"] = offer_id
        # Echo the originating offer terms so audits / observers can
        # confirm the counter surface was seeded from the exact offered
        # package. The staged draft itself can drift as the player
        # edits, but `counter_to_offer_id` + `counter_seed_terms` pin
        # the conversation provenance for the SC-30 voice-routing tests.
        result["counter_to_offer_id"] = offer_id
        result["counter_seed_terms"] = offered_terms
        result["counter_seed_covered_participants"] = covered_enemies
        # Override the staged settlement_confirm `talleyrand_text` with
        # the request-revision voice family so the editor heading reads
        # as "answering with a counter draft", not "Will they accept?".
        revision_voice = resolve_settlement_voice_line(
            "settlement_incoming_offer_request_revision_talleyrand",
            war_label=str(war_id),
            proposer_leader=str(offer_proposer_nation or "their leader"),
        )
        if revision_voice:
            result["talleyrand_text"] = revision_voice
            # Echo into the staged dialogue payload so the popup banner
            # picks up the request-revision framing even after future
            # re-renders. `diplomatic_dialogue` is the canonical key
            # `stage_settlement_confirm` returns.
            staged = result.get("diplomatic_dialogue")
            if isinstance(staged, dict):
                staged["talleyrand_text"] = revision_voice
            result["message"] = revision_voice
        if not result.get("success"):
            result["error_display"] = result.get("error_display") or _error_display(
                str(result.get("error") or "invalid_war_id")
            )
            result.update(_safe_reopen_response(world, war_id=war_id, dialogue=dialogue))
        return result

    if action != "accept_settlement_offer":
        return {
            "success": False,
            "dialogue_type": "incoming_settlement_offer",
            "action": action,
            "error": "unknown_settlement_offer_action",
            "mutated": False,
        }

    # SC-7b: empty / invalid / archived war_id all surface humanized
    # copy and DO NOT promote to `settlement_confirm`. The matching
    # offer entry is still removed (defensive cleanup), but no
    # `stage_settlement_confirm` call is made.
    if not war_id:
        _remove_pending_settlement_offer(world, offer_id=offer_id, war_id=war_id)
        if _is_offer_active_dialogue(world, dialogue):
            world.dialogue_manager.pop()
        result = {
            "success": False,
            "dialogue_type": "incoming_settlement_offer",
            "action": "accept_settlement_offer",
            "war_id": war_id,
            "offer_id": offer_id,
            "error": "invalid_war_id",
            "error_display": _error_display("invalid_war_id"),
            "mutated": False,
        }
        result.update(_no_reopen_target_payload(war_id, error="no_reopen_target_available"))
        result["error"] = "invalid_war_id"
        result["error_display"] = _error_display("invalid_war_id")
        return result
    if not is_war_known(world, war_id):
        _remove_pending_settlement_offer(world, offer_id=offer_id, war_id=war_id)
        if _is_offer_active_dialogue(world, dialogue):
            world.dialogue_manager.pop()
        return {
            "success": False,
            "dialogue_type": "incoming_settlement_offer",
            "action": "accept_settlement_offer",
            "war_id": war_id,
            "offer_id": offer_id,
            "error": "incoming_offer_war_invalid",
            "error_display": _error_display("incoming_offer_war_invalid"),
            "must_reopen": False,
            "reopen_target": {
                "surface": "war_detail",
                "target": "war_detail",
                "war_id": war_id,
                "nation": "",
                "target_nation": "",
            },
            "mutated": False,
        }
    if is_war_archived(world, war_id):
        _remove_pending_settlement_offer(world, offer_id=offer_id, war_id=war_id)
        if _is_offer_active_dialogue(world, dialogue):
            world.dialogue_manager.pop()
        return {
            "success": False,
            "dialogue_type": "incoming_settlement_offer",
            "action": "accept_settlement_offer",
            "war_id": war_id,
            "offer_id": offer_id,
            "error": "incoming_offer_war_archived",
            "error_display": _error_display("incoming_offer_war_archived"),
            "must_reopen": False,
            "reopen_target": {
                "surface": "war_detail",
                "target": "war_detail",
                "war_id": war_id,
                "nation": "",
                "target_nation": "",
            },
            "war_archived": True,
            "mutated": False,
        }

    # Package preservation: forward the offered settlement_terms,
    # covered_enemy_participants, and a deterministic
    # selected_target_nation (the original offering leader if it is
    # one of the covered enemies, else the first covered enemy).
    #
    # `proposer_side` on the offer dict names the side that *authored*
    # the offer (the AI side leader). We do NOT forward that field into
    # `stage_settlement_confirm`: when the player accepts, the staged
    # `settlement_confirm` is the player's ratification request, so the
    # proposer side is inferred from `actor_nation=player` instead.
    # Forwarding the AI side here would fail `not_side_leader` because
    # the player is the leader of the OPPOSITE side.
    offered_terms = list(dialogue.get("settlement_terms") or [])
    covered_enemies = list(dialogue.get("covered_enemy_participants") or [])
    offer_proposer_nation = dialogue.get("proposer_nation")
    selected_target = (
        dialogue.get("selected_target_nation")
        or (
            offer_proposer_nation
            if offer_proposer_nation and offer_proposer_nation in covered_enemies
            else (covered_enemies[0] if covered_enemies else None)
        )
    )

    _remove_pending_settlement_offer(world, offer_id=offer_id, war_id=war_id)
    if _is_offer_active_dialogue(world, dialogue):
        world.dialogue_manager.pop()

    stage_kwargs: Dict[str, Any] = {
        "war_id": war_id,
        "actor_nation": actor,
        "density": "medium",
        # Accepting an AI-authored offer is not an outgoing player-editor
        # draft. Keep the staged review ratifiable, but do not advertise
        # the outgoing `Revise Terms` editor route from SC-5R.
        "caller_kind": "ai_system",
    }
    if offered_terms:
        stage_kwargs["settlement_terms"] = offered_terms
    if covered_enemies:
        stage_kwargs["covered_enemy_participants"] = covered_enemies
    if selected_target:
        stage_kwargs["selected_target_nation"] = selected_target

    result = stage_settlement_confirm(world, **stage_kwargs)
    result["dialogue_type"] = "settlement_confirm"
    result["action"] = "accept_settlement_offer"
    # Echo the originating offer identity so downstream surfaces (and
    # commit 2's mailbox / Voice Bible wiring) can keep the offer
    # context attached to the promoted review.
    result["offer_id"] = offer_id
    result["accepted_offer_terms"] = offered_terms
    if not result.get("success"):
        # Build a SC-13-safe reopen payload using the staged dialogue's
        # selected target / covered participants if present (degrades to
        # choose-from-war-detail when both are missing).
        result["error_display"] = result.get("error_display") or _error_display(str(result.get("error") or "invalid_war_id"))
        result.update(_safe_reopen_response(world, war_id=war_id, dialogue=dialogue))
    return result


# ---------------------------------------------------------------------------
# SC-33 / G2-Slice-9 - Per-turn recurring gold payment processor.
# Wired from `WorldState.advance_turn` near `_process_treaty_clauses` /
# `process_vassal_tribute` so it runs after income/trade and before the
# bankruptcy check. The helper iterates only
# `world.recurring_settlement_payments` (no per-region scan) per golden
# rule 8.
# ---------------------------------------------------------------------------


def _is_renewed_war_between(world: Any, payer: str, recipient: str) -> bool:
    """True when payer / recipient are currently on opposite sides of an
    active war or armistice. Used as a recurring-payment cancellation
    condition (renewed war between the pair voids the obligation).
    """
    is_at_war = getattr(world, "is_at_war", None)
    if callable(is_at_war):
        try:
            if bool(is_at_war(payer, recipient)):
                return True
        except Exception:
            pass
    diplomatic_states = getattr(world, "diplomatic_states", None) or {}
    make_key = getattr(world, "_make_diplo_key", None)
    if callable(make_key):
        try:
            key = make_key(payer, recipient)
        except Exception:
            key = "|".join(sorted([payer, recipient]))
    else:
        key = "|".join(sorted([payer, recipient]))
    state = diplomatic_states.get(key)
    return str(state or "") in ("WAR", "ARMISTICE")


def _is_recurring_payment_nation_eliminated(
    world: Any,
    nation: str,
    *,
    nation_gold: Mapping[str, Any],
    vassals: Mapping[str, Any],
    active_nations: Optional[Set[str]],
) -> bool:
    """Match the live active-nation contract for payment cancellation.

    `nation_gold` persists for eliminated courts, so treasury membership is
    only a legacy fallback. Cached active-nation state is authoritative when
    the world exposes it.
    """
    if not nation:
        return True
    if nation in vassals:
        return False
    if nation not in nation_gold:
        return True
    if active_nations is not None:
        return nation not in active_nations
    # Do not fall back to a region scan from the per-payment loop. Production
    # WorldState exposes cached get_active_nations(); lightweight fakes still
    # get the legacy nation_gold absence behavior above.
    return False


def process_recurring_settlement_payments(world: Any) -> Dict[str, Any]:
    """SC-33 / G2-Slice-9 income-phase processor for recurring settlement
    gold payments.

    Cancellation conditions (per implementation directive May 14, 2026):

    - Payer eliminated (no longer in `world.nation_gold` or no regions).
    - Recipient eliminated.
    - Payer vassalized (now lives in `world.vassals`).
    - Renewed war between payer and recipient (active WAR/ARMISTICE pair).

    Non-cancellation runtime behavior:

    - Payer cannot afford full payment: transfer `min(amount, balance)`,
      never go negative, emit a `settlement_recurring_gold_partial`
      dispatch event, decrement `turns_remaining`, and keep the
      obligation alive until natural completion.
    - Natural completion: when `turns_remaining` reaches zero after a
      tick, emit `settlement_recurring_gold_completed` and remove the
      record.

    Returns an event summary `{paid, partial, completed, cancelled}`.
    """
    payments = getattr(world, "recurring_settlement_payments", None) or []
    if not payments:
        return {"paid": [], "partial": [], "completed": [], "cancelled": []}

    survivors: List[Dict[str, Any]] = []
    events = {"paid": [], "partial": [], "completed": [], "cancelled": []}
    nation_gold = getattr(world, "nation_gold", None) or {}
    vassals = getattr(world, "vassals", None) or {}
    active_nations: Optional[Set[str]] = None
    get_active_nations = getattr(world, "get_active_nations", None)
    if callable(get_active_nations):
        try:
            active_nations = {str(n) for n in get_active_nations()}
        except Exception:
            active_nations = None

    def _war_label_for(entry: Mapping[str, Any]) -> str:
        wid = str(entry.get("war_id") or "")
        if not wid:
            return "the settlement"
        instance = (getattr(world, "war_instances", {}) or {}).get(wid) or {}
        attackers = list(instance.get("attackers") or [])
        defenders = list(instance.get("defenders") or [])
        if attackers and defenders:
            return f"{attackers[0]} vs {defenders[0]}"
        return wid

    for entry in payments:
        if not isinstance(entry, Mapping):
            continue
        payer = str(entry.get("from") or "")
        recipient = str(entry.get("to") or "")
        amount = int(entry.get("amount_per_turn", 0) or 0)
        turns_remaining = int(entry.get("turns_remaining", 0) or 0)
        if not payer or not recipient or amount <= 0 or turns_remaining <= 0:
            # Malformed / already drained — drop silently.
            continue

        if payer in vassals:
            reason = "payer_vassalized"
            events["cancelled"].append({
                "payment_id": str(entry.get("payment_id") or ""),
                "from": payer,
                "to": recipient,
                "reason": reason,
                "remaining_turns": int(turns_remaining),
            })
            queue_dispatch_event(world, "settlement_recurring_gold_cancelled", {
                "from_nation": payer,
                "to_nation": recipient,
                "war_label": _war_label_for(entry),
                "reason": reason,
            }, "always")
            continue
        if _is_recurring_payment_nation_eliminated(
            world,
            payer,
            nation_gold=nation_gold,
            vassals=vassals,
            active_nations=active_nations,
        ):
            reason = "payer_eliminated"
            events["cancelled"].append({
                "payment_id": str(entry.get("payment_id") or ""),
                "from": payer,
                "to": recipient,
                "reason": reason,
                "remaining_turns": int(turns_remaining),
            })
            queue_dispatch_event(world, "settlement_recurring_gold_cancelled", {
                "from_nation": payer,
                "to_nation": recipient,
                "war_label": _war_label_for(entry),
                "reason": reason,
            }, "always")
            continue
        if _is_recurring_payment_nation_eliminated(
            world,
            recipient,
            nation_gold=nation_gold,
            vassals=vassals,
            active_nations=active_nations,
        ):
            reason = "recipient_eliminated"
            events["cancelled"].append({
                "payment_id": str(entry.get("payment_id") or ""),
                "from": payer,
                "to": recipient,
                "reason": reason,
                "remaining_turns": int(turns_remaining),
            })
            queue_dispatch_event(world, "settlement_recurring_gold_cancelled", {
                "from_nation": payer,
                "to_nation": recipient,
                "war_label": _war_label_for(entry),
                "reason": reason,
            }, "always")
            continue
        if _is_renewed_war_between(world, payer, recipient):
            reason = "renewed_war"
            events["cancelled"].append({
                "payment_id": str(entry.get("payment_id") or ""),
                "from": payer,
                "to": recipient,
                "reason": reason,
                "remaining_turns": int(turns_remaining),
            })
            queue_dispatch_event(world, "settlement_recurring_gold_cancelled", {
                "from_nation": payer,
                "to_nation": recipient,
                "war_label": _war_label_for(entry),
                "reason": reason,
            }, "always")
            continue

        # Tick: transfer what's affordable, decrement, surface partial /
        # full / completion events.
        balance = int(nation_gold.get(payer, 0) or 0)
        transfer = min(int(amount), max(0, balance))
        nation_gold[payer] = balance - transfer
        nation_gold[recipient] = int(nation_gold.get(recipient, 0) or 0) + transfer
        turns_remaining -= 1
        record = dict(entry)
        record["turns_remaining"] = int(turns_remaining)
        if transfer < amount:
            events["partial"].append({
                "payment_id": str(entry.get("payment_id") or ""),
                "from": payer,
                "to": recipient,
                "amount_paid": int(transfer),
                "amount_due": int(amount),
                "turns_remaining": int(turns_remaining),
            })
            queue_dispatch_event(world, "settlement_recurring_gold_partial", {
                "from_nation": payer,
                "to_nation": recipient,
                "amount_paid": str(int(transfer)),
                "amount_due": str(int(amount)),
                "war_label": _war_label_for(entry),
            }, "always")
        elif transfer > 0:
            events["paid"].append({
                "payment_id": str(entry.get("payment_id") or ""),
                "from": payer,
                "to": recipient,
                "amount_paid": int(transfer),
                "turns_remaining": int(turns_remaining),
            })
            queue_dispatch_event(world, "settlement_recurring_gold_paid", {
                "from_nation": payer,
                "to_nation": recipient,
                "amount_paid": str(int(transfer)),
                "turns_remaining": str(int(turns_remaining)),
                "war_label": _war_label_for(entry),
            }, "always")

        if turns_remaining <= 0:
            total_amount = int(record.get("total_turns", 0) or 0) * int(amount)
            events["completed"].append({
                "payment_id": str(entry.get("payment_id") or ""),
                "from": payer,
                "to": recipient,
                "total_amount": int(total_amount),
            })
            queue_dispatch_event(world, "settlement_recurring_gold_completed", {
                "from_nation": payer,
                "to_nation": recipient,
                "total_amount": str(int(total_amount)),
                "war_label": _war_label_for(entry),
            }, "always")
            # Drop the record on natural completion.
            continue

        survivors.append(record)

    setattr(world, "recurring_settlement_payments", survivors)
    return events


# Import here to avoid a circular import on module load; the dispatch
# helper is a leaf utility.
from backend.game_logic.dispatch import queue_dispatch_event  # noqa: E402
