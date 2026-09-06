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
from typing import List, Optional, Tuple

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
    # Aug 30, 2026 review: the two most idiomatic English prohibitives carried
    # NO marker at all, because the bare-"no" arm above demands an order-NOUN
    # straight after "no" and here the noun is "circumstances"/"account".
    # Measured on the 1805 boot: "Ney, under no circumstances attack Mack"
    # marched Rhineland->Swabia and FOUGHT him at confidence 0.95 — above the
    # 0.7 gate, so the LLM was never consulted in any mode. The §PARSE-NEG
    # headline shape, recurring for the phrasings its table never sampled.
    # These are whole prepositional phrases, so they are matched in full and
    # the clause is blanked from "under"/"on"/"by"/"in" onward.
    # One arm, not six. The mutation sweep found the first draft's specific
    # phrase arms ("under no circumstances", "on no account") INERT: a general
    # `no (circumstances|account)` arm sat below them and matched the same
    # text, so deleting a specific arm changed nothing and its pin proved
    # nothing. The general form is also the correct one — the prohibitive is
    # "no <abstract noun>" whatever preposition introduces it.
    r"|no\s+(?:circumstances?|account|means|case|event|time|point)\b"
    r")\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# The end-turn vocabulary (FA-6 / FA-N22)
# ---------------------------------------------------------------------------
# The mock chain read end_turn from a bare SUBSTRING test over these three
# words, sitting ABOVE every order verb — so a sentence that merely mentioned
# one became the end-turn command itself. Measured on the shipped 1805 boot:
# `what happens next turn` advanced the turn and ran the enemy phase, and so
# did `we will decide next turn` and `Ney, hold here and attack next turn`,
# while `what should we do next turn?` held it. A non-command advanced the
# turn irreversibly, and inconsistently — a question mark saved you and the
# same sentence without one did not.
#
# The vocabulary is UNCHANGED and lives here so the backend and the client's
# `_is_end_turn_phrasing` cannot drift; what changed is that it must be the
# WHOLE command. `end the turn` is deliberately still not a phrasing — it
# shrugs today, and adding it would be a widening rather than this fix.
END_TURN_PHRASINGS = ("end turn", "end_turn", "next turn")

# FA slice 7: the chief of staff (or the sovereign's own title) addressed
# before a desk verb — "Berthier, status", "Sire, help". FA-R4 (slice 14)
# moved it DOWN here from `llm_client`, because the end-turn gate needs the
# same vocabulary and `llm_client` imports this module rather than the other
# way round. It is the whole desk-address vocabulary, in one place, for the
# backend and — mirrored, with a parity pin — for the client.
DESK_ADDRESS_RE = re.compile(r"^\s*(?:berthier|sire)\s*[,:]\s*",
                             re.IGNORECASE)


def strip_desk_address(text: str) -> str:
    """`"Berthier, end turn"` -> `"end turn"`. Idempotent on an unaddressed
    line, and it removes at most ONE address so `"Berthier, Ney, attack"`
    still reads as an order to Ney rather than to the desk."""
    return DESK_ADDRESS_RE.sub("", text or "", count=1)


def is_bare_end_turn(text: str) -> bool:
    """True only when the command IS an end-turn phrasing and nothing else.

    Trailing punctuation is allowed, and so is an address to the DESK —
    anything else (an order verb, a question) is not an end-turn command and
    falls through to the keyword chain, where the deferral guard and the
    ordinary verbs decide.

    FA-R4 (slice 14). Slice 7 taught the two exact-match desk routes to read
    past "Berthier," and deliberately did NOT teach this one, because the
    client's lapse-confirm gate mirrors this vocabulary word for word and
    widening only the backend would advance the turn behind the confirm that
    warns about unanswered envoys — the UX23 soft-lock class. Both gates are
    widened together here, so measured on the shipped board:

        "Berthier, status"      worked        "Berthier, end turn"   SHRUGGED
        "Berthier, help"        worked        "Sire, end turn"       SHRUGGED
                                              "Berthier, next turn"  SHRUGGED
                                              "Berthier: end turn"   SHRUGGED

    The last two are wider than the row filed, and fall out of the same rule.
    The PHRASING vocabulary itself is untouched: `end the turn` still shrugs,
    and adding it would be a widening rather than this fix.
    """
    stripped = (text or "").strip().lower().rstrip(".!? \t")
    stripped = strip_desk_address(stripped).strip().rstrip(".!? \t")
    return stripped.strip() in END_TURN_PHRASINGS


def negation_marker_spans(text: str) -> List[Tuple[int, int]]:
    """Where the negation markers are, as ``(start, end)`` character spans.

    FA-N2: `dialogue_routing` needs to know not merely THAT a line was
    negated but WHERE, so it can tell an answer that contains a negation
    ("Proceed Without Allies", "never mind") from a negation OF an answer
    ("never proceed without allies"). Exposing the spans keeps that one
    rule in one place; the alternative was a second copy of the marker
    vocabulary in the router, which is the drift this codebase keeps
    finding and re-fixing.

    Returns spans in left-to-right order over the ORIGINAL string, so
    callers may index into the text they passed in.
    """
    if not text:
        return []
    return [(m.start(), m.end()) for m in _NEGATION_MARKER_RE.finditer(text)]


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
# Deferral (FA-7)
# ---------------------------------------------------------------------------
# The guards above knew every way to say "not that" and no way at all to say
# "not YET" — so "Ney, delay the attack" scored `attack` at 0.95, above the
# 0.7 escalation gate, and fought a real battle on the turn it was typed.
# Measured on the shipped 1805 boot: Ney marched Rhineland -> Swabia and lost
# 1,172 men to a battle the player had explicitly postponed. `postpone`,
# `defer`, `put off`, `attack Mack later`, `attack Mack tomorrow` and
# `attack Mack for now` all did the same; the row filed five phrasings and
# nine reproduce.
#
# Two shapes, because English defers in two directions.
_DEFERRAL_VERB_RE = re.compile(
    r"\b(?:"
    r"delay(?:s|ed|ing)?"
    r"|postpone[sd]?|postponing"
    r"|defer(?:s|red|ring)?"
    r"|put\s+(?:it\s+|that\s+|them\s+)?off"
    # `hold off ON <doing something>` postpones it. Bare `hold off <foe>`
    # is the opposite — an order to REPEL him, now. Measured: without the
    # `on`, `Davout, hold off the Austrians` and `Davout, hold off Mack`
    # were refused as deferrals, and so was `Ney, hold back from Swabia`,
    # which orders him to stay clear of it THIS turn. The `on` is what
    # makes it a deferral, so the `on` is required.
    r"|hold\s+off\s+on"
    r")\b",
    re.IGNORECASE,
)
# An adverb of time defers the CLAUSE it sits in, from either end — "attack
# Mack later" and "next turn Ney attacks Mack" are the same instruction.
# NOT `for now`. FA-7's own fix_shape lists it, and it is the opposite of a
# deferral: "for now" means AT PRESENT — do it, provisionally, this turn.
# Measured with it in the list: `Ney, hold your position for now`,
# `Ney, fortify for now`, `Soult, defend Alsace for now` and
# `Murat, scout Swabia for now` were all refused, and answered with copy
# insisting Berthier keeps "no drawer for tomorrow's orders" — telling the
# player their order was about tomorrow when it was about today.
_DEFERRAL_ADVERB_RE = re.compile(
    r"\b(?:later|next\s+turn|tomorrow|next\s+time"
    r"|another\s+time|some\s+other\s+time|in\s+due\s+course|in\s+a\s+while)\b",
    re.IGNORECASE,
)
# Clause boundaries for the deferral scope. `and` counts here even though
# `_CLAUSE_END_RE` deliberately excludes it: "hold here and attack next turn"
# defers only the attack, and the hold is a real order for THIS turn. That is
# the same scoping rule negation already uses — "hold your position, do not
# attack" keeps the hold.
_DEFERRAL_CLAUSE_BOUNDARY_RE = re.compile(
    r"[,;.!?]|\s+then\s+|\s+but\s+|\s+and\s+", re.IGNORECASE)
_WORD_RE = re.compile(r"[A-Za-z']")


def strip_deferred_clauses(text: str) -> Tuple[str, bool]:
    """Blank a DEFERRED order, preserving character positions.

    Returns ``(effective_text, deferred)``.

    "Ney, delay the attack"            -> "Ney,                 "
    "Ney, attack Mack later"           -> "Ney,                  "
    "Ney, hold here and attack next turn" -> "Ney, hold here     …"

    The third shape is the point: a deferral scopes to its own clause, so a
    co-ordinate order for THIS turn survives. When nothing survives, the
    caller refuses — which is the honest answer, because the engine holds no
    order until a later turn and inventing one would hand out free actions.

    **The bare end-turn synonyms are not deferrals** (FA-N23). `next turn`
    typed alone IS the command; the adverb arm therefore fires only when the
    clause carries a word BEFORE the adverb. Without that guard this guard
    runs ~350 lines above the end_turn keyword and would refuse the most
    common command in the game.
    """
    if not text:
        return text, False
    chars = list(text)
    applied = False

    pos = 0
    while pos < len(text):
        marker = _DEFERRAL_VERB_RE.search(text, pos)
        if not marker:
            break
        # The DEFERRAL boundary, not the negation one: `and` ends a deferred
        # clause here. Negation excludes it on purpose ("don't attack and
        # hold" reads as two negated verbs at least as often as one), but a
        # deferral is not ambiguous that way, and the adverb arm below has
        # scoped on `and` since it was written. Measured with the negation
        # boundary: `Ney, delay the attack and move to Swabia` blanked the
        # MOVE as well and refused the whole sentence — the two arms of one
        # function disagreeing about their own documented rule.
        end_match = _DEFERRAL_CLAUSE_BOUNDARY_RE.search(text, marker.end())
        clause_end = end_match.start() if end_match else len(text)
        for i in range(marker.start(), clause_end):
            chars[i] = " "
        applied = True
        pos = max(clause_end, marker.end())

    for adverb in _DEFERRAL_ADVERB_RE.finditer(text):
        start = 0
        for boundary in _DEFERRAL_CLAUSE_BOUNDARY_RE.finditer(
                text, 0, adverb.start()):
            # A WORD connector belongs to the clause it introduces and must be
            # blanked with it; a punctuation separator does not and must be
            # kept. Measured: blanking after the connector left a dangling
            # "and", and the strategic target extractor read "Ney, hold here
            # and" as the province HERE AND — the phantom-province shape this
            # guard exists to prevent, re-created by the guard itself.
            start = (boundary.start()
                     if _WORD_RE.search(boundary.group(0))
                     else boundary.end())
        end_match = _DEFERRAL_CLAUSE_BOUNDARY_RE.search(text, adverb.end())
        end = end_match.start() if end_match else len(text)
        # FA-N23. A clause that is NOTHING but the adverb, and is the whole
        # command, is not a deferral — it IS the order: bare `next turn` is
        # an end-turn synonym, and this guard runs some 350 lines above the
        # arm that reads it, so a refusal here would pre-empt the most
        # common command in the game.
        outside = text[start:adverb.start()] + text[adverb.end():end]
        if not _WORD_RE.search(outside):
            continue
        for i in range(start, end):
            chars[i] = " "
        applied = True

    return ("".join(chars) if applied else text), applied


def address_governs_only_deferred_text(original: str, guarded: str,
                                       address_end: int) -> bool:
    """True when the leading addressee's OWN clause was the deferred one.

    ⛔ THE REGRESSION THIS EXISTS TO CLOSE, and it is FA-7's own headline
    defect re-created by FA-7's own fix. Measured on the shipped 1805 boot:

        "Ney, hold your position for now, Davout attack Mack"
            -> "Ney,                           , Davout attack Mack"

    `has_executable_residue` sees `attack`, so no refusal fires — and the
    leading address token is still `Ney,`, so the surviving verb, which
    names its OWN marshal, is re-addressed to HIM. NEY marched into Swabia
    and lost 1,164 men on a sentence that ordered him to STAND STILL. One
    command, no confirm modal, irreversible. Reachable with `later`,
    `tomorrow` and `delay` too, so it is not an artefact of one adverb.

    That is the same shape as the P1 the PRECEDING slice shipped — blanked
    text handed to a consumer that reads what is left as the player's
    intent — one word further along the sentence.

    The answer is not to refuse: the player gave two orders and only one is
    deferred, so Davout's attack is real and should stand. The address is
    what must go, because it governed the clause that was blanked.
    """
    if not original or address_end <= 0 or address_end > len(guarded):
        return False
    end_match = _DEFERRAL_CLAUSE_BOUNDARY_RE.search(original, address_end)
    clause_end = end_match.start() if end_match else len(original)
    if clause_end <= address_end:
        return False
    # The addressee's own clause is gone, and something else survived.
    return (not guarded[address_end:clause_end].strip()
            and bool(original[address_end:clause_end].strip())
            and bool(guarded[clause_end:].strip()))


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
# FA slice 7 (FA-N39): ONE honorific for every ADDRESS regex in the parse
# pipeline. ADDRESS_TOKEN_RE admitted `marshal` alone while parser.py's WO-1
# copy admitted `general` too — so "General Ney, attack Mack" made every
# address guard blind: measured Sept 4, 2026, a CAPTURED Ney marched out of
# Vienna on that spelling (the prisoner refusal never saw a token) and a
# FALLEN Ney's order was refused in the wrong register. Composed into each
# regex, never copied: the census in tests/test_fa_slice7_* fails on any
# surviving `(?:marshal\s+)?` literal in address position. An import-time
# constant rather than a flip lever on purpose — the ten address regexes that
# read it are compiled at import, and the parser has no series exposure (the
# ambient harness types nothing). The two CAPTURE regexes ("Marshal X" as a
# name pull) stay marshal-only by design.
HONORIFIC = r"(?:marshal|general|gen\.|mar[eé]chal)\s+"

# FA slice 7 (FA-D25's executing half): `will Ney attack Mack?` FOUGHT A
# BATTLE on the boot board (measured: gold -128, four corps to Swabia).
# `will` / `would` / `shall` join the modal leads. The "?"-or-first-person
# requirement in is_question() still keeps the polite, unpunctuated ORDER
# "would you have Ney attack Mack" an order — which was the only reason the
# three were excluded. Flip lever: False restores the shorter lead set.
MODAL_LEADS_ARE_QUESTIONS = True

_INTERROGATIVE_LEAD_SRC = (
    r"^\s*(?:so\s+|and\s+|but\s+|ok(?:ay)?\s*,?\s*|well\s*,?\s*)?"
    # A question may be addressed — "Talleyrand, what about Prussia?",
    # "Ney, can I attack?". The address is consumed so the interrogative word
    # still counts as the LEAD.
    r"(?P<addr>(?:" + HONORIFIC + r")?[A-Za-z][\w'’-]*\s*,\s*)?"
    r"(?P<lead>how|what|why|who|whom|whose|where|when|which|"
    r"can|could|should|is|are|was|were|do|does|did|am|may|might%s)\b"
)
_MODAL_LEADS = frozenset({"will", "would", "shall"})
_SECOND_PERSON_AFTER_LEAD_RE = re.compile(r"\s*you\b", re.IGNORECASE)
_INTERROGATIVE_LEAD_RE = re.compile(
    _INTERROGATIVE_LEAD_SRC % "|will|would|shall", re.IGNORECASE)
_INTERROGATIVE_LEAD_RE_LEGACY = re.compile(
    _INTERROGATIVE_LEAD_SRC % "", re.IGNORECASE)
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
    _lead_re = (_INTERROGATIVE_LEAD_RE if MODAL_LEADS_ARE_QUESTIONS
                else _INTERROGATIVE_LEAD_RE_LEGACY)
    lead = _lead_re.match(text)
    if not text or not lead:
        return False
    lead_word = lead.group("lead").lower()
    if lead_word in _MODAL_LEADS:
        # FA slice 7 review round (R1-8 / R2-9): an English sentence that
        # OPENS with will/would/shall is a question — "will Ney attack
        # Mack", "shall we march", "would Davout hold?" — with ONE
        # exception, the polite imperative to the person addressed: "would
        # you march to Lorraine for me", "will you hold the line", "would
        # you have Ney attack Mack". The subject decides, not the
        # punctuation: measured, the "?"-or-first-person rule sent "Ney,
        # would you scout Swabia?" to the COMMAND REFERENCE and let "would
        # Ney attack Mack" (no "?") fight.
        return not _SECOND_PERSON_AFTER_LEAD_RE.match(text[lead.end("lead"):])
    if text.endswith("?") or _FIRST_PERSON_RE.search(text):
        return True
    return (lead_word in _WH_WORDS
            and bool(_AUXILIARY_RE.search(text[lead.end("lead"):])))


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
