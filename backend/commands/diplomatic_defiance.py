"""
Talleyrand Diplomatic Defiance System — Phase 8 Session 6

Mirrors V2b combat defiance (defiance.py) for the diplomatic layer.
Talleyrand may modify proposals before delivery when authority/trust are low.

Core functions:
- calculate_diplomatic_defiance_chance(): probability curve (§3a)
- apply_diplomatic_sabotage(): what Talleyrand changes (§3b)
- check_sabotage_discovery(): turn-based discovery check (§3c)
- evaluate_pre_proposal_objection(): V2a-pattern objection before departure (§3e)
- check_talleyrand_redemption(): trust ≤ 20 redemption event (§3d)
- apply_redemption_choice(): process player's redemption decision
"""

import copy
import random
from typing import Dict, Optional

from backend.commands.objection_v2 import ConcernLevel


# ════════════════════════════════════════════════════════════════════════════
# §3a — DEFIANCE PROBABILITY CURVE
# ════════════════════════════════════════════════════════════════════════════

SCHEMER_FLOOR = 0.02  # 2% — Schemer minimum, never fully tamed
DEFIANCE_CAP = 0.30   # 30% hard cap


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

    # Trust modifier (Talleyrand's personal trust)
    trust = talleyrand.trust if isinstance(talleyrand.trust, int) else int(talleyrand.trust)
    if trust >= 80:
        base += -0.05  # High loyalty
    elif trust >= 50:
        base += 0.00   # Neutral
    elif trust >= 30:
        base += 0.05   # Growing independence
    else:
        base += 0.10   # Acting on own judgment

    # Variance: random.uniform(-0.05, 0.05)
    variance = random.uniform(-0.05, 0.05)
    final = base + variance

    # Hard cap and Schemer floor
    final = min(DEFIANCE_CAP, final)
    final = max(SCHEMER_FLOOR, final)

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

    trust = talleyrand.trust if isinstance(talleyrand.trust, int) else int(talleyrand.trust)
    if trust >= 80:
        base += -0.05
    elif trust >= 50:
        base += 0.00
    elif trust >= 30:
        base += 0.05
    else:
        base += 0.10

    return min(DEFIANCE_CAP, max(SCHEMER_FLOOR, base))


# ════════════════════════════════════════════════════════════════════════════
# §3b — WHAT TALLEYRAND CHANGES (sabotage application)
# ════════════════════════════════════════════════════════════════════════════

def calculate_proposal_harshness(proposal: Dict) -> float:
    """Calculate harshness score (0.0-1.0) from proposal contents.

    Harshness is driven by demands and clauses:
    - Territory demands: +0.2 per region
    - Gold demands: +0.1 per 100 gold/turn
    - AP demands: +0.3 (very harsh)
    - Unit demands: +0.15
    - Sweeteners: -0.1 per sweetener
    """
    harshness = 0.0

    for demand in proposal.get("demands", []):
        dtype = demand.get("type", "")
        if dtype == "territory_cede":
            harshness += 0.2 * len(demand.get("regions", []))
        elif dtype == "gold_per_turn":
            harshness += 0.1 * (demand.get("value", 0) / 100)
        elif dtype == "ap_per_turn":
            harshness += 0.3
        elif dtype == "unit_trade":
            harshness += 0.15

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
        for demand in modified.get("demands", []):
            if demand.get("type") == "territory_cede" and len(demand.get("regions", [])) > 0:
                demand["regions"] = demand["regions"][:-1]  # Remove last region
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
                "description": "Trust -10, Authority +5, defiance cooldown 5 turns.",
                "action": "confront_sabotage",
            },
            {
                "label": "Overlook",
                "description": "Trust +3. Talleyrand gains confidence.",
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
    parts = []
    ptype = proposal.get("type", "peace")
    # Strip internal state suffixes (e.g. "armistice_losing" → "armistice")
    if ptype.startswith("armistice"):
        ptype = "armistice"
    display = ptype.replace("_", " ").title()
    parts.append(display)

    for demand in proposal.get("demands", []):
        dtype = demand.get("type", "")
        if dtype == "territory_cede":
            regions = demand.get("regions", [])
            parts.append(f"cede {', '.join(regions)}" if regions else "territory")
        elif dtype == "gold_per_turn":
            parts.append(f"{int(demand.get('value', 0))} gold/turn")
        elif dtype == "ap_per_turn":
            parts.append(f"{int(demand.get('value', 1))} AP/turn")
        elif dtype == "unit_trade":
            parts.append(f"{int(demand.get('value', 0))} units")

    for sweetener in proposal.get("sweeteners", []):
        stype = sweetener.get("type", "")
        if stype == "gold_per_turn":
            parts.append(f"offer {int(sweetener.get('value', 0))} gold/turn")

    return ", ".join(parts) if parts else "unspecified terms"


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
        "trust_change": 0,
        "authority_change": 0,
        "cooldown_set": 0,
        "message": "",
    }

    if choice == "confront_sabotage":
        # Trust -10, Authority +5, cooldown 5 turns
        old_trust = talleyrand.trust if isinstance(talleyrand.trust, int) else int(talleyrand.trust)
        talleyrand.trust = max(0, old_trust - 10)
        result["trust_change"] = -10

        world.authority_tracker.modify_authority(+5)
        result["authority_change"] = +5

        world.talleyrand_defiance_cooldown = 5
        result["cooldown_set"] = 5

        result["message"] = (
            "You confront Talleyrand directly. He accepts the rebuke with "
            "characteristic grace, but his eyes betray resentment."
        )
    elif choice == "overlook_sabotage":
        # Trust +3
        old_trust = talleyrand.trust if isinstance(talleyrand.trust, int) else int(talleyrand.trust)
        talleyrand.trust = min(100, old_trust + 3)
        result["trust_change"] = +3

        result["message"] = (
            "You choose to overlook the discrepancy. Talleyrand inclines "
            "his head — a small acknowledgment that his judgment was trusted."
        )

    # Clear the pending sabotage
    world.pending_talleyrand_sabotage = None

    return result


# ════════════════════════════════════════════════════════════════════════════
# §3d — REDEMPTION EVENT (Trust ≤ 20)
# ════════════════════════════════════════════════════════════════════════════

def check_talleyrand_redemption(talleyrand, world) -> bool:
    """Check if Talleyrand's redemption event should fire.

    Fires when trust ≤ 20. Loyalist personality (post-Replace) follows
    standard V2b pattern — no special redemption.

    Args:
        talleyrand: DiplomaticRepresentative
        world: WorldState

    Returns:
        True if redemption should fire
    """
    personality = getattr(talleyrand, 'personality', 'schemer')
    if personality == 'loyalist':
        return False  # Loyalist doesn't trigger diplomatic redemption

    # Cooldown: skip if redemption fired within last 5 turns
    last_redemption = getattr(world, 'last_redemption_turn', 0)
    current_turn = getattr(world, 'turn_number', None) or getattr(world, 'current_turn', 1)
    if last_redemption > 0 and current_turn - last_redemption < 5:
        return False

    trust = talleyrand.trust if isinstance(talleyrand.trust, int) else int(talleyrand.trust)
    return trust <= 20


def build_redemption_dialogue(talleyrand, world) -> Dict:
    """Build the redemption event dialogue.

    Three options: Apologize, Replace with Loyalist, Continue.

    Args:
        talleyrand: DiplomaticRepresentative
        world: WorldState

    Returns:
        Dict suitable for pending_diplomatic_dialogue
    """
    trust = talleyrand.trust if isinstance(talleyrand.trust, int) else int(talleyrand.trust)

    talleyrand_text = (
        f"Sire, the relationship between yourself and Talleyrand has become "
        f"untenable. His trust stands at {int(trust)} — barely functional.\n\n"
        f"Talleyrand: \"Perhaps, Sire, we have pushed each other too far. "
        f"I serve France, not your every whim — but I recognize that "
        f"France requires a functioning partnership at its diplomatic helm.\"\n\n"
        f"How do you wish to proceed?"
    )

    return {
        "type": "talleyrand_redemption",
        "target_nation": "France",
        "talleyrand_text": talleyrand_text,
        "options": [
            {
                "label": "Apologize",
                "description": "Trust +15, Authority -5. Admit you pushed too hard.",
                "action": "redemption_apologize",
            },
            {
                "label": "Replace with Loyalist",
                "description": "Personality → Loyalist, Skill 10→6, Trust → 50. Irreversible.",
                "action": "redemption_replace",
            },
            {
                "label": "Continue as we are",
                "description": "Authority -10. Refuse to bend.",
                "action": "redemption_continue",
            },
        ],
        "context": {
            "current_trust": int(trust),
        },
        "turn_created": int(world.current_turn),
        "blocking": True,
    }


def apply_redemption_choice(choice: str, talleyrand, world) -> Dict:
    """Process the player's redemption decision.

    Args:
        choice: "redemption_apologize", "redemption_replace", or "redemption_continue"
        talleyrand: DiplomaticRepresentative
        world: WorldState

    Returns:
        Dict with trust_change, authority_change, personality_changed, message
    """
    result = {
        "trust_change": 0,
        "authority_change": 0,
        "personality_changed": False,
        "skill_change": 0,
        "message": "",
    }

    if choice == "redemption_apologize":
        old_trust = talleyrand.trust if isinstance(talleyrand.trust, int) else int(talleyrand.trust)
        talleyrand.trust = min(100, old_trust + 15)
        result["trust_change"] = +15

        world.authority_tracker.modify_authority(-5)
        result["authority_change"] = -5

        result["message"] = (
            "You extend an olive branch. Talleyrand accepts with quiet dignity. "
            "\"The partnership endures, Sire. Let us not test it again.\""
        )

    elif choice == "redemption_replace":
        # Replace with Loyalist — irreversible
        old_trust = talleyrand.trust if isinstance(talleyrand.trust, int) else int(talleyrand.trust)
        old_skill = talleyrand.skill
        talleyrand.personality = "loyalist"
        talleyrand.skill = 6
        talleyrand.trust = 50
        result["trust_change"] = 50 - old_trust
        result["personality_changed"] = True
        result["skill_change"] = 6 - old_skill

        result["message"] = (
            "Talleyrand is replaced by a loyal aide. The new diplomat is "
            "competent but lacks the brilliance — and the scheming — of "
            "his predecessor. Diplomatic defiance is no longer a concern."
        )

    elif choice == "redemption_continue":
        world.authority_tracker.modify_authority(-10)
        result["authority_change"] = -10

        result["message"] = (
            "You refuse to bend. Talleyrand says nothing — but the silence "
            "between you speaks volumes. The court notices."
        )

    # Set redemption cooldown (5 turns before next redemption can fire)
    current_turn = getattr(world, 'turn_number', None) or getattr(world, 'current_turn', 1)
    world.last_redemption_turn = int(current_turn)

    return result


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
    trust = talleyrand.trust if isinstance(talleyrand.trust, int) else int(talleyrand.trust)
    authority = world.authority_tracker.authority

    # War declaration on neutral → STRONG
    current_state = world.get_diplomatic_state("France", target_nation) if target_nation else "PEACE"
    if proposal.get("type") == "war_declaration" and current_state not in ("WAR",):
        return ConcernLevel.STRONG

    # Harsh terms (harshness > 0.7) → MODERATE or STRONG based on trust
    if harshness > 0.7:
        if trust < 40:
            return ConcernLevel.STRONG
        return ConcernLevel.MODERATE

    # Generous terms when winning → MILD
    if harshness < 0.3 and target_nation:
        diplo_key = world._make_diplo_key("France", target_nation)
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
