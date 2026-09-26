"""CRT-2 — "The name is never replaced" (the CR-6 triage, slice 2; build
contract = `docs/COMMAND_ROBUSTNESS_SPEC.md` §12.3; rows CQ-17, CQ-29, CQ-30
in `docs/BUG_FIXES.md`). CQ-30 landed as Score Mandate Chunk 3 SR-3a
(September 26, 2026); CQ-17 and CQ-29 land as SR-3b in this file.

CQ-30, reproduced on this HEAD at the real `POST /command` before a line was
written: `Ney, attack Archduke Charls` and `Ney, attack Kutusof` each
answered "Your words named no foe our maps know, Sire — Ney marches on Mack
at Swabia, the nearest in sight" and FOUGHT MACK — an action point, a battle,
the Butcher's Bill — while the exact name refused honestly and `Kutuzof`,
`Kutusov`, `Buxhowdn` asked. A one-letter slip on a FOGGED foe's name was
read as a DESCRIPTION (ESP-EV-4's disclose-and-proceed, right for "the
weakest enemy"), so the player named Charles and the game fought Mack.

The rule: a target run that is a NEAR MISS of any enemy on the roster —
matched omnisciently, answered fog-honestly — takes the ASK arm, naming no
hidden man and no hidden province; every description the ESP-EV-4 pins cover
still discloses and proceeds. Lever `combat_executor.A_NEAR_MISS_ASKS`.
"""

import pytest
from fastapi.testclient import TestClient

import backend.commands.combat_executor as CE
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


def strengths(world):
    return {m.name: (m.location, int(m.strength)) for m in world.marshals.values()}


NEAR_MISSES = ["Ney, attack Archduke Charls", "Ney, attack Kutusof",
               "Ney, attack Kutuzof", "Ney, attack Buxhowdn"]


class TestANearMissOfARosterNameAsks:
    @pytest.mark.parametrize("utterance", NEAR_MISSES)
    def test_nothing_is_fought_and_the_question_is_staged(self, shipped, utterance):
        client, world = shipped
        before, ap = strengths(world), int(world.actions_remaining)
        data = post(client, utterance)
        assert strengths(world) == before, data.get("message")
        assert int(world.actions_remaining) == ap
        assert not data.get("battle_report") and not data.get("battle_diorama")
        assert data.get("clarification_kind") == "attack_target" or \
            data.get("success") is False, data.get("message")
        message = str(data.get("message") or "")
        assert "marches on Mack" not in message, "disclose-and-proceed fired"

    @pytest.mark.parametrize("utterance", NEAR_MISSES)
    def test_the_answer_names_no_hidden_man_and_no_hidden_province(self, shipped, utterance):
        """Charles stands at Carniola and Kutuzov at Podolia, both in fog.
        Either ASK is fog-honest: the near-miss arm's "No foe of that name is
        in sight" (the two slips that used to FIGHT), or the substitution
        arm's "will not charge at a guess" (`Kutuzof` / `Buxhowdn`, which the
        parser's own fuzzy pass already caught before this slice — the row
        measured them asking)."""
        client, world = shipped
        data = post(client, utterance)
        message = str(data.get("message") or "")
        for hidden in ("Carniola", "Podolia", "Charles", "Kutuzov", "Buxhowden"):
            assert hidden not in message, (hidden, message)
        assert "whom shall ney engage" in message.lower() or \
            "whom shall he engage" in message.lower(), message

    @pytest.mark.parametrize("utterance", ["Ney, attack Archduke Charls",
                                           "Ney, attack Kutusof"])
    def test_the_two_that_fought_take_the_near_miss_arm(self, shipped, utterance):
        client, world = shipped
        data = post(client, utterance)
        message = str(data.get("message") or "")
        assert message.startswith("No foe of that name is in sight"), message
        assert data.get("clarification_kind") == "attack_target", data.get("clarification_kind")

    def test_a_description_still_discloses_and_proceeds(self, shipped):
        """ESP-EV-4's founding case is untouched: a delegation with no name
        in it fights the nearest foe and SAYS so."""
        client, world = shipped
        ap = int(world.actions_remaining)
        data = post(client, "Ney, attack the weakest enemy")
        moved = (int(world.actions_remaining) < ap
                 or data.get("battle_report") or data.get("muster_preview")
                 or "Mack" in str(data.get("message") or ""))
        assert moved, data.get("message")

    def test_the_exact_fogged_name_still_says_no_intelligence(self, shipped):
        client, world = shipped
        ap = int(world.actions_remaining)
        data = post(client, "Ney, attack Kutuzov")
        assert "no intelligence" in str(data.get("message") or "").lower(), data.get("message")
        assert int(world.actions_remaining) == ap

    def test_the_lever_down_reproduces_the_battle_against_mack(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(CE, "A_NEAR_MISS_ASKS", False)
        data = post(client, "Ney, attack Archduke Charls")
        assert "marches on Mack" in str(data.get("message") or "") or \
            data.get("battle_report") or data.get("muster_preview"), data.get("message")
