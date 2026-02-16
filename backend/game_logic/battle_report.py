"""
Berthier's After-Action Report — Battle Report Generator

Generates structured battle reports after every player-visible combat.
Shows modifier breakdown, casualty summary, and one Berthier observation.

Read-only snapshots of modifiers are taken BEFORE get_attack_modifier() /
get_defense_modifier() consume one-shot bonuses (strategic combat bonus, etc.).
"""

import random
from typing import Dict, List

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

# Templates use {marshal} for our marshal's name, {enemy} for the enemy's name.
_OBSERVATIONS = {
    "mutual_destruction": [
        "Both armies have been annihilated, Sire. A catastrophe for all involved.",
        "Total destruction on both sides. History will weep for this field.",
        "Neither army survives. The cost of this day is beyond measure.",
    ],
    "lost_into_fortification": [
        "The enemy fortifications proved formidable, Sire. {marshal}'s assault was repulsed.",
        "Attacking prepared positions cost {marshal} dearly. The fortifications held.",
        "{marshal}'s troops broke against their walls. Fortified positions demand respect.",
    ],
    "lost_fort_overrun": [
        "Even {marshal}'s fortifications could not hold, Sire. {enemy} overran the position.",
        "The walls were not enough. {enemy} broke through {marshal}'s prepared defenses.",
        "{marshal}'s fortified position was overwhelmed. A costly investment lost, Sire.",
    ],
    "lost_bad_stance_attacking": [
        "{marshal}'s aggressive posture left the troops exposed to the enemy's disciplined defense.",
        "{enemy}'s defensive position punished {marshal}'s reckless advance.",
        "An aggressive stance against a prepared defender — a costly choice, Sire.",
    ],
    "lost_bad_stance_defending": [
        "{marshal} was caught in an aggressive posture when {enemy} struck, Sire. A defensive stance would have served better.",
        "An aggressive stance invites disaster when one is not the attacker, Sire. {marshal} paid the price.",
        "{marshal}'s aggressive posture left the troops exposed when {enemy}'s attack came.",
    ],
    "lost_terrain_disadvantage": [
        "The terrain heavily favored {enemy}. {marshal}'s men paid the price.",
        "Geography was our enemy today, Sire. {enemy} held the superior ground.",
        "The ground itself worked against {marshal}. Terrain matters, Sire.",
    ],
    "lost_despite_terrain": [
        "Even the favorable ground could not save {marshal}, Sire. {enemy} overcame the terrain.",
        "The hills were ours, but {enemy} took them. {marshal}'s position was overrun.",
        "{marshal} held superior ground, yet {enemy} prevailed. A grim day, Sire.",
    ],
    "won_heavy_casualties": [
        "Victory for {marshal}, but at terrible cost. The ranks are thinned dangerously.",
        "{marshal} carried the field, but the butcher's bill is steep, Sire.",
        "A pyrrhic victory for {marshal}. {enemy} gave ground grudgingly.",
    ],
    "won_broke_fortification": [
        "{marshal} stormed the enemy fortifications! A feat of arms, Sire.",
        "{enemy}'s walls could not save them. {marshal}'s troops showed great valor.",
        "{marshal} broke through fortified positions — extraordinary courage from the men.",
    ],
    "won_fort_held": [
        "{marshal}'s fortifications held firm, Sire. {enemy} broke against our walls.",
        "The prepared defenses proved their worth. {enemy} could not dislodge {marshal}.",
        "A wise investment in fortification. {marshal}'s position was impregnable to {enemy}'s assault.",
    ],
    # Fortification degradation (Session 31) — attacker perspective: we attacked and damaged their fort
    "fort_degraded_attacker": [
        "The walls of the region bear fresh scars, Your Majesty. Their fortifications weaken -- another assault may crack them.",
        "Our bombardment has damaged their works. {enemy}'s defenses erode with each engagement.",
    ],
    # Fortification degradation — defender perspective: our fort was damaged by enemy attack
    "fort_degraded_defender": [
        "Our fortifications have sustained damage in the fighting. The walls will not hold forever, Your Majesty.",
        "The enemy's assault has weakened our works. We must repair or consider withdrawal.",
    ],
    # Fortification destroyed — attacker perspective: we destroyed their fort
    "fort_destroyed_attacker": [
        "{enemy}'s fortifications have been reduced to rubble! They now defend on open ground.",
        "Persistent assault has demolished their works. The advantage of position is no more.",
    ],
    # Fortification destroyed — defender perspective: our fort was destroyed
    "fort_destroyed_defender": [
        "I regret to report our fortifications are destroyed, Your Majesty. We hold open ground now.",
        "The enemy's repeated assaults have leveled our defenses. We fight without cover.",
    ],
    "won_drilled": [
        "{marshal}'s drill training proved its worth on the field today.",
        "Well-drilled troops make the difference. {marshal}'s preparation paid dividends.",
        "The hours of drill translated directly into {marshal}'s battlefield superiority.",
    ],
    "lost_narrow_no_drill": [
        "A narrow defeat for {marshal}, Sire. Better-prepared troops might have tipped the balance.",
        "{marshal} was close. A period of drilling could have changed the outcome.",
        "The margin was slim. Training and preparation would serve {marshal} well.",
    ],
    "lost_costly": [
        "A grievous defeat for {marshal}, Sire. The losses are severe.",
        "{marshal}'s army has been badly mauled. {enemy} proved the stronger force today.",
        "The toll on {marshal}'s forces is heavy, Sire. This defeat will be felt.",
    ],
    "won_decisively": [
        "A decisive victory for {marshal}! {enemy} was thoroughly outmatched.",
        "Complete dominance on the field. {enemy} crumbled before {marshal}.",
        "An exemplary engagement by {marshal}. The outcome was never in doubt.",
    ],
    "stalemate": [
        "Neither {marshal} nor {enemy} could claim the field. The armies remain locked.",
        "An inconclusive affair. Both sides bloodied but unbroken.",
        "Stalemate. {marshal} and {enemy} glare at each other across the field.",
    ],
    "default": [
        "The engagement proceeded as one might expect, Sire.",
        "A standard affair. Nothing unusual to report.",
        "The battle unfolded without particular distinction.",
    ],
}


def _pick_observation(battle_result: Dict, player_nation: str = "France") -> str:
    """
    Select a Berthier observation based on priority rules.
    First matching priority wins.

    Perspective is always from the player's side (Napoleon/Berthier).
    If the player's marshal is the defender, "we won" means the defender won.
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
    defender_won = outcome in ("defender_victory", "defender_tactical_victory")

    # Determine perspective: which side is ours?
    attacker_nation = battle_result.get("attacker_nation", "")
    defender_nation = battle_result.get("defender_nation", "")
    we_are_attacker = (attacker_nation == player_nation)

    # Perspective-flipped variables
    if we_are_attacker:
        we_won = attacker_won
        we_lost = defender_won
        our_mods = atk_mods
        their_mods = def_mods
        our_original = attacker_original
        our_casualties = attacker_casualties
        enemy_casualties = defender_casualties
        our_name = attacker_data.get("name", "Attacker")
        enemy_name = defender_data.get("name", "Defender")
    else:
        we_won = defender_won
        we_lost = attacker_won
        our_mods = def_mods
        their_mods = atk_mods
        our_original = defender_original
        our_casualties = defender_casualties
        enemy_casualties = attacker_casualties
        our_name = defender_data.get("name", "Defender")
        enemy_name = attacker_data.get("name", "Attacker")

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

    def _fill(template: str) -> str:
        return template.format(marshal=our_name, enemy=enemy_name)

    # Priority 1: Mutual destruction
    if outcome == "mutual_destruction":
        return _fill(random.choice(_OBSERVATIONS["mutual_destruction"]))

    # Priority 2: We lost + fortifications were involved
    # 2a: We attacked into enemy fort and lost
    if we_lost and _has_mod(their_mods, "fortif", "bonus"):
        return _fill(random.choice(_OBSERVATIONS["lost_into_fortification"]))
    # 2b: Enemy attacked our fort and still won — our fort was overrun
    if we_lost and _has_mod(our_mods, "fortif", "bonus"):
        return _fill(random.choice(_OBSERVATIONS["lost_fort_overrun"]))

    # Priority 3: We lost + our side was aggressive, their side was defensive
    if we_lost and _has_mod(our_mods, "aggressive stance") and _has_mod(their_mods, "defensive stance"):
        # Use perspective-aware templates: attacking into defense vs caught defending aggressively
        if we_are_attacker:
            return _fill(random.choice(_OBSERVATIONS["lost_bad_stance_attacking"]))
        else:
            return _fill(random.choice(_OBSERVATIONS["lost_bad_stance_defending"]))

    # Priority 4: We lost + terrain was a factor
    # When we attacked into enemy terrain: their_mods has terrain bonus
    # When enemy attacked us on our terrain and still won: our_mods has terrain bonus (we lost DESPITE it)
    if we_lost and _mod_value(their_mods, "terrain", "bonus") >= 15:
        return _fill(random.choice(_OBSERVATIONS["lost_terrain_disadvantage"]))
    if we_lost and _mod_value(our_mods, "terrain", "bonus") >= 15:
        return _fill(random.choice(_OBSERVATIONS["lost_despite_terrain"]))

    # Priority 5: We won + heavy casualties (>40% of our original)
    if we_won and our_original > 0 and our_casualties > our_original * 0.40:
        return _fill(random.choice(_OBSERVATIONS["won_heavy_casualties"]))

    # Priority 6: We won + fortifications were involved
    # 6a: We attacked and broke through enemy fort
    if we_won and _has_mod(their_mods, "fortif", "bonus"):
        return _fill(random.choice(_OBSERVATIONS["won_broke_fortification"]))
    # 6b: We defended with a fort and held — our investment paid off
    if we_won and _has_mod(our_mods, "fortif", "bonus"):
        return _fill(random.choice(_OBSERVATIONS["won_fort_held"]))

    # Priority 6c: Fortification degradation — walls damaged by battle (Session 31)
    # Fires regardless of who won — any battle with degradation is notable
    fort_degraded = battle_result.get("fortification_degraded", False)
    fort_new = battle_result.get("fortification_new", 0)
    if fort_degraded:
        # Determine if the defender's fort was ours or theirs
        defender_is_ours = not we_are_attacker
        if fort_new <= 0:
            # Fort destroyed
            if defender_is_ours:
                return _fill(random.choice(_OBSERVATIONS["fort_destroyed_defender"]))
            else:
                return _fill(random.choice(_OBSERVATIONS["fort_destroyed_attacker"]))
        else:
            # Fort damaged but standing
            if defender_is_ours:
                return _fill(random.choice(_OBSERVATIONS["fort_degraded_defender"]))
            else:
                return _fill(random.choice(_OBSERVATIONS["fort_degraded_attacker"]))

    # Priority 7: We won + our side had drill bonus
    if we_won and _has_mod(our_mods, "drill", "bonus"):
        return _fill(random.choice(_OBSERVATIONS["won_drilled"]))

    # Priority 8: We lost + no drill + narrow margin (< 15% of our original strength)
    if we_lost and not _has_mod(our_mods, "drill", "bonus"):
        if our_original > 0:
            margin = abs(our_casualties - enemy_casualties)
            if margin < our_original * 0.15:
                return _fill(random.choice(_OBSERVATIONS["lost_narrow_no_drill"]))

    # Priority 8.5: We lost with significant casualties (>30% of original) — catch-all for
    # losses that didn't match any specific condition (terrain, stance, fort, narrow margin).
    # Without this, devastating defeats like losing half an army fall through to "standard affair".
    if we_lost and our_original > 0 and our_casualties > our_original * 0.30:
        return _fill(random.choice(_OBSERVATIONS["lost_costly"]))

    # Priority 9: We won decisively (2:1+ casualty ratio in our favor)
    if we_won and enemy_casualties > 0 and our_casualties > 0:
        if enemy_casualties >= our_casualties * 2:
            return _fill(random.choice(_OBSERVATIONS["won_decisively"]))

    # Priority 10: Stalemate
    if outcome == "stalemate":
        return _fill(random.choice(_OBSERVATIONS["stalemate"]))

    # Priority 11: Default
    return _fill(random.choice(_OBSERVATIONS["default"]))


def generate_battle_report(battle_result: Dict, player_nation: str = "France") -> Dict:
    """
    Generate a structured battle report from a resolve_battle() return dict.

    Args:
        battle_result: Full dict from resolve_battle(), augmented with
            attacker_original_strength, defender_original_strength,
            modifier_snapshot, attacker_nation, and defender_nation.
        player_nation: The player's nation for perspective (default "France").

    Returns:
        Dict with modifier_breakdown, casualty_summary, and observation.
        All numeric values are int()-wrapped.
        Observation is always from the player's (Napoleon/Berthier) perspective.
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

    observation = _pick_observation(battle_result, player_nation)

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
