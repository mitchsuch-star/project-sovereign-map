"""Row IC, Session 2 (IC-9) — EXACT ORDERS: the if-thens a standing order carries.

`docs/INDEPENDENT_COMMAND_SPEC.md` §7 (version 6). "Bold and careful men act on
their own. A literal man gets it to the letter." A standing order may carry a
short LIST of if-thens — `StrategicOrder.if_thens` — which the man follows
exactly, after the enemy has moved, each line once:

    "Soult, hold Lorraine. If attacked, dig in. If outnumbered, fall back on
     Champagne."

A literal marshal's order (any standing order) carries up to THREE; any other
marshal's carries ONE, on a hold (the rule the single "contingency" of CC-4 /
D8 had, which this list replaces — an old save's contingency loads as a
one-line list).

THE EIGHT IFS (each reads only what his own nation can SEE):
    enemy_near       an enemy — or a NAMED enemy — comes within reach
    attacked         he is attacked (optionally: by a named enemy)
    outnumbered      fewer men than the enemy within reach
    surrounded       enemy corps in two or more provinces next to him, and no
                     friend next to him
    friend_attacked  a named friend is attacked next to him
    place_falls      a named place falls
    friend_arrives   a named friend comes within one march of him

THE FIVE THENS:
    attack           the enemy that tripped the line, failing that the weakest
                     he can see — and only if he is NOT outnumbered, unless the
                     line says "whatever the odds"
    fall_back / march   to a named place
    join             the friend's battle (the arrival roll, with the order's
                     own weight — `combat_executor`)
    dig_in           fortify where he stands

WORDS, DEFINED (§7). Within reach: his province and the ones next to it (two
provinces for horse), seen ones only. A force under a FIFTH of his own strength
trips nothing (forces in one province are added together) — but a line that
NAMES a marshal fires on that marshal whatever his strength. A line is LIVE
from the turn after it is written, is USED once, and sleeps on a turn he was
given an order by hand (one thing a turn).

This module is the grammar (`read`), the wording (`describe`), the rules
(`settle`) and the triggers (`ready`). The strategic pass fires what `ready`
returns (`strategic.StrategicOrderProcessor._if_thens_pass`). PURE: nothing
here writes to the board, and no die is cast.
"""
from __future__ import annotations

import functools
import re
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from backend.ai import task_words as TW
from backend.ai.clause_guards import HONORIFIC
from backend.display_names import humanize_entity_name
from backend.errors import report

LITERAL_LINES = 3      # a literal marshal's standing order
OTHER_LINES = 1        # anyone else's, on a hold
ATTACK_LINES = 1       # at most one line an order may attack
FLOOR_DIVISOR = 5      # a force under a fifth of his strength trips nothing

IFS = ("enemy_near", "attacked", "outnumbered", "surrounded", "friend_attacked",
       "place_falls", "friend_arrives")
THENS = ("attack", "fall_back", "march", "join", "dig_in")
_MOVING = ("fall_back", "march")


# ═══════════════════════════ the lines of an order ══════════════════════════

def ordered_by_hand(world, marshal_name, action, command, result) -> None:
    """ONE THING A TURN (§7): a man given an order BY HAND today lets the
    if-thens of his standing order sleep this turn — `last_ordered_turn`.
    Today's order is one that reached him and was CARRIED OUT: never the
    game's own carrying-out of a standing order, a read, "stay put", an
    administrative act that merely names him (a pension, a recruit, a
    garrison — the review, S2), or an order he has only been ASKED about (an
    objection still standing). ONE writer: the executor's close and the
    order carried out after an objection (S3) both call it."""
    from backend.ai.validation import ADMINISTRATIVE_ACTIONS, NON_ORDER_ACTIONS
    command = command if isinstance(command, dict) else {}
    if not marshal_name or not isinstance(result, dict) or not result.get("success"):
        return
    if (result.get("state") in ("awaiting_player_choice", "awaiting_clarification")
            or result.get("requires_input") or result.get("pending_glorious_charge")):
        return
    if (command.get("_strategic_execution") or command.get("_jealousy_autonomous")
            or command.get("_autonomous_execution")):
        return
    if action in NON_ORDER_ACTIONS or action in ADMINISTRATIVE_ACTIONS or action == "wait":
        return
    if action == "own_task":
        return      # row IC, Session 3: "stand down", "carry on", "more risk" — no order today
    man = world.get_marshal(str(marshal_name)) if world is not None else None
    if man is not None and man.nation == getattr(world, "player_nation", None):
        first_today = int(getattr(man, "last_ordered_turn", -1) or -1) != int(world.current_turn)
        man.last_ordered_turn = int(world.current_turn)
        if first_today:
            _overruled(world, man, result)


def _overruled(world, man, result) -> None:
    """Row IC, Session 4 (IC-13; §11 "being given today's order over his own"):
    a man with a task of his own — on his own, or a literal man under exact
    orders — who is given TODAY'S ORDER by hand says so, once a turn, in his
    own words; a man who remembers being overruled keeps it (`own_voice.
    REMEMBERS`). The line rides the reply (`voices`); it changes nothing."""
    try:
        from backend.game_logic import own_order as _own
        from backend.game_logic import own_voice as _voice
        order = getattr(man, "strategic_order", None)
        on_task = _own.on_his_own(man) or (
            getattr(man, "personality", "") == "literal" and bool(lines(order)))
        if not on_task:
            return
        # ... a task he ALREADY had: the order that gives him his task today is
        # not an order over it.
        given = getattr(order, "issued_turn", None)
        if given is None:
            given = getattr(order, "started_turn", None)
        if given is None or int(given) >= int(world.current_turn):
            return
        said = _voice.speak(world, man, "overruled")
        _voice.note_memory(world, man, "overruled")
        if said and isinstance(result, dict):
            result.setdefault("voices", []).append({"speaker": man.name, "says": said})
    except Exception as exc:
        report(exc, "if_thens._overruled")


def lines(order) -> List[Dict[str, Any]]:
    """The order's if-thens (a list, possibly empty) — never None."""
    return list(getattr(order, "if_thens", None) or []) if order is not None else []


def unused(order) -> List[Dict[str, Any]]:
    return [ln for ln in lines(order) if not ln.get("used")]


def is_live(line: Dict[str, Any], turn: int) -> bool:
    """Unused, and written before this turn (§7: a line arms one turn after
    it is written — nothing fires on the turn it is given)."""
    if line.get("used"):
        return False
    written = line.get("written")
    return written is None or int(turn) > int(written)


def left_words(order) -> str:
    """"2 of 3 left" — what his piece and the Orders tab say; "" for no list."""
    all_lines = lines(order)
    if not all_lines:
        return ""
    return f"{len(unused(order))} of {len(all_lines)} left"


def from_legacy(contingency: Dict[str, Any]) -> Dict[str, Any]:
    """An old save's single contingency (CC-4 / D8: `{who, then, to, clause}`)
    as a line — already live (it was written before the save)."""
    return make_line("enemy_near", who=contingency.get("who"),
                     then=("attack" if contingency.get("then") == "attack" else "fall_back"),
                     to=contingency.get("to"), clause=str(contingency.get("clause") or ""),
                     written=None)


def make_line(if_: str, *, then: str, who: Optional[str] = None, friend: Optional[str] = None,
              place: Optional[str] = None, to: Optional[str] = None, any_odds: bool = False,
              clause: str = "", written: Optional[int] = None) -> Dict[str, Any]:
    return {"if": if_, "who": who or None, "friend": friend or None, "place": place or None,
            "then": then, "to": to or None, "any_odds": bool(any_odds),
            "clause": str(clause or ""), "used": False, "written": written}


def same_watch(a: Sequence[Dict[str, Any]], b: Sequence[Dict[str, Any]]) -> bool:
    """Two lists do the same things (compared by what they do, not their
    words) — the F10 "already carrying out that order" rule's reading."""
    def key(line):
        return (line.get("if"), line.get("who"), line.get("friend"), line.get("place"),
                line.get("then"), line.get("to"), bool(line.get("any_odds")))
    return [key(x) for x in (a or [])] == [key(x) for x in (b or [])]


# ═══════════════════════════ the wording ════════════════════════════════════

def describe_if(line: Dict[str, Any],
                shown: Callable[[str], str] = humanize_entity_name) -> str:
    kind = line.get("if")
    who, friend, place = line.get("who"), line.get("friend"), line.get("place")
    if kind == "enemy_near":
        return f"if {shown(who)} comes within reach" if who else "if the enemy comes within reach"
    if kind == "attacked":
        return f"if {shown(who)} attacks him" if who else "if he is attacked"
    if kind == "outnumbered":
        return "if he is outnumbered"
    if kind == "surrounded":
        return "if he is being surrounded"
    if kind == "friend_attacked":
        return f"if {shown(friend)} is attacked next to him"
    if kind == "place_falls":
        return f"if {shown(place)} falls"
    if kind == "friend_arrives":
        return f"if {shown(friend)} arrives"
    return "if …"


def describe_then(line: Dict[str, Any],
                  shown: Callable[[str], str] = humanize_entity_name) -> str:
    then = line.get("then")
    if then == "attack":
        return "attack whatever the odds" if line.get("any_odds") else "attack"
    if then == "fall_back":
        return f"fall back to {shown(str(line.get('to') or ''))}"
    if then == "march":
        return f"march to {shown(str(line.get('to') or ''))}"
    if then == "join":
        return "join his battle"
    if then == "dig_in":
        return "dig in"
    return "…"


def describe(line: Dict[str, Any], shown: Callable[[str], str] = humanize_entity_name) -> str:
    """The ONE phrase for a line — the read-back, the confirmation, the Orders
    tab and the map's badge read it ("if Mack comes within reach, fall back to
    Lorraine"). Every phrase it writes is one `read` takes back (the census)."""
    # (the review, L6: every name — a commander's, a province's — as the game prints it)
    return f"{describe_if(line, shown)}, {describe_then(line, shown)}"


def badge_words(order, shown: Callable[[str], str] = humanize_entity_name) -> str:
    """The map badge's few words for an order's if-thens — the first UNUSED
    line's own IF, short, and how many more wait behind it: "if he is
    attacked · +1 more"; "if Mack comes"; "" for an order with none left. (The
    badge used to say "if <whom> comes" of every line: "if the enemy comes" of
    "if he is attacked", "if Rhineland comes" of a place that falls — found in
    the real client.)"""
    live = unused(order)
    if not live:
        return ""
    first = live[0]
    kind = first.get("if")
    if kind == "enemy_near":
        said = f"if {shown(first['who'])} comes" if first.get("who") else "if the enemy comes"
    elif kind == "friend_attacked":
        said = f"if {shown(first.get('friend') or '')} is attacked"
    else:
        said = describe_if(first, shown)
    more = len(live) - 1
    return said + (f" · +{more} more" if more > 0 else "")


def describe_all(order, shown: Callable[[str], str] = humanize_entity_name,
                 only_unused: bool = False) -> str:
    """Every line of the order, in order: "if he is attacked, dig in; if he is
    outnumbered, fall back to Champagne" — a used line says so."""
    out = []
    for line in lines(order):
        if line.get("used"):
            if not only_unused:
                out.append(f"{describe(line, shown)} (used)")
        else:
            out.append(describe(line, shown))
    return "; ".join(out)


def sentence(line: Dict[str, Any], shown: Callable[[str], str] = humanize_entity_name) -> str:
    """A line as a typed sentence: "If he is attacked, dig in." """
    text = describe(line, shown)
    return text[:1].upper() + text[1:] + "."


# ═══════════════════════════ the grammar ════════════════════════════════════

def _phrase_regex(phrase: str) -> str:
    """A flat table phrase as a regex source: words joined by whitespace, a
    slot a lazy named group."""
    parts = []
    for word in phrase.split():
        slot = re.fullmatch(r"\{(\w+)\}", word)
        parts.append(f"(?P<{slot.group(1)}>.+?)" if slot else re.escape(word))
    return r"\s+".join(parts)


_IF_RX = [(name, slot, re.compile(_phrase_regex(text), re.IGNORECASE))
          for name, slot, text in TW.IF_PHRASES]
_SHOULD_RX = [(name, slot, re.compile(_phrase_regex(text), re.IGNORECASE))
              for name, slot, text in TW.IF_SHOULD_PHRASES]
_THEN_RX = [(name, any_odds,
             re.compile(r"^(?P<if>.+?)(?:\s*,\s*|\s+)(?:then\s+)?(?P<then>" + _phrase_regex(text)
                        + r")$", re.IGNORECASE))
            for name, any_odds, text in TW.THEN_PHRASES]
_MARKER_SRC = "|".join(re.escape(m).replace(r"\ ", r"\s+") for m in
                       sorted(TW.IF_MARKERS, key=len, reverse=True))
_MARKER_RE = re.compile(r"^(?:and\s+)?(?P<marker>" + _MARKER_SRC + r")\b\s*", re.IGNORECASE)
# A new segment opens at a sentence end, or at a comma / "and" before a marker.
_SEGMENT_RE = re.compile(
    r"\s*[.;!]+\s*|\s*,\s*(?:and\s+)?(?=(?:" + _MARKER_SRC + r")\b)"
    r"|\s+and\s+(?=(?:" + _MARKER_SRC + r")\b)", re.IGNORECASE)
_ADDRESS_RE = re.compile(r"^\s*(?P<addr>[^,.;:!?]+?)\s*,\s*(?P<rest>.+?)\s*$", re.DOTALL)


def _name_forms(name: str) -> set:
    forms = {str(name).lower(), humanize_entity_name(str(name)).lower()}
    try:
        from backend.ai.llm_client import name_match_patterns
        forms.update(str(f).lower() for f in name_match_patterns(str(name)))
    except Exception as exc:  # pragma: no cover — a cold unit call
        report(exc, "if_thens._name_forms: name_match_patterns")
    return forms


def _resolve_name(text: str, names: Sequence[str]) -> Optional[str]:
    low = re.sub(r"^(?:the\s+)?(?:" + HONORIFIC + r")?", "", str(text or "").strip(),
                 flags=re.IGNORECASE).strip().lower()
    if not low:
        return None
    for name in names or ():
        if low in _name_forms(name):
            return str(name)
    return None


def _resolve_place(text: str, places: Sequence[str]) -> Optional[str]:
    low = re.sub(r"^the\s+", "", str(text or "").strip(), flags=re.IGNORECASE).lower()
    for place in places or ():
        if low in (str(place).lower(), humanize_entity_name(str(place)).lower()):
            return str(place)
    return None


def _read_line(segment: str, friends, enemies, places, addressee: str
               ) -> Tuple[Optional[Dict[str, Any]], str]:
    """`(line, "")` for one "if …, then …" segment, or `(None, why)`."""
    return _read_line_ours(segment, friends, enemies, places, addressee)[:2]


def _read_line_ours(segment: str, friends, enemies, places, addressee: str
                    ) -> Tuple[Optional[Dict[str, Any]], str, bool]:
    """`_read_line`, with whether the segment is an exact order's line AT ALL
    — its answer is one of the five (attack, fall back on a place, march to a
    place, join his battle, dig in), whatever then failed. A segment whose
    answer is none of them ("if he retreats, pursue him into Vienna") is the
    old readers' sentence."""
    opened = _MARKER_RE.match(segment)
    if opened is None:
        return None, "it opens with no 'if'", False
    marker = re.sub(r"\s+", " ", opened.group("marker").lower())
    body = segment[opened.end():].strip().rstrip(".!").strip()
    if not body:
        return None, "it names no condition", False
    if_table = _SHOULD_RX if marker == "should" else _IF_RX
    why = ""
    ours = False
    for then_name, any_odds, then_rx in _THEN_RX:
        split = then_rx.match(body)
        if split is None:
            continue
        ours = True
        if_text = split.group("if").strip(" ,")
        to = None
        if then_name in _MOVING:
            to = _resolve_place(split.group("place"), places)
            if to is None:
                why = why or f"'{split.group('place').strip()}' is no province on the map"
                continue
        for if_name, slot, if_rx in if_table:
            found = if_rx.fullmatch(if_text)
            if found is None:
                continue
            who = friend = place = None
            if slot == "enemy":
                who = _resolve_name(found.group("enemy"), enemies)
                if who is None:
                    why = why or f"no enemy commander is called '{found.group('enemy').strip()}'"
                    continue
            elif slot == "friend":
                friend = _resolve_name(found.group("friend"), friends)
                if friend is None or friend == addressee:
                    why = why or f"'{found.group('friend').strip()}' is not another marshal of ours"
                    continue
            elif slot == "place":
                place = _resolve_place(found.group("place"), places)
                if place is None:
                    why = why or f"'{found.group('place').strip()}' is no province on the map"
                    continue
            if then_name not in TW.THENS_FOR.get(if_name, ()):
                why = why or _mismatch(if_name, then_name)
                continue
            return make_line(if_name, then=then_name, who=who, friend=friend, place=place,
                             to=to, any_odds=any_odds, clause=segment.strip()), "", True
        why = why or "that is no condition he can watch for"
    return None, (why or "that is no answer he can give — attack, fall back on a place, "
                  "march to a place, join a friend's battle, or dig in"), ours


def _mismatch(if_name: str, then_name: str) -> str:
    if then_name == "join":
        return "'join his battle' answers 'if <a friend> is attacked next to him'"
    if if_name == "outnumbered" and then_name == "attack":
        return "an attack line is carried out only when he is not outnumbered — fall back or dig in instead"
    return "that answer does not fit that condition"


def read(text: str, friends: Sequence[str], enemies: Sequence[str], places: Sequence[str]
         ) -> Optional[Dict[str, Any]]:
    """A typed line as an EXACT ORDER, or None when it carries no if-then.

    ``{"addressee", "address", "order", "implicit_hold", "lines", "unread"}``:
    `order` is the order's own words with the if-thens taken out ("hold
    Lorraine"; "hold" when the line is only if-thens — he holds where he
    stands, CC-4 / D8's rule), `lines` the if-thens read, `unread` the
    `(clause, why)` of every segment that opens with an if-word but is no line
    this grammar takes.

    None when: nobody of ours is addressed before the first comma; no segment
    opens with if / when / should / in case; or more than one segment is an
    order (two orders in a line are the relay's). A line whose ONLY content is
    one unreadable if-segment also returns None — the clause guard then
    refuses it exactly as it always has ("Ney, if Mack advances, fall back to
    Narnia") — and so does a line that took NO if-then and whose if-segments
    answer with none of the five thens ("Massena, attack John; if he
    retreats, pursue him into Vienna": the relay gives the attack and offers
    the rest back, as it always did). PURE (names handed in)."""
    found = _ADDRESS_RE.match(text or "")
    if found is None:
        return None
    addr = found.group("addr").strip()
    addressee = _resolve_name(addr, friends)
    if addressee is None:
        return None
    segments = [s.strip() for s in _SEGMENT_RE.split(found.group("rest")) if s and s.strip()]
    orders = [s for s in segments if _MARKER_RE.match(s) is None]
    candidates = [s for s in segments if _MARKER_RE.match(s) is not None]
    if not candidates or len(orders) > 1:
        return None
    taken: List[Dict[str, Any]] = []
    unread: List[Tuple[str, str]] = []
    any_ours = False
    for segment in candidates:
        line, why, ours = _read_line_ours(segment, friends, enemies, places, addressee)
        any_ours = any_ours or ours
        if line is None:
            unread.append((segment.rstrip(".!").strip(), why))
        else:
            taken.append(line)
    if not taken and not orders:
        return None       # one unreadable conditional: the guard's refusal, as before
    if not taken and not any_ours:
        return None       # no answer of the five anywhere: the old readers' sentence
    return {"addressee": addressee, "address": addr,
            "order": (orders[0].rstrip(".!").strip() if orders else "hold"),
            "implicit_hold": not orders, "lines": taken, "unread": unread}


def restate(address: str, order: str, taken: Sequence[Dict[str, Any]],
            shown: Callable[[str], str] = humanize_entity_name) -> str:
    """The line as understood: "Soult, hold Lorraine. If he is attacked, dig
    in." — what "Send what I understood" sends, and `read` takes back."""
    head = f"{address}, {order}".rstrip(". ")
    if not taken:
        return head
    return head + ". " + " ".join(sentence(line, shown) for line in taken)


# ═══════════════════════════ the new task words (IC-8) ══════════════════════

_ARRIVAL_ALIASES = {phrase: verb for phrase, verb in TW.ARRIVAL_THENS.items() if phrase != verb}
# The alias stands right behind "then" / "and" / a stop, and ends at a word's
# edge — whatever follows it (a stop, a reason, an aside: "…then dig in — at
# once") is the other readers' to peel.
_ARRIVAL_ALIAS_RE = (re.compile(
    r"((?:\b(?:and\s+)?then\b|\band\b|;|,)\s*)(" + "|".join(
        re.escape(p).replace(r"\ ", r"\s+") for p in sorted(_ARRIVAL_ALIASES, key=len, reverse=True))
    + r")(?![\w'’-])", re.IGNORECASE) if _ARRIVAL_ALIASES else None)
# "march to" and its kin — the head a "then dig in" must stand behind.
_MARCH_HEAD_RE = re.compile(r"\b(?:march|advance|proceed|head|move|go)\s+(?:to|on|for|toward|towards)\b",
                            re.IGNORECASE)


def restate_task_words(text: str, friends: Sequence[str], places: Sequence[str]) -> str:
    """IC-8: the word table's NEW task words, restated as the table words they
    mean before any reader sees the line — "Davout, keep Lorraine" is "hold
    Lorraine", "Soult, stay with Ney" is "follow Ney", and a march's "then dig
    in" is "then fortify". Each only before the kind of object its task takes
    (`task_words.TASK_REWRITES`): "keep an eye on Swabia" stays a scout, "keep
    marching" stays itself. The text is returned unchanged otherwise. PURE."""
    if not text:
        return text
    out = text
    for word, means, takes in TW.TASK_REWRITES:
        if not re.search(r"\b" + re.escape(word.split()[0]) + r"\b", out, re.IGNORECASE):
            continue
        # The object is the NAME that stands right behind the word — whatever
        # follows the name (a reason, an aside, "with Lannes in support") is
        # the other readers' to peel, as it is behind "hold Lorraine".
        named = (_names_rx(tuple(places or ()), False) if takes == "place"
                 else _names_rx(tuple(friends or ()), True))
        if named is None:
            continue
        head = re.compile(r"\b" + re.escape(word).replace(r"\ ", r"\s+") + r"(?=\s)", re.IGNORECASE)
        pieces, at = [], 0
        for found in head.finditer(out):
            gap = re.match(r"\s+", out[found.end():])
            if gap is None or named.match(out, found.end() + gap.end()) is None:
                continue
            pieces.append(out[at:found.start()] + means)
            at = found.end()
        out = "".join(pieces) + out[at:]
    if _ARRIVAL_ALIAS_RE is not None and _MARCH_HEAD_RE.search(out):
        found = _ARRIVAL_ALIAS_RE.search(out)
        if found is not None:
            phrase = re.sub(r"\s+", " ", found.group(2).lower())
            out = out[:found.start()] + found.group(1) + _ARRIVAL_ALIASES[phrase] + out[found.end():]
    return out


@functools.lru_cache(maxsize=16)
def _names_rx(names: tuple, people: bool):
    """A matcher for one of `names` standing at a position (longest first, to a
    word's edge) — a province by its key or its shown name; one of our men by
    any form his name is typed in, an honorific allowed. None for no names."""
    forms: set = set()
    for name in names:
        if people:
            forms.update(_name_forms(name))
        else:
            forms.update({str(name).lower(), humanize_entity_name(str(name)).lower()})
    forms.discard("")
    if not forms:
        return None
    source = "|".join(re.escape(f).replace(r"\ ", r"\s+")
                      for f in sorted(forms, key=len, reverse=True))
    lead = (r"(?:" + HONORIFIC + r")?") if people else r"(?:the\s+)?"
    return re.compile(lead + r"(?:" + source + r")(?![\w'’-])", re.IGNORECASE)


# ═══════════════════════════ how bold (IC-8) ════════════════════════════════

_RISK_SRC = "|".join(
    re.escape(p).replace(r"\ ", r"\s+").replace("'", "['’]")
    for p in sorted(set(TW.BOLDER_WORDS) | set(TW.CAREFUL_WORDS), key=len, reverse=True))
_RISK_RE = re.compile(r"(?<![\w'’-])(?:" + _RISK_SRC + r")(?![\w'’-])", re.IGNORECASE)
# what may follow a how-bold word that is set aside: the end, a stop, a joiner
_RISK_TAIL_RE = re.compile(r"\s*(?:$|[,.;!?]|(?:and|then|until|for|if|when|but)\b)", re.IGNORECASE)


_HELD_BACK_RE = re.compile(
    r"(?<![\w'’-])(?:" + "|".join(re.escape(p).replace(r"\ ", r"\s+") for p in TW.HELD_BACK)
    + r")(?![\w'’-])", re.IGNORECASE)


def held_back_in(text: str, names: Sequence[str] = ()) -> bool:
    """IC-7: the line says the attack is HELD BACK from the charge — the
    words stand at the END of the line, right behind a name (the enemy's):
    "Murat, attack Mack, held back". A remark about somebody else ("…, Soult
    is holding back", "— the reserve is held back") is no such word (the
    review, L2)."""
    raw = str(text or "").strip().rstrip(".!").strip()
    found = None
    for hit in _HELD_BACK_RE.finditer(raw):
        found = hit
    if found is None or raw[found.end():].strip():
        return False
    before = raw[:found.start()].rstrip().rstrip(",").rstrip().lower()
    forms: set = set()
    for name in names or ():
        forms.update(_name_forms(name))
    forms.discard("")
    return any(before.endswith(form) and (len(before) == len(form)
                                          or not before[-len(form) - 1].isalnum())
               for form in forms)


def tidy(text: str) -> str:
    """A line with a part taken out, put right: one space between words, no
    space before a stop, no doubled commas, no joiner left dangling."""
    out = re.sub(r"\s+", " ", str(text or ""))
    out = re.sub(r"\s+([,.;!?])", r"\1", out)
    out = re.sub(r"([,;])(?:\s*[,;])+", r"\1", out)
    out = re.sub(r"[,;]\s*([.!?])", r"\1", out)
    out = re.sub(r"\b(and|but|then|or),\s*", r"\1 ", out, flags=re.IGNORECASE)
    out = re.sub(r"(?:\s*,)?\s+(?:and|but|then|or)\s*([.!?]?)\s*$", r"\1", out, flags=re.IGNORECASE)
    return out.strip(" ,;")


def set_aside_risk_words(text: str, names: Sequence[str]) -> Tuple[str, List[str]]:
    """IC-8 (§8.3 "How bold"): `(the line, the how-bold words found)`.

    Every how-bold word of the table found in the line is returned (the
    read-back names each under "Not taken": in Session 2 an order is carried
    out as written). One that TRAILS a name — a marshal's or a province's —
    or stands between commas is also taken OUT of the line, so no reader
    takes it for part of the name: "Ney, hold Rhineland carefully" held the
    province "Rhineland Carefully". A word in a verb's place ("Ney,
    aggressively attack Mack") is left where today's readers found it. PURE."""
    out = str(text or "")
    hits = list(_RISK_RE.finditer(out))
    if not hits:
        return out, []
    found: List[str] = []
    forms: set = set()
    for name in names or ():
        forms.update(_name_forms(name))
    forms.discard("")
    cut: List[Tuple[int, int]] = []
    for hit in hits:
        found.append(re.sub(r"\s+", " ", hit.group(0)))
        if _RISK_TAIL_RE.match(out, hit.end()) is None:
            continue
        before = out[:hit.start()].rstrip()
        set_off = before.endswith(",")
        before_low = before.rstrip(",").rstrip().lower()
        trails_a_name = any(
            before_low.endswith(form) and (len(before_low) == len(form)
                                           or not before_low[-len(form) - 1].isalnum())
            for form in forms)
        if trails_a_name or set_off:
            cut.append((hit.start(), hit.end()))
    if not cut:
        return out, found
    for start, end in reversed(cut):
        out = out[:start] + " " + out[end:]
    return tidy(out), found


_OFFER_THEN = {"retreat": "fall_back", "attack": "attack", "fortify": "dig_in",
               "defend": "dig_in", "hold": "fall_back"}
_OFFER_MARKER_RE = re.compile(r"^\s*(?P<marker>unless|" + _MARKER_SRC + r")\b\s*(?P<body>.+?)\s*$",
                              re.IGNORECASE | re.DOTALL)


def offer(world, marshal, clause: str, action: str, order: str = "hold") -> str:
    """IC-8 (§8.3 — "offered back as the if-then it means"): the exact order
    a condition that was NOT taken means, as a sentence the line reads.

        "Ney, retreat if outnumbered"   ->  "Ney, hold. If he is outnumbered,
                                             fall back to Lorraine."
        "Ney, hold Rhineland unless attacked"  ->  "Ney, hold Rhineland. If he
                                             is attacked, fall back to Lorraine."

    The IF is the clause's own, read by the word table; the THEN is what the
    typed order did (a retreat falls back on his nearest safe province, an
    attack attacks, a fortify digs in). "" when the clause is no condition of
    the table's, the answer does not fit it, or his order could not carry the
    line (`settle`). PURE."""
    opened = _OFFER_MARKER_RE.match(str(clause or ""))
    if opened is None or marshal is None or world is None:
        return ""
    unless = opened.group("marker").lower() == "unless"
    then = "fall_back" if unless else _OFFER_THEN.get(str(action or ""))
    if then is None:
        return ""
    friends = [m.name for m in world.marshals.values() if m.nation == marshal.nation]
    enemies = [m.name for m in world.marshals.values() if m.nation != marshal.nation]
    probe, _why = _read_line(f"if {opened.group('body')}, dig in", friends, enemies,
                             list(world.regions), marshal.name)
    if probe is None or then not in TW.THENS_FOR.get(probe["if"], ()):
        return ""
    to = None
    if then == "fall_back":
        to = world.get_safe_retreat_destination(marshal.name)
        region = world.get_region(to) if to else None
        if region is None or getattr(region, "controller", None) != marshal.nation:
            return ""
    line = make_line(probe["if"], then=then, who=probe["who"], friend=probe["friend"],
                     place=probe["place"], to=to)
    kept, _refused = settle(world, marshal, "HOLD", [line])
    if not kept:
        return ""
    return restate(humanize_entity_name(marshal.name), str(order or "hold"), kept)


# ═══════════════════════════ the rules ══════════════════════════════════════

def capacity(marshal) -> int:
    return LITERAL_LINES if getattr(marshal, "personality", "") == "literal" else OTHER_LINES


def carries(marshal, strategic_type: Optional[str]) -> bool:
    """May this man's order of this type carry if-thens at all? A literal
    man's any standing order; anyone else's hold (today's rule)."""
    if not strategic_type:
        return False
    if getattr(marshal, "personality", "") == "literal":
        return strategic_type in ("HOLD", "MOVE_TO", "PURSUE", "SUPPORT")
    return strategic_type == "HOLD"


def settle(world, marshal, strategic_type: Optional[str], asked: Sequence[Dict[str, Any]]
           ) -> Tuple[List[Dict[str, Any]], List[Tuple[Dict[str, Any], str]]]:
    """`(kept, refused)` — the lines this man's order of this type takes, in
    order, and each line it does not with its plain reason (§7, §12):

    * the order must be one that carries if-thens (`carries`);
    * three lines for a literal man, one for anyone else;
    * at most one line may attack;
    * a line that repeats or contradicts an earlier one is refused;
    * "until X falls" when X has already fallen; a friend who is gone.

    PURE: `asked` is not changed (the kept lines are copies)."""
    kept: List[Dict[str, Any]] = []
    refused: List[Tuple[Dict[str, Any], str]] = []
    shown = humanize_entity_name(getattr(marshal, "name", "") or "")
    literal = getattr(marshal, "personality", "") == "literal"
    for line in asked or ():
        why = ""
        if not carries(marshal, strategic_type):
            why = ("an if-then rides a standing order — a hold, a march, a pursuit or a support"
                   if literal else
                   f"an if-then rides a hold — say '{shown}, hold' and the if-then behind it")
        elif len(kept) >= capacity(marshal):
            why = ("his orders carry three if-thens at most" if literal else
                   f"{shown}'s orders carry one if-then — only a marshal who follows orders "
                   f"to the letter takes three")
        elif line.get("then") == "attack" and sum(
                1 for k in kept if k.get("then") == "attack") >= ATTACK_LINES:
            why = "at most one line of an order may attack"
        else:
            why = _clash(line, kept) or _stale(world, marshal, line)
        if why:
            refused.append((dict(line), why))
        else:
            kept.append(dict(line))
    return kept, refused


def _if_key(line) -> tuple:
    return (line.get("if"), line.get("who"), line.get("friend"), line.get("place"))


def _clash(line, kept) -> str:
    for n, earlier in enumerate(kept, 1):
        if _if_key(earlier) != _if_key(line):
            continue
        same = (earlier.get("then"), earlier.get("to")) == (line.get("then"), line.get("to"))
        return (f"it repeats line {n}" if same else f"it contradicts line {n}")
    return ""


def _gone(world, name: Optional[str]) -> bool:
    man = world.get_marshal(name) if (world is not None and name) else None
    return (man is None or int(getattr(man, "strength", 0) or 0) <= 0
            or bool(getattr(man, "captured_by", "")))


def _fallen(world, marshal, place: Optional[str]) -> bool:
    region = world.get_region(place) if (world is not None and place) else None
    if region is None:
        return False
    holder = getattr(region, "controller", None)
    return bool(holder and holder != marshal.nation and world.is_at_war(marshal.nation, holder))


def _stale(world, marshal, line) -> str:
    """Why a line cannot be held as the board stands, or ""."""
    if world is None:
        return ""
    if line.get("friend") and _gone(world, line.get("friend")):
        return f"{humanize_entity_name(str(line['friend']))} is no longer in the field"
    if line.get("if") == "place_falls" and _fallen(world, marshal, line.get("place")):
        return f"{line.get('place')} has already fallen"
    if line.get("then") in _MOVING and _fallen(world, marshal, line.get("to")):
        return f"{line.get('to')} is in the enemy's hands"
    # (the review, S5) a line that names a commander watches an ENEMY: one we
    # are not at war with would never fire, and would sit using up a line.
    who = world.get_marshal(str(line.get("who") or "")) if line.get("who") else None
    if who is not None and marshal is not None \
            and not world.is_at_war(marshal.nation, who.nation):
        return f"we are not at war with {humanize_entity_name(who.name)}'s court"
    return ""


def struck(world, marshal, line) -> str:
    """§12: a line that names a place lost or a friend dead is STRUCK — its
    reason, or "". (A `place_falls` line is not struck by its own place
    falling: that is the line coming true.)"""
    if line.get("used"):
        return ""
    if line.get("friend") and _gone(world, line.get("friend")):
        return f"{humanize_entity_name(str(line['friend']))} is no longer in the field"
    if line.get("then") in _MOVING and _fallen(world, marshal, line.get("to")):
        return f"{line.get('to')} is in the enemy's hands"
    return ""


# ═══════════════════════════ the triggers ═══════════════════════════════════

def _sees(world, marshal, province: str) -> bool:
    """Does HIS OWN NATION see this province? (§7: "only what his own nation
    can see"; §10.3: an enemy literal marshal's if-thens read the live sight
    the code already keeps for each nation — never France's.)

    Row IC, Session 4 (IC-14) — THE ONE PLACE the if-thens ask about sight
    (with `known_strength`; the fog census in `tests/test_ic14_the_war_plan.py`
    pins that no other line of this module reads the player's store):

    * the PLAYER's nation reads its own intelligence — a province it sees
      fully or partly — exactly as before this seam;
    * ANY OTHER nation reads the sight its court's own logic reads
      (`WorldState.is_region_live_visible_to_nation`: the ground it holds, each
      of its corps' provinces and their neighbours, its towers). His own
      province and the ones next to it are his by that rule whatever the cache
      holds, so they are answered here without it; a horseman's second ring is
      read from the cache (the plan's pass refreshes it first).
    """
    nation = getattr(marshal, "nation", None)
    if nation == getattr(world, "player_nation", None):
        from backend.models.intel import FULL, PARTIAL
        return world.get_region_intel(province).visibility in (FULL, PARTIAL)
    here = world.get_region(getattr(marshal, "location", "") or "")
    if here is not None and (province == here.name
                             or province in (getattr(here, "adjacent_regions", None) or ())):
        return True
    return bool(world.is_region_live_visible_to_nation(province, nation))


def reach(world, marshal) -> List[str]:
    """The provinces within his reach that his nation SEES: his own and the
    ones next to it — two provinces out for horse — never across a crossing
    the enemy's fleet shuts (FA-15). His own first, then by the map's order
    (Rule 8: his region and its neighbours only)."""
    from backend.commands.strategic import strike_crossing_verdict
    here = world.get_region(marshal.location)
    if here is None:
        return []
    ring = [here.name] + list(getattr(here, "adjacent_regions", []) or [])
    if getattr(marshal, "cavalry", False):
        for name in list(ring[1:]):
            near = world.get_region(name)
            for further in (getattr(near, "adjacent_regions", []) or []) if near else []:
                if further not in ring:
                    ring.append(further)
    out = []
    for name in ring:
        if not _sees(world, marshal, name):
            continue
        if strike_crossing_verdict(world, marshal, name) is not None:
            continue
        out.append(name)
    return out


def known_strength(world, enemy, viewer=None) -> int:
    """An enemy corps' strength AS HIS NATION KNOWS IT: exact where he is fully
    seen, the middle of his band where he is partly seen, 0 with no reading.
    The one fog-banded helper (`CombatExecutor._fog_banded_strength`).

    Row IC, Session 4 (IC-14): `viewer` is the man who looks. With none, or a
    man of the player's nation, the reading is France's fog band, as before.
    A man of ANY OTHER nation knows what his nation sees exactly — the rule its
    court's own logic follows (`strategic.py`: "fog for the player, live truth
    for the AI"); what it does not see never reaches here (`reach`)."""
    if viewer is not None and getattr(viewer, "nation", None) != getattr(
            world, "player_nation", None):
        return int(getattr(enemy, "strength", 0) or 0)
    try:
        from backend.commands.combat_executor import CombatExecutor
        from backend.commands.order_quotes import _band_range
        label = str(CombatExecutor._fog_banded_strength(enemy, world))
        if label.endswith(" men"):
            return int(label.replace(" men", "").replace(",", ""))
        if label == "strength unknown":
            return 0
        low, high = _band_range(label)
        return int((low + high) // 2) if high else int(low)
    except Exception as exc:
        report(exc, "if_thens.known_strength")
        return 0


def seen_enemies(world, marshal) -> List[Tuple[Any, str]]:
    """`(enemy, province)` for every corps at war with us standing within
    reach where we see it — in `reach`'s order."""
    out = []
    for name in reach(world, marshal):
        for enemy in world.get_enemies_in_region(name, marshal.nation):
            if int(getattr(enemy, "strength", 0) or 0) <= 0 or getattr(enemy, "captured_by", ""):
                continue
            if not world.is_at_war(marshal.nation, enemy.nation):
                continue
            out.append((enemy, name))
    return out


def _floor(marshal) -> int:
    return int(getattr(marshal, "strength", 0) or 0) // FLOOR_DIVISOR


def _forces(world, marshal) -> Dict[str, int]:
    """Province -> the known strength of the enemy seen there (added up)."""
    forces: Dict[str, int] = {}
    for enemy, where in seen_enemies(world, marshal):
        forces[where] = forces.get(where, 0) + known_strength(world, enemy, marshal)
    return forces


def _attacks_on(world, marshal, defender: str) -> List[Dict[str, Any]]:
    """This turn's battles in which `defender` was attacked by a corps at war
    with us (the enemy's phase is behind us when the lines are read)."""
    out = []
    for battle in getattr(world, "battles_this_turn", None) or []:
        if battle.get("defender") != defender:
            continue
        attacker = world.get_marshal(str(battle.get("attacker") or ""))
        nation = getattr(attacker, "nation", None)
        if attacker is None or not nation or nation == marshal.nation:
            continue
        if not world.is_at_war(marshal.nation, nation):
            continue
        out.append({"attacker": attacker, "location": str(battle.get("location") or "")})
    return out


def happened(world, marshal, line: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Is the line's IF true on the board his nation sees? ``{"came", "enemy",
    "where"}`` — what came true in plain words, the enemy that tripped it (or
    None) and where — or None. PURE."""
    kind = line.get("if")
    shown = humanize_entity_name
    if kind == "enemy_near":
        who = line.get("who")
        forces = None
        for enemy, where in seen_enemies(world, marshal):
            if who:
                if enemy.name == who:       # a named marshal fires whatever his strength
                    return {"came": f"{shown(enemy.name)} comes within reach at {where}",
                            "enemy": enemy, "where": where}
                continue
            forces = forces if forces is not None else _forces(world, marshal)
            if forces.get(where, 0) >= max(1, _floor(marshal)):
                return {"came": f"{shown(enemy.name)} comes within reach at {where}",
                        "enemy": enemy, "where": where}
        return None
    if kind == "attacked":
        for battle in _attacks_on(world, marshal, marshal.name):
            attacker = battle["attacker"]
            if line.get("who") and attacker.name != line.get("who"):
                continue
            return {"came": f"{shown(attacker.name)} attacked him at {battle['location']}",
                    "enemy": attacker, "where": battle["location"]}
        return None
    if kind == "outnumbered":
        forces = _forces(world, marshal)
        floor = max(1, _floor(marshal))
        total = sum(v for v in forces.values() if v >= floor)
        if total > int(marshal.strength):
            strongest = max(seen_enemies(world, marshal),
                            key=lambda pair: known_strength(world, pair[0], marshal), default=None)
            return {"came": "he is outnumbered by the enemy within reach",
                    "enemy": strongest[0] if strongest else None,
                    "where": strongest[1] if strongest else marshal.location}
        return None
    if kind == "surrounded":
        here = world.get_region(marshal.location)
        beside = set(getattr(here, "adjacent_regions", []) or []) if here else set()
        forces = _forces(world, marshal)
        floor = max(1, _floor(marshal))
        sides = [name for name in beside if forces.get(name, 0) >= floor]
        if len(sides) < 2:
            return None
        for friend in world.marshals.values():
            if friend.name == marshal.name or int(getattr(friend, "strength", 0) or 0) <= 0:
                continue
            if getattr(friend, "captured_by", "") or friend.location not in beside:
                continue
            ours = friend.nation == marshal.nation
            allied = (not ours and not world.is_at_war(marshal.nation, friend.nation)
                      and _is_friend(world, marshal, friend))
            if ours or allied:
                return None       # a friend next to him: he is not surrounded
        return {"came": f"he is being surrounded — the enemy stands at {' and '.join(sorted(sides))}",
                "enemy": None, "where": marshal.location}
    if kind == "friend_attacked":
        friend = world.get_marshal(str(line.get("friend") or ""))
        if friend is None:
            return None
        here = world.get_region(marshal.location)
        near = {marshal.location} | set(getattr(here, "adjacent_regions", []) or [] if here else [])
        for battle in _attacks_on(world, marshal, friend.name):
            if battle["location"] in near:
                return {"came": f"{shown(friend.name)} was attacked at {battle['location']}",
                        "enemy": battle["attacker"], "where": battle["location"]}
        return None
    if kind == "place_falls":
        if _fallen(world, marshal, line.get("place")):
            return {"came": f"{line.get('place')} has fallen", "enemy": None,
                    "where": str(line.get("place"))}
        return None
    if kind == "friend_arrives":
        friend = world.get_marshal(str(line.get("friend") or ""))
        if friend is None or _gone(world, friend.name):
            return None
        here = world.get_region(marshal.location)
        near = {marshal.location} | set(getattr(here, "adjacent_regions", []) or [] if here else [])
        if friend.location in near:
            return {"came": f"{shown(friend.name)} has arrived at {friend.location}",
                    "enemy": None, "where": friend.location}
        return None
    return None


def _is_friend(world, marshal, other) -> bool:
    """An ally's or a client's corps beside him counts as a friend next to him."""
    try:
        from backend.game_logic.diplomacy import can_enter_territory
        # (WO-17: a nation-level question that relocates nobody — and asked
        # as the peace left it: a beaten enemy walking home through a
        # corridor is no friend next to him.)
        return bool(can_enter_territory(world, other.nation, marshal.nation,
                                        ignore_evacuation=True))
    except Exception as exc:
        report(exc, "if_thens._is_friend: can_enter_territory")
        return False


def attack_target(world, marshal, line: Dict[str, Any], event: Dict[str, Any]):
    """Whom an attack line strikes (§7): the enemy that tripped the line if he
    stands within reach where we see him, failing that the weakest we can see
    there — and only if he is NOT outnumbered by that enemy, unless the line
    says whatever the odds. None when there is nobody he may strike."""
    seen = seen_enemies(world, marshal)
    tripped = event.get("enemy")
    target = next((e for e, _where in seen if tripped is not None and e.name == tripped.name), None)
    if target is None and seen:
        target = min((e for e, _where in seen), key=lambda e: known_strength(world, e, marshal))
    if target is None:
        return None
    if not line.get("any_odds") and int(marshal.strength) < known_strength(world, target, marshal):
        return None
    return target


def ready(world, marshal, order) -> Optional[Dict[str, Any]]:
    """The FIRST live line of the order that has come true and can be carried
    out now — ``{"index", "line", "came", "enemy", "where", "target"}`` — or
    None. Two lines true the same turn: only the first in the list fires
    (§12). A `join` line is never read here: it is answered inside the
    friend's battle (`combat_executor`'s arrival roll). PURE."""
    turn = int(getattr(world, "current_turn", 0) or 0)
    for index, line in enumerate(lines(order)):
        if not is_live(line, turn) or line.get("then") == "join":
            continue
        if struck(world, marshal, line):
            continue
        event = happened(world, marshal, line)
        if event is None:
            continue
        target = None
        if line.get("then") == "attack":
            target = attack_target(world, marshal, line, event)
            if target is None:
                continue          # nobody he may strike yet: the line waits
        return {"index": index, "line": line, "came": event["came"],
                "enemy": event.get("enemy"), "where": event.get("where"), "target": target}
    return None


def join_line(world, candidate, primary) -> Optional[Dict[str, Any]]:
    """The live, unused "if <primary> is attacked next to him, join his
    battle" line of `candidate`'s standing order — the written word that
    brings him to a friend's battle — or None."""
    order = getattr(candidate, "strategic_order", None)
    turn = int(getattr(world, "current_turn", 0) or 0)
    for line in lines(order):
        if (line.get("then") == "join" and line.get("if") == "friend_attacked"
                and line.get("friend") == getattr(primary, "name", None)
                and is_live(line, turn)):
            return line
    return None
