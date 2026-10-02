"""RS-3 (Score Finish Step 3, October 2, 2026) — "the garrison stands".

A field win over the corps standing in a province whose garrison still
fights ends at the works: the victor does not advance, the province is not
taken, the garrison stands and must be assaulted — on BOTH boards, on all
three post-battle advance seams, and only while `garrison_fights` (the
order's own predicate, the desk's forecast's) says the garrison fights.
Lever `combat_executor.A_FIELD_WIN_HALTS_BEFORE_THE_WORKS`; False = the
shipped advance (the capital fell to the field win and the capture erased
its garrison).
"""
from __future__ import annotations

import ast
import contextlib
import io
import random
from pathlib import Path

import pytest

from backend.commands import combat_executor as CE
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState

SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
            / "assets" / "maps" / "europe_1805.json")


def _boot():
    world = WorldState.from_scenario(str(SCENARIO))
    executor = CommandExecutor()
    return world, executor, {"world": world, "executor": executor}


def _clear(world, *regions, keep=()):
    for m in world.marshals.values():
        if m.name not in keep and m.location in regions:
            m.location = "Hungary" if m.nation != "France" else "Berry"


def _run(executor, game_state, command):
    with contextlib.redirect_stdout(io.StringIO()):
        random.seed(1805)
        return executor.execute({"command": command}, game_state)


def _stage_vienna(victor_inside: bool = False, defender_strength: int = 40):
    """Ney (60,000) beats a dying Archduke Charles INSIDE Vienna, whose
    25,000-man garrison still fights."""
    world, executor, gs = _boot()
    vienna = world.get_region("Vienna")
    ney = world.marshals["Ney"]
    ney.location = "Vienna" if victor_inside else "Dresden"
    ney.strength = 60000
    charles = world.marshals["ArchdukeCharles"]
    charles.location = "Vienna"
    charles.strength = defender_strength
    charles.morale = 30
    _clear(world, "Vienna", "Dresden", keep=("Ney", "ArchdukeCharles"))
    assert vienna.garrison_strength == 25000 and vienna.controller == "Austria"
    return world, executor, gs, vienna, ney, charles


class TestTheFieldWinHaltsBeforeTheWorks:
    def test_the_victor_halts_outside_and_the_capital_stands(self):
        world, executor, gs, vienna, ney, charles = _stage_vienna()
        result = _run(executor, gs, {"action": "attack", "marshal": "Ney",
                                     "target": "ArchdukeCharles", "_muster_confirmed": True})
        assert result.get("success")
        assert charles.strength == 0, "the staged defender should have been destroyed"
        assert vienna.controller == "Austria", "a field win must not take a garrisoned capital"
        assert vienna.garrison_strength == 25000, "the garrison must not be erased by the win"
        assert ney.location == "Dresden", "the victor halts before the works"
        assert "halts before Vienna's works" in result["message"]
        assert "25,000 still stands and must be assaulted" in result["message"]

    def test_a_co_located_victor_takes_nothing_either(self):
        world, executor, gs, vienna, ney, charles = _stage_vienna(victor_inside=True)
        result = _run(executor, gs, {"action": "attack", "marshal": "Ney",
                                     "target": "ArchdukeCharles", "_muster_confirmed": True})
        assert result.get("success") and charles.strength == 0
        assert vienna.controller == "Austria" and vienna.garrison_strength == 25000
        assert ney.location == "Vienna"
        assert "must be assaulted" in result["message"]

    def test_the_scouts_sentence_is_true_of_the_attack(self):
        """SR-4a's scout says 'it must be assaulted' of this garrison; the
        attack's own answer now says the same thing of the same garrison."""
        from backend.game_logic.garrison_report import describe_garrison
        world, executor, gs, vienna, ney, charles = _stage_vienna()
        scout = describe_garrison(world, vienna, "France")
        assert "must be assaulted" in scout
        result = _run(executor, gs, {"action": "attack", "marshal": "Ney",
                                     "target": "ArchdukeCharles", "_muster_confirmed": True})
        assert "must be assaulted" in result["message"]

    def test_gr5_a_french_corps_in_paris_does_not_hand_paris_over(self):
        """The other board: Mack beats a dying Lannes inside Paris — Paris's
        25,000 stand and Mack halts at Champagne."""
        world, executor, gs = _boot()
        paris = world.get_region("Paris")
        mack = world.marshals["Mack"]
        mack.location = "Champagne"
        mack.strength = 60000
        lannes = world.marshals["Lannes"]
        lannes.location = "Paris"
        lannes.strength = 40
        lannes.morale = 30
        _clear(world, "Paris", "Champagne", keep=("Mack", "Lannes"))
        assert paris.garrison_strength == 25000
        result = _run(executor, gs, {"action": "attack", "marshal": "Mack", "target": "Lannes",
                                     "_acting_nation": "Austria", "_muster_confirmed": True})
        assert result.get("success")
        assert paris.controller == "France" and paris.garrison_strength == 25000
        assert mack.location == "Champagne"
        assert "halts before Paris's works" in result["message"]

    def test_a_garrison_below_the_collapse_line_does_not_halt(self):
        """`garrison_fights` is the predicate: 4,999 men give way to the
        first corps that marches in, so the win still takes the province."""
        world, executor, gs, vienna, ney, charles = _stage_vienna()
        vienna.garrison_strength = 4999
        result = _run(executor, gs, {"action": "attack", "marshal": "Ney",
                                     "target": "ArchdukeCharles", "_muster_confirmed": True})
        assert result.get("success") and charles.strength == 0
        assert ney.location == "Vienna"
        assert vienna.controller == "France" or getattr(ney, "occupation_region", None) == "Vienna" \
            or world.pending_capture_choice is not None
        assert "halts before" not in result["message"]

    def test_a_detachment_fights_to_the_last_man_and_halts_the_win(self):
        world, executor, gs = _boot()
        bohemia = world.get_region("Bohemia")
        bohemia.garrison_strength = 800     # above SR-7a's surrender floor: it fights to the last man
        bohemia.garrison_detachment = True
        ney = world.marshals["Ney"]
        ney.location = "Dresden"
        ney.strength = 60000
        charles = world.marshals["ArchdukeCharles"]
        charles.location = "Bohemia"
        charles.strength = 40
        charles.morale = 30
        _clear(world, "Bohemia", "Dresden", keep=("Ney", "ArchdukeCharles"))
        result = _run(executor, gs, {"action": "attack", "marshal": "Ney",
                                     "target": "ArchdukeCharles", "_muster_confirmed": True})
        assert result.get("success")
        assert bohemia.controller == "Austria" and bohemia.garrison_strength == 800
        assert "a detachment that fights to the last man of 800" in result["message"]

    def test_the_charge_exit_reads_the_same_rule(self):
        world, executor, gs = _boot()
        vienna = world.get_region("Vienna")
        murat = world.marshals["Murat"]
        murat.location = "Dresden"
        murat.strength = 60000
        murat.recklessness = 1   # a glorious charge needs one victory on the record
        charles = world.marshals["ArchdukeCharles"]
        charles.location = "Vienna"
        charles.strength = 40
        charles.morale = 30
        _clear(world, "Vienna", "Dresden", keep=("Murat", "ArchdukeCharles"))
        result = _run(executor, gs, {"action": "charge", "marshal": "Murat",
                                     "target": "ArchdukeCharles", "_muster_confirmed": True})
        assert result.get("success"), result.get("message")
        assert vienna.controller == "Austria" and vienna.garrison_strength == 25000
        assert murat.location == "Dresden"
        assert "halts before Vienna's works" in result["message"]

    def test_lever_down_the_capital_falls_to_the_field_win(self, monkeypatch):
        """The shipped behaviour, byte for byte: the victor advances and the
        capture seam erases the garrison with the walls."""
        monkeypatch.setattr(CE, "A_FIELD_WIN_HALTS_BEFORE_THE_WORKS", False)
        world, executor, gs, vienna, ney, charles = _stage_vienna()
        result = _run(executor, gs, {"action": "attack", "marshal": "Ney",
                                     "target": "ArchdukeCharles", "_muster_confirmed": True})
        assert result.get("success") and charles.strength == 0
        assert ney.location == "Vienna"
        assert "halts before" not in result["message"]
        # the capture ran (instant, or a plunder/secure question on the desk)
        assert vienna.controller == "France" or world.pending_capture_choice is not None \
            or getattr(ney, "occupation_region", None) == "Vienna"


class TestTheHelper:
    def test_pure_and_fog_free_on_our_own_soil(self):
        world, _executor, _gs = _boot()
        ney = world.marshals["Ney"]
        paris = world.get_region("Paris")
        assert CE.works_halt_line(world, ney, paris) == ""
        assert CE.works_halt_line(world, ney, None) == ""

    def test_a_court_at_peace_never_halts(self):
        world, _executor, _gs = _boot()
        ney = world.marshals["Ney"]
        berlin = world.get_region("Berlin")
        assert not world.is_at_war("France", "Prussia")
        assert berlin.garrison_strength >= 5000
        assert CE.works_halt_line(world, ney, berlin) == ""

    def test_every_post_battle_advance_seam_reads_the_helper(self):
        """The three seams: the field win, the auto-bombardment kill and the
        charge — each calls `works_halt_line` (AST, not a string grep)."""
        src = Path(CE.__file__).read_text(encoding="utf-8")
        tree = ast.parse(src)
        callers: dict = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                calls = sum(
                    1 for sub in ast.walk(node)
                    if isinstance(sub, ast.Call)
                    and getattr(sub.func, "id", None) == "works_halt_line")
                if calls:
                    callers[node.name] = calls
        assert callers.get("_execute_attack", 0) >= 2, callers   # the field win + the auto-bombard exit
        assert callers.get("_execute_glorious_charge", 0) >= 2, callers
