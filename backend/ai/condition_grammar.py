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
ARRIVAL_TAIL_RE = re.compile(
    r"\s*(?:,\s*|;\s*|\s+(?:and\s+then|and|then)\s+)(?:attack|engage|assault)\b.*$")

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
