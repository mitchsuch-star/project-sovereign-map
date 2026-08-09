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

# ── The verb→action table, lifted verbatim out of
# `handle_diplomatic_dialogue_response` so the gate in main.py and the
# resolver in the executor cannot disagree about what a word means.
# Order within a list matters: it is tried in order (e.g. "accept" tries
# the AI-proposal accept before the player-proposal send).
DIALOGUE_ACTION_KEYWORDS: Dict[str, List[str]] = {
    "dismiss": ["dismiss"],
    "cancel": ["cancel_pushback", "cancel_mission", "dismiss"],
    "never mind": ["dismiss"],
    "nudge": ["accept_nudge"],
    "insist": ["insist_original"],
    "send": ["send_override", "send", "execute_proposal"],
    "confirm": ["confirm_settlement", "send_override", "execute_proposal",
                "force_declare_war"],
    "ratify": ["confirm_settlement"],
    # W6-9: execute_suggestion rides LAST in each list — it only wins on
    # the advisory dialogue, whose only other option is dismiss.
    "proceed": ["confirm_settlement", "send_override", "execute_proposal",
                "force_declare_war", "execute_suggestion"],
    "do it": ["execute_suggestion"],
    "yes": ["confirm_settlement", "execute_proposal", "accept_ai_proposal",
            "accept_ai_ultimatum", "force_declare_war", "execute_suggestion"],
    "reconsider": ["back_out_settlement", "reconsider"],
    "no": ["back_out_settlement", "reconsider"],
    "wait": ["reconsider"],
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


def format_numbered_options(dialogue: Optional[dict]) -> str:
    """CA9-N5: ``1=Conquest, 2=Forced Alliance, 3=Back Out`` — a live
    dialogue's own option list, read off the dialogue rather than
    re-described."""
    labels = [str(o.get("label", "?")) for o in dialogue_options(dialogue)]
    return ", ".join(f"{i + 1}={label}" for i, label in enumerate(labels))


def _whole_phrase_in(phrase: str, text: str) -> bool:
    """Word-boundary containment. `no` must not match "north", and
    `start` must not match "restart" — the bare-substring scan is exactly
    how ordinary orders were eaten as dialogue answers."""
    return re.search(
        r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])", text) is not None


def match_dialogue_answer(dialogue: Optional[dict],
                          raw_lower: str) -> Optional[str]:
    """Return the token to hand the response handler, or None if this
    typed line is not an answer to THIS dialogue.

    Only the dialogue's own options may claim a line:
      1. a full option label, or its action id, appearing in the text
      2. every word of a label appearing in the text ("reject THE offer")
      3. a verb keyword — as a WHOLE WORD, and only when it maps onto an
         action this dialogue actually offers
    """
    options = dialogue_options(dialogue)
    if not options:
        return None
    raw_words = set(re.findall(r"[a-z]+", raw_lower))
    for opt in options:
        label = (opt.get("label") or "").lower().strip()
        action = (opt.get("action") or "").lower().strip()
        if label and label in raw_lower:
            return label
        if action and action in raw_lower:
            return action
        label_words = set(re.findall(r"[a-z]+", label))
        if label_words and label_words <= raw_words:
            return action or label
    offered = {str(o.get("action") or "") for o in options}
    for keyword, actions in DIALOGUE_ACTION_KEYWORDS.items():
        if not _whole_phrase_in(keyword, raw_lower):
            continue
        if any(a in offered for a in actions):
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
