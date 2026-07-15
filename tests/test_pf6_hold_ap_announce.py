"""PF-6 (Combat Overhaul Phase 6 — Parser & Play-Friction Cleanup).

A tactical-sounding "hold your ground" is force-upgraded to a 2-AP standing
strategic HOLD for a non-literal marshal, silently. The V2-58 pricing is
deliberate (strategic orders cost 2 AP; "defend" is the documented 1-AP
tactical hold), so the fix is legibility, not price: the HOLD result message
now announces the 2-AP upgrade inline and names the 1-AP "defend" alternative.

Scope: the note is added ONLY for a non-literal marshal's 2-AP strategic HOLD
(literal marshals keep their existing 1-AP caption; other strategic types are
untouched).
"""
import contextlib
import io

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal, Stance
from backend.models.region import Region
from backend.commands.executor import CommandExecutor


def _suppress():
    return contextlib.redirect_stdout(io.StringIO())


def _world():
    world = WorldState()
    world.marshals = {}
    world.regions = {
        "Paris": Region("Paris", ["Belgium", "Brittany"], "France", 100),
        "Belgium": Region("Belgium", ["Paris", "Rhineland", "Netherlands"], "France", 80),
        "Rhineland": Region("Rhineland", ["Belgium", "Bavaria"], "Prussia", 60),
        "Netherlands": Region("Netherlands", ["Belgium"], "Britain", 70),
        "Brittany": Region("Brittany", ["Paris"], "France", 50),
        "Bavaria": Region("Bavaria", ["Rhineland", "Austria"], "Prussia", 60),
        "Austria": Region("Austria", ["Bavaria"], "Austria", 80),
    }
    ney = Marshal("Ney", "Belgium", 30000, "aggressive", "France", cavalry=True)
    ney.morale = 80
    ney.stance = Stance.NEUTRAL
    world.marshals["Ney"] = ney
    grouchy = Marshal("Grouchy", "Brittany", 25000, "literal", "France")
    grouchy.morale = 75
    grouchy.stance = Stance.NEUTRAL
    world.marshals["Grouchy"] = grouchy
    # Enemy adjacent to Belgium so aggressive Ney does not object to HOLD.
    wellington = Marshal("Wellington", "Netherlands", 40000, "cautious", "Britain")
    wellington.morale = 90
    world.marshals["Wellington"] = wellington
    world.player_nation = "France"
    world.current_turn = 1
    world.actions_remaining = 4
    return world


def _strategic(command_dict, strategic_type):
    return {"command": command_dict, "is_strategic": True,
            "strategic_type": strategic_type}


def test_non_literal_hold_announces_2ap_and_defend_alternative():
    """POSITIVE: an aggressive marshal's strategic HOLD costs 2 AP and the
    message discloses the upgrade + the 1-AP 'defend' escape hatch."""
    world = _world()
    executor = CommandExecutor()
    with _suppress():
        result = executor.execute(
            _strategic({"marshal": "Ney", "action": "hold", "target": "Belgium"},
                       "HOLD"),
            {"world": world})
    assert result.get("pending_objection") is not True
    assert result.get("variable_action_cost") == 2
    msg = result["message"]
    assert "2 AP" in msg
    assert "defend" in msg and "1 AP" in msg


def test_literal_hold_keeps_1ap_caption_no_hold_note():
    """FALSIFIABLE NEGATIVE 1: a literal marshal keeps the 1-AP caption and does
    NOT receive the non-literal 2-AP HOLD note (proves the elif scoping)."""
    world = _world()
    executor = CommandExecutor()
    with _suppress():
        result = executor.execute(
            _strategic({"marshal": "Grouchy", "action": "hold", "target": "Brittany"},
                       "HOLD"),
            {"world": world})
    assert result.get("variable_action_cost") == 1
    msg = result["message"]
    assert "1 AP" in msg
    assert "2 AP" not in msg
    assert "standing strategic order to hold this ground" not in msg


def test_non_literal_move_has_no_hold_note():
    """FALSIFIABLE NEGATIVE 2: a non-literal MOVE_TO order does NOT carry the
    HOLD-specific note (proves the note is scoped to strategic_type == HOLD)."""
    world = _world()
    executor = CommandExecutor()
    with _suppress():
        result = executor.execute(
            _strategic({"marshal": "Ney", "action": "move", "target": "Paris"},
                       "MOVE_TO"),
            {"world": world})
    msg = result["message"]
    assert "standing strategic order to hold this ground" not in msg
    assert "'defend' at 1 AP" not in msg
