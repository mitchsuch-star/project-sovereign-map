"""DD-0 — DD0-20: THE SEVENTH BLIND SET'S REGISTER (Pre-Deploy S5, October
11, 2026; BUG_FIXES.md DD0-20; rules SYSTEMS_REFERENCE.md §105; record
PRE_DEPLOY_PLAN.md §3.0 "S5 — DD0-20").

The seventh author's 26 shrugs, two wrong desks and the parser's share of
the honest refusals, each re-typed here and driven through the real
`POST /command` on a fresh 1805 board with the trace on, exactly as the
blind census runs it. The blind file itself stays blind and is never read
here. Beside them, the controls that keep the older rules whole: FA-7's
deferral (a bare "tomorrow" is refused), CX-R1's hand list (`levy <place>`
and `probe <place>` stay unrouted), D10's one march, the take-objective,
the relay's one-order-at-a-time, and the demonym that still names its own
court when no other is named first.
"""
from __future__ import annotations

import contextlib
import io
import os
import tempfile

import pytest


@pytest.fixture(scope="module")
def client():
    os.environ["LLM_MODE"] = "mock"
    os.environ.setdefault("INK_IRON_SAVE_DIR", tempfile.mkdtemp(prefix="dd0_s5_"))
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


def _parsed(reply):
    for r in reply.get("parse_trace", []):
        if r["stage"] == "parse" and r["rule"] == "result":
            return r["detail"]
    return {}


def _rules(reply, stage):
    return [r["rule"] for r in reply.get("parse_trace", []) if r["stage"] == stage]


def _dispatched(reply):
    return _rules(reply, "dispatch")


# ═══════════════════════ THE MARCH (14 shrugs) ═══════════════════════════

class TestTheMarchRegister:
    @pytest.mark.parametrize("line, marshal, place", [
        ("Get Murat's horse moving towards Swabia, I want them in front.", "Murat", "Swabia"),
        ("I want Soult in Franche-Comte by the end of the week.", "Soult", "Franche-Comte"),
        ("Massena: Piedmont. Secure the rear.", "Massena", "Piedmont"),
        ("Bernadotte, take the road to Frankfurt and link with Davout.", "Bernadotte", "Frankfurt"),
        ("Mack is at Swabia, so I want Davout at Frankfurt to cover the northern flank.", "Davout", "Frankfurt"),
        ("Walk Ney across to Nassau, no hurry.", "Ney", "Nassau"),
        ("Davout should get himself to Swabia before Mack can slip away.", "Davout", "Swabia"),
        ("Lannes: Franche-Comte to Swabia, carry 3 days rations.", "Lannes", "Swabia"),
        ("soult->swabia", "Soult", "Swabia"),
        ("Sortez — Soult out of Lorraine and into Franche-Comte.", "Soult", "Franche-Comte"),
        ("Where Mack is, there Ney goes: Swabia.", "Ney", "Swabia"),
        ("Ney take ur boys to nassau", "Ney", "Nassau"),
        ("Lannes is ordered to Lorraine, to form the reserve.", "Lannes", "Lorraine"),
        ("Davout, Swabia, full speed — leave the baggage.", "Davout", "Swabia"),
    ])
    def test_the_line_is_the_march(self, client, line, marshal, place):
        reply = _post(client, line)
        p = _parsed(reply)
        assert p.get("action") == "move", (line, p, reply.get("message"))
        assert p.get("marshal") == marshal and p.get("target") == place, (line, p)
        assert "move" in _dispatched(reply), (line, _dispatched(reply))

    def test_the_from_to_pair_reads_the_second_place_as_the_destination(self, client):
        from backend.ai import reading as R
        s = R.slots_of("Lannes: Franche-Comte to Swabia", ["Lannes", "Ney"], ["Mack"],
                       ["Franche-Comte", "Swabia", "Lorraine"])
        assert s.sources == ["Franche-Comte"] and s.destination() == "Swabia"

    def test_the_possessive_rides_the_name(self, client):
        from backend.ai import reading as R
        s = R.slots_of("Get Murat's horse moving towards Swabia", ["Murat"], ["Mack"], ["Swabia"])
        assert s.friends == ["Murat"] and "murat's" not in s.residue and "moving" in s.residue
        assert R.march_by_slots(s)

    def test_a_bare_tomorrow_is_still_the_deferral(self, client):
        reply = _post(client, "Ney, attack Mack tomorrow.")
        assert not reply.get("success") and "tomorrow" in reply["message"]
        assert "attack" not in _dispatched(reply)

    def test_the_hour_is_colour_but_the_contingency_stays_refused(self, client):
        reply = _post(client, "Ney, attack Mack at dawn.")
        assert _parsed(reply).get("action") == "attack" and _parsed(reply).get("target") == "Mack"
        reply = _post(client, "Davout, hold Rhineland if Mack attacks.")
        assert not reply.get("success") and "contingency" in reply["message"]

    def test_the_bare_levy_stays_unrouted(self, client):
        reply = _post(client, "levy Guyenne")
        assert "recruit" not in _dispatched(reply) and "which marshal" in reply["message"].lower()

    def test_break_camp_and_march_is_still_one_march(self, client):
        reply = _post(client, "Soult, break camp and march to Bohemia.")
        p = _parsed(reply)
        assert p.get("action") == "move" and p.get("target") == "Bohemia" and "attack" not in _dispatched(reply)

    def test_the_take_objective_is_still_the_capture(self, client):
        reply = _post(client, "Ney, take Swabia")
        assert _parsed(reply).get("action") == "attack"


# ═══════════════════════ THE ATTACK (6 shrugs) ═══════════════════════════

class TestTheAttackRegister:
    @pytest.mark.parametrize("line, marshal, target", [
        ("Everybody on Mack. Soult leads.", "Soult", "Mack"),
        ("Ney, break Mack.", "Ney", "Mack"),
        ("Lannes must attack Swabia tomorrow at dawn, no matter the weather.", "Lannes", "Swabia"),
        ("Bernadotte, assail Archduke John.", "Bernadotte", "ArchdukeJohn"),
        ("Soult goes in against Swabia; Davout and Ney will join.", "Soult", "Swabia"),
    ])
    def test_the_line_is_the_attack(self, client, line, marshal, target):
        reply = _post(client, line)
        p = _parsed(reply)
        assert p.get("action") == "attack" and p.get("marshal") == marshal, (line, p, reply.get("message"))
        assert p.get("target") == target, (line, p)

    def test_the_archduke_in_sight_is_john(self, client):
        reply = _post(client, "Massena fall on the Archduke")
        assert _parsed(reply).get("action") == "attack" and "Archduke John" in reply["message"]

    def test_the_title_alone_names_the_one_foe_that_bears_it(self):
        from backend.ai import reading as R
        assert "Archduke" in R.foe_forms(["ArchdukeJohn", "Mack"])
        assert "Archduke" not in R.foe_forms(["ArchdukeJohn", "ArchdukeCharles", "Mack"])

    def test_everybody_on_the_foe_alone_is_the_muster(self, client):
        reply = _post(client, "Everybody on Mack.")
        assert _parsed(reply).get("action") == "attack" and "MUSTER" in reply["message"]

    def test_one_man_who_will_join_rides_the_relay(self, client):
        reply = _post(client, "Soult goes in against Swabia; Davout will join.")
        p = _parsed(reply)
        assert p.get("action") == "attack" and p.get("target") == "Swabia"
        assert p.get("dropped_sequel") == "Davout, support Soult"

    def test_break_camp_is_not_a_break_of_a_foe(self, client):
        reply = _post(client, "Ney, break camp.")
        assert "attack" not in _dispatched(reply) and "unfortify" in _dispatched(reply)

    def test_the_foes_line_of_retreat_is_not_his_position(self, client):
        """The hook's catch (CRT-6's pin): the possessive strip reads the
        ground he holds, never "Mack's line of retreat"."""
        reply = _post(client, "Lannes, cut off Mack's line of retreat")
        assert "retreat" not in _dispatched(reply)
        assert "retreats" not in reply["message"]


# ═══════════════════════ THE DESKS (5 shrugs) ════════════════════════════

class TestTheCabinetsOwnLinesStayWhole:
    def test_have_talleyrand_back_a_quarrel_is_the_sponsorship_idioms(self, client):
        """The hook's catch: "Have Talleyrand back Prussia's quarrel with
        Austria" is the sponsorship idiom's own line (its aim is Austria, and
        the verb refuses it — Prussia's design is aimed at Hanover); the
        delegation rewrite reads the office, never the man."""
        reply = _post(client, "Have Talleyrand back Prussia's quarrel with Austria")
        assert reply.get("success") is False and "aimed at Hanover" in reply["message"]


# ═══════════════════════ THE DESKS (5 shrugs) ════════════════════════════

class TestTheDesks:
    def test_talk_to_a_court_is_the_negotiation(self, client):
        reply = _post(client, "Talk to Spain about their fleet joining ours.")
        p = _parsed(reply)
        assert p.get("target") == "Spain" and p.get("type") == "diplomatic"
        assert "order of battle" not in reply["message"]

    def test_have_the_cabinet_propose_a_treaty_of_alliance(self, client):
        reply = _post(client, "Have the Cabinet propose a treaty of alliance to Denmark.")
        p = _parsed(reply)
        assert p.get("action") == "diplomatic_proposal" and p.get("target") == "Denmark"
        assert "diplomatic_proposal" in _dispatched(reply)

    def test_is_to_retire_is_the_retreat(self, client):
        reply = _post(client, "Davout is to retire and save the corps.")
        assert _parsed(reply).get("action") == "retreat" and "retreat" in _dispatched(reply)

    def test_run_to_ground_is_the_pursuit(self, client):
        reply = _post(client, "Soult, run Mack to ground.")
        assert "pursues Mack" in reply["message"]

    def test_draft_and_enact_is_the_enacting(self, client):
        reply = _post(client, "Berthier, draft and enact the Staff reform.")
        p = _parsed(reply)
        assert p.get("action") == "enact_law" and p.get("target") == "Staff"


# ═══════════════════════ THE TWO WRONG DESKS ═════════════════════════════

class TestTheWrongDesks:
    def test_assault_the_foes_position_with_a_second_in_support(self, client):
        reply = _post(client, "Soult: assault Mack's position, Ney in support.")
        p = _parsed(reply)
        assert p.get("action") == "attack" and p.get("marshal") == "Soult" and p.get("target") == "Mack"
        assert "peel_support_suffix" in _rules(reply, "reading")
        assert "support Bernadotte" not in reply["message"]

    def test_gold_sent_to_a_courts_treasury_is_the_investment(self, client):
        reply = _post(client, "Send 50 gold to the Kingdom of Italy's treasury.")
        p = _parsed(reply)
        assert p.get("action") == "invest_vassal" and p.get("target") == "KingdomOfItaly"
        assert "TREASURY REPORT" not in reply["message"]


# ═══════════════ THE HONEST REFUSALS' PARSER SHARE (15) ══════════════════

class TestTheParsersShareOfTheRefusals:
    def test_the_guard_and_i_is_the_emperors_corps(self, client):
        reply = _post(client, "the Guard and I ride for Franche-Comte")
        p = _parsed(reply)
        assert p.get("action") == "move" and p.get("marshal") == "Napoleon" and p.get("target") == "Franche-Comte"

    def test_the_aim_before_the_dash_yields_to_the_addressed_order(self, client):
        reply = _post(client, "Hit John before he can join Mack — Massena, attack Tyrol.")
        p = _parsed(reply)
        assert p.get("action") == "attack" and p.get("marshal") == "Massena" and p.get("target") == "Tyrol"
        assert "Cannot find" not in reply["message"]

    def test_no_letter_asks_a_court_for_its_men(self, client):
        reply = _post(client, "talleyrand ask bavaria for more troops")
        assert not reply.get("success")
        assert "no letter asks for men" in reply["message"]
        assert "Shall I have Talleyrand court Bavaria" in reply["message"]
        assert not _dispatched(reply)

    def test_a_mission_with_its_aim_behind_the_dash(self, client):
        reply = _post(client, "A mission to Saxony — keep the Elector out of this war.")
        p = _parsed(reply)
        assert p.get("action") == "diplomatic_mission" and p.get("target") == "Saxony"

    @pytest.mark.parametrize("line, court", [
        ("Talleyrand will sound out Denmark on closing the Sound to the British.", "Denmark"),
        ("Talleyrand, see what Portugal wants to leave the British orbit.", "Portugal"),
    ])
    def test_the_court_named_first_outranks_the_demonym(self, client, line, court):
        reply = _post(client, line)
        p = _parsed(reply)
        assert p.get("target") == court and p.get("action") == "diplomatic_advisory", (line, p)
        assert court in reply["message"]

    def test_a_demonym_alone_still_names_its_court(self, client):
        reply = _post(client, "Talleyrand, propose peace to the British.")
        assert _parsed(reply).get("target") == "Britain"

    def test_the_uk_is_not_inside_the_duke(self):
        from backend.game_logic.diplomatic_dialogue import extract_nation_from_command
        assert extract_nation_from_command("sound out Denmark on closing the Sound to the British") == "Denmark"
        assert extract_nation_from_command("see what Portugal wants to leave the British orbit") == "Portugal"
        assert extract_nation_from_command("propose peace to the British") == "Britain"
        assert extract_nation_from_command("ask the Archduke's court, Austria, for terms") == "Austria"

    @pytest.mark.parametrize("line, place", [
        ("The Emperor commands a levy in Guyenne.", "Guyenne"),
        ("More men at Lyonnais — infantry, as many as the treasury allows.", "Lyonnais"),
        ("I want a levy in Languedoc, infantry.", "Languedoc"),
        ("Call up men in Flanders.", "Flanders"),
    ])
    def test_the_levys_register_is_the_recruit(self, client, line, place):
        reply = _post(client, line)
        p = _parsed(reply)
        assert p.get("action") == "recruit" and p.get("target") == place, (line, p, reply.get("message"))
        assert "recruit" in _dispatched(reply)
        assert "There is no '" not in reply["message"]     # the typed head is no addressee

    def test_a_depot_asked_of_berthier_is_built(self, client):
        reply = _post(client, "Berthier, a supply depot in Rhineland.")
        p = _parsed(reply)
        assert p.get("action") == "build" and p.get("target") == "Rhineland"
        assert "Construction started" in reply["message"]

    def test_mending_the_walls_is_the_repair(self, client):
        reply = _post(client, "mend the walls at rhineland")
        p = _parsed(reply)
        assert p.get("action") == "repair" and p.get("target") == "Rhineland"
        assert "repair" in _dispatched(reply)

    def test_the_bare_probe_stays_the_hand_lists(self, client):
        reply = _post(client, "Massena, probe Piedmont for any Austrian movement.")
        assert not reply.get("success") and "scout" not in _dispatched(reply)
