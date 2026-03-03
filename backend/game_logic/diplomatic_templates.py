"""
Diplomatic Template Library — Phase 8 Session 3

Templates T1-T10 for Talleyrand's conversational diplomacy.
Templates T11-T27 are Session 4-6 scope.

Architecture:
  DIPLOMATIC_TEMPLATES keyed by (situation, game_bucket, specificity)
  Each template has text (with {slots}), options, and recommendation index.
"""

from typing import Dict, Optional

# ═══════ TEMPLATE LIBRARY ═══════
# Key: (intent_type, diplo_state, bucket_group)
# bucket_group: specific bucket name OR "any" for wildcard
# Lookup order: exact match → (intent, state, "any") → fallback

DIPLOMATIC_TEMPLATES = {
    # ══════════════════════════════════════════════
    # T1: VAGUE + WAR + winning_comfortably
    # ══════════════════════════════════════════════
    ("proposal_options", "WAR", "winning_comfortably"): {
        "text": (
            "Sire, we hold a commanding position against {target_nation}. "
            "War score stands at {war_score}. I see several paths forward."
        ),
        "options": [
            {
                "label": "Generous peace",
                "description": "Offer magnanimous terms — build goodwill for the future.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Harsh demands",
                "description": "Press our advantage — demand territory and tribute.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Continue fighting",
                "description": "We can extract more concessions on the battlefield.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T2: VAGUE + WAR + losing_badly
    # ══════════════════════════════════════════════
    ("proposal_options", "WAR", "losing_badly"): {
        "text": (
            "Sire, our position against {target_nation} is... precarious. "
            "War score: {war_score}. We must act before things deteriorate further."
        ),
        "options": [
            {
                "label": "Sue for peace",
                "description": "Request peace on reasonable terms while we still can.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Offer concessions",
                "description": "Sweeten the deal with gold or territory to secure acceptance.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Stall",
                "description": "Buy time — request an armistice while we regroup.",
                "action": "execute_proposal",
                "proposal_type": "armistice",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T3: VAGUE + WAR + stalemate (also winning_slightly, losing_slightly)
    # ══════════════════════════════════════════════
    ("proposal_options", "WAR", "stalemate"): {
        "text": (
            "Sire, the war with {target_nation} is at a standstill. "
            "War score: {war_score}. Neither side has a decisive advantage."
        ),
        "options": [
            {
                "label": "Propose peace",
                "description": "End the bloodshed on balanced terms.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Press advantage",
                "description": "Continue the campaign — one victory could tip the balance.",
                "action": "dismiss",
            },
            {
                "label": "Wait",
                "description": "Hold position and see how events unfold.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T4: VAGUE + PEACE + hostile
    # ══════════════════════════════════════════════
    ("proposal_options", "PEACE", "hostile"): {
        "text": (
            "Sire, relations with {target_nation} are tense. "
            "Current relation: {relation}. State: {current_state}. "
            "Tread carefully."
        ),
        "options": [
            {
                "label": "Improve relations",
                "description": "Send me to build bridges — a diplomatic mission.",
                "action": "start_mission",
                "terms": {"mission_type": "IMPROVE_RELATIONS"},
            },
            {
                "label": "Propose open borders",
                "description": "A small step — opening borders shows good faith.",
                "action": "execute_proposal",
                "proposal_type": "open_borders",
            },
            {
                "label": "Leave them be",
                "description": "Some wounds need time to heal.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T5: VAGUE + PEACE + friendly
    # ══════════════════════════════════════════════
    ("proposal_options", "PEACE", "friendly"): {
        "text": (
            "Sire, {target_nation} views us favorably. "
            "Relation: {relation}. State: {current_state}. "
            "The time may be ripe to deepen our ties."
        ),
        "options": [
            {
                "label": "Propose alliance",
                "description": "A full military alliance — mutual defense and cooperation.",
                "action": "execute_proposal",
                "proposal_type": "alliance",
            },
            {
                "label": "Non-aggression pact",
                "description": "A more cautious step — guarantee peace without military commitment.",
                "action": "execute_proposal",
                "proposal_type": "non_aggression",
            },
            {
                "label": "Vassalage",
                "description": "Bind them to our will as a vassal state.",
                "action": "execute_proposal",
                "proposal_type": "vassalage",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T6: MEDIUM + WAR (any bucket) — suggest specific terms
    # ══════════════════════════════════════════════
    ("proposal_confirm", "WAR", "any"): {
        "text": (
            "Sire, for a {proposal_type} proposal to {target_nation}, "
            "I suggest the following terms. War score: {war_score}, relation: {relation}."
        ),
        "options": [
            {
                "label": "Send as suggested",
                "description": "Send the proposal with my recommended terms.",
                "action": "execute_proposal",
            },
            {
                "label": "Harsher terms",
                "description": "Demand more — we can afford to push.",
                "action": "modify_harsh",
            },
            {
                "label": "More generous",
                "description": "Sweeten the offer to improve chances of acceptance.",
                "action": "modify_generous",
            },
            {
                "label": "Reconsider",
                "description": "Let me think about this.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T6b: MEDIUM + PEACE (any bucket)
    # ══════════════════════════════════════════════
    ("proposal_confirm", "PEACE", "any"): {
        "text": (
            "Sire, for a {proposal_type} proposal to {target_nation}, "
            "I have prepared appropriate terms. Relation: {relation}, state: {current_state}."
        ),
        "options": [
            {
                "label": "Send as suggested",
                "description": "Send the proposal with my recommended terms.",
                "action": "execute_proposal",
            },
            {
                "label": "Adjust terms",
                "description": "Let me see what else we could offer or demand.",
                "action": "expand_options",
            },
            {
                "label": "Reconsider",
                "description": "Let me think about this.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T7: SPECIFIC + agree (Talleyrand agrees)
    # Fast-track: immediate execution with [Send][Reconsider]
    # ══════════════════════════════════════════════
    ("proposal_execute", "WAR", "any"): {
        "text": "At once, Sire. I shall deliver your {proposal_type} proposal to {target_nation}.",
        "options": [
            {
                "label": "Send",
                "description": "Dispatch Talleyrand immediately.",
                "action": "send",
            },
            {
                "label": "Reconsider",
                "description": "Wait — let me reconsider.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },

    ("proposal_execute", "PEACE", "any"): {
        "text": "At once, Sire. I shall present your {proposal_type} proposal to {target_nation}.",
        "options": [
            {
                "label": "Send",
                "description": "Dispatch Talleyrand immediately.",
                "action": "send",
            },
            {
                "label": "Reconsider",
                "description": "Wait — let me reconsider.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },

    # ══════════════════════════════════════════════
    # T8: SPECIFIC + object (Talleyrand disagrees)
    # STUB for Session 3 — always agrees (T7 used instead)
    # Real objection logic added in Session 6
    # ══════════════════════════════════════════════

    # ══════════════════════════════════════════════
    # T9: FEASIBILITY — handled by generate_feasibility_dialogue()
    # Template not needed here; logic is in diplomatic_dialogue.py
    # ══════════════════════════════════════════════

    # ══════════════════════════════════════════════
    # T10: MISSION START — handled by generate_mission_dialogue()
    # Template not needed here; logic is in diplomatic_dialogue.py
    # ══════════════════════════════════════════════
}

# ═══════ FALLBACK TEMPLATES ═══════
# Used when no exact template match is found

FALLBACK_TEMPLATES = {
    "proposal_options": {
        "text": (
            "Sire, how shall I approach {target_nation}? "
            "Current state: {current_state}, relation: {relation}."
        ),
        "options": [
            {
                "label": "Propose peace",
                "description": "Seek a peaceful resolution.",
                "action": "execute_proposal",
                "proposal_type": "peace",
            },
            {
                "label": "Improve relations",
                "description": "Send me on a diplomatic mission.",
                "action": "start_mission",
                "terms": {"mission_type": "IMPROVE_RELATIONS"},
            },
            {
                "label": "Dismiss",
                "description": "Not now.",
                "action": "dismiss",
            },
        ],
        "recommendation": 0,
    },
    "proposal_confirm": {
        "text": (
            "Sire, I shall prepare a {proposal_type} proposal for {target_nation}. "
            "Shall I proceed with standard terms?"
        ),
        "options": [
            {
                "label": "Proceed",
                "description": "Send with suggested terms.",
                "action": "execute_proposal",
            },
            {
                "label": "Reconsider",
                "description": "Let me think about this.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },
    "proposal_execute": {
        "text": "At once, Sire. I shall deliver your proposal to {target_nation}.",
        "options": [
            {
                "label": "Send",
                "description": "Dispatch immediately.",
                "action": "send",
            },
            {
                "label": "Reconsider",
                "description": "Wait.",
                "action": "reconsider",
            },
        ],
        "recommendation": 0,
    },
}


def get_template(intent_type: str, diplo_state: str, bucket: str,
                 proposal_type: Optional[str] = None) -> Dict:
    """Look up the best matching template.

    Lookup order:
    1. Exact match: (intent_type, diplo_state, bucket)
    2. Wildcard bucket: (intent_type, diplo_state, "any")
    3. Similar buckets for WAR states
    4. Fallback by intent_type
    """
    # 1. Exact match
    key = (intent_type, diplo_state, bucket)
    if key in DIPLOMATIC_TEMPLATES:
        template = _deep_copy_template(DIPLOMATIC_TEMPLATES[key])
        if proposal_type:
            template["_proposal_type"] = proposal_type
        return template

    # 2. Wildcard bucket
    key = (intent_type, diplo_state, "any")
    if key in DIPLOMATIC_TEMPLATES:
        template = _deep_copy_template(DIPLOMATIC_TEMPLATES[key])
        if proposal_type:
            template["_proposal_type"] = proposal_type
        return template

    # 3. Similar buckets for WAR
    if diplo_state == "WAR":
        similar_map = {
            "winning_slightly": "winning_comfortably",
            "losing_slightly": "losing_badly",
        }
        similar = similar_map.get(bucket)
        if similar:
            key = (intent_type, diplo_state, similar)
            if key in DIPLOMATIC_TEMPLATES:
                template = _deep_copy_template(DIPLOMATIC_TEMPLATES[key])
                if proposal_type:
                    template["_proposal_type"] = proposal_type
                return template

    # 4. Neutral bucket for PEACE
    if diplo_state == "PEACE" and bucket == "neutral":
        # Try hostile template as fallback for neutral
        key = (intent_type, diplo_state, "hostile")
        if key in DIPLOMATIC_TEMPLATES:
            template = _deep_copy_template(DIPLOMATIC_TEMPLATES[key])
            if proposal_type:
                template["_proposal_type"] = proposal_type
            return template

    # 5. Fallback
    if intent_type in FALLBACK_TEMPLATES:
        template = _deep_copy_template(FALLBACK_TEMPLATES[intent_type])
        if proposal_type:
            template["_proposal_type"] = proposal_type
        return template

    # Ultimate fallback
    return {
        "text": "Sire, I await your instructions regarding {target_nation}.",
        "options": [
            {"label": "Dismiss", "description": "Never mind.", "action": "dismiss"},
        ],
        "recommendation": 0,
    }


def _deep_copy_template(template: Dict) -> Dict:
    """Deep copy a template dict (simple structures only)."""
    result = {
        "text": template["text"],
        "options": [opt.copy() for opt in template.get("options", [])],
        "recommendation": template.get("recommendation", 0),
    }
    # Copy terms dicts in options
    for i, opt in enumerate(result["options"]):
        if "terms" in template.get("options", [])[i]:
            result["options"][i]["terms"] = template["options"][i]["terms"].copy()
    return result


def resolve_template_text(text: str, world, target_nation: Optional[str] = None) -> str:
    """Resolve {slot_name} placeholders in template text.

    Golden Rule #2: ALL numeric slots are int() wrapped.
    """
    if not text:
        return text

    slots = {}

    if target_nation:
        slots["target_nation"] = target_nation

        # Get diplomat for target nation
        diplomats = getattr(world, 'diplomats', {})
        target_diplomat = diplomats.get(target_nation)
        slots["target_diplomat"] = target_diplomat.name if target_diplomat else "their diplomat"

        # Numeric values
        diplo_key = world._make_diplo_key("France", target_nation)
        slots["war_score"] = str(int(world.war_scores.get(diplo_key, 0)))
        slots["relation"] = str(int(world.nation_relations.get(diplo_key, 0)))
        slots["current_state"] = world.get_diplomatic_state("France", target_nation)
        slots["dp_cost"] = "1"  # Default, overridden per-context

    # Generic slots
    slots["dp"] = str(int(getattr(world, 'diplomatic_points', 0)))

    # Resolve — use .get for safety
    try:
        return text.format_map(_SafeFormatMap(slots))
    except (KeyError, ValueError):
        return text


class _SafeFormatMap(dict):
    """Format map that returns {key} for missing keys instead of raising."""
    def __missing__(self, key):
        return "{" + key + "}"


def resolve_template_text_with_type(text: str, world, target_nation: Optional[str],
                                     proposal_type: Optional[str] = None) -> str:
    """Resolve template text with proposal_type slot."""
    result = resolve_template_text(text, world, target_nation)
    if proposal_type and "{proposal_type}" in result:
        result = result.replace("{proposal_type}", proposal_type)
    return result


# ═══════ SUGGESTED TERMS GENERATION ═══════

def generate_suggested_terms(target_nation: str, proposal_type: str, world) -> Dict:
    """Generate reasonable default treaty terms based on game state.

    Returns a dict with proposal terms suitable for calculate_acceptance().
    """
    diplo_key = world._make_diplo_key("France", target_nation)
    relation = world.nation_relations.get(diplo_key, 0)
    war_score = world.war_scores.get(diplo_key, 0)

    terms = {
        "type": proposal_type,
        "proposer_nation": "France",
        "target_nation": target_nation,
        "sweeteners": [],
        "demands": [],
        "clauses": [],
    }

    if proposal_type == "peace":
        # Include open borders if relation isn't too hostile
        if relation > -20:
            terms["clauses"].append("open_borders")

        # If winning, demand gold/turn proportional to advantage
        if war_score > 20:
            gold_demand = min(300, war_score * 5)
            terms["demands"].append({"type": "gold_per_turn", "value": int(gold_demand)})
        elif war_score < -20:
            # If losing, offer gold to sweeten
            gold_offer = min(200, abs(war_score) * 3)
            terms["sweeteners"].append({"type": "gold_per_turn", "value": int(gold_offer)})

    elif proposal_type == "alliance":
        # Alliance: minimal terms, mutual defense
        terms["clauses"].append("open_borders")

    elif proposal_type == "vassalage":
        # Vassalage: tribute based on target economy
        target_gold = world.nation_gold.get(target_nation, 500)
        tribute = max(100, int(target_gold * 0.15))
        terms["demands"].append({"type": "gold_per_turn", "value": int(tribute)})

    elif proposal_type == "open_borders":
        terms["clauses"].append("open_borders")

    elif proposal_type == "non_aggression":
        pass  # No special terms needed

    elif proposal_type in ("armistice", "armistice_losing", "armistice_winning"):
        # Armistice is a temporary ceasefire
        terms["type"] = "armistice_losing" if war_score < 0 else "armistice_winning"

    return terms


def calculate_treaty_harshness(treaty: Dict) -> float:
    """Calculate harshness score (0.0-1.0) from treaty clauses.

    Used for DD8-4 escalating harshness tracking.
    """
    harshness = 0.0
    for clause in treaty.get("clauses", []):
        ctype = clause.get("type", "")
        if ctype == "gold_per_turn":
            harshness += 0.1 * (clause.get("amount", 0) / 100)
        elif ctype == "territory_cede":
            harshness += 0.2 * len(clause.get("regions", []))
        elif ctype == "manpower_per_turn":
            harshness += 0.15
    return min(1.0, harshness)
