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
# Note: ARMISTICE and VASSAL intentionally excluded — ARMISTICE auto-expires via
# _process_armistice_turns(), VASSAL exits via release_vassal() or rebellion.
_DOWNGRADE_ORDER = [
    "ALLIANCE", "DEFENSIVE_ALLIANCE", "NON_AGGRESSION",
    "OPEN_BORDERS", "PEACE"
]

# States that allow movement through territory
OPEN_MOVEMENT_STATES = {"OPEN_BORDERS", "NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE", "VASSAL"}

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

# Vassal: requires WAR (dictated peace) or OPEN_BORDERS+
VASSAL_MIN_STATES = {"WAR", "OPEN_BORDERS", "NON_AGGRESSION", "DEFENSIVE_ALLIANCE", "ALLIANCE"}
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
    # BUGFIX: These 3 keys are returned by calculate_acceptance() components
    # but were missing from FEEDBACK_STRINGS, causing empty hint fallback
    # when they are the dominant factor. See BUGFIX_PLAN_PROPOSAL_FLOW.md.
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

# ═══════ SWEETENER / DEMAND VALUES ═══════
SWEETENER_VALUES = {
    "gold_lump": 1 / 100,         # +1 per 100g (R145: was 1/200)
    "gold_per_turn": 3 / 100,     # +3 per 100g/turn
    "manpower_per_turn": 2 / 2000, # +2 per 2000 infantry/turn
    "infantry_manpower": 2 / 5000, # +2 per 5000
    "cavalry_manpower": 4 / 2500,  # +4 per 2500
    "artillery_manpower": 5 / 1500, # +5 per 1500
    "unit_swap": 3,                # +3 per favorable trade
    "ap_per_turn": 18,             # +18 per AP (1 AP/turn is an entire extra action — worth more than territory)
    "territory": 8,                # +8 per region (R144: was 5)
    "territory_cede": 8,           # +8 per region (alias for ratification path)
    "open_borders": 3,             # +3 flat
    "protection": 5,               # +5 flat
}
SWEETENER_CAP = 60                 # R146: was 30, raised to 60 so escalated offers improve acceptance

DEMAND_VALUES = {
    "gold_per_turn": -2 / 100,     # -2 per 100g/turn demanded
    "manpower_per_turn": -3 / 2000, # -3 per 2000 infantry/turn demanded
    "territory": -5,                # -5 per region demanded
    "territory_cede": -5,           # alias for ratification path
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
        return target_state in ("WAR", "PEACE", "NON_AGGRESSION")  # Deep audit fix 14: post_break_map uses NON_AGGRESSION

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
    return relation >= req


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


def _force_retreat_displaced_marshals(world, nation_a: str, nation_b: str) -> None:
    """Force-retreat marshals stranded in hostile territory after war ends.

    When an armistice/peace is signed, any marshal from nation_a in nation_b's
    territory (or vice versa) must be relocated to their nearest friendly region.
    Without this, stranded marshals create engagement deadlocks (C1 bug).
    """

    for marshal in list(world.marshals.values()):
        if marshal.strength <= 0:
            continue

        region = world.get_region(marshal.location)
        if not region:
            continue

        # Check if marshal is in hostile territory of the now-peaceful nation
        is_nation_a_in_b_territory = (
            marshal.nation == nation_a and region.controller == nation_b
        )
        is_nation_b_in_a_territory = (
            marshal.nation == nation_b and region.controller == nation_a
        )

        if not (is_nation_a_in_b_territory or is_nation_b_in_a_territory):
            continue

        # Find nearest friendly region via BFS
        retreat_to = _find_friendly_retreat(world, marshal)
        if retreat_to:
            marshal.move_to(retreat_to)
            # Cancel any strategic orders (they're now invalid)
            if getattr(marshal, 'strategic_order', None):
                marshal.strategic_order = None


def _find_friendly_retreat(world, marshal) -> str:
    """BFS to find nearest region controlled by marshal's nation."""
    from collections import deque

    start_region = world.get_region(marshal.location)
    if not start_region:
        return ""

    visited = {marshal.location}
    queue = deque()

    # Seed with adjacent regions
    for adj_name in start_region.adjacent_regions:
        if adj_name not in visited:
            visited.add(adj_name)
            queue.append(adj_name)

    while queue:
        region_name = queue.popleft()
        region = world.get_region(region_name)
        if not region:
            continue

        if region.controller == marshal.nation:
            return region_name

        for adj_name in region.adjacent_regions:
            if adj_name not in visited:
                visited.add(adj_name)
                queue.append(adj_name)

    # Fallback: capital
    from backend.models.region import NATION_CAPITALS
    capital = NATION_CAPITALS.get(marshal.nation, "")
    if capital and world.get_region(capital):
        return capital

    return ""


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

    # R49: Reset war_exhaustion only for nations with no other active wars
    parts = diplo_key.split("|")
    war_exhaustion = getattr(world, 'war_exhaustion', {})
    if len(parts) == 2:
        for nation in parts:
            has_other_war = False
            for other_key, other_state in world.diplomatic_states.items():
                if other_key == diplo_key:
                    continue
                if other_state == "WAR" and nation in other_key.split("|"):
                    has_other_war = True
                    break
            if not has_other_war:
                war_exhaustion.pop(nation, None)

    # R142: Clear war start turn
    war_start_turns = getattr(world, 'war_start_turns', {})
    war_start_turns.pop(diplo_key, None)
    world.war_start_turns = war_start_turns

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

    # Force-retreat displaced marshals from hostile territory (C1 armistice deadlock fix)
    if len(parts) == 2:
        nation_a, nation_b = parts
        _force_retreat_displaced_marshals(world, nation_a, nation_b)

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

    # ── Relation Modifier (R141: dampened during WAR) ──
    relation = world.nation_relations.get(diplo_key, 0)
    current_diplo_state = world.diplomatic_states.get(diplo_key, "PEACE")
    if current_diplo_state == "WAR":
        relation_mod = max(-10, min(10, relation / 4))  # -40 rel → -10 (was -20)
    else:
        relation_mod = max(-30, min(30, relation / 2))   # unchanged for peacetime

    # ── War Weariness (R142: +2/turn at war, cap +20) ──
    war_weariness_mod = 0
    if current_diplo_state == "WAR":
        war_start = getattr(world, 'war_start_turns', {}).get(diplo_key, world.current_turn)
        turns_at_war = max(0, int(world.current_turn) - int(war_start))
        war_weariness_mod = min(20, turns_at_war * 2)

    # ── Stalemate Duration (R143: +1/stalemate turn, cap +15) ──
    stalemate_duration_mod = 0
    if current_diplo_state == "WAR":
        stalemate_counters = getattr(world, 'ai_stalemate_counters', {})
        target_stalemate = stalemate_counters.get(target, 0)
        stalemate_duration_mod = min(15, target_stalemate)

    # ── Threat Modifier (COALITION_SPEC §6a) ──
    threat = int(getattr(world, 'threat_level', 0))
    threat_mod = 0
    player = getattr(world, 'player_nation', 'France')
    if proposer == player:
        threat_mod = threat * -0.3
    elif target != player:
        threat_mod = threat * 0.2

    # ── Coalition Loyalty Penalty (COALITION_SPEC §6a/§6c) ──
    from backend.game_logic.coalition import get_coalition_loyalty_penalty
    coalition_penalty = get_coalition_loyalty_penalty(target, world)

    # ── Deal Balance ──
    from backend.models.region import NATION_CAPITALS
    _all_capitals = set(NATION_CAPITALS.values())

    sweetener_total = 0.0
    for s in proposal.get("sweeteners", []):
        stype = s.get("type", "")
        svalue = s.get("value", 0)
        rate = SWEETENER_VALUES.get(stype, 0)
        if stype in ("territory_cede", "territory"):
            # Capital regions worth double (+16 vs +8)
            regions = s.get("regions", [])
            if not regions and svalue is None:
                # value=None with no regions — flat rate fallback (1 region implied)
                sweetener_total += rate
            else:
                capital_count = sum(1 for r in regions if r in _all_capitals)
                normal_count = max(0, (svalue or 0) - capital_count)
                sweetener_total += rate * normal_count + rate * 2 * capital_count
        elif isinstance(rate, (int, float)) and rate < 1:
            sweetener_total += (svalue * rate) if svalue is not None else 0
        else:
            sweetener_total += rate * svalue if svalue is not None else rate
    sweetener_total = min(SWEETENER_CAP, sweetener_total)

    demand_total = 0.0
    for d in proposal.get("demands", []):
        dtype = d.get("type", "")
        dvalue = d.get("value", 0)
        rate = DEMAND_VALUES.get(dtype, 0)
        if dtype in ("territory_cede", "territory"):
            # Capital demands worth double (-10 vs -5)
            regions = d.get("regions", [])
            if not regions and dvalue is None:
                # value=None with no regions — flat rate fallback
                demand_total += rate
            else:
                capital_count = sum(1 for r in regions if r in _all_capitals)
                normal_count = max(0, (dvalue or 0) - capital_count)
                demand_total += rate * normal_count + rate * 2 * capital_count
        elif isinstance(rate, (int, float)) and abs(rate) < 1:
            demand_total += (dvalue * rate) if dvalue is not None else 0
        else:
            demand_total += rate * dvalue if dvalue is not None else rate

    deal_balance = sweetener_total + demand_total

    # ── Diplomat Skill Bonus ──
    diplomat_skill_bonus = max(-8, (proposer_skill - target_skill) * 2)

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

    # R8: Military pressure from war score
    military_pressure = 0
    if war_score > 0:
        military_pressure = int(min(15, war_score * 0.15))

    # Use whichever is higher (they don't stack)
    situational_bonus = max(military_supremacy, battlefield_diplomacy, military_pressure)

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

    # ── Diplomatic Reliability (R34) ──
    reliability = getattr(world, 'diplomatic_reliability', {})
    proposer_reliability = reliability.get(proposer, 0)
    # Cap contribution at +/-10
    reliability_modifier = max(-10, min(10, proposer_reliability // 5))

    # ── Sum ──
    raw_score = (
        base
        + war_score_mod
        + relation_mod
        + war_weariness_mod
        + stalemate_duration_mod
        + threat_mod
        + coalition_penalty
        + deal_balance
        + diplomat_skill_bonus
        + personality_mod
        + situational_bonus
        + special_desire_bonus
        + harshness_bonus
        + reliability_modifier
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
        "war_weariness": int(war_weariness_mod),
        "stalemate_duration": int(stalemate_duration_mod),
        "threat_modifier": round(threat_mod, 1),
        "coalition_penalty": int(coalition_penalty),
        "deal_balance": round(deal_balance, 1),
        "diplomat_skill_bonus": diplomat_skill_bonus,
        "personality_modifier": personality_mod,
        "military_supremacy": military_supremacy,
        "battlefield_diplomacy": battlefield_diplomacy,
        "military_pressure": military_pressure,
        "special_desire_bonus": special_desire_bonus,
        "harshness_bonus": harshness_bonus,
        "reliability_modifier": reliability_modifier,
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
        "war_weariness", "stalemate_duration",
        "threat_modifier", "deal_balance", "diplomat_skill_bonus",
        "personality_modifier", "special_desire_bonus",
        "coalition_penalty", "harshness_bonus", "reliability_modifier",
        "military_supremacy", "battlefield_diplomacy", "military_pressure",
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
    base = 3
    skill_bonus = 1 if diplomat and diplomat.skill >= 8 else 0
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
        "propose_vassalage": 3,  # Fix 4: dialogue builds this key, not demand_vassalage
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

def declare_war(world, aggressor: str, target: str, casus_belli: bool = False) -> Dict:
    """Declare war: transition to WAR, apply penalties, handle cascade.

    Args:
        world: WorldState
        aggressor: Nation declaring war
        target: Nation being declared upon
        casus_belli: If True, halve relation penalties (R21 ultimatum rejection)

    Returns:
        {"success": bool, "message": str, "cascade": list of cascade entries,
         "dp_cost": int, "relation_changes": list}
    """
    # Deep audit fix 7: Prevent self-war
    if aggressor == target:
        return {"success": False, "message": "A nation cannot declare war on itself."}

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

    # R142: Record war start turn
    war_start_turns = getattr(world, 'war_start_turns', {})
    war_start_turns[diplo_key] = int(world.current_turn)
    world.war_start_turns = war_start_turns

    # R97: Remove active treaty (alliance clauses must stop during war)
    active_treaties = getattr(world, 'active_treaties', {})
    active_treaties.pop(diplo_key, None)

    # Penalties (halved with casus belli from rejected ultimatum)
    penalty_factor = 0.5 if casus_belli else 1.0
    relation_changes = []
    direct_penalty = int(-30 * penalty_factor)
    world.modify_nation_relation(aggressor, target, direct_penalty)
    relation_changes.append({"nations": (aggressor, target), "delta": direct_penalty})

    # Penalty with ALL other nations (also halved with casus belli)
    indirect_penalty = int(-15 * penalty_factor)
    all_nations = [world.player_nation] + list(getattr(world, 'enemy_nations', []))
    for nation in all_nations:
        if nation != aggressor and nation != target:
            world.modify_nation_relation(aggressor, nation, indirect_penalty)
            relation_changes.append({"nations": (aggressor, nation), "delta": indirect_penalty})

    # Coalition threat: +20 for France declaring war, halved with casus belli (§2a, S5c)
    if aggressor == world.player_nation:
        from backend.game_logic.coalition import add_threat
        threat = 10 if casus_belli else 20
        add_threat(world, threat, "war_declaration")

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

    # ── R12: ALLIANCE PARADOX CHECK (must run BEFORE cascade) ──
    # If both aggressor and target are allied with the player, the player
    # faces a paradox: honoring one alliance means breaking the other.
    # The cascade must skip the player so the player can choose.
    has_paradox = False
    player = world.player_nation
    if aggressor != player and target != player:
        aggressor_state = world.get_diplomatic_state(player, aggressor)
        target_state = world.get_diplomatic_state(player, target)
        alliance_states = ("ALLIANCE", "DEFENSIVE_ALLIANCE")
        if aggressor_state in alliance_states and target_state in alliance_states:
            has_paradox = True
            paradox_msg = (
                f"Sire, a crisis! {aggressor} has declared war on {target}. "
                f"We are allied with both nations. We must choose a side."
            )
            world.alliance_paradox_popup = {
                "attacker": aggressor,
                "defender": target,
                "attacker_alliance": aggressor_state,
                "defender_alliance": target_state,
                "message": paradox_msg,
            }
            # V2-89: Append to queue instead of overwriting
            world.pending_dialogue_queue.append({
                "type": "alliance_paradox",
                "target_nation": "",
                "talleyrand_text": paradox_msg,
                "options": [
                    {
                        "label": f"Honor alliance with {target}",
                        "description": f"Go to war with {aggressor} in defense of {target}.",
                        "action": "honor_defender",
                        "terms": {"attacker": aggressor, "defender": target},
                    },
                    {
                        "label": f"Side with {aggressor}",
                        "description": f"Break our alliance with {target}.",
                        "action": "break_defender_alliance",
                        "terms": {"attacker": aggressor, "defender": target},
                    },
                ],
                "context": {"attacker": aggressor, "defender": target},
                "turn_created": int(world.current_turn),
                "blocking": True,
            })

    # ── DEFENSIVE_ALLIANCE CASCADE ──
    # If paradox detected, exclude the player from cascade (player must choose)
    cascade_skip = {aggressor, target, player} if has_paradox else None
    cascade = _process_war_cascade(world, aggressor, target, processed=cascade_skip)

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

    # R29: Log to diplomatic history
    diplomatic_history = getattr(world, 'diplomatic_history', [])
    diplomatic_history.append({
        "turn": int(world.current_turn),
        "type": "war_declared",
        "nation": aggressor,
        "target": target,
    })
    if len(diplomatic_history) > 20:
        diplomatic_history[:] = diplomatic_history[-20:]
    world.diplomatic_history = diplomatic_history

    messages = [f"{aggressor} declares war on {target}!"]
    for c in cascade:
        if c.get("cascade_type") == "offensive":
            messages.append(
                f"{c['attacker_ally']} enters the war against {c['target']}, "
                f"honoring alliance with {c['aggressor']}!"
            )
        else:
            messages.append(
                f"{c['defender']} enters the war against {aggressor} "
                f"in defense of {c['ally']}!"
            )

    return {
        "success": True,
        "message": " ".join(messages),
        "cascade": cascade,
        "dp_cost": dp_cost,
        "relation_changes": relation_changes,
    }


def _process_war_cascade(world, aggressor: str, target: str, processed: set = None) -> List[Dict]:
    """Process defensive and offensive alliance cascade when war is declared.

    Defensive: Nations with DA/ALLIANCE with the TARGET join against the aggressor.
    Offensive: Nations with ALLIANCE (not DA) with the AGGRESSOR join against the target.

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
                # R142: Record war start turn
                cascade_war_starts = getattr(world, 'war_start_turns', {})
                cascade_war_starts[war_key] = int(world.current_turn)
                world.war_start_turns = cascade_war_starts
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

    # ── OFFENSIVE CASCADE: Aggressor's ALLIANCE partners join against target ──
    for nation in all_nations:
        if nation in processed:
            continue
        if nation in getattr(world, 'vassals', {}):
            continue  # Vassals handled in vassal auto-join block below

        state_with_aggressor = world.get_diplomatic_state(nation, aggressor)
        if state_with_aggressor == "ALLIANCE":
            if not world.is_at_war(nation, target):
                war_key = world._make_diplo_key(nation, target)
                world.diplomatic_states[war_key] = "WAR"
                cascade_war_starts = getattr(world, 'war_start_turns', {})
                cascade_war_starts[war_key] = int(world.current_turn)
                world.war_start_turns = cascade_war_starts
                processed.add(nation)
                active_treaties = getattr(world, 'active_treaties', {})
                active_treaties.pop(war_key, None)
                world.modify_nation_relation(nation, target, -20)

                cascade.append({
                    "attacker_ally": nation,
                    "aggressor": aggressor,
                    "target": target,
                    "cascade_type": "offensive",
                })

                world.log_event({
                    "type": "offensive_cascade",
                    "attacker_ally": nation,
                    "aggressor": aggressor,
                    "against": target,
                })

                from backend.notifications import (
                    create_notification, NotificationPriority, ALLIANCE_CASCADE_WAR,
                )
                world.notifications.add(create_notification(
                    ALLIANCE_CASCADE_WAR,
                    NotificationPriority.HIGH,
                    f"{nation} Joins Offensive!",
                    f"{nation} enters the war against {target}, honoring alliance with {aggressor}.",
                    int(world.current_turn),
                ))

                from backend.game_logic.dispatch import queue_dispatch_event
                queue_dispatch_event(world, "diplomatic_offensive_cascade",
                                    {"nation": nation, "aggressor": aggressor, "target": target},
                                    "partial_on_nation")

                sub_cascade = _process_war_cascade(world, nation, target, processed)
                cascade.extend(sub_cascade)

    # ── VASSAL AUTO-JOIN: Vassals follow their lord into war (Fix 12) ──
    vassals = getattr(world, 'vassals', {})
    for vassal_nation, vassal_data in vassals.items():
        if vassal_nation in processed:
            continue
        lord = vassal_data.get("lord", "")
        if lord in processed and lord != target:
            # Lord joined as aggressor/ally — vassal follows
            if not world.is_at_war(vassal_nation, target):
                war_key = world._make_diplo_key(vassal_nation, target)
                world.diplomatic_states[war_key] = "WAR"
                cascade_war_starts = getattr(world, 'war_start_turns', {})
                cascade_war_starts[war_key] = int(world.current_turn)
                world.war_start_turns = cascade_war_starts
                processed.add(vassal_nation)
                active_treaties = getattr(world, 'active_treaties', {})
                active_treaties.pop(war_key, None)

                cascade.append({
                    "vassal": vassal_nation,
                    "lord": lord,
                    "target": target,
                    "cascade_type": "vassal_auto_join",
                })

                world.log_event({
                    "type": "vassal_auto_join_war",
                    "vassal": vassal_nation,
                    "lord": lord,
                    "against": target,
                })

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
        "message": f"Diplomatic relations between {nation_a} and {nation_b} downgraded: {_STATE_DISPLAY_NAMES.get(current_state, current_state)} → {_STATE_DISPLAY_NAMES.get(new_state, new_state)}.",
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
                               f"{_STATE_DISPLAY_NAMES.get(state, state)} may collapse in 2 turns.",
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
                        # Deep audit fix 5: Clear active treaty on auto-downgrade
                        active_treaties = getattr(world, 'active_treaties', {})
                        active_treaties.pop(diplo_key, None)
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
                                       f"{_STATE_DISPLAY_NAMES.get(state, state)} → {_STATE_DISPLAY_NAMES.get(new_state, new_state)}.",
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
                            f"{parts[0]}-{parts[1]}: {_STATE_DISPLAY_NAMES.get(state, state)} → {_STATE_DISPLAY_NAMES.get(new_state, new_state)}.",
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
                  defender_casualties: int, location: str = "") -> None:
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

    # R9: Only battles with >= 1000 total casualties count for war score
    total_casualties = attacker_casualties + defender_casualties
    if total_casualties < 1000:
        return

    record = {
        "turn": world.current_turn,
        "winner": winner_nation,
        "attacker": attacker_nation,
        "defender": defender_nation,
        "attacker_casualties": int(attacker_casualties),
        "defender_casualties": int(defender_casualties),
        "location": location,
    }
    world.battle_records[diplo_key].append(record)

    # Check for decisive battle (total_casualties already computed above)
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

    # PEACE, ARMISTICE — cannot enter
    return False


# ═══════════════════════════════════════════════════════
# ADVANCE_TURN DIPLOMATIC PROCESSING (§7f)
# ═══════════════════════════════════════════════════════

def process_diplomacy_turn(world) -> List[Dict]:
    """Process diplomatic events during advance_turn.

    Implements §7f processing order (items this session covers):
    1. DP regeneration
    4. War score recalculation
    8. Armistice expiration (minimum 5 turns)
    9. Cooldown decrements
    10. Trade income (handled separately in income phase)
    13. Automatic downgrade check

    Returns list of diplomatic events for Morning Dispatch.
    """
    events = []

    # ── 1. DP regeneration ──
    _process_dp_regen(world)

    # ── 1b. R90: Auto-cancel mission if target nation eliminated ──
    mission_cancel_events = _check_mission_target_eliminated(world)
    events.extend(mission_cancel_events)

    # ── 2. Mission DP deduction (Session 3) ──
    mission_events = _process_mission_dp(world)
    events.extend(mission_events)

    # ── 3. Mission effects (Session 3) ──
    effect_events = _process_mission_effects(world)
    events.extend(effect_events)

    # ── 4. War score recalculation ──
    recalculate_war_scores(world)
    apply_war_score_decay(world)

    # ── 4a. Relation decay (R4a) ──
    _process_relation_decay(world)

    # 5-7: Vassal processing (defection cascade, loyalty, rebellion) — implemented in vassal.py, wired in advance_turn()

    # ── 8. Armistice expiration ──
    armistice_events = _process_armistice_expiration(world)
    events.extend(armistice_events)

    # ── 9. Cooldown decrements ──
    _decrement_cooldowns(world)

    # 9a-9d: Coalition processing (war exhaustion, threat accumulation/decay, coalition check) — implemented in coalition.py, wired in advance_turn()

    # 10. Trade income — handled in process_trade_income() called from advance_turn income phase

    # 11-12: Treaty obligations + Continental System — implemented in diplomacy.py (process_treaty_obligations, apply_continental_system), wired in advance_turn()

    # ── 13. Automatic downgrade check ──
    downgrade_events = check_auto_downgrade(world)
    events.extend(downgrade_events)

    # ── 14. Diplomatic reliability (R34) ──
    _process_diplomatic_reliability(world)

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
            # S1: Queue DP breakdown for morning dispatch
            from backend.game_logic.dispatch import queue_dispatch_event
            parts = ["base 3"]
            if diplomat and diplomat.skill >= 8:
                parts.append("+1 skill")
            if authority >= 60:
                parts.append("+1 authority")
            elif authority < 30:
                parts.append("-1 low authority")
            if not controls_capital:
                parts.append("-1 no capital")
            breakdown_str = ", ".join(parts)
            queue_dispatch_event(world, "diplomatic_dp_regen",
                                {"dp": int(dp), "breakdown": breakdown_str}, "always")
        else:
            # Store AI DP for AI diplomacy consumption
            if not hasattr(world, 'nation_dp'):
                world.nation_dp = {}
            world.nation_dp[nation] = int(dp)


def calculate_trade_income(world) -> Dict[str, int]:
    """Calculate trade income from diplomatic states (read-only, no side effects).

    R6: Diminishing returns — partners sorted by state level (best first),
    rates [1.0, 0.75, 0.50, 0.25]. 5th+ partners get 0.25.

    Returns dict of {nation: trade_income}.
    """
    _DIMINISHING_RATES = [1.0, 0.75, 0.50, 0.25]
    _STATE_PRIORITY = {"ALLIANCE": 0, "DEFENSIVE_ALLIANCE": 1, "NON_AGGRESSION": 2,
                       "OPEN_BORDERS": 3, "PEACE": 4}

    # Collect trade partners per nation: {nation: [(partner, trade_amount, state)]}
    partners_by_nation: Dict[str, list] = {}
    for pair_key, state in world.diplomatic_states.items():
        trade = TRADE_INCOME.get(state, 0)
        if trade > 0:
            parts = pair_key.split("|")
            if len(parts) == 2:
                nation_a, nation_b = parts
                # Skip vassals — tribute replaces trade
                if nation_a in getattr(world, 'vassals', {}) or nation_b in getattr(world, 'vassals', {}):
                    continue
                partners_by_nation.setdefault(nation_a, []).append((nation_b, trade, state))
                partners_by_nation.setdefault(nation_b, []).append((nation_a, trade, state))

    # Apply diminishing returns per nation
    trade_by_nation = {}
    for nation, partners in partners_by_nation.items():
        # Sort by state priority (best first), tiebreak alphabetical
        partners.sort(key=lambda p: (_STATE_PRIORITY.get(p[2], 5), p[0]))
        total = 0
        for i, (partner, trade_amount, state) in enumerate(partners):
            rate = _DIMINISHING_RATES[min(i, len(_DIMINISHING_RATES) - 1)]
            total += int(trade_amount * rate)
        trade_by_nation[nation] = total

    return trade_by_nation


def process_trade_income(world) -> Dict[str, int]:
    """Calculate and apply trade income from diplomatic states.

    Returns dict of {nation: trade_income} for display.
    """
    trade_by_nation = calculate_trade_income(world)

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
            # Fix 12: Notification + dispatch for armistice expiration (peace)
            from backend.notifications import create_notification, NotificationPriority
            world.notifications.add(create_notification(
                "armistice_expired", NotificationPriority.HIGH,
                "Armistice Concluded",
                f"The armistice with {nation_b if nation_a == world.player_nation else nation_a} has concluded. Peace declared.",
                int(world.current_turn),
            ))
            from backend.game_logic.dispatch import queue_dispatch_event
            queue_dispatch_event(world, "diplomatic_armistice_expired_peace",
                                {"nation_a": nation_a, "nation_b": nation_b}, "always")
        else:
            # Relations too hostile — back to WAR
            world.diplomatic_states[diplo_key] = "WAR"
            # R142: Record war start turn
            arm_war_starts = getattr(world, 'war_start_turns', {})
            arm_war_starts[diplo_key] = int(world.current_turn)
            world.war_start_turns = arm_war_starts
            # Deep audit fix 6: Clear active treaty on armistice→WAR
            active_treaties = getattr(world, 'active_treaties', {})
            active_treaties.pop(diplo_key, None)
            events.append({
                "type": "armistice_expired_war",
                "nations": [nation_a, nation_b],
                "message": f"The armistice between {nation_a} and {nation_b} has collapsed. War resumes.",
            })
            # Fix 12: Notification + dispatch for armistice expiration (war)
            from backend.notifications import create_notification, NotificationPriority
            world.notifications.add(create_notification(
                "armistice_expired", NotificationPriority.CRITICAL,
                "Armistice Collapsed",
                f"The armistice with {nation_b if nation_a == world.player_nation else nation_a} has collapsed. War resumes!",
                int(world.current_turn),
            ))
            from backend.game_logic.dispatch import queue_dispatch_event
            queue_dispatch_event(world, "diplomatic_armistice_expired_war",
                                {"nation_a": nation_a, "nation_b": nation_b}, "always")

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
        # R92: Dispatch event for mission completion
        from backend.game_logic.dispatch import queue_dispatch_event
        queue_dispatch_event(world, "diplomatic_mission_completed",
                            {"nation": target}, "player_mission")
        # Stub: no intel revealed yet (Session 4+)

    # UNDERMINE_ALLIANCE: stub (requires intel system)
    # COURT_NATION undermine chance: stub

    return events


def _check_mission_target_eliminated(world) -> List[Dict]:
    """R90: Auto-cancel active diplomatic mission if target nation is eliminated.

    A nation is eliminated when it has 0 regions AND 0 living marshals.
    Called early in process_diplomacy_turn before mission DP deduction.

    Returns list of events (0 or 1 cancellation event).
    """
    events = []
    mission = getattr(world, 'active_diplomatic_mission', None)
    if not mission or mission.get("completed"):
        return events

    target = mission.get("target", "")
    if not target:
        return events

    # Check if target nation has 0 regions
    has_regions = any(
        getattr(r, 'controller', '') == target
        for r in world.regions.values()
    )
    # Check if target nation has 0 living marshals
    has_marshals = any(
        m.nation == target and m.strength > 0
        for m in world.marshals.values()
    )

    if not has_regions and not has_marshals:
        # Nation eliminated — cancel mission
        world.active_diplomatic_mission = None
        if getattr(world, 'talleyrand_state', '') == "ON_MISSION":
            world.talleyrand_state = "IDLE"
        events.append({
            "type": "diplomatic_mission_cancelled",
            "target": target,
            "reason": "nation_eliminated",
            "message": f"Talleyrand's mission to {target} cancelled — the nation no longer exists.",
        })
        world.log_event({
            "type": "diplomatic_mission_cancelled_eliminated",
            "target": target,
        })

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

    # Cost: 1 DP — use player DP for player, nation_dp for AI
    player_nation = getattr(world, 'player_nation', 'France')
    if breaker_nation == player_nation:
        if world.diplomatic_points < 1:
            return {"success": False, "message": "Insufficient DP to break treaty (costs 1 DP)."}
        world.diplomatic_points -= 1
    else:
        nation_dp = getattr(world, 'nation_dp', {})
        if nation_dp.get(breaker_nation, 0) < 1:
            return {"success": False, "message": f"{breaker_nation} has insufficient DP to break treaty."}
        nation_dp[breaker_nation] = nation_dp.get(breaker_nation, 0) - 1
        world.nation_dp = nation_dp

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

    # Deep audit fix 9: Only add threat when PLAYER breaks treaty (threat tracks France's aggression)
    if breaker_nation == world.player_nation:
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
        "WAR": "PEACE",  # Deep audit fix 3
        "ARMISTICE": "PEACE",  # Deep audit fix 3
    }
    current_state = world.diplomatic_states.get(pair_key, "PEACE")
    new_state = post_break_map.get(current_state, "PEACE")
    world.diplomatic_states[pair_key] = new_state

    # Deep audit fix 3: Clean up war data if breaking from WAR/ARMISTICE
    if current_state in ("WAR", "ARMISTICE"):
        cleanup_war_end(world, pair_key)

    # Remove treaty
    del active_treaties[pair_key]

    # Deep audit fix 12: Void any proposal_in_transit for this nation pair
    pit = getattr(world, 'proposal_in_transit', None)
    if pit:
        pit_target = pit.get("target", "")
        pit_proposer = pit.get("proposal", {}).get("proposer_nation", "")
        if pit_target and pit_proposer:
            pit_key = world._make_diplo_key(pit_proposer, pit_target)
            if pit_key == pair_key:
                world.proposal_in_transit = None

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

    # R34: Decrease diplomatic reliability for breaker
    reliability = getattr(world, 'diplomatic_reliability', {})
    reliability[breaker_nation] = max(-100, reliability.get(breaker_nation, 0) - 10)
    world.diplomatic_reliability = reliability

    # R29: Log to diplomatic history
    diplomatic_history = getattr(world, 'diplomatic_history', [])
    diplomatic_history.append({
        "turn": int(world.current_turn),
        "type": "treaty_broken",
        "nation": breaker_nation,
        "target": other,
        "treaty_type": treaty_type,
    })
    if len(diplomatic_history) > 20:
        diplomatic_history[:] = diplomatic_history[-20:]
    world.diplomatic_history = diplomatic_history

    return {
        "success": True,
        "message": f"{breaker_nation} has broken the {treaty_type} with {other}! Relations plummet.",
        "new_state": new_state,
        "relation_changes": relation_changes,
        "treaty_broken_event": treaty_type,  # R23: signal for trust reactions
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


def _process_relation_decay(world) -> None:
    """R4a: Relations drift toward +-10 band each turn.

    Skip pairs that are: vassals, at WAR, in ARMISTICE, or targeted by COURT_NATION mission.
    Above +10: -1/turn. Below -10: +1/turn.
    """
    player = getattr(world, 'player_nation', 'France')
    all_nations = [player] + list(getattr(world, 'enemy_nations', []))

    # Check for active COURT_NATION mission target (player-side only)
    court_target = None
    mission = getattr(world, 'active_diplomatic_mission', None)
    if mission and mission.get("type") == "COURT_NATION":
        court_target = mission.get("target")

    vassals = getattr(world, 'vassals', {})

    for i, nation_a in enumerate(all_nations):
        for nation_b in all_nations[i + 1:]:
            # Deep audit fix 15: Skip vassal-lord pairs only, not vassal-third-party
            if nation_a in vassals and vassals[nation_a].get("lord") == nation_b:
                continue
            if nation_b in vassals and vassals[nation_b].get("lord") == nation_a:
                continue

            diplo_key = world._make_diplo_key(nation_a, nation_b)
            state = world.diplomatic_states.get(diplo_key, "PEACE")

            # Skip WAR and ARMISTICE pairs
            if state in ("WAR", "ARMISTICE"):
                continue

            # Skip if COURT_NATION targets either nation in the pair
            if court_target and court_target in (nation_a, nation_b):
                continue

            relation = world.nation_relations.get(diplo_key, 0)
            if relation > 10:
                world.modify_nation_relation(nation_a, nation_b, -1)
            elif relation < -10:
                world.modify_nation_relation(nation_a, nation_b, 1)


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
    existing_members = list(members)
    for vassal_name, state in world.vassals.items():
        if state["lord"] == lord:
            autonomy = state.get("autonomy", AUTONOMY_SATELLITE)
            if autonomy in (AUTONOMY_PUPPET, AUTONOMY_SATELLITE):
                if vassal_name not in members:
                    members.append(vassal_name)
                    # 6A-8: Queue dispatch event for newly auto-joined vassals
                    from backend.game_logic.dispatch import queue_dispatch_event
                    queue_dispatch_event(world, "diplomatic_continental_system",
                                         {"nation": vassal_name, "action": "joined"}, "always")

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
                world.nation_gold[member] = max(0, world.nation_gold[member] - int(blocked))
            if "Britain" in world.nation_gold:
                world.nation_gold["Britain"] = max(0, world.nation_gold["Britain"] - int(blocked))
            total_blocked += blocked

    world.continental_system_members = members


# ═══════════════════════════════════════════════════════
# DIPLOMATIC RELIABILITY (R34)
# ═══════════════════════════════════════════════════════

def _process_diplomatic_reliability(world) -> None:
    """R34: Increase diplomatic reliability for nations honoring treaties for 10+ turns.

    Each active treaty that has been honored for 10+ turns grants +5 reliability
    to each nation in the treaty, capped at 100.
    """
    active_treaties = getattr(world, 'active_treaties', {})
    reliability = getattr(world, 'diplomatic_reliability', {})

    for pair_key, treaty in active_treaties.items():
        turn_signed = treaty.get("turn_signed", 0)
        turns_honored = world.current_turn - turn_signed

        if turns_honored >= 10 and turns_honored % 10 == 0:
            # Award reliability every 10 turns of honoring
            nations = treaty.get("nations", [])
            for nation in nations:
                current = reliability.get(nation, 0)
                reliability[nation] = min(100, current + 5)

    world.diplomatic_reliability = reliability


# ═══════════════════════════════════════════════════════
# DIPLOMACY BUTTON — PREVIEW HELPERS (Phase 5)
# ═══════════════════════════════════════════════════════

def get_likelihood_descriptor(score: int) -> str:
    """Map acceptance score to a thematic likelihood word (§3a).

    Single source of truth for all likelihood displays:
    wizard, R118 preview, any future acceptance display.
    """
    if score >= 70:
        return "Almost Certain"
    elif score >= 50:
        return "Favorable"
    elif score >= 40:
        return "Uncertain — may counter"
    elif score >= 30:
        return "Doubtful — expect counter"
    elif score >= 15:
        return "Unlikely"
    else:
        return "Hopeless"


def get_relation_descriptor(relation: int) -> str:
    """Map relation score to descriptor word (§2a)."""
    if relation >= 60:
        return "Loyal"
    elif relation >= 30:
        return "Friendly"
    elif relation >= 0:
        return "Neutral"
    elif relation >= -29:
        return "Wary"
    else:
        return "Hostile"


# ═══════ ASSESSMENT TEMPLATES (§3f) ═══════
_ASSESSMENT_TEMPLATES = {
    "war_winning": "{nation} falters, Your Excellency. Our armies press the advantage — an armistice now would be accepted from a position of strength.",
    "war_losing": "The campaign goes poorly against {nation}. An armistice may be wise — though they will sense our weakness and demand terms.",
    "war_stalemate": "The war with {nation} grinds on without decisive result. Both sides bleed. An armistice may find receptive ears.",
    "armistice_wary": "The guns are silent, but the wound festers. Peace may be achievable with {nation}, though they will demand terms.",
    "armistice_neutral": "The armistice holds. {nation} appears open to permanent peace — the moment may be favorable.",
    "peace_hostile": "Relations with {nation} remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes.",
    "peace_wary": "{nation} maintains a cautious distance. Vienna watches our moves with calculating eyes. Open borders would test their appetite.",
    "peace_neutral": "{nation} is neither friend nor foe. Opportunity exists for closer ties — open borders would be a natural first step.",
    "peace_friendly": "{nation} is well-disposed toward us. The time is ripe for open borders, perhaps more.",
    "open_borders_neutral": "Our borders with {nation} are open, but trust remains shallow. A non-aggression pact would formalize the thaw.",
    "open_borders_friendly": "{nation} trades freely with us. The foundation is strong — a non-aggression pact or deeper ties are within reach.",
    "non_aggression_to_alliance": "We have {nation}'s word they will not strike. A defensive alliance would bind us closer — if the relation bears it.",
    "alliance_stable": "Our alliance with {nation} stands firm. There is little to gain from change, and much to lose.",
    "alliance_strained": "Our alliance with {nation} holds, but the bond frays. Tread carefully — a break now would cost us dearly.",
    "vassal_loyal": "{nation} serves faithfully. Tribute flows, the garrison keeps order. A reliable vassal.",
    "vassal_restless": "Unrest simmers in {nation}. The burden of tribute grows heavy — investment would forestall rebellion.",
    "vassal_rebellious": "{nation} teeters on the edge of rebellion, Your Excellency. Urgent investment or increased autonomy may be our only recourse.",
}

_ASSESSMENT_FALLBACK = "Talleyrand considers the situation with {nation}."


def get_assessment_text(world, target_nation: str) -> str:
    """Get Talleyrand's assessment template for a nation (§3f)."""
    player = getattr(world, 'player_nation', 'France')
    diplo_key = world._make_diplo_key(player, target_nation)
    state = world.diplomatic_states.get(diplo_key, "PEACE")
    relation = world.nation_relations.get(diplo_key, 0)

    # Vassal check
    vassals = getattr(world, 'vassals', {})
    if target_nation in vassals:
        loyalty = vassals[target_nation].get("loyalty", 50)
        if loyalty >= 50:
            key = "vassal_loyal"
        elif loyalty >= 25:
            key = "vassal_restless"
        else:
            key = "vassal_rebellious"
        template = _ASSESSMENT_TEMPLATES.get(key, _ASSESSMENT_FALLBACK)
        return template.format(nation=target_nation)

    if state == "WAR":
        war_score = get_war_score_for(world, player, target_nation)
        if war_score > 20:
            key = "war_winning"
        elif war_score < -20:
            key = "war_losing"
        else:
            key = "war_stalemate"
    elif state == "ARMISTICE":
        key = "armistice_wary" if relation < 0 else "armistice_neutral"
    elif state == "PEACE":
        if relation < -29:
            key = "peace_hostile"
        elif relation < 0:
            key = "peace_wary"
        elif relation < 30:
            key = "peace_neutral"
        else:
            key = "peace_friendly"
    elif state == "OPEN_BORDERS":
        key = "open_borders_neutral" if relation < 30 else "open_borders_friendly"
    elif state == "NON_AGGRESSION":
        key = "non_aggression_to_alliance"
    elif state in ("DEFENSIVE_ALLIANCE", "ALLIANCE"):
        key = "alliance_stable" if relation >= 50 else "alliance_strained"
    else:
        key = None

    if key and key in _ASSESSMENT_TEMPLATES:
        return _ASSESSMENT_TEMPLATES[key].format(nation=target_nation)
    return _ASSESSMENT_FALLBACK.format(nation=target_nation)


# ═══════ DISPLAY STATE NAMES ═══════
_STATE_DISPLAY_NAMES = {
    "WAR": "At War",
    "ARMISTICE": "Armistice",
    "PEACE": "Peace",
    "OPEN_BORDERS": "Open Borders",
    "NON_AGGRESSION": "Non-Aggression",
    "DEFENSIVE_ALLIANCE": "Defensive Alliance",
    "ALLIANCE": "Alliance",
    "VASSAL": "Vassal",
}


def get_available_diplomatic_actions(world, target_nation: str) -> List[Dict]:
    """Build available action list for the diplomacy wizard (§2b/2c/2d).

    Returns list of action dicts with dp_cost, available, disabled_reason,
    likelihood (for proposals), likelihood_score.
    """
    # Block all actions while a diplomatic dialogue is pending
    if getattr(world, 'pending_diplomatic_dialogue', None) is not None:
        return []

    player = getattr(world, 'player_nation', 'France')
    diplo_key = world._make_diplo_key(player, target_nation)
    state = world.diplomatic_states.get(diplo_key, "PEACE")
    dp = int(getattr(world, 'diplomatic_points', 0))
    gold = int(world.nation_gold.get(player, 0)) if hasattr(world, 'nation_gold') else 0
    vassals = getattr(world, 'vassals', {})

    # Talleyrand skill for DP cost adjustment
    diplomats = getattr(world, 'diplomats', {})
    talleyrand = diplomats.get(player)
    tal_skill = talleyrand.skill if talleyrand else 5

    actions = []
    active_treaties = getattr(world, 'active_treaties', {})

    # ── VASSAL MANAGEMENT (§2c) ──
    if target_nation in vassals:
        vassal_state = vassals[target_nation]
        autonomy = vassal_state.get("autonomy", 1)

        # Invest in Vassal
        invest_available = True
        invest_reason = ""
        invest_cooldowns = getattr(world, 'vassal_investment_cooldowns', {})
        if target_nation in invest_cooldowns and invest_cooldowns[target_nation] > 0:
            invest_available = False
            invest_reason = f"Cooldown: {invest_cooldowns[target_nation]} turns"
        elif dp < 1:
            invest_available = False
            invest_reason = "Insufficient DP"
        elif gold < 200:
            invest_available = False
            invest_reason = "Insufficient Gold"
        actions.append({
            "action": "invest_vassal",
            "display_name": "Invest in Vassal",
            "dp_cost": 1,
            "gold_cost": 200,
            "available": invest_available,
            "disabled_reason": invest_reason,
        })

        # Increase Autonomy
        from backend.game_logic.vassal import AUTONOMY_AUTONOMOUS
        inc_available = autonomy < AUTONOMY_AUTONOMOUS
        inc_reason = "" if inc_available else "Already at maximum autonomy"
        if inc_available and dp < 1:
            inc_available = False
            inc_reason = "Insufficient DP"
        actions.append({
            "action": "increase_autonomy",
            "display_name": "Increase Autonomy",
            "dp_cost": 1,
            "available": inc_available,
            "disabled_reason": inc_reason,
        })

        # Decrease Autonomy
        from backend.game_logic.vassal import AUTONOMY_PUPPET
        dec_available = autonomy > AUTONOMY_PUPPET
        dec_reason = "" if dec_available else "Already at minimum autonomy"
        if dec_available and dp < 1:
            dec_available = False
            dec_reason = "Insufficient DP"
        actions.append({
            "action": "decrease_autonomy",
            "display_name": "Decrease Autonomy",
            "dp_cost": 1,
            "available": dec_available,
            "disabled_reason": dec_reason,
        })

        # Release Vassal
        release_available = True
        release_reason = ""
        if dp < 1:
            release_available = False
            release_reason = "Insufficient DP"
        actions.append({
            "action": "release_vassal",
            "display_name": "Release Vassal",
            "dp_cost": 1,
            "available": release_available,
            "disabled_reason": release_reason,
        })

        return actions

    # ── FOREIGN AFFAIRS (§2b) ──
    cooldowns = getattr(world, 'player_proposal_cooldowns', {})
    armistice_cooldowns = getattr(world, 'armistice_cooldowns', {})
    ultimatum_cooldowns = getattr(world, 'ultimatum_cooldowns', {})
    relation = world.nation_relations.get(diplo_key, 0)

    def _proposal_action(action_key: str, display: str, target_state: str):
        base_cost = get_transition_dp_cost(state, target_state)
        cost = get_dp_cost(action_key, tal_skill, transition_base=base_cost)
        available = True
        reason = ""

        # Cooldown check
        if target_nation in cooldowns and cooldowns[target_nation] > 0:
            available = False
            reason = f"Cooldown: {cooldowns[target_nation]} turns"
        type_key = f"{target_nation}_{target_state.lower()}"
        if type_key in cooldowns and cooldowns[type_key] > 0:
            available = False
            reason = f"Cooldown: {cooldowns[type_key]} turns"

        # U2: Armistice cooldown check (prioritize over DP)
        arm_cd = armistice_cooldowns.get(diplo_key, 0)
        if arm_cd > 0 and target_state not in ("PEACE", "OPEN_BORDERS", "NON_AGGRESSION",
                                                 "DEFENSIVE_ALLIANCE", "ALLIANCE"):
            available = False
            reason = f"Armistice: {arm_cd} turns remaining"

        # Relation requirement
        req = STATE_RELATION_REQUIREMENTS.get(target_state)
        if req is not None and relation < req:
            available = False
            reason = "Relations too low"

        # DP check
        if available and dp < cost:
            available = False
            reason = "Insufficient DP"

        # Calculate likelihood
        likelihood_score = 0
        likelihood = ""
        if available or reason in ("Insufficient DP", "Relations too low"):
            try:
                _type_map = {
                    "ARMISTICE": "armistice_winning",
                    "PEACE": "peace",
                    "OPEN_BORDERS": "open_borders",
                    "NON_AGGRESSION": "non_aggression",
                    "DEFENSIVE_ALLIANCE": "defensive_alliance",
                    "ALLIANCE": "alliance",
                    "VASSAL": "vassalage",
                }
                ptype = _type_map.get(target_state, "peace")
                if target_state == "ARMISTICE":
                    ws = get_war_score_for(world, player, target_nation)
                    ptype = "armistice_winning" if ws > 0 else "armistice_losing"
                proposal = {
                    "type": ptype,
                    "proposer_nation": player,
                    "target_nation": target_nation,
                    "sweeteners": [],
                    "demands": [],
                    "clauses": [],
                }
                result = calculate_acceptance(proposal, world)
                likelihood_score = int(result.get("score", 0))
                likelihood = get_likelihood_descriptor(likelihood_score)
            except Exception:
                likelihood_score = 0
                likelihood = "Hopeless"

        return {
            "action": action_key,
            "display_name": display,
            "dp_cost": int(cost),
            "available": available,
            "disabled_reason": reason,
            "likelihood": likelihood,
            "likelihood_score": int(likelihood_score),
        }

    # ── MISSION HELPERS ──
    from backend.game_logic.diplomatic_dialogue import MISSION_DP_COSTS
    active_mission = getattr(world, 'active_diplomatic_mission', None)
    tal_state = getattr(world, 'talleyrand_state', 'IDLE')

    # W5: Mission effect text mapping
    _MISSION_EFFECT_SHORT = {
        "IMPROVE_RELATIONS": "+5 relation/turn",
        "COURT_NATION": "+5 relation/turn, 20% blowback",
        "GATHER_INTEL": "3-turn full intel",
        "UNDERMINE_ALLIANCE": "-3 relation between targets/turn",
        "REASSURE_ALLY": "+3 relation/turn",
    }

    def _mission_action(action_key: str, display: str, mission_type: str):
        cost = MISSION_DP_COSTS.get(mission_type, 1)
        available = True
        reason = ""
        if tal_state == "IN_TRANSIT":
            available = False
            reason = "Talleyrand in transit"
        elif active_mission is not None:
            available = False
            reason = "Mission already active"
        elif dp < cost:
            available = False
            reason = "Insufficient DP"
        return {
            "action": action_key,
            "display_name": display,
            "dp_cost": int(cost),
            "available": available,
            "disabled_reason": reason,
            "effect_text": _MISSION_EFFECT_SHORT.get(mission_type, ""),
        }

    if state == "WAR":
        actions.append(_proposal_action("propose_armistice", "Propose Armistice", "ARMISTICE"))
        actions.append(_mission_action("mission_gather_intel", "Gather Intel", "GATHER_INTEL"))
        actions.append(_mission_action("mission_undermine", "Undermine Alliances", "UNDERMINE_ALLIANCE"))

    elif state == "ARMISTICE":
        actions.append(_proposal_action("propose_peace", "Propose Peace", "PEACE"))
        actions.append(_mission_action("mission_improve_relations", "Improve Relations", "IMPROVE_RELATIONS"))
        actions.append(_mission_action("mission_court", "Court Nation", "COURT_NATION"))
        actions.append(_mission_action("mission_gather_intel", "Gather Intel", "GATHER_INTEL"))
        actions.append(_mission_action("mission_undermine", "Undermine Alliances", "UNDERMINE_ALLIANCE"))

    elif state == "PEACE":
        actions.append(_proposal_action("propose_open_borders", "Propose Open Borders", "OPEN_BORDERS"))
        war_available = True
        war_reason = ""
        arm_cd = armistice_cooldowns.get(diplo_key, 0)
        if arm_cd > 0:
            war_available = False
            war_reason = f"Armistice: {arm_cd} turns remaining"
        elif dp < 1:
            war_available = False
            war_reason = "Insufficient DP"
        actions.append({"action": "declare_war", "display_name": "Declare War", "dp_cost": 1, "available": war_available, "disabled_reason": war_reason})
        ult_available = True
        ult_reason = ""
        ult_cd = ultimatum_cooldowns.get(target_nation, 0)
        if ult_cd > 0:
            ult_available = False
            ult_reason = f"Cooldown: {ult_cd} turns"
        elif dp < 2:
            ult_available = False
            ult_reason = "Insufficient DP"
        actions.append({"action": "send_ultimatum", "display_name": "Send Ultimatum", "dp_cost": 2, "available": ult_available, "disabled_reason": ult_reason})
        actions.append(_mission_action("mission_improve_relations", "Improve Relations", "IMPROVE_RELATIONS"))
        actions.append(_mission_action("mission_court", "Court Nation", "COURT_NATION"))
        actions.append(_mission_action("mission_gather_intel", "Gather Intel", "GATHER_INTEL"))
        actions.append(_mission_action("mission_undermine", "Undermine Alliances", "UNDERMINE_ALLIANCE"))

    elif state == "OPEN_BORDERS":
        actions.append(_proposal_action("propose_non_aggression", "Propose Non-Aggression", "NON_AGGRESSION"))
        actions.append(_proposal_action("propose_vassal", "Propose Vassal", "VASSAL"))
        actions.append({"action": "declare_war", "display_name": "Declare War", "dp_cost": 1, "available": dp >= 1, "disabled_reason": "" if dp >= 1 else "Insufficient DP"})
        has_treaty = diplo_key in active_treaties
        bt_available = dp >= 1 and has_treaty
        bt_reason = "" if bt_available else ("No active treaty" if not has_treaty else "Insufficient DP")
        actions.append({"action": "break_treaty", "display_name": "Break Treaty", "dp_cost": 1, "available": bt_available, "disabled_reason": bt_reason})
        actions.append({"action": "downgrade", "display_name": "Downgrade", "dp_cost": 1, "available": dp >= 1, "disabled_reason": "" if dp >= 1 else "Insufficient DP"})
        ult_available = True
        ult_reason = ""
        ult_cd = ultimatum_cooldowns.get(target_nation, 0)
        if ult_cd > 0:
            ult_available = False
            ult_reason = f"Cooldown: {ult_cd} turns"
        elif dp < 2:
            ult_available = False
            ult_reason = "Insufficient DP"
        actions.append({"action": "send_ultimatum", "display_name": "Send Ultimatum", "dp_cost": 2, "available": ult_available, "disabled_reason": ult_reason})
        actions.append(_mission_action("mission_improve_relations", "Improve Relations", "IMPROVE_RELATIONS"))
        actions.append(_mission_action("mission_court", "Court Nation", "COURT_NATION"))
        actions.append(_mission_action("mission_gather_intel", "Gather Intel", "GATHER_INTEL"))
        actions.append(_mission_action("mission_undermine", "Undermine Alliances", "UNDERMINE_ALLIANCE"))

    elif state == "NON_AGGRESSION":
        actions.append(_proposal_action("propose_defensive_alliance", "Propose Defensive Alliance", "DEFENSIVE_ALLIANCE"))
        actions.append(_proposal_action("propose_vassal", "Propose Vassal", "VASSAL"))
        actions.append({"action": "declare_war", "display_name": "Declare War", "dp_cost": 1, "available": dp >= 1, "disabled_reason": "" if dp >= 1 else "Insufficient DP"})
        has_treaty = diplo_key in active_treaties
        bt_available = dp >= 1 and has_treaty
        bt_reason = "" if bt_available else ("No active treaty" if not has_treaty else "Insufficient DP")
        actions.append({"action": "break_treaty", "display_name": "Break Treaty", "dp_cost": 1, "available": bt_available, "disabled_reason": bt_reason})
        actions.append({"action": "downgrade", "display_name": "Downgrade", "dp_cost": 1, "available": dp >= 1, "disabled_reason": "" if dp >= 1 else "Insufficient DP"})
        ult_available = True
        ult_reason = ""
        ult_cd = ultimatum_cooldowns.get(target_nation, 0)
        if ult_cd > 0:
            ult_available = False
            ult_reason = f"Cooldown: {ult_cd} turns"
        elif dp < 2:
            ult_available = False
            ult_reason = "Insufficient DP"
        actions.append({"action": "send_ultimatum", "display_name": "Send Ultimatum", "dp_cost": 2, "available": ult_available, "disabled_reason": ult_reason})
        actions.append(_mission_action("mission_improve_relations", "Improve Relations", "IMPROVE_RELATIONS"))
        actions.append(_mission_action("mission_court", "Court Nation", "COURT_NATION"))
        actions.append(_mission_action("mission_gather_intel", "Gather Intel", "GATHER_INTEL"))
        actions.append(_mission_action("mission_undermine", "Undermine Alliances", "UNDERMINE_ALLIANCE"))

    elif state == "DEFENSIVE_ALLIANCE":
        actions.append(_proposal_action("propose_alliance", "Propose Alliance", "ALLIANCE"))
        actions.append(_proposal_action("propose_vassal", "Propose Vassal", "VASSAL"))
        actions.append({"action": "declare_war", "display_name": "Declare War", "dp_cost": 1, "available": dp >= 1, "disabled_reason": "" if dp >= 1 else "Insufficient DP"})
        has_treaty = diplo_key in active_treaties
        bt_available = dp >= 1 and has_treaty
        bt_reason = "" if bt_available else ("No active treaty" if not has_treaty else "Insufficient DP")
        actions.append({"action": "break_treaty", "display_name": "Break Treaty", "dp_cost": 1, "available": bt_available, "disabled_reason": bt_reason})
        actions.append({"action": "downgrade", "display_name": "Downgrade", "dp_cost": 1, "available": dp >= 1, "disabled_reason": "" if dp >= 1 else "Insufficient DP"})
        actions.append(_mission_action("mission_improve_relations", "Improve Relations", "IMPROVE_RELATIONS"))
        actions.append(_mission_action("mission_reassure", "Reassure Ally", "REASSURE_ALLY"))
        actions.append(_mission_action("mission_gather_intel", "Gather Intel", "GATHER_INTEL"))
        actions.append(_mission_action("mission_undermine", "Undermine Alliances", "UNDERMINE_ALLIANCE"))

    elif state == "ALLIANCE":
        actions.append({"action": "declare_war", "display_name": "Declare War", "dp_cost": 1, "available": dp >= 1, "disabled_reason": "" if dp >= 1 else "Insufficient DP"})
        has_treaty = diplo_key in active_treaties
        bt_available = dp >= 1 and has_treaty
        bt_reason = "" if bt_available else ("No active treaty" if not has_treaty else "Insufficient DP")
        actions.append({"action": "break_treaty", "display_name": "Break Treaty", "dp_cost": 1, "available": bt_available, "disabled_reason": bt_reason})
        actions.append({"action": "downgrade", "display_name": "Downgrade", "dp_cost": 1, "available": dp >= 1, "disabled_reason": "" if dp >= 1 else "Insufficient DP"})
        actions.append(_mission_action("mission_reassure", "Reassure Ally", "REASSURE_ALLY"))
        actions.append(_mission_action("mission_gather_intel", "Gather Intel", "GATHER_INTEL"))
        actions.append(_mission_action("mission_undermine", "Undermine Alliances", "UNDERMINE_ALLIANCE"))

    return actions


def get_diplomatic_preview(world, target_nation: str) -> Dict:
    """Build the full diplomatic preview response for a nation (§3c)."""
    player = getattr(world, 'player_nation', 'France')
    diplo_key = world._make_diplo_key(player, target_nation)
    state = world.diplomatic_states.get(diplo_key, "PEACE")
    relation = world.nation_relations.get(diplo_key, 0)
    dp = int(getattr(world, 'diplomatic_points', 0))
    vassals = getattr(world, 'vassals', {})
    is_vassal = target_nation in vassals

    dialogue_pending = getattr(world, 'pending_diplomatic_dialogue', None) is not None
    talleyrand_state = getattr(world, 'talleyrand_state', 'IDLE')

    response = {
        "nation": target_nation,
        "state": state,  # Bug 7 fix: alias for wizard consistency with Step 1
        "current_state": state,
        "current_state_display": _STATE_DISPLAY_NAMES.get(state, state),
        "relation": int(relation),
        "relation_descriptor": get_relation_descriptor(relation),
        "dp_available": int(dp),
        "dialogue_pending": dialogue_pending,
        "talleyrand_in_transit": talleyrand_state == "IN_TRANSIT",
        "is_vassal": is_vassal,
    }

    if is_vassal:
        from backend.game_logic.vassal import AUTONOMY_NAMES, AUTONOMY_DRIFT
        v = vassals[target_nation]
        loyalty = v.get("loyalty", 50)
        autonomy = v.get("autonomy", 1)
        drift = AUTONOMY_DRIFT.get(autonomy, 0)
        if drift > 0:
            trend = "rising"
        elif drift < 0:
            trend = "falling"
        else:
            trend = "stable"
        response["vassal_loyalty"] = int(loyalty)
        response["vassal_autonomy"] = AUTONOMY_NAMES.get(autonomy, "Satellite")
        response["vassal_loyalty_trend"] = trend
        tribute_rate = v.get("tribute_rate", 0.5)
        vassal_income = sum(50 for r in world.regions.values() if getattr(r, 'controller', '') == target_nation)
        response["vassal_tribute"] = int(vassal_income * tribute_rate)
        response["section"] = "vassal_management"
    else:
        response["section"] = "foreign_affairs"

    response["assessment"] = get_assessment_text(world, target_nation)
    actions = get_available_diplomatic_actions(world, target_nation)
    response["actions"] = actions
    response["recommendation"] = _build_recommendation(world, target_nation, actions, dp, is_vassal, vassals)

    # W3: Acceptance preview — top 3 positive/negative factors for best proposal
    acceptance_preview = None
    best_proposal_action = None
    best_score = -999
    for a in actions:
        if a.get("available") and a["action"].startswith("propose_"):
            score = a.get("likelihood_score", 0)
            if score > best_score:
                best_score = score
                best_proposal_action = a
    if best_proposal_action:
        try:
            # Build a mock proposal to get components
            action_to_type = {
                "propose_armistice": "armistice_winning" if (get_war_score_for(world, player, target) > 0) else "armistice_losing",
                "propose_peace": "peace",
                "propose_open_borders": "open_borders",
                "propose_non_aggression": "non_aggression",
                "propose_defensive_alliance": "defensive_alliance",
                "propose_alliance": "alliance",
                "propose_vassal": "vassalage",
            }
            ptype = action_to_type.get(best_proposal_action["action"], "peace")
            mock_proposal = {
                "type": ptype,
                "proposer_nation": player,
                "target_nation": target_nation,
                "sweeteners": [],
                "demands": [],
                "clauses": [],
            }
            result = calculate_acceptance(mock_proposal, world)
            components = result.get("components", {})

            # Human-readable labels for components
            _COMPONENT_LABELS = {
                "base_disposition": "Base willingness",
                "war_score_modifier": "Our military dominance",
                "relation_modifier": "Current relations",
                "war_weariness": "Exhaustion from prolonged conflict",
                "stalemate_duration": "Stalemate weariness",
                "threat_modifier": "Fear of French expansion",
                "coalition_penalty": "Coalition loyalty binds them",
                "deal_balance": "Deal terms",
                "diplomat_skill_bonus": "Diplomatic skill advantage",
                "personality_modifier": "Diplomat personality",
                "military_supremacy": "Military supremacy",
                "battlefield_diplomacy": "Battlefield diplomacy",
                "military_pressure": "Military pressure",
                "special_desire_bonus": "Appeals to core interests",
                "harshness_bonus": "Previous treaty precedent",
                "reliability_modifier": "Our diplomatic reputation",
            }

            positives = []
            negatives = []
            for key, val in components.items():
                if not val:
                    continue
                label = _COMPONENT_LABELS.get(key, key.replace("_", " ").title())
                entry = {"key": key, "label": label, "value": int(round(val or 0))}
                if val > 0:
                    positives.append(entry)
                else:
                    negatives.append(entry)

            # Sort by magnitude, take top 3
            positives.sort(key=lambda x: x["value"], reverse=True)
            negatives.sort(key=lambda x: x["value"])
            acceptance_preview = {
                "positive": positives[:3],
                "negative": negatives[:3],
            }
        except Exception:
            acceptance_preview = None
    response["acceptance_preview"] = acceptance_preview

    return response


def _build_recommendation(world, target_nation: str, actions: List[Dict],
                          dp: int, is_vassal: bool, vassals: dict) -> str:
    """Build Talleyrand's recommendation (§3f tiers)."""
    if dp <= 0:
        return "Our diplomatic reserves are spent. We must wait."

    if is_vassal:
        v = vassals.get(target_nation, {})
        loyalty = v.get("loyalty", 50)
        if loyalty < 25:
            return "Talleyrand recommends: Invest to strengthen loyalty"
        return "No urgent action needed"

    best_proposal = None
    best_score = -999
    for a in actions:
        if not a.get("available"):
            continue
        score = a.get("likelihood_score", 0)
        if a["action"].startswith("propose_"):
            if score > best_score:
                best_score = score
                best_proposal = a

    if best_proposal and best_score >= 40:
        return f"Talleyrand recommends: {best_proposal['display_name']}"

    # W6: When all proposals are hopeless, suggest improve relations mission if available
    if best_score < 40:
        for a in actions:
            if a.get("available") and a["action"] == "mission_improve_relations":
                return "No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate."

    return "Relations must improve before proposals will find purchase. A battlefield victory would change their calculus."
