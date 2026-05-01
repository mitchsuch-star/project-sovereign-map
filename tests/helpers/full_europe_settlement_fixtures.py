"""Synthetic full-Europe settlement fixtures (Slice A1 foundation).

`WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` §"Full-Europe
Test Fixture Contract" requires synthetic fixtures because the live map
has fewer nations / regions than the spec target. A1 only needs the
foundation-level fixtures: the canonical 13-nation roster and a
20-active-`war_instance` cache/index probe.

A2/A3/B/C/D will extend this module — A1 deliberately keeps fixtures
narrow so the foundation gate stays foundation-only.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from backend.models.world_state import WorldState


# Canonical 13 DG-1 nation ids per spec §0 / plan §"Full-Europe Test
# Fixture Contract". Display names (`Ottoman Empire`, `Naples/Two Sicilies`)
# are aliases — fixtures must use the internal ids only.
CANONICAL_13_NATIONS: Tuple[str, ...] = (
    "France",
    "Britain",
    "Austria",
    "Prussia",
    "Russia",
    "Spain",
    "Ottoman",
    "Sweden",
    "Naples",
    "Bavaria",
    "Saxony",
    "Portugal",
    "Denmark-Norway",
)


def make_synthetic_war_instance(
    war_id: str,
    *,
    attackers: List[str],
    defenders: List[str],
    attacker_leader: str,
    defender_leader: str,
    created_turn: int = 1,
    created_sequence: int = 1,
) -> Dict:
    """Build a minimal `war_instance` dict honoring spec §7.1 shape.

    Slice A1 does not exercise objective_keys, war_bargains, or
    participant_meta beyond `joined_turn`, so this builder keeps those
    fields at the spec-default empty values. Index/cache helpers under
    test only need `attacker_leader`, `defender_leader`,
    `active_participants`, `active_diplo_keys`, `diplo_key_meta`, and
    `ended_turn` — every field is still populated for shape-completeness.
    """
    if attacker_leader not in attackers:
        raise ValueError(
            f"attacker_leader {attacker_leader!r} must be in attackers list"
        )
    if defender_leader not in defenders:
        raise ValueError(
            f"defender_leader {defender_leader!r} must be in defenders list"
        )

    overlap = set(attackers) & set(defenders)
    if overlap:
        raise ValueError(
            f"attackers and defenders overlap on {sorted(overlap)} "
            "(would violate side-disjointness invariant)"
        )

    side_by_nation = {nation: "attackers" for nation in attackers}
    side_by_nation.update({nation: "defenders" for nation in defenders})

    active_pairs: List[str] = []
    diplo_key_meta: Dict[str, Dict] = {}
    for atk in attackers:
        for dfd in defenders:
            pair = "|".join(sorted((atk, dfd)))
            active_pairs.append(pair)
            diplo_key_meta[pair] = {
                "attacker": atk,
                "defender": dfd,
                "joined_turn": created_turn,
                "pair_status": "war",
                "resolved_turn": None,
            }

    participant_meta = {
        nation: {
            "side": side_by_nation[nation],
            "joined_turn": created_turn,
            "exited_turn": None,
            "entry_path": "originator" if nation in (attacker_leader, defender_leader) else "ally_cascade",
        }
        for nation in attackers + defenders
    }

    origin_pair = "|".join(sorted((attacker_leader, defender_leader)))

    return {
        "war_id": war_id,
        "created_turn": int(created_turn),
        "created_sequence": int(created_sequence),
        "originator": attacker_leader,
        "origin_target": defender_leader,
        "origin_diplo_key": origin_pair,
        "objective_keys": [origin_pair],
        "active_diplo_keys": active_pairs,
        "resolved_diplo_keys": [],
        "diplo_key_meta": diplo_key_meta,
        "attacker_leader": attacker_leader,
        "defender_leader": defender_leader,
        "leader_source_by_side": {
            "attackers": "originator",
            "defenders": "origin_target",
        },
        "attackers": list(attackers),
        "defenders": list(defenders),
        "side_by_nation": side_by_nation,
        "active_participants": list(attackers + defenders),
        "participant_meta": participant_meta,
        "separate_peaced": [],
        "war_bargains": [],
        "ended_turn": None,
        "end_reason": None,
    }


def install_synthetic_active_roster(world: WorldState, nations: List[str]) -> None:
    """Extend the fixture world's active roster with synthetic nations.

    Per the plan: "Tests that need active nations must either extend the
    fixture world's active roster (`world.enemy_nations` / runtime nation
    setup) before attaching synthetic regions/controllers, or monkeypatch
    the specific active-nation helper under test." This helper extends
    `world.enemy_nations` with any synthetic nation not already in the
    runtime, then invalidates active-nation / nation-region caches so
    later assertions see the updated roster.
    """
    for nation in nations:
        if nation == world.player_nation:
            continue
        if nation not in world.enemy_nations:
            world.enemy_nations.append(nation)
    world.invalidate_active_nations_cache()


def build_full_europe_war_instance_fixture(
    world: WorldState,
    *,
    target_active_count: int = 20,
    coalition_side_min_size: int = 6,
) -> Dict[str, Dict]:
    """Populate `world.war_instances` with `target_active_count` active records.

    Returns the inserted instances keyed by `war_id`. The fixture covers:

    - The canonical 13-nation roster as participants.
    - A 6+ participant coalition side (anchored on France-attackers vs
      Russia-led defenders).
    - `target_active_count` active records, each with monotonic
      `created_sequence` matching `world.next_war_instance_id`.
    - Disjoint pair-key ownership across instances: each instance uses
      its own bilateral attacker / defender pairings, so the
      `assert_war_instance_invariants` helper finds zero violations on a
      clean fixture.

    The fixture also stamps `diplomatic_states[pair] = "WAR"` for every
    active pair so the invariant's "every WAR pair owned by exactly one
    active instance" check has data to traverse.

    A side-effect: invalidates `war_instances_by_*` indexes so the next
    read rebuilds against the new fixture state.
    """
    if target_active_count < 1:
        raise ValueError("target_active_count must be >= 1")

    install_synthetic_active_roster(world, list(CANONICAL_13_NATIONS))

    inserted: Dict[str, Dict] = {}

    # First instance: 6+ participant coalition side per plan contract.
    big_attackers = ["France", "Saxony", "Bavaria", "Naples", "Spain"]
    big_defenders = [
        "Russia",
        "Austria",
        "Prussia",
        "Britain",
        "Sweden",
        "Portugal",
    ]
    big_war_id = _allocate_war_id(world)
    inserted[big_war_id] = make_synthetic_war_instance(
        big_war_id,
        attackers=big_attackers,
        defenders=big_defenders,
        attacker_leader="France",
        defender_leader="Russia",
        created_turn=int(world.current_turn),
        created_sequence=_current_sequence(world),
    )
    _stamp_war_pairs_in_diplomatic_states(world, inserted[big_war_id])

    # Reserve the remaining slots as smaller bilateral wars across the
    # canonical roster. Use disjoint pair keys: rotate (attacker, defender)
    # pairings so no pair collides with an instance already inserted.
    rotation = [
        ("France", "Britain"),
        ("Austria", "Saxony"),
        ("Prussia", "Denmark-Norway"),
        ("Russia", "Ottoman"),
        ("Sweden", "Russia"),
        ("Britain", "Spain"),
        ("Naples", "Austria"),
        ("Bavaria", "Prussia"),
        ("Portugal", "Spain"),
        ("Denmark-Norway", "Sweden"),
        ("Ottoman", "Russia"),
        ("Saxony", "Russia"),
        ("Naples", "Britain"),
        ("Bavaria", "Austria"),
        ("Portugal", "Britain"),
        ("Denmark-Norway", "Prussia"),
        ("Ottoman", "Austria"),
        ("Saxony", "Britain"),
        ("Spain", "Russia"),
    ]

    seen_pairs: set = set(
        pair
        for instance in inserted.values()
        for pair in instance["active_diplo_keys"]
    )

    rotation_index = 0
    while len(inserted) < target_active_count:
        attacker, defender = rotation[rotation_index % len(rotation)]
        rotation_index += 1
        # Skip rotation entries that would collide with existing pair keys
        # (the big coalition war already covers many of them); fabricate
        # a unique synthetic pair when rotation runs out of fresh entries.
        pair_key = "|".join(sorted((attacker, defender)))
        if pair_key in seen_pairs:
            # Fabricate a fresh synthetic pair using a new attacker rotation.
            attacker, defender = _next_unused_pair(seen_pairs)
            pair_key = "|".join(sorted((attacker, defender)))

        seen_pairs.add(pair_key)
        war_id = _allocate_war_id(world)
        inserted[war_id] = make_synthetic_war_instance(
            war_id,
            attackers=[attacker],
            defenders=[defender],
            attacker_leader=attacker,
            defender_leader=defender,
            created_turn=int(world.current_turn),
            created_sequence=_current_sequence(world),
        )
        _stamp_war_pairs_in_diplomatic_states(world, inserted[war_id])

    # Verify the 6+ participant contract before returning.
    big_side_size = max(
        len(inserted[big_war_id]["attackers"]),
        len(inserted[big_war_id]["defenders"]),
    )
    if big_side_size < coalition_side_min_size:
        raise AssertionError(
            f"coalition side has {big_side_size} participants, "
            f"need >= {coalition_side_min_size}"
        )

    world.war_instances.update(inserted)
    world.invalidate_war_instance_indexes()
    return inserted


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _allocate_war_id(world: WorldState) -> str:
    """Allocate the next war_id and increment `next_war_instance_id`.

    Mirrors the spec §7.2 allocator semantics so fixtures exercise the same
    monotonic counter A2 will use in production paths.
    """
    war_id = f"war_{world.next_war_instance_id}"
    world.next_war_instance_id += 1
    return war_id


def _current_sequence(world: WorldState) -> int:
    """Return the sequence integer corresponding to the most recent war_id.

    `_allocate_war_id` already incremented the counter, so the caller's
    `created_sequence` is `next_war_instance_id - 1`.
    """
    return int(world.next_war_instance_id) - 1


def _stamp_war_pairs_in_diplomatic_states(world: WorldState, instance: Dict) -> None:
    """Ensure every `pair_status='war'` pair appears as `WAR` in `diplomatic_states`.

    The invariant helper requires alignment between active war_instance
    ownership and live `diplomatic_states`. Synthetic fixtures bypass the
    normal declaration path, so this helper writes the pair states
    directly. Resolved/armistice fixtures are not exercised in A1.
    """
    for pair, meta in (instance.get("diplo_key_meta") or {}).items():
        if meta.get("pair_status") == "war":
            world.diplomatic_states[pair] = "WAR"


def _next_unused_pair(seen_pairs: set) -> Tuple[str, str]:
    """Fabricate a fresh attacker/defender pair across the canonical roster.

    Walks the canonical roster as a square cross product, returning the
    first ordered pair whose sorted key is not already in `seen_pairs`.
    Used as a fallback when the rotation list above is exhausted.
    """
    for atk in CANONICAL_13_NATIONS:
        for dfd in CANONICAL_13_NATIONS:
            if atk == dfd:
                continue
            pair_key = "|".join(sorted((atk, dfd)))
            if pair_key not in seen_pairs:
                return atk, dfd
    raise RuntimeError(
        "exhausted canonical 13-nation pair space; raise CANONICAL_13_NATIONS "
        "or relax target_active_count"
    )
