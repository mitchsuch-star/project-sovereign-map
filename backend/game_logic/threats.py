"""Row IC "Independent Command", the desk (November 19, 2026) — WHAT AN ENEMY WE
CAN SEE CAN REACH.

The first playtest's Carniola: taken on turn 3, walked back into by Austria on
turn 5 "because nothing stood there". The game knew, the turn before, that an
Austrian corps stood one march from a province nothing held — the typed "is
Carniola safe?" would have said so — and nothing on the screen did.

ONE reading, three readers:

* `visible_threats` — every enemy corps at war with us THAT WE CAN SEE within
  two marches of a province (the typed "is X safe?", `question_desk._answer_safe`,
  whose loop this is, moved here unchanged);
* `stands_in_the_way` — what of ours would stop a march into a province: a
  corps, a garrison that fights, or its works — the attack road's own exits
  (`ground.standing`, `garrison_report.garrison_fights`), read for OUR ground;
* `in_danger` — the provinces of ours an enemy we can see could walk into on
  his next march because nothing stands in his way (the desk's TO DECIDE row,
  the map's mark, the End Turn list, and the report's "you were warned").

PURE: it reads the world and writes nothing. FOG (R5): only
`world.get_visible_enemies` — a corps we cannot see is never named, counted or
drawn; a strength is the figure our own intel shows (exact at FULL, his band
at PARTIAL — `intel_surfaces.sighting_row`'s rule). Golden rule 8: it walks
the enemies we can see and their neighbours, never the regions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from backend.display_names import humanize_entity_name
from backend.errors import report

# How many provinces the danger reading lists (the rest are counted).
MAX_DANGER_ROWS = 12


def _force_words(world, enemy) -> str:
    """The strength our own intel shows for a corps in sight: "52,000 men" at
    FULL, his band ("large force") at PARTIAL — `_answer_safe`'s words."""
    from backend.models.intel import FULL, get_strength_band
    intel = world.get_region_intel(enemy.location)
    return (f"{int(enemy.strength):,} men" if intel.visibility == FULL
            else get_strength_band(int(enemy.strength)))


def _shown_strength(world, enemy) -> int:
    """A figure to ORDER threats by that gives nothing away: the exact strength
    at FULL, the band's midpoint at PARTIAL (the dispatch's `BAND_MIDPOINTS`)."""
    from backend.models.intel import FULL, get_strength_band
    if world.get_region_intel(enemy.location).visibility == FULL:
        return int(enemy.strength)
    from backend.game_logic.dispatch import BAND_MIDPOINTS
    return int(BAND_MIDPOINTS.get(get_strength_band(int(enemy.strength)), 0))


def two_marches(world, region_name: str) -> Tuple[List[str], set]:
    """The provinces one march from `region_name` (in its own order) and the
    set two marches off."""
    region = world.get_region(region_name)
    adjacent = list(getattr(region, "adjacent_regions", None) or []) if region is not None else []
    two_off = set()
    for name in adjacent:
        near = world.get_region(name)
        for far in (getattr(near, "adjacent_regions", None) or []) if near else []:
            if far != region_name and far not in adjacent:
                two_off.add(far)
    return adjacent, two_off


def visible_threats(world, player: str, region_name: str) -> List[Tuple[int, Any, str]]:
    """Every enemy corps AT WAR with `player` that he can SEE within two
    marches of `region_name`: (marches, the corps, the force as his intel shows
    it), nearest first and then the strongest — `_answer_safe`'s own list."""
    adjacent, two_off = two_marches(world, region_name)
    threats = []
    for enemy in world.get_visible_enemies(player):
        if int(getattr(enemy, "strength", 0) or 0) <= 0:
            continue
        if not world.is_at_war(player, getattr(enemy, "nation", "")):
            continue
        where = enemy.location
        if where == region_name:
            steps = 0
        elif where in adjacent:
            steps = 1
        elif where in two_off:
            steps = 2
        else:
            continue
        threats.append((steps, enemy, _force_words(world, enemy)))
    threats.sort(key=lambda t: (t[0], -int(t[1].strength)))
    return threats


def stands_in_the_way(world, region, player: str, foe_nation: str = "") -> str:
    """What of OURS would stop a march into `region` — "corps", "garrison",
    "works", or "" (nothing: he walks in and it is his).

    The attack road's own exits, read for our ground: a corps in the field
    (ours, or a friend's that is at war with the marcher), a garrison that
    FIGHTS (`garrison_report.garrison_fights` — a detachment under the
    surrender floor and a capital's works under the collapse line give way to
    a march), and a fortification (it must be besieged, which takes turns)."""
    if region is None:
        return ""
    for m in world.get_marshals_in_region(region.name):
        if int(getattr(m, "strength", 0) or 0) <= 0 or getattr(m, "captured_by", ""):
            continue
        if m.nation == player:
            return "corps"
        if foe_nation and world.are_allies(player, m.nation) and world.is_at_war(m.nation, foe_nation):
            return "corps"
    from backend.game_logic.garrison_report import garrison_fights
    if garrison_fights(region):
        return "garrison"
    if region.has_building("fortification"):
        return "works"
    return ""


def in_danger(world, player: str) -> List[Dict[str, Any]]:
    """The provinces of `player` that an enemy he can SEE could walk into on
    his next march, because nothing of ours stands in his way.

    Rows, the heaviest threat first: {region, by (roster keys), by_shown, force
    (the heaviest's, as our intel shows it), more (how many other corps),
    garrison (OUR token garrison there, 0 with none), line}.
    `line` is one plain sentence, 90 characters at most:
    "Nothing holds Bavaria — Mack (52,000 men) is one march away."

    One march is the reading, for every corps: it is the game's own "in
    danger" verdict (`_answer_safe`), and it claims nothing about an arm we
    may not have seen. [] on any error (the reading is display)."""
    try:
        return _in_danger(world, player)
    except Exception as exc:
        report(exc, "threats.in_danger")
        return []


def can_walk_in(world, player: str, enemy, region) -> bool:
    """Could THIS corps take `region` by marching onto it — as far as the
    player can know? Two of the march's own rules, each read only where the
    player holds the facts it turns on (the review, IC-R1 and IC-R8):

    * the water: a sea link the crossing gate shuts to his court is no road
      (`naval.crossing_allowed` — the fleets are on every court's ledger);
    * the raiding party: a corps of fewer than `RAIDING_PARTY_FLOOR` men holds
      no homeland province it walks onto — read only at FULL sight, where the
      player sees the exact count (at PARTIAL he knows a band, and a mark that
      vanished below the floor would hand him the number).

    The recovery after a retreat (`corps_takes_no_ground`) is NOT read: no
    screen shows the player an enemy's recovery, so the warning stands — it is
    the cautious reading, and it gives nothing away."""
    from backend.game_logic import naval
    if naval.is_sea_link(world, str(enemy.location), str(region.name)) \
            and not naval.crossing_allowed(world, str(enemy.nation), str(enemy.location), str(region.name)):
        return False
    from backend.models.intel import FULL
    if world.get_region_intel(enemy.location).visibility == FULL:
        from backend.commands.movement_executor import raiding_party_holds_no_ground
        if raiding_party_holds_no_ground(enemy, region, world):
            return False
    return True


def _in_danger(world, player: str) -> List[Dict[str, Any]]:
    found: Dict[str, List[Any]] = {}
    open_ground: Dict[str, bool] = {}
    for enemy in world.get_visible_enemies(player):
        if int(getattr(enemy, "strength", 0) or 0) <= 0:
            continue
        here = world.get_region(enemy.location)
        if here is None:
            continue
        for name in getattr(here, "adjacent_regions", None) or []:
            key = f"{name}|{enemy.nation}"
            if key not in open_ground:
                region = world.get_region(name)
                open_ground[key] = bool(
                    region is not None
                    and getattr(region, "controller", None) == player
                    and not stands_in_the_way(world, region, player, enemy.nation))
            if open_ground[key] and can_walk_in(world, player, enemy, world.get_region(name)):
                found.setdefault(name, []).append(enemy)
    rows: List[Dict[str, Any]] = []
    for name, enemies in found.items():
        enemies = sorted(enemies, key=lambda e: (-_shown_strength(world, e), e.name))
        lead = enemies[0]
        rows.append({
            "region": name,
            "by": [e.name for e in enemies],
            "by_shown": [humanize_entity_name(e.name) for e in enemies],
            "from": str(lead.location),
            "force": _force_words(world, lead),
            "more": int(len(enemies) - 1),
            # OUR garrison there, when one stands that a march walks through
            # (`stands_in_the_way` said nothing fights): the line then says the
            # garrison is too small, not that nothing is there.
            "garrison": int(getattr(world.get_region(name), "garrison_strength", 0) or 0),
            "_rank": (-_shown_strength(world, lead), name),
        })
    rows.sort(key=lambda r: r["_rank"])
    for row in rows:
        row.pop("_rank", None)
        row["line"] = danger_line(row)
    return rows[:MAX_DANGER_ROWS]


def danger_line(row: Dict[str, Any], cap: int = 90) -> str:
    """One sentence for a province in danger, `cap` characters at most — the
    fullest form that fits; the last one cut at a word, never inside one."""
    region = str(row.get("region") or "")
    shown = list(row.get("by_shown") or [])
    lead = shown[0] if shown else "an enemy corps"
    force = str(row.get("force") or "")
    more = int(row.get("more", 0) or 0)
    others = f" and {more} more" if more > 0 else ""
    verb = "are" if more > 0 else "is"
    if int(row.get("garrison", 0) or 0) > 0:
        head, short = f"{region}'s garrison is too small to hold it", f"{region}: its garrison is too small"
    else:
        head, short = f"Nothing holds {region}", f"{region}: nothing holds it"
    forms = [
        f"{head} — {lead} ({force}){others} {verb} one march away.",
        f"{head} — {lead}{others} {verb} one march away.",
        f"{head} — an enemy corps is one march away.",
        f"{short}, and an enemy is one march away.",
    ]
    for text in forms:
        if len(text) <= cap:
            return text
    cut = forms[-1][:max(1, cap - 1)].rsplit(" ", 1)[0].rstrip(" ,;:—-")
    return cut + "…"
