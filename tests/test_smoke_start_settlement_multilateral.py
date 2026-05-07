"""Opt-in settlement smoke-start preset tests."""

from __future__ import annotations

from backend.game_logic.settlement_helpers import assert_war_instance_invariants
from backend.game_logic.war_status import build_active_wars
from backend.game_logic.war_contribution import current_episode
from backend.models.world_state import (
    SMOKE_START_ENV,
    SMOKE_START_SETTLEMENT_MULTILATERAL,
    WorldState,
)


def test_default_world_state_starts_without_seeded_war_instances(monkeypatch):
    monkeypatch.delenv(SMOKE_START_ENV, raising=False)

    world = WorldState()

    assert world.war_instances == {}
    assert world.diplomatic_states["Britain|France"] == "WAR"
    assert world.diplomatic_states["France|Prussia"] == "WAR"
    assert world.diplomatic_states["Britain|Prussia"] == "ALLIANCE"


def test_settlement_multilateral_smoke_start_seeds_shared_war(monkeypatch):
    monkeypatch.setenv(SMOKE_START_ENV, SMOKE_START_SETTLEMENT_MULTILATERAL)

    world = WorldState()

    assert len(world.war_instances) == 1
    war_id, instance = next(iter(world.war_instances.items()))
    assert instance["ended_turn"] is None
    assert instance["attackers"] == ["France"]
    assert instance["defenders"] == ["Britain", "Prussia"]
    assert instance["attacker_leader"] == "France"
    assert instance["defender_leader"] == "Britain"
    assert instance["active_diplo_keys"] == ["Britain|France", "France|Prussia"]
    assert instance["side_by_nation"] == {
        "France": "attackers",
        "Britain": "defenders",
        "Prussia": "defenders",
    }
    assert instance["active_participants"] == ["France", "Britain", "Prussia"]
    assert world.diplomatic_states["Britain|France"] == "WAR"
    assert world.diplomatic_states["France|Prussia"] == "WAR"
    assert world.diplomatic_states["Britain|Prussia"] == "ALLIANCE"

    for nation in ("France", "Britain", "Prussia"):
        episode = current_episode(world, war_id, nation)
        assert episode is not None
        assert episode["joined_turn"] == world.current_turn
        assert episode["exited_turn"] is None

    assert_war_instance_invariants(world)


def test_settlement_multilateral_smoke_start_renders_as_one_shared_war(monkeypatch):
    monkeypatch.setenv(SMOKE_START_ENV, SMOKE_START_SETTLEMENT_MULTILATERAL)

    world = WorldState()

    active_wars = build_active_wars(world)
    assert len(active_wars["wars"]) == 1
    war = active_wars["wars"][0]
    assert war["war_instance_id"] == "war_1"
    assert war["opponent"] == "Britain"
    assert war["opponents"] == ["Britain", "Prussia"]
    assert war["opponent_display"] == "Britain + Prussia"
    assert war["is_multi_participant_war"] is True
    assert war["settlement_eligibility"]["coverable_enemy_participants"] == [
        "Britain",
        "Prussia",
    ]
