"""The Aug 30, 2026 whole-systems review round.

A 14-finder / 2-refuter-per-finding fleet at committed SHA e206869 confirmed
45 defects across parsing, diplomacy, settlement, economy, combat, marshals,
naval, enemy AI, the turn loop, serialization and the Godot client. This file
pins the fixes.

Method notes worth keeping (they cost real time this round):

* Two findings named the wrong LINE for a real defect. "Free-text target scan
  binds ordinary words to enemy commanders" cited the edit-distance arm; a spy
  on `_closest_by_edit_distance` proved that arm never fired for the measured
  case — the bind was the `auto_correct` arm one rung below, whose
  `_plausible_name_typo` gate cannot separate "moor" from "Moore" (same first
  letter, one edit). VERIFY THE MECHANISM, NOT THE CITATION.

* One finding's prescribed fix would have BROKEN a deliberate contract.
  "'hold the mountain pass' parses as WAIT and the hold order dies" is two
  defects wearing one coat: the WAIT misroute (real, fixed) and the refusal
  (correct — CA8-28's negative control exists precisely so the game never
  invents a hold somewhere else and charges 2 AP for it). Routing the terrain
  noun to a generic target would have made that pin fail for the right reason.
  The refusal stands; its misleading COPY is what was fixed.
"""

import io
import os

import pytest

from backend.ai.clause_guards import strip_negated_clauses
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


SCENARIO = os.path.join(
    "godot-client", "project-sovereign", "assets", "maps", "europe_1805.json")


@pytest.fixture
def board():
    return WorldState.from_scenario(SCENARIO)


@pytest.fixture(scope="module")
def parser():
    return CommandParser()


@pytest.fixture(scope="module")
def executor():
    return CommandExecutor()


def _issue(world, parser, executor, text):
    """Parse and execute one typed command, silencing the engine's stdout."""
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        parsed = parser.parse(text, {"world": world}, world)
        if not parsed.get("success"):
            return parsed, {"success": False,
                            "message": str(parsed.get("error") or ""),
                            "refused_at_parse": True}
        result = executor.execute(dict(parsed, raw_input=text), {"world": world})
    return parsed, result


# ══════════════════════════════════════════════════════════════════════════
# [1] P1 — a QUESTION issued a real standing strategic order, at 0 AP
# ══════════════════════════════════════════════════════════════════════════


class TestAQuestionIsNotAnOrder:
    """`parser.parse`'s strategic-detection block was gated on `world` ALONE.

    So it re-read the utterance no matter what the action chain had resolved,
    and stamped is_strategic on a parse the chain had already ruled was not an
    order. The executor intercepts on is_strategic + strategic_type alone, and
    "help" is in its `free_actions`, so BOTH the 2-AP strategic pre-gate and
    the charge were skipped: measured on the 1805 boot, "Lannes, march to
    Frankfurt" cost 4->3 AP while "Lannes, can you march to Frankfurt?"
    produced the identical standing order for free.
    """

    QUESTIONS = [
        ("Davout, can you support Ney?", "Davout"),
        ("Lannes, can you march to Frankfurt?", "Lannes"),
        ("Ney, can you hold the line?", "Ney"),
        ("Ney, should you attack Mack?", "Ney"),
    ]

    @pytest.mark.parametrize("text,who", QUESTIONS)
    def test_a_question_creates_no_standing_order(
            self, board, parser, executor, text, who):
        before = board.actions_remaining
        parsed, _ = _issue(board, parser, executor, text)
        assert not parsed.get("is_strategic"), (
            f"{text!r} stamped is_strategic — the executor intercepts on that "
            f"flag alone and will create a real order from a question")
        assert board.get_marshal(who).strategic_order is None
        assert board.actions_remaining == before, (
            "and it was free, which made it an AP exploit as well as a "
            "misreading")

    @pytest.mark.parametrize("text,who", QUESTIONS)
    def test_the_marshal_does_not_move(self, board, parser, executor, text, who):
        where = board.get_marshal(who).location
        _issue(board, parser, executor, text)
        assert board.get_marshal(who).location == where

    def test_a_question_never_stages_an_objection(self, board, parser, executor):
        """Measured: "Davout, can you march to Swabia?" fired a real
        pending_strategic_objection in a state where the imperative is refused
        outright — the marshal reacting to an order nobody gave."""
        _issue(board, parser, executor, "Davout, can you march to Swabia?")
        assert not getattr(board, "pending_strategic_objection", None)

    # ── the controls: the imperative must still work, and still cost ──

    IMPERATIVES = [
        ("Lannes, march to Frankfurt", "Lannes", "MOVE_TO"),
        ("Davout, support Ney", "Davout", "SUPPORT"),
        ("Ney, hold your position", "Ney", "HOLD"),
    ]

    @pytest.mark.parametrize("text,who,kind", IMPERATIVES)
    def test_the_imperative_still_issues_and_still_costs(
            self, board, parser, executor, text, who, kind):
        before = board.actions_remaining
        parsed, _ = _issue(board, parser, executor, text)
        assert parsed.get("strategic_type") == kind
        # NOT `== before - 2`: "Lannes, march to Frankfurt" is blocked by Mack
        # at Swabia on the boot board and charges a variable 1 AP for the
        # interrupted first step. That is pre-existing behaviour and measuring
        # it here would pin an unrelated rule. What this control has to prove
        # is that the gate did not disable the feature: the imperative is
        # still strategic and still PAYS, while the question is free.
        assert board.actions_remaining < before, (
            "the imperative must still be charged — the control that proves "
            "the gate did not simply disable the feature")

    def test_the_gate_names_a_rule_not_a_symptom(self):
        """`_NON_ORDER_ACTIONS` is deliberately NEITHER of the two lists it
        sits between: the parser's `meta_actions` holds genuine orders
        (charge, restrain, build, repair, recruit) and the executor's
        `free_actions` holds order-shaped verbs (retreat, wait). Reusing
        either would have changed behaviour far outside this defect."""
        from backend.commands.parser import _NON_ORDER_ACTIONS
        assert "help" in _NON_ORDER_ACTIONS and "status" in _NON_ORDER_ACTIONS
        for genuine_order in ("charge", "restrain", "build", "repair",
                              "recruit", "retreat", "wait", "move", "attack"):
            assert genuine_order not in _NON_ORDER_ACTIONS


# ══════════════════════════════════════════════════════════════════════════
# [2] P1 — "under no circumstances attack Mack" executed the attack
# ══════════════════════════════════════════════════════════════════════════


class TestTheProhibitiveIsHeard:
    """§PARSE-NEG's headline shape, recurring for the two most idiomatic
    English prohibitives its table never sampled.

    `_NEGATION_MARKER_RE`'s bare-"no" arm demands an order-NOUN straight after
    "no" ("no attack", "no advance"). In "under no circumstances attack" the
    noun is "circumstances", so NOTHING matched, the keyword chain read
    "attack" + marshal + target and stamped confidence 0.95 — above the 0.7
    gate, so the LLM was never consulted in any mode. Measured: Ney marched
    Rhineland->Swabia and fought Mack.
    """

    PROHIBITIVES = [
        "Ney, under no circumstances attack Mack",
        "Ney, on no account attack Mack",
        "Ney, by no means advance to Swabia",
        "Ney, in no case attack Mack",
        "Ney, at no time attack Mack",
    ]

    @pytest.mark.parametrize("text", PROHIBITIVES)
    def test_the_clause_is_blanked(self, text):
        effective, applied = strip_negated_clauses(text)
        assert applied is True
        assert "attack" not in effective.lower()
        assert "advance" not in effective.lower()
        assert len(effective) == len(text), (
            "positions must be preserved — every rule downstream indexes into "
            "this text")

    @pytest.mark.parametrize("text", PROHIBITIVES)
    def test_the_forbidden_order_never_executes(
            self, board, parser, executor, text):
        where = board.get_marshal("Ney").location
        before = board.actions_remaining
        _, result = _issue(board, parser, executor, text)
        assert result.get("success") is not True
        assert board.get_marshal("Ney").location == where, (
            "the game executed the precise order the player forbade")
        assert board.actions_remaining == before

    def test_the_attack_idiom_is_not_a_prohibition(self):
        """`attack_vocabulary` ships "no quarter" as an ATTACK idiom — the
        reason the marker list refuses a bare "no" in the first place."""
        effective, applied = strip_negated_clauses("Ney, give no quarter")
        assert applied is False and effective == "Ney, give no quarter"

    def test_the_plain_order_still_stands(self, board, parser, executor):
        parsed, _ = _issue(board, parser, executor, "Ney, attack Mack")
        assert (parsed.get("command") or {}).get("action") == "attack"


# ══════════════════════════════════════════════════════════════════════════
# [22] P3 — the destination fallback shipped the PURPOSE clause
# ══════════════════════════════════════════════════════════════════════════


class TestThePurposeClauseIsNotADestination:
    """"the destination is what follows the LAST preposition" is right for the
    LEADING infinitive ("I would like TO MOVE to Alsace") and wrong for the
    TRAILING purpose ("move to Venetia TO CUT them off"): the tail-cutter had
    no arm for a bare purpose "to", so the phantom won and the executor's
    refusal never even mentioned the province the player typed — defeating the
    Sweep-5 fix ("Region '<typed name>' not found. Nearby: …") this passthrough
    exists for.

    One rule covers both shapes: a preposition that introduces a VERB is not
    introducing a destination.
    """

    @pytest.mark.parametrize("text,expected", [
        ("Ney, move to Venetia to cut them off", "Venetia"),
        ("Ney, move to Alsace to cover the guns", "Alsace"),
        ("Ney, move to Alsace to block the road", "Alsace"),
        ("Ney, march to Venetia to take the crossing", "Venetia"),
        # NOT "…to support Davout": the whole fallback is deliberately skipped
        # when a support verb appears ("move to reinforce Ney" is a SUPPORT
        # order, not a march to a place called Reinforce), so that sentence
        # binds Davout by a different, pre-existing seam. Out of scope here,
        # and pinning it would misattribute someone else's rule to this fix.
        # the leading-infinitive control the "last wins" rule was built for
        ("I would like to move Ney to Alsace", "Alsace"),
        ("Ney, move to Alsace", "Alsace"),
    ])
    def test_the_typed_destination_survives(
            self, board, parser, executor, text, expected):
        parsed, _ = _issue(board, parser, executor, text)
        assert (parsed.get("command") or {}).get("target") == expected

    def test_the_widened_tail_cutter_still_cuts_its_own_arms(
            self, board, parser, executor):
        parsed, _ = _issue(
            board, parser, executor, "Ney, move to Alsace after Davout arrives")
        target = (parsed.get("command") or {}).get("target")
        assert target in (None, "Alsace"), target


# ══════════════════════════════════════════════════════════════════════════
# [23] P3 — an ordinary word bound a fogged commander
# ══════════════════════════════════════════════════════════════════════════


class TestAProperNameDoesNotTakeAnArticle:
    """"Ney, attack across the moor" resolved target=Moore — Britain's
    marshal, fogged, in London — and the refusal ("No intelligence on Moore's
    position") disclosed a hidden commander from a landscape noun.

    `_plausible_name_typo` cannot separate the two: "moor" and "Moore" share a
    first letter and one edit. Grammar separates them where spelling cannot,
    and the rule is applied to commander names ONLY — plenty of provinces are
    spoken with an article ("the Rhineland", "the Tyrol").
    """

    @pytest.mark.parametrize("text", [
        "Ney, attack across the moor",
        "Ney, attack the moor",
        "Ney, advance over the moor",
    ])
    def test_an_articled_noun_never_binds_a_commander(
            self, board, parser, executor, text):
        parsed, _ = _issue(board, parser, executor, text)
        assert (parsed.get("command") or {}).get("target") != "Moore"

    @pytest.mark.parametrize("text,expected", [
        ("Ney, attack Moore", "Moore"),        # deliberate, and fogged: allowed
        ("Ney, attack Mach", "Mack"),          # the CR-0 typo this arm exists for
        ("Ney, attack Mack", "Mack"),
        ("Ney, move to the Rhineland", "Rhineland"),   # articled REGION: fine
    ])
    def test_the_controls_are_untouched(
            self, board, parser, executor, text, expected):
        parsed, _ = _issue(board, parser, executor, text)
        assert (parsed.get("command") or {}).get("target") == expected

    def test_a_prisoner_is_never_a_target(self, board):
        """A captured marshal stays in `world.marshals` at strength 0 at his
        captor's capital, so the omniscient roster still offered him."""
        from backend.commands.parser import _is_targetable_enemy
        victim = next(m for m in board.marshals.values()
                      if m.nation != board.player_nation and m.strength > 0)
        assert _is_targetable_enemy(victim.name, board) is True
        victim.captured_by = board.player_nation
        victim.strength = 0
        assert _is_targetable_enemy(victim.name, board) is False


# ══════════════════════════════════════════════════════════════════════════
# [24] P3 — "hold the <name> pass" fired WAIT
# ══════════════════════════════════════════════════════════════════════════


class TestTheMountainPass:
    """The wait branch's guard used FIXED lookbehinds ("the/a/this/that
    pass"), so any pass noun carrying a modifier fired `wait` — and the wait
    branch sits ABOVE the hold family in the elif chain, so a plain defensive
    order became a turn pass.

    The REFUSAL that follows is correct and deliberate (CA8-28): the player
    named a place, and quietly holding somewhere else while charging 2 AP is
    the defect, not the kindness. What was wrong is the copy.
    """

    PASSES = [
        "Ney, hold the mountain pass",
        "Ney, hold the Brenner pass",
        "Ney, guard the mountain pass",
        "Davout, hold the pass",
    ]

    @pytest.mark.parametrize("text", PASSES)
    def test_it_is_a_hold_order_not_a_turn_pass(
            self, board, parser, executor, text):
        parsed, _ = _issue(board, parser, executor, text)
        assert (parsed.get("command") or {}).get("action") != "wait", (
            "a defensive order became a turn pass")

    @pytest.mark.parametrize("text", PASSES)
    def test_the_refusal_is_honest_and_free(
            self, board, parser, executor, text):
        before = board.actions_remaining
        _, result = _issue(board, parser, executor, text)
        assert result.get("success") is False
        assert "could not make out a destination" not in result["message"], (
            "the player gave a perfectly clear destination; the map simply "
            "has no province for it, and saying otherwise sends him hunting "
            "for a typo he did not make")
        assert "pass" in result["message"].lower()
        assert board.actions_remaining == before
        assert "Nassau" not in result["message"], (
            "CA8-28's negative control: never auto-correct a pass into a "
            "province 200km away")

    @pytest.mark.parametrize("text", ["Ney, pass", "Ney, pass the turn",
                                      "Ney, pass this turn"])
    def test_the_bare_verb_still_passes_the_turn(
            self, board, parser, executor, text):
        parsed, _ = _issue(board, parser, executor, text)
        assert (parsed.get("command") or {}).get("action") == "wait"

    def test_the_terrain_helper_reads_the_noun_not_the_modifier(self):
        from backend.ai.strategic_parser import unmapped_terrain_noun
        assert unmapped_terrain_noun("the mountain pass") == "pass"
        assert unmapped_terrain_noun("the Brenner Pass") == "pass"
        assert unmapped_terrain_noun("the river ford") == "ford"
        assert unmapped_terrain_noun("Swabia") is None
        assert unmapped_terrain_noun("") is None
