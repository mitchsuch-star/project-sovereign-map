"""L-D "The Boolean Road" (Score Mandate, approved by the user September 26,
2026 (evening); contract `docs/audits/LOCAL_PARSER_FEASIBILITY_2026_09_20.md`
§6.4 `done_when`).

Reproduced at `POST /command` on the shipped 1805 boot under LLM_MODE=mock
before a line was written — every row ASKED:

    Ney, deal with Mack          aggressive   ask
    Davout, deal with Mack       cautious     ask
    Soult, deal with Mack        literal      ask   (correct either way)
    Murat, take care of Mack     aggressive   ask
    Lannes, see to Mack          aggressive   ask
    Bernadotte, sort out Mack    cautious     ask
    Massena, handle Mack         aggressive   ask

The three-way split was gated on ONE boolean, `parse_resolved_to_action`, a
MODE gate, while `detect_delegation` computes every input the arms need
deterministically. The witness is re-keyed to the DelegationMatch
(`delegation.delegation_witness`); the incidental case — the fast parser
reading an order of its own out of the delegation's object — still asks.
"""

import contextlib
import io
import random
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.commands.delegation as D
import backend.main as M
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
)


@pytest.fixture()
def shipped():
    """`/command` on the shipped 1805 boot with the MOCK parser — a keyless
    player's road."""
    orig = (M.parser, M.world, M.game_state)
    with contextlib.redirect_stdout(io.StringIO()):
        M.parser = CommandParser(use_real_llm=False)
        M.world = WorldState.from_scenario(str(SCENARIO_PATH))
    M.game_state = {"world": M.world}
    try:
        yield TestClient(M.app), M.world
    finally:
        (M.parser, M.world, M.game_state) = orig


def post(client, line):
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post("/command", json={"command": line}).json()


# done_when 1 + 2: the seven measured rows (plus the two verbs the memo left
# untested) take the marshal's own authored arm; Soult asks.
ROWS = [
    ("Ney, deal with Mack", "Ney", "aggressive"),
    ("Davout, deal with Mack", "Davout", "cautious"),
    ("Soult, deal with Mack", "Soult", "ask"),
    ("Murat, take care of Mack", "Murat", "aggressive"),
    ("Lannes, see to Mack", "Lannes", "aggressive"),
    ("Bernadotte, sort out Mack", "Bernadotte", "cautious"),
    ("Massena, handle Mack", "Massena", "aggressive"),
    ("Ney, do something about Mack", "Ney", "aggressive"),
    ("Davout, attend to Mack", "Davout", "cautious"),
]


def _arm_taken(data, world, name):
    marshal = world.get_marshal(name)
    order = marshal.strategic_order
    if data.get("clarification_kind") == "delegation":
        return "ask"
    if (order is not None and order.command_type == "PURSUE"
            and order.target == "Mack" and order.delegation_inferred):
        return "aggressive"
    if str(data.get("message") or "").startswith(f"{name} scouts Swabia"):
        return "cautious"
    return f"unknown: {str(data.get('message'))[:120]!r}"


class TestTheSevenRowsTakeTheirOwnArm:

    @pytest.mark.parametrize("line,name,arm", ROWS)
    def test_the_marshal_acts_to_his_character(self, shipped, line, name, arm):
        client, world = shipped
        personality = str(world.get_marshal(name).personality).lower()
        assert personality == ("literal" if arm == "ask" else arm), personality
        data = post(client, line)
        assert _arm_taken(data, world, name) == arm

    @pytest.mark.parametrize("line,name,arm", ROWS)
    def test_the_lever_down_asks_every_row(self, shipped, monkeypatch, line, name, arm):
        """Lever False restores the mode gate: every keyless delegation asks."""
        monkeypatch.setattr(D, "KEYLESS_DELEGATION_READS_THE_MATCH", False)
        client, world = shipped
        data = post(client, line)
        assert data.get("clarification_kind") == "delegation"
        assert world.get_marshal(name).strategic_order is None

    def test_soult_asks_and_spends_nothing(self, shipped):
        client, world = shipped
        data = post(client, "Soult, deal with Mack")
        assert data.get("clarification_kind") == "delegation"
        assert "Soult will not presume your meaning" in data["message"]
        assert int(world.actions_remaining) == 4
        assert world.get_marshal("Soult").strategic_order is None

    def test_the_nation_phrasing_takes_the_arm_too(self, shipped):
        """PC-15-8's nation arm (`the Austrians` → Mack) is a DelegationMatch
        like any other."""
        client, world = shipped
        data = post(client, "Davout, deal with the Austrians")
        assert _arm_taken(data, world, "Davout") == "cautious"


class TestAnOrdinaryOrderIsUntouched:
    """done_when 2: `Ney, attack Mack` is byte-identical — no DelegationMatch,
    so the witness is never asked."""

    def _run(self, lever, monkeypatch):
        monkeypatch.setattr(D, "KEYLESS_DELEGATION_READS_THE_MATCH", lever)
        orig = (M.parser, M.world, M.game_state)
        with contextlib.redirect_stdout(io.StringIO()):
            M.parser = CommandParser(use_real_llm=False)
            M.world = WorldState.from_scenario(str(SCENARIO_PATH))
        M.game_state = {"world": M.world}
        try:
            random.seed(1805)
            data = post(TestClient(M.app), "Ney, attack Mack")
            ney = M.world.get_marshal("Ney")
            return (data.get("message"), data.get("success"), ney.location,
                    ney.strength, int(M.world.actions_remaining))
        finally:
            (M.parser, M.world, M.game_state) = orig

    def test_lever_up_and_down_answer_the_same(self, monkeypatch):
        assert self._run(True, monkeypatch) == self._run(False, monkeypatch)


class TestTheIncidentalCaseStillAsks:
    """done_when 3: the case guardrail (e) was written against — the fast
    parser reads an order of its own out of the delegation's object."""

    def test_the_docstrings_own_example_asks(self, shipped):
        client, world = shipped
        data = post(client, "Ney, deal with the attack on Mack")
        assert data.get("clarification_kind") == "delegation"
        assert world.get_marshal("Ney").strategic_order is None

    def test_the_witness(self):
        match = object()
        mock_attack = {"success": True, "mode": "mock", "command": {"action": "attack"}}
        live_attack = {"success": True, "mode": "anthropic", "command": {"action": "attack"}}
        failed = {"success": False, "mode": None, "command": {"action": None}}
        unknown = {"success": True, "mode": "mock", "command": {"action": "unknown"}}
        assert D.delegation_witness(mock_attack, match) is False     # incidental
        assert D.delegation_witness(live_attack, match) is True      # live, unchanged
        assert D.delegation_witness(live_attack, None) is True
        assert D.delegation_witness(failed, match) is True           # the verb IS the order
        assert D.delegation_witness(unknown, match) is True
        assert D.delegation_witness(failed, None) is False           # no match, no arm

    def test_the_predicate_itself_is_unchanged(self):
        """The fix went in at the witness, not the predicate: a mock parse is
        still never 'resolved'."""
        assert D.parse_resolved_to_action(
            {"success": True, "mode": "mock", "command": {"action": "attack"}}) is False


class TestTheGuardrailsHold:

    def test_the_bad_odds_modal_is_the_one_modal(self, shipped):
        """Objection-first single modal: Ney against a dug-in, stronger Mack
        gets the bad-odds confirm and nothing else — no objection beside it,
        and the flavor floor withheld on the modal."""
        client, world = shipped
        data = post(client, "Ney, deal with Mack")
        assert data.get("pending_interrupt"), data.get("message")
        assert not data.get("objection") and world.pending_objection is None
        floors = [f.format(marshal="Ney", target="Mack") for f in D._AGGRESSIVE_FLOORS]
        assert not any(f in data["message"] for f in floors)

    def test_the_keyless_player_hears_the_floor(self, shipped):
        """The CR-5b flavor line stays live-only: on the non-modal path a
        keyless player hears the deterministic, register-gated floor."""
        client, world = shipped
        data = post(client, "Massena, handle Mack")
        floors = [f.format(marshal="Massena", target="Mack") for f in D._AGGRESSIVE_FLOORS]
        assert any(f in data["message"] for f in floors), data["message"]

    def test_the_arm_follows_the_authored_personality(self, shipped):
        """The personality pre-flight reads the WORLD, never the parse: author
        Ney literal and the same sentence asks."""
        client, world = shipped
        world.get_marshal("Ney").personality = "literal"
        data = post(client, "Ney, deal with Mack")
        assert data.get("clarification_kind") == "delegation"

    def test_the_phase_gate_still_holds(self, shipped, monkeypatch):
        """Action-only: with the aggressive phase gate down, the arm asks."""
        monkeypatch.setattr(D, "AGGRESSIVE_ATTACK_ARM_ENABLED", False)
        client, world = shipped
        data = post(client, "Ney, deal with Mack")
        assert data.get("clarification_kind") == "delegation"
