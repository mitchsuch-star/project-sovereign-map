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


def prisoner_is_a_province(world, marshal) -> bool:
    """FA slice 7 review round (R2-1): when a captive's NAME is also a
    province (Brunswick — the WO-13 collision), the province is the only
    live referent an order can mean, so the seams let the region path run
    instead of refusing — the first cut made the province unattackable by
    name for every court while the man sat in a cell (the AI's attack rungs
    emit region names, so its homeland-defence orders failed in silence)."""
    try:
        return marshal.name in (getattr(world, "regions", {}) or {})
    except Exception:
        return False


def cell_in_view(world, location: str, viewer_nation: Optional[str]) -> bool:
    """Whether the viewer may know a captive is held at `location`: the AI
    has no fog; the player knows a cell only at PARTIAL or better."""
    player = getattr(world, "player_nation", None)
    if viewer_nation and viewer_nation != player:
        return True
    try:
        from backend.models.intel import PARTIAL
        return bool(world.get_region_intel(location).visibility_at_least(PARTIAL))
    except Exception:
        return False


def prisoner_refusal(world, marshal, viewer_nation: Optional[str]) -> Dict:
    """The refusal dict every seam returns for an order aimed at a prisoner.
    `prisoner: True` is what lets the combat seam return it verbatim instead
    of falling through to the region fuzzy pass; the cost is zero.

    FA slice 7 review round (R2-2): a THIRD court's captive is named only
    where the cell that holds him is in view — the first cut told the player
    "Kutuzov is a prisoner of Prussia at Berlin" about a capture the campaign
    log itself filters out of sight. Our own captive is always ours to name.
    """
    from backend.display_names import humanize_entity_name
    shown = humanize_entity_name(marshal.name)
    captor = getattr(marshal, "captured_by", "") or ""
    location = getattr(marshal, "location", "") or "the rear"
    base = {"success": False, "prisoner": True, "prisoner_name": marshal.name,
            "variable_action_cost": 0}
    if viewer_nation and captor == viewer_nation:
        return {**base, "message": (
            f"{shown} is our prisoner at {location}, Sire — he leads no "
            f"army. Hold him for the peace table.")}
    if not cell_in_view(world, location, viewer_nation):
        return {**base, "fogged": True, "message": (
            f"No intelligence on {shown}'s position, Sire — scout for him "
            f"before naming him.")}
    try:
        from backend.game_logic.formations import formed_display_name
        court = formed_display_name(world, captor)
    except Exception:
        court = captor or "the enemy"
    return {**base, "message": (
        f"{shown} is a prisoner of {court} at {location}, Sire — "
        f"he leads no army.")}
