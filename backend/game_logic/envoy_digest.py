"""IGR-F — "The small courts write one letter, not five".

The lesser courts of Europe send a relentless drip of routine asks (open
borders, non-aggression, a gift of friendship). Each one used to arrive as
its own blocking modal, chained one after another as the player answered,
which flattened the best per-nation writing in the game into noise.

This module owns ONE derived view — the letter-book — and the predicate
that decides what belongs in it. Nothing here mutates world state: the
digest is rebuilt from the dialogue manager on every response, exactly the
way IGR-B rebuilt the collapsed campaign log at the view layer.

Two hard boundaries, both pinned:

* **Great-power traffic is untouched.** A major court's ask keeps its own
  modal, whatever its type.
* **Consequential traffic is untouched.** A minor court suing for peace
  arrives on the *identical* ``incoming_proposal`` dtype as its open-borders
  request, so the tier test alone is not enough — the type allowlist is
  what keeps a peace offer, an armistice, an alliance, a design purchase or
  a neutrality compact out of the letter-book.
"""
from typing import Dict, List, Optional

# The routine families — a POSITIVE allowlist, never a denylist. A denylist
# would silently admit every future P-rung label into the letter-book.
#
# `opportunistic` is deliberately EXCLUDED: it reads as a non-aggression
# pact but DEMANDS 100 gold per turn in perpetuity (ai_diplomacy
# `_build_proposal_terms`), which is not routine mail. Promoting it needs a
# written decision, not a quiet edit.
ROUTINE_DIGEST_TYPES = frozenset({
    "open_borders",
    "non_aggression",
    "friendly_gift",
})

# The dtype the letter-book batches. Ultimatums, counter-offers, settlement
# offers and ally petitions are distinct literal dtypes with their own
# producers and their own surfaces — excluding them is an equality test, not
# a heuristic.
DIGEST_DIALOGUE_TYPE = "incoming_proposal"


def is_routine_small_court(dialogue: Optional[Dict], world) -> bool:
    """True when this dialogue is a routine letter from a lesser court.

    The conjunction is load-bearing in all three clauses:

    1. ``type == "incoming_proposal"`` — excludes ultimatums, counter-offers,
       settlement offers and ally petitions by exact equality.
    2. ``context["proposal_type"]`` in the allowlist — this is the STABLE
       P-rule label. ``terms["type"]`` is deliberately REWRITTEN downstream
       (``harsh_peace`` -> ``peace``, ``design_purchase`` -> ``open_borders``,
       ``sell_neutrality`` -> ``non_aggression``), so keying on the terms
       would batch a province cession and a binding neutrality compact as
       routine mail. The same trap already broke the rejection cooldown once
       and is documented at the dialogue builder.
    3. the sender is not a great power — ``target_nation`` on an incoming
       proposal IS the sending court. ``get_power_tier`` returns ``None`` for
       an unauthored tag, so the ``secondary`` default is applied here rather
       than assumed; that keeps a newly-minted carve client resolving to a
       small court instead of falling out of the predicate entirely.
    """
    if not isinstance(dialogue, dict):
        return False
    if dialogue.get("type") != DIGEST_DIALOGUE_TYPE:
        return False
    context = dialogue.get("context") or {}
    if context.get("proposal_type") not in ROUTINE_DIGEST_TYPES:
        return False

    from backend.nation_config import _POWER_TIER_DEFAULT

    nation = dialogue.get("target_nation") or context.get("source_nation") or ""
    if not nation:
        return False
    tier = world.get_power_tier(nation) or _POWER_TIER_DEFAULT
    # `!= "major"` — spelled as the existing ai_diplomacy idiom. It must NOT
    # be `== "minor"`: the Ottoman court is authored `secondary`, and Reis
    # Efendi's voice is one of the two the review named as being flattened.
    return tier in ("minor", "secondary")


def _digest_row(dialogue: Dict, world, *, is_active: bool) -> Dict:
    """Project one dialogue into a letter-book row.

    Everything the row renders already exists on the dialogue's own
    ``popup_payload`` — including ``diplomat_line``, the per-nation spoken
    line in the Voice Bible register that this slice exists to protect.
    Raw nation tags are preserved: the client repairs them through
    ``Utils.humanize_nation_keys_in_text`` / ``display_nation_name``, and
    baking a static display name here is the NA-6 stage-3 dead-name hazard.
    """
    from backend.display_names import proposal_display_name
    from backend.nation_config import _POWER_TIER_DEFAULT

    context = dialogue.get("context") or {}
    payload = dialogue.get("popup_payload") or {}
    nation = dialogue.get("target_nation") or context.get("source_nation") or ""
    proposal_type = str(context.get("proposal_type", ""))

    # PT-D3 (Aug-1 re-measure): the row TITLE follows the terms the letter
    # actually carries. A friendly_gift at relation < 0 is rewritten into an
    # open_borders proposal downstream, so titling the row "Gift of
    # Friendship" above a lead clause reading "Proposal: Open Borders
    # Agreement" contradicts the row's own body. The payload's
    # proposal_type_display is terms-derived (mailbox_payloads builds it
    # from terms["type"]); the STABLE context label stays on
    # `proposal_type` untouched — the batching predicate keys on it.
    title = str(payload.get("proposal_type_display", "") or "") \
        or proposal_display_name(proposal_type)

    return {
        "mailbox_id": int(dialogue.get("mailbox_id", 0)),
        "dialogue_id": int(dialogue.get("dialogue_id", -1)),
        "from_nation": nation,
        "power_tier": world.get_power_tier(nation) or _POWER_TIER_DEFAULT,
        "proposal_type": proposal_type,
        "proposal_type_display": title,
        "diplomat_name": str(payload.get("diplomat_name", "")),
        "diplomat_line": str(payload.get("diplomat_line", "")),
        "clauses": list(payload.get("clauses", [])),
        "acceptance_hint": str(payload.get("acceptance_hint", "")),
        "state": "ACTIVE" if is_active else "WAITING",
        "arrival_turn": int(dialogue.get("turn_created", 0)),
    }


def collect_routine_small_court_dialogues(world) -> List[Dict]:
    """Every pending routine small-court dialogue, active slot first.

    Order matches the mailbox panel's own contract (active row first, then
    the queue in its promotion order) so the letter-book and the inbox never
    disagree about which letter is on top.
    """
    dm = world.dialogue_manager
    found = []
    current = dm.peek()
    if is_routine_small_court(current, world):
        found.append(current)
    for queued in dm.iter_queue():
        if is_routine_small_court(queued, world):
            found.append(queued)
    return found


def _headline(world, count: int, nations: List[str]) -> str:
    """Name the courts when there are few enough to name, count them when not.

    Same discipline as IGR-B's collapsed refusal line: lose nothing first,
    then fall back to a true number.

    Names resolve through `formations.formed_display_name`, NOT the bare
    camelCase splitter. The splitter knows nothing about NA-6 formations, so
    it baked a DEAD NAME the client could never repair — the repair pass
    matches on the still-raw tag, and a headline that already reads
    "Kingdom Of Italy" no longer contains one. It also disagreed with the row
    label twenty pixels below it, which does resolve correctly: the Ottoman
    rendered as "Ottoman" in the sentence and "Ottoman Empire" on the row,
    with no formation involved at all. This is the same helper the arrival
    notification for this very delivery already uses.
    """
    from backend.game_logic.formations import formed_display_name

    names = [formed_display_name(world, n) for n in nations]
    if count == 1:
        return f"{names[0]} writes."
    if count <= 3:
        listed = ", ".join(names[:-1]) + f" and {names[-1]}"
        return f"{listed} write."
    return f"{count} of the lesser courts write."


def build_envoy_digest(world) -> Optional[Dict]:
    """The letter-book payload, or ``None`` when no small court has written.

    Pure: reads the dialogue manager and returns a fresh dict. Called from
    ``build_base_response`` so it rides every gameplay response and can never
    go stale against the queue it describes.
    """
    dialogues = collect_routine_small_court_dialogues(world)
    if not dialogues:
        return None

    dm = world.dialogue_manager
    current = dm.peek()
    items = [
        _digest_row(d, world, is_active=(d is current))
        for d in dialogues
    ]
    count = len(items)
    # IGR-F review [7]: the noun follows the roster, not the slice's working
    # title. `!= "major"` deliberately includes the secondary courts — Spain,
    # the Ottomans, Sweden, Naples — and calling the Porte a "small court" in
    # a header is a different claim from batching its routine mail.
    all_minor = all(i["power_tier"] == "minor" for i in items)
    return {
        "turn": int(world.current_turn),
        "count": count,
        "title": (
            ("THE SMALL COURTS WRITE" if all_minor else "THE COURTS WRITE")
            if count > 1
            else ("A SMALL COURT WRITES" if all_minor else "A COURT WRITES")
        ),
        # Deliberately NOT `pending_envoy_count`: that counts persistent
        # settlement offers and ally petitions too, which do NOT lapse. Every
        # row in this list is a CURRENT_TURN_OFFER_TYPES item, so this number
        # is the honest size of the deadline.
        "lapsing_count": count,
        "headline": _headline(world, count, [i["from_nation"] for i in items]),
        # One turn, no grace — `lapse_pending_offers` is the first statement
        # of end_turn. And an ignored ask carries a silent 6-turn per-type
        # cooldown, which the player has never been told about.
        "deadline_note": (
            "Answer them here. Unanswered letters lapse when the turn ends, "
            "and a court left waiting will not raise the matter again for "
            "some seasons."
        ),
        "items": items,
    }


# ═══════════════════════════════════════════════════════════════════════════
# S14E-27 (S14f part 2, October 25, 2026) — what a row of the Envoys panel says
#
# The panel gave every row the same card: a one-line summary cut at 72
# characters and a word "Open ▸". A letter-book row (above) carries its
# court's voice and terms and answers in place; every OTHER row opens its
# letter in full and said nothing of why, nor of what it asks. These two
# readers give the row what the popup will show: the letter's terms (the
# popup's own `clauses`, never a second rendering) and ONE line saying why
# the row opens in full. The boundary above is read, not moved: a row is
# inline exactly when `is_routine_small_court` says so, and an inline row
# needs no reason.
# ═══════════════════════════════════════════════════════════════════════════

# The dialogue types whose popup carries terms to show on the row.
_TERMS_ROW_TYPES = frozenset({
    "incoming_proposal", "counter_offer", "counter_offer_response",
    "incoming_ultimatum",
})

ROW_REASON_GREAT_COURT = ("A great court's letter is answered in full "
                          "— open to accept, haggle or refuse.")
ROW_REASON_TREATY = "A treaty is answered in full — open to accept, haggle or refuse."
ROW_REASON_PETITION = "A client's petition is granted or refused in full — open to decide."
ROW_REASON_CALL_TO_ARMS = "An ally's call to arms is joined or refused in full — open to answer."
ROW_REASON_MOMENT = "A moment of history is answered in full — open the letter to choose."
ROW_REASON_ULTIMATUM = "An ultimatum is yielded to or defied in full — open to answer."
ROW_REASON_COUNTER = ("A counter-offer is accepted or rejected in full "
                      "— open to read the revised terms.")
ROW_REASON_SETTLEMENT = "A settlement offer is answered in full — open to review its terms."
ROW_REASON_ALLY_PETITION = "An ally's petition is answered in full — open to read it and reply."


def mailbox_row_terms(dialogue: Optional[Dict]) -> List[str]:
    """The terms a mailbox row shows: the popup payload's own `clauses` (the
    lines `build_proposal_popup_clauses` / the petition builders wrote and
    the popup prints), as plain strings. [] for a row with no terms to show
    — a moment letter (its record is the letter), a settlement, an ally's
    petition."""
    if not isinstance(dialogue, dict):
        return []
    if str(dialogue.get("type") or "") not in _TERMS_ROW_TYPES:
        return []
    from backend.game_logic.moments import is_moment_letter
    if is_moment_letter(dialogue):
        return []
    payload = dialogue.get("popup_payload") or {}
    clauses = payload.get("clauses") if isinstance(payload, dict) else None
    if not isinstance(clauses, list):
        return []
    return [str(c) for c in clauses if str(c).strip()]


def mailbox_row_reason(dialogue: Optional[Dict], world) -> str:
    """One line saying why a mailbox row opens its letter in full; "" for a
    row that answers in place (a letter-book row), for a row of no known kind
    and when no world is given (the tier of the sender is the world's)."""
    if not isinstance(dialogue, dict) or world is None:
        return ""
    dtype = str(dialogue.get("type") or "")
    if dtype == "incoming_settlement_offer":
        return ROW_REASON_SETTLEMENT
    if dtype == "ally_settlement_petition":
        return ROW_REASON_ALLY_PETITION
    if dtype == "incoming_ultimatum":
        return ROW_REASON_ULTIMATUM
    if dtype in ("counter_offer", "counter_offer_response"):
        return ROW_REASON_COUNTER
    if dtype != DIGEST_DIALOGUE_TYPE:
        return ""
    from backend.game_logic.call_to_arms import is_call_to_arms
    from backend.game_logic.moments import is_moment_letter
    from backend.game_logic.vassal import is_client_petition
    if is_moment_letter(dialogue):
        return ROW_REASON_MOMENT
    if is_client_petition(dialogue):
        return ROW_REASON_PETITION
    if is_call_to_arms(dialogue):
        return ROW_REASON_CALL_TO_ARMS
    if is_routine_small_court(dialogue, world):
        return ""   # a letter-book row: answered in place, no reason owed
    from backend.nation_config import _POWER_TIER_DEFAULT
    context = dialogue.get("context") or {}
    nation = dialogue.get("target_nation") or context.get("source_nation") or ""
    tier = (world.get_power_tier(nation) if nation else None) or _POWER_TIER_DEFAULT
    return ROW_REASON_GREAT_COURT if tier == "major" else ROW_REASON_TREATY
