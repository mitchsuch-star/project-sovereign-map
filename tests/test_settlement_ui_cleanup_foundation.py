"""Foundation tests for `SETTLEMENT_UI_CLEANUP_SPEC` v0.17 G2-Slice-1.

This file covers the foundation-only container scaffolding introduced before
the editor/preview/ratification work in G2-Slice-1. Behavior tests for SC-1
through SC-4 (POST preview, conflict matrix, ratification gating, edit-mode
transitions) live in their own files.
"""

import copy
import json

from backend.models.world_state import WorldState


def test_cleanup_foundation_containers_initialize_to_spec_defaults():
    """`__init__` defaults must match SETTLEMENT_UI_CLEANUP_SPEC G2-Slice-1.

    Both new containers default to `{}` so pre-cleanup saves and new worlds
    are indistinguishable until the editor writes a draft.
    """
    world = WorldState()

    assert world.pending_settlement_drafts == {}
    assert world.settlement_route_seq == {}


def test_old_save_without_cleanup_keys_loads_with_spec_defaults():
    """Pre-cleanup saves omit the new keys; round-trip must default cleanly."""
    world = WorldState()
    data = world.to_dict()
    data.pop("pending_settlement_drafts", None)
    data.pop("settlement_route_seq", None)

    restored = WorldState.from_dict(data)

    assert restored.pending_settlement_drafts == {}
    assert restored.settlement_route_seq == {}


def test_corrupt_top_level_cleanup_containers_load_with_spec_defaults():
    """Corrupt saves with non-dict cleanup containers must not crash load."""
    world = WorldState()
    data = world.to_dict()
    data["pending_settlement_drafts"] = "not a dict"
    data["settlement_route_seq"] = ["not", "a", "dict"]

    restored = WorldState.from_dict(data)

    assert restored.pending_settlement_drafts == {}
    assert restored.settlement_route_seq == {}


def test_pending_settlement_drafts_round_trip_through_to_dict_from_dict():
    """Authored drafts must survive save/load with field fidelity."""
    world = WorldState()
    draft = {
        "war_id": "war_1",
        "proposer_side": "attackers",
        "selected_target_nation": "Austria",
        "covered_enemy_participants": ["Austria", "Saxony"],
        "settlement_terms": [
            {"type": "peace"},
            {"type": "territory_cede", "from": "Austria", "to": "France",
             "region": "Tyrol"},
            {"type": "gold_indemnity", "from": "Austria", "to": "France",
             "amount": 200},
        ],
    }
    world.pending_settlement_drafts = {"war_1": draft}

    restored = WorldState.from_dict(world.to_dict())

    assert restored.pending_settlement_drafts == {"war_1": draft}


def test_pending_settlement_drafts_serialization_is_deepcopy_safe():
    """Mutating the serialized payload must not aliasing-bleed back into world state."""
    world = WorldState()
    world.pending_settlement_drafts = {
        "war_1": {"settlement_terms": [{"type": "peace"}]},
    }

    payload = world.to_dict()
    payload["pending_settlement_drafts"]["war_1"]["settlement_terms"].append(
        {"type": "gold_indemnity", "from": "Austria", "to": "France",
         "amount": 999}
    )

    assert world.pending_settlement_drafts["war_1"]["settlement_terms"] == [
        {"type": "peace"}
    ]


def test_pending_settlement_drafts_from_dict_skips_non_dict_payloads():
    """Corrupt save with non-dict draft entries must load without crashing."""
    world = WorldState()
    data = world.to_dict()
    data["pending_settlement_drafts"] = {
        "war_1": {"settlement_terms": [{"type": "peace"}]},
        "war_2": "not a dict",
        "war_3": None,
        "war_4": [{"type": "peace"}],
    }

    restored = WorldState.from_dict(data)

    assert "war_1" in restored.pending_settlement_drafts
    assert "war_2" not in restored.pending_settlement_drafts
    assert "war_3" not in restored.pending_settlement_drafts
    assert "war_4" not in restored.pending_settlement_drafts


def test_settlement_route_seq_round_trip_preserves_int_turn_keys():
    """Per-(war_id, turn) sequence map must keep int turn keys after load."""
    world = WorldState()
    world.settlement_route_seq = {
        "war_1": {7: 2, 8: 1},
        "war_2": {12: 1},
    }

    restored = WorldState.from_dict(world.to_dict())

    assert set(restored.settlement_route_seq.keys()) == {"war_1", "war_2"}
    assert restored.settlement_route_seq["war_1"] == {7: 2, 8: 1}
    assert restored.settlement_route_seq["war_2"] == {12: 1}
    for per_turn in restored.settlement_route_seq.values():
        for turn_key in per_turn:
            assert isinstance(turn_key, int)


def test_settlement_route_seq_survives_json_round_trip():
    """JSON object keys are strings; load must convert back to int turns.

    This matches the spec's documented serialization shape: `Dict[str, Dict[int, int]]`
    on disk becomes `Dict[str, Dict[str, int]]` after JSON, and `from_dict`
    restores the in-memory int-keyed shape.
    """
    world = WorldState()
    world.settlement_route_seq = {"war_1": {7: 3}, "war_2": {12: 1, 13: 4}}

    encoded = json.dumps(world.to_dict())
    decoded = json.loads(encoded)
    restored = WorldState.from_dict(decoded)

    assert restored.settlement_route_seq == {
        "war_1": {7: 3},
        "war_2": {12: 1, 13: 4},
    }


def test_settlement_route_seq_from_dict_skips_corrupt_entries():
    """Non-int turn keys, non-int seq values, and non-dict per-turn maps drop."""
    world = WorldState()
    data = world.to_dict()
    data["settlement_route_seq"] = {
        "war_1": {
            "7": 1,
            8: 2,
            "not_an_int": 2,
            "9": "3",
            "10": 2.5,
            "11": True,
            True: 4,
            12.5: 5,
        },
        "war_2": "not a dict",
        "war_3": {"5": 9},
    }

    restored = WorldState.from_dict(data)

    assert restored.settlement_route_seq["war_1"] == {7: 1, 8: 2}
    assert "war_2" not in restored.settlement_route_seq
    assert restored.settlement_route_seq["war_3"] == {5: 9}


def test_cleanup_foundation_containers_independent_from_pre_cleanup_state():
    """New cleanup fields must not interfere with existing settlement state."""
    world = WorldState()
    world.pending_settlement_dialogues = [
        {"war_id": "war_1", "dialogue_type": "settlement_confirm"}
    ]
    world.ai_settlement_cooldowns = {"war_1": 7}
    world.pending_settlement_drafts = {"war_1": {"settlement_terms": []}}
    world.settlement_route_seq = {"war_1": {7: 1}}

    restored = WorldState.from_dict(world.to_dict())

    assert restored.pending_settlement_dialogues == world.pending_settlement_dialogues
    assert restored.ai_settlement_cooldowns == world.ai_settlement_cooldowns
    assert restored.pending_settlement_drafts == world.pending_settlement_drafts
    assert restored.settlement_route_seq == world.settlement_route_seq


def test_pending_settlement_drafts_deepcopy_on_to_dict():
    """`to_dict` must not return references to internal world-state structure."""
    world = WorldState()
    world.pending_settlement_drafts = {
        "war_1": {"settlement_terms": [{"type": "peace"}]},
    }

    snapshot = world.to_dict()
    snapshot_draft = snapshot["pending_settlement_drafts"]["war_1"]
    snapshot_draft["settlement_terms"].clear()

    assert world.pending_settlement_drafts["war_1"]["settlement_terms"] == [
        {"type": "peace"}
    ]

    expected = {"war_1": {"settlement_terms": [{"type": "peace"}]}}
    assert WorldState.from_dict(copy.deepcopy(world.to_dict())).pending_settlement_drafts == expected
