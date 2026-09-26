"""CRT-6 — "The retreat is a word, not always an order" — the first pins:
CX5-L5-F2 (landed as Score Mandate Chunk 3 SR-3a, September 26, 2026; the
rest of CRT-6 — CQ-33, F3…F7, N2/N4/N5 — is Chunk 3b's and lands in this
file).

Reproduced on this HEAD at the real `POST /command` on a fresh shipped 1805
boot before a line was written:

    `Lannes, cut off Mack's line of retreat`   Lannes RETREATED (Rhineland →
                                               elsewhere, 0 AP) — a proper
                                               possessive and "line of" escape
                                               `_RETREAT_NOUN_RE`
    `Davout, cover Ney's retreat`              Davout retreated
    `Ney, block that retreat`                  Ney retreated (a demonstrative)

`_RETREAT_NOUN_RE` now takes a demonstrative, a proper possessive and up to
two modifiers, and the "line / route / path / road of" bridge; the ORDER
verbs ("sound / begin / continue the retreat") still carry it out. Lever
`llm_client.THE_RETREAT_NOUN_TAKES_A_POSSESSIVE`.
"""

import pytest
from fastapi.testclient import TestClient

import backend.ai.llm_client as LC
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


THIRD_PARTY_RETREATS = [
    ("Lannes", "Lannes, cut off Mack's line of retreat"),
    ("Davout", "Davout, cover Ney's retreat"),
    ("Ney", "Ney, block that retreat"),
    ("Ney", "Ney, harass the Austrian retreat"),
    ("Lannes", "Lannes, cut the enemy's route of retreat"),
    ("Davout", "Davout, watch this retreat closely"),
]


class TestSomebodyElsesRetreatIsNotAnOrderToRetreat:
    @pytest.mark.parametrize("marshal,utterance", THIRD_PARTY_RETREATS)
    def test_the_marshal_does_not_retreat(self, shipped, marshal, utterance):
        """He stands where he was and no retreat is ordered. What the
        sentence DOES mean is the chain's business — measured at the wire,
        `Davout, cover Ney's retreat` becomes a SUPPORT of Ney (Davout holds
        his written order to march to Ney's guns, 2 AP), which is the
        honest reading; the shrug is the other honest reading."""
        client, world = shipped
        m = world.get_marshal(marshal)
        where = m.location
        data = post(client, utterance)
        assert m.location == where, (utterance, data.get("message"))
        message = str(data.get("message") or "").lower()
        assert "falling back" not in message and "retreats from" not in message, message
        assert not data.get("events") or all(
            str(e.get("type") or "") != "retreat" for e in data.get("events") or []
            if isinstance(e, dict)), data.get("events")

    @pytest.mark.parametrize("utterance", [u for _, u in THIRD_PARTY_RETREATS])
    def test_the_noun_rule_reads_it(self, utterance):
        assert LC._retreat_is_a_noun(utterance.lower()) is True

    @pytest.mark.parametrize("utterance", [
        "Ney, retreat", "Ney, fall back", "Ney, begin the retreat",
        "Ney, sound the retreat", "Ney, continue the retreat",
        "Ney, retreat to Lorraine", "Ney, withdraw",
    ])
    def test_his_own_retreat_is_still_an_order(self, utterance):
        assert LC._retreat_is_a_noun(utterance.lower()) is False

    def test_the_order_still_retreats_at_the_wire(self, shipped):
        client, world = shipped
        ney = world.get_marshal("Ney")
        where = ney.location
        data = post(client, "Ney, retreat")
        moved = ney.location != where
        objected = "object" in str(data.get("message", "")).lower()
        assert moved or objected, data.get("message")

    def test_the_lever_down_reproduces_the_retreat(self, monkeypatch):
        monkeypatch.setattr(LC, "THE_RETREAT_NOUN_TAKES_A_POSSESSIVE", False)
        assert LC._retreat_is_a_noun("lannes, cut off mack's line of retreat") is False
        assert LC._retreat_is_a_noun("davout, cover ney's retreat") is False
        # the pre-slice determiners still read as a noun with the lever down
        assert LC._retreat_is_a_noun("davout, cover the retreat") is True
