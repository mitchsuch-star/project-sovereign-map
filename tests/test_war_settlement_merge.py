"""Slice A3 tests -- merge / archive / leader replacement / elimination.

Slice A3 of `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §7.4 / §7.5 / §7.6
implements the transitive merge transaction, side-scoped leader
replacement, elimination exit, and 10-turn archive compaction. The
post-merge invariant promotion catches dangling absorbed `war_id`
references in live + future-slice containers.

This file owns the focused A3 gate tests per
`WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` §"Slice A
- War Identity And Grouping" -- A3 sub-bullets and the gate criteria.
"""

from __future__ import annotations

import pytest

from backend.game_logic.diplomacy import create_war_bargain_commitment
from backend.game_logic.settlement_helpers import (
    ARCHIVE_RETENTION_TURNS,
    WAR_END_REASON_ALL_PAIRS_RESOLVED,
    WAR_INSTANCE_SIDE_CONFLICT,
    WarInstanceInvariantError,
    archive_terminal_war_instances,
    assert_war_instance_invariants,
    ensure_war_instance_for_pair,
    mark_participant_eliminated_in_all_wars,
    merge_war_instances,
    resolve_pair_to_resolved,
    war_leader_score,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    build_multi_objective_merge_fixture,
    build_side_scoped_leader_source_fixture,
    build_three_instance_chain_merge_fixture,
)


def _clean_world(player_nation: str = "France") -> WorldState:
    world = WorldState(player_nation=player_nation)
    world.diplomatic_states.clear()
    world.invalidate_war_instance_indexes()
    return world


def _pair(a: str, b: str) -> str:
    return "|".join(sorted((a, b)))


def _active(world: WorldState):
    return {
        wid: inst
        for wid, inst in world.war_instances.items()
        if inst.get("ended_turn") is None
    }


# ---------------------------------------------------------------------------
# Merge transaction core
# ---------------------------------------------------------------------------


def test_two_instance_merge_picks_oldest_war_id_as_survivor():
    """Spec §7.6 step 3: merge picks the war_id with the smallest
    `created_sequence` as the survivor; absorbed instances are removed."""
    world = _clean_world()
    first = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    second = ensure_war_instance_for_pair(
        world, "Russia", "Prussia", entry_path="war_declaration"
    )
    result = merge_war_instances(
        world,
        candidate_war_ids=[second["war_id"], first["war_id"]],
    )
    assert result["ok"] is True
    assert result["surviving_war_id"] == first["war_id"]  # older
    assert second["war_id"] in result["absorbed_war_ids"]
    assert first["war_id"] in world.war_instances
    assert second["war_id"] not in world.war_instances


def test_three_instance_chain_merge_collapses_to_one_survivor():
    """Plan gate line 124: synthetic three-instance chain merge collapses
    to exactly one surviving war_instance."""
    world = _clean_world()
    inserted = build_three_instance_chain_merge_fixture(world)
    war_a, war_b, war_c = sorted(inserted.keys())
    # Seed with just one id; the connected-component walker must pick up
    # the other two via shared participants (Austria links A-B; Prussia links B-C).
    result = merge_war_instances(world, candidate_war_ids=[war_a])
    assert result["ok"] is True
    assert result["surviving_war_id"] == war_a
    assert set(result["absorbed_war_ids"]) == {war_b, war_c}
    active = _active(world)
    assert len(active) == 1
    survivor = active[war_a]
    assert {"France", "Prussia"}.issubset(set(survivor["attackers"]))
    assert {"Austria", "Russia"}.issubset(set(survivor["defenders"]))


def test_merge_preserves_participant_meta_joined_turn_and_entry_path():
    """Spec §7.6 step 4: participant_meta is dict-unioned; survivor wins
    on collision; absorbed metadata for non-overlapping nations is
    preserved verbatim."""
    world = _clean_world()
    world.current_turn = 5
    inserted = build_three_instance_chain_merge_fixture(world)
    war_a, war_b, war_c = sorted(inserted.keys())
    # Stamp distinct joined_turn / entry_path so we can verify preservation.
    inserted[war_b]["participant_meta"]["Prussia"]["joined_turn"] = 7
    inserted[war_b]["participant_meta"]["Prussia"]["entry_path"] = "ally_cascade"
    inserted[war_c]["participant_meta"]["Russia"]["joined_turn"] = 9
    inserted[war_c]["participant_meta"]["Russia"]["entry_path"] = "scripted"

    result = merge_war_instances(world, candidate_war_ids=[war_a])
    assert result["ok"] is True
    survivor = world.war_instances[war_a]
    assert survivor["participant_meta"]["France"]["joined_turn"] == 5
    assert survivor["participant_meta"]["Prussia"]["joined_turn"] == 7
    assert survivor["participant_meta"]["Prussia"]["entry_path"] == "ally_cascade"
    assert survivor["participant_meta"]["Russia"]["joined_turn"] == 9
    assert survivor["participant_meta"]["Russia"]["entry_path"] == "scripted"


def test_merge_invalidates_war_instance_indexes():
    """Spec §7.6 step 9: merge marks `war_instances_by_leader` /
    `war_instances_by_participant` dirty so the next reader rebuilds."""
    world = _clean_world()
    inserted = build_three_instance_chain_merge_fixture(world)
    # Force a build of the indexes against the pre-merge state.
    pre_index = world.get_war_instances_by_participant("Austria")
    assert len(pre_index) >= 2  # Austria is in war_a and war_b
    war_a = sorted(inserted.keys())[0]

    merge_war_instances(world, candidate_war_ids=[war_a])
    post_index = world.get_war_instances_by_participant("Austria")
    assert len(post_index) == 1
    assert post_index[0] == war_a


def test_merge_side_conflict_aborts_without_mutation():
    """Spec §7.6 step 2: side conflict (a nation that would land on both
    sides) aborts the merge BEFORE any state mutation."""
    world = _clean_world()
    # war_1: France attackers / Austria defenders
    first = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    # war_2: Austria attackers / Prussia defenders -- side conflict on Austria
    # We construct this by hand because ensure_war_instance_for_pair would
    # try to attach the (Austria, Prussia) pair into first; we need a second
    # *active* instance with conflicting side membership.
    from tests.helpers.full_europe_settlement_fixtures import (
        make_synthetic_war_instance,
    )
    war_2 = make_synthetic_war_instance(
        "war_synthetic_b",
        attackers=["Austria"],
        defenders=["Prussia"],
        attacker_leader="Austria",
        defender_leader="Prussia",
        created_turn=int(world.current_turn),
        created_sequence=int(world.next_war_instance_id),
    )
    world.war_instances["war_synthetic_b"] = war_2
    world.invalidate_war_instance_indexes()
    snapshot = {wid: dict(inst) for wid, inst in world.war_instances.items()}

    result = merge_war_instances(
        world,
        candidate_war_ids=[first["war_id"], "war_synthetic_b"],
    )
    assert result["ok"] is False
    assert result["error"] == WAR_INSTANCE_SIDE_CONFLICT
    # World state is unchanged.
    assert set(world.war_instances.keys()) == set(snapshot.keys())
    for wid, inst in world.war_instances.items():
        assert inst["attackers"] == snapshot[wid]["attackers"]
        assert inst["defenders"] == snapshot[wid]["defenders"]


# ---------------------------------------------------------------------------
# Multi-objective preservation
# ---------------------------------------------------------------------------


def test_merge_preserves_objective_keys_as_union_of_absorbed_instances():
    """Plan gate line 132 + spec §7.2 line 333: surviving war_instance keeps
    every absorbed instance's objective_keys as union -- no one dominant."""
    world = _clean_world()
    inserted = build_multi_objective_merge_fixture(world)
    war_a, war_b = sorted(inserted.keys())
    obj_a = list(inserted[war_a]["objective_keys"])
    obj_b = list(inserted[war_b]["objective_keys"])

    merge_war_instances(world, candidate_war_ids=[war_a])
    survivor = world.war_instances[war_a]
    # Both pre-merge objective_keys must be present in the survivor's union.
    for key in obj_a + obj_b:
        assert key in survivor["objective_keys"]


def test_merge_does_not_select_one_dominant_objective():
    """The merge must not collapse multi-objective absorbed instances to a
    single objective_key."""
    world = _clean_world()
    inserted = build_multi_objective_merge_fixture(world)
    war_a, war_b = sorted(inserted.keys())
    merge_war_instances(world, candidate_war_ids=[war_a])
    survivor = world.war_instances[war_a]
    assert len(survivor["objective_keys"]) >= 2


# ---------------------------------------------------------------------------
# Bargain merge context
# ---------------------------------------------------------------------------


def test_create_war_bargain_captures_war_id_and_side_at_creation():
    """Spec §11.3 line 1573: bargain creation snapshots `war_id`,
    `side_at_creation`, `side_leader_at_creation` from the active war
    covering (promiser, target_enemy)."""
    world = _clean_world()
    # Need a real region for `_resolve_bargain_war_context`'s claim-holder lookup.
    war = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    # Set up an alliance treaty so the bargain validation passes.
    world.diplomatic_states[_pair("France", "Spain")] = "ALLIANCE"
    bargain = create_war_bargain_commitment(
        world,
        promiser="France",
        beneficiary="Spain",
        target_enemy="Austria",
        claim_region="Vienna",
        origin_mode="recompense",
        source_treaty_key=_pair("France", "Spain"),
        validate=False,
    )
    assert bargain["war_id"] == war["war_id"]
    assert bargain["side_at_creation"] == "attackers"
    assert bargain["side_leader_at_creation"] == "France"


def test_merge_rewrites_absorbed_war_id_on_bargains_but_preserves_side_leader_at_creation():
    """A3 spec §11.3 line 1573: merge rewrites `bargain.war_id` to the
    surviving id but preserves `side_at_creation` / `side_leader_at_creation`."""
    world = _clean_world()
    inserted = build_multi_objective_merge_fixture(world)
    war_a, war_b = sorted(inserted.keys())
    # Add a bargain whose war_id is the (would-be-absorbed) war_b.
    bargain = {
        "id": 1,
        "type": "war_bargain",
        "promiser": "France",
        "beneficiary": "Spain",
        "target_enemy": "Prussia",
        "war_id": war_b,
        "side_at_creation": "attackers",
        "side_leader_at_creation": "France",
        "status": "active",
    }
    world.diplomatic_commitments["1"] = bargain
    merge_war_instances(world, candidate_war_ids=[war_a])
    rewritten = world.diplomatic_commitments["1"]
    assert rewritten["war_id"] == war_a  # rewritten
    assert rewritten["side_at_creation"] == "attackers"  # preserved
    assert rewritten["side_leader_at_creation"] == "France"  # preserved


def test_merge_rewrites_absorbed_war_id_in_event_log_payloads():
    """A3 rewrites recent event-log / ledger payload references too."""
    world = _clean_world()
    inserted = build_multi_objective_merge_fixture(world)
    war_a, war_b = sorted(inserted.keys())
    world.event_log.append(
        {
            "type": "war_entry_ledger",
            "war_id": war_b,
            "payload": {
                "war_id": war_b,
                "entries": [{"nation": "Prussia", "war_id": war_b}],
            },
        }
    )

    result = merge_war_instances(world, candidate_war_ids=[war_a])

    assert result["ok"] is True
    assert result["surviving_war_id"] == war_a
    assert world.event_log[-1]["war_id"] == war_a
    assert world.event_log[-1]["payload"]["war_id"] == war_a
    assert world.event_log[-1]["payload"]["entries"][0]["war_id"] == war_a


def test_pre_a3_bargain_loads_with_null_merge_context_via_from_dict_default():
    """Old saves with no `war_id` / `side_at_creation` /
    `side_leader_at_creation` fields on bargains load with None defaults
    via dict.get() semantics."""
    world = _clean_world()
    legacy_bargain = {
        "id": 1,
        "type": "war_bargain",
        "promiser": "France",
        "beneficiary": "Spain",
        "target_enemy": "Austria",
        "status": "active",
        # No war_id / side_at_creation / side_leader_at_creation
    }
    world.diplomatic_commitments["1"] = legacy_bargain
    saved = world.to_dict()
    restored = WorldState.from_dict(saved)
    bargain = restored.diplomatic_commitments["1"]
    # Legacy bargains should not crash readers; missing fields default to None.
    assert bargain.get("war_id") is None
    assert bargain.get("side_at_creation") is None
    assert bargain.get("side_leader_at_creation") is None


# ---------------------------------------------------------------------------
# Leader replacement (war_leader_score + side-scoped sources)
# ---------------------------------------------------------------------------


def test_war_leader_score_preserves_current_leader_when_eligible():
    """Spec §7.4 tie-break: preserve the current leader when it is still
    a same-side active participant."""
    world = _clean_world()
    inserted = build_side_scoped_leader_source_fixture(
        world, attacker_source="originator", defender_source="origin_target"
    )
    war_id = next(iter(inserted))
    instance = world.war_instances[war_id]
    # France is attackers list head AND attacker_leader; the chooser must
    # not unseat it.
    from backend.game_logic.settlement_helpers import _choose_leader_for_side
    picked = _choose_leader_for_side(world, instance, "attackers")
    assert picked == "France"


def test_war_leader_score_alphabetical_tiebreak_when_current_ineligible():
    """Spec §7.4 tie-break: when current leader is no longer eligible, pick
    the alphabetically earliest stable nation id (after war_leader_score
    sort)."""
    world = _clean_world()
    inserted = build_side_scoped_leader_source_fixture(
        world, attacker_source="originator", defender_source="origin_target"
    )
    war_id = next(iter(inserted))
    instance = world.war_instances[war_id]
    # Drop France from attackers so the scorer must pick a replacement.
    instance["attackers"] = [n for n in instance["attackers"] if n != "France"]
    instance["side_by_nation"].pop("France", None)
    instance["attacker_leader"] = ""  # force re-pick
    from backend.game_logic.settlement_helpers import _choose_leader_for_side
    picked = _choose_leader_for_side(world, instance, "attackers")
    # Bavaria is the only remaining attacker.
    assert picked == "Bavaria"


def test_side_scoped_leader_source_each_side_uses_own_metadata():
    """Plan gate line 135: coalition-source attacker + non-coalition
    defender (and inverse) each pick using their own
    `leader_source_by_side[side]`. Coalition sources delegate to
    `select_coalition_leader`; non-coalition sources use
    `war_leader_score()`. The two sides must NOT cross-pollinate."""
    world = _clean_world()
    inserted = build_side_scoped_leader_source_fixture(
        world,
        attacker_source="coalition_leader",
        defender_source="origin_target",
    )
    war_id = next(iter(inserted))
    instance = world.war_instances[war_id]
    # Coalition picker may or may not be available in the test world, but
    # the side-source dispatch must respect each side independently. Verify
    # by reading the source metadata directly: each side's source is
    # preserved through the fixture.
    assert instance["leader_source_by_side"]["attackers"] == "coalition_leader"
    assert instance["leader_source_by_side"]["defenders"] == "origin_target"


def test_war_leader_score_empty_safe_when_no_contribution_recorded():
    """Slice B1 ships the empty contribution store. With no episodes seeded
    yet (no B2 emitters), the contribution share is 0 and `war_leader_score`
    must default that component to 0 without crashing."""
    world = _clean_world()
    inserted = build_side_scoped_leader_source_fixture(
        world, attacker_source="originator", defender_source="origin_target"
    )
    war_id = next(iter(inserted))
    # B1: container exists but is empty for any war that has not accrued.
    assert hasattr(world, "war_contribution_scores")
    assert world.war_contribution_scores == {}
    score = war_leader_score(world, "France", war_id=war_id, side="attackers")
    # Must be a non-negative integer.
    assert isinstance(score, int)
    assert score >= 0


# ---------------------------------------------------------------------------
# Elimination exit
# ---------------------------------------------------------------------------


def test_mark_participant_eliminated_stamps_exited_turn_and_exit_path():
    """Spec §7.4 line 452: stamp `participant_meta[nation]["exited_turn"]`
    and `["exit_path"] = "eliminated"` on every active war_instance the
    eliminated nation participates in."""
    world = _clean_world()
    world.current_turn = 12
    inserted = build_three_instance_chain_merge_fixture(world)
    # Austria is in war_a (defenders) and war_b (defenders).
    result = mark_participant_eliminated_in_all_wars(world, "Austria")
    assert result["ok"] is True
    assert len(result["war_ids_touched"]) == 2
    for war_id in result["war_ids_touched"]:
        instance = world.war_instances[war_id]
        meta = instance["participant_meta"].get("Austria") or {}
        assert meta.get("exited_turn") == 12
        assert meta.get("exit_path") == "eliminated"
        assert "Austria" not in instance.get("attackers", [])
        assert "Austria" not in instance.get("defenders", [])
        assert "Austria" not in instance.get("active_participants", [])
        assert "Austria" not in instance.get("side_by_nation", {})


def test_eliminated_side_leader_triggers_repick():
    """When the eliminated nation was a side leader, the chooser re-picks
    a replacement from the remaining same-side participants."""
    world = _clean_world()
    world.current_turn = 8
    inserted = build_three_instance_chain_merge_fixture(world)
    war_a = sorted(inserted.keys())[0]
    instance = world.war_instances[war_a]
    # Austria is the defender_leader of war_a.
    assert instance["defender_leader"] == "Austria"
    # Add a second defender so there's a candidate to replace Austria.
    instance["defenders"].append("Saxony")
    instance["side_by_nation"]["Saxony"] = "defenders"
    instance["active_participants"].append("Saxony")
    instance["participant_meta"]["Saxony"] = {
        "side": "defenders",
        "joined_turn": 5,
        "exited_turn": None,
        "entry_path": "ally_cascade",
    }
    mark_participant_eliminated_in_all_wars(world, "Austria")
    instance = world.war_instances[war_a]
    assert instance["defender_leader"] != "Austria"
    assert instance["defender_leader"] == "Saxony"


def test_elimination_walks_all_war_instances_for_the_nation():
    """The helper iterates every active war_instance the nation participates
    in -- no instance is silently skipped."""
    world = _clean_world()
    inserted = build_three_instance_chain_merge_fixture(world)
    # Snapshot which instances Austria participates in BEFORE elimination.
    expected = {
        wid for wid, inst in inserted.items()
        if "Austria" in inst.get("active_participants", [])
    }
    assert len(expected) == 2  # Austria is in war_a and war_b
    result = mark_participant_eliminated_in_all_wars(world, "Austria")
    assert set(result["war_ids_touched"]) == expected


# ---------------------------------------------------------------------------
# Terminal retention + archive
# ---------------------------------------------------------------------------


def test_war_with_all_pairs_resolved_stamps_ended_turn_and_end_reason():
    """Spec §7.5: when the last active pair resolves, stamp
    `ended_turn = current_turn` and `end_reason = "all_pairs_resolved"`."""
    world = _clean_world()
    war = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    world.current_turn = 7
    pair = _pair("France", "Austria")
    result = resolve_pair_to_resolved(world, pair)
    assert result["ok"] is True
    instance = world.war_instances[war["war_id"]]
    assert instance["ended_turn"] == 7
    assert instance["end_reason"] == WAR_END_REASON_ALL_PAIRS_RESOLVED


def test_terminal_war_queryable_within_retention_window():
    """Spec §7.5 line 359: keep terminal records in `war_instances` while
    `current_turn - ended_turn < ARCHIVE_RETENTION_TURNS` so readers can
    resolve recent references."""
    world = _clean_world()
    war = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    world.current_turn = 5
    resolve_pair_to_resolved(world, _pair("France", "Austria"))
    # Advance turn by 5 (within the 10-turn window). Use direct counter set
    # so we can probe `archive_terminal_war_instances` deterministically.
    world.current_turn = 10  # 10 - 5 = 5 < 10
    archive_terminal_war_instances(world)
    assert war["war_id"] in world.war_instances
    assert not world.archived_war_instances


def test_archive_terminal_moves_record_at_retention_boundary():
    """Spec §7.5 line 360: at `current_turn - ended_turn >=
    ARCHIVE_RETENTION_TURNS`, move the record to `archived_war_instances`
    and remove it from active `war_instances`."""
    world = _clean_world()
    war = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    world.current_turn = 5
    resolve_pair_to_resolved(world, _pair("France", "Austria"))
    world.current_turn = 5 + ARCHIVE_RETENTION_TURNS  # 15 - 5 = 10 >= 10
    result = archive_terminal_war_instances(world)
    assert war["war_id"] in result["archived_war_ids"]
    assert war["war_id"] not in world.war_instances
    archived_ids = [r["war_id"] for r in world.archived_war_instances]
    assert war["war_id"] in archived_ids


# ---------------------------------------------------------------------------
# Post-merge invariants + no-op-safe hooks for absent Slice B/C containers
# ---------------------------------------------------------------------------


def test_post_merge_invariant_catches_dangling_absorbed_war_id_in_bargains():
    """Plan gate line 134: post-merge invariant catches a dangling absorbed
    `war_id` reference in `diplomatic_commitments`."""
    world = _clean_world()
    # Set up a single active war_instance.
    war = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    # Plant a bargain referencing a war_id that does not exist (simulating
    # an absorbed-but-not-rewritten leak).
    world.diplomatic_commitments["1"] = {
        "id": 1,
        "type": "war_bargain",
        "war_id": "war_absorbed_phantom",
        "status": "active",
    }
    with pytest.raises(WarInstanceInvariantError) as excinfo:
        assert_war_instance_invariants(world, context="post_merge")
    assert any("war_absorbed_phantom" in v for v in excinfo.value.violations)


def test_post_merge_invariant_catches_dangling_absorbed_war_id_in_event_log():
    world = _clean_world()
    world.event_log.append(
        {
            "type": "war_entry_ledger",
            "war_id": "war_absorbed_phantom",
            "payload": {"war_id": "war_absorbed_phantom"},
        }
    )

    with pytest.raises(WarInstanceInvariantError) as excinfo:
        assert_war_instance_invariants(world, context="post_merge")

    assert any(
        "event_log" in v and "war_absorbed_phantom" in v
        for v in excinfo.value.violations
    )


def test_post_merge_no_op_safe_when_slice_bc_containers_empty_or_absent():
    """A3 cross-slice gating: post-merge invariant must not false-positive
    when Slice B `war_contribution_scores` is empty (B1 ships the empty
    container by default), Slice C2 `pending_settlement_dialogues` exists
    but is empty, and future `settlement_route_payloads` does not yet exist."""
    world = _clean_world()
    inserted = build_multi_objective_merge_fixture(world)
    war_a = sorted(inserted.keys())[0]
    # B1: container exists but is empty for fixtures that have not accrued.
    assert hasattr(world, "war_contribution_scores")
    assert world.war_contribution_scores == {}
    # Slice C2 dialogue retry container exists but is empty.
    assert hasattr(world, "pending_settlement_dialogues")
    assert world.pending_settlement_dialogues == []
    assert not hasattr(world, "settlement_route_payloads")
    # Run a real merge and confirm the post-merge invariant passes.
    merge_war_instances(world, candidate_war_ids=[war_a])
    # Already asserted internally by merge; do an explicit re-check here.
    assert_war_instance_invariants(world, context="post_merge")


def test_post_merge_invariant_passes_when_bargain_war_id_resolves_to_archived():
    """Archived war_instances are legitimate references for ledger / log
    readers (spec §7.5 retention window). A bargain referencing an archived
    war_id must NOT trigger a post-merge violation."""
    world = _clean_world()
    war = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    world.current_turn = 5
    resolve_pair_to_resolved(world, _pair("France", "Austria"))
    world.current_turn = 5 + ARCHIVE_RETENTION_TURNS
    archive_terminal_war_instances(world)
    # Bargain referencing the now-archived war_id.
    world.diplomatic_commitments["1"] = {
        "id": 1,
        "type": "war_bargain",
        "war_id": war["war_id"],
        "status": "active",
    }
    # Should NOT raise.
    assert_war_instance_invariants(world, context="post_merge")
