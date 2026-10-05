"""
Reforms Executor — the laws' two verbs (SR-5r RF-1, docs/REFORMS_SPEC.md §2)

enact_law · repeal_law. Thin adapters over backend/game_logic/reforms.py (the
naval_executor idiom): resolve the law the words name, refuse through the SAME
predicate every surface quotes (`reforms.law_refusal` / `repeal_refusal` —
shown = applied), then call the ONE mutation. The admin action is charged by
the shared executor after success (both verbs are ADMIN_ACTIONS); the AI rides
the same verbs with `_acting_nation` and its own admin budget (GR5).
"""
import re
from typing import Dict

from backend.game_logic import reforms
from backend.display_names import marshal_title  # SF5-X3: the ONE style for a marshal in prose

# RF-4a: the enactment confirm (REFORMS_SPEC §8a) — the Admiralty's
# quote-then-confirm on the EXISTING command_clarification channel (no new
# modal type). The option reissues the order with this marker; a typed
# "… confirmed" does the same. An AI court never sees the quote (GR5 — its
# rung already priced the act).
_CONFIRMED_RE = re.compile(r"\s*\bconfirm(?:ed)?\b\s*$", re.IGNORECASE)
COUNCIL = "The Council of State"


def _authority_note(outcome: Dict) -> str:
    """The authority priced aloud on the verb's result — the SAME line the
    chip and the confirm read (`reforms.authority_line`)."""
    if not outcome.get("authority"):
        return ""
    return " " + reforms.authority_line(int(outcome.get("authority_before", 0)),
                                        int(outcome.get("authority_after", 0)))


def _confirmed(command: Dict) -> bool:
    if command.get("confirmed"):
        return True
    for key in ("target", "law", "raw_input", "original_command", "raw_command"):
        words = command.get(key)
        if isinstance(words, str) and _CONFIRMED_RE.search(words):
            return True
    return False


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
    who = marshal_title(world, marshal.name if marshal is not None else str(name))
    words = str(command.get("target") or "the Staff").strip()
    return {"success": False, "variable_action_cost": 0, "message": (
        f"The laws are the Emperor's to {verb}, Sire — {who} "
        f"commands a corps, not the state. Say '{verb} {words}'.")}


class ReformsExecutor:
    """enact_law / repeal_law through the shared executor."""

    def __init__(self, parent):
        self.parent = parent

    def _resolve(self, command: Dict, world, actor: str):
        words = _CONFIRMED_RE.sub("", str(command.get("target") or command.get("law") or ""))
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
        if (not command.get("_acting_nation")
                and actor == getattr(world, "player_nation", None)
                and not _confirmed(command)):
            return self._quote(world, actor, row, command)
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
        # SR-7d DC-2 (DOCTRINES_SPEC §4): the player's own cure is named by
        # the verb's answer — in effect, or waiting on the Staff (RV-15).
        cure_note = ""
        if any(isinstance(c, dict) and c.get("type") == "cures"
               for c in (row.get("effects") or [])) or reforms.is_staff(row):
            from backend.game_logic.doctrines import cure_status
            status = cure_status(world, actor)
            if outcome.get("cure_took_effect"):
                flaw = next((str(c.get("flaw")) for c in (row.get("effects") or [])
                             if isinstance(c, dict) and c.get("type") == "cures"), "")
                if not flaw:
                    flaw = "the army's flaw"
                cure_note = f" {flaw} is cured while {status['staff']} stands."
            elif status.get("needs") and not status.get("cured") and not reforms.is_staff(row):
                cure_note = f" Its cure waits on {status['needs']}."
        # EAD-2: the grip line the Charges of Empire read, when the act
        # crossed it (the same clause the quote named).
        grip_note = ""
        if outcome.get("authority"):
            from backend.game_logic.ledger import charges_grip_clause
            grip = charges_grip_clause(world, actor,
                                       int(outcome.get("authority_before", 0)),
                                       int(outcome.get("authority_after", 0)))
            if grip:
                grip_note = f" {grip[0].upper() + grip[1:]}."
        message = (f"{name[0].upper() + name[1:]} is in force — {paid}. "
                   f"It costs {upkeep:,} gold a turn from now on.{staff}{cure_note}"
                   f"{_authority_note(outcome)}{grip_note}")
        result = {
            "success": True,
            "message": message,
            "law": str(row.get("id")),
            "events": [{"type": "law_enacted", "nation": actor,
                        "law": str(row.get("id"))}],
        }
        result["new_state"] = game_state
        return result

    def _quote(self, world, actor: str, row: Dict, command: Dict) -> Dict:
        """The enactment confirm: the terms first, free (the Admiralty's
        quote-then-confirm). The option reissues the order confirmed."""
        name = reforms.display_name(row)
        spoken = name[0].upper() + name[1:]
        quote = reforms.restoration_price(world, actor, row)
        verb = "Restore" if quote["kind"] == "restore" else "Enact"
        date = str(row.get("date") or "")
        says = str(row.get("says") or "")
        chest = int(getattr(world, "gold", 0) or 0)
        message = (f"{spoken}{f' ({date})' if date else ''}: {says} "
                   f"{reforms.terms_line(world, actor, row)}. The treasury holds "
                   f"{chest:,} gold. {verb} it? (yes / no)")
        return {
            "success": True,
            "free_action": True,
            "state": "awaiting_clarification",
            "type": "clarification",
            "law_confirm": True,
            "marshal": COUNCIL,
            "original_command": command.get("raw_command", ""),
            "message": message,
            "options": [
                {"label": f"{verb} {name}",
                 "command": f"enact {name} confirmed",
                 "aliases": ["yes", "enact", "restore", "confirm"]},
                {"label": "Not now", "command": "cancel",
                 "aliases": ["no", "not now", "stand down"]},
            ],
            "action_summary": world.get_action_summary(),
            "game_state": world.get_filtered_game_state_summary(),
        }

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
        staff = reforms.staff_loss_sentence(row)
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
