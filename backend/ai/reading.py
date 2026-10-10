"""DD-0 S4 "The Command Road" — THE READING (October 10, 2026;
PRE_DEPLOY_PLAN.md §3.0 "the structural fix"; rules SYSTEMS_REFERENCE.md §104).

One tokenised reading of the typed line, carried through the parse. The
typed text is IMMUTABLE here: every stage records a SPAN over it (what was
peeled, and why), and the string the downstream readers see is COMPOSED
from the spans — the address, the residue, the relay — never produced by
splicing one reader's output into the next reader's input. Three producers
used to re-read the raw text in series (the mock chain, the strategic layer,
the fuzzy scan), so each guard had to blank its clause with spaces to keep
every other reader's positions aligned, and a fix to one reader shipped a
hole in another (slice 1, slice 7, CRT-1, PARSE-NEG, the IQ-7 grammar, each
with a P1 found inside the fix). The Reading peels from the OUTSIDE IN —
the suffixes and tails first, then the address, then the core — so a tail
can never become a province and a trailing name can never become the man
the order is about.

Stages (each one row on the parse trace, `reading · <rule>`):

  peel_rhetoric          "It's Mack's turn. Ney, at him."  — a leading sentence
                         that gives no order and names no man of ours is set
                         aside; a foe it names is kept as the pronoun's hint
  peel_support_suffix    "… with Lannes in support"  — the second man's order
                         rides the relay ("…, then Lannes, support Ney"),
                         whatever the head's verb (the ledger's second-name
                         class: take / move / a typo / a telegraph)
  peel_precaution        "…, in case Mack turns on him"  — a precaution is no
                         condition and no reason; it is kept without a dispatch
  peel_reason_tail       "… because the men are ready"  — a reason of OURS
                         (the enemy's movements are clause_guards' — CRT-1)
  peel_trailing_vocative "wait, Ney" / "protect Davout, Ney"  — the man after
                         the comma is the ADDRESSEE, and the line is read as
                         "Ney, wait" / "Ney, protect Davout"
  read_address           "Prince Murat, …" / "Davout will cover …"  — the
                         addressee through his honorific and his modal
  peel_comma_aside       "cancel, the men are rested" / "…, they're green" /
                         "…, via the shortest road"  — a comma clause that
                         names no man, no place and no order is an aside
  rewrite_at_him         "Ney, at him"  — the field's shortest attack

GR6: deterministic, pure text in → text out, no world read beyond the
rosters handed in. Nothing mechanical reads a Reading; it enters no save.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Tuple

from backend.display_names import humanize_entity_name

# The honorifics an address may carry (the player's roster is French, but the
# blind authors wrote "Prince Murat" and "the Marshal Ney").
HONORIFIC_RX = r"(?:the\s+)?(?:marshal|general|gen\.|mar[eé]chal|prince|duke|count|baron)\s+"
_MODAL_RX = r"(?:will|shall|is\s+to|should|must|is\s+going\s+to)\s+"

# The verbs an order may carry — a tail or an aside that holds one is NOT
# peeled (it may be a second order). Inflections are read through (\w*).
ORDER_VERB_RX = re.compile(
    r"\b(?:attack|assault|storm|engage|charge|bombard|pursue|chase|hunt|move|march|"
    r"advance|go|head|proceed|ride|withdraw|retreat|retire|fall\s+back|hold|defend|"
    r"guard|protect|cover|fortify|entrench|dig\s+in|unfortify|drill|train|scout|"
    r"recruit|raise|levy|build|construct|repair|garrison|detach|support|reinforce|"
    r"aid|help|join|wait|stand|form|cancel|halt|stop|sail|land|blockade|declare|"
    r"propose|offer|send|invest|grant|cede|enact|repeal|commission|reward|end|take|"
    r"strike|hit|relocate|redeploy|secure|seize|occupy|follow|screen|shield|back|"
    r"find|look|see|report|get|put|bring|keep|leave|stay|come|exercise|"
    r"dig|throw|press|pull|push|break|make|give|pay|open|let|have|tell|fire|fight|"
    r"burn|cross|camp|watch|observe|probe|feint|sortie|raid|plunder|loot|sack)"
    r"(?:s|es|ed|ing)?\b",
    re.IGNORECASE)
# An aside may also be a short adverbial — but only one that OPENS as one
# ("via the shortest road", "at the double", "now"), never a bare noun phrase.
_ADVERBIAL_OPEN_RX = re.compile(
    r"^(?:via|by|along|through|at\s+the\s+double|at\s+once|at\s+all\s+costs|now|today|tonight|"
    r"this\s+(?:turn|instant|very)|quickly|quietly|swiftly|immediately|carefully|"
    r"with\s+all\s+(?:possible\s+)?speed|in\s+haste|on\s+the\s+double|as\s+fast\s+as|"
    r"if\s+you\s+please|whatever\s+happens|come\s+what\s+may|no\s+matter\s+what)\b",
    re.IGNORECASE)
_NEGATION_RX = re.compile(r"\b(?:no|not|never|don'?t|do\s+not|unless|if|when|once|until|then|instead)\b",
                          re.IGNORECASE)
# Words of state in a tail that make it an order of state, never an aside.
_STATE_NOUN_RX = re.compile(r"\b(?:peace|alliance|treaty|war|gold|terms|tribute|law|vassal|mission|"
                            r"envoy|ambassador|pact|truce|armistice)\b", re.IGNORECASE)
# The shape of a clause of ours: a subject and a verb of being / having.
_CLAUSE_SHAPE_RX = re.compile(
    r"^(?:the|our|my|his|their|your|they|we|it|he|she|you|men|lads|everyone|everybody|"
    r"morale|supplies|time|there)\b.*?\b(?:is|are|was|were|'re|'s|’re|’s|have|has|had|"
    r"will|can|could|look|looks|seem|seems|be|been|need|needs|want|wants|"
    r"rested|ready|fresh|green|tired|low|high|short)\b", re.IGNORECASE)
_PRECAUTION_RX = re.compile(r"[\s,;]+(?:just\s+)?in\s+case\b.*$", re.IGNORECASE | re.DOTALL)
_BECAUSE_RX = re.compile(r"[\s,;]+(?:because|since|as|for)\s+(?P<why>(?:the|our|my|his|their|they|we|it)\b.+?)\s*[.!]*$",
                         re.IGNORECASE)
_SUPPORT_SUFFIX_RX_T = (r"[\s,]+with\s+(?:" + HONORIFIC_RX + r")?(?P<second>{names})\s+"
                        r"(?:in\s+support|supporting|in\s+reserve|backing\s+(?:him|them)\s+up|"
                        r"to\s+back\s+him\s+up|in\s+support\s+of\s+him|behind\s+him)\s*[.!]*$")
_TRAILING_VOCATIVE_RX_T = (r",\s*(?:please\s+)?(?:" + HONORIFIC_RX + r")?(?P<name>{names})\s*[.!]*$")
_LEADING_ADDRESS_RX_T = (r"^\s*(?:" + HONORIFIC_RX + r")?(?P<name>{names})\b\s*"
                         r"(?:(?P<sep>[,:;])\s*|(?P<modal>" + _MODAL_RX + r")|(?P<space>\s+))")
_AT_HIM_RX = re.compile(r"^\s*(?:go\s+)?at\s+(?:him|them|'em|’em|the\s+enemy|the\s+foe|it)\s*[.!]*$",
                        re.IGNORECASE)
_SENTENCE_SPLIT_RX = re.compile(r"(?<=[.!])\s+(?=[A-Za-z])")

# The note a peeled precaution leaves on the `warning` seam (the halt-tail
# precedent): the order went out; the "in case" is kept without a dispatch.
PRECAUTION_NOTE = ("The 'in case' is a precaution, Sire — the order goes out as given, and "
                   "the column asks for your word of itself if the enemy appears.")
_FRIEND_WORD_RX = re.compile(r"[A-Za-z][\w'’-]*")


@dataclass
class Span:
    kind: str
    start: int
    end: int
    text: str


@dataclass
class Reading:
    typed: str
    spans: List[Span] = field(default_factory=list)
    address: Optional[str] = None          # the addressee, canonical roster name
    address_rotated: bool = False          # the address came from a trailing vocative
    address_modal: bool = False            # "Davout will …" read as "Davout, …"
    second: Optional[str] = None           # "… with Lannes in support" → Lannes
    second_lead: Optional[str] = None      # the man the suffix's head addressed
    hint_foe: Optional[str] = None         # a foe named by a peeled sentence
    core_override: Optional[str] = None    # a rewritten core ("at him" → "attack Mack")
    notes: List[str] = field(default_factory=list)
    rows: List[Tuple[str, str, str]] = field(default_factory=list)   # (rule, before, after)

    # ── the derived views ────────────────────────────────────────────────
    def residue(self) -> str:
        """The typed line with every peeled span removed — derived, never
        mutated. Whitespace and dangling punctuation are collapsed."""
        cut = sorted(((s.start, s.end) for s in self.spans), key=lambda p: p[0])
        out = []
        pos = 0
        for a, b in cut:
            if a > pos:
                out.append(self.typed[pos:a])
            pos = max(pos, b)
        out.append(self.typed[pos:])
        text = "".join(out)
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"\s+([,;:.!?])", r"\1", text)
        text = re.sub(r"^[,;:\s]+", "", text)
        text = re.sub(r"[,;:\s]+$", "", text)
        return text

    def core(self) -> str:
        """The order after the address."""
        if self.core_override is not None:
            return self.core_override
        text = self.residue()
        if self.address and not self.address_rotated:
            m = _leading_address_match(text, [self.address])
            if m:
                text = text[m.end():].strip()
        return text

    def text(self) -> str:
        """The line the downstream readers see — composed from the spans."""
        core = self.core()
        if self.address and (self.address_rotated or self.address_modal
                             or self.core_override is not None):
            composed = f"{self.address}, {core}" if core else self.address
        elif self.address and self.core_override is None:
            composed = self.residue()
        else:
            composed = core
        composed = composed.rstrip(" .")
        lead = self.address or self.second_lead
        if self.second and lead:
            composed = f"{composed}, then {self.second}, support {lead}"
        return composed

    def _record(self, rule: str, before: str) -> None:
        after = self.text()
        if after != before:
            self.rows.append((rule, before, after))


# ── helpers ─────────────────────────────────────────────────────────────

def _alt(names: Iterable[str]) -> str:
    return "|".join(re.escape(str(n)) for n in sorted({str(n) for n in names if n},
                                                       key=len, reverse=True))


def _canonical(typed: str, names: Iterable[str]) -> Optional[str]:
    low = typed.strip().lower()
    for n in names:
        if str(n).lower() == low:
            return str(n)
    return None


def _leading_address_match(text: str, friends: Iterable[str]):
    alt = _alt(friends)
    if not alt:
        return None
    return re.match(_LEADING_ADDRESS_RX_T.format(names=alt), text, flags=re.IGNORECASE)


def _known_tokens(names: Iterable[str]) -> set:
    toks = set()
    for n in names or []:
        for t in re.findall(r"[a-z][a-z'’-]+", str(n).lower()):
            toks.add(t)
    return toks


def foe_forms(enemy_names: Iterable[str]) -> List[str]:
    """Every form a foe may be named by: the roster key ("ArchdukeJohn"),
    the printed form ("Archduke John") and the bare surname ("John",
    "Charles", "Mack") when it names one foe only."""
    names = [str(n) for n in enemy_names if n]
    forms: List[str] = []
    seen = set()
    surnames = {}
    for n in names:
        human = humanize_entity_name(n)
        for f in (n, human):
            if f and f.lower() not in seen:
                seen.add(f.lower())
                forms.append(f)
        last = human.split()[-1] if human and " " in human else None
        if last and len(last) >= 4:
            surnames.setdefault(last.lower(), set()).add(n)
    for last, owners in surnames.items():
        if len(owners) == 1 and last not in seen:
            seen.add(last)
            forms.append(last[:1].upper() + last[1:])
    return forms


def foe_named_in(text: str, enemy_names: Iterable[str]) -> Optional[str]:
    """The roster key of the first foe the text names, by any form."""
    names = [str(n) for n in enemy_names if n]
    for form in sorted(foe_forms(names), key=len, reverse=True):
        if re.search(r"\b" + re.escape(form) + r"\b", text, flags=re.IGNORECASE):
            for n in names:
                if form.lower() in (n.lower(), humanize_entity_name(n).lower(),
                                    humanize_entity_name(n).split()[-1].lower()):
                    return n
            return form
    return None


# ── the stages ───────────────────────────────────────────────────────────

def peel_rhetoric(r: Reading, friends: Iterable[str], foes: Iterable[str]) -> None:
    """A leading sentence that gives no order and names none of ours is set
    aside; the first foe it names is the pronoun's hint for `at him`."""
    text = r.residue()
    if "?" in text:
        return
    parts = _SENTENCE_SPLIT_RX.split(text)
    if len(parts) < 2:
        return
    first = parts[0]
    rest = text[len(first):].strip()
    if not rest or not first.strip():
        return
    # "maybe Gen. Ney, hold" — an abbreviation's period is no sentence end,
    # and a hedge ("maybe", "perhaps") is the line's mood, never rhetoric
    # to set aside (the metamorphic hedge family must keep flipping).
    if re.search(r"\b(?:gen|mar|lt|col|maj|capt|st|mr|dr|no)\.$", first, flags=re.IGNORECASE):
        return
    if re.search(r"\b(?:maybe|perhaps|possibly|might|may|could|should|would|wonder|whether|"
                 r"consider|suppose|think|if|unless)\b", first, flags=re.IGNORECASE):
        return
    friend_toks = _known_tokens(friends)
    first_toks = set(re.findall(r"[a-z][a-z'’-]+", first.lower()))
    if first_toks & friend_toks or ORDER_VERB_RX.search(first):
        return
    if not _leading_address_match(rest, friends):
        return
    before = r.text()
    start = r.typed.lower().find(first.lower())
    if start < 0:
        return
    r.spans.append(Span("rhetoric", start, start + len(first), first))
    r.hint_foe = foe_named_in(first, foes)
    r._record("peel_rhetoric", before)


def peel_support_suffix(r: Reading, friends: Iterable[str]) -> None:
    alt = _alt(friends)
    if not alt:
        return
    text = r.residue()
    m = re.search(_SUPPORT_SUFFIX_RX_T.format(names=alt), text, flags=re.IGNORECASE)
    if not m or not text[:m.start()].strip():
        return
    second = _canonical(m.group("second"), friends)
    head = text[:m.start()]
    lead = _leading_address_match(head, friends)
    if not second or not lead:
        return
    addressee = _canonical(lead.group("name"), friends)
    if not addressee or addressee.lower() == second.lower():
        return
    before = r.text()
    _peel_tail(r, m.group(0))
    r.second = second
    r.second_lead = addressee
    r._record("peel_support_suffix", before)


def _peel_tail(r: Reading, tail_text: str) -> bool:
    """Mark the LAST occurrence of `tail_text` in the typed line as peeled
    (the residue is derived from the typed line, so the span is located
    there; the stages only ever peel from the end)."""
    needle = tail_text.strip()
    if not needle:
        return False
    # the LAST occurrence not already peeled (a repeated aside — "…, the men
    # are rested, the men are rested" — is two spans, not one found twice);
    # whitespace-tolerant, since the residue collapsed it
    pat = re.compile(r"\s*".join(re.escape(w) for w in needle.split()), re.IGNORECASE)
    taken = [(s.start, s.end) for s in r.spans]
    hit = None
    for m in reversed(list(pat.finditer(r.typed))):
        if not any(m.start() < b and a < m.end() for a, b in taken):
            hit = m
            break
    if hit is None:
        return False
    pos, end = hit.start(), hit.end()
    # swallow the punctuation and space that led into the tail
    while pos > 0 and r.typed[pos - 1] in " ,;—–-":
        pos -= 1
    while end < len(r.typed) and r.typed[end] in " .!":
        end += 1
    r.spans.append(Span("tail", pos, end, r.typed[pos:end]))
    return True


def peel_precaution(r: Reading) -> None:
    from backend.ai.clause_guards import AN_IN_CASE_IS_A_PRECAUTION
    if not AN_IN_CASE_IS_A_PRECAUTION:
        return   # the guard's own lever: the "in case" is then a condition
    text = r.residue()
    m = _PRECAUTION_RX.search(text)
    if not m or not text[:m.start()].strip():
        return
    before = r.text()
    if _peel_tail(r, m.group(0)):
        r.notes.append("in case")
        r._record("peel_precaution", before)


def peel_reason_tail(r: Reading, known_names: Iterable[str]) -> None:
    text = r.residue()
    m = _BECAUSE_RX.search(text)
    if not m or not text[:m.start()].strip():
        return
    why = m.group("why")
    if (set(re.findall(r"[a-z][a-z'’-]+", why.lower())) & _known_tokens(known_names)
            or ORDER_VERB_RX.search(why)):
        return
    before = r.text()
    if _peel_tail(r, m.group(0)):
        r._record("peel_reason_tail", before)


def peel_trailing_vocative(r: Reading, friends: Iterable[str]) -> None:
    """", Ney" at the end of a line that does not open with an address: the
    man after the comma is the addressee."""
    alt = _alt(friends)
    if not alt or r.address:
        return
    text = r.residue()
    m = re.search(_TRAILING_VOCATIVE_RX_T.format(names=alt), text, flags=re.IGNORECASE)
    if not m:
        return
    head = text[:m.start()].strip()
    if not head or _leading_address_match(head, friends):
        return
    name = _canonical(m.group("name"), friends)
    if not name:
        return
    before = r.text()
    if _peel_tail(r, m.group(0)):
        r.address = name
        r.address_rotated = True
        r._record("peel_trailing_vocative", before)


def read_address(r: Reading, friends: Iterable[str]) -> None:
    """The addressee at the head, through an honorific ("Prince Murat,") and
    a modal ("Davout will cover …" → "Davout, cover …"). A modal before a
    negation is left whole for the guards ("Ney will not attack")."""
    if r.address:
        return
    text = r.residue()
    m = _leading_address_match(text, friends)
    if not m:
        return
    name = _canonical(m.group("name"), friends)
    if not name:
        return
    rest = text[m.end():]
    if m.group("space") and not rest.strip():
        return
    before = r.text()
    r.address = name
    if m.group("modal"):
        if _NEGATION_RX.match(rest.strip()):
            r.address = None
            return
        r.address_modal = True
        r.core_override = rest.strip().rstrip(" .")
    elif m.group("sep") == "," and re.match(
            r"^\s*(?:" + HONORIFIC_RX + r")", text, flags=re.IGNORECASE):
        # "Prince Murat, …" / "the Marshal Ney, …" — an honorific before a
        # comma address is read through to the canonical "Murat, …". A colon
        # ("Marshal Ney: Brabant.") and a SPACE ("Marshal Ney moves to
        # Lorraine") are left to the telegraph and the inflected rewrites,
        # which read the honorific themselves.
        r.address_modal = True
        r.core_override = rest.strip().rstrip(" .")
    r._record("read_address", before)


def peel_comma_aside(r: Reading, known_names: Iterable[str], friends: Iterable[str]) -> None:
    """The last comma clause, when it names no man, no place, no order and
    carries no number or negation: "the men are rested", "they're green",
    "the cavalry is fresh", "via the shortest road", "now"."""
    text = r.core() if r.core_override is not None else r.residue()
    if "," not in text or "?" in r.typed:
        return
    head, _, tail = text.rpartition(",")
    head, tail = head.strip(), tail.strip().rstrip(" .!")
    tail = re.sub(r"^please\s+", "", tail, flags=re.IGNORECASE)
    if not head or not tail or "?" in tail:
        return
    # the head must be more than an address ("Ney, the men are rested" is a
    # statement, not an order with an aside)
    if _canonical(re.sub(r"^(?:" + HONORIFIC_RX + r")", "", head, flags=re.IGNORECASE), friends):
        return
    tail_toks = set(re.findall(r"[a-z][a-z'’-]+", tail.lower()))
    if (tail_toks & _known_tokens(known_names) or ORDER_VERB_RX.search(tail)
            or re.search(r"\d", tail) or _NEGATION_RX.search(tail)
            or _STATE_NOUN_RX.search(tail)):
        return
    words = tail.split()
    clause = bool(_CLAUSE_SHAPE_RX.match(tail))
    adverbial = len(words) <= 5 and bool(_ADVERBIAL_OPEN_RX.match(tail))
    if not (clause or adverbial):
        return
    before = r.text()
    if r.core_override is not None:
        r.core_override = head
        r._record("peel_comma_aside", before)
        return
    if _peel_tail(r, text[text.rfind(","):]):
        r._record("peel_comma_aside", before)


def rewrite_at_him(r: Reading, foes: Iterable[str]) -> None:
    if not r.address:
        return
    core = r.core()
    if not _AT_HIM_RX.match(core):
        return
    before = r.text()
    foe = r.hint_foe
    if foe is None:
        names = [str(n) for n in foes if n]
        foe = names[0] if len(names) == 1 else None
    shown = humanize_entity_name(foe) if foe else ""
    r.core_override = f"attack {shown}".strip()
    r._record("rewrite_at_him", before)


def read(typed: str, friends: Iterable[str], foes: Iterable[str],
         places: Iterable[str], nations: Iterable[str] = ()) -> Reading:
    """The whole reading, outside in. Pure."""
    r = Reading(typed=typed or "")
    if not r.typed.strip():
        return r
    friends = [str(n) for n in friends if n]
    foes = [str(n) for n in foes if n]
    known = list(friends) + list(foes) + [str(p) for p in places if p] + [str(n) for n in nations if n]
    peel_rhetoric(r, friends, foes)
    # the outermost tails first — the please / urgency and the dash aside
    # (S3b's predicates, applied as spans here), so a trailing vocative is
    # found at the END of what remains ("attack Davout, Ney, please")
    peel_please_and_dash_aside(r, known)
    peel_support_suffix(r, friends)
    # the vocative is peeled BEFORE the precaution ("… in case Mack comes,
    # Davout") and again after the asides ("stand behind Ney, Davout, in
    # case …", "attack Davout, Ney, the men are rested").
    peel_trailing_vocative(r, friends)
    peel_precaution(r)
    peel_reason_tail(r, known)
    peel_comma_aside(r, known, friends)
    peel_comma_aside(r, known, friends)   # a second aside behind the first
    peel_trailing_vocative(r, friends)
    read_address(r, friends)
    rewrite_at_him(r, foes)
    return r


def peel_please_and_dash_aside(r: Reading, known_names: Iterable[str]) -> None:
    """"…, please" / "… — thank you" / "… - at once" as spans (the S3b
    rules `strip_please_and_urgency` / `strip_dash_aside`, read here so the
    vocative and the asides behind them are found)."""
    from backend.ai import dd0_rewrites as _dd0
    for _ in range(2):
        text = r.residue()
        head = _dd0.strip_dash_aside(_dd0.strip_please_and_urgency(text), known_names)
        if head == text or not head.strip() or not text.startswith(head.rstrip(" ,;")):
            return
        before = r.text()
        tail = text[len(head.rstrip(" ,;")):]
        if not tail.strip(" ,;.!—–-") or not _peel_tail(r, tail):
            return
        r._record("peel_please_and_dash_aside", before)
