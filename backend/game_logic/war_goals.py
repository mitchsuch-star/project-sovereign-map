"""Row IC, directives (IC-6) — THE WAR GOAL (November 19, 2026).

The design's §9 (`docs/INDEPENDENT_COMMAND_SPEC.md`): one thing a war aims at —
a place ("Vienna") or an enemy army ("Mack") — named by the player, free. It
is said on the desk's WAR line, ringed on the map, and (only once one is set)
TO DECIDE offers the march that closes on it as one list. It moves no rule of
the game: nothing is scored, forced or spent by a goal.

NOT the war's PURPOSE. `world.war_objectives` already holds that (conquest,
defence … — a Cabinet act with its articles, `war_status` / `declared_goals`);
this is the army's aim, kept apart in `world.war_goals` — ``{court: {"kind":
"place" | "army", "target": <province or commander>, "turn": n}}`` — written
to a save only when it holds something.

THE RULES
=========
* A place must be held by a court the player is at war with; an army is named
  by its commander, who must serve such a court. A commander's NAME and SIDE
  are public; where he stands is said only where the player can see him.
* ONE goal a war: a new goal for any court fighting in the same war replaces
  the one that war had.
* A goal stands as "taken" once the place is ours (or the army destroyed or
  its commander a prisoner) until another is named; it is dropped when the
  war with its court ends, or when the place is held by a court the player is
  not fighting (`prune`, as the turn begins).

`a_war_has_a_goal` is the seam: down, no goal is read, shown or set.
"""
from __future__ import annotations

import re
import weakref
from typing import Any, Dict, List, Optional, Tuple

from backend.display_names import humanize_entity_name
from backend.errors import report

KINDS = ("place", "army")


def a_war_has_a_goal() -> bool:
    """The seam (row IC, directives). One line to reverse: return False."""
    return True


# ── reading ─────────────────────────────────────────────────────────────────

def _player(world) -> str:
    return str(getattr(world, "player_nation", "") or "")


def store(world) -> Dict[str, Dict[str, Any]]:
    """The goals as saved ({} when none) — never created by a read."""
    held = getattr(world, "war_goals", None)
    return held if isinstance(held, dict) else {}


def _court(world, nation: str) -> str:
    try:
        from backend.game_logic.formations import formed_display_name
        return str(formed_display_name(world, nation))
    except Exception as exc:
        report(exc, "war_goals._court: formations.formed_display_name")
        return humanize_entity_name(nation)


def _at_war(world, nation: str) -> bool:
    try:
        return bool(nation) and bool(world.is_at_war(_player(world), nation))
    except Exception as exc:
        report(exc, "war_goals._at_war: world.is_at_war")
        return False


def _a_fall_the_player_knows(world, target: str, man) -> bool:
    """Whether the player knows this commander has no army left: he took him
    prisoner, or his battle destroyed the corps (the `marshal_destroyed`
    event's victor — the tombstone keeps none)."""
    player = _player(world)
    if man is not None:
        return str(getattr(man, "captured_by", "") or "") == player
    log = getattr(world, "event_log", None) or []
    for event in reversed(log[-4000:]):
        if isinstance(event, dict) and event.get("type") == "marshal_destroyed" \
                and str(event.get("marshal") or "") == target:
            return str(event.get("victor") or "") == player
    return False


def status(world, court: str, goal: Dict[str, Any]) -> str:
    """``"open"`` (still to be won), ``"taken"`` (the place is ours; the army
    is destroyed or its commander a prisoner) or ``"gone"`` (the war with its
    court is over, or the place is held by a court the player is not
    fighting — nothing left to aim at)."""
    kind, target = str(goal.get("kind") or "place"), str(goal.get("target") or "")
    if kind == "army":
        man = world.get_marshal(target)
        if man is None or getattr(man, "captured_by", "") or int(getattr(man, "strength", 0) or 0) <= 0:
            # FOG (the review): a commander's fall is "taken" only where it was the
            # player's own deed — his prisoner, or a corps his battle destroyed
            # (the tombstone's victor). A fall out of his sight leaves the goal as
            # it stood — open, unringed, no march offered — until the war ends:
            # only the man's name and side are public (R5).
            if _a_fall_the_player_knows(world, target, man):
                return "taken"
            return "open" if _at_war(world, court) else "gone"
        return "open" if _at_war(world, str(getattr(man, "nation", "") or "")) else "gone"
    region = world.get_region(target)
    if region is None:
        return "gone"
    holder = str(getattr(region, "controller", "") or "")
    if holder == _player(world):
        return "taken" if _at_war(world, court) else "gone"
    return "open" if _at_war(world, holder) else "gone"


def target_shown(world, goal: Dict[str, Any]) -> str:
    """The goal in a sentence: "Vienna", "Mack's army"."""
    shown = humanize_entity_name(str(goal.get("target") or ""))
    return f"{shown}'s army" if str(goal.get("kind")) == "army" else shown


def words(world, court: str, goal: Dict[str, Any]) -> str:
    """The goal as THE WAR line says it: "your war goal: Vienna", "your war
    goal: Vienna (taken)", "your war goal: Mack's army (destroyed)". "Your"
    since the directives' blind reading 2: "to hold the homeland — goal:
    Vienna" read as one aim mixing defence and attack; the war's purpose is the
    war's, the goal the player's own."""
    state = status(world, court, goal)
    said = f"your war goal: {target_shown(world, goal)}"
    if state == "taken":
        said += " (destroyed)" if str(goal.get("kind")) == "army" else " (taken)"
    return said


def _courts_of(war_row: Dict[str, Any]) -> List[str]:
    """Every court fighting in a war row (a shared war names them all)."""
    courts = [str(c) for c in (war_row.get("opponents") or []) if c]
    lead = str(war_row.get("opponent") or "")
    if lead and lead not in courts:
        courts.insert(0, lead)
    return courts


def goal_of(world, war_row: Dict[str, Any]) -> Optional[Tuple[str, Dict[str, Any]]]:
    """``(court, goal)`` for the goal this war carries — None when it has
    none, when the seam is down, or when the goal has nothing left to aim at."""
    if not a_war_has_a_goal():
        return None
    held = store(world)
    if not held:
        return None
    for court in _courts_of(war_row):
        goal = held.get(court)
        if isinstance(goal, dict) and goal.get("target") and status(world, court, goal) != "gone":
            return court, goal
    return None


def _ring(world, goal: Dict[str, Any]) -> str:
    """The province the map rings: the place itself; an army's province only
    where the player can SEE him (the fog keeps a man's place — R5)."""
    if str(goal.get("kind")) == "army":
        man = world.get_marshal(str(goal.get("target") or ""))
        try:
            from backend.game_logic.intel_surfaces import in_sight
            if man is not None and in_sight(world, _player(world), man):
                return str(man.location)
        except Exception as exc:
            report(exc, "war_goals._ring: intel_surfaces.in_sight")
        return ""
    return str(goal.get("target") or "")


def ringed(world, court: str, goal: Dict[str, Any]) -> bool:
    """Whether the map rings this goal now: an open goal whose province the
    player may see (`payload`'s own `region` rule)."""
    return status(world, court, goal) == "open" and _ring(world, goal) != ""


def payload(world, wars: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """What the desk carries for the map and the war popup: one row a war that
    has a goal — ``{war, court, kind, target, shown, status, region, line}``
    (`region` is "" where the fog keeps the place). [] when none is set."""
    if not a_war_has_a_goal() or not store(world):
        return []
    out: List[Dict[str, Any]] = []
    for row in (wars or {}).get("wars") or []:
        if not isinstance(row, dict) or row.get("status") != "war":
            continue
        found = goal_of(world, row)
        if found is None:
            continue
        court, goal = found
        state = status(world, court, goal)
        out.append({
            "war": str(row.get("opponent") or ""), "court": court,
            "kind": str(goal.get("kind") or "place"), "target": str(goal.get("target") or ""),
            "shown": target_shown(world, goal), "status": state,
            "region": _ring(world, goal) if state == "open" else "",
            "line": words(world, court, goal),
        })
    return out


# ── who can march on it ─────────────────────────────────────────────────────

# Rule 8 (the review): the desk asks this on EVERY reply while a goal is set,
# and a place goal plots a road for each idle corps. The answer is kept for the
# state it was read on — the turn, the pools, the goal and each candidate's
# place and strength — so a reply that changed none of them reads it back.
_MARCHERS_CACHE: Dict[tuple, tuple] = {}   # key -> (names, order, weakref to the world)
_MARCHERS_CACHE_CAP = 32


def _marchers_key(world, goal: Dict[str, Any], candidates: List[Any]) -> tuple:
    foe = world.get_marshal(str(goal.get("target") or "")) if str(goal.get("kind")) == "army" else None
    return (id(world), int(getattr(world, "current_turn", 0) or 0),
            # an army goal's man: where he stands, whether he still has an army
            (str(getattr(foe, "location", "")), int(getattr(foe, "strength", 0) or 0),
             str(getattr(foe, "captured_by", "") or "")) if foe is not None else None,
            int(getattr(world, "actions_remaining", 0) or 0),
            int(getattr(world, "admin_actions_remaining", 0) or 0),
            int(getattr(world, "diplomatic_points", 0) or 0),
            str(goal.get("kind") or "place"), str(goal.get("target") or ""),
            tuple((str(m.name), str(getattr(m, "location", "")), int(getattr(m, "strength", 0) or 0))
                  for m in candidates))


def marchers(world, goal: Dict[str, Any], candidates: List[Any]) -> Tuple[List[str], str]:
    """``(names, order)`` — which of `candidates` (corps with no orders) can
    be sent at the goal today, and the order's words ("march to Vienna",
    "pursue Mack"). A place: every corps whose march there the road law
    takes and whose state allows a standing order; an army: only where the
    staff knows his position (`strategic.pursue_known_location` — the
    player's own knowledge, never the truth). ([], "") when nobody can.
    Kept for the state it was read on (`_MARCHERS_CACHE` — Rule 8)."""
    key = _marchers_key(world, goal, candidates)
    hit = _MARCHERS_CACHE.get(key)
    if hit is not None and hit[2]() is world:      # the same world, not one born at its address
        return list(hit[0]), hit[1]
    names, order = _marchers_read(world, goal, candidates)
    try:
        ref = weakref.ref(world)
    except TypeError:
        return names, order
    if len(_MARCHERS_CACHE) >= _MARCHERS_CACHE_CAP:
        _MARCHERS_CACHE.clear()
    _MARCHERS_CACHE[key] = (list(names), order, ref)
    return names, order


def _marchers_read(world, goal: Dict[str, Any], candidates: List[Any]) -> Tuple[List[str], str]:
    from backend.commands.state_probe import order_state_refusal
    kind, target = str(goal.get("kind") or "place"), str(goal.get("target") or "")
    names: List[str] = []
    try:
        if kind == "army":
            foe = world.get_marshal(target)
            if foe is None:
                return [], ""
            from backend.commands.strategic import pursue_known_location
            for m in candidates:
                if order_state_refusal(world, m, "pursue"):
                    continue
                if pursue_known_location(world, m, foe):
                    names.append(m.name)
            return names, (f"pursue {humanize_entity_name(target)}" if names else "")
        if world.get_region(target) is None:
            return [], ""
        from backend.commands import order_quotes as Q
        memo: dict = {}
        for m in candidates:
            if str(m.location) == target or order_state_refusal(world, m, "march"):
                continue
            road, refusal, _kind = Q._road(world, m, target, "MOVE_TO", memo)
            if refusal is None and road:
                names.append(m.name)
        return names, (f"march to {target}" if names else "")
    except Exception as exc:
        report(exc, "war_goals.marchers")
        return [], ""


# ── the typed line ──────────────────────────────────────────────────────────

_SET_RES = (
    re.compile(r"^\s*(?:please\s+)?(?:set|make|name|declare|fix)\s+(?:the\s+|our\s+|my\s+)?war\s+goal"
               r"\s*(?:to\b|as\b|is\b|at\b|:|=)?\s*(?P<what>\S.*?)\s*[.!]*\s*$", re.IGNORECASE),
    re.compile(r"^\s*(?:the\s+|our\s+|my\s+)?war\s+goal\s*(?:is|shall\s+be|will\s+be|:|=)\s*"
               r"(?P<what>\S.*?)\s*[.!]*\s*$", re.IGNORECASE),
    re.compile(r"^\s*(?:please\s+)?(?:make|name|set|declare)\s+(?P<what>\S.*?)\s+(?:the|our|my)\s+war\s+goal"
               r"\s*[.!]*\s*$", re.IGNORECASE),
    re.compile(r"^\s*(?:the\s+|our\s+)?goal\s+of\s+(?:the|this|our)\s+war\s+(?:is|shall\s+be|will\s+be|:)\s*"
               r"(?P<what>\S.*?)\s*[.!]*\s*$", re.IGNORECASE),
)
_CLEAR_RE = re.compile(
    r"^\s*(?:please\s+)?(?:(?:clear|drop|remove|unset|forget|cancel|abandon|end|withdraw)\s+"
    r"(?:the\s+|our\s+|my\s+)?war\s+goal|no\s+(?:more\s+)?war\s+goal)"
    r"(?:\s+(?:against|with|for|on)\s+(?P<court>\S.*?))?\s*[.!]*\s*$", re.IGNORECASE)
_NOTHING = re.compile(r"^(?:none|nothing|no\s+goal|not\s+set|unset|cleared?)$", re.IGNORECASE)


def read_order(text: str) -> Optional[Dict[str, str]]:
    """``{"op": "set", "what": …}`` / ``{"op": "clear", "court": …}`` when the
    line is the war goal's ("the war goal is Vienna", "make Mack the war
    goal", "clear the war goal"), else None. PURE — words only; a line that
    ends in a question mark is a question, never this."""
    text = str(text or "")
    if not text.strip() or text.strip().endswith("?"):
        return None
    cleared = _CLEAR_RE.match(text)
    if cleared:
        return {"op": "clear", "court": (cleared.group("court") or "").strip()}
    for pattern in _SET_RES:
        match = pattern.match(text)
        if match:
            what = match.group("what").strip().strip("\"“”'‘’")
            if _NOTHING.match(what):
                return {"op": "clear", "court": ""}
            return {"op": "set", "what": what}
    return None


def _resolve(world, what: str) -> Tuple[str, str]:
    """``(kind, name)`` for what the player named — a province, or a foreign
    commander ("Mack", "Mack's army", "the army of Mack") — or ("", "")."""
    said = str(what or "").strip()
    said = re.sub(r"^(?:the\s+)?(?:city|town|fortress|province|capital)\s+of\s+", "", said, flags=re.I)
    said = re.sub(r"^(?:to\s+take|to\s+destroy|take|destroy|capture)\s+", "", said, flags=re.I)
    army = re.match(r"^(?:the\s+)?army\s+of\s+(?P<who>.+)$", said, re.I) \
        or re.match(r"^(?P<who>.+?)['’]s?\s+(?:army|corps|force)$", said, re.I)
    if army:
        said = army.group("who").strip()
    said = re.sub(r"^the\s+", "", said, flags=re.I)
    low = said.casefold()
    if not army:
        for region_name in (getattr(world, "regions", None) or {}):
            if low in (str(region_name).casefold(), humanize_entity_name(str(region_name)).casefold()):
                return "place", str(region_name)
    player = _player(world)
    for name, man in (getattr(world, "marshals", None) or {}).items():
        if getattr(man, "nation", None) == player:
            continue
        if low in (str(name).casefold(), humanize_entity_name(str(name)).casefold()):
            return "army", str(name)
    return "", ""


def _same_war(world, court: str) -> List[str]:
    """The courts fighting in the same war as `court` (itself included)."""
    try:
        from backend.game_logic.war_status import build_active_wars
        for row in build_active_wars(world).get("wars") or []:
            if isinstance(row, dict) and row.get("status") == "war" and court in _courts_of(row):
                return _courts_of(row)
    except Exception as exc:
        report(exc, "war_goals._same_war: war_status.build_active_wars")
    return [court]


def aim(world, what: str) -> Tuple[str, str, str, str]:
    """``(kind, name, court, refusal)`` for what the player named as a goal:
    a place a court at war with us holds, or an enemy army by its commander.
    `refusal` is the plain sentence when it cannot be a goal ("" when it can)
    — ONE predicate: the order itself and the read-back both ask it. PURE."""
    kind, name = _resolve(world, what)
    if not kind:
        hint = ""
        try:
            from backend.commands.proper_name import near_province
            near = near_province(world, what)
            if near:
                hint = f" Did you mean {near}?"
        except Exception as exc:
            report(exc, "war_goals.aim: proper_name.near_province")
        return "", "", "", (
            f"I know no province or enemy commander called “{str(what).strip()}”, Sire.{hint} "
            "A war goal is a place a court you are fighting holds, or one of its armies by its "
            "commander's name.")
    player = _player(world)
    if kind == "place":
        region = world.get_region(name)
        holder = str(getattr(region, "controller", "") or "")
        if holder == player:
            return kind, name, "", (f"{humanize_entity_name(name)} is yours already, Sire — a war "
                                    "goal is a place a court you are fighting holds.")
        if not _at_war(world, holder):
            who = _court(world, holder) if holder else "no court"
            return kind, name, "", (
                f"{humanize_entity_name(name)} is held by {who}, and you are not at war with "
                f"{'it' if holder else 'anyone there'} — a war goal is a place a court you are "
                "fighting holds.")
        return kind, name, holder, ""
    man = world.get_marshal(name)
    court = str(getattr(man, "nation", "") or "")
    if not _at_war(world, court):
        return kind, name, "", (
            f"{humanize_entity_name(name)} serves {_court(world, court)}, and you are not at war "
            "with it — a war goal is an army of a court you are fighting.")
    if (getattr(man, "captured_by", "") or int(getattr(man, "strength", 0) or 0) <= 0) \
            and _a_fall_the_player_knows(world, name, man):
        # (FOG, the review) said only of a fall the player knows — his own prisoner
        return kind, name, "", f"{humanize_entity_name(name)} has no army left to aim at, Sire."
    return kind, name, court, ""


def _cap(said: str) -> str:
    return said[:1].upper() + said[1:]


def _war_named(world, court: str) -> str:
    """The war a court fights us in, as the war panel names it ("the war with
    the Third Coalition"), else by the court ("the war with Austria") — the
    directives' blind reading 3: the reply named "the war with Austria" while
    the panel beside it said "War with the Third Coalition"."""
    try:
        from backend.game_logic.war_status import build_active_wars
        for row in (build_active_wars(world) or {}).get("wars") or []:
            if isinstance(row, dict) and row.get("status") == "war" and court in _courts_of(row):
                title = str(row.get("war_title") or "").strip()
                if title.lower().startswith("war with "):
                    return "the war with " + title[len("war with "):]
    except Exception as exc:
        report(exc, "war_goals._war_named: war_status.build_active_wars")
    return f"the war with {_court(world, court)}"


def set_goal(world, what: str) -> Dict[str, Any]:
    """Name the goal of a war: a place a court at war with us holds, or an
    enemy army by its commander. Returns {success, message, court, goal}."""
    if not a_war_has_a_goal():
        return {"success": False, "message": "War goals are not kept in this game."}
    kind, name, court, refusal = aim(world, what)
    if refusal:
        return {"success": False, "message": refusal}
    if not isinstance(getattr(world, "war_goals", None), dict):
        world.war_goals = {}
    replaced = ""
    for other in _same_war(world, court):
        old = world.war_goals.pop(other, None)
        if isinstance(old, dict) and old.get("target") and not replaced:
            if (str(old.get("kind")), str(old.get("target"))) != (kind, name):
                replaced = target_shown(world, old)
    goal = {"kind": kind, "target": name, "turn": int(getattr(world, "current_turn", 0) or 0)}
    world.war_goals[court] = goal
    # (the review: "the map rings it" was said of an enemy army the fog hides —
    # his place is never drawn until he is in sight)
    rung = (" The desk names it and the map rings it." if ringed(world, court, goal)
            else " The desk names it; the map will ring his army once he is in sight.")
    message = (f"The goal of {_war_named(world, court)} is now {target_shown(world, goal)}."
               + (f" (It was {replaced}.)" if replaced else "") + rung)
    return {"success": True, "message": message, "court": court, "goal": dict(goal)}


def clear_goal(world, court_said: str = "") -> Dict[str, Any]:
    """Drop a war's goal — the one named by its court, or the only one."""
    held = getattr(world, "war_goals", None)
    if not isinstance(held, dict) or not held:
        return {"success": False, "message": "No war goal is set, Sire."}
    want = str(court_said or "").strip().casefold()
    want = re.sub(r"^the\s+", "", want)
    picks = list(held)
    if want:
        picks = [c for c in held if want in (str(c).casefold(), _court(world, c).casefold(),
                                             humanize_entity_name(str(c)).casefold())]
        if not picks:
            # a court of the same war names that war's goal
            for c in held:
                if any(want in (str(o).casefold(), _court(world, o).casefold())
                       for o in _same_war(world, c)):
                    picks = [c]
                    break
        if not picks:
            return {"success": False,
                    "message": f"No war goal is set against “{court_said.strip()}”, Sire."}
    elif len(picks) > 1:
        said = "; ".join(f"{target_shown(world, held[c])} ({_war_named(world, c)})" for c in picks)
        return {"success": False,
                "message": f"Which goal, Sire? {said}. Say “clear the war goal against <court>”."}
    court = picks[0]
    goal = held.pop(court)
    return {"success": True, "court": court, "goal": dict(goal),
            "message": f"{_cap(_war_named(world, court))} has no goal now "
                       f"(it was {target_shown(world, goal)})."}


def prune(world) -> List[str]:
    """Drop every goal with nothing left to aim at (the war with its court is
    over; the place is held by a court the player is not fighting). Returns
    what to say of it; [] — and nothing written — when no goal is kept or
    nothing changed."""
    held = getattr(world, "war_goals", None)
    if not isinstance(held, dict) or not held:
        return []
    said: List[str] = []
    for court in list(held):
        goal = held.get(court) or {}
        if status(world, court, goal) == "gone":
            del held[court]
            said.append(f"The war goal {target_shown(world, goal)} is dropped — "
                        f"{_war_named(world, court)} no longer reaches it.")
    return said
