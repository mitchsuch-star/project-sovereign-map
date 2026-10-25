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
from backend.errors import report


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
        # NA-6c: losing soil AND gaining a foreign client on your frontier
        # is as material as any cession — an ally sold out this way must
        # get its `sold_out_by_war_leader` reaction. (VS-5's
        # `vassal_transfer` was never added here; it is added alongside,
        # since losing a satellite to the enemy is the same category.)
        "create_client",
        "vassal_transfer",
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

# IQ-4 §7 R2 flip lever (September 14, 2026). The hook's treaty types are the
# diplomatic-STATE spelling ("ALLIANCE"), but `calculate_acceptance` passes
# `proposal.get("type")` — the PROPOSAL spelling, lowercase for the alliance
# family (`diplomacy._DEEP_TREATY_TYPES`; the typed and wizard paths both
# produce "alliance"). Reproduced: France with a live `settlement_gratitude`
# memory toward Prussia, a bare alliance offer scored the term 0, while the
# uppercase call the unit pins make scored 5 — the gratitude never reached
# a real alliance or defensive-alliance offer. The alliance family is now
# read in either case. False = the case-sensitive gate.
_GRATITUDE_ALLIANCE_FAMILY: frozenset = frozenset({"DEFENSIVE_ALLIANCE", "ALLIANCE"})


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
    if (str(proposal_type or "").upper() in _GRATITUDE_ALLIANCE_FAMILY):
        proposal_type = str(proposal_type).upper()
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
    # NA-6c: losing soil AND gaining a foreign client erected on it is at
    # least as material as a plain cession — it prices HARSHER in the
    # acceptance accumulator (0.45 vs 0.30), so generating LESS diplomatic
    # fallout than the milder clause was strictly backwards. Adding the
    # types to `_MATERIAL_LOSS_TYPES` alone was a no-op: that frozenset is
    # only the early-out gate above; this ladder is what returns a reason.
    if ttype == "create_client" and from_nation == participant:
        return True, "territory_loss"
    # VS-5's own gap, closed alongside: the lord that loses a satellite at
    # someone else's peace table is sold out exactly as a ceding court is.
    if ttype == "vassal_transfer" and from_nation == participant:
        return True, "subject_liberated"
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
            # S14E-X115 (S14f part 2): the table's canonical cession carries a
            # SINGULAR `region` (PC-X32's class) — reading only `regions`
            # left every table award unnamed ("her share") in the gratitude
            # record and the words that state it.
            single = str(term.get("region") or "")
            if single and single not in regions:
                regions.append(single)
    return matched, regions


def gratitude_delta(standing: str) -> int:
    """The relation a named proposer-side ally gives back (spec §14.3, the
    single source: a seat +10, a consult +5). `_reward_named_ally` applies
    it and the plan's `rewarded` figure (`proposer_ally_plan`) states it
    before the click, so the +10 shown is the +10 written (S14E-X51)."""
    return int(RELATION_GRATITUDE_SEAT if standing == "seat"
               else RELATION_GRATITUDE_CONSULT)


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
    except Exception as exc:
        report(exc, "settlement_reactions._classify_proposer_ally_standing: import backend.game_logic.war_contribution")
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
        # liberation terms also use vassal_nation / lord_nation (the liberator
        # is the `liberator` key, read above - S14E-X117 dropped the dead
        # `liberator_nation` read: no clause carries that key, only log events)
        for field in ("vassal_nation", "lord_nation"):
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


def _reward_named_ally(world: Any, *, actor: str, ally: str, standing: str,
                       war_id: str, awarded_regions: List[str], episode_id: str,
                       power_tier: str) -> Dict[str, Any]:
    """Spec §14.3 — a proposer-side ally NAMED in the instrument: `they_chose_us`
    durable + the relation + `settlement_gratitude` transient (only when
    material_contribution_points > 0; spec line 1478). ONE body for both
    roads (PC-F81, S13e part 4): the table's proposer-side pass and the
    bilateral ratifier's carried allies (`reward_named_carried_allies`)."""
    relation_delta = gratitude_delta(standing)
    if hasattr(world, "modify_nation_relation"):
        # S14E-X37: the reaction's write keeps a live mission's books.
        from backend.game_logic.diplomatic_dialogue import modify_relation_booked
        modify_relation_booked(world, actor, ally, relation_delta,
                               "settlement_gratitude", actor, ally)
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
    except Exception as exc:
        report(exc, "settlement_reactions._reward_named_ally: import backend.game_logic.war_contribution")
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
    return {
        "kind": "ally_rewarded",
        "ally": ally,
        "standing_level": standing,
        "awarded_regions": awarded_regions,
        "relation_delta": relation_delta,
        "power_tier": power_tier,
        "material_points": material_points,
    }


def carried_ally_standings(world: Any, war_id: str, side: str, allies: Iterable[str],
                           clauses: Iterable[Mapping[str, Any]]) -> Dict[str, str]:
    """PC-F81 (S13e part 4): the carried allies' standing read BEFORE their
    pairs close (the table's lesson, part 2: `cleanup_war_end` closes the
    contribution episode and the standing reads `no_standing` after)."""
    terms = [dict(c) for c in (clauses or []) if isinstance(c, Mapping)]
    return {str(a): _classify_proposer_ally_standing(world, war_id, side, str(a), terms)
            for a in (allies or []) if a}


def reward_named_carried_allies(world: Any, *, war_id: str, actor: str,
                                standings: Mapping[str, str],
                                applied_clauses: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """PC-F81's second road (S13e part 4, October 17, 2026): a carried ally
    the BILATERAL instrument names as beneficiary (F53's `to`, F70's hand-
    off — Tyrol to Bavaria) gets the gratitude pass the table gives it
    (`_reward_named_ally`): before, the ratifier transferred the province and
    nothing else — Bavaria named for Tyrol on the wizard's peace read 60 → 60
    where the table's read 60 → 60 + the gratitude. An ally carried in and
    named for nothing keeps PC-R1's ruling (carried, no fallout); a
    `no_standing` ally does not react (spec §14.4). Returns the reactions."""
    clauses = [dict(c) for c in (applied_clauses or []) if isinstance(c, Mapping)]
    if not clauses or not standings:
        return []
    named_allies = []
    for ally, standing in standings.items():
        if standing == "no_standing":
            continue
        named, regions = _is_named_beneficiary(clauses, ally)
        if named:
            named_allies.append((str(ally), str(standing), list(regions)))
    if not named_allies:
        return []
    episode_id = f"carried:{war_id}:{int(getattr(world, 'current_turn', 0) or 0)}"
    try:
        from backend.game_logic.diplomacy import _allocate_episode_id
        episode_id = str(_allocate_episode_id(world) or episode_id)
    except Exception as exc:
        report(exc, "settlement_reactions.reward_named_carried_allies: _allocate_episode_id")
    out: List[Dict[str, Any]] = []
    for ally, standing, regions in named_allies:
        tier_getter = getattr(world, "get_power_tier", None)
        power_tier = (tier_getter(ally) if callable(tier_getter) else "secondary") or "secondary"
        out.append(_reward_named_ally(
            world, actor=actor, ally=str(ally), standing=str(standing), war_id=war_id,
            awarded_regions=list(regions), episode_id=episode_id, power_tier=power_tier))
    return out


def carried_ally_readings(world: Any, war_id: str, side: str, allies: Iterable[str],
                          clauses: Iterable[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """S14E-10: the carried allies' full reading (standing, material share and
    points, tier) BEFORE their pairs close — `carried_ally_standings` is its
    standing column. The bilateral ratifier snapshots this; the bilateral
    words (`diplomacy.separate_peace_words`) read it live."""
    terms = [dict(c) for c in (clauses or []) if isinstance(c, Mapping)]
    return {str(a): proposer_ally_reading(world, war_id=war_id, proposer_side=side,
                                          ally=str(a), settlement_terms=terms)
            for a in (allies or []) if a}


def shut_out_carried_allies(world: Any, *, war_id: str, side: str, actor: str,
                            readings: Mapping[str, Mapping[str, Any]],
                            applied_clauses: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """S14E-D3's bilateral half (S14f part 1, October 24, 2026): the
    bilateral separate peace that carries an ally (PC-R1 ii: the leader's
    peace is common to its side) and names her for NOTHING runs the SAME
    shut-out reaction the table's ratification runs — the ratifier's own
    plan (`proposer_ally_plan`), the same -18 and durable `settlement_shut_out`
    grievance for an ally with standing and material in the war, the same -7
    for a lesser one, nothing for an ally with no standing (spec §14.4). Before
    this the same outcome cost nothing on the wizard's road and -18 plus a
    grievance at the table. Returns the `ally_shut_out` reaction records."""
    clauses = [dict(c) for c in (applied_clauses or []) if isinstance(c, Mapping)]
    plans = []
    for ally, reading in (readings or {}).items():
        plan = proposer_ally_plan(world, war_id=war_id, proposer_side=side, ally=str(ally),
                                  settlement_terms=clauses, reading=reading)
        if plan["kind"] == "shut_out":
            plans.append(plan)
    if not plans:
        return []
    episode_id = f"carried:{war_id}:{int(getattr(world, 'current_turn', 0) or 0)}"
    try:
        from backend.game_logic.diplomacy import _allocate_episode_id
        episode_id = str(_allocate_episode_id(world) or episode_id)
    except Exception as exc:
        report(exc, "settlement_reactions.shut_out_carried_allies: _allocate_episode_id")
    return [apply_shut_out_plan(world, actor=actor, plan=plan, war_id=war_id,
                                episode_id=episode_id) for plan in plans]


def _display_of(world: Any, nation: str) -> str:
    """The nation's player-facing name: its CURRENT (formed) name when the
    world is at hand, else the R7 rendering of the key."""
    if world is not None:
        try:
            from backend.game_logic.formations import formed_display_name
            return str(formed_display_name(world, nation))
        except Exception as exc:
            report(exc, "settlement_reactions._display_of: formed_display_name")
    from backend.display_names import display_nation
    return str(display_nation(nation))


def _ally_open_enemies(world: Any, war_id: str, proposer_side: str, ally: str,
                       covered: Iterable[str]) -> Tuple[bool, List[str]]:
    """(resolved, fights_on_against) for ONE proposer-side ally and the
    courts a table covers — read off the ratifier's OWN pair plan
    (`settlement_ratify.build_pair_ratification_plan`: every proposer-side
    member at WAR or ARMISTICE with a covered court settles with it), so the
    ally "the table resolves" is the ally whose pair the ratifier closes.
    `fights_on_against` is the ally's other live pairs in the war — the
    enemies the peace leaves her fighting. A read of the live instance:
    call it BEFORE the pairs close."""
    instance = (getattr(world, "war_instances", {}) or {}).get(war_id)
    if not isinstance(instance, Mapping):
        return True, []
    from backend.game_logic.settlement_ratify import build_pair_ratification_plan
    covered_set = {str(c) for c in (covered or []) if c}
    plan = build_pair_ratification_plan(
        world, instance, proposer_side=proposer_side, covered=covered_set,
        settlement_terms=[])
    if any(str(e.get("proposer_member") or "") == ally for e in plan):
        return True, []
    meta = instance.get("diplo_key_meta") or {}
    enemies: List[str] = []
    for pair in list(instance.get("active_diplo_keys") or []):
        names = str(pair).split("|")
        if len(names) != 2 or ally not in names:
            continue
        if (meta.get(pair) or {}).get("pair_status") not in ("war", "armistice"):
            continue
        other = names[1] if names[0] == ally else names[0]
        if other not in covered_set and other not in enemies:
            enemies.append(other)
    return False, sorted(enemies)


def table_resolves_ally(world: Any, war_id: str, ally: str,
                        settlement_terms: Iterable[Mapping[str, Any]],
                        covered: Iterable[str]) -> bool:
    """S14E-D8 (ruling recommended at DESIGN_REFINEMENT S14E-D8; built October
    25, 2026 — S14f part 2) — does the table END a war of this proposer-side
    ally? True when the ally has a live pair (war or armistice) with a covered
    court, the pair the ratifier closes. An ally whose war the table does not
    touch (Spain, at war with Britain, on an Austria-alone table) is NOT
    resolved: she "fights on alone", priced with no relation hit and no
    grievance — F81's teeth are for the ally whose war we ended for nothing.

    THE series seam for the D8 build: the attribution holds the ruling down
    with `--seam backend.game_logic.settlement_reactions:table_resolves_ally=
    lambda w, wid, a, t, c: True` (every ally reached, as shipped before).
    `proposer_ally_reading` looks it up late."""
    side = ((getattr(world, "war_instances", {}) or {}).get(war_id) or {}
            ).get("side_by_nation", {}).get(ally)
    if side not in ("attackers", "defenders"):
        return True
    return _ally_open_enemies(world, war_id, side, ally, covered)[0]


def proposer_ally_reading(
    world: Any, *, war_id: str, proposer_side: str, ally: str,
    settlement_terms: Iterable[Mapping[str, Any]],
    standing: Optional[str] = None,
    covered: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """S14E-10: the INPUTS of the proposer-side reaction for ONE ally, read
    together — its standing, its material share and points, its power tier —
    and read BEFORE the pairs close (PC-F81's lesson: `cleanup_war_end`
    closes the contribution episode, after which the standing reads
    `no_standing` and the share reads 0). The ratifier snapshots this before
    the transitions; the forecast reads it live — one reading, so the price
    shown before the click is the price applied after it.

    S14E-D8: with the table's `covered` courts the reading also says whether
    the table ENDS a war of this ally (`table_resolves`, through the seam
    `table_resolves_ally`) and, if not, the enemies she is left fighting
    (`fights_on_against`); without them the keys are absent and the plan
    reads the ally as before."""
    terms = [t for t in (settlement_terms or []) if isinstance(t, Mapping)]
    resolved = str(standing) if standing else _classify_proposer_ally_standing(
        world, war_id, proposer_side, ally, terms)
    material_share = 0.0
    material_points = 0
    try:
        from backend.game_logic.war_contribution import (
            compute_standing_inputs,
            current_episode_material_total,
        )
        inputs = compute_standing_inputs(world, war_id, ally, side=proposer_side)
        material_share = float(inputs.get("material_share", 0.0) or 0.0)
        material_points = int(current_episode_material_total(world, war_id, ally) or 0)
    except Exception as exc:
        report(exc, "settlement_reactions.proposer_ally_reading: import backend.game_logic.war_contribution")
        material_share = 0.0
        material_points = 0
    tier_getter = getattr(world, "get_power_tier", None)
    power_tier = (tier_getter(ally) if callable(tier_getter) else "secondary") or "secondary"
    reading: Dict[str, Any] = {
        "standing": resolved,
        "material_share": material_share,
        "material_points": material_points,
        "power_tier": str(power_tier),
    }
    covered_list = sorted({str(c) for c in covered if c}) if covered is not None else []
    if covered_list:
        # S14E-D8: the table's coverage is an INPUT of the reaction too —
        # does the table end a war of this ally, read before the pairs
        # close like the rest. No `covered` (the bilateral road, whose
        # carried allies are resolved by construction) = no gate; a table
        # that covers nobody ratifies nothing (`no_resolvable_pairs`).
        resolves = bool(table_resolves_ally(world, war_id, ally, terms, covered_list))
        reading["table_resolves"] = resolves
        reading["fights_on_against"] = ([] if resolves else
                                        _ally_open_enemies(world, war_id, proposer_side,
                                                           ally, covered_list)[1])
    return reading


def proposer_ally_plan(
    world: Any, *, war_id: str, proposer_side: str, ally: str,
    settlement_terms: Iterable[Mapping[str, Any]],
    reading: Optional[Mapping[str, Any]] = None,
    covered: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """S14E-10: THE predicate of the proposer-side reaction (spec §14.1-§14.4)
    — what a settlement does to ONE proposer-side ally. Pure: it reads, it
    writes nothing. The ratifier (`_evaluate_proposer_side_reactions`)
    applies exactly this plan, and the forecast
    (`forecast_proposer_side_reactions`) lists exactly this plan before the
    click, so "who is shut out" and "for how much" have one home.

    `kind`:
      * "none"     — no standing and nothing paid: spec §14.4, no reaction;
      * "rewarded" — named in the instrument: gratitude (`_reward_named_ally`);
        `relation_delta` is the gratitude it writes (S14E-X51, said first);
      * "fights_on" — S14E-D8: the table does NOT end a war of hers (her
        pair is with a court it does not cover; `reading["table_resolves"]`
        False, read before the pairs close): she fights on alone — NO
        relation hit, no grievance, `fights_on_against` the enemies she is
        left with. Not for an ally the instrument names or makes pay;
      * "shut_out" — not named: `severity`, `relation_delta` and
        `grievance_flag_added` as §14.2 reads them (a major shut-out is -18
        and the durable `settlement_shut_out` flag; a minor one -7; the
        zero-material major seat -7 without the flag; made to pay the
        enemy's compensation with nothing gained -18 and the flag).

    `covered` (the table's coverage) is read into the ally's reading when no
    `reading` is supplied; the ratifier's pre-cleanup reading carries it.
    """
    terms = [t for t in (settlement_terms or []) if isinstance(t, Mapping)]
    rd = dict(reading) if reading else proposer_ally_reading(
        world, war_id=war_id, proposer_side=proposer_side, ally=ally,
        settlement_terms=terms, covered=covered)
    standing = str(rd.get("standing") or "no_standing")
    power_tier = str(rd.get("power_tier") or "secondary")
    material_share = float(rd.get("material_share") or 0.0)
    material_points = int(rd.get("material_points") or 0)
    # PC-R7 (ii): a province of this ally PAYS the compensation (the
    # leader's article in the ally's coin — Würzburg at Pressburg).
    paid_regions = [str(t.get("region") or "") for t in terms
                    if t.get("type") == "territory_compensate"
                    and str(t.get("from") or "") == ally and not t.get("design")]
    plan: Dict[str, Any] = {
        "ally": ally,
        "standing_level": standing,
        "power_tier": power_tier,
        "material_share": material_share,
        "material_points": material_points,
        "paid_regions": list(paid_regions),
    }
    if standing == "no_standing" and not paid_regions:
        # Spec §14.4: minor / no-standing participants only react when
        # survival, capital, promise, or territory directly named.
        return dict(plan, kind="none")
    is_beneficiary, awarded_regions = _is_named_beneficiary(terms, ally)
    if is_beneficiary:
        return dict(plan, kind="rewarded", awarded_regions=list(awarded_regions),
                    relation_delta=gratitude_delta(standing))

    # S14E-D8: the ONE gate — an ally whose war the table does not end is not
    # shut out of a peace that never touched her war (an ally made to pay is
    # touched by the instrument itself, so she keeps her price).
    if not paid_regions and not rd.get("table_resolves", True):
        return dict(plan, kind="fights_on", relation_delta=0, grievance_flag_added=False,
                    fights_on_against=[str(n) for n in (rd.get("fights_on_against") or [])])

    # Ally was NOT rewarded. Decide shut-out severity.
    # Spec §14.2 — minor shut-out vs major shut-out.
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

    if paid_regions:
        # PC-R7 (ii): made to pay the enemy's compensation with nothing
        # gained by the same peace — the major shut-out, named. (Paid AND
        # rewarded — the Pressburg exchange — took the beneficiary arm.)
        relation_hit = RELATION_SHUT_OUT_MAJOR_HIT
        severity = "paid_for_the_peace"
        grievance_flag_added = True
    elif zero_material_major:
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
    return dict(plan, kind="shut_out", severity=severity,
                relation_delta=int(relation_hit),
                grievance_flag_added=bool(grievance_flag_added))


def shut_out_words(world: Any, plan: Mapping[str, Any]) -> str:
    """S14E-10: the price of being left out, STATED — one sentence from the
    plan the ratifier applies, so the forecast before the click, the chip,
    the dispatch and the archived review all say the same thing:

        "Spain is left out: -18 relation and a grievance; Make Amends
         (400g + 2 DP) clears it."

    A minor shut-out carries no grievance and no cure: "Holland is left out:
    -7 relation." The Make Amends price is `cabinet_rows`' own (the
    executor's), never a literal here."""
    ally = str(plan.get("ally") or plan.get("nation") or "")
    name = _display_of(world, ally)
    paid = [str(r) for r in (plan.get("paid_regions") or []) if r]
    lead = (f"{name} pays {', '.join(paid)} and is left out" if paid
            else f"{name} is left out")
    return (f"{lead}: {shut_out_price_words(plan)}"
            + alliance_clock_clause(world, ally, int(plan.get("relation_delta") or 0)))


def alliance_clock_clause(world: Any, ally: str, delta: int) -> str:
    """S14E-10's sweep: the −18 can take an ALLIANCE under the line it holds
    on and start the auto-downgrade clock (`check_auto_downgrade`; the
    warning S14E-11 gave its lever) — a consequence the price must state
    where the price is stated: " It takes the alliance under the 40 it holds
    on (40 → 22) — Reassure Ally in the Cabinet before it lapses." '' when
    the pair is not an alliance, or the hit leaves it on or above the line."""
    player = str(getattr(world, "player_nation", "France") or "France")
    if not ally or not hasattr(world, "get_diplomatic_state"):
        return ""
    if str(world.get_diplomatic_state(player, ally) or "") != "ALLIANCE":
        return ""
    from backend.game_logic.diplomacy import STATE_RELATION_THRESHOLDS
    line = int(STATE_RELATION_THRESHOLDS.get("ALLIANCE", 40))
    relations = getattr(world, "nation_relations", {}) or {}
    rel = int(relations.get(world._make_diplo_key(player, ally), 0) or 0)
    after = rel + int(delta)
    if rel < line or after >= line:
        return ""
    return (f" It takes the alliance under the {line} it holds on ({rel} → {after}) "
            f"— Reassure Ally in the Cabinet before it lapses.")


def shut_out_price_words(plan: Mapping[str, Any]) -> str:
    """The price half of `shut_out_words`: "-18 relation and a grievance;
    Make Amends (400g + 2 DP) clears it." (the grievance and its cure only
    where the plan adds a grievance) — the clause the bilateral road's
    carried-ally sentence reuses."""
    delta = int(plan.get("relation_delta") or 0)
    if plan.get("grievance_flag_added"):
        from backend.game_logic.cabinet_rows import AMENDS_GRIEVANCE, amends_price_words
        return (f"{delta:+d} relation and a grievance; Make Amends "
                f"({amends_price_words(AMENDS_GRIEVANCE)}) clears it.")
    return f"{delta:+d} relation."


def apply_shut_out_plan(
    world: Any, *, actor: str, plan: Mapping[str, Any], war_id: str, episode_id: str,
) -> Dict[str, Any]:
    """Apply the `shut_out` plan `proposer_ally_plan` returned — the relation
    hit, the durable `settlement_shut_out` grievance flag where the plan adds
    one, the settlement memory — and return the `ally_shut_out` reaction
    record. ONE body for both roads: the table's proposer-side pass and the
    bilateral ratifier's carried allies (`shut_out_carried_allies`)."""
    from backend.game_logic.diplomacy import _add_grievance_flag

    ally = str(plan["ally"])
    relation_hit = int(plan["relation_delta"])
    grievance_flag_added = bool(plan["grievance_flag_added"])
    if hasattr(world, "modify_nation_relation"):
        # S14E-X37: the reaction's write keeps a live mission's books.
        from backend.game_logic.diplomatic_dialogue import modify_relation_booked
        modify_relation_booked(world, actor, ally, relation_hit,
                               "settlement_shut_out", actor, ally)
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
            "standing_level": plan["standing_level"],
            "material_share": plan["material_share"],
            "material_points": plan["material_points"],
            "severity": plan["severity"],
            "relation_delta": relation_hit,
            "power_tier": plan["power_tier"],
        },
        expires_in=None,
    )
    return {
        "kind": "ally_shut_out",
        "ally": ally,
        "paid_regions": list(plan.get("paid_regions") or []),
        "standing_level": plan["standing_level"],
        "severity": plan["severity"],
        "relation_delta": relation_hit,
        "grievance_flag_added": grievance_flag_added,
        "material_share": plan["material_share"],
        "material_points": plan["material_points"],
        "power_tier": plan["power_tier"],
    }


def forecast_proposer_side_reactions(
    world: Any, *, war_id: str, proposer_side: str,
    settlement_terms: Iterable[Mapping[str, Any]], proposer_leader: str = "",
    covered_enemy_participants: Optional[Iterable[str]] = None,
    kinds: Tuple[str, ...] = ("shut_out",),
) -> List[Dict[str, Any]]:
    """S14E-10 / S14E-D3: the allies a settlement will leave out, and what
    each pays — read BEFORE the click from the ratifier's own plan
    (`proposer_ally_plan` over the same members, the same standing/material
    reading, the same terms), so the list is EXACTLY the allies
    `_evaluate_proposer_side_reactions` will punish and the figures are the
    ones it applies. A pure read (nothing is written). One row per ally:
    the plan plus `nation`, `display` (`shut_out_words`) and `amends`
    ({price, action}) — [] when no ally is left out.

    S14E-D8 / S14E-X51 (S14f part 2): `covered_enemy_participants` (the
    table's coverage) is read into each ally's reading exactly as the
    ratifier reads it (so an ally whose war the table does not end is
    "fights on alone", not a shut-out), and `kinds` widens the list beyond
    the default shut-outs to the plans the ratifier also acts on: "rewarded"
    (the named ally's gratitude, with its figure) and "fights_on". Every row
    carries its plan's `kind`."""
    instance = (getattr(world, "war_instances", {}) or {}).get(war_id)
    if not isinstance(instance, Mapping) or proposer_side not in ("attackers", "defenders"):
        return []
    terms = [t for t in (settlement_terms or []) if isinstance(t, Mapping)]
    actor = (str(proposer_leader or "") or _side_leader(instance, proposer_side)
             or str(getattr(world, "player_nation", "France")))
    covered = (None if covered_enemy_participants is None
               else sorted({str(c) for c in covered_enemy_participants if c}))
    rows: List[Dict[str, Any]] = []
    for ally in _participants_on_side(instance, proposer_side):
        if ally == actor:
            continue
        plan = proposer_ally_plan(
            world, war_id=war_id, proposer_side=proposer_side, ally=ally,
            settlement_terms=terms, covered=covered)
        if plan["kind"] not in kinds:
            continue
        rows.append(shut_out_row(world, plan) if plan["kind"] == "shut_out"
                    else ally_standing_row(world, plan))
    return rows


def _and_list(names: List[str]) -> str:
    return (", ".join(names[:-1]) + " and " + names[-1]) if len(names) > 1 else (names[0] if names else "")


def rewarded_words(world: Any, plan: Mapping[str, Any]) -> str:
    """S14E-X51: the named ally's gratitude, STATED before the click from the
    plan the ratifier writes — "Austria takes Tyrol by it and thanks us
    (+10 relation)." (the bilateral aftermath's own sentence, in the table's
    voice; "her share" when the instrument names her but no province)."""
    name = _display_of(world, str(plan.get("ally") or plan.get("nation") or ""))
    regions = [str(r) for r in (plan.get("awarded_regions") or []) if r]
    return (f"{name} takes {_and_list(regions) or 'her share'} by it and thanks us "
            f"({int(plan.get('relation_delta') or 0):+d} relation).")


def fights_on_words(world: Any, plan: Mapping[str, Any]) -> str:
    """S14E-D8: the ally the table does not reach, STATED before the click —
    "Spain fights on alone against Britain — the table does not touch her
    war." No relation hit, no grievance: nothing is asked of her. An ally with
    no live pair in the war at all has no war to fight on, and the line says
    so (she "has no war the table touches")."""
    name = _display_of(world, str(plan.get("ally") or plan.get("nation") or ""))
    against = [_display_of(world, str(n)) for n in (plan.get("fights_on_against") or []) if n]
    if not against:
        return f"{name} has no war the table touches — nothing changes between us."
    return f"{name} fights on alone against {_and_list(against)} — the table does not touch her war."


def ally_standing_row(world: Any, plan: Mapping[str, Any]) -> Dict[str, Any]:
    """A forecast row from a `rewarded` or `fights_on` plan (the siblings of
    `shut_out_row`): the plan, the nation and the words — whole numbers to
    the client (Golden Rule 2), no cure to buy."""
    row: Dict[str, Any] = dict(plan)
    row["material_share_pct"] = int(round(float(row.pop("material_share", 0.0) or 0.0) * 100))
    row["material_points"] = int(row.get("material_points") or 0)
    row["relation_delta"] = int(row.get("relation_delta") or 0)
    row["nation"] = str(plan.get("ally") or "")
    row["display"] = (rewarded_words(world, plan) if plan.get("kind") == "rewarded"
                      else fights_on_words(world, plan))
    row["amends"] = {}
    return row


def shut_out_row(world: Any, plan: Mapping[str, Any]) -> Dict[str, Any]:
    """A forecast row from a `shut_out` plan: the plan, the nation, the words
    and — where the plan adds a grievance — the cure's price."""
    row: Dict[str, Any] = dict(plan)
    # Golden Rule 2: whole numbers to the client (the share as a percent).
    row["material_share_pct"] = int(round(float(row.pop("material_share", 0.0) or 0.0) * 100))
    row["material_points"] = int(row.get("material_points") or 0)
    row["relation_delta"] = int(row.get("relation_delta") or 0)
    row["nation"] = str(plan.get("ally") or "")
    row["display"] = shut_out_words(world, plan)
    if plan.get("grievance_flag_added"):
        from backend.game_logic.cabinet_rows import (
            AMENDS_GRIEVANCE, _amends_costs, amends_price_words,
        )
        cost = _amends_costs()[AMENDS_GRIEVANCE]
        row["amends"] = {
            "action": AMENDS_GRIEVANCE, "gold": int(cost["gold"]), "dp": int(cost["dp"]),
            "price_display": amends_price_words(AMENDS_GRIEVANCE),
        }
    else:
        row["amends"] = {}
    return row


def _evaluate_proposer_side_reactions(
    world: Any,
    *,
    war_id: str,
    proposer_side: str,
    war_instance: Mapping[str, Any],
    settlement_terms: List[Mapping[str, Any]],
    applied_clauses: List[Mapping[str, Any]],
    episode_id: str,
    pre_cleanup_standings: Optional[Mapping[str, str]] = None,
    pre_cleanup_members: Optional[List[str]] = None,
    pre_cleanup_readings: Optional[Mapping[str, Mapping[str, Any]]] = None,
    proposer_leader: str = "",
) -> List[Dict[str, Any]]:
    reactions: List[Dict[str, Any]] = []
    player_nation = str(getattr(world, "player_nation", "France"))
    # PC-F81: the members and their standing as they stood BEFORE the pair
    # transitions (a carried ally has already left the live instance).
    proposer_members = (list(pre_cleanup_members) if pre_cleanup_members
                        else _participants_on_side(war_instance, proposer_side))
    # S14E-10: the side's leader as it stood BEFORE the cleanup too — once a
    # whole war ends the live instance's leader field holds whichever member
    # left last (the Kingdom of Italy), and the reaction was written between
    # THAT court and the allies instead of France.
    resolved_leader = (str(proposer_leader or "")
                       or _side_leader(war_instance, proposer_side) or player_nation)

    # France is the actor on settlement memories. If the proposer leader
    # is a non-player nation, settlement memories still attribute to the
    # proposer leader (the actor that ratified the package).
    actor = resolved_leader

    for ally in proposer_members:
        if ally == actor:
            continue
        reading = (pre_cleanup_readings or {}).get(ally)
        if not reading:
            reading = proposer_ally_reading(
                world, war_id=war_id, proposer_side=proposer_side, ally=ally,
                settlement_terms=settlement_terms,
                standing=(str(pre_cleanup_standings.get(ally))
                          if pre_cleanup_standings and pre_cleanup_standings.get(ally)
                          else None))
        plan = proposer_ally_plan(
            world, war_id=war_id, proposer_side=proposer_side, ally=ally,
            settlement_terms=settlement_terms, reading=reading)
        if plan["kind"] in ("none", "fights_on"):
            # S14E-D8: "fights_on" is the allies the table does not reach — no
            # relation hit, no grievance, nothing written (the forecast says
            # so before the click: shown == applied).
            continue
        if plan["kind"] == "rewarded":
            reactions.append(_reward_named_ally(
                world, actor=actor, ally=ally, standing=plan["standing_level"],
                war_id=war_id, awarded_regions=plan["awarded_regions"],
                episode_id=episode_id, power_tier=plan["power_tier"]))
            continue
        reactions.append(apply_shut_out_plan(
            world, actor=actor, plan=plan, war_id=war_id, episode_id=episode_id))
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
    enemy_leader: str = "",
) -> List[Dict[str, Any]]:
    reactions: List[Dict[str, Any]] = []
    # PC-F51 sibling: the leader AS IT STOOD when the table was signed —
    # the exit now re-seats a side's leader at once, so the live instance
    # may already name the court that fought on, and the leader who signed
    # would read as "sold out by the war leader" by her own settlement.
    enemy_leader = str(enemy_leader or _side_leader(war_instance, accepting_side) or "")
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
            # S14E-X37: the reaction's writes keep a live mission's books.
            from backend.game_logic.diplomatic_dialogue import modify_relation_booked
            modify_relation_booked(
                world, player_nation, participant, delta_vs_proposer,
                "settlement_sold_out", enemy_leader or player_nation, participant,
            )
            if enemy_leader:
                modify_relation_booked(
                    world, enemy_leader, participant, delta_vs_leader,
                    "settlement_sold_out", enemy_leader, participant,
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
    except Exception as exc:
        report(exc, "settlement_reactions._evaluate_bargain_outcomes: import backend.game_logic.diplomacy")
        return out
    awarded_by_region: Dict[str, Mapping[str, Any]] = {}
    for term in settlement_terms or []:
        if term.get("type") != "territory_cede":
            continue
        # PC-X32 (S14 part 1): the table's canonical cession carries a
        # SINGULAR `region` — reading only the `regions` list left every
        # table award of a claim province to the wrong court unseen.
        regions = list(term.get("regions") or [])
        if term.get("region") and term.get("region") not in regions:
            regions.append(term.get("region"))
        for region in regions:
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
        if not recipient:
            continue
        if recipient == promiser:
            # War Bargains are France-claim-scoped. The WB-B lifecycle
            # pass still owns mechanical fulfillment, but the settlement
            # reaction event needs this marker so Tilsit-style
            # bargain-plus-ally-fallout presentation can be tagged in the
            # same ratification.
            out.append({
                "kind": "bargain_fulfilled_at_settlement",
                "bargain_id": bargain.get("id"),
                "promiser": promiser,
                "beneficiary": beneficiary,
                "claim_region": claim_region,
                "recipient": recipient,
            })
            continue
        if recipient == beneficiary:
            # Not a breach; current bargain semantics are
            # France-claim-scoped, so awarding the claim to the
            # beneficiary is a settlement reward rather than WB-B
            # fulfillment.
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
    settlement_terms: Optional[List[Mapping[str, Any]]] = None,
    pre_cleanup_war_label: str = "",
    pre_cleanup_attacker_leader: str = "",
    pre_cleanup_defender_leader: str = "",
    staged_route_id: str = "",
    route_id: str = "",
    acceptance_snapshot: Optional[Mapping[str, Any]] = None,
    acceptance_at_staging: Optional[Mapping[str, Any]] = None,
    white_peace: bool = False,
    surrender_preset: bool = False,
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
        _term_display,
        detect_awe_set_pieces,
    )
    turn = int(getattr(world, "current_turn", 0) or 0)
    # G4F-11 (term-reflection audit): the dispatch line and the
    # recent-settlements record read these — the old thin
    # "type: from→to" form dropped the gold amount and the ceded
    # region's NAME. Use the same rich formatter the review rows use
    # ("Gold indemnity: 200 gold from Britain to France").
    terms_summary = [_term_display(c) for c in applied_clauses[:3]]
    instance = (getattr(world, "war_instances", {}) or {}).get(war_id) or {}
    # Pre-cleanup overrides win when the caller supplied them; otherwise
    # fall back to the live war_instance state. Cleanup_war_end empties
    # `attackers`/`defenders`/leader fields, so the live read is unsafe
    # for post-ratification calls.
    attacker_leader = (
        pre_cleanup_attacker_leader
        or str(instance.get("attacker_leader") or "")
    )
    defender_leader = (
        pre_cleanup_defender_leader
        or str(instance.get("defender_leader") or "")
    )
    proposer_leader = (
        attacker_leader if proposer_side == "attackers" else defender_leader
    )
    accepting_leader = (
        attacker_leader if accepting_side == "attackers" else defender_leader
    )
    if pre_cleanup_war_label:
        war_label = pre_cleanup_war_label
    else:
        attackers_for_label = (
            list(proposer_members)
            if proposer_side == "attackers"
            else list(accepting_members)
        )
        defenders_for_label = (
            list(proposer_members)
            if proposer_side == "defenders"
            else list(accepting_members)
        )
        if not attackers_for_label:
            attackers_for_label = list(instance.get("attackers") or [])
        if not defenders_for_label:
            defenders_for_label = list(instance.get("defenders") or [])
        # G4F-11: full-sides label (the first-vs-first form undersold a
        # multilateral settlement as a pair).
        war_label = (
            f"{' + '.join(attackers_for_label)} vs "
            f"{' + '.join(defenders_for_label)}"
            if attackers_for_label and defenders_for_label
            else war_id
        )
    awe_tags = detect_awe_set_pieces(
        settlement_terms=list(settlement_terms or applied_clauses or []),
        participant_reactions=list(participant_reactions or []),
        balance_projection=balance_projection or {},
        proposer_side=proposer_side,
    )
    # SC-14c: read the staged dialogue's route id verbatim. The staged
    # dialogue minted a `settlement:{war_id}:{turn}:{seq}` id from the
    # per-(war_id, turn) sequence; reaction events, dispatch, ledger,
    # notification meta, and result feedback all consume it. Falling back
    # to a recomputed id is reserved for legacy save/test fixtures that
    # never staged through `build_settlement_confirm_dialogue`.
    resolved_route_id = str(staged_route_id or route_id or "").strip()
    if not resolved_route_id:
        from backend.game_logic.settlement_routes import (
            mint_settlement_route_id,
        )
        resolved_route_id = mint_settlement_route_id(world, war_id=war_id, turn=turn)
    event = {
        "type": "settlement_summary",
        "turn": turn,
        "war_id": war_id,
        "war_label": war_label,
        "covered_enemy_participants": list(covered_enemy_participants),
        "proposer_side": proposer_side,
        "accepting_side": accepting_side,
        "proposer_members": list(proposer_members),
        "accepting_members": list(accepting_members),
        "attacker_leader": attacker_leader,
        "defender_leader": defender_leader,
        "proposer_leader": proposer_leader,
        "accepting_leader": accepting_leader,
        "terms_summary": terms_summary,
        "applied_clauses": [dict(c) for c in applied_clauses],
        "participant_reactions": [dict(r) for r in participant_reactions],
        "war_ended": bool(war_ended),
        "balance_projection": dict(balance_projection or {}),
        "awe_tags": list(awe_tags),
        # SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1 White Peace
        # Affordance: labels the emitted outcome so dispatch/ledger/
        # campaign-log can render it as a labeled white peace rather
        # than a generic settlement. Defaults to False for normal
        # treaty ratification.
        "white_peace": bool(white_peace),
        # SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-8 Dependency And
        # Surrender Terms Restoration: labels the emitted outcome when
        # the player ratified a Talleyrand surrender preset (peace +
        # dependency clause). Defaults to False for non-surrender
        # ratification, including manual dependency-clause authoring.
        "surrender_preset": bool(surrender_preset),
        # SC-15 amendment: archived settlement review renders the fresh
        # ratification-time `acceptance_snapshot`, not the stale staging
        # preview. `acceptance_at_staging` stays as audit context only.
        "acceptance_snapshot": dict(acceptance_snapshot or {}),
        "acceptance_at_staging": dict(acceptance_at_staging or {}),
        "route": {
            "event_family": SETTLEMENT_EVENT_FAMILY,
            "review_target": (
                SETTLEMENT_REVIEW_TARGET_ARCHIVED
                if war_ended
                else SETTLEMENT_REVIEW_TARGET_ACTIVE
            ),
            "route_id": resolved_route_id,
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

    meta = settlement_notification_meta(event, world=world)
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


def _emit_settlement_digest_event(  # noqa: D401
    world: Any,
    *,
    war_id: str,
    war_ended: bool,
    proposer_members: List[str],
    accepting_members: List[str],
    covered_enemy_participants: List[str],
    hidden_reaction_count: int,
    top_reaction_types: List[str],
    staged_route_id: str = "",
    route_id: str = "",
) -> Optional[Dict[str, Any]]:
    if hidden_reaction_count <= 0:
        return None
    from backend.game_logic.settlement_presentation import (
        SETTLEMENT_EVENT_FAMILY,
        SETTLEMENT_REVIEW_TARGET_ARCHIVED,
    )
    turn = int(getattr(world, "current_turn", 0) or 0)
    # SC-14c: digest reuses the staged route id so dispatch/ledger group
    # the digest under the same focus as the matching summary event.
    resolved_route_id = str(staged_route_id or route_id or "").strip()
    if not resolved_route_id:
        from backend.game_logic.settlement_routes import (
            mint_settlement_route_id,
        )
        resolved_route_id = mint_settlement_route_id(world, war_id=war_id, turn=turn)
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
            "route_id": resolved_route_id,
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
    pre_cleanup_war_label: str = "",
    pre_cleanup_proposer_members: Optional[List[str]] = None,
    pre_cleanup_accepting_members: Optional[List[str]] = None,
    pre_cleanup_attacker_leader: str = "",
    pre_cleanup_defender_leader: str = "",
    pre_cleanup_standings: Optional[Mapping[str, str]] = None,
    pre_cleanup_readings: Optional[Mapping[str, Mapping[str, Any]]] = None,
    staged_route_id: str = "",
    route_id: str = "",
    acceptance_snapshot: Optional[Mapping[str, Any]] = None,
    acceptance_at_staging: Optional[Mapping[str, Any]] = None,
    success: bool = True,
    mutated: bool = True,
    white_peace: bool = False,
    surrender_preset: bool = False,
) -> Dict[str, Any]:
    """D1/D2 settlement / cross-war reaction routing.

    Called from `ratify_settlement_confirm` AFTER cache invalidation and
    BEFORE the dialogue is popped (spec §11 line 1239 ordering). Reads
    fresh `war_instances_by_participant` indexes, writes settlement
    memories + grievance flags, runs WB-B bargain breach detection,
    bounded cross-war scan, and emits `settlement_summary` /
    `settlement_digest`.

    SC-15 / SC-23 failed-ratification guard: callers MUST set
    `success=False, mutated=False` (or pass empty / falsy
    `applied_clauses` plus a missing `acceptance_snapshot`) when
    ratification did not actually mutate state. The summary-event
    producer refuses emission in that case so failed ratifications do
    not leak `PEACE & SETTLEMENT HISTORY` rows into the ledger or the
    dispatch.
    """
    staged_route_id = str(staged_route_id or route_id or "").strip()
    if not success or not mutated:
        # SC-15 / SC-23 failed-ratification guard. Returning an empty
        # summary is sufficient — callers that hold the dialogue will
        # surface the failure through the normal acceptance refusal
        # banner, not through history rows.
        return {
            "summary_event": None,
            "digest_event": None,
            "all_reactions": [],
            "skipped_reason": "failed_ratification",
        }
    instance = (getattr(world, "war_instances", {}) or {}).get(war_id) or {}
    # Pre-cleanup overrides win when present (set by ratify_settlement_confirm
    # before cleanup_war_end empties the live `attackers`/`defenders` lists).
    if pre_cleanup_proposer_members:
        proposer_members = list(pre_cleanup_proposer_members)
    else:
        proposer_members = _participants_on_side(instance, proposer_side)
    if pre_cleanup_accepting_members:
        accepting_members = list(pre_cleanup_accepting_members)
    else:
        accepting_members = _participants_on_side(instance, accepting_side)
    proposer_member_set = set(proposer_members)
    episode_id_alloc = None
    try:
        from backend.game_logic.diplomacy import _allocate_episode_id

        episode_id_alloc = _allocate_episode_id
    except Exception as exc:
        report(exc, "settlement_reactions.route_settlement_reactions: import backend.game_logic.diplomacy")
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
        pre_cleanup_standings=pre_cleanup_standings,
        pre_cleanup_members=list(pre_cleanup_proposer_members or []),
        pre_cleanup_readings=pre_cleanup_readings,
        proposer_leader=str(
            (pre_cleanup_attacker_leader if proposer_side == "attackers"
             else pre_cleanup_defender_leader) or ""),
    )
    enemy_reactions = _evaluate_enemy_side_reactions(
        world,
        war_id=war_id,
        accepting_side=accepting_side,
        war_instance=instance,
        covered_enemy_participants=list(covered_enemy_participants or []),
        settlement_terms=list(settlement_terms or []),
        episode_id=episode_id,
        enemy_leader=str(
            (pre_cleanup_attacker_leader if accepting_side == "attackers"
             else pre_cleanup_defender_leader) or ""),
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
    # S14E-10: the side's leader as it stood BEFORE the cleanup (the live
    # instance's leader field is whichever member left last once a war ends).
    proposer_leader = (
        str((pre_cleanup_attacker_leader if proposer_side == "attackers"
             else pre_cleanup_defender_leader) or "")
        or _side_leader(instance, proposer_side)
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
        settlement_terms=list(settlement_terms or []),
        pre_cleanup_war_label=pre_cleanup_war_label,
        pre_cleanup_attacker_leader=pre_cleanup_attacker_leader,
        pre_cleanup_defender_leader=pre_cleanup_defender_leader,
        staged_route_id=staged_route_id,
        acceptance_snapshot=acceptance_snapshot,
        acceptance_at_staging=acceptance_at_staging,
        white_peace=bool(white_peace),
        surrender_preset=bool(surrender_preset),
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
            staged_route_id=staged_route_id,
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
