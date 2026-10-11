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
_PLEASE_AFTER_ADDRESS_RE = re.compile(r"^(\s*(?:[Mm]arshal\s+)?[A-Za-z][\w'’-]*,\s*)(?:please|kindly|pray)[,\s]+",
                                      re.IGNORECASE)


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
    # S4 part 3 (DD0-17): an aside that IS the order — "Lannes — squares.",
    # "Tighten the leash on Holland — lower its autonomy" — is never cut:
    # the field's one-word orders and the words of state stay.
    if re.search(r"\b(?:squares?|charge|halt|stop|hold|fire|march|forward|scout|retreat|withdraw|"
                 r"autonomy|vassal|tribute|gold|law|peace|war|treaty|alliance|mission|envoy|terms)\b",
                 aside, re.IGNORECASE):
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
    # DD0-18 (c) (S4 part 4): "Shift Murat's horse to Lorraine", "Transfer
    # Bernadotte's corps to Berlin", "Advance Davout to Gelderland", "Pull
    # Bernadotte back out of Franconia to Frankfurt".
    m = re.match(
        r"^\s*(?:send|pull|bring|get|dispatch|order|shift|withdraw|transfer|advance|move|march|take|lead|direct)\s+(?:marshal\s+)?"
        r"(?P<name>" + alt + r")(?:['’]s\s+(?:corps|men|horse|cavalry|division|army|troops|guns|infantry|column))?"
        r"\s+(?:back\s+|over\s+|up\s+|down\s+|across\s+)?(?:out\s+of\s+[A-Za-z][\w'’-]*\s+)?"
        r"(?:to|toward|towards|into|for|upon)\s+(?P<where>[A-Za-z][\w'’ -]{2,40}?)\s*[.!]*$",
        text, flags=re.IGNORECASE)
    if not m or _ORDER_VERB_RE.match(m.group("where").strip()):
        # "send Murat to scout Munich" — the verb after `to` is the order
        return text
    name = next(n for n in friendly_names if str(n).lower() == m.group("name").lower())
    return f"{name}, move to {m.group('where').strip()}"


def rewrite_kill(text: str, enemy_names: Iterable[str]) -> str:
    # DD0-19 (S4 part 4): every form a foe is named by — "go kill archduke
    # john" (the surname with its title, spaced).
    alt = _foe_alt(enemy_names)
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
    # DD0-18 (c) (S4 part 4): "An estate for Marshal Soult, with the Emperor's
    # thanks.", "Bernadotte, an estate, grudgingly.", "Estate for Ney.",
    # "title davout", "Lannes receives a grant of land".
    desk = re.match(
        r"^\s*(?:(?:an?|the)\s+)?(?P<thing>estate|title|duchy|dukedom|reward|grant\s+of\s+land|lands?)\s+for\s+"
        r"(?:marshal\s+)?(?P<name>" + alt + r")\b.*$"
        r"|^\s*(?:marshal\s+)?(?P<name2>" + alt + r")\s*[,:—–-]\s*(?:an?\s+)?(?:estate|title|duchy|dukedom)\b.*$"
        r"|^\s*(?:estate|title|duchy)\s+(?:for\s+)?(?P<name3>" + alt + r")\s*[.!]*$"
        r"|^\s*(?:berthier,?\s+)?(?:see\s+that\s+)?(?:marshal\s+)?(?P<name4>" + alt + r")\s+(?:receives|gets|is\s+to\s+receive|is\s+to\s+have|shall\s+have)\s+"
        r"(?:an?\s+)?(?:estate|title|duchy|grant\s+of\s+land|reward)\b.*$",
        text, flags=re.IGNORECASE)
    if desk:
        typed = desk.group("name") or desk.group("name2") or desk.group("name3") or desk.group("name4")
        name = next(n for n in friendly_names if str(n).lower() == typed.lower())
        return f"reward {name}"
    m = re.match(
        r"^\s*(?:give\s+(?:marshal\s+)?(?P<n1>" + alt + r")\s+"
        r"(?:an?\s+)?(?:estate|title|duchy|dukedom|principality|county|reward)\b"
        r"|make\s+(?:marshal\s+)?(?P<n2>" + alt + r")\s+(?:a\s+|the\s+)?(?:duke|prince|count|marquis|baron|peer)\b"
        r"|reward\s+(?:marshal\s+)?(?P<n3>" + alt + r")\s+with\s+(?:an?\s+)?(?:title|estate|duchy)\b"
        r"|reward\s+(?:marshal\s+)?(?P<n4>" + alt + r")\s+for\s+\S"
        # DD0-17 (S4 part 3): "reward soult estate"; "Ney has earned a
        # title; give him one."
        r"|reward\s+(?:marshal\s+)?(?P<n5>" + alt + r")\s+(?:an?\s+)?(?:title|estate|duchy|dukedom|pension|rente)\b"
        r"|(?:marshal\s+)?(?P<n6>" + alt + r")\s+has\s+(?:well\s+)?earned\s+(?:an?\s+|his\s+)?(?:title|estate|duchy|reward|dukedom)\b)",
        text, flags=re.IGNORECASE)
    if not m:
        return text
    typed = (m.group("n1") or m.group("n2") or m.group("n3") or m.group("n4")
             or m.group("n5") or m.group("n6"))
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
    out = _sub_foe(r"\bfall\s+(?:up)?on\s+(?:the\s+)?(?P<foe>" + foes + r")(?:['’]s\s+(?:flank|flanks|rear|centre|center|left|right|line|column|wing))?\b",
                   "attack {foe}", out, enemy_names)
    # DD0-20 (S5): "assault Mack's position" (the ground he holds is the
    # man), "Ney, break Mack.", "assail Archduke John", "run Mack to
    # ground" (the pursuit), "goes in against Swabia" (the attack on the
    # ground). `break camp` / `break off` stay their own idioms.
    # (narrow: the ground he holds — never "Mack's line of retreat", CRT-6's
    # pin, nor his army, which a statement may name)
    out = _sub_foe(r"\b(?P<foe>" + foes + r")['’]s\s+(?:position|positions|camp|works|entrenchments)\b(?!\s+of\b)",
                   "{foe}", out, enemy_names)
    out = _sub_foe(r"\b(?:assail|assault|smite|storm)\s+(?:the\s+)?(?P<foe>" + foes + r")\b", "attack {foe}", out, enemy_names)
    out = _sub_foe(r"\bbreak\s+(?:the\s+)?(?P<foe>" + foes + r")\b(?!\s+(?:off|camp))", "attack {foe}", out, enemy_names)
    out = _sub_foe(r"\brun\s+(?:the\s+)?(?P<foe>" + foes + r")\s+to\s+ground\b", "pursue {foe}", out, enemy_names)
    out = re.sub(r"\b(?:goes|go|went)\s+in\s+(?:against|at|on|upon)\s+(?:the\s+)?", "attack ", out, count=1, flags=re.IGNORECASE)
    out = _sub_foe(r"\b(?:keep|stay)\s+on\s+(?P<foe>" + foes + r")['’]s\s+(?:heels|tail|trail)\b", "pursue {foe}", out, enemy_names)
    # DD0-16 / DD0-17 (S4 part 3): "dog Mack's heels", "keep after the
    # Austrians under Mack" (the "after" read as a condition before).
    out = _sub_foe(r"\b(?:dog|hound|harry)\s+(?P<foe>" + foes + r")['’]s\s+(?:heels|tail|trail|rear|retreat)\b", "pursue {foe}", out, enemy_names)
    # ("get after <foe>" is the live parser's by IQ-9's cassette gate and is
    # deliberately NOT read here; "go after" is the chain's own pursue word.)
    out = _sub_foe(r"\b(?:keep|stay|press)\s+(?:hard\s+)?after\s+(?:the\s+\w+\s+(?:under|of|led\s+by)\s+)?(?P<foe>" + foes + r")\b",
                   "pursue {foe}", out, enemy_names)
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
# DD0-20 (S5): "Send 50 gold to the Kingdom of Italy's treasury." — gold
# sent TO a court is the investment (it read as the treasury report).
_SEND_GOLD_TO_RE = re.compile(
    r"^\s*(?:send|give|transfer|remit|pay|grant|forward)\s+(?:\d[\d,]*\s*)?(?:gold|g|livres|francs|some\s+gold|more\s+gold)\s+"
    r"(?:to|into)\s+(?:the\s+)?(?P<court>.+?)(?:['’]s\s+(?:treasury|coffers|purse|exchequer|court))?\s*[.!]*$",
    re.IGNORECASE)


def rewrite_invest_gold(text: str) -> str:
    m = _INVEST_GOLD_RE.match(text or "") or _SEND_GOLD_TO_RE.match(text or "")
    return f"invest in {m.group('court')}" if m else text


_TRAILING_END_TURN_RE = re.compile(
    r"^(?P<head>.*?)[,;—–-]+\s*(?:next\s+turn|end\s+(?:the\s+)?turn|end\s+of\s+turn)\s*[.!]*$", re.IGNORECASE)


_END_TURN_OTHER_WORDS_RX = re.compile(
    r"(?:let\s+the\s+turn\s+end|let\s+the\s+day\s+end|close\s+the\s+day|that\s+is\s+all\s+for\s+today|"
    r"that'?s\s+all\s+for\s+today|that\s+will\s+be\s+all\s+for\s+today|we\s+are\s+done\s+for\s+today|"
    r"call\s+it\s+a\s+day|the\s+day\s+is\s+done|end\s+the\s+day|finish\s+the\s+turn|conclude\s+the\s+turn|"
    r"advance\s+the\s+turn|pass\s+the\s+turn|the\s+turn\s+is\s+over|wrap\s+up\s+the\s+turn|"
    r"let\s+the\s+turn\s+pass|move\s+(?:on\s+)?to\s+the\s+next\s+turn|on\s+to\s+the\s+next\s+turn|"
    # DD0-18 (c) (S4 part 4, October 11, 2026): "That is all for today,
    # Berthier. Close the turn.", "Done. Advance the clock." — the closing
    # word and the clock; the fillers before them ("done", "that is all",
    # "very well") are the desk's too, never an order.
    r"close\s+the\s+turn|advance\s+the\s+clock|turn\s+the\s+clock|done|we\s+are\s+done|that\s+is\s+all|"
    r"that'?s\s+all|that\s+will\s+be\s+all|very\s+well|good|enough\s+for\s+today|that'?s\s+it|"
    r"nothing\s+more|no\s+more\s+orders|the\s+turn\s+is\s+done|close\s+out\s+the\s+turn)",
    re.IGNORECASE)


def end_turn_in_other_words(command_lower: str) -> bool:
    """DD0-17 (S4 part 3): "Let the turn end.", "That is all for today,
    Berthier. Close the day." — the whole line is end-turn phrasings in
    other words (the two-word vocabulary is the client's gate; the chain
    answers with the desk's ask, never the turn)."""
    cl = re.sub(r"\b(?:berthier|sire)\b", " ", command_lower or "", flags=re.IGNORECASE)
    parts = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"[,;.!]+", cl)]
    parts = [p for p in parts if p]
    return bool(parts) and all(_END_TURN_OTHER_WORDS_RX.fullmatch(p) for p in parts)


def rewrite_naval_landing(text: str) -> str:
    """DD0-17 (S4 part 3): "naval landing ireland" / "landing at Ulster" →
    "land in <place>" (the fuzzy scan read "landing" as a marshal's name)."""
    m = re.match(r"^\s*(?:a\s+)?(?:naval\s+)?landing\s+(?:in|at|on)?\s*(?P<place>[A-Za-z][\w'’ -]+?)\s*[.!]*$",
                 text or "", flags=re.IGNORECASE)
    return f"land in {m.group('place').strip()}" if m else text


def rewrite_open_talks(text: str) -> str:
    """DD0-17 (S4 part 3): "Talleyrand: open talks with Russia" → the
    Cabinet's own "negotiate with"."""
    if not text:
        return text
    return re.sub(r"\bopen\s+(?:talks|negotiations|a\s+dialogue|discussions|a\s+channel)\s+with\b",
                  "negotiate with", text, count=1, flags=re.IGNORECASE)


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
    # DD0-19 (S4 part 4): the inflected forms — "Bernadotte leaves 3000 men
    # to hold Franconia" had become the HOLD.
    r"\b(?:drop\s+off|drops\s+off|leaves?|detach(?:es)?|posts?|stations?|spares?)\b.{0,30}?"
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
    # DD0-17 (S4 part 3): "Lannes — squares.", "Bernadotte, square up — Deroy
    # has horse" (the dash after the name, the "up", a dash tail).
    return bool("cavalry" in cl
                or re.match(r"^\s*(?:(?:marshal\s+)?[a-z][\w'’-]*\s*(?:[,:]|\s+[—–-]+)\s*)?(?:form\s+)?squares?(?:\s+up)?"
                            r"\s*(?:[—–-].*)?[.!]*$", cl))


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
                or re.search(r"\b(?:mount|make|stage)\s+a\s+landing\b", cl)
                # DD0-17 (S4 part 3): "naval landing ireland".
                or re.search(r"\bnaval\s+landing\b|\blanding\s+(?:in|at|on)\s+\w", cl))


def scout_idiom(command_lower: str) -> bool:
    # DD0-11 / DD0-17 (S4 part 3): "eyes only", "patrol toward Bern".
    # DD0-18 (c) (S4 part 4): "probe toward Bern and report", "screen toward
    # Tyrol" (a screen AIMED at a place is a reconnaissance; "screen the
    # retreat" stays the retreat branch's guard), "reconnaissance toward",
    # "recon dresden", "push scouts into".
    return bool(re.search(r"\beyes\s+(?:on|only)\b|\bfind\s+out\b|\breport\s+back\b|\bsend\s+riders\b"
                          r"|\bpatrol(?:s|led|ling)?\b"
                          # (a bare "probe Swabia" stays unrouted — CX-R1's hand-list pin;
                          # the probe AIMED somewhere is the reconnaissance)
                          r"|\bprob(?:e|es|ed|ing)\s+(?:out\s+)?(?:toward|towards|to|into|along)\b"
                          r"|\bscreen\s+(?:toward|towards|to|into)\b"
                          r"|\breconnaissance\b|\brecon\b|\breconnoit(?:re|er)\b|\bpush\s+scouts\b|\bsend\s+patrols\b",
                          command_lower or ""))


def earthworks_order(command_lower: str) -> bool:
    return bool(re.search(r"\b(?:earthworks|breastworks)\b", command_lower or ""))


def unfortify_idiom(command_lower: str) -> bool:
    # DD0-18 (a) (S4 part 4, October 11, 2026): "strike camp" / "break camp"
    # — the works given up in the soldier's words; `strike` alone is CRT-11's
    # battle verb, and the chain reads this idiom BEFORE it when no foe is
    # named (`_chain_read_action`).
    cl = command_lower or ""
    if re.search(r"\b(?:abandon|leave|quit|give\s+up)\s+(?:the\s+|your\s+|his\s+)?"
                 r"(?:entrenchments?|earthworks|works|fortifications?|breastworks)\b", cl):
        return True
    # "strike camp and march to Bohemia" is ONE order — the march (D10's
    # pin, attack_vocabulary's note); the camp struck with nothing after it,
    # or with the works abandoned, is the unfortify.
    camp = re.search(r"\b(?:strike|break|strikes|breaks)\s+camp\b(?P<rest>.*)$", cl)
    if not camp:
        return False
    return not re.search(r"\b(?:march|move|go|head|advance|proceed|ride|set\s+out|to|toward|towards|for|into)\b",
                         camp.group("rest"))


def drill_idiom(command_lower: str) -> bool:
    return bool(re.search(r"\bthrough\s+(?:its|their|his)\s+paces\b|\bmusketry\b|\bpracti[sc]e\b",
                          command_lower or ""))


def invest_gold(command_lower: str, known_nations_lower) -> bool:
    cl = command_lower or ""
    nations = [n for n in (known_nations_lower or []) if n]
    if not nations or not re.search(r"\bgold\b|\binvest\b", cl):
        return False
    alt = "|".join(re.escape(n) for n in nations)
    return bool(re.search(r"\b(?:invest|put|pour|sink)\b.{0,30}\b(?:in|into)\s+(?:the\s+)?(?:" + alt + r")\b", cl)
                # DD0-17 (S4 part 3): the terse "invest holland 50".
                or re.match(r"^\s*invest\s+(?:in\s+)?(?:the\s+)?(?:" + alt + r")\s+\d", cl))


def march_idiom(command_lower: str) -> bool:
    """"relocate his corps to", "bring the corps back to", "get to Munich";
    DD0-18 (c): "get yourself to Swabia", "get the men to Lorraine", "get
    your corps over to Nassau", "shift to Piedmont", "on to Swabia"."""
    return bool(re.search(r"\b(?:relocate|redeploy)\b|\b(?:bring|get|pull|take)\b.{0,40}\bback\s+to\b"
                          r"|\bget\s+(?:to|into)\b"
                          r"|\bget\s+(?:yourself|yourselves|the\s+men|the\s+corps|your\s+(?:corps|men|horse|cavalry|division|guns))"
                          r"\s+(?:up\s+|down\s+|over\s+|across\s+)?(?:to|into)\b"
                          r"|\bshift\s+(?:up\s+|down\s+|over\s+)?(?:to|into)\b"
                          r"|^\s*(?:(?:marshal\s+)?[a-z][\w'’-]*\s*[,:]\s*)?on\s+to\s+[a-z]",
                          command_lower or ""))


_PRONOUN_ORDER_TAIL_RX = re.compile(
    r"^(?:do\s+it|make\s+it\s+so|see\s+to\s+it|see\s+to\s+that|make\s+it\s+happen|get\s+it\s+done|do\s+so|"
    r"go\s+ahead|proceed|do\s+that|make\s+it\s+happen|let\s+it\s+be\s+done)\s*[.!]*$", re.IGNORECASE)
_SCOUT_FOR_HIM_TAIL_RX = re.compile(r"^(?:scout|look|search|send\s+riders)\s+for\s+(?:him|them|it|her)\s*[.!]*$",
                                    re.IGNORECASE)
_ORDER_TAIL_TIME_RX = re.compile(r"\s+(?:yet|already|still|this\s+turn|next\s+turn|today|tonight|by\s+now|now|at\s+once)\b",
                                 re.IGNORECASE)


def _order_from_question(q: str, alt: str) -> Optional[str]:
    """"Can Lannes be in Rhineland this turn?" → "Lannes, move to Rhineland";
    "Why hasn't Massena attacked Archduke John yet?" → "Massena, attack
    Archduke John"."""
    m = re.match(
        r"^\s*(?:can|could|will|would|should|is|has|does|did|"
        r"why\s+(?:hasn't|has\s+not|isn't|is\s+not|doesn't|does\s+not|didn't|did\s+not|won't|will\s+not|can't|cannot|couldn't)|"
        r"why\s+not\s+(?:have|let))\s+(?:marshal\s+)?(?P<name>" + alt + r")\s+(?P<pred>.+?)\s*\?\s*$",
        q.strip(), flags=re.IGNORECASE)
    if not m:
        return None
    name, pred = m.group("name"), m.group("pred").strip()
    pred = re.sub(r"^(?:be\s+able\s+to|manage\s+to|get\s+to|please|kindly)\s+", "", pred, flags=re.IGNORECASE)
    pred = _ORDER_TAIL_TIME_RX.sub("", pred).strip(" ,")
    be_in = re.match(r"^(?:be\s+)?(?:in|at|near|inside)\s+(?P<place>.+)$", pred, flags=re.IGNORECASE)
    if be_in:
        return f"{name}, move to {be_in.group('place').strip()}"
    go_to = re.match(r"^(?:go|march|move|head|get|ride|advance|proceed)\s+(?:up\s+|over\s+|on\s+|down\s+)?"
                     r"(?:to|into|toward|towards|for)\s+(?P<place>.+)$", pred, flags=re.IGNORECASE)
    if go_to:
        return f"{name}, move to {go_to.group('place').strip()}"
    vo = re.match(r"^(?P<verb>[a-z]+)\s+(?P<obj>.+)$", pred, flags=re.IGNORECASE)
    if not vo:
        return None
    verb = _base_verb(vo.group("verb").lower())
    if not verb:
        return None
    return f"{name}, {verb} {vo.group('obj').strip()}"


def _base_verb(word: str) -> Optional[str]:
    """"attacked" → "attack", "moved" → "move", "marches" → "march" — an
    order verb's base form, or None when no order verb is spelt there."""
    low = word.lower()
    candidates = [low, _uninflect(low)]
    if low.endswith("ed"):
        candidates += [low[:-2], low[:-1]]
        if len(low) > 4 and low[-3] == low[-4]:
            candidates.append(low[:-3])          # "stopped" → "stop"
    if low.endswith("ing"):
        candidates += [low[:-3], low[:-3] + "e"]
    for cand in candidates:
        if cand and _ORDER_VERB_RE.fullmatch(cand):
            return cand
    return None


def split_question_and_order(text: str, friendly_names: Iterable[str],
                             enemy_names: Iterable[str] = ()) -> Optional[Tuple[str, Optional[str]]]:
    """"what's in Tyrol? Massena, find out" → ("what's in Tyrol?", "Massena, find out").

    DD0-14 (S4 part 3, October 10, 2026): the order BEHIND a question that
    names no marshal — "Can Lannes be in Rhineland this turn? Make it so.",
    "Why hasn't Massena attacked Archduke John yet? Do it.", "Where is
    Kutuzov? Scout for him." — is the order the question itself names:
    the line IS that order (the first element), with no sequel (None)."""
    alt = _name_alt(friendly_names)
    if not text or not alt or "?" not in text:
        return None
    m = re.match(r"^(?P<q>[^?]+\?)\s+(?P<tail>(?:marshal\s+)?(?:" + alt + r")[,:]?\s+\S.*)$",
                 text, flags=re.IGNORECASE)
    if m:
        return m.group("q").strip(), m.group("tail").strip()
    m = re.match(r"^(?P<q>[^?]+\?)\s+(?P<tail>\S.*)$", text, flags=re.IGNORECASE)
    if not m:
        return None
    q, tail = m.group("q").strip(), m.group("tail").strip()
    if _PRONOUN_ORDER_TAIL_RX.match(tail):
        order = _order_from_question(q, alt)
        return (order, None) if order else None
    if _SCOUT_FOR_HIM_TAIL_RX.match(tail):
        who = re.match(r"^\s*where(?:'s|’s|\s+is|\s+are)\s+(?P<who>.+?)\s*\?\s*$", q, flags=re.IGNORECASE)
        # Only a foe the board can SEE: a scout is aimed at a province, so
        # "Where is Kutuzov? Scout for him." with Kutuzov out of sight keeps
        # the question, which the desk answers honestly (no word of him).
        from backend.ai.reading import foe_named_in
        if who and foe_named_in(who.group("who"), enemy_names):
            return f"scout for {who.group('who').strip()}", None
    return None


# ── DD-0 S4 (October 10, 2026): the vocabulary the ledger, the six keyless
# shrugs and the sixteen open command rows asked for (rules
# SYSTEMS_REFERENCE.md §104). Each pure, each inert when its shape is absent.

_LAW_NOUN_RX = re.compile(r"\b(?:law|act|reform|bill|ordinance|decree)\b", re.IGNORECASE)


def rewrite_pass_a_law(text: str) -> str:
    """SFR-H2: "pass the Staff law" / "adopt the Staff" / "decree the
    conscription act" → "enact <law>" — the law router knows `enact` /
    `reenact` / `repeal` only, and "pass" fell to the proper-name ask.
    Only a line that names a law (the noun, or "law" somewhere in it)."""
    if not text:
        return text
    # DD0-20 (S5): "Berthier, draft and enact the Staff reform." — the
    # drafting is the enacting's own preface.
    drafted = re.match(r"^\s*(?:berthier,?\s+)?(?:draft|draw\s+up|write|prepare|frame)(?:\s+up)?\s+and\s+"
                       r"(?:enact|pass|adopt|promulgate)\s+(?:the\s+)?(?P<name>.+?)\s*(?:\b(?:reform|law|act|bill)\b)?\s*[.!]*$",
                       text, flags=re.IGNORECASE)
    if drafted and drafted.group("name").strip():
        return f"enact {drafted.group('name').strip()}"
    # DD0-17 (S4 part 3): "Establish the Grand Quartier General" (a law named
    # by its proper name, no law noun), "Berthier, the Staff law is to be
    # enacted this turn", "Let the Artillery Reserve be made law".
    est = re.match(r"^\s*(?i:berthier,?\s+)?(?i:please\s+)?(?i:establish|institute|found|set\s+up|create)\s+"
                   r"(?i:the\s+)?(?P<name>[A-Z][\w'’-]*(?:\s+(?:of|the|des|de|du|la|le)\s+)?(?:\s*[A-Z][\w'’-]*)+)\s*[.!]*$", text)
    if est and not _ORDER_VERB_RE.search(est.group("name")):
        return f"enact {est.group('name').strip()}"
    # DD0-19 (S4 part 4): "establish the artillery reserve" — the law named
    # in lower case; two words at least, never a building or a garrison.
    est_low = re.match(r"^\s*(?:berthier,?\s+)?(?:please\s+)?(?:establish|institute)\s+(?:the\s+)?"
                       r"(?P<name>[a-z][\w'’-]*(?:\s+[a-z][\w'’-]*)+)\s*[.!]*$", text, flags=re.IGNORECASE)
    if (est_low and not _ORDER_VERB_RE.search(est_low.group("name"))
            and not re.search(_BUILDING_RX + r"|\b(?:garrison|camp|base|line|position|post|outpost|magazine|hospital)\b",
                              est_low.group("name"), flags=re.IGNORECASE)):
        return f"enact {est_low.group('name').strip()}"
    passive = re.match(r"^\s*(?:berthier,?\s+|sire,?\s+)?(?:the\s+)?(?P<name>.+?)\s+(?:law\s+|act\s+|reform\s+)?"
                       r"(?:is|are)\s+to\s+be\s+(?:enacted|passed|adopted|made\s+law|put\s+through)\b.*$",
                       text, flags=re.IGNORECASE)
    if passive:
        return f"enact {passive.group('name').strip()}"
    let = re.match(r"^\s*let\s+(?:the\s+)?(?P<name>.+?)\s+be\s+(?:made\s+law|enacted|passed|adopted)\b.*$",
                   text, flags=re.IGNORECASE)
    if let:
        return f"enact {let.group('name').strip()}"
    # DD0-18 (c) (S4 part 4): "the staff law - enact", "Staff: enact",
    # "put the Staff law into effect".
    dash = re.match(r"^\s*(?:the\s+)?(?P<name>[A-Za-z][\w'’ ]{1,40}?)\s*(?:law\s*)?[-—–:]\s*(?:enact|pass|adopt)(?:\s+it)?\s*[.!]*$",
                    text, flags=re.IGNORECASE)
    if dash and not _ORDER_VERB_RE.match(dash.group("name").strip().split()[0]):
        return f"enact {dash.group('name').strip()}"
    effect = re.match(r"^\s*(?:berthier,?\s+)?(?:please\s+)?(?:put|bring)\s+(?:the\s+)?(?P<name>.+?)\s+(?:law\s+)?into\s+(?:effect|force|law)\b.*$",
                      text, flags=re.IGNORECASE)
    if effect:
        return f"enact {effect.group('name').strip()}"
    if not _LAW_NOUN_RX.search(text):
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
    # DD0-20 (S5): "the Guard and I ride for Franche-Comte" — the Emperor
    # with his Guard is the Emperor's corps (it read a region named "And I
    # Ride For Franche-Comte").
    m = re.match(r"^\s*(?:" + guard + r"\s+and\s+(?:i|myself)|i\s+and\s+" + guard + r"|" + guard + r"\s+with\s+me)\s+"
                 r"(?P<rest>.+?)\s*[.!]*$", text, flags=re.IGNORECASE)
    if m and not re.match(r"^(?:not|never|no)\b", m.group("rest"), flags=re.IGNORECASE):
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
        + r"\s+(?:up\s+)?(?:built\s+|erected\s+|raised\s+)?(?:in|at)\s+" + place
        # DD0-19 (S4 part 4): "Put a depot at Franconia for Bernadotte."
        + r"(?:\s+for\s+(?:marshal\s+)?[A-Z][\w'’-]*(?:['’]s\s+\w+)?)?\s*[.!]*$",
        r"^\s*I\s+(?:want|need|would\s+like)\s+(?:a|an|some|new)\s+" + _BUILDING_RX + r"\s+(?:built\s+)?(?:in|at)\s+" + place + r"\s*[.!]*$",
        r"^\s*(?:a\s+|an\s+)?" + _BUILDING_RX + r"\s+(?:in|at)\s+" + place
        + r"\s*,\s*(?:build\s+(?:it|them|one|some)|please|if\s+you\s+please|at\s+once)\s*[.!]*$",
        # the bare noun phrase ("Stables in Burgundy" — the please already cut;
        # DD0-20: "Berthier, a supply depot in Rhineland.")
        r"^\s*(?:berthier,?\s+)?(?:a\s+|an\s+)?" + _BUILDING_RX + r"\s+(?:in|at)\s+" + place + r"\s*[.!]*$",
        # DD0-18 (c) (S4 part 4): "Fort at Milan, Massena will need it." — a
        # statement behind the comma that gives no order of its own.
        r"^\s*(?:a\s+|an\s+)?" + _BUILDING_RX + r"\s+(?:in|at)\s+" + place + r"\s*[,;—–-]\s*(?P<tail>.+?)\s*[.!]*$",
    ):
        m = re.match(pat, text, flags=re.IGNORECASE)
        if m:
            tail = m.groupdict().get("tail")
            if tail and (_ORDER_VERB_RE.search(tail) or re.search(r"\b(?:no|not|never|don'?t|unless|if)\b", tail, re.I)):
                continue
            return f"build {m.group('thing').lower()} in {m.group('place')}"
    return text


def rewrite_hand_over(text: str) -> str:
    """DD0-18 (c) (S4 part 4): "Hand Flanders over to Holland." / "hand over
    Savoy to Sardinia" → "cede Flanders to Holland"."""
    if not text:
        return text
    # (DD0-19: "give savoy to sardinia" — the lowercase forms too; a man's
    # name as the thing given is the reward desk's and never reaches here)
    m = re.match(r"^\s*(?i:hand|turn|give)\s+(?i:over\s+)?(?P<place>[A-Za-z][\w'’-]*(?:[\s-][A-Za-z][\w'’-]*)?)\s+(?i:over\s+)?"
                 r"(?i:to)\s+(?i:the\s+)?(?P<court>[A-Za-z][\w'’ -]{2,30}?)\s*[.!]*$", text)
    if not m or _ORDER_VERB_RE.match(m.group("place").split()[0].lower()):
        return text
    if re.match(r"^(?:a|an|the|him|them|it|us|me|more|less|some)\b", m.group("place"), re.IGNORECASE):
        return text
    return f"cede {m.group('place')} to {m.group('court')}"


# ── DD0-18 (c)/(e) (S4 part 4, October 11, 2026): the fifth set's register.

def rewrite_retire_on(text: str) -> str:
    """"Soult, retire on Franche-Comte." — a retire WITH a destination is the
    march (FA-80's rule: `retire` bare is the retreat verb; `retire to /
    towards <place>` the plain-speech move list already carries, as the
    strategic MOVE_TO). Only the `on / upon` form is restated, to the form
    that road reads — never to a tactical `move to`."""
    if not text:
        return text
    return re.sub(r"\bretire\s+(?:on|upon)\s+(?=[A-Za-z])", "retire to ", text, count=1, flags=re.IGNORECASE)


def rewrite_pull_back(text: str, friendly_names: Iterable[str]) -> str:
    """"Pull Ney back behind the Rhine." / "pull back Davout" — no
    destination named: the retreat; with one, `rewrite_send_marshal` has
    already read the march."""
    alt = _name_alt(friendly_names)
    if not text or not alt:
        return text
    m = re.match(r"^\s*pull\s+(?:marshal\s+)?(?P<name>" + alt + r")\s+back\b(?P<rest>.*)$"
                 r"|^\s*pull\s+back\s+(?:marshal\s+)?(?P<name2>" + alt + r")\b(?P<rest2>.*)$",
                 text, flags=re.IGNORECASE)
    if not m:
        return text
    rest = (m.group("rest") or m.group("rest2") or "")
    if re.search(r"\b(?:to|into|toward|towards)\b", rest, flags=re.IGNORECASE):
        return text
    typed = m.group("name") or m.group("name2")
    name = next(n for n in friendly_names if str(n).lower() == typed.lower())
    return f"{name}, retreat"


def rewrite_break_off_rejoin(text: str, friendly_names: Iterable[str]) -> str:
    """"Lannes, break off, rejoin Soult at Lorraine." → "Lannes, move to
    Lorraine" (the man was read as the place); "rejoin Soult at Lorraine" →
    the march; a bare "break off" is the retreat."""
    alt = _name_alt(friendly_names)
    if not text or not alt:
        return text
    m = re.match(r"^(?P<head>\s*(?:(?:marshal\s+)?(?:" + alt + r")\s*[,:]\s*)?)"
                 # ("join Davout at Lorraine" stays the SUPPORT it is — the
                 # metamorphic corpus's own row; only a REJOINING is the march)
                 r"(?:break\s+off[,;]?\s*(?:and\s+)?)?(?:rejoin|fall\s+back\s+on)\s+"
                 r"(?:marshal\s+)?(?:" + alt + r")\s+(?:at|in)\s+(?P<place>[A-Z][\w'’-]*(?:[\s-][A-Z][\w'’-]*)?)\s*[.!]*$",
                 text, flags=re.IGNORECASE)
    if m:
        return f"{m.group('head')}move to {m.group('place')}"
    m = re.match(r"^(?P<head>\s*(?:(?:marshal\s+)?(?:" + alt + r")\s*[,:]\s*)?)break\s+off\s*[.!]*$",
                 text, flags=re.IGNORECASE)
    if m:
        return f"{m.group('head')}retreat"
    return text


def rewrite_on_to_the_enemy(text: str, friendly_names: Iterable[str]) -> str:
    """"Ney, on to Swabia and the enemy." → "Ney, attack Swabia"."""
    alt = _name_alt(friendly_names)
    if not text or not alt:
        return text
    m = re.match(r"^(?P<head>\s*(?:(?:marshal\s+)?(?:" + alt + r")\s*[,:]\s*)?)on\s+to\s+"
                 r"(?P<place>[A-Z][\w'’-]*(?:[\s-][A-Z][\w'’-]*)?)\s+and\s+(?:the\s+)?(?:enemy|foe|austrians|russians|enemy's\s+army)\s*[.!]*$",
                 text, flags=re.IGNORECASE)
    return f"{m.group('head')}attack {m.group('place')}" if m else text


_NEGATED_HOLD_RX_T = (r"^\s*(?:marshal\s+)?(?P<name>{names})\s*[,:]?\s+"
                      r"(?:dont|don'?t|do\s+not|is\s+not\s+to|must\s+not|mustn'?t|should\s+not|shouldn'?t|"
                      r"will\s+not|won'?t|shall\s+not|isn'?t\s+to)\s*"
                      r"(?:move|march|advance|budge|stir|go\s+anywhere|leave|shift|move\s+an\s+inch|move\s+a\s+step)?"
                      r"(?:\s+(?:this\s+turn|yet|today|tonight|anywhere|an\s+inch|a\s+step|at\s+all|"
                      r"from\s+(?:there|here|where\s+he\s+is|[A-Za-z][\w'’-]*)))?\s*[.!]*$")


def rewrite_negated_hold(text: str, friendly_names: Iterable[str]) -> str:
    """DD0-18 (e): "lannes dont move" — a bare prohibition on moving, with
    nothing else in the line and no destination, IS the hold ("Lannes,
    hold"). A negated order with an object ("don't move to Lorraine", "do not
    attack Mack") is PARSE-NEG's and never reaches this shape."""
    alt = _name_alt(friendly_names)
    if not text or not alt:
        return text
    m = re.match(_NEGATED_HOLD_RX_T.format(names=alt), text, flags=re.IGNORECASE)
    # ("stay put" / "stays put" are the WAIT family's own words — slice 7 —
    # and are not read here)
    if not m or not re.search(r"\b(?:move|march|advance|budge|stir|go|leave|shift)\b", text, flags=re.IGNORECASE):
        return text
    name = next(n for n in friendly_names if str(n).lower() == m.group("name").lower())
    return f"{name}, hold"


# ── DD0-19 (S4 part 4, October 11, 2026): the sixth set's register.

_PLACE_RX = r"(?P<place>[A-Z][\w'’-]*(?:[\s-][A-Z][\w'’-]*)?)"


def rewrite_we_are_at_war(text: str) -> str:
    """"We are at war with Sweden from this day." → "declare war on Sweden"."""
    m = re.match(r"^\s*(?i:we\s+are\s+(?:now\s+|henceforth\s+)?at\s+war\s+with\s+(?:the\s+)?)(?P<court>[A-Z][\w'’ -]{2,30}?)"
                 r"(?i:\s+(?:from\s+this\s+day|as\s+of\s+today|henceforth|from\s+today))?\s*[.!]*$", text or "")
    return f"declare war on {m.group('court').strip()}" if m else text


def rewrite_both_to(text: str, friendly_names: Iterable[str]) -> str:
    """"Berthier: Ney and Davout both to Frankfurt." — two men and a place
    with no verb: the march, said with its verb so the two-marshal road
    reads it ("Ney and Davout both march to Frankfurt")."""
    alt = _name_alt(friendly_names)
    if not text or not alt:
        return text
    m = re.match(r"^\s*(?i:berthier\s*[,:]\s*)?(?P<a>" + alt + r")\s+(?i:and)\s+(?P<b>" + alt + r")\s+(?i:both\s+)?"
                 r"(?i:to)\s+" + _PLACE_RX + r"\s*[.!]*$", text)
    if not m:
        return text
    a = next(n for n in friendly_names if str(n).lower() == m.group("a").lower())
    b = next(n for n in friendly_names if str(n).lower() == m.group("b").lower())
    return f"{a} and {b} both march to {m.group('place')}"


def rewrite_to_place_with_name(text: str, friendly_names: Iterable[str]) -> str:
    """"To Franconia with Ney's corps, Berthier, and no dawdling." — the
    destination first, the man after → "Ney, move to Franconia, …"."""
    alt = _name_alt(friendly_names)
    if not text or not alt:
        return text
    m = re.match(r"^\s*(?i:to)\s+" + _PLACE_RX + r"\s+(?i:with)\s+(?i:marshal\s+)?(?P<name>" + alt + r")"
                 r"(?:['’]s\s+(?:corps|men|horse|cavalry|division|army|troops))?(?P<rest>.*)$", text)
    if not m:
        return text
    name = next(n for n in friendly_names if str(n).lower() == m.group("name").lower())
    return f"{name}, move to {m.group('place')}{m.group('rest')}"


_COURTESY_HEAD_RX = re.compile(
    r"^\s*(?:berthier,?\s+)?(?:be\s+so\s+(?:good|kind)\s+as\s+to|would\s+you\s+(?:kindly\s+|please\s+)?|"
    r"have\s+the\s+goodness\s+to|see\s+to\s+it\s+that|see\s+that|dictate:?|i\s+want\s+you\s+to|"
    r"you\s+will|you\s+are\s+to)\s+(?P<rest>[a-z].+)$", re.IGNORECASE)


def rewrite_courtesy_head(text: str) -> str:
    """"Berthier, be so good as to direct Marshal Lannes to Frankfurt." —
    the courtesy before the order is set aside; the order stands alone."""
    m = _COURTESY_HEAD_RX.match(text or "")
    if not m or _ORDER_VERB_RE.match(m.group("rest").split()[0]) is None and not re.match(
            r"^(?:direct|dispatch|send|order|have|get|bring|take|move|march)\b", m.group("rest"), re.IGNORECASE):
        return text
    return m.group("rest")


def rewrite_emperor_desires(text: str, friendly_names: Iterable[str]) -> str:
    """"Ney, the Emperor desires you at Munich." → "Ney, move to Munich"."""
    alt = _name_alt(friendly_names)
    if not text or not alt:
        return text
    m = re.match(r"^\s*(?i:marshal\s+)?(?P<name>" + alt + r")\s*[,:]\s*(?i:the\s+emperor|i|we|france)\s+"
                 r"(?i:desires?|wants?|wishes|wish|needs?|would\s+have|requires?|must\s+have)\s+(?i:you|him|your\s+corps)\s+"
                 r"(?i:at|in)\s+" + _PLACE_RX + r"\s*[.!]*$", text)
    if not m:
        return text
    name = next(n for n in friendly_names if str(n).lower() == m.group("name").lower())
    return f"{name}, move to {m.group('place')}"


def rewrite_halts_at(text: str, friendly_names: Iterable[str]) -> str:
    """"Murat halts at Franche-Comte." — a halt AT a place is the hold, not
    the stand-down of a standing order ("halt" alone is the cancel)."""
    alt = _name_alt(friendly_names)
    if not text or not alt:
        return text
    m = re.match(r"^\s*(?i:marshal\s+)?(?P<name>" + alt + r")\s*[,:]?\s+(?i:halts?|stops?|pulls?\s+up)\s+"
                 r"(?i:at|in)\s+" + _PLACE_RX + r"\s*[.!]*$", text)
    if not m:
        return text
    name = next(n for n in friendly_names if str(n).lower() == m.group("name").lower())
    return f"{name}, hold"


_NOT_A_LAW_RX = re.compile(r"\b(?:pension|rente|alliance|treaty|pact|peace|autonomy|order|orders|command|mission|"
                           r"truce|armistice|bargain|tribute|guarantee|sponsorship|standing|charter|licence|license|"
                           r"blockade|posture|march|attack)\b", re.IGNORECASE)


def rewrite_repeal(text: str) -> str:
    """"revoke the artillery reserve" / "abolish the Staff" → "repeal <law>"
    (never a pension, a treaty or an order — those have their own desks)."""
    # (`withdraw` is NOT here — "withdraw south" is the free retreat, FA slice 14's pin)
    m = re.match(r"^\s*(?:revoke|rescind|abolish|annul|strike\s+down|do\s+away\s+with)\s+(?:the\s+)?"
                 r"(?P<name>[A-Za-z][\w'’ -]{2,40}?)(?:\s+law)?\s*[.!]*$", text or "", flags=re.IGNORECASE)
    if not m or _NOT_A_LAW_RX.search(m.group("name")):
        return text
    return f"repeal {m.group('name').strip()}"


def rewrite_attack_idioms_p4(text: str, enemy_names: Iterable[str]) -> str:
    """The sixth set's attack register: "go at Mack directly", "throw your
    corps at Swabia"."""
    if not text:
        return text
    alt = _foe_alt(enemy_names)
    out = text
    if alt:
        out = re.sub(r"\bgo\s+(?:straight\s+|directly\s+|right\s+)?at\s+(?=(?:" + alt + r")\b)", "attack ", out,
                     count=1, flags=re.IGNORECASE)
    out = re.sub(r"\bthrow\s+(?:your|the|his|our|every)\s+(?:whole\s+)?(?:corps|men|army|troops|division|weight|"
                 r"everything|regiments?|battalions?)\s+(?:at|against|on|upon|into)\s+", "attack ", out,
                 count=1, flags=re.IGNORECASE)
    return out


# ══════════════════════════════════════════════════════════════════════
# DD0-20 (Pre-Deploy S5, October 11, 2026): the seventh blind set's register
# — the 26 shrugs, the two wrong desks and the parser's share of the honest
# refusals (BUG_FIXES.md DD0-20; rules SYSTEMS_REFERENCE.md §105).
# ══════════════════════════════════════════════════════════════════════

def _canon(typed: str, names: Iterable[str]) -> str:
    """The roster's spelling of a name typed in any case."""
    low = (typed or "").strip().lower()
    for n in names:
        if str(n).lower() == low:
            return str(n)
    return typed


_ARROW_RX = re.compile(r"\s*(?:->|=>|-->|→|⇒|>>)\s*")


def rewrite_arrow(text: str) -> str:
    """"soult->swabia" — the arrow is the march's `to`."""
    if not text or not _ARROW_RX.search(text):
        return text
    return _ARROW_RX.sub(" to ", text).strip()


_NO_HURRY_RX = re.compile(
    r"[\s,;—–-]+(?:no\s+(?:hurry|rush)|there\s+is\s+no\s+hurry|take\s+your\s+time|at\s+(?:your\s+)?leisure|"
    r"in\s+your\s+own\s+time)\s*[.!]*$", re.IGNORECASE)
# The hour and the calendar: "tomorrow at dawn", "by the end of the week".
# A bare "tomorrow" / "next turn" is NOT here — that is FA-7's deferral,
# which the engine refuses on purpose.
_TIME_TAIL_RX = re.compile(
    r"[\s,;]+(?:(?:tomorrow|today|tonight)\s+)?(?:at\s+)?(?:dawn|first\s+light|daybreak|dusk|nightfall|noon|midday|"
    r"sunset|sunrise|midnight|cockcrow)\b"
    r"|[\s,;]+(?:today|this\s+(?:morning|afternoon|evening|week)|in\s+the\s+morning|"
    r"by\s+(?:the\s+end\s+of\s+)?(?:the\s+)?(?:week|day|month|turn|nightfall|dawn|evening|morning)|"
    r"before\s+(?:the\s+)?(?:week|day|month|turn)\s+is\s+out|within\s+the\s+(?:week|day|month|turn))\b",
    re.IGNORECASE)
_WEATHER_TAIL_RX = re.compile(
    r"[\s,;]+(?:no\s+matter\s+(?:the\s+)?\w+|whatever\s+the\s+\w+|come\s+what\s+may|rain\s+or\s+shine|"
    r"no\s+excuses)\s*[.!]*$", re.IGNORECASE)
_RATIONS_TAIL_RX = re.compile(
    r"[\s,;]+(?:and\s+)?(?:carry|carrying|take|taking|bring|bringing|with)\s+(?:\d+|two|three|four|five|six|seven|ten)\s+"
    r"days['’]?\s+(?:of\s+)?(?:rations|provisions|supplies|food|bread|biscuit)\b.*$", re.IGNORECASE)
_SAVE_CORPS_TAIL_RX = re.compile(
    r"[\s,;]+(?:and\s+)?(?:save|preserve|spare)\s+(?:the|his|your|our|its)\s+(?:corps|men|army|troops|division|guns)\s*[.!]*$",
    re.IGNORECASE)


def strip_colour_tails(text: str) -> str:
    """"Walk Ney across to Nassau, NO HURRY." / "I want Soult in
    Franche-Comte BY THE END OF THE WEEK." / "… attack Swabia TOMORROW AT
    DAWN, NO MATTER THE WEATHER." / "…, CARRY 3 DAYS RATIONS." / "… retire
    AND SAVE THE CORPS." — the colour behind an order, cut from the end
    (never the whole line)."""
    if not text:
        return text
    out = text
    for _ in range(4):
        nxt = out
        for rx in (_NO_HURRY_RX, _WEATHER_TAIL_RX, _RATIONS_TAIL_RX, _SAVE_CORPS_TAIL_RX):
            m = rx.search(nxt)
            if m and nxt[:m.start()].strip():
                nxt = nxt[:m.start()].rstrip(" ,;")
        m = _TIME_TAIL_RX.search(nxt)
        if m and nxt[:m.start()].strip() and not nxt[m.end():].strip(" .!,;"):
            nxt = nxt[:m.start()].rstrip(" ,;")
        if nxt == out:
            break
        out = nxt
    return out if out.strip() else text


def strip_head_word_before_dash(text: str, friendly_names: Iterable[str], enemy_names: Iterable[str]) -> str:
    """"SORTEZ — Soult out of Lorraine and into Franche-Comte." — one word
    before a dash and a man of ours is the cry, not the order."""
    alt = _name_alt(friendly_names)
    if not text or not alt:
        return text
    m = re.match(r"^\s*(?P<head>[A-Za-zÀ-ÿ]{3,})\s*[—–:-]+\s+(?=(?:marshal\s+)?(?:" + alt + r")\b)(?P<rest>.+)$",
                 text, flags=re.IGNORECASE)
    if not m:
        return text
    head = m.group("head").lower()
    if (_ORDER_VERB_RE.match(head) or head in _known_tokens(list(friendly_names) + list(enemy_names))
            or head in ("not", "never", "wait", "halt", "stop", "hold", "don't", "dont")):
        return text
    return m.group("rest")


def strip_aim_before_addressed_order(text: str, friendly_names: Iterable[str], enemy_names: Iterable[str]) -> str:
    """"Hit John before he can join Mack — Massena, attack Tyrol." — the
    aim before the dash names a foe and no man of ours; the addressed order
    after the dash is the order (the aim rode the relay as 'Mack — Massena'
    before)."""
    alt = _name_alt(friendly_names)
    if not text or not alt:
        return text
    m = re.match(r"^\s*(?P<aim>[^—–]+?)\s+[—–]+\s+(?P<order>(?:marshal\s+)?(?:" + alt + r")\s*[,:]\s*[A-Za-z].+)$",
                 text, flags=re.IGNORECASE)
    if not m:
        return text
    aim = m.group("aim")
    if set(re.findall(r"[a-z][a-z'’-]+", aim.lower())) & _known_tokens(friendly_names):
        return text
    from backend.ai.reading import foe_named_in
    if not foe_named_in(aim, enemy_names):
        return text
    return m.group("order")


def rewrite_where_foe_is_there_goes(text: str, friendly_names: Iterable[str], enemy_names: Iterable[str],
                                    place_names: Iterable[str]) -> str:
    """"Where Mack is, there Ney goes: Swabia." — the march to the named
    ground (the foe is the reason)."""
    foes, friends, places = _foe_alt(enemy_names), _name_alt(friendly_names), _name_alt(place_names)
    if not (text and foes and friends and places):
        return text
    m = re.match(r"^\s*where\s+(?:the\s+)?(?:" + foes + r")\s+(?:is|stands|sits|lies|waits),?\s+there\s+"
                 r"(?P<name>" + friends + r")\s+(?:goes|marches|rides|shall\s+go|will\s+go|must\s+go)\s*[:,—–-]?\s*"
                 r"(?:to\s+)?(?P<place>" + places + r")\s*[.!]*$", text, flags=re.IGNORECASE)
    if not m:
        return text
    return f"{_canon(m.group('name'), friendly_names)}, move to {_canon(m.group('place'), place_names)}"


def rewrite_is_ordered_to(text: str, friendly_names: Iterable[str], place_names: Iterable[str]) -> str:
    """"Lannes is ordered to Lorraine" / "Davout is directed on Frankfurt" —
    the passive formal march, to a place of the map (never to a verb)."""
    friends, places = _name_alt(friendly_names), _name_alt(place_names)
    if not (text and friends and places):
        return text
    m = re.match(r"^\s*(?:marshal\s+)?(?P<name>" + friends + r")\s+(?:is|are)\s+(?:hereby\s+)?"
                 r"(?:ordered|directed|instructed|commanded|detailed|assigned|posted)\s+"
                 r"(?:to\s+(?:go|march|move|proceed|ride)\s+)?(?:to|into|toward|towards|on|for|at)\s+(?:the\s+)?"
                 r"(?P<place>" + places + r")\b(?P<tail>.*)$", text, flags=re.IGNORECASE)
    if not m:
        return text
    return f"{_canon(m.group('name'), friendly_names)}, move to {_canon(m.group('place'), place_names)}{m.group('tail')}"


def rewrite_everybody_on(text: str, friendly_names: Iterable[str], enemy_names: Iterable[str]) -> str:
    """"Everybody on Mack. Soult leads." — the muster against the foe, led
    by the man named; without a leader, the bare attack (the muster's own
    ask)."""
    foes, friends = _foe_alt(enemy_names), _name_alt(friendly_names)
    if not (text and foes):
        return text
    lead = (r"\s*(?:(?P<lead>" + friends + r")\s+(?:leads|to\s+lead|in\s+the\s+lead|leading|first|has\s+the\s+lead|"
            r"takes\s+the\s+lead|will\s+lead)\s*[.!]*)?" if friends else "")
    m = re.match(r"^\s*(?:everybody|everyone|every\s+corps|all\s+corps|every\s+man|all\s+of\s+you|the\s+whole\s+army|all)\s+"
                 r"(?:on|at|against|upon|onto)\s+(?:the\s+)?(?P<foe>" + foes + r")\s*[.!;,]*" + lead + r"$",
                 text, flags=re.IGNORECASE)
    if not m:
        return text
    foe = _printed_foe(m.group("foe"), enemy_names)
    leader = m.groupdict().get("lead")
    return f"{_canon(leader, friendly_names)}, attack {foe}" if leader else f"attack {foe}"


def rewrite_will_join_tail(text: str, friendly_names: Iterable[str]) -> str:
    """"Soult goes in against Swabia; Davout and Ney will join." — the men
    who follow: one is the second in support (the relay's own road); two or
    more are the colour behind the one order."""
    alt = _name_alt(friendly_names)
    if not text or not alt:
        return text
    m = re.search(r"[\s,;]+(?:with\s+)?(?P<men>(?:marshal\s+)?(?:" + alt + r")(?:\s*(?:,|and|&)\s*(?:marshal\s+)?(?:" + alt + r"))*)\s+"
                  r"(?:will|shall|to|are\s+to)\s+(?:join|follow|come\s+up|support|back\s+(?:him|them)\s+up)"
                  r"(?:\s+(?:him|them|in|up|later|after))?\s*[.!]*$", text, flags=re.IGNORECASE)
    if not m or not text[:m.start()].strip():
        return text
    men = re.findall(alt, m.group("men"), flags=re.IGNORECASE)
    head = text[:m.start()].rstrip(" ,;")
    lead = re.match(r"^\s*(?:marshal\s+)?(?P<name>" + alt + r")[,:]?\s+(?P<order>.+)$", head, flags=re.IGNORECASE)
    if len(men) == 1 and lead and lead.group("name").lower() != men[0].lower():
        # the relay's own shape (`rewrite_second_in_support`'s output)
        first, second = _canon(lead.group("name"), friendly_names), _canon(men[0], friendly_names)
        return f"{first}, {lead.group('order')}, then {second}, support {first}"
    return head


def rewrite_cabinet_delegation(text: str) -> str:
    """"Have the Cabinet propose a treaty of alliance to Denmark." / "Tell
    Talleyrand to …" → "Talleyrand, …"; "a treaty of alliance" is the
    alliance."""
    if not text:
        return text
    # (the office, not the man: "Have Talleyrand back Prussia's quarrel" is
    # the sponsorship idiom's own line — `rewrite_plain_attack_forms` reads
    # it with its aim — and is left whole)
    out = re.sub(r"^\s*(?:have|tell|instruct|order|direct|ask|let)\s+(?:the\s+)?"
                 r"(?:cabinet|foreign\s+office|foreign\s+minister|our\s+envoy|the\s+minister|the\s+chancery)\s+(?:to\s+)?",
                 "Talleyrand, ", text, count=1, flags=re.IGNORECASE)
    out = re.sub(r"\b(?:a\s+|the\s+)?treaty\s+of\s+(?P<kind>alliance|peace|friendship|commerce|neutrality|non-aggression)\b",
                 r"\g<kind>", out, count=1, flags=re.IGNORECASE)
    return out


def rewrite_talk_to(text: str) -> str:
    """"Talk to Spain about their fleet joining ours." — the Cabinet's
    conversation with a court is the negotiation (DD0-17's "open talks")."""
    m = re.match(r"^\s*(?:talleyrand,?\s+)?(?:talk|speak|confer|parley)\s+(?:to|with)\s+(?:the\s+)?"
                 r"(?P<court>[A-Z][\w'’-]*(?:\s+(?:of\s+)?[A-Z][\w'’-]*)?)\s+(?:about|regarding|on|concerning|over)\b.*$",
                 text or "", flags=re.IGNORECASE)
    return f"Talleyrand, negotiate with {m.group('court')}" if m else text


def rewrite_sound_out(text: str) -> str:
    """"Talleyrand will sound out Denmark on closing the Sound to the
    British." / "see what Portugal wants to leave the British orbit" — an
    inquiry into a court's mind is the Cabinet's assessment of that court
    (the advisory), never a letter with no terms (the bare card)."""
    m = re.match(r"^\s*(?:talleyrand,?\s+|talleyrand\s+(?:will|shall|should|is\s+to|must)\s+)?"
                 r"(?:sound\s+out|feel\s+out|see\s+what|find\s+out\s+what|learn\s+what|discover\s+what|ask\s+what|"
                 r"see\s+(?:where|how)|find\s+out\s+(?:where|how)|take\s+the\s+(?:measure|temperature)\s+of)\s+(?:the\s+)?"
                 r"(?P<court>[A-Z][\w'’-]*(?:\s+(?:of\s+)?[A-Z][\w'’-]*)?)\b.*$", text or "", flags=re.IGNORECASE)
    if not m or _ORDER_VERB_RE.match(m.group("court").split()[0]):
        return text
    return f"Talleyrand, what about {m.group('court')}?"


def rewrite_mission_purpose_aside(text: str) -> str:
    """"A mission to Saxony — keep the Elector out of this war." — the aim
    behind the dash is the mission's purpose, not a word of state."""
    m = re.match(r"^\s*(?P<head>(?:talleyrand,?\s+)?(?:send\s+)?(?:a\s+|an\s+)?(?:mission|envoy|emissary|embassy)\s+to\s+"
                 r"[A-Z][\w'’-]*(?:\s+[A-Z][\w'’-]*)?)\s*[—–:,-]+\s*(?:to\s+)?"
                 r"(?:keep|win|bring|draw|pry|detach|secure|hold|sound|see|find|make|get|coax|persuade|convince|talk)\b.*$",
                 text or "", flags=re.IGNORECASE)
    return m.group("head") if m else text


def strip_foe_premise_so(text: str, enemy_names: Iterable[str]) -> str:
    """"Mack is at Swabia, so I want Davout at Frankfurt …" — a statement
    of where the foe stands, joined by `so` to the order it explains, is
    the reason; the order after the `so` is the order."""
    foes = _foe_alt(enemy_names)
    if not text or not foes:
        return text
    m = re.match(r"^\s*(?:the\s+)?(?:" + foes + r")\s+(?:is|sits|stands|lies|waits|holds|camps|remains)\s+"
                 r"(?:at|in|near|before|on|around|outside)\s+[A-Za-z][\w'’-]*(?:\s+[A-Z][\w'’-]*)?\s*[,;]?\s+"
                 r"(?:so|therefore|hence|thus|which\s+is\s+why)\s+(?P<rest>.+)$", text, flags=re.IGNORECASE)
    return m.group("rest") if m else text


def rewrite_is_to_retire(text: str, friendly_names: Iterable[str]) -> str:
    """"Davout is to retire and save the corps." — the retreat (a `retire`
    with no ground named; `retire on <place>` is the march above)."""
    alt = _name_alt(friendly_names)
    if not text or not alt:
        return text
    m = re.match(r"^\s*(?:marshal\s+)?(?P<name>" + alt + r")\s+(?:is|are)\s+to\s+(?:retire|fall\s+back|withdraw|pull\s+back)"
                 r"(?P<rest>.*)$", text, flags=re.IGNORECASE)
    if not m or re.search(r"\b(?:on|to|upon|toward|towards|into)\s+\w", m.group("rest")):
        return text
    return f"{_canon(m.group('name'), friendly_names)}, retreat{m.group('rest')}"


_LEVY_TYPE = r"(?P<type>infantry|cavalry|artillery|horse|foot|guns|dragoons|hussars|grenadiers)"


def rewrite_levy(text: str, place_names: Iterable[str]) -> str:
    """"The Emperor commands a levy in Guyenne." / "Call up men in
    Flanders." / "I want a levy in Languedoc, infantry." / "More men at
    Lyonnais" → "recruit [type] in <place>". A levy named WITH its ground
    and a preposition; the bare `levy <place>` stays CX-R1's (unrouted)."""
    places = _name_alt(place_names)
    if not (text and places):
        return text
    head = (r"^\s*(?:berthier,?\s+)?(?:(?:the\s+emperor|i|we|the\s+army)\s+(?:commands?|orders?|wants?|needs?|desires?|requires?|"
            r"would\s+like)\s+|order\s+|let\s+there\s+be\s+|raise\s+|muster\s+|conscript\s+|call\s+(?:up|out)\s+|levy\s+)?")
    noun = (r"(?:a\s+|an\s+|some\s+|more\s+|new\s+|fresh\s+|the\s+)?(?:" + _LEVY_TYPE + r"\s+)?"
            r"(?:levy|levies|draft|conscription|call-?up|recruits|men|troops|soldiers|conscripts|battalions|regiments)\b")
    m = re.match(head + noun + r"(?:\s+of\s+" + _LEVY_TYPE.replace("type", "type2") + r")?\s+(?:in|at|from)\s+(?:the\s+)?"
                 r"(?P<place>" + places + r")\b(?:\s*[,;—–:-]+\s*" + _LEVY_TYPE.replace("type", "type3") + r"\b)?.*$",
                 text, flags=re.IGNORECASE)
    if not m:
        return text
    kind = (m.group("type") or m.group("type2") or m.group("type3") or "").lower()
    kind = {"horse": "cavalry", "foot": "infantry", "guns": "artillery", "dragoons": "cavalry",
            "hussars": "cavalry", "grenadiers": "infantry"}.get(kind, kind)
    place = _canon(m.group("place"), place_names)
    return f"recruit {kind} in {place}" if kind else f"recruit in {place}"


def rewrite_mend_walls(text: str) -> str:
    """"mend the walls at rhineland" — the repair, in the mason's words."""
    m = re.match(r"^\s*(?:berthier,?\s+)?(?:mend|patch(?:\s+up)?|rebuild|fix|shore\s+up|make\s+good|see\s+to)\s+(?:the\s+)?"
                 r"(?:walls?|forts?|fortress|fortifications?|works|defences|defenses|ramparts|damage|earthworks|breach)\s+"
                 r"(?:at|in|of|around)\s+(?:the\s+)?(?P<place>[A-Za-z][\w'’ -]+?)\s*[.!]*$", text or "", flags=re.IGNORECASE)
    return f"repair the walls at {m.group('place')}" if m else text


def apply_all(text: str, friendly_names: Iterable[str], enemy_names: Iterable[str],
              place_names: Iterable[str], sovereign: Optional[str] = None) -> List[Tuple[str, str, str]]:
    """Every rewrite in order; returns [(rule, before, after)] for the ones
    that fired, the caller reads the final text off the last row."""
    known = list(friendly_names) + list(enemy_names) + list(place_names)
    steps = (
        ("strip_please_and_urgency", lambda t: strip_please_and_urgency(t)),
        # DD0-20 (S5): the arrow, the colour tails, the cry before the dash,
        # the aim before an addressed order, the Cabinet's delegation
        ("rewrite_arrow", lambda t: rewrite_arrow(t)),
        ("strip_colour_tails", lambda t: strip_colour_tails(t)),
        ("rewrite_will_join_tail", lambda t: rewrite_will_join_tail(t, friendly_names)),
        ("strip_head_word_before_dash", lambda t: strip_head_word_before_dash(t, friendly_names, enemy_names)),
        ("strip_aim_before_addressed_order", lambda t: strip_aim_before_addressed_order(t, friendly_names, enemy_names)),
        ("rewrite_cabinet_delegation", lambda t: rewrite_cabinet_delegation(t)),
        ("rewrite_mission_purpose_aside", lambda t: rewrite_mission_purpose_aside(t)),
        ("rewrite_sound_out", lambda t: rewrite_sound_out(t)),
        ("strip_foe_premise_so", lambda t: strip_foe_premise_so(t, enemy_names)),
        # DD0-19: the courtesy before the order is set aside FIRST, so the
        # sent-marshal and the other head readers see the order's own head
        ("rewrite_courtesy_head", lambda t: rewrite_courtesy_head(t)),
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
        ("rewrite_open_talks", lambda t: rewrite_open_talks(t)),
        ("rewrite_naval_landing", lambda t: rewrite_naval_landing(t)),
        ("rewrite_trailing_end_turn", lambda t: rewrite_trailing_end_turn(t)),
        # S4 part 4 (DD0-18): the fifth set's register
        ("rewrite_negated_hold", lambda t: rewrite_negated_hold(t, friendly_names)),
        ("rewrite_retire_on", lambda t: rewrite_retire_on(t)),
        ("rewrite_pull_back", lambda t: rewrite_pull_back(t, friendly_names)),
        ("rewrite_break_off_rejoin", lambda t: rewrite_break_off_rejoin(t, friendly_names)),
        ("rewrite_on_to_the_enemy", lambda t: rewrite_on_to_the_enemy(t, friendly_names)),
        ("rewrite_hand_over", lambda t: rewrite_hand_over(t)),
        # DD0-19: the sixth set's register
        ("rewrite_we_are_at_war", lambda t: rewrite_we_are_at_war(t)),
        ("rewrite_to_place_with_name", lambda t: rewrite_to_place_with_name(t, friendly_names)),
        ("rewrite_both_to", lambda t: rewrite_both_to(t, friendly_names)),
        ("rewrite_emperor_desires", lambda t: rewrite_emperor_desires(t, friendly_names)),
        ("rewrite_halts_at", lambda t: rewrite_halts_at(t, friendly_names)),
        ("rewrite_repeal", lambda t: rewrite_repeal(t)),
        ("rewrite_attack_idioms_p4", lambda t: rewrite_attack_idioms_p4(t, enemy_names)),
        # DD0-20 (S5): the seventh set's register
        ("rewrite_where_foe_is_there_goes", lambda t: rewrite_where_foe_is_there_goes(t, friendly_names, enemy_names, place_names)),
        ("rewrite_is_ordered_to", lambda t: rewrite_is_ordered_to(t, friendly_names, place_names)),
        ("rewrite_everybody_on", lambda t: rewrite_everybody_on(t, friendly_names, enemy_names)),
        ("rewrite_talk_to", lambda t: rewrite_talk_to(t)),
        ("rewrite_is_to_retire", lambda t: rewrite_is_to_retire(t, friendly_names)),
        ("rewrite_levy", lambda t: rewrite_levy(t, place_names)),
        ("rewrite_mend_walls", lambda t: rewrite_mend_walls(t)),
    )
    rows: List[Tuple[str, str, str]] = []
    cur = text
    for rule, fn in steps:
        nxt = fn(cur)
        if nxt != cur:
            rows.append((rule, cur, nxt))
            cur = nxt
    return rows
