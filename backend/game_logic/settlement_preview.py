"""Common-peace settlement preview and dialogue staging helpers.

Slice C2 foundation: endpoint/dialogue contracts around the pure C1b
acceptance formula. These helpers are preview/staging only; they never ratify
terms or mutate treaty/region state.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, Iterable, List, Mapping, Optional

from backend.game_logic.settlement_scoring import calculate_common_peace_acceptance


VALID_SIDES = {"attackers", "defenders"}
SETTLEMENT_COOLDOWN_TURNS = 3


def _other_side(side: str) -> str:
    return "defenders" if side == "attackers" else "attackers"


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
        return {"available": False, "error": "invalid_war_id", "war_id": war_id}
    if instance.get("ended_turn") is not None:
        return {"available": False, "error": "inactive_war_instance", "war_id": war_id}

    side = _infer_actor_side(instance, actor, proposer_side)
    if side not in VALID_SIDES:
        return {"available": False, "error": "not_side_leader", "war_id": war_id}
    if _side_leader(instance, side) != actor:
        return {
            "available": False,
            "error": "not_side_leader",
            "war_id": war_id,
            "proposer_side": side,
        }

    pairs = _active_cross_side_pairs(instance, side)
    if not pairs:
        return {
            "available": False,
            "error": "no_unresolved_hostile_pairs",
            "war_id": war_id,
            "proposer_side": side,
        }

    coverable = get_coverable_enemy_participants(instance, side)
    if not coverable:
        return {
            "available": False,
            "error": "no_coverable_enemy",
            "war_id": war_id,
            "proposer_side": side,
        }

    if not ignore_active_dialogue and _settlement_dialogue_active(world, war_id):
        return {
            "available": False,
            "error": "settlement_dialogue_active",
            "war_id": war_id,
            "proposer_side": side,
        }

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
    covered = sorted(
        {str(n) for n in (covered_enemy_participants or eligibility["coverable_enemy_participants"])}
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

    warnings = []
    if acceptance.get("hard_stops"):
        warnings.append({
            "severity": "critical",
            "category": "hard_stop",
            "items": list(acceptance.get("hard_stops") or []),
        })
    for item in acceptance.get("feedback") or []:
        warnings.append({
            "severity": "warning",
            "category": "acceptance_component",
            "component": item.get("component"),
            "value": item.get("value"),
        })

    preview = {
        "war_instance": instance,
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
    text = (
        f"Review the common settlement for {war_id}. "
        f"Acceptance: {verdict} ({score if score is not None else 'blocked'})."
    )
    return {
        "type": "settlement_confirm",
        "dialogue_type": "settlement_confirm",
        "war_id": war_id,
        "proposer_side": proposer_side,
        "accepting_side": accepting_side,
        "staged_leaders": leaders,
        "staged_turn": int(getattr(world, "current_turn", 0) or 0),
        "settlement_terms": copy.deepcopy(preview.get("settlement_terms") or []),
        "covered_enemy_participants": list(preview.get("covered_enemy_participants") or []),
        "settlement_preview": preview,
        "acceptance_components": dict(preview.get("acceptance_components") or {}),
        "warnings": list(preview.get("warnings") or []),
        "hard_stops": list(preview["acceptance"].get("hard_stops") or []),
        "actions": ["confirm", "back_out", "revise_terms"],
        "options": [
            {"label": "Confirm settlement", "action": "confirm_settlement"},
            {"label": "Revise terms", "action": "revise_settlement_terms"},
            {"label": "Back out", "action": "back_out_settlement"},
        ],
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
    actor_nation: Optional[str] = None,
    density: str = "medium",
) -> Dict[str, Any]:
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
    dialogue = build_settlement_confirm_dialogue(world, preview)
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


def handle_settlement_dialogue_action(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
) -> Dict[str, Any]:
    """Handle C2 settlement dialogue actions without ratification mutation."""
    war_id = str(dialogue.get("war_id") or "")
    if action == "back_out_settlement":
        world.dialogue_manager.pop()
        return {
            "success": True,
            "dialogue_type": "settlement_confirm",
            "action": "back_out",
            "cancelled": True,
            "mutated": False,
            "message": "Settlement review cancelled.",
            "suppress_proposal_result_popup": True,
        }
    if action == "revise_settlement_terms":
        world.dialogue_manager.pop()
        return {
            "success": True,
            "dialogue_type": "settlement_confirm",
            "action": "revise_terms",
            "war_id": war_id,
            "must_reopen": True,
            "mutated": False,
            "message": "Reopen settlement review to revise terms.",
            "suppress_proposal_result_popup": True,
        }
    if action == "confirm_settlement":
        validation = revalidate_staged_settlement(world, dialogue)
        if not validation.get("ok"):
            world.dialogue_manager.pop()
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": "confirm",
                "war_id": war_id,
                "error": validation.get("error"),
                "must_reopen": bool(validation.get("must_reopen")),
                "mutated": False,
            }
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": "confirm",
            "war_id": war_id,
            "error": "ratification_deferred",
            "must_reopen": False,
            "mutated": False,
            "message": "Settlement ratification is not wired in this slice.",
        }
    return {"success": False, "error": "unknown_settlement_action", "mutated": False}
