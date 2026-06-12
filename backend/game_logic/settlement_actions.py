"""Settlement dialogue-action dispatch and handler arms (CH-1 split, layer 5).

handle_settlement_dialogue_action + the CH-5 response-shape wrapper, the
CH-2 dispatch tables (SETTLEMENT_ACTION_DISPATCH +
SETTLEMENT_SCOPE_REPLACE_DISPATCH — action id → module-level `_action_*`
handler with the uniform `(world, *, action, dialogue, action_params,
war_id)` signature), and the tier-2 dial / demand-verb / pair-substitute /
scope-replace handler arms. Split from settlement_preview.py (CH-1); may
import every lower settlement_* layer.
"""

from __future__ import annotations

import copy

from backend.game_logic.diplomatic_templates import (
    resolve_named_diplomat,
    resolve_settlement_voice_line,
)
from backend.game_logic.settlement_scoring import (
    GOLD_PER_TURN_MAX_TURNS,
    GOLD_PER_TURN_MIN_AMOUNT,
    GOLD_PER_TURN_MIN_TURNS,
    MAX_SETTLEMENT_CLAUSE_COUNT,
)
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
)
from backend.game_logic.settlement_baseline import (
    CONCESSION_BASELINE_GOLD_FLOOR,
    CONCESSION_BASELINE_TREASURY_RESERVE,
    _concession_baseline_payer_balance,
    _demand_baseline_select_region,
    _guided_gold_offer_default,
    _guided_region_offer_candidate,
    _promised_regions_in_terms,
    compute_settlement_baseline,
)
from backend.game_logic.settlement_ratify import (
    _stage_replacement_settlement_terms,
    ratify_settlement_confirm,
)
from backend.game_logic.settlement_routes import (
    _error_display,
    _normalize_nation_list,
    _terminal_recovery_copy,
    evaluate_war_detail_actionability,
)
from backend.game_logic.settlement_staging import (
    SETTLEMENT_EDITOR_CALLER_KIND,
    _DEMAND_CLAUSE_CAP_REASON,
    _build_pair_substitute_confirm_dialogue,
    _demand_hard_stop_reason,
    _dialogue_scope_values,
    _discard_scoped_settlement_draft_for_dialogue,
    _redial_settlement_terms,
    _restage_settlement_after_redraw,
    _settlement_remaining_war_courts,
    build_settlement_confirm_dialogue,
    build_settlement_preview,
    compute_settlement_draft_key,
    save_scoped_settlement_draft,
    stage_settlement_confirm,
)
from backend.game_logic.settlement_validation import (
    _has_material_concession_terms,
    _other_side,
    _side_leader,
    _term_lists_equal,
    compute_gold_payer_budgets,
    evaluate_liberation_eligibility,
    evaluate_pair_peace_substitute_eligibility,
    evaluate_subjugation_eligibility,
    evaluate_vassalage_eligibility,
    get_coverable_enemy_participants,
    validate_settlement_terms,
)


def _gold_headroom_for_payer(
    world: Any,
    candidate_terms: List[Dict[str, Any]],
    *,
    payer: str,
    exclude_index: int,
) -> int:
    """Remaining gold capacity for ``payer`` in ``candidate_terms`` once
    every OTHER gold line is funded (Gate-4 G4F-2 / DC-1).

    The clamp-side mirror of ``_check_gold_payment_budget_conflict``: the
    guided magnitude verbs refuse an explicit amount above this bound with a
    humanized in-voice reason instead of authoring a draft the restage
    validator bounces as ``gold_payment_budget_conflict``.
    """
    budgets = compute_gold_payer_budgets(
        world, candidate_terms, extra_payers=[payer],
    )
    used = 0
    for idx, term in enumerate(candidate_terms):
        if idx == exclude_index:
            continue
        if not isinstance(term, Mapping):
            continue
        if term.get("type") not in ("gold_indemnity", "gold_lump", "gold_per_turn"):
            continue
        if str(term.get("from") or "") != payer:
            continue
        amount = abs(int(term.get("amount", 0) or 0))
        if term.get("type") == "gold_per_turn":
            used += amount * max(0, int(term.get("turns", 0) or 0))
        else:
            used += amount
    return max(0, int(budgets.get(payer, 0)) - used)


def _payer_budget_refusal_display(
    *,
    payer: str,
    clause: Mapping[str, Any],
    headroom: int,
) -> str:
    """In-voice refusal for an explicit gold magnitude beyond the payer's
    capacity (G4F-2 / UX-6 — the error path names the binding constraint
    instead of the generic blame-the-player validation copy)."""
    amount = int(clause.get("amount", 0) or 0)
    if headroom <= 0:
        return (
            f"{payer} cannot raise that, Sire — their treasury bears "
            "nothing more."
        )
    if str(clause.get("type") or "") == "gold_per_turn":
        turns = max(1, int(clause.get("turns", 0) or 0))
        per_turn_cap = headroom // turns
        return (
            f"{payer} cannot sustain {amount} gold a turn for {turns} "
            f"turns, Sire — at most {per_turn_cap} a turn over that term."
        )
    return (
        f"{payer} cannot raise {amount} gold, Sire — {headroom} is the "
        "most their treasury bears."
    )


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
    # SC-5R-1 scoped store: clear the prior scope's scoped draft (the
    # chooser is the explicit "replace this scope's draft" path) and
    # write the incoming scope's draft under its own scoped key so a
    # reopen of either scope can read its own draft without collision.
    scoped_drafts = getattr(world, "pending_settlement_drafts_by_key", None)
    if isinstance(scoped_drafts, dict):
        scoped_drafts.pop(current_key, None)
        mounted_draft_key = str(dialogue.get("current_draft_key") or "")
        if mounted_draft_key:
            scoped_drafts.pop(mounted_draft_key, None)
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


def _dial_territory_escalation_candidates(
    world: Any,
    *,
    terms: List[Mapping[str, Any]],
    scope_courts: List[str],
    direction: str,
    proposer_side_participants: List[str],
    proposer_leader: str,
) -> Dict[str, Dict[str, Any]]:
    """GT-A5 (user-approved June 11, 2026) — one ready-to-author territory
    clause per scoped court that may legally escalate, sourced from the SAME
    selectors the guided row suggestions show (`Take <region>` /
    `Offer <region>` — never a dial-invented identity). The redial tail
    authors a candidate only for a court whose gold lever exhausted this
    sweep (ceiling class), under the clause cap.

    Anti-balloon guards applied HERE (the spec §3.5 GT-A5 rule):
    - at most ONE escalated territory clause per court per direction — a
      court with an existing direction-matching territory line never gets a
      second from the dial (the bilateral ``modify_harsh`` ``has_territory``
      guard, direction-scoped); further land is an explicit row click;
    - promised-region dedupe across the package AND across this click's own
      candidates (two courts may not be promised the same France-held
      region);
    - territory only — vassalage/subjugation/liberation-class clauses are
      never auto-authored.
    """
    leader = str(proposer_leader or "")
    if not leader:
        return {}
    claimed = set(_promised_regions_in_terms(terms))
    candidates: Dict[str, Dict[str, Any]] = {}
    for raw_court in scope_courts:
        court = str(raw_court or "")
        if not court:
            continue
        if direction == "harsher":
            already_escalated = any(
                isinstance(t, Mapping)
                and str(t.get("type") or "").startswith("territory")
                and str(t.get("from") or "") == court
                for t in terms
            )
            if already_escalated:
                continue
            region = str(
                _demand_baseline_select_region(
                    world,
                    court=court,
                    proposer_side_participants=proposer_side_participants,
                    excluded_regions=claimed,
                )
                or ""
            )
            if not region or region in claimed:
                continue
            claimed.add(region)
            candidates[court] = {
                "type": "territory_cede", "from": court, "to": leader,
                "region": region, "authored_by": "talleyrand",
            }
        else:
            already_escalated = any(
                isinstance(t, Mapping)
                and str(t.get("type") or "").startswith("territory")
                and str(t.get("from") or "") == leader
                and str(t.get("to") or "") == court
                for t in terms
            )
            if already_escalated:
                continue
            region = str(
                _guided_region_offer_candidate(
                    world,
                    court=court,
                    proposer_side_participants=proposer_side_participants,
                    settlement_terms=terms,
                )
                or ""
            )
            if not region or region in claimed:
                continue
            claimed.add(region)
            candidates[court] = {
                "type": "territory_cede", "from": leader, "to": court,
                "region": region, "authored_by": "talleyrand",
            }
    return candidates


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
        # G4F-2 / DC-1: every gold grow (and the focused seed) is bounded by
        # the payer's real capacity — the same SC-1/SC-33 formula the budget
        # validator enforces — so a dial click can never author a package the
        # restage revalidation would bounce.
        payer_gold_budgets = compute_gold_payer_budgets(
            world,
            terms,
            extra_payers=[
                n for n in [str(proposer_leader or ""), *scope_courts] if n
            ],
        )
        # GT-A5: pre-compute the suggestion-engine territory escalation each
        # scoped court could take if its gold lever exhausts this sweep —
        # the redial tail authors one only for ceiling-class courts.
        territory_escalations = _dial_territory_escalation_candidates(
            world,
            terms=terms,
            scope_courts=scope_courts,
            direction=direction,
            proposer_side_participants=[
                str(n) for n in (war_instance.get(proposer_side) or []) if n
            ],
            proposer_leader=str(proposer_leader or ""),
        )
        new_terms = _redial_settlement_terms(
            terms=terms,
            scope_courts=scope_courts,
            direction=direction,
            proposer_side_leader=proposer_leader,
            protected_notes=protected_notes,
            seeded_events=seeded_events,
            payer_gold_budgets=payer_gold_budgets,
            territory_escalations=territory_escalations,
        )
        verb = "Pressed" if direction == "harsher" else "Eased"
        target_label = "the whole table" if scope == "table" else scope
        message = f"{verb} {target_label}."
        # GT-A5: every territory escalation the redraw authored is VOICED —
        # Talleyrand explains the pivot from coin to land in the popup beat
        # AND the terminal message.
        escalation_lines = [
            resolve_settlement_voice_line(
                "settlement_dial_escalation_demand_talleyrand"
                if event.get("group") == "demand"
                else "settlement_dial_escalation_offer_talleyrand",
                court=str(event.get("court") or ""),
                region=str(event.get("region") or ""),
            )
            for event in seeded_events
            if event.get("kind") == "territory_escalation"
        ]
        if escalation_lines:
            message = " ".join([message, *escalation_lines])
        # De-duplicate while preserving order — a whole-table sweep can emit
        # the same treasury note once per concession line.
        unique_notes = list(dict.fromkeys(protected_notes))
        if unique_notes:
            # §3.5: a protected player-authored line is never invisible — the
            # skip/floor is named in the dial's own response message.
            message = " ".join([message, *unique_notes])
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
        # GT-A5: the escalation lines lead (they explain WHAT the click
        # authored); the DC-4 caution follows where it applies — an escalated
        # demand on a concede-direction court draws BOTH.
        voice_beats: List[Dict[str, str]] = [
            {
                "kind": "talleyrand_line",
                "speaker": "Talleyrand",
                "nation": str(event.get("court") or ""),
                "line": line,
            }
            for event, line in zip(
                [
                    e for e in seeded_events
                    if e.get("kind") == "territory_escalation"
                ],
                escalation_lines,
            )
        ]
        voice_beats.extend(
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
        )
        # G4F-5: the ceiling/protection notes must reach the PLAYER, not just
        # the terminal — the dial response's `message` prints behind the modal
        # popup, so a press at the ceiling read as a wordless flash. The notes
        # ride the restaged dialogue as one-shot voice beats (the same carrier
        # as the DC-4 caution), which the popup preamble already renders.
        voice_beats.extend(
            {
                "kind": "dial_note",
                "speaker": "Talleyrand",
                "nation": "",
                "line": note,
            }
            for note in unique_notes
        )
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
        # G4F-2 / DC-1: an explicit magnitude beyond the payer's capacity is
        # refused HERE with the binding constraint named, never authored for
        # the restage validator to bounce as a generic failure.
        payer = str(clause.get("from") or "")
        if payer:
            candidate_terms = [dict(t) for t in terms]
            candidate_terms[clause_index] = dict(clause)
            headroom = _gold_headroom_for_payer(
                world, candidate_terms, payer=payer, exclude_index=clause_index,
            )
            consumption = int(clause.get("amount", 0) or 0)
            if ttype == "gold_per_turn":
                consumption *= max(0, int(clause.get("turns", 0) or 0))
            if consumption > headroom:
                return _fail(
                    "gold_payment_budget_conflict",
                    _payer_budget_refusal_display(
                        payer=payer, clause=clause, headroom=headroom,
                    ),
                )
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

    # G4F-2 / DC-1: a gold line the payer cannot fund (explicit over-balance
    # amount, or a default colliding with the payer's other package gold) is
    # refused here with the binding constraint named — never authored for
    # the restage validator to bounce.
    if clause.get("type") in ("gold_indemnity", "gold_per_turn"):
        gold_payer = str(clause.get("from") or "")
        if gold_payer:
            candidate_terms = [dict(t) for t in terms] + [dict(clause)]
            headroom = _gold_headroom_for_payer(
                world,
                candidate_terms,
                payer=gold_payer,
                exclude_index=len(candidate_terms) - 1,
            )
            consumption = int(clause.get("amount", 0) or 0)
            if clause.get("type") == "gold_per_turn":
                consumption *= max(0, int(clause.get("turns", 0) or 0))
            if consumption > headroom:
                return _fail(
                    "gold_payment_budget_conflict",
                    _payer_budget_refusal_display(
                        payer=gold_payer, clause=clause, headroom=headroom,
                    ),
                )
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


def _fresh_recurring_gold_preset(
    world: Any,
    dialogue: Mapping[str, Any],
    *,
    action_id: str,
    war_id: str,
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


def _action_suspend_settlement_editor(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
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


def _action_back_out_settlement(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
    # SC-2: discard-confirm semantics. Non-empty drafts signal the
    # frontend to confirm discard; empty drafts pop immediately.
    terms = list(dialogue.get("settlement_terms") or [])
    has_draft = bool(terms)
    world.dialogue_manager.pop()
    # Clear persisted draft on back-out.
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


def _action_submit_settlement_for_review(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
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


def _action_return_to_settlement_terms(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
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


def _action_revise_settlement_terms(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
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


def _action_author_gold_indemnity_terms(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
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


def _action_author_gold_per_turn_terms(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
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


def _action_keep_current_settlement_draft(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
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


def _action_apply_recurring_gold_preset_replacement(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
    preset_payload, preset_terms, error_payload = _fresh_recurring_gold_preset(
        world, dialogue, action_id=action, war_id=war_id,
    )
    if error_payload is not None:
        return error_payload
    return _stage_replacement_settlement_terms(
        world,
        dialogue,
        action=action,
        terms=preset_terms,
        message="Talleyrand's recurring-gold draft has replaced the current draft.",
    )


def _action_apply_concession_baseline_replacement(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
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


def _action_apply_surrender_preset_replacement(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
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


def _action_re_author_with_concessions(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
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


def _action_author_recurring_gold_terms(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
    selected_target = str(dialogue.get("selected_target_nation") or "")
    current_terms = [
        dict(t)
        for t in (dialogue.get("settlement_terms") or [])
        if isinstance(t, Mapping)
    ]
    preset_payload, preset_terms, error_payload = _fresh_recurring_gold_preset(
        world, dialogue, action_id=action, war_id=war_id,
    )
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


def _action_author_surrender_terms(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
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


def _action_open_war_detail(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
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


def _action_scope_replace_keep_current(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
    return _restore_scope_replace_current_dialogue(
        world, dialogue, action=action,
    )


def _action_scope_replace_apply(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
    return _apply_scope_replace_confirm(world, dialogue)


def _action_settlement_tier2(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
    # CH-5: the old per-arm re-show safety net that lived here (re-attach
    # the mounted dialogue on a bare Tier-2 failure) is subsumed by the
    # `_enforce_settlement_response_shape` wrapper, which applies it to
    # EVERY arm - not just these five verbs.
    return _handle_settlement_tier2_action(
        world, action=action, dialogue=dialogue, action_params=action_params,
    )


def _action_settlement_demand_verb(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
    # GT-Slice-1 (S7 wiring point 1): the guided demand-mutation verbs
    # join the dispatch INSIDE the CH-5 wrapper - their failure contract
    # (re-attached dialogue + error_display, never neither) is enforced
    # by `_enforce_settlement_response_shape`, not a per-arm net.
    return _handle_settlement_demand_action(
        world, action=action, dialogue=dialogue, action_params=action_params,
    )


def _action_pair_peace_substitute(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
    # SC-29 / G2-Slice-7 pair-scoped peace substitute CTAs.
    return _handle_pair_peace_substitute_action(
        world, action=action, dialogue=dialogue,
    )


def _action_confirm_settlement(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Dict[str, Any],
    war_id: str,
) -> Dict[str, Any]:
    return ratify_settlement_confirm(world, dialogue)


# CH-2 (Gate-4 pre-flight audit S9): the dispatch tables that replace the
# former ~950-line if-chain. Every player-visible settlement dialogue action
# id maps to one module-level handler with the uniform signature
# `(world, *, action, dialogue, action_params, war_id)`. The Gate 3
# action-id whitelist test asserts membership against these tables (runtime
# truth), replacing the old `action == "..."` source scan.

# Same-war different-scope chooser (G2-Slice-G2e): selected by the staged
# dialogue's TYPE before the action id is consulted, so a chooser click can
# never fall through to the main table.
SETTLEMENT_SCOPE_REPLACE_DISPATCH: Dict[str, Callable[..., Dict[str, Any]]] = {
    "keep_current_scope_draft": _action_scope_replace_keep_current,
    "back_out_settlement": _action_scope_replace_keep_current,
    "replace_current_scope_draft": _action_scope_replace_apply,
}

SETTLEMENT_ACTION_DISPATCH: Dict[str, Callable[..., Dict[str, Any]]] = {
    # Re-front Slice 2 Tier-2 verbs (dials / coverage edits / court focus).
    "settlement_dial_harsher": _action_settlement_tier2,
    "settlement_dial_generous": _action_settlement_tier2,
    "settlement_cover_add": _action_settlement_tier2,
    "settlement_cover_drop": _action_settlement_tier2,
    "settlement_focus_court": _action_settlement_tier2,
    # GT-Slice-1 guided demand-mutation verbs.
    **{
        verb: _action_settlement_demand_verb
        for verb in SETTLEMENT_DEMAND_VERB_ACTION_IDS
    },
    "suspend_settlement_editor": _action_suspend_settlement_editor,
    "back_out_settlement": _action_back_out_settlement,
    "submit_settlement_for_review": _action_submit_settlement_for_review,
    "return_to_settlement_terms": _action_return_to_settlement_terms,
    "revise_settlement_terms": _action_revise_settlement_terms,
    "author_gold_indemnity_terms": _action_author_gold_indemnity_terms,
    "author_gold_per_turn_terms": _action_author_gold_per_turn_terms,
    "keep_current_settlement_draft": _action_keep_current_settlement_draft,
    "apply_recurring_gold_preset_replacement": (
        _action_apply_recurring_gold_preset_replacement
    ),
    "apply_concession_baseline_replacement": (
        _action_apply_concession_baseline_replacement
    ),
    "apply_surrender_preset_replacement": _action_apply_surrender_preset_replacement,
    "re_author_with_concessions": _action_re_author_with_concessions,
    "author_recurring_gold_terms": _action_author_recurring_gold_terms,
    "author_surrender_terms": _action_author_surrender_terms,
    "open_war_detail": _action_open_war_detail,
    # SC-29 / G2-Slice-7 pair-scoped peace substitute CTAs.
    "seek_bilateral_peace": _action_pair_peace_substitute,
    "seek_armistice_instead": _action_pair_peace_substitute,
    "confirm_settlement": _action_confirm_settlement,
}


def _handle_settlement_dialogue_action_inner(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Handle C2 settlement dialogue actions (the per-action dispatch).

    CH-2: the former ~950-line if-chain is a dispatch-table lookup - each
    arm lives in a module-level ``_action_*`` handler registered in
    ``SETTLEMENT_ACTION_DISPATCH`` (or, for the same-war different-scope
    chooser, ``SETTLEMENT_SCOPE_REPLACE_DISPATCH``, selected by the staged
    dialogue's TYPE before the action id is consulted).

    Callers use the public ``handle_settlement_dialogue_action`` wrapper,
    which enforces the CH-5 response-shape invariant on every arm's result -
    handlers here may return bare failures and rely on the wrapper to
    re-attach the mounted dialogue and render ``error_display``.

    ``confirm_settlement`` runs the live ratification mutation through
    ``ratify_settlement_confirm``. ``back_out`` / ``revise_terms`` remain
    pure (no mutation, dialogue popped).

    ``action_params`` carries the clicked affordance's structured fields (e.g.
    a dial's ``scope`` or a coverage edit's ``nation``) for the Re-front Slice 2
    PROPOSE actions (``settlement_dial_*`` / ``settlement_cover_*`` /
    ``settlement_focus_court``), which ride on per-court rows and rail buttons
    rather than the keyword-matched ``options[]`` surface.
    """
    params = dict(action_params or {})
    war_id = str(dialogue.get("war_id") or "")
    dialogue_type = str(dialogue.get("type") or dialogue.get("dialogue_type") or "")
    if dialogue_type == "settlement_scope_replace_confirm":
        handler = SETTLEMENT_SCOPE_REPLACE_DISPATCH.get(action)
        if handler is None:
            return {
                "success": False,
                "dialogue_type": "settlement_scope_replace_confirm",
                "action": action,
                "war_id": war_id,
                "error": "unknown_settlement_action",
                "mutated": False,
            }
        return handler(
            world, action=action, dialogue=dialogue,
            action_params=params, war_id=war_id,
        )
    if dialogue_type == "settlement_pair_substitute_confirm":
        # G4F-8: chooser-scoped dispatch — same TYPE-first selection as the
        # scope-replace chooser above.
        handler = SETTLEMENT_PAIR_SUBSTITUTE_DISPATCH.get(action)
        if handler is None:
            return {
                "success": False,
                "dialogue_type": "settlement_pair_substitute_confirm",
                "action": action,
                "war_id": war_id,
                "error": "unknown_settlement_action",
                "mutated": False,
            }
        return handler(
            world, action=action, dialogue=dialogue,
            action_params=params, war_id=war_id,
        )
    handler = SETTLEMENT_ACTION_DISPATCH.get(action)
    if handler is None:
        return {"success": False, "error": "unknown_settlement_action", "mutated": False}
    return handler(
        world, action=action, dialogue=dialogue,
        action_params=params, war_id=war_id,
    )


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

    # G4F-8: the substitute is no longer a one-click trapdoor. Mount the
    # confirm chooser — the joint draft stays untouched, Cancel restores
    # the REVIEW exactly, and the handoff (draft discard + bilateral mount
    # with the target's authored slice carried over) runs only on
    # `confirm_pair_substitute`.
    confirm_dialogue = _build_pair_substitute_confirm_dialogue(
        dialogue,
        action=action,
        proposal_type=proposal_type,
        selected_target=selected_target,
        eligibility=eligibility,
    )
    world.dialogue_manager.replace(confirm_dialogue)
    return {
        "success": True,
        "dialogue_type": "settlement_pair_substitute_confirm",
        "action": action,
        "war_id": war_id,
        "selected_target_nation": selected_target,
        "scope": "selected_pair",
        "proposal_type": proposal_type,
        "diplomatic_dialogue": confirm_dialogue,
        "message": str(confirm_dialogue.get("message") or ""),
        "awaiting_diplomatic_response": True,
        "mutated": False,
        "suppress_proposal_result_popup": True,
    }


def _pair_substitute_seed_terms(
    settlement_terms: List[Mapping[str, Any]],
    *,
    target: str,
    proposer_leader: str,
) -> Dict[str, List[Dict[str, Any]]]:
    """G4F-8 carry-over — translate the target court's slice of the
    authored settlement package into the bilateral demands/sweeteners
    dialect, so confirming the pair substitute does not throw the player's
    drafting away.

    Mapping (settlement clause → bilateral term):
    - ``gold_indemnity`` FROM the target → demand ``gold_lump`` at face
      value (TO the target → sweetener ``gold_lump``).
    - ``gold_per_turn`` → ``gold_lump`` at ``amount × turns`` — the
      total-obligation basis the solvency check projects. The bilateral
      recurring dialect is PERPETUAL (no ``turns`` field), so a finite
      settlement stream must convert by total, never by rate.
    - ``territory_cede`` FROM the target → one aggregated
      ``territory_cede`` demand carrying every region.
    - Identity-bearing clauses (vassalage, liberation, forced_alliance, …)
      and proposer-paid territory are settlement-tier — skipped; the
      bilateral flow's own authoring handles anything further.
    """
    demands: List[Dict[str, Any]] = []
    sweeteners: List[Dict[str, Any]] = []
    demanded_regions: List[str] = []
    for term in settlement_terms or []:
        if not isinstance(term, Mapping):
            continue
        ttype = str(term.get("type") or "")
        frm = str(term.get("from") or "")
        to = str(term.get("to") or "")
        amount = int(term.get("amount", 0) or 0)
        if ttype == "gold_indemnity" and amount > 0:
            if frm == target:
                demands.append({"type": "gold_lump", "value": amount})
            elif frm == proposer_leader and to == target:
                sweeteners.append({"type": "gold_lump", "value": amount})
        elif ttype == "gold_per_turn" and amount > 0:
            total = amount * max(0, int(term.get("turns", 0) or 0))
            if total <= 0:
                continue
            if frm == target:
                demands.append({"type": "gold_lump", "value": total})
            elif frm == proposer_leader and to == target:
                sweeteners.append({"type": "gold_lump", "value": total})
        elif ttype == "territory_cede" and frm == target:
            region = str(term.get("region") or "")
            if region:
                demanded_regions.append(region)
    if demanded_regions:
        demands.append({
            "type": "territory_cede",
            "value": len(demanded_regions),
            "regions": demanded_regions,
        })
    return {"demands": demands, "sweeteners": sweeteners}


def _execute_pair_substitute_handoff(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    war_id: str,
    selected_target: str,
    proposal_type: str,
) -> Dict[str, Any]:
    """The confirmed pair-substitute handoff (the pre-G4F-8 one-click body):
    discard the now-stale scoped draft, mount the bilateral proposal flow,
    and seed it from the target's authored slice (``dialogue`` is the PRIOR
    settlement dialogue carried on the confirm chooser)."""
    voice_key = (
        "settlement_seek_armistice_instead_talleyrand"
        if action == "seek_armistice_instead"
        else "settlement_seek_bilateral_peace_instead_talleyrand"
    )
    war_label = str(dialogue.get("war_label") or war_id or "this war")

    # SC-29 / War Detail recovery contract: a successful pair substitute
    # makes any preserved scoped settlement draft that covers the target
    # stale. Mark the entry stale via removal here; re-preview is required
    # on the next settlement entry per the spec.
    covered = list(dialogue.get("covered_enemy_participants") or [])
    draft_invalidated = False
    if selected_target in covered:
        draft_invalidated = _discard_scoped_settlement_draft_for_dialogue(
            world, dialogue
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

    # G4F-8 carry-over: seed the bilateral draft from the target court's
    # authored slice instead of discarding the player's drafting. Override
    # the execute_proposal option's terms and re-run the display enrichment
    # so the summary / annotated terms / acceptance estimate all describe
    # the SEEDED package (the G4F-6 objection judged the pre-seed suggested
    # terms — with the G4F-9 ladder those are never light-while-winning, so
    # the stale-beat edge is the rare white-peace floor only).
    if isinstance(proposal_dialogue, dict):
        proposer_side = str(dialogue.get("proposer_side") or "")
        staged_leaders = dialogue.get("staged_leaders") or {}
        proposer_leader = str(
            staged_leaders.get(proposer_side)
            or _side_leader(
                (getattr(world, "war_instances", {}) or {}).get(war_id) or {},
                proposer_side,
            )
            or ""
        )
        seed = _pair_substitute_seed_terms(
            [
                t for t in (dialogue.get("settlement_terms") or [])
                if isinstance(t, Mapping)
            ],
            target=selected_target,
            proposer_leader=proposer_leader,
        )
        if seed["demands"] or seed["sweeteners"]:
            seeded = False
            for opt in proposal_dialogue.get("options", []):
                if opt.get("action") == "execute_proposal":
                    base_terms = dict(opt.get("terms") or {})
                    base_terms["type"] = base_terms.get("type", proposal_type)
                    base_terms["proposal_type"] = proposal_type
                    base_terms["demands"] = seed["demands"]
                    base_terms["sweeteners"] = seed["sweeteners"]
                    base_terms["carried_from_settlement"] = True
                    opt["terms"] = base_terms
                    seeded = True
                    break
            if seeded:
                try:
                    from backend.game_logic.diplomatic_dialogue import (
                        _enrich_proposal_summary,
                    )
                    proposal_dialogue = _enrich_proposal_summary(
                        proposal_dialogue,
                        selected_target,
                        proposal_type,
                        world,
                    )
                except Exception:  # pragma: no cover - defensive
                    pass
                proposal_dialogue["carried_from_settlement"] = True

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


def _action_confirm_pair_substitute(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Mapping[str, Any],
    war_id: str,
) -> Dict[str, Any]:
    """G4F-8 — the confirmed handoff. ``dialogue`` is the chooser; the prior
    settlement dialogue rides on it. Eligibility is re-validated at confirm
    time — a pair gone ineligible between beats restores the REVIEW with the
    refusal named (CH-5 re-attach), mutating nothing."""
    prior = dialogue.get("prior_dialogue")
    sub_action = str(dialogue.get("pair_substitute_action") or "")
    selected_target = str(dialogue.get("selected_target_nation") or "")
    proposal_type = str(dialogue.get("proposal_type") or "peace")
    if not isinstance(prior, Mapping) or not sub_action or not selected_target:
        return {
            "success": False,
            "dialogue_type": "settlement_pair_substitute_confirm",
            "action": action,
            "war_id": war_id,
            "error": "malformed_route",
            "error_display": _error_display("malformed_route"),
            "mutated": False,
            "suppress_proposal_result_popup": True,
        }
    actor = str(getattr(world, "player_nation", "France") or "France")
    eligibility = evaluate_pair_peace_substitute_eligibility(
        world,
        war_id=war_id,
        actor_nation=actor,
        target_nation=selected_target,
        action=sub_action,
    )
    if not eligibility.get("eligible"):
        restored = dict(prior)
        world.dialogue_manager.replace(restored)
        refusal = eligibility.get("refusal_code") or "malformed_route"
        return {
            "success": False,
            "dialogue_type": str(restored.get("dialogue_type") or "settlement_confirm"),
            "action": action,
            "war_id": war_id,
            "selected_target_nation": selected_target,
            "error": refusal,
            "error_display": eligibility.get("disabled_reason_display")
            or _error_display(refusal),
            "pair_substitute_eligibility": eligibility,
            "diplomatic_dialogue": restored,
            "mutated": False,
            "suppress_proposal_result_popup": True,
        }
    return _execute_pair_substitute_handoff(
        world,
        action=sub_action,
        dialogue=prior,
        war_id=war_id,
        selected_target=selected_target,
        proposal_type=proposal_type,
    )


def _action_keep_joint_settlement(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Mapping[str, Any],
    war_id: str,
) -> Dict[str, Any]:
    """G4F-8 — Cancel on the pair-substitute chooser: restore the prior
    settlement dialogue exactly (the scope-replace keep semantics — a no-op
    that re-shows the staged REVIEW; the joint draft was never touched)."""
    prior = dialogue.get("prior_dialogue")
    if not isinstance(prior, Mapping):
        return {
            "success": False,
            "dialogue_type": "settlement_pair_substitute_confirm",
            "action": action,
            "war_id": war_id,
            "error": "malformed_route",
            "error_display": _error_display("malformed_route"),
            "mutated": False,
            "suppress_proposal_result_popup": True,
        }
    restored = dict(prior)
    world.dialogue_manager.replace(restored)
    return {
        "success": True,
        "dialogue_type": str(restored.get("dialogue_type") or "settlement_confirm"),
        "action": action,
        "war_id": war_id,
        "diplomatic_dialogue": restored,
        "message": "Staying with the joint settlement, Sire.",
        "awaiting_diplomatic_response": True,
        "mutated": False,
        "suppress_proposal_result_popup": True,
    }


# G4F-8 — chooser-scoped dispatch (the scope-replace pattern): while the
# pair-substitute confirm dialogue is mounted, ONLY its two verbs resolve;
# stray table actions fail closed instead of running against the chooser.
SETTLEMENT_PAIR_SUBSTITUTE_DISPATCH: Dict[str, Any] = {
    "confirm_pair_substitute": _action_confirm_pair_substitute,
    "keep_joint_settlement": _action_keep_joint_settlement,
}
