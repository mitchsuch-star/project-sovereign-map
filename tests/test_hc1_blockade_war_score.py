"""HC-1 "The Silver Blockade" — naval denial reaches the war score
(gate §2). A signed `blockade` component (cap ±BLOCKADE_SCORE_CAP) on
the PT-J2 campaign-ledger substrate: one `blockade_turns` counter per
side, accrued once per (denier, victim) per turn in the naval tick,
scored min(cap, turns // divisor) per side and differenced.

Never-do pins carried here: derivable to zero on fleetless worlds
(legacy byte-identical); the seven existing components untouched; the
ledger key survives armistice and demobilizes with the pair's formal
peace exactly as captures/casualties do.
"""

from pathlib import Path

import pytest

from backend.game_logic.diplomacy import (
    BLOCKADE_SCORE_CAP,
    BLOCKADE_TURNS_DIVISOR,
    calculate_side_war_score,
    calculate_war_score,
    set_diplomatic_state,
)
from backend.game_logic.naval import (
    _record_blockade_pressure,
    process_naval_turn,
)
from backend.game_logic.war_status import build_active_wars
from backend.models.world_state import WorldState

from tests.conftest import WorldFactory

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture
def europe():
    return WorldState.from_scenario(str(SCENARIO_PATH))


class TestComponentMath:
    """The scoring formula over an injected ledger — the PT-J2 pattern."""

    def test_component_from_recorded_turns(self):
        world = WorldFactory.with_war("France", "Britain")
        key = world._make_diplo_key("France", "Britain")
        world.campaign_ledgers[key] = {
            "captures": {}, "casualties": {},
            "blockade_turns": {"Britain": 10},
        }
        components = calculate_war_score(
            "Britain", "France", world, return_components=True)
        assert components["blockade"] == 10 // BLOCKADE_TURNS_DIVISOR
        assert components["blockade"] == 5

    def test_component_caps_at_fifteen(self):
        world = WorldFactory.with_war("France", "Britain")
        key = world._make_diplo_key("France", "Britain")
        world.campaign_ledgers[key] = {
            "captures": {}, "casualties": {},
            "blockade_turns": {"Britain": 400},
        }
        components = calculate_war_score(
            "Britain", "France", world, return_components=True)
        assert components["blockade"] == BLOCKADE_SCORE_CAP

    def test_mirror_symmetry(self):
        world = WorldFactory.with_war("France", "Britain")
        key = world._make_diplo_key("France", "Britain")
        world.campaign_ledgers[key] = {
            "captures": {}, "casualties": {},
            "blockade_turns": {"Britain": 10, "France": 4},
        }
        a = calculate_war_score("Britain", "France", world,
                                return_components=True)
        b = calculate_war_score("France", "Britain", world,
                                return_components=True)
        assert a["blockade"] == 5 - 2
        assert b["blockade"] == -a["blockade"]

    def test_mutual_blockade_saturates_per_side_before_differencing(self):
        # 60 vs 40 turns: both sides saturate at the cap -> the diff
        # washes to zero (sustained mutual denial is not an edge).
        world = WorldFactory.with_war("France", "Britain")
        key = world._make_diplo_key("France", "Britain")
        world.campaign_ledgers[key] = {
            "captures": {}, "casualties": {},
            "blockade_turns": {"Britain": 60, "France": 40},
        }
        components = calculate_war_score(
            "Britain", "France", world, return_components=True)
        assert components["blockade"] == 0

    def test_absent_key_scores_zero_and_the_seven_components_stand(self):
        world = WorldFactory.with_war("France", "Britain")
        components = calculate_war_score(
            "France", "Britain", world, return_components=True)
        assert components["blockade"] == 0
        for existing in ("territory", "battles", "decisive", "capital",
                         "campaign", "blood", "ticking"):
            assert existing in components

    def test_component_moves_the_total(self):
        world = WorldFactory.with_war("France", "Britain")
        key = world._make_diplo_key("France", "Britain")
        before = calculate_war_score("Britain", "France", world)
        world.campaign_ledgers[key] = {
            "captures": {}, "casualties": {},
            "blockade_turns": {"Britain": 30},
        }
        after = calculate_war_score("Britain", "France", world)
        assert after == before + BLOCKADE_SCORE_CAP

    def test_side_score_inherits_and_reclamps(self):
        world = WorldFactory.with_war("France", "Britain")
        set_diplomatic_state(world, "France", "Prussia", "WAR")
        for opponent in ("Britain", "Prussia"):
            key = world._make_diplo_key("France", opponent)
            world.campaign_ledgers[key] = {
                "captures": {}, "casualties": {},
                "blockade_turns": {opponent: 60},
            }
        side = calculate_side_war_score(
            "France", ["Britain", "Prussia"], world, return_components=True)
        # Two saturated pair reads sum to -30, re-clamped at the pair cap.
        assert side["blockade"] == -BLOCKADE_SCORE_CAP


class TestAccrual:
    """The naval tick writes the counter — arm 1 (posture) on the real
    1805 boot, arm 2 (closure) on a hand-authored fleet store."""

    def test_boot_blockade_credits_britain_each_turn(self, europe):
        # Boot fact: Britain's untargeted blockade pins France (the
        # measured -175 Blockade line). The tick must credit the pair.
        process_naval_turn(europe)
        key = europe._make_diplo_key("France", "Britain")
        ledger = europe.campaign_ledgers.get(key, {})
        assert (ledger.get("blockade_turns") or {}).get("Britain") == 1
        process_naval_turn(europe)
        assert europe.campaign_ledgers[key]["blockade_turns"]["Britain"] == 2

    def test_boot_closure_is_below_the_notch(self, europe):
        # Boot fact (pinned in the NV records): CS closure vs Britain is
        # ~0.385 < 0.40 — the closure arm must NOT credit France at boot.
        process_naval_turn(europe)
        key = europe._make_diplo_key("France", "Britain")
        ledger = europe.campaign_ledgers.get(key, {})
        assert "France" not in (ledger.get("blockade_turns") or {})

    def test_closure_arm_credits_the_at_war_port_owner(self):
        world = WorldFactory.with_war("France", "Britain")
        world.fleets = {
            "France": {"ships": 10, "readiness": 100, "posture": "guard",
                       "ports": 20, "dockyards": [], "island": False},
            "Britain": {"ships": 5, "readiness": 100, "posture": "guard",
                        "ports": 0, "dockyards": [], "island": True},
        }
        _record_blockade_pressure(world, [])
        key = world._make_diplo_key("France", "Britain")
        ledger = world.campaign_ledgers.get(key, {})
        assert (ledger.get("blockade_turns") or {}).get("France") == 1

    def test_no_double_credit_when_both_arms_fire(self):
        world = WorldFactory.with_war("France", "Britain")
        world.fleets = {
            "France": {"ships": 50, "readiness": 100, "posture": "blockade",
                       "ports": 20, "dockyards": [], "island": False},
            "Britain": {"ships": 5, "readiness": 100, "posture": "guard",
                        "ports": 0, "dockyards": [], "island": True},
        }
        # France both posture-blockades Britain AND closes 100% of the
        # continent — one credit per (denier, victim) per turn.
        _record_blockade_pressure(world, ["Britain"])
        key = world._make_diplo_key("France", "Britain")
        assert world.campaign_ledgers[key]["blockade_turns"]["France"] == 1

    def test_peacetime_denial_records_nothing(self):
        world = WorldFactory.basic()
        # The legacy fixture boots France-Britain at WAR — force the pair
        # to peace so the war gate is what this test exercises.
        key = world._make_diplo_key("France", "Britain")
        world.diplomatic_states[key] = "PEACE"
        world.fleets = {
            "France": {"ships": 50, "readiness": 100, "posture": "blockade",
                       "ports": 20, "dockyards": [], "island": False},
            "Britain": {"ships": 5, "readiness": 100, "posture": "guard",
                        "ports": 0, "dockyards": [], "island": True},
        }
        _record_blockade_pressure(world, ["Britain"])
        assert world.campaign_ledgers == {}

    def test_fleetless_world_never_accrues(self):
        world = WorldFactory.with_war("France", "Britain")
        assert process_naval_turn(world) == []
        assert world.campaign_ledgers == {}


class TestLifecycle:
    """The counter inherits the ledger's whole lifecycle for free."""

    def _warred(self):
        world = WorldFactory.with_war("France", "Britain")
        key = world._make_diplo_key("France", "Britain")
        world.campaign_ledgers[key] = {
            "captures": {}, "casualties": {},
            "blockade_turns": {"Britain": 8},
        }
        return world, key

    def test_survives_armistice(self):
        world, key = self._warred()
        set_diplomatic_state(world, "France", "Britain", "ARMISTICE")
        assert world.campaign_ledgers[key]["blockade_turns"] == {"Britain": 8}

    def test_demobilizes_on_formal_peace(self):
        world, key = self._warred()
        set_diplomatic_state(world, "France", "Britain", "PEACE")
        assert key not in world.campaign_ledgers

    def test_round_trips_through_serialization(self):
        world, key = self._warred()
        restored = WorldState.from_dict(world.to_dict())
        assert restored.campaign_ledgers == world.campaign_ledgers
        assert restored.campaign_ledgers[key]["blockade_turns"] == {"Britain": 8}

    def test_land_war_ledger_round_trips_without_the_key(self):
        # SPARSE by design: a land war's ledger keeps its pre-slice
        # shape byte-identically through save/load.
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")
        world.campaign_ledgers[key] = {
            "captures": {"France": ["R1"]},
            "casualties": {"France": 500},
        }
        restored = WorldState.from_dict(world.to_dict())
        assert restored.campaign_ledgers == world.campaign_ledgers
        assert "blockade_turns" not in restored.campaign_ledgers[key]


class TestShownEqualsApplied:
    def test_war_status_breakdown_carries_the_component(self):
        world = WorldFactory.with_war("France", "Britain")
        key = world._make_diplo_key("France", "Britain")
        world.campaign_ledgers[key] = {
            "captures": {}, "casualties": {},
            "blockade_turns": {"Britain": 10},
        }
        wars = build_active_wars(world)["wars"]
        row = next(w for w in wars if w.get("opponent") == "Britain")
        assert row["breakdown"]["blockade"] == -5
        # Shown = applied: the row's figure IS the formula's figure.
        components = calculate_war_score(
            "France", "Britain", world, return_components=True)
        assert row["breakdown"]["blockade"] == components["blockade"]

    def test_scripted_strangulation_moves_the_bar(self, europe):
        """The A2 acceptance case: a sustained blockade war shows a
        nonzero Blockade row whose figure equals the formula over the
        recorded counter — the strangler stops reading 0."""
        for _ in range(12):
            process_naval_turn(europe)
        key = europe._make_diplo_key("France", "Britain")
        turns = europe.campaign_ledgers[key]["blockade_turns"]["Britain"]
        assert turns == 12
        components = calculate_war_score(
            "Britain", "France", europe, return_components=True)
        assert components["blockade"] == min(
            BLOCKADE_SCORE_CAP, turns // BLOCKADE_TURNS_DIVISOR)
        assert components["blockade"] > 0
