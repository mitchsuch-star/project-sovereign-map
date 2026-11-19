"""Row PW "Plain Words" (November 18, 2026 — the first playtest): DOES HE TAKE IT?

The player, of his first thirteen turns: "sometimes they enter enemy land
without taking it", "i had 3 people in colinia and no one could take it". The
rules were all there and all sound — a corps takes a province by walking onto
it only when nothing holds it and the corps is fit to hold ground — but they
were said once, afterwards, in one line of the log, and never BEFORE the
order. A corps already standing on enemy ground had no control that took it:
the way was to type "attack <province>".

This module is the ONE plain reading of that question, for the surfaces that
ask it before an order is given (the click road's quotes, the province panel,
the selection card, the end-turn ask) and after one (the move's reply):

* `entering(world, marshal, region)` — what walking onto the province does;
* `standing(world, marshal)` — why the province he stands in is not ours, and
  the order that would make it so;
* `can_take_where_he_stands(world, marshal)` — the end-turn ask's predicate.

PURE: every function reads the world and writes nothing. Each rule is read
from the predicate the executor itself runs — `garrison_report.
garrison_fights`, `movement_executor.corps_takes_no_ground` and
`raiding_party_holds_no_ground`, `Region.has_building("fortification")`,
`world_state.liberates_ally_ground` — never a copy of its numbers.

FOG (R5): the reading is the PLAYER's. An enemy corps is named only where
`get_visible_enemies_in_region` shows him; a garrison only as far as
`garrison_report.garrison_view` gives it (the map's own rule: a count on a
FULL read, a band on a partial one, nothing otherwise); works only on a
province the player reads at all. Where the player cannot see, the reading
says so ("if nothing we cannot see holds it") and promises nothing.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from backend.display_names import humanize_entity_name
from backend.errors import report


# The readings of `standing` the province panel prints a row for: ground we
# are at war for (takeable or not, and why), and ground a peace closed under
# a corps of ours. An ally's or a neutral's province draws no row.
SAID_ON_THE_PANEL = frozenset({
    "open", "garrison", "fort", "enemy_corps", "raiding", "besieging", "peace_passage"})


def the_ground_is_read_before_the_order() -> bool:
    """Row PW seam (one line to reverse): the quotes, the panel and the move's
    reply carry the ground reading. Down (False): no `ground` key anywhere and
    the move's reply as it stood."""
    return True


def _court(world, nation: str) -> str:
    try:
        from backend.game_logic.formations import formed_display_name
        return formed_display_name(world, nation)
    except Exception as exc:
        report(exc, "ground._court: formed_display_name")
        return str(nation)


def _blank() -> Dict[str, Any]:
    return {
        # True: the province becomes ours. False: he may stand there and it
        # stays theirs. None: there is nothing to take (ours, or no war).
        "takes": None,
        "code": "",
        # one short plain line for a tag or a card ("takes the province")
        "line": "",
        # the order that would take it, when one exists, and its button's words
        "remedy_command": "",
        "remedy_label": "",
    }


def _sees(world, region_name: str) -> str:
    """'full' / 'partial' / 'none' — how the player reads the province."""
    try:
        from backend.models.intel import FULL, PARTIAL, STALE
        visibility = world.get_region_intel(region_name).visibility
        if visibility == FULL:
            return "full"
        if visibility in (PARTIAL, STALE):
            return "partial"
    except Exception as exc:
        report(exc, "ground._sees: world.get_region_intel")
    return "none"


def _visible_foes(world, region_name: str, nation: str) -> list:
    """The enemy corps the PLAYER sees standing in the province, at war with
    `nation` — names only where the sighting rule shows them (R5)."""
    out = []
    try:
        for row in world.get_visible_enemies_in_region(region_name, world.player_nation):
            name = row.get("name") if isinstance(row, dict) else getattr(row, "name", "")
            foe = world.get_marshal(name) if name else None
            if (foe is not None and int(getattr(foe, "strength", 0) or 0) > 0
                    and world.is_at_war(nation, foe.nation)):
                out.append(foe)
    except Exception as exc:
        report(exc, "ground._visible_foes: world.get_visible_enemies_in_region")
    return out


def _unfit(marshal, region, world) -> Optional[Dict[str, str]]:
    """The MOVER's own state that keeps him from holding ground he walks onto:
    the recovery window (FA-9), the raiding party (VP-R1 b). None when fit."""
    from backend.commands.movement_executor import (
        RAIDING_PARTY_FLOOR, corps_takes_no_ground, raiding_party_holds_no_ground)
    shown = humanize_entity_name(marshal.name)
    if corps_takes_no_ground(marshal):
        return {"code": "recovering",
                "line": f"enters only — {shown}'s men are still rallying from a defeat"}
    if raiding_party_holds_no_ground(marshal, region, world):
        return {"code": "raiding",
                "line": (f"enters only — fewer than {RAIDING_PARTY_FLOOR:,} men cannot hold "
                         f"an enemy's home province")}
    return None


def _garrison(world, region, viewer: str) -> Optional[Dict[str, str]]:
    """What the player may know of a garrison that would hold the province
    against a march: {'code', 'words'} or None (none stands, or none that
    fights, as far as he can see)."""
    from backend.game_logic.garrison_report import garrison_fights, garrison_view
    form, value = garrison_view(world, region.name, viewer)
    if form == "exact":
        if garrison_fights(region):
            return {"code": "garrison", "words": f"a garrison of {int(value):,} holds it"}
        return None       # too few to hold: it gives way to the march
    if form == "band":
        # A band, never a count: the player knows that one stands, not whether
        # it is the size that fights. Said as what he knows.
        return {"code": "garrison_unsure",
                "words": f"a garrison ({value}) stands there — it may have to be stormed"}
    return None


def entering(world, marshal, region_name: str) -> Dict[str, Any]:
    """What walking onto `region_name` does to it, as far as the player sees."""
    out = _blank()
    region = world.get_region(region_name) if region_name else None
    if region is None or marshal is None:
        return out
    nation = marshal.nation
    controller = getattr(region, "controller", None)
    shown = humanize_entity_name(marshal.name)
    # A corps of the enemy's in plain sight comes first, on any ground: the
    # move itself is refused while he stands there ("use ATTACK").
    foes = _visible_foes(world, region_name, nation)
    if foes:
        foe = humanize_entity_name(max(foes, key=lambda m: int(m.strength)).name)
        ours_to_take = bool(controller and controller != nation
                            and world.is_at_war(nation, controller))
        out.update(takes=False if ours_to_take else None, code="enemy_corps",
                   line=f"{foe} stands there — he must be beaten first",
                   remedy_command=f"{shown}, attack {foe}", remedy_label=f"Attack {foe}")
        return out
    if not controller or controller == nation:
        out["code"] = "ours" if controller == nation else "nobody"
        return out
    if not world.is_at_war(nation, controller):
        # An ally's or a neutral's province: nothing to take and nothing to
        # say — a line here ("Italy's land — it stays theirs") read as a
        # warning on every march across a friend's ground.
        out["code"] = "not_at_war"
        return out
    seen = _sees(world, region_name)
    # The review (PW-R2): the garrison BEFORE the works — the order that takes
    # the province storms the garrison first and only then lays the siege
    # (`_attack_*`: `garrison_fights` → `_resolve_garrison_combat`), so the
    # remedy named here is the one the order then is ("Storm", never
    # "Besiege", where both stand). `standing` reads them in the same order.
    garrison = _garrison(world, region, world.player_nation)
    if garrison is not None:
        out.update(takes=False if garrison["code"] == "garrison" else None,
                   code=garrison["code"], line=f"enters only — {garrison['words']}",
                   remedy_command=f"{shown}, attack {region_name}",
                   remedy_label=f"Storm {region_name}")
        if garrison["code"] == "garrison_unsure":
            out["line"] = garrison["words"]
        return out
    # The review (PW-R1, fog): a foreign province's BUILDINGS are the player's
    # to read at FULL sight only (`WorldState.region_econ_visible`, the ONE
    # predicate — FOG_OF_WAR_SPEC: the economic block). At PARTIAL or on an
    # old report the works are not named: the reading below promises nothing
    # ("takes it if nothing we cannot see holds it").
    try:
        works_seen = bool(world.region_econ_visible(region_name))
    except Exception as exc:
        report(exc, "ground.entering: region_econ_visible")
        works_seen = False
    if works_seen and region.has_building("fortification"):
        out.update(takes=False, code="fort",
                   line="enters only — the province is fortified: it must be besieged",
                   remedy_command=f"{shown}, attack {region_name}",
                   remedy_label=f"Besiege {region_name}")
        return out
    unfit = _unfit(marshal, region, world)
    if unfit is not None:
        out.update(takes=False, code=unfit["code"], line=unfit["line"])
        return out
    try:
        from backend.models import world_state as _ws
        freed = _ws.liberates_ally_ground(world, region_name, nation)
    except Exception as exc:
        report(exc, "ground.entering: liberates_ally_ground")
        freed = ""
    if seen != "full":
        # The player does not read the province whole: a corps or a garrison
        # he cannot see may hold it. Promise nothing (R5).
        out.update(takes=None, code="takes_if_open",
                   line=(f"frees it for {_court(world, freed)} if nothing we cannot see holds it"
                         if freed else "takes it if nothing we cannot see holds it"))
        return out
    if freed:
        out.update(takes=True, code="liberates", line=f"frees it for {_court(world, freed)}")
        return out
    out.update(takes=True, code="takes", line="takes the province")
    return out


def standing(world, marshal) -> Dict[str, Any]:
    """Why the province `marshal` stands in is not ours, and the order that
    would take it — the attack road's own exits, in its order: a corps in the
    field, a garrison that fights, the raiding party, the works, the open
    province ("takes it where he stands")."""
    out = _blank()
    if marshal is None:
        return out
    region = world.get_region(marshal.location)
    if region is None:
        return out
    nation = marshal.nation
    controller = getattr(region, "controller", None)
    if not controller or controller == nation:
        out["code"] = "ours" if controller == nation else "nobody"
        return out
    name = region.name
    shown = humanize_entity_name(marshal.name)
    if not world.is_at_war(nation, controller):
        out["code"] = "not_at_war"
        out["line"] = f"{name} is {_court(world, controller)}'s and we are not at war — it stays theirs"
        try:
            from backend.game_logic.withdrawal import has_evacuation_grant
            if has_evacuation_grant(world, nation, controller):
                out["code"] = "peace_passage"
                out["line"] = (f"{name} is {_court(world, controller)}'s by the peace — "
                               f"{shown} has safe passage home and must leave")
        except Exception as exc:
            report(exc, "ground.standing: has_evacuation_grant")
        return out
    foes = [m for m in world.get_marshals_in_region(name)
            if m.nation != nation and int(getattr(m, "strength", 0) or 0) > 0
            and world.is_at_war(nation, m.nation)]
    if foes:
        # He stands on the same ground: the corps is in plain sight.
        strongest = max(foes, key=lambda m: int(m.strength))
        foe = humanize_entity_name(strongest.name)
        out.update(takes=False, code="enemy_corps",
                   line=f"{foe} still stands in {name} — beat him and it can be taken",
                   remedy_command=f"{shown}, attack {foe}", remedy_label=f"Attack {foe}",
                   foe=strongest.name)     # his roster key: the attack card's target
        return out
    occupying = str(getattr(marshal, "occupation_region", "") or "")
    if occupying == name:
        need = int(getattr(marshal, "occupation_turns_required", 0) or 0)
        held = int(getattr(marshal, "occupation_turns_held", 0) or 0)
        left = max(0, need - held)
        out.update(takes=False, code="besieging",
                   line=(f"{shown} is besieging {name} — it falls in "
                         f"{left} more turn{'s' if left != 1 else ''} if he holds"))
        return out
    from backend.game_logic.garrison_report import garrison_fights
    take = f"{shown}, attack {name}"
    if garrison_fights(region):
        garrison = int(getattr(region, "garrison_strength", 0) or 0)
        out.update(takes=False, code="garrison",
                   line=f"a garrison of {garrison:,} holds it — it must be stormed",
                   remedy_command=take, remedy_label=f"Storm {name}")
        return out
    from backend.commands.movement_executor import (
        RAIDING_PARTY_FLOOR, raiding_party_holds_no_ground)
    if raiding_party_holds_no_ground(marshal, region, world):
        out.update(takes=False, code="raiding",
                   line=(f"{shown} has fewer than {RAIDING_PARTY_FLOOR:,} men — too few to hold "
                         f"an enemy's home province. Bring a larger corps."))
        return out
    if region.has_building("fortification"):
        out.update(takes=False, code="fort",
                   line=f"it is fortified — {shown} must besiege it and hold",
                   remedy_command=take, remedy_label=f"Besiege {name}")
        return out
    out.update(takes=True, code="open",
               line=f"nothing holds it — {shown} can take it now",
               remedy_command=take, remedy_label=f"Take {name}")
    return out


def can_take_where_he_stands(world, marshal) -> bool:
    """The end-turn ask: an order of one action would make the province ours
    now (nothing holds it), and he has not been told to do anything else."""
    try:
        return standing(world, marshal).get("code") == "open"
    except Exception as exc:
        report(exc, "ground.can_take_where_he_stands")
        return False


def after_the_move(world, marshal, region_name: str, captured: bool) -> Dict[str, Any]:
    """The reading for the move's own reply: {} when the province was taken or
    was never an enemy's to take; else why it is still theirs, as `standing`
    reads it now that he is there, with the order that would take it."""
    if captured or not the_ground_is_read_before_the_order():
        return {}
    try:
        reading = standing(world, marshal)
    except Exception as exc:
        report(exc, "ground.after_the_move: standing")
        return {}
    if reading.get("code") in ("", "ours", "nobody", "not_at_war", "peace_passage"):
        return {}
    return reading
