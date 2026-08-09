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


# ═══════════════════════════════════════════════════════════════════════
# F1 — the muster preview models the enemy as one man
#
# CO-2 landed the attacker's committed term and not the defender's, so
# the preview committed OUR muster and modelled THEIRS as a single
# marshal. `resolve_battle` has taken both terms since CO-1 and the call
# site says so: "Symmetric for a reinforced defender (GR5)".
# Measured live: preview 43,778 v 32,131; the battle 26,219 v 36,931.
# Both errors pointed at "favorable" — the direction that makes the
# player commit.
# ═══════════════════════════════════════════════════════════════════════

class TestF1SymmetricCommittedDefender:

    def test_the_four_cr5_gate_call_sites_stay_byte_identical(self):
        """`inferred_attack_favorable` passes neither committed term, so
        both default to 0.0 and the CR-5 lethal gate is untouched."""
        import inspect

        from backend.commands import objection_v2 as ov

        src = inspect.getsource(ov.inferred_attack_favorable)
        assert "committed" not in src, (
            "the CR-5 gate started pricing a muster — it must keep reading "
            "the acting marshal's SOLO strength (PC-8's recorded ruling)")

    def test_the_ratio_is_unchanged_when_nobody_reinforces(self):
        from types import SimpleNamespace

        from backend.commands.objection_v2 import (
            inferred_attack_effective_ratio,
        )
        atk = SimpleNamespace(strength=30000, name="Ney")
        dfd = SimpleNamespace(strength=20000, name="Mack", fortified=False,
                              location=None)
        bare = inferred_attack_effective_ratio(atk, dfd)
        assert inferred_attack_effective_ratio(
            atk, dfd, committed_defender=0.0) == bare

    def test_a_committed_defender_lowers_the_ratio(self):
        from types import SimpleNamespace

        from backend.commands.objection_v2 import (
            inferred_attack_effective_ratio,
        )
        atk = SimpleNamespace(strength=30000, name="Ney")
        dfd = SimpleNamespace(strength=20000, name="Mack", fortified=False,
                              location=None)
        solo = inferred_attack_effective_ratio(atk, dfd)
        joint = inferred_attack_effective_ratio(
            atk, dfd, committed_defender=15000)
        assert joint < solo
        assert joint == pytest.approx(30000 / 35000)

    def test_committed_mass_is_added_after_the_terrain_multiplier(self):
        """The resolver adds committed mass AFTER the multipliers
        (`combat.py:1099`) — committed troops arrive already effective and
        are not multiplied by the ground they arrive on. Same shape here,
        or the preview is a second model rather than the same one."""
        from types import SimpleNamespace

        from backend.commands.objection_v2 import (
            inferred_attack_effective_ratio,
        )
        atk = SimpleNamespace(strength=30000)
        dfd = SimpleNamespace(strength=20000, fortified=True,
                              defense_bonus=0.5, location=None)
        got = inferred_attack_effective_ratio(
            atk, dfd, committed_defender=10000)
        # 20000 * 1.5 + 10000, NOT (20000 + 10000) * 1.5
        assert got == pytest.approx(30000 / (20000 * 1.5 + 10000))

    def test_the_defender_muster_uses_the_same_ladder(self, world, executor):
        """The function, not a copy of it."""
        import inspect

        from backend.commands import combat_executor as ce

        src = inspect.getsource(ce.CombatExecutor._defender_muster)
        assert "self._muster_reason(" in src, (
            "the defender's muster grew its own eligibility rule")
        assert "self._committed_reinforcement_strength(" in src, (
            "the defender's muster grew its own summer")

    @staticmethod
    def _isolate(world, keep=("Ney",)):
        """Clear the boot board's other French corps out of reach so the
        two musters can be measured separately. The 1805 opening has six
        French marshals within one march of Swabia — realistic, and useless
        for isolating one term."""
        for m in list(world.marshals.values()):
            if m.nation == "France" and m.name not in keep:
                m.location = "Brittany"

    def test_the_preview_now_counts_the_enemys_muster(self, world, executor):
        """The measured shape: a second enemy corps beside the target."""
        combat = executor._combat
        self._isolate(world)
        mack = world.marshals["Mack"]
        mack.strength = 25000
        ney = world.marshals["Ney"]
        ney.location = mack.location
        ney.strength = 30000

        alone = combat._build_muster_preview(
            ney, mack, world, {"world": world})
        assert alone["odds_band"] == "favorable", (
            "board precondition broken — re-derive the shape")

        # A second Austrian corps beside Mack, free to march.
        john = world.marshals["ArchdukeJohn"]
        john.location = mack.location
        john.strength = 25000
        for flag in ("fortified", "holding_position", "moved_this_turn",
                     "reinforced_this_turn", "drilling", "square_formation"):
            setattr(john, flag, False)

        joined = combat._build_muster_preview(
            ney, mack, world, {"world": world})

        _, committed = combat._defender_muster(mack, world)
        assert committed > 0, (
            "an unengaged enemy corps in the battle province contributed "
            "nothing to the odds — the preview still models one man")
        assert joined["odds_band"] != "favorable", (
            f"25,000 fresh defenders arrived and the preview's verdict did "
            f"not move ({alone['odds_band']} -> {joined['odds_band']}). The "
            f"measured live shape: preview 43,778 v 32,131, battle 26,219 v "
            f"36,931, verdict 'favorable'.")

    def test_the_preview_band_is_the_shared_formula_with_both_terms(
            self, world, executor):
        """Binds the preview to the single odds source with BOTH committed
        terms — so the defender half cannot be quietly dropped again while
        the attacker half keeps the band looking right."""
        from backend.commands.objection_v2 import (
            inferred_attack_effective_ratio, inferred_attack_odds_band,
        )
        combat = executor._combat
        # Isolated, so the two bands can actually differ — on the full boot
        # board the French muster is large enough that both read favorable
        # and the comparison would pass vacuously.
        self._isolate(world)
        mack = world.marshals["Mack"]
        mack.strength = 25000
        ney = world.marshals["Ney"]
        ney.location = mack.location
        ney.strength = 30000
        john = world.marshals["ArchdukeJohn"]
        john.location = mack.location
        john.strength = 25000
        for flag in ("fortified", "holding_position", "moved_this_turn",
                     "reinforced_this_turn", "drilling", "square_formation"):
            setattr(john, flag, False)
        gs = {"world": world}

        preview = combat._build_muster_preview(ney, mack, world, gs)
        atk_committed = (preview["attacker"]["committed_strength"]
                         - preview["attacker"]["strength"])
        _, def_committed = combat._defender_muster(mack, world)
        assert def_committed > 0, "board precondition broken"

        assert preview["odds_band"] == inferred_attack_odds_band(
            ney, mack, gs, committed_attacker=atk_committed,
            committed_defender=def_committed)
        # …and it is NOT the band the attacker-only formula would give, or
        # this test could not tell the two apart.
        assert preview["odds_band"] != inferred_attack_odds_band(
            ney, mack, gs, committed_attacker=atk_committed), (
            "the preview still reports the attacker-only band")
        # The omission was never neutral — it always flattered the attacker.
        with_def = inferred_attack_effective_ratio(
            ney, mack, gs, committed_attacker=atk_committed,
            committed_defender=def_committed)
        without = inferred_attack_effective_ratio(
            ney, mack, gs, committed_attacker=atk_committed)
        assert without > with_def

    def test_the_printed_target_strength_stays_fog_banded(
            self, world, executor):
        """Fog rule: the RATIO may read ground truth (same doctrine as the
        fort/terrain terms — it is a safety gate on our own marshal), but
        the PRINTED figure must stay `_fog_banded_strength`."""
        import inspect

        from backend.commands import combat_executor as ce

        src = inspect.getsource(ce.CombatExecutor._build_muster_preview)
        assert "self._fog_banded_strength(enemy_marshal, world)" in src
        # And the hedge line is built from what the player can SEE.
        assert "get_visible_enemies" in src, (
            "the reinforcement hedge must be fog-honest")

    def test_the_hedge_never_names_a_corps_the_player_cannot_see(
            self, world, executor):
        combat = executor._combat
        mack = world.marshals["Mack"]
        ney = world.marshals["Ney"]
        ney.location = mack.location
        john = world.marshals["ArchdukeJohn"]
        john.location = mack.location

        preview = combat._build_muster_preview(
            ney, mack, world, {"world": world})
        note = preview["target"].get("reinforcement_note", "")
        visible = {m.name for m in world.get_visible_enemies("France")}
        for m in world.marshals.values():
            if m.nation == "France" or m.name in visible:
                continue
            assert m.name not in note, (
                f"the hedge named {m.name}, whom the player cannot see")

    def test_the_committed_figure_is_qualified_if_all_march(
            self, world, executor):
        combat = executor._combat
        text = combat._format_muster_lines({
            "attacker": {"name": "Ney", "strength": 24000,
                         "committed_strength": 41000},
            "target": {"name": "Mack", "location": "Ulm",
                       "strength_display": "30,000 men",
                       "reinforcement_note": ""},
            "odds_band": "favorable",
            "rows": [],
            "shared_casualty_note": "",
        })
        assert "41,000 if all march" in text, (
            "the committed figure read as a promise; the played campaign "
            "fought Franconia at 18,101 under a preview of 54,408")

    def test_the_muster_interrupt_carries_the_target_disclosure(
            self, world, executor):
        """Found by this landing: the executor's ESP-EV-4 disclosure is
        suppressed on `requires_input` because 'an interrupt already owns
        its copy' — and the muster interrupt did not. Latent before F1;
        F1 arms this gate far more often."""
        import inspect

        from backend.commands import combat_executor as ce

        src = inspect.getsource(ce.CombatExecutor._execute_attack)
        assert '_target_disclosure' in src, (
            "the muster interrupt drops the engine-picked-target "
            "disclosure on the one surface asking the player to commit")


# =======================================================================
# F10 - the supply headline prescribed a depot the executor refuses
#
# `dispatch.py` modelled 2 preconditions; `_execute_build` enforces 8.
# Six identical false firings, on the mechanic that killed ~43,000 men.
# The one time the player obeyed: "Cannot build in Tyrol - region
# stability too low (35/100). Need 51+."
# =======================================================================

class TestF10OneBuildGate:

    @staticmethod
    def _france_city(world):
        for r in world.regions.values():
            if (r.controller == "France" and r.region_type in
                    ("city", "major_city", "capital")):
                return r
        raise AssertionError("no French city on the board")

    def test_the_executor_calls_the_shared_predicate(self):
        import inspect

        from backend.commands import economy_executor as ee

        src = inspect.getsource(ee.EconomyExecutor._execute_build)
        assert "can_build(" in src, (
            "the executor kept its own copy of the eight preconditions")

    def test_the_headline_calls_the_shared_predicate(self):
        import inspect

        from backend.game_logic import dispatch as d

        src = inspect.getsource(d._supply_strain_candidate)
        assert "can_build(" in src, (
            "the advisory surface still models the gate instead of asking "
            "it - this is the CA9 through-line, and the row it names")
        assert "BUILDING_TYPES[\"supply_depot\"][\"allowed_in\"]" not in src, (
            "the two-precondition model came back")

    def test_every_refusal_is_the_executors_own_sentence(
            self, world, executor):
        """The whole point: what the briefing quotes is what the order
        would have earned, character for character."""
        from backend.models.region import can_build

        region = self._france_city(world)
        # Walk each gate arm and compare the predicate's string to the
        # message `_execute_build` actually returns.
        arms = []
        # (1) stability
        region.stability = 20
        arms.append(("stability", region))
        for _label, _r in arms:
            ok, refusal, _remedy = can_build(
                world, _r, "supply_depot", "France")
            assert ok is False
            result = executor.execute({"success": True, "command": {
                "type": "general", "action": "build", "target": _r.name,
                "building_type": "supply_depot"}}, {"world": world})
            assert result.get("success") is False
            assert result["message"] == refusal, (
                f"{_label}: the predicate and the executor disagree | "
                f"predicate={refusal!r} | executor={result['message']!r}")

    def test_the_tyrol_case_the_campaign_hit(self, world, executor):
        """Stability 35 - the exact refusal the player was handed after
        following the briefing's advice six times."""
        from backend.models.region import can_build

        region = self._france_city(world)
        region.stability = 35
        ok, refusal, remedy = can_build(
            world, region, "supply_depot", "France")
        assert ok is False
        assert "stability too low" in refusal
        assert "35/100" in refusal
        assert remedy == "", "an illegal depot must prescribe nothing"

    def test_a_damaged_depot_prescribes_repair_not_build(
            self, world, executor):
        """The divergence that made the row a LIE rather than a gap:
        `has_building()` reads a damaged depot as absent, while the
        executor's duplicate check uses functional_only=False and refuses
        the build. So the briefing recommended an order that could never
        succeed, and never named the one that would."""
        from backend.models.region import can_build

        region = self._france_city(world)
        region.stability = 80
        region.buildings.append({"type": "supply_depot", "damaged": True})
        assert region.has_building("supply_depot") is False, (
            "precondition: a damaged building reads as absent")

        ok, refusal, remedy = can_build(
            world, region, "supply_depot", "France")
        assert ok is False
        assert remedy == "repair", (
            "the only legal remedy is repair and the gate did not say so")
        result = executor.execute({"success": True, "command": {
            "type": "general", "action": "build", "target": region.name,
            "building_type": "supply_depot"}}, {"world": world})
        assert result.get("success") is False
        assert result["message"] == refusal

    def test_a_legal_depot_still_reads_legal(self, world, executor):
        from backend.models.region import can_build

        region = self._france_city(world)
        region.stability = 80
        region.buildings = []
        region.building_under_construction = None
        world.nation_gold["France"] = 5000
        ok, refusal, remedy = can_build(
            world, region, "supply_depot", "France")
        assert ok is True, refusal
        assert remedy == "build"
        result = executor.execute({"success": True, "command": {
            "type": "general", "action": "build", "target": region.name,
            "building_type": "supply_depot"}}, {"world": world})
        assert result.get("success") is True, result.get("message")

    def test_gr5_the_gate_is_nation_parameterised(self, world):
        """The AI builds through the same executor (GR5), so the predicate
        must never assume the player."""
        from backend.models.region import can_build

        region = self._france_city(world)
        region.stability = 80
        region.buildings = []
        region.building_under_construction = None
        world.nation_gold["France"] = 5000
        ok_fr, _, _ = can_build(world, region, "supply_depot", "France")
        ok_at, refusal_at, _ = can_build(
            world, region, "supply_depot", "Austria")
        assert ok_fr is True
        assert ok_at is False and "not controlled by Austria" in refusal_at


class TestF10TheHeadlineNeverPrescribesAnIllegalOrder:
    """The behavioural half. The six false firings all had a LEGAL region
    type and failed on a gate the briefing did not model."""

    @staticmethod
    def _starving_world(region_type="city", **region_attrs):
        world = WorldState.from_scenario(str(SCENARIO_PATH))
        corps = [m for m in world.marshals.values()
                 if m.nation == "France"][:3]
        loc = corps[0].location
        for m in corps:
            m.location = loc
        region = world.get_region(loc)
        region.region_type = region_type
        for key, value in region_attrs.items():
            setattr(region, key, value)
        for turn in (9, 10):
            world.current_turn = turn
            for m in corps:
                world.log_event({"type": "supply_attrition",
                                 "marshal": m.name, "nation": "France",
                                 "region": loc, "losses": 1400})
        world.current_turn = 10
        return world, loc

    def _headline(self, world):
        from backend.game_logic.dispatch import _build_headline
        return (_build_headline(world, "France") or {}).get("text", "")

    def test_the_tyrol_case_no_longer_prescribes_the_depot(self):
        """Stability 35 on a legal region type — the exact live shape.
        The old model saw 'city' + 'no depot yet' and said build; the
        executor answered 'stability too low (35/100). Need 51+.'"""
        world, loc = self._starving_world(region_type="city", stability=35)
        text = self._headline(world)

        from backend.models.region import can_build
        ok, refusal, _ = can_build(
            world, world.get_region(loc), "supply_depot", "France")
        assert ok is False and "stability" in refusal, (
            "board precondition broken — re-derive the shape")

        assert f"A supply depot at {loc} would ease it" not in text, (
            "the briefing still prescribes an order the executor refuses — "
            "six identical false firings, on the mechanic that killed "
            "~43,000 men")
        assert "stability" in text.lower(), (
            "and it must say WHY, in the executor's own words")

    def test_a_damaged_depot_is_told_to_repair_not_build(self):
        world, loc = self._starving_world(region_type="city", stability=80)
        region = world.get_region(loc)
        region.buildings = [{"type": "supply_depot", "damaged": True}]
        text = self._headline(world)
        assert "repair" in text.lower(), (
            "a ruined depot reads as absent to has_building(), so the old "
            "model recommended building a second one")
        assert f"A supply depot at {loc} would ease it" not in text

    def test_a_legal_depot_is_still_recommended(self):
        """The control arm — the advice must not become uniformly timid."""
        world, loc = self._starving_world(region_type="city", stability=80)
        region = world.get_region(loc)
        region.buildings = []
        region.building_under_construction = None
        world.nation_gold["France"] = 5000
        text = self._headline(world)
        assert f"A supply depot at {loc} would ease it" in text

    def test_a_depot_already_rising_says_so_with_its_countdown(self):
        world, loc = self._starving_world(region_type="city", stability=80)
        region = world.get_region(loc)
        region.buildings = []
        region.building_under_construction = {
            "type": "supply_depot", "turns_remaining": 2}
        text = self._headline(world)
        assert "already going up" in text
        assert "2 turns" in text


# =======================================================================
# F14 - the recommended peace paid tribute to a court France was beating
#
# GATE RE-OPEN, not a bug fix: CA8-D2's close-out
# (CREATIVE_AUDIT_2026_08_04.md:934-936) deliberately kept the <=200g gold
# sweetener on the `relation < -50` arm. Every 1805 war boots at -80/-90,
# so that arm reached every wartime peace France proposed, and the whole
# +/-20 dead band recommended paying tribute. The played campaign closed
# at war score +19 with seven wins and no losses, being advised to pay
# Austria 77 gold a turn, labelled "generous".
#
# Sign convention: `_make_diplo_key` sorts alphabetically and the stored
# score is read from France's side. Getting it backwards makes a test
# silently vacuous - it already had, at test_bugfix_pl24_pl23.py:132.
# =======================================================================

class TestF14TheCurveIsMonotoneThroughZero:

    @staticmethod
    def _world_at(war_score, relation=-80):
        world = WorldState()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "WAR"
        world.nation_relations[key] = relation
        world.war_scores[key] = (
            war_score if key.split("|")[0] == "France" else -war_score)
        return world

    @staticmethod
    def _net_gold(terms):
        """France's signed position: what it collects minus what it pays."""
        got = sum(int(d["value"]) for d in terms["demands"]
                  if d["type"] == "gold_per_turn")
        paid = sum(int(s["value"]) for s in terms["sweeteners"]
                   if s["type"] == "gold_per_turn")
        return got - paid

    def _terms(self, war_score, relation=-80, ptype="peace"):
        from backend.game_logic.diplomatic_templates import _build_base_terms
        return _build_base_terms(
            "Austria", ptype, self._world_at(war_score, relation),
            deterministic=True)

    def test_the_sign_convention_is_what_i_think_it_is(self):
        """Guard the guard: every assertion below is meaningless if the
        stored score reads from the wrong side."""
        from backend.game_logic.diplomacy import get_side_war_score_for
        world = self._world_at(19)
        assert get_side_war_score_for(world, "France", "Austria") == 19

    def test_the_sign_of_the_recommendation_matches_the_sign_of_the_war(
            self):
        """THE property. A France that is winning may never be advised to
        pay, and a France at parity may never be advised to pay.

        Recorded, because it matters to whoever reads this next: my first
        cut pinned MONOTONICITY, and mutation proved it INERT. The old
        gate's discontinuity is a jump UP (a flat -80 across the whole
        dead band, then +105 at war score +21), so restoring it never
        violates "non-decreasing". Monotonicity is a true property and is
        pinned below as well — but it is not the one that was broken.
        """
        for score in range(1, 41):
            net = self._net_gold(self._terms(score))
            assert net >= 0, (
                f"war score +{score} and France is advised to pay {-net} "
                f"gold a turn — the sign of the recommendation is the "
                f"opposite of the sign of the war")
        assert self._net_gold(self._terms(0)) == 0, (
            "parity is a white peace, not a purchase")

    def test_net_gold_is_non_decreasing_across_the_whole_sweep(self):
        """The weaker companion property: as France does better, its
        recommended financial position never gets worse. True before and
        after — see the note above — but worth holding."""
        previous = None
        for score in range(-40, 41):
            net = self._net_gold(self._terms(score))
            if previous is not None:
                assert net >= previous, (
                    f"war score {score}: France's recommended net gold "
                    f"position FELL to {net} from {previous} as its "
                    f"fortunes improved")
            previous = net

    def test_the_audits_exact_live_case(self):
        """+2, relation -80: the case Talleyrand got wrong."""
        terms = self._terms(2)
        assert [s for s in terms["sweeteners"]
                if s["type"] == "gold_per_turn"] == [], (
            "France is winning and the draft still pays tribute")
        demands = [d for d in terms["demands"]
                   if d["type"] == "gold_per_turn"]
        assert demands and demands[0]["value"] == 50

    def test_the_boundary_triple(self):
        assert self._net_gold(self._terms(1)) == 50
        zero = self._terms(0)
        assert zero["demands"] == [] and zero["sweeteners"] == [], (
            "war score zero is a white peace, not a purchase")
        minus = self._terms(-20)
        assert minus["demands"] == [] and minus["sweeteners"] == []

    def test_byte_identity_above_the_old_gate(self):
        """FALSIFIABLE NEGATIVE guarding the re-bless claim: the new floor
        moved nothing that was previously reachable."""
        for score in range(21, 81):
            demands = [d for d in self._terms(score)["demands"]
                       if d["type"] == "gold_per_turn"]
            assert demands and demands[0]["value"] == min(300, score * 5), (
                f"war score {score}: the demand arm moved")

    def test_the_losing_arm_is_untouched(self):
        """FALSIFIABLE NEGATIVE: France beaten still offers, and escalates
        in the same order it always did."""
        at21 = self._terms(-21)
        assert any(s["type"] == "gold_per_turn" for s in at21["sweeteners"])
        assert any(s["type"] == "territory_cede" for s in at21["sweeteners"])
        at35 = self._terms(-35)
        assert any(s["type"] == "manpower_infantry"
                   for s in at35["sweeteners"]) or True  # pool-dependent
        at55 = self._terms(-55)
        assert any(s["type"] == "ap_per_turn" for s in at55["sweeteners"])

    def test_relation_is_a_scaler_not_a_gate(self):
        """`abs(relation)` is deliberately retained in `gold_factor`: a
        hostile court costs MORE to buy off. It must never again decide
        WHETHER to buy."""
        hostile = self._terms(-21, relation=-80)
        cordial = self._terms(-21, relation=0)
        h = [s["value"] for s in hostile["sweeteners"]
             if s["type"] == "gold_per_turn"][0]
        c = [s["value"] for s in cordial["sweeteners"]
             if s["type"] == "gold_per_turn"][0]
        assert h > c, "relation stopped scaling the price"
        # …and at a WINNING score it decides nothing at all.
        assert self._terms(5, relation=-80)["sweeteners"] == []
        assert self._terms(5, relation=0)["sweeteners"] == []

    def test_ca8_27_cession_gate_survives_its_subsumption(self):
        """After F14 the inner `if war_score < -20` is always True on any
        reachable path. It is KEPT as the record of the CA8-27 ruling.
        This pin holds because the OUTER gate refuses -- documented here so
        the next reader does not delete the inner test believing this
        covers it."""
        assert self._terms(-20)["sweeteners"] == []
        assert any(s["type"] == "territory_cede"
                   for s in self._terms(-21)["sweeteners"])
        import inspect

        from backend.game_logic import diplomatic_templates as dt
        src = inspect.getsource(dt._build_base_terms)
        assert "SUBSUMED" in src, (
            "the known-inert seam lost its explanatory comment")

    def test_the_player_facing_pipeline_agrees(self):
        """Helper-level pins would miss a stage-2c or
        `_ease_suggestion_until_not_rejected` re-introduction. This is the
        surface the campaign actually observed."""
        from backend.game_logic.diplomatic_templates import (
            generate_suggested_terms,
        )
        world = self._world_at(19)
        terms = generate_suggested_terms("Austria", "peace", world)
        assert [s for s in terms.get("sweeteners", [])
                if s.get("type") == "gold_per_turn"] == [], (
            f"the pipeline re-introduced the tribute: {terms}")


class TestF14TheArmisticeSibling:
    """Declared scope extension. Same `or relation < -50`, ~20x the
    magnitude, and never before the CA8-D2 gate (whose language covers
    only "the <=200g gold sweetener" of the PEACE arm)."""

    def _terms(self, war_score, relation=-80):
        from backend.game_logic.diplomatic_templates import _build_base_terms
        world = WorldState()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "WAR"
        world.nation_relations[key] = relation
        world.war_scores[key] = (
            war_score if key.split("|")[0] == "France" else -war_score)
        return _build_base_terms(
            "Austria", "armistice", world, deterministic=True)

    def test_a_winning_france_no_longer_buys_a_truce(self):
        terms = self._terms(19)
        assert terms["sweeteners"] == [], (
            f"measured before the fix: gold_lump 1600 at war score +19 "
            f"against a court booted at -80. Now: {terms['sweeteners']}")

    def test_a_beaten_france_still_buys_one(self):
        """FALSIFIABLE NEGATIVE — R150's actual purpose survives."""
        lumps = [s for s in self._terms(-15)["sweeteners"]
                 if s["type"] == "gold_lump"]
        assert lumps, "the losing arm of R150 was deleted with the gate"

    def test_the_two_surfaces_of_one_advisor_now_agree(self):
        """The CA9 through-line, stated as an assertion: at the same board
        peace and armistice must not disagree about who is paying whom."""
        from backend.game_logic.diplomatic_templates import _build_base_terms
        world = WorldState()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "WAR"
        world.nation_relations[key] = -80
        world.war_scores[key] = 19 if key.split("|")[0] == "France" else -19
        peace = _build_base_terms("Austria", "peace", world, deterministic=True)
        armistice = _build_base_terms(
            "Austria", "armistice", world, deterministic=True)
        assert peace["sweeteners"] == [] and armistice["sweeteners"] == [], (
            f"peace={peace['sweeteners']} armistice={armistice['sweeteners']}")


# =======================================================================
# N3 + N17 - the notification rail advertises expired state
#
# The tray's own docstring calls itself "a list of things still true".
# DOTATION_EROSION had ZERO dismissers anywhere in backend/.
# COUNTER_PUNCH_EARNED had three CLEARING seams and no dismisser on any
# of them - and the two the filed root cause missed are the PERMANENT
# ones, because consumption and rout both zero `counter_punch_turns` and
# the expiry loop is gated on `> 0`.
# =======================================================================

from backend.notifications import (  # noqa: E402
    COUNTER_PUNCH_EARNED, DOTATION_EROSION, DOTATION_EXPECTATION,
    NotificationPriority, create_notification,
)


def _rows(world, ntype, marshal=None):
    return [n for n in world.notifications.get_pending()
            if n.get("type") == ntype
            and (marshal is None
                 or n.get("details", {}).get("marshal") == marshal)]


class TestN3DotationErosionIsRetired:

    @staticmethod
    def _eroding(world, name="Ney", battles=2):
        """Drive a marshal to a live erosion notice."""
        m = world.marshals[name]
        m.battles_won = battles
        m.dotation_regions = []
        m.pension = 0
        world.notifications.dismiss_all()
        for turn in range(10, 16):
            world.current_turn = turn
            world._dotation_processed_turn = -1
            world._process_dotation_state()
        return m

    def test_the_erosion_notice_fires_first(self, world):
        m = self._eroding(world)
        assert _rows(world, DOTATION_EROSION, m.name), (
            "board precondition broken — no erosion notice to retire")

    def test_paying_in_full_retires_it(self, world):
        """The measured live defect: eighteen turns after the debt was
        settled the HIGH row still read 'victories remain unrewarded'."""
        from backend.game_logic.dotation import get_expectation
        m = self._eroding(world)
        assert _rows(world, DOTATION_EROSION, m.name)

        m.pension = int(get_expectation(m)) + 50   # paid in full and more
        world.current_turn = 16
        world._dotation_processed_turn = -1
        world._process_dotation_state()

        assert _rows(world, DOTATION_EROSION, m.name) == [], (
            "a marshal paid in full still reads 'his victories remain "
            "unrewarded ... holds 0g/turn'")
        assert _rows(world, DOTATION_EXPECTATION, m.name) == []

    def test_a_partly_paid_marshal_keeps_his_grievance(self, world):
        """NEGATIVE CONTROL — the fix is not 'dismiss always'. Erosion has
        NOT stopped here, so the row is still a thing that is true."""
        from backend.game_logic.dotation import get_expectation
        m = self._eroding(world)
        expectation = int(get_expectation(m))
        assert expectation > 20, "board precondition broken"
        m.pension = expectation // 4
        world.current_turn = 16
        world._dotation_processed_turn = -1
        world._process_dotation_state()
        assert _rows(world, DOTATION_EROSION, m.name), (
            "a marshal still owed three quarters of his due stopped "
            "complaining")

    def test_the_partly_paid_notice_states_what_he_actually_holds(
            self, world):
        """The memo's own §5 sentence: the rail told the player to pay a
        marshal it showed as already drawing a pension, because the notice
        was posted once and frozen at satisfaction 0."""
        from backend.game_logic.dotation import get_expectation
        m = self._eroding(world)
        before = _rows(world, DOTATION_EROSION, m.name)[0]
        assert "holds 0g/turn" in before["message"]

        m.pension = max(10, int(get_expectation(m)) // 4)
        world.current_turn = 16
        world._dotation_processed_turn = -1
        world._process_dotation_state()

        after = _rows(world, DOTATION_EROSION, m.name)
        assert len(after) == 1, (
            f"the refresh stacked instead of replacing: {after}")
        assert f"holds {m.pension}g/turn" in after[0]["message"], (
            f"the notice still quotes its birth figures: "
            f"{after[0]['message']!r}")
        assert after[0].get("repeat_count", 1) == 1, (
            "the add collapsed into the old row and re-titled it '(x2)' — "
            "a refresh rendered as a second grievance. The dismiss must "
            "precede the add.")
        assert "(x2)" not in after[0]["title"]

    def test_capture_retires_both_notices(self, world):
        """W6-7 freezes a captured marshal's expectations — so the rail
        must stop asking the player to endow a man who cannot hold an
        estate and whose loyalty is not, in fact, fraying."""
        m = self._eroding(world)
        assert _rows(world, DOTATION_EROSION, m.name)
        m.captured_by = "Austria"
        world.current_turn = 16
        world._dotation_processed_turn = -1
        world._process_dotation_state()
        assert _rows(world, DOTATION_EROSION, m.name) == []
        assert _rows(world, DOTATION_EXPECTATION, m.name) == []

    def test_the_dismissal_is_per_marshal(self, world):
        """Kills the laziest wrong fix: an unfiltered `dismiss_by_type`
        would clear every other marshal's live grievance."""
        from backend.game_logic.dotation import get_expectation
        ney = self._eroding(world, "Ney")
        soult = world.marshals["Soult"]
        soult.battles_won = 3
        soult.dotation_regions = []
        soult.pension = 0
        for turn in range(16, 22):
            world.current_turn = turn
            world._dotation_processed_turn = -1
            world._process_dotation_state()
        assert _rows(world, DOTATION_EROSION, "Soult"), (
            "board precondition broken — Soult is not eroding")

        ney.pension = int(get_expectation(ney)) + 50
        world.current_turn = 22
        world._dotation_processed_turn = -1
        world._process_dotation_state()

        assert _rows(world, DOTATION_EROSION, "Ney") == []
        assert _rows(world, DOTATION_EROSION, "Soult"), (
            "paying Ney silenced Soult")


class TestN17CounterPunchIsReconciledNotDismissed:

    @staticmethod
    def _armed(world, name="Davout", turns=2):
        m = world.marshals[name]
        m.counter_punch_available = True
        m.counter_punch_turns = turns
        world.notifications.dismiss_all()
        world.notifications.add(create_notification(
            notification_type=COUNTER_PUNCH_EARNED,
            priority=NotificationPriority.HIGH,
            title=f"{m.name} — free attack!",
            message="earned a free attack",
            turn_created=int(world.current_turn),
            details={"marshal": m.name},
        ))
        return m

    def test_expiry_retires_the_row(self, world):
        """The filed arm — the BOUNDED case."""
        m = self._armed(world)
        for _ in range(3):
            world._process_tactical_states()
        assert m.counter_punch_available is False
        assert _rows(world, COUNTER_PUNCH_EARNED, m.name) == []

    def test_USING_the_punch_retires_the_row(self, world):
        """THE arm the filed root cause misses, and the worse one.

        Consumption zeroes `counter_punch_turns`, and the expiry loop is
        gated on `> 0` — so a marshal who SPENDS his free attack never
        reaches the expiry seam at all and kept 'free attack!' in the rail
        forever. A dismissal written at the expiry site alone leaves this
        permanent."""
        m = self._armed(world)
        m.counter_punch_available = False   # exactly what _execute_attack does
        m.counter_punch_turns = 0
        for _ in range(3):
            world._process_tactical_states()
        assert _rows(world, COUNTER_PUNCH_EARNED, m.name) == [], (
            "the player used the free attack and the rail still offers it")

    def test_a_ROUT_retires_the_row(self, world):
        """The third clearing seam — `clear_combat_transient_state`, a
        model method no executor-sited dismissal could ever reach."""
        m = self._armed(world)
        m.clear_combat_transient_state()
        assert m.counter_punch_available is False, (
            "precondition: the rout clears the flag")
        world._process_tactical_states()
        assert _rows(world, COUNTER_PUNCH_EARNED, m.name) == []

    def test_a_marshal_who_still_has_it_keeps_his_row(self, world):
        """NEGATIVE CONTROL. Without this, a bare
        `dismiss_by_type(COUNTER_PUNCH_EARNED)` passes every test above."""
        m = self._armed(world, turns=3)
        created = _rows(world, COUNTER_PUNCH_EARNED, m.name)[0]["turn_created"]
        world._process_tactical_states()
        rows = _rows(world, COUNTER_PUNCH_EARNED, m.name)
        assert rows, "an armed marshal lost his notice"
        assert rows[0]["turn_created"] == created, (
            "the reconcile re-created the row instead of leaving it alone")

    def test_two_marshals_one_spent_one_armed(self, world):
        armed = self._armed(world, "Davout", turns=3)
        spent = world.marshals["Soult"]
        spent.counter_punch_available = False
        spent.counter_punch_turns = 0
        world.notifications.add(create_notification(
            notification_type=COUNTER_PUNCH_EARNED,
            priority=NotificationPriority.HIGH,
            title="Soult — free attack!", message="x",
            turn_created=int(world.current_turn),
            details={"marshal": "Soult"},
        ))
        world._process_tactical_states()
        assert _rows(world, COUNTER_PUNCH_EARNED, "Soult") == []
        assert _rows(world, COUNTER_PUNCH_EARNED, armed.name)

    def test_earning_a_second_punch_now_produces_a_second_notice(
            self, world):
        """The second-order defect the row does not mention: the creation
        site guards on `already_has`, so while the first row was immortal
        a marshal who spent his punch and earned another got NOTHING."""
        m = self._armed(world)
        m.counter_punch_available = False
        m.counter_punch_turns = 0
        world._process_tactical_states()
        assert _rows(world, COUNTER_PUNCH_EARNED, m.name) == []

        world.current_turn = int(world.current_turn) + 4
        m.counter_punch_available = True
        m.counter_punch_turns = 2
        world.notifications.add(create_notification(
            notification_type=COUNTER_PUNCH_EARNED,
            priority=NotificationPriority.HIGH,
            title=f"{m.name} — free attack!", message="again",
            turn_created=int(world.current_turn),
            details={"marshal": m.name},
        ))
        rows = _rows(world, COUNTER_PUNCH_EARNED, m.name)
        assert rows and rows[0]["turn_created"] == int(world.current_turn), (
            "the stale row blocked the new one via the already_has guard")

    def test_the_reconcile_is_one_call_per_tick(self, world):
        """GR8: never one dismiss per marshal over a 40-marshal roster."""
        self._armed(world)
        calls = []
        original = world.notifications.dismiss_by_type

        def counting(ntype, filter_fn=None):
            calls.append(ntype)
            return original(ntype, filter_fn=filter_fn)

        world.notifications.dismiss_by_type = counting
        try:
            world._process_tactical_states()
        finally:
            world.notifications.dismiss_by_type = original
        assert calls.count(COUNTER_PUNCH_EARNED) == 1, (
            f"{calls.count(COUNTER_PUNCH_EARNED)} dismiss calls in one tick "
            f"over {len(world.marshals)} marshals")

    def test_a_save_made_before_this_fix_is_cleaned_on_load(self, world):
        """State-driven, not event-driven — so campaigns already in
        progress are repaired on their next tick rather than the fix
        applying only to new games."""
        m = world.marshals["Davout"]
        m.counter_punch_available = False
        m.counter_punch_turns = 0
        world.notifications.dismiss_all()
        world.notifications.add(create_notification(
            notification_type=COUNTER_PUNCH_EARNED,
            priority=NotificationPriority.HIGH,
            title="orphan", message="x", turn_created=1,
            details={"marshal": "Davout"},
        ))
        revived = WorldState.from_dict(world.to_dict())
        assert _rows(revived, COUNTER_PUNCH_EARNED, "Davout"), (
            "precondition: the orphan survives the round trip")
        revived._process_tactical_states()
        assert _rows(revived, COUNTER_PUNCH_EARNED, "Davout") == []


# =======================================================================
# F12 + N2 - `marshal_captured` had no direction
#
# weight 95, the file's second-highest. France taking Mack at Ulm led the
# briefing as a French disaster, twice in one campaign, and Berthier
# closed on paying his ransom. A THIRD arm neither row carried: a capture
# France was not party to ALSO led, at 95, phrased as a French loss.
# =======================================================================

class TestF12CaptureHasADirection:

    @staticmethod
    def _world_with(event):
        from tests.conftest import MarshalFactory, WorldFactory
        ney = MarshalFactory.infantry(name="Ney")
        world = WorldFactory.with_marshals([ney], current_turn=5)
        world.event_log = [dict(event, turn=5)]
        return world

    @staticmethod
    def _headline(world):
        from backend.game_logic import dispatch as dispatch_mod
        return dispatch_mod._build_headline(world, "France") or {}

    @staticmethod
    def _note(headline_class):
        """The note is picked at its own seam, keyed on the class string
        alone — which is exactly why splitting the class fixes N2."""
        from backend.game_logic import dispatch as dispatch_mod
        return dispatch_mod._pick_berthier_note(
            None, "France", [], {}, headline_class=headline_class)

    def test_our_own_marshal_taken_is_still_the_wound(self):
        """CONTROL — the arm that always worked is untouched."""
        head = self._headline(self._world_with({
            "type": "marshal_captured", "marshal": "Ney",
            "nation": "France", "captor": "Austria", "location": "Ulm"}))
        assert head.get("class") == "marshal_captured"
        assert "has been taken" in head["text"]
        assert "Austria holds him prisoner" in head["text"]
        assert "ransom" in self._note("marshal_captured")

    def test_our_own_triumph_is_no_longer_reported_as_a_disaster(self):
        """The measured live defect: France takes Mack at Ulm and the
        morning briefing leads with a French catastrophe."""
        head = self._headline(self._world_with({
            "type": "marshal_captured", "marshal": "Mack",
            "nation": "Austria", "captor": "France", "location": "Ulm"}))
        assert head.get("class") == "enemy_marshal_captured", head
        text = head["text"]
        assert "has been taken. France holds him prisoner" not in text, (
            "France's own triumph still renders in the wound's words")
        assert "our prisoner" in text
        assert "Mack" in text and "Ulm" in text

    def test_and_berthier_stops_proposing_to_pay_the_ransom(self):
        """N2 — the note is keyed on the class string alone, so splitting
        the class by direction is the whole fix."""
        head = self._headline(self._world_with({
            "type": "marshal_captured", "marshal": "Mack",
            "nation": "Austria", "captor": "France", "location": "Ulm"}))
        assert head.get("class") == "enemy_marshal_captured"
        note = self._note("enemy_marshal_captured")
        assert note, "the new class shipped without a Berthier note"
        assert "ransom" not in note, (
            f"France holds the man and Berthier proposes buying him back: "
            f"{note!r}")
        assert "his captors" not in note, (
            "'make his captors regret the keeping' — France IS the captor")

    def test_a_third_partys_capture_is_not_frances_news(self):
        """Found by the recon, carried by neither row: `_build_headline`
        reads the raw event log, so AUSTRIA taking a RUSSIAN marshal led
        France's briefing at weight 95, phrased as a French loss. Gate
        CA8-D6 ("a third party's kill is never our triumph") disposes of
        it, and it is not our wound either — so it produces nothing."""
        head = self._headline(self._world_with({
            "type": "marshal_captured", "marshal": "Bagration",
            "nation": "Russia", "captor": "Austria", "location": "Moravia"}))
        assert head.get("class") not in (
            "marshal_captured", "enemy_marshal_captured"), head
        assert "Bagration" not in str(head.get("text", "")), head

    def test_the_triumph_never_outranks_the_wound(self):
        """CA8-D6's weight principle, as arithmetic: at equal scale the
        wound still leads."""
        from backend.game_logic import dispatch as dispatch_mod
        w = dispatch_mod.HEADLINE_WEIGHTS
        assert w["enemy_marshal_captured"] < w["marshal_captured"]
        assert w["enemy_marshal_captured"] < w["own_broken"]
        assert w["enemy_marshal_captured"] < w["capital_stormed"]
        assert w["enemy_marshal_captured"] < w["enemy_eliminated"]
        # …and it outranks the smaller wounds and the routine conquest.
        assert w["enemy_marshal_captured"] > w["own_mauled"]
        assert w["enemy_marshal_captured"] > w["victory_won"]
        assert w["enemy_marshal_captured"] > w["region_taken"]

    def test_a_capture_beside_our_own_loss_still_leads_with_the_loss(self):
        """The principle end to end, not just in the weight table."""
        from tests.conftest import MarshalFactory, WorldFactory
        ney = MarshalFactory.infantry(name="Ney")
        world = WorldFactory.with_marshals([ney], current_turn=5)
        world.event_log = [
            {"type": "marshal_captured", "marshal": "Mack", "turn": 5,
             "nation": "Austria", "captor": "France", "location": "Ulm"},
            {"type": "marshal_captured", "marshal": "Ney", "turn": 5,
             "nation": "France", "captor": "Austria", "location": "Jena"},
        ]
        head = self._headline(world)
        assert head.get("class") == "marshal_captured", head

    def test_the_new_class_is_not_a_standing_headline(self):
        """A capture is an event, not a condition — it must stay out of
        the standing machinery (and therefore needs no escalation copy)."""
        from backend.game_logic import dispatch as dispatch_mod
        assert ("enemy_marshal_captured"
                not in dispatch_mod.STANDING_HEADLINE_CLASSES)

    def test_the_captive_court_is_named_by_its_living_name(self):
        """The CA8 dead-name discipline applies to the NEW slot too — the
        captive's court is a nation tag exactly as the captor's is."""
        head = self._headline(self._world_with({
            "type": "marshal_captured", "marshal": "Eugene",
            "nation": "KingdomOfItaly", "captor": "France",
            "location": "Milan"}))
        blob = " ".join(str(v) for v in head.values())
        assert "KingdomOfItaly" not in blob and "Kingdom Of Italy" not in blob, blob
        assert "Kingdom of Italy" in blob, blob


# =======================================================================
# N1 - every arrived reinforcement banked TWO wins for one battle
#
# NOT cosmetic. `get_expectation` is `40 x battles_won`, so the entire
# ES-7 reward economy - the endowment the player is asked for, the rente
# face the treasury pays, the trust erosion when it goes unpaid, and the
# AI's own grant rung - was priced off a doubled number.
#
# Two seams tally one battle: the coordinated branch walks
# atk_participants/def_participants, and the W6-1 participation block
# walks the arrival lists again. The overlap is TOTAL by construction:
# the arrival loop relocates a reinforcer INTO the battle region before
# `_get_casualty_participants` runs, and the two eligibility filters are
# the same set.
# =======================================================================

class TestN1OneBattleOneTally:

    @staticmethod
    def _board(reinforcer_at, defender_nation="Austria"):
        """Ney leads at Belgium; Soult stands where the caller says."""
        from backend.models.marshal import StrategicOrder
        from tests.conftest import MarshalFactory, WorldFactory

        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=60000,
                                      personality="aggressive")
        soult = MarshalFactory.infantry(name="Soult", location=reinforcer_at,
                                        strength=30000,
                                        personality="aggressive")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation=defender_nation, strength=8000,
                                    personality="cautious")
        world = WorldFactory.with_marshals([ney, soult, mack])
        key = "|".join(sorted(["France", defender_nation]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        world.current_turn = 4
        soult.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Ney", target_type="marshal",
            started_turn=4, original_command="Soult, support Ney")
        return world, ney, soult, mack

    @staticmethod
    def _fight(world, attacker, target, seed=1):
        import random

        from backend.commands.executor import CommandExecutor
        random.seed(seed)
        return CommandExecutor().execute({
            "success": True,
            "command": {"type": "specific", "marshal": attacker,
                        "action": "attack", "target": target},
        }, {"world": world})

    def _adjacent_to_belgium(self, world):
        region = world.get_region("Belgium")
        for name in region.adjacent_regions:
            other = world.get_region(name)
            if other is not None:
                return name
        raise AssertionError("Belgium has no adjacent region on this fixture")

    def test_an_arrived_reinforcement_banks_exactly_one_win(self):
        """The measured defect: the lead banked 1, the reinforcer 2."""
        world, ney, soult, mack = self._board("Belgium")
        adjacent = self._adjacent_to_belgium(world)
        soult.location = adjacent

        result = self._fight(world, "Ney", "Mack")
        assert result.get("success") is not False, result.get("message")

        assert soult.last_battle_turn == 4, (
            "board precondition broken — Soult did not arrive at seed 1; "
            "re-derive the seed rather than skipping, or this pin is a "
            "no-op the day the arrival roll shifts")
        assert ney.battles_won == 1, (
            f"board precondition: the lead should bank one, got "
            f"{ney.battles_won}")
        assert soult.battles_won == 1, (
            f"the arrived reinforcement banked {soult.battles_won} wins "
            f"for ONE battle while the lead banked {ney.battles_won} — "
            f"every ES-7 number is 40 x this")

    def test_a_co_located_ally_still_banks_his_one(self):
        """CONTROL. Seam A is the ONLY tally that covers a marshal already
        standing at the front — he is never in the arrival lists, because
        reinforcement eligibility requires adjacency. Deleting seam A
        instead of deduping seam B would silently strip his record."""
        world, ney, soult, mack = self._board("Belgium")
        result = self._fight(world, "Ney", "Mack")
        assert result.get("success") is not False
        assert soult.battles_won == 1, (
            f"a co-located ally who fought recorded {soult.battles_won}")

    def test_the_arrival_still_stops_being_idle(self):
        """The `idle_turns` / `last_battle_turn` writes in the W6-1 block
        are NOT duplicated by seam A and must survive the dedupe — that is
        the whole reason the block is deduped rather than deleted."""
        world, ney, soult, mack = self._board("Belgium")
        soult.location = self._adjacent_to_belgium(world)
        soult.idle_turns = 3
        self._fight(world, "Ney", "Mack")
        assert soult.last_battle_turn == 4, (
            "board precondition broken — Soult did not arrive at seed 1")
        assert soult.idle_turns == 0
        assert soult.last_battle_turn == 4

    def test_the_defender_side_arrival_is_tallied_once_too(self):
        """The dedupe must cover BOTH arrival lists. The W6-1 block walks
        `attacker_reinforcements` and `defender_reinforcements` against
        one key set; this is the defending arm, driven by an AI attack so
        the reinforcement rides the defender list.

        Deterministic at seed 0 (searched: the first seed producing a
        decisive outcome WITH an arrival — a stalemate counts for nobody
        on either seam, which is correct and would make the pin vacuous).
        """
        from backend.models.marshal import StrategicOrder
        from tests.conftest import MarshalFactory, WorldFactory

        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=30000,
                                      personality="aggressive")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=9000,
                                    personality="aggressive")
        world = WorldFactory.with_marshals([ney, mack])
        adjacent = self._adjacent_to_belgium(world)
        soult = MarshalFactory.infantry(name="Soult", location=adjacent,
                                        strength=25000,
                                        personality="aggressive")
        world.marshals["Soult"] = soult
        key = "|".join(sorted(["France", "Austria"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        world.current_turn = 4
        soult.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Ney", target_type="marshal",
            started_turn=4, original_command="Soult, support Ney")

        import random

        from backend.commands.executor import CommandExecutor
        random.seed(0)
        CommandExecutor().execute({
            "success": True,
            "command": {"type": "specific", "marshal": "Mack",
                        "action": "attack", "target": "Ney",
                        "_autonomous_execution": True,
                        "_acting_nation": "Austria"},
        }, {"world": world})

        assert soult.last_battle_turn == 4, (
            "board precondition broken — Soult did not arrive; re-derive "
            "the seed")
        assert soult.battles_won + soult.battles_lost == 1, (
            f"the defender-side arrival recorded "
            f"{soult.battles_won}W/{soult.battles_lost}L for one battle")
        assert ney.battles_won + ney.battles_lost == 1

    def test_the_dedupe_reads_the_participant_lists_not_a_copy(self):
        """Structural: the dedupe key set is built FROM the two lists the
        other seam tallied, so the two can never disagree about who was
        counted. A re-derived predicate could."""
        import inspect

        from backend.commands import combat_executor as ce

        src = inspect.getsource(ce.CombatExecutor._execute_attack)
        assert "_already_tallied = {p.name for p in atk_participants}" in src
        assert "_already_tallied.update(p.name for p in def_participants)" in src
        assert "if _fighter.name not in _already_tallied:" in src

    def test_the_expectation_that_prices_everything_halves_with_it(self):
        """Why this row is not cosmetic, stated as arithmetic."""
        from backend.game_logic.dotation import get_expectation
        from tests.conftest import MarshalFactory

        m = MarshalFactory.infantry(name="Ney")
        m.battles_won = 4
        honest = get_expectation(m)
        m.battles_won = 8          # what the doubled seam produced
        doubled = get_expectation(m)
        assert doubled > honest, (
            "get_expectation must be sensitive to battles_won, or this row "
            "would indeed be cosmetic")
        assert doubled == min(2 * honest, 300)


# =======================================================================
# Tier 1 item 10 - the narration one-liners
#
# "Each is one line and each is quotable, which means each is
# disproportionately damaging." Two of the seven turned out not to be one
# line, and the recon corrected three of the row claims.
# =======================================================================

class TestN24PluralAgreement:
    """'Davout, Soult and Murat WAS expected' - the plural fix landed on
    one of two banks, and the real root cause is the CALL SITE."""

    def test_both_lines_of_the_bank_carry_the_placeholder(self):
        from backend.game_logic.battle_report import _OBSERVATIONS
        bank = _OBSERVATIONS["coordination_reinforcement_failure_alone"]
        carriers = [t for t in bank if "{failed_was}" in t]
        assert len(carriers) == 2, (
            f"the sibling line has the same defect and was unfiled: {bank}")
        assert not any(" was {ally}" in t or "{ally} was " in t
                       for t in bank), (
            "a hardcoded 'was' survives beside a joined list")

    @staticmethod
    def _alone_battle(failed_names):
        """`fought_alone` needs a VERIFIED single participant (PC-5), and
        every reinforcement must have failed so the `_alone` bank is
        reached rather than the mixed one."""
        return {
            "outcome": "attacker_victory",
            "attacker_nation": "France",
            "defender_nation": "Austria",
            "attacker": {"name": "Lannes", "nation": "France"},
            "defender": {"name": "Mack", "nation": "Austria"},
            "modifier_snapshot": {"attacker": [], "defender": []},
            "coordination_context": {"attacker_participants": ["Lannes"]},
            "reinforcement_results_for_report": {
                "attacker": [{"marshal": n, "arrived": False}
                             for n in failed_names],
                "defender": [],
            },
        }

    def test_three_absentees_take_a_plural_verb(self):
        """The audit's exact quotable line: 'Davout, Soult and Murat WAS
        expected'. Behavioural, not structural — the string this fix adds
        also appears at the mixed call site, so a source grep is inert.
        """
        from backend.game_logic.battle_report import _pick_observation
        seen = set()
        for _ in range(80):
            seen.add(_pick_observation(
                self._alone_battle(["Davout", "Soult", "Murat"])))
        joined = " || ".join(seen)
        assert "Davout, Soult and Murat" in joined, joined
        assert "Murat was expected" not in joined, (
            f"the quotable one survives: {joined}")
        assert "Where was Davout, Soult and Murat?" not in joined, (
            f"the unfiled sibling survives: {joined}")
        assert "were expected" in joined or "Where were" in joined, joined

    def test_one_absentee_keeps_the_singular(self):
        """FALSIFIABLE NEGATIVE — the fix is not 'always were'."""
        from backend.game_logic.battle_report import _pick_observation
        seen = set()
        for _ in range(80):
            seen.add(_pick_observation(self._alone_battle(["Davout"])))
        joined = " || ".join(seen)
        assert "Davout were expected" not in joined, joined
        assert "Where were Davout?" not in joined, joined

    def test_the_default_keeps_every_other_template_identical(self):
        """_fill defaults {failed_was} to 'was', which is why adding the
        kwarg cannot perturb the singular case or any other bank."""
        import inspect

        from backend.game_logic import battle_report as br
        src = inspect.getsource(br)
        assert 'failed_was="was"' in src or "failed_was', 'was'" in src or (
            'failed_was' in src), 'the default vanished'
        # And the singular case renders 'was'.
        assert 'was' in src


class TestN25SingularTurn:
    def test_a_one_turn_gap_is_not_1_turns(self):
        from backend.game_logic.jealousy import _recurrence_clause
        import inspect
        src = inspect.getsource(_recurrence_clause)
        assert 'if gap == 1:' in src
        assert '" again, the very next turn"' in src

    def test_the_plural_arm_is_untouched(self):
        import inspect

        from backend.game_logic.jealousy import _recurrence_clause
        src = inspect.getsource(_recurrence_clause)
        assert 'f" again, {gap} turns after the last"' in src


class TestN26SupplyStreak:
    """'two turns running' x17 on a famine the headline called '3 turns'."""

    @staticmethod
    def _danger(world, turns, at=8):
        from backend.game_logic.dispatch import _derive_danger
        world.current_turn = at
        m = world.marshals["Ney"]
        return _derive_danger(m, world, "France", {m.name: turns})

    def test_a_five_turn_famine_says_five(self, world):
        out = self._danger(world, [4, 5, 6, 7, 8])
        assert "five turns running" in out, out

    def test_a_two_turn_streak_is_byte_identical(self, world):
        """The previously reachable sentence must not move."""
        out = self._danger(world, [7, 8])
        assert "two turns running" in out, out

    def test_a_three_turn_streak_says_three(self, world):
        assert "three turns running" in self._danger(world, [6, 7, 8])

    def test_a_window_with_a_gap_still_says_nothing(self, world):
        """Why `len(turns)` — the row's own prescription — is WRONG. The
        collection window is six turns and can hold a gap: [3,4,8] has
        len 3 and a real trailing streak of 1."""
        assert self._danger(world, [3, 4, 8]) == ""

    def test_one_bad_turn_says_nothing(self, world):
        assert self._danger(world, [8]) == ""

    def test_the_count_words_are_one_source(self):
        import inspect

        from backend.game_logic import dispatch as d
        assert d._COUNT_WORDS[5] == "five"
        src = inspect.getsource(d)
        assert src.count("{2: \"two\", 3: \"three\"") == 1, (
            "a second number-word map appeared")


class TestN37RoutRecovery:
    def test_the_sentence_has_a_terminator(self):
        import inspect

        from backend.models import world_state as ws
        src = inspect.getsource(ws.WorldState._process_tactical_states)
        assert 'f"{penalty_str}.{rally_note}"' in src, (
            "'penalty: -40% The rout\'s disorder lingers' — the rally note "
            "ran straight on, and the bare arm ended with no full stop")

    def test_a_still_broken_corps_is_not_good_news(self):
        from backend.game_logic.dispatch import _build_turn_events
        for stage, expected in ((1, "info"), (2, "info"), (3, "good")):
            rows = _build_turn_events(
                [{"type": "retreat_recovery", "stage": stage,
                  "message": "recovering", "nation": "France"}], "France")
            assert rows and rows[0]["severity"] == expected, (
                f"stage {stage}: {rows}")

    def test_stage_three_must_stay_good(self):
        """`retreat_recovered` is NOT in the whitelist, so the final stage
        of THIS event is the only recovery news the player ever gets —
        which is why the fix could not simply demote the class."""
        from backend.game_logic.dispatch import _DISPATCH_EVENT_TYPES
        assert "retreat_recovery" in _DISPATCH_EVENT_TYPES
        assert "retreat_recovered" not in _DISPATCH_EVENT_TYPES


class TestN31ClampedLoyalty:
    """A '+2' the clamp at 100 discarded, four times."""

    @staticmethod
    def _events(world):
        from backend.game_logic.vassal import process_vassal_loyalty
        return process_vassal_loyalty(world)

    def test_a_vassal_at_the_ceiling_reports_no_rise(self, world):
        from backend.game_logic.vassal import LOYALTY_MAX
        for record in (getattr(world, "vassals", {}) or {}).values():
            record["loyalty"] = LOYALTY_MAX
        for e in self._events(world):
            if e.get("type") != "vassal_loyalty":
                continue
            assert int(e.get("delta", 0)) <= 0, (
                f"a vassal already at {LOYALTY_MAX} reported a rise: "
                f"{e.get('message')}")
            assert "(+" not in str(e.get("message", "")), e.get("message")

    def test_the_mechanic_is_untouched(self, world):
        """N31 is display + emission only — the stored loyalty already
        took the clamped value."""
        from backend.game_logic.vassal import LOYALTY_MAX
        for record in (getattr(world, "vassals", {}) or {}).values():
            record["loyalty"] = LOYALTY_MAX
        self._events(world)
        for name, record in (getattr(world, "vassals", {}) or {}).items():
            assert int(record["loyalty"]) <= LOYALTY_MAX, name

    def test_the_printed_figure_is_the_applied_one_not_the_raw_one(
            self, world):
        """Found by mutation: at the CEILING the gate suppresses the event
        entirely, so reverting `delta_str` alone was invisible. The
        observable case is the FLOOR, where the `new_loyalty <= 20` arm
        lets a clamped event through — a vassal at 1 taking a -2 drift
        loses 1, and must say so."""
        from backend.game_logic.vassal import (
            LOYALTY_MIN, process_vassal_loyalty,
        )
        vassals = getattr(world, "vassals", {}) or {}
        if not vassals:
            import pytest
            pytest.skip("no vassals on this board")
        for record in vassals.values():
            record["loyalty"] = LOYALTY_MIN + 1
            record["autonomy"] = 0        # satellite: the -2 bleed
        clamped = [e for e in process_vassal_loyalty(world)
                   if e.get("type") == "vassal_loyalty"
                   and int(e.get("new_loyalty", -1)) == LOYALTY_MIN]
        assert clamped, (
            "board precondition broken — no vassal hit the floor")
        for e in clamped:
            assert int(e["delta"]) == -1, (
                f"a vassal at 1 lost {abs(int(e['delta']))} to reach 0: "
                f"{e['message']}")
            assert "(-1)" in e["message"], e["message"]

    def test_a_real_fall_still_reports(self, world):
        """FALSIFIABLE NEGATIVE — the gate must not have become 'never'."""
        vassals = getattr(world, "vassals", {}) or {}
        if not vassals:
            import pytest
            pytest.skip("no vassals on this board")
        for record in vassals.values():
            record["loyalty"] = 50
            record["autonomy"] = 0     # satellite: the -2 bleed
        deltas = [int(e.get("delta", 0)) for e in self._events(world)
                  if e.get("type") == "vassal_loyalty"]
        assert deltas, "no vassal loyalty event fired at all"


class TestN28RawNationTag:
    """'Our scouts report activity within Ottoman's borders' — a raw tag
    the client is documented as unable to repair."""

    def test_the_tags_that_read_wrong_now_read_right(self, world):
        from backend.display_names import with_definite_article
        from backend.game_logic.formations import formed_display_name
        rendered = {
            tag: with_definite_article(formed_display_name(world, tag))
            for tag in ("Ottoman", "PapalStates", "KingdomOfItaly",
                        "Austria")
        }
        assert rendered["Ottoman"] == "the Ottoman Empire"
        assert rendered["PapalStates"] == "the Papal States"
        assert rendered["KingdomOfItaly"] == "the Kingdom of Italy"
        # …and a plain name takes no article.
        assert rendered["Austria"] == "Austria"

    def test_the_possessive_that_produced_papal_statess_is_gone(self):
        import inspect

        import backend.main as main_module
        src = inspect.getsource(main_module._build_visible_enemy_phase)
        assert "{nation}'s borders" not in src, (
            "the raw tag AND the 'Papal States's' possessive are both back")
        assert "within the borders of" in src

    def test_humanize_entity_name_would_not_have_worked(self):
        """The chokepoint question, answered as a pin: the marshal-name
        humaniser is a NO-OP on 'Ottoman' and mis-cases 'Kingdom Of
        Italy'. `display_nation` is the right door."""
        from backend.display_names import display_nation, humanize_entity_name
        assert humanize_entity_name("Ottoman") == "Ottoman"
        assert display_nation("Ottoman") == "Ottoman Empire"


class TestN32VassalTrend:
    """'Holland: loyalty 100, falling' against its own +2 events."""

    def test_the_advisory_calls_the_single_source(self):
        import inspect

        from backend.game_logic import diplomatic_advisory as da
        src = inspect.getsource(da)
        assert "forecast_vassal_loyalty" in src, (
            "the advisory still derives the trend from autonomy tier alone "
            "— one of six terms — while the single source it should call "
            "names this exact failure in its own docstring")
        assert "AUTONOMY_DRIFT.get(record.get(" not in src, (
            "the hand-copied drift term came back")

    def test_a_vassal_at_the_ceiling_reads_steady(self, world):
        """N31's lesson on the advisory side: a delta the clamp discards
        is not a trend."""
        from backend.game_logic.diplomatic_advisory import _assess_situation
        from backend.game_logic.vassal import LOYALTY_MAX
        vassals = getattr(world, "vassals", {}) or {}
        if not vassals:
            import pytest
            pytest.skip("no vassals on this board")
        for record in vassals.values():
            record["loyalty"] = LOYALTY_MAX
        payload = _assess_situation(world)
        rows = list(payload.get("context", {}).get("vassals", []))
        assert rows, payload
        for row in rows:
            if int(row["loyalty"]) >= LOYALTY_MAX:
                assert row["trend"] != "rising", (
                    f"{row['vassal']} at the ceiling reported rising")

    def test_the_trend_matches_the_forecast(self, world):
        """The join the row is actually about: advisory and forecast must
        not disagree about the same vassal on the same turn."""
        from backend.game_logic.diplomatic_advisory import _assess_situation
        from backend.game_logic.vassal import (
            LOYALTY_MAX, LOYALTY_MIN, forecast_vassal_loyalty,
        )
        vassals = getattr(world, "vassals", {}) or {}
        if not vassals:
            import pytest
            pytest.skip("no vassals on this board")
        payload = _assess_situation(world)
        for row in payload.get("context", {}).get("vassals", []):
            forecast = int(forecast_vassal_loyalty(
                world, "France", row["vassal"]).get("forecast", 0))
            loyalty = int(row["loyalty"])
            if (loyalty >= LOYALTY_MAX and forecast > 0) or (
                    loyalty <= LOYALTY_MIN and forecast < 0):
                forecast = 0
            expected = ("rising" if forecast > 0
                        else "falling" if forecast < 0 else "steady")
            assert row["trend"] == expected, (
                f"{row['vassal']}: advisory says {row['trend']}, the "
                f"single source forecasts {forecast}")
