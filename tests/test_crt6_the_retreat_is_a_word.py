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


# ═══════════════════════════════════════════════════════════════════════════
# SF-CMD-2's head (Score Finish Step 7, October 4, 2026) — CQ-33 and
# CX5-L5-F7, the two HOLD-family misreads that still executed at the Chunk 3b
# exit. Reproduced at `POST /command` on a fresh 1805 boot before a line was
# written: `Ney, move to Paris with the Guard`, `Ney, scout Swabia with the
# guard` and `Ney, fortify with the guard` each took a 2-action standing HOLD
# at Rhineland; `recruit 5000 men for the guard` asked "Which marshal shall
# hold?"; `Ney, protect the rear` and `Ney, guard the rear` MARCHED to
# Lorraine on a 2-action HOLD; `Lannes, guard the retreat` was refused
# "Region 'Retreat' not found. Did you mean 'Crete'?"; `Davout, protect our
# flank` "could not make out a destination".
# ═══════════════════════════════════════════════════════════════════════════
import backend.ai.strategic_parser as SP  # noqa: E402
import backend.commands.parser as P  # noqa: E402


@pytest.fixture
def calm(shipped, monkeypatch):
    """The shipped board with both objection rolls pinned — an aggressive
    Ney objects to a HOLD with no enemy adjacent on a roll (the strategic
    objection, Phase M) and on a promoted concern (the tactical mood roll).
    What these pins read is the ORDER the sentence is read as."""
    monkeypatch.setattr("backend.commands.executor.apply_mood_variance",
                        lambda concern: concern)
    monkeypatch.setattr("backend.commands.strategic_executor.apply_mood_variance",
                        lambda concern: concern)
    return shipped


def _order(world, name):
    o = world.get_marshal(name).strategic_order
    return (o.command_type, o.target) if o is not None else None


class TestTheGuardIsSometimesANoun:
    """CQ-33's done-when, verbatim, plus the Emperor's own sentence."""

    def test_a_march_with_the_guard_marches(self, calm):
        client, world = calm
        data = post(client, "Ney, move to Paris with the Guard")
        assert _order(world, "Ney") == ("MOVE_TO", "Paris"), data.get("message")
        assert "The Guard marches with the Emperor alone, Sire — Ney goes with his own corps." \
            in str(data.get("message") or "")

    def test_a_scout_with_the_guard_scouts_at_one_action(self, calm):
        client, world = calm
        ap = int(world.actions_remaining)
        data = post(client, "Ney, scout Swabia with the guard")
        assert int(world.actions_remaining) == ap - 1, data.get("message")
        assert world.get_marshal("Ney").strategic_order is None
        assert "scout" in str(data.get("message") or "").lower()

    def test_a_fortify_with_the_guard_is_no_hold(self, calm):
        client, world = calm
        data = post(client, "Ney, fortify with the guard")
        assert world.get_marshal("Ney").strategic_order is None, data.get("message")
        assert "Ney will hold" not in str(data.get("message") or "")

    def test_the_emperor_with_his_guard_needs_no_note(self, calm):
        client, world = calm
        data = post(client, "Napoleon, march to Paris with the Guard")
        assert _order(world, "Napoleon") == ("MOVE_TO", "Paris"), data.get("message")
        assert "The Guard marches with the Emperor alone" not in str(data.get("message") or "")

    def test_a_levy_for_the_guard_is_the_emperors(self, calm):
        client, world = calm
        data = post(client, "recruit 5000 men for the guard")
        message = str(data.get("message") or "")
        assert "Which marshal shall hold" not in message, message
        assert "Napoleon" in message, message

    def test_guard_paris_still_holds(self, calm):
        """`guard` the VERB keeps its HOLD. Ney (aggressive) objects to a HOLD
        with no enemy beside it, so his line stages the objection — on a HOLD
        of Paris, which is the reading the pin is about; a cautious Davout
        takes the order outright."""
        client, world = calm
        post(client, "Ney, guard Paris")
        staged = world.pending_strategic_objection or {}
        assert (_order(world, "Ney") == ("HOLD", "Paris")
                or (staged.get("strategic_type"), staged.get("target")) == ("HOLD", "Paris"))
        world.pending_strategic_objection = None
        post(client, "Davout, guard Paris")
        assert _order(world, "Davout") == ("HOLD", "Paris")

    def test_guard_home_waters_is_still_the_fleet(self, calm):
        client, world = calm
        data = post(client, "guard home waters")
        assert all(m.strategic_order is None for m in world.marshals.values()
                   if m.nation == world.player_nation), data.get("message")
        assert "fleet" in str(data.get("message") or "").lower()

    def test_the_rewrite_reads_the_phrase(self):
        text, note, changed = P.rewrite_guard_company(
            "Ney, move to Paris with the Imperial Guard", None, None)
        assert changed and text == "Ney, move to Paris"

    def test_the_lever_down_reproduces_the_hold(self, calm, monkeypatch):
        monkeypatch.setattr(P, "THE_GUARD_MARCHES_WITH_THE_EMPEROR", False)
        client, world = calm
        post(client, "Ney, move to Paris with the Guard")
        assert _order(world, "Ney") == ("HOLD", "Rhineland")


POSITIONS = [
    ("Ney", "Ney, protect the rear"),
    ("Ney", "Ney, guard the rear"),
    ("Lannes", "Lannes, guard the retreat"),
    ("Davout", "Davout, protect our flank"),
    ("Ney", "Ney, hold the left flank"),
]


class TestAPositionIsNotAPlace:
    """CX5-L5-F7: the army's own positions are where the marshal stands."""

    @pytest.mark.parametrize("marshal,utterance", POSITIONS)
    def test_he_holds_where_he_stands(self, calm, marshal, utterance):
        client, world = calm
        m = world.get_marshal(marshal)
        where = m.location
        data = post(client, utterance)
        assert m.location == where, (utterance, data.get("message"))
        assert _order(world, marshal) == ("HOLD", where), (utterance, data.get("message"))
        message = str(data.get("message") or "")
        assert "Marching to" not in message and "not found" not in message, message

    @pytest.mark.parametrize("utterance", ["protect the rear", "guard our flank",
                                           "hold the line", "guard the retreat"])
    def test_the_target_is_no_province(self, utterance):
        assert SP._extract_target_text(utterance, "HOLD") is None

    def test_a_province_is_still_a_target(self):
        assert SP._extract_target_text("guard paris", "HOLD") == "paris"

    def test_a_friends_flank_is_still_his(self, calm):
        client, world = calm
        post(client, "Davout, protect Ney's flank")
        assert _order(world, "Davout") == ("SUPPORT", "Ney")

    def test_the_lever_down_reproduces_the_march(self, calm, monkeypatch):
        monkeypatch.setattr(SP, "A_POSITION_IS_NOT_A_PLACE", False)
        client, world = calm
        post(client, "Ney, protect the rear")
        assert _order(world, "Ney") == ("HOLD", "Lorraine")
