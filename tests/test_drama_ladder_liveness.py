"""Phase 3 (Combat Overhaul, spec §3.2) — DR-3 authority-dampening rework and
integrated ladder liveness (the M7 companion).

DR-3: high authority (> 70) no longer anesthetizes the whole jealousy engine.
The "first rung" — a marshal who ALREADY resents the celebrated man (a Rival
-1 or Hostile -2, relationship-base threshold 1) — keeps his hair-trigger edge
even at the height of empire; his ambition is not calmed by the Emperor's
success. Only the neutral/friendly professionals (rung >= 2) are dampened. The
authority < 30 death-spiral acceleration is untouched.

Liveness: at authority 100 (the reviewed winning-army value), a single glory
lead opens a grievance in the once-per-turn pass — the whole point of Phase 3.
Companion metric: M7 in tests/test_combat_sweep_metrics.py.
"""

from pathlib import Path

import pytest

from backend.game_logic import jealousy as J
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _glory(world, name, points):
    J._append_glory(world.marshals[name], world.current_turn, points)


def _run_pass(world):
    world._jealousy_processed_turn = None
    return J.process_turn(world)


def _isolate(world, keep):
    """Zero out every France marshal except the named pair so the per-nation
    rate limit and hair-trigger rivals don't crowd the assertion."""
    for m in world.marshals.values():
        if m.nation == "France" and m.name not in keep:
            m.strength = 0


# ═══════════════════════ DR-3: the threshold shape ═════════════════════════


class TestThresholdShape:
    def test_rival_undampened_at_high_authority(self, world):
        # Murat -> Davout is authored Rival (-1), base threshold 1. At
        # authority 100 the OLD code raised it to 2; DR-3 exempts the first
        # rung, so it stays 1.
        murat = world.marshals["Murat"]
        davout = world.marshals["Davout"]
        gate = J._threshold_for(murat, davout, authority=100)
        assert gate is not None
        threshold, _requires_idle = gate
        assert threshold == 1

    def test_professional_still_dampened_at_high_authority(self, world):
        # Massena -> Davout has no authored edge (Professional, 0), base 2.
        # High authority still calms the professional: 2 -> 3.
        massena = world.marshals["Massena"]
        davout = world.marshals["Davout"]
        threshold, _ = J._threshold_for(massena, davout, authority=100)
        assert threshold == 3

    def test_professional_undampened_below_cutoff(self, world):
        massena = world.marshals["Massena"]
        davout = world.marshals["Davout"]
        threshold, _ = J._threshold_for(massena, davout, authority=70)
        assert threshold == 2

    def test_below_thirty_still_collapses_to_one(self, world):
        # DR-3 must not disturb the death-spiral acceleration.
        massena = world.marshals["Massena"]
        davout = world.marshals["Davout"]
        threshold, requires_idle = J._threshold_for(massena, davout, authority=20)
        assert threshold == 1
        assert requires_idle is False

    def test_idle_professional_still_dampened_while_winning(self, world):
        # An idle professional (base 2 -> idle 1) is NOT smuggled past the
        # dampening: the exemption keys on the RELATIONSHIP base, not the
        # post-idle value, so winning still calms him (1 -> back to 2).
        massena = world.marshals["Massena"]
        davout = world.marshals["Davout"]
        massena.idle_turns = J.IDLE_ACCELERATION_TURNS
        threshold, _ = J._threshold_for(massena, davout, authority=100)
        assert threshold == 2


# ═══════════════════ DR-3: end-to-end trigger at authority 100 ═════════════


class TestHighAuthorityTrigger:
    def test_rival_grievance_forms_while_winning(self, world):
        world.authority_tracker.authority = 100
        _isolate(world, {"Murat", "Davout"})
        _glory(world, "Davout", 1)          # delta 1 == rival threshold 1
        _run_pass(world)
        assert world.marshals["Murat"].jealous_of == "Davout"

    def test_professional_content_while_winning(self, world):
        world.authority_tracker.authority = 100
        _isolate(world, {"Massena", "Davout"})
        _glory(world, "Davout", 2)          # delta 2 < dampened 3 -> no fire
        _run_pass(world)
        assert world.marshals["Massena"].jealous_of is None

    def test_professional_still_fires_on_a_big_enough_gap(self, world):
        world.authority_tracker.authority = 100
        _isolate(world, {"Massena", "Davout"})
        _glory(world, "Davout", 3)          # delta 3 >= dampened 3 -> fires
        _run_pass(world)
        assert world.marshals["Massena"].jealous_of == "Davout"


# ═══════════════════════ INTEGRATED LADDER LIVENESS (M7) ═══════════════════


class TestLadderLiveness:
    def test_a_single_laurel_wakes_the_ladder_at_full_authority(self, world):
        """The Phase-3 headline: at authority 100 a lone glory lead is enough
        for a hair-trigger rival to develop a grievance within one turn pass —
        the drama engine is no longer dormant for a winning campaign."""
        world.authority_tracker.authority = 100
        # Give one marshal the army's first laurel; leave the roster otherwise
        # even. A rival one rung below should stir.
        _glory(world, "Davout", 1)
        _run_pass(world)
        stirred = [m.name for m in world.marshals.values()
                   if m.nation == "France" and getattr(m, "jealous_of", None)]
        assert stirred, "expected at least one France grievance at authority 100"

    def test_dormant_when_no_gap_exists(self, world):
        # Sanity floor: no glory anywhere -> no grievance (the engine simmers,
        # it does not invent feuds from nothing).
        world.authority_tracker.authority = 100
        _run_pass(world)
        assert not any(getattr(m, "jealous_of", None)
                       for m in world.marshals.values()
                       if m.nation == "France")
