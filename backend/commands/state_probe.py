"""CRT-9 "The state speaks first" — the client half (CQ-21 / CQ-24)
(SCORE_FINISH_SPEC.md §3 Step 4, Chunk 3b; COMMAND_ROBUSTNESS_SPEC.md §12.3
row 9 and §12.16; rules SYSTEMS_REFERENCE.md §89).

The desk half and the standing-order road's fortified / drill-locked arms
landed with SF-CMD-1 part (ii). What stayed open was the SCREEN: a marshal's
STATE refuses whole families of orders at once, and neither surface knew it.

  * CQ-21 — at zero actions every Fortify / Drill / Scout / Attack chip on
    the region panel and the Generals screen stayed enabled and was refused
    ("Not enough actions! Need 1, have 0"); at zero administrative actions
    so was every build, repair and keel chip.
  * CQ-24 — the command-line completer offered orders a marshal's state
    refuses: a fortified man's `move to`, a drill-locked man's every order,
    a routed man's `attack` / `march to` / `scout` (32 lines on the turn-20
    fixture, every one Bernadotte's).

ONE pure probe answers "would this order be refused for the marshal's STATE
or for the action it costs?" — in the order the executor meets its gates:
the action pre-gate first (`executor.py`, so at zero actions the reason is
the pool), then the occupation lock, then the standing-order road's state
arms (`strategic.march_state_refusal`'s family) or the pre-objection
battery's (drill-locked, fortified, recovering, broken, wounded), then each
verb's own predicate (`drill_refusal`, `fortify_refusal`, …). It reads the
same fields with the same rules and writes nothing; the driven census in
`tests/test_crt9_the_state_speaks_first.py` sends every verb for every
staged state through `POST /command` and pins that the probe refuses
exactly what the executor refuses. The payload ships its SHORT reasons —
`tactical_state.order_refusals` for every player marshal, the same map on
the Generals cards, and the turn's `action_pools` — and the region panel,
the Generals screen and the completer read them (the chips dim with the
reason; the completer hides the line).

Player marshals only (the AI never reads a chip). Flip lever
``THE_SCREEN_READS_THE_STATE``: False ships an empty map (the screens fall
back to their own per-verb fields, as before).
"""

from __future__ import annotations

from typing import Dict, Optional

THE_SCREEN_READS_THE_STATE = True

# The verbs the screens offer, each with the executor's base action and the
# standing-order type it is upgraded to (None for a tactical order).
VERBS: Dict[str, tuple] = {
    "attack": ("attack", None),
    "scout": ("scout", None),
    "fortify": ("fortify", None),
    "unfortify": ("unfortify", None),
    "drill": ("drill", None),
    "defend": ("defend", None),
    "move": ("move", None),
    "march": ("move", "MOVE_TO"),
    "pursue": ("attack", "PURSUE"),
    "hold": ("hold", "HOLD"),
    "support": ("move", "SUPPORT"),
    "garrison": ("garrison", None),
    "retreat": ("retreat", None),
    "land": ("naval_expedition", None),
}

# The executor's pre-objection battery runs for these base actions only
# (`executor.py`'s `objection_actions`).
_BATTERY_ACTIONS = frozenset({
    "attack", "defend", "move", "scout", "recruit", "fortify",
    "stance_change", "retreat", "drill", "wait", "hold", "form_square",
})
# The actions the pre-gate never prices (`executor.py`'s `free_actions`).
_FREE_ACTIONS = frozenset({"retreat", "wait"})
# An occupying marshal may do only these (`executor.py` OCCUPATION check).
_OCCUPATION_ALLOWED = frozenset({"retreat", "wait"})


def action_pools(world) -> Dict[str, int]:
    """The turn's two pools, as the top bar states them."""
    return {
        "military": int(getattr(world, "actions_remaining", 0) or 0),
        "admin": int(getattr(world, "admin_actions_remaining", 0) or 0),
    }


def _cost(world, marshal, action: str, strategic_type: Optional[str]) -> int:
    if strategic_type:
        return int(marshal.strategic_order_ap(order_type=strategic_type))
    return int(world.get_action_cost(action))


def _pool_reason(world, marshal, action: str, strategic_type: Optional[str]) -> str:
    if action in _FREE_ACTIONS and not strategic_type:
        return ""
    if (action == "attack" and not strategic_type
            and getattr(marshal, "has_counter_punch", lambda: False)()):
        return ""  # the counter-punch waiver: the free strike stands at 0
    need = _cost(world, marshal, action, strategic_type)
    have = int(getattr(world, "actions_remaining", 0) or 0)
    if have >= need:
        return ""
    if have <= 0:
        return "no military action left this turn"
    return f"needs {need} actions — {have} left"


def _recovery_turns(marshal) -> int:
    return -(-(3 - int(getattr(marshal, "retreat_recovery", 0) or 0))
             // max(1, int(marshal.get_rally_stages_per_turn())))


def _broken_turns(marshal) -> int:
    return -(-(4 - int(getattr(marshal, "broken_recovery", 0) or 0))
             // max(1, int(marshal.get_rally_stages_per_turn())))


def _standing_reason(world, marshal, strategic_type: str) -> str:
    """The standing-order road's state arms (`strategic_executor.
    _execute_strategic_command`), in its order."""
    from backend.commands.movement_executor import RECOVERING_CORPS_TAKES_NO_GROUND
    from backend.commands.strategic import THE_STATE_SPEAKS_FIRST
    recovering = (marshal.in_retreat_recovery() if RECOVERING_CORPS_TAKES_NO_GROUND
                  else int(getattr(marshal, "retreat_recovery", 0) or 0) > 0)
    if recovering:
        return "recovering from a retreat — no standing orders"
    if THE_STATE_SPEAKS_FIRST and strategic_type not in ("HOLD", "SUPPORT"):
        if getattr(marshal, "fortified", False):
            return "fortified — unfortify first"
        if getattr(marshal, "drilling_locked", False) or getattr(marshal, "drilling", False):
            return "drilling this turn — no standing orders"
    if getattr(marshal, "broken", False):
        return "broken — only recruiting until he rallies"
    return ""


def _battery_reason(world, marshal, action: str, verb: str) -> str:
    """The pre-objection battery's state gates (`executor.py`), in order."""
    if action not in _BATTERY_ACTIONS:
        return ""
    # NP-1: the sovereign's orders skip the battery whole (he never objects
    # to himself), so its state gates are not his.
    if getattr(marshal, "is_sovereign", False):
        return ""
    if getattr(marshal, "autonomous", False):
        turns = int(getattr(marshal, "autonomy_turns", 0) or 0)
        return f"acting on his own authority — {turns} turn{'s' if turns != 1 else ''}"
    if getattr(marshal, "drilling_locked", False):
        turn = getattr(marshal, "drill_complete_turn", None)
        return (f"locked in drill until turn {int(turn)}" if turn is not None
                else "locked in drill")
    if getattr(marshal, "fortified", False) and action in ("attack", "move"):
        return "fortified — unfortify first"
    if action == "defend":
        from backend.commands.tactical_executor import defend_refusal
        _sentence, short = defend_refusal(marshal)
        if short:
            return short
    if action == "attack":
        try:
            from backend.game_logic.fortunes_of_war import wound_refusal
            if wound_refusal(marshal, world, "attack"):
                return "wounded — he cannot lead an attack"
        except Exception:
            pass
    if getattr(marshal, "retreating", False) and action in ("attack", "fortify", "drill", "scout"):
        turns = _recovery_turns(marshal)
        return f"recovering from a retreat — {turns} turn{'s' if turns != 1 else ''}"
    if getattr(marshal, "broken", False) and action != "recruit":
        turns = _broken_turns(marshal)
        return f"broken — only recruiting, {turns} turn{'s' if turns != 1 else ''}"
    return ""


def _own_reason(world, marshal, verb: str) -> str:
    """Each verb's own predicate, already the executor's (CN-4 / CX-R2)."""
    from backend.commands import tactical_executor as T
    if verb == "drill":
        return T.drill_refusal(world, marshal)[1] or ""
    if verb == "fortify":
        return T.fortify_refusal(world, marshal)[1] or ""
    if verb == "unfortify":
        return T.unfortify_refusal(marshal)[1] or ""
    return ""


def order_state_refusal(world, marshal, verb: str) -> str:
    """The SHORT reason ``<marshal>, <verb>`` would be refused for his state
    or for the action it costs — "" when neither stops it (the order may
    still be refused for its TARGET, which is each slot's own business).
    PURE."""
    if verb not in VERBS or marshal is None:
        return ""
    action, strategic_type = VERBS[verb]
    reason = _pool_reason(world, marshal, action, strategic_type)
    if reason:
        return reason
    region = getattr(marshal, "occupation_region", None)
    if region and action not in _OCCUPATION_ALLOWED:
        return f"securing {region} — no other orders"
    if strategic_type:
        return _standing_reason(world, marshal, strategic_type)
    return _battery_reason(world, marshal, action, verb) or _own_reason(world, marshal, verb)


def order_refusals(world, marshal) -> Dict[str, str]:
    """``{verb: short reason}`` for every screen verb the marshal's state or
    the turn's actions refuse (verbs that stand are absent). Player marshals
    only; empty with the lever down."""
    if (not THE_SCREEN_READS_THE_STATE or marshal is None
            or getattr(marshal, "nation", None) != getattr(world, "player_nation", None)):
        return {}
    out: Dict[str, str] = {}
    for verb in VERBS:
        reason = order_state_refusal(world, marshal, verb)
        if reason:
            out[verb] = reason
    return out
