"""
AI Diplomatic Proposal System — Phase 8 Session 4

Generates, queues, and delivers AI-initiated diplomatic proposals to the player.
All functions are pure/deterministic — no LLM calls.

Entry points:
  - process_diplomatic_phase(nation, world) → Optional[Dict]
      Evaluates whether an AI nation should propose a treaty to France.
      Runs ONCE per AI nation per turn, BEFORE the Morning Dispatch.

  - deliver_ai_proposal(proposal, world) → Dict
      Sets up world.pending_diplomatic_dialogue for an incoming AI proposal.

  - generate_counter_offer(proposal, world) → Optional[Dict]
      M3 counter-offer algorithm (§9b): deterministic clause adjustment.

  - check_alliance_conflict(nation, new_state, world) → Optional[Dict]
      §5b.3 conflicting alliance check.

Design principles:
  - Uses calculate_acceptance() from diplomacy.py — NEVER re-implements the formula.
  - All numeric values int()-wrapped for Godot.
  - Anti-spam: cooldowns, queue limits, max 1 proposal delivered per turn.
  - Deferred triggers (P3, P5, P6) return None — wired in future sessions.
"""

import copy
from typing import Dict, List, Optional

from backend.game_logic.diplomacy import (
    calculate_acceptance,
    determine_ai_offer_decision_reason,
    get_war_score_for,
)
from backend.game_logic.diplomatic_dialogue import get_game_bucket
from backend.game_logic.mailbox_payloads import build_pending_envoy_popup_from_terms


# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════

# Anti-spam cooldown durations (turns)
NATION_REJECTION_COOLDOWN = 3   # After rejection, nation can't propose for N turns
# W6-10 anti-monotony (blessed 6, band 4-10): after a proposal of type T
# from nation N lapses OR is rejected, N may not re-propose T for N turns
# (live audit: five identical open-borders proposals in five turns).
TYPE_REJECTION_COOLDOWN = 6     # After rejection of type X, same type can't be proposed for N turns
TYPE_LAPSE_COOLDOWN = 6         # After type X lapses unanswered, same block applies
NATION_ACCEPTANCE_COOLDOWN = 2  # After acceptance, nation can't propose for N turns
QUEUE_MAX_SIZE = 3              # Maximum queued proposals
QUEUE_EXPIRY_TURNS = 3          # Queued proposals expire after N turns

# R126: Urgent re-proposal when situation changes drastically
URGENT_REPROPO_DELTA = 20       # War score drop of 20+ bypasses nation cooldown

# NA-5 §8 (R162): the AI ultimatum rung — "satisfy their design or fight".
# Fires between P7 opportunism and P8 for a court whose active ACQUIRE
# design targets player-bloc soil while its army towers over the player's.
# Balance numbers in-band tunable; structure escalates to a gate.
AI_ULTIMATUM_STRENGTH_RATIO = 1.25   # fog-free national strength gate (ledger basis)
AI_ULTIMATUM_COOLDOWN_TURNS = 15     # per-nation re-issue cooldown (set at ISSUE)

# AUD-b (8.EVAL Batch Q, July 16 2026): the P2 "stalemate" armistice used to
# fire purely on turns-since-war-start with NO combat requirement, so an entire
# coalition would sue for peace by turn ~5-7 having never fought a battle. The
# stalemate exit now requires the pair to have actually FOUGHT (>=1 war-score
# battle recorded in world.battle_records for the pair). A genuinely contactless
# war (declared, never engaged) still gets an eventual exit — but only after a
# much longer patience window, so it never pre-empts real combat. Balance number
# (escalates to the gate): 15 turns before a never-fought war may sue.
P2_NO_CONTACT_ESCAPE_TURNS = 15

# ═══════ AI-2 (AI_INTENT_SPEC §4.2) — the intent-driven rungs ═══════
# Blessed numbers, in-band tunable; structure escalates.
#
# §4.2c THE DELIVERY BUDGET: intent asks carry their OWN world-wide
# per-turn budget, sized so the §4.2b marquee case — BOTH belligerents
# of a third-party war courting France in the same turn — can never be
# starved by an unrelated bandwagon flood (turn_manager's
# MAX_BANDWAGON_PER_TURN never counts an intent ask, and vice versa).
# The §4.2c carve on `_has_pending_proposal_from`, decided in writing:
# the one-live-proposal-per-SOURCE gate STANDS — a court with mail in
# transit does not double-court; the budget sizing (2 = two courts per
# turn) is what protects the marquee case, which is two DIFFERENT
# sources by construction.
INTENT_ASK_BUDGET_PER_TURN = 2
DESIGN_PURCHASE_BASE = 400        # gold offered for a coveted province...
DESIGN_PURCHASE_PER_WEIGHT = 8    # ...plus per point of design weight
DESIGN_PURCHASE_TREASURY_FRACTION = 0.5   # never offer more than half the chest
SELL_NEUTRALITY_BASE = 250        # lump floor for buying France's neutrality
SELL_NEUTRALITY_TREASURY_FRACTION = 0.25
AI_SPONSOR_MIN_TREASURY = 1500    # a sponsor-first court needs a real purse
AI_SPONSORSHIPS_PER_TURN = 1      # narration budget: one new patron per turn

# §12.6 — THE ALLEGIANCE AUCTION (AI-2d's Stage C half): when a minor's
# bandwagon readiness crests, the flip is announced as IN PLAY and both
# sides may bid through the same D5 instruments before it resolves by
# lean + the standing offers. Bavaria, September 1805 — courted by both
# empires, signed at Bogenhausen. Blessed numbers, in-band tunable.
ALLEGIANCE_AUCTION_WINDOW = 3     # turns between the announcement and the flip
AUCTION_SPONSORSHIP_LEAN_DIVISOR = 10  # 10g/turn of standing patronage = 1 lean point

# Per-nation desire table for counter-offers (§9b)
# Ordered by preference (most desired first).
#
# DESIGN NOTE: Despite the name, this table describes what each nation is
# willing to OFFER as additional sweeteners to France in a counter-offer
# scenario. When France counter-offers, _try_add_desired_clauses picks from
# this table and adds items as sweeteners (proposer → target = AI → France),
# which increases France's acceptance score toward the ≥50 threshold.
# This is intentional — the M3 algorithm optimizes for France's acceptance.
## NA-2 (§5.2): the dead "territory" rows are DELETED — unreachable since the
## July-2026 AI audit removed the territory branch from _try_add_desired_clauses
## (see the design note there); live territorial desire now flows from the
## agenda substrate (agendas.get_agenda_covets), with these profiles as the
## non-territorial counter-offer vocabulary.
NATION_DESIRES = {
    "Prussia": [
        {"type": "gold_lump", "value": 500,
         "description": "Gold lump sum"},
    ],
    "Austria": [
        {"type": "open_borders", "value": 1, "clause": "open_borders",
         "description": "Open borders"},
        {"type": "protection", "value": 1, "clause": "protection_promised",
         "description": "Protection guarantee"},
        {"type": "gold_per_turn", "value": 100,
         "description": "Gold per turn"},
    ],
    "Britain": [
        {"type": "gold_lump", "value": 800,
         "description": "Gold lump sum (Continental System lifted)"},
        {"type": "gold_lump", "value": 500,
         "description": "Gold lump sum"},
    ],
    "Saxony": [
        {"type": "protection", "value": 1, "clause": "protection_promised",
         "description": "Protection guarantee"},
        {"type": "gold_per_turn", "value": 50,
         "description": "Gold per turn"},
    ],
}

# R115: Personality-driven AI proposal modifiers
# hawk: demands more gold, stricter peace threshold (won't sue for peace easily)
# schemer: patient (waits longer before stalemate proposals)
# dove: demands less gold, sues for peace earlier
# loyalist: baseline behavior (no modifiers)
PERSONALITY_PROPOSAL_MODIFIERS = {
    "hawk":     {"gold_demand_mult": 1.5, "peace_threshold_delta": -20, "patience_bonus": 0},
    "schemer":  {"gold_demand_mult": 1.0, "peace_threshold_delta": 0,   "patience_bonus": 2},
    "dove":     {"gold_demand_mult": 0.75, "peace_threshold_delta": 20, "patience_bonus": 0},
    "loyalist": {"gold_demand_mult": 1.0, "peace_threshold_delta": 0,   "patience_bonus": 0},
}


def _get_personality_modifiers(nation: str, world) -> Dict:
    """R115: Get proposal modifiers based on diplomat personality."""
    diplomats = getattr(world, 'diplomats', {})
    diplomat = diplomats.get(nation)
    personality = getattr(diplomat, 'personality', 'loyalist') if diplomat else 'loyalist'
    return PERSONALITY_PROPOSAL_MODIFIERS.get(personality, PERSONALITY_PROPOSAL_MODIFIERS["loyalist"])


# R125: Personality-driven counter-offer acceptance/rejection thresholds
# hawk: harder to please (accept at 60, reject below 35)
# dove: easier to please (accept at 40, reject below 25)
# schemer/loyalist: baseline (accept at 50, reject below 30)
PERSONALITY_COUNTER_THRESHOLDS = {
    "hawk":     {"accept": 60, "floor": 35},
    "dove":     {"accept": 40, "floor": 25},
    "schemer":  {"accept": 50, "floor": 30},
    "loyalist": {"accept": 50, "floor": 30},
}


# Talleyrand's assessment strings keyed by (proposal_type_category, game_bucket_category)
TALLEYRAND_ASSESSMENTS = {
    ("armistice", "losing"):
        "They are desperate, Sire. We could demand far more.",
    ("armistice", "stalemate"):
        "Neither side gains from continued bloodshed. A pragmatic choice.",
    ("peace", "winning"):
        "They sue for peace from a position of weakness. We hold the cards.",
    ("peace", "losing"):
        "They offer peace while we struggle. Perhaps wisdom lies in accepting.",
    ("peace", "stalemate"):
        "A measured end to an inconclusive war. The terms will tell the tale.",
    ("upgrade", "friendly"):
        "A natural progression. This arrangement serves our interests.",
    ("upgrade", "neutral"):
        "An unexpected overture. There may be hidden motives worth examining.",
    ("opportunistic", "any"):
        "They sense our distraction and seek to capitalize. Tread carefully.",
}


def _get_talleyrand_assessment(proposal_type: str, game_bucket: str) -> str:
    """Look up Talleyrand's assessment for a proposal type and game situation."""
    # Map proposal types to categories
    if proposal_type in ("armistice", "armistice_losing", "armistice_winning"):
        type_cat = "armistice"
    elif proposal_type == "peace":
        type_cat = "peace"
    elif proposal_type in ("non_aggression", "open_borders",
                           "defensive_alliance", "alliance"):
        type_cat = "upgrade"
    else:
        type_cat = proposal_type

    # Map game buckets to categories
    if game_bucket in ("losing_slightly", "losing_badly"):
        bucket_cat = "losing"
    elif game_bucket in ("winning_slightly", "winning_comfortably"):
        bucket_cat = "winning"
    elif game_bucket == "stalemate":
        bucket_cat = "stalemate"
    elif game_bucket == "friendly":
        bucket_cat = "friendly"
    elif game_bucket == "neutral":
        bucket_cat = "neutral"
    else:
        bucket_cat = "any"

    # Try exact match first, then with "any" bucket
    text = TALLEYRAND_ASSESSMENTS.get((type_cat, bucket_cat))
    if text is None:
        text = TALLEYRAND_ASSESSMENTS.get((type_cat, "any"))
    if text is None:
        text = "An interesting proposal. I shall study the terms closely."

    return text


# ═══════════════════════════════════════════════════════════════
# ANTI-SPAM HELPERS
# ═══════════════════════════════════════════════════════════════

def _get_cooldowns(world) -> Dict[str, int]:
    """Safely get ai_proposal_cooldowns from world."""
    return getattr(world, 'ai_proposal_cooldowns', {})


def _set_cooldowns(world, cooldowns: Dict[str, int]) -> None:
    """Safely set ai_proposal_cooldowns on world."""
    world.ai_proposal_cooldowns = cooldowns


def _get_queue(world) -> List[Dict]:
    """DEPRECATED: diplomatic_queue eliminated. Returns empty list for compat."""
    return []


def _set_queue(world, queue: List[Dict]) -> None:
    """DEPRECATED: diplomatic_queue eliminated. No-op."""
    pass


def _is_situation_urgent(nation: str, war_score: int, world) -> bool:
    """R126: Check if war situation has changed drastically since last proposal.

    Returns True if war_score has dropped by URGENT_REPROPO_DELTA or more
    since the nation's last proposal.
    """
    metadata = getattr(world, 'ai_proposal_metadata', {})
    prev = metadata.get(nation)
    if not prev:
        return False
    prev_war_score = prev.get("war_score_at_proposal", 0)
    return (prev_war_score - war_score) >= URGENT_REPROPO_DELTA


def _cooldown_keys(nation: str, proposal_type: str, world,
                   recipient: str = None) -> tuple:
    """(nation_key, type_key) for the ask cooldown store.

    AI-2a (§4.2 seam 4): cooldowns are keyed to an ORDERED
    (proposer, recipient) pair — never `_make_diplo_key`, which sorts and
    would collapse "Prussia asks Austria" with "Austria asks Prussia".
    The migration is built into the key semantics: the legacy
    `{nation}|...` format IS the recipient=player arm (byte-identical for
    every existing save and test), and only a non-player recipient uses
    the explicit `{proposer}>{recipient}|...` form. (The R43
    `ai_ai|{sorted pair}` RATIFY cooldown stays symmetric by decision — a
    fresh treaty blocks rapid re-upgrade in either direction.)
    """
    player = getattr(world, 'player_nation', 'France')
    if recipient is None or recipient == player:
        return f"{nation}|nation", f"{nation}|{proposal_type}"
    return (f"{nation}>{recipient}|nation",
            f"{nation}>{recipient}|{proposal_type}")


def _is_on_cooldown(nation: str, proposal_type: str, world,
                    war_score: int = 0, recipient: str = None) -> bool:
    """Check if a nation or proposal type is on cooldown.

    R126: If war_score is provided and situation is urgent (war score dropped
    by 20+ since last proposal), bypass the nation cooldown. Type cooldown
    still applies.
    """
    cooldowns = _get_cooldowns(world)
    nation_key, type_key = _cooldown_keys(nation, proposal_type, world,
                                          recipient)

    if cooldowns.get(nation_key, 0) > 0:
        # R126: Bypass nation cooldown if situation is urgent
        # AI-2 §4.2c: the OPPORTUNISM valve — §3.2's marquee promise is
        # that willingness rises precisely when the design's obstacle is
        # committed elsewhere; a nation cooldown must not eat that
        # moment. A design-family intent ask while the obstacle fights
        # on two fronts bypasses the NATION cooldown exactly as a
        # war-score collapse does (the URGENT_REPROPO idiom). The TYPE
        # cooldown still applies — the anti-monotony governor stands.
        opportune = False
        if proposal_type in ("design_purchase", "sell_neutrality"):
            from backend.game_logic.intent import get_nation_intent
            view = get_nation_intent(nation, world)
            if (view.against
                    and len(world.get_nations_at_war_with(view.against))
                    >= 2):
                opportune = True
        if not opportune and not _is_situation_urgent(nation, war_score,
                                                      world):
            return True
    type_remaining = int(cooldowns.get(type_key, 0))
    if type_remaining > 0:
        # NA-2 §5.3 hawk persistence: a HAWK court re-asks an agenda-
        # advancing type sooner — the last |AGENDA_PERSISTENCE_COOLDOWN_
        # DELTA| turns of the TYPE cooldown don't block it (derived at
        # check time, so it covers rejection AND lapse cooldowns without
        # touching the stored counter). Nation cooldown is untouched;
        # doves/loyalists keep the full wait — personality stays the
        # governor (hawk persists, dove asks once).
        reduction = 0
        diplomat = getattr(world, 'diplomats', {}).get(nation)
        if getattr(diplomat, 'personality', '') == "hawk":
            from backend.game_logic.agendas import (
                AGENDA_PERSISTENCE_COOLDOWN_DELTA, ask_advances_agenda,
            )
            if ask_advances_agenda(nation, proposal_type, world):
                reduction = -int(AGENDA_PERSISTENCE_COOLDOWN_DELTA)
        if type_remaining > reduction:
            return True
    return False


def apply_rejection_cooldowns(nation: str, proposal_type: str, world, *,
                              deferred: bool = False,
                              recipient: str = None) -> None:
    """Apply cooldowns after a proposal is rejected.

    Called from executor when player rejects an AI proposal. AI-2a:
    `recipient` scopes the cooldown to the ordered (proposer, recipient)
    pair; None keeps the legacy player-addressed keys byte-identically.
    Args:
        deferred: True when called from _process_proposal_in_transit inside
                  advance_turn — adds +1 to compensate for decrement_all running
                  in the same advance_turn call.
    """
    offset = 1 if deferred else 0
    cooldowns = _get_cooldowns(world)
    nation_key, type_key = _cooldown_keys(nation, proposal_type, world,
                                          recipient)
    cooldowns[nation_key] = int(NATION_REJECTION_COOLDOWN) + offset
    cooldowns[type_key] = int(TYPE_REJECTION_COOLDOWN) + offset
    _set_cooldowns(world, cooldowns)


def apply_lapse_type_cooldown(nation: str, proposal_type: str, world,
                              recipient: str = None) -> None:
    """W6-10 anti-monotony: an offer that LAPSES unanswered blocks the same
    type from the same nation for TYPE_LAPSE_COOLDOWN turns — before this,
    only the 2-turn nation cooldown applied on lapse, so an ignored
    open-borders ask came back near-identically within two turns (live
    audit: five in five turns). Key rule: `proposal_type` must be the
    STABLE P-rule label from the dialogue context, never the rewritten
    terms["type"] (the documented trap)."""
    if not nation or proposal_type in ("", "unknown", None):
        return
    cooldowns = _get_cooldowns(world)
    _nation_key, type_key = _cooldown_keys(nation, proposal_type, world,
                                           recipient)
    cooldowns[type_key] = max(
        int(cooldowns.get(type_key, 0)), int(TYPE_LAPSE_COOLDOWN))
    _set_cooldowns(world, cooldowns)


def apply_acceptance_cooldown(nation: str, world, *, deferred: bool = False,
                              recipient: str = None) -> None:
    """Apply a short cooldown after a proposal is accepted.

    Prevents the same nation from immediately proposing the next upgrade
    on the very next turn (spam prevention).
    Args:
        deferred: True when called from _process_proposal_in_transit inside
                  advance_turn — adds +1 to compensate for decrement_all running
                  in the same advance_turn call.
    """
    offset = 1 if deferred else 0
    cooldowns = _get_cooldowns(world)
    nation_key, _type_key = _cooldown_keys(nation, "nation", world,
                                           recipient)
    cooldowns[nation_key] = max(
        int(cooldowns.get(nation_key, 0)),
        int(NATION_ACCEPTANCE_COOLDOWN) + offset,
    )
    _set_cooldowns(world, cooldowns)


# ═══════════════════════════════════════════════════════════════
# AI-2a — the refusal record (§4.2 seam 5, §5 pin 8's substrate)
# ═══════════════════════════════════════════════════════════════

# Dedupe window: the same (proposer>recipient, type) refusal is recorded
# once per this many turns — the AI-AI trigger poll re-fires every turn
# and must not spam the record or the campaign log. Blessed, in-band.
REFUSAL_DEDUPE_TURNS = 6
# Retention: refusals older than this are pruned at write time. AI-3's
# ladder gate ("cheaper instruments tried and refused") reads inside this
# window; matching the agenda-grudge horizon keeps one memory scale.
REFUSAL_MEMORY_TURNS = 12


def record_diplomatic_refusal(world, proposer: str, recipient: str,
                              proposal_type: str) -> bool:
    """Put a refused ask on the SERIALIZED record (§5 pin 8: refused asks
    must survive a save — if they were re-derived, "no cold-open wars"
    becomes a lie the moment a player loads). Ordered key
    `{proposer}>{recipient}`; entries `{"type", "turn"}`.

    Returns True when a new entry was recorded, False when deduped.
    Works on every path: player refuses an AI court, an AI court refuses
    the player, and court-to-court (the moment that did not exist before
    AI-2a).
    """
    if not proposer or not recipient or proposer == recipient:
        return False
    store = getattr(world, 'diplomatic_refusals', None)
    if store is None:
        store = {}
        world.diplomatic_refusals = store
    key = f"{proposer}>{recipient}"
    turn = int(getattr(world, 'current_turn', 0))
    entries = [e for e in (store.get(key) or [])
               if turn - int(e.get("turn", 0)) < REFUSAL_MEMORY_TURNS]
    for entry in entries:
        if (entry.get("type") == proposal_type
                and turn - int(entry.get("turn", 0)) < REFUSAL_DEDUPE_TURNS):
            store[key] = entries
            return False
    entries.append({"type": str(proposal_type), "turn": turn})
    store[key] = entries
    return True


def get_refused_asks(world, proposer: str, recipient: str) -> List[Dict]:
    """The live refusal record for an ordered pair, pruned to the memory
    window — the read AI-3's ladder gate consumes."""
    store = getattr(world, 'diplomatic_refusals', {}) or {}
    turn = int(getattr(world, 'current_turn', 0))
    return [e for e in (store.get(f"{proposer}>{recipient}") or [])
            if turn - int(e.get("turn", 0)) < REFUSAL_MEMORY_TURNS]


def _has_pending_proposal_from(nation: str, world) -> bool:
    """Check if there's already a pending proposal from this nation.

    Prevents duplicate proposals from the same nation piling up in the
    dialogue_manager queue or active slot.
    """
    dm = world.dialogue_manager

    # Check active dialogue
    current = dm.peek()
    if current:
        ctx = current.get("context", {})
        if ctx.get("source_nation") == nation:
            return True
        if current.get("target_nation") == nation and current.get("type", "") in dm.SOFT_STOP_MAILBOX_TYPES:
            return True

    # PL-5B: Check proposal_in_transit — player already has a proposal targeting this nation
    pit = getattr(world, 'proposal_in_transit', None)
    if pit and pit.get("target") == nation:
        return True

    # Check dialogue_manager queue for proposals from this nation
    for item in dm._queue:
        dtype = item.get("type", "")
        if dtype in dm.SOFT_STOP_MAILBOX_TYPES:
            ctx = item.get("context", {})
            if ctx.get("source_nation") == nation:
                return True
            if item.get("target_nation") == nation:
                return True

    return False


def _expire_queue(world) -> None:
    """DEPRECATED: diplomatic_queue eliminated. No-op for compat."""
    pass


def _enqueue_proposal(proposal: Dict, world) -> bool:
    """DEPRECATED: diplomatic_queue eliminated. All proposals now go
    through deliver_ai_proposal → dialogue_manager.push()."""
    return False


def _dequeue_best(world) -> Optional[Dict]:
    """DEPRECATED: diplomatic_queue eliminated."""
    return None


# ═══════════════════════════════════════════════════════════════
# WAR SCORE FROM AI PERSPECTIVE
# ═══════════════════════════════════════════════════════════════

def _get_war_score_for_nation(nation: str, opponent: str, world) -> int:
    """Get war score from a specific nation's perspective.

    DEPRECATED: Use get_war_score_for(world, nation, opponent) from diplomacy.py.
    Kept as thin wrapper for backward compatibility with existing callers.
    """
    return get_war_score_for(world, nation, opponent)


def _calculate_ticking_pressure(nation: str, opponent: str,
                                diplo_key: str, world) -> int:
    """WPS-D §13.2: Ticking pressure modifier for AI peace timing.

    Returns a value clamped to ±10 that shifts the AI's P1 peace threshold.
    Positive = more willing to seek peace (opponent ticking high).
    """
    war_obj_data = getattr(world, 'war_objectives', {}).get(diplo_key, {})
    opponent_obj = war_obj_data.get(opponent, {})
    own_obj = war_obj_data.get(nation, {})

    opponent_ticking = 0
    if opponent_obj and opponent_obj.get("concluded_turn") is None:
        opponent_ticking = int(opponent_obj.get("accumulated_ticking", 0))

    own_ticking = 0
    if own_obj and own_obj.get("concluded_turn") is None:
        own_ticking = int(own_obj.get("accumulated_ticking", 0))

    return max(-10, min(10, (opponent_ticking - own_ticking) // 5))


def ai_check_vassalage_power_cap(nation: str, target: str, world) -> bool:
    """WPS-D §13.3: AI hard pre-check before proposing vassalage.

    Returns True if vassalage is allowed (target under 50% of proposer's power).
    """
    from backend.game_logic.diplomacy import check_vassalage_power_cap
    result = check_vassalage_power_cap(world, nation, target)
    return result.get("allowed", False)


def ai_should_accept_liberation_peace(nation: str, opponent: str,
                                      terms: Dict, world) -> bool:
    """WPS-D §13.5: AI coalition members accept peace terms that include liberation.

    Returns True if the terms include liberation of vassals this nation's
    objective targets, False if terms leave vassals in place when the AI's
    liberation objective is active and war score supports liberation.
    """
    diplo_key = world._make_diplo_key(nation, opponent)
    war_obj_data = getattr(world, 'war_objectives', {}).get(diplo_key, {})
    obj = war_obj_data.get(nation, {})
    if not obj or obj.get("type") != "liberation":
        return True
    if obj.get("concluded_turn") is not None:
        return True

    vassal_nations_targeted = set(obj.get("vassal_nations", []))
    if not vassal_nations_targeted:
        return True

    clauses = list(terms.get("clauses", [])) + list(terms.get("demands", []))
    liberated_nations = set()
    for clause in clauses:
        if (
            isinstance(clause, dict)
            and (clause.get("clause_type") or clause.get("type")) == "liberation"
        ):
            liberated_nations.add(clause.get("vassal_nation", ""))

    war_score = get_war_score_for(world, nation, opponent)
    if war_score >= 40 and vassal_nations_targeted - liberated_nations:
        return False

    return True


# ═══════════════════════════════════════════════════════════════
# STALEMATE TRACKING
# ═══════════════════════════════════════════════════════════════

def _update_stalemate_counter(nation: str, war_score: int, world) -> int:
    """Update and return stalemate counter for a nation.

    Increments if war_score is between -10 and +10, resets otherwise.
    """
    counters = getattr(world, 'ai_stalemate_counters', {})
    if -10 <= war_score <= 10:
        counters[nation] = counters.get(nation, 0) + 1
    else:
        counters[nation] = 0
    world.ai_stalemate_counters = counters
    return counters[nation]


# ═══════════════════════════════════════════════════════════════
# PROPOSAL TERM GENERATION
# ═══════════════════════════════════════════════════════════════

def _build_proposal_terms(
    nation: str,
    proposal_type: str,
    war_score: int,
    world,
    gold_mult: float = 1.0,
    recipient: str = None,
) -> Dict:
    """Build proposal terms dict from AI nation's perspective.

    AI-2a (docs/AI_INTENT_SPEC.md §4.2 seam 1): the envelope is
    recipient-explicit. `recipient=None` keeps the historical default —
    the AI proposes TO France — byte-identically; passing another nation
    addresses the same envelope court-to-court. Nothing passes a
    non-player recipient until AI-2 wires the intent-driven rungs.

    - proposer_nation = AI nation
    - target_nation = recipient (default: the player)
    - sweeteners = things the proposer offers the recipient
    - demands = things the proposer wants from the recipient

    R115: gold_mult scales gold amounts by diplomat personality.
    """
    player = getattr(world, 'player_nation', 'France')
    recipient = recipient or player

    terms = {
        "type": proposal_type,
        "proposer_nation": nation,
        "target_nation": recipient,
        "sweeteners": [],
        "demands": [],
        "clauses": [],
    }

    if proposal_type in ("armistice_losing", "armistice"):
        # AI is losing: offer gold to stop the bleeding
        nation_gold = world.nation_gold.get(nation, 0)
        if nation_gold > 200:
            offer_amount = min(300, int(nation_gold * 0.15 * gold_mult))
            # R113: Cap gold_per_turn at 50% of region income
            # Fix 8: Skip income cap when income is 0 (nation may have gold reserves)
            income_data = world.calculate_turn_income(nation)
            if income_data["income"] > 0:
                max_per_turn = income_data["income"] // 2
                offer_amount = min(offer_amount, max_per_turn)
            if offer_amount > 0:
                terms["sweeteners"].append(
                    {"type": "gold_per_turn", "value": int(offer_amount)}
                )
        terms["type"] = "armistice_losing"

    elif proposal_type == "armistice_stalemate":
        # Stalemate: minimal terms, just stop fighting
        terms["type"] = "armistice_losing"  # Map to known acceptance type

    elif proposal_type == "peace":
        # AI suing for peace (they're losing)
        if war_score < -30:
            # Very desperate: offer gold + open borders
            nation_gold = world.nation_gold.get(nation, 0)
            offer_amount = min(200, int(nation_gold * 0.10 * gold_mult))
            # R113: Cap gold_per_turn at 50% of region income
            # Fix 8: Skip income cap when income is 0 (nation may have gold reserves)
            income_data = world.calculate_turn_income(nation)
            if income_data["income"] > 0:
                max_per_turn = income_data["income"] // 2
                offer_amount = min(offer_amount, max_per_turn)
            if offer_amount > 0:
                terms["sweeteners"].append(
                    {"type": "gold_per_turn", "value": int(offer_amount)}
                )
            terms["clauses"].append("open_borders")

    elif proposal_type in ("non_aggression", "open_borders",
                           "defensive_alliance", "alliance"):
        # Upgrade proposals at peace — minimal terms
        if proposal_type == "non_aggression":
            terms["type"] = "non_aggression"
        elif proposal_type == "open_borders":
            terms["type"] = "open_borders"
            terms["clauses"].append("open_borders")
        elif proposal_type == "defensive_alliance":
            terms["type"] = "defensive_alliance"
            terms["clauses"].append("open_borders")
        elif proposal_type == "alliance":
            terms["type"] = "alliance"
            terms["clauses"].append("open_borders")

        # Saxony always offers protection clause
        if nation == "Saxony":
            terms["clauses"].append("protection_promised")

    elif proposal_type == "friendly_gift":
        # W6-10: a one-time gift softening a low-tier ask — the cool court
        # that would rather pay than fight. The stable P-rule label stays
        # "friendly_gift" (the cooldown key, opportunistic precedent);
        # terms["type"] maps to the highest LEGAL low-tier acceptance type
        # for the current relation (NON_AGGRESSION needs relation >= 0).
        diplo_key = world._make_diplo_key(nation, recipient)
        relation = world.nation_relations.get(diplo_key, 0)
        if relation >= 0:
            terms["type"] = "non_aggression"
        else:
            terms["type"] = "open_borders"
            terms["clauses"].append("open_borders")
        nation_gold = world.nation_gold.get(nation, 0)
        gift = min(150, int(nation_gold * 0.10 * gold_mult))
        if gift >= 25:
            terms["sweeteners"].append(
                {"type": "gold_lump", "value": int(gift)})

    elif proposal_type == "opportunistic":
        # Favorable terms for the AI: demand concessions
        terms["type"] = "non_aggression"  # Map to acceptance type
        terms["demands"].append({"type": "gold_per_turn", "value": int(100 * gold_mult)})

    elif proposal_type == "design_purchase":
        # AI-2 (§4.2): the court asks for its DESIGN — the coveted
        # province France holds — and pays for it at the `buy` rung
        # ("Berlin offers 2,400 gold for Hanover"). The stable P-rule
        # label stays "design_purchase" (cooldown key + register);
        # terms["type"] maps to the next legal upgrade so acceptance
        # ratifies through the ordinary treaty machinery: the demand
        # cedes the province, the sweetener pays the price, both on
        # arms _ratify_treaty already owns.
        from backend.game_logic.intent import get_nation_intent
        view = get_nation_intent(nation, world)
        regions = _ultimatum_demandable_regions(nation, world)
        upgrade = _determine_upgrade_type(nation, world)
        if regions and upgrade:
            terms["type"] = upgrade
            if upgrade in ("open_borders", "defensive_alliance", "alliance"):
                terms["clauses"].append("open_borders")
            terms["demands"].append({
                "type": "territory_cede", "value": 1,
                "regions": [regions[0]],
            })
            if view.price == "buy":
                treasury = int(world.nation_gold.get(nation, 0))
                offer = min(
                    int(treasury * DESIGN_PURCHASE_TREASURY_FRACTION),
                    int((DESIGN_PURCHASE_BASE
                         + DESIGN_PURCHASE_PER_WEIGHT * view.weight)
                        * gold_mult))
                if offer > 0:
                    terms["sweeteners"].append(
                        {"type": "gold_lump", "value": int(offer)})

    elif proposal_type == "sell_neutrality":
        # AI-2d (§4.2b): a belligerent in a war France is NOT in pays
        # France to stay out — Prussia's entire 1795-1806, played from
        # the other side. The lump rides ratification; acceptance mints
        # the §3.3 neutrality compact (the `compact` marker below), so
        # France entering that war later is RENEGING, the strongest
        # casus belli in the game. Without the bond, "refuse everyone"
        # would strictly dominate.
        wars = sorted(world.get_nations_at_war_with(nation))
        terms["type"] = "non_aggression"
        treasury = int(world.nation_gold.get(nation, 0))
        offer = max(SELL_NEUTRALITY_BASE,
                    int(treasury * SELL_NEUTRALITY_TREASURY_FRACTION
                        * gold_mult))
        offer = min(offer, treasury)
        if offer > 0:
            terms["sweeteners"].append(
                {"type": "gold_lump", "value": int(offer)})
        terms["compact"] = "sell_neutrality"
        terms["compact_aim"] = wars[0] if wars else ""

    elif proposal_type == "harsh_peace":
        # R116: AI is winning badly — demand harsh terms
        terms["type"] = "peace"  # Map to peace for acceptance formula
        gold_demand = max(200, int(war_score * 5 * gold_mult))
        terms["demands"].append({"type": "gold_lump", "value": int(gold_demand)})
        diplo_key = world._make_diplo_key(nation, recipient)
        obj = getattr(world, 'war_objectives', {}).get(diplo_key, {}).get(nation, {})
        if obj and obj.get("type") == "liberation" and obj.get("concluded_turn") is None:
            for vassal_nation in obj.get("vassal_nations", []):
                terms["demands"].append({
                    "type": "liberation",
                    "value": 1,
                    "vassal_nation": vassal_nation,
                    "lord_nation": recipient,
                    "liberator": nation,
                })

    return terms


def _reduce_p8_demands(proposal: Dict, nation: str, war_score: int, world) -> Dict:
    """A1: Iteratively reduce P8 harsh peace demands until proposal is viable.

    Steps:
    1. If acceptance score >= 20, return unchanged.
    2. Retry 1: Halve gold_lump demand, re-check.
    3. Retry 2: Drop weakest non-gold demand, re-check.
    4. Fallback: Replace all terms with minimal peace + 200g, set _force_send.
    """
    import copy

    terms = proposal["terms"]
    acceptance = calculate_acceptance(terms, world)
    if acceptance["score"] >= 20:
        return proposal

    # Retry 1: Halve gold_lump demands
    modified = copy.deepcopy(proposal)
    for d in modified["terms"].get("demands", []):
        if d.get("type") == "gold_lump":
            d["value"] = max(200, int(d["value"] // 2))
    acceptance = calculate_acceptance(modified["terms"], world)
    if acceptance["score"] >= 20:
        return modified

    # Retry 2: Drop weakest non-gold demand (lowest value)
    non_gold = [d for d in modified["terms"].get("demands", []) if d.get("type") != "gold_lump"]
    if non_gold:
        weakest = min(non_gold, key=lambda d: d.get("value", 0))
        modified["terms"]["demands"].remove(weakest)
        acceptance = calculate_acceptance(modified["terms"], world)
        if acceptance["score"] >= 20:
            return modified

    # Fallback: Minimal peace + 200g
    player = getattr(world, 'player_nation', 'France')
    fallback_terms = {
        "type": "peace",
        "proposer_nation": nation,
        "target_nation": player,
        "sweeteners": [],
        "demands": [{"type": "gold_lump", "value": 200}],
        "clauses": [],
    }
    modified["terms"] = fallback_terms
    modified["_force_send"] = True
    return modified


def _determine_upgrade_type(nation: str, world) -> Optional[str]:
    """Determine what upgrade the AI should propose based on current state.

    Returns the next valid upgrade type or None if already at max or
    relations are insufficient for the target state.
    """
    from backend.game_logic.diplomacy import STATE_RELATION_REQUIREMENTS
    player = getattr(world, 'player_nation', 'France')
    current_state = world.get_diplomatic_state(player, nation)

    # Map current state to next upgrade in the path
    upgrade_map = {
        "PEACE": ("open_borders", "OPEN_BORDERS"),
        "OPEN_BORDERS": ("non_aggression", "NON_AGGRESSION"),
        "NON_AGGRESSION": ("defensive_alliance", "DEFENSIVE_ALLIANCE"),
        "DEFENSIVE_ALLIANCE": ("alliance", "ALLIANCE"),
    }

    entry = upgrade_map.get(current_state)
    if entry is None:
        return None

    proposal_type, target_state = entry

    # Check relation requirement — don't propose if relations are too low
    diplo_key = world._make_diplo_key(player, nation)
    relation = world.nation_relations.get(diplo_key, 0)
    req = STATE_RELATION_REQUIREMENTS.get(target_state)
    if req is not None and relation < req:
        return None

    return proposal_type


# W6-10: map a low-tier ask type to its target state for legality checks.
_ASK_TARGET_STATE = {
    "open_borders": "OPEN_BORDERS",
    "non_aggression": "NON_AGGRESSION",
    "defensive_alliance": "DEFENSIVE_ALLIANCE",
    "alliance": "ALLIANCE",
}


def _hegemony_ask_candidates(nation: str, diplo_state: str, relation: int,
                             world) -> List[str]:
    """W6-10 anti-monotony: the P3 hegemony-pressure ask varies by relation
    band instead of always leading with open_borders (live audit: five
    identical open-borders proposals in five turns). Candidates are tried
    in order and the per-type cooldown skips a recently rejected/lapsed
    ask, so consecutive approaches differ. Every candidate is a legal
    upward transition whose relation requirement is met — the same rules
    _determine_upgrade_type enforces (R98 jumps allowed). Strictly UPWARD:
    validate_transition also allows adjacent downgrades, which a
    shelter-seeking ask must never propose."""
    from backend.game_logic.diplomacy import (
        STATE_RELATION_REQUIREMENTS, _UPGRADE_ORDER,
    )
    ladder = _determine_upgrade_type(nation, world)
    if relation > 30:
        ordered = ([ladder] if ladder else []) + [
            "non_aggression", "open_borders"]
    elif relation >= 0:
        # The ladder rides LAST as the escalation fallback — a court already
        # at NON_AGGRESSION has no lower-tier ask left, but can still seek
        # the next rung (pre-W6-10 behavior preserved for deep states).
        ordered = ["non_aggression", "friendly_gift", "open_borders"] + (
            [ladder] if ladder else [])
    else:
        ordered = ["friendly_gift", "open_borders"] + (
            [ladder] if ladder else [])

    result: List[str] = []
    for ptype in ordered:
        base = ptype
        if ptype == "friendly_gift":
            # The gift softens the highest LEGAL low-tier ask (see
            # _build_proposal_terms).
            base = "non_aggression" if relation >= 0 else "open_borders"
        target_state = _ASK_TARGET_STATE.get(base)
        if target_state is None:
            continue
        if (diplo_state not in _UPGRADE_ORDER
                or target_state not in _UPGRADE_ORDER
                or _UPGRADE_ORDER.index(target_state)
                <= _UPGRADE_ORDER.index(diplo_state)):
            continue
        req = STATE_RELATION_REQUIREMENTS.get(target_state)
        if req is not None and relation < req:
            continue
        if ptype not in result:
            result.append(ptype)

    # AI-2c (§3.4): the power's statecraft reorders the surviving
    # candidates so its preferred instrument family leads — Prussia
    # reaches for gold before pacts, Austria for pacts before gold.
    # A stable partition, order only; runs BEFORE the NA-2 front-move
    # so the design still outranks the style.
    from backend.game_logic.statecraft import order_asks_by_statecraft
    result = order_asks_by_statecraft(nation, result, world)

    # NA-2 §5.3: an ask that ADVANCES the court's active design leads the
    # list — a guard_neutrality court asks first for the pact its agenda
    # IS (Prussia's armed neutrality seeks the non-aggression guarantee).
    # Legality/relation gates above are unchanged; this is order only.
    from backend.game_logic.agendas import ask_advances_agenda
    for ptype in list(result):
        if ask_advances_agenda(nation, ptype, world):
            result.remove(ptype)
            result.insert(0, ptype)
            break
    return result


def _generate_intent_ask(nation: str, world, diplo_state: str,
                         relation: int, gold_mult: float) -> Optional[Dict]:
    """AI-2 (AI_INTENT_SPEC §4.2) — P-Intent, the peacetime pursuit rung.

    The court's derived intent picks the ask, not the France-relative
    scalars: what it wants, who stands in the way, and what rung of the
    ladder it is prepared to pay. Three arms, first match wins:

    1. THE DESIGN PURCHASE — the obstacle is France and the court is at
       `ask`/`buy`: it asks for the coveted province (paying at `buy`).
       Accept cedes it and the design satisfies (§3.1a a — descent live);
       Reject writes the §5 pin 8 refusal record AI-3 escalates from.
    2. SELL-NEUTRALITY (AI-2d) — the court is fighting a war France is
       not in, and France looms (hostile relation, or the §3.5 mirror
       reads the court as Napoleon's next target): it pays France to
       stay out. Acceptance mints the §3.3 compact.
    3. THE ALIGNMENT ASK — the obstacle is a third court France is also
       hostile to, and this court is at `align`+: it seeks the pact
       ("the enemy of my obstacle").

    Deckless/vassal/survival courts return None (pin 18 — the rung
    falls through to today's behaviour byte-identically). Every
    envelope is tagged `intent_ask` for the §4.2c budget.
    """
    from backend.game_logic.intent import get_nation_intent
    player = getattr(world, "player_nation", "France")
    view = get_nation_intent(nation, world)
    if view.want_id is None or view.survival:
        return None

    proposal = None

    # ── Arm 1: the design purchase / polite request ──
    if (proposal is None and view.against == player
            and view.price in ("ask", "buy")):
        ptype = "design_purchase"
        if not _is_on_cooldown(nation, ptype, world, 0):
            terms = _build_proposal_terms(nation, ptype, 0, world,
                                          gold_mult=gold_mult)
            if terms.get("demands"):  # a demandable region + legal upgrade
                proposal = _make_proposal(nation, ptype, 5, terms, world)

    # ── Arm 2: sell-neutrality (AI-2d's Stage C half) ──
    # Two honesty gates: a court at `coerce`/`fight` does not PAY for
    # peace — it demands (the NA-5 ultimatum rung owns that); and a
    # court whose design obstacle IS France does not buy French
    # neutrality in a side war while coveting French soil — its
    # France-directed instruments are the design purchase above and
    # the ultimatum ladder (so an ultimatum-ready court still reaches
    # NA-5 untouched).
    if (proposal is None
            and view.price in ("ask", "buy", "align", "bandwagon")
            and view.against != player):
        wars = world.get_nations_at_war_with(nation)
        if wars and player not in wars:
            from backend.game_logic.intent import get_france_perceived_intent
            _price, _weight, perceived_target = (
                get_france_perceived_intent(world))
            looming = relation < 0 or perceived_target == nation
            # NON_AGGRESSION must be a strictly upward step from here.
            legal = diplo_state in ("PEACE", "OPEN_BORDERS")
            if looming and legal:
                ptype = "sell_neutrality"
                if not _is_on_cooldown(nation, ptype, world, 0):
                    terms = _build_proposal_terms(nation, ptype, 0, world,
                                                  gold_mult=gold_mult)
                    if terms.get("sweeteners"):  # a real offer, not a token
                        proposal = _make_proposal(nation, ptype, 5, terms,
                                                  world)

    # ── Arm 3: the alignment ask ──
    if (proposal is None and view.against
            and view.against != player
            and view.price in ("align", "bandwagon")):
        obstacle_key = world._make_diplo_key(player, view.against)
        player_hostile = (world.is_at_war(player, view.against)
                          or int(world.nation_relations.get(
                              obstacle_key, 0) or 0) < 0)
        if player_hostile:
            upgrade = _determine_upgrade_type(nation, world)
            if upgrade and not _is_on_cooldown(nation, upgrade, world, 0):
                terms = _build_proposal_terms(nation, upgrade, 0, world,
                                              gold_mult=gold_mult)
                proposal = _make_proposal(nation, upgrade, 5, terms, world)

    if proposal is not None:
        proposal["intent_ask"] = True  # §4.2c: its own delivery budget
    return proposal


# ═══════════════════════════════════════════════════════════════
# P7: OPPORTUNISM CHECK
# ═══════════════════════════════════════════════════════════════

def _national_strength(nation: str, world) -> int:
    """Fog-free national strength on the diplomatic-ledger basis (sum of
    standing marshal strengths — diplomatic_ledger.py's army_strength sum).
    The ledger fogs only the DISPLAY formatting; this is the raw number."""
    return int(sum(m.strength for m in world.marshals.values()
                   if m.nation == nation and m.strength > 0))


def _has_live_ultimatum(world) -> bool:
    """NA-5 §8: max ONE live ultimatum world-wide — scan the active slot
    and the mailbox queue for an undecided incoming_ultimatum dialogue."""
    dm = world.dialogue_manager
    current = dm.peek()
    if current and current.get("type", "") == "incoming_ultimatum":
        return True
    return any(item.get("type", "") == "incoming_ultimatum"
               for item in dm._queue)


def _ultimatum_demandable_regions(nation: str, world) -> List[str]:
    """Unmet ACQUIRE-design targets the player DIRECTLY controls, minus the
    player's capital. The demand must be cedeable by the player's own hand —
    a target held by a player vassal concerns the bloc but cannot ride a
    cession clause the player can sign, and the capital is never demandable
    (conscious tightening of §8's "player-bloc" wording, pinned in tests)."""
    from backend.game_logic.agendas import get_active_agenda
    view = get_active_agenda(nation, world)
    if view is None or view.survival or view.type != "acquire_regions":
        return []
    player = getattr(world, "player_nation", "France")
    player_capital = world.get_nation_capital(player)
    demandable = []
    for region_name in view.regions:
        if region_name == player_capital:
            continue
        region = world.regions.get(region_name)
        if region is not None and getattr(region, "controller", None) == player:
            demandable.append(region_name)
    return demandable


def _generate_agenda_ultimatum(nation: str, world) -> Optional[Dict]:
    """NA-5 §8 (R162): the ultimatum rung body — the caller has already
    established at-peace and relation < 0. The remaining gates (each one
    falsified in test_nation_agendas_ultimatums.py): per-nation 15-turn
    cooldown clear, no live ultimatum anywhere, outside the player's bloc,
    an active acquire design with a player-held unmet target, and fog-free
    national strength >= AI_ULTIMATUM_STRENGTH_RATIO x the player's.

    Building Blocks: terms via the player's own generate_ultimatum_terms
    with the direction inverted (issuer=the AI court, target=the player)
    and the design target as the territory demand. `_force_send` bypasses
    the player-side acceptance filter — ultimatum demands score terribly
    by construction; the send is the point. The cooldown starts at ISSUE,
    so an ignored (lapsed) ultimatum does not return next turn.
    """
    from backend.game_logic.diplomatic_templates import generate_ultimatum_terms

    player = getattr(world, "player_nation", "France")

    cooldowns = _get_cooldowns(world)
    if cooldowns.get(f"{nation}|ultimatum", 0) > 0:
        return None
    if _has_live_ultimatum(world):
        return None
    if nation in set(world.get_bloc_members(player)):
        return None
    demandable = _ultimatum_demandable_regions(nation, world)
    if not demandable:
        return None
    own_strength = _national_strength(nation, world)
    if own_strength <= 0:
        return None  # a court with no army in the field cannot menace
    if own_strength < _national_strength(player, world) * AI_ULTIMATUM_STRENGTH_RATIO:
        return None

    terms = generate_ultimatum_terms(
        player, world, issuer=nation, demand_regions=demandable)
    if not any(d.get("type") == "territory_cede"
               for d in terms.get("demands", [])):
        return None  # the design target must actually ride the demand

    proposal = _make_proposal(nation, "ultimatum", 7, terms, world)
    proposal["_force_send"] = True
    cooldowns[f"{nation}|ultimatum"] = int(AI_ULTIMATUM_COOLDOWN_TURNS)
    _set_cooldowns(world, cooldowns)
    return proposal


def apply_ultimatum_rejection_cooldowns(nation: str, world) -> None:
    """NA-5: rejection re-arms the nation cooldown and FLOORS the ultimatum
    type key at the full AI_ULTIMATUM_COOLDOWN_TURNS. Ultimatums get their
    own applier because apply_rejection_cooldowns OVERWRITES the type key
    with TYPE_REJECTION_COOLDOWN — which would shorten the issue-time 15
    down to 6 (the documented cooldown-overwrite trap, inverted)."""
    cooldowns = _get_cooldowns(world)
    cooldowns[f"{nation}|nation"] = max(
        int(cooldowns.get(f"{nation}|nation", 0)),
        int(NATION_REJECTION_COOLDOWN))
    cooldowns[f"{nation}|ultimatum"] = max(
        int(cooldowns.get(f"{nation}|ultimatum", 0)),
        int(AI_ULTIMATUM_COOLDOWN_TURNS))
    _set_cooldowns(world, cooldowns)


def _count_nations_at_war_with_france(world) -> int:
    """Count how many nations France is currently at war with."""
    player = getattr(world, 'player_nation', 'France')
    count = 0
    for nation in getattr(world, 'enemy_nations', []):
        if world.is_at_war(player, nation):
            count += 1
    return count


# ═══════════════════════════════════════════════════════════════
# MAIN ENTRY POINT: process_diplomatic_phase
# ═══════════════════════════════════════════════════════════════

def process_diplomatic_phase(nation: str, world) -> Optional[Dict]:
    """Evaluate whether an AI nation should make a diplomatic proposal to France.

    Runs ONCE per AI nation per turn, BEFORE the Morning Dispatch.
    Returns a proposal dict if one should be generated, None otherwise.

    Priority table (§9a):
        P1: war_score < -40 (losing badly) → armistice/peace
        P2: war_score between -10..+10 for 5+ turns → armistice
        P3: Threat > 60 AND not allied → [deferred]
        P4: Relation > +30 AND at peace → propose upgrade
        P5: Gold < 200 and declining → [deferred]
        P6: [deferred to Session 5 - vassal courting]
        P7: France at war with 2+ nations AND this nation at peace → favorable terms

    Anti-spam:
        - Per-nation cooldown: 3 turns after rejection
        - Per-type cooldown: 5 turns after same type rejected
        - If pending_diplomatic_dialogue is blocking, queue instead
        - Max 1 AI proposal delivered per turn
        - Queue max 3 items, lowest priority dropped, 3-turn expiry
    """
    player = getattr(world, 'player_nation', 'France')
    if nation == player:
        return None

    # R81: Skip eliminated nations (0 regions + 0 marshals)
    from backend.game_logic.diplomacy import _is_nation_eliminated
    if _is_nation_eliminated(world, nation):
        return None

    # ── Deduplication: skip if this nation already has a pending proposal ──
    if _has_pending_proposal_from(nation, world):
        return None

    # ── Get diplomatic context ──
    diplo_state = world.get_diplomatic_state(player, nation)
    is_at_war = diplo_state == "WAR"
    diplo_key = world._make_diplo_key(player, nation)
    relation = world.nation_relations.get(diplo_key, 0)
    war_score = _get_war_score_for_nation(nation, player, world) if is_at_war else 0

    # R115: Get personality modifiers for this nation's diplomat
    mods = _get_personality_modifiers(nation, world)
    gold_mult = mods["gold_demand_mult"]
    we = world.war_exhaustion.get(nation, 0)
    effective_p1_threshold = -40 + mods["peace_threshold_delta"] + we // 20

    # WPS-D §13.2: AI ticking pressure — opponent ticking makes AI more
    # willing to seek peace (raises threshold); own ticking makes AI less willing.
    if is_at_war:
        ticking_pressure = _calculate_ticking_pressure(nation, player, diplo_key, world)
        effective_p1_threshold += ticking_pressure
        # NA-3 §5.5: agenda resolve — a war that advances the court's
        # design hardens resolve (-8, fights longer); a satisfied design
        # or the survival override sues sooner (+10); an irrelevant war
        # deliberately changes nothing (AUD-b/P2 armistice tuning holds).
        from backend.game_logic.agendas import get_agenda_resolve_delta
        effective_p1_threshold += get_agenda_resolve_delta(nation, player, world)

    effective_stalemate_turns = max(2, 5 + mods["patience_bonus"] - we // 30)

    # Update stalemate counter
    if is_at_war:
        stalemate_turns = _update_stalemate_counter(nation, war_score, world)
    else:
        stalemate_turns = 0

    proposal = None

    # R5b: Block proposals for pairs still on armistice cooldown
    armistice_cooldowns = getattr(world, 'armistice_cooldowns', {})
    if armistice_cooldowns.get(diplo_key, 0) > 0:
        return None

    # ── P1: Losing badly (war_score < effective threshold) ──
    if is_at_war and war_score < effective_p1_threshold:
        # A2: Coalition loyalty — members stay loyal unless desperate
        from backend.game_logic.coalition import is_coalition_member
        coalition_blocked = False
        if is_coalition_member(nation, world):
            war_duration = world.current_turn - world.war_start_turns.get(diplo_key, world.current_turn)
            nation_we = world.war_exhaustion.get(nation, 0)
            # NA-2 §5.4 the Pressburg arm: a member whose court's design is
            # SATISFIED (or fighting for survival) breaks ranks earlier —
            # war_score < AGENDA_SEPARATE_PEACE_SCORE (-30) instead of the
            # stock -50. A nation that got what it wanted sues to lock it.
            from backend.game_logic.agendas import (
                AGENDA_SEPARATE_PEACE_SCORE, agenda_separate_peace_ready,
            )
            pressburg_ready = (
                war_score < AGENDA_SEPARATE_PEACE_SCORE
                and agenda_separate_peace_ready(nation, world)
            )
            if not (war_score < -50 or nation_we > 80
                    or (war_duration >= 8 and war_score < -60)
                    or pressburg_ready):
                coalition_blocked = True

        if not coalition_blocked:
            # Decide: armistice if war_score > -70, peace if truly desperate
            if war_score < -70:
                ptype = "peace"
            else:
                ptype = "armistice_losing"

            if not _is_on_cooldown(nation, ptype, world, war_score):
                terms = _build_proposal_terms(nation, ptype, war_score, world, gold_mult=gold_mult)
                proposal = _make_proposal(nation, ptype, 1, terms, world)

    # ── P2: Stalemate (war_score -10..+10 for N+ turns, R149: fire when not clearly winning) ──
    # AUD-b: gate the stalemate exit on ACTUAL combat. A pair that has recorded
    # >=1 war-score battle uses the normal patience window; a pair that has never
    # fought must wait the much longer no-contact escape so a coalition can't sue
    # for peace by turn ~5-7 without a shot fired. `battle_records[diplo_key]` is
    # non-empty iff a >=1000-casualty battle (the war-score contact threshold)
    # occurred on the pair — so uninvolved coalition members correctly hold.
    if proposal is None and is_at_war and war_score <= 10:
        has_fought = bool(getattr(world, 'battle_records', {}).get(diplo_key))
        p2_threshold = (
            effective_stalemate_turns
            if has_fought
            else max(effective_stalemate_turns, P2_NO_CONTACT_ESCAPE_TURNS)
        )
        if stalemate_turns >= p2_threshold:
            ptype = "armistice_stalemate"
            if not _is_on_cooldown(nation, "armistice", world, war_score):
                terms = _build_proposal_terms(nation, ptype, war_score, world, gold_mult=gold_mult)
                proposal = _make_proposal(nation, "armistice", 2, terms, world)

    # ── P-Intent (AI-2, §4.2): the peacetime pursuit rung — BEFORE P3,
    # because §4.2's core claim is that a court with a live design fires
    # on WHAT IT IS TRYING TO ACHIEVE, not on the France-threat scalar
    # (at the 1805 boot threat stands at 85, so a P3-first ordering
    # would shelter-ask every design ask into silence). Courts with no
    # design-driven ask fall through to P3 byte-identically (pin 18).
    if proposal is None and not is_at_war:
        proposal = _generate_intent_ask(nation, world, diplo_state,
                                        relation, gold_mult)

    # ── P3: Threat > 60 AND not allied → seek shelter (R106, DLF-9) ──
    # W6-10 anti-monotony: the hegemony-pressure ask varies by relation
    # band {ladder upgrade / non_aggression / open_borders / friendly_gift}
    # instead of always leading with open_borders; per-type cooldowns skip
    # a recently rejected or lapsed ask, so consecutive approaches differ.
    if proposal is None and not is_at_war:
        threat = int(getattr(world, 'threat_level', 0))
        if threat > 60:
            if diplo_state not in ("DEFENSIVE_ALLIANCE", "ALLIANCE"):
                for ask_type in _hegemony_ask_candidates(
                        nation, diplo_state, relation, world):
                    if _is_on_cooldown(nation, ask_type, world, war_score):
                        continue
                    terms = _build_proposal_terms(nation, ask_type, 0, world, gold_mult=gold_mult)
                    proposal = _make_proposal(nation, ask_type, 3, terms, world)
                    break

    # ── P4: Relation > +30 AND at peace → propose upgrade ──
    if proposal is None and not is_at_war and relation > 30:
        upgrade_type = _determine_upgrade_type(nation, world)
        if upgrade_type and not _is_on_cooldown(nation, upgrade_type, world, war_score):
            terms = _build_proposal_terms(nation, upgrade_type, 0, world, gold_mult=gold_mult)
            proposal = _make_proposal(nation, upgrade_type, 4, terms, world)

    # ── P5: Gold < 200 and declining [DEFERRED] ──
    # (P-Intent, formerly staged in this slot, moved ABOVE P3 — §4.2's
    # design-outranks-threat-shelter ordering.)

    # ── P6: Vassal courting [DEFERRED to Session 5] ──

    # ── P7: Opportunism — France at war with 2+ AND this nation at peace ──
    # Only fires if current state is below NON_AGGRESSION (the proposed type)
    if proposal is None and not is_at_war:
        wars_against_france = _count_nations_at_war_with_france(world)
        if wars_against_france >= 2 and diplo_state in ("PEACE", "OPEN_BORDERS"):
            ptype = "opportunistic"
            if not _is_on_cooldown(nation, ptype, world, war_score):
                terms = _build_proposal_terms(nation, ptype, 0, world, gold_mult=gold_mult)
                proposal = _make_proposal(nation, ptype, 7, terms, world)

    # ── NA-5 §8 (R162): The Ultimatum — between P7 and P8 ──
    # A court whose active ACQUIRE design targets player-held soil, at peace,
    # hostile (relation < 0), outside the player's bloc, with an army >=1.25x
    # the player's, demands the design target instead of declaring a war it
    # cannot yet have (no unilateral AI declare-war path in NA-5 — the
    # coalition system remains the war-maker; rejection feeds it via the
    # coalition.py pressure marker).
    if proposal is None and not is_at_war and relation < 0:
        proposal = _generate_agenda_ultimatum(nation, world)

    # ── P8: Aggressive Dominance — AI winning badly (war_score > 40) ──
    # R116: When AI is dominating, demand harsh peace terms
    if proposal is None and is_at_war and war_score > 40:
        ptype = "harsh_peace"
        if not _is_on_cooldown(nation, ptype, world, war_score):
            terms = _build_proposal_terms(nation, ptype, war_score, world, gold_mult=gold_mult)
            proposal = _make_proposal(nation, ptype, 8, terms, world)

    # ── P-Bandwagon: non-bloc minor / exposed secondary seeks shelter ──
    # B-Hegemony §7.3 + RELIABILITY_IMPLEMENTATION_PLAN AI escape-valve.
    # Triggers when (a) current hegemon's bloc share >= 50% (the
    # proper-noun reveal threshold, aligned with the player's first visible
    # name-of-the-thing moment — bandwagoning before the player can see
    # "the French System" by name would read as AI cheating), (b) the
    # proposer is not already locked into a rival deep bloc, (c) relations
    # are not hostile. This is the canonical escape valve that keeps
    # hegemony from reading as a hard ban on growth.
    if proposal is None and not is_at_war:
        try:
            from backend.game_logic.coalition import (
                _identify_max_bloc_share, _hegemony_signal_band,
            )
            hegemon, share = _identify_max_bloc_share(world)
            # In v0.1, AI proposals flow to the player. Bandwagon only fires
            # when the PLAYER is the hegemon AND share >= 50% AND this
            # nation is a non-bloc minor/secondary AND not hostile AND not
            # already allied with a non-hegemon major.
            from backend.nation_config import _POWER_TIER_DEFAULT
            self_tier = world.get_power_tier(nation) or _POWER_TIER_DEFAULT
            is_minor_or_secondary = self_tier in ("minor", "secondary")
            bloc_members = world.get_bloc_members(hegemon) if hegemon else []
            already_in_hegemon_bloc = nation in bloc_members
            # Already in rival deep bloc? Any non-hegemon major we have
            # ALLIANCE/DEFENSIVE_ALLIANCE with counts as a "rival deep bloc".
            locked_in_rival_bloc = False
            if hegemon:
                for other in world.get_active_nations():
                    if other == nation or other == hegemon:
                        continue
                    other_tier = world.get_power_tier(other) or _POWER_TIER_DEFAULT
                    if other_tier != "major":
                        continue
                    if world.get_diplomatic_state(nation, other) in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
                        locked_in_rival_bloc = True
                        break
            if (
                hegemon == player
                and _hegemony_signal_band(share) >= 2
                and is_minor_or_secondary
                and not already_in_hegemon_bloc
                and relation >= 0  # not hostile
                and not locked_in_rival_bloc
            ):
                # Proposer bandwagons: offer alliance / defensive alliance to hegemon
                ptype = _determine_upgrade_type(nation, world)
                if ptype and not _is_on_cooldown(nation, ptype, world, war_score):
                    terms = _build_proposal_terms(nation, ptype, 0, world, gold_mult=gold_mult)
                    proposal = _make_proposal(nation, ptype, 9, terms, world)
            elif (
                # AI-2 (§3.1): the rung widened to ANY hegemon and driven
                # from INTENT — a court whose own ladder reads `bandwagon`
                # serves the strong for payment. The recipient-addressed
                # envelope rides the converged AI-2a transport (it never
                # touches the player's mailbox). Player-hegemon behaviour
                # above is byte-identical; this arm is boot-dormant on
                # 1805 (France leads at 0.396, below the 50% band).
                hegemon is not None
                and hegemon != player
                and hegemon != nation
                and _hegemony_signal_band(share) >= 2
                and not already_in_hegemon_bloc
                and not locked_in_rival_bloc
                and not world.is_at_war(nation, hegemon)
            ):
                from backend.game_logic.intent import get_nation_intent
                if get_nation_intent(nation, world).price == "bandwagon":
                    state_h = world.get_diplomatic_state(nation, hegemon)
                    from backend.game_logic.diplomacy import _UPGRADE_ORDER
                    ptype = None
                    if state_h in _UPGRADE_ORDER:
                        if (_UPGRADE_ORDER.index(state_h)
                                < _UPGRADE_ORDER.index("DEFENSIVE_ALLIANCE")):
                            ptype = "defensive_alliance"
                        elif state_h == "DEFENSIVE_ALLIANCE":
                            ptype = "alliance"
                    if ptype and not _is_on_cooldown(
                            nation, ptype, world, war_score,
                            recipient=hegemon):
                        terms = _build_proposal_terms(
                            nation, ptype, 0, world, gold_mult=gold_mult,
                            recipient=hegemon)
                        proposal = _make_proposal(nation, ptype, 9, terms,
                                                  world, recipient=hegemon)
        except Exception as exc:
            from backend.utils.debug import debug_print
            debug_print(
                f"[HEGEMONY] bandwagon evaluation failed for {nation} on "
                f"turn {int(getattr(world, 'current_turn', 1) or 1)}: {exc}"
            )
            # Defensive: bandwagon path never blocks existing P-rules.
            pass

    if proposal is None:
        return None

    # A1: Iterative demand reduction for P8 harsh peace proposals
    if proposal.get("proposal_type") == "harsh_peace":
        proposal = _reduce_p8_demands(proposal, nation, war_score, world)

    # ── Verify proposal is reasonable via calculate_acceptance ──
    acceptance = calculate_acceptance(proposal["terms"], world)
    score = acceptance["score"]

    # AI won't propose something that would be auto-rejected (score < 20)
    # A1: _force_send bypasses this filter for fallback proposals
    if score < 20 and not proposal.get("_force_send"):
        return None

    # Fix 11 / R126: Record metadata AFTER acceptance check passes
    # (previously in _make_proposal, which recorded even for rejected proposals)
    metadata = getattr(world, 'ai_proposal_metadata', {})
    metadata[nation] = {
        "war_score_at_proposal": int(get_war_score_for(world, nation, player)) if is_at_war else 0,
        "turn": int(world.current_turn),
    }
    world.ai_proposal_metadata = metadata

    # Session 2 follow-up: All proposals delivered immediately through
    # dialogue_manager.push() — no separate queue needed. The dialogue
    # manager handles queuing internally when another dialogue is active.
    return proposal


def _make_proposal(
    nation: str,
    proposal_type: str,
    priority: int,
    terms: Dict,
    world,
    recipient: str = None,
) -> Dict:
    """Construct the standard proposal dict.

    AI-2a (§4.2 seam 1): the envelope carries an explicit `recipient`
    (default: the player — byte-identical to the historical shape). The
    Talleyrand assessment and game bucket are FRANCE'S reading of the
    proposer and only exist on player-addressed envelopes; a court-to-
    court proposal carries None there (Talleyrand does not annotate other
    people's mail).
    """
    player = getattr(world, 'player_nation', 'France')
    recipient = recipient or player

    if recipient == player:
        # Get game bucket from France's perspective (Talleyrand's assessment)
        game_bucket = get_game_bucket(nation, world)
        assessment = _get_talleyrand_assessment(proposal_type, game_bucket)
        decision_reason = determine_ai_offer_decision_reason(
            nation, proposal_type, world)
    else:
        assessment = None
        # The player-relative reason ladder does not apply court-to-court;
        # AI-2 refines this when intent drives the rungs. ask_advances is
        # nation-generic, so the one honest label survives.
        from backend.game_logic.agendas import ask_advances_agenda
        decision_reason = ("agenda_pursuit"
                           if ask_advances_agenda(nation, proposal_type,
                                                  world)
                           else "unknown_baseline")

    # Fix 11: Metadata moved to generate_ai_proposal after acceptance check
    # (was here before, but recorded even for rejected proposals)
    return {
        "source": nation,
        "recipient": recipient,
        "proposal_type": proposal_type,
        "priority": int(priority),
        "terms": terms,
        "talleyrand_assessment": assessment,
        "decision_reason": decision_reason,
        "turn_generated": int(world.current_turn),
    }


# ═══════════════════════════════════════════════════════════════
# DELIVERY: deliver_ai_proposal
# ═══════════════════════════════════════════════════════════════

def _build_ai_ultimatum_dialogue(proposal: Dict, world) -> Dict:
    """NA-5 §8: the incoming-ultimatum dialogue — same mailbox transport as
    incoming_proposal but its OWN dtype (the popup renders the ultimatum
    register: struck header, no bargaining), and Yield/Defy only — an
    ultimatum is not a negotiation, so there is no counter-offer arm."""
    nation = proposal["source"]
    terms = proposal["terms"]
    decision_reason = proposal.get("decision_reason", "")

    diplomats = getattr(world, 'diplomats', {})
    diplomat = diplomats.get(nation)
    diplomat_name = diplomat.name if diplomat else f"the {nation} ambassador"

    proposal_summary = _format_proposal_summary(terms)
    assessment = (
        "Talleyrand: \"They believe their army makes the argument, Sire. "
        "Yield, and the design is theirs without a shot; defy them, and "
        "their court will press the next coalition the harder.\""
    )
    popup_payload = build_pending_envoy_popup_from_terms(
        world,
        nation=nation,
        terms=terms,
        assessment=assessment,
        decision_reason=decision_reason,
    )
    popup_payload["is_ultimatum"] = True

    return {
        "type": "incoming_ultimatum",
        "target_nation": nation,
        "talleyrand_text": (
            f"Sire, {diplomat_name} delivers an ULTIMATUM from {nation}:"
            f"\n\n  {proposal_summary}"
            f"\n\n{assessment}"
        ),
        "options": [
            {
                "label": "Yield",
                "description": f"Concede {nation}'s demands in full.",
                "action": "accept_ai_ultimatum",
            },
            {
                "label": "Defy",
                "description": f"Refuse the demands. {nation}'s court will not forget.",
                "action": "reject_ai_ultimatum",
            },
        ],
        "context": {
            "proposal": terms,
            "source_nation": nation,
            "acceptance_score": 0,
            "decision_reason": decision_reason,
            # Stable P-rule label (the documented cooldown-key rule).
            "proposal_type": "ultimatum",
        },
        "turn_created": int(world.current_turn),
        "blocking": False,
        "popup_payload": popup_payload,
    }


def build_ai_proposal_dialogue(proposal: Dict, world) -> Dict:
    """Build a mailbox-aware incoming proposal dialogue without side effects."""
    # NA-5 §8: ultimatums ride the same transport under their own dtype.
    if proposal.get("proposal_type") == "ultimatum":
        return _build_ai_ultimatum_dialogue(proposal, world)
    nation = proposal["source"]
    terms = proposal["terms"]
    assessment = proposal.get("talleyrand_assessment", "")
    decision_reason = proposal.get("decision_reason", "")

    diplomats = getattr(world, 'diplomats', {})
    diplomat = diplomats.get(nation)
    diplomat_name = diplomat.name if diplomat else f"the {nation} ambassador"

    proposal_summary = _format_proposal_summary(terms)
    acceptance = calculate_acceptance(terms, world)
    popup_payload = build_pending_envoy_popup_from_terms(
        world,
        nation=nation,
        terms=terms,
        assessment=assessment,
        acceptance=acceptance,
        decision_reason=decision_reason,
    )

    # W6-10 (E-CA-6): the diplomat's own spoken line rides both surfaces —
    # the popup carries it as `diplomat_line` (built in the payload
    # builder), the typed terminal weaves it into the arrival text.
    diplomat_line = popup_payload.get("diplomat_line", "")
    spoken = f"\n\n  {diplomat_line}" if diplomat_line else ""

    return {
        "type": "incoming_proposal",
        "target_nation": nation,
        "talleyrand_text": (
            f"Sire, {diplomat_name} has arrived with a proposal from {nation}:"
            f"{spoken}"
            f"\n\n  {proposal_summary}"
            f"\n\n{assessment}"
        ),
        "options": [
            {
                "label": "Accept",
                "description": f"Accept {nation}'s proposal as offered.",
                "action": "accept_ai_proposal",
            },
            {
                "label": "Reject",
                "description": f"Decline {nation}'s proposal outright.",
                "action": "reject_ai_proposal",
            },
            {
                "label": "Counter-offer",
                "description": "Costs 1 DP",
                "action": "counter_ai_proposal",
            },
        ],
        "context": {
            "proposal": terms,
            "source_nation": nation,
            "acceptance_score": int(acceptance["score"]),
            "decision_reason": decision_reason,
            # Stable P-rule label ("harsh_peace", "armistice", "peace", ...). The
            # rejection cooldown MUST key on this, not terms["type"] — the latter is
            # rewritten by _build_proposal_terms (harsh_peace -> "peace"), so keying
            # on it set a cooldown the P8/P2 checks never read, letting an urgent
            # re-proposal bypass anti-spam.
            "proposal_type": proposal.get("proposal_type", ""),
        },
        "turn_created": int(world.current_turn),
        "blocking": False,
        "popup_payload": popup_payload,
    }


def deliver_ai_proposal(proposal: Dict, world) -> Dict:
    """Take a proposal dict and set up world.pending_diplomatic_dialogue.

    Creates an incoming_proposal dialogue with Accept/Reject/Counter options.
    Sets blocking=True so no other proposals overwrite it.

    AI-2a (§4.2 seam 2): the transport is recipient-aware. A proposal whose
    `recipient` is another AI court never touches the player's mailbox,
    notifications or popups — it routes to the court-to-court resolution
    (`_resolve_ai_ai_proposal`: accept both sides → ratify; else the
    refusal record + its public event). The player-addressed path below is
    byte-identical to the pre-AI-2a transport.

    Returns the dialogue dict (also stored on world), or the resolution
    event dict (possibly empty) for a court-to-court envelope.
    """
    nation = proposal["source"]
    player = getattr(world, 'player_nation', 'France')
    recipient = proposal.get("recipient") or player
    if recipient != player:
        return _resolve_ai_ai_proposal(proposal, world) or {}

    dialogue = build_ai_proposal_dialogue(proposal, world)

    # V2-89 → R12C: push() auto-queues if another dialogue is active
    world.dialogue_manager.push(dialogue)

    # PL-27: Log arrival event for campaign log visibility
    world.log_event({
        "type": "proposal_arrived",
        "source": nation,
        "proposal_type": proposal.get("proposal_type", ""),
        # v2.4.3 emits `hegemony_pressure` / `unknown_baseline`; legacy saves
        # may still carry `rival_pressure` until the next turn flush rewrites them.
        "decision_reason": proposal.get("decision_reason", ""),
        "turn": int(world.current_turn),
    })

    # Dispatch event (Session 8D)
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "diplomatic_ai_proposal",
                        {"nation": nation}, "always")

    # Notification: AI proposal arrived (Session 8C)
    from backend.notifications import (
        create_notification, NotificationPriority, DIPLOMATIC_PROPOSAL,
    )
    # §11.8 stage 3 — compose on the CURRENT name. The client cannot repair a
    # single-token formable tag here: humanize_nation_keys_in_text skips any
    # key failing _is_prose_safe_nation_key, which names "Holland" outright.
    from backend.game_logic.formations import formed_display_name
    sender = formed_display_name(world, nation)
    if proposal.get("proposal_type") == "ultimatum":
        # NA-5 §8: an ultimatum announces itself as one.
        world.notifications.add(create_notification(
            DIPLOMATIC_PROPOSAL,
            NotificationPriority.HIGH,
            f"Ultimatum from {sender}",
            f"An envoy from {sender} has arrived with an ultimatum. "
            f"Yield, or defy them.",
            int(world.current_turn),
        ))
    else:
        world.notifications.add(create_notification(
            DIPLOMATIC_PROPOSAL,
            NotificationPriority.HIGH,
            f"Envoy from {sender}",
            f"An envoy from {sender} has arrived with a proposal.",
            int(world.current_turn),
        ))

    # Keep the current active popup available for Godot. Queued mailbox items
    # carry their own popup payload on the dialogue itself.
    world.incoming_proposal_popup = copy.deepcopy(dialogue["popup_payload"])

    return dialogue


def _format_proposal_summary(terms: Dict) -> str:
    """Create a human-readable summary of proposal terms."""
    from backend.display_names import format_proposal_summary

    return format_proposal_summary(terms)


# ═══════════════════════════════════════════════════════════════
# DEQUEUE: try_deliver_queued_proposal
# ═══════════════════════════════════════════════════════════════

def try_deliver_queued_proposal(world) -> Optional[Dict]:
    """DEPRECATED: diplomatic_queue eliminated. All proposals go through
    dialogue_manager.push() at generation time. Retained as no-op stub
    for callers that haven't been updated yet."""
    return None


# ═══════════════════════════════════════════════════════════════
# M3 COUNTER-OFFER ALGORITHM (§9b)
# ═══════════════════════════════════════════════════════════════

def generate_counter_offer(
    proposal: Dict, world, *, counter_author: str = "", dry_run: bool = False
) -> Optional[Dict]:
    """Generate a deterministic counter-offer to a proposal.

    Algorithm (§9b):
        Step 1: Calculate per-clause acceptance impact using SWEETENER/DEMAND values.
        Step 2: Identify the single clause with the largest NEGATIVE impact on
                 AI acceptance (i.e., the thing the AI hates most about France's
                 modification).
        Step 3: Remove that clause.
        Step 4: Recalculate. If still 30-49, add cheapest desired clause from
                 per-nation desire table.
        Step 5: If score >= 50: present as counter. If < 30: REJECT.

    G4F-13: the counter is authored by the court that RECEIVED the proposal.
    The M3 path (player counters an AI proposal) keeps proposer_nation as the
    author; for a PLAYER-SENT proposal the author is target_nation — its desire
    table, its diplomat, its DP. Sweeteners are always paid by the PROPOSING
    side, so affordability checks run against the proposer's treasury in both
    directions. For player-sent proposals the bar is the plain sign threshold
    (50) — personality already shapes the score itself, and the counter is the
    AI naming the price at which it WOULD sign.

    Args:
        proposal: The proposal terms dict being countered.
        world: WorldState
        counter_author: Explicit countering nation; derived when empty.
        dry_run: Constructibility check only — no DP charge or world mutation.

    Returns:
        Modified terms dict if counter succeeds, or None if no counter can
        be constructed (the caller degrades to a rejection).
    """
    import copy
    terms = copy.deepcopy(proposal)
    source_nation = terms.get("proposer_nation", "")
    player_nation = getattr(world, 'player_nation', 'France')
    player_sent = bool(source_nation) and source_nation == player_nation
    author = counter_author or (
        terms.get("target_nation", "") if player_sent else source_nation
    )

    # R138: Counter-offers cost 1 DP for AI nations (the AUTHOR pays).
    if not dry_run and author and author != player_nation:
        nation_dp = getattr(world, 'nation_dp', {})
        current_dp = nation_dp.get(author, 0)
        if current_dp < 1:
            return None  # AI can't afford counter-offer — reject instead
        nation_dp[author] = current_dp - 1
        world.nation_dp = nation_dp

    # G4F-13: never author a counter the ratify gate would veto. A peace
    # counter at relations below the STATE_RELATION_REQUIREMENTS threshold
    # would "bind" at >= 50 on the formula and then fail _ratify_treaty —
    # the player accepts and nothing happens. Unratifiable type → no
    # counter (the resolution degrades to an honest rejection instead).
    _counter_target = terms.get("target_nation", "")
    if _counter_target:
        from backend.game_logic.diplomacy import (
            check_relation_requirement,
        )
        _state_for_type = {
            "peace": "PEACE", "armistice": "ARMISTICE",
            "armistice_losing": "ARMISTICE", "armistice_winning": "ARMISTICE",
            "alliance": "ALLIANCE", "defensive_alliance": "DEFENSIVE_ALLIANCE",
            "open_borders": "OPEN_BORDERS", "non_aggression": "NON_AGGRESSION",
        }
        _target_state = _state_for_type.get(str(terms.get("type", "")))
        if _target_state:
            _pair_key = world._make_diplo_key(
                terms.get("proposer_nation", "") or "France", _counter_target
            )
            _relation = getattr(world, 'nation_relations', {}).get(_pair_key, 0)
            _current = world.diplomatic_states.get(_pair_key, "PEACE")
            if not check_relation_requirement(_current, _target_state, _relation):
                return None

    # R125: personality thresholds (the AUTHOR's diplomat) govern the M3
    # path. Player-sent proposals use the formula's own bands (G4F-13).
    if player_sent:
        accept_threshold = 50
        floor_threshold = 30
    else:
        diplomats = getattr(world, 'diplomats', {})
        diplomat = diplomats.get(author)
        diplomat_personality = getattr(diplomat, 'personality', 'loyalist') if diplomat else 'loyalist'
        thresholds = PERSONALITY_COUNTER_THRESHOLDS.get(diplomat_personality, PERSONALITY_COUNTER_THRESHOLDS["loyalist"])
        accept_threshold = thresholds["accept"]
        floor_threshold = thresholds["floor"]

    # ── Step 1: Calculate per-clause impact ──
    # We test removing each sweetener/demand/clause individually to see
    # what impact it has on the acceptance score
    baseline = calculate_acceptance(terms, world)
    baseline_score = baseline["score"]

    # If already acceptable, no need to counter
    if baseline_score >= accept_threshold:
        return terms

    # Track impact of each removable element
    clause_impacts = []

    # Test removing each sweetener (these help France, removing hurts France)
    for i, s in enumerate(terms.get("sweeteners", [])):
        test_terms = copy.deepcopy(terms)
        test_terms["sweeteners"].pop(i)
        test_result = calculate_acceptance(test_terms, world)
        impact = test_result["score"] - baseline_score
        clause_impacts.append({
            "category": "sweetener",
            "index": i,
            "item": s,
            "impact": impact,
            "description": f"sweetener:{s.get('type', '')}={s.get('value', 0)}",
        })

    # Test removing each demand (these hurt France, removing helps France)
    for i, d in enumerate(terms.get("demands", [])):
        test_terms = copy.deepcopy(terms)
        test_terms["demands"].pop(i)
        test_result = calculate_acceptance(test_terms, world)
        impact = test_result["score"] - baseline_score
        clause_impacts.append({
            "category": "demand",
            "index": i,
            "item": d,
            "impact": impact,
            "description": f"demand:{d.get('type', '')}={d.get('value', 0)}",
        })

    # Test removing each special clause
    for i, c in enumerate(terms.get("clauses", [])):
        test_terms = copy.deepcopy(terms)
        test_terms["clauses"].pop(i)
        test_result = calculate_acceptance(test_terms, world)
        impact = test_result["score"] - baseline_score
        clause_impacts.append({
            "category": "clause",
            "index": i,
            "item": c,
            "impact": impact,
            "description": f"clause:{c}",
        })

    def _bridge(candidate: Dict) -> Optional[Dict]:
        """Desire-table walk, then the universal gold bridge (G4F-13).

        Player-sent counters restrict the desire walk to gold types: the
        table's territory/clause entries describe things the AI cedes from
        its OWN holdings (M3 semantics) and would ratify as nonsense when
        France is the payer.
        """
        improved = _try_add_desired_clauses(
            candidate, author, world,
            accept_threshold=accept_threshold, payer_nation=source_nation,
            gold_only=player_sent,
        )
        if improved is not None:
            return improved
        return _gold_bridge_counter(
            candidate, world,
            accept_threshold=accept_threshold, payer_nation=source_nation,
        )

    # ── Step 2: Find clause with largest NEGATIVE impact on acceptance ──
    # (The clause that, when present, hurts acceptance the most =
    #  removing it would INCREASE acceptance the most =
    #  highest positive impact value)
    if not clause_impacts:
        # Nothing to remove — try adding desired clauses directly
        return _bridge(terms)

    # Sort by impact descending (removing the one with highest positive impact
    # improves the score the most — that's the one the AI hates most)
    clause_impacts.sort(key=lambda x: x["impact"], reverse=True)
    worst_clause = clause_impacts[0]

    # Only remove if it actually improves the score
    if worst_clause["impact"] <= 0:
        # No single removal helps — try adding desired clauses
        return _bridge(terms)

    # ── Step 3: Remove that clause ──
    category = worst_clause["category"]
    idx = worst_clause["index"]
    if category == "sweetener":
        terms["sweeteners"].pop(idx)
    elif category == "demand":
        terms["demands"].pop(idx)
    elif category == "clause":
        terms["clauses"].pop(idx)

    # ── Step 4: Recalculate ──
    new_result = calculate_acceptance(terms, world)
    new_score = new_result["score"]

    if new_score >= accept_threshold:
        return terms

    if floor_threshold <= new_score < accept_threshold:
        # Try adding cheapest desired clause from nation's desire table
        improved = _bridge(terms)
        if improved is not None:
            return improved

    # ── Step 5: If below floor, REJECT ──
    if new_score < floor_threshold:
        return None

    # Between floor and accept but couldn't bridge the gap: the M3 path
    # still returns the trimmed package as a counter (legacy behavior).
    # A player-sent counter is the AI naming the price it WOULD sign at,
    # so an under-bar package degrades to an honest rejection instead.
    if player_sent:
        return None
    return terms


def _payer_gold(world, payer_nation: str) -> int:
    """Treasury of the side that pays counter sweeteners (proposer side).

    `world.gold` is a property over nation_gold[player_nation], so the
    nation_gold lookup is payer-correct for player and AI alike.
    """
    try:
        return int(getattr(world, 'nation_gold', {}).get(payer_nation, 0))
    except Exception:
        return 0


def _gold_bridge_counter(
    terms: Dict, world, *, accept_threshold: int, payer_nation: str
) -> Optional[Dict]:
    """G4F-13 universal fallback: bridge the acceptance gap with gold.

    Courts without a NATION_DESIRES entry (and desire walks that fall
    short) still get a constructible counter: the smallest 100-gold step
    the payer can afford that lifts the package to the accept bar. Walks
    the live formula, so no pricing-rate assumption is baked in.
    """
    import copy

    if not payer_nation:
        return None
    treasury = _payer_gold(world, payer_nation)
    if treasury < 100:
        return None
    max_amount = min(treasury, 3000)
    amount = 100
    while amount <= max_amount:
        test_terms = copy.deepcopy(terms)
        test_terms.setdefault("sweeteners", []).append(
            {"type": "gold_lump", "value": int(amount)}
        )
        result = calculate_acceptance(test_terms, world)
        if result["score"] >= accept_threshold:
            return test_terms
        amount += 100
    return None


def _try_add_desired_clauses(
    terms: Dict, source_nation: str, world, accept_threshold: int = 50,
    payer_nation: str = "", gold_only: bool = False,
) -> Optional[Dict]:
    """Try adding the cheapest desired clause from the nation's desire table.

    The countering nation picks from ITS desire table; the sweetener is paid
    by the proposing side (`payer_nation`, defaulting to source_nation for
    the M3 direction where author and payer coincide). See NATION_DESIRES
    design note above.

    R125: accept_threshold is personality-driven (hawk=60, dove=40, default=50).

    Returns modified terms if score reaches >= accept_threshold, otherwise None.
    """
    import copy

    payer = payer_nation or source_nation
    desires = NATION_DESIRES.get(source_nation, [])
    if not desires:
        return None

    # Try each desire in order (cheapest/most preferred first)
    for desire in desires:
        test_terms = copy.deepcopy(terms)
        dtype = desire.get("type", "")

        # G4F-13: player-sent counters only walk gold desires — the
        # territory/clause entries carry M3 (author-cedes) semantics.
        if gold_only and dtype not in ("gold_lump", "gold_per_turn"):
            continue

        # Add as a sweetener from the AI nation to France.
        # July 2026 AI audit: "territory" REMOVED from the offerable set —
        # it carried only a numeric value (no region identity), scored +8
        # acceptance, and was inert at ratification: the player accepted a
        # promise that never executed. Re-adding it requires real region
        # selection + ratification wiring (routed to the 8.EVAL diplomacy
        # triage in ROADMAP.md).
        if dtype in ("gold_lump", "gold_per_turn"):
            sweetener_value = max(5, int(desire.get("value", 0)))
            # R113: Validate gold sweetener against the PAYER's treasury
            # (prevent negative gold)
            if dtype == "gold_lump":
                nation_gold = world.nation_gold.get(payer, 0)
                if nation_gold < sweetener_value:
                    continue  # Can't afford this sweetener
            # R113: Validate gold_per_turn against the PAYER's income
            # (prevent unsustainable offers)
            if dtype == "gold_per_turn":
                income_data = world.calculate_turn_income(payer)
                max_per_turn = income_data["income"] // 2  # 50% of region income
                if max_per_turn <= 0:
                    continue
                sweetener_value = min(sweetener_value, max_per_turn)
            test_terms["sweeteners"].append({
                "type": dtype,
                "value": sweetener_value,
            })
        elif dtype in ("open_borders", "protection"):
            clause_key = desire.get("clause", dtype)
            if clause_key not in test_terms.get("clauses", []):
                test_terms["clauses"].append(clause_key)
            else:
                continue  # Already present, skip

        result = calculate_acceptance(test_terms, world)
        if result["score"] >= accept_threshold:
            return test_terms

    return None


# ═══════════════════════════════════════════════════════════════
# CONFLICTING ALLIANCE CHECK (§5b.3)
# ═══════════════════════════════════════════════════════════════

def check_alliance_conflict(
    nation: str, new_state: str, world
) -> Optional[Dict]:
    """Check if accepting an alliance with a nation would create a conflict.

    §5b.3: When accepting would create ALLIANCE or DEFENSIVE_ALLIANCE with
    a nation, check if France is at WAR with any of that nation's existing
    ALLIANCE/DEFENSIVE_ALLIANCE partners.

    Args:
        nation: The nation France would form an alliance with.
        new_state: The proposed new diplomatic state (e.g. "ALLIANCE").
        world: WorldState

    Returns:
        Conflict info dict if conflict exists:
            {
                "conflicting_nations": [list of nations],
                "alliance_nation": str,
                "new_state": str,
                "message": str,
            }
        None if no conflict.
    """
    # Only relevant for alliance-type states
    if new_state not in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
        return None

    player = getattr(world, 'player_nation', 'France')
    all_nations = [player] + list(getattr(world, 'enemy_nations', []))

    conflicting = []

    for other_nation in all_nations:
        if other_nation == player or other_nation == nation:
            continue

        # Direction 1: Check if 'nation' has an alliance with 'other_nation' who France is at WAR with
        state_with_other = world.get_diplomatic_state(nation, other_nation)
        if state_with_other in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
            if world.is_at_war(player, other_nation):
                if other_nation not in conflicting:
                    conflicting.append(other_nation)

        # R114: Direction 2: Check if France's allies are at WAR with proposed nation
        france_state = world.get_diplomatic_state(player, other_nation)
        if france_state in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
            if world.is_at_war(other_nation, nation):
                if other_nation not in conflicting:
                    conflicting.append(other_nation)

    if not conflicting:
        return None

    conflict_names = ", ".join(conflicting)
    return {
        "conflicting_nations": conflicting,
        "alliance_nation": nation,
        "new_state": new_state,
        "message": (
            f"Warning: Accepting {new_state.replace('_', ' ').title()} with "
            f"{nation} would conflict with our war against {conflict_names}. "
            f"{nation} has existing alliance obligations to "
            f"{conflict_names}."
        ),
    }


# ═══════════════════════════════════════════════════════════════
# AI-AI DIPLOMACY (§9c) — Session 8D
# ═══════════════════════════════════════════════════════════════

def _process_ai_ai_rivalry(world) -> List[Dict]:
    """R15: AI-AI diplomacy degradation.

    Trigger 1 — Adjacency Rivalry: AI nations controlling adjacent regions AND relation > 0 → -3 rel/turn.
    Trigger 2 — Opportunistic Downgrade: AI nation with troops > 2x another AND relation < +30 → one-step downgrade.

    Returns events list for campaign log.
    """
    player = getattr(world, 'player_nation', 'France')
    enemy_nations = list(getattr(world, 'enemy_nations', []))
    events = []

    # Build territory map: nation → set of regions
    nation_regions: Dict[str, set] = {}
    for rname, region in world.regions.items():
        ctrl = getattr(region, 'controller', None)
        if ctrl and ctrl != player:
            nation_regions.setdefault(ctrl, set()).add(rname)

    # Build troop counts per nation
    nation_troops: Dict[str, int] = {}
    for marshal in world.marshals.values():
        if marshal.nation != player:
            nation_troops[marshal.nation] = nation_troops.get(marshal.nation, 0) + getattr(marshal, 'strength', 0)

    downgraded_this_turn: set = set()  # Track pairs already downgraded

    # Build set of nations currently at war with the player
    nations_at_war_with_player = set()
    for diplo_key_check, state_check in world.diplomatic_states.items():
        if state_check == "WAR" and player in diplo_key_check:
            parts = diplo_key_check.split("|")
            for p in parts:
                if p != player:
                    nations_at_war_with_player.add(p)

    for i, nation_a in enumerate(enemy_nations):
        for nation_b in enemy_nations[i + 1:]:
            diplo_key = world._make_diplo_key(nation_a, nation_b)
            relation = world.nation_relations.get(diplo_key, 0)
            state = world.diplomatic_states.get(diplo_key, "PEACE")

            # Skip rivalry when both nations share a common enemy (player)
            both_at_war = (nation_a in nations_at_war_with_player and
                           nation_b in nations_at_war_with_player)

            # Trigger 1: Adjacency Rivalry — skip if fighting common enemy
            if relation > 0 and not both_at_war:
                regions_a = nation_regions.get(nation_a, set())
                regions_b = nation_regions.get(nation_b, set())
                adjacent = False
                for rname in regions_a:
                    region_obj = world.regions.get(rname)
                    if region_obj:
                        for adj in getattr(region_obj, 'adjacent_regions', []):
                            if adj in regions_b:
                                adjacent = True
                                break
                    if adjacent:
                        break
                if adjacent:
                    old_relation = relation
                    world.modify_nation_relation(nation_a, nation_b, -3)
                    new_relation = world.nation_relations.get(diplo_key, 0)
                    # Only emit event when crossing a threshold (every 10 points)
                    # to reduce spam — the relation change always happens silently
                    old_bracket = old_relation // 10
                    new_bracket = new_relation // 10
                    if old_bracket != new_bracket:
                        events.append({
                            "type": "ai_ai_rivalry",
                            "nations": [nation_a, nation_b],
                            "message": f"Territorial rivalry between {nation_a} and {nation_b} grows.",
                        })

            # Trigger 2: Opportunistic Downgrade — skip if fighting common enemy
            if not both_at_war and relation < 30 and state != "PEACE" and state != "WAR" and state != "ARMISTICE" and state != "VASSAL":
                pair_key = f"{nation_a}|{nation_b}"
                if pair_key not in downgraded_this_turn:
                    troops_a = nation_troops.get(nation_a, 0)
                    troops_b = nation_troops.get(nation_b, 0)
                    stronger, weaker = (nation_a, nation_b) if troops_a > troops_b else (nation_b, nation_a)
                    stronger_troops = max(troops_a, troops_b)
                    weaker_troops = min(troops_a, troops_b)
                    if weaker_troops > 0 and stronger_troops > 2 * weaker_troops:
                        from backend.game_logic.diplomacy import _DOWNGRADE_ORDER, DOWNGRADE_PENALTIES
                        if state in _DOWNGRADE_ORDER:
                            idx = _DOWNGRADE_ORDER.index(state)
                            if idx < len(_DOWNGRADE_ORDER) - 1:
                                new_state = _DOWNGRADE_ORDER[idx + 1]
                                from backend.game_logic.diplomacy import set_diplomatic_state
                                set_diplomatic_state(world, nation_a, nation_b, new_state, "ai_ai_downgrade")
                                # Apply relation penalty from DOWNGRADE_PENALTIES
                                penalty_key = (state, new_state)
                                penalty = DOWNGRADE_PENALTIES.get(penalty_key, {})
                                rel_hit = penalty.get("relation_target", -10)
                                world.modify_nation_relation(nation_a, nation_b, rel_hit)
                                downgraded_this_turn.add(pair_key)
                                events.append({
                                    "type": "ai_ai_downgrade",
                                    "nations": [nation_a, nation_b],
                                    "from_state": state,
                                    "to_state": new_state,
                                    "message": f"{stronger} has downgraded relations with {weaker}: {state} → {new_state}.",
                                })

    return events


_AI_AI_MAX_TREATIES_PER_TURN = 2


def _process_ai_sponsorships(world) -> List[Dict]:
    """AI-2c/§3.1 — the SPONSOR branch, AI-side (GR5's other direction):
    a sponsor-first court (Russia, Britain — the §3.4 statecraft table)
    with a real purse funds another court's live design against the
    same obstacle. 'Britain's gold appearing in a war it never joined'
    — §3.4's witnessed politics. At most AI_SPONSORSHIPS_PER_TURN new
    patronages per turn (the narration budget); the record is the same
    AI-2b directed sponsorship the player mints, bond included.
    Deckless worlds: every court is indifferent → no-op (pin 18)."""
    from backend.game_logic.instruments import (
        grant_directed_sponsorship,
        standing_sponsorship_amount,
    )
    from backend.game_logic.intent import get_nation_intent

    player = getattr(world, "player_nation", "France")
    events: List[Dict] = []
    from backend.game_logic.diplomacy import _is_nation_eliminated
    active = [n for n in getattr(world, "enemy_nations", [])
              if n in set(world.get_active_nations())
              and not _is_nation_eliminated(world, n)]
    for payer in active:
        if len(events) >= AI_SPONSORSHIPS_PER_TURN:
            break
        statecraft = world.get_statecraft(payer)
        if "sponsor" not in (statecraft.get("reaches_first") or ()):
            continue
        treasury = int(world.nation_gold.get(payer, 0))
        if treasury < AI_SPONSOR_MIN_TREASURY:
            continue
        payer_view = get_nation_intent(payer, world)
        aim = payer_view.against
        if not aim or payer_view.want_id is None:
            continue
        from backend.game_logic.agendas import get_paymaster_subsidy_amount
        amount = int(get_paymaster_subsidy_amount(world, payer))
        if treasury < amount * 4:  # must be able to sustain the term
            continue
        for recipient in active:
            if recipient in (payer, aim) or recipient == player:
                continue
            view = get_nation_intent(recipient, world)
            if (view.want_id is None or view.survival
                    or view.against != aim):
                continue
            if standing_sponsorship_amount(world, payer, recipient) > 0:
                continue
            result = grant_directed_sponsorship(
                world, payer=payer, recipient=recipient, aim=aim,
                amount_per_turn=amount)
            events.append(result["event"])
            break
    return events


def process_allegiance_auctions(world) -> List[Dict]:
    """§12.6 — the allegiance auction: a minor whose intent crests at
    `bandwagon` has its flip ANNOUNCED as in play (the Courier beat),
    stays biddable for ALLEGIANCE_AUCTION_WINDOW turns (the D5
    instruments are the bids — sponsor the minor, court its relations),
    then resolves to the best-standing suitor: lean (relations) plus
    standing patronage. A player-won auction arrives as a mailbox offer
    the player may still refuse; an AI winner ratifies the pact
    directly (the auction WAS the consent). A crest that passes before
    resolution lapses the auction — §3.1a: a reading, never a latch.

    Boot-dormant on 1805 (no minor crests at bandwagon at boot, pinned)
    and deckless-silent (pin 18: indifferent courts never crest)."""
    from backend.game_logic.instruments import standing_sponsorship_amount
    from backend.game_logic.intent import get_nation_intent
    from backend.nation_config import _POWER_TIER_DEFAULT

    events: List[Dict] = []
    player = getattr(world, "player_nation", "France")
    turn = int(world.current_turn)
    auctions = getattr(world, "allegiance_auctions", {})
    active = set(world.get_active_nations())

    # ── Open new auctions (announce the flip) ──
    for nation in getattr(world, "enemy_nations", []):
        if nation in auctions or nation not in active:
            continue
        tier = world.get_power_tier(nation) or _POWER_TIER_DEFAULT
        if tier not in ("minor", "secondary"):
            continue
        view = get_nation_intent(nation, world)
        if view.price != "bandwagon" or view.survival:
            continue
        auctions[nation] = {
            "opened_turn": turn,
            "resolves_turn": turn + int(ALLEGIANCE_AUCTION_WINDOW),
        }
        event = {
            "type": "allegiance_auction_opened",
            "nation": nation,
            "resolves_turn": turn + int(ALLEGIANCE_AUCTION_WINDOW),
            "turn": turn,
        }
        world.log_event(event)
        events.append(event)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "allegiance_in_play",
                             {"nation": nation}, "always")
        from backend.notifications import (
            DIPLOMATIC_PROPOSAL,
            NotificationPriority,
            create_notification,
        )
        world.notifications.add(create_notification(
            DIPLOMATIC_PROPOSAL,
            NotificationPriority.HIGH,
            f"{nation}'s allegiance is in play",
            (f"The court of {nation} weighs its allegiance — the flip "
             f"resolves within {int(ALLEGIANCE_AUCTION_WINDOW)} turns. "
             f"Sponsorship and standing win it."),
            turn,
        ))

    # ── Resolve or lapse due auctions ──
    for nation, record in list(auctions.items()):
        if nation not in active:
            del auctions[nation]
            continue
        view = get_nation_intent(nation, world)
        if view.price != "bandwagon":
            del auctions[nation]
            event = {
                "type": "allegiance_auction_resolved",
                "nation": nation, "winner": None,
                "outcome": "lapsed", "turn": turn,
            }
            world.log_event(event)
            events.append(event)
            continue
        if turn < int(record.get("resolves_turn", turn)):
            continue

        # Suitors: the raw hegemon, the player, and the next-ranked bloc
        # leader — nobody at war with the minor bids.
        from backend.game_logic.agendas import _hegemon
        from backend.game_logic.coalition import identify_ranked_bloc_shares
        suitors: List[str] = []
        hegemon, _share = _hegemon(world)
        for leader, _s in (identify_ranked_bloc_shares(world) or [])[:2]:
            if leader:
                suitors.append(leader)
        if hegemon:
            suitors.append(hegemon)
        suitors.append(player)
        seen = []
        for suitor in suitors:
            if (suitor and suitor != nation and suitor not in seen
                    and not world.is_at_war(nation, suitor)):
                seen.append(suitor)
        best, best_score = None, None
        for suitor in seen:
            relation = int(world.nation_relations.get(
                world._make_diplo_key(nation, suitor), 0) or 0)
            patronage = (standing_sponsorship_amount(world, suitor, nation)
                         // int(AUCTION_SPONSORSHIP_LEAN_DIVISOR))
            score = relation + patronage
            if best_score is None or (score, suitor) > (best_score, best):
                best, best_score = suitor, score
        del auctions[nation]

        if best is None:
            event = {
                "type": "allegiance_auction_resolved",
                "nation": nation, "winner": None,
                "outcome": "no_suitor", "turn": turn,
            }
            world.log_event(event)
            events.append(event)
            continue

        if best == player:
            # The player wins the bidding — the pact still arrives as an
            # OFFER (never an imposed ally): the minor proposes.
            terms = _build_proposal_terms(nation, "defensive_alliance", 0,
                                          world)
            proposal = _make_proposal(nation, "defensive_alliance", 9,
                                      terms, world)
            deliver_ai_proposal(proposal, world)
            outcome = "player_offer"
        else:
            state = world.get_diplomatic_state(nation, best)
            if state not in ("DEFENSIVE_ALLIANCE", "ALLIANCE", "WAR"):
                world._ratify_treaty({
                    "type": "defensive_alliance",
                    "proposer_nation": nation,
                    "target_nation": best,
                    "sweeteners": [], "demands": [], "clauses": [],
                })
            outcome = "flipped"
        event = {
            "type": "allegiance_auction_resolved",
            "nation": nation, "winner": best,
            "outcome": outcome, "turn": turn,
        }
        world.log_event(event)
        events.append(event)

    world.allegiance_auctions = auctions
    return events


def process_ai_ai_diplomatic_phase(world) -> List[Dict]:
    """Process diplomatic proposals between AI nations (excluding France).

    Called from advance_turn() after the existing AI proposal phase.
    Anti-spam: max 2 AI-AI treaties per turn total.

    Returns list of treaty event dicts (for campaign log wiring).
    """
    # R15: Process AI-AI rivalry degradation first
    rivalry_events = _process_ai_ai_rivalry(world)

    # AI-2c: the sponsor branch — patronage before proposals, so a
    # freshly funded court still evaluates its own asks this turn.
    sponsorship_events = _process_ai_sponsorships(world)
    rivalry_events = rivalry_events + sponsorship_events

    # §12.6: the allegiance auction — announce/resolve minors' flips.
    rivalry_events = rivalry_events + process_allegiance_auctions(world)

    enemy_nations = list(getattr(world, 'enemy_nations', []))
    treaties_this_turn = 0
    events = []

    # R81: Filter out eliminated nations (0 regions + 0 marshals)
    from backend.game_logic.diplomacy import _is_nation_eliminated
    active_nations = [n for n in enemy_nations if not _is_nation_eliminated(world, n)]

    for i, initiator in enumerate(active_nations):
        if treaties_this_turn >= _AI_AI_MAX_TREATIES_PER_TURN:
            break

        for target in active_nations[i + 1:]:
            if treaties_this_turn >= _AI_AI_MAX_TREATIES_PER_TURN:
                break

            proposal = _evaluate_ai_ai_proposal(initiator, target, world)
            if not proposal:
                continue

            # AI-2a (§4.2 seam 3): resolution converged into ONE arm both
            # the trigger loop above and a recipient-addressed
            # deliver_ai_proposal reach. Ratify outcomes are byte-identical
            # to the pre-AI-2a inline block; the refusal moment is NEW —
            # it did not exist on this path at all (§5 pin 8's substrate).
            event = _resolve_ai_ai_proposal(proposal, world)
            if event and event.get("type") != "ai_ai_proposal_refused":
                events.append(event)
                treaties_this_turn += 1

    return rivalry_events + events


def _resolve_ai_ai_proposal(proposal: Dict, world) -> Optional[Dict]:
    """Resolve a court-to-court proposal: acceptance both sides → ratify,
    else record the refusal (serialized) and emit its public event.

    AI-2a decision, AMENDED by AI-2c as promised (§4.2 seam 3 — the
    counter-offer arm): the statecraft weighting now exists, so a
    HAGGLING recipient (Metternich, Hardenberg, Castlereagh — never
    Alexander) whose refusal fell in the near-miss band
    [HAGGLE_BAND_FLOOR, 50) answers with the one counter a court can
    make without a table: the same ask one rung down the upgrade
    ladder. Both sides re-score the downgraded type; dual consent
    ratifies it (the event carries `countered: True`), anything else
    falls through to the refusal record exactly as before. Courts that
    do not haggle keep the AI-2a accept-or-refuse arm byte-identically.
    """
    # Two envelope shapes reach this arm: the trigger loop's minimal
    # {"type", "proposer", "target"} and _make_proposal's full
    # {"proposal_type", "source", "recipient", "terms"} — normalise both.
    terms = proposal.get("terms") or {}
    initiator = (proposal.get("proposer") or proposal.get("source")
                 or terms.get("proposer_nation"))
    target = (proposal.get("target") or proposal.get("recipient")
              or terms.get("target_nation"))
    ptype = (proposal.get("type") or terms.get("type")
             or proposal.get("proposal_type"))
    if not initiator or not target or not ptype:
        return None

    # AI-2 (§4.2 trigger 0a): a bare court-to-court DESIGN ASK is never
    # satisfiable by agreement in Stage C — territorial AI-AI transfer
    # lands with AI-4's third-party settlements. A court does not hand
    # over provinces for a polite request; the ask exists to be refused,
    # and the refusal IS the deliverable (§5 pin 8's record + the
    # fog-visible event AI-3's ladder gate escalates from).
    if ptype == "design_ask":
        if record_diplomatic_refusal(world, initiator, target, ptype):
            event = {
                "type": "ai_ai_proposal_refused",
                "proposer": initiator,
                "recipient": target,
                "refused_by": target,
                "proposal_type": ptype,
                "turn": int(world.current_turn),
            }
            world.log_event(event)
            return event
        return None

    scored = {"type": ptype, "proposer": initiator, "target": target}

    acceptance_a = _ai_ai_acceptance(scored, initiator, target, world)
    acceptance_b = _ai_ai_acceptance(scored, target, initiator, world)

    if acceptance_a >= 50 and acceptance_b >= 50:
        # Ratify immediately via unified path (no transit delay for AI-AI)
        normalized = {
            "type": ptype,
            "proposer_nation": initiator,
            "target_nation": target,
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        return world._ratify_treaty(normalized)

    # AI-2c: the haggle arm — a near-miss refusal from a court that
    # bargains resolves as one step down the ladder when both sides
    # would sign THAT. Upgrade-family types only; everything else keeps
    # the accept-or-refuse shape.
    from backend.game_logic.statecraft import HAGGLE_BAND_FLOOR, haggles
    if (acceptance_a >= 50 and HAGGLE_BAND_FLOOR <= acceptance_b < 50
            and haggles(world, target)):
        from backend.game_logic.diplomacy import _UPGRADE_ORDER
        asked_state = ptype.upper()
        # Never counter below OPEN_BORDERS — "one step down" from there
        # is the war/peace family, which is not a haggle.
        if (asked_state in _UPGRADE_ORDER
                and _UPGRADE_ORDER.index(asked_state)
                > _UPGRADE_ORDER.index("OPEN_BORDERS")):
            lower = _UPGRADE_ORDER[
                _UPGRADE_ORDER.index(asked_state) - 1].lower()
            scored_lower = {"type": lower, "proposer": initiator,
                            "target": target}
            if (_ai_ai_acceptance(scored_lower, initiator, target,
                                  world) >= 50
                    and _ai_ai_acceptance(scored_lower, target,
                                          initiator, world) >= 50):
                normalized = {
                    "type": lower,
                    "proposer_nation": initiator,
                    "target_nation": target,
                    "sweeteners": [],
                    "demands": [],
                    "clauses": [],
                }
                event = world._ratify_treaty(normalized)
                if isinstance(event, dict):
                    event["countered"] = True
                    event["asked_type"] = ptype
                return event

    # The refusal moment (AI-2a seam 5): the ask happened and was rebuffed
    # — put it on the serialized record and in the campaign log, ONCE per
    # (pair, type) per dedupe window, so the every-turn trigger re-poll
    # does not spam either. AI-3's ladder gate reads this record.
    # Review fix [7]/[15]: ONLY a recipient-side refusal is a refusal.
    # When the proposer's OWN acceptance balks (a < 50 <= b), the ask
    # never truly happened — recording it would write a false "the
    # recipient said no" onto the record AI-3 escalates from, and the
    # one-liner would read "{X} rebuffs {X}". Pre-refactor this dual-
    # consent failure was silent; it stays silent.
    if acceptance_b >= 50:
        return None
    if record_diplomatic_refusal(world, initiator, target, ptype):
        event = {
            "type": "ai_ai_proposal_refused",
            "proposer": initiator,
            "recipient": target,
            "refused_by": target,
            "proposal_type": ptype,
            "turn": int(world.current_turn),
        }
        world.log_event(event)
        return event
    return None


def _evaluate_ai_ai_proposal(nation_a: str, nation_b: str, world) -> Optional[Dict]:
    """Evaluate if two AI nations should propose to each other.

    Trigger conditions (per the spec):
    1. Both at WAR with France AND relation > -20 → DEFENSIVE_ALLIANCE
    2. One losing badly (war_score < -40) AND other at peace → NON_AGGRESSION
    3. Both at PEACE with France AND relation > +40 → upgrade treaty one step
    4. One gold < 200 AND other gold > 400 → trade deal (open_borders)
    """
    # R43: Per-pair cooldown for AI-AI proposals
    diplo_key = world._make_diplo_key(nation_a, nation_b)
    cooldowns = _get_cooldowns(world)
    if cooldowns.get(f"ai_ai|{diplo_key}", 0) > 0:
        return None

    player = getattr(world, 'player_nation', 'France')

    state_a_france = world.get_diplomatic_state(nation_a, player)
    state_b_france = world.get_diplomatic_state(nation_b, player)
    state_ab = world.get_diplomatic_state(nation_a, nation_b)

    diplo_key_ab = world._make_diplo_key(nation_a, nation_b)
    relation_ab = world.nation_relations.get(diplo_key_ab, 0)

    # ── Trigger 0 (AI-2, §4.2): intent-driven court-to-court asks ──
    # Deckless worlds skip both arms byte-identically (pin 18: every
    # court reads `indifferent`).
    from backend.game_logic.intent import get_nation_intent
    for proposer, target in ((nation_a, nation_b), (nation_b, nation_a)):
        view = get_nation_intent(proposer, world)
        if view.want_id is None or view.survival:
            continue
        # 0a — THE DESIGN ASK: the obstacle is the other court, and the
        # proposer stands at ask/buy. Court-to-court territorial
        # transfer by agreement lands with AI-4's settlements; in
        # Stage C the ask exists to be REFUSED — the §5 pin 8 record
        # and the fog-visible refusal event are the ladder's substrate.
        if (view.against == target and view.price in ("ask", "buy")
                and not world.is_at_war(proposer, target)):
            return {"type": "design_ask", "proposer": proposer,
                    "target": target}
        # 0b — THE ALIGNMENT ASK: a court at `align` courts the enemies
        # of its obstacle ("Vienna seeks a Russian guarantee"). The
        # target must itself be cold toward the obstacle, and the pact
        # must be new ground for the pair.
        if (view.price in ("align", "bandwagon") and view.against
                and view.against not in (target, player)
                and state_ab not in ("DEFENSIVE_ALLIANCE", "ALLIANCE")
                and relation_ab > -10):
            obstacle_key = world._make_diplo_key(target, view.against)
            target_cold = (world.is_at_war(target, view.against)
                           or int(world.nation_relations.get(
                               obstacle_key, 0) or 0) < 0)
            if target_cold:
                return {"type": "defensive_alliance", "proposer": proposer,
                        "target": target}

    # Trigger 1: Both at war with France, relation > -20 → DEFENSIVE_ALLIANCE
    if (state_a_france == "WAR" and state_b_france == "WAR"
            and relation_ab > -20
            and state_ab not in ("DEFENSIVE_ALLIANCE", "ALLIANCE")):
        return {"type": "defensive_alliance", "proposer": nation_a, "target": nation_b}

    # Trigger 2: One losing badly, other at peace → NON_AGGRESSION
    if state_a_france == "WAR" and state_b_france != "WAR":
        ws = _get_war_score_for_nation(nation_a, player, world)
        if ws < -40 and state_ab not in ("NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE"):
            return {"type": "non_aggression", "proposer": nation_a, "target": nation_b}
    if state_b_france == "WAR" and state_a_france != "WAR":
        ws = _get_war_score_for_nation(nation_b, player, world)
        if ws < -40 and state_ab not in ("NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE"):
            return {"type": "non_aggression", "proposer": nation_b, "target": nation_a}

    # Trigger 3: Both at peace, relation > +40 → upgrade one step
    if (state_a_france != "WAR" and state_b_france != "WAR"
            and relation_ab > 40):
        from backend.game_logic.diplomacy import _UPGRADE_ORDER
        if state_ab in _UPGRADE_ORDER:
            idx = _UPGRADE_ORDER.index(state_ab)
            if idx < len(_UPGRADE_ORDER) - 1:
                next_state = _UPGRADE_ORDER[idx + 1]
                return {"type": next_state.lower(), "proposer": nation_a, "target": nation_b}

    # Trigger 4: One gold < 200, other gold > 400 → open_borders
    gold_a = world.nation_gold.get(nation_a, 0)
    gold_b = world.nation_gold.get(nation_b, 0)
    if state_ab in ("PEACE", "WAR", "ARMISTICE"):
        if gold_a < 200 and gold_b > 400 and state_ab == "PEACE":
            return {"type": "open_borders", "proposer": nation_a, "target": nation_b}
        if gold_b < 200 and gold_a > 400 and state_ab == "PEACE":
            return {"type": "open_borders", "proposer": nation_b, "target": nation_a}

    # Trigger 5: Preemptive alliance — both threatened by France (N1)
    threat = int(getattr(world, 'threat_level', 0))
    if threat > 40:
        if (state_a_france != "WAR" and state_b_france != "WAR"
                and state_ab not in ("DEFENSIVE_ALLIANCE", "ALLIANCE")):
            # Both must have negative relation with France and not be friendly
            rel_a_france = world.nation_relations.get(
                world._make_diplo_key(nation_a, player), 0)
            rel_b_france = world.nation_relations.get(
                world._make_diplo_key(nation_b, player), 0)
            # Neither has NON_AGGRESSION+ with France
            has_pact_a = state_a_france in ("NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE")
            has_pact_b = state_b_france in ("NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE")
            if (rel_a_france < 0 and rel_b_france < 0
                    and not has_pact_a and not has_pact_b
                    and relation_ab > -10):
                return {"type": "defensive_alliance", "proposer": nation_a, "target": nation_b}

    return None


def _ai_ai_acceptance(proposal: Dict, evaluator: str, other: str, world) -> int:
    """Simplified acceptance check for AI-AI proposals.

    Uses the same calculate_acceptance formula but with AI nations.
    """
    # Build a proposal dict compatible with calculate_acceptance.
    # July 2026 AI audit: the proposer must be the COUNTERPARTY from the
    # evaluator's perspective. The old proposal.get("proposer", other)
    # made the initiator-side check evaluate a SELF-PAIR (initiator vs
    # itself), which never scored >= 50 — the entire AI-AI treaty phase
    # was dead (zero AI-AI treaties ever ratified).
    acceptance_proposal = {
        "type": proposal["type"],
        "proposer_nation": other,
        "target_nation": evaluator,
        "sweeteners": [],
        "demands": [],
        "clauses": [],
    }
    result = calculate_acceptance(acceptance_proposal, world)
    return result["score"]


    # _ratify_ai_ai_treaty removed (R107/R108) — unified into WorldState._ratify_treaty()


# ═══════════════════════════════════════════════════════════════
# SETTLEMENT OFFER PRODUCER (SC-5 reversal / Slice G1 commit 1)
# ═══════════════════════════════════════════════════════════════
#
# `process_settlement_offer_phase(world)` is the gameplay-natural
# producer that replaces the previous SC-5 defer-and-hide stance.
#
# Scope (this commit):
#   - Backend production only. Produced offers live in
#     `world.pending_settlement_dialogues`. No mailbox, notification,
#     dispatch, popup-queue, or Godot surface is touched in this
#     commit; commit 2 wires the UI promotion layer.
#   - Triggers for active multi-party (3+ participant) war_instances
#     where the player is a participant on one side and the opposing
#     side leader is an AI nation.
#   - Cooldown: `SETTLEMENT_OFFER_COOLDOWN_TURNS` turns per `war_id`
#     after the most recent offer, tracked in
#     `world.ai_settlement_cooldowns[war_id]` as the next-allowed turn.
#   - One-active-offer guard: skip if `pending_settlement_dialogues`
#     already carries an `incoming_settlement_offer` entry for the
#     same `war_id`.
#   - Stable offer identity: `offer_id="settlement_offer:{war_id}:
#     {turn}:{seq}"` where `seq` is a per-(war_id, turn) monotonic
#     counter derived from existing offers.
#   - Terms: `[{"type": "peace"}, {"type": "gold_indemnity", ...}]`
#     with a deterministic amount based on the war's age. Other clause
#     types (territory_cede, forced_alliance, dependency) are reserved
#     for SC-32 / Slice G2 follow-through where the producer can
#     reason about side_pressure_score and beneficial direction.
#
# Out of scope (commit 2 or later):
#   - Promotion into `dialogue_manager`, mailbox payloads, notifications,
#     dispatch events, popup-queue entries, Godot popup routing, Voice
#     Bible §16.1 incoming-offer voice families, `Request Revision`
#     counter/edit route, request-terms lifecycle.

SETTLEMENT_OFFER_COOLDOWN_TURNS = 5
SETTLEMENT_OFFER_MIN_WAR_DURATION_TURNS = 2
SETTLEMENT_OFFER_MULTI_PARTY_MIN_PARTICIPANTS = 3
SETTLEMENT_OFFER_BASE_GOLD_AMOUNT = 500
SETTLEMENT_OFFER_PER_DURATION_BONUS = 50
SETTLEMENT_OFFER_MAX_GOLD_AMOUNT = 2000
# EC-W4 "Peace with Teeth" (memo ECON_WAR_COUPLING_RESEARCH_2026_07_17 §3):
# indemnities price to the LOSER'S PURSE — Pressburg/Tilsit-style terms
# measured against the treasury, not a flat cap. The July-17 playtest saw
# Britain (+24 war score) demand 600g of a 61,000g French hoard (~1%).
# demand = min(base + duration + |war_score|×PER_SCORE + treasury×FRACTION,
#              treasury × MAX_FRACTION)
# The old flat SETTLEMENT_OFFER_MAX_GOLD_AMOUNT cap survives only as the
# fallback when the payer's treasury is unreadable. Sweep-tunable.
SETTLEMENT_OFFER_TREASURY_FRACTION = 0.15
SETTLEMENT_OFFER_MAX_TREASURY_FRACTION = 0.40
SETTLEMENT_OFFER_PER_WAR_SCORE = 40
# AUD-c (8.EVAL Batch Q, July 16 2026): the incoming multi-party settlement
# offer used to hard-code the indemnity direction (player ALWAYS pays), so a
# player who was clearly WINNING still got dunned for reparations. The offer is
# now war-score-aware. When the player leads the opposing leader by at least this
# band the losing AI offers CONCESSIONS (it pays the player); when the player
# trails by the band the player pays reparations (the historical framing); a war
# inside the band settles as a white peace (peace clause, no indemnity). Balance
# number (escalates to the gate).
SETTLEMENT_OFFER_DECISIVE_WAR_SCORE = 20

# SC-30 / Slice G1 — the Request Terms lifecycle. A player request is
# answered on the next AI diplomatic phase: GRANTED (the answering leader
# authors a real incoming offer through the normal producer path) unless
# the answering side is decisively winning, in which case the court
# REFUSES with voice and the request enters its own cooldown.
REQUEST_TERMS_COOLDOWN_TURNS = 5
REQUEST_TERMS_REFUSAL_WAR_SCORE = 30


def _settlement_offer_next_seq(
    pending: List[Dict],
    *,
    war_id: str,
    current_turn: int,
) -> int:
    """Per-(war_id, turn) monotonic counter for offer_id stability.

    The one-active-offer guard normally caps existing offers per war
    at 1, so `seq` is `1` in normal flow. The counter remains for
    audit-trail clarity and future producers (e.g. SC-32) that may
    legitimately re-author within the same turn after explicit
    cleanup.
    """
    seq = 1
    prefix = f"settlement_offer:{war_id}:{current_turn}:"
    for entry in pending:
        if not isinstance(entry, dict):
            continue
        if entry.get("type") != "incoming_settlement_offer":
            continue
        if str(entry.get("offer_id") or "").startswith(prefix):
            seq += 1
    return seq


def _settlement_offer_already_pending(
    pending: List[Dict],
    *,
    war_id: str,
) -> bool:
    """One-active-offer-per-war guard for unpromoted producer storage."""
    for entry in pending:
        if not isinstance(entry, dict):
            continue
        if entry.get("type") != "incoming_settlement_offer":
            continue
        if str(entry.get("war_id") or "") == war_id:
            return True
    return False


def _settlement_offer_already_promoted(world, *, war_id: str) -> bool:
    """One-active-offer-per-war guard for promoted mailbox entries."""
    dm = getattr(world, "dialogue_manager", None)
    if dm is None:
        return False
    candidates = []
    current = getattr(dm, "_current", None)
    if isinstance(current, dict):
        candidates.append(current)
    candidates.extend(
        item for item in (getattr(dm, "_queue", None) or [])
        if isinstance(item, dict)
    )
    for entry in candidates:
        if entry.get("type") != "incoming_settlement_offer":
            continue
        if str(entry.get("war_id") or "") == war_id:
            return True
    return False


def _settlement_offer_opposing_side_leader(
    war: Dict,
    *,
    player_side: str,
) -> Optional[str]:
    """Return the leader of the side NOT containing the player."""
    opposing_side = "defenders" if player_side == "attackers" else "attackers"
    leader_key = (
        "defender_leader" if opposing_side == "defenders" else "attacker_leader"
    )
    leader = war.get(leader_key)
    if not leader:
        return None
    return str(leader)


def _settlement_offer_build_terms(
    *,
    player: str,
    proposer_nation: str,
    war_age_turns: int,
    player_war_score: int = 0,
    world=None,
) -> List[Dict]:
    """Deterministic peace + (war-score-directed) gold_indemnity package.

    AUD-c: the indemnity DIRECTION follows the war score from the player's
    perspective against the opposing leader (`proposer_nation`):
    - player winning by >= the decisive band → the losing AI pays the player
      (concession); the player finally sees a favourable offer.
    - player losing by >= the band → the player pays reparations (the historical
      "settle now, pay to end it" framing; unchanged from before).
    - inside the band → a white peace: the `peace` clause with no indemnity.
    The player can still reject or counter through the editor.

    EC-W4: the AMOUNT prices to the payer's purse (memo §3) — base + war-age
    + |war_score|×PER_SCORE + treasury×FRACTION, capped at treasury×
    MAX_FRACTION so a court is never dunned past what it can plausibly pay
    (a bankrupt payer → white peace). GR5: both directions read the actual
    payer's treasury through the same math. Without `world` (legacy direct
    calls) the pre-EC-W4 flat sizing is preserved.
    """
    duration_bonus = max(0, war_age_turns) * SETTLEMENT_OFFER_PER_DURATION_BONUS
    base_amount = SETTLEMENT_OFFER_BASE_GOLD_AMOUNT + duration_bonus

    if player_war_score >= SETTLEMENT_OFFER_DECISIVE_WAR_SCORE:
        payer, payee = proposer_nation, player
    elif player_war_score <= -SETTLEMENT_OFFER_DECISIVE_WAR_SCORE:
        payer, payee = player, proposer_nation
    else:
        # An even war settles as a clean white peace (no indemnity clause).
        return [{"type": "peace"}]

    if world is not None:
        payer_treasury = int(getattr(world, "nation_gold", {}).get(payer, 0))
        scaled = (base_amount
                  + abs(int(player_war_score)) * SETTLEMENT_OFFER_PER_WAR_SCORE
                  + int(payer_treasury * SETTLEMENT_OFFER_TREASURY_FRACTION))
        cap = int(payer_treasury * SETTLEMENT_OFFER_MAX_TREASURY_FRACTION)
        amount = max(0, min(scaled, cap))
    else:
        amount = min(SETTLEMENT_OFFER_MAX_GOLD_AMOUNT, base_amount)

    terms: List[Dict] = [{"type": "peace"}]
    # A payer with an empty (or negative) chest cannot be squeezed, so the
    # INDEMNITY is dropped — but control must fall through to the carve gate
    # below rather than returning. Returning here coupled a TERRITORIAL
    # clause to the payer's coin balance: the most decisively beaten France,
    # exactly the state §11.4 models with the Duchy of Normandy, was the one
    # state immune to being carved, and was offered gentler terms than a
    # solvent loser.
    if amount > 0:
        terms.append({
            "type": "gold_indemnity",
            "from": payer,
            "to": payee,
            "amount": int(amount),
        })

    # NA-6c §11.6-6 (the Normandy mirror): when the AI is the DECISIVE
    # victor, it may also erect a client state out of the player's soil —
    # the same clause, the same executor, the same UX the player uses to
    # erect the Duchy of Warsaw. GR5 is the whole point of this arm: a
    # carve must be something the player can SUFFER, not only inflict.
    #
    # Gated on the AI winning decisively (payer == player) so a carve never
    # rides an even peace, and on the shared eligibility predicate so the
    # AI can never propose soil it does not hold.
    if world is not None and payer == player:
        carve = _settlement_offer_carve_clause(
            world, player=player, proposer_nation=proposer_nation)
        if carve is not None:
            terms.append(carve)
    return terms


def _settlement_offer_carve_clause(world, *, player: str,
                                   proposer_nation: str) -> Optional[Dict]:
    """The first client state ``proposer_nation`` may erect out of the
    PLAYER's soil, as a ready `create_client` clause — or None.

    Routes through the identical `evaluate_create_client_eligibility` the
    player's own authoring seam uses, so the two directions can never drift
    apart (GR5). Stamps the same denormalized display/pricing fields the
    player's add-verb stamps, so the incoming-offer surfaces render a real
    sentence rather than a bare template id.
    """
    catalogue = getattr(world, "formable_nations", None) or {}
    if not catalogue:
        return None
    from backend.game_logic.settlement_validation import (
        evaluate_create_client_eligibility,
    )
    from backend.game_logic.formations import (
        get_template, get_template_identity, template_provinces,
    )
    war_instance = _find_war_instance_for_pair(world, proposer_nation, player)
    if war_instance is None:
        return None
    for template_id in catalogue:
        eligibility = evaluate_create_client_eligibility(
            world, war_instance=war_instance, template_id=template_id,
            from_court=player, carver=proposer_nation,
        )
        if not eligibility.get("eligible"):
            continue
        template = get_template(world, template_id)
        identity = get_template_identity(template) or {}
        return {
            "type": "create_client",
            "from": player,
            "to": proposer_nation,
            "tag": template_id,
            "provinces": list(template_provinces(template)),
            "client_display_name": str(
                identity.get("display_name") or template_id),
        }
    return None


def _find_war_instance_for_pair(world, nation_a: str, nation_b: str) -> Optional[Dict]:
    """The live war instance placing ``nation_a`` and ``nation_b`` on
    opposite sides, or None."""
    for instance in (getattr(world, "war_instances", {}) or {}).values():
        if not isinstance(instance, dict):
            continue
        attackers = set(instance.get("attackers") or [])
        defenders = set(instance.get("defenders") or [])
        if ((nation_a in attackers and nation_b in defenders)
                or (nation_a in defenders and nation_b in attackers)):
            return instance
    return None


def _settlement_offer_eligible_for_war(
    world,
    war: Dict,
    *,
    player: str,
    current_turn: int,
) -> Optional[str]:
    """Return `None` when the war is eligible to produce an offer this
    turn, otherwise the refusal code (for telemetry / future
    instrumentation).
    """
    if war.get("ended_turn") is not None:
        return "war_archived"
    participants = list(war.get("active_participants") or [])
    if len(participants) < SETTLEMENT_OFFER_MULTI_PARTY_MIN_PARTICIPANTS:
        return "war_not_multi_party"
    if player not in participants:
        return "player_not_participant"
    side_by_nation = war.get("side_by_nation") or {}
    player_side = side_by_nation.get(player)
    if player_side not in ("attackers", "defenders"):
        return "player_side_unknown"
    opposing_side = "defenders" if player_side == "attackers" else "attackers"
    leader = _settlement_offer_opposing_side_leader(war, player_side=player_side)
    if not leader or leader == player:
        return "opposing_leader_unknown"
    if side_by_nation.get(leader) != opposing_side:
        return "opposing_leader_side_mismatch"
    covered_enemies = [
        nation
        for nation, side in side_by_nation.items()
        if side == opposing_side and nation != player
    ]
    if not covered_enemies:
        return "no_covered_enemy"
    created_turn = int(war.get("created_turn") or current_turn)
    if current_turn - created_turn < SETTLEMENT_OFFER_MIN_WAR_DURATION_TURNS:
        return "war_too_young"
    cooldowns = getattr(world, "ai_settlement_cooldowns", None) or {}
    next_allowed = int(cooldowns.get(str(war.get("war_id") or "")) or 0)
    if current_turn < next_allowed:
        return "cooldown_active"
    pending = getattr(world, "pending_settlement_dialogues", None) or []
    if _settlement_offer_already_pending(pending, war_id=str(war.get("war_id") or "")):
        return "offer_already_pending"
    if _settlement_offer_already_promoted(world, war_id=str(war.get("war_id") or "")):
        return "offer_already_promoted"
    return None


def _emit_settlement_offer_for_war(
    world,
    war_id: str,
    war: Dict,
    *,
    player: str,
    current_turn: int,
    pending: List[Dict],
    cooldowns: Dict[str, int],
    requested_by_player: bool = False,
) -> Dict:
    """Author one incoming settlement offer for an already-vetted war.

    Shared by the periodic producer scan and the SC-30 request-terms
    grant path (Building Blocks: a granted request produces its offer
    through the SAME emission, tagged with provenance)."""
    side_by_nation = war.get("side_by_nation") or {}
    player_side = side_by_nation.get(player)
    opposing_side = "defenders" if player_side == "attackers" else "attackers"
    proposer_nation = _settlement_offer_opposing_side_leader(
        war, player_side=player_side,
    )
    covered_enemies = [
        nation
        for nation, side in side_by_nation.items()
        if side == opposing_side and nation != player
    ]
    war_age_turns = current_turn - int(war.get("created_turn") or current_turn)

    # AUD-c: war score from the player's perspective vs the opposing leader
    # decides whether the offer demands or grants an indemnity.
    from backend.game_logic.diplomacy import get_war_score_for
    player_war_score = 0
    if proposer_nation:
        try:
            player_war_score = int(get_war_score_for(world, player, proposer_nation))
        except Exception:
            player_war_score = 0

    terms = _settlement_offer_build_terms(
        player=player,
        proposer_nation=proposer_nation,
        war_age_turns=war_age_turns,
        player_war_score=player_war_score,
        world=world,
    )
    seq = _settlement_offer_next_seq(
        pending, war_id=str(war_id), current_turn=current_turn,
    )
    offer_id = f"settlement_offer:{war_id}:{current_turn}:{seq}"

    offer = {
        "type": "incoming_settlement_offer",
        "dialogue_type": "incoming_settlement_offer",
        "offer_id": offer_id,
        "war_id": str(war_id),
        "proposer_nation": proposer_nation,
        "proposer_side": opposing_side,
        "accepting_side": player_side,
        "accepting_leader": player,
        "covered_enemy_participants": list(covered_enemies),
        "settlement_terms": terms,
        "turn_created": current_turn,
    }
    if requested_by_player:
        offer["requested_by_player"] = True
    pending.append(offer)
    cooldowns[str(war_id)] = current_turn + SETTLEMENT_OFFER_COOLDOWN_TURNS
    return offer


def _resolve_settlement_terms_requests(
    world,
    *,
    player: str,
    current_turn: int,
    pending: List[Dict],
    cooldowns: Dict[str, int],
) -> List[Dict]:
    """SC-30 / Slice G1 — answer open player terms requests.

    Runs BEFORE the periodic producer scan so a granted request cannot be
    swallowed by that scan's cooldown gate (the request has its own
    cooldown; the grant still writes the producer cooldown as usual).
    Every open request resolves OBSERVABLY this phase:

    - GRANT: the answering side is not decisively winning
      (`get_war_score_for(leader, player) < REQUEST_TERMS_REFUSAL_WAR_SCORE`)
      → a real incoming offer via `_emit_settlement_offer_for_war` with
      `requested_by_player` provenance; state -> "granted".
    - REFUSE: the winning court declines with voice (named diplomat /
      chancery — never anonymous) + a notification + a campaign-log
      event; state -> "refused" with `REQUEST_TERMS_COOLDOWN_TURNS`.
    - LAPSE: the war archived / lost its multi-party shape since the ask
      → state -> "refused" with reason "war_changed", a Talleyrand lapse
      notice, and NO cooldown (the war itself moved on).

    Returns the granted offers (already appended to `pending`).
    """
    requests = getattr(world, "settlement_terms_requests", None)
    if not isinstance(requests, dict) or not requests:
        return []
    from backend.game_logic.diplomacy import get_war_score_for
    from backend.game_logic.diplomatic_templates import (
        resolve_named_diplomat,
        resolve_settlement_voice_line,
    )
    from backend.notifications import (
        NotificationPriority,
        SETTLEMENT_TERMS_REQUEST_RESULT,
        create_notification,
    )

    war_instances = getattr(world, "war_instances", None) or {}
    granted: List[Dict] = []
    for war_id in sorted(requests.keys()):
        entry = requests.get(war_id)
        if not isinstance(entry, dict) or entry.get("status") != "requested":
            continue
        war = war_instances.get(war_id)
        structural = (
            _settlement_offer_eligible_for_war(
                world, war, player=player, current_turn=current_turn,
            )
            if isinstance(war, dict)
            else "war_archived"
        )
        war_label = _settlement_request_war_label(war, war_id)
        leader = str(entry.get("answering_leader") or "")
        if structural in (None, "cooldown_active", "war_too_young") and (
            _settlement_offer_already_pending(pending, war_id=str(war_id))
            or _settlement_offer_already_promoted(world, war_id=str(war_id))
        ):
            # An offer surfaced between the ask and the answer (the
            # eligibility function's first-refusal-wins ordering can mask
            # this behind `cooldown_active`) — never double-produce.
            structural = "offer_already_pending"
        if structural in (None, "cooldown_active", "war_too_young"):
            # Structurally answerable. `cooldown_active` is the producer's
            # periodic clock — a direct request bypasses it by design; the
            # request's own cooldown gated the click. `war_too_young` was
            # already gated at click time and only shrinks.
            score = int(get_war_score_for(world, leader, player)) if leader else 0
            if score >= REQUEST_TERMS_REFUSAL_WAR_SCORE:
                entry["status"] = "refused"
                entry["resolved_turn"] = int(current_turn)
                entry["resolve_reason"] = "winning_side_refuses"
                entry["cooldown_until_turn"] = int(
                    current_turn + REQUEST_TERMS_COOLDOWN_TURNS
                )
                # A court that refuses to name terms does not spontaneously
                # offer them the same phase — the refusal quiets the
                # periodic producer for the same window.
                cooldowns[str(war_id)] = int(
                    current_turn + SETTLEMENT_OFFER_COOLDOWN_TURNS
                )
                speaker = resolve_named_diplomat("envoy", leader, world)
                line = resolve_settlement_voice_line(
                    "settlement_request_terms_refused_court",
                    speaker=speaker, court=leader,
                )
                world.notifications.add(create_notification(
                    notification_type=SETTLEMENT_TERMS_REQUEST_RESULT,
                    priority=NotificationPriority.NORMAL,
                    title=f"Terms refused by {leader}",
                    message=line,
                    turn_created=int(current_turn),
                    details={
                        "war_id": str(war_id),
                        "result": "refused",
                        "resolve_reason": "winning_side_refuses",
                    },
                ))
                if hasattr(world, "log_event"):
                    world.log_event({
                        "type": "settlement_terms_request_refused",
                        "nation": player,
                        "war_id": str(war_id),
                        "war_label": war_label,
                        "answering_leader": leader,
                        "turn": int(current_turn),
                    })
                continue
            offer = _emit_settlement_offer_for_war(
                world, str(war_id), war,
                player=player, current_turn=current_turn,
                pending=pending, cooldowns=cooldowns,
                requested_by_player=True,
            )
            entry["status"] = "granted"
            entry["resolved_turn"] = int(current_turn)
            entry["resolve_reason"] = "terms_granted"
            entry["cooldown_until_turn"] = int(
                current_turn + REQUEST_TERMS_COOLDOWN_TURNS
            )
            granted.append(offer)
            if hasattr(world, "log_event"):
                world.log_event({
                    "type": "settlement_terms_request_granted",
                    "nation": player,
                    "war_id": str(war_id),
                    "war_label": war_label,
                    "answering_leader": leader,
                    "turn": int(current_turn),
                })
        elif structural in ("offer_already_pending", "offer_already_promoted"):
            # An offer surfaced between the ask and the answer — the
            # request is trivially satisfied; the player reviews THAT.
            entry["status"] = "granted"
            entry["resolved_turn"] = int(current_turn)
            entry["resolve_reason"] = "offer_already_available"
            entry["cooldown_until_turn"] = int(
                current_turn + REQUEST_TERMS_COOLDOWN_TURNS
            )
        else:
            # The war archived or lost its answerable shape since the ask.
            entry["status"] = "refused"
            entry["resolved_turn"] = int(current_turn)
            entry["resolve_reason"] = "war_changed"
            entry["cooldown_until_turn"] = int(current_turn)
            lapse = resolve_settlement_voice_line(
                "settlement_request_terms_lapsed_talleyrand",
                war_label=war_label,
            )
            world.notifications.add(create_notification(
                notification_type=SETTLEMENT_TERMS_REQUEST_RESULT,
                priority=NotificationPriority.NORMAL,
                title="Request for terms lapsed",
                message=lapse,
                turn_created=int(current_turn),
                details={
                    "war_id": str(war_id),
                    "result": "refused",
                    "resolve_reason": "war_changed",
                },
            ))
    return granted


def _settlement_request_war_label(war, war_id: str) -> str:
    if isinstance(war, dict):
        attackers = list(war.get("attackers") or [])
        defenders = list(war.get("defenders") or [])
        if attackers and defenders:
            return f"{' + '.join(attackers)} vs {' + '.join(defenders)}"
    return str(war_id) or "the war"


def process_settlement_offer_phase(world) -> List[Dict]:
    """Produce AI-originated incoming settlement offers for the player.

    Runs once per turn from the AI diplomatic phase. Returns the list
    of offers appended to `world.pending_settlement_dialogues` this
    tick (may be empty). The handler
    `handle_incoming_settlement_offer_action(...)` in
    `settlement_preview.py` is the package-preserving consumer; the
    UI promotion layer that surfaces these offers in
    `dialogue_manager` lands in commit 2 of the SC-5 reversal.
    SC-30 / Slice G1: open player terms requests are answered FIRST
    (grant / refuse / lapse — see `_resolve_settlement_terms_requests`).
    """
    player = getattr(world, "player_nation", "France")
    current_turn = int(getattr(world, "current_turn", 0))
    war_instances = getattr(world, "war_instances", None) or {}

    # Defensive: ensure the storage attributes exist on legacy saves.
    pending = getattr(world, "pending_settlement_dialogues", None)
    if pending is None:
        pending = []
        world.pending_settlement_dialogues = pending
    cooldowns = getattr(world, "ai_settlement_cooldowns", None)
    if cooldowns is None:
        cooldowns = {}
        world.ai_settlement_cooldowns = cooldowns

    produced: List[Dict] = []
    produced.extend(_resolve_settlement_terms_requests(
        world,
        player=player,
        current_turn=current_turn,
        pending=pending,
        cooldowns=cooldowns,
    ))
    if not war_instances:
        return produced

    # Deterministic iteration order so tests can pin offer_id sequence.
    for war_id in sorted(war_instances.keys()):
        war = war_instances[war_id]
        if not isinstance(war, dict):
            continue

        refusal = _settlement_offer_eligible_for_war(
            world, war, player=player, current_turn=current_turn,
        )
        if refusal is not None:
            continue

        produced.append(_emit_settlement_offer_for_war(
            world, str(war_id), war,
            player=player, current_turn=current_turn,
            pending=pending, cooldowns=cooldowns,
        ))

    return produced
