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
    # FA-N2: read what the player still MEANS, not what they typed. A
    # negated clause is blanked before any arm below sees it, so a refusal
    # can never be matched as the consent it negates. See
    # `text_the_player_still_means`.
    raw_lower = text_the_player_still_means(raw_lower, options)
    raw_words = set(re.findall(r"[a-z]+", raw_lower))
    addressed = addresses_a_marshal(raw_lower, marshal_names)

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
        # Aug 30, 2026 review: arm 1 is bare-substring containment, so a
        # ONE-WORD label is as loose as the keyword scan below — measured, the
        # label `Cancel` claimed "cancel the march", an order to break a
        # standing move, and the executor never saw it. Same rule as arms 3
        # and 4: an answer names the decision, an order names the war.
        if label and label in raw_lower:
            if _carries_military_content(raw_lower, label, world_regions,
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
        if label_words and label_words <= raw_words:
            # Aug 30, 2026 review: the same order-vs-answer rule as arm 4.
            # A ONE-WORD label makes this arm as loose as a bare-substring
            # scan — measured, the label `Cancel` claimed "cancel the march",
            # an order to break a standing move, and the executor never saw
            # it.
            if _carries_military_content(raw_lower, label, world_regions,
                                         dialogue):
                continue
            return action or label

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
        if _carries_military_content(raw_lower, keyword, world_regions,
                                     dialogue):
            continue
        return keyword
    return None


# ══════════════════════════════════════════════════════════════════════
# Which court is on the table, and which court did the player name?
# ══════════════════════════════════════════════════════════════════════

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

    from backend.display_names import display_nation

    active_display = display_nation(active)
    named_display = " and ".join(display_nation(n) for n in addressed)

    waiting = _queued_court_summary(world, addressed)
    if waiting:
        tail = (
            f" {waiting} — open the letter-book and answer it there."
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


def _queued_court_summary(world, courts: List[str]) -> str:
    """"Portugal's proposal waits in the letter-book" — but only if it
    genuinely does."""
    from backend.display_names import display_nation

    manager = getattr(world, "dialogue_manager", None)
    if manager is None or not hasattr(manager, "get_mailbox_items"):
        return ""
    try:
        items = manager.get_mailbox_items() or []
    except Exception:
        return ""
    hits = [
        item for item in items
        if str(item.get("source_nation") or "") in courts
        and str(item.get("state") or "") != "ACTIVE"
    ]
    if not hits:
        return ""
    names = sorted({display_nation(str(h.get("source_nation")))
                    for h in hits})
    subject = " and ".join(names)
    verb = "waits" if len(names) == 1 else "wait"
    return f"{subject}'s matter {verb} in the letter-book"
