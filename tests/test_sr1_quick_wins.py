"""Score Mandate Chunk 1 — the quick-win reserve (`docs/SCORE_MANDATE_PLAN.md`
§3; September 26, 2026).

AAR-12 — spending the last ADMINISTRATIVE action no longer auto-ends the
turn. The typed `end turn` road carries an envoy-lapse confirmation the
auto-advance never did, so a keel laid or a levy raised with the military
pool already spent ended the day mid-thought (the AAR's turns 9 and 11).
The military road keeps its auto-advance (WO-22's defer aside); the
administrative one says the pools are dry and leaves the day to the player.
"""
import contextlib
import io
from pathlib import Path

import pytest

import backend.commands.executor as EX
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState

SCENARIO_PATH = (Path(__file__).resolve().parents[1] / "godot-client"
                 / "project-sovereign" / "assets" / "maps" / "europe_1805.json")


@pytest.fixture
def europe():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO_PATH))


def _build_market(world, region="Paris"):
    world.nation_gold["France"] = 50_000
    parsed = {"command": {"action": "build", "target": region,
                          "building_type": "market"},
              "original_command": f"build market at {region}"}
    with contextlib.redirect_stdout(io.StringIO()):
        return CommandExecutor().execute(parsed, {"world": world})


class TestAAR12TheLastAdminSpendDoesNotEndTheDay:

    def test_the_last_admin_spend_leaves_the_turn_to_the_player(self, europe):
        europe.actions_remaining = 0
        europe.admin_actions_remaining = 1
        turn_before = int(europe.current_turn)
        result = _build_market(europe)
        assert result["success"] is True, result.get("message")
        assert int(europe.current_turn) == turn_before
        assert result["action_info"]["turn_advanced"] is False
        assert int(europe.admin_actions_remaining) == 0
        assert result.get("last_order_of_the_day") is True
        assert EX.LAST_ORDER_OF_THE_DAY_NOTICE in result["message"]

    def test_the_notice_rides_only_when_both_pools_are_dry(self, europe):
        europe.actions_remaining = 2
        europe.admin_actions_remaining = 1
        result = _build_market(europe)
        assert result["success"] is True, result.get("message")
        assert result.get("last_order_of_the_day") is None
        assert EX.LAST_ORDER_OF_THE_DAY_NOTICE not in result["message"]
        assert result["action_info"]["turn_advanced"] is False

    def test_the_lever_down_reproduces_the_old_auto_advance(self, europe, monkeypatch):
        """The pin binds: with the lever down the last administrative spend
        auto-advances exactly as it did before the row."""
        monkeypatch.setattr(EX, "AN_ADMIN_SPEND_NEVER_ENDS_THE_DAY", False)
        europe.actions_remaining = 0
        europe.admin_actions_remaining = 1
        turn_before = int(europe.current_turn)
        result = _build_market(europe)
        assert result["success"] is True, result.get("message")
        assert result["action_info"]["turn_advanced"] is True
        assert int(europe.current_turn) == turn_before + 1

    def test_the_typed_end_turn_still_ends_the_dry_day(self, europe):
        """No soft-lock: 0/0 with no auto-advance is the WO-22 state, and the
        exit is the same — `end turn`."""
        europe.actions_remaining = 0
        europe.admin_actions_remaining = 1
        _build_market(europe)
        turn_before = int(europe.current_turn)
        with contextlib.redirect_stdout(io.StringIO()):
            result = CommandExecutor().execute(
                {"command": {"action": "end_turn"}, "original_command": "end turn"},
                {"world": europe})
        assert result["success"] is True, result.get("message")
        assert int(europe.current_turn) == turn_before + 1
