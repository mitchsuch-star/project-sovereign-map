"""CA9 — the single source for "does this typed line answer that dialogue?"

Three copies of the same rule shipped in three places (`main.py:2092`,
`main.py:1901`, `diplomatic_executor.py:3380`), and none of them read the
COURT the player named. Measured live: with Prussia's proposal active,
``accept Portugal's proposal`` signed a **permanent treaty with Prussia**.

The client-side guard for this exact class already shipped as W6-0's
``dialogue_id`` check (`diplomatic_executor.py:3225-3254`) — it binds a
popup answer to the dialogue that was RENDERED. The typed path, which is
this game's premise, was never given anything equivalent, because a typed
line carries no dialogue id. What it carries instead is the court's name,
in the player's own words. This module reads it.

Two public rules:

``match_dialogue_answer(dialogue, raw_lower)``
    Only a dialogue's OWN options may claim a typed line. The former
    hard-stop arm scanned a fixed keyword list for bare substrings, so
    ``send Ney to Bavaria`` answered "send" and ``garrison Paris``
    answered "garrison" on whatever hard stop happened to be staged.

``court_mismatch_refusal(world, dialogue, raw_text)``
    If the player named a court and it is not the court on the table,
    refuse and say whose matter is actually before them.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from backend.ai.clause_guards import (
    negation_marker_spans,
    strip_negated_clauses,
)

# ── The verb→action table, lifted verbatim out of
# `handle_diplomatic_dialogue_response` so the gate in main.py and the
# resolver in the executor cannot disagree about what a word means.
# Order within a list matters: it is tried in order (e.g. "accept" tries
# the AI-proposal accept before the player-proposal send).
DIALOGUE_ACTION_KEYWORDS: Dict[str, List[str]] = {
    "dismiss": ["dismiss"],
    # PC15-3: keep_joint_settlement rides LAST — it only wins on the
    # pair-substitute chooser, whose other option is confirm_pair_substitute.
    "cancel": ["cancel_pushback", "cancel_mission", "dismiss",
               "keep_joint_settlement"],
    "never mind": ["dismiss"],
    "nudge": ["accept_nudge"],
    "insist": ["insist_original"],
    "send": ["send_override", "send", "execute_proposal"],
    # PC15-3: typed "confirm" could not resolve the pair-substitute
    # chooser at all (none of its actions were in this list), so the word
    # fell through to the parser while the chooser stayed mounted — the
    # measured eight-deep confirm loop. confirm_pair_substitute rides
    # LAST: it never co-occurs with the other confirm actions.
    "confirm": ["confirm_settlement", "send_override", "execute_proposal",
                "force_declare_war", "confirm_pair_substitute"],
    "ratify": ["confirm_settlement"],
    # W6-9: execute_suggestion rides LAST in each list — it only wins on
    # the advisory dialogue, whose only other option is dismiss.
    "proceed": ["confirm_settlement", "send_override", "execute_proposal",
                "force_declare_war", "execute_suggestion",
                "confirm_pair_substitute"],
    "do it": ["execute_suggestion"],
    "yes": ["confirm_settlement", "execute_proposal", "accept_ai_proposal",
            "accept_ai_ultimatum", "force_declare_war", "execute_suggestion",
            "confirm_pair_substitute"],
    "keep": ["keep_joint_settlement"],
    "reconsider": ["back_out_settlement", "reconsider",
                   "keep_joint_settlement"],
    "no": ["back_out_settlement", "reconsider", "keep_joint_settlement"],
    "wait": ["reconsider"],
    # PT-A3: the war-purpose dialogue is RAISED with the sentence
    # "…choose our purpose, or let the province stand." That phrase was
    # offered by the engine and refused by the engine — the four
    # `_stage_war_purpose_selection` call sites speak it and the router
    # had no vocabulary for it. Shown == accepted.
    "let the province stand": ["reconsider"],
    "let it stand": ["reconsider"],
    "harsh": ["modify_harsh"],
    "generous": ["modify_generous"],
    "adjust": ["adjust_terms", "expand_options"],
    "territory": ["ultimatum_territory_yes", "territory_yes", "offer_region"],
    "enough": ["ultimatum_enough_territory", "ultimatum_done_manpower",
               "enough_territory"],
    "offer": ["offer_region", "offer_gold", "offer_ap"],
    "skip": ["ultimatum_skip_gold", "ultimatum_skip_territory",
             "ultimatum_skip_manpower", "skip_region", "skip_gold", "skip_ap"],
    "another": ["ultimatum_another_type"],
    "start over": ["ultimatum_start_over"],
    "less": ["ultimatum_less_gold", "ultimatum_less_manpower"],
    "begin": ["start_mission"],
    "start": ["start_mission"],
    "accept": ["confirm_settlement", "accept_with_conflict",
               "accept_ai_proposal", "accept_ai_ultimatum",
               "execute_proposal"],
    "agree": ["confirm_settlement", "accept_with_conflict",
              "accept_ai_proposal", "accept_ai_ultimatum",
              "execute_proposal"],
    "reject": ["reject_ai_proposal", "reject_ai_ultimatum"],
    "decline": ["reject_ai_proposal", "reject_ai_ultimatum"],
    # NA-5 §8: the ultimatum's own register — typed "yield"/"defy" resolve
    # only on the ultimatum dialogue (no other dialogue carries these).
    "yield": ["accept_ai_ultimatum"],
    "defy": ["reject_ai_ultimatum"],
    "refuse": ["reject_ai_ultimatum"],
    "counter": ["counter_ai_proposal"],
    "thank": ["dismiss"],
    "customize": ["ultimatum_customize"],
    "deliver": ["execute_ultimatum"],
    "trust": ["send_suggested"],
    "elaborate": ["elaborate", "expand_to_proposal"],
    "more": ["ultimatum_more_gold", "ultimatum_more_manpower",
             "ultimatum_another_type", "elaborate", "expand_to_proposal"],
    "review": ["review_counter"],
    "consider": ["review_counter"],
}


# ══════════════════════════════════════════════════════════════════════
# IQ-7 review R9 ([09]/[13]/[15]) — THE PETITION'S OWN VOCABULARY.
#
# The rail says "Grant it, or refuse it"; the popup's buttons read Grant /
# Refuse; and none of those words answered the petition when typed
# (`refuse` mapped only to the ultimatum, `grant` to nothing), while the
# generic `accept` / `reject` answered whichever letter was on top. These
# words resolve ONLY on a petition dialogue (`vassal.is_client_petition`)
# and ONLY when the WHOLE line, less answer filler, is the phrase — never
# by containment, so `grant it more autonomy` stays the vassal order it is
# (measured: a containment arm GRANTED the petition and ceded a province).
# `accept_ai_proposal` / `reject_ai_proposal` are every letter's actions,
# which is why this table is consulted by the DIALOGUE, not the keyword.
# ══════════════════════════════════════════════════════════════════════
PETITION_ANSWER_KEYWORDS: Dict[str, str] = {
    "grant": "accept_ai_proposal",
    "grant it": "accept_ai_proposal",
    "grant the petition": "accept_ai_proposal",
    "refuse": "reject_ai_proposal",
    "refuse it": "reject_ai_proposal",
    "refuse the petition": "reject_ai_proposal",
}
_PETITION_VERB_ACTIONS = {"grant": "accept_ai_proposal", "refuse": "reject_ai_proposal"}
_PETITION_NOUN_WORDS = frozenset({"petition", "petitions", "petition's"})

# ══════════════════════════════════════════════════════════════════════
# IQ-7 review, pass 2 (September 18, 2026) — two levers, both ROUTING.
#
# A_PETITION_IS_ANSWERED_PLAINLY (P2-1). With a CLIENT petition current,
# `grant the petition later` / `next turn` / `, but not now` / `if the
# treasury allows` / `should i grant the petition?` / `maybe grant the
# petition` all GRANTED it (1 DP, 1800g forgone), and `refuse the petition
# later` REFUSED it at the -10 / -20 price: arm 1's label containment and
# arm 3's every-label-word match fire on the very words the popup's buttons
# teach, before the whole-line arm 3b is ever asked — and the keyword arm
# did the same (`accept the petition later`, `yes, later`). True = a client
# petition is answered by a PLAIN line only (`petition_plain_answer`): every
# arm yields to the whole line, and a question never answers. False = the
# pass-1 router, byte for byte.
#
# THE_MATTER_GUARD_READS_THE_TABLE (P3-3 / P3-4 / P4-3 / P4-6). The pass-1
# matter guard read the NOUN and nothing else, so it ate the player's own
# typed ULTIMATUM ORDER, refused a bare `refuse` at the ultimatum it
# answers, claimed `refuse the offer` for a queued petition, and shrugged
# where an ally petition was on the table. True = it reads the table too.
# False = the pass-1 guard.
# ══════════════════════════════════════════════════════════════════════
A_PETITION_IS_ANSWERED_PLAINLY = True
THE_MATTER_GUARD_READS_THE_TABLE = True

# ══════════════════════════════════════════════════════════════════════
# IQ-7 review, pass 3 (September 18, 2026) — two more ROUTING levers.
#
# A_QUESTION_NEVER_ANSWERS (R3-9). Measured with Portugal's open-borders
# letter current: `should i accept?` SIGNED THE TREATY — the keyword arm
# read `accept` out of a question. True = a line that carries `?`, or that
# `clause_guards.is_question` flags, answers NO dialogue of any family (an
# exact option id, a digit and an exact option label are exempt — a label
# that happens to end in `?` must still resolve). False = the prior router.
#
# THE_BUTTON_ROUTE_READS_THE_COURT (R3-10). `POST /respond_to_diplomatic_
# dialogue` handed the handler no `raw_text`, so the court guard and the
# matter guard were bypassed there for every family: measured, the free
# text `accept Switzerland's petition` signed Portugal's letter. True = a
# choice that is FREE TEXT (not a digit, not an exact option id, not an
# exact label) is passed on as `raw_text`, so the handler seam's guards
# read it. False = the prior endpoint (no `raw_text`, ever).
# ══════════════════════════════════════════════════════════════════════
A_QUESTION_NEVER_ANSWERS = True
THE_BUTTON_ROUTE_READS_THE_COURT = True

# P4-3: the nouns of the LETTER on the table. They are answer filler to
# every other reader ("reject the offer"), but a line that names one is
# speaking of that letter — never of a petition waiting behind it.
_LETTER_NOUN_WORDS = frozenset({"offer", "terms", "proposal", "letter"})

# P2-1: once every arm yields to the whole line, an EMPHATIC yes must still
# be a yes — `grant the petition at once`, `grant it gladly`, `refuse it
# today`. None of these words defers, conditions or negates (`once Ney
# returns` carries `ney` and `returns`, which are none of these).
_PETITION_EMPHASIS_WORDS = frozenset({
    "today", "immediately", "once", "forthwith", "gladly", "willingly",
    "certainly", "indeed", "course",
})


def _petition_vocabulary_kept(raw_lower: str) -> List[str]:
    """The words left once answer filler, plain emphasis and the petition
    noun are gone. P4-3: a LETTER noun is kept — it is not the petition's."""
    words = re.findall(r"[a-z']+", str(raw_lower or "").lower())
    emphasis = (_PETITION_EMPHASIS_WORDS if A_PETITION_IS_ANSWERED_PLAINLY
                else frozenset())
    return [w for w in words
            if w not in _PETITION_NOUN_WORDS
            and w not in emphasis
            and (w not in _ANSWER_FILLER_WORDS
                 or (THE_MATTER_GUARD_READS_THE_TABLE
                     and w in _LETTER_NOUN_WORDS))]


def petition_vocabulary_answer(raw_lower: str) -> Optional[str]:
    """The action a typed line answers a PETITION with, or None.

    Whole-line only: every token that is not answer filler or the petition
    noun must be the verb itself. `grant it`, `grant the petition, sire`,
    `refuse` -> an action; `grant it more autonomy`, `grant it later`,
    `refuse Prussia's demand` -> None (an order, a deferral, another court).

    Pass 2 (P4-3): `refuse the offer` / `refuse the proposal` / `the
    letter` / `the terms` -> None. The letter nouns are filler everywhere
    else; here they say which matter the player means, and it is not the
    petition.
    """
    kept = _petition_vocabulary_kept(raw_lower)
    if len(kept) != 1:
        return None
    return _PETITION_VERB_ACTIONS.get(kept[0])


# ── P2-1: what answers a CLIENT petition — a PLAIN line, and nothing else ──
_BARE_NEGATION_WORDS = frozenset({
    "not", "never", "nor", "neither", "no", "cannot", "don't", "dont",
    "won't", "wont", "can't", "cant", "shan't", "doesn't", "didn't",
})
# `grant their petition` answers as `grant the petition` does.
_POSSESSIVE_PRONOUNS = frozenset({"their", "his", "her", "its"})

# ══════════════════════════════════════════════════════════════════════
# IQ-7 review, pass 3 — THE PLAIN ANSWER IS A CLOSED GRAMMAR, AND IT FAILS
# CLOSED.
#
# Three passes each found new phrasings that answered a client petition at
# its price, because the rule was "strip what we recognise as filler, see
# what is left" — and the general `_ANSWER_FILLER_WORDS` was never written
# for an irreversible priced answer (it holds `if`, `or`, `is`, `are`,
# `by`, `and`, `instead`, `rather`…). Measured by the second verifier:
# `grant them relief instead` typed at a PROVINCE petition CEDED TYROL;
# `if we refuse` REFUSED at −10 / −20; `is that a yes` GRANTED.
#
# So for a CLIENT petition the line is accepted only when EVERY token is in
# the allowlist below — each set LITERAL, written out word by word, never
# derived from `_ANSWER_FILLER_WORDS` by subtraction, so widening the
# general filler can never widen this. A legitimate phrasing the grammar
# does not know gets a re-prompt or Berthier: that is the design, not a
# defect. (`instead`, `rather`, `if`, `or`, `by`, `and`, `is`, `are`, `am`,
# `was`, `all`, `but`, `not` and `tribute` are deliberately NOT here.)
# ══════════════════════════════════════════════════════════════════════
# The diplomat address — `clause_guards._EMPTY_RESIDUE_WORDS`' own diplomat
# synonyms, spelled out (V2-2: `Talleyrand, grant the petition` answers, as
# it does on every other letter). A drift pin holds the two lists together.
_PLAIN_DIPLOMAT_WORDS = frozenset({
    "talleyrand", "diplomat", "envoy", "minister", "ambassador", "foreign",
})
_PLAIN_ADDRESS_WORDS = frozenset({"sire", "please"}) | _PLAIN_DIPLOMAT_WORDS
_PLAIN_PETITION_NOUNS = frozenset({
    "petition", "petitions", "petition's",
    "request", "requests", "request's",
    "plea", "pleas", "plea's",
})
# Pass 4 (R4-1a, September 18, 2026): `they` is NOT here. A line about what
# THEY do is not the Emperor's answer — measured, `do they refuse` REFUSED
# the petition at −10 / −20 and `do the swiss accept` GRANTED it.
_PLAIN_PRONOUNS = frozenset({"it", "its", "them", "their", "this"})
# The petition's OWN subject only (V2-1). `tribute` is in neither: `accept
# their tribute` must not REMIT the tribute — it claims nothing.
_PLAIN_PROVINCE_SUBJECT_WORDS = frozenset({"province"})
_PLAIN_RELIEF_SUBJECT_WORDS = frozenset({"relief", "remission"})
# Exactly what the measured positives need — `so be it, grant it`, `very
# well, grant it`, `do grant it`, `grant it, then`, `we shall grant it`,
# `grant Tyrol to the Kingdom of Italy`, `the petition from Switzerland`,
# `the petition for relief`. (`yes` is an ANSWER word, below — so `yes,
# refuse it` names two answers and claims nothing.)
_PLAIN_FUNCTION_WORDS = frozenset({
    "the", "a", "an", "to", "of", "for", "from", "we", "i", "shall", "will",
    "do", "so", "be", "very", "well", "then",
})
# Pass 4 (R4-1b, September 18, 2026) — THE AUXILIARIES ANSWER IN STATEMENT
# ORDER ONLY. `clause_guards.is_question` is anchored on the LEADING word,
# and the allowlist above holds every word a question is made of, so a
# question whose interrogative is not first answered the petition at its
# price. Measured on the turn-6 board, both routes: `then shall we grant it`
# GRANTED (1 DP, 1800g forgone), `sire do we refuse` REFUSED at −10 / −20,
# `then shall we grant tyrol` CEDED TYROL. So `shall` / `will` are read only
# directly AFTER the subject (`we shall grant it`, `i will grant it`), and
# `do` only directly after the subject (`i do accept`) or directly BEFORE an
# answer word (`do grant it`). Inverted (`shall we`, `do we`), tagged (`grant
# it, shall we`) or about a third party (`do the swiss accept`), the line
# claims nothing.
_PLAIN_SUBJECTS = frozenset({"we", "i"})
_PLAIN_MODAL_AUXILIARIES = frozenset({"shall", "will"})
_PLAIN_DO_AUXILIARY = "do"
# Emphasis is read as PHRASES, longest first: a bare `at` outside `at once`
# is not allowed (`grant it, if at all`), a bare `course` outside `of
# course` is not, and `once Ney returns` is not `at once`. (`of course` is
# the one phrase beyond the ruling's six: the second verifier's own probe
# measured `grant it, of course` answering under pass 2.)
_PLAIN_EMPHASIS_PHRASES = (
    "immediately", "of course", "at once", "for now", "gladly", "today",
    "now",
)
# Every answer word, and the ONE action it means. A word whose action this
# dialogue does not offer is not an answer word at all.
_PLAIN_GRANTS = "accept_ai_proposal"
_PLAIN_REFUSES = "reject_ai_proposal"
_PLAIN_ANSWER_WORDS: Dict[str, str] = {
    "grant": _PLAIN_GRANTS, "accept": _PLAIN_GRANTS, "agree": _PLAIN_GRANTS,
    "yes": _PLAIN_GRANTS,
    "refuse": _PLAIN_REFUSES, "reject": _PLAIN_REFUSES,
    "decline": _PLAIN_REFUSES,
}
# The petition's OWN verbs. P4-3 holds inside the grammar: beside a LETTER
# noun (`refuse the offer`) they never answer — the line names the letter —
# while every letter's generic words still do (`accept the terms`, pass 2's
# pinned positive).
_PLAIN_PETITION_VERBS = frozenset({"grant", "refuse"})
# Punctuation that separates words and carries no meaning of its own. `?`
# is not here: a question never answers.
_PLAIN_PUNCTUATION = ",.;:!—–-"


def _is_client_petition_dialogue(dialogue: Optional[dict]) -> bool:
    if not isinstance(dialogue, dict):
        return False
    from backend.game_logic.vassal import is_client_petition
    return bool(is_client_petition(dialogue))


def _petition_of_dialogue(dialogue: Optional[dict]) -> dict:
    """The stored petition terms a client-petition dialogue carries."""
    context = dialogue.get("context") if isinstance(dialogue, dict) else None
    proposal = context.get("proposal") if isinstance(context, dict) else None
    petition = proposal.get("petition") if isinstance(proposal, dict) else None
    return petition if isinstance(petition, dict) else {}


def _plain_normalised(text: str) -> str:
    """Lower-case, one apostrophe, separators to single spaces."""
    lowered = str(text or "").lower().replace("’", "'")
    for mark in _PLAIN_PUNCTUATION:
        lowered = lowered.replace(mark, " ")
    return " ".join(lowered.split())


def _petition_plain_tokens(dialogue: Optional[dict], typed: str) -> List[str]:
    """The typed line as the closed grammar reads it: the petition's OWN
    court (every name form, with its possessive), the province it asks for
    (a PROVINCE petition only) and the emphasis PHRASES are blanked; what is
    left is split into tokens, every one of which must then be in the
    allowlist. `grant Switzerland's petition`, `grant the Swiss petition`,
    `grant them Tyrol` name the matter on the table and nothing more.
    Another court's name is NOT blanked, so `grant Holland's petition` is
    not a plain answer to Switzerland's — the court guard answers it."""
    text = f" {_plain_normalised(typed)} "
    petition = _petition_of_dialogue(dialogue)
    names = []
    court = dialogue_court(dialogue)
    if court:
        names.extend(_plain_normalised(f) for f in _addressee_forms(court))
    if str(petition.get("subject") or "") == "province":
        region = _plain_normalised(str(petition.get("region") or ""))
        if region:
            names.append(region)
    for form in sorted({n for n in names if n}, key=len, reverse=True):
        text = re.sub(
            rf"(?<![a-z']){re.escape(form)}(?:'s|s'|')?(?![a-z'])", " ", text)
    for phrase in _PLAIN_EMPHASIS_PHRASES:
        text = re.sub(
            rf"(?<![a-z']){re.escape(phrase)}(?![a-z'])", " ", text)
    return text.split()


def _plain_answer_words(dialogue: Optional[dict]) -> Dict[str, str]:
    """The literal answer words whose action THIS dialogue offers."""
    offered = offered_actions(dialogue_options(dialogue))
    return {word: action for word, action in _PLAIN_ANSWER_WORDS.items()
            if action in offered}


def petition_plain_answer(dialogue: Optional[dict], typed: str) -> Optional[str]:
    """The ONE offered action a typed line PLAINLY answers a client petition
    with — or None, and then no arm of the router may claim it.

    A petition is answered at a price either way (1 DP and the tribute
    forgone or a province ceded, or −10 loyalty and −20 on the bond), so the
    line is read by a CLOSED GRAMMAR (pass 3 — the design ruling above):

      * a question never answers (`line_asks_a_question`: `?` anywhere,
        `clause_guards.is_question` — `do we grant it`, `can i accept` —
        or, pass 4, a subject-auxiliary inversion ANYWHERE in the line —
        `then shall we grant it`), and neither does a line carrying one of
        FA-N2's negation markers (`decline to reject it` is made of two
        reject-words and means the opposite);
      * pass 4 (R4-1b): an auxiliary answers in STATEMENT order only —
        `shall` / `will` directly after `we` / `i`, `do` directly after
        `we` / `i` or directly before an answer word (`we shall grant it`,
        `i do accept`, `do grant it`; never `sire do we refuse`, `grant it,
        shall we`, `do the swiss accept`);
      * EVERY token must be in the literal allowlist: the address (`sire`,
        `please`, the diplomat synonyms), the petition nouns, the
        petition's OWN court and pronouns, the petition's OWN subject (a
        province petition: `province` and the province's name; a relief
        petition: `relief`, `remission`), the closed function-word list,
        the emphasis PHRASES, the letter nouns beside a generic answer word
        only (P4-3) — or an ANSWER word;
      * there must be an answer word, and every answer word on the line
        must mean the SAME action (`refuse it and grant the petition`,
        `yes, refuse it`, `accept or reject it` claim nothing).

    So a deferral (`… later`, `next turn`, `by and by`), a condition (`if we
    refuse`, `grant it, if at all`), a hedge (`maybe …`, `is that a yes`), a
    substitution (`grant them relief instead` at a province petition), a
    negation, a correction in progress (`accept, no, reject it`) and a
    compound (`…, and invest in holland`) all carry a token the grammar does
    not know, and claim nothing — it fails CLOSED. Such a line falls to the
    ordinary road (or, when it was plainly TRYING to answer, is re-prompted
    in place — `petition_line_reprompt`), and the petition stays unanswered
    on the desk.
    """
    options = dialogue_options(dialogue)
    offered = offered_actions(options)
    text = str(typed or "").lower()
    if not text.strip() or not offered:
        return None
    # A machine token, spelled out, is never a sentence.
    for action in offered:
        if action and text.strip() == action.lower():
            return action
    # Pass 4 (R4-1c): ONE question test for the petition and every other
    # family — `line_asks_a_question`, inversion arm and all.
    if line_asks_a_question(text, options):
        return None
    # FA-N2's markers are phrases, and two of them are MADE of answer
    # words: `decline to reject it` is two reject-words and means "accept".
    if negation_marker_spans(text):
        return None
    answer_words = _plain_answer_words(dialogue)
    subject = str(_petition_of_dialogue(dialogue).get("subject") or "")
    subject_words = (_PLAIN_PROVINCE_SUBJECT_WORDS if subject == "province"
                     else _PLAIN_RELIEF_SUBJECT_WORDS if subject == "relief"
                     else frozenset())
    tokens = _petition_plain_tokens(dialogue, text)
    answers = [t for t in tokens if t in answer_words]
    if not answers:
        return None
    actions_named = {answer_words[t] for t in answers}
    if len(actions_named) != 1:
        return None
    # Pass 4 (R4-1b): the auxiliaries in STATEMENT order, or not at all.
    for index, token in enumerate(tokens):
        after_subject = index > 0 and tokens[index - 1] in _PLAIN_SUBJECTS
        if token in _PLAIN_MODAL_AUXILIARIES and not after_subject:
            return None
        if token == _PLAIN_DO_AUXILIARY and not after_subject:
            before_answer = (index + 1 < len(tokens)
                             and tokens[index + 1] in answer_words)
            if not before_answer:
                return None
    # P4-3: a LETTER noun is allowed beside every letter's generic words
    # only — `refuse the offer` names the letter, not the petition.
    letter_nouns = (frozenset() if set(answers) & _PLAIN_PETITION_VERBS
                    else _LETTER_NOUN_WORDS)
    for token in tokens:
        if token in answer_words:
            continue
        if (token in _PLAIN_ADDRESS_WORDS
                or token in _PLAIN_PETITION_NOUNS
                or token in _PLAIN_PRONOUNS
                or token in subject_words
                or token in _PLAIN_FUNCTION_WORDS
                or token in letter_nouns):
            continue
        return None
    return actions_named.pop()


def petition_reprompt_message(dialogue: Optional[dict]) -> str:
    """The ONE sentence a client petition answers a line it cannot read as a
    plain answer with — the third copy's (`POST /respond_to_diplomatic_
    dialogue`) and the `/command` router seam's (R3-2)."""
    return ("The petition takes a plain answer, Sire — nothing was relayed. "
            f"Answer with one of: {format_numbered_options(dialogue)}.")


# R4-4: the answer words as the player states them DONE (`switzerland,
# granted`) — read by the re-prompt's shape (d) only. They never ANSWER: the
# closed grammar does not hold them.
_PLAIN_ANSWER_DONE_FORMS: Dict[str, str] = {
    "granted": _PLAIN_GRANTS, "accepted": _PLAIN_GRANTS,
    "agreed": _PLAIN_GRANTS,
    "refused": _PLAIN_REFUSES, "rejected": _PLAIN_REFUSES,
    "declined": _PLAIN_REFUSES,
}
# R4-4: the bare negations a diplomat-addressed REFUSAL is made of
# (`Talleyrand, no`, `envoy, tell them no`, `minister, not today`).
_PETITION_REFUSAL_NEGATIONS = frozenset({"no", "not", "never"})


def petition_line_reprompt(dialogue: Optional[dict], typed: str,
                           marshal_names: Optional[List[str]] = None,
                           world=None) -> Optional[dict]:
    """R3-2 (V2-7, and V2-2's second half): nothing is mounted over a CURRENT
    client petition by a line that was trying to answer it.

    Measured: `accept, they have earned it` fell to the ordinary road, where
    the comma-address parser read the ANSWER WORD as a marshal and mounted a
    "Whom did you intend?" question OVER the petition; `Talleyrand, grant
    the petition later` mounted the diplomat route's nation picker over it.
    Either way the next plain `grant the petition` was refused — the player
    had to re-open Envoys to answer what he had open.

    Returns the in-place re-prompt (the third copy's own sentence, the
    petition re-attached) when the line is not a plain answer, names no
    marshal, and EITHER (b) its first word after the address is an answer
    word followed by `,` `;` `:` or a dash, OR (c) it is addressed to the
    diplomat, carries an answer word and is not a question. Everything
    else returns None and keeps the ordinary road: `grant switzerland more
    autonomy` executes, `grant the petition later` reaches Berthier's
    deferral arm, `Soult, the petition can wait, march to Swabia` marches.

    Pass 4 (R4-4, September 18, 2026) — the residue the two shapes left.
    Measured on the turn-6 board: `hmm, grant it` / `oui, grant it` /
    `switzerland, granted` mounted "There is no Marshal 'hmm'…" OVER the
    petition, and `Talleyrand, no` / `envoy, tell them no` / `minister, not
    today` mounted the diplomat route's nation picker over it — after which
    a plain `refuse` was refused, and the `2` the re-prompt teaches as
    Refuse chose BAVARIA in the picker. Two more shapes, RE-PROMPT ONLY
    (nothing here ever executes an answer):

      (d) the line leads with a comma-addressed token that is NOT a roster
          marshal (nor the diplomat — that is shape (c)) and the text after
          the first comma carries an answer word, stated or done (`granted`),
          or is itself a plain answer. It fires for a question too: measured,
          `hmm, should i grant it?` mounted the same marshal question;
      (c) widened — a diplomat-addressed line that carries a bare negation
          (`no`, `not`, `never`) and names no court other than the
          petition's is a refusal that the grammar cannot read.

    …and shape (c) is NARROWED (`world` given): a diplomat-addressed line
    that names a court OTHER than the petition's and is not answer-shaped
    is the player's own ORDER about that court (`Talleyrand, propose peace
    to Austria and accept their terms`) — it keeps the ordinary road. A
    line that names a roster marshal always did (`Ney, accept - attack
    Mack`).
    """
    from backend.ai.clause_guards import is_question
    from backend.commands.parser import _leading_addressed_token

    if not (A_PETITION_IS_ANSWERED_PLAINLY
            and _is_client_petition_dialogue(dialogue)):
        return None
    text = str(typed or "").lower().replace("’", "'").strip()
    if not text:
        return None
    asks = "?" in text or bool(is_question(text))
    if petition_plain_answer(dialogue, text) is not None:
        return None
    if addresses_a_marshal(text, marshal_names):
        return None
    answer_words = _plain_answer_words(dialogue)
    tokens = _plain_normalised(text).split()
    carries_answer = any(t in answer_words for t in tokens)
    carries_negation = any(t in _PETITION_REFUSAL_NEGATIONS for t in tokens)
    # (b) the line LEADS with an answer word and then breaks off.
    address = "|".join(sorted(_PLAIN_ADDRESS_WORDS, key=len, reverse=True))
    lead = re.match(
        rf"^(?:(?:{address})(?![a-z'])[\s,;:—–-]*)*([a-z']+)\s*[,;:—–-]", text)
    leads_with_answer = bool(lead) and lead.group(1) in answer_words
    # (c) the diplomat is the ADDRESS: he opens the line, or closes it
    # after a comma (`grant the petition later, Talleyrand`).
    diplomat_addressed = bool(tokens) and (
        tokens[0] in _PLAIN_DIPLOMAT_WORDS
        or re.search(rf",\s*(?:{'|'.join(sorted(_PLAIN_DIPLOMAT_WORDS))})"
                     r"[\s.!]*$", text) is not None)
    other_courts = [c for c in courts_addressed_in(text, world)
                    if c != dialogue_court(dialogue)]
    diplomat_shape = diplomat_addressed and (
        (carries_answer
         and not (other_courts and not _line_is_answer_shaped(text, world)))
        or (carries_negation and not other_courts))
    # (d) the line leads with a comma-addressed token that is no marshal of
    # ours (a roster name returned above) and no diplomat, and what follows
    # the comma is an answer — stated, done, or plain.
    addressed_token = str(_leading_addressed_token(text) or "").lower()
    stray_address = False
    if addressed_token and addressed_token not in _PLAIN_ADDRESS_WORDS:
        rest = text.split(",", 1)[1] if "," in text else ""
        offered = offered_actions(dialogue_options(dialogue))
        done_forms = {w for w, a in _PLAIN_ANSWER_DONE_FORMS.items()
                      if a in offered}
        rest_tokens = _plain_normalised(rest).split()
        stray_address = (
            any(t in answer_words or t in done_forms for t in rest_tokens)
            or petition_plain_answer(dialogue, rest) is not None)
    # A QUESTION keeps the ordinary road (the question desk, Talleyrand's
    # own counsel) — except in shapes (b) and (d): measured, `accept, should
    # i?` and `hmm, should i grant it?` are no questions to the ordinary
    # road either. Its comma-address parser reads the lead word as a marshal
    # and mounts the same "Whom did you intend?" over the petition.
    if asks and not (leads_with_answer or stray_address):
        return None
    if not (leads_with_answer or diplomat_shape or stray_address):
        return None
    return {
        "success": False,
        "petition_reprompt": True,
        "message": petition_reprompt_message(dialogue),
        "diplomatic_dialogue": dialogue,
        "awaiting_diplomatic_response": True,
    }


def _dialogue_is_petition_family(dialogue: Optional[dict]) -> bool:
    if not isinstance(dialogue, dict):
        return False
    if str(dialogue.get("type") or "") == "ally_settlement_petition":
        return True
    from backend.game_logic.vassal import is_client_petition
    return is_client_petition(dialogue)


def _dialogue_is_ultimatum_family(dialogue: Optional[dict]) -> bool:
    if not isinstance(dialogue, dict):
        return False
    if str(dialogue.get("type") or "") == "incoming_ultimatum":
        return True
    context = dialogue.get("context") if isinstance(dialogue.get("context"), dict) else {}
    return str(context.get("proposal_type") or "") == "ultimatum"


def _dialogue_is_settlement_family(dialogue: Optional[dict]) -> bool:
    if not isinstance(dialogue, dict):
        return False
    return str(dialogue.get("type") or "") in (
        "incoming_settlement_offer", "ally_settlement_petition",
        "settlement_confirm", "settlement_pair_substitute_confirm",
    )


# The per-FAMILY matter-noun table: the noun the player types, the
# predicate that says a dialogue IS of that family, and the word the refusal
# uses for the waiting matter.
MATTER_NOUN_FAMILIES = (
    ("petition", r"petition(?:s|'s|’s)?", _dialogue_is_petition_family, "petition"),
    ("ultimatum", r"ultimatums?", _dialogue_is_ultimatum_family, "ultimatum"),
    ("settlement", r"settlements?", _dialogue_is_settlement_family, "settlement offer"),
)


def dialogue_options(dialogue: Optional[dict]) -> List[dict]:
    """A dialogue's answerable options, with the `popup_payload` fallback
    every other reader already carries (settlement offers promoted before
    the promote-time fix keep their actions only in there)."""
    if not isinstance(dialogue, dict):
        return []
    options = dialogue.get("options") or []
    if not options and isinstance(dialogue.get("popup_payload"), dict):
        options = dialogue["popup_payload"].get("options") or []
    return list(options)


def format_answer_words(choices) -> str:
    """CA9-N5: the exact words that clear a block, quoted so the player can
    type them verbatim — ``'trust', 'insist' or 'compromise'``.

    A blocking state that does not name its own exits is the "the game
    stopped listening" moment. Six of them in the CA9 campaign, and the
    words were already in the payload every time; only the sentence
    omitted them. One helper, so shown = offered.
    """
    words = [f"'{str(c).strip()}'" for c in (choices or []) if str(c).strip()]
    if not words:
        return ""
    if len(words) == 1:
        return words[0]
    return ", ".join(words[:-1]) + " or " + words[-1]


# PT-A3: what the player is being asked, in words, so a hard stop can
# name its own blocker the way an objection names the marshal who raised
# it. Keyed on `DialogueManager.HARD_STOP_TYPES` — the only dialogues
# that can reach the refusal.
_HARD_STOP_SUBJECT = {
    "force_declare_war_confirmation": "The declaration of war",
    "force_break_treaty_confirmation": "The breaking of the treaty",
    "alliance_paradox": "The conflict between your alliances",
    "commitment_paradox": "The conflict between your commitments",
    "war_purpose_selection": "Our purpose in this war",
    "settlement_confirm": "The terms on the table",
    # PC15-3: the chooser names itself instead of silently eating commands.
    "settlement_pair_substitute_confirm":
        "The choice between the joint settlement and a separate peace",
}


def hard_stop_subject(dialogue: Optional[dict]) -> str:
    """Name the thing that is blocking, for a hard-stop refusal.

    PT-A3. A hard stop that answers "I don't understand that choice" to a
    sentence about something else has told the player neither what is
    waiting nor how to clear it. The objection block has named its blocker
    since CA9-N5; this is the same courtesy one branch over.
    """
    dtype = ""
    if isinstance(dialogue, dict):
        dtype = str(dialogue.get("type") or "")
    return _HARD_STOP_SUBJECT.get(dtype, "A decision")


def format_numbered_options(dialogue: Optional[dict]) -> str:
    """CA9-N5: ``1=Conquest, 2=Forced Alliance, 3=Back Out`` — a live
    dialogue's own option list, read off the dialogue rather than
    re-described."""
    labels = [str(o.get("label", "?")) for o in dialogue_options(dialogue)]
    return ", ".join(f"{i + 1}={label}" for i, label in enumerate(labels))


def whole_phrase_in(phrase: str, text: str) -> bool:
    """Word-boundary containment. `no` must not match "north", and
    `start` must not match "restart" — the bare-substring scan is exactly
    how ordinary orders were eaten as dialogue answers."""
    return re.search(
        r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])", text) is not None


_MACHINE_TOKEN_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)+$")


def choice_is_an_exact_token(choice, options: List[dict]) -> bool:
    """True when `choice` is one of the shapes a BUTTON sends and a sentence
    never is: a digit, an option's exact action id, an option's exact label
    — or any snake_case machine id (FA-N5's own shape: a structured
    settlement verb such as `settlement_dial_harsher` rides in `choice`
    without being an option). Everything else is free text — the player's
    own words."""
    if isinstance(choice, int):
        return True
    token = str(choice or "").strip().lower()
    if not token:
        return True
    if token.isdigit() or _MACHINE_TOKEN_RE.match(token):
        return True
    for opt in options or []:
        if not isinstance(opt, dict):
            continue
        if token == str(opt.get("action") or "").strip().lower():
            return True
        # Pass 4 (R4-2): a label is compared modulo its TERMINAL punctuation
        # — the advisory's `What should we do about Prussia?` typed without
        # its `?` is still that label. A `?` is dropped only when the LABEL
        # itself is a question: `accept?` is not the label `Accept`.
        label = str(opt.get("label") or "")
        question_label = "?" in label
        label_key = _label_key(label, question_label)
        if label_key and _label_key(token, question_label) == label_key:
            return True
    return False


_TERMINAL_PUNCTUATION_RE = re.compile(r"[\s!.]+$")
_TERMINAL_QUESTION_PUNCTUATION_RE = re.compile(r"[\s?!.,;:]+$")


def _label_key(text: str, question_label: bool) -> str:
    """A label, or a typed line compared with one, less its terminal
    punctuation and case. The `?` goes only for a QUESTION-shaped label."""
    lowered = str(text or "").strip().lower()
    pattern = (_TERMINAL_QUESTION_PUNCTUATION_RE if question_label
               else _TERMINAL_PUNCTUATION_RE)
    return pattern.sub("", lowered)


def _carries_a_question_label(typed: str, options: List[dict]) -> bool:
    """R4-2: True when the line carries EVERY word of an option label that
    is ITSELF a question — arm 3's own predicate, restricted to labels that
    contain `?`. Three shipped labels are questions (`What should we do?`,
    `What should we do about {nation}?`, `What terms would they accept?`),
    and the player types them bare, lower-case or with a lead-in (`so what
    should we do about prussia?`). A plain `Accept` label is NOT exempted,
    so `accept?` stays a question."""
    words = set(re.findall(r"[a-z]+", str(typed or "").lower()))
    for opt in options or []:
        if not isinstance(opt, dict):
            continue
        label = str(opt.get("label") or "")
        if "?" not in label:
            continue
        label_words = set(re.findall(r"[a-z]+", label.lower()))
        if label_words and label_words <= words:
            return True
    return False


# R4-3: a subject-auxiliary inversion — `shall we`, `do i`, `would we` —
# ANYWHERE in the line. `clause_guards.is_question` reads the LEADING word
# only, so `then shall we ratify` was a statement to it.
_SUBJECT_AUXILIARY_INVERSION_RE = re.compile(
    r"(?<![a-z'])(?:shall|will|would|should|can|could|may|might|must"
    r"|do|does|did)\s+(?:we|i)(?![a-z'])")


def line_asks_a_question(typed: str, options: List[dict]) -> bool:
    """R3-9: True when the typed line is a QUESTION — it carries `?`, or
    `clause_guards.is_question` flags it (`should i accept`, `do we grant
    it`). Exempt: a digit, an exact option id and an exact option label —
    a label that happens to end in `?` must still resolve.

    Pass 4 (September 18, 2026):
      * R4-2 — pass 3's exemption held for a BYTE-exact label only, so the
        advisory's own question-shaped labels stopped resolving unless typed
        with their `?` (measured: `what should we do about prussia` got the
        COMMAND REFERENCE; the button route answered "A question is not an
        answer… 1=What should we do about Prussia?"). A label is compared
        modulo terminal punctuation, and a line that carries every word of
        a QUESTION-shaped label is that label, whatever leads it in;
      * R4-3 — a subject-auxiliary inversion ANYWHERE in the line is a
        question too. Measured, pre-existing on every family: `then shall
        we ratify` RATIFIED a seven-pair settlement at a HARD STOP, `sire do
        we accept` SIGNED Portugal's treaty, `then shall we yield` YIELDED an
        ultimatum. The statements `we shall accept`, `i will accept`, `we do
        accept` are not inversions and still answer. Behind
        A_QUESTION_NEVER_ANSWERS, like the rule it completes.
    """
    from backend.ai.clause_guards import is_question

    text = str(typed or "")
    if choice_is_an_exact_token(text, options):
        return False
    if _carries_a_question_label(text, options):
        return False
    if "?" in text or bool(is_question(text)):
        return True
    return bool(A_QUESTION_NEVER_ANSWERS
                and _SUBJECT_AUXILIARY_INVERSION_RE.search(text.lower()))


def free_text_of_choice(dialogue: Optional[dict], choice) -> Optional[str]:
    """R3-10: the `raw_text` a button-route choice carries, or None.

    `POST /respond_to_diplomatic_dialogue` takes a digit, an action id, a
    label — or FREE TEXT, and free text names courts and matters exactly as
    a typed line does. Measured: `accept Switzerland's petition` sent there
    with Portugal's letter current SIGNED PORTUGAL'S TREATY, because the
    endpoint handed the handler no `raw_text` and the court guard never
    ran. An exact token is what a button sends and names nothing, so it
    stays None (the W6-0 `dialogue_id` binds it instead)."""
    if not THE_BUTTON_ROUTE_READS_THE_COURT or not isinstance(choice, str):
        return None
    if choice_is_an_exact_token(choice, dialogue_options(dialogue)):
        return None
    return choice


def _names_a_marshal(text: str,
                     marshal_names: Optional[List[str]]) -> bool:
    """True when `text` contains one of the roster names as a whole word."""
    if not marshal_names or not text:
        return False
    return any(whole_phrase_in(n.lower(), text)
               for n in marshal_names if n)


def addresses_a_marshal(raw_lower: str,
                        marshal_names: Optional[List[str]]) -> bool:
    """True when the typed line names one of the player's own marshals.

    UX23-R5. An order that names a marshal is an ORDER, and must never be
    consumed as an answer to a dialogue that merely happens to share a word
    with it. Measured: with a Talleyrand advisory open, `Soult, cancel your
    march` matched the `cancel` keyword (which maps onto the advisory's
    `dismiss`) and was eaten as the answer — Soult marched on.

    Two shapes, because the defect has two:
      * the comma address — `Soult, cancel your march` — via the parser's own
        `_leading_addressed_token`, so the interjection/bare-verb exclusions
        ("No, charge!") are inherited rather than re-implemented;
      * the name anywhere in the line as a whole word — `cancel Soult's
        march`. `main.py` already runs exactly this pair inside the
        strategic-interrupt block, for exactly this reason.
    """
    if not marshal_names:
        return False
    from backend.commands.parser import _leading_addressed_token

    addressed = _leading_addressed_token(raw_lower)
    lowered = {n.lower() for n in marshal_names if n}
    if addressed and addressed.lower() in lowered:
        return True
    return _names_a_marshal(raw_lower, marshal_names)


# Aug 30, 2026 review: the vocabulary of an ORDER. Reused rather than
# re-listed where possible — the verb half is `clause_guards._ORDER_NOUNS`,
# which already enumerates attack/advance/march/retreat/bombard/siege and
# their inflections for the negation guard. What is added here is the nouns an
# order acts ON, which that regex has no reason to carry.
_MILITARY_OBJECT_WORDS = frozenset({
    "corps", "army", "armies", "troops", "men", "soldiers", "regiment",
    "regiments", "division", "divisions", "battalion", "guard", "column",
    "infantry", "cavalry", "artillery", "guns", "cannon", "horse", "foot",
    "depot", "depots", "fort", "fortress", "fortification", "garrison",
    "watchtower", "market", "stables", "ships", "fleet", "squadron",
    "north", "south", "east", "west", "flank", "rear", "front", "line",
})
# Ordinary words a real ANSWER may carry — "cancel it", "yes, do that then".
_ANSWER_FILLER_WORDS = frozenset({
    "the", "a", "an", "it", "this", "that", "those", "these", "them",
    "please", "sire", "then", "just", "now", "ok", "okay", "well", "very",
    "do", "does", "did", "is", "are", "be", "and", "but", "or", "so", "if",
    "we", "i", "you", "us", "our", "my", "let", "lets", "with", "for", "to",
    "of", "on", "in", "at", "by", "as", "all", "any", "matter", "offer",
    "terms", "proposal", "letter", "answer", "reply", "decision", "choice",
    "one", "two", "three", "first", "second", "third", "instead", "rather",
})


def _dialogue_subject_words(dialogue: Optional[dict]) -> set:
    """Every word the dialogue itself speaks — its prompt, its options, its
    context. A word the matter at hand already contains is the SUBJECT, not a
    foreign order: `yield Hanover` answering Prussia's demand for Hanover is
    an answer, while `cancel the march` on a proposal confirm is an order,
    because that dialogue says nothing of a march.
    """
    if not isinstance(dialogue, dict):
        return set()
    blob = []
    for key in ("message", "prompt", "text", "talleyrand_text", "title"):
        value = dialogue.get(key)
        if isinstance(value, str):
            blob.append(value)
    context = dialogue.get("context")
    if isinstance(context, dict):
        blob.append(repr(context))
    for option in dialogue.get("options") or []:
        if isinstance(option, dict):
            blob.append(repr(option))
    return set(re.findall(r"[a-z']+", " ".join(blob).lower()))


# SR-2b (AAR-20b, September 26, 2026): the words a player uses to PICK a row
# off the open nation list — anything else on the line is an order.
_COURT_PICK_WORDS = frozenset({"choose", "pick", "select", "approach", "try",
                               "go", "yes"})


def _line_is_only_the_court(raw_lower: str, label: str) -> bool:
    """True when the line names the court and nothing else (filler and a
    picking verb aside). The proposal picker's nation list may claim a line
    only then: `improve relations with Russia` is an ORDER for Russia."""
    label_words = set(re.findall(r"[a-z]+", (label or "").lower()))
    if not label_words:
        return False
    rest = [w for w in re.findall(r"[a-z']+", raw_lower)
            if w not in label_words and w not in _ANSWER_FILLER_WORDS
            and w not in _COURT_PICK_WORDS]
    return not rest


def _carries_military_content(raw_lower: str, keyword: str,
                              world_regions=None,
                              dialogue: Optional[dict] = None) -> bool:
    """True when what remains after the keyword reads as an ORDER.

    An answer names the decision in front of the player; an order names the
    war. `send the corps north` and `cancel the march` were both consumed as
    dialogue answers — the order never reached the executor and the player was
    never told.

    Words the dialogue ITSELF uses are exempt, which is what keeps `yield
    Hanover` answering an ultimatum that demands Hanover: nineteen province
    names double as court names and several are ordinary military nouns, so
    without that exemption the guard would refuse the answers it exists to
    protect.
    """
    from backend.ai.clause_guards import _ORDER_NOUNS

    leftover = re.sub(r"(?<![a-z])" + re.escape(keyword) + r"(?![a-z])",
                      " ", raw_lower)
    subject = _dialogue_subject_words(dialogue)
    words = [w for w in re.findall(r"[a-z']+", leftover)
             if w not in _ANSWER_FILLER_WORDS and w not in subject]
    if not words:
        return False
    order_verb = re.compile(r"^(?:" + _ORDER_NOUNS + r")$")
    for word in words:
        if word in _MILITARY_OBJECT_WORDS or order_verb.match(word):
            return True
    if world_regions:
        lowered = {str(r).lower() for r in world_regions}
        if any(w in lowered for w in words):
            return True
    return False


def _self_negating_answer_tokens(options: List[dict]) -> List[str]:
    """FA-N2: the answer tokens that ARE a negation, rather than a refusal
    of one.

    Exactly two exist in the shipped game, and both are load-bearing: the
    option label ``Proceed Without Allies`` (the ally-entry confirm,
    `diplomatic_executor.py`) and the verb keyword ``never mind`` (which maps
    onto ``dismiss``). ``without`` and ``never`` are negation markers, so
    blanking negated clauses would silently make both unanswerable. They are
    restored below rather than special-cased, so the rule is stated once:
    *a token that is itself an answer may carry a negation; a negation ABOUT
    an answer is not one.*

    Measured census over `backend/` at the time of writing: 229 distinct
    literal option labels, of which one carries a marker; 45 keywords, of
    which one does. A third arriving later is restored automatically —
    nothing here enumerates them by name.
    """
    tokens = [(opt.get("label") or "").lower().strip() for opt in options]
    tokens.extend(DIALOGUE_ACTION_KEYWORDS)
    return [t for t in tokens if t and negation_marker_spans(t)]


def text_the_player_still_means(raw_lower: str,
                                options: List[dict]) -> str:
    """FA-N2 (verification pass, September 2, 2026): blank the clauses the
    player NEGATED, so a refusal can never be read as consent.

    Every arm of `match_dialogue_answer` reads the raw line, and a negated
    sentence carries the same words as its affirmative — so `do not accept`
    returned ``accept`` and SIGNED THE TREATY; `we will not yield` conceded
    an ultimatum; `don't accept`, `never accept`, `I refuse to accept these
    terms` and `under no circumstances accept` all did the same. This is
    PARSE-NEG's exact defect class alive one layer ABOVE the seam PARSE-NEG
    guards: `clause_guards` runs inside the parser, and this router answers
    before the parser is ever consulted. The two sibling routers in `main.py`
    already strip negated clauses before reading the line; this one never
    did, and the last maintenance pass on this function (UX23-R5) added a
    marshal-address guard, not a negation guard.

    The blank is index-preserving by `strip_negated_clauses`'s own documented
    contract, which is what lets the exemption above be a RESTORE of the
    original characters rather than a second copy of arm 1's matching rule.
    Every arm below then runs unchanged, keeping its own address and
    military-content guards — the "two implementations of one rule, only one
    maintained" failure this codebase keeps finding is avoided by
    construction.

    When nothing survives, no arm can claim the line: a hard stop answers
    with its own numbered re-prompt, and a soft stop falls through to the
    ordinary road, where the parser refuses the order the player forbade.
    Neither executes it.
    """
    effective, negated = strip_negated_clauses(raw_lower)
    if not negated:
        return raw_lower
    markers = negation_marker_spans(raw_lower)
    chars = list(effective)
    for token in _self_negating_answer_tokens(options):
        start = raw_lower.find(token)
        while start != -1:
            end = start + len(token)
            # The token is restored only when the negation that blanked it is
            # the token's OWN — a marker inside the span, with none standing
            # before it. `never proceed without allies` REFUSES the option
            # whose label happens to read `Proceed Without Allies`, and must
            # not be answered with it; `sire, never mind` is that answer.
            # A line that negates something else FIRST ("do not attack, never
            # mind") declines to restore: two clauses, and refusing to guess
            # is the safe half of the trade.
            own = any(start <= m_start < end for m_start, _ in markers)
            preceded = any(m_start < start for m_start, _ in markers)
            if own and not preceded:
                chars[start:end] = list(token)
            start = raw_lower.find(token, start + 1)
    return "".join(chars)


def match_dialogue_answer(dialogue: Optional[dict],
                          raw_lower: str,
                          marshal_names: Optional[List[str]] = None,
                          world_regions=None
                          ) -> Optional[str]:
    """Return the token to hand the response handler, or None if this
    typed line is not an answer to THIS dialogue.

    Only the dialogue's own options may claim a line:
      1. a full option label, or its action id, appearing in the text —
         SKIPPED for a line that names a marshal, unless the option's own
         label names one too
      2. — the UX23-R5 guard: any other line that NAMES A MARSHAL stops here —
      3. every word of a label appearing in the text ("reject THE offer")
      4. a verb keyword — as a WHOLE WORD, and only when it maps onto an
         action this dialogue actually offers

    An order that names a marshal is an ORDER, and reaches none of these arms.
    The per-option exemption in arm 1 is what keeps `Recall Ney` working: an
    option whose own label names a marshal may still match verbatim, because
    there the name is the answer rather than the address.

    Recorded trade: a conversational answer that happens to name a marshal —
    `accept, and let Ney hold` on an incoming proposal — now falls through to
    the parser instead of answering. That is the intended direction (the row's
    completion definition is "an order naming a marshal is never consumed as a
    dialogue answer"), and it is stated here rather than discovered later.
    """
    options = dialogue_options(dialogue)
    if not options:
        return None
    # ══════════════════════════════════════════════════════════════════
    # FA-N2 — AN ANSWER IS READ FROM WHAT THE PLAYER STILL MEANS; AN ORDER
    # IS DETECTED FROM WHAT THEY SAID.
    #
    # The MATCHING arms below read the negation-stripped line, so a refusal
    # can never be matched as the consent it negates.
    #
    # The two GUARDS keep the line as typed, and that distinction is
    # load-bearing. A first cut reassigned `raw_lower` and let everything
    # read the blanked text — which silently disarmed both guards, because
    # a prohibition is still military content and a name inside a
    # prohibition is still a name. Measured on that first cut:
    # `without ney, cancel` CANCELLED THE SETTLEMENT (the UX23-R5 marshal
    # guard saw no marshal — the name had been blanked), and
    # `accept, never march on paris` SIGNED THE TREATY and threw the order
    # away without telling the player — the exact Aug-30 defect that guard
    # was landed to close, re-opened by the fix for this one. The pin that
    # should have caught it went VACUOUS rather than red: `never mind the
    # money` stopped reaching `_names_a_marshal` at all.
    # ══════════════════════════════════════════════════════════════════
    typed = raw_lower
    # ══════════════════════════════════════════════════════════════════
    # IQ-7 review pass 3 (R3-9) — A QUESTION IS NEVER AN ANSWER, for ANY
    # dialogue. Measured with Portugal's open-borders letter current:
    # `should i accept?` SIGNED THE TREATY (arm 4 read `accept` out of the
    # question). A soft stop hands such a line to the ordinary road, where
    # the question desk answers it; a hard stop re-prompts with its own
    # numbered options. Neither executes anything.
    # ══════════════════════════════════════════════════════════════════
    if A_QUESTION_NEVER_ANSWERS and line_asks_a_question(typed, options):
        return None
    # ══════════════════════════════════════════════════════════════════
    # IQ-7 review pass 2 (P2-1) — A CLIENT PETITION IS ANSWERED PLAINLY.
    #
    # The popup's buttons and the rail teach the words `Grant the petition`
    # / `Refuse the petition`, and arm 1 (label containment) and arm 3
    # (every label word) matched them INSIDE any sentence: measured on the
    # shipped turn-6 board with the petition current, `grant the petition
    # later`, `… next turn`, `…, but not now`, `… if the treasury allows`,
    # `should i grant the petition?`, `maybe grant the petition` and `i
    # will grant the petition later` all GRANTED (1 DP, 1800g forgone),
    # and `refuse the petition later` REFUSED at -10 loyalty / -20 bond.
    # The keyword arm did the same one rung down (`accept the petition
    # later`, `yes, later`, `accept it next turn`, `could we grant the
    # petition`, `reject the petition tomorrow`, `yes, but not the
    # petition` — all measured answering).
    #
    # For a CLIENT petition only (Slice H's ally petition is untouched, and
    # so is every other family — FA-N2's trailing-bare-`no` and two-option
    # cases stay a stated limit on that row) EVERY arm yields to the whole
    # line: `petition_plain_answer` is the router. A line that is not a
    # plain answer claims nothing and falls to the ordinary road, where
    # Berthier's own deferral arm answers it ("For a later day, Sire — but
    # I keep no drawer for tomorrow's orders") and nothing is executed.
    # The arms below are unreachable for such a dialogue by construction,
    # which is the point: there is no second reading of the line to drift.
    # ══════════════════════════════════════════════════════════════════
    if (A_PETITION_IS_ANSWERED_PLAINLY
            and _is_client_petition_dialogue(dialogue)):
        return petition_plain_answer(dialogue, typed)
    raw_lower = text_the_player_still_means(raw_lower, options)
    raw_words = set(re.findall(r"[a-z]+", raw_lower))
    addressed = addresses_a_marshal(typed, marshal_names)

    # 1. verbatim — a label or an action id, spelled out.
    #
    # The guard is applied PER OPTION here, not as a gate below this loop.
    # A first cut put it below, reasoning that a verbatim match is never a
    # guess — but arm 1 is bare-substring containment, so any dialogue whose
    # option label is a single common word matched before the guard ever ran.
    # Measured on production option sets: with an incoming ULTIMATUM mounted
    # (labels `Yield` / `Defy`), **`Ney, yield no ground` YIELDED THE
    # ULTIMATUM** — an order to a marshal ceding the demanded provinces. Same
    # for `Accept`/`Reject` on an incoming proposal and `Cancel` on the war-
    # purpose chooser. That is the very class of defect this row exists to
    # close, and the fix had walked straight past it.
    #
    # The exemption is what keeps `Recall Ney` and `Commission Suchet`
    # working: an option whose OWN label names a marshal may still be matched
    # verbatim, because there the name is the answer rather than the address.
    for opt in options:
        label = (opt.get("label") or "").lower().strip()
        action = (opt.get("action") or "").lower().strip()
        if addressed and not _names_a_marshal(label, marshal_names):
            continue
        # SR-2b (AAR-20b): the open NATION LIST (the proposal picker's
        # `expand_options` rows) may claim a line only when the line IS the
        # court. `improve relations with Russia` is an order for Russia —
        # measured, the list claimed it by substring, the resolver matched
        # "russia" inside "Prussia", and the player was answered with
        # PRUSSIA's proposal menu.
        if action == "expand_options" and not _line_is_only_the_court(raw_lower, label):
            continue
        # Aug 30, 2026 review: arm 1 is bare-substring containment, so a
        # ONE-WORD label is as loose as the keyword scan below — measured, the
        # label `Cancel` claimed "cancel the march", an order to break a
        # standing move, and the executor never saw it. Same rule as arms 3
        # and 4: an answer names the decision, an order names the war.
        if label and label in raw_lower:
            if _carries_military_content(typed, label, world_regions,
                                         dialogue):
                continue
            return label
        if action and action in raw_lower:
            return action

    # 2. the guard, for the inferential arms below.
    if addressed:
        return None

    # 3. every word of a label, in any order. A live hijack vector of its own:
    #    the label "Send as ordered" is {send, as, ordered}, which
    #    `as ordered, send Ney` satisfies without meaning it.
    for opt in options:
        label = (opt.get("label") or "").lower().strip()
        action = (opt.get("action") or "").lower().strip()
        label_words = set(re.findall(r"[a-z]+", label))
        # SR-2b (AAR-20b): same rule as arm 1 for the nation list.
        if action == "expand_options" and not _line_is_only_the_court(raw_lower, label):
            continue
        if label_words and label_words <= raw_words:
            # Aug 30, 2026 review: the same order-vs-answer rule as arm 4.
            # A ONE-WORD label makes this arm as loose as a bare-substring
            # scan — measured, the label `Cancel` claimed "cancel the march",
            # an order to break a standing move, and the executor never saw
            # it.
            if _carries_military_content(typed, label, world_regions,
                                         dialogue):
                continue
            return action or label

    # 3b. IQ-7 review R9: the petition's own words, on a petition ONLY and
    #     only as the whole line (see PETITION_ANSWER_KEYWORDS). Read from
    #     the negation-stripped line like every matching arm, so `do not
    #     grant it` survives as nothing and claims nothing (FA-N2).
    #     Pass 2 (P2-1): with A_PETITION_IS_ANSWERED_PLAINLY up a CLIENT
    #     petition never reaches this arm — `petition_plain_answer` is its
    #     whole router, above; this arm is the lever-down (pass-1) road.
    if _dialogue_is_petition_family(dialogue):
        petition_action = petition_vocabulary_answer(raw_lower)
        if petition_action and petition_action in offered_actions(options):
            return petition_action

    # 4. a bare verb keyword.
    #
    # Aug 30, 2026 review: "bare" was never enforced — the arm asked only
    # whether the keyword appeared ANYWHERE in the sentence, so a marshal-less
    # ORDER carrying one of these words was silently consumed as an answer.
    # Measured against a live `proposal_confirm` option set: "send the corps
    # north" -> `send` and "cancel the march" -> `cancel`. The order never
    # reached the executor and the player was never told, which is the same
    # class of defect as the `Ney, yield no ground` hijack arm 1 guards
    # against — one rung down, and without a marshal name for that guard to
    # catch.
    #
    # An answer names the decision; an order names the war. If anything
    # military survives once the keyword and ordinary filler are removed, this
    # is an order and the arm declines it.
    offered = {str(o.get("action") or "") for o in options}
    for keyword, actions in DIALOGUE_ACTION_KEYWORDS.items():
        if not whole_phrase_in(keyword, raw_lower):
            continue
        if not any(a in offered for a in actions):
            continue
        if _carries_military_content(typed, keyword, world_regions,
                                     dialogue):
            continue
        return keyword
    return None


# ══════════════════════════════════════════════════════════════════════
# Which court is on the table, and which court did the player name?
# ══════════════════════════════════════════════════════════════════════

def offered_actions(options: List[dict]) -> set:
    return {str(o.get("action") or "") for o in (options or [])}


def dialogue_court(dialogue: Optional[dict]) -> str:
    """The court a dialogue concerns. Same resolution order the W6-0
    stale-dialogue refusal already uses to name the court in its own
    message — one reader now, so the guard and the message cannot drift."""
    if not isinstance(dialogue, dict):
        return ""
    context = dialogue.get("context")
    context = context if isinstance(context, dict) else {}
    return str(
        dialogue.get("target_nation")
        or dialogue.get("proposer_nation")
        or dialogue.get("ally_nation")
        # PC15-3: the pair-substitute chooser carries its court under
        # `selected_target_nation` — with none of the keys above set,
        # dialogue_court returned "" and the CA9 typed court guard was a
        # no-op for this dtype.
        or dialogue.get("selected_target_nation")
        or context.get("source_nation")
        or context.get("source")
        or dialogue.get("nation")
        or ""
    )


# An addressee marker, not a mere mention. `accept Portugal's proposal`
# names a counterparty; `accept, and we keep Hanover` names a province
# that happens to share a nation's tag. Under-refusing is the safe
# direction, so only an explicit possessive or a preposition counts.
_ADDRESSEE_PREPOSITIONS = ("from", "with", "to", "for", "of", "by", "on")


def _addressee_forms(nation: str) -> List[str]:
    """Every spelling of a court that could carry the addressee role."""
    from backend.display_names import display_nation, nation_adjective

    forms = {str(nation), display_nation(nation), nation_adjective(nation)}
    return [f.lower() for f in forms if f]


def courts_addressed_in(text: str, world) -> List[str]:
    """Courts the player explicitly ADDRESSED in this line.

    A bare mention is not enough — the name must carry a possessive
    (`Portugal's`, `the Portuguese`) or follow an addressee preposition
    (`the offer from Prussia`). This keeps `we keep Hanover` from reading
    as a court, since Hanover is also a province on this map.
    """
    lowered = str(text or "").lower()
    if not lowered:
        return []
    get_nations = getattr(world, "get_active_nations", None)
    if not callable(get_nations):
        return []
    try:
        nations = list(get_nations() or [])
    except Exception:
        return []
    player = str(getattr(world, "player_nation", "") or "")
    prepositions = "|".join(_ADDRESSEE_PREPOSITIONS)
    found: List[str] = []
    for nation in nations:
        if nation == player:
            continue
        for form in _addressee_forms(nation):
            escaped = re.escape(form)
            possessive = (
                rf"(?<![a-z]){escaped}(?:'s|’s|s'|s’)(?![a-z])")
            prepositional = (
                rf"(?<![a-z])(?:{prepositions})\s+(?:the\s+)?{escaped}"
                rf"(?![a-z])")
            attributive = rf"(?<![a-z])the\s+{escaped}(?![a-z])"
            if (re.search(possessive, lowered)
                    or re.search(prepositional, lowered)
                    or re.search(attributive, lowered)):
                found.append(nation)
                break
    return found


def _names_the_matter_at_hand(name: str, dialogue: Optional[dict],
                              world) -> bool:
    """True when `name` is a PROVINCE the active dialogue is about.

    Nineteen 1805 province names double as court names (Hanover, Bavaria,
    Saxony, Naples…), so "yield Hanover" reads as addressing Hanover's court
    when it is in fact answering Prussia's demand FOR Hanover. Both halves are
    required: the name must be a real region, and the dialogue must already be
    about it — so "declare war on Hanover" typed at Prussia's table is still
    refused, because Prussia's matter says nothing of Hanover.
    """
    if not name or not dialogue:
        return False
    regions = getattr(world, "regions", None) or {}
    if name not in regions:
        return False
    haystack = []
    for key in ("message", "prompt", "text", "talleyrand_text", "title"):
        value = dialogue.get(key)
        if isinstance(value, str):
            haystack.append(value)
    context = dialogue.get("context")
    if isinstance(context, dict):
        haystack.append(repr(context))
    for option in dialogue.get("options") or []:
        if isinstance(option, dict):
            haystack.append(repr(option))
    lowered = " ".join(haystack).lower()
    return name.lower() in lowered


def court_mismatch_refusal(world, dialogue: Optional[dict],
                           raw_text: str) -> Optional[dict]:
    """Refuse a typed answer aimed at a court that is not on the table.

    Returns None when the answer may proceed: no court named, or the
    active court is among the ones named (``reject Prussia's demand for
    Hanover`` names two and the active one is there).
    """
    active = dialogue_court(dialogue)
    if not active:
        return None
    addressed = courts_addressed_in(raw_text, world)
    # Aug 30, 2026 review: nineteen of the map's province names are also court
    # names, so a player answering the matter in front of him by naming the
    # PROVINCE it is about was refused for addressing a third court. Measured
    # shape: Prussia's ultimatum demands Hanover, the player types "yield
    # Hanover", and the guard answers that nothing from Hanover is before him.
    # A name the ACTIVE dialogue is itself about is the subject, not an
    # addressee.
    addressed = [n for n in addressed
                 if not _names_the_matter_at_hand(n, dialogue, world)]
    if not addressed or active in addressed:
        return None

    from backend.display_names import display_nation, with_definite_article

    # Pass 3 (NOTED c): the active court carries its article, as the matter
    # guard's head always has — "delivered to the Kingdom of Italy".
    active_display = with_definite_article(display_nation(active))
    # Pass 4 (R4-5): …and so does every court the TAIL names — measured with
    # Switzerland's petition current, `grant the kingdom of italy's petition`
    # answered "Nothing from Kingdom of Italy is before you".
    named_display = " and ".join(
        with_definite_article(display_nation(n)) for n in addressed)

    waiting, place, it = _queued_court_summary(world, addressed)
    if waiting:
        tail = (
            f" {waiting} — open {place} and answer {it} there."
        )
    else:
        tail = (
            f" Nothing from {named_display} is before you; answer "
            f"{active_display} first, or set this matter aside."
        )
    return {
        "success": False,
        "court_mismatch": True,
        "message": (
            f"Sire — that answer would be delivered to {active_display}, "
            f"whose matter is the one before you.{tail}"
        ),
        "diplomatic_dialogue": dialogue,
        "awaiting_diplomatic_response": True,
    }


def court_mismatch_refusal_for_a_petition(world, dialogue: Optional[dict],
                                          raw_text: str) -> Optional[dict]:
    """R3-3 (V2-4): the court guard, at the `/command` ROUTER seam, for a
    CURRENT client petition.

    The court guard lives at the handler seam, which a line reaches only
    when the active dialogue CLAIMED it. A client petition claims a line
    only by the closed plain grammar, which blanks its OWN court and nothing
    else — so with the petition current, `accept portugal's offer`, `decline
    the portuguese offer`, `grant the kingdom of italy's petition` and
    `decline spain's petition` never reached the guard and got Berthier's
    shrug (lever down: "Portugal's matter waits in the letter-book"). Here
    an ANSWER-SHAPED line (`_line_is_answer_shaped` — never an order that
    merely names a court) is read by the court guard first, so the waiting
    court's pointer is reachable again. Nothing is executed either way.
    """
    if not (A_PETITION_IS_ANSWERED_PLAINLY
            and _is_client_petition_dialogue(dialogue)):
        return None
    if not _line_is_answer_shaped(str(raw_text or ""), world):
        return None
    return court_mismatch_refusal(world, dialogue, raw_text)


def _queued_matter_dialogues(world, predicate) -> List[dict]:
    """The QUEUED (not current) dialogues of one family."""
    manager = getattr(world, "dialogue_manager", None)
    if manager is None or not hasattr(manager, "iter_queue"):
        return []
    try:
        queued = list(manager.iter_queue() or [])
    except Exception:
        return []
    return [d for d in queued if isinstance(d, dict) and predicate(d)]


# P3-3: the verbs that ANSWER a matter. An order may carry a family noun
# (`send ultimatum to Austria`, `petition the senate for more men`); only a
# line that is one of these verbs and nothing else is an answer.
_MATTER_ANSWER_VERBS = frozenset({
    "accept", "agree", "reject", "decline", "refuse", "grant", "yield",
    "defy", "honour", "honor", "counter",
    # …and the same verbs as the player states them done: `the petition's
    # terms are agreed`, `petition granted` (pass 1's own pinned phrasing).
    "accepted", "agreed", "rejected", "declined", "refused", "granted",
    "yielded", "defied", "honoured", "honored", "countered",
})


def _line_is_answer_shaped(typed: str, world) -> bool:
    """P3-3: True when the typed line, less answer filler, the family nouns,
    the negation markers and any court it names, is ONE answer verb.

    `accept the ultimatum`, `yield to the ultimatum`, `do not accept the
    petition`, `grant Switzerland's petition` -> True.
    `send ultimatum to Austria`, `deliver an ultimatum to Austria: cede
    Tyrol`, `Ney, ignore the petition and march to Swabia` -> False: an
    ORDER, which the router must hand to the ordinary road.
    """
    text = str(typed or "").lower().replace("’", "'")
    chars = list(text)
    for start, end in negation_marker_spans(text):
        for i in range(start, end):
            chars[i] = " "
    text = "".join(chars)
    get_nations = getattr(world, "get_active_nations", None)
    nations: List[str] = []
    if callable(get_nations):
        try:
            nations = list(get_nations() or [])
        except Exception:
            nations = []
    # Pass 3, behind A_PETITION_IS_ANSWERED_PLAINLY — the shape gate knows
    # the plain grammar's own vocabulary, so the SAME line is not a priced
    # answer with the petition current and Berthier's shrug with it queued:
    #   * R3-5 (V2-6): the emphasis PHRASES go (`grant the petition at
    #     once`, `accept the petition gladly` keep their Envoys pointer;
    #     `send ultimatum to Austria at once` is still an order — `send`);
    #   * the diplomat address goes (`Talleyrand, grant the petition`);
    #   * R3-3: `from <court>` goes with the court it introduces (`accept
    #     the offer from portugal` is answer-shaped, so the court guard can
    #     speak) — `from` is not answer filler on its own.
    plain = bool(A_PETITION_IS_ANSWERED_PLAINLY)
    introduced = r"(?:from\s+)?(?:the\s+)?" if plain else ""
    for nation in nations:
        for form in sorted(_addressee_forms(nation), key=len, reverse=True):
            text = re.sub(
                rf"(?<![a-z]){introduced}{re.escape(form)}(?:'s|’s|s'|s’)?(?![a-z])",
                " ", text)
    if plain:
        for emphasis in _PLAIN_EMPHASIS_PHRASES:
            text = re.sub(rf"(?<![a-z]){re.escape(emphasis)}(?![a-z])", " ", text)
    family_nouns = re.compile(
        r"^(?:" + "|".join(p for _, p, _, _ in MATTER_NOUN_FAMILIES) + r")$")
    # A possessive qualifies the noun (`grant Italy's petition`, `grant
    # their petition`); it is never the verb of an order.
    kept = [w for w in re.findall(r"[a-z']+", text)
            if w not in _ANSWER_FILLER_WORDS
            and not (plain and w in _PLAIN_DIPLOMAT_WORDS)
            and w not in _BARE_NEGATION_WORDS
            and w not in _POSSESSIVE_PRONOUNS
            and not w.endswith("'s")
            and not family_nouns.match(w)]
    return len(kept) == 1 and kept[0] in _MATTER_ANSWER_VERBS


def _names_a_waiting_court(world, predicate, addressed: List[str]) -> bool:
    """R3-6: True when the line addresses a court that has a matter of this
    family WAITING in the queue — that line is about the waiting matter,
    whatever family the active dialogue belongs to."""
    if not addressed:
        return False
    queued_courts = {dialogue_court(d)
                     for d in _queued_matter_dialogues(world, predicate)}
    return any(court in queued_courts for court in addressed)


def _active_dialogue_claims_the_verb(dialogue: Optional[dict],
                                     typed: str) -> bool:
    """P3-4: True when the bare petition verb on this line (`refuse`,
    `refuse it`, `refuse them`) is one the ACTIVE dialogue answers to —
    `DIALOGUE_ACTION_KEYWORDS['refuse']` is `reject_ai_ultimatum`, and an
    ultimatum's own Defy option reads "Refuse the demands"."""
    kept = _petition_vocabulary_kept(typed)
    if len(kept) != 1:
        return False
    offered = offered_actions(dialogue_options(dialogue))
    return any(a in offered
               for a in DIALOGUE_ACTION_KEYWORDS.get(kept[0], []))


def matter_mismatch_refusal(world, dialogue: Optional[dict],
                            raw_text: str, *,
                            answers_only: bool = False) -> Optional[dict]:
    """IQ-7 review R9 ([09]/[13]): refuse a typed answer that names a MATTER
    which is not the one on the table.

    The court guard above binds a typed line to a court; this is its
    sibling for the family noun — "the petition", "the ultimatum", "the
    settlement" — because on the shipped board the petition is queued
    behind whatever mail arrived first, and `accept the petition` signed
    Portugal's open-borders letter. Rules, in order:

      * the noun is read from the line AS TYPED, like the court guard, so
        `do not accept the petition` is refused rather than passed on;
      * a line that names a family the ACTIVE dialogue itself belongs to
        proceeds (`decline the petition` on an ally petition is an answer);
      * a line that also names the ACTIVE court proceeds (`never mind the
        petition, accept Portugal's offer`), as the court guard lets
        `reject Prussia's demand for Hanover` through;
      * the refusal fires ONLY while a dialogue of that family is QUEUED —
        with none pending the line falls through exactly as today;
      * the petition's own vocabulary with no noun (`grant it`, `refuse`)
        is a petition-family line too, so it gets the same "waits" line and
        never Berthier's shrug.

    Pass 2, behind THE_MATTER_GUARD_READS_THE_TABLE:

      * P3-3 — `answers_only=True` is the `/command` ROUTER seam, where by
        construction no answer keyword matched the letter on top. There the
        guard fires only for an ANSWER-SHAPED line (`_line_is_answer_
        shaped`): measured, the noun alone refused the player's own `send
        ultimatum to Austria` as "Prussia's ultimatum waits in Envoys" —
        an ORDER eaten by a dialogue guard. The handler seam (the active
        letter DID claim the line) keeps the broad noun rule;
      * P3-4 — a bare petition verb the ACTIVE dialogue answers to is that
        dialogue's word, not the petition's: `refuse` defies the ultimatum
        on the table even while a petition waits behind it;
      * P4-6 — an ACTIVE petition-family dialogue that does not OFFER the
        resolved action (Slice H's ally petition offers Grant the Claim /
        Decline, never `accept_ai_proposal`) does not own `grant the
        petition`; the line gets the "waits in Envoys" refusal, naming the
        words the ally petition itself takes, rather than Berthier's shrug;
      * P4-4 — a courtless active dialogue (the W6-9 `advisory`) is named
        as "the matter before you", once;
      * R3-6 (pass 3) — a same-family line that NAMES a court whose matter
        is waiting (`grant switzerland's petition` with Spain's ally
        petition current) is about the waiting matter: it gets the same
        "waits in Envoys" refusal the bare verb gets.

    Returns None when the answer may proceed.
    """
    if not isinstance(dialogue, dict):
        return None
    typed = str(raw_text or "").lower()
    if not typed:
        return None
    active = dialogue_court(dialogue)
    addressed = courts_addressed_in(raw_text, world)
    if active and active in addressed:
        return None

    from backend.display_names import display_nation, with_definite_article

    reads_the_table = bool(THE_MATTER_GUARD_READS_THE_TABLE)
    if (answers_only and reads_the_table
            and not _line_is_answer_shaped(typed, world)):
        return None

    for family, pattern, predicate, noun in MATTER_NOUN_FAMILIES:
        named = re.search(r"(?<![a-z])" + pattern + r"(?![a-z])", typed) is not None
        by_noun = named
        if (not named and family == "petition"
                and petition_vocabulary_answer(typed) is not None):
            named = True
        if (named and not by_noun and reads_the_table
                and _active_dialogue_claims_the_verb(dialogue, typed)):
            # P3-4: the bare verb is the ACTIVE dialogue's own word.
            named = False
        if not named:
            continue
        same_family = bool(predicate(dialogue))
        if same_family:
            # P4-6: the active dialogue speaks of this family — it owns the
            # line unless the line resolves to an action it does not offer.
            resolved = (petition_vocabulary_answer(typed)
                        if family == "petition" and reads_the_table else None)
            if resolved is None or resolved in offered_actions(
                    dialogue_options(dialogue)):
                # Pass 3 (R3-6, V2-8): …and unless the line NAMES a court
                # whose matter of this family is WAITING. Measured with
                # Spain's ally petition current: the bare `grant` got the
                # Envoys pointer while the MORE explicit `grant
                # switzerland's petition` got Berthier's shrug.
                if not (reads_the_table and _names_a_waiting_court(
                        world, predicate, addressed)):
                    continue
        waiting = _queued_matter_dialogues(world, predicate)
        if not waiting:
            continue
        courts = []
        for d in waiting:
            court = dialogue_court(d)
            if court and court not in courts:
                courts.append(court)
        # A line that names one of the waiting courts means THAT court's
        # matter, not every court's.
        narrowed = [c for c in courts if c in addressed]
        if narrowed:
            courts = narrowed
        named_courts = " and ".join(
            with_definite_article(display_nation(c)) for c in courts) or "a court"
        verb = "waits" if len(courts) <= 1 else "wait"
        plural = "s" if len(courts) > 1 else ""
        waits = (
                f"{named_courts[:1].upper()}"
                f"{named_courts[1:]}'s {noun}{plural} {verb} in Envoys — open "
                f"Envoys and answer it there."
        )
        if len(courts) > 1:
            waits = waits.replace("answer it there.", "answer them there.")
        if same_family:
            own_words = format_answer_words(
                o.get("label") for o in dialogue_options(dialogue))
            whose = (f"{with_definite_article(display_nation(active), capitalize=True)}'s "
                     f"own {noun}" if active else f"Another {noun}")
            takes = f", and it takes {own_words}" if own_words else ""
            head = f"Sire — {whose} is the matter before you{takes}."
        elif active:
            head = (f"Sire — that answer would be delivered to "
                    f"{with_definite_article(display_nation(active))}, whose "
                    f"matter is the one before you.")
        else:
            # P4-4: no court to name — say so once, not twice.
            head = "Sire — the matter before you takes that answer;"
            waits = waits[:1].lower() + waits[1:] if _starts_with_article(waits) else waits
        return {
            "success": False,
            "matter_mismatch": True,
            "matter_family": family,
            "message": f"{head} {waits}",
            "diplomatic_dialogue": dialogue,
            "awaiting_diplomatic_response": True,
        }
    return None


def _starts_with_article(sentence: str) -> bool:
    """True for a sentence whose capital is only the article's ("The
    Kingdom of Italy's…") — the one case a mid-sentence join lowercases."""
    return str(sentence or "").startswith("The ")


def _mailbox_item_family_noun(item: dict) -> str:
    """P4-5: the family noun of one mailbox row — what the player would
    call it — or "" for an ordinary letter."""
    from backend.game_logic.vassal import CLIENT_PETITION_TYPE

    item_type = str(item.get("item_type") or "")
    proposal_type = str(item.get("proposal_type") or "")
    if (item_type == "ally_settlement_petition"
            or proposal_type == CLIENT_PETITION_TYPE):
        return "petition"
    if item_type == "incoming_ultimatum" or proposal_type == "ultimatum":
        return "ultimatum"
    if item_type == "incoming_settlement_offer":
        return "settlement offer"
    return ""


def _queued_court_summary(world, courts: List[str]) -> tuple:
    """`("Portugal's matter waits in the letter-book", "the letter-book",
    "it")` — the sentence, the place, the pronoun — but only if it genuinely
    does; `("", "", "it")` otherwise.

    Pass 2 (P4-5): a queued PETITION (or ultimatum, or settlement offer) is
    named by its family noun and by where the client actually shows it —
    the top bar's **Envoys** button — so the court guard and the matter
    guard say the same thing about the same mailbox row ("Switzerland's
    petition waits in Envoys"); the court carries its article ("the Kingdom
    of Italy's petition"). An ordinary letter keeps the letter-book copy.
    """
    from backend.display_names import display_nation, with_definite_article

    manager = getattr(world, "dialogue_manager", None)
    if manager is None or not hasattr(manager, "get_mailbox_items"):
        return ("", "", "it")
    try:
        items = manager.get_mailbox_items() or []
    except Exception:
        return ("", "", "it")
    hits = [
        item for item in items
        if str(item.get("source_nation") or "") in courts
        and str(item.get("state") or "") != "ACTIVE"
    ]
    if not hits:
        return ("", "", "it")
    names = sorted({with_definite_article(display_nation(str(h.get("source_nation"))))
                    for h in hits})
    subject = " and ".join(names)
    subject = subject[:1].upper() + subject[1:]
    several = len(names) > 1
    verb = "wait" if several else "waits"
    nouns = {_mailbox_item_family_noun(h) for h in hits}
    if nouns == {""}:
        noun, place = "matter", "the letter-book"
    else:
        noun = nouns.pop() if len(nouns) == 1 else "matter"
        noun = noun or "matter"
        place = "Envoys"
    if several:
        noun += "s"
    return (f"{subject}'s {noun} {verb} in {place}", place,
            "them" if several else "it")
