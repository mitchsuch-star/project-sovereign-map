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
