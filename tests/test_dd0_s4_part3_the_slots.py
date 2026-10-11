"""DD-0 S4 part 3 "The Command Road" — THE SPINE SPLIT and THE SLOT READER
(October 10, 2026; PRE_DEPLOY_PLAN.md §3.0 "S4 landing record, part 3";
rules SYSTEMS_REFERENCE.md §104; rows BUG_FIXES.md §DD-0 S4 DD0-11 … DD0-17).

The mock chain is a chain of named stages along the parse trace's seams
(`_chain_cheat` … `_chain_finish`) reading ONE `_ChainState`; the slot
reader (`_chain_read_slots`) consumes the Reading's slots — the addressee,
the places, the foes, what is left — when the verb chain found nothing:
"take your horse to Rhineland", "Murat — rhineland — go.", "ney franconia
pls" are one reading (a march); "I want Ney on Mack this turn", "ney go get
mack" are another (an attack). The strategic layer keeps the chain's known
place instead of re-scanning the composed string. Each DD0 row is driven
through the real `POST /command` on a fresh 1805 board with the trace on.
"""
from __future__ import annotations

import contextlib
import io
import os
import tempfile

import pytest

from backend.ai import reading as R

FRIENDS = ["Ney", "Davout", "Soult", "Lannes", "Murat", "Massena", "Bernadotte", "Napoleon"]
FOES = ["Mack", "ArchdukeJohn", "ArchdukeCharles", "Kutuzov"]
PLACES = ["Rhineland", "Swabia", "Lorraine", "Frankfurt", "Munich", "Milan", "Tyrol",
          "Franconia", "Savoy", "Paris", "Franche-Comte"]
NATIONS = ["Austria", "Prussia", "Sweden", "Bavaria"]


@pytest.fixture(scope="module")
def client():
    os.environ["LLM_MODE"] = "mock"
    os.environ.setdefault("INK_IRON_SAVE_DIR", tempfile.mkdtemp(prefix="dd0_s4p3_"))
    from fastapi.testclient import TestClient
    with contextlib.redirect_stdout(io.StringIO()):
        import backend.main as M
        c = TestClient(M.app)
    originals = (M.game_state["world"], M.world, M.parser)
    try:
        yield c, M
    finally:
        M.game_state["world"], M.world, M.parser = originals


def _post(client, line):
    c, M = client
    from backend.ai import parser_eval as pe
    from backend.commands.parser import CommandParser
    with contextlib.redirect_stdout(io.StringIO()):
        world = pe.build_world("1805")
        M.game_state["world"] = world
        M.world = world
        M.parser = CommandParser(use_real_llm=False)
        r = c.post("/command", json={"command": line, "trace": True})
    return r.json()


def _rules(reply, stage):
    return [r["rule"] for r in reply.get("parse_trace", []) if r["stage"] == stage]


def _slots(line):
    return R.slots_of(line, FRIENDS, FOES, PLACES, NATIONS)


# ═════════════════════════ THE SPINE SPLIT ═══════════════════════════════════

class TestTheSpineSplit:
    def test_the_chain_is_named_stages_reading_one_state(self):
        import backend.ai.llm_client as L
        names = ["_chain_cheat", "_chain_first_contact", "_chain_guards", "_chain_cabinet",
                 "_chain_question", "_chain_bind_marshal", "_chain_meta", "_chain_read_action",
                 "_chain_read_target", "_chain_read_slots", "_chain_finish"]
        for n in names:
            assert callable(getattr(L.LLMClient, n)), n
        assert L._ChainState(command_text="x", game_state=None).action == "unknown"

    def test_the_generator_walks_every_stage(self):
        """`tools/gen_routed_order_words.py` harvests the routing branches
        from the stages, so a keyword added to a stage reaches the
        addressee rule (CX-R1) exactly as it did from the one body."""
        from tools import gen_routed_order_words as GEN
        for n in ("_chain_cabinet", "_chain_read_action", "_chain_meta"):
            assert n in GEN.ROUTER_FUNCTIONS

    def test_the_invest_idiom_is_consulted(self, client):
        """The `or` used to sit inside the `any(...)` call: a non-empty
        keyword list short-circuited the idiom and `invest holland 50`
        shrugged (found by the split; DD0-17)."""
        import backend.ai.llm_client as L
        from backend.ai import parser_eval as pe
        _, M = client
        with contextlib.redirect_stdout(io.StringIO()):
            c = L.LLMClient(use_real_api=False)
            M.game_state["world"] = M.world = pe.build_world("1805")
            gs = M.get_llm_game_state()
        r = c._parse_with_mock_chain("invest holland 50", gs)
        assert r.action == "invest_vassal" and r.target == "Holland"
        r = c._parse_with_mock_chain("invest 100 gold in holland", gs)
        assert r.action == "invest_vassal" and r.target == "Holland"


# ═════════════════════════ THE SLOT VIEW, PURE ═══════════════════════════════

class TestTheSlotView:
    @pytest.mark.parametrize("line,dest,residue", [
        ("Murat, take your horse to Rhineland", "Rhineland", ["take", "your", "horse", "to"]),
        ("Davout, get out of Rhineland and into Frankfurt", "Frankfurt", ["get", "out", "of", "and", "into"]),
        ("Murat to Franconia, by way of Rhineland", "Franconia", ["to", "by", "way", "of"]),
        ("Murat — rhineland — go.", "Rhineland", ["go"]),
        ("ney franconia pls", "Franconia", ["pls"]),
        ("Shift Bernadotte west to Rhineland", "Rhineland", ["shift", "west", "to"]),
    ])
    def test_a_march_by_slots(self, line, dest, residue):
        s = _slots(line)
        assert s.destination() == dest and s.residue == residue
        assert R.march_by_slots(s)

    @pytest.mark.parametrize("line", [
        "Ney, Rhineland is lost", "Ney, remember Rhineland", "Davout, hold Lorraine",
        "Ney, wait for Mack", "Lannes, make your way to Swabia",   # the last is IQ-9's (live)
    ])
    def test_not_a_march_by_slots(self, line):
        assert not R.march_by_slots(_slots(line))

    @pytest.mark.parametrize("line,foe", [
        ("I want Ney on Mack this turn, no excuses.", "Mack"),
        ("ney go get mack", "Mack"),
        ("Massena, you have forty-two thousand men. Use them on John.", "ArchdukeJohn"),
    ])
    def test_an_attack_by_slots(self, line, foe):
        s = _slots(line)
        assert s.foes == [foe] and R.attack_by_slots(s, NATIONS)

    @pytest.mark.parametrize("line", ["Ney, Mack", "Ney, attack Mack", "Ney, wait for Mack"])
    def test_not_an_attack_by_slots(self, line):
        assert not R.attack_by_slots(_slots(line), NATIONS)

    @pytest.mark.parametrize("line,composed,rule", [
        ("Soult — Paris — the Emperor wants him near", "Soult — Paris", "peel_comma_aside"),
        ("Lannes — Rhineland, double quick", "Lannes — Rhineland", "peel_comma_aside"),
        ("I want Ney on Mack this turn, no excuses.", "I want Ney on Mack this turn", "peel_comma_aside"),
        ("Soult, to Franche-Comte. The roads are dry.", "Soult, to Franche-Comte", "peel_trailing_statement"),
        ("Ney: Frankfurt. Davout: stays.", "Ney: Frankfurt, then Davout, hold", "peel_second_telegraph"),
        ("Massena, you have forty-two thousand men. Use them on John.", "Massena, Use them on John",
         "peel_statement_after_address"),
        ("pursue john massena", "Massena, pursue john", "peel_trailing_vocative"),
        ("Marshal Soult will be so good as to bring his corps up to the Rhineland",
         "Soult, bring his corps up to the Rhineland", "read_address"),
    ])
    def test_the_new_peels(self, line, composed, rule):
        r = R.read(line, FRIENDS, FOES, PLACES, NATIONS)
        assert r.text() == composed
        assert rule in [x[0] for x in r.rows]


# ═════════════════════════ THE ROWS, DRIVEN ══════════════════════════════════

class TestDD011TheForbiddenFightDoesNotFight:
    def test_eyes_only_no_fighting_scouts(self, client):
        reply = _post(client, "Murat, your light horse to the Tyrol — eyes only, no fighting.")
        assert reply["success"] is True
        assert reply["message"].startswith("Murat scouts Tyrol")
        assert "MUSTER" not in reply["message"]


class TestDD012TheDeclarationOutranksTheMission:
    def test_inform_the_courts_declares(self, client):
        reply = _post(client, "Berthier, inform the courts: France declares war on Sweden.")
        assert "war purpose against Sweden" in reply["message"]
        assert "charm" not in reply["message"]


class TestDD013TheEpithetAsTheObject:
    def test_murat_will_support_the_iron_marshal(self, client):
        reply = _post(client, "Murat will support the Iron Marshal.")
        assert "Bernadotte" not in reply["message"]
        trace = reply.get("parse_trace", [])
        detected = [r for r in trace if r["stage"] == "strategic" and r["rule"] == "detected"]
        assert detected and detected[0]["detail"].get("target") == "Davout"


class TestDD014TheOrderBehindAQuestion:
    def test_make_it_so_is_the_march(self, client):
        reply = _post(client, "Can Lannes be in Rhineland this turn? Make it so.")
        assert "split_question_and_order" in _rules(reply, "parser")
        assert "yields" not in reply["message"]          # not the income desk
        assert "Lannes" in reply["message"]

    def test_do_it_is_the_attack(self, client):
        reply = _post(client, "Why hasn't Massena attacked Archduke John yet? Do it.")
        assert "MUSTER" in reply["message"] and "Massena" in reply["message"]

    def test_scout_for_him_keeps_the_question_when_the_foe_is_unseen(self, client):
        reply = _post(client, "Where is Kutuzov? Scout for him.")
        assert "no word of Kutuzov" in reply["message"]


class TestDD015TheMarchRegister:
    @pytest.mark.parametrize("line,who", [
        ("Murat, take your horse to Rhineland", "Murat"),
        ("Soult, shift your corps to Savoy", "Soult"),
        ("Soult, to Franche-Comte. The roads are dry.", "Soult"),
        ("Murat to Franconia, by way of Rhineland", "Murat"),
        ("Soult — Paris — the Emperor wants him near", "Soult"),
        ("Lannes and Murat to Lorraine, together", "Lannes"),
        ("Murat — rhineland — go.", "Murat"),
        ("mve murat to rhineland", "Murat"),
    ])
    def test_the_march_goes_out(self, client, line, who):
        reply = _post(client, line)
        assert reply["success"] is True, reply["message"]
        assert reply["message"].startswith(who), reply["message"]
        assert "moves" in reply["message"] or "marching" in reply["message"]

    def test_the_slot_reader_is_on_the_trace(self, client):
        reply = _post(client, "ney franconia pls")
        assert "slots_march" in _rules(reply, "mock_chain")

    def test_his_corps_is_the_men_not_the_province(self, client):
        reply = _post(client, "Marshal Davout is to march his corps to Franconia.")
        assert reply["success"] is True
        assert "Franconia" in reply["message"] and "His Corps" not in reply["message"]

    def test_the_second_telegraph_rides_the_relay(self, client):
        reply = _post(client, "Ney: Frankfurt. Davout: stays.")
        assert "Davout, hold" in reply["message"]


class TestDD016TheAttackRegister:
    @pytest.mark.parametrize("line,who", [
        ("I want Ney on Mack this turn, no excuses.", "Ney"),
        ("ney go get mack", "Ney"),
        ("Massena, you have forty-two thousand men. Use them on John.", "Massena"),
    ])
    def test_the_attack_musters(self, client, line, who):
        reply = _post(client, line)
        assert "MUSTER" in reply["message"] and who in reply["message"]

    def test_the_inverted_name_pursues(self, client):
        reply = _post(client, "pursue john massena")
        assert reply["message"].startswith("Massena pursues Archduke John")

    def test_keep_after_pursues(self, client):
        reply = _post(client, "Murat, keep after the Austrians under Mack")
        assert reply["message"].startswith("Murat pursues Mack")

    def test_get_after_stays_the_live_parsers(self, client):
        """IQ-9's cassette gate is the authority: the mock never reads it."""
        reply = _post(client, "Ney, get after Mack")
        assert reply["success"] is False


class TestDD017TheDesksIdioms:
    @pytest.mark.parametrize("line,expect", [
        ("Lannes, patrol toward Bern and report", "Lannes scouts Bern"),
        ("Soult, dog Mack's heels", "Soult pursues Mack"),
        ("Bernadotte, square up — Deroy has horse", "Bernadotte forms square"),
        ("reward soult estate", "Reward dialog is open"),
        ("Ney has earned a title; give him one.", "Reward dialog is open"),
        ("Establish the Grand Quartier General", "Grand Quartier"),
        ("Berthier, the Staff law is to be enacted this turn", "Grand Quartier"),
        ("Let the Artillery Reserve be made law", "Artillery Reserve"),
        ("invest holland 50", "Holland"),
        ("Let the turn end.", "Type 'end turn'"),
        ("That is all for today, Berthier. Close the day.", "Type 'end turn'"),
        ("Give Oudinot a baton", "Commissioning Oudinot"),
        ("declare war saxony", "war purpose against Saxony"),
        ("Stables in Burgundy, build them", "Burgundy"),
        ("Tighten the leash on Holland — lower its autonomy", "Holland autonomy changed"),
        ("naval landing ireland", "Name the marshal who is to embark"),
    ])
    def test_the_idiom_reaches_its_desk(self, client, line, expect):
        reply = _post(client, line)
        assert expect in reply["message"], reply["message"]
        assert "in the order of battle" not in reply["message"]

    def test_lannes_squares_is_the_square(self, client):
        reply = _post(client, "Lannes — squares.")
        assert "square" in reply["message"].lower()
        assert "instruction is unclear" not in reply["message"]

    def test_repudiate_the_peace_is_the_cabinets(self, client):
        reply = _post(client, "Repudiate the peace with Prussia")
        assert "There is no 'Repudiate'" not in reply["message"]


class TestTheGuardsStillHold:
    @pytest.mark.parametrize("line", [
        "Ney, never attack Mack", "Ney, Rhineland is lost", "Would Davout kindly go and smash Mack?",
    ])
    def test_nothing_runs(self, client, line):
        reply = _post(client, line)
        assert "MUSTER" not in reply["message"] and "moves" not in reply["message"]
