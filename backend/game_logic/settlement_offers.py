"""Incoming settlement offers, ally petitions, recurring payments (CH-1 split, layer 6).

Incoming-offer popup/promotion/handling, ally settlement petitions
(build/queue/handle), and process_recurring_settlement_payments.
Split from settlement_preview.py (CH-1); top data layer — may import every
lower settlement_* module.
"""

from __future__ import annotations

import copy

from backend.game_logic.diplomatic_templates import (
    resolve_named_diplomat,
    resolve_settlement_voice_line,
)
from backend.game_logic.settlement_presentation import _term_display
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
from backend.game_logic.settlement_scoring import MAX_SETTLEMENT_CLAUSE_COUNT
from backend.game_logic.settlement_routes import (
    _error_display,
    _no_reopen_target_payload,
    _safe_reopen_response,
    _war_label,
    is_war_archived,
    is_war_known,
)
from backend.game_logic.settlement_staging import stage_settlement_confirm
from backend.game_logic.settlement_validation import (
    VALID_SIDES,
    _pair_nations,
    _side_for_nation,
    get_coverable_enemy_participants,
)


ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE = "ally_settlement_petition"


ALLY_SETTLEMENT_PETITION_REQUEST_OPEN = "request_open_settlement"


ALLY_SETTLEMENT_PETITION_WARN_SELLOUT = "warn_against_sellout"


# Slice H (approved July 3, 2026): the two full-agency petition types
# deferred by SC-32 / G2-Slice-G2b. `request_reward_or_restoration` asks
# for a concrete stake (occupied-homeland restoration, or a contribution-
# earned reward); `demand_bargain_honor` warns when the staged terms put a
# live war bargain at risk BEFORE ratification makes the breach real.
ALLY_SETTLEMENT_PETITION_REWARD = "request_reward_or_restoration"


ALLY_SETTLEMENT_PETITION_BARGAIN_HONOR = "demand_bargain_honor"


ALLY_SETTLEMENT_PETITION_FULL_AGENCY_TYPES = frozenset({
    ALLY_SETTLEMENT_PETITION_REWARD,
    ALLY_SETTLEMENT_PETITION_BARGAIN_HONOR,
})


ALLY_SETTLEMENT_PETITION_SHIPPED_TYPES = frozenset({
    ALLY_SETTLEMENT_PETITION_REQUEST_OPEN,
    ALLY_SETTLEMENT_PETITION_WARN_SELLOUT,
    ALLY_SETTLEMENT_PETITION_REWARD,
    ALLY_SETTLEMENT_PETITION_BARGAIN_HONOR,
})


ALLY_SETTLEMENT_PETITION_SOLICITED_TRIGGERS = frozenset({
    "open_settlement",
    "stage_settlement",
    "reject_settlement_offer",
})


ALLY_SETTLEMENT_PETITION_ACK_ACTION = "acknowledge_ally_settlement_petition"


# Slice H action ids (W1 three-place sync: this module's dispatch arm in
# `diplomatic_executor._process_dialogue_choice`, Godot main.gd
# SETTLEMENT_DIALOGUE_ACTIONS, tests/test_godot_parse_harness.py).
ALLY_SETTLEMENT_PETITION_GRANT_ACTION = "grant_ally_petition_clause"
ALLY_SETTLEMENT_PETITION_DECLINE_ACTION = "decline_ally_petition"
ALLY_SETTLEMENT_PETITION_HONOR_ACTION = "honor_bargain_in_settlement"


# Slice H constants (D-H4, named in SYSTEMS_REFERENCE.md): per-(war, ally)
# cooldown after ANY petition resolution (matches REQUEST_TERMS_COOLDOWN_TURNS);
# at most 2 live ally-petition dialogues; the advisory-tier decline dip
# (§16.6 of the ally-participation spec authorizes the light touch — the
# ratify-time shut-out / breach pipelines own the real teeth, D-H2).
ALLY_PETITION_COOLDOWN_TURNS = 5
ALLY_PETITION_MAX_LIVE = 2
ALLY_PETITION_DECLINE_RELATION_DELTA = -3
# Decline memories expire on the sold-out presentation window.
ALLY_PETITION_DECLINED_MEMORY_TURNS = 10
# Gold fallback for a reward petition when no region candidate survives
# validation — clamped to the payer's remaining budget headroom.
ALLY_PETITION_GOLD_REWARD_AMOUNT = 200


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


def _ally_petition_voice_suffix(ally_nation: str) -> str:
    return {
        "Britain": "castlereagh",
        "Prussia": "hardenberg",
        "Austria": "metternich",
        "Saxony": "einsiedel",
    }.get(str(ally_nation or ""), "chancery")


def _ally_petition_voice_family(petition_type: str, ally_nation: str) -> str:
    return (
        f"settlement_ally_petition_{petition_type}_"
        f"{_ally_petition_voice_suffix(ally_nation)}"
    )


def _ally_petition_resolution_voice(ally: str, kind: str, **slots: Any) -> str:
    """Grant/decline/honor acknowledgment line, spoken by the ally's named
    diplomat register with chancery fallback (§7)."""
    line = resolve_settlement_voice_line(
        f"settlement_ally_petition_{kind}_{_ally_petition_voice_suffix(ally)}",
        **slots,
    )
    if not line:
        line = resolve_settlement_voice_line(
            f"settlement_ally_petition_{kind}_chancery",
            **slots,
        )
    return line


def _ally_petition_summary_text(petition: Mapping[str, Any]) -> str:
    ally = str(petition.get("ally_nation") or "An ally")
    ptype = str(petition.get("petition_type") or "")
    claim_region = str(petition.get("claim_region") or "a claim")
    target_enemy = str(petition.get("target_enemy") or "the enemy")
    if ptype == ALLY_SETTLEMENT_PETITION_REQUEST_OPEN:
        return f"{ally} asks to be heard before {claim_region} is left outside peace."
    if ptype == ALLY_SETTLEMENT_PETITION_WARN_SELLOUT:
        return f"{ally} warns that {claim_region} against {target_enemy} is omitted."
    if ptype == ALLY_SETTLEMENT_PETITION_REWARD:
        if str(petition.get("basis") or "") == "restoration":
            return f"{ally} petitions for the return of {claim_region}."
        return f"{ally} petitions for {claim_region} as reward for its arms."
    if ptype == ALLY_SETTLEMENT_PETITION_BARGAIN_HONOR:
        return f"{ally} demands France honor its pledge on {claim_region}."
    return f"{ally} petitions over settlement scope."


# ---------------------------------------------------------------------------
# Slice H — full-agency ally petition substrate (approved July 3, 2026)
# ---------------------------------------------------------------------------


def _ally_petition_state_store(world: Any) -> Dict[str, Dict[str, Any]]:
    store = getattr(world, "ally_petition_state", None)
    if not isinstance(store, dict):
        store = {}
        world.ally_petition_state = store
    return store


def _ally_petition_state_key(war_id: str, ally: str) -> str:
    return f"{war_id}|{ally}"


def _ally_petition_on_cooldown(world: Any, war_id: str, ally: str) -> bool:
    entry = _ally_petition_state_store(world).get(
        _ally_petition_state_key(str(war_id or ""), str(ally or ""))
    )
    if not isinstance(entry, Mapping):
        return False
    current_turn = int(getattr(world, "current_turn", 0) or 0)
    return current_turn < int(entry.get("cooldown_until_turn", 0) or 0)


def _record_ally_petition_resolution(
    world: Any,
    *,
    war_id: str,
    ally: str,
    petition_type: str,
    resolution: str,
) -> None:
    """Stamp the §5/§6 per-(war, ally) resolution state: the 5-turn absolute
    cooldown plus the granted/declined type memory feeding voice."""
    store = _ally_petition_state_store(world)
    key = _ally_petition_state_key(str(war_id or ""), str(ally or ""))
    entry = store.get(key)
    if not isinstance(entry, dict):
        entry = {
            "last_petition_turn": 0,
            "cooldown_until_turn": 0,
            "declined_types": [],
            "granted_types": [],
        }
        store[key] = entry
    current_turn = int(getattr(world, "current_turn", 0) or 0)
    entry["last_petition_turn"] = current_turn
    entry["cooldown_until_turn"] = current_turn + ALLY_PETITION_COOLDOWN_TURNS
    bucket = "granted_types" if resolution == "granted" else "declined_types"
    types = list(entry.get(bucket) or [])
    if petition_type not in types:
        types.append(str(petition_type))
    entry[bucket] = types


def _count_live_ally_petitions(world: Any) -> int:
    """Live ally-petition dialogues across the active slot, the queue, and
    the pending store (§6 salience cap input)."""
    count = 0
    dm = getattr(world, "dialogue_manager", None)
    if dm is not None:
        current = dm.peek() if hasattr(dm, "peek") else getattr(dm, "_current", None)
        if (
            isinstance(current, Mapping)
            and current.get("type") == ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE
        ):
            count += 1
        queued = (
            dm.iter_queue()
            if hasattr(dm, "iter_queue")
            else (getattr(dm, "_queue", None) or [])
        )
        for queued_dialogue in queued:
            if (
                isinstance(queued_dialogue, Mapping)
                and queued_dialogue.get("type")
                == ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE
            ):
                count += 1
    for entry in getattr(world, "pending_settlement_dialogues", []) or []:
        if (
            isinstance(entry, Mapping)
            and entry.get("type") == ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE
        ):
            count += 1
    return count


def _territory_clause_regions(term: Mapping[str, Any]) -> List[str]:
    """Normalize the `region` / `regions` clause-shape variants (the same
    tolerance the ratify path applies via `_territory_term_regions`)."""
    regions = [str(r) for r in (term.get("regions") or []) if r]
    single = str(term.get("region") or "")
    if single and single not in regions:
        regions.append(single)
    return regions


def _petition_clause_prevalidates(
    world: Any,
    clause: Mapping[str, Any],
    *,
    settlement_terms: Iterable[Mapping[str, Any]],
    covered_enemy_participants: Iterable[str],
) -> bool:
    """§3.2 pre-checks at queue time AND at Grant click time: the petition
    never asks for something the draft cannot legally hold (no-false-
    affordance — the G4F-16 / G1 pattern). V1 double-promise, clause cap,
    V3 side partition (payer must be a covered enemy), payer still holds
    the region / can fund the gold."""
    terms = [t for t in (settlement_terms or []) if isinstance(t, Mapping)]
    covered = {str(n) for n in (covered_enemy_participants or []) if n}
    if len(terms) >= MAX_SETTLEMENT_CLAUSE_COUNT:
        return False
    payer = str(clause.get("from") or "")
    if payer not in covered:
        return False
    ctype = str(clause.get("type") or "")
    if ctype == "territory_cede":
        regions = _territory_clause_regions(clause)
        if not regions:
            return False
        from backend.game_logic.settlement_baseline import (
            _promised_regions_in_terms,
        )

        promised = _promised_regions_in_terms(terms)
        for region in regions:
            if region in promised:
                return False
            region_obj = (getattr(world, "regions", {}) or {}).get(region)
            if region_obj is None or str(
                getattr(region_obj, "controller", "") or ""
            ) != payer:
                return False
        return True
    if ctype == "gold_indemnity":
        amount = int(clause.get("amount", 0) or 0)
        if amount <= 0:
            return False
        from backend.game_logic.settlement_actions import (
            _gold_headroom_for_payer,
        )

        candidate_terms = [dict(t) for t in terms] + [dict(clause)]
        headroom = _gold_headroom_for_payer(
            world,
            candidate_terms,
            payer=payer,
            exclude_index=len(candidate_terms) - 1,
        )
        return amount <= headroom
    return False


def _ally_material_share(world: Any, war_id: str, ally: str, side: str) -> float:
    from backend.game_logic.war_contribution import material_contribution_share

    try:
        return float(material_contribution_share(world, war_id, ally, side))
    except Exception:
        return 0.0


def _ally_has_reward_standing(
    world: Any, war_id: str, ally: str, side: str
) -> bool:
    """D-H3: contribution-based asks need `seat` or `consult` standing.
    Restoration basis is exempt (checked by the caller)."""
    from backend.game_logic.war_contribution import standing_for_participant

    try:
        standing = standing_for_participant(world, war_id, ally, side=side)
    except Exception:
        return False
    return standing in ("seat", "consult")


def _restoration_region_for_ally(
    world: Any,
    ally: str,
    *,
    covered_enemy_participants: Iterable[str],
) -> Tuple[str, str]:
    """Strongest basis (§3.1): a region with `starting_controller == ally`
    currently controlled by a covered enemy court. Returns
    ``(region, holder)`` or ``("", "")``."""
    covered = {str(n) for n in (covered_enemy_participants or []) if n}
    starting = (getattr(world, "nation_starting_regions", {}) or {}).get(ally, [])
    regions = getattr(world, "regions", {}) or {}
    for region in sorted(str(r) for r in starting):
        region_obj = regions.get(region)
        if region_obj is None:
            continue
        holder = str(getattr(region_obj, "controller", "") or "")
        if holder in covered and holder != ally:
            return region, holder
    return "", ""


def _reward_region_for_ally(
    world: Any,
    ally: str,
    *,
    war_id: str,
    covered_enemy_participants: Iterable[str],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> Tuple[str, str]:
    """Contribution basis region: an unsatisfied objective claim from
    `_active_objective_claims_for_ally`, else a coveted region
    (`NATION_DESIRE_PROFILES.covets_regions`) held by a covered enemy."""
    covered = {str(n) for n in (covered_enemy_participants or []) if n}
    regions = getattr(world, "regions", {}) or {}
    terms = [t for t in (settlement_terms or []) if isinstance(t, Mapping)]
    for claim in _active_objective_claims_for_ally(
        world, ally, required_war_id=str(war_id or "")
    ):
        if _settlement_terms_satisfy_ally_claim(terms, claim):
            continue
        claim_region = str(claim.get("claim_region") or "")
        region_obj = regions.get(claim_region)
        if region_obj is None:
            continue
        holder = str(getattr(region_obj, "controller", "") or "")
        if holder in covered and holder != ally:
            return claim_region, holder
    from backend.game_logic.diplomatic_templates import NATION_DESIRE_PROFILES

    profile = NATION_DESIRE_PROFILES.get(ally) or {}
    for region in [str(r) for r in (profile.get("covets_regions") or [])]:
        region_obj = regions.get(region)
        if region_obj is None:
            continue
        holder = str(getattr(region_obj, "controller", "") or "")
        if holder in covered and holder != ally:
            return region, holder
    return "", ""


def _find_reward_or_restoration_petition_contexts(
    world: Any,
    *,
    war_id: str,
    covered_enemy_participants: Iterable[str],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """Slice H §3.1 — ranked `request_reward_or_restoration` candidates.

    Restoration basis first (always eligible — an occupied homeland may
    always ask), then contribution basis (D-H3: seat/consult standing).
    Every candidate carries the exact valid-by-construction clause Grant
    would inject (§3.2) — a candidate whose clause fails pre-validation is
    dropped (gold fallback tried first for contribution asks)."""
    player = str(getattr(world, "player_nation", "France") or "France")
    war = (getattr(world, "war_instances", {}) or {}).get(str(war_id or ""))
    if not isinstance(war, Mapping) or war.get("ended_turn") is not None:
        return []
    player_side = _side_for_nation(war, player)
    if player_side not in VALID_SIDES:
        return []
    covered = [str(n) for n in (covered_enemy_participants or []) if n]
    terms = [t for t in (settlement_terms or []) if isinstance(t, Mapping)]
    war_label = _war_label_for_id(world, str(war_id or ""))
    candidates: List[Dict[str, Any]] = []
    same_side = [
        str(nation)
        for nation in (war.get(player_side) or [])
        if str(nation) and str(nation) != player
    ]
    for ally in sorted(same_side):
        if _ally_petition_on_cooldown(world, str(war_id or ""), ally):
            continue
        share = _ally_material_share(world, str(war_id or ""), ally, player_side)
        basis = ""
        clause: Optional[Dict[str, Any]] = None
        region, holder = _restoration_region_for_ally(
            world, ally, covered_enemy_participants=covered
        )
        if region:
            basis = "restoration"
            # `region` singular — the guided authoring surface's clause
            # shape (settlement_demand_add); the validator + ratify
            # normalize both variants.
            clause = {
                "type": "territory_cede",
                "from": holder,
                "to": ally,
                "region": region,
            }
            if not _petition_clause_prevalidates(
                world,
                clause,
                settlement_terms=terms,
                covered_enemy_participants=covered,
            ):
                clause = None
        if clause is None and _ally_has_reward_standing(
            world, str(war_id or ""), ally, player_side
        ):
            region, holder = _reward_region_for_ally(
                world,
                ally,
                war_id=str(war_id or ""),
                covered_enemy_participants=covered,
                settlement_terms=terms,
            )
            if region:
                basis = "contribution"
                clause = {
                    "type": "territory_cede",
                    "from": holder,
                    "to": ally,
                    "region": region,
                }
                if not _petition_clause_prevalidates(
                    world,
                    clause,
                    settlement_terms=terms,
                    covered_enemy_participants=covered,
                ):
                    # §3.2 gold fallback: a modest indemnity to the ally
                    # inside the payer's remaining budget headroom.
                    clause = {
                        "type": "gold_indemnity",
                        "from": holder,
                        "to": ally,
                        "amount": int(ALLY_PETITION_GOLD_REWARD_AMOUNT),
                    }
                    if not _petition_clause_prevalidates(
                        world,
                        clause,
                        settlement_terms=terms,
                        covered_enemy_participants=covered,
                    ):
                        clause = None
        if clause is None or not basis:
            continue
        target_enemy = str(clause.get("from") or "")
        claim_region = (
            _territory_clause_regions(clause)[0]
            if clause.get("type") == "territory_cede"
            else str(region or "")
        )
        if basis == "restoration":
            basis_display = (
                f"{target_enemy} occupies {claim_region} — "
                f"{ally}'s own soil."
            )
        else:
            basis_display = (
                f"{ally} fought for this coalition and presses its claim."
            )
        candidates.append({
            "war_id": str(war_id or ""),
            "war_label": war_label,
            "ally_nation": ally,
            "petition_type": ALLY_SETTLEMENT_PETITION_REWARD,
            "basis": basis,
            "basis_display": basis_display,
            "claim_region": claim_region,
            "target_enemy": target_enemy,
            "candidate_clause": dict(clause),
            "material_share": share,
        })
    # Restoration outranks reward; ties by material contribution share (§6).
    candidates.sort(
        key=lambda c: (
            0 if c.get("basis") == "restoration" else 1,
            -float(c.get("material_share") or 0.0),
            str(c.get("ally_nation") or ""),
        )
    )
    return candidates


def _bargain_at_risk_case(
    world: Any,
    bargain: Mapping[str, Any],
    *,
    settlement_terms: Iterable[Mapping[str, Any]],
    covered_enemy_participants: Iterable[str],
) -> str:
    """Dry-run the ALREADY-LANDED ratify-time predicates against the STAGED
    terms (§4.1): `imminent_breach` when the claim region is awarded to a
    third party; `abandonment` when the settlement makes peace with the
    bargain's target enemy while France neither holds nor gains the claim
    region. Returns "" when the staged terms leave the bargain safe."""
    player = str(getattr(world, "player_nation", "France") or "France")
    promiser = str(bargain.get("promiser") or "")
    beneficiary = str(bargain.get("beneficiary") or "")
    claim_region = str(
        (bargain.get("claim_term") or {}).get("claim_region") or ""
    )
    if not claim_region:
        return ""
    terms = [t for t in (settlement_terms or []) if isinstance(t, Mapping)]
    covered = {str(n) for n in (covered_enemy_participants or []) if n}
    for term in terms:
        if str(term.get("type") or "") != "territory_cede":
            continue
        if claim_region not in _territory_clause_regions(term):
            continue
        recipient = str(term.get("beneficiary") or term.get("to") or "")
        if recipient and recipient not in (promiser, beneficiary):
            return "imminent_breach"
    target_enemy = str(bargain.get("target_enemy") or "")
    if target_enemy and target_enemy in covered:
        region_obj = (getattr(world, "regions", {}) or {}).get(claim_region)
        france_holds = (
            region_obj is not None
            and str(getattr(region_obj, "controller", "") or "") == player
        )
        france_gains = any(
            str(term.get("type") or "") == "territory_cede"
            and str(term.get("to") or "") == player
            and claim_region in _territory_clause_regions(term)
            for term in terms
        )
        if not france_holds and not france_gains:
            return "abandonment"
    return ""


def _find_bargain_honor_petition_contexts(
    world: Any,
    *,
    war_id: str,
    covered_enemy_participants: Iterable[str],
    settlement_terms: Iterable[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """Slice H §4.1 — ranked `demand_bargain_honor` candidates: a live war
    bargain promised by France whose beneficiary fights on France's side in
    this war, put at risk by the staged terms."""
    from backend.game_logic.diplomacy import (
        BARGAIN_BREACH_COOLDOWN_TURNS,
        BARGAIN_BREACH_RELATION_DELTA,
        BARGAIN_BREACH_RELIABILITY_DELTA,
        _get_live_bargains_by_promiser,
    )

    player = str(getattr(world, "player_nation", "France") or "France")
    war = (getattr(world, "war_instances", {}) or {}).get(str(war_id or ""))
    if not isinstance(war, Mapping) or war.get("ended_turn") is not None:
        return []
    player_side = _side_for_nation(war, player)
    if player_side not in VALID_SIDES:
        return []
    same_side = {
        str(nation)
        for nation in (war.get(player_side) or [])
        if str(nation) and str(nation) != player
    }
    covered = [str(n) for n in (covered_enemy_participants or []) if n]
    terms = [t for t in (settlement_terms or []) if isinstance(t, Mapping)]
    war_label = _war_label_for_id(world, str(war_id or ""))
    candidates: List[Dict[str, Any]] = []
    for bargain in _get_live_bargains_by_promiser(world, player):
        beneficiary = str(bargain.get("beneficiary") or "")
        if beneficiary not in same_side:
            continue
        if _ally_petition_on_cooldown(world, str(war_id or ""), beneficiary):
            continue
        case = _bargain_at_risk_case(
            world,
            bargain,
            settlement_terms=terms,
            covered_enemy_participants=covered,
        )
        if not case:
            continue
        claim_region = str(
            (bargain.get("claim_term") or {}).get("claim_region") or ""
        )
        candidate_clause: Optional[Dict[str, Any]] = None
        if case == "abandonment":
            # Honoring an abandonment means France TAKES the claim region at
            # this table (WB v1: the bargain promises France's claim
            # priority). No-false-affordance: skip when no covered enemy
            # holds it.
            region_obj = (getattr(world, "regions", {}) or {}).get(claim_region)
            holder = str(getattr(region_obj, "controller", "") or "") if region_obj else ""
            candidate_clause = {
                "type": "territory_cede",
                "from": holder,
                "to": player,
                "region": claim_region,
            }
            if not _petition_clause_prevalidates(
                world,
                candidate_clause,
                settlement_terms=terms,
                covered_enemy_participants=covered,
            ):
                continue
        created_turn = int(bargain.get("created_turn", 0) or 0)
        consequence_display = (
            f"Proceeding to ratification breaches the pledge: "
            f"{BARGAIN_BREACH_RELIABILITY_DELTA} reliability, "
            f"{BARGAIN_BREACH_RELATION_DELTA} relation with {beneficiary}, "
            f"a betrayal strike, and a {BARGAIN_BREACH_COOLDOWN_TURNS}-turn "
            f"bargain cooldown."
        )
        candidates.append({
            "war_id": str(war_id or ""),
            "war_label": war_label,
            "ally_nation": beneficiary,
            "petition_type": ALLY_SETTLEMENT_PETITION_BARGAIN_HONOR,
            "basis": case,
            "basis_display": (
                f"France pledged its claim on {claim_region} to secure "
                f"{beneficiary}'s arms (turn {created_turn})."
            ),
            "claim_region": claim_region,
            "target_enemy": str(bargain.get("target_enemy") or ""),
            "bargain_id": str(bargain.get("id") or ""),
            "bargain_created_turn": created_turn,
            "consequence_display": consequence_display,
            "candidate_clause": (
                dict(candidate_clause) if candidate_clause else None
            ),
            "material_share": _ally_material_share(
                world, str(war_id or ""), beneficiary, player_side
            ),
        })
    candidates.sort(
        key=lambda c: (
            -float(c.get("material_share") or 0.0),
            str(c.get("ally_nation") or ""),
        )
    )
    return candidates


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
        # Slice H slots (leniently resolved — absent for the G2b types).
        "basis_display": str(context.get("basis_display") or ""),
        "created_turn_label": (
            f"turn {int(context.get('bargain_created_turn', 0) or 0)}"
        ),
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
    candidate_clause = context.get("candidate_clause")
    if isinstance(candidate_clause, Mapping):
        candidate_clause = dict(candidate_clause)
    else:
        candidate_clause = None
    if petition_type == ALLY_SETTLEMENT_PETITION_REWARD:
        options = [
            {
                "label": "Grant the Claim",
                "description": (
                    "Add the petitioned clause to the settlement draft and "
                    "re-score every court."
                ),
                "action": ALLY_SETTLEMENT_PETITION_GRANT_ACTION,
                "available": True,
            },
            {
                "label": "Decline",
                "description": (
                    "Refuse the petition. The ally remembers the answer; "
                    "concluding the peace without them carries its own cost."
                ),
                "action": ALLY_SETTLEMENT_PETITION_DECLINE_ACTION,
                "available": True,
            },
        ]
    elif petition_type == ALLY_SETTLEMENT_PETITION_BARGAIN_HONOR:
        options = [
            {
                "label": "Honor the Bargain",
                "description": (
                    "Adjust the settlement draft so France's pledged claim "
                    "survives ratification."
                ),
                "action": ALLY_SETTLEMENT_PETITION_HONOR_ACTION,
                "available": True,
            },
            {
                "label": "Proceed Regardless",
                "description": (
                    "Keep the draft as it stands. Ratifying it breaches the "
                    "pledge with the full landed penalty."
                ),
                "action": ALLY_SETTLEMENT_PETITION_DECLINE_ACTION,
                "available": True,
            },
        ]
    else:
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
        "available_action_ids": [
            str(opt.get("action") or "") for opt in options
        ],
    }
    if petition_type in ALLY_SETTLEMENT_PETITION_FULL_AGENCY_TYPES:
        # Slice H payload: the concrete valid-by-construction candidate
        # clause (§3.2), the named basis (§13.4 rule), and — for bargain
        # honor — the exact landed consequence ladder (§4.2, no invented
        # numbers).
        dialogue["basis"] = str(context.get("basis") or "")
        dialogue["basis_display"] = str(context.get("basis_display") or "")
        dialogue["candidate_clause"] = candidate_clause
        dialogue["candidate_clause_display"] = (
            _term_display(candidate_clause) if candidate_clause else ""
        )
        if petition_type == ALLY_SETTLEMENT_PETITION_BARGAIN_HONOR:
            dialogue["bargain_id"] = str(context.get("bargain_id") or "")
            dialogue["bargain_created_turn"] = int(
                context.get("bargain_created_turn", 0) or 0
            )
            dialogue["consequence_display"] = str(
                context.get("consequence_display") or ""
            )
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
    payload = {
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
    if str(dialogue.get("petition_type") or "") in (
        ALLY_SETTLEMENT_PETITION_FULL_AGENCY_TYPES
    ):
        candidate_clause = dialogue.get("candidate_clause")
        payload["basis"] = str(dialogue.get("basis") or "")
        payload["basis_display"] = str(dialogue.get("basis_display") or "")
        payload["candidate_clause"] = (
            dict(candidate_clause)
            if isinstance(candidate_clause, Mapping)
            else None
        )
        payload["candidate_clause_display"] = str(
            dialogue.get("candidate_clause_display") or ""
        )
        payload["bargain_id"] = str(dialogue.get("bargain_id") or "")
        payload["consequence_display"] = str(
            dialogue.get("consequence_display") or ""
        )
    return payload


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
    if (
        petition_type in ALLY_SETTLEMENT_PETITION_FULL_AGENCY_TYPES
        and _count_live_ally_petitions(world) >= ALLY_PETITION_MAX_LIVE
    ):
        # §6 salience cap: at most 2 live ally-petition dialogues.
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
    if petition_type in ALLY_SETTLEMENT_PETITION_FULL_AGENCY_TYPES:
        # §5: stamp the ask turn (the cooldown stamps at RESOLUTION).
        store = _ally_petition_state_store(world)
        key = _ally_petition_state_key(
            str(dialogue.get("war_id") or ""),
            str(dialogue.get("ally_nation") or ""),
        )
        entry = store.get(key)
        if not isinstance(entry, dict):
            entry = {
                "last_petition_turn": 0,
                "cooldown_until_turn": 0,
                "declined_types": [],
                "granted_types": [],
            }
            store[key] = entry
        entry["last_petition_turn"] = int(
            getattr(world, "current_turn", 0) or 0
        )
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
    queued: List[Dict[str, Any]] = []

    def _queue_full_agency_candidates(
        candidates: List[Dict[str, Any]],
    ) -> None:
        """Slice H §6: queue in salience order, one petition per (war,
        ally) per trigger, `_queue_ally_settlement_petition` enforcing the
        2-live cap and the petition_key dedupe."""
        allies_this_trigger = {
            str(p.get("ally_nation") or "") for p in queued
        }
        for candidate in candidates:
            ally = str(candidate.get("ally_nation") or "")
            if not ally or ally in allies_this_trigger:
                continue
            petition = _queue_ally_settlement_petition(
                world,
                petition_type=str(candidate.get("petition_type") or ""),
                context=candidate,
                trigger_action=trigger_action,
            )
            if petition is not None:
                queued.append(petition)
                allies_this_trigger.add(ally)

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
        if petition is not None:
            queued.append(petition)
        # Slice H: reward/restoration asks fire from the same solicited
        # sites (§3.1) — never unsolicited (the D7 lock holds).
        _queue_full_agency_candidates(
            _find_reward_or_restoration_petition_contexts(
                world,
                war_id=str(war_id or ""),
                covered_enemy_participants=covered_enemy_participants or [],
                settlement_terms=settlement_terms or [],
            )
        )
        return queued
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
        if petition is not None:
            queued.append(petition)
        if trigger_action == "stage_settlement":
            # Slice H §6 salience: a promise at risk beats a new ask —
            # bargain-honor candidates queue before reward/restoration.
            _queue_full_agency_candidates(
                _find_bargain_honor_petition_contexts(
                    world,
                    war_id=str(war_id or ""),
                    covered_enemy_participants=(
                        covered_enemy_participants or []
                    ),
                    settlement_terms=settlement_terms or [],
                )
            )
            _queue_full_agency_candidates(
                _find_reward_or_restoration_petition_contexts(
                    world,
                    war_id=str(war_id or ""),
                    covered_enemy_participants=(
                        covered_enemy_participants or []
                    ),
                    settlement_terms=settlement_terms or [],
                )
            )
        return queued
    return []


def _remove_ally_petition_dialogue(world: Any, petition_key: str) -> int:
    dm = getattr(world, "dialogue_manager", None)
    if dm is None or not hasattr(dm, "remove_matching"):
        return 0
    return dm.remove_matching(
        lambda item: (
            isinstance(item, Mapping)
            and item.get("type") == ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE
            and (
                not petition_key
                or str(item.get("petition_key") or "") == petition_key
            )
        )
    )


def _pending_envoy_count(world: Any) -> int:
    dm = getattr(world, "dialogue_manager", None)
    if dm is not None and hasattr(dm, "get_mailbox_count"):
        return int(dm.get_mailbox_count())
    return 0


def _mounted_propose_settlement_dialogue(
    world: Any, war_id: str
) -> Optional[Mapping[str, Any]]:
    """The mounted PROPOSE settlement_confirm for `war_id`, or None. Grant /
    Honor inject through the SAME restage seam every guided demand verb
    rides (Building Blocks) — that seam replaces the ACTIVE dialogue slot,
    so the settlement surface must be mounted and in PROPOSE (REVIEW is a
    frozen staged-decision surface — UX-2)."""
    dm = getattr(world, "dialogue_manager", None)
    if dm is None:
        return None
    current = dm.peek() if hasattr(dm, "peek") else getattr(dm, "_current", None)
    if not isinstance(current, Mapping):
        return None
    dtype = str(current.get("type") or current.get("dialogue_type") or "")
    if dtype != "settlement_confirm":
        return None
    if str(current.get("war_id") or "") != str(war_id or ""):
        return None
    if str(current.get("dialogue_mode") or "PROPOSE") != "PROPOSE":
        return None
    return current


def _petition_table_not_mounted_response(
    action: str, war_id: str
) -> Dict[str, Any]:
    return {
        "success": False,
        "dialogue_type": ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE,
        "action": action,
        "war_id": str(war_id or ""),
        "error": "petition_table_not_mounted",
        "error_display": (
            "The settlement table for this war is not open in authoring, "
            "Sire. Open the settlement (Return to Terms if under review), "
            "then answer the petition."
        ),
        "mutated": False,
        "petition_retained": True,
        "suppress_proposal_result_popup": True,
    }


def _suspended_draft_for_war(
    world: Any, war_id: str
) -> Optional[List[Dict[str, Any]]]:
    """The suspended PROPOSE draft for `war_id` from the scoped store
    (PF-2 war-prefix fallback). The REAL Godot answer path reaches Grant /
    Honor with the settlement table SUSPENDED — mailbox activation is
    blocked while a settlement_confirm hard-stop is mounted, so the player
    suspends (draft kept), activates the petition, and answers. The draft
    IS the authoring surface then; staging it back with the granted clause
    is the same promise `suspend → reopen` already makes."""
    from backend.game_logic.settlement_staging import (
        load_scoped_settlement_draft,
    )

    return load_scoped_settlement_draft(
        world,
        war_id=str(war_id or ""),
        selected_target_nation=None,
        covered_enemy_participants=None,
    )


def _default_coverage_for_war(world: Any, war_id: str) -> List[str]:
    player = str(getattr(world, "player_nation", "France") or "France")
    war = (getattr(world, "war_instances", {}) or {}).get(str(war_id or ""))
    if not isinstance(war, Mapping):
        return []
    player_side = _side_for_nation(war, player)
    if player_side not in VALID_SIDES:
        return []
    return [
        str(n)
        for n in get_coverable_enemy_participants(war, player_side)
        if n
    ]


def _stage_granted_terms_from_draft(
    world: Any,
    *,
    action: str,
    war_id: str,
    new_terms: List[Dict[str, Any]],
    message: str,
) -> Dict[str, Any]:
    """Mount the suspended draft WITH the granted adjustment as a fresh
    PROPOSE surface (stage_settlement_confirm re-validates, re-scores, and
    handles same-war replace per LEGB-F2) and persist the scoped draft so
    an immediate re-suspend keeps the grant."""
    player = str(getattr(world, "player_nation", "France") or "France")
    result = stage_settlement_confirm(
        world,
        war_id=str(war_id or ""),
        actor_nation=player,
        settlement_terms=new_terms,
        dialogue_mode="PROPOSE",
    )
    if not result.get("success"):
        result.setdefault("action", action)
        result["suppress_proposal_result_popup"] = True
        return result
    staged = result.get("diplomatic_dialogue") or {}
    from backend.game_logic.settlement_staging import (
        save_scoped_settlement_draft,
    )

    save_scoped_settlement_draft(
        world,
        war_id=str(war_id or ""),
        selected_target_nation=str(
            staged.get("selected_target_nation") or ""
        ) or None,
        covered_enemy_participants=list(
            staged.get("covered_enemy_participants") or []
        ),
        settlement_terms=[
            dict(t)
            for t in (staged.get("settlement_terms") or new_terms)
            if isinstance(t, Mapping)
        ],
    )
    result["action"] = action
    result["message"] = message
    result["suppress_proposal_result_popup"] = True
    return result


def _petition_lapsed_response(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
    message: str,
) -> Dict[str, Any]:
    """G1 click-time re-run pattern: the draft changed since queue time and
    the petitioned adjustment is no longer possible/needed — remove the
    stale dialogue with a voiced notice, never a validator bounce. No
    cooldown stamps: the ally may re-petition on the next staging."""
    removed = _remove_ally_petition_dialogue(
        world, str(dialogue.get("petition_key") or "")
    )
    return {
        "success": True,
        "dialogue_type": ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE,
        "action": action,
        "war_id": str(dialogue.get("war_id") or ""),
        "message": message,
        "mutated": False,
        "petition_lapsed": True,
        "removed_dialogues": int(removed),
        "pending_envoy_count": _pending_envoy_count(world),
        "suppress_proposal_result_popup": True,
    }


def _log_ally_petition_event(
    world: Any, event_type: str, dialogue: Mapping[str, Any]
) -> None:
    if not hasattr(world, "log_event"):
        return
    world.log_event({
        "type": str(event_type),
        "nation": str(getattr(world, "player_nation", "France") or "France"),
        "ally_nation": str(dialogue.get("ally_nation") or ""),
        "petition_type": str(dialogue.get("petition_type") or ""),
        "war_id": str(dialogue.get("war_id") or ""),
        "war_label": str(dialogue.get("war_label") or ""),
        "claim_region": str(dialogue.get("claim_region") or ""),
        "turn": int(getattr(world, "current_turn", 0) or 0),
    })


def _handle_grant_ally_petition(
    world: Any, dialogue: Mapping[str, Any]
) -> Dict[str, Any]:
    """Slice H §3.3 Grant: inject the carried clause into the mounted
    PROPOSE draft through the demand-add/restage seam. The PLAYER clicks
    Grant, so the Slice-G player-only mutation boundary is preserved."""
    war_id = str(dialogue.get("war_id") or "")
    ally = str(dialogue.get("ally_nation") or "")
    settlement_dialogue = _mounted_propose_settlement_dialogue(world, war_id)
    draft_terms: Optional[List[Dict[str, Any]]] = None
    if settlement_dialogue is not None:
        terms = [
            dict(t)
            for t in (settlement_dialogue.get("settlement_terms") or [])
            if isinstance(t, Mapping)
        ]
        covered = [
            str(n)
            for n in (
                settlement_dialogue.get("covered_enemy_participants") or []
            )
            if n
        ]
    else:
        # The REAL Godot flow: the petition is answered with the table
        # SUSPENDED (mailbox activation is blocked by the mounted
        # hard-stop) — the suspended scoped draft is the authoring
        # surface then.
        draft_terms = _suspended_draft_for_war(world, war_id)
        if draft_terms is None:
            return _petition_table_not_mounted_response(
                ALLY_SETTLEMENT_PETITION_GRANT_ACTION, war_id
            )
        terms = draft_terms
        covered = _default_coverage_for_war(world, war_id)
    clause = dialogue.get("candidate_clause")
    if not isinstance(clause, Mapping) or not _petition_clause_prevalidates(
        world,
        clause,
        settlement_terms=terms,
        covered_enemy_participants=covered,
    ):
        return _petition_lapsed_response(
            world,
            action=ALLY_SETTLEMENT_PETITION_GRANT_ACTION,
            dialogue=dialogue,
            message=resolve_settlement_voice_line(
                "settlement_ally_petition_lapsed_talleyrand",
                ally_nation=ally,
            ) or (
                f"Sire, the draft has moved on — {ally}'s ask can no "
                "longer be granted as petitioned."
            ),
        )
    granted_clause = dict(clause)
    # D-H1 (approved): granted clauses carry `ally_petition` provenance and
    # join the dial sweep's protected set — a More-Generous sweep can never
    # silently un-reward the ally; per-row Remove is the deliberate verb.
    granted_clause["authored_by"] = "ally_petition"
    new_terms = [dict(t) for t in terms] + [granted_clause]
    _remove_ally_petition_dialogue(world, str(dialogue.get("petition_key") or ""))
    _record_ally_petition_resolution(
        world,
        war_id=war_id,
        ally=ally,
        petition_type=str(dialogue.get("petition_type") or ""),
        resolution="granted",
    )
    _log_ally_petition_event(
        world, "settlement_ally_petition_granted", dialogue
    )
    clause_label = _term_display(granted_clause)
    grant_line = _ally_petition_resolution_voice(
        ally,
        "granted",
        ally_nation=ally,
        claim_region=str(dialogue.get("claim_region") or ""),
    )
    if settlement_dialogue is None:
        result = _stage_granted_terms_from_draft(
            world,
            action=ALLY_SETTLEMENT_PETITION_GRANT_ACTION,
            war_id=war_id,
            new_terms=new_terms,
            message=f"Granted {ally}'s petition — {clause_label}. {grant_line}",
        )
    else:
        voice_beats = [{
            "kind": "ally_petition_granted",
            "speaker": resolve_named_diplomat("envoy", ally, world),
            "nation": ally,
            "line": grant_line,
        }]
        from backend.game_logic.settlement_staging import (
            _restage_settlement_after_redraw,
        )

        result = _restage_settlement_after_redraw(
            world,
            settlement_dialogue,
            action=ALLY_SETTLEMENT_PETITION_GRANT_ACTION,
            new_terms=new_terms,
            new_covered=covered,
            message=f"Granted {ally}'s petition — {clause_label}.",
            extra={"authoring_voice_beats": voice_beats},
        )
    result["petition_granted"] = {
        "ally_nation": ally,
        "petition_type": str(dialogue.get("petition_type") or ""),
        "clause_display": clause_label,
    }
    return result


def _handle_decline_ally_petition(
    world: Any, dialogue: Mapping[str, Any]
) -> Dict[str, Any]:
    """Slice H §3.3/§4.3 Decline / Proceed Regardless (D-H2: light memory —
    the −3 advisory dip plus the decline record; the ratify-time shut-out /
    breach pipelines own the real teeth, never a second penalty here)."""
    war_id = str(dialogue.get("war_id") or "")
    ally = str(dialogue.get("ally_nation") or "")
    player = str(getattr(world, "player_nation", "France") or "France")
    if ally and hasattr(world, "modify_nation_relation"):
        world.modify_nation_relation(
            player, ally, ALLY_PETITION_DECLINE_RELATION_DELTA
        )
    episode_id = f"petition:{war_id}:{ally}:{int(getattr(world, 'current_turn', 0) or 0)}"
    try:
        from backend.game_logic.diplomacy import _allocate_episode_id

        episode_id = _allocate_episode_id(world, prefix="petition")
    except Exception:
        pass
    from backend.game_logic.settlement_reactions import _add_settlement_memory

    _add_settlement_memory(
        world,
        actor=player,
        subject=ally,
        memory_type="petition_declined",
        episode_id=episode_id,
        payload={
            "war_id": war_id,
            "petition_type": str(dialogue.get("petition_type") or ""),
            "claim_region": str(dialogue.get("claim_region") or ""),
            "relation_delta": ALLY_PETITION_DECLINE_RELATION_DELTA,
        },
        expires_in=ALLY_PETITION_DECLINED_MEMORY_TURNS,
    )
    _record_ally_petition_resolution(
        world,
        war_id=war_id,
        ally=ally,
        petition_type=str(dialogue.get("petition_type") or ""),
        resolution="declined",
    )
    removed = _remove_ally_petition_dialogue(
        world, str(dialogue.get("petition_key") or "")
    )
    _log_ally_petition_event(
        world, "settlement_ally_petition_declined", dialogue
    )
    line = _ally_petition_resolution_voice(
        ally,
        "declined",
        ally_nation=ally,
        claim_region=str(dialogue.get("claim_region") or ""),
    )
    return {
        "success": True,
        "dialogue_type": ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE,
        "action": ALLY_SETTLEMENT_PETITION_DECLINE_ACTION,
        "war_id": war_id,
        "message": line or f"{ally}'s petition is declined, Sire.",
        "mutated": False,
        "petition_declined": {
            "ally_nation": ally,
            "petition_type": str(dialogue.get("petition_type") or ""),
            "relation_delta": ALLY_PETITION_DECLINE_RELATION_DELTA,
        },
        "removed_dialogues": int(removed),
        "pending_envoy_count": _pending_envoy_count(world),
        "suppress_proposal_result_popup": True,
    }


def _handle_honor_bargain_in_settlement(
    world: Any, dialogue: Mapping[str, Any]
) -> Dict[str, Any]:
    """Slice H §4.3 Honor (D-H5: auto-adjust via restage, voiced). WB v1
    semantics: the bargain promises FRANCE's claim priority — honoring
    retargets the conflicting third-party award to France (imminent
    breach), or injects the France-takes-claim cession (abandonment)."""
    war_id = str(dialogue.get("war_id") or "")
    ally = str(dialogue.get("ally_nation") or "")
    player = str(getattr(world, "player_nation", "France") or "France")
    claim_region = str(dialogue.get("claim_region") or "")
    settlement_dialogue = _mounted_propose_settlement_dialogue(world, war_id)
    if settlement_dialogue is not None:
        terms = [
            dict(t)
            for t in (settlement_dialogue.get("settlement_terms") or [])
            if isinstance(t, Mapping)
        ]
        covered = [
            str(n)
            for n in (
                settlement_dialogue.get("covered_enemy_participants") or []
            )
            if n
        ]
    else:
        # Suspended-table flow (same rationale as Grant): honor the pledge
        # inside the suspended scoped draft, then re-mount it.
        draft_terms = _suspended_draft_for_war(world, war_id)
        if draft_terms is None:
            return _petition_table_not_mounted_response(
                ALLY_SETTLEMENT_PETITION_HONOR_ACTION, war_id
            )
        terms = draft_terms
        covered = _default_coverage_for_war(world, war_id)
    from backend.game_logic.diplomacy import _get_live_bargains_by_promiser

    bargain = None
    bargain_id = str(dialogue.get("bargain_id") or "")
    for candidate in _get_live_bargains_by_promiser(world, player):
        if str(candidate.get("id") or "") == bargain_id:
            bargain = candidate
            break
    lapse_message = resolve_settlement_voice_line(
        "settlement_ally_petition_lapsed_talleyrand",
        ally_nation=ally,
    ) or (
        f"Sire, the pledge to {ally} no longer stands in the draft's way."
    )
    if bargain is None:
        return _petition_lapsed_response(
            world,
            action=ALLY_SETTLEMENT_PETITION_HONOR_ACTION,
            dialogue=dialogue,
            message=lapse_message,
        )
    case = _bargain_at_risk_case(
        world,
        bargain,
        settlement_terms=terms,
        covered_enemy_participants=covered,
    )
    if not case:
        return _petition_lapsed_response(
            world,
            action=ALLY_SETTLEMENT_PETITION_HONOR_ACTION,
            dialogue=dialogue,
            message=lapse_message,
        )
    if case == "imminent_breach":
        new_terms: List[Dict[str, Any]] = []
        for term in terms:
            if (
                str(term.get("type") or "") == "territory_cede"
                and claim_region in _territory_clause_regions(term)
                and str(term.get("beneficiary") or term.get("to") or "")
                not in (player, ally)
            ):
                retargeted = dict(term)
                retargeted["to"] = player
                retargeted.pop("beneficiary", None)
                retargeted["authored_by"] = "ally_petition"
                new_terms.append(retargeted)
            else:
                new_terms.append(dict(term))
    else:
        clause = dialogue.get("candidate_clause")
        if not isinstance(clause, Mapping) or not _petition_clause_prevalidates(
            world,
            clause,
            settlement_terms=terms,
            covered_enemy_participants=covered,
        ):
            return _petition_lapsed_response(
                world,
                action=ALLY_SETTLEMENT_PETITION_HONOR_ACTION,
                dialogue=dialogue,
                message=lapse_message,
            )
        honored_clause = dict(clause)
        honored_clause["authored_by"] = "ally_petition"
        new_terms = terms + [honored_clause]
    _remove_ally_petition_dialogue(world, str(dialogue.get("petition_key") or ""))
    _record_ally_petition_resolution(
        world,
        war_id=war_id,
        ally=ally,
        petition_type=ALLY_SETTLEMENT_PETITION_BARGAIN_HONOR,
        resolution="granted",
    )
    _log_ally_petition_event(world, "settlement_bargain_honored", dialogue)
    honored_line = _ally_petition_resolution_voice(
        ally,
        "honored",
        ally_nation=ally,
        claim_region=claim_region,
    )
    if settlement_dialogue is None:
        result = _stage_granted_terms_from_draft(
            world,
            action=ALLY_SETTLEMENT_PETITION_HONOR_ACTION,
            war_id=war_id,
            new_terms=new_terms,
            message=(
                f"The pledge on {claim_region} stands in the draft, Sire. "
                f"{honored_line}"
            ),
        )
    else:
        voice_beats = [{
            "kind": "ally_petition_honored",
            "speaker": resolve_named_diplomat("envoy", ally, world),
            "nation": ally,
            "line": honored_line,
        }]
        from backend.game_logic.settlement_staging import (
            _restage_settlement_after_redraw,
        )

        result = _restage_settlement_after_redraw(
            world,
            settlement_dialogue,
            action=ALLY_SETTLEMENT_PETITION_HONOR_ACTION,
            new_terms=new_terms,
            new_covered=covered,
            message=(
                f"The pledge on {claim_region} stands in the draft, Sire."
            ),
            extra={"authoring_voice_beats": voice_beats},
        )
    result["bargain_honored"] = {
        "ally_nation": ally,
        "bargain_id": bargain_id,
        "claim_region": claim_region,
        "case": case,
    }
    return result


def handle_ally_settlement_petition_action(
    world: Any,
    *,
    action: str,
    dialogue: Mapping[str, Any],
) -> Dict[str, Any]:
    if action == ALLY_SETTLEMENT_PETITION_GRANT_ACTION:
        return _handle_grant_ally_petition(world, dialogue)
    if action == ALLY_SETTLEMENT_PETITION_DECLINE_ACTION:
        return _handle_decline_ally_petition(world, dialogue)
    if action == ALLY_SETTLEMENT_PETITION_HONOR_ACTION:
        return _handle_honor_bargain_in_settlement(world, dialogue)
    if action != ALLY_SETTLEMENT_PETITION_ACK_ACTION:
        return {
            "success": False,
            "message": f"Unknown ally petition action: {action}",
        }
    petition_key = str(dialogue.get("petition_key") or "")
    removed = _remove_ally_petition_dialogue(world, petition_key)
    return {
        "success": True,
        "message": "The allied petition has been recorded.",
        "mutated": False,
        "removed_dialogues": int(removed),
        "pending_envoy_count": _pending_envoy_count(world),
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


def _derive_status_quo_lines(world: Any, war: Any) -> List[str]:
    """W6-10 (E-CA-5): who keeps what, derived from current controller vs
    `nation_starting_regions` across the war's opposing participants.
    One clause per occupier holding enemy homeland soil."""
    if not isinstance(war, Mapping):
        return []
    side_by_nation = war.get("side_by_nation") or {}
    participants = list(side_by_nation)
    lines: List[str] = []
    for occupier in participants:
        occupier_side = side_by_nation.get(occupier)
        occupier_regions = world.get_nation_regions(occupier)
        held: List[str] = []
        for victim in participants:
            if victim == occupier:
                continue
            if side_by_nation.get(victim) == occupier_side:
                continue
            victim_home = set(
                world.nation_starting_regions.get(victim, []) or [])
            held.extend(r for r in occupier_regions if r in victim_home)
        if held:
            lines.append(f"{occupier} retains {', '.join(sorted(held))}")
    return lines


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

    # ES-7 second pass (§0.6.8 item 3): an incoming offer demanding a
    # province that sustains a PLAYER marshal's estate says so — accepting
    # it is a foresighted choice, never a silent strip. Covers both the
    # singular `region` and plural `regions` clause shapes (review fix).
    from backend.game_logic.dotation import estate_cession_warning
    _estate_warned = set()
    from backend.game_logic.settlement_scoring import cession_shaped_regions
    for term in settlement_terms:
        # NA-6c: carves strip estates too, and their soil rides `provinces`.
        for _raw_name in cession_shaped_regions(term):
            _region_name = str(_raw_name or "")
            if not _region_name or _region_name in _estate_warned:
                continue
            _estate_warned.add(_region_name)
            _estate_text = estate_cession_warning(world, _region_name)
            if _estate_text:
                terms_summary.append("WARNING: " + _estate_text)

    # W6-10 (E-CA-5) — territorial honesty: a peace that freezes the lines
    # must say WHO KEEPS WHAT. When any war participant occupies an
    # opposing participant's homeland soil, the summary appends the
    # derived status-quo line ("Status quo: Britain retains Flanders,
    # Amsterdam"). Pure display — the ratification math is untouched.
    # GR8: cached get_nation_regions x homeland sets, never a region
    # scan; diplomacy has no fog (project rule).
    status_quo = _derive_status_quo_lines(world, war)
    if status_quo:
        terms_summary.append("Status quo: " + "; ".join(status_quo) + ".")

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
                # GT-Slice-4 retired the freeform editor; the counter route
                # is the guided per-court table (LEGF-3 copy retarget).
                "Lay the offered terms on our own table, court by court, "
                "and answer with a counter draft."
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

    payload = {
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
    # W6-0 (BUG-CA-7): popups regenerated from a mounted dialogue carry the
    # dialogue's identity so the client answers the offer it actually saw.
    if offer.get("dialogue_id") is not None:
        payload["dialogue_id"] = offer["dialogue_id"]
    return payload


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
        # Gate-4 1805 smoke (E-3): dialogue-choice resolution reads TOP-LEVEL
        # `options` (diplomatic_executor `options = dialogue.get("options")`),
        # but the producer entry carries none — the popup contract's actions
        # lived only inside `popup_payload`, so accept / request-revision /
        # reject could NEVER resolve (every click fell to the unknown-choice
        # refusal and the offer sat unanswerable in the mailbox). Promote the
        # popup's options onto the dialogue itself — the standard dialogue
        # contract every other family satisfies.
        popup = dialogue["popup_payload"]
        if isinstance(popup, dict) and not dialogue.get("war_label"):
            # E-5: the mailbox summary renders the humanized war label —
            # the producer entry itself never carried one.
            dialogue["war_label"] = str(popup.get("war_label") or "")
        if not dialogue.get("options") and isinstance(popup, dict):
            dialogue["options"] = [
                dict(opt) for opt in (popup.get("options") or [])
                if isinstance(opt, dict)
            ]
            dialogue["available_action_ids"] = list(
                popup.get("available_action_ids") or []
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
        # next AI tick. Draft state lives in the scoped
        # `pending_settlement_drafts_by_key` store from `stage_settlement_confirm`.
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
        # G4F smoke follow-up: prefer the label stamped at ratification —
        # the settled war is archived by the time the income phase pays,
        # so the live lookup below would fall back to the raw war_id
        # ("the settlement of war_1" reached the morning dispatch).
        stored = str(entry.get("war_label") or "")
        if stored:
            return stored
        wid = str(entry.get("war_id") or "")
        if not wid:
            return "the settlement"
        instance = (getattr(world, "war_instances", {}) or {}).get(wid) or {}
        attackers = list(instance.get("attackers") or [])
        defenders = list(instance.get("defenders") or [])
        if attackers and defenders:
            return f"{attackers[0]} vs {defenders[0]}"
        return wid

    def _log_campaign(event_type: str, fields: Dict[str, Any]) -> None:
        # G4F smoke follow-up: payments fired in the morning dispatch but
        # vanished from the campaign log history — mirror each event into
        # `world.event_log` for the fog-filtered log surface.
        log = getattr(world, "log_event", None)
        if callable(log):
            log({"type": event_type, **fields})

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
            _log_campaign("settlement_recurring_gold_cancelled", {
                "from_nation": payer,
                "to_nation": recipient,
                "war_label": _war_label_for(entry),
                "reason": reason,
            })
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
            _log_campaign("settlement_recurring_gold_cancelled", {
                "from_nation": payer,
                "to_nation": recipient,
                "war_label": _war_label_for(entry),
                "reason": reason,
            })
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
            _log_campaign("settlement_recurring_gold_cancelled", {
                "from_nation": payer,
                "to_nation": recipient,
                "war_label": _war_label_for(entry),
                "reason": reason,
            })
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
            _log_campaign("settlement_recurring_gold_cancelled", {
                "from_nation": payer,
                "to_nation": recipient,
                "war_label": _war_label_for(entry),
                "reason": reason,
            })
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
            _log_campaign("settlement_recurring_gold_partial", {
                "from_nation": payer,
                "to_nation": recipient,
                "amount_paid": int(transfer),
                "amount_due": int(amount),
                "war_label": _war_label_for(entry),
            })
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
            _log_campaign("settlement_recurring_gold_paid", {
                "from_nation": payer,
                "to_nation": recipient,
                "amount_paid": int(transfer),
                "turns_remaining": int(turns_remaining),
                "war_label": _war_label_for(entry),
            })

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
            _log_campaign("settlement_recurring_gold_completed", {
                "from_nation": payer,
                "to_nation": recipient,
                "total_amount": int(total_amount),
                "war_label": _war_label_for(entry),
            })
            # Drop the record on natural completion.
            continue

        survivors.append(record)

    setattr(world, "recurring_settlement_payments", survivors)
    return events


# Import here to avoid a circular import on module load; the dispatch
# helper is a leaf utility.
from backend.game_logic.dispatch import queue_dispatch_event  # noqa: E402
