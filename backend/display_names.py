"""Single source of truth for all internal→display name translations.

All display maps live here.  Backend modules import from here.
Never return raw internal names to the frontend.

R7 — Architecture Refactoring Session 6.
"""

import re

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
    "propose_common_peace": "opens settlement with",  # Imperial Settlement
    "open_settlement": "opens settlement with",       # Godot wizard action
    "request_terms": "requests terms from",           # SC-30 / Slice G1
    "grant_dotation": "is endowed with",              # ES-7 (Economy S7)
    "grant_pension": "is granted a rente",            # ES-7 second pass (§0.6.8)
    "revoke_pension": "has his rente withdrawn",      # ES-7 second pass (§0.6.8)
    "recruit_marshal": "commissions",                 # Marshal Recruitment (v3.2)
    "grant_region_to_vassal": "cedes territory to",   # VS-3 (Vassal Depth)
    "sponsor_design": "sponsors",                     # AI-2b (D5-2)
    "buy_off_design": "buys off",                     # AI-2b (D5-1)
    "guarantee_nation": "guarantees",                 # AI-2b (D5-3)
    "build_fleet": "lays down a ship",                # DEF-5 naval (NV-0)
    "set_fleet_posture": "orders the fleet to",       # DEF-5 naval (NV-0)
    "naval_expedition": "embarks an expedition to",   # DEF-5 naval (NV-2)
    "naval_diversion": "orders the grand diversion",  # DEF-5 naval (NV-3)
}

# ============================================================================
# NATION DISPLAY — player-facing names for multi-word internal nation keys
# Internal nation keys are single tokens; three read wrong raw (R7). Mirrors
# Godot's Utils.NATION_DISPLAY_NAMES — keep the two maps in sync.
# ============================================================================

NATION_DISPLAY = {
    "Ottoman": "Ottoman Empire",
    "PapalStates": "Papal States",
    "KingdomOfItaly": "Kingdom of Italy",
    # NA-6c: the Class C carve tags. Unlike Godot, this chokepoint has no
    # camelCase fallback — an unauthored tag passes through RAW, so
    # "DuchyOfWarsaw" would reach the player verbatim in backend prose.
    "DuchyOfWarsaw": "Duchy of Warsaw",
    "RomanRepublic": "Roman Republic",
    # "Normandy" is deliberately ABSENT, mirroring Godot: it is also a
    # PROVINCE name on this map, and a carved Normandy always resolves its
    # player-facing name through the formation identity override anyway.
}


def display_nation(nation: str) -> str:
    """Return the player-facing name for an internal nation key."""
    return NATION_DISPLAY.get(nation, nation)


# ============================================================================
# NATION ADJECTIVES — "the French fleet", never "the France fleet"
# The SINGLE source (R7). `ai/strategic_parser.py` reads the same table for
# the parse side, so a nation added in one place is understood in both.
# ============================================================================

NATION_DEMONYMS = {
    "britain": "british",
    "france": "french",
    "spain": "spanish",
    "sweden": "swedish",
    "denmark": "danish",
    "naples": "neapolitan",
    "netherlands": "dutch",
    "holland": "dutch",
    "ottoman": "ottoman",
    "portugal": "portuguese",
    "switzerland": "swiss",
    "saxony": "saxon",
    "piedmont": "piedmontese",
    "hesse": "hessian",
    "papalstates": "papal",
    "kingdomofitaly": "italian",
}


def nation_adjective(nation: str) -> str:
    """The adjectival form, capitalised for prose: France → French,
    Austria → Austrian, Prussia → Prussian. Regular nations derive
    (-a → +'n', else +'ian'), which is why the table only holds the
    irregulars."""
    base = str(nation or "").lower()
    if not base:
        return ""
    demonym = NATION_DEMONYMS.get(base)
    if demonym is None:
        demonym = base + "n" if base.endswith("a") else base + "ian"
    return demonym[:1].upper() + demonym[1:]


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
    "propose_common_peace": "opening settlement",  # Imperial Settlement
    "open_settlement": "opening settlement",       # Godot wizard action
    "request_terms": "requesting terms",            # SC-30 / Slice G1
    "grant_dotation": "receiving an estate",        # ES-7 (no objections in v1)
    "grant_pension": "receiving a rente",           # ES-7 second pass (no objections in v1)
    "revoke_pension": "losing his rente",           # ES-7 second pass (no objections in v1)
    "recruit_marshal": "commissioning a marshal",   # Marshal Recruitment (no objections in v1)
    "grant_region_to_vassal": "ceding territory",   # VS-3 (no objections in v1)
    "sponsor_design": "sponsoring a design",        # AI-2b (no objections in v1)
    "buy_off_design": "buying off a design",        # AI-2b (no objections in v1)
    "guarantee_nation": "pledging a guarantee",     # AI-2b (no objections in v1)
    "build_fleet": "laying down a ship",            # DEF-5 naval (no objections in v1)
    "set_fleet_posture": "re-tasking the fleet",    # DEF-5 naval (no objections in v1)
    "naval_expedition": "embarking on the transports",  # DEF-5 naval (no objections in v1)
    "naval_diversion": "the grand diversion",       # DEF-5 naval (no objections in v1)
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
    "propose_common_peace": "opened settlement",  # Imperial Settlement
    "open_settlement": "opened settlement",       # Godot wizard action
    "request_terms": "requested terms",            # SC-30 / Slice G1
    "grant_dotation": "received an estate",        # ES-7 (no defiance in v1)
    "grant_pension": "received a rente",           # ES-7 second pass (no defiance in v1)
    "revoke_pension": "lost his rente",            # ES-7 second pass (no defiance in v1)
    "recruit_marshal": "commissioned a marshal",   # Marshal Recruitment (no defiance in v1)
    "grant_region_to_vassal": "ceded territory",   # VS-3 (no defiance in v1)
    "sponsor_design": "sponsored a design",        # AI-2b (no defiance in v1)
    "buy_off_design": "bought off a design",       # AI-2b (no defiance in v1)
    "guarantee_nation": "pledged a guarantee",     # AI-2b (no defiance in v1)
    "build_fleet": "laid down a ship",             # DEF-5 naval (no defiance in v1)
    "set_fleet_posture": "re-tasked the fleet",    # DEF-5 naval (no defiance in v1)
    "naval_expedition": "embarked an expedition",  # DEF-5 naval (no defiance in v1)
    "naval_diversion": "ordered the diversion",    # DEF-5 naval (no defiance in v1)
}

# ============================================================================
# W6-8 ESTATE CHOICE DISPLAY — player-facing labels for the conquered-estate
# resolution (the second capture choice). Choice tokens, not parser actions.
# ============================================================================

ESTATE_CHOICE_DISPLAY = {
    "confiscate": "Confiscate the estate",
    "respect": "Respect the title",
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
    "broker_peace": "Brokered Peace",  # AI-4b (§4.2b): mediate a third-party war
    "ultimatum_demand": "Ultimatum",  # PL-14
    # W6-10: the P3 relation-band gift ask (stable P-rule label; the terms
    # type underneath is non_aggression or open_borders)
    "friendly_gift": "Gift of Friendship",
    # AI-2 (AI_INTENT_SPEC §4.2): the intent-driven asks (stable P-rule
    # labels; the terms type underneath is a legal treaty state)
    "design_purchase": "Treaty of Cession",
    "sell_neutrality": "Purchase of Neutrality",
    # AI-5 (§4.5): a bandwagoning minor offers its own crown — the
    # Confederation of the Rhine step, chosen rather than imposed.
    "offer_vassalage": "Offer of Submission",
}

CLAUSE_TYPE_DISPLAY = {
    "peace": "Peace",
    "gold_lump": "Gold payment",
    "gold_indemnity": "Gold indemnity",
    "gold_per_turn": "Gold per turn",
    "territory_cede": "Territory cession",
    "territory_return": "Territory return",
    "territory": "Territory cession",
    "forced_alliance": "Forced alliance",
    "prisoner_return": "Prisoner return",  # W6-7 Marshal Fates (ransom)
    "vassalage": "Vassalage",
    "subjugation": "Subjugation",
    "liberation": "Liberation",
    "action_point": "Action point concession",
    "ap_per_turn": "Action point concession",
    "ap_reduction": "Action point reduction",
    "unit_trade": "Military units",
    "open_borders": "Open borders",
    "protection": "Protection guarantee",
    "protection_promised": "Protection guarantee",
    # AI-2d (Stage C): the sell-neutrality bond, DISCLOSED at decision
    # time (pin 23 — accepting binds France out of the payer's war;
    # entering it later is reneging).
    "neutrality_compact": "Neutrality compact — France stays OUT of their war (entering it later is reneging)",
    "continental_system_lifted": "Continental System lifted",
    "manpower_infantry": "Infantry manpower",
    "infantry_manpower": "Infantry manpower",
    "manpower_cavalry": "Cavalry reserves",
    "cavalry_manpower": "Cavalry reserves",
    "manpower_artillery": "Artillery reserves",
    "artillery_manpower": "Artillery reserves",
    "war_bargain": "War bargain",
    # VS-5 / NA-6c: the two dependency clauses that mint or move a court.
    # Both were reaching the title-case fallback ("Vassal Transfer" /
    # "Create Client") — flat, non-diegetic, and in NA-6c's case actively
    # misleading about what happens.
    "vassal_transfer": "Vassal transferred",
    "create_client": "Client state erected",
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
    # W6-8 (Spoils of War) — the conqueror honored one of their marshals'
    # titles on occupied estate soil.
    "respected_estate_mod": {
        "negative": "no honored titles between our courts",
        "positive": "the marshal's title we chose to respect",
    },
    # NA-2 (Nation Agendas §5.2) — the offer advanced or entrenched the
    # denial of the target court's active national design.
    "agenda_mod": {
        "negative": "the design of their court our terms deny",
        "positive": "the design of their court our terms advance",
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
    # CA9 row 1 (war-age penalty). Only ever negative — the term is 0 or
    # below by construction — but both keys are authored so a future sign
    # flip cannot fall through to "unknown factors".
    "war_age_penalty": {
        "negative": "the war is barely begun — no court signs away a "
                    "province over one skirmish",
        "positive": "the war has run long enough to be worth ending",
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

# W6-4 muster preview (EXP-C1): reason codes -> the player-facing line that
# explains why a nearby friendly WILL or WILL NOT join the battle. Derived
# from the EXISTING reinforcement eligibility + Grouchy Rule — codes only,
# the mechanics are untouched.
MUSTER_REASON_DISPLAY = {
    "shares_the_field": "stands on the field and will fight beside him",
    "has_support_order": "marches under your written support order",
    "aggressive_marches": "will march to the sound of the guns",
    "answers_the_guns": "is willing to march if the roads allow",
    "literal_awaits_orders": "awaits explicit orders and will NOT march",
    # MC-1 signature-ability arms (W6-4 honesty)
    "roland_marches": "marches to the sound of the guns — the Roland of the Army",
    "eyes_on_a_crown": "hesitates — the I Corps weighs its own ambitions",
    "fortified_static": "is dug in and will not abandon his works",
    "holding_position": "holds his position under standing orders",
    "drilling": "is drilling and cannot break formation in time",
    "broken_recovering": "is in no condition to fight",
    "hostile_refuses": "will not lift a finger for this marshal",
    "cooldown_spent": "has already marched this turn",
    "engaged": "is pinned by enemies before his own front",
    "square_formation": "stands in square and cannot march",
    # VS-4: assimilated ex-vassal contingent whose homeland wavers
    "vassal_wavering": "will not march — his homeland's loyalty wavers",
    # NV-9: reinforcement Rule 2b — the sea between him and the guns
    "sea_barred": "cannot reach the guns — the enemy's sail lie between",
    # CA9-F13 (review round): the field is on a court we are at peace
    # with, so no order can send him there. shown = applied — the
    # relocation guard turns him back, and the preview must say so
    # rather than promising a march and pricing him into the odds.
    "neutral_soil": "cannot march — the field is on soil we are not at war with",
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
    "agenda_pursuit": "national design",
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
# ALLY ENTRY BLOCK DISPLAY — whole sentences for the war-entry hard blocks
# Source: IGR-A item A1. `get_ally_entry_hard_blocks` (diplomacy.py) returns
# machine keys; two surfaces used to print them verbatim
# ("Spain cannot join against Prussia: no_participation_path.").
#
# Register is CHANCERY THIRD PERSON with no "Sire" — the same table feeds the
# campaign log, which is a chronicle and never addresses the Emperor. Wrap
# Talleyrand's first person at a call site if a surface wants it.
#
# Placeholders: {ally} (beneficiary), {enemy} (named enemy), {promiser} (the
# power making the call — "us" when it cannot be threaded).
#
# NOT registered in `_CATEGORY_MAPS`: `display()` returns a hit verbatim, so a
# brace-bearing template there would ship a NEW leak. Same reason
# AMENDS_REFUSAL_DISPLAY is kept out. Three of the producer's keys carry a
# dynamic nation suffix, so lookup is prefix-aware — see
# `ally_entry_block_line`.
# ============================================================================

ALLY_ENTRY_BLOCK_DISPLAY = {
    "armistice_cooldown_with_": (
        "{ally} is still bound by its armistice with {enemy} and cannot take "
        "the field against that court."
    ),
    "anti_promiser_coalition_member": (
        "{ally} has taken its place in the coalition against {promiser} and "
        "will not march at our side."
    ),
    "hard_reject_posture": (
        "{ally} has shut its chancery to us after repeated betrayals and will "
        "hear no call to arms against {enemy}."
    ),
    "no_participation_path": (
        "{ally} can find no road to {enemy} — no shared border, and no "
        "friendly passage within reach — so its armies could never come to "
        "grips."
    ),
    # Structurally unreachable from the live producer today (a court cannot be
    # both ALLIANCE and WAR on one symmetric key), but named so a future
    # producer cannot re-leak the raw string.
    "at_war_with_": (
        "{ally} already stands against us in this quarrel and cannot be "
        "called to our side."
    ),
    "direct_enemy_of_": (
        "{ally} already stands against us in this quarrel and cannot be "
        "called to our side."
    ),
}

# Keys whose stored form is a PREFIX (the producer appends a nation name).
_ALLY_ENTRY_BLOCK_PREFIXES = (
    "armistice_cooldown_with_",
    "at_war_with_",
    "direct_enemy_of_",
)

ALLY_ENTRY_BLOCK_FALLBACK = "{ally} cannot be brought into the war against {enemy}."


# ============================================================================
# IMPERIAL SETTLEMENT DISPLAY — disabled reasons, acceptance, and components
# ============================================================================

SETTLEMENT_DISABLED_REASON_DISPLAY = {
    "inactive_war_instance": "This war state has changed; reopen settlement review.",
    "invalid_war_id": "This war can no longer be found.",
    "war_state_changed_since_open": "This war changed while the review was open.",
    "missing_player_nation": "No player nation was available for this settlement.",
    "missing_target_nation": "Choose a hostile court before opening settlement.",
    "self_settlement": "France cannot settle with itself.",
    "not_at_war": "France is not at war with this court.",
    "not_side_leader": "Only the war leader can settle this side.",
    "one_to_one_war": "Use bilateral peace or armistice for a one-on-one war.",
    "no_unresolved_hostile_pairs": "There are no hostile pairs left to settle.",
    "no_coverable_enemy": "There is no enemy participant this settlement can cover.",
    "settlement_dialogue_active": "Resolve the current settlement review first.",
    "multi_war_ambiguity": "Multiple wars with this court; select a specific war from war detail.",
    "proposer_leader_changed": "Your side's war leader changed; reopen settlement review.",
    "active_pair_changed": "The war changed while the settlement was open.",
    "no_selected_target_nation": "No settlement target court is selected.",
    "no_covered_enemy_participants": "No enemy participant is selected for settlement.",
    # G4F-18: the V5 coverage floor — distinct from a missing selection.
    "coverage_floor": (
        "At least one covered enemy court must remain. To abandon the "
        "settlement entirely, use Back Out instead."
    ),
    "selected_target_not_covered": "The selected settlement target is outside this settlement scope.",
    "settlement_eligibility_unavailable": "Settlement eligibility could not be evaluated; reopen war detail.",
    "malformed_route": "This recovery route is incomplete.",
    "war_archived": "This war is no longer active; review settlement history.",
    "selected_pair_missing": "No live enemy pair is selected for war detail recovery.",
    "pair_not_at_war": "The selected pair is not currently at war.",
    "pair_already_resolved": "The selected pair has already been resolved.",
    "editor_cannot_change_blocker": "The settlement editor cannot change this blocker.",
    "no_peace_seeking_control": "War detail has no current peace-seeking control for this pair.",
    "request_terms_ineligible": "Requesting enemy terms is not available for this pair.",
    "active_participant_changed": "A participant changed sides or left the war.",
    "no_resolvable_pairs": "No covered hostile pair can be resolved by these terms.",
    "unknown_settlement_action": "That settlement choice is not recognized.",
    "unknown_settlement_offer_action": "That settlement-offer choice is not recognized.",
    # SC-1 POST preview validation codes
    "max_clause_count_exceeded": "Too many treaty clauses (maximum 8).",
    "duplicate_or_conflicting_clauses": "Some treaty clauses conflict with each other.",
    "unauthorized_actor": "Only the player nation may author settlement terms.",
    "proposer_side_mismatch": "The proposing court does not match your side in this war.",
    "empty_authored_draft": "Add at least one treaty clause before submitting.",
    "invalid_clause_type": "One or more clauses use an unrecognized type.",
    "invalid_clause_schema": "One or more clauses are missing required fields.",
    "submitted_terms_failed_revalidation": "The submitted terms failed validation; review and correct them.",
    # Re-front Slice 3 §12 cross-court validity codes (V1-V3).
    "region_double_promised": "The same region cannot be promised to two different courts.",
    "clause_target_uncovered": "A clause names a court that is not part of this settlement.",
    "clause_side_mismatch": "A clause's giving and receiving courts must be on opposite sides of the war.",
    # SC-3/SC-4 ratification gate codes
    "acceptance_rejected": "The accepting side has rejected these terms.",
    "acceptance_blocked": "A hard stop prevents ratification of these terms.",
    # SC-14b reopen-attempt cap
    "reopen_attempt_cap_exceeded": "We cannot reopen this settlement review - choose from war detail.",
    # SC-13 dual-empty fallback / SC-7b stale offer fallback
    "no_reopen_target_available": "We cannot reopen this settlement review - choose from war detail.",
    # SC-7b stale incoming offer
    "incoming_offer_war_archived": "That settlement offer is no longer relevant; the war has ended.",
    "incoming_offer_war_invalid": "That settlement offer references a war we cannot find; choose from war detail.",
    # SC-5 reversal commit 1 leaves the deferred constant in place as a
    # named flag so a future emergency disable can flip it back to True
    # without a code rewrite. The display string is only ever reached
    # through a stale-save defensive path or that emergency disable.
    "incoming_offer_deferred": "Incoming settlement offers are not available in this build.",
    # SC-26 collision codes
    "cross_war_settlement_collision": "Resolve the active settlement review before opening another war's settlement.",
    "same_war_merge_conflict": "These terms conflict with the open settlement review; revise before merging.",
    # SC-14e aged-out dispatch link
    "settlement_no_longer_in_recent_window": "That settlement is no longer in the recent window.",
    # SC-29 / G2-Slice-7 pair-scoped peace substitute eligibility codes.
    # Closed taxonomy per SETTLEMENT_UI_CLEANUP_SPEC.md "Pair substitute
    # eligibility helper schema". Reuses pair_not_at_war / war_archived /
    # malformed_route / settlement_collision_active from the surrounding
    # helper taxonomy.
    "already_at_peace": "France is already at peace with this court.",
    "already_in_armistice": "France is already in armistice with this court.",
    "actor_not_at_war_with_target": "France is not at war with this court.",
    "target_not_selected_pair": "This court is not the selected hostile pair for this war.",
    "target_not_in_war": "This court is not a participant in this war.",
    "cooldown_active": "A recent proposal cooldown is still active for this court.",
    "insufficient_resources": "Insufficient diplomatic points for this proposal.",
    # SC-31 / G2-Slice-8 dependency-clause eligibility codes. Closed
    # taxonomy returned by evaluate_subjugation_eligibility /
    # evaluate_vassalage_eligibility / evaluate_liberation_eligibility.
    "dependency_direction_invalid": (
        "Dependency clauses must list the vassal/subjugated nation as "
        "from and the lord as to."
    ),
    "dependency_target_not_in_war": (
        "Dependency clauses require the lord and the target to be on "
        "opposite sides of the active war."
    ),
    "dependency_target_already_vassal": (
        "That nation is already someone's vassal; release them before "
        "imposing a new dependency."
    ),
    # VS-5 (July 16, 2026): vassal_transfer refusal — the named vassal is
    # not currently a vassal of the named losing lord.
    "transfer_target_not_their_vassal": (
        "That nation is not currently a vassal of the court you would "
        "take it from."
    ),
    # VS-5 post-build review C5: one package cannot both free a vassal and
    # claim it.
    "dependency_same_vassal_conflict": (
        "These terms both liberate and claim the same vassal - strike one "
        "of the two."
    ),
    # NA-6c (July 19, 2026): carve-out refusals. Every one names what is
    # missing, so the honest-availability chip can state its gate terms
    # rather than simply vanishing (§11.6-1).
    "carve_template_unknown": (
        "No such client state can be erected - the scenario authors no "
        "template by that name."
    ),
    "carve_tag_already_exists": (
        "That state already stands on the map; it cannot be erected twice."
    ),
    "carve_provinces_not_held": (
        "Your armies do not hold every province the new state would be "
        "made of."
    ),
    "carve_not_defeated_soil": (
        "A client state is carved from the soil of the court that is "
        "paying - not from land taken elsewhere, and never from your own."
    ),
    "carve_total_annexation_blocked": (
        "This would take their last province and erase them from the map. "
        "Only a decisive victory can do that."
    ),
    "carve_region_double_promised": (
        "A province cannot both be ceded and be made part of a new client "
        "state - strike one of the two."
    ),
    "dependency_power_cap_blocked": (
        "The lord lacks the national power to legally vassalize a "
        "target this large."
    ),
    "dependency_invalid": "Dependency clause is not eligible for this war.",
    "liberation_target_not_vassal": (
        "Liberation requires the target to currently be a vassal."
    ),
    "liberation_lord_mismatch": (
        "The declared lord does not match the target's current lord."
    ),
    "liberation_invalid_liberator": (
        "The liberator must be a recognized nation on the opposite side "
        "of the current lord, and not the lord or the vassal itself."
    ),
    "liberation_invalid": "Liberation clause is not eligible for this war.",
    # SC-31 / G2-Slice-8 surrender preset dialogue refusal codes.
    "surrender_preset_unavailable": (
        "No surrender preset is available now; author concessions or "
        "hold the line."
    ),
    "surrender_preset_failed_preview": (
        "The surrender preset could not be previewed; try refreshing."
    ),
    # SC-33 / G2-Slice-9 recurring gold payment validator codes.
    "gold_per_turn_amount_too_small": (
        "Recurring gold payments must be at least 10 gold per turn."
    ),
    "gold_per_turn_duration_out_of_range": (
        "Recurring gold payments must run between 1 and 20 turns."
    ),
    "gold_payment_budget_conflict": (
        "The combined gold obligation exceeds projected solvency for "
        "the payer; reduce the amount, the duration, or pair it with a "
        "smaller lump-sum demand."
    ),
}

# Side label display — used by settlement review's allies block to surface
# "Attackers" / "Defenders" instead of leaking the raw enum keys downstream.
SIDE_LABEL_DISPLAY = {
    "attackers": "Attackers",
    "defenders": "Defenders",
}

# G4F-7 (Gate-4 smoke): the band chips must be threshold-honest. A court
# below the ratify threshold is mechanically a HOLDOUT — the old
# "Near acceptable" chip put the word "acceptable" on a blocking state, and
# two such rows read as "net terms acceptable" in the live smoke. Wording
# aligns with the committed multi-court voice families (will sign /
# leaning / holds out).
ACCEPTANCE_BAND_DISPLAY = {
    "accept": "Will sign",
    "acceptable": "Will sign",
    "near_acceptable": "Holding out (close)",
    "reject": "Holding out",
    "unlikely": "Holding out",
    "blocked": "Blocked",
}

ACCEPTANCE_BAND_PHRASE = {
    "accept": "Likely to accept",
    "acceptable": "Likely to accept",
    "near_acceptable": "Close, but not yet acceptable",
    "reject": "Likely to reject",
    "unlikely": "Likely to reject",
    "blocked": "Blocked by a hard condition",
}

ACCEPTANCE_COMPONENT_DISPLAY = {
    "base_side_pressure": "Base side pressure",
    "settlement_tier_legitimacy": "Settlement legitimacy",
    "term_harshness_penalty": "Term harshness",
    "leader_own_losses": "Leader's own losses",
    "burdened_participant_penalty": "Ally burden",
    "projected_hegemony_mod": "Balance of Europe pressure",
    "war_objective_alignment": "War objective alignment",
    "concession_credit": "Concession credit",
    "war_exhaustion": "War exhaustion",
    "abandoned_by_ally_acceptance_mod": "Abandoned ally grievance",
    # NA-3 §7 rider (a): the per-court agenda term on the settlement scorer
    "agenda_settlement_mod": "National design",
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
    "settlement_disabled_reason": SETTLEMENT_DISABLED_REASON_DISPLAY,
    "acceptance_band": ACCEPTANCE_BAND_DISPLAY,
    "acceptance_component": ACCEPTANCE_COMPONENT_DISPLAY,
    "side_label": SIDE_LABEL_DISPLAY,
}


def action_display_name(action: str) -> str:
    """Translate internal action name to player-readable text."""
    return ACTION_DISPLAY.get(action, action.replace("_", " "))


def diplomatic_decision_reason_display(reason: str) -> str:
    """Translate a deterministic decision_reason enum to player-facing text."""
    result, raw = _lookup_display_name(DECISION_REASON_DISPLAY, reason)
    return result or _fallback_display_name(raw, default="")


def ally_entry_block_line(
    reason: str,
    beneficiary: str,
    named_enemy: str,
    promiser: str = "",
    world=None,
) -> str:
    """IGR-A1: render ONE war-entry hard block as a whole prose sentence.

    `reason` is the raw key from `get_ally_entry_hard_blocks`. Three of its
    kinds carry a dynamic nation suffix (`armistice_cooldown_with_Prussia`),
    so an exact dict lookup is not enough — prefixes are matched explicitly.

    Never falls through to `_fallback_display_name`: title-casing the key
    ("No Participation Path") is the same leak wearing a hat. Unknown keys get
    a prose default instead.
    """
    key = str(reason or "")
    template = ALLY_ENTRY_BLOCK_DISPLAY.get(key)
    if template is None:
        for prefix in _ALLY_ENTRY_BLOCK_PREFIXES:
            if key.startswith(prefix):
                template = ALLY_ENTRY_BLOCK_DISPLAY.get(prefix)
                break
    if template is None:
        template = ALLY_ENTRY_BLOCK_FALLBACK

    # NA-6 §11.8 stage 3 ("no surface may show the dead name"): once a court
    # has formed, `display_nation` is the DEAD name, and because this helper
    # composes finished prose the client's raw-tag override can never repair
    # it downstream. Resolve through the formation-aware chokepoint when a
    # world is available. `format_event_oneliner` has none, but the campaign
    # log is already repaired by `apply_formation_names_to_history`.
    def _name(tag: str, fallback: str) -> str:
        if not tag:
            return fallback
        if world is not None:
            try:
                from backend.game_logic.formations import formed_display_name
                return formed_display_name(world, tag)
            except Exception:
                pass
        return display_nation(tag)

    return template.format(
        ally=_name(beneficiary, "That court"),
        enemy=_name(named_enemy, "that court"),
        # The campaign-log event carries no promiser; "us" keeps the line
        # true from the player's chair without hardcoding France.
        promiser=_name(promiser, "us"),
    )


def warnings_to_plain_text(warnings, separator: str = "\n") -> str:
    """IGR-A2: the ONE formatter for a structured `warnings[]` list as prose.

    The confirm dialogues ship `warnings[]` to a popup that renders them under
    "Political Context:", so they must NOT also inline them into the message
    (that was the duplication A2 fixes). Surfaces that have no such renderer —
    the commitment-paradox popup, API-only consumers — route through here so
    the concatenation cannot be hand-rolled back into existence.
    """
    if not warnings:
        return ""
    lines = []
    for warning in warnings:
        text = ""
        if isinstance(warning, dict):
            text = str(warning.get("text", "") or "")
        elif warning:
            text = str(warning)
        if text:
            lines.append(text)
    return separator.join(lines)


def settlement_disabled_reason_display(reason: str) -> str:
    """Translate settlement eligibility/refusal reason codes."""
    result, raw = _lookup_display_name(SETTLEMENT_DISABLED_REASON_DISPLAY, reason)
    return result or _fallback_display_name(raw, default="Settlement unavailable.")


def acceptance_band_display(band: str) -> str:
    """Translate settlement acceptance band/verdict codes."""
    result, raw = _lookup_display_name(ACCEPTANCE_BAND_DISPLAY, band)
    return result or _fallback_display_name(raw, default="Acceptance unknown")


def acceptance_band_phrase(band: str) -> str:
    """Return a short player-facing acceptance phrase."""
    result, raw = _lookup_display_name(ACCEPTANCE_BAND_PHRASE, band)
    return result or acceptance_band_display(raw)


def acceptance_component_display(component: str) -> str:
    """Translate settlement acceptance component keys."""
    result, raw = _lookup_display_name(ACCEPTANCE_COMPONENT_DISPLAY, component)
    return result or _fallback_display_name(raw, default="Settlement pressure")


def side_label_display(side: str) -> str:
    """Translate `attackers` / `defenders` enum to player-facing text."""
    result, raw = _lookup_display_name(SIDE_LABEL_DISPLAY, side)
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


# Splits a camelCase / underscore entity KEY into its display form without
# re-casing the words (so "ArchdukeCharles" -> "Archduke Charles",
# "White_Russia" -> "White Russia", already-spaced "Mack" / "Archduke Charles"
# pass through unchanged). Backend-side chokepoint for player-facing prose that
# embeds a raw marshal/region key (R7): Godot's render-time humanizer only
# splits a short list of NATION keys, never camelCase MARSHAL names, so any
# terminal/popup message composed backend-side must humanize here.
_CAMEL_BOUNDARY_RE = re.compile(r"(?<=[a-z])(?=[A-Z])")


def humanize_entity_name(name: str) -> str:
    if not name:
        return name
    return _CAMEL_BOUNDARY_RE.sub(" ", str(name)).replace("_", " ")


def with_indefinite_article(phrase: str) -> str:
    """Prefix "a"/"an" by leading letter ("an Open Borders Agreement")."""
    if not phrase:
        return phrase
    article = "an" if phrase[0].lower() in "aeiou" else "a"
    return f"{article} {phrase}"


# PC-9 (quiet-France played campaign, Aug 3 2026): "The Switzerland has
# ceased to exist." A state's name takes a definite article when it names an
# INSTITUTION (a Duchy, a Republic, a Confederation) or is a plural/compound
# ("the United Provinces", "the Two Sicilies"), and takes none when it is a
# bare proper noun. Carved clients are authored both ways — "Duchy of Warsaw"
# and "Poland" flow through the same sentence — so the article cannot be
# hardcoded into the template.
_INSTITUTION_WORDS = frozenset({
    "duchy", "duchies", "kingdom", "republic", "confederation", "empire",
    "electorate", "principality", "states", "provinces", "union", "league",
    "netherlands", "sicilies", "cantons",
})
# Leading modifiers that make the whole name definite even when no
# institution noun follows ("the United Netherlands", "the Two Sicilies").
_DEFINITE_ARTICLE_HEADS = frozenset({
    "united", "grand", "holy", "papal", "free", "two", "helvetic",
    "batavian", "ligurian", "cisalpine",
})


def takes_definite_article(name: str) -> bool:
    """Whether a state's display name reads with a leading "the"."""
    clean = humanize_entity_name(str(name or "")).strip()
    if not clean:
        return False
    words = [w.lower() for w in clean.split()]
    if words[0] == "the":
        return False  # already carries its own article
    if words[0] in _DEFINITE_ARTICLE_HEADS:
        return True
    if any(w in _INSTITUTION_WORDS for w in words):
        return True
    # "Kingdom of Italy" / "Confederation of the Rhine" — an " of " compound
    # names an institution even when the noun itself is unlisted.
    return "of" in words


def with_definite_article(name: str, capitalize: bool = False) -> str:
    """Render a state name with "the" only where English wants it.

    "Duchy of Warsaw" -> "the Duchy of Warsaw"; "Switzerland" -> "Switzerland".
    `capitalize` for sentence-initial use ("The Duchy of Warsaw has…").
    """
    clean = humanize_entity_name(str(name or "")).strip()
    if not clean or not takes_definite_article(clean):
        return clean
    return f"{'The' if capitalize else 'the'} {clean}"


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
        elif demand_type == "create_client":
            # NA-6c / IGR-D: without this arm the generic fallback below
            # renders a bare "Demand: Client state erected" — naming
            # neither the nation being founded nor the soil it stands on,
            # on the one surface where the player commits to the carve.
            client = str(demand.get("client_display_name")
                         or demand.get("tag") or "a client state")
            provinces = [str(p) for p in (demand.get("provinces") or []) if p]
            soil = f" out of {', '.join(provinces)}" if provinces else ""
            lines.append(f"{target_label} yields {client}{soil}")
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
