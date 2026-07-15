"""PF-4 (Combat Overhaul Phase 6 — Parser & Play-Friction Cleanup).

An attack order whose target is OUT OF RANGE is never a tactical fight: inside
`_execute_attack` it becomes a strategic PURSUE (with its own, correct strategic
objection), an artillery hard-fail, or a 'cannot reach' error. Yet the TACTICAL
objection was evaluated first — so the player could pay a trust-costing INSIST
on an order that never engages, and a cautious marshal could then draw a SECOND
(strategic) objection.

The fix pre-validates reachability BEFORE the objection check (single-sourcing
`_execute_attack`'s `world.get_distance` vs `marshal.movement_range` primitive)
and skips only the tactical objection when the target is resolvable but out of
range. In-range attacks still object normally.
"""
import contextlib
import io

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal, Stance
from backend.models.region import Region
from backend.commands.executor import CommandExecutor


def _suppress():
    return contextlib.redirect_stdout(io.StringIO())


def _world(blucher_location):
    """Chain Paris(1)-Belgium(1)-Rhineland(2)-Bavaria(3) from Paris."""
    world = WorldState()
    world.marshals = {}
    world.regions = {
        "Paris": Region("Paris", ["Belgium"], "France", 100),
        "Belgium": Region("Belgium", ["Paris", "Rhineland"], "France", 80),
        "Rhineland": Region("Rhineland", ["Belgium", "Bavaria"], "Prussia", 60),
        "Bavaria": Region("Bavaria", ["Rhineland"], "Prussia", 60),
    }
    davout = Marshal("Davout", "Paris", 20000, "cautious", "France")
    davout.morale = 80
    davout.stance = Stance.NEUTRAL
    assert davout.movement_range == 1, "Davout must be infantry (range 1)"
    world.marshals["Davout"] = davout
    blucher = Marshal("Blucher", blucher_location, 60000, "aggressive", "Prussia")
    blucher.morale = 85
    world.marshals["Blucher"] = blucher
    world.player_nation = "France"
    world.current_turn = 1
    world.actions_remaining = 4
    return world


def _attack(command_dict):
    return {"command": command_dict}


# ── unit: the reachability probe ────────────────────────────────────────────

def test_probe_true_when_out_of_range():
    world = _world("Rhineland")  # distance 2 from Paris > range 1
    ex = CommandExecutor()
    davout = world.marshals["Davout"]
    assert ex._attack_target_beyond_range(davout, "Blucher", world) is True


def test_probe_false_when_in_range():
    world = _world("Belgium")  # distance 1 == range 1
    ex = CommandExecutor()
    davout = world.marshals["Davout"]
    assert ex._attack_target_beyond_range(davout, "Blucher", world) is False


def test_probe_false_for_bare_and_unresolvable_target():
    world = _world("Rhineland")
    ex = CommandExecutor()
    davout = world.marshals["Davout"]
    assert ex._attack_target_beyond_range(davout, None, world) is False
    assert ex._attack_target_beyond_range(davout, "", world) is False
    assert ex._attack_target_beyond_range(davout, "Zzyzx", world) is False


# ── integration: objection is skipped only when out of range ────────────────

def test_out_of_range_attack_skips_tactical_objection():
    """POSITIVE: a cautious marshal ordered to attack a distant, stronger enemy
    no longer raises the wasted TACTICAL objection (the order becomes a
    strategic PURSUE with its own channel)."""
    world = _world("Rhineland")
    ex = CommandExecutor()
    with _suppress():
        ex.execute(_attack({"marshal": "Davout", "action": "attack",
                            "target": "Blucher"}), {"world": world})
    assert world.pending_objection is None


def test_in_range_bad_odds_attack_still_objects():
    """FALSIFIABLE NEGATIVE (scope guard): with the enemy IN range and bad odds,
    the cautious marshal's tactical objection DOES still fire — the suppression
    is scoped strictly to out-of-range."""
    world = _world("Belgium")  # in range, 3:1 against Davout -> cautious objects
    ex = CommandExecutor()
    with _suppress():
        result = ex.execute(_attack({"marshal": "Davout", "action": "attack",
                                     "target": "Blucher"}), {"world": world})
    fired = (world.pending_objection is not None
             or result.get("pending_objection") is True
             or "objection" in result)
    assert fired, "in-range bad-odds attack should still raise a tactical objection"
