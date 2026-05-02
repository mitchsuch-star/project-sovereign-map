"""Imperial Settlement / Ally Participation — Contribution Tracker (Slices B1 + B2 ordering guard).

Slice B1 ships (already landed):

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

Slice B2 ordering guard ships (this commit):

- `accrue_battle_contribution(...)` — the canonical battle-bucket accrual
  entrypoint, called from `diplomacy.record_battle()` BEFORE the 1000-casualty
  war-score early return (spec §9.4: sub-1000-casualty battles still accrue
  settlement contribution). Accepts legacy single-attacker/single-defender
  shape (current call sites) and theater shape (post-B2 emitter wiring).

Future B2 work (not in this commit):

- Theater-aware call-site updates: `_post_combat_pipeline()`,
  `_execute_attack()` inline path, auto-dispatch charge path, glorious-charge
  pipeline. Each must pass `attacker_participants`, `defender_participants`,
  and `nation_theater_strength` derived from one-hop adjacency.
- Occupation, support, and treaty-clause emitters.
- British coalition subsidy attribution.

Slice B3 ships (later):

- Per-turn staying-power accrual.
- War-entry seam wiring of `open_episode()` / `close_episode_for_exit()`.
- Same-turn separate-peace event ordering.
- Archive compaction.

The module is event-driven by design (spec §9.5): no per-region scans,
no per-turn `world.regions.values()` walks. All readers go through
`war_contribution_scores[war_id][nation]` indexing.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Set, Tuple


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


# ===========================================================================
# Slice B2 — Battle-bucket accrual entrypoint (spec §9.2 / §9.4)
# ===========================================================================
#
# This is the single canonical accrual entrypoint that
# `diplomacy.record_battle()` calls BEFORE the 1000-casualty war-score early
# return. The ordering is pinned by tests; settlement contribution must not
# inherit the war-score sub-1000 filter (spec §9.4 line 713).


def detect_battle_theater(
    world: Any,
    *,
    battle_region: str,
    attacker_nation: str,
    defender_nation: str,
    attacker_marshal_name: Optional[str] = None,
    defender_marshal_name: Optional[str] = None,
    war_id: Optional[str] = None,
    attacker_pre_battle_strength: Optional[int] = None,
    defender_pre_battle_strength: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """One-hop adjacency theater detector for battle contribution (spec §9.4).

    Builds the `attacker_participants` / `defender_participants` /
    `nation_theater_strength` payload that `accrue_battle_contribution()`
    consumes for theater-aware credit splitting. Per spec §9.4 line 717:

    - A nation participates if it has an active marshal in the battle region
      OR in any one-hop adjacent region during the turn of the battle.
    - Only active participants in the same `war_instance` side can be credited.
    - Credit divides by `nation_theater_strength` among detected participants
      on that side (spec §9.4 line 721).

    Whole-war credit is forbidden (spec §9.4 line 725): a same-side
    participant fighting on a different front gets nothing from this battle.

    Returns ``None`` when the battle cannot resolve into a war side
    (no active war_instance owns the pair, or both nations land on
    the same side). The caller must fall back to legacy single-attacker /
    single-defender accrual in that case (the legacy adapter already
    handles the no-`war_id` path inside `accrue_battle_contribution`).

    `attacker_pre_battle_strength` / `defender_pre_battle_strength` are
    optional overrides for the explicit attacker / defender; when paired with
    marshal names they replace only that primary marshal's current
    (post-battle) strength. Other same-nation marshals in the theater keep
    their recorded strength, so multi-marshal same-nation theater strength
    does not collapse to the primary combatant alone.
    """
    if not battle_region or not attacker_nation or not defender_nation:
        return None
    resolved_war_id = war_id or _resolve_active_war_id_for_pair(
        world, attacker_nation, defender_nation,
    )
    if not resolved_war_id:
        return None
    instances = getattr(world, "war_instances", None) or {}
    instance = instances.get(resolved_war_id) or {}
    if not instance:
        return None
    side_by_nation = instance.get("side_by_nation") or {}
    attacker_side = side_by_nation.get(attacker_nation)
    defender_side = side_by_nation.get(defender_nation)
    if not attacker_side or not defender_side or attacker_side == defender_side:
        return None

    active_participants = set(instance.get("active_participants") or [])

    theater_regions: Set[str] = {battle_region}
    region_getter = getattr(world, "get_region", None)
    region = region_getter(battle_region) if callable(region_getter) else None
    if region is not None:
        for adj in getattr(region, "adjacent_regions", []) or []:
            if adj:
                theater_regions.add(adj)

    attacker_set: Set[str] = set()
    defender_set: Set[str] = set()
    nation_theater_strength: Dict[str, int] = {}

    marshals = getattr(world, "marshals", None) or {}
    for marshal in marshals.values():
        if not marshal:
            continue
        location = getattr(marshal, "location", None)
        if not location or location not in theater_regions:
            continue
        marshal_name = getattr(marshal, "name", None)
        strength = max(0, int(getattr(marshal, "strength", 0) or 0))
        if (
            attacker_pre_battle_strength is not None
            and attacker_marshal_name
            and marshal_name == attacker_marshal_name
        ):
            strength = max(int(attacker_pre_battle_strength) or 0, 0)
        elif (
            defender_pre_battle_strength is not None
            and defender_marshal_name
            and marshal_name == defender_marshal_name
        ):
            strength = max(int(defender_pre_battle_strength) or 0, 0)
        if strength <= 0:
            continue
        nation = getattr(marshal, "nation", None)
        if not nation:
            continue
        if active_participants and nation not in active_participants:
            continue
        side = side_by_nation.get(nation)
        if side == attacker_side:
            attacker_set.add(nation)
        elif side == defender_side:
            defender_set.add(nation)
        else:
            continue
        nation_theater_strength[nation] = (
            nation_theater_strength.get(nation, 0) + strength
        )

    # Always credit the explicit attacker / defender even if their marshal
    # was annihilated mid-resolve; floor 1 (or pre-battle override when the
    # caller has it) keeps the per-side denominator non-zero.
    attacker_set.add(attacker_nation)
    defender_set.add(defender_nation)

    if attacker_pre_battle_strength is not None:
        if not attacker_marshal_name:
            nation_theater_strength[attacker_nation] = max(
                nation_theater_strength.get(attacker_nation, 0),
                int(attacker_pre_battle_strength) or 0,
                0,
            )
        else:
            nation_theater_strength.setdefault(
                attacker_nation, max(int(attacker_pre_battle_strength) or 0, 0),
            )
    if defender_pre_battle_strength is not None:
        if not defender_marshal_name:
            nation_theater_strength[defender_nation] = max(
                nation_theater_strength.get(defender_nation, 0),
                int(defender_pre_battle_strength) or 0,
                0,
            )
        else:
            nation_theater_strength.setdefault(
                defender_nation, max(int(defender_pre_battle_strength) or 0, 0),
            )

    nation_theater_strength.setdefault(attacker_nation, 0)
    nation_theater_strength.setdefault(defender_nation, 0)

    return {
        "war_id": resolved_war_id,
        "attacker_participants": sorted(attacker_set),
        "defender_participants": sorted(defender_set),
        "nation_theater_strength": dict(nation_theater_strength),
    }


def _resolve_active_war_id_for_pair(
    world: Any, nation_a: str, nation_b: str,
) -> Optional[str]:
    """Return the active `war_id` whose `active_diplo_keys` contains the pair.

    Uses the cached `world.get_war_instances_by_participant()` index when
    available so settlement accrual stays off the per-region/per-instance
    scan budget at full-Europe scale (impl plan §"Scale Rules").

    Returns ``None`` when no active war_instance owns the pair (e.g. the
    diplomatic state is WAR but the war_instance has not been allocated, or
    the pair belongs only to a `resolved_diplo_keys` archive).
    """
    if not nation_a or not nation_b:
        return None
    make_key = getattr(world, "_make_diplo_key", None)
    diplo_key = (
        make_key(nation_a, nation_b)
        if callable(make_key)
        else "|".join(sorted((nation_a, nation_b)))
    )
    instances = getattr(world, "war_instances", None) or {}
    if not instances:
        return None
    candidate_war_ids: List[str] = []
    participant_lookup = getattr(world, "get_war_instances_by_participant", None)
    if callable(participant_lookup):
        candidate_war_ids = list(participant_lookup(nation_a) or [])
    if not candidate_war_ids:
        candidate_war_ids = list(instances.keys())
    for war_id in candidate_war_ids:
        instance = instances.get(war_id) or {}
        if diplo_key in (instance.get("active_diplo_keys") or []):
            return war_id
    return None


def _battle_side_raw(
    *,
    inflicted_casualties: int,
    suffered_casualties: int,
    decisive_win: bool,
) -> int:
    """Per-side raw battle points per spec §9.2.

    ``battle_side_raw =
        casualties_inflicted // 100
        + casualties_suffered // 250
        + decisive_battle_win * 25``

    The raw value is per-side; per-nation distribution divides by theater
    strength share (spec §9.4). The decisive criterion matches the existing
    war-score decisive criterion (ratio > 2:1 AND total > 10,000) so a single
    battle never gets two different "decisive" interpretations; the
    war-score decisive cap (max 2 per war) is a war-score concept and is
    not mirrored on the settlement side because the episode boundary already
    bounds settlement decisive credit.
    """
    return (
        max(0, int(inflicted_casualties)) // 100
        + max(0, int(suffered_casualties)) // 250
        + (25 if decisive_win else 0)
    )


def _is_decisive_battle(
    attacker_casualties: int, defender_casualties: int,
) -> bool:
    """Match the war-score decisive criterion in `diplomacy.record_battle()`."""
    total = int(attacker_casualties) + int(defender_casualties)
    if total <= 10000:
        return False
    if attacker_casualties <= 0 or defender_casualties <= 0:
        return False
    ratio = (
        max(attacker_casualties, defender_casualties)
        / min(attacker_casualties, defender_casualties)
    )
    return ratio > 2.0


def accrue_battle_contribution(
    world: Any,
    *,
    attacker_nation: str,
    defender_nation: str,
    winner_nation: str,
    attacker_casualties: int,
    defender_casualties: int,
    location: str = "",
    war_id: Optional[str] = None,
    attacker_participants: Optional[List[str]] = None,
    defender_participants: Optional[List[str]] = None,
    nation_theater_strength: Optional[Mapping[str, int]] = None,
    turn: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """Accrue battle-bucket contribution for a battle (spec §9.2 / §9.4).

    Slice B2 entrypoint, called from `diplomacy.record_battle()` BEFORE the
    1000-casualty war-score early return. Sub-1000-casualty battles still
    accrue settlement contribution (spec §9.4 line 713) — only the pairwise
    war-score record is filtered.

    Calling shapes:

    - **Legacy** (current B2-transition callers): omit
      `attacker_participants` / `defender_participants` /
      `nation_theater_strength`; the legacy adapter (spec §9.6) fills them
      with `[attacker]`, `[defender]`, theater strength `1` each.
    - **Theater-aware** (post-B2 emitter wiring): supply explicit
      participant lists derived from one-hop adjacency, plus per-nation
      theater strength.

    No-op cases (return ``None``):

    - `attacker_nation` or `defender_nation` empty.
    - `war_id` cannot be resolved (no active war_instance owns the pair).
    - `war_instance` has no `side_by_nation` mapping for both nations, or
      the two nations land on the same side.
    - No same-side participant has an active episode (per spec §7.5 the
      reader filters by active-episode turn range; nothing to accrue).
    - Both side-raw values land at zero (e.g. zero casualties + no
      decisive win).

    Returns the accrual event dict (annotated with
    `accrued_battle_points: {nation: bucket_points}`) for tests/debug callers.
    """
    if not attacker_nation or not defender_nation:
        return None
    resolved_war_id = war_id or _resolve_active_war_id_for_pair(
        world, attacker_nation, defender_nation,
    )
    if not resolved_war_id:
        return None
    instances = getattr(world, "war_instances", None) or {}
    instance = instances.get(resolved_war_id) or {}
    if not instance:
        return None
    side_by_nation = instance.get("side_by_nation") or {}
    attacker_side = side_by_nation.get(attacker_nation)
    defender_side = side_by_nation.get(defender_nation)
    if not attacker_side or not defender_side or attacker_side == defender_side:
        return None

    # Fill theater data via the legacy adapter when caller passed nothing.
    legacy_record = adapt_legacy_battle_record({
        "attacker": attacker_nation,
        "defender": defender_nation,
        "winner": winner_nation,
        "attacker_casualties": int(attacker_casualties),
        "defender_casualties": int(defender_casualties),
        "battle_region": location,
        "war_id": resolved_war_id,
        "turn": turn,
        "attacker_participants": attacker_participants,
        "defender_participants": defender_participants,
        "nation_theater_strength": nation_theater_strength,
    })
    a_participants: List[str] = list(legacy_record["attacker_participants"])
    d_participants: List[str] = list(legacy_record["defender_participants"])
    theater: Dict[str, int] = dict(legacy_record["nation_theater_strength"])

    decisive = _is_decisive_battle(attacker_casualties, defender_casualties)
    attacker_decisive_win = decisive and winner_nation == attacker_nation
    defender_decisive_win = decisive and winner_nation == defender_nation

    attacker_side_raw = _battle_side_raw(
        inflicted_casualties=defender_casualties,
        suffered_casualties=attacker_casualties,
        decisive_win=attacker_decisive_win,
    )
    defender_side_raw = _battle_side_raw(
        inflicted_casualties=attacker_casualties,
        suffered_casualties=defender_casualties,
        decisive_win=defender_decisive_win,
    )

    accrued: Dict[str, int] = {}

    def _episode_accepts_turn(episode: Mapping[str, Any]) -> bool:
        if turn is None:
            return True
        event_turn = int(turn)
        joined_turn = episode.get("joined_turn")
        if joined_turn is not None and event_turn < int(joined_turn):
            return False
        exited_turn = episode.get("exited_turn")
        if exited_turn is not None and event_turn > int(exited_turn):
            return False
        return True

    def _accrue_side(participants: List[str], side_raw: int, side: str) -> None:
        if side_raw <= 0 or not participants:
            return
        active_participants = set(instance.get("active_participants") or [])
        same_side_participants = [
            p for p in participants
            if side_by_nation.get(p) == side
            and (not active_participants or p in active_participants)
        ]
        if not same_side_participants:
            return
        # Floor 1 per spec §9.4 line 622: an otherwise valid detected
        # participant with theater strength <= 0 is not silently dropped.
        per_nation_strength: Dict[str, int] = {
            p: max(1, int(theater.get(p) or 0) or 1)
            for p in same_side_participants
        }
        side_strength = sum(per_nation_strength.values())
        if side_strength <= 0:
            return
        for participant in same_side_participants:
            episode = current_episode(world, resolved_war_id, participant)
            if episode is None:
                continue
            if not _episode_accepts_turn(episode):
                continue
            nation_raw = round(
                side_raw * per_nation_strength[participant] / side_strength,
            )
            if nation_raw <= 0:
                continue
            bucket_points = round(
                (nation_raw / side_raw) * BUCKET_WEIGHTS["battle"],
            )
            if bucket_points <= 0:
                continue
            episode["battle"] = int(episode.get("battle") or 0) + bucket_points
            episode["total"] = int(episode.get("total") or 0) + bucket_points
            accrued[participant] = accrued.get(participant, 0) + bucket_points

    _accrue_side(a_participants, attacker_side_raw, attacker_side)
    _accrue_side(d_participants, defender_side_raw, defender_side)

    if not accrued:
        return None

    return {
        "type": "war_battle_contribution",
        "war_id": resolved_war_id,
        "battle_region": location,
        "winner": winner_nation,
        "turn": turn,
        "attacker": attacker_nation,
        "defender": defender_nation,
        "attacker_casualties": int(attacker_casualties),
        "defender_casualties": int(defender_casualties),
        "attacker_participants": a_participants,
        "defender_participants": d_participants,
        "nation_theater_strength": theater,
        "decisive": decisive,
        "accrued_battle_points": dict(accrued),
    }


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
    "accrue_battle_contribution",
    "adapt_legacy_battle_record",
    "canonical_episode_id",
    "classify_standing",
    "close_episode_for_exit",
    "compute_standing_inputs",
    "contribution_share",
    "current_episode",
    "current_episode_material_total",
    "current_episode_total",
    "detect_battle_theater",
    "iter_active_episodes",
    "material_contribution_points",
    "material_contribution_share",
    "open_episode",
    "standing_for_participant",
    "total_side_current_episode_contribution",
    "total_side_material_contribution",
]
