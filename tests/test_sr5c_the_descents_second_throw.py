"""SR-5c "The Descent's second throw" — Score Mandate Chunk 5
(`docs/SCORE_MANDATE_PLAN.md` §2), September 28, 2026. Rules
`docs/SYSTEMS_REFERENCE.md` §78.

RULED by the user ("Readiness sets the odds, repeatable"): the Grand
Diversion may be sailed again `DIVERSION_WAIT_TURNS` (4) after its last
throw, and its odds are the fleet's readiness less 25 — 45 at the boot
readiness 70, 50 at the drill ceiling 75, 25 at the blockade floor 50. A
failed throw leaves a fleet whose readiness must be rebuilt before the next
is worth sailing. The wait resets when the naval war ends. One source,
`naval.diversion_odds`, for the roll, the confirm, the chip, the terms and
the expedition's diversion lever. Lever `naval.THE_DIVERSION_IS_THROWN_AGAIN`.
"""
import contextlib
import io
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.game_logic import naval as N
from backend.game_logic.diplomacy import set_diplomatic_state
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


def _roll(monkeypatch, result):
    """Force the seeded roll's outcome and record the odds it was asked."""
    asked = []

    def fake(world, namespace, chance_pct):
        asked.append(int(chance_pct))
        return result
    monkeypatch.setattr(N, "_pct_roll", fake)
    return asked


def _chip(world):
    for chip in N.build_admiralty_report(world).get("chips", []):
        if chip["label"] == "The Grand Diversion":
            return chip
    return {}


def _stage_camp(world):
    rec = N.get_fleet(world, "France")
    camp = list(rec.get("camp_provinces") or [])
    french = world.get_marshals_by_nation("France")
    french[0].location = camp[0]
    french[0].strength = N.DESCENT_CAMP_MIN_TROOPS + 1000
    rec["camp_turns"] = N.DESCENT_CAMP_STAGED_TURNS
    world._build_marshal_index()


class TestTheOdds:

    @pytest.mark.parametrize("readiness,odds", [
        (70, 45), (75, 50), (50, 25), (100, 75), (40, 15)])
    def test_readiness_sets_the_odds(self, readiness, odds):
        w = _boot()
        N.get_fleet(w, "France")["readiness"] = readiness
        assert N.diversion_odds(w, "France") == odds

    def test_the_odds_are_clamped(self):
        w = _boot()
        N.get_fleet(w, "France")["readiness"] = 10
        assert N.diversion_odds(w, "France") == N.DIVERSION_ODDS_FLOOR
        N.get_fleet(w, "France")["readiness"] = 150
        assert N.diversion_odds(w, "France") == N.DIVERSION_ODDS_CEILING

    def test_the_boot_odds_are_the_old_odds(self):
        """At the boot readiness 70 the new rule reads the old 45 — the
        first throw of a campaign is the throw it always was."""
        w = _boot()
        assert N.get_fleet(w, "France")["readiness"] == 70
        assert N.diversion_odds(w, "France") == N.DIVERSION_SUCCESS_PCT

    def test_the_roll_reads_the_odds(self, monkeypatch):
        w = _boot()
        N.get_fleet(w, "France")["readiness"] = 60
        asked = _roll(monkeypatch, True)
        result = N.resolve_diversion(w, "France")
        assert asked == [35]
        assert result["odds"] == 35 and result["window"] is True

    def test_the_odds_are_read_before_the_failure_docks_readiness(
            self, monkeypatch):
        w = _boot()
        N.get_fleet(w, "France")["readiness"] = 68
        asked = _roll(monkeypatch, False)
        result = N.resolve_diversion(w, "France")
        assert asked == [43] and result["odds"] == 43
        assert result["window"] is False


class TestTheWait:

    def test_the_feint_waits_four_turns_then_sails_again(self, monkeypatch):
        w = _boot()
        _roll(monkeypatch, True)
        start = int(w.current_turn)
        assert N.resolve_diversion(w, "France")["window"] is True
        for elapsed in range(N.DIVERSION_WAIT_TURNS):
            w.current_turn = start + elapsed
            N.get_fleet(w, "France")["window_turns"] = 0
            refused = N.resolve_diversion(w, "France")
            assert refused["success"] is False
            left = N.DIVERSION_WAIT_TURNS - elapsed
            assert (f"may try it again in {left} turn"
                    f"{'s' if left != 1 else ''}") in refused["message"]
        w.current_turn = start + N.DIVERSION_WAIT_TURNS
        again = N.resolve_diversion(w, "France")
        assert again["success"] is True and again["window"] is True
        assert N.last_diversion_turn(N.get_fleet(w, "France")) == int(
            w.current_turn)

    def test_a_failed_throw_says_when_she_may_try_again(self, monkeypatch):
        w = _boot()
        _roll(monkeypatch, False)
        result = N.resolve_diversion(w, "France")
        assert result["window"] is False
        assert (f"She may try it again in {N.DIVERSION_WAIT_TURNS} turns"
                in result["message"])

    def test_the_wait_resets_with_the_naval_war(self):
        w = _boot()
        rec = N.get_fleet(w, "France")
        rec["diversion_last_turn"] = int(w.current_turn)
        with _quiet():
            for nation in ("Britain", "Russia"):
                set_diplomatic_state(w, "France", nation, "PEACE", "test")
            N.process_naval_turn(w)
        assert not N.has_naval_war(w, "France")
        assert rec["diversion_last_turn"] == -1

    def test_inside_its_war_the_wait_stands(self):
        w = _boot()
        rec = N.get_fleet(w, "France")
        rec["diversion_last_turn"] = int(w.current_turn)
        with _quiet():
            N.process_naval_turn(w)
        assert rec["diversion_last_turn"] == int(w.current_turn)
        assert N.diversion_wait(w, "France") == N.DIVERSION_WAIT_TURNS

    def test_the_terms_and_the_chip_name_the_wait(self):
        w = _boot()
        N.get_fleet(w, "France")["diversion_last_turn"] = int(w.current_turn)
        terms = N.diversion_terms_for(w, "France")
        ready = terms[2]
        assert ready["met"] is False
        assert ready["unmet"] == (
            "the fleet sailed the feint this turn — she may try it again "
            f"in {N.DIVERSION_WAIT_TURNS} turns")
        chip = _chip(w)
        assert chip["enabled"] is False and ready["unmet"] in chip["reason"]
        w.current_turn += N.DIVERSION_WAIT_TURNS
        assert _chip(w)["enabled"] is True


class TestTheSurfaces:

    def test_the_confirm_quotes_the_readiness_odds_and_the_wait(self, board):
        rec = N.get_fleet(board, "France")
        rec["readiness"] = 62
        reply = _post("order the diversion")
        msg = reply.get("message") or ""
        assert "37 times in 100 at her readiness (62)" in msg, msg
        assert (f"she may try it again {N.DIVERSION_WAIT_TURNS} turns "
                f"from now") in msg
        assert "once only" not in msg
        assert N.last_diversion_turn(rec) == -1, "the quote spent nothing"

    def test_a_waiting_fleet_is_refused_on_the_typed_road(self, board):
        N.get_fleet(board, "France")["diversion_last_turn"] = int(
            board.current_turn)
        reply = _post("order the diversion")
        assert reply.get("success") is False
        assert "may try it again in" in (reply.get("message") or "")

    def test_the_chip_note_states_the_odds_and_the_wait(self):
        w = _boot()
        note = _chip(w)["note"]
        assert note.startswith(
            f"45 in 100 at readiness 70 — and again "
            f"{N.DIVERSION_WAIT_TURNS} turns after, whatever the outcome")

    def test_the_expedition_lever_reads_the_same_odds(self):
        w = _boot()
        N.get_fleet(w, "France")["readiness"] = 60
        levers = N.expedition_odds_levers(w, "France", "London", 9000)
        div = next(lv for lv in levers if lv["key"] == "diversion")
        assert div["label"] == "a won diversion first (35 in 100)"

    def test_the_admiralty_payload_carries_the_wait_and_the_odds(self):
        w = _boot()
        own = N.build_admiralty_report(w)["own_fleet"]
        assert own["diversion_wait"] == 0 and own["diversion_odds"] == 45
        assert own["diversion_used"] is False
        N.get_fleet(w, "France")["diversion_last_turn"] = int(w.current_turn)
        own = N.build_admiralty_report(w)["own_fleet"]
        assert own["diversion_wait"] == N.DIVERSION_WAIT_TURNS
        assert own["diversion_used"] is True

    def test_the_help_line(self, board):
        reply = _post("help")
        text = reply.get("message") or ""
        assert "again 4 turns after the last" in text


class TestTheAIWaitsToo:
    """GR5: the AI rung reads the same wait."""

    def test_the_rung_waits_out_the_feint(self):
        w = _boot()
        _stage_camp(w)
        assert N.find_ai_diversion(w, "France") is not None
        N.get_fleet(w, "France")["diversion_last_turn"] = int(w.current_turn)
        assert N.find_ai_diversion(w, "France") is None
        w.current_turn += N.DIVERSION_WAIT_TURNS
        assert N.find_ai_diversion(w, "France") is not None


class TestTheMigration:

    def test_a_spent_card_becomes_a_throw_on_the_load_turn(self):
        w = _boot()
        rec = N.get_fleet(w, "France")
        rec.pop("diversion_last_turn", None)
        rec["diversion_used"] = True
        w.current_turn = 12
        with _quiet():
            loaded = WorldState.from_dict(w.to_dict())
        lrec = N.get_fleet(loaded, "France")
        assert "diversion_used" not in lrec
        assert lrec["diversion_last_turn"] == 12
        assert N.diversion_wait(loaded, "France") == N.DIVERSION_WAIT_TURNS

    def test_an_unspent_card_becomes_never(self):
        w = _boot()
        rec = N.get_fleet(w, "France")
        rec.pop("diversion_last_turn", None)
        rec["diversion_used"] = False
        with _quiet():
            loaded = WorldState.from_dict(w.to_dict())
        lrec = N.get_fleet(loaded, "France")
        assert "diversion_used" not in lrec
        assert lrec["diversion_last_turn"] == -1

    def test_a_record_still_carrying_the_flag_reads_as_thrown(self):
        assert N.last_diversion_turn({"diversion_used": True}) == 0
        assert N.last_diversion_turn({"diversion_used": False}) == -1
        assert N.last_diversion_turn({}) == -1

    def test_the_boot_record_carries_the_new_field(self):
        w = _boot()
        for _nation, rec in N.iter_fleets(w):
            assert rec["diversion_last_turn"] == -1
            assert "diversion_used" not in rec


class TestTheLever:

    def test_lever_down_is_once_per_war_at_45(self, monkeypatch):
        monkeypatch.setattr(N, "THE_DIVERSION_IS_THROWN_AGAIN", False)
        w = _boot()
        N.get_fleet(w, "France")["readiness"] = 60
        assert N.diversion_odds(w, "France") == N.DIVERSION_SUCCESS_PCT
        assert _chip(w)["note"].startswith(
            f"{N.DIVERSION_SUCCESS_PCT}% — and once only, this war")
        N.get_fleet(w, "France")["diversion_last_turn"] = int(w.current_turn)
        w.current_turn += 40
        refused = N.resolve_diversion(w, "France")
        assert refused["success"] is False
        assert "already attempted its grand diversion" in refused["message"]
        assert N.diversion_terms_for(w, "France")[2]["unmet"] == (
            "the diversion is already spent this war")


class TestTheRecords:

    def test_the_systems_reference_carries_the_rules(self):
        ref = (DOCS / "SYSTEMS_REFERENCE.md").read_text(encoding="utf-8")
        assert re.search(r"^## 78\. ", ref, re.MULTILINE)

    def test_the_plan_records_the_slice(self):
        plan = (DOCS / "SCORE_MANDATE_PLAN.md").read_text(encoding="utf-8")
        assert "SR-5c The Descent's second throw LANDED" in plan
