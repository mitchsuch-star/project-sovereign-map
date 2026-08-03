"""PARSE-NEG: sentence-shape guards for the deterministic fast parser.

WHY THIS MODULE EXISTS
======================
The fast parser picks an action by scanning for keywords, and its confidence
score is computed from how many identifiers it matched — never from whether
the sentence actually MEANT the keyword it found. A negated sentence contains
the *same keywords* as its affirmative, so "Ney, never attack Mack" scored
0.95 and issued the attack, while `should_use_llm` short-circuits at
`LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7` — the LLM was never consulted, in
any mode, with or without a key (`BUG_FIXES.md` §PARSE-NEG).

The fix therefore cannot live downstream of action selection: it has to change
what text action selection *sees*. Every helper here is a pure function over
the raw utterance, so the executor stays deterministic (Golden Rule 6) and
mock mode — the shipped EA default — gets the corrected behaviour without an
API key.

THE INDEX-PRESERVING BLANK
--------------------------
Clauses are removed by overwriting their characters with SPACES rather than by
splicing the string. Every position-aware rule already in the parser (the CR-2
executor-eligibility scan, the "Marshal <Name>" capture, the unresolved-address
confidence demotion) indexes into the command text, so a length-changing edit
would silently move all of them. Blanking keeps `len(effective) == len(raw)`.

WHAT EACH GUARD DOES
--------------------
`strip_negated_clauses`  — blanks "never attack Mack", "do not attack",
    "instead of attacking", "without attacking". What survives is the order
    the player actually gave: "hold your position, do not attack" keeps
    "hold your position". When nothing survives, the caller refuses rather
    than executing the affirmative.

`strip_condition_clauses` — blanks "until Davout arrives then attack" so the
    keyword inside a subordinate clause stops outranking the main verb, and
    reports whether the clause was a REAL condition the engine cannot honour
    ("if Mack advances ...") so the caller can refuse instead of executing it
    immediately.

`mentions_stand_down` — "stop attacking" / "attack no more" mean CANCEL, not
    attack. Routing them to the existing cancel action is both correct and
    kinder than a refusal.

`is_question` — "how do I attack?" is a request for help, not an assault.

None of these guards ever *choose* an action; they only decide what text the
existing keyword chain reads, and whether the caller should refuse.
"""

import re
from typing import Optional, Tuple

# ---------------------------------------------------------------------------
# Clause terminators
# ---------------------------------------------------------------------------
# A negated / conditional clause ends at sentence punctuation or at a
# contrastive connector. `and` is deliberately NOT a terminator: "don't attack
# and hold" reads as two negated verbs at least as often as one, and refusing
# an ambiguous order is the safe half of the trade.
_CLAUSE_END_RE = re.compile(r"[,;.!?]|\s+then\s+|\s+but\s+", re.IGNORECASE)

# `until` is the ONE condition the engine actually implements (StrategicCondition
# until_marshal_arrives / until_destroyed / until_relieved), so its clause runs
# to the end of the utterance exactly as strategic_parser._strip_conditions has
# always treated it. Terminating it at `then` would re-open the headline bug:
# "hold until Davout arrives then attack" would leave "attack" standing.
_UNTIL_CLAUSE_END_RE = re.compile(r"[.!?]")


# ---------------------------------------------------------------------------
# Negation
# ---------------------------------------------------------------------------
# Markers are precise phrases, never a bare "no" — `attack_vocabulary` ships
# "no quarter" as an ATTACK idiom, and a bare "not" collides with the CR-4
# "not you, Davout" rewrite that context_carryover resolves upstream.
_NEGATION_MARKER_RE = re.compile(
    r"\b(?:"
    r"never"
    r"|do(?:es)?\s*n[o']t|do(?:es)?\s+not|dont|doesnt"
    r"|did\s*n[o']t|did\s+not|didnt"
    r"|wo\s*n[o']t|will\s+not|shall\s+not|sha\s*n[o']t"
    r"|must\s*n[o']t|must\s+not"
    r"|should\s*n[o']t|should\s+not"
    r"|ca\s*n[o']t|cannot|can\s+not"
    r"|is\s*n[o']t|is\s+not|are\s*n[o']t|are\s+not"
    r"|refrain\s+from|refuse[sd]?\s+to|decline[sd]?\s+to"
    r"|rather\s+than|instead\s+of|without"
    r"|avoid(?:s|ing)?"
    r"|no\s+(?:attack|advance|assault|charge|retreat|move|movement|march"
    r"|bombardment|pursuit|offensive)\b"
    r")\b",
    re.IGNORECASE,
)


def strip_negated_clauses(text: str) -> Tuple[str, bool]:
    """Blank every negated clause, preserving character positions.

    Returns ``(effective_text, negation_applied)``.

    "Ney, hold your position, do not attack" -> "Ney, hold your position,     "
    "Ney, never attack Mack"                 -> "Ney,                        "

    The second shape leaves nothing to execute, which is the point: the caller
    refuses instead of issuing the very order the player forbade.
    """
    if not text:
        return text, False
    chars = list(text)
    applied = False
    pos = 0
    while pos < len(text):
        marker = _NEGATION_MARKER_RE.search(text, pos)
        if not marker:
            break
        end_match = _CLAUSE_END_RE.search(text, marker.end())
        clause_end = end_match.start() if end_match else len(text)
        for i in range(marker.start(), clause_end):
            chars[i] = " "
        applied = True
        pos = max(clause_end, marker.end())
    return ("".join(chars), applied) if applied else (text, False)


# ---------------------------------------------------------------------------
# Conditions
# ---------------------------------------------------------------------------
# REFUSING markers introduce a condition the engine has no way to hold open —
# executing the order NOW is the defect ("if Mack advances fall back to Alsace"
# marched immediately at confidence 0.95).
_REFUSING_CONDITION_WORDS = (
    "as soon as", "in case", "provided that", "provided",
    "if", "unless", "when", "once", "after",
)
# BLANK-ONLY markers keep their historical behaviour: the main clause's order
# stands, and only the subordinate clause is kept out of action selection.
# `until` is engine-supported; `while`/`before` describe an order that is
# correct to issue right now.
_BLANK_ONLY_CONDITION_WORDS = ("until", "while", "before")

# Longest-first so "as soon as" is not shadowed by a shorter alternative, and
# multi-word markers tolerate any run of whitespace.
_CONDITION_MARKER_RE = re.compile(
    r"\b(?:" + "|".join(
        w.replace(" ", r"\s+")
        for w in sorted(_REFUSING_CONDITION_WORDS + _BLANK_ONLY_CONDITION_WORDS,
                        key=len, reverse=True)
    ) + r")\b",
    re.IGNORECASE,
)
# "go after Blucher" is the PURSUE idiom, not a temporal condition.
_PURSUE_AFTER_RE = re.compile(r"\b(?:go(?:es|ing)?|went|came|come|run|ran|chase[sd]?)\s+$",
                              re.IGNORECASE)
# "once more" / "once again" mean "repeat", not "at the moment when".
_ONCE_ADVERB_RE = re.compile(r"^\s*(?:more|again)\b", re.IGNORECASE)
# A `should` that is not clause-initial is a plain modal in an order the player
# is giving ("Ney, you should attack Mack"), never a conditional inversion
# ("Ney, should Mack advance, fortify"). A first- or second-person subject is
# excluded too: "Talleyrand, should we declare war on Prussia?" is the player
# asking for counsel — it has always routed to the advisory desk and must keep
# doing so — while a THIRD party as the subject is the real inversion.
_SHOULD_INVERSION_RE = re.compile(
    r"(?:^|[,;.!?]\s*)should\s+(?!(?:i|we|you|us|me)\b)\w+\s+\w+",
    re.IGNORECASE)


def _clause_word_count(text: str, start: int, end: int) -> int:
    return len(re.findall(r"[A-Za-z']+", text[start:end]))


def strip_condition_clauses(text: str) -> Tuple[str, bool]:
    """Blank subordinate condition clauses, preserving character positions.

    Returns ``(effective_text, refuse)``.

    ``refuse`` is True when the utterance carries a condition the engine cannot
    honour AND that condition is a real clause — at least two words. The
    two-word floor is what keeps an elliptical adverbial ("when ready then
    retreat", pinned in the golden corpus) executing as it always has, while
    "when Davout arrives, attack" stops attacking on the turn it is typed.
    """
    if not text:
        return text, False
    chars = list(text)
    refuse = False
    applied = False
    pos = 0
    while pos < len(text):
        marker = _CONDITION_MARKER_RE.search(text, pos)
        if not marker:
            break
        word = marker.group(0).lower()
        collapsed = re.sub(r"\s+", " ", word)
        pos = marker.end()

        if collapsed == "after" and _PURSUE_AFTER_RE.search(text[:marker.start()]):
            continue
        if collapsed == "once" and _ONCE_ADVERB_RE.match(text[marker.end():]):
            continue

        if collapsed == "until":
            end_match = _UNTIL_CLAUSE_END_RE.search(text, marker.end())
        else:
            end_match = _CLAUSE_END_RE.search(text, marker.end())
        clause_end = end_match.start() if end_match else len(text)

        if (collapsed in _REFUSING_CONDITION_WORDS
                and _clause_word_count(text, marker.end(), clause_end) >= 2):
            refuse = True

        for i in range(marker.start(), clause_end):
            chars[i] = " "
        applied = True
        pos = max(clause_end, marker.end())

    inversion = _SHOULD_INVERSION_RE.search(text)
    if inversion:
        refuse = True
        end_match = _CLAUSE_END_RE.search(text, inversion.end())
        clause_end = end_match.start() if end_match else len(text)
        start = inversion.start()
        while start < len(text) and text[start] in ",;.!? ":
            start += 1
        for i in range(start, clause_end):
            chars[i] = " "
        applied = True

    return ("".join(chars) if applied else text), refuse


# ---------------------------------------------------------------------------
# Stand-down ("stop attacking" is a CANCEL, not an attack)
# ---------------------------------------------------------------------------
_ORDER_NOUNS = (
    r"attack(?:s|ing)?|advance[sd]?|advancing|assault(?:s|ing)?|charge[sd]?"
    r"|charging|march(?:es|ing)?|move[sd]?|moving|movement|pursuit|pursuing"
    r"|chase|bombard(?:ment|ing|s)?|retreat(?:s|ing)?|drill(?:s|ing)?"
    r"|siege|operations?|orders?|offensive|push|manoeuvres?|maneuvers?"
)
_STAND_DOWN_RE = re.compile(
    # "stop attacking", "call off the assault", "break off his pursuit"
    r"\b(?:stop|cease|halt|abandon|discontinue|break\s+off|call\s+off)\s+"
    r"(?:the\s+|your\s+|his\s+|her\s+|their\s+|our\s+|this\s+|that\s+)?"
    r"(?:" + _ORDER_NOUNS + r")\b"
    # "attack no more" / "no longer advance"
    r"|\b(?:" + _ORDER_NOUNS + r")\s+no\s+(?:more|longer)\b"
    r"|\bno\s+(?:more|longer)\s+(?:" + _ORDER_NOUNS + r")\b",
    re.IGNORECASE,
)


def mentions_stand_down(command_lower: str) -> bool:
    """True for "Ney, stop attacking" / "Ney, attack no more".

    Deliberately narrow: it requires an ORDER noun, so "Talleyrand, stop the
    war with Britain" (a peace proposal) and "stop Davout's pension" (a revoke)
    keep their own routes — both are pinned in the golden corpus.
    """
    return bool(_STAND_DOWN_RE.search(command_lower or ""))


# ---------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------
# `would` / `will` / `shall` are excluded on purpose: "would you have Ney
# attack Mack" is a polite ORDER and parses as one today.
_INTERROGATIVE_LEAD_RE = re.compile(
    r"^\s*(?:so\s+|and\s+|but\s+|ok(?:ay)?\s*,?\s*|well\s*,?\s*)?"
    # A question may be addressed — "Talleyrand, what about Prussia?",
    # "Ney, can I attack?". The address is consumed so the interrogative word
    # still counts as the LEAD.
    r"(?:(?:marshal\s+)?[A-Za-z][\w'’-]*\s*,\s*)?"
    r"(how|what|why|who|whom|whose|where|when|which|"
    r"can|could|should|is|are|was|were|do|does|did|am|may|might)\b",
    re.IGNORECASE,
)
_FIRST_PERSON_RE = re.compile(r"\b(?:i|we|me|us|my|our|ours)\b", re.IGNORECASE)
# A WH-word cannot begin an imperative, so "how does recruiting work" needs no
# punctuation to be a question. The modal leads (can/should/is/do…) DO begin
# imperative-ish orders in practice ("can you attack Mack"), which is why they
# require a question mark or a first-person subject.
_WH_WORDS = frozenset({"how", "what", "why", "who", "whom", "whose",
                       "where", "when", "which"})
_AUXILIARY_RE = re.compile(
    r"\b(?:do|does|did|is|are|was|were|am|can|could|should|would|will|shall"
    r"|may|might|must|have|has|had)\b", re.IGNORECASE)


def is_question(command_text: str) -> bool:
    """True for "how do I attack?" — a request for guidance, not an order.

    Requires an interrogative LEAD, so an order that merely ends in a question
    mark ("Ney, attack Mack?") stays an order. Beyond the lead it needs one
    more signal — a question mark, a first-person subject, or (for a WH-lead
    only) an auxiliary verb — so that "can you attack Mack", a polite order
    typed without punctuation, still marches.
    """
    text = (command_text or "").strip()
    lead = _INTERROGATIVE_LEAD_RE.match(text)
    if not text or not lead:
        return False
    if text.endswith("?") or _FIRST_PERSON_RE.search(text):
        return True
    return (lead.group(1).lower() in _WH_WORDS
            and bool(_AUXILIARY_RE.search(text[lead.end(1):])))


# ---------------------------------------------------------------------------
# "Did the guard leave anything to execute?"
# ---------------------------------------------------------------------------
# Words that cannot carry an order on their own. A residue of only these means
# the whole instruction lived inside the clause we just blanked.
_EMPTY_RESIDUE_WORDS = frozenset({
    "the", "and", "but", "for", "with", "your", "his", "her", "our", "their",
    "them", "they", "him", "she", "you", "sir", "sire", "please", "now",
    "then", "that", "this", "these", "those", "any", "all", "men", "troops",
    "marshal", "marshals", "general", "generals", "commander", "corps",
    "army", "not", "own", "are", "was", "were", "has", "have", "had",
    # every diplomat synonym that can route a command on its own
    "talleyrand", "diplomat", "envoy", "minister", "ambassador", "foreign",
})


def has_executable_residue(effective_text: str,
                           address_token: Optional[str] = None) -> bool:
    """True when blanked text still holds a word that could name an order.

    The address itself never counts — "Talleyrand," alone is not an
    instruction, which is why "Talleyrand, do not propose peace with Austria"
    must refuse rather than fall through to the bare-diplomat route and open
    the proposal nation-picker.
    """
    residue = (effective_text or "").lower()
    if address_token:
        residue = residue.replace(address_token.lower(), " ", 1)
    for word in re.findall(r"[a-z']{2,}", residue):
        if word not in _EMPTY_RESIDUE_WORDS:
            return True
    return False
