"""Single source of truth for all internal→display name translations.

All display maps live here.  Backend modules import from here.
Never return raw internal names to the frontend.

R7 — Architecture Refactoring Session 6.
"""

# ============================================================================
# ACTION DISPLAY — player-facing verb form (3rd person present)
# Source: executor.py _ACTION_DISPLAY_NAMES
# ============================================================================

ACTION_DISPLAY = {
    "attack": "attacks",
    "move": "moves to",
    "defend": "defends",
    "fortify": "fortifies",
    "unfortify": "abandons fortification",
    "form_square": "forms square",
    "break_square": "breaks square",
    "drill": "drills",
    "stance_change": "changes stance",
    "retreat": "retreats to",
    "wait": "holds position",
    "recruit": "recruits",
    "scout": "scouts",
    "hold": "holds",
    "build": "builds",
    "repair": "repairs",
    "garrison": "garrisons",
    "bombardment": "bombards",
}

# ============================================================================
# OBJECTION DISPLAY — gerund form for objection context
# Source: campaign_log.py _OBJECTION_DISPLAY
# ============================================================================

OBJECTION_DISPLAY = {
    "attack": "attacking",
    "move": "moving",
    "defend": "defending",
    "fortify": "fortifying",
    "unfortify": "abandoning fortification",
    "form_square": "forming square",
    "break_square": "breaking square",
    "drill": "drilling",
    "stance_change": "changing stance",
    "retreat": "retreating",
    "wait": "waiting",
    "recruit": "recruiting",
    "scout": "scouting",
    "hold": "holding",
    "build": "building",
    "repair": "repairing",
    "garrison": "garrisoning",
    "bombardment": "bombarding",
}

# ============================================================================
# DEFIANCE DISPLAY — past tense for defiance context
# Source: campaign_log.py _DEFIANCE_DISPLAY
# ============================================================================

DEFIANCE_DISPLAY = {
    "attack": "attacked",
    "move": "moved",
    "defend": "defended",
    "fortify": "fortified",
    "unfortify": "abandoned fortification",
    "form_square": "formed square",
    "break_square": "broke square",
    "drill": "drilled",
    "stance_change": "changed stance",
    "retreat": "retreated",
    "wait": "waited",
    "recruit": "recruited",
    "scout": "scouted",
    "hold": "held position",
    "build": "built",
    "repair": "repaired",
    "garrison": "garrisoned",
    "bombardment": "bombarded",
}

# ============================================================================
# PROPOSAL TYPE DISPLAY — treaty/proposal type labels
# Source: diplomatic_dialogue.py PROPOSAL_TYPE_DISPLAY
# ============================================================================

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

# ============================================================================
# DIPLOMATIC STATE DISPLAY — title case for UI labels
# Source: diplomacy.py _STATE_DISPLAY_NAMES
# ============================================================================

STATE_DISPLAY = {
    "WAR": "At War",
    "ARMISTICE": "Armistice",
    "PEACE": "Peace",
    "OPEN_BORDERS": "Open Borders",
    "NON_AGGRESSION": "Non-Aggression",
    "DEFENSIVE_ALLIANCE": "Defensive Alliance",
    "ALLIANCE": "Alliance",
    "VASSAL": "Vassal",
}

# ============================================================================
# DIPLOMATIC STATE NARRATIVE — lowercase narrative form (Talleyrand's voice)
# Source: diplomatic_advisory.py _STATE_DISPLAY
# ============================================================================

STATE_NARRATIVE_DISPLAY = {
    "WAR": "at war",
    "ARMISTICE": "under armistice",
    "PEACE": "at peace",
    "OPEN_BORDERS": "sharing open borders",
    "NON_AGGRESSION": "bound by non-aggression",
    "DEFENSIVE_ALLIANCE": "in defensive alliance",
    "ALLIANCE": "allied",
    "VASSAL": "our vassal",
}

# ============================================================================
# FEEDBACK STRINGS — acceptance formula factor explanations
# Source: diplomacy.py FEEDBACK_STRINGS
# ============================================================================

FEEDBACK_STRINGS = {
    "relation_modifier": {
        "negative": "deep-seated hostility",
        "positive": "goodwill between our nations",
    },
    "threat_modifier": {
        "negative": "fear of French expansion",
        "positive": "France's measured approach",
    },
    "war_score_modifier": {
        "negative": "our military position is weak",
        "positive": "our military dominance",
    },
    "deal_balance": {
        "negative": "insufficient concessions",
        "positive": "generous terms",
    },
    "personality_modifier": {
        "negative": "personal opposition from their diplomat",
        "positive": "diplomatic rapport",
    },
    "diplomat_skill_bonus": {
        "negative": "their diplomat outmaneuvered us",
        "positive": "Talleyrand's superior skill",
    },
    "base_disposition": {
        "negative": "fundamental resistance to this type of agreement",
        "positive": "natural willingness to negotiate",
    },
    "special_desire_bonus": {
        "negative": "their specific strategic interests were not addressed",
        "positive": "we addressed their core strategic interest",
    },
    "coalition_penalty": {
        "negative": "coalition loyalty binds them against us",
        "positive": "coalition obligations have weakened",
    },
    "harshness_bonus": {
        "negative": "memory of past harsh treaties",
        "positive": "prior harsh terms make them more pliable",
    },
    "reliability_modifier": {
        "negative": "France's reputation for breaking agreements",
        "positive": "France's record of honoring treaties",
    },
    "war_weariness": {
        "negative": "the war has dragged on too long",
        "positive": "exhaustion from prolonged conflict",
    },
    "stalemate_duration": {
        "negative": "the deadlock shows no sign of breaking",
        "positive": "neither side can gain the upper hand",
    },
    "military_supremacy": {
        "negative": "their overwhelming military advantage",
        "positive": "our decisive military superiority",
    },
    "battlefield_diplomacy": {
        "negative": "recent battlefield setbacks",
        "positive": "our recent victories on the battlefield",
    },
    "military_pressure": {
        "negative": "the military balance favors them",
        "positive": "our military pressure on their borders",
    },
}

# ============================================================================
# NEW MAPS — previously missing, now centralized
# ============================================================================

DEFIANCE_OUTCOME_DISPLAY = {
    "failed_roll": "Failed",
    "right": "Vindicated",
    "wrong": "Misguided",
    "spectacular": "Spectacular Success",
    "disaster": "Disaster",
    "inconclusive": "Inconclusive",
}

PERSONALITY_DISPLAY = {
    "aggressive": "Aggressive",
    "cautious": "Cautious",
    "literal": "Literal",
    "balanced": "Balanced",
    "loyal": "Loyal",
}

STANCE_DISPLAY = {
    "neutral": "Neutral",
    "defensive": "Defensive",
    "aggressive": "Aggressive",
}

CONCERN_LEVEL_DISPLAY = {
    "NONE": "None",
    "MILD": "Mild",
    "MODERATE": "Moderate",
    "STRONG": "Strong",
    "EXTREME": "Extreme",
}

TRUST_TIER_DISPLAY = {
    "HOSTILE": "Hostile",
    "WARY": "Wary",
    "TRUSTING": "Trusting",
    "DEVOTED": "Devoted",
}


# ============================================================================
# UNIVERSAL TRANSLATOR
# ============================================================================

_CATEGORY_MAPS = {
    "action": ACTION_DISPLAY,
    "objection": OBJECTION_DISPLAY,
    "defiance": DEFIANCE_DISPLAY,
    "proposal": PROPOSAL_TYPE_DISPLAY,
    "state": STATE_DISPLAY,
    "state_narrative": STATE_NARRATIVE_DISPLAY,
    "defiance_outcome": DEFIANCE_OUTCOME_DISPLAY,
    "personality": PERSONALITY_DISPLAY,
    "stance": STANCE_DISPLAY,
    "concern": CONCERN_LEVEL_DISPLAY,
    "trust_tier": TRUST_TIER_DISPLAY,
}


def display(category: str, internal_name: str, fallback: str = None) -> str:
    """Universal translator.  Never returns raw internal name.

    If internal_name not found in the map, returns fallback or
    auto-formatted version (Title Case with underscores removed).
    """
    display_map = _CATEGORY_MAPS.get(category, {})
    result = display_map.get(internal_name)
    if result:
        return result
    if fallback:
        return fallback
    return internal_name.replace("_", " ").title()
