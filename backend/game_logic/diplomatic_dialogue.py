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

from backend.nation_config import (
    DEFAULT_PLAYER_NATION,
    build_enemy_nations,
    get_player_diplomat,
    get_player_nation,
)


# ═══════ NATION NAME ALIASES ═══════
NATION_ALIASES = {
    "england": "Britain",
    "uk": "Britain",
    "united kingdom": "Britain",
    "great britain": "Britain",
    "british": "Britain",
    "english": "Britain",
    "britain": "Britain",
    "the british": "Britain",
    "britian": "Britain",  # common typo
    "britiain": "Britain",  # common typo
    "prussian": "Prussia",
    "prussia": "Prussia",
    "the prussians": "Prussia",
    "prussians": "Prussia",
    "prusia": "Prussia",  # common typo
    "austrian": "Austria",
    "austria": "Austria",
    "the austrians": "Austria",
    "austrians": "Austria",
    "autria": "Austria",  # common typo
    "saxon": "Saxony",
    "saxons": "Saxony",
    "saxony": "Saxony",
    "the saxons": "Saxony",
    "france": "France",
    "french": "France",
    "the french": "France",
}

KNOWN_NATIONS = set(build_enemy_nations(DEFAULT_PLAYER_NATION))


def get_known_nations(world=None) -> set:
    """Return the set of known nations, including any vassals (R93)."""
    nations = set(KNOWN_NATIONS)
    if world:
        nations = set(getattr(world, 'enemy_nations', [])) or set(build_enemy_nations(get_player_nation(world)))
        nations.discard(get_player_nation(world))
        vassals = getattr(world, 'vassals', {})
        nations.update(vassals.keys())
    return nations

# ═══════ PROPOSAL TYPE KEYWORDS ═══════
PROPOSAL_TYPE_KEYWORDS = {
    "peace": ["peace", "ceasefire", "end the war", "stop fighting", "end hostilities",
              "sue for peace", "make peace", "peace deal", "peace offer", "settle",
              "end war", "stop the war", "peace agreement"],
    "defensive_alliance": ["defensive alliance", "defense alliance", "mutual defense",
                           "defense pact", "defensive pact", "defend each other"],
    "alliance": ["alliance", "ally", "allies", "allied", "form alliance",
                 "full alliance", "military alliance", "join forces",
                 "unite with", "unite against", "become allies"],
    "armistice": ["armistice", "truce", "temporary peace", "temporary ceasefire",
                  "pause hostilities", "halt fighting", "brief truce"],
    "open_borders": ["open borders", "free passage", "passage rights", "border access",
                     "right of passage", "cross borders", "border agreement",
                     "transit rights", "march through"],
    "non_aggression": ["non-aggression", "non aggression", "nonaggression", "pact",
                       "non aggression pact", "neutrality", "neutrality pact",
                       "mutual non-aggression", "agree not to attack"],
    "vassalage": ["vassal", "vassalage", "subjugate", "submit", "submission", "puppet",
                  "tributary", "client state", "protectorate", "subject"],
}

# Proposal type display — single source in display_names.py (R7)
from backend.display_names import (
    format_terms_for_display as _shared_format_terms_for_display,
    proposal_display_name,
)


def _display_proposal_type(proposal_type: str) -> str:
    """Convert internal proposal_type to player-facing display name."""
    return proposal_display_name(proposal_type)


# ═══════ MISSION TYPE KEYWORDS ═══════
MISSION_TYPE_KEYWORDS = {
    "IMPROVE_RELATIONS": ["improve relations", "build relations", "warm relations", "befriend",
                          "better relations", "strengthen relations", "friendly",
                          "build rapport", "diplomatic relations", "get closer to"],
    "COURT_NATION": ["court", "charm", "woo", "seduce", "win over", "sway",
                     "bring over", "convince", "persuade", "entice",
                     "lure", "attract"],
    "GATHER_INTEL": ["gather intel", "spy", "intelligence", "information",
                     "spy on", "gather information", "reconnaissance on",
                     "what are they doing", "what is happening in",
                     "investigate", "learn about"],
    "UNDERMINE_ALLIANCE": ["undermine", "sabotage", "weaken alliance", "drive a wedge",
                           "break apart", "split", "divide", "sow discord",
                           "turn against", "poison relations"],
    "REASSURE_ALLY": ["reassure", "calm", "soothe", "appease",
                      "strengthen alliance", "reaffirm", "shore up",
                      "bolster alliance", "keep them happy"],
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
    # NOTE: Uses substring matching which could theoretically false-positive
    # on words containing nation name substrings. Acceptable for current game
    # commands which are short and focused on diplomatic actions.
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
    if target_nation and target_nation not in get_known_nations(world):
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
    player_nation = get_player_nation(world)
    state = world.get_diplomatic_state(player_nation, target_nation)
    if state == "WAR":
        from backend.game_logic.diplomacy import get_war_score_for
        war_score = get_war_score_for(world, player_nation, target_nation)

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
        relation = world.nation_relations.get(world._make_diplo_key(player_nation, target_nation), 0)
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
    player_nation = get_player_nation(world)
    # Determine game bucket
    bucket = get_game_bucket(target_nation, world) if target_nation else "neutral"

    # Determine diplomatic state for template matching
    diplo_state = "WAR" if target_nation and world.get_diplomatic_state(player_nation, target_nation) == "WAR" else "PEACE"

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

    # Context-aware option descriptions for war proposals
    if target_nation and intent_type == "proposal_confirm":
        from backend.game_logic.diplomacy import get_war_score_for
        player_war_score = get_war_score_for(world, player_nation, target_nation)
        for opt in options:
            if opt["action"] == "modify_harsh" and player_war_score < -10:
                opt["description"] = "Demand more — risky given our weak position."
            elif opt["action"] == "modify_generous" and player_war_score > 20:
                opt["description"] = "Offer concessions — unnecessary given our strong position."

    # Build context snapshot
    context = {}
    if target_nation:
        from backend.game_logic.diplomacy import get_war_score_for
        diplo_key = world._make_diplo_key(player_nation, target_nation)
        context = {
            "war_score": int(get_war_score_for(world, player_nation, target_nation)),
            "relation": int(world.nation_relations.get(diplo_key, 0)),
            "threat": int(getattr(world, 'threat_level', 0)),
            "current_state": world.get_diplomatic_state(player_nation, target_nation),
        }
        # PL-3: Populate diplomat info so incoming_proposal popup shows real name
        diplomats = getattr(world, 'diplomats', {})
        diplomat = diplomats.get(target_nation)
        if diplomat:
            context["diplomat_name"] = diplomat.name
            context["diplomat_personality"] = getattr(diplomat, 'personality', 'unknown')
    if proposal_type:
        context["proposal_type"] = proposal_type

    dialogue = {
        "type": intent_type,
        "target_nation": target_nation or "",
        "talleyrand_text": talleyrand_text,
        "options": options,
        "context": context,
        "turn_created": int(world.current_turn),
        "blocking": False,
    }

    # ═══════ PROPOSAL TERMS ENRICHMENT ═══════
    # For proposal_confirm/proposal_execute, compute and attach terms summary,
    # acceptance estimate, harshness, and DP cost so the frontend popup can
    # display them to the player.
    if intent_type in ("proposal_execute", "proposal_confirm") and target_nation and proposal_type:
        dialogue = _enrich_proposal_summary(dialogue, target_nation, proposal_type, world)

    # ═══════ SESSION 6: Pre-proposal objection merge ═══════
    # When sending a proposal, evaluate Talleyrand's concern and merge
    # into the dialogue (not a separate popup per §10a).
    if intent_type in ("proposal_execute", "proposal_confirm") and target_nation:
        dialogue = _merge_pre_proposal_objection(dialogue, parsed_command, world)

    return dialogue


def _enrich_ultimatum_dialogue(dialogue: Dict, target_nation: str, world) -> Dict:
    """Add acceptance estimate and consequence preview to ultimatum dialogue (PL-14 §5).

    Separate from _enrich_proposal_summary — ultimatums have flat DP cost,
    no state transition, and always-coercive harshness.
    """
    from backend.game_logic.diplomacy import calculate_acceptance

    terms = dialogue.get("terms", {})
    demands = terms.get("demands", [])

    # Build acceptance proposal struct
    proposer = get_player_nation(world)
    proposal = {
        "type": "ultimatum_demand",
        "proposer_nation": proposer,
        "target_nation": target_nation,
        "sweeteners": [],
        "demands": demands,
        "clauses": [],
    }

    # Calculate acceptance
    try:
        result = calculate_acceptance(proposal, world)
        dialogue["acceptance_estimate"] = int(result.get("score", 0))
        dialogue["acceptance_outcome"] = result.get("outcome", "REJECT")
        # Find key obstacle for hint
        components = result.get("components", {})
        negative_components = {k: v for k, v in components.items() if isinstance(v, (int, float)) and v < 0}
        if negative_components:
            worst = min(negative_components, key=negative_components.get)
            from backend.display_names import FEEDBACK_STRINGS
            fb = FEEDBACK_STRINGS.get(worst, {})
            dialogue["acceptance_hint"] = fb.get("negative", worst.replace("_", " "))
        else:
            dialogue["acceptance_hint"] = ""
        dialogue["acceptance_components"] = components
    except Exception:
        dialogue["acceptance_estimate"] = 20
        dialogue["acceptance_outcome"] = "REJECT"
        dialogue["acceptance_hint"] = "Unable to estimate"

    # Flat DP cost (no state transition)
    dialogue["dp_cost"] = 2
    dialogue["harshness_label"] = "Coercive"

    # Format demands for display
    demand_lines = []
    for d in demands:
        dtype = d.get("type", "")
        value = d.get("value", 0)
        if dtype == "gold_per_turn":
            demand_lines.append(f"  - {int(value)} gold per turn")
        elif dtype == "gold_lump":
            demand_lines.append(f"  - {int(value)} gold (immediate)")
        elif dtype == "territory_cede":
            region_names = d.get("regions", [])
            if region_names:
                demand_lines.append(f"  - Cede {', '.join(region_names)}")
            else:
                demand_lines.append(f"  - Cede {int(value)} region(s)")
        elif dtype in ("manpower_infantry", "manpower_cavalry", "manpower_artillery"):
            unit_label = dtype.replace("manpower_", "")
            demand_lines.append(f"  - {int(value)} {unit_label}")
        elif dtype == "manpower":
            demand_lines.append(f"  - {int(value)} infantry")
    dialogue["demands_display"] = demand_lines

    # PL-19 §D: Diplomatic cost preview
    # PL-20 §E: Talleyrand territory warnings
    import math
    from backend.game_logic.diplomacy import analyze_territory_demands, DEMAND_VALUES as _DV

    t_analysis = analyze_territory_demands(demands, target_nation, world)

    # Compute preview penalty (same logic as executor Step 2)
    territory_demand_penalty = 0.0
    for r in t_analysis["demanded_regions"]:
        weight = t_analysis["region_income_weights"].get(r, 1.0)
        region_cost = -5 * weight
        if r in t_analysis["capital_regions"]:
            region_cost *= 2
        territory_demand_penalty += region_cost

    if t_analysis["is_annex"]:
        territory_demand_penalty *= 2.5
    elif t_analysis["is_rump"]:
        territory_demand_penalty *= 2.0
    elif t_analysis["demanded_count"] >= 4:
        territory_demand_penalty *= 1.5
    elif t_analysis["demanded_count"] >= 2:
        territory_demand_penalty *= 1.2

    other_demand_penalty = 0.0
    for d in demands:
        dtype = d.get("type", "")
        if dtype in ("territory_cede", "territory"):
            continue
        dvalue = d.get("value", 0)
        rate = _DV.get(dtype, 0)
        if isinstance(rate, (int, float)) and abs(rate) < 1:
            other_demand_penalty += (dvalue * rate) if dvalue is not None else 0
        else:
            other_demand_penalty += rate * dvalue if dvalue is not None else rate

    preview_penalty = max(-60, math.floor(-10 + territory_demand_penalty + other_demand_penalty))
    preview_penalty = min(preview_penalty, -10)

    dialogue["diplomatic_cost"] = int(preview_penalty)
    # Severity labels
    abs_pen = abs(preview_penalty)
    if abs_pen <= 15:
        dialogue["diplomatic_cost_label"] = "mild"
    elif abs_pen <= 25:
        dialogue["diplomatic_cost_label"] = "moderate"
    elif abs_pen <= 40:
        dialogue["diplomatic_cost_label"] = "severe"
    else:
        dialogue["diplomatic_cost_label"] = "extreme"

    # Talleyrand territory warnings
    warning = ""
    if t_analysis["is_annex"]:
        warning = (f"Sire, demanding all of {target_nation}'s territory would erase them from the map entirely. "
                   "Every nation in Europe will view this as an existential threat. "
                   "The acceptance chance is near zero, and the diplomatic cost would be catastrophic.")
    elif t_analysis["is_rump"]:
        warning = (f"Reducing {target_nation} to their capital alone would make them desperate — "
                   "and their allies furious. Expect heavy diplomatic consequences and a near-certain rejection.")
    elif t_analysis["demanded_count"] >= 4:
        warning = (f"Demanding {t_analysis['demanded_count']} regions is an extraordinary claim, Sire. "
                   "Even after a decisive victory, such vast territorial concessions are rarely accepted. "
                   "All of Europe will take notice.")
    elif t_analysis["demanded_count"] >= 2:
        warning = "A substantial territorial demand. The diplomatic cost will be significant."
    dialogue["talleyrand_territory_warning"] = warning

    return dialogue


def _enrich_proposal_summary(dialogue: Dict, target_nation: str, proposal_type: str, world) -> Dict:
    """Add proposal terms summary, acceptance estimate, harshness, and DP cost to dialogue.

    These fields let the frontend popup display the mechanical content of the
    proposal alongside Talleyrand's thematic commentary.
    """
    from backend.game_logic.diplomacy import (
        build_proposal_commitment_warnings,
        calculate_acceptance,
        get_dp_cost,
        get_transition_dp_cost,
    )
    from backend.game_logic.diplomatic_templates import generate_suggested_terms, calculate_treaty_harshness

    # Find terms from the first execute_proposal option, or generate fresh
    player_nation = get_player_nation(world)
    terms = None
    for opt in dialogue.get("options", []):
        if opt.get("action") == "execute_proposal" and opt.get("terms"):
            terms = opt["terms"]
            break
    if not terms:
        terms = generate_suggested_terms(target_nation, proposal_type, world)
        terms["proposal_type"] = proposal_type

    # PL-13-B: Always ensure both keys are present (covers dialogue option round-trip)
    if "proposal_type" not in terms:
        terms["proposal_type"] = terms.get("type", proposal_type)
    if "type" not in terms:
        terms["type"] = terms.get("proposal_type", proposal_type)

    dialogue["talleyrand_commentary"] = terms.get("talleyrand_commentary", "")

    # Build human-readable clause descriptions
    dialogue["proposal_terms_summary"] = _format_terms_for_display(terms, proposal_type, target_nation)

    # Harshness — normalize string clauses to dicts for calculate_treaty_harshness
    harshness_terms = dict(terms)
    harshness_terms["clauses"] = [
        c if isinstance(c, dict) else {"type": c}
        for c in terms.get("clauses", [])
    ]
    harshness = calculate_treaty_harshness(harshness_terms)
    dialogue["harshness"] = round(harshness, 2)
    if harshness < 0.15:
        dialogue["harshness_label"] = "Low"
    elif harshness < 0.35:
        dialogue["harshness_label"] = "Moderate"
    elif harshness < 0.6:
        dialogue["harshness_label"] = "High"
    else:
        dialogue["harshness_label"] = "Very High"

    # Acceptance estimate
    proposal_for_calc = {
        "type": terms.get("type", proposal_type),
        "proposer_nation": player_nation,
        "target_nation": target_nation,
        "sweeteners": terms.get("sweeteners", []),
        "demands": terms.get("demands", []),
        "clauses": terms.get("clauses", []),
    }
    try:
        result = calculate_acceptance(proposal_for_calc, world)
        score = int(result["score"])
        dialogue["acceptance_estimate"] = max(0, min(100, score))
        dialogue["acceptance_outcome"] = result.get("outcome", "Unknown")

        # Extract key obstacle from components for player hint
        from backend.display_names import FEEDBACK_STRINGS
        components = result.get("components", {})
        worst_key, worst_val = "", 0
        for comp_key, comp_val in components.items():
            if comp_val < worst_val:
                worst_key = comp_key
                worst_val = comp_val
        if worst_key:
            hint_phrase = FEEDBACK_STRINGS.get(worst_key, {}).get("negative", "")
            if hint_phrase:
                dialogue["acceptance_hint"] = f"Key obstacle: {hint_phrase}"
            else:
                dialogue["acceptance_hint"] = ""
        else:
            dialogue["acceptance_hint"] = ""

        # PL-9 Part A: Warn player when acceptance is borderline (50-75%)
        if 50 <= score <= 75:
            dialogue["acceptance_warning"] = (
                "This estimate reflects current conditions, Sire. Much may change "
                "during my journey — a battle lost, a relation soured. I would counsel "
                "a wider margin if you wish certainty."
            )
        else:
            dialogue["acceptance_warning"] = ""
    except Exception:
        dialogue["acceptance_estimate"] = -1
        dialogue["acceptance_outcome"] = "Unable to estimate"
        dialogue["acceptance_hint"] = ""
        dialogue["acceptance_warning"] = ""

    # DP cost
    _state_map = {
        "peace": "PEACE", "alliance": "ALLIANCE", "defensive_alliance": "DEFENSIVE_ALLIANCE",
        "non_aggression": "NON_AGGRESSION", "open_borders": "OPEN_BORDERS", "armistice": "ARMISTICE",
        "vassalage": "VASSAL",
    }
    current_diplo = world.get_diplomatic_state(get_player_nation(world), target_nation)
    target_diplo = _state_map.get(proposal_type, "PEACE")
    jump_cost = get_transition_dp_cost(current_diplo, target_diplo)
    dp_action = f"propose_{proposal_type}"
    talleyrand = get_player_diplomat(world)
    skill = talleyrand.skill if talleyrand else 5
    dialogue["dp_cost"] = int(get_dp_cost(dp_action, skill, transition_base=jump_cost))

    # Display name
    dialogue["proposal_type_display"] = _display_proposal_type(proposal_type)
    dialogue["speaker_attribution"] = "talleyrand"

    warnings = build_proposal_commitment_warnings(
        world,
        proposer_nation=player_nation,
        target_nation=target_nation,
        proposal_type=proposal_type,
    )
    if warnings:
        dialogue["warnings"] = warnings

    return dialogue


def _format_terms_for_display(terms: Dict, proposal_type: str, target_nation: str) -> list:
    """Convert a terms dict into a list of human-readable clause strings."""
    lines = _shared_format_terms_for_display(terms, proposal_type, target_nation)

    # If no extra terms beyond the base
    if len(lines) == 1 and proposal_type in ("non_aggression", "open_borders"):
        lines.append("No additional terms")

    return lines


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
    talleyrand = get_player_diplomat(world)
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
        target_nation_obj = parsed_command.get("target_nation", "")
        proposal_type_obj = parsed_command.get("proposal_type", "peace")
        proposal_summary = f"{proposal.get('type', 'unknown')} with {proposal.get('target_nation', 'unknown')}"

        # Enrich with proposal terms so objection popup can display them
        terms_for_display = []
        acceptance_estimate = -1
        acceptance_outcome = ""
        for opt in dialogue.get("options", []):
            if opt.get("action") == "execute_proposal" and opt.get("terms"):
                terms_for_display = _format_terms_for_display(
                    opt["terms"], proposal_type_obj, target_nation_obj)
                break
        if target_nation_obj:
            from backend.game_logic.diplomacy import calculate_acceptance
            from backend.game_logic.diplomatic_templates import generate_suggested_terms as _gen_terms
            player_nation = get_player_nation(world)
            calc_terms = None
            for opt in dialogue.get("options", []):
                if opt.get("action") == "execute_proposal" and opt.get("terms"):
                    calc_terms = opt["terms"]
                    break
            if not calc_terms:
                calc_terms = _gen_terms(target_nation_obj, proposal_type_obj, world)
            calc_proposal = {
                "type": proposal_type_obj,
                "proposer_nation": player_nation,
                "target_nation": target_nation_obj,
                "sweeteners": calc_terms.get("sweeteners", []),
                "demands": calc_terms.get("demands", []),
                "clauses": calc_terms.get("clauses", []),
            }
            try:
                acc_result = calculate_acceptance(calc_proposal, world)
                acceptance_estimate = int(acc_result["score"])
                acceptance_estimate = max(0, min(100, acceptance_estimate))
                acceptance_outcome = acc_result.get("outcome", "Unknown")
            except Exception:
                acceptance_estimate = -1
                acceptance_outcome = "Unable to estimate"

        world.diplomatic_objection_popup = {
            "concern_level": concern_label,
            "objection_text": objection_text,
            "defiance_risk": defiance_risk,
            "proposal_summary": proposal_summary,
            "proposal_terms": terms_for_display,
            "acceptance_estimate": int(acceptance_estimate),
            "acceptance_outcome": acceptance_outcome,
            "target_nation": target_nation_obj,
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
    from backend.game_logic.diplomacy import calculate_acceptance, get_dp_cost, get_war_score_for

    target_nation = parsed_command.get("target_nation")
    proposal_type = parsed_command.get("proposal_type", "peace")
    player_nation = get_player_nation(world)

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
        "proposer_nation": player_nation,
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
    current_state = world.get_diplomatic_state(player_nation, target_nation)
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
            "war_score": int(get_war_score_for(world, player_nation, target_nation)),
            "relation": int(world.nation_relations.get(world._make_diplo_key(player_nation, target_nation), 0)),
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

    # DLF-2: UNDERMINE_ALLIANCE requires ally selection
    if mission_type == "UNDERMINE_ALLIANCE":
        active_nations = world.get_active_nations()
        allies = [
            n for n in active_nations
            if n != target_nation and world.are_allies(target_nation, n)
        ]
        if not allies:
            return {
                "type": "mission",
                "target_nation": target_nation,
                "talleyrand_text": f"Sire, {target_nation} has no alliances to undermine.",
                "options": [
                    {"label": "Dismiss", "description": "Never mind.", "action": "dismiss"},
                ],
                "context": {},
                "turn_created": int(world.current_turn),
                "blocking": False,
            }
        if len(allies) == 1:
            # Auto-select sole ally
            ally = allies[0]
            text = (
                f"Sire, I shall work to undermine the alliance between "
                f"{target_nation} and {ally}. "
                f"This will cost {int(dp_cost)} DP per turn.{existing_text}"
            )
            return {
                "type": "mission",
                "target_nation": target_nation,
                "talleyrand_text": text,
                "options": [
                    {
                        "label": "Begin mission",
                        "description": f"Undermine {target_nation}-{ally} alliance.",
                        "action": "start_mission",
                        "terms": {
                            "mission_type": mission_type,
                            "target_nation": target_nation,
                            "target_ally": ally,
                        },
                    },
                    {"label": "Not now", "description": "Cancel.", "action": "dismiss"},
                ],
                "context": {"dp_cost_per_turn": int(dp_cost), "target_ally": ally},
                "turn_created": int(world.current_turn),
                "blocking": False,
            }
        # Multiple allies — present selection
        text = (
            f"Sire, {target_nation} has multiple alliances. "
            f"Which alliance shall I undermine? ({int(dp_cost)} DP/turn){existing_text}"
        )
        options = [
            {
                "label": f"{ally}",
                "description": f"Undermine {target_nation}-{ally} alliance.",
                "action": "start_mission",
                "terms": {
                    "mission_type": mission_type,
                    "target_nation": target_nation,
                    "target_ally": ally,
                },
            }
            for ally in allies
        ]
        options.append({"label": "Not now", "description": "Cancel.", "action": "dismiss"})
        return {
            "type": "mission",
            "target_nation": target_nation,
            "talleyrand_text": text,
            "options": options,
            "context": {"dp_cost_per_turn": int(dp_cost)},
            "turn_created": int(world.current_turn),
            "blocking": False,
        }

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
