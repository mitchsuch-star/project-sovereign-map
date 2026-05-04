"""D1/D2 settlement reaction routing.

Wired from ``ratify_settlement_confirm`` AFTER cache invalidation but
BEFORE the dialogue is popped (see spec §11 line 1239). This module is
the post-ratification orchestrator that turns a successful C2 mutation
into the per-side reaction effects:

- Proposer-side ally reactions (`settlement_shut_out` grievance flag,
  `they_chose_us` + `settlement_gratitude` memory, WB-B bargain breach
  for active French claims awarded to a different beneficiary).
- Enemy-side reactions (`sold_out_by_war_leader` memory + relation
  deltas vs. France and the leader, per spec §14.6 Tilsit threshold).
- Europe-at-large beats: `settlement_summary` event + capped dispatch
  (4-beat primary cap per spec §11.6 line 1279) plus a
  `settlement_digest` rollup line for the overflow.
- Cross-war reaction scan bounded by the affected-nation set per spec
  §11.5 line 1241; iterates only `world.get_war_instances_by_participant(...)`
  for each affected nation, never the full `world.war_instances` table.

The module also owns the `settlement_memories` data field lifecycle:
``_add_settlement_memory`` writes per-pair records, and
``prune_expired_settlement_memories`` clears expired transient records
on each `world.advance_turn`. A small acceptance helper
``settlement_gratitude_mod`` is exposed for diplomacy.py to add to
deep-treaty / war-entry / bargain-ally-entry proposals per spec §14.3.

Deferred to E1 presentation: rich Talleyrand voice copy, settlement
review payload, named-diplomat acceptance lines, and ledger surfacing.
This slice produces the structured records and the dispatch event
families; the presentation surface consumes them.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Tuple


# Spec §14.3 line 1478 — gratitude memory window.
SETTLEMENT_GRATITUDE_TURNS = 10
# Spec §14.6 line 1524 — sold-out memory window.
SOLD_OUT_BY_LEADER_TURNS = 10
# Spec §14.3 line 1482 — gratitude acceptance bonus.
SETTLEMENT_GRATITUDE_MOD = 5
# Spec §11.6 line 1279 — settlement dispatch primary-beat cap.
SETTLEMENT_DISPATCH_PRIMARY_CAP = 4
# Spec §13.4 / §14.5 / §14.6 — relation deltas (single source).
RELATION_GRATITUDE_SEAT = 10
RELATION_GRATITUDE_CONSULT = 5
RELATION_SHUT_OUT_MINOR_HIT = -7
RELATION_SHUT_OUT_MAJOR_HIT = -18
RELATION_ZERO_MATERIAL_MAJOR_HIT = -7
RELATION_SOLD_OUT_VS_FRANCE = -15
RELATION_SOLD_OUT_VS_LEADER = -22

# Spec §14.6 line 1511 Tilsit threshold — material-loss families that
# trigger `sold_out_by_war_leader`. Mapped from settlement term type or
# `applied_clause["type"]`.
_MATERIAL_LOSS_TYPES: frozenset = frozenset(
    {
        "territory_cede",
        "vassalage",
        "subjugation",
        "forced_alliance",
        "liberation",
        "continental_system_join",
    }
)

# Cross-war secondary-scan cap per spec §11.5 line 1243 ("at most 3" cap
# applies only to secondary local-balance scans whose sole connection is
# adjacency / sphere / `rival_strengthened`).
CROSS_WAR_SECONDARY_SCAN_CAP = 3


# ---------------------------------------------------------------------------
# Settlement memory storage
# ---------------------------------------------------------------------------


def _memory_key(actor: str, subject: str) -> str:
    """Deterministic actor->subject pair key.

    Memories are *directional* (gratitude France->Prussia is not the
    same as France being grateful to Prussia from Prussia's side), so we
    do NOT sort the pair. Use as `f"{actor}|{subject}"`.
    """
    return f"{actor}|{subject}"


def _ensure_memory_store(world: Any) -> Dict[str, List[Dict[str, Any]]]:
    store = getattr(world, "settlement_memories", None)
    if store is None:
        store = {}
        world.settlement_memories = store
    return store


def _add_settlement_memory(
    world: Any,
    *,
    actor: str,
    subject: str,
    memory_type: str,
    episode_id: str,
    payload: Mapping[str, Any],
    expires_in: Optional[int] = None,
) -> Dict[str, Any]:
    """Append (or refresh) a settlement memory for the actor->subject pair.

    Refresh semantics per spec §14.3 line 1480: a subsequent rewarded
    settlement REFRESHES the expiry of an existing same-type memory; it
    does not stack. Same applies to `sold_out_by_war_leader` so a second
    burdening pass extends the posture window without doubling its
    severity.

    `expires_in=None` writes a durable record (`settlement_context`,
    `they_chose_us`) — these survive turn pruning.
    """
    if not actor or not subject:
        return {}
    current_turn = int(getattr(world, "current_turn", 0) or 0)
    expires_on_turn: Optional[int] = (
        None if expires_in is None else current_turn + int(expires_in)
    )
    store = _ensure_memory_store(world)
    key = _memory_key(actor, subject)
    records = list(store.get(key) or [])

    refreshable = ("settlement_gratitude", "sold_out_by_war_leader")
    if memory_type in refreshable:
        for existing in records:
            if existing.get("memory_type") == memory_type:
                existing["episode_id"] = str(episode_id)
                existing["turn"] = current_turn
                existing["expires_on_turn"] = expires_on_turn
                existing["payload"] = dict(payload or {})
                store[key] = records
                world.settlement_memories = store
                return existing

    record = {
        "actor": str(actor),
        "subject": str(subject),
        "memory_type": str(memory_type),
        "episode_id": str(episode_id),
        "turn": current_turn,
        "expires_on_turn": expires_on_turn,
        "payload": dict(payload or {}),
    }
    records.append(record)
    store[key] = records
    world.settlement_memories = store
    return record


def get_settlement_memories(
    world: Any,
    *,
    actor: Optional[str] = None,
    subject: Optional[str] = None,
    memory_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return memories filtered by actor/subject/memory_type.

    All filters are optional. Caller must not mutate returned dicts in
    place — use ``_add_settlement_memory`` to refresh.
    """
    store = getattr(world, "settlement_memories", None) or {}
    out: List[Dict[str, Any]] = []
    if actor and subject:
        records = store.get(_memory_key(actor, subject)) or []
        for record in records:
            if memory_type and record.get("memory_type") != memory_type:
                continue
            out.append(dict(record))
        return out
    for key, records in store.items():
        for record in records or []:
            if actor and record.get("actor") != actor:
                continue
            if subject and record.get("subject") != subject:
                continue
            if memory_type and record.get("memory_type") != memory_type:
                continue
            out.append(dict(record))
    return out


def prune_expired_settlement_memories(world: Any) -> int:
    """Drop transient memories whose `expires_on_turn` is past current turn.

    Called at `world.advance_turn` after diplomacy processing. Returns
    the number of pruned records; durable records (`expires_on_turn` is
    None) are never pruned here.
    """
    store = getattr(world, "settlement_memories", None) or {}
    if not store:
        return 0
    current_turn = int(getattr(world, "current_turn", 0) or 0)
    pruned_count = 0
    for key in list(store.keys()):
        records = store.get(key) or []
        kept: List[Dict[str, Any]] = []
        for record in records:
            expires_on_turn = record.get("expires_on_turn")
            if expires_on_turn is not None and int(expires_on_turn) <= current_turn:
                pruned_count += 1
                continue
            kept.append(record)
        if kept:
            store[key] = kept
        else:
            store.pop(key, None)
    return pruned_count


# ---------------------------------------------------------------------------
# Acceptance hook (spec §14.3 line 1482)
# ---------------------------------------------------------------------------


_GRATITUDE_HOOK_TREATY_TYPES: frozenset = frozenset(
    {"DEFENSIVE_ALLIANCE", "ALLIANCE", "war_entry", "war_bargain", "ally_entry"}
)


def settlement_gratitude_mod(
    world: Any, asker: str, target: str, proposal_type: str,
) -> int:
    """Acceptance bonus from an active `settlement_gratitude` memory.

    Returns ``+5`` when the asker has rewarded the target through a
    settlement (memory `settlement_gratitude` exists with the asker as
    actor and the target as subject) AND the proposal is in the
    treaty/war-entry/bargain-ally-entry families per spec §14.3 line
    1482. Returns ``0`` otherwise. Single-component upside; spec line
    1482 says it stays outside the political-subtotal clamp.
    """
    if proposal_type not in _GRATITUDE_HOOK_TREATY_TYPES:
        return 0
    current_turn = int(getattr(world, "current_turn", 0) or 0)
    matches = get_settlement_memories(
        world, actor=asker, subject=target, memory_type="settlement_gratitude",
    )
    for memory in matches:
        expires_on_turn = memory.get("expires_on_turn")
        if expires_on_turn is None or int(expires_on_turn) > current_turn:
            return SETTLEMENT_GRATITUDE_MOD
    return 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _other_side(side: str) -> str:
    return "defenders" if side == "attackers" else "attackers"


def _side_leader(war_instance: Mapping[str, Any], side: str) -> Optional[str]:
    if side == "attackers":
        return war_instance.get("attacker_leader")
    if side == "defenders":
        return war_instance.get("defender_leader")
    return None


def _participants_on_side(
    war_instance: Mapping[str, Any], side: str,
) -> List[str]:
    return list(war_instance.get(side) or [])


def _term_burdens_participant(
    term: Mapping[str, Any], participant: str,
) -> Tuple[bool, str]:
    """Whether a settlement term materially burdens this participant.

    Returns `(is_material_loss, reason)`. Reason is the spec §14.6 line
    1511 family that triggers `sold_out_by_war_leader`.
    """
    ttype = term.get("type")
    if ttype not in _MATERIAL_LOSS_TYPES:
        return False, ""
    from_nation = str(term.get("from") or "")
    if ttype == "territory_cede" and from_nation == participant:
        return True, "territory_loss"
    if ttype in ("vassalage", "subjugation") and from_nation == participant:
        return True, "vassalage_imposed"
    if ttype == "forced_alliance" and from_nation == participant:
        return True, "forced_alliance"
    if ttype == "liberation":
        lord = str(term.get("lord_nation") or term.get("to") or "")
        if lord == participant:
            return True, "subject_liberated"
    if ttype == "continental_system_join" and from_nation == participant:
        return True, "forced_continental_system"
    return False, ""


def _sum_severity_score(
    settlement_terms: Iterable[Mapping[str, Any]], participant: str,
) -> Tuple[int, List[str]]:
    """Severity score + reason list for `sold_out_by_war_leader`.

    Per spec §14.6 line 1522 the relation toward France ranges `-10`
    to `-25` and toward the leader `-15` to `-30` depending on
    severity. This helper folds the burden families into a [0, 4]
    score: `0` no burden, `4` heavy multi-clause burden.
    """
    score = 0
    reasons: List[str] = []
    for term in settlement_terms or []:
        burdened, reason = _term_burdens_participant(term, participant)
        if not burdened:
            continue
        reasons.append(reason)
        if reason == "territory_loss":
            score += 1
        elif reason in ("vassalage_imposed", "subject_liberated"):
            score += 3
        elif reason == "forced_alliance":
            score += 2
        elif reason == "forced_continental_system":
            score += 1
    return min(4, score), reasons


def _gradient_relation(
    base_min: int, base_max: int, severity_score: int,
) -> int:
    """Clamp severity_score [0..4] to a relation delta `[base_max..base_min]`.

    Both bounds are negative; `base_max` is the *less harsh* (closer to
    0) bound used at severity 1, `base_min` is the deeper hit at
    severity 4. Severity 0 returns 0.
    """
    if severity_score <= 0:
        return 0
    if severity_score >= 4:
        return base_min
    span = base_min - base_max  # both negative; span is more negative
    step = span / 3.0
    return int(round(base_max + step * (severity_score - 1)))


def _is_named_beneficiary(
    settlement_terms: Iterable[Mapping[str, Any]], nation: str,
) -> Tuple[bool, List[str]]:
    """Whether the nation is a named beneficiary on any term.

    Returns `(is_beneficiary, region_list)`. Region list is empty for
    non-territorial beneficiary entries.
    """
    regions: List[str] = []
    matched = False
    for term in settlement_terms or []:
        if term.get("beneficiary") == nation or term.get("to") == nation:
            matched = True
            for region in term.get("regions") or []:
                regions.append(str(region))
    return matched, regions


def _classify_proposer_ally_standing(
    world: Any, war_id: str, proposer_side: str, ally: str,
    settlement_terms: Iterable[Mapping[str, Any]],
) -> str:
    """Wrap `standing_for_participant` with settlement-term inputs.

    Pure pass-through to `war_contribution.standing_for_participant`,
    seeded with the named-beneficiary boolean drawn from the locked
    settlement package per Slice D plan ("Slice D wires the same
    inputs from confirmed settlement reactions").
    """
    is_beneficiary, _ = _is_named_beneficiary(settlement_terms, ally)
    try:
        from backend.game_logic.war_contribution import standing_for_participant

        return standing_for_participant(
            world,
            war_id,
            ally,
            side=proposer_side,
            is_named_beneficiary=is_beneficiary,
        )
    except Exception:
        return "no_standing"


# ---------------------------------------------------------------------------
# Affected-nation set per spec §11.5 line 1243
# ---------------------------------------------------------------------------


def _compute_affected_nations(
    settlement_terms: Iterable[Mapping[str, Any]],
    applied_clauses: Iterable[Mapping[str, Any]],
    resolved_pairs: Iterable[Mapping[str, Any]],
    covered_enemy_participants: Iterable[str],
    *,
    proposer_side_members: Iterable[str],
) -> Set[str]:
    """Build the affected-nation set for cross-war reactions.

    Per spec §11.5 line 1243 the set is bounded by:
    - term payers (`from`)
    - beneficiaries (`to` / `beneficiary` / `liberator`)
    - resolved-pair members
    - covered enemy participants
    """
    affected: Set[str] = set()
    for term in list(settlement_terms or []) + list(applied_clauses or []):
        if not isinstance(term, Mapping):
            continue
        for field in ("from", "to", "beneficiary", "liberator"):
            value = term.get(field)
            if isinstance(value, str) and value:
                affected.add(value)
        # liberation terms also use vassal_nation / lord_nation
        for field in ("vassal_nation", "lord_nation", "liberator_nation"):
            value = term.get(field)
            if isinstance(value, str) and value:
                affected.add(value)
    for pair in resolved_pairs or []:
        if not isinstance(pair, Mapping):
            continue
        for key in ("proposer_member", "covered_enemy"):
            value = pair.get(key)
            if isinstance(value, str) and value:
                affected.add(value)
    for nation in covered_enemy_participants or []:
        if isinstance(nation, str) and nation:
            affected.add(nation)
    return affected


# ---------------------------------------------------------------------------
# Proposer-side reactions (spec §14.1 / §14.3)
# ---------------------------------------------------------------------------


def _evaluate_proposer_side_reactions(
    world: Any,
    *,
    war_id: str,
    proposer_side: str,
    war_instance: Mapping[str, Any],
    settlement_terms: List[Mapping[str, Any]],
    applied_clauses: List[Mapping[str, Any]],
    episode_id: str,
) -> List[Dict[str, Any]]:
    from backend.game_logic.diplomacy import _add_grievance_flag

    reactions: List[Dict[str, Any]] = []
    player_nation = str(getattr(world, "player_nation", "France"))
    proposer_members = _participants_on_side(war_instance, proposer_side)
    proposer_leader = _side_leader(war_instance, proposer_side) or player_nation

    # France is the actor on settlement memories. If the proposer leader
    # is a non-player nation, settlement memories still attribute to the
    # proposer leader (the actor that ratified the package).
    actor = proposer_leader

    for ally in proposer_members:
        if ally == actor:
            continue
        standing = _classify_proposer_ally_standing(
            world, war_id, proposer_side, ally, settlement_terms,
        )
        if standing == "no_standing":
            # Spec §14.4: minor / no-standing participants only react when
            # survival, capital, promise, or territory directly named.
            continue
        is_beneficiary, awarded_regions = _is_named_beneficiary(
            settlement_terms, ally,
        )
        tier_getter = getattr(world, "get_power_tier", None)
        power_tier = tier_getter(ally) if callable(tier_getter) else "secondary"
        power_tier = power_tier or "secondary"

        if is_beneficiary:
            # Spec §14.3 — `they_chose_us` durable + `settlement_gratitude`
            # transient (only when material_contribution_points > 0; spec
            # line 1478).
            relation_delta = (
                RELATION_GRATITUDE_SEAT if standing == "seat"
                else RELATION_GRATITUDE_CONSULT
            )
            if hasattr(world, "modify_nation_relation"):
                world.modify_nation_relation(actor, ally, relation_delta)
            _add_settlement_memory(
                world,
                actor=actor,
                subject=ally,
                memory_type="they_chose_us",
                episode_id=episode_id,
                payload={
                    "war_id": war_id,
                    "standing_level": standing,
                    "awarded_regions": awarded_regions,
                    "relation_delta": relation_delta,
                },
                expires_in=None,
            )
            material_points = 0
            try:
                from backend.game_logic.war_contribution import (
                    current_episode_material_total,
                )
                material_points = int(
                    current_episode_material_total(world, war_id, ally) or 0
                )
            except Exception:
                material_points = 0
            if material_points > 0:
                _add_settlement_memory(
                    world,
                    actor=actor,
                    subject=ally,
                    memory_type="settlement_gratitude",
                    episode_id=episode_id,
                    payload={
                        "war_id": war_id,
                        "standing_level": standing,
                        "awarded_regions": awarded_regions,
                        "material_contribution_points": material_points,
                    },
                    expires_in=SETTLEMENT_GRATITUDE_TURNS,
                )
            reactions.append({
                "kind": "ally_rewarded",
                "ally": ally,
                "standing_level": standing,
                "awarded_regions": awarded_regions,
                "relation_delta": relation_delta,
                "power_tier": power_tier,
                "material_points": material_points,
            })
            continue

        # Ally was NOT rewarded. Decide shut-out severity.
        # Spec §14.2 — minor shut-out vs major shut-out.
        # Material share gates major — read the bundled inputs.
        material_share = 0.0
        material_points = 0
        try:
            from backend.game_logic.war_contribution import (
                compute_standing_inputs,
                current_episode_material_total,
            )
            inputs = compute_standing_inputs(
                world, war_id, ally, side=proposer_side,
            )
            material_share = float(inputs.get("material_share", 0.0) or 0.0)
            material_points = int(
                current_episode_material_total(world, war_id, ally) or 0
            )
        except Exception:
            material_share = 0.0
            material_points = 0

        # Spec §14.2 line 1469: zero-material `major` with `seat`
        # standing reduces the relation hit and skips the grievance
        # flag entirely.
        zero_material_major = (
            power_tier == "major"
            and material_points == 0
            and standing == "seat"
        )

        is_major_shut_out = (
            standing == "seat" or material_share >= 0.20
        ) and not zero_material_major

        if zero_material_major:
            relation_hit = RELATION_ZERO_MATERIAL_MAJOR_HIT
            severity = "minor_shut_out_major_zero_material"
            grievance_flag_added = False
        elif is_major_shut_out:
            relation_hit = RELATION_SHUT_OUT_MAJOR_HIT
            severity = "major_shut_out"
            grievance_flag_added = True
        else:
            relation_hit = RELATION_SHUT_OUT_MINOR_HIT
            severity = "minor_shut_out"
            grievance_flag_added = False

        if hasattr(world, "modify_nation_relation"):
            world.modify_nation_relation(actor, ally, relation_hit)

        if grievance_flag_added:
            _add_grievance_flag(
                world,
                breaker=actor,
                victim=ally,
                grievance_type="settlement_shut_out",
                episode_id=episode_id,
                source_episode_type="settlement_reaction",
            )
        _add_settlement_memory(
            world,
            actor=actor,
            subject=ally,
            memory_type="settlement_shut_out" if grievance_flag_added
            else "settlement_context",
            episode_id=episode_id,
            payload={
                "war_id": war_id,
                "standing_level": standing,
                "material_share": material_share,
                "material_points": material_points,
                "severity": severity,
                "relation_delta": relation_hit,
                "power_tier": power_tier,
            },
            expires_in=None,
        )
        reactions.append({
            "kind": "ally_shut_out",
            "ally": ally,
            "standing_level": standing,
            "severity": severity,
            "relation_delta": relation_hit,
            "grievance_flag_added": grievance_flag_added,
            "material_share": material_share,
            "material_points": material_points,
            "power_tier": power_tier,
        })
    return reactions


# ---------------------------------------------------------------------------
# Enemy-side reactions (spec §14.6 — sold_out_by_war_leader)
# ---------------------------------------------------------------------------


def _evaluate_enemy_side_reactions(
    world: Any,
    *,
    war_id: str,
    accepting_side: str,
    war_instance: Mapping[str, Any],
    covered_enemy_participants: Iterable[str],
    settlement_terms: List[Mapping[str, Any]],
    episode_id: str,
) -> List[Dict[str, Any]]:
    reactions: List[Dict[str, Any]] = []
    enemy_leader = _side_leader(war_instance, accepting_side) or ""
    player_nation = str(getattr(world, "player_nation", "France"))

    for participant in covered_enemy_participants:
        if not participant or participant == enemy_leader:
            continue
        severity_score, reasons = _sum_severity_score(
            settlement_terms, participant,
        )
        if severity_score <= 0:
            continue
        # Spec §14.6 line 1522 — relation deltas, gradient by severity.
        delta_vs_proposer = _gradient_relation(
            -25, -10, severity_score,
        )
        delta_vs_leader = _gradient_relation(
            -30, -15, severity_score,
        )
        if hasattr(world, "modify_nation_relation"):
            world.modify_nation_relation(
                player_nation, participant, delta_vs_proposer,
            )
            if enemy_leader:
                world.modify_nation_relation(
                    enemy_leader, participant, delta_vs_leader,
                )
        if enemy_leader:
            _add_settlement_memory(
                world,
                actor=enemy_leader,
                subject=participant,
                memory_type="sold_out_by_war_leader",
                episode_id=episode_id,
                payload={
                    "war_id": war_id,
                    "leader": enemy_leader,
                    "burdens": reasons,
                    "severity_score": severity_score,
                    "relation_delta_vs_leader": delta_vs_leader,
                    "relation_delta_vs_proposer": delta_vs_proposer,
                },
                expires_in=SOLD_OUT_BY_LEADER_TURNS,
            )
        reactions.append({
            "kind": "enemy_sold_out",
            "burdened_participant": participant,
            "leader": enemy_leader,
            "burdens": reasons,
            "severity_score": severity_score,
            "relation_delta_vs_proposer": delta_vs_proposer,
            "relation_delta_vs_leader": delta_vs_leader,
        })
    return reactions


# ---------------------------------------------------------------------------
# WB-B bargain integration at settlement (spec §15)
# ---------------------------------------------------------------------------


def _evaluate_bargain_outcomes(
    world: Any,
    *,
    war_id: str,
    settlement_terms: List[Mapping[str, Any]],
    proposer_member_set: Set[str],
    episode_id: str,
) -> List[Dict[str, Any]]:
    """Detect WB claims awarded to a different beneficiary at settlement.

    Bargain *fulfillment* is auto-detected on the next per-turn
    `process_bargain_lifecycle` pass when France controls the claim
    region and co-belligerence holds — this slice does not duplicate
    that path. It DOES detect explicit breaches: an active French WB
    claim where the settlement awards the claim region to a different
    `beneficiary` (or `to`). That routes through the existing
    `breach_bargain` pipeline so WB-B grievance / reliability deltas
    apply.
    """
    out: List[Dict[str, Any]] = []
    try:
        from backend.game_logic.diplomacy import _get_live_bargains, breach_bargain
    except Exception:
        return out
    awarded_by_region: Dict[str, Mapping[str, Any]] = {}
    for term in settlement_terms or []:
        if term.get("type") != "territory_cede":
            continue
        for region in term.get("regions") or []:
            awarded_by_region[str(region)] = term
    if not awarded_by_region:
        return out
    for bargain in _get_live_bargains(world):
        if bargain.get("war_id") and str(bargain.get("war_id")) != war_id:
            continue
        promiser = str(bargain.get("promiser") or "")
        beneficiary = str(bargain.get("beneficiary") or "")
        if promiser != "France":
            continue
        claim_region = str(
            (bargain.get("claim_term") or {}).get("claim_region") or ""
        )
        if not claim_region or claim_region not in awarded_by_region:
            continue
        award = awarded_by_region[claim_region]
        recipient = str(award.get("beneficiary") or award.get("to") or "")
        if not recipient or recipient == beneficiary or recipient == promiser:
            # Awarded to the bargain beneficiary or to France (the
            # promiser): not a breach. Lifecycle pass handles fulfillment.
            continue
        breach_event = breach_bargain(
            world, bargain, "settlement_awarded_to_other",
            episode_id=episode_id,
        )
        out.append({
            "kind": "bargain_breach_at_settlement",
            "bargain_id": bargain.get("id"),
            "promiser": promiser,
            "beneficiary": beneficiary,
            "claim_region": claim_region,
            "recipient": recipient,
            "event_emitted": bool(breach_event),
        })
    return out


# ---------------------------------------------------------------------------
# Cross-war reactions (spec §11.5 / §14.4)
# ---------------------------------------------------------------------------


def _scan_cross_war_reactions(
    world: Any,
    *,
    own_war_id: str,
    affected_nations: Set[str],
    settlement_terms: List[Mapping[str, Any]],
    episode_id: str,
    proposer_leader: str,
) -> List[Dict[str, Any]]:
    """Bounded cross-war scan per spec §11.5 line 1243.

    For each nation in `affected_nations`, look up its active wars
    through ``world.get_war_instances_by_participant(nation)`` (the
    only allowed seam — never iterate ``world.war_instances`` blind).
    For each such war, if any settlement beneficiary is on the
    OPPOSITE side from the affected nation in that war, the affected
    nation receives a ``rival_strengthened`` grievance flag against
    the proposer leader (the settlement actor) plus a durable
    ``settlement_context`` memory recording the cross-war context.

    Directly affected wars (nation is a payer / beneficiary / WB
    party / capital target on a settlement term) are mandatory and
    have no cap. The secondary 3-war cap
    (``CROSS_WAR_SECONDARY_SCAN_CAP``) applies only to scans whose
    SOLE connection is adjacency / sphere / `rival_strengthened`
    heuristics — currently no such heuristics fire from this module,
    so the cap is effectively reserved for future expansion.
    """
    from backend.game_logic.diplomacy import _add_grievance_flag

    out: List[Dict[str, Any]] = []
    if not affected_nations or not proposer_leader:
        return out
    beneficiaries: Set[str] = set()
    payers: Set[str] = set()
    for term in settlement_terms or []:
        if not isinstance(term, Mapping):
            continue
        from_nation = term.get("from")
        if isinstance(from_nation, str) and from_nation:
            payers.add(from_nation)
        for field in ("to", "beneficiary"):
            value = term.get(field)
            if isinstance(value, str) and value:
                beneficiaries.add(value)
    if not beneficiaries:
        return out
    seen_pairs: Set[Tuple[str, str, str]] = set()
    index_getter = getattr(world, "get_war_instances_by_participant", None)
    if not callable(index_getter):
        return out
    for nation in sorted(affected_nations):
        if nation == proposer_leader or nation in beneficiaries:
            # The proposer leader and direct beneficiaries do not
            # grieve about strengthening themselves.
            continue
        active_war_ids = index_getter(nation) or []
        for other_war_id in active_war_ids:
            if str(other_war_id) == str(own_war_id):
                continue
            other_instance = (
                getattr(world, "war_instances", {}) or {}
            ).get(other_war_id)
            if not other_instance or other_instance.get("ended_turn") is not None:
                continue
            other_attackers = set(other_instance.get("attackers") or [])
            other_defenders = set(other_instance.get("defenders") or [])
            if nation in other_attackers:
                nation_side = "attackers"
                opposing = other_defenders
            elif nation in other_defenders:
                nation_side = "defenders"
                opposing = other_attackers
            else:
                continue
            strengthened_rivals = sorted(beneficiaries & opposing)
            if not strengthened_rivals:
                continue
            pair_key = (str(other_war_id), proposer_leader, nation)
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)
            _add_grievance_flag(
                world,
                breaker=proposer_leader,
                victim=nation,
                grievance_type="rival_strengthened",
                episode_id=episode_id,
                source_episode_type="settlement_reaction",
            )
            _add_settlement_memory(
                world,
                actor=proposer_leader,
                subject=nation,
                memory_type="settlement_context",
                episode_id=episode_id,
                payload={
                    "cross_war_id": other_war_id,
                    "settlement_war_id": own_war_id,
                    "rival_strengthened": strengthened_rivals,
                    "nation_side_in_cross_war": nation_side,
                    "payers": sorted(payers),
                },
                expires_in=None,
            )
            out.append({
                "kind": "cross_war_rival_strengthened",
                "cross_war_id": other_war_id,
                "breaker": proposer_leader,
                "victim": nation,
                "rival_strengthened": strengthened_rivals,
            })
    return out


# ---------------------------------------------------------------------------
# Dispatch / event emission
# ---------------------------------------------------------------------------


def _emit_settlement_summary_event(
    world: Any,
    *,
    war_id: str,
    proposer_side: str,
    accepting_side: str,
    proposer_members: List[str],
    accepting_members: List[str],
    covered_enemy_participants: List[str],
    applied_clauses: List[Mapping[str, Any]],
    participant_reactions: List[Mapping[str, Any]],
    war_ended: bool,
    balance_projection: Mapping[str, Any],
) -> Dict[str, Any]:
    """Emit `settlement_summary` to event_log + pending_dispatch.

    Per spec §11.6 line 1287 the event ships a structured payload
    (`participant_reactions` carries every reaction, the dispatch
    one-liner shows at most three). Route metadata names the
    settlement family per spec §11.6 line 1290.
    """
    from backend.game_logic.settlement_presentation import (
        SETTLEMENT_EVENT_FAMILY,
        SETTLEMENT_REVIEW_TARGET_ACTIVE,
        SETTLEMENT_REVIEW_TARGET_ARCHIVED,
    )
    turn = int(getattr(world, "current_turn", 0) or 0)
    terms_summary = [
        f"{c.get('type')}: {c.get('from','')}→{c.get('to','')}"
        for c in applied_clauses[:3]
    ]
    event = {
        "type": "settlement_summary",
        "turn": turn,
        "war_id": war_id,
        "covered_enemy_participants": list(covered_enemy_participants),
        "proposer_side": proposer_side,
        "accepting_side": accepting_side,
        "proposer_members": list(proposer_members),
        "accepting_members": list(accepting_members),
        "terms_summary": terms_summary,
        "applied_clauses": [dict(c) for c in applied_clauses],
        "participant_reactions": [dict(r) for r in participant_reactions],
        "war_ended": bool(war_ended),
        "balance_projection": dict(balance_projection or {}),
        "route": {
            "event_family": SETTLEMENT_EVENT_FAMILY,
            "review_target": (
                SETTLEMENT_REVIEW_TARGET_ARCHIVED
                if war_ended
                else SETTLEMENT_REVIEW_TARGET_ACTIVE
            ),
            "route_id": f"settlement_summary:{war_id}:{turn}",
        },
    }
    if hasattr(world, "log_event"):
        world.log_event(event)
    pending = getattr(world, "pending_dispatch_events", None)
    if pending is None:
        world.pending_dispatch_events = []
        pending = world.pending_dispatch_events
    pending.append(dict(event))
    _queue_settlement_notification(world, event)
    return event


def _notification_priority(priority_name: str):
    from backend.notifications import NotificationPriority

    name = str(priority_name or "").upper()
    if name == "CRITICAL":
        return NotificationPriority.CRITICAL
    if name == "HIGH":
        return NotificationPriority.HIGH
    return NotificationPriority.NORMAL


def _queue_settlement_notification(world: Any, event: Mapping[str, Any]) -> None:
    notifications = getattr(world, "notifications", None)
    if notifications is None or not hasattr(notifications, "add"):
        return
    from backend.game_logic.settlement_presentation import (
        compose_summary_oneliner,
        settlement_notification_meta,
    )
    from backend.notifications import create_notification

    meta = settlement_notification_meta(event)
    if meta.get("rail_spotlight") != "yes":
        return
    notifications.add(create_notification(
        str(meta.get("event_type", event.get("type", "settlement_summary"))),
        _notification_priority(str(meta.get("priority", "HIGH"))),
        str(meta.get("label", "Settlement Ratified")),
        compose_summary_oneliner(event, world=world),
        int(event.get("turn", 0) or 0),
        details=meta,
    ))


def _emit_settlement_digest_event(
    world: Any,
    *,
    war_id: str,
    war_ended: bool,
    proposer_members: List[str],
    accepting_members: List[str],
    covered_enemy_participants: List[str],
    hidden_reaction_count: int,
    top_reaction_types: List[str],
) -> Optional[Dict[str, Any]]:
    if hidden_reaction_count <= 0:
        return None
    from backend.game_logic.settlement_presentation import (
        SETTLEMENT_EVENT_FAMILY,
        SETTLEMENT_REVIEW_TARGET_ARCHIVED,
    )
    turn = int(getattr(world, "current_turn", 0) or 0)
    event = {
        "type": "settlement_digest",
        "turn": turn,
        "war_id": war_id,
        "proposer_members": list(proposer_members),
        "accepting_members": list(accepting_members),
        "covered_enemy_participants": list(covered_enemy_participants),
        "hidden_reaction_count": int(hidden_reaction_count),
        "top_reaction_types": list(top_reaction_types),
        "route": {
            "event_family": SETTLEMENT_EVENT_FAMILY,
            "review_target": SETTLEMENT_REVIEW_TARGET_ARCHIVED,
            "route_id": f"settlement_digest:{war_id}:{turn}",
        },
    }
    if hasattr(world, "log_event"):
        world.log_event(event)
    pending = getattr(world, "pending_dispatch_events", None)
    if pending is None:
        world.pending_dispatch_events = []
        pending = world.pending_dispatch_events
    pending.append(dict(event))
    return event


# ---------------------------------------------------------------------------
# Top-level orchestrator
# ---------------------------------------------------------------------------


def route_settlement_reactions(
    world: Any,
    *,
    war_id: str,
    proposer_side: str,
    accepting_side: str,
    covered_enemy_participants: List[str],
    settlement_terms: List[Mapping[str, Any]],
    resolved_pairs: List[Mapping[str, Any]],
    applied_clauses: List[Mapping[str, Any]],
    pre_cleanup_snapshots: List[Mapping[str, Any]],
    war_ended: bool,
    balance_projection: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """D1/D2 settlement / cross-war reaction routing.

    Called from `ratify_settlement_confirm` AFTER cache invalidation and
    BEFORE the dialogue is popped (spec §11 line 1239 ordering). Reads
    fresh `war_instances_by_participant` indexes, writes settlement
    memories + grievance flags, runs WB-B bargain breach detection,
    bounded cross-war scan, and emits `settlement_summary` /
    `settlement_digest`.
    """
    instance = (getattr(world, "war_instances", {}) or {}).get(war_id) or {}
    proposer_member_set = set(
        _participants_on_side(instance, proposer_side)
    )
    proposer_members = _participants_on_side(instance, proposer_side)
    accepting_members = _participants_on_side(instance, accepting_side)
    episode_id_alloc = None
    try:
        from backend.game_logic.diplomacy import _allocate_episode_id

        episode_id_alloc = _allocate_episode_id
    except Exception:
        episode_id_alloc = None
    episode_id = (
        episode_id_alloc(world, prefix="settlement")
        if callable(episode_id_alloc)
        else f"settlement_{int(getattr(world, 'current_turn', 0) or 0)}"
    )

    proposer_reactions = _evaluate_proposer_side_reactions(
        world,
        war_id=war_id,
        proposer_side=proposer_side,
        war_instance=instance,
        settlement_terms=list(settlement_terms or []),
        applied_clauses=list(applied_clauses or []),
        episode_id=episode_id,
    )
    enemy_reactions = _evaluate_enemy_side_reactions(
        world,
        war_id=war_id,
        accepting_side=accepting_side,
        war_instance=instance,
        covered_enemy_participants=list(covered_enemy_participants or []),
        settlement_terms=list(settlement_terms or []),
        episode_id=episode_id,
    )
    bargain_reactions = _evaluate_bargain_outcomes(
        world,
        war_id=war_id,
        settlement_terms=list(settlement_terms or []),
        proposer_member_set=proposer_member_set,
        episode_id=episode_id,
    )

    affected_nations = _compute_affected_nations(
        list(settlement_terms or []),
        list(applied_clauses or []),
        list(resolved_pairs or []),
        list(covered_enemy_participants or []),
        proposer_side_members=proposer_member_set,
    )
    proposer_leader = (
        _side_leader(instance, proposer_side)
        or str(getattr(world, "player_nation", "France"))
    )
    cross_war_reactions = _scan_cross_war_reactions(
        world,
        own_war_id=war_id,
        affected_nations=affected_nations,
        settlement_terms=list(settlement_terms or []),
        episode_id=episode_id,
        proposer_leader=proposer_leader,
    )

    all_reactions: List[Dict[str, Any]] = (
        list(proposer_reactions)
        + list(enemy_reactions)
        + list(bargain_reactions)
        + list(cross_war_reactions)
    )
    summary_event = _emit_settlement_summary_event(
        world,
        war_id=war_id,
        proposer_side=proposer_side,
        accepting_side=accepting_side,
        proposer_members=proposer_members,
        accepting_members=accepting_members,
        covered_enemy_participants=list(covered_enemy_participants or []),
        applied_clauses=list(applied_clauses or []),
        participant_reactions=all_reactions,
        war_ended=bool(war_ended),
        balance_projection=balance_projection or {},
    )
    digest_event: Optional[Dict[str, Any]] = None
    if len(all_reactions) > SETTLEMENT_DISPATCH_PRIMARY_CAP:
        # Top reaction types — preserve order of first appearance.
        seen_types: List[str] = []
        for r in all_reactions[SETTLEMENT_DISPATCH_PRIMARY_CAP:]:
            kind = r.get("kind", "")
            if kind and kind not in seen_types:
                seen_types.append(kind)
        digest_event = _emit_settlement_digest_event(
            world,
            war_id=war_id,
            war_ended=bool(war_ended),
            proposer_members=proposer_members,
            accepting_members=accepting_members,
            covered_enemy_participants=list(covered_enemy_participants or []),
            hidden_reaction_count=len(all_reactions)
            - SETTLEMENT_DISPATCH_PRIMARY_CAP,
            top_reaction_types=seen_types[:3],
        )

    return {
        "episode_id": episode_id,
        "proposer_side_reactions": proposer_reactions,
        "enemy_side_reactions": enemy_reactions,
        "bargain_reactions": bargain_reactions,
        "cross_war_reactions": cross_war_reactions,
        "affected_nations": sorted(affected_nations),
        "summary_event": summary_event,
        "digest_event": digest_event,
        "primary_beat_cap": SETTLEMENT_DISPATCH_PRIMARY_CAP,
    }
