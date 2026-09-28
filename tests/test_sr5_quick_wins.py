"""The Chunk 5 quick-win reserve — Score Mandate (`docs/SCORE_MANDATE_PLAN.md`
§2 Chunk 5), September 28, 2026. Rules `docs/SYSTEMS_REFERENCE.md` §79.

  * SR5B-2 — an order carried out over a standing order names the order it
    set aside ("Ney's hold at Rhineland is set aside."); never on a refusal
    (SR5B-1 restored that order); the player's marshals only (lever
    `executor.AN_OVERRIDE_NAMES_THE_ORDER_IT_SETS_ASIDE`).
  * FA-66 — a fleet action can lead the morning dispatch: a decisive loss
    ("fleet_shattered", between a broken corps and a destroyed marshal), a
    beaten fleet, a decisive victory — the loser's OWN sail named through
    the naval layer's `losses_sentence` (lever
    `dispatch.FLEET_ACTIONS_LEAD_THE_DISPATCH`).
"""
import contextlib
import io
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import executor as EX
from backend.game_logic import dispatch as D
from backend.game_logic import naval as N
from backend.models.world_state import WorldState
from tests import _chip_census as C

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = (ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
            / "europe_1805.json")
DOCS = ROOT / "docs"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _boot():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def board(monkeypatch):
    C.board_env(monkeypatch)
    return M.world


def _post(text):
    return C.post(TestClient(M.app), {"command": text})


def _fought(reply):
    events = reply.get("events") or []
    return (any(isinstance(e, dict) and e.get("type") == "battle"
                for e in events) or bool(reply.get("battle_result")))


# ═══════════════════════════════════════════════════════════════════════════
# SR5B-2 — the override says what it set aside
# ═══════════════════════════════════════════════════════════════════════════

class TestTheOverrideNamesWhatItSetsAside:

    def test_a_battle_over_a_hold_names_the_hold(self, board):
        assert _post("Ney, hold Rhineland").get("success")
        reply = _post("Ney, attack Mack")
        assert _fought(reply), reply.get("message")
        assert (reply.get("message") or "").rstrip().endswith(
            "Ney's hold at Rhineland is set aside.")

    def test_a_refusal_names_nothing(self, board):
        assert _post("Soult, march to Bordelais").get("success")
        reply = _post("Soult, attack Lisbon")
        assert reply.get("success") is False
        assert "set aside" not in (reply.get("message") or "")
        assert board.get_marshal("Soult").strategic_order is not None

    @pytest.mark.parametrize("kind,target,expected", [
        ("MOVE_TO", "Lisbon", "Soult's march to Lisbon is set aside."),
        ("HOLD", "Bearn", "Soult's hold at Bearn is set aside."),
        ("PURSUE", "ArchdukeCharles",
         "Soult's pursuit of Archduke Charles is set aside."),
        ("SUPPORT", "Ney", "Soult's support of Ney is set aside."),
    ])
    def test_the_clause_names_each_kind(self, kind, target, expected):
        class _M:
            name = "Soult"

        class _O:
            command_type = kind
        _O.target = target
        assert EX.set_aside_clause(_M(), _O()) == expected

    def test_a_refusal_names_nothing_even_when_the_order_is_lost(
            self, board, monkeypatch):
        """With SR5B-1's lever down a refusal still ends the order — and the
        refusal is still not "carried out", so nothing is announced."""
        monkeypatch.setattr(EX, "A_REFUSED_ORDER_KEEPS_THE_STANDING_ORDER",
                            False)
        assert _post("Soult, march to Bordelais").get("success")
        reply = _post("Soult, attack Lisbon")
        assert reply.get("success") is False
        assert board.get_marshal("Soult").strategic_order is None
        assert "set aside" not in (reply.get("message") or "")

    def test_an_order_that_never_ended_is_not_announced(self):
        class _W:
            player_nation = "France"
        order = type("O", (), {"command_type": "HOLD", "target": "Bearn"})()
        soult = type("Soult", (), {"name": "Soult", "nation": "France"})()
        soult.strategic_order = order
        result = {"success": True, "message": "Soult drills."}
        EX.CommandExecutor._announce_set_aside(
            [(soult, order, True, "Bearn", None)], result, {"world": _W()})
        assert result["message"] == "Soult drills."

    def test_the_lever_down_is_silent(self, board, monkeypatch):
        monkeypatch.setattr(EX, "AN_OVERRIDE_NAMES_THE_ORDER_IT_SETS_ASIDE",
                            False)
        assert _post("Ney, hold Rhineland").get("success")
        reply = _post("Ney, attack Mack")
        assert _fought(reply)
        assert "set aside" not in (reply.get("message") or "")

    def test_an_enemy_marshals_order_is_not_announced(self):
        """The announcement is for the player's own answer."""
        class _W:
            player_nation = "France"
        mack = type("Mack", (), {"name": "Mack", "nation": "Austria",
                                 "strategic_order": None})()
        order = type("O", (), {"command_type": "HOLD", "target": "Swabia"})()
        result = {"success": True, "message": "Mack attacks."}
        EX.CommandExecutor._announce_set_aside(
            [(mack, order, False, "", None)], result, {"world": _W()})
        assert result["message"] == "Mack attacks."


# ═══════════════════════════════════════════════════════════════════════════
# FA-66 — a fleet action can lead the dispatch
# ═══════════════════════════════════════════════════════════════════════════

def _fleet_event(world, winner, loser, decisive, losses,
                 name="the Battle of Ushant"):
    world.log_event({"type": "trafalgar" if decisive else "fleet_action",
                     "turn": int(world.current_turn), "winner": winner,
                     "loser": loser, "decisive": decisive,
                     "battle_name": name, "context": "test",
                     "losses": losses})


class TestTheFleetActionLeads:

    def test_a_decisive_loss_leads_with_our_own_sail(self):
        w = _boot()
        with _quiet():
            action = N.resolve_fleet_action(w, "France", "Britain",
                                            context="test")
        assert action["loser"] == "France" and action["decisive"]
        head = D._build_headline(w, "France")
        assert head["class"] == "fleet_shattered"
        assert N.losses_sentence(action, "France") in head["text"]
        # SRX-19 (the exit's residue): the opponent, not "the X–Y action".
        assert head["text"].startswith(
            "Sire — The fleet is shattered in action with Britain — ")

    def test_a_beaten_fleet_is_a_lesser_lead(self):
        w = _boot()
        _fleet_event(w, "Britain", "France", False,
                     {"France": {"France": 6}, "Britain": {"Britain": 2}})
        head = D._build_headline(w, "France")
        assert head["class"] == "fleet_beaten"
        assert "France loses 6 sail" in head["text"]

    def test_a_decisive_victory_is_a_triumph(self):
        w = _boot()
        _fleet_event(w, "France", "Britain", True,
                     {"France": {"France": 3},
                      "Britain": {"Britain": 40, "Portugal": 2}})
        head = D._build_headline(w, "France")
        assert head["class"] == "fleet_triumph"
        assert head["text"] == (
            "Sire — The fleet wins its action with Britain — Britain loses "
            "40 sail; Portugal 2 beside her; we lose 3 sail.")

    def test_an_indecisive_win_is_no_triumph(self):
        w = _boot()
        _fleet_event(w, "France", "Britain", False,
                     {"France": {"France": 4}, "Britain": {"Britain": 6}})
        head = D._build_headline(w, "France")
        assert head is None or not head["class"].startswith("fleet_")

    def test_another_courts_action_is_not_ours(self):
        w = _boot()
        _fleet_event(w, "Britain", "Spain", True,
                     {"Spain": {"Spain": 15}, "Britain": {"Britain": 1}})
        head = D._build_headline(w, "France")
        assert head is None or not head["class"].startswith("fleet_")

    def test_the_weights_sit_where_the_ruling_puts_them(self):
        wts = D.HEADLINE_WEIGHTS
        assert wts["own_broken"] < wts["fleet_shattered"] < wts["marshal_destroyed"]
        assert wts["fleet_triumph"] < wts["own_broken"]
        assert wts["fleet_beaten"] < wts["vassal_lost"]
        for cls in ("fleet_shattered", "fleet_beaten", "fleet_triumph"):
            assert cls in D._HEADLINE_TEMPLATES
            assert cls in D._HEADLINE_BERTHIER_NOTES
            assert cls not in D.STANDING_HEADLINE_CLASSES

    def test_a_shattered_fleet_outranks_a_broken_corps(self):
        w = _boot()
        w.log_event({"type": "retreat", "turn": int(w.current_turn),
                     "marshal": "Ney", "nation": "France", "forced": True,
                     "region": "Swabia"})
        _fleet_event(w, "Britain", "France", True,
                     {"France": {"France": 23}, "Britain": {"Britain": 1}})
        head = D._build_headline(w, "France")
        assert head["class"] == "fleet_shattered"

    def test_the_lever_down_is_the_old_page(self, monkeypatch):
        monkeypatch.setattr(D, "FLEET_ACTIONS_LEAD_THE_DISPATCH", False)
        w = _boot()
        _fleet_event(w, "Britain", "France", True,
                     {"France": {"France": 23}, "Britain": {"Britain": 1}})
        head = D._build_headline(w, "France")
        assert head is None or not head["class"].startswith("fleet_")


class TestTheRecords:

    def test_the_systems_reference_carries_the_rules(self):
        ref = (DOCS / "SYSTEMS_REFERENCE.md").read_text(encoding="utf-8")
        assert re.search(r"^## 79\. ", ref, re.MULTILINE)
