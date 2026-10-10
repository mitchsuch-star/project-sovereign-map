"""DD-0 S3b — the pre-parse rewrites the instrument's findings asked for
(October 10, 2026; rows BUG_FIXES.md §DD-0 S3; rules SYSTEMS_REFERENCE.md
§103). Every function is pure text → text (or a split), reads only the
rosters it is handed, and is applied in `CommandParser.parse` BEFORE any
reader sees the line — so the mock chain, the strategic layer and the fuzzy
scan agree by construction (the three-producers lesson). Each leaves the
line untouched when its shape is absent.

  strip_please_and_urgency   "please, …" / "…, please" / "…, at once" / "… with all speed"
  strip_dash_aside           "… — thank you" / "… — the Austrians are close": an aside
                             after a dash that names no place, no man and no order
  strip_because_tail         "… because the men are ready": a reason of OURS (the
                             enemy's reasons are clause_guards' — CRT-1)
  rewrite_self_correction    "go to Berlin — no wait, Dresden" → "go to Dresden"
  rewrite_arrival_wait       "go to Gelderland and wait there" → "go to Gelderland"
                             (the WAIT arm sits above the move arm — DD0-2)
  rewrite_second_in_support  "Ney, attack Mack with Lannes in support" →
                             "Ney, attack Mack, then Lannes, support Ney" (the
                             second man's order rides the relay — the ledger's
                             second_name_role class)
  rewrite_send_marshal       "send Soult to Orleanais" / "pull Bernadotte back to
                             Frankfurt" / "get Lannes to Munich" → "<Name>, move to <X>"
  rewrite_kill               "go kill Mack" / "kill Mack" → "attack Mack" (a foe in sight)
  rewrite_reward_idiom       "give Ney an estate" / "make Massena a duke" / "reward
                             Soult with a title" → "reward <Name>" (the Reward desk)
  split_question_and_order   "what's in Tyrol? Massena, find out" → the question and
                             the addressed order behind it (DD0-5)
"""
from __future__ import annotations

import re
from typing import Iterable, List, Optional, Tuple

_ORDER_VERB_RE = re.compile(
    r"\b(?:attack|assault|storm|engage|charge|bombard|pursue|chase|hunt|move|march|"
    r"advance|go|head|proceed|ride|withdraw|retreat|retire|fall\s+back|hold|defend|"
    r"guard|protect|cover|fortify|entrench|dig\s+in|unfortify|drill|train|scout|"
    r"recruit|raise|levy|build|construct|repair|garrison|detach|support|reinforce|"
    r"aid|help|join|wait|stand|form|cancel|halt|stop|sail|land|blockade|declare|"
    r"propose|offer|send|invest|grant|cede|enact|repeal|commission|reward|end)\b",
    re.IGNORECASE)

_PLEASE_LEAD_RE = re.compile(r"^\s*(?:please|pray|kindly)[,\s]+", re.IGNORECASE)
_URGENCY_TAIL_RE = re.compile(
    r"[\s,;—–-]+(?:please|at\s+once|with\s+all\s+(?:possible\s+)?speed|immediately|right\s+away|"
    r"this\s+instant|forthwith|at\s+the\s+double|without\s+delay|if\s+you\s+please|"
    r"thank\s+you)\s*[.!]*\s*$", re.IGNORECASE)
_PLEASE_AFTER_ADDRESS_RE = re.compile(r"^(\s*(?:[Mm]arshal\s+)?[A-Za-z][\w'’-]*,\s*)please[,\s]+", re.IGNORECASE)


def strip_please_and_urgency(text: str) -> str:
    if not text:
        return text
    out = text
    for _ in range(3):
        out = _PLEASE_LEAD_RE.sub("", out, count=1)
    out = _PLEASE_AFTER_ADDRESS_RE.sub(r"\1", out, count=1)
    for _ in range(2):
        out = _URGENCY_TAIL_RE.sub("", out, count=1)
    return out if out.strip() else text


def _known_tokens(names: Iterable[str]) -> set:
    toks = set()
    for n in names or []:
        for t in re.findall(r"[a-z][a-z'’-]+", str(n).lower()):
            toks.add(t)
    return toks


_DASH_RE = re.compile(r"\s+[—–-]+\s+")


def strip_dash_aside(text: str, known_names: Iterable[str]) -> str:
    """Cut an aside after a dash when it names nothing the board knows and
    gives no order — "— thank you", "- at once", "— the Austrians are
    close". "Murat — Swabia. Go." and "Davout — Mack — go." keep their
    dashes (a place or a man follows)."""
    if not text:
        return text
    m = _DASH_RE.search(text)
    if not m:
        return text
    head, aside = text[:m.start()], text[m.end():]
    if not head.strip() or not aside.strip():
        return text
    known = _known_tokens(known_names)
    aside_tokens = set(re.findall(r"[a-z][a-z'’-]+", aside.lower()))
    if aside_tokens & known or _ORDER_VERB_RE.search(aside) or re.search(r"\d", aside):
        return text
    if re.search(r"\b(?:no|not|never|don'?t|wait|turn|end)\b", aside, re.IGNORECASE):
        return text
    return head.rstrip(" ,;")


_BECAUSE_RE = re.compile(r"[\s,;]+because\s+(?P<why>.+?)\s*[.!]*$", re.IGNORECASE)


def strip_because_tail(text: str, known_names: Iterable[str]) -> str:
    """"… because the men are ready" — a reason of ours that names no place,
    no man and no order is cut; a reason that names the enemy's movements is
    clause_guards' (CRT-1) and is left to it."""
    if not text:
        return text
    m = _BECAUSE_RE.search(text)
    if not m:
        return text
    why = m.group("why")
    known = _known_tokens(known_names)
    if set(re.findall(r"[a-z][a-z'’-]+", why.lower())) & known or _ORDER_VERB_RE.search(why):
        return text
    return text[:m.start()].rstrip(" ,;")


_SELF_CORRECTION_RE = re.compile(
    r"\b(?P<prep>to|toward|towards|on|into|for)\s+(?P<first>[A-Za-z][\w'’-]+(?:\s+[A-Z][\w'’-]+)?)"
    r"\s*[—–,-]+\s*(?:no[, ]+wait|no[, ]+make\s+that|scratch\s+that|I\s+mean|rather|sorry)[, ]+"
    r"(?P<second>[A-Za-z][\w'’-]+(?:\s+[A-Z][\w'’-]+)?)\s*[.!]*$", re.IGNORECASE)


def rewrite_self_correction(text: str) -> str:
    if not text:
        return text
    m = _SELF_CORRECTION_RE.search(text)
    if not m:
        return text
    return text[:m.start()] + f"{m.group('prep')} {m.group('second')}"


_ARRIVAL_WAIT_RE = re.compile(
    r"^(?P<head>.*\b(?:go|move|march|head|proceed|advance|ride|get|travel|push)\b.+?\S)"
    r"[\s,]+(?:and|then)\s+(?:wait|stand\s+by|halt|stop)"
    r"(?:\s+(?:there|here)|\s+(?:in|at)\s+[A-Za-z][\w'’-]+)?\s*[.!]*$", re.IGNORECASE)


def rewrite_arrival_wait(text: str) -> str:
    if not text:
        return text
    m = _ARRIVAL_WAIT_RE.match(text)
    if not m:
        return text
    return m.group("head")


def _name_alt(names: Iterable[str]) -> str:
    return "|".join(re.escape(str(n)) for n in sorted(names or [], key=len, reverse=True))


def rewrite_second_in_support(text: str, friendly_names: Iterable[str]) -> str:
    alt = _name_alt(friendly_names)
    if not text or not alt:
        return text
    m = re.match(
        r"^\s*(?P<addr>(?:(?:marshal|general|gen\.|maréchal|marechal)\s+)?(?P<name>" + alt + r"))[,:]?\s+(?P<order>.+?)"
        r"\s+with\s+(?:marshal\s+)?(?P<second>" + alt + r")\s+"
        r"(?:in\s+support|supporting|in\s+reserve|backing\s+(?:him|them)\s+up|to\s+back\s+him\s+up)"
        r"\s*[.!]*$", text, flags=re.IGNORECASE)
    if not m or m.group("name").lower() == m.group("second").lower():
        return text
    if not _ORDER_VERB_RE.search(m.group("order")):
        return text
    first = next(n for n in friendly_names if str(n).lower() == m.group("name").lower())
    second = next(n for n in friendly_names if str(n).lower() == m.group("second").lower())
    return f"{first}, {m.group('order')}, then {second}, support {first}"


def rewrite_send_marshal(text: str, friendly_names: Iterable[str]) -> str:
    alt = _name_alt(friendly_names)
    if not text or not alt:
        return text
    m = re.match(
        r"^\s*(?:send|pull|bring|get|dispatch|order|shift|withdraw)\s+(?:marshal\s+)?"
        r"(?P<name>" + alt + r")(?:'s\s+corps|'s\s+men)?\s+(?:back\s+|over\s+|up\s+|down\s+)?"
        r"(?:to|toward|towards|into|for)\s+(?P<where>[A-Za-z][\w'’ -]{2,40}?)\s*[.!]*$",
        text, flags=re.IGNORECASE)
    if not m or _ORDER_VERB_RE.match(m.group("where").strip()):
        # "send Murat to scout Munich" — the verb after `to` is the order
        return text
    name = next(n for n in friendly_names if str(n).lower() == m.group("name").lower())
    return f"{name}, move to {m.group('where').strip()}"


def rewrite_kill(text: str, enemy_names: Iterable[str]) -> str:
    alt = _name_alt(enemy_names)
    if not text or not alt:
        return text
    # "destroy" / "crush" stay CRT-11's battle verbs (the destroy clause);
    # only the colloquial kill forms are restated.
    return re.sub(r"\b(?:go\s+(?:and\s+)?)?(?:kill|slaughter|murder)\s+(?=(?:" + alt + r")\b)",
                  "attack ", text, count=1, flags=re.IGNORECASE)


def rewrite_reward_idiom(text: str, friendly_names: Iterable[str]) -> str:
    alt = _name_alt(friendly_names)
    if not text or not alt:
        return text
    # "grant <Name> a rente / a pension" is the ES-7 endow family's own
    # verb and is NOT restated; the estate, the title and the dukedom open
    # the Reward desk.
    m = re.match(
        r"^\s*(?:give\s+(?:marshal\s+)?(?P<n1>" + alt + r")\s+"
        r"(?:an?\s+)?(?:estate|title|duchy|dukedom|principality|county|reward)\b"
        r"|make\s+(?:marshal\s+)?(?P<n2>" + alt + r")\s+(?:a\s+|the\s+)?(?:duke|prince|count|marquis|baron|peer)\b"
        r"|reward\s+(?:marshal\s+)?(?P<n3>" + alt + r")\s+with\s+(?:an?\s+)?(?:title|estate|duchy)\b)",
        text, flags=re.IGNORECASE)
    if not m:
        return text
    typed = m.group("n1") or m.group("n2") or m.group("n3")
    name = next(n for n in friendly_names if str(n).lower() == typed.lower())
    return f"reward {name}"


def rewrite_attack_idioms(text: str, friendly_names: Iterable[str], enemy_names: Iterable[str]) -> str:
    """The field's idioms for a battle, restated: "run down Mack('s guns)",
    "drive Mack out", "give Mack a bloody nose" → attack Mack; "keep on
    John's heels" → pursue John; "Davout — Mack — go." → Davout, attack Mack."""
    foes = _name_alt(enemy_names)
    if not text or not foes:
        return text
    # "ride down" is RIDE_DOWN_A_FOE_RE's own lever-gated road; "run down" here.
    out = re.sub(r"\brun\s+down\s+(?P<foe>" + foes + r")(?:['’]s\s+\w+)?\b", r"attack \g<foe>", text, count=1, flags=re.IGNORECASE)
    out = re.sub(r"\bdrive\s+(?P<foe>" + foes + r")\s+(?:out|off|back|away)\b", r"attack \g<foe>", out, count=1, flags=re.IGNORECASE)
    out = re.sub(r"\b(?:give|gave)\s+(?P<foe>" + foes + r")\s+a\s+(?:bloody\s+nose|thrashing|beating|hiding|drubbing)\b",
                 r"attack \g<foe>", out, count=1, flags=re.IGNORECASE)
    out = re.sub(r"\b(?:keep|stay)\s+on\s+(?P<foe>" + foes + r")['’]s\s+(?:heels|tail|trail)\b", r"pursue \g<foe>", out, count=1, flags=re.IGNORECASE)
    friends = _name_alt(friendly_names)
    if friends:
        m = re.match(r"^\s*(?:marshal\s+)?(?P<name>" + friends + r")\s*[—–-]+\s*(?P<foe>" + foes + r")\s*[—–-]*\s*(?:go|attack|now)?\s*[.!]*$",
                     out, flags=re.IGNORECASE)
        if m:
            out = f"{m.group('name')}, attack {m.group('foe')}"
    return out


_INVEST_GOLD_RE = re.compile(
    r"^\s*(?:invest|put|pour|sink|send)\s+(?:\d[\d,]*\s+)?(?:some\s+|more\s+|a\s+little\s+)?gold\s+(?:in|into)\s+(?P<court>.+?)\s*[.!]*$",
    re.IGNORECASE)


def rewrite_invest_gold(text: str) -> str:
    m = _INVEST_GOLD_RE.match(text or "")
    return f"invest in {m.group('court')}" if m else text


_TRAILING_END_TURN_RE = re.compile(
    r"^(?P<head>.*?)[,;—–-]+\s*(?:next\s+turn|end\s+(?:the\s+)?turn|end\s+of\s+turn)\s*[.!]*$", re.IGNORECASE)


def rewrite_trailing_end_turn(text: str) -> str:
    """"That's all for now, Berthier — next turn." → "end turn" (only when
    the head gives no order of its own)."""
    m = _TRAILING_END_TURN_RE.match(text or "")
    if not m or _ORDER_VERB_RE.search(m.group("head")):
        return text
    return "end turn"


# ── the router's idiom predicates ───────────────────────────────────────
# Read by `_parse_with_mock_chain`'s branches. They live HERE, not inline,
# because `tools/gen_routed_order_words.py` harvests the leading word of
# every keyword in a routing branch as a ROUTED ORDER WORD, and a noun
# harvested that way ("cavalry", "ships", "gold", "earthworks") stops
# being an addressee the CX-R1 rule can refuse — "the cavalry, attack
# Mack" fought. The generator follows helpers one hop into llm_client,
# attack_vocabulary and strategic_parser only; this module is outside it.

_GARRISON_IDIOM_RE = re.compile(
    r"\b(?:drop\s+off|leave|detach|post|station|spare)\b.{0,30}?"
    r"\b(?:battalions?|regiments?|brigades?|companies|men|troops|a\s+garrison|"
    r"some\s+of\s+(?:the|his|your)\s+(?:corps|men))\b")


def garrison_idiom(command_lower: str) -> bool:
    """DD0-4: men LEFT to hold a place."""
    return bool(_GARRISON_IDIOM_RE.search(command_lower or ""))


def squares_order(command_lower: str) -> bool:
    """"Soult, squares — Austrian cavalry coming" / "Soult, squares"."""
    cl = command_lower or ""
    if not re.search(r"\bsquares?\b", cl) or re.search(r"\b(?:break|leave|exit)\b", cl):
        return False
    return bool("cavalry" in cl
                or re.match(r"^\s*(?:(?:marshal\s+)?[a-z][\w'’-]*\s*[,:]\s*)?(?:form\s+)?squares?\s*[.!]*$", cl))


def fleet_sortie(command_lower: str) -> bool:
    cl = command_lower or ""
    return bool(re.search(r"\bsortie\b", cl) and re.search(r"\b(?:fleet|navy|ships|admiral)\b", cl))


def fleet_feint(command_lower: str) -> bool:
    cl = command_lower or ""
    return bool((re.search(r"\bfeint\b", cl) and re.search(r"\b(?:fleet|navy|ships)\b", cl))
                or re.search(r"\bdraw\s+\w+\s+off\b", cl))


def landing_order(command_lower: str) -> bool:
    cl = command_lower or ""
    return bool(re.search(r"\bland\b\s+(?!to\b)(?:[\w',]+\s+){0,2}(?:in|at|on)\b", cl)
                or re.search(r"\b(?:mount|make|stage)\s+a\s+landing\b", cl))


def scout_idiom(command_lower: str) -> bool:
    return bool(re.search(r"\beyes\s+on\b|\bfind\s+out\b|\breport\s+back\b|\bsend\s+riders\b",
                          command_lower or ""))


def earthworks_order(command_lower: str) -> bool:
    return bool(re.search(r"\b(?:earthworks|breastworks)\b", command_lower or ""))


def unfortify_idiom(command_lower: str) -> bool:
    return bool(re.search(r"\b(?:abandon|leave|quit|give\s+up)\s+(?:the\s+|your\s+|his\s+)?"
                          r"(?:entrenchments?|earthworks|works|fortifications?|breastworks)\b",
                          command_lower or ""))


def drill_idiom(command_lower: str) -> bool:
    return bool(re.search(r"\bthrough\s+(?:its|their|his)\s+paces\b|\bmusketry\b|\bpracti[sc]e\b",
                          command_lower or ""))


def invest_gold(command_lower: str, known_nations_lower) -> bool:
    cl = command_lower or ""
    nations = [n for n in (known_nations_lower or []) if n]
    if not nations or not re.search(r"\bgold\b|\binvest\b", cl):
        return False
    return bool(re.search(r"\b(?:invest|put|pour|sink)\b.{0,30}\b(?:in|into)\s+(?:the\s+)?(?:"
                          + "|".join(re.escape(n) for n in nations) + r")\b", cl))


def march_idiom(command_lower: str) -> bool:
    """"relocate his corps to", "bring the corps back to", "get to Munich"."""
    return bool(re.search(r"\b(?:relocate|redeploy)\b|\b(?:bring|get|pull|take)\b.{0,40}\bback\s+to\b"
                          r"|\bget\s+(?:to|into)\b", command_lower or ""))


def split_question_and_order(text: str, friendly_names: Iterable[str]) -> Optional[Tuple[str, str]]:
    """"what's in Tyrol? Massena, find out" → ("what's in Tyrol?", "Massena, find out")."""
    alt = _name_alt(friendly_names)
    if not text or not alt or "?" not in text:
        return None
    m = re.match(r"^(?P<q>[^?]+\?)\s+(?P<tail>(?:marshal\s+)?(?:" + alt + r")[,:]?\s+\S.*)$",
                 text, flags=re.IGNORECASE)
    if not m:
        return None
    return m.group("q").strip(), m.group("tail").strip()


def apply_all(text: str, friendly_names: Iterable[str], enemy_names: Iterable[str],
              place_names: Iterable[str]) -> List[Tuple[str, str, str]]:
    """Every rewrite in order; returns [(rule, before, after)] for the ones
    that fired, the caller reads the final text off the last row."""
    known = list(friendly_names) + list(enemy_names) + list(place_names)
    steps = (
        ("strip_please_and_urgency", lambda t: strip_please_and_urgency(t)),
        ("strip_dash_aside", lambda t: strip_dash_aside(t, known)),
        ("strip_because_tail", lambda t: strip_because_tail(t, known)),
        ("rewrite_self_correction", lambda t: rewrite_self_correction(t)),
        ("rewrite_arrival_wait", lambda t: rewrite_arrival_wait(t)),
        ("rewrite_second_in_support", lambda t: rewrite_second_in_support(t, friendly_names)),
        ("rewrite_send_marshal", lambda t: rewrite_send_marshal(t, friendly_names)),
        ("rewrite_kill", lambda t: rewrite_kill(t, enemy_names)),
        ("rewrite_attack_idioms", lambda t: rewrite_attack_idioms(t, friendly_names, enemy_names)),
        ("rewrite_reward_idiom", lambda t: rewrite_reward_idiom(t, friendly_names)),
        ("rewrite_invest_gold", lambda t: rewrite_invest_gold(t)),
        ("rewrite_trailing_end_turn", lambda t: rewrite_trailing_end_turn(t)),
    )
    rows: List[Tuple[str, str, str]] = []
    cur = text
    for rule, fn in steps:
        nxt = fn(cur)
        if nxt != cur:
            rows.append((rule, cur, nxt))
            cur = nxt
    return rows
