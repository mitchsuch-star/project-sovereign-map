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

    return {
        "mailbox_id": int(dialogue.get("mailbox_id", 0)),
        "dialogue_id": int(dialogue.get("dialogue_id", -1)),
        "from_nation": nation,
        "power_tier": world.get_power_tier(nation) or _POWER_TIER_DEFAULT,
        "proposal_type": proposal_type,
        "proposal_type_display": proposal_display_name(proposal_type),
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


def _headline(count: int, nations: List[str]) -> str:
    """Name the courts when there are few enough to name, count them when not.

    Same discipline as IGR-B's collapsed refusal line: lose nothing first,
    then fall back to a true number.
    """
    from backend.display_names import humanize_entity_name

    names = [humanize_entity_name(n) for n in nations]
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
    return {
        "turn": int(world.current_turn),
        "count": count,
        # Deliberately NOT `pending_envoy_count`: that counts persistent
        # settlement offers and ally petitions too, which do NOT lapse. Every
        # row in this list is a CURRENT_TURN_OFFER_TYPES item, so this number
        # is the honest size of the deadline.
        "lapsing_count": count,
        "headline": _headline(count, [i["from_nation"] for i in items]),
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
