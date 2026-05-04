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
    "charge": "charges",           # R18: cavalry charge
    "restrain": "restrains",       # R18: restrain reckless cavalry
    "cancel": "cancels order",     # R18: cancel strategic order
    "economy": "reviews finances", # R18: economy info command
    "diplomatic_ultimatum": "delivers ultimatum to",  # PL-14
    "make_amends": "offers amends to",                # B-B7 (spec §8.6.1)
    "set_war_purpose": "sets war purpose against",    # WPS-A
    "repudiate_bargain": "repudiates bargain with",  # WB-C
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
    "charge": "charging",           # R18
    "restrain": "restraining",      # R18
    "cancel": "cancelling order",   # R18
    "economy": "reviewing finances",# R18
    "diplomatic_ultimatum": "issuing ultimatum",  # PL-14
    "make_amends": "offering amends",              # B-B7 (no marshal objections in v0.1)
    "set_war_purpose": "setting war purpose",      # WPS-A
    "repudiate_bargain": "repudiating bargain",   # WB-C
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
    "charge": "charged",             # R18
    "restrain": "restrained",        # R18
    "cancel": "cancelled order",     # R18
    "economy": "reviewed finances",  # R18
    "diplomatic_ultimatum": "issued ultimatum",  # PL-14
    "make_amends": "offered amends",             # B-B7 (no marshal defiance in v0.1)
    "set_war_purpose": "set war purpose",         # WPS-A
    "repudiate_bargain": "repudiated bargain",   # WB-C
}

# ============================================================================
# STRATEGIC ORDER DISPLAY — player-facing names for strategic order types
# Source: ledger.py _ORDER_DISPLAY_NAMES (R15 centralization)
# ============================================================================

STRATEGIC_ORDER_DISPLAY = {
    "MOVE_TO": "March",
    "PURSUE": "Pursue",
    "HOLD": "Hold",
    "SUPPORT": "Support",
}


def get_strategic_display(order_type: str) -> str:
    """Return player-facing name for a strategic order type."""
    return STRATEGIC_ORDER_DISPLAY.get(order_type, order_type.replace("_", " ").title())


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
    "harsh_peace": "Harsh Peace Treaty",  # R18: AI-generated harsh peace proposals
    "ultimatum_demand": "Ultimatum",  # PL-14
}

CLAUSE_TYPE_DISPLAY = {
    "gold_lump": "Gold payment",
    "gold_per_turn": "Gold per turn",
    "territory_cede": "Territory cession",
    "territory_return": "Territory return",
    "territory": "Territory cession",
    "action_point": "Action point concession",
    "ap_per_turn": "Action point concession",
    "ap_reduction": "Action point reduction",
    "unit_trade": "Military units",
    "open_borders": "Open borders",
    "protection": "Protection guarantee",
    "protection_promised": "Protection guarantee",
    "continental_system_lifted": "Continental System lifted",
    "manpower_infantry": "Infantry manpower",
    "infantry_manpower": "Infantry manpower",
    "manpower_cavalry": "Cavalry reserves",
    "cavalry_manpower": "Cavalry reserves",
    "manpower_artillery": "Artillery reserves",
    "artillery_manpower": "Artillery reserves",
    "war_bargain": "War bargain",
}

PROPOSAL_TYPE_SUMMARY_DISPLAY = {
    "armistice": "Armistice (cease hostilities temporarily)",
    "armistice_losing": "Armistice (cease hostilities temporarily)",
    "armistice_stalemate": "Armistice (cease hostilities temporarily)",
    "armistice_winning": "Armistice (cease hostilities temporarily)",
    "peace": "Peace Treaty (end state of war)",
    "non_aggression": "Non-Aggression Pact (agree not to attack)",
    "open_borders": "Open Borders Agreement (free military passage)",
    "alliance": "Full Alliance (mutual military cooperation)",
    "defensive_alliance": "Defensive Alliance (mutual defense pact)",
    "ultimatum_demand": "Ultimatum",
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
    "hegemony_target_mod": {
        "negative": "the weight of the bloc pressing against them",
        "positive": "balance of power across Europe",
    },
    "bilateral_betrayal_mod": {
        "negative": "their memory of our broken commitments",
        "positive": "a clean bilateral slate with them",
    },
    "grievance_modifier": {
        # B-B4 §8.8.9 + §9.3. Grievance flags land on defensive-call
        # refusals and persist until repaired via Make Amends (grievance
        # variant). "Abandoned alliance" is the player-facing phrase used
        # consistently across spec + parser disambiguation + ledger row.
        "negative": "their grievance over abandoned alliances",
        "positive": "no grievance over abandoned alliances",
    },
    "bargain_value_mod": {
        "negative": "no war bargain offered",
        "positive": "a war bargain sweetens the deal",
    },
    # WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC §14.3 (D1) — gratitude
    # acceptance bonus from a recently rewarded ally.
    "settlement_gratitude_mod": {
        "negative": "no recent settlement reward from us",
        "positive": "the recent settlement reward they remember",
    },
    "bargain_conflict_penalty": {
        "negative": "existing bargain conflicts with this nation",
        "positive": "no bargain conflicts",
    },
    # B-B4 §9.3 composite-floor debug metadata. These entries exist so the
    # component-key completeness test stays green; `_generate_feedback`
    # does NOT list them in `trackable`, so they never drive player-facing
    # hint text. Copy is neutral because the fields describe the floor's
    # state, not a political pressure the diplomat would voice.
    "grievance_flag_count_raw": {
        "negative": "raw count of outstanding grievances",
        "positive": "no outstanding grievances",
    },
    "composite_floor": {
        "negative": "the political-pressure floor held at -60",
        "positive": "no composite floor was reached",
    },
    "composite_floor_applied": {
        "negative": "the composite floor clamped the political subtotal",
        "positive": "the composite floor was not engaged",
    },
    "composite_floor_adjustment": {
        # `composite_floor_adjustment` is the non-negative amount the
        # floor *added* to lift the raw subtotal back to -60; it is
        # never negative by construction. The `negative` key is the
        # "floor engaged" copy (adjustment > 0) and `positive` is the
        # "floor dormant" copy (adjustment == 0).
        "negative": "the composite floor lifted the political subtotal back to -60",
        "positive": "no floor adjustment was required",
    },
    # B-B4 §8.8.7 — anti-renewal cooldown gate copy. The block is a
    # mechanical score clamp (parallel to `hard_reject_posture`); none
    # of these rows are in `_generate_feedback` trackable so they never
    # drive player-facing hint text. They exist so the component-key
    # completeness test stays green and the ledger can render "deep
    # treaties blocked: N turns remaining" distinctly.
    "anti_renewal_block": {
        "negative": "the anti-renewal cooldown blocked the deep-treaty proposal",
        "positive": "no anti-renewal cooldown is active",
    },
    "anti_renewal_active": {
        "negative": "an anti-renewal cooldown is active on this pair",
        "positive": "no anti-renewal cooldown is active on this pair",
    },
    "anti_renewal_turns_remaining": {
        "negative": "turns remaining on the anti-renewal cooldown",
        "positive": "no anti-renewal cooldown is pending",
    },
    "oathbreaker_posture": {
        "negative": "the court's oathbreaker posture blocks new deep treaties",
        "positive": "no oathbreaker posture blocks the proposal",
    },
    "oathbreaker_active": {
        "negative": "oathbreaker posture is active",
        "positive": "no oathbreaker posture is active",
    },
    "oathbreaker_turns_remaining": {
        "negative": "turns remaining on the oathbreaker auto-reject window",
        "positive": "no oathbreaker auto-reject window remains",
    },
    "harshness_penalty": {
        "negative": "the harshness of current demands",
        "positive": "our reasonable terms",
    },
    "harshness_bonus": {
        "negative": "prior harsh treaties breed resentment",
        "positive": "no history of harsh terms",
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
    "ultimatum_bonus": {
        "positive": "military threat backs demands",
        "negative": "lack of military presence near target",
    },
    "territory_escalation": {
        "negative": "the sheer scale of territorial demands",
        "positive": "modest territorial terms",
    },
    "hard_reject_posture": {
        "negative": "their remembered betrayals of France",
        "positive": "the chancery remains open to deeper commitments",
    },
}

# ============================================================================
# AMENDS REFUSAL DISPLAY — Talleyrand-voiced advisory lines per refusal cause
# Source: RELIABILITY_COMMITMENTS_SPEC §8.6.1 (B-B7 Make Amends standard variant)
# Refusal codes are stable strings the executor returns; templates expose
# `{nation}` (target court), `{turns_remaining}` (cooldown countdown), and
# `{required}` / `{available}` (resource shortfall) where relevant.
# ============================================================================

AMENDS_REFUSAL_DISPLAY = {
    "no_active_strikes": (
        "There is nothing to repair with {nation}, Sire. "
        "They hold no living grievance against France."
    ),
    "cooldown_active": (
        "We offered amends to {nation} only {turns_since} turns ago. "
        "Too soon would read as petition, not as state."
    ),
    "war_or_armistice": (
        "Amends before peace read as ransom, Sire. "
        "Restore the treaty with {nation} first."
    ),
    "insufficient_gold": (
        "Insufficient treasury, Sire. Reparations to {nation} require "
        "{required} gold, but we have only {available}."
    ),
    "insufficient_dp": (
        "Insufficient Diplomatic Points, Sire. Reparations to {nation} require "
        "{required} DP, but we have only {available}."
    ),
    # B-B4 §8.6.1a — grievance-variant refusal for the "no abandoned
    # alliance to repair" case. Talleyrand voice per spec excerpt: "There
    # is no abandoned alliance to repair, Sire — {nation} holds no living
    # grievance of that kind against France."
    "no_active_grievance": (
        "There is no abandoned alliance to repair, Sire — "
        "{nation} holds no living grievance of that kind against France."
    ),
}

# ============================================================================
# END_REASON_FAMILY_DISPLAY — ledger / dispatch labels per §9.9 fault family.
# Source: RELIABILITY_COMMITMENTS_SPEC §9.9 + §8.8.7a (defensive refusal
# termination). Keys match the `END_REASON_FAMILY_*` constants in
# `backend.game_logic.diplomacy` so presentation never emits raw enum
# strings per the R7 display-map contract.
# ============================================================================

END_REASON_FAMILY_DISPLAY = {
    "french_breach": "Broken by France",
    "counterparty_reversal": "Broken by the counterparty",
    "obsolescence_or_external": "Forced by cascade or external event",
    # B-B4 §8.8.7a — refusal-as-repudiation. Kept distinct from
    # `french_breach` so the ledger can tell "France broke the alliance"
    # from "France refused the defensive call and thereby ended the
    # alliance."
    "defensive_refusal_termination": "Ended by refusal of the defensive call",
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

TRUST_TIER_DISPLAY = {
    "HOSTILE": "Hostile",
    "WARY": "Wary",
    "TRUSTING": "Trusting",
    "DEVOTED": "Devoted",
}

DECISION_REASON_DISPLAY = {
    "claim_obsolete": "claim obsolete",
    "claim_trade": "claim trade",
    "anti_renewal_active": "anti-renewal cooldown",
    "coalition_conflict": "coalition conflict",
    "concern_pressure": "hegemony pressure",
    "counterparty_reversal": "counterparty reversal",
    "distrust_promiser": "remembered betrayals",
    "hegemony_pressure": "hegemony pressure",
    "rival_pressure": "hegemony pressure",
    "route_blocked": "route blocked",
    "shared_enemy_survival": "shared-enemy survival",
    "unknown_baseline": "unknown baseline",
    "war_overload": "war exhaustion",
    "anti_spam": "existing bargain",
    "cooldown_active": "bargain cooldown",
    "hard_blocked": "hard block",
    "no_feasible_target": "no feasible target",
    "no_valid_region": "no valid claim region",
    "participation_blocked": "participation blocked",
    "strength_insufficient": "insufficient strength",
}


# ============================================================================
# UNIVERSAL TRANSLATOR
# ============================================================================

_CATEGORY_MAPS = {
    "action": ACTION_DISPLAY,
    "objection": OBJECTION_DISPLAY,
    "defiance": DEFIANCE_DISPLAY,
    "proposal": PROPOSAL_TYPE_DISPLAY,
    "clause": CLAUSE_TYPE_DISPLAY,
    "state": STATE_DISPLAY,
    "state_narrative": STATE_NARRATIVE_DISPLAY,
    "defiance_outcome": DEFIANCE_OUTCOME_DISPLAY,
    "personality": PERSONALITY_DISPLAY,
    "stance": STANCE_DISPLAY,
    "trust_tier": TRUST_TIER_DISPLAY,
}


def action_display_name(action: str) -> str:
    """Translate internal action name to player-readable text."""
    return ACTION_DISPLAY.get(action, action.replace("_", " "))


def diplomatic_decision_reason_display(reason: str) -> str:
    """Translate a deterministic decision_reason enum to player-facing text."""
    result, raw = _lookup_display_name(DECISION_REASON_DISPLAY, reason)
    return result or _fallback_display_name(raw, default="")


def _lookup_display_name(display_map: dict, internal_name: str):
    raw = "" if internal_name is None else str(internal_name).strip()
    if not raw:
        return None, raw
    if raw in display_map:
        return display_map[raw], raw
    lowered = raw.lower()
    if lowered in display_map:
        return display_map[lowered], raw
    uppered = raw.upper()
    if uppered in display_map:
        return display_map[uppered], raw
    return None, raw


def _fallback_display_name(raw: str, default: str = "Unknown") -> str:
    if not raw:
        return default
    return raw.replace("_", " ").title()


def proposal_display_name(proposal_type: str) -> str:
    """Translate internal proposal_type to player-readable text."""
    result, raw = _lookup_display_name(PROPOSAL_TYPE_DISPLAY, proposal_type)
    return result or _fallback_display_name(raw, default="Unknown Proposal")


def clause_display_name(clause_type: str) -> str:
    """Translate an internal clause or treaty token to player-readable text."""
    result, raw = _lookup_display_name(CLAUSE_TYPE_DISPLAY, clause_type)
    return result or _fallback_display_name(raw, default="Unknown Clause")


def proposal_summary_display_name(proposal_type: str, target_nation: str = "") -> str:
    """Return the rich summary line used in diplomacy dialogue previews."""
    result, raw = _lookup_display_name(PROPOSAL_TYPE_SUMMARY_DISPLAY, proposal_type)
    if result:
        return result
    proposal_label = proposal_display_name(raw)
    if (raw or "").strip().lower() == "vassalage" and target_nation:
        return f"{proposal_label} ({target_nation} becomes a subject state)"
    return proposal_label


def decision_reason_display_name(reason: str) -> str:
    """Backward-compatible alias for decision-reason copy."""
    return diplomatic_decision_reason_display(reason)


def _format_display_value(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return str(value)
    if isinstance(value, int):
        return str(value)
    return str(value).strip()


def _format_clause_detail(clause) -> str:
    if not isinstance(clause, dict):
        return ""
    regions = clause.get("regions", [])
    if isinstance(regions, list) and regions:
        return ", ".join(str(region) for region in regions)
    if "value" in clause:
        return _format_display_value(clause.get("value"))
    if "amount" in clause:
        return _format_display_value(clause.get("amount"))
    if clause.get("type") == "war_bargain":
        named_enemy = clause.get("named_enemy", "")
        claim_region = clause.get("claim_region", "")
        parts = []
        if named_enemy:
            parts.append(f"against {named_enemy}")
        if claim_region:
            parts.append(f"claim on {claim_region}")
        return ", ".join(parts)
    return ""


def _format_popup_clause_line(prefix: str, clause_type: str, clause) -> str:
    label = clause_display_name(clause_type)
    detail = _format_clause_detail(clause)
    if detail:
        return f"{prefix}: {label} - {detail}"
    return f"{prefix}: {label}"


def build_proposal_popup_clauses(terms: dict, *, include_base: bool = True) -> list[str]:
    """Build incoming proposal popup clause strings from backend-owned labels."""
    clauses = []
    proposal_type = terms.get("type") or terms.get("proposal_type") or "unknown"
    if include_base:
        clauses.append(f"Proposal: {proposal_display_name(proposal_type)}")

    for clause in terms.get("clauses", []):
        clause_type = clause.get("type", "unknown") if isinstance(clause, dict) else clause
        clauses.append(_format_popup_clause_line("Clause", clause_type, clause))

    for demand in terms.get("demands", []):
        clauses.append(_format_popup_clause_line("Demand", demand.get("type", "unknown"), demand))

    for sweetener in terms.get("sweeteners", []):
        clauses.append(_format_popup_clause_line("Offer", sweetener.get("type", "unknown"), sweetener))

    if not clauses:
        return ["Diplomatic proposal"]
    return clauses


def format_terms_for_display(terms: dict, proposal_type: str, target_nation: str) -> list[str]:
    """Convert a proposal terms dict into player-facing summary lines."""
    lines = []
    target_label = target_nation or terms.get("target_nation") or "Target nation"
    proposal_key = terms.get("type") or proposal_type
    lines.append(proposal_summary_display_name(proposal_key, target_label))

    for clause in terms.get("clauses", []):
        clause_type = clause.get("type", "unknown") if isinstance(clause, dict) else clause
        if str(clause_type).strip().lower() == "open_borders":
            lines.append("Open borders included")
            continue
        detail = _format_clause_detail(clause)
        clause_label = clause_display_name(clause_type)
        if detail:
            lines.append(f"{clause_label} ({detail})")
        else:
            lines.append(clause_label)

    for demand in terms.get("demands", []):
        demand_type = str(demand.get("type", "")).strip().lower()
        value = demand.get("value", 0)
        if demand_type == "gold_per_turn":
            lines.append(f"{target_label} pays {int(value)} gold/turn")
        elif demand_type in ("territory_cede", "territory"):
            regions = demand.get("regions", [])
            lines.append(f"{target_label} cedes {', '.join(regions) if regions else 'territory'}")
        elif demand_type in ("infantry_manpower", "manpower_infantry"):
            lines.append(f"{target_label} provides {int(value)} infantry manpower")
        elif demand_type in ("cavalry_manpower", "manpower_cavalry"):
            lines.append(f"{target_label} provides {int(value)} cavalry reserves")
        elif demand_type in ("artillery_manpower", "manpower_artillery"):
            lines.append(f"{target_label} provides {int(value)} artillery reserves")
        elif demand_type == "gold_lump":
            lines.append(f"{target_label} pays {int(value)} gold")
        elif demand_type == "ap_per_turn":
            lines.append(f"{target_label} loses {int(value)} AP/turn")
        else:
            detail = _format_clause_detail(demand)
            detail_suffix = f" ({detail})" if detail else ""
            lines.append(f"Demand: {clause_display_name(demand_type)}{detail_suffix}")

    for sweetener in terms.get("sweeteners", []):
        sweetener_type = str(sweetener.get("type", "")).strip().lower()
        value = sweetener.get("value", 0)
        if sweetener_type == "gold_per_turn":
            lines.append(f"France offers {int(value)} gold/turn")
        elif sweetener_type == "gold_lump":
            lines.append(f"France offers {int(value)} gold (lump sum)")
        elif sweetener_type in ("territory_cede", "territory"):
            regions = sweetener.get("regions", [])
            lines.append(f"France cedes {', '.join(regions) if regions else 'territory'}")
        elif sweetener_type in ("infantry_manpower", "manpower_infantry"):
            lines.append(f"France provides {int(value)} infantry manpower")
        elif sweetener_type in ("cavalry_manpower", "manpower_cavalry"):
            lines.append(f"France provides {int(value)} cavalry reserves")
        elif sweetener_type in ("artillery_manpower", "manpower_artillery"):
            lines.append(f"France provides {int(value)} artillery reserves")
        elif sweetener_type == "ap_per_turn":
            lines.append(f"France concedes {int(value)} AP/turn")
        else:
            detail = _format_clause_detail(sweetener)
            detail_suffix = f" ({detail})" if detail else ""
            lines.append(f"Offer: {clause_display_name(sweetener_type)}{detail_suffix}")

    return lines


def format_proposal_summary(terms: dict) -> str:
    """Create a human-readable multi-line summary of proposal terms."""
    parts = []
    proposal_type = terms.get("type", "unknown")
    proposer = terms.get("proposer_nation", "Unknown")
    target = terms.get("target_nation", "France")
    parts.append(f"{proposal_display_name(proposal_type)} between {proposer} and {target}")

    for sweetener in terms.get("sweeteners", []):
        sweetener_type = str(sweetener.get("type", "")).strip().lower()
        value = sweetener.get("value", 0)
        if sweetener_type == "gold_per_turn":
            parts.append(f"  - {proposer} offers {int(value)} gold per turn")
        elif sweetener_type == "gold_lump":
            parts.append(f"  - {proposer} offers {int(value)} gold")
        elif sweetener_type in ("territory_cede", "territory"):
            detail = _format_clause_detail(sweetener)
            suffix = detail if detail else "territory"
            parts.append(f"  - {proposer} cedes {suffix}")
        elif sweetener_type == "open_borders":
            parts.append(f"  - {proposer} grants open borders")
        elif sweetener_type == "protection":
            parts.append(f"  - {proposer} offers protection guarantee")
        else:
            detail = _format_clause_detail(sweetener)
            label = clause_display_name(sweetener_type).lower()
            if detail:
                parts.append(f"  - {proposer} offers {label} ({detail})")
            else:
                parts.append(f"  - {proposer} offers {label}")

    for demand in terms.get("demands", []):
        demand_type = str(demand.get("type", "")).strip().lower()
        value = demand.get("value", 0)
        if demand_type == "gold_per_turn":
            parts.append(f"  - {proposer} demands {int(value)} gold per turn")
        elif demand_type == "gold_lump":
            parts.append(f"  - {proposer} demands {int(value)} gold")
        elif demand_type in ("territory_cede", "territory"):
            detail = _format_clause_detail(demand)
            suffix = detail if detail else "territory"
            parts.append(f"  - {proposer} demands {suffix}")
        else:
            detail = _format_clause_detail(demand)
            label = clause_display_name(demand_type).lower()
            if detail:
                parts.append(f"  - {proposer} demands {label} ({detail})")
            else:
                parts.append(f"  - {proposer} demands {label}")

    for clause in terms.get("clauses", []):
        clause_type = clause.get("type", "clause") if isinstance(clause, dict) else clause
        detail = _format_clause_detail(clause)
        label = clause_display_name(clause_type)
        if detail:
            parts.append(f"  - {label} ({detail})")
        else:
            parts.append(f"  - {label}")

    return "\n".join(parts)


def summarize_proposal(proposal: dict) -> str:
    """Generate a concise, backend-owned proposal summary for sabotage paths."""
    parts = [proposal_display_name(proposal.get("type", "peace"))]

    for demand in proposal.get("demands", []):
        demand_type = str(demand.get("type", "")).strip().lower()
        if demand_type in ("territory_cede", "territory"):
            regions = demand.get("regions", [])
            parts.append(f"cede {', '.join(regions)}" if regions else "territory")
        elif demand_type == "gold_per_turn":
            parts.append(f"{int(demand.get('value', 0))} gold/turn")
        elif demand_type == "ap_per_turn":
            parts.append(f"{int(demand.get('value', 1))} AP/turn")
        elif demand_type == "unit_trade":
            parts.append(f"{int(demand.get('value', 0))} units")
        else:
            detail = _format_clause_detail(demand)
            label = clause_display_name(demand_type).lower()
            if detail:
                parts.append(f"{label} ({detail})")
            else:
                parts.append(label)

    for sweetener in proposal.get("sweeteners", []):
        sweetener_type = str(sweetener.get("type", "")).strip().lower()
        if sweetener_type == "gold_per_turn":
            parts.append(f"offer {int(sweetener.get('value', 0))} gold/turn")
        else:
            detail = _format_clause_detail(sweetener)
            label = clause_display_name(sweetener_type).lower()
            if detail:
                parts.append(f"offer {label} ({detail})")
            else:
                parts.append(f"offer {label}")

    return ", ".join(parts) if parts else "unspecified terms"


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
