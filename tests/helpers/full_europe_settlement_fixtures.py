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


# ---------------------------------------------------------------------------
# Slice A3: merge / multi-objective / side-scoped leader fixtures
# ---------------------------------------------------------------------------


def build_three_instance_chain_merge_fixture(world: WorldState) -> Dict[str, Dict]:
    """Three active war_instances connected via shared participants.

    Used by Slice A3 merge tests to prove transitive connected-component
    merge collapses to one survivor. Each pair of adjacent instances
    shares a participant so the connected component contains all three:

    - war_A: France(attackers) vs Austria(defenders)
    - war_B: Austria(defenders) vs Prussia(attackers)  -- shares Austria with A
    - war_C: Prussia(attackers) vs Russia(defenders)   -- shares Prussia with B

    A merge seeded with any one war_id must walk to all three. After the
    merge:
      - attackers contain {France, Prussia}
      - defenders contain {Austria, Russia}
      - no nation lands on both sides (validated)
    """
    install_synthetic_active_roster(
        world, ["France", "Austria", "Prussia", "Russia"]
    )
    inserted: Dict[str, Dict] = {}

    war_a_id = _allocate_war_id(world)
    inserted[war_a_id] = make_synthetic_war_instance(
        war_a_id,
        attackers=["France"],
        defenders=["Austria"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=int(world.current_turn),
        created_sequence=_current_sequence(world),
    )
    _stamp_war_pairs_in_diplomatic_states(world, inserted[war_a_id])

    war_b_id = _allocate_war_id(world)
    inserted[war_b_id] = make_synthetic_war_instance(
        war_b_id,
        attackers=["Prussia"],
        defenders=["Austria"],
        attacker_leader="Prussia",
        defender_leader="Austria",
        created_turn=int(world.current_turn),
        created_sequence=_current_sequence(world),
    )
    _stamp_war_pairs_in_diplomatic_states(world, inserted[war_b_id])

    war_c_id = _allocate_war_id(world)
    inserted[war_c_id] = make_synthetic_war_instance(
        war_c_id,
        attackers=["Prussia"],
        defenders=["Russia"],
        attacker_leader="Prussia",
        defender_leader="Russia",
        created_turn=int(world.current_turn),
        created_sequence=_current_sequence(world),
    )
    _stamp_war_pairs_in_diplomatic_states(world, inserted[war_c_id])

    world.war_instances.update(inserted)
    world.invalidate_war_instance_indexes()
    return inserted


def build_multi_objective_merge_fixture(world: WorldState) -> Dict[str, Dict]:
    """Two wars with DIFFERENT WPS objective_keys whose participants overlap.

    A3 spec §7.2 line 333: a merged war_instance keeps every absorbed
    instance's WPS objective references as independent contexts (union,
    never one dominant).

    - war_A: France(attackers) vs Austria(defenders); objective_keys=[france_austria]
    - war_B: France(attackers) vs Prussia(defenders); objective_keys=[france_prussia]

    France is shared, so the connected component contains both. Sides are
    compatible (France=attackers in both), so merge succeeds. The survivor
    must keep BOTH objective_keys.
    """
    install_synthetic_active_roster(world, ["France", "Austria", "Prussia"])
    inserted: Dict[str, Dict] = {}

    war_a_id = _allocate_war_id(world)
    instance_a = make_synthetic_war_instance(
        war_a_id,
        attackers=["France"],
        defenders=["Austria"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=int(world.current_turn),
        created_sequence=_current_sequence(world),
    )
    instance_a["objective_keys"] = [instance_a["origin_diplo_key"]]
    inserted[war_a_id] = instance_a
    _stamp_war_pairs_in_diplomatic_states(world, instance_a)

    war_b_id = _allocate_war_id(world)
    instance_b = make_synthetic_war_instance(
        war_b_id,
        attackers=["France"],
        defenders=["Prussia"],
        attacker_leader="France",
        defender_leader="Prussia",
        created_turn=int(world.current_turn),
        created_sequence=_current_sequence(world),
    )
    instance_b["objective_keys"] = [instance_b["origin_diplo_key"]]
    inserted[war_b_id] = instance_b
    _stamp_war_pairs_in_diplomatic_states(world, instance_b)

    world.war_instances.update(inserted)
    world.invalidate_war_instance_indexes()
    return inserted


def build_side_scoped_leader_source_fixture(
    world: WorldState,
    *,
    attacker_source: str,
    defender_source: str,
) -> Dict[str, Dict]:
    """One active war_instance with explicit side-scoped leader sources.

    A3 spec §7.4 + impl plan line 135: each side decides its leader using
    its own `leader_source_by_side[side]` source metadata. Coalition-source
    sides go through `select_coalition_leader`; non-coalition sources use
    `war_leader_score()`.

    `attacker_source` / `defender_source` may be one of:
        "originator", "origin_target", "ally_cascade", "coalition_leader",
        "scripted".
    """
    install_synthetic_active_roster(
        world, ["France", "Austria", "Prussia", "Russia"]
    )
    war_id = _allocate_war_id(world)
    instance = make_synthetic_war_instance(
        war_id,
        attackers=["France", "Bavaria"],
        defenders=["Austria", "Prussia"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=int(world.current_turn),
        created_sequence=_current_sequence(world),
    )
    instance["leader_source_by_side"] = {
        "attackers": attacker_source,
        "defenders": defender_source,
    }
    _stamp_war_pairs_in_diplomatic_states(world, instance)
    world.war_instances[war_id] = instance
    world.invalidate_war_instance_indexes()
    return {war_id: instance}


# ---------------------------------------------------------------------------
# Slice B3: lifecycle / per-turn staying-power / archive retention fixtures
# ---------------------------------------------------------------------------


def build_three_theater_full_europe_fixture(
    world: WorldState,
) -> Dict[str, Dict]:
    """Single 6+ participant war spanning three distant theaters.

    Spec §9.4 line 717 + impl plan B3 gate: a coalition war with marshals
    on opposite ends of Europe must NOT credit a same-side participant
    fighting on a different front for events on this front. This fixture
    seats the canonical roster across three theaters (German, Iberian,
    Russian) and returns the war_id so per-theater contribution tests can
    drive battle / occupation events without polluting the active-roster
    install pattern used by smaller B1/B2 tests.

    Returns ``{war_id: instance}``.
    """
    install_synthetic_active_roster(
        world,
        [
            "France", "Saxony", "Bavaria",      # German theater (attackers)
            "Spain", "Portugal",                # Iberian theater (defenders)
            "Russia", "Prussia",                # Russian / Northern theater (defenders)
            "Austria",                          # German theater (defenders)
            "Britain",                          # Iberian / strategic ally (defenders)
        ],
    )
    war_id = _allocate_war_id(world)
    instance = make_synthetic_war_instance(
        war_id,
        attackers=["France", "Saxony", "Bavaria"],
        defenders=["Austria", "Russia", "Prussia", "Britain", "Spain", "Portugal"],
        attacker_leader="France",
        defender_leader="Russia",
        created_turn=int(world.current_turn),
        created_sequence=_current_sequence(world),
    )
    _stamp_war_pairs_in_diplomatic_states(world, instance)
    world.war_instances[war_id] = instance
    world.invalidate_war_instance_indexes()
    return {war_id: instance}


def build_concurrent_war_lifecycle_fixture(
    world: WorldState,
) -> Tuple[str, str]:
    """One nation participating in TWO independent active war_instances.

    Spec §9.5 line 738 + impl plan B3 gate: a nation active in two
    concurrent ``war_instance`` records accrues staying power, support, and
    current-episode totals independently per ``war_id``. Only a merge
    transaction rewrites those records together — and a merge is impossible
    here because the two wars share zero participants beyond the bridge.

    Layout (Russia is the bridge nation):
      - war_X: France(attackers, leader) vs Russia(defenders, leader)
      - war_Y: Russia(attackers, leader) vs Ottoman(defenders, leader)

    Returns ``(war_x_id, war_y_id)``.
    """
    install_synthetic_active_roster(
        world, ["France", "Russia", "Ottoman"]
    )

    war_x_id = _allocate_war_id(world)
    instance_x = make_synthetic_war_instance(
        war_x_id,
        attackers=["France"],
        defenders=["Russia"],
        attacker_leader="France",
        defender_leader="Russia",
        created_turn=int(world.current_turn),
        created_sequence=_current_sequence(world),
    )
    _stamp_war_pairs_in_diplomatic_states(world, instance_x)
    world.war_instances[war_x_id] = instance_x

    war_y_id = _allocate_war_id(world)
    instance_y = make_synthetic_war_instance(
        war_y_id,
        attackers=["Russia"],
        defenders=["Ottoman"],
        attacker_leader="Russia",
        defender_leader="Ottoman",
        created_turn=int(world.current_turn),
        created_sequence=_current_sequence(world),
    )
    _stamp_war_pairs_in_diplomatic_states(world, instance_y)
    world.war_instances[war_y_id] = instance_y

    world.invalidate_war_instance_indexes()
    return war_x_id, war_y_id


def build_archive_retention_fixture(
    world: WorldState,
    *,
    ended_turn: int,
    current_turn: int,
) -> str:
    """Single ended ``war_instance`` ready to test the 10-turn retention boundary.

    Spec §7.5 / §9.5 line 178: ``war_contribution_scores[war_id]`` survives
    until ``current_turn - ended_turn >= 10``, then compacts to per-nation
    finals on archive. The fixture creates one war between France and
    Austria that ended on ``ended_turn`` and seeds ``current_turn`` so
    retention math is deterministic.

    Returns the ``war_id`` of the terminal instance. The caller is
    responsible for seeding contribution episodes (``open_episode`` etc.)
    against the returned war_id before exercising
    ``archive_terminal_war_instances``.
    """
    install_synthetic_active_roster(world, ["France", "Austria"])
    war_id = _allocate_war_id(world)
    instance = make_synthetic_war_instance(
        war_id,
        attackers=["France"],
        defenders=["Austria"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=int(ended_turn) - 5,  # arbitrary pre-end window
        created_sequence=_current_sequence(world),
    )
    instance["ended_turn"] = int(ended_turn)
    instance["end_reason"] = "all_pairs_resolved"
    # Move the bilateral pair into the resolved bucket so the invariant
    # walker does not flag it as an active-but-WAR pair.
    pair = "|".join(sorted(("France", "Austria")))
    instance["active_diplo_keys"] = []
    instance["resolved_diplo_keys"] = [pair]
    if pair in (instance.get("diplo_key_meta") or {}):
        instance["diplo_key_meta"][pair]["pair_status"] = "resolved"
        instance["diplo_key_meta"][pair]["resolved_turn"] = int(ended_turn)
    # Drop the live-WAR diplomatic_states stamp the make_synthetic helper
    # would have set: an ended war should not look like an active WAR pair
    # to the invariant assertion.
    world.diplomatic_states.pop(pair, None)
    world.war_instances[war_id] = instance
    world.current_turn = int(current_turn)
    world.invalidate_war_instance_indexes()
    return war_id
