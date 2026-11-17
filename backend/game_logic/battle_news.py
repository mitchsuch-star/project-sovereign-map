"""Row BA, session BA-4 — BA2-X20's other half: news of a battle abroad.

A battle lights its field for those who fought in it
(`intel_surfaces.battle_lights_field`). So that Europe does not go dark with
that rule, a battle between crowns the player is no party to is told as NEWS
— the crowns, the province and who held the field, never a commander, a man
or a figure — when it is:

  * a GREAT battle (the game's own bar, `WorldState.GREAT_BATTLE_THRESHOLD`),
    whoever fought it; or
  * a battle of an ally's in a war the player shares (the ally against a
    court the player is at war with).

The news is a row of the campaign log (`foreign_battle`), which Le Moniteur
prints on its war page — a great one forces a special the turn after — and a
line of the morning's dispatch. Nothing here reads the dice or writes a
number of the game: it is built from the battle's own result after the
battle is over (GR6).

EVERY road a field is lit on tells its dark side (the session's review, lane
4: the news was written on the main attack's road alone, so an ally's
assault on a garrison, his guns, a cavalry charge and a corps destroyed by
the guns before the assault were told to nobody — before the rule each had
lit its field):

  * a field battle on any road — the attack, the charge, the charge the
    cavalry makes of itself, the attack whose guns destroyed the defender —
    is `of_a_battle`;
  * an assault on a garrison is `of_an_assault`: who stormed whose works and
    whether the place fell — a great one, or an ally's in a shared war;
  * a cannonade is `of_a_cannonade`: whose guns opened on whom — an ally's
    in a shared war only. A cannonade is no battle (it has no victor), so
    there is no "great" one and none forces a special.

Fog: a province's name and the crowns that met there are news; who commanded,
how many stood and how many fell are the field's own, and the field is not
the player's to see. Where the field IS in his sight (he scouted it, or a
corps of his stands beside it at FULL), the ordinary battle row tells him all
of it and no news is written.
"""
from __future__ import annotations

from typing import Optional

from backend.errors import report


def _crown(nation) -> str:
    from backend.display_names import display_nation, with_definite_article
    return with_definite_article(display_nation(str(nation or "")), capitalize=False)


def _the_players_ally(world, player: str, nation: str) -> bool:
    """An ally of the player's: an alliance of either kind, or lord and client."""
    if not nation or nation == player:
        return False
    if world.get_diplomatic_state(player, nation) in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
        return True
    vassals = getattr(world, "vassals", None) or {}
    return bool((vassals.get(nation) or {}).get("lord") == player
                or (vassals.get(player) or {}).get("lord") == nation)


def an_allys_in_a_shared_war(world, player: str, attacker_nation: str, defender_nation: str) -> str:
    """The ally's name when one side of the battle is the player's ally and
    the other a court the player is at war with; "" otherwise."""
    for ally, foe in ((attacker_nation, defender_nation), (defender_nation, attacker_nation)):
        if _the_players_ally(world, player, ally) and world.is_at_war(player, foe):
            return str(ally)
    return ""


def the_days_verdict(battle_result: dict, attacker_nation: str, defender_nation: str) -> tuple:
    """How the day ended, as Europe hears it — `(kind, crown)`:

      "held"    a crown held the field: the other army was driven from it
      "better"  a crown had the better of the day, and both armies still stand
      "ruin"    both armies were ruined on it
      "drawn"   neither gave way and neither won

    Read off the battle's own outcome; never a figure."""
    result = battle_result if isinstance(battle_result, dict) else {}
    outcome = str(result.get("outcome") or "")
    if outcome == "attacker_victory":
        return "held", str(attacker_nation)
    if outcome == "defender_victory":
        return "held", str(defender_nation)
    if outcome == "attacker_tactical_victory":
        return "better", str(attacker_nation)
    if outcome == "defender_tactical_victory":
        return "better", str(defender_nation)
    if outcome == "mutual_destruction":
        return "ruin", ""
    return "drawn", ""


def line_of(region_name: str, attacker_nation: str, defender_nation: str,
            verdict: tuple, *, great: bool, ally: str = "") -> str:
    """The news, in one sentence — crowns only, no figure."""
    first, second = _crown(attacker_nation), _crown(defender_nation)
    if great:
        head = f"News from {region_name}: {first} and {second} have fought a great battle"
    else:
        other = defender_nation if ally == attacker_nation else attacker_nation
        head = f"News from {region_name}: our ally {_crown(ally)} has fought {_crown(other)}"
    kind, crown = verdict
    if kind == "held":
        return f"{head} — {_crown(crown)} held the field."
    if kind == "better":
        return f"{head} — {_crown(crown)} had the better of the day."
    if kind == "ruin":
        return f"{head} — both armies were ruined on it."
    return f"{head} — the day was drawn."


def assault_line(region_name: str, attacker_nation: str, defender_nation: str,
                 fell: bool, *, great: bool, ally: str = "") -> str:
    """An assault on a garrison, in one sentence — who stormed whose works and
    whether the place fell; crowns only, no figure."""
    first, second = _crown(attacker_nation), _crown(defender_nation)
    if great:
        head = f"News from {region_name}: {first} has thrown a great assault on the works of {second}"
    elif ally == attacker_nation:
        head = f"News from {region_name}: our ally {first} has assaulted the works of {second}"
    else:
        head = f"News from {region_name}: {first} has assaulted the works of our ally {second}"
    return f"{head} — the place has fallen." if fell else f"{head} — the walls held."


def cannonade_line(region_name: str, attacker_nation: str, defender_nation: str, *, ally: str) -> str:
    """A cannonade, in one sentence — whose guns opened on whom."""
    first, second = _crown(attacker_nation), _crown(defender_nation)
    if ally == attacker_nation:
        return f"News from {region_name}: the guns of our ally {first} have opened on {second}."
    return f"News from {region_name}: the guns of {first} have opened on our ally {second}."


def _what_is_news(world, region_name: str, a: str, d: str, total_engaged: int) -> Optional[tuple]:
    """`(great, ally)` when a fight between the crowns `a` and `d`, on a
    field the rule did not light for the player, is news; None otherwise —
    the player's own fight, a small fight that is no ally's, or a field he
    sees for himself (the fight's own row tells him all of it)."""
    player = str(getattr(world, "player_nation", "") or "")
    if not player or not a or not d or player in (a, d):
        return None
    great = int(total_engaged or 0) >= int(getattr(world, "GREAT_BATTLE_THRESHOLD", 80000))
    ally = an_allys_in_a_shared_war(world, player, a, d)
    if not (great or ally):
        return None
    from backend.models.intel import FULL
    if world.get_region_intel(region_name).visibility == FULL:
        return None
    return great, ally


def _tell(world, event: dict) -> dict:
    """The news goes on the record and into the morning's dispatch, in the
    same words."""
    world.log_event(event)
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "battle_news", {"line": event["line"]}, "always")
    return event


def of_a_battle(world, region_name: str, attacker, defender, battle_result: dict,
                total_engaged: int, *, road: str = "") -> Optional[dict]:
    """A battle the rule did NOT light for the player: write its news where it
    is news, and return the logged event (None where nothing is written).
    `road` names a road other than the main attack's (a charge, the cavalry's
    own charge, an attack whose guns destroyed the defender): the sentence is
    the same; the row says which road told it."""
    try:
        a = str(getattr(attacker, "nation", "") or "")
        d = str(getattr(defender, "nation", "") or "")
        news = _what_is_news(world, region_name, a, d, total_engaged)
        if news is None:
            return None
        great, ally = news
        verdict = the_days_verdict(battle_result, a, d)
        line = line_of(str(region_name), a, d, verdict, great=great, ally=ally)
        event = {
            "type": "foreign_battle", "location": str(region_name),
            "crowns": [a, d], "verdict": verdict[0], "crown": verdict[1],
            "great": bool(great), "ally": ally, "line": line,
        }
        if road:
            event["road"] = str(road)
        return _tell(world, event)
    except Exception as exc:
        report(exc, "battle_news.of_a_battle")
        return None


def of_an_assault(world, region_name: str, attacker, defender_nation: str, fell: bool,
                  total_engaged: int) -> Optional[dict]:
    """An assault on a garrison the rule did not light for the player —
    `defender_nation` the crown whose works they were BEFORE any capture."""
    try:
        a = str(getattr(attacker, "nation", "") or "")
        d = str(defender_nation or "")
        news = _what_is_news(world, region_name, a, d, total_engaged)
        if news is None:
            return None
        great, ally = news
        line = assault_line(str(region_name), a, d, bool(fell), great=great, ally=ally)
        return _tell(world, {
            "type": "foreign_battle", "kind": "assault", "location": str(region_name),
            "crowns": [a, d], "verdict": "fell" if fell else "walls_held",
            "crown": a if fell else d, "great": bool(great), "ally": ally, "line": line,
        })
    except Exception as exc:
        report(exc, "battle_news.of_an_assault")
        return None


def of_a_cannonade(world, region_name: str, attacker, defender) -> Optional[dict]:
    """A cannonade the rule did not light for the player: news where it is an
    ally's in a shared war (his guns, or the guns turned on him). Never
    "great" — a cannonade has no victor and forces no special."""
    try:
        a = str(getattr(attacker, "nation", "") or "")
        d = str(getattr(defender, "nation", "") or "")
        news = _what_is_news(world, region_name, a, d, 0)
        if news is None:
            return None
        _great, ally = news
        line = cannonade_line(str(region_name), a, d, ally=ally)
        return _tell(world, {
            "type": "foreign_battle", "kind": "cannonade", "location": str(region_name),
            "crowns": [a, d], "verdict": "", "crown": "", "great": False, "ally": ally,
            "line": line,
        })
    except Exception as exc:
        report(exc, "battle_news.of_a_cannonade")
        return None
