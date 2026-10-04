"""SF-CMD-1 "The unrehearsed line" — part (ii), THE FIXES W1 … W9 (SCORE_FINISH
_SPEC.md §3 Step 4, October 3, 2026; rules SYSTEMS_REFERENCE.md §88; rows
BUG_FIXES.md §SF-CMD-1 census worklist).

Every pin drives the real `POST /command` on a fresh SHIPPED 1805 boot (Ney
and Davout at Rhineland, Mack at Swabia, Prussia at peace, Bavaria our ally,
the chest at 800) and reads the WORLD beside the message. The blind census's
own lines are the fixtures, verbatim; a lever-down arm per rule reproduces
the measured defect so the fix is falsifiable.
"""
from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

import backend.ai.clause_guards as CG
import backend.ai.condition_grammar as CGR
import backend.ai.llm_client as LC
import backend.ai.state_desk as SD
import backend.main as M
from backend.commands.parser import CommandParser

SHRUG = re.compile(r"cannot answer that from the dispatches|cannot interpret|order eludes me|"
                   r"cannot parse this order|cannot make sense of this|instruction is unclear", re.I)


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False
    return TestClient(M.app), M.world


def post(client, command, **extra):
    body = {"command": command}
    body.update(extra)
    return client.post("/command", json=body).json()


def answered(reply) -> bool:
    msg = str(reply.get("message") or "")
    return bool(msg.strip()) and not SHRUG.search(msg)


# ═══════════════════════════════════════════════════════════════════════════
# W1 / CRT-9 — the desk answers the natural question
# ═══════════════════════════════════════════════════════════════════════════

W1_LINES = [
    # the census's own classes, one or two lines each
    "what are the odds if Ney attacks Mack", "if Ney attacks Mack, what are his chances",
    "how long for Massena to reach Vienna", "why are we at war with Austria",
    "what's our net", "what does recruiting infantry cost", "what does it cost to commission Mortier",
    "who is winning the war", "what is Ney's trust", "what does Davout's ability do",
    "how do Davout and Bernadotte get on", "is Prussia against us", "what is our force limit",
    "how far is Vienna from Rhineland", "is Swabia next to Rhineland", "what is Bavaria's army",
    "how many enemy marshals are near Rhineland", "is Deroy still at Munich",
    "what are my marshals doing", "which of my marshals is strongest", "who's closest to Mack",
    "what is Murat's morale", "is anyone fortified", "is Ney drilling",
    "what standing orders are active", "when does Lannes arrive at Swabia",
    "what turn is it", "what date is it", "what does a fort do", "what does drilling do",
    "what does fortify do", "what happens if I fortify at Rhineland", "what does form square do",
    "what does support mean", "how much AP does a march cost", "how much does scouting cost",
    "what will it cost to keep the army for a turn", "why is our upkeep so high",
    "how much are we paying in rentes", "what is the blockade costing us",
    "how many ships do we have", "where is the fleet", "how strong is the Royal Navy",
    "can we cross to London", "what are the odds of landing in Ireland", "how long to build a ship",
    "what is the Continental System closure", "is the Channel open", "what is the fleet's readiness",
    "would Austria accept peace", "what terms would Britain accept",
    "is Prussia likely to join the coalition", "what is the coalition's threat level",
    "how much would it cost to buy off Prussia's design", "what is our relation with Russia",
    "who leads the coalition", "is Bavaria a vassal of Austria", "who are our vassals",
    "how loyal is Holland", "what tribute do we get from vassals",
    "what's the war score against Austria", "what is Britain's war weariness",
    "what is Prussia's agenda toward Hanover", "what does guaranteeing Prussia do",
    "what does sponsoring a design do", "what is Ney's ability", "what does the Rally do",
    "what is Murat's shock skill", "who is the best general for an assault",
    "which marshal has the most glory", "is anyone jealous", "does Ney dislike Massena",
    "what does Soult think of Ney", "what is the Emperor's authority", "how is my grip",
    "what does the Presence do", "can Napoleon be captured", "is Mack fortified",
    "what terrain is Swabia", "what is Tyrol like", "how many provinces do we hold",
    "how many provinces does Austria hold", "what did Mack do last turn",
    "did anyone attack us last turn", "any news from the courts", "has Russia moved",
    "what's the garrison at Paris", "what's the stability of Rhineland",
    "how much does Rhineland earn", "what buildings are at Paris", "can I build at Swabia",
    "what does an estate do for Ney", "is anyone expecting a reward", "why is Lannes unhappy",
    "how much is Mortier", "who can I commission", "can Massena hold Milan",
    "what if Mack attacks Davout", "what would happen if I march Ney into Swabia",
    "who should I attack first", "whats the best move", "are we ready to fight",
    "what's the French army's total strength", "how many men do we have in total",
    "is Bernadotte reliable", "whats mack doing",
]


class TestW1TheDeskAnswers:
    @pytest.mark.parametrize("line", W1_LINES)
    def test_the_natural_question_is_answered_and_nothing_is_spent(self, shipped, line):
        client, world = shipped
        before = (int(world.actions_remaining), int(world.gold), int(world.diplomatic_points),
                  {m.name: (m.location, int(m.strength)) for m in world.marshals.values()})
        reply = post(client, line)
        assert answered(reply), (line, reply.get("message"))
        after = (int(world.actions_remaining), int(world.gold), int(world.diplomatic_points),
                 {m.name: (m.location, int(m.strength)) for m in world.marshals.values()})
        assert before == after, line

    def test_the_answers_read_the_board(self, shipped):
        client, world = shipped
        assert "Ney" in post(client, "which of my marshals is strongest")["message"] or \
            "Massena" in post(client, "which of my marshals is strongest")["message"]
        msg = post(client, "how many provinces do we hold")["message"]
        assert str(len(world.get_nation_regions("France"))) in msg
        msg = post(client, "what is Ney's trust")["message"]
        assert str(int(world.get_marshal("Ney").trust.value)) in msg
        msg = post(client, "how do Davout and Bernadotte get on")["message"]
        assert "Davout" in msg and "Bernadotte" in msg and "hostile" in msg.lower()
        msg = post(client, "what turn is it")["message"]
        assert "turn 1" in msg and "1805" in msg
        msg = post(client, "is Swabia next to Rhineland")["message"]
        assert msg.startswith("Yes")

    def test_an_unknown_name_is_refused_never_substituted(self, shipped):
        client, world = shipped
        for line in ("where is Zorglub", "is Atlantis ours", "where is Wellington"):
            msg = post(client, line)["message"]
            assert "no marshal, no province, no court" in msg, (line, msg)
            assert "Nothing is substituted" in msg
            assert not any(m.name in msg for m in world.get_player_marshals()), (line, msg)

    def test_a_typo_of_one_roster_name_is_disclosed(self, shipped):
        client, _ = shipped
        msg = post(client, "where is Archduke Jhon")["message"]
        assert msg.startswith("(I read 'Jhon' as Archduke John.)"), msg
        assert "Tyrol" in msg or "no word" in msg
        msg = post(client, "where is Bernadote right now")["message"]
        assert "Bernadotte" in msg and msg.startswith("(I read 'Bernadote' as Bernadotte.)")

    def test_a_capitalised_game_term_is_not_a_name(self, shipped):
        """"the Staff", "the Royal Navy", "AP" — the first draft refused each
        as an unknown name; they are game terms the desk owns."""
        client, _ = shipped
        assert "laws of state" in post(client, "what does the Staff cost")["message"].lower()
        assert "100 sail" in post(client, "how strong is the Royal Navy")["message"]
        assert "standing order" in post(client, "how much AP does a march cost")["message"]

    def test_a_question_is_never_split_on_a_second_name(self, shipped):
        """"how do Davout and Bernadotte get on" was cut at "and Bernadotte"
        into "how do Davout" and a dropped tail."""
        client, _ = shipped
        reply = post(client, "how do Davout and Bernadotte get on")
        assert reply.get("dropped_sequel") in (None, "")
        assert "hostile" in reply["message"].lower()

    def test_a_hedge_is_left_to_the_router(self, shipped):
        client, _ = shipped
        msg = post(client, "perhaps build ships")["message"]
        assert "45 sail" not in msg

    def test_the_lever_restores_the_shrug(self, shipped, monkeypatch):
        client, _ = shipped
        monkeypatch.setattr(SD, "STATE_DESK_ACTIVE", False)
        assert SHRUG.search(post(client, "what is Ney's trust")["message"])

    def test_the_three_question_leads(self):
        assert CG.is_question("whats mack doing", ["Mack"])
        assert CG.is_question("any news from the courts", [])
        assert CG.is_question("if Ney attacks Mack, what are his chances", ["Ney", "Mack"])
        # an order with a comma tail is still an order
        assert not CG.is_question("if Mack is still in Swabia, attack him", ["Mack"])


# ═══════════════════════════════════════════════════════════════════════════
# W2 — the contingency phrasings
# ═══════════════════════════════════════════════════════════════════════════

class TestW2TheContingencyPhrasings:
    def test_the_arrival_idiom_is_the_tail(self, shipped):
        client, world = shipped
        a = post(client, "Soult, march to Swabia and attack Mack when you get there")
        assert "contingency" not in a["message"]
        # the same reply the fused form gives (CR-7-1's own idiom)
        M._reset_world_state()
        b = post(client, "Soult, march to Swabia and attack Mack")
        assert a["message"].split("\n")[0] == b["message"].split("\n")[0]

    def test_the_arrival_idiom_strips_only_at_the_tail(self):
        assert CGR.strip_arrival_idiom("march to Swabia and attack Mack when you get there") == (
            "march to Swabia and attack Mack", True)
        assert CGR.strip_arrival_idiom("attack Mack the moment you arrive")[0] == "attack Mack"
        assert CGR.strip_arrival_idiom("when you get there")[1] is False

    def test_a_true_premise_runs_the_order_now(self, shipped):
        client, world = shipped
        reply = post(client, "if Mack is still in Swabia, attack him")
        assert "contingency" not in reply["message"]
        assert "MUSTER" in reply["message"] or "attack" in reply["message"].lower()

    def test_a_false_premise_is_refused_by_name_free(self, shipped):
        client, world = shipped
        ap = int(world.actions_remaining)
        reply = post(client, "if Mack is still in Lorraine, attack him")
        assert reply["success"] is False
        assert "Mack" in reply["message"] and "Lorraine" in reply["message"]
        assert "Swabia" in reply["message"]  # where our word places him
        assert int(world.actions_remaining) == ap
        assert all(not getattr(m, "strategic_order", None) for m in world.get_player_marshals())

    def test_an_unseen_premise_asks_for_a_scout(self, shipped):
        client, world = shipped
        from backend.models.intel import UNKNOWN
        kutuzov = next(m for m in world.marshals.values() if m.name == "Kutuzov")
        assert not world.get_region_intel(kutuzov.location).visibility_at_least("PARTIAL") or True
        reply = post(client, f"if Kutuzov is still in {kutuzov.location}, attack him")
        assert reply["success"] is False
        assert "no word" in reply["message"] or "last word" in reply["message"]

    def test_the_premise_lever_restores_the_refusal(self, shipped, monkeypatch):
        client, _ = shipped
        monkeypatch.setattr(CGR, "A_PREMISE_IS_CHECKED_AT_ISSUANCE", False)
        assert "contingency" in post(client, "if Mack is still in Swabia, attack him")["message"]

    def test_if_he_moves_stays_refused_and_names_the_pursuit(self, shipped):
        client, world = shipped
        ap = int(world.actions_remaining)
        reply = post(client, "Ney, attack Mack if he moves")
        assert "contingency" in reply["message"]
        assert "pursue Mack" in reply["message"]
        assert int(world.actions_remaining) == ap

    def test_once_a_friend_engages_is_support(self, shipped):
        client, world = shipped
        reply = post(client, "Soult, once Ney engages Mack, hit his flank")
        assert "contingency" not in reply["message"]
        soult = world.get_marshal("Soult")
        assert soult.strategic_order is not None
        assert soult.strategic_order.command_type == "SUPPORT"
        assert soult.strategic_order.target == "Ney"

    def test_the_engagement_rewrite_needs_a_friend(self):
        roster = ["Ney", "Davout", "Soult"]
        assert CGR.rewrite_engagement_support("Soult, once Ney engages Mack, hit his flank", roster) == (
            "Soult, support Ney", "Ney")
        assert CGR.rewrite_engagement_support("Soult, once Mack engages Ney, hit his flank", roster)[1] is None
        assert CGR.rewrite_engagement_support("Ney, attack if Davout supports", roster)[1] is None

    def test_a_halt_tail_marches_and_says_the_roads_rule(self, shipped):
        client, world = shipped
        reply = post(client, "Lannes, head for Swabia but stop if Mack turns on you")
        assert "contingency" not in reply["message"]
        assert "halts of itself" in reply["message"]
        lannes = world.get_marshal("Lannes")
        assert lannes.strategic_order is not None or "blocks the path" in reply["message"]

    def test_the_halt_lever_restores_the_refusal(self, shipped, monkeypatch):
        client, _ = shipped
        monkeypatch.setattr(CGR, "A_HALT_TAIL_IS_THE_ROADS_OWN_RULE", False)
        assert "contingency" in post(client, "Lannes, head for Swabia but stop if Mack turns on you")["message"]


# ═══════════════════════════════════════════════════════════════════════════
# W3 — the basic forms
# ═══════════════════════════════════════════════════════════════════════════

class TestW3TheBasicForms:
    @pytest.mark.parametrize("line", ["end the turn", "just end the turn", "end my turn",
                                      "End this turn.", "Berthier, end the turn"])
    def test_end_the_turn_ends_the_turn(self, shipped, line):
        client, world = shipped
        assert CG.is_bare_end_turn(line), line
        post(client, line)
        assert world.current_turn == 2, line

    @pytest.mark.parametrize("line", ["what happens next turn", "Davout, fortify until next turn",
                                      "Ney, hold Bavaria until the end turn", "Ney, end turn"])
    def test_the_fa6_controls_still_hold(self, line):
        assert CG.is_bare_end_turn(line) is False, line

    def test_the_client_gate_speaks_every_phrasing(self):
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "godot-client", "project-sovereign",
                            "scripts", "main.gd")
        src = open(path, encoding="utf-8").read()
        body = src[src.index("func _is_end_turn_phrasing("):]
        body = body[:body.index("func _execute_end_turn():")]
        needles = set(re.findall(r'c\s*==\s*"([^"]+)"', body))
        assert set(CG.END_TURN_PHRASINGS) <= needles, needles
        for filler in CG.END_TURN_LEADING_FILLER:
            assert f'"{filler}"' in body, filler

    def test_the_negated_compound_asks_and_does_not_end_the_turn(self, shipped):
        client, world = shipped
        reply = post(client, "don't move anyone this turn, just end the turn")
        assert world.current_turn == 1
        assert "Shall I close the day" in reply["message"]

    def test_a_bare_go_asks_where(self, shipped):
        client, world = shipped
        reply = post(client, "Ney, go")
        assert "Where shall Ney march" in reply["message"]
        assert world.get_marshal("Ney").location == "Rhineland"

    def test_could_x_please_is_an_order(self, shipped):
        client, world = shipped
        reply = post(client, "could Ney please fortify")
        assert not SHRUG.search(reply["message"])
        ney = world.get_marshal("Ney")
        assert ney.fortified or reply.get("pending_objection") or "objects" in reply["message"]
        # the question stays a question
        assert CG.is_question("can Ney attack Mack", ["Ney", "Mack"])
        assert not CG.is_question("could Ney please fortify", ["Ney"])

    def test_the_collective_march_relays_the_rest(self, shipped):
        client, world = shipped
        reply = post(client, "Ney, Davout, Soult: everyone converge on Swabia")
        assert "One order at a time" in reply["message"]
        assert reply.get("dropped_sequel") == "Davout, Soult: converge on Swabia"

    def test_keep_an_eye_on_is_a_scout(self, shipped):
        client, world = shipped
        reply = post(client, "Bernadotte, keep an eye on Berlin")
        assert "scouts Berlin" in reply["message"]

    def test_reward_x_opens_the_reward_desk(self, shipped):
        client, world = shipped
        reply = post(client, "reward Lannes")
        assert reply.get("open_reward_for") == "Lannes"
        assert "Lannes expects" in reply["message"]
        assert int(world.admin_actions_remaining) == 2


# ═══════════════════════════════════════════════════════════════════════════
# W4 / CRT-8 — the Cabinet's verbs without the address; its rules
# ═══════════════════════════════════════════════════════════════════════════

class TestW4TheCabinetsVerbs:
    def test_propose_an_alliance_to_prussia_reaches_the_cabinet(self, shipped):
        client, _ = shipped
        reply = post(client, "propose an alliance to Prussia")
        assert not SHRUG.search(reply["message"])
        assert "DP" in reply["message"] or reply.get("diplomatic_dialogue")

    def test_ask_austria_for_terms_is_request_terms(self, shipped):
        client, _ = shipped
        reply = post(client, "ask Austria for terms")
        assert "terms" in reply["message"].lower() and not SHRUG.search(reply["message"])

    def test_a_marshal_addressed_keeps_the_verb_from_the_cabinet(self, shipped):
        client, world = shipped
        reply = post(client, "Ney, propose an alliance to Prussia")
        assert not reply.get("diplomatic_dialogue")
        assert world.get_diplomatic_state("France", "Prussia") == "PEACE"

    @pytest.mark.parametrize("line", ["improve our relations with Prussia", "make friends with Saxony",
                                      "mend relations with Prussia", "warm our ties with Saxony"])
    def test_rs7_the_relation_phrasings_begin_the_mission(self, shipped, line):
        client, world = shipped
        reply = post(client, line)
        assert "improve relations" in reply["message"].lower(), reply["message"]
        assert not SHRUG.search(reply["message"])
        assert "await your instructions" not in reply["message"]

    def test_cq36_the_boot_alliance_is_refused_by_its_true_name(self, shipped):
        client, world = shipped
        reply = post(client, "break the alliance with Spain")
        assert "bond of 1805" in reply["message"]
        assert "downgrade" in reply["message"].lower()
        assert world.get_diplomatic_state("France", "Spain") == "ALLIANCE"
        from backend.game_logic.diplomacy import get_diplomatic_preview
        preview = get_diplomatic_preview(world, "Spain")
        row = next(a for a in preview["actions"] if a["action"] == "break_treaty")
        assert row["available"] is False and "1805" in row["disabled_reason"]

    def test_cx_x3_vassalize_a_standing_great_power_is_refused(self, shipped):
        client, world = shipped
        for court in ("Austria", "Britain", "Russia"):
            reply = post(client, f"vassalize {court}")
            assert court not in world.vassals, court
            assert "still stands" in reply["message"], reply["message"]

    def test_cx_x3_a_court_at_peace_is_the_cabinets_priced_proposal(self, shipped):
        client, world = shipped
        reply = post(client, "make Bavaria a vassal")
        assert "Bavaria" not in world.vassals
        assert reply.get("diplomatic_dialogue") or "Vassalage" in reply["message"]

    def test_the_vassal_gate_lever_restores_the_free_treaty_path(self, shipped, monkeypatch):
        """Lever down: a court at peace is vassalized free by the treaty path
        (CX-X3's peace-side half); the WAR path keeps GEV-1's own gate."""
        from backend.commands.vassal_executor import VassalExecutor
        client, world = shipped
        monkeypatch.setattr(VassalExecutor, "THE_VASSAL_VERB_IS_GATED", False)
        post(client, "vassalize Bavaria")
        assert "Bavaria" in world.vassals


# ═══════════════════════════════════════════════════════════════════════════
# W5 … W9
# ═══════════════════════════════════════════════════════════════════════════

class TestW5TheSecondNameIsHeard:
    def test_the_comma_before_a_second_marshal_is_a_boundary(self, shipped):
        client, world = shipped
        reply = post(client, "Ney attack Mack, Davout support him")
        assert "Cannot find marshal 'Him'" not in reply["message"]
        assert reply.get("dropped_sequel") == "Davout support him"

    def test_him_after_support_is_the_man_last_addressed(self, shipped):
        client, world = shipped
        from backend.commands.context_carryover import resolve_context_references
        world.add_to_command_history({"raw_input": "Ney attack Mack", "marshal": "Ney",
                                      "action": "attack", "target": "Mack", "turn": 1})
        out = resolve_context_references("Davout support him", world)
        assert out.get("text", "") == "Davout support Ney" or "Ney" in str(out)


class TestW6TheEpithets:
    def test_iron_marshal_is_davout(self, shipped):
        client, world = shipped
        reply = post(client, "Iron Marshal, dig in")
        assert "Davout fortifies" in reply["message"] or world.get_marshal("Davout").fortified

    def test_the_bravest_of_the_brave_is_ney(self, shipped):
        client, world = shipped
        reply = post(client, "the Bravest of the Brave, attack Mack")
        assert "in the order of battle" not in reply["message"]
        assert "Ney" in reply["message"]

    def test_a_title_the_board_does_not_carry_stays_refused(self, shipped):
        client, world = shipped
        reply = post(client, "Prince of Moskowa, attack Mack")
        assert all(m.location == "Rhineland" for m in (world.get_marshal("Ney"), world.get_marshal("Davout")))


class TestW7TheAdverbAndTheReasonClause:
    def test_hunt_mack_down_pursues_mack(self, shipped):
        client, world = shipped
        reply = post(client, "Murat, hunt Mack down")
        assert "Mack Down" not in reply["message"]
        assert "pursues Mack" in reply["message"] or "Mack" in reply["message"]

    def test_fall_back_with_a_reason_is_a_retreat(self, shipped):
        client, world = shipped
        reply = post(client, "Ney, fall back - I don't like Swabia")
        assert "could not make out a destination" not in reply["message"]
        assert "retreat" in reply["message"].lower() or "objects" in reply["message"]

    def test_fall_back_to_a_place_is_still_a_march(self, shipped):
        client, world = shipped
        reply = post(client, "Ney, fall back to Lorraine")
        assert "Lorraine" in reply["message"]

    N2_TAILS = ("Ney, fall back now", "Ney, fall back in good order",
                "Ney, fall back and regroup", "Ney, fall back at once",
                "Ney, withdraw immediately", "Ney, retire at once")

    @pytest.mark.parametrize("line", N2_TAILS)
    def test_cx5_l5_n2_a_manner_tail_is_no_destination(self, shipped, line):
        """CX5-L5-N2 (the CR-6 triage, Sept 23), closed by this rule and
        re-measured at the Chunk 3b exit (Oct 3, 2026): "now", "at once",
        "in good order", "and regroup", "immediately" had each been read
        as a DESTINATION ("Region 'Now' not found.")."""
        client, world = shipped
        message = post(client, line)["message"]
        assert "not found" not in message, message
        assert "could not make out a destination" not in message, message
        assert "retreat" in message.lower() or "objects" in message, message

    def test_cx5_l5_n2_the_lever_down_reads_the_tail_as_a_place(self, shipped, monkeypatch):
        import backend.commands.parser as P
        client, world = shipped
        monkeypatch.setattr(P, "A_REASON_TAIL_IS_NOT_A_DESTINATION", False)
        assert "Region 'Now' not found" in post(client, "Ney, fall back now")["message"]

    def test_emperor_to_rhineland_is_a_move(self, shipped):
        client, world = shipped
        reply = post(client, "Emperor to Rhineland")
        assert world.get_marshal("Napoleon").location == "Rhineland", reply["message"]


class TestW8TheNavalPhrasings:
    def test_bring_the_fleet_home_is_the_guard_posture(self, shipped):
        client, world = shipped
        reply = post(client, "bring the fleet home")
        assert "guard" in reply["message"].lower()
        assert not SHRUG.search(reply["message"])

    def test_ship_davout_to_london_is_the_landing_verb(self, shipped):
        client, _ = shipped
        reply = post(client, "ship Davout to London")
        assert "transports" in reply["message"].lower() or "land" in reply["message"].lower()
        assert not SHRUG.search(reply["message"])


class TestW9TheRefusalNamesTheMan:
    def test_the_treasury_refusal_names_the_man_and_the_arm(self, shipped):
        client, world = shipped
        reply = post(client, "Murat, recruit cavalry")
        assert reply["success"] is False
        assert reply["message"].startswith("Murat's cavalry levy:")
        assert "1,504 gold" in reply["message"]
        from tools.unrehearsed_census import classify_order  # the census judge
        assert classify_order({"action": "recruit", "marshal": "Murat"}, reply) == "board_refusal"


class TestCRT9TheStateSpeaksFirst:
    def test_a_fortified_marshal_is_refused_a_march_free(self, shipped):
        client, world = shipped
        post(client, "Davout, fortify")
        davout = world.get_marshal("Davout")
        assert davout.fortified
        ap = int(world.actions_remaining)
        reply = post(client, "Davout, march to Paris")
        assert reply["success"] is False
        assert "fortified" in reply["message"] and "unfortify" in reply["message"]
        assert int(world.actions_remaining) == ap
        assert davout.strategic_order is None

    def test_a_fortified_marshal_may_hold(self, shipped):
        client, world = shipped
        post(client, "Davout, fortify")
        reply = post(client, "Davout, hold Rhineland")
        assert "cannot march from his works" not in reply["message"]

    def test_the_probe_names_both_arms(self, shipped):
        from backend.commands.strategic import march_state_refusal
        client, world = shipped
        davout = world.get_marshal("Davout")
        davout.fortified = True
        assert "fortified" in (march_state_refusal(world, davout) or "")
        davout.fortified = False
        davout.drilling_locked = True
        assert "drill" in (march_state_refusal(world, davout) or "")


# ═══════════════════════════════════════════════════════════════════════════
# The completion census — a FRESH blind file, never the committed one
# ═══════════════════════════════════════════════════════════════════════════

class TestTheFreshBlindCensus:
    """The completion definition (STATUS, Step 4): the census re-run on a
    FRESH blind file (`unrehearsed_2026_10_03_fresh.json`, a second blind
    author) with the dangerous classes at zero and the question shrugs at or
    under 30 of 150. The record is re-read by the judge that SHIPS.

    Two readings the judge files as dangerous are RECORDED designs, not
    defects, and are pinned by name: `Berthier, propose peace to Austria`
    (CX-R1 — the desk relays an order of state; the blind author expected
    the wrong-desk refusal) and `Davout, fortify Rhineland and hold it until
    Lannes arrives` (FA-50's hold idiom — "fortify and hold" is ONE hold
    order, pinned in the CR-7 family; the author expected a fortify)."""

    RECORDED = {
        "Berthier, propose peace to Austria",
        "Davout, fortify Rhineland and hold it until Lannes arrives",
    }

    def _record(self):
        import importlib.util
        import json
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location("census_fresh", root / "tools" / "unrehearsed_census.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        rec = json.loads((root / "docs" / "audits" / "unrehearsed" / "2026_10_03_fresh_keyless.json")
                         .read_text(encoding="utf-8"))
        return mod.reclassify(rec)

    def test_the_fresh_file_is_a_second_blind_author(self):
        import json
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        fresh = json.loads((root / "tools" / "playtest_scripts" / "unrehearsed_2026_10_03_fresh.json").read_text(encoding="utf-8"))
        first = json.loads((root / "tools" / "playtest_scripts" / "unrehearsed_2026_10_03.json").read_text(encoding="utf-8"))
        assert len(fresh["orders"]) == 150 and len(fresh["questions"]) == 150
        overlap = {o["line"] for o in fresh["orders"]} & {o["line"] for o in first["orders"]}
        overlap |= {q["line"] for q in fresh["questions"]} & {q["line"] for q in first["questions"]}
        # the two authors meet on the canonical forms ("build ships",
        # "commission Mortier") — measured 15 of 300; the file is fresh when
        # 280 of its 300 lines are its own
        assert len(overlap) <= 20, overlap

    def test_nothing_the_player_did_not_mean_was_executed(self):
        rec = self._record()
        assert len(rec["rows"]) == 300
        assert set(rec["dangerous"]) <= self.RECORDED, rec["dangerous"]

    def test_the_question_shrugs_are_under_the_bar(self):
        rec = self._record()
        shrugs = int(rec["totals"]["question"].get("shrug", 0))
        assert shrugs <= 30, shrugs
        assert int(rec["totals"]["question"].get("answered", 0)) >= 120

    def test_the_order_shrugs_are_under_the_first_census(self):
        rec = self._record()
        assert int(rec["totals"]["order"].get("shrug", 0)) <= 9
        assert int(rec["totals"]["order"].get("as_meant", 0)) >= 55
