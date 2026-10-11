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
# S4 part 3: the courtesy modal — "Marshal Soult will be so good as to bring
# his corps up to the Rhineland" (the fourth set).
_MODAL_RX = (r"(?:(?:will|would|shall|is\s+to)\s+be\s+so\s+(?:good|kind)\s+as\s+to|"
             r"will|shall|is\s+to|should|must|is\s+going\s+to)\s+")

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
    r"burn|cross|camp|watch|observe|probe|feint|sortie|raid|plunder|loot|sack|use)"
    r"(?:s|es|ed|ing)?\b",
    re.IGNORECASE)
# An aside may also be a short adverbial — but only one that OPENS as one
# ("via the shortest road", "at the double", "now"), never a bare noun phrase.
_ADVERBIAL_OPEN_RX = re.compile(
    r"^(?:via|by|along|through|at\s+the\s+double|at\s+once|at\s+all\s+costs|now|today|tonight|"
    r"this\s+(?:turn|instant|very)|quickly|quietly|swiftly|immediately|carefully|"
    r"with\s+all\s+(?:possible\s+)?speed|in\s+haste|on\s+the\s+double|as\s+fast\s+as|"
    r"if\s+you\s+please|whatever\s+happens|come\s+what\s+may|no\s+matter\s+what|"
    # S4 part 3 (the fourth set): "double quick", "sharpish", "post-haste"
    r"double[\s-]quick|quick\s+march|smartly|sharpish|without\s+delay|forthwith|post-?haste|"
    r"and\s+(?:quickly|fast|smartly)|fast)\b",
    re.IGNORECASE)
# S4 part 3 (DD0-16): an EMPHATIC tail — "no excuses", "no delay", "no
# arguments" — carries a "no" and is no prohibition; it is an aside.
_EMPHATIC_TAIL_RX = re.compile(
    r"^(?:and\s+)?(?:no\s+(?:excuses?|delays?|arguments?|questions?|buts|dawdling|dallying|loitering|"
    r"hesitation|nonsense|objections?|complaints?|exceptions?)|without\s+fail|and\s+no\s+mistake|"
    r"and\s+be\s+quick\s+about\s+it|do\s+you\s+hear|you\s+hear|understood|is\s+that\s+clear|"
    r"that\s+is\s+an\s+order|that'?s\s+an\s+order)\s*[.!]*$",
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
    r"will|can|could|may|might|must|should|would|shall|look|looks|seem|seems|be|been|need|needs|want|wants|"
    r"rested|ready|fresh|green|tired|low|high|short)\b", re.IGNORECASE)
# DD0-19 (S4 part 4): a passive about US in an aside — "we may be attacked
# before the others arrive", "we could be cut off" — is a statement; the
# participle is not our order.
_PASSIVE_ABOUT_US_RX = re.compile(
    r"\b(?:we|they|the\s+men|the\s+corps|the\s+army|he|our\s+\w+)\s+(?:may|might|could|will|would|shall|can|must)?\s*"
    r"(?:be|get)\s+(?:attacked|assaulted|charged|bombarded|cut\s+off|flanked|surrounded|caught|struck|engaged|"
    r"pursued|driven|beaten|outflanked|overrun|hit)\b", re.IGNORECASE)
_PRECAUTION_RX = re.compile(r"[\s,;]+(?:just\s+)?in\s+case\b.*$", re.IGNORECASE | re.DOTALL)
# DD0-18 (c) (S4 part 4): "…, and keep an eye out for Charles on the way" —
# a watchfulness clause behind the order is a precaution too (the order goes
# out; the eye is kept without a dispatch). Only behind a HEAD that holds an
# order or a destination — "Murat, keep an eye on Berlin" is the scout.
_WATCH_PRECAUTION_RX = re.compile(
    r"[\s,;.]+(?:and\s+|but\s+)?(?:keep\s+an\s+eye\s+out\s+for|keep\s+an\s+eye\s+on|keep\s+a\s+watch\s+for|"
    r"watch\s+(?:out\s+)?for|look\s+out\s+for|beware\s+(?:of\s+)?|be\s+wary\s+of|mind|"
    # DD0-19: "Lannes to Bern. Watch the passes." — the ground to be watched
    r"watch\s+(?:the\s+)?(?:passes|pass|roads?|flanks?|river|frontier|border|approaches|coast|"
    r"rear|crossings?|bridges?|fords?))\b.*$",
    re.IGNORECASE | re.DOTALL)
_BECAUSE_RX = re.compile(r"[\s,;]+(?:because|since|as|for)\s+(?P<why>(?:the|our|my|his|their|they|we|it)\b.+?)\s*[.!]*$",
                         re.IGNORECASE)
# DD0-18 (c) (S4 part 4, October 11, 2026): the PURPOSE tail — "so he can
# screen the Emperor", "so that the road is covered", ", I want the Swiss road
# covered", "; the Dutch coast wants watching" — a reason in the future
# tense. The verb inside it is the purpose's, never a second order, so the
# order-verb test is not applied; a known name inside it still keeps it.
_PURPOSE_TAIL_RX = re.compile(
    r"[\s,;]+(?P<why>(?:so\s+(?:that\s+)?(?:he|she|they|we|it|you|the|our|his|their|my)\b.+?"
    r"|(?:i|we)\s+(?:want|need|would\s+like|must\s+have|shall\s+want)\s+(?:the|our|a|an|his|their|that|this|some|more)\b.+?"
    r"|(?:the|our|his|their)\s+[\w'’ -]{2,30}?\s+(?:wants?|needs?|bears?)\s+(?:watching|covering|guarding|holding|securing|screening)"
    r"))\s*[.!]*$",
    re.IGNORECASE)
# The participle purpose after a destination: "in Brabant covering the Dutch
# coast", "at Bern watching the passes", "to Rhineland screening Davout".
_GROUND_PURPOSE_RX = re.compile(
    r"(?:[\s,;.!]+(?:to\s+|in\s+order\s+to\s+|so\s+as\s+to\s+)?|\s+to\s+)"
    r"(?P<why>(?:form|cover|secure|guard|protect|screen|watch|anchor|shield|mask|block)\s+"
    r"(?:the|our|his|your|their|a)\s+(?:(?:northern|southern|eastern|western|left|right|open|exposed|whole)\s+)?"
    r"(?:rear|flank|flanks|line|lines|road|roads|river|crossing|crossings|pass|passes|coast|frontier|"
    r"border|approaches|reserve|reserves|retreat|position|ground|wing|centre|center))\s*[.!]*$",
    re.IGNORECASE)
_BEFORE_FOE_RX = re.compile(
    r"[\s,;]+(?:before|lest|ere)\s+(?:the\s+)?(?P<foe>[A-Za-z][\w'’-]*(?:\s+[A-Z][\w'’-]*)?)\s+"
    r"(?:can|could|may|might|has|have|gets?|slips?|escapes?|moves?|marches?|reaches?|joins?|arrives?|"
    r"is|are|does|do|comes?|makes?|finds?)\b(?P<rest>.*?)\s*[.!]*$",
    re.IGNORECASE)
_PARTICIPLE_TAIL_RX = re.compile(
    r"\s+(?P<tail>(?:covering|screening|watching|guarding|protecting|holding|securing|blocking|"
    r"masking|shielding|observing|keeping\s+an\s+eye\s+on|keeping\s+watch\s+(?:on|over))\s+"
    r"(?:the|our|his|their|an?|that|those|every)\b.+?)\s*[.!]*$",
    re.IGNORECASE)
# A statement about a FOE before the order, set off by a dash or a period:
# "Massena, John sits at Tyrol — go and get him.", "Mack must be destroyed.
# Davout, see to it." — the foe is the pronoun's hint.
_FOE_STATEMENT_VERB_RX = re.compile(
    r"\b(?:sits|is|stands|lies|waits|holds|camps|has|was|will|remains|moves|marches|"
    r"must\s+be|is\s+to\s+be|cannot|can't|shall\s+not|won't|threatens|masses|gathers)\b",
    re.IGNORECASE)
# (DD0-20, S5: ", Ney in support" — the second man without the `with`.)
_SUPPORT_SUFFIX_RX_T = (r"[\s,]+(?:with\s+)?(?:" + HONORIFIC_RX + r")?(?P<second>{names})\s+"
                        r"(?:in\s+support|supporting|in\s+reserve|backing\s+(?:him|them)\s+up|"
                        r"to\s+back\s+him\s+up|in\s+support\s+of\s+him|behind\s+him)\s*[.!]*$")
_TRAILING_VOCATIVE_RX_T = (r",\s*(?:please\s+)?(?:" + HONORIFIC_RX + r")?(?P<name>{names})\s*[.!]*$")
_LEADING_ADDRESS_RX_T = (r"^\s*(?:" + HONORIFIC_RX + r")?(?P<name>{names})\b\s*"
                         r"(?:(?P<sep>[,:;])\s*|(?P<modal>" + _MODAL_RX + r")|(?P<space>\s+))")
_AT_HIM_RX = re.compile(r"^\s*(?:go\s+(?:and\s+)?)?(?:at|get|take|finish|see\s+to|deal\s+with|destroy|crush|smash|"
                        r"beat|fight|engage|attack|hit|strike|bring\s+(?:him|them)\s+to\s+battle)"
                        r"(?:\s+(?:him|them|'em|’em|the\s+enemy|the\s+foe|it))?\s*[.!]*$",
                        re.IGNORECASE)
_SENTENCE_SPLIT_RX = re.compile(r"(?<=[.!])\s+(?=[A-Za-z])")
# S4 part 3: the separators an aside may follow — a comma or a spaced dash.
_ASIDE_SEP_RX = re.compile(r",|\s+[—–-]+\s+")

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
    second_order: Optional[str] = None     # S4 part 3: a second telegraph ("Davout: stays.") → "Davout, hold"
    notes: List[str] = field(default_factory=list)
    rows: List[Tuple[str, str, str]] = field(default_factory=list)   # (rule, before, after)
    # S4 part 3: the rosters the Reading was read against (the slot view
    # derives from them; nothing mechanical reads a Reading).
    friends: List[str] = field(default_factory=list)
    foes_roster: List[str] = field(default_factory=list)
    places_roster: List[str] = field(default_factory=list)
    nations_roster: List[str] = field(default_factory=list)

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
        elif self.second_order:
            composed = f"{composed}, then {self.second_order}"
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


# DD0-19 (S4 part 4): the generic words of a multi-word name — "New Russia",
# "East Prussia", "United Netherlands", "Armed Neutrality" — are not the name;
# "The new conscripts are green" was kept for the "new" of New Russia and
# RECRUITED (the fifth set's sixth-author reading).
_GENERIC_NAME_TOKENS = frozenset("""
new old east west north south upper lower little great united free armed the of de la le du des
saint st san santa holy grand high low royal republic kingdom empire duchy county states
""".split())


def _known_tokens(names: Iterable[str]) -> set:
    toks = set()
    for n in names or []:
        parts = re.findall(r"[a-z][a-z'’-]+", str(n).lower())
        for t in parts:
            if len(parts) > 1 and t in _GENERIC_NAME_TOKENS:
                continue
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
    # DD0-20 (S5): the title alone — "fall on the Archduke" — when ONE foe
    # of those in view bears it (the roster handed in is the visible one,
    # so "the Archduke" is John while Charles is out of sight).
    titles = {}
    for n in names:
        human = humanize_entity_name(n)
        if human and " " in human:
            titles.setdefault(human.split()[0].lower(), set()).add(n)
    for title, owners in titles.items():
        if len(owners) == 1 and len(title) >= 4 and title not in seen:
            seen.add(title)
            forms.append(title[:1].upper() + title[1:])
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
    # DD0-20 (S5): "Everybody on Mack. Soult leads." — the muster against a
    # foe is the order, not rhetoric before one (`rewrite_everybody_on`).
    if re.match(r"^\s*(?:everybody|everyone|every\s+corps|all\s+corps|every\s+man|all\s+of\s+you|the\s+whole\s+army|all)\s+"
                r"(?:on|at|against|upon|onto)\b", first, flags=re.IGNORECASE) and first_toks & _known_tokens(foes):
        return
    # DD0-19 (S4 part 4): "More men. Recruit in Orleanais." — a SHORT
    # leading exclamation before an un-addressed order (the order verb in
    # the rest) is rhetoric too; a longer sentence still needs the address.
    short = len(first_toks) <= 3 and not first_toks & _known_tokens(foes)
    if not _leading_address_match(rest, friends) and not (short and ORDER_VERB_RX.search(rest)):
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
        m = _WATCH_PRECAUTION_RX.search(text)
        if not m:
            return
        head = text[:m.start()]
        head_body = re.sub(r"^\s*(?:" + HONORIFIC_RX + r")?[A-Za-z][\w'’-]*\s*[,:]\s*", "", head)
        if not head_body.strip() or not (ORDER_VERB_RX.search(head_body)
                                         or re.search(r"\b(?:to|into|toward|towards)\s+\w", head_body)):
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


def peel_purpose_tail(r: Reading, known_names: Iterable[str]) -> None:
    """DD0-18 (c): "Shift Murat's horse to Lorraine so he can screen the
    Emperor." / "Get Murat's horse down to Bern, I want the Swiss road
    covered." — the purpose is set aside; a known name inside it keeps it
    (the purpose then names a man or a place the order may be about).
    DD0-20 (S5): "…, to form the reserve", "… at Frankfurt to cover the
    northern flank", "Massena: Piedmont. Secure the rear." — the purpose
    said as the ground to be held, after a comma, a `to` or a full stop."""
    text = r.residue()
    m = _PURPOSE_TAIL_RX.search(text)
    if not m or not text[:m.start()].strip():
        m = _GROUND_PURPOSE_RX.search(text)
        if not m or not text[:m.start()].strip():
            return
        head = text[:m.start()]
        if not (set(re.findall(r"[a-z][a-z'’-]+", head.lower())) & _known_tokens(r.places_roster)
                or re.search(r"\b(?:to|into|toward|towards|at|in)\s+\w", head)):
            return
    why = m.group("why")
    if set(re.findall(r"[a-z][a-z'’-]+", why.lower())) & _known_tokens(known_names):
        return
    before = r.text()
    if _peel_tail(r, m.group(0)):
        r._record("peel_purpose_tail", before)


def peel_before_foe_clause(r: Reading, foes: Iterable[str]) -> None:
    """DD0-20 (S5): "Davout should get himself to Swabia before Mack can
    slip away." — a `before <foe> …` clause behind a destination is the
    reason for haste, not a second order; the foe it names is context. Only
    behind a head that holds a destination, and only when the clause gives
    no order of its own ("before Mack attacks" stays the contingency
    PARSE-NEG refuses)."""
    text = r.residue()
    m = _BEFORE_FOE_RX.search(text)
    if not m or not text[:m.start()].strip():
        return
    if not foe_named_in(m.group("foe"), foes):
        return
    if ORDER_VERB_RX.search(m.group("rest") or ""):
        return
    head = text[:m.start()]
    if not re.search(r"\b(?:to|into|toward|towards|at|in|for)\s+\w", head):
        return
    before = r.text()
    if _peel_tail(r, m.group(0)):
        r._record("peel_before_foe_clause", before)


def peel_participle_tail(r: Reading, known_names: Iterable[str], places: Iterable[str]) -> None:
    """DD0-18 (c): "Davout, I want you in Brabant covering the Dutch coast."
    — a present participle after the destination is the purpose. Only when
    the head names a place of the map and the tail names no known name."""
    text = r.residue()
    m = _PARTICIPLE_TAIL_RX.search(text)
    if not m:
        return
    head = text[:m.start()]
    if not head.strip() or not (set(re.findall(r"[a-z][a-z'’-]+", head.lower())) & _known_tokens(places)):
        return
    tail = m.group("tail")
    if set(re.findall(r"[a-z][a-z'’-]+", tail.lower())) & _known_tokens(known_names):
        return
    before = r.text()
    if _peel_tail(r, m.group(0)):
        r._record("peel_participle_tail", before)


def peel_foe_statement(r: Reading, friends: Iterable[str], foes: Iterable[str]) -> None:
    """DD0-18 (c): "Massena, John sits at Tyrol — go and get him." / "Mack
    must be destroyed. Davout, see to it." — a statement about a foe, set
    off by a dash or a period, before (or after) the address and the order.
    The statement is set aside and the foe becomes the pronoun's hint, so
    `rewrite_at_him` reads "go and get him" / "see to it" as the attack."""
    text = r.residue()
    if "?" in text or r.hint_foe:
        return
    parts = re.split(r"(?<=[.!])\s+(?=[A-Za-z])|\s+[—–]+\s+|\s+-\s+", text)
    if len(parts) != 2:
        return
    for stmt, order in ((parts[0], parts[1]), (parts[1], parts[0])):
        # the statement may carry the address: "Massena, John sits at Tyrol"
        m = _leading_address_match(stmt, friends)
        body = stmt[m.end():] if (m and m.group("sep")) else stmt
        foe = foe_named_in(body, foes)
        if not foe or not _FOE_STATEMENT_VERB_RX.search(body):
            continue
        if set(re.findall(r"[a-z][a-z'’-]+", body.lower())) & _known_tokens(friends):
            continue
        # the statement's own verbs ("stands", "holds", "must be destroyed")
        # are not orders here
        stripped = _FOE_STATEMENT_VERB_RX.sub(" ", body)
        stripped = re.sub(r"\b(?:destroyed|crushed|smashed|beaten|broken|driven|taken|attacked|engaged)\b", " ", stripped)
        if ORDER_VERB_RX.search(stripped):
            continue
        # the other part must hold an order, or a pronoun order ("see to it")
        from backend.ai.dd0_rewrites import _PRONOUN_ORDER_TAIL_RX
        om = _leading_address_match(order, friends)
        order_body = order[om.end():] if (om and om.group("sep")) else order
        if not (ORDER_VERB_RX.search(order_body) or _PRONOUN_ORDER_TAIL_RX.match(order_body.strip())
                or _AT_HIM_RX.match(order_body)):
            continue
        before = r.text()
        start = r.typed.lower().find(body.strip().lower())
        if start < 0:
            continue
        end = start + len(body.strip())
        while end < len(r.typed) and r.typed[end] in " .!—–-":
            end += 1
        r.spans.append(Span("statement", start, end, r.typed[start:end]))
        r.hint_foe = foe
        r._record("peel_foe_statement", before)
        return


def peel_trailing_vocative(r: Reading, friends: Iterable[str]) -> None:
    """", Ney" at the end of a line that does not open with an address: the
    man after the comma is the addressee."""
    alt = _alt(friends)
    if not alt or r.address:
        return
    text = r.residue()
    m = re.search(_TRAILING_VOCATIVE_RX_T.format(names=alt), text, flags=re.IGNORECASE)
    if not m:
        # S4 part 3 (DD0-16): the INVERTED name with no comma — "pursue John
        # Massena", "attack Mack Ney": an order verb, a foe, then one of ours.
        m = re.search(r"\s+(?P<name>" + alt + r")\s*[.!]*$", text, flags=re.IGNORECASE)
        if not m:
            return
        head = text[:m.start()].strip()
        if (not head or not ORDER_VERB_RX.search(head) or _leading_address_match(head, friends)
                or not foe_named_in(head.split()[-1], r.foes_roster)):
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
    if "?" in r.typed:
        return
    # S4 part 3 (the fourth set): the LAST comma OR dash clause — "Lannes —
    # Rhineland, double quick", "Soult — Paris — the Emperor wants him near".
    seps = [m for m in _ASIDE_SEP_RX.finditer(text)]
    if not seps:
        return
    sep = seps[-1]
    head, tail = text[:sep.start()], text[sep.end():]
    head, tail = head.strip(), tail.strip().rstrip(" .!")
    tail = re.sub(r"^please\s+", "", tail, flags=re.IGNORECASE)
    if not head or not tail or "?" in tail:
        return
    # the head must be more than an address ("Ney, the men are rested" is a
    # statement, not an order with an aside)
    if _canonical(re.sub(r"^(?:" + HONORIFIC_RX + r")", "", head, flags=re.IGNORECASE), friends):
        return
    tail_toks = set(re.findall(r"[a-z][a-z'’-]+", tail.lower()))
    emphatic = bool(_EMPHATIC_TAIL_RX.match(tail))
    if (tail_toks & _known_tokens(known_names) or re.search(r"\d", tail)
            or _STATE_NOUN_RX.search(tail)):
        return
    # DD0-19: "we may be attacked before the others arrive" — the passive
    # about us is a statement, its participle no order of ours
    tail_for_verbs = _PASSIVE_ABOUT_US_RX.sub(" ", tail)
    if not emphatic and (ORDER_VERB_RX.search(tail_for_verbs) or _NEGATION_RX.search(tail)):
        return
    words = tail.split()
    clause = bool(_CLAUSE_SHAPE_RX.match(tail))
    adverbial = len(words) <= 5 and bool(_ADVERBIAL_OPEN_RX.match(tail))
    if not (clause or adverbial or emphatic):
        return
    before = r.text()
    if r.core_override is not None:
        r.core_override = head
        r._record("peel_comma_aside", before)
        return
    if _peel_tail(r, text[sep.start():]):
        r._record("peel_comma_aside", before)


def rewrite_at_him(r: Reading, foes: Iterable[str]) -> None:
    if not r.address:
        return
    core = r.core()
    from backend.ai.dd0_rewrites import _PRONOUN_ORDER_TAIL_RX
    m = _AT_HIM_RX.match(core)
    # "go and get him" needs its pronoun; a bare battle verb ("attack") does
    # not reach here. "see to it" / "do it" reads only behind a foe statement.
    if m and not re.search(r"\b(?:him|them|'em|’em|enemy|foe|it)\b", core, flags=re.IGNORECASE):
        return
    if not m and not (r.hint_foe and _PRONOUN_ORDER_TAIL_RX.match(core.strip())):
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
    r.friends, r.foes_roster = list(friends), list(foes)
    r.places_roster = [str(p) for p in places if p]
    r.nations_roster = [str(n) for n in nations if n]
    known = list(friends) + list(foes) + list(r.places_roster) + list(r.nations_roster)
    peel_rhetoric(r, friends, foes)
    # S4 part 4 (DD0-18): a statement about a foe before the order — "John
    # sits at Tyrol — go and get him", "Mack must be destroyed. Davout, see
    # to it." — read before the sentence peels so the foe is the hint.
    peel_foe_statement(r, friends, foes)
    # S4 part 3: "Massena, you have forty-two thousand men. Use them on
    # John." — a statement after the address, then the order; and the
    # trailing statement / the second telegraph ("Soult, to Franche-Comte.
    # The roads are dry.", "Ney: Frankfurt. Davout: stays.").
    peel_statement_after_address(r, friends, known)
    peel_trailing_statement(r, friends, known)
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
    # DD0-20 (S5): "… to Swabia before Mack can slip away" — the haste
    # clause that names the foe as context.
    peel_before_foe_clause(r, foes)
    # S4 part 4 (DD0-18): the purpose tail and the participle after the
    # destination ("so he can screen …", "I want the Swiss road covered",
    # "in Brabant covering the Dutch coast").
    peel_purpose_tail(r, known)
    peel_participle_tail(r, known, r.places_roster)
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


# ═══════════════════════════════════════════════════════════════════════════
# S4 part 3 (October 10, 2026) — THE SECOND HALF: the statement peels and
# THE SLOT VIEW. The fourth blind set's march register ("take your horse to
# Rhineland", "Murat — rhineland — go.", "ney franconia pls") bound the man
# and the place in the chain and shrugged for want of a verb; its attack
# register ("I want Ney on Mack this turn", "ney go get mack") bound the man
# and the foe the same way. The readers consume the SLOTS the Reading fills
# (the addressee, the places, the foes, the friends, what is left) instead
# of re-scanning the composed string for a keyword: an address, a place and
# nothing but the words of a march IS a march; a man, a foe and the words of
# an attack IS an attack. Rules SYSTEMS_REFERENCE.md §104.
# ═══════════════════════════════════════════════════════════════════════════

def _fold(text: str) -> str:
    """Lower-cased, accents folded one-for-one (an index into the folded
    string is an index into the original)."""
    import unicodedata
    out = []
    for ch in str(text or ""):
        if ord(ch) < 128:
            out.append(ch.lower())
            continue
        dec = unicodedata.normalize("NFKD", ch)
        base = next((c for c in dec if not unicodedata.combining(c)), ch)
        out.append(base.lower() if ord(base) < 128 else ch.lower())
    return "".join(out)


def peel_statement_after_address(r: Reading, friends: Iterable[str], known_names: Iterable[str]) -> None:
    """"Massena, you have forty-two thousand men. Use them on John." — the
    address, a statement that names nothing and orders nothing, then the
    order. The statement is set aside; the address stays."""
    text = r.residue()
    if "?" in text:
        return
    parts = _SENTENCE_SPLIT_RX.split(text)
    if len(parts) < 2:
        return
    first = parts[0]
    rest = text[len(first):].strip()
    m = _leading_address_match(first, friends)
    if not m or not m.group("sep") or not rest:
        return
    statement = first[m.end():].strip().rstrip(" .!")
    if not statement or not _CLAUSE_SHAPE_RX.match(statement):
        return
    if set(re.findall(r"[a-z][a-z'’-]+", statement.lower())) & _known_tokens(known_names):
        return
    if _NEGATION_RX.search(statement) or ORDER_VERB_RX.search(rest) is None:
        return
    before = r.text()
    start = r.typed.lower().find(statement.lower())
    if start < 0:
        return
    end = start + len(statement)
    while end < len(r.typed) and r.typed[end] in " .!":
        end += 1
    r.spans.append(Span("statement", start, end, r.typed[start:end]))
    r._record("peel_statement_after_address", before)


_SECOND_TELEGRAPH_WORDS = {
    "stays": "hold", "stay": "hold", "stays put": "hold", "stay put": "hold",
    "holds": "hold", "hold": "hold", "holds fast": "hold", "hold fast": "hold",
    "remains": "hold", "remain": "hold", "stands": "hold", "stand": "hold",
    "stands fast": "hold", "stand fast": "hold", "waits": "wait", "wait": "wait",
    "rests": "wait", "rest": "wait", "digs in": "fortify", "dig in": "fortify",
    "fortifies": "fortify", "fortify": "fortify", "scouts": "scout", "scout": "scout",
}


def peel_trailing_statement(r: Reading, friends: Iterable[str], known_names: Iterable[str]) -> None:
    """A trailing SENTENCE behind an addressed order: "Soult, to Franche-
    Comte. The roads are dry." (a statement that names nothing — set aside)
    or "Ney: Frankfurt. Davout: stays." (a second telegraph — carried on
    the relay as "Davout, hold")."""
    text = r.residue()
    if "?" in text:
        return
    parts = _SENTENCE_SPLIT_RX.split(text)
    if len(parts) < 2:
        return
    last = parts[-1].strip()
    head = text[:len(text) - len(parts[-1])].strip()
    if not head or not last or not _leading_address_match(head, friends):
        return
    alt = _alt(friends)
    m = re.match(r"^(?:" + HONORIFIC_RX + r")?(?P<name>" + alt + r")\s*[:,]?\s+(?P<words>[A-Za-z][\w'’ -]{0,30}?)\s*[.!]*$",
                 last, flags=re.IGNORECASE) if alt else None
    if m and _canonical(m.group("name"), friends):
        name = _canonical(m.group("name"), friends)
        words = m.group("words").strip()
        low = words.lower()
        if len(low.split()) > 3 or _NEGATION_RX.search(low):
            return
        before = r.text()
        if _peel_tail(r, last):
            r.second_order = f"{name}, {_SECOND_TELEGRAPH_WORDS.get(low, words)}"
            r._record("peel_second_telegraph", before)
        return
    statement = last.rstrip(" .!")
    if not _CLAUSE_SHAPE_RX.match(statement):
        return
    if (set(re.findall(r"[a-z][a-z'’-]+", statement.lower())) & _known_tokens(known_names)
            or ORDER_VERB_RX.search(statement) or _NEGATION_RX.search(statement)
            or _STATE_NOUN_RX.search(statement)):
        return
    before = r.text()
    if _peel_tail(r, last):
        r._record("peel_trailing_statement", before)


# ── the slot view ────────────────────────────────────────────────────────

@dataclass
class Slots:
    address: Optional[str]
    friends: List[str]          # other men of ours named in the core, in order
    foes: List[str]             # the foes named (roster keys), in order
    places: List[str]           # the provinces named (map keys), in order
    sources: List[str]          # the places marked as where FROM / by way of
    residue: List[str]          # every other word, lower-cased, in order
    core: str = ""
    prepositioned: List[str] = field(default_factory=list)   # the places a destination preposition led into

    def destination(self) -> Optional[str]:
        for p in self.places:
            if p not in self.sources:
                return p
        return None


_SOURCE_MARK_RX = re.compile(
    r"(?:\bfrom|\bout\s+of|\bvia|\bby\s+way\s+of|\bthrough|\bpast|\bleaving|\bclear\s+of|\baway\s+from)"
    r"\s+(?:the\s+)?$", re.IGNORECASE)
_PLACE_TO_PLACE_RX = re.compile(r"\s*,?\s*(?:then\s+)?(?:to|into|toward|towards|on\s+to)\s+(?:the\s+)?", re.IGNORECASE)


def _foe_form_map(roster: Iterable[str]) -> List[Tuple[str, str]]:
    """[(form, key)] for every form a foe may be named by, longest first."""
    names = [str(n) for n in roster if n]
    out: List[Tuple[str, str]] = []
    for form in foe_forms(names):
        for n in names:
            human = humanize_entity_name(n)
            if form.lower() in (n.lower(), human.lower(), human.split()[-1].lower()):
                out.append((form, n))
                break
    return sorted(out, key=lambda fk: len(fk[0]), reverse=True)


def _slots_of_reading(r: Reading) -> Slots:
    core = r.core()
    low = _fold(core)
    taken: List[Tuple[int, int]] = []
    places: List[str] = []
    sources: List[str] = []
    prepositioned: List[str] = []
    foes: List[str] = []
    friends: List[str] = []
    hits: List[Tuple[int, str, str]] = []   # (start, bucket, canonical)

    def _claim(form: str, canon: str, bucket: str) -> None:
        f = _fold(form)
        if not f:
            return
        # DD0-20 (S5): the possessive rides the name — "Get Murat's horse
        # moving", "assault Mack's position" — so "murat's" is Murat and
        # the 's leaves the residue with him.
        for m in re.finditer(r"(?<![\w'’-])" + re.escape(f) + r"(?:['’]s)?(?![\w'’-])", low):
            if any(m.start() < b and a < m.end() for a, b in taken):
                continue
            taken.append((m.start(), m.end()))
            hits.append((m.start(), m.end(), bucket, canon))
            if bucket == "place" and _SOURCE_MARK_RX.search(low[:m.start()]):
                sources.append(canon)
            elif bucket == "place" and _DEST_PREP_RX.search(low[:m.start()]):
                prepositioned.append(canon)

    for p in sorted(r.places_roster, key=len, reverse=True):
        _claim(p, p, "place")
        human = humanize_entity_name(p)
        if human and human.lower() != p.lower():
            _claim(human, p, "place")
    for form, key in _foe_form_map(r.foes_roster):
        _claim(form, key, "foe")
    for f in sorted(r.friends, key=len, reverse=True):
        if r.address and f.lower() == r.address.lower():
            continue
        _claim(f, f, "friend")
    ordered = sorted(hits, key=lambda h: h[0])
    # DD0-20 (S5): "Lannes: Franche-Comte to Swabia" — a place that a
    # destination preposition leads OUT of into the next place is where the
    # march starts, not where it ends.
    for (_, end_a, bucket_a, canon_a), (start_b, _, bucket_b, _) in zip(ordered, ordered[1:]):
        if (bucket_a == "place" and bucket_b == "place" and canon_a not in sources
                and _PLACE_TO_PLACE_RX.fullmatch(low[end_a:start_b])):
            sources.append(canon_a)
    for _, _, bucket, canon in ordered:
        {"place": places, "foe": foes, "friend": friends}[bucket].append(canon)
    blanked = list(low)
    for a, b in taken:
        for i in range(a, b):
            blanked[i] = " "
    residue = re.findall(r"[a-z][a-z'’-]*", "".join(blanked))
    return Slots(address=r.address, friends=friends, foes=foes, places=places,
                 sources=sources, residue=residue, core=core, prepositioned=prepositioned)


def slots_of(text: str, friends: Iterable[str], foes: Iterable[str],
             places: Iterable[str], nations: Iterable[str] = ()) -> Slots:
    """The slot view of a line: ONE reading, then the names it fills."""
    return _slots_of_reading(read(text, friends, foes, places, nations))


# The words a march may be given in, and nothing else: the prepositions,
# the articles, the corps nouns, the directions, the urgencies, the march
# verbs. A word outside this set ("is", "lost", "remember", "wait") keeps
# the line a shrug — the slot reader only ever fills a verb the chain found
# missing, never one it read. ("make" is absent on purpose: "make your way
# to Swabia" is the live parser's by IQ-9's cassette gate — the authority.)
MARCH_WORDS = frozenset("""
to into toward towards for on at in the a an go now pls plz please then and up over down back out of
west east north south double quick quickly once immediately speed all haste with by way via road roads
shortest together his your our my corps men army troops division column horse cavalry infantry guns
him them it there here i want need must should be this turn today tonight forward onward ahead home
quickest fastest route directly straight bring take shift move march get cross send push lead ride
head proceed carry swing wheel transfer redeploy relocate come hurry hasten advance drive press
walk slide shove pull draw close concentrate mass assemble converge rendezvous meet continue keep
let have off along across through from fall rest
ok okay right yes sire emperor wants wishes would like you
flank wing centre center left rear gallop await orders
interior frontier border coast front river both berthier northern southern eastern western
moving full ur boys lads link himself herself themselves
""".split())
# (DD0-20, S5: "Get Murat's horse MOVING towards Swabia", "FULL speed",
# "take UR BOYS to nassau", "take the road to Frankfurt and LINK with
# Davout", "get HIMSELF to Swabia" — a gerund, not an inflected order.)
# (S4 part 4, DD0-18: the positional colour of a march — "up to Rhineland,
# right flank", "to Nassau, then await orders" — and `gallop`, a verb no
# chain branch routes on.)
# (The INFLECTED forms — "moves", "marches", "rides", "heads", "goes" — are
# absent on purpose: "Ney moves to Lorraine" is the inflected-order rewrite's
# own road, and its lever down must shrug as it did; `Murat rides to
# Nivernais` stays the fifth set's, DD0-18.)
_DEST_PREP_RX = re.compile(r"\b(?:to|into|toward|towards|for|at|in|on|up|down|over)\s+(?:the\s+)?$", re.IGNORECASE)
# The words an attack may be given in; one of the TRIGGER words must be
# present ("Ney, Mack" alone stays a shrug; "ney go get mack" fights).
ATTACK_WORDS = frozenset("""
on at after keep go get use them him it want i we this turn no excuses the a an under with and now today
hard em up down into onto upon see to off set loose sic let have forces corps men army troops
position positions lines camp works
""".split())
ATTACK_TRIGGERS = frozenset("on onto upon at after use get go loose sic".split())


def _demonym_ok(token: str, nations: Iterable[str]) -> bool:
    t = token.lower()
    for n in nations or ():
        base = _fold(str(n))[:5]
        if len(base) >= 5 and t.startswith(base):
            return True
    return False


def march_by_slots(s: Slots) -> bool:
    """An addressee (or a man named) and a destination, in the words of a
    march and nothing else."""
    if not s.destination() or s.foes:
        return False
    if "?" in s.core:
        return False
    # "take Swabia" is the take-objective's (a capture, RS-11's own lever);
    # "take your horse TO Rhineland" is the march — the preposition decides.
    if "take" in s.residue and s.destination() not in s.prepositioned:
        return False
    return all(w in MARCH_WORDS for w in s.residue)


def attack_by_slots(s: Slots, nations: Iterable[str] = ()) -> bool:
    """A man of ours, ONE foe, a trigger word and nothing but the words of
    an attack."""
    if len(s.foes) != 1 or s.places or "?" in s.core:
        return False
    if not (set(s.residue) & ATTACK_TRIGGERS):
        return False
    return all(w in ATTACK_WORDS or _demonym_ok(w, nations) for w in s.residue)
