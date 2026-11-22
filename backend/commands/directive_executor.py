"""
Directive Executor — the staff's two free books (row IC, directives; November 19, 2026).

army          form · add · remove · disband a NAMED ARMY (`backend/game_logic/armies.py`)
set_war_goal  name — or drop — the goal of a war   (`backend/game_logic/war_goals.py`)

Thin adapters (the naval and reforms executors' idiom): each reads its parts
off the line the player wrote (`armies.read_order` / `war_goals.read_order` —
the built-in parser's own readers, so the words that chose the action are the
words that fill it), calls the ONE mutation, and says what happened. Both are
the player's own bookkeeping: FREE (no action, no gold), never an order to a
marshal — so neither is in `objection_actions` (nobody objects to a list), and
neither is the enemy's to use (a court keeps no named army and no stated goal;
`_acting_nation` other than the player's is refused).

Each writes one line to the campaign log (`army_roster`, `war_goal`) and can
be taken back (`take_back.ORDER_KEYS` holds `armies` and `war_goals`).
"""
from typing import Any, Dict, List

from backend.game_logic import armies, war_goals


def _raw(command: Dict) -> str:
    for key in ("raw_command", "raw_input", "original_command"):
        words = command.get(key)
        if isinstance(words, str) and words.strip():
            return words
    return ""


def _free(result: Dict[str, Any]) -> Dict[str, Any]:
    result.setdefault("variable_action_cost", 0)
    return result


class DirectiveExecutor:
    def __init__(self, executor):
        self.executor = executor

    def _not_the_players(self, command: Dict, world) -> bool:
        actor = command.get("_acting_nation")
        return bool(actor) and actor != getattr(world, "player_nation", None)

    # ── army ────────────────────────────────────────────────────────────────

    def _execute_army(self, command: Dict, game_state: Dict) -> Dict:
        world = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}
        if self._not_the_players(command, world):
            return _free({"success": False, "message": "A court keeps no named army."})
        if not armies.armies_can_be_named():
            return _free({"success": False, "message": "Armies cannot be named in this game."})
        # Structured fields first (a caller that names the parts outright),
        # then the line as the player wrote it.
        order = None
        if command.get("army_op"):
            order = {"op": str(command.get("army_op")),
                     "name": str(command.get("army_name") or command.get("target") or ""),
                     "who": [str(n) for n in (command.get("army_members") or [])]}
        if order is None:
            order = armies.read_order(world, _raw(command))
        if order is None:
            return _free({"success": False, "message": (
                "Say what to do with an army, Sire: “form the Army of Italy with Ney and Lannes”, "
                "“add Murat to the Army of Italy”, “remove Ney from the Army of Italy” or "
                "“disband the Army of Italy” — or select the corps on the map and press "
                "“Name this army…”.")})
        outcome = armies.carry_out(world, order)
        result: Dict[str, Any] = {"success": bool(outcome.get("success")),
                                  "message": str(outcome.get("message") or "")}
        if outcome.get("success") and order["op"] != "list":
            event = {"type": "army_roster", "nation": world.player_nation,
                     "op": str(order["op"]), "army": str(outcome.get("army") or order.get("name") or ""),
                     "line": result["message"]}
            world.log_event(dict(event))
            result["events"] = [event]
            result["army"] = event["army"]
        result["armies"] = armies.payload(world)
        result["new_state"] = game_state
        return _free(result)

    # ── set_war_goal ────────────────────────────────────────────────────────

    def _execute_set_war_goal(self, command: Dict, game_state: Dict) -> Dict:
        world = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}
        if self._not_the_players(command, world):
            return _free({"success": False, "message": "A court states no war goal."})
        if not war_goals.a_war_has_a_goal():
            return _free({"success": False, "message": "War goals are not kept in this game."})
        order = None
        if command.get("goal_op"):
            order = {"op": str(command.get("goal_op")), "what": str(command.get("target") or ""),
                     "court": str(command.get("target_nation") or "")}
        if order is None:
            order = war_goals.read_order(_raw(command))
        if order is None and command.get("target"):
            order = {"op": "set", "what": str(command.get("target"))}
        if order is None:
            return _free({"success": False, "message": (
                "Name the goal, Sire: “the war goal is Vienna”, “make Mack the war goal”, or "
                "“clear the war goal” — or click a province of a court you are fighting and "
                "press “Make this the war goal”.")})
        if order["op"] == "clear":
            outcome = war_goals.clear_goal(world, str(order.get("court") or ""))
        else:
            outcome = war_goals.set_goal(world, str(order.get("what") or ""))
        result: Dict[str, Any] = {"success": bool(outcome.get("success")),
                                  "message": str(outcome.get("message") or "")}
        if outcome.get("success"):
            # Row IC, Session 3b: a goal cleared — or named on this road, which
            # turns nobody (the LIST turns the men who serve it: `army_task`) —
            # leaves each man who served it at the target he has, said.
            court = str(outcome.get("court") or "")
            new = outcome.get("goal") or {}
            keep = []
            if order["op"] != "clear":
                from backend.game_logic import own_order
                keep = [m.name for m in war_goals.serving(world, court)
                        if str((own_order.own(m) or {}).get("target") or "") == str(new.get("target") or "")]
            let_go = war_goals.release(world, keep=keep, court=court)
            if let_go:
                result["message"] = (result["message"] + " " + " ".join(let_go)).strip()
            outcome["message"] = result["message"]
            goal = outcome.get("goal") or {}
            event = {"type": "war_goal", "nation": world.player_nation,
                     "op": "clear" if order["op"] == "clear" else "set",
                     "against": str(outcome.get("court") or ""),
                     "target": str(goal.get("target") or ""), "kind": str(goal.get("kind") or ""),
                     "line": result["message"]}
            world.log_event(dict(event))
            result["events"] = [event]
        result["new_state"] = game_state
        return _free(result)
