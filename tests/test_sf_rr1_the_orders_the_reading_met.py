"""Score Finish Step 9, SF-RR1 "the orders the reading met" — part (i): the
final reading's one P1 and the premise it met on the HOLD (October 5, 2026).

Reproduced at `POST /command` on a fresh 1805 boot (Lannes placed at Rhineland)
before a line was written:

    `Lannes, march home to Franche-Comte`
        -> "Lannes begins march to Lorraine … (Our maps read Lorraine as the
           province nearest your order, Sire.)"            (SFR-D11, P1)
    `Lannes, march back to Franche-Comte`              -> Lorraine
    `Lannes, march to Franche-Comte`                   -> Franche-Comte
    `Ney, if Mack's still in Swabia, attack him`
        -> "Sire, that is a contingency, not an order"      (SFR-H1)

Every rule's lever down reproduces its row; the wire pins drive the real
`POST /command`.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import backend.ai.condition_grammar as CG
import backend.ai.strategic_parser as SP
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


@pytest.fixture
def lannes_at_rhineland(shipped):
    client, world = shipped
    world.marshals["Lannes"].location = "Rhineland"
    return client, world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


def order_target(world, name):
    order = getattr(world.marshals[name], "strategic_order", None)
    return getattr(order, "target", None) if order else None


def battles(world):
    return len([e for e in world.event_log if e.get("type") == "battle"])


# ═════════════ SFR-D11: a named province outranks "home" ═════════════════════

class TestTheNamedProvinceOutranksHome:

    @pytest.mark.parametrize("line", [
        "Lannes, march home to Franche-Comte",
        "Lannes, march back to Franche-Comte",
        "Lannes, march home toward Franche-Comte",
    ])
    def test_the_named_province_is_the_destination(self, lannes_at_rhineland, line):
        client, world = lannes_at_rhineland
        r = post(client, line)
        assert order_target(world, "Lannes") == "Franche-Comte", r.get("message")
        assert "nearest your order" not in str(r.get("message") or "")

    def test_an_accent_does_not_hide_the_province(self, lannes_at_rhineland):
        client, world = lannes_at_rhineland
        post(client, "Lannes, march home to Franche-Comté")
        assert order_target(world, "Lannes") == "Franche-Comte"

    def test_march_home_alone_still_goes_home(self, lannes_at_rhineland):
        client, world = lannes_at_rhineland
        post(client, "Lannes, march home")
        assert order_target(world, "Lannes") == "Lorraine"

    def test_home_to_a_purpose_still_goes_home(self, lannes_at_rhineland):
        """Only a province on the map takes the order: "to rest the men" is a
        purpose, and the march still goes one step toward the capital."""
        client, world = lannes_at_rhineland
        post(client, "Lannes, march home to rest the men")
        assert order_target(world, "Lannes") == "Lorraine"

    def test_the_reader_is_pure_and_strict(self, shipped):
        _client, world = shipped
        read = SP.province_named_after_relative
        assert read("march home to franche-comte", world) == "Franche-Comte"
        assert read("march back towards franche-comté and then fortify", world) == "Franche-Comte"
        assert read("march home to rest the men", world) is None
        assert read("march home", world) is None
        assert read("march home to franche-comte", None) is None

    def test_lever_down_restores_the_reading_of_home(self, lannes_at_rhineland, monkeypatch):
        monkeypatch.setattr(SP, "A_NAMED_PLACE_OUTRANKS_HOME", False)
        client, world = lannes_at_rhineland
        r = post(client, "Lannes, march home to Franche-Comte")
        assert order_target(world, "Lannes") == "Lorraine"
        assert "nearest your order" in str(r.get("message") or "")


# ═════════════ SFR-H1: a contracted premise is read ══════════════════════════

class TestAContractedPremiseIsRead:

    @pytest.mark.parametrize("line", [
        "Ney, if Mack's still in Swabia, attack him",
        "Ney, if Mack’s still in Swabia, attack him",
        "Ney, if Mack is still in Swabia, attack him",
    ])
    def test_the_premise_splits(self, line):
        rest, premise = CG.split_premise(line, ["Mack", "ArchdukeCharles"], ["Swabia", "Bohemia"])
        assert rest == "Ney, attack Mack"
        assert premise and premise["marshal"] == "Mack" and premise["region"] == "Swabia"

    def test_a_two_word_foe_still_reads(self):
        rest, premise = CG.split_premise(
            "Davout, if Archduke Charles is in Bohemia, attack him",
            ["Mack", "ArchdukeCharles"], ["Swabia", "Bohemia"])
        assert premise and premise["marshal"] == "ArchdukeCharles"
        assert rest == "Davout, attack ArchdukeCharles"

    def test_lever_down_restores_the_refusal_shape(self, monkeypatch):
        monkeypatch.setattr(CG, "A_CONTRACTED_PREMISE_IS_READ", False)
        line = "Ney, if Mack's still in Swabia, attack him"
        assert CG.split_premise(line, ["Mack"], ["Swabia"]) == (line, None)

    def test_the_order_runs_at_the_wire(self, shipped):
        client, world = shipped
        before = battles(world)
        r = post(client, "Ney, if Mack's still in Swabia, attack him")
        msg = str(r.get("message") or "")
        assert "contingency" not in msg
        assert battles(world) > before or "MUSTER" in msg, msg[:200]

    def test_lever_down_refuses_at_the_wire(self, shipped, monkeypatch):
        monkeypatch.setattr(CG, "A_CONTRACTED_PREMISE_IS_READ", False)
        client, world = shipped
        r = post(client, "Ney, if Mack's still in Swabia, attack him")
        assert "contingency" in str(r.get("message") or "")
