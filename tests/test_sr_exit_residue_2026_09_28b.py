"""The Score Mandate's second session exit of September 28, 2026 — its residue.
Memo `docs/audits/SR_SESSION_EXIT_2026_09_28b.md`; rows `docs/BUG_FIXES.md`
§Score Mandate Session Exit (September 28, second), SRX-18 … SRX-23; rules
`docs/SYSTEMS_REFERENCE.md` §79.3.

  * SRX-18 — the desk names a naval yard only where one could stand, and a
    refusal ends on one period.
  * SRX-19 — the fleet-action headline names the opponent, not "the
    France–Britain action".
  * SRX-20 — "the British fleet" / "the British patrols", never "the Britain
    fleet".
  * SRX-21 — an eliminated court by its name on the rail, the dispatch and
    the log.
  * SRX-22 — the proposing court by its name in the log ("the Papal States'").
  * SRX-23 — an attack held for a declaration keeps the standing order
    (lever `executor.AN_ATTACK_HELD_FOR_A_DECLARATION_KEEPS_THE_ORDER`).
"""
import contextlib
import io
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend import campaign_log as CL
from backend.commands import executor as EX
from backend.game_logic import dispatch as D
from backend.game_logic import naval as N
from backend.game_logic.diplomacy import set_diplomatic_state
from backend.models.marshal import StrategicOrder
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


class TestSRX18TheDeskNamesAYardOnlyWhereOneCouldStand:

    def test_an_inland_answer_names_no_yard(self, board):
        reply = _post("what can I build")
        msg = reply.get("message") or ""
        assert "naval yard" not in msg, msg
        assert ".." not in msg

    def test_a_site_still_hears_of_the_yard(self, board):
        from backend.ai.question_desk import _answer_can_build
        site = N.naval_yard_sites(board, "France")[0][0]
        board.nation_gold["France"] = 20_000
        answer = _answer_can_build(board, "France", site)
        assert "naval yard (1,200g)" in answer

    def test_a_refusal_ends_on_one_period(self, board, monkeypatch):
        # After the skip above, no refusal on the boot board ends in a period
        # (the inland yard was the case the exit read), so the gate is given
        # one that does: the desk closes the sentence itself, once.
        from backend.ai.question_desk import _answer_can_build
        from backend.models import region as R
        real = R.can_build

        def gate(world, region, key, nation):
            if key == "supply_depot":
                return (False, "The magazine is full.")
            return real(world, region, key, nation)
        monkeypatch.setattr(R, "can_build", gate)
        board.nation_gold["France"] = 20_000
        answer = _answer_can_build(board, "France", "Paris")
        assert "supply depot — The magazine is full." in answer, answer
        assert ".." not in answer, answer

    def test_the_second_sentence_opens_in_capitals(self, board):
        from backend.ai.question_desk import _answer_can_build
        board.nation_gold["France"] = 0
        answer = _answer_can_build(board, "France", "Paris")
        assert answer.startswith("Nothing can be built at Paris today, Sire. ")
        tail = answer.split("Sire. ", 1)[1]
        assert tail[:1].isupper(), answer


class TestSRX19TheFleetHeadlineNamesTheOpponent:

    def test_the_loss_names_the_victor(self):
        w = _boot()
        with _quiet():
            N.resolve_fleet_action(w, "France", "Britain", context="test")
        head = D._build_headline(w, "France")
        assert head["class"] == "fleet_shattered"
        assert "in action with Britain — France loses" in head["text"]
        assert "France–Britain action" not in head["text"]

    def test_the_article_rides_the_name(self):
        w = _boot()
        w.log_event({"type": "fleet_action", "turn": int(w.current_turn),
                     "winner": "Ottoman", "loser": "France",
                     "decisive": False, "battle_name": "the X–Y action",
                     "context": "test",
                     "losses": {"France": {"France": 4},
                                "Ottoman": {"Ottoman": 1}}})
        head = D._build_headline(w, "France")
        assert "in action with the Ottoman Empire — " in head["text"]


class TestSRX20TheAdjectiveBeforeTheFleet:

    def test_the_strait_line_says_british(self, monkeypatch):
        w = _boot()
        monkeypatch.setattr(N, "_pct_roll", lambda *a, **k: True)
        assert N.resolve_diversion(w, "France")["window"] is True
        lines = [str((e.get("template_vars") or {}).get("line", ""))
                 for e in w.pending_dispatch_events
                 if e.get("type") == "strait_open"]
        assert lines, "the window queued its beat"
        text = " ".join(lines)
        assert "the British fleet off station" in text, text
        assert "the Britain fleet" not in text

    def test_the_landing_line_says_british(self, board, monkeypatch):
        oudinot_like = board.get_marshal("Lannes")
        oudinot_like.strength, oudinot_like.location = 5000, "Bordelais"
        monkeypatch.setattr(N, "_pct_roll", lambda *a, **k: True)
        reply = _post("land Lannes in Munster confirmed")
        msg = reply.get("message") or ""
        assert "the British patrols" in msg, msg
        assert "the Britain patrols" not in msg


class TestSRX21TheEliminatedCourtByName:

    def test_the_rail_the_dispatch_and_the_log(self):
        w = _boot()
        with _quiet():
            w._eliminate_nation("KingdomOfItaly")
        rail = [n for n in w.notifications.to_list()
                if "Eliminated" in str(n.get("title", ""))]
        assert rail, "the elimination reached the rail"
        text = " ".join(f"{n.get('title', '')} {n.get('message', '')}"
                        for n in rail)
        assert "The Kingdom of Italy has been eliminated" in text
        assert "KingdomOfItaly" not in text
        line = CL.format_event_oneliner({"type": "nation_eliminated",
                                         "nation": "KingdomOfItaly"})
        assert line == "The Kingdom of Italy has been eliminated from the war."
        assert D._format_dispatch_event_text(
            "nation_eliminated", {"nation": "KingdomOfItaly"}) == (
            "Sire — the Kingdom of Italy has been eliminated from the war.")

    def test_a_bare_name_takes_no_article(self):
        assert CL.format_event_oneliner({
            "type": "nation_eliminated", "nation": "Prussia"}) == (
            "Prussia has been eliminated from the war.")


    def test_the_preview_refusal_names_the_court(self, board):
        for region in board.regions.values():
            if region.controller == "KingdomOfItaly":
                region.controller = "France"
        for marshal in board.marshals.values():
            if marshal.nation == "KingdomOfItaly":
                marshal.strength = 0
        assert "KingdomOfItaly" in board.enemy_nations
        with _quiet():
            reply = TestClient(M.app).get(
                "/diplomatic_preview", params={"nation": "KingdomOfItaly"}).json()
        assert reply.get("success") is False
        assert reply.get("error") == (
            "The Kingdom of Italy has been eliminated from the war.")


class TestSRX22TheProposingCourtByName:

    @pytest.mark.parametrize("tag,expected", [
        ("Saxony", "We rejected Saxony's open borders"),
        ("PapalStates", "We rejected the Papal States' open borders"),
        ("Ottoman", "We rejected the Ottoman Empire's open borders"),
    ])
    def test_the_possessive_takes_the_name(self, tag, expected):
        line = CL.format_event_oneliner({
            "type": "ai_proposal_rejected", "source": tag,
            "proposal_type": "open_borders"})
        assert line.startswith(expected), line

    def test_the_accepted_line_takes_the_name_too(self):
        line = CL.format_event_oneliner({
            "type": "ai_proposal_accepted", "source": "PapalStates",
            "proposal_type": "open_borders"})
        assert line.startswith("We accepted the Papal States' open borders"), line


class TestSRX23AnAttackHeldForADeclarationKeepsTheOrder:

    def _stage(self, board):
        with _quiet():
            set_diplomatic_state(board, "France", "Austria", "PEACE", "test")
        lannes = board.get_marshal("Lannes")
        lannes.location = "Munich"
        board._build_marshal_index()
        order = StrategicOrder(
            command_type="MOVE_TO", target="Vienna", target_type="region",
            started_turn=1, original_command="march to Vienna",
            path=["Vienna"], issued_turn=0)
        lannes.strategic_order = order
        return lannes, order

    def test_the_march_stands_through_the_declaration(self, board):
        lannes, order = self._stage(board)
        reply = _post("Lannes, attack Tyrol")
        assert reply.get("awaiting_diplomatic_response")
        assert "set aside" not in (reply.get("message") or "")
        assert lannes.strategic_order is order

    def test_the_lever_down_loses_it(self, board, monkeypatch):
        monkeypatch.setattr(
            EX, "AN_ATTACK_HELD_FOR_A_DECLARATION_KEEPS_THE_ORDER", False)
        lannes, _order = self._stage(board)
        reply = _post("Lannes, attack Tyrol")
        assert reply.get("awaiting_diplomatic_response")
        assert lannes.strategic_order is None
        assert "Lannes's march to Vienna is set aside." in (
            reply.get("message") or "")

    def test_the_announcement_reads_the_same_predicate(self, board,
                                                       monkeypatch):
        # With SR5B-1's restore off, only the announcement's own reading of
        # the predicate stands between a held attack and "is set aside".
        monkeypatch.setattr(EX, "A_REFUSED_ORDER_KEEPS_THE_STANDING_ORDER",
                            False)
        self._stage(board)
        reply = _post("Lannes, attack Tyrol")
        assert reply.get("awaiting_diplomatic_response")
        assert "set aside" not in (reply.get("message") or "")

    def test_a_held_order_that_fought_is_carried_out(self):
        result = {"success": True, "awaiting_diplomatic_response": True,
                  "events": [{"type": "battle"}]}
        assert EX.order_was_not_carried_out(result) is False
        assert EX.order_was_not_carried_out(
            {"success": True, "awaiting_diplomatic_response": True,
             "events": []}) is True


class TestTheRecords:

    def test_the_memo_and_the_rules(self):
        assert (DOCS / "audits" / "SR_SESSION_EXIT_2026_09_28b.md").exists()
        ref = (DOCS / "SYSTEMS_REFERENCE.md").read_text(encoding="utf-8")
        assert "### 79.3" in ref
