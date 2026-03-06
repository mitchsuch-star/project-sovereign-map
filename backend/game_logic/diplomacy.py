"""
Diplomacy Engine — Phase 8 Session 2

All functions are pure/deterministic — no LLM calls.
Single source of truth for diplomatic mechanics:
  - State transitions & validation
  - War score calculation
  - Acceptance formula
  - DP economy
  - War declaration & cascade
  - Downgrade transitions
"""

from typing import Dict, List

# ═══════ DIPLOMATIC STATE HIERARCHY ═══════
# Upgrade path (adjacency enforced):
# WAR → ARMISTICE → PEACE → OPEN_BORDERS → NON_AGGRESSION → DEFENSIVE_ALLIANCE → ALLIANCE
#                                                                                       ↓
#                                                                                    VASSAL

DIPLOMATIC_STATES = [
    "WAR", "ARMISTICE", "PEACE", "OPEN_BORDERS",
    "NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE", "VASSAL"
]

# Upgrade adjacency (index in list → next valid state)
_UPGRADE_ORDER = [
    "WAR", "ARMISTICE", "PEACE", "OPEN_BORDERS",
    "NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE"
]

# Downgrade adjacency
_DOWNGRADE_ORDER = [
    "ALLIANCE", "DEFENSIVE_ALLIANCE", "NON_AGGRESSION",
    "OPEN_BORDERS", "PEACE"
]

# States that allow movement through territory
OPEN_MOVEMENT_STATES = {"OPEN_BORDERS", "DEFENSIVE_ALLIANCE", "ALLIANCE", "VASSAL"}

# ═══════ TRADE INCOME TABLE (§7e) ═══════
TRADE_INCOME = {
    "PEACE": 50,
    "OPEN_BORDERS": 100,
    "NON_AGGRESSION": 150,
    "DEFENSIVE_ALLIANCE": 150,
    "ALLIANCE": 200,
}
# WAR, ARMISTICE: 0. VASSAL: 0 (tribute replaces trade, Session 5)

# ═══════ TRANSITION COSTS & REQUIREMENTS ═══════
TRANSITION_RULES = {
    # (from, to): {"dp_cost": int, "relation_req": int or None}
    ("WAR", "ARMISTICE"): {"dp_cost": 1, "relation_req": None},
    ("ARMISTICE", "PEACE"): {"dp_cost": 2, "relation_req": -60},
    ("PEACE", "OPEN_BORDERS"): {"dp_cost": 1, "relation_req": -20},
    ("OPEN_BORDERS", "NON_AGGRESSION"): {"dp_cost": 1, "relation_req": 0},
    ("NON_AGGRESSION", "DEFENSIVE_ALLIANCE"): {"dp_cost": 2, "relation_req": 20},
    ("DEFENSIVE_ALLIANCE", "ALLIANCE"): {"dp_cost": 2, "relation_req": 40},
}

# ═══════ STATE-LEVEL RELATION REQUIREMENTS (R98: jumps) ═══════
# For non-adjacent upward jumps, the TARGET state's relation requirement applies.
STATE_RELATION_REQUIREMENTS = {
    "ARMISTICE": None,
    "PEACE": -60,
    "OPEN_BORDERS": -20,
    "NON_AGGRESSION": 0,
    "DEFENSIVE_ALLIANCE": 20,
    "ALLIANCE": 40,
}

# Vassal: requires OPEN_BORDERS or above
VASSAL_MIN_STATES = {"OPEN_BORDERS", "NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE"}
VASSAL_DP_COST = 3

# War declaration
WAR_DP_COST = 1

# ═══════ DOWNGRADE PENALTIES ═══════
DOWNGRADE_PENALTIES = {
    ("ALLIANCE", "DEFENSIVE_ALLIANCE"): {
        "dp_cost": 1, "relation_target": -15, "relation_all": -5, "threat": 5
    },
    ("DEFENSIVE_ALLIANCE", "NON_AGGRESSION"): {
        "dp_cost": 1, "relation_target": -20, "relation_all": -5, "threat": 5
    },
    ("NON_AGGRESSION", "OPEN_BORDERS"): {
        "dp_cost": 1, "relation_target": -15, "relation_all": 0, "threat": 3
    },
    ("OPEN_BORDERS", "PEACE"): {
        "dp_cost": 1, "relation_target": -10, "relation_all": 0, "threat": 0
    },
}

# Auto-downgrade thresholds (§5b.1)
STATE_RELATION_THRESHOLDS = {
    "ALLIANCE": 40,
    "DEFENSIVE_ALLIANCE": 20,
    "NON_AGGRESSION": 0,
    "OPEN_BORDERS": -20,
}

# ═══════ BASE DISPOSITION BY PROPOSAL TYPE ═══════
BASE_DISPOSITION = {
    "armistice_losing": 40,
    "armistice_winning": 20,
    "peace": 30,
    "alliance": 20,
    "defensive_alliance": 25,
    "vassalage": 10,
    "open_borders": 35,
    "non_aggression": 30,
}

# ═══════ PERSONALITY MODIFIERS ═══════
# {personality: (peace_alliance_mod, harsh_demands_mod)}
PERSONALITY_MODIFIERS = {
    "dove": (10, -10),
    "hawk": (-5, 5),
    "loyalist": (0, 0),
    "schemer": (5, 5),
}

# ═══════ SPECIAL ACCEPTANCE BONUSES (§6d) ═══════
# Checked against proposal clauses
SPECIAL_BONUSES = {
    "Prussia": {"territory_saxony": 10},
    "Austria": {"territory_bavaria": 8},
    "Britain": {"continental_system_lifted": 15},
    "Saxony": {"protection_promised": 10},
}

# ═══════ FEEDBACK STRINGS (§6f) ═══════
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
}

# ═══════ SWEETENER / DEMAND VALUES ═══════
SWEETENER_VALUES = {
    "gold_lump": 1 / 200,         # +1 per 200g
    "gold_per_turn": 3 / 100,     # +3 per 100g/turn
    "manpower_per_turn": 2 / 2000, # +2 per 2000 infantry/turn
    "infantry_manpower": 2 / 5000, # +2 per 5000
    "cavalry_manpower": 4 / 2500,  # +4 per 2500
    "artillery_manpower": 5 / 1500, # +5 per 1500
    "unit_swap": 3,                # +3 per favorable trade
    "ap_per_turn": 8,              # +8 per AP
    "territory": 5,                # +5 per region
    "open_borders": 3,             # +3 flat
    "protection": 5,               # +5 flat
}
SWEETENER_CAP = 30

DEMAND_VALUES = {
    "gold_per_turn": -2 / 100,     # -2 per 100g/turn demanded
    "manpower_per_turn": -3 / 2000, # -3 per 2000 infantry/turn demanded
    "territory": -5,                # -5 per region demanded
    "ap_per_turn": -25,             # -25 per AP demanded (extreme)
    "unit_swap": -2,                # -2 per unfavorable trade
}


# ═══════════════════════════════════════════════════════
# STATE TRANSITION VALIDATION
# ═══════════════════════════════════════════════════════

def validate_transition(current_state: str, target_state: str) -> bool:
    """Check if a diplomatic state transition is valid (adjacency only, no relation check)."""
    if current_state == target_state:
        return False

    # Any state → WAR (war declaration) — always valid
    if target_state == "WAR":
        return True

    # VASSAL transitions
    if target_state == "VASSAL":
        return current_state in VASSAL_MIN_STATES
    if current_state == "VASSAL":
        return target_state in ("WAR", "PEACE")

    # Upgrade path: any upward jump allowed (R98 — cumulative DP cost)
    if current_state in _UPGRADE_ORDER and target_state in _UPGRADE_ORDER:
        curr_idx = _UPGRADE_ORDER.index(current_state)
        tgt_idx = _UPGRADE_ORDER.index(target_state)
        if tgt_idx > curr_idx:
            return True

    # Downgrade path: must be adjacent in _DOWNGRADE_ORDER
    if current_state in _DOWNGRADE_ORDER and target_state in _DOWNGRADE_ORDER:
        curr_idx = _DOWNGRADE_ORDER.index(current_state)
        tgt_idx = _DOWNGRADE_ORDER.index(target_state)
        if tgt_idx == curr_idx + 1:
            return True

    return False


def check_relation_requirement(current_state: str, target_state: str, relation: int) -> bool:
    """Check if relation meets the requirement for an upgrade transition.

    R98: Uses target state's relation requirement (supports jumps).
    Returns True if requirement is met or no requirement exists.
    """
    req = STATE_RELATION_REQUIREMENTS.get(target_state)
    if req is None:
        return True
    return relation > req


def get_transition_dp_cost(current_state: str, target_state: str) -> int:
    """Get DP cost for a transition.

    R98: For upward jumps, sums all intermediate step DP costs.
    E.g. PEACE→ALLIANCE = 1+1+2+2 = 6 DP.
    """
    if target_state == "WAR":
        return WAR_DP_COST
    if target_state == "VASSAL":
        return VASSAL_DP_COST

    # Adjacent upgrade (exact match in TRANSITION_RULES)
    rule = TRANSITION_RULES.get((current_state, target_state))
    if rule:
        return rule["dp_cost"]

    # Non-adjacent upward jump: sum intermediate costs
    if current_state in _UPGRADE_ORDER and target_state in _UPGRADE_ORDER:
        curr_idx = _UPGRADE_ORDER.index(current_state)
        tgt_idx = _UPGRADE_ORDER.index(target_state)
        if tgt_idx > curr_idx:
            total = 0
            for i in range(curr_idx, tgt_idx):
                step_from = _UPGRADE_ORDER[i]
                step_to = _UPGRADE_ORDER[i + 1]
                step_rule = TRANSITION_RULES.get((step_from, step_to))
                total += step_rule["dp_cost"] if step_rule else 1
            return total

    # Downgrade
    penalty = DOWNGRADE_PENALTIES.get((current_state, target_state))
    if penalty:
        return penalty["dp_cost"]
    return 1  # Default


# ═══════════════════════════════════════════════════════
# WAR SCORE CALCULATION (§6e)
# ═══════════════════════════════════════════════════════

def calculate_war_score(nation_a: str, nation_b: str, world, return_components: bool = False):
    """Calculate war score between two nations. Positive = nation_a winning.

    Components: territory (±40), battles (±30), decisive (±20), capital (±30).
    Total capped at ±100.

    If return_components=True, returns {"total": int, "territory": int,
    "battles": int, "decisive": int, "capital": int} instead of int.
    """
    from backend.models.region import NATION_CAPITALS

    # Territory score (cap ±40)
    territory_score = 0
    a_starting = set(world.nation_starting_regions.get(nation_a, []))
    b_starting = set(world.nation_starting_regions.get(nation_b, []))
    for region in world.regions.values():
        if region.name in b_starting and region.controller == nation_a:
            territory_score += 5  # A holds B's starting region
        if region.name in a_starting and region.controller == nation_b:
            territory_score -= 5  # B holds A's starting region
    territory_score = max(-40, min(40, territory_score))

    # Battle score (cap ±30)
    battle_score = 0
    diplo_key = world._make_diplo_key(nation_a, nation_b)
    records = getattr(world, 'battle_records', {}).get(diplo_key, [])
    for record in records:
        if record.get("winner") == nation_a:
            battle_score += 3
        elif record.get("winner") == nation_b:
            battle_score -= 3
    battle_score = max(-30, min(30, battle_score))

    # Decisive battle bonus (cap ±20)
    decisive_score = 0
    decisive_records = getattr(world, 'decisive_battles', {}).get(diplo_key, [])
    for d in decisive_records:
        if d.get("winner") == nation_a:
            decisive_score += 10
        elif d.get("winner") == nation_b:
            decisive_score -= 10
    decisive_score = max(-20, min(20, decisive_score))

    # Capital score (cap ±30)
    capital_score = 0
    a_capital = NATION_CAPITALS.get(nation_a)
    b_capital = NATION_CAPITALS.get(nation_b)

    if b_capital and b_capital in world.regions:
        b_cap_region = world.regions[b_capital]
        if b_cap_region.controller == nation_a:
            capital_score += 20
        elif any(m.nation == nation_a and m.location == b_capital
                 for m in world.marshals.values()):
            capital_score += 10  # Contested
    if a_capital and a_capital in world.regions:
        a_cap_region = world.regions[a_capital]
        if a_cap_region.controller == nation_b:
            capital_score -= 20
        elif any(m.nation == nation_b and m.location == a_capital
                 for m in world.marshals.values()):
            capital_score -= 10  # Contested
    capital_score = max(-30, min(30, capital_score))

    total = territory_score + battle_score + decisive_score + capital_score
    total = int(max(-100, min(100, total)))

    if return_components:
        return {
            "total": total,
            "territory": int(territory_score),
            "battles": int(battle_score),
            "decisive": int(decisive_score),
            "capital": int(capital_score),
        }
    return total


def apply_war_score_decay(world) -> None:
    """Apply war score decay: -2/turn when no battles for 3+ turns.

    Decisive bonuses do NOT decay. Only the battle_score portion decays
    by clearing old battle records. Also prunes battle records older than
    10 turns (R1a).
    """
    war_scores = getattr(world, 'war_scores', {})
    battle_records = getattr(world, 'battle_records', {})

    # R1a: Prune battle records older than 10 turns
    for diplo_key in list(battle_records.keys()):
        records = battle_records[diplo_key]
        battle_records[diplo_key] = [
            r for r in records
            if world.current_turn - r.get("turn", 0) <= 10
        ]

    for diplo_key in list(war_scores.keys()):
        records = battle_records.get(diplo_key, [])
        if not records:
            # No battles ever — decay toward 0
            current = war_scores.get(diplo_key, 0)
            if current > 0:
                war_scores[diplo_key] = max(0, current - 2)
            elif current < 0:
                war_scores[diplo_key] = min(0, current + 2)
            continue

        # Check if last battle was 3+ turns ago
        last_battle_turn = max(r.get("turn", 0) for r in records)
        turns_since = world.current_turn - last_battle_turn
        if turns_since >= 3:
            current = war_scores.get(diplo_key, 0)
            if current > 0:
                war_scores[diplo_key] = max(0, current - 2)
            elif current < 0:
                war_scores[diplo_key] = min(0, current + 2)


def recalculate_war_scores(world) -> None:
    """Recalculate war scores for all active wars."""
    war_scores = getattr(world, 'war_scores', {})
    for diplo_key, state in world.diplomatic_states.items():
        if state == "WAR":
            parts = diplo_key.split("|")
            if len(parts) == 2:
                score = calculate_war_score(parts[0], parts[1], world)
                war_scores[diplo_key] = int(score)
    world.war_scores = war_scores


def get_war_score_for(world, nation: str, opponent: str) -> int:
    """Get war score from a specific nation's perspective.

    Positive = nation is winning, negative = nation is losing.
    The stored war_score is from alphabetically-first nation's perspective.
    Canonical helper — all callers should use this instead of manual flipping.
    """
    diplo_key = world._make_diplo_key(nation, opponent)
    raw_score = getattr(world, 'war_scores', {}).get(diplo_key, 0)

    # If nation is alphabetically second, flip the sign
    parts = diplo_key.split("|")
    if len(parts) == 2 and parts[0] != nation:
        raw_score = -raw_score

    return int(raw_score)


def cleanup_war_end(world, diplo_key: str) -> None:
    """Clean up war-related data when a war ends (R1b, R49, R47/R30).

    Called on WAR→ARMISTICE/PEACE transitions.
    - Clears battle_records, decisive_battles, war_scores for the pair
    - Resets war_exhaustion for both nations to 0
    - Cancels PURSUE/MOVE_TO strategic orders targeting the now-peaceful nation's marshals
    """
    # R1b: Clear war data
    battle_records = getattr(world, 'battle_records', {})
    decisive_battles = getattr(world, 'decisive_battles', {})
    war_scores = getattr(world, 'war_scores', {})

    battle_records.pop(diplo_key, None)
    decisive_battles.pop(diplo_key, None)
    war_scores.pop(diplo_key, None)

    # R49: Reset war_exhaustion for both nations
    parts = diplo_key.split("|")
    war_exhaustion = getattr(world, 'war_exhaustion', {})
    if len(parts) == 2:
        war_exhaustion.pop(parts[0], None)
        war_exhaustion.pop(parts[1], None)

    # R69: Clear cascade_triggered entries for this war pair
    cascade_triggered = getattr(world, 'cascade_triggered', set())
    to_remove = {key for key in cascade_triggered if diplo_key in key}
    cascade_triggered -= to_remove
    world.cascade_triggered = cascade_triggered

    # R110: Clear stalemate counters for the war pair nations
    stalemate_counters = getattr(world, 'ai_stalemate_counters', {})
    if len(parts) == 2:
        stalemate_counters.pop(parts[0], None)
        stalemate_counters.pop(parts[1], None)
    world.ai_stalemate_counters = stalemate_counters

    # R47/R30: Cancel PURSUE/MOVE_TO orders targeting the now-peaceful nation's marshals
    if len(parts) == 2:
        nation_a, nation_b = parts
        # Collect marshal names for each nation
        nation_a_marshals = {m.name for m in world.marshals.values() if m.nation == nation_a}
        nation_b_marshals = {m.name for m in world.marshals.values() if m.nation == nation_b}

        for marshal in world.marshals.values():
            order = getattr(marshal, 'strategic_order', None)
            if not order:
                continue
            cmd_type = getattr(order, 'command_type', '')
            if cmd_type not in ("PURSUE", "MOVE_TO"):
                continue
            target_type = getattr(order, 'target_type', '')
            if target_type != "marshal":
                continue
            target_name = getattr(order, 'target', '')
            # Cancel if marshal belongs to nation_a and target to nation_b, or vice versa
            if marshal.nation == nation_a and target_name in nation_b_marshals:
                marshal.strategic_order = None
            elif marshal.nation == nation_b and target_name in nation_a_marshals:
                marshal.strategic_order = None


# ═══════════════════════════════════════════════════════
# ACCEPTANCE FORMULA (§6)
# ═══════════════════════════════════════════════════════

def calculate_acceptance(proposal: Dict, world) -> Dict:
    """Calculate acceptance score for a diplomatic proposal.

    Args:
        proposal: {
            "type": str (peace/alliance/vassalage/armistice_losing/armistice_winning/
                         open_borders/non_aggression),
            "proposer_nation": str,
            "target_nation": str,
            "sweeteners": list of {"type": str, "value": int/float},
            "demands": list of {"type": str, "value": int/float},
            "clauses": list of str (special clause keys),
        }
        world: WorldState

    Returns:
        {"score": int, "outcome": str, "components": dict, "feedback": str}
    """
    proposal_type = proposal.get("type", "peace")
    proposer = proposal.get("proposer_nation", "France")
    target = proposal.get("target_nation", "")

    # Get diplomats
    diplomats = getattr(world, 'diplomats', {})
    proposer_diplomat = diplomats.get(proposer)
    target_diplomat = diplomats.get(target)

    proposer_skill = proposer_diplomat.skill if proposer_diplomat else 5
    target_skill = target_diplomat.skill if target_diplomat else 5
    target_personality = target_diplomat.personality if target_diplomat else "loyalist"

    # ── Base Disposition ──
    base = BASE_DISPOSITION.get(proposal_type, 30)

    # ── War Score Modifier ──
    diplo_key = world._make_diplo_key(proposer, target)
    war_score = getattr(world, 'war_scores', {}).get(diplo_key, 0)
    # Positive war_score means first-alphabetically nation is winning
    # Adjust sign so positive = proposer winning
    parts = diplo_key.split("|")
    if len(parts) == 2 and parts[0] == target:
        war_score = -war_score  # Flip: target is first in key, so proposer winning = negative in storage
    war_score_mod = war_score * 0.3

    # ── Relation Modifier ──
    relation = world.nation_relations.get(diplo_key, 0)
    relation_mod = relation / 2

    # ── Threat Modifier (COALITION_SPEC §6a) ──
    threat = int(getattr(world, 'threat_level', 0))
    threat_mod = 0
    if proposer == "France":
        threat_mod = threat * -0.3
    elif target != "France":
        threat_mod = threat * 0.2

    # ── Coalition Loyalty Penalty (COALITION_SPEC §6a/§6c) ──
    from backend.game_logic.coalition import get_coalition_loyalty_penalty
    coalition_penalty = get_coalition_loyalty_penalty(target, world)

    # ── Deal Balance ──
    sweetener_total = 0.0
    for s in proposal.get("sweeteners", []):
        stype = s.get("type", "")
        svalue = s.get("value", 0)
        rate = SWEETENER_VALUES.get(stype, 0)
        if isinstance(rate, (int, float)) and rate < 1:
            sweetener_total += svalue * rate
        else:
            sweetener_total += rate * svalue if svalue else rate
    sweetener_total = min(SWEETENER_CAP, sweetener_total)

    demand_total = 0.0
    for d in proposal.get("demands", []):
        dtype = d.get("type", "")
        dvalue = d.get("value", 0)
        rate = DEMAND_VALUES.get(dtype, 0)
        if isinstance(rate, (int, float)) and abs(rate) < 1:
            demand_total += dvalue * rate
        else:
            demand_total += rate * dvalue if dvalue else rate

    deal_balance = sweetener_total + demand_total

    # ── Diplomat Skill Bonus ──
    diplomat_skill_bonus = (proposer_skill - target_skill) * 2

    # ── Personality Modifier ──
    peace_mod, harsh_mod = PERSONALITY_MODIFIERS.get(target_personality, (0, 0))
    is_harsh = proposal_type in ("vassalage",)
    # Also check if demands outweigh sweeteners significantly
    if demand_total < -10:
        is_harsh = True
    personality_mod = harsh_mod if is_harsh else peace_mod

    # ── Military Supremacy (§6b.1) ──
    military_supremacy = 0
    from backend.models.region import NATION_CAPITALS
    target_capital = NATION_CAPITALS.get(target)
    if war_score >= 70 and target_capital:
        cap_region = world.regions.get(target_capital)
        if cap_region and cap_region.controller == proposer:
            military_supremacy = 25

    # ── Battlefield Diplomacy (COALITION_SPEC R3) ──
    battlefield_diplomacy = 0
    if (war_score > 20
            and proposal_type in ("peace", "armistice_losing", "armistice_winning")
            and military_supremacy == 0):  # Does NOT stack with Military Supremacy
        battlefield_diplomacy = 10

    # Use whichever is higher (they don't stack)
    situational_bonus = max(military_supremacy, battlefield_diplomacy)

    # ── Special Desire Bonus (§6d) ──
    # Nation-specific acceptance bonuses when proposal addresses core interests
    special_desire_bonus = 0
    clauses = proposal.get("clauses", [])
    target_specials = SPECIAL_BONUSES.get(target, {})
    # Check both string clauses and dict clauses
    for clause in clauses:
        if isinstance(clause, str):
            if clause in target_specials:
                special_desire_bonus += target_specials[clause]
        elif isinstance(clause, dict):
            # Handle structured clause dicts: {"type": "territory", "region": "Saxony"}
            ctype = clause.get("type", "")
            cregion = clause.get("region", "")
            # Match territory_X patterns
            clause_key = f"{ctype}_{cregion.lower()}" if cregion else ctype
            if clause_key in target_specials:
                special_desire_bonus += target_specials[clause_key]
            elif ctype in target_specials:
                special_desire_bonus += target_specials[ctype]

    # ── Escalating Harshness (DD8-4) ──
    harshness_bonus = 0
    prev_treaties = getattr(world, 'previous_treaties', {}).get(diplo_key, [])
    for treaty in prev_treaties:
        if treaty.get("harshness", 0) > 0.3:
            harshness_bonus = 5
            break

    # ── Sum ──
    raw_score = (
        base
        + war_score_mod
        + relation_mod
        + threat_mod
        + coalition_penalty
        + deal_balance
        + diplomat_skill_bonus
        + personality_mod
        + situational_bonus
        + special_desire_bonus
        + harshness_bonus
    )

    score = int(round(raw_score))

    if score >= 50:
        outcome = "ACCEPT"
    elif score >= 30:
        outcome = "COUNTER_OFFER"
    else:
        outcome = "REJECT"

    # Build components dict for debugging/display
    components = {
        "base_disposition": base,
        "war_score_modifier": round(war_score_mod, 1),
        "relation_modifier": round(relation_mod, 1),
        "threat_modifier": round(threat_mod, 1),
        "coalition_penalty": int(coalition_penalty),
        "deal_balance": round(deal_balance, 1),
        "diplomat_skill_bonus": diplomat_skill_bonus,
        "personality_modifier": personality_mod,
        "military_supremacy": military_supremacy,
        "battlefield_diplomacy": battlefield_diplomacy,
        "special_desire_bonus": special_desire_bonus,
        "harshness_bonus": harshness_bonus,
    }

    # ── Feedback (§6f) ──
    feedback = _generate_feedback(outcome, components)

    return {
        "score": int(score),
        "outcome": outcome,
        "components": components,
        "feedback": feedback,
    }


def _generate_feedback(outcome: str, components: Dict) -> str:
    """Generate natural-language feedback based on formula components."""
    # Find largest positive and negative components
    trackable = {
        "base_disposition", "war_score_modifier", "relation_modifier",
        "threat_modifier", "deal_balance", "diplomat_skill_bonus",
        "personality_modifier", "special_desire_bonus",
    }

    largest_positive = ("", 0)
    largest_negative = ("", 0)
    second_negative = ("", 0)

    for key in trackable:
        val = components.get(key, 0)
        if val > largest_positive[1]:
            largest_positive = (key, val)
        if val < largest_negative[1]:
            second_negative = largest_negative
            largest_negative = (key, val)
        elif val < second_negative[1]:
            second_negative = (key, val)

    proposer_name = "Talleyrand"  # Default for player feedback

    if outcome == "REJECT":
        key = largest_negative[0]
        phrase = FEEDBACK_STRINGS.get(key, {}).get("negative", "unknown factors")
        return f"{proposer_name} reports the key obstacle was {phrase}."
    elif outcome == "COUNTER_OFFER":
        key = second_negative[0] if second_negative[0] else largest_negative[0]
        phrase = FEEDBACK_STRINGS.get(key, {}).get("negative", "unresolved concerns")
        return f"The sticking point appears to be {phrase}."
    else:  # ACCEPT
        key = largest_positive[0]
        phrase = FEEDBACK_STRINGS.get(key, {}).get("positive", "favorable conditions")
        return f"The decisive factor was {phrase}."


# ═══════════════════════════════════════════════════════
# DP ECONOMY (§4)
# ═══════════════════════════════════════════════════════

def calculate_dp(diplomat, authority: int, controls_capital: bool) -> int:
    """Calculate DP generation for a nation.

    Args:
        diplomat: DiplomaticRepresentative (or None)
        authority: Nation's authority level (0-100)
        controls_capital: Whether nation controls its capital

    Returns:
        DP per turn (1-5)
    """
    base = 2
    skill_bonus = 1 if diplomat and diplomat.skill >= 10 else 0
    authority_bonus = 1 if authority >= 60 else (-1 if authority < 30 else 0)
    capital_penalty = -1 if not controls_capital else 0
    return max(1, min(5, base + skill_bonus + authority_bonus + capital_penalty))


def get_dp_cost(action_type: str, diplomat_skill: int = 10, transition_base: int = 0) -> int:
    """Get DP cost for a diplomatic action, adjusted for skill.

    Base costs from §4b. Skill penalty: +1 if skill 4-6, +2 if skill < 4.
    transition_base: if provided, use the higher of table cost and cumulative
    jump cost (from get_transition_dp_cost). This ensures multi-step jumps
    (e.g. PEACE→ALLIANCE) charge the full intermediate cost.
    """
    base_costs = {
        "propose_peace": 2,
        "propose_alliance": 2,
        "propose_non_aggression": 1,
        "propose_open_borders": 1,
        "propose_downgrade": 1,
        "demand_vassalage": 3,
        "offer_trade": 1,
        "respond": 0,
        "cancel_treaty": 1,
        "invest_vassal": 1,
        "declare_war": 1,
    }
    base = max(base_costs.get(action_type, 1), transition_base)

    # Skill penalty
    if diplomat_skill < 4:
        base += 2
    elif diplomat_skill <= 6:
        base += 1

    return base


# ═══════════════════════════════════════════════════════
# NATION AUTHORITY (AI nations)
# ═══════════════════════════════════════════════════════

def modify_nation_authority(world, nation: str, delta: int) -> int:
    """Modify a nation's authority. Clamped 0-100."""
    auth = getattr(world, 'nation_authority', {})
    current = auth.get(nation, 60)
    new_val = max(0, min(100, current + delta))
    auth[nation] = new_val
    return new_val


# ═══════════════════════════════════════════════════════
# WAR DECLARATION & CASCADE
# ═══════════════════════════════════════════════════════

def declare_war(world, aggressor: str, target: str) -> Dict:
    """Declare war: transition to WAR, apply penalties, handle cascade.

    Returns:
        {"success": bool, "message": str, "cascade": list of cascade entries,
         "dp_cost": int, "relation_changes": list}
    """
    diplo_key = world._make_diplo_key(aggressor, target)
    current_state = world.diplomatic_states.get(diplo_key, "PEACE")

    if current_state == "WAR":
        return {"success": False, "message": f"{aggressor} is already at war with {target}."}

    # R99: Block war declaration during armistice cooldown
    armistice_cooldown = getattr(world, 'armistice_cooldowns', {}).get(diplo_key, 0)
    if armistice_cooldown > 0:
        return {
            "success": False,
            "message": f"Armistice cooldown in effect with {target} ({armistice_cooldown} turns remaining). War cannot be declared."
        }

    # Transition to WAR
    world.diplomatic_states[diplo_key] = "WAR"

    # R97: Remove active treaty (alliance clauses must stop during war)
    active_treaties = getattr(world, 'active_treaties', {})
    active_treaties.pop(diplo_key, None)

    # Penalties
    relation_changes = []
    world.modify_nation_relation(aggressor, target, -30)
    relation_changes.append({"nations": (aggressor, target), "delta": -30})

    # -15 with ALL other nations
    all_nations = [world.player_nation] + list(getattr(world, 'enemy_nations', []))
    for nation in all_nations:
        if nation != aggressor and nation != target:
            world.modify_nation_relation(aggressor, nation, -15)
            relation_changes.append({"nations": (aggressor, nation), "delta": -15})

    # Coalition threat: +20 for France declaring war (§2a)
    if aggressor == world.player_nation:
        from backend.game_logic.coalition import add_threat
        add_threat(world, 20, "war_declaration")

    # Authority changes for AI nations
    nation_auth = getattr(world, 'nation_authority', {})
    if target in nation_auth:
        # Being attacked doesn't change authority directly
        pass

    # DP cost: 1
    dp_cost = WAR_DP_COST

    # Log event
    world.log_event({
        "type": "war_declaration",
        "aggressor": aggressor,
        "target": target,
        "previous_state": current_state,
    })

    # ── DEFENSIVE_ALLIANCE CASCADE ──
    cascade = _process_war_cascade(world, aggressor, target)

    # Notification: war declared (Session 8C)
    from backend.notifications import (
        create_notification, NotificationPriority, WAR_DECLARED,
    )
    world.notifications.add(create_notification(
        WAR_DECLARED,
        NotificationPriority.HIGH,
        f"War with {target}!" if aggressor == world.player_nation else f"{aggressor} Declares War!",
        f"{aggressor} has declared war on {target}.",
        int(world.current_turn),
    ))

    # Dispatch event (Session 8D)
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "diplomatic_war_declared",
                        {"nation": aggressor, "target": target},
                        "partial_on_nation")

    messages = [f"{aggressor} declares war on {target}!"]
    for c in cascade:
        messages.append(f"{c['defender']} enters the war against {aggressor} in defense of {c['ally']}!")

    return {
        "success": True,
        "message": " ".join(messages),
        "cascade": cascade,
        "dp_cost": dp_cost,
        "relation_changes": relation_changes,
    }


def _process_war_cascade(world, aggressor: str, target: str, processed: set = None) -> List[Dict]:
    """Process DEFENSIVE_ALLIANCE / ALLIANCE cascade when war is declared.

    Loop protection: max cascade depth = number of nations.
    """
    if processed is None:
        processed = {aggressor, target}

    cascade = []
    all_nations = [world.player_nation] + list(getattr(world, 'enemy_nations', []))

    for nation in all_nations:
        if nation in processed:
            continue

        # Check if this nation has DEFENSIVE_ALLIANCE or ALLIANCE with the target
        state = world.get_diplomatic_state(nation, target)
        if state in ("DEFENSIVE_ALLIANCE", "ALLIANCE"):
            # Check if already at war with aggressor
            if not world.is_at_war(nation, aggressor):
                # Force WAR — bypasses armistice cooldowns
                war_key = world._make_diplo_key(nation, aggressor)
                world.diplomatic_states[war_key] = "WAR"
                processed.add(nation)

                # R97: Remove active treaty for the cascading pair
                active_treaties = getattr(world, 'active_treaties', {})
                active_treaties.pop(war_key, None)

                # R100: Apply relation penalty for cascaded war
                world.modify_nation_relation(aggressor, nation, -20)

                cascade.append({
                    "defender": nation,
                    "ally": target,
                    "previous_state": state,
                })

                world.log_event({
                    "type": "defensive_cascade",
                    "defender": nation,
                    "ally": target,
                    "against": aggressor,
                })

                # Notification: alliance cascade (Session 8C)
                from backend.notifications import (
                    create_notification, NotificationPriority, ALLIANCE_CASCADE_WAR,
                )
                world.notifications.add(create_notification(
                    ALLIANCE_CASCADE_WAR,
                    NotificationPriority.HIGH,
                    f"{nation} Enters War!",
                    f"{nation} enters the war via alliance with {target}.",
                    int(world.current_turn),
                ))

                # Dispatch event (Session 8D)
                from backend.game_logic.dispatch import queue_dispatch_event
                queue_dispatch_event(world, "diplomatic_alliance_cascade",
                                    {"nation": nation, "ally": target},
                                    "partial_on_nation")

                # Recursive cascade: nation's allies may also join
                sub_cascade = _process_war_cascade(world, aggressor, nation, processed)
                cascade.extend(sub_cascade)

    return cascade


# ═══════════════════════════════════════════════════════
# DOWNGRADE TRANSITIONS (§5b.1)
# ═══════════════════════════════════════════════════════

def execute_downgrade(world, nation_a: str, nation_b: str) -> Dict:
    """Execute a one-step downgrade between two nations.

    Returns:
        {"success": bool, "message": str, "new_state": str, "dp_cost": int}
    """
    diplo_key = world._make_diplo_key(nation_a, nation_b)
    current_state = world.diplomatic_states.get(diplo_key, "PEACE")

    # Find next downgrade step
    if current_state not in _DOWNGRADE_ORDER:
        return {"success": False, "message": f"Cannot downgrade from {current_state}."}

    idx = _DOWNGRADE_ORDER.index(current_state)
    if idx >= len(_DOWNGRADE_ORDER) - 1:
        return {"success": False, "message": f"Already at minimum downgradable state ({current_state})."}

    new_state = _DOWNGRADE_ORDER[idx + 1]
    penalties = DOWNGRADE_PENALTIES.get((current_state, new_state))
    if not penalties:
        return {"success": False, "message": f"No downgrade path from {current_state} to {new_state}."}

    # Apply
    world.diplomatic_states[diplo_key] = new_state

    # R45: Remove active treaty on downgrade (treaty was for the old state)
    active_treaties = getattr(world, 'active_treaties', {})
    active_treaties.pop(diplo_key, None)

    # Relation penalties
    world.modify_nation_relation(nation_a, nation_b, penalties["relation_target"])
    all_nations = [world.player_nation] + list(getattr(world, 'enemy_nations', []))
    if penalties["relation_all"] != 0:
        for nation in all_nations:
            if nation != nation_a and nation != nation_b:
                world.modify_nation_relation(nation_a, nation, penalties["relation_all"])

    # Coalition threat from downgrade (§2a)
    threat_amount = penalties.get("threat", 0)
    if threat_amount > 0 and nation_a == world.player_nation:
        from backend.game_logic.coalition import add_threat
        add_threat(world, threat_amount, "diplomatic_downgrade")

    world.log_event({
        "type": "diplomatic_downgrade",
        "from_state": current_state,
        "to_state": new_state,
        "nation_a": nation_a,
        "nation_b": nation_b,
    })

    return {
        "success": True,
        "message": f"Diplomatic relations between {nation_a} and {nation_b} downgraded: {current_state} → {new_state}.",
        "new_state": new_state,
        "dp_cost": penalties["dp_cost"],
    }


def check_auto_downgrade(world) -> List[Dict]:
    """Check for automatic downgrades when relations stay 30+ below threshold for 5 turns.

    Returns list of downgrade events for Morning Dispatch.
    """
    turns_below = getattr(world, 'turns_below_threshold', {})
    events = []

    for diplo_key, state in list(world.diplomatic_states.items()):
        threshold = STATE_RELATION_THRESHOLDS.get(state)
        if threshold is None:
            # State not subject to auto-downgrade
            turns_below.pop(diplo_key, None)
            continue

        relation = world.nation_relations.get(diplo_key, 0)
        gap = threshold - relation  # Positive = below threshold

        if gap >= 30:
            turns_below[diplo_key] = turns_below.get(diplo_key, 0) + 1

            # Warn at turn 3 (2 turns before downgrade)
            if turns_below[diplo_key] == 3:
                parts = diplo_key.split("|")
                events.append({
                    "type": "downgrade_warning",
                    "nations": parts,
                    "state": state,
                    "turns_remaining": 2,
                    "message": f"Relations between {parts[0]} and {parts[1]} are deteriorating. "
                               f"{state} may collapse in 2 turns.",
                })

            # Auto-downgrade at turn 5
            if turns_below[diplo_key] >= 5:
                parts = diplo_key.split("|")
                # Apply half penalties
                idx = _DOWNGRADE_ORDER.index(state) if state in _DOWNGRADE_ORDER else -1
                if idx >= 0 and idx < len(_DOWNGRADE_ORDER) - 1:
                    new_state = _DOWNGRADE_ORDER[idx + 1]
                    penalties = DOWNGRADE_PENALTIES.get((state, new_state))
                    if penalties:
                        world.diplomatic_states[diplo_key] = new_state
                        # Half penalties
                        world.modify_nation_relation(
                            parts[0], parts[1], penalties["relation_target"] // 2)
                        turns_below[diplo_key] = 0  # Reset counter

                        events.append({
                            "type": "auto_downgrade",
                            "nations": parts,
                            "from_state": state,
                            "to_state": new_state,
                            "message": f"Relations between {parts[0]} and {parts[1]} have collapsed: "
                                       f"{state} → {new_state}.",
                        })

                        world.log_event({
                            "type": "auto_downgrade",
                            "from_state": state,
                            "to_state": new_state,
                            "nation_a": parts[0],
                            "nation_b": parts[1],
                        })

                        # R80: Dispatch event + notification for auto-downgrade
                        from backend.game_logic.dispatch import queue_dispatch_event
                        queue_dispatch_event(world, "diplomatic_auto_downgrade", {
                            "nation_a": parts[0],
                            "nation_b": parts[1],
                            "from_state": state,
                            "to_state": new_state,
                        }, "always")

                        from backend.notifications import (
                            create_notification, NotificationPriority, DIPLO_AUTO_DOWNGRADE,
                        )
                        world.notifications.add(create_notification(
                            DIPLO_AUTO_DOWNGRADE,
                            NotificationPriority.NORMAL,
                            "Relations Deteriorated",
                            f"{parts[0]}-{parts[1]}: {state} → {new_state}.",
                            int(world.current_turn),
                        ))
        else:
            # Above threshold or gap < 30 — reset counter
            turns_below.pop(diplo_key, None)

    world.turns_below_threshold = turns_below
    return events


# ═══════════════════════════════════════════════════════
# BATTLE RECORDING
# ═══════════════════════════════════════════════════════

def record_battle(world, attacker_nation: str, defender_nation: str,
                  winner_nation: str, attacker_casualties: int,
                  defender_casualties: int) -> None:
    """Record a battle result for war score calculation.

    Also checks for decisive battle (casualty ratio > 2:1 AND total > 10,000).
    Max 2 decisive bonuses per war.
    """
    if not world.is_at_war(attacker_nation, defender_nation):
        return  # Only record battles between nations at war

    diplo_key = world._make_diplo_key(attacker_nation, defender_nation)

    # Ensure data structures exist
    if not hasattr(world, 'battle_records'):
        world.battle_records = {}
    if not hasattr(world, 'decisive_battles'):
        world.decisive_battles = {}

    if diplo_key not in world.battle_records:
        world.battle_records[diplo_key] = []
    if diplo_key not in world.decisive_battles:
        world.decisive_battles[diplo_key] = []

    record = {
        "turn": world.current_turn,
        "winner": winner_nation,
        "attacker": attacker_nation,
        "defender": defender_nation,
        "attacker_casualties": int(attacker_casualties),
        "defender_casualties": int(defender_casualties),
    }
    world.battle_records[diplo_key].append(record)

    # Check for decisive battle
    total_casualties = attacker_casualties + defender_casualties
    if total_casualties > 10000:
        if attacker_casualties > 0 and defender_casualties > 0:
            ratio = max(attacker_casualties, defender_casualties) / min(attacker_casualties, defender_casualties)
            if ratio > 2.0:
                # Max 2 decisive bonuses per war
                if len(world.decisive_battles[diplo_key]) < 2:
                    world.decisive_battles[diplo_key].append({
                        "turn": world.current_turn,
                        "winner": winner_nation,
                        "total_casualties": int(total_casualties),
                        "ratio": round(ratio, 1),
                    })


# ═══════════════════════════════════════════════════════
# MOVEMENT VALIDATION HELPERS
# ═══════════════════════════════════════════════════════

def can_enter_territory(world, marshal_nation: str, region_controller: str) -> bool:
    """Check if a nation's marshal can enter territory controlled by another nation.

    Returns True if movement is allowed.
    """
    if not region_controller:
        return True  # Unclaimed territory
    if marshal_nation == region_controller:
        return True  # Own territory

    state = world.get_diplomatic_state(marshal_nation, region_controller)

    # WAR — can enter (but must attack if enemies present)
    if state == "WAR":
        return True

    # OPEN_BORDERS and above — can enter
    if state in OPEN_MOVEMENT_STATES:
        return True

    # PEACE, NON_AGGRESSION, ARMISTICE — cannot enter
    return False


# ═══════════════════════════════════════════════════════
# ADVANCE_TURN DIPLOMATIC PROCESSING (§7f)
# ═══════════════════════════════════════════════════════

def process_diplomacy_turn(world) -> List[Dict]:
    """Process diplomatic events during advance_turn.

    Implements §7f processing order (items this session covers):
    1. DP regeneration
    4. War score recalculation
    8. Armistice expiration (minimum 3 turns)
    9. Cooldown decrements
    10. Trade income (handled separately in income phase)
    13. Automatic downgrade check

    Returns list of diplomatic events for Morning Dispatch.
    """
    events = []

    # ── 1. DP regeneration ──
    _process_dp_regen(world)

    # ── 2. Mission DP deduction (Session 3) ──
    mission_events = _process_mission_dp(world)
    events.extend(mission_events)

    # ── 3. Mission effects (Session 3) ──
    effect_events = _process_mission_effects(world)
    events.extend(effect_events)

    # ── 4. War score recalculation ──
    recalculate_war_scores(world)
    apply_war_score_decay(world)

    # TODO: 5. Defection cascade check (Session 5)
    # TODO: 6. Vassal loyalty processing (Session 5)
    # TODO: 7. Vassal rebellion check (Session 5)

    # ── 8. Armistice expiration ──
    armistice_events = _process_armistice_expiration(world)
    events.extend(armistice_events)

    # ── 9. Cooldown decrements ──
    _decrement_cooldowns(world)

    # TODO: 9a. War exhaustion update (Session 7 — Coalition)
    # TODO: 9b. Threat accumulation (Session 7 — Coalition)
    # TODO: 9c. Threat decay (Session 7 — Coalition)
    # TODO: 9d. Coalition check (Session 7 — Coalition)

    # 10. Trade income — handled in process_trade_income() called from advance_turn income phase

    # TODO: 11. Treaty obligation checks (Session 3)
    # TODO: 12. Continental System check (Session 3)

    # ── 13. Automatic downgrade check ──
    downgrade_events = check_auto_downgrade(world)
    events.extend(downgrade_events)

    # TODO: 14. Proactive suggestion evaluation (Session 4)

    # ── Nation authority changes ──
    _process_nation_authority(world)

    return events


def _is_nation_eliminated(world, nation: str) -> bool:
    """R81: Check if a nation is eliminated (0 regions).

    Marshals are guaranteed removed by _eliminate_nation(), so region check suffices.
    """
    return not any(
        getattr(r, 'controller', '') == nation
        for r in world.regions.values()
    )


def _process_dp_regen(world) -> None:
    """Regenerate DP for all nations. DP does NOT accumulate — reset each turn."""
    from backend.models.region import NATION_CAPITALS
    diplomats = getattr(world, 'diplomats', {})
    nation_auth = getattr(world, 'nation_authority', {})

    all_nations = [world.player_nation] + list(getattr(world, 'enemy_nations', []))
    for nation in all_nations:
        # R81: Skip eliminated nations (0 regions + 0 marshals)
        if nation != world.player_nation and _is_nation_eliminated(world, nation):
            continue
        diplomat = diplomats.get(nation)
        if nation == world.player_nation:
            authority = world.authority_tracker.authority if hasattr(world, 'authority_tracker') else 60
        else:
            authority = nation_auth.get(nation, 60)

        capital = NATION_CAPITALS.get(nation)
        controls_capital = False
        if capital and capital in world.regions:
            controls_capital = world.regions[capital].controller == nation

        dp = calculate_dp(diplomat, authority, controls_capital)

        if nation == world.player_nation:
            world.diplomatic_points = int(dp)
        else:
            # Store AI DP for AI diplomacy consumption
            if not hasattr(world, 'nation_dp'):
                world.nation_dp = {}
            world.nation_dp[nation] = int(dp)


def process_trade_income(world) -> Dict[str, int]:
    """Calculate and apply trade income from diplomatic states.

    Returns dict of {nation: trade_income} for display.
    """
    trade_by_nation = {}
    for pair_key, state in world.diplomatic_states.items():
        trade = TRADE_INCOME.get(state, 0)
        if trade > 0:
            parts = pair_key.split("|")
            if len(parts) == 2:
                nation_a, nation_b = parts
                trade_by_nation[nation_a] = trade_by_nation.get(nation_a, 0) + trade
                trade_by_nation[nation_b] = trade_by_nation.get(nation_b, 0) + trade

    # Apply to nation_gold
    for nation, income in trade_by_nation.items():
        if nation in world.nation_gold:
            world.nation_gold[nation] += int(income)

    return trade_by_nation


def _process_armistice_expiration(world) -> List[Dict]:
    """Handle armistice expirations (R5a).

    Tracks turns in ARMISTICE state. After 5 turns:
    - If relations >= -60: transition to PEACE, call cleanup_war_end
    - If relations < -60: transition back to WAR

    Returns list of dispatch events.
    """
    events = []
    armistice_turns = getattr(world, 'armistice_turns', {})

    for diplo_key, state in list(world.diplomatic_states.items()):
        if state != "ARMISTICE":
            # Not in armistice — remove tracking if present
            armistice_turns.pop(diplo_key, None)
            continue

        # Increment turn counter
        armistice_turns[diplo_key] = armistice_turns.get(diplo_key, 0) + 1
        turns = armistice_turns[diplo_key]

        if turns < 5:
            continue

        # Armistice expired — check relations to determine outcome
        parts = diplo_key.split("|")
        if len(parts) != 2:
            continue
        nation_a, nation_b = parts
        relation = world.nation_relations.get(diplo_key, 0)

        if relation >= -60:
            # Transition to PEACE
            world.diplomatic_states[diplo_key] = "PEACE"
            cleanup_war_end(world, diplo_key)
            events.append({
                "type": "armistice_expired_peace",
                "nations": [nation_a, nation_b],
                "message": f"The armistice between {nation_a} and {nation_b} has concluded. Peace declared.",
            })
        else:
            # Relations too hostile — back to WAR
            world.diplomatic_states[diplo_key] = "WAR"
            events.append({
                "type": "armistice_expired_war",
                "nations": [nation_a, nation_b],
                "message": f"The armistice between {nation_a} and {nation_b} has collapsed. War resumes.",
            })

        # Clear tracking
        armistice_turns.pop(diplo_key, None)

    world.armistice_turns = armistice_turns
    return events


def _decrement_cooldowns(world) -> None:
    """Decrement armistice cooldowns by 1 per turn. Remove expired ones."""
    cooldowns = getattr(world, 'armistice_cooldowns', {})
    expired = []
    for key in cooldowns:
        cooldowns[key] -= 1
        if cooldowns[key] <= 0:
            expired.append(key)
    for key in expired:
        del cooldowns[key]
    world.armistice_cooldowns = cooldowns


def _process_mission_dp(world) -> List[Dict]:
    """Deduct DP for active diplomatic mission. Pause if insufficient."""
    events = []
    mission = getattr(world, 'active_diplomatic_mission', None)
    if not mission or mission.get("completed"):
        return events

    from backend.game_logic.diplomatic_dialogue import MISSION_DP_COSTS
    cost = MISSION_DP_COSTS.get(mission["type"], 1)

    if mission.get("paused"):
        # Already paused — check if we can resume
        if world.diplomatic_points >= cost:
            # Resume
            mission["paused"] = False
            mission["paused_turns"] = 0
            world.diplomatic_points -= cost
            mission["turns_active"] = mission.get("turns_active", 0) + 1
        else:
            # Still can't afford — increment paused turns
            mission["paused_turns"] = mission.get("paused_turns", 0) + 1
    elif world.diplomatic_points >= cost:
        world.diplomatic_points -= cost
        mission["turns_active"] = mission.get("turns_active", 0) + 1
        mission["paused_turns"] = 0
    else:
        mission["paused"] = True
        mission["paused_turns"] = mission.get("paused_turns", 0) + 1
        events.append({
            "type": "diplomatic_mission_paused",
            "target": mission.get("target", ""),
            "message": "Talleyrand's diplomatic efforts curtailed — insufficient resources.",
        })
        # Dispatch event (Session 8D)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "diplomatic_mission_paused",
                            {"nation": mission.get("target", "")}, "player_mission")

    # Auto-cancel after 3+ consecutive paused turns
    paused_turns = mission.get("paused_turns", 0)
    if paused_turns >= 3:
        target = mission.get("target", "unknown")
        world.active_diplomatic_mission = None
        if getattr(world, 'talleyrand_state', '') == "ON_MISSION":
            world.talleyrand_state = "IDLE"
        events.append({
            "type": "diplomatic_mission_cancelled",
            "target": target,
            "message": f"Talleyrand's mission to {target} has collapsed after prolonged inactivity.",
        })
        # Dispatch event (Session 8D)
        from backend.game_logic.dispatch import queue_dispatch_event as _qde
        _qde(world, "diplomatic_mission_cancelled",
             {"nation": target}, "player_mission")

    return events


def _process_mission_effects(world) -> List[Dict]:
    """Apply per-turn mission effects."""
    events = []
    mission = getattr(world, 'active_diplomatic_mission', None)
    if not mission or mission.get("paused") or mission.get("completed"):
        return events

    from backend.game_logic.diplomatic_dialogue import MISSION_EFFECTS
    mission_type = mission.get("type", "")
    effects = MISSION_EFFECTS.get(mission_type, {})
    target = mission.get("target", "")

    if not target:
        return events

    # Get Talleyrand skill for bonus calculation
    player_nation = getattr(world, 'player_nation', 'France')
    diplomats = getattr(world, 'diplomats', {})
    talleyrand = diplomats.get(player_nation)  # Player's diplomat
    skill = talleyrand.skill if talleyrand else 5

    # Skill multiplier: 10 → 1.5x, 4-6 → 0.75x, else → 1.0x
    if skill >= 10:
        multiplier = 1.5
    elif 4 <= skill <= 6:
        multiplier = 0.75
    else:
        multiplier = 1.0

    # Apply relation change
    relation_change = effects.get("relation_change", 0)
    if relation_change:
        scaled = int(round(relation_change * multiplier))
        world.modify_nation_relation(player_nation, target, scaled)
        # Dispatch event (Session 8D)
        diplo_key = world._make_diplo_key(player_nation, target)
        current_relation = world.nation_relations.get(diplo_key, 0)
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "diplomatic_mission_progress",
                            {"nation": target, "value": int(current_relation)},
                            "player_mission")

    # GATHER_INTEL: auto-complete after duration turns
    duration = effects.get("duration")
    if duration and mission.get("turns_active", 0) >= duration:
        mission["completed"] = True
        world.talleyrand_state = "IDLE"
        events.append({
            "type": "diplomatic_mission_completed",
            "target": target,
            "mission_type": mission_type,
            "message": f"Talleyrand has completed his intelligence gathering on {target}.",
        })
        # Stub: no intel revealed yet (Session 4+)

    # UNDERMINE_ALLIANCE: stub (requires intel system)
    # COURT_NATION undermine chance: stub

    return events


def break_treaty(pair_key: str, breaker_nation: str, world) -> Dict:
    """Break an active treaty. Costs 1 DP.

    Returns:
        {"success": bool, "message": str, "relation_changes": list}
    """
    active_treaties = getattr(world, 'active_treaties', {})
    treaty = active_treaties.get(pair_key)
    if not treaty:
        return {"success": False, "message": "No active treaty to break."}

    # R101: Validate breaker is party to the treaty
    treaty_nations = treaty.get("nations", [])
    if treaty_nations and breaker_nation not in treaty_nations:
        return {"success": False, "message": f"{breaker_nation} is not a party to this treaty."}

    # Cost: 1 DP
    if world.diplomatic_points < 1:
        return {"success": False, "message": "Insufficient DP to break treaty (costs 1 DP)."}
    world.diplomatic_points -= 1

    treaty_type = treaty.get("type", "peace")
    nations = treaty.get("nations", [])
    other_nation = [n for n in nations if n != breaker_nation]
    other = other_nation[0] if other_nation else ""

    # Relation penalties
    relation_changes = []

    # Target: -30 (or -40 for alliance/defensive_alliance)
    penalty = -40 if treaty_type in ("alliance", "defensive_alliance") else -30
    world.modify_nation_relation(breaker_nation, other, penalty)
    relation_changes.append({"nations": (breaker_nation, other), "delta": penalty})

    # ALL nations: -10
    all_nations = [world.player_nation] + list(getattr(world, 'enemy_nations', []))
    for nation in all_nations:
        if nation != breaker_nation and nation != other:
            world.modify_nation_relation(breaker_nation, nation, -10)
            relation_changes.append({"nations": (breaker_nation, nation), "delta": -10})

    # Threat: +15 (or +25 for alliance)
    from backend.game_logic.coalition import add_threat
    threat_amount = 25 if treaty_type in ("alliance", "defensive_alliance") else 15
    add_threat(world, threat_amount, f"broke_{treaty_type}")

    # Post-break state: one level below broken treaty (E11)
    # IMPORTANT: Must include ALL diplomatic states. If you add a new
    # state to the diplomacy chain, add it here too. (Audit fix L-4)
    post_break_map = {
        "ALLIANCE": "NON_AGGRESSION",
        "DEFENSIVE_ALLIANCE": "OPEN_BORDERS",
        "NON_AGGRESSION": "PEACE",
        "OPEN_BORDERS": "PEACE",
        "PEACE": "PEACE",
        "VASSAL": "NON_AGGRESSION",  # Audit fix L-4
    }
    current_state = world.diplomatic_states.get(pair_key, "PEACE")
    new_state = post_break_map.get(current_state, "PEACE")
    world.diplomatic_states[pair_key] = new_state

    # Remove treaty
    del active_treaties[pair_key]

    # Log
    world.log_event({
        "type": "diplomatic_treaty_broken",
        "breaker": breaker_nation,
        "other": other,
        "treaty_type": treaty_type,
        "new_state": new_state,
    })

    # Notification: treaty broken (Session 8C)
    from backend.notifications import (
        create_notification, NotificationPriority, TREATY_BROKEN,
    )
    world.notifications.add(create_notification(
        TREATY_BROKEN,
        NotificationPriority.HIGH,
        f"Treaty Broken: {treaty_type}",
        f"{breaker_nation} has broken the {treaty_type} with {other}.",
        int(world.current_turn),
    ))

    # Dispatch event (Session 8D)
    from backend.game_logic.dispatch import queue_dispatch_event
    queue_dispatch_event(world, "diplomatic_treaty_broken",
                        {"nation": breaker_nation, "treaty_type": treaty_type},
                        "partial_on_nation")

    return {
        "success": True,
        "message": f"{breaker_nation} has broken the {treaty_type} with {other}! Relations plummet.",
        "new_state": new_state,
        "relation_changes": relation_changes,
    }


def _process_nation_authority(world) -> None:
    """Update AI nation authority based on events.

    Authority changes:
    - Losing battle: -3
    - Losing region: -5
    - Breaking treaty: -10
    - Winning battle: +2
    - Favorable treaty: +5

    Actual tracking of these events is done at the point they happen
    (combat resolution, territory changes, etc.) via modify_nation_authority().
    This function is a placeholder for any per-turn authority processing.
    """
    pass  # Authority changes happen at event time, not during turn processing


# ═══════════════════════════════════════════════════════
# AP/TURN CLAUSE VALIDATION (Phase 8 Session 5)
# ═══════════════════════════════════════════════════════

def validate_ap_clause(world, target: str) -> bool:
    """Validate that AP/turn demand is allowed. Requires war_score > 80."""
    player = getattr(world, 'player_nation', 'France')
    war_score = get_war_score_for(world, player, target)
    return war_score > 80


# ═══════════════════════════════════════════════════════
# CONTINENTAL SYSTEM (Phase 8 Session 5 §5d)
# ═══════════════════════════════════════════════════════

def apply_continental_system(world) -> None:
    """
    Apply Continental System trade penalties during income phase.

    Members: -75g/turn trade income cap with Britain.
    Total cap: 200g/turn across all members.
    PUPPET/SATELLITE vassals auto-join if lord runs system.
    """
    members = getattr(world, 'continental_system_members', [])
    if not members:
        return

    lord = getattr(world, 'player_nation', 'France')

    # Auto-join PUPPET/SATELLITE vassals
    from backend.game_logic.vassal import AUTONOMY_PUPPET, AUTONOMY_SATELLITE
    for vassal_name, state in world.vassals.items():
        if state["lord"] == lord:
            autonomy = state.get("autonomy", AUTONOMY_SATELLITE)
            if autonomy in (AUTONOMY_PUPPET, AUTONOMY_SATELLITE):
                if vassal_name not in members:
                    members.append(vassal_name)

    # Cap trade income between Britain and members
    total_blocked = 0
    max_total_cap = 200
    for member in members:
        if total_blocked >= max_total_cap:
            break
        # Check trade income between member and Britain
        member_state = world.get_diplomatic_state(member, "Britain")
        trade = TRADE_INCOME.get(member_state, 0)
        if trade > 0:
            blocked = min(75, trade, max_total_cap - total_blocked)
            if member in world.nation_gold:
                world.nation_gold[member] -= int(blocked)
            if "Britain" in world.nation_gold:
                world.nation_gold["Britain"] -= int(blocked)
            total_blocked += blocked

    world.continental_system_members = members
