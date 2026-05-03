"""Imperial Settlement / Ally Participation — Contribution Tracker (Slices B1 + B2 + B3).

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

Slice B2 ordering guard + emitter wiring (already landed):

- `accrue_battle_contribution(...)` — the canonical battle-bucket accrual
  entrypoint, called from `diplomacy.record_battle()` BEFORE the 1000-casualty
  war-score early return (spec §9.4: sub-1000-casualty battles still accrue
  settlement contribution).
- `detect_battle_theater(...)` — one-hop adjacency theater detector consumed
  by `_post_combat_pipeline()` / `_execute_attack()` inline / auto-dispatch
  charge.

Slice B2 non-battle emitters (already landed):

- `accrue_occupation_event(...)` — `war_occupation_event` accrual for
  enemy_region_captured (20), enemy_capital_captured (40),
  allied_region_restored (15), liberated_region_restored (15) per spec §9.2.
  `treaty_transfer` is logged but not accrued (spec §9.2 line 641).
- `emit_capture_occupation_event(...)` — capture-path convenience wrapper
  that classifies the kind from `from_controller`, captured region, and
  same-side ally membership before delegating to `accrue_occupation_event`.
- `accrue_support_event(...)` — `war_support_delivered` accrual for
  gold / subsidy / ap / manpower / access / supply per spec §9.2 line 614,
  with episode-id dedupe and per-`(war_id, supporter, support_kind)`
  access/supply cap.
- `resolve_british_subsidy_war_id(...)` — deterministic war attribution for
  `_process_british_subsidy()` per impl plan B2 bullets.

Slice B3 ships (this commit):

- Per-turn staying-power accrual: `accrue_staying_power_for_war(...)` and
  `accrue_staying_power_all_wars(...)` apply ``+5`` raw per active episode
  per turn, capped at ``10`` qualifying turns per episode (spec §9.2
  line 612). Idempotent per ``(war_id, nation, current_turn)``.
- Archive compaction: `compact_war_contribution_for_archive(...)` drops
  episode detail when an archived ``war_instance`` clears its 10-turn
  retention window (spec §9.5 line 178). The compacted per-nation totals
  move into ``world.archived_war_contribution_scores``.

War-entry seam wiring of `open_episode()` / `close_episode_for_exit()`,
same-turn separate-peace event ordering, and the live `cleanup_war_end`
hook live in `backend/game_logic/settlement_helpers.py` next to the
existing `attach_*` / `mark_participant_eliminated_in_all_wars` /
`archive_terminal_war_instances` helpers — keeping the lifecycle wiring
co-located with the war_instance state mutations.

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


# ===========================================================================
# Slice B2 — Occupation event accrual (spec §9.2 / §9.4)
# ===========================================================================

# Spec §9.2 line 641 raw point values, applied directly to `episode["occupation"]`.
# `treaty_transfer` is logged but not accrued (spec §9.2 line 641: "treaty_transfer
# events are ignored for contribution unless a future settlement-followup
# explicitly marks them as wartime occupation credit").
OCCUPATION_POINTS: Dict[str, int] = {
    "enemy_region_captured": 20,
    "enemy_capital_captured": 40,
    "allied_region_restored": 15,
    "liberated_region_restored": 15,
    "treaty_transfer": 0,
}

OCCUPATION_KINDS: Tuple[str, ...] = tuple(OCCUPATION_POINTS.keys())


def _episode_accepts_event_turn(
    episode: Mapping[str, Any], turn: Optional[int],
) -> bool:
    """Inclusive ``joined_turn <= turn <= exited_turn`` boundary check.

    Same rule as the per-battle filter inside `accrue_battle_contribution`:
    spec §7.5 / §9.5 require this exact boundary so same-turn exits still see
    the turn's contribution events when emitted before the exit stamp lands.
    """
    if turn is None:
        return True
    event_turn = int(turn)
    joined = episode.get("joined_turn")
    if joined is not None and event_turn < int(joined):
        return False
    exited = episode.get("exited_turn")
    if exited is not None and event_turn > int(exited):
        return False
    return True


def _resolve_war_id_for_pair_on_opposite_sides(
    world: Any, actor_nation: str, target_nation: str,
) -> Optional[str]:
    """Return the active `war_id` where actor and target are on opposite sides.

    Equivalent to `_resolve_active_war_id_for_pair` plus a side-membership
    check. Used by occupation accrual when the caller hands us
    ``actor_nation`` + ``target_nation`` (the previous controller of a
    captured region) without already knowing the war_id.
    """
    war_id = _resolve_active_war_id_for_pair(world, actor_nation, target_nation)
    if not war_id:
        return None
    instances = getattr(world, "war_instances", None) or {}
    instance = instances.get(war_id) or {}
    side_by_nation = instance.get("side_by_nation") or {}
    a_side = side_by_nation.get(actor_nation)
    t_side = side_by_nation.get(target_nation)
    if not a_side or not t_side or a_side == t_side:
        return None
    return war_id


def accrue_occupation_event(
    world: Any,
    *,
    actor_nation: str,
    region: str,
    occupation_kind: str,
    from_controller: str = "",
    to_controller: str = "",
    war_id: Optional[str] = None,
    target_nation: Optional[str] = None,
    turn: Optional[int] = None,
    event_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Accrue one occupation event into ``war_contribution_scores`` (spec §9.2).

    Returns the accrual event dict on success, ``None`` on no-op:

    - ``occupation_kind`` not in ``OCCUPATION_KINDS``.
    - ``actor_nation`` empty.
    - ``war_id`` cannot be resolved (`target_nation` must place the actor on
      a side opposite ``target_nation`` in some active `war_instance`).
    - Actor has no active episode in that war (spec §7.5).
    - Episode's `joined_turn`/`exited_turn` window excludes ``turn``.
    - ``treaty_transfer`` (spec §9.2 line 641: logged but not accrued).
    - Duplicate ``event_id`` already seen for this nation in this war.

    Per-event raw points are taken directly from ``OCCUPATION_POINTS`` and
    added to ``episode["occupation"]`` plus ``episode["total"]``. Slice B
    stores raw bucket points; standing computation derives shares at read
    time (spec §9.2 normalization formula).
    """
    if not actor_nation:
        return None
    if occupation_kind not in OCCUPATION_KINDS:
        return None

    resolved_war_id = war_id
    if not resolved_war_id and target_nation:
        resolved_war_id = _resolve_war_id_for_pair_on_opposite_sides(
            world, actor_nation, target_nation,
        )
    if not resolved_war_id:
        return None

    instances = getattr(world, "war_instances", None) or {}
    instance = instances.get(resolved_war_id) or {}
    if not instance:
        return None
    side_by_nation = instance.get("side_by_nation") or {}
    actor_side = side_by_nation.get(actor_nation)
    if not actor_side:
        return None
    active_participants = set(instance.get("active_participants") or [])
    if active_participants and actor_nation not in active_participants:
        return None

    points = OCCUPATION_POINTS.get(occupation_kind, 0)
    record = _get_nation_record(world, resolved_war_id, actor_nation)
    if not record:
        return None
    seen = record.setdefault("seen_occupation_event_ids", [])
    if event_id and event_id in seen:
        return None
    episode = current_episode(world, resolved_war_id, actor_nation)
    if episode is None:
        return None
    if not _episode_accepts_event_turn(episode, turn):
        return None

    if points > 0:
        episode["occupation"] = int(episode.get("occupation") or 0) + points
        episode["total"] = int(episode.get("total") or 0) + points
    if event_id:
        seen.append(event_id)

    return {
        "type": "war_occupation_event",
        "war_id": resolved_war_id,
        "actor_nation": actor_nation,
        "side": actor_side,
        "region": region,
        "from_controller": from_controller,
        "to_controller": to_controller,
        "occupation_kind": occupation_kind,
        "points_accrued": int(points),
        "turn": int(turn) if turn is not None else None,
        "episode_id": event_id,
    }


def _classify_capture_occupation_kind(
    world: Any,
    *,
    region: str,
    actor_nation: str,
    from_controller: str,
    war_id: str,
) -> str:
    """Decide which occupation_kind a capture event represents (spec §9.2 line 583).

    - If the captured region is the previous controller's national capital,
      it is `enemy_capital_captured`.
    - Else if the region's `starting_controller` is a same-side ally of the
      actor, it is `allied_region_restored`.
    - Else it is `enemy_region_captured`.

    Returns ``""`` if no kind applies (e.g. malformed inputs).
    """
    if not region or not actor_nation:
        return ""
    instances = getattr(world, "war_instances", None) or {}
    instance = instances.get(war_id) or {}
    side_by_nation = instance.get("side_by_nation") or {}
    actor_side = side_by_nation.get(actor_nation)
    if not actor_side:
        return ""

    # Capital match — single source of truth in `region.NATION_CAPITALS`.
    if from_controller:
        try:
            from backend.models.region import NATION_CAPITALS
        except Exception:  # pragma: no cover — import guard
            NATION_CAPITALS = {}
        if NATION_CAPITALS.get(from_controller) == region:
            return "enemy_capital_captured"

    # Ally restoration — captured region's lawful (starting) owner is a
    # same-side ally of actor in this war_instance. The Region class doesn't
    # store starting controller (only current controller); the
    # `get_starting_controllers()` helper is the single source of truth
    # (see `region.NATION_CAPITALS` documentation block).
    starting_controller = ""
    try:
        from backend.models.region import get_starting_controllers
        starting_controller = get_starting_controllers().get(region, "") or ""
    except Exception:  # pragma: no cover — import guard
        starting_controller = ""
    if (
        starting_controller
        and starting_controller != actor_nation
        and side_by_nation.get(starting_controller) == actor_side
    ):
        return "allied_region_restored"

    return "enemy_region_captured"


def emit_capture_occupation_event(
    world: Any,
    *,
    actor_nation: str,
    region: str,
    from_controller: str,
    turn: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """Capture-path convenience wrapper around `accrue_occupation_event`.

    Resolves the war_id from ``(actor_nation, from_controller)``, classifies
    the occupation_kind via `_classify_capture_occupation_kind`, and emits
    the event. Returns ``None`` if the capture has no resolvable war (e.g.
    actor and previous controller are not at war in any active war_instance).

    Caller is the controller-change site (`world_state.capture_region`); this
    keeps the kind-classification logic out of the model code per the project
    convention of routing event-driven contribution emission through
    `war_contribution`.
    """
    if not actor_nation or not from_controller or actor_nation == from_controller:
        return None
    war_id = _resolve_war_id_for_pair_on_opposite_sides(
        world, actor_nation, from_controller,
    )
    if not war_id:
        return None
    kind = _classify_capture_occupation_kind(
        world,
        region=region,
        actor_nation=actor_nation,
        from_controller=from_controller,
        war_id=war_id,
    )
    if not kind:
        return None
    event_turn = int(turn) if turn is not None else int(
        getattr(world, "current_turn", 0) or 0,
    )
    event_id = (
        f"occupation-{event_turn}-{war_id}-{actor_nation}-{kind}-{region}"
    )
    return accrue_occupation_event(
        world,
        actor_nation=actor_nation,
        region=region,
        occupation_kind=kind,
        from_controller=from_controller,
        to_controller=actor_nation,
        war_id=war_id,
        turn=event_turn,
        event_id=event_id,
    )


# ===========================================================================
# Slice B2 — Support event accrual (spec §9.2 line 614 / line 658)
# ===========================================================================

# Spec §9.2 raw formulas. Stored directly on `episode["support"]` per the
# "raw points" convention shared with `accrue_occupation_event`.
SUPPORT_KINDS: Tuple[str, ...] = (
    "gold", "subsidy", "ap", "manpower", "access", "supply",
)
ACCESS_SUPPLY_CAP: int = 5  # raw points per (war_id, supporter, support_kind)
SUPPORT_SOURCES: Tuple[str, ...] = (
    "treaty_clause", "coalition_subsidy", "command", "scripted_ai",
    "settlement_followup",
)


def _support_raw_points(support_kind: str, value: int) -> int:
    """Spec §9.2 raw point formula, dispatched per support_kind.

    - gold / subsidy: ``value // 100``
    - ap: ``value * 5``
    - manpower: ``value // 500``
    - access / supply: ``1`` per qualifying turn (caller already passes
      ``value=1``); the per-(war_id, supporter, support_kind) cap is applied
      by `accrue_support_event`.
    """
    v = max(0, int(value or 0))
    if support_kind in ("gold", "subsidy"):
        return v // 100
    if support_kind == "ap":
        return v * 5
    if support_kind == "manpower":
        return v // 500
    if support_kind in ("access", "supply"):
        return 1 if v > 0 else 0
    return 0


def accrue_support_event(
    world: Any,
    *,
    war_id: Optional[str],
    supporter: str,
    recipient: str,
    support_kind: str,
    value: int,
    source: str,
    source_detail: str = "",
    turn: Optional[int] = None,
    event_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Accrue one ``war_support_delivered`` event (spec §9.2 line 658).

    Returns the accrual event dict (with `points_accrued` and `attributed`
    booleans) on success or fall-through. Returns ``None`` for malformed
    no-op inputs.

    Filtering rules (spec §9.2 line 674):

    - Both supporter and recipient must be active same-side participants in
      ``war_id`` on the event turn.
    - Either side missing from ``active_participants`` → no accrual.
    - Different sides → no accrual (the spec excludes peace-treaty payments
      between former enemies; their flow is logged but never accrued).
    - ``war_id`` ``None`` → unattributed logging event; returns the event
      dict with ``attributed=False`` and ``points_accrued=0``. The British
      subsidy fallback path uses this branch.

    Dedupe (spec §9.2 line 670):

    - Caller may pass ``event_id``; otherwise a deterministic id is built
      from ``(turn, war_id, supporter, recipient, support_kind, source,
      source_detail)``. Repeat events with the same id no-op.

    Cap (spec §9.2 line 674):

    - ``access`` / ``supply`` raw is clamped per
      ``(war_id, supporter, support_kind)`` to ``ACCESS_SUPPLY_CAP`` (5).
      Re-entry in the same war_id does NOT reset the cap; the counter lives
      on the per-nation record.

    Contribution accrues to the **supporter**, not the recipient — spec
    §9.2 line 585 ("delivered to active same-side participants") describes
    the recipient relationship, not the credit assignment; line 652 ("Britain
    or another paymaster receives support contribution") fixes who earns the
    political standing.
    """
    if not supporter or not recipient or supporter == recipient:
        return None
    if support_kind not in SUPPORT_KINDS:
        return None
    if source not in SUPPORT_SOURCES:
        return None

    raw_points = _support_raw_points(support_kind, value)

    # Unattributed logging path — spec line 676 + impl plan B2 §British
    # subsidy bullet: no accrual, but the event still exists for callers
    # that audit "we paid but couldn't attribute" surfaces.
    if not war_id:
        return {
            "type": "war_support_delivered",
            "war_id": None,
            "supporter": supporter,
            "recipient": recipient,
            "support_kind": support_kind,
            "value": int(value or 0),
            "source": source,
            "source_detail": source_detail or "unattributed_subsidy",
            "turn": int(turn) if turn is not None else None,
            "episode_id": event_id,
            "points_accrued": 0,
            "attributed": False,
        }

    instances = getattr(world, "war_instances", None) or {}
    instance = instances.get(war_id) or {}
    if not instance:
        return None
    side_by_nation = instance.get("side_by_nation") or {}
    s_side = side_by_nation.get(supporter)
    r_side = side_by_nation.get(recipient)
    if not s_side or not r_side or s_side != r_side:
        return None
    active_participants = set(instance.get("active_participants") or [])
    if active_participants:
        if supporter not in active_participants or recipient not in active_participants:
            return None

    if turn is None:
        turn = int(getattr(world, "current_turn", 0) or 0)
    resolved_event_id = event_id or (
        f"support-{int(turn)}-{war_id}-{supporter}-{recipient}-"
        f"{support_kind}-{source}-{source_detail}"
    )

    record = _get_nation_record(world, war_id, supporter)
    if not record:
        return None
    seen = record.setdefault("seen_support_event_ids", [])
    if resolved_event_id in seen:
        return None

    # Access/supply cap applied BEFORE accrual + dedupe append so a capped
    # event neither inflates the bucket nor blocks a future legal event id.
    if support_kind in ("access", "supply") and raw_points > 0:
        caps = record.setdefault("support_caps", {})
        used = int(caps.get(support_kind) or 0)
        remaining = max(0, ACCESS_SUPPLY_CAP - used)
        if remaining <= 0:
            return {
                "type": "war_support_delivered",
                "war_id": war_id,
                "supporter": supporter,
                "recipient": recipient,
                "support_kind": support_kind,
                "value": int(value or 0),
                "source": source,
                "source_detail": source_detail,
                "turn": int(turn),
                "episode_id": resolved_event_id,
                "points_accrued": 0,
                "attributed": True,
                "capped": True,
            }
        raw_points = min(raw_points, remaining)
        caps[support_kind] = used + raw_points

    if raw_points <= 0:
        # Still dedupe so a 0-raw event blocks a duplicate id (e.g. 99-gold
        # one-time payments collapsing into the same `(turn, source_detail)`
        # episode key).
        seen.append(resolved_event_id)
        return {
            "type": "war_support_delivered",
            "war_id": war_id,
            "supporter": supporter,
            "recipient": recipient,
            "support_kind": support_kind,
            "value": int(value or 0),
            "source": source,
            "source_detail": source_detail,
            "turn": int(turn),
            "episode_id": resolved_event_id,
            "points_accrued": 0,
            "attributed": True,
        }

    episode = current_episode(world, war_id, supporter)
    if episode is None:
        return None
    if not _episode_accepts_event_turn(episode, turn):
        return None

    episode["support"] = int(episode.get("support") or 0) + raw_points
    episode["total"] = int(episode.get("total") or 0) + raw_points
    seen.append(resolved_event_id)

    return {
        "type": "war_support_delivered",
        "war_id": war_id,
        "supporter": supporter,
        "recipient": recipient,
        "support_kind": support_kind,
        "value": int(value or 0),
        "source": source,
        "source_detail": source_detail,
        "turn": int(turn),
        "episode_id": resolved_event_id,
        "points_accrued": int(raw_points),
        "attributed": True,
    }


def resolve_treaty_clause_support_war_id(
    world: Any, supporter: str, recipient: str,
) -> Optional[str]:
    """Pick the war_id where supporter and recipient are active same-side allies.

    Used by `_ratify_treaty()` / `_process_treaty_clauses()` to attribute
    treaty-clause support to one specific war when the participants share
    sides in multiple. Tie-break: oldest `created_sequence` wins.

    Returns ``None`` when no such war exists; treaty-clause callers then
    skip emission (a peace-treaty indemnity flowing between former enemies
    is not support).
    """
    if not supporter or not recipient or supporter == recipient:
        return None
    instances = getattr(world, "war_instances", None) or {}
    if not instances:
        return None
    candidates: List[Tuple[int, str]] = []
    for war_id, instance in instances.items():
        if not isinstance(instance, dict):
            continue
        side_by_nation = instance.get("side_by_nation") or {}
        s_side = side_by_nation.get(supporter)
        r_side = side_by_nation.get(recipient)
        if not s_side or not r_side or s_side != r_side:
            continue
        active_participants = set(instance.get("active_participants") or [])
        if active_participants and (
            supporter not in active_participants
            or recipient not in active_participants
        ):
            continue
        seq = int(instance.get("created_sequence") or 0)
        candidates.append((seq, war_id))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][1]


# ===========================================================================
# Slice B2 — British coalition subsidy attribution (impl plan §British subsidy)
# ===========================================================================


def resolve_british_subsidy_war_id(
    world: Any, *, recipient: str,
) -> Tuple[Optional[str], str]:
    """Deterministic war attribution for `_process_british_subsidy()`.

    Per impl plan B2 §British subsidy (mirrored at spec §9.2 line 676):

    1. Unique eligible war (Britain + recipient same-side participants in
       exactly one active war_instance) → return that war_id with detail
       ``"unique_eligible"``.
    2. Multiple eligible wars: prefer one whose `objective_target` matches
       the active coalition's named target → ``"matching_coalition_target"``.
    3. Else, prefer the war with the highest overlap between active
       coalition members and `war_instance.active_participants` →
       ``"highest_overlap"``.
    4. Else, oldest `created_sequence` → ``"oldest_sequence"``.
    5. None of the above (no eligible war) → return ``(None,
       "unattributed_subsidy")``; the caller emits a logging-only event with
       no accrual.
    """
    if not recipient:
        return (None, "unattributed_subsidy")
    instances = getattr(world, "war_instances", None) or {}
    if not instances:
        return (None, "unattributed_subsidy")

    eligible: List[Tuple[int, str, Dict[str, Any]]] = []
    for war_id, instance in instances.items():
        if not isinstance(instance, dict):
            continue
        side_by_nation = instance.get("side_by_nation") or {}
        b_side = side_by_nation.get("Britain")
        r_side = side_by_nation.get(recipient)
        if not b_side or not r_side or b_side != r_side:
            continue
        active_participants = set(instance.get("active_participants") or [])
        if active_participants and (
            "Britain" not in active_participants
            or recipient not in active_participants
        ):
            continue
        seq = int(instance.get("created_sequence") or 0)
        eligible.append((seq, war_id, instance))

    if not eligible:
        return (None, "unattributed_subsidy")
    if len(eligible) == 1:
        return (eligible[0][1], "unique_eligible")

    coalition = getattr(world, "active_coalition", None) or {}
    coalition_target = coalition.get("target", "")
    coalition_members = set(coalition.get("members") or [])

    if coalition_target:
        target_matches = [
            (seq, wid, inst)
            for (seq, wid, inst) in eligible
            if inst.get("objective_target") == coalition_target
        ]
        if len(target_matches) == 1:
            return (target_matches[0][1], "matching_coalition_target")
        if len(target_matches) > 1:
            target_matches.sort()
            return (target_matches[0][1], "matching_coalition_target")

    if coalition_members:
        scored = []
        for seq, wid, inst in eligible:
            ap = set(inst.get("active_participants") or [])
            overlap = len(ap & coalition_members)
            scored.append((-overlap, seq, wid))
        scored.sort()
        if scored and scored[0][0] < 0:  # at least one overlap
            return (scored[0][2], "highest_overlap")

    eligible.sort()
    return (eligible[0][1], "oldest_sequence")


# ===========================================================================
# Slice B3 — Per-turn staying-power accrual (spec §9.2 line 612)
# ===========================================================================

# Spec §9.2 line 612: ``staying_power_raw = min(active_turns, 10) * 5``.
# B3 implements this as a per-turn increment of 5 raw points capped at
# 10 qualifying turns (50 raw points) per episode. The per-turn step is
# idempotent: re-running on the same `current_turn` is a no-op.
STAYING_POWER_PER_TURN: int = 5
STAYING_POWER_TURN_CAP: int = 10
STAYING_POWER_RAW_CAP: int = STAYING_POWER_PER_TURN * STAYING_POWER_TURN_CAP


def accrue_staying_power_for_war(
    world: Any,
    war_id: str,
    *,
    current_turn: int,
) -> Dict[str, int]:
    """Accrue +5 staying-power per active episode for ``war_id`` on ``current_turn``.

    Spec §9.2 line 612 + §7.5: each active participant earns 5 raw points
    per turn for the first 10 qualifying turns of the active episode, then
    the staying-power bucket is frozen for that episode.

    Idempotent per ``(war_id, nation, current_turn)``: an episode whose
    ``last_staying_power_turn`` already covers ``current_turn`` is skipped.
    The cap is per-episode — re-entry creates a new episode and resets the
    counter (spec §7.5: "On re-entry, create a new episode and leave old
    episode totals available only for history panels").

    No-ops when the war instance is unknown / archived. Callers wire this
    via `accrue_staying_power_all_wars(...)` which iterates active
    `world.war_instances` once per `process_diplomacy_turn` call.

    Returns ``{nation: bucket_points_added}`` for tests / debug.
    """
    accrued: Dict[str, int] = {}
    if not war_id:
        return accrued
    instances = getattr(world, "war_instances", None) or {}
    instance = instances.get(war_id)
    if not isinstance(instance, dict):
        return accrued
    if instance.get("ended_turn") is not None:
        return accrued
    for nation, episode in iter_active_episodes(world, war_id):
        last_turn = episode.get("last_staying_power_turn")
        if last_turn is not None and int(last_turn) >= int(current_turn):
            continue
        joined = episode.get("joined_turn")
        if joined is not None and int(current_turn) < int(joined):
            continue
        credited = int(episode.get("staying_power_credited_turns") or 0)
        if credited >= STAYING_POWER_TURN_CAP:
            episode["last_staying_power_turn"] = int(current_turn)
            continue
        episode["staying_power_credited_turns"] = credited + 1
        episode["last_staying_power_turn"] = int(current_turn)
        episode["staying_power"] = (
            int(episode.get("staying_power") or 0) + STAYING_POWER_PER_TURN
        )
        episode["total"] = int(episode.get("total") or 0) + STAYING_POWER_PER_TURN
        accrued[nation] = STAYING_POWER_PER_TURN
    return accrued


def accrue_staying_power_all_wars(
    world: Any,
    *,
    current_turn: int,
) -> Dict[str, Dict[str, int]]:
    """Walk active ``world.war_instances`` once and apply per-turn staying-power.

    Caller (typically `diplomacy.process_diplomacy_turn`) invokes this once
    per turn after event-time accrual and before exit-stamping events
    (spec §9.5 line 740). Episodes that exit later in the same turn still
    capture this turn's staying-power because exits stamp `exited_turn`
    but never overwrite `last_staying_power_turn`.

    Empty-safe at every layer; returns ``{war_id: {nation: points}}``
    snapshot for tests.
    """
    out: Dict[str, Dict[str, int]] = {}
    instances = getattr(world, "war_instances", None) or {}
    if not instances:
        return out
    for war_id, instance in instances.items():
        if not isinstance(instance, dict):
            continue
        if instance.get("ended_turn") is not None:
            continue
        accrued = accrue_staying_power_for_war(
            world, war_id, current_turn=current_turn,
        )
        if accrued:
            out[war_id] = accrued
    return out


# ===========================================================================
# Slice B3 — Archive compaction (spec §9.5 line 178)
# ===========================================================================


def _episode_bucket_total(episode: Mapping[str, Any]) -> int:
    """Sum of the four spec-defined buckets on a single episode dict."""
    return sum(int(episode.get(bucket) or 0) for bucket in ALL_BUCKETS)


def compact_war_contribution_for_archive(
    world: Any,
    war_id: str,
    *,
    archived_turn: int,
) -> Optional[Dict[str, Any]]:
    """Compact ``war_contribution_scores[war_id]`` to per-nation totals (spec §9.5 line 178).

    Called by `archive_terminal_war_instances(...)` once a `war_instance`
    has cleared the 10-turn retention window. The compacted record drops
    per-episode detail and stores per-nation finals plus the war-level
    bucket totals so settlement memory / ledger archive readers can still
    reconstruct shares without keeping the full episode dict alive.

    Output shape (single record per archived war_id), stored under
    ``world.archived_war_contribution_scores[war_id]``:

    ``{
        "war_id": str,
        "archived_turn": int,
        "per_nation_totals": {
            nation: {
                "battle": int, "occupation": int, "staying_power": int,
                "support": int, "total": int, "material_total": int,
                "episode_count": int,
                "first_joined_turn": int, "last_exited_turn": int | None,
            },
            ...
        },
    }``

    Returns the compacted record, or ``None`` when there is no contribution
    record to compact (e.g. an archived war that never accrued anything).
    Removes ``war_contribution_scores[war_id]`` after writing the archive
    entry so the active-store stays in sync with active war_instances.
    """
    store = getattr(world, "war_contribution_scores", None)
    if not isinstance(store, dict):
        return None
    war_dict = store.get(war_id)
    if not isinstance(war_dict, dict) or not war_dict:
        # Nothing to compact, but still drop the empty container so the
        # active store does not retain dangling war_id keys.
        store.pop(war_id, None)
        return None

    archived_container = getattr(world, "archived_war_contribution_scores", None)
    if not isinstance(archived_container, dict):
        archived_container = {}
        setattr(world, "archived_war_contribution_scores", archived_container)

    per_nation_totals: Dict[str, Dict[str, Any]] = {}
    for nation, record in war_dict.items():
        if not isinstance(record, dict):
            continue
        episodes = record.get("episodes") or {}
        bucket_totals: Dict[str, int] = {bucket: 0 for bucket in ALL_BUCKETS}
        first_joined: Optional[int] = None
        last_exited: Optional[int] = None
        episode_count = 0
        for episode in episodes.values():
            if not isinstance(episode, dict):
                continue
            episode_count += 1
            for bucket in ALL_BUCKETS:
                bucket_totals[bucket] += int(episode.get(bucket) or 0)
            joined = episode.get("joined_turn")
            if joined is not None:
                joined_int = int(joined)
                if first_joined is None or joined_int < first_joined:
                    first_joined = joined_int
            exited = episode.get("exited_turn")
            if exited is not None:
                exited_int = int(exited)
                if last_exited is None or exited_int > last_exited:
                    last_exited = exited_int
        material_total = sum(bucket_totals[b] for b in MATERIAL_BUCKETS)
        per_nation_totals[nation] = {
            "battle": bucket_totals["battle"],
            "occupation": bucket_totals["occupation"],
            "staying_power": bucket_totals["staying_power"],
            "support": bucket_totals["support"],
            "total": sum(bucket_totals[b] for b in ALL_BUCKETS),
            "material_total": int(material_total),
            "episode_count": int(episode_count),
            "first_joined_turn": int(first_joined) if first_joined is not None else None,
            "last_exited_turn": int(last_exited) if last_exited is not None else None,
            "historical_total": int(record.get("historical_total") or 0),
        }

    compacted_record = {
        "war_id": war_id,
        "archived_turn": int(archived_turn),
        "per_nation_totals": per_nation_totals,
    }
    archived_container[war_id] = compacted_record
    store.pop(war_id, None)
    return compacted_record


__all__ = [
    "ACCESS_SUPPLY_CAP",
    "ALL_BUCKETS",
    "BENEFICIARY_ONLY",
    "BUCKET_WEIGHTS",
    "CONSULT",
    "CONSULT_MATERIAL_SHARE_THRESHOLD",
    "DISPATCH_LIGHT_THRESHOLD",
    "DISPATCH_SEAT_THRESHOLD",
    "MATERIAL_BUCKETS",
    "NO_STANDING",
    "OCCUPATION_KINDS",
    "OCCUPATION_POINTS",
    "SEAT",
    "SEAT_MATERIAL_SHARE_THRESHOLD",
    "STAYING_POWER_PER_TURN",
    "STAYING_POWER_RAW_CAP",
    "STAYING_POWER_TURN_CAP",
    "SUPPORT_KINDS",
    "SUPPORT_SOURCES",
    "accrue_battle_contribution",
    "accrue_occupation_event",
    "accrue_staying_power_all_wars",
    "accrue_staying_power_for_war",
    "accrue_support_event",
    "adapt_legacy_battle_record",
    "canonical_episode_id",
    "classify_standing",
    "close_episode_for_exit",
    "compact_war_contribution_for_archive",
    "compute_standing_inputs",
    "contribution_share",
    "current_episode",
    "current_episode_material_total",
    "current_episode_total",
    "detect_battle_theater",
    "emit_capture_occupation_event",
    "iter_active_episodes",
    "material_contribution_points",
    "material_contribution_share",
    "open_episode",
    "resolve_british_subsidy_war_id",
    "resolve_treaty_clause_support_war_id",
    "standing_for_participant",
    "total_side_current_episode_contribution",
    "total_side_material_contribution",
]
