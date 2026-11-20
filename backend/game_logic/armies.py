"""Row IC, directives (IC-5) — NAMED ARMIES (November 19, 2026).

The user's ruling in Plan Mode: "Yes, named armies" — form an army, name it,
give it an order by name ("Army of Italy, hold"). An army is a SAVED GROUP of
the player's own marshals and nothing more: no bonus, no cost, no rule of the
game reads it. It exists so that one line, or one chip, addresses the same men
again (`backend/commands/directive.py` reads who an order goes to).

The store is `world.armies` — ``{name: {"members": [marshal, …],
"formed_turn": n}}`` — written to a save only when it holds something. The
four verbs (form · add · remove · disband) are the free action `army`
(`backend/commands/directive_executor.py`).

THE RULES
=========
* A marshal is in ONE army at most: joining a second takes him out of the
  first, and the reply says so.
* An army with no member left dissolves, and says so.
* A member who is no longer ours to order — dead, dismissed, a prisoner, gone
  over to another court — drops out (`prune`, called where a marshal leaves the
  roster and as the turn begins).
* A name must hold the word "army" (or "armée"), is not named after a man (no
  marshal's name inside it), and is not the bare words that already mean the
  whole army ("the army", "Grande Armée"). "Army of Italy" is fine: an army's
  name is read BEFORE any other reader sees the line (`address_of`).

`armies_can_be_named` is the seam: down, no army can be formed and no line is
read as addressed to one.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from backend.display_names import humanize_entity_name
from backend.errors import report

NAME_MIN = 4
NAME_MAX = 40
_NAME_CHARS_RE = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ0-9 '’\-]+$")
_ARMY_WORD_RE = re.compile(r"(?<![A-Za-zÀ-ÿ])arm(?:y|[eé]e)(?![A-Za-zÀ-ÿ])", re.IGNORECASE)
_ARTICLE_RE = re.compile(r"^\s*(?:the|my|our|la|l['’])\s*", re.IGNORECASE)


def armies_can_be_named() -> bool:
    """The seam (row IC, directives). One line to reverse: return False."""
    return True


# ── reading ─────────────────────────────────────────────────────────────────

def _player(world) -> str:
    return str(getattr(world, "player_nation", "") or "")


def store(world) -> Dict[str, Dict[str, Any]]:
    """The armies as saved ({} when none) — never created by a read."""
    held = getattr(world, "armies", None)
    return held if isinstance(held, dict) else {}


def tidy(name: str) -> str:
    """A name as it is kept: quotes and a leading article off, one space
    between words ("the  Army of Italy" -> "Army of Italy")."""
    quotes = "\"“”'‘’"
    text = str(name or "").strip().strip(quotes).strip()
    text = _ARTICLE_RE.sub("", text).strip().strip(quotes)
    return " ".join(text.split())


def _key(name: str) -> str:
    return tidy(name).casefold()


def find(world, typed: str) -> Optional[str]:
    """The saved name `typed` means (any case, an article or not), or None."""
    want = _key(typed)
    if not want:
        return None
    for name in store(world):
        if _key(name) == want:
            return name
    return None


def _ours(world, marshal) -> bool:
    return (marshal is not None and getattr(marshal, "nation", None) == _player(world)
            and not getattr(marshal, "captured_by", ""))


def members(world, name: str) -> List[str]:
    """The army's men who are still ours to order, in the order they were named."""
    row = store(world).get(name) or {}
    roster = getattr(world, "marshals", None) or {}
    return [str(n) for n in (row.get("members") or []) if _ours(world, roster.get(str(n)))]


def field_members(world, name: str) -> List[str]:
    """Those of them standing in the field (not at a desk, with men under them)."""
    roster = getattr(world, "marshals", None) or {}
    out = []
    for n in members(world, name):
        m = roster.get(n)
        if (m is not None and int(getattr(m, "strength", 0) or 0) > 0
                and not getattr(m, "administrative", False)):
            out.append(n)
    return out


def army_of(world, marshal_name: str) -> Optional[str]:
    """The army this marshal is in, or None."""
    for name, row in store(world).items():
        if str(marshal_name) in [str(n) for n in ((row or {}).get("members") or [])]:
            return name
    return None


def shown(name: str) -> str:
    """The army in a sentence: "the Army of Italy"."""
    return f"the {name}"


def _names(listed: List[str]) -> str:
    listed = [humanize_entity_name(n) for n in listed if n]
    if not listed:
        return ""
    if len(listed) == 1:
        return listed[0]
    return ", ".join(listed[:-1]) + " and " + listed[-1]


def payload(world) -> List[Dict[str, Any]]:
    """What the client draws its army chips from: the armies in the order they
    were formed, each with its men still ours to order (a marshal's key and
    his printed name). [] when none — and with the seam down."""
    if not armies_can_be_named():
        return []
    out: List[Dict[str, Any]] = []
    for name in store(world):
        mine = members(world, name)
        if not mine:
            continue
        out.append({"name": str(name), "members": mine,
                    "members_shown": [humanize_entity_name(n) for n in mine],
                    "in_field": int(len(field_members(world, name)))})
    return out


# ── the name ────────────────────────────────────────────────────────────────

def name_refusal(world, name: str) -> str:
    """Why `name` cannot be an army's name, in plain words — "" when it can."""
    text = tidy(name)
    if len(text) < NAME_MIN:
        return "An army needs a name — for example “Army of Italy”."
    if len(text) > NAME_MAX:
        return f"That name is too long — keep it under {NAME_MAX} letters."
    if not _NAME_CHARS_RE.match(text):
        return "An army's name is letters, numbers and spaces only."
    if not _ARMY_WORD_RE.search(text):
        return ("An army's name must hold the word “army” — for example "
                f"“Army of {text}”.")
    from backend.commands import group_orders
    if group_orders.is_collective_address(text) or group_orders.is_collective_address("the " + text):
        return (f"“{text}” already means every corps you have — give the army a name of "
                "its own, for example “Army of Italy”.")
    roster = getattr(world, "marshals", None) or {}
    for marshal_name in roster:
        for form in {str(marshal_name), humanize_entity_name(str(marshal_name))}:
            if form and re.search(r"(?<![A-Za-zÀ-ÿ])" + re.escape(form) + r"(?![A-Za-zÀ-ÿ])",
                                  text, re.IGNORECASE):
                return (f"An army is not named after a man — “{humanize_entity_name(marshal_name)}” "
                        "in its name would be read as an order to him. Name it for a place "
                        "or a task.")
    low = text.casefold()
    for region_name in (getattr(world, "regions", None) or {}):
        if str(region_name).casefold() == low:
            return f"“{text}” is a province — give the army a name of its own."
    try:
        nations = list(world.get_active_nations())
    except Exception as exc:
        report(exc, "armies.name_refusal: world.get_active_nations")
        nations = []
    for nation in nations:
        if low in (str(nation).casefold(), humanize_entity_name(str(nation)).casefold()):
            return f"“{text}” is a court — give the army a name of its own."
    return ""


# ── the address: "Army of Italy, hold" ──────────────────────────────────────

def address_of(world, text: str) -> Optional[Dict[str, str]]:
    """``{"army": <saved name>, "rest": <the order's words>}`` when the line
    opens with the name of an army that exists ("Army of Italy, hold", "the
    Army of Italy marches on Vienna"), else None. The longest name wins. PURE.

    Read BEFORE the ordinary parse: "army" alone already means every corps
    (`group_orders.COLLECTIVE_HEAD_RE`), so the saved names are tried first —
    and only when an army exists, so a board with none reads as it did."""
    if not armies_can_be_named():
        return None
    held = store(world)
    if not held or not text:
        return None
    # The review: "Army of Italy, disband" opens with the army's name too — it is
    # the army's own verb (`read_order`), never an order to its corps.
    if read_order(world, text) is not None:
        return None
    for name in sorted(held, key=len, reverse=True):
        pattern = r"\s+".join(re.escape(word) for word in str(name).split())
        match = re.match(r"^\s*(?:(?:the|my|our)\s+)?" + pattern
                         + r"(?![A-Za-zÀ-ÿ])\s*[,:;—-]?\s*(?P<rest>\S.*)?$",
                         str(text), re.IGNORECASE)
        if match:
            rest = (match.group("rest") or "").strip()
            if not rest:
                return None
            return {"army": str(name), "rest": rest}
    return None


# ── the typed line: form · add · remove · disband ──────────────────────────

_NAME = r"(?P<name>[^,:;]*?(?<![A-Za-zÀ-ÿ])arm(?:y|[eé]e)(?![A-Za-zÀ-ÿ])[^,:;]*?)"
_END = r"\s*[.!]*\s*$"
_FORM_RE = re.compile(
    r"^\s*(?:please\s+)?(?:form|create|raise|make|found|organi[sz]e|muster|gather)\s+"
    r"(?:(?:an?|the|a\s+new)\s+)?" + _NAME
    + r"\s*(?:[,:]|\b(?:with|from|out\s+of|of\s+the\s+corps\s+of|under|made\s+up\s+of|comprising)\b)\s*"
    r"(?P<who>\S.*?)" + _END, re.IGNORECASE)
_ADD_RE = re.compile(
    r"^\s*(?:please\s+)?(?:add|put|attach|assign)\s+(?P<who>\S.*?)\s+(?:to|into|in)\s+(?:the\s+)?"
    + _NAME + _END, re.IGNORECASE)
_JOINS_RE = re.compile(
    r"^\s*(?P<who>\S.*?)\s+(?:will\s+|shall\s+|now\s+)?joins?\s+(?:the\s+)?" + _NAME + _END, re.IGNORECASE)
_REMOVE_RE = re.compile(
    r"^\s*(?:please\s+)?(?:remove|take|detach|drop|strike)\s+(?P<who>\S.*?)\s+(?:from|out\s+of)\s+(?:the\s+)?"
    + _NAME + _END, re.IGNORECASE)
_LEAVES_RE = re.compile(
    r"^\s*(?P<who>\S.*?)\s+(?:will\s+|shall\s+|now\s+)?(?:leaves?|quits?)\s+(?:the\s+)?" + _NAME + _END,
    re.IGNORECASE)
_DISBAND_RE = re.compile(
    r"^\s*(?:please\s+)?(?:disband|dissolve|break\s+up)\s+(?:the\s+|my\s+|our\s+)?" + _NAME + _END,
    re.IGNORECASE)
_DISBAND_AFTER_RE = re.compile(
    r"^\s*(?:the\s+)?" + _NAME + r"\s*[,:]\s*(?:disband|dissolve|break\s+up)" + _END, re.IGNORECASE)
_LIST_RE = re.compile(r"^\s*(?:(?:list|show|name)\s+)?(?:my\s+|our\s+|the\s+)?armies" + _END, re.IGNORECASE)


def _people(who: str) -> List[str]:
    """The names in "Ney, Lannes and Marshal Murat"."""
    out = []
    for token in re.split(r"\s*(?:,|;|&|\band\b|\bplus\b)\s*", str(who or "")):
        token = re.sub(r"^(?:marshal|general|the\s+emperor['’]?s?\s+)\s*", "", token.strip(), flags=re.I)
        token = token.strip(" .!'’\"")
        if token:
            out.append(token)
    return out


def read_order(world, text: str) -> Optional[Dict[str, Any]]:
    """``{"op", "name", "who"}`` when the line is one of the army's four verbs
    ("form the Army of Italy with Masséna and Ney" · "add Lannes to the Army
    of Italy" · "remove Ney from the Army of Italy" · "disband the Army of
    Italy") or asks for the list ("armies"), else None. PURE.

    A line that forms, adds or removes must name at least one marshal of the
    player's own ("raise an army with fresh conscripts" is no such line); a
    question is never an order."""
    text = str(text or "")
    if world is None or not armies_can_be_named() or not text.strip() or text.strip().endswith("?"):
        return None
    if _LIST_RE.match(text):
        return {"op": "list", "name": "", "who": []}
    for pattern in (_DISBAND_RE, _DISBAND_AFTER_RE):
        match = pattern.match(text)
        if match:
            return {"op": "disband", "name": tidy(match.group("name")), "who": []}
    for op, patterns in (("remove", (_REMOVE_RE, _LEAVES_RE)), ("add", (_ADD_RE, _JOINS_RE)),
                         ("form", (_FORM_RE,))):
        for pattern in patterns:
            match = pattern.match(text)
            if not match:
                continue
            who = _people(match.group("who"))
            good, _bad = _resolve(world, who)
            if not good:
                continue
            # "Lannes joins the army at Ulm" is a sentence about a march, not
            # the roll: the forms that open with the man's name are read only
            # for an army that EXISTS (the verb-first forms name their intent).
            if pattern in (_JOINS_RE, _LEAVES_RE) and find(world, match.group("name")) is None:
                continue
            return {"op": op, "name": tidy(match.group("name")), "who": who}
    return None


def carry_out(world, order: Dict[str, Any]) -> Dict[str, Any]:
    """One of the four verbs, as `read_order` read it."""
    op = str(order.get("op") or "")
    name, who = str(order.get("name") or ""), list(order.get("who") or [])
    if op == "form":
        return form(world, name, who)
    if op == "add":
        return add(world, name, who)
    if op == "remove":
        return remove(world, name, who)
    if op == "disband":
        return disband(world, name)
    if op == "list":
        held = store(world)
        if not held:
            return {"success": True, "said": [], "message": (
                "You have formed no army yet. Select corps and press “Name this army…”, or say "
                "“form the Army of Italy with Ney and Lannes”.")}
        rows = [f"{name}: {_names(members(world, name)) or 'nobody'}" for name in held]
        return {"success": True, "said": [], "message": "Your armies — " + "; ".join(rows) + "."}
    return _refused("Say what to do with the army: form it, add a marshal, remove one, or disband it.")


# ── the four verbs ──────────────────────────────────────────────────────────

def _resolve(world, typed: List[str]) -> tuple:
    """(the player's marshals named, the names that are not ours to put in an army)."""
    roster = getattr(world, "marshals", None) or {}
    by_low = {str(n).casefold(): str(n) for n in roster}
    by_shown = {humanize_entity_name(str(n)).casefold(): str(n) for n in roster}
    good: List[str] = []
    bad: List[str] = []
    for raw in typed:
        low = str(raw or "").strip().casefold()
        if not low:
            continue
        key = by_low.get(low) or by_shown.get(low)
        if key is not None and _ours(world, roster.get(key)):
            if key not in good:
                good.append(key)
        else:
            bad.append(str(raw).strip())
    return good, bad


def _take_out(world, marshal_names: List[str], keep: str = "") -> List[str]:
    """Take these men out of every army but `keep`; returns what to say of it
    (who left where; an army left empty is dissolved)."""
    said: List[str] = []
    held = getattr(world, "armies", None)
    if not isinstance(held, dict):
        return said
    for name in list(held):
        if name == keep:
            continue
        row = held.get(name) or {}
        before = [str(n) for n in (row.get("members") or [])]
        leaving = [n for n in before if n in marshal_names]
        if not leaving:
            continue
        row["members"] = [n for n in before if n not in marshal_names]
        if row["members"]:
            said.append(f"{_names(leaving)} {'leaves' if len(leaving) == 1 else 'leave'} "
                        f"{shown(name)}.")
        else:
            del held[name]
            said.append(f"{shown(name)[0].upper()}{shown(name)[1:]} has no corps left and is dissolved.")
    return said


def _refused(message: str) -> Dict[str, Any]:
    return {"success": False, "message": message, "said": []}


def _known(world) -> str:
    held = list(store(world))
    if not held:
        return "You have formed no army yet."
    return "Your armies: " + ", ".join(held) + "."


def form(world, name: str, marshal_names: List[str]) -> Dict[str, Any]:
    """Form the army `name` of these men — or, where an army of that name
    exists, give it exactly these men. Returns {success, message, army, said}."""
    if not armies_can_be_named():
        return _refused("Armies cannot be named in this game.")
    kept = find(world, name)
    text = kept or tidy(name)
    if kept is None:
        why = name_refusal(world, text)
        if why:
            return _refused(why)
    good, bad = _resolve(world, marshal_names)
    if bad:
        return _refused(f"{_names(bad)} {'is' if len(bad) == 1 else 'are'} not yours to put in an "
                        "army — name marshals of your own who are not prisoners.")
    if not good:
        return _refused(f"Name the marshals of {shown(text)} — for example “form the {text} "
                        "with Ney and Lannes”.")
    if not isinstance(getattr(world, "armies", None), dict):
        world.armies = {}
    said = _take_out(world, good, keep=text)
    world.armies[text] = {"members": list(good),
                          "formed_turn": int((world.armies.get(text) or {}).get(
                              "formed_turn", getattr(world, "current_turn", 0)) or 0)}
    head = (f"{shown(text)[0].upper()}{shown(text)[1:]} now holds {_names(good)}." if kept
            else f"{shown(text)[0].upper()}{shown(text)[1:]} is formed: {_names(good)}.")
    # how to use it, said once — when the army is new
    how = ([] if kept else [f"Press its chip beside your marshals to select its men, or say "
                            f"“{text}, hold”."])
    return {"success": True, "army": text, "said": said, "formed": kept is None,
            "message": " ".join([head] + said + how)}


def add(world, name: str, marshal_names: List[str]) -> Dict[str, Any]:
    kept = find(world, name)
    if kept is None:
        return _refused(f"There is no army called “{tidy(name)}”. {_known(world)}")
    good, bad = _resolve(world, marshal_names)
    if bad:
        return _refused(f"{_names(bad)} {'is' if len(bad) == 1 else 'are'} not yours to put in an "
                        "army — name marshals of your own who are not prisoners.")
    row = world.armies[kept]
    joining = [n for n in good if n not in row["members"]]
    if not joining:
        return _refused(f"{_names(good) or 'Nobody named'} "
                        f"{'is' if len(good) == 1 else 'are'} already in {shown(kept)}."
                        if good else f"Name who joins {shown(kept)}.")
    said = _take_out(world, joining, keep=kept)
    row["members"] = list(row["members"]) + joining
    head = (f"{_names(joining)} {'joins' if len(joining) == 1 else 'join'} {shown(kept)} "
            f"(now {_names(members(world, kept))}).")
    return {"success": True, "army": kept, "said": said, "message": " ".join([head] + said)}


def remove(world, name: str, marshal_names: List[str]) -> Dict[str, Any]:
    kept = find(world, name)
    if kept is None:
        return _refused(f"There is no army called “{tidy(name)}”. {_known(world)}")
    good, bad = _resolve(world, marshal_names)
    row = world.armies[kept]
    leaving = [n for n in good if n in row["members"]]
    if not leaving:
        # (the review: "Nobody you named is not in …" said the opposite of what
        # happened, and a name that is no marshal of ours was dropped in silence)
        holds = f"{shown(kept)}, which holds {_names(members(world, kept))}"
        if good:
            return _refused(f"{_names(good)} {'is' if len(good) == 1 else 'are'} not in {holds}.")
        if bad:
            said = ", ".join(f"“{b}”" for b in bad)
            return _refused(f"{said} {'is' if len(bad) == 1 else 'are'} not one of your marshals — "
                            f"nobody was taken out of {holds}.")
        return _refused(f"Name a marshal to take out of {holds}.")
    row["members"] = [n for n in row["members"] if n not in leaving]
    if not row["members"]:
        del world.armies[kept]
        return {"success": True, "army": kept, "said": [], "dissolved": True,
                "message": (f"{_names(leaving)} {'leaves' if len(leaving) == 1 else 'leave'} "
                            f"{shown(kept)}; it has no corps left and is dissolved.")}
    return {"success": True, "army": kept, "said": [],
            "message": (f"{_names(leaving)} {'leaves' if len(leaving) == 1 else 'leave'} "
                        f"{shown(kept)} (now {_names(members(world, kept))}).")}


def disband(world, name: str) -> Dict[str, Any]:
    kept = find(world, name)
    if kept is None:
        return _refused(f"There is no army called “{tidy(name)}”. {_known(world)}")
    del world.armies[kept]
    return {"success": True, "army": kept, "said": [], "dissolved": True,
            "message": (f"{shown(kept)[0].upper()}{shown(kept)[1:]} is disbanded. Its corps keep "
                        "their orders and stand where they are.")}


# ── who drops out ───────────────────────────────────────────────────────────

def roll_call(world) -> List[str]:
    """Called where a marshal leaves the roster (he falls, is dismissed, is
    taken prisoner) and as each turn begins: prune the armies and, with the
    wars' goals, write what changed to the campaign log — "the Army of Italy
    has no corps left and is dissolved". Returns the sentences; [] — and
    nothing read or written — on a board with no army and no goal."""
    if not getattr(world, "armies", None) and not getattr(world, "war_goals", None):
        return []
    said: List[str] = []
    try:
        for line in prune(world):
            said.append(line)
            world.log_event({"type": "army_roster", "nation": _player(world),
                             "op": "prune", "army": "", "line": line})
        from backend.game_logic import war_goals
        for line in war_goals.prune(world):
            said.append(line)
            world.log_event({"type": "war_goal", "nation": _player(world), "op": "drop",
                             "against": "", "target": "", "kind": "", "line": line})
    except Exception as exc:
        report(exc, "armies.roll_call")
    return said



def prune(world) -> List[str]:
    """Drop every member who is no longer ours to order (dead, dismissed, a
    prisoner, gone over to another court) and dissolve an army left with
    nobody. Returns what to say of it, one sentence a change; [] — and nothing
    written — when no army exists or nothing changed."""
    held = getattr(world, "armies", None)
    if not isinstance(held, dict) or not held:
        return []
    roster = getattr(world, "marshals", None) or {}
    said: List[str] = []
    for name in list(held):
        row = held.get(name) or {}
        before = [str(n) for n in (row.get("members") or [])]
        still = [n for n in before if _ours(world, roster.get(n))]
        if still == before:
            continue
        gone = [n for n in before if n not in still]
        if still:
            row["members"] = still
            said.append(f"{_names(gone)} {'is' if len(gone) == 1 else 'are'} no longer with "
                        f"{shown(name)} (now {_names(still)}).")
        else:
            del held[name]
            said.append(f"{shown(name)[0].upper()}{shown(name)[1:]} has no corps left and is dissolved.")
    return said
