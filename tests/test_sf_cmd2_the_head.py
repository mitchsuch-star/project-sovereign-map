"""SF-CMD-2's head (Score Finish Step 7, October 4, 2026) — the reflexive
(NPC-9 / NP-X1) and the emphatic order (SF5-RV13). CQ-33 and CX5-L5-F7 land in
`tests/test_crt6_the_retreat_is_a_word.py`, the file their rows name.

Reproduced at `POST /command` on a fresh 1805 boot before a line was written:

    `I will march to Lorraine myself and attack Mack`
        -> "Napoleon begins march to Lorraine Myself." (1 action)
    `I will take the field myself and march to Lorraine`
        -> "Which marshal shall march to Lorraine, Sire?"
    no Emperor on the board: `Ney, march to Lorraine myself`
        -> a 2-action MOVE_TO on "Lorraine Myself"
    no Emperor: `I will march to Lorraine myself`
        -> "Which marshal shall march to Lorraine Myself, Sire?"
    Ney's bad-odds interrupt pending: `attack, what are you waiting for`
    (with and without "?"), `hold, do as I say`, `do what I say: attack`
        -> "A question is not an answer, Sire — nothing was ordered."
    the general road: `Ney, do as I say and attack Mack`
        -> the desk's shrug ("I cannot answer that from the dispatches")

Every pin drives the real `POST /command`; each rule's lever down reproduces
its row.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import backend.ai.clause_guards as CG
import backend.commands.parser as P
import backend.main as M
from backend.commands.parser import CommandParser
from backend.models.marshal import StrategicOrder


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


@pytest.fixture
def no_emperor(shipped):
    client, world = shipped
    world.marshals.pop("Napoleon", None)
    world.invalidate_active_nations_cache()
    return client, world


@pytest.fixture
def interrupt(shipped):
    """Ney on Mack's province under a PURSUE, the first-step gate's own
    bad-odds interrupt pending — the board SF5-X1's pins use."""
    client, world = shipped
    ney, mack = world.marshals["Ney"], world.marshals["Mack"]
    ney.location = mack.location
    ney.strategic_order = StrategicOrder(
        command_type="PURSUE", target="Mack", target_type="marshal",
        started_turn=int(world.current_turn), original_command="pursue Mack",
        path=[mack.location])
    ney.pending_interrupt = {
        "marshal": "Ney", "interrupt_type": "contact_bad_odds", "enemy": "Mack",
        "location": ney.location, "is_first_step": True,
        "options": ["attack_anyway", "hold_position", "cancel_order"],
        "message": "Ney faces poor odds against Mack."}
    return client, world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


def battles(world):
    return len([e for e in world.event_log if e.get("type") == "battle"])


def order(world, name):
    o = world.marshals[name].strategic_order
    return (o.command_type, o.target) if o is not None else None


class TestAReflexiveIsNeverAPlace:
    def test_the_emperor_marches_to_lorraine(self, shipped):
        client, world = shipped
        data = post(client, "I will march to Lorraine myself and attack Mack")
        assert order(world, "Napoleon") == ("MOVE_TO", "Lorraine"), data.get("message")
        assert "Myself" not in str(data.get("message") or "")

    def test_taking_the_field_himself_is_the_emperors_march(self, shipped):
        client, world = shipped
        data = post(client, "I will take the field myself and march to Lorraine")
        assert order(world, "Napoleon") == ("MOVE_TO", "Lorraine"), data.get("message")

    def test_with_no_emperor_ney_marches_to_lorraine(self, no_emperor):
        client, world = no_emperor
        data = post(client, "Ney, march to Lorraine myself")
        assert order(world, "Ney") == ("MOVE_TO", "Lorraine"), data.get("message")
        assert "Myself" not in str(data.get("message") or "")

    def test_with_no_emperor_the_first_person_asks_which_marshal(self, no_emperor):
        client, world = no_emperor
        data = post(client, "I will march to Lorraine myself")
        assert str(data.get("message") or "") == "Which marshal shall march to Lorraine, Sire?"

    @pytest.mark.parametrize("raw,clean", [
        ("march to Ulm myself", "march to Ulm"),
        ("march to Ulm myself.", "march to Ulm"),
        ("I will march to Lorraine myself and attack Mack",
         "I will march to Lorraine and attack Mack"),
        ("scout Bavaria in person", "scout Bavaria"),
        ("I will go by myself to Paris", "I will go to Paris"),
        ("Ney, march to Paris", "Ney, march to Paris"),
    ])
    def test_the_marker_is_taken_out_anywhere(self, raw, clean):
        assert P.strip_self_markers(raw) == clean

    def test_the_lever_down_reproduces_the_phantom(self, no_emperor, monkeypatch):
        monkeypatch.setattr(P, "A_REFLEXIVE_IS_NEVER_A_PLACE", False)
        client, world = no_emperor
        post(client, "Ney, march to Lorraine myself")
        assert order(world, "Ney") == ("MOVE_TO", "Lorraine Myself")


class TestAnEmphaticOrderIsAnOrder:
    @pytest.mark.parametrize("phrase", ["attack, what are you waiting for",
                                        "attack, what are you waiting for?",
                                        "do what I say: attack"])
    def test_the_impatient_attack_answers_the_interrupt(self, interrupt, phrase):
        client, world = interrupt
        before = battles(world)
        data = post(client, phrase)
        assert battles(world) == before + 1, data.get("message")

    def test_the_impatient_hold_answers_the_interrupt(self, interrupt):
        client, world = interrupt
        data = post(client, "hold, do as I say")
        assert not str(data.get("message") or "").startswith("A question is not an answer")
        assert world.marshals["Ney"].pending_interrupt is None, data.get("message")

    def test_the_general_road_reads_the_order(self, shipped):
        client, world = shipped
        before = battles(world)
        data = post(client, "Ney, do as I say and attack Mack")
        assert battles(world) == before + 1, data.get("message")

    @pytest.mark.parametrize("phrase", ["what are you waiting for?",
                                        "should we attack, what are you waiting for",
                                        "should we attack?"])
    def test_a_real_question_still_orders_nothing(self, interrupt, phrase):
        """CRT-3's rule is untouched: rhetoric alone, or a question with
        rhetoric attached, fights nothing and leaves the interrupt standing
        (a question that names an option is restated; one that names none
        goes to the desk — SF5-X1's own split)."""
        client, world = interrupt
        before = battles(world)
        post(client, phrase)
        assert battles(world) == before, phrase
        assert world.marshals["Ney"].pending_interrupt, phrase
        assert order(world, "Ney") == ("PURSUE", "Mack"), phrase

    @pytest.mark.parametrize("raw,clean", [
        ("attack, what are you waiting for?", "attack"),
        ("hold, do as I say", "hold"),
        ("do what I say: attack", "attack"),
        ("Ney, do as I say and attack Mack", "Ney, attack Mack"),
        ("Ney, attack Mack. That's an order.", "Ney, attack Mack"),
        ("what are you waiting for?", "what are you waiting for?"),
        ("what are you waiting for, Ney?", "what are you waiting for, Ney?"),
    ])
    def test_the_rule_reads_the_clause(self, raw, clean):
        assert CG.strip_emphasis(raw) == clean

    def test_the_lever_down_reproduces_the_question(self, interrupt, monkeypatch):
        monkeypatch.setattr(CG, "AN_EMPHATIC_ORDER_IS_AN_ORDER", False)
        client, world = interrupt
        before = battles(world)
        data = post(client, "attack, what are you waiting for")
        assert battles(world) == before
        assert str(data.get("message") or "").startswith("A question is not an answer")
