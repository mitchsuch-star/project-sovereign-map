"""Score Finish Step 3 (October 2, 2026) — combat legibility C1 at the
exit: the attack an answered contact question commits to prints its muster.

Measured on the FLD arm, turn 7: `Ney, attack Archduke John` raised the
`contact_bad_odds` question ("Odds unfavorable. Your orders?"), the driver
answered `attack_anyway`, and the battle opened straight onto the combat
lines — the re-issue rode `_strategic_execution` alone, which skips the
muster block. RS-13's family (the pressed attack prints its muster), one
road over: the re-issue now carries `_muster_confirmed`, the muster block
rides the battle, the confirm popup stays off.
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

from backend.commands import strategic as strategic_mod
from backend.commands.executor import CommandExecutor
from backend.commands.strategic import StrategicOrderProcessor
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState

SCENARIO = str(Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
               / "assets" / "maps" / "europe_1805.json")


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _contact():
    """Davout at Rhineland under MOVE_TO Munich; Mack stands on the road at
    Nassau; the contact question is on the desk."""
    with _quiet():
        world = WorldState.from_scenario(SCENARIO)
    davout = world.get_marshal("Davout")
    mack = world.get_marshal("Mack")
    davout.location = "Rhineland"
    davout.strategic_order = StrategicOrder(
        command_type="MOVE_TO", target="Munich", target_type="region",
        started_turn=world.current_turn, original_command="Davout, march to Munich",
        path=["Nassau", "Munich"])
    mack.location = "Nassau"
    mack.strength = 30000
    world.invalidate_active_nations_cache()
    world._build_marshal_index()
    world.calculate_visibility()
    pending = {"interrupt_type": "contact_bad_odds", "enemy": "Mack",
               "location": "Nassau", "marshal": "Davout",
               "options": ["attack_anyway", "go_around", "hold_position", "cancel_order"]}
    davout.pending_interrupt = pending
    return world, davout, mack, pending


def _answer(world, davout, pending, choice="attack_anyway"):
    proc = StrategicOrderProcessor(CommandExecutor())
    with _quiet():
        return proc._respond_blocked_path(davout, davout.strategic_order, choice,
                                          pending, world, {"world": world})


def _text(reply) -> str:
    return " ".join(str(reply.get(k) or "") for k in ("message", "battle_message"))


class TestTheAnsweredContactPrintsItsMuster:
    def test_attack_anyway_opens_on_the_muster(self):
        world, davout, mack, pending = _contact()
        before = mack.strength
        reply = _answer(world, davout, pending)
        assert mack.strength < before, "the answer fought"
        assert "MUSTER" in _text(reply), _text(reply)[:300]
        assert reply.get("requires_input") is not True, "the confirm popup stays off"

    def test_lever_down_the_battle_opens_bare(self, monkeypatch):
        monkeypatch.setattr(strategic_mod, "THE_ANSWERED_CONTACT_PRINTS_ITS_MUSTER", False)
        world, davout, mack, pending = _contact()
        before = mack.strength
        reply = _answer(world, davout, pending)
        assert mack.strength < before
        assert "MUSTER" not in _text(reply)

    def test_the_ai_road_is_untouched(self):
        """An AI strategic re-issue carries no `_muster_confirmed` — the
        preview is a player legibility surface (GR5: the AI prices its own)."""
        world, davout, mack, pending = _contact()
        davout.nation = "Austria"
        mack.nation = "France"
        world.invalidate_active_nations_cache()
        world._build_marshal_index()
        reply = _answer(world, davout, pending)
        assert "MUSTER" not in _text(reply)
