"""CF-4 "A refusal names its remedy and does not offer it" (row CC beside
CC-4; `docs/BUG_FIXES.md` §CF; rules `SYSTEMS_REFERENCE.md` §126.2;
pins `tests/test_cf_the_four_rows.py::TestCF4`).

Measured on the command-feel drive (`docs/audits/COMMAND_FEEL_2026_10_16.md`
§4): five of eleven refusals were of this shape — "Ney is fortified at
Rhineland and cannot attack. Order 'unfortify' first … Try: 'Ney, unfortify'"
— text, while the ↳ offer slot CC-0 built stayed empty and the player
retyped the remedy, then retyped the order.

THE RULE
--------
A refusal whose remedy is ONE known verb the game takes today — `unfortify`
(the fortified corps told to attack, move or march, or to drill), the stance
change (`neutral`, free, for the aggressive corps told to fortify or drill)
— rides `remedy_command` on the response: the literal line the player would
type. The client puts it in the ↳ offer slot (`main.gd._offer_beside_line`,
never on the line, never sent — CC-0's "the line is the player's"). The
original order is kept for exactly one command's life (`world._pending_remedy`
— transient, never serialized, let go at the turn boundary beside the relay:
CR-7-8, nothing is held for a later turn) and, when the NEXT command is the
remedy sent unchanged and it goes out, the original is RE-OFFERED ONCE on
the relay's own keys (`relay_kind` "ready", `relay_command` the order) so the
client's existing fill puts it on the line. Any other command lets it go
without a word — the player was offered a remedy, not promised a queue.

The withdrawal (DDB R6: the engaged corps told to move onto friendly ground
is told "'Davout, retreat to Swabia' (free …)") is the first half only
(`reoffer=False`): the retreat REPLACES the move, so re-offering the move
afterwards would offer an order the game refuses ("already there"). A
refusal whose "Try:" names a DIFFERENT order (attack the man in the way;
march within range and recruit; pursue instead of attack) is not this class
at all: nothing is stamped, nothing stashed. GR5: the AI never posts
`/command`, so no stash is ever its.
"""

from __future__ import annotations

from typing import Dict, Optional

from backend.display_names import humanize_entity_name


def line(marshal_name: str, verb: str) -> str:
    """The literal typed remedy — `<Shown>, <verb>` — the ONE string the
    producer stamps and the pin drives."""
    return f"{humanize_entity_name(marshal_name)}, {verb}"


def stamp(result: Dict, marshal_name: Optional[str], verb: str, *,
          reoffer: bool = True) -> Dict:
    """Put the remedy on a refusal result (in place; returned for chaining).
    No marshal, no remedy. `reoffer=False` marks a remedy that REPLACES the
    order (the withdrawal): offered, never re-offered."""
    if isinstance(result, dict) and marshal_name and verb:
        result["remedy_command"] = line(marshal_name, verb)
        if not reoffer:
            result["remedy_reoffer"] = False
    return result


def _norm(text) -> str:
    return " ".join(str(text or "").strip().lower().replace(",", " ").split())


def stash(world, remedy_command: str, original: str) -> None:
    """Keep the refused order for exactly one command's life."""
    if not remedy_command or not original:
        return
    world._pending_remedy = {
        "remedy": str(remedy_command),
        "original": str(original).strip(),
        "turn": int(getattr(world, "current_turn", 0) or 0),
    }


def pop(world) -> Optional[Dict]:
    pending = getattr(world, "_pending_remedy", None)
    world._pending_remedy = None
    return pending


def is_the_remedy(pending: Optional[Dict], typed: str) -> bool:
    """The next command IS the remedy, sent unchanged (case and the comma
    forgiven — "ney unfortify" is the same order)."""
    if not pending:
        return False
    return _norm(pending.get("remedy")) == _norm(typed) and _norm(typed) != ""


def reoffer_relay(pending: Dict) -> Dict:
    """The re-offer, on the relay's keys (`relay.attach` / `append_note`
    read them): kind ``ready`` with the original order as the command."""
    original = str(pending.get("original") or "").strip()
    note = (f'The order it answered — "{original}" — is on the line; send it '
            f'when you are ready.')
    return {
        "dropped_sequel": original,
        "relay_kind": "ready",
        "relay_command": original,
        "relay_note": note,
        "relay_line": note,
    }
