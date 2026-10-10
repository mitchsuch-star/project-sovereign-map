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
    # the Reward desk. S4 (SFR-D8): "reward Murat for his charge at Swabia"
    # is the Reward desk too — the "for …" is the reason, never a charge.
    m = re.match(
        r"^\s*(?:give\s+(?:marshal\s+)?(?P<n1>" + alt + r")\s+"
        r"(?:an?\s+)?(?:estate|title|duchy|dukedom|principality|county|reward)\b"
        r"|make\s+(?:marshal\s+)?(?P<n2>" + alt + r")\s+(?:a\s+|the\s+)?(?:duke|prince|count|marquis|baron|peer)\b"
        r"|reward\s+(?:marshal\s+)?(?P<n3>" + alt + r")\s+with\s+(?:an?\s+)?(?:title|estate|duchy)\b"
        r"|reward\s+(?:marshal\s+)?(?P<n4>" + alt + r")\s+for\s+\S)",
        text, flags=re.IGNORECASE)
    if not m:
        return text
    typed = m.group("n1") or m.group("n2") or m.group("n3") or m.group("n4")
    name = next(n for n in friendly_names if str(n).lower() == typed.lower())
    return f"reward {name}"


def _foe_alt(enemy_names: Iterable[str]) -> str:
    """Every form a foe is named by (S4: the surname alone — "John's heels",
    "Charles" — when it names one foe only; `reading.foe_forms`)."""
    from backend.ai.reading import foe_forms
    return _name_alt(foe_forms(enemy_names))


def _printed_foe(typed: str, enemy_names: Iterable[str]) -> str:
    """The form the game PRINTS for a foe typed by any of his forms — so a
    surname ("John") hands the pursuit "Archduke John", which every target
    resolver knows, never the bare word."""
    from backend.ai.reading import foe_named_in
    from backend.display_names import humanize_entity_name
    key = foe_named_in(typed, enemy_names)
    return humanize_entity_name(key) if key else typed


def _sub_foe(pattern: str, template: str, text: str, enemy_names: Iterable[str]) -> str:
    """`re.sub` whose `{foe}` is the printed form of the matched foe."""
    def _rep(m):
        return template.format(foe=_printed_foe(m.group("foe"), enemy_names))
    return re.sub(pattern, _rep, text, count=1, flags=re.IGNORECASE)


def rewrite_attack_idioms(text: str, friendly_names: Iterable[str], enemy_names: Iterable[str]) -> str:
    """The field's idioms for a battle, restated: "run down Mack('s guns)",
    "drive Mack out", "give Mack a bloody nose", "fall on Mack's flank" →
    attack Mack; "keep on John's heels", "chase Mack down wherever he runs",
    "follow Mack to the ends of the earth" → pursue; "Davout — Mack — go." →
    Davout, attack Mack."""
    foes = _foe_alt(enemy_names)
    if not text or not foes:
        return text
    # "ride down" is RIDE_DOWN_A_FOE_RE's own lever-gated road; "run down" here.
    out = _sub_foe(r"\brun\s+down\s+(?P<foe>" + foes + r")(?:['’]s\s+\w+)?\b", "attack {foe}", text, enemy_names)
    out = _sub_foe(r"\bdrive\s+(?P<foe>" + foes + r")\s+(?:out|off|back|away)\b", "attack {foe}", out, enemy_names)
    out = _sub_foe(r"\b(?:give|gave)\s+(?P<foe>" + foes + r")\s+a\s+(?:bloody\s+nose|thrashing|beating|hiding|drubbing)\b",
                   "attack {foe}", out, enemy_names)
    out = _sub_foe(r"\bfall\s+(?:up)?on\s+(?P<foe>" + foes + r")(?:['’]s\s+(?:flank|flanks|rear|centre|center|left|right|line|column|wing))?\b",
                   "attack {foe}", out, enemy_names)
    out = _sub_foe(r"\b(?:keep|stay)\s+on\s+(?P<foe>" + foes + r")['’]s\s+(?:heels|tail|trail)\b", "pursue {foe}", out, enemy_names)
    out = _sub_foe(r"\b(?:chase|hunt|run|track)\s+(?P<foe>" + foes + r")\s+down"
                   r"(?:\s+wherever\s+(?:he|they|it)\s+(?:runs?|goes|flees|hides?|may\s+go|may\s+run))?\b",
                   "pursue {foe}", out, enemy_names)
    out = _sub_foe(r"\b(?:follow|chase|hunt|pursue)\s+(?P<foe>" + foes + r")\s+"
                   r"(?:to\s+the\s+ends\s+of\s+the\s+earth|wherever\s+(?:he|they|it)\s+(?:runs?|goes|flees|hides?|may\s+go)|"
                   r"to\s+the\s+gates\s+of\s+\w+|day\s+and\s+night|without\s+rest)\b",
                   "pursue {foe}", out, enemy_names)
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


# ── DD-0 S4 (October 10, 2026): the vocabulary the ledger, the six keyless
# shrugs and the sixteen open command rows asked for (rules
# SYSTEMS_REFERENCE.md §104). Each pure, each inert when its shape is absent.

_LAW_NOUN_RX = re.compile(r"\b(?:law|act|reform|bill|ordinance|decree)\b", re.IGNORECASE)


def rewrite_pass_a_law(text: str) -> str:
    """SFR-H2: "pass the Staff law" / "adopt the Staff" / "decree the
    conscription act" → "enact <law>" — the law router knows `enact` /
    `reenact` / `repeal` only, and "pass" fell to the proper-name ask.
    Only a line that names a law (the noun, or "law" somewhere in it)."""
    if not text or not _LAW_NOUN_RX.search(text):
        return text
    m = re.match(r"^\s*(?:please\s+)?(?:pass|adopt|decree|promulgate|introduce|bring\s+in|put\s+through)\s+"
                 r"(?:the\s+|a\s+|an\s+)?(?P<name>.+?)\s*[.!]*$", text, flags=re.IGNORECASE)
    if not m:
        return text
    name = re.sub(r"\s*\b(?:law|act|bill|ordinance|decree)\b\s*$", "", m.group("name"), flags=re.IGNORECASE).strip()
    name = re.sub(r"^(?:a\s+)?(?:law|act|bill)\s+(?:raising|lowering|on|for|about|that|which)\s+", "", name,
                  flags=re.IGNORECASE).strip()
    return f"enact {name}" if name else text


def rewrite_take_back(text: str) -> str:
    """SFR-D37: "take Lyonnais back from Paget" / "retake Provence" → "take
    <province>" (RS-11's objective reads the rest)."""
    if not text:
        return text
    out = re.sub(r"\b(?:take|win|get)\s+(?P<obj>[A-Za-z][\w'’-]*(?:\s+[A-Z][\w'’-]*)?)\s+back"
                 r"(?:\s+from\s+(?:the\s+)?[A-Za-z][\w'’ -]*?)?(?=\s*[.!,;]|\s+(?:and|then)\b|$)",
                 lambda m: text[m.start():m.end()] if m.group("obj").lower() in ("it", "them", "him", "her", "that", "this")
                 else f"take {m.group('obj')}", text, count=1, flags=re.IGNORECASE)
    out = re.sub(r"\bretake\s+", "take ", out, count=1, flags=re.IGNORECASE)
    return out


def rewrite_return_to(text: str) -> str:
    """SFR-D37: "return to Paris" / "go back to Lorraine" / "keep going to
    Provence" / "press on to Munich" → "move to <place>". A "fall back to"
    stays the retreat it is."""
    if not text:
        return text
    # the word after `to` must be a place, never a verb ("continue to hold")
    not_a_verb = r"(?!(?:" + _ORDER_VERB_RE.pattern.strip(r"\b") + r")\b)"
    # ("march back to X" / "head back to X" are SFR-D11's own relative-place
    # reader in the strategic layer and are left to it)
    out = re.sub(r"\b(?:return|go\s+back|get\s+back|come\s+back)"
                 r"\s+(?:to|toward|towards|for)\s+" + not_a_verb + r"(?=[A-Za-z])", "move to ", text, count=1,
                 flags=re.IGNORECASE)
    # ("push on to" / "press on to" / "march on to" are the strategic
    # layer's own march verbs already and are left to it)
    out = re.sub(r"\b(?:keep\s+going|carry\s+on|continue)"
                 r"\s+(?:to|toward|towards|for)\s+" + not_a_verb + r"(?=[A-Za-z])", "move to ", out, count=1,
                 flags=re.IGNORECASE)
    return out


# ("stay here" / "stay put" are the WAIT family's own words — slice 7 — and
# "hold fast" / "hold firm" are CQ-37's; each is left to its own rule.)
_HOLD_HERE_RX = re.compile(
    r"\b(?:hold|stand|remain)\s+(?:where\s+(?:you|he|they)\s+(?:are|is|stand|stands)|your\s+ground|"
    r"his\s+ground|this\s+ground|in\s+place|right\s+where\s+you\s+are)\b",
    re.IGNORECASE)


def rewrite_hold_where_you_are(text: str) -> str:
    """SFR-D24: "hold where you are" / "stand fast" / "hold your ground" →
    "hold" — the standing order on the ground he stands on."""
    return _HOLD_HERE_RX.sub("hold", text, count=1) if text else text


def strip_stop_chasing(text: str, enemy_names: Iterable[str]) -> str:
    """SFR-D24: "stop chasing John and hold …" → "hold …" (a new order to
    the man sets the pursuit aside, and SR5B names the order it ended);
    "stop chasing John" alone is the cancel."""
    foes = _foe_alt(enemy_names)
    if not text or not foes:
        return text
    m = re.match(r"^(?P<addr>\s*(?:(?:marshal|general|prince)\s+)?[A-Za-z][\w'’-]*\s*[,:]\s*)?"
                 r"(?:stop|cease|quit|break\s+off|leave\s+off|give\s+up|call\s+off)\s+"
                 r"(?:chasing|pursuing|following|hunting|the\s+pursuit\s+of|the\s+chase\s+of|the\s+hunt\s+for)\s+"
                 r"(?:" + foes + r")\b[,;]?\s*(?:(?:and|then)\s+(?P<rest>.+))?\s*[.!]*$",
                 text, flags=re.IGNORECASE)
    if not m:
        return text
    addr = m.group("addr") or ""
    rest = (m.group("rest") or "").strip()
    if rest:
        return f"{addr}{rest}"
    # the cancel takes the man's name after the verb ("cancel Ney"), never
    # as an address ("Ney, cancel" is unknown to the router)
    name = re.sub(r"^\s*(?:(?:marshal|general|prince)\s+)?", "", addr, flags=re.IGNORECASE).strip(" ,:")
    return f"cancel {name}" if name else "cancel"


def strip_hold_the_line_tail(text: str) -> str:
    """SFR-D10: "dig in at Milan and hold the line" → "dig in at Milan" —
    the hold is what the works are for, not a second order."""
    if not text:
        return text
    m = re.match(r"^(?P<head>.*\b(?:dig\s+in|fortify|entrench|throw\s+up\s+earthworks|earthworks|breastworks)\b.*?)"
                 r"[\s,]+and\s+hold\s+(?:the\s+line|firm|fast|there|position|your\s+ground|it|on|the\s+ground)\s*[.!]*$",
                 text, flags=re.IGNORECASE)
    return m.group("head") if m else text


def rewrite_drill_your_guard(text: str) -> str:
    """SFR-D9: "drill your guard" is a drill — the Guard is the men, never
    the hold family's `guard` keyword."""
    if not text:
        return text
    return re.sub(r"\b(?P<verb>drill|train|exercise|rest|parade|inspect|review)\s+(?:your|the|his|my|our)\s+"
                  r"(?:imperial\s+|old\s+|young\s+)?guards?\b", r"\g<verb> your men", text, count=1, flags=re.IGNORECASE)


def _uninflect(verb: str) -> str:
    low = verb.lower()
    if low.endswith("ies"):
        return low[:-3] + "y"
    if re.search(r"(?:ch|sh|ss|x|z)es$", low):
        return low[:-2]
    if low.endswith("s") and not low.endswith("ss"):
        return low[:-1]
    return low


def rewrite_guard_subject(text: str, sovereign: Optional[str]) -> str:
    """DD0-10: the Guard as a SUBJECT is the Emperor's corps — "Let the Guard
    attack Mack" / "The Guard will support Soult." / "the guard stays put" /
    "Have the Guard dig in." → "<Sovereign>, <order>". Dormant without a
    sovereign on the roster."""
    if not text or not sovereign:
        return text
    guard = r"the\s+(?:imperial\s+|old\s+|young\s+)?guard\b"
    m = re.match(r"^\s*(?:let|have|tell|order|get)\s+" + guard + r"\s+(?:to\s+)?(?P<rest>.+?)\s*[.!]*$",
                 text, flags=re.IGNORECASE)
    if m:
        return f"{sovereign}, {m.group('rest')}"
    m = re.match(r"^\s*" + guard + r"\s+(?:will|shall|is\s+to|should|must|can)\s+(?P<rest>.+?)\s*[.!]*$",
                 text, flags=re.IGNORECASE)
    if m and not re.match(r"^(?:not|never|no)\b", m.group("rest"), flags=re.IGNORECASE):
        return f"{sovereign}, {m.group('rest')}"
    m = re.match(r"^\s*" + guard + r"\s+(?P<verb>[a-z]+?(?:s|es))(?P<rest>\s+.*?)?\s*[.!]*$", text, flags=re.IGNORECASE)
    if m and m.group("verb").lower() not in ("is", "was", "has", "does", "needs", "wants"):
        return f"{sovereign}, {_uninflect(m.group('verb'))}{m.group('rest') or ''}"
    return text


def rewrite_bench_question(text: str) -> str:
    """SFR-H6 / DD0-9: "Commission another marshal" / "Promote someone to
    marshal" → "commission" — the bench, not a candidate named Another."""
    if not text:
        return text
    if re.match(r"^\s*(?:promote|commission|appoint|raise|name|make|elevate)\s+"
                r"(?:someone|somebody|anyone|another|a\s+new|a|one\s+of\s+(?:the|our)\s+generals|a\s+general|"
                r"another\s+general|one)\b.*?\b(?:marshal|marshalate)\b", text, flags=re.IGNORECASE):
        return "commission"
    if re.match(r"^\s*commission\s+(?:another|someone|somebody|anyone|a\s+new\s+one|one)\s*[.!]*$",
                text, flags=re.IGNORECASE):
        return "commission"
    return text


def strip_affordability_premise(text: str) -> str:
    """SFR-H5: "If we can still afford it, put a depot up in the Rhineland"
    — the build's own price check IS the premise; the clause is cut."""
    if not text:
        return text
    m = re.match(r"^\s*(?:if|provided|so\s+long\s+as|as\s+long\s+as|assuming)\s+(?:we|i|the\s+treasury|the\s+purse)\s+"
                 r"(?:can\s+(?:still\s+)?(?:afford|pay\s+for|manage|stretch\s+to|cover)|"
                 r"(?:still\s+)?(?:have|has)\s+the\s+(?:gold|money|funds|coin)(?:\s+for)?)\s*(?:it|that|this|them)?"
                 r"\s*[,;]?\s*(?P<rest>.+)$", text, flags=re.IGNORECASE)
    return m.group("rest").strip() if m else text


_BUILDING_RX = (r"(?P<thing>supply\s+depot|depot|fort(?:ress|ification|ifications)?|walls|barracks|"
                r"training\s+ground|drill\s+ground|parade\s+ground|stables?|watchtower|market|arsenal)")


def rewrite_build_idiom(text: str) -> str:
    """The third set's build register: "put a supply depot up in the
    Rhineland" / "I want a supply depot in Savoy" / "Stables in Burgundy,
    please" / "Fortress at Lorraine, build it" → "build <thing> in <place>"."""
    if not text:
        return text
    place = r"(?:the\s+)?(?P<place>[A-Z][\w'’-]*(?:[\s-][A-Z][\w'’-]*)?)"
    for pat in (
        r"^\s*(?:please\s+)?(?:put|throw|set|get|have|erect|raise)\s+(?:up\s+)?(?:a|an|the|some|new)\s+" + _BUILDING_RX
        + r"\s+(?:up\s+)?(?:built\s+|erected\s+|raised\s+)?(?:in|at)\s+" + place + r"\s*[.!]*$",
        r"^\s*I\s+(?:want|need|would\s+like)\s+(?:a|an|some|new)\s+" + _BUILDING_RX + r"\s+(?:built\s+)?(?:in|at)\s+" + place + r"\s*[.!]*$",
        r"^\s*(?:a\s+|an\s+)?" + _BUILDING_RX + r"\s+(?:in|at)\s+" + place
        + r"\s*,\s*(?:build\s+it|please|if\s+you\s+please|at\s+once)\s*[.!]*$",
        # the bare noun phrase ("Stables in Burgundy" — the please already cut)
        r"^\s*(?:a\s+|an\s+)?" + _BUILDING_RX + r"\s+(?:in|at)\s+" + place + r"\s*[.!]*$",
    ):
        m = re.match(pat, text, flags=re.IGNORECASE)
        if m:
            return f"build {m.group('thing').lower()} in {m.group('place')}"
    return text


def apply_all(text: str, friendly_names: Iterable[str], enemy_names: Iterable[str],
              place_names: Iterable[str], sovereign: Optional[str] = None) -> List[Tuple[str, str, str]]:
    """Every rewrite in order; returns [(rule, before, after)] for the ones
    that fired, the caller reads the final text off the last row."""
    known = list(friendly_names) + list(enemy_names) + list(place_names)
    steps = (
        ("strip_please_and_urgency", lambda t: strip_please_and_urgency(t)),
        ("strip_dash_aside", lambda t: strip_dash_aside(t, known)),
        ("strip_because_tail", lambda t: strip_because_tail(t, known)),
        ("strip_affordability_premise", lambda t: strip_affordability_premise(t)),
        ("rewrite_self_correction", lambda t: rewrite_self_correction(t)),
        ("rewrite_arrival_wait", lambda t: rewrite_arrival_wait(t)),
        ("rewrite_second_in_support", lambda t: rewrite_second_in_support(t, friendly_names)),
        ("rewrite_send_marshal", lambda t: rewrite_send_marshal(t, friendly_names)),
        ("rewrite_guard_subject", lambda t: rewrite_guard_subject(t, sovereign)),
        ("rewrite_drill_your_guard", lambda t: rewrite_drill_your_guard(t)),
        ("rewrite_kill", lambda t: rewrite_kill(t, enemy_names)),
        ("rewrite_attack_idioms", lambda t: rewrite_attack_idioms(t, friendly_names, enemy_names)),
        ("strip_stop_chasing", lambda t: strip_stop_chasing(t, enemy_names)),
        ("rewrite_hold_where_you_are", lambda t: rewrite_hold_where_you_are(t)),
        ("strip_hold_the_line_tail", lambda t: strip_hold_the_line_tail(t)),
        ("rewrite_take_back", lambda t: rewrite_take_back(t)),
        ("rewrite_return_to", lambda t: rewrite_return_to(t)),
        ("rewrite_reward_idiom", lambda t: rewrite_reward_idiom(t, friendly_names)),
        ("rewrite_bench_question", lambda t: rewrite_bench_question(t)),
        ("rewrite_pass_a_law", lambda t: rewrite_pass_a_law(t)),
        ("rewrite_build_idiom", lambda t: rewrite_build_idiom(t)),
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
