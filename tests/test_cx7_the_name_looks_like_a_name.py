"""CX-7 — "THE NAME LOOKS LIKE A NAME": row CX's own review round.

Row CX ("The Hand on the Keyboard"). Owner record:
`docs/COMMAND_EXPERIENCE_SPEC.md` §8; rules `docs/SYSTEMS_REFERENCE.md` §50.

A 63-agent adversarial review at `727cf88a`, every finding put to refuters
whose default verdict was REFUTED, confirmed TWO defects that row CX had
itself shipped. Both are the same mistake in opposite directions, and both
live in the pair of rules slice 1 landed in one commit.

────────────────────────────────────────────────────────────────────────
L2-5 — THE BLOCKLIST FAILED OPEN (256 of 261 cells)
────────────────────────────────────────────────────────────────────────
`_unbound_addressee`'s comma-less arm asked *is this leading run NOT a
name?* against a hand-written list of grammar words. English has more
adverbs than that list will ever hold, so every unlisted word was claimed
as somebody's name and the order refused. Filed as 23 shapes across 2
doors; MEASURED by the refuter at 9 marshal-less doors × 29 natural
leading runs = 261 cells, **256 newly refused**, proven against a true
pre-row tree (`git archive b4a27a15^`) rather than a lever flip:

    "quickly attack Mack"  → "There is no 'quickly' in the order of
                              battle, Sire. Whom did you intend?"
    "cavalry attack Mack"  → the same, for an arm of service
    "ok retreat"           → the same, for assent
    "someone attack Mack"  → the same — and this is the sharpest of all,
                              because "I do not care who, send whoever is
                              nearest" is precisely what `auto_assign_attack`
                              exists for, and the game's own clarification
                              asks "Which marshal shall lead the attack?"

⚠ The finding's own prescribed fix — L2-4's head-token rule — was measured
by the refuter to close **0 of 23**, and to WIDEN the defect by one shape
("quickly and at once attack Mack"). It was not followed.

And the SAME hand-written list under-refused in the other direction: the
verb regex the head is measured against was missing two verbs the mock
parser routes into the marshal-less family, so

    "Zorglub pull back"    → a WHOLE-ARMY RETREAT
    "Zorglub recon Swabia" → Soult scouted

— FA-22's original defect, still live. One root, both signs.

────────────────────────────────────────────────────────────────────────
CXR1-1 — THE ROW ARGUED WITH ITSELF (86 of 128 orders)
────────────────────────────────────────────────────────────────────────
Arm (e) of the question guard read a line as ADDRESSED only through
`_ADDRESSED_LINE_RE`, which requires a comma or a colon — while the other
half of the very same commit is titled AN ADDRESS NEEDS NO COMMA and
exists *because a player does not type the comma*. So:

    "Ney, attack Mack?"  → Ney fights (1 AP, 291 gold, four corps move)
    "Ney attack Mack?"   → "Berthier sets down his pen. I cannot answer
                            that from the dispatches, Sire."

The refuter's effect sweep, joined across both trees: of 128 comma-free
addressed orders, **86 acted before and are inert now**; 58 of those
changed real state and 28 raised a marshal's objection — a decision point
that now raises nothing. Nothing is spent and nothing is corrupted, which
is what keeps it off P1; it is wide, silent and on the road this row's own
gate ruling calls *the road that wins the turn*, which is what keeps it
off P3.

────────────────────────────────────────────────────────────────────────
THE FIX — ONE PREDICATE, ASKED THE OTHER WAY ROUND
────────────────────────────────────────────────────────────────────────
`clause_guards.looks_like_an_address` asks *does this run LOOK LIKE a
name?* and fails CLOSED. `clause_guards.address_of` is the single source
for "who was addressed", comma or no comma, and BOTH rules read it — so
the two halves of row CX cannot disagree again.

This is IQ-7's own review-round lesson arriving one row later: *a rule
built by stripping what you recognise is only as safe as the list it
strips.* The answer there was to write the allowlist out; it is the answer
here too.

MEASURED, on the refuter's own 261-cell grid, both lever arms, driven end
to end through `POST /command` on a fresh shipped 1805 board per cell:

    LEVER OFF (reproduces HEAD)   221 of 261 refused as unknown officers
    LEVER ON  (CX-7)                9 of 261

⚠ The surviving 9 are all `sure <door>` and are NOT this row's: they come
from the parser's own fuzzy near-miss guard, a different producer with a
different sentence ("I do not find 'sure' in the order of battle, Sire.
Did you mean Soult?"). Filed as CX7-X1, not fixed here.

HONEST RESIDUE, stated rather than discovered later
===================================================
An all-lowercase INVENTED name (`zorglub attack mack`) is no longer
claimed as an address, so it reaches the marshal-less arm exactly as it
did before row CX. That is the pre-row behaviour, not a new loss — and the
near-miss that actually matters (`nay` → Ney) is still caught at any case
by the one-keystroke arm. Pinned below so it cannot change in silence.
"""

import io
import contextlib

import pytest

from backend.ai import clause_guards as CG
from backend.commands.executor import CommandExecutor


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _fresh_board():
    from fastapi.testclient import TestClient
    from backend.ai.parser_eval import build_world
    from backend.commands.parser import CommandParser
    import backend.main as M
    with _quiet():
        world = build_world("1805")
        M.world = world
        M.game_state = {"world": world}
        M.parser = CommandParser(use_real_llm=False)
        client = TestClient(M.app)
    return world, client


def _drive(utterance):
    world, client = _fresh_board()
    before = (world.actions_remaining, world.gold, world.current_turn,
              {m.name: (m.location, m.strength)
               for m in world.get_player_marshals()})
    with _quiet():
        response = client.post("/command", json={"command": utterance}).json()
    after = (world.actions_remaining, world.gold, world.current_turn,
             {m.name: (m.location, m.strength)
              for m in world.get_player_marshals()})
    footprint = {
        "ap": (before[0], after[0]),
        "gold": (before[1], after[1]),
        "turn": (before[2], after[2]),
        "moved": sorted(k for k, v in before[3].items()
                        if after[3].get(k) != v),
        "battle": bool(response.get("battle_report")),
    }
    return response, footprint


def _message(response):
    return (response.get("message") or response.get("error") or "")


_UNBOUND = "in the order of battle"


def _refused_as_unknown(response):
    """The unbound-addressee refusal SPECIFICALLY — not the parser's own
    fuzzy near-miss guard, which says "I do not find … Did you mean …?"
    and belongs to a different producer (CX7-X1)."""
    return "There is no '" in _message(response)


# ═══════════════════════════════════════════════════════════════════════════
# L2-5 — the grid. An ordinary order with a word in front of it is an order.
# ═══════════════════════════════════════════════════════════════════════════
# The refuter's own runs, one per closed class it found. Crossed with the
# doors below in the grid test; named individually here so a failure says
# WHICH class regressed.
_LEADING_RUNS = [
    # the productive class, closed by morphology rather than by listing
    "quickly", "immediately", "urgently", "promptly", "instantly", "swiftly",
    # assent and hesitation
    "ok", "okay", "yes", "alright", "right", "well",
    # time
    "today", "tonight", "now", "finally",
    # arms of service — a collective, not a person
    "cavalry", "infantry", "artillery", "guards", "gentlemen",
    # the indefinite pronouns — the plain English for auto-assign
    "someone", "somebody", "anyone",
    # the bare honorific: a title with nobody after it names nobody
    "Marshal", "General",
]

_MARSHAL_LESS_DOORS = [
    "attack Mack", "attack", "assault", "storm", "retreat", "withdraw",
    "pull back", "scout Swabia", "bombard Mack",
]


class TestAnOrdinaryOrderIsNotAnUnknownOfficer:
    """256 of 261 cells. Each of these was refused at HEAD."""

    @pytest.mark.parametrize("run", _LEADING_RUNS)
    def test_the_run_is_not_claimed_as_a_name(self, run):
        response, _ = _drive(f"{run} attack Mack")
        assert not _refused_as_unknown(response), _message(response)

    @pytest.mark.parametrize("door", _MARSHAL_LESS_DOORS)
    def test_every_marshal_less_door(self, door):
        response, _ = _drive(f"quickly {door}")
        assert not _refused_as_unknown(response), _message(response)

    def test_the_indefinite_pronoun_reaches_the_auto_assign(self):
        """"someone attack Mack" IS the auto-assign — the game's own
        clarification asks "Which marshal shall lead the attack, Sire?"."""
        response, footprint = _drive("someone attack Mack")
        assert not _refused_as_unknown(response), _message(response)
        assert footprint["moved"] or "muster" in _message(response).lower() \
            or "which marshal" in _message(response).lower(), _message(response)

    def test_a_run_of_grammar_around_a_content_word(self):
        """The prescribed head-token fix would have ADDED this refusal; the
        refuter measured it, and it is pinned so nobody re-introduces it."""
        response, _ = _drive("quickly and at once attack Mack")
        assert not _refused_as_unknown(response), _message(response)

    @pytest.mark.parametrize("run", [
        "Ok", "Okay", "Yes", "Well", "Right", "Sure", "Now", "Today",
        "Tonight", "Please", "Can", "Do", "Let", "First", "Just",
    ])
    def test_the_class_list_earns_its_keep_on_a_CAPITALISED_run(self, run):
        """The list's one unique job, and the sweep found it unpinned.

        A lowercase grammar word fails the name test on its own — it is not
        capitalised and it is not near any roster name — so emptying the list
        changed nothing the other pins could see and the mutation came back
        INERT. The list exists for the player who capitalises the first word
        of a sentence, and THAT is what has to be pinned. (`Quickly` is not
        in here on purpose: the -ly rule owns it, and has its own pin.)"""
        assert CG.looks_like_an_address(run, ["Ney", "Soult"]) is False, run
        assert CG.address_of(f"{run} attack Mack", ["Ney"]) is None

    def test_a_capitalised_sentence_start_still_marches(self):
        """End to end, on the shape a capitalising player actually types."""
        for utterance in ("Ok retreat", "Well, attack Mack",
                          "Quickly attack Mack"):
            response, _ = _drive(utterance)
            assert not _refused_as_unknown(response), (utterance,
                                                       _message(response))

    def test_the_bare_honorific_names_nobody(self):
        """HONORIFIC comes off first, and what is left is nothing — so the
        order is bare, not addressed to an officer called "Marshal"."""
        assert CG.looks_like_an_address("Marshal") is False
        assert CG.looks_like_an_address("General") is False
        assert CG.looks_like_an_address("Marshal Ney") is True

    def test_the_ly_adverb_is_closed_by_morphology_not_by_listing(self):
        """The one PRODUCTIVE class. A word this test has never seen must
        still fail, or the rule is a list again."""
        for invented in ("blisteringly", "thunderously", "obstreperously"):
            assert CG.looks_like_an_address(invented) is False, invented
            assert CG.looks_like_an_address(invented.capitalize()) is False


# ═══════════════════════════════════════════════════════════════════════════
# The guard must still BITE — CX-1's own reason for existing.
# ═══════════════════════════════════════════════════════════════════════════
class TestTheGuardStillBites:

    @pytest.mark.parametrize("utterance", [
        "Nay attack Mack",          # a one-keystroke typo for Ney
        "nay attack mack",          # ... at any case, via the keystroke arm
        "Nay, attack Mack",         # ... and with the comma
        "Zorglub attack Mack",      # an invented name, capitalised
        "Grouchy attack Mack",      # on the commission bench, not in the field
        "Wellington retreat",       # a foreign marshal — used to march OUR army
        "Blucher attack Mack",
    ])
    def test_an_unbound_name_is_still_refused_free(self, utterance):
        response, footprint = _drive(utterance)
        assert _refused_as_unknown(response), _message(response)
        assert footprint["ap"][0] == footprint["ap"][1], footprint
        assert footprint["gold"][0] == footprint["gold"][1], footprint
        assert not footprint["moved"], footprint
        assert not footprint["battle"], footprint

    @pytest.mark.parametrize("utterance", [
        "Zorglub pull back",        # FA-22's own defect, still live at HEAD
        "Zorglub recon Swabia",
    ])
    def test_the_mirror_hole_is_closed(self, utterance):
        """The verb list the head is measured against was hand-maintained in
        `executor.py` and missing two verbs the mock parser routes. At HEAD
        these ran a whole-army retreat and a scout for a name nobody has."""
        response, footprint = _drive(utterance)
        assert _refused_as_unknown(response), _message(response)
        assert not footprint["moved"], footprint

    def test_the_collective_reaches_the_clarification_with_a_comma_too(self):
        """A stated correction: CX-1's collective stand-down lived INSIDE the
        comma-less branch, so "all marshals, attack" — the same address, one
        keystroke over — was refused as an officer called "all marshals"."""
        response, _ = _drive("all marshals, attack")
        assert not _refused_as_unknown(response), _message(response)

    def test_the_lowercase_invented_name_is_the_stated_residue(self):
        """Not an oversight — the price of failing closed, and the pre-row
        behaviour. If this ever changes, it changes deliberately."""
        assert CG.looks_like_an_address("zorglub") is False
        assert CG.looks_like_an_address("zorglub", ["Ney", "Soult"]) is False


# ═══════════════════════════════════════════════════════════════════════════
# THE COMMA IS THE PLAYER'S OWN MARK OF ADDRESS.
# ═══════════════════════════════════════════════════════════════════════════
# Found by running the full suite: applying the name rule to the COMMA'D arm
# too — which had never had one — redded four of FA-22's pins, because
# "the cavalry, attack Mack" and "the reserve, attack Mack" are ADDRESSES by
# the player's own punctuation and FA-22 exists to stop the game answering
# them with somebody else. The resolution is not a third list but the
# separator itself:
#
#   comma  → the player MARKED a run as an address. Claim it and answer for
#            it. (FA-22, unchanged.)
#   none   → nothing was marked, so claim it only if it LOOKS like a name.
#            (CX-7.)
#
# The one thing that stands down on BOTH arms is the COLLECTIVE, because the
# marshal-less arm exists precisely to serve it.
#
# This leaves a deliberate asymmetry on runs that are not name-shaped —
# "cavalry attack Mack" falls through, "the cavalry, attack Mack" is refused
# — and it is NOT the split CXR1-1 condemns. There the two forms carried the
# same name and disagreed anyway; here the forms carry different evidence of
# intent, and the comma is the evidence.
class TestTheCommaIsTheMark:

    @pytest.mark.parametrize("utterance,expected", [
        ("the Iron Marshal, attack Mack", "Iron Marshal"),
        ("Iron Marshal, attack Mack", "Iron Marshal"),
        ("Berthier, attack Mack", "Berthier"),
        ("Prince of Moskowa, attack Mack", "Prince of Moskowa"),
        ("the cavalry, attack Mack", "cavalry"),
        ("the reserve, attack Mack", "reserve"),
    ])
    def test_a_marked_run_is_answered_for(self, utterance, expected):
        """FA-22's own list, verbatim. The refusal names what the player
        typed, minus the article."""
        assert CG.address_of(utterance, ["Ney", "Soult"]) == expected

    @pytest.mark.parametrize("utterance", [
        "cavalry attack Mack", "infantry attack Mack", "guards attack Mack",
        "gentlemen attack Mack", "artillery attack Mack",
    ])
    def test_an_unmarked_arm_of_service_falls_through(self, utterance):
        """Deliberately in NEITHER list: bare and lowercase they are not
        name-shaped, so nothing claims them."""
        assert CG.address_of(utterance, ["Ney", "Soult"]) is None

    @pytest.mark.parametrize("utterance", [
        "all marshals, attack", "all marshals attack",
        "everyone, attack Mack", "everyone attack Mack",
        "someone, attack Mack", "someone attack Mack",
        "whoever is closest, attack Mack",
    ])
    def test_a_collective_stands_down_on_both_arms(self, utterance):
        """The correction. At HEAD the stand-down lived INSIDE the comma-less
        branch, so the same address was served without a comma and refused
        with one."""
        assert CG.address_of(utterance, ["Ney", "Soult"]) is None
        assert CG.addresses_the_army(utterance.split(",")[0]) is True \
            or "attack" in utterance.split(",")[0]

    def test_the_arms_disagree_only_where_the_evidence_does(self):
        """The asymmetry, stated as a property rather than as a list: a
        NAME-shaped run behaves the same either way — that is CXR1-1 — and
        only an unmarked, un-name-shaped run differs."""
        roster = ["Ney", "Soult"]
        for name in ("Nay", "Zorglub", "Wellington"):
            assert CG.address_of(f"{name} attack Mack", roster) == name
            assert CG.address_of(f"{name}, attack Mack", roster) == name


# ═══════════════════════════════════════════════════════════════════════════
# CXR1-1 — the pair must behave alike.
# ═══════════════════════════════════════════════════════════════════════════
class TestTheCommaIsNotTheDifference:

    @pytest.mark.parametrize("bare,with_comma", [
        ("Ney attack Mack?", "Ney, attack Mack?"),
        ("Ney retreat?", "Ney, retreat?"),
        ("Ney scout Swabia?", "Ney, scout Swabia?"),
        ("Marshal Ney attack Mack?", "Marshal Ney, attack Mack?"),
    ])
    def test_the_comma_does_not_decide_the_reading(self, bare, with_comma):
        """The finding itself, pinned at the seam that DECIDES it.

        Deliberately not an end-to-end footprint comparison: a retreat is
        free by design (FA-R3), the endpoint re-seats `world`, and Ney's
        objection to a retreat is a probabilistic roll — a first cut of this
        pin compared footprints and was FLAKY on "Ney, retreat?" for that
        reason. `is_question` is the thing the defect lived in, and it is
        deterministic."""
        roster = ["Ney", "Davout", "Soult"]
        assert CG.is_question(with_comma, roster) is False, with_comma
        assert CG.is_question(bare, roster) is False, (
            bare, "the comma was the whole difference")
        assert CG.address_of(bare, roster) is not None, bare

    def test_the_question_mark_alone_no_longer_swallows_the_order(self):
        response, _ = _drive("Ney attack Mack?")
        assert "I cannot answer that" not in _message(response), \
            _message(response)
        assert "muster" in _message(response).lower(), _message(response)


    @pytest.mark.parametrize("bare,with_comma", [
        ("Ney attack Mack?", "Ney, attack Mack?"),
        ("Ney scout Swabia?", "Ney, scout Swabia?"),
    ])
    def test_end_to_end_on_the_deterministic_verbs(self, bare, with_comma):
        """The two doors with no objection roll on them, driven whole."""
        bare_r, _ = _drive(bare)
        comma_r, _ = _drive(with_comma)
        assert "I cannot answer that" not in _message(comma_r), with_comma
        assert "I cannot answer that" not in _message(bare_r), bare
        assert _message(bare_r)[:50] == _message(comma_r)[:50], (
            _message(bare_r)[:50], _message(comma_r)[:50])


class TestArmEStillHoldsItsControls:
    """Everything CX-1 landed arm (e) FOR. A bare order that asks is still a
    question — it is the ADDRESS that changes the reading, not the "?"."""

    @pytest.mark.parametrize("utterance", [
        "retreat?", "attack?", "fortify?", "charge?", "drill?",
        "all marshals attack?",
    ])
    def test_an_unaddressed_order_that_asks_is_still_a_question(self,
                                                                utterance):
        response, footprint = _drive(utterance)
        assert not footprint["moved"], (utterance, footprint)
        assert not footprint["battle"], (utterance, footprint)
        assert footprint["ap"][0] == footprint["ap"][1], footprint

    @pytest.mark.parametrize("utterance", [
        "why not attack Mack", "who holds Swabia", "is Swabia defended",
        "can Ney attack Mack", "what about attack Mack",
    ])
    def test_the_other_arms_are_untouched(self, utterance):
        _, footprint = _drive(utterance)
        assert not footprint["moved"], (utterance, footprint)
        assert not footprint["battle"], (utterance, footprint)

    @pytest.mark.parametrize("utterance", [
        "attack Mack", "retreat", "everyone attack Mack",
        "can you attack Mack", "do attack Mack", "please attack Mack",
        "Ney, attack Mack",
    ])
    def test_the_orders_that_must_still_march(self, utterance):
        response, footprint = _drive(utterance)
        assert not _refused_as_unknown(response), _message(response)
        assert (footprint["moved"] or footprint["battle"]
                or footprint["ap"][1] < footprint["ap"][0]
                or "muster" in _message(response).lower()), footprint

    def test_end_turn_with_a_question_mark_still_ends_the_turn(self):
        """FA-R4, deliberately. Pinned so CX-7 cannot drift it either."""
        _, footprint = _drive("end turn?")
        assert footprint["turn"][1] > footprint["turn"][0], footprint


# ═══════════════════════════════════════════════════════════════════════════
# THE PREDICATE, pinned directly — arms, classes and boundaries.
# ═══════════════════════════════════════════════════════════════════════════
class TestThePredicate:

    def test_capitalisation_as_typed_is_one_arm(self):
        assert CG.looks_like_an_address("Zorglub") is True
        assert CG.looks_like_an_address("zorglub") is False

    def test_one_keystroke_from_a_roster_name_is_the_other(self):
        assert CG.looks_like_an_address("nay", ["Ney"]) is True
        assert CG.looks_like_an_address("nay", []) is False
        assert CG.looks_like_an_address("davut", ["Davout"]) is True

    def test_it_fails_closed(self):
        """Anything it cannot positively recognise is NOT an address. This is
        the whole direction change, and the thing that must never invert."""
        for run in ("frobnicate", "wibbly", "hencewise", ""):
            assert CG.looks_like_an_address(run) is False, run

    def test_more_than_three_tokens_is_not_a_name(self):
        """A bound, not a coincidence. The first cut of this pin used
        "Whoever Is Closest To Him", whose FIRST token is a closed-class
        word — so it passed with the bound deleted, and the mutation
        sweep called it INERT. Four capitalised tokens with no class
        word among them reach the bound and nothing else."""
        assert CG.looks_like_an_address("Alpha Beta Gamma Delta") is False
        assert CG.looks_like_an_address("Alpha Beta Gamma") is True
        assert CG.looks_like_an_address("Whoever Is Closest To Him") is False

    def test_the_article_and_the_honorific_come_off_first(self):
        """In that ORDER, and with the trailing space optional.

        A regression this slice shipped and the full suite caught: applying
        the name rule to the COMMA'D arm too (which had skipped it entirely)
        put the singular "marshal" in the closed-class list, so Davout's own
        epithet stopped being a name and "the Iron Marshal, attack Mack"
        SENT SOULT — the exact defect FA-22's pin exists for. The title is
        the HONORIFIC's business; the class list keeps only the plurals."""
        assert CG.looks_like_an_address("Marshal") is False
        assert CG.looks_like_an_address("the Marshal") is False
        assert CG.looks_like_an_address("a general") is False
        assert CG.looks_like_an_address("Marshal Ney") is True
        assert CG.looks_like_an_address("the Marshal Ney") is True
        assert CG.looks_like_an_address("the Iron Marshal") is True
        assert CG.looks_like_an_address("Iron Marshal") is True
        assert CG.looks_like_an_address("generals") is False

    def test_our_own_marshal_is_never_unbound(self):
        """`_names_a_player_marshal` is the guard that stops a name-shaped
        run NAMING ONE OF OURS from being refused as a stranger. It is only
        reachable when the parser failed to bind, which no end-to-end
        sentence on the boot board does — so it is driven at the function's
        own contract instead, which is where it lives. The sweep called the
        first, end-to-end version of this pin INERT, correctly."""
        world, _ = _fresh_board()
        ex = CommandExecutor()

        def unbound(phrase):
            cmd = {"type": "general_attack",
                   "raw_input": f"{phrase} attack Mack"}
            return ex._unbound_addressee(cmd, cmd, world)

        assert unbound("Zorglub") == "Zorglub"
        for ours in ("Ney", "Massena", "Massena's corps", "Davout"):
            assert unbound(ours) is None, ours

    def test_address_of_is_the_single_source(self):
        """One reader for "who was addressed", comma or not — the whole point
        of the slice. If these disagree, the two halves have split again."""
        roster = ["Ney", "Soult"]
        assert CG.address_of("Ney, attack Mack?", roster) == "Ney"
        assert CG.address_of("Ney attack Mack?", roster) == "Ney"
        assert CG.address_of("attack Mack", roster) is None
        assert CG.address_of("quickly attack Mack", roster) is None
        assert CG.address_of("what about attacking?", roster) is None

    def test_require_separator_carries_the_older_lever(self):
        """CX-1's `AN_ADDRESS_NEEDS_NO_COMMA` is nested inside CX-7's and must
        keep meaning what it says, not be swallowed by the newer rule."""
        assert CG.address_of("Nay attack Mack", ["Ney"]) == "Nay"
        assert CG.address_of("Nay attack Mack", ["Ney"],
                             require_separator=True) is None


# ═══════════════════════════════════════════════════════════════════════════
# THE SUBJECT MAY HAVE TWO NAMES.
# ═══════════════════════════════════════════════════════════════════════════
# The review round filed this as a false CLAIM in `is_question`'s docstring —
# the roster arm advertised a roster and read ONE token after the lead. It is
# also a live defect on the typed road, so it is fixed rather than only
# stated: the roster holds the PRINTED form of a name, so the commanders the
# game shows the player are exactly the ones the arm could not see.
class TestTheSubjectMayHaveTwoNames:

    ROSTER = ["Ney", "Mack", "Davout", "Archduke Charles", "Prince Bagration"]

    @pytest.mark.parametrize("utterance", [
        "can Archduke Charles attack Mack",
        "does Archduke Charles hold Vienna",
        "will Prince Bagration attack",
        "should Archduke Charles retreat",
    ])
    def test_a_two_word_subject_asks(self, utterance):
        assert CG.is_question(utterance, self.ROSTER) is True, utterance

    @pytest.mark.parametrize("utterance", [
        "can Ney attack Mack", "does Mack hold Swabia",
    ])
    def test_the_one_word_subject_is_unchanged(self, utterance):
        assert CG.is_question(utterance, self.ROSTER) is True, utterance

    @pytest.mark.parametrize("utterance", [
        "can you attack Mack", "would you have Ney attack Mack",
    ])
    def test_the_second_person_is_still_an_order(self, utterance):
        assert CG.is_question(utterance, self.ROSTER) is False, utterance

    def test_both_spellings_of_one_man_ask(self):
        """A roster carrying the key AND the printed form — which is exactly
        what `_question_subjects` now hands in — asks either way.

        ⚠ It does NOT pin an ordering. The first draft sorted longest-first
        "so a shorter name cannot shadow a longer one"; the sweep showed that
        sort inert, because the test is `startswith` on the opening of the
        run and the answer is a boolean. The sort is deleted, not pinned."""
        roster = ["ArchdukeCharles", "Archduke Charles"]
        for spelling in ("can Archduke Charles attack Mack",
                         "can ArchdukeCharles attack Mack"):
            assert CG.is_question(spelling, roster) is True, spelling

    def test_the_lever(self):
        assert CG.THE_SUBJECT_MAY_HAVE_TWO_NAMES is True
        original = CG.THE_SUBJECT_MAY_HAVE_TWO_NAMES
        try:
            CG.THE_SUBJECT_MAY_HAVE_TWO_NAMES = False
            assert CG.is_question("can Archduke Charles attack Mack",
                                  self.ROSTER) is False,                 "lever off = the defect reproduces"
            assert CG.is_question("can Ney attack Mack", self.ROSTER) is True
        finally:
            CG.THE_SUBJECT_MAY_HAVE_TWO_NAMES = original

    def test_it_reaches_the_board_end_to_end(self):
        """The shipped 1805 board prints "Archduke Charles"; driving him is
        the row's own geometry, not a fixture's."""
        response, footprint = _drive("can Archduke Charles attack Mack")
        assert not footprint["battle"], footprint
        assert not footprint["moved"], footprint
        assert footprint["ap"][0] == footprint["ap"][1], footprint
        del response


# ═══════════════════════════════════════════════════════════════════════════
# THE LEVERS — each False arm reproduces exactly what that caller shipped.
# ═══════════════════════════════════════════════════════════════════════════
class TestTheLevers:

    def test_the_lever_is_on(self):
        assert CG.THE_ADDRESS_LOOKS_LIKE_A_NAME is True

    def test_lever_off_reproduces_the_defect(self):
        original = CG.THE_ADDRESS_LOOKS_LIKE_A_NAME
        try:
            CG.THE_ADDRESS_LOOKS_LIKE_A_NAME = False
            response, _ = _drive("quickly attack Mack")
            assert _refused_as_unknown(response), \
                ("lever off = L2-5 reproduces", _message(response))
            _, footprint = _drive("Ney attack Mack?")
            assert not footprint["moved"] and not footprint["battle"], \
                ("lever off = CXR1-1 reproduces", footprint)
        finally:
            CG.THE_ADDRESS_LOOKS_LIKE_A_NAME = original

    def test_the_older_lever_is_still_live_underneath(self):
        """A lever swallowed by a newer one is not a lever. With CX-1's arm
        off, a comma-free unbound name falls through as it did before row CX."""
        original = CommandExecutor.AN_ADDRESS_NEEDS_NO_COMMA
        try:
            CommandExecutor.AN_ADDRESS_NEEDS_NO_COMMA = False
            response, footprint = _drive("Nay attack Mack")
            assert not _refused_as_unknown(response), _message(response)
            assert footprint["battle"] or footprint["moved"], footprint
        finally:
            CommandExecutor.AN_ADDRESS_NEEDS_NO_COMMA = original


# ═══════════════════════════════════════════════════════════════════════════
# THE WIRE and THE COMPLETER — CX-3's own rule, breached through its own
# history arm.
# ═══════════════════════════════════════════════════════════════════════════
class TestTheGameDoesNotOfferWhatItCannotRead:

    def test_kind_reaches_the_wire(self):
        """`_build_command_response` composes from named fields and dropped
        `kind`, so an unreadable refusal arrived as a bare sentence with no
        structured handle. Display-only (GR6)."""
        response, _ = _drive("Nay attack Mack")
        assert response.get("kind") == "marshal_not_found", response.get("kind")

    def test_an_ordinary_refusal_carries_no_such_kind(self):
        """Deliberately narrow: a command the game READ and refused for game
        reasons is not unreadable, and stays in history."""
        response, _ = _drive("Ney, march to Moscow")
        assert response.get("success") is False
        assert response.get("kind") is None, response.get("kind")

    def test_the_forget_rule_itself(self):
        """The guard, mirrored. A source census alone is killed by a text
        mutation by construction (slice 13's lesson), and the first cut of
        this pin checked only that the KINDS dict existed — the sweep turned
        the guard into `if false:` and the pin stayed green. So the three
        clauses are asserted against the source AND the rule is exercised."""
        src = io.open("godot-client/project-sovereign/scripts/main.gd",
                      encoding="utf-8").read()
        body = src[src.index("func _forget_unreadable_command"):]
        body = body[:body.index("func _on_end_turn_pressed")]
        assert 'if response.get("success", false):' in body, \
            "a command the game ACTED on is never forgotten"
        assert 'not UNREADABLE_KINDS.has(kind)' in body, \
            "only an unreadable kind is forgotten — not every refusal"
        assert "command_history.pop_back()" in body

        # the rule, mirrored from those three clauses
        kinds = {"marshal_not_found", "enemy_addressee"}

        def forgets(response):
            if response.get("success", False):
                return False
            kind = str(response.get("kind", ""))
            return bool(kind) and kind in kinds

        assert forgets({"success": False, "kind": "marshal_not_found"}) is True
        assert forgets({"success": True, "kind": "marshal_not_found"}) is False
        assert forgets({"success": False, "kind": None}) is False
        assert forgets({"success": False}) is False

    def test_the_client_forgets_an_unreadable_command(self):
        """The history arm runs BEFORE the grammar and offers a past command
        verbatim, and `_add_to_history` is called ~50 lines before the send
        with no success flag — so a refused sentence was recorded and never
        un-recorded. Source census: the forget must be CALLED, and called
        before any routing or early return."""
        import re
        src = io.open(
            "godot-client/project-sovereign/scripts/main.gd",
            encoding="utf-8").read()
        assert "func _forget_unreadable_command" in src
        assert src.count("_forget_unreadable_command(response)") == 1, \
            "called exactly once, from the pre-routing block"
        stash = src.index("_stash_proclamation(response)")
        forget = src.index("_forget_unreadable_command(response)")
        assert forget < stash, "must run before any stash or early return"
        # the set is explicit, and success never forgets
        body = src[forget:src.index("func _on_end_turn_pressed")]
        assert "UNREADABLE_KINDS" in src
        assert re.search(r'"marshal_not_found":\s*true', src)
        del body

    def test_the_completer_history_arm_is_the_surface_at_risk(self):
        """Ported verbatim from `_build_completions`' first block, so this
        pin fails if the history arm stops being prefix-first."""
        history = ["Ney, attack Mack", "quickly attack Mack"]
        prefix = "qui"
        offered = [h for h in reversed(history)
                   if h.lower().startswith(prefix.lower())]
        assert offered == ["quickly attack Mack"], offered
        # ... and with CX-7 landed, that sentence is one the game CAN read.
        response, _ = _drive("quickly attack Mack")
        assert not _refused_as_unknown(response), _message(response)
