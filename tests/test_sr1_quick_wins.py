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


# ═══════════════════════════════════════════════════════════════════════
# AAR-15 — an armistice is an armistice
# ═══════════════════════════════════════════════════════════════════════

def _ratify(world, proposer, target, ptype):
    with contextlib.redirect_stdout(io.StringIO()):
        return world._ratify_treaty({
            "proposer_nation": proposer, "target_nation": target,
            "type": ptype, "sweeteners": [], "demands": []})


class TestAAR15AnArmisticeIsAnArmistice:

    def test_a_truce_queues_the_truces_own_dispatch_event(self, europe):
        from backend.game_logic.diplomacy import ARMISTICE_AUTO_PEACE_RELATION, ARMISTICE_DURATION
        _ratify(europe, "Russia", "France", "armistice")
        types = [e["type"] for e in europe.pending_dispatch_events]
        assert "armistice_ratified" in types and "peace_ratified" not in types
        beat = next(e for e in europe.pending_dispatch_events if e["type"] == "armistice_ratified")
        assert beat["template_vars"] == {
            "proposer_nation": "Russia", "target_nation": "France", "other": "Russia",
            "turns": int(ARMISTICE_DURATION), "thaw": int(ARMISTICE_AUTO_PEACE_RELATION)}

    def test_a_peace_still_queues_the_peace(self, europe):
        _ratify(europe, "Russia", "France", "peace")
        types = [e["type"] for e in europe.pending_dispatch_events]
        assert "peace_ratified" in types and "armistice_ratified" not in types

    def test_the_log_row_keeps_its_type_and_its_transition(self, europe):
        """No new campaign-log type: the log row already said 'Armistice
        ratified'; only the dispatch's own event and headline were wrong."""
        _ratify(europe, "Russia", "France", "armistice")
        rows = [e for e in europe.event_log if e.get("type") == "peace_ratified"]
        assert rows and rows[-1]["state_transition"] == "WAR_TO_ARMISTICE"

    def test_the_headline_is_the_truce_with_its_clock(self, europe):
        from backend.game_logic import dispatch as D
        from backend.game_logic.diplomacy import ARMISTICE_AUTO_PEACE_RELATION, ARMISTICE_DURATION
        _ratify(europe, "Russia", "France", "armistice")
        europe.current_turn += 1
        with contextlib.redirect_stdout(io.StringIO()):
            morning = D.build_morning_dispatch(europe)
        text = json_dumps(morning)
        assert "Sire — a truce with Russia is signed." in text
        assert (f"The fighting stops for {ARMISTICE_DURATION} turns; peace if relations "
                f"heal to {ARMISTICE_AUTO_PEACE_RELATION} or better, else the war resumes.") in text
        assert "peace with Russia is signed" not in text
        assert "the war ends in a stalemate" not in text

    def test_the_truce_class_is_registered_everywhere(self):
        from backend.game_logic import dispatch as D
        assert "truce_signed" in D.HEADLINE_WEIGHTS
        assert "truce_signed" in D._HEADLINE_TEMPLATES
        assert "truce_signed" in D._HEADLINE_BERTHIER_NOTES
        assert "armistice_ratified" in D._DIPLOMATIC_EVENT_TEMPLATES
        assert D._DIPLOMATIC_EVENT_PRIORITY["armistice_ratified"] == "HIGH"
        assert D.HEADLINE_WEIGHTS["truce_signed"] < D.HEADLINE_WEIGHTS["peace_signed"]


def json_dumps(obj) -> str:
    import json
    return json.dumps(obj, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════
# GE-V §4 nits — the Congress price levers
# ═══════════════════════════════════════════════════════════════════════

class TestGEVSection4Nits:

    def _war_row(self, europe, court):
        from backend.game_logic import congress
        row = congress.answer(europe, court)
        assert row.get("by") == "war", row
        return row

    def test_the_capital_lever_names_it_as_the_capital(self, europe):
        from backend.game_logic import congress
        row = self._war_row(europe, "Russia")
        price = congress.price(europe, "Russia", row)
        texts = [lv["text"] for lv in price["levers"]]
        capital = europe.get_nation_capital("Russia")
        assert f"take its capital, {capital}" in texts
        assert not any(t == f"take {capital}" for t in texts)

    def test_an_island_courts_ports_lever_comes_before_its_capital(self, europe):
        from backend.game_logic import congress
        row = self._war_row(europe, "Britain")
        price = congress.price(europe, "Britain", row)
        keys = [lv["key"] for lv in price["levers"]]
        assert "ports" in keys and "capital" in keys
        assert keys.index("ports") < keys.index("capital")
        assert keys[0] == "war"

    def test_a_continental_court_keeps_its_capital_ahead_of_the_ports(self, europe):
        from backend.game_logic import congress
        row = self._war_row(europe, "Austria")
        keys = [lv["key"] for lv in congress.price(europe, "Austria", row)["levers"]]
        assert keys[:3] == ["war", "capital", "peace"]


# ═══════════════════════════════════════════════════════════════════════
# The School of War's Congress card
# ═══════════════════════════════════════════════════════════════════════

class TestTheSchoolTeachesTheCongress:

    def test_the_card_sits_between_the_wooden_wall_and_the_instruments(self):
        from backend.game_logic import tutorial_state as T
        ids = [s[0] for s in T.STEPS]
        assert ids.index("congress") == ids.index("naval") + 1
        assert ids.index("free_books") == ids.index("congress") + 1
        titles = dict((s[0], s[2]) for s in T.STEPS)
        assert titles["congress"] == "XVII. The Congress of Paris"
        assert titles["free_books"] == "XVIII. The Instruments"
        assert titles["handoff"] == "XIX. The Lesson Ends"
        gates = dict((s[0], s[1]) for s in T.STEPS)
        assert gates["congress"] == 11 and gates["free_books"] == 12 and gates["handoff"] == 13

    def test_the_card_teaches_the_road_and_names_its_surfaces(self):
        src = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
               / "scripts" / "tutorial_overlay.gd").read_text(encoding="utf-8")
        card = src.split('"id": "congress"', 1)[1].split('"id": "free_books"', 1)[0]
        assert "forty-five provinces by TITLE" in card
        assert "a signed peace titles what you keep of the loser's" in card
        assert "CONGRESS tab" in card and "names each held one's road to title" in card
        assert '"advance": "_pred_turn_gte_12"' in card
        assert "func _pred_turn_gte_13(" in src
