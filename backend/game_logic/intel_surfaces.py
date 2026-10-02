"""SR-6a "The dispatch pass" (Score Finish Step 2, October 2, 2026) — ONE fog
reader for every intelligence SURFACE: the morning dispatch's INTELLIGENCE
rows, the Strategic Ledger's intel tab and Berthier's `status` report.

Three rows share a root:

* **AAR-5** — the dispatch placed Buxhowden at Podolia "[partial]" the morning
  after he conquered Hungary at FULL. `RegionIntel.refresh` early-returns on a
  LOWER visibility without touching `known_marshals` or `last_updated_turn`,
  so a province labelled FULL yesterday keeps that label (decay starts at
  three turns) over a snapshot frozen BEFORE the man moved — and the province
  he moved INTO can be labelled FULL by the battle refresh with an EMPTY
  snapshot (measured turn 6 of the ambient run: Milan FULL/t5 holding
  Archduke Charles at 35,513, Munich FULL/t5 holding nobody, Charles standing
  at Munich with 28,384). The map summary already reads the LIVE marshals of
  every FULL province; the dispatch and the Ledger read the frozen snapshot.
  The rule here is the map's: **a FULL province is read live** — the men who
  stand there now, at today's strength; a frozen snapshot is kept only where
  the fog is real, and never for a man confirmed live elsewhere.

* **AAR4-X2** — `status` left out a FULL province held by a garrison alone,
  and the Ledger / dispatch read marshals only. Every surface now names a
  KNOWN garrison of a court at war with the viewer, through the one fog rule
  the map uses for garrisons (`garrison_report.garrison_view`: exact at FULL
  or on own soil, the band at PARTIAL / STALE, nothing below).

* **AAR24-X4** — the dispatch dropped a `garrison_regen` event whose nation
  was not the player's, so an enemy capital's +2,000 reached no surface. The
  turn-events builder keeps a KNOWN enemy garrison's regrowth, fog-honestly
  (exact figures at FULL, the band otherwise).

Display only: the enemy AI reads none of this (GR5 — it never reads the
intel store). Levers: False reproduces each pre-slice surface byte for byte.
"""
from typing import Any, Dict, List, Optional, Tuple

from backend.display_names import humanize_entity_name
from backend.models.intel import (
    FULL, LAST_KNOWN, PARTIAL, STALE, UNKNOWN, VISIBILITY_PRIORITY,
    get_strength_band,
)

# AAR-5: a FULL province is read live on the dispatch and the Ledger.
THE_SIGHTING_IS_LIVE = True
# AAR4-X2: every intelligence surface names a known enemy garrison.
THE_SURFACES_NAME_THE_GARRISON = True
# AAR24-X4: a known enemy garrison's regrowth rides the dispatch.
THE_ENEMY_WORKS_REGROW_ALOUD = True

GARRISON_ROW_KIND = "garrison"


def _nation_at_war_with_viewer(world, nation: str, viewer: str) -> bool:
    if not nation or nation == viewer:
        return False
    try:
        return bool(world.is_at_war(viewer, nation))
    except Exception:
        return False


def live_sightings(world, viewer: str) -> Dict[str, Dict[str, Any]]:
    """The men standing, right now, in every province the viewer sees at
    FULL — keyed by roster name. Exact strength (that is what FULL means on
    the map), `intel_turn` = this turn, source `live`. Our own men are never
    listed; a corps at zero strength is not a sighting."""
    out: Dict[str, Dict[str, Any]] = {}
    turn = int(getattr(world, "current_turn", 0) or 0)
    for region_name, intel in world.intel.items():
        if intel.visibility != FULL:
            continue
        for m in world.get_marshals_in_region(region_name):
            if m.nation == viewer or int(getattr(m, "strength", 0) or 0) <= 0:
                continue
            if getattr(m, "captured_by", ""):
                continue
            out[m.name] = {
                "name": humanize_entity_name(m.name),
                "roster_name": m.name,
                "nation": m.nation,
                "location": region_name,
                "strength": int(m.strength),
                "strength_display": f"{int(m.strength):,}",
                "visibility": FULL,
                "intel_turn": turn,
                "source": "live",
            }
    return out


def enemy_sightings(world, viewer: str) -> List[Dict[str, Any]]:
    """AAR-5: the dispatch's / Ledger's rows — one per enemy marshal, the
    live FULL sighting first, then the frozen snapshots where the fog is real
    (PARTIAL / STALE / LAST_KNOWN, and a FULL label whose live read is empty
    — that label is yesterday's), deduped so a "[partial]" row never outranks
    a live one. Sorted FULL → PARTIAL → STALE → LAST_KNOWN."""
    rank = VISIBILITY_PRIORITY
    sightings: Dict[str, Dict[str, Any]] = {}
    if THE_SIGHTING_IS_LIVE:
        sightings.update(live_sightings(world, viewer))
    for region_name, intel in world.intel.items():
        vis = intel.visibility
        if vis == UNKNOWN:
            continue
        if THE_SIGHTING_IS_LIVE and vis == FULL:
            # Read live above; a frozen FULL snapshot naming a man who is
            # not there is yesterday's label, not a sighting.
            continue
        for km in intel.known_marshals:
            if km.get("nation") == viewer:
                continue
            name = km.get("name", "Unknown")
            updated = int(intel.last_updated_turn)
            existing = sightings.get(name)
            if existing is not None:
                if existing.get("source") == "live":
                    continue  # the live read outranks every snapshot
                if ((existing["intel_turn"], rank.get(existing["visibility"], 0))
                        >= (updated, rank.get(vis, 0))):
                    continue
            if vis == FULL and "strength" in km:
                strength_display = f"{int(km['strength']):,}"
            elif "band" in km:
                strength_display = km["band"]
            elif "strength" in km:
                strength_display = get_strength_band(int(km["strength"]))
            else:
                strength_display = intel.strength_band
            sightings[name] = {
                "name": humanize_entity_name(name),
                "roster_name": name,
                "nation": km.get("nation", "?"),
                "location": region_name,
                "strength": int(km.get("strength", 0) or 0),
                "strength_display": strength_display,
                "visibility": vis,
                "intel_turn": updated,
                "source": "snapshot",
            }
    return sorted(sightings.values(),
                  key=lambda s: rank.get(s["visibility"], 0), reverse=True)


def known_garrisons(world, viewer: str) -> List[Dict[str, Any]]:
    """AAR4-X2: every garrison of a court at war with the viewer that the
    viewer's fog admits — through `garrison_view` (the map's own rule):
    exact at FULL, the band at PARTIAL / STALE, nothing below. A province
    the viewer holds is his own garrison, not intelligence."""
    if not THE_SURFACES_NAME_THE_GARRISON:
        return []
    from backend.game_logic.garrison_report import garrison_view
    rows: List[Dict[str, Any]] = []
    turn = int(getattr(world, "current_turn", 0) or 0)
    for region_name, region in world.regions.items():
        holder = getattr(region, "controller", None)
        if holder == viewer or not _nation_at_war_with_viewer(world, holder, viewer):
            continue
        if int(getattr(region, "garrison_strength", 0) or 0) <= 0:
            continue
        form, value = garrison_view(world, region_name, viewer)
        if form is None:
            continue
        intel = world.get_region_intel(region_name)
        vis = intel.visibility if intel.visibility in (FULL, PARTIAL, STALE) else PARTIAL
        if form == "exact":
            display = f"garrison of {int(value):,}"
            strength = int(value)
        else:
            display = f"garrison — {value}"
            strength = 0
        rows.append({
            "name": f"{region_name} garrison",
            "roster_name": "",
            "nation": holder,
            "location": region_name,
            "strength": strength,
            "strength_display": display,
            "visibility": vis,
            "intel_turn": turn if vis == FULL else int(intel.last_updated_turn),
            "source": "garrison",
            "kind": GARRISON_ROW_KIND,
        })
    return rows


def garrison_regen_line(world, event: Dict[str, Any], viewer: str) -> Optional[str]:
    """AAR24-X4: the sentence a KNOWN enemy garrison's regrowth earns on the
    dispatch — exact at FULL ("Vienna's garrison regains 2,000: 23,000 ->
    25,000."), the band at PARTIAL / STALE ("Vienna's garrison regrows — a
    large force."), None when the fog hides it or the court is not at war."""
    if not THE_ENEMY_WORKS_REGROW_ALOUD:
        return None
    region_name = event.get("region")
    if not region_name:
        return None
    holder = event.get("nation") or ""
    if not _nation_at_war_with_viewer(world, holder, viewer):
        return None
    from backend.game_logic.garrison_report import garrison_view
    form, value = garrison_view(world, region_name, viewer)
    if form == "exact":
        old = int(event.get("old_strength", 0) or 0)
        new = int(event.get("new_strength", 0) or 0)
        return (f"{region_name}'s garrison regains {new - old:,}: "
                f"{old:,} -> {new:,}.")
    if form == "band":
        return f"{region_name}'s garrison regrows — {value}."
    return None


def visible_tuple(sighting: Dict[str, Any]) -> Tuple[str, str, str]:
    """(name, location, visibility) — the three things a row says."""
    return (sighting["name"], sighting["location"], sighting["visibility"])
