"""Row IC, Session 2 (IC-8) — "Give him a task…": the line is never blank.

`docs/INDEPENDENT_COMMAND_SPEC.md` §8.2: "'Give him a task…' on his card opens
the line ALREADY WRITTEN … for a literal man, two or three ready sentences to
take or edit." A task is typed — but nobody has to compose one from nothing:
this module writes, for one of the player's marshals on today's board, a few
ready sentences with REAL names in them. The first fills the command line; the
rest are chips beside it. Each is a sentence the word table reads
(`backend/ai/word_table.py`), and the route checks every one through the
read-back before offering it (`GET /task_presets`), so no chip can teach a
sentence the game refuses.

    a marshal who follows orders to the letter   exact orders: a hold with
                                                 if-thens (his three lines)
    anyone else                                  today's standing orders with
                                                 their parts: a hold for three
                                                 turns, a chase until the
                                                 quarry is destroyed, a hold
                                                 with one if-then, a follow

PURE: reads the board, writes nothing, casts no die. Enemy names come only
from what France can see (`world.get_visible_enemies`, R5).
"""
from __future__ import annotations

from typing import List, Tuple

from backend.display_names import humanize_entity_name

MAX_PRESETS = 4
CHASE_WITHIN = 2      # a quarry to offer stands within two provinces of him


def _safe_ground(world, marshal) -> str:
    """The province he would fall back on — his own nation's, next to him — or ""."""
    try:
        place = world.get_safe_retreat_destination(marshal.name)
    except Exception as exc:
        from backend.errors import report
        report(exc, "task_presets._safe_ground: world.get_safe_retreat_destination")
        return ""
    region = world.get_region(place) if place else None
    if region is None or getattr(region, "controller", None) != marshal.nation:
        return ""
    return str(place)


def _nearest_foe(world, marshal) -> str:
    from backend.commands.task_line import _visible_enemies
    for name in _visible_enemies(world, marshal):
        foe = world.get_marshal(name)
        gap = world.get_distance(marshal.location, getattr(foe, "location", "")) if foe else None
        if isinstance(gap, int) and gap <= CHASE_WITHIN:
            return name
    return ""


def _friend_beside(world, marshal) -> str:
    """One of our own corps in his province or next to it, the strongest first."""
    here = world.get_region(marshal.location)
    near = {marshal.location} | set(getattr(here, "adjacent_regions", ()) or ())
    rows = [(-int(m.strength), m.name) for m in world.get_player_marshals()
            if m.name != marshal.name and int(getattr(m, "strength", 0) or 0) > 0
            and m.location in near]
    return sorted(rows)[0][1] if rows else ""


def build(world, marshal) -> List[Tuple[str, str]]:
    """``[(label, sentence), …]`` for `marshal`, the first the one that fills
    the line. Labels are short plain words for the chips."""
    name = humanize_entity_name(marshal.name)
    here = humanize_entity_name(marshal.location)
    safe = _safe_ground(world, marshal)
    back = humanize_entity_name(safe) if safe else ""
    foe = humanize_entity_name(_nearest_foe(world, marshal))
    friend = humanize_entity_name(_friend_beside(world, marshal))
    rows: List[Tuple[str, str]] = []
    if getattr(marshal, "personality", "") == "literal":
        if back:
            rows.append(("Hold; if outnumbered, fall back",
                         f"{name}, hold {here}. If outnumbered, fall back to {back}."))
            rows.append(("Hold; dig in if attacked, fall back if outnumbered",
                         f"{name}, hold {here}. If attacked, dig in. If outnumbered, "
                         f"fall back to {back}."))
        else:
            rows.append(("Hold; if attacked, dig in", f"{name}, hold {here}. If attacked, dig in."))
        if foe:
            rows.append((f"Hold; attack {foe} if he comes",
                         f"{name}, hold {here}. If {foe} comes within reach, attack."))
        if friend:
            rows.append((f"Hold; join {friend} if he is attacked",
                         f"{name}, hold {here}. If {friend} is attacked next to you, "
                         f"join his battle."))
        return rows[:MAX_PRESETS]
    # Row IC, Session 3 (§6.9): a bold or careful man who may be set on his
    # own offers HIS OWN proposal first — the task he would choose, on his own.
    rows_own: List[Tuple[str, str]] = []
    try:
        from backend.game_logic import own_order as _own
        if not _own.on_his_own(marshal) and not _own.why_not(world, marshal):
            prop = _own.proposal(world, marshal)
            spec = {"task": prop["task"], "target": prop["target"], "area": [prop["target"]]}
            rows_own.append((f"On his own: {_own.task_words(spec)} — his idea", prop["line"]))
    except Exception as exc:
        from backend.errors import report
        report(exc, "task_presets.build: his own proposal")
        rows_own = []
    hold = ("Hold for three turns", f"{name}, hold {here} for 3 turns.")
    watch = ("Hold; if attacked, dig in", f"{name}, hold {here}. If attacked, dig in.")
    chase = (f"Chase {foe}", f"{name}, chase {foe} until he is destroyed.") if foe else None
    follow = (f"Follow {friend}", f"{name}, follow {friend}.") if friend else None
    order = ([hold, watch, follow, chase] if getattr(marshal, "personality", "") == "cautious"
             else [chase, hold, watch, follow])
    return (rows_own + [row for row in order if row is not None])[:MAX_PRESETS]
