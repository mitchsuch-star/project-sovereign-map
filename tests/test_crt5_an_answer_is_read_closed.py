"""CRT-5 "An answer is read closed" (Score Mandate SR-2e part (ii),
September 26, 2026; `COMMAND_ROBUSTNESS_SPEC.md` §12.3 row 5, IQ7-X7).

Reproduced at `POST /command` on the shipped 1805 boot before a line was
written (a read-only recon, 19 deferral and condition tails × 20 dialogue
families):

    Portugal's letter current:  `accept the offer later`, `accept it next
                                turn`, `yes, later`, `if we accept`, `accept
                                the offer, but not now`, `we will accept
                                tomorrow`, `accept once Austria agrees` —
                                each SIGNED PEACE → OPEN_BORDERS
    an ultimatum up:            `yield later` ceded the demanded 500 gold
    a staged settlement:        `ratify it later` RATIFIED it (two pairs)
    a vassal rebellion:         `garrison next turn` spent 2 actions
    `accept prussia` (S1):      signed PORTUGAL's letter
    an objection (S4):          `trust him tomorrow` carried out the
                                alternative and fought a battle

The rule: a typed answer is the dialogue's own answer phrase plus plain
words (a closed allowlist); anything else fails CLOSED — the line claims
nothing and executes nothing. Every rule sits behind a lever whose down arm
reproduces the row.
"""

import contextlib
import io

import pytest
from fastapi.testclient import TestClient

import backend.commands.dialogue_routing as DR
import backend.main as M
from backend.commands.parser import CommandParser


LETTER = {"type": "incoming_proposal", "target_nation": "Portugal",
          "context": {"proposal_type": "open_borders"},
          "options": [{"label": "Accept", "action": "accept_ai_proposal"},
                      {"label": "Reject", "action": "reject_ai_proposal"},
                      {"label": "Counter-offer", "action": "counter_ai_proposal"}]}

ULTIMATUM = {"type": "incoming_ultimatum", "target_nation": "Prussia",
             "options": [{"label": "Yield", "action": "accept_ai_ultimatum"},
                         {"label": "Defy", "action": "reject_ai_ultimatum"}]}

SETTLEMENT = {"type": "settlement_confirm",
              "options": [{"label": "Ratify", "action": "confirm_settlement"},
                          {"label": "Back Out", "action": "back_out_settlement"}]}

DEFERRALS = [
    "accept the offer later", "accept it next turn", "yes, later",
    "if we accept", "accept the offer, but not now", "accept, but later",
    "we will accept tomorrow", "accept once Austria agrees",
    "accept the offer when the war ends", "not yet, accept later",
    "accept eventually", "accept soon", "accept until spring",
    "accept unless they object", "yes - tomorrow", "accept prussia",
    "accept, they have earned it", "accept and march on Vienna",
]

PLAIN = [
    ("accept", "accept"), ("Accept", "accept"), ("I accept", "accept"),
    ("we accept the offer", "accept"), ("we shall accept the offer", "accept"),
    ("I would accept", "accept"), ("yes", "yes"), ("accept the terms", "accept"),
    ("accept Portugal's offer", "accept"), ("accept the offer from Portugal", "accept"),
    ("accept the offer, Talleyrand", "accept"), ("accept it at once", "accept"),
    ("reject", "reject"), ("decline the offer", "decline"),
    ("counter-offer", "counter-offer"),
]


class TestTheLetterIsAnsweredPlainly:

    @pytest.mark.parametrize("line", DEFERRALS)
    def test_a_deferral_or_a_condition_claims_nothing(self, line):
        assert DR.match_dialogue_answer(LETTER, line.lower()) is None, line

    @pytest.mark.parametrize("line,token", PLAIN)
    def test_a_plain_answer_is_claimed(self, line, token):
        assert DR.match_dialogue_answer(LETTER, line.lower()) == token, line

    def test_two_answers_claim_nothing(self):
        assert DR.match_dialogue_answer(LETTER, "accept or reject") is None
        # …and with nothing but plain words between them (the sweep's case)
        assert DR.match_dialogue_answer(LETTER, "accept, reject") is None
        assert DR.match_dialogue_answer(LETTER, "yes, reject the offer") is None

    def test_an_inverted_auxiliary_claims_nothing(self):
        assert DR.match_dialogue_answer(LETTER, "shall we accept") is None
        assert DR.match_dialogue_answer(LETTER, "then shall we accept it") is None
        # a TAG question is a question too (CRT-3's guard reads the inverted
        # modal anywhere in the line)
        assert DR.match_dialogue_answer(LETTER, "accept it, shall we") is None
        assert DR.match_dialogue_answer(LETTER, "accept it, will we") is None

    def test_the_statement_order_rule_stands_without_the_question_guard(self, monkeypatch):
        """The question guard is sited first and catches every inverted
        auxiliary, so the closed grammar's own statement-order rule is
        DEFENCE IN DEPTH (measured INERT with the guard up). With the guard
        lowered it alone refuses the inversion — and admits the statement."""
        monkeypatch.setattr(DR, "A_QUESTION_NEVER_ANSWERS", False)
        for line in ("shall we accept", "will we accept the offer",
                     "accept it, shall we", "do we accept"):
            assert DR.match_dialogue_answer(LETTER, line) is None, line
        for line in ("we shall accept", "we do accept", "do accept"):
            assert DR.match_dialogue_answer(LETTER, line) == "accept", line

    def test_a_negation_is_no_answer_word(self):
        """FA-N2 through the allowlist: `not`, `never`, `no`, `without` are
        admitted only inside a self-negating answer phrase."""
        for line in ("not accept", "never accept", "accept, no", "do not accept",
                     "accept without delay"):
            assert DR.match_dialogue_answer(LETTER, line) is None, line

    def test_a_negation_made_of_answer_words_is_no_answer(self):
        """FA-N2's marker check is NOT redundant with the allowlist: `decline
        to reject it` is two reject-words and means accept, and every word in
        it is admitted. Only the marker (`decline to`) sees the negation."""
        for line in ("decline to reject it", "refuse to decline the offer",
                     "decline to refuse it"):
            assert DR.match_dialogue_answer(LETTER, line) is None, line

    @pytest.mark.parametrize("line", DEFERRALS[:5])
    def test_the_lever_down_signs(self, line, monkeypatch):
        monkeypatch.setattr(DR, "AN_ANSWER_IS_READ_CLOSED", False)
        assert DR.match_dialogue_answer(LETTER, line.lower()) is not None, line


class TestEveryFamilyIsReadClosed:

    @pytest.mark.parametrize("line", ["yield later", "we will yield tomorrow",
                                      "yield, but not now", "if we yield",
                                      "yes, later", "defy them next turn"])
    def test_an_ultimatum(self, line):
        assert DR.match_dialogue_answer(ULTIMATUM, line) is None, line

    def test_an_ultimatum_plainly(self):
        assert DR.match_dialogue_answer(ULTIMATUM, "yield") == "yield"
        assert DR.match_dialogue_answer(ULTIMATUM, "defy them") == "defy"

    @pytest.mark.parametrize("line", ["ratify it later", "yes, but not now",
                                      "confirm tomorrow", "ratify once they sign"])
    def test_a_settlement(self, line):
        assert DR.match_dialogue_answer(SETTLEMENT, line) is None, line

    def test_a_settlement_plainly(self):
        assert DR.match_dialogue_answer(SETTLEMENT, "ratify") == "ratify"
        assert DR.match_dialogue_answer(SETTLEMENT, "ratify it") == "ratify"

    def test_a_counter_offer_answers_to_its_head_word(self):
        """S2: `accept` could not answer `counter_offer_response` (no keyword
        mapped onto `accept_counter_offer`); the label's head word does."""
        counter = {"type": "counter_offer_response", "target_nation": "Austria",
                   "options": [{"label": "Accept counter-offer",
                                "action": "accept_counter_offer"},
                               {"label": "Reject counter-offer",
                                "action": "reject_counter_offer"}]}
        assert DR.match_dialogue_answer(counter, "accept") is not None
        assert DR.match_dialogue_answer(counter, "accept later") is None

    def test_the_client_petition_keeps_its_own_grammar(self):
        """A client petition is still read by `petition_plain_answer`."""
        assert DR.AN_ANSWER_IS_READ_CLOSED is True
        assert DR.A_PETITION_IS_ANSWERED_PLAINLY is True


# ═══════════════════════════════════════════════════════════════════════════
# At the wire
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False, "a probe must never pay for a parse"
    return TestClient(M.app), M.world


def post(client, command):
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post("/command", json={"command": command}).json()


def _deliver_portugal(world):
    from backend.game_logic.ai_diplomacy import deliver_ai_proposal
    world.dialogue_manager._queue = []
    world.dialogue_manager._current = None
    with contextlib.redirect_stdout(io.StringIO()):
        return deliver_ai_proposal({
            "source": "Portugal", "recipient": "France",
            "proposal_type": "open_borders", "priority": 1,
            "terms": {"type": "open_borders", "proposer_nation": "Portugal",
                      "target_nation": "France"},
            "talleyrand_assessment": "", "decision_reason": "probe",
            "turn_generated": 1}, world)


def _deliver_ultimatum(world):
    from backend.game_logic.ai_diplomacy import deliver_ai_proposal
    world.dialogue_manager._queue = []
    world.dialogue_manager._current = None
    with contextlib.redirect_stdout(io.StringIO()):
        return deliver_ai_proposal({
            "source": "Prussia", "recipient": "France",
            "proposal_type": "ultimatum", "priority": 1,
            "terms": {"type": "ultimatum", "proposer_nation": "Prussia",
                      "target_nation": "France",
                      "demands": [{"type": "gold_lump", "value": 500}],
                      "sweeteners": [], "clauses": ["ultimatum"]},
            "talleyrand_assessment": "", "decision_reason": "agenda_pursuit",
            "turn_generated": 1}, world)


class TestAtTheWire:

    @pytest.mark.parametrize("line", ["accept the offer later", "yes, later",
                                      "if we accept", "accept prussia",
                                      "we will accept tomorrow"])
    def test_a_deferred_answer_signs_nothing(self, shipped, line):
        client, world = shipped
        letter = _deliver_portugal(world)
        if letter is None:
            pytest.skip("the delivery road refused the staged letter")
        before = world.get_diplomatic_state("France", "Portugal")
        post(client, line)
        assert world.get_diplomatic_state("France", "Portugal") == before, line
        assert world.pending_diplomatic_dialogue is not None, line

    def test_a_plain_answer_signs(self, shipped):
        client, world = shipped
        letter = _deliver_portugal(world)
        if letter is None:
            pytest.skip("the delivery road refused the staged letter")
        before = world.get_diplomatic_state("France", "Portugal")
        post(client, "accept")
        assert world.get_diplomatic_state("France", "Portugal") != before

    def test_the_line_is_reprompted_in_place(self, shipped):
        client, world = shipped
        letter = _deliver_portugal(world)
        if letter is None:
            pytest.skip("the delivery road refused the staged letter")
        data = post(client, "accept, they have earned it")
        assert "not an answer" in str(data.get("message") or ""), data.get("message")
        assert world.pending_diplomatic_dialogue is not None

    def test_an_ultimatum_is_not_yielded_later(self, shipped):
        client, world = shipped
        ultimatum = _deliver_ultimatum(world)
        if ultimatum is None:
            pytest.skip("the delivery road refused the staged ultimatum")
        post(client, "status")
        gold = (world.nation_gold.get("France"), world.nation_gold.get("Prussia"))
        post(client, "yield later")
        assert (world.nation_gold.get("France"),
                world.nation_gold.get("Prussia")) == gold

    def test_the_button_road_is_read_closed(self, shipped):
        client, world = shipped
        letter = _deliver_portugal(world)
        if letter is None:
            pytest.skip("the delivery road refused the staged letter")
        before = world.get_diplomatic_state("France", "Portugal")
        with contextlib.redirect_stdout(io.StringIO()):
            data = client.post("/respond_to_diplomatic_dialogue",
                               json={"choice": "accept it next turn"}).json()
        assert world.get_diplomatic_state("France", "Portugal") == before
        assert not data.get("success")
        with contextlib.redirect_stdout(io.StringIO()):
            client.post("/respond_to_diplomatic_dialogue",
                        json={"choice": "accept_ai_proposal"}).json()
        assert world.get_diplomatic_state("France", "Portugal") != before


class TestTheObjectionAnswerIsPlain:
    """S4: `trust him tomorrow` carried out Ney's alternative and fought."""

    @pytest.mark.parametrize("line,plain", [
        ("I trust him", True), ("insist on it", True), ("trust Davout", True),
        ("insist, as ordered", True), ("compromise", True),
        ("trust his judgment", True),
        ("trust him tomorrow", False), ("insist once Mack moves", False),
        ("trust him, but later", False), ("insist if he agrees", False)])
    def test_the_answer_word_stands_with_plain_words(self, line, plain):
        answer = next(w for w in ("trust", "insist", "compromise") if w in line.lower())
        assert DR.objection_answer_is_plain(
            line.lower(), answer, ["Davout", "Ney", "Mack"]) is plain, line

    def test_the_lever_down_takes_any_line(self, monkeypatch):
        monkeypatch.setattr(DR, "AN_OBJECTION_ANSWER_IS_READ_CLOSED", False)
        assert DR.objection_answer_is_plain("trust him tomorrow", "trust") is True


# ═══════════════════════════════════════════════════════════════════════════
# What the families taught the grammar (each a pinned positive kept)
# ═══════════════════════════════════════════════════════════════════════════

PICKER = {"type": "proposal_options", "target_nation": "Prussia",
          "options": [{"label": "Prussia", "action": "expand_options",
                       "terms": {"target_nation": "Prussia"}},
                      {"label": "Austria", "action": "expand_options",
                       "terms": {"target_nation": "Austria"}}]}

ADVISORY = {"type": "advisory", "options": [
    {"label": "Execute", "action": "execute_suggestion"},
    {"label": "Dismiss", "action": "dismiss"}]}

PARADOX = {"type": "commitment_paradox", "target_nation": "",
           "options": [{"label": "Honor alliance with Bavaria", "action": "honor_defender"},
                       {"label": "Side with Austria", "action": "break_defender_alliance"}]}

BREAK_CONFIRM = {"type": "force_break_treaty_confirmation",
                 "target_nation": "Austria",
                 "options": [{"label": "Proceed — break the treaty",
                              "action": "force_break_treaty"},
                             {"label": "Reconsider", "action": "reconsider"}]}


class TestWhatTheFamiliesTaughtIt:

    def test_a_court_that_is_the_option_is_the_answer(self):
        """The nation picker's rows ARE court names; the dialogue's own court
        is never blanked where it is a whole label."""
        assert DR.match_dialogue_answer(PICKER, "prussia") == "prussia"
        assert DR.match_dialogue_answer(PICKER, "choose austria") == "austria"

    def test_a_dismissal_names_its_matter(self):
        assert DR.match_dialogue_answer(ADVISORY, "never mind the money") == "never mind"

    def test_a_counter_names_its_instrument(self):
        assert DR.match_dialogue_answer(LETTER, "counter with gold") is not None

    def test_another_matter_dismissed_is_no_second_answer(self):
        """IQ-7 R9's positive: when THIS dialogue offers no dismissal,
        `never mind the petition` dismisses ANOTHER matter."""
        assert DR.match_dialogue_answer(
            LETTER, "never mind the petition, accept portugal's proposal") == "accept"

    def test_the_break_treaty_confirm_answers_to_its_own_verb(self):
        """S3: `proceed` could not answer the confirm, while `proceed and
        break the treaty later` broke the treaty."""
        assert DR.match_dialogue_answer(BREAK_CONFIRM, "proceed") is not None
        assert DR.match_dialogue_answer(
            BREAK_CONFIRM, "proceed and break the treaty later") is None
        assert DR.match_dialogue_answer(BREAK_CONFIRM, "reconsider") == "reconsider"

    def test_a_court_the_label_names_is_part_of_the_answer(self, monkeypatch):
        """The families census's one loss, caught before landing: the
        commitment paradox's labels NAME the courts, and blanking `with
        Bavaria` as an addressee slot left "Honor alliance with Bavaria"
        unmatchable — its own label claimed nothing."""
        assert DR.match_dialogue_answer(
            PARADOX, "honor alliance with bavaria") == "honor alliance with bavaria"
        assert DR.match_dialogue_answer(PARADOX, "side with austria") == "side with austria"
        assert DR.match_dialogue_answer(
            PARADOX, "honor the alliance with bavaria later") is None
        monkeypatch.setattr(DR, "A_LABEL_COURT_IS_THE_ANSWER", False)
        assert DR.match_dialogue_answer(PARADOX, "honor alliance with bavaria") is None

    def test_gibberish_is_not_told_it_deferred(self):
        assert not DR.closed_line_tried_to_answer(LETTER, "xyznonsense")
        assert DR.closed_line_tried_to_answer(LETTER, "accept it later")


class TestTheRouterSeam:

    def test_an_answer_shaped_line_to_another_court_meets_the_court_guard(self, shipped):
        """A line the grammar returns None for, answer-shaped and naming
        another court, is refused by the court guard at the router seam."""
        client, world = shipped
        letter = _deliver_portugal(world)
        if letter is None:
            pytest.skip("the delivery road refused the staged letter")
        before = world.get_diplomatic_state("France", "Portugal")
        data = post(client, "if we accept prussia's offer")
        assert world.get_diplomatic_state("France", "Portugal") == before
        assert "would be delivered to" in str(data.get("message") or ""), data.get("message")

    def test_the_lever_down_keeps_the_old_router(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(DR, "AN_ANSWER_IS_READ_CLOSED", False)
        letter = _deliver_portugal(world)
        if letter is None:
            pytest.skip("the delivery road refused the staged letter")
        before = world.get_diplomatic_state("France", "Portugal")
        post(client, "accept the offer later")
        assert world.get_diplomatic_state("France", "Portugal") != before


class TestTheObjectionAtTheWire:
    """S4 at `POST /command`: with Massena's objection standing, `trust him
    tomorrow` carries out nothing; `trust him` answers."""

    @pytest.fixture
    def objecting(self, shipped, monkeypatch):
        import random
        import backend.commands.defiance as DEF
        import backend.commands.executor as EX
        monkeypatch.setattr(EX, "apply_mood_variance", lambda concern: concern)
        monkeypatch.setattr(DEF, "calculate_defiance_chance", lambda *a, **k: 0.0)
        random.seed(11)
        client, world = shipped
        data = post(client, "Massena, fortify")
        assert data.get("objection") or data.get("pending_objection"), data.get("message")
        return client, world

    def test_a_deferred_trust_carries_out_nothing(self, objecting):
        client, world = objecting
        before = int(world.actions_remaining)
        post(client, "trust him tomorrow")
        assert world.pending_objection is not None
        assert int(world.actions_remaining) == before

    def test_a_plain_trust_answers(self, objecting):
        client, world = objecting
        post(client, "I trust him")
        assert world.pending_objection is None

    def test_the_lever_down_answers_the_deferred_line(self, objecting, monkeypatch):
        client, world = objecting
        monkeypatch.setattr(DR, "AN_OBJECTION_ANSWER_IS_READ_CLOSED", False)
        post(client, "trust him tomorrow")
        assert world.pending_objection is None
