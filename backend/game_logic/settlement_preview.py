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
    resolve_settlement_voice_line,
)
from backend.game_logic.settlement_scoring import (
    ACCEPTANCE_THRESHOLD,
    calculate_common_peace_acceptance,
    CANONICAL_CLAUSE_TYPES,
    CLAUSE_CONFLICT_MATRIX,
    CLAUSE_CONTROL_SCHEMA,
    compute_direct_scores_by_enemy,
    compute_side_pressure_score,
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


VALID_SIDES = {"attackers", "defenders"}
SETTLEMENT_COOLDOWN_TURNS = 3

# G2-Slice-3 SC-14b: stale-recovery reopen cap per (war_id, turn). Attempts
# 1..MAX may reopen when the target is valid; attempt MAX+1 returns
# `must_reopen=False` with the SC-14b choose-from-war-detail copy.
SETTLEMENT_REOPEN_MAX_ATTEMPTS = 3

# G2-Slice-3 SC-14c: route id namespace + format
#   `settlement:{war_id}:{turn}:{seq}` where `seq` is a per-(war_id, turn)
# monotonic counter starting at 1, persisted on
# `world.settlement_route_seq[war_id][turn]`.
SETTLEMENT_ROUTE_NAMESPACE = "settlement"

SETTLEMENT_FAMILY_DIALOGUE_TYPES = frozenset(
    {"settlement_confirm", "incoming_settlement_offer", "settlement_scope_replace_confirm"}
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

SETTLEMENT_ERROR_DISPLAY = SETTLEMENT_DISABLED_REASON_DISPLAY


def _error_display(code: str) -> str:
    return settlement_disabled_reason_display(code)


def _blocked_payload(code: str, **extra: Any) -> Dict[str, Any]:
    display = _error_display(code)
    payload = {
        "available": False,
        "error": code,
        "error_display": display,
        "disabled_reason_display": display,
        "display_reason": display,
        **extra,
    }
    if code == "settlement_dialogue_active":
        payload["talleyrand_text"] = resolve_settlement_voice_line(
            "settlement_collision_active_review_talleyrand",
            active_war_label=str(extra.get("war_id") or "the active war"),
            blocked_war_label=str(extra.get("war_id") or "this war"),
        )
    return payload


# ---------------------------------------------------------------------------
# SC-33 / G2-Slice-9 - Recurring gold payment helpers
# ---------------------------------------------------------------------------


def _estimate_payer_net_income_per_turn(world: Any, payer: str) -> int:
    """Non-mutating per-turn net income estimate for `payer`.

    Sums region income for regions controlled by `payer` (the closest
    existing non-mutating income projection — `process_income_phase`
    debits upkeep and admin bonuses, which we avoid because they are
    not idempotent). Clamped at 0 because the validator capacity rule
    uses `max(0, expected_net_income_per_turn)`.

    Falls back to 0 when `world.regions` is unavailable so legacy
    schema-only callers degrade safely.
    """
    regions = getattr(world, "regions", None) or {}
    income = 0
    for region in regions.values():
        if getattr(region, "controller", None) != payer:
            continue
        try:
            income += int(region.get_effective_income())
        except Exception:
            continue
    return max(0, int(income))


def _check_gold_payment_budget_conflict(
    world: Any,
    terms: List[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    """SC-1 / SC-33 budget conflict: combined gold obligations versus
    projected solvency, per the cleanup spec.

    Formula (per implementation directive May 14, 2026):

        payer_new_obligation =
            lump_sum_gold_due_now + sum(amount * turns) over submitted
            `gold_per_turn` clauses authored by the payer
        payer_existing_obligation =
            sum of (amount_per_turn * turns_remaining) over the payer's
            existing `world.recurring_settlement_payments`
        capacity =
            current_gold
            + max(0, expected_net_income_per_turn)
              * max_turns_in_submitted_terms

    Rejects with `gold_payment_budget_conflict` when
    `payer_new_obligation + payer_existing_obligation > capacity`. The
    rejection names the offending clause index so the editor can focus
    the budget conflict on the recurring entry.
    """
    nation_gold = getattr(world, "nation_gold", None) or {}
    payer_obligations: Dict[str, Dict[str, Any]] = {}
    max_turns = 0
    for idx, clause in enumerate(terms):
        ctype = clause.get("type")
        if ctype not in ("gold_indemnity", "gold_lump", "gold_per_turn"):
            continue
        payer = str(clause.get("from") or "")
        if not payer:
            continue
        amount = int(clause.get("amount", 0) or 0)
        record = payer_obligations.setdefault(
            payer,
            {"lump": 0, "recurring": 0, "max_turns": 0, "last_recurring_idx": None},
        )
        if ctype == "gold_per_turn":
            turns = int(clause.get("turns", 0) or 0)
            if turns <= 0 or amount <= 0:
                continue
            record["recurring"] += amount * turns
            record["max_turns"] = max(record["max_turns"], turns)
            record["last_recurring_idx"] = idx
            max_turns = max(max_turns, turns)
        else:
            record["lump"] += abs(amount)
    if not payer_obligations:
        return None

    existing = getattr(world, "recurring_settlement_payments", None) or []
    for payer, data in payer_obligations.items():
        existing_obligation = 0
        for entry in existing:
            if not isinstance(entry, Mapping):
                continue
            if str(entry.get("from") or "") != payer:
                continue
            existing_obligation += int(
                int(entry.get("amount_per_turn", 0) or 0)
                * int(entry.get("turns_remaining", 0) or 0)
            )
        current_gold = int(nation_gold.get(payer, 0) or 0)
        net_income = _estimate_payer_net_income_per_turn(world, payer)
        capacity = current_gold + max(0, net_income) * max(0, data["max_turns"])
        new_obligation = int(data["lump"]) + int(data["recurring"])
        if new_obligation + existing_obligation > capacity:
            error_index = data["last_recurring_idx"]
            if error_index is None:
                # Lump-sum-only budget conflict: focus the first lump-sum
                # clause for this payer.
                for jdx, clause in enumerate(terms):
                    if clause.get("type") in ("gold_indemnity", "gold_lump") and (
                        str(clause.get("from") or "") == payer
                    ):
                        error_index = jdx
                        break
            return {
                "valid": False,
                "error": "gold_payment_budget_conflict",
                "error_index": error_index,
                "disabled_reason_display": _error_display(
                    "gold_payment_budget_conflict"
                ),
            }
    return None


def _failed_ratification_reaction_summary(
    world: Any,
    *,
    war_id: str,
    proposer_side: str = "",
    accepting_side: str = "",
    covered_enemy_participants: Optional[Iterable[str]] = None,
    settlement_terms: Optional[Iterable[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    from backend.game_logic.settlement_reactions import route_settlement_reactions

    return route_settlement_reactions(
        world,
        war_id=war_id,
        proposer_side=proposer_side,
        accepting_side=accepting_side,
        covered_enemy_participants=list(covered_enemy_participants or []),
        settlement_terms=[dict(t) for t in (settlement_terms or []) if isinstance(t, Mapping)],
        resolved_pairs=[],
        applied_clauses=[],
        pre_cleanup_snapshots=[],
        war_ended=False,
        success=False,
        mutated=False,
    )


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


def _side_leader(war_instance: Mapping[str, Any], side: str) -> Optional[str]:
    if side == "attackers":
        return war_instance.get("attacker_leader")
    if side == "defenders":
        return war_instance.get("defender_leader")
    return None


def _side_for_nation(war_instance: Mapping[str, Any], nation: str) -> Optional[str]:
    nation_name = str(nation or "")
    if nation_name in set(war_instance.get("attackers") or []):
        return "attackers"
    if nation_name in set(war_instance.get("defenders") or []):
        return "defenders"
    side_by_nation = war_instance.get("side_by_nation") or {}
    side = str(side_by_nation.get(nation_name) or "")
    return side if side in VALID_SIDES else None


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
        if pair_meta.get("pair_status", "war") not in ("war", "armistice"):
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
    dm = getattr(world, "dialogue_manager", None)
    queued = list(dm.iter_queue()) if dm is not None and hasattr(dm, "iter_queue") else []
    for dialogue in ([current] if current else []) + queued:
        if not isinstance(dialogue, Mapping):
            continue
        if dialogue.get("type") not in ("settlement_confirm", "incoming_settlement_offer"):
            continue
        if str(dialogue.get("war_id") or "") == str(war_id):
            return True
    return False


def _settlement_history_route(
    *,
    war_id: str,
    route_id: str = "",
    reason: str = "",
) -> Dict[str, Any]:
    route = {
        "surface": "settlement_history",
        "target": "settlement_history",
        "war_id": str(war_id or ""),
        "route_id": str(route_id or ""),
    }
    if reason:
        route["reason"] = reason
    return route


def _war_detail_recovery_route(
    *,
    war_id: str,
    selected_target_nation: str = "",
    covered_enemy_participants: Optional[Iterable[str]] = None,
    source_route_id: str = "",
    reason: str = "",
) -> Dict[str, Any]:
    route = {
        "surface": "war_detail",
        "target": "war_detail",
        "war_id": str(war_id or ""),
        "selected_target_nation": str(selected_target_nation or ""),
        "target_nation": str(selected_target_nation or ""),
        "nation": str(selected_target_nation or ""),
        "covered_enemy_participants": list(covered_enemy_participants or []),
        "source_route_id": str(source_route_id or ""),
    }
    if reason:
        route["reason"] = reason
    return route


def _terminal_recovery_copy(war_id: str = "") -> str:
    return resolve_settlement_voice_line(
        "settlement_no_alternative_route_chancery",
        war_label=str(war_id or "this war"),
    ) or (
        "This settlement cannot currently be recovered from the existing "
        "surfaces. Close this review and reassess the war next turn."
    )


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


def evaluate_war_detail_actionability(
    world: Any,
    *,
    war_id: str,
    selected_target_nation: Optional[str] = None,
    covered_enemy_participants: Optional[Iterable[str]] = None,
    source_route_id: str = "",
    actor_nation: Optional[str] = None,
) -> Dict[str, Any]:
    """SC-10b: decide whether blocked review may show Open War Detail.

    This helper deliberately answers only whether War Detail is a real
    recovery surface for the selected live pair. It does not expose direct
    pair-substitute actions from settlement_confirm; War Detail remains the
    owner of bilateral peace / armistice controls.
    """
    war_id_str = str(war_id or "")
    actor = str(actor_nation or getattr(world, "player_nation", "France") or "France")
    selected = str(selected_target_nation or "").strip()
    covered = _normalize_nation_list(covered_enemy_participants)

    def _blocked(code: str, **extra: Any) -> Dict[str, Any]:
        display = _error_display(code)
        return {
            "actionable": False,
            "war_id": war_id_str,
            "selected_target_nation": selected,
            "covered_enemy_participants": covered,
            "refusal_code": code,
            "refusal_code_display": display,
            "error": code,
            "error_display": display,
            "peace_seeking_controls": [],
            **extra,
        }

    if not war_id_str:
        return _blocked("malformed_route")
    instance = (getattr(world, "war_instances", {}) or {}).get(war_id_str)
    if not isinstance(instance, Mapping):
        if is_war_archived(world, war_id_str):
            return _blocked(
                "war_archived",
                recovery_route=_settlement_history_route(
                    war_id=war_id_str,
                    route_id=source_route_id,
                    reason="war_archived",
                ),
            )
        return _blocked("war_archived" if is_war_known(world, war_id_str) else "malformed_route")
    if instance.get("ended_turn") is not None:
        return _blocked(
            "war_archived",
            recovery_route=_settlement_history_route(
                war_id=war_id_str,
                route_id=source_route_id,
                reason="war_archived",
            ),
        )
    mounted = _mounted_settlement_dialogue(world)
    if mounted is not None and str(mounted.get("war_id") or "") not in ("", war_id_str):
        return _blocked("settlement_collision_active")
    if not selected:
        return _blocked("selected_pair_missing")

    side_by_nation = instance.get("side_by_nation") or {}
    actor_side = side_by_nation.get(actor)
    selected_side = side_by_nation.get(selected)
    if not actor_side or not selected_side or actor_side == selected_side:
        return _blocked("selected_pair_missing")

    pair = world._make_diplo_key(actor, selected) if hasattr(world, "_make_diplo_key") else "|".join(sorted([actor, selected]))
    meta = instance.get("diplo_key_meta") or {}
    pair_meta = meta.get(pair) or {}
    resolved_pairs = set(instance.get("resolved_diplo_keys") or [])
    if pair in resolved_pairs or pair_meta.get("pair_status") == "resolved":
        return _blocked("pair_already_resolved")
    active_pairs = set(instance.get("active_diplo_keys") or [])
    if pair not in active_pairs:
        return _blocked("selected_pair_missing")
    if pair_meta.get("pair_status", "war") != "war":
        return _blocked("pair_not_at_war")
    if (getattr(world, "diplomatic_states", {}) or {}).get(pair) != "WAR":
        return _blocked("pair_not_at_war")

    route = _war_detail_recovery_route(
        war_id=war_id_str,
        selected_target_nation=selected,
        covered_enemy_participants=covered,
        source_route_id=source_route_id,
        reason="blocked_settlement_recovery",
    )
    return {
        "actionable": True,
        "war_id": war_id_str,
        "selected_target_nation": selected,
        "covered_enemy_participants": covered,
        "refusal_code": "",
        "refusal_code_display": "",
        "peace_seeking_controls": ["negotiate_peace"],
        "recovery_route": route,
    }


# ---------------------------------------------------------------------------
# SC-29 / G2-Slice-7: pair-scoped peace substitute CTAs
# ---------------------------------------------------------------------------


PAIR_SUBSTITUTE_ACTIONS = frozenset({"seek_armistice_instead", "seek_bilateral_peace"})

PAIR_SUBSTITUTE_TEMPORAL_REFUSAL_CODES = frozenset({"cooldown_active"})

PAIR_SUBSTITUTE_REFUSAL_CODES = frozenset({
    "already_at_peace",
    "already_in_armistice",
    "pair_not_at_war",
    "war_archived",
    "actor_not_at_war_with_target",
    "target_not_selected_pair",
    "target_not_in_war",
    "settlement_collision_active",
    "cooldown_active",
    "insufficient_resources",
    "malformed_route",
})


def evaluate_pair_peace_substitute_eligibility(
    world: Any,
    *,
    war_id: str,
    actor_nation: str,
    target_nation: str,
    action: str,
) -> Dict[str, Any]:
    """SC-29 / G2-Slice-7: decide whether a rejected settlement popup may
    expose `Seek Armistice Instead` or `Seek Bilateral Peace` for the
    selected actor/target pair.

    Returns a dict whose shape is pinned by the spec
    "Pair substitute eligibility helper schema":

        {
            "eligible": bool,
            "refusal_code": str | null,
            "disabled_reason_display": str | null,
            "selected_pair": {
                "actor": str,
                "target": str,
                "war_id": str,
            },
        }

    The refusal taxonomy is closed (see `PAIR_SUBSTITUTE_REFUSAL_CODES`).
    Only `cooldown_active` is a temporal disabled state per spec
    "Disabled vs Hidden Affordance Policy"; every other code hides the
    substitute action rather than rendering it disabled.
    """
    war_id_str = str(war_id or "")
    actor = str(actor_nation or "").strip()
    target = str(target_nation or "").strip()
    action_str = str(action or "").strip()

    selected_pair = {"actor": actor, "target": target, "war_id": war_id_str}

    def _refused(code: str) -> Dict[str, Any]:
        return {
            "eligible": False,
            "refusal_code": code,
            "disabled_reason_display": _error_display(code),
            "selected_pair": selected_pair,
        }

    if action_str not in PAIR_SUBSTITUTE_ACTIONS:
        return _refused("malformed_route")
    if not war_id_str or not actor or not target:
        return _refused("malformed_route")
    if actor == target:
        return _refused("malformed_route")

    instance = (getattr(world, "war_instances", {}) or {}).get(war_id_str)
    if not isinstance(instance, Mapping):
        if is_war_archived(world, war_id_str):
            return _refused("war_archived")
        return _refused("malformed_route")
    if instance.get("ended_turn") is not None:
        return _refused("war_archived")

    side_by_nation = instance.get("side_by_nation") or {}
    actor_side = side_by_nation.get(actor)
    target_side = side_by_nation.get(target)
    if not actor_side:
        return _refused("actor_not_at_war_with_target")
    if not target_side:
        return _refused("target_not_in_war")
    if actor_side == target_side:
        return _refused("target_not_selected_pair")

    pair = (
        world._make_diplo_key(actor, target)
        if hasattr(world, "_make_diplo_key")
        else "|".join(sorted([actor, target]))
    )
    pair_state = (getattr(world, "diplomatic_states", {}) or {}).get(pair)
    if pair_state == "PEACE":
        return _refused("already_at_peace")
    if pair_state == "ARMISTICE":
        if action_str == "seek_armistice_instead":
            return _refused("already_in_armistice")
    if pair_state not in ("WAR", "ARMISTICE"):
        return _refused("actor_not_at_war_with_target")

    meta = instance.get("diplo_key_meta") or {}
    pair_meta = meta.get(pair) or {}
    resolved_pairs = set(instance.get("resolved_diplo_keys") or [])
    if pair in resolved_pairs or pair_meta.get("pair_status") == "resolved":
        return _refused("pair_not_at_war")
    active_pairs = set(instance.get("active_diplo_keys") or [])
    if pair not in active_pairs:
        return _refused("target_not_selected_pair")
    pair_status = pair_meta.get("pair_status", "war")
    if pair_status == "armistice" and action_str == "seek_armistice_instead":
        return _refused("already_in_armistice")
    if pair_status not in ("war", "armistice"):
        return _refused("pair_not_at_war")
    if action_str == "seek_bilateral_peace" and pair_state == "WAR" and pair_status != "war":
        # State and pair_status disagree — fail safe so we never advertise
        # a substitute action on a stale view.
        return _refused("pair_not_at_war")

    mounted = _mounted_settlement_dialogue(world)
    if mounted is not None and str(mounted.get("war_id") or "") not in ("", war_id_str):
        return _refused("settlement_collision_active")

    cooldowns = getattr(world, "player_proposal_cooldowns", None) or {}
    proposal_type = "armistice" if action_str == "seek_armistice_instead" else "peace"
    type_key = f"{target}_{proposal_type}"
    if isinstance(cooldowns, Mapping):
        if cooldowns.get(target, 0) > 0:
            return _refused("cooldown_active")
        if cooldowns.get(type_key, 0) > 0:
            return _refused("cooldown_active")

    # DP cost is computed via the same helper the proposal executor uses,
    # so the substitute CTA never advertises a proposal the player cannot
    # actually send.
    try:
        from backend.game_logic.diplomacy import get_dp_cost, get_transition_dp_cost
    except Exception:  # pragma: no cover - defensive import guard
        get_dp_cost = None
        get_transition_dp_cost = None
    if get_dp_cost is not None and get_transition_dp_cost is not None:
        _state_map = {
            "peace": "PEACE",
            "armistice": "ARMISTICE",
        }
        try:
            current_diplo = world.get_diplomatic_state(actor, target)
        except Exception:  # pragma: no cover - defensive
            current_diplo = pair_state or "WAR"
        target_diplo = _state_map.get(proposal_type, "PEACE")
        jump_cost = get_transition_dp_cost(current_diplo, target_diplo)
        try:
            from backend.nation_config import get_player_diplomat
            talleyrand = get_player_diplomat(world)
            skill = int(getattr(talleyrand, "skill", 5)) if talleyrand else 5
        except Exception:  # pragma: no cover - defensive
            skill = 5
        cost = get_dp_cost(f"propose_{proposal_type}", skill, transition_base=jump_cost)
        if float(getattr(world, "diplomatic_points", 0) or 0) < float(cost):
            return _refused("insufficient_resources")

    return {
        "eligible": True,
        "refusal_code": None,
        "disabled_reason_display": None,
        "selected_pair": selected_pair,
    }


# ---------------------------------------------------------------------------
# G2-Slice-3 helpers: route id, collision, reopen cap, active-vs-archived
# ---------------------------------------------------------------------------


def _mounted_settlement_dialogue(world: Any) -> Optional[Mapping[str, Any]]:
    """Return the *current* settlement-family dialogue, or None.

    SC-14 / SC-26 mounted means the current hard-stop dialogue. Queued or
    dismissed settlement-family items don't count for live-route precedence
    or collision protection.
    """
    current = getattr(world, "pending_diplomatic_dialogue", None)
    if not isinstance(current, Mapping):
        return None
    if current.get("type") not in SETTLEMENT_FAMILY_DIALOGUE_TYPES:
        return None
    return current


def mint_settlement_route_id(
    world: Any,
    *,
    war_id: str,
    turn: Optional[int] = None,
) -> str:
    """SC-14c: mint a unique `settlement:{war_id}:{turn}:{seq}` route id.

    `seq` is a per-(war_id, turn) monotonic counter starting at 1, persisted
    on `world.settlement_route_seq[war_id][turn]` so two settlement events
    in the same turn do not collide. The staged dialogue owns the id; every
    downstream consumer (reaction event, dispatch, ledger, notification,
    result feedback) reads the staged value verbatim and never recomputes.
    """
    if turn is None:
        turn = int(getattr(world, "current_turn", 0) or 0)
    else:
        turn = int(turn)
    store = getattr(world, "settlement_route_seq", None)
    if store is None:
        world.settlement_route_seq = {}
        store = world.settlement_route_seq
    per_war = store.setdefault(str(war_id), {})
    last = int(per_war.get(turn, 0) or 0)
    seq = last + 1
    per_war[turn] = seq
    return f"{SETTLEMENT_ROUTE_NAMESPACE}:{war_id}:{turn}:{seq}"


def _reopen_attempt_store(world: Any) -> Dict[str, Dict[int, int]]:
    store = getattr(world, "settlement_reopen_attempts", None)
    if store is None:
        world.settlement_reopen_attempts = {}
        store = world.settlement_reopen_attempts
    return store


def get_reopen_attempts(world: Any, *, war_id: str) -> int:
    """Read the SC-14b reopen attempt count for the current `(war_id, turn)`."""
    if not war_id:
        return 0
    turn = int(getattr(world, "current_turn", 0) or 0)
    return int((_reopen_attempt_store(world).get(str(war_id)) or {}).get(turn, 0))


def record_reopen_attempt(world: Any, *, war_id: str) -> int:
    """SC-14b: increment + return the per-(war_id, turn) reopen attempt count.

    Attempt 1..SETTLEMENT_REOPEN_MAX_ATTEMPTS may reopen when the target is
    valid; the next attempt must return `must_reopen=False` with the
    `reopen_attempt_cap_exceeded` SC-14b choose-from-war-detail copy.
    """
    if not war_id:
        return 0
    turn = int(getattr(world, "current_turn", 0) or 0)
    store = _reopen_attempt_store(world)
    per_war = store.setdefault(str(war_id), {})
    per_war[turn] = int(per_war.get(turn, 0) or 0) + 1
    return int(per_war[turn])


def reopen_attempt_cap_exceeded(world: Any, *, war_id: str) -> bool:
    """True when a further reopen for this `(war_id, turn)` must NOT fire."""
    return get_reopen_attempts(world, war_id=war_id) >= SETTLEMENT_REOPEN_MAX_ATTEMPTS


def is_war_archived(world: Any, war_id: str) -> bool:
    """SC-14/14d/14e: the war is archived (or no longer active) right now.

    Click-time check: an active `war_instance` with no `ended_turn` is
    live; anything else (ended, missing, or in `archived_war_instances`)
    must route to the archived ledger row.
    """
    if not war_id:
        return False
    instances = getattr(world, "war_instances", {}) or {}
    instance = instances.get(str(war_id))
    if isinstance(instance, Mapping):
        if instance.get("ended_turn") is not None:
            return True
        return False
    archived = getattr(world, "archived_war_instances", None) or []
    for entry in archived:
        if isinstance(entry, Mapping) and str(entry.get("war_id") or "") == str(war_id):
            return True
    return False


def is_war_known(world: Any, war_id: str) -> bool:
    """True if `war_id` resolves to either an active or archived instance."""
    if not war_id:
        return False
    instances = getattr(world, "war_instances", {}) or {}
    if str(war_id) in instances:
        return True
    archived = getattr(world, "archived_war_instances", None) or []
    return any(
        isinstance(entry, Mapping) and str(entry.get("war_id") or "") == str(war_id)
        for entry in archived
    )


def derive_settlement_review_target(world: Any, *, war_id: str) -> str:
    """SC-14/14d/14e click-time re-resolution.

    Returns the canonical review-target string to use *now*, regardless of
    what was rendered into a notification, dispatch, or result feedback row
    when it was first emitted. Active war -> live settlement review surface;
    archived (ended/no longer in `war_instances`) -> archived ledger row.
    """
    from backend.game_logic.settlement_presentation import (
        SETTLEMENT_REVIEW_TARGET_ACTIVE,
        SETTLEMENT_REVIEW_TARGET_ARCHIVED,
    )

    if is_war_archived(world, war_id):
        return SETTLEMENT_REVIEW_TARGET_ARCHIVED
    return SETTLEMENT_REVIEW_TARGET_ACTIVE


def resolve_settlement_route_click(
    world: Any,
    *,
    war_id: str,
    route_id: Optional[str] = None,
    recent_window_route_ids: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """SC-14/14d/14e: re-resolve a settlement route click against live state.

    Returns a structured payload describing what the click should do *now*:

    - `available=True, review_target="settlement_review", war_id=...` for
      live wars (route the click into an in-flight active surface).
    - `available=True, review_target="ledger_settlements", war_id=..., route_id=...`
      for archived rows still inside the recent-settlement window.
    - `available=False, error="settlement_no_longer_in_recent_window"` when
      `recent_window_route_ids` is supplied and the route id is no longer
      present (SC-14e aged-out dispatch link).
    - `available=False, error="invalid_war_id"` for unknown wars.

    Callers pass `recent_window_route_ids` (the route ids visible in the
    current recent-settlement window) when they care about aged-out
    routing; callers that don't care (live result feedback) leave it
    None and just get archived/active routing.
    """
    from backend.game_logic.settlement_presentation import (
        SETTLEMENT_REVIEW_TARGET_ACTIVE,
        SETTLEMENT_REVIEW_TARGET_ARCHIVED,
    )

    war_id_str = str(war_id or "")
    if not war_id_str or not is_war_known(world, war_id_str):
        return {
            "available": False,
            "war_id": war_id_str,
            "route_id": str(route_id or ""),
            "review_target": "",
            "error": "invalid_war_id",
            "error_display": _error_display("invalid_war_id"),
        }
    archived = is_war_archived(world, war_id_str)
    if archived and recent_window_route_ids is not None:
        window = {str(r or "") for r in recent_window_route_ids if r is not None}
        if route_id and str(route_id) not in window:
            return {
                "available": False,
                "war_id": war_id_str,
                "route_id": str(route_id or ""),
                "review_target": SETTLEMENT_REVIEW_TARGET_ARCHIVED,
                "error": "settlement_no_longer_in_recent_window",
                "error_display": _error_display(
                    "settlement_no_longer_in_recent_window"
                ),
            }
    return {
        "available": True,
        "war_id": war_id_str,
        "route_id": str(route_id or ""),
        "review_target": (
            SETTLEMENT_REVIEW_TARGET_ARCHIVED
            if archived
            else SETTLEMENT_REVIEW_TARGET_ACTIVE
        ),
        "war_archived": bool(archived),
    }


def _no_reopen_target_payload(
    war_id: str,
    *,
    error: str = "no_reopen_target_available",
) -> Dict[str, Any]:
    """SC-13 / SC-14b / SC-7b dual-empty / cap-exceeded fallback payload.

    Returns the structured response fields used when reopen cannot be
    safely fired and the player must be redirected to war detail. The
    caller is responsible for adding success/dialogue_type/action.
    """
    payload = {
        "must_reopen": False,
        "reopen_target": {
            "surface": "war_detail",
            "target": "war_detail",
            "war_id": war_id,
            "nation": "",
            "target_nation": "",
        },
        "error": error,
        "error_display": _error_display(error),
    }
    if error == "reopen_attempt_cap_exceeded":
        payload["talleyrand_text"] = resolve_settlement_voice_line(
            "settlement_reopen_cap_exhausted_talleyrand",
            war_label=war_id or "this war",
        )
    return payload


def _safe_reopen_response(
    world: Any,
    *,
    war_id: str,
    dialogue: Mapping[str, Any],
    fallback_error: str = "no_reopen_target_available",
) -> Dict[str, Any]:
    """Build the SC-2/SC-3/SC-13 reopen payload with the SC-14b cap applied.

    Honors SC-7b (no `must_reopen=True` with empty target), SC-13
    (dual-empty fallback) and SC-14b (per-(war_id, turn) attempt cap).
    The caller then merges this payload into its action result.
    """
    selected = str(dialogue.get("selected_target_nation") or "")
    covered = list(dialogue.get("covered_enemy_participants") or [])
    has_target = bool(selected) or bool(covered)
    if not has_target:
        return _no_reopen_target_payload(war_id, error=fallback_error)
    if reopen_attempt_cap_exceeded(world, war_id=war_id):
        actionability = evaluate_war_detail_actionability(
            world,
            war_id=war_id,
            selected_target_nation=selected or (str(covered[0]) if covered else ""),
            covered_enemy_participants=covered,
            source_route_id=str(dialogue.get("route_id") or ""),
        )
        payload = {
            "must_reopen": False,
            "error": "reopen_attempt_cap_exceeded",
            "error_display": _error_display("reopen_attempt_cap_exceeded"),
            "war_detail_actionability": actionability,
            "talleyrand_text": resolve_settlement_voice_line(
                "settlement_reopen_cap_exhausted_talleyrand",
                war_label=war_id or "this war",
            ),
        }
        if actionability.get("actionable"):
            route = dict(actionability.get("recovery_route") or {})
            payload["recovery_route"] = route
            payload["reopen_target"] = route
        else:
            payload["terminal_recovery_copy"] = _terminal_recovery_copy(war_id)
            payload["reopen_target"] = {
                "surface": "blocked_terminal",
                "target": "blocked_terminal",
                "war_id": war_id,
                "nation": selected,
                "target_nation": selected,
            }
        return payload
    record_reopen_attempt(world, war_id=war_id)
    return {
        "must_reopen": True,
        "reopen_target": _reopen_target(war_id, dialogue),
    }


# ---------------------------------------------------------------------------
# G2-Slice-3 SC-26: same-war / cross-war collision support
# ---------------------------------------------------------------------------


def _clause_identity_key(term: Mapping[str, Any]) -> Tuple[str, str, str, str]:
    """Type-specific identity tuple per SC-26 same-war merge semantics.

    Same-key entries with differing values conflict; cross-key entries
    are non-conflicting and merge by append. The canonical identity is
    (type, from, to, region) for clauses that have all four; missing
    fields collapse to "" so key uniqueness aligns with the canonical
    schema.
    """
    return (
        str(term.get("type") or ""),
        str(term.get("from") or ""),
        str(term.get("to") or ""),
        str(term.get("region") or ""),
    )


def _terms_equal(a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
    """Strict equality for clause merge conflict detection.

    Two same-key clauses are equal only when every field matches. Same
    region with different gold amounts conflicts; same region with
    identical fields is a duplicate (the merge ignores duplicates).
    """
    keys = set(a.keys()) | set(b.keys())
    for key in keys:
        if a.get(key) != b.get(key):
            return False
    return True


def merge_same_war_settlement_drafts(
    existing_terms: Iterable[Mapping[str, Any]],
    new_terms: Iterable[Mapping[str, Any]],
) -> Tuple[bool, List[Dict[str, Any]], List[Dict[str, Any]]]:
    """SC-26 merge contract: keep authored draft, fold compatible new terms.

    Returns (ok, merged_terms, conflicts):
      - ok=True when every new term is either compatible with the active
        draft (same identity AND same fields => duplicate, kept once) or
        adds a new identity (appended). The merged list keeps existing
        draft order and appends compatible additions.
      - ok=False when any new term collides with an existing draft term
        on the same identity but differs in fields. The merged list is
        the unchanged existing draft (per SC-26 "active draft unchanged")
        and the conflicts list contains the offending pairs.
    """
    existing_list = [dict(t) for t in (existing_terms or []) if isinstance(t, Mapping)]
    additions: List[Dict[str, Any]] = []
    conflicts: List[Dict[str, Any]] = []
    by_key: Dict[Tuple[str, str, str, str], Dict[str, Any]] = {
        _clause_identity_key(term): term for term in existing_list
    }
    for term in new_terms or []:
        if not isinstance(term, Mapping):
            continue
        key = _clause_identity_key(term)
        if key in by_key:
            if _terms_equal(by_key[key], term):
                continue  # duplicate -> idempotent merge
            conflicts.append({"existing": dict(by_key[key]), "incoming": dict(term)})
        else:
            additions.append(dict(term))
    if conflicts:
        return False, existing_list, conflicts
    return True, existing_list + additions, []


def _territory_term_regions(term: Mapping[str, Any]) -> List[str]:
    regions = term.get("regions")
    if isinstance(regions, (list, tuple)) and regions:
        return [str(r) for r in regions if str(r)]
    region = str(term.get("region") or "")
    return [region] if region else []


def _normalize_staged_terms_for_validation(
    settlement_terms: Iterable[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """Return a canonical-shaped COPY of staged settlement terms for the
    ratify-time defense-in-depth revalidation (the mutation path keeps
    consuming the originals — this never mutates ``settlement_terms``).

    Staged packages may carry two apply-format variances that the canonical
    ``validate_settlement_terms`` schema would otherwise reject (the legacy
    ratification fixtures + historical drafts the type-only guard tolerates):

    - ``gold_lump`` (``RATIFY_LEGACY_APPLY_CLAUSE_TYPES``) → ``gold_indemnity``.
    - ``territory_cede`` carrying a plural ``regions`` list → one canonical
      single-``region`` clause per region (mirrors ``_territory_term_regions``).

    Every other clause passes through untouched, so any genuinely-malformed
    staged clause still fails revalidation (defense in depth, not laundering).
    """
    normalized: List[Dict[str, Any]] = []
    for term in settlement_terms or []:
        if not isinstance(term, Mapping):
            # Leave non-mappings for the validator to reject.
            normalized.append(term)  # type: ignore[arg-type]
            continue
        clause = dict(term)
        if clause.get("type") == "gold_lump":
            clause["type"] = "gold_indemnity"
        if clause.get("type") == "territory_cede" and isinstance(
            clause.get("regions"), (list, tuple)
        ):
            regions = [str(r) for r in (clause.get("regions") or []) if str(r)]
            base = {k: v for k, v in clause.items() if k not in ("regions", "region")}
            if not regions:
                # No usable region — keep one clause so the schema check still
                # surfaces the missing `region` rather than silently dropping it.
                normalized.append(base)
            else:
                for region in regions:
                    single = dict(base)
                    single["region"] = region
                    normalized.append(single)
            continue
        normalized.append(clause)
    return normalized


def _has_material_concession_terms(terms: Iterable[Mapping[str, Any]]) -> bool:
    return any(
        isinstance(term, Mapping) and term.get("type") != "peace"
        for term in (terms or [])
    )


def _term_lists_equal(
    left: Iterable[Mapping[str, Any]],
    right: Iterable[Mapping[str, Any]],
) -> bool:
    left_terms = [dict(t) for t in (left or []) if isinstance(t, Mapping)]
    right_terms = [dict(t) for t in (right or []) if isinstance(t, Mapping)]
    if len(left_terms) != len(right_terms):
        return False
    return all(_terms_equal(a, b) for a, b in zip(left_terms, right_terms))


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


# SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1 Concession Baseline.
# Spec §"Concession And Treaty Conversation Contract" pins the deterministic
# normal-gameplay algorithm: losing-side predicate uses
# `side_pressure_score <= LOSING_SIDE_PRESSURE_THRESHOLD`, gold candidate is
# the smallest strictly positive of (treasury - reserve, hard cap, acceptance
# gap * 100), and territory escalation uses BFS distance from the accepting
# leader's capital with deterministic tie-breaking.
LOSING_SIDE_PRESSURE_THRESHOLD = -20
CONCESSION_BASELINE_TREASURY_RESERVE = 500
CONCESSION_BASELINE_GOLD_HARD_CAP = 1500
CONCESSION_BASELINE_GOLD_FLOOR = 300
CONCESSION_BASELINE_BFS_MAX_DEPTH = 6

# Re-front Slice 1: a strong-lead threshold for authoring a TERRITORY demand,
# mirroring `generate_suggested_terms`' bilateral demand stage (which demands a
# border region at `war_score > 30`). Below this but above the direction margin
# the baseline demands gold only (a lighter ask); inside the margin it is a
# neutral peace.
DEMAND_TERRITORY_DIRECT_SCORE = 30

# Re-front Slice 1 / spec §8 OQ#5: per-court baseline DIRECTION dead-band.
# This thresholds a single court's raw `direct_score` (the int half of
# `select_direct_score(direct_scores[court])`, on the [-100, 100] war-score
# scale) to choose demand vs concede vs neutral-peace. It is deliberately a
# DISTINCT constant from `LOSING_SIDE_PRESSURE_THRESHOLD`: that one thresholds
# the power-weighted *side-pressure* scalar (a different scale/quantity), and
# reusing it here would re-introduce the scale conflation the spec's pressure
# model note exists to prevent. France clearly leads a court at
# `direct_score > +MARGIN` (demand), is clearly pressured by it at
# `direct_score < -MARGIN` (concede), and is in a neutral dead-band in between
# (white-peace floor).
DIRECT_SCORE_DIRECTION_MARGIN = 10

# Re-front Slice 2 / spec §11.3 + OQ#7: Tier-2 intent dials adjust MAGNITUDE at
# the court level (harsher = press the court / larger demands + smaller
# concessions; generous = ease the court / smaller demands + larger
# concessions). Each click steps gold by this amount and adds/removes whole
# clauses by COUNT — it NEVER swaps the requested region or payer IDENTITY (that
# is a Tier-3 request). Gold magnitude is bounded by the same hard cap the
# concession baseline uses so a runaway dial cannot author an absurd indemnity.
SETTLEMENT_DIAL_GOLD_STEP = 100


def _concession_baseline_payer_balance(world: Any, nation: str) -> int:
    """Return the payer nation's available gold balance (int)."""
    gold_map = getattr(world, "nation_gold", None)
    if isinstance(gold_map, Mapping):
        try:
            return int(gold_map.get(nation, 0) or 0)
        except (TypeError, ValueError):
            return 0
    return 0


def _concession_baseline_bfs_distance(
    world: Any,
    *,
    origin_region: str,
    target_region: str,
    max_depth: int = CONCESSION_BASELINE_BFS_MAX_DEPTH,
) -> Optional[int]:
    """Bounded BFS over `region.adjacent_regions` for capital-distance sort.

    Returns the shortest hop count from `origin_region` to `target_region`,
    or None when the target is unreachable inside `max_depth`. Spec §"Concession
    And Treaty Conversation Contract" line 284: regions unreachable inside the
    bound fall through to the lower priority sort keys rather than being
    excluded.
    """
    if not origin_region or not target_region:
        return None
    if origin_region == target_region:
        return 0
    regions = getattr(world, "regions", None)
    if not isinstance(regions, Mapping):
        return None
    if origin_region not in regions or target_region not in regions:
        return None
    visited = {origin_region}
    frontier = [origin_region]
    for depth in range(1, max_depth + 1):
        next_frontier: List[str] = []
        for current in frontier:
            region = regions.get(current)
            adjacent = (
                getattr(region, "adjacent_regions", None) or []
                if region is not None
                else []
            )
            for neighbour in adjacent:
                if neighbour in visited:
                    continue
                if neighbour == target_region:
                    return depth
                visited.add(neighbour)
                next_frontier.append(neighbour)
        frontier = next_frontier
        if not frontier:
            break
    return None


def _concession_baseline_select_transferable_region(
    world: Any,
    *,
    proposer_side_participants: Iterable[str],
    accepting_leader: str,
) -> Optional[str]:
    """Pick the deterministic concession region per the spec algorithm.

    Sort key: (BFS distance from `NATION_CAPITALS[accepting_leader]` when
    reachable inside `CONCESSION_BASELINE_BFS_MAX_DEPTH`, else a sentinel
    above all real depths), then economic income value (low first), then
    region name. Eligible regions are currently controlled by a proposer-side
    participant, not a capital, and not the historical home of any proposer-
    side participant (so a captured rival region returns to the accepting
    leader rather than the proposer ceding home territory).

    Historical home lookup goes through `region.get_starting_controllers()`
    rather than `region.starting_controller` because the Region class
    stores the starting controller only in the module-level
    REGIONS_DATA dict; the Region instance carries the live `controller`
    field only.
    """
    proposer_set = {str(n) for n in proposer_side_participants if n}
    if not proposer_set:
        return None
    from backend.models.region import NATION_CAPITALS, get_starting_controllers

    target_region = NATION_CAPITALS.get(accepting_leader)
    regions = getattr(world, "regions", None)
    if not isinstance(regions, Mapping):
        return None
    starting_controllers = get_starting_controllers()

    # Golden Rule 8: iterate per-participant via the cached
    # `world.get_nation_regions(...)` lookup and union the results
    # rather than scanning every region in the world. The pattern
    # mirrors `settlement_scoring._project_balance_after_settlement`
    # line 1589 and scales to the 1805 Europe map.
    candidate_names: set[str] = set()
    if hasattr(world, "get_nation_regions"):
        for participant in proposer_set:
            try:
                candidate_names.update(world.get_nation_regions(participant))
            except Exception:
                continue
    else:
        # Defensive fallback for tests that build a thin world stub
        # without the cached lookup helper. Behaviour matches the
        # original full scan.
        for name, region in regions.items():
            if str(getattr(region, "controller", "") or "") in proposer_set:
                candidate_names.add(name)

    candidates: List[Tuple[int, int, str]] = []
    unreachable_sentinel = CONCESSION_BASELINE_BFS_MAX_DEPTH + 1
    for name in candidate_names:
        region = regions.get(name)
        if region is None:
            continue
        if bool(getattr(region, "is_capital", False)):
            continue
        starting = str(starting_controllers.get(name, "") or "")
        if starting in proposer_set:
            continue
        distance = (
            _concession_baseline_bfs_distance(
                world,
                origin_region=str(target_region or ""),
                target_region=str(name),
            )
            if target_region
            else None
        )
        if distance is None:
            distance = unreachable_sentinel
        income_value = int(getattr(region, "income_value", 100) or 100)
        candidates.append((distance, income_value, str(name)))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][2]


def _format_concession_reasoning(
    *,
    proposer_leader: str,
    accepting_leader: str,
    gold_amount: Optional[int],
    region: Optional[str],
) -> str:
    """Humanized one-line rationale for the baseline draft.

    May 24, 2026 audit punch list Tier 2: the final reasoning string now
    routes through `settlement_concession_authored_talleyrand` (Voice
    Bible §16.1) instead of returning a hard-coded f-string. The parts
    construction logic above remains unchanged so the popup keeps
    rendering "pay X gold and cede Y" baseline summaries; only the
    surrounding Talleyrand frame moves into the template registry.
    """
    parts: List[str] = []
    if gold_amount is not None and gold_amount > 0:
        parts.append(
            f"{proposer_leader} would pay {accepting_leader} {gold_amount} gold"
        )
    if region:
        if parts:
            parts.append(f"and cede {region}")
        else:
            parts.append(f"{proposer_leader} would cede {region} to {accepting_leader}")
    if not parts:
        return ""
    summary = " ".join(parts)
    return resolve_settlement_voice_line(
        "settlement_concession_authored_talleyrand",
        summary=summary,
        accepting_leader=accepting_leader,
    ) or ("Talleyrand's draft: " + summary + " to improve acceptance.")


# SC-31 / G2-Slice-8 - Dependency clause eligibility helpers.
#
# These helpers are the source of truth for whether a vassalage /
# subjugation / liberation clause can be authored. They are reused by
# the POST preview validator, the surrender-preset algorithm, and by
# the SC-31 behavior tests so a single closed taxonomy of refusal codes
# governs both editor visibility and submit-time rejection.


def _resolve_war_sides(
    war_instance: Mapping[str, Any], nation: str
) -> Optional[str]:
    """Return ``"attackers"`` / ``"defenders"`` for ``nation`` on a war."""
    for side in VALID_SIDES:
        if nation in (war_instance.get(side) or []):
            return side
    return None


def _dependency_eligibility_payload(
    eligible: bool,
    *,
    refusal_code: str = "",
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    if eligible:
        payload: Dict[str, Any] = {"eligible": True, "refusal_code": None, "disabled_reason_display": None}
    else:
        payload = {
            "eligible": False,
            "refusal_code": refusal_code or "dependency_invalid",
            "disabled_reason_display": _error_display(refusal_code or "dependency_invalid"),
        }
    if extra:
        payload.update(dict(extra))
    return payload


def _check_vassalage_state(
    world: Any,
    *,
    war_instance: Mapping[str, Any],
    lord_nation: str,
    target_nation: str,
) -> Dict[str, Any]:
    """Shared pre-checks for vassalage / subjugation.

    Returns an eligible payload OR a refusal payload from the closed
    taxonomy ``dependency_*``. Power-cap is checked separately so
    callers can branch on `dependency_power_cap_blocked` independently.
    """
    if not lord_nation or not target_nation or lord_nation == target_nation:
        return _dependency_eligibility_payload(False, refusal_code="dependency_direction_invalid")
    lord_side = _resolve_war_sides(war_instance, lord_nation)
    target_side = _resolve_war_sides(war_instance, target_nation)
    if lord_side is None or target_side is None or lord_side == target_side:
        return _dependency_eligibility_payload(False, refusal_code="dependency_target_not_in_war")
    pair_key = world._make_diplo_key(lord_nation, target_nation)
    meta = (war_instance.get("diplo_key_meta") or {}).get(pair_key) or {}
    pair_status = str(meta.get("pair_status") or "")
    if pair_status not in ("war", "armistice"):
        return _dependency_eligibility_payload(False, refusal_code="dependency_target_not_in_war")
    vassals = getattr(world, "vassals", {}) or {}
    if target_nation in vassals:
        return _dependency_eligibility_payload(False, refusal_code="dependency_target_already_vassal")
    return _dependency_eligibility_payload(True)


def evaluate_subjugation_eligibility(
    world: Any,
    *,
    war_instance: Mapping[str, Any],
    lord_nation: str,
    target_nation: str,
) -> Dict[str, Any]:
    """Whether a ``subjugation`` clause may target ``target_nation``.

    Direction is canonical: ``target_nation`` is the prospective vassal
    (clause ``from``); ``lord_nation`` is the prospective lord (clause
    ``to``). Power-cap is enforced through `check_vassalage_power_cap`
    so a defeated giant cannot be forcibly vassalized by a smaller
    coalition member.
    """
    state = _check_vassalage_state(
        world,
        war_instance=war_instance,
        lord_nation=lord_nation,
        target_nation=target_nation,
    )
    if not state.get("eligible"):
        return state
    from backend.game_logic.diplomacy import check_vassalage_power_cap
    cap = check_vassalage_power_cap(world, lord_nation, target_nation)
    if not cap.get("allowed"):
        return _dependency_eligibility_payload(
            False,
            refusal_code="dependency_power_cap_blocked",
            extra={
                "lord_power": int(cap.get("lord_power", 0) or 0),
                "target_power": int(cap.get("target_power", 0) or 0),
                "power_pct": int(cap.get("pct", 0) or 0),
            },
        )
    return _dependency_eligibility_payload(
        True,
        extra={
            "lord_power": int(cap.get("lord_power", 0) or 0),
            "target_power": int(cap.get("target_power", 0) or 0),
            "power_pct": int(cap.get("pct", 0) or 0),
        },
    )


def evaluate_vassalage_eligibility(
    world: Any,
    *,
    war_instance: Mapping[str, Any],
    lord_nation: str,
    target_nation: str,
) -> Dict[str, Any]:
    """Whether a ``vassalage`` (treaty path) clause may target ``target_nation``.

    Treaty vassalization shares the same pre-checks as subjugation —
    direction, war state, not-already-vassal, and the power cap.
    """
    return evaluate_subjugation_eligibility(
        world,
        war_instance=war_instance,
        lord_nation=lord_nation,
        target_nation=target_nation,
    )


def evaluate_liberation_eligibility(
    world: Any,
    *,
    war_instance: Mapping[str, Any],
    vassal_nation: str,
    lord_nation: str,
    liberator: str,
) -> Dict[str, Any]:
    """Whether a ``liberation`` clause may free ``vassal_nation``.

    Liberation requires (a) the target is currently someone's vassal,
    (b) the declared ``lord_nation`` matches the current lord, and
    (c) the ``liberator`` is a recognized nation different from the
    current lord. The pair (lord vs liberator) must also currently be
    on opposite sides of the war so the clause has cross-side authority.
    """
    if not vassal_nation:
        return _dependency_eligibility_payload(
            False, refusal_code="liberation_target_not_vassal"
        )
    vassals = getattr(world, "vassals", {}) or {}
    state = vassals.get(vassal_nation)
    if not isinstance(state, Mapping):
        return _dependency_eligibility_payload(
            False, refusal_code="liberation_target_not_vassal"
        )
    current_lord = str(state.get("lord") or state.get("lord_nation") or "")
    if not current_lord or current_lord != lord_nation:
        return _dependency_eligibility_payload(
            False, refusal_code="liberation_lord_mismatch",
            extra={"current_lord": current_lord},
        )
    if not liberator or liberator == current_lord or liberator == vassal_nation:
        return _dependency_eligibility_payload(
            False, refusal_code="liberation_invalid_liberator"
        )
    # Liberator must be a known nation in the world; reject typos.
    known_nations: Set[str] = set()
    diplomatic_states = getattr(world, "diplomatic_states", {}) or {}
    for key in diplomatic_states:
        for part in str(key).split("|"):
            if part:
                known_nations.add(part)
    if liberator not in known_nations:
        return _dependency_eligibility_payload(
            False, refusal_code="liberation_invalid_liberator"
        )
    lord_side = _resolve_war_sides(war_instance, current_lord)
    liberator_side = _resolve_war_sides(war_instance, liberator)
    if lord_side is None or liberator_side is None or lord_side == liberator_side:
        return _dependency_eligibility_payload(
            False, refusal_code="liberation_invalid_liberator"
        )
    return _dependency_eligibility_payload(
        True, extra={"current_lord": current_lord},
    )


def _compute_surrender_preset(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    accepting_leader: str,
    proposer_side_leader: Optional[str],
    covered_enemy_participants: Iterable[str],
    side_pressure_score: Optional[int],
) -> Dict[str, Any]:
    """SC-31 / G2-Slice-8 surrender-preset algorithm.

    Deterministic ``[peace, dependency]`` preset where ``dependency`` is
    the harshest legal clause in the order
    ``subjugation -> vassalage`` against the accepting leader. The
    accepting leader is the prospective lord because surrender is the
    losing-side player handing dependency authority to the winning
    leader. Liberation is never authored by this preset (it is owned by
    the editor's standalone liberation control).

    Visibility reuses the concession-baseline losing-side predicate
    (``side_pressure_score <= LOSING_SIDE_PRESSURE_THRESHOLD``) AND
    requires at least one material dependency to be legal under the
    accepting leader's power cap. When the predicate passes but no
    legal dependency clause can be authored — the most common cause
    being the accepting leader being too small under POWER_CAP_RATIO —
    the affordance is hidden, not disabled, per the Disabled vs Hidden
    Affordance Policy at spec §"Disabled vs Hidden Affordance Policy".

    Result shape:

    - ``{"losing_for_surrender_preset": bool,
        "surrender_preset_visible": bool,
        "surrender_preset": {"terms": List[Clause], "reasoning": str,
                              "dependency_kind": str} | None,
        "surrender_preset_reason": str}``
    """
    if side_pressure_score is None:
        return {
            "losing_for_surrender_preset": False,
            "surrender_preset_visible": False,
            "surrender_preset": None,
            "surrender_preset_reason": "no_side_pressure_score",
        }
    losing = int(side_pressure_score) <= LOSING_SIDE_PRESSURE_THRESHOLD
    if not losing:
        return {
            "losing_for_surrender_preset": False,
            "surrender_preset_visible": False,
            "surrender_preset": None,
            "surrender_preset_reason": "not_losing_side",
        }
    if not proposer_side_leader or not accepting_leader:
        return {
            "losing_for_surrender_preset": True,
            "surrender_preset_visible": False,
            "surrender_preset": None,
            "surrender_preset_reason": "missing_leaders",
        }
    covered = {str(n) for n in (covered_enemy_participants or []) if n}
    if accepting_leader not in covered:
        # Spec line 277 requires clause targets to lie in
        # `covered_enemy_participants`; if the accepting leader is not
        # covered, dependency cannot legally beneficiary-route.
        return {
            "losing_for_surrender_preset": True,
            "surrender_preset_visible": False,
            "surrender_preset": None,
            "surrender_preset_reason": "accepting_leader_not_covered",
        }
    subjugation = evaluate_subjugation_eligibility(
        world,
        war_instance=war_instance,
        lord_nation=accepting_leader,
        target_nation=proposer_side_leader,
    )
    dependency_kind: Optional[str] = None
    if subjugation.get("eligible"):
        dependency_kind = "subjugation"
    else:
        vassalage = evaluate_vassalage_eligibility(
            world,
            war_instance=war_instance,
            lord_nation=accepting_leader,
            target_nation=proposer_side_leader,
        )
        if vassalage.get("eligible"):
            dependency_kind = "vassalage"
    if not dependency_kind:
        return {
            "losing_for_surrender_preset": True,
            "surrender_preset_visible": False,
            "surrender_preset": None,
            "surrender_preset_reason": "no_legal_dependency_clause",
        }
    preset_terms: List[Dict[str, Any]] = [
        {"type": "peace"},
        {
            "type": dependency_kind,
            "from": proposer_side_leader,
            "to": accepting_leader,
        },
    ]
    vassal_kind = "conquest vassal" if dependency_kind == "subjugation" else "treaty vassal"
    # May 24, 2026 audit punch list Tier 2: route the surrender preset
    # reasoning through `settlement_surrender_preset_authored_talleyrand`
    # (Voice Bible §16.1) instead of the prior hard-coded f-string. The
    # template ships the deliberate-surrender framing; the inline string
    # remains as the fallback when the template is missing/disabled.
    reasoning = resolve_settlement_voice_line(
        "settlement_surrender_preset_authored_talleyrand",
        war_label=str(war_id or "this war"),
        vassal_kind=vassal_kind,
        proposer_leader=str(proposer_side_leader),
        accepting_leader=str(accepting_leader),
    ) or (
        f"Talleyrand's draft: {proposer_side_leader} submits to {accepting_leader} "
        f"as a {vassal_kind} in exchange for ending the war."
    )
    return {
        "losing_for_surrender_preset": True,
        "surrender_preset_visible": True,
        "surrender_preset": {
            "terms": preset_terms,
            "reasoning": reasoning,
            "dependency_kind": dependency_kind,
        },
        "surrender_preset_reason": "material_dependency_available",
    }


def _compute_recurring_gold_preset(
    world: Any,
    *,
    war_instance: Mapping[str, Any],
    proposer_side_leader: Optional[str],
    accepting_leader: str,
    covered_enemy_participants: Iterable[str],
    side_pressure_score: Optional[int],
) -> Dict[str, Any]:
    """SC-33 / G2-Slice-9 recurring-gold draft for the settlement popup.

    The action exposes payer, recipient, amount, and duration in the
    staged payload and authors a legal finite `gold_per_turn` draft using
    the fixture-provided smoke values when present and otherwise the
    SC-33 validator minimums.
    """
    if "gold_per_turn" not in SETTLEMENT_LIVE_CLAUSE_TYPES:
        return {
            "losing_for_recurring_gold_preset": False,
            "recurring_gold_preset_visible": False,
            "recurring_gold_preset": None,
            "recurring_gold_preset_reason": "gold_per_turn_not_live",
        }
    if side_pressure_score is None:
        return {
            "losing_for_recurring_gold_preset": False,
            "recurring_gold_preset_visible": False,
            "recurring_gold_preset": None,
            "recurring_gold_preset_reason": "no_side_pressure_score",
        }
    losing = int(side_pressure_score) <= LOSING_SIDE_PRESSURE_THRESHOLD
    if not losing:
        return {
            "losing_for_recurring_gold_preset": False,
            "recurring_gold_preset_visible": False,
            "recurring_gold_preset": None,
            "recurring_gold_preset_reason": "not_losing_side",
        }
    if not proposer_side_leader or not accepting_leader:
        return {
            "losing_for_recurring_gold_preset": True,
            "recurring_gold_preset_visible": False,
            "recurring_gold_preset": None,
            "recurring_gold_preset_reason": "missing_leaders",
        }
    covered = {str(n) for n in (covered_enemy_participants or []) if n}
    if accepting_leader not in covered:
        return {
            "losing_for_recurring_gold_preset": True,
            "recurring_gold_preset_visible": False,
            "recurring_gold_preset": None,
            "recurring_gold_preset_reason": "accepting_leader_not_covered",
        }

    fixture = getattr(world, "settlement_smoke_fixture", None)
    fixture_meta = fixture if isinstance(fixture, Mapping) else {}

    def _bounded_int(raw: Any, default: int, *, low: int, high: int) -> int:
        try:
            value = int(raw)
        except (TypeError, ValueError):
            value = int(default)
        return max(low, min(high, value))

    amount = _bounded_int(
        fixture_meta.get("expected_recurring_amount_min"),
        GOLD_PER_TURN_MIN_AMOUNT,
        low=GOLD_PER_TURN_MIN_AMOUNT,
        high=10_000,
    )
    turns = _bounded_int(
        fixture_meta.get("expected_recurring_turns_min"),
        3,
        low=GOLD_PER_TURN_MIN_TURNS,
        high=GOLD_PER_TURN_MAX_TURNS,
    )
    preset_terms: List[Dict[str, Any]] = [
        {"type": "peace"},
        {
            "type": "gold_per_turn",
            "from": str(proposer_side_leader),
            "to": str(accepting_leader),
            "amount": int(amount),
            "turns": int(turns),
        },
    ]
    validation = validate_settlement_terms(
        preset_terms,
        world=world,
        war_instance=war_instance,
    )
    if not validation.get("valid"):
        return {
            "losing_for_recurring_gold_preset": True,
            "recurring_gold_preset_visible": False,
            "recurring_gold_preset": None,
            "recurring_gold_preset_reason": str(
                validation.get("error") or "recurring_gold_preset_invalid"
            ),
        }
    # May 24, 2026 audit punch list Tier 2: route the recurring-gold
    # preset reasoning through `settlement_recurring_gold_authored_talleyrand`
    # (Voice Bible §16.1) instead of the prior hard-coded f-string. The
    # template ships the projected-total framing ("ties the treasury for
    # years") that the f-string omitted.
    projected_total = int(amount) * int(turns)
    reasoning = resolve_settlement_voice_line(
        "settlement_recurring_gold_authored_talleyrand",
        payer=str(proposer_side_leader),
        amount_per_turn=str(int(amount)),
        recipient=str(accepting_leader),
        turns=str(int(turns)),
        projected_total=str(projected_total),
    ) or (
        f"Talleyrand's draft: {proposer_side_leader} would pay {accepting_leader} "
        f"{amount} gold per turn for {turns} turns ({projected_total} gold in total)."
    )
    return {
        "losing_for_recurring_gold_preset": True,
        "recurring_gold_preset_visible": True,
        "recurring_gold_preset": {
            "terms": preset_terms,
            "reasoning": reasoning,
            "amount": int(amount),
            "turns": int(turns),
            "payer": str(proposer_side_leader),
            "recipient": str(accepting_leader),
        },
        "recurring_gold_preset_reason": "finite_recurring_gold_available",
    }


def _compute_concession_baseline(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    accepting_leader: str,
    proposer_side_leader: Optional[str],
    covered_enemy_participants: Iterable[str],
    side_pressure_score: Optional[int],
    accept_threshold: int = 50,
    near_acceptance_floor: int = 35,
) -> Dict[str, Any]:
    """Return the deterministic losing-side concession baseline payload.

    Result shape:

    - ``{"losing_for_concession_baseline": bool, "concession_baseline_visible":
      bool, "concession_baseline": {"terms": List[Clause], "reasoning": str} |
      None, "concession_baseline_reason": str}``

    Visibility is the conjunction of the side-pressure predicate
    (``side_pressure_score <= LOSING_SIDE_PRESSURE_THRESHOLD``) and the
    algorithm's ability to author at least one material concession (gold,
    territory, or both). When the predicate passes but no material concession
    is possible, ``concession_baseline_visible`` is False and
    ``concession_baseline`` is None per spec §"Concession And Treaty
    Conversation Contract".
    """
    if side_pressure_score is None:
        return {
            "losing_for_concession_baseline": False,
            "concession_baseline_visible": False,
            "concession_baseline": None,
            "concession_baseline_reason": "no_side_pressure_score",
        }
    losing = int(side_pressure_score) <= LOSING_SIDE_PRESSURE_THRESHOLD
    if not losing:
        return {
            "losing_for_concession_baseline": False,
            "concession_baseline_visible": False,
            "concession_baseline": None,
            "concession_baseline_reason": "not_losing_side",
        }
    if not proposer_side_leader or not accepting_leader:
        return {
            "losing_for_concession_baseline": True,
            "concession_baseline_visible": False,
            "concession_baseline": None,
            "concession_baseline_reason": "missing_leaders",
        }
    covered = [str(n) for n in (covered_enemy_participants or []) if n]
    proposer_participants = list(war_instance.get(proposer_side) or [])
    peace_floor_result = calculate_common_peace_acceptance(
        world,
        war_id=war_id,
        war_instance=war_instance,
        proposer_side=proposer_side,
        accepting_side=accepting_side,
        accepting_leader=accepting_leader,
        proposer_side_leader=proposer_side_leader,
        covered_enemy_participants=covered,
        settlement_terms=[{"type": "peace"}],
    )
    peace_only_score = peace_floor_result.get("score")
    if peace_only_score is None:
        return {
            "losing_for_concession_baseline": True,
            "concession_baseline_visible": False,
            "concession_baseline": None,
            "concession_baseline_reason": "peace_only_score_unavailable",
        }
    acceptance_gap = max(0, int(accept_threshold) - int(peace_only_score))
    payer_balance = _concession_baseline_payer_balance(world, proposer_side_leader)
    treasury_candidate = payer_balance - CONCESSION_BASELINE_TREASURY_RESERVE
    gap_candidate = max(CONCESSION_BASELINE_GOLD_FLOOR, acceptance_gap * 100)
    # Affordability first: gold is offered only when treasury - 500 is
    # strictly positive (the spec's "available treasury above a 500-gold
    # reserve" / "strictly positive payable amount" promise). The 1500
    # hard cap and the gap-derived candidate cap the amount when the
    # payer can afford a non-trivial indemnity; they cannot themselves
    # mint a payment from a near-empty treasury.
    if treasury_candidate > 0:
        positive_candidates = [
            c for c in (treasury_candidate, CONCESSION_BASELINE_GOLD_HARD_CAP, gap_candidate)
            if c > 0
        ]
        gold_amount: Optional[int] = (
            int(min(positive_candidates)) if positive_candidates else None
        )
    else:
        gold_amount = None

    draft_terms: List[Dict[str, Any]] = [{"type": "peace"}]
    if gold_amount is not None:
        draft_terms.append({
            "type": "gold_indemnity",
            "from": proposer_side_leader,
            "to": accepting_leader,
            "amount": int(gold_amount),
        })

    hypothetical = (
        calculate_common_peace_acceptance(
            world,
            war_id=war_id,
            war_instance=war_instance,
            proposer_side=proposer_side,
            accepting_side=accepting_side,
            accepting_leader=accepting_leader,
            proposer_side_leader=proposer_side_leader,
            covered_enemy_participants=covered,
            settlement_terms=draft_terms,
        )
        if gold_amount is not None
        else peace_floor_result
    )
    hypothetical_score = hypothetical.get("score")
    escalate_to_territory = (
        hypothetical_score is None
        or int(hypothetical_score) < int(near_acceptance_floor)
    )
    region_choice: Optional[str] = None
    if escalate_to_territory:
        region_choice = _concession_baseline_select_transferable_region(
            world,
            proposer_side_participants=proposer_participants,
            accepting_leader=accepting_leader,
        )
        if region_choice:
            draft_terms.append({
                "type": "territory_cede",
                "from": proposer_side_leader,
                "to": accepting_leader,
                "region": region_choice,
            })

    material_terms = [t for t in draft_terms if t.get("type") != "peace"]
    if not material_terms:
        return {
            "losing_for_concession_baseline": True,
            "concession_baseline_visible": False,
            "concession_baseline": None,
            "concession_baseline_reason": "no_material_concession_available",
        }
    reasoning = _format_concession_reasoning(
        proposer_leader=str(proposer_side_leader),
        accepting_leader=str(accepting_leader),
        gold_amount=gold_amount,
        region=region_choice,
    )
    return {
        "losing_for_concession_baseline": True,
        "concession_baseline_visible": True,
        "concession_baseline": {
            "terms": draft_terms,
            "reasoning": reasoning,
        },
        "concession_baseline_reason": "material_concession_available",
    }


def _demand_baseline_select_region(
    world: Any,
    *,
    court: str,
    proposer_side_participants: Iterable[str],
) -> Optional[str]:
    """Pick the deterministic demand region a winning court would cede.

    Mirrors the bilateral demand-stage selection in
    ``generate_suggested_terms`` (border regions the enemy holds adjacent to
    the demanding side, excluding the enemy's capital — see
    ``diplomatic_templates.py`` stage 2b). The court keeps its capital; a
    border province changes hands. Deterministic tie-break is (income value
    low-first, region name) so the baseline regenerates identically across
    reruns. Falls back to any non-capital region the court controls when no
    border province exists, and returns None when the court holds only its
    capital (no transferable region).

    Golden Rule #8: holdings come from the cached
    ``world.get_nation_regions(...)`` lookups, not a full ``world.regions``
    scan.
    """
    regions = getattr(world, "regions", None)
    if not isinstance(regions, Mapping):
        return None
    from backend.models.region import NATION_CAPITALS

    court_capital = NATION_CAPITALS.get(court)
    try:
        court_regions = list(world.get_nation_regions(court))
    except Exception:
        court_regions = []
    if not court_regions:
        return None
    proposer_holdings: set[str] = set()
    for participant in proposer_side_participants:
        if not participant:
            continue
        try:
            proposer_holdings.update(world.get_nation_regions(participant))
        except Exception:
            continue
    border: List[Tuple[int, str]] = []
    fallback: List[Tuple[int, str]] = []
    for rname in court_regions:
        if rname == court_capital:
            continue
        region = regions.get(rname)
        if region is None:
            continue
        if bool(getattr(region, "is_capital", False)):
            continue
        income_value = int(getattr(region, "income_value", 100) or 100)
        fallback.append((income_value, str(rname)))
        adjacent = getattr(region, "adjacent_regions", None) or []
        if any(adj in proposer_holdings for adj in adjacent):
            border.append((income_value, str(rname)))
    pool = border or fallback
    if not pool:
        return None
    pool.sort()
    return pool[0][1]


def _score_court_for_baseline(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    court: str,
    proposer_side_leader: Optional[str],
    covered: Iterable[str],
    settlement_terms: Iterable[Mapping[str, Any]],
    side_pressure_result: Optional[Mapping[str, Any]],
    direct_scores: Optional[Mapping[str, Mapping[str, int]]],
) -> Optional[int]:
    """Score ``court``'s acceptance of a candidate baseline package.

    Shares the package-level ``side_pressure_result`` / ``direct_scores``
    pass (both term-independent) so the baseline build does not re-walk war
    scores per candidate; ``raw_total_harshness`` is recomputed per call
    because it depends on the candidate terms. Returns the int score or None
    on a scorer hard stop.
    """
    result = calculate_common_peace_acceptance(
        world,
        war_id=war_id,
        war_instance=war_instance,
        proposer_side=proposer_side,
        accepting_side=accepting_side,
        accepting_leader=court,
        proposer_side_leader=proposer_side_leader,
        covered_enemy_participants=list(covered),
        settlement_terms=[dict(t) for t in settlement_terms],
        side_pressure_result=side_pressure_result,
        direct_scores=direct_scores,
    )
    score = result.get("score")
    return int(score) if score is not None else None


def _relax_baseline_demands_for_package_harshness(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    proposer_side_leader: Optional[str],
    covered: List[str],
    combined_terms: List[Dict[str, Any]],
    per_court_baseline: Dict[str, Any],
    side_pressure_result: Optional[Mapping[str, Any]],
    direct_scores: Optional[Mapping[str, Mapping[str, int]]],
    near_acceptance_floor: int,
) -> List[Dict[str, Any]]:
    """Reconcile the per-court demand build with the WHOLE-package score.

    ``_demand_terms_for_court`` floor-checks each court against only that
    court's OWN slice of harshness, but the live surface
    (``compute_per_court_acceptance``) scores every covered court against the
    WHOLE package's ``raw_total_harshness`` (package-level, shared across
    courts). So in a multi-court demand a court can pass its slice floor yet
    land far below it once the table's combined harshness applies — a winning
    multilateral that should carry opens deeply rejected instead (the Gate-4
    smoke surfaced France-vs-Britain+Prussia opening at 5/50 with both courts
    holding out despite a decisive lead).

    Strip demand clauses — one per pass, from the worst demand-direction court
    still below the floor under the FULL package — until every demand court
    clears ``near_acceptance_floor``, or no demand clause remains for it (a
    genuine holdout at peace). Concessions are never stripped (they only raise
    the accepting court's acceptance, so stripping them would deepen a reject).
    Deterministic (sorted courts, territory-before-gold, then highest index);
    only REMOVES clauses, so the package stays valid-by-construction and within
    the clause cap. ``per_court_baseline`` terms are kept in lockstep so the
    display matches the scored package.
    """
    covered_set = {str(c) for c in covered}
    sorted_covered = sorted(covered_set)

    def _is_demand_clause(clause: Any, court: str) -> bool:
        return (
            isinstance(clause, Mapping)
            and clause.get("type") != "peace"
            and str(clause.get("from") or "") == court
        )

    terms = [dict(t) for t in combined_terms]
    # Bounded: at most one demand clause is removed per pass.
    for _ in range(len(terms) + 1):
        below: List[tuple] = []
        for court in sorted_covered:
            entry = per_court_baseline.get(court) or {}
            if entry.get("direction") != "demand":
                continue
            if not any(_is_demand_clause(c, court) for c in terms):
                continue  # nothing left to relax for this court
            score = _score_court_for_baseline(
                world, war_id=war_id, war_instance=war_instance,
                proposer_side=proposer_side, accepting_side=accepting_side,
                court=court, proposer_side_leader=proposer_side_leader,
                covered=sorted_covered, settlement_terms=terms,
                side_pressure_result=side_pressure_result, direct_scores=direct_scores,
            )
            if score is not None and int(score) < int(near_acceptance_floor):
                below.append((int(score), court))
        if not below:
            break
        below.sort()  # lowest score first; court name breaks ties
        worst = below[0][1]
        worst_idxs = [i for i, c in enumerate(terms) if _is_demand_clause(c, worst)]
        # Territory cession is the harshest lever — drop it before gold.
        territory_idxs = [
            i for i in worst_idxs if terms[i].get("type") == "territory_cede"
        ]
        drop_idx = (territory_idxs or worst_idxs)[-1]
        dropped = terms.pop(drop_idx)
        entry = per_court_baseline.get(worst)
        if isinstance(entry, dict):
            kept: List[Dict[str, Any]] = []
            removed = False
            for t in entry.get("terms") or []:
                if not removed and t == dropped:
                    removed = True
                    continue
                kept.append(t)
            entry["terms"] = kept
            entry["relaxed_for_package_harshness"] = True
    return terms


def compute_settlement_baseline(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    proposer_side_leader: Optional[str],
    covered_enemy_participants: Iterable[str],
    direct_scores: Optional[Mapping[str, Mapping[str, int]]] = None,
    side_pressure_result: Optional[Mapping[str, Any]] = None,
    accept_threshold: int = ACCEPTANCE_THRESHOLD,
    near_acceptance_floor: int = NEAR_ACCEPTANCE_FLOOR,
) -> Dict[str, Any]:
    """Re-front Slice 1 / spec §8 OQ#5 — the multi-party, per-court baseline.

    Generalizes ``_compute_concession_baseline`` (single losing-side draft)
    into a per-court draft that chooses DIRECTION per covered court from
    *that court's* direct war score, not the package-level side-pressure
    scalar (which cannot express per-court direction). For each covered
    court:

    - ``select_direct_score(direct_scores[court])`` returns a
      ``(direct_score, source)`` tuple, or ``None`` when the court has no
      active cross-side pair. A ``None`` court is surfaced as a per-court
      **hard stop** (matching the scorer's ``HARD_STOP_NO_DIRECT_WAR_SCORE``)
      — it is NOT neutral-floored.
    - ``direct_score > +DIRECT_SCORE_DIRECTION_MARGIN`` → **demand** (France
      leads the court): author a border-region cession + a modest affordable
      indemnity *from the court*, each kept only while the court stays at/above
      the **near-acceptance floor** (so a suggested demand never pushes a
      winning court into outright reject). If even white peace for the court is
      below the floor — the shared package-level ``base_side_pressure``
      dominates — no demand is suggested and the court eases/drops in the
      conversation.
    - ``direct_score < -DIRECT_SCORE_DIRECTION_MARGIN`` → **concede** (France
      is pressured by the court): the existing peace→gold→territory
      escalation paid *by* the proposer leader, escalated only until the
      court reaches the near-acceptance floor.
    - inside the dead-band → ``{"type": "peace"}`` neutral floor.

    Returns ``{"settlement_terms": [...], "per_court_baseline": {court: {...}},
    "hard_stop_courts": [...], "covered_enemy_participants": [...]}``. The
    combined ``settlement_terms`` is one shared ``{"type": "peace"}`` plus each
    court's material slice, capped at ``MAX_SETTLEMENT_CLAUSE_COUNT``. The
    draft is deterministic (sorted court order, no RNG — OQ#6) and
    valid-by-construction.
    """
    covered = sorted({str(n) for n in (covered_enemy_participants or []) if n})
    proposer_participants = [
        str(n) for n in (war_instance.get(proposer_side) or []) if n
    ]
    if direct_scores is None:
        direct_scores = compute_direct_scores_by_enemy(
            world,
            war_instance,
            proposer_side=proposer_side,
            covered_enemy_participants=covered,
        )
    if side_pressure_result is None:
        side_pressure_result = compute_side_pressure_score(
            world,
            war_instance,
            proposer_side=proposer_side,
            covered_enemy_participants=covered,
            direct_scores=direct_scores,
        )

    combined_terms: List[Dict[str, Any]] = [{"type": "peace"}]
    per_court_baseline: Dict[str, Any] = {}
    hard_stop_courts: List[str] = []

    for court in covered:
        selection = select_direct_score(direct_scores.get(court) or {})
        if selection is None:
            hard_stop_courts.append(court)
            per_court_baseline[court] = {
                "direction": "hard_stop",
                "direct_score": None,
                "terms": [],
                "reason": HARD_STOP_NO_DIRECT_WAR_SCORE,
            }
            continue
        direct_score, _source = selection
        budget_remaining = MAX_SETTLEMENT_CLAUSE_COUNT - len(combined_terms)
        court_terms: List[Dict[str, Any]] = []

        if direct_score > DIRECT_SCORE_DIRECTION_MARGIN:
            direction = "demand"
            # Author demands on a court France leads, mirroring
            # `generate_suggested_terms`' bilateral demand stage (border-region
            # demand at a strong lead + a modest affordable indemnity). The
            # helper is FLOOR-AWARE: it keeps a demand clause only while the
            # court stays at/above the near-acceptance floor, and suggests
            # nothing when even white peace for the court is below the floor
            # (`base_side_pressure` is package-level — §11.2 — so a led court can
            # share a negative package pressure). So a suggested demand never
            # pushes a winning court into outright reject (§8 OQ#5). Suggestions,
            # not impositions — the player can press harder or replace them in
            # Tier 3.
            court_terms = _demand_terms_for_court(
                world, war_id=war_id, war_instance=war_instance,
                proposer_side=proposer_side, accepting_side=accepting_side,
                court=court, proposer_side_leader=proposer_side_leader,
                proposer_side_participants=proposer_participants,
                covered=covered, side_pressure_result=side_pressure_result,
                direct_scores=direct_scores, direct_score=int(direct_score),
                near_acceptance_floor=near_acceptance_floor,
                budget_remaining=budget_remaining,
            )
        elif direct_score < -DIRECT_SCORE_DIRECTION_MARGIN:
            direction = "concede"
            court_terms = _concession_terms_for_court(
                world, war_id=war_id, war_instance=war_instance,
                proposer_side=proposer_side, accepting_side=accepting_side,
                court=court, proposer_side_leader=proposer_side_leader,
                covered=covered, side_pressure_result=side_pressure_result,
                direct_scores=direct_scores, near_acceptance_floor=near_acceptance_floor,
                budget_remaining=budget_remaining,
            )
        else:
            direction = "peace"

        per_court_baseline[court] = {
            "direction": direction,
            "direct_score": int(direct_score),
            "terms": [dict(t) for t in court_terms],
            "reason": direction,
        }
        for term in court_terms:
            if len(combined_terms) >= MAX_SETTLEMENT_CLAUSE_COUNT:
                break
            combined_terms.append(term)

    # Each court's demand slice was floor-checked against its OWN harshness, but
    # the surface scores every court against the WHOLE package's harshness; relax
    # over-demanded courts so the assembled table clears the near-acceptance
    # floor it was built to (no spurious all-holdout opening on a winning war).
    combined_terms = _relax_baseline_demands_for_package_harshness(
        world,
        war_id=war_id,
        war_instance=war_instance,
        proposer_side=proposer_side,
        accepting_side=accepting_side,
        proposer_side_leader=proposer_side_leader,
        covered=covered,
        combined_terms=combined_terms,
        per_court_baseline=per_court_baseline,
        side_pressure_result=side_pressure_result,
        direct_scores=direct_scores,
        near_acceptance_floor=near_acceptance_floor,
    )

    return {
        "settlement_terms": combined_terms,
        "per_court_baseline": per_court_baseline,
        "hard_stop_courts": hard_stop_courts,
        "covered_enemy_participants": covered,
    }


def _concession_terms_for_court(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    court: str,
    proposer_side_leader: Optional[str],
    covered: Iterable[str],
    side_pressure_result: Optional[Mapping[str, Any]],
    direct_scores: Optional[Mapping[str, Mapping[str, int]]],
    near_acceptance_floor: int,
    budget_remaining: int,
) -> List[Dict[str, Any]]:
    """Author proposer-side concessions (gold, then territory) that move a
    losing-direction ``court`` toward the near-acceptance floor.

    Mirrors ``_compute_concession_baseline``'s escalation but scoped to one
    court and sharing the memoized package-level score inputs. Returns the
    material clauses the proposer leader pays/cedes to the court (no
    ``{"type": "peace"}`` — the caller owns the shared package peace).
    """
    if not proposer_side_leader or budget_remaining <= 0:
        return []
    terms: List[Dict[str, Any]] = []
    peace_score = _score_court_for_baseline(
        world, war_id=war_id, war_instance=war_instance,
        proposer_side=proposer_side, accepting_side=accepting_side,
        court=court, proposer_side_leader=proposer_side_leader,
        covered=covered, settlement_terms=[{"type": "peace"}],
        side_pressure_result=side_pressure_result, direct_scores=direct_scores,
    )
    if peace_score is not None and peace_score >= near_acceptance_floor:
        return []
    # Gold escalation: smallest strictly positive of (treasury - reserve,
    # hard cap, gap * 100), affordability-gated.
    payer_balance = _concession_baseline_payer_balance(world, proposer_side_leader)
    treasury_candidate = payer_balance - CONCESSION_BASELINE_TREASURY_RESERVE
    acceptance_gap = max(0, int(near_acceptance_floor) - int(peace_score or 0))
    gap_candidate = max(CONCESSION_BASELINE_GOLD_FLOOR, acceptance_gap * 100)
    if treasury_candidate > 0:
        positive = [
            c for c in (treasury_candidate, CONCESSION_BASELINE_GOLD_HARD_CAP, gap_candidate)
            if c > 0
        ]
        gold_amount = int(min(positive)) if positive else None
    else:
        gold_amount = None
    if gold_amount is not None and len(terms) < budget_remaining:
        terms.append({
            "type": "gold_indemnity",
            "from": proposer_side_leader,
            "to": court,
            "amount": int(gold_amount),
        })
    gold_score = _score_court_for_baseline(
        world, war_id=war_id, war_instance=war_instance,
        proposer_side=proposer_side, accepting_side=accepting_side,
        court=court, proposer_side_leader=proposer_side_leader,
        covered=covered, settlement_terms=[{"type": "peace"}] + terms,
        side_pressure_result=side_pressure_result, direct_scores=direct_scores,
    )
    escalate_to_territory = (
        gold_score is None or int(gold_score) < int(near_acceptance_floor)
    )
    if escalate_to_territory and len(terms) < budget_remaining:
        region = _concession_baseline_select_transferable_region(
            world,
            proposer_side_participants=list(war_instance.get(proposer_side) or []),
            accepting_leader=court,
        )
        if region:
            terms.append({
                "type": "territory_cede",
                "from": proposer_side_leader,
                "to": court,
                "region": region,
            })
    return terms


def _demand_terms_for_court(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    court: str,
    proposer_side_leader: Optional[str],
    proposer_side_participants: Iterable[str],
    covered: Iterable[str],
    side_pressure_result: Optional[Mapping[str, Any]],
    direct_scores: Optional[Mapping[str, Mapping[str, int]]],
    direct_score: int,
    near_acceptance_floor: int,
    budget_remaining: int,
) -> List[Dict[str, Any]]:
    """Author demands (territory, then gold) on a court France leads, keeping
    that court at/above the near-acceptance floor.

    Mirrors `generate_suggested_terms`' bilateral demand stage (border-region
    demand at a strong lead + a modest affordable indemnity) but is
    **floor-aware**: a candidate clause is kept only when the court still
    scores at/above ``near_acceptance_floor`` with it (spec §8 OQ#5 — "never
    suggest a demand that makes a court outright reject"). Because
    ``base_side_pressure`` is package-level (§11.2), a court France leads can
    share a middling/negative package pressure; if even white peace for the
    court is below the floor, NO demand is suggested (the court is an
    ease/drop holdout regardless of terms, not a court the demand should push
    further down). Returns the kept demand clauses (no ``{"type": "peace"}`` —
    the caller owns the shared package peace).
    """
    if not proposer_side_leader or budget_remaining <= 0:
        return []
    peace_score = _score_court_for_baseline(
        world, war_id=war_id, war_instance=war_instance,
        proposer_side=proposer_side, accepting_side=accepting_side,
        court=court, proposer_side_leader=proposer_side_leader,
        covered=covered, settlement_terms=[{"type": "peace"}],
        side_pressure_result=side_pressure_result, direct_scores=direct_scores,
    )
    if peace_score is None or int(peace_score) < int(near_acceptance_floor):
        # Shared package pressure already rejects this court at white peace; a
        # demand can only make it worse. Suggest nothing — never push below the
        # floor (the court eases/drops in the conversation).
        return []
    kept: List[Dict[str, Any]] = []

    def _stays_acceptable(candidate: List[Dict[str, Any]]) -> bool:
        score = _score_court_for_baseline(
            world, war_id=war_id, war_instance=war_instance,
            proposer_side=proposer_side, accepting_side=accepting_side,
            court=court, proposer_side_leader=proposer_side_leader,
            covered=covered, settlement_terms=[{"type": "peace"}] + candidate,
            side_pressure_result=side_pressure_result, direct_scores=direct_scores,
        )
        return score is not None and int(score) >= int(near_acceptance_floor)

    # Border-region cession — strong lead only, mirroring the bilateral demand
    # stage (`war_score > 30`). Kept only if the court stays acceptable.
    if direct_score > DEMAND_TERRITORY_DIRECT_SCORE and len(kept) < budget_remaining:
        region = _demand_baseline_select_region(
            world,
            court=court,
            proposer_side_participants=proposer_side_participants,
        )
        if region:
            candidate = kept + [{
                "type": "territory_cede",
                "from": court,
                "to": proposer_side_leader,
                "region": region,
            }]
            if _stays_acceptable(candidate):
                kept = candidate
    # Modest affordable indemnity from the court. Kept only if acceptable.
    court_balance = _concession_baseline_payer_balance(world, court)
    gold_candidate = min(
        court_balance - CONCESSION_BASELINE_TREASURY_RESERVE,
        CONCESSION_BASELINE_GOLD_FLOOR,
    )
    if gold_candidate > 0 and len(kept) < budget_remaining:
        candidate = kept + [{
            "type": "gold_indemnity",
            "from": court,
            "to": proposer_side_leader,
            "amount": int(gold_candidate),
        }]
        if _stays_acceptable(candidate):
            kept = candidate
    return kept


def _court_direction_summary(
    court: str,
    proposer_side_leader: Optional[str],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> str:
    """Humanize one court's slice of the package for the PROPOSE per-court row.

    Reads the clauses that touch ``court`` and renders a one-line
    "Demanded: <region> + <amount>g" / "Conceded: <region> + <amount>g" /
    "White peace" summary. Presentation only; never feeds the scored result.
    """
    demanded_regions: List[str] = []
    conceded_regions: List[str] = []
    demanded_gold = 0
    conceded_gold = 0
    for term in settlement_terms:
        if not isinstance(term, Mapping):
            continue
        ttype = term.get("type")
        frm = str(term.get("from") or "")
        to = str(term.get("to") or "")
        if ttype == "territory_cede":
            if frm == court:
                demanded_regions.append(str(term.get("region") or ""))
            elif to == court:
                conceded_regions.append(str(term.get("region") or ""))
        elif ttype in ("gold_indemnity", "gold_lump", "gold_per_turn"):
            amount = int(term.get("amount", 0) or 0)
            if frm == court:
                demanded_gold += amount
            elif to == court:
                conceded_gold += amount
    demand_parts: List[str] = []
    demand_parts.extend(r for r in demanded_regions if r)
    if demanded_gold > 0:
        demand_parts.append(f"{demanded_gold}g")
    concede_parts: List[str] = []
    concede_parts.extend(r for r in conceded_regions if r)
    if conceded_gold > 0:
        concede_parts.append(f"{conceded_gold}g")
    if demand_parts and concede_parts:
        return f"Demanded: {' + '.join(demand_parts)}; Conceded: {' + '.join(concede_parts)}"
    if demand_parts:
        return f"Demanded: {' + '.join(demand_parts)}"
    if concede_parts:
        return f"Conceded: {' + '.join(concede_parts)}"
    return "White peace"


def compute_per_court_acceptance(
    world: Any,
    *,
    war_id: str,
    war_instance: Mapping[str, Any],
    proposer_side: str,
    accepting_side: str,
    proposer_side_leader: Optional[str],
    covered_enemy_participants: Iterable[str],
    settlement_terms: Iterable[Mapping[str, Any]],
    accept_threshold: int = ACCEPTANCE_THRESHOLD,
    direct_scores: Optional[Mapping[str, Mapping[str, int]]] = None,
    side_pressure_result: Optional[Mapping[str, Any]] = None,
    raw_total_harshness: Optional[float] = None,
    balance_projection: Optional[Mapping[str, Any]] = None,
    previous_bands: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    """Re-front Slice 1 / spec §11.2 — the per-court acceptance aggregator.

    One ``calculate_common_peace_acceptance`` call per covered court over a
    single shared score pass (``direct_scores`` + ``side_pressure_result`` +
    ``raw_total_harshness`` are package-level and computed once — Golden Rule
    #8). Each call VARIES ``accepting_leader=<that court>`` while HOLDING
    ``covered_enemy_participants=<the full covered set>`` constant, so every
    court's burden / abandonment components still reflect the whole table
    (principle 5 — Talleyrand reasons across the table).

    Re-front Slice 2 / spec §15 F-5 — the balance projection
    (``project_balance_after_settlement``) is also package-level (independent
    of ``accepting_leader``), so the aggregator computes it ONCE for the whole
    covered loop and injects it into each scorer call via ``balance_projection``
    rather than letting the scorer recompute it per court (O(N) projections).
    A caller may pass a pre-computed ``balance_projection`` (one dial/coverage
    action shares it across re-scores); when ``None`` it is computed once here.

    A covered court with no active cross-side pair (``select_direct_score``
    returns ``None``) is surfaced as a per-court hard-stop row (``total=null``)
    rather than poisoning the shared side-pressure for the scoreable courts.

    ``overall_acceptance.carries`` is True iff *every* covered court has a
    non-null ``total`` at/above the accept threshold AND no per-court
    ``hard_stops`` (spec §11.4 — the per-covered-court ratification gate).
    """
    covered = sorted({str(n) for n in (covered_enemy_participants or []) if n})
    terms = [dict(t) for t in (settlement_terms or []) if isinstance(t, Mapping)]
    if direct_scores is None:
        direct_scores = compute_direct_scores_by_enemy(
            world,
            war_instance,
            proposer_side=proposer_side,
            covered_enemy_participants=covered,
        )
    scoreable = [
        court for court in covered
        if select_direct_score(direct_scores.get(court) or {}) is not None
    ]
    if side_pressure_result is None:
        # Compute pressure over the scoreable subset so a no-direct-score
        # court does not bubble a hard stop that poisons every scorer call.
        side_pressure_result = compute_side_pressure_score(
            world,
            war_instance,
            proposer_side=proposer_side,
            covered_enemy_participants=scoreable,
            direct_scores={c: dict(direct_scores.get(c) or {}) for c in scoreable},
        )
    if raw_total_harshness is None:
        raw_total_harshness = calculate_raw_treaty_harshness(
            {"clauses": [], "demands": terms}
        )
    if balance_projection is None and scoreable:
        # Slice 2 / §15 F-5: the projection is package-level (no leader arg),
        # so compute it ONCE for the whole per-court loop and inject it into
        # each scorer call instead of letting the scorer recompute it per
        # court. A hard-stop-only covered set (no scoreable court) needs no
        # projection.
        balance_projection = project_balance_after_settlement(
            world, war_id=war_id, settlement_terms=terms,
        )

    per_court: List[Dict[str, Any]] = []
    holdout_courts: List[str] = []
    carries = True
    previous_bands = previous_bands or {}

    for court in covered:
        if court not in scoreable:
            band = "reject"
            per_court.append({
                "nation": court,
                "band": band,
                "band_display": acceptance_band_display(band),
                "total": None,
                "threshold": int(accept_threshold),
                "verdict": "reject",
                "top_blocker_display": acceptance_band_display(band),
                "direction_summary": _court_direction_summary(
                    court, proposer_side_leader, terms,
                ),
                "previous_band": previous_bands.get(court),
                "delta_display": None,
                "hard_stops": [
                    {"reason": HARD_STOP_NO_DIRECT_WAR_SCORE, "enemy": court}
                ],
            })
            carries = False
            holdout_courts.append(court)
            continue
        result = calculate_common_peace_acceptance(
            world,
            war_id=war_id,
            war_instance=war_instance,
            proposer_side=proposer_side,
            accepting_side=accepting_side,
            accepting_leader=court,
            proposer_side_leader=proposer_side_leader,
            covered_enemy_participants=covered,
            settlement_terms=terms,
            side_pressure_result=side_pressure_result,
            direct_scores=direct_scores,
            raw_total_harshness=raw_total_harshness,
            balance_projection=balance_projection,
        )
        enriched = _enrich_acceptance_display(result)
        total = result.get("score")
        band = str(enriched.get("band") or result.get("verdict") or "reject")
        hard_stops = list(result.get("hard_stops") or [])
        court_passes = (
            total is not None and int(total) >= int(accept_threshold) and not hard_stops
        )
        below_threshold = total is None or int(total) < int(accept_threshold)
        top_blocker = enriched.get("top_blocker_display") if below_threshold else None
        previous_band = previous_bands.get(court)
        delta_display = None
        if previous_band and previous_band != band:
            delta_display = (
                f"{court} {acceptance_band_display(previous_band)} "
                f"→ {acceptance_band_display(band)}"
            )
        per_court.append({
            "nation": court,
            "band": band,
            "band_display": acceptance_band_display(band),
            "total": int(total) if total is not None else None,
            "threshold": int(accept_threshold),
            "verdict": result.get("verdict"),
            "top_blocker_display": top_blocker,
            "direction_summary": _court_direction_summary(
                court, proposer_side_leader, terms,
            ),
            "previous_band": previous_band,
            "delta_display": delta_display,
            "hard_stops": hard_stops,
        })
        if not court_passes:
            carries = False
            holdout_courts.append(court)

    if not covered:
        carries = False
    if carries:
        summary_display = "This peace carries."
    elif len(holdout_courts) == 1:
        summary_display = f"{holdout_courts[0]} is the holdout."
    elif holdout_courts:
        summary_display = f"{len(holdout_courts)} courts hold out."
    else:
        summary_display = "No covered courts."
    return {
        "per_court_acceptance": per_court,
        "overall_acceptance": {
            "carries": bool(carries),
            "holdout_courts": holdout_courts,
            "summary_display": summary_display,
        },
    }


def _redial_settlement_terms(
    *,
    terms: Iterable[Mapping[str, Any]],
    scope_courts: Iterable[str],
    direction: str,
    proposer_side_leader: Optional[str],
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

    A FOCUSED dial (exactly one scoped court) with no material slice for that
    court seeds a single modest gold clause in the dial direction (press → a
    demand FROM the court; ease → a concession the proposer PAYS to it) so the
    one-click ``Ease <holdout>`` / ``press <court>`` affordance actually moves
    the needle — but only while the package is under
    ``MAX_SETTLEMENT_CLAUSE_COUNT`` and the proposer leader is known (both seed
    shapes reference the leader). A capped or leaderless package yields a no-op
    redraft rather than an over-cap / malformed one, so the focused click always
    produces a valid-by-construction package. Multi-court whole-table dials
    (scope ≥ 2) never seed — they only steer existing terms. Clauses that touch
    no scoped court — including the shared ``{"type": "peace"}`` — are copied
    through untouched.
    """
    scope = {str(n) for n in (scope_courts or []) if n}
    leader = str(proposer_side_leader or "")
    out: List[Dict[str, Any]] = []
    touched: Set[str] = set()
    for term in terms:
        if not isinstance(term, Mapping):
            continue
        clause = dict(term)
        ttype = str(clause.get("type") or "")
        frm = str(clause.get("from") or "")
        to = str(clause.get("to") or "")
        court = frm if frm in scope else (to if to in scope else "")
        if not court or ttype == "peace":
            out.append(clause)
            continue
        touched.add(court)
        is_demand = frm == court  # the court pays/cedes => a demand on it
        if ttype in ("gold_indemnity", "gold_lump", "gold_per_turn"):
            amount = int(clause.get("amount", 0) or 0)
            # Grow on harsher-demand / generous-concession; shrink otherwise.
            if (direction == "harsher") == is_demand:
                amount = min(
                    amount + SETTLEMENT_DIAL_GOLD_STEP,
                    CONCESSION_BASELINE_GOLD_HARD_CAP,
                )
            else:
                amount -= SETTLEMENT_DIAL_GOLD_STEP
            if amount <= 0:
                continue  # drop the clause (count down) — never below zero
            clause["amount"] = int(amount)
            out.append(clause)
            continue
        if ttype.startswith("territory"):
            # Territory is binary (count), never identity. Harsher keeps a
            # demand and drops a concession; generous the mirror.
            drop = (not is_demand) if direction == "harsher" else is_demand
            if drop:
                continue
            out.append(clause)
            continue
        # Identity-bearing clause types (liberation, alliance, vassalage, …) are
        # not Tier-2 magnitude levers — pass them through unchanged.
        out.append(clause)
    # Focused-dial seed. Only fires for exactly one scoped court that the dial
    # left untouched, only while a proposer leader is known (both seed shapes
    # reference the leader — symmetric guard), and only while the package is
    # under the clause cap. A capped package yields a NO-OP redraft rather than
    # an over-cap one, so the one-click ``Press <court>`` / ``Ease <court>``
    # affordance always produces a valid-by-construction package (it never
    # authors a draft the restage revalidation would reject for
    # ``max_clause_count_exceeded``).
    if len(scope) == 1 and leader:
        for court in sorted(scope - touched):
            if len(out) >= MAX_SETTLEMENT_CLAUSE_COUNT:
                break  # hard cap honored — no over-cap seed
            if direction == "harsher":
                out.append({
                    "type": "gold_indemnity", "from": court, "to": leader,
                    "amount": int(SETTLEMENT_DIAL_GOLD_STEP),
                })
            else:
                out.append({
                    "type": "gold_indemnity", "from": leader, "to": court,
                    "amount": int(SETTLEMENT_DIAL_GOLD_STEP),
                })
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
        elif str(row.get("band") or "") == "accept":
            press.append(nation)
    parts: List[str] = []
    if press:
        parts.append("press " + ", ".join(sorted(press)))
    if ease:
        parts.append("ease " + ", ".join(sorted(ease)))
    if not parts:
        return ""
    return "I'd " + " and ".join(parts) + ", Sire — the table is yours to shape."


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
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": action,
            "war_id": war_id,
            "error": "submitted_terms_failed_revalidation",
            "error_display": _error_display("submitted_terms_failed_revalidation"),
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
    drafts = getattr(world, "pending_settlement_drafts", None)
    if drafts is None:
        world.pending_settlement_drafts = {}
        drafts = world.pending_settlement_drafts
    drafts[war_id] = [dict(t) for t in terms]
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
    for key in ("ignored_participants", "remaining_wars", "focused_court"):
        if extra and key in extra:
            result[key] = extra[key]
    return result


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


# Re-front Slice 3 §12 V3: clause types that move value across the war and so
# must bind two participants on OPPOSITE war sides (demand burdens the accepting
# side; concession burdens the proposer side — either way `from`/`to` straddle
# the line). Dependency clauses (vassalage/subjugation/liberation) carry their
# own cross-side eligibility checks and are excluded here.
_CROSS_SIDE_TRANSFER_CLAUSE_TYPES = frozenset(
    {"territory_cede", "gold_indemnity", "gold_per_turn", "forced_alliance"}
)


def _clause_role_nations(clause: Mapping[str, Any]) -> List[str]:
    """Enemy/proposer courts a clause binds, for the V2 coverage check.

    Every clause binds ``from``/``to`` except ``liberation``, which binds
    its ``lord_nation`` (the covered enemy losing the vassal) and
    ``liberator`` (a proposer-side participant). ``vassal_nation`` is
    deliberately excluded: it is the freed party, not a court bound into
    the settlement, and ``evaluate_liberation_eligibility`` (§12 V4) never
    requires it to be a war participant — so checking it here would
    over-reject valid liberations of a non-participant vassal. ``peace``
    binds nothing.
    """
    if str(clause.get("type") or "") == "liberation":
        keys = ("lord_nation", "liberator")
    else:
        keys = ("from", "to")
    return [
        str(clause.get(k)).strip()
        for k in keys
        if str(clause.get(k) or "").strip()
    ]


def validate_settlement_terms(
    terms: Any,
    *,
    actor_nation: Optional[str] = None,
    player_nation: Optional[str] = None,
    proposer_side: Optional[str] = None,
    actor_side_in_war: Optional[str] = None,
    covered_enemy_participants: Optional[Iterable[str]] = None,
    world: Any = None,
    war_instance: Optional[Mapping[str, Any]] = None,
    enforce_solvency: bool = True,
) -> Dict[str, Any]:
    """SC-1 POST preview clause validation.

    Returns {"valid": True} or {"valid": False, "error": ..., "error_index": ...,
    "disabled_reason_display": ...}.

    SC-31 / G2-Slice-8: when ``world`` and ``war_instance`` are supplied,
    dependency-clause direction, target eligibility, and power-cap legality
    are additionally enforced. Hidden clause types are never live in
    `CLAUSE_CONTROL_SCHEMA`, but illegal-by-state dependency clauses
    submitted via tampered payloads return canonical error codes:

    - ``dependency_direction_invalid`` — vassalage / subjugation use
      ``from = vassal/subjugated, to = lord``; the validator rejects
      reversed projections.
    - ``dependency_target_not_in_war`` — vassalage / subjugation target
      must currently be at WAR or ARMISTICE with the lord on the war
      instance.
    - ``dependency_target_already_vassal`` — vassalage / subjugation
      target is already someone's vassal.
    - ``dependency_power_cap_blocked`` — lord power is not at least
      ``POWER_CAP_RATIO`` × target power.
    - ``liberation_target_not_vassal`` — liberation target is not
      currently a vassal of any lord.
    - ``liberation_lord_mismatch`` — declared ``lord_nation`` does not
      match the current lord of ``vassal_nation``.
    - ``liberation_invalid_liberator`` — ``liberator`` is missing,
      equal to the current lord, or not a recognized nation.

    Re-front Slice 3 §12 multi-party cross-court validity rules (defense in
    depth at POST-preview, Submit revalidation, and dial/coverage restage):

    - ``region_double_promised`` — the same region appears in more than one
      ``territory_cede`` clause (V1). Always enforced (structural).
    - ``clause_target_uncovered`` — a clause names a court that is neither
      proposer-side nor in ``covered_enemy_participants`` (V2). Enforced when
      ``war_instance`` is supplied and a ``covered_enemy_participants`` /
      ``proposer_side`` context lets the allowed set be derived.
    - ``clause_side_mismatch`` — a value-transfer clause's ``from`` and ``to``
      are not on opposite, known war sides (V3). Enforced when ``war_instance``
      is supplied.

    ``enforce_solvency`` gates only the authoring-time gold budget/solvency
    check (``_check_gold_payment_budget_conflict``). It is ``True`` for every
    authoring caller (POST-preview / Submit / restage). The ratify-time
    defense-in-depth revalidation passes ``False`` because the apply path
    *clamps* a gold transfer to the payer's available balance rather than
    blocking it (a winning settlement is never voided by a payer who has since
    spent down), so re-running the solvency gate there would wrongly reject a
    clamp-valid package. Every other rule — structural (V1), coverage (V2),
    war-side (V3), self-reference/dependency eligibility (V4) — still runs.
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
                        "conflicting_index": terms.index(ca),
                        "disabled_reason_display": _error_display("duplicate_or_conflicting_clauses"),
                    }

    # Re-front Slice 3 §12 V1: no region promised to two courts. Each region may
    # appear in at most one `territory_cede` clause regardless of from/to. This
    # is structural (no world/war_instance needed) so it always runs.
    seen_regions: Dict[str, int] = {}
    for idx, clause in enumerate(terms):
        if clause.get("type") != "territory_cede":
            continue
        region = str(clause.get("region") or "")
        if not region:
            continue
        if region in seen_regions:
            return {
                "valid": False,
                "error": "region_double_promised",
                "error_index": idx,
                "conflicting_index": seen_regions[region],
                "disabled_reason_display": _error_display("region_double_promised"),
            }
        seen_regions[region] = idx

    # Re-front Slice 3 §12 V2/V3: cross-court binding + war-side validity. Both
    # need the live `war_instance` to resolve sides; bare schema-only callers
    # (no war_instance) skip them, matching the dependency-clause gate below.
    if isinstance(war_instance, Mapping) and war_instance:
        covered_set = {
            str(n).strip()
            for n in (covered_enemy_participants or [])
            if str(n).strip()
        }
        ps = str(proposer_side or "")
        proposer_participants: Set[str] = (
            {
                str(n).strip()
                for n in (war_instance.get(ps) or [])
                if str(n).strip()
            }
            if ps in VALID_SIDES
            else set()
        )
        # V2: every clause role nation must be proposer-side or covered. Only
        # enforced when BOTH the proposer side and the covered set are known, so
        # a partial-context caller is never over-constrained.
        if proposer_participants and covered_set:
            allowed = proposer_participants | covered_set
            for idx, clause in enumerate(terms):
                for role_nation in _clause_role_nations(clause):
                    if role_nation not in allowed:
                        return {
                            "valid": False,
                            "error": "clause_target_uncovered",
                            "error_index": idx,
                            "uncovered_nation": role_nation,
                            "disabled_reason_display": _error_display(
                                "clause_target_uncovered"
                            ),
                        }
        # V3: value-transfer clauses must straddle opposite, known war sides.
        for idx, clause in enumerate(terms):
            if clause.get("type") not in _CROSS_SIDE_TRANSFER_CLAUSE_TYPES:
                continue
            frm = str(clause.get("from") or "")
            to = str(clause.get("to") or "")
            from_side = _side_for_nation(war_instance, frm) if frm else None
            to_side = _side_for_nation(war_instance, to) if to else None
            if from_side is None or to_side is None or from_side == to_side:
                return {
                    "valid": False,
                    "error": "clause_side_mismatch",
                    "error_index": idx,
                    "disabled_reason_display": _error_display("clause_side_mismatch"),
                }

    # SC-33 / G2-Slice-9: per-clause amount + duration bounds for
    # `gold_per_turn` clauses (no silent clamping — submitted values are
    # rejected with humanized copy if out of range).
    for idx, clause in enumerate(terms):
        if clause.get("type") != "gold_per_turn":
            continue
        amount = int(clause.get("amount", 0) or 0)
        turns = int(clause.get("turns", 0) or 0)
        if amount < GOLD_PER_TURN_MIN_AMOUNT:
            return {
                "valid": False,
                "error": "gold_per_turn_amount_too_small",
                "error_index": idx,
                "disabled_reason_display": _error_display(
                    "gold_per_turn_amount_too_small"
                ),
            }
        if turns < GOLD_PER_TURN_MIN_TURNS or turns > GOLD_PER_TURN_MAX_TURNS:
            return {
                "valid": False,
                "error": "gold_per_turn_duration_out_of_range",
                "error_index": idx,
                "disabled_reason_display": _error_display(
                    "gold_per_turn_duration_out_of_range"
                ),
            }

    # SC-33 / G2-Slice-9: projected-solvency budget conflict. Combines all
    # lump-sum + recurring gold obligations the same payer is committing
    # to in this draft, plus their existing recurring settlement
    # obligations, against `current_gold + max(0, expected_net_income) *
    # max_turns_in_submitted_terms`. Rejects when the combined obligation
    # exceeds capacity. Skipped when `world` is unavailable (legacy
    # schema-only callers).
    if world is not None and enforce_solvency:
        conflict = _check_gold_payment_budget_conflict(world, terms)
        if conflict is not None:
            return conflict

    # SC-31 / G2-Slice-8: dependency-clause eligibility uses world state.
    # When called without a `world`+`war_instance` context (legacy callers
    # / pure schema validation), the dependency-state checks are skipped.
    if world is not None and isinstance(war_instance, Mapping):
        for idx, clause in enumerate(terms):
            ctype = clause.get("type")
            if ctype in ("vassalage", "subjugation"):
                # Canonical direction: from = vassal/subjugated, to = lord.
                vassal_nation = str(clause.get("from") or "")
                lord_nation = str(clause.get("to") or "")
                if not vassal_nation or not lord_nation or vassal_nation == lord_nation:
                    return {
                        "valid": False,
                        "error": "dependency_direction_invalid",
                        "error_index": idx,
                        "disabled_reason_display": _error_display(
                            "dependency_direction_invalid"
                        ),
                    }
                eligibility = (
                    evaluate_subjugation_eligibility
                    if ctype == "subjugation"
                    else evaluate_vassalage_eligibility
                )(
                    world,
                    war_instance=war_instance,
                    lord_nation=lord_nation,
                    target_nation=vassal_nation,
                )
                if not eligibility.get("eligible"):
                    return {
                        "valid": False,
                        "error": str(eligibility.get("refusal_code") or "dependency_invalid"),
                        "error_index": idx,
                        "disabled_reason_display": eligibility.get("disabled_reason_display")
                        or _error_display(
                            str(eligibility.get("refusal_code") or "dependency_invalid")
                        ),
                    }
            elif ctype == "liberation":
                vassal_nation = str(clause.get("vassal_nation") or "")
                lord_nation = str(clause.get("lord_nation") or "")
                liberator = str(clause.get("liberator") or "")
                eligibility = evaluate_liberation_eligibility(
                    world,
                    war_instance=war_instance,
                    vassal_nation=vassal_nation,
                    lord_nation=lord_nation,
                    liberator=liberator,
                )
                if not eligibility.get("eligible"):
                    return {
                        "valid": False,
                        "error": str(eligibility.get("refusal_code") or "liberation_invalid"),
                        "error_index": idx,
                        "disabled_reason_display": eligibility.get("disabled_reason_display")
                        or _error_display(
                            str(eligibility.get("refusal_code") or "liberation_invalid")
                        ),
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
    baseline_payload = _compute_concession_baseline(
        world,
        war_id=war_id,
        war_instance=instance,
        proposer_side=side,
        accepting_side=accepting_side,
        accepting_leader=str(accepting_leader or ""),
        proposer_side_leader=str(proposer_leader or ""),
        covered_enemy_participants=covered,
        side_pressure_score=acceptance.get("side_pressure_score"),
        accept_threshold=int(
            acceptance.get("accept_threshold")
            or review_acceptance.get("threshold")
            or 50
        ),
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
SETTLEMENT_EDITOR_SOURCES = frozenset({"rejected_review", "stale_recovery", "explicit_revise"})

# SC-5R-1 pre-ratification clause-type guard allowlist for legacy aliases
# the apply path still tolerates (`gold_lump` is a pre-cleanup alias for
# `gold_indemnity` recognized by `_apply_settlement_terms` at line ~3877).
# Cut clause types (e.g. clause types removed by a SC-32 / D-series
# product decision) do not appear here and are rejected by the guard.
RATIFY_LEGACY_APPLY_CLAUSE_TYPES = frozenset({"gold_lump"})


def _scoped_settlement_drafts(world: Any) -> Dict[str, List[Dict[str, Any]]]:
    """Return the SC-5R scoped settlement draft store, creating it lazily.

    Storage is keyed by ``compute_settlement_draft_key(...)`` so same-war
    drafts with different ``selected_target_nation`` / covered scope do not
    collide. The legacy ``pending_settlement_drafts`` (war_id keyed) store
    remains for backward compatibility within SC-5R-1; SC-5R-2 routes the
    editor through the scoped store.
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
    """Return the scoped draft for the given war/scope, or ``None``."""
    draft_key = compute_settlement_draft_key(
        war_id, selected_target_nation, covered_enemy_participants,
    )
    drafts = getattr(world, "pending_settlement_drafts_by_key", None)
    if not isinstance(drafts, dict):
        return None
    entry = drafts.get(draft_key)
    if not isinstance(entry, list):
        return None
    return [dict(t) for t in entry if isinstance(t, Mapping)]


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


def _field_schema(
    *,
    control: str,
    label: str,
    options: Optional[List[Dict[str, Any]]] = None,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    default: Any = None,
    direction_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "control": control,
        "label": label,
        "options": list(options or []),
        "min": min_value,
        "max": max_value,
        "default": default,
        "direction_metadata": dict(direction_metadata or {}),
    }


def _control_option(
    option_id: str,
    *,
    label: Optional[str] = None,
    disabled: bool = False,
    disabled_reason_display: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "id": str(option_id),
        "label": str(label if label is not None else option_id),
        "disabled": bool(disabled),
        "disabled_reason_display": disabled_reason_display,
    }


def _nation_control_options(
    world: Any,
    war_instance: Optional[Mapping[str, Any]],
    covered_enemy_participants: Optional[Iterable[str]],
    *,
    proposer_side: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Nation picker options for the Tier-3 editor.

    Re-front Slice 3 §13 P2/P3: when the proposer side is known, the picker
    offers every proposer-side participant plus ONLY the covered accepting-side
    courts. An uncovered enemy can never be picked (mirrors the V2 validator
    rule), and dropping a court from ``covered_enemy_participants`` removes it
    from every picker on the next rebuild (P3 — the conversational coverage edit
    rebuilds the dialogue and so the schema). Without a known proposer side it
    falls back to listing every participant (legacy schema-only callers).
    """
    covered = {
        str(n or "").strip()
        for n in (covered_enemy_participants or [])
        if str(n or "").strip()
    }
    nations: List[str] = []

    def _add(name: Any) -> None:
        ns = str(name or "").strip()
        if ns and ns not in nations:
            nations.append(ns)

    ps = str(proposer_side or "")
    if isinstance(war_instance, Mapping) and ps in VALID_SIDES:
        accepting = _other_side(ps)
        for nation in war_instance.get(ps) or []:
            _add(nation)
        for nation in war_instance.get(accepting) or []:
            if str(nation or "").strip() in covered:
                _add(nation)
    elif isinstance(war_instance, Mapping):
        for side in ("attackers", "defenders"):
            for nation in war_instance.get(side) or []:
                _add(nation)
    # Covered courts stay selectable even if the side lookup missed them
    # (defensive); the player nation is always present.
    for nation in covered:
        _add(nation)
    _add(getattr(world, "player_nation", ""))
    return [_control_option(nation) for nation in nations]


def _region_control_options(
    world: Any,
    nation_options: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    allowed_controllers = {str(option.get("id") or "") for option in nation_options}
    regions = getattr(world, "regions", None) or {}
    options: List[Dict[str, Any]] = []
    for region_name in sorted(regions):
        region = regions.get(region_name)
        controller = str(getattr(region, "controller", "") or "")
        if allowed_controllers and controller not in allowed_controllers:
            continue
        options.append(_control_option(str(region_name)))
    return options


def _vassal_control_options(world: Any) -> List[Dict[str, Any]]:
    vassals = getattr(world, "vassals", None) or {}
    if isinstance(vassals, Mapping):
        return [_control_option(str(nation)) for nation in sorted(vassals)]
    return []


def _side_partitioned_options(
    war_instance: Optional[Mapping[str, Any]],
    covered_enemy_participants: Optional[Iterable[str]],
    proposer_side: Optional[str],
    nation_options: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Split the proposer+covered nation options into (proposer_side, covered)
    lists for the role-specific Tier-3 pickers (§13 P2).

    Used only for roles whose side is FIXED regardless of demand/concession
    direction — ``forced_alliance`` (subject = covered enemy, imposer =
    proposer-side; demand-only per the cleanup matrix) and ``liberation``
    (lord = covered enemy losing the vassal, liberator = proposer-side). The
    direction-CHOSEN roles (territory/gold payer↔payee, vassalage/subjugation)
    keep the full filtered list because either side can legally be ``from`` /
    ``to``; their opposite-side rule is the validator's V3/V4 authority (the
    cleanup spec line-609 "validator is authority, pickers are a filtered view"
    contract — a picker cannot statically know the player's chosen direction).

    When the war-side context is unknown (legacy schema-only callers) both lists
    fall back to the full ``nation_options`` so no picker is emptied by missing
    context; the validator stays the authority.
    """
    ps = str(proposer_side or "")
    if not (isinstance(war_instance, Mapping) and ps in VALID_SIDES):
        return list(nation_options), list(nation_options)
    proposer_members = {
        str(n).strip() for n in (war_instance.get(ps) or []) if str(n or "").strip()
    }
    covered = {
        str(n).strip()
        for n in (covered_enemy_participants or [])
        if str(n or "").strip()
    }
    proposer_opts = [
        opt for opt in nation_options if str(opt.get("id") or "") in proposer_members
    ]
    covered_opts = [
        opt for opt in nation_options if str(opt.get("id") or "") in covered
    ]
    return proposer_opts, covered_opts


def _clause_fields_for_review(
    clause_type: str,
    *,
    nation_options: Optional[List[Dict[str, Any]]] = None,
    region_options: Optional[List[Dict[str, Any]]] = None,
    vassal_options: Optional[List[Dict[str, Any]]] = None,
    proposer_options: Optional[List[Dict[str, Any]]] = None,
    covered_options: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Dict[str, Any]]:
    nation_picker = {
        "control": "picker",
        "options": list(nation_options or []),
        "min_value": None,
        "max_value": None,
        "default": None,
    }

    def _picker_for(options: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        # Role-specific option list; falls back to the shared nation list when a
        # side partition was not supplied (legacy callers).
        chosen = options if options is not None else nation_options
        return {
            "control": "picker",
            "options": list(chosen or []),
            "min_value": None,
            "max_value": None,
            "default": None,
        }
    if clause_type == "peace":
        return {}
    if clause_type == "territory_cede":
        return {
            "from": _field_schema(
                **nation_picker,
                label="Ceding court",
                direction_metadata={"role": "payer", "direction": "conceded"},
            ),
            "to": _field_schema(
                **nation_picker,
                label="Receiving court",
                direction_metadata={"role": "recipient", "direction": "demanded"},
            ),
            "region": _field_schema(
                control="picker",
                label="Region",
                options=list(region_options or []),
                direction_metadata={"role": "asset", "direction": "demanded"},
            ),
        }
    if clause_type == "gold_indemnity":
        return {
            "from": _field_schema(
                **nation_picker,
                label="Paying court",
                direction_metadata={"role": "payer", "direction": "demanded"},
            ),
            "to": _field_schema(
                **nation_picker,
                label="Receiving court",
                direction_metadata={"role": "recipient", "direction": "demanded"},
            ),
            "amount": _field_schema(
                control="number",
                label="Gold",
                min_value=1,
                default=200,
                direction_metadata={"role": "amount", "direction": "demanded"},
            ),
        }
    if clause_type == "gold_per_turn":
        return {
            "from": _field_schema(
                **nation_picker,
                label="Paying court",
                direction_metadata={"role": "payer", "direction": "demanded"},
            ),
            "to": _field_schema(
                **nation_picker,
                label="Receiving court",
                direction_metadata={"role": "recipient", "direction": "demanded"},
            ),
            "amount": _field_schema(
                control="number",
                label="Gold per turn",
                min_value=GOLD_PER_TURN_MIN_AMOUNT,
                default=max(GOLD_PER_TURN_MIN_AMOUNT, 50),
                direction_metadata={"role": "amount", "direction": "demanded"},
            ),
            "turns": _field_schema(
                control="number",
                label="Turns",
                min_value=GOLD_PER_TURN_MIN_TURNS,
                max_value=GOLD_PER_TURN_MAX_TURNS,
                default=3,
                direction_metadata={"role": "duration", "direction": "demanded"},
            ),
        }
    if clause_type == "forced_alliance":
        # §13 P2: forced alliance is demand-only — the subject is a covered
        # enemy, the imposer is a proposer-side court. Same-side imposition is
        # unauthorable because the two pickers draw from disjoint side lists.
        return {
            "from": _field_schema(
                **_picker_for(covered_options),
                label="Court forced into alliance",
                direction_metadata={"role": "subject", "direction": "demanded"},
            ),
            "to": _field_schema(
                **_picker_for(proposer_options),
                label="Alliance imposed by",
                direction_metadata={"role": "imposer", "direction": "demanded"},
            ),
            "includes_continental_system": _field_schema(
                control="toggle",
                label="Continental System inclusion",
                default=False,
                direction_metadata={"role": "modifier", "direction": "demanded"},
            ),
        }
    if clause_type in {"vassalage", "subjugation"}:
        return {
            "from": _field_schema(
                **nation_picker,
                label="Subject court",
                direction_metadata={"role": "subject", "direction": "demanded"},
            ),
            "to": _field_schema(
                **nation_picker,
                label="Overlord court",
                direction_metadata={"role": "overlord", "direction": "demanded"},
            ),
        }
    if clause_type == "liberation":
        return {
            "vassal_nation": _field_schema(
                control="picker",
                label="Vassal to liberate",
                # Slice 0 / cleanup spec line 601: the picker offers only real
                # vassals. The old `or nation_options` fallback let non-vassals
                # (including France) appear, which is what produced the
                # France-liberates-France nonsense the validator only caught at
                # Submit. With no vassals the picker is empty and the clause is
                # disabled (see _build_clause_control_schema_for_review).
                options=list(vassal_options or []),
                direction_metadata={"role": "subject", "direction": "demanded"},
            ),
            # §13 P2: the lord losing the vassal is a covered enemy; the
            # liberator is a proposer-side court (opposite the lord, mirroring
            # `evaluate_liberation_eligibility`). Disjoint side lists make a
            # same-side liberation unauthorable, not merely Submit-rejected.
            "lord_nation": _field_schema(
                **_picker_for(covered_options),
                label="Current overlord",
                direction_metadata={"role": "overlord", "direction": "demanded"},
            ),
            "liberator": _field_schema(
                **_picker_for(proposer_options),
                label="Liberating court",
                direction_metadata={"role": "liberator", "direction": "demanded"},
            ),
        }
    return {}


def _clause_enabled_from_pickers(
    fields: Mapping[str, Mapping[str, Any]],
) -> Tuple[bool, Optional[str]]:
    """Compute per-clause-type ``enabled`` from picker emptiness.

    Slice 0 / cleanup spec line 601 contract: a live clause type whose
    required picker fields have zero options after filtering cannot author
    a valid clause, so its Add Clause control is disabled with a humanized
    reason naming the empty picker(s). Number / toggle fields never gate
    ``enabled`` (only ``picker`` controls carry a target list), and a
    clause type with no fields at all (``peace``) is always enabled.
    """
    empty_picker_labels = [
        str(field.get("label") or name)
        for name, field in fields.items()
        if field.get("control") == "picker" and not field.get("options")
    ]
    if empty_picker_labels:
        return False, "No eligible options available for: " + ", ".join(
            empty_picker_labels
        )
    return True, None


def _build_clause_control_schema_for_review(
    world: Any = None,
    *,
    war_instance: Optional[Mapping[str, Any]] = None,
    covered_enemy_participants: Optional[Iterable[str]] = None,
    proposer_side: Optional[str] = None,
) -> Dict[str, Dict[str, Any]]:
    """Return the SC-5R clause control schema for live clause types.

    The schema is the backend source of truth for Godot picker contents
    (spec §Editor Layout Contract). Hidden clause types are absent from
    both the schema and ``available_clause_types[]`` so clients cannot
    synthesize disabled rows for absent types.

    Re-front Slice 3 §13: ``proposer_side`` lets the nation/region pickers
    filter to proposer-side + covered courts (P2/P3); a coverage edit rebuilds
    the dialogue and so re-filters every picker. The fixed-direction roles
    (``forced_alliance`` subject/imposer, ``liberation`` lord/liberator) are
    additionally split onto disjoint side lists via ``_side_partitioned_options``
    so a same-side imposition/liberation cannot be authored; the
    direction-chosen roles (territory/gold payer↔payee) keep the full filtered
    list and rely on the validator's V3/V4 authority (cleanup spec line 609).
    """
    schema: Dict[str, Dict[str, Any]] = {}
    nation_options = _nation_control_options(
        world, war_instance, covered_enemy_participants, proposer_side=proposer_side,
    )
    proposer_options, covered_options = _side_partitioned_options(
        war_instance, covered_enemy_participants, proposer_side, nation_options,
    )
    region_options = _region_control_options(world, nation_options)
    vassal_options = _vassal_control_options(world)
    for clause_type, base in CLAUSE_CONTROL_SCHEMA.items():
        if not base.get("enabled"):
            continue
        if clause_type not in SETTLEMENT_LIVE_CLAUSE_TYPES:
            continue
        fields = _clause_fields_for_review(
            clause_type,
            nation_options=nation_options,
            region_options=region_options,
            vassal_options=vassal_options,
            proposer_options=proposer_options,
            covered_options=covered_options,
        )
        enabled, disabled_reason_display = _clause_enabled_from_pickers(fields)
        schema[clause_type] = {
            "enabled": enabled,
            "disabled_reason_display": disabled_reason_display,
            "fields": fields,
        }
    return schema


def _available_clause_types_for_review() -> List[str]:
    """Return the ordered list of live clause types for ``available_clause_types[]``."""
    schema = _build_clause_control_schema_for_review()
    return sorted(schema.keys())


def _build_settlement_editor_route(
    *,
    war_id: str,
    selected_target_nation: str,
    covered_enemy_participants: Iterable[str],
    draft_key: str,
    available_clause_types: Iterable[str],
    staged_settlement_terms: Iterable[Mapping[str, Any]],
    source_route_id: Optional[str] = None,
    source: str = "explicit_revise",
) -> Dict[str, Any]:
    """Build the SC-5R ``editor_route`` payload for an EDIT-capable review.

    The shape is exact per spec line 548; SC-5R-2 will consume this on
    the Godot side to mount the editor surface.
    """
    if source not in SETTLEMENT_EDITOR_SOURCES:
        source = "explicit_revise"
    return {
        "surface": "settlement_editor",
        "war_id": str(war_id or ""),
        "selected_target_nation": str(selected_target_nation or ""),
        "covered_enemy_participants": [
            str(n) for n in (covered_enemy_participants or []) if str(n)
        ],
        "draft_key": str(draft_key or ""),
        "available_clause_types": list(available_clause_types or []),
        "staged_settlement_terms": [
            dict(t) for t in (staged_settlement_terms or []) if isinstance(t, Mapping)
        ],
        "source_route_id": str(source_route_id) if source_route_id else None,
        "source": source,
    }


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
    # REFRONT-V: each per-court row speaks through its NAMED diplomat (chancery
    # fallback — never an anonymous beat), and Talleyrand narrates the table.
    multi_court_voice = resolve_multi_court_settlement_voice(
        world,
        per_court_acceptance=per_court_acceptance,
        overall_acceptance=overall_acceptance,
        war_label=str(preview.get("war_label") or _war_label(war_id, war_instance)),
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
    leaders = {
        "attackers": war_instance.get("attacker_leader"),
        "defenders": war_instance.get("defender_leader"),
    }
    score = preview["acceptance"].get("score")
    verdict = preview["acceptance"].get("verdict")
    war_label = str(preview.get("war_label") or _war_label(war_id, war_instance))
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
        options.append({"label": "Ratify Settlement", "action": "confirm_settlement"})
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
    # SC-29 / G2-Slice-7: pair-scoped peace substitute CTAs. Only emitted
    # on blocked ratification, with a non-empty selected target, and only
    # when `evaluate_pair_peace_substitute_eligibility(...)` returns
    # eligible=True for each action. Order per failure-state table:
    # Re-author -> Revise Terms -> Seek Bilateral Peace -> Seek Armistice
    # Instead -> Open War Detail -> Back Out.
    if not can_ratify and resolved_target:
        actor_for_substitute = str(
            getattr(world, "player_nation", "France") or "France"
        )
        for action_id, label, voice_key, description in (
            (
                "seek_bilateral_peace",
                "Seek Bilateral Peace",
                "settlement_seek_bilateral_peace_instead_talleyrand",
                "Open a bilateral peace with the selected court only; "
                "the other hostile pairs remain at war.",
            ),
            (
                "seek_armistice_instead",
                "Seek Armistice Instead",
                "settlement_seek_armistice_instead_talleyrand",
                "Open an armistice with the selected court only; "
                "the war continues elsewhere.",
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
                # SC-29 + Disabled vs Hidden Affordance Policy: only
                # `cooldown_active` may render as a pre-click disabled
                # button after SC-29 lands. Every other refusal hides
                # the substitute action entirely.
                if eligibility.get("refusal_code") in PAIR_SUBSTITUTE_TEMPORAL_REFUSAL_CODES:
                    options.append({
                        "label": label,
                        "action": action_id,
                        "available": False,
                        "disabled_reason_display": eligibility.get(
                            "disabled_reason_display"
                        ),
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
    holdout_set = {str(n) for n in holdout_courts}
    for row in per_court_acceptance:
        court = str(row.get("nation") or "")
        is_holdout = court in holdout_set
        row["is_holdout"] = is_holdout
        # Re-front Slice-G boundary: the dial/coverage affordances are
        # player-only. A non-player (AI/system) caller never gets the
        # one-click Ease/Drop routes, mirroring the `can_edit_terms` gate.
        court_holdout_actions: List[Dict[str, Any]] = []
        if is_holdout and str(caller_kind or "") == SETTLEMENT_EDITOR_CALLER_KIND:
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
        if is_dialable and str(caller_kind or "") == SETTLEMENT_EDITOR_CALLER_KIND:
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
    if dialogue_mode == "PROPOSE" and str(caller_kind or "") == SETTLEMENT_EDITOR_CALLER_KIND:
        # PROPOSE is the conversational front (Tiers 1-2): an authoring rail,
        # not a staged-decision rail. Adjust terms (-> EDIT/Tier 3), Submit for
        # Review (-> REVIEW), Back Out. No `confirm_settlement` — ratification
        # only ever fires from REVIEW. Holdout Ease/Drop ride on the rows above.
        # The authoring rail is PLAYER-ONLY (Slice-G boundary): a non-player
        # PROPOSE staging keeps the default non-authoring rail (no `adjust_terms`
        # / `submit_settlement_for_review` / `suspend_settlement_editor`), in
        # lockstep with `can_edit_terms=False` / `editor_route=None` below.
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
            "label": "Adjust terms",
            "action": "adjust_terms",
            "description": "Open the structured editor to shape specific clauses.",
        }, {
            "label": "Submit for Review",
            "action": "submit_settlement_for_review",
            "description": "Lock in this package and review it for ratification.",
        }]
        available_action_ids = [
            "settlement_dial_harsher",
            "settlement_dial_generous",
            "adjust_terms",
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
    # SC-5R-1/2: publish the EDIT payload contract per spec line 543-556
    # plus the editor-layout empty-draft rule at line 595.
    # `can_edit_terms` is the gate for showing `Revise Terms` on REVIEW;
    # SC-5R-2 will consume `available_clause_types[]` + `clause_control_schema`
    # + `editor_route` to mount the Godot editor surface. Hidden clause
    # types are absent from both fields so clients cannot synthesize
    # disabled rows for absent types.
    war_active = bool(
        war_instance
        and isinstance(war_instance, Mapping)
        and war_instance.get("ended_turn") is None
    )
    sc5r_clause_control_schema = _build_clause_control_schema_for_review(
        world,
        war_instance=war_instance,
        covered_enemy_participants=covered,
        proposer_side=proposer_side,
    )
    sc5r_available_clause_types = sorted(sc5r_clause_control_schema.keys())
    staged_terms_for_edit = copy.deepcopy(preview.get("settlement_terms") or [])
    can_edit_terms = bool(
        str(caller_kind or "") == SETTLEMENT_EDITOR_CALLER_KIND
        and war_active
        and not white_peace
        and sc5r_available_clause_types
    )
    sc5r_draft_key = compute_settlement_draft_key(war_id, resolved_target, covered)
    sc5r_editor_route = (
        _build_settlement_editor_route(
            war_id=war_id,
            selected_target_nation=resolved_target,
            covered_enemy_participants=covered,
            draft_key=sc5r_draft_key,
            available_clause_types=sc5r_available_clause_types,
            staged_settlement_terms=staged_terms_for_edit,
            source_route_id=route_id,
            source="explicit_revise",
        )
        if can_edit_terms
        else None
    )
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
        "targeted_posture_advisory": (
            _settlement_targeted_posture_advisory(per_court_acceptance, holdout_courts)
            if dialogue_mode == "PROPOSE"
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
        # SC-5R-1 EDIT payload contract per spec §Full Treaty Settlement
        # Flow line 546-556 plus the editor-layout empty-draft rule.
        # `can_edit_terms` is true when the staged dialogue is a
        # player-editor draft on an active war with at least one live
        # clause type authorable; empty packages open EDIT with Submit
        # disabled instead of blocking editor mount. White peace remains
        # a REVIEW-only empty-package ratification path.
        # `available_clause_types[]` and
        # `clause_control_schema` are absent (empty) when not editable
        # so hidden clause types cannot leak as disabled labels;
        # `editor_route` is None when not editable so SC-5R-2 cannot
        # advertise an editor handoff for non-editor staging.
        "can_edit_terms": can_edit_terms,
        "available_clause_types": (
            list(sc5r_available_clause_types) if can_edit_terms else []
        ),
        "clause_control_schema": (
            copy.deepcopy(sc5r_clause_control_schema) if can_edit_terms else {}
        ),
        "editor_route": sc5r_editor_route,
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
            # Same-war restage: refresh the mounted dialogue and merge
            # non-conflicting authored draft terms through the
            # `pending_settlement_drafts` store. Conflicting clauses keep
            # the active draft unchanged and surface a humanized merge
            # conflict beat.
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
            existing_terms = list(mounted.get("settlement_terms") or [])
            incoming_terms = list(settlement_terms or [])
            ok, merged_terms, conflicts = merge_same_war_settlement_drafts(
                existing_terms, incoming_terms,
            )
            drafts = getattr(world, "pending_settlement_drafts", None)
            if drafts is None:
                world.pending_settlement_drafts = {}
                drafts = world.pending_settlement_drafts
            if not ok:
                # Preserve the active draft per SC-26 — return without
                # restaging. Drafts store holds the existing draft.
                drafts[war_id_str] = [dict(t) for t in existing_terms]
                # SC-5R-1 scoped draft persistence: dual-write the
                # preserved draft to the scoped store under the active
                # dialogue's scope so reopen / War Detail recovery
                # finds it under `draft_key`, not just `war_id`.
                save_scoped_settlement_draft(
                    world,
                    war_id=war_id_str,
                    selected_target_nation=str(
                        mounted.get("selected_target_nation") or ""
                    ),
                    covered_enemy_participants=mounted_covered,
                    settlement_terms=existing_terms,
                )
                return _settlement_collision_payload(
                    error="same_war_merge_conflict",
                    active_war_id=war_id_str,
                    incoming_war_id=war_id_str,
                    extra={
                        "dialogue_type": "settlement_confirm",
                        "war_id": war_id_str,
                        "merge_conflict": True,
                        "conflicts": conflicts,
                        "preserved_terms": [dict(t) for t in existing_terms],
                    },
                )
            # Compatible merge: persist merged draft + restage with merged
            # terms so preview/acceptance reflect the new authored set.
            drafts[war_id_str] = [dict(t) for t in merged_terms]
            # SC-5R-1: dual-write the merged draft to the scoped store
            # under the incoming scope (same-war refresh adopts the
            # caller's scope when present).
            save_scoped_settlement_draft(
                world,
                war_id=war_id_str,
                selected_target_nation=incoming_target_for_scope,
                covered_enemy_participants=incoming_covered_for_scope,
                settlement_terms=merged_terms,
            )
            settlement_terms = merged_terms
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
    if getattr(world.dialogue_manager, "peek", lambda: None)() is None:
        world.dialogue_manager.replace(dialogue)
    elif hasattr(world.dialogue_manager, "preempt"):
        world.dialogue_manager.preempt(dialogue)
    else:
        world.dialogue_manager.replace(dialogue)
    ally_petitions: List[Dict[str, Any]] = []
    if caller_kind == "player_editor":
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
    vassalage_terms_by_pair: Dict[frozenset[str], Mapping[str, Any]] = {}
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
                vassalage_terms_by_pair[frozenset((vassal_lord, vassal_target))] = term

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
        vassalage_term = vassalage_terms_by_pair.get(
            frozenset((proposer_member, covered_enemy))
        )
        if vassalage_term is not None:
            target_state = "VASSAL"
            vassal_lord = str(
                vassalage_term.get("to") or vassalage_term.get("lord_nation") or ""
            )
            vassal_target = str(
                vassalage_term.get("from") or vassalage_term.get("vassal_nation") or ""
            )
        else:
            vassal_lord = ""
            vassal_target = ""
        current_state = world.diplomatic_states.get(pair, "PEACE")
        plan.append({
            "pair": pair,
            "proposer_member": proposer_member,
            "covered_enemy": covered_enemy,
            "current_state": current_state,
            "pair_status_before": pair_meta.get("pair_status"),
            "target_state": target_state,
            "vassal_lord": vassal_lord,
            "vassal_target": vassal_target,
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
    war_id: str = "",
    settlement_route_id: str = "",
) -> List[Dict[str, Any]]:
    """Apply package-level territory, gold, and liberation outcomes.

    Forced-alliance state transitions are handled per pair after pair
    cleanup (see ``_resolve_pair_state_transitions``) because the alliance
    state must replace the intermediate ``PEACE`` state established by
    cleanup.

    `war_id` / `settlement_route_id` are forwarded as identity columns on
    ratified recurring-gold obligations so the per-turn processor and the
    diplomatic ledger can attribute each tick to the originating war.
    """
    applied: List[Dict[str, Any]] = []
    for idx, term in enumerate(settlement_terms or []):
        if not isinstance(term, Mapping):
            continue
        ttype = term.get("type")
        from_nation = str(term.get("from") or "")
        to_nation = str(term.get("to") or "")
        if ttype == "territory_cede":
            regions = _territory_term_regions(term)
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
                if "regions" in clause:
                    clause["regions"] = transferred
                elif transferred:
                    clause["region"] = transferred[0]
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
        elif ttype in ("gold_lump", "gold_indemnity"):
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
                    clause["type"] = ttype
                    clause["amount"] = int(transfer)
                    applied.append(clause)
        elif ttype == "gold_per_turn":
            amount = abs(int(term.get("amount", 0) or 0))
            turns = abs(int(term.get("turns", 0) or 0))
            if from_nation and to_nation and amount > 0 and turns > 0:
                # SC-33 / G2-Slice-9: register a recurring obligation on
                # `world.recurring_settlement_payments`. The income-phase
                # processor in `world_state.advance_turn` debits the
                # payer once per turn until `turns_remaining` hits zero
                # or a cancellation condition fires (payer/recipient
                # eliminated, payer vassalized, renewed war between the
                # pair). Ratification itself does not move gold — the
                # first transfer happens on the next turn's income
                # phase, mirroring bilateral treaty per-turn clauses.
                payments = getattr(world, "recurring_settlement_payments", None)
                if payments is None:
                    payments = []
                    setattr(world, "recurring_settlement_payments", payments)
                ratified_turn = int(getattr(world, "current_turn", 0) or 0)
                seq = sum(
                    1
                    for entry in payments
                    if isinstance(entry, Mapping)
                    and int(entry.get("ratified_turn", -1) or -1) == ratified_turn
                )
                payment_id = (
                    f"recurring_gold:{from_nation}:{to_nation}:"
                    f"{ratified_turn}:{seq}"
                )
                payments.append({
                    "payment_id": payment_id,
                    "from": from_nation,
                    "to": to_nation,
                    "amount_per_turn": int(amount),
                    "turns_remaining": int(turns),
                    "total_turns": int(turns),
                    "war_id": str(war_id or ""),
                    "ratified_turn": int(ratified_turn),
                    "settlement_route_id": str(settlement_route_id or ""),
                    "source_clause_index": int(idx),
                })
                clause = dict(term)
                clause["amount"] = amount
                clause["turns"] = turns
                clause["payment_id"] = payment_id
                clause["ratified_turn"] = int(ratified_turn)
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
                    clause["pair_state_transition"] = "VASSALAGE -> SOVEREIGN"
                    # SC-31 / G2-Slice-8 applied_clauses_preview fields
                    # for liberation: defensive_alliance_with_liberator,
                    # relation_deltas (lib_vassal vs former lord -20 /
                    # vs liberator +30), threat_reduction (lord-on-player
                    # side delta).
                    clause["defensive_alliance_with_liberator"] = bool(lib_liberator)
                    clause["relation_deltas"] = {
                        f"{lib_vassal}|{lib_from}": -20,
                        f"{lib_vassal}|{lib_liberator}": 30,
                    }
                    clause["threat_reduction"] = (
                        8 if lib_from == getattr(world, "player_nation", None) else 0
                    )
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
            vassal_lord = str(entry.get("vassal_lord") or "")
            vassal_target = str(entry.get("vassal_target") or "")
            term = vassalage_terms_by_pair.get((vassal_lord, vassal_target))
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
                        world, vassal_lord, vassal_target,
                        garrison_size=int(term.get("garrison_size", 0) or 0),
                    )
                else:
                    vassal_result = create_vassal_treaty(
                        world, vassal_lord, vassal_target,
                        generosity_bonus=int(term.get("generosity_bonus", 0) or 0),
                        terms=list(settlement_terms or []),
                    )
                if vassal_result.get("success"):
                    assimilated_marshals = assimilate_vassal_marshals(
                        world, vassal_target
                    )
                    clause = dict(term)
                    clause.setdefault("from", vassal_target)
                    clause.setdefault("to", vassal_lord)
                    clause["pair_state_transition"] = "WAR -> VASSALAGE"
                    # SC-31 / G2-Slice-8 applied_clauses_preview fields
                    # for vassalage / subjugation. Values read from the
                    # live vassal record so the preview matches the
                    # mutation that ran. autonomy_after / loyalty_after /
                    # tribute_rate_after / vassal_path use the values
                    # stamped by create_vassal_conquest /
                    # create_vassal_treaty; threat_delta_for_lord is the
                    # coalition-threat delta from the same helper (+25
                    # for conquest, +5 for treaty per WPS-B §2a);
                    # marshal_assimilation_count counts marshals moved
                    # to the lord pool.
                    vassal_record = (
                        (getattr(world, "vassals", {}) or {}).get(vassal_target)
                        or {}
                    )
                    autonomy_level = int(vassal_record.get("autonomy", 1))
                    autonomy_after_display = {
                        0: "Puppet",
                        1: "Satellite",
                        2: "Autonomous",
                    }.get(autonomy_level, "Satellite")
                    clause["autonomy_after"] = autonomy_after_display
                    clause["loyalty_after"] = int(vassal_record.get("loyalty") or 0)
                    clause["tribute_rate_after"] = float(
                        vassal_record.get("tribute_rate") or 0.0
                    )
                    clause["vassal_path"] = str(vassal_record.get("path") or "")
                    clause["marshal_assimilation_count"] = len(assimilated_marshals)
                    clause["threat_delta_for_lord"] = (
                        25 if term.get("type") == "subjugation" else 5
                    )
                    state_clauses_applied.append(clause)
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
            # G2-Slice-1b-Repair-1: Continental System surcharge.
            # Base +15 threat for the alliance imposition; +10 extra
            # when CS=True so the imperial cost of forcing inclusion is
            # charged at ratification, matching what the preview shows.
            from backend.game_logic.settlement_scoring import (
                FORCED_ALLIANCE_THREAT_PER_CLAUSE,
                FORCED_ALLIANCE_CONTINENTAL_SYSTEM_THREAT_SURCHARGE,
            )
            clause_threat_delta = int(FORCED_ALLIANCE_THREAT_PER_CLAUSE)
            if includes_cs:
                clause_threat_delta += int(
                    FORCED_ALLIANCE_CONTINENTAL_SYSTEM_THREAT_SURCHARGE
                )
            if proposer_member == getattr(world, "player_nation", None):
                from backend.game_logic.coalition import add_threat
                add_threat(world, clause_threat_delta, "forced_alliance")
            if hasattr(world, "log_event"):
                world.log_event({
                    "type": "forced_alliance_imposed",
                    "imposer": proposer_member,
                    "target": covered_enemy,
                    "imposing_nation": proposer_member,
                    "forced_nation": covered_enemy,
                    "includes_continental_system": includes_cs,
                    "projected_threat_delta": clause_threat_delta,
                    "turn": int(getattr(world, "current_turn", 0) or 0),
                })
            if term is not None:
                clause = dict(term)
                clause["includes_continental_system"] = includes_cs
                # Always overwrite so preview and applied row agree on
                # the CS-adjusted delta even when the editor pre-stamped
                # the legacy +15 baseline before authoring the toggle.
                clause["projected_threat_delta"] = clause_threat_delta
                clause["pair_state_transition"] = "WAR -> ALLIANCE"
                state_clauses_applied.append(clause)

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
        # SC-24: store BOTH raw common-peace harshness and the legacy
        # 1.0-clamped harshness under separate explicit fields. Named
        # consumers that interpret authored common-peace terms read
        # `raw_harshness` (no 1.0 ceiling); legacy bilateral consumers
        # may keep reading `harshness` for backward compatibility.
        clamped_harshness = calculate_treaty_harshness({"clauses": pair_terms})
        raw_harshness = calculate_raw_treaty_harshness({"clauses": pair_terms})
        treaty = {
            "nations": [proposer_member, covered_enemy],
            "type": treaty_type,
            "state_transition": f"{entry['current_state']}_TO_{final_state}",
            "clauses": [dict(t) for t in pair_terms],
            "turn_signed": int(getattr(world, "current_turn", 0) or 0),
            "harshness": clamped_harshness,
            # SC-24 raw common-peace harshness consumers: ledger / AI
            # proposal / coalition threat / dispatch / notifications.
            "raw_harshness": float(raw_harshness or 0.0),
            "clamped_harshness": float(clamped_harshness or 0.0),
            "source": "common_peace",
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
        proposer_side = str(dialogue.get("proposer_side") or "")
        accepting_side = str(dialogue.get("accepting_side") or "")
        result = {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": "confirm",
            "war_id": war_id,
            "error": error,
            "error_display": _error_display(error),
            "mutated": False,
            "settlement_reactions": _failed_ratification_reaction_summary(
                world,
                war_id=war_id,
                proposer_side=proposer_side,
                accepting_side=accepting_side,
                covered_enemy_participants=dialogue.get("covered_enemy_participants") or [],
                settlement_terms=dialogue.get("settlement_terms") or [],
            ),
        }
        if validation.get("must_reopen"):
            # SC-2/SC-3/SC-13/SC-14b: gate `must_reopen=True` on a non-empty
            # target and the SC-14b per-(war_id, turn) attempt cap.
            result.update(_safe_reopen_response(world, war_id=war_id, dialogue=dialogue))
        else:
            result["must_reopen"] = False
            result["reopen_target"] = _reopen_target(war_id, dialogue)
        return result

    war_instance = (getattr(world, "war_instances", {}) or {}).get(war_id)
    if not war_instance or war_instance.get("ended_turn") is not None:
        world.dialogue_manager.pop()
        error = "inactive_war_instance"
        result = {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": "confirm",
            "war_id": war_id,
            "error": error,
            "error_display": _error_display(error),
            "mutated": False,
            "settlement_reactions": _failed_ratification_reaction_summary(
                world,
                war_id=war_id,
                proposer_side=str(dialogue.get("proposer_side") or ""),
                accepting_side=str(dialogue.get("accepting_side") or ""),
                covered_enemy_participants=dialogue.get("covered_enemy_participants") or [],
                settlement_terms=dialogue.get("settlement_terms") or [],
            ),
        }
        result.update(_safe_reopen_response(world, war_id=war_id, dialogue=dialogue))
        # The original code path treated this as `must_reopen=True`; keep
        # that behavior unless SC-14b's per-(war_id, turn) cap intervenes.
        return result

    # SC-3/SC-4: fresh acceptance rescore from current world state before mutation.
    proposer_side = str(dialogue.get("proposer_side") or "")
    accepting_side = str(dialogue.get("accepting_side") or "")
    covered = list(dialogue.get("covered_enemy_participants") or [])
    settlement_terms = list(dialogue.get("settlement_terms") or [])
    # G2-Slice-W1: pass labeled white-peace + caller_kind through to the
    # ratification event + empty-Ratify gate. Player-editor-staged empty
    # drafts with white_peace=False fail the gate even if acceptance
    # passes (defense-in-depth on top of the dialogue's `options[]` /
    # `available_action_ids[]` omission).
    white_peace = bool(dialogue.get("white_peace", False))
    caller_kind = str(dialogue.get("caller_kind") or "player_editor")
    # SC-31 / G2-Slice-8 - surrender_preset propagates through the
    # ratification event so dispatch/ledger/campaign-log render the
    # outcome as a labeled surrender. The flag is set when the player
    # accepted Talleyrand's surrender preset (or any future authored
    # surrender package that opts into the label); generic dependency
    # clauses authored manually do not toggle the flag automatically.
    surrender_preset = bool(dialogue.get("surrender_preset", False))
    if (
        caller_kind == "player_editor"
        and not settlement_terms
        and not white_peace
    ):
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": "confirm",
            "war_id": war_id,
            "error": "empty_editor_draft_ratification",
            "error_display": _error_display("empty_authored_draft"),
            "mutated": False,
            "talleyrand_text": (
                "Sire, this settlement cannot be ratified without authored terms."
            ),
        }

    # SC-5R-1 pre-ratification clause-type revalidation: defense in
    # depth for dialogues that bypass the submit-time `validate_settlement_terms`
    # call (e.g. fixture-staged tests, save-loaded drafts that survived
    # a code change). The goal is narrow: the cut clause type guard
    # (an unrecognized `type` like the D3-CUT clause) must fail before
    # `_apply_settlement_terms` runs so treaty history cannot record an
    # unsupported clause. Strict per-key schema validation already runs
    # at submit time through `_execute_propose_common_peace` and
    # `_stage_replacement_settlement_terms`; the legacy apply path
    # tolerates a few key variants (e.g. `regions` vs `region`) for
    # backward compat with historical ratification fixtures, so the
    # pre-ratify guard checks only the clause `type` field. White peace
    # ratifies an empty package by design and skips the non-empty guard.
    if settlement_terms and not white_peace:
        for idx, clause in enumerate(settlement_terms):
            if not isinstance(clause, Mapping):
                world.dialogue_manager.pop()
                return {
                    "success": False,
                    "dialogue_type": "settlement_confirm",
                    "action": "confirm",
                    "war_id": war_id,
                    "error": "submitted_terms_failed_revalidation",
                    "error_display": _error_display(
                        "submitted_terms_failed_revalidation"
                    ),
                    "validation_error": "invalid_clause_schema",
                    "validation_detail": _error_display(
                        "invalid_clause_schema"
                    ),
                    "validation_error_index": idx,
                    "mutated": False,
                    "talleyrand_text": (
                        "Sire, the settlement draft is malformed and cannot "
                        "be ratified."
                    ),
                }
            clause_type = clause.get("type")
            if (
                clause_type not in CANONICAL_CLAUSE_TYPES
                and clause_type not in RATIFY_LEGACY_APPLY_CLAUSE_TYPES
            ):
                world.dialogue_manager.pop()
                return {
                    "success": False,
                    "dialogue_type": "settlement_confirm",
                    "action": "confirm",
                    "war_id": war_id,
                    "error": "submitted_terms_failed_revalidation",
                    "error_display": _error_display(
                        "submitted_terms_failed_revalidation"
                    ),
                    "validation_error": "invalid_clause_type",
                    "validation_detail": _error_display(
                        "invalid_clause_type"
                    ),
                    "validation_error_index": idx,
                    "mutated": False,
                    "talleyrand_text": (
                        "Sire, the settlement draft contains an unsupported "
                        "clause and cannot be ratified."
                    ),
                }

    # Re-front Slice 3 §12 defense-in-depth (CRITICAL audit fix): re-run the
    # multi-party cross-court validity rules — V1 region double-promise, V2
    # uncovered court, V3 war-side, V4 self-reference / dependency eligibility —
    # against the LIVE world before mutation. The authoring gates (POST-preview,
    # Submit, restage) already enforce these, but staged terms can outlive the
    # state they were validated against (save/load, a drifting world); without
    # this gate a stale package mutates state — e.g. a staged liberation whose
    # vassal's live lord has changed would otherwise release the wrong (and
    # uncovered) lord's vassal at `_apply_settlement_terms`. Staged terms are
    # normalized to the canonical shape first (apply-format `gold_lump` / plural
    # `regions` → canonical) so the strict schema validator accepts the legacy
    # apply-format the fixtures + historical drafts use, and the authoring-only
    # solvency gate is skipped (the apply path clamps gold to the payer balance
    # rather than blocking). White peace ratifies an empty package by design.
    if settlement_terms and not white_peace:
        staged_revalidation = validate_settlement_terms(
            _normalize_staged_terms_for_validation(settlement_terms),
            proposer_side=proposer_side,
            covered_enemy_participants=covered,
            world=world,
            war_instance=war_instance,
            enforce_solvency=False,
        )
        if not staged_revalidation.get("valid"):
            world.dialogue_manager.pop()
            revalidation_error = str(staged_revalidation.get("error") or "")
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": "confirm",
                "war_id": war_id,
                "error": "submitted_terms_failed_revalidation",
                "error_display": _error_display("submitted_terms_failed_revalidation"),
                "validation_error": revalidation_error,
                "validation_detail": staged_revalidation.get("disabled_reason_display")
                or _error_display(revalidation_error),
                "validation_error_index": staged_revalidation.get("error_index"),
                "mutated": False,
                "talleyrand_text": (
                    "Sire, the terms we staged no longer hold against the present "
                    "situation — this settlement cannot be ratified as written."
                ),
            }

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
        band_display = acceptance_band_display(str(fresh_verdict or ""))
        top_blocker = ""
        feedback = list(fresh_acceptance.get("feedback") or [])
        if feedback and isinstance(feedback[0], Mapping):
            top_blocker = str(
                feedback[0].get("component_display")
                or feedback[0].get("display")
                or feedback[0].get("component")
                or ""
            )
        if fresh_hard_stops:
            first_stop = fresh_hard_stops[0]
            if isinstance(first_stop, Mapping):
                top_blocker = str(
                    first_stop.get("display")
                    or first_stop.get("detail")
                    or first_stop.get("reason")
                    or top_blocker
                )
        top_blocker = top_blocker or "a hard condition"
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
            "talleyrand_text": resolve_settlement_voice_line(
                "settlement_rescored_after_staging_talleyrand",
                war_label=str(dialogue.get("war_label") or war_id),
                acceptance_band=band_display,
                top_blocker=top_blocker,
            ),
            "settlement_reactions": _failed_ratification_reaction_summary(
                world,
                war_id=war_id,
                proposer_side=proposer_side,
                accepting_side=accepting_side,
                covered_enemy_participants=covered,
                settlement_terms=settlement_terms,
            ),
        }

    # Re-front Slice 1 §11.4: the per-covered-court ratification gate (defense
    # in depth beyond the dialogue's `can_ratify`). The single-leader rescore
    # above is retained for the leader summary + the n=1 path; this
    # additionally requires EVERY covered court to carry, so a multi-court
    # settlement cannot ratify while a covered minor holds out. White peace
    # ratifies an empty package by design and is exempt.
    if not white_peace and settlement_terms:
        per_court_block = compute_per_court_acceptance(
            world,
            war_id=war_id,
            war_instance=war_instance,
            proposer_side=proposer_side,
            accepting_side=accepting_side,
            proposer_side_leader=_side_leader(war_instance, proposer_side),
            covered_enemy_participants=covered,
            settlement_terms=settlement_terms,
        )
        overall = per_court_block["overall_acceptance"]
        if not overall.get("carries"):
            holdouts = list(overall.get("holdout_courts") or [])
            holdout_label = holdouts[0] if holdouts else "a covered court"
            return {
                "success": False,
                "dialogue_type": "settlement_confirm",
                "action": "confirm",
                "war_id": war_id,
                "error": "acceptance_rejected",
                "error_display": _error_display("acceptance_rejected"),
                "per_court_acceptance": per_court_block["per_court_acceptance"],
                "overall_acceptance": overall,
                "holdout_courts": holdouts,
                "mutated": False,
                "talleyrand_text": (
                    resolve_settlement_voice_line(
                        "settlement_multi_court_holdout_blocks_talleyrand",
                        war_label=str(dialogue.get("war_label") or war_id),
                        holdout_court=holdout_label,
                    )
                    or (
                        f"Sire, {holdout_label} will not sign; the settlement "
                        "cannot be ratified until they are eased or dropped."
                    )
                ),
                "settlement_reactions": _failed_ratification_reaction_summary(
                    world,
                    war_id=war_id,
                    proposer_side=proposer_side,
                    accepting_side=accepting_side,
                    covered_enemy_participants=covered,
                    settlement_terms=settlement_terms,
                ),
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
        result = {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": "confirm",
            "war_id": war_id,
            "error": error,
            "error_display": _error_display(error),
            "mutated": False,
            "settlement_reactions": _failed_ratification_reaction_summary(
                world,
                war_id=war_id,
                proposer_side=proposer_side,
                accepting_side=accepting_side,
                covered_enemy_participants=covered,
                settlement_terms=settlement_terms,
            ),
        }
        result.update(_safe_reopen_response(world, war_id=war_id, dialogue=dialogue))
        return result

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
        world,
        settlement_terms=settlement_terms,
        war_id=war_id,
        settlement_route_id=str(dialogue.get("route_id") or ""),
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
    staged_route_id = str(dialogue.get("route_id") or "")
    # SC-15: build the fresh ratification-time acceptance_snapshot from
    # the rescore that authorized mutation. Archived settlement review
    # later renders this snapshot rather than the stale staging score.
    # `acceptance_at_staging` is preserved for audit context.
    acceptance_snapshot = {
        "score": fresh_acceptance.get("score"),
        "verdict": fresh_acceptance.get("verdict"),
        "threshold": fresh_acceptance.get("accept_threshold"),
        "band": str(fresh_acceptance.get("verdict") or "near_acceptable"),
        "band_display": acceptance_band_display(
            str(fresh_acceptance.get("verdict") or "")
        ),
        "top_components": list(fresh_acceptance.get("feedback") or [])[:3],
        "hard_stops": list(fresh_acceptance.get("hard_stops") or []),
    }
    staged_acceptance = (dialogue.get("settlement_preview") or {}).get("acceptance") or {}
    acceptance_at_staging = {
        "score": staged_acceptance.get("score") or staged_acceptance.get("total"),
        "verdict": staged_acceptance.get("verdict") or staged_acceptance.get("band"),
        "threshold": staged_acceptance.get("threshold") or staged_acceptance.get("accept_threshold"),
        "band": str(staged_acceptance.get("band") or staged_acceptance.get("verdict") or ""),
    }
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
        staged_route_id=staged_route_id,
        acceptance_snapshot=acceptance_snapshot,
        acceptance_at_staging=acceptance_at_staging,
        white_peace=white_peace,
        surrender_preset=surrender_preset,
    )

    world.dialogue_manager.pop()
    drafts = getattr(world, "pending_settlement_drafts", None)
    if isinstance(drafts, dict):
        drafts.pop(war_id, None)
    _discard_scoped_settlement_draft_for_dialogue(world, dialogue)

    result_message = (
        f"Settlement Ratified: {dialogue.get('war_label') or pre_cleanup_war_label or war_id} "
        f"({len(resolved_pairs)} pair(s) resolved)."
    )
    # SC-14c: result feedback consumes the staged route id verbatim. The
    # summary event already echoes the staged id, so prefer that path; fall
    # back to the staged dialogue's id (same value) before minting a fresh
    # one for legacy callers.
    review_route_id = str(
        (reaction_summary.get("summary_event") or {}).get("route", {}).get("route_id", "")
        or dialogue.get("route_id")
        or mint_settlement_route_id(world, war_id=war_id)
    )
    # SC-14/14d/14e: result feedback re-resolves active vs archived at the
    # moment ratification completes. Active partial settlements route to
    # the live war/settlement surface; archived (full-war end) settlements
    # route to the ledger row.
    live_review_target = derive_settlement_review_target(world, war_id=war_id)
    review_route = {
        "surface": live_review_target,
        "review_target": live_review_target,
        "route_id": review_route_id,
        "war_id": war_id,
        "war_ended": bool(war_ended),
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


def _stage_replacement_settlement_terms(
    world: Any,
    dialogue: Mapping[str, Any],
    *,
    action: str,
    terms: Iterable[Mapping[str, Any]],
    message: str,
    surrender_preset: bool = False,
) -> Dict[str, Any]:
    war_id = str(dialogue.get("war_id") or "")
    covered = list(dialogue.get("covered_enemy_participants") or [])
    selected_target = str(dialogue.get("selected_target_nation") or "")
    actor = getattr(world, "player_nation", "France")
    replacement_terms = [
        dict(t) for t in (terms or []) if isinstance(t, Mapping)
    ]
    # SC-5R-1 pre-staging revalidation: an author handler that
    # constructs tampered or cut clause types (e.g. a clause `type`
    # that is no longer in `CANONICAL_CLAUSE_TYPES`, or a
    # `gold_indemnity` carrying an unknown `turns` field) must fail
    # before `build_settlement_preview(...)` so the dialogue never
    # reaches the player. The validator is the single source of truth
    # for clause schema; the matching pre-ratification guard in
    # `ratify_settlement_confirm` provides defense in depth for
    # dialogues that bypass this path (fixture-staged or save-loaded).
    war_instance = (getattr(world, "war_instances", {}) or {}).get(war_id) or {}
    revalidation = validate_settlement_terms(
        replacement_terms,
        proposer_side=str(dialogue.get("proposer_side") or ""),
        covered_enemy_participants=covered,
        world=world,
        war_instance=war_instance,
    )
    if not revalidation.get("valid"):
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": action,
            "war_id": war_id,
            "error": "submitted_terms_failed_revalidation",
            "error_display": _error_display(
                "submitted_terms_failed_revalidation"
            ),
            "validation_error": revalidation.get("error"),
            "validation_detail": revalidation.get("disabled_reason_display"),
            "validation_error_index": revalidation.get("error_index"),
            "mutated": False,
            "suppress_proposal_result_popup": True,
        }
    preview = build_settlement_preview(
        world,
        war_id=war_id,
        proposer_side=str(dialogue.get("proposer_side") or ""),
        settlement_terms=replacement_terms,
        covered_enemy_participants=covered,
        actor_nation=actor,
        ignore_active_dialogue=True,
    )
    if not preview.get("success"):
        return {
            "success": False,
            "dialogue_type": "settlement_confirm",
            "action": action,
            "war_id": war_id,
            "error": preview.get("error") or "settlement_replacement_failed_preview",
            "error_display": preview.get("error_display") or (
                "The replacement draft could not be previewed."
            ),
            "mutated": False,
            "suppress_proposal_result_popup": True,
        }
    new_dialogue = build_settlement_confirm_dialogue(
        world,
        preview,
        selected_target_nation=selected_target or None,
        caller_kind=str(dialogue.get("caller_kind") or "player_editor"),
        white_peace=bool(dialogue.get("white_peace", False)),
        surrender_preset=surrender_preset,
    )
    drafts = getattr(world, "pending_settlement_drafts", None)
    if drafts is None:
        world.pending_settlement_drafts = {}
        drafts = world.pending_settlement_drafts
    drafts[war_id] = [dict(t) for t in replacement_terms]
    # SC-5R-1 scoped draft persistence: dual-write the replacement
    # draft into the scoped store keyed by `compute_settlement_draft_key`
    # so a same-war restage with a different selected target /
    # covered scope keeps both drafts addressable. Legacy
    # `pending_settlement_drafts[war_id]` storage is preserved for
    # backward compatibility within SC-5R-1 (SC-5R-2 routes the
    # Godot editor through the scoped store and may decommission it).
    save_scoped_settlement_draft(
        world,
        war_id=war_id,
        selected_target_nation=selected_target,
        covered_enemy_participants=covered,
        settlement_terms=replacement_terms,
    )
    world.dialogue_manager.replace(new_dialogue)
    result = {
        "success": True,
        "dialogue_type": "settlement_confirm",
        "action": action,
        "war_id": war_id,
        "diplomatic_dialogue": new_dialogue,
        "settlement_preview": preview["settlement_preview"],
        "awaiting_diplomatic_response": True,
        "mutated": False,
        "message": message,
        "suppress_proposal_result_popup": True,
    }
    if (
        action == "apply_concession_baseline_replacement"
        and new_dialogue.get("can_edit_terms")
        and new_dialogue.get("editor_route")
    ):
        result["open_editor_on_mount"] = True
    return result


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

    All five verbs are PLAYER-ONLY (the Slice-G boundary, mirroring the editor
    ``can_edit_terms`` gate): a non-player staging never reaches an authoring
    redraw. Dials and coverage edits re-draft + re-score live over one shared
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
        new_terms = _redial_settlement_terms(
            terms=terms,
            scope_courts=scope_courts,
            direction=direction,
            proposer_side_leader=proposer_leader,
        )
        verb = "Pressed" if direction == "harsher" else "Eased"
        target_label = "the whole table" if scope == "table" else scope
        return _restage_settlement_after_redraw(
            world,
            dialogue,
            action=action,
            new_terms=new_terms,
            new_covered=covered,
            message=f"{verb} {target_label}.",
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


def handle_settlement_dialogue_action(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    action_params: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Handle C2 settlement dialogue actions.

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
        result = _handle_settlement_tier2_action(
            world, action=action, dialogue=dialogue, action_params=action_params,
        )
        # Re-show safety net: a Tier-2 affordance hides the popup on click
        # (proposal_confirm_popup.gd::_on_settlement_tier2_affordance) and
        # relies on the response carrying `diplomatic_dialogue` to re-mount it
        # (main.gd::_response_has_proposal_confirm_route). A blocked / no-op
        # action that returns a bare error therefore ORPHANS the popup — the
        # player is left with no surface while the settlement_confirm dialogue
        # stays mounted (so the war detail also greys out "Open Settlement" and
        # any reopen targets the still-mounted scope). Dropping the last
        # covered court hit exactly this. Re-attach the unchanged mounted
        # dialogue so the popup re-mounts on its current state with the
        # humanized reason intact. Player-editor only (a non-player caller has
        # no popup to strand).
        if (
            isinstance(result, Mapping)
            and not result.get("success")
            and not result.get("diplomatic_dialogue")
            and isinstance(dialogue, Mapping)
            and dialogue
            and str(dialogue.get("caller_kind") or "") == SETTLEMENT_EDITOR_CALLER_KIND
        ):
            result = dict(result)
            result["diplomatic_dialogue"] = dict(dialogue)
            result.setdefault("awaiting_diplomatic_response", True)
        return result
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
        new_dialogue = build_settlement_confirm_dialogue(
            world,
            baseline_preview,
            selected_target_nation=selected_target or None,
            caller_kind=str(dialogue.get("caller_kind") or "player_editor"),
            white_peace=False,
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
        if new_dialogue.get("can_edit_terms") and new_dialogue.get("editor_route"):
            result["open_editor_on_mount"] = True
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
        # SC-5 reversal commit 2: `request_settlement_revision` opens a
        # real counter / edit route by staging `settlement_confirm` in
        # player-editor mode seeded with the exact offered terms. The
        # player can revise and then submit / ratify as a counter, or
        # back out of the editor without sending a counter. The original
        # offer entry is removed because the player has explicitly
        # chosen to counter (rather than leaving the offer open in the
        # mailbox alongside an editor draft). Click-time revalidation
        # still runs through `stage_settlement_confirm`, so a
        # state-changed war returns a humanized error instead of
        # opening a stale editor.
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
            # Player-editor mode so the editor controls (Submit for
            # Review, clause edits, Back Out / discard confirm) appear
            # the way they do for the standard player-authored
            # settlement review. The offered terms become the initial
            # draft.
            "caller_kind": "player_editor",
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
        if (
            result.get("success")
            and isinstance(result.get("diplomatic_dialogue"), dict)
            and result["diplomatic_dialogue"].get("can_edit_terms")
            and result["diplomatic_dialogue"].get("editor_route")
        ):
            # Request Revision is an explicit counter-authoring choice;
            # mount EDIT immediately instead of making the player click
            # Revise Terms on an intermediate REVIEW popup.
            result["open_editor_on_mount"] = True
        # Echo the originating offer terms so audits / observers can
        # confirm the counter editor was seeded from the exact offered
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
