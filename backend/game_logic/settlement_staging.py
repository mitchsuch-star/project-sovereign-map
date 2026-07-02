"""Settlement dialogue staging and the PROPOSE/REVIEW surface (CH-1 split, layer 3).

Scoped draft store, scope utils, build_settlement_confirm_dialogue,
build_settlement_preview, stage/revalidate/restage, the guided per-court
payload (suggestions, current demands, dials, budget-bound recommendation).
Split from settlement_preview.py (CH-1); may import settlement_routes /
settlement_validation / settlement_baseline. The two ally-petition calls in
stage_settlement_confirm use a function-level import (offers is a higher
layer) — the established settlement cycle-break pattern.
"""

from __future__ import annotations

import copy
import hashlib
import json

from backend.display_names import (
    acceptance_band_display,
    acceptance_band_phrase,
)
from backend.game_logic import settlement_scoring
from backend.game_logic.diplomatic_templates import (
    resolve_multi_court_settlement_voice,
    resolve_settlement_voice_line,
)
from backend.game_logic.settlement_presentation import (
    build_contribution_share_rows,
    build_settlement_review,
    detect_awe_set_pieces,
)
from backend.game_logic.settlement_scoring import (
    ACCEPTANCE_THRESHOLD,
    CONCESSION_GOLD_CAP,
    CONCESSION_GOLD_DIVISOR,
    GOLD_PER_TURN_MAX_TURNS,
    GOLD_PER_TURN_MIN_AMOUNT,
    GOLD_PER_TURN_MIN_TURNS,
    MAX_SETTLEMENT_CLAUSE_COUNT,
)
from typing import (
    Any,
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
    CONCESSION_BASELINE_GOLD_HARD_CAP,
    CONCESSION_BASELINE_TREASURY_RESERVE,
    SETTLEMENT_DIAL_GOLD_STEP,
    _compute_recurring_gold_preset,
    _compute_surrender_preset,
    _concession_baseline_payer_balance,
    _concession_baseline_transferable_candidates,
    _demand_baseline_region_candidates,
    _enrich_acceptance_display,
    _gold_per_turn_prefill,
    _guided_gold_offer_default,
    _payer_net_income_estimate,
    _promised_regions_in_terms,
    compute_concession_baseline_payload,
    compute_per_court_acceptance,
    compute_settlement_baseline,
    compute_settlement_treasury_line,
)
from backend.game_logic.settlement_routes import (
    SETTLEMENT_FAMILY_DIALOGUE_TYPES,
    _error_display,
    _mounted_settlement_dialogue,
    _normalize_nation_list,
    _terminal_recovery_copy,
    _war_label,
    evaluate_war_detail_actionability,
    mint_settlement_route_id,
)
from backend.game_logic.settlement_validation import (
    PAIR_SUBSTITUTE_DISABLED_RENDER_CODES,
    _active_cross_side_pairs,
    _blocked_payload,
    _check_gold_payment_budget_conflict,
    _has_material_concession_terms,
    _side_leader,
    _term_lists_equal,
    evaluate_liberation_eligibility,
    evaluate_open_settlement_eligibility,
    evaluate_pair_peace_substitute_eligibility,
    evaluate_subjugation_eligibility,
    evaluate_vassalage_eligibility,
    get_coverable_enemy_participants,
    validate_settlement_terms,
)


SETTLEMENT_COOLDOWN_TURNS = 3


def compute_settlement_draft_key(
    war_id: str,
    selected_target_nation: Optional[str],
    covered_enemy_participants: Optional[Iterable[str]],
) -> str:
    """Canonical scoped settlement draft key from the cleanup spec."""
    selected_key = str(selected_target_nation or "").strip() or "_none"
    covered = sorted(
        {
            str(n).strip()
            for n in (covered_enemy_participants or [])
            if str(n).strip()
        }
    )
    scope_json = json.dumps(covered, separators=(",", ":"), ensure_ascii=True)
    scope_hash = hashlib.sha256(scope_json.encode("ascii")).hexdigest()[:16]
    return f"settlement_draft:{str(war_id or '')}:{selected_key}:{scope_hash}"


def _scope_display(selected_target_nation: str, covered: Iterable[str]) -> str:
    covered_list = [str(n) for n in (covered or []) if str(n)]
    if not covered_list:
        return str(selected_target_nation or "no covered court")
    if selected_target_nation and selected_target_nation not in covered_list:
        covered_list = [selected_target_nation] + covered_list
    return ", ".join(covered_list)


def _dialogue_scope_values(dialogue: Mapping[str, Any]) -> Tuple[str, List[str]]:
    covered = _normalize_nation_list(dialogue.get("covered_enemy_participants") or [])
    selected = str(dialogue.get("selected_target_nation") or "").strip()
    if not selected and covered:
        selected = covered[0]
    return selected, covered


def _scope_changed(
    current_dialogue: Mapping[str, Any],
    *,
    incoming_selected_target: str,
    incoming_covered: Iterable[str],
) -> bool:
    current_selected, current_covered = _dialogue_scope_values(current_dialogue)
    incoming_selected = str(incoming_selected_target or "").strip()
    incoming_scope = _normalize_nation_list(incoming_covered)
    return current_selected != incoming_selected or current_covered != incoming_scope


def _settlement_collision_payload(
    *,
    error: str,
    active_war_id: str,
    incoming_war_id: str,
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "success": False,
        "error": error,
        "error_display": _error_display(error),
        "mutated": False,
        "active_war_id": active_war_id,
        "incoming_war_id": incoming_war_id,
        "collision": True,
        "talleyrand_text": resolve_settlement_voice_line(
            "settlement_collision_active_review_talleyrand",
            active_war_label=active_war_id or "the active war",
            blocked_war_label=incoming_war_id or "this war",
        ),
    }
    if extra:
        payload.update(dict(extra))
    return payload


def _build_settlement_scope_replace_confirm_dialogue(
    current_dialogue: Mapping[str, Any],
    *,
    incoming_request: Mapping[str, Any],
) -> Dict[str, Any]:
    """Build the G2e same-war different-scope replace chooser."""
    war_id = str(current_dialogue.get("war_id") or incoming_request.get("war_id") or "")
    current_selected, current_covered = _dialogue_scope_values(current_dialogue)
    incoming_covered = _normalize_nation_list(
        incoming_request.get("covered_enemy_participants") or []
    )
    incoming_selected = str(
        incoming_request.get("selected_target_nation") or ""
    ).strip() or (incoming_covered[0] if incoming_covered else "")
    current_key = str(current_dialogue.get("draft_key") or "") or compute_settlement_draft_key(
        war_id, current_selected, current_covered,
    )
    incoming_key = compute_settlement_draft_key(
        war_id, incoming_selected, incoming_covered,
    )
    current_scope_display = _scope_display(current_selected, current_covered)
    incoming_scope_display = _scope_display(incoming_selected, incoming_covered)
    war_label = str(current_dialogue.get("war_label") or war_id or "this war")
    message = resolve_settlement_voice_line(
        "settlement_scope_replace_confirm_talleyrand",
        war_label=war_label,
        current_scope=current_scope_display,
        incoming_scope=incoming_scope_display,
    ) or (
        "A different settlement scope is already staged. Replace it or keep "
        "the current draft."
    )
    return {
        "type": "settlement_scope_replace_confirm",
        "dialogue_type": "settlement_scope_replace_confirm",
        "war_id": war_id,
        "war_label": war_label,
        "current_dialogue": copy.deepcopy(dict(current_dialogue)),
        "incoming_request": copy.deepcopy(dict(incoming_request)),
        "current_draft_key": current_key,
        "incoming_draft_key": incoming_key,
        "current_scope": {
            "selected_target_nation": current_selected,
            "covered_enemy_participants": current_covered,
            "display": current_scope_display,
        },
        "incoming_scope": {
            "selected_target_nation": incoming_selected,
            "covered_enemy_participants": incoming_covered,
            "display": incoming_scope_display,
        },
        "current_scope_display": current_scope_display,
        "incoming_scope_display": incoming_scope_display,
        "available_action_ids": [
            "replace_current_scope_draft",
            "keep_current_scope_draft",
        ],
        "options": [
            {
                "label": "Replace current draft",
                "action": "replace_current_scope_draft",
                "description": (
                    "Clear the current scoped draft and stage the new scope."
                ),
            },
            {
                "label": "Keep current draft",
                "action": "keep_current_scope_draft",
                "description": "Return to the current scoped draft unchanged.",
            },
        ],
        "outer_cancel_action": "keep_current_scope_draft",
        "outer_cancel_treated_as_keep": True,
        "message": message,
        "talleyrand_text": message,
        "mutated": False,
        "blocking": True,
    }


def _build_pair_substitute_confirm_dialogue(
    current_dialogue: Mapping[str, Any],
    *,
    action: str,
    proposal_type: str,
    selected_target: str,
    eligibility: Mapping[str, Any],
) -> Dict[str, Any]:
    """G4F-8 (Gate-4 smoke) — the pair-substitute confirm chooser.

    "Make peace with {target} only" on a blocked REVIEW read as the
    system's VERDICT and one click silently discarded the authored joint
    draft, popped the settlement, and opened the bilateral engine with
    fresh terms. The substitute now mounts this chooser first: the joint
    draft is untouched until the player confirms, Cancel restores the
    REVIEW exactly (the scope-replace prior-snapshot pattern), and the
    copy states the consequence — the other courts fight on; the drafted
    terms for the target travel into the new talks.
    """
    war_id = str(current_dialogue.get("war_id") or "")
    war_label = str(current_dialogue.get("war_label") or war_id or "this war")
    arm_label = "an armistice" if proposal_type == "armistice" else "peace"
    message = resolve_settlement_voice_line(
        "settlement_pair_substitute_confirm_talleyrand",
        war_label=war_label,
        target_nation=selected_target,
    ) or (
        f"Leave the joint settlement and seek {arm_label} with "
        f"{selected_target} alone? The other courts stay at war."
    )
    return {
        "type": "settlement_pair_substitute_confirm",
        "dialogue_type": "settlement_pair_substitute_confirm",
        "war_id": war_id,
        "war_label": war_label,
        "selected_target_nation": selected_target,
        "pair_substitute_action": str(action),
        "proposal_type": str(proposal_type),
        "prior_dialogue": copy.deepcopy(dict(current_dialogue)),
        "pair_substitute_eligibility": dict(eligibility),
        "available_action_ids": [
            "confirm_pair_substitute",
            "keep_joint_settlement",
        ],
        "options": [
            {
                "label": (
                    f"Proceed — {arm_label} with {selected_target} alone"
                ),
                "action": "confirm_pair_substitute",
                "description": (
                    "Set aside the joint settlement; the other courts stay "
                    f"at war. Your drafted terms for {selected_target} "
                    "carry into the talks."
                ),
            },
            {
                "label": "Stay with the joint settlement",
                "action": "keep_joint_settlement",
                "description": "Return to the staged review unchanged.",
            },
        ],
        "outer_cancel_action": "keep_joint_settlement",
        "outer_cancel_treated_as_keep": True,
        "message": message,
        "talleyrand_text": message,
        "mutated": False,
        "blocking": True,
    }


# §3.1 / §3.3 — the two row-authoring refusal reasons, shared verbatim
# between the GT-Slice-1 add verb (server-side rejection) and the GT-Slice-2
# row payload (pre-click disabled state) so the copy can never drift.
_DEMAND_CLAUSE_CAP_REASON = (
    "The settlement already carries eight clauses, Sire — remove "
    "one before adding another."
)


def _demand_hard_stop_reason(court: str) -> str:
    return (
        f"No terms can move {court} while no live war score binds "
        "them, Sire — set that court aside instead."
    )


def _guided_magnitude_meta(clause_type: str, amount: int, turns: Optional[int]) -> Dict[str, int]:
    """Magnitude metadata for a gold line/suggestion — the bounds the
    `settlement_demand_set_magnitude` verb enforces, exposed so the row
    control renders valid ranges instead of discovering them by rejection."""
    meta: Dict[str, int] = {
        "amount": int(amount),
        "amount_min": int(
            GOLD_PER_TURN_MIN_AMOUNT if clause_type == "gold_per_turn" else 1
        ),
    }
    if clause_type == "gold_per_turn":
        meta["turns"] = int(turns or 0)
        meta["turns_min"] = int(GOLD_PER_TURN_MIN_TURNS)
        meta["turns_max"] = int(GOLD_PER_TURN_MAX_TURNS)
    return meta


def _guided_line_display(term: Mapping[str, Any], court: str) -> Tuple[str, str]:
    """One staged clause as a per-court row line: ``(direction_tag,
    line_display)`` per spec §3.1, reusing the cleanup-spec direction-tag
    vocabulary (`Demanded` / `Conceded` / `Mutual`)."""
    ttype = str(term.get("type") or "")
    frm = str(term.get("from") or "")
    amount = int(term.get("amount", 0) or 0)
    if ttype == "liberation":
        return "Demanded", f"Free {term.get('vassal_nation')}"
    if frm == court:
        tag = "Demanded"
    elif str(term.get("to") or "") == court:
        tag = "Conceded"
    else:
        tag = "Mutual"
    if ttype == "territory_cede":
        display = (
            f"Cede {term.get('region')}"
            if frm == court
            else f"{frm} cedes {term.get('region')}"
        )
    elif ttype in ("gold_indemnity", "gold_lump"):
        display = f"{amount} gold" if frm == court else f"{frm} pays {amount} gold"
    elif ttype == "gold_per_turn":
        turns = int(term.get("turns", 0) or 0)
        display = (
            f"{amount} gold a turn for {turns} turns"
            if frm == court
            else f"{frm} pays {amount} gold a turn for {turns} turns"
        )
    elif ttype == "vassalage":
        display = "Vassalage"
    elif ttype == "subjugation":
        display = "Subjugation"
    elif ttype == "forced_alliance":
        display = "Forced alliance" + (
            " (Continental System)" if term.get("includes_continental_system") else ""
        )
    else:
        display = ttype.replace("_", " ") or "Clause"
    return tag, display


def _court_current_demand_lines(
    court: str,
    settlement_terms: Iterable[Mapping[str, Any]],
    *,
    war_id: str,
    draft_key: str,
) -> List[Dict[str, Any]]:
    """Guided Terms §3.1 — ``current_demands[]`` for one covered court row.

    Each staged clause touching the court renders as a plain line with
    magnitude metadata and the per-line mutation affordances, carrying the
    EXACT ``action_params`` the GT-Slice-1 verbs accept (``clause_index`` +
    ``expected_type`` — the stale-click guard). The shared ``peace`` clause
    is not a line (it is the package, not a demand); liberation lands on
    the LORD court's row (the §4 mapping authors it there).
    """
    lines: List[Dict[str, Any]] = []
    for idx, term in enumerate(settlement_terms or []):
        if not isinstance(term, Mapping):
            continue
        ttype = str(term.get("type") or "")
        if ttype == "peace":
            continue
        touches = court in (
            str(term.get("from") or ""), str(term.get("to") or "")
        ) or (
            ttype == "liberation"
            and str(term.get("lord_nation") or "") == court
        )
        if not touches:
            continue
        direction_tag, line_display = _guided_line_display(term, court)
        entry: Dict[str, Any] = {
            "clause_index": int(idx),
            "clause_type": ttype,
            "direction_tag": direction_tag,
            "line_display": line_display,
            "authored_by": str(term.get("authored_by") or ""),
            "magnitude": None,
            "remove_action": {
                "action": "settlement_demand_remove",
                "war_id": war_id,
                "draft_key": draft_key,
                "action_params": {
                    "clause_index": int(idx),
                    "expected_type": ttype,
                },
            },
            "set_magnitude_action": None,
        }
        if ttype in ("gold_indemnity", "gold_lump", "gold_per_turn"):
            entry["magnitude"] = _guided_magnitude_meta(
                ttype,
                int(term.get("amount", 0) or 0),
                int(term.get("turns", 0) or 0) if ttype == "gold_per_turn" else None,
            )
            entry["set_magnitude_action"] = {
                "action": "settlement_demand_set_magnitude",
                "war_id": war_id,
                "draft_key": draft_key,
                "action_params": {
                    "clause_index": int(idx),
                    "expected_type": ttype,
                },
            }
        lines.append(entry)
    return lines


def _guided_suggestion(
    *,
    label: str,
    group: str,
    clause_type: str,
    reason_display: str,
    court: str,
    war_id: str,
    draft_key: str,
    params: Dict[str, Any],
    **extra: Any,
) -> Dict[str, Any]:
    """One ``demand_suggestions[]`` entry. ``action_params`` is the exact
    payload the GT-Slice-1 add verb accepts — direction is fixed per option
    by ``group`` + the court (D3/D4); no identity field ever crosses the
    transport, so France/France is structurally impossible."""
    suggestion: Dict[str, Any] = {
        "label": label,
        "group": group,
        "clause_type": clause_type,
        "reason_display": reason_display,
        "action": "settlement_demand_add",
        "war_id": war_id,
        "draft_key": draft_key,
        "action_params": {
            "nation": court,
            "group": group,
            "clause_type": clause_type,
            **params,
        },
    }
    suggestion.update(extra)
    return suggestion


def _court_demand_suggestions(
    world: Any,
    *,
    court: str,
    direction: str,
    war_id: str,
    draft_key: str,
    war_instance: Mapping[str, Any],
    proposer_side_participants: List[str],
    proposer_holdings: Set[str],
    proposer_leader: str,
    settlement_terms: List[Mapping[str, Any]],
    promised_regions: Set[str],
    treasury_remaining: int,
    income_cache: Dict[str, int],
) -> List[Dict[str, Any]]:
    """Guided Terms §3.1/§3.2/§4 — ``demand_suggestions[]`` for one court row.

    Both option groups per D4 (demands: court → France; offers/sweeteners:
    France → court), the court's direction choosing which group LEADS the
    list (§3.3 — a losing court leads with offers; the dead-band offers
    both unexpanded). Every option is fully formed, eligibility-gated, and
    TABLE-scoped valid-by-construction (§3.4): gold defaults cap at the
    shared-treasury ``remaining``, region candidates exclude promised
    regions, dependency/liberation options run their live eligibility
    evaluators before rendering. Ineligible options simply do not appear.

    ``income_cache`` memoizes the per-payer net-income estimate (§4 — one
    estimate per payer per preview, reused across options). All numerics
    ``int()`` (Golden Rule #2). ``reason_display`` resolves through the
    committed ``settlement_guided_reason_*_talleyrand`` voice families
    (GT-Slice-V — the bilateral "I suggest Silesia — {reason}" beat in
    Talleyrand's register; Voice Bible §16.1a).
    """
    if not proposer_leader:
        return []

    def _income(payer: str) -> int:
        if payer not in income_cache:
            income_cache[payer] = _payer_net_income_estimate(world, payer)
        return int(income_cache[payer])

    demand_group: List[Dict[str, Any]] = []
    offer_group: List[Dict[str, Any]] = []

    # --- Demand group (court → France), §4 listing order -----------------
    demand_regions = _demand_baseline_region_candidates(
        world,
        court=court,
        proposer_side_participants=proposer_side_participants,
        excluded_regions=promised_regions,
    )
    if demand_regions:
        region = demand_regions[0]
        region_obj = (getattr(world, "regions", None) or {}).get(region)
        adjacent = getattr(region_obj, "adjacent_regions", None) or []
        is_border = any(adj in proposer_holdings for adj in adjacent)
        reason = resolve_settlement_voice_line(
            "settlement_guided_reason_territory_demand_border_talleyrand"
            if is_border
            else "settlement_guided_reason_territory_demand_yield_talleyrand",
            region=region,
            court=court,
        )
        demand_group.append(_guided_suggestion(
            label=f"Take {region} from {court}",
            group="demand",
            clause_type="territory_cede",
            reason_display=reason,
            court=court,
            war_id=war_id,
            draft_key=draft_key,
            params={"region": region},
            region_options=[str(r) for r in demand_regions],
        ))
    court_balance = _concession_baseline_payer_balance(world, court)
    gold_demand_default = min(
        court_balance - CONCESSION_BASELINE_TREASURY_RESERVE,
        CONCESSION_BASELINE_GOLD_FLOOR,
    )
    if gold_demand_default > 0:
        demand_group.append(_guided_suggestion(
            label=f"Demand {int(gold_demand_default)} gold from {court}",
            group="demand",
            clause_type="gold_indemnity",
            reason_display=resolve_settlement_voice_line(
                "settlement_guided_reason_gold_demand_talleyrand",
                court=court,
                amount=int(gold_demand_default),
            ),
            court=court,
            war_id=war_id,
            draft_key=draft_key,
            params={"amount": int(gold_demand_default)},
            magnitude=_guided_magnitude_meta(
                "gold_indemnity", int(gold_demand_default), None
            ),
        ))
    recurring_demand = _gold_per_turn_prefill(
        world,
        payer=court,
        settlement_terms=settlement_terms,
        income_per_turn=_income(court),
    )
    if recurring_demand:
        amount = int(recurring_demand["amount"])
        turns = int(recurring_demand["turns"])
        demand_group.append(_guided_suggestion(
            label=(
                f"Demand {amount} gold a turn from {court} for {turns} turns"
            ),
            group="demand",
            clause_type="gold_per_turn",
            reason_display=resolve_settlement_voice_line(
                "settlement_guided_reason_recurring_demand_talleyrand",
                court=court,
                amount=amount,
                turns=turns,
            ),
            court=court,
            war_id=war_id,
            draft_key=draft_key,
            params={"amount": amount, "turns": turns},
            magnitude=_guided_magnitude_meta("gold_per_turn", amount, turns),
        ))
    vassalage_eligibility = evaluate_vassalage_eligibility(
        world,
        war_instance=war_instance,
        lord_nation=proposer_leader,
        target_nation=court,
    )
    if vassalage_eligibility.get("eligible"):
        power_pct = int(vassalage_eligibility.get("power_pct", 0) or 0)
        demand_group.append(_guided_suggestion(
            label=f"Vassalize {court}",
            group="demand",
            clause_type="vassalage",
            reason_display=resolve_settlement_voice_line(
                "settlement_guided_reason_vassalage_talleyrand",
                court=court,
                power_pct=power_pct,
            ),
            court=court,
            war_id=war_id,
            draft_key=draft_key,
            params={},
        ))
    subjugation_eligibility = evaluate_subjugation_eligibility(
        world,
        war_instance=war_instance,
        lord_nation=proposer_leader,
        target_nation=court,
    )
    if subjugation_eligibility.get("eligible"):
        power_pct = int(subjugation_eligibility.get("power_pct", 0) or 0)
        demand_group.append(_guided_suggestion(
            label=f"Subjugate {court}",
            group="demand",
            clause_type="subjugation",
            reason_display=resolve_settlement_voice_line(
                "settlement_guided_reason_subjugation_talleyrand",
                court=court,
                power_pct=power_pct,
            ),
            court=court,
            war_id=war_id,
            draft_key=draft_key,
            params={},
        ))
    already_allied = False
    try:
        already_allied = bool(world.are_allies(proposer_leader, court))
    except Exception:
        already_allied = False
    if not already_allied:
        demand_group.append(_guided_suggestion(
            label=f"Force {court} into alliance",
            group="demand",
            clause_type="forced_alliance",
            reason_display=resolve_settlement_voice_line(
                "settlement_guided_reason_forced_alliance_talleyrand",
                court=court,
            ),
            court=court,
            war_id=war_id,
            draft_key=draft_key,
            params={},
            supports_continental_system=True,
        ))
    vassals = getattr(world, "vassals", {}) or {}
    court_vassals = sorted(
        str(v) for v, s in vassals.items()
        if isinstance(s, Mapping)
        and str(s.get("lord") or s.get("lord_nation") or "") == court
    )
    eligible_vassals = [
        v for v in court_vassals
        if evaluate_liberation_eligibility(
            world,
            war_instance=war_instance,
            vassal_nation=v,
            lord_nation=court,
            liberator=proposer_leader,
        ).get("eligible")
    ]
    if eligible_vassals:
        vassal = eligible_vassals[0]
        demand_group.append(_guided_suggestion(
            label=f"Free {court}'s vassal {vassal}",
            group="demand",
            clause_type="liberation",
            reason_display=resolve_settlement_voice_line(
                "settlement_guided_reason_liberation_talleyrand",
                court=court,
                vassal=vassal,
            ),
            court=court,
            war_id=war_id,
            draft_key=draft_key,
            params={"vassal_nation": vassal},
            vassal_options=list(eligible_vassals),
        ))

    # --- Offer group (France → court), the D4 sweetener lever ------------
    gold_offer_default = _guided_gold_offer_default(
        world,
        proposer_side_leader=proposer_leader,
        settlement_terms=settlement_terms,
    )
    if gold_offer_default > 0:
        offer_group.append(_guided_suggestion(
            label=f"Offer {int(gold_offer_default)} gold to {court}",
            group="offer",
            clause_type="gold_indemnity",
            reason_display=resolve_settlement_voice_line(
                "settlement_guided_reason_gold_offer_talleyrand",
                court=court,
                amount=int(gold_offer_default),
            ),
            court=court,
            war_id=war_id,
            draft_key=draft_key,
            params={"amount": int(gold_offer_default)},
            magnitude=_guided_magnitude_meta(
                "gold_indemnity", int(gold_offer_default), None
            ),
        ))
    offer_regions = _concession_baseline_transferable_candidates(
        world,
        proposer_side_participants=proposer_side_participants,
        accepting_leader=court,
        excluded_regions=promised_regions,
    )
    if offer_regions:
        region = offer_regions[0]
        offer_group.append(_guided_suggestion(
            label=f"Offer {region} to {court}",
            group="offer",
            clause_type="territory_cede",
            reason_display=resolve_settlement_voice_line(
                "settlement_guided_reason_territory_offer_talleyrand",
                court=court,
                region=region,
            ),
            court=court,
            war_id=war_id,
            draft_key=draft_key,
            params={"region": region},
            region_options=[str(r) for r in offer_regions],
        ))
    recurring_offer = _gold_per_turn_prefill(
        world,
        payer=proposer_leader,
        settlement_terms=settlement_terms,
        income_per_turn=_income(proposer_leader),
        cap_total=int(treasury_remaining),
    )
    if recurring_offer:
        amount = int(recurring_offer["amount"])
        turns = int(recurring_offer["turns"])
        offer_group.append(_guided_suggestion(
            label=f"Offer {court} {amount} gold a turn for {turns} turns",
            group="offer",
            clause_type="gold_per_turn",
            reason_display=resolve_settlement_voice_line(
                "settlement_guided_reason_recurring_offer_talleyrand",
                court=court,
                amount=amount,
                turns=turns,
            ),
            court=court,
            war_id=war_id,
            draft_key=draft_key,
            params={"amount": amount, "turns": turns},
            magnitude=_guided_magnitude_meta("gold_per_turn", amount, turns),
        ))

    # §3.3 — direction picks which group LEADS the flat list; the trailing
    # group renders collapsed. The dead-band keeps the written §3.1 order
    # (demands first) with neither pre-expanded (`lead_group` stays empty).
    if direction == "concede":
        return offer_group + demand_group
    return demand_group + offer_group


def _redial_settlement_terms(
    *,
    terms: Iterable[Mapping[str, Any]],
    scope_courts: Iterable[str],
    direction: str,
    proposer_side_leader: Optional[str],
    protected_notes: Optional[List[str]] = None,
    seeded_events: Optional[List[Dict[str, str]]] = None,
    payer_gold_budgets: Optional[Mapping[str, int]] = None,
    territory_escalations: Optional[Mapping[str, Mapping[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Re-front Slice 2 / spec §11.3 + OQ#7 — apply a harsher/generous dial to
    the package slice(s) that touch ``scope_courts``, changing MAGNITUDE (gold
    amount) and COUNT (whole clauses) only — never the requested region or payer
    IDENTITY (those are Tier-3 requests).

    For a scoped court:

    - ``harsher`` presses the court: a clause it PAYS/CEDES (``from == court`` —
      a demand on it) grows by ``SETTLEMENT_DIAL_GOLD_STEP`` (gold, capped); a
      clause the proposer concedes TO it (``to == court``) shrinks by a step and
      drops at zero, and a conceded region is dropped (count down).
    - ``generous`` eases the court: the mirror — demands shrink/drop, the
      proposer's concessions grow, and a conceded-region demand is dropped.

    **Guided Terms §3.5 (dial composition rule):** the dial is a TUNING verb
    over Talleyrand-suggested lines; per-line ``Remove`` is the player's
    deletion verb. A clause tagged ``authored_by == "player"`` (hand-authored
    via the guided demand verbs, or hand-set magnitude) is therefore never
    silently DROPPED by a dial sweep: its gold shrinks toward — never past —
    the ``SETTLEMENT_DIAL_GOLD_STEP`` floor, and a territory line that the
    sweep would drop is skipped (copied through unchanged). Each protected
    line appends a player-facing note ("Your demand for Silesia stands,
    Sire.") to ``protected_notes`` when the caller supplies the collector, so
    the protection is never invisible. Untagged (suggested/seeded) clauses
    keep the full legacy semantics above.

    **Gate-4 G4F-5 (dial dead-click):** any scoped court the sweep leaves
    WITHOUT a material delta — no slice at all, only a kept territory demand,
    only identity-bearing clauses — is seeded with a single modest gold clause
    in the dial direction (press → a demand FROM the court; ease → a
    concession the proposer PAYS to it), so a dial click always moves the
    needle for every court it claims to press/ease. This applies to the
    whole-table dial and the focused dial alike (pre-G4F-5 only a focused dial
    on a clause-LESS court seeded, so "Harsher terms" on a gold-free
    multi-court table was a silent dead click — the same D3 silent-dial class
    the leg-1 fixes outlawed at the gold ceiling). Seeds stay valid by
    construction: they fire only while the package is under
    ``MAX_SETTLEMENT_CLAUSE_COUNT`` (a capped package appends a player-facing
    note instead of seeding) and only while the proposer leader is known (both
    seed shapes reference the leader; a leaderless package yields a no-op
    redraft rather than a malformed clause). A court that already drew a
    ceiling/protection note this sweep is not additionally seeded — the note
    is its feedback. Clauses that touch no scoped court — including the shared
    ``{"type": "peace"}`` — are copied through untouched.

    **Gate-4 G4F-2 (DC-1):** ``payer_gold_budgets`` (from
    ``compute_gold_payer_budgets`` — the clamp-side mirror of the SC-1/SC-33
    budget validator) bounds every gold grow at the payer's REMAINING
    capacity, consumed line by line across the sweep, and gates the focused
    seed the same way. A press at the payer's ceiling yields the unchanged
    amount plus a player-facing note ("Prussia can pay no more, Sire.")
    instead of an over-budget draft the restage validator would bounce —
    valid-by-construction applies to the system author too.

    **GT-A5 (user-approved June 11, 2026 — the OQ#7 crossing):**
    ``territory_escalations`` (court → ready territory clause, built by the
    dial handler from the SAME selectors the guided row suggestions show)
    lets a court whose gold lever is EXHAUSTED this sweep — grow at the
    budget/hard cap, or the unpressed-court seed unfundable — escalate ONCE
    into the suggested territory clause in the dial direction instead of
    merely noting (the bilateral ``modify_harsh`` round-2 ladder). The
    caller pre-applies the anti-balloon guards (one escalated territory per
    court per direction, promised-region dedupe, never vassalage-class);
    this pass honors the clause cap and records a ``territory_escalation``
    seeded event so the handler can voice the authored line. Exhausted
    courts that do not escalate keep the D3 ceiling note — never wordless.
    """
    scope = {str(n) for n in (scope_courts or []) if n}
    leader = str(proposer_side_leader or "")
    term_list = [t for t in (terms or []) if isinstance(t, Mapping)]
    out: List[Dict[str, Any]] = []
    # G4F-5: `changed` = courts that took a material delta this sweep (grown /
    # shrunk / dropped clause); `noted` = courts whose lack of movement already
    # produced a §3.5 protection note. Courts in NEITHER set (nor `ceiling`)
    # are the silent dead-click class — they get the seed below.
    # GT-A5: `ceiling` = courts whose gold lever exhausted this sweep (grow at
    # the budget/hard cap, or the seed unfundable). They escalate into their
    # suggested territory clause in the tail pass, or fall back to the D3 note.
    changed: Set[str] = set()
    noted: Set[str] = set()
    ceiling: Set[str] = set()
    remaining_budget: Optional[Dict[str, int]] = (
        dict(payer_gold_budgets) if payer_gold_budgets is not None else None
    )

    def _gold_consumption(clause: Mapping[str, Any]) -> int:
        amount = int(clause.get("amount", 0) or 0)
        if str(clause.get("type") or "") == "gold_per_turn":
            turns = int(clause.get("turns", 0) or 0)
            return abs(amount) * max(0, turns)
        return abs(amount)

    def _adjust_budget(payer: str, delta: int) -> None:
        if remaining_budget is None:
            return
        if payer in remaining_budget:
            remaining_budget[payer] -= delta

    # G4S-2 (Gate-4 1805 smoke): pre-charge EVERY existing gold line against
    # its payer's capacity up front, then adjust by DELTA as the sweep tunes
    # each line. The old consume-on-visit accounting let an early line's grow
    # overspend the budget a LATER existing line already occupied — the sweep
    # authored an over-capacity package, the restage validator bounced the
    # whole redial (discarding the ceiling notes and the GT-A5 territory
    # escalation with it), and every further dial click repeated the same
    # refusal (the 1805 leg-A dead end at 37/50). Pre-charging keeps the
    # never-bounce invariant: an exhausted gold lever now classes as
    # `ceiling` (note / escalation), never as a validator bounce.
    if remaining_budget is not None:
        for t in term_list:
            if str(t.get("type") or "") in (
                "gold_indemnity", "gold_lump", "gold_per_turn",
            ):
                _adjust_budget(str(t.get("from") or ""), _gold_consumption(t))
    notes = protected_notes if protected_notes is not None else []
    for term in term_list:
        clause = dict(term)
        ttype = str(clause.get("type") or "")
        frm = str(clause.get("from") or "")
        to = str(clause.get("to") or "")
        court = frm if frm in scope else (to if to in scope else "")
        if not court or ttype == "peace":
            out.append(clause)
            # G4S-2: out-of-scope gold lines are already pre-charged above —
            # no per-visit consumption (it would double-count).
            continue
        is_demand = frm == court  # the court pays/cedes => a demand on it
        player_authored = str(clause.get("authored_by") or "") == "player"
        if ttype in ("gold_indemnity", "gold_lump", "gold_per_turn"):
            amount = int(clause.get("amount", 0) or 0)
            original_amount = amount
            per_unit = (
                max(1, int(clause.get("turns", 0) or 0))
                if ttype == "gold_per_turn"
                else 1
            )
            # Grow on harsher-demand / generous-concession; shrink otherwise.
            if (direction == "harsher") == is_demand:
                grown = min(
                    amount + SETTLEMENT_DIAL_GOLD_STEP,
                    CONCESSION_BASELINE_GOLD_HARD_CAP,
                )
                # G4F-2 / DC-1 (+ G4S-2 delta accounting): bound the grow at
                # the payer's remaining EXTRA capacity — the whole package is
                # pre-charged, so `remaining_budget` is what the payer can
                # still add on top of every existing line — so a sweep never
                # authors a package the budget validator would bounce as
                # `gold_payment_budget_conflict`.
                if remaining_budget is not None and frm in remaining_budget:
                    extra_units = max(0, remaining_budget[frm]) // per_unit
                    if grown > amount + extra_units:
                        grown = amount + extra_units
                if grown == amount:
                    # A press at the ceiling — budget OR the 1500 hard cap —
                    # keeps the amount. GT-A5: the note is DEFERRED to the
                    # tail pass, which first tries the territory escalation
                    # and only then falls back to the D3 ceiling note (a
                    # no-op click must still never be wordless).
                    ceiling.add(court)
                amount = grown
            else:
                amount -= SETTLEMENT_DIAL_GOLD_STEP
            if amount < SETTLEMENT_DIAL_GOLD_STEP and player_authored:
                # §3.5: a player-authored gold line shrinks toward (never
                # past) the dial-step floor instead of dropping.
                clipped = max(int(clause.get("amount", 0) or 0), 0)
                amount = min(SETTLEMENT_DIAL_GOLD_STEP, clipped) or SETTLEMENT_DIAL_GOLD_STEP
                noted.add(court)
                if is_demand:
                    notes.append(
                        f"Your demand of {amount} gold from {court} stands, Sire."
                    )
                else:
                    notes.append(
                        f"Your offer of {amount} gold to {court} stands, Sire."
                    )
            elif amount <= 0:
                changed.add(court)  # the drop IS the material delta
                # G4S-2: refund the dropped line's pre-charged consumption.
                _adjust_budget(frm, -original_amount * per_unit)
                continue  # drop the clause (count down) — never below zero
            clause["amount"] = int(amount)
            if int(amount) != original_amount:
                changed.add(court)
            out.append(clause)
            # G4S-2: adjust by DELTA only — the original amount is already
            # pre-charged (a shrink refunds; a grow consumes the increase).
            _adjust_budget(frm, (int(amount) - original_amount) * per_unit)
            continue
        if ttype.startswith("territory"):
            # Territory is binary (count), never identity. Harsher keeps a
            # demand and drops a concession; generous the mirror.
            drop = (not is_demand) if direction == "harsher" else is_demand
            if drop:
                if player_authored:
                    # §3.5: the sweep skips player-authored territory lines —
                    # per-line Remove is the player's deletion verb.
                    noted.add(court)
                    region = str(clause.get("region") or "")
                    if is_demand:
                        notes.append(f"Your demand for {region} stands, Sire.")
                    else:
                        notes.append(f"Your offer of {region} stands, Sire.")
                    out.append(clause)
                    continue
                changed.add(court)  # the drop IS the material delta
                continue
            out.append(clause)
            continue
        # Identity-bearing clause types (liberation, alliance, vassalage, …) are
        # not Tier-2 magnitude levers — pass them through unchanged.
        out.append(clause)
    # G4F-5 unpressed-court seed. The sweep above only TUNES existing material
    # lines, so any scoped court it left without a delta or a note (no slice
    # at all, a kept territory demand, identity-only clauses) would make the
    # dial a silent dead click — six "Harsher terms" clicks on a gold-free
    # multi-court table changed nothing, wordlessly. Every such court now gets
    # the modest gold seed the focused dial always had (press → a demand FROM
    # the court; ease → a concession the proposer PAYS), still gated by the
    # proposer-leader guard (both seed shapes reference the leader — symmetric
    # guard) and the clause cap. A capped package appends a player-facing note
    # rather than seeding (never an over-cap draft the restage revalidation
    # would reject for ``max_clause_count_exceeded``) and never breaks
    # silently.
    if leader:
        for court in sorted(scope - changed - noted - ceiling):
            if len(out) >= MAX_SETTLEMENT_CLAUSE_COUNT:
                # Hard cap honored — no over-cap seed, but never wordless.
                notes.append("The accord can bear no further terms, Sire.")
                break
            seed_payer = court if direction == "harsher" else leader
            if (
                remaining_budget is not None
                and seed_payer in remaining_budget
                and max(0, remaining_budget[seed_payer])
                < SETTLEMENT_DIAL_GOLD_STEP
            ):
                # G4F-2: a seed the payer cannot fund is never authored for
                # the validator to bounce. GT-A5: ceiling class — the tail
                # pass escalates to territory or notes.
                ceiling.add(court)
                continue
            if direction == "harsher":
                seed = {
                    "type": "gold_indemnity", "from": court, "to": leader,
                    "amount": int(SETTLEMENT_DIAL_GOLD_STEP),
                }
                seed_group = "demand"
            else:
                seed = {
                    "type": "gold_indemnity", "from": leader, "to": court,
                    "amount": int(SETTLEMENT_DIAL_GOLD_STEP),
                }
                seed_group = "offer"
            out.append(seed)
            _adjust_budget(str(seed.get("from") or ""), _gold_consumption(seed))
            if seeded_events is not None:
                # GT-Slice-V / DC-4: the dial handler needs to know the seed
                # fired (and in which arm) so a demand seeded on a court that
                # is beating France gets Talleyrand's guard line.
                seeded_events.append({"court": court, "group": seed_group})
    # GT-A5 escalation tail (user-approved June 11, 2026). A FULLY-STUCK
    # ceiling court (no material delta anywhere in its slice) authors the
    # caller-supplied suggestion-engine territory clause in the dial
    # direction — once per court per direction; the caller's candidate map
    # already enforces that guard plus promised-region dedupe and the
    # never-vassalage-class scope. Courts that cannot escalate (no candidate,
    # cap reached, or a partial delta elsewhere in their slice) keep the D3
    # ceiling note — the click is never wordless.
    escalated: Set[str] = set()
    if leader:
        for court in sorted(ceiling - changed):
            candidate = (territory_escalations or {}).get(court)
            if not isinstance(candidate, Mapping):
                continue
            if len(out) >= MAX_SETTLEMENT_CLAUSE_COUNT:
                notes.append("The accord can bear no further terms, Sire.")
                break
            clause = dict(candidate)
            out.append(clause)
            escalated.add(court)
            if seeded_events is not None:
                seeded_events.append({
                    "court": court,
                    "group": "demand" if direction == "harsher" else "offer",
                    "kind": "territory_escalation",
                    "region": str(clause.get("region") or ""),
                })
    for court in sorted(ceiling - escalated):
        if direction == "harsher":
            notes.append(f"{court} can pay no more, Sire.")
        else:
            notes.append("The treasury can bear no more, Sire.")
    return out


def _settlement_targeted_posture_advisory(
    per_court_acceptance: Iterable[Mapping[str, Any]],
    holdout_courts: Iterable[str],
) -> str:
    """Re-front Slice 2 / OQ#1 — a VOICE-ONLY targeted-posture suggestion
    ("I'd press X and ease Y, Sire").

    Deterministic from the per-court bands: courts that already accept are
    candidates to *press* (extract more), eased-able holdouts (below threshold
    but not hard-stopped) are candidates to *ease*. This is advice only — it
    NEVER applies a dial or mutates terms; the player must click (Golden Rule
    #6). Returns "" when there is nothing to suggest.

    PF-1 / D6 guard: a CONCEDE-direction court (France losing the pair) is
    never a press candidate, whatever its band — Talleyrand does not counsel
    pressing the court that is winning.
    """
    holdout_set = {str(n) for n in (holdout_courts or [])}
    press: List[str] = []
    ease: List[str] = []
    for row in per_court_acceptance:
        if not isinstance(row, Mapping):
            continue
        nation = str(row.get("nation") or "")
        if not nation:
            continue
        if nation in holdout_set:
            if row.get("total") is not None:  # hard-stops cannot be dialed
                ease.append(nation)
        elif (
            str(row.get("band") or "") == "accept"
            and str(row.get("direction") or "") != "concede"
        ):
            press.append(nation)
    parts: List[str] = []
    if press:
        parts.append("press " + ", ".join(sorted(press)))
    if ease:
        parts.append("ease " + ", ".join(sorted(ease)))
    if not parts:
        return ""
    return "I'd " + " and ".join(parts) + ", Sire — the table is yours to shape."


def _join_court_names(names: Iterable[str]) -> str:
    """Oxford-comma join of court names for player-facing guidance copy."""
    clean = [str(n) for n in (names or []) if str(n)]
    if not clean:
        return ""
    if len(clean) == 1:
        return clean[0]
    if len(clean) == 2:
        return f"{clean[0]} and {clean[1]}"
    return ", ".join(clean[:-1]) + f", and {clean[-1]}"


def _settlement_budget_bound_constraint(
    world: Any,
    *,
    proposer_leader: str,
    per_court_acceptance: Iterable[Mapping[str, Any]],
    holdout_courts: Iterable[str],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    """PF-1 / DC-2 — detect the solvency-bound table (D5's lying hint).

    Returns ``{"budget_bound": True, "concede_holdouts": [...]}`` when at
    least one easeable holdout is a CONCEDE-direction court AND the next
    'More generous' gold step would already breach the proposer leader's
    solvency — i.e. gold escalation is exhausted, so "ease until each
    accepts" is unreachable and the honest guidance is the binding
    constraint: drop a court, or pay in land. Detection probes the REAL
    validator rule (``_check_gold_payment_budget_conflict`` with one extra
    ``SETTLEMENT_DIAL_GOLD_STEP`` clause) so the hint flips exactly when the
    dials would start failing. Deterministic, presentation-only. Returns
    ``{}`` when the constraint does not bind.
    """
    if not proposer_leader:
        return {}
    holdout_set = {str(n) for n in (holdout_courts or []) if str(n)}
    concede_holdouts = sorted(
        str(row.get("nation") or "")
        for row in (per_court_acceptance or [])
        if isinstance(row, Mapping)
        and str(row.get("nation") or "") in holdout_set
        and str(row.get("direction") or "") == "concede"
        and row.get("total") is not None
    )
    if not concede_holdouts:
        return {}
    probe_terms = [
        dict(t) for t in (settlement_terms or []) if isinstance(t, Mapping)
    ]
    probe_terms.append({
        "type": "gold_indemnity",
        "from": str(proposer_leader),
        "to": concede_holdouts[0],
        "amount": int(SETTLEMENT_DIAL_GOLD_STEP),
    })
    if _check_gold_payment_budget_conflict(world, probe_terms) is None:
        return {}
    return {"budget_bound": True, "concede_holdouts": concede_holdouts}


def _settlement_budget_bound_recommendation(
    world: Any,
    *,
    proposer_leader: str,
    per_court_acceptance: Iterable[Mapping[str, Any]],
    budget_bound_constraint: Mapping[str, Any],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Guided Terms §8 OQ-6 (GT-A2) — the deterministic cheapest-signature
    allocation rule for a budget-bound losing table.

    Triggered by the live PF-1 detector (`_settlement_budget_bound_constraint`
    — the caller gates on its ``budget_bound``). Talleyrand's recommendation
    is COMPUTED, never vibes (Golden Rule #6):

    - Rank concede-direction holdouts by ``gap_to_threshold`` ascending
      (cheapest signature first); tie-break by larger ``abs(direct_score)``,
      then lexicographic court name.
    - The allocation pool is what the proposer can pay while keeping the
      treasury reserve (``treasury − reserve`` — i.e. committed gold the
      player could re-direct plus the §3.4 ``remaining``).
    - A gap is *coverable* when one concentrated gold offer can buy it at
      the live scorer's credit rate: ``gold_needed = gap ×
      CONCESSION_GOLD_DIVISOR``, bounded by the per-term credit cap
      (``gap ≤ CONCESSION_GOLD_CAP``) and the pool walked cheapest-first.
    - The most expensive holdout is named the court to SET ASIDE (Drop) —
      Pressburg logic: buy the peace you can afford and let the dearest
      enemy fight on.

    Advice only — the player clicks; nothing here mutates the draft.
    ``recommendation_display`` is plain UI guidance (the carry-hint
    register); ``recommendation_voice`` is the GT-Slice-V in-character
    extension of ``settlement_budget_bound_constraint_talleyrand``
    (Voice Bible §16.1a), resolved from the same computed allocation.
    All numerics ``int()``.
    """
    if not (budget_bound_constraint or {}).get("budget_bound"):
        return {}
    rows_by_nation = {
        str(row.get("nation") or ""): row
        for row in (per_court_acceptance or [])
        if isinstance(row, Mapping)
    }
    ranked: List[Dict[str, Any]] = []
    for nation in budget_bound_constraint.get("concede_holdouts") or []:
        row = rows_by_nation.get(str(nation)) or {}
        total = row.get("total")
        if total is None:
            continue
        threshold = int(row.get("threshold") or ACCEPTANCE_THRESHOLD)
        gap = max(1, threshold - int(total))
        direct_score = row.get("direct_score")
        ranked.append({
            "nation": str(nation),
            "gap_to_threshold": int(gap),
            "direct_score": int(direct_score) if direct_score is not None else 0,
            "gold_needed": int(gap * CONCESSION_GOLD_DIVISOR),
            "coverable": False,
        })
    if not ranked:
        return {}
    ranked.sort(key=lambda h: (
        h["gap_to_threshold"], -abs(h["direct_score"]), h["nation"],
    ))
    treasury_line = compute_settlement_treasury_line(
        world,
        proposer_side_leader=proposer_leader,
        settlement_terms=settlement_terms,
    )
    pool = max(0, int(treasury_line["treasury"]) - int(treasury_line["reserve"]))
    pool_left = pool
    concentrate: List[str] = []
    for holdout in ranked:
        if (
            holdout["gap_to_threshold"] <= CONCESSION_GOLD_CAP
            and holdout["gold_needed"] <= pool_left
        ):
            holdout["coverable"] = True
            concentrate.append(holdout["nation"])
            pool_left -= holdout["gold_needed"]
    # Non-coverable courts are a suffix of the ascending rank (a bigger gap
    # never costs less), so the most expensive holdout is the set-aside.
    set_aside_court = ranked[-1]["nation"] if not ranked[-1]["coverable"] else ""
    if concentrate and set_aside_court:
        recommendation_display = (
            f"Concentrate the gold on {_join_court_names(concentrate)} — the "
            f"cheapest signature{'s' if len(concentrate) > 1 else ''} still "
            f"within reach — and set {set_aside_court} aside; they fight on."
        )
        recommendation_voice = resolve_settlement_voice_line(
            "settlement_budget_bound_recommendation_talleyrand",
            concentrate_names=_join_court_names(concentrate),
            set_aside_court=set_aside_court,
        )
    elif concentrate:
        recommendation_display = (
            f"Concentrate the gold on {_join_court_names(concentrate)} — the "
            "cheapest signatures still within reach."
        )
        recommendation_voice = resolve_settlement_voice_line(
            "settlement_budget_bound_recommendation_concentrate_only_talleyrand",
            concentrate_names=_join_court_names(concentrate),
        )
    else:
        recommendation_display = (
            "No gold we hold can buy these signatures. Set "
            f"{set_aside_court} aside; they fight on."
        )
        recommendation_voice = resolve_settlement_voice_line(
            "settlement_budget_bound_recommendation_set_aside_only_talleyrand",
            set_aside_court=set_aside_court,
        )
    return {
        "budget_bound": True,
        "allocation_pool": int(pool),
        "ranked_holdouts": ranked,
        "concentrate_courts": concentrate,
        "set_aside_court": set_aside_court,
        "recommendation_display": recommendation_display,
        "recommendation_voice": recommendation_voice,
    }


def _settlement_propose_carry_hint(
    holdout_courts: Iterable[str],
    per_court_acceptance: Iterable[Mapping[str, Any]],
    budget_bound_constraint: Optional[Mapping[str, Any]] = None,
) -> str:
    """Re-front UX follow-up — a plain guidance line on the PROPOSE surface
    shown ONLY while the package does not carry yet.

    A winning baseline opens as a near-acceptable DEMAND that no court accepts
    until the player eases it. Without this hint a player can Submit a
    non-carrying package straight into a blocked REVIEW with no Ratify button
    (which reads as "Submit didn't work"). This names the holdout courts and
    points at the dials. It is UI guidance, not a diplomat voice line (the
    Talleyrand table narration carries the in-character beat); returns "" when
    the package already carries / there is nothing to flag.

    PF-1 / D5 + DC-2: when ``budget_bound_constraint`` reports the treasury
    cannot raise the offer further, the generic "use 'More generous' until
    each accepts" guidance is a lie (every further gold ease would fail
    validation — D3's silent wall). The hint pivots to the binding
    constraint instead: drop a court, or pay in land via a territory offer
    on the court's row (GT-Slice-4: the guided rows replaced 'Adjust terms').
    """
    holdouts = [str(n) for n in (holdout_courts or []) if str(n)]
    if not holdouts:
        return ""
    hard_stopped = {
        str(row.get("nation") or "")
        for row in (per_court_acceptance or [])
        if isinstance(row, Mapping) and row.get("total") is None
    }
    easeable = [n for n in holdouts if n not in hard_stopped]
    names = _join_court_names(holdouts)
    if easeable and (budget_bound_constraint or {}).get("budget_bound"):
        return (
            f"{names} won't accept, and the treasury cannot raise the gold "
            "offer further. Drop a court from the table (they fight on), or "
            "add a territory offer on the court's row to pay in land instead."
        )
    if easeable:
        return (
            f"{names} won't accept these terms yet. Use 'More generous' (or ease "
            "a court) until each accepts, then 'Submit for Review' to ratify. "
            "Submitting now only opens a review you cannot ratify."
        )
    return (
        f"{names} cannot accept any terms in this settlement right now. Drop "
        f"{'them' if len(holdouts) > 1 else 'the court'} from the table, or open "
        "War Detail — submitting now only opens a review you cannot ratify."
    )


def _settlement_remaining_war_courts(
    world: Any,
    *,
    war_id: str,
    proposer_side: str,
    covered_enemy_participants: Iterable[str],
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Re-front Slice 2 / spec §11.3 — coverage-edit consequence rows.

    Returns ``(ignored_participants, remaining_wars)`` for a covered set:
    coverable enemy courts NOT in ``covered_enemy_participants`` are *ignored*
    (left out of the settlement) and stay at war — so each is also a remaining
    war pair. Both update whenever the player adds/drops coverage.
    """
    war_instance = (getattr(world, "war_instances", {}) or {}).get(war_id) or {}
    coverable = set(get_coverable_enemy_participants(war_instance, proposer_side))
    covered = {str(n) for n in (covered_enemy_participants or []) if n}
    ignored = sorted(coverable - covered)
    remaining = [
        {"enemy": nation, "war_id": war_id, "status_display": f"{nation} remains at war"}
        for nation in ignored
    ]
    return ignored, remaining


def _restage_settlement_after_redraw(
    world: Any,
    dialogue: Mapping[str, Any],
    *,
    action: str,
    new_terms: Iterable[Mapping[str, Any]],
    new_covered: Iterable[str],
    message: str,
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Re-front Slice 2 — re-preview and re-stage a PROPOSE settlement after a
    dial or coverage redraw.

    Preserves the dialogue mode (PROPOSE stays an authoring surface — never a
    hard stop), threads the prior dialogue's per-court bands as ``previous_bands``
    so each row carries the live band DELTA (presentation only — §11.2 / Golden
    Rule #6), revalidates the new package, persists the scoped draft, and
    replaces the mounted dialogue. ``extra`` is merged onto the new dialogue and
    surfaced on the result (used to carry coverage's ``ignored_participants`` /
    ``remaining_wars``).
    """
    war_id = str(dialogue.get("war_id") or "")
    proposer_side = str(dialogue.get("proposer_side") or "")
    caller_kind = str(dialogue.get("caller_kind") or SETTLEMENT_EDITOR_CALLER_KIND)
    dialogue_mode = str(dialogue.get("dialogue_mode") or "PROPOSE")
    actor = getattr(world, "player_nation", "France")
    covered = sorted({str(n) for n in (new_covered or []) if n})
    terms = [dict(t) for t in (new_terms or []) if isinstance(t, Mapping)]
    selected_target = str(dialogue.get("selected_target_nation") or "")
    if selected_target not in covered:
        selected_target = covered[0] if covered else ""
    previous_bands = {
        str(r.get("nation")): str(r.get("band"))
        for r in (dialogue.get("per_court_acceptance") or [])
        if isinstance(r, Mapping) and r.get("nation") and r.get("band")
    }
    war_instance = (getattr(world, "war_instances", {}) or {}).get(war_id) or {}
    revalidation = validate_settlement_terms(
        terms,
        proposer_side=proposer_side,
        covered_enemy_participants=covered,
        world=world,
        war_instance=war_instance,
    )
    if not revalidation.get("valid"):
        # G4F-2 residual (UX-6): this bounce should now be unreachable from
        # the budget-clamped dials, but any residual restage failure names
        # the validator's binding constraint instead of the generic
        # blame-the-player copy.
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": action,
            "war_id": war_id,
            "error": "submitted_terms_failed_revalidation",
            "error_display": str(
                revalidation.get("disabled_reason_display")
                or _error_display(str(revalidation.get("error") or ""))
                or _error_display("submitted_terms_failed_revalidation")
            ),
            "validation_error": revalidation.get("error"),
            "mutated": False,
            "suppress_proposal_result_popup": True,
        }
    preview = build_settlement_preview(
        world,
        war_id=war_id,
        proposer_side=proposer_side,
        settlement_terms=terms,
        covered_enemy_participants=covered,
        actor_nation=actor,
        ignore_active_dialogue=True,
        previous_bands=previous_bands,
    )
    if not preview.get("success"):
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": action,
            "war_id": war_id,
            "error": preview.get("error") or "settlement_redial_failed_preview",
            "error_display": preview.get("error_display") or (
                "The settlement could not be re-previewed."
            ),
            "mutated": False,
            "suppress_proposal_result_popup": True,
        }
    new_dialogue = build_settlement_confirm_dialogue(
        world,
        preview,
        selected_target_nation=selected_target or None,
        caller_kind=caller_kind,
        dialogue_mode=dialogue_mode,
    )
    if extra:
        new_dialogue.update(extra)
    # PF-2 / CH-3: the scoped store is the ONE draft store for the PROPOSE
    # authoring lifecycle (dial → suspend → reopen). The legacy war_id-keyed
    # dual-write is gone — reopen never read it, and the two-stores-one-reader
    # split is exactly what broke the "Settlement draft kept" promise (D4).
    save_scoped_settlement_draft(
        world,
        war_id=war_id,
        selected_target_nation=selected_target,
        covered_enemy_participants=covered,
        settlement_terms=terms,
    )
    world.dialogue_manager.replace(new_dialogue)
    result = {
        "success": True,
        "dialogue_type": "settlement_confirm",
        "action": action,
        "war_id": war_id,
        "diplomatic_dialogue": new_dialogue,
        "settlement_preview": preview["settlement_preview"],
        "per_court_acceptance": new_dialogue.get("per_court_acceptance"),
        "overall_acceptance": new_dialogue.get("overall_acceptance"),
        "settlement_terms": [dict(t) for t in terms],
        "awaiting_diplomatic_response": True,
        "mutated": False,
        "message": message,
        "suppress_proposal_result_popup": True,
    }
    for key in (
        "ignored_participants",
        "remaining_wars",
        "focused_court",
        "authoring_voice_beats",
    ):
        if extra and key in extra:
            result[key] = extra[key]
    return result


def build_settlement_preview(
    world: Any,
    *,
    war_id: str,
    proposer_side: Optional[str] = None,
    settlement_terms: Optional[Iterable[Mapping[str, Any]]] = None,
    covered_enemy_participants: Optional[Iterable[str]] = None,
    actor_nation: Optional[str] = None,
    density: str = "medium",
    ignore_active_dialogue: bool = False,
    generate_baseline_when_empty: bool = False,
    previous_bands: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    """Build the non-mutating settlement preview response.

    When ``generate_baseline_when_empty`` is True and no ``settlement_terms``
    are supplied, the PROPOSE landing draws a per-court Talleyrand baseline
    (``compute_settlement_baseline``) instead of an empty draft, so the
    player never faces a blank form (Re-front Slice 1 / spec §3a).
    """
    terms = [dict(t) for t in (settlement_terms or []) if isinstance(t, Mapping)]
    eligibility = evaluate_open_settlement_eligibility(
        world,
        war_id=war_id,
        actor_nation=actor_nation,
        proposer_side=proposer_side,
        ignore_active_dialogue=ignore_active_dialogue,
    )
    if not eligibility.get("available"):
        return {"success": False, **eligibility}

    instance = copy.deepcopy((getattr(world, "war_instances", {}) or {})[war_id])
    side = eligibility["proposer_side"]
    accepting_side = eligibility["accepting_side"]
    covered = sorted(
        {str(n) for n in (covered_enemy_participants or eligibility["coverable_enemy_participants"])}
    )
    accepting_leader = eligibility["accepting_leader"]
    proposer_leader = eligibility["proposer_leader"]

    baseline_generated = False
    baseline_payload: Optional[Dict[str, Any]] = None
    if generate_baseline_when_empty and not terms:
        baseline_payload = compute_settlement_baseline(
            world,
            war_id=war_id,
            war_instance=instance,
            proposer_side=side,
            accepting_side=accepting_side,
            proposer_side_leader=proposer_leader,
            covered_enemy_participants=covered,
        )
        terms = [dict(t) for t in baseline_payload.get("settlement_terms") or []]
        baseline_generated = True

    acceptance = settlement_scoring.calculate_common_peace_acceptance(
        world,
        war_id=war_id,
        war_instance=instance,
        proposer_side=side,
        accepting_side=accepting_side,
        accepting_leader=accepting_leader,
        proposer_side_leader=proposer_leader,
        covered_enemy_participants=covered,
        settlement_terms=terms,
    )

    # Severity uses the spec §16.3 line 1660 casing
    # (HARD_STOP / WARNING / INFO) so downstream `apply_warning_cap`
    # consumers do not need to defensively `.upper()` every row.
    warnings = []
    if acceptance.get("hard_stops"):
        warnings.append({
            "severity": "HARD_STOP",
            "category": "hard_stop",
            "items": list(acceptance.get("hard_stops") or []),
        })
    for item in acceptance.get("feedback") or []:
        warnings.append({
            "severity": "WARNING",
            "category": "acceptance_component",
            "component": item.get("component"),
            "value": item.get("value"),
        })

    # Re-front Slice 1 §11.2: per-court acceptance + the §11.4 carry gate.
    # Computed for every preview (PROPOSE and REVIEW) so the displayed
    # acceptance is the real gate. n=1 collapses to the single leader row.
    per_court_block = compute_per_court_acceptance(
        world,
        war_id=war_id,
        war_instance=instance,
        proposer_side=side,
        accepting_side=accepting_side,
        proposer_side_leader=proposer_leader,
        covered_enemy_participants=covered,
        settlement_terms=terms,
        previous_bands=previous_bands,
    )

    preview = {
        "war_instance": instance,
        "war_label": _war_label(war_id, instance),
        "covered_enemy_participants": covered,
        "proposer_side": side,
        "accepting_side": accepting_side,
        "proposer_side_participants": list(instance.get(side) or []),
        "accepting_side_participants": list(instance.get(accepting_side) or []),
        "standing": {},
        "settlement_terms": copy.deepcopy(terms),
        "acceptance": acceptance,
        "acceptance_components": dict(acceptance.get("components") or {}),
        "per_court_acceptance": per_court_block["per_court_acceptance"],
        "overall_acceptance": per_court_block["overall_acceptance"],
        "baseline_generated": baseline_generated,
        "baseline_per_court": (
            baseline_payload.get("per_court_baseline") if baseline_payload else {}
        ),
        "warnings": warnings,
        "density": density if density in ("compact", "medium", "verbose") else "medium",
    }
    contribution = build_contribution_share_rows(
        world, war_id, settlement_terms=terms,
    )
    review_acceptance = _enrich_acceptance_display(acceptance)
    review_acceptance.setdefault("total", acceptance.get("score", 0))
    review_acceptance.setdefault("threshold", 50)
    review_acceptance.setdefault("band", acceptance.get("verdict", "near_acceptable"))
    review_acceptance["band_display"] = acceptance_band_display(review_acceptance.get("band", ""))
    review_acceptance["band_phrase"] = acceptance_band_phrase(review_acceptance.get("band", ""))
    preview["acceptance"] = review_acceptance
    # SC-15: live awe tags + SC-16: forced-alliance threat preview
    # surfaced into review_sections at preview time (the previous
    # `awe_tags=[]` + missing threat preview meant the popup had no
    # signal until ratification fired; the popup-side "set-piece"
    # affordance was effectively dead).
    component_debug = dict(acceptance.get("component_debug") or {})
    forced_alliance_threat_preview = (
        component_debug.get("forced_alliance_threat_preview")
        if isinstance(component_debug.get("forced_alliance_threat_preview"), Mapping)
        else None
    )
    visible_enemy_nations: Set[str] = set()
    if hasattr(world, "get_visible_enemies"):
        try:
            visible_enemy_nations = {
                str(getattr(m, "nation", "") or "")
                for m in world.get_visible_enemies(getattr(world, "player_nation", "France"))
                if getattr(m, "nation", "")
            }
        except Exception:
            visible_enemy_nations = set()
    review_covered = [
        n for n in covered
        if not visible_enemy_nations or n in visible_enemy_nations
    ]
    review_allies = []
    for row in list(contribution.get("rows", [])):
        if not isinstance(row, Mapping):
            continue
        nation = str(row.get("nation") or "")
        row_side = str(row.get("side") or "")
        if row_side == side or not visible_enemy_nations or nation in visible_enemy_nations:
            review_allies.append(row)
    preview_awe_tags = detect_awe_set_pieces(
        settlement_terms=list(terms),
        participant_reactions=[],
        balance_projection=None,
        proposer_side=side,
    )
    preview["review_sections"] = build_settlement_review(
        war_id=war_id,
        war_label=preview["war_label"],
        proposer_side=side,
        accepting_side=accepting_side,
        covered_enemy_participants=review_covered,
        terms=terms,
        allies=review_allies,
        warnings=warnings,
        acceptance=review_acceptance,
        density=preview["density"],
        awe_tags=preview_awe_tags,
        forced_alliance_threat_preview=forced_alliance_threat_preview,
        world=world,
    )
    # SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1 Concession Baseline:
    # POST preview is the source of truth for `losing_for_concession_baseline`,
    # `concession_baseline_visible`, and `concession_baseline`. The dialogue
    # builder later copies these onto the staged `settlement_confirm` payload.
    # CH-4: the payload adapter rides compute_settlement_baseline — the same
    # per-court generator the PROPOSE mount uses — so the rail's seed and the
    # front door's baseline can never diverge again.
    baseline_payload = compute_concession_baseline_payload(
        world,
        war_id=war_id,
        war_instance=instance,
        proposer_side=side,
        accepting_side=accepting_side,
        proposer_side_leader=str(proposer_leader or ""),
        covered_enemy_participants=covered,
        side_pressure_score=acceptance.get("side_pressure_score"),
        near_acceptance_floor=int(
            acceptance.get("near_acceptable_threshold") or 35
        ),
    )
    preview["losing_for_concession_baseline"] = bool(
        baseline_payload.get("losing_for_concession_baseline")
    )
    preview["concession_baseline_visible"] = bool(
        baseline_payload.get("concession_baseline_visible")
    )
    preview["concession_baseline"] = baseline_payload.get("concession_baseline")
    preview["concession_baseline_reason"] = str(
        baseline_payload.get("concession_baseline_reason") or ""
    )
    # SC-31 / G2-Slice-8 - surrender preset payload mirrors the concession
    # baseline contract: POST preview is the source of truth, and the
    # staged settlement_confirm dialogue carries the same three keys at
    # the canonical position so Godot can render the EDIT-rail
    # `Author surrender terms (Talleyrand)` button without an extra
    # preview round-trip.
    surrender_payload = _compute_surrender_preset(
        world,
        war_id=war_id,
        war_instance=instance,
        proposer_side=side,
        accepting_side=accepting_side,
        accepting_leader=str(accepting_leader or ""),
        proposer_side_leader=str(proposer_leader or ""),
        covered_enemy_participants=covered,
        side_pressure_score=acceptance.get("side_pressure_score"),
    )
    preview["losing_for_surrender_preset"] = bool(
        surrender_payload.get("losing_for_surrender_preset")
    )
    preview["surrender_preset_visible"] = bool(
        surrender_payload.get("surrender_preset_visible")
    )
    preview["surrender_preset"] = surrender_payload.get("surrender_preset")
    preview["surrender_preset_reason"] = str(
        surrender_payload.get("surrender_preset_reason") or ""
    )
    recurring_gold_payload = _compute_recurring_gold_preset(
        world,
        war_instance=instance,
        proposer_side_leader=str(proposer_leader or ""),
        accepting_leader=str(accepting_leader or ""),
        covered_enemy_participants=covered,
        side_pressure_score=acceptance.get("side_pressure_score"),
    )
    preview["losing_for_recurring_gold_preset"] = bool(
        recurring_gold_payload.get("losing_for_recurring_gold_preset")
    )
    preview["recurring_gold_preset_visible"] = bool(
        recurring_gold_payload.get("recurring_gold_preset_visible")
    )
    preview["recurring_gold_preset"] = recurring_gold_payload.get(
        "recurring_gold_preset"
    )
    preview["recurring_gold_preset_reason"] = str(
        recurring_gold_payload.get("recurring_gold_preset_reason") or ""
    )
    # G2-Slice-1b-Repair-1 - per-clause Continental System toggle
    # differential. Surfaces the threat / Balance cost differential
    # between `includes_continental_system=True` and `=False` for every
    # forced_alliance clause in the draft, so the player can see the
    # imperial cost of the toggle before authoring. Empty list when no
    # forced_alliance clause is present; the staged dialogue copies the
    # field through `copy.deepcopy(preview)` in
    # `build_settlement_confirm_dialogue`.
    from backend.game_logic.settlement_scoring import (
        compute_forced_alliance_continental_toggle_differential,
    )
    preview["forced_alliance_continental_toggle_differential"] = (
        compute_forced_alliance_continental_toggle_differential(
            world, war_id=war_id, settlement_terms=terms,
        )
    )
    return {
        "success": True,
        "mode": "settlement",
        "war_id": war_id,
        "settlement_preview": preview,
        "eligibility": eligibility,
        "mutated": False,
    }


SETTLEMENT_EDITOR_CALLER_KIND = "player_editor"


def _scoped_settlement_drafts(world: Any) -> Dict[str, List[Dict[str, Any]]]:
    """Return the SC-5R scoped settlement draft store, creating it lazily.

    Storage is keyed by ``compute_settlement_draft_key(...)`` so same-war
    drafts with different ``selected_target_nation`` / covered scope do not
    collide. CH-3: this is the ONE draft store — the legacy war_id-keyed
    ``pending_settlement_drafts`` is deleted (old saves migrate on load).
    """
    drafts = getattr(world, "pending_settlement_drafts_by_key", None)
    if drafts is None:
        world.pending_settlement_drafts_by_key = {}
        drafts = world.pending_settlement_drafts_by_key
    return drafts


def save_scoped_settlement_draft(
    world: Any,
    *,
    war_id: str,
    selected_target_nation: Optional[str],
    covered_enemy_participants: Optional[Iterable[str]],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> str:
    """Persist ``settlement_terms`` under the scoped ``draft_key``.

    Returns the canonical draft_key so callers can echo it back on the
    staged dialogue. Empty / non-mapping clauses are filtered before
    storage; an explicit empty list is stored as an empty list (callers
    that want to delete the slot should remove the key directly).
    """
    drafts = _scoped_settlement_drafts(world)
    draft_key = compute_settlement_draft_key(
        war_id, selected_target_nation, covered_enemy_participants,
    )
    drafts[draft_key] = [
        dict(t) for t in (settlement_terms or []) if isinstance(t, Mapping)
    ]
    return draft_key


def load_scoped_settlement_draft(
    world: Any,
    *,
    war_id: str,
    selected_target_nation: Optional[str],
    covered_enemy_participants: Optional[Iterable[str]],
) -> Optional[List[Dict[str, Any]]]:
    """Return the scoped draft for the given war/scope, or ``None``.

    PF-2 / D4 (Gate-4 pre-flight audit): the only real reopen route — War
    Detail's "Open Settlement" — sends ``{war_id, target_nation}`` with NO
    covered list, so the exact key (which hashes the covered set) can never
    match a draft suspended under explicit coverage and "Settlement draft
    kept" was a broken promise. When the exact key misses, fall back to the
    most recently saved draft under the ``(war_id, selected_target)`` key
    prefix, then under the ``war_id`` prefix (the player's mental model of
    the promise is war-scoped). Dict insertion order makes "most recent"
    deterministic and it round-trips through save/load.
    """
    drafts = getattr(world, "pending_settlement_drafts_by_key", None)
    if not isinstance(drafts, dict):
        return None

    def _coerce(entry: Any) -> Optional[List[Dict[str, Any]]]:
        if not isinstance(entry, list):
            return None
        return [dict(t) for t in entry if isinstance(t, Mapping)]

    draft_key = compute_settlement_draft_key(
        war_id, selected_target_nation, covered_enemy_participants,
    )
    exact = _coerce(drafts.get(draft_key))
    if exact is not None:
        return exact
    war_key = str(war_id or "")
    if not war_key:
        return None
    selected_key = str(selected_target_nation or "").strip() or "_none"
    for prefix in (
        f"settlement_draft:{war_key}:{selected_key}:",
        f"settlement_draft:{war_key}:",
    ):
        matches = [
            key for key in drafts
            if isinstance(key, str) and key.startswith(prefix)
        ]
        for key in reversed(matches):
            entry = _coerce(drafts.get(key))
            if entry:
                return entry
    return None


def discard_scoped_settlement_draft(
    world: Any,
    *,
    war_id: str,
    selected_target_nation: Optional[str],
    covered_enemy_participants: Optional[Iterable[str]],
) -> bool:
    """Remove the scoped draft if it exists. Returns whether anything was removed."""
    drafts = getattr(world, "pending_settlement_drafts_by_key", None)
    if not isinstance(drafts, dict):
        return False
    draft_key = compute_settlement_draft_key(
        war_id, selected_target_nation, covered_enemy_participants,
    )
    return drafts.pop(draft_key, None) is not None


def _discard_scoped_settlement_draft_for_dialogue(
    world: Any,
    dialogue: Mapping[str, Any],
) -> bool:
    """Discard the scoped draft addressed by a staged settlement dialogue."""
    war_id = str(dialogue.get("war_id") or "")
    selected, covered = _dialogue_scope_values(dialogue)
    removed = discard_scoped_settlement_draft(
        world,
        war_id=war_id,
        selected_target_nation=selected,
        covered_enemy_participants=covered,
    )
    draft_key = str(dialogue.get("draft_key") or "")
    drafts = getattr(world, "pending_settlement_drafts_by_key", None)
    if draft_key and isinstance(drafts, dict):
        removed = drafts.pop(draft_key, None) is not None or removed
    return removed


def build_settlement_confirm_dialogue(
    world: Any,
    preview_response: Mapping[str, Any],
    *,
    selected_target_nation: Optional[str] = None,
    caller_kind: str = "player_editor",
    white_peace: bool = False,
    surrender_preset: bool = False,
    dialogue_mode: str = "REVIEW",
) -> Dict[str, Any]:
    preview = copy.deepcopy(preview_response["settlement_preview"])
    war_id = str(preview_response["war_id"])
    proposer_side = preview["proposer_side"]
    accepting_side = preview["accepting_side"]
    war_instance = preview["war_instance"]
    dialogue_mode = str(dialogue_mode or "REVIEW").upper()
    if dialogue_mode not in ("REVIEW", "PROPOSE"):
        dialogue_mode = "REVIEW"
    # Re-front Slice 1 §11.2/§11.4: the per-court acceptance block + the
    # per-covered-court carry gate. `per_court_carries` is True only when
    # every covered court is at/above threshold with no per-court hard stop;
    # it tightens (never loosens) the single-leader gate below. White peace
    # ratifies an empty package by design and stays exempt from the gate.
    per_court_acceptance = list(preview.get("per_court_acceptance") or [])
    overall_acceptance = dict(preview.get("overall_acceptance") or {})
    per_court_carries = bool(overall_acceptance.get("carries"))
    holdout_courts = list(overall_acceptance.get("holdout_courts") or [])
    leaders = {
        "attackers": war_instance.get("attacker_leader"),
        "defenders": war_instance.get("defender_leader"),
    }
    war_label = str(preview.get("war_label") or _war_label(war_id, war_instance))
    # G4F-7 (Gate-4 smoke): a multilateral settlement is labeled by its
    # COVERAGE, not the leader pair — "the settlement of France vs Britain"
    # on a Britain + Prussia table fed the "Britain-only" misreading. The
    # leader-pair `_war_label` stays for war-scoped surfaces; the SETTLEMENT
    # dialogue names every covered court. G4S-3 (1805 smoke): computed BEFORE
    # the table voice below — the narration previously resolved against the
    # leader-pair label ("this settlement of France vs Britain seats 3
    # courts") while the rest of the dialogue was already coverage-aware.
    covered_for_label = [
        str(n)
        for n in (preview.get("covered_enemy_participants") or [])
        if n
    ]
    proposer_leader_for_label = str(
        leaders.get(str(preview.get("proposer_side") or "")) or ""
    )
    if covered_for_label and proposer_leader_for_label:
        war_label = (
            f"{proposer_leader_for_label} vs {' + '.join(covered_for_label)}"
        )
    # REFRONT-V: each per-court row speaks through its NAMED diplomat (chancery
    # fallback — never an anonymous beat), and Talleyrand narrates the table.
    multi_court_voice = resolve_multi_court_settlement_voice(
        world,
        per_court_acceptance=per_court_acceptance,
        overall_acceptance=overall_acceptance,
        war_label=war_label,
    )
    _voice_by_court = {
        str(v.get("nation")): v for v in multi_court_voice.get("per_court_voice") or []
    }
    enriched_per_court: List[Dict[str, Any]] = []
    for row in per_court_acceptance:
        row = dict(row)
        voice = _voice_by_court.get(str(row.get("nation"))) or {}
        row["voice_line"] = voice.get("line", "")
        row["speaker_display"] = voice.get("speaker", "")
        enriched_per_court.append(row)
    per_court_acceptance = enriched_per_court
    multi_court_table_narration = multi_court_voice.get("table_narration", "")
    score = preview["acceptance"].get("score")
    verdict = preview["acceptance"].get("verdict")
    # SC-14c: settlement route id format is `settlement:{war_id}:{turn}:{seq}`,
    # minted from the per-(war_id, turn) `world.settlement_route_seq` counter
    # so two same-turn settlement events for one war never share a focus id.
    # Reaction event, dispatch, ledger, notification meta, and result feedback
    # all consume this staged id verbatim.
    route_id = mint_settlement_route_id(world, war_id=war_id)
    review_route = {
        "surface": "ledger_settlements",
        "review_target": "ledger_settlements",
        "route_id": route_id,
        "war_id": war_id,
    }
    # SC-3/SC-4: gate Ratify Settlement on acceptance verdict and hard stops.
    hard_stops = list(preview["acceptance"].get("hard_stops") or [])
    acceptance_threshold = preview["acceptance"].get("threshold") or preview["acceptance"].get("accept_threshold") or 50
    acceptance_score = preview["acceptance"].get("score") if preview["acceptance"].get("score") is not None else preview["acceptance"].get("total")
    # SETTLEMENT_UI_CLEANUP_SPEC v0.32 SC-5R edit contract:
    # editor-staged empty drafts with `white_peace=False` may not mint
    # Ratify regardless of acceptance verdict. They can still open the
    # EDIT editor so the player can author the first clause; the Godot
    # action rail disables Submit for Review until a non-empty package
    # exists. White-peace dialogues set the flag explicitly so the labeled
    # action can ratify an empty package. AI/system staging
    # (caller_kind != "player_editor") still respects acceptance gating only.
    staged_terms_for_gate = list(preview.get("settlement_terms") or [])
    # G4F-19: a package the player has stripped to the bare peace clause IS
    # a white peace — label and gate it like one. The typed
    # `propose_white_peace` path sets the flag explicitly; the guided rows
    # reach the same state by removing every material clause, and the old
    # flag-only read left that package unlabeled (generic heading, generic
    # ratify label, no White Peace banner).
    if (
        not white_peace
        and staged_terms_for_gate
        and all(
            isinstance(t, Mapping) and t.get("type") == "peace"
            for t in staged_terms_for_gate
        )
    ):
        white_peace = True
    empty_editor_block = (
        caller_kind == "player_editor"
        and not staged_terms_for_gate
        and not white_peace
    )
    can_ratify = (
        not hard_stops
        and verdict not in ("reject", "blocked")
        and (acceptance_score is not None and acceptance_score >= acceptance_threshold)
        and not empty_editor_block
        # Re-front §11.4: the per-covered-court gate. A multi-court settlement
        # ratifies only when EVERY covered court carries; a single holdout
        # blocks. n=1 collapses to the leader row, so this is identical to the
        # legacy single-leader gate for bilateral settlements. White peace is
        # exempt (it ratifies an empty package by design).
        and (white_peace or per_court_carries)
    )
    # SC-17 / SC-19: humanize the live-review heading. The raw verdict
    # f-string ("Acceptance: near_acceptable (49)") leaked enum strings
    # to player BBCode. Resolve through the settlement voice family so
    # the player sees acceptance band display + top-blocker phrasing,
    # never raw `near_acceptable` / `reject` / `blocked` enums.
    band_code = str(preview["acceptance"].get("band") or verdict or "near_acceptable").lower()
    band_display = acceptance_band_display(band_code) or "Under review"
    top_blocker_display = ""
    components = list(preview["acceptance"].get("top_components") or [])
    if components:
        first = components[0] if isinstance(components[0], Mapping) else {}
        top_blocker_display = str(first.get("component_display") or first.get("display") or "")
    if not top_blocker_display:
        top_blocker_display = "no single dominant pressure"
    if empty_editor_block:
        top_blocker_display = "no settlement terms authored"
    player_nation = str(getattr(world, "player_nation", "France") or "France")
    all_members = {
        str(n)
        for side_name in ("attackers", "defenders")
        for n in (war_instance.get(side_name) or [])
        if n
    }
    if player_nation not in all_members:
        if can_ratify:
            text = resolve_settlement_voice_line(
                "settlement_observed_foreign_court_chancery",
                war_label=war_label,
                accepting_leader=str(leaders.get(accepting_side) or "the accepting court"),
            ) or f"Foreign Office records the settlement of {war_label}."
        else:
            text = resolve_settlement_voice_line(
                "settlement_blocked_for_ratification_observer",
                war_label=war_label,
                top_blocker=top_blocker_display,
            ) or f"The chancery records the draft of {war_label} as blocked."
    elif white_peace and can_ratify:
        # G2-Slice-W1: labeled white-peace heading variant. Reuses
        # `settlement_review_heading_talleyrand` template if no
        # white-peace-specific family is registered, but the popup
        # already labels the action as a White Peace via `white_peace`.
        text = (
            resolve_settlement_voice_line(
                "settlement_white_peace_heading_talleyrand",
                war_label=war_label,
            )
            or f"White peace with {war_label}: no terms will be exchanged."
        )
    elif white_peace and not can_ratify:
        text = (
            resolve_settlement_voice_line(
                "settlement_white_peace_blocked_talleyrand",
                war_label=war_label,
                top_blocker=top_blocker_display,
            )
            or f"A white peace for {war_label} cannot be ratified now."
        )
    elif can_ratify:
        text = resolve_settlement_voice_line(
            "settlement_review_heading_talleyrand",
            war_label=war_label,
            acceptance_band=band_display,
            top_blocker=top_blocker_display,
        ) or f"Review the settlement of {war_label}."
    else:
        # SC-3 / SC-19 / SC-15b: when ratification is blocked, suppress
        # outgoing "Will they accept?" framing and use the blocked voice
        # family. The popup also reads `acceptance_display.band_display`
        # ("Blocked"), but the heading text still belongs to the voice
        # family rather than an inline f-string.
        text = resolve_settlement_voice_line(
            "settlement_blocked_for_ratification_talleyrand",
            war_label=war_label,
            top_blocker=top_blocker_display,
        ) or f"This settlement of {war_label} cannot be ratified now."
    covered = list(preview.get("covered_enemy_participants") or [])
    selected_target = str(selected_target_nation or "").strip()
    if selected_target and selected_target not in covered:
        raise ValueError("selected_target_not_covered")
    resolved_target = selected_target or (covered[0] if covered else "")
    war_detail_actionability = evaluate_war_detail_actionability(
        world,
        war_id=war_id,
        selected_target_nation=resolved_target,
        covered_enemy_participants=covered,
        source_route_id=route_id,
    )

    options = []
    available_action_ids = []
    staged_has_recurring_gold = any(
        isinstance(t, Mapping) and t.get("type") == "gold_per_turn"
        for t in staged_terms_for_gate
    )
    suppress_concession_baseline = bool(surrender_preset) or staged_has_recurring_gold
    concession_baseline = (
        copy.deepcopy(preview.get("concession_baseline"))
        if preview.get("concession_baseline_visible") and not suppress_concession_baseline
        else None
    )
    baseline_terms = (
        list(concession_baseline.get("terms") or [])
        if isinstance(concession_baseline, Mapping)
        else []
    )
    can_re_author_with_concessions = (
        not can_ratify
        and not suppress_concession_baseline
        and bool(preview.get("concession_baseline_visible"))
        and _has_material_concession_terms(baseline_terms)
        and not _term_lists_equal(staged_terms_for_gate, baseline_terms)
    )
    surrender_preset_payload = (
        copy.deepcopy(preview.get("surrender_preset"))
        if preview.get("surrender_preset_visible")
        else None
    )
    surrender_terms_preset = (
        list(surrender_preset_payload.get("terms") or [])
        if isinstance(surrender_preset_payload, Mapping)
        else []
    )
    can_author_surrender_terms = (
        not can_ratify
        and bool(preview.get("surrender_preset_visible"))
        and any(
            isinstance(t, Mapping) and t.get("type") in ("vassalage", "subjugation")
            for t in surrender_terms_preset
        )
        and not _term_lists_equal(staged_terms_for_gate, surrender_terms_preset)
    )
    recurring_gold_preset_payload = (
        copy.deepcopy(preview.get("recurring_gold_preset"))
        if preview.get("recurring_gold_preset_visible")
        else None
    )
    recurring_gold_terms_preset = (
        list(recurring_gold_preset_payload.get("terms") or [])
        if isinstance(recurring_gold_preset_payload, Mapping)
        else []
    )
    can_author_recurring_gold_terms = (
        not can_ratify
        and bool(preview.get("recurring_gold_preset_visible"))
        and any(
            isinstance(t, Mapping) and t.get("type") == "gold_per_turn"
            for t in recurring_gold_terms_preset
        )
        and not _term_lists_equal(staged_terms_for_gate, recurring_gold_terms_preset)
    )
    side_pressure_score = preview.get("acceptance", {}).get("side_pressure_score")
    can_author_gold_demands = (
        empty_editor_block
        and resolved_target
        and side_pressure_score is not None
        and int(side_pressure_score) >= 0
    )
    if can_ratify:
        # G4F-19: the white-peace ratify action is labeled as one.
        options.append({
            "label": "Ratify White Peace" if white_peace else "Ratify Settlement",
            "action": "confirm_settlement",
        })
        available_action_ids.append("confirm_settlement")
    elif can_re_author_with_concessions:
        options.append({
            "label": "Re-author with Concessions",
            "action": "re_author_with_concessions",
            "description": "Apply Talleyrand's concession baseline after a fresh preview.",
            "concession_baseline_preview": concession_baseline,
        })
        available_action_ids.append("re_author_with_concessions")
    if can_author_recurring_gold_terms:
        amount = int(recurring_gold_preset_payload.get("amount") or 0)
        turns = int(recurring_gold_preset_payload.get("turns") or 0)
        options.append({
            "label": "Offer Gold Over Time",
            "action": "author_recurring_gold_terms",
            "description": (
                "Apply Talleyrand's recurring-gold draft: a finite payment "
                f"of {amount} gold per turn for {turns} turns."
            ),
            "recurring_gold_preset_preview": recurring_gold_preset_payload,
        })
        available_action_ids.append("author_recurring_gold_terms")
    if can_author_gold_demands:
        options.append({
            "label": "Demand Gold",
            "action": "author_gold_indemnity_terms",
            "description": (
                f"Author a draft demanding 200 gold from {resolved_target}."
            ),
        })
        available_action_ids.append("author_gold_indemnity_terms")
        options.append({
            "label": "Demand Gold Over Time",
            "action": "author_gold_per_turn_terms",
            "description": (
                f"Author a draft demanding 50 gold per turn from {resolved_target} "
                "for 3 turns."
            ),
        })
        available_action_ids.append("author_gold_per_turn_terms")
    # SC-31 / G2-Slice-8 - Surrender preset CTA. Appears only when the
    # losing-side concession baseline predicate passes AND the surrender
    # preset can author a material dependency clause. Order matters: it
    # sits between Re-author with Concessions and Seek Bilateral Peace /
    # Seek Armistice Instead because surrender is a more drastic
    # concessionary authoring step than gold/territory concessions but
    # still narrower than abandoning the war-scoped settlement entirely.
    if can_author_surrender_terms:
        options.append({
            "label": "Author surrender terms (Talleyrand)",
            "action": "author_surrender_terms",
            "description": (
                "Apply Talleyrand's surrender preset: peace plus a dependency "
                "clause submitting to the accepting court."
            ),
            "surrender_preset_preview": surrender_preset_payload,
        })
        available_action_ids.append("author_surrender_terms")
    # Re-front UX follow-up: a blocked REVIEW is NOT a dead end. Lead the
    # blocked options with a non-destructive "Return to terms" that re-stages
    # the conversational PROPOSE surface, so the player can ease the package
    # toward carry (the winning case) or soften concessions (the losing case)
    # instead of being pushed only toward the pair-scoped escape hatches below.
    if (
        not can_ratify
        and str(caller_kind or "") == SETTLEMENT_EDITOR_CALLER_KIND
        and staged_terms_for_gate
    ):
        options.append({
            "label": "Return to terms",
            "action": "return_to_settlement_terms",
            "description": (
                "Go back to shaping the terms — ease or press each court, "
                "then submit again."
            ),
        })
        available_action_ids.append("return_to_settlement_terms")
    # SC-29 / G2-Slice-7: pair-scoped peace substitute CTAs. Only emitted
    # on blocked ratification, with a non-empty selected target, and only
    # when `evaluate_pair_peace_substitute_eligibility(...)` returns
    # eligible=True for each action. Order per failure-state table:
    # Re-author -> Revise Terms -> Return to terms -> Seek Bilateral Peace ->
    # Seek Armistice Instead -> Open War Detail -> Back Out. The labels name
    # the single covered court explicitly so the player knows these ABANDON the
    # joint settlement for one court (the source of the "only England, reject 5"
    # confusion in the Gate-4 smoke).
    if not can_ratify and resolved_target:
        actor_for_substitute = str(
            getattr(world, "player_nation", "France") or "France"
        )
        for action_id, label, voice_key, description in (
            (
                "seek_bilateral_peace",
                f"Make peace with {resolved_target} only",
                "settlement_seek_bilateral_peace_instead_talleyrand",
                f"Leave the joint settlement and make peace with {resolved_target} "
                "alone; the other courts stay at war.",
            ),
            (
                "seek_armistice_instead",
                f"Armistice with {resolved_target} only",
                "settlement_seek_armistice_instead_talleyrand",
                f"Leave the joint settlement for an armistice with {resolved_target} "
                "alone; the war continues elsewhere.",
            ),
        ):
            eligibility = evaluate_pair_peace_substitute_eligibility(
                world,
                war_id=war_id,
                actor_nation=actor_for_substitute,
                target_nation=resolved_target,
                action=action_id,
            )
            if not eligibility.get("eligible"):
                # SC-29 Disabled vs Hidden Affordance Policy, widened by
                # G4F-16: cooldown_active / already_in_armistice /
                # insufficient_resources render as a pre-click disabled
                # button WITH the reason (the live smoke could not tell why
                # the armistice arm was absent). Structural refusals still
                # hide the substitute action entirely.
                refusal_code = eligibility.get("refusal_code")
                if refusal_code in PAIR_SUBSTITUTE_DISABLED_RENDER_CODES:
                    reason_display = str(
                        eligibility.get("disabled_reason_display") or ""
                    )
                    if refusal_code == "already_in_armistice":
                        # Name the clock: how long until the truce resolves.
                        from backend.game_logic.diplomacy import (
                            ARMISTICE_DURATION,
                        )
                        pair_key = world._make_diplo_key(
                            actor_for_substitute, resolved_target
                        )
                        elapsed = int(
                            (getattr(world, "armistice_turns", {}) or {}).get(
                                pair_key, 0
                            )
                        )
                        remaining = max(0, ARMISTICE_DURATION - elapsed)
                        if remaining:
                            reason_display = (
                                f"{reason_display} It has {remaining} "
                                f"turn{'s' if remaining != 1 else ''} to run."
                            )
                    elif refusal_code == "cooldown_active":
                        # G4F sibling sweep: name THIS clock too — the bare
                        # "a cooldown is active" left the player guessing
                        # how long.
                        cooldowns = (
                            getattr(world, "player_proposal_cooldowns", {})
                            or {}
                        )
                        cd_type = (
                            "armistice"
                            if action_id == "seek_armistice_instead"
                            else "peace"
                        )
                        cd_remaining = max(
                            int(cooldowns.get(resolved_target, 0) or 0),
                            int(
                                cooldowns.get(
                                    f"{resolved_target}_{cd_type}", 0
                                )
                                or 0
                            ),
                        )
                        if cd_remaining > 0:
                            reason_display = (
                                f"{reason_display} ({cd_remaining} "
                                f"turn{'s' if cd_remaining != 1 else ''} "
                                "remaining.)"
                            )
                    options.append({
                        "label": label,
                        "action": action_id,
                        "available": False,
                        "disabled_reason_display": reason_display,
                        "scope": "selected_pair",
                        "war_id": war_id,
                        "selected_target_nation": resolved_target,
                    })
                continue
            options.append({
                "label": label,
                "action": action_id,
                "description": description,
                "scope": "selected_pair",
                "war_id": war_id,
                "selected_target_nation": resolved_target,
                "talleyrand_text": resolve_settlement_voice_line(
                    voice_key,
                    war_label=war_label or war_id or "this war",
                    target_nation=resolved_target,
                ),
                "voice_family": voice_key,
            })
            available_action_ids.append(action_id)
    if war_detail_actionability.get("actionable") and (
        not can_ratify or bool(staged_terms_for_gate)
    ):
        options.append({
            "label": "Open War Detail",
            "action": "open_war_detail",
            "description": "Return to the live war detail for this selected court.",
            "recovery_route": dict(war_detail_actionability.get("recovery_route") or {}),
        })
        available_action_ids.append("open_war_detail")
    available_action_ids.append("back_out_settlement")
    options.append({"label": "Back Out", "action": "back_out_settlement"})

    # Re-front §11.4: a holdout court is never a dead end. Each below-threshold
    # covered court ROW exposes one-click `Ease <court>` (focused More generous)
    # and `Drop <court>` (focused coverage drop) affordances — attached to the
    # per-court row, not the global rail, so the rail stays clean and the
    # affordance reads as "this court's escape." The dial / coverage HANDLERS +
    # interactive wiring land in Slice 2; Slice 1 publishes the row contract.
    settlement_draft_key_for_options = compute_settlement_draft_key(
        war_id, resolved_target, covered,
    )
    # Guided Terms §3.4 (GT-A1): ONE treasury-line computation per build,
    # shared by the payload block, the per-court suggestion defaults, and
    # the OQ-6 allocation pool. PROPOSE-only (the authoring surface).
    guided_proposer_leader = str(leaders.get(proposer_side) or "")
    guided_treasury_line: Dict[str, int] = (
        compute_settlement_treasury_line(
            world,
            proposer_side_leader=guided_proposer_leader,
            settlement_terms=staged_terms_for_gate,
        )
        if dialogue_mode == "PROPOSE"
        else {}
    )
    # GT-Slice-2: per-court demand authoring payload — suggestions, current
    # demand lines, and the row authoring state (§3.1/§3.3). PROPOSE + the
    # player editor only (the Slice-G boundary; REVIEW is a frozen
    # staged-decision surface, so its rows expose NO authoring affordances
    # — UX-2's server half).
    guided_authoring = (
        dialogue_mode == "PROPOSE"
        and str(caller_kind or "") == SETTLEMENT_EDITOR_CALLER_KIND
    )
    guided_promised_regions: Set[str] = set()
    guided_proposer_participants: List[str] = []
    guided_proposer_holdings: Set[str] = set()
    guided_income_cache: Dict[str, int] = {}
    guided_at_clause_cap = False
    if guided_authoring:
        guided_promised_regions = _promised_regions_in_terms(staged_terms_for_gate)
        guided_proposer_participants = [
            str(n) for n in (war_instance.get(proposer_side) or []) if n
        ]
        for participant in guided_proposer_participants:
            try:
                guided_proposer_holdings.update(
                    str(r) for r in world.get_nation_regions(participant)
                )
            except Exception:
                continue
        guided_at_clause_cap = (
            len(staged_terms_for_gate) >= MAX_SETTLEMENT_CLAUSE_COUNT
        )
    holdout_set = {str(n) for n in holdout_courts}
    for row in per_court_acceptance:
        court = str(row.get("nation") or "")
        is_holdout = court in holdout_set
        row["is_holdout"] = is_holdout
        # Re-front Slice-G boundary: the dial/coverage affordances are
        # player-only. A non-player (AI/system) caller never gets the
        # one-click Ease/Drop routes.
        # UX-2 (GT-Slice-3, server half): REVIEW is a staged-decision
        # surface — terms frozen, dials gone — so the per-row authoring
        # affordances attach on PROPOSE only (absent buttons by
        # construction; the blocked-REVIEW rail's `Return to terms` is the
        # route back to shaping).
        court_holdout_actions: List[Dict[str, Any]] = []
        if (
            is_holdout
            and dialogue_mode == "PROPOSE"
            and str(caller_kind or "") == SETTLEMENT_EDITOR_CALLER_KIND
        ):
            court_holdout_actions.append({
                "label": f"Ease {court}",
                "action": "settlement_dial_generous",
                "scope": court,
                "nation": court,
                "war_id": war_id,
                "draft_key": settlement_draft_key_for_options,
                "description": (
                    f"Soften terms toward {court} to bring them to the table."
                ),
            })
            # V5 coverage floor: a settlement must keep >= 1 covered court, so
            # the LAST covered court offers NO Drop (dropping it would hit the
            # floor and strand the surface — the player could otherwise drop
            # every covered court, the popup would hide on the click, and the
            # blocked drop returns no dialogue to re-show it). Ease still
            # applies to a single remaining court.
            if len(covered) > 1:
                court_holdout_actions.append({
                    "label": f"Drop {court}",
                    "action": "settlement_cover_drop",
                    "nation": court,
                    "war_id": war_id,
                    "draft_key": settlement_draft_key_for_options,
                    "description": (
                        f"Drop {court} from the settlement; they remain at war."
                    ),
                })
        row["holdout_actions"] = court_holdout_actions
        # Re-front Slice 2 / OQ#1 + §17: focused dialing ("press Prussia",
        # "ease Britain") is reached from each per-court ROW, applying the dial
        # to that one court (scope=court). Every dialable row (a real direct
        # score — not a hard stop) gets a focused `Press`; non-holdout rows also
        # get a focused `Ease` (holdout rows already expose Ease via
        # `holdout_actions`, so this avoids a duplicate). Player-only, mirroring
        # the holdout/coverage routes. A hard-stopped court cannot be dialed
        # toward acceptance, so it gets none.
        is_dialable = row.get("total") is not None and not row.get("hard_stops")
        dial_actions: List[Dict[str, Any]] = []
        if (
            is_dialable
            and dialogue_mode == "PROPOSE"
            and str(caller_kind or "") == SETTLEMENT_EDITOR_CALLER_KIND
        ):
            dial_actions.append({
                "label": f"Press {court}",
                "action": "settlement_dial_harsher",
                "scope": court,
                "nation": court,
                "war_id": war_id,
                "draft_key": settlement_draft_key_for_options,
                "description": f"Press {court} harder — applies to this court only.",
            })
            if not is_holdout:
                dial_actions.append({
                    "label": f"Ease {court}",
                    "action": "settlement_dial_generous",
                    "scope": court,
                    "nation": court,
                    "war_id": war_id,
                    "draft_key": settlement_draft_key_for_options,
                    "description": f"Ease {court} — applies to this court only.",
                })
        row["dial_actions"] = dial_actions
        # GT-Slice-2 (Guided Terms §3.1/§3.3): the per-court authoring
        # payload. Four row states: a hard-stopped court exposes NO
        # authoring (Drop only — no clause can move a total=null court); a
        # capped table disables ADD with the shared §3.1 reason but keeps
        # the current lines (Remove is the way back UNDER the cap); live
        # courts get both suggestion groups with the direction-led group
        # first + their current demand lines with mutation affordances.
        row_direction = str(row.get("direction") or "")
        if not guided_authoring:
            row["can_author"] = False
            row["lead_group"] = ""
            row["authoring_disabled_reason_display"] = ""
            row["demand_suggestions"] = []
            row["current_demands"] = []
        elif row_direction == "hard_stop":
            row["can_author"] = False
            row["lead_group"] = ""
            row["authoring_disabled_reason_display"] = _demand_hard_stop_reason(court)
            row["demand_suggestions"] = []
            row["current_demands"] = []
        else:
            lead_group = (
                "offer" if row_direction == "concede"
                else ("demand" if row_direction == "demand" else "")
            )
            row["lead_group"] = lead_group
            row["current_demands"] = _court_current_demand_lines(
                court,
                staged_terms_for_gate,
                war_id=war_id,
                draft_key=settlement_draft_key_for_options,
            )
            if guided_at_clause_cap:
                row["can_author"] = False
                row["authoring_disabled_reason_display"] = _DEMAND_CLAUSE_CAP_REASON
                row["demand_suggestions"] = []
            else:
                row["can_author"] = True
                row["authoring_disabled_reason_display"] = ""
                row["demand_suggestions"] = _court_demand_suggestions(
                    world,
                    court=court,
                    direction=row_direction,
                    war_id=war_id,
                    draft_key=settlement_draft_key_for_options,
                    war_instance=war_instance,
                    proposer_side_participants=guided_proposer_participants,
                    proposer_holdings=guided_proposer_holdings,
                    proposer_leader=guided_proposer_leader,
                    settlement_terms=staged_terms_for_gate,
                    promised_regions=guided_promised_regions,
                    treasury_remaining=int(
                        guided_treasury_line.get("remaining", 0) or 0
                    ),
                    income_cache=guided_income_cache,
                )
    if dialogue_mode == "PROPOSE" and str(caller_kind or "") == SETTLEMENT_EDITOR_CALLER_KIND:
        # PROPOSE is the conversational front: an authoring rail, not a
        # staged-decision rail. Submit for Review (-> REVIEW), Back Out. No
        # `confirm_settlement` — ratification only ever fires from REVIEW.
        # Holdout Ease/Drop and the guided demand authoring ride on the rows
        # above (GT-Slice-4: the per-court ROWS are the deep tier — the
        # freeform editor and its `adjust_terms` rail verb are retired).
        # The authoring rail is PLAYER-ONLY (Slice-G boundary): a non-player
        # PROPOSE staging keeps the default non-authoring rail (no
        # `submit_settlement_for_review` / `suspend_settlement_editor`).
        # Re-front Slice 2 / OQ#1: the whole-table intent dials are the primary
        # Tier-2 levers and lead the PROPOSE rail. They re-draft the package
        # harsher/more-generous across every covered court and re-score live;
        # focused (per-court) dialing rides on the per-court rows (Ease/press).
        options = [{
            "label": "Harsher terms",
            "action": "settlement_dial_harsher",
            "scope": "table",
            "war_id": war_id,
            "draft_key": settlement_draft_key_for_options,
            "description": "Press every court harder and watch each react live.",
        }, {
            "label": "More generous",
            "action": "settlement_dial_generous",
            "scope": "table",
            "war_id": war_id,
            "draft_key": settlement_draft_key_for_options,
            "description": "Ease every court and watch each react live.",
        }, {
            "label": "Submit for Review",
            "action": "submit_settlement_for_review",
            "description": "Lock in this package and review it for ratification.",
        }]
        available_action_ids = [
            "settlement_dial_harsher",
            "settlement_dial_generous",
            "submit_settlement_for_review",
        ]
        # PROPOSE Back Out is non-destructive (§10): it suspends the authoring
        # surface and PRESERVES the scoped draft for same-turn reopen, unlike
        # the discarding `back_out_settlement` on REVIEW.
        options.append({"label": "Back Out", "action": "suspend_settlement_editor"})
        available_action_ids.append("suspend_settlement_editor")
    ratify_blocked_reason = ""
    if empty_editor_block:
        ratify_blocked_reason = "No settlement terms have been authored."
    elif not can_ratify:
        if hard_stops:
            first_stop = hard_stops[0]
            if isinstance(first_stop, Mapping):
                ratify_blocked_reason = str(
                    first_stop.get("display")
                    or first_stop.get("detail")
                    or first_stop.get("code")
                    or ""
                )
            else:
                ratify_blocked_reason = str(first_stop or "")
        elif verdict in ("reject", "blocked") or (
            acceptance_score is not None and acceptance_score < acceptance_threshold
        ):
            ratify_blocked_reason = top_blocker_display
    review_sections_payload = copy.deepcopy(preview.get("review_sections") or {})
    if empty_editor_block:
        sections_payload = review_sections_payload.setdefault("sections", {})
        sections_payload["acceptance"] = {
            "total": None,
            "threshold": None,
            "band": "blocked",
            "band_display": "Blocked",
            "top_components": [],
            "blocker_display": ratify_blocked_reason,
        }
    # GT-Slice-4: the SC-5R EDIT payload contract (`can_edit_terms` /
    # `available_clause_types[]` / `clause_control_schema` / `editor_route`)
    # is retired with the freeform editor — the guided per-court rows are
    # the deep authoring tier and carry their own valid-by-construction
    # suggestion payloads (GT-Slice-2).
    sc5r_draft_key = compute_settlement_draft_key(war_id, resolved_target, covered)
    # PF-1 / DC-2: detect the solvency-bound table ONCE for both guidance
    # surfaces — the carry hint pivots to the binding constraint and the
    # advisory slot speaks Talleyrand's voice line for it (PROPOSE only).
    budget_bound_constraint = (
        _settlement_budget_bound_constraint(
            world,
            proposer_leader=str(leaders.get(proposer_side) or ""),
            per_court_acceptance=per_court_acceptance,
            holdout_courts=holdout_courts,
            settlement_terms=staged_terms_for_gate,
        )
        if dialogue_mode == "PROPOSE" and not per_court_carries
        else {}
    )
    budget_bound_voice = (
        resolve_settlement_voice_line(
            "settlement_budget_bound_constraint_talleyrand",
            holdout_names=_join_court_names(
                budget_bound_constraint.get("concede_holdouts") or []
            ),
        )
        if budget_bound_constraint.get("budget_bound")
        else ""
    )
    # Guided Terms §8 OQ-6 (GT-A2): the deterministic cheapest-signature
    # recommendation, computed ONCE here so the payload block and the
    # GT-Slice-V advisory voice share one allocation pass.
    budget_bound_recommendation = (
        _settlement_budget_bound_recommendation(
            world,
            proposer_leader=guided_proposer_leader,
            per_court_acceptance=per_court_acceptance,
            budget_bound_constraint=budget_bound_constraint,
            settlement_terms=staged_terms_for_gate,
        )
        if budget_bound_constraint.get("budget_bound")
        else {}
    )
    if budget_bound_voice and budget_bound_recommendation.get("recommendation_voice"):
        # GT-Slice-V — the OQ-6 recommendation extends the binding-constraint
        # line in the advisory slot: Talleyrand names the constraint, then the
        # computed allocation (advice only; the player clicks).
        budget_bound_voice = " ".join([
            budget_bound_voice,
            str(budget_bound_recommendation["recommendation_voice"]),
        ])
    return {
        "type": "settlement_confirm",
        "dialogue_type": "settlement_confirm",
        "dialogue_mode": dialogue_mode,
        # Re-front Slice 1 §11.2/§11.4: the per-court acceptance block and the
        # per-covered-court carry gate ride on every settlement_confirm
        # dialogue (PROPOSE and REVIEW) so the displayed acceptance IS the gate.
        # REFRONT-V: each per-court row carries `voice_line` + `speaker_display`
        # (named diplomat / chancery fallback); Talleyrand narrates the table.
        "per_court_acceptance": per_court_acceptance,
        "overall_acceptance": overall_acceptance,
        "multi_court_table_narration": multi_court_table_narration,
        # Re-front Slice 2 / OQ#1: a VOICE-ONLY targeted-posture recommendation
        # on the conversational PROPOSE surface ("I'd press Prussia and ease
        # Britain, Sire"). It never applies a dial — the player must click — so
        # it is empty outside PROPOSE and carries no mechanical effect.
        # PF-1 / DC-2: when the treasury binds, the advisory slot carries
        # Talleyrand's binding-constraint line instead of press/ease advice
        # (which would point at dials that can only fail validation).
        "targeted_posture_advisory": (
            (
                budget_bound_voice
                or _settlement_targeted_posture_advisory(
                    per_court_acceptance, holdout_courts
                )
            )
            if dialogue_mode == "PROPOSE"
            else ""
        ),
        # Re-front UX follow-up: a plain guidance line on PROPOSE telling the
        # player to ease the terms until every court accepts BEFORE Submit, so a
        # non-carrying package is not submitted into a blocked, no-Ratify REVIEW
        # dead-end. Empty once the package carries / outside PROPOSE. PF-1/DC-2:
        # pivots to the binding-constraint guidance when the treasury binds.
        "propose_carry_hint": (
            _settlement_propose_carry_hint(
                holdout_courts,
                per_court_acceptance,
                budget_bound_constraint=budget_bound_constraint,
            )
            if dialogue_mode == "PROPOSE" and not per_court_carries
            else ""
        ),
        # Re-front Slice 2 / OQ#2: conversational coverage prompts — one-click
        # "Bring <court> to the table" suggestions for hostile courts not yet in
        # the settlement. They write the SAME `covered_enemy_participants` state
        # as the editor checklist (no second store). PROPOSE-only and player-only.
        "coverage_add_suggestions": (
            [
                {
                    "label": f"Bring {nation} to the table",
                    "action": "settlement_cover_add",
                    "nation": nation,
                    "war_id": war_id,
                    "draft_key": settlement_draft_key_for_options,
                    "description": (
                        f"Add {nation} to this settlement and re-draft for the new set."
                    ),
                }
                for nation in sorted(
                    set(get_coverable_enemy_participants(war_instance, proposer_side))
                    - set(covered)
                )
            ]
            if dialogue_mode == "PROPOSE"
            and str(caller_kind or "") == SETTLEMENT_EDITOR_CALLER_KIND
            else []
        ),
        # Guided Terms §3.4 (GT-A1): the shared-treasury allocation block —
        # one pool across every court's France-paid gold. PROPOSE-only (the
        # authoring surface); recomputed on every restage since it derives
        # from the staged terms (computed ONCE above, shared with the
        # suggestion defaults + OQ-6 pool). All values int() (Golden Rule #2).
        "treasury_line": guided_treasury_line,
        # Guided Terms §8 OQ-6 (GT-A2): the deterministic cheapest-signature
        # recommendation for a budget-bound losing table — rank concede
        # holdouts by gap, concentrate the pool on coverable gaps, name the
        # most expensive holdout as the Drop. Advice only; the player clicks.
        # Computed once above; its GT-Slice-V `recommendation_voice` extends
        # the binding-constraint advisory line.
        "budget_bound_recommendation": budget_bound_recommendation,
        "war_id": war_id,
        "war_label": war_label,
        "route_id": route_id,
        "draft_key": sc5r_draft_key,
        "route": review_route,
        "proposer_side": proposer_side,
        "accepting_side": accepting_side,
        "staged_leaders": leaders,
        "staged_turn": int(getattr(world, "current_turn", 0) or 0),
        "settlement_terms": copy.deepcopy(preview.get("settlement_terms") or []),
        "covered_enemy_participants": covered,
        "selected_target_nation": resolved_target,
        "settlement_preview": preview,
        "acceptance_components": dict(preview.get("acceptance_components") or {}),
        "warnings": list(preview.get("warnings") or []),
        "hard_stops": hard_stops,
        "review_sections": review_sections_payload,
        "coverage_scope_display": review_sections_payload.get("coverage_scope_display", ""),
        "war_scope_display": review_sections_payload.get("war_scope_display", ""),
        "covered_enemy_display_chips": list(review_sections_payload.get("covered_enemy_display_chips") or []),
        "uncovered_enemy_display_chips": list(review_sections_payload.get("uncovered_enemy_display_chips") or []),
        "acceptance_display": review_sections_payload.get("sections", {}).get("acceptance", {}),
        "available_action_ids": available_action_ids,
        "can_ratify": can_ratify,
        "ratify_blocked_reason": ratify_blocked_reason,
        "options": options,
        "war_detail_actionability": war_detail_actionability,
        "recovery_route": dict(war_detail_actionability.get("recovery_route") or {}) if war_detail_actionability.get("actionable") else {},
        "terminal_recovery_copy": "" if war_detail_actionability.get("actionable") or can_ratify else _terminal_recovery_copy(war_id),
        "message": text,
        "talleyrand_text": text,
        "turn_created": int(getattr(world, "current_turn", 0) or 0),
        # Re-front §10: PROPOSE is an authoring surface (like EDIT) — NOT a
        # hard stop, so the player is never trapped and can end the turn from
        # it (the unsubmitted draft discards per SC-2). REVIEW stays blocking.
        "blocking": dialogue_mode != "PROPOSE",
        # SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1 propagation:
        # `caller_kind` distinguishes player-editor-staged dialogues from
        # AI/system staging so the empty-Ratify gate fires only for
        # player editor drafts. `white_peace` labels the dialogue as a
        # white-peace ratification path so the popup exempts the empty
        # draft from the editor gate and the emitted summary event tags
        # `white_peace=true`.
        "caller_kind": str(caller_kind or "player_editor"),
        "white_peace": bool(white_peace),
        # G2-Slice-W1 Concession Baseline payload is published on the
        # staged dialogue in addition to POST preview so Godot can render
        # the first-frame `Generate concession baseline (Talleyrand)`
        # button without an extra preview round trip. POST preview remains
        # the source of truth for click-time revalidation.
        "losing_for_concession_baseline": bool(
            preview.get("losing_for_concession_baseline")
        ),
        "concession_baseline_visible": bool(
            preview.get("concession_baseline_visible")
            and not suppress_concession_baseline
        ),
        "concession_baseline": concession_baseline,
        # May 24, 2026 audit punch list Tier 2: Voice Bible §16.1
        # `settlement_losing_side_pressure_explained_talleyrand` is published
        # on the staged dialogue whenever `losing_for_concession_baseline=True`,
        # so the popup can render a Talleyrand reading of the top blocker
        # (alongside the existing concession-baseline reasoning) rather than
        # forcing the player to infer the losing-side context from the
        # acceptance-band display alone. Empty string when not on the losing
        # side or no top blocker is identifiable.
        "losing_side_pressure_voice": (
            resolve_settlement_voice_line(
                "settlement_losing_side_pressure_explained_talleyrand",
                war_label=war_label,
                top_pressure_label=top_blocker_display,
                accepting_leader=str(leaders.get(accepting_side) or "the accepting court"),
            )
            if preview.get("losing_for_concession_baseline")
            else ""
        ),
        # SC-31 / G2-Slice-8 - `surrender_preset` (the bool flag) labels
        # the dialogue as a surrender-preset-authored package for banner
        # copy + emitted `settlement_summary.surrender_preset` tagging.
        # `surrender_preset_visible` / `surrender_preset` are the
        # preview-time payloads Godot reads to render the EDIT-rail CTA.
        "surrender_preset": bool(surrender_preset),
        "losing_for_surrender_preset": bool(
            preview.get("losing_for_surrender_preset")
        ),
        "surrender_preset_visible": bool(
            preview.get("surrender_preset_visible")
        ),
        "surrender_preset_payload": surrender_preset_payload,
        "surrender_preset_reason": str(preview.get("surrender_preset_reason") or ""),
        "losing_for_recurring_gold_preset": bool(
            preview.get("losing_for_recurring_gold_preset")
        ),
        "recurring_gold_preset_visible": bool(
            preview.get("recurring_gold_preset_visible")
            and not staged_has_recurring_gold
        ),
        "recurring_gold_preset_payload": (
            None if staged_has_recurring_gold else recurring_gold_preset_payload
        ),
        "recurring_gold_preset_reason": str(
            preview.get("recurring_gold_preset_reason") or ""
        ),
        # G2-Slice-1b-Repair-1: surface the per-clause Continental
        # System toggle differential at the staged dialogue's top level
        # so Godot can read it without descending into
        # `settlement_preview`. POST preview remains the source of
        # truth and is consumed for click-time revalidation when the
        # editor toggle flips.
        "forced_alliance_continental_toggle_differential": list(
            preview.get("forced_alliance_continental_toggle_differential") or []
        ),
    }


def stage_settlement_confirm(
    world: Any,
    *,
    war_id: str,
    proposer_side: Optional[str] = None,
    settlement_terms: Optional[Iterable[Mapping[str, Any]]] = None,
    covered_enemy_participants: Optional[Iterable[str]] = None,
    selected_target_nation: Optional[str] = None,
    actor_nation: Optional[str] = None,
    density: str = "medium",
    require_explicit_scope: bool = False,
    caller_kind: str = "player_editor",
    white_peace: bool = False,
    surrender_preset: bool = False,
    dialogue_mode: str = "REVIEW",
) -> Dict[str, Any]:
    war_id_str = str(war_id or "")
    dialogue_mode = str(dialogue_mode or "REVIEW").upper()
    explicit_covered = _normalize_nation_list(covered_enemy_participants)
    explicit_target = str(selected_target_nation or "").strip()
    if require_explicit_scope and not explicit_covered:
        return {"success": False, **_blocked_payload("no_covered_enemy_participants", war_id=war_id_str)}
    if require_explicit_scope and not explicit_target:
        return {"success": False, **_blocked_payload("no_selected_target_nation", war_id=war_id_str)}
    if explicit_target and explicit_covered and explicit_target not in explicit_covered:
        return {
            "success": False,
            **_blocked_payload(
                "selected_target_not_covered",
                war_id=war_id_str,
                selected_target_nation=explicit_target,
                covered_enemy_participants=explicit_covered,
            ),
        }
    # SC-26: settlement-family collision protection applied BEFORE building
    # the preview so a second settlement entry for a different war_id can't
    # mutate the staged dialogue or shift caches behind the active draft.
    is_same_war_refresh = False
    mounted = _mounted_settlement_dialogue(world)
    if mounted is not None:
        active_war_id = str(mounted.get("war_id") or "")
        if active_war_id and active_war_id != war_id_str:
            return _settlement_collision_payload(
                error="cross_war_settlement_collision",
                active_war_id=active_war_id,
                incoming_war_id=war_id_str,
                extra={
                    "dialogue_type": "settlement_confirm",
                    "war_id": war_id_str,
                    "active_dialogue_type": str(mounted.get("type") or ""),
                },
            )
        if active_war_id and active_war_id == war_id_str:
            # Same-war restage: refresh the mounted dialogue; the scoped
            # draft store keeps the refreshed terms addressable for a
            # later reopen (GT-Slice-4 §6 mounted-draft-wins semantics).
            mounted_covered = _normalize_nation_list(
                mounted.get("covered_enemy_participants") or []
            )
            incoming_covered_for_scope = (
                explicit_covered if explicit_covered else mounted_covered
            )
            # A pure reopen / same-war refresh (no explicit covered set) must
            # treat the MOUNTED scope as authoritative: the war-detail
            # "Open Settlement" always targets the war's defender leader, but
            # the player may have dropped that court from their narrowed
            # coverage. Snap an out-of-scope incoming target to the mounted
            # dialogue's target (or a covered court) instead of rejecting
            # `selected_target_not_covered` — this mirrors the dial/coverage
            # re-stage path (`_restage_settlement_after_redraw`), so reopening
            # always re-shows the in-progress settlement. An EXPLICIT scope
            # edit still validates target-in-covered below.
            mounted_target = str(mounted.get("selected_target_nation") or "")
            if explicit_covered:
                incoming_target_for_scope = (
                    explicit_target
                    or (incoming_covered_for_scope[0] if incoming_covered_for_scope else "")
                )
            elif explicit_target and explicit_target in incoming_covered_for_scope:
                incoming_target_for_scope = explicit_target
            elif mounted_target and mounted_target in incoming_covered_for_scope:
                incoming_target_for_scope = mounted_target
            else:
                incoming_target_for_scope = (
                    incoming_covered_for_scope[0] if incoming_covered_for_scope else ""
                )
            if incoming_target_for_scope and (
                incoming_target_for_scope not in incoming_covered_for_scope
            ):
                return {
                    "success": False,
                    **_blocked_payload(
                        "selected_target_not_covered",
                        war_id=war_id_str,
                        selected_target_nation=incoming_target_for_scope,
                        covered_enemy_participants=incoming_covered_for_scope,
                    ),
                }
            if _scope_changed(
                mounted,
                incoming_selected_target=incoming_target_for_scope,
                incoming_covered=incoming_covered_for_scope,
            ):
                incoming_request = {
                    "war_id": war_id_str,
                    "proposer_side": proposer_side,
                    "settlement_terms": [
                        dict(t)
                        for t in (settlement_terms or [])
                        if isinstance(t, Mapping)
                    ],
                    "covered_enemy_participants": incoming_covered_for_scope,
                    "selected_target_nation": incoming_target_for_scope,
                    "actor_nation": actor_nation,
                    "density": density,
                    "caller_kind": caller_kind,
                    "white_peace": bool(white_peace),
                    "surrender_preset": bool(surrender_preset),
                }
                replace_dialogue = _build_settlement_scope_replace_confirm_dialogue(
                    mounted,
                    incoming_request=incoming_request,
                )
                world.dialogue_manager.replace(replace_dialogue)
                return {
                    "success": True,
                    "dialogue_type": "settlement_scope_replace_confirm",
                    "war_id": war_id_str,
                    "diplomatic_dialogue": replace_dialogue,
                    "awaiting_diplomatic_response": True,
                    "mutated": False,
                    "requires_scope_replace_confirm": True,
                    "message": replace_dialogue["talleyrand_text"],
                    "suppress_proposal_result_popup": True,
                }
            # GT-Slice-4 (Guided Terms §6): there is no editor submit blob to
            # reconcile — the STAGED draft is the single source of truth. A
            # same-war same-scope refresh (War Detail reopen, wizard Open
            # Settlement) re-shows the mounted dialogue's terms; the caller's
            # terms (the scoped store's copy of the same draft) only seed an
            # empty mounted draft. The old additive merge — and its
            # `same_war_merge_conflict` dead end — retired with the editor.
            existing_terms = list(mounted.get("settlement_terms") or [])
            incoming_terms = list(settlement_terms or [])
            refreshed_terms = existing_terms if existing_terms else incoming_terms
            # SC-5R-1: persist the refreshed draft to the scoped store
            # under the incoming scope (same-war refresh adopts the
            # caller's scope when present).
            save_scoped_settlement_draft(
                world,
                war_id=war_id_str,
                selected_target_nation=incoming_target_for_scope,
                covered_enemy_participants=incoming_covered_for_scope,
                settlement_terms=refreshed_terms,
            )
            settlement_terms = refreshed_terms
            is_same_war_refresh = True
            # Same-war refresh inherits the mounted dialogue's selected
            # target/covered set when the caller did not re-author them.
            if not covered_enemy_participants:
                covered_enemy_participants = list(
                    mounted.get("covered_enemy_participants") or []
                )
            # Adopt the scope-resolved target. `incoming_target_for_scope`
            # above already snapped an out-of-scope pure-reopen target into the
            # mounted coverage; carry that through so the post-preview
            # target-in-covered guard does not re-reject the caller's original
            # (dropped) target and strand the reopen.
            _refresh_covered = _normalize_nation_list(covered_enemy_participants)
            if (not selected_target_nation) or (
                selected_target_nation not in _refresh_covered
            ):
                selected_target_nation = (
                    incoming_target_for_scope
                    or str(mounted.get("selected_target_nation") or "")
                    or None
                )
    preview = build_settlement_preview(
        world,
        war_id=war_id_str,
        proposer_side=proposer_side,
        settlement_terms=settlement_terms,
        covered_enemy_participants=covered_enemy_participants,
        actor_nation=actor_nation,
        density=density,
        ignore_active_dialogue=is_same_war_refresh,
        generate_baseline_when_empty=(dialogue_mode == "PROPOSE"),
    )
    if not preview.get("success"):
        return preview
    covered = list(preview["settlement_preview"].get("covered_enemy_participants") or [])
    resolved_target = str(selected_target_nation or "").strip() or (covered[0] if covered else "")
    if not covered:
        return {"success": False, **_blocked_payload("no_covered_enemy_participants", war_id=war_id_str)}
    if not resolved_target:
        return {"success": False, **_blocked_payload("no_selected_target_nation", war_id=war_id_str)}
    if resolved_target not in covered:
        return {
            "success": False,
            **_blocked_payload(
                "selected_target_not_covered",
                war_id=war_id_str,
                selected_target_nation=resolved_target,
                covered_enemy_participants=covered,
            ),
        }
    try:
        dialogue = build_settlement_confirm_dialogue(
            world, preview,
            selected_target_nation=resolved_target,
            caller_kind=caller_kind,
            white_peace=white_peace,
            surrender_preset=surrender_preset,
            dialogue_mode=dialogue_mode,
        )
    except ValueError as exc:
        return {"success": False, **_blocked_payload(str(exc), war_id=war_id_str)}
    _current = getattr(world.dialogue_manager, "peek", lambda: None)()
    if _current is None:
        world.dialogue_manager.replace(dialogue)
    elif (
        str(_current.get("type") or _current.get("dialogue_type") or "")
        in SETTLEMENT_FAMILY_DIALOGUE_TYPES
        and str(_current.get("war_id") or "") == war_id_str
    ):
        # LEGB-F2 (Gate-4 1805 smoke): a same-war restage REPLACES the
        # mounted settlement dialogue. Preempting re-queued the displaced
        # twin, so Back Out popped only the top copy — the stale twin then
        # resurrected the discarded draft on the next mount.
        world.dialogue_manager.replace(dialogue)
    elif hasattr(world.dialogue_manager, "preempt"):
        world.dialogue_manager.preempt(dialogue)
    else:
        world.dialogue_manager.replace(dialogue)
    ally_petitions: List[Dict[str, Any]] = []
    if caller_kind == "player_editor":
        # Function-level import: the petition family lives in the offers layer
        # above staging (CH-1 documented lazy edge — the established
        # settlement cycle-break pattern).
        from backend.game_logic.settlement_offers import (
            build_ally_settlement_petition_popup,
            queue_ally_settlement_petitions_for_player_action,
        )
        staged_terms_source = dialogue.get("settlement_terms") or settlement_terms or []
        terms_for_trigger = [
            dict(term)
            for term in staged_terms_source
            if isinstance(term, Mapping)
        ]
        if terms_for_trigger or white_peace:
            petition_trigger = "stage_settlement"
        else:
            petition_trigger = "open_settlement"
        ally_petitions = queue_ally_settlement_petitions_for_player_action(
            world,
            trigger_action=petition_trigger,
            war_id=war_id_str,
            covered_enemy_participants=covered,
            settlement_terms=terms_for_trigger,
        )
        if ally_petitions:
            dialogue["ally_petitions"] = [
                build_ally_settlement_petition_popup(petition)
                for petition in ally_petitions
            ]
    return {
        "success": True,
        "dialogue_type": "settlement_confirm",
        "war_id": war_id_str,
        "diplomatic_dialogue": dialogue,
        "settlement_preview": preview["settlement_preview"],
        "ally_settlement_petitions": [
            copy.deepcopy(petition) for petition in ally_petitions
        ],
        "awaiting_diplomatic_response": True,
        "mutated": False,
        "message": dialogue["talleyrand_text"],
    }


def revalidate_staged_settlement(world: Any, dialogue: Mapping[str, Any]) -> Dict[str, Any]:
    """Live-state validation for staged settlement_confirm before mutation."""
    war_id = str(dialogue.get("war_id") or "")
    instance = (getattr(world, "war_instances", {}) or {}).get(war_id)
    if not instance or instance.get("ended_turn") is not None:
        return {"ok": False, "error": "inactive_war_instance"}
    proposer_side = str(dialogue.get("proposer_side") or "")
    accepting_side = str(dialogue.get("accepting_side") or "")
    staged_leaders = dialogue.get("staged_leaders") or {}
    if _side_leader(instance, proposer_side) != staged_leaders.get(proposer_side):
        return {"ok": False, "error": "proposer_leader_changed", "must_reopen": True}

    active_pairs = set(_active_cross_side_pairs(instance, proposer_side))
    meta = instance.get("diplo_key_meta") or {}
    proposers = set(instance.get(proposer_side) or [])
    covered = set(dialogue.get("covered_enemy_participants") or [])
    for pair in dialogue.get("settlement_preview", {}).get("war_instance", {}).get("active_diplo_keys", []) or []:
        pair_meta = meta.get(pair) or {}
        if pair not in active_pairs or pair_meta.get("pair_status") not in ("war", "armistice"):
            return {"ok": False, "error": "active_pair_changed", "must_reopen": True}
    if not covered:
        return {"ok": False, "error": "no_covered_enemy_participants", "must_reopen": True}
    if not proposers:
        return {"ok": False, "error": "active_participant_changed", "must_reopen": True}
    return {
        "ok": True,
        "war_id": war_id,
        "proposer_side": proposer_side,
        "accepting_side": accepting_side,
    }
