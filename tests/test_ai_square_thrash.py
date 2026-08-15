"""PT-F6 — the AI square-thrash (August 1, 2026 live-playthrough finding).

Seen live every enemy phase from turn 3: Moore formed square at Nivernais
THREE times in one phase, breaking it himself each time (stance change,
then counter-punch, then re-form); Archduke Charles and Castanos produced
the same transcript shape. Mechanism: the P2.5 break rung sets
``ai_square_cooldown``, but ``_auto_break_square`` (fired when the AI's own
attack/move/stance change breaks the square) sets nothing — so the planner
re-formed the square it had just broken, burning AP and reading as farce
("the enemy phase as theater: 5.5", AI_V_SWEEP_2026_08_01.md §10.4).

The fix, both halves at execution seams (never inside evaluation):
1. THE LATCH — ``self._squares_formed_this_turn``: a marshal forms square
   at most once per enemy phase (BUG_FIXES.md's completion criterion).
2. THE STANCE GUARD — a marshal standing in square holds his posture: the
   central candidate filter skips stance changes for in-square marshals
   (the S5-1 fortify guards' missing sibling). Attack/move breaks stay
   legal — abandoning a square for a counter-blow is a choice; fidgeting
   out of it via stance is the farce.

Falsifiability: every phase test here carries a NEUTERED control arm (the
latch/guard structurally disabled) that must still reproduce the thrash —
if the board drifts and the shape stops provoking, the control fails loud
instead of the real assertion passing vacuously.

Harness note (BUG_FIXES.md PT-F6): this slice is harness-sensitive.
M1–M7 + BASELINE_SERIES were run before and after the change; verdict
recorded in the landing record (docs/STATUS.md + BUG_FIXES.md strike).
"""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
from backend.models.marshal import Stance
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


class _NeverSet(set):
    """A set that refuses membership — the latch, structurally disabled."""

    def add(self, x):
        pass

    def __contains__(self, x):
        return False


class _ThrashAI(EnemyAI):
    """The pre-fix planner: latch neutered AND the in-square stance guard
    bypassed (its skip keys off ``square_formation`` via this property's
    sibling check in ``_select_next_marshal_action`` — we disable only the
    latch here; the stance-guard control uses the shape where the attack
    is the breaker, which the guard never touches)."""

    @property
    def _squares_formed_this_turn(self):
        return _NeverSet()

    @_squares_formed_this_turn.setter
    def _squares_formed_this_turn(self, v):
        pass


def _counter_punch_shape(world):
    """The live Moore shape, counter-punch as the breaker: infantry with
    enemy cavalry ADJACENT (co-location routes to P0 instead), stance
    already defensive so P3 stays quiet, and a banked counter-punch.

    Phase script this provokes (latch neutered):
    form_square -> counter-punch attack (breaks it) -> form_square -> ...

    THE SHAPE MOVED ASHORE (NV-4, August 2, 2026). It used to stand Moore
    in London against Murat across the Channel at Flanders, and the whole
    test rested on Moore ATTACKING over that water. The naval host rule
    refuses an amphibious assault as an ordinary attack, so the breaker
    stopped firing and this file's own coverage guard caught it — exactly
    what that guard is for. Re-derived on land: a British beachhead in
    Normandy with Murat's cavalry one march away at Maine. The square
    trigger (adjacent enemy cavalry) and the breaker (a counter-punch that
    can actually be delivered) are both real again, and nothing about what
    is under test changed."""
    moore = world.marshals["Moore"]
    murat = world.marshals["Murat"]
    assert getattr(murat, "cavalry", False), "the shape needs real cavalry"
    world.regions["Normandy"].controller = "Britain"
    world.invalidate_active_nations_cache()
    moore.location = "Normandy"  # the beachhead — land contact with France
    murat.location = "Maine"     # land-adjacent to Normandy
    murat.strength = 40000       # the counter-punch loses; cavalry stays
    # NP-A (Aug 15, 2026): Napoleon boots at Paris — one march from the
    # Normandy beachhead — and his small Guard was a BETTER counter-punch
    # ratio than the planted Murat, so Moore attacked the Emperor instead
    # of thrashing. The shape isolates him: this file tests the square
    # latch, not the sovereign.
    world.marshals["Napoleon"].location = "Lorraine"
    moore.stance = Stance.DEFENSIVE
    moore.counter_punch_available = True
    world._build_marshal_index()
    return moore


def _stance_breaker_shape(world):
    """The other live breaker: NEUTRAL stance so P3 wants a defensive
    stance change — which would break the square just formed."""
    moore = world.marshals["Moore"]
    murat = world.marshals["Murat"]
    # NV-8c: the Flanders line is cut — Normandy is the link adjacent to
    # London, so the invasion-scare cavalry threat stands there now.
    murat.location = "Normandy"
    murat.strength = 40000
    moore.stance = Stance.NEUTRAL
    moore.counter_punch_available = False
    return moore


def _run_phase(ai_cls, world):
    random.seed(42)
    ai = ai_cls(CommandExecutor())
    results = ai.process_nation_turn("Britain", world, {"world": world})
    return [(r.get("ai_action") or {}) for r in results]


def _forms_by(actions, name):
    return [a for a in actions
            if a.get("action") == "form_square" and a.get("marshal") == name]


# ═══════════════════════════════════════════════════════════════════════
# 1. The phase-transcript criterion: ≤1 square formation per marshal
# ═══════════════════════════════════════════════════════════════════════

class TestSquareFormedAtMostOncePerPhase:
    def test_control_arm_the_shape_still_provokes_the_thrash(self, world):
        """With the latch structurally disabled, the counter-punch shape
        must still produce ≥2 formations — else the real test is vacuous."""
        _counter_punch_shape(world)
        actions = _run_phase(_ThrashAI, world)
        assert len(_forms_by(actions, "Moore")) >= 2, (
            "the reproduction shape no longer provokes the thrash — the "
            "board drifted; re-derive the shape before trusting the pins")

    def test_production_ai_forms_square_at_most_once(self, world):
        _counter_punch_shape(world)
        actions = _run_phase(EnemyAI, world)
        forms = _forms_by(actions, "Moore")
        assert len(forms) <= 1, (
            f"square-thrash: Moore formed square {len(forms)} times in one "
            f"enemy phase — {[a.get('action') for a in actions]}")
        # The latch must have been EXERCISED, not idle: he formed once and
        # his own later action broke the square (the counter-punch).
        assert len(forms) == 1
        seq = [a.get("action") for a in actions if a.get("marshal") == "Moore"]
        assert "attack" in seq[seq.index("form_square"):], (
            "the breaker never fired — this run no longer covers the latch")


# ═══════════════════════════════════════════════════════════════════════
# 2. The stance guard: an in-square marshal holds his posture
# ═══════════════════════════════════════════════════════════════════════

class TestInSquareStanceGuard:
    def test_stance_change_never_breaks_a_standing_square(self, world):
        """Live breaker #1: P3 wanted a defensive stance for the marshal
        who had JUST formed square, breaking it one action later. The
        central filter now skips stance changes for in-square marshals."""
        _stance_breaker_shape(world)
        actions = _run_phase(EnemyAI, world)
        seq = [a.get("action") for a in actions if a.get("marshal") == "Moore"]
        assert "form_square" in seq
        assert "stance_change" not in seq[seq.index("form_square"):], (
            "the AI fidgeted out of its own square via stance change")

    def test_stance_change_still_free_when_not_in_square(self, world):
        """Positive control: the guard is square-scoped — the same shape
        WITHOUT the square trigger (no adjacent cavalry) must leave the
        P3 defensive stance change reachable."""
        moore = _stance_breaker_shape(world)
        murat = world.marshals["Murat"]
        murat.cavalry = False  # no square trigger; still a stronger threat
        actions = _run_phase(EnemyAI, world)
        seq = [a.get("action") for a in actions if a.get("marshal") == "Moore"]
        assert "form_square" not in seq
        assert "stance_change" in seq, (
            "the guard over-captured: stance changes must stay legal for "
            "marshals not standing in square")
        assert moore.stance == Stance.DEFENSIVE


# ═══════════════════════════════════════════════════════════════════════
# 3. The latch at the rung level (the cooldown test's sibling idiom)
# ═══════════════════════════════════════════════════════════════════════

class TestLatchAtTheRung:
    def _eval(self, ai, world):
        moore = world.marshals["Moore"]
        world.marshals["Murat"].location = "Normandy"  # NV-8c: the link
        world.marshals["Murat"].strength = 40000
        ai._enter_indexed_evaluation_scope(world)
        try:
            return ai._evaluate_marshal(moore, "Britain", world)
        finally:
            ai._exit_indexed_evaluation_scope()

    def test_latched_marshal_does_not_reform(self, world):
        ai = EnemyAI(CommandExecutor())
        ai._squares_formed_this_turn = {"Moore"}
        action, _prio = self._eval(ai, world)
        assert not (action and action.get("action") == "form_square"), (
            "P2.5 re-formed a square for a marshal already latched this phase")

    def test_unlatched_marshal_forms(self, world):
        """Positive control for the pin above — same board, empty latch."""
        ai = EnemyAI(CommandExecutor())
        ai._squares_formed_this_turn = set()
        action, _prio = self._eval(ai, world)
        assert action and action.get("action") == "form_square", (
            "the baseline form rung stopped firing — the latch test above "
            "would now pass vacuously")
