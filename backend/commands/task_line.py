"""Row IC, Session 2 (IC-8) — WHAT THE LINE REFUSES, with the nearest real
sentence already written in (`docs/INDEPENDENT_COMMAND_SPEC.md` §8.3).

The typed line is the road for a TASK, and it takes a wide array of wordings
(`backend/ai/word_table.py`). This module holds the few things a task cannot
be, each of which the line used to read as SOMETHING ELSE without a word:

    a stretch of country   "Davout, hold between Munich and Vienna" marched
                           him to hold a province called "Between Munich";
                           "hold the line of the Inn" read back as a priced
                           hold and was then refused for want of a destination
    "their main army"      "Ney, attack their main army" was read as an attack
                           on the province of Maine
    a loose time           "hold Rhineland through the winter", "for two
                           weeks", "as long as it takes" — the words were
                           dropped and the hold given with no limit
    a leading "first"      "Murat, first take Swabia then support Soult" gave
                           the SECOND order and dropped the first
    a tail no marshal's    "Ney, hold Rhineland and build a fort" — the tail
    order carries          was dropped

Two are REFUSED free, on both roads, with the nearest real sentences offered
(`refusal`: a stretch, "their main army" — there is no order to understand).
The rest are READ AND SET ASIDE: the order goes as it always could have, and
the read-back names what was not taken (`parse_preview.not_taken_rows`), so
Enter sends the line as understood.

PURE: names are handed in, the board is only read, no die is cast.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

from backend.commands import if_thens as IT
from backend.display_names import humanize_entity_name

# ── a loose time ────────────────────────────────────────────────────────────
# "for now" / "for a while" / "for the present" are NOT here: they ask for no
# limit at all ("hold your position for now" is a plain hold, and always was).
_COUNT = (r"(?:\d+|an?|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
          r"several|some|many|a\s+few|a\s+couple\s+of)")
_SEASON = r"(?:winter|spring|summer|autumn)"
LOOSE_TIME_RE = re.compile(
    r"(?<![\w'’-])(?:"
    r"(?:all\s+)?(?:through|throughout|during|over|for)\s+(?:the\s+)?(?:whole\s+)?" + _SEASON
    + r"|(?:through|throughout|during)\s+the\s+(?:fall|season|campaign|year)"
    r"|for\s+" + _COUNT + r"\s+(?:more\s+)?(?:day|week|month|year|season)s?"
    r"|(?:for\s+)?as\s+long\s+as\s+(?:it\s+takes|necessary|needed|need\s+be|possible|you\s+can|"
    r"he\s+can|you\s+must)"
    r")(?![\w'’-])", re.IGNORECASE)
WHY_LOOSE_TIME = "say how long in turns: ‘for 3 turns’ or ‘until turn 9’"

# ── a tail no marshal's order carries ───────────────────────────────────────
_FORBIDDEN_TAIL_RE = re.compile(
    r"(?:\s*[,;]\s*(?:and\s+)?(?:then\s+)?|\s+and\s+(?:then\s+)?|\s+then\s+)"
    r"(?P<verb>recruit|raise\s+(?:\d|troops|men|infantry|cavalry|levies|a\s+levy)|levy|conscript|"
    r"build|construct|repair|buy|purchase|spend|negotiate)\b[^.;!?]*", re.IGNORECASE)
FORBIDDEN_ACTIONS = frozenset({"recruit", "build", "repair", "purchase_levy", "recruit_marshal"})
WHY_NOT_A_MARSHALS = ("a marshal's order marches, holds, chases or supports; "
                      "give that order by itself")

# ── a leading "first" ───────────────────────────────────────────────────────
_FIRST_RE = re.compile(r"^(?P<addr>\s*[^,.;:!?]+?\s*,\s*)first(?:\s+of\s+all)?\s*,?\s+(?=[A-Za-z])",
                       re.IGNORECASE)

# ── a stretch of country; "their main army" ─────────────────────────────────
_BETWEEN_RE = re.compile(r"\bbetween\s+(?P<a>[^,.;!?]+?)\s+and\s+(?P<b>[^,.;!?]+)", re.IGNORECASE)
_RIVER_LINE_RE = re.compile(
    r"\b(?:the\s+)?line\s+of\s+(?:the\s+)?[A-Za-z][\w'’-]*"
    r"|\bthe\s+(?-i:[A-Z])[\w'’-]*\s+line\b"
    r"|\b(?:the\s+)?(?:whole\s+)?(?:length|course|banks?)\s+of\s+the\s+[A-Za-z][\w'’-]*"
    r"|\balong\s+the\s+[A-Za-z][\w'’-]*", re.IGNORECASE)
# (the review, L1: never "the main army" by itself — that is ours as readily
# as theirs — and only as the object of a fighting verb)
_MAIN_ARMY_RE = re.compile(
    r"\b(?:their|the\s+enem(?:y|ies)(?:['’]s?)?|the\s+(?:austrian|russian|prussian|british|"
    r"english|allied|coalition)s?(?:['’]s?)?)\s+main\s+(?:army|body|force|host)\b"
    r"|\bthe\s+main\s+(?:enemy|austrian|russian|prussian|british|english|allied|coalition)\s+"
    r"(?:army|body|force|host)\b", re.IGNORECASE)
_FIGHTING_WORD_RE = re.compile(
    r"\b(?:attack|assault|engage|strike|hit|charge|bombard|shell|pursue|chase|hunt|harry|"
    r"shadow|destroy|crush|smash|fall\s+upon|go\s+after|march\s+(?:on|against))\b", re.IGNORECASE)
_HOLDING_WORD_RE = re.compile(r"\b(?:hold|guard|protect|keep|defend|secure|man|watch|cover)\b",
                              re.IGNORECASE)
_ADDRESS_RE = re.compile(r"^\s*(?P<addr>[^,.;:!?]+?)\s*,\s*(?P<rest>.+?)\s*$", re.DOTALL)


def drop_leading_first(text: str, friends: Sequence[str]) -> str:
    """ "Murat, first take Swabia then support Soult" -> "Murat, take Swabia
    then support Soult": the relay then gives the first and offers the second
    ("One order at a time"), as it does without the word. Only behind the
    address of one of our men; the text is returned unchanged otherwise."""
    found = _FIRST_RE.match(text or "")
    if found is None:
        return text
    if IT._resolve_name(found.group("addr").strip().rstrip(","), friends) is None:
        return text
    return found.group("addr") + text[found.end():]


def set_aside_loose_time(text: str) -> Tuple[str, List[str]]:
    """`(the line without them, the loose time words found)` — "through the
    winter", "for two weeks", "as long as it takes". The read-back names each
    under "Not taken" and offers the line with "for 3 turns" in its place."""
    out = str(text or "")
    # (the review, L7: only a phrase that ENDS its clause — "during the fall
    # of Vienna" is no season)
    hits = [hit for hit in LOOSE_TIME_RE.finditer(out) if IT._RISK_TAIL_RE.match(out, hit.end())]
    if not hits:
        return out, []
    found = [re.sub(r"\s+", " ", hit.group(0)) for hit in hits]
    for hit in reversed(hits):
        out = out[:hit.start()] + " " + out[hit.end():]
    return IT.tidy(out), found


def forbidden_tail(text: str) -> str:
    """The tail of a line that asks a marshal for what is not a marshal's to
    do ("…and build a fort", "…then recruit"), as typed — "" for none."""
    found = _FORBIDDEN_TAIL_RE.search(str(text or ""))
    return found.group(0).strip(" ,;") if found else ""


def _visible_enemies(world, marshal) -> List[str]:
    """The enemy commanders at war with us that France can SEE, nearest the
    marshal first (R5: never one out of sight)."""
    if world is None or marshal is None:
        return []
    rows = []
    for foe in world.get_visible_enemies(marshal.nation):
        if int(getattr(foe, "strength", 0) or 0) <= 0 or not world.is_at_war(marshal.nation, foe.nation):
            continue
        gap = world.get_distance(marshal.location, foe.location)
        rows.append((gap if isinstance(gap, int) else 99, foe.name))
    return [name for _gap, name in sorted(rows)]


def _swap(text: str, start: int, end: int, word: str) -> str:
    return IT.tidy(text[:start] + word + text[end:])


def refusal(world, text: str, friends: Sequence[str], places: Sequence[str]
            ) -> Optional[Dict[str, Any]]:
    """The free refusal of a line that asks one of our marshals for a STRETCH
    of country or for "their main army" — ``{"error", "short", "offers"}``:
    the reply's words, the read-back's, and the nearest real sentences (each
    the typed line with a real province, or a commander France can see, in
    the phrase's place). None when the line is neither."""
    found = _ADDRESS_RE.match(text or "")
    if found is None:
        return None
    addressee = IT._resolve_name(found.group("addr").strip(), friends)
    if addressee is None:
        return None
    marshal = world.get_marshal(addressee) if world is not None else None
    rest_at = found.start("rest")
    rest = found.group("rest")

    army = _MAIN_ARMY_RE.search(rest)
    if army is not None and _FIGHTING_WORD_RE.search(rest[:army.start()]):
        offers = [_swap(text, rest_at + army.start(), rest_at + army.end(),
                        humanize_entity_name(name))
                  for name in _visible_enemies(world, marshal)[:2]]
        example = offers[0] if offers else f"{found.group('addr').strip()}, attack <his name>"
        return {
            "error": (f"Name its commander, Sire — an order goes against a man, not "
                      f"'{army.group(0)}': '{example}'. Nothing has been relayed."),
            "short": "Name its commander — an order goes against a man, not an army",
            "offers": offers,
        }

    between = _BETWEEN_RE.search(rest)
    if between is not None:
        a = IT._resolve_place(between.group("a"), places)
        b = IT._resolve_place(between.group("b"), places)
        if a is not None and b is not None:
            offers = [_swap(text, rest_at + between.start(), rest_at + between.end(),
                            humanize_entity_name(place)) for place in (a, b)]
            return {
                "error": (f"A corps holds one province, Sire, not the country between two — name "
                          f"one: '{offers[0]}'. Nothing has been relayed."),
                "short": "Name one province — a corps holds a province, not a stretch between two",
                "offers": offers,
            }
    river = _RIVER_LINE_RE.search(rest)
    # only behind a word that asks him to HOLD ground ("march along the road
    # to Paris" is a march, and is read as it always was)
    # (the review, L5: … and in the SAME clause — "hold Lorraine, then march
    # along the road to Paris" holds Lorraine)
    if river is not None and _HOLDING_WORD_RE.search(
            re.split(r"[,;]|\b(?:then|and)\b", rest[:river.start()])[-1]):
        offers = []
        if marshal is not None and getattr(marshal, "location", None):
            offers = [_swap(text, rest_at + river.start(), rest_at + river.end(),
                            humanize_entity_name(marshal.location))]
        example = offers[0] if offers else f"{found.group('addr').strip()}, hold <a province>"
        return {
            "error": (f"A corps holds a province, Sire, not a line on the map — name one: "
                      f"'{example}'. Nothing has been relayed."),
            "short": "Name one province — a corps holds a province, not a line",
            "offers": offers,
        }
    return None
