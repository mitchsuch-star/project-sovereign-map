"""CRT-11 "The second name is heard" — a second name is a ROLE, never a
second order (SCORE_FINISH_SPEC.md §3 Step 4, Chunk 3b trimmed to what the
census confirms; COMMAND_ROBUSTNESS_SPEC.md §12.16; rules
SYSTEMS_REFERENCE.md §89; rows BUG_FIXES.md RS-6, RS-8; the HOLD arm's blind
line "Lannes, follow Ney in and back him up.").

Every pin drives the real `POST /command` on a fresh SHIPPED 1805 boot
(Ney and Davout at Rhineland, Soult at Lorraine, Lannes and Murat at
Franche-Comte, Mack at Swabia) and reads the world beside the message.
Reproduced at HEAD `e631f4bd` before a line was written:

  * "Marshal Soult, bring your corps up in support of Ney." -> "Cannot find
    marshal 'Of Ney' to support."
  * "Soult, march in support of Ney" -> a 1-action march to the province
    "In Support Of Ney"; "march to the aid of Ney" -> "Aid Of Ney".
  * "Soult, come to Ney's support" -> "You wish me to support Bernadotte?"
  * "Lannes, follow Ney in and back him up." -> "the instruction is unclear".
  * "Ney, march on Swabia and destroy Mack" -> a plain march, no arrival
    target, the destroy clause gone without a word; "crush" alike.
  * "Ney, march against Mack" -> a march to the province "Against Mack".
  * "Ney, fortify and destroy Mack" -> FOUGHT, the fortify swallowed.
  * the explicit order's bad-odds interrupt quoted Ney's 24,000 alone while
    the battle it would start drew 85,000 against Mack's 52,000.
"""

import pytest
from fastapi.testclient import TestClient

import backend.ai.attack_vocabulary as AV
import backend.ai.second_name as SN
import backend.commands.context_carryover as CC
import backend.commands.strategic as ST
import backend.main as M
from backend.commands.parser import CommandParser


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


def order_of(world, name):
    o = getattr(world.get_marshal(name), "strategic_order", None)
    return (o.command_type, o.target) if o else None


def parse(text):
    return M.parser.parse(text, M.get_llm_game_state(), world=M.world)


# ═══════════════════════════════════════════════════════════════════════════
# RS-6 + the HOLD line: the supporting phrasings are the SUPPORT order
# ═══════════════════════════════════════════════════════════════════════════

SUPPORT_LINES = [
    ("Marshal Soult, bring your corps up in support of Ney.", "Soult"),
    ("Soult, march in support of Ney", "Soult"),
    ("Soult, march to the aid of Ney", "Soult"),
    ("Soult, come to Ney's support", "Soult"),
    ("Soult, ride to the relief of Ney", "Soult"),
    ("Soult, march to Ney's aid", "Soult"),
    ("Lannes, follow Ney in and back him up.", "Lannes"),
    ("Lannes, follow Ney", "Lannes"),
    ("Lannes, back Ney up", "Lannes"),
]


class TestTheSupportRoleIsHeard:

    @pytest.mark.parametrize("line,who", SUPPORT_LINES)
    def test_the_line_is_a_support_order_for_ney(self, shipped, line, who):
        client, world = shipped
        reply = post(client, line)
        message = str(reply.get("message") or "")
        assert order_of(M.world, who) == ("SUPPORT", "Ney"), (line, message)
        assert "Of Ney" not in message and "Aid Of" not in message, message
        assert "Bernadotte" not in message, message

    @pytest.mark.parametrize("line,who", SUPPORT_LINES)
    def test_a_support_order_costs_one_action(self, shipped, line, who):
        client, world = shipped
        ap = int(world.actions_remaining)
        post(client, line)
        assert int(M.world.actions_remaining) == ap - 1, line

    def test_the_record_keeps_the_typed_words(self, shipped):
        client, world = shipped
        post(client, "Soult, march in support of Ney")
        order = world.get_marshal("Soult").strategic_order
        assert "in support of Ney" in (order.original_command or ""), order.original_command

    def test_unaddressed_it_asks_which_marshal(self, shipped):
        client, world = shipped
        reply = post(client, "march in support of Ney")
        assert "Which marshal shall support Ney" in str(reply.get("message") or ""), reply.get("message")

    def test_the_strategic_reader_skips_a_leading_of(self, shipped):
        """The reader's own half, for a phrasing that reaches it unrewritten:
        the SUPPORT keyword's tail "of Ney" names Ney."""
        from backend.ai.strategic_parser import _friendly_forms, _friendly_head
        forms = _friendly_forms("Soult", M.world)
        assert _friendly_head("of ney", forms) == "ney"
        assert _friendly_head("of marshal ney.", forms) == "ney"

    def test_a_foe_is_never_supported(self, shipped):
        """Only a marshal of OURS is restated: "the aid of Mack" names no
        order the engine has."""
        assert SN.rewrite_support_role("Soult, march to the aid of Mack",
                                       ["Ney", "Soult"]) == (
            "Soult, march to the aid of Mack", None)

    def test_the_condition_after_the_phrase_rides_along(self, shipped):
        result = parse("Soult, march in support of Ney until the battle is won")
        assert result.get("strategic_type") == "SUPPORT"
        assert result.get("strategic_condition") == {"until_battle_won": True}

    def test_him_in_the_same_clause_is_the_man_named_there(self, shipped):
        """The carryover read "support him" as the last man addressed — here
        Lannes himself; the antecedent named in the same clause wins."""
        client, world = shipped
        world.add_to_command_history({"raw_input": "Lannes, move to Lorraine",
                                      "marshal": "Lannes", "action": "move",
                                      "target": "Lorraine", "turn": 1})
        out = CC.resolve_context_references("Lannes, follow Ney in and support him", world)
        assert out.get("command", "").endswith("support Ney"), out
        # W5's pin stands: a second clause's "him" is still the head's man
        world.add_to_command_history({"raw_input": "Ney attack Mack", "marshal": "Ney",
                                      "action": "attack", "target": "Mack", "turn": 1})
        out = CC.resolve_context_references("Davout support him", world)
        assert "Ney" in str(out), out

    def test_the_judge_reads_the_engaged_refusal_as_the_boards(self):
        """The exit's HOLD arm: the blind line now reads as the SUPPORT it
        means and the board answers with the march law's engaged refusal,
        naming Lannes — the ONE judge counts it as the board's, not as a
        misreading (`tools/_score_probes.py`, BOARD_GATE_RX)."""
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from tools import _score_probes as P
        msg = ("Lannes is engaged with Mack and cannot begin a strategic march. "
               "Deal with the engagement first.")
        assert P.BOARD_GATE_RX.search(msg)
        assert not P.REFUSED_RX.search(msg)

    def test_the_lever_down_restores_the_misreads(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(SN, "THE_SUPPORT_ROLE_IS_HEARD", False)
        reply = post(client, "Lannes, follow Ney in and back him up.")
        assert order_of(M.world, "Lannes") is None, reply.get("message")
        reply = post(client, "Soult, march in support of Ney")
        assert order_of(M.world, "Soult") != ("SUPPORT", "Ney"), reply.get("message")


# ═══════════════════════════════════════════════════════════════════════════
# RS-8: the destroy clause is heard
# ═══════════════════════════════════════════════════════════════════════════

class TestTheDestroyClauseIsHeard:

    @pytest.mark.parametrize("line", [
        "Ney, march on Swabia and destroy Mack",
        "Ney, march on Swabia and crush Mack",
        "Ney, march on Swabia and smash Mack",
        "Ney, march on Swabia then destroy Mack",
        "Ney, march on Swabia and attack Mack",
    ])
    def test_the_arrival_names_mack(self, shipped, line):
        result = parse(line)
        assert result.get("strategic_type") == "MOVE_TO", line
        assert result.get("attack_on_arrival") is True, line
        assert result.get("arrival_target") == "Mack", line
        assert result.get("dropped_sequel") is None, line

    def test_a_capture_tail_arms_the_arrival(self, shipped):
        result = parse("Ney, march to Swabia and capture it")
        assert result.get("attack_on_arrival") is True
        assert result.get("arrival_target") is None

    def test_march_against_is_the_foe_not_a_province(self, shipped):
        client, world = shipped
        reply = post(client, "Ney, march against Mack")
        message = str(reply.get("message") or "")
        assert "Against Mack" not in message, message
        order = world.get_marshal("Ney").strategic_order
        assert order is None or order.target == "Mack", message

    def test_a_head_that_cannot_carry_an_arrival_keeps_its_order(self, shipped):
        """CR-7-1's rule, one verb over: "fortify and destroy Mack" FOUGHT
        with the fortify swallowed."""
        client, world = shipped
        mack = int(world.get_marshal("Mack").strength)
        reply = post(client, "Ney, fortify and destroy Mack")
        assert int(M.world.get_marshal("Mack").strength) == mack, reply.get("message")
        assert not reply.get("battle_report")
        assert reply.get("dropped_sequel") == "destroy Mack", reply.get("dropped_sequel")

    def test_one_alternation_feeds_every_reader(self):
        """The five readers are built from the vocabulary, never a hand list."""
        alt = AV.arrival_tail_alternation(True).split("|")
        assert set(alt) == set(AV.BATTLE_VERBS | AV.CAPTURE_VERBS)
        assert set(AV.arrival_tail_alternation(False).split("|")) == {"attack", "engage", "assault"}

    def test_the_lever_down_loses_the_clause_again(self, shipped, monkeypatch):
        monkeypatch.setattr(AV, "THE_DESTROY_CLAUSE_IS_HEARD", False)
        result = parse("Ney, march on Swabia and destroy Mack")
        assert result.get("arrival_target") is None
        assert result.get("attack_on_arrival") is not True


# ═══════════════════════════════════════════════════════════════════════════
# RS-8's rider (P4): the explicit interrupt names the muster
# ═══════════════════════════════════════════════════════════════════════════

class TestTheExplicitInterruptNamesTheMuster:

    def test_the_first_step_interrupt_names_who_would_answer(self, shipped):
        client, world = shipped
        reply = post(client, "Ney, march on Swabia and destroy Mack")
        message = str(reply.get("message") or "")
        assert "Odds unfavorable" in message, message
        assert "Berthier adds:" in message and "would answer the guns" in message, message
        assert "with the muster committed" in message, message

    def test_the_lever_down_keeps_the_bare_line(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(ST, "THE_EXPLICIT_INTERRUPT_NAMES_THE_MUSTER", False)
        reply = post(client, "Ney, march on Swabia and destroy Mack")
        assert "Berthier adds:" not in str(reply.get("message") or "")
