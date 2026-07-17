"""
Talleyrand Diplomatic Defiance System — Phase 8 Session 6

Mirrors V2b combat defiance (defiance.py) for the diplomatic layer.
Talleyrand may modify proposals before delivery when authority is low.

Core functions:
- calculate_diplomatic_defiance_chance(): probability curve (§3a)
- apply_diplomatic_sabotage(): what Talleyrand changes (§3b)
- check_sabotage_discovery(): turn-based discovery check (§3c)
- evaluate_pre_proposal_objection(): V2a-pattern objection before departure (§3e)
- roll_drafting_pushback(): PL-23 authority-driven pushback during drafting
- apply_pen_nudge(): PL-23 deterministic term softening
"""

import copy
import random
from typing import Dict, Optional

from backend.commands.objection_v2 import ConcernLevel
from backend.nation_config import get_player_nation


# ════════════════════════════════════════════════════════════════════════════
# §3a — DEFIANCE PROBABILITY CURVE
# ════════════════════════════════════════════════════════════════════════════

SCHEMER_FLOOR = 0.02  # 2% — the absolute Schemer minimum (low authority; curve dominates)
DEFIANCE_CAP = 0.30   # 30% hard cap

# E7 (8.EVAL Batch Q, July 16 2026): at high authority the base curve collapses
# to 0.00, so the flat 2% floor left the ENTIRE sabotage/discovery/confrontation
# /redemption arc + its two shipped popups as near-dead content — at boot
# authority 100 a Schemer defied barely 1-in-50 proposals. A strong Emperor
# should still meet OCCASIONAL Talleyrand mischief. The floor is now authority-
# BANDED (the Jealousy §0.2-11b boot-dormancy precedent — a banded floor, NOT a
# flat curve raise): lifted at high authority, easing to the ordinary curve below
# it (where the curve already exceeds the floor, so nothing changes). Balance
# numbers (escalate to the gate).
STRONG_EMPEROR_AUTHORITY_BAND = 70    # authority >= this uses the lifted floor
STRONG_EMPEROR_DEFIANCE_FLOOR = 0.05  # 5% — a strong Emperor still sees mischief


def _defiance_floor_for_authority(authority: int) -> float:
    """E7: the banded lower bound on the defiance chance. Lifted to 5% for a
    strong Emperor (authority >= 70) so the sabotage arc is reachable; the
    ordinary 2% Schemer floor applies below the band, where the base curve is
    already well above it (so the floor is moot — the curve dominates)."""
    if authority >= STRONG_EMPEROR_AUTHORITY_BAND:
        return STRONG_EMPEROR_DEFIANCE_FLOOR
    return SCHEMER_FLOOR


def calculate_diplomatic_defiance_chance(talleyrand, world) -> float:
    """Calculate probability of Talleyrand defying the player's proposal.

    Mirrors V2b combat defiance curve with diplomat-specific parameters.
    Schemer personality always has a 2% floor (never fully controllable).

    Args:
        talleyrand: DiplomaticRepresentative (France's diplomat)
        world: WorldState for authority/cooldown data

    Returns:
        Float probability (0.02 to 0.30 for schemer, 0.0 for loyalist)
    """
    # Loyalist personality: no defiance (post-Replace path)
    personality = getattr(talleyrand, 'personality', 'schemer')
    if personality == 'loyalist':
        return 0.0

    # Cooldown check
    cooldown = getattr(world, 'talleyrand_defiance_cooldown', 0)
    if cooldown > 0:
        return 0.0

    # Base: 5% — rare by default
    base = 0.05

    # Authority modifier
    authority = world.authority_tracker.authority
    if authority >= 80:
        base += -0.05  # Strong Emperor → obeys
    elif authority >= 60:
        base += 0.00   # Neutral
    elif authority >= 40:
        base += 0.05   # Weakening → "helps"
    else:
        base += 0.15   # Weak Emperor → takes charge

    # PL-23: Trust removed — authority is sole driver of Talleyrand's independence

    # Variance: random.uniform(-0.05, 0.05)
    variance = random.uniform(-0.05, 0.05)
    final = base + variance

    # Hard cap and E7 authority-banded floor
    final = min(DEFIANCE_CAP, final)
    final = max(_defiance_floor_for_authority(authority), final)

    return final


def calculate_diplomatic_defiance_chance_deterministic(talleyrand, world) -> float:
    """Deterministic version for mock mode / testing (no variance).

    Returns the exact midpoint probability without random variance.
    """
    personality = getattr(talleyrand, 'personality', 'schemer')
    if personality == 'loyalist':
        return 0.0

    cooldown = getattr(world, 'talleyrand_defiance_cooldown', 0)
    if cooldown > 0:
        return 0.0

    base = 0.05

    authority = world.authority_tracker.authority
    if authority >= 80:
        base += -0.05
    elif authority >= 60:
        base += 0.00
    elif authority >= 40:
        base += 0.05
    else:
        base += 0.15

    # PL-23: Trust removed — authority is sole driver

    return min(DEFIANCE_CAP, max(_defiance_floor_for_authority(authority), base))


# ════════════════════════════════════════════════════════════════════════════
# §3b — WHAT TALLEYRAND CHANGES (sabotage application)
# ════════════════════════════════════════════════════════════════════════════

def calculate_proposal_harshness(proposal: Dict) -> float:
    """Calculate harshness score (0.0-1.0) from proposal contents.

    Harshness is driven by demands and clauses:
    - Territory demands: +0.2 per region (or per value count)
    - Gold per-turn demands: +0.1 per 100 gold/turn
    - Gold lump demands: +0.1 per 500 gold (lower weight, one-time)
    - AP demands: +0.3 per AP/turn
    - Manpower demands: +0.15 per 1000 troops
    - Sweeteners: -0.1 per sweetener
    """
    harshness = 0.0

    for demand in proposal.get("demands", []):
        dtype = demand.get("type", "")
        if dtype == "territory_cede":
            regions = demand.get("regions", [])
            if regions:
                harshness += 0.2 * len(regions)
            else:
                harshness += 0.2 * max(1, demand.get("value", 1))
        elif dtype == "gold_per_turn":
            harshness += 0.1 * (max(0, demand.get("value", 0)) / 100)
        elif dtype == "gold_lump":
            harshness += 0.1 * (max(0, demand.get("value", 0)) / 500)
        elif dtype == "ap_per_turn":
            harshness += 0.3 * max(1, demand.get("value", 1))
        elif dtype in ("manpower_infantry", "manpower_cavalry", "manpower_artillery"):
            value = demand.get("value", 0)
            harshness += max(0.15, 0.15 * (value / 1000))

    for sweetener in proposal.get("sweeteners", []):
        harshness -= 0.1

    # Vassalage proposals are inherently harsh
    if proposal.get("type") == "vassalage":
        harshness += 0.3

    return max(0.0, min(1.0, harshness))


def apply_diplomatic_sabotage(original_proposal: Dict, talleyrand, world) -> Dict:
    """Modify proposal based on Talleyrand's judgment (§3b).

    Returns a sabotage record with original_proposal, modified_proposal,
    defiance_type, and discovery_chance.

    Args:
        original_proposal: The proposal as the player ordered
        talleyrand: DiplomaticRepresentative
        world: WorldState

    Returns:
        Sabotage record dict
    """
    modified = _deep_copy_proposal(original_proposal)
    harshness = calculate_proposal_harshness(original_proposal)
    defiance_type = "stalled"  # default

    # Count territory demands
    territory_demands = [d for d in modified.get("demands", []) if d.get("type") == "territory_cede"]
    territory_count = sum(len(d.get("regions", [])) for d in territory_demands)

    # Check for AP/turn demands
    ap_demands = [d for d in modified.get("demands", []) if d.get("type") == "ap_per_turn"]

    # Check for unit trade
    unit_demands = [d for d in modified.get("demands", []) if d.get("type") == "unit_trade"]

    if ap_demands:
        # AP/turn demand → downgrade to gold/turn equivalent
        for demand in list(modified.get("demands", [])):
            if demand.get("type") == "ap_per_turn":
                modified["demands"].remove(demand)
                modified["demands"].append({
                    "type": "gold_per_turn",
                    "value": 200,  # Gold equivalent
                })
        defiance_type = "ap_downgrade"
    elif unit_demands:
        # Unit trade → overpay by 100%
        for demand in modified.get("demands", []):
            if demand.get("type") == "unit_trade":
                demand["value"] = int(demand.get("value", 1000) * 2)
        defiance_type = "unit_overpay"
    elif territory_count >= 3:
        # Too many territory demands → reduce by 1
        for demand in list(modified.get("demands", [])):
            if demand.get("type") == "territory_cede":
                regions = demand.get("regions", [])
                if len(regions) > 1:
                    demand["regions"] = regions[:-1]  # Remove last region
                    break
                elif len(regions) == 1:
                    # Fix 14: Single region — remove entire demand instead of leaving empty list
                    modified["demands"].remove(demand)
                    break
        defiance_type = "softened"
    elif harshness > 0.7:
        # Harsh terms → cut gold by 40%
        for demand in modified.get("demands", []):
            if demand.get("type") == "gold_per_turn":
                demand["value"] = int(demand.get("value", 0) * 0.6)
        defiance_type = "softened"
    elif harshness < 0.3:
        # Too generous → add face-saving clause, increase gold 30%
        for demand in modified.get("demands", []):
            if demand.get("type") == "gold_per_turn":
                demand["value"] = int(demand.get("value", 0) * 1.3)
        # If no gold demand, add a small one
        gold_demands = [d for d in modified.get("demands", []) if d.get("type") == "gold_per_turn"]
        if not gold_demands:
            modified.setdefault("demands", []).append({
                "type": "gold_per_turn",
                "value": 50,
            })
        defiance_type = "hardened"
    else:
        # Middle harshness → stall (delivery delay +1)
        defiance_type = "stalled"

    sabotage_record = {
        "original_proposal": original_proposal,
        "modified_proposal": modified,
        "defiance_type": defiance_type,
        "discovery_chance": 0.40,  # 40% base
        "turns_hidden": 0,
        "discovered": False,
        "target_nation": original_proposal.get("target_nation", ""),
    }

    return sabotage_record


def _deep_copy_proposal(proposal: Dict) -> Dict:
    """Deep copy a proposal dict (full depth via copy.deepcopy)."""
    return copy.deepcopy(proposal)


# ════════════════════════════════════════════════════════════════════════════
# §3c — DISCOVERY
# ════════════════════════════════════════════════════════════════════════════

def check_sabotage_discovery(sabotage: Dict, world) -> bool:
    """Check if Talleyrand's sabotage is discovered this turn.

    40% base + 10% per turn cumulative.
    Called during Morning Dispatch building.

    Args:
        sabotage: The pending_talleyrand_sabotage record
        world: WorldState

    Returns:
        True if discovery happens this turn
    """
    if sabotage.get("discovered"):
        return False  # Already discovered

    base_chance = 0.40
    turns_hidden = sabotage.get("turns_hidden", 0)
    cumulative = turns_hidden * 0.10
    total_chance = min(1.0, base_chance + cumulative)

    # In mock/deterministic mode, use threshold check
    roll = random.random()
    return roll < total_chance


def check_sabotage_discovery_deterministic(sabotage: Dict) -> bool:
    """Deterministic discovery check for testing.

    Returns True if cumulative chance >= 0.5 (fires on turn 2+).
    """
    base_chance = 0.40
    turns_hidden = sabotage.get("turns_hidden", 0)
    total_chance = min(1.0, base_chance + turns_hidden * 0.10)
    return total_chance >= 0.50


def build_confrontation_dialogue(sabotage: Dict, talleyrand) -> Dict:
    """Build the sabotage confrontation dialogue (T22 template).

    Shows what was ordered vs what was delivered + Talleyrand's reasoning.

    Args:
        sabotage: The pending_talleyrand_sabotage record
        talleyrand: DiplomaticRepresentative

    Returns:
        Dict suitable for pending_diplomatic_dialogue
    """
    original = sabotage.get("original_proposal", {})
    modified = sabotage.get("modified_proposal", {})
    defiance_type = sabotage.get("defiance_type", "stalled")
    target_nation = sabotage.get("target_nation", "them")

    # Build reasoning text based on defiance type
    reasoning_map = {
        "softened": (
            "Sire, I adjusted the terms because demanding too much "
            "would have ensured rejection. The result speaks for itself."
        ),
        "hardened": (
            "Sire, I strengthened our position slightly. "
            "Appearing too generous invites contempt, not gratitude."
        ),
        "stalled": (
            "Sire, I delayed delivery by one turn. "
            "I left the door open — timing in diplomacy is everything."
        ),
        "ap_downgrade": (
            "Sire, I converted the AP demand to gold. "
            "AP demands breed rebellion faster than anything else."
        ),
        "unit_overpay": (
            "Sire, I offered more units than you specified. "
            "They were much more amenable to the increased offer."
        ),
    }
    reasoning = reasoning_map.get(defiance_type, "I used my judgment, Sire.")

    # Build summary of differences
    original_summary = _summarize_proposal(original)
    modified_summary = _summarize_proposal(modified)

    talleyrand_text = (
        f"Berthier's agents report that the proposal delivered to "
        f"{target_nation} was not precisely as you ordered.\n\n"
        f"You ordered: {original_summary}\n"
        f"Talleyrand sent: {modified_summary}\n\n"
        f"Talleyrand: \"{reasoning}\""
    )

    return {
        "type": "sabotage_confrontation",
        "target_nation": target_nation,
        "talleyrand_text": talleyrand_text,
        "options": [
            {
                "label": "Confront",
                "description": "Authority +5, defiance cooldown 5 turns.",
                "action": "confront_sabotage",
            },
            {
                "label": "Overlook",
                "description": "Authority -3. Talleyrand gains confidence.",
                "action": "overlook_sabotage",
            },
        ],
        "context": {
            "defiance_type": defiance_type,
            "original_proposal": original,
            "modified_proposal": modified,
        },
        "turn_created": sabotage.get("turn_created", 1),
        "blocking": True,
        "sabotage_record": sabotage,
    }


def _summarize_proposal(proposal: Dict) -> str:
    """Generate a human-readable summary of proposal terms."""
    from backend.display_names import summarize_proposal

    return summarize_proposal(proposal)


# ════════════════════════════════════════════════════════════════════════════
# CONFRONTATION RESOLUTION
# ════════════════════════════════════════════════════════════════════════════

def resolve_confrontation(choice: str, talleyrand, world) -> Dict:
    """Resolve the player's response to sabotage discovery.

    Args:
        choice: "confront_sabotage" or "overlook_sabotage"
        talleyrand: DiplomaticRepresentative
        world: WorldState

    Returns:
        Dict with trust_change, authority_change, cooldown, message
    """
    result = {
        "authority_change": 0,
        "cooldown_set": 0,
        "message": "",
    }

    if choice == "confront_sabotage":
        # PL-23: Authority +5, cooldown 5 turns (trust removed)
        world.authority_tracker.modify_authority(+5)
        result["authority_change"] = +5

        world.talleyrand_defiance_cooldown = 5
        result["cooldown_set"] = 5

        result["message"] = (
            "You confront Talleyrand directly. He accepts the rebuke with "
            "characteristic grace, but his eyes betray resentment."
        )
    elif choice == "overlook_sabotage":
        # PL-23: Authority -3 (trust removed, mild authority cost for letting it slide)
        world.authority_tracker.modify_authority(-3)
        result["authority_change"] = -3

        result["message"] = (
            "You choose to overlook the discrepancy. Talleyrand inclines "
            "his head — a small acknowledgment that his judgment was trusted."
        )

    # Clear the pending sabotage
    world.pending_talleyrand_sabotage = None

    return result


# §3d — REDEMPTION EVENT — DELETED (PL-23: trust system removed)


# ════════════════════════════════════════════════════════════════════════════
# §3e — PRE-PROPOSAL OBJECTION (V2a pattern)
# ════════════════════════════════════════════════════════════════════════════

def evaluate_pre_proposal_objection(
    proposal: Dict,
    talleyrand,
    world,
) -> ConcernLevel:
    """Evaluate Talleyrand's concern about a proposal before departure.

    Uses V2a ConcernLevel pattern. Schemer personality objects based on
    strategic calculation, not honor or fear.

    Args:
        proposal: The proposal dict
        talleyrand: DiplomaticRepresentative
        world: WorldState

    Returns:
        ConcernLevel (NONE, MILD, MODERATE, STRONG)
    """
    personality = getattr(talleyrand, 'personality', 'schemer')

    # Loyalist personality: never objects (just follows orders)
    if personality == 'loyalist':
        return ConcernLevel.NONE

    harshness = calculate_proposal_harshness(proposal)
    target_nation = proposal.get("target_nation", "")

    # Get diplomatic context
    authority = world.authority_tracker.authority if hasattr(world, 'authority_tracker') else 60
    player_nation = get_player_nation(world)
    # War declaration on neutral → STRONG
    current_state = world.get_diplomatic_state(player_nation, target_nation) if target_nation else "PEACE"
    if proposal.get("type") == "war_declaration" and current_state not in ("WAR",):
        return ConcernLevel.STRONG

    # PL-23: Harsh terms → MODERATE or STRONG based on authority (trust removed)
    if harshness > 0.7:
        if authority < 50:
            return ConcernLevel.STRONG
        return ConcernLevel.MODERATE

    # Generous terms when winning → MILD. G4F-8 follow-through: "offering
    # such generous terms... it rewards their failure" means GIVING WITHOUT
    # TAKING, so it fires only when the package demands nothing. The old
    # `harshness < 0.3` gate caught a one-region cession or a 200-gold
    # tribute (weight 0.2 each) and grumbled "too generous" at real
    # demands — the live-smoke contradiction class.
    if not proposal.get("demands") and target_nation:
        diplo_key = world._make_diplo_key(player_nation, target_nation)
        war_score = world.war_scores.get(diplo_key, 0)
        # Adjust sign for France perspective
        parts = diplo_key.split("|")
        if len(parts) == 2 and parts[0] == target_nation:
            war_score = -war_score
        if war_score > 20:
            return ConcernLevel.MILD

    return ConcernLevel.NONE


def get_objection_text(concern_level: ConcernLevel, proposal: Dict, talleyrand) -> str:
    """Get Talleyrand's objection text for a given concern level.

    Args:
        concern_level: ConcernLevel
        proposal: The proposal dict
        talleyrand: DiplomaticRepresentative

    Returns:
        Objection text string
    """
    target = proposal.get("target_nation", "them")

    if concern_level == ConcernLevel.STRONG:
        if proposal.get("type") == "war_declaration":
            return (
                f"Sire, {target} has given us no cause for war. "
                f"Attacking them is how coalitions are born."
            )
        return (
            "Sire, these terms will unite all of Europe against us. "
            "The courts are watching."
        )

    if concern_level == ConcernLevel.MODERATE:
        return (
            f"Sire, I must counsel caution. Demanding too much from "
            f"{target} may ensure they never forgive us."
        )

    if concern_level == ConcernLevel.MILD:
        return (
            f"Sire, offering such generous terms to {target} while "
            f"we hold the advantage... it rewards their failure."
        )

    return ""


# ════════════════════════════════════════════════════════════════════════════
# HONESTY PROBLEM (§10c)
# ════════════════════════════════════════════════════════════════════════════

def record_override(world, proposal_type: str, override_result: str) -> None:
    """Record when player overrides Talleyrand's objection.

    Args:
        world: WorldState
        proposal_type: Type of proposal overridden
        override_result: "good" or "bad"
    """
    history = getattr(world, 'talleyrand_override_history', [])
    history.append({
        "proposal_type": proposal_type,
        "override_result": override_result,
        "turn": int(world.current_turn),
    })
    # Keep last 5 overrides only
    world.talleyrand_override_history = history[-5:]


def get_override_dispatch_note(world) -> Optional[str]:
    """Generate Morning Dispatch note about recent override outcomes.

    Args:
        world: WorldState

    Returns:
        Note string or None if no recent overrides
    """
    history = getattr(world, 'talleyrand_override_history', [])
    if not history:
        return None

    # Only report on most recent override
    latest = history[-1]
    if latest.get("turn", 0) < world.current_turn - 1:
        return None  # Only report recent overrides

    if latest.get("override_result") == "good":
        return (
            "Talleyrand's assessment appears to have been... pessimistic. "
            "The proposal succeeded despite his warnings."
        )
    elif latest.get("override_result") == "bad":
        return (
            "Talleyrand's warnings prove prescient. "
            "The diplomatic outcome was not as we hoped."
        )

    return None


# ════════════════════════════════════════════════════════════════════════════
# PL-23 — DRAFTING PUSHBACK (authority-driven, probabilistic)
# ════════════════════════════════════════════════════════════════════════════

def roll_drafting_pushback(terms: Dict, context: Dict, world) -> bool:
    """Roll whether Talleyrand pushes back during drafting.

    Called at each modify_harsh/modify_generous/ultimatum confirm step.
    Returns True if Talleyrand intercepts with his own version.

    Args:
        terms: Current proposal terms dict (with demands/sweeteners)
        context: Dialogue context dict (must have proposal_type, may have objection_resolved)
        world: WorldState

    Returns:
        True if pushback fires, False otherwise
    """
    # AM-23.15: Already pushed back on this proposal → no re-roll
    if context.get("objection_resolved"):
        return False

    # AM-23.1: Empty demands → nothing to soften
    demands = terms.get("demands", [])
    if not demands:
        return False

    # Loyalist personality: never pushes back
    diplomats = getattr(world, 'diplomats', {})
    talleyrand = diplomats.get(world.player_nation)
    if not talleyrand:
        return False
    personality = getattr(talleyrand, 'personality', 'schemer')
    if personality == 'loyalist':
        return False

    harshness = calculate_proposal_harshness(terms)

    # Base chance from harshness
    if harshness <= 0.4:
        base = 0.0
    elif harshness <= 0.7:
        base = 0.05
    else:
        base = 0.15

    # No pushback on reasonable terms
    if base == 0.0:
        return False

    # Authority modifier (sole driver — PL-23)
    authority = world.authority_tracker.authority if hasattr(world, 'authority_tracker') else 60
    if authority >= 80:
        base -= 0.10
    elif authority < 50:
        base += 0.10

    # Variance ±5%
    variance = random.uniform(-0.05, 0.05)
    final = base + variance

    # Cap at 30%, schemer floor at 2% (when harshness > 0.4)
    final = min(0.30, final)
    final = max(0.02, final)

    return random.random() < final


def roll_drafting_pushback_deterministic(terms: Dict, context: Dict, world) -> float:
    """Deterministic version for testing — returns the probability without rolling.

    Same logic as roll_drafting_pushback but no random variance or roll.
    """
    if context.get("objection_resolved"):
        return 0.0

    demands = terms.get("demands", [])
    if not demands:
        return 0.0

    diplomats = getattr(world, 'diplomats', {})
    talleyrand = diplomats.get(world.player_nation)
    if not talleyrand:
        return 0.0
    personality = getattr(talleyrand, 'personality', 'schemer')
    if personality == 'loyalist':
        return 0.0

    harshness = calculate_proposal_harshness(terms)

    if harshness <= 0.4:
        return 0.0
    elif harshness <= 0.7:
        base = 0.05
    else:
        base = 0.15

    authority = world.authority_tracker.authority if hasattr(world, 'authority_tracker') else 60
    if authority >= 80:
        base -= 0.10
    elif authority < 50:
        base += 0.10

    return min(0.30, max(0.02, base))


def apply_pen_nudge(terms: Dict) -> Dict:
    """Apply Talleyrand's pen nudge — soften the harshest demand.

    Deterministic: finds the demand with highest harshness contribution
    and reduces it by 20%. Returns a modified copy.

    Pen nudge rules:
    1. Find demand with highest harshness contribution
    2. If numeric (gold/manpower): reduce by 20%, remove if ≤ 0
    3. If territory with regions list: remove last region
    4. If territory with value shape: reduce by 1, remove if ≤ 0
    5. If only AP demands remain: leave AP, add gold sweetener
    6. Recalculate harshness on result

    Args:
        terms: Proposal terms dict

    Returns:
        Modified copy of terms with the nudge applied
    """
    import copy
    nudged = copy.deepcopy(terms)
    demands = nudged.get("demands", [])
    if not demands:
        return nudged

    # Score each demand's harshness contribution
    scored = []
    for i, d in enumerate(demands):
        dtype = d.get("type", "")
        value = d.get("value", 0)
        if dtype == "territory_cede":
            regions = d.get("regions", [])
            score = 0.2 * len(regions) if regions else 0.2 * max(1, value)
        elif dtype == "gold_per_turn":
            score = 0.1 * (value / 100)
        elif dtype == "gold_lump":
            score = 0.1 * (value / 500)
        elif dtype == "ap_per_turn":
            score = 0.3 * max(1, value)
        elif dtype in ("manpower_infantry", "manpower_cavalry", "manpower_artillery"):
            score = max(0.15, 0.15 * (value / 1000))
        else:
            score = 0.0
        scored.append((score, i, dtype))

    # Sort by score descending, tie-break: territory > gold > manpower > AP
    _TYPE_ORDER = {"territory_cede": 0, "gold_per_turn": 1, "gold_lump": 1, "manpower_infantry": 2, "manpower_cavalry": 2, "manpower_artillery": 2, "ap_per_turn": 3}
    scored.sort(key=lambda x: (-x[0], _TYPE_ORDER.get(x[2], 99)))

    if not scored or scored[0][0] == 0.0:
        return nudged

    _, target_idx, target_type = scored[0]
    target_demand = demands[target_idx]

    # Rule 5: if only AP demands remain, add sweetener instead
    non_ap = [d for d in demands if d.get("type") != "ap_per_turn"]
    if not non_ap:
        nudged.setdefault("sweeteners", []).append({"type": "gold_per_turn", "value": 100})
        return nudged

    # Apply the nudge
    if target_type == "territory_cede":
        regions = target_demand.get("regions", [])
        if regions:
            # Remove last-added region
            regions.pop()
            if not regions:
                demands.pop(target_idx)
        else:
            # Value shape: reduce by 1
            new_val = target_demand.get("value", 1) - 1
            if new_val <= 0:
                demands.pop(target_idx)
            else:
                target_demand["value"] = new_val
    elif target_type in ("gold_per_turn", "gold_lump", "manpower_infantry", "manpower_cavalry", "manpower_artillery"):
        new_val = int(target_demand.get("value", 0) * 0.8)
        if new_val <= 0:
            demands.pop(target_idx)
        else:
            target_demand["value"] = new_val
    elif target_type == "ap_per_turn":
        new_val = int(target_demand.get("value", 1) * 0.8)
        if new_val <= 0:
            demands.pop(target_idx)
        else:
            target_demand["value"] = new_val

    return nudged


def apply_pen_nudge_personality(terms: Dict, world) -> Dict:
    """Apply personality-biased pen nudge (PL-25).

    Schemer: swaps the harshest demand type (territory → gold, AP → sweetener).
    Loyalist/other: standard 20% reduction via apply_pen_nudge().

    AM-25.1: If swap would create a duplicate demand type, merge values.
    If ALL swap targets occupied, fall back to 20% reduction.

    Args:
        terms: Proposal terms dict
        world: WorldState (for diplomat personality)

    Returns:
        Modified copy of terms with personality-biased nudge
    """
    diplomats = getattr(world, 'diplomats', {})
    talleyrand = diplomats.get(get_player_nation(world))
    personality = getattr(talleyrand, 'personality', 'schemer') if talleyrand else 'schemer'

    if personality != 'schemer':
        return apply_pen_nudge(terms)

    # Schemer: swap the harshest non-AP demand to a different type
    nudged = copy.deepcopy(terms)
    demands = nudged.get("demands", [])
    if not demands:
        return nudged

    # PL-25 AM-25.9: Get desire profile bias for target nation
    target_nation = terms.get("target_nation", "")
    from backend.game_logic.diplomatic_templates import get_desire_profile_nudge_bias
    bias = get_desire_profile_nudge_bias(target_nation)

    # Score demands (same as apply_pen_nudge, with desire profile multipliers)
    scored = []
    for i, d in enumerate(demands):
        dtype = d.get("type", "")
        value = d.get("value", 0)
        if dtype == "territory_cede":
            regions = d.get("regions", [])
            score = 0.2 * len(regions) if regions else 0.2 * max(1, value)
            score *= bias["territory_mult"]  # AM-25.9: 1.5x for territory-valuing nations
        elif dtype == "gold_per_turn":
            score = 0.1 * (value / 100)
        elif dtype == "gold_lump":
            score = 0.1 * (value / 500)
        elif dtype == "ap_per_turn":
            score = 0.3 * max(1, value)
        elif dtype in ("manpower_infantry", "manpower_cavalry", "manpower_artillery"):
            score = max(0.15, 0.15 * (value / 1000))
        else:
            score = 0.0
        scored.append((score, i, dtype))

    _TYPE_ORDER = {"territory_cede": 0, "gold_per_turn": 1, "gold_lump": 1,
                   "manpower_infantry": 2, "manpower_cavalry": 2, "manpower_artillery": 2,
                   "ap_per_turn": 3}
    scored.sort(key=lambda x: (-x[0], _TYPE_ORDER.get(x[2], 99)))

    if not scored or scored[0][0] == 0.0:
        return nudged

    # AM-25.9: Weakness override — if weakness matches a demand type, target it
    override_type = bias.get("nudge_override_type")
    target_idx = scored[0][1]
    target_type = scored[0][2]
    if override_type:
        for score, idx, dtype in scored:
            if dtype == override_type and score > 0:
                target_idx = idx
                target_type = dtype
                break

    target_demand = demands[target_idx]

    # AP-only → fall back to standard nudge (adds sweetener)
    non_ap = [d for d in demands if d.get("type") != "ap_per_turn"]
    if not non_ap:
        return apply_pen_nudge(terms)

    # Schemer swap: convert demand type to gold equivalent
    # Try swap targets in priority order: gold_per_turn → gold_lump → ap_per_turn
    swap_targets = ["gold_per_turn", "gold_lump", "ap_per_turn"]
    # Don't swap to the same type
    swap_targets = [t for t in swap_targets if t != target_type]

    swap_value = _estimate_gold_equivalent(target_demand)

    for swap_type in swap_targets:
        existing = [d for d in demands if d.get("type") == swap_type]
        if existing:
            # AM-25.1: Merge — add swap value to existing demand
            existing[0]["value"] = int(existing[0].get("value", 0) + swap_value)
            demands.pop(target_idx)
            return nudged
        else:
            # No collision — create new demand of swap type
            demands.pop(target_idx)
            demands.append({"type": swap_type, "value": int(swap_value)})
            return nudged

    # All swap targets occupied — fall back to 20% reduction
    return apply_pen_nudge(terms)


def _estimate_gold_equivalent(demand: Dict) -> int:
    """Estimate gold_per_turn equivalent of a demand for schemer swaps."""
    dtype = demand.get("type", "")
    value = demand.get("value", 0)
    if dtype == "territory_cede":
        regions = demand.get("regions", [])
        count = len(regions) if regions else max(1, value)
        return count * 150  # Each region ≈ 150 gold/turn
    elif dtype in ("manpower_infantry", "manpower_cavalry", "manpower_artillery"):
        return max(50, int(value * 0.05))  # 1000 troops ≈ 50 gold/turn
    elif dtype == "ap_per_turn":
        return max(1, value) * 200  # 1 AP ≈ 200 gold/turn
    elif dtype in ("gold_per_turn", "gold_lump"):
        return max(1, value)
    return 100
