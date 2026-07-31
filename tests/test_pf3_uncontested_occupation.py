"""PF-3 (Combat Overhaul Phase 6 — Parser & Play-Friction Cleanup).

Moving a marshal onto an EMPTY, unfortified, ungarrisoned enemy province
(uncontested occupation) previously seized nothing and gave zero feedback — only
the ATTACK path flipped control. The fix flips control via the SINGLE capture
pipeline (`_attempt_region_capture`), so it is GR5-symmetric (player -> plunder/
secure popup; AI -> auto-decision) and fortified/garrisoned provinces remain a
genuine ATTACK contest.

Legacy world layout used here: Ney (France) @ Belgium; Netherlands is Britain-
controlled, empty of marshals, garrison 15k, no fort; Waterloo holds Wellington.
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


def _world():
    world = WorldState()
    world.pending_capture_choice = None
    return world


def _move(world, marshal, target):
    executor = CommandExecutor()
    with _suppress():
        return executor._execute_move(marshal, target, world, {"world": world})


def test_uncontested_occupation_captures_and_prompts():
    """POSITIVE: Ney walks onto undefended (garrison-cleared) enemy Netherlands
    -> it flips to France and the plunder/secure popup is surfaced."""
    world = _world()
    ney = world.get_marshal("Ney")  # @ Belgium
    world.get_region("Netherlands").garrison_strength = 0
    assert world.get_region("Netherlands").controller == "Britain"
    res = _move(world, ney, "Netherlands")
    assert res["success"] is True
    assert world.get_region("Netherlands").controller == "France"
    assert res.get("pending_capture_choice") is True
    assert res.get("capture_data") is not None
    assert "falls to France" in res["message"]


def test_garrisoned_province_not_captured():
    """FALSIFIABLE NEGATIVE: a garrisoned enemy province is not seized by a mere
    move (Netherlands boots with a 15k garrison)."""
    world = _world()
    ney = world.get_marshal("Ney")
    assert world.get_region("Netherlands").garrison_strength >= 5000
    res = _move(world, ney, "Netherlands")
    assert world.get_region("Netherlands").controller == "Britain"
    assert res.get("pending_capture_choice") is not True


def test_not_at_war_province_not_captured():
    """FALSIFIABLE NEGATIVE: moving onto an open-borders (not at war) province
    does not capture it."""
    world = _world()
    ney = world.get_marshal("Ney")
    nl = world.get_region("Netherlands")
    nl.controller = "Saxony"       # France|Saxony is OPEN_BORDERS (entry allowed)
    nl.garrison_strength = 0
    res = _move(world, ney, "Netherlands")
    assert res["success"] is True
    assert world.get_region("Netherlands").controller == "Saxony"
    assert res.get("pending_capture_choice") is not True


def test_defended_province_not_captured():
    """FALSIFIABLE NEGATIVE: a visible enemy marshal present -> the move is
    refused entirely, never a silent capture (Wellington sits in Waterloo)."""
    world = _world()
    ney = world.get_marshal("Ney")
    assert any(m.location == "Waterloo" and m.nation == "Britain"
               for m in world.marshals.values())
    res = _move(world, ney, "Waterloo")
    assert res.get("success") is False
    assert world.get_region("Waterloo").controller == "Britain"
    assert res.get("pending_capture_choice") is not True


def test_friendly_province_not_captured():
    """FALSIFIABLE NEGATIVE: moving onto own territory never captures."""
    world = _world()
    ney = world.get_marshal("Ney")
    assert world.get_region("Paris").controller == "France"
    res = _move(world, ney, "Paris")
    assert world.get_region("Paris").controller == "France"
    assert res.get("pending_capture_choice") is not True


def test_gr5_enemy_move_capture_no_popup():
    """GR5 SYMMETRY: an enemy AI marshal moving onto an undefended player
    province flips control too, and auto-resolves (no player popup)."""
    world = _world()
    world.get_marshal("Ney").location = "Paris"  # vacate Belgium
    wellington = world.get_marshal("Wellington")  # @ Waterloo (adjacent to Belgium)
    world.get_region("Belgium").garrison_strength = 0
    assert world.get_region("Belgium").controller == "France"
    res = _move(world, wellington, "Belgium")
    assert world.get_region("Belgium").controller == "Britain"
    assert res.get("pending_capture_choice") is not True
    assert getattr(world, "pending_capture_choice", None) is None


# ── review-fix: a mid-march capture must not halt the turn ───────────────────

def test_pending_capture_blocks_manual_but_not_strategic_execution():
    """Review-fix regression: a pending capture choice blocks a NEW manual
    command (intended UX), but must NOT block an automated per-hop STRATEGIC
    march step — else a move-capture halts the rest of the turn."""
    world = _world()
    world.get_marshal("Ney").location = "Belgium"
    world.pending_capture_choice = {"region": "X", "capturer": "Someone",
                                    "previous_controller": "Britain"}
    executor = CommandExecutor()
    # Manual move -> blocked by the capture guard.
    with _suppress():
        manual = executor.execute(
            {"command": {"marshal": "Ney", "action": "move", "target": "Paris"}},
            {"world": world})
    assert manual.get("pending_capture_choice") is True
    assert manual.get("success") is False
    # Strategic-execution move -> NOT blocked (proceeds).
    with _suppress():
        strat = executor.execute(
            {"command": {"marshal": "Ney", "action": "move", "target": "Paris",
                         "_strategic_execution": True}},
            {"world": world})
    assert "decide how to handle the captured region" not in strat.get("message", "")


def _mk(name, adj, controller):
    r = Region(name, adj, 50)
    r.controller = controller
    return r


def test_strategic_march_capture_does_not_halt_next_hop():
    """A cavalry player marshal on a MOVE_TO order captures an undefended enemy
    province on hop 1 and STILL advances hop 2 (before the fix, the mid-march
    pending_capture_choice tripped the guard and stranded the marshal)."""
    world = WorldState()
    world.regions = {
        "A": _mk("A", ["B"], "France"),
        "B": _mk("B", ["A", "C"], "Britain"),
        "C": _mk("C", ["B"], "Britain"),
    }
    world.player_nation = "France"
    world.current_turn = 1
    world.actions_remaining = 4
    world.pending_capture_choice = None
    world.diplomatic_states[world._make_diplo_key("France", "Britain")] = "WAR"
    cav = Marshal("NeyC", "A", 40000, "aggressive", "France", movement_range=2)
    world.marshals["NeyC"] = cav
    cav.strategic_order = StrategicOrder(
        command_type="MOVE_TO", target="C", target_type="region",
        started_turn=1, original_command="NeyC march to C", path=[])
    proc = StrategicOrderProcessor(CommandExecutor())
    with _suppress():
        proc._execute_move_to(cav, world, {"world": world})
    assert cav.location == "C"                       # both hops executed
    assert world.regions["B"].controller == "France"  # hop-1 capture
    assert world.regions["C"].controller == "France"  # hop-2 capture (not halted)
    # Auto-secured (like the AI) — no per-hop popup accumulates, so the single
    # slot is never clobbered and neither capture is left dangling.
    assert world.pending_capture_choice is None
    # IGR-X5: "auto-secured" is now TRUE, not just this comment — before the
    # fix the fresh pending choice was discarded and nothing was applied, so
    # marching in was strictly better than capturing and securing.
    for name in ("B", "C"):
        assert world.regions[name].stability == 25
        assert world.regions[name].plundered is False
    captured_rows = [e for e in world.event_log
                     if e.get("type") == "region_captured"]
    assert {e["region"] for e in captured_rows} == {"B", "C"}
    assert all(e["method"] == "secure" and e["captured_by"] == "France"
               for e in captured_rows)


def test_strategic_march_capture_secures_like_an_attack_capture():
    """IGR-X5 Done-when: a march capture and an attack capture answered
    'secure' leave the province in the same state — buildings damaged,
    construction cancelled, stability 25, region_captured logged."""
    world = WorldState()
    world.regions = {
        "A": _mk("A", ["B"], "France"),
        "B": _mk("B", ["A"], "Britain"),
    }
    world.player_nation = "France"
    world.current_turn = 1
    world.actions_remaining = 4
    world.pending_capture_choice = None
    world.diplomatic_states[world._make_diplo_key("France", "Britain")] = "WAR"
    target = world.regions["B"]
    target.buildings = [{"type": "market"}]
    target.building_under_construction = {"type": "supply_depot", "turns": 2}
    soult = Marshal("Soult", "A", 40000, "aggressive", "France")
    world.marshals["Soult"] = soult
    executor = CommandExecutor()
    with _suppress():
        result = executor._execute_move(soult, "B", world, {"world": world},
                                        strategic_execution=True)
    assert target.controller == "France"
    assert target.stability == 25
    assert all(b.get("damaged") for b in target.buildings)
    assert target.building_under_construction is None
    assert world.pending_capture_choice is None
    assert "secured" in result.get("message", "")
    assert any(e.get("type") == "region_captured" and e.get("region") == "B"
               and e.get("method") == "secure" for e in world.event_log)


def test_strategic_capture_preserves_earlier_marshals_pending_choice():
    """Review-fix regression: a later marshal's strategic move-capture auto-secures
    WITHOUT discarding an EARLIER marshal's still-pending choice (e.g. from a
    PURSUE attack-capture) on the shared single-slot pending_capture_choice."""
    world = WorldState()
    world.regions = {
        "A": _mk("A", ["B"], "France"),
        "B": _mk("B", ["A"], "Britain"),
    }
    world.player_nation = "France"
    world.current_turn = 1
    world.actions_remaining = 4
    world.diplomatic_states[world._make_diplo_key("France", "Britain")] = "WAR"
    # An earlier marshal's unresolved attack-capture popup already sits in the slot.
    earlier = {"region": "Elsewhere", "capturer": "Augereau",
               "previous_controller": "Austria"}
    world.pending_capture_choice = earlier
    soult = Marshal("Soult", "A", 40000, "aggressive", "France")
    world.marshals["Soult"] = soult
    executor = CommandExecutor()
    with _suppress():
        executor._execute_move(soult, "B", world, {"world": world},
                               strategic_execution=True)
    assert world.regions["B"].controller == "France"  # Soult captured B
    assert world.pending_capture_choice == earlier     # Augereau's choice preserved
