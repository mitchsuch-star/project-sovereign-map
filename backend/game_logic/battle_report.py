"""
Berthier's After-Action Report — Battle Report Generator

Generates structured battle reports after every player-visible combat.
Shows modifier breakdown, casualty summary, and one Berthier observation.

Read-only snapshots of modifiers are taken BEFORE get_attack_modifier() /
get_defense_modifier() consume one-shot bonuses (strategic combat bonus, etc.).
"""

import random

from backend.display_names import humanize_entity_name
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
    # W6-1 (BUG-CA-5): "Strategic orders" was unmappable to any player
    # action — name what actually earned it. Label only, GR1 math untouched.
    strat_bonus = getattr(attacker, "strategic_combat_bonus", 0)
    if strat_bonus > 0:
        mods.append({"label": "Forced march momentum (order completed)",
                     "value": int(strat_bonus), "type": "bonus"})

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

    # --- Exhaustion penalty (artillery exempt) ---
    if not getattr(attacker, "artillery", False):
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

    # --- Cavalry counter vs artillery ---
    if getattr(attacker, "cavalry", False) and getattr(defender, "artillery", False):
        mods.append({"label": "Cavalry counter (vs artillery)", "value": 30, "type": "bonus"})

    # --- Square formation interactions (Session 67) ---
    if getattr(defender, "square_formation", False):
        if getattr(attacker, "cavalry", False):
            mods.append({"label": "Square formation (vs cavalry)", "value": 40, "type": "penalty"})
        elif getattr(attacker, "artillery", False):
            mods.append({"label": "Square formation (vs artillery)", "value": 50, "type": "bonus"})

    # --- Flanking bonus ---
    if flanking_bonus > 0:
        mods.append({"label": "Flanking", "value": int(flanking_bonus), "type": "bonus"})

    # --- Ranged bombardment (reduces return casualties) ---
    if getattr(attacker, "artillery", False):
        atk_loc = getattr(attacker, "location", None)
        def_loc = getattr(defender, "location", None)
        if atk_loc and def_loc and atk_loc != def_loc:
            mods.append({"label": "Ranged bombardment (−50% return fire)", "value": 50, "type": "bonus"})

    # --- Counter-Punch Mastery (Davout's Iron Marshal ability) ---
    if getattr(attacker, "counter_punch_ready", False):
        if hasattr(attacker, 'ability') and attacker.ability.get("name") == "Counter-Punch Mastery":
            mods.append({"label": "Counter-Punch Mastery", "value": 20, "type": "bonus"})

    # --- Iron Resolve (MC-1c: Davout's coiled-spring assault) ---
    # Snapshots run BEFORE get_attack_modifier() consumes the stacks
    # (memo-verified safe) — the report names what the assault carried.
    _iron_stacks = getattr(attacker, "iron_resolve_stacks", 0)
    if (_iron_stacks > 0 and hasattr(attacker, 'ability')
            and attacker.ability.get("name") == "Iron Resolve"):
        from backend.models.marshal import Marshal as _Marshal
        _iron_pct = int(round(_iron_stacks * _Marshal.IRON_RESOLVE_BONUS_PER_STACK * 100))
        _plural = "s" if _iron_stacks != 1 else ""
        mods.append({"label": f"Iron Resolve ({_iron_stacks} stack{_plural})",
                     "value": _iron_pct, "type": "bonus"})

    # --- The Presence (NP-2: the Emperor commands in person) ---
    # Deliberately SHOWN unlike coordination — the aura is its own factor
    # outside the coordination caps, and the report names it (shown =
    # applied, percentage derived from the consumed constant).
    # NP-V: derived from the SAME product the modifier applies, so a
    # cracked aura reads "+7%", not "+10%" — the player watches the star
    # dim in the battle report itself.
    _pres_a = float(getattr(attacker, "sovereign_presence", 0.0) or 0.0)
    if _pres_a:
        from backend.models.marshal import Marshal as _M
        mods.append({"label": ("The Emperor commands in person"
                               if _pres_a >= 0.999 else
                               "The Emperor commands in person "
                               "(his star dims)"),
                     "value": int(round(
                         _M.SOVEREIGN_PRESENCE_ATTACK * _pres_a * 100)),
                     "type": "bonus"})

    # --- Glorious Charge ---
    if glorious_charge:
        mods.append({"label": "Glorious Charge", "value": 100, "type": "bonus"})

    # --- Overwatch penalty (Session 68) ---
    overwatch_penalty = getattr(attacker, "overwatch_penalty", 0.0)
    if overwatch_penalty > 0:
        pct = int(round(overwatch_penalty * 100))
        mods.append({"label": "Artillery overwatch", "value": pct, "type": "penalty"})

    # --- Coordination bonuses (Phase 7, Sessions 57-65) ---
    # Combined arms, per-ally coordination, dedicated coordination, adjacent
    # support, and total coordination are intentionally OMITTED from the
    # modifier breakdown.  Berthier's narrative observation (see
    # coordination_* templates in _OBSERVATIONS) conveys coordination info
    # in prose.  Detailed numbers will appear in the Battle History screen
    # (Phase 8.5).  The bonuses still affect combat via marshal transient
    # fields — they are just not shown as raw stats here.

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
    # W6-1 (BUG-CA-5): named for the player action that earned it (see
    # the attacker-side label note). Label only, GR1 math untouched.
    strat_def = getattr(defender, "strategic_defense_bonus", 0)
    if strat_def > 0:
        mods.append({"label": "Forced march momentum (order completed)",
                     "value": int(strat_def), "type": "bonus"})

    # --- Drilling penalty ---
    is_drilling = getattr(defender, "drilling", False) or getattr(defender, "drilling_locked", False)
    if is_drilling:
        mods.append({"label": "Caught drilling", "value": 25, "type": "penalty"})

    # --- Artillery moved this turn (guns not set up) ---
    if getattr(defender, "artillery", False) and getattr(defender, "moved_this_turn", False):
        mods.append({"label": "Artillery in transit", "value": 25, "type": "penalty"})

    # --- Personality defense modifier (stateless function) ---
    is_outnumbered = defender.strength < attacker.strength
    is_holding = getattr(defender, "holding_position", False)
    personality = getattr(defender, "personality", "unknown")
    pers_mod = get_defense_modifier_for_personality(
        personality, stance.value, is_outnumbered, is_holding
    )
    if pers_mod > 1.001:
        pct = int(round((pers_mod - 1.0) * 100))
        # W6-1 (BUG-CA-5): a literal marshal's hold bonus gets its doctrine
        # name instead of the opaque personality caption. Label only.
        if personality == "literal" and is_holding:
            mods.append({"label": "Immovable (literal hold)", "value": pct, "type": "bonus"})
        else:
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

    # --- Square formation defense bonus (Session 67) ---
    if getattr(defender, "square_formation", False):
        mods.append({"label": "Square formation", "value": 5, "type": "bonus"})

    # --- Signature abilities (defense) ---
    ability = getattr(defender, "ability", None)
    if ability:
        ability_name = ability.get("name", "") if isinstance(ability, dict) else ""
        if ability_name == "Reverse Slope Defense":
            mods.append({"label": "Reverse Slope Defense", "value": 5, "type": "bonus"})
        elif ability_name == "Habsburg Resolve":
            mods.append({"label": "Habsburg Resolve", "value": 3, "type": "bonus"})
        elif ability_name == "Child of Victory" and is_outnumbered:
            # MC-1: Massena — the report names why the outnumbered wall held.
            # Mirrors marshal.get_defense_modifier's is_outnumbered gate.
            mods.append({"label": "Child of Victory (outnumbered)", "value": 10, "type": "bonus"})

    # --- The Presence (NP-2: the Emperor stands with the defence) ---
    _pres_d = float(getattr(defender, "sovereign_presence", 0.0) or 0.0)
    if _pres_d:
        from backend.models.marshal import Marshal as _M
        mods.append({"label": ("The Emperor commands in person"
                               if _pres_d >= 0.999 else
                               "The Emperor commands in person "
                               "(his star dims)"),
                     "value": int(round(
                         _M.SOVEREIGN_PRESENCE_DEFENSE * _pres_d * 100)),
                     "type": "bonus"})

    # --- Coordination bonuses (Phase 7, Sessions 57-65) ---
    # Intentionally omitted — see comment in snapshot_attacker_modifiers().

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
    # ── PT-D4: the outcome the selector had no arm for ─────────────────
    # `The Great Battle of Milan` — Massena broken, routed, Milan lost —
    # was reported as "A standard affair. Nothing unusual to report."
    # Not bad luck: he took 26.2%, just under the 30% `lost_costly`
    # threshold, and a grep of the whole selector returned ZERO
    # references to `forced_retreat`, `routed` or `region_conquered`.
    #
    # SCOPED DELIBERATELY to the rout. `forced_retreat` is published on
    # both side dicts (`combat.py:966/972`) and was simply never read —
    # so this arm is backed by data that already exists. The other two
    # thirds of the row are NOT built, because at this seam they would be
    # dead code: `generate_battle_report` runs inside `combat.py`, where
    # the province is not yet known to have changed hands (conquest is
    # decided afterwards, in `combat_executor`) and `broken` lives on the
    # Marshal, never on the payload. Shipping banks that cannot fire is
    # the defect this row is about. The measured case is covered — the
    # rout is what happened to Massena.
    "routed": [
        "{marshal}'s corps broke, Sire. They are streaming back from the field.",
        "The line gave way. {marshal} is falling back, and not in good order.",
        "{marshal} was driven from the field. His men are scattered.",
    ],
    "won_flawless": [
        "A flawless victory, Sire! {marshal} defeated {enemy} without a single loss.",
        "Not a man lost! {marshal}'s handling of {enemy} was nothing short of masterful.",
        "Perfection on the battlefield. {marshal} destroyed {enemy} while preserving every soldier.",
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
    # Artillery bombardment observations
    "artillery_bombardment_effective": [
        "{marshal}'s artillery devastated {enemy}'s position. The guns speak with authority, Sire.",
        "A masterful bombardment by {marshal}. {enemy}'s defenses crumble under sustained fire.",
        "{marshal}'s gunners proved their worth today. The enemy position was thoroughly reduced.",
    ],
    "artillery_caught_moving": [
        "{marshal}'s guns were caught in transit when {enemy} struck. The crews had no time to deploy.",
        "A costly lesson, Sire. {marshal}'s artillery was vulnerable during repositioning.",
        "{enemy} exploited {marshal}'s movement. Artillery must be given time to set up.",
    ],
    "cavalry_overran_artillery": [
        "{enemy}'s cavalry swept through {marshal}'s gun line. Unscreened artillery is cavalry's prey.",
        "The horsemen of {enemy} overran {marshal}'s guns before the crews could react.",
        "{marshal}'s artillery was defenseless against {enemy}'s cavalry charge. Infantry screens are essential, Sire.",
    ],
    "cavalry_overrun_attacker": [
        "{marshal}'s cavalry thundered through {enemy}'s gun line! Unscreened artillery cannot withstand the charge.",
        "The horsemen smashed {enemy}'s batteries. {marshal}'s cavalry overran the guns, Sire!",
        "{marshal} exploited {enemy}'s exposed artillery. A textbook cavalry charge against unsupported guns.",
    ],
    "artillery_fort_degradation": [
        "{marshal}'s bombardment is systematically dismantling {enemy}'s fortifications. The walls cannot endure much more.",
        "Our artillery is the answer to their walls, Sire. {marshal}'s guns crack what infantry cannot.",
        "Persistent bombardment by {marshal} erodes the enemy's prepared positions. Time and gunpowder are on our side.",
    ],
    # ── Bombardment-specific observations (§11.1) ──
    "bombardment_effective": [
        "{marshal}'s guns thunder across the valley. The enemy position absorbs punishment, Sire.",
        "A methodical bombardment by {marshal}. Each salvo finds its mark.",
        "Smoke rises from {enemy}'s position. {marshal}'s fire is taking its toll.",
    ],
    "bombardment_fort_cracking": [
        "{marshal}'s sustained fire is dismantling {enemy}'s fortifications. The walls cannot endure.",
        "Cracks spread through the enemy works under {marshal}'s bombardment. They weaken, Sire.",
    ],
    "bombardment_ineffective": [
        "{marshal}'s guns fire into the mass, but {enemy}'s army is vast. The shells are pinpricks.",
        "The bombardment continues, but {enemy}'s numbers absorb our fire with barely a flinch.",
    ],
    "bombardment_target_broken": [
        "{marshal}'s bombardment has shattered {enemy}'s position entirely. The way is clear for advance.",
        "The guns fall silent — there is nothing left to shell. {enemy}'s force is destroyed.",
    ],
    "bombardment_terrain_difficulty": [
        "{marshal}'s guns struggle to find targets in the {terrain}. The land itself shields {enemy}.",
        "The {terrain} terrain hampers {marshal}'s fire. Shells fall wide of their marks.",
    ],
    "bombardment_friendly_fire": [
        "Sire, our own forces were caught in {marshal}'s bombardment. Regrettable, but unavoidable.",
        "{marshal}'s shells struck friend as well as foe. The price of area bombardment.",
    ],
    # ── Coordination observations (Phase 7, Session 65) ──
    "coordination_full_triangle": [
        "Infantry, cavalry, and guns — the full triangle of arms! {marshal}'s combined arms proved textbook Napoleonic doctrine, Sire.",
        "Three arms working as one! {marshal}'s infantry holds, cavalry flanks, artillery breaks. This is how wars are won.",
        "The full combined arms triangle was deployed, Sire. {marshal} commands a truly integrated force.",
    ],
    "coordination_reinforcement_arrival": [
        "{ally} arrived to reinforce {marshal}! The timely arrival swung the battle in our favor, Sire.",
        "Reinforcements! {ally} marched onto the field beside {marshal}. The enemy's advantage melted away.",
        "{ally}'s timely arrival bolstered {marshal}'s position. Well-coordinated, Sire.",
    ],
    # W6-1 (BUG-CA-5): the observation must not claim victory the battle
    # didn't deliver — outcome-aware variants for stalemates and losses.
    "coordination_reinforcement_arrival_held": [
        "{ally} reached the field beside {marshal}, Sire — it saved the line, no more.",
        "{ally} arrived in time to steady {marshal}'s position. The field was held, nothing further.",
        "Reinforcement from {ally} kept {marshal} standing, Sire — but neither side yielded the ground.",
    ],
    "coordination_reinforcement_arrival_lost": [
        "{ally} reached {marshal} in time, Sire — but even together, the field could not be held.",
        "{ally} marched to {marshal}'s guns as ordered. It was not enough.",
        "The reinforcement arrived, Sire. The verdict of the field went against us regardless.",
    ],
    "coordination_reinforcement_mixed": [
        "{ally} arrived to reinforce {marshal}, but {failed_ally} failed to reach the field in time.",
        "Reinforcements from {ally} bolstered {marshal}'s position — though {failed_ally} never arrived, Sire.",
        "{ally}'s timely arrival aided {marshal}. {failed_ally}, however, {failed_was} conspicuously absent.",
    ],
    # PC-5 (quiet-France played campaign, Aug 3 2026): this bank is split.
    # The "held the field alone" line was fired over a tableau listing three
    # engaged corps and 64,943 men committed — it is a claim about who ELSE
    # was on the field, and nothing was checking. The lines below are true
    # whenever a called-for corps failed to arrive, whoever else was present.
    "coordination_reinforcement_failure": [
        "{ally} failed to arrive in time. {marshal}'s army fought without expected support.",
        "{marshal} fought without {ally}'s support. The roads, or the will, proved insufficient.",
        "{ally} never reached the guns. The battle was decided without them, Sire.",
    ],
    # Only reachable when our side's participant list is exactly the primary:
    # the solitude is verified, not assumed.
    "coordination_reinforcement_failure_alone": [
        # N24 (CA9): `{ally}` is a JOINED LIST here, so a hardcoded "was"
        # shipped "Davout, Soult and Murat was expected". The plural fix
        # landed on the MIXED bank only; both lines of this one had it.
        "Where {failed_was} {ally}? {marshal} held the field alone — reinforcement never came.",
        "{marshal} stood alone, Sire. {ally} never came.",
        "Not one corps reached {marshal}. {ally} {failed_was} expected; {marshal} fought the battle single-handed.",
    ],
    "coordination_hostile_forced": [
        "{ally}'s presence brought numbers if not cooperation, Sire. They fought — as ordered — but every step beside {marshal} was teeth gritted.",
        "{ally} fought alongside {marshal} under protest. The SUPPORT order was obeyed, but coordination was nonexistent.",
        "Under your orders, {ally} marched beside {marshal}. They bled together — but fought as strangers.",
    ],
    "coordination_hostile_refused": [
        "{ally} stood idle while {marshal} fought. Their hostility runs deeper than duty, Sire.",
        "{marshal} received no aid from {ally}. Hostile indifference — they watched from the same field.",
    ],
    "coordination_devoted_synergy": [
        "{ally}'s devotion amplified {marshal}'s coordination beyond the ordinary. A remarkable synergy, Sire.",
        "{marshal} and {ally} fought as one mind. Devoted allies make the finest corps.",
    ],
    "coordination_rival_improved": [
        "Sire, I believe {marshal}'s opinion of {ally} is... shifting.",
        "An interesting development, Sire. {marshal} may be warming to {ally} after their shared ordeal.",
    ],
    # ── Auto-Bombardment + Overwatch observations (Phase 7b, Session 68) ──
    "support_bombardment_effective": [
        "{artillery}'s preparatory bombardment was devastating. {marshal}'s charge met a shaken enemy.",
        "The guns of {artillery} softened the enemy before {marshal}'s assault. Textbook combined arms, Sire.",
        "{artillery}'s fire support proved decisive. {enemy} was already reeling when {marshal} struck.",
    ],
    "support_bombardment_minimal": [
        "{artillery}'s guns fired in support, though the terrain blunted their effect.",
        "{artillery} provided covering fire, but the ground offered {enemy} too much shelter.",
    ],
    "overwatch_repelled": [
        "The enemy advance faltered under {artillery}'s watchful guns. Even without a full bombardment, the artillery's presence was felt.",
        "{artillery}'s overwatch suppressed the enemy assault. The guns need not fire to inspire caution.",
        "The mere presence of {artillery}'s battery discouraged {enemy}'s attack. Artillery overwatch proved its worth.",
    ],
    # ── Square Formation observations (Phase 7b, Session 67) ──
    "square_cavalry_repulsed": [
        "{marshal}'s square held firm against {enemy}'s cavalry, Sire. The bayonets turned aside the charge.",
        "The square formation proved its worth. {enemy}'s horsemen could not break {marshal}'s bristling ranks.",
        "{enemy}'s cavalry dashed themselves against {marshal}'s square. A textbook defense, Sire.",
    ],
    "square_artillery_punished": [
        "{marshal}'s square was a perfect target for {enemy}'s guns, Sire. Packed ranks invite canister.",
        "The square that saved {marshal} from cavalry now condemned them to {enemy}'s artillery fire.",
        "{enemy}'s gunners found {marshal}'s dense formation an unmissable target. The cost was terrible.",
    ],
    "square_held_defense": [
        "{marshal}'s square formation provided a solid defensive anchor, Sire.",
        "The square held its ground. {marshal}'s infantry stood like a fortress on the field.",
        "{marshal}'s men formed square and weathered the storm. Discipline held the line.",
    ],
    "default": [
        "The engagement proceeded as one might expect, Sire.",
        "A standard affair. Nothing unusual to report.",
        "The battle unfolded without particular distinction.",
    ],
}


def _join_names(names) -> str:
    """Render a marshal list as prose: "A", "A and B", "A, B and C".

    `" and ".join()` produced "Lannes and Murat and Bernadotte" in a live
    Berthier observation — a coordination report is read every battle, so
    the list has to read like a sentence.
    """
    clean = [str(n).strip() for n in names if str(n or "").strip()]
    if not clean:
        return ""
    if len(clean) == 1:
        return clean[0]
    if len(clean) == 2:
        return f"{clean[0]} and {clean[1]}"
    return ", ".join(clean[:-1]) + f" and {clean[-1]}"


def _our_side(battle_result: Dict, player_nation: str = "France") -> Dict:
    """PT-D4: the player's own side of the battle payload.

    `forced_retreat` has been published on both sides since the rout
    system landed (`combat.py:966/972`); the observation selector simply
    never read it. `broken` and `region_lost` ride the same dicts when the
    resolver sets them.
    """
    attacker_nation = battle_result.get("attacker_nation", "")
    side = "attacker" if attacker_nation == player_nation else "defender"
    data = battle_result.get(side, {})
    return data if isinstance(data, dict) else {}


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

    def _fill(template: str, **extra) -> str:
        # PT-G5(f): Berthier said "ArchdukeCharles broke through Ney's
        # prepared defenses" in his own mouth. This file contained ZERO
        # calls to `humanize_entity_name`, the project's single source for
        # exactly this repair, while the enemy_voice line three rows below
        # in the same block printed the name correctly spaced — because
        # the BACKEND humanizes there and not here.
        from backend.display_names import humanize_entity_name as _hz

        result = template
        result = result.replace("{marshal}", _hz(our_name))
        result = result.replace("{enemy}", _hz(enemy_name))
        # Coordination placeholders (Session 65, M6)
        result = result.replace("{ally}", _hz(extra.get("ally", "")))
        result = result.replace("{failed_ally}", _hz(extra.get("failed_ally", "")))
        result = result.replace("{relationship}", extra.get("relationship", ""))
        result = result.replace("{coordination_bonus}", extra.get("coordination_bonus", ""))
        result = result.replace("{arrival_score}", extra.get("arrival_score", ""))
        # Session 68: artillery name placeholder
        result = result.replace("{artillery}", _hz(extra.get("artillery", "")))
        # Number agreement for the multi-name coordination banks: three
        # absent marshals took a singular verb ("Lannes and Murat and
        # Bernadotte, however, was conspicuously absent").
        result = result.replace("{failed_was}", extra.get("failed_was", "was"))
        return result

    # ════════════════════════════════════════════════════════════════════════
    # COORDINATION OBSERVATIONS (Session 65)
    # Data injected by executor.py after resolve_battle() returns.
    # When called from inside resolve_battle (first pass), these dicts are
    # empty and all coordination checks are no-ops.
    # ════════════════════════════════════════════════════════════════════════
    coordination = battle_result.get("coordination_context", {})
    reinforcement_data = battle_result.get("reinforcement_results_for_report", {})
    relationship_changes = battle_result.get("relationship_changes", [])

    # Perspective-correct reinforcement data: our side's reinforcements
    our_reinforcements = reinforcement_data.get(
        "attacker" if we_are_attacker else "defender", [])

    # Perspective-correct coordination data (audit 2026-07-09 fix 2.2): the
    # legacy keys carry the ATTACKER side; defender-side copies are tagged.
    # Pre-fix, an enemy attacker's combined-arms triangle (or its internal
    # hostile/devoted politics) was narrated as "our side" when the player
    # was the defender.
    if we_are_attacker:
        our_type_count = coordination.get(
            "attacker_type_count", coordination.get("type_count", 0))
        our_hostile_forced = coordination.get("hostile_forced_participants", [])
        our_hostile_refused = coordination.get("hostile_refused", [])
        our_devoted_allies = coordination.get("devoted_allies", [])
        our_participants = coordination.get("attacker_participants")
    else:
        our_type_count = coordination.get("defender_type_count", 0)
        our_hostile_forced = coordination.get("defender_hostile_forced_participants", [])
        our_hostile_refused = coordination.get("defender_hostile_refused", [])
        our_devoted_allies = coordination.get("defender_devoted_allies", [])
        our_participants = coordination.get("defender_participants")

    # PC-5: "held the field alone" is a claim about the rest of the field.
    # A MISSING participants list is not evidence of solitude — when we
    # cannot check, we do not claim it. (The list is absent only on the
    # first-pass call from inside resolve_battle, where the reinforcement
    # branches below are unreachable anyway.)
    fought_alone = bool(our_participants) and len(our_participants) <= 1

    # Priority 0.5: Full combined arms triangle (3/3 unit types) — our side
    if our_type_count >= 3:
        return _fill(random.choice(_OBSERVATIONS["coordination_full_triangle"]))

    # Priority 0.7: Reinforcement results (our side)
    arrived = [r for r in our_reinforcements if r.get("arrived")]
    failed = [r for r in our_reinforcements if not r.get("arrived")]

    if arrived and failed:
        # Mixed: some arrived, some didn't — mention both
        arrived_names = _join_names([r.get("marshal", "") for r in arrived])
        failed_names = _join_names([r.get("marshal", "") for r in failed])
        return _fill(random.choice(_OBSERVATIONS["coordination_reinforcement_mixed"]),
                     ally=arrived_names, failed_ally=failed_names,
                     failed_was=("were" if len(failed) > 1 else "was"))

    if arrived:
        ally_names = _join_names([r.get("marshal", "") for r in arrived])
        # W6-1 (BUG-CA-5): branch on the OUTCOME — the arrival bank claims
        # "swung the battle in our favor", which the live audit caught being
        # said about a stalemate. Stalemate → held; loss → not enough.
        outcome = str(battle_result.get("outcome", ""))
        we_won = (
            (we_are_attacker and outcome in
             ("attacker_victory", "attacker_tactical_victory"))
            or (not we_are_attacker and outcome in
                ("defender_victory", "defender_tactical_victory"))
        )
        if outcome == "stalemate":
            bank = "coordination_reinforcement_arrival_held"
        elif we_won:
            bank = "coordination_reinforcement_arrival"
        else:
            bank = "coordination_reinforcement_arrival_lost"
        return _fill(random.choice(_OBSERVATIONS[bank]), ally=ally_names)

    # Priority 0.8: All reinforcements failed (our side)
    if failed:
        failed_names = _join_names([r.get("marshal", "") for r in failed])
        bank = ("coordination_reinforcement_failure_alone" if fought_alone
                else "coordination_reinforcement_failure")
        # N24 (CA9) — the ROOT CAUSE, not the template. The mixed-bank call
        # site passes `failed_was`; this one never did, so no amount of
        # template editing could have made the verb agree. Safe by
        # construction: `_fill` defaults `{failed_was}` to "was", so every
        # other template and the singular case stay byte-identical.
        return _fill(random.choice(_OBSERVATIONS[bank]), ally=failed_names,
                     failed_was=("were" if len(failed) > 1 else "was"))

    # Priority 0.6: Support auto-bombardment (Session 68)
    support_bombardment_damage = battle_result.get("support_bombardment_total_damage", 0)
    if support_bombardment_damage > 0 and we_are_attacker:
        # Find the artillery that provided support (first SUPPORT artillery on our side)
        support_artillery_name = ""
        for m_data in battle_result.get("auto_bombardment_results", []):
            atk_data = m_data.get("attacker", {})
            if atk_data.get("name"):
                support_artillery_name = atk_data["name"]
                break
        if support_bombardment_damage > defender_original * 0.05:
            return _fill(random.choice(_OBSERVATIONS["support_bombardment_effective"]),
                         artillery=support_artillery_name)
        else:
            return _fill(random.choice(_OBSERVATIONS["support_bombardment_minimal"]),
                         artillery=support_artillery_name)

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

    # Priority 5.5 (coordination): Hostile marshal forced to fight via SUPPORT (D3/A-M4)
    if our_hostile_forced:
        return _fill(random.choice(_OBSERVATIONS["coordination_hostile_forced"]),
                     ally=our_hostile_forced[0])

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

    # Priority 6d: Artillery-specific observations
    cavalry_counter = battle_result.get("cavalry_counter_message")

    # Cavalry overran our artillery
    if we_lost and cavalry_counter and not we_are_attacker:
        return _fill(random.choice(_OBSERVATIONS["cavalry_overran_artillery"]))

    # Our artillery caught moving
    if we_lost and _has_mod(our_mods, "artillery in transit", "penalty"):
        return _fill(random.choice(_OBSERVATIONS["artillery_caught_moving"]))

    # Our artillery bombardment was effective (we won + fort degradation from artillery)
    if we_won and fort_degraded and we_are_attacker:
        # Check if the attacker is artillery (fort degrades 10% vs 5%)
        atk_nation = battle_result.get("attacker_nation", "")
        if atk_nation == player_nation:
            return _fill(random.choice(_OBSERVATIONS["artillery_fort_degradation"]))

    # Our cavalry overran enemy artillery (attacker side)
    if we_won and cavalry_counter and we_are_attacker:
        return _fill(random.choice(_OBSERVATIONS["cavalry_overrun_attacker"]))

    # Priority 6e: Square formation interactions (Session 67)
    # Cavalry repulsed by square
    if _has_mod(their_mods, "square formation (vs cavalry)", "penalty") and not we_lost:
        return _fill(random.choice(_OBSERVATIONS["square_cavalry_repulsed"]))
    # Artillery punished square
    if _has_mod(our_mods, "square formation (vs artillery)", "bonus") and we_won:
        return _fill(random.choice(_OBSERVATIONS["square_artillery_punished"]))
    # Square held on defense (defender had square bonus)
    if _has_mod(our_mods, "square formation", "bonus") and not we_lost and not we_are_attacker:
        return _fill(random.choice(_OBSERVATIONS["square_held_defense"]))

    # Priority 6f: Overwatch observation (Session 68)
    # Fires when overwatch was active AND defender won.
    # overwatch_count is always attacker-perspective (enemy artillery in defender's region).
    # If we are defender and we won, our artillery provided the overwatch.
    # If we are attacker and we lost, enemy artillery provided overwatch against us.
    overwatch_count_val = battle_result.get("overwatch_count", 0)
    if overwatch_count_val > 0:
        if (we_won and not we_are_attacker) or (we_lost and we_are_attacker):
            return _fill(random.choice(_OBSERVATIONS["overwatch_repelled"]),
                         artillery="our artillery")

    # Priority 7: We won + our side had drill bonus
    if we_won and _has_mod(our_mods, "drill", "bonus"):
        return _fill(random.choice(_OBSERVATIONS["won_drilled"]))

    # Priority 8: We lost + no drill + narrow margin (< 15% of our original strength)
    #
    # PT-D4: ...but a defeat that ended in a ROUT is not a narrow one. This
    # arm is what caught the measured case — Massena broken, routed and
    # Milan lost came back "A narrow defeat, Sire. Better-prepared troops
    # might have tipped the balance." The margin was indeed narrow; the
    # sentence was still wrong about the day. Guarded rather than
    # reordered, so the whole ladder above stays byte-identical and only
    # the routed case falls through to its own arm at 8.6.
    if (we_lost and not _has_mod(our_mods, "drill", "bonus")
            and not _our_side(battle_result, player_nation).get(
                "forced_retreat")):
        if our_original > 0:
            margin = abs(our_casualties - enemy_casualties)
            if margin < our_original * 0.15:
                return _fill(random.choice(_OBSERVATIONS["lost_narrow_no_drill"]))

    # Priority 8.5: We lost with significant casualties (>30% of original) — catch-all for
    # losses that didn't match any specific condition (terrain, stance, fort, narrow margin).
    # Without this, devastating defeats like losing half an army fall through to "standard affair".
    if we_lost and our_original > 0 and our_casualties > our_original * 0.30:
        return _fill(random.choice(_OBSERVATIONS["lost_costly"]))

    # ── PT-D4, priority 8.6 ─────────────────────────────────────────────
    # Below the 30% line and above the default. A rout is not about the
    # butcher's bill — a corps can be driven from the field having taken
    # 26% — and there was no arm for it at any priority.
    if _our_side(battle_result, player_nation).get("forced_retreat"):
        return _fill(random.choice(_OBSERVATIONS["routed"]))

    # Priority 8.7: Flawless victory (we won with zero casualties)
    if we_won and our_casualties == 0 and enemy_casualties > 0:
        return _fill(random.choice(_OBSERVATIONS["won_flawless"]))

    # Priority 9: We won decisively (2:1+ casualty ratio in our favor)
    if we_won and enemy_casualties > 0 and our_casualties > 0:
        if enemy_casualties >= our_casualties * 2:
            return _fill(random.choice(_OBSERVATIONS["won_decisively"]))

    # Priority 9.5 (coordination): Devoted ally synergy — more interesting than generic stalemate
    if our_devoted_allies:
        return _fill(random.choice(_OBSERVATIONS["coordination_devoted_synergy"]),
                     ally=our_devoted_allies[0])

    # Priority 9.6 (coordination): Rival→Professional relationship improvement (A-I3)
    # A8 (CA9 row 3): only narrate a thaw that actually happened. A `+1` on a
    # pair carrying a live grievance is REPORTED and never lands (see
    # `relationship.py`'s `stored_moved` note), so Berthier used to
    # congratulate the player on a reconciliation on the very battle where
    # the grievance penalty applied. `stored_moved` defaults True so any
    # other producer of `relationship_changes` is unaffected.
    player_rel_improvements = [
        r for r in relationship_changes
        if r.get("nation") == player_nation and r.get("direction") == "improved"
        and r.get("stored_moved", True)
    ]
    if player_rel_improvements:
        rc = player_rel_improvements[0]
        return _fill(random.choice(_OBSERVATIONS["coordination_rival_improved"]),
                     ally=rc.get("toward", ""))

    # Priority 10: Stalemate
    if outcome == "stalemate":
        return _fill(random.choice(_OBSERVATIONS["stalemate"]))

    # Priority 12 (coordination): Hostile ally in region with 0% coordination (no SUPPORT)
    if our_hostile_refused:
        return _fill(random.choice(_OBSERVATIONS["coordination_hostile_refused"]),
                     ally=our_hostile_refused[0])

    # Priority 16: Default
    return _fill(random.choice(_OBSERVATIONS["default"]))


# HC-2 "The Butcher's Ledger Speaks" (gate §3): past this many of a
# side's own recorded dead, every battle report in that war closes on
# the running cost. Blessed, in-band tunable.
CAMPAIGN_COST_NOTE_THRESHOLD = 25000


def compose_campaign_cost_note(world, own_nation: str,
                               enemy_nation: str) -> str:
    """Stateless closing clause reading the PT-J2 campaign ledger —
    the SAME figure the war-detail popup renders (own recorded dead
    only, the [PTJ-D1] attribution-safe half). Empty below the
    threshold, outside a live ledger, or off the Europe campaign.

    `generate_battle_report` itself has no world access by design —
    this helper takes the world and is glued on at the combat
    executor's after-action seam, the expectation_note pattern.
    """
    if world is None:
        return ""
    if getattr(world, "sovereign_map", "legacy") != "europe":
        return ""
    if not own_nation or not enemy_nation:
        return ""
    ledger = getattr(world, "campaign_ledgers", {}).get(
        world._make_diplo_key(own_nation, enemy_nation), {})
    own_dead = int((ledger.get("casualties") or {}).get(own_nation, 0))
    if own_dead < CAMPAIGN_COST_NOTE_THRESHOLD:
        return ""
    return f"The war's cost now stands at {own_dead:,} of our men."


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
    # W6-1 (BUG-CA-4): derive remaining from the same values the battle
    # event carries (original − casualties). The passed-through "remaining"
    # echoed the ORIGINAL strength on the report surface (live audit:
    # 40,000 → "remaining 40,000" after 6,501 casualties).
    attacker_remaining = max(0, attacker_original - attacker_casualties)
    defender_remaining = max(0, defender_original - defender_casualties)

    observation = _pick_observation(battle_result, player_nation)

    return {
        "modifier_breakdown": {
            "attacker": modifier_snapshot.get("attacker", []),
            "defender": modifier_snapshot.get("defender", []),
        },
        "casualty_summary": {
            # PT-G5(f), completed by the review fleet: `_fill` was
            # humanized and these three renders in the SAME block were
            # not, so Berthier's observation said "Archduke Charles" and
            # the casualty line under it said "ArchdukeCharles".
            "attacker_name": humanize_entity_name(
                str(attacker_data.get("name", "Attacker"))),
            "attacker_original": int(attacker_original),
            "attacker_casualties": int(attacker_casualties),
            "attacker_remaining": int(attacker_remaining),
            "defender_name": humanize_entity_name(
                str(defender_data.get("name", "Defender"))),
            "defender_original": int(defender_original),
            "defender_casualties": int(defender_casualties),
            "defender_remaining": int(defender_remaining),
        },
        "observation": str(observation),
    }


# ════════════════════════════════════════════════════════════════════════════════
# BOMBARDMENT REPORT  (BOMBARDMENT_SPEC §11)
# ════════════════════════════════════════════════════════════════════════════════

def _pick_bombardment_observation(bombardment_data: Dict, player_nation: str = "France") -> str:
    """
    Select a Berthier observation for a bombardment (not a battle).

    Priority rules per BOMBARDMENT_SPEC §11.2:
      1. Defender reduced to 0 → bombardment_target_broken
      2. Collateral hit friendly → bombardment_friendly_fire
      3. Fort degraded → bombardment_fort_cracking
      4. Terrain modifier < 0.80 → bombardment_terrain_difficulty
      5. Defender casualties < 3% of pre-bombardment strength → bombardment_ineffective
      6. Default → bombardment_effective
    """
    attacker_name = str(bombardment_data.get("attacker_name", "Artillery"))
    defender_name = str(bombardment_data.get("defender_name", "Enemy"))
    defender_remaining = bombardment_data.get("defender_remaining", 1)
    defender_original = bombardment_data.get("defender_original", 1)
    defender_casualties = bombardment_data.get("defender_casualties", 0)
    terrain = str(bombardment_data.get("terrain", "plains"))
    terrain_modifier = bombardment_data.get("terrain_modifier", 1.0)
    fort_degraded = bombardment_data.get("fort_degraded", False)
    collateral = bombardment_data.get("collateral", [])

    # Check for friendly fire in collateral
    has_friendly_fire = any(
        c.get("friendly_fire", False) for c in (collateral or [])
    )

    terrain_display = terrain.replace("_", " ")

    def _fill(template: str) -> str:
        return template.format(
            marshal=attacker_name, enemy=defender_name, terrain=terrain_display
        )

    # P1: Defender destroyed
    if defender_remaining <= 0:
        return _fill(random.choice(_OBSERVATIONS["bombardment_target_broken"]))

    # P2: Friendly fire collateral
    if has_friendly_fire:
        return _fill(random.choice(_OBSERVATIONS["bombardment_friendly_fire"]))

    # P3: Fort degraded
    if fort_degraded:
        return _fill(random.choice(_OBSERVATIONS["bombardment_fort_cracking"]))

    # P4: Terrain difficulty (modifier < 0.80 means heavy cover)
    if terrain_modifier < 0.80:
        return _fill(random.choice(_OBSERVATIONS["bombardment_terrain_difficulty"]))

    # P5: Ineffective bombardment (< 3% of defender's pre-bombardment strength)
    if defender_original > 0 and defender_casualties < defender_original * 0.03:
        return _fill(random.choice(_OBSERVATIONS["bombardment_ineffective"]))

    # P6: Default — effective bombardment
    return _fill(random.choice(_OBSERVATIONS["bombardment_effective"]))


def generate_bombardment_report(bombardment_data: Dict, player_nation: str = "France") -> str:
    """
    Generate a Berthier observation string for a bombardment result.

    Unlike generate_battle_report() which returns a full dict with modifier
    breakdowns, bombardment reports return just the observation string.
    The casualty/terrain/fort data is already in the bombardment_result dict
    that Godot receives, so no duplication is needed.

    Args:
        bombardment_data: Dict with keys:
            attacker_name, defender_name, attacker_casualties,
            defender_casualties, defender_remaining, defender_original,
            terrain, terrain_modifier, fort_degraded, fort_old, fort_new,
            collateral (list of dicts with name/nation/casualties/friendly_fire)
        player_nation: For perspective (default "France").

    Returns:
        str: Berthier observation text.
    """
    return _pick_bombardment_observation(bombardment_data, player_nation)
