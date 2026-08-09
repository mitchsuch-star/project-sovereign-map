"""Creative Audit CA9 — the August 8, 2026 played-campaign fix queue.

Record: `docs/audits/CREATIVE_AUDIT_2026_08_08.md` (authoritative);
rows: `docs/BUG_FIXES.md` §Creative Audit CA9.

The through-line these pins defend: **every system computes the right
answer and then tells the player a different one, and the divergence
always points the way that makes the player commit.** Where a fix could
be written either as a copy of the executor's rule or as a call to it,
these tests pin the CALL.
"""

from __future__ import annotations

import random
import re
from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.models.dialogue_manager import DialogueManager
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


@pytest.fixture
def executor():
    return CommandExecutor()


def _attack(world, executor, marshal_name, target):
    world.actions_remaining = 4
    random.seed(7)
    return executor.execute({
        "success": True,
        "command": {"type": "specific", "marshal": marshal_name,
                    "action": "attack", "target": target},
    }, {"world": world})


def _weaken(world, name, strength=6000):
    m = world.marshals[name]
    m.strength = strength
    return m


# ═══════════════════════════════════════════════════════════════════════
# F6 — the war-purpose hard stop is armed but never DELIVERED
#
# `war_purpose_selection` blocks every command. The client gates its whole
# popup route on `response.diplomatic_dialogue` (`main.gd:1617`), so a
# response that stages the dialogue without carrying it produces an
# INVISIBLE hard stop: the player sees nothing, and the next command —
# including `end turn` — comes back "I don't understand that choice,
# Sire. Options: 1=Conquest…" for a question never displayed. Four times
# in the CA9 campaign.
#
# `_execute_attack`'s undefended-territory gate (:3176) always stamped it;
# the three battle-advance sites did not.
# ═══════════════════════════════════════════════════════════════════════

class TestF6WarPurposeIsDelivered:
    """Every path that stages the hard stop must carry it on its result."""

    _KEYS = ("diplomatic_dialogue", "awaiting_diplomatic_response",
             "war_purpose_popup")

    def _assert_delivered(self, result, world, where):
        assert world.pending_diplomatic_dialogue is not None, (
            f"{where}: precondition broken — no dialogue was staged, so "
            f"this board no longer exercises the delivery seam")
        assert (world.pending_diplomatic_dialogue.get("type")
                == "war_purpose_selection"), where
        for key in self._KEYS:
            assert result.get(key), (
                f"{where}: staged a HARD STOP and returned without "
                f"'{key}' — the client renders no popup and every "
                f"subsequent command, including `end turn`, is swallowed")
        assert (result["diplomatic_dialogue"]
                is world.pending_diplomatic_dialogue), (
            f"{where}: delivered a COPY of the dialogue, not the live one")

    def test_main_battle_advance_delivers_the_dialogue(self, world, executor):
        """combat_executor.py:5410 — the Nassau shape played live."""
        mack = _weaken(world, "Mack")
        mack.location = "Nassau"
        assert world.get_region("Nassau").controller == "Hesse"

        result = _attack(world, executor, "Ney", "Mack")

        assert result.get("success"), result.get("message")
        self._assert_delivered(result, world, "main battle advance")

    def test_glorious_charge_delivers_the_dialogue(self, world, executor):
        """combat_executor.py:6323 — the charge door."""
        mack = _weaken(world, "Mack")
        mack.location = "Nassau"
        murat = world.marshals["Murat"]
        murat.location = "Rhineland"
        world.actions_remaining = 4
        random.seed(7)

        result = executor._combat._execute_glorious_charge(
            murat, "Mack", world, {"world": world})

        assert result.get("success"), result.get("message")
        if world.pending_diplomatic_dialogue is None:
            pytest.skip("charge did not reach the pursuit gate on this seed")
        self._assert_delivered(result, world, "glorious charge")

    def test_auto_bombardment_kill_delivers_the_dialogue(
            self, world, executor):
        """combat_executor.py:4489 — the auto-bombardment-kill exit.

        The board: a French gun adjacent to a neutral province destroys
        the last defender with preparatory fire, so the infantry lead
        advances into an already-empty enemy-held-but-neutral-owned
        province.
        """
        combat = executor._combat
        # Drive the shared helper directly: the auto-kill exit needs a
        # bombardment that lands exactly lethal, which is not reliably
        # reproducible from a seed. What must be pinned is that this
        # RETURN carries the staged dialogue.
        mack = _weaken(world, "Mack", 500)
        mack.location = "Nassau"
        popup = combat._stage_war_purpose_selection(world, "France", "Hesse")
        result = combat._attach_staged_war_purpose(
            {"success": True, "message": "x"}, world, popup)
        self._assert_delivered(result, world, "auto-bombardment kill")

    def test_helper_is_a_no_op_when_nothing_was_staged(self, world, executor):
        """The three sites call the helper unconditionally on their way
        out; an ordinary battle must stay byte-identical."""
        combat = executor._combat
        base = {"success": True, "message": "ordinary battle"}
        out = combat._attach_staged_war_purpose(dict(base), world, None)
        assert out == base

    def test_every_staging_site_routes_through_the_helper(self):
        """Falsifiability guard: a fourth site added later must not be
        able to stage the hard stop without delivering it.

        Counted structurally rather than by behaviour, because three of
        the four sites need a different battle shape to reach."""
        import inspect

        from backend.commands import combat_executor as ce

        src = inspect.getsource(ce)
        staged = src.count("self._stage_war_purpose_selection(")
        attached = src.count("_attach_staged_war_purpose(")
        # 4 staging sites; the helper is defined once and called 4 times
        # (3 battle-advance returns + the auto-kill probe's own path),
        # and `_stage_war_purpose_for_attack` inlines the same three keys.
        assert staged == 4, (
            f"{staged} war-purpose staging sites found, expected 4 — a new "
            f"one was added; wire it through _attach_staged_war_purpose")
        assert attached >= 4, (
            "a staging site is not paired with a delivery")

    def test_the_undefended_territory_gate_still_stamps_inline(self):
        """:3176 predates the helper and keeps its inline stamp. Pin it so
        a cleanup cannot delete the one site that always worked."""
        import inspect

        from backend.commands import combat_executor as ce

        src = inspect.getsource(ce.CombatExecutor._execute_attack)
        assert '"diplomatic_dialogue": world.pending_diplomatic_dialogue' in src
        assert '"awaiting_diplomatic_response": True' in src


class TestF6UnresolvedChoiceBackstop:
    """`_unresolved_choice_failure` re-attaches for the settlement family
    only. Widen it to every HARD_STOP_TYPE so the NEXT unwired dialogue
    type surfaces itself instead of locking the player out silently."""

    def _stage_and_answer(self, world, executor, garbage="march on Bohemia"):
        executor._combat._stage_war_purpose_selection(world, "France", "Hesse")
        return executor._diplomatic.handle_diplomatic_dialogue_response(
            garbage, {"world": world})

    def test_a_hard_stop_reattaches_itself_on_an_unresolvable_answer(
            self, world, executor):
        result = self._stage_and_answer(world, executor)
        assert result.get("success") is False
        assert result.get("diplomatic_dialogue") is not None, (
            "the hard stop refused the answer and re-attached nothing — the "
            "Godot popup hides itself when it responds, so the player is "
            "left at an invisible block")
        assert (result["diplomatic_dialogue"].get("type")
                == "war_purpose_selection")
        assert result.get("awaiting_diplomatic_response") is True

    def test_a_local_planning_dialogue_keeps_the_legacy_bare_refusal(
            self, world, executor):
        """Scope guard: only hard stops re-attach. A non-blocking dialogue
        must not start pushing itself back at the client."""
        world.dialogue_manager.replace({
            "type": "advisory",
            "message": "counsel",
            "options": [{"label": "Dismiss", "action": "dismiss"}],
            "turn_created": int(world.current_turn),
        })
        assert "advisory" not in DialogueManager.HARD_STOP_TYPES
        result = executor._diplomatic.handle_diplomatic_dialogue_response(
            "march on Bohemia", {"world": world})
        assert result.get("success") is False
        assert "diplomatic_dialogue" not in result


# ═══════════════════════════════════════════════════════════════════════
# The typed dialogue router — it never read the court the player named
#
# Live: with Prussia's proposal ACTIVE, `accept Portugal's proposal`
# signed a PERMANENT TREATY WITH PRUSSIA. The client-side guard for this
# exact class already shipped (W6-0's dialogue_id binding); the typed
# path — this game's premise — never got it.
# ═══════════════════════════════════════════════════════════════════════

def _incoming_proposal(nation, ptype="alliance"):
    """The shape `ai_diplomacy._build_incoming_proposal_dialogue` produces."""
    return {
        "type": "incoming_proposal",
        "target_nation": nation,
        "talleyrand_text": f"A proposal from {nation}.",
        "options": [
            {"label": "Accept", "action": "accept_ai_proposal"},
            {"label": "Reject", "action": "reject_ai_proposal"},
            {"label": "Counter-offer", "action": "counter_ai_proposal"},
        ],
        "context": {
            "proposal": {"type": ptype, "target_nation": nation},
            "source_nation": nation,
            "acceptance_score": 90,
            "proposal_type": ptype,
        },
        "turn_created": 1,
        "blocking": False,
    }


class TestTypedDialogueRouterReadsTheCourt:

    def _prussia_active(self, world):
        world.dialogue_manager.replace(_incoming_proposal("Prussia"))
        return world.pending_diplomatic_dialogue

    def test_the_live_case_accepting_portugal_never_answers_prussia(
            self, world, executor):
        self._prussia_active(world)
        before = dict(world.diplomatic_states)

        result = executor._diplomatic.handle_diplomatic_dialogue_response(
            "accept", {"world": world},
            raw_text="accept Portugal's proposal")

        # The damage first: NO treaty may be signed with anyone.
        assert dict(world.diplomatic_states) == before, (
            "the answer was applied to whichever dialogue was ACTIVE — this "
            "is how `accept Portugal's proposal` signed a PERMANENT TREATY "
            "with Prussia")
        assert result.get("success") is False
        assert result.get("court_mismatch") is True
        assert "Prussia" in result["message"], (
            "a refusal that does not name the court on the table teaches "
            "the player nothing")
        # The hard requirement from the memo: refuse AND say which court is
        # being answered.
        assert result.get("diplomatic_dialogue") is not None

    def test_naming_the_active_court_proceeds(self, world, executor):
        self._prussia_active(world)
        result = executor._diplomatic.handle_diplomatic_dialogue_response(
            "accept", {"world": world},
            raw_text="accept Prussia's proposal")
        assert result.get("court_mismatch") is not True

    def test_naming_no_court_proceeds_unchanged(self, world, executor):
        self._prussia_active(world)
        result = executor._diplomatic.handle_diplomatic_dialogue_response(
            "accept", {"world": world}, raw_text="accept")
        assert result.get("court_mismatch") is not True

    def test_naming_both_courts_proceeds_when_the_active_one_is_named(
            self, world, executor):
        """`reject Prussia's demand for Hanover` names two — the active
        court is one of them, so it is an answer, not a misdelivery."""
        self._prussia_active(world)
        result = executor._diplomatic.handle_diplomatic_dialogue_response(
            "reject", {"world": world},
            raw_text="reject Prussia's demand for Hanover")
        assert result.get("court_mismatch") is not True

    def test_a_province_that_shares_a_nation_tag_is_not_an_addressee(
            self, world, executor):
        """Under-refusing is the safe direction. Hanover is a province on
        this map as well as a court; a bare mention must not refuse."""
        self._prussia_active(world)
        result = executor._diplomatic.handle_diplomatic_dialogue_response(
            "accept", {"world": world},
            raw_text="accept, and we keep Hanover")
        assert result.get("court_mismatch") is not True

    def test_the_popup_path_is_untouched(self, world, executor):
        """The button route carries an action id and no raw text; the
        guard must be structurally unreachable for it."""
        self._prussia_active(world)
        result = executor._diplomatic.handle_diplomatic_dialogue_response(
            "reject_ai_proposal", {"world": world})
        assert result.get("court_mismatch") is not True

    def test_the_refusal_names_the_letter_book_when_the_court_is_queued(
            self, world, executor):
        world.dialogue_manager.replace(_incoming_proposal("Prussia"))
        world.dialogue_manager.push(_incoming_proposal("Portugal"))
        # Prussia stays ACTIVE; Portugal queues behind it.
        assert world.pending_diplomatic_dialogue.get(
            "target_nation") == "Prussia"

        result = executor._diplomatic.handle_diplomatic_dialogue_response(
            "accept", {"world": world},
            raw_text="accept Portugal's proposal")
        assert result.get("court_mismatch") is True
        assert "letter-book" in result["message"], result["message"]
        assert "Portugal" in result["message"]

    def test_demonym_addressing_is_read(self, world, executor):
        self._prussia_active(world)
        result = executor._diplomatic.handle_diplomatic_dialogue_response(
            "accept", {"world": world},
            raw_text="accept the Portuguese offer")
        assert result.get("court_mismatch") is True


class TestHardStopMatcherIsNoLongerABareSubstringScan:
    """`main.py`'s hard-stop arm scanned a fixed keyword list for bare
    substrings, and that list held ordinary game words."""

    def _staged(self, world, executor):
        executor._combat._stage_war_purpose_selection(world, "France", "Hesse")
        return world.pending_diplomatic_dialogue

    def test_send_a_marshal_somewhere_is_not_an_answer(self, world, executor):
        from backend.commands.dialogue_routing import match_dialogue_answer
        dlg = self._staged(world, executor)
        assert match_dialogue_answer(dlg, "send ney to bavaria") is None, (
            "'send' matched as a bare substring and was applied to the "
            "staged hard stop")

    def test_move_north_is_not_the_word_no(self, world, executor):
        from backend.commands.dialogue_routing import match_dialogue_answer
        dlg = self._staged(world, executor)
        assert match_dialogue_answer(dlg, "ney, move north") is None

    def test_garrison_paris_never_declares_a_war_of_conquest(
            self, world, executor):
        from backend.commands.dialogue_routing import match_dialogue_answer
        dlg = self._staged(world, executor)
        assert match_dialogue_answer(dlg, "garrison paris") is None

    def test_the_real_answers_still_resolve(self, world, executor):
        from backend.commands.dialogue_routing import match_dialogue_answer
        dlg = self._staged(world, executor)
        labels = [o.get("label", "") for o in dlg["options"]]
        assert labels, "the staged dialogue offers nothing to answer"
        for label in labels:
            assert match_dialogue_answer(dlg, label.lower()) is not None, (
                f"a verbatim option label '{label}' stopped resolving")
        # "back out" is the Back Out label; "no"/"reconsider" map onto its
        # action, which this dialogue does offer.
        assert match_dialogue_answer(dlg, "no") is not None
        assert match_dialogue_answer(dlg, "reconsider") is not None

    def test_a_verb_only_matches_when_the_dialogue_offers_that_action(
            self, world, executor):
        """The gate that makes the whole-word scan safe."""
        from backend.commands.dialogue_routing import match_dialogue_answer
        dlg = self._staged(world, executor)
        offered = {o.get("action") for o in dlg["options"]}
        assert "send_override" not in offered
        assert match_dialogue_answer(dlg, "send") is None
        # …and on a dialogue that DOES offer it, the same word lands.
        proposal = {
            "type": "proposal_confirm",
            "options": [{"label": "Send it", "action": "send_override"}],
        }
        assert match_dialogue_answer(proposal, "send") is not None

    def test_the_extracted_keyword_table_is_the_one_the_executor_uses(self):
        """Falsifiability: the table moved out of the executor; pin that
        the executor reads the moved copy rather than keeping a fork."""
        import inspect

        from backend.commands import diplomatic_executor as de
        from backend.commands.dialogue_routing import (
            DIALOGUE_ACTION_KEYWORDS,
        )

        src = inspect.getsource(de.DiplomaticExecutor
                                .handle_diplomatic_dialogue_response)
        assert "DIALOGUE_ACTION_KEYWORDS as action_map" in src
        assert "action_map = {" not in src, (
            "the inline table came back — two definitions of what a word "
            "means is the defect this collapsed")
        assert "accept" in DIALOGUE_ACTION_KEYWORDS


# ═══════════════════════════════════════════════════════════════════════
# N5 — the objection that never states its options
#
# "A pending objection blocks everything including free reads (`status`),
# never names the two words that clear it, and rejects plain English
# meaning one of them." `choices` was already in the payload and the
# sentence omitted it.
# ═══════════════════════════════════════════════════════════════════════

def _pending_objection(world, marshal="Davout", alternative=None):
    world.pending_objection = {
        "type": "major_objection",
        "marshal": marshal,
        "message": f"{marshal} objects.",
        "original_order": {"action": "attack", "marshal": marshal,
                           "target": "Bohemia"},
        "suggested_alternative": alternative,
        "alternative": alternative,
        "compromise": None,
    }
    return world.pending_objection


class TestN5ObjectionStatesItsOptions:

    def _blocked(self, world, executor, action="attack", **extra):
        cmd = {"type": "specific", "marshal": "Ney", "action": action}
        cmd.update(extra)
        return executor.execute(
            {"success": True, "command": cmd}, {"world": world})

    def test_the_block_names_the_two_words_that_clear_it(
            self, world, executor):
        _pending_objection(world)
        result = self._blocked(world, executor, target="Bohemia")

        assert result.get("success") is False
        msg = result["message"]
        assert "'trust'" in msg and "'insist'" in msg, (
            "the block told the player to 'settle the objection' and never "
            "named a single word that would settle it — while returning "
            f"those exact words in `choices`: {msg!r}")
        # shown == offered: the sentence is built from the payload list.
        for choice in result["choices"]:
            assert f"'{choice}'" in msg

    def test_a_third_road_is_named_when_it_exists(self, world, executor):
        _pending_objection(world, alternative={"action": "scout"})
        result = self._blocked(world, executor, target="Bohemia")
        assert "'compromise'" in result["message"]
        assert result["choices"] == ["trust", "insist", "compromise"]

    def test_free_reads_pass_the_block(self, world, executor):
        """A marshal standing on his dignity may not also stop the Emperor
        from reading the report that would decide the argument."""
        from backend.commands.executor import OBJECTION_FREE_READS

        for action in sorted(OBJECTION_FREE_READS):
            _pending_objection(world)
            result = executor.execute(
                {"success": True, "command": {"type": "general",
                                              "action": action}},
                {"world": world})
            assert "settle the objection" not in str(
                result.get("message", "")), (
                f"'{action}' is a pure read and was blocked by an objection")
            assert world.pending_objection is not None, (
                f"'{action}' cleared the objection — a read must not answer "
                f"the question")

    def test_a_free_read_costs_nothing_and_changes_nothing(
            self, world, executor):
        """The exemption is only safe because these five are pure."""
        _pending_objection(world)
        ap_before = int(world.actions_remaining)
        snapshot = world.to_dict()
        executor.execute(
            {"success": True, "command": {"type": "general",
                                          "action": "status"}},
            {"world": world})
        assert int(world.actions_remaining) == ap_before
        assert world.to_dict() == snapshot

    def test_an_order_is_still_blocked(self, world, executor):
        """The control arm — the block is still a block."""
        _pending_objection(world)
        result = self._blocked(world, executor, target="Bohemia")
        assert result.get("success") is False
        assert "settle the objection" in result["message"]

    def test_the_ai_is_never_blocked_by_the_players_objection(
            self, world, executor):
        _pending_objection(world)
        result = executor.execute({
            "success": True,
            "command": {"type": "specific", "marshal": "Mack",
                        "action": "fortify", "_autonomous_execution": True},
        }, {"world": world})
        assert "settle the objection" not in str(result.get("message", ""))


class TestN5PlainEnglishAnswers:
    """The exact-token gate rejected plain English meaning one of its own
    words. Nothing else can execute while an objection stands, so a line
    naming exactly one answer word is unambiguous."""

    @staticmethod
    def _answers(text):
        return [w for w in ("trust", "insist", "compromise")
                if re.search(rf"(?<![a-z]){w}(?![a-z])", text.strip().lower())]

    @pytest.mark.parametrize("line", [
        "I trust him",
        "trust Davout",
        "insist on it",
        "very well, insist",
        "let us compromise",
    ])
    def test_plain_english_resolves_to_exactly_one_answer(self, line):
        assert len(self._answers(line)) == 1, (
            f"'{line}' must resolve to exactly one objection answer")

    @pytest.mark.parametrize("line", [
        "Ney, march on Bohemia",
        "status",
        "distrusting the marshals",   # 'trust' inside a longer word
        "insistence is not a plan",   # 'insist' inside a longer word
    ])
    def test_ordinary_lines_are_not_objection_answers(self, line):
        assert self._answers(line) == [], (
            f"'{line}' was read as an objection answer")

    def test_two_answer_words_stay_ambiguous(self):
        assert len(self._answers("trust him or insist?")) == 2

    def test_main_routes_the_plain_english_form(self):
        """Pin the wiring, not just the predicate."""
        import inspect

        import backend.main as main_module

        src = inspect.getsource(main_module.execute_command)
        assert "_objection_pending" in src
        assert "Plain-English objection answer" in src


class TestN5OneHelperForEveryBlockingSurface:

    def test_format_answer_words_shape(self):
        from backend.commands.dialogue_routing import format_answer_words
        assert format_answer_words(
            ["trust", "insist"]) == "'trust' or 'insist'"
        assert format_answer_words(
            ["trust", "insist", "compromise"]
        ) == "'trust', 'insist' or 'compromise'"
        assert format_answer_words(["plunder"]) == "'plunder'"
        assert format_answer_words([]) == ""

    def test_format_numbered_options_reads_the_live_dialogue(
            self, world, executor):
        from backend.commands.dialogue_routing import format_numbered_options
        executor._combat._stage_war_purpose_selection(world, "France", "Hesse")
        rendered = format_numbered_options(world.pending_diplomatic_dialogue)
        labels = [o["label"]
                  for o in world.pending_diplomatic_dialogue["options"]]
        assert rendered.startswith("1=")
        for i, label in enumerate(labels):
            assert f"{i + 1}={label}" in rendered

    def test_every_blocking_surface_uses_the_helper(self):
        """Falsifiability: four surfaces named the words by hand; they now
        share one. A fifth hand-rolled join must not creep back."""
        import inspect

        import backend.main as main_module
        from backend.commands import diplomatic_executor as de
        from backend.commands import executor as ex
        from backend.commands import meta_executor as me

        for module, needle in (
            (ex, "format_answer_words"),
            (me, "format_answer_words"),
            (main_module, "format_answer_words"),
            (de, "format_numbered_options"),
        ):
            assert needle in inspect.getsource(module), (
                f"{module.__name__} stopped using {needle}")
        assert "repr(c) for c in" not in inspect.getsource(main_module), (
            "a hand-rolled choice join came back")
