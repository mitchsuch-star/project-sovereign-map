"""
Diplomatic Advisory System — Phase 8 Session 4

Handles Talleyrand's strategic advisory conversations: threat assessment,
nation analysis, action recommendations, and diplomatic overview.

All functions are pure/deterministic — no LLM calls. Works identically
in mock mode. Advisory dialogues cost 0 DP and are non-blocking.

Entry points:
  - detect_advisory_type() → keyword match to advisory subtype
  - generate_advisory() → builds pending_diplomatic_dialogue dict (type="advisory")
"""

from typing import Dict, List, Optional

from backend.game_logic.diplomacy import get_war_score_for
from backend.game_logic.diplomatic_dialogue import (
    get_known_nations,
)

# ═══════ ADVISORY KEYWORD MAP ═══════
# Longest-first matching prevents "what" from shadowing "what about"

ADVISORY_KEYWORDS = {
    "what about": "assess_nation",
    "what should": "recommend_action",
    "who is": "compare_threats",
    "should i": "recommend_action",
    "what happens if": "predict_outcome",
    "what if": "predict_outcome",
    "bigger threat": "compare_threats",
    "focus on": "recommend_priority",
    "can we": "feasibility",
    "how do we": "recommend_action",
}

# Sorted by key length descending so longer phrases match first
_SORTED_KEYWORDS = sorted(ADVISORY_KEYWORDS.items(), key=lambda kv: -len(kv[0]))

# Diplomat personality descriptors (for Talleyrand's commentary)
_DIPLOMAT_DESCRIPTORS = {
    "hawk": "bellicose",
    "schemer": "calculating",
    "dove": "conciliatory",
    "loyalist": "steadfast",
}

# State display names for Talleyrand's voice
_STATE_DISPLAY = {
    "WAR": "at war",
    "ARMISTICE": "under armistice",
    "PEACE": "at peace",
    "OPEN_BORDERS": "sharing open borders",
    "NON_AGGRESSION": "bound by non-aggression",
    "DEFENSIVE_ALLIANCE": "in defensive alliance",
    "ALLIANCE": "allied",
    "VASSAL": "our vassal",
}


# ═══════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════

def detect_advisory_type(text: str) -> Optional[str]:
    """Detect advisory subtype from player text via keyword matching.

    Returns one of: assess_nation, recommend_action, compare_threats,
    predict_outcome, recommend_priority, feasibility — or None if no match.
    """
    text_lower = text.lower().strip()
    for keyword, subtype in _SORTED_KEYWORDS:
        if keyword in text_lower:
            # "can we" / feasibility is handled by the feasibility system, not here
            if subtype == "feasibility":
                return None
            return subtype
    return None


def generate_advisory(
    target_nation: Optional[str],
    advisory_type: str,
    world,
) -> Dict:
    """Build an advisory dialogue dict for pending_diplomatic_dialogue.

    Args:
        target_nation: Specific nation being asked about, or None for overview.
        advisory_type: One of the subtypes from detect_advisory_type().
        world: WorldState instance.

    Returns:
        Dict suitable for world.pending_diplomatic_dialogue (type="advisory").
    """
    if advisory_type == "compare_threats":
        return _compare_threats(world)
    elif advisory_type == "assess_nation" and target_nation:
        return _assess_nation(target_nation, world)
    elif advisory_type == "recommend_action":
        if target_nation:
            return _recommend_action(target_nation, world)
        return _recommend_action_overview(world)
    elif advisory_type == "recommend_priority":
        return _compare_threats(world)
    elif advisory_type == "predict_outcome" and target_nation:
        return _assess_nation(target_nation, world)
    else:
        # Fallback: general overview
        return _diplomatic_overview(world)


# ═══════════════════════════════════════════════════════
# NATION ASSESSMENT
# ═══════════════════════════════════════════════════════

def _assess_nation(nation: str, world) -> Dict:
    """Assess a specific nation — relations, military, diplomatic posture."""
    diplo_key = world._make_diplo_key("France", nation)
    state = world.get_diplomatic_state("France", nation)
    relation = int(world.nation_relations.get(diplo_key, 0))
    advantage = _get_military_advantage(nation, world)
    diplomat = world.diplomats.get(nation)
    diplomat_desc = ""
    if diplomat:
        personality_word = _DIPLOMAT_DESCRIPTORS.get(diplomat.personality, "unknown")
        diplomat_desc = (
            f"{diplomat.name} is {personality_word} — "
            f"skill {int(diplomat.skill)}, trust {int(diplomat.trust)}. "
        )

    france_war_score = get_war_score_for(world, "France", nation)

    state_text = _STATE_DISPLAY.get(state, state.lower())
    summary = _get_nation_summary(nation, world)

    # R130: Confidence based on fog of war visibility of target nation's regions
    target_regions = [r for r in world.regions.values() if getattr(r, 'controller', '') == nation]
    if target_regions:
        visible_count = sum(
            1 for r in target_regions
            if world.get_region_intel(r.name).visibility in ("full", "partial")
        )
        total_count = len(target_regions)
        visibility_ratio = visible_count / total_count
        if visibility_ratio >= 0.7:
            confidence = "high"
        elif visibility_ratio >= 0.3:
            confidence = "medium"
        else:
            confidence = "low"
    else:
        confidence = "medium"

    CONFIDENCE_PREAMBLES = {
        "high": "I am confident in this assessment, Sire. My sources are reliable. ",
        "medium": "Our intelligence is adequate, though gaps remain. ",
        "low": "I must warn you — my information is incomplete. Proceed with caution. ",
    }
    confidence_preamble = CONFIDENCE_PREAMBLES.get(confidence, "")

    if state == "WAR":
        situation = (
            f"{confidence_preamble}"
            f"We are {state_text} with {nation}, Sire. "
            f"War score stands at {int(france_war_score)} from our perspective. "
            f"Their military strength is {advantage} relative to ours. "
            f"{diplomat_desc}"
            f"{summary}"
        )
        if france_war_score > 20:
            recommendation = "We hold the advantage. Press for favorable terms or continue fighting."
            hints = [f"Propose peace with {nation}", "Continue military pressure"]
        elif france_war_score < -20:
            recommendation = "The war goes poorly. Consider armistice before it worsens."
            hints = [f"Propose armistice with {nation}", "Reinforce the front"]
        else:
            recommendation = "The war is balanced. A decisive battle could tip the scales either way."
            hints = ["Seek a decisive engagement", "Propose peace on equal terms"]
    else:
        situation = (
            f"{confidence_preamble}"
            f"We are {state_text} with {nation}, Sire. "
            f"Relations stand at {relation}. "
            f"Their military strength is {advantage} relative to ours. "
            f"{diplomat_desc}"
            f"{summary}"
        )
        if relation > 30:
            recommendation = f"{nation} is well-disposed toward us. An alliance is within reach."
            hints = [f"Propose alliance with {nation}", "Strengthen relations further"]
        elif relation > 0:
            recommendation = f"{nation} is cautiously favorable. Patience will yield dividends."
            hints = [f"Improve relations with {nation}", "Propose non-aggression pact"]
        elif relation > -30:
            recommendation = f"{nation} is wary but not hostile. Courtship could sway them."
            hints = [f"Court {nation}", f"Improve relations with {nation}"]
        else:
            recommendation = f"{nation} harbors deep resentment. Diplomatic progress will be slow and costly."
            hints = [f"Improve relations with {nation}", "Consider whether confrontation is inevitable"]

    # Build options
    options = []
    if state == "WAR":
        options.append({
            "label": "What terms would they accept?",
            "description": f"Assess feasibility of peace with {nation}.",
            "action": "expand_to_proposal",
        })
    else:
        options.append({
            "label": f"What should we do about {nation}?",
            "description": f"Get a recommendation for our next move with {nation}.",
            "action": "expand_to_proposal",
        })
    options.append({
        "label": "Thank you",
        "description": "Dismiss.",
        "action": "dismiss",
    })

    return {
        "type": "advisory",
        "target_nation": nation,
        "talleyrand_text": situation,
        "options": options,
        "context": {
            "situation_summary": summary,
            "recommendation": recommendation,
            "confidence_level": confidence,
            "action_hints": hints,
            "war_score": int(france_war_score) if state == "WAR" else 0,
            "relation": int(relation),
            "diplomatic_state": state,
            "military_advantage": advantage,
        },
        "turn_created": int(world.current_turn),
        "blocking": False,
    }


# ═══════════════════════════════════════════════════════
# THREAT COMPARISON
# ═══════════════════════════════════════════════════════

def _compare_threats(world) -> Dict:
    """Compare all nations as threats to France. Deterministic ranking."""
    threat_entries: List[Dict] = []
    france_strength = _get_fogged_strength("France", world)
    for nation in sorted(get_known_nations(world)):
        diplo_key = world._make_diplo_key("France", nation)
        state = world.get_diplomatic_state("France", nation)
        relation = int(world.nation_relations.get(diplo_key, 0))
        strength = _get_fogged_strength(nation, world)

        # Threat score: higher = more threatening
        # Hostile relations, large army, at war all increase threat
        threat_score = 0
        threat_score -= relation  # negative relation = more threatening
        if state == "WAR":
            threat_score += 40
        elif state == "ARMISTICE":
            threat_score += 15
        if strength > france_strength * 0.5:
            threat_score += 20
        elif strength > france_strength:
            threat_score += 20

        threat_entries.append({
            "nation": nation,
            "state": state,
            "relation": relation,
            "strength": strength,
            "threat_score": threat_score,
        })

    # Sort by threat score descending
    threat_entries.sort(key=lambda e: -e["threat_score"])

    if not threat_entries:
        return {
            "type": "advisory",
            "target_nation": "",
            "talleyrand_text": "No foreign nations detected, Sire.",
            "options": [{"label": "Thank you", "description": "Dismiss.", "action": "dismiss"}],
            "context": {
                "situation_summary": "No foreign nations detected.",
                "recommendation": "The situation is stable.",
                "confidence_level": "low",
                "action_hints": [],
                "threat_ranking": [],
            },
            "turn_created": int(world.current_turn),
            "blocking": False,
        }

    top_threat = threat_entries[0]
    second_threat = threat_entries[1] if len(threat_entries) > 1 else None

    # Build Talleyrand's assessment
    lines = ["An astute question, Sire. Let me assess our position.\n"]
    for entry in threat_entries:
        n = entry["nation"]
        state_text = _STATE_DISPLAY.get(entry["state"], entry["state"].lower())
        adv = _get_military_advantage(n, world)
        lines.append(
            f"  {n} — {state_text.capitalize()}, relations {entry['relation']}. "
            f"Military: {adv}."
        )

    lines.append("")
    lines.append(
        f"My assessment: {top_threat['nation']} is the most pressing concern."
    )
    if second_threat and second_threat["threat_score"] > 20:
        lines.append(
            f"{second_threat['nation']} should not be ignored either."
        )
    lines.append(
        f"Address {top_threat['nation']} first, Sire — "
        f"{'end the war' if top_threat['state'] == 'WAR' else 'prevent hostilities'} "
        f"before it spirals."
    )

    talleyrand_text = "\n".join(lines)

    # Recommendation
    if top_threat["state"] == "WAR":
        recommendation = f"Prioritize the war with {top_threat['nation']}."
        hints = [
            f"Propose peace with {top_threat['nation']}",
            f"Win a decisive battle against {top_threat['nation']}",
        ]
    else:
        recommendation = f"Secure {top_threat['nation']} diplomatically before conflict erupts."
        hints = [
            f"Court {top_threat['nation']}",
            f"Propose non-aggression with {top_threat['nation']}",
        ]

    confidence = "high" if top_threat["threat_score"] > 50 else "medium"

    # Build options
    options = [
        {
            "label": f"Tell me more about {top_threat['nation']}",
            "description": f"Detailed assessment of {top_threat['nation']}.",
            "action": "expand_to_proposal",
        },
        {
            "label": "Thank you",
            "description": "Dismiss.",
            "action": "dismiss",
        },
    ]

    return {
        "type": "advisory",
        "target_nation": top_threat["nation"],
        "talleyrand_text": talleyrand_text,
        "options": options,
        "context": {
            "situation_summary": f"{top_threat['nation']} is the primary threat.",
            "recommendation": recommendation,
            "confidence_level": confidence,
            "action_hints": hints,
            "threat_ranking": [
                {"nation": e["nation"], "threat_score": int(e["threat_score"])}
                for e in threat_entries
            ],
        },
        "turn_created": int(world.current_turn),
        "blocking": False,
    }


# ═══════════════════════════════════════════════════════
# ACTION RECOMMENDATION
# ═══════════════════════════════════════════════════════

def _recommend_action(target_nation: str, world) -> Dict:
    """Recommend a diplomatic action for a specific nation."""
    diplo_key = world._make_diplo_key("France", target_nation)
    state = world.get_diplomatic_state("France", target_nation)
    relation = int(world.nation_relations.get(diplo_key, 0))
    advantage = _get_military_advantage(target_nation, world)

    france_war_score = get_war_score_for(world, "France", target_nation)

    if state == "WAR":
        if france_war_score > 20:
            path = "military"
            text = (
                f"Sire, we hold the upper hand against {target_nation}. "
                f"War score: {int(france_war_score)}. I recommend pressing for peace "
                f"on favorable terms. Their {advantage} military position means they "
                f"cannot sustain this war indefinitely.\n\n"
                f"Alternatively, continue fighting to improve terms further — "
                f"though I caution against overreach. Empires are lost to greed "
                f"as often as to defeat."
            )
            recommendation = "Propose peace with strong terms."
            hints = [f"Propose peace with {target_nation}", "Continue fighting for better terms"]
            confidence = "high"
        elif france_war_score < -20:
            path = "diplomatic"
            text = (
                f"Sire, I must speak plainly — the war with {target_nation} "
                f"does not favor us. War score: {int(france_war_score)}. "
                f"I strongly advise seeking an armistice before our position "
                f"deteriorates further.\n\n"
                f"Pride is a luxury we cannot afford when armies bleed."
            )
            recommendation = "Seek armistice immediately."
            hints = [f"Propose armistice with {target_nation}", "Reinforce the front lines"]
            confidence = "high"
        else:
            path = "combined"
            text = (
                f"Sire, the war with {target_nation} hangs in the balance. "
                f"War score: {int(france_war_score)}. Neither side commands a "
                f"decisive advantage.\n\n"
                f"I recommend the Tilsit model — win one more engagement, "
                f"then propose generous peace. Military pressure makes "
                f"diplomatic solutions cheaper."
            )
            recommendation = "Win a battle, then propose peace."
            hints = [
                f"Attack {target_nation}'s forces",
                f"Propose peace with {target_nation}",
            ]
            confidence = "medium"
    else:
        # At peace — recommend next diplomatic step
        if relation > 30 and state not in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
            text = (
                f"Sire, {target_nation} is well-disposed toward us — relations "
                f"stand at {relation}. The time is ripe to deepen our ties.\n\n"
                f"I recommend pursuing a formal alliance. The diplomatic cost "
                f"is modest and the strategic benefit immense."
            )
            recommendation = f"Pursue alliance with {target_nation}."
            hints = [f"Propose alliance with {target_nation}", "Improve relations further"]
            confidence = "high"
        elif relation > 0:
            text = (
                f"Sire, relations with {target_nation} are cautiously positive "
                f"at {relation}. We should nurture this goodwill.\n\n"
                f"I suggest improving relations through diplomatic missions. "
                f"A non-aggression pact would formalize our understanding."
            )
            recommendation = "Continue improving relations."
            hints = [f"Improve relations with {target_nation}", "Propose non-aggression pact"]
            confidence = "medium"
        elif relation > -40:
            text = (
                f"Sire, {target_nation} remains suspicious of our intentions — "
                f"relations at {relation}. Direct proposals would be rebuffed.\n\n"
                f"I recommend a patient courtship. Send diplomatic missions, "
                f"improve relations, and wait for the moment to present itself. "
                f"Diplomacy, like seduction, cannot be rushed."
            )
            recommendation = "Begin diplomatic courtship."
            hints = [f"Court {target_nation}", f"Improve relations with {target_nation}"]
            confidence = "medium"
        else:
            text = (
                f"Sire, {target_nation} harbors deep hostility — relations "
                f"at {relation}. Diplomacy will be a long and arduous road.\n\n"
                f"Frankly, Sire, some nations must be defeated before they "
                f"can be befriended. Consider whether military action might "
                f"achieve what words cannot."
            )
            recommendation = "Relations too hostile for diplomacy. Consider military options."
            hints = [f"Improve relations with {target_nation}", "Prepare for potential conflict"]
            confidence = "low"

    options = [
        {
            "label": "What should we do?",
            "description": f"Explore specific proposals for {target_nation}.",
            "action": "expand_to_proposal",
        },
        {
            "label": "Thank you",
            "description": "Dismiss.",
            "action": "dismiss",
        },
    ]

    return {
        "type": "advisory",
        "target_nation": target_nation,
        "talleyrand_text": text,
        "options": options,
        "context": {
            "situation_summary": _get_nation_summary(target_nation, world),
            "recommendation": recommendation,
            "confidence_level": confidence,
            "action_hints": hints,
        },
        "turn_created": int(world.current_turn),
        "blocking": False,
    }


def _recommend_action_overview(world) -> Dict:
    """General recommendation when no target nation specified."""
    return _diplomatic_overview(world)


# ═══════════════════════════════════════════════════════
# DIPLOMATIC OVERVIEW
# ═══════════════════════════════════════════════════════

def _diplomatic_overview(world) -> Dict:
    """Generate a full diplomatic overview across all nations."""
    lines = ["An overview, Sire:\n"]
    most_urgent_nation = None
    most_urgent_score = -999

    for nation in sorted(get_known_nations(world)):
        diplo_key = world._make_diplo_key("France", nation)
        state = world.get_diplomatic_state("France", nation)
        relation = int(world.nation_relations.get(diplo_key, 0))
        state_text = _STATE_DISPLAY.get(state, state.lower())
        summary = _get_nation_summary(nation, world)
        advantage = _get_military_advantage(nation, world)

        # Priority scoring: higher = more urgent to address
        urgency = 0
        urgency -= relation  # hostile = urgent
        if state == "WAR":
            urgency += 40
        elif state == "ARMISTICE":
            urgency += 15

        if urgency > most_urgent_score:
            most_urgent_score = urgency
            most_urgent_nation = nation

        war_note = ""
        if state == "WAR":
            france_ws = get_war_score_for(world, "France", nation)
            war_note = f" War score: {int(france_ws)}."

        lines.append(
            f"  {nation} — {state_text.capitalize()}. Relations: {relation}. "
            f"Military: {advantage}.{war_note} {summary}"
        )

    lines.append("")
    if most_urgent_nation:
        lines.append(
            f"My recommendation: address {most_urgent_nation} first, Sire. "
            f"Everything else can wait."
        )

    talleyrand_text = "\n".join(lines)

    recommendation = (
        f"Focus on {most_urgent_nation}."
        if most_urgent_nation
        else "The situation is stable."
    )
    hints = []
    if most_urgent_nation:
        state = world.get_diplomatic_state("France", most_urgent_nation)
        if state == "WAR":
            hints = [f"Propose peace with {most_urgent_nation}", "Win a decisive battle"]
        else:
            hints = [f"Court {most_urgent_nation}", f"Improve relations with {most_urgent_nation}"]

    options = []
    if most_urgent_nation:
        options.append({
            "label": f"Tell me about {most_urgent_nation}",
            "description": f"Detailed assessment of {most_urgent_nation}.",
            "action": "expand_to_proposal",
        })
    options.append({
        "label": "Thank you",
        "description": "Dismiss.",
        "action": "dismiss",
    })

    return {
        "type": "advisory",
        "target_nation": most_urgent_nation or "",
        "talleyrand_text": talleyrand_text,
        "options": options,
        "context": {
            "situation_summary": "Overview of all diplomatic relations.",
            "recommendation": recommendation,
            "confidence_level": "medium",
            "action_hints": hints,
        },
        "turn_created": int(world.current_turn),
        "blocking": False,
    }


# ═══════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════

def _get_nation_total_strength(nation: str, world) -> int:
    """Sum total troop strength across all marshals of a nation."""
    total = 0
    for marshal in world.marshals.values():
        if marshal.nation == nation and marshal.strength > 0:
            total += marshal.strength
    return int(total)


def _get_nation_visibility(nation: str, world) -> str:
    """Get fog visibility tier for a nation's forces (R65 fog fix).

    Imports the canonical helper from diplomatic_ledger.
    """
    from backend.game_logic.diplomatic_ledger import _get_nation_visibility as _ledger_vis
    return _ledger_vis(nation, world)


def _get_fogged_strength(nation: str, world) -> int:
    """Get fog-filtered numeric strength estimate for threat scoring.

    FULL/PARTIAL: exact raw strength.
    STALE: mid-point of display band (rough estimate).
    UNKNOWN: default estimate of 30000 (mid-range assumption).

    This prevents fog-of-war leaks in threat scoring calculations.
    """
    raw = _get_nation_total_strength(nation, world)
    vis = _get_nation_visibility(nation, world)

    if vis in ("full", "partial"):
        return raw

    if vis == "stale":
        # Return band mid-points matching _format_army_strength bands
        if raw < 10000:
            return 5000
        elif raw < 30000:
            return 20000
        elif raw < 60000:
            return 45000
        elif raw < 100000:
            return 80000
        else:
            return 120000

    # UNKNOWN: use a default mid-range estimate
    return 30000


def _get_military_advantage(nation: str, world) -> str:
    """Compare a nation's total military strength to France's.

    Returns fog-filtered qualitative assessment. FULL visibility gives
    exact ratios; lower tiers give vaguer descriptions (R65 fog fix).
    """
    nation_strength = _get_nation_total_strength(nation, world)
    france_strength = _get_nation_total_strength("France", world)
    vis = _get_nation_visibility(nation, world)

    # With unknown visibility, we can't assess military strength
    if vis == "unknown":
        return "unknown"

    if france_strength == 0:
        return "overwhelming" if nation_strength > 0 else "even"

    ratio = nation_strength / france_strength

    # Stale visibility: only broad bands (collapse slight/even/disadvantage)
    if vis == "stale":
        if ratio > 1.3:
            return "considerable"
        elif ratio > 0.7:
            return "comparable"
        else:
            return "modest"

    # PARTIAL or FULL: full detail
    if ratio > 1.5:
        return "overwhelming"
    elif ratio > 1.1:
        return "significant"
    elif ratio > 0.75:
        return "slight"
    elif ratio > 0.5:
        return "even"
    else:
        return "disadvantage"


def _get_nation_summary(nation: str, world) -> str:
    """One-liner summary for a nation's diplomatic posture."""
    diplo_key = world._make_diplo_key("France", nation)
    state = world.get_diplomatic_state("France", nation)
    relation = int(world.nation_relations.get(diplo_key, 0))
    diplomat = world.diplomats.get(nation)

    # Check for alliances with other nations (coalition risk)
    allied_with = []
    for other in get_known_nations(world):
        if other == nation:
            continue
        other_state = world.get_diplomatic_state(nation, other)
        if other_state in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
            allied_with.append(other)

    if state == "WAR":
        if allied_with:
            return f"Embattled, but allied with {', '.join(allied_with)}."
        return "At war with no allies to call upon." if relation < -40 else "Fighting, but not beyond reason."
    elif state in ("ALLIANCE", "DEFENSIVE_ALLIANCE"):
        return "A reliable partner — for now."
    elif state == "VASSAL":
        return "Subordinate to our will."
    elif relation > 20:
        if allied_with:
            return f"Friendly, but bound to {', '.join(allied_with)}."
        return "Amenable to deeper cooperation."
    elif relation > -20:
        if diplomat and diplomat.personality == "schemer":
            return "Watching, waiting, calculating."
        return "Neutral — could go either way."
    else:
        if allied_with:
            return f"Hostile, and allied with {', '.join(allied_with)}. A dangerous combination."
        return "Hostile. Tread carefully."
