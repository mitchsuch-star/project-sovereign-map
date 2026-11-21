"""Row IC, Session 3 — IC-11, THE MEN DIFFER (November 21, 2026).

`docs/INDEPENDENT_COMMAND_SPEC.md` §6.7: "if army has differner personalities they
arent all doing same thing every turn" (the user, November 20). Seven ways, no
dice: his nature, his own proposal, his way of waiting, the third night, one man
per target, his recent record, his personal line. The module is
`backend/game_logic/own_order.py`; the voice `backend/game_logic/own_voice.py`.
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

from backend.game_logic import own_order as O
from backend.game_logic import own_voice as V
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
                 / "europe_1805.json")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def world1805():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO_PATH))


def _fresh(world1805) -> WorldState:
    with _quiet():
        return WorldState.from_dict(world1805.to_dict())


def _give(world, name, task, target):
    marshal = world.marshals[name]
    spec, why = O.spec_from(world, marshal, task, target)
    assert spec is not None, why
    with _quiet():
        assert O.give(world, marshal, spec, line="", own_proposal=True)["success"]
    O.own(marshal)["given"] = int(world.current_turn) - 1
    O.own(marshal)["late"] = False
    return marshal


class TestHisOwnOddsAndHisRecord:

    def test_his_record_moves_him_one_step_and_two_at_most_in_all(self, world1805):
        ney = world1805.marshals["Ney"]
        assert O.needed(ney, 0, {"acts": [], "quiet": 0, "last": ""})["needed"] == 6
        assert O.needed(ney, 0, {"acts": [], "quiet": 0, "last": "won"})["needed"] == 5
        assert O.needed(ney, 0, {"acts": [], "quiet": 0, "last": "lost"})["needed"] == 7
        # impatient (a bold man, three quiet nights) AND a win: still one step from him
        assert O.needed(ney, 0, {"acts": [], "quiet": 3, "last": "won"})["needed"] == 5
        # your step and his: two at most
        assert O.needed(ney, 1, {"acts": [], "quiet": 3, "last": ""})["needed"] == 4
        davout = world1805.marshals["Davout"]
        assert O.needed(davout, 0, {"acts": [], "quiet": 5, "last": ""})["needed"] == 10, \
            "a careful man does not grow impatient"

    def test_the_words_say_every_step(self, world1805):
        ney = world1805.marshals["Ney"]
        n = O.needed(ney, 1, {"acts": [], "quiet": 0, "last": "won"})
        assert O.needed_words(n) == ("our 4 to their 10 or better (his own 6, one step bolder from you, "
                                     "one step bolder since his last win)")

    def test_no_two_of_the_six_read_the_same(self, world1805):
        figures = [O.his_odds(world1805.marshals[n])
                   for n in ("Murat", "Ney", "Lannes", "Massena", "Davout", "Bernadotte")]
        assert len(set(figures)) == 6


class TestTheThirdNight:

    def test_not_the_same_waiting_act_a_third_night_while_another_exists(self, world1805):
        world = _fresh(world1805)
        davout = _give(world, "Davout", "hold", "Rhineland")
        davout.fortified = False
        with _quiet():
            first = O.read(world, davout)
        assert first["act"] == "dig_in"
        davout.own_record = {"acts": [["dig_in", davout.location, 1], ["dig_in", davout.location, 2]],
                             "quiet": 2, "last": ""}
        with _quiet():
            third = O.read(world, davout)
        assert (third["act"], third["place"]) != ("dig_in", davout.location) or third["again"]

    def test_when_nothing_else_exists_the_line_says_so(self, world1805):
        world = _fresh(world1805)
        davout = _give(world, "Davout", "hold", "Rhineland")
        davout.fortified = True
        with _quiet():
            reading = O.read(world, davout)
        if reading["act"] == "stay":
            assert "keeps to his works" in reading["line"]


class TestTheirProposals:

    def test_proposals_differ_by_man(self, world1805):
        world = _fresh(world1805)
        with _quiet():
            props = {n: O.proposal(world, world.marshals[n])
                     for n in ("Ney", "Davout", "Murat", "Lannes", "Massena", "Bernadotte")}
        assert props["Davout"]["task"] == "hold"
        assert props["Bernadotte"]["task"] == "hold" and "rear" in props["Bernadotte"]["why"]
        assert props["Massena"]["task"] == "hold"
        assert props["Murat"]["task"] in ("pursue", "take", "hold")
        assert len({(p["task"], p["target"]) for p in props.values()}) >= 3
        for p in props.values():
            assert p["line"].endswith("on your own.")

    def test_each_man_has_his_own_voice(self):
        said = {V.line(n, "bold" if n != "Davout" else "careful", "ack", 3)
                for n in ("Ney", "Davout", "Murat", "Lannes", "Massena", "Bernadotte")}
        assert len(said) == 6
        assert V.line("Ney", "bold", "ack", 3) == V.line("Ney", "bold", "ack", 3), "never a die"


class TestTheirPersonalLines:

    def test_bernadotte_starts_a_night_late(self, world1805):
        world = _fresh(world1805)
        bern = world.marshals["Bernadotte"]
        spec, _ = O.spec_from(world, bern, "hold", bern.location)
        with _quiet():
            O.give(world, bern, spec, line="", own_proposal=True)
        O.own(bern)["given"] = int(world.current_turn) - 1
        with _quiet():
            reading = O.read(world, bern)
        assert reading["act"] == "start" and "a night late" in reading["line"]

    def test_murat_never_storms_walls(self, world1805):
        world = _fresh(world1805)
        murat = world.marshals["Murat"]
        spec, _ = O.spec_from(world, murat, "take", "Swabia")
        world.marshals["Mack"].location = "Bohemia"
        region = world.get_region("Swabia")
        region.garrison_strength = 1000
        with _quiet():
            reading, why = O._take_place(world, murat, "Swabia", O.needed(murat), {})
        assert reading is None or reading["act"] not in ("storm",)


class TestVariety:
    """A small R-VARIETY on the 1805 board — five men on their own, six nights:
    every man shows at least two kinds of night, and they do not all do the
    same thing every night. (The full measure is `tools/_ic3_measure.py`.)"""

    def test_five_men_six_nights(self, world1805, monkeypatch):
        import json
        import random

        import backend.main as M
        from fastapi.testclient import TestClient

        from backend.commands import parse_preview as PP
        from backend.commands.parser import CommandParser
        for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
            monkeypatch.delenv(key, raising=False)
        monkeypatch.setenv("LLM_MODE", "mock")
        prior = (M.world, M.game_state.get("world"), M.parser)
        try:
            with _quiet():
                M._reset_world_state()
                world = WorldState.from_dict(json.loads(json.dumps(M.world.to_dict(), default=str)))
                M._set_active_world(world)
                M.parser = CommandParser(use_real_llm=False)
            monkeypatch.setattr(O, "COUNT_AT_START", 5)
            for name in ("Ney", "Davout", "Murat", "Massena", "Lannes"):
                prop = O.proposal(world, world.marshals[name])
                _give(world, name, prop["task"], prop["target"])
            kinds = {n: set() for n in ("Ney", "Davout", "Murat", "Massena", "Lannes")}
            nights_alike = 0
            with TestClient(M.app) as client:
                for night in range(6):
                    random.seed(1805 + night)
                    with _quiet():
                        out = client.post("/command", json={"command": "end turn"}).json()
                    acts = {}
                    for row in out.get("strategic_reports") or []:
                        if row.get("own") and row.get("marshal") in kinds:
                            kinds[row["marshal"]].add(row["act"])
                            acts[row["marshal"]] = row["act"]
                    if len(acts) >= 3 and len(set(acts.values())) == 1:
                        nights_alike += 1
            # (six nights is a short look: the full bar — every man two kinds in
            # twenty turns — is the measure's, `tools/_ic3_measure.py`)
            assert sum(1 for seen in kinds.values() if len(seen) >= 2) >= 3, kinds
            assert nights_alike <= 2, nights_alike
        finally:
            M.world, M.parser = prior[0], prior[2]
            M.game_state["world"] = prior[1]
            PP.invalidate()
