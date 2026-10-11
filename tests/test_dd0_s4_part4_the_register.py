"""DD-0 S4 part 4 "The Command Road" — DD0-18: THE ONE REAL EXECUTION, THE
WAR ON OUR OWN VASSAL, THE FIFTH SET'S REGISTER (October 11, 2026;
PRE_DEPLOY_PLAN.md §3.0 "S4 landing record, part 4"; rules
SYSTEMS_REFERENCE.md §104 part 4; row BUG_FIXES.md §DD-0 S4 DD0-18).

Each line is driven through the real `POST /command` on a fresh 1805 board
with the trace on, exactly as the blind census runs it. The fifth blind file
itself stays blind and is never read here — these are the register's shapes,
each re-typed, with the controls that keep the older rules whole (D10's one
march, the metamorphic corpus's SUPPORT, PARSE-NEG's refusals, the WAIT
family's "stay put", IQ-9's gate, CX-R1's hand list).
"""
from __future__ import annotations

import contextlib
import io
import os
import tempfile

import pytest

FRIENDS = ["Ney", "Davout", "Soult", "Lannes", "Murat", "Massena", "Bernadotte", "Napoleon"]
FOES = ["Mack", "ArchdukeJohn", "ArchdukeCharles", "Kutuzov"]
PLACES = ["Rhineland", "Swabia", "Lorraine", "Frankfurt", "Munich", "Milan", "Tyrol", "Brabant",
          "Franche-Comte", "Nivernais", "Bern", "Nassau", "Bohemia"]


@pytest.fixture(scope="module")
def client():
    os.environ["LLM_MODE"] = "mock"
    os.environ.setdefault("INK_IRON_SAVE_DIR", tempfile.mkdtemp(prefix="dd0_s4p4_"))
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
    for r in reply.get("parse_trace", []):
        if r["stage"] == "parse" and r["rule"] == "result":
            return r["detail"]
    return {}


def _dispatched(reply):
    return [r["rule"] for r in reply.get("parse_trace", []) if r["stage"] == "dispatch"]


# ═══════════════ (a) THE ONE REAL EXECUTION — the order of the chain ═══════

class TestA_TheCampStruckIsNoBattle:
    def test_strike_camp_abandon_the_works_does_not_fight(self, client):
        reply = _post(client, "Ney, strike camp, abandon the works.")
        assert "MUSTER" not in reply["message"] and "engaged" not in reply["message"]
        assert "unfortify" in _dispatched(reply)
        assert "not currently fortified" in reply["message"]     # the board's own refusal

    def test_strike_camp_alone_is_the_unfortify(self, client):
        reply = _post(client, "Ney, strike camp.")
        assert "unfortify" in _dispatched(reply) and "MUSTER" not in reply["message"]

    def test_a_named_foe_keeps_the_battle(self, client):
        reply = _post(client, "Ney, strike Mack.")
        assert "attack" in _dispatched(reply) and "MUSTER" in reply["message"]

    def test_break_camp_and_march_is_one_march(self, client):
        """D10's pin, kept: the camp struck before a march IS the march."""
        reply = _post(client, "Lannes, break camp and march to Bohemia")
        assert _parsed(reply).get("action") == "move" and _parsed(reply).get("target") == "Bohemia"
        reply = _post(client, "Ney, strike camp and march to Lorraine")
        assert "unfortify" not in _dispatched(reply) and "Lorraine" in reply["message"]
        assert "march to Lorraine" in reply["message"] or "moves to Lorraine" in reply["message"].lower()

    def test_the_idiom_names_the_order(self):
        from backend.ai import dd0_rewrites as D
        assert D.unfortify_idiom("strike camp")
        assert D.unfortify_idiom("ney, strike camp, abandon the works.")
        assert not D.unfortify_idiom("strike camp and march to bohemia")
        assert not D.unfortify_idiom("strike mack")


# ═══════════════ (b) THE WAR ON OUR OWN VASSAL ══════════════════════════════

class TestB_TheCabinetRefusesAWarOnASatellite:
    @pytest.mark.parametrize("line,court", [
        ("Declare war on Holland.", "Holland"),
        ("Talleyrand, declare war on the Kingdom of Italy.", "Kingdom of Italy"),
        ("declare war switzerland", "Switzerland"),
    ])
    def test_refused_in_words_before_the_chooser(self, client, line, court):
        reply = _post(client, line)
        assert reply["success"] is False
        assert "own vassal" in reply["message"] and court in reply["message"]
        assert "Choose your war purpose" not in reply["message"]
        assert not reply.get("war_purpose_popup")

    def test_a_foreign_court_still_reaches_the_chooser(self, client):
        reply = _post(client, "Declare war on Prussia.")
        assert "Choose your war purpose against Prussia" in reply["message"]

    def test_the_gate_is_the_players_backstop_and_leaves_the_ai_alone(self, client):
        c, M = client
        world = _fresh(M)
        from backend.game_logic.diplomacy import declare_war, own_vassal_refusal
        res = declare_war(world, "France", "Holland")
        assert res["success"] is False and "own vassal" in res["message"]
        assert world.get_diplomatic_state("France", "Holland") != "WAR"
        # an AI lord's road is untouched by this gate (no AI declares on its own vassal today)
        assert own_vassal_refusal(world, "Austria", "Holland") is None
        assert own_vassal_refusal(world, "France", "Prussia") is None


# ═══════════════ (c) THE REGISTER ═══════════════════════════════════════════

class TestC_TheMarchRegister:
    @pytest.mark.parametrize("line,expect", [
        ("Lannes, get yourself to Swabia.", "enemy forces present"),            # the board's own refusal
        ("Marshal Ney, kindly take your corps down to Nassau.", "Cannot enter Nassau"),
        ("Soult, bring the corps up to Rhineland alongside Davout.", "Soult moves from Lorraine to Rhineland"),
        ("Murat rides to Nivernais.", "Murat moves from Franche-Comte to Nivernais"),
        ("Shift Murat's horse to Lorraine so he can screen the Emperor.", "Murat moves from Franche-Comte to Lorraine"),
        ("Davout, I want you in Brabant covering the Dutch coast.", "Davout moves from Rhineland to Brabant"),
        ("Bernadotte, shift your corps to Bohemia, and keep an eye out for Charles on the way.", "Bernadotte moves from Franconia to Bohemia"),
        ("Get Murat's horse down to Bern, I want the Swiss road covered.", "Murat moves from Franche-Comte to Bern"),
        ("Order Davout into Brabant; the Dutch coast wants watching.", "Davout moves from Rhineland to Brabant"),
    ])
    def test_the_march_is_read(self, client, line, expect):
        reply = _post(client, line)
        assert expect in reply["message"], reply["message"][:200]

    def test_on_to_the_place_and_the_enemy_is_the_attack(self, client):
        reply = _post(client, "Ney, on to Swabia and the enemy.")
        assert "attack" in _dispatched(reply) and "Mack" in reply["message"]

    def test_the_watch_precaution_never_eats_a_bare_scout(self, client):
        reply = _post(client, "Murat, keep an eye on Berlin.")
        assert "scout" in _dispatched(reply) or "scout" in reply["message"].lower()

    def test_the_inflected_verbs(self):
        from backend.commands import parser as P
        for word in ("ride", "dig", "stand", "form", "retire", "gallop", "stay", "take", "fall", "engage", "shift"):
            assert word in P._INFLECTED_ORDER_VERBS


class TestC_TheRetreatRegister:
    def test_retire_on_a_place_is_the_march(self, client):
        """`retire on <place>` is restated to `retire to <place>` — the
        plain-speech road's own form, which is the strategic MOVE_TO (FA
        slice 7's pin), never a tactical `move to`."""
        reply = _post(client, "Soult, retire on Franche-Comte.")
        assert "rewrite_retire_on" in _rules(reply, "parser")
        assert "Franche-Comte" in reply["message"]
        assert "march" in reply["message"].lower() or "moves" in reply["message"].lower()
        assert "retreats" not in reply["message"] and "-45%" not in reply["message"]

    def test_pull_back_with_no_destination_is_the_retreat(self, client):
        reply = _post(client, "Pull Ney back behind the Rhine.")
        assert "rewrite_pull_back" in _rules(reply, "parser")
        # the retreat went out, or Ney objected to it (the objection dice) — never a shrug
        assert "retreat" in _dispatched(reply) or "retreat" in reply["message"].lower()
        assert "cannot" not in reply["message"].lower() or "retreat" in reply["message"].lower()

    def test_break_off_and_rejoin_reads_the_man_as_the_man(self, client):
        reply = _post(client, "Lannes, break off, rejoin Soult at Lorraine.")
        assert "Lannes moves from Franche-Comte to Lorraine" in reply["message"]
        assert "Region 'Soult'" not in reply["message"]

    def test_join_at_stays_the_support_it_was(self, client):
        """The metamorphic corpus's own row: "join Davout at Lorraine" is a
        SUPPORT of Davout, never a march to Lorraine."""
        reply = _post(client, "Ney, join Davout at Lorraine")
        assert "Ney moves from Rhineland to Lorraine" not in reply["message"]
        assert _parsed(reply).get("strategic_type") == "SUPPORT" or "guns" in reply["message"]


class TestC_TheDesks:
    @pytest.mark.parametrize("line,expect", [
        ("Massena digs in at Milan.", "fortify"),
        ("Davout stands fast at Rhineland.", "hold"),
        ("Lannes forms square against the Austrian horse.", "form_square"),
        ("Lannes, probe toward Bern and report.", "scout"),
        ("Murat, screen toward Tyrol.", "scout"),
        ("Fort at Milan, Massena will need it.", "build"),
        ("Make Suchet a marshal.", "recruit_marshal"),
        ("oudinot to marshal", "recruit_marshal"),
        ("the staff law - enact", "enact_law"),
        ("Hand Flanders over to Holland.", "grant_region_to_vassal"),
    ])
    def test_the_desk_is_reached(self, client, line, expect):
        reply = _post(client, line)
        assert _parsed(reply).get("action") == expect or expect in _dispatched(reply), (
            _parsed(reply), _dispatched(reply), reply["message"][:160])

    @pytest.mark.parametrize("line", [
        "An estate for Marshal Soult, with the Emperor's thanks.",
        "Bernadotte, an estate, grudgingly.",
        "Estate for Ney.",
        "title davout",
    ])
    def test_the_reward_desk_opens(self, client, line):
        reply = _post(client, line)
        assert "rewrite_reward_idiom" in _rules(reply, "parser")
        assert "Reward dialog" in reply["message"]

    def test_a_bare_probe_still_routes_nowhere(self, client):
        """CX-R1's hand-list pin: "probe Swabia" is not an order."""
        c, M = client
        _fresh(M)
        assert M.parser.llm.fast_parse("probe Swabia").action == "unknown"

    @pytest.mark.parametrize("line", [
        "That is all for today, Berthier. Close the turn.",
        "Done. Advance the clock.",
    ])
    def test_the_end_turn_in_other_words_is_the_desks_ask(self, client, line):
        reply = _post(client, line)
        assert "Shall I close the day" in reply["message"]
        assert "Turn 1 ended" not in reply["message"] and "Turn 2" not in reply["message"]


class TestC_TheStatementBeforeTheOrder:
    def test_the_dash_statement_names_the_foe(self, client):
        reply = _post(client, "Massena, John sits at Tyrol — go and get him.")
        assert "peel_foe_statement" in _rules(reply, "reading")
        assert "MUSTER — Massena" in reply["message"] and "Archduke John" in reply["message"]

    def test_the_sentence_statement_and_see_to_it(self, client):
        reply = _post(client, "Mack must be destroyed. Davout, see to it.")
        # the leading sentence is rhetoric to `peel_rhetoric` (it runs first)
        # or a foe statement to `peel_foe_statement`; either hints the foe
        assert {"peel_foe_statement", "peel_rhetoric"} & set(_rules(reply, "reading"))
        assert "rewrite_at_him" in _rules(reply, "reading")
        assert _parsed(reply).get("action") == "attack"
        assert "Mack" in str(_parsed(reply).get("target")) or "Mack" in reply["message"]

    def test_the_reading_is_pure(self):
        from backend.ai import reading as R
        r = R.read("Massena, John sits at Tyrol — go and get him.", FRIENDS, FOES, PLACES)
        assert r.address == "Massena" and r.hint_foe == "ArchdukeJohn"
        assert r.core().lower().startswith("attack")
        r = R.read("Davout, I want you in Brabant covering the Dutch coast.", FRIENDS, FOES, PLACES)
        assert "covering" not in r.text()
        r = R.read("Shift Murat's horse to Lorraine so he can screen the Emperor.", FRIENDS, FOES, PLACES)
        assert "screen" not in r.text()
        # a known name inside the purpose keeps it
        r = R.read("Ney, move to Lorraine so he can support Davout.", FRIENDS, FOES, PLACES)
        assert "Davout" in r.text()


# ═══════════════ (d) THE CABINET'S BARE DESK ════════════════════════════════

class TestD_TheCabinetsBareDesk:
    @pytest.mark.parametrize("line,court", [
        ("Send a mission to Saxony.", "Saxony"),
        ("Talleyrand, send a mission to Prussia.", "Prussia"),
        ("Mission to the Porte — Talleyrand, court the Ottomans.", "Ottoman"),
        ("mission to hesse", "Hesse"),
    ])
    def test_a_mission_with_no_purpose_warms_the_court(self, client, line, court):
        reply = _post(client, line)
        assert "await your instructions" not in reply["message"]
        assert "improve relations with" in reply["message"] and court in reply["message"]

    def test_a_mission_to_a_belligerents_capital_is_the_boards_refusal(self, client):
        reply = _post(client, "Mission to Vienna.")
        assert "we do not court a belligerent" in reply["message"] and "Austria" in reply["message"]

    def test_the_declaration_is_never_a_mission(self, client):
        reply = _post(client, "War with Portugal. Inform their ambassador.")
        assert _parsed(reply).get("action") == "diplomatic_declare_war"

    def test_the_court_by_its_seat(self):
        from backend.game_logic.diplomatic_dialogue import extract_nation_from_command
        assert extract_nation_from_command("Mission to Vienna.") == "Austria"
        assert extract_nation_from_command("Send a mission to Berlin to keep the Prussians neutral.") == "Prussia"
        assert extract_nation_from_command("Mission to the Porte") == "Ottoman"
        assert extract_nation_from_command("Ney, march to Swabia") is None

    def test_open_talks_at_war_is_the_cabinets_card_and_the_judge_reads_it_as_asked(self, client):
        import importlib.util
        from pathlib import Path
        reply = _post(client, "Talleyrand: open talks with Russia.")
        assert "is at a standstill" in reply["message"]
        assert reply.get("diplomatic_dialogue") or reply.get("awaiting_diplomatic_response")
        spec = importlib.util.spec_from_file_location(
            "census_p4", Path(__file__).resolve().parents[1] / "tools" / "unrehearsed_census.py")
        census = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(census)
        assert census.classify_order({"action": "diplomacy", "marshal": "state"}, reply) == "asked"
        # the two PEACE-state cards were withheld from the judge (they move committed classes)
        import _score_probes as judge
        assert not judge.ASKED_RX.search("Sire, relations with Saxony are tense.")
        assert not judge.ASKED_RX.search("Sire, Naples views us favorably.")


# ═══════════════ (e) THE NEGATION THAT IS A HOLD ════════════════════════════

class TestE_DontMoveIsTheHold:
    def test_lannes_dont_move_holds(self, client):
        reply = _post(client, "lannes dont move")
        assert "rewrite_negated_hold" in _rules(reply, "parser")
        assert "Lannes will hold" in reply["message"]

    @pytest.mark.parametrize("line", [
        "Ney, don't move to Lorraine.",       # a destination: PARSE-NEG's refusal
        "Ney, do not attack Mack.",            # another verb: PARSE-NEG's refusal
        "Davout, never march on Swabia",
    ])
    def test_a_negated_order_with_an_object_is_still_refused(self, client, line):
        reply = _post(client, line)
        assert "no order goes out" in reply["message"] or "relayed nothing" in reply["message"]
        assert "will hold" not in reply["message"]

    def test_stay_put_stays_the_wait_familys(self, client):
        reply = _post(client, "the guard stays put")
        assert "rewrite_negated_hold" not in _rules(reply, "parser")
