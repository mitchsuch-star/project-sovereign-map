"""CR-7-4 — THE ONE VOCABULARY FOR STANDING-ORDER CONDITIONS.

WHY THIS MODULE EXISTS
======================
`StrategicCondition` (marshal.py) is a live, serialized, per-turn-evaluated
substrate — nothing here is dead code. What was broken is what a player could
SAY. `strategic_parser._strip_conditions` decided what was REMOVED from the
target text and `strategic_parser._parse_condition` decided what was READ, and
the two held different vocabularies: `until` but not `till`, digits but not
word-numbers, no honorific. Measured on the shipped 1805 boot, September 22
2026 (`docs/audits/COMPOUND_CONDITIONAL_COMMANDS_2026_09_20.md` §1):

    hold Lorraine till Ney arrives      -> HOLD on "Lorraine Till Ney Arrives"
    hold Lorraine for three turns       -> HOLD on "Lorraine For Three Turns"
    hold Lorraine until relief arrives  -> until_marshal_arrives = "Relief"
    hold Lorraine until Godot arrives   -> accepted; Godot is not on the board
    hold Lorraine for 0 turns           -> max_turns = 0, a paid no-op
    hold Lorraine until turn 5          -> silently unconditional
    hold Lorraine until Marshal Ney arrives -> silently unconditional

4 of 15 phrasings produced the condition asked for; every one was charged
2 AP. A prior experiment widened `_parse_condition` ALONE and the phantom
province stood on 5 of 6 — because the strip and the read must move together.
So they are ONE list here, and every reader — the strip, the read, the
confirmation echo, the Strategic Ledger — derives from it.

THE RULES (SYSTEMS_REFERENCE.md §4 Stage 2b)
--------------------------------------------
1. A clause the engine READS is a clause the target text never sees.
2. A referent the engine cannot meet is REFUSED at 0 AP, never minted: an
   `until X arrives` names a friendly marshal on the board, or it is refused
   by name. "until relief arrives" is `until_relieved` (the words mean it).
3. `for N turns` is floored at 1; `for 0 turns` is refused. `until turn N`
   is READ as `for (N - now) turns` and the echo says so; a turn already
   behind us is refused.
4. Shown == applied: the confirmation names every accepted condition from the
   same sentence the Ledger renders (`describe_condition`), and a subordinate
   clause the engine could NOT read is named as unread ("the order stands
   without it") rather than dropped in silence.

`world is None` (the legacy unit-level calls in test_strategic_parser.py /
test_llm_strategic.py) keeps the pre-slice READ byte-for-byte: names are
capitalised, nothing is validated, and no notes are produced.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from backend.ai.attack_vocabulary import levered_arrival_pattern
from backend.ai.clause_guards import HONORIFIC, condition_marker_spans
from backend.display_names import plural as _plural  # LV-9 (row EP F2)

WORD_NUMBERS: Dict[str, int] = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}
_NUMBER = r"(?:\d+|" + "|".join(WORD_NUMBERS) + r")"
# Every way the game accepts "until". `till` and `'til` were the phantom-
# province forms; "until such time as" is the period's own phrasing.
UNTIL = r"(?:until\s+such\s+time\s+as|until|till|['’]til)"
# CR-7-9: a clause may also open with the CONNECTOR that joins it to the
# clause before it ("until Davout arrives OR the battle is won") — the
# second `until` is what a player says, not what a player types.
_LEAD = r"(?:" + UNTIL + r"|and|or)"
_NAME = r"[a-z][a-z'’-]*"

# ── The clauses the engine READS ──────────────────────────────────────────
# Every regex here is ALSO a strip: `strip_condition_text` removes exactly
# these spans (plus the generic until-tail below) from the target text.
ARRIVES_RE = re.compile(
    r"\b" + _LEAD + r"\s+(?:" + HONORIFIC + r")?(?!relief\b|reinforcements?\b|help\b)"
    r"(?P<name>" + _NAME + r")\s+arrives?\b")
RELIEVED_RE = re.compile(
    r"\b" + _LEAD + r"\s+(?:relieved|(?:the\s+)?(?:relief|reinforcements?|help)"
    r"\s+(?:arrives?|comes?|reaches\s+(?:him|us|them)))\b")
BATTLE_WON_RE = re.compile(
    r"\b" + _LEAD + r"\s+(?:(?:the\s+)?battle\s+(?:is\s+)?won|victory|victorious"
    r"|(?:the\s+)?battle\s+is\s+(?:decided|over))\b")
DESTROYED_RE = re.compile(
    r"\b(?:" + _LEAD + r"\s+(?:(?P<who>" + _NAME + r")\s+(?:is\s+|are\s+)?)?destroyed"
    r"|to\s+destruction)\b")
TURNS_RE = re.compile(r"\bfor\s+(?P<n>" + _NUMBER + r")\s+(?:more\s+)?turns?\b")
UNTIL_TURN_RE = re.compile(r"\b" + UNTIL + r"\s+turn\s+(?P<t>\d+)\b")
# The generic cut every unread `until …` clause still gets, so a clause the
# engine cannot read never rides into the target ("hold Lorraine until the
# cows come home" holds Lorraine, and the echo names the unread clause).
UNTIL_TAIL_RE = re.compile(r"\s+" + UNTIL + r"\s+.*$")
# The attack-on-arrival tail (CR-7-1's boundary set + CR-7-3's bare comma).
# CRT-11 / RS-8: the one battle/capture vocabulary (`attack_vocabulary`).
ARRIVAL_TAIL_RE = levered_arrival_pattern(
    r"\s*(?:,\s*|;\s*|\s+(?:and\s+then|and|then)\s+)(?:{verbs})\b.*$")

_READ_CLAUSES: Tuple[Tuple[str, "re.Pattern"], ...] = (
    ("until_marshal_arrives", ARRIVES_RE),
    ("until_relieved", RELIEVED_RE),
    ("until_battle_won", BATTLE_WON_RE),
    ("until_marshal_destroyed", DESTROYED_RE),
    ("max_turns", TURNS_RE),
    ("until_turn", UNTIL_TURN_RE),
)


def strip_condition_text(text: str) -> str:
    """Remove every condition clause the engine reads — and the generic
    `until …` tail — so none of it is read as a destination."""
    for _key, pattern in _READ_CLAUSES:
        text = pattern.sub("", text)
    text = UNTIL_TAIL_RE.sub("", text)
    text = ARRIVAL_TAIL_RE.sub("", text)
    # CR-7-9: "for 2 turns and until Davout arrives" leaves "… and" behind
    # once both clauses are cut — a connector is never a destination.
    text = re.sub(r"\s+(?:and|or)\s*$", "", text)
    return re.sub(r"\s{2,}", " ", text).strip()


@dataclass
class ConditionRead:
    """What one sentence asked for, and what the engine did about it."""
    condition: Optional[Dict] = None      # StrategicCondition-shaped, or None
    refusal: Optional[Dict] = None        # {"kind": …, …} — refuse at 0 AP
    notes: List[str] = field(default_factory=list)    # how a clause was READ
    unread: List[str] = field(default_factory=list)   # clauses the engine cannot hold


def _resolve_marshal(name: str, world):
    """The marshal a typed name denotes, or None. Reads the ONE name-form
    source (`llm_client.name_match_patterns`) so "Archduke Charles" and the
    scenario key resolve alike."""
    if not name or world is None:
        return None
    wanted = name.strip().lower()
    try:
        from backend.ai.llm_client import name_match_patterns
    except Exception:  # pragma: no cover — import guard for cold unit calls
        name_match_patterns = None
    for m in (getattr(world, "marshals", {}) or {}).values():
        forms = {m.name.lower()}
        if name_match_patterns is not None:
            try:
                forms.update(f.lower() for f in name_match_patterns(m.name))
            except Exception:
                pass
        if wanted in forms:
            return m
    return None


def _issuer_nation(world, issuing_marshal: Optional[str]) -> Optional[str]:
    if world is None:
        return None
    issuer = world.get_marshal(issuing_marshal) if issuing_marshal else None
    if issuer is not None:
        return getattr(issuer, "nation", None)
    return getattr(world, "player_nation", None)


def parse_condition(command_lower: str, target: str, *, world=None,
                    issuing_marshal: Optional[str] = None,
                    current_turn: Optional[int] = None) -> ConditionRead:
    """Read the condition clauses of one lower-cased order.

    ``world`` None = the legacy read (capitalised names, no validation).
    With a world: referents are validated against the board (rule 2), the
    turn forms are floored / mapped (rule 3), and `notes` / `unread` carry
    what the echo must say (rule 4).
    """
    read = ConditionRead()
    cond: Dict = {}
    nation = _issuer_nation(world, issuing_marshal)

    m = ARRIVES_RE.search(command_lower)
    if m:
        raw = m.group("name")
        if world is None:
            cond["until_marshal_arrives"] = raw.capitalize()
        else:
            who = _resolve_marshal(raw, world)
            if who is None:
                read.refusal = {"kind": "unknown_referent", "name": raw.capitalize()}
                return read
            if issuing_marshal and who.name == issuing_marshal:
                read.refusal = {"kind": "self_referent", "name": who.name}
                return read
            if nation is not None and getattr(who, "nation", None) != nation:
                read.refusal = {"kind": "enemy_referent", "name": who.name}
                return read
            if getattr(who, "captured_by", "") or getattr(who, "strength", 1) <= 0:
                read.refusal = {"kind": "fallen_referent", "name": who.name}
                return read
            cond["until_marshal_arrives"] = who.name
            if re.search(HONORIFIC, m.group(0), re.IGNORECASE) or raw.lower() != who.name.lower():
                read.notes.append(f"'{m.group(0).strip()}' read as until {who.name} arrives")

    if RELIEVED_RE.search(command_lower):
        cond["until_relieved"] = True
        rm = RELIEVED_RE.search(command_lower)
        if world is not None and "relieved" not in rm.group(0):
            read.notes.append(f"'{rm.group(0).strip()}' read as until relieved")

    dm = DESTROYED_RE.search(command_lower)
    if dm:
        who_raw = dm.groupdict().get("who")
        if who_raw and world is not None:
            who = _resolve_marshal(who_raw, world)
            cond["until_marshal_destroyed"] = who.name if who is not None else target
        else:
            cond["until_marshal_destroyed"] = target

    tm = TURNS_RE.search(command_lower)
    if tm:
        raw_n = tm.group("n")
        n = int(raw_n) if raw_n.isdigit() else WORD_NUMBERS[raw_n]
        if world is not None and n < 1:
            read.refusal = {"kind": "zero_turns"}
            return read
        cond["max_turns"] = n
        if world is not None and not raw_n.isdigit():
            read.notes.append(f"'for {raw_n} turns' read as for {n} turns")

    um = UNTIL_TURN_RE.search(command_lower)
    if um and world is not None:
        wanted = int(um.group("t"))
        now = int(current_turn if current_turn is not None
                  else getattr(world, "current_turn", 0) or 0)
        if wanted <= now:
            read.refusal = {"kind": "turn_passed", "turn": wanted, "current": now}
            return read
        cond["max_turns"] = wanted - now
        read.notes.append(f"'until turn {wanted}' read as for {_plural(wanted - now, 'turn')} from now")

    if BATTLE_WON_RE.search(command_lower):
        cond["until_battle_won"] = True

    # CR-7-9: the connector decides how several arms combine. `and` = every
    # arm must be met (all-of, latched on the order); `or`, a comma, or no
    # word at all = whichever comes first — the engine's own reading since
    # conditions existed, now SAID in the echo and on the Ledger.
    if len(cond) >= 2:
        joined, seen = read_connector(command_lower)
        if joined == "and":
            cond["require_all"] = True
        elif joined == "mixed" and world is not None:
            read.notes.append("'and' and 'or' both used — read as whichever comes first")
    if world is not None and cond.get("until_marshal_arrives") and issuing_marshal:
        me = world.get_marshal(issuing_marshal)
        who = world.get_marshal(cond["until_marshal_arrives"])
        if (me is not None and who is not None
                and getattr(me, "location", None) == getattr(who, "location", None)):
            read.notes.append(f"{who.name} is already at {who.location} with him — that arm is met at the turn's end")

    read.condition = cond if cond else None
    if world is not None:
        read.unread = unread_condition_clauses(command_lower)
    return read


_CONNECTOR_LEAD_RE = re.compile(r"(and|or)\b")
_CONNECTOR_GAP_RE = re.compile(r"\b(and|or)\b")


def read_connector(command_lower: str) -> Tuple[Optional[str], List[str]]:
    """The word joining the condition clauses: ``"and"`` (all-of), ``"or"``
    (any-of), ``"mixed"`` (both typed — read as any-of, and said), or
    ``None`` (nothing typed — any-of). A clause that opens with the
    connector (`or the battle is won`) carries it; otherwise the gap
    between two clauses is read (`for 2 turns, and until …`)."""
    spans = []
    for _key, pattern in _READ_CLAUSES:
        for m in pattern.finditer(command_lower):
            spans.append((m.start(), m.end(), m.group(0)))
    spans = sorted(set(spans))
    seen: List[str] = []
    for i in range(1, len(spans)):
        prev_end = spans[i - 1][1]
        start, _end, text = spans[i]
        if start < prev_end:
            continue
        lead = _CONNECTOR_LEAD_RE.match(text)
        if lead:
            seen.append(lead.group(1))
            continue
        gap = _CONNECTOR_GAP_RE.search(command_lower[prev_end:start])
        if gap:
            seen.append(gap.group(1))
    if not seen:
        return None, seen
    if "and" in seen and "or" in seen:
        return "mixed", seen
    return seen[0], seen


_CLAUSE_END_RE = re.compile(r"[,;.!?]|\s+then\s+|\s+but\s+", re.IGNORECASE)
_SENTENCE_END_RE = re.compile(r"[.!?]")


def unread_condition_clauses(command_lower: str) -> List[str]:
    """Subordinate clauses in the sentence that produced NO condition.

    `while Ney marches`, `unless attacked`, `if pressed` are blanked by the
    guards and were dropped in silence; the echo names them so shown ==
    applied. An `until …` clause the engine READ is not unread.
    """
    out: List[str] = []
    for start, end in condition_marker_spans(command_lower):
        marker = re.sub(r"\s+", " ", command_lower[start:end].lower())
        if marker in ("until", "till", "'til", "’til"):
            end_match = _SENTENCE_END_RE.search(command_lower, end)
        else:
            end_match = _CLAUSE_END_RE.search(command_lower, end)
        clause_end = end_match.start() if end_match else len(command_lower)
        clause = command_lower[start:clause_end].strip()
        if not clause or len(clause.split()) < 2:
            continue
        if marker in ("until", "till", "'til", "’til") and any(
                p.search(clause) for _k, p in _READ_CLAUSES):
            continue
        out.append(clause)
    return out


def describe_condition(cond, *, remaining: Optional[int] = None,
                       progress=None, only_unmet: bool = False) -> str:
    """The ONE sentence for a condition — the confirmation echo AND the
    Strategic Ledger read it, so shown == applied by construction.

    ``cond`` is a StrategicCondition or its dict. ``remaining`` (the ledger)
    renders a timed hold as turns left; the confirmation renders the term.
    CR-7-9: several arms are joined by the word that combines them —
    ``or … — whichever comes first`` (any-of, the default) or ``and … — both``
    (all-of), and ``progress`` (the arms already met on an all-of order)
    ticks them off; ``only_unmet`` names what is still waited for.
    """
    if cond is None:
        return ""
    get = (cond.get if isinstance(cond, dict)
           else lambda k, d=None: getattr(cond, k, d))
    met = set(progress or [])
    entries: List[Tuple[str, str]] = []
    if get("max_turns") is not None:
        n = int(get("max_turns"))
        if "max_turns" in met:
            entries.append(("max_turns", f"{_plural(n, 'turn')} passed"))
        elif remaining is not None:
            entries.append(("max_turns", f"{_plural(int(remaining), 'turn')} remaining"))
        else:
            entries.append(("max_turns", f"for {_plural(n, 'turn')}"))
    if get("until_marshal_arrives"):
        entries.append(("until_marshal_arrives", f"until {get('until_marshal_arrives')} arrives"))
    if get("until_relieved"):
        entries.append(("until_relieved", "until relieved"))
    if get("until_battle_won"):
        entries.append(("until_battle_won", "until the battle is won"))
    if get("until_marshal_destroyed"):
        entries.append(("until_marshal_destroyed", f"until {get('until_marshal_destroyed')} is destroyed"))
    if only_unmet:
        entries = [(k, t) for k, t in entries if k not in met]
    if not entries:
        return ""
    if len(entries) == 1:
        return entries[0][1]
    if bool(get("require_all")):
        texts = [t + (" (met)" if k in met and not only_unmet else "")
                 for k, t in entries]
        if only_unmet:
            return " and ".join(texts)
        tail = " — both" if len(texts) == 2 else f" — all {len(texts)}"
        return " and ".join(texts) + tail
    return " or ".join(t for _k, t in entries) + " — whichever comes first"


def refusal_copy(detail: Dict, marshal_name: Optional[str], world=None,
                 target: Optional[str] = None) -> str:
    """Berthier's line for a condition the engine must refuse — by CAUSE.
    Every arm names the supported form, and none blames the enemy for a
    sentence about a friendly arrival (the CR-7-4 §1 finding)."""
    kind = (detail or {}).get("kind")
    who = marshal_name or "the marshal"
    name = (detail or {}).get("name", "")
    place = f" {target}" if target and target != "generic" else ""
    if kind == "unknown_referent":
        roster = ""
        if world is not None:
            nation = _issuer_nation(world, marshal_name)
            names = sorted(m.name for m in (getattr(world, "marshals", {}) or {}).values()
                           if getattr(m, "nation", None) == nation and m.name != marshal_name
                           and getattr(m, "strength", 0) > 0
                           and not getattr(m, "captured_by", ""))
            if names:
                roster = " He may wait for " + ", ".join(names[:6]) + "."
        return (f"Berthier sets down his pen. \"Sire, I find no '{name}' in the "
                f"order of battle — {who} would hold until the end of the war. "
                f"Nothing has been relayed.{roster}\"")
    if kind == "enemy_referent":
        return (f"Berthier sets down his pen. \"Sire, {name} serves the enemy — a "
                f"hold that waits on HIS arrival is a hold until attacked, and "
                f"{who} would meet him standing anyway. Nothing has been relayed. "
                f"Say 'hold{place}' and he holds until relieved of the order.\"")
    if kind == "self_referent":
        return (f"Berthier sets down his pen. \"Sire, {who} cannot wait for his own "
                f"arrival. Nothing has been relayed. Name the marshal he is to wait "
                f"for, or say 'hold{place}' and he holds until relieved of the order.\"")
    if kind == "fallen_referent":
        return (f"Berthier sets down his pen. \"Sire, {name} is not in the field and "
                f"will not arrive. Nothing has been relayed. Name a marshal who can "
                f"reach him, or say 'hold{place}'.\"")
    if kind == "zero_turns":
        return (f"Berthier sets down his pen. \"Sire, a hold of no turns is no hold "
                f"at all. Nothing has been relayed. Name the turns — 'hold{place} for "
                f"3 turns' — or the relief: 'hold{place} until Davout arrives'.\"")
    if kind == "turn_passed":
        return (f"Berthier sets down his pen. \"Sire, it is turn {detail.get('current')} "
                f"— turn {detail.get('turn')} is behind us. Nothing has been relayed. "
                f"Name a turn still to come, or a duration: 'hold{place} for 3 turns'.\"")
    return ("Berthier sets down his pen. \"Sire, that condition is not one I can "
            "hold. Nothing has been relayed.\"")


def notes_sentence(notes: List[str], unread: List[str]) -> str:
    """The echo's second half: how the clauses were read, and which were not."""
    parts: List[str] = []
    if notes:
        parts.append("; ".join(notes) + ".")
    if unread:
        quoted = ", ".join(f"'{c}'" for c in unread)
        verb = "is not a clause" if len(unread) == 1 else "are not clauses"
        parts.append(f"{quoted} {verb} I can hold — the order stands without it.")
    if not parts:
        return ""
    return " Berthier: \"" + " ".join(parts) + "\""


# ═══════════════════════════════════════════════════════════════════════════
# SF-CMD-1 W2 (Oct 3, 2026) — THE CONTINGENCY PHRASINGS, said in CR-7's own
# vocabulary where the engine can hold them, refused where it cannot.
#
# Measured on the blind census: "march to Swabia and attack Mack when you get
# there", "if Mack is still in Swabia, attack him", "once Ney engages Mack,
# hit his flank" and "head for Swabia but stop if Mack turns on you" were all
# refused as "a contingency, not an order", while each is an order the
# engine already takes in other words:
#   • "when you get there" IS the arrival tail (CR-7-1 fuses "march to X and
#     attack Y" — the idiom is an adverb of the tail, not a condition);
#   • "if Mack is still in Swabia" is a PREMISE about the present board,
#     checked once at issuance (fog-honestly) — true, the order runs now;
#     false or unseen, it is refused free by name;
#   • "once Ney engages Mack, hit his flank" is the SUPPORT road — Soult
#     marches to Ney and joins his battle;
#   • "but stop if Mack turns on you" is the march's own rule — the contact
#     interrupt halts the column and asks when an enemy stands in the road.
# "attack Mack if he moves" stays a refusal: nothing watches an enemy's
# movement, and §2e holds no order for a later turn. The refusal names the
# road that does follow him (pursue).
# Each reader is PURE and lever-gated; the levers restore the refusal.
# ═══════════════════════════════════════════════════════════════════════════
THE_ARRIVAL_IDIOM_IS_THE_TAIL = True
A_PREMISE_IS_CHECKED_AT_ISSUANCE = True
AN_ENGAGEMENT_CLAUSE_IS_SUPPORT = True
A_HALT_TAIL_IS_THE_ROADS_OWN_RULE = True

_ON_ARRIVAL_IDIOM_RE = re.compile(
    r"\s*,?\s*(?:(?:when|once|as\s+soon\s+as|the\s+moment|after|if)\s+"
    r"(?:you|he|she|they|it)\s+(?:get|gets|got|arrive|arrives|arrived|reach|reaches|reached"
    r"|is|are)(?:\s+(?:there|it|him|the\s+place|the\s+field|at\s+the\s+walls))?"
    r"|(?:up)?on\s+(?:your\s+|his\s+)?arrival(?:\s+there)?)\s*[.!]*\s*$",
    re.IGNORECASE)
_PREMISE_RE = re.compile(
    r"^\s*(?:(?P<addr>(?:" + HONORIFIC + r")?[A-Za-z][\w'’-]*)\s*[,:]\s*)?"
    r"(?:if|provided|provided\s+that|so\s+long\s+as|as\s+long\s+as)\s+"
    r"(?P<foe>(?:the\s+)?[A-Za-z][\w'’-]*(?:\s+[A-Z][\w'’-]*)?)\s+"
    r"(?:is|are|'s|stands|sits|remains)\s+(?:still\s+)?(?:in|at|standing\s+in|sitting\s+in|holding|near)\s+"
    r"(?P<place>[A-Za-z][\w'’ -]{2,40}?)\s*,\s*(?P<rest>.+)$", re.IGNORECASE)
# SF-RR1 / SFR-H1 (Score Finish Step 9, October 5, 2026): "Ney, if Mack's
# still in Swabia, attack him" was refused as a contingency on the fresh HOLD.
# The foe's character class takes the apostrophe, so "Mack's" swallowed its
# own verb and nothing was left to match "'s". The foe is read lazily and the
# contracted verb may be attached ("Mack's", "Mack’s"). Flip lever: False.
A_CONTRACTED_PREMISE_IS_READ = True
_PREMISE_RE_CONTRACTED = re.compile(
    r"^\s*(?:(?P<addr>(?:" + HONORIFIC + r")?[A-Za-z][\w'’-]*)\s*[,:]\s*)?"
    r"(?:if|provided|provided\s+that|so\s+long\s+as|as\s+long\s+as)\s+"
    r"(?P<foe>(?:the\s+)?[A-Za-z][\w'’-]*?(?:\s+[A-Z][\w'’-]*?)?)"
    r"(?:\s+(?:is|are|'s|stands|sits|remains)|['’]s)\s+(?:still\s+)?"
    r"(?:in|at|standing\s+in|sitting\s+in|holding|near)\s+"
    r"(?P<place>[A-Za-z][\w'’ -]{2,40}?)\s*,\s*(?P<rest>.+)$", re.IGNORECASE)
_HALT_TAIL_RE = re.compile(
    r"\s*,?\s*(?:but|and)\s+(?:stop|halt|hold|wait|pause|pull\s+up|turn\s+back|fall\s+back|withdraw)"
    r"\s+(?:if|when|should|once|the\s+moment)\s+.+$", re.IGNORECASE)


def strip_arrival_idiom(text: str) -> Tuple[str, bool]:
    """"… and attack Mack when you get there" -> "… and attack Mack", True."""
    if not THE_ARRIVAL_IDIOM_IS_THE_TAIL or not text:
        return text, False
    m = _ON_ARRIVAL_IDIOM_RE.search(text)
    if not m or m.start() == 0:
        return text, False
    return text[:m.start()].rstrip(), True


# DD-0 S4 (October 10, 2026; SFR-D20 / SFR-H13): two more PREMISES about the
# board as it stands — "attack Mack if he is still standing" (the foe is alive
# and in sight) and "If Ney beat Mack, give him a rente" (a battle on the
# record). Each is a fact the game holds and checks ONCE at issuance; a false
# one is refused free by name. "him" in the rest is the premise's own subject:
# the FOE for the standing shape, the FRIEND for the battle shape. (No lever —
# the code-health ratchet holds levers lower-only.)
_STILL_STANDING = (r"(?:is|are|'s|’s)\s+still\s+(?:standing|alive|there|about|around|in\s+the\s+field|"
                   r"on\s+the\s+board|in\s+play|at\s+large|with\s+us|in\s+sight)")
_PREMISE_STANDING_TRAIL_RE = re.compile(
    r"^(?P<rest>.+?)\s*,?\s+(?:if|provided|so\s+long\s+as|as\s+long\s+as|while)\s+"
    r"(?P<foe>he|they|it|(?:the\s+)?[A-Za-z][\w'’-]*(?:\s+[A-Z][\w'’-]*)?)\s+" + _STILL_STANDING
    + r"\s*[.!]*$", re.IGNORECASE)
_PREMISE_STANDING_LEAD_RE = re.compile(
    r"^\s*(?:(?P<addr>(?:" + HONORIFIC + r")?[A-Za-z][\w'’-]*)\s*[,:]\s*)?"
    r"(?:if|provided|so\s+long\s+as|as\s+long\s+as|while)\s+"
    r"(?P<foe>(?:the\s+)?[A-Za-z][\w'’-]*(?:\s+[A-Z][\w'’-]*)?)\s+" + _STILL_STANDING
    + r"\s*,\s*(?P<rest>.+)$", re.IGNORECASE)
_PREMISE_BATTLE_RE = re.compile(
    r"^\s*(?:(?P<addr>(?:" + HONORIFIC + r")?[A-Za-z][\w'’-]*)\s*[,:]\s*)?"
    r"(?:if|provided|so\s+long\s+as|as\s+long\s+as|since|now\s+that)\s+(?:" + HONORIFIC + r")?"
    r"(?P<friend>[A-Za-z][\w'’-]*)\s+(?:has\s+|have\s+)?(?:beat|beaten|defeated|thrashed|routed|broke|broken|"
    r"bested|whipped|drove\s+off|driven\s+off|won\s+against|prevailed\s+over)\s+(?:" + HONORIFIC + r")?"
    r"(?P<foe>[A-Za-z][\w'’-]*(?:\s+[A-Z][\w'’-]*)?)\s*,\s*(?P<rest>.+)$", re.IGNORECASE)


def _resolve_name(typed: str, names) -> Optional[str]:
    low = re.sub(r"^the\s+", "", (typed or "").strip(), flags=re.I).lower()
    for n in names:
        if low in {p.lower() for p in _patterns(n)} | {str(n).lower()}:
            return n
    return None


def _split_standing_or_battle(text: str, enemy_names, friendly_names) -> Tuple[str, Optional[Dict]]:
    m = _PREMISE_STANDING_LEAD_RE.match(text) or _PREMISE_STANDING_TRAIL_RE.match(text)
    if True:
        if m:
            rest = m.group("rest").strip()
            foe_text = m.group("foe").strip()
            if foe_text.lower() in ("he", "they", "it"):
                from backend.ai.reading import foe_named_in
                foe = foe_named_in(rest, enemy_names)
            else:
                foe = _resolve_name(foe_text, enemy_names)
            if foe:
                rest = re.sub(r"\b(?:him|them|it)\b", foe, rest, count=1, flags=re.I)
                addr = (m.groupdict().get("addr") or "").strip()
                rebuilt = f"{addr}, {rest}" if addr else rest
                return rebuilt, {"kind": "standing", "marshal": foe, "region": None,
                                 "clause": m.group(0)[m.start("foe") - m.start(0):].strip()}
    if friendly_names:
        m = _PREMISE_BATTLE_RE.match(text)
        if m:
            friend = _resolve_name(m.group("friend"), friendly_names)
            foe = _resolve_name(m.group("foe"), enemy_names)
            if friend and foe:
                rest = re.sub(r"\b(?:him|her)\b", friend, m.group("rest").strip(), count=1, flags=re.I)
                rest = re.sub(r"\s+for\s+(?:it|that|this|the\s+victory|his\s+victory|his\s+trouble)\s*[.!]*$",
                              "", rest, flags=re.I)
                addr = (m.group("addr") or "").strip()
                rebuilt = f"{addr}, {rest}" if addr else rest
                return rebuilt, {"kind": "battle", "marshal": foe, "friend": friend, "region": None,
                                 "clause": text[m.start("friend"):m.end("foe")].strip()}
    return text, None


def battle_on_record(world, friend: str, foe: str) -> Optional[bool]:
    """True when the event log holds a battle the friend WON against the foe,
    False when it holds none; None when the world keeps no log."""
    log = getattr(world, "event_log", None)
    if not isinstance(log, list):
        return None
    for ev in log:
        if not isinstance(ev, dict) or ev.get("type") != "battle":
            continue
        att = (ev.get("attacker") or {}).get("name") if isinstance(ev.get("attacker"), dict) else None
        dfn = (ev.get("defender") or {}).get("name") if isinstance(ev.get("defender"), dict) else None
        outcome = str(ev.get("outcome") or "")
        if att == friend and dfn == foe and ("attacker" in outcome and "victory" in outcome
                                             or ev.get("marshal_destroyed") or ev.get("marshal_captured")):
            return True
        if dfn == friend and att == foe and "defender" in outcome and "victory" in outcome:
            return True
    return False


def split_premise(text: str, enemy_names, region_names, friendly_names=()) -> Tuple[str, Optional[Dict]]:
    """"if Mack is still in Swabia, attack him" -> ("attack Mack", {"marshal":
    "Mack", "region": "Swabia"}); a sentence of any other shape is returned
    unchanged with None. A bare object pronoun in the rest is the premise's
    own man. Names are matched against the rosters handed in (pure)."""
    if not A_PREMISE_IS_CHECKED_AT_ISSUANCE or not text:
        return text, None
    m = (_PREMISE_RE_CONTRACTED if A_CONTRACTED_PREMISE_IS_READ
         else _PREMISE_RE).match(text)
    if not m:
        return _split_standing_or_battle(text, enemy_names, friendly_names)
    foe_text = re.sub(r"^the\s+", "", m.group("foe").strip(), flags=re.I).lower()
    place_text = m.group("place").strip().lower()
    foe = next((n for n in enemy_names
                if foe_text in {p.lower() for p in _patterns(n)} | {str(n).lower()}), None)
    place = next((r for r in region_names if str(r).lower() == place_text), None)
    if not foe or not place:
        return text, None
    rest = m.group("rest").strip()
    rest = re.sub(r"\b(?:him|them|it)\b", foe, rest, count=1, flags=re.I)
    addr = (m.group("addr") or "").strip()
    rebuilt = f"{addr}, {rest}" if addr else rest
    return rebuilt, {"marshal": foe, "region": place, "clause": text[m.start('foe') - 3:m.end('place')].strip() if m.start('foe') >= 3 else text[:m.end('place')]}


def _patterns(name):
    from backend.ai.llm_client import name_match_patterns
    return list(name_match_patterns(str(name)))


def premise_refusal(world, premise: Optional[Dict]) -> Optional[str]:
    """The sentence that refuses an order whose premise does not hold on the
    board the player can SEE — or None when it holds. Fog-honest: an unseen
    man is "no word", never a guess."""
    if not premise or world is None:
        return None
    from backend.display_names import humanize_entity_name
    from backend.models.intel import PARTIAL
    name = str(premise.get("marshal") or "")
    place = str(premise.get("region") or "")
    shown = humanize_entity_name(name)
    enemy = world.get_marshal(name)
    kind = premise.get("kind")
    if kind == "battle":
        friend = str(premise.get("friend") or "")
        won = battle_on_record(world, friend, name)
        if won:
            return None
        return (f"The order rested on {friend} having beaten {shown}, Sire, and "
                f"{'no such battle is on the record' if won is False else 'the record holds no battles'}"
                f" — nothing has been relayed.")
    # DD-0 S4: the STANDING shape ("if he is still standing") shares every
    # check but the place — one road, one guard.
    standing = kind == "standing"
    rested = f"{shown} still standing" if standing else f"{shown} standing at {place}"
    if enemy is None or int(getattr(enemy, "strength", 0) or 0) <= 0:
        return (f"The order rested on {rested}, Sire, and he leads "
                f"no army our maps know — nothing has been relayed.")
    if getattr(enemy, "captured_by", ""):
        return (f"The order rested on {rested}, Sire, and he is a "
                f"prisoner — nothing has been relayed.")
    try:
        seen = world.get_region_intel(enemy.location).visibility_at_least(PARTIAL)
    except Exception:
        seen = False
    if not seen:
        return (f"The order rested on {rested}, Sire, and we have no "
                f"word of him — scout before you condition an order on "
                f"{'him' if standing else 'his position'}. Nothing has been relayed.")
    if standing:
        return None
    if enemy.location != place:
        return (f"The order rested on {shown} standing at {place}, Sire, and our last "
                f"word places him at {enemy.location} — so it does not go out. Nothing "
                f"has been relayed.")
    return None


def rewrite_engagement_support(text: str, friendly_names) -> Tuple[str, Optional[str]]:
    """"Soult, once Ney engages Mack, hit his flank" -> ("Soult, support Ney",
    "Ney"). The friend must be one of OURS, the clause a single engagement
    verb, the residue a flank/rear/join phrase; anything else is unchanged."""
    if not AN_ENGAGEMENT_CLAUSE_IS_SUPPORT or not text:
        return text, None
    friends = sorted({str(n) for n in friendly_names if n}, key=len, reverse=True)
    if not friends:
        return text, None
    names = "|".join(re.escape(n) for n in friends)
    m = re.match(
        r"^\s*(?:(?P<addr>(?:" + HONORIFIC + r")?[A-Za-z][\w'’-]*)\s*[,:]\s*)?"
        r"(?:once|when|as\s+soon\s+as|after|if)\s+(?:" + HONORIFIC + r")?(?P<friend>" + names + r")\s+"
        r"(?:engages?|attacks?|fights?|strikes?|closes?\s+with|is\s+engaged\s+with|hits?|goes?\s+in"
        r"|has\s+engaged|makes?\s+contact\s+with)\b[^,]*,\s*"
        r"(?:(?:hit|strike|attack|fall\s+on|take|turn\s+on|go\s+for|roll\s+up)\s+(?:his|their|the|its)\s+(?:flank|rear|flanks|left|right)"
        r"|(?:join|support|back|second)\s+(?:him|them|the\s+attack|in|the\s+fight|the\s+battle)"
        r"|(?:come|go)\s+in\s+(?:behind|beside)\s+him|pile\s+in)\b",
        text, flags=re.IGNORECASE)
    if not m:
        # the trailing form: "charge Mack when Ney engages (him)"
        m2 = re.match(
            r"^\s*(?:(?P<addr>(?:" + HONORIFIC + r")?[A-Za-z][\w'’-]*)\s*[,:]\s*)?"
            r"(?:charge|attack|hit|strike|fall\s+on|join|go\s+in|pile\s+in|engage)\b[^,]*?\s+"
            r"(?:when|once|as\s+soon\s+as|after)\s+(?:" + HONORIFIC + r")?(?P<friend>" + names + r")\s+"
            r"(?:engages?|attacks?|fights?|strikes?|closes?\s+with|is\s+engaged|goes?\s+in|makes?\s+contact)"
            r"(?:\s+(?:him|them|the\s+enemy|[A-Z][\w'’-]*))?\s*[.!]*$", text, flags=re.IGNORECASE)
        if not m2:
            return text, None
        friend = next(n for n in friends if n.lower() == m2.group("friend").lower())
        addr = (m2.group("addr") or "").strip()
        return (f"{addr}, support {friend}" if addr else f"support {friend}"), friend
    friend = next(n for n in friends if n.lower() == m.group("friend").lower())
    addr = (m.group("addr") or "").strip()
    rebuilt = f"{addr}, support {friend}" if addr else f"support {friend}"
    return rebuilt, friend


def strip_halt_tail(text: str) -> Tuple[str, Optional[str]]:
    """"Lannes, head for Swabia but stop if Mack turns on you" -> ("Lannes,
    head for Swabia", "but stop if Mack turns on you")."""
    if not A_HALT_TAIL_IS_THE_ROADS_OWN_RULE or not text:
        return text, None
    m = _HALT_TAIL_RE.search(text)
    if not m or m.start() == 0:
        return text, None
    return text[:m.start()].rstrip(" ,"), text[m.start():].strip(" ,")


HALT_TAIL_NOTE = ("The march halts of itself when an enemy stands in the road, Sire, and "
                  "asks for your orders — that is the road's own rule, so the '{tail}' "
                  "is kept without a dispatch.")
