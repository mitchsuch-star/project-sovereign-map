"""The walls and the guns (row BA, session BA-2) — the tableau payloads of a
garrison assault and of a standalone bombardment.

Owner: `docs/BATTLE_DIORAMA_SPEC.md` §15.5.4 (the user's ruling 8, "Both get
a tableau") and §15.12 (the landing record). It closes the garrison rider of
§12.5 (CA8-25): a stormed garrison rendered no tableau because the tableau
had no defender without a marshal.

Both payloads have the SHAPE the field battle's has
(`battle_diorama.build_battle_diorama`) and ride the SAME two transports —
`result["battle_diorama"]` and `events[0]["diorama"]` — so the response
layer, the enemy phase and the client read them with no new key. `kind`
tells the table which to lay: "assault" (a wall, and a garrison block that
has no commander) or "bombardment" (the cannonade alone). A field battle's
payload carries no `kind`.

The laws are the field battle's own:

1. Display only (Golden Rule 6). Nothing here is read by routing or
   mechanics; nothing is written to a marshal, a region or the world.
2. Every figure is one the resolver already produced.
3. Fog. The player a party to it -> the payload exists. Otherwise it exists
   only when the province is FULL-visible to the player (the field battle's
   gate; every battle lights its own province, `update_intel_from_battle`).
4. Every number is an int (Golden Rule 2): the top-level key is not
   float-stripped on the way out.
"""

from typing import List, Optional

from backend import errors as _errors
from backend.display_names import humanize_entity_name
from backend.game_logic import battle_diorama as _bd
from backend.models.intel import FULL

ASSAULT = "assault"
BOMBARDMENT = "bombardment"

# What the wall did (the assault's three exits).
HELD = "held"
STORMED = "stormed"
CAPITULATED = "capitulated"

# The banner over the table, by whose table it is and what the wall did. The
# field battle's own words do not fit a wall ("THE FIELD IS OURS").
_ASSAULT_BANNERS = {
    ("attacker", STORMED): "THE WALLS ARE CARRIED",
    ("attacker", CAPITULATED): "THE GARRISON CAPITULATES",
    ("attacker", HELD): "THE ASSAULT FAILS",
    ("defender", HELD): "THE WALLS HOLD",
    ("defender", STORMED): "THE WALLS ARE LOST",
    ("defender", CAPITULATED): "THE GARRISON HAS YIELDED",
    (None, HELD): "THE WALLS HOLD",
    (None, STORMED): "THE WALLS ARE CARRIED",
    (None, CAPITULATED): "THE GARRISON CAPITULATES",
}


def _i(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def garrison_name(region_name: str) -> str:
    """The garrison block's name on the table: it has no commander, so it is
    named for its walls."""
    return f"{region_name} garrison"


def _player_side(world, attacker_nation: str, defender_nation: str) -> Optional[str]:
    player = str(getattr(world, "player_nation", "France") or "France")
    if attacker_nation == player:
        return "attacker"
    if defender_nation == player:
        return "defender"
    return None


def _in_sight(world, region_name: str, player_side: Optional[str]) -> bool:
    """The field battle's gate: the player fought there, or sees it whole."""
    if player_side is not None:
        return True
    intel = world.get_region_intel(region_name)
    return getattr(intel, "visibility", None) == FULL


def _great(world, men: int) -> bool:
    return bool(int(men) >= int(getattr(world, "GREAT_BATTLE_THRESHOLD", 10 ** 9)))


def _carry(result: dict, payload: Optional[dict]) -> dict:
    """Both transports. The event is COPIED: a bombardment logs the very dict
    it returns as `events[0]`, and a tableau written onto it would be written
    into the campaign log and the save."""
    if not payload:
        return result
    result["battle_diorama"] = payload
    events = result.get("events") or []
    if events and isinstance(events[0], dict):
        result["events"] = [dict(events[0], diorama=payload)] + list(events[1:])
    return result


# ─────────────────────────────────────────────────────────────────────────────
# The assault on a garrison
# ─────────────────────────────────────────────────────────────────────────────

def build_assault_diorama(world, marshal, region, result: dict, facts: dict,
                          held: bool) -> Optional[dict]:
    """The tableau of one garrison assault, or None when fog says the player
    may not see those walls.

    `result` is the assault's own result (its events say whether the province
    was taken or a siege laid); `facts` are the resolver's locals, handed over
    as it leaves: `attacker_before`, `attacker_losses`, `garrison_before`,
    `garrison_losses`, `capitulated`, `defender_nation` (the walls' owner
    BEFORE any capture), `fortified`, `drilled` (drill stacks spent), `iron`
    (Iron Resolve stacks released)."""
    atk_nation = str(getattr(marshal, "nation", "") or "")
    def_nation = str(facts.get("defender_nation") or "")
    region_name = str(getattr(region, "name", "") or "")
    player_side = _player_side(world, atk_nation, def_nation)
    if not _in_sight(world, region_name, player_side):
        return None

    fate = HELD if held else (CAPITULATED if facts.get("capitulated") else STORMED)
    atk_before = max(0, _i(facts.get("attacker_before")))
    atk_lost = min(atk_before, max(0, _i(facts.get("attacker_losses"))))
    gar_before = max(0, _i(facts.get("garrison_before")))
    # A wall that falls loses every man behind it — killed or taken (the
    # assault's own line: "Garrison collapses (12,000 -> 0)").
    gar_lost = min(gar_before, max(0, _i(facts.get("garrison_losses")))) if held else gar_before
    gar_left = gar_before - gar_lost

    events = [e for e in (result.get("events") or []) if isinstance(e, dict)]
    conquest = next((e for e in events if e.get("type") == "conquest"), None)
    siege = next((e for e in events if e.get("type") == "occupation_started"), None)
    conquered = bool(conquest)
    liberated_to = str((conquest or {}).get("liberated_to") or "")

    attacker = _bd._contingent(
        marshal, atk_before, atk_lost, atk_before - atk_lost,
        "destroyed" if atk_before - atk_lost <= 0 else "engaged", True, world)
    walls = garrison_name(region_name)
    garrison = {
        "name": walls,
        "nation": def_nation,
        "arm": "infantry",
        "committed": int(gar_before),
        "casualties": int(gar_lost),
        "remaining": int(gar_left),
        "status": "engaged" if held else "destroyed",
        "lead": True,
        "crowned": False,
        "sovereign": False,
        # the table's mark for a block with no commander: no portrait, no
        # standard to take
        "garrison": True,
    }
    attacker_side = _bd._cap_side([attacker])
    attacker_side["nation"] = atk_nation
    defender_side = _bd._cap_side([garrison])
    defender_side["nation"] = def_nation

    outcome = "defender_victory" if held else "attacker_victory"
    great = _great(world, atk_before + gar_before)
    shown_region = humanize_entity_name(region_name)
    name = {
        HELD: f"Assault on {shown_region}",
        STORMED: f"Storming of {shown_region}",
        CAPITULATED: f"Capitulation of {shown_region}",
    }[fate]
    if fate == HELD:
        observation = (f"The walls of {shown_region} stand. {gar_left:,} defenders remain "
                       f"behind them.")
    elif fate == CAPITULATED:
        observation = (f"The garrison of {shown_region} laid down its arms before the "
                       f"assault went home.")
    else:
        observation = f"{shown_region} is carried by storm."

    payload = {
        "kind": ASSAULT,
        "fate": fate,
        "battle_name": name,
        "region": region_name,
        **_bd.ground_key(world, region_name),      # BA-5: the province's terrain, for the table's felt
        "turn": _i(getattr(world, "current_turn", 0)),
        "outcome": outcome,
        "victor": walls if held else marshal.name,
        "attacker_nation": atk_nation,
        "defender_nation": def_nation,
        "player_side": player_side,
        "register": _bd.derive_register(player_side, outcome),
        # The field battle's two predicates, read for a wall: the player's
        # own assault always shows; the UNINVITED showing (the enemy's phase)
        # is earned by a wall that falls.
        "significant": bool(player_side is not None or not held or great),
        "dramatic": bool(not held or great),
        "great_battle": great,
        "region_conquered": conquered,
        "attacker": attacker_side,
        "defender": defender_side,
        "observation": observation,
        "banner": _ASSAULT_BANNERS[(player_side, fate)],
        "fortified": bool(facts.get("fortified")),
    }
    if player_side is not None:
        # BA-5 (the second reading): what told at the wall, under the headline
        # of an assault the player's court made or stood — as a field battle's
        # own table says it (`battle_day.the_verdicts_line`).
        try:
            from backend.game_logic import battle_telling as _telling
            if _telling.a_verdict_names_what_told():
                told = _telling.assault_told(
                    held, player_side == "attacker",
                    _i(facts.get("attacker_effective")) or atk_before,
                    _i(facts.get("garrison_effective")) or gar_before,
                    bool(facts.get("fortified")), men=(atk_before, gar_before))
                if told:
                    payload["verdict_told"] = told
        except Exception as exc:
            _errors.report(exc, "siege_diorama.build_assault_diorama: what told")
    if siege is not None:
        turns = _i(siege.get("turns_required"))
        payload["sub_banner"] = (
            f"{shown_region} is occupied: {turns} turn{'s' if turns != 1 else ''} to hold it."
            if turns > 0 else f"{shown_region} is occupied.")
        payload["siege_turns"] = turns
    if conquered and liberated_to:
        from backend.models.world_state import liberation_line
        payload["liberated_to"] = liberated_to
        payload["liberation_line"] = liberation_line(world, region_name, liberated_to)
    try:
        from backend.game_logic.battle_script import build_assault_script
        per_stack = float(getattr(marshal, "IRON_RESOLVE_BONUS_PER_STACK", 0.0) or 0.0)
        payload["script"] = build_assault_script(world, payload, marshal, dict(
            facts, iron_pct=int(round(_i(facts.get("iron")) * per_stack * 100))))
    except Exception as exc:
        _errors.report(exc, "siege_diorama.build_assault_diorama: the assault's script")
    return payload


def with_assault_tableau(world, result: dict, marshal, region, facts: dict,
                         held: bool = False) -> dict:
    """The assault's result with its tableau on both transports. A display
    layer never costs an assault its report: a failure is reported and the
    result goes out as it was."""
    try:
        if isinstance(result, dict) and result.get("success"):
            return _carry(result, build_assault_diorama(world, marshal, region, result,
                                                         facts or {}, held))
    except Exception as exc:
        _errors.report(exc, "siege_diorama.with_assault_tableau")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# The standalone bombardment
# ─────────────────────────────────────────────────────────────────────────────

def _levelled(br: dict) -> bool:
    """His works brought down to nothing by this salvo."""
    return bool(br.get("fort_degraded") and _i(br.get("fort_old")) > 0
                and _i(br.get("fort_new")) <= 0)


def _of_the_guns(world, nation: str, atk_nation: str, def_nation: str) -> bool:
    """A bystander of another crown that fights on the BATTERY's side: at war
    with the target's nation and not with the battery's."""
    if not nation or nation in (atk_nation, def_nation):
        return nation == atk_nation and bool(nation)
    try:
        return bool(world.is_at_war(nation, def_nation)) \
            and not bool(world.is_at_war(nation, atk_nation))
    except Exception as exc:
        _errors.report(exc, "siege_diorama._of_the_guns")
        return False


def build_bombardment_diorama(world, battery, target, result: dict) -> Optional[dict]:
    """The tableau of one standalone bombardment — the cannonade alone — or
    None when fog says the player may not see that field. Built from the
    bombardment's own result (`bombardment_result`) and event."""
    br = result.get("bombardment_result") if isinstance(result, dict) else None
    if not isinstance(br, dict):
        return None
    event = next((e for e in (result.get("events") or [])
                  if isinstance(e, dict) and e.get("type") == "bombardment"), {})
    atk_nation = str(getattr(battery, "nation", "") or "")
    def_nation = str(getattr(target, "nation", "") or "")
    region_name = str(event.get("defender_location") or getattr(target, "location", "") or "")
    player_side = _player_side(world, atk_nation, def_nation)
    if not _in_sight(world, region_name, player_side):
        return None

    atk = br.get("attacker") or {}
    dfd = br.get("defender") or {}
    atk_lost, atk_left = max(0, _i(atk.get("casualties"))), max(0, _i(atk.get("remaining")))
    def_lost, def_left = max(0, _i(dfd.get("casualties"))), max(0, _i(dfd.get("remaining")))
    destroyed = def_left <= 0
    # A battery standing in its target's own province is caught by its own
    # stray shells: the collateral roll takes every corps there but the
    # target (BA2-X12 owns that rule). The table seats him ONCE, as the
    # battery, and counts those dead with his own — never a second block for
    # the same man beside his target (the review, November 15, 2026).
    gunner = str(getattr(battery, "name", "") or "")
    atk_lost += sum(max(0, _i(row.get("casualties"))) for row in (br.get("collateral") or [])
                    if isinstance(row, dict) and str(row.get("name", "") or "") == gunner)

    gunners = _bd._contingent(battery, atk_left + atk_lost, atk_lost, atk_left,
                              "destroyed" if atk_left <= 0 else "engaged", True, world)
    struck = _bd._contingent(target, def_left + def_lost, def_lost, def_left,
                             "destroyed" if destroyed else "engaged", True, world)
    others: List[dict] = []
    for row in br.get("collateral") or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("name", "") or "") == gunner:
            continue                  # the battery itself: counted with it, above
        bystander = (getattr(world, "marshals", None) or {}).get(str(row.get("name", "") or ""))
        lost = max(0, _i(row.get("casualties")))
        if bystander is None or lost <= 0:
            continue
        left = max(0, _i(getattr(bystander, "strength", 0)))
        entry = _bd._contingent(bystander, left + lost, lost, left,
                                "destroyed" if left <= 0 else "engaged", False, world)
        # a corps that stood by and was caught in the fire; ours when the
        # battery's own side shelled it
        entry["bystander"] = True
        entry["friendly_fire"] = bool(row.get("friendly_fire"))
        entry["of_the_guns"] = bool(entry["friendly_fire"] or _of_the_guns(
            world, str(getattr(bystander, "nation", "") or ""), atk_nation, def_nation))
        others.append(entry)

    attacker_side = _bd._cap_side([gunners])
    attacker_side["nation"] = atk_nation
    defender_side = _bd._cap_side([struck] + others)
    defender_side["nation"] = def_nation
    # A corps of the battery's own side that stood under the fire is SEATED
    # where it stood — beside the target — and COUNTED with its own side: the
    # loss counter and the bar are a side's, and the table showed Lannes's
    # dead as Austria's (the frames, November 14).
    seated = defender_side.get("contingents") or []
    for entry in others:
        if entry["of_the_guns"]:
            for key in ("casualties_total", "committed_total"):
                moved = _i(entry["casualties" if key == "casualties_total" else "committed"])
                defender_side[key] = int(defender_side[key] - moved)
                attacker_side[key] = int(attacker_side[key] + moved)
            if not any(entry is shown for shown in seated):
                # ...and one of them that found no seat is ITS side's reserve.
                # The reserve line stands beside a side's loss counter, and it
                # read "+2 corps in reserve — 700 lost" under Austria for two
                # French corps (the review, November 15, 2026: BA2-X11).
                lost = _i(entry["casualties"])
                defender_side["reserve_count"] = int(_i(defender_side.get("reserve_count")) - 1)
                attacker_side["reserve_count"] = int(_i(attacker_side.get("reserve_count")) + 1)
                if "reserve_casualties" in defender_side:
                    defender_side["reserve_casualties"] = int(
                        _i(defender_side.get("reserve_casualties")) - lost)
                    attacker_side["reserve_casualties"] = int(
                        _i(attacker_side.get("reserve_casualties")) + lost)

    # What a WATCHER of another crown's cannonade is told is what its script
    # tells him (battle_script, the cannonade's fog cases): who fired on whom
    # and who was destroyed. The works, the province the battery fired from and
    # Berthier's line are a party's.
    party = player_side is not None
    levelled = party and _levelled(br)
    opens = bool(destroyed or levelled)
    shown_region = humanize_entity_name(region_name)
    shown_target = humanize_entity_name(str(getattr(target, "name", "") or ""))
    if destroyed:
        banner = "DESTROYED UNDER THE GUNS"
    elif levelled:
        banner = "THE WORKS ARE LEVELLED"
    else:
        banner = "THE GUNS SPEAK"
    payload = {
        "kind": BOMBARDMENT,
        "battle_name": f"Cannonade at {shown_region}",
        "region": region_name,
        **_bd.ground_key(world, region_name),      # BA-5: the province's terrain, for the table's felt
        "turn": _i(getattr(world, "current_turn", 0)),
        # no field is won by guns alone: the register reads "grim" for a
        # party to it and "observer" for a watcher
        "outcome": BOMBARDMENT,
        "victor": None,
        "attacker_nation": atk_nation,
        "defender_nation": def_nation,
        "player_side": player_side,
        "register": _bd.derive_register(player_side, BOMBARDMENT),
        # §15.5.4: a link by default; it opens by itself only when it destroys
        # its target or brings his works down to nothing (guns never break a
        # corps — `combat_executor.shelled_morale`)
        "significant": opens,
        "dramatic": opens,
        "great_battle": False,
        "region_conquered": False,
        "attacker": attacker_side,
        "defender": defender_side,
        # Berthier reports the Emperor's own batteries (BA2-X1)
        "observation": (str(br.get("berthier_observation", "") or "")
                        if player_side == "attacker" else ""),
        "banner": banner,
        "works_old": _i(br.get("fort_old")) if party else 0,
        "works_new": _i(br.get("fort_new")) if party else 0,
        "battery_at": str(event.get("attacker_location") or "") if party else "",
    }
    if destroyed:
        payload["sub_banner"] = f"{shown_target}'s corps is no more."
    try:
        from backend.game_logic.battle_script import build_bombardment_script
        payload["script"] = build_bombardment_script(world, payload, battery, target, br)
    except Exception as exc:
        _errors.report(exc, "siege_diorama.build_bombardment_diorama: the cannonade's script")
    return payload


def with_bombardment_tableau(world, result: dict, battery, target) -> dict:
    """A STANDALONE bombardment's result with its tableau on both transports
    (never the supporting salvo before an assault: that one is a beat of the
    battle it prepares). A failure is reported and costs the salvo nothing."""
    try:
        if isinstance(result, dict) and result.get("success") \
                and result.get("bombardment_result"):
            return _carry(result, build_bombardment_diorama(world, battery, target, result))
    except Exception as exc:
        _errors.report(exc, "siege_diorama.with_bombardment_tableau")
    return result
