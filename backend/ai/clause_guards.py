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
from typing import Iterable, List, Optional, Tuple

from backend.ai.routed_order_words import ROUTED_ORDER_WORDS

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
#
# CX-R1: the addressees are named once, because the executor's addressee
# rule needs them as NAMES too — the desk is somebody the game knows, so an
# order of state addressed to Berthier is bound, not an unknown officer.
DESK_ADDRESSEES = ("berthier", "sire")
DESK_ADDRESS_RE = re.compile(
    r"^\s*(?:" + "|".join(DESK_ADDRESSEES) + r")\s*[,:]\s*", re.IGNORECASE)


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
# CR-7-5 (CQ-7): the TRAILING inversion. `attack Mack should the enemy advance`
# fought, because the arm above is clause-initial only. Mid-sentence, a
# `should` followed by a DETERMINER ("should the enemy…", "should his corps…")
# or by a marshal's name (the roster the chain hands in) is the inversion;
# followed by a verb ("you should attack") it is the plain modal and stays.
_SHOULD_TRAILING_DETERMINER_RE = re.compile(
    r"\sshould\s+(?:the|a|an|any|our|their|his|her|its|this|that|these|those|no"
    r"|enemy|hostile)\s+\w+",
    re.IGNORECASE)

# CR-7-5 — THE THIRD VERDICT. A REFUSING marker whose clause is exactly
# `<friendly marshal> arrives` (with or without the honorific, with or without
# a leading comma) is HANDED OFF to the strategic layer as the engine's one
# implemented condition, `until_marshal_arrives`, instead of refused. It is a
# CLOSED grammar over a CLOSED roster and fails closed: any other clause on
# the same marker takes the ordinary REFUSE road, `_REFUSING_CONDITION_WORDS`
# is not widened, and the two-word floor is untouched. The residue must be a
# HOLD — the chain checks that, because "when Davout arrives, attack" must
# stay refused (PARSE-NEG's own pinned row).
_HANDOFF_MARKERS = frozenset({"when", "if", "once", "as soon as"})
_HANDOFF_ARRIVAL_RE = re.compile(
    r"^\s*(?:" + HONORIFIC + r")?(?P<name>[A-Za-z][A-Za-z'’-]*)\s+arrives?\s*$",
    re.IGNORECASE)
_COMMA_RE = re.compile(r",")
# A LEADING clause: nothing before the marker but whitespace and, at most,
# the addressee ("Davout, until Ney arrives, hold Lorraine").
_LEADING_ADDRESS_RE = re.compile(
    r"\s*(?:(?:" + HONORIFIC + r")?[A-Za-z][A-Za-z'’-]*\s*,\s*)?", re.IGNORECASE)
# The comma leak (CQ-7's third member): `attack if, Bavaria is threatened`
# measured the clause as the word "if" alone, below the floor, and the noun
# after the comma was read as the province to attack. Punctuation immediately
# after a marker is skipped before the clause is measured.
_MARKER_PUNCT_RE = re.compile(r"\s*[,;:]\s*")


def _clause_word_count(text: str, start: int, end: int) -> int:
    return len(re.findall(r"[A-Za-z']+", text[start:end]))


def condition_marker_spans(text: str) -> List[Tuple[int, int]]:
    """Where the condition markers are, as ``(start, end)`` spans over the
    ORIGINAL string — the `negation_marker_spans` idiom, exposed so the
    condition grammar (`condition_grammar.unread_condition_clauses`) reads
    the ONE marker vocabulary instead of copying it."""
    if not text:
        return []
    out: List[Tuple[int, int]] = []
    pos = 0
    while pos < len(text):
        marker = _CONDITION_MARKER_RE.search(text, pos)
        if not marker:
            break
        collapsed = re.sub(r"\s+", " ", marker.group(0).lower())
        pos = marker.end()
        if collapsed == "after" and _PURSUE_AFTER_RE.search(text[:marker.start()]):
            continue
        if collapsed == "once" and _ONCE_ADVERB_RE.match(text[marker.end():]):
            continue
        out.append((marker.start(), marker.end()))
    return out


class ConditionGuardVerdict:
    """What `strip_condition_clauses_with_handoff` decided, in full."""
    __slots__ = ("text", "refuse", "handoff", "refusing_clause")

    def __init__(self, text: str, refuse: bool, handoff: Optional[dict],
                 refusing_clause: Optional[str]):
        self.text = text
        self.refuse = refuse
        self.handoff = handoff
        self.refusing_clause = refusing_clause

    def __iter__(self):
        yield self.text
        yield self.refuse
        yield self.handoff


def strip_condition_clauses_with_handoff(
        text: str, friendly_names: Iterable[str] = (),
        roster_names: Iterable[str] = ()) -> ConditionGuardVerdict:
    """Blank subordinate condition clauses, preserving character positions,
    and decide among THREE verdicts per clause:

    * REFUSE   — a real (two-word) clause on a REFUSING marker the engine
                 cannot hold ("if Mack advances …").
    * BLANK    — `until` / `while` / `before`, or an elliptical adverbial.
    * HAND-OFF — CR-7-5: `when|if|once|as soon as <friendly marshal> arrives`,
                 returned as ``handoff = {"until_marshal_arrives": Name,
                 "span": (start, end), "clause": "…"}`` for the strategic
                 layer to apply as the engine's own `until` condition. At most
                 one per sentence; any second condition marker refuses.

    ``friendly_names`` is the roster the hand-off may name (the player's own
    marshals); an empty roster means no hand-off is possible and the
    function is the pre-CR-7-5 guard plus the comma-leak and trailing-
    `should` fixes. ``roster_names`` (every marshal on the board) feeds the
    trailing-`should` inversion arm.
    """
    if not text:
        return ConditionGuardVerdict(text, False, None, None)
    friendly = {n.lower(): n for n in friendly_names if n}
    roster = sorted({n for n in roster_names if n}, key=len, reverse=True)
    chars = list(text)
    refuse = False
    applied = False
    handoff: Optional[dict] = None
    refusing_clause: Optional[str] = None
    marker_count = 0
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
        marker_count += 1

        # CR-7-5: skip punctuation glued to the marker before measuring.
        clause_start = marker.end()
        punct = _MARKER_PUNCT_RE.match(text, clause_start)
        if punct and punct.end() > clause_start:
            clause_start = punct.end()

        if collapsed == "until":
            end_match = _UNTIL_CLAUSE_END_RE.search(text, clause_start)
        else:
            end_match = _CLAUSE_END_RE.search(text, clause_start)
        clause_end = end_match.start() if end_match else len(text)

        # CR-7-5: a LEADING `until <friendly marshal> arrives,` — the one
        # `until` shape the engine's own read could never reach, because the
        # clause runs to the sentence end and took the order with it
        # ("until Ney arrives, hold Lorraine" was refused as unparseable).
        # Handed off exactly like `when …`: the clause ends at its comma,
        # names one of our own, is the sole condition, and the chain still
        # demands a HOLD residue (fails closed on "until Ney arrives, attack").
        if (collapsed == "until" and friendly and handoff is None
                and marker_count == 1
                and _LEADING_ADDRESS_RE.fullmatch(text[:marker.start()] or "")):
            comma = _COMMA_RE.search(text, clause_start)
            if comma:
                arrival = _HANDOFF_ARRIVAL_RE.match(text[clause_start:comma.start()])
                canonical = (friendly.get(arrival.group("name").lower())
                             if arrival else None)
                if canonical:
                    clause_end = comma.start()
                    handoff = {
                        "until_marshal_arrives": canonical,
                        "span": (marker.start(), clause_end),
                        "clause": text[marker.start():clause_end].strip(),
                    }

        if collapsed in _REFUSING_CONDITION_WORDS:
            arrival = (_HANDOFF_ARRIVAL_RE.match(text[clause_start:clause_end])
                       if collapsed in _HANDOFF_MARKERS and friendly else None)
            canonical = (friendly.get(arrival.group("name").lower())
                         if arrival else None)
            if canonical and handoff is None and marker_count == 1:
                handoff = {
                    "until_marshal_arrives": canonical,
                    "span": (marker.start(), clause_end),
                    "clause": text[marker.start():clause_end].strip(),
                }
            elif _clause_word_count(text, clause_start, clause_end) >= 2:
                refuse = True
                if refusing_clause is None:
                    refusing_clause = text[marker.start():clause_end].strip()

        for i in range(marker.start(), clause_end):
            chars[i] = " "
        applied = True
        pos = max(clause_end, marker.end())

    # A hand-off is only ever the SOLE condition in the sentence.
    if handoff is not None and marker_count > 1:
        refuse = True
        if refusing_clause is None:
            refusing_clause = handoff["clause"]
        handoff = None

    inversion = _SHOULD_INVERSION_RE.search(text)
    if not inversion:
        inversion = _SHOULD_TRAILING_DETERMINER_RE.search(text)
    if not inversion and roster:
        roster_re = re.compile(
            r"\sshould\s+(?:" + HONORIFIC + r")?(?:"
            + "|".join(re.escape(n) for n in roster) + r")\s+\w+",
            re.IGNORECASE)
        inversion = roster_re.search(text)
    if inversion:
        refuse = True
        end_match = _CLAUSE_END_RE.search(text, inversion.end())
        clause_end = end_match.start() if end_match else len(text)
        start = inversion.start()
        while start < len(text) and text[start] in ",;.!? ":
            start += 1
        if refusing_clause is None:
            refusing_clause = text[start:clause_end].strip()
        for i in range(start, clause_end):
            chars[i] = " "
        applied = True
        handoff = None

    return ConditionGuardVerdict(
        ("".join(chars) if applied else text), refuse, handoff, refusing_clause)


def strip_condition_clauses(text: str) -> Tuple[str, bool]:
    """Blank subordinate condition clauses, preserving character positions.

    Returns ``(effective_text, refuse)``.

    ``refuse`` is True when the utterance carries a condition the engine cannot
    honour AND that condition is a real clause — at least two words. The
    two-word floor is what keeps an elliptical adverbial ("when ready then
    retreat", pinned in the golden corpus) executing as it always has, while
    "when Davout arrives, attack" stops attacking on the turn it is typed.

    CR-7-5: the two-tuple face of `strip_condition_clauses_with_handoff`
    with NO roster — so no hand-off can fire through it, and every caller
    that never learned the third verdict keeps the two it knows.
    """
    verdict = strip_condition_clauses_with_handoff(text)
    return verdict.text, verdict.refuse


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
    # CX: `has`/`had` join the leads — "has Ney taken Vienna" asks, and no
    # English imperative can open with either. `have` is DELIBERATELY absent:
    # "have Ney attack Mack" is the causative imperative and a real order.
    r"can|could|should|is|are|was|were|do|does|did|am|may|might|has|had%s)\b"
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

# ───────────────────────────────────────────────────────────────────────────
# CX slice 1 — "A QUESTION NEVER ORDERS"
# ───────────────────────────────────────────────────────────────────────────
# The auxiliary requirement above is what a WH-lead needed to count as a
# question without a "?" — and it left two holes that EXECUTED. Measured on
# the 1805 boot board through `POST /command`:
#
#   "why not attack Mack"  → AP 4→3 and a REAL BATTLE. Six French corps bled
#                            (Ney −946, Davout −1,025, Soult −1,980, Lannes
#                            −709, Murat −867, and the Emperor's Guard −394).
#   "why not retreat"      → a GENERAL RETREAT of the whole army: all eight
#                            marshals fell back, Massena losing 2,100 men to
#                            movement attrition.
#   "who holds Swabia"     → "Which marshal shall hold Swabia, Sire?" — the
#                            question desk's OWN advertised kind, shadowed by
#                            the HOLD verb and one answer from an order.
#
# Neither sentence carries an auxiliary, so `is_question` returned False and
# the verb chain read the imperative inside the question. The narrow, provable
# rule: **no English imperative begins with `who`, `whom`, `whose` or `why`**,
# so those four leads are a question on their own.
#
# It is exactly four words and not "every WH-lead", because the corpus itself
# refutes the wider rule: `cr2-when-ready-then-retreat-not-split` pins
# "when ready then retreat" as a RETREAT, and "what"/"where"/"how"/"which"
# all begin real phrasings the game already accepts. Measured against all 447
# corpus entries, the four-word rule moves 0 rows.
#
# Flip lever: False restores the pre-CX lead rule byte-for-byte.
A_QUESTION_NEVER_ORDERS = True

# The four leads that cannot open an imperative.
_SUBJECT_WH_WORDS = frozenset({"who", "whom", "whose", "why"})

# "where's Ney" is "where is Ney" with the auxiliary contracted onto the lead,
# so the auxiliary scan could never see it: measured, `where is Ney` answered
# from the desk while `where's Ney` fell through to Berthier's shrug.
_CONTRACTED_AUX_RE = re.compile(r"^\s*['’]s\b", re.IGNORECASE)

# THE DELIBERATIVE OPENERS. A 373-case sweep of (question lead x order verb)
# through `POST /command` on a fresh 1805 board found thirteen more that
# EXECUTED, and they are three phrasings, not thirteen:
#
#   "what about attack Mack"          → a real battle, AP 4→3, seven corps moved
#   "how about retreat"               → a GENERAL RETREAT of the whole army
#   "is it time to build a depot in Paris" → 300 gold and an admin AP spent
#
# Each carries a WH or `is` lead whose extra-signal test fails: "about" is not
# an auxiliary, and "it" is not a first person. They are the way a person MUSES
# — the single most natural thing to type at a war table — and every one of
# them committed the deed.
_DELIBERATIVE_OPENER_RE = re.compile(
    r"^(?:what|how)\s+about\b"
    r"|^is\s+it\s+(?:time|wise|worth|right|prudent|safe|sensible|best)\b"
    r"|^(?:what|how)\s+say\b",
    re.IGNORECASE)

# THE SUBJECT DECIDES — the rule FA slice 7's review round already wrote for
# will/would/shall, extended to the rest of the modal leads.
#
# The modal leads require a "?" or a first person because "can you attack
# Mack" is a polite ORDER. But `can NEY attack Mack` names a THIRD PARTY, and
# nobody orders Ney by asking whether Ney can. Measured on the 1805 boot, all
# four fought a real battle and spent an action point:
#
#     can Ney attack Mack · may Ney attack Mack
#     does Ney attack Mack · is Ney attacking Mack
#
# The lead cannot tell them apart from "can you attack Mack" on its own — only
# the SUBJECT can — so `is_question` takes an optional roster and asks whether
# the word after the lead names somebody other than the person addressed.
# Omitted (the default, and every caller outside the parse chain) the arm is
# dormant and the function is byte-identical to before.
_SUBJECT_AFTER_LEAD_RE = re.compile(
    r"\s*(?:the\s+)?(?:" + HONORIFIC + r")?(?P<subj>[A-Za-z][\w'’-]*)",
    re.IGNORECASE)
# Third-person SUBJECT pronouns need no roster: "is he attacking", "do they
# hold".
#
# ⚠ THE OBJECT PRONOUNS ARE DELIBERATELY ABSENT, and the first draft had them.
# `it`, `him`, `her` and `them` follow an imperative as its OBJECT far more
# often than they follow a modal as its subject — measured, including `it`
# turned **`do it`** and **`Ney, do it`** into questions, which is a plain
# affirmative and a plain order. The whole suite was green about it, because
# nothing pinned either. `is it done` and `does it matter` are unaffected:
# `is` and `does` have no imperative form at all and are questions by arm (c)
# whatever follows. The case this loses is `can it be done` without a question
# mark, which shrugs either way.
_THIRD_PERSON_SUBJECTS = frozenset({"he", "she", "they"})

# ⚠ The subject rule is only NEEDED where the lead has an imperative form.
# `can/could/may/might/will/would/shall/do/should` all do — "can you attack
# Mack" is a polite order, "do attack Mack" an emphatic one — so for those the
# subject decides. The copular and perfect leads have NO imperative form in
# English at all: there is no order that begins "is …", "was …", "does …" or
# "had …". Those are a question whatever follows, and that is what closes the
# case the fast parser was measured executing at confidence 0.90 with a
# PROVINCE as its subject, which no roster of commanders could have reached:
#
#     "is Swabia defended"  → a whole-army DEFEND, 1 AP spent.
_NEVER_IMPERATIVE_LEADS = frozenset({
    "is", "are", "was", "were", "am", "does", "did", "has", "had"})

# A BARE ORDER THAT ASKS. `retreat?` ordered a GENERAL RETREAT of all eight
# corps and `attack?` armed the bare-attack clarification — neither carries an
# interrogative lead, so the lead rule above can never see them. An order
# addressed to a marshal keeps its question mark by design ("Ney, attack
# Mack?" is a hesitant order, and the docstring has said so since FA slice 7);
# an UNADDRESSED line that ends in a question mark is a question.
#
# `end turn?` is NOT in this family: `is_bare_end_turn` strips trailing "?" on
# purpose (FA-R4), because the old behaviour — where a question mark saved you
# from an accidental turn advance and its absence did not — was itself the
# defect that rule was written to kill. It is left exactly as it is.
# ─────────────────────────────────────────────────────────────────────
# CX-7 — THE NAME LOOKS LIKE A NAME
# ─────────────────────────────────────────────────────────────────────
# CX slice 1 decided whether a comma-less leading run was somebody's name
# by asking whether it was NOT grammar, against a hand-written blocklist.
# English has more adverbs than that list will ever hold, and the review
# round measured the cost on a 261-cell grid (9 marshal-less doors × 29
# natural leading runs): 256 ordinary orders newly refused as unknown
# officers — `quickly attack Mack`, `cavalry attack Mack`, `ok retreat`,
# `tonight retreat` — and the sharpest family of all, the indefinite
# pronouns (`someone attack Mack`, `whoever is closest attack Mack`),
# which are the plain English for the very thing `auto_assign_attack`
# exists to do, and whose own clarification asks "Which marshal shall
# lead the attack, Sire?".
#
# The root is the DIRECTION of the question. Asked as "is this run NOT a
# name?" the rule fails OPEN into a refusal on everything unlisted; asked
# as "does this run LOOK LIKE a name?" it fails CLOSED, and its residue is
# the pre-CX reading — which is what the player had the day before.
# This is IQ-7's own review-round lesson arriving one row later — *a rule
# built by stripping what you recognise is only as safe as the list it
# strips* — and the answer is the same one: write the allowlist out.
#
# A run is an address when, after the article and the HONORIFIC come off,
# it is one to three tokens, none of them a word that cannot be a name,
# and EITHER
#   * a token is capitalised as the player typed it (`Nay`, `Zorglub`), or
#   * a token is within one keystroke of a name on the roster handed in
#     (`nay` → Ney), so an all-lowercase typist still gets the guard on a
#     real near-miss.
#
# The words that cannot be a name are CLOSED classes, not a sample: the
# collectives and grammar CX-1's blocklist already held, the indefinite
# pronouns, assent, time — plus the one PRODUCTIVE class, the `-ly`
# adverb, closed by morphology instead of by enumeration. No marshal on
# any roster in this game ends in `-ly`.
#
# Honest residue, measured and accepted: an all-lowercase INVENTED name
# (`zorglub attack mack`) is no longer claimed, so it reaches the
# marshal-less arm exactly as it did before row CX. That is the pre-row
# behaviour, not a new loss, and the near-miss that matters (`nay`) is
# still caught at any case by the keystroke arm.
#
# Flip lever: False restores CX-1's blocklist rule byte-for-byte.
THE_ADDRESS_LOOKS_LIKE_A_NAME = True

# TWO lists, because the comma means something. A player who writes a comma
# has MARKED a run as an address — "the reserve, attack Mack" — and FA-22's
# whole point is that the game must then answer for that run rather than send
# somebody else. A player who writes no comma has marked nothing, so the run
# is claimed only if it LOOKS like a name. Which is why these two differ:
#
#   _COLLECTIVE   stands down on BOTH arms. These address the army as a whole
#                 or ask for whoever is nearest, and the game HAS a right
#                 answer for them — the marshal-less arm exists for exactly
#                 this — so refusing them is strictly worse than serving them.
#                 (CX-7 correction: the collective test used to live inside
#                 the comma-LESS branch, so "all marshals attack" fell through
#                 and "all marshals, attack" — the same address, one keystroke
#                 over — was refused as an officer of that name.)
#
#   _NOT_A_NAME   stands down on the BARE arm only. Grammar, assent, time and
#                 the -ly adverb are not names, but they are not addresses
#                 the game can serve either; with a comma in front of them the
#                 player has still named something, and FA-22's refusal is the
#                 honest answer.
#
# Arms of service — "cavalry attack Mack", "the reserve, attack Mack" — are
# deliberately in NEITHER. Bare and lowercase they are not name-shaped, so
# they fall through; marked with a comma they are claimed and refused, which
# is FA-22's own ruling and the right one: auto-assigning an infantry marshal
# to an order addressed to the cavalry is worse than asking whom.
_COLLECTIVE = frozenset((
    "all every everyone everybody each both any army armies corps troops "
    "marshals generals commanders men soldiers forces everything "
    # the indefinite pronouns — "someone attack Mack" IS the auto-assign, and
    # the game's own clarification answers it with "Which marshal shall lead
    # the attack, Sire?"
    "someone somebody anyone anybody whoever whomever nobody noone none"
).split())

# Not a name, by class — the BARE arm's guard. Every group is CLOSED in
# English, which is the whole difference between this list and the one it
# replaces. It is cheap insurance for the player who capitalises the first
# word of a sentence; lowercase runs fail the name test on their own.
# Never an address, comma or no comma. None of these can head a NOUN PHRASE
# in English, so a comma after one is ordinary punctuation and not a mark of
# address: "Well, attack Mack" and "Ok, retreat" are a player clearing his
# throat, and nobody commands an officer called Well. (Found by driving the
# capitalised forms — the first cut applied this list to the bare arm only
# and refused "Well, attack Mack" as an unknown officer.)
_NEVER_AN_ADDRESS = frozenset((
    # the polite imperative ("can you attack"), the emphatic one ("do
    # attack"), and the pronouns that go with them
    "can could may might will would shall should must do does did done "
    "let lets please kindly you your we our us i my me "
    # assent, hesitation, emphasis
    "ok okay yes yeah yep no nope alright right well sure fine very "
    "quick hurry urgent finally "
    # time and sequence
    "now then today tonight tomorrow morning evening soon later first "
    "next also just still again immediate once"
).split()) | _COLLECTIVE

# ... and the BARE arm's list adds what may legitimately appear INSIDE an
# addressed noun phrase — "Prince of Moskowa", "the Bravest of the Brave" —
# so these disqualify a run only when nothing marked it as an address.
_NOT_A_NAME = _NEVER_AN_ADDRESS | frozenset((
    "he she they them his her their it its and but so if when while "
    "the a an of to for"
).split())

# The one PRODUCTIVE class, closed by morphology rather than by listing:
# `quickly`, `urgently`, `promptly`, `instantly`, `swiftly`, `hastily`.
_ADVERB_LY_RE = re.compile(r"^\w{3,}ly$", re.IGNORECASE)
_LEADING_ARTICLE_RE = re.compile(r"^(?:the|a|an)\s+", re.IGNORECASE)
# Composed from HONORIFIC, never copied (FA slice 7's census), with the
# trailing space made optional so a BARE title — "Marshal attack Mack",
# "the Marshal" — is stripped to nothing and names nobody, while an epithet
# that ENDS in a title ("the Iron Marshal") keeps it and stays a name.
# Getting this wrong sent Soult in for Davout: FA-22's pin.
_HONORIFIC_ONLY_RE = re.compile(
    r"^(?:" + HONORIFIC.replace(r"\s+", r"(?:\s+|$)") + r")+",
    re.IGNORECASE)
_NAME_TOKEN_RE = re.compile(r"[A-Za-z\u00c0-\u00ff'\u2019-]+")


def _strip_titles(run: str) -> str:
    """The article first, then the honorific — in that order, or "the
    Marshal" keeps a title the bare "Marshal" loses."""
    phrase = (run or "").strip().strip("'\"").strip()
    phrase = _LEADING_ARTICLE_RE.sub("", phrase).strip()
    return _HONORIFIC_ONLY_RE.sub("", phrase).strip()


def addresses_the_army(run: str) -> bool:
    """The army as a whole, or whoever is nearest — served, never refused."""
    tokens = _NAME_TOKEN_RE.findall(_strip_titles(run))
    return any(tok.lower() in _COLLECTIVE for tok in tokens)


def never_an_address(run: str) -> bool:
    """A run no comma can turn into somebody's name."""
    tokens = _NAME_TOKEN_RE.findall(_strip_titles(run))
    if not tokens:
        return True
    return any(tok.lower() in _NEVER_AN_ADDRESS or _ADVERB_LY_RE.match(tok)
               for tok in tokens)


def looks_like_an_address(run: str,
                          roster: Optional[Iterable[str]] = None) -> bool:
    """True when `run` is plausibly the name of somebody being addressed.

    Fails CLOSED: anything it cannot positively recognise as a name is not
    an address, and the sentence keeps whatever reading it already had.
    `roster` is any collection of known names — marshals, commanders — and
    is consulted only for the one-keystroke arm, so the predicate is pure
    and works with nothing handed in at all.
    """
    phrase = _strip_titles(run)
    if not phrase or len(phrase) > 40:
        return False
    tokens = _NAME_TOKEN_RE.findall(phrase)
    if THE_ADDRESS_IS_ITS_HEAD:
        # CX-R1: a connective INSIDE a name is part of the name, not grammar
        # around it — "Prince of Moskowa", "Bravest of the Brave". Only
        # between two other tokens: a run that opens or closes on "of" is
        # not a name.
        tokens = [tok for i, tok in enumerate(tokens)
                  if not (0 < i < len(tokens) - 1
                          and tok.lower() in _NAME_CONNECTIVES)]
    if not tokens or len(tokens) > 3:
        return False
    for tok in tokens:
        low = tok.lower()
        if low in _NOT_A_NAME or _ADVERB_LY_RE.match(tok):
            return False
    if any(tok[0].isupper() for tok in tokens):
        return True
    from backend.utils.fuzzy_matcher import osa_distance_at_most
    for name in (roster or ()):
        for part in _NAME_TOKEN_RE.findall(str(name)):
            if len(part) < 3:
                continue
            for tok in tokens:
                if osa_distance_at_most(tok.lower(), part.lower(), 1):
                    return True
    return False


# The verbs a leading run is measured AGAINST. It lived in `executor.py` as
# `_ADDRESSEE_IS_AN_ORDER_RE` and was hand-maintained there, which left two
# holes the review round measured on the shipped board: `pull back` and
# `recon` are routed by the mock parser into the marshal-less family and were
# absent from the list, so `Zorglub pull back` ran a WHOLE-ARMY RETREAT and
# `Zorglub recon Swabia` sent Soult — FA-22's own defect, still live. It is a
# sentence-SHAPE question, so it belongs here beside the other four, read by
# the executor and by is_question() alike rather than copied into each.
_ORDER_VERB_RE = re.compile(
    r"\b(?:attack|assault|engage|storm|charge|bombard|shell|retreat|withdraw"
    r"|fall\s+back|pull\s+back|fall\s+in|move|march|advance|go|proceed"
    r"|scout|reconnoitre|reconnoiter|recon|probe|observe|watch"
    r"|hold|defend|fortify|entrench|dig\s+in|drill|train|wait|stand"
    r"|halt|stop|cancel|abort|recruit|raise|levy|build|repair|garrison"
    r"|blockade|guard|secure|pursue|chase|hunt|follow"
    r"|support|reinforce|assist|help|cover|screen|declare|propose|demand"
    r"|end|status|sortie|sally|rally|regroup|form)\b",
    re.IGNORECASE,
)


# ───────────────────────────────────────────────────────────────────────────
# CX-R1 (September 22, 2026) — THE VERB SET IS DERIVED, NOT WRITTEN.
# ───────────────────────────────────────────────────────────────────────────
# The list above was widened twice and was still 27 of 40 routed verbs short
# (row L2-1), so `Zorglub crush Mack` fought a battle and `Zorglub retire`
# marched the whole army back for a name nobody has — and, one word over,
# `crush Mack, then hold your positions` was refused as an officer called
# "crush Mack" (the mirror, L2-1 §6). The words the rule measures against are
# now the words the fast parser ROUTES on, generated from its own branches by
# `tools/gen_routed_order_words.py` into `routed_order_words.py`; a census in
# `tests/test_cx_r1_the_unbound_name_spends_nothing.py` re-derives them from
# the live parser and fails on drift, so a keyword added to the chain cannot
# ship without this rule learning it.
#
# How a word matches. The chain routes most keywords by SUBSTRING (`"recon"
# in command_lower` reads "reconnoitre"), so a word of five letters or more
# matches as a word PREFIX — the router's own reach — while a short word
# ("go", "dig", "pay", "lay") matches whole, with its inflections, because
# "be" as a prefix would read Bernadotte and Berthier as orders.
#
# Flip lever: False restores the hand-written `_ORDER_VERB_RE` above
# byte-for-byte.
ORDER_WORDS_ARE_DERIVED = True


def compile_routed_order_words(words) -> "re.Pattern":
    """One regex over the routed order words (the rule above)."""
    long_words = sorted((w for w in words if len(w) >= 5),
                        key=lambda w: (-len(w), w))
    short_words = sorted((w for w in words if len(w) < 5),
                         key=lambda w: (-len(w), w))
    parts = []
    if long_words:
        parts.append(r"(?:" + "|".join(map(re.escape, long_words))
                     + r")\w*")
    if short_words:
        parts.append(r"(?:" + "|".join(map(re.escape, short_words))
                     + r")(?:s|es|ed|d|ing)?")
    return re.compile(r"\b(?:" + "|".join(parts) + r")\b", re.IGNORECASE)


_ROUTED_ORDER_VERB_RE = compile_routed_order_words(ROUTED_ORDER_WORDS)


def order_verb_re() -> "re.Pattern":
    """The verbs a leading run is measured against — derived, or (lever
    down) the hand-written list it replaced."""
    return _ROUTED_ORDER_VERB_RE if ORDER_WORDS_ARE_DERIVED else _ORDER_VERB_RE


# ───────────────────────────────────────────────────────────────────────────
# CX-R1 — AN UNMARKED ADDRESS IS THE NAME AT ITS HEAD.
# ───────────────────────────────────────────────────────────────────────────
# With no comma, the address was "every word before the first order verb",
# judged WHOLE — so one word of filler after the name made the whole run
# grammar and the name vanished: `Zorglub just attack Mack`, `Zorglub please
# attack Mack`, `Zorglub's corps attack Mack` all fought for a name nobody
# has (row L2-4), and `the Prince of Moskowa attack Mack` fought because "of"
# is a closed-class word (L2-3, the epithet half). The address is now the
# NAME the run opens with — the article and the honorific in front of it,
# then name-shaped tokens, a connective allowed only between two of them —
# and whatever follows it is filler. The run's FIRST word still decides:
# "quickly attack Mack" and "can you attack Mack" name nobody, exactly as
# CX-7 pins them. Unmarked arms of service ("cavalry attack Mack") stay
# CX-7's deliberate ruling — lowercase and not a name, they are not claimed.
#
# Flip lever: False restores the whole-run reading byte-for-byte.
THE_ADDRESS_IS_ITS_HEAD = True

_NAME_CONNECTIVES = frozenset(
    "of de du des la le von van der den di da the".split())
_TITLE_WORDS = frozenset(("marshal", "general", "gen.", "marechal",
                          "maréchal"))
_POSSESSIVE_RE = re.compile(r"['’]s$", re.IGNORECASE)


def _bare_token(word: str) -> str:
    return word.strip(".,;:!?\"()[]")


def _leading_name_run(head: str,
                      roster: Optional[Iterable[str]] = None) -> str:
    """The name an unmarked address OPENS with, or "" when it opens with
    none. Keeps the article and the honorific in front ("the Iron Marshal",
    "Marshal Zorglub") and a title that closes an epithet."""
    # Bare tokens throughout, so the refusal names "Zorglub" and not the
    # "Zorglub!" the player typed.
    words = [_bare_token(word) for word in head.split()]
    prefix: List[str] = []
    i = 0
    while i < len(words) and (
            words[i].lower() in ("the", "a", "an")
            or words[i].lower() in _TITLE_WORDS):
        prefix.append(words[i])
        i += 1
    name: List[str] = []
    while i < len(words):
        bare = words[i]
        if not bare:
            break
        if looks_like_an_address(bare, roster) or (
                name and bare.lower() in _TITLE_WORDS):
            name.append(bare)
            i += 1
            continue
        if name and bare.lower() in _NAME_CONNECTIVES:
            j = i
            while j < len(words) and words[j].lower() in _NAME_CONNECTIVES:
                j += 1
            if j < len(words) and looks_like_an_address(words[j], roster):
                name.extend(words[i:j])
                i = j
                continue
        break
    if not name:
        return ""
    return " ".join(prefix + name)


def address_of(text: str,
               roster: Optional[Iterable[str]] = None,
               *, require_separator: bool = False) -> Optional[str]:
    """The run the player ADDRESSED, comma or no comma — or None.

    One source for the two rules row CX shipped in disagreement with each
    other. CX slice 1's second half exists *because a player does not type
    the comma*, and its first half then required one before it would read a
    line as addressed — so `Ney, attack Mack?` fought and `Ney attack Mack?`
    was swallowed as a question, on 86 of 128 ordinary orders measured.
    Whatever answers one must answer the other.

    Lever-free on purpose: each caller branches on its own
    `THE_ADDRESS_LOOKS_LIKE_A_NAME` so that arm's False position reproduces
    exactly what that caller shipped, rather than a blend of the two.
    `require_separator` carries the executor's older, still-live
    `AN_ADDRESS_NEEDS_NO_COMMA` down into the shared body, so CX-1's lever
    keeps meaning what it says instead of being swallowed by CX-7's.
    """
    raw = (text or "").strip()
    if not raw:
        return None
    head, sep, _tail = raw.partition(",")
    if not sep:
        head, sep, _tail = raw.partition(":")
    verbs = order_verb_re()
    scan = raw
    if sep and THE_ADDRESS_IS_ITS_HEAD and verbs.search(head):
        # CX-R1: a comma AFTER an order closes a clause, not an address —
        # `Zorglub attack Mack, then hold` read "Zorglub attack Mack" as the
        # addressed run, found a verb in it, and let the name go. The head is
        # read as an unmarked line instead; `attack Bern, then hold your
        # positions` still opens with its order and names nobody.
        sep = ""
        scan = head
    if not sep:
        if require_separator:
            return None      # the executor's own AN_ADDRESS_NEEDS_NO_COMMA
        verb = verbs.search(scan)
        if not verb:
            return None
        head = raw[:verb.start()]
        if THE_ADDRESS_IS_ITS_HEAD:
            head = _leading_name_run(head, roster)
            if not head:
                return None  # the run opens with grammar, not a name
    phrase = head.strip().strip("'\"").strip()
    if phrase.lower().startswith(("the ", "a ", "an ")):
        # the refusal names what the player typed, minus the article —
        # "no 'Iron Marshal' in the order of battle" (FA-22's own pin)
        phrase = phrase.split(None, 1)[1].strip() if " " in phrase else phrase
    if not phrase or verbs.search(phrase):
        return None
    if never_an_address(phrase):
        return None          # a collective, an interjection, an adverb
    if not sep and not looks_like_an_address(phrase, roster):
        return None          # nothing marked it, and it is not name-shaped
    if not sep and THE_ADDRESS_IS_ITS_HEAD:
        # "Zorglub's corps attack Mack" names Zorglub
        phrase = _POSSESSIVE_RE.sub("", phrase).strip()
    return phrase


def order_after_address(text: str) -> str:
    """CX-R1: the order the player gave, with the address taken off —
    `Zorglub build ships` -> `build ships`, `Zorglub, vassalize Austria` ->
    `vassalize Austria`. What a refusal hands back so the player can give an
    order of state without the name. "" when there is nothing to hand back."""
    raw = (text or "").strip()
    verbs = order_verb_re()
    for sep in (",", ":"):
        head, found, tail = raw.partition(sep)
        if found:
            if THE_ADDRESS_IS_ITS_HEAD and verbs.search(head):
                break        # the comma closes a clause (`address_of`)
            return tail.strip()
    verb = verbs.search(raw)
    return raw[verb.start():].strip() if verb else ""


_ADDRESSED_LINE_RE = re.compile(
    r"^\s*(?:" + HONORIFIC + r")?[A-Za-z][\w'’-]*\s*[,:]", re.IGNORECASE)
# ", <at least one more word>" — the tail of an inverted conditional.
_TRAILING_CLAUSE_RE = re.compile(r",\s*\S")



# CX-7. The roster arm read ONE token after the lead, so a MULTI-WORD name
# could not reach it: measured, `can Archduke Charles attack Mack` FOUGHT —
# AP 4→3 — while `can Mack attack Ney`, one word shorter, asked. The roster
# holds the printed form ("Archduke Charles", "Prince Bagration"), so the
# names the game shows are exactly the ones the arm could not see. It reads
# the whole opening run now.
#
# ⚠ There is deliberately NO longest-first ordering here. The first draft
# sorted by length "so a name that contains another cannot be shadowed", and
# the mutation sweep showed the sort INERT: the test is `startswith` on the
# OPENING of the run and the answer is a boolean, so a shorter name matching
# first returns the same True. A guard no mutation can kill is a guard no pin
# can be about, so it is gone.
THE_SUBJECT_MAY_HAVE_TWO_NAMES = True


def _names_a_subject(rest: str, subjects) -> bool:
    """Whether the run after the lead OPENS with a name on the roster."""
    opening = rest.strip().lower()
    for name in subjects:
        low = name.strip().lower()
        if not low:
            continue
        if not THE_SUBJECT_MAY_HAVE_TWO_NAMES and " " in low:
            continue
        if opening == low or opening.startswith(low + " "):
            return True
    return False


def _line_is_addressed(text: str,
                       roster: "Optional[Iterable[str]]" = None) -> bool:
    """Arm (e)'s reader — CX-7.

    CX-1 asked `_ADDRESSED_LINE_RE`, which requires a comma or a colon, so a
    hesitant order typed the way people type (`Ney attack Mack?`) was read as
    a question and silently dropped — while `Ney, attack Mack?`, one keystroke
    away, fought. Measured on the shipped board: 86 of 128 comma-free
    addressed orders inert, 58 of them state-changing. The comma requirement
    was never stated as deliberate anywhere, and the same commit's other half
    is titled AN ADDRESS NEEDS NO COMMA.

    Flip lever False restores the comma-only reading byte-for-byte.
    """
    if not THE_ADDRESS_LOOKS_LIKE_A_NAME:
        return bool(_ADDRESSED_LINE_RE.match(text))
    return (bool(_ADDRESSED_LINE_RE.match(text))
            or address_of(text, roster) is not None)

def is_question(command_text: str,
                subjects: Optional[Iterable[str]] = None) -> bool:
    """True for "how do I attack?" — a request for guidance, not an order.

    Requires an interrogative LEAD, so an order ADDRESSED to a marshal that
    merely ends in a question mark ("Ney, attack Mack?") stays an order.
    Beyond the lead it needs one more signal — a question mark, a first-person
    subject, or (for a WH-lead only) an auxiliary verb — so that "can you
    attack Mack", a polite order typed without punctuation, still marches.

    `subjects` (CX) is the live roster — marshals and known commanders. When
    it is given, a modal lead followed by one of those names is a question
    about a third party rather than an order to the person addressed:
    "can Ney attack Mack" asks; "can you attack Mack" commands. Omitted, the
    arm is dormant.

    ⚠ The arm read ONE token after the lead until CX-7, so a MULTI-WORD
    name could not reach it and "can Archduke Charles attack Mack" FOUGHT
    (measured, AP 4→3) while "can Mack attack Ney" asked — the names the
    game PRINTS being exactly the ones it could not see. It reads the whole
    opening run now.
    """
    text = (command_text or "").strip()
    # CX: an UNADDRESSED line ending in a question mark is a question.
    # `retreat?` marched eight corps; `Ney, attack Mack?` keeps its order.
    if (A_QUESTION_NEVER_ORDERS and text.endswith("?")
            and not _line_is_addressed(text, subjects)
            and not is_bare_end_turn(text)):
        return True
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
    # CX: the four leads no imperative can open are a question on their own.
    if A_QUESTION_NEVER_ORDERS and lead_word in _SUBJECT_WH_WORDS:
        return True
    # CX: "what about …", "how about …", "is it time to …" — the deliberative
    # openers, read from the LEAD onward so an address never hides them.
    if A_QUESTION_NEVER_ORDERS and _DELIBERATIVE_OPENER_RE.match(
            text[lead.start("lead"):]):
        return True
    if text.endswith("?") or _FIRST_PERSON_RE.search(text):
        return True
    rest = text[lead.end("lead"):]
    # CX: the subject decides. A modal lead naming a THIRD PARTY asks about
    # him; only the second person is a polite imperative.
    #
    # ⚠ The arm stands down when a COMMA and a further clause follow, because
    # that is the INVERTED CONDITIONAL and not a question: "Ney, should Mack
    # advance, fortify" means "if Mack advances, fortify" and must reach the
    # condition guard's refusal, which `test_parse_negation` pins. A question
    # of this shape does not carry a trailing main clause.
    if (A_QUESTION_NEVER_ORDERS and lead_word in _NEVER_IMPERATIVE_LEADS
            and not _TRAILING_CLAUSE_RE.search(rest)):
        return True
    if (A_QUESTION_NEVER_ORDERS and lead_word not in _WH_WORDS
            and not _TRAILING_CLAUSE_RE.search(rest)):
        subj = _SUBJECT_AFTER_LEAD_RE.match(rest)
        if subj:
            word = subj.group("subj").lower()
            if word in _THIRD_PERSON_SUBJECTS:
                return True
            if subjects and _names_a_subject(rest, subjects):
                return True
    if A_QUESTION_NEVER_ORDERS and lead_word in _WH_WORDS:
        # "where's Ney" — the auxiliary is contracted onto the lead.
        if _CONTRACTED_AUX_RE.match(rest):
            return True
    return lead_word in _WH_WORDS and bool(_AUXILIARY_RE.search(rest))


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
