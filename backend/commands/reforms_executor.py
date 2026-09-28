"""
Reforms Executor — the laws' two verbs (SR-5r RF-1, docs/REFORMS_SPEC.md §2)

enact_law · repeal_law. Thin adapters over backend/game_logic/reforms.py (the
naval_executor idiom): resolve the law the words name, refuse through the SAME
predicate every surface quotes (`reforms.law_refusal` / `repeal_refusal` —
shown = applied), then call the ONE mutation. The admin action is charged by
the shared executor after success (both verbs are ADMIN_ACTIONS); the AI rides
the same verbs with `_acting_nation` and its own admin budget (GR5).
"""
from typing import Dict

from backend.game_logic import reforms


def _authority_note(outcome: Dict) -> str:
    """"Authority 100 → 85" plus every threshold the spend crossed (§3's
    teeth): the diplomatic point at 60, the marshals' calm at 70, the floor
    at 30."""
    before = int(outcome.get("authority_before", 0))
    after = int(outcome.get("authority_after", 0))
    if not outcome.get("authority"):
        return ""
    crossed = []
    if before >= 70 > after:
        crossed.append("the marshals' calm above 70 is lost")
    if before >= 60 > after:
        crossed.append("the diplomatic point above 60 is lost")
    if before >= 30 > after:
        crossed.append("below 30 the court loses a diplomatic point a turn")
    tail = (" — " + "; ".join(crossed)) if crossed else ""
    return f" Authority {before} → {after}{tail}."


def _misaddressed(command: Dict, world, actor: str, verb: str) -> Dict:
    """A law order put to a marshal in the field is refused in words, free
    (the Admiralty's idiom): the laws are the Emperor's acts of state. The
    Emperor himself (the sovereign marshal) is not misaddressed."""
    if actor != getattr(world, "player_nation", None):
        return {}
    name = command.get("marshal")
    if not name:
        return {}
    marshal = (getattr(world, "marshals", {}) or {}).get(name)
    if marshal is not None and getattr(marshal, "is_sovereign", False):
        return {}
    from backend.display_names import humanize_entity_name
    shown = humanize_entity_name(marshal.name if marshal is not None else str(name))
    words = str(command.get("target") or "the Staff").strip()
    return {"success": False, "variable_action_cost": 0, "message": (
        f"The laws are the Emperor's to {verb}, Sire — Marshal {shown} "
        f"commands a corps, not the state. Say '{verb} {words}'.")}


class ReformsExecutor:
    """enact_law / repeal_law through the shared executor."""

    def __init__(self, parent):
        self.parent = parent

    def _resolve(self, command: Dict, world, actor: str):
        words = command.get("target") or command.get("law") or ""
        row = reforms.resolve_law(world, actor, words)
        if row is not None:
            return row, None
        listing = reforms.deck_listing(world, actor)
        if not listing:
            return None, "This campaign has no laws to enact."
        shown = str(words).strip()
        if shown.lower().startswith("the "):
            shown = shown[4:]
        named = f"no law called '{shown}'" if shown else "no law named"
        return None, (f"There is {named} among the laws of state, Sire. "
                      f"They are: {listing}.")

    def _execute_enact_law(self, command: Dict, game_state: Dict) -> Dict:
        world = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}
        actor = command.get("_acting_nation") or getattr(world, "player_nation", "France")
        misaddressed = _misaddressed(command, world, actor, "enact")
        if misaddressed:
            return misaddressed
        row, unresolved = self._resolve(command, world, actor)
        if unresolved:
            return {"success": False, "message": unresolved}
        admin = command.get("_admin_actions")
        if admin is None and actor != getattr(world, "player_nation", None):
            admin = reforms.ADMIN_ACTIONS_PER_ACT   # the AI loop holds one
        refusal = reforms.law_refusal(world, actor, str(row.get("id")),
                                      admin_actions=admin)
        if refusal:
            return {"success": False, "message": refusal}
        outcome = reforms.enact_law(world, actor, row)
        quote = outcome["quote"]
        name = reforms.display_name(row)
        if quote["kind"] == "restore":
            paid = (f"restored for {int(quote['price']):,} "
                    f"{'gold' if quote['currency'] == 'gold' else 'authority'} "
                    f"and {int(quote['arrears']):,} gold in arrears "
                    f"({int(quote['turns_dead'])} turn"
                    f"{'s' if int(quote['turns_dead']) != 1 else ''} unpaid)")
        elif quote["currency"] == "gold":
            paid = f"enacted for {int(quote['price']):,} gold"
        else:
            paid = f"enacted for {int(quote['price'])} authority"
        staff = (" From the next refill, one more order each day."
                 if reforms.is_staff(row) else "")
        upkeep = int(row.get("upkeep", 0) or 0)
        message = (f"{name[0].upper() + name[1:]} is in force — {paid}. "
                   f"It costs {upkeep:,} gold a turn from now on.{staff}"
                   f"{_authority_note(outcome)}")
        result = {
            "success": True,
            "message": message,
            "law": str(row.get("id")),
            "events": [{"type": "law_enacted", "nation": actor,
                        "law": str(row.get("id"))}],
        }
        result["new_state"] = game_state
        return result

    def _execute_repeal_law(self, command: Dict, game_state: Dict) -> Dict:
        world = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}
        actor = command.get("_acting_nation") or getattr(world, "player_nation", "France")
        misaddressed = _misaddressed(command, world, actor, "repeal")
        if misaddressed:
            return misaddressed
        row, unresolved = self._resolve(command, world, actor)
        if unresolved:
            return {"success": False, "message": unresolved}
        admin = command.get("_admin_actions")
        refusal = reforms.repeal_refusal(world, actor, str(row.get("id")),
                                         admin_actions=admin)
        if refusal:
            return {"success": False, "message": refusal}
        reforms.repeal_law(world, actor, row)
        name = reforms.display_name(row)
        price = int(row.get("price", 0) or 0)
        unit = "authority" if row.get("currency") == "authority" else "gold"
        staff = (" Its extra order of the day goes with it at the next refill."
                 if reforms.is_staff(row) else "")
        message = (f"{name[0].upper() + name[1:]} is repealed — its "
                   f"{int(row.get('upkeep', 0) or 0):,} gold a turn ends, and "
                   f"nothing is refunded.{staff} Enacting it again costs its "
                   f"full price ({price:,} {unit}).")
        result = {
            "success": True,
            "message": message,
            "law": str(row.get("id")),
            "events": [{"type": "law_repealed", "nation": actor,
                        "law": str(row.get("id"))}],
        }
        result["new_state"] = game_state
        return result
