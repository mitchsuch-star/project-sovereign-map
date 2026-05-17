"""Foundation tests for Imperial Settlement / Ally Participation scaffolding.

Slice A1 of `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.24 — foundation
gate. Behavioral settlement tests (A2 cascade threading, B contribution,
C common-peace scoring, D reactions, E presentation) live in their own
files.
"""

import inspect
import re

import pytest

from backend.game_logic import diplomacy as diplomacy_module
from backend.game_logic.settlement_helpers import (
    WarInstanceInvariantError,
    assert_war_instance_invariants,
)
from backend.models.dialogue_manager import DialogueManager
from backend.models.region import NATION_CAPITALS
from backend.models.world_state import WorldState
from backend.nation_config import NATION_POWER_TIERS
from tests.helpers.full_europe_settlement_fixtures import (
    CANONICAL_13_NATIONS,
    build_full_europe_war_instance_fixture,
    install_synthetic_active_roster,
    make_synthetic_war_instance,
)


def test_settlement_home_capital_alias_uses_configured_mapped_capital():
    world = WorldState()

    assert world.get_settlement_home_capital("Britain") == NATION_CAPITALS["Britain"]
    assert world.get_settlement_home_capital("Britain") == "Netherlands"
    assert world.get_settlement_home_capital("Unconfigured Nation") is None


def test_settlement_home_capital_requires_region_in_current_world(monkeypatch):
    world = WorldState()

    monkeypatch.setitem(NATION_CAPITALS, "Fixture Nation", "Imaginary Capital")
    assert world.get_settlement_home_capital("Fixture Nation") is None

    world.regions.pop(NATION_CAPITALS["Britain"], None)
    assert world.get_settlement_home_capital("Britain") is None


def test_future_nation_power_tier_does_not_make_active_participant():
    world = WorldState()

    assert NATION_POWER_TIERS["Russia"] == "major"
    assert world.get_settlement_home_capital("Russia") is None
    assert "Russia" not in world.get_active_nations()


def test_incoming_settlement_offer_in_persistent_mailbox_taxonomy_after_sc5_reversal_commit2():
    """SC-5 reversal commit 2 (Slice G1) re-adds
    `incoming_settlement_offer` to the persistent mailbox set so the
    producer-promoted offer can surface through `/mailbox`,
    `/pending_envoy`, and the Godot mailbox panel. The type stays out
    of `CURRENT_TURN_OFFER_TYPES` because incoming settlement offers
    persist across turns (no end-of-turn lapse) and out of
    `HARD_STOP_TYPES` because they never block ordinary commands."""
    assert "incoming_settlement_offer" in DialogueManager.PERSISTENT_MAILBOX_TYPES
    assert "incoming_settlement_offer" in DialogueManager.SOFT_STOP_MAILBOX_TYPES
    assert "incoming_settlement_offer" in DialogueManager.DIALOGUE_PRIORITY
    assert "incoming_settlement_offer" in DialogueManager.MAILBOX_SUMMARY_LABELS
    assert "incoming_settlement_offer" not in DialogueManager.CURRENT_TURN_OFFER_TYPES
    assert "incoming_settlement_offer" not in DialogueManager.HARD_STOP_TYPES


def test_settlement_containers_initialize_to_spec_defaults():
    """`__init__` defaults must match spec §0 / §7.2 exactly."""
    world = WorldState()

    assert world.next_war_instance_id == 1
    assert world.war_instances == {}
    assert world.archived_war_instances == []
    assert world.pending_settlement_dialogues == []
    assert world.ai_settlement_cooldowns == {}


def test_old_save_without_settlement_keys_loads_with_spec_defaults():
    """Pre-A1 saves have no settlement keys; round-trip must default cleanly."""
    world = WorldState()
    data = world.to_dict()
    # Simulate a pre-A1 save by stripping the new keys entirely.
    data.pop("next_war_instance_id", None)
    data.pop("war_instances", None)
    data.pop("archived_war_instances", None)
    data.pop("pending_settlement_dialogues", None)
    data.pop("ai_settlement_cooldowns", None)

    restored = WorldState.from_dict(data)

    assert restored.next_war_instance_id == 1
    assert restored.war_instances == {}
    assert restored.archived_war_instances == []
    assert restored.pending_settlement_dialogues == []
    assert restored.ai_settlement_cooldowns == {}


def test_settlement_containers_round_trip_through_to_dict_from_dict():
    """A1 must serialize and round-trip the new fields without loss."""
    world = WorldState()
    fixture = build_full_europe_war_instance_fixture(world, target_active_count=3)
    world.archived_war_instances = [
        {"war_id": "war_archive_1", "ended_turn": 5, "end_reason": "all_pairs_resolved"}
    ]
    world.pending_settlement_dialogues = [
        {"war_id": "war_1", "dialogue_type": "settlement_confirm"}
    ]
    world.ai_settlement_cooldowns = {"war_1": 7}
    snapshot_next_id = world.next_war_instance_id

    restored = WorldState.from_dict(world.to_dict())

    assert restored.next_war_instance_id == snapshot_next_id
    assert set(restored.war_instances.keys()) == set(fixture.keys())
    for war_id, instance in fixture.items():
        round_tripped = restored.war_instances[war_id]
        assert round_tripped["attacker_leader"] == instance["attacker_leader"]
        assert round_tripped["defender_leader"] == instance["defender_leader"]
        assert sorted(round_tripped["active_participants"]) == sorted(
            instance["active_participants"]
        )
    assert restored.archived_war_instances == world.archived_war_instances
    assert restored.pending_settlement_dialogues == world.pending_settlement_dialogues
    assert restored.ai_settlement_cooldowns == world.ai_settlement_cooldowns


def test_war_instance_indexes_are_empty_safe_before_any_instance_exists():
    """A1 helpers must return empty results when `war_instances == {}`."""
    world = WorldState()

    assert world.war_instances == {}
    assert world.get_war_instances_by_leader() == {}
    assert world.get_war_instances_by_leader("France") == []
    assert world.get_war_instances_by_participant() == {}
    assert world.get_war_instances_by_participant("France") == []


def test_war_instance_indexes_rebuild_at_target_scale():
    """20-active-`war_instance` synthetic fixture exercises the helpers at scale."""
    world = WorldState()
    fixture = build_full_europe_war_instance_fixture(world, target_active_count=20)

    leader_index = world.get_war_instances_by_leader()
    participant_index = world.get_war_instances_by_participant()

    assert len(fixture) == 20

    seen_war_ids_in_leader = {wid for wars in leader_index.values() for wid in wars}
    seen_war_ids_in_participant = {
        wid for wars in participant_index.values() for wid in wars
    }
    assert seen_war_ids_in_leader == set(fixture.keys())
    assert seen_war_ids_in_participant == set(fixture.keys())

    # Big coalition side leadership shows up in both indexes.
    assert "war_1" in world.get_war_instances_by_leader("France")
    assert "war_1" in world.get_war_instances_by_leader("Russia")
    assert "war_1" in world.get_war_instances_by_participant("Saxony")

    # Empty-list values must not leak into the index for non-participants.
    fake_nation = "ImaginaryRepublic"
    assert fake_nation not in leader_index
    assert fake_nation not in participant_index

    # Public all-index reads return defensive copies, not writable cache refs.
    leader_index["France"].append("fake_war")
    participant_index["Saxony"].append("fake_war")
    assert "fake_war" not in world.get_war_instances_by_leader("France")
    assert "fake_war" not in world.get_war_instances_by_participant("Saxony")


def test_war_instance_index_invalidation_is_idempotent():
    """Calling invalidate N times yields at most ONE rebuild on next read."""
    world = WorldState()
    build_full_europe_war_instance_fixture(world, target_active_count=4)

    # Prime the cache.
    primed = world.get_war_instances_by_leader()
    assert primed  # non-empty

    rebuild_calls = {"count": 0}
    original = world._rebuild_war_instance_indexes

    def counting_rebuild():
        rebuild_calls["count"] += 1
        original()

    world._rebuild_war_instance_indexes = counting_rebuild

    for _ in range(5):
        world.invalidate_war_instance_indexes()

    # First read after the storm of invalidates rebuilds once.
    world.get_war_instances_by_leader()
    # Subsequent reads must NOT rebuild again until the next invalidation.
    world.get_war_instances_by_leader()
    world.get_war_instances_by_participant("France")

    assert rebuild_calls["count"] == 1


def test_war_instance_indexes_dirty_flag_clears_after_rebuild():
    """The dirty flag must clear after a rebuild so subsequent reads short-circuit."""
    world = WorldState()
    build_full_europe_war_instance_fixture(world, target_active_count=2)

    assert world._war_instance_indexes_dirty is True
    world.get_war_instances_by_leader()
    assert world._war_instance_indexes_dirty is False
    world.get_war_instances_by_participant()
    assert world._war_instance_indexes_dirty is False


def test_invariant_assertion_passes_on_empty_world():
    """A1 contract: empty `war_instances` must trivially satisfy the invariant."""
    world = WorldState()

    # Default WorldState has WAR pairs (Britain|France, France|Prussia) but no
    # war_instances claim them yet. The invariant must FAIL because the WAR
    # pairs are unowned — that's the foundation gate's expected behavior
    # before A2 wires declarations to instance creation.
    with pytest.raises(WarInstanceInvariantError) as exc_info:
        assert_war_instance_invariants(world, context="bare_world")
    assert any("Britain|France" in v for v in exc_info.value.violations)

    # When we strip live diplomatic_states down to nothing, an empty
    # war_instances world is invariant-clean.
    world.diplomatic_states = {}
    assert_war_instance_invariants(world, context="empty_world")


def test_invariant_assertion_passes_on_clean_full_europe_fixture():
    """The 20-instance fixture must produce zero invariant violations."""
    world = WorldState()
    # Strip live diplomatic_states first so the fixture's WAR pair stamps
    # are the only WAR entries the invariant sees.
    world.diplomatic_states = {}
    build_full_europe_war_instance_fixture(world, target_active_count=20)

    assert_war_instance_invariants(world, context="post_merge")


def test_invariant_assertion_catches_duplicate_pair_owner():
    """Bad fixture: same pair claimed by two active war_instances must fail."""
    world = WorldState()
    world.diplomatic_states = {}
    install_synthetic_active_roster(world, list(CANONICAL_13_NATIONS))

    war_a = make_synthetic_war_instance(
        "war_1",
        attackers=["France"],
        defenders=["Austria"],
        attacker_leader="France",
        defender_leader="Austria",
        created_sequence=1,
    )
    war_b = make_synthetic_war_instance(
        "war_2",
        attackers=["France"],
        defenders=["Austria"],
        attacker_leader="France",
        defender_leader="Austria",
        created_sequence=2,
    )
    world.war_instances["war_1"] = war_a
    world.war_instances["war_2"] = war_b
    world.diplomatic_states["Austria|France"] = "WAR"
    world.invalidate_war_instance_indexes()

    with pytest.raises(WarInstanceInvariantError) as exc_info:
        assert_war_instance_invariants(world, context="post_merge")

    assert exc_info.value.context == "post_merge"
    assert any(
        "Austria|France" in v and "war_1" in v and "war_2" in v
        for v in exc_info.value.violations
    )


def test_invariant_assertion_catches_side_disjointness_violation():
    """Bad fixture: same nation on both sides must fail."""
    world = WorldState()
    world.diplomatic_states = {}
    install_synthetic_active_roster(world, list(CANONICAL_13_NATIONS))

    bad = make_synthetic_war_instance(
        "war_1",
        attackers=["France", "Saxony"],
        defenders=["Austria"],
        attacker_leader="France",
        defender_leader="Austria",
    )
    bad["defenders"].append("Saxony")
    bad["side_by_nation"]["Saxony"] = "defenders"
    world.war_instances["war_1"] = bad
    world.diplomatic_states["Austria|France"] = "WAR"
    world.diplomatic_states["Austria|Saxony"] = "WAR"
    world.diplomatic_states["France|Saxony"] = "WAR"
    world.invalidate_war_instance_indexes()

    with pytest.raises(WarInstanceInvariantError) as exc_info:
        assert_war_instance_invariants(world, context="declaration")

    assert any("both sides" in v and "Saxony" in v for v in exc_info.value.violations)


def test_elimination_helper_uses_cached_nation_regions_lookup():
    """A1 plan: refactor any touched elimination helper to the cached path.

    Source-level proof: `_is_nation_eliminated` must NOT scan
    `world.regions.values()` raw any more; it must read through
    `get_nation_regions(...)`. The functional behavior is also covered by
    `get_active_nations()` — eliminating France clears its regions, then
    the helper sees the empty list and reports elimination.
    """
    src = inspect.getsource(diplomacy_module._is_nation_eliminated)
    # Strip docstring + comments before scanning so the assertion checks
    # live code, not Slice A1 commentary that explains the refactor.
    code_only = "\n".join(
        line for line in src.splitlines()
        if not line.lstrip().startswith("#")
    )
    code_only = re.sub(r'""".*?"""', "", code_only, flags=re.DOTALL)
    assert "world.regions.values()" not in code_only, (
        "_is_nation_eliminated still scans world.regions.values() raw — "
        "Slice A1 plan demands the cached get_nation_regions() path."
    )
    assert re.search(r"get_nation_regions\(", code_only), (
        "_is_nation_eliminated must read through world.get_nation_regions(...)."
    )

    # Behavioral cross-check: empty controllers + no vassals => eliminated.
    world = WorldState()
    for region in world.regions.values():
        if region.controller == "Saxony":
            region.controller = "France"
    world.invalidate_active_nations_cache()
    assert diplomacy_module._is_nation_eliminated(world, "Saxony") is True

    # Britain is mapped to Netherlands and still controls regions, so it is
    # NOT eliminated. This pins the A1 contract that Britain is a normal
    # mapped participant — not a separate settlement identity.
    assert diplomacy_module._is_nation_eliminated(world, "Britain") is False


def test_britain_followed_by_normal_mapped_rules_in_active_roster():
    """Britain is a mapped participant in the current runtime, not an exception."""
    world = WorldState()

    assert world.get_settlement_home_capital("Britain") == "Netherlands"
    assert "Britain" in world.get_active_nations()
    # Britain controls its three mapped regions; eliminating those should
    # follow the normal mapped-nation rule (no special settlement branch).
    for region in world.regions.values():
        if region.controller == "Britain":
            region.controller = "France"
    world.invalidate_active_nations_cache()
    assert "Britain" not in world.get_active_nations()
