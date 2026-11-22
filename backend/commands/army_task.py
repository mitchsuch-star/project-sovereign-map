"""Row IC, Session 3b (IC-12) — AN ARMY'S TASK, and the list of a changed war goal.

`docs/INDEPENDENT_COMMAND_SPEC.md` §9, §9.1, §15 ("Session 3b"); the rules
`docs/SYSTEMS_REFERENCE.md` §234. The user's words (November 20, 2026): "if
army has differner personalities they arent all doing same thing every turn" —
and his direction for every man set on his own: they "really do stuff", work
with each other, "help their friends"; the order is guidance.

WHAT IT IS. A named army (`backend/game_logic/armies.py`) given a TASK — "Army
of Italy, take Swabia", "…, chase Mack", "…, hold Milan", "…, take the war
goal" — is two marshals as one force, writ large, and no new rule:

    its COMMANDER   is set ON HIS OWN with the task (`own_order` — his own
                    typed line, "Masséna, take Swabia on your own"): the man
                    you named, else the highest-ranked of its men who may be
                    set on his own;
    EVERY OTHER MAN is set to FOLLOW him — today's standing support that
                    stays (`standing_follow`), 1 action, not counted against
                    "on their own";
    A MAN LEFT OUT  is said, with why: already on his own (he keeps his own
                    task), on his task to prove himself, cannot reach him.

ONE LIST (the user's ruling "One list for all"): the task rides the directive
card (`backend/commands/directive.py`) — each row is the read-back's own
reading of that man's OWN line (`parse_preview.read_one`), so the list, the
read-back and the price cannot drift; Give sends the ticked rows as one order
and one Take-back unit, commander first, each line through the ordinary parser
and executor (golden rule 5).

THE ARMY MOVES AS ONE. A follower of an army's commander is not ticked by the
standing-order pass (it runs after the enemy has moved, and a bold man's
standing order is dropped for any battle within two provinces — his own
commander's too). He moves in THE PASS (`own_order.the_pass`), right after his
commander and before the enemy: "Tonight" is shown for him and is what he does,
or he stays put and says why (D8); he starts no attack of his own, and he is
not drawn off by distant cannon fire. He still reaches the commander's battles
by the game's own arrival roll, which favours a man under a support order.
`following` is the ONE test, derived — never stored.

A CHANGED WAR GOAL is a list too (§9): every man serving the goal is turned,
1 action each, said before Give; a man left unticked keeps his old target and
serves the goal no longer.

PURE where it reads: `read`, `build`, `rows`, `follower_reading`, `tonight`
write nothing and cast no die. `an_army_takes_a_task` is the seam.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from backend.ai import task_words as _tw
from backend.display_names import humanize_entity_name
from backend.errors import report


def an_army_takes_a_task() -> bool:
    """The seam (row IC, Session 3b). One line to reverse: return False — an
    army's "take Swabia" is then its first man's one battle, as it was."""
    return True


_STANDING = object()      # "read the order the marshal holds now"


def _shown(name) -> str:
    return humanize_entity_name(str(name or ""))


def _names(listed: List[str]) -> str:
    listed = [_shown(n) for n in listed if n]
    if not listed:
        return ""
    if len(listed) == 1:
        return listed[0]
    return ", ".join(listed[:-1]) + " and " + listed[-1]


def _plural(n: int, word: str) -> str:
    if word == "man":
        return f"{int(n)} {'man' if int(n) == 1 else 'men'}"
    return f"{int(n)} {word}{'' if int(n) == 1 else 's'}"


# ═══════════════════════════ the words (pure) ═══════════════════════════════

# "Army of Italy under Ney, take Swabia" — who commands, named in the line.
_UNDER_RE = re.compile(
    r"^\s*(?:under|led\s+by|commanded\s+by)\s+(?:marshal\s+|general\s+)?"
    r"(?P<who>[A-Za-zÀ-ÿ'’\-]+(?:\s+[A-Za-zÀ-ÿ'’\-]+)?)\s*[,:;—-]\s*(?P<rest>\S.*)$",
    re.IGNORECASE)
# THE WORDS are the word table's (`backend/ai/word_table.py` → the generated
# `task_words.py`; after changing the table: `python -m tools.gen_task_words`).


def _alt(phrases) -> str:
    return "|".join(re.escape(p).replace(r"\ ", r"\s+") for p in sorted(phrases, key=len, reverse=True))


# The plain order to every corps, asked for by name ("…, hold Milan by exact
# orders"): the mark is set aside and the line is today's directive.
_EXACT_RE = re.compile(r"[\s,;]*\b(?:" + _alt(_tw.ARMY_EXACT) + r")\b[\s,;]*", re.IGNORECASE)
# What an army is told of ITSELF, said to its commander as he hears it.
_ARMY_MARKS = tuple((re.compile(r"\b" + _alt([said]) + r"\b", re.IGNORECASE), means)
                    for said, means in _tw.ARMY_MARKS)
_LEAD = r"^\s*(?:please\s+)?(?:now\s+)?"
# The task verbs (each read to its task by the built-in reader — the census in
# `tests/test_ic12_an_armys_task.py` runs every one). "attack" is NOT among
# them: an army's attack is one battle today, its first man's, as it was.
TAKE_VERBS = tuple(_tw.ARMY_TASK["take"])
CHASE_VERBS = tuple(_tw.ARMY_TASK["chase"])
HOLD_VERBS = tuple(_tw.ARMY_TASK["hold"])
# …and the verbs that are a task only when the line says so (a mark of
# judgement or a how-bold word): "Army of Italy, march on Swabia as it sees fit".
MARKED_VERBS = tuple(_tw.ARMY_TASK["marked"])
_GOAL_OBJECT_RE = re.compile(r"^(?:" + _alt(_tw.GOAL_OBJECTS) + r")(?![A-Za-zÀ-ÿ])", re.IGNORECASE)


def _verb_re(verbs) -> "re.Pattern":
    return re.compile(_LEAD + r"(?P<verb>" + _alt(verbs) + r")\s+(?P<obj>\S.*)$", re.IGNORECASE)


_TAKE_RE, _CHASE_RE, _HOLD_RE, _MARKED_RE = (
    _verb_re(TAKE_VERBS), _verb_re(CHASE_VERBS), _verb_re(HOLD_VERBS), _verb_re(MARKED_VERBS))


def without_exact(rest: str) -> Tuple[str, bool]:
    """`(the order's words without "by exact orders", whether it was said)`."""
    if not _EXACT_RE.search(rest or ""):
        return str(rest or ""), False
    cleaned = _EXACT_RE.sub(" ", rest)
    return re.sub(r"\s+([.!?])", r"\1", re.sub(r"\s{2,}", " ", cleaned)).strip(), True


def _leads_with(obj: str, names) -> str:
    """The name of `names` that `obj` opens with (the longest), or ""."""
    text = re.sub(r"^(?:the\s+)?(?:(?:city|town|fortress|province|army)\s+of\s+)?", "", obj.strip(),
                  flags=re.IGNORECASE)
    for name in sorted({str(n) for n in names if n}, key=len, reverse=True):
        for form in {name, _shown(name)}:
            if re.match(re.escape(form) + r"(?![A-Za-zÀ-ÿ])", text, re.IGNORECASE):
                return name
    return ""


def _marked(rest: str) -> bool:
    """A mark of judgement, or a how-bold word, rides the line."""
    try:
        from backend.ai import own_words, task_words
        _clean, marks = own_words.set_aside_marks(as_his(rest))
        if marks:
            return True
        low = " " + re.sub(r"[^a-z' ]+", " ", str(rest or "").lower()) + " "
        return any(f" {w} " in low for w in tuple(task_words.BOLDER_WORDS) + tuple(task_words.CAREFUL_WORDS))
    except Exception as exc:
        report(exc, "army_task._marked")
        return False


def as_his(rest: str) -> str:
    """The army's words as its commander hears them ("on its own" → "on your own")."""
    text = str(rest or "")
    for pattern, his in _ARMY_MARKS:
        text = pattern.sub(his, text)
    return text


def read(world, army: str, rest: str) -> Optional[Dict[str, Any]]:
    """Whether the words an army is given are a TASK — ``{"kind": take | pursue
    | hold, "rest": the task's words, "under": the commander named in the line
    (or ""), "goal": whether it is the war goal's}`` — else None (today's
    order to each corps, or its first man's one battle). PURE — words and names
    only; the build reads the board."""
    if not an_army_takes_a_task() or world is None or not str(rest or "").strip():
        return None
    text = str(rest).strip()
    under = ""
    named = _UNDER_RE.match(text)
    if named:
        under, text = named.group("who").strip(), named.group("rest").strip()
    text, exact = without_exact(text)
    if exact:
        return None
    places = list(getattr(world, "regions", None) or {})
    player = getattr(world, "player_nation", None)
    foes = [n for n, m in (getattr(world, "marshals", None) or {}).items()
            if getattr(m, "nation", None) != player]
    kind, goal = "", False
    for pattern, task in ((_TAKE_RE, "take"), (_CHASE_RE, "pursue"), (_HOLD_RE, "hold")):
        hit = pattern.match(text)
        if not hit:
            continue
        obj = hit.group("obj")
        if task != "hold" and _GOAL_OBJECT_RE.match(obj.strip()):
            kind, goal = task, True
        elif task in ("take", "hold") and _leads_with(obj, places):
            kind = task
        elif task == "pursue" and _leads_with(obj, foes):
            kind = task
        break
    if not kind and _marked(text):
        hit = _MARKED_RE.match(text)
        if hit and (_leads_with(hit.group("obj"), places) or _GOAL_OBJECT_RE.match(hit.group("obj").strip())):
            kind, goal = "take", bool(_GOAL_OBJECT_RE.match(hit.group("obj").strip()))
    if not kind:
        return None
    return {"kind": kind, "rest": text, "under": under, "goal": goal, "army": str(army)}


def lead_line(lead: str, rest: str) -> str:
    """The commander's own typed line: the army's task, said to him — "Massena,
    take Swabia on your own" (the mark goes in where the task's words end)."""
    words = as_his(rest).strip()
    try:
        from backend.ai import own_words
        _clean, marks = own_words.set_aside_marks(words)
    except Exception as exc:
        report(exc, "army_task.lead_line")
        marks = []
    if not marks:
        stop = re.search(r"[.!;]", words)
        at = stop.start() if stop else len(words)
        words = words[:at].rstrip() + " on your own" + words[at:]
    return f"{lead}, {words}"


def follow_line(name: str, lead: str) -> str:
    return f"{name}, follow {lead}"


def canonical(army: str, task: Dict[str, Any]) -> str:
    """The line the list sends back with its ticks — read again to the same task."""
    under = f" under {task['under_name']}" if task.get("under_name") else ""
    return f"{army}{under}, {task['rest']}"


# ═══════════════════════════ who commands ═══════════════════════════════════

def _own():
    from backend.game_logic import own_order
    return own_order


def _in_rank(world, names: List[str]) -> List[str]:
    try:
        from backend.game_logic import precedence
        order = [m.name for m in precedence.order_of_precedence(world, world.player_nation)]
    except Exception as exc:
        report(exc, "army_task._in_rank")
        order = []
    seat = {n: i for i, n in enumerate(order)}
    return sorted(names, key=lambda n: (seat.get(n, len(seat)), n))


def may_command(world, marshal, kind: str) -> str:
    """Why this man cannot be the one set on his own for the army's task — ""
    when he can (the count aside: a full count is said on his row, with the
    stand-down that frees a place)."""
    own = _own()
    return own.why_not(world, marshal, kind, replacing=True)


def commander(world, army: str, kind: str, under: str = "") -> Dict[str, Any]:
    """Who commands the army's task and why: ``{"lead", "why", "named",
    "passed": [(name, why)], "next": [names], "refusal"}``. The man named in
    the line; else the man named for the army; else the highest-ranked of its
    men in the field who may be set on his own. `refusal`: the line named a
    man who is not of this army. PURE."""
    from backend.game_logic import armies
    own = _own()
    field = list(armies.field_members(world, army))
    out: Dict[str, Any] = {"lead": "", "why": "", "named": "", "passed": [], "next": [], "refusal": ""}
    ranked = _in_rank(world, field)
    able = [n for n in ranked
            if not own.on_his_own(world.get_marshal(n)) and not may_command(world, world.get_marshal(n), kind)]
    if under:
        good, _bad = armies._resolve(world, [under])
        if not good or good[0] not in field:
            who = _shown(good[0]) if good else under
            out["refusal"] = (f"{who} is not one of the {army}'s corps in the field — it holds "
                              f"{_names(field) or 'nobody'}. Name one of them to command it.")
            return out
        out.update(lead=good[0], named=good[0], why="you named him for this task")
    else:
        at_its_head = str(task_of(world, army).get("lead") or "")
        kept = armies.commander(world, army)
        if at_its_head and at_its_head in field:
            # the army has a task already: the man at its head stays there (the
            # line changes his task, or adds the men who do not follow him yet)
            out.update(lead=at_its_head, why="he commands it on its own already")
        elif kept and kept in field:
            out.update(lead=kept, named=kept, why="you named him to command the army")
        elif able:
            out.update(lead=able[0], why="the highest-ranked of its men who can be set on his own")
            for name in ranked:
                if name == able[0]:
                    break
                man = world.get_marshal(name)
                why = ("is on his own already" if own.on_his_own(man) else may_command(world, man, kind))
                out["passed"].append((name, _passed_words(name, why)))
    out["next"] = [n for n in able if n != out["lead"]]
    return out


def _passed_words(name: str, why: str) -> str:
    """Why a higher man does not command, in one clause ("follows orders to the letter")."""
    shown = _shown(name)
    said = str(why or "").strip()
    for lead in (shown + " ", shown + "'s "):
        if said.startswith(lead):
            said = ("his " if lead.endswith("'s ") else "") + said[len(lead):]
            break
    return said.split(" — ")[0].rstrip(".") or "cannot be set on his own"


def _so(why: str) -> str:
    """A passed-over senior's reason as the commander's row says it (read
    blind, round 1: "Soult outranks him but follows orders to the letter" —
    "why can't Soult command?"): what bars him, in the game's own word for it
    (an exact order is the only kind such a man takes)."""
    said = str(why or "")
    return "takes only exact orders" if said == "follows orders to the letter" else said


# ═══════════════════════════ the build (pure) ═══════════════════════════════

def build(world, address: Dict[str, Any], command_text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    """The army's task as the fan-out will run it — ``("stash", stash)`` — or
    the free answer in its place — ``("result", …)``. `address` is
    `directive.address`'s reading (kind `army`, with its `task`). PURE."""
    from backend.game_logic import armies, trial
    own = _own()
    task = dict(address.get("task") or {})
    army = str(address.get("army") or "")
    field = list(armies.field_members(world, army))
    if not field:
        return ("result", {"success": False, "variable_action_cost": 0,
                           "message": f"The {army} has no corps in the field to take an order, Sire — nothing spent."})
    who = commander(world, army, task["kind"], task.get("under") or "")
    if who["refusal"]:
        return ("result", {"success": False, "variable_action_cost": 0,
                           "message": f"{who['refusal']} Nothing was spent."})
    lead = who["lead"]
    task["under_name"] = lead if task.get("under") else ""
    left: Dict[str, str] = {}
    lines: Dict[str, str] = {}
    verbs: Dict[str, str] = {}
    members: List[str] = []
    lead_man = world.get_marshal(lead) if lead else None
    if lead:
        members.append(lead)
        lines[lead] = lead_line(lead, task["rest"])
        verbs[lead] = ""          # his own road reads everything about him (`own_order.why_not`)
    for name in field:
        if name == lead:
            continue
        man = world.get_marshal(name)
        if not lead:
            left[name] = _passed_words(name, ("is on his own already" if own.on_his_own(man)
                                              else may_command(world, man, task["kind"])))
            continue
        if own.on_his_own(man):
            held = own.own(man) or {}
            if str(held.get("army") or "") == army:
                # (the review, IC3B-V7) a NEW commander was named over the man at
                # its head: the list says what becomes of him before Give
                left[name] = (f"on his own: {own.task_words(held)} — he keeps that task as his own, "
                              f"and commands the {army} no longer")
            else:
                left[name] = f"on his own: {own.task_words(held)} — not included"
            continue
        if trial.on_trial(man):
            left[name] = "on his task to prove himself — he takes no orders"
            continue
        if following(world, man) is lead_man and lead_man is not None:
            left[name] = f"follows {_shown(lead)} already"
            continue
        members.append(name)
        lines[name] = follow_line(name, lead)
        verbs[name] = "follow"
    stash: Dict[str, Any] = {
        "rest": task["rest"], "action": "own_task", "strategic_type": None,
        "target": "", "members": list(members),
        "turn": int(getattr(world, "current_turn", 0) or 0),
        "army": False, "band": None, "note": "", "lines": [], "events": [],
        "raw": command_text, "at": "",
        "kind": "army", "addressed": list(members) + [n for n in field if n in left],
        "who": list(members), "army_name": army, "click": False,
        "lines_by": lines, "verbs_by": verbs, "always_list": True, "own_lines": True,
        "task": {**task, "army": army, "lead": lead, "why_lead": who["why"],
                 "passed": list(who["passed"]), "next": list(who["next"]), "left": left},
    }
    return ("stash", stash)


def price_of(world, marshal, stash: Dict[str, Any]) -> int:
    """What this man's row costs, read where his own order reads it."""
    own = _own()
    task = stash.get("task") or {}
    goal = stash.get("goal") or {}
    try:
        if goal or marshal.name == task.get("lead"):
            if own.on_his_own(marshal):
                return int(own.CHANGE_PRICE)
            kind = str(task.get("kind") or goal.get("task") or "take")
            return int(own.PRICE.get(kind, 2))
        return int(marshal.strategic_order_ap(order_type="SUPPORT"))
    except Exception as exc:
        report(exc, "army_task.price_of")
        return 1


# ═══════════════════════════ the list's rows ════════════════════════════════

_ABILITY_WORDS = {
    "Roland of the Army": "he is quick to the guns",
    "Eyes on a Crown": "he is slow to another man's battle",
}


def _arrival(world, lead, man) -> Tuple[int, int]:
    """`(his chance to reach a battle beside the commander under this order,
    the same without it)` in whole percent — the arrival roll's own figures
    (`combat_executor._arrival_odds_row`: shown = applied), (0, 0) unread."""
    try:
        from backend.commands import order_quotes as _q
        reader = _q._MUSTER_READER.get("combat")
        if reader is None:
            from backend.commands.executor import CommandExecutor
            reader = _q._MUSTER_READER["combat"] = CommandExecutor()._combat
        row = reader._arrival_odds_row(lead, man, str(lead.location or ""), world, "has_support_order")
        return int(row.get("arrival_odds_with_support", 0) or 0), int(row.get("arrival_odds", 0) or 0)
    except Exception as exc:
        report(exc, "army_task._arrival")
        return 0, 0


def his_part(world, lead, man) -> str:
    """A follower's own part, as the game already decides it (§9.1)."""
    lead_shown = _shown(lead.name)
    with_order, without = _arrival(world, lead, man)
    ability = str((getattr(man, "ability", None) or {}).get("name") or "") \
        if isinstance(getattr(man, "ability", None), dict) else str(getattr(getattr(man, "ability", None), "name", "") or "")
    tag = _ABILITY_WORDS.get(ability, "")
    if str(getattr(man, "personality", "") or "") == "literal":
        head = (f"To the letter: marches where {lead_shown} marches, and this order is his "
                f"written word to join {lead_shown}'s battles next to him")
    else:
        head = (f"Moves with {lead_shown} each night, before the enemy does, and may join "
                f"{lead_shown}'s battles next to him")
    odds = ""
    if with_order:
        odds = f" — about {with_order} times in 100" + (f" ({tag})" if tag else "")
    elif tag:
        odds = f" — {tag}"
    # (read blind, round 1: "Not counted among those on their own" — counted
    # against what? The commander's row names the place he takes; this names
    # the same thing, not taken.)
    return head + odds + ". He takes none of your places for men on their own."


def rows(world, stash: Dict[str, Any], readers: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The list's rows for an army's task or a changed war goal — each the
    read-back's own reading of that man's OWN line. The caller holds
    `parse_preview.reading()`. PURE."""
    from backend.commands import directive as DV
    from backend.commands import parse_preview as pp
    task = stash.get("task") or {}
    goal = stash.get("goal") or {}
    left = dict(task.get("left") or goal.get("left") or {})
    lead = str(task.get("lead") or "")
    lead_man = world.get_marshal(lead) if lead else None
    out: List[Dict[str, Any]] = []
    lead_ok = True
    for name in [str(n) for n in (stash.get("addressed") or stash.get("members") or [])]:
        man = world.get_marshal(name)
        line = str((stash.get("lines_by") or {}).get(name) or "")
        if name in left or man is None or not line:
            row = DV._row_from_reading(name, line, {})
            row["why"] = left.get(name) or "not in the field"
            out.append(row)
            continue
        try:
            reading = pp.read_one(world, line, **readers)
        except Exception as exc:
            report(exc, "army_task.rows: parse_preview.read_one")
            reading = {}
        row = DV._row_from_reading(name, line, reading)
        if task and name == lead:
            row["lead"] = True
            held = _own().own(man) or {}
            at_its_head = str(held.get("army") or "") == str(task.get("army") or "")
            if (at_its_head and row["ok"] and not _marked_bold(str(task.get("rest") or ""))
                    and row["says"] == f"on his own: {_own().task_words(held)}"):
                # the same task again: he is at it — the line only adds the men
                # who do not follow him yet
                row.update(ok=False, already=True, notes=[], ap=0,
                           why=f"commands the {task['army']} on its own already — {_own().task_words(held)}")
            elif row["ok"]:
                row["locked"] = not at_its_head
                head = (f"Commands the {task['army']} — {task.get('why_lead') or 'by your word'}."
                        if not at_its_head else
                        f"Commands the {task['army']} on its own already — this changes his task.")
                passed = "; ".join(f"{_shown(n)} outranks him but {_so(why)}"
                                   for n, why in (task.get("passed") or []))
                place = ""
                if not _own().on_his_own(man):
                    room = int(_own().allowed(world))
                    place = (" He takes your one place for a man on his own." if room == 1 else
                             f" He takes {_own().count(world) + 1} of the {room} places you have for "
                             "men on their own.")
                row["voice"] = next((str(n) for n in row["notes"] if str(n).startswith("“")), "")
                row["notes"] = ([head + (f" ({passed}.)" if passed else "") + place]
                                + _for_the_list(row["notes"], _shown(name), _army_shown(stash)))
            else:
                lead_ok = False
                if not _own().on_his_own(man) and _own().count(world) >= _own().allowed(world) \
                        and not may_command(world, man, str(task.get("kind") or "")):
                    # (pressed in the real client: "the count is full — on their
                    # own: 1 of the 1 …" twice on one card) said once, plainly
                    row["why"] = "would command — but no place is free for another man on his own"
        elif task and row["ok"]:
            terms = str(((reading.get("_quote") or {}) if isinstance(reading.get("_quote"), dict) else {})
                        .get("terms") or "").strip()
            kept = [n for n in row["notes"] if n != terms and not _a_supports_own_terms(n)]
            row["notes"] = [his_part(world, lead_man, man)] + kept
            row["says"] = f"follow {_shown(lead)}"
        elif goal and row["ok"]:
            # (short, as a commander's row is: his first night, then what warns)
            # (read blind, round 2: "keeps to Bohemia" — keeps attacking it, or his order
            # stands? The reply's own words: he keeps to his task)
            row["notes"] = ([f"Untick him and he keeps to his task ({_was(world, man)}) — he then serves "
                             "the war goal no longer."]
                            + _for_the_list(row["notes"], _shown(name)))
        out.append(row)
    if task and not lead_ok:
        # nobody follows a commander who cannot take the task (a commander who
        # is at it already is no such case: `already`)
        for row in out:
            if row.get("ok") and not row.get("lead"):
                row["ok"] = False
                row["why"] = f"would follow {_shown(lead)} — who cannot take the task as things stand"
    for row in out:
        row["tones"] = [_tone(note) for note in (row.get("notes") or [])]
    return out


def _tone(note: str) -> str:
    """How a row's note is to be read on the card: `warn` (it costs or bars
    something), `tonight` (what he will do), `voice` (his answer), else `info`."""
    said = str(note or "")
    if said.startswith("“"):
        return "voice"
    if said.startswith(("His first night", "Tonight, as things stand", "Every night")):
        return "tonight"
    low = said.lower()
    if (low.startswith(("he objects", "not taken:", "untick him", "a second order")) or "he will resent" in low
            or "blocks the road" in low or "bars the road" in low or "costs" in low and "trust" in low):
        return "warn"
    return "info"


def _for_the_list(notes: List[str], shown: str, army_men: Tuple[str, ...] = ()) -> List[str]:
    """A commander's notes as the LIST says them — short enough that the men
    who follow him stand on the same screen (pressed in the real client at the
    first player's setup: his full read-back pushed both followers below the
    fold): his first night, then what warns. His odds are said where his first
    night does not say them; the count stands in the row's first line; his
    answer and the small print are the read-back's and his card's.

    `army_men` (the army's men as shown) — read blind, round 1: a man named
    beside the commander's battle, or the senior who resents the task, is often
    NOT of the army ("what do Lannes and Murat do?"), so the list says so."""
    night = [_beside_for_the_list(str(n), army_men) for n in notes
             if str(n).startswith(("His first night", "Tonight, as things stand"))]
    odds = [n for n in notes if str(n).startswith("he attacks only when")]
    warns = [_slight_for_the_list(str(n), shown, army_men) for n in notes if _tone(n) == "warn"]
    said_odds = any("he goes in when" in str(n) for n in night)
    return night + ([] if said_odds else [o[:1].upper() + o[1:] + "." for o in odds]) + warns


_SLIGHT_MARK = " outranks him and has no order"
_BESIDE_RE = re.compile(r", with (?P<who>[^()—]+?) beside him \((?P<may>they may join|he may join)\)")


def _slight_for_the_list(said: str, shown: str, army_men: Tuple[str, ...]) -> str:
    """"Murat outranks him and has no order" names the commander — and says
    when the senior is not one of the army's own men."""
    if _SLIGHT_MARK not in said:
        return said
    senior = said.split(_SLIGHT_MARK, 1)[0].strip()
    aside = " (not of this army)" if army_men and senior not in army_men else ""
    # one line on the list at the first player's setup (pressed: the bracket
    # wrapped it, and the card grew a line): what it costs, said short
    return f"{senior}{aside} outranks {shown} and has no order — he will resent {shown} for it"


def _beside_for_the_list(said: str, army_men: Tuple[str, ...]) -> str:
    """"…with Davout, Lannes and Murat beside him (they may join)" — where a
    man beside the battle is not of the army, the bracket says he may join all
    the same (the arrival roll asks who stands near, not whose army he is of)."""
    hit = _BESIDE_RE.search(said) if army_men else None
    if hit is None:
        return said
    named = [n.strip() for n in re.split(r", | and ", hit.group("who")) if n.strip()]
    outside = [n for n in named if n not in army_men]
    if not outside:
        return said
    may = hit.group("may")
    tail = "though not of this army" if len(outside) == len(named) else "of this army or not"
    return said[:hit.start("may")] + f"{may}, {tail}" + said[hit.end("may"):]


def _army_shown(stash: Dict[str, Any]) -> Tuple[str, ...]:
    """The army's men as the screen names them (the list's own addressees)."""
    return tuple(_shown(str(n)) for n in (stash.get("addressed") or stash.get("members") or []))


def _a_supports_own_terms(note: str) -> bool:
    """A sentence of the plain support order's terms that does not hold for an
    army's follower (he does not lapse, and he does not leave for the guns)."""
    text = str(note or "")
    return ("He will drop this order" in text or "lapses of itself" in text
            or "until you cancel it" in text or "keeps him at" in text)


def _was(world, man) -> str:
    own = _own()
    return own.task_words(own.own(man) or {}) if own.own(man) else "as it stands"


def offer(world, stash: Dict[str, Any], listing_rows: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """The one button the list offers when the task cannot be given as asked:
    stand down the lowest-ranked man on his own (the count is full), or give
    the same words as a plain order to every corps (nobody can command)."""
    own = _own()
    task = stash.get("task") or {}
    if not task:
        return None
    army = str(task.get("army") or "")
    lead = str(task.get("lead") or "")
    if not lead:
        return {"label": "Plain orders to each corps instead", "kind": "list",
                "line": f"{army}, {task['rest']} by exact orders",
                "tip": "The same words as an ordinary order for every corps — nobody is set on his own."}
    lead_row = next((r for r in listing_rows if r.get("marshal") == lead), None)
    lead_man = world.get_marshal(lead)
    if lead_row is None or lead_row.get("ok") or lead_man is None or own.on_his_own(lead_man):
        return None
    if own.count(world) < own.allowed(world):
        return None
    if may_command(world, lead_man, str(task.get("kind") or "")):
        # (the review, IC3B-V5) the count is not what bars him (a commander named
        # by the line whose trust is low): a freed place would not help — no
        # stand-down is offered for nothing
        return None
    lowest = (own.men(world) or [None])[-1]
    if lowest is None:
        return None
    price = str((own.payload(world, lowest) or {}).get("stand_down") or "free").split(" — ")[0]
    return {"label": f"Stand down {_shown(lowest.name)} ({price}) and list again", "kind": "send",
            "line": f"{lowest.name}, stand down", "then": canonical(army, task),
            "tip": (f"{_shown(lowest.name)} is the lowest-ranked of your men on their own "
                    f"({own.task_words(own.own(lowest) or {})}). Standing him down frees a place; "
                    "the list is then drawn again.")}


def dress(world, stash: Dict[str, Any], out: Dict[str, Any]) -> Dict[str, Any]:
    """What the list of an army's task (or a changed goal) carries besides its
    rows: its head's words, who commands, the note above the rows, the offer."""
    own = _own()
    task = stash.get("task") or {}
    goal = stash.get("goal") or {}
    rows_ = out.get("rows") or []
    if goal:
        out["order"] = f"turn to {goal['shown']} — your new war goal"
        out["who"] = "The men serving your war goal"
        out["goal"] = {"what": str(goal.get("what") or ""), "shown": str(goal.get("shown") or ""),
                       "was": str(goal.get("was") or "")}
        men = "the 1 man who serves" if len(rows_) == 1 else f"the {len(rows_)} men who serve"
        each = "1 action" if len(rows_) == 1 else "1 action each"
        # (read blind, round 1: "naming it is free" against "turning a man costs"
        # had to be read twice — the two prices stand in two sentences)
        out["say"] = (f"The war goal becomes {goal['shown']}"
                      + (f" (it was {goal['was']})" if goal.get("was") else "")
                      + f" when you Give — naming it is free. What costs is turning {men} it: {each}. "
                      "A man you leave unticked keeps his old target and serves the goal no longer.")
        out["help"] = ("Give names the new war goal and turns the ticked men to it. Untick a man to "
                       "leave him at his old target. Take back (Ctrl+Z) undoes it all.")
        return out
    if not task:
        return out
    lead = str(task.get("lead") or "")
    lead_row = next((r for r in rows_ if r.get("marshal") == lead), None)
    words = ""
    if lead_row is not None and str(lead_row.get("says") or "").startswith("on his own: "):
        words = str(lead_row["says"])[len("on his own: "):]
    if not words:
        words = re.sub(r"\s+", " ", as_his(task["rest"])).strip(" .!")
    out["order"] = f"{words}, on its own"       # the card's headline: "The Army of Italy: take Swabia, on its own"
    out["task"] = {"army": str(task.get("army") or ""), "lead": lead, "lead_shown": _shown(lead),
                   "words": words, "why_lead": str(task.get("why_lead") or ""),
                   "next": [str(n) for n in (task.get("next") or [])]}
    gift = offer(world, stash, rows_)
    if gift is not None:
        out["offer"] = gift
    note = ""
    if not lead:
        note = (f"No man of the {task['army']} can be set on his own — a task needs a bold or a "
                "careful marshal whose trust in you is 30 or more. Each man's reason is below.")
    elif lead_row is not None and not lead_row.get("ok") and not lead_row.get("already"):
        lead_man = world.get_marshal(lead)
        if (lead_man is not None and not own.on_his_own(lead_man) and own.count(world) >= own.allowed(world)
                and not may_command(world, lead_man, str(task.get("kind") or ""))):
            note = (f"You already have as many on their own as you may — "
                    f"{own.count_words(world).lower()}. {_shown(lead)} cannot take the army's task "
                    "until a place is free.")
        else:
            note = f"{_shown(lead)} cannot take the army's task: {lead_row.get('why') or 'it would be refused'}."
        if task.get("next") and not gift:
            note += f" Or have {_shown(task['next'][0])} command: “{task['army']} under {_shown(task['next'][0])}, {task['rest']}”."
    if note:
        out["note"] = note
    # (read blind, round 1: "the commander's row stays" was read as "he cannot be
    # unticked" — he can, and then nobody goes: the help says what happens)
    whom = _shown(lead) if lead else "the commander"
    out["help"] = (f"Untick a follower to leave him out; untick {whom} and nobody goes. Give sends it "
                   "as one order; Take back (Ctrl+Z) undoes it all. A marshal who objects asks you, "
                   "and the rest wait behind his question.")
    return out


def nobody_words(world, stash: Dict[str, Any]) -> str:
    """Said when no man of the army can be set on his own: each man's reason,
    and the same words as a plain order to every corps."""
    task = stash.get("task") or {}
    army = str(task.get("army") or "")
    left = task.get("left") or {}
    each = "; ".join(f"{_shown(n)} {why}" for n, why in left.items())
    return (f"No man of the {army} can be set on his own, Sire — {each or 'none qualifies'}. "
            f"For the same words as a plain order to every corps, say “{army}, {task.get('rest')} "
            "by exact orders”.")


def stale(listing: Dict[str, Any], members: List[str]) -> str:
    """The army's own rule on what was ticked: nobody follows a commander who
    is not given the task (unless he commands it already)."""
    task = listing.get("task") if isinstance(listing.get("task"), dict) else None
    if not task or not members:
        return ""
    lead = str(task.get("lead") or "")
    lead_row = next((r for r in (listing.get("rows") or []) if r.get("marshal") == lead), None)
    if lead and lead not in members and lead_row is not None and lead_row.get("ok") \
            and lead_row.get("locked"):
        return (f"{_shown(lead)} commands this task — the others follow him, so his own row "
                "cannot be left out.")
    return ""


# ═══════════════════════════ the give's seams ═══════════════════════════════

def after(world, stash: Dict[str, Any], name: str, result: Any) -> bool:
    """Called by the fan-out after each man's own line ran. Stamps what the
    list knew and his own line could not say — the army he commands, the war
    whose goal he serves — and returns False when the rest must not go (the
    commander did not take the task: nobody follows him)."""
    own = _own()
    task = stash.get("task") or {}
    goal = stash.get("goal") or {}
    ok = isinstance(result, dict) and result.get("success") is not False
    man = world.get_marshal(name)
    spec = own.own(man) if man is not None else None
    if task and name == task.get("lead"):
        if not ok or spec is None:
            return False
        army = str(task.get("army") or "")
        # ONE man at an army's head: a man who commanded it before keeps his
        # task as his own, and commands it no longer
        for other in own.men(world):
            if other is not man and str((own.own(other) or {}).get("army") or "") == army:
                (own.own(other) or {}).pop("army", None)
        spec["army"] = army
        return True
    if goal and ok and spec is not None:
        spec["goal"] = str(goal.get("court") or "")
    return True


def lead_stands(world, stash: Dict[str, Any], name: str) -> bool:
    """Asked by the fan-out before a FOLLOWER's line is sent: does the army's
    commander hold its task? `after` says so when his own line ran to its end —
    but a line the parser could not read, one the state probe refused or one
    that raised never reaches `after`, and his men were then sent to follow a
    man with no task (the review, IC3B-V4). True for the commander's own line,
    for a changed goal's list, and wherever the list has no commander. PURE."""
    task = stash.get("task") or {}
    lead = str(task.get("lead") or "")
    if not task or not lead or name == lead:
        return True
    man = world.get_marshal(lead)
    spec = _own().own(man) if man is not None else None
    return spec is not None and str(spec.get("army") or "") == str(task.get("army") or "")


def settle(world) -> List[str]:
    """A commander whose army is gone, or who is its man no longer, commands
    nothing: he keeps his task as his own, and the men who followed him follow
    by an ordinary order (`following` is None for them). The review (IC3B-V6):
    the mark `own["army"]` is the army's NAME — it outlived a disbanded army,
    and a new army of that name made his old followers an army's again with no
    list. Called where the armies change and as each turn begins. Returns what
    to say; [] — and nothing written — when nothing changed."""
    said: List[str] = []
    try:
        own = _own()
        from backend.game_logic import armies
        for man in own.men(world):
            spec = own.own(man) or {}
            army = str(spec.get("army") or "")
            if not army or man.name in armies.members(world, army):
                continue
            spec.pop("army", None)
            said.append(f"{_shown(man.name)} commands the {army} no longer — he keeps his task "
                        f"({own.task_words(spec)}) as his own; any man who followed him still "
                        "does, by an ordinary order.")
    except Exception as exc:
        report(exc, "army_task.settle")
    return said


def before(world, stash: Dict[str, Any]) -> List[str]:
    """Called once by the fan-out before the first line: a changed war goal is
    NAMED first (free), so each man's line turns him to it. Returns what to say."""
    goal = stash.get("goal") or {}
    if not goal:
        return []
    from backend.game_logic import war_goals
    outcome = war_goals.set_goal(world, str(goal.get("what") or ""))
    if not outcome.get("success"):
        raise GoalNotSet(str(outcome.get("message") or "The war goal could not be named."))
    named = outcome.get("goal") or {}
    world.log_event({"type": "war_goal", "nation": world.player_nation, "op": "set",
                     "against": str(outcome.get("court") or ""),
                     "target": str(named.get("target") or ""), "kind": str(named.get("kind") or ""),
                     "line": str(outcome.get("message") or "")})
    return [str(outcome.get("message") or "")]


def after_all(world, stash: Dict[str, Any], sent: List[str]) -> List[str]:
    """Called once after the last line: the men who served the old goal and
    were not turned keep their targets and serve it no longer."""
    goal = stash.get("goal") or {}
    if not goal:
        return []
    from backend.game_logic import war_goals
    return war_goals.release(world, keep=sent, court=str(goal.get("court") or ""))


class GoalNotSet(Exception):
    """The war goal the list named could not be set — nothing is turned."""


# ═══════════════════════════ a changed war goal ═════════════════════════════

def goal_change(world, text: str) -> Optional[Dict[str, Any]]:
    """`{"kind": "goal", "names", "what", …}` when the line names a NEW war
    goal while men serve the goal of that war — else None (the staff's free
    book takes the line, as it always did). PURE."""
    if not an_army_takes_a_task():
        return None
    try:
        from backend.game_logic import war_goals
        order = war_goals.read_order(text)
        if not order or order.get("op") != "set" or not war_goals.a_war_has_a_goal():
            return None
        kind, name, court, refusal = war_goals.aim(world, str(order.get("what") or ""))
        if refusal or not court:
            return None
        men = war_goals.serving(world, court)
        if not men:
            return None
        old = war_goals.goal_in_war(world, court)
        if old is not None and (str(old[1].get("kind")), str(old[1].get("target"))) == (kind, name):
            return None
        return {"kind": "goal", "names": [m.name for m in men], "rest": "",
                "what": str(order.get("what") or ""), "goal_kind": kind, "target": name, "court": court,
                "was": war_goals.target_shown(world, old[1]) if old is not None else ""}
    except Exception as exc:
        report(exc, "army_task.goal_change")
        return None


def build_goal(world, found: Dict[str, Any], command_text: str) -> Tuple[str, Dict[str, Any]]:
    """The stash of a changed war goal: each man serving it, turned by his own
    typed line ("Ney, take Munich on your own"). PURE."""
    from backend.game_logic import war_goals
    kind, target = str(found.get("goal_kind") or "place"), str(found.get("target") or "")
    names = _in_rank(world, [str(n) for n in (found.get("names") or [])])
    verb, task = ("chase", "pursue") if kind == "army" else ("take", "take")
    lines = {n: f"{n}, {verb} {_shown(target)} on your own" for n in names}
    shown = war_goals.target_shown(world, {"kind": kind, "target": target})
    return ("stash", {
        "rest": f"{verb} {_shown(target)}", "action": "own_task", "strategic_type": None,
        "target": target, "members": list(names),
        "turn": int(getattr(world, "current_turn", 0) or 0),
        "army": False, "band": None, "note": "", "lines": [], "events": [],
        "raw": command_text, "at": "", "kind": "goal", "addressed": list(names), "who": list(names),
        "army_name": "", "click": False, "always_list": True, "own_lines": True,
        "lines_by": lines, "verbs_by": {n: "" for n in names},
        "goal": {"what": str(found.get("what") or ""), "court": str(found.get("court") or ""),
                 "task": task, "target": target, "kind": kind, "shown": shown,
                 "was": str(found.get("was") or ""),
                 "line": (f"make {_shown(target)} the war goal" if kind == "army"
                          else f"the war goal is {_shown(target)}")},
    })


# ═══════════════════════════ the followers ══════════════════════════════════

def following(world, marshal, order=_STANDING):
    """THE one test: the commander this man follows as part of an army's task
    — a FOLLOW order (the support that stays) whose friend commands, on his
    own, the army this man is in — or None. `order` is the order in question
    (default: the one he holds); a new order being read is handed in."""
    if marshal is None or world is None or not an_army_takes_a_task():
        return None
    held = getattr(marshal, "strategic_order", None) if order is _STANDING else order
    if held is None or str(getattr(held, "command_type", "") or "") != "SUPPORT" \
            or not getattr(held, "standing_follow", False):
        return None
    lead = world.get_marshal(str(getattr(held, "target", "") or ""))
    if lead is None or lead is marshal or getattr(lead, "nation", None) != getattr(marshal, "nation", None):
        return None
    spec = _own().own(lead)
    army = str((spec or {}).get("army") or "")
    if not army:
        return None
    from backend.game_logic import armies
    men = armies.members(world, army)
    # (the review, IC3B-V6) BOTH are the army's men: a commander taken out of
    # it leads no army, whatever mark his task still carries
    return lead if marshal.name in men and lead.name in men else None


def followers(world, lead) -> List[Any]:
    """The men who follow this commander as his army's task, highest rank first."""
    spec = _own().own(lead) if lead is not None else None
    army = str((spec or {}).get("army") or "")
    if not army:
        return []
    from backend.game_logic import armies
    found = []
    for name in armies.members(world, army):
        man = world.get_marshal(name)
        if man is not None and man is not lead and following(world, man) is lead \
                and int(getattr(man, "strength", 0) or 0) > 0:
            found.append(name)
    return [world.get_marshal(n) for n in _in_rank(world, found)]


def task_of(world, army: str) -> Dict[str, Any]:
    """The army's task, for its chip and its card — {} when it has none."""
    own = _own()
    from backend.game_logic import armies
    for name in armies.members(world, army):
        man = world.get_marshal(name)
        spec = own.own(man) if man is not None else None
        if spec is not None and str(spec.get("army") or "") == str(army):
            words = own.task_words(spec)
            return {"lead": name, "lead_shown": _shown(name), "words": words,
                    "line": f"on its own: {words}",
                    "followers": [m.name for m in followers(world, man)]}
    return {}


def proposal(world, army: str) -> Dict[str, Any]:
    """A ready task for the army ("Give it a task…" — the line is never
    blank): the war goal, where one is open and its commander can go for it;
    else its commander's OWN idea (`own_order.proposal`), said to the army.
    ``{"line", "lead", "why"}`` — `line` "" when no man of it can command. PURE."""
    own = _own()
    lead = str(task_of(world, army).get("lead") or "") or commander(world, army, "hold")["lead"]
    man = world.get_marshal(lead) if lead else None
    if man is None:
        return {"line": "", "lead": "", "why": f"No man of the {army} can be set on his own"}
    try:
        from backend.game_logic import war_goals
        goal = war_goals.task_for(world, man)
        if not goal["refusal"] and not own.why_not(world, man, goal["task"], replacing=True):
            return {"line": f"{army}, take the war goal", "lead": lead,
                    "why": f"your war goal is open, and {_shown(lead)} can go for it"}
    except Exception as exc:
        report(exc, "army_task.proposal: the war goal")
    idea = own.proposal(world, man)
    task, target = str(idea.get("task") or "hold"), str(idea.get("target") or "")
    if task == "take" and target:
        words = f"take {_shown(target)}"
    elif task == "pursue" and target:
        words = f"chase {_shown(target)}"
    elif task == "hold" and target:
        words = f"hold {_shown(target)}"
    else:
        words = f"hold {_shown(man.location)}"
    return {"line": f"{army}, {words}", "lead": lead, "why": str(idea.get("why") or "")}


def _battle_of(reading: Dict[str, Any]) -> str:
    """The place the commander's planned act fights at, or ""."""
    if any((step or {}).get("action") == "attack" for step in (reading.get("do") or [])):
        return str(reading.get("place") or "")
    return ""


def _ends_at(lead, reading: Dict[str, Any]) -> str:
    """Where the commander stands when his planned act is done (a battle may
    carry him forward: he is read as standing where he is)."""
    if _battle_of(reading):
        return str(lead.location or "")
    moves = [str(step.get("target") or "") for step in (reading.get("do") or [])
             if (step or {}).get("action") == "move" and step.get("target")]
    return moves[-1] if moves else str(lead.location or "")


def _f(man, lead, act: str, line: str, *, place: str = "", do=None, why: str = "") -> Dict[str, Any]:
    return {"marshal": man.name, "shown": _shown(man.name), "act": act,
            "place": place or str(man.location or ""), "target": lead.name, "line": line,
            "do": list(do or []), "why": why, "follows": lead.name,
            "visible": act in ("follow", "stand_by", "join"),
            "may_day": False, "step_out": False}


def follower_reading(world, man, lead, lead_dest: str, battle_place: str = "") -> Dict[str, Any]:
    """What a follower does tonight — PURE. `lead_dest`: where his commander
    will stand; `battle_place`: where the commander fights tonight, if he does.
    Beside the battle he stands by (the arrival roll may bring him into it);
    with his commander he stays; else he marches after him, by the road a man
    marching to a friend takes (`own_order._road`: round the enemy France
    sees), as far as he ranges and short of any corps in sight."""
    own = _own()
    shown, lead_shown = _shown(man.name), _shown(lead.name)
    here = str(man.location or "")
    turn = int(getattr(world, "current_turn", 0) or 0)
    order = getattr(man, "strategic_order", None)
    if order is not None and getattr(order, "issued_turn", None) == turn:
        return _f(man, lead, "start", f"{shown} set out when the order was given — he follows "
                                      f"{lead_shown} from tomorrow night", why="given today")
    if own._int({"t": getattr(man, "last_ordered_turn", None)}, "t") == turn:
        return _f(man, lead, "stay", f"{shown} carried out your order today — he follows {lead_shown} "
                                     "again tomorrow night", why="your order today")
    if bool(getattr(man, "reinforced_this_turn", False)) and not battle_place:
        return _f(man, lead, "stay", f"{shown} fought beside a friend today — he follows {lead_shown} "
                                     "again tomorrow night", why="drawn in today")
    unfit = own._unfit(world, man)
    if unfit:
        return _f(man, lead, "recover", f"{shown} recovers — {unfit}", why=unfit)
    if battle_place:
        d = own._distance(world, here, battle_place)
        if d is not None and d <= 1:
            with_order, _without = _arrival(world, lead, man)
            odds = f" (about {with_order} times in 100)" if with_order else ""
            return _f(man, lead, "stand_by",
                      f"{shown} stands by {lead_shown}'s attack at {_shown(battle_place)} — he may "
                      f"join it{odds}", place=here)
    dest = str(lead_dest or "")
    if not dest or here == dest:
        return _f(man, lead, "with", f"{shown} stays with {lead_shown} at {_shown(here)}", place=here)
    road = own._road(world, man, dest, avoid_foes=True)
    if not road:
        return _f(man, lead, "halt", f"{shown} cannot reach {lead_shown} — no road is open to him",
                  why="no road")
    leg = own._first_leg(world, man, road)
    if not leg:
        return _f(man, lead, "halt",
                  f"{shown} halts — the road to {lead_shown} is barred at {_shown(road[0])}",
                  why="road barred")
    do = ([{"action": "unfortify"}] if getattr(man, "fortified", False) else [])
    do += [{"action": "move", "target": p} for p in leg]
    if leg[-1] == dest:
        line = f"{shown} marches to join {lead_shown} at {_shown(dest)}"
    else:
        behind = max(1, len(road) - len(leg))
        line = (f"{shown} marches after {lead_shown} — to {_shown(leg[-1])}, "
                f"{_plural(behind, 'march')} behind him")
    return _f(man, lead, "follow", line, place=leg[-1], do=do)


def key_of(reading: Optional[Dict[str, Any]]) -> Tuple[str, str]:
    """What makes two follower readings the same act (R-TRUE)."""
    if not reading:
        return ("", "")
    return (str(reading.get("act") or ""), str(reading.get("place") or ""))


def tonight(world, readings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Every follower's night, in the order of the pass — after his commander,
    highest rank first — read on what the commander's "Tonight" says. PURE."""
    out: List[Dict[str, Any]] = []
    if not an_army_takes_a_task() or not getattr(world, "armies", None):
        return out
    for reading in readings or []:
        lead = world.get_marshal(str(reading.get("marshal") or ""))
        if lead is None:
            continue
        for man in followers(world, lead):
            try:
                out.append(follower_reading(world, man, lead, _ends_at(lead, reading), _battle_of(reading)))
            except Exception as exc:
                report(exc, f"army_task.tonight: {man.name}")
                out.append(_f(man, lead, "stay", f"{_shown(man.name)} stays put",
                              why="the board could not be read"))
    return out


def followers_night(world, executor, game_state, lead, said_lead: Dict[str, Any],
                    plan: Dict[str, Dict[str, Any]], fought: List[str]) -> List[Dict[str, Any]]:
    """THE PASS, for one commander's followers — right after his own act, before
    the enemy moves. Each does what "Tonight" said, or stays put and says why
    (D8); none starts an attack of his own."""
    rows_: List[Dict[str, Any]] = []
    lead_shown = _shown(lead.name)
    fights = lead.name in (fought or [])
    battle = _battle_of(said_lead or {}) if fights else ""
    for man in followers(world, lead):
        said = plan.get(man.name)
        if said is None or getattr(world, "game_over", False):
            continue
        shown = _shown(man.name)
        try:
            if said.get("act") == "stand_by":
                if not fights:
                    rows_.append(_row(man, lead, said, "stay",
                                      f"{shown} stays put — {lead_shown} did not attack after all"))
                elif bool(getattr(man, "reinforced_this_turn", False)):
                    rows_.append(_row(man, lead, said, "join",
                                      f"{shown} marched to {lead_shown}'s battle at "
                                      f"{_shown(battle)} and joined it"))
                else:
                    rows_.append(_row(man, lead, said, "stand_by",
                                      f"{shown} stood by {lead_shown}'s attack at {_shown(battle)} "
                                      "and did not arrive in time"))
                continue
            if bool(getattr(man, "reinforced_this_turn", False)) and said.get("why") != "drawn in today":
                rows_.append(_row(man, lead, said, "join",
                                  f"{shown} was drawn into a battle beside him — that was his night"))
                continue
            fresh = follower_reading(world, man, lead, str(lead.location or ""), battle)
            if key_of(fresh) != key_of(said):
                what = "fight" if fights else "night"
                rows_.append(_row(man, lead, said, "stay",
                                  f"{shown} stays put — {lead_shown}'s {what} changed things"))
                continue
            refused = ""
            moved = False
            for step in fresh.get("do") or []:
                result = executor.execute({"command": {"marshal": man.name, "_strategic_execution": True,
                                                       **step}}, game_state)
                if step.get("action") == "unfortify":
                    continue
                if not (isinstance(result, dict) and result.get("success", False)):
                    refused = str((result or {}).get("message") or "the march could not be made")
                    break
                moved = True
            if refused:
                rows_.append(_row(man, lead, said, "follow" if moved else "stay",
                                  f"{shown} could not follow {lead_shown} as planned: {refused.rstrip('.')}"))
                continue
            line = str(fresh.get("line") or "")
            if fresh.get("act") == "start":
                line = f"{shown} set out to follow {lead_shown} when the order was given"
            rows_.append(_row(man, lead, said, str(fresh.get("act") or "stay"), line,
                              place=str(fresh.get("place") or "")))
        except Exception as exc:
            report(exc, f"army_task.followers_night: {man.name}")
            rows_.append(_row(man, lead, said, "stay",
                              f"{shown} stays put — the night could not be carried out"))
    return rows_


def _row(man, lead, said: Dict[str, Any], act: str, message: str, **extra) -> Dict[str, Any]:
    row = {"marshal": man.name, "command": "SUPPORT", "order_status": "continues",
           "action": f"army_{act}", "message": message.rstrip(".") + ".",
           "reason": message.rstrip(".") + ".", "own": True, "follows": lead.name,
           "act": act, "said": str(said.get("line") or "")}
    row.update(extra)
    return row


# ═══════════════════════════ what the screens say ═══════════════════════════

_SHOWN: Dict[str, Any] = {"key": None, "rows": None}


def tonight_shown(world) -> List[Dict[str, Any]]:
    """`tonight` for the screens, kept while the board is unchanged (the desk
    is built on every reply — golden rule 8)."""
    own = _own()
    if not getattr(world, "armies", None):
        return []
    try:
        key = own._board_key(world)
    except Exception as exc:
        report(exc, "army_task.tonight_shown: the key")
        return tonight(world, own.tonight_shown(world))
    if _SHOWN["key"] != key:
        _SHOWN["rows"] = tonight(world, own.tonight_shown(world))
        _SHOWN["key"] = key
    return list(_SHOWN["rows"] or [])


def tonight_rows(world, lead_name: str) -> List[Dict[str, Any]]:
    """The followers' lines under their commander's "Tonight" (the desk, the
    End Turn list)."""
    out = []
    for reading in tonight_shown(world):
        if reading.get("follows") != lead_name:
            continue
        out.append({"marshal": reading["marshal"], "shown": reading["shown"], "act": reading["act"],
                    "line": "Tonight: " + str(reading.get("line") or ""),
                    "may_day": False, "visible": bool(reading.get("visible")),
                    "step_out": False, "follows": lead_name})
    return out


def follower_payload(world, marshal) -> Optional[Dict[str, Any]]:
    """A follower's card: whom he follows, for which army, and his night."""
    lead = following(world, marshal)
    if lead is None:
        return None
    own = _own()
    spec = own.own(lead) or {}
    mine = next((r for r in tonight_shown(world) if r.get("marshal") == marshal.name), {})
    with_order, _without = _arrival(world, lead, marshal)
    return {"lead": lead.name, "lead_shown": _shown(lead.name), "army": str(spec.get("army") or ""),
            "task": own.task_words(spec), "tonight": str(mine.get("line") or ""),
            "odds": int(with_order)}


def commander_payload(world, marshal) -> Dict[str, Any]:
    """What a commander's card adds: the army he commands and who follows him."""
    spec = _own().own(marshal) or {}
    army = str(spec.get("army") or "")
    if not army:
        return {}
    return {"army": army, "followers": [_shown(m.name) for m in followers(world, marshal)]}


def ending_words(world, marshal) -> str:
    """Said when a commander's task ends: his followers keep following him."""
    spec = _own().own(marshal) or {}
    army = str(spec.get("army") or "")
    men = followers(world, marshal) if army else []
    if not men:
        return ""
    who = _names([m.name for m in men])
    one = len(men) == 1
    # (the review: "him" stood a sentence away from the man it meant; one man is "him")
    return (f" {who} still follow{'s' if one else ''} {_shown(marshal.name)}, by an ordinary order now — "
            f"“{army}, stop” recalls {'him' if one else 'them'}.")


# ═══════════════════════════ the read-back ══════════════════════════════════

def readback(world, text: str, out: Dict[str, Any], listing: Dict[str, Any],
             stash: Dict[str, Any]) -> Dict[str, Any]:
    """`/parse_preview`'s reading of a line that is an army's task (or a
    changed war goal with men serving it): the list it will open, said in rows
    — who commands, his first night, what the others do, who is left out, the
    price — and the buttons that write into the sentence. Called INSIDE the
    read-back's lock."""
    from backend.commands import parse_preview as pp
    rows_ = listing.get("rows") or []
    going = [r for r in rows_ if r.get("ok")]
    ticked = [r for r in rows_ if r.get("ticked")]
    have = int(listing.get("have", 0) or 0)
    full = sum(int(r.get("ap", 0) or 0) for r in going)
    out.update(kind="order", action="own_task", strategic=True, ap=int(listing.get("total", 0) or 0),
               ap_left=have, pool="military", ok=bool(going), free=False)
    out["directive"] = True
    parts: List[Tuple[str, str]] = []
    chips: List[Dict[str, str]] = []
    if listing.get("goal"):
        goal = listing["goal"]
        parts.append(("head", f"The war goal · {goal['shown']} · {_plural(len(going), 'man')} to turn"))
        parts.append(("cost", f"{pp._cost_text(full, 'military', full == 0)} for the {have} in hand"
                              if going else "free"))
        for r in going:
            parts.append(("taken", f"{r['shown']} serves the war goal — he turns to {goal['shown']} (1 action)"))
        for r in rows_:
            if not r.get("ok"):
                parts.append(("warn", f"{r['shown']} is not turned — {r.get('why') or 'he cannot be'}; "
                                      "he keeps his old target"))
        parts.append(("note", "naming the goal is free; a man left unticked keeps his old target"))
        parts.append(("note", "Enter shows the list"))
        out["parts"] = [pp._part(role, said) for role, said in parts]
        return out
    task = listing.get("task") or {}
    army = str(task.get("army") or "")
    lead = str(task.get("lead") or "")
    lead_row = next((r for r in rows_ if r.get("marshal") == lead), None)
    head = f"The {army} · on its own: {task.get('words') or 'a task'}"
    if not going:
        why = str(listing.get("note") or "nobody can take this task as things stand")
        out.update(kind="refusal", ok=False, refusal=why)
        parts = [("head", head), ("bad", why), ("cost", "free refusal")]
        for r in rows_:
            if r.get("why") and not listing.get("offer", {}).get("kind") == "send":
                parts.append(("warn", f"{r['shown']} — {r['why']}"))
    else:
        short = len(going) - len(ticked)
        cost = f"{pp._cost_text(full, 'military', full == 0)} for the {have} in hand"
        if short > 0:
            cost += f" — {_plural(short, 'man')} must wait for tomorrow's actions"
        parts = [("head", head), ("cost", cost)]
        if lead_row is not None and lead_row.get("ok"):
            price = int(lead_row.get("ap", 0) or 0)
            parts.append(("taken", f"{_shown(lead)} commands — {task.get('why_lead') or 'by your word'}; "
                                   f"he is set on his own ({_plural(price, 'action')})"))
            for note in (lead_row.get("notes") or [])[1:]:
                said = str(note)
                if said.startswith("His first night") or said.startswith("Tonight, as things stand"):
                    parts.append(("tonight", said))
                elif _tone(said) == "warn":
                    parts.append(("warn", said))
            if lead_row.get("voice"):
                parts.append(("answer", str(lead_row["voice"])))
        elif lead_row is not None:
            parts.append(("taken", f"{_shown(lead)} {lead_row.get('why') or 'commands it already'}"))
        men = [r for r in going if r.get("marshal") != lead]
        if men:
            who = _names([r["marshal"] for r in men])
            one = len(men) == 1
            parts.append(("taken", f"{who} follow{'s' if one else ''} him — 1 action{'' if one else ' each'}, "
                                   f"and take{'s' if one else ''} none of your places for men on their "
                                   f"own; {'he moves' if one else 'they move'} with him each night and "
                                   f"may join his battles"))
        for r in rows_:
            if not r.get("ok") and r.get("marshal") != lead:
                parts.append(("warn", f"{r['shown']} is left out — {r.get('why') or 'he cannot go'}"))
        parts.append(("note", "Enter shows the list"))
    out["parts"] = [pp._part(role, said) for role, said in parts]
    gift = listing.get("offer") if isinstance(listing.get("offer"), dict) else None
    if gift is not None:
        chips.append({"label": str(gift.get("label") or ""), "line": str(gift.get("line") or "")})
    typed = str(text or "").rstrip()
    if going and not _marked_bold(typed):
        chips.append({"label": "+ boldly (attacks at worse odds)", "line": pp._with_word(typed, "boldly")})
        chips.append({"label": "+ carefully (only at better odds)", "line": pp._with_word(typed, "carefully")})
    for name in (task.get("next") or [])[:1]:
        chips.append({"label": f"{_shown(name)} commands instead",
                      "line": f"{army} under {_shown(name)}, {task_rest(text, army)}"})
    if going or lead:
        chips.append({"label": "Plain orders to each corps instead",
                      "line": f"{army}, {task_rest(text, army)} by exact orders"})
    out["candidates"] = chips[:4]
    return out


def _marked_bold(text: str) -> bool:
    try:
        from backend.ai import task_words
        low = " " + re.sub(r"[^a-z' ]+", " ", str(text or "").lower()) + " "
        return any(f" {w} " in low for w in tuple(task_words.BOLDER_WORDS) + tuple(task_words.CAREFUL_WORDS))
    except Exception as exc:
        report(exc, "army_task._marked_bold")
        return True


def task_rest(text: str, army: str) -> str:
    """The task's own words off a typed line ("Army of Italy under Ney, take
    Swabia." → "take Swabia")."""
    pattern = r"\s+".join(re.escape(word) for word in str(army).split())
    rest = re.sub(r"^\s*(?:(?:the|my|our)\s+)?" + pattern + r"\s*[,:;—-]?\s*", "", str(text or ""),
                  flags=re.IGNORECASE)
    named = _UNDER_RE.match(rest)
    if named:
        rest = named.group("rest")
    return rest.strip().rstrip(".! ")
