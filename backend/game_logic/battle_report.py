"""
Berthier's After-Action Report — Battle Report Generator

Generates structured battle reports after every player-visible combat.
Shows modifier breakdown, casualty summary, and one Berthier observation.

Read-only snapshots of modifiers are taken BEFORE get_attack_modifier() /
get_defense_modifier() consume one-shot bonuses (strategic combat bonus, etc.).
"""

import random
from typing import Dict, List, Optional

from backend.models.region import TERRAIN_DEFENSE_BONUS, TERRAIN_CAVALRY_EFFECTIVENESS
from backend.models.personality_modifiers import (
    get_attack_modifier_for_personality,
    get_defense_modifier_for_personality,
)


def snapshot_attacker_modifiers(
    attacker,
    defender,
    terrain: str,
    fortification_bonus: float,
    flanking_bonus: int,
    glorious_charge: bool,
) -> List[Dict]:
    """
    Read-only snapshot of all attack modifiers BEFORE they are consumed.

    Returns list of {label: str, value: int (%), type: "bonus"|"penalty"}.
    Only includes modifiers that are actually active (non-zero).
    """
    from backend.models.marshal import Stance

    mods: List[Dict] = []

    # --- Stance ---
    stance = getattr(attacker, "stance", Stance.NEUTRAL)
    if stance == Stance.AGGRESSIVE:
        mods.append({"label": "Aggressive stance", "value": 15, "type": "bonus"})
    elif stance == Stance.DEFENSIVE:
        mods.append({"label": "Defensive stance", "value": 10, "type": "penalty"})

    # --- Drill / shock_bonus ---
    shock = getattr(attacker, "shock_bonus", 0)
    if shock > 0:
        mods.append({"label": "Drill training", "value": int(shock * 10), "type": "bonus"})

    # --- Strategic combat bonus (peek only, do NOT zero) ---
    strat_bonus = getattr(attacker, "strategic_combat_bonus", 0)
    if strat_bonus > 0:
        mods.append({"label": "Strategic orders", "value": int(strat_bonus), "type": "bonus"})

    # --- Personality attack modifier (stateless function) ---
    strength_ratio = attacker.strength / defender.strength if defender.strength > 0 else float("inf")
    has_drill = shock > 0
    personality = getattr(attacker, "personality", "unknown")
    pers_mod = get_attack_modifier_for_personality(
        personality, stance.value, has_drill, strength_ratio
    )
    if pers_mod > 1.001:
        pct = int(round((pers_mod - 1.0) * 100))
        mods.append({"label": f"Personality ({personality})", "value": pct, "type": "bonus"})
    elif pers_mod < 0.999:
        pct = int(round((1.0 - pers_mod) * 100))
        mods.append({"label": f"Personality ({personality})", "value": pct, "type": "penalty"})

    # --- Recklessness attack bonus ---
    if getattr(attacker, "is_reckless_cavalry", False):
        reck_bonus = attacker._get_recklessness_attack_bonus()
        if reck_bonus > 0:
            mods.append({"label": "Recklessness", "value": int(round(reck_bonus * 100)), "type": "bonus"})

    # --- Exhaustion penalty ---
    exhaustion = getattr(attacker, "_get_exhaustion_penalty", lambda: 0.0)()
    if exhaustion > 0:
        mods.append({"label": "Exhaustion", "value": int(round(exhaustion * 100)), "type": "penalty"})

    # --- Cavalry terrain effectiveness ---
    if getattr(attacker, "cavalry", False) and getattr(attacker, "is_reckless_cavalry", False):
        reck_bonus_raw = attacker._get_recklessness_attack_bonus()
        if reck_bonus_raw > 0:
            terrain_cav_mult = TERRAIN_CAVALRY_EFFECTIVENESS.get(terrain, 1.0)
            if terrain_cav_mult != 1.0:
                eff_pct = int(terrain_cav_mult * 100)
                if terrain_cav_mult > 1.0:
                    mods.append({"label": f"Cavalry terrain ({terrain})", "value": eff_pct - 100, "type": "bonus"})
                else:
                    mods.append({"label": f"Cavalry terrain ({terrain})", "value": 100 - eff_pct, "type": "penalty"})

    # --- Flanking bonus ---
    if flanking_bonus > 0:
        mods.append({"label": "Flanking", "value": int(flanking_bonus), "type": "bonus"})

    # --- Glorious Charge ---
    if glorious_charge:
        mods.append({"label": "Glorious Charge", "value": 100, "type": "bonus"})

    return mods


def snapshot_defender_modifiers(
    defender,
    attacker,
    terrain: str,
    fortification_bonus: float,
) -> List[Dict]:
    """
    Read-only snapshot of all defense modifiers BEFORE they are consumed.

    Returns list of {label: str, value: int (%), type: "bonus"|"penalty"}.
    Only includes modifiers that are actually active (non-zero).
    """
    from backend.models.marshal import Stance

    mods: List[Dict] = []

    # --- Stance ---
    stance = getattr(defender, "stance", Stance.NEUTRAL)
    if stance == Stance.DEFENSIVE:
        mods.append({"label": "Defensive stance", "value": 15, "type": "bonus"})
    elif stance == Stance.AGGRESSIVE:
        mods.append({"label": "Aggressive stance", "value": 10, "type": "penalty"})

    # --- Fortify bonus (defense_bonus field) ---
    fort_bonus = getattr(defender, "defense_bonus", 0.0)
    if fort_bonus > 0:
        mods.append({"label": "Fortified position", "value": int(round(fort_bonus * 100)), "type": "bonus"})

    # --- Strategic defense bonus (peek only, do NOT zero) ---
    strat_def = getattr(defender, "strategic_defense_bonus", 0)
    if strat_def > 0:
        mods.append({"label": "Strategic orders", "value": int(strat_def), "type": "bonus"})

    # --- Drilling penalty ---
    is_drilling = getattr(defender, "drilling", False) or getattr(defender, "drilling_locked", False)
    if is_drilling:
        mods.append({"label": "Caught drilling", "value": 25, "type": "penalty"})

    # --- Personality defense modifier (stateless function) ---
    is_outnumbered = defender.strength < attacker.strength
    is_holding = getattr(defender, "holding_position", False)
    personality = getattr(defender, "personality", "unknown")
    pers_mod = get_defense_modifier_for_personality(
        personality, stance.value, is_outnumbered, is_holding
    )
    if pers_mod > 1.001:
        pct = int(round((pers_mod - 1.0) * 100))
        mods.append({"label": f"Personality ({personality})", "value": pct, "type": "bonus"})
    elif pers_mod < 0.999:
        pct = int(round((1.0 - pers_mod) * 100))
        mods.append({"label": f"Personality ({personality})", "value": pct, "type": "penalty"})

    # --- Recklessness defense penalty ---
    if getattr(defender, "is_reckless_cavalry", False):
        reck_penalty = defender._get_recklessness_defense_penalty()
        if reck_penalty > 0:
            mods.append({"label": "Recklessness", "value": int(round(reck_penalty * 100)), "type": "penalty"})

    # --- Terrain defense bonus ---
    terrain_def = TERRAIN_DEFENSE_BONUS.get(terrain, 0.0)
    if terrain_def > 0:
        terrain_name = terrain.replace("_", " ").title()
        mods.append({"label": f"Terrain ({terrain_name})", "value": int(round(terrain_def * 100)), "type": "bonus"})

    # --- Fortification building bonus ---
    if fortification_bonus > 0:
        mods.append({"label": "Fortification building", "value": int(round(fortification_bonus * 100)), "type": "bonus"})

    return mods


# ════════════════════════════════════════════════════════════════════════════════
# BERTHIER OBSERVATION TEMPLATES
# ════════════════════════════════════════════════════════════════════════════════

_OBSERVATIONS = {
    "mutual_destruction": [
        "Both armies have been annihilated, Sire. A catastrophe for all involved.",
        "Total destruction on both sides. History will weep for this field.",
        "Neither army survives. The cost of this day is beyond measure.",
    ],
    "lost_into_fortification": [
        "The enemy fortifications proved formidable, Sire.",
        "Attacking prepared positions cost us dearly. The fortifications held.",
        "Our assault broke against their walls. Fortified positions demand respect.",
    ],
    "lost_bad_stance": [
        "Our aggressive posture left us exposed to their disciplined defense.",
        "The enemy's defensive position punished our reckless advance.",
        "An aggressive stance against a prepared defender — a costly choice.",
    ],
    "lost_terrain_disadvantage": [
        "The terrain favored the defender heavily. We fought uphill in every sense.",
        "Geography was our enemy today. The defender held the high ground.",
        "The ground itself conspired against us. Terrain matters, Sire.",
    ],
    "won_heavy_casualties": [
        "Victory, but at terrible cost. Our ranks are thinned dangerously.",
        "We carried the field, but the butcher's bill is steep, Sire.",
        "A pyrrhic victory, one might say. The enemy gave ground grudgingly.",
    ],
    "won_broke_fortification": [
        "We stormed their fortifications successfully! A feat of arms, Sire.",
        "The enemy's walls could not save them. Our troops showed great valor.",
        "Breaking through fortified positions — the men fought with extraordinary courage.",
    ],
    "won_drilled": [
        "The drill training proved its worth on the field today.",
        "Well-drilled troops make the difference. Our preparation paid dividends.",
        "The hours of drill translated directly into battlefield superiority.",
    ],
    "lost_narrow_no_drill": [
        "A narrow defeat, Sire. Better-prepared troops might have tipped the balance.",
        "We were close. A period of drilling could have changed the outcome.",
        "The margin was slim. Training and preparation would serve us well.",
    ],
    "won_decisively": [
        "A decisive victory! The enemy was thoroughly outmatched.",
        "Complete dominance on the field. The enemy crumbled before us.",
        "An exemplary engagement. The outcome was never in doubt.",
    ],
    "stalemate": [
        "Neither side could claim the field. The armies remain locked.",
        "An inconclusive affair. Both sides bloodied but unbroken.",
        "Stalemate. The armies glare at each other across the field.",
    ],
    "default": [
        "The engagement proceeded as one might expect, Sire.",
        "A standard affair. Nothing unusual to report.",
        "The battle unfolded without particular distinction.",
    ],
}


def _pick_observation(battle_result: Dict) -> str:
    """
    Select a Berthier observation based on priority rules.
    First matching priority wins.
    """
    outcome = battle_result.get("outcome", "")
    attacker_data = battle_result.get("attacker", {})
    defender_data = battle_result.get("defender", {})
    modifier_snapshot = battle_result.get("modifier_snapshot", {})
    atk_mods = modifier_snapshot.get("attacker", [])
    def_mods = modifier_snapshot.get("defender", [])

    attacker_original = battle_result.get("attacker_original_strength", 0)
    defender_original = battle_result.get("defender_original_strength", 0)
    attacker_casualties = attacker_data.get("casualties", 0)
    defender_casualties = defender_data.get("casualties", 0)

    attacker_won = outcome in ("attacker_victory", "attacker_tactical_victory")
    attacker_lost = outcome in ("defender_victory", "defender_tactical_victory")

    def _has_mod(mod_list, label_fragment, mod_type=None):
        for m in mod_list:
            if label_fragment.lower() in m.get("label", "").lower():
                if mod_type is None or m.get("type") == mod_type:
                    return True
        return False

    def _mod_value(mod_list, label_fragment, mod_type=None):
        for m in mod_list:
            if label_fragment.lower() in m.get("label", "").lower():
                if mod_type is None or m.get("type") == mod_type:
                    return m.get("value", 0)
        return 0

    # Priority 1: Mutual destruction
    if outcome == "mutual_destruction":
        return random.choice(_OBSERVATIONS["mutual_destruction"])

    # Priority 2: Lost + attacked into fortification
    if attacker_lost and (
        _has_mod(def_mods, "fortif", "bonus") or _has_mod(def_mods, "fortification", "bonus")
    ):
        return random.choice(_OBSERVATIONS["lost_into_fortification"])

    # Priority 3: Lost + bad stance (aggressive into defensive)
    if attacker_lost and _has_mod(atk_mods, "aggressive stance", "bonus") and _has_mod(def_mods, "defensive stance", "bonus"):
        return random.choice(_OBSERVATIONS["lost_bad_stance"])

    # Priority 4: Lost + terrain disadvantage >= 15%
    if attacker_lost and _mod_value(def_mods, "terrain", "bonus") >= 15:
        return random.choice(_OBSERVATIONS["lost_terrain_disadvantage"])

    # Priority 5: Won + heavy casualties (>40% of attacker original)
    if attacker_won and attacker_original > 0 and attacker_casualties > attacker_original * 0.40:
        return random.choice(_OBSERVATIONS["won_heavy_casualties"])

    # Priority 6: Won + broke through fortification
    if attacker_won and (
        _has_mod(def_mods, "fortif", "bonus") or _has_mod(def_mods, "fortification", "bonus")
    ):
        return random.choice(_OBSERVATIONS["won_broke_fortification"])

    # Priority 7: Won + drilled
    if attacker_won and _has_mod(atk_mods, "drill", "bonus"):
        return random.choice(_OBSERVATIONS["won_drilled"])

    # Priority 8: Lost + no drill + narrow margin (< 15% of attacker original strength)
    if attacker_lost and not _has_mod(atk_mods, "drill", "bonus"):
        if attacker_original > 0:
            margin = abs(attacker_casualties - defender_casualties)
            if margin < attacker_original * 0.15:
                return random.choice(_OBSERVATIONS["lost_narrow_no_drill"])

    # Priority 9: Won decisively (2:1+ casualty ratio)
    if attacker_won and defender_casualties > 0 and attacker_casualties > 0:
        if defender_casualties >= attacker_casualties * 2:
            return random.choice(_OBSERVATIONS["won_decisively"])

    # Priority 10: Stalemate
    if outcome == "stalemate":
        return random.choice(_OBSERVATIONS["stalemate"])

    # Priority 11: Default
    return random.choice(_OBSERVATIONS["default"])


def generate_battle_report(battle_result: Dict) -> Dict:
    """
    Generate a structured battle report from a resolve_battle() return dict.

    Args:
        battle_result: Full dict from resolve_battle(), augmented with
            attacker_original_strength, defender_original_strength,
            and modifier_snapshot.

    Returns:
        Dict with modifier_breakdown, casualty_summary, and observation.
        All numeric values are int()-wrapped.
    """
    attacker_data = battle_result.get("attacker", {})
    defender_data = battle_result.get("defender", {})
    modifier_snapshot = battle_result.get("modifier_snapshot", {})

    attacker_original = int(battle_result.get("attacker_original_strength", 0))
    defender_original = int(battle_result.get("defender_original_strength", 0))

    attacker_casualties = int(attacker_data.get("casualties", 0))
    defender_casualties = int(defender_data.get("casualties", 0))
    attacker_remaining = int(attacker_data.get("remaining", 0))
    defender_remaining = int(defender_data.get("remaining", 0))

    observation = _pick_observation(battle_result)

    return {
        "modifier_breakdown": {
            "attacker": modifier_snapshot.get("attacker", []),
            "defender": modifier_snapshot.get("defender", []),
        },
        "casualty_summary": {
            "attacker_name": str(attacker_data.get("name", "Attacker")),
            "attacker_original": int(attacker_original),
            "attacker_casualties": int(attacker_casualties),
            "attacker_remaining": int(attacker_remaining),
            "defender_name": str(defender_data.get("name", "Defender")),
            "defender_original": int(defender_original),
            "defender_casualties": int(defender_casualties),
            "defender_remaining": int(defender_remaining),
        },
        "observation": str(observation),
    }
