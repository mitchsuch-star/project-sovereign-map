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


# ══════════════════════════════════════════════════════════════════════════
# PART 2 — diplomacy, settlement, the turn loop and the client
# ══════════════════════════════════════════════════════════════════════════


def _read(path):
    import io
    return io.open(path, encoding="utf-8").read()


def _code_only(text: str) -> str:
    """`text` with comments and docstrings removed.

    THE standing lesson of this codebase, and it bit four pins in this very
    file before the sweep: a source-substring pin must never read the prose
    written to explain its own fix. Every fix here carries a comment quoting
    the retired expression it replaced, so a bare `in`/`not in` scan finds the
    string it is asserting is gone — green when the fix is absent, and green
    when the comment is absent too. Strip the prose; pin the code.
    """
    import io as _io
    import tokenize
    newline = chr(10)
    try:
        out = []
        readline = _io.StringIO(text).readline
        for tok in tokenize.generate_tokens(readline):
            if tok.type == tokenize.COMMENT:
                continue
            if tok.type == tokenize.STRING and tok.line.strip().startswith(
                    ('"""', "'''", 'r"""')):
                continue
            out.append(tok.string)
        return " ".join(out)
    except Exception:
        # A partial slice (or GDScript) that `tokenize` cannot read: fall back
        # to a line-level strip, which still removes the explanatory prose
        # these pins kept finding.
        return newline.join(
            ln for ln in text.split(newline)
            if not ln.strip().startswith("#"))


class TestOneArmisticeRule:
    """Four sites resolved the armistice variant and disagreed at exactly 0.

    The scoring seam read `ws < 0 -> losing` (a level war is
    `armistice_winning`, BASE_DISPOSITION 20); the wizard likelihood, the
    acceptance preview and the BPH-B snapshot all read `ws > 0 -> winning`
    (a level war is `armistice_losing`, base 40). A dead-even war is the most
    ordinary state a truce is asked for in, and the preview promised a court
    twenty base points more willing than the send would find it.
    """

    def test_zero_is_the_winning_variant(self, board, monkeypatch):
        from backend.game_logic import diplomacy as D
        monkeypatch.setattr(D, "get_war_score_for", lambda *a, **k: 0)
        assert D.armistice_variant_for(board, "France", "Austria") == \
            "armistice_winning"

    def test_the_sign_rule_is_strict(self, board, monkeypatch):
        from backend.game_logic import diplomacy as D
        monkeypatch.setattr(D, "get_war_score_for", lambda *a, **k: -1)
        assert D.armistice_variant_for(board, "France", "Austria") == \
            "armistice_losing"
        monkeypatch.setattr(D, "get_war_score_for", lambda *a, **k: 1)
        assert D.armistice_variant_for(board, "France", "Austria") == \
            "armistice_winning"

    def test_no_site_re_implements_it(self):
        """The wizard/preview sites must CALL the helper, not carry a fourth
        copy of the comparison — which is how they came to disagree."""
        src = _read("backend/game_logic/diplomacy.py")
        assert 'if (get_war_score_for(world, player, target_nation) > 0)' not in src
        assert src.count('armistice_variant_for(') >= 4


class TestTheTruceDoesNotFreezeTheScore:
    """Ratifying WAR->ARMISTICE runs `cleanup_war_end`, which POPS
    war_scores / battle_records / decisive_battles for the pair — every battle
    won before the truce is amnestied, permanently. The decision surface said
    the score "freezes": the opposite of the mechanic, at the moment of
    deciding."""

    def _block(self):
        src = _read("backend/game_logic/diplomacy.py")
        block = src[src.index('snapshot["armistice_mechanics"]'):]
        return block[:block.index("return snapshot")]

    def test_the_false_promise_is_gone(self):
        assert "war score freezes" not in _code_only(self._block())

    def test_and_what_replaces_it_is_true(self):
        block = _code_only(self._block())
        assert "struck from the war" in block
        assert "campaign ledger" in block, (
            "PT-J2's ledger genuinely survives the truce, so the sentence "
            "must name both halves or it trades one falsehood for another")

    def test_the_mechanic_it_describes_is_real(self, board):
        """Falsifiable: the score really is popped, so the new copy is not
        describing a bug that has since been fixed."""
        from backend.game_logic.diplomacy import cleanup_war_end
        key = board._make_diplo_key("France", "Austria")
        board.war_scores = {key: 42}
        cleanup_war_end(board, key)
        assert key not in board.war_scores


class TestTheSeatNeedsTheCapital:
    def test_an_occupied_capital_seats_nobody(self, board):
        """`sovereign_seat_bonus` read the capital's NAME and never its
        controller, while its own caller charges -1 for the lost capital three
        lines above — so an enemy-held Paris cost a DP and paid one back."""
        from backend.game_logic.diplomacy import sovereign_seat_bonus
        sovereign = next((m for m in board.marshals.values()
                          if getattr(m, "is_sovereign", False)
                          and m.nation == board.player_nation), None)
        if sovereign is None:
            pytest.skip("no sovereign on this board")
        capital = board.get_nation_capital(board.player_nation)
        sovereign.location = capital
        assert sovereign_seat_bonus(board, board.player_nation) == 1
        board.get_region(capital).controller = "Austria"
        assert sovereign_seat_bonus(board, board.player_nation) == 0


class TestTheGuarantorIsNotBrandedForItsWardsWar:
    def test_the_aggressor_test_is_applied(self):
        """A guarantee is a promise to DEFEND. The loop walked every war the
        ward was in and branded the guarantor for all of them, so a ward that
        DECLARED an offensive war dragged its protector's name through the mud
        for not joining an attack it never promised to make — and
        `guarantee_abandoned` is the strongest casus belli in the system."""
        src = _read("backend/game_logic/instruments.py")
        body = src[src.index(
            "        for attacker in world.get_nations_at_war_with(protected):"):]
        body = body[:body.index("        if voided:")]
        assert "_pair_aggressor(world, protected, attacker) == protected" in body
        assert body.index("_pair_aggressor(world, protected, attacker)") < \
            body.index("if turn - max(war_start, pledged)"), (
            "the attribution test must precede the grace/branding arithmetic")


class TestACrisisThatBecameAWar:
    def test_the_cause_exists_in_both_copy_tables(self):
        from backend.game_logic.war_council import (
            _CRISIS_CAUSE_COPY, _CRISIS_CAUSE_SHORT, crisis_cause_phrase,
        )
        assert "war_joined" in _CRISIS_CAUSE_COPY
        assert "war_joined" in _CRISIS_CAUSE_SHORT
        assert crisis_cause_phrase("war_joined") != crisis_cause_phrase("starved"), (
            "the July-25 review found three causes degraded to the `starved` "
            "phrase; a new cause must not repeat it")

    def test_already_at_war_closes_the_crisis_before_the_stall_counter(self):
        src = _read("backend/game_logic/war_council.py")
        body = src[src.index("        preview = can_declare_war("):]
        body = body[:body.index('        if not record.get("coerce_recorded_turn")')]
        assert 'preview["reason"] == "already_at_war"' in body
        assert body.index("already_at_war") < body.index("stall_turns"), (
            "answered before the stall counter — which is what cooled a LIVE "
            "war on screen as 'the moment passed'")


class TestTheRoadHomeAfterATruce:
    def test_the_peace_that_ends_a_truce_opens_the_corridor(self):
        src = _read("backend/game_logic/diplomacy.py")
        assert ('elif old_state == "ARMISTICE" and new_state not in '
                '("WAR", "ARMISTICE"):') in src

    def test_the_war_arm_is_untouched(self):
        """§5's pin: a truce strands an army exactly as a peace does, so
        WAR->ARMISTICE must still open one. The fix ADDS an arm — a first cut
        that replaced the condition broke this, and the pin caught it."""
        src = _read("backend/game_logic/diplomacy.py")
        assert 'if old_state == "WAR" and new_state != "WAR":' in src

    def test_the_corridor_is_re_run_after_the_cessions(self):
        """`set_diplomatic_state` opens the corridor hundreds of lines before
        `_ratify_treaty` moves a province, so it judged stranding on the
        pre-cession map — a corps whose only road home is a province the
        treaty gives away read as connected, and (if nobody else was
        stranded) the provisional grant was rolled back entirely."""
        src = _read("backend/models/world_state.py")
        body = src[src.index("    def _ratify_treaty("):]
        body = body[:body.index("\n    def ", 10)]
        cede = body.index("region.controller = to_nation")
        reopen = body.index(
            "open_evacuation_corridor(self, proposer, target_nation)")
        assert reopen > cede, (
            "the re-run must sit AFTER the transfers or it re-asks the same "
            "question on the same map")


class TestTheIdleClockSurvivesASave:
    """`_acted_this_turn` was a setattr-created underscore attribute nothing
    serialized — and `test_serialization_enforcement` filters underscore
    names, so it was structurally invisible (the A10 class). A mid-turn
    save/load marked every marshal who had already marched as IDLE, and
    `idle_turns` drives the jealousy grievance threshold (>=3), the
    hostile-pair triggers (>=2) and vindication decay."""

    def test_the_flag_is_a_real_field(self, board):
        marshal = board.marshals[next(iter(board.marshals))]
        assert hasattr(marshal, "acted_this_turn")
        assert "acted_this_turn" in marshal.to_dict()

    def test_it_round_trips(self, board):
        from backend.models.marshal import Marshal
        marshal = board.marshals[next(iter(board.marshals))]
        marshal.acted_this_turn = True
        assert Marshal.from_dict(marshal.to_dict()).acted_this_turn is True

    def test_the_old_underscore_name_is_gone_from_every_reader(self):
        """Both halves: nothing writes it, and nothing reads it. A rename that
        leaves one reader behind is worse than no rename at all."""
        import glob
        for path in glob.glob("backend/**/*.py", recursive=True):
            assert "_acted_this_turn" not in _code_only(_read(path)), path

    def test_the_combat_flag_is_no_longer_wiped_on_load(self):
        src = _read("backend/save_manager.py")
        body = src[src.index("# Clear transient per-turn data"):]
        body = body[:body.index("world.threat_sources_this_turn")]
        assert "marshal.in_combat_this_turn = False" not in body


class TestAPrisonerIsNotDestroyed:
    def test_the_pursue_completion_distinguishes_the_two_fates(self):
        """`strength <= 0` is satisfied by two different fates, and the
        project distinguishes them everywhere else — a W6-7 prisoner stays in
        `world.marshals` at strength 0 with `captured_by` set."""
        src = _read("backend/commands/strategic.py")
        body = src[src.index("        # Target destroyed — or TAKEN."):]
        body = body[:body.index("        # ═══")]
        assert "captured_by" in body and "taken prisoner" in body
        assert "humanize_entity_name" in body, (
            "and the raw scenario key must not reach the player — "
            "`order.target` is 'ArchdukeCharles', the NPC-12 shape")


class TestTheInternedEmperor:
    def test_the_return_value_is_read(self):
        """`destroy_marshal` returns False when it CAPTURES instead of
        removing (the sovereign death-guard). This was the one removal call
        site that discarded it, so an Emperor whose safe passage lapsed was
        reported 'disarmed and interned' while the engine had taken him — the
        most consequential event in the game, announced as paperwork."""
        src = _read("backend/game_logic/withdrawal.py")
        body = src[src.index("def _intern("):]
        assert "removed = world.destroy_marshal(" in body
        assert "if removed is False:" in body
        assert "sovereign_captured" in body

    def test_the_type_it_emits_is_a_known_dispatch_class(self):
        from backend.game_logic.dispatch import HEADLINE_WEIGHTS
        assert "sovereign_captured" in HEADLINE_WEIGHTS


class TestTheFallOfTheCapitalIsPrinted:
    def test_the_gazette_asks_the_same_question_the_dispatch_does(self):
        """Slice 4's review widened the DISPATCH to `_on_our_side(prev)`, so
        an ally losing a liberated Paris fires "PARIS HAS FALLEN" at weight
        100 — while Le Moniteur keyed on `get_nation_capital(prev)`, found
        Munich, and printed nothing at all."""
        src = _read("backend/game_logic/gazette.py")
        assert "_is_our_capital_lost" in src
        body = src[src.index("_is_our_capital_lost = bool("):]
        body = body[:body.index("if region and (")]
        assert "not _taker_is_ours" in body, (
            "retaking our own capital must not print as its fall")


class TestTheTurnTheEnemyActedOn:
    def test_the_key_is_produced(self):
        """`TurnManager.end_turn` returns `turn_ended`; `_execute_end_turn`
        built a fresh dict and hand-copied a key set that omitted it — the
        exact PT-F1 seam its own comment documents thirty lines below."""
        src = _read("backend/commands/meta_executor.py")
        body = src[src.index('        result = {\n            "success": True,'):]
        body = body[:body.index("        if tactical_battle_report:")]
        assert '"turn_ended": turn_result.get("turn_ended")' in body


class TestTheLapseWarningCountsOnlyWhatLapses:
    def test_the_two_counts_answer_different_questions(self, board):
        dm = board.dialogue_manager
        dm.push({"type": "incoming_proposal", "nation": "Saxony",
                 "message": "x", "options": []})
        dm.push({"type": "incoming_settlement_offer", "nation": "Austria",
                 "message": "y", "options": []})
        assert dm.get_mailbox_count() == 2, "the badge counts the whole book"
        assert dm.get_lapsing_count() == 1, (
            "only the current-turn offer lapses — a persistent settlement "
            "offer survives the turn by design, so counting it made the "
            "warning claim a loss that could not happen, and when it was the "
            "only item, a stop nothing could clear")

    def test_the_client_gate_reads_the_lapsing_count(self):
        src = _read("godot-client/project-sovereign/scripts/main.gd")
        assert "var _current_lapsing_count" in src
        assert "if _current_lapsing_count > 0:" in src
        assert "% _current_lapsing_count" in src

    def test_the_badge_still_reads_the_full_count(self):
        src = _read("godot-client/project-sovereign/scripts/main.gd")
        assert 'open_envoys_button.text = "Open Envoys (%d)" % _current_envoy_count' in src


class TestEveryEndTurnPhrasingMeetsTheGate:
    def test_the_client_speaks_the_parsers_vocabulary(self):
        """The gate matched the literal "end turn" while `llm_client` reads
        end_turn from a SUBSTRING test over three keywords, so "next turn" and
        "end turn now" advanced the turn with no lapse warning at all."""
        src = _read("godot-client/project-sovereign/scripts/main.gd")
        body = src[src.index("func _is_end_turn_phrasing("):]
        body = body[:body.index("func _execute_end_turn():")]
        for phrase in ("end turn", "end_turn", "next turn"):
            assert phrase in body

    def test_the_backend_vocabulary_is_the_same_three(self):
        """Falsifiable join: if the parser grows a fourth phrasing this pin
        fails, rather than the gate silently going porous again."""
        src = _read("backend/ai/llm_client.py")
        line = [ln for ln in src.split("\n")
                if 'elif "end turn" in command_lower' in ln]
        assert line, "the parser arm moved — re-derive the client's list"
        assert line[0].count(" in command_lower") == 3


class TestTheDigitsGoToTheCommandLine:
    SCREENS = [
        "godot-client/project-sovereign/scripts/strategic_ledger.gd",
        "godot-client/project-sovereign/scripts/marshal_management.gd",
        "godot-client/project-sovereign/scripts/diplomatic_ledger.gd",
    ]

    def test_every_screen_yields_to_a_focused_text_field(self):
        """`Node._input` runs BEFORE GUI input reaches a focused control, and
        all three screens are non-modal — the terminal stays live behind them
        — so every bare digit typed into the command line was eaten and
        `set_input_as_handled()` stopped it arriving. "recruit 5000 infantry"
        became "recruit  infantry" plus three tab switches."""
        for path in self.SCREENS:
            src = _read(path)
            body = src[src.index("func _input(event):"):]
            body = body[:body.index("\n\n\n")] if "\n\n\n" in body else body
            assert "gui_get_focus_owner()" in body, path
            assert "is LineEdit" in body, path
            assert body.index("gui_get_focus_owner()") < body.index("KEY_1"), path


class TestTheCaptureQuestionDoesNotEatTheTurn:
    def test_an_end_turn_response_is_told_first(self):
        """A capture question mounted DURING end-turn processing arrives on
        the SAME response as the enemy phase, the strategic reports and the
        Morning Dispatch — and the capture route matched first, returned, and
        `_display_result` never ran. The player was asked to sack or secure a
        town while the entire report of the turn that took it vanished."""
        src = _read("godot-client/project-sovereign/scripts/main.gd")
        body = src[src.index("func _response_has_capture_choice_route("):]
        body = body[:body.index("func _route_capture_choice_response(")]
        assert 'response.has("enemy_phase")' in body
        assert "pending_capture_response = response" in body
        assert "return false" in body

    def test_and_raised_when_control_returns(self):
        src = _read("godot-client/project-sovereign/scripts/main.gd")
        assert "func _show_pending_capture_choice() -> bool:" in src
        body = src[src.index("func _show_pending_dispatch():"):]
        body = body[:body.index("func _display_turn_advance(")]
        assert "_show_pending_capture_choice()" in body, (
            "the dispatch is the last thing shown before control returns — "
            "the NA-6b stash-and-raise idiom this file already uses")


class TestTheInterruptTailShowsTheDispatch:
    def test_the_ordinary_exit_calls_it(self):
        """The end-turn route that passes through an input-requiring
        interrupt early-returns out of BOTH `_on_enemy_phase_dismissed` and
        `_on_strategic_report_dismissed` ahead of their own
        `_show_pending_dispatch()` calls — so on exactly the turns that
        produced an interrupt worth stopping for, the briefing was stashed and
        never shown. The redemption arm already knew to call it."""
        src = _read("godot-client/project-sovereign/scripts/main.gd")
        body = src[src.index("func _process_next_interrupt():"):]
        body = body[:body.index("func _show_clarification_popup(")]
        tail = body[body.index("# All interrupts processed"):]
        assert "_show_pending_dispatch()" in tail


class TestTheWorldSwapGoesQuiet:
    def test_the_in_scene_swap_sweeps_audio(self):
        """`hide_all()` raw-hides every popup WITHOUT running its close
        handler, so neither ownership seam fires and the one-shots — children
        of the AudioManager singleton, not of any scene — ring on into the
        freshly loaded campaign. UX23-B added this sweep for the main-menu
        path; the in-scene swap never got it."""
        src = _read("godot-client/project-sovereign/scripts/main.gd")
        body = src[src.index("func _reset_frontend_state_for_world_swap("):]
        body = body[:body.index("\nfunc ")]
        assert "AudioManager.stop_all_cues()" in body
        assert "AudioManager.stop_all_loops()" in body
        assert body.index("dialog_manager.hide_all()") < \
            body.index("AudioManager.stop_all_cues()")


class TestTheDamageAnnouncesItself:
    def test_the_producer_and_the_renderer_are_joined(self):
        """The [V-6] slice added the `buildings_damaged` producer so "the
        damage announces itself" and never made the renderer join, so a
        wrecked market arrived as the anonymous priority pill "INF"."""
        from backend.notifications import BUILDINGS_DAMAGED
        src = _read("godot-client/project-sovereign/scripts/notification_bar.gd")
        icons = src[src.index("const TYPE_ICONS = {"):]
        icons = icons[:icons.index("}")]
        assert f'"{BUILDINGS_DAMAGED}"' in icons


class TestTheLevyPriceIsThePriceHere:
    def test_the_payload_carries_a_per_region_price(self, board):
        summary = board.get_filtered_game_state_summary()
        regions = summary.get("map_data") or {}
        priced = [v.get("recruit_price_here") for v in regions.values()
                  if isinstance(v, dict) and v.get("recruit_price_here")]
        assert priced, "no province ships a levy price"

    def test_it_differs_from_the_capitals_rate(self, board):
        """The measured shape: the panel quoted 654g (the capital's) beside
        chips that charge 872g in Rhineland — a third more than the number the
        player read while choosing."""
        from backend.commands.economy_executor import get_levy_status
        capital_price = int(get_levy_status(board, "France")["infantry_price"])
        summary = board.get_filtered_game_state_summary()
        regions = summary.get("map_data") or {}
        prices = {v.get("recruit_price_here") for v in regions.values()
                  if isinstance(v, dict) and v.get("recruit_price_here")}
        assert prices - {capital_price}, (
            "if no province differs from the capital the defect would be "
            "invisible — this pin exists because they do differ")

    def test_the_panel_reads_it(self):
        src = _read("godot-client/project-sovereign/scripts/region_panel.gd")
        body = src[src.index("var levy = _map_node.levy_status"):]
        body = body[:body.index("action_rows.append")]
        assert 'data.get("recruit_price_here", 0)' in body
        assert "foot here" in body


class TestTheDisabledRouteIsRefusedWhenTyped:
    def test_the_gate_runs_at_execution_not_only_at_render(self):
        """IGR-D Q2(b) disabled the bilateral substitute when the draft holds
        a settlement-tier identity clause — at option-RENDER time only. The
        greyed-out row was fully executable by typing its number, and the
        drafting the gate exists to protect was thrown away after all."""
        src = _read("backend/game_logic/settlement_actions.py")
        body = src[src.index("def _handle_pair_peace_substitute_action("):]
        body = _code_only(
            body[:body.index("    # G4F-8: the substitute is no longer")])
        assert "pair_substitute_settlement_tier_block" in body
        assert body.index("pair_substitute_settlement_tier_block") < \
            body.index("evaluate_pair_peace_substitute_eligibility"), (
            "the draft-aware gate must run BEFORE the eligibility check that "
            "cannot see the draft")


class TestTheCommonPeaceRecordsThePairsOwnClauses:
    def test_a_third_courts_clause_does_not_ride_into_every_pair(self):
        """The arm read `term_to == proposer_member and term_from` — ANY
        clause pointing at the leader, from ANY court — so in a settlement
        where France covers Austria AND Prussia, Prussia's indemnity was
        written into the France-Austria record too."""
        src = _read("backend/game_logic/settlement_ratify.py")
        body = src[src.index("        for term in all_terms:"):]
        body = _code_only(body[:body.index("        treaty_type = {")])
        assert "term_to == proposer_member and term_from" not in body
        assert "term_from == proposer_member and term_to == covered_enemy" in body, (
            "and the leader's own sweeteners — the province that buys the "
            "signature — had no arm at all and were dropped from the record")


class TestTheRansomedMarshalComesHomeSomewhereReal:
    def test_an_occupied_capital_is_not_a_spawn(self, board):
        """`get_nation_capital` returns the AUTHORED capital with no
        controller check, so a ransomed marshal was set down inside a capital
        the enemy holds — standing on hostile soil he could not legally have
        marched to."""
        src = _read("backend/models/world_state.py")
        body = src[src.index("    def release_captured_marshal("):]
        body = body[:body.index("\n    def ", 10)]
        assert "find_safe_spawn(marshal)" in body
        assert body.index("get_nation_capital(marshal.nation)") < \
            body.index("find_safe_spawn(marshal)")


class TestTheRecklessChargeNamesTheRightNation:
    def test_a_formed_nation_is_not_billed_under_its_dead_name(self):
        """NA-6 §11.8-3. The maintained sibling in the executor pipeline uses
        `formed_display_name`; this copy humanised the raw tag, which also
        mangles "KingdomOfItaly" into "Kingdom Of Italy".

        (The TALLY half of the same fix has its own class below — this pin was
        the weaker of the two and the mutation sweep found it inert, because
        reverting the assignment left the words in the surrounding lines.)"""
        src = _read("backend/models/world_state.py")
        body = src[src.index("                # EC-W3: The Butcher's Bill"):]
        body = _code_only(body[:body.index("                if charge_blocked:")])
        assert "formed_display_name" in body
        assert "humanize_entity_name" not in body


# ══════════════════════════════════════════════════════════════════════════
# The mutation sweep's five INERT pins, replaced with binding ones.
#
# Every one was a source-substring pin: reverting the production line left the
# searched-for words in place (in the very comment explaining the fix, or in a
# sibling line), so the pin passed either way. These are behavioural.
# ══════════════════════════════════════════════════════════════════════════


class TestAPrisonerIsNotDestroyedBehaviour:
    def test_the_completion_says_TAKEN_not_destroyed(self, board):
        """The source pin was inert — reverting the fate branch left the words
        "captured_by" and "taken prisoner" in the block, so it passed either
        way. This runs the arm."""
        from backend.commands.executor import CommandExecutor
        from backend.commands.strategic import StrategicOrderProcessor
        from backend.models.marshal import StrategicOrder
        proc = StrategicOrderProcessor(CommandExecutor())
        hunter = board.get_marshal("Ney")
        quarry = next(m for m in board.marshals.values()
                      if m.nation != board.player_nation and m.strength > 0
                      and board.is_at_war(board.player_nation, m.nation))
        board.capture_marshal(quarry, board.player_nation)
        order = StrategicOrder(
            command_type="PURSUE", target=quarry.name,
            target_type="marshal", started_turn=int(board.current_turn),
            original_command=f"Ney, pursue {quarry.name}",
            issued_turn=int(board.current_turn) - 1)
        hunter.strategic_order = order
        result = proc._execute_pursue(hunter, board, {"world": board})
        message = str((result or {}).get("message", ""))
        assert "destroyed" not in message.lower(), message
        assert "prisoner" in message.lower(), message

    def test_a_truly_destroyed_quarry_still_reads_destroyed(self, board):
        """The other half of the same branch — a fate test that only ever
        answers one way is not a fate test."""
        from backend.commands.executor import CommandExecutor
        from backend.commands.strategic import StrategicOrderProcessor
        from backend.models.marshal import StrategicOrder
        proc = StrategicOrderProcessor(CommandExecutor())
        hunter = board.get_marshal("Ney")
        quarry = next(m for m in board.marshals.values()
                      if m.nation != board.player_nation and m.strength > 0
                      and board.is_at_war(board.player_nation, m.nation))
        quarry.strength = 0
        order = StrategicOrder(
            command_type="PURSUE", target=quarry.name,
            target_type="marshal", started_turn=int(board.current_turn),
            original_command=f"Ney, pursue {quarry.name}",
            issued_turn=int(board.current_turn) - 1)
        hunter.strategic_order = order
        result = proc._execute_pursue(hunter, board, {"world": board})
        assert "destroyed" in str((result or {}).get("message", "")).lower()


class TestTheDisabledRouteIsRefusedWhenTypedBehaviour:
    def test_a_draft_holding_vassalage_refuses_the_substitute(self, board):
        """The source pin was inert — reverting `if _tier_block:` to
        `if False:` left the call and the ordering in place. This calls the
        handler and reads its answer."""
        from backend.game_logic.settlement_actions import (
            _handle_pair_peace_substitute_action,
        )
        dialogue = {
            "type": "settlement_confirm",
            "war_id": "w1",
            "selected_target_nation": "Prussia",
            "settlement_terms": [
                {"type": "vassalage", "from": "Prussia", "to": "France"},
            ],
        }
        result = _handle_pair_peace_substitute_action(
            board, action="seek_bilateral_peace", dialogue=dialogue)
        assert result.get("success") is False
        assert result.get("error") == "settlement_tier_clause_blocks_substitute"
        assert str(result.get("error_display") or "") != "", (
            "a refusal that does not state its reason is the silent discard "
            "the gate exists to prevent")

    def test_a_plain_draft_is_not_blocked_by_this_arm(self, board):
        """The negative control: the gate must not refuse every substitute.
        (A plain draft may still be refused by the ELIGIBILITY check below it —
        what matters here is that it is not refused by the TIER block.)"""
        from backend.game_logic.settlement_actions import (
            _handle_pair_peace_substitute_action,
        )
        dialogue = {
            "type": "settlement_confirm",
            "war_id": "w1",
            "selected_target_nation": "Prussia",
            "settlement_terms": [
                {"type": "gold_indemnity", "from": "Prussia", "to": "France",
                 "amount": 500},
            ],
        }
        result = _handle_pair_peace_substitute_action(
            board, action="seek_bilateral_peace", dialogue=dialogue)
        assert result.get("error") != "settlement_tier_clause_blocks_substitute"


class TestTheRecklessChargeBillIsTalliedBehaviour:
    def test_the_tally_is_written_where_the_banner_reads_it(self):
        """The source pin was inert — the words survived in the comment and in
        the `_tally = getattr(...)` line above the assignment. Anchor on the
        ASSIGNMENT, which is the line that does the work."""
        src = _read("backend/models/world_state.py")
        body = src[src.index("                # EC-W3: The Butcher's Bill"):]
        body = _code_only(body[:body.index("                if charge_blocked:")])
        # ALL whitespace, not just spaces: `_code_only` re-emits tokens and the
        # original line wraps inside `int(...)`, so a space-only strip leaves a
        # newline in the middle of the expression and the pin never matches.
        flat = "".join(body.split())
        assert "_tally[_m_nation]=int(_tally.get(_m_nation,0))+_bill" in flat, (
            "the debit without the tally is the whole defect: money leaves "
            "the chest and the end-turn banner hides it in 'Other'")


class TestAQuestionIsNotAnOrderInLiveMode:
    """The mock parser routes EVERY interrogative to `help`, which the
    non-order set already covers — so the sweep found the question half of the
    gate inert, and it is, against mock. It is not redundant: in live mode the
    model may resolve a question to a real action verb, and then only the
    question test stands between "can you march to Frankfurt?" and a standing
    order. This drives that path by making the parse resolve to `move`."""

    def test_a_question_resolving_to_a_real_verb_still_issues_nothing(
            self, board, monkeypatch, parser):
        import contextlib
        import io as _io
        from backend.ai import llm_client as LC

        real = parser.llm.parse_command

        def _as_live_move(text, game_state=None, *a, **k):
            out = real(text, game_state, *a, **k)
            if isinstance(out, dict) and "march" in text.lower():
                out = dict(out, action="move", marshal="Lannes",
                           target="Frankfurt", mode="anthropic")
            return out

        monkeypatch.setattr(parser.llm, "parse_command", _as_live_move)
        before = board.actions_remaining
        buf = _io.StringIO()
        with contextlib.redirect_stdout(buf):
            parsed = parser.parse(
                "Lannes, can you march to Frankfurt?", {"world": board}, board)
        assert (parsed.get("command") or {}).get("action") == "move", (
            "the fixture must actually reach the live-shaped branch, or this "
            "pin tests nothing")
        assert not parsed.get("is_strategic"), (
            "a question resolving to a real verb must still issue no standing "
            "order — the half of the gate mock mode cannot exercise")
        assert board.actions_remaining == before


# ══════════════════════════════════════════════════════════════════════════
# REV-X1 — the assurance harness reported the game wrongly
#
# Filed unfixed in the first pass with an explicitly-unproven hypothesis that
# blamed an id()-backed ordering "on the AI-AI proposal path". THE HYPOTHESIS
# WAS WRONG and the record is corrected: the game is deterministic — a clean
# 40-turn driver snapshotting gold, relations, marshals, controllers,
# manpower, refusals, cooldowns and war intents is byte-identical cold vs
# warm. What varied was the harness's REPORT of it.
#
# `RunCapture._drain_events` answered "have I already reported this event?"
# with `id(e)`. `id()` is unique only among LIVE objects, and the file chose
# addresses PRECISELY because the 500-cap evicts — which is what makes them
# unsound: an evicted event is freed, CPython recycles its address, and the
# next event dict allocated there carries an id the seen-set already holds,
# so a genuinely new event is dropped from the digest. Compiling the backend
# changes the heap layout, which is why the failure tracked a cold
# __pycache__ and why the FIRST of two child processes was always the odd one.
# ══════════════════════════════════════════════════════════════════════════


class _StubWorld:
    """The minimum `RunCapture.__init__` reads."""

    def __init__(self):
        self.player_nation = "France"
        self.marshals = {}
        self.event_log = []
        self.war_instances = {}
        self.dialogue_manager = None
        self.pending_dispatch_events = []


class TestTheEventDrainCannotBeFooledByARecycledAddress:

    def _capture(self):
        import sys
        sys.path.insert(0, ".")
        from tools.ai_v_sweep import RunCapture
        world = _StubWorld()
        return RunCapture(world), world

    def test_the_seen_map_pins_the_objects_it_has_seen(self):
        """The load-bearing assertion, and the one the old code fails.

        After the log has turned over completely, the map must still hold
        every event it has ever reported — that is what keeps their addresses
        reserved. The old implementation REBUILT the set from the live log
        each turn, so it held 1, and the two evicted events' addresses were
        free to be handed to a future event that would then be read as
        already-seen.
        """
        import gc
        cap, world = self._capture()

        world.event_log[:] = [{"type": "a", "turn": 1},
                              {"type": "b", "turn": 1}]
        assert len(cap._drain_events()) == 2

        world.event_log[:] = []          # the 500-cap evicts
        gc.collect()
        world.event_log[:] = [{"type": "c", "turn": 2}]
        assert len(cap._drain_events()) == 1, (
            "a fresh event after a full turnover must still be reported")

        assert len(cap._seen_events) == 3, (
            "the map must ACCUMULATE and pin: 2 evicted + 1 live. Rebuilding "
            "it from the live log is the defect — it releases exactly the "
            "addresses the id test depends on")

    def test_every_id_in_the_map_belongs_to_a_live_object_it_holds(self):
        """The invariant stated directly: an id is only a valid identity while
        its object is alive, so the map must BE the thing keeping it alive."""
        import gc
        cap, world = self._capture()
        world.event_log[:] = [{"type": "a", "turn": 1}]
        cap._drain_events()
        world.event_log[:] = []
        gc.collect()
        for key, obj in cap._seen_events.items():
            assert id(obj) == key, (
                "the map's key must be the identity of the object it holds — "
                "a bare id set proves nothing once the object is freed")

    def test_an_unchanged_log_reports_nothing_twice(self):
        """The negative control: pinning must not turn the drain into a
        firehose that re-reports everything each turn."""
        cap, world = self._capture()
        world.event_log[:] = [{"type": "a", "turn": 1}]
        assert len(cap._drain_events()) == 1
        assert cap._drain_events() == []

    def test_the_control_arm_is_deterministic_from_a_cold_bytecode_cache(self):
        """The end-to-end proof, run as its own subprocess pair.

        Skipped by default because it costs two 40-turn runs; the unit pins
        above are the standing guard. Enable with REV_X1_E2E=1 when touching
        the drain.
        """
        import json
        import os
        import subprocess
        import sys
        if os.environ.get("REV_X1_E2E") != "1":
            pytest.skip("set REV_X1_E2E=1 to run the two-process check")
        sys.path.insert(0, ".")
        import tools.ai_v_sweep as sweep
        for root, dirs, _ in os.walk("backend"):
            for d in list(dirs):
                if d == "__pycache__":
                    subprocess.run(["rm", "-rf", os.path.join(root, d)])
        views = [
            json.dumps(sweep._control_view(
                sweep.spawn_run("historical", sweep.AMBIENT_K, 40)),
                sort_keys=True)
            for _ in range(3)
        ]
        assert len(set(views)) == 1
