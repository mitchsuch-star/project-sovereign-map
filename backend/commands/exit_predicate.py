"""DD-0 S4 "The Command Road" — THE EXIT PREDICATE (October 10, 2026;
PRE_DEPLOY_PLAN.md §3.0 "the structural fix"; rules SYSTEMS_REFERENCE.md §104).

One question at the executor's door and again at its exit: *did I act on
the marshal, the place and the arm that were named?* A substitution is
DISCLOSED or REFUSED, never silent. The depth campaign's worst class lived
here — a drill carried out where he stands instead of at the named
province (SFR-D7), cavalry asked and infantry paid (SFR-D41), `drill your
guard` turned into a standing HOLD (SFR-D9) — and every one of them was the
game doing something other than what was typed, without a word.

Two halves, both PURE readers of the command and the result (no lever — the
code-health ratchet holds levers lower-only; every pin reads behaviour):

  place_pre_check   BEFORE the dispatch: a stationary arm (drill, fortify,
                    defend, wait, form square, unfortify) that
                    names a province the marshal does not stand in is
                    refused by name, free, with the two roads that do what
                    was meant — the march first, or the arm where he stands.
                    (The stationary executors never read the target; the
                    order was being carried out where he stood, in silence.)
  disclose          AFTER the executor returns: the command as it entered
                    and as it left (the trace's `command_changed` snapshots)
                    are compared on the marshal, the target and the arm; a
                    value that changed and is not named in the reply is
                    appended to it. The gates that substitute on purpose —
                    the bare attack's pick, the auto-assigned scout, the
                    recruit arm's soft correction — already name their
                    choice, so this is the net under them, not a second
                    sentence over them.

GR6: display and refusal only; nothing here changes a mechanic, a price or
an AP pool. A refusal here spends nothing (`free_action`).
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional

from backend.display_names import humanize_entity_name as _h

# The arms that are carried out WHERE THE MARSHAL STANDS and never read a
# place: a province named in the order is either where he is, or a mistake
# the player must hear about.
# (`garrison` has its own named refusal with the road — CX-R2 — and is not here.)
STATIONARY_ARMS = frozenset({
    "drill", "fortify", "defend", "wait", "form_square", "unfortify",
    # T0-C (CMDFEEL-2, GR-22): the stance verb with a place — "take up a
    # defensive position in Lorraine" shifted the stance where he stood and
    # the province vanished in silence, while "defend Lorraine" refused by
    # name. The unswept sibling of SFR-D7's arms (Rule 10).
    "stance_change",
})

_ARM_WORD = {
    "drill": "a drill is held", "fortify": "the works are dug", "defend": "a defence is stood",
    "wait": "a wait is kept", "form_square": "a square is formed",
    "unfortify": "the works are struck", "garrison": "a garrison is left",
    "stance_change": "a stance is taken",
}
_ARM_VERB = {
    "drill": "drill", "fortify": "fortify", "defend": "defend", "wait": "wait",
    "form_square": "form square", "unfortify": "unfortify", "garrison": "garrison",
}


def _region_key(world, name: Any) -> Optional[str]:
    """The world's region key for a typed place, or None."""
    if not name or not isinstance(name, str):
        return None
    regions = getattr(world, "regions", None)
    if not isinstance(regions, dict):
        return None
    if name in regions:
        return name
    low = name.strip().lower()
    for key in regions:
        if str(key).lower() == low or _h(str(key)).lower() == low:
            return str(key)
    return None


def place_pre_check(command: Dict[str, Any], action: str, world) -> Optional[Dict[str, Any]]:
    """The refusal when a stationary arm names a province the marshal is
    not in; None when the order may proceed. Reads the command AFTER the
    executor resolved its marshal (`command["marshal"]` is a roster name)."""
    if action not in STATIONARY_ARMS or not isinstance(command, dict):
        return None
    if (command.get("_strategic_execution") or command.get("is_strategic")
            or command.get("strategic_type")):
        return None
    target = command.get("target")
    if action == "stance_change" and not command.get("target_stance"):
        # the stance itself rides `target` ("Ney, aggressive") — no place named
        return None
    place = _region_key(world, target)
    if place is None:
        return None
    marshal = None
    get_marshal = getattr(world, "get_marshal", None)
    if callable(get_marshal) and command.get("marshal"):
        marshal = get_marshal(command.get("marshal"))
    if marshal is None:
        return None
    here = getattr(marshal, "location", None)
    if not here or here == place:
        return None
    verb = _ARM_VERB.get(action, action)
    if action == "stance_change":
        stance = str(command.get("target_stance") or "").strip().lower()
        remedy = f"'{marshal.name}, {stance} stance' to take it at {_h(here)}"
    else:
        remedy = f"'{marshal.name}, {verb}' to {verb} at {_h(here)}"
    return {
        "success": False,
        "message": (
            f"{marshal.name} stands at {_h(here)}, not {_h(place)}, Sire — {_ARM_WORD.get(action, 'the order is carried out')} "
            f"where the corps stands. Order '{marshal.name}, move to {_h(place)}' first, or "
            f"{remedy}. Nothing has been relayed."),
        "free_action": True,
        "refusal": "place_mismatch",
        "named_place": place,
        "marshal_place": here,
    }


# UI6-X25 (Session UI-6, Nov 13, 2026): the arms above (and the ones that
# are done where the corps stands: recruit, build, repair, restrain) never
# read an object, so a COMMANDER's name given as the object was dropped in
# silence ("Davout, fortify Kutuzov" dug in at Rhineland). CRT-2's rule: the
# name the sentence gives is acted on or the order is refused free saying
# which name it was read as. His name and side are public; his place is
# never printed.
_COMMANDER_OBJECT_ARMS = STATIONARY_ARMS | frozenset({"recruit", "build", "repair", "restrain"})
_DOES = {
    "drill": ("drills", "drill"), "fortify": ("fortifies", "fortify"),
    "defend": ("defends", "defend"), "wait": ("waits", "wait"),
    "form_square": ("forms square", "form square"), "unfortify": ("unfortifies", "unfortify"),
    "stance_change": ("takes his stance", None), "recruit": ("recruits", "recruit"),
    "build": ("builds", "build"), "repair": ("repairs", "repair"),
    "restrain": ("restrains", "restrain"),
}
_OBJECT_VERBS = frozenset({
    "defend", "fortify", "entrench", "drill", "recruit", "restrain",
    "build", "repair", "wait", "unfortify", "dig", "square"})
_OBJECT_FILLER = frozenset({"at", "the", "marshal", "general", "to", "against", "in", "for",
                            "on", "of", "from", "near", "by"})


def _named_commander(world, command: Dict[str, Any], raw: str, marshal):
    """The roster commander the order's OBJECT names (never the addressee,
    never a province): the parsed target when it is one, else the word(s)
    right after the verb in the player's own line (the parser nulls a
    friend's name, which drops it in silence just the same)."""
    get_marshal = getattr(world, "get_marshal", None)
    if not callable(get_marshal):
        return None

    def _man(text):
        text = str(text or "").strip()
        if not text or _region_key(world, text) is not None:
            return None
        found = get_marshal(text)
        if found is None or getattr(found, "name", None) == getattr(marshal, "name", None):
            return None
        return found

    named = _man(command.get("target"))
    if named is not None:
        return named
    words = re.findall(r"[A-Za-z][A-Za-z'\-]*", raw or "")
    for i, word in enumerate(words):
        if word.lower() in _OBJECT_VERBS:
            rest = [w for w in words[i + 1:] if w.lower() not in _OBJECT_FILLER][:2]
            if len(rest) == 2:
                found = _man(" ".join(rest))
                if found is not None:
                    return found
            return _man(rest[0]) if rest else None
    return None


_RETREAT_PRONOUN_RE = re.compile(
    r"\b(?:retreat|fall\s+back|withdraw|retire|pull\s+back)\s+"
    r"(?:to|toward|towards|into|from)?\s*(?:him|her|them)\b", re.IGNORECASE)


def commander_object_pre_check(command: Dict[str, Any], action: str, world,
                               raw: str = "") -> Optional[Dict[str, Any]]:
    """UI6-X25: the free refusal when a stationary / in-place arm's object is
    a COMMANDER's name rather than a province — "Kutuzov is a commander,
    Sire, not a place — Davout fortifies where he stands; say 'Davout,
    fortify'". It names him and says what was read; it prints no place or
    figure of his. A strategic order, an AI command and the arms that
    legitimately take a marshal (support, follow, pursue, attack) never come
    here."""
    if action == "retreat" and isinstance(command, dict) and not command.get("_strategic_execution"):
        _get = getattr(world, "get_marshal", None)
        _who = _get(command.get("marshal")) if callable(_get) and command.get("marshal") else None
        if _who is None:
            return None
        _named = retreat_destination_commander(
            raw or str(command.get("_raw_input") or ""), world, _who.name)
        if _named is None:
            # UI6-X68: "Mack is attacking Swabia so retreat from him" - the pronoun
            # the clause bound to a commander is no place either ("Mack cannot be
            # reached - no such province" was false).
            _t = command.get("target")
            _tm = _get(_t) if callable(_get) and _t else None
            if (_tm is not None and _tm is not _who and _region_key(world, str(_t)) is None
                    and _RETREAT_PRONOUN_RE.search(raw or str(command.get("_raw_input") or ""))):
                _named = _tm
        if _named is None:
            return None
        return retreat_commander_refusal(_named, _h(_who.name), f"{_h(_who.name)}, retreat")
    if action not in _COMMANDER_OBJECT_ARMS or not isinstance(command, dict):
        return None
    if (command.get("_strategic_execution") or command.get("is_strategic")
            or command.get("strategic_type")):
        return None
    if action == "stance_change" and not command.get("target_stance"):
        return None
    get_marshal = getattr(world, "get_marshal", None)
    if not callable(get_marshal) or not command.get("marshal"):
        return None
    marshal = get_marshal(command.get("marshal"))
    if marshal is None:
        return None
    named = _named_commander(world, command, raw, marshal)
    if named is None:
        return None
    does, say = _DOES.get(action, ("acts", None))
    mine = _h(marshal.name)
    remedy = f"; say '{mine}, {say}'" if say else ""
    return {
        "success": False,
        "message": (f"{_h(named.name)} is a commander, Sire, not a place — {mine} {does} "
                    f"where he stands{remedy}. Nothing has been relayed."),
        "free_action": True,
        "variable_action_cost": 0,
        "refusal": "commander_not_a_place",
    }


_ARM_LABELS = ("infantry", "cavalry", "artillery")


def _names(message: str, value: Any) -> bool:
    if value is None:
        return True
    text = str(message or "").lower()
    v = str(value).strip().lower()
    if not v or v == "generic":
        return True
    if v in text or _h(str(value)).lower() in text:
        return True
    # the surname alone ("Archduke John" → "John")
    last = v.split()[-1] if " " in v else None
    return bool(last and re.search(r"\b" + re.escape(last) + r"\b", text))


def disclose(entered: Optional[Dict[str, Any]], exited: Optional[Dict[str, Any]],
             result: Any, world=None) -> Optional[str]:
    """The sentence appended to a reply whose executor changed the marshal,
    the target or the arm without naming the change — or None. PURE."""
    if (not isinstance(result, dict) or not isinstance(entered, dict)
            or not isinstance(exited, dict)):
        return None
    if result.get("success") is not True:
        return None
    message = str(result.get("message") or "")
    clauses = []
    for key, noun in (("marshal", "the order went to"), ("target", "it was carried out against")):
        before, after = entered.get(key), exited.get(key)
        if after in (None, "", "generic") or before == after:
            continue
        if _names(message, after):
            continue
        if before in (None, "", "generic"):
            clauses.append(f"{noun} {_h(after)}")
        else:
            clauses.append(f"you named {_h(before)} and {noun} {_h(after)}")
    # the recruit arm: the player asked for one arm and the levy raised another
    asked = entered.get("requested_type")
    if (str(entered.get("action") or exited.get("action") or "") == "recruit"
            and asked and str(asked).lower() in _ARM_LABELS
            and str(asked).lower() not in message.lower()
            and not any(a in message.lower() for a in _ARM_LABELS)):
        clauses.append(f"you asked for {asked} and the levy was of another arm")
    if not clauses:
        return None
    return "Berthier: \"" + "; ".join(clauses) + ".\""


# UI6-X39 (Session UI-6, Nov 13, 2026): the X25 family for the retreat. "Ney,
# retreat to Kutuzov" fell back to Lorraine and said "Kutuzov cannot be
# reached … no such province"; "all corps retreat to Kutuzov" ran the general
# retreat and dropped the name. A COMMANDER given as the retreat's
# destination is refused free in X25's words (he is named, his side is
# public, his place is never printed). A reason word before him ("for",
# "considering") is no destination at all - `clause_guards.purpose_tail_spans`
# blanks it, so the retreat is the plain one.
# UI6-X42: the object needs no "to" - "retreat Kutuzov", "retreat from Mack",
# "fall back Kutuzov", "withdraw Kutuzov" name the same commander, and are
# refused the same way (never read as his place, never a silent plain retreat).
_RETREAT_DEST_RE = re.compile(
    r"\b(?:retreat|fall\s+back|withdraw|retire|pull\s+back)\s+"
    r"(?:(?:to|toward|towards|into|from)\s+)?(?P<rest>[^,;.!?]*)", re.IGNORECASE)


_RETREAT_TO_RE = re.compile(
    r"\b(?:retreat|fall\s+back|withdraw|retire|pull\s+back)\s+"
    r"(?:from\s+[^,;.!?]*?\s+)?(?:to|toward|towards|into)\s+"
    r"(?P<rest>[^,;.!?]*)", re.IGNORECASE)


def retreat_stated_destination(raw: str) -> Optional[str]:
    """UI6-X64: the destination a retreat line STATES ("retreat to Zorglub") when
    the parse bound none - so W6-1's substitution note names what was typed
    ("Zorglub cannot be reached, Sire - no such province is known to the staff;
    Ney falls back to Lorraine instead") instead of retreating in silence. The
    first word or two after to / toward / into; None when the line states none."""
    if not raw:
        return None
    found = _RETREAT_TO_RE.search(str(raw))
    if found is None:
        return None
    from backend.commands.proper_name import object_words
    words = object_words(found.group("rest"))
    while words and words[0].lower() in {"the", "a"}:
        words = words[1:]
    if not words:
        return None
    return " ".join(words[:2]) if len(words) > 1 and words[1][:1].isupper() else words[0]


class _SharedTitle:
    """UI6-X42: a title two commanders bear ("Archduke") named as a retreat's
    object - stands in for the commander in the refusal; names no man."""
    is_title = True

    def __init__(self, word: str):
        self.name = word


_RETREAT_FROM_RE = re.compile(
    r"\b(?:retreat|fall\s+back|withdraw|retire|pull\s+back)\s+from\s+(?P<rest>[^,;.!?]*)",
    re.IGNORECASE)


_FROM_REST_CUT_RE = re.compile(r"\s+\b(?:to|toward|towards|into)\b", re.IGNORECASE)


def _from_words(raw: str):
    """UI6-X67: the words of a retreat's FROM-phrase ("retreat from Swabia to
    Lorraine" -> ["Swabia"]), articles dropped; [] when the line has none."""
    found = _RETREAT_FROM_RE.search(str(raw or ""))
    if found is None:
        return []
    from backend.commands.proper_name import object_words
    words = object_words(found.group("rest"))
    while words and words[0].lower() in {"the", "a", "an", "his", "our"}:
        words = words[1:]
    return words


def retreat_from_region(raw: str, world) -> Optional[str]:
    """UI6-X67: the province a retreat's from-phrase names, or None."""
    words = _from_words(raw)
    for k in range(min(len(words), 3), 0, -1):
        place = _region_key(world, " ".join(words[:k]))
        if place is not None:
            return place
    return None


def _a_court_or_a_commander(world, words) -> bool:
    """A from-phrase naming a court ("retreat from Austria" - its soil, read as a
    plain retreat) or a commander (the commander refusal reads him first)."""
    said = {" ".join(words[:k]).lower() for k in range(1, min(len(words), 2) + 1)}
    for m in (getattr(world, "marshals", None) or {}).values():
        if str(m.name).lower() in said or _h(str(m.name)).lower() in said:
            return True
    _active = getattr(world, "get_active_nations", None)
    keys = list(_active()) if callable(_active) else []
    keys += list(getattr(world, "enemy_nations", None) or []) + [getattr(world, "player_nation", "") or ""]
    from backend.display_names import display_nation
    for key in keys:
        if key and (str(key).lower() in said or _h(str(key)).lower() in said
                    or str(display_nation(key)).lower() in said):
            return True
    return False


def retreat_from_pre_check(command: Dict[str, Any], action: str, world,
                           raw: str = "") -> Optional[Dict[str, Any]]:
    """UI6-X67 (Session UI-6's last verifier: UI6-X59 still retreated): "retreat
    from <a province he is not in>" is refused FREE, as `place_pre_check`
    refuses a stationary order at a province he is not in - a retreat costs the
    corps its effectiveness for three turns, so it is never run on a misread;
    "retreat from Lorraine" had sent him INTO Lorraine. A proper name that is no
    province ("retreat from Zorglub") is refused naming it. His own province, a
    lowercase phrase ("from the enemy", "from here") and a court's name are a
    plain retreat; a commander is the commander refusal's (`commander_object_pre_check`
    reads first). Prints his own place only - never anyone else's."""
    if action != "retreat" or not isinstance(command, dict) or command.get("_strategic_execution"):
        return None
    _get = getattr(world, "get_marshal", None)
    who = _get(command.get("marshal")) if callable(_get) and command.get("marshal") else None
    if who is None:
        return None
    text = raw or str(command.get("_raw_input") or "")
    words = _from_words(text)
    if not words:
        return None
    here = getattr(who, "location", None)
    name = _h(who.name)
    place = retreat_from_region(text, world)
    if place is None:
        if not words[0][:1].isupper() or _a_court_or_a_commander(world, words):
            return None
        typed = " ".join(words[:2]) if len(words) > 1 and words[1][:1].isupper() else words[0]
        return {
            "success": False,
            "message": (f"No province called '{typed}' is known to the staff, Sire — {name} "
                        f"stands at {_h(here)}; say '{name}, retreat' to fall back from there. "
                        f"Nothing has been relayed."),
            "free_action": True,
            "variable_action_cost": 0,
            "refusal": "retreat_from_unknown",
        }
    if not here or place == here:
        return None
    return {
        "success": False,
        "message": (f"{name} stands at {_h(here)}, not {_h(place)}, Sire — a retreat falls back "
                    f"from where the corps stands. Say '{name}, retreat' to fall back from "
                    f"{_h(here)}. Nothing has been relayed."),
        "free_action": True,
        "variable_action_cost": 0,
        "refusal": "retreat_from_elsewhere",
        "named_place": place,
        "marshal_place": here,
    }


def retreat_from_place(raw: str, target) -> Optional[str]:
    """UI6-X59: the `target` a retreat parse bound when the player typed
    "retreat from <it>" - the place he falls back FROM, not a destination -
    else None (also None for a commander: the commander refusal keeps that)."""
    if not raw or not target:
        return None
    found = _RETREAT_FROM_RE.search(str(raw))
    if found is None:
        return None
    # UI6-X67: the from-phrase ends at its destination's preposition ("retreat
    # from Rhineland to Lorraine" falls back FROM Rhineland, TO Lorraine).
    rest = _FROM_REST_CUT_RE.split(found.group("rest"), maxsplit=1)[0].lower()
    shown = str(target).lower()
    if shown in rest or _h(str(target)).lower() in rest:
        return str(target)
    return None


def retreat_destination_commander(raw: str, world, addressee: Optional[str] = None):
    """The roster commander a retreat's DESTINATION names ("retreat to
    Kutuzov" / "fall back to Archduke John" / "withdraw to Davout"), or None.
    Matched on the key and the printed form; a province of that name is the
    province (never here); the addressee never counts."""
    if world is None or not raw:
        return None
    found = _RETREAT_DEST_RE.search(raw)
    if found is None:
        return None
    from backend.commands.proper_name import object_words
    words = object_words(found.group("rest"))
    while words and words[0].lower() in {"the", "marshal", "general", "gen"}:
        words = words[1:]
    if not words or _region_key(world, " ".join(words)) is not None:
        return None
    forms: Dict[str, Any] = {}
    for m in (getattr(world, "marshals", None) or {}).values():
        if getattr(m, "name", None) == addressee:
            continue
        for form in (m.name, _h(m.name)):
            forms.setdefault(str(form).lower(), m)
    for k in range(len(words), 0, -1):
        hit = forms.get(" ".join(words[:k]).lower())
        if hit is not None:
            return hit
    if len(words) == 1 and len(words[0]) >= 3:
        # a title two men share ("Archduke") is no place either, and no man
        tokens: Dict[str, int] = {}
        for m in (getattr(world, "marshals", None) or {}).values():
            for w in set(re.findall(r"[a-z']+", _h(m.name).lower())):
                tokens[w] = tokens.get(w, 0) + 1
        if tokens.get(words[0].lower(), 0) > 1:
            return _SharedTitle(words[0])
    return None


def retreat_commander_refusal(named, who: str, say: str) -> Dict[str, Any]:
    """The free refusal of a retreat whose destination is a commander."""
    if getattr(named, "is_title", False):
        return {
            "success": False,
            "message": (f"{_h(named.name)} is a title more than one commander bears, Sire, "
                        f"not a place — {who} falls back to safe ground of his own choosing; "
                        f"name a province, or say '{say}'. Nothing has been relayed."),
            "free_action": True,
            "variable_action_cost": 0,
            "refusal": "commander_not_a_place",
        }
    return {
        "success": False,
        "message": (f"{_h(named.name)} is a commander, Sire, not a place — {who} falls back "
                    f"to safe ground of his own choosing; name a province, or say '{say}'. "
                    f"Nothing has been relayed."),
        "free_action": True,
        "variable_action_cost": 0,
        "refusal": "commander_not_a_place",
    }
