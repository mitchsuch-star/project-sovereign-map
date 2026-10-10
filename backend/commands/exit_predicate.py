"""DD-0 S4 "The Command Road" — THE EXIT PREDICATE (October 10, 2026;
PRE_DEPLOY_PLAN.md §3.0 "the structural fix"; rules SYSTEMS_REFERENCE.md §104).

One question at the executor's door and again at its exit: *did I act on
the marshal, the place and the arm that were named?* A substitution is
DISCLOSED or REFUSED, never silent. The depth campaign's worst class lived
here — a drill carried out where he stands instead of at the named
province (SFR-D7), cavalry asked and infantry paid (SFR-D41), `drill your
guard` turned into a standing HOLD (SFR-D9) — and every one of them was the
game doing something other than what was typed, without a word.

Two halves, both PURE readers of the command and the result (no lever — the
code-health ratchet holds levers lower-only; every pin reads behaviour):

  place_pre_check   BEFORE the dispatch: a stationary arm (drill, fortify,
                    defend, wait, form square, unfortify) that
                    names a province the marshal does not stand in is
                    refused by name, free, with the two roads that do what
                    was meant — the march first, or the arm where he stands.
                    (The stationary executors never read the target; the
                    order was being carried out where he stood, in silence.)
  disclose          AFTER the executor returns: the command as it entered
                    and as it left (the trace's `command_changed` snapshots)
                    are compared on the marshal, the target and the arm; a
                    value that changed and is not named in the reply is
                    appended to it. The gates that substitute on purpose —
                    the bare attack's pick, the auto-assigned scout, the
                    recruit arm's soft correction — already name their
                    choice, so this is the net under them, not a second
                    sentence over them.

GR6: display and refusal only; nothing here changes a mechanic, a price or
an AP pool. A refusal here spends nothing (`free_action`).
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional

from backend.display_names import humanize_entity_name as _h

# The arms that are carried out WHERE THE MARSHAL STANDS and never read a
# place: a province named in the order is either where he is, or a mistake
# the player must hear about.
# (`garrison` has its own named refusal with the road — CX-R2 — and is not here.)
STATIONARY_ARMS = frozenset({
    "drill", "fortify", "defend", "wait", "form_square", "unfortify",
})

_ARM_WORD = {
    "drill": "a drill is held", "fortify": "the works are dug", "defend": "a defence is stood",
    "wait": "a wait is kept", "form_square": "a square is formed",
    "unfortify": "the works are struck", "garrison": "a garrison is left",
}
_ARM_VERB = {
    "drill": "drill", "fortify": "fortify", "defend": "defend", "wait": "wait",
    "form_square": "form square", "unfortify": "unfortify", "garrison": "garrison",
}


def _region_key(world, name: Any) -> Optional[str]:
    """The world's region key for a typed place, or None."""
    if not name or not isinstance(name, str):
        return None
    regions = getattr(world, "regions", None)
    if not isinstance(regions, dict):
        return None
    if name in regions:
        return name
    low = name.strip().lower()
    for key in regions:
        if str(key).lower() == low or _h(str(key)).lower() == low:
            return str(key)
    return None


def place_pre_check(command: Dict[str, Any], action: str, world) -> Optional[Dict[str, Any]]:
    """The refusal when a stationary arm names a province the marshal is
    not in; None when the order may proceed. Reads the command AFTER the
    executor resolved its marshal (`command["marshal"]` is a roster name)."""
    if action not in STATIONARY_ARMS or not isinstance(command, dict):
        return None
    if (command.get("_strategic_execution") or command.get("is_strategic")
            or command.get("strategic_type")):
        return None
    target = command.get("target")
    place = _region_key(world, target)
    if place is None:
        return None
    marshal = None
    get_marshal = getattr(world, "get_marshal", None)
    if callable(get_marshal) and command.get("marshal"):
        marshal = get_marshal(command.get("marshal"))
    if marshal is None:
        return None
    here = getattr(marshal, "location", None)
    if not here or here == place:
        return None
    verb = _ARM_VERB.get(action, action)
    return {
        "success": False,
        "message": (
            f"{marshal.name} stands at {_h(here)}, not {_h(place)}, Sire — {_ARM_WORD.get(action, 'the order is carried out')} "
            f"where the corps stands. Order '{marshal.name}, move to {_h(place)}' first, or "
            f"'{marshal.name}, {verb}' to {verb} at {_h(here)}. Nothing has been relayed."),
        "free_action": True,
        "refusal": "place_mismatch",
        "named_place": place,
        "marshal_place": here,
    }


_ARM_LABELS = ("infantry", "cavalry", "artillery")


def _names(message: str, value: Any) -> bool:
    if value is None:
        return True
    text = str(message or "").lower()
    v = str(value).strip().lower()
    if not v or v == "generic":
        return True
    if v in text or _h(str(value)).lower() in text:
        return True
    # the surname alone ("Archduke John" → "John")
    last = v.split()[-1] if " " in v else None
    return bool(last and re.search(r"\b" + re.escape(last) + r"\b", text))


def disclose(entered: Optional[Dict[str, Any]], exited: Optional[Dict[str, Any]],
             result: Any, world=None) -> Optional[str]:
    """The sentence appended to a reply whose executor changed the marshal,
    the target or the arm without naming the change — or None. PURE."""
    if (not isinstance(result, dict) or not isinstance(entered, dict)
            or not isinstance(exited, dict)):
        return None
    if result.get("success") is not True:
        return None
    message = str(result.get("message") or "")
    clauses = []
    for key, noun in (("marshal", "the order went to"), ("target", "it was carried out against")):
        before, after = entered.get(key), exited.get(key)
        if after in (None, "", "generic") or before == after:
            continue
        if _names(message, after):
            continue
        if before in (None, "", "generic"):
            clauses.append(f"{noun} {_h(after)}")
        else:
            clauses.append(f"you named {_h(before)} and {noun} {_h(after)}")
    # the recruit arm: the player asked for one arm and the levy raised another
    asked = entered.get("requested_type")
    if (str(entered.get("action") or exited.get("action") or "") == "recruit"
            and asked and str(asked).lower() in _ARM_LABELS
            and str(asked).lower() not in message.lower()
            and not any(a in message.lower() for a in _ARM_LABELS)):
        clauses.append(f"you asked for {asked} and the levy was of another arm")
    if not clauses:
        return None
    return "Berthier: \"" + "; ".join(clauses) + ".\""
