"""
Diplomatic Dialogue State Machine — Phase 8 Session 3

Handles specificity classification, dialogue generation, and game state bucketing
for Talleyrand's conversational diplomacy system.

Entry points:
  - classify_diplomatic_intent() → routes parsed command to dialogue type
  - generate_dialogue() → creates pending_diplomatic_dialogue dict
  - get_game_bucket() → determines game situation for template selection
"""

from typing import Dict, Optional


# ═══════ NATION NAME ALIASES ═══════
NATION_ALIASES = {
    "england": "Britain",
    "uk": "Britain",
    "united kingdom": "Britain",
    "great britain": "Britain",
    "british": "Britain",
    "english": "Britain",
    "britain": "Britain",
    "prussian": "Prussia",
    "prussia": "Prussia",
    "austrian": "Austria",
    "austria": "Austria",
    "saxon": "Saxony",
    "saxons": "Saxony",
    "saxony": "Saxony",
    "france": "France",
    "french": "France",
}

KNOWN_NATIONS = {"Britain", "Prussia", "Austria", "Saxony"}


def get_known_nations(world=None) -> set:
    """Return the set of known nations, including any vassals (R93)."""
    nations = set(KNOWN_NATIONS)
    if world:
        vassals = getattr(world, 'vassals', {})
        nations.update(vassals.keys())
    return nations

# ═══════ PROPOSAL TYPE KEYWORDS ═══════
PROPOSAL_TYPE_KEYWORDS = {
    "peace": ["peace", "ceasefire", "end the war", "stop fighting", "end hostilities"],
    "alliance": ["alliance", "ally", "allies", "allied"],
    "armistice": ["armistice", "truce", "temporary peace"],
    "open_borders": ["open borders", "free passage", "passage rights", "border access"],
    "non_aggression": ["non-aggression", "non aggression", "nonaggression", "pact"],
    "vassalage": ["vassal", "vassalage", "subjugate", "submit", "submission", "puppet"],
}

# ═══════ PROPOSAL TYPE DISPLAY NAMES ═══════
PROPOSAL_TYPE_DISPLAY = {
    "peace": "Peace Treaty",
    "alliance": "Full Alliance",
    "non_aggression": "Non-Aggression Pact",
    "open_borders": "Open Borders Agreement",
    "defensive_alliance": "Defensive Alliance",
    "armistice": "Armistice",
    "armistice_losing": "Armistice",
    "armistice_stalemate": "Armistice",
    "armistice_winning": "Armistice",
    "vassalage": "Vassalage",
    "opportunistic": "Non-Aggression Pact",
}


def _display_proposal_type(proposal_type: str) -> str:
    """Convert internal proposal_type to player-facing display name."""
    return PROPOSAL_TYPE_DISPLAY.get(proposal_type, proposal_type.replace("_", " ").title())


# ═══════ MISSION TYPE KEYWORDS ═══════
MISSION_TYPE_KEYWORDS = {
    "IMPROVE_RELATIONS": ["improve relations", "build relations", "warm relations", "befriend"],
    "COURT_NATION": ["court", "charm", "woo", "seduce", "win over", "sway"],
    "GATHER_INTEL": ["gather intel", "spy", "intelligence", "information"],
    "UNDERMINE_ALLIANCE": ["undermine", "sabotage", "weaken alliance", "drive a wedge"],
    "REASSURE_ALLY": ["reassure", "calm", "soothe", "appease"],
}

# ═══════ FEASIBILITY KEYWORDS ═══════
FEASIBILITY_KEYWORDS = [
    "what would it take", "can we", "is it possible", "how hard",
    "feasibility", "realistic", "should i focus", "what are the chances",
    "how likely", "what do we need", "what must we do",
]

# ═══════ MISSION DP COSTS ═══════
MISSION_DP_COSTS = {
    "IMPROVE_RELATIONS": 1,
    "COURT_NATION": 2,
    "GATHER_INTEL": 1,
    "UNDERMINE_ALLIANCE": 2,
    "REASSURE_ALLY": 1,
    "CONTINENTAL_SYSTEM": 1,  # R18: Explicit (was defaulting to 1 via .get)
}

# ═══════ MISSION EFFECTS ═══════
MISSION_EFFECTS = {
    "IMPROVE_RELATIONS": {"relation_change": 5},
    "COURT_NATION": {"relation_change": 5, "undermine_chance": 0.20, "undermine_amount": -3},
    "GATHER_INTEL": {"duration": 3},
    "UNDERMINE_ALLIANCE": {"target_pair_relation_change": -3},
    "REASSURE_ALLY": {"relation_change": 3},
}

MISSION_DESCRIPTIONS = {
    "IMPROVE_RELATIONS": "improve relations",
    "COURT_NATION": "court and charm",
    "GATHER_INTEL": "gather intelligence on",
    "UNDERMINE_ALLIANCE": "undermine alliances with",
    "REASSURE_ALLY": "reassure",
}


def resolve_nation_name(text: str) -> Optional[str]:
    """Fuzzy match a nation name from text. Returns canonical name or None."""
    text_lower = text.lower().strip()

    # Direct alias match
    for alias, canonical in NATION_ALIASES.items():
        if alias in text_lower:
            return canonical

    return None


def extract_nation_from_command(raw_text: str) -> Optional[str]:
    """Extract target nation from a diplomatic command string."""
    text_lower = raw_text.lower()

    # Try each known nation (and aliases)
    for alias, canonical in NATION_ALIASES.items():
        if alias in text_lower and canonical != "France":
            return canonical

    return None


def extract_proposal_type(raw_text: str) -> Optional[str]:
    """Extract proposal type from command text."""
    text_lower = raw_text.lower()
    for ptype, keywords in PROPOSAL_TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return ptype
    return None


def extract_mission_type(raw_text: str) -> Optional[str]:
    """Extract mission type from command text."""
    text_lower = raw_text.lower()

    # Check cancel first
    if any(kw in text_lower for kw in ["cancel mission", "halt mission", "stop mission",
                                        "cancel diplomatic", "abort mission"]):
        return "CANCEL"

    for mtype, keywords in MISSION_TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return mtype
    return None


def classify_diplomatic_intent(parsed_command: Dict, world) -> str:
    """Classify what kind of diplomatic dialogue to generate.

    Returns one of:
        "not_diplomatic" — no diplomatic keywords
        "unknown_nation" — nation mentioned but not recognized
        "feasibility" — asking about possibility
        "advisory" — general question (stub for Session 4)
        "mission" — start/cancel a diplomatic mission
        "proposal_execute" — SPECIFIC: has proposal type + clauses
        "proposal_confirm" — MEDIUM: has proposal type, needs confirmation
        "proposal_options" — VAGUE: needs to pick proposal type
    """
    raw_text = parsed_command.get("raw_text", "")
    target_nation = parsed_command.get("target_nation")
    has_proposal_type = parsed_command.get("proposal_type") is not None
    has_clauses = len(parsed_command.get("clauses", [])) > 0
    is_question = parsed_command.get("is_question", False)
    has_diplomatic_keywords = parsed_command.get("has_diplomatic_keywords", True)
    mission_type = parsed_command.get("mission_type")

    if not has_diplomatic_keywords and not is_question and not mission_type:
        return "not_diplomatic"

    # Check for unknown nation (mentioned but not recognized)
    if target_nation and target_nation not in KNOWN_NATIONS:
        return "unknown_nation"

    # Mission commands
    if mission_type:
        return "mission"

    # Question classification
    if is_question:
        text_lower = raw_text.lower()
        if any(kw in text_lower for kw in FEASIBILITY_KEYWORDS):
            return "feasibility"
        return "advisory"

    # Specificity classification
    if has_clauses:
        return "proposal_execute"
    elif has_proposal_type:
        return "proposal_confirm"
    else:
        return "proposal_options"


def get_game_bucket(target_nation: str, world) -> str:
    """Determine the game state bucket for template selection.

    Returns one of:
        At war: "winning_comfortably", "winning_slightly", "stalemate",
                "losing_slightly", "losing_badly"
        At peace: "friendly", "neutral", "hostile"
    """
    state = world.get_diplomatic_state("France", target_nation)
    if state == "WAR":
        war_score = world.war_scores.get(world._make_diplo_key("France", target_nation), 0)
        # Adjust sign: war_score is for alphabetically-sorted key
        diplo_key = world._make_diplo_key("France", target_nation)
        parts = diplo_key.split("|")
        if len(parts) == 2 and parts[0] == target_nation:
            war_score = -war_score

        if war_score > 30:
            return "winning_comfortably"
        if war_score > 0:
            return "winning_slightly"
        if war_score > -10:
            return "stalemate"
        if war_score > -30:
            return "losing_slightly"
        return "losing_badly"
    else:
        relation = world.nation_relations.get(world._make_diplo_key("France", target_nation), 0)
        if relation > 20:
            return "friendly"
        if relation > -20:
            return "neutral"
        return "hostile"


def generate_dialogue(intent_type: str, parsed_command: Dict, world) -> Dict:
    """Generate a pending_diplomatic_dialogue dict based on intent classification.

    Returns a dict suitable for storage as world.pending_diplomatic_dialogue.
    """
    from backend.game_logic.diplomatic_templates import (
        get_template, resolve_template_text, generate_suggested_terms,
    )

    target_nation = parsed_command.get("target_nation")
    proposal_type = parsed_command.get("proposal_type")
    raw_text = parsed_command.get("raw_text", "")

    # Determine game bucket
    bucket = get_game_bucket(target_nation, world) if target_nation else "neutral"

    # Determine diplomatic state for template matching
    diplo_state = "WAR" if target_nation and world.get_diplomatic_state("France", target_nation) == "WAR" else "PEACE"

    # Get template
    template = get_template(intent_type, diplo_state, bucket, proposal_type)

    # Resolve slots in template text (including {proposal_type})
    talleyrand_text = resolve_template_text(
        template.get("text", ""), world, target_nation)
    if proposal_type and "{proposal_type}" in talleyrand_text:
        talleyrand_text = talleyrand_text.replace("{proposal_type}", _display_proposal_type(proposal_type))

    # Build options with resolved text
    options = []
    for opt in template.get("options", []):
        resolved_opt = {
            "label": opt["label"],
            "description": resolve_template_text(
                opt.get("description", ""), world, target_nation),
            "action": opt["action"],
        }
        if "terms" in opt:
            resolved_opt["terms"] = opt["terms"]
        elif opt["action"] == "execute_proposal" and target_nation:
            # Generate terms for execute options
            ptype = opt.get("proposal_type", proposal_type)
            if ptype:
                resolved_opt["terms"] = generate_suggested_terms(
                    target_nation, ptype, world)
                resolved_opt["terms"]["proposal_type"] = ptype
        options.append(resolved_opt)

    # Build context snapshot
    context = {}
    if target_nation:
        diplo_key = world._make_diplo_key("France", target_nation)
        context = {
            "war_score": int(world.war_scores.get(diplo_key, 0)),
            "relation": int(world.nation_relations.get(diplo_key, 0)),
            "threat": int(getattr(world, 'threat_level', 0)),
            "current_state": world.get_diplomatic_state("France", target_nation),
        }

    dialogue = {
        "type": intent_type,
        "target_nation": target_nation or "",
        "talleyrand_text": talleyrand_text,
        "options": options,
        "context": context,
        "turn_created": int(world.current_turn),
        "blocking": False,
    }

    # ═══════ SESSION 6: Pre-proposal objection merge ═══════
    # When sending a proposal, evaluate Talleyrand's concern and merge
    # into the dialogue (not a separate popup per §10a).
    if intent_type in ("proposal_execute", "proposal_confirm") and target_nation:
        dialogue = _merge_pre_proposal_objection(dialogue, parsed_command, world)

    return dialogue


def _merge_pre_proposal_objection(dialogue: Dict, parsed_command: Dict, world) -> Dict:
    """Merge Talleyrand's pre-proposal objection into the dialogue flow.

    V2a pattern: MILD = flavor text (no blocking), MODERATE/STRONG = inline
    options with "Send anyway" / "Modify terms" / "Trust Talleyrand".

    Args:
        dialogue: The base dialogue dict
        parsed_command: Original parsed command
        world: WorldState

    Returns:
        Modified dialogue dict with objection merged
    """
    from backend.commands.diplomatic_defiance import (
        evaluate_pre_proposal_objection, get_objection_text,
    )

    # Build a lightweight proposal for objection evaluation
    proposal = {
        "type": parsed_command.get("proposal_type", "peace"),
        "target_nation": parsed_command.get("target_nation", ""),
        "demands": parsed_command.get("clauses", []),
        "sweeteners": [],
    }

    # Get Talleyrand
    diplomats = getattr(world, 'diplomats', {})
    talleyrand = diplomats.get("France")
    if not talleyrand:
        return dialogue

    concern = evaluate_pre_proposal_objection(proposal, talleyrand, world)

    from backend.commands.objection_v2 import ConcernLevel

    if concern == ConcernLevel.NONE:
        return dialogue  # No objection

    objection_text = get_objection_text(concern, proposal, talleyrand)

    if concern == ConcernLevel.MILD:
        # MILD: flavor text prepended, no blocking, no extra options
        dialogue["talleyrand_text"] = objection_text + "\n\n" + dialogue["talleyrand_text"]
        dialogue["objection_level"] = "mild"
    else:
        # MODERATE/STRONG: inline options merged into dialogue
        dialogue["talleyrand_text"] = objection_text
        dialogue["objection_level"] = "strong" if concern >= ConcernLevel.STRONG else "moderate"
        dialogue["blocking"] = False  # Still not a popup — inline in conversation

        # Set diplomatic_objection_popup for Godot (Session 8C)
        concern_label = "STRONG" if concern >= ConcernLevel.STRONG else "MODERATE"
        defiance_risk = "High" if concern >= ConcernLevel.STRONG else "Medium"
        proposal_summary = f"{proposal.get('type', 'unknown')} with {proposal.get('target_nation', 'unknown')}"
        world.diplomatic_objection_popup = {
            "concern_level": concern_label,
            "objection_text": objection_text,
            "defiance_risk": defiance_risk,
            "proposal_summary": proposal_summary,
        }

        # R42: Preserve original terms for send_override/send_suggested handlers
        # Find original proposal terms from the pre-objection options
        target_nation = parsed_command.get("target_nation", "")
        original_terms = None
        for opt in dialogue.get("options", []):
            if opt.get("action") == "execute_proposal" and opt.get("terms"):
                original_terms = opt["terms"]
                break

        # Generate Talleyrand's suggested (softer) terms
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        proposal_type = parsed_command.get("proposal_type", "peace")
        suggested_terms = generate_suggested_terms(target_nation, proposal_type, world) if target_nation else {}
        if suggested_terms:
            suggested_terms["proposal_type"] = proposal_type

        # Store in context for executor handlers
        dialogue["context"]["original_proposal"] = original_terms or {"proposal_type": proposal_type}
        dialogue["context"]["suggested_terms"] = suggested_terms

        # Replace options with objection-aware choices
        dialogue["options"] = [
            {
                "label": "Send my terms as ordered",
                "description": "Insist on your original proposal. Defiance may trigger during transit.",
                "action": "send_override",
                "terms": original_terms or {"proposal_type": proposal_type},
            },
            {
                "label": "Use Talleyrand's suggestion",
                "description": "Trust his diplomatic judgment.",
                "action": "send_suggested",
                "terms": suggested_terms,
            },
            {
                "label": "Modify terms",
                "description": "Reconsider the proposal.",
                "action": "reconsider",
            },
        ]

    return dialogue


def generate_feasibility_dialogue(parsed_command: Dict, world) -> Dict:
    """Generate a feasibility assessment dialogue (0 DP cost)."""
    from backend.game_logic.diplomacy import calculate_acceptance, get_dp_cost

    target_nation = parsed_command.get("target_nation")
    proposal_type = parsed_command.get("proposal_type", "peace")

    if not target_nation:
        return {
            "type": "feasibility",
            "target_nation": "",
            "talleyrand_text": "Sire, I need to know which nation you wish me to assess.",
            "options": [
                {"label": "Dismiss", "description": "Never mind.", "action": "dismiss"},
            ],
            "context": {},
            "turn_created": int(world.current_turn),
            "blocking": False,
        }

    # Run hypothetical acceptance
    hypothetical = {
        "type": proposal_type,
        "proposer_nation": "France",
        "target_nation": target_nation,
        "sweeteners": [],
        "demands": [],
        "clauses": [],
    }
    result = calculate_acceptance(hypothetical, world)
    score = result["score"]
    outcome = result["outcome"]
    components = result["components"]
    feedback = result["feedback"]

    # Find largest obstacle
    largest_obstacle = ""
    worst_val = 0
    for key, val in components.items():
        if val < worst_val:
            worst_val = val
            largest_obstacle = key

    # Calculate steps to goal
    current_state = world.get_diplomatic_state("France", target_nation)
    from backend.game_logic.diplomacy import _UPGRADE_ORDER
    target_state_map = {
        "peace": "PEACE",
        "alliance": "ALLIANCE",
        "open_borders": "OPEN_BORDERS",
        "non_aggression": "NON_AGGRESSION",
        "armistice": "ARMISTICE",
    }
    goal_state = target_state_map.get(proposal_type, "PEACE")
    steps = 0
    if current_state in _UPGRADE_ORDER and goal_state in _UPGRADE_ORDER:
        curr_idx = _UPGRADE_ORDER.index(current_state)
        goal_idx = _UPGRADE_ORDER.index(goal_state)
        steps = max(0, goal_idx - curr_idx)

    # Build assessment text
    display_type = _display_proposal_type(proposal_type)
    if score >= 50:
        assessment = (
            f"Sire, {display_type} with {target_nation} appears quite achievable. "
            f"My assessment suggests a score of {int(score)} — they would likely accept. "
            f"{feedback}"
        )
    elif score >= 30:
        assessment = (
            f"Sire, {display_type} with {target_nation} is possible but uncertain. "
            f"My assessment yields {int(score)} — they might counter-offer. "
            f"{feedback}"
        )
    else:
        obstacle_names = {
            "relation_modifier": "our poor relations",
            "war_score_modifier": "the military situation",
            "threat_modifier": "their fear of us",
            "deal_balance": "the balance of terms",
            "personality_modifier": "their diplomat's disposition",
            "base_disposition": "fundamental resistance to this type of agreement",
        }
        obstacle_text = obstacle_names.get(largest_obstacle, "several factors")
        assessment = (
            f"Sire, I must be frank — {display_type} with {target_nation} faces serious obstacles. "
            f"My assessment is only {int(score)}. The largest obstacle is {obstacle_text}. "
            f"{feedback}"
        )

    if steps > 0:
        assessment += f" We would need {steps} diplomatic steps to reach {goal_state}."

    # DP cost info
    dp_cost = get_dp_cost(f"propose_{proposal_type}", 10)
    assessment += f" The proposal itself would cost {int(dp_cost)} DP."

    return {
        "type": "feasibility",
        "target_nation": target_nation,
        "talleyrand_text": assessment,
        "options": [
            {
                "label": "Proceed anyway",
                "description": f"Send the {display_type} proposal despite the assessment.",
                "action": "execute_proposal",
                "terms": {
                    "proposal_type": proposal_type,
                    "target_nation": target_nation,
                    "sweeteners": [],
                    "demands": [],
                    "clauses": [],
                },
            },
            {"label": "Dismiss", "description": "Thank you, Talleyrand.", "action": "dismiss"},
        ],
        "context": {
            "war_score": int(world.war_scores.get(world._make_diplo_key("France", target_nation), 0)),
            "relation": int(world.nation_relations.get(world._make_diplo_key("France", target_nation), 0)),
            "threat": int(getattr(world, 'threat_level', 0)),
            "acceptance_score": int(score),
            "acceptance_outcome": outcome,
            "largest_obstacle": largest_obstacle,
            "steps_to_goal": int(steps),
        },
        "turn_created": int(world.current_turn),
        "blocking": False,
    }


def generate_mission_dialogue(parsed_command: Dict, world) -> Dict:
    """Generate a mission confirmation dialogue."""
    target_nation = parsed_command.get("target_nation")
    mission_type = parsed_command.get("mission_type")

    if not target_nation:
        return {
            "type": "mission",
            "target_nation": "",
            "talleyrand_text": "Sire, where shall I direct my efforts?",
            "options": [
                {"label": "Dismiss", "description": "Never mind.", "action": "dismiss"},
            ],
            "context": {},
            "turn_created": int(world.current_turn),
            "blocking": False,
        }

    if mission_type == "CANCEL":
        return {
            "type": "mission",
            "target_nation": target_nation,
            "talleyrand_text": "Very well, Sire. I shall cease my diplomatic efforts.",
            "options": [
                {
                    "label": "Confirm cancel",
                    "description": "Cancel the current mission.",
                    "action": "cancel_mission",
                },
                {"label": "Continue mission", "description": "Keep the current mission active.", "action": "dismiss"},
            ],
            "context": {},
            "turn_created": int(world.current_turn),
            "blocking": False,
        }

    description = MISSION_DESCRIPTIONS.get(mission_type, "conduct diplomacy with")
    dp_cost = MISSION_DP_COSTS.get(mission_type, 1)

    # Check for existing mission
    existing = getattr(world, 'active_diplomatic_mission', None)
    existing_text = ""
    if existing and not existing.get("completed"):
        existing_text = (
            f" Note: this will replace my current mission to "
            f"{MISSION_DESCRIPTIONS.get(existing['type'], 'conduct diplomacy with')} "
            f"{existing['target']}."
        )

    text = (
        f"Sire, I shall begin efforts to {description} {target_nation}. "
        f"This will cost {int(dp_cost)} DP per turn.{existing_text}"
    )

    return {
        "type": "mission",
        "target_nation": target_nation,
        "talleyrand_text": text,
        "options": [
            {
                "label": "Begin mission",
                "description": f"Start {description} {target_nation}.",
                "action": "start_mission",
                "terms": {
                    "mission_type": mission_type,
                    "target_nation": target_nation,
                },
            },
            {"label": "Not now", "description": "Cancel.", "action": "dismiss"},
        ],
        "context": {
            "dp_cost_per_turn": int(dp_cost),
        },
        "turn_created": int(world.current_turn),
        "blocking": False,
    }
