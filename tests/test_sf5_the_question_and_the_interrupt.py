"""SF5-X1 + SF5-X2 — the typed interrupt route's two guards (Score Finish
Step 5, October 3, 2026; found in passing while building VD-C — BUG_FIXES
§Score Finish Step 5).

Measured on the SHIPPED 1805 boot before the fix, with Ney standing on Mack's
province under a PURSUE order and the first-step gate's own bad-odds
interrupt pending (options: attack anyway / hold / cancel):

* SF5-X1 (P1) — a QUESTION answered the interrupt: "should we attack?",
  "should I attack anyway?", "can we attack him?" and "would it be wise to
  proceed?" each FOUGHT the battle (`_interrupt_choice_from_text` mapped the
  option word; no question guard ran on this road — CRT-3's class, one road
  over).
* SF5-X2 (P2) — the route ran AHEAD of a standing hard stop: with the war's
  purpose waiting, "attack anyway" reached the interrupt, the attack was
  refused downstream by the hard stop's diplomacy gate, and the refusal
  destroyed the interrupt AND the standing order with nothing done.

Every pin drives `POST /command` on the real board.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands.parser import CommandParser
from backend.models.marshal import StrategicOrder

REPO = Path(__file__).resolve().parents[1]
QUESTIONS = ("should we attack?", "should I attack anyway?", "can we attack him?",
             "would it be wise to proceed?")


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    world = M.world
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
    return TestClient(M.app), world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


def battles(world):
    return len([e for e in world.event_log if e.get("type") == "battle"])


class TestAQuestionNeverAnswersAnInterrupt:
    @pytest.mark.parametrize("phrase", QUESTIONS)
    def test_a_question_fights_nothing_and_restates_the_question(self, shipped, phrase):
        client, world = shipped
        before, ap = battles(world), int(world.actions_remaining)
        r = post(client, phrase)
        assert battles(world) == before
        assert int(world.actions_remaining) == ap
        ney = world.marshals["Ney"]
        assert ney.pending_interrupt and ney.strategic_order is not None
        assert r.get("success") is False
        assert r["message"].startswith("A question is not an answer, Sire — nothing was ordered.")
        assert "Ney faces poor odds against Mack." in r["message"]
        assert r["message"].endswith(
            "Ney awaits your word: Commit the Attack, Hold Position or Cancel Order.")
        # re-carried, so the client raises the popup again
        assert (r.get("pending_interrupt") or {}).get("interrupt_type") == "contact_bad_odds"

    def test_an_answer_still_answers(self, shipped):
        client, world = shipped
        before = battles(world)
        post(client, "attack anyway")
        assert battles(world) == before + 1

    def test_an_exact_option_id_still_answers(self, shipped):
        client, world = shipped
        post(client, "hold_position")
        assert world.marshals["Ney"].pending_interrupt is None

    def test_a_question_about_something_else_is_the_desks(self, shipped):
        client, world = shipped
        r = post(client, "how much gold do we have?")
        assert not r["message"].startswith("A question is not an answer")
        assert world.marshals["Ney"].pending_interrupt   # untouched

    def test_lever_down_the_question_fights(self, shipped, monkeypatch):
        """The measured defect, reproduced."""
        monkeypatch.setattr(M, "A_QUESTION_NEVER_ANSWERS_AN_INTERRUPT", False)
        client, world = shipped
        before = battles(world)
        post(client, "should we attack?")
        assert battles(world) == before + 1


class TestAHardStopOutranksAnInterrupt:
    def _with_the_war_purpose_waiting(self, client, world):
        post(client, "declare war on Prussia")
        stop = world.dialogue_manager.peek()
        assert stop["type"] == "war_purpose_selection" and world.dialogue_manager.is_hard_stop()
        return stop

    @pytest.mark.parametrize("phrase", ("attack anyway", "hold", "should we attack?"))
    def test_the_hard_stop_names_its_question_and_the_interrupt_waits(self, shipped, phrase):
        client, world = shipped
        stop = self._with_the_war_purpose_waiting(client, world)
        before = battles(world)
        r = post(client, phrase)
        assert str(r.get("message")).startswith("Our purpose in this war awaits your answer")
        assert battles(world) == before
        ney = world.marshals["Ney"]
        assert ney.pending_interrupt and ney.strategic_order.command_type == "PURSUE"
        assert world.dialogue_manager.peek() is stop

    def test_lever_down_the_refusal_destroys_the_decision(self, shipped, monkeypatch):
        """The measured defect, reproduced: the interrupt and the order gone,
        nothing done, the hard stop still on the desk."""
        monkeypatch.setattr(M, "A_HARD_STOP_OUTRANKS_AN_INTERRUPT", False)
        client, world = shipped
        self._with_the_war_purpose_waiting(client, world)
        post(client, "attack anyway")
        ney = world.marshals["Ney"]
        assert ney.pending_interrupt is None and ney.strategic_order is None


class TestTheLabelsAreThePopups:
    def test_the_restated_answers_are_the_buttons_the_player_sees(self):
        src = (REPO / "godot-client" / "project-sovereign" / "scripts"
               / "interrupt_popup.gd").read_text(encoding="utf-8")
        block = src[src.index("const OPTION_LABELS = {"):]
        block = block[:block.index("}")]
        labels = dict(re.findall(r'"([a-z_]+)":\s*"([^"]+)"', block))
        assert labels == M._INTERRUPT_OPTION_LABELS
