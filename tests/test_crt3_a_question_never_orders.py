"""CRT-3 — "A question never orders" (the CR-6 triage, slice 3; build
contract = `docs/COMMAND_ROBUSTNESS_SPEC.md` §12.3; rows CX-X1, L2-7b,
CXR1-2, CXR1-4, CXR1-5, CXR1-N2, CXR1-N3 in `docs/BUG_FIXES.md`; landed as
Score Mandate Chunk 3 SR-3a, September 26, 2026).

Reproduced on this HEAD at the real `POST /command` before a line was
written, on a fresh shipped 1805 boot per sentence:

    `why not declare war on Prussia`     "Choose your war purpose against
                                         Prussia." — the chooser staged
                                         against a court at PEACE (CX-X1)
    `why not downgrade relations with Spain`  Alliance → Defensive Alliance,
                                         1 DP spent, no confirm
    `should we court Bavaria?`           a courting mission staged, "?" and all
    `can Ney attack Mack, Berthier`      a muster and a battle (CXR1-2)
    `perhaps build ships`                400 gold, a keel laid (CXR1-4)
    `hmm why not defend`                 the whole army defends (CXR1-5)
    `Ney why not attack Mack`            a battle (CXR1-N2)
    `hmm, why not defend`                "There is no 'hmm' in the order of
                                         battle" (CXR1-N3)
    `can Bavaria attack Mack`            a muster and a battle (L2-7b)

Six rules, each behind its own lever whose down arm reproduces the row:
the Cabinet's parser reads the SHARED question verdict (CX-X1); the comma
tail stands the subject arms down only when it OPENS with an order verb
(CXR1-2); a hedge is a question (CXR1-4); a leading run of up to three
non-order words hides no deliberative question (CXR1-5, CXR1-N2); the
interjections are never an address (CXR1-N3); a court is a subject (L2-7b).
Every wire pin reads the WORLD — the diplomatic states, the points, every
marshal's ground and strength, the dialogue slot — never only the message.
"""

import pytest
from fastapi.testclient import TestClient

import backend.ai.clause_guards as CG
import backend.ai.llm_client as LC
import backend.main as M
from backend.commands.parser import CommandParser


# ═══════════════════════════════════════════════════════════════════════
# The board
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture
def shipped(monkeypatch):
    """A fresh SHIPPED 1805 world at all three seams with a mock parser (the
    CRT-1 idiom). The suite pins `SOVEREIGN_SCENARIO=none`; these rows need
    Ney at Rhineland, Mack at Swabia and Prussia at peace with France."""
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False, "a probe must never pay for a parse"
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


def snapshot(world):
    """Everything an order can move: the purse, the points, every marshal's
    ground / strength / order / stance, the dialogue slot, three pairs."""
    out = {
        "ap": int(world.actions_remaining),
        "admin": int(getattr(world, "admin_actions_remaining", 0)),
        "gold": int(world.gold),
        "dp": int(world.diplomatic_points),
        "fr_pr": world.get_diplomatic_state("France", "Prussia"),
        "fr_sp": world.get_diplomatic_state("France", "Spain"),
        "fr_ba": world.get_diplomatic_state("France", "Bavaria"),
        "dialogue": (world.pending_diplomatic_dialogue or {}).get("type"),
        "mission": bool(getattr(world, "active_diplomatic_mission", None)),
        "fleets": repr(getattr(world, "fleets", None)),
    }
    for m in world.marshals.values():
        out["m:" + m.name] = (m.location, int(m.strength),
                              getattr(m, "strategic_order", None) is not None,
                              str(getattr(m, "stance", "")),
                              bool(getattr(m, "fortified", False)))
    return out


ADVISORY_DIALOGUES = (None, "advisory", "diplomatic_advisory", "feasibility",
                      "diplomatic_feasibility", "command_clarification")


def nothing_moved(before, after, *, ignore=()):
    diff = {k: (before.get(k), after.get(k))
            for k in before if k not in ignore and before.get(k) != after.get(k)}
    assert not diff, diff


def only_the_advisory_opened(before, after):
    """A question may open Talleyrand's ADVISORY conversation (a
    LOCAL_PLANNING dialogue) or a clarification — never the war-purpose
    chooser, a mission confirm or a proposal. Everything else is unmoved."""
    nothing_moved(before, after, ignore=("dialogue",))
    assert after["dialogue"] in ADVISORY_DIALOGUES, after["dialogue"]


DESK_OPENINGS = (
    "Were you to give the order",          # the desk's what-if (the muster)
    "Berthier sets down his pen",          # the router's shrug
    "I cannot answer that",
    "War score, Sire",                     # the desk's board answers
    "The treasury holds",
    "Yes, Sire", "No, Sire", "No corps of ours",
)


def is_a_question_answer(data):
    """The reply a question gets on the wire: Talleyrand's ADVISORY
    conversation (`diplomatic_dialogue.type == "advisory"`, or the
    feasibility desk), Berthier's desk or router (a known opening), or a
    refusal — never a battle, a march, an event or a charge. The `/command`
    response carries no `command` block on these roads, so the shape is read
    off the dialogue and the message."""
    dialogue = data.get("diplomatic_dialogue") or {}
    if str(dialogue.get("type") or "") in ("advisory", "feasibility",
                                            "diplomatic_advisory",
                                            "diplomatic_feasibility"):
        return True
    if data.get("battle_report") or data.get("battle_diorama") \
            or data.get("muster_preview") or data.get("events"):
        return False
    message = str(data.get("message") or "")
    if message.startswith(DESK_OPENINGS):
        return True
    if data.get("clarification_kind"):
        return True
    return data.get("success") is False


def _subjects(world):
    return LC._question_subjects(M.get_llm_game_state())


# ═══════════════════════════════════════════════════════════════════════
# CX-X1 — the Cabinet's parser reads the shared question verdict
# ═══════════════════════════════════════════════════════════════════════

CABINET_QUESTIONS = [
    "why not declare war on Prussia",
    "what if we declare war on Prussia",
    "how about we declare war on Prussia",
    "why not downgrade relations with Spain",
    "how about we downgrade relations with Bavaria",
    "why not cool relations with Spain",
    "should we court Bavaria?",
    "should we court Prussia?",
    "Talleyrand, should we declare war on Prussia",
]


class TestACourtsQuestionReachesTheAdvisory:
    @pytest.mark.parametrize("utterance", CABINET_QUESTIONS)
    def test_the_states_and_the_points_do_not_move(self, shipped, utterance):
        client, world = shipped
        before = snapshot(world)
        data = post(client, utterance)
        only_the_advisory_opened(before, snapshot(world))
        assert is_a_question_answer(data), (utterance, data.get("message"))
        assert (world.pending_diplomatic_dialogue or {}).get("type") != \
            "war_purpose_selection"

    def test_a_wh_question_about_an_act_of_state_reaches_the_advisory(self, shipped):
        """The row's own done-when: `diplomatic_advisory`, not the chooser —
        read off the parse (the `/command` response carries no `command`
        block on this road) and off the wire (Talleyrand's advisory
        conversation opens; the war-purpose chooser does not)."""
        client, world = shipped
        parsed = M.parser.parse("why not declare war on Prussia",
                                M.get_llm_game_state(), world=world)
        diplo = ((parsed.get("command") or {}).get("diplomatic_data") or {})
        assert diplo.get("action") in ("diplomatic_advisory", "diplomatic_feasibility"), diplo
        assert diplo.get("is_question") is True
        data = post(client, "why not declare war on Prussia")
        assert (data.get("diplomatic_dialogue") or {}).get("type") == "advisory", data.get("message")
        assert (world.pending_diplomatic_dialogue or {}).get("type") != "war_purpose_selection"
        assert world.get_diplomatic_state("France", "Prussia") != "WAR"

    def test_the_order_still_stages_the_chooser(self, shipped):
        client, world = shipped
        data = post(client, "Talleyrand, declare war on Prussia")
        dtype = (world.pending_diplomatic_dialogue or {}).get("type") or \
            (data.get("diplomatic_dialogue") or {}).get("type")
        assert dtype == "war_purpose_selection" or "war purpose" in str(
            data.get("message", "")).lower(), data.get("message")

    def test_the_courting_order_still_stages_the_mission(self, shipped):
        """`should we court Prussia?` asks; `Talleyrand, court Prussia` acts
        (Prussia is at PEACE and not an ally at boot — Bavaria is an ally,
        and SR-2b refuses courting an ally on either road)."""
        client, world = shipped
        asked = post(client, "should we court Prussia?")
        assert (asked.get("diplomatic_dialogue") or {}).get("type") == "advisory", \
            asked.get("message")
        assert not getattr(world, "active_diplomatic_mission", None)
        M._reset_world_state()
        ordered = post(client, "Talleyrand, court Prussia")
        assert (ordered.get("diplomatic_dialogue") or {}).get("type") != "advisory"
        # the order reaches the mission road: a running mission, a confirm
        # dialogue, or the mission's own priced sentence — never the desk
        message = str(ordered.get("message") or "").lower()
        assert (getattr(M.world, "active_diplomatic_mission", None)
                or ordered.get("diplomatic_dialogue")
                or "mission" in message or "court" in message), ordered.get("message")

    def test_the_lever_down_reproduces_the_chooser(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(LC, "THE_CABINET_READS_THE_SHARED_QUESTION", False)
        post(client, "why not declare war on Prussia")
        dtype = (world.pending_diplomatic_dialogue or {}).get("type")
        assert dtype == "war_purpose_selection", (
            "the exit's reading: a question staged the war-purpose chooser")


# ═══════════════════════════════════════════════════════════════════════
# CXR1-2 — the tail stands the subject arms down only on an order verb
# ═══════════════════════════════════════════════════════════════════════

TAIL_QUESTIONS = [
    "can Ney attack Mack, Berthier",
    "could Davout recruit, Berthier",
    "are they going to retreat, Berthier",
    "does Ney hold Rhineland, Berthier",
    "is Ney attacking Mack, Berthier",
    "can Ney attack Mack, tell me",
]


class TestTheTailStandsDownOnlyOnAnOrder:
    @pytest.mark.parametrize("utterance", TAIL_QUESTIONS)
    def test_a_vocative_tail_keeps_the_question(self, shipped, utterance):
        client, world = shipped
        before = snapshot(world)
        data = post(client, utterance)
        only_the_advisory_opened(before, snapshot(world))
        assert is_a_question_answer(data), (utterance, data.get("message"))

    @pytest.mark.parametrize("utterance", TAIL_QUESTIONS)
    def test_the_guard_itself(self, shipped, utterance):
        _, world = shipped
        assert CG.is_question(utterance, _subjects(world)) is True

    def test_the_inverted_conditional_still_stands_the_arm_down(self, shipped):
        """`Ney, should Mack advance, fortify` — the tail OPENS with an order
        verb: not a question; the condition guard's refusal (pinned by
        test_parse_negation) keeps its road."""
        _, world = shipped
        assert CG.is_question("Ney, should Mack advance, fortify",
                              _subjects(world)) is False
        assert CG.is_question("should Mack advance, fortify the line",
                              _subjects(world)) is False

    def test_the_lever_down_reproduces_the_battle_road(self, shipped, monkeypatch):
        _, world = shipped
        monkeypatch.setattr(CG, "THE_TAIL_STANDS_DOWN_ONLY_ON_AN_ORDER", False)
        assert CG.is_question("can Ney attack Mack, Berthier",
                              _subjects(world)) is False


# ═══════════════════════════════════════════════════════════════════════
# CXR1-4 — a hedge is a question
# ═══════════════════════════════════════════════════════════════════════

HEDGES = [
    "perhaps build ships",
    "maybe build a depot in Paris",
    "worth attacking Mack",
    "maybe defend",
    "possibly attack Mack",
    "perhaps we should release Holland",
    "Ney, perhaps attack Mack",
]


class TestAHedgeIsNotAnOrder:
    @pytest.mark.parametrize("utterance", HEDGES)
    def test_nothing_is_spent(self, shipped, utterance):
        client, world = shipped
        before = snapshot(world)
        data = post(client, utterance)
        only_the_advisory_opened(before, snapshot(world))
        assert is_a_question_answer(data), (utterance, data.get("message"))

    def test_time_to_is_deliberately_not_a_hedge(self, shipped):
        """`time to march on Vienna` is an order (the triage's ruling)."""
        client, world = shipped
        assert CG.is_question("time to march on Vienna", _subjects(world)) is False
        data = post(client, "Ney, time to march on Vienna")
        assert not is_a_question_answer(data) or data.get("clarification_kind"), data

    def test_a_hedge_in_the_body_is_not_a_lead(self, shipped):
        _, world = shipped
        assert CG.is_question("Ney, attack Mack, perhaps with Davout in support",
                              _subjects(world)) is False

    def test_the_lever_down_reproduces_the_keel(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(CG, "A_HEDGE_IS_NOT_AN_ORDER", False)
        assert CG.is_question("perhaps build ships", _subjects(world)) is False


# ═══════════════════════════════════════════════════════════════════════
# CXR1-5 / CXR1-N2 / CXR1-N3 — a leading run hides no question
# ═══════════════════════════════════════════════════════════════════════

LEADING_RUNS = [
    "hmm why not defend",
    "just wondering why not retreat",
    "I wonder why not retreat",
    "tell me why not retreat",
    "actually what about build ships",
    "Ney why not attack Mack",
    "Davout why not retreat",
    "Davout how about fortify",
    "hmm, why not defend",
    "uh, why not retreat",
]


class TestALeadingRunHidesNoQuestion:
    @pytest.mark.parametrize("utterance", LEADING_RUNS)
    def test_nothing_moves(self, shipped, utterance):
        client, world = shipped
        before = snapshot(world)
        data = post(client, utterance)
        only_the_advisory_opened(before, snapshot(world))
        assert is_a_question_answer(data), (utterance, data.get("message"))
        assert "in the order of battle" not in str(data.get("message", "")), (
            "CXR1-N3: the interjection claimed as an unknown officer")

    @pytest.mark.parametrize("utterance", [
        "quickly attack Mack", "Ney attack Mack", "someone attack Mack",
        "cavalry attack Mack", "tonight retreat",
    ])
    def test_the_cx7_controls_still_march(self, shipped, utterance):
        """A leading run before an ORDER is CX-7's business, unchanged."""
        _, world = shipped
        assert CG.is_question(utterance, _subjects(world)) is False

    def test_the_run_may_be_longer_than_the_row_measured(self, shipped):
        """The row measured one to three words; a cap of three let `I was
        just wondering why not retreat` (four) order a GENERAL RETREAT at the
        wire during the build. The ceiling is six; the no-order-verb
        condition is what keeps an order an order."""
        _, world = shipped
        assert CG.is_question("I was just wondering why not retreat",
                              _subjects(world)) is True
        assert CG.is_question("well then tell me why not retreat",
                              _subjects(world)) is True
        assert CG.is_question("so I have been sitting here wondering why not retreat",
                              _subjects(world)) is False  # seven words: past the ceiling
        # a run that carries an ORDER verb is never a hidden question
        assert CG.is_question("attack Mack why not", _subjects(world)) is False
        assert CG.is_question("Ney attack Mack why not press on",
                              _subjects(world)) is False

    def test_a_relative_clause_order_is_not_a_question(self, shipped):
        """The bare subject-WH leads are NOT read behind a run — the
        comma-free relative clause the row warned about stays an order."""
        _, world = shipped
        assert CG.is_question("Davout who is at Paris attack Mack",
                              _subjects(world)) is False

    def test_the_interjections_are_never_an_address(self):
        for word in ("hmm", "um", "er", "uh", "erm", "ah"):
            assert CG.never_an_address(word) is True, word
            assert CG.address_of(f"{word}, why not defend", ["Ney"]) is None

    def test_the_lever_down_reproduces_the_defend(self, shipped, monkeypatch):
        _, world = shipped
        monkeypatch.setattr(CG, "A_LEADING_RUN_HIDES_NO_QUESTION", False)
        assert CG.is_question("hmm why not defend", _subjects(world)) is False


# ═══════════════════════════════════════════════════════════════════════
# L2-7b — a court is a subject
# ═══════════════════════════════════════════════════════════════════════

COURT_SUBJECTS = [
    "can Bavaria attack Mack",
    "can Prussia retreat",
    "could Russia defend",
    "can the Prussians attack",
    "could the Austrian army retreat",
]


class TestACourtIsASubject:
    @pytest.mark.parametrize("utterance", COURT_SUBJECTS)
    def test_nothing_moves(self, shipped, utterance):
        client, world = shipped
        before = snapshot(world)
        data = post(client, utterance)
        only_the_advisory_opened(before, snapshot(world))
        assert is_a_question_answer(data), (utterance, data.get("message"))

    def test_the_roster_holds_the_courts(self, shipped):
        _, world = shipped
        subjects = {s.lower() for s in _subjects(world)}
        assert {"bavaria", "prussia", "russia", "austria"} <= subjects

    @pytest.mark.parametrize("utterance", COURT_SUBJECTS + [
        "could the Prussians attack Mack", "can the Austrians hold Vienna"])
    def test_the_guard_reads_the_court_as_the_subject(self, shipped, utterance):
        """The guard itself — the article cases are pinned HERE because at
        the wire they are refused for other reasons too (an attack on a court
        at peace is a declaration; "the Austrian army retreat" is the
        retreat NOUN), so a wire pin alone was inert on the article strip
        (the first sweep found it)."""
        _, world = shipped
        assert CG.is_question(utterance, _subjects(world)) is True

    def test_the_article_strip_is_load_bearing(self, shipped, monkeypatch):
        _, world = shipped
        subjects = _subjects(world)
        assert CG.is_question("could the Prussians attack Mack", subjects) is True
        monkeypatch.setattr(CG, "A_COURT_IS_A_SUBJECT", False)
        assert CG.is_question("could the Prussians attack Mack", subjects) is False
        assert CG.is_question("can the Austrians hold Vienna", subjects) is False

    def test_a_polite_order_to_the_addressee_still_marches(self, shipped):
        """`can you attack Mack` is the polite imperative — unchanged."""
        _, world = shipped
        assert CG.is_question("can you attack Mack", _subjects(world)) is False

    def test_the_lever_down_reproduces_the_battle(self, shipped, monkeypatch):
        _, world = shipped
        monkeypatch.setattr(CG, "A_COURT_IS_A_SUBJECT", False)
        assert CG.is_question("can Bavaria attack Mack", _subjects(world)) is False
