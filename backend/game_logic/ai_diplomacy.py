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

from typing import Dict, List, Optional

from backend.game_logic.diplomacy import (
    calculate_acceptance,
)
from backend.game_logic.diplomatic_dialogue import get_game_bucket


# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════

# Anti-spam cooldown durations (turns)
NATION_REJECTION_COOLDOWN = 3   # After rejection, nation can't propose for N turns
TYPE_REJECTION_COOLDOWN = 5     # After rejection of type X, same type can't be proposed for N turns
QUEUE_MAX_SIZE = 3              # Maximum queued proposals
QUEUE_EXPIRY_TURNS = 3          # Queued proposals expire after N turns

# Per-nation desire table for counter-offers (§9b)
# Ordered by preference (most desired first).
#
# DESIGN NOTE: Despite the name, this table describes what each nation is
# willing to OFFER as additional sweeteners to France in a counter-offer
# scenario. When France counter-offers, _try_add_desired_clauses picks from
# this table and adds items as sweeteners (proposer → target = AI → France),
# which increases France's acceptance score toward the ≥50 threshold.
# This is intentional — the M3 algorithm optimizes for France's acceptance.
NATION_DESIRES = {
    "Prussia": [
        {"type": "territory", "value": 1, "clause": "territory_saxony",
         "description": "Territory (Saxony)"},
        {"type": "territory", "value": 1,
         "description": "Territory (any)"},
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
        {"type": "territory", "value": 1,
         "description": "Territory"},
    ],
    "Saxony": [
        {"type": "protection", "value": 1, "clause": "protection_promised",
         "description": "Protection guarantee"},
        {"type": "gold_per_turn", "value": 50,
         "description": "Gold per turn"},
    ],
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
    """Safely get diplomatic_queue from world."""
    return getattr(world, 'diplomatic_queue', [])


def _set_queue(world, queue: List[Dict]) -> None:
    """Safely set diplomatic_queue on world."""
    world.diplomatic_queue = queue


def _is_on_cooldown(nation: str, proposal_type: str, world) -> bool:
    """Check if a nation or proposal type is on cooldown."""
    cooldowns = _get_cooldowns(world)
    nation_key = f"{nation}|nation"
    type_key = f"{nation}|{proposal_type}"

    if cooldowns.get(nation_key, 0) > 0:
        return True
    if cooldowns.get(type_key, 0) > 0:
        return True
    return False


def apply_rejection_cooldowns(nation: str, proposal_type: str, world) -> None:
    """Apply cooldowns after a proposal is rejected.

    Called from executor when player rejects an AI proposal.
    """
    cooldowns = _get_cooldowns(world)
    nation_key = f"{nation}|nation"
    type_key = f"{nation}|{proposal_type}"
    cooldowns[nation_key] = int(NATION_REJECTION_COOLDOWN)
    cooldowns[type_key] = int(TYPE_REJECTION_COOLDOWN)
    _set_cooldowns(world, cooldowns)


def _expire_queue(world) -> None:
    """Remove expired items from the diplomatic queue."""
    queue = _get_queue(world)
    current_turn = int(world.current_turn)
    queue = [
        item for item in queue
        if current_turn - item.get("turn_generated", 0) < QUEUE_EXPIRY_TURNS
    ]
    _set_queue(world, queue)


def _enqueue_proposal(proposal: Dict, world) -> bool:
    """Add a proposal to the diplomatic queue. Returns True if added.

    Drops lowest-priority item if queue is full.
    """
    queue = _get_queue(world)

    if len(queue) >= QUEUE_MAX_SIZE:
        # Find highest priority number (lowest urgency) in queue + new proposal
        all_items = queue + [proposal]
        all_items.sort(key=lambda x: x.get("priority", 99))
        # Drop the last (highest priority number = least urgent)
        queue = all_items[:QUEUE_MAX_SIZE]
    else:
        queue.append(proposal)

    _set_queue(world, queue)
    return True


def _dequeue_best(world) -> Optional[Dict]:
    """Pop the highest-priority (lowest number) item from the queue."""
    queue = _get_queue(world)
    if not queue:
        return None

    queue.sort(key=lambda x: x.get("priority", 99))
    best = queue.pop(0)
    _set_queue(world, queue)
    return best


# ═══════════════════════════════════════════════════════════════
# WAR SCORE FROM AI PERSPECTIVE
# ═══════════════════════════════════════════════════════════════

def _get_war_score_for_nation(nation: str, opponent: str, world) -> int:
    """Get war score from a specific nation's perspective.

    Positive = nation is winning, negative = nation is losing.
    The stored war_score is from alphabetically-first nation's perspective.
    """
    diplo_key = world._make_diplo_key(nation, opponent)
    raw_score = getattr(world, 'war_scores', {}).get(diplo_key, 0)

    # If nation is alphabetically second, flip the sign
    parts = diplo_key.split("|")
    if len(parts) == 2 and parts[0] != nation:
        raw_score = -raw_score

    return int(raw_score)


# ═══════════════════════════════════════════════════════════════
# STALEMATE TRACKING
# ═══════════════════════════════════════════════════════════════

def _get_stalemate_turns(nation: str, world) -> int:
    """Get consecutive stalemate turns for a nation's war with France."""
    counters = getattr(world, 'ai_stalemate_counters', {})
    return counters.get(nation, 0)


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
) -> Dict:
    """Build proposal terms dict from AI nation's perspective.

    The AI proposes TO France. So:
    - proposer_nation = AI nation
    - target_nation = France (player)
    - sweeteners = things AI offers to France to sweeten the deal
    - demands = things AI wants from France
    """
    player = getattr(world, 'player_nation', 'France')

    terms = {
        "type": proposal_type,
        "proposer_nation": nation,
        "target_nation": player,
        "sweeteners": [],
        "demands": [],
        "clauses": [],
    }

    if proposal_type in ("armistice_losing", "armistice"):
        # AI is losing: offer gold to stop the bleeding
        nation_gold = world.nation_gold.get(nation, 0)
        if nation_gold > 200:
            offer_amount = min(300, int(nation_gold * 0.15))
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
            offer_amount = min(200, int(nation_gold * 0.10))
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
            terms["type"] = "alliance"  # Uses alliance base disposition
            terms["clauses"].append("open_borders")
        elif proposal_type == "alliance":
            terms["type"] = "alliance"
            terms["clauses"].append("open_borders")

        # Saxony always offers protection clause
        if nation == "Saxony":
            terms["clauses"].append("protection_promised")

    elif proposal_type == "opportunistic":
        # Favorable terms for the AI: demand concessions
        terms["type"] = "non_aggression"  # Map to acceptance type
        terms["demands"].append({"type": "gold_per_turn", "value": int(100)})

    return terms


def _determine_upgrade_type(nation: str, world) -> Optional[str]:
    """Determine what upgrade the AI should propose based on current state.

    Returns the next valid upgrade type or None if already at max.
    """
    player = getattr(world, 'player_nation', 'France')
    current_state = world.get_diplomatic_state(player, nation)

    # Map current state to next upgrade in the path
    upgrade_map = {
        "PEACE": "open_borders",
        "OPEN_BORDERS": "non_aggression",
        "NON_AGGRESSION": "defensive_alliance",
        "DEFENSIVE_ALLIANCE": "alliance",
    }

    return upgrade_map.get(current_state)


# ═══════════════════════════════════════════════════════════════
# P7: OPPORTUNISM CHECK
# ═══════════════════════════════════════════════════════════════

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

    # ── Expire old queue items ──
    _expire_queue(world)

    # ── Check blocking dialogue ──
    pending = getattr(world, 'pending_diplomatic_dialogue', None)
    has_blocking_dialogue = (
        pending is not None and pending.get("blocking", False)
    )

    # ── Get diplomatic context ──
    diplo_state = world.get_diplomatic_state(player, nation)
    is_at_war = diplo_state == "WAR"
    diplo_key = world._make_diplo_key(player, nation)
    relation = world.nation_relations.get(diplo_key, 0)
    war_score = _get_war_score_for_nation(nation, player, world) if is_at_war else 0

    # Update stalemate counter
    if is_at_war:
        stalemate_turns = _update_stalemate_counter(nation, war_score, world)
    else:
        stalemate_turns = 0

    proposal = None

    # ── P1: Losing badly (war_score < -40) ──
    if is_at_war and war_score < -40:
        # Decide: armistice if war_score > -70, peace if truly desperate
        if war_score < -70:
            ptype = "peace"
        else:
            ptype = "armistice_losing"

        if not _is_on_cooldown(nation, ptype, world):
            terms = _build_proposal_terms(nation, ptype, war_score, world)
            proposal = _make_proposal(nation, ptype, 1, terms, world)

    # ── P2: Stalemate (war_score -10..+10 for 5+ turns) ──
    if proposal is None and is_at_war and stalemate_turns >= 5:
        ptype = "armistice_stalemate"
        if not _is_on_cooldown(nation, "armistice", world):
            terms = _build_proposal_terms(nation, ptype, war_score, world)
            proposal = _make_proposal(nation, "armistice", 2, terms, world)

    # ── P3: Threat > 60 AND not allied [DEFERRED] ──
    # Returns None — wired when threat system is implemented (Session 7)

    # ── P4: Relation > +30 AND at peace → propose upgrade ──
    if proposal is None and not is_at_war and relation > 30:
        upgrade_type = _determine_upgrade_type(nation, world)
        if upgrade_type and not _is_on_cooldown(nation, upgrade_type, world):
            terms = _build_proposal_terms(nation, upgrade_type, 0, world)
            proposal = _make_proposal(nation, upgrade_type, 4, terms, world)

    # ── P5: Gold < 200 and declining [DEFERRED] ──
    # Returns None — no gold_history tracking yet

    # ── P6: Vassal courting [DEFERRED to Session 5] ──

    # ── P7: Opportunism — France at war with 2+ AND this nation at peace ──
    if proposal is None and not is_at_war:
        wars_against_france = _count_nations_at_war_with_france(world)
        if wars_against_france >= 2:
            ptype = "opportunistic"
            if not _is_on_cooldown(nation, ptype, world):
                terms = _build_proposal_terms(nation, ptype, 0, world)
                proposal = _make_proposal(nation, ptype, 7, terms, world)

    if proposal is None:
        return None

    # ── Verify proposal is reasonable via calculate_acceptance ──
    acceptance = calculate_acceptance(proposal["terms"], world)
    score = acceptance["score"]

    # AI won't propose something that would be auto-rejected (score < 20)
    # Score < 20 means even the AI knows it's unreasonable
    if score < 20:
        return None

    # ── Delivery or queue ──
    if has_blocking_dialogue:
        _enqueue_proposal(proposal, world)
        return None  # Queued, not delivered this turn

    return proposal


def _make_proposal(
    nation: str,
    proposal_type: str,
    priority: int,
    terms: Dict,
    world,
) -> Dict:
    """Construct the standard proposal dict."""
    # Get game bucket from France's perspective (for Talleyrand's assessment)
    game_bucket = get_game_bucket(nation, world)
    assessment = _get_talleyrand_assessment(proposal_type, game_bucket)

    return {
        "source": nation,
        "proposal_type": proposal_type,
        "priority": int(priority),
        "terms": terms,
        "talleyrand_assessment": assessment,
        "turn_generated": int(world.current_turn),
    }


# ═══════════════════════════════════════════════════════════════
# DELIVERY: deliver_ai_proposal
# ═══════════════════════════════════════════════════════════════

def deliver_ai_proposal(proposal: Dict, world) -> Dict:
    """Take a proposal dict and set up world.pending_diplomatic_dialogue.

    Creates an incoming_proposal dialogue with Accept/Reject/Counter options.
    Sets blocking=True so no other proposals overwrite it.

    Returns the dialogue dict (also stored on world).
    """
    nation = proposal["source"]
    terms = proposal["terms"]
    assessment = proposal.get("talleyrand_assessment", "")

    # Get diplomat name for flavor text
    diplomats = getattr(world, 'diplomats', {})
    diplomat = diplomats.get(nation)
    diplomat_name = diplomat.name if diplomat else f"the {nation} ambassador"

    # Build human-readable proposal summary
    proposal_summary = _format_proposal_summary(terms)

    # Run acceptance calculation to provide context score
    acceptance = calculate_acceptance(terms, world)
    score = acceptance["score"]

    # Build dialogue
    dialogue = {
        "type": "incoming_proposal",
        "target_nation": nation,
        "talleyrand_text": (
            f"Sire, {diplomat_name} has arrived with a proposal from {nation}:"
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
            "acceptance_score": int(score),
        },
        "turn_created": int(world.current_turn),
        "blocking": True,
    }

    world.pending_diplomatic_dialogue = dialogue

    # Dispatch event (Session 8D)
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "diplomatic_ai_proposal",
                        {"nation": nation}, "always")

    # Notification: AI proposal arrived (Session 8C)
    from backend.notifications import (
        create_notification, NotificationPriority, DIPLOMATIC_PROPOSAL,
    )
    world.notifications.add(create_notification(
        DIPLOMATIC_PROPOSAL,
        NotificationPriority.HIGH,
        f"Envoy from {nation}",
        f"An envoy from {nation} has arrived with a proposal.",
        int(world.current_turn),
    ))

    # Set incoming_proposal_popup for Godot (Session 8C)
    diplomat_personality = getattr(diplomat, 'personality', 'unknown') if diplomat else "unknown"
    # Build human-readable clause list
    clauses = []
    for d in terms.get("demands", []):
        clauses.append(f"Demand: {d.get('type', 'unknown')} — {d.get('value', '')}")
    for s in terms.get("sweeteners", []):
        clauses.append(f"Offer: {s.get('type', 'unknown')} — {s.get('value', '')}")

    # Find largest positive/negative factor
    factors = acceptance.get("factors", [])
    positive_factors = [f for f in factors if f.get("value", 0) > 0]
    negative_factors = [f for f in factors if f.get("value", 0) < 0]
    acceptance_hint = positive_factors[0].get("reason", "No strong positives") if positive_factors else "No strong positives identified"
    rejection_hint = negative_factors[0].get("reason", "No major obstacles") if negative_factors else "No major obstacles identified"

    world.incoming_proposal_popup = {
        "from_nation": nation,
        "diplomat_name": diplomat_name,
        "diplomat_personality": diplomat_personality,
        "proposal_type": terms.get("type", "unknown"),
        "clauses": clauses,
        "talleyrand_assessment": assessment or "Talleyrand has no assessment.",
        "acceptance_hint": acceptance_hint,
        "rejection_hint": rejection_hint,
    }

    return dialogue


def _format_proposal_summary(terms: Dict) -> str:
    """Create a human-readable summary of proposal terms."""
    parts = []
    proposal_type = terms.get("type", "unknown")
    proposer = terms.get("proposer_nation", "Unknown")
    target = terms.get("target_nation", "France")

    # Type description
    type_names = {
        "armistice_losing": "Armistice",
        "armistice_winning": "Armistice",
        "peace": "Peace Treaty",
        "alliance": "Full Alliance",
        "non_aggression": "Non-Aggression Pact",
        "open_borders": "Open Borders Agreement",
        "defensive_alliance": "Defensive Alliance",
        "vassalage": "Vassalage",
    }
    parts.append(f"{type_names.get(proposal_type, proposal_type.title())} "
                 f"between {proposer} and {target}")

    # Sweeteners (what AI offers)
    for s in terms.get("sweeteners", []):
        stype = s.get("type", "")
        svalue = s.get("value", 0)
        if stype == "gold_per_turn":
            parts.append(f"  - {proposer} offers {int(svalue)} gold per turn")
        elif stype == "gold_lump":
            parts.append(f"  - {proposer} offers {int(svalue)} gold")
        elif stype == "territory":
            parts.append(f"  - {proposer} cedes territory")
        elif stype == "protection":
            parts.append(f"  - {proposer} offers protection guarantee")
        elif stype == "open_borders":
            parts.append(f"  - {proposer} grants open borders")

    # Demands (what AI wants)
    for d in terms.get("demands", []):
        dtype = d.get("type", "")
        dvalue = d.get("value", 0)
        if dtype == "gold_per_turn":
            parts.append(f"  - {proposer} demands {int(dvalue)} gold per turn")
        elif dtype == "gold_lump":
            parts.append(f"  - {proposer} demands {int(dvalue)} gold")
        elif dtype == "territory":
            parts.append(f"  - {proposer} demands territory")

    # Clauses
    clause_names = {
        "open_borders": "Open borders",
        "protection_promised": "Protection guarantee",
        "territory_saxony": "Saxony territory transfer",
        "continental_system_lifted": "Continental System lifted",
    }
    for c in terms.get("clauses", []):
        name = clause_names.get(c, c.replace("_", " ").title())
        parts.append(f"  - {name}")

    return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════
# DEQUEUE: try_deliver_queued_proposal
# ═══════════════════════════════════════════════════════════════

def try_deliver_queued_proposal(world) -> Optional[Dict]:
    """Try to deliver a queued proposal if no blocking dialogue exists.

    Called from turn_manager AFTER process_diplomatic_phase for all nations.
    Returns the delivered dialogue dict, or None.
    """
    pending = getattr(world, 'pending_diplomatic_dialogue', None)
    if pending is not None and pending.get("blocking", False):
        return None

    _expire_queue(world)
    proposal = _dequeue_best(world)
    if proposal is None:
        return None

    return deliver_ai_proposal(proposal, world)


# ═══════════════════════════════════════════════════════════════
# M3 COUNTER-OFFER ALGORITHM (§9b)
# ═══════════════════════════════════════════════════════════════

def generate_counter_offer(proposal: Dict, world) -> Optional[Dict]:
    """Generate a deterministic counter-offer for an AI proposal.

    Algorithm (§9b):
        Step 1: Calculate per-clause acceptance impact using SWEETENER/DEMAND values.
        Step 2: Identify the single clause with the largest NEGATIVE impact on
                 AI acceptance (i.e., the thing the AI hates most about France's
                 modification).
        Step 3: Remove that clause.
        Step 4: Recalculate. If still 30-49, add cheapest desired clause from
                 per-nation desire table.
        Step 5: If score >= 50: present as counter. If < 30: REJECT.

    Args:
        proposal: The original AI proposal terms dict. This is the "terms" field
                  from the AI proposal, which the player is now counter-offering
                  (we modify it to be more favorable to France).
        world: WorldState

    Returns:
        Modified terms dict if counter succeeds (score >= 50), or
        None if counter fails (score < 30 after adjustments).
    """
    import copy
    terms = copy.deepcopy(proposal)
    source_nation = terms.get("proposer_nation", "")

    # ── Step 1: Calculate per-clause impact ──
    # We test removing each sweetener/demand/clause individually to see
    # what impact it has on the acceptance score
    baseline = calculate_acceptance(terms, world)
    baseline_score = baseline["score"]

    # If already acceptable, no need to counter
    if baseline_score >= 50:
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

    # ── Step 2: Find clause with largest NEGATIVE impact on acceptance ──
    # (The clause that, when present, hurts acceptance the most =
    #  removing it would INCREASE acceptance the most =
    #  highest positive impact value)
    if not clause_impacts:
        # Nothing to remove — try adding desired clauses directly
        return _try_add_desired_clauses(terms, source_nation, world)

    # Sort by impact descending (removing the one with highest positive impact
    # improves the score the most — that's the one the AI hates most)
    clause_impacts.sort(key=lambda x: x["impact"], reverse=True)
    worst_clause = clause_impacts[0]

    # Only remove if it actually improves the score
    if worst_clause["impact"] <= 0:
        # No single removal helps — try adding desired clauses
        return _try_add_desired_clauses(terms, source_nation, world)

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

    if new_score >= 50:
        return terms

    if 30 <= new_score < 50:
        # Try adding cheapest desired clause from nation's desire table
        improved = _try_add_desired_clauses(terms, source_nation, world)
        if improved is not None:
            return improved

    # ── Step 5: If < 30, REJECT ──
    if new_score < 30:
        return None

    # Between 30-49 but couldn't add desired clauses: still return as counter
    return terms


def _try_add_desired_clauses(
    terms: Dict, source_nation: str, world
) -> Optional[Dict]:
    """Try adding the cheapest desired clause from the nation's desire table.

    The AI nation adds additional sweeteners it offers TO France to bridge
    the acceptance gap toward ≥50. See NATION_DESIRES design note above.

    Returns modified terms if score reaches >= 50, otherwise None.
    """
    import copy

    desires = NATION_DESIRES.get(source_nation, [])
    if not desires:
        return None

    # Try each desire in order (cheapest/most preferred first)
    for desire in desires:
        test_terms = copy.deepcopy(terms)
        dtype = desire.get("type", "")

        # Add as a sweetener from the AI nation to France
        if dtype in ("gold_lump", "gold_per_turn", "territory"):
            test_terms["sweeteners"].append({
                "type": dtype,
                "value": int(desire.get("value", 0)),
            })
        elif dtype in ("open_borders", "protection"):
            clause_key = desire.get("clause", dtype)
            if clause_key not in test_terms.get("clauses", []):
                test_terms["clauses"].append(clause_key)
            else:
                continue  # Already present, skip

        result = calculate_acceptance(test_terms, world)
        if result["score"] >= 50:
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

        # Check if 'nation' has an alliance with 'other_nation'
        state_with_other = world.get_diplomatic_state(nation, other_nation)
        if state_with_other not in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
            continue

        # Check if France is at WAR with that allied nation
        if world.is_at_war(player, other_nation):
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

_AI_AI_MAX_TREATIES_PER_TURN = 2


def process_ai_ai_diplomatic_phase(world) -> List[Dict]:
    """Process diplomatic proposals between AI nations (excluding France).

    Called from advance_turn() after the existing AI proposal phase.
    Anti-spam: max 2 AI-AI treaties per turn total.

    Returns list of treaty event dicts (for campaign log wiring).
    """
    player = getattr(world, 'player_nation', 'France')
    enemy_nations = list(getattr(world, 'enemy_nations', []))
    treaties_this_turn = 0
    events = []

    for i, initiator in enumerate(enemy_nations):
        if treaties_this_turn >= _AI_AI_MAX_TREATIES_PER_TURN:
            break

        for target in enemy_nations[i + 1:]:
            if treaties_this_turn >= _AI_AI_MAX_TREATIES_PER_TURN:
                break

            proposal = _evaluate_ai_ai_proposal(initiator, target, world)
            if not proposal:
                continue

            # Check acceptance from both sides
            acceptance_a = _ai_ai_acceptance(proposal, initiator, target, world)
            acceptance_b = _ai_ai_acceptance(proposal, target, initiator, world)

            if acceptance_a >= 50 and acceptance_b >= 50:
                # Ratify immediately (no transit delay for AI-AI)
                event = _ratify_ai_ai_treaty(initiator, target, proposal, world)
                if event:
                    events.append(event)
                    treaties_this_turn += 1

    return events


def _evaluate_ai_ai_proposal(nation_a: str, nation_b: str, world) -> Optional[Dict]:
    """Evaluate if two AI nations should propose to each other.

    Trigger conditions (per the spec):
    1. Both at WAR with France AND relation > -20 → DEFENSIVE_ALLIANCE
    2. One losing badly (war_score < -40) AND other at peace → NON_AGGRESSION
    3. Both at PEACE with France AND relation > +40 → upgrade treaty one step
    4. One gold < 200 AND other gold > 400 → trade deal (open_borders)
    """
    player = getattr(world, 'player_nation', 'France')

    state_a_france = world.get_diplomatic_state(nation_a, player)
    state_b_france = world.get_diplomatic_state(nation_b, player)
    state_ab = world.get_diplomatic_state(nation_a, nation_b)

    diplo_key_ab = world._make_diplo_key(nation_a, nation_b)
    relation_ab = world.nation_relations.get(diplo_key_ab, 0)

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

    return None


def _ai_ai_acceptance(proposal: Dict, evaluator: str, other: str, world) -> int:
    """Simplified acceptance check for AI-AI proposals.

    Uses the same calculate_acceptance formula but with AI nations.
    """
    # Build a proposal dict compatible with calculate_acceptance
    acceptance_proposal = {
        "type": proposal["type"],
        "proposer_nation": proposal.get("proposer", other),
        "target_nation": evaluator,
        "sweeteners": [],
        "demands": [],
        "clauses": [],
    }
    result = calculate_acceptance(acceptance_proposal, world)
    return result["score"]


def _ratify_ai_ai_treaty(nation_a: str, nation_b: str, proposal: Dict, world) -> Optional[Dict]:
    """Ratify an AI-AI treaty. No transit delay — immediate.

    Applies state transition and queues dispatch/campaign log events.
    """
    from backend.game_logic.diplomacy import _UPGRADE_ORDER

    proposal_type = proposal["type"]
    diplo_key = world._make_diplo_key(nation_a, nation_b)
    current_state = world.get_diplomatic_state(nation_a, nation_b)

    # Map proposal type to target state
    state_map = {
        "defensive_alliance": "DEFENSIVE_ALLIANCE",
        "alliance": "ALLIANCE",
        "non_aggression": "NON_AGGRESSION",
        "open_borders": "OPEN_BORDERS",
        "peace": "PEACE",
    }
    target_state = state_map.get(proposal_type)
    if not target_state:
        return None

    # Don't downgrade
    if target_state in _UPGRADE_ORDER and current_state in _UPGRADE_ORDER:
        if _UPGRADE_ORDER.index(target_state) <= _UPGRADE_ORDER.index(current_state):
            return None

    # Apply transition
    world.diplomatic_states[diplo_key] = target_state

    # Improve relations
    world.modify_nation_relation(nation_a, nation_b, 10)

    treaty_type_display = proposal_type.replace("_", " ").title()

    # Queue dispatch event (fog-filtered)
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "diplomatic_ai_ai_treaty",
                        {"nation_a": nation_a, "nation_b": nation_b,
                         "treaty_type": treaty_type_display},
                        "partial_on_nation")

    # Campaign log event
    world.log_event({
        "type": "diplomatic_ai_ai_treaty",
        "nation_a": nation_a,
        "nation_b": nation_b,
        "treaty_type": treaty_type_display,
        "turn": int(world.current_turn),
    })

    return {
        "type": "ai_ai_treaty",
        "nation_a": nation_a,
        "nation_b": nation_b,
        "treaty_type": treaty_type_display,
        "message": f"{nation_a} and {nation_b} have signed a {treaty_type_display}.",
    }
