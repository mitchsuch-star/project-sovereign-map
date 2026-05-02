"""Imperial Settlement / Ally Participation — Contribution Tracker (Slice B1).

Slice B1 owns:

- Data shape for ``world.war_contribution_scores`` per spec §9.1.
- Episode helpers (`canonical_episode_id`, `open_episode`,
  `close_episode_for_exit`, `current_episode`, `iter_active_episodes`).
- Current-episode math (`current_episode_total`,
  `current_episode_material_total`, `total_side_current_episode_contribution`,
  `total_side_material_contribution`, `contribution_share`,
  `material_contribution_share`).
- Old-record adapter (`adapt_legacy_battle_record`) per spec §9.6.
- Pure standing classifier (`classify_standing`) per spec §8.2 — accepts
  term-derived booleans explicitly so B1 callers never fabricate Slice C/D
  reaction state.

Slice B1 must NOT:

- Implement battle / occupation / support emitters (B2).
- Wire per-turn staying-power accrual or exit stamping (B3).
- Read or compute common-peace term legitimacy / War Bargain settlement
  classification / Slice C/D reaction routing.

The module is event-driven by design (spec §9.5): no per-region scans,
no per-turn `world.regions.values()` walks. All readers go through
`war_contribution_scores[war_id][nation]` indexing.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Tuple


# ===========================================================================
# Bucket weights (spec §9.2)
# ===========================================================================

BUCKET_WEIGHTS: Dict[str, int] = {
    "battle": 40,
    "occupation": 35,
    "staying_power": 15,
    "support": 10,
}

MATERIAL_BUCKETS: Tuple[str, ...] = ("battle", "occupation", "support")
ALL_BUCKETS: Tuple[str, ...] = ("battle", "occupation", "staying_power", "support")

# Standing thresholds (spec §8.2)
SEAT_MATERIAL_SHARE_THRESHOLD = 0.25
CONSULT_MATERIAL_SHARE_THRESHOLD = 0.10

# Contribution-signal thresholds (spec §9.3) — exposed for B2 dispatch wiring.
DISPATCH_LIGHT_THRESHOLD = 0.15
DISPATCH_SEAT_THRESHOLD = 0.25


# ===========================================================================
# Episode id canonicalization
# ===========================================================================


def canonical_episode_id(nation: str, war_sequence: int, episode_index: int) -> str:
    """Build the canonical episode id per spec §9.1 / §7.5.

    ``episode_id = "{nation_slug}_{war_sequence}_{episode_index}"`` where
    ``war_sequence`` is the surviving ``war_instance.created_sequence``
    (post-merge re-stamping is a B/A3 concern; B1 just builds the id from
    the supplied integers and trusts callers to pass the surviving
    sequence).

    Nation slug uses the raw nation key — current rosters are ASCII and
    contain no spaces, so a slug step would be cosmetic. Callers passing
    future nation keys with whitespace must normalize before calling.
    """
    return f"{nation}_{int(war_sequence)}_{int(episode_index)}"


# ===========================================================================
# Internal accessors — empty-safe at every layer
# ===========================================================================


def _get_store(world: Any) -> Dict[str, Dict[str, Dict]]:
    """Return ``world.war_contribution_scores`` as a dict, creating if absent."""
    store = getattr(world, "war_contribution_scores", None)
    if not isinstance(store, dict):
        store = {}
        setattr(world, "war_contribution_scores", store)
    return store


def _get_war_dict(world: Any, war_id: str, *, create: bool = False) -> Dict[str, Dict]:
    store = _get_store(world)
    war_dict = store.get(war_id)
    if war_dict is None and create:
        war_dict = {}
        store[war_id] = war_dict
    return war_dict if isinstance(war_dict, dict) else {}


def _get_nation_record(
    world: Any, war_id: str, nation: str, *, create: bool = False,
) -> Dict[str, Any]:
    """Return the ``{current_episode_id, episodes, historical_total}`` dict."""
    war_dict = _get_war_dict(world, war_id, create=create)
    if not war_dict and not create:
        return {}
    record = war_dict.get(nation)
    if record is None and create:
        record = {
            "current_episode_id": "",
            "episodes": {},
            "historical_total": 0,
        }
        war_dict[nation] = record
    return record if isinstance(record, dict) else {}


def _get_war_sequence(world: Any, war_id: str) -> int:
    """Read ``war_instances[war_id].created_sequence`` for canonical episode ids.

    Returns ``0`` if the instance is unknown (caller should treat that as
    a malformed call — episode ids would not be canonical).
    """
    instances = getattr(world, "war_instances", None) or {}
    instance = instances.get(war_id) or {}
    return int(instance.get("created_sequence") or 0)


# ===========================================================================
# Episode lifecycle helpers (B1 pure helpers; B3 wires call sites)
# ===========================================================================


def _new_episode_record(*, joined_turn: int) -> Dict[str, Any]:
    return {
        "joined_turn": int(joined_turn),
        "exited_turn": None,
        "battle": 0,
        "occupation": 0,
        "staying_power": 0,
        "support": 0,
        "total": 0,
    }


def open_episode(
    world: Any,
    war_id: str,
    nation: str,
    *,
    joined_turn: int,
    war_sequence: Optional[int] = None,
) -> Dict[str, Any]:
    """Create a new contribution episode for ``(war_id, nation)``.

    Spec §7.5: re-entry creates a NEW episode_id — never overwrite the
    prior one. B1 ships the helper; B3 wires the calls (war-entry seams,
    armistice resumption, late join).

    Returns the new episode dict (a reference into the store).
    """
    record = _get_nation_record(world, war_id, nation, create=True)
    sequence = (
        int(war_sequence) if war_sequence is not None else _get_war_sequence(world, war_id)
    )
    episodes = record.setdefault("episodes", {})
    next_index = len(episodes) + 1
    episode_id = canonical_episode_id(nation, sequence, next_index)
    episode = _new_episode_record(joined_turn=joined_turn)
    episodes[episode_id] = episode
    record["current_episode_id"] = episode_id
    return episode


def close_episode_for_exit(
    world: Any,
    war_id: str,
    nation: str,
    *,
    exited_turn: int,
    exit_path: str = "",
) -> Optional[Dict[str, Any]]:
    """Stamp ``exited_turn`` on the active episode (spec §7.5 / §9.5).

    The boundary is INCLUSIVE: same-turn settlement / elimination /
    separate-peace events still read the final active-turn contribution
    (spec line 574). We do NOT clear ``current_episode_id`` because
    same-turn readers may still need to attribute battle / occupation /
    support events that fire after the exit stamp under correct event
    ordering. ``exit_path`` is accepted for call-site symmetry with
    participant metadata, but is not written into the episode because
    spec §9.1 keeps episode records to the contribution/timing fields.

    Returns the closed episode dict, or ``None`` if there is no active
    episode (no record / no current_episode_id).
    """
    record = _get_nation_record(world, war_id, nation)
    if not record:
        return None
    current_id = record.get("current_episode_id") or ""
    if not current_id:
        return None
    episode = (record.get("episodes") or {}).get(current_id)
    if not isinstance(episode, dict):
        return None
    if episode.get("exited_turn") is None:
        episode["exited_turn"] = int(exited_turn)
    return episode


def current_episode(
    world: Any,
    war_id: str,
    nation: str,
) -> Optional[Dict[str, Any]]:
    """Return the active episode dict for ``(war_id, nation)`` or ``None``."""
    record = _get_nation_record(world, war_id, nation)
    if not record:
        return None
    current_id = record.get("current_episode_id") or ""
    if not current_id:
        return None
    episode = (record.get("episodes") or {}).get(current_id)
    return episode if isinstance(episode, dict) else None


def iter_active_episodes(world: Any, war_id: str) -> List[Tuple[str, Dict[str, Any]]]:
    """Return ``[(nation, episode_dict)]`` for every nation with an active episode.

    "Active" means the nation has a ``current_episode_id`` that resolves
    and the episode is unstamped (``exited_turn is None``). Used by B3
    per-turn staying-power accrual and B2 emitter same-side filters.
    """
    out: List[Tuple[str, Dict[str, Any]]] = []
    war_dict = _get_war_dict(world, war_id)
    for nation, record in war_dict.items():
        if not isinstance(record, dict):
            continue
        current_id = record.get("current_episode_id") or ""
        if not current_id:
            continue
        episode = (record.get("episodes") or {}).get(current_id)
        if not isinstance(episode, dict):
            continue
        if episode.get("exited_turn") is not None:
            continue
        out.append((nation, episode))
    return out


# ===========================================================================
# Current-episode totals (read-only, no mutation)
# ===========================================================================


def _episode_total(episode: Mapping[str, Any], buckets: Tuple[str, ...]) -> int:
    return sum(int(episode.get(bucket) or 0) for bucket in buckets)


def current_episode_total(world: Any, war_id: str, nation: str) -> int:
    """Sum of all four buckets on the active episode (spec §9.1)."""
    episode = current_episode(world, war_id, nation)
    if episode is None:
        return 0
    return _episode_total(episode, ALL_BUCKETS)


def current_episode_material_total(world: Any, war_id: str, nation: str) -> int:
    """Sum of material buckets (battle + occupation + support) only.

    ``staying_power`` is excluded — spec §8.2 / §9.1: standing thresholds
    use material share, not total share. Staying power can never trigger
    seat / 15% / 25% dispatches or major shut-out grievance by itself.
    """
    episode = current_episode(world, war_id, nation)
    if episode is None:
        return 0
    return _episode_total(episode, MATERIAL_BUCKETS)


def _side_members(world: Any, war_id: str, side: str) -> List[str]:
    """Return active participants on ``side`` of ``war_id``.

    Reads the `war_instances` record directly. B1 callers pass the side
    string; B2/B3 emitters resolve it from ``side_by_nation`` before
    calling.
    """
    instances = getattr(world, "war_instances", None) or {}
    instance = instances.get(war_id) or {}
    if side == "attackers":
        return list(instance.get("attackers") or [])
    if side == "defenders":
        return list(instance.get("defenders") or [])
    return []


def total_side_current_episode_contribution(
    world: Any, war_id: str, side: str,
) -> int:
    """Sum of all-bucket totals across every active participant on ``side``."""
    return sum(
        current_episode_total(world, war_id, nation)
        for nation in _side_members(world, war_id, side)
    )


def total_side_material_contribution(
    world: Any, war_id: str, side: str,
) -> int:
    """Sum of material totals across every active participant on ``side``."""
    return sum(
        current_episode_material_total(world, war_id, nation)
        for nation in _side_members(world, war_id, side)
    )


def contribution_share(
    world: Any, war_id: str, nation: str, side: str,
) -> float:
    """Total contribution share for ``nation`` on ``side`` (spec §9.1).

    Zero-safe: returns ``0.0`` when the side total is ``<= 0`` rather
    than dividing by zero.
    """
    nation_total = current_episode_total(world, war_id, nation)
    side_total = total_side_current_episode_contribution(world, war_id, side)
    if side_total <= 0:
        return 0.0
    return float(nation_total) / float(side_total)


def material_contribution_share(
    world: Any, war_id: str, nation: str, side: str,
) -> float:
    """Material contribution share — used for standing thresholds (spec §8.3).

    Per spec §9.1: if total side contribution is positive but material
    side contribution is zero, every nation's material share defaults to
    ``0`` (never divides by zero). Standing falls back to non-contribution
    rules for that side.
    """
    nation_material = current_episode_material_total(world, war_id, nation)
    side_material = total_side_material_contribution(world, war_id, side)
    if side_material <= 0:
        return 0.0
    return float(nation_material) / float(side_material)


def material_contribution_points(
    world: Any, war_id: str, nation: str,
) -> int:
    """Active-episode material points for the gate condition in §8.2.

    Equivalent to `current_episode_material_total`; named separately for
    readability at the classify-standing call site (spec uses the
    "material_contribution_points" term in §8.2 / §8.3).
    """
    return current_episode_material_total(world, war_id, nation)


# ===========================================================================
# Old-record adapter (spec §9.6)
# ===========================================================================


def adapt_legacy_battle_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    """Coerce a pre-B1 battle record into the theater shape per spec §9.6.

    Old records have only ``attacker``, ``defender``,
    ``attacker_casualties``, ``defender_casualties`` (and possibly
    ``location`` / ``region`` / ``turn``). The adapter fills in the
    theater fields B2 readers need:

    - ``attacker_participants`` defaults to ``[record["attacker"]]``.
    - ``defender_participants`` defaults to ``[record["defender"]]``.
    - ``nation_theater_strength`` defaults to ``{attacker: 1,
      defender: 1}`` so denominator math works.
    - ``battle_region`` derived from ``battle_region`` /
      ``location`` / ``region`` in that order.
    - ``war_id`` left as-is (``None`` if absent — B2 readers must skip
      records with no resolvable war_id; no retroactive multi-participant
      attribution per spec §9.6 line 756).

    The adapter is non-destructive: any field already present on the
    record wins. Returns a new dict (callers must not assume in-place
    mutation).
    """
    if not isinstance(record, Mapping):
        return {}
    attacker = record.get("attacker") or ""
    defender = record.get("defender") or ""
    attacker_participants = list(record.get("attacker_participants") or []) or (
        [attacker] if attacker else []
    )
    defender_participants = list(record.get("defender_participants") or []) or (
        [defender] if defender else []
    )
    theater_strength = dict(record.get("nation_theater_strength") or {})
    if not theater_strength:
        if attacker:
            theater_strength[attacker] = 1
        if defender:
            theater_strength[defender] = 1
    battle_region = (
        record.get("battle_region")
        or record.get("location")
        or record.get("region")
        or ""
    )
    return {
        "attacker": attacker,
        "defender": defender,
        "attacker_participants": attacker_participants,
        "defender_participants": defender_participants,
        "nation_theater_strength": theater_strength,
        "battle_region": battle_region,
        "war_id": record.get("war_id"),
        "turn": record.get("turn"),
        "attacker_casualties": int(record.get("attacker_casualties") or 0),
        "defender_casualties": int(record.get("defender_casualties") or 0),
        "winner": record.get("winner"),
        "decisive": bool(record.get("decisive") or False),
    }


# ===========================================================================
# Standing classifier (spec §8.2 / §8.3)
# ===========================================================================


SEAT = "seat"
CONSULT = "consult"
BENEFICIARY_ONLY = "beneficiary_only"
NO_STANDING = "no_standing"

_STANDING_RANK = {
    SEAT: 3,
    CONSULT: 2,
    BENEFICIARY_ONLY: 1,
    NO_STANDING: 0,
}


def classify_standing(
    *,
    power_tier: str,
    material_share: float,
    material_contribution_points: int,
    is_active_same_side: bool = True,
    is_vassal_auto_join: bool = False,
    has_active_bargain_stake: bool = False,
    has_survival_stake: bool = False,
    is_named_beneficiary: bool = False,
    has_direct_territorial_interest: bool = False,
    is_treaty_ally_materially_involved: bool = False,
    rival_strengthened: bool = False,
) -> str:
    """Pure standing classifier per spec §8.2.

    All term-derived inputs default to ``False`` so B1-only callers and
    tests can drive contribution-only paths without inventing Slice C/D
    reaction state. Slice C wires the term-derived booleans by walking
    the locked ``settlement_terms`` package; Slice D wires the same
    inputs from confirmed settlement reactions.

    Vassal auto-join cap (spec §8.2 line 506): vassal auto-joins receive
    AT MOST ``beneficiary_only`` UNLESS they independently meet
    material-contribution thresholds for ``consult`` or ``seat``. Other
    promotion paths (major auto-seat, bargain stake, survival stake,
    rival_strengthened, treaty ally, secondary tier) are gated by the cap.

    Returns one of ``"seat"``, ``"consult"``, ``"beneficiary_only"``,
    ``"no_standing"``.
    """
    tier = power_tier or "minor"
    has_material = bool(material_contribution_points and material_contribution_points > 0)
    share = float(material_share or 0.0)

    # Vassal cap branch — material thresholds are the only escape.
    if is_vassal_auto_join:
        if has_material and share >= SEAT_MATERIAL_SHARE_THRESHOLD:
            return SEAT
        if has_material and share >= CONSULT_MATERIAL_SHARE_THRESHOLD:
            return CONSULT
        # Cap non-material standing inputs at beneficiary_only. The cap is
        # not a floor: an unstaked auto-joined vassal stays no_standing.
        if (
            has_active_bargain_stake
            or has_survival_stake
            or is_named_beneficiary
            or has_direct_territorial_interest
            or is_treaty_ally_materially_involved
            or rival_strengthened
            or (is_active_same_side and has_material)
        ):
            return BENEFICIARY_ONLY
        return NO_STANDING

    # Seat tier (spec §8.2 line 487)
    if is_active_same_side and tier == "major":
        return SEAT
    if has_active_bargain_stake:
        return SEAT
    if has_survival_stake:
        return SEAT
    if has_material and share >= SEAT_MATERIAL_SHARE_THRESHOLD:
        return SEAT

    # Consult tier (spec §8.2 line 493)
    if has_material and share >= CONSULT_MATERIAL_SHARE_THRESHOLD:
        return CONSULT
    if tier == "secondary" and has_material:
        return CONSULT
    if has_direct_territorial_interest:
        return CONSULT
    if is_treaty_ally_materially_involved:
        return CONSULT
    if rival_strengthened and tier in ("major", "secondary"):
        return CONSULT
    # Minor tier with rival_strengthened needs material_contribution_points > 0
    # to promote to consult (spec §8.2 line 497).
    if rival_strengthened and tier == "minor" and has_material:
        return CONSULT

    # Beneficiary tier (spec §8.2 line 499)
    if is_named_beneficiary:
        return BENEFICIARY_ONLY
    if tier == "minor" and is_active_same_side and (
        is_named_beneficiary or has_direct_territorial_interest
    ):
        # minor with a named outcome already returned above; this branch
        # is the "vassal / liberated state receiving or losing a direct
        # outcome" arm where the stake is implicit.
        return BENEFICIARY_ONLY
    if is_active_same_side and has_material:
        return BENEFICIARY_ONLY

    return NO_STANDING


# ===========================================================================
# Composite standing-input bundler
# ===========================================================================


def compute_standing_inputs(
    world: Any,
    war_id: str,
    nation: str,
    *,
    side: str,
    is_vassal_auto_join: bool = False,
    has_active_bargain_stake: bool = False,
    has_survival_stake: bool = False,
    is_named_beneficiary: bool = False,
    has_direct_territorial_interest: bool = False,
    is_treaty_ally_materially_involved: bool = False,
    rival_strengthened: bool = False,
) -> Dict[str, Any]:
    """Bundle the inputs `classify_standing` consumes for a participant.

    Reads the contribution store + side membership only; term-derived
    inputs are passed through verbatim. B1 callers that have not staged
    a settlement package leave term inputs at their ``False`` defaults.
    """
    instances = getattr(world, "war_instances", None) or {}
    instance = instances.get(war_id) or {}
    side_by_nation = instance.get("side_by_nation") or {}
    is_active_same_side = side_by_nation.get(nation) == side

    tier_getter = getattr(world, "get_power_tier", None)
    tier = tier_getter(nation) if callable(tier_getter) else None
    power_tier = tier or "minor"

    nation_total = current_episode_total(world, war_id, nation)
    nation_material = current_episode_material_total(world, war_id, nation)
    side_total = total_side_current_episode_contribution(world, war_id, side)
    side_material = total_side_material_contribution(world, war_id, side)
    total_share = (
        float(nation_total) / float(side_total) if side_total > 0 else 0.0
    )
    mat_share = (
        float(nation_material) / float(side_material) if side_material > 0 else 0.0
    )

    return {
        "nation": nation,
        "side": side,
        "war_id": war_id,
        "power_tier": power_tier,
        "material_share": mat_share,
        "total_share": total_share,
        "material_contribution_points": nation_material,
        "total_contribution_points": nation_total,
        "is_active_same_side": is_active_same_side,
        "is_vassal_auto_join": is_vassal_auto_join,
        "has_active_bargain_stake": has_active_bargain_stake,
        "has_survival_stake": has_survival_stake,
        "is_named_beneficiary": is_named_beneficiary,
        "has_direct_territorial_interest": has_direct_territorial_interest,
        "is_treaty_ally_materially_involved": is_treaty_ally_materially_involved,
        "rival_strengthened": rival_strengthened,
    }


def standing_for_participant(
    world: Any,
    war_id: str,
    nation: str,
    *,
    side: str,
    **term_inputs: Any,
) -> str:
    """Convenience wrapper: bundle inputs + classify in one call.

    All term-derived booleans default to ``False`` (passed through
    `compute_standing_inputs`). Slice C/D callers supply explicit
    booleans drawn from the locked settlement package.
    """
    inputs = compute_standing_inputs(
        world,
        war_id,
        nation,
        side=side,
        **{k: v for k, v in term_inputs.items() if k in {
            "is_vassal_auto_join",
            "has_active_bargain_stake",
            "has_survival_stake",
            "is_named_beneficiary",
            "has_direct_territorial_interest",
            "is_treaty_ally_materially_involved",
            "rival_strengthened",
        }},
    )
    return classify_standing(
        power_tier=inputs["power_tier"],
        material_share=inputs["material_share"],
        material_contribution_points=inputs["material_contribution_points"],
        is_active_same_side=inputs["is_active_same_side"],
        is_vassal_auto_join=inputs["is_vassal_auto_join"],
        has_active_bargain_stake=inputs["has_active_bargain_stake"],
        has_survival_stake=inputs["has_survival_stake"],
        is_named_beneficiary=inputs["is_named_beneficiary"],
        has_direct_territorial_interest=inputs["has_direct_territorial_interest"],
        is_treaty_ally_materially_involved=inputs["is_treaty_ally_materially_involved"],
        rival_strengthened=inputs["rival_strengthened"],
    )


__all__ = [
    "ALL_BUCKETS",
    "BENEFICIARY_ONLY",
    "BUCKET_WEIGHTS",
    "CONSULT",
    "CONSULT_MATERIAL_SHARE_THRESHOLD",
    "DISPATCH_LIGHT_THRESHOLD",
    "DISPATCH_SEAT_THRESHOLD",
    "MATERIAL_BUCKETS",
    "NO_STANDING",
    "SEAT",
    "SEAT_MATERIAL_SHARE_THRESHOLD",
    "adapt_legacy_battle_record",
    "canonical_episode_id",
    "classify_standing",
    "close_episode_for_exit",
    "compute_standing_inputs",
    "contribution_share",
    "current_episode",
    "current_episode_material_total",
    "current_episode_total",
    "iter_active_episodes",
    "material_contribution_points",
    "material_contribution_share",
    "open_episode",
    "standing_for_participant",
    "total_side_current_episode_contribution",
    "total_side_material_contribution",
]
