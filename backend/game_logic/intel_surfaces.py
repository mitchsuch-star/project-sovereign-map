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
from backend.errors import report

# AAR-5: a FULL province is read live on the dispatch and the Ledger.
THE_SIGHTING_IS_LIVE = True
# AAR4-X2: every intelligence surface names a known enemy garrison.
THE_SURFACES_NAME_THE_GARRISON = True
# AAR24-X4: a known enemy garrison's regrowth rides the dispatch.
THE_ENEMY_WORKS_REGROW_ALOUD = True
# Score Finish Step 3 exit: a captured man's frozen snapshot is not a sighting.
A_PRISONER_IS_NOT_A_SIGHTING = True
# SF-LB-2's exit (narration C4, October 3, 2026): A FULL LABEL KEEPS ITS LAST
# SIGHTING. The rule above skipped every frozen snapshot in a province that is
# in full view today — right for the LIVE read (the man is plainly not there),
# wrong for the KNOWLEDGE: on the historical commanded seed at turn 30
# Archduke Charles was last seen at Franconia on turn 10 (FULL then, FULL
# still, and empty of him now), and skipping that snapshot handed the row an
# OLDER Tyrol sighting from turn 8 — while the store's own reader
# (`get_last_known_location`) ranked by turn and said Franconia. A frozen
# snapshot in a full-view province rides as a `last_known` sighting with its
# own turn, so the most recent knowledge wins the dedupe; the live read still
# outranks every snapshot. False = the skip, byte for byte.
A_FULL_LABEL_KEEPS_ITS_LAST_SIGHTING = True

GARRISON_ROW_KIND = "garrison"


def _nation_at_war_with_viewer(world, nation: str, viewer: str) -> bool:
    if not nation or nation == viewer:
        return False
    try:
        return bool(world.is_at_war(viewer, nation))
    except Exception as exc:
        report(exc, "intel_surfaces._nation_at_war_with_viewer: bool / world.is_at_war")
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


# ── RR6-X3 (Pre-Deploy S14b's head, October 21, 2026): ONE SIGHTING RULE ──
# Three readers of "where the player last saw a man" stood: the store's
# snapshots (the order, its per-turn gate, the cautious objection), this
# module's rows (the dispatch, the Ledger), and the live read under a PARTIAL
# label (the desk, the map, `get_visible_enemies`). Measured on the FLD arm's
# turn 7: the dialog showed Archduke John take Provence, the map and the desk
# placed him there, and the order answered "No intelligence on Archduke John's
# position" — Provence's own read was turn 6's, empty, and no shown action
# wrote a sighting. Ruled under the standing delegation (BUG_FIXES §RR6):
#   1. IN SIGHT — the map's rule: a foreign corps whose own province reads
#      PARTIAL or better is placed where he stands, today (`in_sight`);
#   2. OUT OF SIGHT — the newest snapshot naming him, each entry its own turn;
#      a snapshot in a province in sight today that no longer holds him is
#      yesterday's (it rides as `last_known`, as a FULL label's always did);
#   3. THE STORE LEARNS WHAT THE DIALOG SHOWED — every enemy-phase action the
#      fog filter shows writes its actor's sighting where the dialog places him
#      (`record_shown_sightings`), so once the label decays he is "last seen
#      at Provence", not "no intelligence".
# `last_seen` is the one answer; the order, the per-turn gate, the cautious
# objection, the desk, the dispatch, the Ledger and the status report ask it.


def in_sight(world, viewer: str, man) -> bool:
    """RR6-X3 rule 1 — the map's: a foreign corps stands IN SIGHT when the
    province he stands in reads PARTIAL or better (what `get_visible_enemies`,
    the map's markers and the desk read). Our own, an empty corps and a
    prisoner are never sightings."""
    if man is None or getattr(man, "nation", None) == viewer:
        return False
    if int(getattr(man, "strength", 0) or 0) <= 0 or getattr(man, "captured_by", ""):
        return False
    intel = world.intel.get(str(getattr(man, "location", "") or ""))
    return (intel is not None
            and VISIBILITY_PRIORITY.get(intel.visibility, 0) >= VISIBILITY_PRIORITY[PARTIAL])


def _in_sight_rows(world, viewer: str) -> Dict[str, Dict[str, Any]]:
    """Rule 1's rows: every foreign corps in sight, where he stands today —
    exact at FULL, his own band at PARTIAL (the desk's and the map's figure,
    never the province's aggregate)."""
    out: Dict[str, Dict[str, Any]] = {}
    turn = int(getattr(world, "current_turn", 0) or 0)
    for m in (getattr(world, "marshals", {}) or {}).values():
        if not in_sight(world, viewer, m):
            continue
        vis = world.intel[m.location].visibility
        out[m.name] = {
            "name": humanize_entity_name(m.name),
            "roster_name": m.name,
            "nation": m.nation,
            "location": m.location,
            "strength": int(m.strength),
            "strength_display": (f"{int(m.strength):,}" if vis == FULL
                                 else get_strength_band(int(m.strength))),
            "visibility": vis,
            "intel_turn": turn,
            "source": "live",
        }
    return out


def last_seen(world, viewer: str, name: str) -> Optional[Dict[str, Any]]:
    """RR6-X3: THE answer to "where does the player place this man" — his row
    under the one rule (in sight now, else his newest sighting), or None when
    the player has no sighting of him. `location`, `intel_turn`, `visibility`
    and `source` (`live` / `snapshot`) as the dispatch's rows carry them."""
    if not name:
        return None
    for row in enemy_sightings(world, viewer):
        if row.get("roster_name") == name:
            return row
    return None


def _shown_place(world, action: Dict[str, Any], actor: str) -> Optional[str]:
    """Where the enemy-phase dialog places `actor` for one shown action — only
    what its lines print (`enemy_phase_dialog.gd` `_format_action`): the
    province he "moves to" / "retreats to" (the march's own event, so a march
    that did not happen places nobody) or "Region captured: X" under his
    action, else the province he stands in when that is in full view (the
    filter's region gate showed the action because of it). A battle's retreat
    is never printed with its road, so it places nobody — the battle's own
    intelligence (`update_intel_from_battle`) reads its field."""
    place = None
    verb = str((action.get("ai_action") or {}).get("action") or "")
    for evt in action.get("events") or []:
        if not isinstance(evt, dict) or evt.get("marshal") != actor:
            continue
        etype = str(evt.get("type") or "")
        if etype == "conquest" and evt.get("region"):
            place = str(evt["region"])
        elif etype == verb and etype in ("move", "retreat") and evt.get("to"):
            place = str(evt["to"])
    if place is None:
        man = world.marshals.get(actor)
        here = str(getattr(man, "location", "") or "")
        intel = world.intel.get(here)
        if intel is not None and intel.visibility == FULL:
            place = here
    return place if place in getattr(world, "regions", {}) else None


def record_shown_sightings(world, shown_phase: Optional[Dict[str, Any]]) -> int:
    """RR6-X3 rule 3: the store learns what the enemy-phase dialog SHOWED.
    Every shown action's actor is written into the snapshot of the province
    the dialog places him in, stamped with this turn (`SEEN_TURN_KEY`) — the
    province's own read and label untouched, so decay ages it as it would.
    Skipped where a read of this turn already names him (the live end of the
    phase is the newer knowledge). Returns the sightings written."""
    from backend.models.intel import SEEN_TURN_KEY, snapshot_entry
    if not shown_phase or not shown_phase.get("nations"):
        return 0
    viewer = getattr(world, "player_nation", "")
    turn = int(getattr(world, "current_turn", 0) or 0)
    placed: Dict[str, str] = {}
    for nation_data in shown_phase["nations"].values():
        for action in nation_data.get("actions", []) or []:
            ai = action.get("ai_action") or {}
            actor = str(ai.get("marshal") or "") if isinstance(ai, dict) else ""
            man = world.marshals.get(actor) if actor else None
            if (man is None or man.nation == viewer
                    or int(getattr(man, "strength", 0) or 0) <= 0
                    or getattr(man, "captured_by", "")):
                continue
            place = _shown_place(world, action, actor)
            if place:
                placed[actor] = place   # the phase's last shown place wins
    written = 0
    for actor, place in placed.items():
        known = world.get_last_known_location(actor)
        if known is not None and known[1] >= turn:
            continue
        man = world.marshals[actor]
        intel = world._intel_entry(place)
        entry = world._build_marshal_snapshot([man], full=(intel.visibility == FULL))[0]
        entry[SEEN_TURN_KEY] = turn
        intel.known_marshals = ([km for km in intel.known_marshals
                                 if snapshot_entry(km).get("name") != actor] + [entry])
        written += 1
    return written


def enemy_sightings(world, viewer: str) -> List[Dict[str, Any]]:
    """AAR-5: the dispatch's / Ledger's rows — one per enemy marshal, the
    live sighting first, then the frozen snapshots where the fog is real
    (PARTIAL / STALE / LAST_KNOWN, and a label in sight whose live read lacks
    him — that label is yesterday's), deduped so a "[partial]" row never
    outranks a live one. Sorted FULL → PARTIAL → STALE → LAST_KNOWN.

    RR6-X3: THE sighting rule (`last_seen` reads it) — the live read covers
    every corps IN SIGHT (a PARTIAL label too, the map's rule), and each
    snapshot entry carries its own turn (`entry_seen_turn`)."""
    from backend.models.intel import entry_seen_turn, snapshot_entry
    rank = VISIBILITY_PRIORITY
    sightings: Dict[str, Dict[str, Any]] = {}
    if THE_SIGHTING_IS_LIVE:
        sightings.update(_in_sight_rows(world, viewer))
    for region_name, intel in world.intel.items():
        vis = intel.visibility
        if vis == UNKNOWN:
            continue
        frozen_full = False
        if THE_SIGHTING_IS_LIVE and vis == FULL:
            # Read live above; a frozen FULL snapshot naming a man who is
            # not there is yesterday's LABEL — but it is still the player's
            # most recent KNOWLEDGE of him, so it rides as last_known with
            # its own turn (A_FULL_LABEL_KEEPS_ITS_LAST_SIGHTING) — unless
            # the man STANDS in a full-view province today, where the live
            # read is the whole truth and already decided (an empty corps,
            # a prisoner, a man in plain sight), or he is on no roster at
            # all (a phantom label: SR-6a's own ledger pin). (A PARTIAL
            # label's snapshot keeps its tier — "reported" — as it always
            # has; RR6-X3 moves only the place, never a report's word.)
            if not A_FULL_LABEL_KEEPS_ITS_LAST_SIGHTING:
                continue
            frozen_full = True
            vis = LAST_KNOWN
        for km in map(snapshot_entry, intel.known_marshals):
            if km.get("nation") == viewer:
                continue
            name = km.get("name", "Unknown")
            if frozen_full and name not in (getattr(world, "marshals", {}) or {}):
                continue  # a label with no man behind it is no sighting
            if A_FULL_LABEL_KEEPS_ITS_LAST_SIGHTING:
                # A man STANDING in a full-view province today is the live
                # read's to show or to omit (an empty corps, a prisoner) —
                # no frozen snapshot of him, here or elsewhere, rides.
                _standing = world.marshals.get(name) if hasattr(world, "marshals") else None
                _where = world.intel.get(str(getattr(_standing, "location", "") or ""))
                if _standing is not None and _where is not None and (
                        _where.visibility == FULL
                        or in_sight(world, viewer, _standing)):
                    continue  # the live read already spoke for him (RR6-X3: in sight)
            if A_PRISONER_IS_NOT_A_SIGHTING:
                # Score Finish Step 3 exit (narration C4): a man the roster
                # knows to be a PRISONER never rides as a frozen snapshot —
                # measured on CMD-H turn 40, Deroy taken at Franche-Comte in
                # the enemy phase and his three-turn-old Franconia label still
                # on the morning's intelligence rows. The prisoner surface
                # names him; the live read already skips him (`captured_by`).
                _man = world.marshals.get(name) if hasattr(world, "marshals") else None
                if _man is not None and getattr(_man, "captured_by", ""):
                    continue
            updated = entry_seen_turn(intel, km)
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
