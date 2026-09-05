"""FA slice 7 (Sept 2026) — A PRISONER IS NAMED.

FA-24 / FA-48 / NPC-7 / NPC-19, one root: every enemy lookup on the order
path reads a `strength > 0` roster, and a captured marshal is held at the
captor's capital at strength 0 — so his name fell through to the REGION
fuzzy pass ("Region 'Mack' not found. Did you mean 'La Mancha'?"), to the
destroyed arm ("Mack has already been destroyed!") or, on the PURSUE road,
to an accepted 2-AP chase of a man in our own cells. Measured Sept 4, 2026
on the 1805 boot with Mack captured by France.

ONE refusal, read by the executor's fuzzy seam, the auto-assign attack and
the strategic PURSUE arm. Lever False reproduces every pre-slice answer.
"""
from __future__ import annotations

from typing import Dict, Optional

PRISONERS_ARE_NAMED = True


def prisoner_of(world, name: str, viewer_nation: Optional[str] = None):
    """The captured marshal `name` refers to (either register), or None.
    A viewer's OWN captured marshal is not returned — that case belongs to
    main.py's addressed-marshal guard, which speaks in the first person."""
    if not PRISONERS_ARE_NAMED or not name or world is None:
        return None
    typed = str(name).strip()
    marshal = world.get_marshal(typed)
    if marshal is None:
        from backend.display_names import humanize_entity_name
        low = typed.lower()
        for candidate in (getattr(world, "marshals", {}) or {}).values():
            if humanize_entity_name(candidate.name).lower() == low:
                marshal = candidate
                break
    if marshal is None or not getattr(marshal, "captured_by", ""):
        return None
    if viewer_nation and marshal.nation == viewer_nation:
        return None
    return marshal


def prisoner_refusal(world, marshal, viewer_nation: Optional[str]) -> Dict:
    """The refusal dict every seam returns for an order aimed at a prisoner.
    `prisoner: True` is what lets the combat seam return it verbatim instead
    of falling through to the region fuzzy pass; the cost is zero."""
    from backend.display_names import humanize_entity_name
    shown = humanize_entity_name(marshal.name)
    captor = getattr(marshal, "captured_by", "") or ""
    location = getattr(marshal, "location", "") or "the rear"
    if viewer_nation and captor == viewer_nation:
        message = (f"{shown} is our prisoner at {location}, Sire — he leads no "
                   f"army. Hold him for the peace table.")
    else:
        try:
            from backend.game_logic.formations import formed_display_name
            court = formed_display_name(world, captor)
        except Exception:
            court = captor or "the enemy"
        message = (f"{shown} is a prisoner of {court} at {location}, Sire — "
                   f"he leads no army.")
    return {
        "success": False,
        "message": message,
        "prisoner": True,
        "prisoner_name": marshal.name,
        "variable_action_cost": 0,
    }
