"""DD-0 S3b — THE INSTRUMENT'S FINDINGS FIXED (October 10, 2026; rows
BUG_FIXES.md §DD-0 S3, DD0-1 … DD0-10; rules SYSTEMS_REFERENCE.md §103).

Every row of the third blind set the instrument read as the parser's, and
the metamorphic ledger's largest classes, driven through the real
`POST /command` on a fresh 1805 board with the trace on, so each pin reads
the stage that used to go wrong:

  DD0-1  an attack on our own marshal / on "everything" refuses or asks
  DD0-2  "go to X and wait there" marches; "go to Berlin — no wait, Dresden" corrects
  DD0-3  "ride to Lannes' aid" supports Lannes
  DD0-4  "drop off a few battalions to hold Franconia" is a garrison
  DD0-5  "what's in Tyrol? Massena, find out" answers AND relays the order
  DD0-6  "War with Portugal." declares
  DD0-7  "attack Mack and also do not attack Mack" is refused as a contradiction
  DD0-8  the ONE judge reads the ten honest shapes
  DD0-9  the chatty register (the telegraph, the idioms, the rewards, the courts)
  DD0-10 the dash aside, the reason tail, the second man in support
"""
from __future__ import annotations

import contextlib
import io
import os
import tempfile

import pytest

from backend.ai import parser_metamorphic as pm


@pytest.fixture(scope="module")
def client():
    os.environ["LLM_MODE"] = "mock"
    os.environ.setdefault("INK_IRON_SAVE_DIR", tempfile.mkdtemp(prefix="dd0_s3b_"))
    from fastapi.testclient import TestClient
    with contextlib.redirect_stdout(io.StringIO()):
        import backend.main as M
        c = TestClient(M.app)
    originals = (M.game_state["world"], M.world, M.parser)
    try:
        yield c, M
    finally:
        M.game_state["world"], M.world, M.parser = originals


def _fresh(M):
    from backend.ai import parser_eval as pe
    from backend.commands.parser import CommandParser
    with contextlib.redirect_stdout(io.StringIO()):
        world = pe.build_world("1805")
        M.game_state["world"] = world
        M.world = world
        M.parser = CommandParser(use_real_llm=False)
    return world


def _post(client, line):
    c, M = client
    _fresh(M)
    with contextlib.redirect_stdout(io.StringIO()):
        r = c.post("/command", json={"command": line, "trace": True})
    return r.json()


def _rules(reply, stage):
    return [r["rule"] for r in reply.get("parse_trace", []) if r["stage"] == stage]


def _parsed(reply):
    """The `parse · result` row's detail — the reading before the board."""
    for r in reply.get("parse_trace", []):
        if r["stage"] == "parse" and r["rule"] == "result":
            return r["detail"]
    return {}


class TestDD0_1TheOwnMarshalAndEverything:
    def test_attack_own_marshal_refuses_by_name(self, client):
        reply = _post(client, "Ney, attack Davout")
        assert reply["success"] is False
        assert "Davout is a marshal of France" in reply["message"]
        assert "will not attack our own" in reply["message"]
        assert "MUSTER" not in reply["message"]

    def test_attack_everything_asks(self, client):
        reply = _post(client, "Ney, Davout, Soult, everyone — attack everything")
        assert "Attack whom" in reply["message"]
        assert "MUSTER" not in reply["message"]


class TestDD0_2TheWaitAndTheCorrection:
    def test_go_and_wait_there_marches(self, client):
        reply = _post(client, "Davout, go to Gelderland and wait there")
        assert "rewrite_arrival_wait" in _rules(reply, "parser")
        parsed = _parsed(reply)
        assert parsed.get("action") == "move" and parsed.get("target") == "Gelderland", parsed
        assert "holds position" not in reply["message"]

    def test_no_wait_takes_the_second_place(self, client):
        reply = _post(client, "Bernadotte, go to Berlin — no wait, Dresden")
        assert "rewrite_self_correction" in _rules(reply, "parser")
        parsed = _parsed(reply)
        assert parsed.get("action") == "move" and parsed.get("target") == "Dresden", parsed


class TestDD0_3ThePossessiveAid:
    def test_ride_to_lannes_aid_supports_lannes(self, client):
        """Read off the trace, not the reply: Murat may OBJECT to the order
        (the mood dice), and an objection is still the RIGHT order on the
        desk — 'support Lannes', never Bernadotte."""
        reply = _post(client, "Murat, ride to Lannes' aid")
        parsed = _parsed(reply)
        assert parsed.get("strategic_type") == "SUPPORT" and parsed.get("target") == "Lannes", parsed
        assert "Bernadotte" not in reply["message"]


class TestDD0_4TheGarrisonIdiom:
    def test_drop_off_battalions_is_a_garrison(self, client):
        reply = _post(client, "Bernadotte, drop off a few battalions to hold Franconia")
        assert "garrison" in _rules(reply, "dispatch")
        assert "strategic_order" not in _rules(reply, "dispatch")


class TestDD0_5TheQuestionAndTheOrder:
    def test_the_question_is_answered_and_the_order_relayed(self, client):
        reply = _post(client, "what's in Tyrol? Massena, find out")
        assert "split_question_and_order" in _rules(reply, "parser")
        assert "Tyrol" in reply["message"]
        assert reply.get("dropped_sequel") == "Massena, find out"


class TestDD0_6TheDeclarationAsAFact:
    def test_war_with_portugal_declares(self, client):
        reply = _post(client, "War with Portugal. Inform their ambassador.")
        assert "diplomatic_declare_war" in _rules(reply, "dispatch")
        assert "war purpose" in reply["message"].lower()


class TestDD0_7TheContradiction:
    def test_attack_and_do_not_attack_is_refused(self, client):
        reply = _post(client, "Ney, attack Mack and also do not attack Mack")
        assert reply["success"] is False
        assert "forbids it in the same breath" in reply["message"]
        assert "MUSTER" not in reply["message"]
        refusals = [r for r in reply["parse_trace"] if r["rule"] == "refusal"]
        assert refusals and refusals[0]["detail"]["kind"] == "contradiction"

    def test_a_plain_negation_is_still_a_negation(self, client):
        reply = _post(client, "Ney, hold your position, do not attack")
        assert "forbids it in the same breath" not in reply["message"]


class TestDD0_8TheJudge:
    def test_the_ten_shapes(self):
        import importlib.util
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location("probes_dd0", root / "tools" / "_score_probes.py")
        j = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(j)
        for s in ("Bernadotte challenges the order", "shall we engage him?", "whom shall Murat engage?",
                  "which nation should I direct", "Attack whom, Sire?", "Which is it to be?"):
            assert j.ASKED_RX.search(s), s
        for s in ("Charge requires a marshal", "I need a marshal and an action"):
            assert j.REFUSED_RX.search(s), s
        for s in ("The Admiralty takes its orders from the Emperor", "Cannot vassalize France",
                  "We do not control Vienna", "Soult is not cavalry", "Ney will not attack our own"):
            assert j.BOARD_GATE_RX.search(s), s
        import re
        assert re.search(j.ACTION_WORDS["diplomacy"], "I shall begin efforts to conduct diplomacy with Denmark", re.I)
        assert re.search(j.ACTION_WORDS["retreat"], "Murat moves from Franche-Comte to Lorraine", re.I)


class TestDD0_9TheChattyRegister:
    @pytest.mark.parametrize("line,rule,action,target", [
        ("Marshal Ney moves to Lorraine", "rewrite_inflected_order", "move", "Lorraine"),
        ("Marshal Soult will relocate his corps to Nivernais.", "read_address", "move", "Nivernais"),
        ("send Soult to Orleanais", "rewrite_send_marshal", "move", "Orleanais"),
        ("Pull Bernadotte back to Frankfurt", "rewrite_send_marshal", "move", "Frankfurt"),
        ("Marshal Ney: Brabant.", "rewrite_telegraphic_march", "move", "Brabant"),
        ("Murat — Swabia. Go.", "rewrite_telegraphic_march", "move", "Swabia"),
        ("ney frankfurt", "rewrite_telegraphic_march", "move", "Frankfurt"),
        ("ney go kill mack", "rewrite_kill", "attack", "Mack"),
        ("Davout — Mack — go.", "rewrite_attack_idioms", "attack", "Mack"),
        ("Go on Davout, drive Mack out", "rewrite_attack_idioms", "attack", "Mack"),
        ("Give Ney an estate", "rewrite_reward_idiom", "status", None),
        ("invest 100 gold in switzerland", "rewrite_invest_gold", "invest_vassal", "Switzerland"),
        ("That's all for now, Berthier — next turn.", "rewrite_trailing_end_turn", "end_turn", None),
    ])
    def test_the_rewrites_fire_and_read(self, client, line, rule, action, target):
        reply = _post(client, line)
        # DD-0 S4: the modal address is the Reading's own stage now.
        assert rule in _rules(reply, "parser") + _rules(reply, "reading"), reply["parse_trace"]
        parsed = _parsed(reply)
        assert parsed.get("action") == action, parsed
        if target:
            assert parsed.get("target") == target, parsed

    @pytest.mark.parametrize("line,action", [
        ("Ney, I need eyes on Nassau", "scout"),
        ("Massena, throw up earthworks around Milan", "fortify"),
        ("Lannes, have the men practise their musketry", "drill"),
        ("Soult, squares — Austrian cavalry coming", "form_square"),
        ("the navy should sortie", "set_fleet_posture"),
        ("Davout, bring the corps back to Lorraine", "move"),
        ("Bernadotte, get to Munich.", "move"),
        ("please, cancel", "cancel"),
        ("Land 10,000 men in Ireland", "naval_expedition"),
        ("davout suport ney", "move"),
    ])
    def test_the_idioms_are_read(self, client, line, action):
        reply = _post(client, line)
        assert _parsed(reply).get("action") == action, reply["parse_trace"]

    def test_send_to_scout_is_a_scout(self, client):
        reply = _post(client, "Send Murat to scout Munich")
        assert "rewrite_send_marshal" not in _rules(reply, "parser")
        assert _parsed(reply).get("action") == "scout"

    def test_grant_a_rente_stays_the_endow_verb(self, client):
        reply = _post(client, "grant Ney a rente")
        assert "rewrite_reward_idiom" not in _rules(reply, "parser")


class TestDD0_10TheLedgersClasses:
    def test_the_dash_aside_is_not_the_province(self, client):
        reply = _post(client, "Ney, advance on Swabia — thank you")
        # DD-0 S4: the aside is peeled as a SPAN by the Reading (§104).
        rules = _rules(reply, "parser") + _rules(reply, "reading")
        assert ("strip_dash_aside" in rules or "strip_please_and_urgency" in rules
                or "peel_please_and_dash_aside" in rules)
        assert "Thank You" not in reply["message"]
        assert _parsed(reply).get("target") == "Swabia"
        reply = _post(client, "Soult, dig in — the Austrians are close")
        assert ("strip_dash_aside" in _rules(reply, "parser")
                or "peel_please_and_dash_aside" in _rules(reply, "reading"))
        assert _parsed(reply).get("action") == "fortify"

    def test_a_dash_before_a_place_is_kept(self, client):
        reply = _post(client, "Murat — Swabia. Go.")
        assert "strip_dash_aside" not in _rules(reply, "parser")

    def test_the_because_tail_is_cut(self, client):
        reply = _post(client, "Ney, hold position because the men are ready")
        assert ("strip_because_tail" in _rules(reply, "parser")
                or "peel_reason_tail" in _rules(reply, "reading"))
        assert "Because" not in reply["message"]

    def test_the_second_in_support_keeps_the_attack(self, client):
        reply = _post(client, "Soult, attack Mack with Lannes in support")
        assert ("rewrite_second_in_support" in _rules(reply, "parser")
                or "peel_support_suffix" in _rules(reply, "reading"))
        assert "MUSTER" in reply["message"]
        assert reply.get("dropped_sequel") == "Lannes, support Soult"

    def test_the_metamorphic_ledger_fell(self):
        """The ratchet's own count (`LEDGER_CAP`) is in the harness; here the
        families the fixes addressed read under their first-reading counts."""
        from backend.ai import parser_eval
        rows = parser_eval.load_corpus()["entries"]
        outcomes = pm.run(rows, families=["dash_aside", "reason_tail", "second_name_role"])
        failed = pm.summarize(outcomes)["by_family"]
        assert failed["dash_aside"]["failed"] < 70
        assert failed["reason_tail"]["failed"] < 18
        assert failed["second_name_role"]["failed"] < 31
