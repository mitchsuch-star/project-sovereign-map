"""CR-7-5 — "The third verdict": a narrow conditional grammar, kill-gated.

Build contract: `docs/audits/COMPOUND_CONDITIONAL_COMMANDS_2026_09_20.md`
§CR-7-5 (row CQ-7). Reproduced on this HEAD before a line was written
(September 22, 2026): `hold Lorraine when|if|once|as soon as Ney arrives`
were all refused with a line that blamed the ENEMY; `attack Mack if he is
not fortified` mustered and FOUGHT at 1 AP while its un-negated twin was
correctly refused (the negation was blanked first and the clause fell under
the two-word floor); `attack Mack should the enemy advance` fought (the
inversion arm was clause-initial only); `attack if, Bavaria is threatened`
measured the clause as the word "if" and read the noun after the comma as
the province.

`clause_guards.strip_condition_clauses_with_handoff` returns the third
verdict — HAND-OFF — for exactly one predicate family, `<friendly marshal>
arrives` behind `when|if|once|as soon as` (and a LEADING `until … ,`), and
FAILS CLOSED: the residue must be a HOLD, the name must be on the friendly
roster, it must be the sole condition. The four non-negotiables are pinned
below by construction: the index-preserving blank stays, the nine REFUSING
words are not widened, the two-word floor is untouched, and a refusal stays
terminal (no model is consulted).
"""

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.ai import clause_guards as guards
from backend.ai.clause_guards import (
    _REFUSING_CONDITION_WORDS,
    strip_condition_clauses,
    strip_condition_clauses_with_handoff,
)
from backend.ai.parser_eval import build_llm_game_state, build_world, evaluate_entry, load_corpus
from backend.commands.parser import CommandParser


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def run(shipped, command):
    client, _world = shipped
    return client.post("/command", json={"command": command}).json()


def parse(text):
    return M.parser.parse(text, M.get_llm_game_state(), world=M.world)


FRIENDLY = ("Ney", "Davout", "Soult", "Lannes", "Murat")

EIGHT = [
    "Davout, when Ney arrives, hold Lorraine",
    "Davout, hold Lorraine when Ney arrives",
    "Davout, if Ney arrives, hold Lorraine",
    "Davout, hold Lorraine if Ney arrives",
    "Davout, once Ney arrives, hold Lorraine",
    "Davout, hold Lorraine once Ney arrives",
    "Davout, as soon as Ney arrives, hold Lorraine",
    "Davout, hold Lorraine as soon as Marshal Ney arrives",
]


class TestEightOfEight:

    @pytest.mark.parametrize("text", EIGHT)
    def test_the_same_order_and_condition_as_until(self, shipped, text):
        reference = parse("Davout, hold Lorraine until Ney arrives")
        got = parse(text)
        assert got.get("success"), got
        assert got.get("strategic_type") == "HOLD"
        assert got["command"]["target"] == reference["command"]["target"] == "Lorraine"
        assert got.get("strategic_condition") == reference.get("strategic_condition") == {
            "until_marshal_arrives": "Ney"}

    def test_the_echo_says_the_hold_begins_now(self, shipped):
        reply = run(shipped, "Davout, when Ney arrives, hold Lorraine")
        assert reply.get("success") is True
        assert "holds NOW" in reply["message"], reply["message"]
        order = M.world.get_marshal("Davout").strategic_order
        assert order.condition.until_marshal_arrives == "Ney"

    def test_the_leading_until_form_is_handed_off_too(self, shipped):
        got = parse("Davout, until Ney arrives, hold Lorraine")
        assert got.get("strategic_type") == "HOLD"
        assert got.get("strategic_condition") == {"until_marshal_arrives": "Ney"}


class TestItFailsClosed:

    @pytest.mark.parametrize("text", [
        "Ney, when Davout arrives, attack",          # PARSE-NEG's own pinned row
        "Ney, attack Mack when Davout arrives",
        "Ney, as soon as Davout arrives, march to Swabia",
        "Ney, if Davout arrives, fall back to Lorraine",
    ])
    def test_only_a_hold_takes_the_hand_off(self, shipped, text):
        got = parse(text)
        assert got.get("success") is False, got
        assert got.get("refusal") == "conditional"

    @pytest.mark.parametrize("text", [
        "Davout, when Godot arrives, hold Lorraine",       # not on the board
        "Davout, when Mack arrives, hold Lorraine",        # the enemy
        "Davout, when Ney and Soult arrive, hold Lorraine",  # not the grammar
        "Davout, when Ney arrives with guns, hold Lorraine",
        "Davout, when Ney arrives, hold Lorraine, if Mack advances retreat",  # two conditions
    ])
    def test_anything_else_on_the_marker_refuses(self, shipped, text):
        got = parse(text)
        assert got.get("success") is False, got
        assert got.get("refusal") in ("conditional", "condition")

    def test_a_second_clause_even_an_elliptical_one_refuses(self, shipped):
        """The sole-condition guard binds where the chain's own refusal does
        not: an ELLIPTICAL second clause ("unless attacked", one word) never
        refuses on its own, so without the guard the hand-off would ride
        beside a clause the engine cannot hold."""
        got = parse("Davout, when Ney arrives, hold Lorraine unless attacked")
        assert got.get("success") is False, got
        assert got.get("refusal") == "conditional"
        verdict = strip_condition_clauses_with_handoff(
            "Davout, when Ney arrives, hold Lorraine unless attacked",
            friendly_names=FRIENDLY)
        assert verdict.handoff is None and verdict.refuse is True

    def test_a_marshal_cannot_wait_for_himself(self, shipped):
        reply = run(shipped, "Davout, hold Rhineland when Davout arrives")
        assert reply.get("success") is False
        assert "his own arrival" in reply["message"]

    def test_the_hand_off_rides_only_a_matched_order(self):
        """A refusal, a question or an unknown never carries a hand-off."""
        verdict = strip_condition_clauses_with_handoff(
            "when Ney arrives, hold Lorraine", friendly_names=FRIENDLY)
        assert verdict.handoff is not None
        verdict = strip_condition_clauses_with_handoff(
            "when Ney arrives, hold Lorraine", friendly_names=())
        assert verdict.handoff is None and verdict.refuse is True


class TestTheOrderingDefect:
    """CQ-7: the verdict is taken on the pre-negation text too."""

    def test_the_negated_twin_is_refused_exactly_like_its_twin(self, shipped):
        _client, world = shipped
        ap = world.actions_remaining
        negated = run(shipped, "Ney, attack Mack if he is not fortified")
        assert negated.get("success") is False, negated.get("message")
        assert not negated.get("battle_report")
        assert M.world.actions_remaining == ap
        M._reset_world_state()
        plain = run(shipped, "Ney, attack Mack if he is fortified")
        assert plain.get("success") is False
        assert negated["message"].split("—")[0] == plain["message"].split("—")[0]

    def test_the_counterfactual_flips_no_corpus_row(self):
        """The memo's number, re-taken: asking the floor against the PRE-
        negation text changes the verdict on 0 corpus rows."""
        corpus = load_corpus()
        flips = []
        for entry in corpus["entries"]:
            text = entry["utterance"]
            _t, pre = strip_condition_clauses(text)
            negated, _applied = guards.strip_negated_clauses(text)
            _t2, post = strip_condition_clauses(negated)
            if pre and not post:
                flips.append(entry["id"])
        assert flips == ["cr7-negated-condition-refuses-too"], flips


class TestTheTrailingShouldAndTheCommaLeak:

    @pytest.mark.parametrize("text", [
        "Ney, attack Mack should the enemy advance",
        "Ney, attack Mack should Mack advance",
        "Ney, fortify should his corps appear",
    ])
    def test_a_trailing_inversion_refuses(self, shipped, text):
        got = parse(text)
        assert got.get("success") is False and got.get("refusal") == "conditional", got

    def test_a_plain_modal_still_orders(self, shipped):
        got = parse("Ney, you should attack Mack")
        assert got.get("success") and got["command"]["action"] == "attack"

    def test_no_province_is_conjured_by_the_comma_leak(self, shipped):
        _client, world = shipped
        reply = run(shipped, "Ney, attack if, Swabia is threatened")
        assert reply.get("success") is False
        assert not reply.get("battle_report")
        assert M.world.get_marshal("Ney").location == "Rhineland"
        _text, refuse = strip_condition_clauses("Ney, attack if, Swabia is threatened")
        assert refuse is True


class TestTheNonNegotiables:

    def test_the_blank_is_index_preserving(self):
        for text in EIGHT + ["Ney, attack Mack if he is not fortified",
                             "Ney, attack if, Swabia is threatened"]:
            verdict = strip_condition_clauses_with_handoff(text, friendly_names=FRIENDLY)
            assert len(verdict.text) == len(text), text

    def test_the_nine_refusing_words_are_not_widened(self):
        assert _REFUSING_CONDITION_WORDS == (
            "as soon as", "in case", "provided that", "provided",
            "if", "unless", "when", "once", "after")

    def test_the_two_word_floor_is_untouched(self, shipped):
        assert parse("when ready then retreat")["command"]["action"] == "retreat"
        assert parse("Ney, unless attacked, hold position")["command"]["action"] == "hold"
        assert parse("Ney, retreat if outnumbered")["command"]["action"] == "retreat"

    def test_a_refusal_stays_terminal(self, shipped):
        """No model is consulted for a hand-off OR a refusal (GR6)."""
        from backend.ai.llm_client import LLMClient
        client = M.parser.llm
        refusal = client.fast_parse("Ney, when Davout arrives, attack", M.get_llm_game_state())
        assert refusal.refusal == "conditional"
        assert LLMClient._should_fallback_to_llm(client, refusal, M.get_llm_game_state()) is False

    def test_the_two_tuple_face_never_hands_off(self):
        text, refuse = strip_condition_clauses("when Ney arrives, hold Lorraine")
        assert refuse is True


class TestThePinnedRefusalsDoNotFlip:
    """The seven refusals PARSE-NEG pinned, and the corpus's own
    `parseneg-*` rows on both worlds: at most 3 may flip by contract;
    ZERO do."""

    SEVEN = [
        "Ney, if Mack advances fall back to Lorraine",
        "if Mack advances, Ney should fall back to Lorraine",
        "Ney, attack if Davout supports",
        "Ney, when Davout arrives, attack",
        "Ney, move to Lorraine after Davout arrives",
        "Ney, attack Mack once Davout arrives",
        "Ney, should Mack advance, fortify",
    ]

    def test_zero_of_seven_flip(self, shipped):
        flipped = [t for t in self.SEVEN if parse(t).get("success")]
        assert flipped == []

    def test_every_parseneg_corpus_row_is_green_on_both_worlds(self):
        corpus = load_corpus()
        rows = [e for e in corpus["entries"] if e["id"].startswith("parseneg-")]
        assert len(rows) >= 20, len(rows)
        parser = CommandParser(use_real_llm=False)
        failures = {}
        for key in ("legacy", "1805"):
            world = build_world(key)
            state = build_llm_game_state(world)
            for entry in rows:
                if entry.get("world") not in ("any", key):
                    continue
                mismatches = evaluate_entry(parser, entry, key, world, state)
                if mismatches:
                    failures[(entry["id"], key)] = mismatches
        assert not failures, failures
