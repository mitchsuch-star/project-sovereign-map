"""PT-F1 — pursuit-battle capture of neutral/allied soil (Aug 1, 2026).

Seen live twice in the played-world re-measure:
(a) Mack routed into Nassau — HESSE's province, a court at PEACE with
    France. Ney pursued, destroyed him, and Nassau silently became French;
    Hesse stayed at relation 0 and wrote a non-aggression letter two turns
    later. Only the global threat scalar noticed.
(b) Retro-discovered: Swabia is BAVARIAN at boot (Mack merely occupies
    it), so the session's Ulm strike transferred a bloc ALLY's province to
    France, equally unremarked.

Stage-D pin 15 closed the movement-capture hole; the battle-advance path
never passed that seam. The gate question was delegated ("make the
decision yourself") and decided AS RECOMMENDED on the BUG_FIXES row:

  (i)  NEUTRAL court  -> the pin-15 War Purpose flow: the advance halts at
       the frontier, nothing transfers, and the player is offered the
       declaration (the Ansbach moment). The AI restrains — its war
       decisions belong to the Stage-D machinery, never to a pursuit's
       momentum.
  (iii) ALLY/VASSAL   -> pursuit is not conquest: the victor advances as a
       liberator, the province stays its owner's.

One predicate (`_pursuit_capture_guard`, keyed on the region's CONTROLLER
at the moment of transfer) guards all four capture doors: the main
battle-advance, the auto-bombardment advance, the glorious charge, and the
reckless auto-charge's bare controller assignment in world_state.
"""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
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
# The Nassau shape — a NEUTRAL court's soil (arm i)
# ═══════════════════════════════════════════════════════════════════════

class TestNeutralSoilPursuit:
    def _nassau_board(self, world):
        # The live shape: Mack routed into Nassau (Hesse — PEACE with
        # France); Ney stands adjacent at Rhineland, his boot position.
        mack = _weaken(world, "Mack")
        mack.location = "Nassau"
        assert world.get_region("Nassau").controller == "Hesse"
        assert world.get_diplomatic_state("France", "Hesse") == "PEACE"
        assert world.marshals["Ney"].location == "Rhineland"
        return mack

    def test_nassau_never_transfers_and_the_war_purpose_is_staged(
            self, world, executor):
        self._nassau_board(world)
        result = _attack(world, executor, "Ney", "Mack")

        assert result.get("success"), result.get("message")
        assert world.get_region("Nassau").controller == "Hesse", (
            "a pursuit battle annexed a neutral court's province with no "
            "declaration — the live Nassau capture")
        # The frontier halt: no uninvited army on peaceful soil.
        assert world.marshals["Ney"].location == "Rhineland"
        # No war was declared FOR the player...
        assert world.get_diplomatic_state("France", "Hesse") == "PEACE"
        # ...but the choice is offered — the pin-15 dialogue, staged.
        dlg = world.pending_diplomatic_dialogue
        assert dlg is not None and dlg.get("type") == "war_purpose_selection"
        assert dlg.get("target_nation") == "Hesse"
        # And no plunder/secure prompt for a province that never fell.
        assert world.pending_capture_choice is None
        msg = str(result.get("message", ""))
        assert "halts at the frontier of Nassau" in msg
        assert "make war on Hesse" in msg

    def test_no_capture_threat_accrues_for_the_untaken_province(
            self, world, executor):
        """The live report: 'only the global threat scalar noticed (+15)'.
        With no transfer there is no region_capture/capital_capture threat;
        the honest battle_win accrual stays."""
        self._nassau_board(world)
        before = int(getattr(world, "threat_level", 0) or 0)
        _attack(world, executor, "Ney", "Mack")
        delta = int(getattr(world, "threat_level", 0) or 0) - before
        assert delta <= 8, (
            f"threat rose {delta} — a capture-family accrual fired for a "
            f"province that never changed hands")


# ═══════════════════════════════════════════════════════════════════════
# The boot-Swabia shape — an ALLY's occupied soil (arm iii)
# ═══════════════════════════════════════════════════════════════════════

class TestAlliedSoilPursuit:
    def test_ulm_liberates_swabia_for_bavaria_not_france(
            self, world, executor):
        # The literal boot board: Mack OCCUPIES Bavarian Swabia; Ney at
        # Rhineland. The historical Ulm strike, exactly as played live.
        _weaken(world, "Mack")
        assert world.marshals["Mack"].location == "Swabia"
        assert world.get_region("Swabia").controller == "Bavaria"
        assert world.get_diplomatic_state("France", "Bavaria") == "ALLIANCE"

        result = _attack(world, executor, "Ney", "Mack")

        assert result.get("success"), result.get("message")
        assert world.get_region("Swabia").controller == "Bavaria", (
            "the Ulm pursuit annexed a bloc ALLY's province — the live "
            "boot-Swabia transfer")
        # The liberator advances — driving the enemy off an ally's soil is
        # the whole point of the alliance.
        assert world.marshals["Ney"].location == "Swabia"
        assert world.get_diplomatic_state("France", "Bavaria") == "ALLIANCE"
        assert world.pending_capture_choice is None, (
            "no plunder/secure prompt on an ally's town")
        dlg = world.pending_diplomatic_dialogue
        assert not (dlg and dlg.get("type") == "war_purpose_selection"), (
            "no war-purpose question against our own ally")
        msg = str(result.get("message", ""))
        assert "Swabia remains Bavaria's soil" in msg


# ═══════════════════════════════════════════════════════════════════════
# The control arm — an at-war court's soil still falls
# ═══════════════════════════════════════════════════════════════════════

class TestAtWarSoilStillFalls:
    def test_pursuit_onto_austrian_soil_captures_as_before(
            self, world, executor):
        """Massena at Milan strikes Mack on Tyrol — AUSTRIA's own soil,
        and France is at war with Austria. The guard must not over-capture:
        this is ordinary conquest and proceeds exactly as before."""
        mack = _weaken(world, "Mack", 3000)
        mack.location = "Tyrol"
        # ArchdukeJohn boots at Tyrol — clear him so the field is Mack's
        # alone and the capture question is actually reached.
        world.marshals["ArchdukeJohn"].location = "Vienna"
        assert world.get_region("Tyrol").controller == "Austria"
        assert world.is_at_war("France", "Austria")
        assert world.marshals["Massena"].location == "Milan"

        result = _attack(world, executor, "Massena", "Mack")

        assert result.get("success"), result.get("message")
        assert world.get_region("Tyrol").controller == "France", (
            "the guard blocked a legitimate at-war conquest")
        assert world.pending_capture_choice is not None, (
            "the plunder/secure choice must still fire for a real conquest")


# ═══════════════════════════════════════════════════════════════════════
# GR5 — the AI arm: same predicate, restrained answer
# ═══════════════════════════════════════════════════════════════════════

class TestAIPursuitRestraint:
    def test_ai_victor_never_annexes_neutral_soil_nor_declares(
            self, world, executor):
        """Austria's Mack destroys a French corps standing in Nassau
        (Hesse — at PEACE with Austria). Same guard, same halt: no
        transfer, no auto-declaration, no dialogue for an AI."""
        davout = _weaken(world, "Davout", 4000)
        davout.location = "Nassau"
        mack = world.marshals["Mack"]
        assert mack.location == "Swabia"  # adjacent to Nassau
        assert world.get_diplomatic_state("Austria", "Hesse") == "PEACE"
        world.dialogue_manager.clear_all() if hasattr(
            world.dialogue_manager, "clear_all") else None

        result = _attack(world, executor, "Mack", "Davout")

        assert result.get("success"), result.get("message")
        assert world.get_region("Nassau").controller == "Hesse", (
            "the AI farmed the pursuit hole the player just lost")
        assert mack.location == "Swabia", "the AI halts at the frontier too"
        assert world.get_diplomatic_state("Austria", "Hesse") == "PEACE", (
            "a pursuit's momentum must never make the AI's war decisions — "
            "those belong to the Stage-D machinery")
        dlg = world.pending_diplomatic_dialogue
        assert not (dlg and dlg.get("type") == "war_purpose_selection")


# ═══════════════════════════════════════════════════════════════════════
# The other two capture doors share the guard
# ═══════════════════════════════════════════════════════════════════════

class TestGloriousChargeDoor:
    def test_charge_onto_neutral_soil_never_transfers(self, world, executor):
        mack = _weaken(world, "Mack")
        mack.location = "Nassau"
        murat = world.marshals["Murat"]
        murat.location = "Rhineland"
        world.actions_remaining = 4
        random.seed(7)

        result = executor._combat._execute_glorious_charge(
            murat, "Mack", world, {"world": world})

        assert result.get("success"), result.get("message")
        assert world.get_region("Nassau").controller == "Hesse", (
            "the charge door bypassed the pursuit guard")
        assert world.pending_capture_choice is None
        if murat.strength > 0 and murat.location == "Nassau":
            # Victory case: the choice is offered, the annexation is not.
            dlg = world.pending_diplomatic_dialogue
            assert dlg is not None and dlg.get("type") == "war_purpose_selection"


class TestRecklessAutoChargeDoor:
    def test_auto_charge_win_leaves_neutral_soil_alone(self, world):
        mack = _weaken(world, "Mack", 3000)
        mack.location = "Nassau"
        murat = world.marshals["Murat"]
        murat.location = "Rhineland"
        murat.recklessness = 4
        # Clear other adjacent temptations: the boot board leaves Mack the
        # only enemy in reach of Rhineland once he stands in Nassau.
        random.seed(7)

        events = world._process_reckless_cavalry_turn_start()

        charges = [e for e in events
                   if e.get("type") == "auto_glorious_charge"
                   and e.get("marshal") == "Murat"]
        assert charges, (
            "the auto-charge never fired — this board no longer covers the "
            "world_state capture door; re-derive the shape")
        assert world.get_region("Nassau").controller == "Hesse", (
            "the auto-charge's bare controller assignment bypassed the "
            "pursuit guard")
