"""PF-8 (Combat Overhaul Phase 6 — Parser & Play-Friction Cleanup).

A strategic MOVE_TO routed through impassable (PEACE / closed-border) neutral
territory and then stalled every turn with a content-free message and no order
break. The fix:
  A. pathfinding gains an optional `passable_for` constraint so a player's march
     prefers own / allied / open-border / at-war corridors (destination never
     filtered); and
  B. a stall on a diplomatic block reroutes once, else BREAKS the order with a
     reason naming the blocking nation (instead of re-stalling silently).
"""
import contextlib
import io

from backend.models.world_state import WorldState
from backend.models.region import Region
from backend.models.marshal import Marshal, StrategicOrder
from backend.commands.executor import CommandExecutor
from backend.commands.strategic import StrategicOrderProcessor


def _suppress():
    return contextlib.redirect_stdout(io.StringIO())


def _mk(name, adj, controller):
    r = Region(name, adj, 50)
    r.controller = controller
    return r


def _branched_world():
    """Start(FR) - MidH(Hanover,PEACE) - Dest(FR), plus an all-French detour
    Start - Alt1 - Alt2 - Dest."""
    world = WorldState()
    world.regions = {
        "Start": _mk("Start", ["MidH", "Alt1"], "France"),
        "MidH": _mk("MidH", ["Start", "Dest"], "Hanover"),
        "Dest": _mk("Dest", ["MidH", "Alt2"], "France"),
        "Alt1": _mk("Alt1", ["Start", "Alt2"], "France"),
        "Alt2": _mk("Alt2", ["Alt1", "Dest"], "France"),
    }
    world.player_nation = "France"
    world.diplomatic_states[world._make_diplo_key("France", "Hanover")] = "PEACE"
    return world


# ── A. routing ──────────────────────────────────────────────────────────────

def test_passable_route_avoids_closed_territory():
    world = _branched_world()
    passable = world.find_weighted_path("Start", "Dest", passable_for="France")
    terrain_only = world.find_weighted_path("Start", "Dest")
    assert "MidH" not in passable          # routed around the closed province
    assert "MidH" in terrain_only          # the terrain-shortest path went through it
    assert passable[0] == "Start" and passable[-1] == "Dest"


def test_find_path_bfs_also_respects_passable():
    world = _branched_world()
    passable = world.find_path("Start", "Dest", passable_for="France")
    assert passable is not None
    assert "MidH" not in passable


def test_destination_never_filtered():
    """A march INTO closed territory still builds a path (destination excluded
    from the filter) so it can hand off to the stall-feedback break."""
    world = _branched_world()
    path = world.find_weighted_path("Start", "MidH", passable_for="France")
    assert path is not None
    assert path[-1] == "MidH"


def test_at_war_territory_is_passable():
    """GR5 / semantics: war territory is passable (combat handles it) — only
    PEACE/closed borders are avoided."""
    world = _branched_world()
    assert world._region_passable_for("MidH", "France") is False  # PEACE
    world.diplomatic_states[world._make_diplo_key("France", "Hanover")] = "WAR"
    assert world._region_passable_for("MidH", "France") is True   # WAR passable


# ── B. stall feedback ───────────────────────────────────────────────────────

def _linear_world():
    """Start(FR) - MidH(Hanover,PEACE) - Dest(FR): the ONLY route crosses H."""
    world = WorldState()
    world.regions = {
        "Start": _mk("Start", ["MidH"], "France"),
        "MidH": _mk("MidH", ["Start", "Dest"], "Hanover"),
        "Dest": _mk("Dest", ["MidH"], "France"),
    }
    world.player_nation = "France"
    world.current_turn = 1
    world.actions_remaining = 4
    world.diplomatic_states[world._make_diplo_key("France", "Hanover")] = "PEACE"
    return world


def test_stall_on_closed_border_breaks_with_reason():
    world = _linear_world()
    marshal = Marshal("Ney2", "Start", 30000, "aggressive", "France")
    world.marshals["Ney2"] = marshal
    marshal.strategic_order = StrategicOrder(
        command_type="MOVE_TO", target="Dest", target_type="region",
        started_turn=1, original_command="Ney2 march to Dest", path=[])
    proc = StrategicOrderProcessor(CommandExecutor())
    with _suppress():
        result = proc._execute_move_to(marshal, world, {"world": world})
    # The march halts and the order is CLEARED (no eternal silent re-stall).
    assert marshal.strategic_order is None
    assert result.get("order_status") == "breaks"
    text = (result.get("message", "") + " " + result.get("reason", ""))
    assert "Hanover" in text
    assert "could not advance toward" not in text


def test_pursue_stall_on_closed_border_breaks_with_reason():
    """Review-fix regression: PURSUE (like MOVE_TO) must break with a reason on a
    diplomatic block, not re-stall silently. An enemy (Prussia) pursuer chases a
    France target across Hanover (PEACE) territory it cannot enter."""
    world = WorldState()
    world.regions = {
        "Start": _mk("Start", ["MidH"], "Prussia"),
        "MidH": _mk("MidH", ["Start", "Dest"], "Hanover"),
        "Dest": _mk("Dest", ["MidH"], "Prussia"),
    }
    world.player_nation = "France"   # so the Prussia pursuer is enemy (omniscient)
    world.current_turn = 1
    world.diplomatic_states[world._make_diplo_key("Prussia", "Hanover")] = "PEACE"
    world.diplomatic_states[world._make_diplo_key("Prussia", "France")] = "WAR"
    pursuer = Marshal("Gneisenau", "Start", 30000, "aggressive", "Prussia")
    quarry = Marshal("Ney3", "Dest", 25000, "aggressive", "France")
    world.marshals["Gneisenau"] = pursuer
    world.marshals["Ney3"] = quarry
    pursuer.strategic_order = StrategicOrder(
        command_type="PURSUE", target="Ney3", target_type="marshal",
        started_turn=1, original_command="Gneisenau pursue Ney3", path=[])
    proc = StrategicOrderProcessor(CommandExecutor())
    with _suppress():
        result = proc._execute_pursue(pursuer, world, {"world": world})
    assert pursuer.strategic_order is None
    assert result.get("order_status") == "breaks"
    text = (result.get("message", "") + " " + result.get("reason", ""))
    assert "Hanover" in text
    assert "could not advance toward" not in text
