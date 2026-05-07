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
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Tuple

from backend.display_names import (
    SETTLEMENT_DISABLED_REASON_DISPLAY,
    acceptance_band_display,
    acceptance_band_phrase,
    acceptance_component_display,
    settlement_disabled_reason_display,
)
from backend.game_logic.diplomatic_templates import calculate_treaty_harshness
from backend.game_logic.settlement_scoring import (
    calculate_common_peace_acceptance,
    CANONICAL_CLAUSE_TYPES,
    CLAUSE_CONFLICT_MATRIX,
    MAX_SETTLEMENT_CLAUSE_COUNT,
    SETTLEMENT_HARD_STOP_CODES,
    SETTLEMENT_MVP_CLAUSE_TYPES,
)
from backend.game_logic.settlement_presentation import (
    build_contribution_share_rows,
    build_settlement_review,
)


VALID_SIDES = {"attackers", "defenders"}
SETTLEMENT_COOLDOWN_TURNS = 3

SETTLEMENT_ERROR_DISPLAY = SETTLEMENT_DISABLED_REASON_DISPLAY


def _error_display(code: str) -> str:
    return settlement_disabled_reason_display(code)


def _blocked_payload(code: str, **extra: Any) -> Dict[str, Any]:
    display = _error_display(code)
    return {
        "available": False,
        "error": code,
        "error_display": display,
        "disabled_reason_display": display,
        "display_reason": display,
        **extra,
    }


def _enrich_acceptance_display(acceptance: Mapping[str, Any]) -> Dict[str, Any]:
    enriched = dict(acceptance or {})
    band = str(enriched.get("band") or enriched.get("verdict") or "")
    enriched["band"] = band
    enriched["band_display"] = acceptance_band_display(band)
    enriched["band_phrase"] = acceptance_band_phrase(band)
    top_components = []
    for item in enriched.get("feedback") or []:
        if not isinstance(item, Mapping):
            continue
        component = str(item.get("component") or "")
        value = item.get("value")
        top_components.append({
            **dict(item),
            "component_display": acceptance_component_display(component),
            "value_display": f"{int(value):+d}" if isinstance(value, (int, float)) else str(value or ""),
        })
    enriched["top_components"] = top_components[:3]
    if top_components:
        enriched["top_blocker_display"] = top_components[0]["component_display"]
        enriched["top_blocker_value_display"] = top_components[0]["value_display"]
    return enriched


def _war_label(war_id: str, war_instance: Mapping[str, Any]) -> str:
    attackers = list(war_instance.get("attackers") or [])
    defenders = list(war_instance.get("defenders") or [])
    if attackers and defenders:
        return f"{attackers[0]} vs {defenders[0]}"
    return war_id or "Settlement"


def _reopen_target(war_id: str, dialogue: Mapping[str, Any]) -> Dict[str, Any]:
    preview = dialogue.get("settlement_preview") or {}
    covered = list(dialogue.get("covered_enemy_participants") or preview.get("covered_enemy_participants") or [])
    selected = str(dialogue.get("selected_target_nation") or "")
    if not selected and covered:
        selected = covered[0]
    diagnostic_fallback = not bool(dialogue.get("selected_target_nation"))
    result: Dict[str, Any] = {
        "surface": "settlement_review",
        "target": "settlement_review",
        "war_id": war_id,
        "nation": selected,
        "target_nation": selected,
        "proposer_side": str(dialogue.get("proposer_side") or preview.get("proposer_side") or ""),
    }
    if diagnostic_fallback and selected:
        result["diagnostic_fallback_target"] = True
        result["error_display"] = "This settlement lost its selected court. Reopen from war detail."
    return result


def _normalize_nation_list(values: Optional[Iterable[str]]) -> List[str]:
    if values is None:
        return []
    return sorted({str(value) for value in values if str(value or "").strip()})


def _other_side(side: str) -> str:
    return "defenders" if side == "attackers" else "attackers"


def _allocate_settlement_route_id(world: Any, war_id: str) -> str:
    """Allocate a same-turn unique settlement route id for a staged dialogue."""
    turn = int(getattr(world, "current_turn", 0) or 0)
    route_seq = getattr(world, "settlement_route_seq", None)
    if not isinstance(route_seq, dict):
        return f"{war_id}:{turn}:1"
    per_war = route_seq.setdefault(str(war_id), {})
    last_seq = int(per_war.get(turn, 0) or 0)
    next_seq = last_seq + 1
    per_war[turn] = next_seq
    return f"{war_id}:{turn}:{next_seq}"


def _side_leader(war_instance: Mapping[str, Any], side: str) -> Optional[str]:
    if side == "attackers":
        return war_instance.get("attacker_leader")
    if side == "defenders":
        return war_instance.get("defender_leader")
    return None


def _pair_nations(pair: str) -> List[str]:
    return [p for p in str(pair).split("|") if p]


def _active_cross_side_pairs(
    war_instance: Mapping[str, Any],
    proposer_side: str,
) -> List[str]:
    proposers = set(war_instance.get(proposer_side) or [])
    enemies = set(war_instance.get(_other_side(proposer_side)) or [])
    meta = war_instance.get("diplo_key_meta") or {}
    pairs: List[str] = []
    for pair in war_instance.get("active_diplo_keys") or []:
        pair_meta = meta.get(pair) or {}
        if pair_meta.get("pair_status") not in ("war", "armistice"):
            continue
        nations = _pair_nations(pair)
        if len(nations) != 2:
            continue
        a, b = nations
        if (a in proposers and b in enemies) or (b in proposers and a in enemies):
            pairs.append(pair)
    return sorted(pairs)


def _settlement_dialogue_active(world: Any, war_id: str) -> bool:
    current = getattr(world, "pending_diplomatic_dialogue", None)
    queued = list(getattr(getattr(world, "dialogue_manager", None), "_queue", []) or [])
    for dialogue in ([current] if current else []) + queued:
        if not isinstance(dialogue, Mapping):
            continue
        if dialogue.get("type") not in ("settlement_confirm", "incoming_settlement_offer"):
            continue
        if str(dialogue.get("war_id") or "") == str(war_id):
            return True
    return False


def _infer_actor_side(
    war_instance: Mapping[str, Any],
    actor_nation: str,
    proposer_side: Optional[str],
) -> Optional[str]:
    if proposer_side in VALID_SIDES:
        return proposer_side
    side_by_nation = war_instance.get("side_by_nation") or {}
    side = side_by_nation.get(actor_nation)
    if side in VALID_SIDES:
        return side
    for candidate in ("attackers", "defenders"):
        if actor_nation in (war_instance.get(candidate) or []):
            return candidate
    return None


def get_coverable_enemy_participants(
    war_instance: Mapping[str, Any],
    proposer_side: str,
) -> List[str]:
    """Return opposing-side participants with active unresolved cross-pairs."""
    accepting_side = _other_side(proposer_side)
    enemies = set(war_instance.get(accepting_side) or [])
    pairs = _active_cross_side_pairs(war_instance, proposer_side)
    coverable = set()
    for pair in pairs:
        for nation in _pair_nations(pair):
            if nation in enemies:
                coverable.add(nation)
    leader = _side_leader(war_instance, accepting_side)
    if leader in enemies:
        coverable.add(str(leader))
    return sorted(coverable)


def is_common_settlement_worth_showing(war_instance: Mapping[str, Any]) -> bool:
    """Return True when common peace adds value over bilateral peace."""
    if not isinstance(war_instance, Mapping):
        return False
    attackers = list(war_instance.get("attackers") or [])
    defenders = list(war_instance.get("defenders") or [])
    return len(set(attackers + defenders)) > 2


def evaluate_open_settlement_eligibility(
    world: Any,
    *,
    war_id: str,
    actor_nation: Optional[str] = None,
    proposer_side: Optional[str] = None,
    ignore_active_dialogue: bool = False,
) -> Dict[str, Any]:
    """Spec §10.3 Open Settlement eligibility / grey-out rules."""
    actor = actor_nation or getattr(world, "player_nation", "France")
    instance = (getattr(world, "war_instances", {}) or {}).get(war_id)
    if not instance:
        return _blocked_payload("invalid_war_id", war_id=war_id)
    if instance.get("ended_turn") is not None:
        return _blocked_payload("inactive_war_instance", war_id=war_id)
    if not is_common_settlement_worth_showing(instance):
        return _blocked_payload("one_to_one_war", war_id=war_id)

    side = _infer_actor_side(instance, actor, proposer_side)
    if side not in VALID_SIDES:
        return _blocked_payload("not_side_leader", war_id=war_id)
    if _side_leader(instance, side) != actor:
        return _blocked_payload("not_side_leader", war_id=war_id, proposer_side=side)

    pairs = _active_cross_side_pairs(instance, side)
    if not pairs:
        return _blocked_payload("no_unresolved_hostile_pairs", war_id=war_id, proposer_side=side)
    if len(pairs) == 1:
        return _blocked_payload("one_to_one_war", war_id=war_id, proposer_side=side)

    coverable = get_coverable_enemy_participants(instance, side)
    if not coverable:
        return _blocked_payload("no_coverable_enemy", war_id=war_id, proposer_side=side)

    if not ignore_active_dialogue and _settlement_dialogue_active(world, war_id):
        return _blocked_payload("settlement_dialogue_active", war_id=war_id, proposer_side=side)

    accepting_side = _other_side(side)
    return {
        "available": True,
        "war_id": war_id,
        "proposer_side": side,
        "accepting_side": accepting_side,
        "proposer_leader": _side_leader(instance, side),
        "accepting_leader": _side_leader(instance, accepting_side),
        "active_diplo_keys": pairs,
        "coverable_enemy_participants": coverable,
    }


def validate_settlement_terms(
    terms: List[Dict[str, Any]],
    *,
    actor_nation: Optional[str] = None,
    player_nation: Optional[str] = None,
    proposer_side: Optional[str] = None,
    actor_side_in_war: Optional[str] = None,
) -> Dict[str, Any]:
    """SC-1 POST preview clause validation.

    Returns {"valid": True} or {"valid": False, "error": ..., "error_index": ...,
    "disabled_reason_display": ...}.
    """
    if actor_nation and player_nation and actor_nation != player_nation:
        return {
            "valid": False,
            "error": "unauthorized_actor",
            "disabled_reason_display": _error_display("unauthorized_actor"),
        }
    if proposer_side and actor_side_in_war and proposer_side != actor_side_in_war:
        return {
            "valid": False,
            "error": "proposer_side_mismatch",
            "disabled_reason_display": _error_display("proposer_side_mismatch"),
        }
    if not isinstance(terms, list):
        return {
            "valid": False,
            "error": "invalid_clause_schema",
            "disabled_reason_display": _error_display("invalid_clause_schema"),
        }
    if not terms:
        return {
            "valid": False,
            "error": "empty_authored_draft",
            "disabled_reason_display": _error_display("empty_authored_draft"),
        }
    if len(terms) > MAX_SETTLEMENT_CLAUSE_COUNT:
        return {
            "valid": False,
            "error": "max_clause_count_exceeded",
            "error_index": MAX_SETTLEMENT_CLAUSE_COUNT,
            "disabled_reason_display": _error_display("max_clause_count_exceeded"),
        }
    for idx, clause in enumerate(terms):
        if not isinstance(clause, Mapping):
            return {
                "valid": False,
                "error": "invalid_clause_schema",
                "error_index": idx,
                "disabled_reason_display": _error_display("invalid_clause_schema"),
            }
        ctype = clause.get("type")
        if ctype not in CANONICAL_CLAUSE_TYPES:
            return {
                "valid": False,
                "error": "invalid_clause_type",
                "error_index": idx,
                "disabled_reason_display": _error_display("invalid_clause_type"),
            }
        spec = CANONICAL_CLAUSE_TYPES[ctype]
        required = set(spec["required"])
        optional = set(spec.get("optional") or set())
        clause_keys = set(clause.keys())
        missing = required - clause_keys
        if missing:
            return {
                "valid": False,
                "error": "invalid_clause_schema",
                "error_index": idx,
                "missing_keys": sorted(missing),
                "disabled_reason_display": _error_display("invalid_clause_schema"),
            }
        unknown = clause_keys - required - optional
        if unknown:
            return {
                "valid": False,
                "error": "invalid_clause_schema",
                "error_index": idx,
                "unknown_keys": sorted(unknown),
                "disabled_reason_display": _error_display("invalid_clause_schema"),
            }
    for type_a, type_b, match_keys in CLAUSE_CONFLICT_MATRIX:
        clauses_a = [c for c in terms if c.get("type") == type_a]
        clauses_b = [c for c in terms if c.get("type") == type_b]
        for ca in clauses_a:
            for cb in clauses_b:
                if all(ca.get(k) == cb.get(k) for k in match_keys):
                    return {
                        "valid": False,
                        "error": "duplicate_or_conflicting_clauses",
                        "error_index": terms.index(cb),
                        "disabled_reason_display": _error_display("duplicate_or_conflicting_clauses"),
                    }
    return {"valid": True}


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
) -> Dict[str, Any]:
    """Build the non-mutating settlement preview response."""
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
    covered = _normalize_nation_list(
        covered_enemy_participants or eligibility["coverable_enemy_participants"]
    )
    accepting_leader = eligibility["accepting_leader"]
    proposer_leader = eligibility["proposer_leader"]

    acceptance = calculate_common_peace_acceptance(
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
    preview["review_sections"] = build_settlement_review(
        war_id=war_id,
        war_label=preview["war_label"],
        proposer_side=side,
        accepting_side=accepting_side,
        covered_enemy_participants=covered,
        terms=terms,
        allies=list(contribution.get("rows", [])),
        warnings=warnings,
        acceptance=review_acceptance,
        density=preview["density"],
        awe_tags=[],
    )
    return {
        "success": True,
        "mode": "settlement",
        "war_id": war_id,
        "settlement_preview": preview,
        "eligibility": eligibility,
        "mutated": False,
    }


def build_settlement_confirm_dialogue(
    world: Any,
    preview_response: Mapping[str, Any],
    *,
    selected_target_nation: Optional[str] = None,
) -> Dict[str, Any]:
    preview = copy.deepcopy(preview_response["settlement_preview"])
    war_id = str(preview_response["war_id"])
    proposer_side = preview["proposer_side"]
    accepting_side = preview["accepting_side"]
    war_instance = preview["war_instance"]
    leaders = {
        "attackers": war_instance.get("attacker_leader"),
        "defenders": war_instance.get("defender_leader"),
    }
    score = preview["acceptance"].get("score")
    verdict = preview["acceptance"].get("verdict")
    war_label = str(preview.get("war_label") or _war_label(war_id, war_instance))
    # Spec §11.6 / SC-14c: staging owns the route id that dispatch,
    # notifications, the ledger row, and result feedback all share.
    route_id = _allocate_settlement_route_id(world, war_id)
    text = f"Review the settlement of {war_label}. Acceptance: {verdict} ({score if score is not None else 'blocked'})."
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
    can_ratify = (
        not hard_stops
        and verdict not in ("reject", "blocked")
        and (acceptance_score is not None and acceptance_score >= acceptance_threshold)
    )
    ratify_blocked_reason = ""
    if not can_ratify:
        if hard_stops:
            ratify_blocked_reason = "Ratification blocked by hard-stop warnings."
        elif acceptance_score is None:
            ratify_blocked_reason = f"Ratification unavailable: acceptance is blocked / {acceptance_threshold}."
        else:
            ratify_blocked_reason = f"Ratification unavailable: acceptance is {acceptance_score} / {acceptance_threshold}."
    options = []
    available_action_ids = []
    if can_ratify:
        options.append({"label": "Ratify Settlement", "action": "confirm_settlement", "available": True})
        available_action_ids.append("confirm_settlement")
    else:
        options.append(
            {
                "label": "Ratify Settlement",
                "action": "confirm_settlement",
                "available": False,
                "disabled_reason": ratify_blocked_reason,
                "description": ratify_blocked_reason,
            }
        )
    available_action_ids.append("back_out_settlement")
    options.append({"label": "Back Out", "action": "back_out_settlement", "available": True})

    covered = list(preview.get("covered_enemy_participants") or [])
    selected_target = str(selected_target_nation or "").strip()
    if selected_target and selected_target not in covered:
        raise ValueError("selected_target_not_covered")
    resolved_target = selected_target or (covered[0] if covered else "")
    return {
        "type": "settlement_confirm",
        "dialogue_type": "settlement_confirm",
        "war_id": war_id,
        "war_label": war_label,
        "route_id": route_id,
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
        "review_sections": copy.deepcopy(preview.get("review_sections") or {}),
        "coverage_scope_display": (preview.get("review_sections") or {}).get("coverage_scope_display", ""),
        "war_scope_display": (preview.get("review_sections") or {}).get("war_scope_display", ""),
        "covered_enemy_display_chips": list((preview.get("review_sections") or {}).get("covered_enemy_display_chips") or []),
        "uncovered_enemy_display_chips": list((preview.get("review_sections") or {}).get("uncovered_enemy_display_chips") or []),
        "acceptance_display": (preview.get("review_sections") or {}).get("sections", {}).get("acceptance", {}),
        "available_action_ids": available_action_ids,
        "can_ratify": can_ratify,
        "ratify_blocked_reason": ratify_blocked_reason,
        "options": options,
        "message": text,
        "talleyrand_text": text,
        "turn_created": int(getattr(world, "current_turn", 0) or 0),
        "blocking": True,
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
) -> Dict[str, Any]:
    explicit_covered = _normalize_nation_list(covered_enemy_participants)
    explicit_target = str(selected_target_nation or "").strip()
    if require_explicit_scope and not explicit_covered:
        return {"success": False, **_blocked_payload("no_covered_enemy_participants", war_id=war_id)}
    if require_explicit_scope and not explicit_target:
        return {"success": False, **_blocked_payload("no_selected_target_nation", war_id=war_id)}
    if explicit_target and explicit_covered and explicit_target not in explicit_covered:
        return {
            "success": False,
            **_blocked_payload(
                "selected_target_not_covered",
                war_id=war_id,
                selected_target_nation=explicit_target,
                covered_enemy_participants=explicit_covered,
            ),
        }
    preview = build_settlement_preview(
        world,
        war_id=war_id,
        proposer_side=proposer_side,
        settlement_terms=settlement_terms,
        covered_enemy_participants=covered_enemy_participants,
        actor_nation=actor_nation,
        density=density,
    )
    if not preview.get("success"):
        return preview
    covered = list(preview["settlement_preview"].get("covered_enemy_participants") or [])
    resolved_target = explicit_target or (covered[0] if covered else "")
    if not covered:
        return {"success": False, **_blocked_payload("no_covered_enemy_participants", war_id=war_id)}
    if not resolved_target:
        return {"success": False, **_blocked_payload("no_selected_target_nation", war_id=war_id)}
    if resolved_target not in covered:
        return {
            "success": False,
            **_blocked_payload(
                "selected_target_not_covered",
                war_id=war_id,
                selected_target_nation=resolved_target,
                covered_enemy_participants=covered,
            ),
        }
    try:
        dialogue = build_settlement_confirm_dialogue(
            world, preview, selected_target_nation=resolved_target,
        )
    except ValueError as exc:
        return {"success": False, **_blocked_payload(str(exc), war_id=war_id)}
    if getattr(world.dialogue_manager, "peek", lambda: None)() is None:
        world.dialogue_manager.replace(dialogue)
    elif hasattr(world.dialogue_manager, "preempt"):
        world.dialogue_manager.preempt(dialogue)
    else:
        world.dialogue_manager.replace(dialogue)
    return {
        "success": True,
        "dialogue_type": "settlement_confirm",
        "war_id": war_id,
        "diplomatic_dialogue": dialogue,
        "settlement_preview": preview["settlement_preview"],
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


def _build_pair_ratification_plan(
    world: Any,
    war_instance: Mapping[str, Any],
    *,
    proposer_side: str,
    covered: Iterable[str],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """Per-pair plan for which active cross-side pairs settle to which state.

    Each plan entry names the pair, the proposer-side member, the covered
    enemy, the pair's current state (so callers can branch ARMISTICE vs WAR
    cleanup), and the post-ratification target state. ``ALLIANCE`` is set
    only when a ``forced_alliance`` term exists with ``from`` matching the
    covered enemy and ``to`` matching the proposer-side member of the pair
    (spec §10.5 line 1038). Every other covered hostile pair settles to
    ``PEACE``.
    """
    proposer_members: Set[str] = set(war_instance.get(proposer_side) or [])
    covered_set: Set[str] = {str(n) for n in covered}
    forced_alliance_targets: Dict[str, Set[str]] = {}
    vassalage_targets: Dict[str, Dict[str, Mapping[str, Any]]] = {}
    for term in settlement_terms or []:
        if not isinstance(term, Mapping):
            continue
        if term.get("type") == "forced_alliance":
            fa_target = str(term.get("from") or "")
            fa_imposer = str(term.get("to") or "")
            if fa_target and fa_imposer:
                forced_alliance_targets.setdefault(fa_target, set()).add(fa_imposer)
        elif term.get("type") in ("vassalage", "subjugation"):
            vassal_target = str(term.get("from") or term.get("vassal_nation") or "")
            vassal_lord = str(term.get("to") or term.get("lord_nation") or "")
            if vassal_target and vassal_lord:
                vassalage_targets.setdefault(vassal_target, {})[vassal_lord] = term

    meta = war_instance.get("diplo_key_meta") or {}
    plan: List[Dict[str, Any]] = []
    for pair in list(war_instance.get("active_diplo_keys") or []):
        nations = _pair_nations(pair)
        if len(nations) != 2:
            continue
        a, b = nations
        if a in proposer_members and b in covered_set:
            proposer_member, covered_enemy = a, b
        elif b in proposer_members and a in covered_set:
            proposer_member, covered_enemy = b, a
        else:
            continue
        pair_meta = meta.get(pair) or {}
        if pair_meta.get("pair_status") not in ("war", "armistice"):
            continue
        target_state = "PEACE"
        if proposer_member in forced_alliance_targets.get(covered_enemy, set()):
            target_state = "ALLIANCE"
        if proposer_member in vassalage_targets.get(covered_enemy, {}):
            target_state = "VASSAL"
        current_state = world.diplomatic_states.get(pair, "PEACE")
        plan.append({
            "pair": pair,
            "proposer_member": proposer_member,
            "covered_enemy": covered_enemy,
            "current_state": current_state,
            "pair_status_before": pair_meta.get("pair_status"),
            "target_state": target_state,
        })
    return plan


def _capture_pair_pre_cleanup_war_data(
    world: Any,
    proposer_member: str,
    covered_enemy: str,
) -> Dict[str, Any]:
    """Snapshot war data from the resolving pair's proposer-side perspective."""
    diplo_key = world._make_diplo_key(proposer_member, covered_enemy)
    war_start = getattr(world, "war_start_turns", {}).get(
        diplo_key, getattr(world, "current_turn", 0),
    )
    war_duration = int(max(0, int(getattr(world, "current_turn", 0) or 0) - int(war_start)))

    raw_score = int(getattr(world, "war_scores", {}).get(diplo_key, 0))
    parts = diplo_key.split("|")
    proposer_war_score = raw_score
    if len(parts) == 2 and parts[0] != proposer_member:
        proposer_war_score = -raw_score

    records = list(getattr(world, "battle_records", {}).get(diplo_key, []) or [])
    proposer_casualties = 0
    covered_enemy_casualties = 0
    for record in records:
        attacker = record.get("attacker")
        defender = record.get("defender")
        attacker_casualties = int(record.get("attacker_casualties", 0) or 0)
        defender_casualties = int(record.get("defender_casualties", 0) or 0)
        if attacker == proposer_member:
            proposer_casualties += attacker_casualties
        elif defender == proposer_member:
            proposer_casualties += defender_casualties
        if attacker == covered_enemy:
            covered_enemy_casualties += attacker_casualties
        elif defender == covered_enemy:
            covered_enemy_casualties += defender_casualties

    player = getattr(world, "player_nation", "France")
    result = {
        "war_duration": war_duration,
        "war_score": int(proposer_war_score),
        "proposer_member": proposer_member,
        "covered_enemy": covered_enemy,
        "proposer_casualties": int(proposer_casualties),
        "covered_enemy_casualties": int(covered_enemy_casualties),
    }
    if proposer_member == player:
        result["french_casualties"] = int(proposer_casualties)
        result["enemy_casualties"] = int(covered_enemy_casualties)
    elif covered_enemy == player:
        result["french_casualties"] = int(covered_enemy_casualties)
        result["enemy_casualties"] = int(proposer_casualties)
    else:
        result["french_casualties"] = 0
        result["enemy_casualties"] = int(covered_enemy_casualties)
    return result


def _apply_settlement_terms(
    world: Any,
    *,
    settlement_terms: Iterable[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """Apply package-level territory, gold, and liberation outcomes.

    Forced-alliance state transitions are handled per pair after pair
    cleanup (see ``_resolve_pair_state_transitions``) because the alliance
    state must replace the intermediate ``PEACE`` state established by
    cleanup.
    """
    applied: List[Dict[str, Any]] = []
    for term in settlement_terms or []:
        if not isinstance(term, Mapping):
            continue
        ttype = term.get("type")
        from_nation = str(term.get("from") or "")
        to_nation = str(term.get("to") or "")
        if ttype == "territory_cede":
            regions = list(term.get("regions") or [])
            cede_from_regions = set()
            if from_nation:
                cede_from_regions = set(getattr(world, "get_nation_regions")(from_nation))
            if from_nation and regions and cede_from_regions:
                if len(cede_from_regions - set(regions)) == 0:
                    ws_key = world._make_diplo_key(from_nation, to_nation)
                    ws = abs(int(getattr(world, "war_scores", {}).get(ws_key, 0) or 0))
                    if ws < 90:
                        continue
            transferred: List[str] = []
            for region_name in regions:
                if region_name not in getattr(world, "regions", {}):
                    continue
                region = world.regions[region_name]
                if from_nation and getattr(region, "controller", None) != from_nation:
                    continue
                region.controller = to_nation
                region.stability = 50
                transferred.append(region_name)
                if from_nation and to_nation:
                    from backend.models.region import get_starting_controllers
                    starting_controllers = get_starting_controllers()
                    if starting_controllers.get(region_name) == to_nation:
                        from backend.game_logic.war_contribution import (
                            _resolve_war_id_for_pair_on_opposite_sides,
                            accrue_occupation_event,
                        )
                        cede_war_id = _resolve_war_id_for_pair_on_opposite_sides(
                            world, to_nation, from_nation,
                        )
                        if cede_war_id:
                            event_id = (
                                f"occupation-{int(getattr(world, 'current_turn', 0) or 0)}-"
                                f"{cede_war_id}-{to_nation}-"
                                f"allied_region_restored-{region_name}"
                            )
                            accrue_occupation_event(
                                world,
                                actor_nation=to_nation,
                                region=region_name,
                                occupation_kind="allied_region_restored",
                                from_controller=from_nation,
                                to_controller=to_nation,
                                war_id=cede_war_id,
                                turn=int(getattr(world, "current_turn", 0) or 0),
                                event_id=event_id,
                            )
            if transferred:
                clause = dict(term)
                clause["regions"] = transferred
                applied.append(clause)
                if hasattr(world, "invalidate_active_nations_cache"):
                    world.invalidate_active_nations_cache()
                if to_nation == getattr(world, "player_nation", None):
                    from backend.game_logic.coalition import add_threat
                    add_threat(world, 8 * len(transferred), "treaty_annex")
                if from_nation == getattr(world, "player_nation", None):
                    from backend.game_logic.coalition import reduce_threat
                    reduce_threat(world, 5 * len(transferred), "territory_return")
                for nation in {from_nation}:
                    if (
                        nation
                        and nation != getattr(world, "player_nation", None)
                        and hasattr(world, "get_nation_regions")
                        and not world.get_nation_regions(nation)
                    ):
                        world._eliminate_nation(nation)
        elif ttype == "gold_lump":
            amount = abs(int(term.get("amount", 0) or 0))
            nation_gold = getattr(world, "nation_gold", {}) or {}
            if from_nation in nation_gold:
                available = int(nation_gold.get(from_nation, 0))
                transfer = min(amount, max(0, available))
                nation_gold[from_nation] = available - transfer
                if to_nation in nation_gold:
                    nation_gold[to_nation] = int(nation_gold.get(to_nation, 0)) + transfer
                if transfer > 0:
                    clause = dict(term)
                    clause["amount"] = int(transfer)
                    applied.append(clause)
        elif ttype == "liberation":
            lib_vassal = str(term.get("vassal_nation") or term.get("from") or "")
            lib_from = str(term.get("lord_nation") or term.get("to") or "")
            lib_liberator = str(term.get("liberator") or "")
            vassals = getattr(world, "vassals", {}) or {}
            if lib_vassal and lib_vassal in vassals:
                pre_release_vassal_regions = list(world.get_nation_regions(lib_vassal))
                from backend.game_logic.vassal import release_vassal
                release_result = release_vassal(
                    world, lib_vassal, reduce_threat_on_release=False,
                )
                if release_result.get("success"):
                    if lib_liberator:
                        from backend.game_logic.diplomacy import (
                            set_diplomatic_state as _sds,
                        )
                        _sds(
                            world, lib_liberator, lib_vassal,
                            "DEFENSIVE_ALLIANCE", "common_peace_liberation",
                        )
                        if hasattr(world, "modify_nation_relation"):
                            world.modify_nation_relation(lib_vassal, lib_from, -20)
                            world.modify_nation_relation(lib_vassal, lib_liberator, 30)
                    if lib_from == getattr(world, "player_nation", None):
                        from backend.game_logic.coalition import reduce_threat
                        reduce_threat(world, 8, "liberation")
                    if (
                        lib_liberator
                        and lib_from
                        and lib_liberator != lib_from
                        and pre_release_vassal_regions
                    ):
                        from backend.game_logic.war_contribution import (
                            _resolve_war_id_for_pair_on_opposite_sides,
                            accrue_occupation_event,
                        )
                        lib_war_id = _resolve_war_id_for_pair_on_opposite_sides(
                            world, lib_liberator, lib_from,
                        )
                        if lib_war_id:
                            for lib_region in pre_release_vassal_regions:
                                event_id = (
                                    f"occupation-{int(getattr(world, 'current_turn', 0) or 0)}-"
                                    f"{lib_war_id}-{lib_liberator}-"
                                    f"liberated_region_restored-{lib_region}"
                                )
                                accrue_occupation_event(
                                    world,
                                    actor_nation=lib_liberator,
                                    region=lib_region,
                                    occupation_kind="liberated_region_restored",
                                    from_controller=lib_from,
                                    to_controller=lib_vassal,
                                    war_id=lib_war_id,
                                    turn=int(getattr(world, "current_turn", 0) or 0),
                                    event_id=event_id,
                                )
                    clause = dict(term)
                    clause["vassal_nation"] = lib_vassal
                    clause["lord_nation"] = lib_from
                    clause["liberator"] = lib_liberator
                    applied.append(clause)
                    if hasattr(world, "log_event"):
                        world.log_event({
                            "type": "vassal_liberated",
                            "vassal_nation": lib_vassal,
                            "former_lord": lib_from,
                            "liberator": lib_liberator,
                            "liberator_nation": lib_liberator,
                            "turn": int(getattr(world, "current_turn", 0) or 0),
                        })
    return applied


def _resolve_pair_state_transitions(
    world: Any,
    plan: List[Dict[str, Any]],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Run per-pair state transitions + cleanup for the ratification plan.

    For each plan entry: set ``PEACE`` (so cleanup_war_end resolves the
    pair, closes contribution episodes, clears war scores / start turns /
    decisive battles / cascade tracking / stalemate counters / armistice
    cooldowns), then for ``ALLIANCE`` targets re-set the state to
    ``ALLIANCE`` and apply forced-alliance side effects (alliance origin,
    Continental System membership, +15 threat when France imposes,
    relation reset, ``forced_alliance_imposed`` log event).

    Returns ``(resolved_pairs, forced_alliance_clauses_applied)`` so the
    caller can build a structured ratification summary.
    """
    from backend.game_logic.diplomacy import (
        cleanup_war_end,
        set_diplomatic_state,
    )

    forced_alliance_terms_by_pair: Dict[Tuple[str, str], Mapping[str, Any]] = {}
    vassalage_terms_by_pair: Dict[Tuple[str, str], Mapping[str, Any]] = {}
    for term in settlement_terms or []:
        if not isinstance(term, Mapping):
            continue
        if term.get("type") != "forced_alliance":
            if term.get("type") in ("vassalage", "subjugation"):
                vassal_target = str(term.get("from") or term.get("vassal_nation") or "")
                vassal_lord = str(term.get("to") or term.get("lord_nation") or "")
                if vassal_target and vassal_lord:
                    vassalage_terms_by_pair[(vassal_lord, vassal_target)] = term
            continue
        fa_target = str(term.get("from") or "")
        fa_imposer = str(term.get("to") or "")
        if fa_target and fa_imposer:
            forced_alliance_terms_by_pair[(fa_imposer, fa_target)] = term

    resolved_pairs: List[Dict[str, Any]] = []
    state_clauses_applied: List[Dict[str, Any]] = []

    for entry in plan:
        proposer_member = entry["proposer_member"]
        covered_enemy = entry["covered_enemy"]
        target_state = entry["target_state"]
        pair_key = world._make_diplo_key(proposer_member, covered_enemy)

        # Always transition out of WAR/ARMISTICE through PEACE so
        # cleanup_war_end runs the same closure path as bilateral peace
        # (resolve_pair_to_resolved + episode close + war-data clear).
        current_state = world.get_diplomatic_state(proposer_member, covered_enemy)
        if target_state == "VASSAL":
            term = vassalage_terms_by_pair.get((proposer_member, covered_enemy))
            vassal_result = {"success": False}
            if current_state == "ARMISTICE" and term is not None:
                set_diplomatic_state(
                    world, proposer_member, covered_enemy,
                    "WAR", "common_peace_vassalage_ratification",
                )
                current_state = "WAR"
            if current_state == "WAR" and term is not None:
                from backend.game_logic.vassal import (
                    assimilate_vassal_marshals,
                    create_vassal_conquest,
                    create_vassal_treaty,
                )
                if term.get("type") == "subjugation":
                    vassal_result = create_vassal_conquest(
                        world, proposer_member, covered_enemy,
                        garrison_size=int(term.get("garrison_size", 0) or 0),
                    )
                else:
                    vassal_result = create_vassal_treaty(
                        world, proposer_member, covered_enemy,
                        generosity_bonus=int(term.get("generosity_bonus", 0) or 0),
                        terms=list(settlement_terms or []),
                    )
                if vassal_result.get("success"):
                    assimilate_vassal_marshals(world, covered_enemy)
                    state_clauses_applied.append(dict(term))
                    cleanup_war_end(world, pair_key, conclude_objectives=True)
                else:
                    set_diplomatic_state(
                        world, proposer_member, covered_enemy,
                        "PEACE", "common_peace_settlement",
                    )
                    cleanup_war_end(world, pair_key, conclude_objectives=True)
            else:
                set_diplomatic_state(
                    world, proposer_member, covered_enemy,
                    "PEACE", "common_peace_settlement",
                )
                cleanup_war_end(world, pair_key, conclude_objectives=True)
        elif current_state in ("WAR", "ARMISTICE"):
            set_diplomatic_state(
                world, proposer_member, covered_enemy,
                "PEACE", "common_peace_settlement",
            )
            cleanup_war_end(world, pair_key, conclude_objectives=True)
        else:
            cleanup_war_end(world, pair_key, conclude_objectives=True)

        if target_state == "ALLIANCE":
            set_diplomatic_state(
                world, proposer_member, covered_enemy,
                "ALLIANCE", "common_peace_forced_alliance",
            )
            world.nation_relations[pair_key] = 0
            alliance_origins = getattr(world, "alliance_origins", {}) or {}
            alliance_origins[pair_key] = "forced"
            world.alliance_origins = alliance_origins
            term = forced_alliance_terms_by_pair.get(
                (proposer_member, covered_enemy),
            )
            includes_cs = bool(term.get("includes_continental_system", True)) if term else True
            if includes_cs:
                cs_members = getattr(world, "continental_system_members", []) or []
                if isinstance(cs_members, set):
                    cs_members.add(covered_enemy)
                elif covered_enemy not in cs_members:
                    cs_members.append(covered_enemy)
                world.continental_system_members = cs_members
            if proposer_member == getattr(world, "player_nation", None):
                from backend.game_logic.coalition import add_threat
                add_threat(world, 15, "forced_alliance")
            if hasattr(world, "log_event"):
                world.log_event({
                    "type": "forced_alliance_imposed",
                    "imposer": proposer_member,
                    "target": covered_enemy,
                    "imposing_nation": proposer_member,
                    "forced_nation": covered_enemy,
                    "includes_continental_system": includes_cs,
                    "turn": int(getattr(world, "current_turn", 0) or 0),
                })
            if term is not None:
                state_clauses_applied.append(dict(term))

        resolved_pairs.append({
            "pair": entry["pair"],
            "proposer_member": proposer_member,
            "covered_enemy": covered_enemy,
            "current_state_before": entry["current_state"],
            "pair_status_before": entry["pair_status_before"],
            "final_state": world.get_diplomatic_state(proposer_member, covered_enemy),
            "target_state": target_state,
        })

    return resolved_pairs, state_clauses_applied


def _record_common_peace_treaties(
    world: Any,
    *,
    plan: List[Dict[str, Any]],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> None:
    """Write per-pair treaty records in the same shape bilateral ratification uses."""
    active_treaties = getattr(world, "active_treaties", {}) or {}
    previous_treaties = getattr(world, "previous_treaties", {}) or {}
    all_terms = [dict(t) for t in (settlement_terms or []) if isinstance(t, Mapping)]
    for entry in plan:
        proposer_member = entry["proposer_member"]
        covered_enemy = entry["covered_enemy"]
        pair_key = world._make_diplo_key(proposer_member, covered_enemy)
        final_state = world.get_diplomatic_state(proposer_member, covered_enemy)
        pair_terms = []
        for term in all_terms:
            term_type = term.get("type")
            term_from = str(term.get("from") or term.get("vassal_nation") or "")
            term_to = str(term.get("to") or term.get("lord_nation") or term.get("liberator") or "")
            if term_type in ("forced_alliance", "vassalage", "subjugation"):
                if term_from == covered_enemy and term_to == proposer_member:
                    pair_terms.append(term)
            elif term_from == covered_enemy:
                pair_terms.append(term)
            elif term_to == proposer_member and term_from:
                pair_terms.append(term)
        treaty_type = {
            "ALLIANCE": "alliance",
            "VASSAL": "vassalage",
            "DEFENSIVE_ALLIANCE": "defensive_alliance",
        }.get(final_state, "peace")
        treaty = {
            "nations": [proposer_member, covered_enemy],
            "type": treaty_type,
            "state_transition": f"{entry['current_state']}_TO_{final_state}",
            "clauses": [dict(t) for t in pair_terms],
            "turn_signed": int(getattr(world, "current_turn", 0) or 0),
            "harshness": calculate_treaty_harshness({"clauses": pair_terms}),
        }
        active_treaties[pair_key] = treaty
        previous_treaties.setdefault(pair_key, []).append(dict(treaty))
    world.active_treaties = active_treaties
    world.previous_treaties = previous_treaties


def _capture_pre_cleanup_snapshots(
    world: Any,
    plan: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Snapshot per-pair war data before cleanup_war_end clears it.

    Spec §11 ratification ordering line 1239 requires snapshotting every
    covered pair's war-instance data before any cleanup runs. The C2
    summary shape exposes per-pair war_score / war_duration /
    casualties so D1 reactions can read frozen pre-settlement context.
    """
    snapshots: Dict[str, Dict[str, Any]] = {}
    for entry in plan:
        snapshots[entry["pair"]] = _capture_pair_pre_cleanup_war_data(
            world, entry["proposer_member"], entry["covered_enemy"],
        )
    return snapshots


def ratify_settlement_confirm(
    world: Any,
    dialogue: Mapping[str, Any],
) -> Dict[str, Any]:
    """Run the C2 common-peace ratification mutation.

    Per spec §10.5 / §11.1 / §11 ordering this function:

    1. Re-runs ``revalidate_staged_settlement`` on the live world.
    2. Builds a per-pair plan of which active cross-side pairs settle to
       ``PEACE`` vs ``ALLIANCE`` (forced-alliance only when a
       ``forced_alliance`` term targets the proposer-side member of the
       pair).
    3. Snapshots each covered pair's war data before cleanup.
    4. Applies package-level territory / gold / liberation term outcomes.
    5. Drives per-pair state transitions through ``set_diplomatic_state``
       + ``cleanup_war_end`` so the bilateral peace closure path runs
       (which moves the pair to ``resolved_diplo_keys`` and closes the
       contribution episode via ``resolve_pair_to_resolved``).
    6. For forced-alliance pairs, re-sets the state to ``ALLIANCE`` and
       applies forced-origin metadata, Continental System membership, and
       coalition threat per WPS-C §9.2 (already wired for bilateral
       forced-alliance treaties in ``_ratify_treaty``).
    7. Invalidates ``war_instances_by_*`` / bloc / active-nation caches
       before any subsequent reaction reader runs.
    8. Pops the ``settlement_confirm`` dialogue.

    D1/D2 settlement / cross-war reaction routing now runs AFTER the
    cache invalidation step in this function but BEFORE the dialogue is
    popped, satisfying spec §11 line 1239 ordering. The returned summary
    exposes the structured reaction payload under
    ``settlement_reactions`` for downstream presentation work (Slice E).
    """
    war_id = str(dialogue.get("war_id") or "")
    validation = revalidate_staged_settlement(world, dialogue)
    if not validation.get("ok"):
        world.dialogue_manager.pop()
        error = str(validation.get("error") or "")
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": "confirm",
            "war_id": war_id,
            "error": error,
            "error_display": _error_display(error),
            "reopen_target": _reopen_target(war_id, dialogue),
            "must_reopen": bool(validation.get("must_reopen")),
            "mutated": False,
        }

    war_instance = (getattr(world, "war_instances", {}) or {}).get(war_id)
    if not war_instance or war_instance.get("ended_turn") is not None:
        world.dialogue_manager.pop()
        error = "inactive_war_instance"
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": "confirm",
            "war_id": war_id,
            "error": error,
            "error_display": _error_display(error),
            "reopen_target": _reopen_target(war_id, dialogue),
            "must_reopen": True,
            "mutated": False,
        }

    # SC-3/SC-4: fresh acceptance rescore from current world state before mutation.
    proposer_side = str(dialogue.get("proposer_side") or "")
    accepting_side = str(dialogue.get("accepting_side") or "")
    covered = list(dialogue.get("covered_enemy_participants") or [])
    settlement_terms = list(dialogue.get("settlement_terms") or [])

    fresh_acceptance = calculate_common_peace_acceptance(
        world,
        war_id=war_id,
        war_instance=war_instance,
        proposer_side=proposer_side,
        accepting_side=accepting_side,
        accepting_leader=_side_leader(war_instance, accepting_side),
        proposer_side_leader=_side_leader(war_instance, proposer_side),
        covered_enemy_participants=covered,
        settlement_terms=settlement_terms,
    )
    fresh_hard_stops = list(fresh_acceptance.get("hard_stops") or [])
    fresh_score = fresh_acceptance.get("score")
    fresh_threshold = fresh_acceptance.get("accept_threshold") or 50
    fresh_verdict = fresh_acceptance.get("verdict") or "reject"

    # SC-4: unknown hard-stop codes fail closed.
    has_unknown_hard_stop = any(
        (hs.get("reason") or "") not in SETTLEMENT_HARD_STOP_CODES
        for hs in fresh_hard_stops
    )
    ratification_blocked = (
        fresh_hard_stops
        or fresh_verdict in ("reject", "blocked")
        or (fresh_score is not None and fresh_score < fresh_threshold)
        or has_unknown_hard_stop
    )
    if ratification_blocked:
        error = "acceptance_blocked" if fresh_hard_stops or has_unknown_hard_stop else "acceptance_rejected"
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": "confirm",
            "war_id": war_id,
            "error": error,
            "error_display": _error_display(error),
            "acceptance_verdict": fresh_verdict,
            "acceptance_score": fresh_score,
            "acceptance_threshold": fresh_threshold,
            "hard_stops": fresh_hard_stops,
            "mutated": False,
        }

    plan = _build_pair_ratification_plan(
        world,
        war_instance,
        proposer_side=proposer_side,
        covered=covered,
        settlement_terms=settlement_terms,
    )
    if not plan:
        world.dialogue_manager.pop()
        error = "no_resolvable_pairs"
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": "confirm",
            "war_id": war_id,
            "error": error,
            "error_display": _error_display(error),
            "reopen_target": _reopen_target(war_id, dialogue),
            "must_reopen": True,
            "mutated": False,
        }

    pre_cleanup_snapshots = _capture_pre_cleanup_snapshots(world, plan)
    # Capture pre-cleanup participant lists + side leaders so the
    # post-ratification `settlement_summary` event can render a friendly
    # war_label / leader markers even after cleanup_war_end empties the
    # live war_instance.attackers / .defenders lists. Spec §11.6 line
    # 1287 — event payload minimums.
    pre_cleanup_war_label = ""
    pre_cleanup_attackers = list(war_instance.get("attackers") or [])
    pre_cleanup_defenders = list(war_instance.get("defenders") or [])
    if pre_cleanup_attackers and pre_cleanup_defenders:
        pre_cleanup_war_label = (
            f"{pre_cleanup_attackers[0]} vs {pre_cleanup_defenders[0]}"
        )
    pre_cleanup_proposer_members = (
        list(pre_cleanup_attackers)
        if proposer_side == "attackers"
        else list(pre_cleanup_defenders)
    )
    pre_cleanup_accepting_members = (
        list(pre_cleanup_attackers)
        if accepting_side == "attackers"
        else list(pre_cleanup_defenders)
    )
    pre_cleanup_attacker_leader = str(war_instance.get("attacker_leader") or "")
    pre_cleanup_defender_leader = str(war_instance.get("defender_leader") or "")
    applied_clauses = _apply_settlement_terms(
        world, settlement_terms=settlement_terms,
    )
    resolved_pairs, fa_applied = _resolve_pair_state_transitions(
        world, plan, settlement_terms,
    )
    applied_clauses.extend(fa_applied)
    _record_common_peace_treaties(
        world, plan=plan, settlement_terms=settlement_terms,
    )

    # Spec §11 ratification ordering line 1239: invalidate war-instance
    # indexes + Balance of Europe / hegemony / bloc caches before any
    # cross-war reaction reader runs in the next slice.
    if hasattr(world, "invalidate_war_instance_indexes"):
        world.invalidate_war_instance_indexes()
    if hasattr(world, "invalidate_bloc_members_cache"):
        world.invalidate_bloc_members_cache()
    if hasattr(world, "invalidate_active_nations_cache"):
        world.invalidate_active_nations_cache()

    war_instance_after = (getattr(world, "war_instances", {}) or {}).get(war_id) or {}
    war_ended = war_instance_after.get("ended_turn") is not None

    # D1/D2 settlement / cross-war reaction routing per spec §11.5 / §14.
    # Runs AFTER cache invalidation but BEFORE the dialogue is popped so
    # any reaction reader sees fresh `war_instances_by_*` indexes.
    from backend.game_logic.settlement_reactions import (
        route_settlement_reactions,
    )
    reaction_summary = route_settlement_reactions(
        world,
        war_id=war_id,
        proposer_side=proposer_side,
        accepting_side=accepting_side,
        covered_enemy_participants=list(covered),
        settlement_terms=list(settlement_terms),
        resolved_pairs=resolved_pairs,
        applied_clauses=applied_clauses,
        pre_cleanup_snapshots=pre_cleanup_snapshots,
        war_ended=bool(war_ended),
        balance_projection=dict(dialogue.get("balance_projection") or {}),
        pre_cleanup_war_label=pre_cleanup_war_label,
        pre_cleanup_proposer_members=pre_cleanup_proposer_members,
        pre_cleanup_accepting_members=pre_cleanup_accepting_members,
        pre_cleanup_attacker_leader=pre_cleanup_attacker_leader,
        pre_cleanup_defender_leader=pre_cleanup_defender_leader,
        route_id=str(dialogue.get("route_id") or ""),
    )

    world.dialogue_manager.pop()

    result_message = (
        f"Settlement Ratified: {dialogue.get('war_label') or pre_cleanup_war_label or war_id} "
        f"({len(resolved_pairs)} pair(s) resolved)."
    )
    review_route_id = str(
        (reaction_summary.get("summary_event") or {}).get("route", {}).get("route_id", "")
        or dialogue.get("route_id")
        or f"{war_id}:{int(getattr(world, 'current_turn', 0) or 0)}"
    )
    review_route = {
        "surface": "ledger_settlements",
        "review_target": "ledger_settlements",
        "route_id": review_route_id,
        "war_id": war_id,
    }
    return {
        "success": True,
        "dialogue_type": "settlement_confirm",
        "action": "confirm",
        "war_id": war_id,
        "proposer_side": proposer_side,
        "accepting_side": accepting_side,
        "covered_enemy_participants": list(covered),
        "resolved_pairs": resolved_pairs,
        "applied_clauses": applied_clauses,
        "pre_cleanup_snapshots": pre_cleanup_snapshots,
        "war_ended": bool(war_ended),
        "settlement_reactions": reaction_summary,
        "settlement_result_feedback": {
            "title": "Settlement Ratified",
            "war_label": dialogue.get("war_label") or pre_cleanup_war_label or war_id,
            "resolved_pair_count": len(resolved_pairs),
            "review_target": "ledger_settlements",
            "route_id": review_route_id,
            "war_id": war_id,
            "review_route": review_route,
            "message": (
                f"{len(resolved_pairs)} hostile pair(s) resolved. "
                "Review the settlement in the diplomatic ledger."
            ),
        },
        "mutated": True,
        "message": result_message,
    }


def handle_settlement_dialogue_action(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
) -> Dict[str, Any]:
    """Handle C2 settlement dialogue actions.

    ``confirm_settlement`` runs the live ratification mutation through
    ``ratify_settlement_confirm``. ``back_out`` / ``revise_terms`` remain
    pure (no mutation, dialogue popped).
    """
    war_id = str(dialogue.get("war_id") or "")
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
        return {
            "success": True,
            "dialogue_type": "settlement_confirm",
            "action": "back_out",
            "cancelled": True,
            "mutated": False,
            "had_draft": has_draft,
            "message": "Settlement review cancelled.",
            "suppress_proposal_result_popup": True,
        }
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
    if action == "confirm_settlement":
        return ratify_settlement_confirm(world, dialogue)
    return {"success": False, "error": "unknown_settlement_action", "mutated": False}


def handle_incoming_settlement_offer_action(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
) -> Dict[str, Any]:
    """Handle mailbox-driven incoming settlement offers.

    Accepting an offer intentionally rebuilds a fresh settlement_confirm
    from live war state instead of ratifying the stale mailbox payload.

    NOTE: as of Slice F there is no producer of `incoming_settlement_offer`
    dialogues yet — the AI-initiated common-peace offer pipeline lands
    in a future slice (see WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §11.5).
    The handler is wired up now so the action dispatcher does not need a
    follow-up edit when offers begin to be produced; until then, this
    code path is unreachable from gameplay.
    """
    war_id = str(dialogue.get("war_id") or "")
    actor = getattr(world, "player_nation", "France")
    if action == "reject_settlement_offer":
        world.dialogue_manager.pop()
        return {
            "success": True,
            "dialogue_type": "incoming_settlement_offer",
            "action": "reject_settlement_offer",
            "mutated": False,
            "message": "Settlement offer rejected.",
            "suppress_proposal_result_popup": True,
        }
    if action == "request_settlement_revision":
        world.dialogue_manager.pop()
        return {
            "success": True,
            "dialogue_type": "incoming_settlement_offer",
            "action": "request_settlement_revision",
            "war_id": war_id,
            "must_reopen": True,
            "reopen_target": _reopen_target(war_id, dialogue),
            "mutated": False,
            "message": "Revision requested. Reopen the settlement review to adjust terms.",
            "suppress_proposal_result_popup": True,
        }
    if action != "accept_settlement_offer":
        return {"success": False, "error": "unknown_settlement_offer_action", "mutated": False}
    if not war_id:
        world.dialogue_manager.pop()
        return {
            "success": False,
            "dialogue_type": "incoming_settlement_offer",
            "action": "accept_settlement_offer",
            "war_id": war_id,
            "must_reopen": True,
            "error": "invalid_war_id",
            "error_display": _error_display("invalid_war_id"),
            "mutated": False,
        }

    world.dialogue_manager.pop()
    result = stage_settlement_confirm(
        world,
        war_id=war_id,
        actor_nation=actor,
        selected_target_nation=dialogue.get("selected_target_nation"),
        covered_enemy_participants=dialogue.get("covered_enemy_participants"),
        density="medium",
    )
    result["dialogue_type"] = "settlement_confirm"
    result["action"] = "accept_settlement_offer"
    if not result.get("success"):
        result["must_reopen"] = True
        result["error_display"] = result.get("error_display") or _error_display(str(result.get("error") or "invalid_war_id"))
    return result
