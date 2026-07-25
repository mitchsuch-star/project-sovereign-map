"""Nation-name recognition for typed orders (IGR-A3).

A player who types `"Ney, move to Austria"` names a COUNTRY where the order
wants a PROVINCE. Before this module the fuzzy ladder silently auto-corrected
it into the nearest-scoring province — `Austria` marched a French corps eight
provinces to the Spanish coast (`Asturias`), and `Britain` marched it to
`Brittany`. Everything else in the roster produced a useless suggestion
(`"Saxony" -> "Did you mean 'Savoy'?"`).

Two rules make this safe, and both are load-bearing:

1. **A word that is ALSO an exact region name is a region.** `Hanover`,
   `Naples` and `Normandy` are simultaneously nations (or formable tags) and
   provinces on the 1805 board, and `Saxony` is both on the legacy board.
   Those must keep resolving to the province the player is standing next to.
2. **The roster is derived from the world it is handed, never hardcoded.** The
   legacy fixture world and the 1805 campaign have different rosters AND
   different collision sets, and the golden corpus runs `world: "any"` rows
   against both.

This is deliberately NOT folded into `strategic_parser._nation_demonyms`:
that list is shared with the strategic-target classifier, where widening it to
bare names would reclassify `"march to Saxony"` as a generic army order.
"""
from typing import List, Optional

from backend.display_names import NATION_DISPLAY


def _normalize(text: str) -> str:
    """Casefold, drop a leading article, and squeeze out spaces/punctuation.

    Squeezing is what lets the typed display form `"Papal States"` match the
    internal tag `PapalStates`.
    """
    cleaned = str(text or "").strip().lower()
    for article in ("the ", "l'", "la ", "le "):
        if cleaned.startswith(article):
            cleaned = cleaned[len(article):]
            break
    return "".join(ch for ch in cleaned if ch.isalnum())


def resolve_typed_nation(text: Optional[str], world) -> Optional[str]:
    """Return the internal nation tag `text` names, or None.

    Returns None when `world` is missing (unit tests build parsers with no
    world), when the roster cannot be read, or — critically — when the word is
    an exact region name on this map.
    """
    if not text or world is None:
        return None
    region_lookup = getattr(world, "get_region", None)
    if callable(region_lookup):
        try:
            if region_lookup(str(text).strip()) is not None:
                return None
        except Exception:
            return None
    get_nations = getattr(world, "get_active_nations", None)
    if not callable(get_nations):
        return None
    try:
        nations = get_nations() or []
    except Exception:
        return None
    wanted = _normalize(text)
    if not wanted:
        return None
    for nation in nations:
        tag = str(nation)
        if _normalize(tag) == wanted:
            return tag
        display = NATION_DISPLAY.get(tag)
        if display and _normalize(display) == wanted:
            return tag
    return None


def nation_province_list(nation: str, world) -> List[str]:
    """The provinces `nation` currently controls, sorted, for player copy.

    Uses the per-turn-cached `get_nation_regions` (Golden Rule 8). Returns []
    for a nation holding nothing — an eliminated or freshly carved court hits
    that arm immediately, so every caller needs an empty-list branch.
    """
    getter = getattr(world, "get_nation_regions", None)
    if not callable(getter):
        return []
    try:
        return sorted(getter(nation) or [])
    except Exception:
        return []
